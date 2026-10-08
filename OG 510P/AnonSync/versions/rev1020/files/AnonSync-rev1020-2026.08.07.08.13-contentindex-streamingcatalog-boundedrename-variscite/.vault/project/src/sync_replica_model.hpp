#pragma once

#include <algorithm>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <map>
#include <optional>
#include <set>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// Executable reference semantics for AnonSync's causal convergence layer.
// The model retains immutable evidence and deterministically projects the
// active operation graph. It is intentionally not a production storage engine.
enum class SyncReplicaValueKind {
    File,
    Tombstone,
};

// An epoch is part of the event-minting authority. A replica that loses its
// durable counter state must never silently reuse the old (device, epoch)
// namespace; it must start under a new epoch instead.
struct SyncReplicaActor final {
    std::string device_id;
    std::uint64_t epoch = 0;

    auto operator<=>(const SyncReplicaActor&) const = default;
};

struct SyncReplicaDot final {
    SyncReplicaActor actor;
    std::uint64_t counter = 0;

    auto operator<=>(const SyncReplicaDot&) const = default;
};

struct SyncReplicaClockEntry final {
    SyncReplicaActor actor;
    std::uint64_t counter = 0;

    auto operator<=>(const SyncReplicaClockEntry&) const = default;
};

struct SyncReplicaOperation final {
    std::string operation_id;
    std::string folder_id;
    std::string canonical_path;
    SyncReplicaValueKind kind = SyncReplicaValueKind::File;
    std::uint64_t size_bytes = 0;
    std::string content_sha256;
    SyncReplicaDot dot;
    std::vector<SyncReplicaClockEntry> causal_context;

    // Exact immediate causal dependencies. IDs are strictly sorted and unique.
    // The operation ID commits to this set. A receiver can therefore distinguish
    // "the vector says something happened" from possession of the exact bytes
    // that allegedly happened, request missing nodes, and defer applicability
    // without letting absent history contaminate its active frontier.
    std::vector<std::string> predecessor_operation_ids;

    bool operator==(const SyncReplicaOperation&) const = default;
};

struct SyncReplicaModelLimits final {
    // This bound applies to retained evidence, not merely active operations.
    // Pending and quarantined evidence is still attacker-controlled memory.
    std::uint64_t max_operations = 10000;
    std::uint64_t max_context_entries = 4096;
    std::uint64_t max_predecessor_ids = 4096;
    std::uint64_t max_canonical_operation_bytes = 4U * 1024U * 1024U;

    // Per-envelope ceilings do not bound the aggregate retained attack surface:
    // max_operations envelopes at the canonical-byte ceiling would otherwise
    // authorize roughly 40 GiB before map/vector/string overhead at the defaults.
    // These independent cumulative budgets charge active, pending, and
    // quarantined evidence alike.
    std::uint64_t max_retained_canonical_bytes =
        256ULL * 1024ULL * 1024ULL;
    std::uint64_t max_retained_context_entries = 1000000ULL;
    std::uint64_t max_retained_predecessor_ids = 1000000ULL;

    bool operator==(const SyncReplicaModelLimits&) const = default;
};

// Shared fail-fast configuration boundary for storage owners, wire decoders,
// simulators, and future indexed implementations. Callers should not need to
// construct a throwaway model merely to validate one limits value.
void validate_sync_replica_model_limits_or_throw(
    const SyncReplicaModelLimits& limits);

// Evidence admission and active applicability are deliberately separate. An
// immutable operation may be durably retained even though it is waiting for an
// exact predecessor or is deterministically excluded from active state.
enum class SyncReplicaAdmission {
    InsertedActive,
    InsertedPending,
    InsertedQuarantined,
    Duplicate,
    // The envelope is well-formed and belongs to this folder, but admitting
    // one more retained owner would cross a local configured capacity. This is
    // retryable policy state, not evidence invalidity and not quarantine.
    CapacityBlocked,
};

enum class SyncReplicaRemoteReadiness {
    Admissible,
    Duplicate,
    CapacityBlocked,
};

// Exact resource state for one prospective remote envelope. The values are
// semantic charges, not allocator estimates. would_exceed() is subtraction-
// based so a maliciously large incoming charge cannot wrap through uint64_t.
struct SyncReplicaResourceBudget final {
    std::uint64_t retained = 0;
    std::uint64_t incoming = 0;
    std::uint64_t limit = 0;

    [[nodiscard]] bool would_exceed() const noexcept {
        return retained > limit || incoming > limit - retained;
    }

    bool operator==(const SyncReplicaResourceBudget&) const = default;
};

struct SyncReplicaRemoteAdmissionPreflight final {
    SyncReplicaRemoteReadiness readiness =
        SyncReplicaRemoteReadiness::Admissible;
    SyncReplicaResourceBudget operations;
    SyncReplicaResourceBudget canonical_bytes;
    SyncReplicaResourceBudget context_entries;
    SyncReplicaResourceBudget predecessor_ids;

    bool operator==(const SyncReplicaRemoteAdmissionPreflight&) const =
        default;
};

enum class SyncReplicaEvidenceState {
    Active,
    PendingMissingDependency,
    QuarantinedDotFork,
    QuarantinedDependency,
    QuarantinedCausalEnvelope,
    QuarantinedDependencyCycle,
};

[[nodiscard]] bool sync_replica_evidence_state_is_quarantined(
    SyncReplicaEvidenceState state) noexcept;

struct SyncReplicaPathView final {
    std::string canonical_path;
    std::vector<std::string> visible_operation_ids;
    std::string primary_operation_id;
    SyncReplicaValueKind primary_kind = SyncReplicaValueKind::File;
    // Every visible file sibling other than a file primary. If a tombstone is
    // primary, all concurrent file siblings are preservation candidates.
    std::vector<std::string> preserved_file_operation_ids;

    bool operator==(const SyncReplicaPathView&) const = default;
};

// A wire-compatible identity continuation inferred from ordinary immutable
// file/tombstone evidence. The destination File is immediately followed by the
// source Tombstone under one actor epoch. The destination observed one exact
// visible source File with identical content in its causal past, and the source
// Tombstone names the destination File as its sole immediate predecessor. No
// transport-only rename flag or mutable inode identity is introduced.
//
// Exact-content copy followed by deletion is observationally indistinguishable
// from a rename at this layer. Callers must therefore present this as causal
// identity continuity, not proof of a particular filesystem rename syscall.
struct SyncReplicaIdentityPreservingRename final {
    std::string source_canonical_path;
    std::string destination_canonical_path;
    std::string source_file_operation_id;
    std::string destination_file_operation_id;
    std::string source_tombstone_operation_id;
    std::uint64_t size_bytes = 0U;
    std::string content_sha256;

    bool operator==(const SyncReplicaIdentityPreservingRename&) const = default;
};

struct SyncReplicaDurableState final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t last_local_counter = 0;

    // Index counter-1 is the exact operation ID minted under local_actor at that
    // counter. This prevents restore from guessing which side of a same-dot fork
    // was locally authorized and lets a late fork fail the minting authority
    // closed without discarding evidence.
    std::vector<std::string> local_operation_ids;

    // Strictly sorted by operation_id. Includes active, pending, and quarantined
    // evidence so crash/restart cannot erase the fact that a fork or unresolved
    // dependency was observed.
    std::vector<SyncReplicaOperation> operations;

    bool operator==(const SyncReplicaDurableState&) const = default;
};

// Canonical binary operation bytes exclude operation_id itself. The fixed
// versioned encoding uses big-endian integer and length fields, is bounded
// before allocation, and binds predecessor IDs as well as the dotted summary.
// This measurement applies exactly the same semantic and per-envelope limits
// as encoding but does not allocate the encoded envelope. operation_id may be
// empty while a local operation is being prepared.
[[nodiscard]] std::uint64_t
    sync_replica_operation_canonical_size_or_throw(
        const SyncReplicaOperation& operation,
        const SyncReplicaModelLimits& limits = {});

// Derives one exact local operation from the bounded active causal-head set
// observed by a storage owner. The head span must be strictly ordered by
// operation ID, contain active operations from this folder, and summarize the
// complete active causal frontier at the observation cutpoint. Storage owners remain
// responsible for proving that completeness and for re-proving any path-local
// publication fence before committing the derived immutable operation.
[[nodiscard]] SyncReplicaOperation
make_sync_replica_local_operation_from_causal_heads_or_throw(
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::uint64_t last_local_counter,
    std::string canonical_path,
    SyncReplicaValueKind kind,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const SyncReplicaOperation> causal_heads,
    const SyncReplicaModelLimits& limits = {});

// Domain-separated element witnesses for the schema-v8 commutative
// projection accumulators. Cardinality remains separately bound by durable
// metadata; these functions bind one immutable set member or one complete
// canonical path projection.
[[nodiscard]] std::string
sync_replica_active_operation_accumulator_element_digest_or_throw(
    std::string_view operation_id);
[[nodiscard]] std::string
sync_replica_evidence_operation_accumulator_element_digest_or_throw(
    std::string_view operation_id);
[[nodiscard]] std::string
sync_replica_visible_path_accumulator_element_digest_or_throw(
    const SyncReplicaPathView& view);

[[nodiscard]] std::string encode_sync_replica_operation_canonical_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits = {});

// Decoding consumes one exact canonical envelope, rejects truncation/trailing
// bytes/noncanonical structure, and derives operation_id from the exact bytes.
[[nodiscard]] SyncReplicaOperation
    decode_sync_replica_operation_canonical_or_throw(
        std::string_view canonical_bytes,
        const SyncReplicaModelLimits& limits = {});

// The caller may leave operation_id empty while minting. Identity is SHA-256 of
// the canonical operation bytes above.
[[nodiscard]] std::string make_sync_replica_operation_id_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits = {});

// Rejects malformed IDs, noncanonical clocks/parents/paths, impossible value
// shapes, oversized canonical bytes, and IDs that do not match exact bytes.
void validate_sync_replica_operation_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits = {});

[[nodiscard]] bool sync_replica_context_covers_dot(
    const std::vector<SyncReplicaClockEntry>& context,
    const SyncReplicaDot& dot) noexcept;

// True only when newer is a same-path active operation whose causal context
// includes older's unique dot. Concurrent operations never supersede one another.
[[nodiscard]] bool sync_replica_operation_supersedes(
    const SyncReplicaOperation& newer,
    const SyncReplicaOperation& older) noexcept;

class SyncReplicaModel final {
public:
    SyncReplicaModel(
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaModelLimits limits = {});

    [[nodiscard]] static SyncReplicaModel restore_or_throw(
        SyncReplicaDurableState durable,
        SyncReplicaModelLimits limits = {});

    // Local mutations observe only the active causal graph, bind its exact heads
    // as predecessor IDs, mint one dot, and publish evidence/projection/local
    // authority atomically. Ordinary mutation refuses an unresolved path
    // conflict; conflict collapse is a separate explicit operation below. A
    // compromised local actor epoch cannot mint again.
    [[nodiscard]] SyncReplicaOperation create_local_file_or_throw(
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256);

    // Scanner/publication boundary. The caller supplies the exact path heads
    // against which it observed the local bytes. Minting fails atomically if
    // remote admission, restart recovery, or another local writer changed that
    // path before this call. An unresolved multi-head path must use the explicit
    // resolution surface instead of laundering one displayed candidate into a
    // winner.
    [[nodiscard]] SyncReplicaOperation
    create_local_file_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);

    // Explicit conflict boundary. The supplied set must be the exact current
    // sorted multi-head view for this path. A stale, partial, duplicate, or
    // one-head set cannot resolve anything. The resulting operation remains an
    // ordinary canonical file operation; its causal context proves which prior
    // values it supersedes without introducing a transport-only winner flag.
    [[nodiscard]] SyncReplicaOperation
    resolve_local_file_conflict_or_throw(
        std::string canonical_path,
        std::span<const std::string> expected_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);

    [[nodiscard]] SyncReplicaOperation create_local_tombstone_or_throw(
        std::string canonical_path);

    // Absence-observation boundary. As with scanner file publication, the
    // caller supplies the exact visible heads against which it proved the path
    // absent. A concurrent admission or local writer cannot turn stale absence
    // into a tombstone over newer evidence.
    [[nodiscard]] SyncReplicaOperation
    create_local_tombstone_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids);

    // Validates identity and semantics and returns exact local capacity state
    // without mutating the model. Exact retained duplicates bypass rehashing and
    // report zero incoming charge. CapacityBlocked means valid evidence may be
    // retried under a different local retention policy; it is never quarantine.
    [[nodiscard]] SyncReplicaRemoteAdmissionPreflight
    preflight_remote_admission_or_throw(
        const SyncReplicaOperation& operation) const;

    // A well-formed exact envelope is retained before deterministic projection.
    // Missing dependencies remain pending. Same-dot forks and invalid causal
    // envelopes are quarantined as evidence rather than selected by arrival.
    // Locally insufficient retention capacity returns CapacityBlocked without
    // mutating evidence, projection, authority, or aggregate counters.
    [[nodiscard]] SyncReplicaAdmission accept_remote_or_throw(
        const SyncReplicaOperation& operation);

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }

    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    [[nodiscard]] std::uint64_t last_local_counter() const noexcept {
        return last_local_counter_;
    }

    // Exact operation IDs minted by this actor epoch, indexed by counter-1.
    // Exposing a const view lets durable owners attest this non-derivable
    // authority mapping without cloning the entire retained evidence set.
    [[nodiscard]] const std::vector<std::string>& local_operation_ids()
        const noexcept {
        return local_operation_ids_;
    }

    [[nodiscard]] bool local_actor_compromised() const noexcept {
        return local_actor_compromised_;
    }

    [[nodiscard]] std::size_t operation_count() const noexcept {
        return active_operation_ids_.size();
    }

    [[nodiscard]] std::size_t evidence_count() const noexcept {
        return evidence_by_id_.size();
    }

    [[nodiscard]] std::uint64_t retained_canonical_bytes() const noexcept {
        return retained_canonical_bytes_;
    }

    [[nodiscard]] std::uint64_t retained_context_entry_count() const noexcept {
        return retained_context_entries_;
    }

    [[nodiscard]] std::uint64_t retained_predecessor_id_count() const noexcept {
        return retained_predecessor_ids_;
    }

    [[nodiscard]] std::size_t pending_operation_count() const noexcept;
    [[nodiscard]] std::size_t quarantined_operation_count() const noexcept;

    [[nodiscard]] std::optional<SyncReplicaEvidenceState> evidence_state(
        const std::string& operation_id) const noexcept;

    // Active lookup. Use evidence_operation_by_id() for retained but inactive
    // pending/quarantined bytes.
    [[nodiscard]] std::optional<SyncReplicaOperation> operation_by_id(
        const std::string& operation_id) const;

    // Borrowed active lookup for immutable bulk projections. The pointer is
    // null for an inactive/unknown ID and remains valid only while this exact
    // model remains alive and no non-const model operation is invoked.
    [[nodiscard]] const SyncReplicaOperation* active_operation_by_id_or_none(
        const std::string& operation_id) const;

    // Visits borrowed immutable active operations without cloning the retained
    // evidence set. The callback must not mutate this model or retain a
    // reference beyond the call. This keeps bounded projections from paying an
    // avoidable O(active operations) copy before applying their own output cap.
    template <typename Visitor>
    void for_each_active_operation(const Visitor& visitor) const {
        for (const std::string& operation_id : active_operation_ids_) {
            const auto found = evidence_by_id_.find(operation_id);
            if (found == evidence_by_id_.end()) {
                throw std::logic_error(
                    "sync replica active operation ID is absent from evidence");
            }
            visitor(found->second);
        }
    }

    // Visits every borrowed retained operation together with its exact current
    // evidence state in operation-ID order. The two durable maps are required
    // to remain in lockstep; divergence fails closed. The compile-time visitor
    // is neither copied nor type-erased and must not mutate this model or retain
    // references beyond the call.
    template <typename Visitor>
    void for_each_evidence_operation(const Visitor& visitor) const {
        auto state = evidence_state_by_id_.begin();
        for (const auto& [operation_id, operation] : evidence_by_id_) {
            if (state == evidence_state_by_id_.end() ||
                state->first != operation_id) {
                throw std::logic_error(
                    "sync replica evidence operation/state maps diverged");
            }
            visitor(operation, state->second);
            ++state;
        }
        if (state != evidence_state_by_id_.end()) {
            throw std::logic_error(
                "sync replica evidence state map has an extra operation");
        }
    }

    [[nodiscard]] std::optional<SyncReplicaOperation> evidence_operation_by_id(
        const std::string& operation_id) const;

    [[nodiscard]] std::vector<SyncReplicaOperation> all_operations() const;
    [[nodiscard]] std::vector<SyncReplicaOperation> all_evidence_operations()
        const;

    [[nodiscard]] std::vector<SyncReplicaClockEntry> observed_context() const;
    [[nodiscard]] std::vector<std::string> causal_head_operation_ids() const;

    // Exact absent IDs that currently block evidence which could still become
    // active. Missing references reachable only from quarantined evidence are
    // deliberately omitted so dependency fetch cannot chase impossible work.
    [[nodiscard]] std::vector<std::string> missing_predecessor_operation_ids()
        const;

    [[nodiscard]] std::optional<SyncReplicaPathView> visible_path(
        const std::string& canonical_path) const;

    // Recognizes the canonical two-operation rename shape without changing the
    // operation codec or reconciliation protocol. Unknown, inactive, malformed,
    // conflicted, content-changing, or causally ambiguous evidence returns no
    // identity continuation. The lookup is O(active evidence) and is intended
    // for bounded operator/history diagnostics and exact publication reproof,
    // not for whole-history eager projection.
    [[nodiscard]] std::optional<SyncReplicaIdentityPreservingRename>
    identity_preserving_rename_for_source_tombstone(
        const std::string& source_tombstone_operation_id) const;

    // Groups active operations by borrowed canonical-path views exactly once,
    // computes each visible projection once, and invokes the compile-time
    // visitor in bytewise path order. The visitor must not mutate this model or
    // retain any pointer/reference beyond the call. Keeping this a template
    // avoids adding a type-erased executable boundary to the model API.
    template <typename Visitor>
    void for_each_active_path(const Visitor& visitor) const {
        std::vector<const SyncReplicaOperation*> ordered =
            ordered_active_operations_by_path();
        std::size_t first = 0U;
        while (first < ordered.size()) {
            std::size_t after = first + 1U;
            while (after < ordered.size() &&
                   ordered[after]->canonical_path ==
                       ordered[first]->canonical_path) {
                ++after;
            }
            const std::span<const SyncReplicaOperation* const> candidates(
                ordered.data() + first, after - first);
            const SyncReplicaPathView view =
                visible_path_view_from_active_candidates_or_throw(candidates);
            visitor(view, candidates);
            first = after;
        }
    }

    [[nodiscard]] std::vector<SyncReplicaPathView> visible_paths() const;

    // Active-operation digest. Independently named replicas converge on this
    // after deterministically projecting the same evidence set.
    [[nodiscard]] std::string operation_set_digest() const;

    // Retained evidence digest includes active, pending, and quarantined IDs.
    [[nodiscard]] std::string evidence_set_digest() const;

    [[nodiscard]] std::string visible_state_digest() const;

    // Schema-v8 bounded-update witnesses. Unlike the legacy sorted-stream
    // digests above, these are commutative 256-bit accumulators whose exact
    // cardinalities are bound separately. They permit one exact insertion or
    // path replacement to update durable metadata without rescanning unrelated
    // retained history.
    [[nodiscard]] std::string operation_set_accumulator_digest() const;
    [[nodiscard]] std::string evidence_set_accumulator_digest() const;
    [[nodiscard]] std::uint64_t visible_path_count() const;
    [[nodiscard]] std::string visible_state_accumulator_digest() const;

    [[nodiscard]] SyncReplicaDurableState durable_state() const;

private:
    friend class SyncReplicaNetworkSimulator;

    enum class LocalMutationPurpose {
        Ordinary,
        ConflictResolution,
    };

    [[nodiscard]] std::vector<const SyncReplicaOperation*>
    ordered_active_operations_by_path() const;

    [[nodiscard]] SyncReplicaPathView
    visible_path_view_from_active_candidates_or_throw(
        std::span<const SyncReplicaOperation* const> candidates) const;

    [[nodiscard]] SyncReplicaOperation create_local_operation_or_throw(
        std::string canonical_path,
        SyncReplicaValueKind kind,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::optional<std::vector<std::string>> expected_visible_operation_ids,
        LocalMutationPurpose purpose);

    // Consumes an admissible preflight produced against this exact immutable
    // state (or a byte-for-byte model copy). The network simulator is a friend
    // solely so it can preflight before cloning and avoid validating/hashing the
    // same envelope twice after the copy.
    [[nodiscard]] SyncReplicaAdmission
    accept_remote_admissible_after_preflight_or_throw(
        const SyncReplicaOperation& operation,
        const SyncReplicaRemoteAdmissionPreflight& preflight);

    [[nodiscard]] bool compute_local_actor_compromised(
        const std::map<std::string, SyncReplicaOperation>& evidence,
        const std::map<std::string, SyncReplicaEvidenceState>& states,
        const std::vector<std::string>& local_operation_ids,
        const std::string* appended_local_operation_id = nullptr) const noexcept;

    std::string folder_id_;
    SyncReplicaActor local_actor_;
    SyncReplicaModelLimits limits_;
    std::uint64_t last_local_counter_ = 0;
    std::vector<std::string> local_operation_ids_;
    bool local_actor_compromised_ = false;

    std::map<std::string, SyncReplicaOperation> evidence_by_id_;
    std::set<std::string> active_operation_ids_;
    std::map<std::string, SyncReplicaEvidenceState> evidence_state_by_id_;
    std::set<std::string> causal_head_operation_ids_;

    // Exact aggregate charge of evidence_by_id_. These values are published in
    // the same no-throw commit section as graph projection and are unchanged on
    // every rejected or allocation-failed admission.
    std::uint64_t retained_canonical_bytes_ = 0;
    std::uint64_t retained_context_entries_ = 0;
    std::uint64_t retained_predecessor_ids_ = 0;
};

}  // namespace anonsync
