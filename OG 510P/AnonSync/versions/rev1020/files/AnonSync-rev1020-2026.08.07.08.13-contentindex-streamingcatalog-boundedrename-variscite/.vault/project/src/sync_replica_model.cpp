#include "sync_replica_model.hpp"

#include "sha256_digest.hpp"
#include "sync_conflict_resolution.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_digest_accumulator.hpp"
#include "sync_replica_evidence_projection.hpp"
#include "sync_replica_operation_codec_internal.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <type_traits>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

using SyncReplicaOperationMap =
    std::map<std::string, SyncReplicaOperation>;
using SyncReplicaEvidenceStateMap =
    std::map<std::string, SyncReplicaEvidenceState>;

struct RetainedEvidenceCharge final {
    std::uint64_t canonical_bytes = 0;
    std::uint64_t context_entries = 0;
    std::uint64_t predecessor_ids = 0;
};

struct RetainedEvidenceTotals final {
    std::uint64_t canonical_bytes = 0;
    std::uint64_t context_entries = 0;
    std::uint64_t predecessor_ids = 0;
};

static_assert(std::is_nothrow_move_constructible_v<std::string>);
static_assert(std::is_nothrow_swappable_v<SyncReplicaOperationMap>);
static_assert(std::is_nothrow_swappable_v<SyncReplicaEvidenceStateMap>);
static_assert(std::is_nothrow_swappable_v<std::set<std::string>>);

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    std::string_view label) {
    if (std::cmp_greater(
            value, std::numeric_limits<std::uint64_t>::max())) {
        throw std::overflow_error(
            "sync replica " + std::string(label) +
            " does not fit uint64_t");
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] RetainedEvidenceCharge retained_charge_or_throw(
    const SyncReplicaOperation& operation,
    std::uint64_t canonical_bytes) {
    return {
        canonical_bytes,
        size_to_u64_or_throw(
            operation.causal_context.size(), "causal context entry count"),
        size_to_u64_or_throw(
            operation.predecessor_operation_ids.size(),
            "predecessor ID count"),
    };
}

[[nodiscard]] std::uint64_t checked_retained_total_or_throw(
    std::uint64_t current,
    std::uint64_t addition,
    std::uint64_t limit,
    std::string_view label) {
    if (current > limit) {
        throw std::logic_error(
            "sync replica retained " + std::string(label) +
            " counter already exceeds its configured budget");
    }
    if (addition > limit - current) {
        throw std::length_error(
            "sync replica retained evidence exceeds configured aggregate " +
            std::string(label) + " budget");
    }
    return current + addition;
}

[[nodiscard]] RetainedEvidenceTotals prospective_retained_totals_or_throw(
    const RetainedEvidenceTotals& current,
    const RetainedEvidenceCharge& charge,
    const SyncReplicaModelLimits& limits) {
    return {
        checked_retained_total_or_throw(
            current.canonical_bytes,
            charge.canonical_bytes,
            limits.max_retained_canonical_bytes,
            "canonical-byte"),
        checked_retained_total_or_throw(
            current.context_entries,
            charge.context_entries,
            limits.max_retained_context_entries,
            "context-entry"),
        checked_retained_total_or_throw(
            current.predecessor_ids,
            charge.predecessor_ids,
            limits.max_retained_predecessor_ids,
            "predecessor-ID"),
    };
}

[[nodiscard]] SyncReplicaResourceBudget resource_budget_or_throw(
    std::uint64_t retained,
    std::uint64_t incoming,
    std::uint64_t limit,
    std::string_view label) {
    if (retained > limit) {
        throw std::logic_error(
            "sync replica retained " + std::string(label) +
            " counter already exceeds its configured budget");
    }
    return {retained, incoming, limit};
}

[[nodiscard]] bool remote_preflight_is_capacity_blocked(
    const SyncReplicaRemoteAdmissionPreflight& preflight) noexcept {
    return preflight.operations.would_exceed() ||
           preflight.canonical_bytes.would_exceed() ||
           preflight.context_entries.would_exceed() ||
           preflight.predecessor_ids.would_exceed();
}

[[nodiscard]] std::string_view kind_text(
    SyncReplicaValueKind kind) noexcept {
    return kind == SyncReplicaValueKind::Tombstone ? "tombstone" : "file";
}

[[nodiscard]] SyncConflictValueKind conflict_kind(
    SyncReplicaValueKind kind) {
    switch (kind) {
        case SyncReplicaValueKind::File:
            return SyncConflictValueKind::File;
        case SyncReplicaValueKind::Tombstone:
            return SyncConflictValueKind::Tombstone;
    }
    throw std::invalid_argument(
        "sync replica operation has unknown value kind");
}

void append_framed_component(
    Sha256DigestBuilder& digest,
    std::string_view component) {
    std::array<char, 32> decimal{};
    const auto converted = std::to_chars(
        decimal.data(), decimal.data() + decimal.size(), component.size());
    if (converted.ec != std::errc{}) {
        throw std::runtime_error(
            "sync replica digest length formatting failed");
    }
    digest.update(std::string_view(
        decimal.data(),
        static_cast<std::size_t>(converted.ptr - decimal.data())));
    digest.update(":");
    digest.update(component);
}

[[nodiscard]] std::string decimal_u64(std::uint64_t value) {
    std::array<char, 32> decimal{};
    const auto converted = std::to_chars(
        decimal.data(), decimal.data() + decimal.size(), value);
    if (converted.ec != std::errc{}) {
        throw std::runtime_error(
            "sync replica integer formatting failed");
    }
    return std::string(
        decimal.data(),
        static_cast<std::size_t>(converted.ptr - decimal.data()));
}

void validate_expected_visible_operation_ids_or_throw(
    const std::vector<std::string>& operation_ids) {
    if (!std::is_sorted(operation_ids.begin(), operation_ids.end()) ||
        std::adjacent_find(operation_ids.begin(), operation_ids.end()) !=
            operation_ids.end()) {
        throw std::invalid_argument(
            "sync replica observed path heads must be strictly sorted and unique");
    }
    for (const std::string& operation_id : operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                "sync replica observed path head is not a lowercase SHA-256 operation ID");
        }
    }
}

[[nodiscard]] const SyncReplicaOperation*
primary_visible_operation_or_throw(
    const std::vector<const SyncReplicaOperation*>& visible) {
    if (visible.empty()) {
        throw std::logic_error(
            "sync replica visible set unexpectedly has no operations");
    }
    const SyncReplicaOperation* winner = visible.front();
    for (std::size_t index = 1; index < visible.size(); ++index) {
        const SyncReplicaOperation* candidate = visible[index];
        const SyncConflictResolution resolution =
            resolve_sync_conflict_or_throw(
                conflict_kind(winner->kind), winner->operation_id,
                conflict_kind(candidate->kind), candidate->operation_id);
        if (!resolution.local_is_winner()) winner = candidate;
    }
    return winner;
}

[[nodiscard]] SyncReplicaPathView visible_path_view_or_throw(
    std::string_view canonical_path,
    std::span<const SyncReplicaOperation* const> candidates) {
    if (candidates.empty()) {
        throw std::logic_error(
            "sync replica indexed path unexpectedly has no operations");
    }

    // For one candidate to supersede another, its same-path causal context
    // must cover the older operation's exact actor dot. Aggregate the greatest
    // covered counter per actor once. The canonical own-context invariant is
    // dot.counter - 1, so an operation cannot make itself disappear. This is
    // exactly equivalent to the former all-pairs predicate while reducing one
    // long path history from quadratic comparisons to a single context scan.
    std::map<SyncReplicaActor, std::uint64_t> maximum_covered_counter;
    for (const SyncReplicaOperation* candidate : candidates) {
        if (candidate == nullptr ||
            candidate->canonical_path != canonical_path) {
            throw std::logic_error(
                "sync replica indexed path contains an invalid candidate");
        }
        for (const SyncReplicaClockEntry& observed :
             candidate->causal_context) {
            auto [position, inserted] = maximum_covered_counter.emplace(
                observed.actor, observed.counter);
            if (!inserted && position->second < observed.counter) {
                position->second = observed.counter;
            }
        }
    }

    std::vector<const SyncReplicaOperation*> visible;
    visible.reserve(candidates.size());
    for (const SyncReplicaOperation* candidate : candidates) {
        const auto covered = maximum_covered_counter.find(
            candidate->dot.actor);
        if (covered == maximum_covered_counter.end() ||
            covered->second < candidate->dot.counter) {
            visible.push_back(candidate);
        }
    }
    if (visible.empty()) {
        throw std::logic_error(
            "sync replica active path has no maximal operation");
    }
    std::sort(
        visible.begin(), visible.end(),
        [](const SyncReplicaOperation* left,
           const SyncReplicaOperation* right) {
            return left->operation_id < right->operation_id;
        });

    const SyncReplicaOperation* primary =
        primary_visible_operation_or_throw(visible);
    SyncReplicaPathView view;
    view.canonical_path = canonical_path;
    view.visible_operation_ids.reserve(visible.size());
    for (const SyncReplicaOperation* operation : visible) {
        view.visible_operation_ids.push_back(operation->operation_id);
    }
    view.primary_operation_id = primary->operation_id;
    view.primary_kind = primary->kind;
    view.preserved_file_operation_ids.reserve(visible.size() - 1U);
    for (const SyncReplicaOperation* operation : visible) {
        if (operation->kind == SyncReplicaValueKind::File &&
            operation != primary) {
            view.preserved_file_operation_ids.push_back(
                operation->operation_id);
        }
    }
    return view;
}

[[nodiscard]] SyncReplicaAdmission admission_for_state(
    SyncReplicaEvidenceState state) noexcept {
    if (state == SyncReplicaEvidenceState::Active) {
        return SyncReplicaAdmission::InsertedActive;
    }
    if (state == SyncReplicaEvidenceState::PendingMissingDependency) {
        return SyncReplicaAdmission::InsertedPending;
    }
    return SyncReplicaAdmission::InsertedQuarantined;
}

void validate_local_operation_ids_or_throw(
    const SyncReplicaDurableState& durable,
    const SyncReplicaModelLimits& limits) {
    if (durable.last_local_counter > limits.max_operations) {
        throw std::invalid_argument(
            "sync replica durable local counter exceeds configured operation limit");
    }
    if (durable.local_operation_ids.size() != durable.last_local_counter) {
        throw std::invalid_argument(
            "sync replica durable local operation ID sequence length disagrees with its counter");
    }
    std::set<std::string> unique_ids;
    for (const std::string& operation_id : durable.local_operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                "sync replica durable local operation ID is not a lowercase SHA-256 digest");
        }
        if (!unique_ids.insert(operation_id).second) {
            throw std::invalid_argument(
                "sync replica durable local operation ID sequence contains a duplicate");
        }
    }
}

void validate_local_operation_bindings_or_throw(
    const SyncReplicaDurableState& durable,
    const std::map<std::string, SyncReplicaOperation>& evidence) {
    for (std::size_t index = 0;
         index < durable.local_operation_ids.size(); ++index) {
        const std::string& operation_id = durable.local_operation_ids[index];
        const auto operation = evidence.find(operation_id);
        if (operation == evidence.end()) {
            throw std::invalid_argument(
                "sync replica durable local operation ID is absent from retained evidence");
        }
        if (operation->second.dot.actor != durable.local_actor ||
            operation->second.dot.counter != index + 1U) {
            throw std::invalid_argument(
                "sync replica durable local operation ID does not bind its authorized actor counter");
        }
    }
}

}  // namespace

SyncReplicaOperation
make_sync_replica_local_operation_from_causal_heads_or_throw(
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::uint64_t last_local_counter,
    std::string canonical_path,
    SyncReplicaValueKind kind,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const SyncReplicaOperation> causal_heads,
    const SyncReplicaModelLimits& limits) {
    validate_sync_replica_model_limits_or_throw(limits);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            "sync replica local frontier folder_id must be a lowercase portable sync id");
    }
    detail::validate_sync_replica_actor_or_throw(
        local_actor, "sync replica local frontier actor");
    if (last_local_counter == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "sync replica local dot counter is exhausted; rotate actor epoch");
    }
    if (causal_heads.size() > limits.max_predecessor_ids) {
        throw std::length_error(
            "sync replica active causal heads exceed configured predecessor limit");
    }

    std::map<SyncReplicaActor, std::uint64_t> frontier;
    std::string_view previous_operation_id;
    bool first = true;
    std::vector<std::string> predecessor_ids;
    predecessor_ids.reserve(causal_heads.size());
    for (const SyncReplicaOperation& head : causal_heads) {
        validate_sync_replica_operation_or_throw(head, limits);
        if (head.folder_id != folder_id) {
            throw std::invalid_argument(
                "sync replica local frontier head belongs to a different folder");
        }
        if (!first && previous_operation_id >= head.operation_id) {
            throw std::invalid_argument(
                "sync replica local frontier heads must be strictly ordered and unique");
        }
        previous_operation_id = head.operation_id;
        first = false;
        predecessor_ids.push_back(head.operation_id);

        auto& dot_counter = frontier[head.dot.actor];
        dot_counter = std::max(dot_counter, head.dot.counter);
        for (const SyncReplicaClockEntry& entry : head.causal_context) {
            auto& counter = frontier[entry.actor];
            counter = std::max(counter, entry.counter);
        }
    }

    std::vector<SyncReplicaClockEntry> context;
    context.reserve(frontier.size());
    for (const auto& [actor, counter] : frontier) {
        if (counter != 0U) context.push_back({actor, counter});
    }
    if (context.size() > limits.max_context_entries) {
        throw std::length_error(
            "sync replica active causal frontier exceeds configured context limit");
    }
    if (detail::sync_replica_context_counter(context, local_actor) !=
        last_local_counter) {
        throw std::runtime_error(
            "sync replica active frontier disagrees with local counter authority");
    }

    SyncReplicaOperation operation;
    operation.folder_id = std::move(folder_id);
    operation.canonical_path = std::move(canonical_path);
    operation.kind = kind;
    operation.size_bytes = size_bytes;
    operation.content_sha256 = std::move(content_sha256);
    operation.dot = {std::move(local_actor), last_local_counter + 1U};
    operation.causal_context = std::move(context);
    operation.predecessor_operation_ids = std::move(predecessor_ids);
    operation.operation_id =
        make_sync_replica_operation_id_or_throw(operation, limits);
    validate_sync_replica_operation_or_throw(operation, limits);
    return operation;
}

std::string
sync_replica_active_operation_accumulator_element_digest_or_throw(
    std::string_view operation_id) {
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            "sync replica active accumulator operation ID is invalid");
    }
    Sha256DigestBuilder digest;
    digest.update(
        "anonsync-sync-replica-active-operation-accumulator-element-v1");
    append_framed_component(digest, operation_id);
    return digest.finish_hex();
}

std::string
sync_replica_evidence_operation_accumulator_element_digest_or_throw(
    std::string_view operation_id) {
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            "sync replica evidence accumulator operation ID is invalid");
    }
    Sha256DigestBuilder digest;
    digest.update(
        "anonsync-sync-replica-evidence-operation-accumulator-element-v1");
    append_framed_component(digest, operation_id);
    return digest.finish_hex();
}

std::string
sync_replica_visible_path_accumulator_element_digest_or_throw(
    const SyncReplicaPathView& view) {
    const SyncValidationResult path =
        validate_sync_relative_path(view.canonical_path);
    if (!path.ok || view.visible_operation_ids.empty() ||
        !std::is_sorted(
            view.visible_operation_ids.begin(),
            view.visible_operation_ids.end()) ||
        std::adjacent_find(
            view.visible_operation_ids.begin(),
            view.visible_operation_ids.end()) !=
            view.visible_operation_ids.end() ||
        !std::binary_search(
            view.visible_operation_ids.begin(),
            view.visible_operation_ids.end(),
            view.primary_operation_id) ||
        !std::is_sorted(
            view.preserved_file_operation_ids.begin(),
            view.preserved_file_operation_ids.end()) ||
        std::adjacent_find(
            view.preserved_file_operation_ids.begin(),
            view.preserved_file_operation_ids.end()) !=
            view.preserved_file_operation_ids.end()) {
        throw std::invalid_argument(
            "sync replica visible accumulator path view is noncanonical");
    }
    for (const std::string& operation_id : view.visible_operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                "sync replica visible accumulator operation ID is invalid");
        }
    }
    for (const std::string& operation_id :
         view.preserved_file_operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id) ||
            !std::binary_search(
                view.visible_operation_ids.begin(),
                view.visible_operation_ids.end(), operation_id) ||
            operation_id == view.primary_operation_id) {
            throw std::invalid_argument(
                "sync replica visible accumulator preservation set is invalid");
        }
    }

    Sha256DigestBuilder digest;
    digest.update(
        "anonsync-sync-replica-visible-path-accumulator-element-v1");
    append_framed_component(digest, view.canonical_path);
    append_framed_component(digest, view.primary_operation_id);
    append_framed_component(digest, kind_text(view.primary_kind));
    append_framed_component(
        digest, decimal_u64(static_cast<std::uint64_t>(
                    view.visible_operation_ids.size())));
    for (const std::string& operation_id : view.visible_operation_ids) {
        append_framed_component(digest, operation_id);
    }
    append_framed_component(
        digest, decimal_u64(static_cast<std::uint64_t>(
                    view.preserved_file_operation_ids.size())));
    for (const std::string& operation_id :
         view.preserved_file_operation_ids) {
        append_framed_component(digest, operation_id);
    }
    return digest.finish_hex();
}

bool sync_replica_evidence_state_is_quarantined(
    SyncReplicaEvidenceState state) noexcept {
    return state == SyncReplicaEvidenceState::QuarantinedDotFork ||
           state == SyncReplicaEvidenceState::QuarantinedDependency ||
           state == SyncReplicaEvidenceState::QuarantinedCausalEnvelope ||
           state == SyncReplicaEvidenceState::QuarantinedDependencyCycle;
}

SyncReplicaModel::SyncReplicaModel(
    std::string folder_id,
    SyncReplicaActor local_actor,
    SyncReplicaModelLimits limits)
    : folder_id_(std::move(folder_id)),
      local_actor_(std::move(local_actor)),
      limits_(limits) {
    detail::validate_sync_replica_model_limits_impl_or_throw(limits_);
    if (!sync_id_is_valid(folder_id_)) {
        throw std::invalid_argument(
            "sync replica model folder_id must be a lowercase portable sync id");
    }
    detail::validate_sync_replica_actor_or_throw(
        local_actor_, "sync replica local actor");
}

SyncReplicaModel SyncReplicaModel::restore_or_throw(
    SyncReplicaDurableState durable,
    SyncReplicaModelLimits limits) {
    SyncReplicaModel restored(durable.folder_id, durable.local_actor, limits);
    if (durable.operations.size() > limits.max_operations) {
        throw std::invalid_argument(
            "sync replica durable evidence set exceeds configured operation limit");
    }
    validate_local_operation_ids_or_throw(durable, limits);

    std::map<std::string, SyncReplicaOperation> evidence;
    RetainedEvidenceTotals retained_totals;
    for (SyncReplicaOperation& operation : durable.operations) {
        const std::uint64_t canonical_bytes =
            detail::validate_sync_replica_operation_and_measure_or_throw(
                operation, limits);
        if (operation.folder_id != durable.folder_id) {
            throw std::invalid_argument(
                "sync replica durable evidence belongs to a different folder");
        }
        if (!evidence.empty() &&
            evidence.rbegin()->first >= operation.operation_id) {
            throw std::invalid_argument(
                "sync replica durable evidence must be strictly sorted and unique by operation_id");
        }
        retained_totals = prospective_retained_totals_or_throw(
            retained_totals,
            retained_charge_or_throw(operation, canonical_bytes),
            limits);
        std::string operation_id = operation.operation_id;
        const bool inserted = evidence.emplace(
            std::move(operation_id), std::move(operation)).second;
        if (!inserted) {
            throw std::invalid_argument(
                "sync replica durable evidence contains a duplicate operation");
        }
    }
    validate_local_operation_bindings_or_throw(durable, evidence);

    detail::SyncReplicaEvidenceProjection projection =
        detail::project_sync_replica_evidence_or_throw(
            evidence, durable.folder_id, limits);

    restored.last_local_counter_ = durable.last_local_counter;
    restored.local_operation_ids_ = std::move(durable.local_operation_ids);
    restored.evidence_by_id_ = std::move(evidence);
    restored.active_operation_ids_ =
        std::move(projection.active_operation_ids);
    restored.evidence_state_by_id_ = std::move(projection.state_by_id);
    restored.causal_head_operation_ids_ =
        std::move(projection.causal_head_operation_ids);
    restored.retained_canonical_bytes_ = retained_totals.canonical_bytes;
    restored.retained_context_entries_ = retained_totals.context_entries;
    restored.retained_predecessor_ids_ = retained_totals.predecessor_ids;
    restored.local_actor_compromised_ =
        restored.compute_local_actor_compromised(
            restored.evidence_by_id_,
            restored.evidence_state_by_id_,
            restored.local_operation_ids_);
    return restored;
}

SyncReplicaOperation SyncReplicaModel::create_local_file_or_throw(
    std::string canonical_path,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_operation_or_throw(
        std::move(canonical_path),
        SyncReplicaValueKind::File,
        size_bytes,
        std::move(content_sha256),
        std::nullopt,
        LocalMutationPurpose::Ordinary);
}

SyncReplicaOperation
SyncReplicaModel::create_local_file_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_operation_or_throw(
        std::move(canonical_path),
        SyncReplicaValueKind::File,
        size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            observed_visible_operation_ids.begin(),
            observed_visible_operation_ids.end()),
        LocalMutationPurpose::Ordinary);
}

SyncReplicaOperation SyncReplicaModel::resolve_local_file_conflict_or_throw(
    std::string canonical_path,
    std::span<const std::string> expected_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_operation_or_throw(
        std::move(canonical_path),
        SyncReplicaValueKind::File,
        size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            expected_visible_operation_ids.begin(),
            expected_visible_operation_ids.end()),
        LocalMutationPurpose::ConflictResolution);
}

SyncReplicaOperation SyncReplicaModel::create_local_tombstone_or_throw(
    std::string canonical_path) {
    return create_local_operation_or_throw(
        std::move(canonical_path),
        SyncReplicaValueKind::Tombstone,
        0U,
        {},
        std::nullopt,
        LocalMutationPurpose::Ordinary);
}

SyncReplicaOperation
SyncReplicaModel::create_local_tombstone_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids) {
    return create_local_operation_or_throw(
        std::move(canonical_path),
        SyncReplicaValueKind::Tombstone,
        0U,
        {},
        std::vector<std::string>(
            observed_visible_operation_ids.begin(),
            observed_visible_operation_ids.end()),
        LocalMutationPurpose::Ordinary);
}

SyncReplicaOperation SyncReplicaModel::create_local_operation_or_throw(
    std::string canonical_path,
    SyncReplicaValueKind kind,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::optional<std::vector<std::string>> expected_visible_operation_ids,
    LocalMutationPurpose purpose) {
    const std::optional<SyncReplicaPathView> current_path =
        visible_path(canonical_path);
    const std::vector<std::string> current_visible_operation_ids =
        current_path.has_value()
            ? current_path->visible_operation_ids
            : std::vector<std::string>{};
    if (expected_visible_operation_ids.has_value()) {
        validate_expected_visible_operation_ids_or_throw(
            expected_visible_operation_ids.value());
        if (expected_visible_operation_ids.value() !=
            current_visible_operation_ids) {
            throw std::runtime_error(
                "sync replica observed path heads changed before local publication");
        }
    }
    if (purpose == LocalMutationPurpose::ConflictResolution) {
        if (!expected_visible_operation_ids.has_value()) {
            throw std::logic_error(
                "sync replica conflict resolution requires an exact expected path-head set");
        }
        if (current_visible_operation_ids.size() < 2U) {
            throw std::runtime_error(
                "sync replica path is not currently conflicted");
        }
    } else if (current_visible_operation_ids.size() > 1U) {
        throw std::runtime_error(
            "sync replica path has unresolved conflict; explicit resolution is required");
    }

    if (local_actor_compromised_) {
        throw std::runtime_error(
            "sync replica local actor epoch is compromised; rotate epoch before minting");
    }
    if (last_local_counter_ == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "sync replica local dot counter is exhausted; rotate actor epoch");
    }
    if (evidence_by_id_.size() >= limits_.max_operations) {
        throw std::length_error(
            "sync replica retained evidence reached configured operation limit");
    }
    if (causal_head_operation_ids_.size() >
        limits_.max_predecessor_ids) {
        throw std::length_error(
            "sync replica active causal heads exceed configured predecessor limit");
    }

    SyncReplicaOperation operation;
    operation.folder_id = folder_id_;
    operation.canonical_path = std::move(canonical_path);
    operation.kind = kind;
    operation.size_bytes = size_bytes;
    operation.content_sha256 = std::move(content_sha256);
    operation.dot = {local_actor_, last_local_counter_ + 1U};
    operation.causal_context = observed_context();
    operation.predecessor_operation_ids.assign(
        causal_head_operation_ids_.begin(),
        causal_head_operation_ids_.end());

    const std::uint64_t own_frontier =
        detail::sync_replica_context_counter(
            operation.causal_context, local_actor_);
    if (own_frontier != last_local_counter_) {
        throw std::logic_error(
            "sync replica active frontier disagrees with local counter authority");
    }
    operation.operation_id =
        make_sync_replica_operation_id_or_throw(operation, limits_);
    const RetainedEvidenceCharge retained_charge = retained_charge_or_throw(
        operation,
        sync_replica_operation_canonical_size_or_throw(operation, limits_));
    const RetainedEvidenceTotals retained_totals =
        prospective_retained_totals_or_throw(
            {retained_canonical_bytes_,
             retained_context_entries_,
             retained_predecessor_ids_},
            retained_charge,
            limits_);

    // Stage the only potentially allocating local-authority changes before
    // publishing evidence. Reserving capacity is not semantically observable,
    // and the later move of a prepared std::string cannot allocate. This avoids
    // both an exception window and an O(local history) vector clone per write.
    if (local_operation_ids_.size() == local_operation_ids_.max_size()) {
        throw std::length_error(
            "sync replica local operation ID sequence reached vector max_size");
    }
    local_operation_ids_.reserve(local_operation_ids_.size() + 1U);
    std::string staged_local_operation_id = operation.operation_id;

    const auto inserted = evidence_by_id_.emplace(
        operation.operation_id, operation);
    if (!inserted.second) {
        throw std::logic_error(
            "sync replica minted operation unexpectedly matched retained evidence");
    }
    try {
        detail::SyncReplicaEvidenceProjection projection =
            detail::project_sync_replica_evidence_or_throw(
                evidence_by_id_, folder_id_, limits_);
        const auto new_state =
            projection.state_by_id.find(operation.operation_id);
        if (new_state == projection.state_by_id.end() ||
            new_state->second != SyncReplicaEvidenceState::Active) {
            throw std::logic_error(
                "sync replica locally minted operation did not project active");
        }
        if (compute_local_actor_compromised(
                evidence_by_id_,
                projection.state_by_id,
                local_operation_ids_,
                &operation.operation_id)) {
            throw std::logic_error(
                "sync replica locally minted operation compromised its own actor epoch");
        }

        // Capacity and the string payload were staged before evidence insertion.
        // No subsequent operation can throw: default-container swaps and the
        // prepared string move are noexcept under this model's concrete types.
        local_operation_ids_.push_back(
            std::move(staged_local_operation_id));
        active_operation_ids_.swap(projection.active_operation_ids);
        evidence_state_by_id_.swap(projection.state_by_id);
        causal_head_operation_ids_.swap(
            projection.causal_head_operation_ids);
        last_local_counter_ = operation.dot.counter;
        retained_canonical_bytes_ = retained_totals.canonical_bytes;
        retained_context_entries_ = retained_totals.context_entries;
        retained_predecessor_ids_ = retained_totals.predecessor_ids;
    } catch (...) {
        evidence_by_id_.erase(inserted.first);
        throw;
    }
    return operation;
}

SyncReplicaRemoteAdmissionPreflight
SyncReplicaModel::preflight_remote_admission_or_throw(
    const SyncReplicaOperation& operation) const {
    // Exact replay is already authorized by the immutable retained owner. Avoid
    // re-encoding and rehashing a potentially large envelope on every retry. A
    // same-ID but nonidentical value still takes the full validation path below
    // and can only survive it if SHA-256 itself collides.
    const auto duplicate = evidence_by_id_.find(operation.operation_id);
    if (duplicate != evidence_by_id_.end() &&
        duplicate->second == operation) {
        return {
            SyncReplicaRemoteReadiness::Duplicate,
            resource_budget_or_throw(
                size_to_u64_or_throw(
                    evidence_by_id_.size(), "retained evidence count"),
                0U,
                limits_.max_operations,
                "operation-count"),
            resource_budget_or_throw(
                retained_canonical_bytes_,
                0U,
                limits_.max_retained_canonical_bytes,
                "canonical-byte"),
            resource_budget_or_throw(
                retained_context_entries_,
                0U,
                limits_.max_retained_context_entries,
                "context-entry"),
            resource_budget_or_throw(
                retained_predecessor_ids_,
                0U,
                limits_.max_retained_predecessor_ids,
                "predecessor-ID"),
        };
    }

    const std::uint64_t canonical_bytes =
        detail::validate_sync_replica_operation_and_measure_or_throw(
            operation, limits_);
    if (operation.folder_id != folder_id_) {
        throw std::invalid_argument(
            "sync replica rejected evidence from a different folder");
    }
    if (duplicate != evidence_by_id_.end()) {
        throw std::runtime_error(
            "sync replica operation digest collision changed canonical bytes");
    }
    const RetainedEvidenceCharge retained_charge = retained_charge_or_throw(
        operation, canonical_bytes);
    SyncReplicaRemoteAdmissionPreflight preflight{
        SyncReplicaRemoteReadiness::Admissible,
        resource_budget_or_throw(
            size_to_u64_or_throw(
                evidence_by_id_.size(), "retained evidence count"),
            1U,
            limits_.max_operations,
            "operation-count"),
        resource_budget_or_throw(
            retained_canonical_bytes_,
            retained_charge.canonical_bytes,
            limits_.max_retained_canonical_bytes,
            "canonical-byte"),
        resource_budget_or_throw(
            retained_context_entries_,
            retained_charge.context_entries,
            limits_.max_retained_context_entries,
            "context-entry"),
        resource_budget_or_throw(
            retained_predecessor_ids_,
            retained_charge.predecessor_ids,
            limits_.max_retained_predecessor_ids,
            "predecessor-ID"),
    };
    if (remote_preflight_is_capacity_blocked(preflight)) {
        preflight.readiness = SyncReplicaRemoteReadiness::CapacityBlocked;
    }
    return preflight;
}

SyncReplicaAdmission SyncReplicaModel::accept_remote_or_throw(
    const SyncReplicaOperation& operation) {
    const SyncReplicaRemoteAdmissionPreflight preflight =
        preflight_remote_admission_or_throw(operation);
    if (preflight.readiness == SyncReplicaRemoteReadiness::Duplicate) {
        return SyncReplicaAdmission::Duplicate;
    }
    if (preflight.readiness ==
        SyncReplicaRemoteReadiness::CapacityBlocked) {
        return SyncReplicaAdmission::CapacityBlocked;
    }
    return accept_remote_admissible_after_preflight_or_throw(
        operation, preflight);
}

SyncReplicaAdmission
SyncReplicaModel::accept_remote_admissible_after_preflight_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaRemoteAdmissionPreflight& preflight) {
    const std::uint64_t evidence_count = size_to_u64_or_throw(
        evidence_by_id_.size(), "retained evidence count");
    if (preflight.readiness != SyncReplicaRemoteReadiness::Admissible ||
        remote_preflight_is_capacity_blocked(preflight) ||
        preflight.operations != SyncReplicaResourceBudget{
            evidence_count, 1U, limits_.max_operations} ||
        preflight.canonical_bytes.retained != retained_canonical_bytes_ ||
        preflight.canonical_bytes.limit !=
            limits_.max_retained_canonical_bytes ||
        preflight.context_entries.retained != retained_context_entries_ ||
        preflight.context_entries.limit !=
            limits_.max_retained_context_entries ||
        preflight.predecessor_ids.retained != retained_predecessor_ids_ ||
        preflight.predecessor_ids.limit !=
            limits_.max_retained_predecessor_ids ||
        evidence_by_id_.contains(operation.operation_id)) {
        throw std::logic_error(
            "sync replica remote admission preflight is stale or inconsistent with its model owner");
    }
    const RetainedEvidenceTotals retained_totals{
        preflight.canonical_bytes.retained +
            preflight.canonical_bytes.incoming,
        preflight.context_entries.retained +
            preflight.context_entries.incoming,
        preflight.predecessor_ids.retained +
            preflight.predecessor_ids.incoming,
    };

    const auto inserted = evidence_by_id_.emplace(
        operation.operation_id, operation);
    if (!inserted.second) {
        throw std::logic_error(
            "sync replica remote evidence unexpectedly became a duplicate during admission");
    }
    try {
        detail::SyncReplicaEvidenceProjection projection =
            detail::project_sync_replica_evidence_or_throw(
                evidence_by_id_, folder_id_, limits_);
        const SyncReplicaEvidenceState incoming_state =
            projection.state_by_id.at(operation.operation_id);
        const bool compromised = compute_local_actor_compromised(
            evidence_by_id_,
            projection.state_by_id,
            local_operation_ids_);

        active_operation_ids_.swap(projection.active_operation_ids);
        evidence_state_by_id_.swap(projection.state_by_id);
        causal_head_operation_ids_.swap(
            projection.causal_head_operation_ids);
        local_actor_compromised_ = compromised;
        retained_canonical_bytes_ = retained_totals.canonical_bytes;
        retained_context_entries_ = retained_totals.context_entries;
        retained_predecessor_ids_ = retained_totals.predecessor_ids;
        return admission_for_state(incoming_state);
    } catch (...) {
        evidence_by_id_.erase(inserted.first);
        throw;
    }
}

bool SyncReplicaModel::compute_local_actor_compromised(
    const std::map<std::string, SyncReplicaOperation>& evidence,
    const std::map<std::string, SyncReplicaEvidenceState>& states,
    const std::vector<std::string>& local_operation_ids,
    const std::string* appended_local_operation_id) const noexcept {
    const std::size_t authorized_count =
        local_operation_ids.size() +
        (appended_local_operation_id != nullptr ? 1U : 0U);
    const auto authorized_id_at = [&](std::size_t index) noexcept
        -> const std::string& {
        if (index < local_operation_ids.size()) {
            return local_operation_ids[index];
        }
        return *appended_local_operation_id;
    };

    for (std::size_t index = 0; index < authorized_count; ++index) {
        const std::string& authorized_id = authorized_id_at(index);
        const auto operation = evidence.find(authorized_id);
        const auto state = states.find(authorized_id);
        if (operation == evidence.end() || state == states.end() ||
            operation->second.dot.actor != local_actor_ ||
            operation->second.dot.counter != index + 1U ||
            state->second != SyncReplicaEvidenceState::Active) {
            return true;
        }
    }

    for (const auto& [operation_id, operation] : evidence) {
        if (operation.dot.actor != local_actor_) continue;
        if (operation.dot.counter <= authorized_count) {
            const std::size_t index = static_cast<std::size_t>(
                operation.dot.counter - 1U);
            if (authorized_id_at(index) != operation_id) return true;
            continue;
        }
        // Applicability is irrelevant to local minting authority. Any retained
        // envelope in this process's actor epoch that was not minted by this
        // durable authority is evidence of namespace reuse or compromise. In
        // particular, a forged future dot with a missing dependency must stop
        // minting immediately rather than lying dormant until that dot collides.
        return true;
    }
    return false;
}

std::size_t SyncReplicaModel::pending_operation_count() const noexcept {
    return static_cast<std::size_t>(std::count_if(
        evidence_state_by_id_.begin(), evidence_state_by_id_.end(),
        [](const auto& entry) {
            return entry.second ==
                   SyncReplicaEvidenceState::PendingMissingDependency;
        }));
}

std::size_t SyncReplicaModel::quarantined_operation_count() const noexcept {
    return static_cast<std::size_t>(std::count_if(
        evidence_state_by_id_.begin(), evidence_state_by_id_.end(),
        [](const auto& entry) {
            return sync_replica_evidence_state_is_quarantined(entry.second);
        }));
}

std::optional<SyncReplicaEvidenceState> SyncReplicaModel::evidence_state(
    const std::string& operation_id) const noexcept {
    const auto found = evidence_state_by_id_.find(operation_id);
    if (found == evidence_state_by_id_.end()) return std::nullopt;
    return found->second;
}

std::optional<SyncReplicaOperation> SyncReplicaModel::operation_by_id(
    const std::string& operation_id) const {
    const SyncReplicaOperation* operation =
        active_operation_by_id_or_none(operation_id);
    if (operation == nullptr) return std::nullopt;
    return *operation;
}

const SyncReplicaOperation*
SyncReplicaModel::active_operation_by_id_or_none(
    const std::string& operation_id) const {
    if (!active_operation_ids_.contains(operation_id)) return nullptr;
    const auto found = evidence_by_id_.find(operation_id);
    if (found == evidence_by_id_.end()) {
        throw std::logic_error(
            "sync replica active operation ID is absent from evidence");
    }
    return &found->second;
}

std::optional<SyncReplicaOperation>
SyncReplicaModel::evidence_operation_by_id(
    const std::string& operation_id) const {
    const auto found = evidence_by_id_.find(operation_id);
    if (found == evidence_by_id_.end()) return std::nullopt;
    return found->second;
}

std::vector<SyncReplicaOperation> SyncReplicaModel::all_operations() const {
    std::vector<SyncReplicaOperation> operations;
    operations.reserve(active_operation_ids_.size());
    for (const std::string& operation_id : active_operation_ids_) {
        operations.push_back(evidence_by_id_.at(operation_id));
    }
    return operations;
}

std::vector<SyncReplicaOperation>
SyncReplicaModel::all_evidence_operations() const {
    std::vector<SyncReplicaOperation> operations;
    operations.reserve(evidence_by_id_.size());
    for (const auto& [operation_id, operation] : evidence_by_id_) {
        (void)operation_id;
        operations.push_back(operation);
    }
    return operations;
}

std::vector<SyncReplicaClockEntry> SyncReplicaModel::observed_context() const {
    std::map<SyncReplicaActor, std::uint64_t> frontier;
    // Every active operation is either a head or an ancestor of one. Exact
    // predecessor closure therefore lets the heads summarize the complete
    // active frontier; rescanning every retained active envelope only repeats
    // transitive metadata and turns long histories into needless work.
    for (const std::string& operation_id : causal_head_operation_ids_) {
        const SyncReplicaOperation& operation =
            evidence_by_id_.at(operation_id);
        auto& dot_counter = frontier[operation.dot.actor];
        dot_counter = std::max(dot_counter, operation.dot.counter);
        for (const SyncReplicaClockEntry& entry : operation.causal_context) {
            auto& counter = frontier[entry.actor];
            counter = std::max(counter, entry.counter);
        }
    }

    std::vector<SyncReplicaClockEntry> context;
    context.reserve(frontier.size());
    for (const auto& [actor, counter] : frontier) {
        if (counter != 0U) context.push_back({actor, counter});
    }
    if (context.size() > limits_.max_context_entries) {
        throw std::length_error(
            "sync replica active causal frontier exceeds configured context limit");
    }
    return context;
}

std::vector<std::string>
SyncReplicaModel::causal_head_operation_ids() const {
    return std::vector<std::string>(
        causal_head_operation_ids_.begin(),
        causal_head_operation_ids_.end());
}

std::vector<std::string>
SyncReplicaModel::missing_predecessor_operation_ids() const {
    std::set<std::string> missing;
    for (const auto& [operation_id, operation] : evidence_by_id_) {
        const auto state = evidence_state_by_id_.find(operation_id);
        if (state == evidence_state_by_id_.end() ||
            state->second !=
                SyncReplicaEvidenceState::PendingMissingDependency) {
            continue;
        }
        for (const std::string& predecessor_id :
             operation.predecessor_operation_ids) {
            if (!evidence_by_id_.contains(predecessor_id)) {
                missing.insert(predecessor_id);
            }
        }
    }
    return std::vector<std::string>(missing.begin(), missing.end());
}

std::optional<SyncReplicaPathView> SyncReplicaModel::visible_path(
    const std::string& canonical_path) const {
    const SyncValidationResult path =
        validate_sync_relative_path(canonical_path);
    if (!path.ok) {
        throw std::invalid_argument(
            "sync replica visible path lookup is not canonical: " + path.reason);
    }

    std::vector<const SyncReplicaOperation*> candidates;
    for (const std::string& operation_id : active_operation_ids_) {
        const SyncReplicaOperation& operation =
            evidence_by_id_.at(operation_id);
        if (operation.canonical_path == canonical_path) {
            candidates.push_back(&operation);
        }
    }
    if (candidates.empty()) return std::nullopt;
    return visible_path_view_from_active_candidates_or_throw(
        std::span<const SyncReplicaOperation* const>(
            candidates.data(), candidates.size()));
}

std::optional<SyncReplicaIdentityPreservingRename>
SyncReplicaModel::identity_preserving_rename_for_source_tombstone(
    const std::string& source_tombstone_operation_id) const {
    const SyncReplicaOperation* source_tombstone =
        active_operation_by_id_or_none(source_tombstone_operation_id);
    if (source_tombstone == nullptr ||
        source_tombstone->kind != SyncReplicaValueKind::Tombstone ||
        source_tombstone->predecessor_operation_ids.size() != 1U) {
        return std::nullopt;
    }

    const SyncReplicaOperation* destination_file =
        active_operation_by_id_or_none(
            source_tombstone->predecessor_operation_ids.front());
    if (destination_file == nullptr ||
        destination_file->kind != SyncReplicaValueKind::File ||
        destination_file->canonical_path ==
            source_tombstone->canonical_path ||
        destination_file->dot.actor != source_tombstone->dot.actor ||
        destination_file->dot.counter ==
            std::numeric_limits<std::uint64_t>::max() ||
        source_tombstone->dot.counter !=
            destination_file->dot.counter + 1U ||
        !sync_replica_context_covers_dot(
            source_tombstone->causal_context, destination_file->dot)) {
        return std::nullopt;
    }

    // Reconstruct the exact namespace projection that the destination File had
    // observed, one canonical path at a time. Identity is recognized only when
    // exactly one visible File anywhere in that causal past has the destination
    // content. This rejects duplicate-content ambiguity rather than letting a
    // later source tombstone arbitrarily choose one of several indistinguishable
    // predecessors. The method remains diagnostic O(active evidence), with one
    // pointer projection plus one path-local candidate buffer.
    const std::vector<const SyncReplicaOperation*> ordered =
        ordered_active_operations_by_path();
    std::vector<const SyncReplicaOperation*> observed_path_candidates;
    const SyncReplicaOperation* source_file = nullptr;
    const SyncReplicaOperation* sole_matching_file = nullptr;
    std::size_t index = 0U;
    while (index < ordered.size()) {
        const std::string_view path = ordered[index]->canonical_path;
        observed_path_candidates.clear();
        std::size_t next = index;
        while (next < ordered.size() &&
               ordered[next]->canonical_path == path) {
            if (sync_replica_context_covers_dot(
                    destination_file->causal_context, ordered[next]->dot)) {
                observed_path_candidates.push_back(ordered[next]);
            }
            ++next;
        }
        index = next;
        if (observed_path_candidates.empty()) continue;

        const SyncReplicaPathView observed_path =
            visible_path_view_from_active_candidates_or_throw(
                std::span<const SyncReplicaOperation* const>(
                    observed_path_candidates.data(),
                    observed_path_candidates.size()));
        if (path == source_tombstone->canonical_path) {
            if (observed_path.visible_operation_ids.size() != 1U ||
                observed_path.primary_kind != SyncReplicaValueKind::File ||
                !observed_path.preserved_file_operation_ids.empty()) {
                return std::nullopt;
            }
            source_file = active_operation_by_id_or_none(
                observed_path.primary_operation_id);
        }

        for (const std::string& visible_operation_id :
             observed_path.visible_operation_ids) {
            const SyncReplicaOperation* visible =
                active_operation_by_id_or_none(visible_operation_id);
            if (visible != nullptr &&
                visible->kind == SyncReplicaValueKind::File &&
                visible->size_bytes == destination_file->size_bytes &&
                visible->content_sha256 ==
                    destination_file->content_sha256) {
                if (sole_matching_file != nullptr) return std::nullopt;
                sole_matching_file = visible;
            }
        }
    }

    if (source_file == nullptr || sole_matching_file != source_file ||
        source_file->kind != SyncReplicaValueKind::File ||
        source_file->canonical_path != source_tombstone->canonical_path ||
        !sync_replica_context_covers_dot(
            destination_file->causal_context, source_file->dot) ||
        !sync_replica_context_covers_dot(
            source_tombstone->causal_context, source_file->dot)) {
        return std::nullopt;
    }

    return SyncReplicaIdentityPreservingRename{
        source_file->canonical_path,
        destination_file->canonical_path,
        source_file->operation_id,
        destination_file->operation_id,
        source_tombstone->operation_id,
        destination_file->size_bytes,
        destination_file->content_sha256};
}

std::vector<const SyncReplicaOperation*>
SyncReplicaModel::ordered_active_operations_by_path() const {
    // One sorted pointer vector avoids a map node and a separately allocated
    // vector for every distinct path. Equal-path pointers are operation-ID
    // ordered, matching active_operation_ids_ while making each borrowed span
    // deterministic. Callers consume one visible projection at a time without
    // cloning every path view or repeatedly rescanning the complete model.
    std::vector<const SyncReplicaOperation*> ordered;
    ordered.reserve(active_operation_ids_.size());
    for (const std::string& operation_id : active_operation_ids_) {
        ordered.push_back(&evidence_by_id_.at(operation_id));
    }
    std::sort(
        ordered.begin(), ordered.end(),
        [](const SyncReplicaOperation* left,
           const SyncReplicaOperation* right) {
            if (left->canonical_path != right->canonical_path) {
                return left->canonical_path < right->canonical_path;
            }
            return left->operation_id < right->operation_id;
        });
    return ordered;
}

SyncReplicaPathView
SyncReplicaModel::visible_path_view_from_active_candidates_or_throw(
    std::span<const SyncReplicaOperation* const> candidates) const {
    if (candidates.empty() || candidates.front() == nullptr) {
        throw std::logic_error(
            "sync replica active-path projection has no first operation");
    }
    return visible_path_view_or_throw(
        candidates.front()->canonical_path, candidates);
}

std::vector<SyncReplicaPathView> SyncReplicaModel::visible_paths() const {
    std::vector<SyncReplicaPathView> views;
    for_each_active_path(
        [&](const SyncReplicaPathView& view,
            std::span<const SyncReplicaOperation* const>) {
            views.push_back(view);
        });
    return views;
}

std::string SyncReplicaModel::operation_set_digest() const {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-active-operation-set-v2");
    append_framed_component(digest, "folder_id");
    append_framed_component(digest, folder_id_);
    append_framed_component(digest, "operation_count");
    append_framed_component(
        digest,
        decimal_u64(static_cast<std::uint64_t>(active_operation_ids_.size())));
    for (const std::string& operation_id : active_operation_ids_) {
        append_framed_component(digest, "operation_id");
        append_framed_component(digest, operation_id);
    }
    return digest.finish_hex();
}

std::string SyncReplicaModel::evidence_set_digest() const {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-evidence-set-v1");
    append_framed_component(digest, "folder_id");
    append_framed_component(digest, folder_id_);
    append_framed_component(digest, "evidence_count");
    append_framed_component(
        digest,
        decimal_u64(static_cast<std::uint64_t>(evidence_by_id_.size())));
    for (const auto& [operation_id, operation] : evidence_by_id_) {
        (void)operation;
        append_framed_component(digest, "operation_id");
        append_framed_component(digest, operation_id);
    }
    return digest.finish_hex();
}

std::string SyncReplicaModel::visible_state_digest() const {
    const std::vector<SyncReplicaPathView> views = visible_paths();
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-visible-state-v2");
    append_framed_component(digest, "folder_id");
    append_framed_component(digest, folder_id_);
    append_framed_component(digest, "path_count");
    append_framed_component(
        digest,
        decimal_u64(static_cast<std::uint64_t>(views.size())));
    for (const SyncReplicaPathView& view : views) {
        append_framed_component(digest, "canonical_path");
        append_framed_component(digest, view.canonical_path);
        append_framed_component(digest, "primary_operation_id");
        append_framed_component(digest, view.primary_operation_id);
        append_framed_component(digest, "primary_kind");
        append_framed_component(digest, kind_text(view.primary_kind));
        append_framed_component(digest, "visible_count");
        append_framed_component(
            digest,
            decimal_u64(static_cast<std::uint64_t>(
                view.visible_operation_ids.size())));
        for (const std::string& operation_id :
             view.visible_operation_ids) {
            append_framed_component(digest, "visible_operation_id");
            append_framed_component(digest, operation_id);
        }
        append_framed_component(digest, "preserved_file_count");
        append_framed_component(
            digest,
            decimal_u64(static_cast<std::uint64_t>(
                view.preserved_file_operation_ids.size())));
        for (const std::string& operation_id :
             view.preserved_file_operation_ids) {
            append_framed_component(
                digest, "preserved_file_operation_id");
            append_framed_component(digest, operation_id);
        }
    }
    return digest.finish_hex();
}

std::string SyncReplicaModel::operation_set_accumulator_digest() const {
    std::string accumulator = sync_replica_digest_accumulator_zero();
    for (const std::string& operation_id : active_operation_ids_) {
        accumulator = sync_replica_digest_accumulator_add_or_throw(
            accumulator,
            sync_replica_active_operation_accumulator_element_digest_or_throw(
                operation_id));
    }
    return accumulator;
}

std::string SyncReplicaModel::evidence_set_accumulator_digest() const {
    std::string accumulator = sync_replica_digest_accumulator_zero();
    for (const auto& [operation_id, operation] : evidence_by_id_) {
        (void)operation;
        accumulator = sync_replica_digest_accumulator_add_or_throw(
            accumulator,
            sync_replica_evidence_operation_accumulator_element_digest_or_throw(
                operation_id));
    }
    return accumulator;
}

std::uint64_t SyncReplicaModel::visible_path_count() const {
    std::uint64_t count = 0U;
    for_each_active_path(
        [&](const SyncReplicaPathView&,
            std::span<const SyncReplicaOperation* const>) {
            if (count == std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error(
                    "sync replica visible path count overflow");
            }
            ++count;
        });
    return count;
}

std::string SyncReplicaModel::visible_state_accumulator_digest() const {
    std::string accumulator = sync_replica_digest_accumulator_zero();
    for_each_active_path(
        [&](const SyncReplicaPathView& view,
            std::span<const SyncReplicaOperation* const>) {
            accumulator = sync_replica_digest_accumulator_add_or_throw(
                accumulator,
                sync_replica_visible_path_accumulator_element_digest_or_throw(
                    view));
        });
    return accumulator;
}

SyncReplicaDurableState SyncReplicaModel::durable_state() const {
    SyncReplicaDurableState durable;
    durable.folder_id = folder_id_;
    durable.local_actor = local_actor_;
    durable.last_local_counter = last_local_counter_;
    durable.local_operation_ids = local_operation_ids_;
    durable.operations = all_evidence_operations();
    return durable;
}

}  // namespace anonsync
