#include "sync_replica_evidence_projection.hpp"

#include "sync_manifest_validation.hpp"
#include "sync_replica_operation_codec_internal.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace anonsync::detail {
namespace {

constexpr std::size_t kNoParent =
    std::numeric_limits<std::size_t>::max();

struct TopTwoParentCoverage final {
    std::size_t first_parent = kNoParent;
    std::uint64_t first_counter = 0U;
    std::size_t second_parent = kNoParent;
    std::uint64_t second_counter = 0U;
};

struct ActorParentAggregate final {
    std::uint64_t expected_counter = 0U;
    TopTwoParentCoverage coverage;
};

void record_parent_coverage(
    TopTwoParentCoverage& coverage,
    std::uint64_t counter,
    std::size_t parent_index) {
    if (coverage.first_parent == parent_index) {
        coverage.first_counter = std::max(coverage.first_counter, counter);
        return;
    }
    if (coverage.second_parent == parent_index) {
        coverage.second_counter = std::max(coverage.second_counter, counter);
        if (coverage.second_counter > coverage.first_counter) {
            std::swap(coverage.first_parent, coverage.second_parent);
            std::swap(coverage.first_counter, coverage.second_counter);
        }
        return;
    }
    if (coverage.first_parent == kNoParent ||
        counter > coverage.first_counter) {
        coverage.second_parent = coverage.first_parent;
        coverage.second_counter = coverage.first_counter;
        coverage.first_parent = parent_index;
        coverage.first_counter = counter;
        return;
    }
    if (coverage.second_parent == kNoParent ||
        counter > coverage.second_counter) {
        coverage.second_parent = parent_index;
        coverage.second_counter = counter;
    }
}

void merge_context(
    std::map<SyncReplicaActor, ActorParentAggregate>& aggregate_by_actor,
    const SyncReplicaOperation& operation,
    std::size_t parent_index) {
    for (const SyncReplicaClockEntry& entry : operation.causal_context) {
        ActorParentAggregate& aggregate = aggregate_by_actor[entry.actor];
        aggregate.expected_counter =
            std::max(aggregate.expected_counter, entry.counter);
        record_parent_coverage(
            aggregate.coverage,
            entry.counter,
            parent_index);
    }
    ActorParentAggregate& dot_aggregate =
        aggregate_by_actor[operation.dot.actor];
    dot_aggregate.expected_counter =
        std::max(dot_aggregate.expected_counter, operation.dot.counter);
    record_parent_coverage(
        dot_aggregate.coverage,
        operation.dot.counter,
        parent_index);
}

[[nodiscard]] bool context_exactly_matches(
    const std::vector<SyncReplicaClockEntry>& declared,
    const std::map<SyncReplicaActor, ActorParentAggregate>& expected) noexcept {
    if (declared.size() != expected.size()) return false;
    auto expected_it = expected.begin();
    for (const SyncReplicaClockEntry& entry : declared) {
        if (expected_it == expected.end() ||
            expected_it->first != entry.actor ||
            expected_it->second.expected_counter != entry.counter) {
            return false;
        }
        ++expected_it;
    }
    return expected_it == expected.end();
}

[[nodiscard]] bool context_dominates_known_parent_aggregate(
    const std::vector<SyncReplicaClockEntry>& declared,
    const std::map<SyncReplicaActor, ActorParentAggregate>& expected) noexcept {
    for (const auto& [actor, aggregate] : expected) {
        if (sync_replica_context_counter(declared, actor) <
            aggregate.expected_counter) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool known_predecessor_subset_is_minimal(
    const SyncReplicaOperation& operation,
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id,
    const std::map<SyncReplicaActor, ActorParentAggregate>&
        aggregate_by_actor) {
    for (std::size_t candidate_index = 0;
         candidate_index < operation.predecessor_operation_ids.size();
         ++candidate_index) {
        const auto candidate = evidence_by_id.find(
            operation.predecessor_operation_ids[candidate_index]);
        if (candidate == evidence_by_id.end()) continue;
        const auto aggregate = aggregate_by_actor.find(
            candidate->second.dot.actor);
        if (aggregate == aggregate_by_actor.end()) {
            throw std::logic_error(
                "sync replica predecessor coverage omitted its own dot");
        }
        const TopTwoParentCoverage& coverage =
            aggregate->second.coverage;
        const std::uint64_t other_parent_counter =
            coverage.first_parent != candidate_index
                ? coverage.first_counter
                : coverage.second_counter;
        if (other_parent_counter >= candidate->second.dot.counter) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] std::map<SyncReplicaActor, ActorParentAggregate>
aggregate_known_predecessors(
    const SyncReplicaOperation& operation,
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id) {
    std::map<SyncReplicaActor, ActorParentAggregate> aggregate_by_actor;
    for (std::size_t parent_index = 0;
         parent_index < operation.predecessor_operation_ids.size();
         ++parent_index) {
        const auto parent = evidence_by_id.find(
            operation.predecessor_operation_ids[parent_index]);
        if (parent == evidence_by_id.end()) continue;
        merge_context(
            aggregate_by_actor,
            parent->second,
            parent_index);
    }
    return aggregate_by_actor;
}

[[nodiscard]] bool causal_envelope_can_still_match(
    const SyncReplicaOperation& operation,
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id,
    bool all_direct_predecessors_known) {
    const std::map<SyncReplicaActor, ActorParentAggregate>
        aggregate_by_actor =
            aggregate_known_predecessors(operation, evidence_by_id);
    const bool context_possible = all_direct_predecessors_known
        ? context_exactly_matches(
              operation.causal_context, aggregate_by_actor)
        : context_dominates_known_parent_aggregate(
              operation.causal_context, aggregate_by_actor);
    return context_possible && known_predecessor_subset_is_minimal(
        operation, evidence_by_id, aggregate_by_actor);
}

[[nodiscard]] SyncReplicaEvidenceState classify_against_active_parents(
    const SyncReplicaOperation& operation,
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id) {
    if (!causal_envelope_can_still_match(
            operation, evidence_by_id, true)) {
        return SyncReplicaEvidenceState::QuarantinedCausalEnvelope;
    }
    return SyncReplicaEvidenceState::Active;
}

}  // namespace

SyncReplicaEvidenceProjection project_sync_replica_evidence_or_throw(
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id,
    const std::string& folder_id,
    const SyncReplicaModelLimits& limits) {
    ::anonsync::detail::validate_sync_replica_model_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            "sync replica projection folder_id must be a lowercase portable sync id");
    }
    if (evidence_by_id.size() > limits.max_operations) {
        throw std::length_error(
            "sync replica retained evidence exceeds configured operation limit");
    }

    std::map<SyncReplicaDot, std::vector<std::string>> ids_by_dot;
    for (const auto& [operation_id, operation] : evidence_by_id) {
        if (operation_id != operation.operation_id) {
            throw std::invalid_argument(
                "sync replica evidence map key does not match operation_id");
        }
        if (operation.folder_id != folder_id) {
            throw std::invalid_argument(
                "sync replica evidence operation belongs to a different folder");
        }
        ids_by_dot[operation.dot].push_back(operation_id);
    }

    SyncReplicaEvidenceProjection projection;

    // A dot is single-writer authority. Retain every conflicting envelope, but
    // select none of them. This decision depends on the complete evidence set,
    // never on which fork arrived first.
    for (const auto& [dot, operation_ids] : ids_by_dot) {
        (void)dot;
        if (operation_ids.size() > 1U) {
            for (const std::string& operation_id : operation_ids) {
                projection.state_by_id.emplace(
                    operation_id,
                    SyncReplicaEvidenceState::QuarantinedDotFork);
            }
        }
    }

    // Resolve the hash graph from roots outward with a dependency worklist.
    // This avoids rescanning the entire graph once per causal depth. The graph
    // walk and parent-minimality aggregation are linear in retained vertices,
    // edges, and parent causal metadata, plus ordered-map/set lookup costs.
    // Ordered ready IDs make diagnostics and execution reproducible, although
    // the classification itself is mathematically independent of that order.
    std::map<std::string, std::vector<std::string>> children_by_parent;
    std::map<std::string, std::size_t> unresolved_parent_counts;
    std::map<std::string, bool> has_missing_predecessor_by_id;
    for (const auto& [operation_id, operation] : evidence_by_id) {
        if (projection.state_by_id.contains(operation_id)) continue;
        std::size_t unresolved = 0U;
        bool has_missing_predecessor = false;
        for (const std::string& predecessor_id :
             operation.predecessor_operation_ids) {
            if (!evidence_by_id.contains(predecessor_id)) {
                has_missing_predecessor = true;
                continue;
            }
            children_by_parent[predecessor_id].push_back(operation_id);
            if (!projection.state_by_id.contains(predecessor_id)) {
                ++unresolved;
            }
        }
        unresolved_parent_counts.emplace(operation_id, unresolved);
        has_missing_predecessor_by_id.emplace(
            operation_id, has_missing_predecessor);
    }

    std::set<std::string> ready;
    for (const auto& [operation_id, unresolved] :
         unresolved_parent_counts) {
        if (unresolved == 0U) ready.insert(operation_id);
    }

    while (!ready.empty()) {
        const std::string operation_id = *ready.begin();
        ready.erase(ready.begin());
        const SyncReplicaOperation& operation =
            evidence_by_id.at(operation_id);

        const bool has_missing_direct_predecessor =
            has_missing_predecessor_by_id.at(operation_id);
        bool has_pending_parent = has_missing_direct_predecessor;
        bool has_quarantined_parent = false;
        for (const std::string& predecessor_id :
             operation.predecessor_operation_ids) {
            if (!evidence_by_id.contains(predecessor_id)) continue;
            const SyncReplicaEvidenceState parent_state =
                projection.state_by_id.at(predecessor_id);
            if (parent_state ==
                SyncReplicaEvidenceState::PendingMissingDependency) {
                has_pending_parent = true;
            } else if (sync_replica_evidence_state_is_quarantined(
                           parent_state)) {
                has_quarantined_parent = true;
            }
        }

        SyncReplicaEvidenceState state;
        // Quarantine dominates absence. Once any exact parent is known to be
        // unusable, this child can never activate, so retaining a "pending"
        // label would both hide transitive quarantine and invite pointless
        // requests for unrelated missing hashes.
        if (has_quarantined_parent) {
            state = SyncReplicaEvidenceState::QuarantinedDependency;
        } else if (has_pending_parent) {
            // A missing hash cannot repair a declaration that already omits a
            // known parent's causal closure or names a known parent together
            // with one of its ancestors. Quarantine such irreversible shapes
            // now so dependency pull does not amplify impossible work. When
            // every direct parent is present but one is itself pending, exact
            // equality is already decidable from those immutable envelopes.
            state = causal_envelope_can_still_match(
                        operation,
                        evidence_by_id,
                        !has_missing_direct_predecessor)
                ? SyncReplicaEvidenceState::PendingMissingDependency
                : SyncReplicaEvidenceState::QuarantinedCausalEnvelope;
        } else {
            state = classify_against_active_parents(
                operation, evidence_by_id);
        }
        projection.state_by_id.emplace(operation_id, state);

        const auto children = children_by_parent.find(operation_id);
        if (children == children_by_parent.end()) continue;
        for (const std::string& child_id : children->second) {
            if (projection.state_by_id.contains(child_id)) continue;
            auto unresolved = unresolved_parent_counts.find(child_id);
            if (unresolved == unresolved_parent_counts.end() ||
                unresolved->second == 0U) {
                throw std::logic_error(
                    "sync replica projection dependency worklist underflow");
            }
            --unresolved->second;
            if (unresolved->second == 0U) ready.insert(child_id);
        }
    }

    // A practical SHA-256 operation graph cannot be deliberately cyclic without
    // finding a fixed point, but fail closed if corrupt/invented evidence ever
    // reaches this pure projection through a future alternate identity scheme.
    for (const auto& [operation_id, operation] : evidence_by_id) {
        (void)operation;
        if (!projection.state_by_id.contains(operation_id)) {
            projection.state_by_id.emplace(
                operation_id,
                SyncReplicaEvidenceState::QuarantinedDependencyCycle);
        }
    }

    for (const auto& [operation_id, state] : projection.state_by_id) {
        if (state == SyncReplicaEvidenceState::Active) {
            projection.active_operation_ids.insert(operation_id);
        }
    }

    projection.causal_head_operation_ids =
        projection.active_operation_ids;
    for (const std::string& operation_id :
         projection.active_operation_ids) {
        const SyncReplicaOperation& operation =
            evidence_by_id.at(operation_id);
        for (const std::string& predecessor_id :
             operation.predecessor_operation_ids) {
            if (!projection.active_operation_ids.contains(predecessor_id)) {
                throw std::logic_error(
                    "sync replica active projection contains an inactive predecessor");
            }
            projection.causal_head_operation_ids.erase(predecessor_id);
        }
    }

    if (projection.state_by_id.size() != evidence_by_id.size()) {
        throw std::logic_error(
            "sync replica evidence projection did not classify every operation");
    }
    return projection;
}

}  // namespace anonsync::detail
