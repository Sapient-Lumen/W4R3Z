#pragma once

#if !defined(_WIN32)

#include "sync_posix_descriptor_snapshot.hpp"

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view
    kSyncReplicaFilePayloadRetentionMarkBasename =
        ".anonsync-payload-retention-mark-v1";
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadRetentionMarkMaximumGraceSeconds =
        10ULL * 365ULL * 24ULL * 60ULL * 60ULL;

// Explicit bounded operator policy attached to one deletion-free candidate
// observation. This is not collection authority: a later collector must
// reacquire all current causal, transient, live-capability, inode, byte, root,
// elapsed-time, quota, and ENOSPC cutpoints before any rename or unlink.
struct SyncReplicaFilePayloadRetentionPolicy final {
    std::uint64_t minimum_grace_seconds = 0U;
    std::uint64_t maximum_candidate_payload_count = 0U;
    std::uint64_t maximum_candidate_payload_bytes = 0U;
    std::uint64_t maximum_collection_payload_count = 0U;
    std::uint64_t maximum_collection_payload_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadRetentionPolicy&) const = default;
};

// Validates the policy/time relationship without consulting one store's
// configured capacity. This lets parsers and generic callers reject malformed
// operator input independently of a live store owner.
void validate_sync_replica_file_payload_retention_policy_or_throw(
    const SyncReplicaFilePayloadRetentionPolicy& policy,
    std::uint64_t marked_at_unix_seconds,
    std::string_view label = "payload retention policy");

// Adds the exact store-capacity frontier to the generic policy validation.
// Higher owners call this before acquiring a writer fence or enumerating the
// payload namespace, so a configuration-impossible policy cannot spend a
// complete physical observation merely to fail during record serialization.
void validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
    const SyncReplicaFilePayloadRetentionPolicy& policy,
    std::uint64_t marked_at_unix_seconds,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label = "payload retention policy for store");

// One checksum-framed, exact-store-identity-bound historical mark. It records
// a restart-stable candidate witness and conservative policy, but deliberately
// carries no reclaimable, quarantine, or unlink bit.
struct SyncReplicaFilePayloadRetentionMark final {
    std::string store_identity_sha256;
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata;
    // Continuity evidence only while a structurally usable predecessor exists.
    // Absence or unusable bytes restart at one, so this is not freshness,
    // elapsed-time, or anti-rollback authority.
    std::uint64_t generation = 1U;
    std::uint64_t marked_at_unix_seconds = 0U;
    SyncReplicaFilePayloadRetentionPolicy policy;

    // Monotonic within one retained SQLite database lineage, this owner
    // generation prevents a causal-root ABA from inheriting grace merely
    // because all content digests later return to the same values. It is not an
    // external anti-rollback counter: exact database restoration can recreate
    // both generation and digests, and this mark grants no collection authority.
    std::uint64_t source_replica_state_generation = 0U;
    std::string source_operation_set_digest;
    std::string source_evidence_set_digest;
    std::string source_historical_version_pin_set_digest;
    std::string source_visible_state_digest;
    std::string source_payload_snapshot_digest;
    std::string source_payload_transient_namespace_digest;
    std::string unreferenced_candidate_set_digest;
    // Opaque v2 witness over the exact database incarnation, recovery epoch,
    // state generation, causal roots, payload namespace, and candidate set.
    // Keeping the lineage inside this canonical digest preserves the fixed v1
    // record layout while making prior unbound witness generations fail closed.
    std::string durable_candidate_witness_digest;
    std::uint64_t unreferenced_candidate_payload_count = 0U;
    std::uint64_t unreferenced_candidate_payload_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadRetentionMark&) const = default;
};

[[nodiscard]] std::uint64_t
sync_replica_file_payload_retention_mark_exact_bytes() noexcept;

[[nodiscard]] std::string
serialize_sync_replica_file_payload_retention_mark_or_throw(
    const SyncReplicaFilePayloadRetentionMark& mark,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label = "payload retention mark serialization");

[[nodiscard]] SyncReplicaFilePayloadRetentionMark
parse_sync_replica_file_payload_retention_mark_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label = "payload retention mark parsing");

[[nodiscard]] std::string
sync_replica_file_payload_retention_mark_digest_or_throw(
    const SyncReplicaFilePayloadRetentionMark& mark,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label = "payload retention mark digest");

}  // namespace anonsync

#endif
