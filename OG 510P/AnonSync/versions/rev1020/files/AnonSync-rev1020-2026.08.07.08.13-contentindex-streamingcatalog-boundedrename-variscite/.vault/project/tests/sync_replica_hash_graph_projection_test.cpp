#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_digest_accumulator.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename ExpectedException, typename Callable>
void require_throws(
    Callable&& callable,
    const std::string& message,
    int& checks) {
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

std::string payload_digest(const std::string& material) {
    return anonsync::sha256_hex(material);
}

anonsync::SyncReplicaOperation chain_operation(
    const std::string& folder,
    const anonsync::SyncReplicaActor& chain_actor,
    std::uint64_t counter,
    const std::string& predecessor_id) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = "graph/chain.bin";
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = counter;
    operation.content_sha256 =
        payload_digest("chain:" + std::to_string(counter));
    operation.dot = {chain_actor, counter};
    if (counter > 1U) {
        operation.causal_context = {{chain_actor, counter - 1U}};
        operation.predecessor_operation_ids = {predecessor_id};
    }
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

anonsync::SyncReplicaOperation independent_root(
    const std::string& folder,
    const anonsync::SyncReplicaActor& root_actor) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = "graph/independent.bin";
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = 7U;
    operation.content_sha256 = payload_digest("independent");
    operation.dot = {root_actor, 1U};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

std::string numbered_id(const std::string& prefix, std::size_t number) {
    std::string suffix = std::to_string(number);
    if (suffix.size() < 3U) {
        suffix.insert(0U, 3U - suffix.size(), '0');
    }
    return prefix + suffix;
}

anonsync::SyncReplicaOperation operation_from_parents(
    const std::string& folder,
    const anonsync::SyncReplicaActor& operation_actor,
    const std::string& label,
    const std::vector<const anonsync::SyncReplicaOperation*>& parents,
    const anonsync::SyncReplicaModelLimits& limits) {
    std::map<anonsync::SyncReplicaActor, std::uint64_t> context_by_actor;
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = "graph/differential.bin";
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(label.size());
    operation.content_sha256 = payload_digest("differential:" + label);
    operation.dot = {operation_actor, 1U};

    for (const anonsync::SyncReplicaOperation* parent : parents) {
        if (parent == nullptr) {
            throw std::logic_error(
                "hash graph differential fixture received a null parent");
        }
        operation.predecessor_operation_ids.push_back(parent->operation_id);
        auto& dot_counter = context_by_actor[parent->dot.actor];
        dot_counter = std::max(dot_counter, parent->dot.counter);
        for (const anonsync::SyncReplicaClockEntry& entry :
             parent->causal_context) {
            auto& counter = context_by_actor[entry.actor];
            counter = std::max(counter, entry.counter);
        }
    }
    std::sort(
        operation.predecessor_operation_ids.begin(),
        operation.predecessor_operation_ids.end());
    if (std::adjacent_find(
            operation.predecessor_operation_ids.begin(),
            operation.predecessor_operation_ids.end()) !=
        operation.predecessor_operation_ids.end()) {
        throw std::logic_error(
            "hash graph differential fixture selected a duplicate parent");
    }
    operation.causal_context.reserve(context_by_actor.size());
    for (const auto& [context_actor, counter] : context_by_actor) {
        operation.causal_context.push_back({context_actor, counter});
    }
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation, limits);
    return operation;
}

bool parent_covers_dot(
    const anonsync::SyncReplicaOperation& parent,
    const anonsync::SyncReplicaDot& dot) {
    return parent.dot == dot ||
           anonsync::sync_replica_context_covers_dot(
               parent.causal_context, dot);
}

bool predecessor_set_is_minimal_reference(
    const std::vector<const anonsync::SyncReplicaOperation*>& parents) {
    for (std::size_t candidate = 0; candidate < parents.size(); ++candidate) {
        for (std::size_t other = 0; other < parents.size(); ++other) {
            if (candidate == other) continue;
            if (parent_covers_dot(*parents[other], parents[candidate]->dot)) {
                return false;
            }
        }
    }
    return true;
}

class DeterministicGenerator final {
public:
    explicit DeterministicGenerator(std::uint64_t state) : state_(state) {}

    std::uint64_t next() noexcept {
        state_ = state_ * 6364136223846793005ULL +
                 1442695040888963407ULL;
        return state_;
    }

    std::size_t bounded(std::size_t bound) {
        if (bound == 0U) {
            throw std::logic_error(
                "hash graph deterministic generator received a zero bound");
        }
        return static_cast<std::size_t>(
            next() % static_cast<std::uint64_t>(bound));
    }

private:
    std::uint64_t state_;
};

}  // namespace

int main() {
    using namespace anonsync;

    try {
        int checks = 0;
        const std::string folder = "folder-hash-graph";
        const SyncReplicaActor chain_actor = actor("device-chain", 71U);
        const SyncReplicaActor observer_actor = actor("device-observer", 72U);
        const SyncReplicaActor independent_actor =
            actor("device-independent", 73U);

        SyncReplicaModelLimits limits;
        limits.max_operations = 700U;
        limits.max_context_entries = 16U;
        limits.max_predecessor_ids = 16U;

        const std::string accumulator_zero =
            sync_replica_digest_accumulator_zero();
        const std::string accumulator_left = sha256_hex("accumulator-left");
        const std::string accumulator_right = sha256_hex("accumulator-right");
        const std::string left_then_right =
            sync_replica_digest_accumulator_add_or_throw(
                sync_replica_digest_accumulator_add_or_throw(
                    accumulator_zero, accumulator_left),
                accumulator_right);
        const std::string right_then_left =
            sync_replica_digest_accumulator_add_or_throw(
                sync_replica_digest_accumulator_add_or_throw(
                    accumulator_zero, accumulator_right),
                accumulator_left);
        require(
            left_then_right == right_then_left &&
                sync_replica_digest_accumulator_subtract_or_throw(
                    left_then_right, accumulator_right) == accumulator_left &&
                sync_replica_digest_accumulator_subtract_or_throw(
                    left_then_right, accumulator_left) == accumulator_right,
            "digest accumulator is not commutative and exactly reversible",
            checks);
        const std::string accumulator_max(64U, 'f');
        const std::string accumulator_one =
            std::string(63U, '0') + "1";
        require(
            sync_replica_digest_accumulator_add_or_throw(
                accumulator_max, accumulator_one) == accumulator_zero &&
                sync_replica_digest_accumulator_subtract_or_throw(
                    accumulator_zero, accumulator_one) == accumulator_max &&
                sync_replica_digest_accumulator_subtract_or_throw(
                    sync_replica_digest_accumulator_add_or_throw(
                        accumulator_zero, accumulator_left),
                    accumulator_left) == accumulator_zero,
            "digest accumulator did not implement exact modulo-2^256 carry and borrow",
            checks);
        require_throws<std::invalid_argument>(
            [&] {
                (void)sync_replica_digest_accumulator_add_or_throw(
                    accumulator_zero, "NOT-A-DIGEST");
            },
            "digest accumulator accepted noncanonical input", checks);

        constexpr std::size_t kChainLength = 384U;
        std::vector<SyncReplicaOperation> chain;
        chain.reserve(kChainLength);
        std::string predecessor_id;
        for (std::size_t index = 0; index < kChainLength; ++index) {
            chain.push_back(chain_operation(
                folder,
                chain_actor,
                static_cast<std::uint64_t>(index + 1U),
                predecessor_id));
            predecessor_id = chain.back().operation_id;
        }

        // Reverse delivery is the adversarial shape that made the old dotted
        // summary unsafe: every received operation claims a long absent past.
        // Exact hashes keep all of it pending and the active frontier empty.
        SyncReplicaModel reverse(folder, observer_actor, limits);
        for (auto operation = chain.rbegin(); operation != chain.rend();
             ++operation) {
            (void)reverse.accept_remote_or_throw(*operation);
            if (operation + 1 != chain.rend()) {
                require(reverse.operation_count() == 0U,
                        "reverse chain must remain inactive until its root arrives",
                        checks);
            }
        }
        require(reverse.evidence_count() == kChainLength &&
                    reverse.operation_count() == kChainLength &&
                    reverse.pending_operation_count() == 0U &&
                    reverse.quarantined_operation_count() == 0U,
                "one root arrival must activate the complete exact chain",
                checks);
        require(reverse.observed_context() ==
                    std::vector<SyncReplicaClockEntry>{
                        {chain_actor, kChainLength}},
                "activated chain must expose its exact maximal dot", checks);
        require(reverse.causal_head_operation_ids() ==
                    std::vector<std::string>{chain.back().operation_id},
                "activated chain must expose one exact hash head", checks);

        // The same evidence in forward order must have identical projection.
        SyncReplicaModel forward(folder, observer_actor, limits);
        for (const SyncReplicaOperation& operation : chain) {
            require(forward.accept_remote_or_throw(operation) ==
                        SyncReplicaAdmission::InsertedActive,
                    "forward chain operations must activate as dependencies arrive",
                    checks);
        }
        require(forward.operation_set_digest() ==
                        reverse.operation_set_digest() &&
                    forward.evidence_set_digest() ==
                        reverse.evidence_set_digest() &&
                    forward.visible_state_digest() ==
                        reverse.visible_state_digest() &&
                    forward.operation_set_accumulator_digest() ==
                        reverse.operation_set_accumulator_digest() &&
                    forward.evidence_set_accumulator_digest() ==
                        reverse.evidence_set_accumulator_digest() &&
                    forward.visible_path_count() ==
                        reverse.visible_path_count() &&
                    forward.visible_state_accumulator_digest() ==
                        reverse.visible_state_accumulator_digest(),
                "forward and reverse exact evidence must converge under both ordered and incremental witnesses", checks);

        const SyncReplicaOperation safe_root =
            independent_root(folder, independent_actor);
        (void)forward.accept_remote_or_throw(safe_root);
        (void)reverse.accept_remote_or_throw(safe_root);

        // Introduce a late alternate root under the same dot. Both root bytes
        // become fork evidence, the whole dependent chain is quarantined, and
        // the unrelated branch remains active. The result cannot depend on
        // which root happened to be observed first.
        SyncReplicaOperation fork_root = chain.front();
        fork_root.content_sha256 = payload_digest("alternate-root");
        fork_root.operation_id =
            make_sync_replica_operation_id_or_throw(fork_root, limits);
        require(forward.accept_remote_or_throw(fork_root) ==
                    SyncReplicaAdmission::InsertedQuarantined,
                "late chain-root fork must be quarantined", checks);

        SyncReplicaModel fork_first(folder, observer_actor, limits);
        (void)fork_first.accept_remote_or_throw(safe_root);
        require(fork_first.accept_remote_or_throw(fork_root) ==
                    SyncReplicaAdmission::InsertedActive,
                "one fork side may be provisionally active before conflict evidence",
                checks);
        for (auto operation = chain.rbegin(); operation != chain.rend();
             ++operation) {
            (void)fork_first.accept_remote_or_throw(*operation);
        }

        require(forward.evidence_count() == kChainLength + 2U &&
                    forward.operation_count() == 1U &&
                    forward.quarantined_operation_count() ==
                        kChainLength + 1U,
                "fork must quarantine both roots and every dependent chain node",
                checks);
        require(forward.evidence_state(chain.front().operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDotFork &&
                    forward.evidence_state(fork_root.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDotFork &&
                    forward.evidence_state(chain.back().operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDependency,
                "fork and transitive dependency states must be explicit", checks);
        require(forward.operation_by_id(safe_root.operation_id).has_value() &&
                    !forward.operation_by_id(chain.back().operation_id)
                         .has_value(),
                "unrelated active evidence must survive fork quarantine", checks);
        require(forward.operation_set_digest() ==
                        fork_first.operation_set_digest() &&
                    forward.evidence_set_digest() ==
                        fork_first.evidence_set_digest() &&
                    forward.visible_state_digest() ==
                        fork_first.visible_state_digest(),
                "late-fork and fork-first histories must project identically",
                checks);

        // Projection state is durable evidence, not transient arrival metadata.
        const SyncReplicaDurableState durable = forward.durable_state();
        SyncReplicaModel restored =
            SyncReplicaModel::restore_or_throw(durable, limits);
        require(restored.operation_set_digest() ==
                        forward.operation_set_digest() &&
                    restored.evidence_set_digest() ==
                        forward.evidence_set_digest() &&
                    restored.quarantined_operation_count() ==
                        forward.quarantined_operation_count(),
                "restart must recompute the same fork quarantine", checks);

        // The local ID vector is durable minting authority, not a hint. Restore
        // must reject a sequence whose referenced bytes disappeared or whose
        // dot belongs to another actor instead of silently marking the epoch
        // compromised and accepting a corrupted authority record.
        const SyncReplicaActor authority_actor =
            actor("device-restore-authority", 74U);
        SyncReplicaModel authority(folder, authority_actor, limits);
        const SyncReplicaOperation authorized_operation =
            authority.create_local_file_or_throw(
                "graph/authority.bin", 1U, payload_digest("authorized"));
        SyncReplicaDurableState missing_authority =
            authority.durable_state();
        missing_authority.operations.clear();
        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncReplicaModel::restore_or_throw(
                    missing_authority, limits);
            },
            "restore must reject a local authority ID absent from evidence",
            checks);

        const SyncReplicaOperation foreign_authority = independent_root(
            folder, actor("device-restore-foreign", 75U));
        (void)authority.accept_remote_or_throw(foreign_authority);
        SyncReplicaDurableState misbound_authority =
            authority.durable_state();
        misbound_authority.local_operation_ids.front() =
            foreign_authority.operation_id;
        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncReplicaModel::restore_or_throw(
                    misbound_authority, limits);
            },
            "restore must reject a local authority ID bound to another actor",
            checks);
        require(
            authority.operation_by_id(authorized_operation.operation_id)
                .has_value(),
            "restore corruption fixtures must not alter the live authority",
            checks);

        // A local merge cannot encode more exact heads than its predecessor
        // budget. Denial must occur before evidence publication or local counter
        // consumption; this also guards the mint strong guarantee at a
        // deterministic preallocation boundary.
        SyncReplicaModelLimits narrow_head_limits;
        narrow_head_limits.max_operations = 16U;
        narrow_head_limits.max_context_entries = 8U;
        narrow_head_limits.max_predecessor_ids = 2U;
        SyncReplicaModel narrow_heads(
            folder,
            actor("device-narrow-heads", 76U),
            narrow_head_limits);
        for (std::size_t index = 0; index < 3U; ++index) {
            const SyncReplicaOperation root = independent_root(
                folder,
                actor(numbered_id("device-narrow-root-", index),
                      77U + index));
            (void)narrow_heads.accept_remote_or_throw(root);
        }
        const SyncReplicaDurableState narrow_before =
            narrow_heads.durable_state();
        require_throws<std::length_error>(
            [&] {
                (void)narrow_heads.create_local_file_or_throw(
                    "graph/narrow.bin", 2U, payload_digest("narrow"));
            },
            "local mint must preflight exact-head fan-in",
            checks);
        require(
            narrow_heads.durable_state() == narrow_before &&
                narrow_heads.last_local_counter() == 0U &&
                narrow_heads.evidence_count() == 3U,
            "predecessor-budget denial must leave minting state unchanged",
            checks);

        // Missing dependency is not a reason to retain an impossible operation
        // as pending. Once a known parent proves that the declared context omits
        // its causal closure, no future hash can repair the envelope and the
        // absent hash must disappear from the fetch set.
        const std::string never_present_id(64U, 'f');
        const SyncReplicaOperation known_parent = independent_root(
            folder, actor("device-known-parent", 80U));
        SyncReplicaOperation impossible_pending;
        impossible_pending.folder_id = folder;
        impossible_pending.canonical_path = "graph/impossible.bin";
        impossible_pending.kind = SyncReplicaValueKind::File;
        impossible_pending.size_bytes = 3U;
        impossible_pending.content_sha256 =
            payload_digest("impossible-pending");
        impossible_pending.dot = {
            actor("device-impossible-child", 81U), 1U};
        impossible_pending.predecessor_operation_ids = {
            known_parent.operation_id, never_present_id};
        std::sort(
            impossible_pending.predecessor_operation_ids.begin(),
            impossible_pending.predecessor_operation_ids.end());
        impossible_pending.operation_id =
            make_sync_replica_operation_id_or_throw(
                impossible_pending, limits);

        SyncReplicaModel impossible_first(
            folder, actor("device-impossible-observer-a", 82U), limits);
        require(
            impossible_first.accept_remote_or_throw(impossible_pending) ==
                    SyncReplicaAdmission::InsertedPending &&
                impossible_first.missing_predecessor_operation_ids().size() ==
                    2U,
            "an envelope with no known parents may remain provisionally pending",
            checks);
        (void)impossible_first.accept_remote_or_throw(known_parent);
        require(
            impossible_first.evidence_state(
                impossible_pending.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedCausalEnvelope &&
                impossible_first.missing_predecessor_operation_ids().empty(),
            "known causal contradiction must stop impossible dependency pull",
            checks);

        SyncReplicaModel known_first(
            folder, actor("device-impossible-observer-b", 83U), limits);
        (void)known_first.accept_remote_or_throw(known_parent);
        require(
            known_first.accept_remote_or_throw(impossible_pending) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                known_first.evidence_state(impossible_pending.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedCausalEnvelope &&
                known_first.missing_predecessor_operation_ids().empty(),
            "known-first impossible envelope must quarantine immediately",
            checks);
        require(
            impossible_first.operation_set_digest() ==
                    known_first.operation_set_digest() &&
                impossible_first.evidence_set_digest() ==
                    known_first.evidence_set_digest(),
            "impossible pending evidence must converge across arrival orders",
            checks);

        // A missing third parent cannot make a known ancestor-plus-descendant
        // pair minimal. Quarantine the redundant subset rather than requesting
        // bytes that cannot change the verdict.
        const std::vector<const SyncReplicaOperation*> one_parent = {
            &known_parent};
        const SyncReplicaOperation known_child = operation_from_parents(
            folder,
            actor("device-known-child", 84U),
            "known-child",
            one_parent,
            limits);
        SyncReplicaModel redundant_pending_model(
            folder, actor("device-redundant-observer", 85U), limits);
        (void)redundant_pending_model.accept_remote_or_throw(known_parent);
        (void)redundant_pending_model.accept_remote_or_throw(known_child);
        const std::vector<const SyncReplicaOperation*> redundant_parents = {
            &known_parent, &known_child};
        SyncReplicaOperation redundant_pending = operation_from_parents(
            folder,
            actor("device-redundant-pending", 86U),
            "redundant-pending",
            redundant_parents,
            limits);
        redundant_pending.predecessor_operation_ids.push_back(
            never_present_id);
        std::sort(
            redundant_pending.predecessor_operation_ids.begin(),
            redundant_pending.predecessor_operation_ids.end());
        redundant_pending.operation_id =
            make_sync_replica_operation_id_or_throw(
                redundant_pending, limits);
        require(
            redundant_pending_model.accept_remote_or_throw(
                redundant_pending) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                redundant_pending_model.evidence_state(
                    redundant_pending.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedCausalEnvelope &&
                redundant_pending_model
                    .missing_predecessor_operation_ids().empty(),
            "known redundant parents must dominate a missing dependency",
            checks);

        // Exact bytes can represent a different valid operation when a payload
        // byte changes; decoding derives that new identity rather than trusting
        // an out-of-band claimed digest.
        std::string mutated =
            encode_sync_replica_operation_canonical_or_throw(safe_root, limits);
        const std::size_t digest_position =
            mutated.find(safe_root.content_sha256);
        require(digest_position != std::string::npos,
                "canonical fixture must contain the payload digest bytes", checks);
        mutated[digest_position] =
            mutated[digest_position] == '0' ? '1' : '0';
        const SyncReplicaOperation decoded_mutation =
            decode_sync_replica_operation_canonical_or_throw(mutated, limits);
        require(decoded_mutation.operation_id == sha256_hex(mutated) &&
                    decoded_mutation.operation_id != safe_root.operation_id,
                "decoder must derive identity from mutated exact bytes", checks);

        // Wide fan-in exercises the parent-minimality path without quadratic
        // pairwise ancestry probes. Every independent root is necessary for the
        // honest merge; adding one root beside that merge is redundant because
        // the merge's causal closure already covers it.
        constexpr std::size_t kWideRootCount = 128U;
        SyncReplicaModelLimits wide_limits;
        wide_limits.max_operations = 300U;
        wide_limits.max_context_entries = 200U;
        wide_limits.max_predecessor_ids = 200U;
        const SyncReplicaActor wide_merger =
            actor("device-wide-merger", 800U);
        SyncReplicaModel wide(folder, wide_merger, wide_limits);
        std::vector<SyncReplicaOperation> wide_roots;
        wide_roots.reserve(kWideRootCount);
        for (std::size_t index = 0; index < kWideRootCount; ++index) {
            const std::string suffix =
                index < 10U ? "00" + std::to_string(index)
                            : index < 100U ? "0" + std::to_string(index)
                                           : std::to_string(index);
            wide_roots.push_back(independent_root(
                folder,
                actor("device-wide-" + suffix, 900U + index)));
            require(
                wide.accept_remote_or_throw(wide_roots.back()) ==
                    SyncReplicaAdmission::InsertedActive,
                "independent wide root must activate", checks);
        }
        require(wide.causal_head_operation_ids().size() == kWideRootCount,
                "all independent wide roots must remain causal heads", checks);
        const SyncReplicaOperation wide_merge =
            wide.create_local_file_or_throw(
                "graph/wide.bin", 128U, payload_digest("wide-merge"));
        require(
            wide_merge.predecessor_operation_ids.size() == kWideRootCount &&
                wide_merge.causal_context.size() == kWideRootCount &&
                wide.causal_head_operation_ids() ==
                    std::vector<std::string>{wide_merge.operation_id},
            "wide merge must bind every independent head exactly once", checks);

        SyncReplicaOperation redundant_wide_parent;
        redundant_wide_parent.folder_id = folder;
        redundant_wide_parent.canonical_path = "graph/wide.bin";
        redundant_wide_parent.kind = SyncReplicaValueKind::File;
        redundant_wide_parent.size_bytes = 129U;
        redundant_wide_parent.content_sha256 =
            payload_digest("redundant-wide-parent");
        redundant_wide_parent.dot = {
            actor("device-wide-redundant", 1001U), 1U};
        redundant_wide_parent.causal_context = wide_merge.causal_context;
        redundant_wide_parent.causal_context.push_back(
            {wide_merge.dot.actor, wide_merge.dot.counter});
        std::sort(
            redundant_wide_parent.causal_context.begin(),
            redundant_wide_parent.causal_context.end(),
            [](const SyncReplicaClockEntry& left,
               const SyncReplicaClockEntry& right) {
                return left.actor < right.actor;
            });
        redundant_wide_parent.predecessor_operation_ids = {
            wide_roots.front().operation_id, wide_merge.operation_id};
        std::sort(
            redundant_wide_parent.predecessor_operation_ids.begin(),
            redundant_wide_parent.predecessor_operation_ids.end());
        redundant_wide_parent.operation_id =
            make_sync_replica_operation_id_or_throw(
                redundant_wide_parent, wide_limits);
        require(
            wide.accept_remote_or_throw(redundant_wide_parent) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                wide.evidence_state(redundant_wide_parent.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedCausalEnvelope,
            "wide parent-minimality check must reject a head plus its covered ancestor",
            checks);

        // Differentially check the optimized top-two parent coverage algorithm
        // against an intentionally simple O(P^2) oracle over a deterministic,
        // branching valid DAG. The optimized path must accept every antichain and
        // reject every set containing an ancestor beside its descendant.
        constexpr std::size_t kDifferentialBaseCount = 96U;
        constexpr std::size_t kDifferentialCandidateCount = 192U;
        SyncReplicaModelLimits differential_limits;
        differential_limits.max_operations = 400U;
        differential_limits.max_context_entries = 256U;
        differential_limits.max_predecessor_ids = 32U;
        SyncReplicaModel differential(
            folder,
            actor("device-differential-observer", 1100U),
            differential_limits);
        DeterministicGenerator generator(0x5a17d3c4b29e8061ULL);
        std::vector<SyncReplicaOperation> base_operations;
        base_operations.reserve(kDifferentialBaseCount);
        std::map<std::string, std::size_t> base_index_by_id;
        std::set<std::size_t> head_indices;
        std::vector<std::size_t> non_root_indices;

        for (std::size_t index = 0; index < kDifferentialBaseCount; ++index) {
            std::vector<std::size_t> selected_indices;
            if (index >= 12U && index % 3U != 0U) {
                const std::size_t parent_count =
                    index % 11U == 0U && head_indices.size() >= 2U
                        ? 2U
                        : 1U;
                std::vector<std::size_t> available_heads(
                    head_indices.begin(), head_indices.end());
                while (selected_indices.size() < parent_count) {
                    const std::size_t position =
                        generator.bounded(available_heads.size());
                    selected_indices.push_back(available_heads[position]);
                    available_heads.erase(available_heads.begin() +
                                          static_cast<std::ptrdiff_t>(position));
                }
                non_root_indices.push_back(index);
            }

            std::vector<const SyncReplicaOperation*> parents;
            parents.reserve(selected_indices.size());
            for (const std::size_t parent_index : selected_indices) {
                parents.push_back(&base_operations[parent_index]);
            }
            SyncReplicaOperation operation = operation_from_parents(
                folder,
                actor(numbered_id("device-dag-", index),
                      1200U + static_cast<std::uint64_t>(index)),
                numbered_id("base-", index),
                parents,
                differential_limits);
            require(
                differential.accept_remote_or_throw(operation) ==
                    SyncReplicaAdmission::InsertedActive,
                "valid differential DAG base operation must activate",
                checks);
            base_index_by_id.emplace(operation.operation_id, index);
            base_operations.push_back(std::move(operation));
            for (const std::size_t parent_index : selected_indices) {
                head_indices.erase(parent_index);
            }
            head_indices.insert(index);
        }
        require(head_indices.size() >= 8U && !non_root_indices.empty(),
                "differential DAG must retain breadth and ancestry", checks);

        std::size_t oracle_active = 0U;
        std::size_t oracle_quarantined = 0U;
        const std::vector<std::size_t> final_heads(
            head_indices.begin(), head_indices.end());
        for (std::size_t sample = 0;
             sample < kDifferentialCandidateCount; ++sample) {
            std::set<std::size_t> selected;
            if (sample % 3U == 0U) {
                const std::size_t count = 1U +
                    generator.bounded(std::min<std::size_t>(8U, final_heads.size()));
                while (selected.size() < count) {
                    selected.insert(
                        final_heads[generator.bounded(final_heads.size())]);
                }
            } else if (sample % 3U == 1U) {
                const std::size_t child_index = non_root_indices[
                    generator.bounded(non_root_indices.size())];
                selected.insert(child_index);
                const SyncReplicaOperation& child =
                    base_operations[child_index];
                const std::string& direct_parent_id =
                    child.predecessor_operation_ids[
                        generator.bounded(
                            child.predecessor_operation_ids.size())];
                selected.insert(base_index_by_id.at(direct_parent_id));
                const std::size_t extra_heads = generator.bounded(4U);
                for (std::size_t extra = 0; extra < extra_heads; ++extra) {
                    selected.insert(
                        final_heads[generator.bounded(final_heads.size())]);
                }
            } else {
                const std::size_t count = 2U + generator.bounded(7U);
                while (selected.size() < count) {
                    selected.insert(
                        generator.bounded(base_operations.size()));
                }
            }

            std::vector<const SyncReplicaOperation*> parents;
            parents.reserve(selected.size());
            for (const std::size_t parent_index : selected) {
                parents.push_back(&base_operations[parent_index]);
            }
            const bool reference_minimal =
                predecessor_set_is_minimal_reference(parents);
            SyncReplicaOperation candidate = operation_from_parents(
                folder,
                actor(numbered_id("device-candidate-", sample),
                      2000U + static_cast<std::uint64_t>(sample)),
                numbered_id("candidate-", sample),
                parents,
                differential_limits);
            const SyncReplicaAdmission admission =
                differential.accept_remote_or_throw(candidate);
            const bool projected_active =
                admission == SyncReplicaAdmission::InsertedActive &&
                differential.evidence_state(candidate.operation_id) ==
                    SyncReplicaEvidenceState::Active;
            require(projected_active == reference_minimal,
                    "optimized parent-minimality result must match pairwise oracle",
                    checks);
            if (reference_minimal) {
                ++oracle_active;
            } else {
                require(
                    admission == SyncReplicaAdmission::InsertedQuarantined &&
                    differential.evidence_state(candidate.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedCausalEnvelope,
                    "nonminimal differential parent set must quarantine causally",
                    checks);
                ++oracle_quarantined;
            }
        }
        require(oracle_active != 0U && oracle_quarantined != 0U,
                "differential corpus must exercise both oracle outcomes", checks);

        std::cout << "sync replica hash graph projection tests passed ("
                  << checks << " checks, " << kChainLength
                  << "-operation reverse chain, " << kWideRootCount
                  << "-root fan-in, " << kDifferentialCandidateCount
                  << " differential candidates)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica hash graph projection tests failed: "
                  << error.what() << '\n';
        return 1;
    }
}
