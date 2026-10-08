#pragma once

#if !defined(_WIN32)

#include "sync_directory_authority.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_replica_selective_sync_policy.hpp"

#include <cstdint>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaFolderObservationMaximumEntries = 1000000U;
inline constexpr std::uint64_t
    kSyncReplicaFolderObservationMaximumRegularFiles = 1000000U;
inline constexpr std::uint64_t
    kSyncReplicaFolderObservationMaximumDirectoryDepth = 256U;
inline constexpr std::uint64_t
    kSyncReplicaFolderObservationDefaultMaximumEntries = 262144U;
inline constexpr std::uint64_t
    kSyncReplicaFolderObservationDefaultMaximumRegularFiles = 100000U;

// Deliberately bounded first-folder limits. Every directory entry counts against
// maximum_entries, including directories, ignored links, special files, and
// internal publication residue. Only synchronizable regular files count against
// maximum_regular_files. Keeping those ceilings independent prevents namespace
// shape from being mistaken for durable catalog or payload capacity while a tree
// full of objects AnonSync does not yet synchronize remains bounded.
struct SyncReplicaFolderObservationLimits final {
    std::uint64_t maximum_entries =
        kSyncReplicaFolderObservationDefaultMaximumEntries;
    std::uint64_t maximum_regular_files =
        kSyncReplicaFolderObservationDefaultMaximumRegularFiles;
    std::uint64_t maximum_file_bytes = 64ULL * 1024ULL * 1024ULL;
    std::uint64_t maximum_total_file_bytes = 256ULL * 1024ULL * 1024ULL;
    std::uint64_t maximum_relative_path_bytes = 4096;
    // Zero permits only regular files directly below the configured root.
    std::uint64_t maximum_directory_depth = 64;

    bool operator==(const SyncReplicaFolderObservationLimits&) const = default;
};

// A resumable walk can be bounded independently by both classified bytes and
// delivered regular-file count. The count frontier prevents a namespace of
// zero-byte or very small files from turning one scheduling segment into an
// effectively whole-tree callback batch. It does not weaken maximum_entries:
// every directory entry, including ignored objects and the skipped prefix,
// continues to spend that whole-walk safety budget.
inline constexpr std::uint64_t
    kSyncReplicaFolderTraversalDefaultMaximumRegularFiles = 4096U;

// Resumable production walks never retain an entire flat directory's basename
// vector. They select the next component-wise lexicographic batch with one
// complete readdir pass, process it in order, and rescan only when the current
// scheduling segment still has useful work capacity. This is an internal work-
// memory boundary rather than a user policy knob: the independent namespace
// entry ceiling remains authoritative and every non-dot entry in the first
// complete directory census is charged exactly once.
inline constexpr std::uint64_t
    kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch = 4096U;

struct SyncReplicaFolderTraversalSegmentLimits final {
    std::uint64_t maximum_regular_files =
        kSyncReplicaFolderTraversalDefaultMaximumRegularFiles;

    bool operator==(const SyncReplicaFolderTraversalSegmentLimits&) const =
        default;
};

// Shared fail-fast boundary for both full observations and streaming walks.
// Keeping one validator prevents a composed folder owner from silently
// accepting limits that the traversal later interprets differently.
void validate_sync_replica_folder_observation_limits_or_throw(
    const SyncReplicaFolderObservationLimits& limits,
    std::string label = "sync replica folder observation limits");

void validate_sync_replica_folder_traversal_segment_limits_or_throw(
    const SyncReplicaFolderTraversalSegmentLimits& limits,
    std::string label = "sync replica folder traversal segment limits");

// Namespace-only traversal report. classified_regular_file_bytes is charged
// from the no-follow status observed before the visitor is invoked. A visitor
// that later opens the path must impose its own exact byte limit because the
// namespace can change between those two observations.
struct SyncReplicaFolderTraversalSummary final {
    std::uint64_t visited_entry_count = 0;
    std::uint64_t visited_directory_count = 0;
    std::uint64_t regular_file_count = 0;
    std::uint64_t ignored_symbolic_link_count = 0;
    std::uint64_t ignored_special_file_count = 0;
    std::uint64_t ignored_internal_artifact_count = 0;
    // Selective-sync filtering occurs before a regular file spends the file-
    // count or byte frontiers. A pruned directory is counted once but its
    // descendants are deliberately not enumerated; this is selected-namespace
    // accounting, not a claim about the complete physical tree.
    std::uint64_t metadata_only_regular_file_count = 0;
    // Sum of st_size for metadata-only regular files that were individually
    // classified. This is sparse logical size from one no-follow namespace
    // observation, not allocated blocks, exact retained bytes, or hash work.
    // Descendants of a pruned metadata-only directory are deliberately absent
    // because the traversal never enumerates them.
    std::uint64_t metadata_only_regular_file_logical_bytes = 0;
    std::uint64_t metadata_only_pruned_directory_count = 0;
    std::uint64_t classified_regular_file_bytes = 0;

    bool operator==(const SyncReplicaFolderTraversalSummary&) const = default;
};

using SyncReplicaFolderRegularFilePathVisitor =
    std::function<void(const std::string& canonical_path,
                       std::uint64_t classified_size_bytes)>;

enum class SyncReplicaFolderTraversalStopReason : std::uint8_t {
    NotStarted = 0,
    EndOfNamespace = 1,
    AggregateFileByteFrontier = 2,
    RegularFileCountFrontier = 3,
    DirectoryCensusFrontier = 4,
};

[[nodiscard]] constexpr std::string_view
sync_replica_folder_traversal_stop_reason_name(
    SyncReplicaFolderTraversalStopReason reason) noexcept {
    switch (reason) {
        case SyncReplicaFolderTraversalStopReason::NotStarted:
            return "not_started";
        case SyncReplicaFolderTraversalStopReason::EndOfNamespace:
            return "end_of_namespace";
        case SyncReplicaFolderTraversalStopReason::AggregateFileByteFrontier:
            return "aggregate_file_byte_frontier";
        case SyncReplicaFolderTraversalStopReason::RegularFileCountFrontier:
            return "regular_file_count_frontier";
        case SyncReplicaFolderTraversalStopReason::DirectoryCensusFrontier:
            return "directory_census_frontier";
    }
    return "unknown";
}

// The traversal order is component-wise bytewise preorder: entries in each
// directory are sorted by basename, and a directory's complete subtree is
// visited before the next sibling. This differs from a flat string comparison
// for cases such as "a/child" and "a.txt". Persisted continuation cursors must
// use this comparator or a restarted walk can skip or repeat a path.
[[nodiscard]] bool sync_replica_folder_traversal_path_less(
    std::string_view left, std::string_view right) noexcept;

struct SyncReplicaFolderTraversalSegment final {
    SyncReplicaFolderTraversalSummary traversal;
    // True only when the walk reached the end of the namespace. A false value
    // means the next eligible regular file would have crossed the aggregate
    // byte or delivered-file-count frontier, or a later directory enumeration
    // observed names beyond that visit's first census. In every case work is
    // deliberately left for a later segment. stop_reason distinguishes those
    // scheduling outcomes without making any of them durable synchronization
    // authority.
    bool completed = false;
    SyncReplicaFolderTraversalStopReason stop_reason =
        SyncReplicaFolderTraversalStopReason::NotStarted;
    std::uint64_t skipped_regular_file_count = 0;
    // Diagnostic proof of the bounded sorted-name implementation. The first
    // value counts complete readdir passes (a large mixed directory can require
    // another pass after one component batch); the second is the largest
    // individual sorted basename batch. The third is the largest aggregate
    // number of selected basenames retained simultaneously by the resumable
    // walk. Parent batch storage is released before recursive descent, so the
    // aggregate remains bounded by one batch. Recursive descriptors and one
    // component/path observation per active depth remain depth-indexed state;
    // aggregate string bytes also depend on growing canonical-path lengths.
    // These diagnostics
    // authorize no deletion, cursor publication, or filesystem effects.
    std::uint64_t directory_enumeration_pass_count = 0;
    std::uint64_t peak_buffered_directory_component_batch_count = 0;
    std::uint64_t peak_simultaneously_buffered_directory_component_count = 0;
    // Last path successfully delivered to the visitor. When no new path was
    // delivered, this retains the input continuation cursor.
    std::string resume_after_path;

    bool operator==(const SyncReplicaFolderTraversalSegment&) const = default;
};

// Restartable counterpart to the full traversal below. Regular paths at or
// before resume_after_path in component-wise traversal order are classified but
// not charged to the aggregate file-byte budget and are not delivered again.
// When the next eligible file would cross either segment frontier, a
// non-complete segment is returned after all opened directory identities and
// the retained root have been re-proved. At least one eligible file must fit an
// empty byte segment; callers should require maximum_file_bytes <=
// maximum_total_file_bytes. Visitor effects must be idempotent and restart-safe,
// and the cursor should be persisted only after the visitor's complete path
// effect succeeds. The explicit segment-limits overload is the production
// scheduling boundary. The compatibility overload below adds no smaller
// scheduling frontier: it permits delivery up to the whole-folder regular-file
// capacity while retaining the independent aggregate-byte frontier.
[[nodiscard]] SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits,
    const SyncReplicaFolderTraversalSegmentLimits& segment_limits,
    std::string label);

// Selective counterpart. Only paths resolved to Materialize spend regular-file
// count/byte scheduling frontiers or reach the visitor. Metadata-only subtrees
// with no deeper include rule are descriptor-cold pruned at the directory name.
[[nodiscard]] SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaSelectiveSyncPolicy& selective_sync_policy,
    const SyncReplicaFolderObservationLimits& limits,
    const SyncReplicaFolderTraversalSegmentLimits& segment_limits,
    std::string label);

[[nodiscard]] SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits = {},
    std::string label = "sync replica folder resumable path traversal");

// Walks one retained root without retaining file payloads or a whole-tree path
// list. Names within each open directory are processed in bytewise order, so a
// stable namespace produces a stable callback order. The production resumable
// overload releases an ancestor's selected-name batch before recursive descent
// and resumes that directory from the exact component boundary, bounding its
// simultaneous selected-basename storage to one batch plus O(depth) path state.
// The non-resumable overload still retains unprocessed ancestor vectors, bounded
// only by the global entry ceiling and configured depth ceiling. The callback runs
// synchronously and may make durable progress. A later traversal error does not
// roll back earlier callback effects;
// callers must make each callback idempotent and restart-safe.
// The callback receives a classification-time size only. It must open, bound,
// and re-attest the exact file itself before treating bytes as authoritative.
[[nodiscard]] SyncReplicaFolderTraversalSummary
visit_sync_replica_folder_regular_file_paths_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits = {},
    std::string label = "sync replica folder path traversal");

// One exact regular-file observation. content_bytes are retained because this
// first bounded slice must be able to stage the same bytes it hashed without a
// second pathname read. The production folder pass uses the path visitor above
// and releases each independently prepared file before visiting the next path.
struct SyncReplicaObservedRegularFile final {
    std::string canonical_path;
    std::string content_sha256;
    std::string content_bytes;
    SyncPosixRegularFileSnapshotMetadata metadata;

    bool operator==(const SyncReplicaObservedRegularFile&) const = default;
};

struct SyncReplicaFolderObservation final {
    // Strictly sorted by canonical_path.
    std::vector<SyncReplicaObservedRegularFile> regular_files;
    std::uint64_t visited_entry_count = 0;
    std::uint64_t visited_directory_count = 0;
    std::uint64_t ignored_symbolic_link_count = 0;
    std::uint64_t ignored_special_file_count = 0;
    std::uint64_t ignored_internal_artifact_count = 0;
    std::uint64_t total_regular_file_bytes = 0;

    bool operator==(const SyncReplicaFolderObservation&) const = default;
};

// Observes one retained Linux/POSIX folder authority without following links or
// crossing onto another mount. The function opens an independent root directory
// description for readdir(3), so repeated scans do not consume the retained
// authority's shared directory offset. Every regular file is opened relative to
// its retained parent, frozen with pread(2), and then rebound to the same
// parent/name with a no-follow status check after hashing. Any I/O error,
// nonportable regular-file/directory path, bound breach, mount crossing, or
// namespace substitution aborts the whole returned batch. Symbolic links and
// non-regular special files are counted but not followed or synchronized.
[[nodiscard]] SyncReplicaFolderObservation
observe_sync_replica_folder_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFolderObservationLimits& limits = {},
    std::string label = "sync replica folder observation");

}  // namespace anonsync

#endif
