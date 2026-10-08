#pragma once

#if !defined(_WIN32)

#include "sync_replica_content_defined_chunker.hpp"
#include "sync_replica_deployment_identity.hpp"
#include "sync_replica_file_content_inventory.hpp"
#include "sync_replica_file_payload_retention_mark.hpp"
#include "sync_replica_source_manifest_checkpoint.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_payload_extent.hpp"
#include "sync_posix_descriptor_snapshot.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <vector>
#include <utility>

namespace anonsync {

class SyncReplicaReconciliationService;

inline constexpr std::uint64_t kSyncReplicaFilePayloadStoreMaxEntries =
    kSyncReplicaFileContentInventoryMaxEntries;
// The shipping folder/catalog owners admit 100,000 current paths. Production
// payload composition must not silently retain the generic 4,096-entry test
// default, or a valid tree of small unique files becomes unsynchronizable long
// before the folder owner reaches its own reviewed boundary. This is a capacity
// ceiling, not a retention promise: historical versions still require GC.
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreProductionMaxEntries = 100000U;
// Structural aggregate byte frontier for the production store. This is the
// largest exactly representable JSON integer (8 PiB minus one), not a quota or
// a reservation. It prevents the old 64 GiB hidden store ceiling from making a
// valid multi-terabyte tree unsynchronizable while keeping every persisted and
// operator-visible byte count exact.
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreProductionMaxIndexedBytes =
        9007199254740991ULL;
static_assert(
    kSyncReplicaFilePayloadStoreProductionMaxEntries <=
    kSyncReplicaFilePayloadStoreMaxEntries);
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreMaxTransientEntries = 65536U;
// Corrupt bytes are preserved only through an explicit exact-pair operator
// action. A fixed archive frontier prevents repeated faults from becoming an
// unbounded hidden retention policy; quarantine is diagnostic evidence, not
// version history or garbage collection.
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreMaxQuarantineEntries = 16U;

// Cross-process cooperative lifetime witness for an already-open committed
// payload descriptor. Selection takes the store-wide shared observation lease
// first, then this shared inode lease. Namespace mutation takes the store-wide
// exclusive lease first, then this inode lease exclusively. The stable lock
// order prevents new readers while allowing a collector to detect descriptors
// that outlive their short namespace observation cutpoint.
inline constexpr std::string_view
    kSyncReplicaFilePayloadUseLeaseProtocol =
        "anonsync:sync-replica-file-payload-use-flock-lease:v1";

struct SyncReplicaFilePayloadStoreLimits final {
    std::uint64_t max_entries = 4096U;
    std::uint64_t max_payload_bytes = 4ULL * 1024ULL * 1024ULL;
    std::uint64_t max_indexed_bytes = 64ULL * 1024ULL * 1024ULL * 1024ULL;
    std::uint64_t max_transient_entries = 4096U;
    std::uint64_t max_transient_bytes = 64ULL * 1024ULL * 1024ULL;

    // Optional rotating byte-integrity work. Both fields are zero when scrub
    // scheduling is disabled. The production composition enables a strict
    // per-attempt byte and distinct-entry bound; partial SHA-256 continuation
    // is durable, so one very large payload cannot starve later identities.
    std::uint64_t max_scrub_bytes_per_attempt = 0U;
    std::uint64_t max_scrub_entries_per_attempt = 0U;

    bool operator==(const SyncReplicaFilePayloadStoreLimits&) const = default;
};

void validate_sync_replica_file_payload_store_limits_or_throw(
    const SyncReplicaFilePayloadStoreLimits& limits);

// Exact result of publishing one historical, deletion-free retention mark. The
// record is durable and identity-bound but remains non-authoritative: a future
// collection operation must re-prove every causal, transient, capability, inode,
// byte, root, policy, and elapsed-time condition.
struct SyncReplicaFilePayloadRetentionMarkPublication final {
    SyncReplicaFilePayloadRetentionMark mark;
    std::string mark_digest;
    bool replaced_existing_file = false;
    bool replaced_usable_mark = false;

    bool operator==(
        const SyncReplicaFilePayloadRetentionMarkPublication&) const = default;
};

// Canonical production composition. New prefix-owner transfers need one
// whole-payload reservation. The retained rev0941 range-file compatibility
// owner can still hold its immutable ranges plus one private whole-file
// assembly, so mixed-version recovery keeps the two-payload transient frontier.
[[nodiscard]] SyncReplicaFilePayloadStoreLimits
sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
    std::uint64_t max_payload_bytes,
    std::string_view label =
        "sync replica file payload store production limits");

enum class SyncReplicaFilePayloadStorePutDisposition : std::uint8_t {
    Inserted = 1,
    AlreadyPresent = 2,
};

enum class SyncReplicaFilePayloadStoreStageDisposition : std::uint8_t {
    Progress = 1,
    CompletedInserted = 2,
    CompletedAlreadyPresent = 3,
};

// Separates observation/mutation authority from bootstrap authority. An
// ExistingOnly store may use an exact durable identity marker but can never
// adopt an unbound directory or mint that marker. A writable open may migrate
// one exact legacy-reader marker to the current minimum-reader basename only
// after an exclusive lease and a complete non-accelerated byte proof.
// CreateIfMissing is reserved for explicit bootstrap and still validates the
// complete pre-existing namespace before publishing the immutable folder
// binding.
enum class SyncReplicaFilePayloadStoreOpenDisposition : std::uint8_t {
    ExistingOnly = 1,
    CreateIfMissing = 2,
    // Existing current product-bound marker and payload bytes are attested
    // without durability reconciliation. The snapshot acquires the same
    // cooperative shared lease but performs no fsync and can never publish,
    // rename, or migrate a marker or payload. This is reserved for forensic
    // observation.
    ReadOnlyInspect = 3,
};

struct SyncReplicaFilePayloadStorePutResult final {
    SyncReplicaFilePayloadStorePutDisposition disposition =
        SyncReplicaFilePayloadStorePutDisposition::Inserted;
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;

    bool operator==(const SyncReplicaFilePayloadStorePutResult&) const =
        default;
};

// One exact content-defined chunk in canonical file order. The rolling gear
// hash chooses boundaries only; this SHA-256 and the whole-payload SHA-256 are
// the evidence consumed by reconciliation and final publication.
struct SyncReplicaFilePayloadStoreContentDefinedChunk final {
    SyncReplicaFilePayloadStoreContentDefinedChunk() noexcept = default;
    SyncReplicaFilePayloadStoreContentDefinedChunk(
        std::uint64_t size,
        std::string_view digest)
        : size_bytes(size), sha256(digest) {}
    SyncReplicaFilePayloadStoreContentDefinedChunk(
        std::uint64_t size,
        Sha256DigestValue digest) noexcept
        : size_bytes(size), sha256(std::move(digest)) {}

    std::uint64_t size_bytes = 0U;
    Sha256DigestValue sha256;

    [[nodiscard]] std::string sha256_hex() const {
        return sha256.lowercase_hex();
    }

    bool operator==(
        const SyncReplicaFilePayloadStoreContentDefinedChunk&) const = default;
};

static_assert(
    sizeof(SyncReplicaFilePayloadStoreContentDefinedChunk) == 40U,
    "payload-store content-defined chunks must remain fixed 40-byte records");
static_assert(
    std::is_trivially_copyable_v<
        SyncReplicaFilePayloadStoreContentDefinedChunk>,
    "payload-store content-defined chunks must not own hidden heap state");

struct SyncReplicaFilePayloadStoreContentDefinedManifest final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    SyncReplicaContentDefinedChunkingParameters parameters;
    std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk> chunks;

    bool operator==(
        const SyncReplicaFilePayloadStoreContentDefinedManifest&) const =
        default;
};

// One copyable bounded checkpoint extracted at an arbitrary byte frontier.
// The resumable whole hash covers exactly next_offset_bytes; the retained chunk
// vector covers completed_chunk_bytes; and the current hash plus rolling
// chunker cover the remaining in-progress chunk. It owns no descriptor or
// namespace authority; durable storage must additionally bind exact store,
// operation, and payload observations.
struct SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    SyncPosixRegularFileSnapshotMetadata metadata;
    SyncReplicaContentDefinedChunkingParameters parameters;
    std::uint64_t next_offset_bytes = 0U;
    std::uint64_t completed_chunk_bytes = 0U;
    ResumableSha256Checkpoint whole_hash;
    ResumableSha256Checkpoint current_chunk_hash;
    SyncReplicaContentDefinedChunkerCheckpoint chunker;
    std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk>
        completed_chunks;

    bool operator==(
        const SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint&)
        const = default;
};

// Process-local, move-only progress for one exact descriptor-rooted
// content-defined projection. The projection owns only bounded hashing and
// chunk-frontier state; it owns no descriptor, payload-store lease, namespace
// capability, or durable authority. Every bounded advance must therefore
// reopen the payload through ordinary targeted access and re-prove the exact
// retained inode observation before the next bytes can extend this state.
//
// Completed chunks are safe acceleration evidence for immediate local reuse:
// each chunk carries its own SHA-256, every later source range is independently
// rehashed by the payload-store owner, and only the final target whole digest
// can publish the assembled payload. The source whole digest is still required
// before this projection can become a complete reusable manifest.
class SyncReplicaFilePayloadStoreContentDefinedProjection final {
public:
    SyncReplicaFilePayloadStoreContentDefinedProjection() noexcept;
    SyncReplicaFilePayloadStoreContentDefinedProjection(
        const SyncReplicaFilePayloadStoreContentDefinedProjection&) = delete;
    SyncReplicaFilePayloadStoreContentDefinedProjection& operator=(
        const SyncReplicaFilePayloadStoreContentDefinedProjection&) = delete;
    SyncReplicaFilePayloadStoreContentDefinedProjection(
        SyncReplicaFilePayloadStoreContentDefinedProjection&&) noexcept;
    SyncReplicaFilePayloadStoreContentDefinedProjection& operator=(
        SyncReplicaFilePayloadStoreContentDefinedProjection&&) noexcept;
    ~SyncReplicaFilePayloadStoreContentDefinedProjection() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] const std::string& content_sha256() const;
    [[nodiscard]] std::uint64_t total_size_bytes() const;
    [[nodiscard]] std::uint64_t next_offset_bytes() const;
    [[nodiscard]] std::uint64_t completed_chunk_bytes() const;
    [[nodiscard]] const SyncReplicaContentDefinedChunkingParameters&
    parameters() const;
    [[nodiscard]] const SyncPosixRegularFileSnapshotMetadata& metadata() const;
    [[nodiscard]] const std::vector<
        SyncReplicaFilePayloadStoreContentDefinedChunk>&
    completed_chunks() const;

    // Returns the exact current byte frontier. The returned copy is bounded by
    // the 8,192-chunk protocol frontier and may describe progress inside the
    // first chunk.
    [[nodiscard]]
    SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint checkpoint()
        const;

    // Restores one previously validated boundary. The next opened-payload
    // advance still requires exact content, size, metadata, and parameter
    // equality before it may read another byte.
    void restore_checkpoint_or_throw(
        SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint
            checkpoint,
        std::string_view label =
            "content-defined projection checkpoint restore");

private:
    struct State;
    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStoreOpenedPayload;
};

struct SyncReplicaFilePayloadStoreContentDefinedProjectionStep final {
    // Exact bytes consumed during this call. A nonterminal step never exceeds
    // the caller's maximum_step_bytes frontier.
    std::uint64_t hashed_bytes = 0U;
    std::uint64_t newly_completed_chunk_count = 0U;
    // Present only when the exact final source digest and observation have
    // both been re-proved. Completion consumes and clears the progress owner.
    std::optional<SyncReplicaFilePayloadStoreContentDefinedManifest>
        completed_manifest;
    // Present with completed_manifest and covers the exact whole payload before
    // terminal padding. It lets the durable completed record independently
    // re-derive the trusted content digest without rereading source bytes.
    std::optional<ResumableSha256Checkpoint> completed_whole_hash;
};

struct SyncReplicaFilePayloadStoreRange final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t offset_bytes = 0U;
    std::string chunk_sha256;
    std::string bytes;

    bool operator==(const SyncReplicaFilePayloadStoreRange&) const = default;
};

// Durable contiguous-prefix staging result. Progress means an admitted private
// staging owner retains an exact prefix below total_size_bytes. A completed
// result means the whole SHA-256 was re-proved and the digest-named immutable
// payload is durable; no staging name still carries authority.
struct SyncReplicaFilePayloadStoreStageResult final {
    SyncReplicaFilePayloadStoreStageDisposition disposition =
        SyncReplicaFilePayloadStoreStageDisposition::Progress;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t next_offset_bytes = 0U;
    std::uint64_t accepted_range_bytes = 0U;
    // Exact number of bounded whole-target SHA-256 steps performed by this
    // call. Range staging may enter one terminal step when it completes the
    // durable prefix; the source-byte-free continuation performs exactly one
    // step unless it discovers an already durable payload first. Diagnostic
    // and scheduler accounting only.
    std::uint64_t terminal_verification_steps = 0U;
    // Exact durable whole-target SHA-256 frontier after this call. It is zero
    // while range staging has not reached the complete-prefix boundary, equals
    // total_size_bytes after publication, and otherwise names the persisted
    // restart checkpoint. This is diagnostic/scheduler evidence only; the
    // opened staged inode and checksum-framed journal retain authority.
    std::uint64_t terminal_verification_verified_offset_bytes = 0U;
    bool operator==(const SyncReplicaFilePayloadStoreStageResult&) const =
        default;
};

// One bounded receiver-local whole-target verification obligation already
// discovered by a complete leased payload-store observation. The exact staged
// inode and its journal are re-opened and re-proved before every effect; this
// compact object is scheduler acceleration, never payload authority.
struct SyncReplicaFilePayloadStoreTerminalVerificationWork final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t verified_offset_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadStoreTerminalVerificationWork&) const =
        default;
};

// Filesystem-cold owner-thread status for pending terminal SHA-256 work. A
// fresh store owner reports observation_known=false until an ordinary complete
// snapshot has enumerated the private namespace. Counts and byte frontiers are
// bounded by the configured transient-entry and payload-byte limits.
struct SyncReplicaFilePayloadStoreTerminalVerificationStatus final {
    bool observation_known = false;
    std::uint64_t pending_entry_count = 0U;
    std::uint64_t pending_total_bytes = 0U;
    std::uint64_t pending_verified_bytes = 0U;
    std::optional<SyncReplicaFilePayloadStoreTerminalVerificationWork>
        next_work;

    bool operator==(
        const SyncReplicaFilePayloadStoreTerminalVerificationStatus&) const =
        default;
};

enum class SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition
    : std::uint8_t {
    ObservationUnknown = 1U,
    NoPendingWork = 2U,
    Progress = 3U,
    CompletedInserted = 4U,
    CompletedAlreadyPresent = 5U,
};

[[nodiscard]] std::string_view
sync_replica_file_payload_store_terminal_verification_step_disposition_name(
    SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition
        disposition) noexcept;

struct SyncReplicaFilePayloadStoreTerminalVerificationStepResult final {
    SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition
        disposition =
            SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                ObservationUnknown;
    std::optional<SyncReplicaFilePayloadStoreTerminalVerificationWork>
        work_before;
    std::uint64_t verified_offset_after_bytes = 0U;
    std::uint64_t hashed_bytes = 0U;
    std::uint64_t terminal_verification_steps = 0U;

    bool operator==(
        const SyncReplicaFilePayloadStoreTerminalVerificationStepResult&)
        const = default;
};

[[nodiscard]] bool
sync_replica_file_payload_store_range_basename_is_exact(
    std::string_view basename);

// One raw private partial file is the shipping receiver staging shape. Its
// canonical basename binds the whole-content digest, total size, and exact
// committed contiguous prefix. The file may contain a longer uncommitted tail
// after a crash; reopening truncates that tail to the basename cutpoint before
// accepting more bytes.
[[nodiscard]] bool
sync_replica_file_payload_store_prefix_basename_is_exact(
    std::string_view basename);

// Fixed two-slot terminal SHA-256 journal for one staged-prefix digest. The
// basename is recognized internal progress only; it never grants payload or
// publication authority by itself.
[[nodiscard]] bool
sync_replica_file_payload_store_terminal_verification_basename_is_exact(
    std::string_view basename);

// Canonical non-authoritative quarantine name. It binds both the immutable
// digest name that failed and the exact corrupt byte image observed at the
// quarantine cutpoint. Quarantined bytes are never returned by content
// inventory or targeted payload access.
[[nodiscard]] bool
sync_replica_file_payload_store_quarantine_basename_is_exact(
    std::string_view basename);

enum class SyncReplicaFilePayloadStoreQuarantineAction : std::uint8_t {
    Preserve = 1,
    Release = 2,
};

[[nodiscard]] std::string_view
sync_replica_file_payload_store_quarantine_action_name(
    SyncReplicaFilePayloadStoreQuarantineAction action) noexcept;

enum class SyncReplicaFilePayloadStoreQuarantineDisposition : std::uint8_t {
    Quarantined = 1,
    ActiveFaultMismatch = 2,
    PayloadAbsent = 3,
    PayloadAlreadyRepaired = 4,
    ObservedDigestChanged = 5,
    ExactQuarantineAlreadyPresent = 6,
    EntryCapacityExceeded = 7,
    ByteCapacityExceeded = 8,
    Released = 9,
    ExactQuarantineAbsent = 10,
    ActiveFaultPresent = 11,
};

[[nodiscard]] std::string_view
sync_replica_file_payload_store_quarantine_disposition_name(
    SyncReplicaFilePayloadStoreQuarantineDisposition disposition) noexcept;

struct SyncReplicaFilePayloadStoreQuarantineResult final {
    SyncReplicaFilePayloadStoreQuarantineAction action =
        SyncReplicaFilePayloadStoreQuarantineAction::Preserve;
    SyncReplicaFilePayloadStoreQuarantineDisposition disposition =
        SyncReplicaFilePayloadStoreQuarantineDisposition::ActiveFaultMismatch;
    std::string expected_content_sha256;
    std::string requested_observed_content_sha256;
    std::string current_observed_content_sha256;
    std::string quarantine_basename;
    std::uint64_t size_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadStoreQuarantineResult&) const = default;
};

// One exact retained diagnostic image from the most recent complete leased
// quarantine-namespace observation. Digest pairs select the existing explicit
// release operation; size is metadata evidence only. Quarantined bytes remain
// outside authoritative payload inventory and are not hashed for this status.
struct SyncReplicaFilePayloadStoreQuarantineInventoryEntry final {
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    std::uint64_t size_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadStoreQuarantineInventoryEntry&) const =
        default;
};

// Filesystem-cold, owner-thread status for the bounded diagnostic quarantine.
// A fresh process reports observation_known=false until an ordinary complete
// payload scan or an exact preserve/release action reaches its final rooted
// lease cutpoint. The monotonic age describes that last complete observation;
// it is deliberately not a persisted creation or retention age.
struct SyncReplicaFilePayloadStoreQuarantineInventoryStatus final {
    bool observation_known = false;
    std::optional<std::uint64_t> last_observation_age_milliseconds;
    std::uint64_t entry_limit =
        kSyncReplicaFilePayloadStoreMaxQuarantineEntries;
    std::uint64_t byte_limit = 0U;
    std::uint64_t total_bytes = 0U;
    std::vector<SyncReplicaFilePayloadStoreQuarantineInventoryEntry> entries;

    bool operator==(
        const SyncReplicaFilePayloadStoreQuarantineInventoryStatus&) const =
        default;
};

// Stable classification for the cooperative lease frontier. This is local
// availability evidence, not operation, attempt, or effect authority.
enum class SyncReplicaFilePayloadStoreLeaseMode : std::uint8_t {
    SharedObservation = 1,
    ExclusiveMutation = 2,
};

// Typed local availability result for a cooperative shared/exclusive lease
// conflict. No payload, attempt, or effect authority has been consumed when
// this exception is raised; callers may retry from a fresh observation
// cutpoint without parsing diagnostic text.
class SyncReplicaFilePayloadStoreLeaseBusyError final
    : public std::runtime_error {
public:
    SyncReplicaFilePayloadStoreLeaseBusyError(
        SyncReplicaFilePayloadStoreLeaseMode mode,
        const std::string& message)
        : std::runtime_error(message), mode_(mode) {}

    [[nodiscard]] SyncReplicaFilePayloadStoreLeaseMode mode() const noexcept {
        return mode_;
    }

private:
    SyncReplicaFilePayloadStoreLeaseMode mode_ =
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation;
};

// A bounded scrub reached the exact payload extent over one or more attempts
// and the observed SHA-256 differed from its immutable digest basename. This is
// an integrity alarm, not necessarily a point-in-time byte image. The sole copy
// is never deleted or silently quarantined by this owner. failure_persisted()
// reports
// whether the checksum-framed durable failure witness was committed before the
// exception crossed the API boundary.
class SyncReplicaFilePayloadStoreIntegrityError final
    : public std::runtime_error {
public:
    SyncReplicaFilePayloadStoreIntegrityError(
        std::string expected_content_sha256,
        std::string observed_content_sha256,
        bool failure_persisted,
        const std::string& message)
        : std::runtime_error(message),
          expected_content_sha256_(std::move(expected_content_sha256)),
          observed_content_sha256_(std::move(observed_content_sha256)),
          failure_persisted_(failure_persisted) {}

    [[nodiscard]] const std::string& expected_content_sha256() const noexcept {
        return expected_content_sha256_;
    }
    [[nodiscard]] const std::string& observed_content_sha256() const noexcept {
        return observed_content_sha256_;
    }
    [[nodiscard]] bool failure_persisted() const noexcept {
        return failure_persisted_;
    }

private:
    std::string expected_content_sha256_;
    std::string observed_content_sha256_;
    bool failure_persisted_ = false;
};

enum class SyncReplicaFilePayloadStoreScrubDisposition : std::uint8_t {
    Disabled = 1,
    DeferredBySchedule = 2,
    Empty = 3,
    DeferredLeaseBusy = 4,
    DeferredStaleSnapshot = 5,
    DeferredTransientCapacity = 6,
    DeferredPublicationFailure = 7,
    DeferredAttemptFailure = 8,
    Advanced = 9,
};

[[nodiscard]] std::string_view
sync_replica_file_payload_store_scrub_disposition_name(
    SyncReplicaFilePayloadStoreScrubDisposition disposition) noexcept;

struct SyncReplicaFilePayloadStoreScrubReport final {
    SyncReplicaFilePayloadStoreScrubDisposition disposition =
        SyncReplicaFilePayloadStoreScrubDisposition::Disabled;
    std::uint64_t hashed_bytes = 0U;
    std::uint64_t touched_entry_count = 0U;
    std::uint64_t completed_entry_count = 0U;
    std::uint64_t completed_cycles = 0U;
    std::uint64_t state_generation = 0U;
    std::string active_content_sha256;
    std::uint64_t active_offset_bytes = 0U;
    bool state_rebuilt = false;
    // True when the authoritative snapshot scan itself rehashed and proved an
    // exact Prepared/Progress target good, then this attempt durably advanced
    // past that payload without resuming the older partial SHA-256 checkpoint.
    // The complete scan is the stronger current-byte proof; retaining the stale
    // checkpoint would duplicate potentially unbounded I/O and could report a
    // false mismatch after metadata-hidden repair.
    bool reverified_active_completed = false;
    // True when the authoritative snapshot scan itself rehashed and disproved
    // a matching durable failure witness, then this attempt durably advanced
    // past that payload without performing a redundant second whole-file read.
    bool reverified_failure_cleared = false;

    bool operator==(const SyncReplicaFilePayloadStoreScrubReport&) const =
        default;
};

// Process-local operator projection of the restart-safe scrub scheduler. The
// durable cycle count and continuation position come from the checksum-framed
// scrub record. Ages are deliberately optional: rev0955 did not persist wall
// time, so a fresh process must not invent when a pre-existing cycle completed.
// Once this process observes a report, report age is monotonic-clock based; once
// it itself completes a cycle, last_completed_cycle_age_milliseconds becomes
// available until process restart.
struct SyncReplicaFilePayloadStoreScrubStatus final {
    bool enabled = false;
    std::uint64_t max_bytes_per_attempt = 0U;
    std::uint64_t max_entries_per_attempt = 0U;
    std::optional<SyncReplicaFilePayloadStoreScrubReport> last_report;
    std::optional<std::uint64_t> last_report_age_milliseconds;
    std::optional<std::uint64_t> last_completed_cycle_age_milliseconds;

    bool operator==(const SyncReplicaFilePayloadStoreScrubStatus&) const =
        default;
};

class SyncReplicaFilePayloadStore;
class SyncReplicaFilePayloadStoreSnapshot;
class SyncReplicaFilePayloadStoreMutationBatch;
class SyncReplicaFilePayloadStoreTargetedAccess;
class SyncReplicaFolderScanOwner;
struct SyncReplicaFilePayloadStoreTestAccess;

// Exact same-process, same-durable-store capabilities that can still consume
// or reopen payload bytes independently of the retention planner's own
// snapshot lease. Independently opened owners over the same attested root and
// immutable store identity share this bounded registry. This is intentionally
// narrower than global collection authority: another process is not visible
// here and remains fenced only by the cross-process exact-inode use lease.
struct SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot final {
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;

    bool operator==(
        const SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot&) const =
        default;
};

struct SyncReplicaFilePayloadStoreLiveCapabilityCutpoint final {
    // Deterministic binding of the attested root, current identity basename,
    // and immutable expected identity. The incarnation changes whenever the
    // final in-process owner releases the scope and a later owner recreates it.
    std::string process_store_scope_digest;
    std::string process_store_scope_incarnation_digest;
    std::string capability_set_digest;
    // Non-durable interval witness. The registry advances this generation on
    // every successful capability registration and unregister. It is excluded
    // from capability_set_digest and the deletion-free mark so a quiescent set
    // retains one canonical identity, but before/after cutpoint equality still
    // detects a capability created and destroyed entirely between observations.
    std::uint64_t activity_generation = 0U;
    std::uint64_t snapshot_count = 0U;
    std::uint64_t opened_payload_count = 0U;
    std::uint64_t targeted_access_count = 0U;
    std::uint64_t mutation_batch_count = 0U;
    std::uint64_t distinct_opened_payload_root_count = 0U;
    std::uint64_t distinct_opened_payload_root_bytes = 0U;
    std::vector<SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot>
        opened_payload_roots;

    [[nodiscard]] bool all_current_payloads_may_be_reopened() const noexcept {
        return snapshot_count != 0U || targeted_access_count != 0U ||
               mutation_batch_count != 0U;
    }

    bool operator==(
        const SyncReplicaFilePayloadStoreLiveCapabilityCutpoint&) const =
        default;
};

// Move-only exact source capability for one digest-named durable payload. The
// descriptor remains positioned independently because all consumers use
// pread(2). Metadata and digest are frozen at selection; descriptor-streaming
// publication re-proves both before the destination namespace is committed.
// This object owns the selected descriptor, its same-process-store live-root
// registration, and the shared per-payload inode use lease attached to the
// descriptor's open file description. It never owns the store-wide namespace
// lease or a cleanup capability. The inode lease survives rename and is
// released with the final descriptor close. Callers must therefore keep this
// object bounded to actual local byte consumption and must not retain it across
// network waits, sleeps, or unrelated service work.
class SyncReplicaFilePayloadStoreOpenedPayload final {
public:
    SyncReplicaFilePayloadStoreOpenedPayload() noexcept = default;
    SyncReplicaFilePayloadStoreOpenedPayload(
        const SyncReplicaFilePayloadStoreOpenedPayload&) = delete;
    SyncReplicaFilePayloadStoreOpenedPayload& operator=(
        const SyncReplicaFilePayloadStoreOpenedPayload&) = delete;
    SyncReplicaFilePayloadStoreOpenedPayload(
        SyncReplicaFilePayloadStoreOpenedPayload&&) noexcept;
    SyncReplicaFilePayloadStoreOpenedPayload& operator=(
        SyncReplicaFilePayloadStoreOpenedPayload&&) noexcept;
    ~SyncReplicaFilePayloadStoreOpenedPayload() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] int borrowed_descriptor() const;
    [[nodiscard]] std::uint64_t size_bytes() const;
    [[nodiscard]] const std::string& content_sha256() const;
    [[nodiscard]] const SyncPosixRegularFileSnapshotMetadata& metadata() const;

    // Bounded exact-byte consumers for an already selected immutable payload.
    // Both use pread(2), preserve descriptor position, and re-prove the complete
    // eleven-field observation after reading. The manifest streams through a
    // fixed buffer and retains only one digest per bounded content-defined chunk.
    [[nodiscard]] SyncReplicaFilePayloadStoreRange copy_range_or_throw(
        std::uint64_t offset_bytes,
        std::uint64_t maximum_range_bytes,
        std::string_view label) const;

    // Fills one caller-owned exact range directly from the retained immutable
    // descriptor and returns the SHA-256 of those bytes. No range-sized source
    // string is created. The destination may be empty only for the complete
    // zero-byte payload. The same exact inode observation and whole-payload
    // corruption handling as copy_range_or_throw remain in force.
    [[nodiscard]] std::string copy_exact_range_into_or_throw(
        std::uint64_t offset_bytes,
        std::span<char> destination,
        std::string_view label) const;

    [[nodiscard]] SyncReplicaFilePayloadStoreContentDefinedManifest
    content_defined_manifest_or_throw(
        SyncReplicaContentDefinedChunkingParameters parameters,
        std::string_view label) const;

    // Extends one process-local projection by at most maximum_step_bytes. A
    // fresh projection is initialized from this exact payload observation; a
    // resumed projection must bind the same content identity, size, eleven-
    // field inode observation, and chunking parameters. The descriptor is not
    // retained after this call. Any read or reproof failure discards the
    // process-local progress before propagating the error.
    [[nodiscard]] SyncReplicaFilePayloadStoreContentDefinedProjectionStep
    advance_content_defined_projection_or_throw(
        SyncReplicaFilePayloadStoreContentDefinedProjection& projection,
        SyncReplicaContentDefinedChunkingParameters parameters,
        std::uint64_t maximum_step_bytes,
        std::string_view label) const;

private:
    struct State;

    explicit SyncReplicaFilePayloadStoreOpenedPayload(
        std::unique_ptr<State> state) noexcept;
    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStoreSnapshot;
    friend class SyncReplicaFilePayloadStoreTargetedAccess;
    friend class SyncReplicaReconciliationService;
};

// Move-only pass-scoped authority for bounded exact-name payload access. Birth
// performs the potentially expensive identity bootstrap/reconciliation once,
// freezes the exact identity-marker inode and one matching rooted directory
// capability, and does not enumerate the payload namespace. Each later probe or
// descriptor selection acquires its own fail-fast shared lease and requires the
// marker observation to remain identical to this access cutpoint. The access
// itself therefore holds no store lease across planning or destination I/O.
//
// This is intentionally private product plumbing. The folder-convergence owner
// may use exact absence only as unresolved scheduling evidence; the reconciliation
// source may use it only to return PayloadUnavailable for the exact retained file
// operation. Neither use is namespace-health authority. This lane does not
// enumerate, capacity-attest, or validate unrelated payload-root entries.
// Reserved identity basenames are not unrelated: every exact marker open/reproof
// rejects all competing known generations, including unsupported v1.
// snapshot_or_throw remains the complete-namespace health, capacity, and digest
// inventory oracle. Callers must also bound the access lifetime: while live it
// conservatively roots every current payload for retention planning.
class SyncReplicaFilePayloadStoreTargetedAccess final {
public:
    SyncReplicaFilePayloadStoreTargetedAccess() noexcept = default;
    SyncReplicaFilePayloadStoreTargetedAccess(
        const SyncReplicaFilePayloadStoreTargetedAccess&) = delete;
    SyncReplicaFilePayloadStoreTargetedAccess& operator=(
        const SyncReplicaFilePayloadStoreTargetedAccess&) = delete;
    SyncReplicaFilePayloadStoreTargetedAccess(
        SyncReplicaFilePayloadStoreTargetedAccess&&) noexcept;
    SyncReplicaFilePayloadStoreTargetedAccess& operator=(
        SyncReplicaFilePayloadStoreTargetedAccess&&) noexcept;
    ~SyncReplicaFilePayloadStoreTargetedAccess() noexcept;

    [[nodiscard]] bool active() const noexcept;

private:
    struct State;

    explicit SyncReplicaFilePayloadStoreTargetedAccess(
        std::unique_ptr<State> state) noexcept;

    [[nodiscard]] State& require_state_or_throw(std::string_view label);

    [[nodiscard]] std::optional<std::uint64_t>
    observe_optional_payload_size_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label);

    [[nodiscard]] std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
    open_optional_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label);

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStore;
    friend class SyncReplicaFolderScanOwner;
    friend class SyncReplicaReconciliationService;
};

// Move-only, thread-affine read authority for one bounded observation of a
// durable content directory. Construction acquires a fail-fast shared advisory
// lease on the exact folder-identity marker, passes that move-only witness into
// a dedicated private-root scan, rejects unexpected namespace entries, hashes
// every cold, new, or metadata-changed digest-named regular file without
// retaining its bytes, and may reuse a prior complete verification only while
// the exact inode/mode/link/owner/size/mtime/ctime observation is unchanged.
// It synchronizes newly verified files and directory state, re-proves that the
// marker name still identifies the exact locked inode, and freezes a canonical
// digest/size index. The process-owner-local verification cache and the
// checksum-sealed durable verification checkpoint are acceleration, never
// payload authority. A new owner still performs a complete rooted namespace
// scan, but may avoid payload byte reads only for exact marker-bound checkpoint
// observations. Missing, malformed, stale, or changed observations are hashed
// in full.
// The scan is not hostile-writer-exclusive: noncooperating same-UID/privileged
// writers and
// filesystems that cannot prove independent-open flock exclusion remain outside
// this authority. Lease contention fails rather than blocking an event loop.
//
// The snapshot may be reused synchronously across multiple requests. Its scan
// proves each whole digest either by current hashing or by an exact unchanged
// observation retained from a prior complete hash under the cooperative lease,
// then freezes the exact inode/time/size observation. An unchanged observation
// takes the bounded
// fast path: reopen relative to the retained root, read and hash only the exact
// requested range, then re-prove the named inode and root. If the observation
// drifted, selection performs one complete digest revalidation while retaining
// the requested range; an exact atomic re-publication remains usable, while
// changed bytes fail closed. Each reopen first takes one short store-wide
// shared observation lease, then transfers the exact selected inode into a
// shared per-payload use lease before releasing the store-wide lease. No
// store-wide lease is retained across a network session, so a slow Tor/I2P peer
// cannot block unrelated cooperative publication; the selected descriptor must
// still be released promptly after local byte consumption so later quarantine
// or collection can acquire the inode exclusively. Noncooperating same-UID/
// privileged writers remain outside this authority.
// A process-observed digest mismatch revokes every future method call on a
// still-live snapshot issued by that owner before the alarm. Repair or absence
// can authorize a newly completed snapshot, but cannot resurrect an older
// snapshot. Values or references already returned and a payload descriptor
// already moved out before the alarm are intentionally not revocable
// capabilities.
class SyncReplicaFilePayloadStoreSnapshot final {
public:
    SyncReplicaFilePayloadStoreSnapshot() noexcept = default;
    SyncReplicaFilePayloadStoreSnapshot(
        const SyncReplicaFilePayloadStoreSnapshot&) = delete;
    SyncReplicaFilePayloadStoreSnapshot& operator=(
        const SyncReplicaFilePayloadStoreSnapshot&) = delete;
    SyncReplicaFilePayloadStoreSnapshot(
        SyncReplicaFilePayloadStoreSnapshot&&) noexcept;
    SyncReplicaFilePayloadStoreSnapshot& operator=(
        SyncReplicaFilePayloadStoreSnapshot&&) noexcept;
    ~SyncReplicaFilePayloadStoreSnapshot() noexcept;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] const std::filesystem::path& root_path() const;
    [[nodiscard]] std::uint64_t entry_count() const;
    [[nodiscard]] std::uint64_t indexed_bytes() const;

    // Work performed by the namespace scan that constructed this snapshot.
    // These diagnostic counters do not affect snapshot_digest(). A cold owner
    // hashes every payload; a warm owner may metadata-reuse exact previously
    // verified observations from either the process-local cache or the durable
    // marker-bound checkpoint. The total reused counters are the exact sum of
    // the two origin-specific pairs below. ReadOnlyInspect always performs a
    // cold-style hash and reports zero reuse.
    [[nodiscard]] std::uint64_t scan_hashed_entry_count() const;
    [[nodiscard]] std::uint64_t scan_hashed_bytes() const;
    [[nodiscard]] std::uint64_t scan_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_reused_bytes() const;
    [[nodiscard]] std::uint64_t scan_process_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_process_reused_bytes() const;
    [[nodiscard]] std::uint64_t scan_durable_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_durable_reused_bytes() const;

    // True when this complete authoritative scan proved that the optional
    // restart-checkpoint writer residue could not fit the current transient
    // capacity. The process retains that negative scheduling evidence and does
    // not immediately re-enumerate the namespace under an exclusive lease.
    // This diagnostic does not affect snapshot_digest().
    [[nodiscard]] bool
    verification_checkpoint_deferred_by_transient_capacity() const;

    // One process-throttled, byte- and entry-bounded rotating scrub attempt may
    // follow the complete snapshot scan. This report is diagnostic/scheduling
    // evidence only and does not enter snapshot_digest(). Integrity mismatch is
    // raised as SyncReplicaFilePayloadStoreIntegrityError instead of returned.
    [[nodiscard]] const SyncReplicaFilePayloadStoreScrubReport&
    scrub_report() const;

    [[nodiscard]] std::uint64_t transient_entry_count() const;
    [[nodiscard]] std::uint64_t transient_bytes() const;
    // Exact capacity reservation consumed by the complete transient namespace.
    // Prefix receivers reserve their declared whole-payload extent even when
    // the currently durable prefix is shorter; ranges and crash residues
    // reserve their physical size. This value can therefore exceed
    // transient_bytes(), but never the configured transient-byte frontier.
    [[nodiscard]] std::uint64_t transient_reserved_bytes() const;
    // Canonical identity of every admitted transient namespace obligation at
    // this snapshot cutpoint. The digest binds staged-prefix and staged-range
    // basenames plus their semantic extents, exact assembly/publication
    // residue basenames plus sizes, and one canonical fixed-width POSIX
    // observation for every transient inode. It is namespace/restart-
    // obligation evidence, not a complete-byte proof for opaque crash
    // residues.
    [[nodiscard]] const std::string& transient_namespace_digest() const;
    [[nodiscard]] const std::string& root_attestation_digest() const;
    [[nodiscard]] const std::string& snapshot_digest() const;
    [[nodiscard]] const SyncReplicaFilePayloadStoreLimits& limits() const;

    // Fixed-width historical mark observed during this complete namespace scan.
    // Present-but-unusable distinguishes torn, malformed, stale-identity, or
    // otherwise invalid evidence from clean absence. The file is deliberately
    // excluded from snapshot_digest() and transient accounting so publication
    // cannot self-invalidate the candidate witness it records.
    [[nodiscard]] bool retention_mark_present() const;
    // True only when this snapshot performed the synchronized byte observation
    // needed to distinguish clean absence, a usable exact mark, and damaged or
    // stale evidence. ReadOnlyInspect remains byte-cold and therefore reports
    // this false even when the internal basename is present.
    [[nodiscard]] bool retention_mark_observation_known() const;
    [[nodiscard]] bool retention_mark_usable() const;
    [[nodiscard]] const std::optional<SyncReplicaFilePayloadRetentionMark>&
    retention_mark() const;
    [[nodiscard]] const std::optional<std::string>&
    retention_mark_digest() const;

    [[nodiscard]] SyncReplicaFileContentInventory content_inventory() const;
    [[nodiscard]] std::optional<std::uint64_t> payload_size_or_none(
        std::string_view content_sha256) const;

    [[nodiscard]] SyncReplicaFilePayloadStoreOpenedPayload
    open_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label =
            "sync replica durable file payload open") const;

    // Compatibility/oracle API. Shipping folder apply uses the opened payload
    // above so a large file is never assembled in one std::string.
    [[nodiscard]] std::string copy_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label =
            "sync replica durable file payload lookup") const;

    [[nodiscard]] SyncReplicaFilePayloadStoreRange
    copy_payload_range_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::uint64_t offset_bytes,
        std::uint64_t maximum_range_bytes,
        std::string_view label =
            "sync replica durable file payload range lookup") const;

    void require_folder_or_throw(
        std::string_view folder_id,
        std::string_view label) const;

    // Pure pre-claim authority reproof. No payload bytes are read and no
    // durable sender state is touched.
    void preflight_or_throw(std::string_view label) const;

private:
    struct State;

    explicit SyncReplicaFilePayloadStoreSnapshot(
        std::unique_ptr<State> state) noexcept;

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStore;
};

// Move-only, thread-affine local publication batch. Construction acquires one
// exclusive cooperative store lease, validates and hashes the complete private
// namespace once, removes admitted stale publication residues, and freezes the
// resulting capacity index. Sequential puts then update that exact in-memory
// index after each durable create-new publication instead of rescanning and
// re-hashing every older payload for every new local file. When the batch is
// released, its complete already verified index is published once into the
// process-local warm-verification cache. The next retained snapshot therefore
// does not perform one redundant whole-byte pass over payloads just created by
// that batch. Cache publication is best-effort acceleration and cannot change a
// durable put result.
//
// The batch is deliberately synchronous and narrow. It owns everything needed
// for its bounded mutation scope and may outlive the store handle that created
// it, but it must not be retained across network waits, sleeps, callbacks, or
// unrelated service work because a live batch makes shared snapshots and other
// cooperative mutations fail busy.
// Exceptional publication recovery may perform another complete scan; the
// ordinary successful path performs only the construction scan. The older
// one-put store APIs remain as compatibility/oracle entry points and delegate
// to a one-element batch.
class SyncReplicaFilePayloadStoreMutationBatch final {
public:
    SyncReplicaFilePayloadStoreMutationBatch() noexcept;
    SyncReplicaFilePayloadStoreMutationBatch(
        const SyncReplicaFilePayloadStoreMutationBatch&) = delete;
    SyncReplicaFilePayloadStoreMutationBatch& operator=(
        const SyncReplicaFilePayloadStoreMutationBatch&) = delete;
    SyncReplicaFilePayloadStoreMutationBatch(
        SyncReplicaFilePayloadStoreMutationBatch&&) noexcept;
    SyncReplicaFilePayloadStoreMutationBatch& operator=(
        SyncReplicaFilePayloadStoreMutationBatch&&) noexcept;
    ~SyncReplicaFilePayloadStoreMutationBatch() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] std::uint64_t full_scan_count() const;
    // Cumulative exact byte-verification work performed by construction and
    // any authoritative recovery scans retained by this batch. Reuse counters
    // describe entries whose complete earlier digest proof remained reusable
    // under an exact metadata observation. The origin-specific counters
    // partition the totals into process-local and durable-checkpoint reuse.
    // Diagnostic/scheduling only.
    [[nodiscard]] std::uint64_t scan_hashed_entry_count() const;
    [[nodiscard]] std::uint64_t scan_hashed_bytes() const;
    [[nodiscard]] std::uint64_t scan_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_reused_bytes() const;
    [[nodiscard]] std::uint64_t scan_process_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_process_reused_bytes() const;
    [[nodiscard]] std::uint64_t scan_durable_reused_entry_count() const;
    [[nodiscard]] std::uint64_t scan_durable_reused_bytes() const;
    [[nodiscard]] std::uint64_t put_count() const;
    // Exact bytes presented to put operations, including duplicate proofs.
    // Diagnostic/scheduling accounting only; it grants no payload authority.
    [[nodiscard]] std::uint64_t source_bytes() const;
    [[nodiscard]] std::uint64_t inserted_count() const;
    [[nodiscard]] std::uint64_t already_present_count() const;
    [[nodiscard]] std::uint64_t indexed_entry_count() const;
    [[nodiscard]] std::uint64_t indexed_bytes() const;

    [[nodiscard]] SyncReplicaFilePayloadStorePutResult put_payload_or_throw(
        std::string payload);

    [[nodiscard]] SyncReplicaFilePayloadStorePutResult
    put_payload_from_borrowed_descriptor_or_throw(
        int source_descriptor,
        const SyncPosixRegularFileSnapshotMetadata& expected_source,
        std::string content_sha256);

    // Re-proves the exact lock anchor and retained root without scanning or
    // reading payload bytes. A poisoned batch (one whose failed publication
    // could not be authoritatively reconciled) rejects every later operation.
    void preflight_or_throw(
        std::string_view label =
            "sync replica file payload mutation batch") const;

private:
    struct State;

    explicit SyncReplicaFilePayloadStoreMutationBatch(
        std::unique_ptr<State> state) noexcept;
    [[nodiscard]] State& require_state_or_throw(std::string_view label);
    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;
    void refresh_namespace_after_failure_or_throw(std::string_view phase);

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStore;
};

// Durable content-addressed directory owner. Payload bytes are published under
// their full lowercase SHA-256 name through the existing descriptor-relative,
// create-new, file-sync, no-replace rename, and directory-sync owner. A put holds
// a fail-fast exclusive advisory lease on the exact immutable folder marker from
// full-store capacity preflight through publication/reconciliation. The scan
// requires that exact lease witness and re-proves the locked anchor after
// traversal. Cooperative processes using this owner therefore cannot
// independently spend the same
// aggregate budget. The root must already exist as a dedicated private
// directory; this class never guesses directory creation, cleanup, garbage
// collection, or hostile-writer authority.
class SyncReplicaFilePayloadStore final {
public:
    SyncReplicaFilePayloadStore(
        std::string folder_id,
        std::filesystem::path absolute_root_directory,
        SyncReplicaFilePayloadStoreOpenDisposition disposition,
        SyncReplicaFilePayloadStoreLimits limits = {},
        std::string label = "sync replica file payload store");

    // Product-bound form. The immutable v3 identity bytes commit the deployment
    // ID, exact manifest digest/path, folder, and local actor. The current
    // reader-fenced basename raises the minimum supported reader generation;
    // writable opens migrate the exact legacy v3 lock inode only after a cold
    // complete-byte proof. It remains intentionally incompatible with the
    // standalone v2 folder-only identity, so an independently initialized
    // payload directory cannot be recomposed into a committed deployment.
    SyncReplicaFilePayloadStore(
        SyncReplicaDeploymentIdentity deployment_identity,
        std::filesystem::path absolute_root_directory,
        SyncReplicaFilePayloadStoreOpenDisposition disposition,
        SyncReplicaFilePayloadStoreLimits limits = {},
        std::string label = "sync replica product-bound file payload store");

    SyncReplicaFilePayloadStore(
        const SyncReplicaFilePayloadStore&) = delete;
    SyncReplicaFilePayloadStore& operator=(
        const SyncReplicaFilePayloadStore&) = delete;
    SyncReplicaFilePayloadStore(
        SyncReplicaFilePayloadStore&&) = delete;
    SyncReplicaFilePayloadStore& operator=(
        SyncReplicaFilePayloadStore&&) = delete;
    ~SyncReplicaFilePayloadStore() noexcept;

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] const std::filesystem::path& root_path() const;
    [[nodiscard]] const SyncReplicaFilePayloadStoreLimits& limits() const;

    // Cheap exact-owner status projection. This performs no filesystem I/O and
    // grants no payload or scheduling authority. It is intended for immutable
    // status serialization on the store's originating owner thread.
    [[nodiscard]] SyncReplicaFilePayloadStoreScrubStatus scrub_status() const;

    // Allocation-free owner-thread readiness predicate for the same cached
    // observation rendered by quarantine_inventory_status(). It performs no
    // filesystem I/O and exists so service readiness cannot silently diverge
    // from diagnostic-inventory discoverability after a failed mutation.
    [[nodiscard]] bool quarantine_inventory_observation_known() const;

    // Returns the last complete bounded quarantine observation already proved
    // by ordinary store work. This method performs no filesystem I/O, acquires
    // no store lease, and hashes no bytes; it is exact-thread owner status in
    // the same sense as scrub_status().
    [[nodiscard]] SyncReplicaFilePayloadStoreQuarantineInventoryStatus
    quarantine_inventory_status() const;

    // Returns the bounded process-local projection established by the most
    // recent complete writable store observation and maintained by exact
    // prefix staging. This method performs no filesystem I/O and advances no
    // durable scheduler state.
    [[nodiscard]] SyncReplicaFilePayloadStoreTerminalVerificationStatus
    terminal_verification_status() const;

    // Advances at most one exact 32 MiB whole-target SHA-256 step for the
    // fairest currently known completed staged prefix. It accepts no peer
    // bytes, opens only the exact prefix/journal/identity names during
    // nonterminal progress, and retains the existing complete-store scan as
    // the final publication fence. A fresh owner first needs one ordinary
    // complete snapshot to discover restart obligations.
    [[nodiscard]] SyncReplicaFilePayloadStoreTerminalVerificationStepResult
    continue_one_pending_terminal_verification_or_throw();

    // Shipping many-file publication seam. One complete store scan and one
    // exclusive lease are amortized across a bounded synchronous caller-owned
    // batch. The caller must destroy the batch before awaiting peer I/O or
    // requesting a payload snapshot.
    [[nodiscard]] SyncReplicaFilePayloadStoreMutationBatch
    begin_mutation_batch_or_throw();

    [[nodiscard]] SyncReplicaFilePayloadStorePutResult put_payload_or_throw(
        std::string payload);

    // Production local-file admission. The source descriptor remains borrowed.
    // The exact metadata/digest pair must come from a retained observation; the
    // publisher re-proves metadata and hashes while copying before the
    // digest-named namespace entry can become visible.
    [[nodiscard]] SyncReplicaFilePayloadStorePutResult
    put_payload_from_borrowed_descriptor_or_throw(
        int source_descriptor,
        const SyncPosixRegularFileSnapshotMetadata& expected_source,
        std::string content_sha256);

    [[nodiscard]] SyncReplicaFilePayloadStoreStageResult
    stage_payload_range_or_throw(
        std::string content_sha256,
        std::uint64_t total_size_bytes,
        std::uint64_t offset_bytes,
        std::string chunk_sha256,
        std::string bytes);

    // Production contiguous-range receiver. New transfers reserve one private
    // raw partial file instead of one immutable file per range plus a second
    // whole-file assembly. Each accepted range is written and fsynced first;
    // an atomic no-replace rename then advances the committed prefix encoded in
    // the basename. A crash before that rename leaves a conservatively
    // truncatable tail.
    //
    // Once the exact committed prefix reaches total_size_bytes, terminal
    // verification is a separate bounded phase. One checksum-framed two-slot
    // journal binds a provider-independent SHA-256 checkpoint to the current
    // store identity and exact complete staged inode. Each owner call reads at
    // most 32 MiB from that descriptor. Progress returns
    // next_offset_bytes == total_size_bytes; reconciliation generation 9 keeps
    // the same operation and prior cursor live through payload-cold turns. The
    // journal is never publication authority: the current process must finish
    // SHA-256, compare the trusted whole-content digest, and rename that exact
    // opened inode before the durable payload exists.
    //
    // stage_payload_range_or_throw remains the range-file compatibility and
    // differential-oracle path for transfers started by revision 0941.
    [[nodiscard]] SyncReplicaFilePayloadStoreStageResult
    stage_payload_prefix_or_throw(
        std::string content_sha256,
        std::uint64_t total_size_bytes,
        std::uint64_t offset_bytes,
        std::string chunk_sha256,
        std::string_view bytes);

    // Commits the exact authenticated range under the same writer-fenced
    // prefix owner, but never starts or advances terminal whole-target SHA-256.
    // A range that completes the byte prefix therefore returns Progress at the
    // exact total-size cutpoint. Reconciliation uses this narrow variant only
    // after its per-apply terminal-step budget is exhausted; a later local
    // continuation must still verify and publish the exact staged inode.
    [[nodiscard]] SyncReplicaFilePayloadStoreStageResult
    stage_payload_prefix_deferring_terminal_verification_or_throw(
        std::string content_sha256,
        std::uint64_t total_size_bytes,
        std::uint64_t offset_bytes,
        std::string chunk_sha256,
        std::string_view bytes);

    // Advances only the local exact whole-target SHA-256 continuation after
    // the complete staged prefix is durable. No source range or chunk bytes
    // are accepted; each call reads at most the bounded terminal-verification
    // frontier from the exact staged inode and either persists nonterminal
    // computational progress or publishes the fully verified payload.
    [[nodiscard]] SyncReplicaFilePayloadStoreStageResult
    continue_staged_payload_prefix_verification_or_throw(
        std::string content_sha256,
        std::uint64_t total_size_bytes);

    [[nodiscard]] SyncReplicaFilePayloadStoreSnapshot snapshot_or_throw() const;

    // Owner-triggered current-byte proof. This takes the same complete rooted
    // shared-lease snapshot as snapshot_or_throw(), but mechanically disables
    // both process-local and durable digest reuse. Every current payload byte is
    // hashed before authority is returned; the exact resulting snapshot can be
    // moved directly into ordinary convergence without a second namespace scan.
    [[nodiscard]] SyncReplicaFilePayloadStoreSnapshot
    snapshot_rechecking_current_bytes_or_throw() const;

    // Explicitly preserves one exact currently corrupt payload image outside
    // the authoritative digest namespace. The request must match the active
    // process-local integrity witness exactly. Under the exclusive store lease,
    // current bytes are rehashed again; changed, repaired, or absent content is
    // reported without rename. A successful no-replace rename is directory-
    // synced and leaves the integrity alarm active until a later complete scan
    // proves the authoritative digest name absent or good.
    [[nodiscard]] SyncReplicaFilePayloadStoreQuarantineResult
    quarantine_corrupt_payload_or_throw(
        std::string expected_content_sha256,
        std::string observed_content_sha256);

    // Explicitly releases one exact retained diagnostic image after the active
    // process integrity alarm has cleared. The exact canonical pair selects a
    // single rooted private regular file; the operation holds the exclusive
    // reader-fenced store lease, unlinks only the opened inode, synchronizes
    // the directory, and proves absence. It does not inspect authoritative
    // payload bytes, imply repair, or introduce automatic retention/GC policy.
    [[nodiscard]] SyncReplicaFilePayloadStoreQuarantineResult
    release_quarantined_payload_or_throw(
        std::string expected_content_sha256,
        std::string observed_content_sha256);

private:
    [[nodiscard]] SyncReplicaFilePayloadStoreStageResult
    stage_payload_prefix_impl_or_throw(
        std::string content_sha256,
        std::uint64_t total_size_bytes,
        std::uint64_t offset_bytes,
        std::string chunk_sha256,
        std::string_view bytes,
        bool terminal_verification_only,
        bool defer_terminal_verification);

    [[nodiscard]] SyncReplicaFilePayloadStoreSnapshot
    snapshot_with_reuse_policy_or_throw(
        bool require_current_bytes,
        bool retain_exclusive_writer_fence) const;

    // Private retention-planner observation. The complete namespace scan is
    // made beneath the current store identity's fail-fast exclusive lease and
    // that exact lock remains owned by the returned snapshot until destruction.
    // The snapshot is metadata-only while fenced: byte-selection methods would
    // attempt the normal shared re-entry and are intentionally unavailable to
    // the folder owner. No scrub or checkpoint publication is scheduled while
    // the fence is retained.
    [[nodiscard]] SyncReplicaFilePayloadStoreSnapshot
    snapshot_writer_fenced_for_retention_or_throw() const;

    // Probes one exact snapshot entry for an exclusive per-payload use lease
    // while the snapshot's store-global writer fence is still live. False is a
    // typed point-in-time busy observation, not an error and not a durable root.
    [[nodiscard]] bool
    writer_fenced_payload_use_exclusive_available_or_throw(
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view content_sha256,
        std::uint64_t size_bytes,
        std::string_view label) const;

    void verify_writer_fenced_retention_snapshot_or_throw(
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view label) const;

    // Publishes one policy-bound historical mark while the caller still owns
    // the exact complete writer-fenced payload snapshot that produced its
    // candidate witness. The caller supplies source/candidate fields; this owner
    // overwrites identity and generation fields, atomically replaces any
    // recognized prior mark, and re-opens the exact committed record before
    // returning. No second namespace scan, payload rename, or unlink occurs.
    [[nodiscard]] SyncReplicaFilePayloadRetentionMarkPublication
    publish_retention_mark_or_throw(
        const SyncReplicaFilePayloadStoreSnapshot& writer_fenced_snapshot,
        SyncReplicaFilePayloadRetentionMark mark) const;

    // Exact-owner composition fence for a snapshot handed directly into the
    // retained folder owner. Folder/root/limit equality is not enough: another
    // independently opened handle to the same durable store owns a different
    // process-local integrity epoch and verification cache. Only a snapshot
    // issued by this exact store handle may be reused without another complete
    // namespace observation.
    void require_exact_snapshot_origin_or_throw(
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view label) const;

    // Starts the bounded exact-name lane without retaining a shared lease. The
    // returned authority amortizes identity durability/bootstrap and root
    // selection across one convergence pass while each probe/selection still
    // re-locks and re-proves the exact marker. Explicit identity genesis retains
    // its complete namespace preflight before this lane can begin.
    [[nodiscard]] SyncReplicaFilePayloadStoreTargetedAccess
    begin_targeted_access_or_throw(std::string_view label) const;

    // Optional bounded source-manifest acceleration. Both methods acquire the
    // store-global lease and must therefore be called without any retained
    // opened-payload descriptor. The publisher overwrites store identity and
    // generation, atomically replaces a recognized predecessor, and reopens
    // the exact committed record before returning.
    [[nodiscard]] std::optional<SyncReplicaSourceManifestCheckpoint>
    load_source_manifest_checkpoint_or_none_or_throw(
        std::string_view label) const;

    // Mutates the caller-owned bounded candidate in place with the exact store
    // identity and successor generation before publication. Keeping the
    // caller's vector storage stable is intentional: the reconciliation owner
    // may retain this same candidate across typed lease or atomic-publication
    // deferral without copying the complete <=8,192-chunk sequence.
    void publish_source_manifest_checkpoint_or_throw(
        SyncReplicaSourceManifestCheckpoint& checkpoint,
        std::string_view label) const;

    // Filesystem-cold owner-thread scheduling witness for bounded negative
    // payload discovery. The generation advances after this exact retained
    // store owner proves a newly visible durable payload publication (and may
    // conservatively advance while reconciling a post-publication failure).
    // It does not prove that any particular digest exists, that the namespace
    // is healthy or complete, or that a payload remains available. Generation
    // exhaustion returns nullopt so consumers must stop caching absence.
    [[nodiscard]] std::optional<std::uint64_t>
    payload_availability_generation_or_throw(std::string_view label) const;

    // Same-owner process-lifetime observation for deletion-free retention
    // planning. The supplied snapshot is excluded because the planner itself
    // necessarily owns it. Exact-origin proof prevents another independently
    // opened handle from subtracting a foreign capability. The result performs
    // no filesystem I/O and grants no collection authority.
    [[nodiscard]] SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
    live_capability_cutpoint_excluding_snapshot_or_throw(
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view label) const;

    struct State;
    std::unique_ptr<State> state_;

    friend class SyncReplicaFolderScanOwner;
    friend class SyncReplicaReconciliationService;
    // The focused payload-store regression defines this bridge in its own
    // translation unit. No shipping implementation or public operation is
    // added merely to inspect the private deletion-free cutpoint.
    friend struct SyncReplicaFilePayloadStoreTestAccess;
};

}  // namespace anonsync

#endif
