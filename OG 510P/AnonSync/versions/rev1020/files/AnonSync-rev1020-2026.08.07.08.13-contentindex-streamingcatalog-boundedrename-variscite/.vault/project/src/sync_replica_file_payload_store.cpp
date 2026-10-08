#include "sync_replica_file_payload_store.hpp"

#include "sync_replica_file_payload_verification_index.hpp"
#include "sync_replica_file_payload_scrub_state.hpp"
#include "sync_replica_file_payload_terminal_verification_state.hpp"
#include "sync_replica_file_payload_retention_mark.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "resumable_sha256.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_directory_authority.hpp"
#include "sync_directory_authority_internal.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_posix_directory_resolution.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <charconv>
#include <chrono>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <dirent.h>
#include <exception>
#include <fcntl.h>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <random>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <type_traits>
#include <utility>
#include <vector>

#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::string_view kSnapshotDigestDomain =
    "anonsync:sync-replica-file-payload-store-snapshot:v4";
constexpr std::string_view kTransientNamespaceDigestDomain =
    "anonsync:sync-replica-file-payload-store-transient-namespace:v2";
// The identity payload generation and the minimum-reader basename generation
// are deliberately separate. rev0959 keeps the exact v2/v3 identity bytes but
// moves the flock anchor to a name that older readers do not recognize. That
// atomic, inode-preserving rename is the downgrade fence for the rev0958
// Prepared scrub-state semantics.
constexpr std::string_view kStandaloneStoreIdentityBasenameV2ReaderFenceV1 =
    ".anonsync-payload-store-identity-v2-reader-fence-v1";
constexpr std::string_view kProductStoreIdentityBasenameV3ReaderFenceV1 =
    ".anonsync-payload-store-identity-v3-reader-fence-v1";
constexpr std::string_view kStandaloneStoreIdentityBasenameV2LegacyReader =
    ".anonsync-payload-store-identity-v2";
constexpr std::string_view kProductStoreIdentityBasenameV3LegacyReader =
    ".anonsync-payload-store-identity-v3";
constexpr std::string_view kLegacyStoreIdentityBasenameV1 =
    ".anonsync-payload-store-identity-v1";
// Lease-capable names are the generations this reader may select as the exact
// lock anchor. The broader known-name set also includes v1: this reader can
// never select or migrate v1, but every exact-name lane must still reject it as
// a competing lock authority rather than silently proceeding without a full
// namespace traversal.
constexpr std::array<std::string_view, 4U>
    kLeaseCapableStoreIdentityBasenames{
        kStandaloneStoreIdentityBasenameV2ReaderFenceV1,
        kProductStoreIdentityBasenameV3ReaderFenceV1,
        kStandaloneStoreIdentityBasenameV2LegacyReader,
        kProductStoreIdentityBasenameV3LegacyReader,
    };
constexpr std::array<std::string_view, 5U> kKnownStoreIdentityBasenames{
    kStandaloneStoreIdentityBasenameV2ReaderFenceV1,
    kProductStoreIdentityBasenameV3ReaderFenceV1,
    kStandaloneStoreIdentityBasenameV2LegacyReader,
    kProductStoreIdentityBasenameV3LegacyReader,
    kLegacyStoreIdentityBasenameV1,
};
constexpr std::string_view kStandaloneStoreIdentityDomainV2 =
    "anonsync:sync-replica-file-payload-store-identity:v2";
constexpr std::string_view kProductStoreIdentityDomainV3 =
    "anonsync:sync-replica-file-payload-store-identity:v3";
constexpr std::string_view kStoreLeaseProtocol =
    "anonsync:sync-replica-file-payload-store-flock-lease:v1";
// A committed payload descriptor that escapes the short store-namespace
// observation cutpoint carries its own shared advisory lock on the exact
// payload inode. A future collector must hold the ordinary exclusive store
// lease first and then acquire an exclusive lock on the candidate inode before
// rename or unlink. That ordering prevents new readers while detecting readers
// whose already-open descriptors outlive the namespace observation without
// retaining the global store lease across large local publication I/O.
static_assert(!kSyncReplicaFilePayloadUseLeaseProtocol.empty());
constexpr std::string_view kStagedRangeBasenamePrefix =
    ".anonsync-payload-range-v1-";
constexpr std::string_view kStagedPrefixBasenamePrefix =
    ".anonsync-payload-prefix-v1-";
constexpr std::string_view kAssemblyBasenamePrefix =
    ".anonsync-payload-assemble-v1-";
constexpr std::string_view kQuarantineBasenamePrefix =
    ".anonsync-payload-quarantine-v1-";
constexpr std::size_t kSha256HexCharacters = 64U;
constexpr std::size_t kStreamingBufferBytes = 64U * 1024U;
constexpr std::uint64_t kMaximumPersistentInteger =
    static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());
// A complete verification checkpoint is O(payload identities), so rewriting it
// after every one-file compatibility batch would turn an N-file initial sync
// into O(N^2) metadata writes. Runtime checkpoints therefore grow
// geometrically, with bounded tails once a store is large. Graceful owner
// teardown still attempts one final checkpoint; a crash merely leaves the
// bounded dirty tail to be byte-hashed on the next authoritative scan.
constexpr std::uint64_t kVerificationCheckpointMinimumAddedEntries = 256U;
constexpr std::uint64_t kVerificationCheckpointMaximumAddedEntries = 4096U;
constexpr std::uint64_t kVerificationCheckpointMinimumAddedBytes =
    64ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kVerificationCheckpointMaximumAddedBytes =
    1024ULL * 1024ULL * 1024ULL;
// Repeated complete payload snapshots can occur within one convergence pass.
// Bound scrub I/O once per process minute instead of charging every snapshot;
// restart intentionally makes one immediate attempt so durable continuation
// advances even for short-lived one-shot invocations.
constexpr auto kPayloadScrubMinimumInterval = std::chrono::minutes(1);
// A non-cooperating same-UID writer can invalidate one complete namespace
// observation even while the cooperative shared/exclusive lease remains
// exact. Restart once from a fresh descriptor-rooted directory cursor. The
// complete scanner publishes neither a verification generation nor snapshot
// authority before its final cutpoint, so the first stale attempt is
// disposable. A second drift remains terminal and bounded rather than turning
// an externally mutable private store into an unbounded retry loop.
constexpr std::uint32_t kMaximumCompleteScanObservationAttempts = 2U;
constexpr std::string_view kLiveCapabilityProcessStoreScopeDomain =
    "anonsync:sync-replica-file-payload-store-live-capability-process-store-scope:v1";
constexpr std::string_view kLiveCapabilityProcessStoreScopeIncarnationDomain =
    "anonsync:sync-replica-file-payload-store-live-capability-process-store-incarnation:v1";
constexpr std::string_view kLiveCapabilitySetDigestDomain =
    "anonsync:sync-replica-file-payload-store-live-capability-set:v2";
constexpr std::uint64_t kLiveCapabilityFixedRecordAllowance = 4096U;
constexpr std::size_t kMaximumProcessLiveCapabilityStoreScopes = 4096U;
static_assert(
    kSyncReplicaFilePayloadStoreMaxEntries <=
    std::numeric_limits<std::uint64_t>::max() -
        kLiveCapabilityFixedRecordAllowance);
constexpr std::uint64_t kMaximumProcessLiveCapabilityRecordsPerStore =
    kSyncReplicaFilePayloadStoreMaxEntries +
    kLiveCapabilityFixedRecordAllowance;

class PayloadStoreObservationStaleError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

template <std::size_t Size>
[[nodiscard]] bool payload_store_identity_basename_is_in(
    const std::array<std::string_view, Size>& names,
    std::string_view basename) noexcept {
    return std::find(names.begin(), names.end(), basename) != names.end();
}

[[nodiscard]] bool payload_store_identity_basename_is_lease_capable(
    std::string_view basename) noexcept {
    return payload_store_identity_basename_is_in(
        kLeaseCapableStoreIdentityBasenames, basename);
}

[[nodiscard]] bool payload_store_identity_basename_is_known(
    std::string_view basename) noexcept {
    return payload_store_identity_basename_is_in(
        kKnownStoreIdentityBasenames, basename);
}

[[nodiscard]] bool payload_store_identity_basenames_are_supported_upgrade_pair(
    std::string_view legacy_basename,
    std::string_view current_basename) noexcept {
    return (legacy_basename ==
                kStandaloneStoreIdentityBasenameV2LegacyReader &&
            current_basename ==
                kStandaloneStoreIdentityBasenameV2ReaderFenceV1) ||
           (legacy_basename ==
                kProductStoreIdentityBasenameV3LegacyReader &&
            current_basename ==
                kProductStoreIdentityBasenameV3ReaderFenceV1);
}

class OwnedFd final {
public:
    explicit OwnedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~OwnedFd() { reset(); }
    OwnedFd(const OwnedFd&) = delete;
    OwnedFd& operator=(const OwnedFd&) = delete;
    OwnedFd(OwnedFd&& other) noexcept
        : descriptor_(other.release()) {}
    OwnedFd& operator=(OwnedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }

private:
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

    int descriptor_ = -1;
};

class OwnedDirectoryStream final {
public:
    explicit OwnedDirectoryStream(DIR* stream = nullptr) noexcept
        : stream_(stream) {}
    ~OwnedDirectoryStream() {
        if (stream_ != nullptr) (void)::closedir(stream_);
    }
    OwnedDirectoryStream(const OwnedDirectoryStream&) = delete;
    OwnedDirectoryStream& operator=(const OwnedDirectoryStream&) = delete;

    [[nodiscard]] DIR* get() const noexcept { return stream_; }

private:
    DIR* stream_ = nullptr;
};

struct PayloadIndexEntry final {
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;
    struct stat status {};
};

struct StagedRangeEntry final {
    std::string basename;
    std::string content_sha256;
    std::uint64_t offset_bytes = 0U;
    std::string chunk_sha256;
    std::uint64_t size_bytes = 0U;
    struct stat status {};
};

struct StagedPrefixEntry final {
    std::string basename;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t committed_prefix_bytes = 0U;
    std::uint64_t actual_size_bytes = 0U;
    struct stat status {};
};

struct AssemblyEntry final {
    std::string basename;
    std::uint64_t size_bytes = 0U;
    struct stat status {};
};

struct PublicationResidueEntry final {
    std::string basename;
    std::uint64_t size_bytes = 0U;
    struct stat status {};
};

[[nodiscard]] bool staged_prefix_precedes(
    const StagedPrefixEntry& left,
    const StagedPrefixEntry& right) noexcept {
    if (left.content_sha256 != right.content_sha256) {
        return left.content_sha256 < right.content_sha256;
    }
    if (left.total_size_bytes != right.total_size_bytes) {
        return left.total_size_bytes < right.total_size_bytes;
    }
    return left.committed_prefix_bytes < right.committed_prefix_bytes;
}

[[nodiscard]] bool staged_range_precedes(
    const StagedRangeEntry& left,
    const StagedRangeEntry& right) noexcept {
    if (left.content_sha256 != right.content_sha256) {
        return left.content_sha256 < right.content_sha256;
    }
    if (left.offset_bytes != right.offset_bytes) {
        return left.offset_bytes < right.offset_bytes;
    }
    return left.chunk_sha256 < right.chunk_sha256;
}

[[nodiscard]] bool assembly_precedes(
    const AssemblyEntry& left,
    const AssemblyEntry& right) noexcept {
    return left.basename < right.basename;
}

[[nodiscard]] bool publication_residue_precedes(
    const PublicationResidueEntry& left,
    const PublicationResidueEntry& right) noexcept {
    return left.basename < right.basename;
}

struct QuarantineEntry final {
    std::string basename;
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    std::uint64_t size_bytes = 0U;
    struct stat status {};
};

struct VerificationIndexFileObservation final {
    bool present = false;
    bool usable = false;
    struct stat status {};
    std::optional<SyncPosixRegularFileSnapshotMetadata> metadata;
    std::optional<SyncReplicaFilePayloadVerificationIndex> index;
};

struct ScrubStateFileObservation final {
    bool present = false;
    bool usable = false;
    struct stat status {};
    std::optional<SyncPosixRegularFileSnapshotMetadata> metadata;
    std::optional<SyncReplicaFilePayloadScrubState> state;
};

struct TerminalVerificationStateFileObservation final {
    bool present = false;
    bool usable = false;
    struct stat status {};
    std::optional<SyncPosixRegularFileSnapshotMetadata> metadata;
    std::optional<SyncReplicaFilePayloadTerminalVerificationJournal> journal;
};

struct TerminalVerificationJournalEntry final {
    std::string content_sha256;
    bool usable = false;
    std::optional<SyncReplicaFilePayloadTerminalVerificationState>
        latest_state;
};

struct RetentionMarkFileObservation final {
    bool present = false;
    bool usable = false;
    struct stat status {};
    std::optional<SyncPosixRegularFileSnapshotMetadata> metadata;
    std::optional<SyncReplicaFilePayloadRetentionMark> mark;
    std::optional<std::string> mark_digest;
};

struct SourceManifestCheckpointFileObservation final {
    bool present = false;
    bool usable = false;
    struct stat status {};
    std::optional<SyncPosixRegularFileSnapshotMetadata> metadata;
    std::optional<SyncReplicaSourceManifestCheckpoint> checkpoint;
};

struct ScannedPayloadIndex final {
    std::vector<PayloadIndexEntry> entries;
    std::vector<StagedRangeEntry> staged_ranges;
    std::vector<StagedPrefixEntry> staged_prefixes;
    std::vector<AssemblyEntry> assemblies;
    std::vector<PublicationResidueEntry> publication_residues;
    std::vector<QuarantineEntry> quarantines;
    std::vector<TerminalVerificationJournalEntry>
        terminal_verification_journals;
    std::vector<SyncReplicaFilePayloadStoreTerminalVerificationWork>
        terminal_verification_work;
    std::uint64_t indexed_bytes = 0U;
    std::uint64_t quarantine_bytes = 0U;
    // Diagnostic work accounting for this scan. These values never enter the
    // canonical snapshot digest: an exact cold scan and an exact warm scan
    // describe the same durable content authority.
    std::uint64_t scan_hashed_entry_count = 0U;
    std::uint64_t scan_hashed_bytes = 0U;
    std::uint64_t scan_reused_entry_count = 0U;
    std::uint64_t scan_reused_bytes = 0U;
    std::uint64_t scan_process_reused_entry_count = 0U;
    std::uint64_t scan_process_reused_bytes = 0U;
    std::uint64_t scan_durable_reused_entry_count = 0U;
    std::uint64_t scan_durable_reused_bytes = 0U;
    std::uint64_t transient_entry_count = 0U;
    // Physical bytes currently present in transient files. Prefix owners
    // reserve their full declared extent separately so a short durable prefix
    // cannot overcommit the bounded completion frontier.
    std::uint64_t transient_bytes = 0U;
    std::uint64_t transient_reserved_bytes = 0U;
    // One fixed-size terminal-hash journal may accompany each staged prefix.
    // These checksum-framed computation checkpoints are recognized private
    // metadata, not payload or transfer obligations, so they remain outside
    // the public transient count/byte/digest surfaces.
    std::uint64_t terminal_verification_entry_count = 0U;
    bool identity_present = false;
    // Internal restart acceleration is outside content/transient accounting.
    // These fields retain only enough exact namespace state to conditionally
    // replace a stale/malformed record after a successful authoritative scan.
    bool verification_index_present = false;
    bool verification_index_contents_requested = false;
    bool verification_index_usable = false;
    bool verification_index_current = false;
    std::uint64_t verification_index_entry_count = 0U;
    std::uint64_t verification_index_indexed_bytes = 0U;
    std::optional<SyncPosixRegularFileSnapshotMetadata>
        verification_index_metadata;

    // Fixed-size rotating scrub scheduling/failure evidence is outside payload
    // and transient accounting. A matching IntegrityFailure forces a complete
    // payload hash in this scan; it never grants failure authority by itself.
    bool scrub_state_present = false;
    bool scrub_state_contents_requested = false;
    bool scrub_state_usable = false;
    bool scrub_active_reverified_good = false;
    bool scrub_failure_reverified_good = false;
    bool process_integrity_fault_reverified_good = false;
    std::optional<SyncPosixRegularFileSnapshotMetadata> scrub_state_metadata;
    std::optional<SyncReplicaFilePayloadScrubState> scrub_state;

    // Historical retention policy evidence is recognized internal metadata. It
    // is never payload content, a transient protocol obligation, or acceleration
    // authority. Synchronized writable scans carry exact usability; byte-cold
    // forensic inspection carries only namespace presence.
    bool retention_mark_present = false;
    bool retention_mark_contents_requested = false;
    bool retention_mark_usable = false;
    std::optional<SyncPosixRegularFileSnapshotMetadata> retention_mark_metadata;
    std::optional<SyncReplicaFilePayloadRetentionMark> retention_mark;
    std::optional<std::string> retention_mark_digest;
    struct stat directory_status {};
};

struct VerificationIndexPublicationCapacity final {
    std::uint64_t encoded_bytes = 0U;
    bool available = false;
};

[[nodiscard]] VerificationIndexPublicationCapacity
verification_index_publication_capacity_or_throw(
    const ScannedPayloadIndex& scanned,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view label);

// Process-owner-local acceleration only. Every cached entry originated in a
// complete digest verification under the cooperative lease and is reusable
// only while the exact inode/mode/link/owner/size/mtime/ctime observation is
// unchanged. It is neither durable authority nor a substitute for cold-start
// verification.
//
// Generations are immutable after publication. Cache access is deliberately
// unsynchronized: every store, batch, targeted-access, and snapshot path proves
// its originating-thread-bound directory authority before it can read or
// replace this pointer. The shared pointer carries lifetime only, allowing a
// batch or snapshot to outlive the store handle that created it; it does not
// grant cross-thread execution. A complete replacement generation is published
// only after the final lease proof.
struct PayloadVerificationGeneration final {
    std::optional<struct stat> identity_status;
    std::vector<PayloadIndexEntry> entries;
};

struct PayloadVerificationCheckpointState final {
    // observation_known means one complete leased scan has established whether
    // the durable checkpoint was absent, unusable, stale, or exact. The state
    // remains process-local scheduling evidence and never grants payload reuse.
    bool observation_known = false;
    bool force_checkpoint = false;
    std::uint64_t durable_entry_count = 0U;
    std::uint64_t durable_indexed_bytes = 0U;
    std::uint64_t pending_added_entries = 0U;
    std::uint64_t pending_added_bytes = 0U;
    // One complete leased scan can also prove that the non-authoritative
    // checkpoint writer residue cannot fit the current transient frontier.
    // Retain that negative scheduling evidence so an ordinary snapshot and
    // graceful teardown do not each perform another complete namespace scan
    // merely to rediscover the same impossible publication. A later complete
    // scan replaces the observation, while any payload mutation invalidates it.
    bool publication_capacity_observation_known = false;
    bool publication_capacity_available = false;
};

// Process-local fail-closed evidence for one payload whose current bytes were
// observed to disagree with its immutable digest name. Unlike the durable
// scrub record, this witness survives only for the lifetime of the owner/cache;
// unlike either verification cache, it can never grant payload authority. The
// exact digest remains blocked until a complete leased scan hashes current
// bytes successfully or proves that the digest name is absent.
struct ProcessIntegrityFaultObservation final {
    std::array<char, kSha256HexCharacters> expected_content_sha256{};
    std::array<char, kSha256HexCharacters> observed_content_sha256{};

    [[nodiscard]] std::string_view expected_digest() const noexcept {
        return {expected_content_sha256.data(),
                expected_content_sha256.size()};
    }

    [[nodiscard]] std::string_view observed_digest() const noexcept {
        return {observed_content_sha256.data(),
                observed_content_sha256.size()};
    }
};

static_assert(std::is_trivially_copyable_v<ProcessIntegrityFaultObservation>);
static_assert(noexcept(
    std::declval<std::optional<ProcessIntegrityFaultObservation>&>() =
        std::declval<const ProcessIntegrityFaultObservation&>()));

// Same-process proof for one exact durable Prepared/Progress record. It is
// installed either when this owner publishes and re-observes the record or when
// this owner completes a current-byte scan while that exact record and file
// observation are frozen by the shared lease. A fresh process begins without
// this witness and must hash the active payload before it may trust any
// metadata-only checkpoint. The fixed-width form is deliberately allocation-
// free; exact scrub-state-file metadata prevents another process's replacement
// from borrowing this owner's acceleration.
struct ProcessScrubActiveObservation final {
    std::array<char, kSha256HexCharacters> active_content_sha256{};
    std::uint64_t state_generation = 0U;
    SyncReplicaFilePayloadScrubStateDisposition disposition =
        SyncReplicaFilePayloadScrubStateDisposition::Prepared;
    SyncPosixRegularFileSnapshotMetadata active_metadata;
    std::uint64_t active_offset_bytes = 0U;
    ResumableSha256Checkpoint active_hash;
    SyncPosixRegularFileSnapshotMetadata scrub_state_metadata;
    // True only when this process completed a full current-byte proof for the
    // exact active state/file observation. Partial scrub publication never
    // sets it. Exact subsequent scans may carry it forward while both the
    // process verification generation and durable state observation remain
    // unchanged.
    bool active_current_bytes_verified = false;

    [[nodiscard]] std::string_view active_digest() const noexcept {
        return {active_content_sha256.data(),
                active_content_sha256.size()};
    }
};

static_assert(std::is_trivially_copyable_v<ProcessScrubActiveObservation>);
static_assert(noexcept(
    std::declval<std::optional<ProcessScrubActiveObservation>&>() =
        std::declval<const ProcessScrubActiveObservation&>()));

[[nodiscard]] bool copy_exact_lowercase_sha256_hex(
    std::string_view source,
    std::array<char, kSha256HexCharacters>& destination) noexcept {
    if (source.size() != destination.size()) return false;
    for (const char value : source) {
        if (!((value >= '0' && value <= '9') ||
              (value >= 'a' && value <= 'f'))) {
            return false;
        }
    }
    std::memcpy(destination.data(), source.data(), destination.size());
    return true;
}

// Allocation-free process projection of one complete quarantine observation.
// The store never retains more than sixteen entries, so this fixed form can be
// prepared before a namespace mutation and published after its final lease
// cutpoint without an allocation failure reopening a stale status window.
struct ProcessQuarantineInventoryEntry final {
    std::array<char, kSha256HexCharacters> expected_content_sha256{};
    std::array<char, kSha256HexCharacters> observed_content_sha256{};
    std::uint64_t size_bytes = 0U;

    [[nodiscard]] std::string_view expected_digest() const noexcept {
        return {expected_content_sha256.data(),
                expected_content_sha256.size()};
    }

    [[nodiscard]] std::string_view observed_digest() const noexcept {
        return {observed_content_sha256.data(),
                observed_content_sha256.size()};
    }
};

struct ProcessQuarantineInventoryObservation final {
    std::array<ProcessQuarantineInventoryEntry,
               kSyncReplicaFilePayloadStoreMaxQuarantineEntries> entries{};
    std::uint64_t entry_count = 0U;
    std::uint64_t total_bytes = 0U;
};

static_assert(std::is_trivially_copyable_v<
              ProcessQuarantineInventoryObservation>);
static_assert(noexcept(
    std::declval<std::optional<ProcessQuarantineInventoryObservation>&>() =
        std::declval<const ProcessQuarantineInventoryObservation&>()));

void append_process_quarantine_inventory_entry_or_throw(
    ProcessQuarantineInventoryObservation& inventory,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256,
    std::uint64_t size_bytes,
    std::string_view label) {
    if (inventory.entry_count >= inventory.entries.size()) {
        throw std::length_error(
            std::string(label) + " quarantine inventory exceeds fixed budget");
    }
    if (size_bytes >
        std::numeric_limits<std::uint64_t>::max() - inventory.total_bytes) {
        throw std::overflow_error(
            std::string(label) + " quarantine inventory byte total overflows");
    }
    ProcessQuarantineInventoryEntry& entry =
        inventory.entries[static_cast<std::size_t>(inventory.entry_count)];
    if (!copy_exact_lowercase_sha256_hex(
            expected_content_sha256, entry.expected_content_sha256) ||
        !copy_exact_lowercase_sha256_hex(
            observed_content_sha256, entry.observed_content_sha256) ||
        expected_content_sha256 == observed_content_sha256) {
        throw std::logic_error(
            std::string(label) + " quarantine inventory digest is not exact");
    }
    entry.size_bytes = size_bytes;
    ++inventory.entry_count;
    inventory.total_bytes += size_bytes;
}

void sort_process_quarantine_inventory(
    ProcessQuarantineInventoryObservation& inventory) noexcept {
    auto begin = inventory.entries.begin();
    auto end = begin + static_cast<std::ptrdiff_t>(inventory.entry_count);
    std::sort(begin, end, [](const auto& left, const auto& right) noexcept {
        if (left.expected_digest() != right.expected_digest()) {
            return left.expected_digest() < right.expected_digest();
        }
        return left.observed_digest() < right.observed_digest();
    });
}

[[nodiscard]] ProcessQuarantineInventoryObservation
make_process_quarantine_inventory_or_throw(
    const std::vector<QuarantineEntry>& entries,
    std::uint64_t expected_total_bytes,
    std::string_view label) {
    ProcessQuarantineInventoryObservation inventory;
    for (const QuarantineEntry& entry : entries) {
        append_process_quarantine_inventory_entry_or_throw(
            inventory, entry.expected_content_sha256,
            entry.observed_content_sha256, entry.size_bytes, label);
    }
    if (inventory.total_bytes != expected_total_bytes) {
        throw std::logic_error(
            std::string(label) + " quarantine inventory byte total drifted");
    }
    sort_process_quarantine_inventory(inventory);
    return inventory;
}

[[nodiscard]] bool erase_process_quarantine_inventory_entry(
    ProcessQuarantineInventoryObservation& inventory,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256) noexcept {
    std::uint64_t destination = 0U;
    bool erased = false;
    for (std::uint64_t source = 0U; source < inventory.entry_count; ++source) {
        const ProcessQuarantineInventoryEntry& candidate =
            inventory.entries[static_cast<std::size_t>(source)];
        if (!erased && candidate.expected_digest() == expected_content_sha256 &&
            candidate.observed_digest() == observed_content_sha256) {
            inventory.total_bytes -= candidate.size_bytes;
            erased = true;
            continue;
        }
        if (destination != source) {
            inventory.entries[static_cast<std::size_t>(destination)] =
                candidate;
        }
        ++destination;
    }
    if (erased) {
        inventory.entry_count = destination;
        inventory.entries[static_cast<std::size_t>(destination)] = {};
    }
    return erased;
}

struct PayloadVerificationCache final {
    std::shared_ptr<const PayloadVerificationGeneration> generation;
    PayloadVerificationCheckpointState checkpoint;
    // Process-local scheduling acceleration for bounded negative discovery.
    // This advances only after the exact retained owner has proved a new
    // digest-named payload visible (or conservatively reconciled a failure that
    // may have crossed that publication cutpoint). It is deliberately not a
    // namespace generation: removal, corruption, and unsupported external
    // mutation are outside its authority, and consumers must re-open/re-prove
    // every selected digest through ordinary targeted access.
    std::uint64_t payload_availability_generation = 0U;
    bool payload_availability_generation_exhausted = false;
    // A mismatch revokes every snapshot issued under an older epoch. The epoch
    // is never reset when current good bytes or absence clear the active fault:
    // repair may authorize a newly scanned snapshot, but must not resurrect an
    // older point-in-time capability that was live when corruption was found.
    std::uint64_t integrity_fault_epoch = 0U;
    bool integrity_fault_epoch_exhausted = false;
    std::optional<ProcessIntegrityFaultObservation> integrity_fault;
    std::optional<ProcessIntegrityFaultObservation>
        most_recent_integrity_fault;
    std::optional<ProcessScrubActiveObservation> scrub_active;
    // Last complete quarantine namespace observation proved by this exact
    // process owner. It grants no filesystem or content authority; it only
    // makes bounded retained diagnostic images discoverable through status.
    std::optional<ProcessQuarantineInventoryObservation>
        quarantine_inventory;
    std::chrono::steady_clock::time_point quarantine_inventory_observed_at =
        std::chrono::steady_clock::time_point::min();
};

void publish_process_quarantine_inventory(
    PayloadVerificationCache& cache,
    const ProcessQuarantineInventoryObservation& inventory) noexcept {
    cache.quarantine_inventory = inventory;
    cache.quarantine_inventory_observed_at =
        std::chrono::steady_clock::now();
}

void forget_process_quarantine_inventory(
    PayloadVerificationCache& cache) noexcept {
    cache.quarantine_inventory.reset();
    cache.quarantine_inventory_observed_at =
        std::chrono::steady_clock::time_point::min();
}

[[nodiscard]] std::uint64_t monotonic_age_milliseconds(
    std::chrono::steady_clock::time_point now,
    std::chrono::steady_clock::time_point observed) noexcept {
    if (now < observed) return 0U;
    const auto age = std::chrono::duration_cast<std::chrono::milliseconds>(
        now - observed);
    return age.count() <= 0
        ? std::uint64_t{0U}
        : static_cast<std::uint64_t>(age.count());
}

[[nodiscard]] bool scrub_state_is_active(
    const SyncReplicaFilePayloadScrubState& state) noexcept {
    return state.disposition ==
               SyncReplicaFilePayloadScrubStateDisposition::Prepared ||
           state.disposition ==
               SyncReplicaFilePayloadScrubStateDisposition::Progress;
}

[[nodiscard]] bool process_scrub_active_observation_matches_state(
    const ProcessScrubActiveObservation& observation,
    const SyncReplicaFilePayloadScrubState& state,
    const SyncPosixRegularFileSnapshotMetadata& state_metadata) noexcept {
    return scrub_state_is_active(state) &&
           observation.active_digest() == state.active_content_sha256 &&
           observation.state_generation == state.generation &&
           observation.disposition == state.disposition &&
           observation.active_metadata == state.active_metadata &&
           observation.active_offset_bytes == state.active_offset_bytes &&
           observation.active_hash == state.active_hash &&
           observation.scrub_state_metadata == state_metadata;
}

[[nodiscard]] bool retain_process_scrub_active_observation(
    PayloadVerificationCache& cache,
    const SyncReplicaFilePayloadScrubState& state,
    const SyncPosixRegularFileSnapshotMetadata& state_metadata,
    bool active_current_bytes_verified) noexcept {
    if (!scrub_state_is_active(state)) {
        cache.scrub_active.reset();
        return false;
    }
    ProcessScrubActiveObservation observation;
    if (!copy_exact_lowercase_sha256_hex(
            state.active_content_sha256,
            observation.active_content_sha256)) {
        cache.scrub_active.reset();
        return false;
    }
    observation.state_generation = state.generation;
    observation.disposition = state.disposition;
    observation.active_metadata = state.active_metadata;
    observation.active_offset_bytes = state.active_offset_bytes;
    observation.active_hash = state.active_hash;
    observation.scrub_state_metadata = state_metadata;
    observation.active_current_bytes_verified =
        active_current_bytes_verified ||
        (cache.scrub_active.has_value() &&
         cache.scrub_active->active_current_bytes_verified &&
         process_scrub_active_observation_matches_state(
             *cache.scrub_active, state, state_metadata));
    cache.scrub_active = observation;
    return true;
}

[[nodiscard]] bool process_scrub_active_observation_matches(
    const PayloadVerificationCache& cache,
    const SyncReplicaFilePayloadScrubState& state,
    const SyncPosixRegularFileSnapshotMetadata& state_metadata) noexcept {
    if (!scrub_state_is_active(state) || !cache.scrub_active.has_value()) {
        return false;
    }
    return process_scrub_active_observation_matches_state(
        *cache.scrub_active, state, state_metadata);
}

void note_process_scrub_state_observation(
    PayloadVerificationCache& cache,
    const SyncReplicaFilePayloadScrubState* state,
    const SyncPosixRegularFileSnapshotMetadata* state_metadata,
    bool active_current_bytes_verified) noexcept {
    if (state == nullptr || state_metadata == nullptr ||
        !retain_process_scrub_active_observation(
            cache, *state, *state_metadata,
            active_current_bytes_verified)) {
        cache.scrub_active.reset();
    }
}

[[nodiscard]] bool retain_process_integrity_fault(
    PayloadVerificationCache& cache,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256) noexcept {
    if (cache.integrity_fault.has_value() &&
        cache.integrity_fault->expected_digest() != expected_content_sha256) {
        // Preserve the oldest unresolved target. A complete scan cannot return
        // while it remains corrupt, so no newer snapshot can inherit authority
        // from this failed observation.
        return false;
    }

    ProcessIntegrityFaultObservation observation;
    const bool expected_exact = copy_exact_lowercase_sha256_hex(
        expected_content_sha256, observation.expected_content_sha256);
    const bool observed_exact = copy_exact_lowercase_sha256_hex(
        observed_content_sha256, observation.observed_content_sha256);
    if (!expected_exact || !observed_exact) {
        // Both values originate from a validated digest basename and the
        // canonical SHA-256 encoder. A violated internal invariant must remain
        // fail-closed without attempting diagnostic heap allocation.
        cache.integrity_fault_epoch_exhausted = true;
        if (!expected_exact) {
            observation.expected_content_sha256.fill('?');
        }
        if (!observed_exact) {
            observation.observed_content_sha256.fill('?');
        }
    }

    if (!cache.integrity_fault.has_value()) {
        if (cache.integrity_fault_epoch ==
            std::numeric_limits<std::uint64_t>::max()) {
            // Impossibly many independent corruption epochs must still fail
            // closed rather than wrapping and accidentally matching an ancient
            // snapshot generation.
            cache.integrity_fault_epoch_exhausted = true;
        } else {
            ++cache.integrity_fault_epoch;
        }
    }

    cache.integrity_fault = observation;
    cache.most_recent_integrity_fault = observation;
    return true;
}

void reject_process_integrity_fault_for_payload_or_throw(
    const std::shared_ptr<PayloadVerificationCache>& cache,
    std::string_view content_sha256,
    std::string_view label,
    std::string_view authority_kind) {
    if (!cache || !cache->integrity_fault.has_value() ||
        cache->integrity_fault->expected_digest() != content_sha256) {
        return;
    }
    const ProcessIntegrityFaultObservation& fault = *cache->integrity_fault;
    throw SyncReplicaFilePayloadStoreIntegrityError(
        std::string(fault.expected_digest()),
        std::string(fault.observed_digest()), false,
        std::string(label) + " rejects " + std::string(authority_kind) +
            " access to a process-observed corrupt payload " +
            std::string(fault.expected_digest()) +
            " until a complete leased scan proves current good bytes or "
            "absence");
}

void reject_revoked_snapshot_authority_or_throw(
    const std::shared_ptr<PayloadVerificationCache>& cache,
    std::uint64_t issued_integrity_fault_epoch,
    std::string_view label) {
    if (!cache) return;
    const bool revoked = cache->integrity_fault_epoch_exhausted ||
                         cache->integrity_fault.has_value() ||
                         cache->integrity_fault_epoch !=
                             issued_integrity_fault_epoch;
    if (!revoked) return;

    const ProcessIntegrityFaultObservation* fault =
        cache->integrity_fault.has_value()
            ? &*cache->integrity_fault
            : (cache->most_recent_integrity_fault.has_value()
                   ? &*cache->most_recent_integrity_fault
                   : nullptr);
    if (fault == nullptr) {
        throw std::logic_error(
            std::string(label) +
            " payload snapshot integrity epoch changed without retained "
            "diagnostic evidence");
    }
    throw SyncReplicaFilePayloadStoreIntegrityError(
        std::string(fault->expected_digest()),
        std::string(fault->observed_digest()), false,
        std::string(label) +
            " rejects a payload snapshot revoked by process-observed "
            "corruption of " + std::string(fault->expected_digest()) +
            "; a newly completed leased scan must issue replacement "
            "snapshot authority");
}

[[nodiscard]] std::uint64_t saturating_add_u64(
    std::uint64_t left,
    std::uint64_t right) noexcept {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return left + right;
}

void note_verification_checkpoint_observation(
    PayloadVerificationCache& cache,
    const ScannedPayloadIndex& scanned,
    std::optional<bool> publication_capacity_available) noexcept {
    PayloadVerificationCheckpointState& state = cache.checkpoint;
    state.publication_capacity_observation_known =
        publication_capacity_available.has_value();
    state.publication_capacity_available =
        publication_capacity_available.value_or(false);

    // Absence is visible even when an exact process-local generation avoided
    // reading payload-checkpoint bytes. Preserve accumulated additions but make
    // the next eligible checkpoint recreate the missing file.
    if (!scanned.verification_index_present) {
        state.observation_known = true;
        state.force_checkpoint = true;
        state.durable_entry_count = 0U;
        state.durable_indexed_bytes = 0U;
        return;
    }

    if (!scanned.verification_index_contents_requested) {
        // A matched process-local generation deliberately avoids rereading the
        // potentially multi-megabyte checkpoint. Its prior scheduling state is
        // still exact for cooperative mutations. Unknown state is treated
        // conservatively so graceful teardown will establish a baseline.
        if (!state.observation_known) {
            state.observation_known = true;
            state.force_checkpoint = true;
            return;
        }

        // The process-local generation can remain useful after an external
        // metadata-only rewrite, replacement, insertion, or removal that leaves
        // the digest namespace valid. Any cache miss paid for a complete byte
        // proof, while count/byte drift proves that the last observed durable
        // checkpoint cannot describe the current namespace. Retain that exact
        // evidence so the successful snapshot refreshes restart acceleration
        // now instead of forcing the next process to repeat avoidable work.
        if (scanned.scan_hashed_entry_count != 0U ||
            state.durable_entry_count !=
                static_cast<std::uint64_t>(scanned.entries.size()) ||
            state.durable_indexed_bytes != scanned.indexed_bytes) {
            state.force_checkpoint = true;
        }
        return;
    }

    state.observation_known = true;
    if (scanned.verification_index_current) {
        state.force_checkpoint = false;
        state.durable_entry_count =
            static_cast<std::uint64_t>(scanned.entries.size());
        state.durable_indexed_bytes = scanned.indexed_bytes;
        state.pending_added_entries = 0U;
        state.pending_added_bytes = 0U;
        return;
    }

    // A malformed, identity-mismatched, or metadata-stale record cannot grant
    // reuse. Keep any parsed usable baseline only for geometric scheduling and
    // force one replacement after the complete byte proof succeeds.
    state.force_checkpoint = true;
    if (scanned.verification_index_usable) {
        state.durable_entry_count = scanned.verification_index_entry_count;
        state.durable_indexed_bytes =
            scanned.verification_index_indexed_bytes;
    } else {
        state.durable_entry_count = 0U;
        state.durable_indexed_bytes = 0U;
    }
}

void note_verification_checkpoint_payload_addition(
    PayloadVerificationCache& cache,
    std::uint64_t payload_bytes) noexcept {
    if (!cache.payload_availability_generation_exhausted) {
        if (cache.payload_availability_generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            cache.payload_availability_generation_exhausted = true;
        } else {
            ++cache.payload_availability_generation;
        }
    }
    PayloadVerificationCheckpointState& state = cache.checkpoint;
    state.observation_known = true;
    state.pending_added_entries = saturating_add_u64(
        state.pending_added_entries, 1U);
    state.pending_added_bytes = saturating_add_u64(
        state.pending_added_bytes, payload_bytes);
    // The encoded record grew and the surrounding mutation may also have
    // reconciled transient files. Only a new exact current-index preflight may
    // decide whether publication now fits.
    state.publication_capacity_observation_known = false;
    state.publication_capacity_available = false;
}

void note_verification_checkpoint_published(
    PayloadVerificationCache& cache,
    const ScannedPayloadIndex& scanned) noexcept {
    PayloadVerificationCheckpointState& state = cache.checkpoint;
    state.observation_known = true;
    state.force_checkpoint = false;
    state.durable_entry_count =
        static_cast<std::uint64_t>(scanned.entries.size());
    state.durable_indexed_bytes = scanned.indexed_bytes;
    state.pending_added_entries = 0U;
    state.pending_added_bytes = 0U;
    state.publication_capacity_observation_known = true;
    state.publication_capacity_available = true;
}

void note_verification_checkpoint_capacity_deferred(
    PayloadVerificationCache& cache) noexcept {
    PayloadVerificationCheckpointState& state = cache.checkpoint;
    state.publication_capacity_observation_known = true;
    state.publication_capacity_available = false;
}

[[nodiscard]] bool verification_checkpoint_due(
    const PayloadVerificationCache& cache,
    bool graceful_final_checkpoint) noexcept {
    const PayloadVerificationCheckpointState& state = cache.checkpoint;
    if (state.force_checkpoint) return true;
    if (state.pending_added_entries == 0U &&
        state.pending_added_bytes == 0U) {
        return false;
    }
    if (graceful_final_checkpoint) return true;

    const std::uint64_t entry_threshold = std::clamp(
        state.durable_entry_count,
        kVerificationCheckpointMinimumAddedEntries,
        kVerificationCheckpointMaximumAddedEntries);
    const std::uint64_t byte_threshold = std::clamp(
        state.durable_indexed_bytes,
        kVerificationCheckpointMinimumAddedBytes,
        kVerificationCheckpointMaximumAddedBytes);
    return state.pending_added_entries >= entry_threshold ||
           state.pending_added_bytes >= byte_threshold;
}

[[nodiscard]] bool verification_checkpoint_deferred_by_known_capacity(
    const PayloadVerificationCache& cache,
    bool graceful_final_checkpoint) noexcept {
    const PayloadVerificationCheckpointState& state = cache.checkpoint;
    return verification_checkpoint_due(cache, graceful_final_checkpoint) &&
           state.publication_capacity_observation_known &&
           !state.publication_capacity_available;
}

[[nodiscard]] bool verification_checkpoint_publication_worth_attempting(
    const PayloadVerificationCache& cache,
    bool graceful_final_checkpoint) noexcept {
    // A complete scan must clear observed corruption before either the
    // graceful-close path or a completed-payload fast path may publish restart
    // acceleration. Keeping the stale generation in memory is harmless because
    // the same witness forces current-byte reproof; writing it durably would be
    // wasteful and could make a later cold process repeat avoidable work.
    return !cache.integrity_fault.has_value() &&
           verification_checkpoint_due(cache, graceful_final_checkpoint) &&
           !verification_checkpoint_deferred_by_known_capacity(
               cache, graceful_final_checkpoint);
}

[[nodiscard]] const PayloadIndexEntry* find_entry(
    const std::vector<PayloadIndexEntry>& entries,
    std::string_view digest) noexcept;

enum class StoreObservationDurability : std::uint8_t {
    Reconcile = 1U,
    ObserveOnly = 2U,
};

enum class PayloadVerificationReusePolicy : std::uint8_t {
    AllowAcceleration = 1U,
    RequireCurrentBytes = 2U,
};

[[nodiscard]] bool synchronizes_store_observation(
    StoreObservationDurability durability) noexcept {
    return durability == StoreObservationDurability::Reconcile;
}

class StoreLease final {
public:
    StoreLease(
        OwnedFd root_descriptor,
        OwnedFd identity_descriptor,
        struct stat identity_status,
        SyncDirectoryAttestation root_attestation,
        std::string identity_basename,
        std::string expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode mode,
        StoreObservationDurability durability) noexcept
        : root_descriptor_(std::move(root_descriptor)),
          identity_descriptor_(std::move(identity_descriptor)),
          identity_status_(identity_status),
          root_attestation_(root_attestation),
          identity_basename_(std::move(identity_basename)),
          expected_identity_(std::move(expected_identity)),
          mode_(mode),
          durability_(durability) {}
    StoreLease(const StoreLease&) = delete;
    StoreLease& operator=(const StoreLease&) = delete;
    StoreLease(StoreLease&&) noexcept = default;
    StoreLease& operator=(StoreLease&&) noexcept = default;
    ~StoreLease() noexcept = default;

    void verify_or_throw(
        const SyncDirectoryAuthority& root_authority,
        const std::string& label) const;

    // Atomically move the exact locked identity inode to a basename that raises
    // the minimum reader generation. The flock remains attached to the open
    // file description; the method accepts only the rename-induced ctime
    // transition, synchronizes the directory, and then rebinds this lease to
    // the new pathname observation.
    void rebind_identity_basename_after_atomic_rename_or_throw(
        const SyncDirectoryAuthority& root_authority,
        std::string new_identity_basename,
        const std::string& label);

    [[nodiscard]] SyncReplicaFilePayloadStoreLeaseMode mode() const noexcept {
        return mode_;
    }

    [[nodiscard]] const struct stat& identity_status() const noexcept {
        return identity_status_;
    }

private:
    // flock(2) locks are released with the final close of the independently
    // opened identity file description. Retaining the exact root descriptor,
    // identity inode, and bytes lets every protected scan re-prove that the
    // pathname still names the locked anchor rather than an identical
    // replacement inode. Both descriptors remain CLOEXEC through the shared
    // resolvers.
    OwnedFd root_descriptor_;
    OwnedFd identity_descriptor_;
    struct stat identity_status_ {};
    SyncDirectoryAttestation root_attestation_;
    std::string identity_basename_;
    std::string expected_identity_;
    SyncReplicaFilePayloadStoreLeaseMode mode_ =
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation;
    StoreObservationDurability durability_ =
        StoreObservationDurability::Reconcile;
};

struct VerifiedStoreIdentityFile final {
    OwnedFd descriptor;
    struct stat status {};
};

[[nodiscard]] std::string error_text(int error_number) {
    return std::error_code(error_number, std::generic_category()).message();
}

void require_no_competing_store_identity_names_or_throw(
    int directory_descriptor,
    std::string_view selected_identity_basename,
    const std::string& label) {
    if (directory_descriptor < 0 ||
        !payload_store_identity_basename_is_lease_capable(
            selected_identity_basename)) {
        throw std::logic_error(
            label + " payload-store identity-name proof is misconfigured");
    }

    // A targeted payload access intentionally does not enumerate the payload
    // namespace. It must nevertheless reject split lock authority. Probe the
    // complete fixed set of reserved identity names, including unsupported v1,
    // every time the selected marker is opened or re-proved. Any other entry,
    // including a symlink or malformed regular file, is incompatible by name
    // alone and therefore cannot be ignored merely because the selected marker
    // remains exact.
    for (const std::string_view candidate : kKnownStoreIdentityBasenames) {
        if (candidate == selected_identity_basename) continue;
        struct stat status {};
        int result;
        do {
            result = ::fstatat(
                directory_descriptor, candidate.data(),
                &status, AT_SYMLINK_NOFOLLOW);
        } while (result != 0 && errno == EINTR);
        if (result == 0) {
            throw std::runtime_error(
                label +
                " refuses coexisting incompatible payload-store identity "
                "marker: " +
                std::string(candidate));
        }
        if (errno != ENOENT) {
            const int error = errno;
            throw std::runtime_error(
                label + " competing identity-name proof failed for " +
                std::string(candidate) + ": " + error_text(error));
        }
    }
}

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(label + " size exceeds uint64 range");
        }
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::size_t u64_to_size_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value > static_cast<std::uint64_t>(
                    std::numeric_limits<std::size_t>::max())) {
        throw std::overflow_error(label + " exceeds addressable size");
    }
    return static_cast<std::size_t>(value);
}

[[nodiscard]] std::uint64_t checked_add_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(label + " exceeds uint64 range");
    }
    return left + right;
}

struct ParsedStagedRangeBasename final {
    std::string content_sha256;
    std::uint64_t offset_bytes = 0U;
    std::string chunk_sha256;
};

struct ParsedStagedPrefixBasename final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t committed_prefix_bytes = 0U;
};

struct ParsedQuarantineBasename final {
    std::string expected_content_sha256;
    std::string observed_content_sha256;
};

[[nodiscard]] std::optional<std::uint64_t> parse_canonical_u64(
    std::string_view text) {
    if (text.empty()) return std::nullopt;
    std::uint64_t value = 0U;
    const auto parsed = std::from_chars(
        text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != text.data() + text.size() ||
        std::to_string(value) != text) {
        return std::nullopt;
    }
    return value;
}

[[nodiscard]] std::optional<ParsedStagedRangeBasename>
parse_staged_range_basename(std::string_view basename) {
    if (!basename.starts_with(kStagedRangeBasenamePrefix)) {
        return std::nullopt;
    }
    basename.remove_prefix(kStagedRangeBasenamePrefix.size());
    if (basename.size() < 64U + 1U + 1U + 1U + 64U) {
        return std::nullopt;
    }
    const std::string_view content = basename.substr(0U, 64U);
    if (!is_lowercase_sha256_hex(content) || basename[64U] != '-') {
        return std::nullopt;
    }
    const std::size_t chunk_separator = basename.find('-', 65U);
    if (chunk_separator == std::string_view::npos ||
        chunk_separator == 65U) {
        return std::nullopt;
    }
    const std::string_view offset_text =
        basename.substr(65U, chunk_separator - 65U);
    const std::string_view chunk = basename.substr(chunk_separator + 1U);
    if (!is_lowercase_sha256_hex(chunk)) return std::nullopt;

    const auto offset = parse_canonical_u64(offset_text);
    if (!offset.has_value()) return std::nullopt;
    return ParsedStagedRangeBasename{
        std::string(content), *offset, std::string(chunk)};
}

[[nodiscard]] std::optional<ParsedStagedPrefixBasename>
parse_staged_prefix_basename(std::string_view basename) {
    if (!basename.starts_with(kStagedPrefixBasenamePrefix)) {
        return std::nullopt;
    }
    basename.remove_prefix(kStagedPrefixBasenamePrefix.size());
    if (basename.size() < 64U + 1U + 1U + 1U + 1U) {
        return std::nullopt;
    }
    const std::string_view content = basename.substr(0U, 64U);
    if (!is_lowercase_sha256_hex(content) || basename[64U] != '-') {
        return std::nullopt;
    }
    const std::size_t committed_separator = basename.find('-', 65U);
    if (committed_separator == std::string_view::npos ||
        committed_separator == 65U ||
        committed_separator + 1U >= basename.size()) {
        return std::nullopt;
    }
    const auto total = parse_canonical_u64(
        basename.substr(65U, committed_separator - 65U));
    const auto committed = parse_canonical_u64(
        basename.substr(committed_separator + 1U));
    if (!total.has_value() || !committed.has_value() || *total == 0U ||
        *committed > *total) {
        return std::nullopt;
    }
    return ParsedStagedPrefixBasename{
        std::string(content), *total, *committed};
}

[[nodiscard]] std::optional<std::string>
parse_terminal_verification_basename(std::string_view basename) {
    if (!basename.starts_with(
            kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix)) {
        return std::nullopt;
    }
    basename.remove_prefix(
        kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix.size());
    if (!is_lowercase_sha256_hex(basename)) return std::nullopt;
    return std::string(basename);
}

[[nodiscard]] std::optional<ParsedQuarantineBasename>
parse_quarantine_basename(std::string_view basename) {
    if (!basename.starts_with(kQuarantineBasenamePrefix)) {
        return std::nullopt;
    }
    basename.remove_prefix(kQuarantineBasenamePrefix.size());
    if (basename.size() != 64U + 1U + 64U || basename[64U] != '-') {
        return std::nullopt;
    }
    const std::string_view expected = basename.substr(0U, 64U);
    const std::string_view observed = basename.substr(65U, 64U);
    if (!is_lowercase_sha256_hex(expected) ||
        !is_lowercase_sha256_hex(observed) || expected == observed) {
        return std::nullopt;
    }
    return ParsedQuarantineBasename{
        std::string(expected), std::string(observed)};
}

[[nodiscard]] std::string quarantine_basename_or_throw(
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256) {
    if (!is_lowercase_sha256_hex(expected_content_sha256) ||
        !is_lowercase_sha256_hex(observed_content_sha256) ||
        expected_content_sha256 == observed_content_sha256) {
        throw std::invalid_argument(
            "sync replica payload quarantine digest pair is invalid");
    }
    std::string out;
    out.reserve(kQuarantineBasenamePrefix.size() + 64U + 1U + 64U);
    out.append(kQuarantineBasenamePrefix);
    out.append(expected_content_sha256);
    out.push_back('-');
    out.append(observed_content_sha256);
    return out;
}

[[nodiscard]] std::uint64_t maximum_quarantine_bytes(
    const SyncReplicaFilePayloadStoreLimits& limits) noexcept {
    const std::uint64_t entry_derived_limit =
        limits.max_payload_bytes >
                kMaximumPersistentInteger /
                    kSyncReplicaFilePayloadStoreMaxQuarantineEntries
            ? kMaximumPersistentInteger
            : limits.max_payload_bytes *
                  kSyncReplicaFilePayloadStoreMaxQuarantineEntries;
    return std::min(limits.max_indexed_bytes, entry_derived_limit);
}

[[nodiscard]] bool assembly_basename_is_exact(
    std::string_view basename) noexcept {
    if (!basename.starts_with(kAssemblyBasenamePrefix)) return false;
    basename.remove_prefix(kAssemblyBasenamePrefix.size());
    return is_lowercase_sha256_hex(basename);
}

[[nodiscard]] std::string staged_range_basename_or_throw(
    std::string_view content_sha256,
    std::uint64_t offset_bytes,
    std::string_view chunk_sha256) {
    if (!is_lowercase_sha256_hex(content_sha256) ||
        !is_lowercase_sha256_hex(chunk_sha256)) {
        throw std::invalid_argument(
            "sync replica staged payload range digest is invalid");
    }
    std::string out;
    out.reserve(
        kStagedRangeBasenamePrefix.size() + 64U + 1U + 20U + 1U + 64U);
    out.append(kStagedRangeBasenamePrefix);
    out.append(content_sha256);
    out.push_back('-');
    out.append(std::to_string(offset_bytes));
    out.push_back('-');
    out.append(chunk_sha256);
    return out;
}

[[nodiscard]] std::string staged_prefix_basename_or_throw(
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    std::uint64_t committed_prefix_bytes) {
    if (!is_lowercase_sha256_hex(content_sha256) || total_size_bytes == 0U ||
        committed_prefix_bytes > total_size_bytes) {
        throw std::invalid_argument(
            "sync replica staged payload prefix identity is invalid");
    }
    std::string out;
    out.reserve(
        kStagedPrefixBasenamePrefix.size() + 64U + 1U + 20U + 1U + 20U);
    out.append(kStagedPrefixBasenamePrefix);
    out.append(content_sha256);
    out.push_back('-');
    out.append(std::to_string(total_size_bytes));
    out.push_back('-');
    out.append(std::to_string(committed_prefix_bytes));
    return out;
}

[[nodiscard]] std::string terminal_verification_basename_or_throw(
    std::string_view content_sha256) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            "sync replica terminal payload verification digest is invalid");
    }
    std::string out(
        kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix);
    out.append(content_sha256);
    return out;
}

[[nodiscard]] std::string assembly_basename_or_throw(
    std::string_view content_sha256) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            "sync replica payload assembly digest is invalid");
    }
    std::string out(kAssemblyBasenamePrefix);
    out.append(content_sha256);
    return out;
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& bytes) noexcept {
    return {reinterpret_cast<const unsigned char*>(bytes.data()), bytes.size()};
}

[[nodiscard]] std::string standalone_store_identity_payload(
    std::string_view folder_id) {
    std::string payload;
    payload.reserve(
        kStandaloneStoreIdentityDomainV2.size() + folder_id.size() +
        kStoreLeaseProtocol.size() + 3U);
    payload.append(kStandaloneStoreIdentityDomainV2);
    payload.push_back('\n');
    payload.append(folder_id);
    payload.push_back('\n');
    payload.append(kStoreLeaseProtocol);
    payload.push_back('\n');
    return payload;
}

void append_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    std::array<char, 8U> bytes{};
    for (std::size_t index = bytes.size(); index != 0U; --index) {
        bytes[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(std::string_view(bytes.data(), bytes.size()));
}

void append_string(Sha256DigestBuilder& digest, std::string_view value) {
    if (value.size() > std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "durable payload store digest field exceeds uint64 range");
    }
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

enum class PayloadStoreLiveCapabilityKind : std::uint8_t {
    Snapshot = 1U,
    OpenedPayload = 2U,
    TargetedAccess = 3U,
    MutationBatch = 4U,
};

struct PayloadStoreLiveCapabilityRecord final {
    PayloadStoreLiveCapabilityKind kind =
        PayloadStoreLiveCapabilityKind::Snapshot;
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;
};

[[nodiscard]] std::string
payload_store_live_capability_process_store_scope_digest_or_throw(
    std::string_view root_attestation_digest,
    std::string_view identity_basename,
    std::string_view expected_identity,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "payload-store process-store-scope label is empty");
    }
    if (!is_lowercase_sha256_hex(root_attestation_digest)) {
        throw std::invalid_argument(
            label + " root-attestation digest is invalid");
    }
    if (identity_basename.empty() || expected_identity.empty()) {
        throw std::invalid_argument(
            label + " immutable identity binding is incomplete");
    }

    Sha256DigestBuilder digest;
    append_string(digest, kLiveCapabilityProcessStoreScopeDomain);
    append_string(digest, root_attestation_digest);
    append_string(digest, identity_basename);
    append_string(digest, expected_identity);
    return digest.finish_hex();
}

[[nodiscard]] std::string
new_payload_store_live_capability_process_store_scope_incarnation_or_throw() {
    // This is one process/store-scope incarnation discriminator for a
    // non-authoritative retention cutpoint, not a persisted secret. Mix
    // independent OS entropy with process/time/counter inputs so a stale mark
    // cannot silently survive release of the final owner and later scope
    // reconstruction even on a platform with a weak random_device backend.
    static std::atomic<std::uint64_t> process_counter{0U};
    std::uint64_t counter = process_counter.load(std::memory_order_relaxed);
    for (;;) {
        if (counter == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                "payload-store live-capability process counter is exhausted");
        }
        if (process_counter.compare_exchange_weak(
                counter, counter + 1U,
                std::memory_order_relaxed,
                std::memory_order_relaxed)) {
            break;
        }
    }

    std::random_device random;
    Sha256DigestBuilder digest;
    append_string(digest, kLiveCapabilityProcessStoreScopeIncarnationDomain);
    append_u64(digest, static_cast<std::uint64_t>(::getpid()));
    append_u64(
        digest,
        static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count()));
    append_u64(digest, counter);
    for (std::size_t index = 0U; index < 8U; ++index) {
        append_u64(digest, static_cast<std::uint64_t>(random()));
    }
    return digest.finish_hex();
}

class PayloadStoreLiveCapabilityRegistry final {
public:
    explicit PayloadStoreLiveCapabilityRegistry(
        std::string process_store_scope_digest,
        std::uint64_t maximum_records,
        std::string label)
        : process_store_scope_digest_(
              std::move(process_store_scope_digest)),
          maximum_records_(maximum_records),
          label_(std::move(label)),
          process_store_scope_incarnation_digest_(
              new_payload_store_live_capability_process_store_scope_incarnation_or_throw()) {
        if (!is_lowercase_sha256_hex(process_store_scope_digest_)) {
            throw std::invalid_argument(
                label_ + " process-store-scope digest is invalid");
        }
        if (maximum_records_ == 0U) {
            throw std::invalid_argument(
                label_ + " live-capability record limit is zero");
        }
    }

    PayloadStoreLiveCapabilityRegistry(
        const PayloadStoreLiveCapabilityRegistry&) = delete;
    PayloadStoreLiveCapabilityRegistry& operator=(
        const PayloadStoreLiveCapabilityRegistry&) = delete;

    [[nodiscard]] std::uint64_t register_or_throw(
        PayloadStoreLiveCapabilityKind kind,
        std::string content_sha256 = {},
        std::uint64_t size_bytes = 0U) {
        switch (kind) {
            case PayloadStoreLiveCapabilityKind::Snapshot:
            case PayloadStoreLiveCapabilityKind::TargetedAccess:
            case PayloadStoreLiveCapabilityKind::MutationBatch:
                if (!content_sha256.empty() || size_bytes != 0U) {
                    throw std::invalid_argument(
                        label_ +
                        " non-payload live capability carries payload identity");
                }
                break;
            case PayloadStoreLiveCapabilityKind::OpenedPayload:
                if (!is_lowercase_sha256_hex(content_sha256)) {
                    throw std::invalid_argument(
                        label_ +
                        " opened-payload live capability digest is invalid");
                }
                break;
            default:
                throw std::invalid_argument(
                    label_ + " live capability kind is invalid");
        }

        std::lock_guard<std::mutex> lock(mutex_);
        if (records_.size() >= maximum_records_) {
            throw std::length_error(
                label_ + " live-capability record frontier is exhausted");
        }
        if (next_registration_id_ == 0U) {
            throw std::overflow_error(
                label_ + " live-capability registration IDs are exhausted");
        }
        if (activity_generation_exhausted_ ||
            activity_generation_ ==
                std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label_ + " live-capability activity generation is exhausted");
        }
        const std::uint64_t registration_id = next_registration_id_;
        if (next_registration_id_ ==
            std::numeric_limits<std::uint64_t>::max()) {
            next_registration_id_ = 0U;
        } else {
            ++next_registration_id_;
        }
        const auto [position, inserted] = records_.emplace(
            registration_id,
            PayloadStoreLiveCapabilityRecord{
                kind, std::move(content_sha256), size_bytes});
        (void)position;
        if (!inserted) {
            throw std::logic_error(
                label_ + " live-capability registration ID collided");
        }
        ++activity_generation_;
        return registration_id;
    }

    void unregister_noexcept(std::uint64_t registration_id) noexcept {
        if (registration_id == 0U) return;
        try {
            std::lock_guard<std::mutex> lock(mutex_);
            if (records_.erase(registration_id) != 1U) {
                std::terminate();
            }
            if (activity_generation_ ==
                std::numeric_limits<std::uint64_t>::max()) {
                activity_generation_exhausted_ = true;
            } else {
                ++activity_generation_;
            }
        } catch (...) {
            std::terminate();
        }
    }

    [[nodiscard]] SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
    cutpoint_excluding_snapshot_or_throw(
        std::uint64_t excluded_snapshot_registration_id,
        std::string_view label_view) const {
        const std::string label(label_view);
        if (label.empty()) {
            throw std::invalid_argument(
                "payload-store live-capability cutpoint label is empty");
        }

        std::lock_guard<std::mutex> lock(mutex_);
        if (activity_generation_exhausted_) {
            throw std::overflow_error(
                label + " live-capability activity generation is exhausted");
        }
        const auto excluded = records_.find(excluded_snapshot_registration_id);
        if (excluded == records_.end() ||
            excluded->second.kind != PayloadStoreLiveCapabilityKind::Snapshot) {
            throw std::logic_error(
                label + " excluded snapshot registration is not live");
        }

        SyncReplicaFilePayloadStoreLiveCapabilityCutpoint out;
        out.process_store_scope_digest = process_store_scope_digest_;
        out.process_store_scope_incarnation_digest = process_store_scope_incarnation_digest_;
        out.activity_generation = activity_generation_;
        if (records_.size() > 1U) {
            out.opened_payload_roots.reserve(records_.size() - 1U);
        }

        Sha256DigestBuilder digest;
        append_string(digest, kLiveCapabilitySetDigestDomain);
        append_string(digest, process_store_scope_digest_);
        append_string(digest, process_store_scope_incarnation_digest_);
        std::uint64_t retained_record_count = 0U;
        for (const auto& [registration_id, record] : records_) {
            if (registration_id == excluded_snapshot_registration_id) {
                continue;
            }
            if (retained_record_count ==
                std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error(
                    label + " live-capability record count overflows");
            }
            ++retained_record_count;
            append_u64(digest, registration_id);
            append_u64(digest, static_cast<std::uint64_t>(record.kind));
            append_string(digest, record.content_sha256);
            append_u64(digest, record.size_bytes);
            switch (record.kind) {
                case PayloadStoreLiveCapabilityKind::Snapshot:
                    ++out.snapshot_count;
                    break;
                case PayloadStoreLiveCapabilityKind::OpenedPayload:
                    ++out.opened_payload_count;
                    out.opened_payload_roots.push_back(
                        SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot{
                            record.content_sha256, record.size_bytes});
                    break;
                case PayloadStoreLiveCapabilityKind::TargetedAccess:
                    ++out.targeted_access_count;
                    break;
                case PayloadStoreLiveCapabilityKind::MutationBatch:
                    ++out.mutation_batch_count;
                    break;
            }
        }
        append_u64(digest, retained_record_count);
        append_u64(digest, out.snapshot_count);
        append_u64(digest, out.opened_payload_count);
        append_u64(digest, out.targeted_access_count);
        append_u64(digest, out.mutation_batch_count);
        out.capability_set_digest = digest.finish_hex();

        std::sort(
            out.opened_payload_roots.begin(),
            out.opened_payload_roots.end(),
            [](const SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot& left,
               const SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot& right) {
                if (left.content_sha256 != right.content_sha256) {
                    return left.content_sha256 < right.content_sha256;
                }
                return left.size_bytes < right.size_bytes;
            });
        out.opened_payload_roots.erase(
            std::unique(
                out.opened_payload_roots.begin(),
                out.opened_payload_roots.end()),
            out.opened_payload_roots.end());
        if (out.opened_payload_roots.size() >
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label + " distinct opened-payload root count overflows");
        }
        out.distinct_opened_payload_root_count =
            static_cast<std::uint64_t>(out.opened_payload_roots.size());
        for (const auto& root : out.opened_payload_roots) {
            if (root.size_bytes >
                std::numeric_limits<std::uint64_t>::max() -
                    out.distinct_opened_payload_root_bytes) {
                throw std::overflow_error(
                    label + " distinct opened-payload root bytes overflow");
            }
            out.distinct_opened_payload_root_bytes += root.size_bytes;
        }
        return out;
    }

private:
    const std::string process_store_scope_digest_;
    const std::uint64_t maximum_records_;
    const std::string label_;
    const std::string process_store_scope_incarnation_digest_;
    mutable std::mutex mutex_;
    std::uint64_t next_registration_id_ = 1U;
    std::uint64_t activity_generation_ = 0U;
    bool activity_generation_exhausted_ = false;
    std::map<std::uint64_t, PayloadStoreLiveCapabilityRecord> records_;
};

class PayloadStoreLiveCapabilityRegistryBroker final {
public:
    [[nodiscard]] static PayloadStoreLiveCapabilityRegistryBroker& instance() {
        static PayloadStoreLiveCapabilityRegistryBroker broker;
        return broker;
    }

    [[nodiscard]] std::shared_ptr<PayloadStoreLiveCapabilityRegistry>
    acquire_or_throw(
        std::string process_store_scope_digest,
        std::string_view label_view) {
        const std::string label(label_view);
        if (label.empty()) {
            throw std::invalid_argument(
                "payload-store live-capability broker label is empty");
        }
        if (!is_lowercase_sha256_hex(process_store_scope_digest)) {
            throw std::invalid_argument(
                label + " process-store-scope digest is invalid");
        }

        std::lock_guard<std::mutex> lock(mutex_);
        for (auto position = registries_.begin();
             position != registries_.end();) {
            if (position->second.expired()) {
                position = registries_.erase(position);
            } else {
                ++position;
            }
        }

        const auto existing = registries_.find(process_store_scope_digest);
        if (existing != registries_.end()) {
            if (auto retained = existing->second.lock()) {
                return retained;
            }
            registries_.erase(existing);
        }
        if (registries_.size() >=
            kMaximumProcessLiveCapabilityStoreScopes) {
            throw std::length_error(
                label + " process live-capability store-scope frontier is exhausted");
        }

        auto registry = std::make_shared<PayloadStoreLiveCapabilityRegistry>(
            process_store_scope_digest,
            kMaximumProcessLiveCapabilityRecordsPerStore,
            label + " process store scope");
        const auto [position, inserted] = registries_.emplace(
            std::move(process_store_scope_digest), registry);
        (void)position;
        if (!inserted) {
            throw std::logic_error(
                label + " process live-capability store-scope insertion collided");
        }
        return registry;
    }

private:
    PayloadStoreLiveCapabilityRegistryBroker() = default;

    std::mutex mutex_;
    std::map<
        std::string,
        std::weak_ptr<PayloadStoreLiveCapabilityRegistry>> registries_;
};

[[nodiscard]] std::shared_ptr<PayloadStoreLiveCapabilityRegistry>
acquire_payload_store_live_capability_registry_or_throw(
    std::string_view root_attestation_digest,
    std::string_view identity_basename,
    std::string_view expected_identity,
    std::string_view label) {
    return PayloadStoreLiveCapabilityRegistryBroker::instance().acquire_or_throw(
        payload_store_live_capability_process_store_scope_digest_or_throw(
            root_attestation_digest, identity_basename, expected_identity,
            label),
        label);
}

class PayloadStoreLiveCapabilityRegistration final {
public:
    PayloadStoreLiveCapabilityRegistration() noexcept = default;

    PayloadStoreLiveCapabilityRegistration(
        std::shared_ptr<PayloadStoreLiveCapabilityRegistry> registry,
        PayloadStoreLiveCapabilityKind kind,
        std::string content_sha256 = {},
        std::uint64_t size_bytes = 0U)
        : registry_(std::move(registry)) {
        if (!registry_) {
            throw std::invalid_argument(
                "payload-store live-capability registry is absent");
        }
        registration_id_ = registry_->register_or_throw(
            kind, std::move(content_sha256), size_bytes);
    }

    PayloadStoreLiveCapabilityRegistration(
        const PayloadStoreLiveCapabilityRegistration&) = delete;
    PayloadStoreLiveCapabilityRegistration& operator=(
        const PayloadStoreLiveCapabilityRegistration&) = delete;

    PayloadStoreLiveCapabilityRegistration(
        PayloadStoreLiveCapabilityRegistration&& other) noexcept
        : registry_(std::move(other.registry_)),
          registration_id_(std::exchange(other.registration_id_, 0U)) {}

    PayloadStoreLiveCapabilityRegistration& operator=(
        PayloadStoreLiveCapabilityRegistration&& other) noexcept {
        if (this == &other) return *this;
        release_noexcept();
        registry_ = std::move(other.registry_);
        registration_id_ = std::exchange(other.registration_id_, 0U);
        return *this;
    }

    ~PayloadStoreLiveCapabilityRegistration() noexcept {
        release_noexcept();
    }

    [[nodiscard]] std::uint64_t registration_id() const noexcept {
        return registration_id_;
    }

    [[nodiscard]] const std::shared_ptr<PayloadStoreLiveCapabilityRegistry>&
    registry() const noexcept {
        return registry_;
    }

private:
    void release_noexcept() noexcept {
        if (registry_ && registration_id_ != 0U) {
            registry_->unregister_noexcept(registration_id_);
        }
        registration_id_ = 0U;
        registry_.reset();
    }

    std::shared_ptr<PayloadStoreLiveCapabilityRegistry> registry_;
    std::uint64_t registration_id_ = 0U;
};

[[nodiscard]] std::string transient_namespace_digest_or_throw(
    const ScannedPayloadIndex& scanned,
    std::string_view label) {
    const auto count_to_u64 = [&](std::size_t count,
                                  std::string_view field) {
        if (count > std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                std::string(label) + " " + std::string(field) +
                " count exceeds uint64 range");
        }
        return static_cast<std::uint64_t>(count);
    };
    const std::uint64_t staged_prefix_count = count_to_u64(
        scanned.staged_prefixes.size(), "staged-prefix");
    const std::uint64_t staged_range_count = count_to_u64(
        scanned.staged_ranges.size(), "staged-range");
    const std::uint64_t assembly_count = count_to_u64(
        scanned.assemblies.size(), "assembly-residue");
    const std::uint64_t publication_residue_count = count_to_u64(
        scanned.publication_residues.size(), "publication-residue");

    std::uint64_t observed_count = 0U;
    std::uint64_t observed_bytes = 0U;
    std::uint64_t observed_reserved_bytes = 0U;
    const auto add_checked = [&](std::uint64_t& total,
                                 std::uint64_t amount,
                                 std::string_view field) {
        if (amount > std::numeric_limits<std::uint64_t>::max() - total) {
            throw std::overflow_error(
                std::string(label) + " transient namespace " +
                std::string(field) + " overflows");
        }
        total += amount;
    };
    const auto observe = [&](std::uint64_t bytes,
                             std::uint64_t reserved_bytes) {
        add_checked(observed_count, 1U, "count");
        add_checked(observed_bytes, bytes, "physical bytes");
        add_checked(
            observed_reserved_bytes, reserved_bytes, "reserved bytes");
    };
    for (const StagedPrefixEntry& entry : scanned.staged_prefixes) {
        observe(entry.actual_size_bytes, entry.total_size_bytes);
    }
    for (const StagedRangeEntry& entry : scanned.staged_ranges) {
        observe(entry.size_bytes, entry.size_bytes);
    }
    for (const AssemblyEntry& entry : scanned.assemblies) {
        observe(entry.size_bytes, entry.size_bytes);
    }
    for (const PublicationResidueEntry& entry :
         scanned.publication_residues) {
        observe(entry.size_bytes, entry.size_bytes);
    }
    if (observed_count != scanned.transient_entry_count ||
        observed_bytes != scanned.transient_bytes ||
        observed_reserved_bytes != scanned.transient_reserved_bytes) {
        throw std::logic_error(
            std::string(label) +
            " transient namespace aggregate accounting is inconsistent");
    }

    if (!std::is_sorted(
            scanned.staged_prefixes.begin(),
            scanned.staged_prefixes.end(), staged_prefix_precedes) ||
        !std::is_sorted(
            scanned.staged_ranges.begin(), scanned.staged_ranges.end(),
            staged_range_precedes) ||
        !std::is_sorted(
            scanned.assemblies.begin(), scanned.assemblies.end(),
            assembly_precedes) ||
        !std::is_sorted(
            scanned.publication_residues.begin(),
            scanned.publication_residues.end(),
            publication_residue_precedes)) {
        throw std::logic_error(
            std::string(label) +
            " transient namespace is not canonically ordered");
    }

    Sha256DigestBuilder digest;
    append_string(digest, kTransientNamespaceDigestDomain);
    std::string metadata_bytes;
    metadata_bytes.reserve(
        static_cast<std::size_t>(
            kSyncPosixRegularFileSnapshotMetadataEncodedBytes));
    const std::string metadata_label =
        std::string(label) + " transient file observation";
    const auto append_metadata = [&](const struct stat& status) {
        const SyncPosixRegularFileSnapshotMetadata metadata =
            sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                status, SyncPosixDescriptorLinkPolicy::exactly_one,
                metadata_label);
        metadata_bytes.clear();
        append_sync_posix_regular_file_snapshot_metadata_binary(
            metadata_bytes, metadata);
        if (metadata_bytes.size() !=
            kSyncPosixRegularFileSnapshotMetadataEncodedBytes) {
            throw std::logic_error(
                std::string(label) +
                " transient file metadata codec returned a noncanonical width");
        }
        append_string(digest, metadata_bytes);
    };

    append_string(digest, "staged_prefix");
    append_u64(digest, staged_prefix_count);
    for (const StagedPrefixEntry& entry : scanned.staged_prefixes) {
        append_string(digest, entry.basename);
        append_string(digest, entry.content_sha256);
        append_u64(digest, entry.total_size_bytes);
        append_u64(digest, entry.committed_prefix_bytes);
        append_u64(digest, entry.actual_size_bytes);
        append_metadata(entry.status);
    }

    append_string(digest, "staged_range");
    append_u64(digest, staged_range_count);
    for (const StagedRangeEntry& entry : scanned.staged_ranges) {
        append_string(digest, entry.basename);
        append_string(digest, entry.content_sha256);
        append_u64(digest, entry.offset_bytes);
        append_string(digest, entry.chunk_sha256);
        append_u64(digest, entry.size_bytes);
        append_metadata(entry.status);
    }

    append_string(digest, "assembly_residue");
    append_u64(digest, assembly_count);
    for (const AssemblyEntry& entry : scanned.assemblies) {
        append_string(digest, entry.basename);
        append_u64(digest, entry.size_bytes);
        append_metadata(entry.status);
    }

    append_string(digest, "publication_residue");
    append_u64(digest, publication_residue_count);
    for (const PublicationResidueEntry& entry :
         scanned.publication_residues) {
        append_string(digest, entry.basename);
        append_u64(digest, entry.size_bytes);
        append_metadata(entry.status);
    }

    append_u64(digest, observed_count);
    append_u64(digest, observed_bytes);
    append_u64(digest, observed_reserved_bytes);
    return digest.finish_hex();
}
void append_framed_marker_field(
    std::string& output,
    std::string_view value) {
    output.append(std::to_string(value.size()));
    output.push_back(':');
    output.append(value);
}

[[nodiscard]] std::string product_store_identity_payload_or_throw(
    const SyncReplicaDeploymentIdentity& identity,
    const std::string& label) {
    validate_sync_replica_deployment_identity_or_throw(identity, label);
    std::string payload;
    payload.reserve(
        kProductStoreIdentityDomainV3.size() +
        identity.deployment_id.size() + identity.manifest_digest.size() +
        identity.manifest_path.generic_string().size() +
        identity.folder_id.size() + identity.local_actor.device_id.size() +
        kStoreLeaseProtocol.size() + 192U);
    payload.append(kProductStoreIdentityDomainV3);
    payload.push_back('\n');
    append_framed_marker_field(payload, identity.deployment_id);
    append_framed_marker_field(payload, identity.manifest_digest);
    append_framed_marker_field(
        payload, identity.manifest_path.generic_string());
    append_framed_marker_field(payload, identity.folder_id);
    append_framed_marker_field(payload, identity.local_actor.device_id);
    append_framed_marker_field(
        payload, std::to_string(identity.local_actor.epoch));
    append_framed_marker_field(payload, kStoreLeaseProtocol);
    return payload;
}

[[nodiscard]] bool same_identity(
    const struct stat& left,
    const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] bool same_timespec(
    const timespec& left,
    const timespec& right) noexcept {
    return left.tv_sec == right.tv_sec && left.tv_nsec == right.tv_nsec;
}

[[nodiscard]] bool same_node_observation(
    const struct stat& left,
    const struct stat& right) noexcept {
    const bool common =
        same_identity(left, right) && left.st_mode == right.st_mode &&
        left.st_nlink == right.st_nlink && left.st_uid == right.st_uid &&
        left.st_gid == right.st_gid && left.st_size == right.st_size;
#if defined(__APPLE__)
    return common && same_timespec(left.st_mtimespec, right.st_mtimespec) &&
           same_timespec(left.st_ctimespec, right.st_ctimespec);
#elif defined(__linux__) || defined(__FreeBSD__) || defined(__NetBSD__) || \
    defined(__OpenBSD__)
    return common && same_timespec(left.st_mtim, right.st_mtim) &&
           same_timespec(left.st_ctim, right.st_ctim);
#else
    return common && left.st_mtime == right.st_mtime &&
           left.st_ctime == right.st_ctime;
#endif
}

[[nodiscard]] bool same_directory_observation(
    const struct stat& left,
    const struct stat& right) noexcept {
    return same_node_observation(left, right);
}

// rename(2) may advance ctime on the renamed inode even though its content and
// all other retained metadata remain unchanged. Publication paths re-fstat the
// still-open descriptor after rename, permit only that ctime transition, and
// then use the new complete observation for exact pathname reproof.
[[nodiscard]] bool same_regular_file_rename_transition(
    const struct stat& before,
    const struct stat& after) noexcept {
    const bool common =
        same_identity(before, after) && before.st_mode == after.st_mode &&
        before.st_nlink == after.st_nlink && before.st_uid == after.st_uid &&
        before.st_gid == after.st_gid && before.st_size == after.st_size;
#if defined(__APPLE__)
    return common && same_timespec(before.st_mtimespec, after.st_mtimespec);
#elif defined(__linux__) || defined(__FreeBSD__) || defined(__NetBSD__) || \
    defined(__OpenBSD__)
    return common && same_timespec(before.st_mtim, after.st_mtim);
#else
    return common && before.st_mtime == after.st_mtime;
#endif
}

// In-place journal slot updates may advance both mtime and ctime. The exact
// inode, private ownership/mode, link count, and fixed encoded extent must stay
// unchanged across that write; the post-write observation is then used for the
// final pathname proof.
[[nodiscard]] bool same_regular_file_write_transition(
    const struct stat& before,
    const struct stat& after) noexcept {
    return same_identity(before, after) && before.st_mode == after.st_mode &&
           before.st_nlink == after.st_nlink && before.st_uid == after.st_uid &&
           before.st_gid == after.st_gid && before.st_size == after.st_size;
}

void fsync_or_throw(int descriptor, const std::string& label) {
    int result;
    do {
        result = ::fsync(descriptor);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(label + " synchronization failed: " +
                                 error_text(error));
    }
}

void require_private_regular_file_or_throw(
    const struct stat& status,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " is not a regular file");
    }
    if (status.st_nlink != 1) {
        throw std::runtime_error(label + " is not a single-link file");
    }
    if (static_cast<std::uint64_t>(status.st_dev) !=
        root_attestation.device) {
        throw std::runtime_error(label + " is not on the retained root device");
    }
    if (static_cast<std::uint64_t>(status.st_uid) !=
        root_attestation.effective_user_id) {
        throw std::runtime_error(label + " is not owned by the effective user");
    }
    if ((status.st_mode & 07777U) != (S_IRUSR | S_IWUSR)) {
        throw std::runtime_error(label + " does not have exact mode 0600");
    }
    if (status.st_size < 0) {
        throw std::runtime_error(label + " has a negative size");
    }
}

void verify_named_regular_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const struct stat& expected,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label);

[[nodiscard]] bool same_regular_file_observation(
    const struct stat& left,
    const struct stat& right) noexcept {
    return same_node_observation(left, right);
}

[[nodiscard]] std::shared_ptr<const PayloadVerificationGeneration>
matching_verification_generation_or_none(
    PayloadVerificationCache& cache,
    const struct stat& identity_status) {
    const std::shared_ptr<const PayloadVerificationGeneration> generation =
        cache.generation;
    if (generation == nullptr || !generation->identity_status.has_value() ||
        !same_regular_file_observation(
            *generation->identity_status, identity_status)) {
        return {};
    }
    return generation;
}

[[nodiscard]] std::shared_ptr<const PayloadVerificationGeneration>
publish_verification_generation(
    PayloadVerificationCache& cache,
    std::shared_ptr<const PayloadVerificationGeneration> generation) {
    if (generation == nullptr || !generation->identity_status.has_value()) {
        throw std::logic_error(
            "payload verification cache cannot publish an empty generation");
    }
    std::shared_ptr<const PayloadVerificationGeneration> retired =
        std::move(cache.generation);
    cache.generation = std::move(generation);
    return retired;
}

struct StreamedFileDigest final {
    std::string sha256;
    std::string selected_bytes;
};

[[nodiscard]] StreamedFileDigest stream_hash_regular_file_or_throw(
    int descriptor,
    const struct stat& expected_status,
    std::optional<std::pair<std::uint64_t, std::uint64_t>> selected_range,
    const std::string& label) {
    if (expected_status.st_size < 0) {
        throw std::runtime_error(label + " has a negative size");
    }
    const std::uint64_t total_size =
        static_cast<std::uint64_t>(expected_status.st_size);
    if (selected_range.has_value()) {
        const auto [offset, length] = *selected_range;
        if (offset > total_size || length > total_size - offset) {
            throw std::invalid_argument(
                label + " selected range exceeds the exact file size");
        }
    }

    StreamedFileDigest out;
    if (selected_range.has_value()) {
        out.selected_bytes.reserve(u64_to_size_or_throw(
            selected_range->second, label + " selected range"));
    }
    Sha256DigestBuilder digest;
    std::array<char, kStreamingBufferBytes> buffer{};
    std::uint64_t position = 0U;
    while (position < total_size) {
        const std::uint64_t remaining = total_size - position;
        const std::size_t requested = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, buffer.size()));
        ssize_t read_count;
        do {
            read_count = ::pread(
                descriptor, buffer.data(), requested,
                static_cast<off_t>(position));
        } while (read_count < 0 && errno == EINTR);
        if (read_count < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " read failed: " + error_text(error));
        }
        if (read_count == 0) {
            throw PayloadStoreObservationStaleError(
                label + " became truncated while read");
        }
        const std::uint64_t got = static_cast<std::uint64_t>(read_count);
        if (got > remaining) {
            throw std::runtime_error(label + " read crossed its exact size");
        }
        const std::string_view block(
            buffer.data(), static_cast<std::size_t>(read_count));
        digest.update(block);

        if (selected_range.has_value()) {
            const std::uint64_t selected_begin = selected_range->first;
            const std::uint64_t selected_end =
                selected_begin + selected_range->second;
            const std::uint64_t block_begin = position;
            const std::uint64_t block_end = position + got;
            const std::uint64_t overlap_begin =
                std::max(block_begin, selected_begin);
            const std::uint64_t overlap_end =
                std::min(block_end, selected_end);
            if (overlap_begin < overlap_end) {
                const std::size_t local_offset =
                    u64_to_size_or_throw(
                        overlap_begin - block_begin,
                        label + " selected block offset");
                const std::size_t local_size =
                    u64_to_size_or_throw(
                        overlap_end - overlap_begin,
                        label + " selected block size");
                out.selected_bytes.append(block.substr(local_offset, local_size));
            }
        }
        position += got;
    }

    struct stat after{};
    if (::fstat(descriptor, &after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final fstat failed: " + error_text(error));
    }
    if (!same_regular_file_observation(expected_status, after)) {
        throw PayloadStoreObservationStaleError(
            label + " changed while it was read");
    }
    if (selected_range.has_value() &&
        out.selected_bytes.size() != selected_range->second) {
        throw std::runtime_error(label + " did not yield its exact selected range");
    }
    out.sha256 = digest.finish_hex();
    return out;
}

struct ContentDefinedDigestProjection final {
    std::string whole_sha256;
    ResumableSha256Checkpoint whole_checkpoint;
    std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk> chunks;
};

// One shared accumulator backs both the traditional complete descriptor scan
// and the bounded source projection. An active checkpoint captures the exact
// arbitrary-byte frontier, including the rolling gear state and resumable
// whole/current-chunk SHA-256 states. Higher owners bind that acceleration to
// the exact payload inode observation before any later bytes may extend it.
class ContentDefinedDigestAccumulator final {
public:
    ContentDefinedDigestAccumulator(
        std::uint64_t total_size_bytes,
        SyncReplicaContentDefinedChunkingParameters parameters,
        const std::string& label)
        : total_size_bytes_(total_size_bytes),
          parameters_(parameters),
          chunker_(parameters, label + " chunker") {
        initialize_or_throw(label);
    }

    ContentDefinedDigestAccumulator(
        std::uint64_t total_size_bytes,
        SyncReplicaContentDefinedChunkingParameters parameters,
        SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint checkpoint,
        const std::string& label)
        : total_size_bytes_(total_size_bytes),
          parameters_(parameters),
          chunker_(parameters, checkpoint.chunker,
                   label + " restored chunker"),
          whole_digest_(checkpoint.whole_hash,
                        label + " restored whole hash"),
          chunk_digest_(checkpoint.current_chunk_hash,
                        label + " restored current chunk hash"),
          chunks_(std::move(checkpoint.completed_chunks)),
          consumed_bytes_(checkpoint.next_offset_bytes),
          completed_chunk_bytes_(checkpoint.completed_chunk_bytes),
          current_chunk_bytes_(checkpoint.chunker.pending_chunk_bytes) {
        initialize_or_throw(label);
        if (checkpoint.total_size_bytes != total_size_bytes_ ||
            checkpoint.parameters != parameters_ ||
            checkpoint.next_offset_bytes == 0U ||
            checkpoint.next_offset_bytes >= total_size_bytes_ ||
            checkpoint.whole_hash.total_bytes != checkpoint.next_offset_bytes ||
            checkpoint.current_chunk_hash.total_bytes !=
                checkpoint.chunker.pending_chunk_bytes ||
            checkpoint.chunker.finished ||
            checkpoint.chunker.completed_chunk_count != chunks_.size() ||
            chunks_.size() > parameters_.maximum_chunk_count) {
            throw std::invalid_argument(
                label + " restored projection checkpoint is not one exact nonterminal byte frontier");
        }
        std::uint64_t extent = 0U;
        for (const auto& chunk : chunks_) {
            if (chunk.size_bytes < parameters_.minimum_chunk_bytes ||
                chunk.size_bytes > parameters_.maximum_chunk_bytes ||
                extent > checkpoint.completed_chunk_bytes ||
                chunk.size_bytes > checkpoint.completed_chunk_bytes - extent) {
                throw std::invalid_argument(
                    label + " restored projection checkpoint has a noncanonical completed chunk");
            }
            extent += chunk.size_bytes;
        }
        if (extent != checkpoint.completed_chunk_bytes ||
            checkpoint.completed_chunk_bytes > checkpoint.next_offset_bytes ||
            checkpoint.chunker.pending_chunk_bytes >
                checkpoint.next_offset_bytes - checkpoint.completed_chunk_bytes ||
            checkpoint.completed_chunk_bytes +
                    checkpoint.chunker.pending_chunk_bytes !=
                checkpoint.next_offset_bytes) {
            throw std::invalid_argument(
                label + " restored projection checkpoint extents do not reach its byte frontier");
        }
    }

    void consume_or_throw(
        std::string_view bytes,
        const std::string& label) {
        if (bytes.empty()) return;
        const std::uint64_t byte_count = size_to_u64_or_throw(
            bytes.size(), label + " projected byte count");
        if (consumed_bytes_ > total_size_bytes_ ||
            byte_count > total_size_bytes_ - consumed_bytes_) {
            throw std::invalid_argument(
                label + " projected bytes exceed the exact payload extent");
        }

        std::size_t span_begin = 0U;
        for (std::size_t index = 0U; index < bytes.size(); ++index) {
            if (current_chunk_bytes_ ==
                std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error(
                    label + " projected chunk byte counter overflow");
            }
            ++current_chunk_bytes_;
            if (!chunker_.consume_byte(
                    static_cast<std::uint8_t>(
                        static_cast<unsigned char>(bytes[index])))) {
                continue;
            }
            const std::size_t span_size = index + 1U - span_begin;
            const std::string_view completed_span =
                bytes.substr(span_begin, span_size);
            whole_digest_.update(completed_span);
            chunk_digest_.update(completed_span);
            if (completed_chunk_bytes_ > total_size_bytes_ ||
                current_chunk_bytes_ >
                    total_size_bytes_ - completed_chunk_bytes_) {
                throw std::overflow_error(
                    label + " projected chunk extent overflow");
            }
            completed_chunk_bytes_ += current_chunk_bytes_;
            chunks_.emplace_back(
                current_chunk_bytes_,
                Sha256DigestValue(chunk_digest_.finish_binary_array()));
            chunk_digest_ = ResumableSha256{};
            current_chunk_bytes_ = 0U;
            span_begin = index + 1U;
        }
        if (span_begin != bytes.size()) {
            const std::string_view pending_span = bytes.substr(span_begin);
            whole_digest_.update(pending_span);
            chunk_digest_.update(pending_span);
        }
        consumed_bytes_ += byte_count;
        if (current_chunk_bytes_ != chunker_.pending_chunk_bytes()) {
            throw std::logic_error(
                label + " projected chunk hash and rolling frontier diverged");
        }
    }

    [[nodiscard]] std::uint64_t consumed_bytes() const noexcept {
        return consumed_bytes_;
    }

    [[nodiscard]] std::uint64_t completed_chunk_bytes() const noexcept {
        return completed_chunk_bytes_;
    }

    [[nodiscard]] const std::vector<
        SyncReplicaFilePayloadStoreContentDefinedChunk>&
    chunks() const noexcept {
        return chunks_;
    }

    [[nodiscard]]
    SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint checkpoint(
        std::string_view content_sha256,
        const SyncPosixRegularFileSnapshotMetadata& metadata) const {
        if (consumed_bytes_ == 0U || consumed_bytes_ >= total_size_bytes_ ||
            current_chunk_bytes_ != chunker_.pending_chunk_bytes() ||
            chunks_.size() != chunker_.completed_chunk_count()) {
            throw std::logic_error(
                "content-defined projection has no exact nonterminal checkpoint");
        }
        return {
            std::string(content_sha256),
            total_size_bytes_,
            metadata,
            parameters_,
            consumed_bytes_,
            completed_chunk_bytes_,
            whole_digest_.checkpoint(),
            chunk_digest_.checkpoint(),
            chunker_.checkpoint(),
            chunks_,
        };
    }

    [[nodiscard]] ContentDefinedDigestProjection finish_or_throw(
        const std::string& label) {
        if (consumed_bytes_ != total_size_bytes_) {
            throw std::logic_error(
                label + " content-defined projection ended before its exact extent");
        }
        if (current_chunk_bytes_ != 0U) {
            const std::uint64_t final_chunk_bytes = current_chunk_bytes_;
            chunker_.finish_stream_or_throw();
            if (completed_chunk_bytes_ > total_size_bytes_ ||
                final_chunk_bytes >
                    total_size_bytes_ - completed_chunk_bytes_) {
                throw std::overflow_error(
                    label + " final projected chunk extent overflow");
            }
            completed_chunk_bytes_ += final_chunk_bytes;
            chunks_.emplace_back(
                final_chunk_bytes,
                Sha256DigestValue(chunk_digest_.finish_binary_array()));
            chunk_digest_ = ResumableSha256{};
            current_chunk_bytes_ = 0U;
        } else {
            chunker_.finish_stream_or_throw();
        }
        const SyncReplicaContentDefinedChunkerCheckpoint terminal_chunker =
            chunker_.checkpoint();
        if (chunks_.empty() ||
            chunks_.size() != terminal_chunker.completed_chunk_count ||
            !terminal_chunker.finished ||
            terminal_chunker.pending_chunk_bytes != 0U ||
            completed_chunk_bytes_ != total_size_bytes_) {
            throw std::logic_error(
                label + " content-defined projection lost its chunk frontier");
        }
        const ResumableSha256Checkpoint whole_checkpoint =
            whole_digest_.checkpoint();
        if (whole_checkpoint.total_bytes != total_size_bytes_) {
            throw std::logic_error(
                label + " content-defined projection lost its whole-hash frontier");
        }
        return {
            whole_digest_.finish_hex(), whole_checkpoint, std::move(chunks_)};
    }

private:
    void initialize_or_throw(const std::string& label) {
        if (total_size_bytes_ == 0U) {
            throw std::invalid_argument(
                label + " requires one nonempty regular payload");
        }
        validate_sync_replica_content_defined_chunking_parameters_or_throw(
            parameters_, label + " parameters");
        const std::uint64_t conservative_count =
            1U + ((total_size_bytes_ - 1U) /
                  parameters_.minimum_chunk_bytes);
        chunks_.reserve(u64_to_size_or_throw(
            std::min<std::uint64_t>(
                conservative_count, parameters_.maximum_chunk_count),
            label + " chunk reserve"));
    }

    std::uint64_t total_size_bytes_ = 0U;
    SyncReplicaContentDefinedChunkingParameters parameters_;
    SyncReplicaContentDefinedChunker chunker_;
    ResumableSha256 whole_digest_;
    ResumableSha256 chunk_digest_;
    std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk> chunks_;
    std::uint64_t consumed_bytes_ = 0U;
    std::uint64_t completed_chunk_bytes_ = 0U;
    std::uint64_t current_chunk_bytes_ = 0U;
};

[[nodiscard]] ContentDefinedDigestProjection
hash_regular_file_content_defined_chunks_or_throw(
    int descriptor,
    const struct stat& expected_status,
    SyncReplicaContentDefinedChunkingParameters parameters,
    const std::string& label) {
    if (expected_status.st_size <= 0) {
        throw std::invalid_argument(
            label + " requires one nonempty regular payload");
    }
    const std::uint64_t total_size =
        static_cast<std::uint64_t>(expected_status.st_size);
    ContentDefinedDigestAccumulator accumulator(
        total_size, parameters, label);
    std::array<char, kStreamingBufferBytes> buffer{};
    while (accumulator.consumed_bytes() < total_size) {
        const std::uint64_t remaining =
            total_size - accumulator.consumed_bytes();
        const std::size_t requested = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, buffer.size()));
        ssize_t read_count;
        do {
            read_count = ::pread(
                descriptor, buffer.data(), requested,
                static_cast<off_t>(accumulator.consumed_bytes()));
        } while (read_count < 0 && errno == EINTR);
        if (read_count < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " content-defined read failed: " + error_text(error));
        }
        if (read_count == 0) {
            throw PayloadStoreObservationStaleError(
                label + " became truncated while content-defined chunks were read");
        }
        const std::size_t got = static_cast<std::size_t>(read_count);
        if (static_cast<std::uint64_t>(got) > remaining) {
            throw std::runtime_error(
                label + " content-defined read crossed its exact extent");
        }
        accumulator.consume_or_throw(
            std::string_view(buffer.data(), got), label);
    }

    struct stat after{};
    if (::fstat(descriptor, &after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final fstat failed: " + error_text(error));
    }
    if (!same_regular_file_observation(expected_status, after)) {
        throw PayloadStoreObservationStaleError(
            label + " changed while content-defined chunks were read");
    }
    return accumulator.finish_or_throw(label);
}

struct CopiedFileRange final {
    std::string chunk_sha256;
    std::string bytes;
};

// A payload snapshot already proved the whole digest while scanning under the
// cooperative store lease. The unchanged-inode fast path therefore re-proves
// the exact indexed observation and reads only the requested range. If that
// observation drifted, the caller performs a rare complete-digest fallback so
// an exact atomic re-publication remains usable while changed bytes still fail
// closed. Re-reading the complete file for every ordinary bounded range made an
// N-range transfer O(N^2) in source I/O without adding authority against
// noncooperating same-UID writers, which are outside this store boundary.
//
// The destination is caller-owned. This lets the reconciliation source read
// directly into its one final wire frame instead of first retaining one owned
// range string beside that frame.
[[nodiscard]] std::string copy_hash_regular_file_range_into_or_throw(
    int descriptor,
    const struct stat& expected_status,
    std::uint64_t offset_bytes,
    std::span<char> destination,
    const std::string& label) {
    if (expected_status.st_size < 0) {
        throw std::runtime_error(label + " has a negative size");
    }
    const std::uint64_t total_size =
        static_cast<std::uint64_t>(expected_status.st_size);
    const std::uint64_t range_bytes = size_to_u64_or_throw(
        destination.size(), label + " selected range");
    if (offset_bytes > total_size ||
        range_bytes > total_size - offset_bytes) {
        throw std::invalid_argument(
            label + " selected range exceeds the exact file size");
    }

    Sha256DigestBuilder digest;
    std::uint64_t copied = 0U;
    while (copied < range_bytes) {
        const std::uint64_t remaining = range_bytes - copied;
        const std::size_t copied_size = u64_to_size_or_throw(
            copied, label + " copied range bytes");
        const std::size_t requested = std::min<std::size_t>(
            u64_to_size_or_throw(remaining, label + " remaining range bytes"),
            static_cast<std::size_t>(std::numeric_limits<ssize_t>::max()));
        ssize_t read_count;
        do {
            read_count = ::pread(
                descriptor, destination.data() + copied_size, requested,
                static_cast<off_t>(offset_bytes + copied));
        } while (read_count < 0 && errno == EINTR);
        if (read_count < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " range read failed: " + error_text(error));
        }
        if (read_count == 0) {
            throw std::runtime_error(
                label + " became truncated while its range was read");
        }
        const std::uint64_t got = static_cast<std::uint64_t>(read_count);
        if (got > remaining) {
            throw std::runtime_error(
                label + " range read crossed its exact extent");
        }
        digest.update(std::string_view(
            destination.data() + copied_size,
            static_cast<std::size_t>(read_count)));
        copied += got;
    }

    struct stat after{};
    if (::fstat(descriptor, &after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final fstat failed: " + error_text(error));
    }
    if (!same_regular_file_observation(expected_status, after)) {
        throw std::runtime_error(label + " changed while its range was read");
    }
    if (copied != range_bytes) {
        throw std::runtime_error(label + " did not yield its exact selected range");
    }
    return digest.finish_hex();
}

[[nodiscard]] CopiedFileRange copy_hash_regular_file_range_or_throw(
    int descriptor,
    const struct stat& expected_status,
    std::uint64_t offset_bytes,
    std::uint64_t range_bytes,
    const std::string& label) {
    CopiedFileRange out;
    out.bytes.resize(u64_to_size_or_throw(
        range_bytes, label + " selected range"));
    out.chunk_sha256 = copy_hash_regular_file_range_into_or_throw(
        descriptor, expected_status, offset_bytes,
        std::span<char>(out.bytes.data(), out.bytes.size()), label);
    return out;
}

[[nodiscard]] std::uint64_t
next_terminal_verification_generation_or_throw(
    const TerminalVerificationStateFileObservation& observation,
    const std::string& label) {
    const std::uint64_t maximum =
        observation.usable && observation.journal.has_value()
            ? observation.journal->latest_state.generation
            : 0U;
    if (maximum == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " terminal verification generation is exhausted");
    }
    return maximum + 1U;
}

void write_all_or_throw(
    int descriptor,
    std::string_view bytes,
    const std::string& label) {
    std::size_t written = 0U;
    while (written < bytes.size()) {
        ssize_t count;
        do {
            count = ::write(
                descriptor, bytes.data() + written, bytes.size() - written);
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " write failed: " + error_text(error));
        }
        if (count == 0) {
            throw std::runtime_error(label + " write made no progress");
        }
        written += static_cast<std::size_t>(count);
    }
}

void pwrite_all_or_throw(
    int descriptor,
    std::string_view bytes,
    std::uint64_t offset_bytes,
    const std::string& label) {
    std::size_t written = 0U;
    while (written < bytes.size()) {
        const std::uint64_t position = checked_add_u64_or_throw(
            offset_bytes, static_cast<std::uint64_t>(written),
            label + " write offset");
        if (position > kMaximumPersistentInteger) {
            throw std::overflow_error(label + " write offset exceeds off_t range");
        }
        ssize_t count;
        do {
            count = ::pwrite(
                descriptor, bytes.data() + written, bytes.size() - written,
                static_cast<off_t>(position));
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " pwrite failed: " + error_text(error));
        }
        if (count == 0) {
            throw std::runtime_error(label + " pwrite made no progress");
        }
        written += static_cast<std::size_t>(count);
    }
}

void ftruncate_or_throw(
    int descriptor,
    std::uint64_t size_bytes,
    const std::string& label) {
    if (size_bytes > kMaximumPersistentInteger) {
        throw std::overflow_error(label + " truncate size exceeds off_t range");
    }
    int result;
    do {
        result = ::ftruncate(descriptor, static_cast<off_t>(size_bytes));
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " truncate failed: " + error_text(error));
    }
}

void unlinkat_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const std::string& label) {
    const std::string name(basename);
    int result;
    do {
        result = ::unlinkat(directory_descriptor, name.c_str(), 0);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " unlink failed: " + error_text(error));
    }
}

void unlink_scanned_private_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const struct stat& expected_status,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    verify_named_regular_file_or_throw(
        directory_descriptor, basename, expected_status, root_attestation,
        label + " pre-unlink proof");
    unlinkat_or_throw(directory_descriptor, basename, label);
}

void remove_scanned_publication_residues_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const std::vector<PublicationResidueEntry>& residues,
    const std::string& label) {
    if (residues.empty()) return;
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    root_authority.verify_or_throw(label + " root preflight");
    auto descriptor_lease = Access::duplicate_shared_open_description_or_throw(
        root_authority, label + " root");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    for (const PublicationResidueEntry& residue : residues) {
        unlink_scanned_private_file_or_throw(
            root_descriptor.get(), residue.basename, residue.status,
            root_authority.attestation(),
            label + " " + residue.basename);
    }
    fsync_or_throw(root_descriptor.get(), label + " root directory");
    root_authority.verify_or_throw(label + " final root proof");
}

void fchmod_private_or_throw(int descriptor, const std::string& label) {
    int result;
    do {
        result = ::fchmod(descriptor, S_IRUSR | S_IWUSR);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " mode normalization failed: " + error_text(error));
    }
}

void rename_noreplace_at_or_throw(
    int directory_descriptor,
    std::string_view source_basename,
    std::string_view destination_basename,
    const std::string& label) {
#if defined(__linux__) && defined(RENAME_NOREPLACE)
    const std::string source(source_basename);
    const std::string destination(destination_basename);
    int result;
    do {
        result = ::renameat2(
            directory_descriptor, source.c_str(), directory_descriptor,
            destination.c_str(), RENAME_NOREPLACE);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " no-replace rename failed: " + error_text(error));
    }
#else
    (void)directory_descriptor;
    (void)source_basename;
    (void)destination_basename;
    throw std::runtime_error(
        label + " requires Linux renameat2 RENAME_NOREPLACE");
#endif
}

void verify_named_regular_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const struct stat& expected,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    const std::string name(basename);
    struct stat observed{};
    int result;
    do {
        result = ::fstatat(directory_descriptor, name.c_str(), &observed,
                           AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT || error == ESTALE) {
            throw PayloadStoreObservationStaleError(
                label + " final namespace entry disappeared: " +
                error_text(error));
        }
        throw std::runtime_error(label + " final namespace inspection failed: " +
                                 error_text(error));
    }
    require_private_regular_file_or_throw(
        observed, root_attestation, label + " final namespace entry");
    if (!same_regular_file_observation(expected, observed)) {
        throw PayloadStoreObservationStaleError(
            label + " namespace entry changed during validation");
    }
}

void verify_named_entry_absent_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const std::string& label) {
    const std::string name(basename);
    struct stat observed{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, name.c_str(), &observed,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result == 0) {
        throw PayloadStoreObservationStaleError(
            label + " namespace entry remains present");
    }
    const int error = errno;
    if (error != ENOENT) {
        throw std::runtime_error(
            label + " namespace absence inspection failed: " +
            error_text(error));
    }
}

[[nodiscard]] SyncPosixOpenedRegularFile open_store_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const std::string& label) {
    return sync_posix_open_regular_file_component_or_throw(
        directory_descriptor, basename, root_path / std::string(basename),
        SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
        capability, mount_identity, label);
}

[[nodiscard]] std::optional<SyncPosixOpenedRegularFile>
open_optional_store_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const std::string& label) {
    return sync_posix_open_optional_regular_file_component_or_throw(
        directory_descriptor, basename, root_path / std::string(basename),
        SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
        capability, mount_identity, label);
}

[[nodiscard]] const SyncReplicaFilePayloadVerificationIndexEntry*
find_verification_index_entry(
    const SyncReplicaFilePayloadVerificationIndex& index,
    std::string_view digest) noexcept {
    const auto found = std::lower_bound(
        index.entries.begin(), index.entries.end(), digest,
        [](const SyncReplicaFilePayloadVerificationIndexEntry& entry,
           std::string_view value) {
            return entry.content_sha256 < value;
        });
    if (found == index.entries.end() || found->content_sha256 != digest) {
        return nullptr;
    }
    return &*found;
}

[[nodiscard]] VerificationIndexFileObservation
observe_verification_index_file_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat* locked_identity_status,
    bool read_contents,
    const std::string& label) {
    VerificationIndexFileObservation out;
    const std::string basename(
        kSyncReplicaFilePayloadVerificationIndexBasename);
    struct stat named{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, basename.c_str(), &named,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT) return out;
        throw std::runtime_error(
            label + " namespace inspection failed: " + error_text(error));
    }

    require_private_regular_file_or_throw(
        named, root_attestation, label + " namespace entry");
    const std::uint64_t maximum_bytes =
        sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
            limits.max_entries, label);
    // Oversized private metadata is unusable acceleration, not payload
    // authority. Bind and retain its exact observation so a complete byte scan
    // can conditionally replace it; never allocate or read beyond the
    // encoded-size ceiling merely because a stale/corrupt checkpoint exists.
    const bool encoded_size_admissible =
        static_cast<std::uint64_t>(named.st_size) <= maximum_bytes;

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability,
        mount_identity, label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (!same_regular_file_observation(named, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " changed between namespace inspection and open");
    }

    out.present = true;
    out.status = opened.status;
    out.metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            opened.status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " metadata");

    if (read_contents && encoded_size_admissible) {
        FrozenSyncPosixRegularFileSnapshot frozen =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                file.get(), maximum_bytes,
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " bytes");
        if (!frozen.matches_status(opened.status)) {
            throw PayloadStoreObservationStaleError(
                label + " changed between open and byte snapshot");
        }
        try {
            out.index =
                parse_sync_replica_file_payload_verification_index_or_throw(
                    frozen.bytes(), limits.max_entries,
                    limits.max_indexed_bytes, label + " contents");
        } catch (const std::invalid_argument&) {
            // A malformed checksum/encoding cannot grant reuse. The physical
            // file remains a recognized private metadata entry so a later
            // successful authoritative scan can conditionally replace it.
            out.index.reset();
        }

        if (out.index.has_value() && locked_identity_status != nullptr) {
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    *locked_identity_status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " identity binding");
            out.usable =
                out.index->store_identity_sha256 ==
                    sha256_hex(std::string(expected_identity)) &&
                out.index->store_identity_metadata == identity_metadata;
        }
    }

    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label + " final name proof");
    return out;
}

[[nodiscard]] ScrubStateFileObservation
observe_scrub_state_file_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat* locked_identity_status,
    bool read_contents,
    const std::string& label) {
    ScrubStateFileObservation out;
    const std::string basename(kSyncReplicaFilePayloadScrubStateBasename);
    struct stat named{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, basename.c_str(), &named,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT) return out;
        throw std::runtime_error(
            label + " namespace inspection failed: " + error_text(error));
    }

    require_private_regular_file_or_throw(
        named, root_attestation, label + " namespace entry");
    const std::uint64_t exact_bytes =
        sync_replica_file_payload_scrub_state_exact_bytes();
    const bool encoded_size_admissible =
        static_cast<std::uint64_t>(named.st_size) == exact_bytes;

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability,
        mount_identity, label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (!same_regular_file_observation(named, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " changed between namespace inspection and open");
    }

    out.present = true;
    out.status = opened.status;
    out.metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            opened.status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " metadata");

    if (read_contents && encoded_size_admissible) {
        FrozenSyncPosixRegularFileSnapshot frozen =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                file.get(), exact_bytes,
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " bytes");
        if (!frozen.matches_status(opened.status)) {
            throw PayloadStoreObservationStaleError(
                label + " changed between open and byte snapshot");
        }
        try {
            out.state = parse_sync_replica_file_payload_scrub_state_or_throw(
                frozen.bytes(), limits.max_payload_bytes,
                label + " contents");
        } catch (const std::invalid_argument&) {
            // Torn, stale, checksum-invalid, or otherwise malformed progress is
            // disposable scheduling evidence. Retain only the exact file
            // observation so a successful bounded attempt can replace it.
            out.state.reset();
        }
        if (out.state.has_value() && locked_identity_status != nullptr) {
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    *locked_identity_status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " identity binding");
            out.usable =
                out.state->store_identity_sha256 ==
                    sha256_hex(std::string(expected_identity)) &&
                out.state->store_identity_metadata == identity_metadata;
        }
    }

    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label + " final name proof");
    return out;
}

[[nodiscard]] TerminalVerificationStateFileObservation
observe_terminal_verification_state_file_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat& locked_identity_status,
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    bool read_contents,
    const std::string& label) {
    TerminalVerificationStateFileObservation out;
    const std::string basename =
        terminal_verification_basename_or_throw(content_sha256);
    struct stat named{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, basename.c_str(), &named,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT) return out;
        throw std::runtime_error(
            label + " namespace inspection failed: " + error_text(error));
    }

    require_private_regular_file_or_throw(
        named, root_attestation, label + " namespace entry");
    const std::uint64_t exact_bytes =
        sync_replica_file_payload_terminal_verification_journal_exact_bytes();
    const bool encoded_size_admissible =
        static_cast<std::uint64_t>(named.st_size) == exact_bytes;

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability,
        mount_identity, label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (!same_regular_file_observation(named, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " changed between namespace inspection and open");
    }

    out.present = true;
    out.status = opened.status;
    out.metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            opened.status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " metadata");

    if (read_contents && encoded_size_admissible) {
        FrozenSyncPosixRegularFileSnapshot frozen =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                file.get(), exact_bytes,
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " bytes");
        if (!frozen.matches_status(opened.status)) {
            throw PayloadStoreObservationStaleError(
                label + " changed between open and byte snapshot");
        }
        try {
            out.journal =
                parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
                    frozen.bytes(), limits.max_payload_bytes,
                    label + " contents");
        } catch (const std::invalid_argument&) {
            // Both slots may be torn or otherwise malformed. The file remains
            // recognized private computation metadata, but it grants no hash
            // continuation. A later exact prefix observation may rebuild it.
            out.journal.reset();
        }
        if (out.journal.has_value()) {
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    locked_identity_status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " identity binding");
            const std::string identity_sha256 =
                sha256_hex(std::string(expected_identity));
            out.usable = out.journal->valid_slot_count != 0U;
            for (const auto& slot : out.journal->slots) {
                if (!slot.has_value()) continue;
                out.usable =
                    out.usable &&
                    slot->store_identity_sha256 == identity_sha256 &&
                    slot->store_identity_metadata == identity_metadata &&
                    slot->content_sha256 == content_sha256 &&
                    slot->total_size_bytes == total_size_bytes;
            }
        }
    }

    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label + " final name proof");
    return out;
}

[[nodiscard]] RetentionMarkFileObservation
observe_retention_mark_file_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat* locked_identity_status,
    bool read_contents,
    const std::string& label) {
    RetentionMarkFileObservation out;
    const std::string basename(kSyncReplicaFilePayloadRetentionMarkBasename);
    struct stat named{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, basename.c_str(), &named,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT) return out;
        throw std::runtime_error(
            label + " namespace inspection failed: " + error_text(error));
    }

    require_private_regular_file_or_throw(
        named, root_attestation, label + " namespace entry");
    const std::uint64_t exact_bytes =
        sync_replica_file_payload_retention_mark_exact_bytes();
    const bool encoded_size_admissible =
        static_cast<std::uint64_t>(named.st_size) == exact_bytes;

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability,
        mount_identity, label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (!same_regular_file_observation(named, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " changed between namespace inspection and open");
    }

    out.present = true;
    out.status = opened.status;
    out.metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            opened.status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " metadata");

    if (read_contents && encoded_size_admissible) {
        FrozenSyncPosixRegularFileSnapshot frozen =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                file.get(), exact_bytes,
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " bytes");
        if (!frozen.matches_status(opened.status)) {
            throw PayloadStoreObservationStaleError(
                label + " changed between open and byte snapshot");
        }
        try {
            out.mark =
                parse_sync_replica_file_payload_retention_mark_or_throw(
                    frozen.bytes(), limits.max_entries,
                    limits.max_indexed_bytes, label + " contents");
        } catch (const std::invalid_argument&) {
            // Malformed/torn/stale-policy evidence is recognized internal
            // metadata but grants no collection authority. Exact file metadata
            // remains available for a later conditional replacement.
            out.mark.reset();
        }
        if (out.mark.has_value() && locked_identity_status != nullptr) {
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    *locked_identity_status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " identity binding");
            out.usable =
                out.mark->store_identity_sha256 ==
                    sha256_hex(std::string(expected_identity)) &&
                out.mark->store_identity_metadata == identity_metadata;
            if (out.usable) {
                out.mark_digest =
                    sync_replica_file_payload_retention_mark_digest_or_throw(
                        *out.mark, limits.max_entries,
                        limits.max_indexed_bytes, label + " digest");
            }
        }
    }

    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label + " final name proof");
    return out;
}

[[nodiscard]] SourceManifestCheckpointFileObservation
observe_source_manifest_checkpoint_file_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat* locked_identity_status,
    bool read_contents,
    const std::string& label) {
    SourceManifestCheckpointFileObservation out;
    const std::string basename(kSyncReplicaSourceManifestCheckpointBasename);
    struct stat named{};
    int result;
    do {
        result = ::fstatat(
            directory_descriptor, basename.c_str(), &named,
            AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == ENOENT) return out;
        throw std::runtime_error(
            label + " namespace inspection failed: " + error_text(error));
    }

    require_private_regular_file_or_throw(
        named, root_attestation, label + " namespace entry");
    // This record is disposable acceleration. An oversized private regular
    // file is malformed evidence, not payload or namespace authority. Keep
    // observing and re-proving the exact named inode so a later publication
    // can conditionally replace it, but never let its extent deny ordinary
    // payload access or a complete payload-store observation.
    const bool encoded_extent_is_usable =
        named.st_size >= 0 &&
        static_cast<std::uint64_t>(named.st_size) <=
            sync_replica_source_manifest_checkpoint_maximum_bytes();

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability,
        mount_identity, label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (!same_regular_file_observation(named, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " changed between namespace inspection and open");
    }

    out.present = true;
    out.status = opened.status;
    out.metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            opened.status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " metadata");
    const bool opened_extent_is_usable =
        opened.status.st_size >= 0 &&
        static_cast<std::uint64_t>(opened.status.st_size) <=
            sync_replica_source_manifest_checkpoint_maximum_bytes();
    if (read_contents && encoded_extent_is_usable &&
        opened_extent_is_usable && opened.status.st_size > 0) {
        const std::uint64_t exact_bytes =
            static_cast<std::uint64_t>(opened.status.st_size);
        FrozenSyncPosixRegularFileSnapshot frozen =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                file.get(), exact_bytes,
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " bytes");
        if (!frozen.matches_status(opened.status)) {
            throw PayloadStoreObservationStaleError(
                label + " changed between open and byte snapshot");
        }
        try {
            out.checkpoint =
                parse_sync_replica_source_manifest_checkpoint_or_throw(
                    frozen.bytes(), limits.max_payload_bytes,
                    kSyncReplicaSourceManifestCheckpointMaximumChunks,
                    label + " contents");
        } catch (const std::invalid_argument&) {
            // This file is optional acceleration. Malformed/torn bytes remain
            // recognized private metadata but never become source-byte proof.
            out.checkpoint.reset();
        }
        if (out.checkpoint.has_value() &&
            locked_identity_status != nullptr) {
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    *locked_identity_status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " identity binding");
            out.usable =
                out.checkpoint->store_identity_sha256 ==
                    sha256_hex(std::string(expected_identity)) &&
                out.checkpoint->store_identity_metadata == identity_metadata;
        }
    }

    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label + " final name proof");
    return out;
}

[[nodiscard]] bool verification_index_matches_scan(
    const SyncReplicaFilePayloadVerificationIndex& index,
    const ScannedPayloadIndex& scanned) {
    if (index.indexed_bytes != scanned.indexed_bytes ||
        index.entries.size() != scanned.entries.size()) {
        return false;
    }
    for (std::size_t position = 0U;
         position < scanned.entries.size(); ++position) {
        const PayloadIndexEntry& payload = scanned.entries[position];
        const SyncReplicaFilePayloadVerificationIndexEntry& verified =
            index.entries[position];
        if (verified.content_sha256 != payload.content_sha256 ||
            !sync_posix_regular_file_snapshot_metadata_matches_status(
                verified.metadata, payload.status)) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] StagedPrefixEntry open_staged_prefix_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    const ParsedStagedPrefixBasename& parsed,
    std::string_view basename,
    const SyncReplicaFilePayloadStoreLimits& limits,
    const std::string& label) {
    if (parsed.total_size_bytes == 0U ||
        parsed.total_size_bytes > limits.max_payload_bytes ||
        parsed.committed_prefix_bytes > parsed.total_size_bytes) {
        throw std::length_error(
            label + " staged prefix extent exceeds the payload ceiling");
    }
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, basename, root_path, capability, mount_identity,
        label);
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation, label);
    if (opened.status.st_size < 0) {
        throw std::runtime_error(label + " staged prefix has a negative size");
    }
    const std::uint64_t actual_size =
        static_cast<std::uint64_t>(opened.status.st_size);
    if (actual_size < parsed.committed_prefix_bytes) {
        throw std::runtime_error(
            label + " staged prefix is shorter than its committed basename cutpoint");
    }
    if (actual_size > parsed.total_size_bytes) {
        throw std::length_error(
            label + " staged prefix exceeds its exact total size");
    }
    verify_named_regular_file_or_throw(
        directory_descriptor, basename, opened.status, root_attestation,
        label);
    return StagedPrefixEntry{
        std::string(basename), parsed.content_sha256,
        parsed.total_size_bytes, parsed.committed_prefix_bytes, actual_size,
        opened.status};
}

[[nodiscard]] SyncPosixOpenedRegularFile
open_staged_prefix_writable_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const struct stat& expected_status,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    const std::string name(basename);
    int flags = O_RDWR;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    int descriptor;
    do {
        descriptor = ::openat(directory_descriptor, name.c_str(), flags);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " writable open failed: " + error_text(error));
    }
    OwnedFd owned(descriptor);
    struct stat status{};
    if (::fstat(owned.get(), &status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " writable fstat failed: " + error_text(error));
    }
    require_private_regular_file_or_throw(status, root_attestation, label);
    if (!same_regular_file_observation(expected_status, status)) {
        throw std::runtime_error(
            label + " changed before writable staging ownership");
    }
    verify_named_regular_file_or_throw(
        directory_descriptor, basename, status, root_attestation, label);
    return SyncPosixOpenedRegularFile{owned.release(), status};
}

[[nodiscard]] SyncDirectoryAuthority
reopen_matching_root_authority_or_throw(
    const SyncDirectoryAuthority& retained,
    const std::string& label) {
    retained.verify_or_throw(label + " retained root pre-open proof");
    SyncDirectoryAuthority reopened = SyncDirectoryAuthority::open_or_throw(
        retained.path(), label + " reopened root");
    retained.verify_or_throw(label + " retained root post-open proof");
    const std::string retained_digest =
        sync_directory_attestation_digest_or_throw(retained.attestation());
    const std::string reopened_digest =
        sync_directory_attestation_digest_or_throw(reopened.attestation());
    if (reopened.path() != retained.path() ||
        reopened_digest != retained_digest ||
        reopened.resolution_capability() != retained.resolution_capability() ||
        reopened.mount_namespace_identity() !=
            retained.mount_namespace_identity()) {
        throw std::runtime_error(
            label + " reopened root does not match retained store authority");
    }
    return reopened;
}

void verify_open_store_identity_or_throw(
    int directory_descriptor,
    int identity_descriptor,
    const struct stat& opened_status,
    const SyncDirectoryAttestation& root_attestation,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const std::string& label,
    StoreObservationDurability durability) {
    require_private_regular_file_or_throw(
        opened_status, root_attestation, label);
    if (static_cast<std::uint64_t>(opened_status.st_size) !=
        expected_identity.size()) {
        throw std::runtime_error(label + " does not bind this folder");
    }
    FrozenSyncPosixRegularFileSnapshot frozen =
        FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
            identity_descriptor, expected_identity.size(),
            SyncPosixDescriptorLinkPolicy::exactly_one, label);
    if (frozen.bytes() != expected_identity) {
        throw std::runtime_error(label + " does not bind this folder");
    }
    if (synchronizes_store_observation(durability)) {
        fsync_or_throw(identity_descriptor, label);
    }
    verify_named_regular_file_or_throw(
        directory_descriptor, identity_basename, opened_status,
        root_attestation, label);
    require_no_competing_store_identity_names_or_throw(
        directory_descriptor, identity_basename, label);
}

[[nodiscard]] VerifiedStoreIdentityFile
open_verified_store_identity_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const std::string& label,
    StoreObservationDurability durability) {
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, identity_basename, root_path, capability,
        mount_identity, label);
    VerifiedStoreIdentityFile identity{
        OwnedFd(opened.descriptor), opened.status};
    verify_open_store_identity_or_throw(
        directory_descriptor, identity.descriptor.get(), identity.status,
        root_attestation, identity_basename, expected_identity, label,
        durability);
    return identity;
}

void StoreLease::verify_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const std::string& label) const {
    if (root_descriptor_.get() < 0 || identity_descriptor_.get() < 0) {
        throw std::logic_error(label + " payload-store lease is inactive");
    }
    root_authority.verify_or_throw(label + " retained root pre-proof");
    if (root_authority.attestation() != root_attestation_) {
        throw std::runtime_error(
            label + " payload-store lease root attestation changed");
    }
    verify_open_store_identity_or_throw(
        root_descriptor_.get(), identity_descriptor_.get(), identity_status_,
        root_attestation_, identity_basename_, expected_identity_,
        label + " locked identity", durability_);
    root_authority.verify_or_throw(label + " retained root post-proof");
}

void StoreLease::rebind_identity_basename_after_atomic_rename_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string new_identity_basename,
    const std::string& label) {
    if (root_descriptor_.get() < 0 || identity_descriptor_.get() < 0) {
        throw std::logic_error(label + " payload-store lease is inactive");
    }
    if (mode_ != SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation) {
        throw std::logic_error(
            label + " identity migration requires an exclusive store lease");
    }
    if (!synchronizes_store_observation(durability_)) {
        throw std::logic_error(
            label + " identity migration requires reconciliation durability");
    }
    if (!payload_store_identity_basenames_are_supported_upgrade_pair(
            identity_basename_, new_identity_basename)) {
        throw std::invalid_argument(
            label +
            " identity migration requires an exact same-family reader "
            "upgrade pair");
    }

    // Allocate both names before the namespace mutation. A later exception may
    // report failure after the durable rename, but it leaves a singleton marker
    // that the next ensure pass can reconcile. No post-rename path may continue
    // under the old basename inside this lease.
    const std::string old_identity_basename = identity_basename_;
    verify_or_throw(root_authority, label + " pre-rename lease proof");

    struct stat destination_status {};
    int destination_result;
    do {
        destination_result = ::fstatat(
            root_descriptor_.get(), new_identity_basename.c_str(),
            &destination_status, AT_SYMLINK_NOFOLLOW);
    } while (destination_result != 0 && errno == EINTR);
    if (destination_result == 0) {
        throw std::runtime_error(
            label + " refuses an existing minimum-reader identity marker");
    }
    if (errno != ENOENT) {
        const int error = errno;
        throw std::runtime_error(
            label + " minimum-reader identity preflight failed: " +
            error_text(error));
    }

    rename_noreplace_at_or_throw(
        root_descriptor_.get(), old_identity_basename,
        new_identity_basename, label + " identity migration");

    struct stat renamed_status {};
    if (::fstat(identity_descriptor_.get(), &renamed_status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " renamed identity fstat failed: " + error_text(error));
    }
    require_private_regular_file_or_throw(
        renamed_status, root_attestation_, label + " renamed identity");
    if (!same_regular_file_rename_transition(
            identity_status_, renamed_status)) {
        throw std::runtime_error(
            label + " identity inode changed across atomic rename");
    }

    FrozenSyncPosixRegularFileSnapshot frozen =
        FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
            identity_descriptor_.get(), expected_identity_.size(),
            SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " renamed identity bytes");
    if (frozen.bytes() != expected_identity_) {
        throw std::runtime_error(
            label + " renamed identity no longer binds this folder");
    }

    // The file bytes were synchronized by the pre-rename lease proof. Repeat
    // the file synchronization after the ctime transition, then make the name
    // move durable before accepting it as the new lock anchor.
    fsync_or_throw(
        identity_descriptor_.get(), label + " renamed identity");
    fsync_or_throw(
        root_descriptor_.get(), label + " identity migration directory");

    struct stat old_status {};
    int old_result;
    do {
        old_result = ::fstatat(
            root_descriptor_.get(), old_identity_basename.c_str(),
            &old_status, AT_SYMLINK_NOFOLLOW);
    } while (old_result != 0 && errno == EINTR);
    if (old_result == 0) {
        throw std::runtime_error(
            label + " legacy identity name survived atomic migration");
    }
    if (errno != ENOENT) {
        const int error = errno;
        throw std::runtime_error(
            label + " legacy identity absence proof failed: " +
            error_text(error));
    }
    verify_named_regular_file_or_throw(
        root_descriptor_.get(), new_identity_basename, renamed_status,
        root_attestation_, label + " migrated identity pathname");
    require_no_competing_store_identity_names_or_throw(
        root_descriptor_.get(), new_identity_basename,
        label + " migrated identity namespace");
    root_authority.verify_or_throw(label + " migrated root authority");

    // Only after every durable pathname proof succeeds may later lease proofs
    // follow the new basename and post-rename ctime observation.
    identity_status_ = renamed_status;
    identity_basename_ = std::move(new_identity_basename);
    verify_or_throw(root_authority, label + " rebound lease proof");
}

[[nodiscard]] bool flock_conflict_error(int error_number) noexcept {
    return error_number == EWOULDBLOCK || error_number == EAGAIN;
}

[[nodiscard]] const char* store_lease_mode_name(
    SyncReplicaFilePayloadStoreLeaseMode mode) noexcept {
    switch (mode) {
        case SyncReplicaFilePayloadStoreLeaseMode::SharedObservation:
            return "shared observation";
        case SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation:
            return "exclusive mutation";
    }
    return "unknown";
}

void acquire_flock_nonblocking_or_throw(
    int descriptor,
    int operation,
    SyncReplicaFilePayloadStoreLeaseMode mode,
    const std::string& label) {
    int result;
    do {
        result = ::flock(descriptor, operation | LOCK_NB);
    } while (result != 0 && errno == EINTR);
    if (result == 0) return;
    const int error = errno;
    if (flock_conflict_error(error)) {
        throw SyncReplicaFilePayloadStoreLeaseBusyError(
            mode,
            label + " payload-store " + store_lease_mode_name(mode) +
                " lease is busy");
    }
    throw std::runtime_error(
        label + " payload-store " + store_lease_mode_name(mode) +
        " lease acquisition failed: " + error_text(error));
}

[[nodiscard]] bool try_acquire_payload_use_flock_nonblocking_or_throw(
    int descriptor,
    int operation,
    const std::string& label) {
    if (descriptor < 0 ||
        (operation != LOCK_SH && operation != LOCK_EX)) {
        throw std::logic_error(
            label + " payload-use lease acquisition is misconfigured");
    }
    int result;
    do {
        result = ::flock(descriptor, operation | LOCK_NB);
    } while (result != 0 && errno == EINTR);
    if (result == 0) return true;
    const int error = errno;
    if (flock_conflict_error(error)) return false;
    throw std::runtime_error(
        label + " payload-use lease acquisition failed: " + error_text(error));
}

void acquire_payload_use_flock_nonblocking_or_throw(
    int descriptor,
    int operation,
    SyncReplicaFilePayloadStoreLeaseMode mode,
    const std::string& label) {
    if (try_acquire_payload_use_flock_nonblocking_or_throw(
            descriptor, operation, label)) {
        return;
    }
    throw SyncReplicaFilePayloadStoreLeaseBusyError(
        mode,
        label + " payload-use " + store_lease_mode_name(mode) +
            " lease is busy");
}

void acquire_shared_payload_use_lease_or_throw(
    int descriptor,
    const std::string& label) {
    acquire_payload_use_flock_nonblocking_or_throw(
        descriptor, LOCK_SH,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation, label);
}

void acquire_exclusive_payload_use_lease_or_throw(
    int descriptor,
    const std::string& label) {
    acquire_payload_use_flock_nonblocking_or_throw(
        descriptor, LOCK_EX,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation, label);
}

[[nodiscard]] StoreLease acquire_store_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string_view identity_basename,
    std::string_view expected_identity,
    SyncReplicaFilePayloadStoreLeaseMode mode,
    const std::string& label,
    StoreObservationDurability durability) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    root_authority.verify_or_throw(label + " root pre-lease proof");
    auto root_lease =
        Access::duplicate_shared_open_description_or_throw(
            root_authority, label + " root");
    OwnedFd root_descriptor(root_lease.release_descriptor());
    const SyncDirectoryAttestation& root_attestation =
        root_authority.attestation();

    // Preserve the explicit-bootstrap diagnostic in the observation-only lane
    // without invoking reconciliation or creating a marker. The later
    // descriptor-rooted open still owns the race-closing identity proof.
    const std::string identity_name(identity_basename);
    struct stat named_identity {};
    int identity_result;
    do {
        identity_result = ::fstatat(
            root_descriptor.get(), identity_name.c_str(), &named_identity,
            AT_SYMLINK_NOFOLLOW);
    } while (identity_result != 0 && errno == EINTR);
    if (identity_result != 0 && errno == ENOENT) {
        throw std::runtime_error(
            label +
            " payload-store identity marker is absent and requires explicit "
            "bootstrap");
    }

    VerifiedStoreIdentityFile identity =
        open_verified_store_identity_or_throw(
            root_descriptor.get(), root_authority.path(),
            root_lease.resolution_capability(), root_lease.mount_identity(),
            root_attestation, identity_basename, expected_identity,
            label + " identity lock anchor", durability);
    const int requested =
        mode == SyncReplicaFilePayloadStoreLeaseMode::SharedObservation
            ? LOCK_SH
            : LOCK_EX;
    acquire_flock_nonblocking_or_throw(
        identity.descriptor.get(), requested, mode, label);

    // A successful advisory lock is not promoted to authority until a second,
    // independently opened file description proves that the opposite lock is
    // rejected. This catches platforms/filesystems that collapse locks to
    // process ownership or otherwise fail to provide the required exclusion.
    VerifiedStoreIdentityFile conflict_probe =
        open_verified_store_identity_or_throw(
            root_descriptor.get(), root_authority.path(),
            root_lease.resolution_capability(), root_lease.mount_identity(),
            root_attestation, identity_basename, expected_identity,
            label + " independent lease conflict probe", durability);
    const int conflicting =
        mode == SyncReplicaFilePayloadStoreLeaseMode::SharedObservation
            ? LOCK_EX
            : LOCK_SH;
    int probe_result;
    do {
        probe_result = ::flock(
            conflict_probe.descriptor.get(), conflicting | LOCK_NB);
    } while (probe_result != 0 && errno == EINTR);
    if (probe_result == 0) {
        (void)::flock(conflict_probe.descriptor.get(), LOCK_UN);
        throw std::runtime_error(
            label +
            " payload-store lease exclusion self-proof unexpectedly succeeded");
    }
    const int probe_error = errno;
    if (!flock_conflict_error(probe_error)) {
        throw std::runtime_error(
            label + " payload-store lease exclusion self-proof failed: " +
            error_text(probe_error));
    }

    StoreLease lease(
        std::move(root_descriptor), std::move(identity.descriptor),
        identity.status, root_attestation, std::string(identity_basename),
        std::string(expected_identity), mode, durability);
    lease.verify_or_throw(
        root_authority, label + " identity lock anchor after exclusion proof");
    return lease;
}

[[nodiscard]] std::string snapshot_digest_or_throw(
    std::string_view folder_id,
    std::string_view root_path,
    std::string_view root_attestation_digest,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::uint64_t transient_entry_count,
    std::uint64_t transient_bytes,
    std::uint64_t transient_reserved_bytes,
    std::string_view transient_namespace_digest,
    std::uint64_t indexed_bytes,
    const std::vector<PayloadIndexEntry>& entries) {
    if (!is_lowercase_sha256_hex(transient_namespace_digest)) {
        throw std::invalid_argument(
            "durable payload snapshot transient namespace digest is invalid");
    }
    Sha256DigestBuilder digest;
    append_string(digest, kSnapshotDigestDomain);
    append_string(digest, kStoreLeaseProtocol);
    append_string(digest, folder_id);
    append_string(digest, root_path);
    append_string(digest, root_attestation_digest);
    append_string(digest, identity_basename);
    append_string(digest, sha256_hex(std::string(expected_identity)));
    append_u64(digest, limits.max_entries);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, limits.max_indexed_bytes);
    append_u64(digest, limits.max_transient_entries);
    append_u64(digest, limits.max_transient_bytes);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    append_u64(digest, indexed_bytes);
    append_u64(digest, transient_entry_count);
    append_u64(digest, transient_bytes);
    append_u64(digest, transient_reserved_bytes);
    append_string(digest, transient_namespace_digest);
    for (const PayloadIndexEntry& entry : entries) {
        append_string(digest, entry.content_sha256);
        append_u64(digest, entry.size_bytes);
    }
    return digest.finish_hex();
}

// Raw namespace traversal. The only intentionally unleased caller is clean
// identity bootstrap before a stable lock anchor exists. Every ordinary
// observation and mutation must enter through scan_store_under_lease_or_throw.
[[nodiscard]] ScannedPayloadIndex scan_store_namespace_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    bool identity_required,
    const std::string& label,
    StoreObservationDurability durability,
    const std::vector<PayloadIndexEntry>* verified_payloads,
    const struct stat* locked_identity_status,
    PayloadVerificationCache* verification_cache) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    // dup/fcntl descriptors share one open-file-description directory offset.
    // fdopendir/readdir on a duplicate would therefore mutate the retained
    // authority's cursor and make a later scan begin at end-of-directory.
    // Reopen and attest an independent root before duplicating it into DIR.
    SyncDirectoryAuthority scan_authority =
        reopen_matching_root_authority_or_throw(
            root_authority, label + " independent cursor");
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            scan_authority, label + " scan");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat directory_before{};
    if (::fstat(root_descriptor.get(), &directory_before) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " initial root fstat failed: " +
                                 error_text(error));
    }
    if (!S_ISDIR(directory_before.st_mode)) {
        throw std::runtime_error(label + " retained root is not a directory");
    }

    DIR* raw_stream = ::fdopendir(root_descriptor.get());
    if (raw_stream == nullptr) {
        const int error = errno;
        throw std::runtime_error(label + " directory stream open failed: " +
                                 error_text(error));
    }
    (void)root_descriptor.release();
    OwnedDirectoryStream stream(raw_stream);
    const int directory_descriptor = ::dirfd(stream.get());
    if (directory_descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(label + " directory stream descriptor failed: " +
                                 error_text(error));
    }

    ScannedPayloadIndex out;
    // The production owner admits 100,000 payload identities, but most stores
    // are much smaller. Do not turn that safety ceiling into an unconditional
    // multi-megabyte allocation on every scan; vector growth remains bounded by
    // max_entries as entries are actually observed.
    constexpr std::uint64_t kInitialPayloadIndexReserveEntries = 4096U;
    out.entries.reserve(static_cast<std::size_t>(
        std::min(limits.max_entries, kInitialPayloadIndexReserveEntries)));
    const SyncDirectoryAttestation& root_attestation =
        scan_authority.attestation();
    const bool read_verification_index =
        verified_payloads == nullptr && locked_identity_status != nullptr &&
        synchronizes_store_observation(durability);
    VerificationIndexFileObservation verification_index =
        observe_verification_index_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, locked_identity_status,
            read_verification_index, label + " verification index");
    out.verification_index_present = verification_index.present;
    out.verification_index_contents_requested = read_verification_index;
    out.verification_index_metadata = verification_index.metadata;
    out.verification_index_usable = verification_index.usable;
    if (verification_index.usable && verification_index.index.has_value()) {
        out.verification_index_entry_count = static_cast<std::uint64_t>(
            verification_index.index->entries.size());
        out.verification_index_indexed_bytes =
            verification_index.index->indexed_bytes;
    }
    const SyncReplicaFilePayloadVerificationIndex* durable_verified_payloads =
        verification_index.usable ? &*verification_index.index : nullptr;
    bool verification_index_seen = false;

    const bool read_scrub_state =
        locked_identity_status != nullptr &&
        synchronizes_store_observation(durability);
    ScrubStateFileObservation scrub_state = observe_scrub_state_file_or_throw(
        directory_descriptor, scan_authority.path(),
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(), root_attestation, limits,
        expected_identity, locked_identity_status, read_scrub_state,
        label + " scrub state");
    out.scrub_state_present = scrub_state.present;
    out.scrub_state_contents_requested = read_scrub_state;
    out.scrub_state_usable = scrub_state.usable;
    out.scrub_state_metadata = scrub_state.metadata;
    if (scrub_state.usable) out.scrub_state = scrub_state.state;
    bool scrub_state_seen = false;

    const bool read_retention_mark =
        locked_identity_status != nullptr &&
        synchronizes_store_observation(durability);
    RetentionMarkFileObservation retention_mark =
        observe_retention_mark_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, locked_identity_status, read_retention_mark,
            label + " retention mark");
    out.retention_mark_present = retention_mark.present;
    out.retention_mark_contents_requested = read_retention_mark;
    out.retention_mark_usable = retention_mark.usable;
    out.retention_mark_metadata = retention_mark.metadata;
    if (retention_mark.usable) {
        out.retention_mark = retention_mark.mark;
        out.retention_mark_digest = retention_mark.mark_digest;
    }
    bool retention_mark_seen = false;
    SourceManifestCheckpointFileObservation source_manifest_checkpoint =
        observe_source_manifest_checkpoint_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, locked_identity_status, false,
            label + " source manifest checkpoint");
    bool source_manifest_checkpoint_seen = false;
    // A present but unusable record is not clean absence. It can be the damaged
    // remains of Prepared/Progress, whose whole purpose is to revoke metadata
    // acceleration after a payload was selected but before its bytes were
    // completely checked. Because the damaged record cannot identify one
    // digest safely, every payload in this complete scan must prove current
    // bytes before snapshot authority can return. The later exclusive scrub
    // phase may replace the damaged record with canonical state.
    const bool unusable_scrub_state_requires_current_bytes =
        scrub_state.present && !scrub_state.usable;

    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(stream.get());
        if (entry == nullptr) {
            if (errno != 0) {
                const int error = errno;
                throw std::runtime_error(label + " directory scan failed: " +
                                         error_text(error));
            }
            break;
        }
        const std::string_view basename(entry->d_name);
        if (basename == "." || basename == "..") continue;

        if (basename == kLegacyStoreIdentityBasenameV1) {
            throw std::runtime_error(
                label +
                " refuses legacy payload-store identity generation v1; "
                "offline migration is required before lease-protected use");
        }
        const bool known_identity_name =
            payload_store_identity_basename_is_known(basename);
        if (known_identity_name && basename != identity_basename) {
            throw std::runtime_error(
                label +
                " refuses an incompatible payload-store identity generation: " +
                std::string(basename));
        }

        if (basename == identity_basename) {
            if (out.identity_present) {
                throw std::runtime_error(
                    label + " observed duplicate payload-store identity authority");
            }
            (void)open_verified_store_identity_or_throw(
                directory_descriptor, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                root_attestation, identity_basename, expected_identity,
                label + " identity marker", durability);
            out.identity_present = true;
            continue;
        }

        if (is_lowercase_sha256_hex(basename)) {
            if (out.entries.size() >= limits.max_entries) {
                throw std::length_error(
                    label + " payload entry count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " payload " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " payload " + std::string(basename));
            const std::uint64_t size_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (size_bytes > limits.max_payload_bytes) {
                throw std::length_error(
                    label + " payload exceeds configured byte budget: " +
                    std::string(basename));
            }
            if (out.indexed_bytes > limits.max_indexed_bytes ||
                size_bytes > limits.max_indexed_bytes - out.indexed_bytes) {
                throw std::length_error(
                    label + " aggregate payload bytes exceed configured budget");
            }

            const PayloadIndexEntry* process_verified =
                verified_payloads == nullptr
                    ? nullptr
                    : find_entry(*verified_payloads, basename);
            const SyncReplicaFilePayloadVerificationIndexEntry*
                durable_verified =
                    durable_verified_payloads == nullptr
                        ? nullptr
                        : find_verification_index_entry(
                              *durable_verified_payloads, basename);
            const bool scrub_failure_targets_payload =
                scrub_state.usable && scrub_state.state.has_value() &&
                scrub_state.state->disposition ==
                    SyncReplicaFilePayloadScrubStateDisposition::
                        IntegrityFailure &&
                scrub_state.state->active_content_sha256 == basename;
            const bool matching_scrub_failure =
                scrub_failure_targets_payload &&
                sync_posix_regular_file_snapshot_metadata_matches_status(
                    scrub_state.state->active_metadata, opened.status);
            const bool scrub_active_targets_payload =
                scrub_state.usable && scrub_state.state.has_value() &&
                scrub_state_is_active(*scrub_state.state) &&
                scrub_state.state->active_content_sha256 == basename;
            const bool exact_same_process_scrub_active =
                scrub_active_targets_payload &&
                verification_cache != nullptr &&
                scrub_state.metadata.has_value() &&
                process_scrub_active_observation_matches(
                    *verification_cache, *scrub_state.state,
                    *scrub_state.metadata);
            const bool process_integrity_fault_targets_payload =
                verification_cache != nullptr &&
                verification_cache->integrity_fault.has_value() &&
                verification_cache->integrity_fault
                        ->expected_digest() == basename;
            const bool current_bytes_required =
                unusable_scrub_state_requires_current_bytes ||
                matching_scrub_failure ||
                process_integrity_fault_targets_payload;
            // Neither a checksum-framed durable failure record nor a
            // process-local observed mismatch is content authority. Likewise,
            // Prepared/Progress is a write-ahead crash witness, not proof that
            // the selected bytes were good. A present but unusable state may be
            // damaged active intent whose target can no longer be recovered, so
            // it revokes acceleration for the complete namespace. A matching
            // same-process witness may reuse only the exact process cache; a
            // fresh process or a replaced state file must hash, and durable
            // checkpoint reuse is forbidden for every active target.
            const bool exact_process_observation =
                !current_bytes_required &&
                (!scrub_active_targets_payload ||
                 exact_same_process_scrub_active) &&
                process_verified != nullptr &&
                process_verified->size_bytes == size_bytes &&
                same_regular_file_observation(
                    process_verified->status, opened.status);
            const bool exact_durable_observation =
                !current_bytes_required &&
                !scrub_active_targets_payload &&
                durable_verified != nullptr &&
                durable_verified->metadata.size_bytes == size_bytes &&
                sync_posix_regular_file_snapshot_metadata_matches_status(
                    durable_verified->metadata, opened.status);
            if (exact_process_observation) {
                if (scrub_active_targets_payload &&
                    exact_same_process_scrub_active &&
                    verification_cache->scrub_active
                        ->active_current_bytes_verified) {
                    // Carry a stronger exact full-byte proof through the
                    // metadata-only process-cache reuse. This is needed when a
                    // minimum-reader identity rename rebinds the same verified
                    // generation before the ordinary scrub phase.
                    out.scrub_active_reverified_good = true;
                }
                ++out.scan_reused_entry_count;
                out.scan_reused_bytes += size_bytes;
                ++out.scan_process_reused_entry_count;
                out.scan_process_reused_bytes += size_bytes;
            } else if (exact_durable_observation) {
                ++out.scan_reused_entry_count;
                out.scan_reused_bytes += size_bytes;
                ++out.scan_durable_reused_entry_count;
                out.scan_durable_reused_bytes += size_bytes;
            } else {
                const StreamedFileDigest streamed =
                    stream_hash_regular_file_or_throw(
                        file.get(), opened.status, std::nullopt,
                        label + " payload " + std::string(basename));
                if (streamed.sha256 != basename) {
                    const bool exact_failure_witness_persisted =
                        matching_scrub_failure &&
                        scrub_state.state->observed_content_sha256 ==
                            streamed.sha256;
                    if (verification_cache != nullptr) {
                        // A second mismatch encountered before the original
                        // target must not displace an older unresolved
                        // process-local fault. The failed scan cannot publish
                        // changed metadata, so that second path remains
                        // independently hash-forcing on its next observation.
                        (void)retain_process_integrity_fault(
                            *verification_cache, basename, streamed.sha256);
                    }
                    throw SyncReplicaFilePayloadStoreIntegrityError(
                        std::string(basename), streamed.sha256,
                        exact_failure_witness_persisted,
                        label +
                            " payload bytes do not match digest basename: " +
                            std::string(basename));
                }
                if (scrub_failure_targets_payload) {
                    out.scrub_failure_reverified_good = true;
                }
                if (scrub_active_targets_payload) {
                    out.scrub_active_reverified_good = true;
                }
                if (process_integrity_fault_targets_payload) {
                    out.process_integrity_fault_reverified_good = true;
                }
                if (synchronizes_store_observation(durability)) {
                    fsync_or_throw(
                        file.get(),
                        label + " payload " + std::string(basename));
                }
                ++out.scan_hashed_entry_count;
                out.scan_hashed_bytes += size_bytes;
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " payload " + std::string(basename));
            out.entries.push_back(PayloadIndexEntry{
                std::string(basename), size_bytes, opened.status});
            out.indexed_bytes += size_bytes;
            continue;
        }

        if (basename ==
            kSyncReplicaFilePayloadVerificationIndexBasename) {
            if (!verification_index.present || verification_index_seen) {
                throw std::runtime_error(
                    label +
                    " verification index changed during namespace traversal");
            }
            verification_index_seen = true;
            continue;
        }

        if (basename == kSyncReplicaFilePayloadScrubStateBasename) {
            if (!scrub_state.present || scrub_state_seen) {
                throw std::runtime_error(
                    label +
                    " scrub state changed during namespace traversal");
            }
            scrub_state_seen = true;
            continue;
        }

        if (basename == kSyncReplicaFilePayloadRetentionMarkBasename) {
            if (!retention_mark.present || retention_mark_seen) {
                throw std::runtime_error(
                    label +
                    " retention mark changed during namespace traversal");
            }
            retention_mark_seen = true;
            continue;
        }

        if (basename == kSyncReplicaSourceManifestCheckpointBasename) {
            if (!source_manifest_checkpoint.present ||
                source_manifest_checkpoint_seen) {
                throw std::runtime_error(
                    label +
                    " source manifest checkpoint changed during namespace traversal");
            }
            source_manifest_checkpoint_seen = true;
            continue;
        }

        if (const auto parsed_terminal =
                parse_terminal_verification_basename(basename);
            parsed_terminal.has_value()) {
            if (out.terminal_verification_entry_count >=
                limits.max_transient_entries) {
                throw std::length_error(
                    label +
                    " terminal verification journal count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " terminal verification journal " +
                    std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " terminal verification journal " +
                    std::string(basename));
            if (opened.status.st_size < 0 ||
                static_cast<std::uint64_t>(opened.status.st_size) >
                    sync_replica_file_payload_terminal_verification_journal_exact_bytes()) {
                throw std::runtime_error(
                    label +
                    " terminal verification journal exceeds its fixed extent");
            }
            TerminalVerificationJournalEntry journal_entry;
            journal_entry.content_sha256 = *parsed_terminal;
            const std::uint64_t exact_journal_bytes =
                sync_replica_file_payload_terminal_verification_journal_exact_bytes();
            if (locked_identity_status != nullptr &&
                synchronizes_store_observation(durability) &&
                static_cast<std::uint64_t>(opened.status.st_size) ==
                    exact_journal_bytes) {
                FrozenSyncPosixRegularFileSnapshot frozen =
                    FrozenSyncPosixRegularFileSnapshot::
                        freeze_borrowed_descriptor_or_throw(
                            file.get(), exact_journal_bytes,
                            SyncPosixDescriptorLinkPolicy::exactly_one,
                            label + " terminal verification journal " +
                                std::string(basename) + " bytes");
                if (!frozen.matches_status(opened.status)) {
                    throw PayloadStoreObservationStaleError(
                        label +
                        " terminal verification journal changed during byte observation");
                }
                try {
                    const auto journal =
                        parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
                            frozen.bytes(), limits.max_payload_bytes,
                            label + " terminal verification journal " +
                                std::string(basename) + " contents");
                    const auto identity_metadata =
                        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                            *locked_identity_status,
                            SyncPosixDescriptorLinkPolicy::exactly_one,
                            label +
                                " terminal verification journal identity binding");
                    const std::string identity_sha256 =
                        sha256_hex(std::string(expected_identity));
                    bool usable = journal.valid_slot_count != 0U;
                    for (const auto& slot : journal.slots) {
                        if (!slot.has_value()) continue;
                        usable =
                            usable &&
                            slot->store_identity_sha256 == identity_sha256 &&
                            slot->store_identity_metadata == identity_metadata &&
                            slot->content_sha256 == *parsed_terminal &&
                            slot->total_size_bytes ==
                                journal.latest_state.total_size_bytes;
                    }
                    journal_entry.usable = usable;
                    if (usable) {
                        journal_entry.latest_state = journal.latest_state;
                    }
                } catch (const std::invalid_argument&) {
                    // A malformed or torn journal remains recognized private
                    // computation metadata. Its completed staged prefix is
                    // scheduled from offset zero after this complete scan.
                }
            }
            if (synchronizes_store_observation(durability)) {
                fsync_or_throw(
                    file.get(),
                    label + " terminal verification journal " +
                        std::string(basename));
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " terminal verification journal " +
                    std::string(basename));
            out.terminal_verification_journals.push_back(
                std::move(journal_entry));
            ++out.terminal_verification_entry_count;
            continue;
        }

        if (const auto parsed = parse_quarantine_basename(basename);
            parsed.has_value()) {
            if (out.quarantines.size() >=
                kSyncReplicaFilePayloadStoreMaxQuarantineEntries) {
                throw std::length_error(
                    label + " payload quarantine count exceeds fixed budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " payload quarantine " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " payload quarantine " + std::string(basename));
            const std::uint64_t quarantine_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            const std::uint64_t byte_limit = maximum_quarantine_bytes(limits);
            if (quarantine_bytes > limits.max_payload_bytes ||
                out.quarantine_bytes > byte_limit ||
                quarantine_bytes > byte_limit - out.quarantine_bytes) {
                throw std::length_error(
                    label + " payload quarantine bytes exceed fixed budget");
            }
            if (synchronizes_store_observation(durability)) {
                fsync_or_throw(
                    file.get(),
                    label + " payload quarantine " + std::string(basename));
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " payload quarantine " + std::string(basename));
            out.quarantines.push_back(QuarantineEntry{
                std::string(basename), parsed->expected_content_sha256,
                parsed->observed_content_sha256, quarantine_bytes,
                opened.status});
            out.quarantine_bytes += quarantine_bytes;
            continue;
        }

        if (const auto parsed = parse_staged_prefix_basename(basename);
            parsed.has_value()) {
            if (out.transient_entry_count >= limits.max_transient_entries) {
                throw std::length_error(
                    label + " staged prefix count exceeds configured budget");
            }
            if (out.transient_reserved_bytes > limits.max_transient_bytes ||
                parsed->total_size_bytes >
                    limits.max_transient_bytes -
                        out.transient_reserved_bytes) {
                throw std::length_error(
                    label + " staged prefix reservation exceeds configured budget");
            }
            StagedPrefixEntry prefix = open_staged_prefix_or_throw(
                directory_descriptor, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(), root_attestation, *parsed,
                basename, limits,
                label + " staged prefix " + std::string(basename));
            // The basename is the commit record. A longer physical file is an
            // admitted crash tail, not additional durable prefix authority.
            // Mutation reopens and truncates it before accepting another range.
            if (synchronizes_store_observation(durability) &&
                prefix.actual_size_bytes == prefix.committed_prefix_bytes) {
                SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                    directory_descriptor, basename, scan_authority.path(),
                    descriptor_lease.resolution_capability(),
                    descriptor_lease.mount_identity(),
                    label + " committed staged prefix " + std::string(basename));
                OwnedFd file(opened.descriptor);
                if (!same_regular_file_observation(prefix.status, opened.status)) {
                    throw PayloadStoreObservationStaleError(
                        label + " staged prefix changed during durability reconciliation");
                }
                fsync_or_throw(
                    file.get(),
                    label + " staged prefix " + std::string(basename));
            }
            out.staged_prefixes.push_back(std::move(prefix));
            ++out.transient_entry_count;
            out.transient_bytes +=
                out.staged_prefixes.back().actual_size_bytes;
            out.transient_reserved_bytes += parsed->total_size_bytes;
            continue;
        }

        if (const auto parsed = parse_staged_range_basename(basename);
            parsed.has_value()) {
            if (out.transient_entry_count >= limits.max_transient_entries) {
                throw std::length_error(
                    label + " staged range count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " staged range " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " staged range " + std::string(basename));
            const std::uint64_t range_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (range_bytes == 0U ||
                parsed->offset_bytes > limits.max_payload_bytes ||
                range_bytes >
                    limits.max_payload_bytes - parsed->offset_bytes) {
                throw std::length_error(
                    label + " staged range exceeds the maximum payload extent");
            }
            if (out.transient_reserved_bytes > limits.max_transient_bytes ||
                range_bytes >
                    limits.max_transient_bytes -
                        out.transient_reserved_bytes) {
                throw std::length_error(
                    label + " staged range bytes exceed configured budget");
            }
            const StreamedFileDigest streamed =
                stream_hash_regular_file_or_throw(
                    file.get(), opened.status, std::nullopt,
                    label + " staged range " + std::string(basename));
            if (streamed.sha256 != parsed->chunk_sha256) {
                throw std::runtime_error(
                    label + " staged range bytes do not match their chunk digest");
            }
            if (synchronizes_store_observation(durability)) {
                fsync_or_throw(
                    file.get(), label + " staged range " + std::string(basename));
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " staged range " + std::string(basename));
            out.staged_ranges.push_back(StagedRangeEntry{
                std::string(basename), parsed->content_sha256,
                parsed->offset_bytes, parsed->chunk_sha256, range_bytes,
                opened.status});
            ++out.transient_entry_count;
            out.transient_bytes += range_bytes;
            out.transient_reserved_bytes += range_bytes;
            continue;
        }

        if (assembly_basename_is_exact(basename)) {
            if (out.transient_entry_count >= limits.max_transient_entries) {
                throw std::length_error(
                    label + " payload assembly residue count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " payload assembly residue " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " payload assembly residue " + std::string(basename));
            const std::uint64_t residue_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (residue_bytes > limits.max_payload_bytes ||
                out.transient_reserved_bytes > limits.max_transient_bytes ||
                residue_bytes >
                    limits.max_transient_bytes -
                        out.transient_reserved_bytes) {
                throw std::length_error(
                    label + " payload assembly residue exceeds configured budget");
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " payload assembly residue " + std::string(basename));
            out.assemblies.push_back(AssemblyEntry{
                std::string(basename), residue_bytes, opened.status});
            ++out.transient_entry_count;
            out.transient_bytes += residue_bytes;
            out.transient_reserved_bytes += residue_bytes;
            continue;
        }

        if (sync_atomic_file_publication_temp_basename_is_exact(basename)) {
            if (out.transient_entry_count >= limits.max_transient_entries) {
                throw std::length_error(
                    label + " publication residue count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " publication residue " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " publication residue " + std::string(basename));
            const std::uint64_t residue_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (out.transient_reserved_bytes > limits.max_transient_bytes ||
                residue_bytes >
                    limits.max_transient_bytes -
                        out.transient_reserved_bytes) {
                throw std::length_error(
                    label +
                    " publication residue bytes exceed configured budget");
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " publication residue " + std::string(basename));
            out.publication_residues.push_back(PublicationResidueEntry{
                std::string(basename), residue_bytes, opened.status});
            ++out.transient_entry_count;
            out.transient_bytes += residue_bytes;
            out.transient_reserved_bytes += residue_bytes;
            continue;
        }

        throw std::runtime_error(
            label + " refuses unexpected payload-root entry: " +
            std::string(basename));
    }

    if (verification_index_seen != verification_index.present) {
        throw PayloadStoreObservationStaleError(
            label + " verification index changed during namespace traversal");
    }
    if (verification_index.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor,
            kSyncReplicaFilePayloadVerificationIndexBasename,
            verification_index.status, root_attestation,
            label + " verification index traversal cutpoint");
    }
    if (scrub_state_seen != scrub_state.present) {
        throw PayloadStoreObservationStaleError(
            label + " scrub state changed during namespace traversal");
    }
    if (scrub_state.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor, kSyncReplicaFilePayloadScrubStateBasename,
            scrub_state.status, root_attestation,
            label + " scrub state traversal cutpoint");
    }
    if (retention_mark_seen != retention_mark.present) {
        throw PayloadStoreObservationStaleError(
            label + " retention mark changed during namespace traversal");
    }
    if (retention_mark.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor, kSyncReplicaFilePayloadRetentionMarkBasename,
            retention_mark.status, root_attestation,
            label + " retention mark traversal cutpoint");
    }
    if (source_manifest_checkpoint_seen !=
        source_manifest_checkpoint.present) {
        throw PayloadStoreObservationStaleError(
            label +
            " source manifest checkpoint changed during namespace traversal");
    }
    if (source_manifest_checkpoint.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor,
            kSyncReplicaSourceManifestCheckpointBasename,
            source_manifest_checkpoint.status, root_attestation,
            label + " source manifest checkpoint traversal cutpoint");
    }

    std::sort(
        out.entries.begin(), out.entries.end(),
        [](const PayloadIndexEntry& left, const PayloadIndexEntry& right) {
            return left.content_sha256 < right.content_sha256;
        });
    if (std::adjacent_find(
            out.entries.begin(), out.entries.end(),
            [](const PayloadIndexEntry& left, const PayloadIndexEntry& right) {
                return left.content_sha256 == right.content_sha256;
            }) != out.entries.end()) {
        throw std::runtime_error(
            label + " observed duplicate digest namespace authority");
    }
    std::sort(
        out.staged_prefixes.begin(), out.staged_prefixes.end(),
        staged_prefix_precedes);
    for (std::size_t index = 1U; index < out.staged_prefixes.size(); ++index) {
        if (out.staged_prefixes[index - 1U].content_sha256 ==
            out.staged_prefixes[index].content_sha256) {
            throw std::runtime_error(
                label + " contains competing staged prefix owners for one content digest");
        }
    }
    std::sort(
        out.terminal_verification_journals.begin(),
        out.terminal_verification_journals.end(),
        [](const TerminalVerificationJournalEntry& left,
           const TerminalVerificationJournalEntry& right) {
            return left.content_sha256 < right.content_sha256;
        });
    for (std::size_t index = 1U;
         index < out.terminal_verification_journals.size(); ++index) {
        if (out.terminal_verification_journals[index - 1U].content_sha256 ==
            out.terminal_verification_journals[index].content_sha256) {
            throw std::runtime_error(
                label +
                " contains duplicate terminal-verification journals for one content digest");
        }
    }

    // A complete staged prefix is itself the durable restart obligation. The
    // journal contributes only a reusable hash frontier when its identity,
    // content, total size, and exact staged-inode metadata all agree. Missing,
    // torn, or stale journals conservatively restart that target at byte zero.
    out.terminal_verification_work.reserve(out.staged_prefixes.size());
    for (const StagedPrefixEntry& prefix : out.staged_prefixes) {
        if (prefix.committed_prefix_bytes != prefix.total_size_bytes ||
            prefix.actual_size_bytes != prefix.total_size_bytes) {
            continue;
        }
        std::uint64_t verified_offset_bytes = 0U;
        const auto journal = std::lower_bound(
            out.terminal_verification_journals.begin(),
            out.terminal_verification_journals.end(),
            prefix.content_sha256,
            [](const TerminalVerificationJournalEntry& candidate,
               std::string_view digest) {
                return candidate.content_sha256 < digest;
            });
        if (journal != out.terminal_verification_journals.end() &&
            journal->content_sha256 == prefix.content_sha256 &&
            journal->usable && journal->latest_state.has_value()) {
            const auto& state = *journal->latest_state;
            const auto prefix_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    prefix.status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " terminal-verification staged-prefix binding");
            if (state.total_size_bytes == prefix.total_size_bytes &&
                state.staged_prefix_metadata == prefix_metadata &&
                state.verified_offset_bytes < prefix.total_size_bytes) {
                verified_offset_bytes = state.verified_offset_bytes;
            }
        }
        out.terminal_verification_work.push_back({
            prefix.content_sha256,
            prefix.total_size_bytes,
            verified_offset_bytes,
        });
    }
    std::sort(
        out.terminal_verification_work.begin(),
        out.terminal_verification_work.end(),
        [](const auto& left, const auto& right) {
            if (left.verified_offset_bytes != right.verified_offset_bytes) {
                return left.verified_offset_bytes <
                    right.verified_offset_bytes;
            }
            return left.content_sha256 < right.content_sha256;
        });
    std::sort(
        out.staged_ranges.begin(), out.staged_ranges.end(),
        staged_range_precedes);
    for (std::size_t index = 1U; index < out.staged_ranges.size(); ++index) {
        const StagedRangeEntry& previous = out.staged_ranges[index - 1U];
        const StagedRangeEntry& current = out.staged_ranges[index];
        if (previous.content_sha256 == current.content_sha256 &&
            previous.offset_bytes == current.offset_bytes) {
            throw std::runtime_error(
                label + " contains competing staged ranges at one content offset");
        }
    }
    std::sort(
        out.assemblies.begin(), out.assemblies.end(), assembly_precedes);
    std::sort(
        out.publication_residues.begin(), out.publication_residues.end(),
        publication_residue_precedes);
    if (verification_index.usable && verification_index.index.has_value()) {
        out.verification_index_current =
            verification_index_matches_scan(*verification_index.index, out);
    }

    if (identity_required && !out.identity_present) {
        throw std::runtime_error(
            label + " payload-store identity marker is absent");
    }

    if (synchronizes_store_observation(durability)) {
        fsync_or_throw(directory_descriptor, label + " root directory");
    }
    struct stat directory_after{};
    if (::fstat(directory_descriptor, &directory_after) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " final root fstat failed: " +
                                 error_text(error));
    }
    if (!same_directory_observation(directory_before, directory_after)) {
        throw PayloadStoreObservationStaleError(
            label + " payload root changed while its index was scanned");
    }
    out.directory_status = directory_after;
    scan_authority.verify_or_throw(label + " final scan root authority");
    root_authority.verify_or_throw(label + " final retained root authority");
    return out;
}

[[nodiscard]] ScannedPayloadIndex scan_store_under_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const StoreLease& lease,
    SyncReplicaFilePayloadStoreLeaseMode required_mode,
    const std::string& label,
    StoreObservationDurability durability,
    PayloadVerificationCache* verification_cache,
    PayloadVerificationReusePolicy reuse_policy =
        PayloadVerificationReusePolicy::AllowAcceleration) {
    if (lease.mode() != required_mode) {
        throw std::logic_error(
            label + " payload-store scan received the wrong lease mode");
    }
    if (verification_cache != nullptr &&
        !synchronizes_store_observation(durability)) {
        throw std::logic_error(
            label +
            " read-only payload-store scan cannot reuse a verification cache");
    }

    lease.verify_or_throw(root_authority, label + " pre-scan lease proof");
    std::shared_ptr<const PayloadVerificationGeneration> cached_generation;
    std::vector<PayloadIndexEntry> deliberately_empty_verified_payloads;
    const std::vector<PayloadIndexEntry>* verified_payloads = nullptr;
    if (reuse_policy == PayloadVerificationReusePolicy::RequireCurrentBytes) {
        // A non-null empty process generation also suppresses durable-index
        // loading in the raw scanner. Every digest-named payload therefore
        // reaches the complete-byte hash path while the successful scan can
        // still publish one exact process generation for immediate reuse.
        verified_payloads = &deliberately_empty_verified_payloads;
    } else if (verification_cache != nullptr) {
        cached_generation = matching_verification_generation_or_none(
            *verification_cache, lease.identity_status());
        if (cached_generation != nullptr) {
            verified_payloads = &cached_generation->entries;
        }
    }
    ScannedPayloadIndex out;
    for (std::uint32_t attempt = 0U;; ++attempt) {
        try {
            out = scan_store_namespace_or_throw(
                root_authority, limits, identity_basename,
                expected_identity, true, label, durability,
                verified_payloads, &lease.identity_status(),
                verification_cache);
            break;
        } catch (const PayloadStoreObservationStaleError&) {
            // Re-prove the exact lock inode before discarding the stale
            // namespace observation. The scanner has not yet published a
            // replacement verification generation, checkpoint observation,
            // or snapshot authority, so restarting from a fresh independent
            // directory cursor is side-effect free with respect to content
            // authority. One retry absorbs a finite in-place write; repeated
            // churn remains a bounded terminal condition.
            lease.verify_or_throw(
                root_authority, label + " stale-observation lease proof");
            if (attempt + 1U >=
                kMaximumCompleteScanObservationAttempts) {
                throw;
            }
        }
    }

    // Allocate the replacement before the final authority cutpoint. A failed
    // allocation or failed scan leaves the prior exact cache intact.
    std::shared_ptr<const PayloadVerificationGeneration> verified_after;
    ProcessQuarantineInventoryObservation quarantine_inventory_after;
    if (verification_cache != nullptr) {
        auto mutable_generation =
            std::make_shared<PayloadVerificationGeneration>();
        mutable_generation->identity_status = lease.identity_status();
        mutable_generation->entries = out.entries;
        verified_after = std::move(mutable_generation);
        quarantine_inventory_after = make_process_quarantine_inventory_or_throw(
            out.quarantines, out.quarantine_bytes,
            label + " complete quarantine observation");
    }
    // The directory scan validates the marker it enumerated. This separate
    // proof binds that name back to the exact inode carrying our still-live
    // lock, closing an identical-marker replacement/split-lock frontier.
    lease.verify_or_throw(root_authority, label + " final lease proof");
    if (verification_cache != nullptr) {
        std::optional<bool> checkpoint_capacity_available;
        try {
            checkpoint_capacity_available =
                verification_index_publication_capacity_or_throw(
                    out, limits,
                    label + " verification-index capacity observation")
                    .available;
        } catch (...) {
            // Optional restart acceleration must not make an otherwise exact
            // payload scan fail. Unknown capacity remains retryable.
        }
        note_verification_checkpoint_observation(
            *verification_cache, out, checkpoint_capacity_available);
        const std::shared_ptr<const PayloadVerificationGeneration>
            retired_generation = publish_verification_generation(
                *verification_cache, std::move(verified_after));
        // Potentially large old metadata is reclaimed after the complete
        // generation replacement rather than during its pointer assignment.
        // The shared filesystem lease remains live until the caller completes
        // its surrounding observation, so this affects latency but not the
        // namespace cutpoint or cache correctness.
        (void)retired_generation;

        if (verification_cache->integrity_fault.has_value()) {
            const bool faulted_digest_present = std::any_of(
                out.entries.begin(), out.entries.end(),
                [&](const PayloadIndexEntry& entry) {
                    return entry.content_sha256 ==
                           verification_cache->integrity_fault
                               ->expected_digest();
                });
            if (faulted_digest_present &&
                !out.process_integrity_fault_reverified_good) {
                throw std::logic_error(
                    label +
                    " process-local payload integrity fault survived a "
                    "successful complete scan without current-byte reproof");
            }
            // The final lease cutpoint now proves either current good bytes or
            // absence. Only this complete scan may release the process-local
            // fail-closed witness.
            verification_cache->integrity_fault.reset();
        }
        // A complete successful scan has now proved the active target's current
        // bytes (or its absence). Retain exact same-process acceleration only
        // for the precise state-file inode/metadata instance just observed.
        note_process_scrub_state_observation(
            *verification_cache,
            out.scrub_state_usable && out.scrub_state.has_value()
                ? &*out.scrub_state
                : nullptr,
            out.scrub_state_metadata.has_value()
                ? &*out.scrub_state_metadata
                : nullptr,
            out.scrub_active_reverified_good);
        // Publish diagnostic discoverability only after every authoritative
        // cache/fault invariant above has completed. The fixed projection and
        // monotonic timestamp cannot fail after this final lease cutpoint.
        publish_process_quarantine_inventory(
            *verification_cache, quarantine_inventory_after);
    }
    return out;
}

[[nodiscard]] SyncPosixRegularFileSnapshotMetadata
publish_rebound_scrub_state_after_identity_rename_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const StoreLease& migration_lease,
    const SyncPosixRegularFileSnapshotMetadata& prior_state_metadata,
    const SyncReplicaFilePayloadScrubState& rebound_state,
    const std::string& label);

void migrate_minimum_reader_identity_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view legacy_identity_basename,
    std::string_view current_identity_basename,
    std::string_view expected_identity,
    PayloadVerificationCache& verification_cache,
    const std::string& label) {
    if (!payload_store_identity_basenames_are_supported_upgrade_pair(
            legacy_identity_basename, current_identity_basename)) {
        throw std::logic_error(
            label +
            " minimum-reader identity migration lacks an exact same-family "
            "upgrade pair");
    }

    StoreLease migration_lease = acquire_store_lease_or_throw(
        root_authority, legacy_identity_basename, expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        label + " minimum-reader migration",
        StoreObservationDurability::Reconcile);

    // The legacy reader generation can interpret Prepared as an unknown scrub
    // state and then trust stale restart metadata. Before rev0959 removes the
    // old lock-anchor name, hash every current payload byte under that exact
    // legacy inode's exclusive lease. A corruption failure leaves the legacy
    // name in place and publishes no new-reader authority.
    ScannedPayloadIndex cold = scan_store_under_lease_or_throw(
        root_authority, limits, legacy_identity_basename, expected_identity,
        migration_lease,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        label + " minimum-reader migration cold namespace proof",
        StoreObservationDurability::Reconcile, &verification_cache,
        PayloadVerificationReusePolicy::RequireCurrentBytes);

    // Prepare every allocation-backed handoff before the durable name
    // transition. Allocation failure at this point leaves the legacy reader
    // anchor untouched. A usable scrub record is rebound as well: an active or
    // repaired-failure target becomes a fresh Prepared record over the exact
    // current file observation just proved by the cold scan. Its partial hash
    // is deliberately discarded; the same-process full-byte witness lets the
    // ordinary post-migration scrub settle it without rereading bytes. A
    // present unusable record is rebuilt to canonical Idle from the same cold
    // namespace proof so it cannot force an immediate duplicate scan.
    std::optional<SyncReplicaFilePayloadScrubState> rebound_scrub_state;
    std::optional<SyncPosixRegularFileSnapshotMetadata>
        prior_scrub_state_metadata;
    bool rebound_active_current_bytes_verified = false;
    if (cold.scrub_state_usable && !cold.scrub_state.has_value()) {
        throw std::logic_error(
            label +
            " minimum-reader migration usable scrub state lacked parsed "
            "contents");
    }
    if (cold.scrub_state_present &&
        !cold.scrub_state_metadata.has_value()) {
        throw std::logic_error(
            label +
            " minimum-reader migration scrub state lacked exact metadata");
    }
    if (cold.scrub_state_usable) {
        if (cold.scrub_state->generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label +
                " minimum-reader migration scrub-state generation is "
                "exhausted");
        }
        rebound_scrub_state = *cold.scrub_state;
        prior_scrub_state_metadata = *cold.scrub_state_metadata;
        ++rebound_scrub_state->generation;

        const bool active_before = scrub_state_is_active(*rebound_scrub_state);
        const bool failure_before =
            rebound_scrub_state->disposition ==
            SyncReplicaFilePayloadScrubStateDisposition::IntegrityFailure;
        if (active_before || failure_before) {
            const PayloadIndexEntry* current_active = find_entry(
                cold.entries, rebound_scrub_state->active_content_sha256);
            const bool current_bytes_reverified =
                active_before
                    ? cold.scrub_active_reverified_good
                    : cold.scrub_failure_reverified_good;
            if (current_active == nullptr) {
                rebound_scrub_state->disposition =
                    SyncReplicaFilePayloadScrubStateDisposition::Idle;
                rebound_scrub_state->active_content_sha256.clear();
                rebound_scrub_state->active_metadata = {};
                rebound_scrub_state->active_offset_bytes = 0U;
                rebound_scrub_state->active_hash =
                    ResumableSha256{}.checkpoint();
                rebound_scrub_state->observed_content_sha256.clear();
            } else {
                if (!current_bytes_reverified) {
                    throw std::logic_error(
                        label +
                        " minimum-reader migration scrub target lacked its "
                        "complete current-byte proof");
                }
                rebound_scrub_state->disposition =
                    SyncReplicaFilePayloadScrubStateDisposition::Prepared;
                rebound_scrub_state->active_metadata =
                    sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                        current_active->status,
                        SyncPosixDescriptorLinkPolicy::exactly_one,
                        label +
                            " minimum-reader migrated scrub payload metadata");
                rebound_scrub_state->active_offset_bytes = 0U;
                rebound_scrub_state->active_hash =
                    ResumableSha256{}.checkpoint();
                rebound_scrub_state->observed_content_sha256.clear();
                rebound_active_current_bytes_verified = true;
            }
        }
    } else if (cold.scrub_state_present) {
        // The mandatory cold scan has already paid the namespace-wide proof
        // required by an unusable write-ahead record. Rebuild canonical idle
        // state as part of the same migration handoff; otherwise the first
        // ordinary snapshot would see the damaged record and repeat every
        // payload hash despite the exact process generation retained above.
        rebound_scrub_state =
            initial_sync_replica_file_payload_scrub_state_or_throw(
                sha256_hex(std::string(expected_identity)),
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    migration_lease.identity_status(),
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label +
                        " minimum-reader damaged-state identity metadata"),
                label + " minimum-reader damaged-state rebuild");
        prior_scrub_state_metadata = *cold.scrub_state_metadata;
    }

    auto rebound_generation =
        std::make_shared<PayloadVerificationGeneration>();
    rebound_generation->entries = std::move(cold.entries);

    migration_lease.rebind_identity_basename_after_atomic_rename_or_throw(
        root_authority, std::string(current_identity_basename),
        label + " minimum-reader migration");

    // rename(2) may advance the identity inode's ctime. Rebind the successful
    // cold scan to that post-rename observation without rereading payload bytes;
    // the inode, lock, identity bytes, root authority, and complete payload
    // namespace remained continuously fenced by the same lease.
    rebound_generation->identity_status = migration_lease.identity_status();
    const std::shared_ptr<const PayloadVerificationGeneration>
        retired_generation = publish_verification_generation(
            verification_cache, std::move(rebound_generation));
    (void)retired_generation;

    if (rebound_scrub_state.has_value()) {
        rebound_scrub_state->store_identity_metadata =
            sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                migration_lease.identity_status(),
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " minimum-reader migrated scrub identity metadata");
        const SyncPosixRegularFileSnapshotMetadata committed_metadata =
            publish_rebound_scrub_state_after_identity_rename_or_throw(
                root_authority, limits, expected_identity, migration_lease,
                *prior_scrub_state_metadata, *rebound_scrub_state,
                label + " minimum-reader migrated scrub state");
        note_process_scrub_state_observation(
            verification_cache, &*rebound_scrub_state,
            &committed_metadata,
            rebound_active_current_bytes_verified);
    }

    // Any durable checkpoint was framed against the pre-rename identity
    // observation. It can no longer grant restart reuse and must be replaced at
    // the next eligible ordinary checkpoint cutpoint.
    verification_cache.checkpoint.observation_known = true;
    verification_cache.checkpoint.force_checkpoint = true;
    verification_cache.checkpoint.publication_capacity_observation_known =
        false;
    verification_cache.checkpoint.publication_capacity_available = false;
    migration_lease.verify_or_throw(
        root_authority, label + " minimum-reader migration final proof");
}

struct StagedPrefixNamespaceObservation final {
    std::optional<StagedPrefixEntry> prefix;
    TerminalVerificationStateFileObservation terminal_verification;
    bool durable_payload_name_present = false;
    bool legacy_range_or_assembly_present = false;
    bool publication_residue_present = false;
};

// Lightweight receiver hot-path traversal. It validates the complete lexical
// namespace and opens only the one matching prefix owner. Unrelated immutable
// payloads are deliberately not rehashed: a full leased scan remains mandatory
// when reserving a new partial and immediately before final publication.
[[nodiscard]] StagedPrefixNamespaceObservation
observe_staged_prefix_namespace_under_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const StoreLease& lease,
    const std::string& label) {
    if (lease.mode() !=
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation) {
        throw std::logic_error(
            label + " staged-prefix observation requires an exclusive store lease");
    }
    lease.verify_or_throw(root_authority, label + " pre-observation lease proof");

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    SyncDirectoryAuthority scan_authority =
        reopen_matching_root_authority_or_throw(
            root_authority, label + " independent cursor");
    auto descriptor_lease = Access::duplicate_shared_open_description_or_throw(
        scan_authority, label + " directory scan");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat directory_before{};
    if (::fstat(root_descriptor.get(), &directory_before) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " initial root fstat failed: " + error_text(error));
    }
    if (!S_ISDIR(directory_before.st_mode)) {
        throw std::runtime_error(label + " retained root is not a directory");
    }

    DIR* raw_stream = ::fdopendir(root_descriptor.get());
    if (raw_stream == nullptr) {
        const int error = errno;
        throw std::runtime_error(
            label + " directory stream open failed: " + error_text(error));
    }
    (void)root_descriptor.release();
    OwnedDirectoryStream stream(raw_stream);
    const int directory_descriptor = ::dirfd(stream.get());
    if (directory_descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " directory stream descriptor failed: " +
            error_text(error));
    }

    StagedPrefixNamespaceObservation out;
    const SyncDirectoryAttestation& root_attestation =
        scan_authority.attestation();
    const std::string legacy_assembly =
        assembly_basename_or_throw(content_sha256);
    const VerificationIndexFileObservation verification_index =
        observe_verification_index_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, &lease.identity_status(), false,
            label + " verification index");
    bool verification_index_seen = false;
    const ScrubStateFileObservation scrub_state =
        observe_scrub_state_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, &lease.identity_status(), false,
            label + " scrub state");
    bool scrub_state_seen = false;
    const RetentionMarkFileObservation retention_mark =
        observe_retention_mark_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, &lease.identity_status(), false,
            label + " retention mark");
    bool retention_mark_seen = false;
    const SourceManifestCheckpointFileObservation source_manifest_checkpoint =
        observe_source_manifest_checkpoint_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, &lease.identity_status(), false,
            label + " source manifest checkpoint");
    bool source_manifest_checkpoint_seen = false;
    out.terminal_verification =
        observe_terminal_verification_state_file_or_throw(
            directory_descriptor, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, lease.identity_status(), content_sha256,
            total_size_bytes, true,
            label + " terminal verification");
    bool terminal_verification_seen = false;

    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(stream.get());
        if (entry == nullptr) {
            if (errno != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " directory scan failed: " + error_text(error));
            }
            break;
        }
        const std::string_view basename(entry->d_name);
        if (basename == "." || basename == "..") continue;

        if (basename == kLegacyStoreIdentityBasenameV1) {
            throw std::runtime_error(
                label +
                " refuses legacy payload-store identity generation v1; "
                "offline migration is required before lease-protected use");
        }
        const bool known_identity_name =
            payload_store_identity_basename_is_known(basename);
        if (known_identity_name) {
            if (basename != identity_basename) {
                throw std::runtime_error(
                    label +
                    " refuses an incompatible payload-store identity generation: " +
                    std::string(basename));
            }
            continue;
        }

        if (is_lowercase_sha256_hex(basename)) {
            if (basename == content_sha256) {
                out.durable_payload_name_present = true;
            }
            continue;
        }
        if (basename ==
            kSyncReplicaFilePayloadVerificationIndexBasename) {
            if (!verification_index.present || verification_index_seen) {
                throw std::runtime_error(
                    label +
                    " verification index changed during namespace traversal");
            }
            verification_index_seen = true;
            continue;
        }
        if (basename == kSyncReplicaFilePayloadScrubStateBasename) {
            if (!scrub_state.present || scrub_state_seen) {
                throw std::runtime_error(
                    label +
                    " scrub state changed during namespace traversal");
            }
            scrub_state_seen = true;
            continue;
        }
        if (basename == kSyncReplicaFilePayloadRetentionMarkBasename) {
            if (!retention_mark.present || retention_mark_seen) {
                throw std::runtime_error(
                    label +
                    " retention mark changed during namespace traversal");
            }
            retention_mark_seen = true;
            continue;
        }
        if (basename == kSyncReplicaSourceManifestCheckpointBasename) {
            if (!source_manifest_checkpoint.present ||
                source_manifest_checkpoint_seen) {
                throw std::runtime_error(
                    label +
                    " source manifest checkpoint changed during namespace traversal");
            }
            source_manifest_checkpoint_seen = true;
            continue;
        }
        if (parse_quarantine_basename(basename).has_value()) {
            continue;
        }
        if (const auto terminal_content =
                parse_terminal_verification_basename(basename);
            terminal_content.has_value()) {
            if (*terminal_content == content_sha256) {
                if (!out.terminal_verification.present ||
                    terminal_verification_seen) {
                    throw std::runtime_error(
                        label +
                        " terminal verification changed during namespace traversal");
                }
                terminal_verification_seen = true;
            }
            continue;
        }
        if (const auto parsed = parse_staged_prefix_basename(basename);
            parsed.has_value()) {
            if (parsed->content_sha256 != content_sha256) continue;
            if (parsed->total_size_bytes != total_size_bytes) {
                throw std::runtime_error(
                    label + " staged prefix total size conflicts for one content digest");
            }
            if (out.prefix.has_value()) {
                throw std::runtime_error(
                    label + " contains competing staged prefix owners for one content digest");
            }
            out.prefix = open_staged_prefix_or_throw(
                directory_descriptor, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(), root_attestation, *parsed,
                basename, limits,
                label + " staged prefix " + std::string(basename));
            continue;
        }
        if (const auto parsed = parse_staged_range_basename(basename);
            parsed.has_value()) {
            if (parsed->content_sha256 == content_sha256) {
                out.legacy_range_or_assembly_present = true;
            }
            continue;
        }
        if (assembly_basename_is_exact(basename)) {
            if (basename == legacy_assembly) {
                out.legacy_range_or_assembly_present = true;
            }
            continue;
        }
        if (sync_atomic_file_publication_temp_basename_is_exact(basename)) {
            out.publication_residue_present = true;
            continue;
        }
        throw std::runtime_error(
            label + " refuses unexpected payload-root entry: " +
            std::string(basename));
    }

    if (verification_index_seen != verification_index.present) {
        throw std::runtime_error(
            label + " verification index changed during namespace traversal");
    }
    if (verification_index.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor,
            kSyncReplicaFilePayloadVerificationIndexBasename,
            verification_index.status, root_attestation,
            label + " verification index traversal cutpoint");
    }
    if (scrub_state_seen != scrub_state.present) {
        throw std::runtime_error(
            label + " scrub state changed during namespace traversal");
    }
    if (scrub_state.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor, kSyncReplicaFilePayloadScrubStateBasename,
            scrub_state.status, root_attestation,
            label + " scrub state traversal cutpoint");
    }
    if (retention_mark_seen != retention_mark.present) {
        throw std::runtime_error(
            label + " retention mark changed during namespace traversal");
    }
    if (retention_mark.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor, kSyncReplicaFilePayloadRetentionMarkBasename,
            retention_mark.status, root_attestation,
            label + " retention mark traversal cutpoint");
    }
    if (source_manifest_checkpoint_seen !=
        source_manifest_checkpoint.present) {
        throw std::runtime_error(
            label +
            " source manifest checkpoint changed during namespace traversal");
    }
    if (source_manifest_checkpoint.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor, kSyncReplicaSourceManifestCheckpointBasename,
            source_manifest_checkpoint.status, root_attestation,
            label + " source manifest checkpoint traversal cutpoint");
    }
    if (terminal_verification_seen !=
        out.terminal_verification.present) {
        throw std::runtime_error(
            label +
            " terminal verification changed during namespace traversal");
    }
    if (out.terminal_verification.present) {
        verify_named_regular_file_or_throw(
            directory_descriptor,
            terminal_verification_basename_or_throw(content_sha256),
            out.terminal_verification.status, root_attestation,
            label + " terminal verification traversal cutpoint");
    }

    struct stat directory_after{};
    if (::fstat(directory_descriptor, &directory_after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final root fstat failed: " + error_text(error));
    }
    if (!same_directory_observation(directory_before, directory_after)) {
        throw std::runtime_error(
            label + " payload root changed during staged-prefix observation");
    }
    scan_authority.verify_or_throw(label + " final scan root authority");
    root_authority.verify_or_throw(label + " final retained root authority");
    lease.verify_or_throw(root_authority, label + " final observation lease proof");
    return out;
}

// Receiver-local terminal verification already has one exact completed-prefix
// owner and one checksum-framed journal. Re-enumerating every immutable payload
// and transient basename for each 32 MiB SHA-256 continuation makes a large
// store's computational progress proportional to unrelated namespace size.
// This targeted observer instead reopens only the exact completed prefix,
// terminal journal, and possible durable digest name beneath the same
// store-global exclusive lease. It intentionally grants no namespace-health,
// capacity, cleanup, or publication authority: every terminal completion still
// enters scan_store_under_lease_or_throw immediately before the digest-named
// rename, where unexpected entries and competing owners remain fail-closed.
[[nodiscard]] StagedPrefixNamespaceObservation
observe_staged_prefix_terminal_target_under_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const StoreLease& lease,
    const std::string& label) {
    if (lease.mode() !=
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation) {
        throw std::logic_error(
            label + " targeted terminal observation requires an exclusive store lease");
    }
    lease.verify_or_throw(
        root_authority, label + " pre-observation lease proof");

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    SyncDirectoryAuthority target_authority =
        reopen_matching_root_authority_or_throw(
            root_authority, label + " independent target root");
    auto descriptor_lease = Access::duplicate_shared_open_description_or_throw(
        target_authority, label + " exact target access");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat directory_before{};
    if (::fstat(root_descriptor.get(), &directory_before) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " initial root fstat failed: " + error_text(error));
    }
    if (!S_ISDIR(directory_before.st_mode)) {
        throw std::runtime_error(label + " retained root is not a directory");
    }

    StagedPrefixNamespaceObservation out;
    const SyncDirectoryAttestation& root_attestation =
        target_authority.attestation();
    out.terminal_verification =
        observe_terminal_verification_state_file_or_throw(
            root_descriptor.get(), target_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(), root_attestation, limits,
            expected_identity, lease.identity_status(), content_sha256,
            total_size_bytes, true,
            label + " terminal verification");

    const std::string prefix_basename = staged_prefix_basename_or_throw(
        content_sha256, total_size_bytes, total_size_bytes);
    const auto parsed_prefix = parse_staged_prefix_basename(prefix_basename);
    if (!parsed_prefix.has_value()) {
        throw std::logic_error(
            label + " canonical completed-prefix basename did not parse");
    }
    if (auto opened = open_optional_store_file_or_throw(
            root_descriptor.get(), prefix_basename, target_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(),
            label + " exact completed prefix");
        opened.has_value()) {
        OwnedFd prefix_file(opened->descriptor);
        require_private_regular_file_or_throw(
            opened->status, root_attestation,
            label + " exact completed prefix");
        if (opened->status.st_size < 0) {
            throw std::runtime_error(
                label + " exact completed prefix has a negative size");
        }
        const std::uint64_t actual_size =
            static_cast<std::uint64_t>(opened->status.st_size);
        if (actual_size != total_size_bytes) {
            throw std::runtime_error(
                label + " exact completed prefix changed size");
        }
        verify_named_regular_file_or_throw(
            root_descriptor.get(), prefix_basename, opened->status,
            root_attestation, label + " exact completed prefix");
        out.prefix = StagedPrefixEntry{
            prefix_basename, parsed_prefix->content_sha256,
            parsed_prefix->total_size_bytes,
            parsed_prefix->committed_prefix_bytes, actual_size,
            opened->status};
    }

    if (auto opened = open_optional_store_file_or_throw(
            root_descriptor.get(), content_sha256, target_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(),
            label + " exact durable payload name");
        opened.has_value()) {
        OwnedFd durable_file(opened->descriptor);
        require_private_regular_file_or_throw(
            opened->status, root_attestation,
            label + " exact durable payload name");
        if (opened->status.st_size < 0 ||
            static_cast<std::uint64_t>(opened->status.st_size) !=
                total_size_bytes) {
            throw std::runtime_error(
                label + " exact durable payload size conflicts with terminal continuation");
        }
        verify_named_regular_file_or_throw(
            root_descriptor.get(), content_sha256, opened->status,
            root_attestation, label + " exact durable payload name");
        out.durable_payload_name_present = true;
    }

    struct stat directory_after{};
    if (::fstat(root_descriptor.get(), &directory_after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final root fstat failed: " + error_text(error));
    }
    if (!same_directory_observation(directory_before, directory_after)) {
        throw PayloadStoreObservationStaleError(
            label + " payload root changed during exact terminal observation");
    }
    target_authority.verify_or_throw(label + " final target root authority");
    root_authority.verify_or_throw(label + " final retained root authority");
    lease.verify_or_throw(
        root_authority, label + " final observation lease proof");
    return out;
}

void ensure_store_identity_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view legacy_identity_basename,
    std::string_view expected_identity,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    bool allow_existing_payload_adoption,
    PayloadVerificationCache& verification_cache,
    const std::string& label) {
    if (!payload_store_identity_basenames_are_supported_upgrade_pair(
            legacy_identity_basename, identity_basename)) {
        throw std::logic_error(
            label +
            " payload-store identity generations are not one exact "
            "same-family upgrade pair");
    }

    const std::string expected(expected_identity);
    auto reconcile = [&](std::string_view basename,
                         std::string_view phase) {
        return reconcile_sync_immutable_file_create_new_under_directory_or_throw(
            root_authority, fs::path(basename), byte_span(expected),
            label + " " + std::string(phase));
    };

    const SyncImmutableFileReconciliationOutcome current = reconcile(
        identity_basename, "minimum-reader identity reconciliation");
    if (current ==
        SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        throw std::runtime_error(
            label + " identity marker conflicts with the requested folder");
    }
    if (current ==
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        const SyncImmutableFileReconciliationOutcome legacy = reconcile(
            legacy_identity_basename,
            "legacy-reader identity absence reconciliation");
        if (legacy != SyncImmutableFileReconciliationOutcome::Absent) {
            throw std::runtime_error(
                label +
                " refuses coexisting current and legacy-reader payload-store "
                "identity markers");
        }
        return;
    }

    const SyncImmutableFileReconciliationOutcome legacy = reconcile(
        legacy_identity_basename,
        "legacy-reader identity reconciliation");
    if (legacy ==
        SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        throw std::runtime_error(
            label +
            " legacy-reader identity marker conflicts with the requested "
            "folder");
    }
    if (legacy ==
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        migrate_minimum_reader_identity_or_throw(
            root_authority, limits, legacy_identity_basename,
            identity_basename, expected, verification_cache, label);
        const SyncImmutableFileReconciliationOutcome migrated_current =
            reconcile(
                identity_basename,
                "migrated minimum-reader identity reconciliation");
        const SyncImmutableFileReconciliationOutcome migrated_legacy =
            reconcile(
                legacy_identity_basename,
                "migrated legacy-reader identity absence reconciliation");
        if (migrated_current !=
                SyncImmutableFileReconciliationOutcome::
                    ExactAndDirectorySynced ||
            migrated_legacy !=
                SyncImmutableFileReconciliationOutcome::Absent) {
            throw std::runtime_error(
                label +
                " minimum-reader identity migration did not settle to one "
                "durable current marker");
        }
        return;
    }

    if (disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly) {
        throw std::runtime_error(
            label +
            " payload-store identity marker is absent and requires explicit "
            "bootstrap");
    }

    // Bootstrap is mutation-free until the complete pre-existing namespace is
    // validated. This permits adoption of exact digest-named payloads while an
    // unknown, malformed, linked, over-budget, or legacy-reader identity entry
    // cannot gain a current marker merely by invoking the constructor or
    // snapshot API.
    const ScannedPayloadIndex bootstrap = scan_store_namespace_or_throw(
        root_authority, limits, identity_basename, expected, false,
        label + " identity bootstrap preflight",
        StoreObservationDurability::Reconcile, nullptr, nullptr, nullptr);
    // Quarantine names are diagnostic evidence from an already identified
    // store. They never participate in ordinary payload adoption: without an
    // identity marker there is no authenticated folder/store generation that
    // can explain or own those retained bytes. This rejection is intentionally
    // outside the standalone payload-adoption exception.
    if (!bootstrap.quarantines.empty()) {
        throw std::runtime_error(
            label +
            " fresh bootstrap refuses pre-existing payload quarantine "
            "evidence");
    }
    if (!allow_existing_payload_adoption &&
        (!bootstrap.entries.empty() ||
         bootstrap.transient_entry_count != 0U ||
         bootstrap.transient_bytes != 0U ||
         bootstrap.terminal_verification_entry_count != 0U ||
         bootstrap.verification_index_present ||
         bootstrap.scrub_state_present ||
         bootstrap.retention_mark_present)) {
        throw std::runtime_error(
            label +
            " product-bound bootstrap refuses adoption of pre-existing "
            "payload-root entries");
    }
    if (bootstrap.identity_present) {
        const SyncImmutableFileReconciliationOutcome raced = reconcile(
            identity_basename, "raced identity reconciliation");
        if (raced ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            return;
        }
        throw std::runtime_error(
            label + " identity marker changed during bootstrap");
    }

    try {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            root_authority, fs::path(identity_basename),
            byte_span(expected), label + " identity publication");
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        const SyncImmutableFileReconciliationOutcome raced = reconcile(
            identity_basename, "identity publication reconciliation");
        if (raced ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            return;
        }
        if (raced ==
            SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
            throw std::runtime_error(
                label +
                " identity publication raced with a conflicting folder "
                "binding");
        }
        std::rethrow_exception(original);
    }

    const SyncImmutableFileReconciliationOutcome published = reconcile(
        identity_basename, "published identity reconciliation");
    if (published !=
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        throw std::runtime_error(
            label + " identity publication did not become durable and exact");
    }
}

void validate_targeted_payload_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::string_view expected_folder_id,
    const SyncReplicaFilePayloadStoreLimits& limits,
    const std::string& label) {
    if (operation.folder_id != expected_folder_id) {
        throw std::invalid_argument(
            label + " operation belongs to another folder");
    }
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(label + " requires a file operation");
    }
    if (!is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            label + " operation content digest is invalid");
    }
    if (operation.size_bytes > limits.max_payload_bytes) {
        throw std::length_error(
            label + " operation exceeds the durable payload budget");
    }
}

// One descriptor-rooted observation of exactly one digest name beneath a
// pass-scoped targeted-access root. The per-call shared lease remains live
// through synchronization, metadata capture, and final name/lock proofs, while
// the expensive identity reconciliation and root selection stay amortized by
// the caller-owned access capability. Absence is returned only after the same
// final root/lease cutpoint; no unrelated payload-root entry is enumerated or
// read. The returned descriptor is intentionally not hashed here: the atomic
// publication owner verifies SHA-256 while consuming it, avoiding a duplicate
// whole-file read.
struct TargetedPayloadObservation final {
    StoreLease observation_lease;
    OwnedFd payload_descriptor;
    struct stat payload_status {};
    StoreObservationDurability payload_durability =
        StoreObservationDurability::Reconcile;
};

[[nodiscard]] std::optional<TargetedPayloadObservation>
open_targeted_payload_observation_or_throw(
    const SyncDirectoryAuthority& targeted_root_authority,
    int targeted_root_descriptor,
    SyncPosixDirectoryResolutionCapability resolution_capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_folder_id,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const struct stat& expected_identity_status,
    StoreObservationDurability payload_durability,
    const SyncReplicaOperation& operation,
    const std::string& label) {
    validate_targeted_payload_operation_or_throw(
        operation, expected_folder_id, limits, label);
    if (targeted_root_descriptor < 0) {
        throw std::logic_error(
            label + " targeted payload root descriptor is inactive");
    }
    targeted_root_authority.verify_or_throw(label + " root pre-open proof");
    StoreLease observation_lease = acquire_store_lease_or_throw(
        targeted_root_authority, identity_basename, expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        label + " selection", StoreObservationDurability::ObserveOnly);
    if (!same_regular_file_observation(
            observation_lease.identity_status(), expected_identity_status)) {
        throw std::runtime_error(
            label +
            " payload-store identity changed after targeted-access preflight");
    }
    std::optional<SyncPosixOpenedRegularFile> opened =
        open_optional_store_file_or_throw(
            targeted_root_descriptor, operation.content_sha256,
            targeted_root_authority.path(), resolution_capability,
            mount_identity, label + " selected payload");
    if (!opened.has_value()) {
        observation_lease.verify_or_throw(
            targeted_root_authority,
            label + " absent payload lease cutpoint");
        targeted_root_authority.verify_or_throw(
            label + " absent payload root proof");
        return std::nullopt;
    }

    OwnedFd payload_descriptor(opened->descriptor);
    require_private_regular_file_or_throw(
        opened->status, targeted_root_authority.attestation(),
        label + " selected payload");
    if (static_cast<std::uint64_t>(opened->status.st_size) !=
        operation.size_bytes) {
        throw std::runtime_error(
            label + " selected payload size disagrees with the operation");
    }
    verify_named_regular_file_or_throw(
        targeted_root_descriptor, operation.content_sha256, opened->status,
        targeted_root_authority.attestation(), label + " selected payload");
    observation_lease.verify_or_throw(
        targeted_root_authority,
        label + " selected payload lease cutpoint");
    targeted_root_authority.verify_or_throw(
        label + " selected payload root proof");

    return TargetedPayloadObservation{
        std::move(observation_lease), std::move(payload_descriptor),
        opened->status, payload_durability};
}

[[nodiscard]] const PayloadIndexEntry* find_entry(
    const std::vector<PayloadIndexEntry>& entries,
    std::string_view digest) noexcept {
    const auto found = std::lower_bound(
        entries.begin(), entries.end(), digest,
        [](const PayloadIndexEntry& entry, std::string_view value) {
            return entry.content_sha256 < value;
        });
    if (found == entries.end() || found->content_sha256 != digest) {
        return nullptr;
    }
    return &*found;
}

[[nodiscard]] SyncReplicaFilePayloadVerificationIndex
make_verification_index_or_throw(
    const ScannedPayloadIndex& scanned,
    std::string_view expected_identity,
    const struct stat& identity_status,
    const std::string& label) {
    SyncReplicaFilePayloadVerificationIndex out;
    out.store_identity_sha256 = sha256_hex(std::string(expected_identity));
    out.store_identity_metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            identity_status, SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " identity metadata");
    out.indexed_bytes = scanned.indexed_bytes;
    out.entries.reserve(scanned.entries.size());
    for (const PayloadIndexEntry& entry : scanned.entries) {
        out.entries.push_back(
            SyncReplicaFilePayloadVerificationIndexEntry{
                entry.content_sha256,
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    entry.status, SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " payload metadata")});
    }
    return out;
}

enum class VerificationIndexPublicationDisposition : std::uint8_t {
    AlreadyCurrent = 1U,
    Published = 2U,
    SkippedTransientCapacity = 3U,
};

VerificationIndexPublicationCapacity
verification_index_publication_capacity_or_throw(
    const ScannedPayloadIndex& scanned,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view label) {
    VerificationIndexPublicationCapacity out;
    out.encoded_bytes =
        sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
            size_to_u64_or_throw(
                scanned.entries.size(),
                std::string(label) + " entry count"),
            std::string(label) + " exact encoded size");
    out.available =
        scanned.transient_entry_count < limits.max_transient_entries &&
        scanned.transient_reserved_bytes <= limits.max_transient_bytes &&
        out.encoded_bytes <=
            limits.max_transient_bytes - scanned.transient_reserved_bytes;
    return out;
}

// Publishes only after a complete authoritative scan and only when a crash
// residue of the metadata writer itself remains admissible under the store's
// existing transient budget. Acceleration must never consume capacity needed
// by the payload protocol or make an otherwise valid store unrecoverable.
[[nodiscard]] VerificationIndexPublicationDisposition
publish_verification_index_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const struct stat& identity_status,
    const ScannedPayloadIndex& scanned,
    const std::string& label) {
    if (scanned.verification_index_current) {
        return VerificationIndexPublicationDisposition::AlreadyCurrent;
    }

    // The v1 record is fixed-width, so its exact encoded size is known from
    // the entry count. Apply the non-authoritative transient-capacity fence
    // before constructing and serializing an O(namespace) checkpoint; a store
    // that cannot admit the writer residue must not pay a large doomed
    // allocation on every ordinary snapshot.
    const VerificationIndexPublicationCapacity capacity =
        verification_index_publication_capacity_or_throw(
            scanned, limits, label + " capacity preflight");
    if (!capacity.available) {
        return VerificationIndexPublicationDisposition::
            SkippedTransientCapacity;
    }

    const SyncReplicaFilePayloadVerificationIndex index =
        make_verification_index_or_throw(
            scanned, expected_identity, identity_status, label);
    const std::string encoded =
        serialize_sync_replica_file_payload_verification_index_or_throw(
            index, limits.max_entries, limits.max_indexed_bytes, label);
    if (size_to_u64_or_throw(encoded.size(), label + " encoded bytes") !=
        capacity.encoded_bytes) {
        throw std::logic_error(
            label + " verification index exact-size preflight drifted");
    }

    if (scanned.verification_index_present) {
        if (!scanned.verification_index_metadata.has_value()) {
            throw std::logic_error(
                label + " present verification index lacks exact metadata");
        }
        write_sync_file_atomically_replace_expected_under_directory_or_throw(
            root_authority,
            fs::path(kSyncReplicaFilePayloadVerificationIndexBasename),
            byte_span(encoded), *scanned.verification_index_metadata, label);
    } else {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            root_authority,
            fs::path(kSyncReplicaFilePayloadVerificationIndexBasename),
            byte_span(encoded), label);
    }
    return VerificationIndexPublicationDisposition::Published;
}

void note_verification_checkpoint_publication_disposition(
    PayloadVerificationCache& cache,
    const ScannedPayloadIndex& scanned,
    VerificationIndexPublicationDisposition disposition) noexcept {
    if (disposition == VerificationIndexPublicationDisposition::
                           SkippedTransientCapacity) {
        note_verification_checkpoint_capacity_deferred(cache);
        return;
    }
    note_verification_checkpoint_published(cache, scanned);
}

void require_new_payload_retention_capacity_or_throw(
    const ScannedPayloadIndex& index,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::uint64_t size_bytes,
    const std::string& label) {
    if (index.entries.size() >= limits.max_entries) {
        throw std::length_error(
            label + " payload entry count is at configured capacity");
    }
    if (index.indexed_bytes > limits.max_indexed_bytes ||
        size_bytes > limits.max_indexed_bytes - index.indexed_bytes) {
        throw std::length_error(
            label + " aggregate payload bytes exceed configured budget");
    }
}

void require_new_payload_publication_capacity_or_throw(
    const ScannedPayloadIndex& index,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::uint64_t size_bytes,
    const std::string& label) {
    require_new_payload_retention_capacity_or_throw(
        index, limits, size_bytes, label);
    if (index.transient_entry_count >= limits.max_transient_entries) {
        throw std::length_error(
            label + " publication residue count is at configured capacity");
    }
    if (index.transient_reserved_bytes > limits.max_transient_bytes ||
        size_bytes >
            limits.max_transient_bytes - index.transient_reserved_bytes) {
        throw std::length_error(
            label +
            " publication residue bytes cannot admit one bounded writer");
    }
}

[[nodiscard]] PayloadIndexEntry
observe_exact_published_payload_without_rehash_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string_view content_sha256,
    std::uint64_t expected_size_bytes,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            label + " published payload digest is invalid");
    }
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    root_authority.verify_or_throw(label + " root pre-observation proof");
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            root_authority, label + " root");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), content_sha256, root_authority.path(),
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(), label + " payload");
    OwnedFd payload_descriptor(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_authority.attestation(), label + " payload");
    const std::uint64_t observed_size =
        static_cast<std::uint64_t>(opened.status.st_size);
    if (observed_size != expected_size_bytes) {
        throw std::runtime_error(
            label + " published payload has an unexpected extent");
    }
    verify_named_regular_file_or_throw(
        root_descriptor.get(), content_sha256, opened.status,
        root_authority.attestation(), label + " payload");
    root_authority.verify_or_throw(label + " root final observation proof");
    return PayloadIndexEntry{
        std::string(content_sha256), expected_size_bytes, opened.status};
}

void insert_payload_index_entry_or_throw(
    ScannedPayloadIndex& index,
    PayloadIndexEntry entry,
    const SyncReplicaFilePayloadStoreLimits& limits,
    const std::string& label) {
    const auto found = std::lower_bound(
        index.entries.begin(), index.entries.end(), entry.content_sha256,
        [](const PayloadIndexEntry& retained, std::string_view digest) {
            return retained.content_sha256 < digest;
        });
    if (found != index.entries.end() &&
        found->content_sha256 == entry.content_sha256) {
        throw std::logic_error(
            label + " attempted to insert a duplicate payload index entry");
    }
    require_new_payload_retention_capacity_or_throw(
        index, limits, entry.size_bytes, label);
    index.indexed_bytes += entry.size_bytes;
    index.entries.insert(found, std::move(entry));
    // The durable verification checkpoint described the pre-insertion payload
    // set. Even though the newly published payload has already been completely
    // hashed, the old checkpoint cannot remain classified as current.
    index.verification_index_current = false;
}

struct StagedPrefix final {
    std::vector<const StagedRangeEntry*> ranges;
    std::uint64_t next_offset_bytes = 0U;
};

[[nodiscard]] StagedPrefix staged_prefix_for_content_or_throw(
    const ScannedPayloadIndex& scanned,
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const std::string& label) {
    StagedPrefix out;
    for (const StagedRangeEntry& entry : scanned.staged_ranges) {
        if (entry.content_sha256 != content_sha256) continue;
        if (entry.offset_bytes != out.next_offset_bytes) {
            throw std::runtime_error(
                label + " staged ranges are not one contiguous prefix");
        }
        if (entry.size_bytes == 0U ||
            entry.offset_bytes > total_size_bytes ||
            entry.size_bytes > total_size_bytes - entry.offset_bytes) {
            throw std::runtime_error(
                label + " staged range is outside the claimed payload extent");
        }
        out.ranges.push_back(&entry);
        out.next_offset_bytes += entry.size_bytes;
    }
    return out;
}

[[nodiscard]] const StagedRangeEntry* staged_range_at_offset_or_none(
    const ScannedPayloadIndex& scanned,
    std::string_view content_sha256,
    std::uint64_t offset_bytes) noexcept {
    for (const StagedRangeEntry& entry : scanned.staged_ranges) {
        if (entry.content_sha256 == content_sha256 &&
            entry.offset_bytes == offset_bytes) {
            return &entry;
        }
    }
    return nullptr;
}

[[nodiscard]] const StagedPrefixEntry* staged_prefix_for_content_or_none(
    const ScannedPayloadIndex& scanned,
    std::string_view content_sha256) noexcept {
    for (const StagedPrefixEntry& entry : scanned.staged_prefixes) {
        if (entry.content_sha256 == content_sha256) return &entry;
    }
    return nullptr;
}

struct QuarantineNamespaceObservation final {
    ProcessQuarantineInventoryObservation inventory;
    std::optional<struct stat> exact_destination_status;
};

// Quarantine must remain available while the ordinary complete scanner is
// intentionally fail-closed on the corrupt digest. This narrow traversal
// validates the complete lexical root and opens every retained quarantine, but
// does not hash unrelated authoritative payloads or grant snapshot authority.
[[nodiscard]] QuarantineNamespaceObservation
observe_quarantine_namespace_under_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    const StoreLease& lease,
    std::string_view exact_destination_basename,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    SyncDirectoryAuthority scan_authority =
        reopen_matching_root_authority_or_throw(
            root_authority, label + " independent cursor");
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            scan_authority, label + " scan");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat directory_before{};
    if (::fstat(root_descriptor.get(), &directory_before) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " initial root fstat failed: " + error_text(error));
    }
    DIR* raw_stream = ::fdopendir(root_descriptor.get());
    if (raw_stream == nullptr) {
        const int error = errno;
        throw std::runtime_error(
            label + " directory stream open failed: " + error_text(error));
    }
    (void)root_descriptor.release();
    OwnedDirectoryStream stream(raw_stream);
    const int directory_descriptor = ::dirfd(stream.get());
    if (directory_descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " directory stream descriptor failed: " +
            error_text(error));
    }

    const SyncDirectoryAttestation& root_attestation =
        scan_authority.attestation();
    QuarantineNamespaceObservation out;
    bool identity_seen = false;
    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(stream.get());
        if (entry == nullptr) {
            if (errno != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " directory scan failed: " + error_text(error));
            }
            break;
        }
        const std::string_view basename(entry->d_name);
        if (basename == "." || basename == "..") continue;

        if (basename == identity_basename) {
            if (identity_seen) {
                throw std::runtime_error(
                    label + " observed duplicate identity authority");
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, lease.identity_status(),
                root_attestation, label + " identity marker");
            identity_seen = true;
            continue;
        }
        if (payload_store_identity_basename_is_known(basename)) {
            throw std::runtime_error(
                label + " refuses a competing payload-store identity: " +
                std::string(basename));
        }
        if (is_lowercase_sha256_hex(basename) ||
            basename == kSyncReplicaFilePayloadVerificationIndexBasename ||
            basename == kSyncReplicaFilePayloadScrubStateBasename ||
            basename == kSyncReplicaFilePayloadRetentionMarkBasename ||
            basename == kSyncReplicaSourceManifestCheckpointBasename ||
            parse_staged_prefix_basename(basename).has_value() ||
            parse_terminal_verification_basename(basename).has_value() ||
            parse_staged_range_basename(basename).has_value() ||
            assembly_basename_is_exact(basename) ||
            sync_atomic_file_publication_temp_basename_is_exact(basename)) {
            continue;
        }
        const auto quarantine = parse_quarantine_basename(basename);
        if (!quarantine.has_value()) {
            throw std::runtime_error(
                label + " refuses unexpected payload-root entry: " +
                std::string(basename));
        }
        if (out.inventory.entry_count >=
            kSyncReplicaFilePayloadStoreMaxQuarantineEntries) {
            throw std::length_error(
                label + " payload quarantine count exceeds fixed budget");
        }
        SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
            directory_descriptor, basename, scan_authority.path(),
            descriptor_lease.resolution_capability(),
            descriptor_lease.mount_identity(),
            label + " retained quarantine " + std::string(basename));
        OwnedFd file(opened.descriptor);
        require_private_regular_file_or_throw(
            opened.status, root_attestation,
            label + " retained quarantine " + std::string(basename));
        const std::uint64_t size_bytes =
            static_cast<std::uint64_t>(opened.status.st_size);
        const std::uint64_t byte_limit = maximum_quarantine_bytes(limits);
        if (size_bytes > limits.max_payload_bytes ||
            out.inventory.total_bytes > byte_limit ||
            size_bytes > byte_limit - out.inventory.total_bytes) {
            throw std::length_error(
                label + " payload quarantine bytes exceed fixed budget");
        }
        verify_named_regular_file_or_throw(
            directory_descriptor, basename, opened.status, root_attestation,
            label + " retained quarantine " + std::string(basename));
        append_process_quarantine_inventory_entry_or_throw(
            out.inventory, quarantine->expected_content_sha256,
            quarantine->observed_content_sha256, size_bytes, label);
        if (basename == exact_destination_basename) {
            if (out.exact_destination_status.has_value()) {
                throw std::runtime_error(
                    label + " observed duplicate exact quarantine name");
            }
            out.exact_destination_status = opened.status;
        }
    }
    if (!identity_seen) {
        throw PayloadStoreObservationStaleError(
            label + " identity marker disappeared during traversal");
    }
    struct stat directory_after{};
    if (::fstat(directory_descriptor, &directory_after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final root fstat failed: " + error_text(error));
    }
    if (!same_directory_observation(directory_before, directory_after)) {
        throw PayloadStoreObservationStaleError(
            label + " payload root changed during quarantine observation");
    }
    sort_process_quarantine_inventory(out.inventory);
    scan_authority.verify_or_throw(label + " final scan root authority");
    root_authority.verify_or_throw(label + " final retained root authority");
    lease.verify_or_throw(root_authority, label + " final lease proof");
    return out;
}

}  // namespace

bool sync_replica_file_payload_store_range_basename_is_exact(
    std::string_view basename) {
    return parse_staged_range_basename(basename).has_value();
}

bool sync_replica_file_payload_store_prefix_basename_is_exact(
    std::string_view basename) {
    return parse_staged_prefix_basename(basename).has_value();
}

bool sync_replica_file_payload_store_terminal_verification_basename_is_exact(
    std::string_view basename) {
    return parse_terminal_verification_basename(basename).has_value();
}

std::string_view
sync_replica_file_payload_store_terminal_verification_step_disposition_name(
    SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition
        disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                ObservationUnknown:
            return "observation_unknown";
        case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                NoPendingWork:
            return "no_pending_work";
        case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                Progress:
            return "progress";
        case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                CompletedInserted:
            return "completed_inserted";
        case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                CompletedAlreadyPresent:
            return "completed_already_present";
    }
    return "unknown";
}

bool sync_replica_file_payload_store_quarantine_basename_is_exact(
    std::string_view basename) {
    return parse_quarantine_basename(basename).has_value();
}

std::string_view sync_replica_file_payload_store_quarantine_action_name(
    SyncReplicaFilePayloadStoreQuarantineAction action) noexcept {
    switch (action) {
        case SyncReplicaFilePayloadStoreQuarantineAction::Preserve:
            return "preserve";
        case SyncReplicaFilePayloadStoreQuarantineAction::Release:
            return "release";
    }
    return "unknown";
}

std::string_view sync_replica_file_payload_store_quarantine_disposition_name(
    SyncReplicaFilePayloadStoreQuarantineDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFilePayloadStoreQuarantineDisposition::Quarantined:
            return "quarantined";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ActiveFaultMismatch:
            return "active_fault_mismatch";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::PayloadAbsent:
            return "payload_absent";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                PayloadAlreadyRepaired:
            return "payload_already_repaired";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ObservedDigestChanged:
            return "observed_digest_changed";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ExactQuarantineAlreadyPresent:
            return "exact_quarantine_already_present";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                EntryCapacityExceeded:
            return "entry_capacity_exceeded";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ByteCapacityExceeded:
            return "byte_capacity_exceeded";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::Released:
            return "released";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ExactQuarantineAbsent:
            return "exact_quarantine_absent";
        case SyncReplicaFilePayloadStoreQuarantineDisposition::
                ActiveFaultPresent:
            return "active_fault_present";
    }
    return "unknown";
}

struct SyncReplicaFilePayloadStoreContentDefinedProjection::State final {
    State(
        std::string content_sha256_value,
        SyncPosixRegularFileSnapshotMetadata metadata_value,
        SyncReplicaContentDefinedChunkingParameters parameters_value,
        const std::string& label)
        : content_sha256(std::move(content_sha256_value)),
          metadata(metadata_value),
          parameters(parameters_value),
          accumulator(metadata.size_bytes, parameters, label) {}

    State(
        SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint
            checkpoint,
        const std::string& label)
        : content_sha256(checkpoint.content_sha256),
          metadata(checkpoint.metadata),
          parameters(checkpoint.parameters),
          accumulator(
              checkpoint.total_size_bytes, checkpoint.parameters,
              std::move(checkpoint), label) {}

    std::string content_sha256;
    SyncPosixRegularFileSnapshotMetadata metadata;
    SyncReplicaContentDefinedChunkingParameters parameters;
    ContentDefinedDigestAccumulator accumulator;
};

struct SyncReplicaFilePayloadStoreOpenedPayload::State final {
    PayloadStoreLiveCapabilityRegistration live_capability_registration;
    int descriptor = -1;
    struct stat status {};
    SyncPosixRegularFileSnapshotMetadata metadata;
    std::string content_sha256;
    std::shared_ptr<PayloadVerificationCache> verification_cache;

    ~State() noexcept {
        if (descriptor >= 0) (void)::close(descriptor);
    }
};

struct SyncReplicaFilePayloadStoreTargetedAccess::State final {
    State(
        std::string folder_id_value,
        SyncReplicaFilePayloadStoreLimits limits_value,
        SyncDirectoryAuthority root_authority_value,
        std::string identity_basename_value,
        std::string expected_identity_value,
        struct stat identity_status_value,
        StoreObservationDurability durability_value,
        OwnedFd root_descriptor_value,
        SyncPosixDirectoryResolutionCapability resolution_capability_value,
        SyncPosixMountIdentity mount_identity_value,
        std::shared_ptr<PayloadVerificationCache> verification_cache_value,
        std::shared_ptr<PayloadStoreLiveCapabilityRegistry>
            live_capability_registry_value)
        : live_capability_registration(
              std::move(live_capability_registry_value),
              PayloadStoreLiveCapabilityKind::TargetedAccess),
          folder_id(std::move(folder_id_value)),
          limits(limits_value),
          root_authority(std::move(root_authority_value)),
          identity_basename(std::move(identity_basename_value)),
          expected_identity(std::move(expected_identity_value)),
          identity_status(identity_status_value),
          durability(durability_value),
          root_descriptor(std::move(root_descriptor_value)),
          resolution_capability(resolution_capability_value),
          mount_identity(std::move(mount_identity_value)),
          verification_cache(std::move(verification_cache_value)) {}

    PayloadStoreLiveCapabilityRegistration live_capability_registration;
    std::string folder_id;
    SyncReplicaFilePayloadStoreLimits limits;
    SyncDirectoryAuthority root_authority;
    std::string identity_basename;
    std::string expected_identity;
    struct stat identity_status {};
    StoreObservationDurability durability =
        StoreObservationDurability::Reconcile;
    OwnedFd root_descriptor;
    SyncPosixDirectoryResolutionCapability resolution_capability =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity mount_identity;
    std::shared_ptr<PayloadVerificationCache> verification_cache;
};

struct SyncReplicaFilePayloadStoreSnapshot::State final {
    PayloadStoreLiveCapabilityRegistration live_capability_registration;
    std::string folder_id;
    fs::path root_path;
    SyncDirectoryAuthority root_authority;
    // Present only for the private retention planner. The exact identity-marker
    // EX flock outlives the complete namespace scan and every causal/inode probe
    // performed by the folder owner, then releases automatically with this
    // snapshot. It is deliberately not exposed through ordinary snapshot APIs.
    std::unique_ptr<StoreLease> retained_writer_fence;
    std::string identity_basename;
    std::string expected_identity;
    StoreObservationDurability durability =
        StoreObservationDurability::Reconcile;
    SyncReplicaFilePayloadStoreLimits limits;
    std::vector<PayloadIndexEntry> entries;
    SyncReplicaFileContentInventory content_inventory;
    std::uint64_t indexed_bytes = 0U;
    std::uint64_t scan_hashed_entry_count = 0U;
    std::uint64_t scan_hashed_bytes = 0U;
    std::uint64_t scan_reused_entry_count = 0U;
    std::uint64_t scan_reused_bytes = 0U;
    std::uint64_t scan_process_reused_entry_count = 0U;
    std::uint64_t scan_process_reused_bytes = 0U;
    std::uint64_t scan_durable_reused_entry_count = 0U;
    std::uint64_t scan_durable_reused_bytes = 0U;
    bool verification_checkpoint_deferred_by_transient_capacity = false;
    SyncReplicaFilePayloadStoreScrubReport scrub_report;
    std::shared_ptr<PayloadVerificationCache> verification_cache;
    std::uint64_t issued_integrity_fault_epoch = 0U;
    std::uint64_t transient_entry_count = 0U;
    std::uint64_t transient_bytes = 0U;
    std::uint64_t transient_reserved_bytes = 0U;
    std::string transient_namespace_digest;
    bool scrub_state_present = false;
    bool scrub_state_usable = false;
    bool scrub_active_reverified_good = false;
    bool scrub_failure_reverified_good = false;
    std::optional<SyncPosixRegularFileSnapshotMetadata> scrub_state_metadata;
    std::optional<SyncReplicaFilePayloadScrubState> scrub_state;
    bool retention_mark_present = false;
    bool retention_mark_observation_known = false;
    bool retention_mark_usable = false;
    std::optional<SyncReplicaFilePayloadRetentionMark> retention_mark;
    std::optional<std::string> retention_mark_digest;
    struct stat directory_status {};
    std::string root_attestation_digest;
    std::string snapshot_digest;
};

[[nodiscard]] bool terminal_verification_work_precedes(
    const SyncReplicaFilePayloadStoreTerminalVerificationWork& left,
    const SyncReplicaFilePayloadStoreTerminalVerificationWork& right)
    noexcept {
    if (left.verified_offset_bytes != right.verified_offset_bytes) {
        return left.verified_offset_bytes < right.verified_offset_bytes;
    }
    return left.content_sha256 < right.content_sha256;
}

void canonicalize_terminal_verification_work_or_throw(
    std::vector<SyncReplicaFilePayloadStoreTerminalVerificationWork>& work,
    const SyncReplicaFilePayloadStoreLimits& limits,
    const std::string& label) {
    if (work.size() > limits.max_transient_entries) {
        throw std::length_error(
            label + " terminal-verification work exceeds entry budget");
    }
    for (const auto& entry : work) {
        if (!is_lowercase_sha256_hex(entry.content_sha256) ||
            entry.total_size_bytes == 0U ||
            entry.total_size_bytes > limits.max_payload_bytes ||
            entry.verified_offset_bytes >= entry.total_size_bytes) {
            throw std::logic_error(
                label + " terminal-verification work is noncanonical");
        }
    }
    std::sort(
        work.begin(), work.end(), terminal_verification_work_precedes);
    std::vector<std::string_view> digests;
    digests.reserve(work.size());
    for (const auto& entry : work) digests.push_back(entry.content_sha256);
    std::sort(digests.begin(), digests.end());
    if (std::adjacent_find(digests.begin(), digests.end()) != digests.end()) {
        throw std::logic_error(
            label + " terminal-verification work contains duplicate digests");
    }
}

void upsert_terminal_verification_work_if_known_or_throw(
    bool observation_known,
    std::vector<SyncReplicaFilePayloadStoreTerminalVerificationWork>& target,
    SyncReplicaFilePayloadStoreTerminalVerificationWork work,
    const SyncReplicaFilePayloadStoreLimits& limits,
    const std::string& label) {
    if (!observation_known) return;
    const auto existing = std::find_if(
        target.begin(), target.end(),
        [&](const auto& candidate) {
            return candidate.content_sha256 == work.content_sha256;
        });
    if (existing != target.end()) {
        *existing = std::move(work);
    } else {
        target.push_back(std::move(work));
    }
    canonicalize_terminal_verification_work_or_throw(target, limits, label);
}

void erase_terminal_verification_work_if_known(
    bool observation_known,
    std::vector<SyncReplicaFilePayloadStoreTerminalVerificationWork>& target,
    std::string_view content_sha256) {
    if (!observation_known) return;
    const auto removed = std::remove_if(
        target.begin(), target.end(),
        [&](const auto& candidate) {
            return candidate.content_sha256 == content_sha256;
        });
    target.erase(removed, target.end());
}

struct SyncReplicaFilePayloadStore::State final {
    ~State() noexcept;

    std::string folder_id;
    fs::path root_path;
    SyncReplicaFilePayloadStoreOpenDisposition disposition =
        SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly;
    SyncReplicaFilePayloadStoreLimits limits;
    std::string label;
    std::string identity_basename;
    std::string legacy_identity_basename;
    std::string expected_identity;
    bool allow_existing_payload_adoption = true;
    SyncDirectoryAuthority root_authority;
    std::string root_attestation_digest;
    // A mutation batch is a self-contained move-only capability and may
    // legitimately outlive the store handle that created it. Keep the
    // process-local acceleration owner shared so successful batch teardown can
    // publish its already verified complete index without retaining a raw
    // pointer into a destroyed store State. Graceful State teardown makes one
    // fail-fast final checkpoint attempt when a bounded dirty tail remains.
    std::shared_ptr<PayloadVerificationCache> verification_cache =
        std::make_shared<PayloadVerificationCache>();
    std::shared_ptr<PayloadStoreLiveCapabilityRegistry>
        live_capability_registry;
    std::chrono::steady_clock::time_point next_scrub_not_before =
        std::chrono::steady_clock::time_point::min();
    // Operator-only process observations. Durable scheduling authority remains
    // exclusively in .anonsync-payload-scrub-state-v1; these timestamps are
    // monotonic and intentionally disappear at restart rather than pretending
    // a wall-clock age that rev0955 never persisted.
    std::optional<SyncReplicaFilePayloadStoreScrubReport> last_scrub_report;
    std::chrono::steady_clock::time_point last_scrub_report_at =
        std::chrono::steady_clock::time_point::min();
    std::optional<std::chrono::steady_clock::time_point>
        last_scrub_cycle_completed_at;
    // Bounded owner-local acceleration for receiver-terminal SHA-256 work.
    // A complete writable namespace scan replaces this vector atomically.
    // Exact prefix staging maintains it only after observation_known becomes
    // true; a fresh process never infers global completeness from one targeted
    // mutation. Every scheduled effect still reopens and re-proves the durable
    // staged inode and checksum-framed journal.
    bool terminal_verification_observation_known = false;
    std::vector<SyncReplicaFilePayloadStoreTerminalVerificationWork>
        terminal_verification_work;
};

struct SyncReplicaFilePayloadStoreMutationBatch::State final {
    State(
        SyncDirectoryAuthority root_authority_value,
        SyncReplicaFilePayloadStoreLimits limits_value,
        std::string label_value,
        std::string identity_basename_value,
        std::string expected_identity_value,
        StoreLease mutation_lease_value,
        std::shared_ptr<PayloadVerificationCache> verification_cache_value,
        std::shared_ptr<PayloadStoreLiveCapabilityRegistry>
            live_capability_registry_value,
        ScannedPayloadIndex index_value,
        std::uint64_t full_scan_count_value,
        std::uint64_t scan_hashed_entry_count_value,
        std::uint64_t scan_hashed_bytes_value,
        std::uint64_t scan_reused_entry_count_value,
        std::uint64_t scan_reused_bytes_value,
        std::uint64_t scan_process_reused_entry_count_value,
        std::uint64_t scan_process_reused_bytes_value,
        std::uint64_t scan_durable_reused_entry_count_value,
        std::uint64_t scan_durable_reused_bytes_value)
        : live_capability_registration(
              std::move(live_capability_registry_value),
              PayloadStoreLiveCapabilityKind::MutationBatch),
          root_authority(std::move(root_authority_value)),
          limits(limits_value),
          label(std::move(label_value)),
          identity_basename(std::move(identity_basename_value)),
          expected_identity(std::move(expected_identity_value)),
          verification_cache(std::move(verification_cache_value)),
          index(std::move(index_value)),
          full_scan_count(full_scan_count_value),
          scan_hashed_entry_count(scan_hashed_entry_count_value),
          scan_hashed_bytes(scan_hashed_bytes_value),
          scan_reused_entry_count(scan_reused_entry_count_value),
          scan_reused_bytes(scan_reused_bytes_value),
          scan_process_reused_entry_count(
              scan_process_reused_entry_count_value),
          scan_process_reused_bytes(scan_process_reused_bytes_value),
          scan_durable_reused_entry_count(
              scan_durable_reused_entry_count_value),
          scan_durable_reused_bytes(scan_durable_reused_bytes_value),
          mutation_lease(std::move(mutation_lease_value)) {}

    ~State() noexcept {
        // The batch index began as one complete leased scan and every ordinary
        // successful put updated it only after durable create-new publication,
        // exact reopen, and a final lease proof. First attempt to checkpoint the
        // same complete view as restart acceleration while the exclusive lease
        // remains live. This record is non-authoritative: any allocation, budget,
        // publication, or final-proof failure is ignored and a future cold scan
        // hashes the affected payloads.
        if (poisoned || !verification_cache) return;
        try {
            sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
                require_current_owner_or_throw(
                    root_authority,
                    label + " verification-cache ownership preflight");
        } catch (...) {
            // State and its owner-local cache must not be inspected from a
            // foreign thread. Member teardown will apply the directory
            // authority's ordinary fail-stop lifetime rule after this body.
            return;
        }
        const bool last_cache_owner = verification_cache.use_count() == 1U;
        if (verification_checkpoint_publication_worth_attempting(
                *verification_cache, last_cache_owner)) {
            try {
                mutation_lease.verify_or_throw(
                    root_authority,
                    label +
                        " durable verification-index prepublication cutpoint");
                const VerificationIndexPublicationDisposition disposition =
                    publish_verification_index_or_throw(
                        root_authority, limits, expected_identity,
                        mutation_lease.identity_status(), index,
                        label + " durable verification-index publication");
                mutation_lease.verify_or_throw(
                    root_authority,
                    label + " durable verification-index final cutpoint");
                note_verification_checkpoint_publication_disposition(
                    *verification_cache, index, disposition);
            } catch (...) {
                // A durable acceleration failure cannot change any already
                // returned payload publication result or poison the complete
                // in-memory index.
            }
        }

        // Publish the complete verified view process-locally as well. Teardown
        // owns the vector exclusively, so the replacement generation takes it
        // without an O(n) copy. Old and failed-to-publish generations are retained
        // as State members until after the exclusive flock is released by member
        // destruction order.
        try {
            auto mutable_generation =
                std::make_shared<PayloadVerificationGeneration>();
            mutable_generation->identity_status =
                mutation_lease.identity_status();
            mutable_generation->entries.swap(index.entries);
            pending_cache_generation = std::move(mutable_generation);
            mutation_lease.verify_or_throw(
                root_authority,
                label + " verification-cache publication lease cutpoint");
            retired_cache_generation = publish_verification_generation(
                *verification_cache, pending_cache_generation);
        } catch (...) {
            // Verification caching is process-local acceleration only. The
            // durable namespace and the batch's already returned results remain
            // authoritative; a later scan will rebuild any missing cache state.
        }
    }

    PayloadStoreLiveCapabilityRegistration live_capability_registration;
    SyncDirectoryAuthority root_authority;
    SyncReplicaFilePayloadStoreLimits limits;
    std::string label;
    std::string identity_basename;
    std::string expected_identity;
    std::shared_ptr<PayloadVerificationCache> verification_cache;
    ScannedPayloadIndex index;
    std::uint64_t full_scan_count = 0U;
    std::uint64_t scan_hashed_entry_count = 0U;
    std::uint64_t scan_hashed_bytes = 0U;
    std::uint64_t scan_reused_entry_count = 0U;
    std::uint64_t scan_reused_bytes = 0U;
    std::uint64_t scan_process_reused_entry_count = 0U;
    std::uint64_t scan_process_reused_bytes = 0U;
    std::uint64_t scan_durable_reused_entry_count = 0U;
    std::uint64_t scan_durable_reused_bytes = 0U;
    std::uint64_t put_count = 0U;
    std::uint64_t source_bytes = 0U;
    std::uint64_t inserted_count = 0U;
    std::uint64_t already_present_count = 0U;
    bool poisoned = false;
    std::shared_ptr<const PayloadVerificationGeneration>
        pending_cache_generation;
    std::shared_ptr<const PayloadVerificationGeneration>
        retired_cache_generation;
    // Declared last so its destructor releases the exclusive flock before the
    // pending or displaced cache generations are destroyed. Cache promotion
    // remains lease-proved, while potentially large metadata reclamation no
    // longer extends the cooperative mutation exclusion window.
    StoreLease mutation_lease;
};

namespace {

struct PayloadScrubAttemptSnapshotView final {
    const std::vector<PayloadIndexEntry>& entries;
    struct stat directory_status {};
    std::uint64_t transient_entry_count = 0U;
    std::uint64_t transient_reserved_bytes = 0U;
    bool scrub_state_present = false;
    std::optional<SyncPosixRegularFileSnapshotMetadata> scrub_state_metadata;
    bool scrub_active_reverified_good = false;
    bool scrub_failure_reverified_good = false;
};

[[nodiscard]] bool payload_scrub_enabled(
    const SyncReplicaFilePayloadStoreLimits& limits) noexcept {
    return limits.max_scrub_bytes_per_attempt != 0U &&
           limits.max_scrub_entries_per_attempt != 0U;
}

void clear_payload_scrub_active(
    SyncReplicaFilePayloadScrubState& state) {
    state.disposition = SyncReplicaFilePayloadScrubStateDisposition::Idle;
    state.active_content_sha256.clear();
    state.active_metadata = {};
    state.active_offset_bytes = 0U;
    state.active_hash = ResumableSha256{}.checkpoint();
    state.observed_content_sha256.clear();
}

[[nodiscard]] std::uint64_t next_scrub_generation_or_throw(
    const ScrubStateFileObservation& current,
    const std::string& label) {
    if (!current.usable) return 1U;
    if (!current.state.has_value()) {
        throw std::logic_error(
            label + " usable scrub state lacks parsed contents");
    }
    if (current.state->generation ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " scrub-state generation is exhausted");
    }
    return current.state->generation + 1U;
}

[[nodiscard]] SyncReplicaFilePayloadStoreScrubReport scrub_report_from_state(
    SyncReplicaFilePayloadStoreScrubDisposition disposition,
    const SyncReplicaFilePayloadScrubState* state,
    bool state_rebuilt = false) {
    SyncReplicaFilePayloadStoreScrubReport report;
    report.disposition = disposition;
    report.state_rebuilt = state_rebuilt;
    if (state != nullptr) {
        report.completed_cycles = state->completed_cycles;
        report.state_generation = state->generation;
        if (scrub_state_is_active(*state)) {
            report.active_content_sha256 = state->active_content_sha256;
            report.active_offset_bytes = state->active_offset_bytes;
        }
    }
    return report;
}

[[nodiscard]] std::optional<SyncPosixRegularFileSnapshotMetadata>
publish_payload_scrub_state_with_reconciliation(
    const SyncDirectoryAuthority& root_authority,
    int root_descriptor,
    SyncPosixDirectoryResolutionCapability resolution_capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const StoreLease& lease,
    const ScrubStateFileObservation& current,
    const SyncReplicaFilePayloadScrubState& desired,
    const std::string& label) noexcept {
    const auto observe_exact_committed = [&]()
        -> std::optional<SyncPosixRegularFileSnapshotMetadata> {
        const ScrubStateFileObservation observed =
            observe_scrub_state_file_or_throw(
                root_descriptor, root_authority.path(),
                resolution_capability, mount_identity,
                root_authority.attestation(), limits, expected_identity,
                &lease.identity_status(), true,
                label + " committed-state observation");
        lease.verify_or_throw(
            root_authority, label + " committed-state lease cutpoint");
        if (!observed.usable || !observed.state.has_value() ||
            !observed.metadata.has_value() ||
            *observed.state != desired) {
            return std::nullopt;
        }
        return observed.metadata;
    };

    try {
        const std::string encoded =
            serialize_sync_replica_file_payload_scrub_state_or_throw(
                desired, limits.max_payload_bytes, label + " encoding");
        lease.verify_or_throw(
            root_authority, label + " prepublication lease cutpoint");
        if (current.present) {
            if (!current.metadata.has_value()) {
                throw std::logic_error(
                    label + " present scrub state lacks exact metadata");
            }
            write_sync_file_atomically_replace_expected_under_directory_or_throw(
                root_authority,
                fs::path(kSyncReplicaFilePayloadScrubStateBasename),
                byte_span(encoded), *current.metadata, label);
        } else {
            write_sync_file_atomically_create_new_under_directory_or_throw(
                root_authority,
                fs::path(kSyncReplicaFilePayloadScrubStateBasename),
                byte_span(encoded), label);
        }
        lease.verify_or_throw(
            root_authority, label + " postpublication lease cutpoint");
        return observe_exact_committed();
    } catch (...) {
        // Atomic publication may report an exception after the rename cutpoint,
        // or exact re-observation itself may fail transiently. Reconcile under
        // the still-live exclusive lease; only an exact checksum-framed record
        // equal to desired authorizes the caller to read payload bytes.
        try {
            return observe_exact_committed();
        } catch (...) {
            return std::nullopt;
        }
    }
}

[[nodiscard]] SyncPosixRegularFileSnapshotMetadata
publish_rebound_scrub_state_after_identity_rename_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const StoreLease& migration_lease,
    const SyncPosixRegularFileSnapshotMetadata& prior_state_metadata,
    const SyncReplicaFilePayloadScrubState& rebound_state,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            root_authority, label + " root descriptor");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    ScrubStateFileObservation current;
    current.present = true;
    current.metadata = prior_state_metadata;
    const std::optional<SyncPosixRegularFileSnapshotMetadata> committed =
        publish_payload_scrub_state_with_reconciliation(
            root_authority, root_descriptor.get(), resolution_capability,
            mount_identity, limits, expected_identity, migration_lease,
            current, rebound_state, label);
    if (!committed.has_value()) {
        throw std::runtime_error(
            label +
            " could not durably rebind the active write-ahead state to the "
            "new minimum-reader identity");
    }
    return *committed;
}

[[nodiscard]] SyncReplicaFilePayloadStoreScrubReport
advance_payload_scrub_from_snapshot_or_throw(
    const SyncDirectoryAuthority& retained_root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    PayloadVerificationCache& verification_cache,
    const PayloadScrubAttemptSnapshotView& snapshot,
    const std::string& label) {
    const bool scrub_enabled = payload_scrub_enabled(limits);
    // Disabling bounded scrub reads does not authorize a durable write-ahead
    // record to remain unresolved forever. A present damaged/active/failure
    // record may still need one metadata-only settlement after the complete
    // snapshot scan has proved current bytes. Clean absence needs no lease.
    if (!scrub_enabled && !snapshot.scrub_state_present) {
        return scrub_report_from_state(
            SyncReplicaFilePayloadStoreScrubDisposition::Disabled, nullptr);
    }

    SyncDirectoryAuthority scrub_root = reopen_matching_root_authority_or_throw(
        retained_root_authority, label + " root");
    StoreLease lease = acquire_store_lease_or_throw(
        scrub_root, identity_basename, expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        label, StoreObservationDurability::Reconcile);

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease = Access::duplicate_shared_open_description_or_throw(
        scrub_root, label + " root descriptor");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat current_directory{};
    if (::fstat(root_descriptor.get(), &current_directory) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " root fstat failed: " + error_text(error));
    }
    if (!same_directory_observation(
            snapshot.directory_status, current_directory)) {
        return scrub_report_from_state(
            SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredStaleSnapshot,
            nullptr);
    }

    ScrubStateFileObservation current =
        observe_scrub_state_file_or_throw(
            root_descriptor.get(), scrub_root.path(), resolution_capability,
            mount_identity, scrub_root.attestation(), limits,
            expected_identity, &lease.identity_status(), true,
            label + " state");
    if (current.present != snapshot.scrub_state_present ||
        (current.present &&
         (!current.metadata.has_value() ||
          !snapshot.scrub_state_metadata.has_value() ||
          *current.metadata != *snapshot.scrub_state_metadata))) {
        return scrub_report_from_state(
            SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredStaleSnapshot,
            current.usable ? &*current.state : nullptr);
    }

    const std::uint64_t encoded_bytes =
        sync_replica_file_payload_scrub_state_exact_bytes();
    if (snapshot.transient_entry_count >= limits.max_transient_entries ||
        snapshot.transient_reserved_bytes > limits.max_transient_bytes ||
        encoded_bytes >
            limits.max_transient_bytes -
                snapshot.transient_reserved_bytes) {
        return scrub_report_from_state(
            SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredTransientCapacity,
            current.usable ? &*current.state : nullptr);
    }

    const SyncPosixRegularFileSnapshotMetadata identity_metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            lease.identity_status(),
            SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " identity metadata");
    SyncReplicaFilePayloadScrubState working =
        current.usable
            ? *current.state
            : initial_sync_replica_file_payload_scrub_state_or_throw(
                  sha256_hex(std::string(expected_identity)),
                  identity_metadata, label + " genesis");
    bool state_rebuilt = current.present && !current.usable;
    enum class ReverifiedScrubSettlement : std::uint8_t {
        None = 0,
        ActiveCompleted = 1,
        FailureCleared = 2,
    };
    ReverifiedScrubSettlement reverified_settlement =
        ReverifiedScrubSettlement::None;

    // Every committed transition is re-observed under the exact exclusive
    // lease. This mutable observation then becomes the compare-and-replace
    // source for the next transition in the same bounded attempt. The
    // same-process active witness is retained before any potentially allocating
    // copy into current.state; a failure after commit is therefore safe and the
    // durable Prepared/Progress record remains conservative across restart.
    const auto publish_working = [&](const std::string& publication_label) {
        working.generation =
            next_scrub_generation_or_throw(current, publication_label);
        const std::optional<SyncPosixRegularFileSnapshotMetadata> committed =
            publish_payload_scrub_state_with_reconciliation(
                scrub_root, root_descriptor.get(), resolution_capability,
                mount_identity, limits, expected_identity, lease, current,
                working, publication_label);
        if (!committed.has_value()) return false;
        note_process_scrub_state_observation(
            verification_cache, &working, &*committed, false);
        current.present = true;
        current.usable = true;
        current.metadata = *committed;
        current.state = working;
        return true;
    };

    if (current.usable) {
        if (scrub_state_is_active(working)) {
            const PayloadIndexEntry* active = find_entry(
                snapshot.entries, working.active_content_sha256);
            if (active == nullptr ||
                !sync_posix_regular_file_snapshot_metadata_matches_status(
                    working.active_metadata, active->status)) {
                clear_payload_scrub_active(working);
                state_rebuilt = true;
            } else if (snapshot.scrub_active_reverified_good) {
                // A fresh/replaced-state owner was already forced through the
                // complete current-byte scanner before this exclusive attempt.
                // That exact scan is stronger than the older Prepared/Progress
                // continuation checkpoint. Settle the fair cursor from the
                // complete proof instead of rereading a suffix (or the whole
                // file) and risking a false mismatch from stale partial state.
                working.cursor_after_content_sha256 =
                    working.active_content_sha256;
                clear_payload_scrub_active(working);
                reverified_settlement =
                    ReverifiedScrubSettlement::ActiveCompleted;
            }
        } else if (working.disposition ==
                   SyncReplicaFilePayloadScrubStateDisposition::
                       IntegrityFailure) {
            const PayloadIndexEntry* failed = find_entry(
                snapshot.entries, working.active_content_sha256);
            const bool same_failed_observation =
                failed != nullptr &&
                sync_posix_regular_file_snapshot_metadata_matches_status(
                    working.active_metadata, failed->status);
            if (same_failed_observation &&
                !snapshot.scrub_failure_reverified_good) {
                throw std::logic_error(
                    label +
                    " matching scrub failure lacked a current full-byte reproof");
            }
            // If the complete snapshot just disproved the old failure, that
            // full-byte proof is already stronger than repeating the same read
            // under this optional scrub attempt. Advance the fair cursor past
            // the exact reverified payload and publish only that scheduling
            // transition. If the named payload changed/disappeared, preserve
            // the old cursor and let the ordinary cycle revisit current state.
            if (failed != nullptr &&
                snapshot.scrub_failure_reverified_good) {
                working.cursor_after_content_sha256 =
                    working.active_content_sha256;
                reverified_settlement =
                    ReverifiedScrubSettlement::FailureCleared;
            }
            clear_payload_scrub_active(working);
            state_rebuilt = true;
        }
    }

    if (snapshot.entries.empty()) {
        const bool needs_clear =
            current.present &&
            (!current.usable ||
             working.disposition !=
                 SyncReplicaFilePayloadScrubStateDisposition::Idle ||
             !working.cursor_after_content_sha256.empty());
        if (!needs_clear) {
            return scrub_report_from_state(
                SyncReplicaFilePayloadStoreScrubDisposition::Empty,
                current.usable ? &working : nullptr, state_rebuilt);
        }
        clear_payload_scrub_active(working);
        working.cursor_after_content_sha256.clear();
        working.completed_cycles = 0U;
        const bool published = publish_working(
            label + " empty-state publication");
        return scrub_report_from_state(
            published
                ? (scrub_enabled
                       ? SyncReplicaFilePayloadStoreScrubDisposition::Empty
                       : SyncReplicaFilePayloadStoreScrubDisposition::Disabled)
                : SyncReplicaFilePayloadStoreScrubDisposition::
                      DeferredPublicationFailure,
            published ? &working : (current.usable ? &*current.state : nullptr),
            state_rebuilt);
    }

    if (reverified_settlement != ReverifiedScrubSettlement::None) {
        const bool published = publish_working(
            label + " reverified-state publication");
        SyncReplicaFilePayloadStoreScrubReport report =
            scrub_report_from_state(
                published
                    ? (scrub_enabled
                           ? SyncReplicaFilePayloadStoreScrubDisposition::
                                 Advanced
                           : SyncReplicaFilePayloadStoreScrubDisposition::
                                 Disabled)
                    : SyncReplicaFilePayloadStoreScrubDisposition::
                          DeferredPublicationFailure,
                published
                    ? &working
                    : (current.usable ? &*current.state : nullptr),
                state_rebuilt);
        if (published) {
            report.completed_entry_count = 1U;
            report.reverified_active_completed =
                reverified_settlement ==
                ReverifiedScrubSettlement::ActiveCompleted;
            report.reverified_failure_cleared =
                reverified_settlement ==
                ReverifiedScrubSettlement::FailureCleared;
        }
        return report;
    }

    if (!scrub_enabled) {
        if (!state_rebuilt) {
            return scrub_report_from_state(
                SyncReplicaFilePayloadStoreScrubDisposition::Disabled,
                current.usable ? &working : nullptr, false);
        }
        const bool published = publish_working(
            label + " disabled restart-fence settlement publication");
        return scrub_report_from_state(
            published
                ? SyncReplicaFilePayloadStoreScrubDisposition::Disabled
                : SyncReplicaFilePayloadStoreScrubDisposition::
                      DeferredPublicationFailure,
            published ? &working
                      : (current.usable ? &*current.state : nullptr),
            state_rebuilt);
    }

    const std::uint64_t distinct_limit = std::min<std::uint64_t>(
        limits.max_scrub_entries_per_attempt,
        size_to_u64_or_throw(snapshot.entries.size(), label + " entry count"));
    SyncReplicaFilePayloadStoreScrubReport report;
    report.disposition =
        SyncReplicaFilePayloadStoreScrubDisposition::Advanced;
    report.state_rebuilt = state_rebuilt;

    while (report.touched_entry_count < distinct_limit) {
        const PayloadIndexEntry* active = nullptr;
        if (scrub_state_is_active(working)) {
            active = find_entry(
                snapshot.entries, working.active_content_sha256);
            if (active == nullptr) {
                throw std::logic_error(
                    label + " active scrub payload disappeared from snapshot");
            }
        } else {
            auto selected = std::upper_bound(
                snapshot.entries.begin(), snapshot.entries.end(),
                working.cursor_after_content_sha256,
                [](std::string_view digest, const PayloadIndexEntry& entry) {
                    return digest < entry.content_sha256;
                });
            if (selected == snapshot.entries.end()) {
                if (working.completed_cycles ==
                    std::numeric_limits<std::uint64_t>::max()) {
                    throw std::overflow_error(
                        label + " scrub cycle counter is exhausted");
                }
                ++working.completed_cycles;
                // The cursor is scoped to the newly entered cycle. Leaving
                // the prior cycle's final digest here makes a one-entry store
                // encode active==cursor, which the canonical state correctly
                // rejects and would otherwise repeat the first bounded range
                // forever without durable progress.
                working.cursor_after_content_sha256.clear();
                selected = snapshot.entries.begin();
            }
            if (selected->size_bytes != 0U &&
                report.hashed_bytes >=
                    limits.max_scrub_bytes_per_attempt) {
                break;
            }

            // Write-ahead rule: persist and re-observe the exact selected
            // inode/metadata before opening or reading even one byte. If this
            // process dies after the read begins but before terminal failure or
            // progress publication, a fresh process sees Prepared and cannot
            // reuse the durable metadata checkpoint for this payload.
            working.disposition =
                SyncReplicaFilePayloadScrubStateDisposition::Prepared;
            working.active_content_sha256 = selected->content_sha256;
            working.active_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    selected->status,
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    label + " selected metadata");
            working.active_offset_bytes = 0U;
            working.active_hash = ResumableSha256{}.checkpoint();
            working.observed_content_sha256.clear();
            if (!publish_working(label + " write-ahead intent publication")) {
                SyncReplicaFilePayloadStoreScrubReport deferred =
                    scrub_report_from_state(
                        SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredPublicationFailure,
                        current.usable ? &*current.state : nullptr,
                        state_rebuilt);
                deferred.hashed_bytes = report.hashed_bytes;
                deferred.touched_entry_count = report.touched_entry_count;
                deferred.completed_entry_count = report.completed_entry_count;
                return deferred;
            }
            active = &*selected;
        }

        if (active->size_bytes != 0U &&
            report.hashed_bytes >= limits.max_scrub_bytes_per_attempt) {
            break;
        }
        ++report.touched_entry_count;

        SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
            root_descriptor.get(), active->content_sha256, scrub_root.path(),
            resolution_capability, mount_identity,
            label + " payload " + active->content_sha256);
        OwnedFd payload(opened.descriptor);
        require_private_regular_file_or_throw(
            opened.status, scrub_root.attestation(),
            label + " payload " + active->content_sha256);
        if (!same_regular_file_observation(active->status, opened.status) ||
            !sync_posix_regular_file_snapshot_metadata_matches_status(
                working.active_metadata, opened.status)) {
            return scrub_report_from_state(
                SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredStaleSnapshot,
                current.usable ? &*current.state : nullptr, state_rebuilt);
        }

        ResumableSha256 digest(
            working.active_hash, label + " active hash");
        std::array<char, kStreamingBufferBytes> buffer{};
        while (working.active_offset_bytes < active->size_bytes &&
               report.hashed_bytes < limits.max_scrub_bytes_per_attempt) {
            const std::uint64_t remaining_file =
                active->size_bytes - working.active_offset_bytes;
            const std::uint64_t remaining_budget =
                limits.max_scrub_bytes_per_attempt - report.hashed_bytes;
            const std::size_t requested = static_cast<std::size_t>(
                std::min<std::uint64_t>(
                    std::min(remaining_file, remaining_budget),
                    buffer.size()));
            ssize_t count;
            do {
                count = ::pread(
                    payload.get(), buffer.data(), requested,
                    static_cast<off_t>(working.active_offset_bytes));
            } while (count < 0 && errno == EINTR);
            if (count < 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " scrub read failed: " + error_text(error));
            }
            if (count == 0) {
                throw std::runtime_error(
                    label + " payload became truncated during scrub");
            }
            const std::uint64_t received =
                static_cast<std::uint64_t>(count);
            if (received > remaining_file || received > remaining_budget) {
                throw std::runtime_error(
                    label + " scrub read crossed its bounded extent");
            }
            digest.update(std::string_view(
                buffer.data(), static_cast<std::size_t>(count)));
            working.active_offset_bytes += received;
            report.hashed_bytes += received;
        }
        working.active_hash = digest.checkpoint();

        struct stat after{};
        if (::fstat(payload.get(), &after) != 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " scrub final fstat failed: " + error_text(error));
        }
        if (!same_regular_file_observation(opened.status, after)) {
            throw std::runtime_error(
                label + " payload changed while being scrubbed");
        }
        verify_named_regular_file_or_throw(
            root_descriptor.get(), active->content_sha256, after,
            scrub_root.attestation(),
            label + " payload " + active->content_sha256);
        lease.verify_or_throw(
            scrub_root, label + " payload-read lease cutpoint");

        if (working.active_offset_bytes != active->size_bytes) {
            working.disposition =
                SyncReplicaFilePayloadScrubStateDisposition::Progress;
            break;
        }

        ResumableSha256 completed(
            working.active_hash, label + " completed hash");
        const std::array<char, kSha256HexCharacters> observed_chars =
            completed.finish_hex_array();
        const std::string_view observed(
            observed_chars.data(), observed_chars.size());
        if (observed != active->content_sha256) {
            // This is the first exact point at which current bytes are known to
            // disagree with their immutable digest name. Revoke every older
            // snapshot and drop the same-process active acceleration before
            // assigning strings, serializing durable evidence, or constructing
            // the typed exception. If any later allocation/publication fails,
            // the already committed Prepared/Progress state remains a durable
            // restart fence and the fixed-width process fault remains fail-closed.
            (void)retain_process_integrity_fault(
                verification_cache, active->content_sha256, observed);
            verification_cache.scrub_active.reset();
            working.disposition =
                SyncReplicaFilePayloadScrubStateDisposition::
                    IntegrityFailure;
            working.observed_content_sha256 = observed;
            const bool persisted = publish_working(
                label + " failure publication");
            throw SyncReplicaFilePayloadStoreIntegrityError(
                active->content_sha256, std::string(observed), persisted,
                label + " detected a payload-byte integrity mismatch for " +
                    active->content_sha256 +
                    (persisted
                         ? " and persisted the failure witness"
                         : " but could not persist the failure witness"));
        }

        working.cursor_after_content_sha256 = active->content_sha256;
        clear_payload_scrub_active(working);
        ++report.completed_entry_count;
    }

    // Enabled attempts with a nonempty snapshot always either touch at least
    // one payload or stop only after an earlier completed file exhausted the
    // byte budget. In both cases the resulting cursor/progress is worth one
    // durable publication.
    const bool published = publish_working(
        label + " progress publication");
    if (!published) {
        SyncReplicaFilePayloadStoreScrubReport deferred =
            scrub_report_from_state(
                SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredPublicationFailure,
                current.usable ? &*current.state : nullptr, state_rebuilt);
        deferred.hashed_bytes = report.hashed_bytes;
        deferred.touched_entry_count = report.touched_entry_count;
        deferred.completed_entry_count = report.completed_entry_count;
        return deferred;
    }

    report.completed_cycles = working.completed_cycles;
    report.state_generation = working.generation;
    if (scrub_state_is_active(working)) {
        report.active_content_sha256 = working.active_content_sha256;
        report.active_offset_bytes = working.active_offset_bytes;
    }
    return report;
}

}  // namespace

void refresh_verification_index_best_effort(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    PayloadVerificationCache& verification_cache,
    const std::string& label,
    bool graceful_final_checkpoint) noexcept {
    try {
        sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
            require_current_owner_or_throw(
                root_authority,
                label + " verification-cache ownership preflight");
        if (!verification_checkpoint_publication_worth_attempting(
                verification_cache, graceful_final_checkpoint)) {
            return;
        }
        root_authority.verify_or_throw(
            label + " verification-index refresh source preflight");
        SyncDirectoryAuthority refresh_root =
            reopen_matching_root_authority_or_throw(
                root_authority, label + " verification-index refresh");
        StoreLease refresh_lease = acquire_store_lease_or_throw(
            refresh_root, identity_basename, expected_identity,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            label + " verification-index refresh",
            StoreObservationDurability::Reconcile);
        ScannedPayloadIndex current = scan_store_under_lease_or_throw(
            refresh_root, limits, identity_basename, expected_identity,
            refresh_lease,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            label + " verification-index refresh scan",
            StoreObservationDurability::Reconcile, &verification_cache);
        if (!verification_checkpoint_publication_worth_attempting(
                verification_cache, graceful_final_checkpoint)) {
            return;
        }
        refresh_lease.verify_or_throw(
            refresh_root,
            label + " verification-index refresh prepublication cutpoint");
        const VerificationIndexPublicationDisposition disposition =
            publish_verification_index_or_throw(
                refresh_root, limits, expected_identity,
                refresh_lease.identity_status(), current,
                label + " verification-index refresh publication");
        refresh_lease.verify_or_throw(
            refresh_root,
            label + " verification-index refresh final cutpoint");
        note_verification_checkpoint_publication_disposition(
            verification_cache, current, disposition);
    } catch (...) {
        // This path runs only after a complete authoritative snapshot has been
        // constructed and its shared lease released. Contention, ENOSPC, stale
        // namespace metadata, or allocation failure must not change that result.
    }
}

SyncReplicaFilePayloadStore::State::~State() noexcept {
    if (disposition ==
            SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect ||
        !verification_cache) {
        return;
    }
    // The refresh helper proves the originating process/thread before reading
    // the deliberately unsynchronized checkpoint scheduler. Its cheap gate
    // preserves the old no-op close path without paying for a filesystem
    // authority reproof when no checkpoint is due.
    refresh_verification_index_best_effort(
        root_authority, limits, identity_basename, expected_identity,
        *verification_cache, label + " graceful close", true);
}

// A completed receiver publication already paid for a whole-file digest and
// retained a complete prepublication namespace scan. Fold the exact published
// descriptor observation into that scan so the next same-process snapshot does
// not hash the new file again. Durable checkpointing follows the geometric
// policy above; it is not rewritten after every received file.
void retain_completed_payload_verification_best_effort(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view expected_identity,
    const StoreLease& mutation_lease,
    const std::shared_ptr<PayloadVerificationCache>& verification_cache,
    ScannedPayloadIndex& completed,
    std::uint64_t added_payload_bytes,
    const std::string& label) noexcept {
    if (!verification_cache) return;

    try {
        mutation_lease.verify_or_throw(
            root_authority, label + " completed payload cache cutpoint");
        note_verification_checkpoint_payload_addition(
            *verification_cache, added_payload_bytes);
    } catch (...) {
        return;
    }

    if (verification_checkpoint_publication_worth_attempting(
            *verification_cache, false)) {
        try {
            const VerificationIndexPublicationDisposition disposition =
                publish_verification_index_or_throw(
                    root_authority, limits, expected_identity,
                    mutation_lease.identity_status(), completed,
                    label + " completed payload verification checkpoint");
            mutation_lease.verify_or_throw(
                root_authority,
                label + " completed payload checkpoint final cutpoint");
            note_verification_checkpoint_publication_disposition(
                *verification_cache, completed, disposition);
        } catch (...) {
            // The payload and its operation-visible result were already exact
            // before entering this non-authoritative acceleration path.
        }
    }

    try {
        auto generation = std::make_shared<PayloadVerificationGeneration>();
        generation->identity_status = mutation_lease.identity_status();
        generation->entries.swap(completed.entries);
        mutation_lease.verify_or_throw(
            root_authority,
            label + " completed payload warm-cache final cutpoint");
        const std::shared_ptr<const PayloadVerificationGeneration> retired =
            publish_verification_generation(
                *verification_cache, std::move(generation));
        (void)retired;
    } catch (...) {
        // A later complete scan will rebuild process-local acceleration.
    }
}

std::string_view sync_replica_file_payload_store_scrub_disposition_name(
    SyncReplicaFilePayloadStoreScrubDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFilePayloadStoreScrubDisposition::Disabled:
            return "disabled";
        case SyncReplicaFilePayloadStoreScrubDisposition::DeferredBySchedule:
            return "deferred_by_schedule";
        case SyncReplicaFilePayloadStoreScrubDisposition::Empty:
            return "empty";
        case SyncReplicaFilePayloadStoreScrubDisposition::DeferredLeaseBusy:
            return "deferred_lease_busy";
        case SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredStaleSnapshot:
            return "deferred_stale_snapshot";
        case SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredTransientCapacity:
            return "deferred_transient_capacity";
        case SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredPublicationFailure:
            return "deferred_publication_failure";
        case SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredAttemptFailure:
            return "deferred_attempt_failure";
        case SyncReplicaFilePayloadStoreScrubDisposition::Advanced:
            return "advanced";
    }
    return "unknown";
}

void validate_sync_replica_file_payload_store_limits_or_throw(
    const SyncReplicaFilePayloadStoreLimits& limits) {
    if (limits.max_entries == 0U ||
        limits.max_entries > kSyncReplicaFilePayloadStoreMaxEntries) {
        throw std::invalid_argument(
            "sync replica file payload store entry limit is invalid");
    }
    if (limits.max_payload_bytes == 0U ||
        limits.max_indexed_bytes == 0U ||
        limits.max_payload_bytes > limits.max_indexed_bytes ||
        limits.max_payload_bytes > kSha256MaximumMessageBytes ||
        limits.max_indexed_bytes > kMaximumPersistentInteger) {
        throw std::invalid_argument(
            "sync replica file payload store byte limits are invalid");
    }
    // A complete payload is retained and streamed by descriptor. Individual
    // compatibility copies and wire ranges perform their own size_t checks;
    // the durable file extent itself is not one memory allocation.
    if (limits.max_transient_entries == 0U ||
        limits.max_transient_entries >
            kSyncReplicaFilePayloadStoreMaxTransientEntries) {
        throw std::invalid_argument(
            "sync replica file payload store transient-entry limit is invalid");
    }
    if (limits.max_transient_bytes == 0U ||
        limits.max_transient_bytes > kMaximumPersistentInteger) {
        throw std::invalid_argument(
            "sync replica file payload store transient-byte limit is invalid");
    }
    const bool scrub_disabled =
        limits.max_scrub_bytes_per_attempt == 0U &&
        limits.max_scrub_entries_per_attempt == 0U;
    const bool scrub_enabled =
        limits.max_scrub_bytes_per_attempt != 0U &&
        limits.max_scrub_entries_per_attempt != 0U &&
        limits.max_scrub_bytes_per_attempt <= limits.max_indexed_bytes &&
        limits.max_scrub_entries_per_attempt <= limits.max_entries;
    if (!scrub_disabled && !scrub_enabled) {
        throw std::invalid_argument(
            "sync replica file payload store scrub limits are invalid");
    }
}

SyncReplicaFilePayloadStoreLimits
sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
    std::uint64_t max_payload_bytes,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload store limit label must not be empty");
    }
    if (max_payload_bytes == 0U ||
        max_payload_bytes > kSyncReplicaMaximumPayloadExtentBytes ||
        max_payload_bytes > kMaximumPersistentInteger / 2U) {
        throw std::invalid_argument(
            label + " payload ceiling cannot reserve exact assembly space");
    }
    SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries =
        kSyncReplicaFilePayloadStoreProductionMaxEntries;
    limits.max_payload_bytes = max_payload_bytes;
    // This is a comparison frontier only. No buffer, file, or filesystem
    // reservation is sized to it. Actual retained bytes remain bounded by the
    // selected filesystem, quota, and future best-effort retention policy.
    limits.max_indexed_bytes =
        kSyncReplicaFilePayloadStoreProductionMaxIndexedBytes;
    limits.max_transient_bytes = std::max<std::uint64_t>(
        limits.max_transient_bytes, max_payload_bytes * 2U);
    limits.max_scrub_bytes_per_attempt = 4ULL * 1024ULL * 1024ULL;
    limits.max_scrub_entries_per_attempt = 4U;
    validate_sync_replica_file_payload_store_limits_or_throw(limits);
    return limits;
}

SyncReplicaFilePayloadStoreContentDefinedProjection::
SyncReplicaFilePayloadStoreContentDefinedProjection() noexcept = default;

SyncReplicaFilePayloadStoreContentDefinedProjection::
SyncReplicaFilePayloadStoreContentDefinedProjection(
    SyncReplicaFilePayloadStoreContentDefinedProjection&&) noexcept = default;

SyncReplicaFilePayloadStoreContentDefinedProjection&
SyncReplicaFilePayloadStoreContentDefinedProjection::operator=(
    SyncReplicaFilePayloadStoreContentDefinedProjection&&) noexcept = default;

SyncReplicaFilePayloadStoreContentDefinedProjection::~
SyncReplicaFilePayloadStoreContentDefinedProjection() noexcept = default;

bool SyncReplicaFilePayloadStoreContentDefinedProjection::active() const noexcept {
    return static_cast<bool>(state_);
}

const SyncReplicaFilePayloadStoreContentDefinedProjection::State&
SyncReplicaFilePayloadStoreContentDefinedProjection::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica content-defined projection label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " content-defined projection is inactive");
    }
    return *state_;
}

const std::string&
SyncReplicaFilePayloadStoreContentDefinedProjection::content_sha256() const {
    return require_state_or_throw(
               "sync replica content-defined projection content identity")
        .content_sha256;
}

std::uint64_t
SyncReplicaFilePayloadStoreContentDefinedProjection::total_size_bytes() const {
    return require_state_or_throw(
               "sync replica content-defined projection total size")
        .metadata.size_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreContentDefinedProjection::next_offset_bytes() const {
    return require_state_or_throw(
               "sync replica content-defined projection next offset")
        .accumulator.consumed_bytes();
}

std::uint64_t
SyncReplicaFilePayloadStoreContentDefinedProjection::completed_chunk_bytes()
    const {
    return require_state_or_throw(
               "sync replica content-defined projection completed bytes")
        .accumulator.completed_chunk_bytes();
}

const SyncReplicaContentDefinedChunkingParameters&
SyncReplicaFilePayloadStoreContentDefinedProjection::parameters() const {
    return require_state_or_throw(
               "sync replica content-defined projection parameters")
        .parameters;
}

const SyncPosixRegularFileSnapshotMetadata&
SyncReplicaFilePayloadStoreContentDefinedProjection::metadata() const {
    return require_state_or_throw(
               "sync replica content-defined projection metadata")
        .metadata;
}

const std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk>&
SyncReplicaFilePayloadStoreContentDefinedProjection::completed_chunks() const {
    return require_state_or_throw(
               "sync replica content-defined projection completed chunks")
        .accumulator.chunks();
}

SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint
SyncReplicaFilePayloadStoreContentDefinedProjection::checkpoint() const {
    const State& state = require_state_or_throw(
        "sync replica content-defined projection checkpoint");
    return state.accumulator.checkpoint(
        state.content_sha256, state.metadata);
}

void SyncReplicaFilePayloadStoreContentDefinedProjection::
    restore_checkpoint_or_throw(
        SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint
            checkpoint,
        std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "content-defined projection checkpoint restore label must not be empty");
    }
    if (state_) {
        throw std::logic_error(
            label + " cannot replace an active content-defined projection");
    }
    if (!is_lowercase_sha256_hex(checkpoint.content_sha256) ||
        checkpoint.total_size_bytes == 0U ||
        checkpoint.metadata.size_bytes != checkpoint.total_size_bytes ||
        checkpoint.next_offset_bytes == 0U ||
        checkpoint.next_offset_bytes >= checkpoint.total_size_bytes) {
        throw std::invalid_argument(
            label + " is not an exact nonterminal payload checkpoint");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        checkpoint.metadata, checkpoint.total_size_bytes,
        label + " metadata");
    validate_resumable_sha256_checkpoint_or_throw(
        checkpoint.whole_hash, label + " whole hash");
    validate_resumable_sha256_checkpoint_or_throw(
        checkpoint.current_chunk_hash, label + " current chunk hash");
    validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
        checkpoint.parameters, checkpoint.chunker,
        label + " rolling chunker");
    state_ = std::make_unique<State>(std::move(checkpoint), label);
}

SyncReplicaFilePayloadStoreOpenedPayload::
SyncReplicaFilePayloadStoreOpenedPayload(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaFilePayloadStoreOpenedPayload::
SyncReplicaFilePayloadStoreOpenedPayload(
    SyncReplicaFilePayloadStoreOpenedPayload&&) noexcept = default;

SyncReplicaFilePayloadStoreOpenedPayload&
SyncReplicaFilePayloadStoreOpenedPayload::operator=(
    SyncReplicaFilePayloadStoreOpenedPayload&&) noexcept = default;

SyncReplicaFilePayloadStoreOpenedPayload::~
SyncReplicaFilePayloadStoreOpenedPayload() noexcept = default;

bool SyncReplicaFilePayloadStoreOpenedPayload::active() const noexcept {
    return static_cast<bool>(state_);
}

const SyncReplicaFilePayloadStoreOpenedPayload::State&
SyncReplicaFilePayloadStoreOpenedPayload::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica opened payload label must not be empty");
    }
    if (!state_ || state_->descriptor < 0) {
        throw std::logic_error(
            std::string(label) + " opened payload is inactive");
    }
    return *state_;
}

int SyncReplicaFilePayloadStoreOpenedPayload::borrowed_descriptor() const {
    return require_state_or_throw(
               "sync replica opened payload descriptor")
        .descriptor;
}

std::uint64_t SyncReplicaFilePayloadStoreOpenedPayload::size_bytes() const {
    return require_state_or_throw(
               "sync replica opened payload size")
        .metadata.size_bytes;
}

const std::string&
SyncReplicaFilePayloadStoreOpenedPayload::content_sha256() const {
    return require_state_or_throw(
               "sync replica opened payload digest")
        .content_sha256;
}

const SyncPosixRegularFileSnapshotMetadata&
SyncReplicaFilePayloadStoreOpenedPayload::metadata() const {
    return require_state_or_throw(
               "sync replica opened payload metadata")
        .metadata;
}

SyncReplicaFilePayloadStoreRange
SyncReplicaFilePayloadStoreOpenedPayload::copy_range_or_throw(
    std::uint64_t offset_bytes,
    std::uint64_t maximum_range_bytes,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (maximum_range_bytes == 0U) {
        throw std::invalid_argument(label + " range byte limit is zero");
    }
    if (offset_bytes > state.metadata.size_bytes ||
        (offset_bytes == state.metadata.size_bytes &&
         state.metadata.size_bytes != 0U)) {
        throw std::invalid_argument(
            label + " range offset does not name retained payload bytes");
    }
    const std::uint64_t range_bytes = std::min<std::uint64_t>(
        maximum_range_bytes, state.metadata.size_bytes - offset_bytes);
    CopiedFileRange copied = copy_hash_regular_file_range_or_throw(
        state.descriptor, state.status, offset_bytes, range_bytes, label);
    if (offset_bytes == 0U && range_bytes == state.metadata.size_bytes &&
        copied.chunk_sha256 != state.content_sha256) {
        if (state.verification_cache) {
            (void)retain_process_integrity_fault(
                *state.verification_cache, state.content_sha256,
                copied.chunk_sha256);
        }
        throw SyncReplicaFilePayloadStoreIntegrityError(
            state.content_sha256, copied.chunk_sha256, false,
            label + " complete range discovered payload corruption");
    }
    return {
        state.content_sha256,
        state.metadata.size_bytes,
        offset_bytes,
        std::move(copied.chunk_sha256),
        std::move(copied.bytes),
    };
}

std::string
SyncReplicaFilePayloadStoreOpenedPayload::copy_exact_range_into_or_throw(
    std::uint64_t offset_bytes,
    std::span<char> destination,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    const std::uint64_t range_bytes = size_to_u64_or_throw(
        destination.size(), label + " exact destination range");
    if (offset_bytes > state.metadata.size_bytes ||
        range_bytes > state.metadata.size_bytes - offset_bytes ||
        (range_bytes == 0U &&
         (offset_bytes != 0U || state.metadata.size_bytes != 0U))) {
        throw std::invalid_argument(
            label + " exact destination does not name retained payload bytes");
    }
    std::string chunk_sha256 =
        copy_hash_regular_file_range_into_or_throw(
            state.descriptor, state.status, offset_bytes, destination, label);
    if (offset_bytes == 0U && range_bytes == state.metadata.size_bytes &&
        chunk_sha256 != state.content_sha256) {
        if (state.verification_cache) {
            (void)retain_process_integrity_fault(
                *state.verification_cache, state.content_sha256,
                chunk_sha256);
        }
        throw SyncReplicaFilePayloadStoreIntegrityError(
            state.content_sha256, chunk_sha256, false,
            label + " complete range discovered payload corruption during direct fill");
    }
    return chunk_sha256;
}

SyncReplicaFilePayloadStoreContentDefinedManifest
SyncReplicaFilePayloadStoreOpenedPayload::content_defined_manifest_or_throw(
    SyncReplicaContentDefinedChunkingParameters parameters,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    ContentDefinedDigestProjection projection =
        hash_regular_file_content_defined_chunks_or_throw(
            state.descriptor, state.status, parameters, label);
    if (projection.whole_sha256 != state.content_sha256) {
        if (state.verification_cache) {
            (void)retain_process_integrity_fault(
                *state.verification_cache, state.content_sha256,
                projection.whole_sha256);
        }
        throw SyncReplicaFilePayloadStoreIntegrityError(
            state.content_sha256, projection.whole_sha256, false,
            label +
                " content-defined projection discovered payload corruption");
    }
    return {
        state.content_sha256,
        state.metadata.size_bytes,
        parameters,
        std::move(projection.chunks),
    };
}

SyncReplicaFilePayloadStoreContentDefinedProjectionStep
SyncReplicaFilePayloadStoreOpenedPayload::
advance_content_defined_projection_or_throw(
    SyncReplicaFilePayloadStoreContentDefinedProjection& projection,
    SyncReplicaContentDefinedChunkingParameters parameters,
    std::uint64_t maximum_step_bytes,
    std::string_view label_view) const {
    const State& source = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (maximum_step_bytes == 0U) {
        throw std::invalid_argument(
            label + " content-defined projection step budget must be positive");
    }

    if (!projection.state_) {
        projection.state_ = std::make_unique<
            SyncReplicaFilePayloadStoreContentDefinedProjection::State>(
                source.content_sha256, source.metadata, parameters, label);
    } else if (
        projection.state_->content_sha256 != source.content_sha256 ||
        projection.state_->metadata != source.metadata ||
        projection.state_->parameters != parameters) {
        projection.state_.reset();
        throw PayloadStoreObservationStaleError(
            label +
            " resumed content-defined projection does not bind this exact payload observation");
    }

    auto& progress = *projection.state_;
    const std::uint64_t before_bytes =
        progress.accumulator.consumed_bytes();
    const std::size_t before_chunks = progress.accumulator.chunks().size();
    if (before_bytes >= source.metadata.size_bytes) {
        projection.state_.reset();
        throw std::logic_error(
            label + " active content-defined projection has no remaining bytes");
    }
    const std::uint64_t step_bytes = std::min<std::uint64_t>(
        maximum_step_bytes, source.metadata.size_bytes - before_bytes);
    const std::uint64_t step_end = before_bytes + step_bytes;

    try {
        std::array<char, kStreamingBufferBytes> buffer{};
        while (progress.accumulator.consumed_bytes() < step_end) {
            const std::uint64_t remaining =
                step_end - progress.accumulator.consumed_bytes();
            const std::size_t requested = static_cast<std::size_t>(
                std::min<std::uint64_t>(remaining, buffer.size()));
            ssize_t read_count;
            do {
                read_count = ::pread(
                    source.descriptor, buffer.data(), requested,
                    static_cast<off_t>(
                        progress.accumulator.consumed_bytes()));
            } while (read_count < 0 && errno == EINTR);
            if (read_count < 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " bounded content-defined read failed: " +
                    error_text(error));
            }
            if (read_count == 0) {
                throw PayloadStoreObservationStaleError(
                    label +
                    " became truncated while bounded content-defined bytes were read");
            }
            const std::size_t got = static_cast<std::size_t>(read_count);
            if (static_cast<std::uint64_t>(got) > remaining) {
                throw std::runtime_error(
                    label +
                    " bounded content-defined read crossed its exact step extent");
            }
            progress.accumulator.consume_or_throw(
                std::string_view(buffer.data(), got), label);
        }

        struct stat after{};
        if (::fstat(source.descriptor, &after) != 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " final bounded projection fstat failed: " +
                error_text(error));
        }
        if (!same_regular_file_observation(source.status, after)) {
            throw PayloadStoreObservationStaleError(
                label + " changed while bounded content-defined bytes were read");
        }

        SyncReplicaFilePayloadStoreContentDefinedProjectionStep out;
        out.hashed_bytes =
            progress.accumulator.consumed_bytes() - before_bytes;
        if (progress.accumulator.consumed_bytes() ==
            source.metadata.size_bytes) {
            ContentDefinedDigestProjection completed =
                progress.accumulator.finish_or_throw(label);
            if (completed.whole_sha256 != source.content_sha256) {
                if (source.verification_cache) {
                    (void)retain_process_integrity_fault(
                        *source.verification_cache, source.content_sha256,
                        completed.whole_sha256);
                }
                throw SyncReplicaFilePayloadStoreIntegrityError(
                    source.content_sha256, completed.whole_sha256, false,
                    label +
                        " bounded content-defined projection discovered payload corruption");
            }
            if (completed.chunks.size() < before_chunks) {
                throw std::logic_error(
                    label + " completed projection lost prior chunk progress");
            }
            out.newly_completed_chunk_count = static_cast<std::uint64_t>(
                completed.chunks.size() - before_chunks);
            out.completed_whole_hash = completed.whole_checkpoint;
            out.completed_manifest =
                SyncReplicaFilePayloadStoreContentDefinedManifest{
                    source.content_sha256,
                    source.metadata.size_bytes,
                    parameters,
                    std::move(completed.chunks),
                };
            projection.state_.reset();
            return out;
        }

        const std::size_t after_chunks =
            progress.accumulator.chunks().size();
        if (after_chunks < before_chunks) {
            throw std::logic_error(
                label + " bounded projection moved its chunk frontier backward");
        }
        out.newly_completed_chunk_count = static_cast<std::uint64_t>(
            after_chunks - before_chunks);
        return out;
    } catch (...) {
        projection.state_.reset();
        throw;
    }
}

SyncReplicaFilePayloadStoreTargetedAccess::
SyncReplicaFilePayloadStoreTargetedAccess(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}


SyncReplicaFilePayloadStoreTargetedAccess::
SyncReplicaFilePayloadStoreTargetedAccess(
    SyncReplicaFilePayloadStoreTargetedAccess&&) noexcept = default;

SyncReplicaFilePayloadStoreTargetedAccess&
SyncReplicaFilePayloadStoreTargetedAccess::operator=(
    SyncReplicaFilePayloadStoreTargetedAccess&&) noexcept = default;

SyncReplicaFilePayloadStoreTargetedAccess::~
SyncReplicaFilePayloadStoreTargetedAccess() noexcept = default;

bool SyncReplicaFilePayloadStoreTargetedAccess::active() const noexcept {
    return static_cast<bool>(state_);
}

SyncReplicaFilePayloadStoreTargetedAccess::State&
SyncReplicaFilePayloadStoreTargetedAccess::require_state_or_throw(
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica targeted payload access label must not be empty");
    }
    if (!state_ || state_->root_descriptor.get() < 0) {
        throw std::logic_error(
            std::string(label) + " targeted payload access is inactive");
    }
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority,
            std::string(label) + " targeted payload access owner");
    return *state_;
}

std::optional<std::uint64_t>
SyncReplicaFilePayloadStoreTargetedAccess::
    observe_optional_payload_size_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label_view) {
    State& access = require_state_or_throw(label_view);
    const std::string label(label_view);
    reject_process_integrity_fault_for_payload_or_throw(
        access.verification_cache, operation.content_sha256, label,
        "targeted");
    std::optional<TargetedPayloadObservation> observed =
        open_targeted_payload_observation_or_throw(
            access.root_authority, access.root_descriptor.get(),
            access.resolution_capability, access.mount_identity, access.limits,
            access.folder_id, access.identity_basename,
            access.expected_identity, access.identity_status,
            access.durability, operation, label);
    if (!observed.has_value()) return std::nullopt;
    return operation.size_bytes;
}

std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
SyncReplicaFilePayloadStoreTargetedAccess::
    open_optional_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label_view) {
    State& access = require_state_or_throw(label_view);
    const std::string label(label_view);
    reject_process_integrity_fault_for_payload_or_throw(
        access.verification_cache, operation.content_sha256, label,
        "targeted");
    std::optional<TargetedPayloadObservation> observed =
        open_targeted_payload_observation_or_throw(
            access.root_authority, access.root_descriptor.get(),
            access.resolution_capability, access.mount_identity, access.limits,
            access.folder_id, access.identity_basename,
            access.expected_identity, access.identity_status,
            access.durability, operation, label);
    if (!observed.has_value()) return std::nullopt;

    TargetedPayloadObservation& payload = *observed;
    if (synchronizes_store_observation(payload.payload_durability)) {
        fsync_or_throw(
            payload.payload_descriptor.get(), label + " selected payload");
    }
    const SyncPosixRegularFileSnapshotMetadata metadata =
        observe_sync_posix_regular_file_descriptor_or_throw(
            payload.payload_descriptor.get(),
            SyncPosixDescriptorLinkPolicy::stable_named_object,
            label + " selected payload metadata");
    // Lock order is store observation first, exact payload inode second. The
    // descriptor keeps this shared inode lease after the short store lease is
    // released at the return cutpoint.
    acquire_shared_payload_use_lease_or_throw(
        payload.payload_descriptor.get(), label + " selected payload");
    verify_named_regular_file_or_throw(
        access.root_descriptor.get(), operation.content_sha256,
        payload.payload_status, access.root_authority.attestation(),
        label + " selected payload");
    payload.observation_lease.verify_or_throw(
        access.root_authority,
        label + " selected payload descriptor lease cutpoint");
    access.root_authority.verify_or_throw(
        label + " selected payload descriptor root proof");

    auto selected =
        std::make_unique<SyncReplicaFilePayloadStoreOpenedPayload::State>();
    selected->live_capability_registration =
        PayloadStoreLiveCapabilityRegistration(
            access.live_capability_registration.registry(),
            PayloadStoreLiveCapabilityKind::OpenedPayload,
            operation.content_sha256, operation.size_bytes);
    selected->descriptor = payload.payload_descriptor.release();
    selected->status = payload.payload_status;
    selected->metadata = metadata;
    selected->content_sha256 = operation.content_sha256;
    selected->verification_cache = access.verification_cache;
    return SyncReplicaFilePayloadStoreOpenedPayload(std::move(selected));
}

SyncReplicaFilePayloadStoreMutationBatch::
SyncReplicaFilePayloadStoreMutationBatch() noexcept = default;

SyncReplicaFilePayloadStoreMutationBatch::
SyncReplicaFilePayloadStoreMutationBatch(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaFilePayloadStoreMutationBatch::
SyncReplicaFilePayloadStoreMutationBatch(
    SyncReplicaFilePayloadStoreMutationBatch&&) noexcept = default;

SyncReplicaFilePayloadStoreMutationBatch&
SyncReplicaFilePayloadStoreMutationBatch::operator=(
    SyncReplicaFilePayloadStoreMutationBatch&&) noexcept = default;

SyncReplicaFilePayloadStoreMutationBatch::~
SyncReplicaFilePayloadStoreMutationBatch() noexcept = default;

bool SyncReplicaFilePayloadStoreMutationBatch::active() const noexcept {
    return static_cast<bool>(state_);
}

SyncReplicaFilePayloadStoreMutationBatch::State&
SyncReplicaFilePayloadStoreMutationBatch::require_state_or_throw(
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload mutation batch label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " payload mutation batch is inactive");
    }
    return *state_;
}

const SyncReplicaFilePayloadStoreMutationBatch::State&
SyncReplicaFilePayloadStoreMutationBatch::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload mutation batch label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " payload mutation batch is inactive");
    }
    return *state_;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::full_scan_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch full scan count")
        .full_scan_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_hashed_entry_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch scan hashed entry count")
        .scan_hashed_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_hashed_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch scan hashed bytes")
        .scan_hashed_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch scan reused entry count")
        .scan_reused_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_reused_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch scan reused bytes")
        .scan_reused_bytes;
}

std::uint64_t SyncReplicaFilePayloadStoreMutationBatch::
    scan_process_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch process reused entry count")
        .scan_process_reused_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_process_reused_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch process reused bytes")
        .scan_process_reused_bytes;
}

std::uint64_t SyncReplicaFilePayloadStoreMutationBatch::
    scan_durable_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch durable reused entry count")
        .scan_durable_reused_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::scan_durable_reused_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch durable reused bytes")
        .scan_durable_reused_bytes;
}

std::uint64_t SyncReplicaFilePayloadStoreMutationBatch::put_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch put count")
        .put_count;
}

std::uint64_t SyncReplicaFilePayloadStoreMutationBatch::source_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch source bytes")
        .source_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::inserted_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch inserted count")
        .inserted_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::already_present_count() const {
    return require_state_or_throw(
               "sync replica payload mutation batch already-present count")
        .already_present_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::indexed_entry_count() const {
    const State& batch = require_state_or_throw(
        "sync replica payload mutation batch indexed entry count");
    return size_to_u64_or_throw(
        batch.index.entries.size(), batch.label + " indexed entry count");
}

std::uint64_t
SyncReplicaFilePayloadStoreMutationBatch::indexed_bytes() const {
    return require_state_or_throw(
               "sync replica payload mutation batch indexed bytes")
        .index.indexed_bytes;
}

void SyncReplicaFilePayloadStoreMutationBatch::preflight_or_throw(
    std::string_view label_view) const {
    const State& batch = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (batch.poisoned) {
        throw std::logic_error(
            label +
            " payload mutation batch is poisoned after an unreconciled failure");
    }
    batch.mutation_lease.verify_or_throw(
        batch.root_authority, label + " lease cutpoint");
}

void SyncReplicaFilePayloadStoreMutationBatch::
refresh_namespace_after_failure_or_throw(std::string_view phase_view) {
    State& batch = require_state_or_throw(
        "sync replica payload mutation batch failure reconciliation");
    const std::string phase(phase_view);
    if (phase.empty()) {
        throw std::invalid_argument(
            batch.label + " failure reconciliation phase must not be empty");
    }
    batch.poisoned = true;
    batch.mutation_lease.verify_or_throw(
        batch.root_authority,
        batch.label + " " + phase + " pre-scan lease cutpoint");
    const auto record_scan_diagnostics =
        [&](const ScannedPayloadIndex& scanned) {
            batch.scan_hashed_entry_count = checked_add_u64_or_throw(
                batch.scan_hashed_entry_count,
                scanned.scan_hashed_entry_count,
                batch.label + " mutation batch scan hashed entry count");
            batch.scan_hashed_bytes = checked_add_u64_or_throw(
                batch.scan_hashed_bytes, scanned.scan_hashed_bytes,
                batch.label + " mutation batch scan hashed bytes");
            batch.scan_reused_entry_count = checked_add_u64_or_throw(
                batch.scan_reused_entry_count,
                scanned.scan_reused_entry_count,
                batch.label + " mutation batch scan reused entry count");
            batch.scan_reused_bytes = checked_add_u64_or_throw(
                batch.scan_reused_bytes, scanned.scan_reused_bytes,
                batch.label + " mutation batch scan reused bytes");
            batch.scan_process_reused_entry_count = checked_add_u64_or_throw(
                batch.scan_process_reused_entry_count,
                scanned.scan_process_reused_entry_count,
                batch.label +
                    " mutation batch scan process reused entry count");
            batch.scan_process_reused_bytes = checked_add_u64_or_throw(
                batch.scan_process_reused_bytes,
                scanned.scan_process_reused_bytes,
                batch.label + " mutation batch scan process reused bytes");
            batch.scan_durable_reused_entry_count = checked_add_u64_or_throw(
                batch.scan_durable_reused_entry_count,
                scanned.scan_durable_reused_entry_count,
                batch.label +
                    " mutation batch scan durable reused entry count");
            batch.scan_durable_reused_bytes = checked_add_u64_or_throw(
                batch.scan_durable_reused_bytes,
                scanned.scan_durable_reused_bytes,
                batch.label + " mutation batch scan durable reused bytes");
        };
    ScannedPayloadIndex refreshed = scan_store_under_lease_or_throw(
        batch.root_authority, batch.limits, batch.identity_basename,
        batch.expected_identity, batch.mutation_lease,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        batch.label + " " + phase + " namespace scan",
        StoreObservationDurability::Reconcile, nullptr);
    record_scan_diagnostics(refreshed);
    batch.full_scan_count = checked_add_u64_or_throw(
        batch.full_scan_count, 1U,
        batch.label + " mutation batch full scan count");
    if (!refreshed.publication_residues.empty()) {
        remove_scanned_publication_residues_or_throw(
            batch.root_authority, refreshed.publication_residues,
            batch.label + " " + phase + " publication-residue cleanup");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " " + phase + " residue-cleanup lease cutpoint");
        ScannedPayloadIndex rescanned = scan_store_under_lease_or_throw(
            batch.root_authority, batch.limits, batch.identity_basename,
            batch.expected_identity, batch.mutation_lease,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            batch.label + " " + phase + " post-cleanup namespace scan",
            StoreObservationDurability::Reconcile, nullptr);
        record_scan_diagnostics(rescanned);
        refreshed = std::move(rescanned);
        batch.full_scan_count = checked_add_u64_or_throw(
            batch.full_scan_count, 1U,
            batch.label + " mutation batch full scan count");
    }
    batch.index = std::move(refreshed);
    batch.mutation_lease.verify_or_throw(
        batch.root_authority,
        batch.label + " " + phase + " final lease cutpoint");
    batch.poisoned = false;
}

SyncReplicaFilePayloadStoreSnapshot::SyncReplicaFilePayloadStoreSnapshot(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaFilePayloadStoreSnapshot::SyncReplicaFilePayloadStoreSnapshot(
    SyncReplicaFilePayloadStoreSnapshot&&) noexcept = default;

SyncReplicaFilePayloadStoreSnapshot&
SyncReplicaFilePayloadStoreSnapshot::operator=(
    SyncReplicaFilePayloadStoreSnapshot&&) noexcept = default;

SyncReplicaFilePayloadStoreSnapshot::~SyncReplicaFilePayloadStoreSnapshot()
    noexcept = default;

const SyncReplicaFilePayloadStoreSnapshot::State&
SyncReplicaFilePayloadStoreSnapshot::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica durable payload snapshot operation label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " durable payload snapshot is inactive");
    }
    // The shared verification cache is intentionally mutex-free. Enforce the
    // snapshot's documented exact-thread affinity before even reading its
    // revocation epoch; a foreign-thread metadata-only method must not race the
    // originating owner while it records or clears an integrity fault.
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority,
            std::string(label) + " durable payload snapshot owner");
    reject_revoked_snapshot_authority_or_throw(
        state_->verification_cache, state_->issued_integrity_fault_epoch, label);
    return *state_;
}

const std::string& SyncReplicaFilePayloadStoreSnapshot::folder_id() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot folder")
        .folder_id;
}

const fs::path& SyncReplicaFilePayloadStoreSnapshot::root_path() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot root path")
        .root_path;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::entry_count() const {
    const State& state = require_state_or_throw(
        "sync replica durable payload snapshot entry count");
    return static_cast<std::uint64_t>(state.entries.size());
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::indexed_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot indexed bytes")
        .indexed_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::scan_hashed_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot hashed entry count")
        .scan_hashed_entry_count;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::scan_hashed_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot hashed bytes")
        .scan_hashed_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::scan_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot reused entry count")
        .scan_reused_entry_count;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::scan_reused_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot reused bytes")
        .scan_reused_bytes;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::
    scan_process_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot process reused entry count")
        .scan_process_reused_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::scan_process_reused_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot process reused bytes")
        .scan_process_reused_bytes;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::
    scan_durable_reused_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot durable reused entry count")
        .scan_durable_reused_entry_count;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::scan_durable_reused_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot durable reused bytes")
        .scan_durable_reused_bytes;
}

bool SyncReplicaFilePayloadStoreSnapshot::
    verification_checkpoint_deferred_by_transient_capacity() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot checkpoint capacity")
        .verification_checkpoint_deferred_by_transient_capacity;
}

const SyncReplicaFilePayloadStoreScrubReport&
SyncReplicaFilePayloadStoreSnapshot::scrub_report() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot scrub report")
        .scrub_report;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::transient_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient entry count")
        .transient_entry_count;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::transient_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient bytes")
        .transient_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::transient_reserved_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient reserved bytes")
        .transient_reserved_bytes;
}

const std::string&
SyncReplicaFilePayloadStoreSnapshot::transient_namespace_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient namespace digest")
        .transient_namespace_digest;
}

const std::string&
SyncReplicaFilePayloadStoreSnapshot::root_attestation_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot root attestation digest")
        .root_attestation_digest;
}

const std::string&
SyncReplicaFilePayloadStoreSnapshot::snapshot_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot digest")
        .snapshot_digest;
}

const SyncReplicaFilePayloadStoreLimits&
SyncReplicaFilePayloadStoreSnapshot::limits() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot limits")
        .limits;
}

bool SyncReplicaFilePayloadStoreSnapshot::retention_mark_present() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot retention mark presence")
        .retention_mark_present;
}

bool SyncReplicaFilePayloadStoreSnapshot::retention_mark_observation_known() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot retention mark observation")
        .retention_mark_observation_known;
}

bool SyncReplicaFilePayloadStoreSnapshot::retention_mark_usable() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot retention mark usability")
        .retention_mark_usable;
}

const std::optional<SyncReplicaFilePayloadRetentionMark>&
SyncReplicaFilePayloadStoreSnapshot::retention_mark() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot retention mark")
        .retention_mark;
}

const std::optional<std::string>&
SyncReplicaFilePayloadStoreSnapshot::retention_mark_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot retention mark digest")
        .retention_mark_digest;
}

SyncReplicaFileContentInventory
SyncReplicaFilePayloadStoreSnapshot::content_inventory() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot content inventory")
        .content_inventory;
}

std::optional<std::uint64_t>
SyncReplicaFilePayloadStoreSnapshot::payload_size_or_none(
    std::string_view content_sha256) const {
    const State& state = require_state_or_throw(
        "sync replica durable payload snapshot size lookup");
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            "sync replica durable payload snapshot size lookup digest is invalid");
    }
    const PayloadIndexEntry* entry = find_entry(state.entries, content_sha256);
    if (entry == nullptr) return std::nullopt;
    return entry->size_bytes;
}

SyncReplicaFilePayloadStoreOpenedPayload
SyncReplicaFilePayloadStoreSnapshot::open_payload_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(label + " requires a file operation");
    }
    if (!is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            label + " operation content digest is invalid");
    }
    if (operation.size_bytes > state.limits.max_payload_bytes) {
        throw std::length_error(
            label + " operation exceeds the durable payload budget");
    }
    const PayloadIndexEntry* indexed =
        find_entry(state.entries, operation.content_sha256);
    if (indexed == nullptr) {
        throw std::runtime_error(
            label + " has no indexed payload for the claimed operation");
    }
    if (indexed->size_bytes != operation.size_bytes) {
        throw std::logic_error(
            label + " indexed payload size disagrees with the claimed operation");
    }

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    state.root_authority.verify_or_throw(label + " root preflight");
    StoreLease observation_lease = acquire_store_lease_or_throw(
        state.root_authority, state.identity_basename,
        state.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        label + " selected payload", state.durability);
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            state.root_authority, label + " selected payload");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), operation.content_sha256, state.root_path,
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(),
        label + " selected payload");
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, state.root_authority.attestation(),
        label + " selected payload");
    if (static_cast<std::uint64_t>(opened.status.st_size) !=
        operation.size_bytes) {
        throw std::runtime_error(
            label + " selected payload changed size after indexing");
    }

    if (!same_regular_file_observation(indexed->status, opened.status)) {
        const StreamedFileDigest revalidated =
            stream_hash_regular_file_or_throw(
                file.get(), opened.status, std::nullopt,
                label + " selected payload replacement revalidation");
        if (revalidated.sha256 != operation.content_sha256) {
            throw std::runtime_error(
                label + " selected payload changed after indexing");
        }
    }
    const SyncPosixRegularFileSnapshotMetadata metadata =
        observe_sync_posix_regular_file_descriptor_or_throw(
            file.get(), SyncPosixDescriptorLinkPolicy::stable_named_object,
            label + " selected payload metadata");
    acquire_shared_payload_use_lease_or_throw(
        file.get(), label + " selected payload");
    verify_named_regular_file_or_throw(
        root_descriptor.get(), operation.content_sha256, opened.status,
        state.root_authority.attestation(), label + " selected payload");
    observation_lease.verify_or_throw(
        state.root_authority,
        label + " selected payload descriptor lease cutpoint");
    state.root_authority.verify_or_throw(label + " final root proof");

    auto selected =
        std::make_unique<SyncReplicaFilePayloadStoreOpenedPayload::State>();
    selected->live_capability_registration =
        PayloadStoreLiveCapabilityRegistration(
            state.live_capability_registration.registry(),
            PayloadStoreLiveCapabilityKind::OpenedPayload,
            operation.content_sha256, operation.size_bytes);
    selected->descriptor = file.release();
    selected->status = opened.status;
    selected->metadata = metadata;
    selected->content_sha256 = operation.content_sha256;
    selected->verification_cache = state.verification_cache;
    return SyncReplicaFilePayloadStoreOpenedPayload(std::move(selected));
}

std::string
SyncReplicaFilePayloadStoreSnapshot::copy_payload_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::string_view label_view) const {
    const SyncReplicaFilePayloadStoreRange range =
        copy_payload_range_for_operation_or_throw(
            operation, 0U,
            std::max<std::uint64_t>(operation.size_bytes, 1U), label_view);
    if (range.offset_bytes != 0U ||
        range.total_size_bytes != operation.size_bytes ||
        range.bytes.size() != operation.size_bytes ||
        range.chunk_sha256 != operation.content_sha256) {
        throw std::logic_error(
            std::string(label_view) +
            " whole-payload range did not preserve exact content identity");
    }
    return range.bytes;
}

SyncReplicaFilePayloadStoreRange
SyncReplicaFilePayloadStoreSnapshot::copy_payload_range_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::uint64_t offset_bytes,
    std::uint64_t maximum_range_bytes,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(label + " requires a file operation");
    }
    if (!is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            label + " operation content digest is invalid");
    }
    if (operation.size_bytes > state.limits.max_payload_bytes) {
        throw std::length_error(
            label + " operation exceeds the durable payload budget");
    }
    if (maximum_range_bytes == 0U) {
        throw std::invalid_argument(label + " range byte limit is zero");
    }
    if (offset_bytes > operation.size_bytes) {
        throw std::invalid_argument(label + " range offset exceeds payload size");
    }
    const PayloadIndexEntry* indexed =
        find_entry(state.entries, operation.content_sha256);
    if (indexed == nullptr) {
        throw std::runtime_error(
            label + " has no indexed payload for the claimed operation");
    }
    if (indexed->size_bytes != operation.size_bytes) {
        throw std::logic_error(
            label + " indexed payload size disagrees with the claimed operation");
    }

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    state.root_authority.verify_or_throw(label + " root preflight");
    StoreLease observation_lease = acquire_store_lease_or_throw(
        state.root_authority, state.identity_basename,
        state.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        label + " selected payload", state.durability);
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            state.root_authority, label + " selected payload");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), operation.content_sha256, state.root_path,
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(),
        label + " selected payload");
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, state.root_authority.attestation(),
        label + " selected payload");
    if (static_cast<std::uint64_t>(opened.status.st_size) !=
        operation.size_bytes) {
        throw std::runtime_error(
            label + " selected payload changed size after indexing");
    }
    acquire_shared_payload_use_lease_or_throw(
        file.get(), label + " selected payload");
    const std::uint64_t range_size = std::min<std::uint64_t>(
        maximum_range_bytes, operation.size_bytes - offset_bytes);

    CopiedFileRange copied;
    if (same_regular_file_observation(indexed->status, opened.status)) {
        copied = copy_hash_regular_file_range_or_throw(
            file.get(), opened.status, offset_bytes, range_size,
            label + " selected payload");
    } else {
        // Preserve the pre-range snapshot contract for an exact atomic
        // re-publication. This slow path is intentionally complete: a changed
        // inode or timestamp cannot inherit the old digest merely because the
        // requested range happens to match.
        StreamedFileDigest revalidated = stream_hash_regular_file_or_throw(
            file.get(), opened.status,
            std::pair<std::uint64_t, std::uint64_t>{
                offset_bytes, range_size},
            label + " selected payload replacement revalidation");
        if (revalidated.sha256 != operation.content_sha256) {
            throw std::runtime_error(
                label + " selected payload changed after indexing");
        }
        copied.chunk_sha256 = sha256_hex(revalidated.selected_bytes);
        copied.bytes = std::move(revalidated.selected_bytes);
    }
    verify_named_regular_file_or_throw(
        root_descriptor.get(), operation.content_sha256, opened.status,
        state.root_authority.attestation(), label + " selected payload");
    observation_lease.verify_or_throw(
        state.root_authority,
        label + " selected payload range lease cutpoint");
    state.root_authority.verify_or_throw(label + " final root proof");
    return SyncReplicaFilePayloadStoreRange{
        operation.content_sha256,
        operation.size_bytes,
        offset_bytes,
        copied.chunk_sha256,
        copied.bytes};
}

void SyncReplicaFilePayloadStoreSnapshot::require_folder_or_throw(
    std::string_view folder_id,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " service folder_id is invalid");
    }
    if (state.folder_id != folder_id) {
        throw std::invalid_argument(
            std::string(label) +
            " durable payload snapshot does not match service folder identity");
    }
}

void SyncReplicaFilePayloadStoreSnapshot::preflight_or_throw(
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    state.root_authority.verify_or_throw(
        std::string(label) + " root authority");
}

SyncReplicaFilePayloadStore::SyncReplicaFilePayloadStore(
    std::string folder_id,
    fs::path absolute_root_directory,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    SyncReplicaFilePayloadStoreLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload store label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    switch (disposition) {
        case SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly:
        case SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing:
        case SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect:
            break;
        default:
            throw std::invalid_argument(
                label + " payload-store open disposition is invalid");
    }
    validate_sync_replica_file_payload_store_limits_or_throw(limits);

    auto state = std::make_unique<State>();
    state->folder_id = std::move(folder_id);
    state->disposition = disposition;
    state->limits = limits;
    state->label = std::move(label);
    state->identity_basename = std::string(
        kStandaloneStoreIdentityBasenameV2ReaderFenceV1);
    state->legacy_identity_basename = std::string(
        kStandaloneStoreIdentityBasenameV2LegacyReader);
    state->expected_identity =
        standalone_store_identity_payload(state->folder_id);
    state->allow_existing_payload_adoption = true;
    state->root_authority = SyncDirectoryAuthority::open_or_throw(
        absolute_root_directory, state->label + " root");
    state->root_path = state->root_authority.path();
    state->root_attestation_digest =
        sync_directory_attestation_digest_or_throw(
            state->root_authority.attestation());
    state->live_capability_registry =
        acquire_payload_store_live_capability_registry_or_throw(
            state->root_attestation_digest, state->identity_basename,
            state->expected_identity, state->label);
    state_ = std::move(state);
}

SyncReplicaFilePayloadStore::SyncReplicaFilePayloadStore(
    SyncReplicaDeploymentIdentity deployment_identity,
    fs::path absolute_root_directory,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    SyncReplicaFilePayloadStoreLimits limits,
    std::string label)
    : SyncReplicaFilePayloadStore(
          deployment_identity.folder_id, std::move(absolute_root_directory),
          disposition, limits, std::move(label)) {
    validate_sync_replica_deployment_identity_or_throw(
        deployment_identity, state_->label + " deployment identity");
    state_->identity_basename = std::string(
        kProductStoreIdentityBasenameV3ReaderFenceV1);
    state_->legacy_identity_basename = std::string(
        kProductStoreIdentityBasenameV3LegacyReader);
    state_->expected_identity = product_store_identity_payload_or_throw(
        deployment_identity, state_->label + " deployment identity");
    state_->allow_existing_payload_adoption = false;
    // The delegating standalone constructor has not issued any capability.
    // Rebind its temporary standalone scope to the exact product identity
    // before this fully constructed owner can expose snapshot/access authority.
    state_->live_capability_registry =
        acquire_payload_store_live_capability_registry_or_throw(
            state_->root_attestation_digest, state_->identity_basename,
            state_->expected_identity, state_->label);
}

SyncReplicaFilePayloadStore::~SyncReplicaFilePayloadStore() noexcept = default;

const std::string& SyncReplicaFilePayloadStore::folder_id() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->folder_id;
}

const fs::path& SyncReplicaFilePayloadStore::root_path() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->root_path;
}

const SyncReplicaFilePayloadStoreLimits&
SyncReplicaFilePayloadStore::limits() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->limits;
}

void SyncReplicaFilePayloadStore::require_exact_snapshot_origin_or_throw(
    const SyncReplicaFilePayloadStoreSnapshot& snapshot,
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica payload snapshot origin label must not be empty");
    }

    const SyncReplicaFilePayloadStoreSnapshot::State& candidate =
        snapshot.require_state_or_throw(label + " candidate");
    state_->root_authority.verify_or_throw(label + " retained store root");
    candidate.root_authority.verify_or_throw(label + " candidate root");

    // The verification cache remains the exact retained-owner identity. The
    // live-capability registry is deliberately shared by independently opened
    // owners over this exact process/store scope, so registry identity alone
    // cannot authorize snapshot handoff. Two handles may legitimately attest
    // the same durable folder, root, limits, and marker while owning independent
    // integrity epochs. Treating their snapshots as interchangeable would let
    // one owner bypass another owner's active fail-closed witness. The remaining
    // comparisons make accidental structural drift fail explicitly rather than
    // relying only on the verification-cache pointer.
    if (!candidate.verification_cache ||
        candidate.verification_cache.get() !=
            state_->verification_cache.get() ||
        !candidate.live_capability_registration.registry() ||
        candidate.live_capability_registration.registry().get() !=
            state_->live_capability_registry.get() ||
        candidate.folder_id != state_->folder_id ||
        candidate.root_path != state_->root_path ||
        candidate.root_attestation_digest !=
            state_->root_attestation_digest ||
        candidate.limits != state_->limits) {
        throw std::invalid_argument(
            label +
            " payload snapshot was not issued by the exact retained store owner");
    }
}

SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
SyncReplicaFilePayloadStore::
live_capability_cutpoint_excluding_snapshot_or_throw(
    const SyncReplicaFilePayloadStoreSnapshot& snapshot,
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica live-capability cutpoint label must not be empty");
    }

    require_exact_snapshot_origin_or_throw(
        snapshot, label + " exact snapshot origin");
    const SyncReplicaFilePayloadStoreSnapshot::State& candidate =
        snapshot.require_state_or_throw(label + " planner snapshot");
    const PayloadStoreLiveCapabilityRegistration& registration =
        candidate.live_capability_registration;
    if (!state_->live_capability_registry ||
        !registration.registry() ||
        registration.registry().get() !=
            state_->live_capability_registry.get() ||
        registration.registration_id() == 0U) {
        throw std::logic_error(
            label + " planner snapshot live-capability registration is invalid");
    }
    return state_->live_capability_registry->
        cutpoint_excluding_snapshot_or_throw(
            registration.registration_id(), label);
}

void SyncReplicaFilePayloadStore::
verify_writer_fenced_retention_snapshot_or_throw(
    const SyncReplicaFilePayloadStoreSnapshot& snapshot,
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "writer-fenced retention snapshot label must not be empty");
    }
    require_exact_snapshot_origin_or_throw(
        snapshot, label + " exact snapshot origin");
    const SyncReplicaFilePayloadStoreSnapshot::State& candidate =
        snapshot.require_state_or_throw(label + " retained snapshot");
    if (!candidate.retained_writer_fence ||
        candidate.retained_writer_fence->mode() !=
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation) {
        throw std::logic_error(
            label + " snapshot does not retain the exact writer fence");
    }
    candidate.retained_writer_fence->verify_or_throw(
        candidate.root_authority, label + " identity lease cutpoint");
    candidate.root_authority.verify_or_throw(label + " snapshot root proof");
    state_->root_authority.verify_or_throw(label + " retained-root proof");
}

bool SyncReplicaFilePayloadStore::
writer_fenced_payload_use_exclusive_available_or_throw(
    const SyncReplicaFilePayloadStoreSnapshot& snapshot,
    std::string_view content_sha256,
    std::uint64_t size_bytes,
    std::string_view label_view) const {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            std::string(label_view) +
            " writer-fenced payload-use probe digest is invalid");
    }
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "writer-fenced payload-use probe label must not be empty");
    }
    verify_writer_fenced_retention_snapshot_or_throw(
        snapshot, label + " opening cutpoint");
    const SyncReplicaFilePayloadStoreSnapshot::State& candidate =
        snapshot.require_state_or_throw(label + " retained snapshot");
    const PayloadIndexEntry* indexed =
        find_entry(candidate.entries, content_sha256);
    if (indexed == nullptr || indexed->size_bytes != size_bytes) {
        throw std::invalid_argument(
            label + " candidate is not one exact retained snapshot entry");
    }

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            candidate.root_authority, label + " retained root");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), content_sha256, candidate.root_path,
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(), label + " candidate");
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, candidate.root_authority.attestation(),
        label + " candidate");
    if (opened.status.st_size < 0 ||
        static_cast<std::uint64_t>(opened.status.st_size) != size_bytes ||
        !same_regular_file_observation(indexed->status, opened.status)) {
        throw PayloadStoreObservationStaleError(
            label + " candidate changed after the writer-fenced scan");
    }

    const bool exclusive_available =
        try_acquire_payload_use_flock_nonblocking_or_throw(
            file.get(), LOCK_EX, label + " candidate");
    verify_named_regular_file_or_throw(
        root_descriptor.get(), std::string(content_sha256), opened.status,
        candidate.root_authority.attestation(), label + " candidate");
    verify_writer_fenced_retention_snapshot_or_throw(
        snapshot, label + " final cutpoint");
    return exclusive_available;
}

SyncReplicaFilePayloadStoreScrubStatus
SyncReplicaFilePayloadStore::scrub_status() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority, state_->label + " scrub status");

    SyncReplicaFilePayloadStoreScrubStatus status;
    status.enabled =
        state_->disposition !=
            SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect &&
        payload_scrub_enabled(state_->limits);
    status.max_bytes_per_attempt =
        state_->limits.max_scrub_bytes_per_attempt;
    status.max_entries_per_attempt =
        state_->limits.max_scrub_entries_per_attempt;
    if (!state_->last_scrub_report.has_value()) return status;

    status.last_report = state_->last_scrub_report;
    const auto now = std::chrono::steady_clock::now();
    status.last_report_age_milliseconds =
        monotonic_age_milliseconds(now, state_->last_scrub_report_at);
    if (state_->last_scrub_cycle_completed_at.has_value()) {
        status.last_completed_cycle_age_milliseconds =
            monotonic_age_milliseconds(
                now, *state_->last_scrub_cycle_completed_at);
    }
    return status;
}

bool SyncReplicaFilePayloadStore::
quarantine_inventory_observation_known() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority,
            state_->label + " quarantine inventory readiness");
    return state_->verification_cache->quarantine_inventory.has_value();
}

SyncReplicaFilePayloadStoreQuarantineInventoryStatus
SyncReplicaFilePayloadStore::quarantine_inventory_status() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority,
            state_->label + " quarantine inventory status");

    SyncReplicaFilePayloadStoreQuarantineInventoryStatus status;
    status.byte_limit = maximum_quarantine_bytes(state_->limits);
    const auto& observed = state_->verification_cache->quarantine_inventory;
    if (!observed.has_value()) return status;

    status.observation_known = true;
    status.last_observation_age_milliseconds =
        monotonic_age_milliseconds(
            std::chrono::steady_clock::now(),
            state_->verification_cache->quarantine_inventory_observed_at);
    status.total_bytes = observed->total_bytes;
    status.entries.reserve(
        static_cast<std::size_t>(observed->entry_count));
    for (std::uint64_t index = 0U;
         index < observed->entry_count;
         ++index) {
        const ProcessQuarantineInventoryEntry& entry =
            observed->entries[static_cast<std::size_t>(index)];
        status.entries.push_back({
            std::string(entry.expected_digest()),
            std::string(entry.observed_digest()),
            entry.size_bytes,
        });
    }
    return status;
}

SyncReplicaFilePayloadStoreTerminalVerificationStatus
SyncReplicaFilePayloadStore::terminal_verification_status() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority,
            state_->label + " terminal-verification status");

    SyncReplicaFilePayloadStoreTerminalVerificationStatus status;
    status.observation_known =
        state_->terminal_verification_observation_known;
    if (!status.observation_known) return status;

    status.pending_entry_count = static_cast<std::uint64_t>(
        state_->terminal_verification_work.size());
    for (const auto& work : state_->terminal_verification_work) {
        status.pending_total_bytes = checked_add_u64_or_throw(
            status.pending_total_bytes, work.total_size_bytes,
            state_->label + " terminal-verification pending bytes");
        status.pending_verified_bytes = checked_add_u64_or_throw(
            status.pending_verified_bytes, work.verified_offset_bytes,
            state_->label + " terminal-verification verified bytes");
    }
    if (!state_->terminal_verification_work.empty()) {
        status.next_work = state_->terminal_verification_work.front();
    }
    return status;
}

SyncReplicaFilePayloadStoreTerminalVerificationStepResult
SyncReplicaFilePayloadStore::
continue_one_pending_terminal_verification_or_throw() {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            store.root_authority,
            store.label + " terminal-verification scheduler step");
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot advance terminal verification");
    }

    SyncReplicaFilePayloadStoreTerminalVerificationStepResult result;
    if (!store.terminal_verification_observation_known) {
        result.disposition =
            SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                ObservationUnknown;
        return result;
    }
    if (store.terminal_verification_work.empty()) {
        result.disposition =
            SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                NoPendingWork;
        return result;
    }

    const SyncReplicaFilePayloadStoreTerminalVerificationWork work =
        store.terminal_verification_work.front();
    result.work_before = work;
    const SyncReplicaFilePayloadStoreStageResult stage =
        continue_staged_payload_prefix_verification_or_throw(
            work.content_sha256, work.total_size_bytes);
    if (stage.content_sha256 != work.content_sha256 ||
        stage.total_size_bytes != work.total_size_bytes ||
        stage.next_offset_bytes != work.total_size_bytes) {
        throw std::logic_error(
            store.label +
            " terminal-verification scheduler received an inconsistent staged result");
    }
    result.verified_offset_after_bytes =
        stage.terminal_verification_verified_offset_bytes;
    result.terminal_verification_steps =
        stage.terminal_verification_steps;
    if (result.verified_offset_after_bytes < work.verified_offset_bytes ||
        result.verified_offset_after_bytes > work.total_size_bytes) {
        throw std::logic_error(
            store.label +
            " terminal-verification scheduler frontier regressed or overflowed");
    }
    const std::uint64_t advanced_bytes =
        result.verified_offset_after_bytes - work.verified_offset_bytes;
    // An exact durable payload may already exist when a stale process-local
    // work projection is selected. Reconciliation then advances the semantic
    // frontier to completion without reading target bytes; do not report that
    // skipped range as hash work.
    result.hashed_bytes = result.terminal_verification_steps == 0U
        ? 0U
        : advanced_bytes;

    switch (stage.disposition) {
        case SyncReplicaFilePayloadStoreStageDisposition::Progress:
            if (result.terminal_verification_steps != 1U ||
                result.hashed_bytes == 0U ||
                result.verified_offset_after_bytes >= work.total_size_bytes ||
                result.hashed_bytes >
                    kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep) {
                throw std::logic_error(
                    store.label +
                    " terminal-verification scheduler progress crossed its bounded contract");
            }
            result.disposition =
                SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    Progress;
            break;
        case SyncReplicaFilePayloadStoreStageDisposition::CompletedInserted:
            if (result.verified_offset_after_bytes != work.total_size_bytes) {
                throw std::logic_error(
                    store.label +
                    " terminal-verification insertion lacks a complete frontier");
            }
            result.disposition =
                SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    CompletedInserted;
            break;
        case SyncReplicaFilePayloadStoreStageDisposition::
                CompletedAlreadyPresent:
            if (result.verified_offset_after_bytes != work.total_size_bytes) {
                throw std::logic_error(
                    store.label +
                    " terminal-verification reconciliation lacks a complete frontier");
            }
            result.disposition =
                SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    CompletedAlreadyPresent;
            break;
    }
    return result;
}

SyncReplicaFilePayloadStoreTargetedAccess
SyncReplicaFilePayloadStore::begin_targeted_access_or_throw(
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica targeted payload access label must not be empty");
    }
    const StoreObservationDurability durability =
        store.disposition ==
                SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect
            ? StoreObservationDurability::ObserveOnly
            : StoreObservationDurability::Reconcile;
    store.root_authority.verify_or_throw(
        label + " source preflight");
    if (synchronizes_store_observation(durability)) {
        ensure_store_identity_or_throw(
            store.root_authority, store.limits, store.identity_basename,
            store.legacy_identity_basename, store.expected_identity,
            store.disposition, store.allow_existing_payload_adoption,
            *store.verification_cache, label);
    }

    SyncDirectoryAuthority targeted_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, label + " root selection");
    StoreLease preflight_lease = acquire_store_lease_or_throw(
        targeted_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        label + " identity cutpoint",
        StoreObservationDurability::ObserveOnly);
    const struct stat identity_status = preflight_lease.identity_status();

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            targeted_root, label + " retained root");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    preflight_lease.verify_or_throw(
        targeted_root, label + " final identity lease cutpoint");
    targeted_root.verify_or_throw(label + " final selected-root proof");
    store.root_authority.verify_or_throw(
        label + " final retained-root proof");

    auto targeted =
        std::make_unique<SyncReplicaFilePayloadStoreTargetedAccess::State>(
            store.folder_id, store.limits, std::move(targeted_root),
            store.identity_basename, store.expected_identity,
            identity_status, durability, std::move(root_descriptor),
            resolution_capability, mount_identity,
            store.verification_cache, store.live_capability_registry);
    return SyncReplicaFilePayloadStoreTargetedAccess(std::move(targeted));
}

std::optional<SyncReplicaSourceManifestCheckpoint>
SyncReplicaFilePayloadStore::
    load_source_manifest_checkpoint_or_none_or_throw(
        std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint load label must not be empty");
    }
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            store.root_authority, label + " owner-thread preflight");
    const StoreObservationDurability durability =
        store.disposition ==
                SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect
            ? StoreObservationDurability::ObserveOnly
            : StoreObservationDurability::Reconcile;
    store.root_authority.verify_or_throw(label + " retained-root preflight");
    if (synchronizes_store_observation(durability)) {
        ensure_store_identity_or_throw(
            store.root_authority, store.limits, store.identity_basename,
            store.legacy_identity_basename, store.expected_identity,
            store.disposition, store.allow_existing_payload_adoption,
            *store.verification_cache, label);
    }

    SyncDirectoryAuthority selected_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, label + " selected root");
    StoreLease lease = acquire_store_lease_or_throw(
        selected_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        label + " identity cutpoint", StoreObservationDurability::ObserveOnly);
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            selected_root, label + " retained root");
    const auto resolution_capability =
        descriptor_lease.resolution_capability();
    const auto mount_identity = descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    const SourceManifestCheckpointFileObservation observed =
        observe_source_manifest_checkpoint_file_or_throw(
            root_descriptor.get(), selected_root.path(),
            resolution_capability, mount_identity,
            selected_root.attestation(), store.limits,
            store.expected_identity, &lease.identity_status(), true,
            label + " record");
    lease.verify_or_throw(selected_root, label + " final lease cutpoint");
    selected_root.verify_or_throw(label + " selected-root proof");
    store.root_authority.verify_or_throw(label + " retained-root proof");
    if (!observed.usable) return std::nullopt;
    if (!observed.checkpoint.has_value()) {
        throw std::logic_error(
            label + " usable checkpoint lacks parsed contents");
    }
    return observed.checkpoint;
}

void
SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw(
    SyncReplicaSourceManifestCheckpoint& checkpoint,
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint publication label must not be empty");
    }
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            store.root_authority, label + " owner-thread preflight");
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            label + " read-only inspection store cannot publish acceleration");
    }
    store.root_authority.verify_or_throw(label + " retained-root preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, label);

    SyncDirectoryAuthority selected_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, label + " selected root");
    StoreLease lease = acquire_store_lease_or_throw(
        selected_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        label + " identity cutpoint", StoreObservationDurability::Reconcile);
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            selected_root, label + " retained root");
    const auto resolution_capability =
        descriptor_lease.resolution_capability();
    const auto mount_identity = descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    const SourceManifestCheckpointFileObservation current =
        observe_source_manifest_checkpoint_file_or_throw(
            root_descriptor.get(), selected_root.path(),
            resolution_capability, mount_identity,
            selected_root.attestation(), store.limits,
            store.expected_identity, &lease.identity_status(), true,
            label + " current record");
    checkpoint.store_identity_sha256 =
        sha256_hex(store.expected_identity);
    checkpoint.store_identity_metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            lease.identity_status(),
            SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " identity metadata");
    if (current.usable) {
        if (!current.checkpoint.has_value()) {
            throw std::logic_error(
                label + " usable predecessor lacks parsed contents");
        }
        if (current.checkpoint->generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(label + " generation is exhausted");
        }
        checkpoint.generation = current.checkpoint->generation + 1U;
    } else {
        checkpoint.generation = 1U;
    }

    const std::string encoded =
        serialize_sync_replica_source_manifest_checkpoint_or_throw(
            checkpoint, store.limits.max_payload_bytes,
            kSyncReplicaSourceManifestCheckpointMaximumChunks,
            label + " encoding");
    lease.verify_or_throw(selected_root, label + " pre-publication lease");
    if (current.present) {
        if (!current.metadata.has_value()) {
            throw std::logic_error(
                label + " predecessor observation lacks metadata");
        }
        write_sync_file_atomically_replace_expected_under_directory_or_throw(
            selected_root,
            fs::path(kSyncReplicaSourceManifestCheckpointBasename),
            byte_span(encoded), *current.metadata,
            label + " replacement");
    } else {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            selected_root,
            fs::path(kSyncReplicaSourceManifestCheckpointBasename),
            byte_span(encoded), label + " creation");
    }
    lease.verify_or_throw(selected_root, label + " post-publication lease");

    const SourceManifestCheckpointFileObservation committed =
        observe_source_manifest_checkpoint_file_or_throw(
            root_descriptor.get(), selected_root.path(),
            resolution_capability, mount_identity,
            selected_root.attestation(), store.limits,
            store.expected_identity, &lease.identity_status(), true,
            label + " committed record");
    if (!committed.usable || !committed.checkpoint.has_value() ||
        *committed.checkpoint != checkpoint) {
        throw std::runtime_error(
            label + " publication failed exact reproof");
    }
    lease.verify_or_throw(selected_root, label + " final lease cutpoint");
    selected_root.verify_or_throw(label + " selected-root proof");
    store.root_authority.verify_or_throw(label + " retained-root proof");
}

std::optional<std::uint64_t>
SyncReplicaFilePayloadStore::payload_availability_generation_or_throw(
    std::string_view label_view) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica payload availability generation label must not be empty");
    }
    sync_directory_authority_detail::SyncDirectoryAuthorityAccess::
        require_current_owner_or_throw(
            state_->root_authority, label + " owner-thread preflight");
    if (state_->verification_cache->
            payload_availability_generation_exhausted) {
        return std::nullopt;
    }
    return state_->verification_cache->payload_availability_generation;
}

SyncReplicaFilePayloadStoreSnapshot
SyncReplicaFilePayloadStore::snapshot_or_throw() const {
    return snapshot_with_reuse_policy_or_throw(false, false);
}

SyncReplicaFilePayloadStoreSnapshot
SyncReplicaFilePayloadStore::snapshot_rechecking_current_bytes_or_throw()
    const {
    return snapshot_with_reuse_policy_or_throw(true, false);
}

SyncReplicaFilePayloadStoreSnapshot
SyncReplicaFilePayloadStore::snapshot_writer_fenced_for_retention_or_throw()
    const {
    return snapshot_with_reuse_policy_or_throw(false, true);
}

SyncReplicaFilePayloadRetentionMarkPublication
SyncReplicaFilePayloadStore::publish_retention_mark_or_throw(
    const SyncReplicaFilePayloadStoreSnapshot& writer_fenced_snapshot,
    SyncReplicaFilePayloadRetentionMark mark) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const std::string label = store.label + " payload retention mark";
    verify_writer_fenced_retention_snapshot_or_throw(
        writer_fenced_snapshot, label + " source cutpoint");
    const SyncReplicaFilePayloadStoreSnapshot::State& candidate =
        writer_fenced_snapshot.require_state_or_throw(
            label + " writer-fenced snapshot");
    if (!candidate.retained_writer_fence) {
        throw std::logic_error(
            label + " writer-fenced snapshot lost its retained lease");
    }
    StoreLease& lease = *candidate.retained_writer_fence;

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            candidate.root_authority, label + " retained root");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    const RetentionMarkFileObservation current =
        observe_retention_mark_file_or_throw(
            root_descriptor.get(), candidate.root_path,
            resolution_capability, mount_identity,
            candidate.root_authority.attestation(), candidate.limits,
            candidate.expected_identity, &lease.identity_status(), true,
            label + " current record");

    mark.store_identity_sha256 =
        sha256_hex(candidate.expected_identity);
    mark.store_identity_metadata =
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            lease.identity_status(),
            SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " identity metadata");
    if (current.usable) {
        if (!current.mark.has_value()) {
            throw std::logic_error(
                label + " usable current record lacks parsed contents");
        }
        if (current.mark->generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(label + " generation is exhausted");
        }
        mark.generation = current.mark->generation + 1U;
    } else {
        mark.generation = 1U;
    }

    const std::string encoded =
        serialize_sync_replica_file_payload_retention_mark_or_throw(
            mark, candidate.limits.max_entries,
            candidate.limits.max_indexed_bytes,
            label + " encoding");
    const std::string desired_digest =
        sync_replica_file_payload_retention_mark_digest_or_throw(
            mark, candidate.limits.max_entries,
            candidate.limits.max_indexed_bytes,
            label + " digest");

    const auto observe_exact_committed = [&]()
        -> std::optional<SyncReplicaFilePayloadRetentionMarkPublication> {
        const RetentionMarkFileObservation observed =
            observe_retention_mark_file_or_throw(
                root_descriptor.get(), candidate.root_path,
                resolution_capability, mount_identity,
                candidate.root_authority.attestation(), candidate.limits,
                candidate.expected_identity, &lease.identity_status(), true,
                label + " committed record");
        verify_writer_fenced_retention_snapshot_or_throw(
            writer_fenced_snapshot, label + " committed cutpoint");
        if (!observed.usable || !observed.mark.has_value() ||
            !observed.mark_digest.has_value() ||
            *observed.mark != mark ||
            *observed.mark_digest != desired_digest) {
            return std::nullopt;
        }
        return SyncReplicaFilePayloadRetentionMarkPublication{
            .mark = mark,
            .mark_digest = desired_digest,
            .replaced_existing_file = current.present,
            .replaced_usable_mark = current.usable,
        };
    };

    verify_writer_fenced_retention_snapshot_or_throw(
        writer_fenced_snapshot, label + " prepublication cutpoint");
    try {
        if (current.present) {
            if (!current.metadata.has_value()) {
                throw std::logic_error(
                    label + " present current record lacks exact metadata");
            }
            write_sync_file_atomically_replace_expected_under_directory_or_throw(
                candidate.root_authority,
                fs::path(kSyncReplicaFilePayloadRetentionMarkBasename),
                byte_span(encoded), *current.metadata,
                label + " replacement");
        } else {
            write_sync_file_atomically_create_new_under_directory_or_throw(
                candidate.root_authority,
                fs::path(kSyncReplicaFilePayloadRetentionMarkBasename),
                byte_span(encoded), label + " publication");
        }
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        try {
            if (const auto committed = observe_exact_committed();
                committed.has_value()) {
                return *committed;
            }
        } catch (...) {
            // Reconciliation is intentionally best effort. A secondary open,
            // parse, allocation, or rooted-reproof failure must not replace the
            // atomic publisher's primary exception with weaker diagnostic noise.
        }
        std::rethrow_exception(original);
    }

    if (const auto committed = observe_exact_committed();
        committed.has_value()) {
        return *committed;
    }
    throw std::runtime_error(
        label + " publication did not settle to the exact requested record");
}

SyncReplicaFilePayloadStoreQuarantineResult
SyncReplicaFilePayloadStore::quarantine_corrupt_payload_or_throw(
    std::string expected_content_sha256,
    std::string observed_content_sha256) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    if (!is_lowercase_sha256_hex(expected_content_sha256) ||
        !is_lowercase_sha256_hex(observed_content_sha256) ||
        expected_content_sha256 == observed_content_sha256) {
        throw std::invalid_argument(
            "payload quarantine requires distinct canonical SHA-256 digests");
    }

    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot quarantine payload bytes");
    }

    SyncReplicaFilePayloadStoreQuarantineResult result;
    result.action = SyncReplicaFilePayloadStoreQuarantineAction::Preserve;
    result.expected_content_sha256 = expected_content_sha256;
    result.requested_observed_content_sha256 = observed_content_sha256;
    result.current_observed_content_sha256 = observed_content_sha256;
    const std::string target_quarantine_basename = quarantine_basename_or_throw(
        expected_content_sha256, observed_content_sha256);

    store.root_authority.verify_or_throw(
        store.label + " payload quarantine source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, store.label);

    const auto active_fault = store.verification_cache->integrity_fault;
    if (!active_fault.has_value() ||
        active_fault->expected_digest() != expected_content_sha256 ||
        active_fault->observed_digest() != observed_content_sha256) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ActiveFaultMismatch;
        if (active_fault.has_value() &&
            active_fault->expected_digest() == expected_content_sha256) {
            result.current_observed_content_sha256 =
                std::string(active_fault->observed_digest());
        }
        return result;
    }

    SyncDirectoryAuthority quarantine_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, store.label + " payload quarantine");
    StoreLease mutation_lease = acquire_store_lease_or_throw(
        quarantine_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " payload quarantine",
        StoreObservationDurability::Reconcile);

    const QuarantineNamespaceObservation retained =
        observe_quarantine_namespace_under_lease_or_throw(
            quarantine_root, store.limits, store.identity_basename,
            mutation_lease, target_quarantine_basename,
            store.label + " payload quarantine namespace");

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            quarantine_root,
            store.label + " payload quarantine retained root");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    const SyncDirectoryAttestation& root_attestation =
        quarantine_root.attestation();

    auto verify_nonmutating_cutpoint_or_throw =
        [&](std::string_view outcome) {
            const std::string outcome_label =
                store.label + " payload quarantine " + std::string(outcome);
            mutation_lease.verify_or_throw(
                quarantine_root, outcome_label + " lease cutpoint");
            quarantine_root.verify_or_throw(
                outcome_label + " root proof");
            store.root_authority.verify_or_throw(
                outcome_label + " retained-root proof");
            publish_process_quarantine_inventory(
                *store.verification_cache, retained.inventory);
        };

    auto refresh_acceleration_after_authoritative_namespace_mutation = [&]() {
        // The immutable process generation remains safe acceleration: complete
        // scans still enumerate the current namespace, exact metadata gates
        // every reused entry, and the active integrity witness forbids reuse
        // for this faulted digest. Only durable checkpoint scheduling and an
        // active scrub observation for the removed digest become stale. Do not
        // turn one explicit quarantine into a whole-store rehash.
        store.verification_cache->checkpoint.observation_known = true;
        store.verification_cache->checkpoint.force_checkpoint = true;
        store.verification_cache->checkpoint
            .publication_capacity_observation_known = false;
        store.verification_cache->checkpoint
            .publication_capacity_available = false;
        if (store.verification_cache->scrub_active.has_value() &&
            store.verification_cache->scrub_active->active_digest() ==
                expected_content_sha256) {
            store.verification_cache->scrub_active.reset();
        }
        store.next_scrub_not_before =
            std::chrono::steady_clock::time_point::min();
    };

    auto verify_exact_quarantine_or_throw = [&]() {
        if (!retained.exact_destination_status.has_value()) return false;
        SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
            root_descriptor.get(), target_quarantine_basename,
            quarantine_root.path(), resolution_capability, mount_identity,
            store.label + " exact retained payload quarantine");
        OwnedFd file(opened.descriptor);
        require_private_regular_file_or_throw(
            opened.status, root_attestation,
            store.label + " exact retained payload quarantine");
        if (!same_regular_file_observation(
                *retained.exact_destination_status, opened.status)) {
            throw PayloadStoreObservationStaleError(
                store.label +
                " exact retained payload quarantine changed after scan");
        }
        const StreamedFileDigest streamed =
            stream_hash_regular_file_or_throw(
                file.get(), opened.status, std::nullopt,
                store.label + " exact retained payload quarantine");
        if (streamed.sha256 != observed_content_sha256) {
            throw std::runtime_error(
                store.label +
                " exact quarantine name does not bind its observed bytes");
        }
        fsync_or_throw(
            file.get(),
            store.label + " exact retained payload quarantine");
        verify_named_regular_file_or_throw(
            root_descriptor.get(), target_quarantine_basename,
            opened.status, root_attestation,
            store.label + " exact retained payload quarantine");
        result.size_bytes =
            static_cast<std::uint64_t>(opened.status.st_size);
        result.quarantine_basename = target_quarantine_basename;
        return true;
    };

    std::optional<SyncPosixOpenedRegularFile> opened =
        open_optional_store_file_or_throw(
            root_descriptor.get(), expected_content_sha256,
            quarantine_root.path(), resolution_capability, mount_identity,
            store.label + " corrupt payload quarantine source");
    if (!opened.has_value()) {
        result.disposition = verify_exact_quarantine_or_throw()
            ? SyncReplicaFilePayloadStoreQuarantineDisposition::
                  ExactQuarantineAlreadyPresent
            : SyncReplicaFilePayloadStoreQuarantineDisposition::PayloadAbsent;
        verify_nonmutating_cutpoint_or_throw("absent-source");
        return result;
    }

    OwnedFd source_file(opened->descriptor);
    require_private_regular_file_or_throw(
        opened->status, root_attestation,
        store.label + " corrupt payload quarantine source");
    // The store-wide exclusive lease prevents new cooperative payload
    // selections. The exact-inode exclusive lease also detects descriptors
    // that were selected earlier and outlived their short store observation.
    // Do not hash, rename, or unlink until both fences are held.
    acquire_exclusive_payload_use_lease_or_throw(
        source_file.get(),
        store.label + " corrupt payload quarantine source");
    result.size_bytes = static_cast<std::uint64_t>(opened->status.st_size);
    if (result.size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " corrupt payload exceeds payload byte limit");
    }
    const StreamedFileDigest streamed = stream_hash_regular_file_or_throw(
        source_file.get(), opened->status, std::nullopt,
        store.label + " corrupt payload quarantine current-byte proof");
    result.current_observed_content_sha256 = streamed.sha256;
    verify_named_regular_file_or_throw(
        root_descriptor.get(), expected_content_sha256, opened->status,
        root_attestation,
        store.label + " corrupt payload quarantine source");

    if (streamed.sha256 == expected_content_sha256) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                PayloadAlreadyRepaired;
        verify_nonmutating_cutpoint_or_throw("repaired-source");
        return result;
    }
    if (streamed.sha256 != observed_content_sha256) {
        (void)retain_process_integrity_fault(
            *store.verification_cache, expected_content_sha256,
            streamed.sha256);
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ObservedDigestChanged;
        store.next_scrub_not_before =
            std::chrono::steady_clock::time_point::min();
        verify_nonmutating_cutpoint_or_throw("changed-source");
        return result;
    }

    if (verify_exact_quarantine_or_throw()) {
        // A previous quarantine may already retain this exact wrong byte
        // image while the authoritative digest name has since reappeared and
        // corrupted to the same bytes again. The explicit exact-pair action
        // must still remove that current corrupt name or recovery would be
        // permanently stuck. The already retained destination was fully
        // rehashed above, so removing this duplicate source does not discard
        // the requested byte image.
        mutation_lease.verify_or_throw(
            quarantine_root,
            store.label + " duplicate payload quarantine pre-unlink cutpoint");
        unlink_scanned_private_file_or_throw(
            root_descriptor.get(), expected_content_sha256, opened->status,
            root_attestation,
            store.label + " duplicate corrupt payload quarantine source");
        fsync_or_throw(
            root_descriptor.get(),
            store.label + " duplicate corrupt payload quarantine directory");
        verify_named_entry_absent_or_throw(
            root_descriptor.get(), expected_content_sha256,
            store.label + " duplicate quarantined payload source");
        verify_named_regular_file_or_throw(
            root_descriptor.get(), target_quarantine_basename,
            *retained.exact_destination_status, root_attestation,
            store.label + " duplicate quarantined payload destination");
        mutation_lease.verify_or_throw(
            quarantine_root,
            store.label + " duplicate payload quarantine final cutpoint");
        quarantine_root.verify_or_throw(
            store.label + " duplicate payload quarantine final root proof");
        store.root_authority.verify_or_throw(
            store.label +
            " duplicate payload quarantine final retained-root proof");
        refresh_acceleration_after_authoritative_namespace_mutation();
        publish_process_quarantine_inventory(
            *store.verification_cache, retained.inventory);
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ExactQuarantineAlreadyPresent;
        return result;
    }
    if (retained.inventory.entry_count >=
        kSyncReplicaFilePayloadStoreMaxQuarantineEntries) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                EntryCapacityExceeded;
        verify_nonmutating_cutpoint_or_throw("entry-capacity");
        return result;
    }
    const std::uint64_t quarantine_byte_limit =
        maximum_quarantine_bytes(store.limits);
    if (retained.inventory.total_bytes > quarantine_byte_limit ||
        result.size_bytes >
            quarantine_byte_limit - retained.inventory.total_bytes) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ByteCapacityExceeded;
        verify_nonmutating_cutpoint_or_throw("byte-capacity");
        return result;
    }

    ProcessQuarantineInventoryObservation inventory_after =
        retained.inventory;
    append_process_quarantine_inventory_entry_or_throw(
        inventory_after, expected_content_sha256, observed_content_sha256,
        result.size_bytes,
        store.label + " payload quarantine post-rename inventory");
    sort_process_quarantine_inventory(inventory_after);

    mutation_lease.verify_or_throw(
        quarantine_root,
        store.label + " payload quarantine pre-rename lease cutpoint");
    quarantine_root.verify_or_throw(
        store.label + " payload quarantine pre-rename root proof");
    // Make the exact byte image durable before making its diagnostic name
    // durable. Directory synchronization alone cannot promise that dirty
    // in-place corruption survives a crash under the new quarantine name.
    fsync_or_throw(
        source_file.get(),
        store.label + " corrupt payload quarantine source bytes");
    verify_named_regular_file_or_throw(
        root_descriptor.get(), expected_content_sha256, opened->status,
        root_attestation,
        store.label + " corrupt payload quarantine durable source");
    // From this point a failure may leave the quarantine namespace changed.
    // Revoke the previous diagnostic projection before the no-replace rename;
    // the prepared fixed-width successor publishes only after final reproof.
    forget_process_quarantine_inventory(*store.verification_cache);
    rename_noreplace_at_or_throw(
        root_descriptor.get(), expected_content_sha256,
        target_quarantine_basename,
        store.label + " corrupt payload quarantine");
    fsync_or_throw(
        root_descriptor.get(),
        store.label + " corrupt payload quarantine directory");

    struct stat renamed_status{};
    if (::fstat(source_file.get(), &renamed_status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            store.label + " quarantined payload fstat failed: " +
            error_text(error));
    }
    require_private_regular_file_or_throw(
        renamed_status, root_attestation,
        store.label + " quarantined payload");
    if (!same_regular_file_rename_transition(
            opened->status, renamed_status)) {
        throw std::runtime_error(
            store.label +
            " corrupt payload inode changed across quarantine rename");
    }
    verify_named_entry_absent_or_throw(
        root_descriptor.get(), expected_content_sha256,
        store.label + " quarantined payload source");
    verify_named_regular_file_or_throw(
        root_descriptor.get(), target_quarantine_basename, renamed_status,
        root_attestation,
        store.label + " quarantined payload destination");
    mutation_lease.verify_or_throw(
        quarantine_root,
        store.label + " payload quarantine final lease cutpoint");
    quarantine_root.verify_or_throw(
        store.label + " payload quarantine final root proof");
    store.root_authority.verify_or_throw(
        store.label + " payload quarantine final retained-root proof");

    refresh_acceleration_after_authoritative_namespace_mutation();
    publish_process_quarantine_inventory(
        *store.verification_cache, inventory_after);

    result.quarantine_basename = target_quarantine_basename;
    result.disposition =
        SyncReplicaFilePayloadStoreQuarantineDisposition::Quarantined;
    return result;
}

SyncReplicaFilePayloadStoreQuarantineResult
SyncReplicaFilePayloadStore::release_quarantined_payload_or_throw(
    std::string expected_content_sha256,
    std::string observed_content_sha256) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    if (!is_lowercase_sha256_hex(expected_content_sha256) ||
        !is_lowercase_sha256_hex(observed_content_sha256) ||
        expected_content_sha256 == observed_content_sha256) {
        throw std::invalid_argument(
            "payload quarantine release requires distinct canonical SHA-256 "
            "digests");
    }

    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot release quarantined bytes");
    }

    SyncReplicaFilePayloadStoreQuarantineResult result;
    result.action = SyncReplicaFilePayloadStoreQuarantineAction::Release;
    result.expected_content_sha256 = expected_content_sha256;
    result.requested_observed_content_sha256 = observed_content_sha256;
    result.current_observed_content_sha256 = observed_content_sha256;
    const std::string target_quarantine_basename = quarantine_basename_or_throw(
        expected_content_sha256, observed_content_sha256);

    store.root_authority.verify_or_throw(
        store.label + " payload quarantine release preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, store.label);

    // Evidence for a current unresolved integrity incident is not releasable.
    // Recovery first requires an ordinary complete current-byte proof; only
    // then may the owner explicitly reclaim this diagnostic capacity.
    const auto active_fault = store.verification_cache->integrity_fault;
    if (active_fault.has_value()) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ActiveFaultPresent;
        result.current_observed_content_sha256.clear();
        if (active_fault->expected_digest() == expected_content_sha256) {
            result.current_observed_content_sha256 =
                std::string(active_fault->observed_digest());
        }
        return result;
    }

    SyncDirectoryAuthority release_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, store.label + " payload quarantine release");
    StoreLease mutation_lease = acquire_store_lease_or_throw(
        release_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " payload quarantine release",
        StoreObservationDurability::Reconcile);

    const QuarantineNamespaceObservation retained =
        observe_quarantine_namespace_under_lease_or_throw(
            release_root, store.limits, store.identity_basename,
            mutation_lease, target_quarantine_basename,
            store.label + " payload quarantine release namespace");

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            release_root,
            store.label + " payload quarantine release retained root");
    const SyncPosixDirectoryResolutionCapability resolution_capability =
        descriptor_lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity =
        descriptor_lease.mount_identity();
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    const SyncDirectoryAttestation& root_attestation =
        release_root.attestation();

    auto verify_cutpoint_or_throw = [&](std::string_view outcome) {
        const std::string outcome_label =
            store.label + " payload quarantine release " +
            std::string(outcome);
        mutation_lease.verify_or_throw(
            release_root, outcome_label + " lease cutpoint");
        release_root.verify_or_throw(outcome_label + " root proof");
        store.root_authority.verify_or_throw(
            outcome_label + " retained-root proof");
    };

    if (!retained.exact_destination_status.has_value()) {
        result.disposition =
            SyncReplicaFilePayloadStoreQuarantineDisposition::
                ExactQuarantineAbsent;
        result.current_observed_content_sha256.clear();
        verify_cutpoint_or_throw("absent");
        publish_process_quarantine_inventory(
            *store.verification_cache, retained.inventory);
        return result;
    }

    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), target_quarantine_basename,
        release_root.path(), resolution_capability, mount_identity,
        store.label + " exact payload quarantine release target");
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, root_attestation,
        store.label + " exact payload quarantine release target");
    acquire_exclusive_payload_use_lease_or_throw(
        file.get(),
        store.label + " exact payload quarantine release target");
    if (!same_regular_file_observation(
            *retained.exact_destination_status, opened.status)) {
        throw PayloadStoreObservationStaleError(
            store.label +
            " exact payload quarantine release target changed after scan");
    }
    result.size_bytes = static_cast<std::uint64_t>(opened.status.st_size);
    result.quarantine_basename = target_quarantine_basename;
    ProcessQuarantineInventoryObservation inventory_after =
        retained.inventory;
    if (!erase_process_quarantine_inventory_entry(
            inventory_after, expected_content_sha256,
            observed_content_sha256)) {
        throw std::logic_error(
            store.label +
            " exact payload quarantine release target is absent from inventory");
    }
    mutation_lease.verify_or_throw(
        release_root,
        store.label + " payload quarantine release pre-unlink cutpoint");
    verify_named_regular_file_or_throw(
        root_descriptor.get(), target_quarantine_basename, opened.status,
        root_attestation,
        store.label + " exact payload quarantine release target");
    // A failure after the unlink begins may leave the old observation stale.
    // Revoke it first; the exact fixed successor publishes only after absence,
    // lease, and both rooted authorities have been re-proved.
    forget_process_quarantine_inventory(*store.verification_cache);
    unlink_scanned_private_file_or_throw(
        root_descriptor.get(), target_quarantine_basename, opened.status,
        root_attestation,
        store.label + " exact payload quarantine release target");
    fsync_or_throw(
        root_descriptor.get(),
        store.label + " payload quarantine release directory");
    verify_named_entry_absent_or_throw(
        root_descriptor.get(), target_quarantine_basename,
        store.label + " released payload quarantine");
    verify_cutpoint_or_throw("final");

    // Quarantine files are outside authoritative inventory and verification
    // generations. Their explicit removal cannot stale payload-byte proof or
    // the durable authoritative checkpoint, so preserve all acceleration.
    publish_process_quarantine_inventory(
        *store.verification_cache, inventory_after);
    result.disposition =
        SyncReplicaFilePayloadStoreQuarantineDisposition::Released;
    return result;
}

SyncReplicaFilePayloadStoreSnapshot
SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw(
    bool require_current_bytes,
    bool retain_exclusive_writer_fence) const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const StoreObservationDurability durability =
        store.disposition ==
                SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect
            ? StoreObservationDurability::ObserveOnly
            : StoreObservationDurability::Reconcile;
    if (require_current_bytes &&
        !synchronizes_store_observation(durability)) {
        throw std::logic_error(
            store.label +
            " read-only inspection cannot accept an operator recheck");
    }
    if (retain_exclusive_writer_fence &&
        !synchronizes_store_observation(durability)) {
        throw std::logic_error(
            store.label +
            " read-only inspection cannot retain a writer-fenced retention "
            "observation");
    }
    if (require_current_bytes && retain_exclusive_writer_fence) {
        throw std::logic_error(
            store.label +
            " current-byte recheck and writer-fenced retention modes cannot "
            "be combined");
    }
    store.root_authority.verify_or_throw(
        store.label + " snapshot source preflight");
    if (synchronizes_store_observation(durability)) {
        ensure_store_identity_or_throw(
            store.root_authority, store.limits, store.identity_basename,
            store.legacy_identity_basename, store.expected_identity,
            store.disposition, store.allow_existing_payload_adoption,
            *store.verification_cache, store.label);
    }
    const std::string& expected_identity = store.expected_identity;
    bool refresh_verification_index = false;
    std::unique_ptr<SyncReplicaFilePayloadStoreSnapshot::State> snapshot;
    {
        const SyncReplicaFilePayloadStoreLeaseMode observation_mode =
            retain_exclusive_writer_fence
                ? SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation
                : SyncReplicaFilePayloadStoreLeaseMode::SharedObservation;
        const std::string snapshot_label =
            store.label +
            (retain_exclusive_writer_fence
                 ? " writer-fenced retention snapshot"
                 : " snapshot");
        SyncDirectoryAuthority snapshot_root =
            reopen_matching_root_authority_or_throw(
                store.root_authority, snapshot_label);
        StoreLease observation_lease = acquire_store_lease_or_throw(
            snapshot_root, store.identity_basename, expected_identity,
            observation_mode, snapshot_label, durability);

        ScannedPayloadIndex scanned = scan_store_under_lease_or_throw(
            snapshot_root, store.limits, store.identity_basename,
            expected_identity, observation_lease,
            observation_mode, snapshot_label, durability,
            synchronizes_store_observation(durability)
                ? store.verification_cache.get()
                : nullptr,
            require_current_bytes
                ? PayloadVerificationReusePolicy::RequireCurrentBytes
                : PayloadVerificationReusePolicy::AllowAcceleration);
        if (require_current_bytes &&
            (scanned.scan_reused_entry_count != 0U ||
             scanned.scan_reused_bytes != 0U ||
             scanned.scan_process_reused_entry_count != 0U ||
             scanned.scan_process_reused_bytes != 0U ||
             scanned.scan_durable_reused_entry_count != 0U ||
             scanned.scan_durable_reused_bytes != 0U ||
             scanned.scan_hashed_entry_count != scanned.entries.size() ||
             scanned.scan_hashed_bytes != scanned.indexed_bytes)) {
            throw std::logic_error(
                store.label +
                " operator recheck returned incomplete current-byte work");
        }
        const bool checkpoint_deferred_by_capacity =
            synchronizes_store_observation(durability) &&
            verification_checkpoint_deferred_by_known_capacity(
                *store.verification_cache, false);
        refresh_verification_index =
            synchronizes_store_observation(durability) &&
            verification_checkpoint_publication_worth_attempting(
                *store.verification_cache, false);

        snapshot =
            std::make_unique<SyncReplicaFilePayloadStoreSnapshot::State>();
        snapshot->folder_id = store.folder_id;
        snapshot->root_path = store.root_path;
        snapshot->root_authority = std::move(snapshot_root);
        snapshot->identity_basename = store.identity_basename;
        snapshot->expected_identity = expected_identity;
        snapshot->durability = durability;
        snapshot->limits = store.limits;
        if (synchronizes_store_observation(durability)) {
            snapshot->verification_cache = store.verification_cache;
            snapshot->issued_integrity_fault_epoch =
                store.verification_cache->integrity_fault_epoch;
        }
        snapshot->entries = std::move(scanned.entries);
        snapshot->indexed_bytes = scanned.indexed_bytes;
        snapshot->scan_hashed_entry_count = scanned.scan_hashed_entry_count;
        snapshot->scan_hashed_bytes = scanned.scan_hashed_bytes;
        snapshot->scan_reused_entry_count = scanned.scan_reused_entry_count;
        snapshot->scan_reused_bytes = scanned.scan_reused_bytes;
        snapshot->scan_process_reused_entry_count =
            scanned.scan_process_reused_entry_count;
        snapshot->scan_process_reused_bytes =
            scanned.scan_process_reused_bytes;
        snapshot->scan_durable_reused_entry_count =
            scanned.scan_durable_reused_entry_count;
        snapshot->scan_durable_reused_bytes =
            scanned.scan_durable_reused_bytes;
        snapshot->verification_checkpoint_deferred_by_transient_capacity =
            checkpoint_deferred_by_capacity;
        snapshot->transient_entry_count = scanned.transient_entry_count;
        snapshot->transient_bytes = scanned.transient_bytes;
        snapshot->transient_reserved_bytes =
            scanned.transient_reserved_bytes;
        snapshot->transient_namespace_digest =
            transient_namespace_digest_or_throw(
                scanned, store.label + " snapshot transient namespace");
        snapshot->scrub_state_present = scanned.scrub_state_present;
        snapshot->scrub_state_usable = scanned.scrub_state_usable;
        snapshot->scrub_failure_reverified_good =
            scanned.scrub_failure_reverified_good;
        snapshot->scrub_active_reverified_good =
            scanned.scrub_active_reverified_good;
        snapshot->scrub_state_metadata = scanned.scrub_state_metadata;
        snapshot->scrub_state = std::move(scanned.scrub_state);
        snapshot->retention_mark_present = scanned.retention_mark_present;
        snapshot->retention_mark_observation_known =
            scanned.retention_mark_contents_requested;
        snapshot->retention_mark_usable = scanned.retention_mark_usable;
        snapshot->retention_mark = std::move(scanned.retention_mark);
        snapshot->retention_mark_digest =
            std::move(scanned.retention_mark_digest);
        snapshot->directory_status = scanned.directory_status;
        snapshot->root_attestation_digest = store.root_attestation_digest;

        std::vector<std::string> digests;
        digests.reserve(snapshot->entries.size());
        for (const PayloadIndexEntry& entry : snapshot->entries) {
            digests.push_back(entry.content_sha256);
        }
        snapshot->content_inventory = SyncReplicaFileContentInventory(
            snapshot->folder_id, std::move(digests),
            store.label + " snapshot content inventory");
        snapshot->snapshot_digest = snapshot_digest_or_throw(
            snapshot->folder_id, snapshot->root_path.generic_string(),
            snapshot->root_attestation_digest, store.identity_basename,
            expected_identity, snapshot->limits,
            snapshot->transient_entry_count, snapshot->transient_bytes,
            snapshot->transient_reserved_bytes,
            snapshot->transient_namespace_digest,
            snapshot->indexed_bytes, snapshot->entries);
        // Keep the observation lease live through every allocation and
        // derived-index construction. The final proof prevents an
        // identical-bytes replacement marker from turning a completed scan into
        // authority bound to a different lock inode before the snapshot is
        // returned. The retention-only mode then transfers this exact EX lock
        // into the snapshot instead of releasing it at the end of the scope.
        observation_lease.verify_or_throw(
            snapshot->root_authority,
            snapshot_label + " final lease cutpoint");
        if (synchronizes_store_observation(durability)) {
            // The scan already canonicalized this bounded projection. Move it
            // only after every snapshot allocation and the final exact lease
            // proof, so failed observations never displace an older known
            // scheduler frontier and successful publication adds no O(n) copy.
            store.terminal_verification_work =
                std::move(scanned.terminal_verification_work);
            store.terminal_verification_observation_known = true;
        }
        if (retain_exclusive_writer_fence) {
            snapshot->retained_writer_fence =
                std::make_unique<StoreLease>(std::move(observation_lease));
        }
    }

    if (retain_exclusive_writer_fence) {
        const SyncReplicaFilePayloadScrubState* retained_state =
            snapshot->scrub_state_usable && snapshot->scrub_state.has_value()
                ? &*snapshot->scrub_state
                : nullptr;
        snapshot->scrub_report = scrub_report_from_state(
            payload_scrub_enabled(store.limits)
                ? SyncReplicaFilePayloadStoreScrubDisposition::DeferredLeaseBusy
                : SyncReplicaFilePayloadStoreScrubDisposition::Disabled,
            retained_state);
        snapshot->live_capability_registration =
            PayloadStoreLiveCapabilityRegistration(
                store.live_capability_registry,
                PayloadStoreLiveCapabilityKind::Snapshot);
        return SyncReplicaFilePayloadStoreSnapshot(std::move(snapshot));
    }

    const std::uint64_t scrub_cycles_before_attempt =
        snapshot->scrub_state_usable && snapshot->scrub_state.has_value()
        ? snapshot->scrub_state->completed_cycles
        : 0U;

    // A successful snapshot is already complete authority. Only after releasing
    // its shared lease do we take an exclusive lease either for one
    // process-throttled rotating byte scrub or for metadata-only settlement of
    // a damaged/active restart fence. Disabling bounded scrub reads must not
    // preserve stale write-ahead intent and force one complete rehash after
    // every restart. Partial scrub state remains scheduling evidence only.
    // Fail-fast contention, a stale cutpoint, or ordinary scrub-state
    // publication failure leaves the complete returned payload authority
    // unchanged. Exact-extent scrub mismatch is the sole exceptional optional
    // result; when continuation spans attempts it is an integrity alarm, not a
    // point-in-time byte image.
    const bool scrub_enabled = payload_scrub_enabled(store.limits);
    const SyncReplicaFilePayloadScrubState* prior_state =
        snapshot->scrub_state_usable && snapshot->scrub_state.has_value()
            ? &*snapshot->scrub_state
            : nullptr;
    const bool disabled_restart_fence_requires_settlement =
        !scrub_enabled && snapshot->scrub_state_present &&
        (prior_state == nullptr ||
         prior_state->disposition !=
             SyncReplicaFilePayloadScrubStateDisposition::Idle);
    if (!synchronizes_store_observation(durability) ||
        (!scrub_enabled &&
         !disabled_restart_fence_requires_settlement)) {
        snapshot->scrub_report = scrub_report_from_state(
            SyncReplicaFilePayloadStoreScrubDisposition::Disabled,
            prior_state);
    } else {
        const auto now = std::chrono::steady_clock::now();
        if (scrub_enabled && now < store.next_scrub_not_before) {
            snapshot->scrub_report = scrub_report_from_state(
                SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredBySchedule,
                prior_state);
        } else {
            // Set the process-local deadline before the attempt. Lease
            // contention, stale observations, and I/O failure must not turn a
            // hot snapshot path into an unbounded retry loop. A fresh process
            // intentionally receives one immediate attempt.
            if (scrub_enabled) {
                store.next_scrub_not_before =
                    now + kPayloadScrubMinimumInterval;
            }
            const PayloadScrubAttemptSnapshotView scrub_view{
                snapshot->entries,
                snapshot->directory_status,
                snapshot->transient_entry_count,
                snapshot->transient_reserved_bytes,
                snapshot->scrub_state_present,
                snapshot->scrub_state_metadata,
                snapshot->scrub_active_reverified_good,
                snapshot->scrub_failure_reverified_good,
            };
            try {
                snapshot->scrub_report =
                    advance_payload_scrub_from_snapshot_or_throw(
                        snapshot->root_authority, store.limits,
                        store.identity_basename, expected_identity,
                        *store.verification_cache, scrub_view,
                        store.label + " rotating payload scrub");
            } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
                snapshot->scrub_report = scrub_report_from_state(
                    SyncReplicaFilePayloadStoreScrubDisposition::
                        DeferredLeaseBusy,
                    prior_state);
            } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
                // The allocation-free mismatch cutpoint inside the scrubber has
                // already revoked older snapshots. If an older unresolved
                // target was preserved instead, cancel the throttle so its
                // current-byte reproof is attempted immediately.
                if (!store.verification_cache->integrity_fault.has_value() ||
                    store.verification_cache->integrity_fault
                            ->expected_digest() !=
                        error.expected_content_sha256()) {
                    store.next_scrub_not_before =
                        std::chrono::steady_clock::time_point::min();
                }
                throw;
            } catch (...) {
                if (store.verification_cache->integrity_fault.has_value() ||
                    store.verification_cache
                        ->integrity_fault_epoch_exhausted) {
                    // Any exception after the digest mismatch cutpoint is an
                    // integrity-alarm delivery failure, not an optional scrub
                    // failure. Keep the alarm fail-closed and retry without the
                    // ordinary scheduling delay.
                    store.next_scrub_not_before =
                        std::chrono::steady_clock::time_point::min();
                    throw;
                }
                snapshot->scrub_report = scrub_report_from_state(
                    SyncReplicaFilePayloadStoreScrubDisposition::
                        DeferredAttemptFailure,
                    prior_state);
            }
        }
    }

    const auto scrub_report_observed_at = std::chrono::steady_clock::now();
    if (snapshot->scrub_report.completed_cycles >
        scrub_cycles_before_attempt) {
        store.last_scrub_cycle_completed_at = scrub_report_observed_at;
    }
    store.last_scrub_report = snapshot->scrub_report;
    store.last_scrub_report_at = scrub_report_observed_at;

    if (refresh_verification_index) {
        refresh_verification_index_best_effort(
            store.root_authority, store.limits, store.identity_basename,
            expected_identity, *store.verification_cache, store.label, false);
    }
    snapshot->live_capability_registration =
        PayloadStoreLiveCapabilityRegistration(
            store.live_capability_registry,
            PayloadStoreLiveCapabilityKind::Snapshot);
    return SyncReplicaFilePayloadStoreSnapshot(std::move(snapshot));
}

SyncReplicaFilePayloadStoreMutationBatch
SyncReplicaFilePayloadStore::begin_mutation_batch_or_throw() {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot begin a mutation batch");
    }

    store.root_authority.verify_or_throw(
        store.label + " mutation batch source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, store.label);

    SyncDirectoryAuthority batch_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, store.label + " mutation batch");
    StoreLease mutation_lease = acquire_store_lease_or_throw(
        batch_root, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " mutation batch",
        StoreObservationDurability::Reconcile);
    ScannedPayloadIndex index = scan_store_under_lease_or_throw(
        batch_root, store.limits, store.identity_basename,
        store.expected_identity, mutation_lease,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " mutation batch initial namespace scan",
        StoreObservationDurability::Reconcile,
        store.verification_cache.get());
    std::uint64_t full_scan_count = 1U;
    std::uint64_t scan_hashed_entry_count =
        index.scan_hashed_entry_count;
    std::uint64_t scan_hashed_bytes = index.scan_hashed_bytes;
    std::uint64_t scan_reused_entry_count =
        index.scan_reused_entry_count;
    std::uint64_t scan_reused_bytes = index.scan_reused_bytes;
    std::uint64_t scan_process_reused_entry_count =
        index.scan_process_reused_entry_count;
    std::uint64_t scan_process_reused_bytes =
        index.scan_process_reused_bytes;
    std::uint64_t scan_durable_reused_entry_count =
        index.scan_durable_reused_entry_count;
    std::uint64_t scan_durable_reused_bytes =
        index.scan_durable_reused_bytes;
    if (!index.publication_residues.empty()) {
        remove_scanned_publication_residues_or_throw(
            batch_root, index.publication_residues,
            store.label + " mutation batch stale publication-residue cleanup");
        mutation_lease.verify_or_throw(
            batch_root,
            store.label + " mutation batch residue-cleanup lease cutpoint");
        ScannedPayloadIndex rescanned = scan_store_under_lease_or_throw(
            batch_root, store.limits, store.identity_basename,
            store.expected_identity, mutation_lease,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            store.label + " mutation batch post-cleanup namespace scan",
            StoreObservationDurability::Reconcile,
            store.verification_cache.get());
        scan_hashed_entry_count = checked_add_u64_or_throw(
            scan_hashed_entry_count, rescanned.scan_hashed_entry_count,
            store.label + " mutation batch scan hashed entry count");
        scan_hashed_bytes = checked_add_u64_or_throw(
            scan_hashed_bytes, rescanned.scan_hashed_bytes,
            store.label + " mutation batch scan hashed bytes");
        scan_reused_entry_count = checked_add_u64_or_throw(
            scan_reused_entry_count, rescanned.scan_reused_entry_count,
            store.label + " mutation batch scan reused entry count");
        scan_reused_bytes = checked_add_u64_or_throw(
            scan_reused_bytes, rescanned.scan_reused_bytes,
            store.label + " mutation batch scan reused bytes");
        scan_process_reused_entry_count = checked_add_u64_or_throw(
            scan_process_reused_entry_count,
            rescanned.scan_process_reused_entry_count,
            store.label + " mutation batch scan process reused entry count");
        scan_process_reused_bytes = checked_add_u64_or_throw(
            scan_process_reused_bytes, rescanned.scan_process_reused_bytes,
            store.label + " mutation batch scan process reused bytes");
        scan_durable_reused_entry_count = checked_add_u64_or_throw(
            scan_durable_reused_entry_count,
            rescanned.scan_durable_reused_entry_count,
            store.label + " mutation batch scan durable reused entry count");
        scan_durable_reused_bytes = checked_add_u64_or_throw(
            scan_durable_reused_bytes, rescanned.scan_durable_reused_bytes,
            store.label + " mutation batch scan durable reused bytes");
        index = std::move(rescanned);
        full_scan_count = 2U;
    }
    mutation_lease.verify_or_throw(
        batch_root, store.label + " mutation batch ready cutpoint");

    auto batch =
        std::make_unique<SyncReplicaFilePayloadStoreMutationBatch::State>(
            std::move(batch_root), store.limits,
            store.label + " mutation batch", store.identity_basename,
            store.expected_identity, std::move(mutation_lease),
            store.verification_cache, store.live_capability_registry,
            std::move(index), full_scan_count,
            scan_hashed_entry_count, scan_hashed_bytes,
            scan_reused_entry_count, scan_reused_bytes,
            scan_process_reused_entry_count, scan_process_reused_bytes,
            scan_durable_reused_entry_count, scan_durable_reused_bytes);
    return SyncReplicaFilePayloadStoreMutationBatch(std::move(batch));
}

SyncReplicaFilePayloadStorePutResult
SyncReplicaFilePayloadStoreMutationBatch::put_payload_or_throw(
    std::string payload) {
    State& batch = require_state_or_throw(
        "sync replica payload mutation batch string put");
    preflight_or_throw(batch.label + " string put preflight");

    const std::uint64_t size_bytes =
        size_to_u64_or_throw(payload.size(), batch.label + " payload");
    if (size_bytes > batch.limits.max_payload_bytes) {
        throw std::length_error(
            batch.label + " payload exceeds configured byte budget");
    }
    const std::string digest = sha256_hex(payload);
    batch.put_count = checked_add_u64_or_throw(
        batch.put_count, 1U, batch.label + " put count");
    batch.source_bytes = checked_add_u64_or_throw(
        batch.source_bytes, size_bytes, batch.label + " source bytes");

    if (find_entry(batch.index.entries, digest) != nullptr) {
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " existing payload pre-reconciliation lease cutpoint");
        const SyncImmutableFileReconciliationOutcome reconciliation =
            reconcile_sync_immutable_file_create_new_under_directory_or_throw(
                batch.root_authority, fs::path(digest), byte_span(payload),
                batch.label + " existing payload reconciliation");
        if (reconciliation !=
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            throw std::runtime_error(
                batch.label +
                " digest-named payload conflicts with the exact supplied bytes");
        }
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " existing payload final lease cutpoint");
        batch.already_present_count = checked_add_u64_or_throw(
            batch.already_present_count, 1U,
            batch.label + " already-present count");
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
            digest, size_bytes};
    }

    require_new_payload_publication_capacity_or_throw(
        batch.index, batch.limits, size_bytes, batch.label);
    batch.mutation_lease.verify_or_throw(
        batch.root_authority,
        batch.label + " payload pre-publication lease cutpoint");
    try {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            batch.root_authority, fs::path(digest), byte_span(payload),
            batch.label + " payload publication");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " payload publication lease cutpoint");
        PayloadIndexEntry inserted =
            observe_exact_published_payload_without_rehash_or_throw(
                batch.root_authority, digest, size_bytes,
                batch.label + " published payload index update");
        insert_payload_index_entry_or_throw(
            batch.index, std::move(inserted), batch.limits,
            batch.label + " published payload index update");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " payload publication final lease cutpoint");
        batch.inserted_count = checked_add_u64_or_throw(
            batch.inserted_count, 1U, batch.label + " inserted count");
        note_verification_checkpoint_payload_addition(
            *batch.verification_cache, size_bytes);
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::Inserted,
            digest, size_bytes};
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        refresh_namespace_after_failure_or_throw(
            "failed string publication reconciliation");
        const PayloadIndexEntry* durable =
            find_entry(batch.index.entries, digest);
        if (durable != nullptr) {
            if (durable->size_bytes != size_bytes) {
                throw std::runtime_error(
                    batch.label +
                    " reconciled payload has an impossible size conflict");
            }
            const SyncImmutableFileReconciliationOutcome reconciliation =
                reconcile_sync_immutable_file_create_new_under_directory_or_throw(
                    batch.root_authority, fs::path(digest), byte_span(payload),
                    batch.label + " reconciled payload exact-byte proof");
            if (reconciliation !=
                SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
                throw std::runtime_error(
                    batch.label +
                    " reconciled digest-named payload conflicts with supplied bytes");
            }
            batch.mutation_lease.verify_or_throw(
                batch.root_authority,
                batch.label + " reconciled payload final lease cutpoint");
            batch.already_present_count = checked_add_u64_or_throw(
                batch.already_present_count, 1U,
                batch.label + " already-present count");
            // The failure may have occurred after the create-new rename became
            // durable. Conservatively dirty the checkpoint; an extra later
            // rewrite is harmless, while omitting a newly published payload is
            // avoidable restart hashing.
            note_verification_checkpoint_payload_addition(
                *batch.verification_cache, size_bytes);
            return SyncReplicaFilePayloadStorePutResult{
                SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
                digest, size_bytes};
        }
        batch.poisoned = true;
        std::rethrow_exception(original);
    }
}

SyncReplicaFilePayloadStorePutResult
SyncReplicaFilePayloadStoreMutationBatch::
put_payload_from_borrowed_descriptor_or_throw(
    int source_descriptor,
    const SyncPosixRegularFileSnapshotMetadata& expected_source,
    std::string content_sha256) {
    State& batch = require_state_or_throw(
        "sync replica payload mutation batch descriptor put");
    preflight_or_throw(batch.label + " descriptor put preflight");
    if (source_descriptor < 0) {
        throw std::invalid_argument(
            batch.label + " payload source descriptor is invalid");
    }
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            batch.label + " payload source digest is invalid");
    }
    const std::uint64_t size_bytes = expected_source.size_bytes;
    if (size_bytes > batch.limits.max_payload_bytes) {
        throw std::length_error(
            batch.label + " payload exceeds configured byte budget");
    }

    const auto require_source_metadata = [&](std::string_view phase) {
        const SyncPosixRegularFileSnapshotMetadata observed =
            observe_sync_posix_regular_file_descriptor_or_throw(
                source_descriptor,
                SyncPosixDescriptorLinkPolicy::stable_named_object,
                batch.label + " payload source " + std::string(phase));
        if (observed != expected_source) {
            throw std::runtime_error(
                batch.label + " payload source changed after observation");
        }
    };
    const auto require_source_identity = [&](std::string_view phase) {
        const SyncPosixRegularFileDigestObservation source =
            hash_sync_posix_regular_file_descriptor_or_throw(
                source_descriptor, batch.limits.max_payload_bytes,
                SyncPosixDescriptorLinkPolicy::stable_named_object,
                batch.label + " payload source " + std::string(phase));
        if (source.metadata != expected_source ||
            source.content_sha256 != content_sha256) {
            throw std::runtime_error(
                batch.label +
                " payload source does not match its observed digest");
        }
    };

    require_source_metadata("preflight");
    batch.put_count = checked_add_u64_or_throw(
        batch.put_count, 1U, batch.label + " put count");
    batch.source_bytes = checked_add_u64_or_throw(
        batch.source_bytes, size_bytes, batch.label + " source bytes");
    const PayloadIndexEntry* existing =
        find_entry(batch.index.entries, content_sha256);
    if (existing != nullptr) {
        if (existing->size_bytes != size_bytes) {
            throw std::runtime_error(
                batch.label +
                " digest-named payload has an impossible size conflict");
        }
        // No destination write hashes the source in this branch. Re-prove the
        // caller's content identity before reporting success.
        require_source_identity("existing payload proof");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " existing descriptor payload final lease cutpoint");
        batch.already_present_count = checked_add_u64_or_throw(
            batch.already_present_count, 1U,
            batch.label + " already-present count");
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
            std::move(content_sha256), size_bytes};
    }

    require_new_payload_publication_capacity_or_throw(
        batch.index, batch.limits, size_bytes, batch.label);
    batch.mutation_lease.verify_or_throw(
        batch.root_authority,
        batch.label + " descriptor payload pre-publication lease cutpoint");
    try {
        copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
            batch.root_authority, fs::path(content_sha256), source_descriptor,
            expected_source, content_sha256,
            batch.label + " descriptor payload publication");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " descriptor payload publication lease cutpoint");
        PayloadIndexEntry inserted =
            observe_exact_published_payload_without_rehash_or_throw(
                batch.root_authority, content_sha256, size_bytes,
                batch.label + " descriptor payload index update");
        insert_payload_index_entry_or_throw(
            batch.index, std::move(inserted), batch.limits,
            batch.label + " descriptor payload index update");
        batch.mutation_lease.verify_or_throw(
            batch.root_authority,
            batch.label + " descriptor payload final lease cutpoint");
        batch.inserted_count = checked_add_u64_or_throw(
            batch.inserted_count, 1U, batch.label + " inserted count");
        note_verification_checkpoint_payload_addition(
            *batch.verification_cache, size_bytes);
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::Inserted,
            std::move(content_sha256), size_bytes};
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        refresh_namespace_after_failure_or_throw(
            "failed descriptor publication reconciliation");
        const PayloadIndexEntry* durable =
            find_entry(batch.index.entries, content_sha256);
        if (durable != nullptr) {
            if (durable->size_bytes != size_bytes) {
                throw std::runtime_error(
                    batch.label +
                    " reconciled descriptor payload has an impossible size conflict");
            }
            // A post-rename failure cannot launder a source that changed after
            // the caller's observation.
            require_source_identity("reconciled payload proof");
            batch.mutation_lease.verify_or_throw(
                batch.root_authority,
                batch.label +
                    " reconciled descriptor payload final lease cutpoint");
            batch.already_present_count = checked_add_u64_or_throw(
                batch.already_present_count, 1U,
                batch.label + " already-present count");
            note_verification_checkpoint_payload_addition(
                *batch.verification_cache, size_bytes);
            return SyncReplicaFilePayloadStorePutResult{
                SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
                std::move(content_sha256), size_bytes};
        }
        batch.poisoned = true;
        std::rethrow_exception(original);
    }
}

SyncReplicaFilePayloadStorePutResult
SyncReplicaFilePayloadStore::put_payload_or_throw(std::string payload) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label + " read-only inspection store cannot publish payloads");
    }
    const std::uint64_t size_bytes =
        size_to_u64_or_throw(payload.size(), store.label + " payload");
    if (size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " payload exceeds configured byte budget");
    }
    SyncReplicaFilePayloadStoreMutationBatch batch =
        begin_mutation_batch_or_throw();
    return batch.put_payload_or_throw(std::move(payload));
}

SyncReplicaFilePayloadStorePutResult
SyncReplicaFilePayloadStore::put_payload_from_borrowed_descriptor_or_throw(
    int source_descriptor,
    const SyncPosixRegularFileSnapshotMetadata& expected_source,
    std::string content_sha256) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot publish payloads");
    }
    if (source_descriptor < 0) {
        throw std::invalid_argument(
            store.label + " payload source descriptor is invalid");
    }
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            store.label + " payload source digest is invalid");
    }
    if (expected_source.size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " payload exceeds configured byte budget");
    }
    const SyncPosixRegularFileSnapshotMetadata observed =
        observe_sync_posix_regular_file_descriptor_or_throw(
            source_descriptor,
            SyncPosixDescriptorLinkPolicy::stable_named_object,
            store.label + " payload source preflight");
    if (observed != expected_source) {
        throw std::runtime_error(
            store.label + " payload source changed after observation");
    }

    SyncReplicaFilePayloadStoreMutationBatch batch =
        begin_mutation_batch_or_throw();
    return batch.put_payload_from_borrowed_descriptor_or_throw(
        source_descriptor, expected_source, std::move(content_sha256));
}

SyncReplicaFilePayloadStoreStageResult
SyncReplicaFilePayloadStore::stage_payload_range_or_throw(
    std::string content_sha256,
    std::uint64_t total_size_bytes,
    std::uint64_t offset_bytes,
    std::string chunk_sha256,
    std::string bytes) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label + " read-only inspection store cannot stage payload ranges");
    }
    if (!is_lowercase_sha256_hex(content_sha256) ||
        !is_lowercase_sha256_hex(chunk_sha256)) {
        throw std::invalid_argument(
            store.label + " staged payload range digest is invalid");
    }
    const std::uint64_t range_bytes =
        size_to_u64_or_throw(bytes.size(), store.label + " staged range");
    if (total_size_bytes == 0U ||
        total_size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " staged payload total size is invalid");
    }
    if (range_bytes == 0U || offset_bytes >= total_size_bytes ||
        range_bytes > total_size_bytes - offset_bytes) {
        throw std::invalid_argument(
            store.label + " staged payload range extent is invalid");
    }
    if (sha256_hex(bytes) != chunk_sha256) {
        throw std::invalid_argument(
            store.label + " staged payload range digest does not match its bytes");
    }

    store.root_authority.verify_or_throw(
        store.label + " staged payload source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, store.label);
    StoreLease mutation_lease = acquire_store_lease_or_throw(
        store.root_authority, store.identity_basename, store.expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " staged payload range",
        StoreObservationDurability::Reconcile);

    auto scan = [&](std::string_view phase) {
        return scan_store_under_lease_or_throw(
            store.root_authority, store.limits, store.identity_basename,
            store.expected_identity, mutation_lease,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            store.label + " staged payload " + std::string(phase),
            StoreObservationDurability::Reconcile,
            store.verification_cache.get());
    };

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            store.root_authority, store.label + " staged payload root");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    const SyncDirectoryAttestation& root_attestation =
        store.root_authority.attestation();
    const std::string assembly_basename =
        assembly_basename_or_throw(content_sha256);

    auto remove_matching_transients = [&](const ScannedPayloadIndex& scanned) {
        bool changed = false;
        for (const StagedRangeEntry& entry : scanned.staged_ranges) {
            if (entry.content_sha256 != content_sha256) continue;
            unlink_scanned_private_file_or_throw(
                root_descriptor.get(), entry.basename, entry.status,
                root_attestation,
                store.label + " completed staged range cleanup");
            changed = true;
        }
        for (const AssemblyEntry& entry : scanned.assemblies) {
            if (entry.basename != assembly_basename) continue;
            unlink_scanned_private_file_or_throw(
                root_descriptor.get(), entry.basename, entry.status,
                root_attestation,
                store.label + " completed assembly cleanup");
            changed = true;
        }
        if (changed) {
            fsync_or_throw(
                root_descriptor.get(),
                store.label + " completed staged payload cleanup directory");
        }
    };

    ScannedPayloadIndex before = scan("preflight");
    if (!before.publication_residues.empty()) {
        remove_scanned_publication_residues_or_throw(
            store.root_authority, before.publication_residues,
            store.label + " stale staged publication-residue cleanup");
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " staged publication-residue cleanup lease cutpoint");
        before = scan("post-residue-cleanup");
    }
    const PayloadIndexEntry* durable =
        find_entry(before.entries, content_sha256);
    if (durable != nullptr) {
        if (durable->size_bytes != total_size_bytes) {
            throw std::runtime_error(
                store.label + " durable payload size conflicts with staged operation");
        }
        remove_matching_transients(before);
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " existing staged payload final lease cutpoint");
        return SyncReplicaFilePayloadStoreStageResult{
            SyncReplicaFilePayloadStoreStageDisposition::
                CompletedAlreadyPresent,
            std::move(content_sha256), total_size_bytes, total_size_bytes, 0U};
    }
    if (before.entries.size() >= store.limits.max_entries ||
        before.indexed_bytes > store.limits.max_indexed_bytes ||
        total_size_bytes >
            store.limits.max_indexed_bytes - before.indexed_bytes) {
        throw std::length_error(
            store.label + " cannot admit the completed staged payload");
    }

    StagedPrefix prefix = staged_prefix_for_content_or_throw(
        before, content_sha256, total_size_bytes,
        store.label + " staged payload preflight");
    const StagedRangeEntry* existing_range =
        staged_range_at_offset_or_none(before, content_sha256, offset_bytes);
    bool inserted_range = false;
    if (existing_range != nullptr) {
        if (existing_range->chunk_sha256 != chunk_sha256 ||
            existing_range->size_bytes != range_bytes ||
            existing_range->basename != staged_range_basename_or_throw(
                content_sha256, offset_bytes, chunk_sha256)) {
            throw std::runtime_error(
                store.label + " staged payload range conflicts at one offset");
        }
    } else {
        if (offset_bytes != prefix.next_offset_bytes) {
            throw std::runtime_error(
                store.label + " staged payload range is not the next contiguous offset");
        }
        if (before.transient_entry_count >=
                store.limits.max_transient_entries ||
            before.transient_reserved_bytes >
                store.limits.max_transient_bytes ||
            range_bytes >
                store.limits.max_transient_bytes -
                    before.transient_reserved_bytes) {
            throw std::length_error(
                store.label + " staged payload range exceeds transient capacity");
        }
        const std::string range_basename = staged_range_basename_or_throw(
            content_sha256, offset_bytes, chunk_sha256);
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " staged payload pre-publication lease cutpoint");
        try {
            write_sync_file_atomically_create_new_under_directory_or_throw(
                store.root_authority, fs::path(range_basename), byte_span(bytes),
                store.label + " staged payload range publication");
            inserted_range = true;
        } catch (...) {
            const std::exception_ptr original = std::current_exception();
            const ScannedPayloadIndex reconciled = scan("failed range reconciliation");
            const StagedRangeEntry* exact = staged_range_at_offset_or_none(
                reconciled, content_sha256, offset_bytes);
            if (exact == nullptr || exact->chunk_sha256 != chunk_sha256 ||
                exact->size_bytes != range_bytes ||
                exact->basename != range_basename) {
                std::rethrow_exception(original);
            }
        }
    }

    ScannedPayloadIndex after = scan("post-range");
    prefix = staged_prefix_for_content_or_throw(
        after, content_sha256, total_size_bytes,
        store.label + " staged payload post-range");
    if (prefix.next_offset_bytes < total_size_bytes) {
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " staged payload progress final lease cutpoint");
        return SyncReplicaFilePayloadStoreStageResult{
            SyncReplicaFilePayloadStoreStageDisposition::Progress,
            std::move(content_sha256), total_size_bytes,
            prefix.next_offset_bytes,
            inserted_range ? range_bytes : 0U};
    }
    if (prefix.next_offset_bytes != total_size_bytes) {
        throw std::logic_error(
            store.label + " staged payload prefix crossed its exact total size");
    }

    // A previous crash may have left only the exact private assembly name.
    // Remove it under the same exclusive store lease before rebuilding from
    // independently verified immutable ranges.
    bool removed_assembly = false;
    for (const AssemblyEntry& entry : after.assemblies) {
        if (entry.basename != assembly_basename) continue;
        unlink_scanned_private_file_or_throw(
            root_descriptor.get(), entry.basename, entry.status,
            root_attestation,
            store.label + " stale payload assembly cleanup");
        removed_assembly = true;
    }
    if (removed_assembly) {
        fsync_or_throw(
            root_descriptor.get(),
            store.label + " stale payload assembly cleanup directory");
        after = scan("post-assembly-cleanup");
        prefix = staged_prefix_for_content_or_throw(
            after, content_sha256, total_size_bytes,
            store.label + " staged payload post-assembly-cleanup");
        if (prefix.next_offset_bytes != total_size_bytes) {
            throw std::runtime_error(
                store.label + " staged payload prefix changed during assembly cleanup");
        }
    }
    if (after.transient_entry_count >= store.limits.max_transient_entries ||
        after.transient_reserved_bytes >
            store.limits.max_transient_bytes ||
        total_size_bytes >
            store.limits.max_transient_bytes -
                after.transient_reserved_bytes) {
        throw std::length_error(
            store.label + " payload assembly exceeds transient capacity");
    }

    int create_flags = O_WRONLY | O_CREAT | O_EXCL;
#ifdef O_CLOEXEC
    create_flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    create_flags |= O_NOFOLLOW;
#endif
    int assembly_fd;
    do {
        assembly_fd = ::openat(
            root_descriptor.get(), assembly_basename.c_str(), create_flags,
            S_IRUSR | S_IWUSR);
    } while (assembly_fd < 0 && errno == EINTR);
    if (assembly_fd < 0) {
        const int error = errno;
        throw std::runtime_error(
            store.label + " payload assembly create failed: " +
            error_text(error));
    }
    OwnedFd assembly_file(assembly_fd);
    fchmod_private_or_throw(
        assembly_file.get(), store.label + " payload assembly");
    struct stat assembly_status{};
    if (::fstat(assembly_file.get(), &assembly_status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            store.label + " payload assembly fstat failed: " +
            error_text(error));
    }
    require_private_regular_file_or_throw(
        assembly_status, root_attestation,
        store.label + " payload assembly");

    bool assembly_published = false;
    try {
        Sha256DigestBuilder whole_digest;
        std::uint64_t assembled_bytes = 0U;
        for (const StagedRangeEntry* entry : prefix.ranges) {
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                root_descriptor.get(), entry->basename, store.root_path,
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                store.label + " assembly input " + entry->basename);
            OwnedFd range_file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                store.label + " assembly input " + entry->basename);
            if (!same_regular_file_observation(entry->status, opened.status)) {
                throw std::runtime_error(
                    store.label + " staged range changed before assembly");
            }
            const StreamedFileDigest streamed =
                stream_hash_regular_file_or_throw(
                    range_file.get(), opened.status,
                    std::pair<std::uint64_t, std::uint64_t>{
                        0U, entry->size_bytes},
                    store.label + " assembly input " + entry->basename);
            if (streamed.sha256 != entry->chunk_sha256 ||
                streamed.selected_bytes.size() != entry->size_bytes) {
                throw std::runtime_error(
                    store.label + " staged range lost its exact chunk identity");
            }
            write_all_or_throw(
                assembly_file.get(), streamed.selected_bytes,
                store.label + " payload assembly");
            whole_digest.update(streamed.selected_bytes);
            assembled_bytes = checked_add_u64_or_throw(
                assembled_bytes, entry->size_bytes,
                store.label + " assembled payload size");
        }
        if (assembled_bytes != total_size_bytes) {
            throw std::logic_error(
                store.label + " payload assembly did not consume the exact prefix");
        }
        fsync_or_throw(
            assembly_file.get(), store.label + " payload assembly file");
        struct stat completed_status{};
        if (::fstat(assembly_file.get(), &completed_status) != 0) {
            const int error = errno;
            throw std::runtime_error(
                store.label + " completed payload assembly fstat failed: " +
                error_text(error));
        }
        require_private_regular_file_or_throw(
            completed_status, root_attestation,
            store.label + " completed payload assembly");
        if (static_cast<std::uint64_t>(completed_status.st_size) !=
                total_size_bytes ||
            whole_digest.finish_hex() != content_sha256) {
            throw std::runtime_error(
                store.label + " completed payload assembly failed whole-file verification");
        }
        verify_named_regular_file_or_throw(
            root_descriptor.get(), assembly_basename, completed_status,
            root_attestation,
            store.label + " completed payload assembly");
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " payload assembly pre-publication lease cutpoint");
        rename_noreplace_at_or_throw(
            root_descriptor.get(), assembly_basename, content_sha256,
            store.label + " payload assembly publication");
        assembly_published = true;
        fsync_or_throw(
            root_descriptor.get(),
            store.label + " payload assembly publication directory");
        struct stat published_status{};
        if (::fstat(assembly_file.get(), &published_status) != 0) {
            const int error = errno;
            throw std::runtime_error(
                store.label + " published payload fstat failed: " +
                error_text(error));
        }
        require_private_regular_file_or_throw(
            published_status, root_attestation,
            store.label + " published assembled payload");
        if (!same_regular_file_rename_transition(
                completed_status, published_status)) {
            throw std::runtime_error(
                store.label +
                " assembled payload changed across namespace publication");
        }
        verify_named_regular_file_or_throw(
            root_descriptor.get(), content_sha256, published_status,
            root_attestation,
            store.label + " published assembled payload");

        for (const StagedRangeEntry* entry : prefix.ranges) {
            unlink_scanned_private_file_or_throw(
                root_descriptor.get(), entry->basename, entry->status,
                root_attestation,
                store.label + " published range cleanup");
        }
        fsync_or_throw(
            root_descriptor.get(),
            store.label + " published range cleanup directory");
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " staged payload completion final lease cutpoint");
        insert_payload_index_entry_or_throw(
            after,
            PayloadIndexEntry{
                content_sha256, total_size_bytes, published_status},
            store.limits,
            store.label + " completed assembled payload index update");
        retain_completed_payload_verification_best_effort(
            store.root_authority, store.limits, store.expected_identity,
            mutation_lease, store.verification_cache, after,
            total_size_bytes,
            store.label + " completed assembled payload");
        return SyncReplicaFilePayloadStoreStageResult{
            SyncReplicaFilePayloadStoreStageDisposition::CompletedInserted,
            std::move(content_sha256), total_size_bytes, total_size_bytes,
            inserted_range ? range_bytes : 0U};
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        if (!assembly_published) {
            try {
                struct stat named{};
                if (::fstatat(
                        root_descriptor.get(), assembly_basename.c_str(),
                        &named, AT_SYMLINK_NOFOLLOW) == 0 &&
                    same_identity(assembly_status, named)) {
                    unlinkat_or_throw(
                        root_descriptor.get(), assembly_basename,
                        store.label + " failed payload assembly cleanup");
                    fsync_or_throw(
                        root_descriptor.get(),
                        store.label + " failed payload assembly cleanup directory");
                }
            } catch (...) {
                // Preserve the original failure. The exact private assembly
                // name is admitted by the scanner and can be removed on retry.
            }
        }
        std::rethrow_exception(original);
    }
}

SyncReplicaFilePayloadStoreStageResult
SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw(
    std::string content_sha256,
    std::uint64_t total_size_bytes,
    std::uint64_t offset_bytes,
    std::string chunk_sha256,
    std::string_view bytes) {
    return stage_payload_prefix_impl_or_throw(
        std::move(content_sha256), total_size_bytes, offset_bytes,
        std::move(chunk_sha256), bytes, false, false);
}

SyncReplicaFilePayloadStoreStageResult
SyncReplicaFilePayloadStore::
stage_payload_prefix_deferring_terminal_verification_or_throw(
    std::string content_sha256,
    std::uint64_t total_size_bytes,
    std::uint64_t offset_bytes,
    std::string chunk_sha256,
    std::string_view bytes) {
    return stage_payload_prefix_impl_or_throw(
        std::move(content_sha256), total_size_bytes, offset_bytes,
        std::move(chunk_sha256), bytes, false, true);
}

SyncReplicaFilePayloadStoreStageResult
SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw(
    std::string content_sha256,
    std::uint64_t total_size_bytes,
    std::uint64_t offset_bytes,
    std::string chunk_sha256,
    std::string_view bytes,
    bool terminal_verification_only,
    bool defer_terminal_verification) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    auto note_terminal_work = [&](std::uint64_t verified_offset_bytes) noexcept {
        if (!store.terminal_verification_observation_known) return;
        try {
            // This cache is scheduler acceleration published after durable
            // staged-prefix or journal effects. Cross-process mutation can make
            // an older complete projection overcount the current namespace,
            // and allocation itself can fail. Neither condition may turn an
            // already committed payload effect into a reported operation
            // failure. Invalidate the advisory projection and require the next
            // ordinary complete scan to rebuild it.
            upsert_terminal_verification_work_if_known_or_throw(
                true, store.terminal_verification_work,
                SyncReplicaFilePayloadStoreTerminalVerificationWork{
                    content_sha256, total_size_bytes, verified_offset_bytes},
                store.limits,
                store.label + " staged-prefix scheduler cache");
        } catch (const std::exception&) {
            store.terminal_verification_work.clear();
            store.terminal_verification_observation_known = false;
        }
    };
    auto note_terminal_complete = [&]() noexcept {
        erase_terminal_verification_work_if_known(
            store.terminal_verification_observation_known,
            store.terminal_verification_work, content_sha256);
    };
    if (store.disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect) {
        throw std::logic_error(
            store.label +
            " read-only inspection store cannot stage payload prefixes");
    }
    if (terminal_verification_only && defer_terminal_verification) {
        throw std::logic_error(
            store.label +
            " terminal-only staging cannot defer terminal verification");
    }
    if (!is_lowercase_sha256_hex(content_sha256) ||
        (!terminal_verification_only &&
         !is_lowercase_sha256_hex(chunk_sha256))) {
        throw std::invalid_argument(
            store.label + " staged payload prefix digest is invalid");
    }
    const std::uint64_t range_bytes =
        size_to_u64_or_throw(bytes.size(), store.label + " staged prefix range");
    if (total_size_bytes == 0U ||
        total_size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " staged payload prefix total size is invalid");
    }
    if (terminal_verification_only) {
        if (range_bytes != 0U || offset_bytes != total_size_bytes ||
            !chunk_sha256.empty()) {
            throw std::logic_error(
                store.label +
                " internal terminal verification call carries source range authority");
        }
    } else {
        if (range_bytes == 0U || offset_bytes >= total_size_bytes ||
            range_bytes > total_size_bytes - offset_bytes) {
            throw std::invalid_argument(
                store.label + " staged payload prefix range extent is invalid");
        }
        Sha256DigestBuilder range_digest;
        range_digest.update(bytes);
        if (range_digest.finish_hex() != chunk_sha256) {
            throw std::invalid_argument(
                store.label +
                " staged payload prefix range digest does not match its bytes");
        }
    }

    store.root_authority.verify_or_throw(
        store.label + " staged payload prefix source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.legacy_identity_basename, store.expected_identity,
        store.disposition, store.allow_existing_payload_adoption,
        *store.verification_cache, store.label);

    bool delegate_to_legacy_range_owner = false;
    {
        StoreLease mutation_lease = acquire_store_lease_or_throw(
            store.root_authority, store.identity_basename,
            store.expected_identity,
            SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            store.label + " staged payload prefix",
            StoreObservationDurability::Reconcile);

        auto observe = [&](std::string_view phase) {
            const std::string observation_label =
                store.label + " staged payload prefix " +
                std::string(phase);
            if (terminal_verification_only) {
                return
                    observe_staged_prefix_terminal_target_under_lease_or_throw(
                        store.root_authority, store.limits,
                        store.expected_identity, content_sha256,
                        total_size_bytes, mutation_lease,
                        observation_label);
            }
            return observe_staged_prefix_namespace_under_lease_or_throw(
                store.root_authority, store.limits, store.identity_basename,
                store.expected_identity, content_sha256, total_size_bytes,
                mutation_lease, observation_label);
        };
        auto scan = [&](std::string_view phase) {
            return scan_store_under_lease_or_throw(
                store.root_authority, store.limits, store.identity_basename,
                store.expected_identity, mutation_lease,
                SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
                store.label + " staged payload prefix " +
                    std::string(phase),
                StoreObservationDurability::Reconcile,
                store.verification_cache.get());
        };

        StagedPrefixNamespaceObservation observed = observe("preflight");
        if (!observed.prefix.has_value() &&
            !observed.durable_payload_name_present &&
            observed.legacy_range_or_assembly_present &&
            !terminal_verification_only) {
            // A rev0941 transfer already owns this digest. Release the new
            // owner's lease before entering the compatibility path so restart
            // resumes exact durable work rather than creating a second owner.
            delegate_to_legacy_range_owner = true;
        } else {
            using Access = sync_directory_authority_detail::
                SyncDirectoryAuthorityAccess;
            auto descriptor_lease =
                Access::duplicate_shared_open_description_or_throw(
                    store.root_authority,
                    store.label + " staged payload prefix root");
            OwnedFd root_descriptor(descriptor_lease.release_descriptor());
            const SyncDirectoryAttestation& root_attestation =
                store.root_authority.attestation();
            const std::string legacy_assembly =
                assembly_basename_or_throw(content_sha256);

            const std::string terminal_verification_basename =
                terminal_verification_basename_or_throw(content_sha256);
            const std::uint64_t terminal_verification_journal_bytes =
                sync_replica_file_payload_terminal_verification_journal_exact_bytes();
            const std::uint64_t terminal_verification_slot_bytes =
                sync_replica_file_payload_terminal_verification_slot_exact_bytes();
            const SyncPosixRegularFileSnapshotMetadata identity_metadata =
                sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                    mutation_lease.identity_status(),
                    SyncPosixDescriptorLinkPolicy::exactly_one,
                    store.label +
                        " staged prefix terminal verification identity");

            auto observe_terminal_verification = [
                &](const struct stat* expected_prefix_status) {
                TerminalVerificationStateFileObservation out =
                    observe_terminal_verification_state_file_or_throw(
                        root_descriptor.get(), store.root_authority.path(),
                        descriptor_lease.resolution_capability(),
                        descriptor_lease.mount_identity(), root_attestation,
                        store.limits, store.expected_identity,
                        mutation_lease.identity_status(), content_sha256,
                        total_size_bytes, true,
                        store.label +
                            " staged prefix terminal verification observation");
                if (out.usable && out.journal.has_value() &&
                    expected_prefix_status != nullptr) {
                    const auto& state = out.journal->latest_state;
                    const auto payload_metadata =
                        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                            *expected_prefix_status,
                            SyncPosixDescriptorLinkPolicy::exactly_one,
                            store.label +
                                " staged prefix terminal verification payload binding");
                    out.usable =
                        state.staged_prefix_metadata == payload_metadata &&
                        state.verified_offset_bytes < total_size_bytes;
                }
                return out;
            };

            auto publish_terminal_verification = [
                &](const SyncReplicaFilePayloadTerminalVerificationState& state,
                    const TerminalVerificationStateFileObservation& previous,
                    const struct stat& expected_prefix_status) {
                std::uint32_t expected_slot = 0U;
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " terminal verification pre-publication lease cutpoint");
                if (previous.usable && previous.journal.has_value()) {
                    expected_slot =
                        sync_replica_file_payload_terminal_verification_next_slot_index(
                            *previous.journal);
                    const std::string encoded =
                        serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                            state, store.limits.max_payload_bytes,
                            store.label +
                                " staged prefix terminal verification slot");
                    SyncPosixOpenedRegularFile opened =
                        open_staged_prefix_writable_or_throw(
                            root_descriptor.get(),
                            terminal_verification_basename,
                            previous.status, root_attestation,
                            store.label +
                                " staged prefix terminal verification journal");
                    OwnedFd journal_file(opened.descriptor);
                    if (opened.status.st_size < 0 ||
                        static_cast<std::uint64_t>(opened.status.st_size) !=
                            terminal_verification_journal_bytes) {
                        throw std::runtime_error(
                            store.label +
                            " terminal verification journal changed size before update");
                    }
                    pwrite_all_or_throw(
                        journal_file.get(), encoded,
                        static_cast<std::uint64_t>(expected_slot) *
                            terminal_verification_slot_bytes,
                        store.label +
                            " staged prefix terminal verification slot update");
                    fsync_or_throw(
                        journal_file.get(),
                        store.label +
                            " staged prefix terminal verification journal");
                    struct stat after{};
                    if (::fstat(journal_file.get(), &after) != 0) {
                        const int error = errno;
                        throw std::runtime_error(
                            store.label +
                            " terminal verification journal fstat failed: " +
                            error_text(error));
                    }
                    require_private_regular_file_or_throw(
                        after, root_attestation,
                        store.label +
                            " updated terminal verification journal");
                    if (!same_regular_file_write_transition(
                            opened.status, after)) {
                        throw PayloadStoreObservationStaleError(
                            store.label +
                            " terminal verification journal identity changed during update");
                    }
                    verify_named_regular_file_or_throw(
                        root_descriptor.get(),
                        terminal_verification_basename, after,
                        root_attestation,
                        store.label +
                            " updated terminal verification journal");
                } else {
                    const std::string encoded =
                        initial_sync_replica_file_payload_terminal_verification_journal_or_throw(
                            state, store.limits.max_payload_bytes,
                            store.label +
                                " staged prefix terminal verification journal");
                    if (previous.present) {
                        if (!previous.metadata.has_value()) {
                            throw std::logic_error(
                                store.label +
                                " terminal verification observation lacks metadata");
                        }
                        write_sync_file_atomically_replace_expected_under_directory_or_throw(
                            store.root_authority,
                            fs::path(terminal_verification_basename),
                            byte_span(encoded), *previous.metadata,
                            store.label +
                                " staged prefix terminal verification replacement");
                    } else {
                        write_sync_file_atomically_create_new_under_directory_or_throw(
                            store.root_authority,
                            fs::path(terminal_verification_basename),
                            byte_span(encoded),
                            store.label +
                                " staged prefix terminal verification creation");
                    }
                }
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " terminal verification post-publication lease cutpoint");

                TerminalVerificationStateFileObservation current =
                    observe_terminal_verification(&expected_prefix_status);
                if (!current.present || !current.usable ||
                    !current.journal.has_value() ||
                    current.journal->latest_slot_index != expected_slot ||
                    current.journal->latest_state != state) {
                    throw std::runtime_error(
                        store.label +
                        " terminal verification publication failed exact reproof");
                }
                return current;
            };

            auto remove_matching_transients = [
                &](const ScannedPayloadIndex& scanned,
                    bool include_prefix_owner) {
                bool changed = false;
                for (const StagedRangeEntry& entry : scanned.staged_ranges) {
                    if (entry.content_sha256 != content_sha256) continue;
                    unlink_scanned_private_file_or_throw(
                        root_descriptor.get(), entry.basename, entry.status,
                        root_attestation,
                        store.label +
                            " completed legacy staged range cleanup");
                    changed = true;
                }
                for (const AssemblyEntry& entry : scanned.assemblies) {
                    if (entry.basename != legacy_assembly) continue;
                    unlink_scanned_private_file_or_throw(
                        root_descriptor.get(), entry.basename, entry.status,
                        root_attestation,
                        store.label +
                            " completed legacy assembly cleanup");
                    changed = true;
                }
                const TerminalVerificationStateFileObservation verification =
                    observe_terminal_verification(nullptr);
                if (verification.present) {
                    unlink_scanned_private_file_or_throw(
                        root_descriptor.get(),
                        terminal_verification_basename_or_throw(content_sha256),
                        verification.status, root_attestation,
                        store.label +
                            " completed staged-prefix verification cleanup");
                    changed = true;
                }
                if (include_prefix_owner) {
                    for (const StagedPrefixEntry& entry :
                         scanned.staged_prefixes) {
                        if (entry.content_sha256 != content_sha256) continue;
                        unlink_scanned_private_file_or_throw(
                            root_descriptor.get(), entry.basename,
                            entry.status, root_attestation,
                            store.label +
                                " completed staged prefix cleanup");
                        changed = true;
                    }
                }
                if (changed) {
                    fsync_or_throw(
                        root_descriptor.get(),
                        store.label +
                            " completed staged payload cleanup directory");
                }
            };

            std::optional<ScannedPayloadIndex> preflight;
            if (observed.publication_residue_present ||
                observed.durable_payload_name_present ||
                !observed.prefix.has_value() ||
                observed.legacy_range_or_assembly_present) {
                preflight.emplace(scan("full preflight"));
                if (!preflight->publication_residues.empty()) {
                    remove_scanned_publication_residues_or_throw(
                        store.root_authority,
                        preflight->publication_residues,
                        store.label +
                            " stale staged-prefix publication-residue cleanup");
                    mutation_lease.verify_or_throw(
                        store.root_authority,
                        store.label +
                            " staged-prefix residue cleanup lease cutpoint");
                    preflight.emplace(scan("post-residue cleanup"));
                    observed = observe("post-residue cleanup");
                }

                const PayloadIndexEntry* durable =
                    find_entry(preflight->entries, content_sha256);
                if (durable != nullptr) {
                    if (durable->size_bytes != total_size_bytes) {
                        throw std::runtime_error(
                            store.label +
                            " durable payload size conflicts with staged prefix operation");
                    }
                    remove_matching_transients(*preflight, true);
                    mutation_lease.verify_or_throw(
                        store.root_authority,
                        store.label +
                            " existing staged prefix final lease cutpoint");
                    note_terminal_complete();
                    return SyncReplicaFilePayloadStoreStageResult{
                        SyncReplicaFilePayloadStoreStageDisposition::
                            CompletedAlreadyPresent,
                        std::move(content_sha256), total_size_bytes,
                        total_size_bytes, 0U, 0U, total_size_bytes};
                }

                const StagedPrefixEntry* scanned_prefix =
                    staged_prefix_for_content_or_none(
                        *preflight, content_sha256);
                if (scanned_prefix != nullptr) {
                    if (scanned_prefix->total_size_bytes != total_size_bytes) {
                        throw std::runtime_error(
                            store.label +
                            " staged prefix total size conflicts for one content digest");
                    }
                    observed.prefix = *scanned_prefix;
                } else if (observed.prefix.has_value()) {
                    throw std::runtime_error(
                        store.label +
                        " staged prefix disappeared between leased observations");
                }

                if (observed.prefix.has_value() &&
                    observed.legacy_range_or_assembly_present) {
                    remove_matching_transients(*preflight, false);
                    mutation_lease.verify_or_throw(
                        store.root_authority,
                        store.label +
                            " legacy staged transfer cleanup lease cutpoint");
                    observed = observe("post-legacy cleanup");
                    preflight.reset();
                }
            }

            StagedPrefixEntry prefix;
            if (observed.prefix.has_value()) {
                prefix = *observed.prefix;
                if (prefix.total_size_bytes != total_size_bytes) {
                    throw std::runtime_error(
                        store.label +
                        " staged prefix total size conflicts for one content digest");
                }
            } else {
                if (terminal_verification_only) {
                    throw std::runtime_error(
                        store.label +
                        " terminal staged-prefix verification has no completed prefix owner");
                }
                if (!preflight.has_value()) {
                    preflight.emplace(scan("new-owner admission"));
                }
                if (find_entry(preflight->entries, content_sha256) != nullptr ||
                    staged_prefix_for_content_or_none(
                        *preflight, content_sha256) != nullptr) {
                    throw std::runtime_error(
                        store.label +
                        " staged prefix admission changed after its leased observation");
                }
                if (preflight->entries.size() >= store.limits.max_entries ||
                    preflight->indexed_bytes >
                        store.limits.max_indexed_bytes ||
                    total_size_bytes >
                        store.limits.max_indexed_bytes -
                            preflight->indexed_bytes) {
                    throw std::length_error(
                        store.label +
                        " cannot admit the completed staged prefix payload");
                }
                if (preflight->transient_entry_count >=
                        store.limits.max_transient_entries ||
                    preflight->transient_reserved_bytes >
                        store.limits.max_transient_bytes ||
                    total_size_bytes >
                        store.limits.max_transient_bytes -
                            preflight->transient_reserved_bytes) {
                    throw std::length_error(
                        store.label +
                        " staged prefix reservation exceeds transient capacity");
                }

                const std::string basename =
                    staged_prefix_basename_or_throw(
                        content_sha256, total_size_bytes, 0U);
                int create_flags = O_RDWR | O_CREAT | O_EXCL;
#ifdef O_CLOEXEC
                create_flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
                create_flags |= O_NOFOLLOW;
#endif
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " staged prefix creation lease cutpoint");
                int created_fd;
                do {
                    created_fd = ::openat(
                        root_descriptor.get(), basename.c_str(), create_flags,
                        S_IRUSR | S_IWUSR);
                } while (created_fd < 0 && errno == EINTR);
                if (created_fd < 0) {
                    const int error = errno;
                    throw std::runtime_error(
                        store.label + " staged prefix create failed: " +
                        error_text(error));
                }
                OwnedFd created(created_fd);
                fchmod_private_or_throw(
                    created.get(), store.label + " staged prefix");
                struct stat status{};
                if (::fstat(created.get(), &status) != 0) {
                    const int error = errno;
                    throw std::runtime_error(
                        store.label + " staged prefix fstat failed: " +
                        error_text(error));
                }
                require_private_regular_file_or_throw(
                    status, root_attestation,
                    store.label + " staged prefix");
                if (status.st_size != 0) {
                    throw std::runtime_error(
                        store.label +
                        " newly created staged prefix is not empty");
                }
                fsync_or_throw(
                    created.get(), store.label + " staged prefix file");
                verify_named_regular_file_or_throw(
                    root_descriptor.get(), basename, status,
                    root_attestation,
                    store.label + " staged prefix creation");
                fsync_or_throw(
                    root_descriptor.get(),
                    store.label + " staged prefix creation directory");
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " staged prefix creation final lease cutpoint");
                prefix = StagedPrefixEntry{
                    basename, content_sha256, total_size_bytes, 0U, 0U,
                    status};
            }

            SyncPosixOpenedRegularFile opened =
                open_staged_prefix_writable_or_throw(
                    root_descriptor.get(), prefix.basename, prefix.status,
                    root_attestation,
                    store.label + " staged prefix writable owner");
            OwnedFd prefix_file(opened.descriptor);
            prefix.status = opened.status;
            prefix.actual_size_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);

            if (prefix.actual_size_bytes >
                prefix.committed_prefix_bytes) {
                // The basename is the durable commit record. Bytes beyond that
                // cutpoint were written before a crash but never committed by
                // the no-replace rename, so they are discarded before replay.
                ftruncate_or_throw(
                    prefix_file.get(), prefix.committed_prefix_bytes,
                    store.label + " staged prefix crash-tail recovery");
                fsync_or_throw(
                    prefix_file.get(),
                    store.label + " staged prefix crash-tail recovery file");
                struct stat truncated{};
                if (::fstat(prefix_file.get(), &truncated) != 0) {
                    const int error = errno;
                    throw std::runtime_error(
                        store.label +
                        " staged prefix crash-tail fstat failed: " +
                        error_text(error));
                }
                require_private_regular_file_or_throw(
                    truncated, root_attestation,
                    store.label + " truncated staged prefix");
                if (static_cast<std::uint64_t>(truncated.st_size) !=
                    prefix.committed_prefix_bytes) {
                    throw std::runtime_error(
                        store.label +
                        " staged prefix crash-tail truncation missed its commit cutpoint");
                }
                verify_named_regular_file_or_throw(
                    root_descriptor.get(), prefix.basename, truncated,
                    root_attestation,
                    store.label + " truncated staged prefix");
                prefix.status = truncated;
                prefix.actual_size_bytes = prefix.committed_prefix_bytes;
            }

            std::uint64_t accepted_range_bytes = 0U;
            if (!terminal_verification_only) {
                const std::uint64_t range_end = checked_add_u64_or_throw(
                    offset_bytes, range_bytes,
                    store.label + " staged prefix range end");
                if (offset_bytes < prefix.committed_prefix_bytes) {
                    if (range_end > prefix.committed_prefix_bytes) {
                        throw std::runtime_error(
                            store.label +
                            " staged payload prefix range overlaps its committed boundary");
                    }
                    const CopiedFileRange committed =
                        copy_hash_regular_file_range_or_throw(
                            prefix_file.get(), prefix.status, offset_bytes,
                            range_bytes,
                            store.label + " committed staged prefix replay");
                    if (committed.chunk_sha256 != chunk_sha256 ||
                        committed.bytes != bytes) {
                        throw std::runtime_error(
                            store.label +
                            " staged payload prefix range conflicts with committed prefix");
                    }
                } else if (offset_bytes > prefix.committed_prefix_bytes) {
                    throw std::runtime_error(
                        store.label +
                        " staged payload prefix range is not the next contiguous offset");
                } else {
                    pwrite_all_or_throw(
                        prefix_file.get(), bytes, offset_bytes,
                        store.label + " staged prefix range");
                    fsync_or_throw(
                        prefix_file.get(),
                        store.label + " staged prefix range file");

                    struct stat advanced{};
                    if (::fstat(prefix_file.get(), &advanced) != 0) {
                        const int error = errno;
                        throw std::runtime_error(
                            store.label + " advanced staged prefix fstat failed: " +
                            error_text(error));
                    }
                    require_private_regular_file_or_throw(
                        advanced, root_attestation,
                        store.label + " advanced staged prefix");
                    if (static_cast<std::uint64_t>(advanced.st_size) != range_end) {
                        throw std::runtime_error(
                            store.label +
                            " staged prefix write did not reach its exact next cutpoint");
                    }
                    verify_named_regular_file_or_throw(
                        root_descriptor.get(), prefix.basename, advanced,
                        root_attestation,
                        store.label + " advanced staged prefix pre-commit");
                    mutation_lease.verify_or_throw(
                        store.root_authority,
                        store.label +
                            " staged prefix pre-commit lease cutpoint");

                    const std::string advanced_basename =
                        staged_prefix_basename_or_throw(
                            content_sha256, total_size_bytes, range_end);
                    rename_noreplace_at_or_throw(
                        root_descriptor.get(), prefix.basename,
                        advanced_basename,
                        store.label + " staged prefix commit");
                    fsync_or_throw(
                        root_descriptor.get(),
                        store.label + " staged prefix commit directory");

                    // rename(2) legitimately advances inode ctime. Retaining the
                    // pre-rename observation would make the final publication scan
                    // reject our own committed prefix as externally changed.
                    struct stat committed{};
                    if (::fstat(prefix_file.get(), &committed) != 0) {
                        const int error = errno;
                        throw std::runtime_error(
                            store.label +
                            " committed staged prefix fstat failed: " +
                            error_text(error));
                    }
                    require_private_regular_file_or_throw(
                        committed, root_attestation,
                        store.label + " committed staged prefix");
                    if (!same_regular_file_rename_transition(
                            advanced, committed) ||
                        static_cast<std::uint64_t>(committed.st_size) !=
                            range_end) {
                        throw std::runtime_error(
                            store.label +
                            " staged prefix commit changed beyond the permitted ctime transition");
                    }
                    verify_named_regular_file_or_throw(
                        root_descriptor.get(), advanced_basename, committed,
                        root_attestation,
                        store.label + " committed staged prefix");
                    prefix.basename = advanced_basename;
                    prefix.committed_prefix_bytes = range_end;
                    prefix.actual_size_bytes = range_end;
                    prefix.status = committed;
                    accepted_range_bytes = range_bytes;
                }
            }

            if (prefix.committed_prefix_bytes < total_size_bytes) {
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " staged prefix progress final lease cutpoint");
                note_terminal_complete();
                return SyncReplicaFilePayloadStoreStageResult{
                    SyncReplicaFilePayloadStoreStageDisposition::Progress,
                    std::move(content_sha256), total_size_bytes,
                    prefix.committed_prefix_bytes, accepted_range_bytes};
            }
            if (prefix.committed_prefix_bytes != total_size_bytes ||
                prefix.actual_size_bytes != total_size_bytes) {
                throw std::logic_error(
                    store.label +
                    " staged prefix crossed its exact total size");
            }
            if (defer_terminal_verification) {
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " deferred terminal verification final lease cutpoint");
                note_terminal_work(0U);
                return SyncReplicaFilePayloadStoreStageResult{
                    SyncReplicaFilePayloadStoreStageDisposition::Progress,
                    std::move(content_sha256), total_size_bytes,
                    total_size_bytes, accepted_range_bytes, 0U, 0U};
            }

            TerminalVerificationStateFileObservation verification =
                observe_terminal_verification(&prefix.status);

            if (!verification.present) {
                // The continuation is one additional transient namespace entry.
                // Reserve it from a complete writer-fenced scan before the
                // first write-ahead state is made visible. Once present,
                // malformed or stale records are replaced in place and consume
                // no new namespace capacity.
                const ScannedPayloadIndex state_admission =
                    scan("terminal-verification state admission");
                verification = observe_terminal_verification(&prefix.status);
                if (!verification.present &&
                    state_admission.terminal_verification_entry_count >=
                        store.limits.max_transient_entries) {
                    throw std::length_error(
                        store.label +
                        " cannot admit one terminal-verification continuation");
                }
            }

            if (!verification.usable) {
                SyncReplicaFilePayloadTerminalVerificationState prepared{
                    sha256_hex(store.expected_identity),
                    identity_metadata,
                    1U,
                    content_sha256,
                    total_size_bytes,
                    sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
                        prefix.status,
                        SyncPosixDescriptorLinkPolicy::exactly_one,
                        store.label +
                            " staged-prefix verification payload"),
                    0U,
                    ResumableSha256{}.checkpoint()};
                prepared.generation =
                    next_terminal_verification_generation_or_throw(
                        verification,
                        store.label + " staged-prefix verification reset");
                verification = publish_terminal_verification(
                    prepared, verification, prefix.status);
            }
            if (!verification.journal.has_value()) {
                throw std::logic_error(
                    store.label +
                    " usable staged-prefix verification lacks parsed state");
            }

            SyncReplicaFilePayloadTerminalVerificationState working =
                verification.journal->latest_state;
            ResumableSha256 running(
                working.hash,
                store.label + " staged-prefix verification checkpoint");
            const std::uint64_t remaining =
                total_size_bytes - working.verified_offset_bytes;
            const std::uint64_t step_bytes = std::min<std::uint64_t>(
                remaining,
                kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep);
            constexpr std::uint64_t terminal_verification_steps = 1U;
            std::array<char, kStreamingBufferBytes> verification_buffer{};
            std::uint64_t consumed = 0U;
            while (consumed < step_bytes) {
                const std::uint64_t step_remaining = step_bytes - consumed;
                const std::size_t requested = static_cast<std::size_t>(
                    std::min<std::uint64_t>(
                        step_remaining, verification_buffer.size()));
                const std::uint64_t absolute_offset = checked_add_u64_or_throw(
                    working.verified_offset_bytes, consumed,
                    store.label + " staged-prefix verification read offset");
                ssize_t read_count;
                do {
                    read_count = ::pread(
                        prefix_file.get(), verification_buffer.data(), requested,
                        static_cast<off_t>(absolute_offset));
                } while (read_count < 0 && errno == EINTR);
                if (read_count < 0) {
                    const int error = errno;
                    throw std::runtime_error(
                        store.label +
                        " staged-prefix verification read failed: " +
                        error_text(error));
                }
                if (read_count == 0) {
                    throw PayloadStoreObservationStaleError(
                        store.label +
                        " completed staged prefix became truncated while verified");
                }
                const std::uint64_t received =
                    static_cast<std::uint64_t>(read_count);
                if (received > step_remaining) {
                    throw std::runtime_error(
                        store.label +
                        " staged-prefix verification read crossed its bounded step");
                }
                running.update(std::string_view(
                    verification_buffer.data(),
                    static_cast<std::size_t>(read_count)));
                consumed += received;
            }

            struct stat verified_prefix_status{};
            if (::fstat(prefix_file.get(), &verified_prefix_status) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    store.label +
                    " staged-prefix verification final fstat failed: " +
                    error_text(error));
            }
            if (!same_regular_file_observation(
                    prefix.status, verified_prefix_status)) {
                throw PayloadStoreObservationStaleError(
                    store.label +
                    " completed staged prefix changed while terminal verification advanced");
            }
            verify_named_regular_file_or_throw(
                root_descriptor.get(), prefix.basename,
                verified_prefix_status, root_attestation,
                store.label +
                    " completed staged-prefix verification final name proof");
            mutation_lease.verify_or_throw(
                store.root_authority,
                store.label +
                    " completed staged-prefix verification read lease cutpoint");

            const std::uint64_t verified_offset = checked_add_u64_or_throw(
                working.verified_offset_bytes, consumed,
                store.label + " staged-prefix verified offset");
            if (verified_offset < total_size_bytes) {
                working.generation =
                    next_terminal_verification_generation_or_throw(
                        verification,
                        store.label + " staged-prefix verification progress");
                working.verified_offset_bytes = verified_offset;
                working.hash = running.checkpoint();
                (void)publish_terminal_verification(
                    working, verification, prefix.status);
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " staged-prefix verification progress final lease cutpoint");
                note_terminal_work(verified_offset);
                return SyncReplicaFilePayloadStoreStageResult{
                    SyncReplicaFilePayloadStoreStageDisposition::Progress,
                    std::move(content_sha256), total_size_bytes,
                    total_size_bytes, accepted_range_bytes,
                    terminal_verification_steps, verified_offset};
            }
            if (verified_offset != total_size_bytes) {
                throw std::logic_error(
                    store.label +
                    " staged-prefix verification crossed its exact total size");
            }

            const std::string completed_sha256 = running.finish_hex();
            if (completed_sha256 != content_sha256) {
                if (verification.present) {
                    unlink_scanned_private_file_or_throw(
                        root_descriptor.get(),
                        terminal_verification_basename_or_throw(content_sha256),
                        verification.status, root_attestation,
                        store.label +
                            " invalid staged-prefix verification-state cleanup");
                }
                unlink_scanned_private_file_or_throw(
                    root_descriptor.get(), prefix.basename, prefix.status,
                    root_attestation,
                    store.label + " invalid completed staged prefix cleanup");
                fsync_or_throw(
                    root_descriptor.get(),
                    store.label +
                        " invalid completed staged prefix cleanup directory");
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " invalid completed staged prefix lease cutpoint");
                note_terminal_complete();
                throw std::runtime_error(
                    store.label +
                    " completed staged prefix failed whole-file verification");
            }

            ScannedPayloadIndex final_scan = scan("final publication preflight");
            if (!final_scan.publication_residues.empty()) {
                remove_scanned_publication_residues_or_throw(
                    store.root_authority, final_scan.publication_residues,
                    store.label +
                        " final staged-prefix publication-residue cleanup");
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " final staged-prefix residue cleanup lease cutpoint");
                final_scan = scan("post-final-residue cleanup");
            }

            const PayloadIndexEntry* durable =
                find_entry(final_scan.entries, content_sha256);
            if (durable != nullptr) {
                if (durable->size_bytes != total_size_bytes) {
                    throw std::runtime_error(
                        store.label +
                        " durable payload size conflicts at staged-prefix completion");
                }
                remove_matching_transients(final_scan, true);
                mutation_lease.verify_or_throw(
                    store.root_authority,
                    store.label +
                        " reconciled staged prefix final lease cutpoint");
                note_terminal_complete();
                return SyncReplicaFilePayloadStoreStageResult{
                    SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedAlreadyPresent,
                    std::move(content_sha256), total_size_bytes,
                    total_size_bytes, accepted_range_bytes,
                    terminal_verification_steps, total_size_bytes};
            }

            const StagedPrefixEntry* final_prefix =
                staged_prefix_for_content_or_none(
                    final_scan, content_sha256);
            if (final_prefix == nullptr ||
                final_prefix->basename != prefix.basename ||
                final_prefix->total_size_bytes != total_size_bytes ||
                final_prefix->committed_prefix_bytes != total_size_bytes ||
                final_prefix->actual_size_bytes != total_size_bytes ||
                !same_regular_file_observation(
                    final_prefix->status, prefix.status)) {
                throw std::runtime_error(
                    store.label +
                    " completed staged prefix changed before publication");
            }
            if (final_scan.entries.size() >= store.limits.max_entries ||
                final_scan.indexed_bytes > store.limits.max_indexed_bytes ||
                total_size_bytes >
                    store.limits.max_indexed_bytes -
                        final_scan.indexed_bytes) {
                throw std::length_error(
                    store.label +
                    " cannot admit the completed staged prefix payload");
            }

            verify_named_regular_file_or_throw(
                root_descriptor.get(), prefix.basename, prefix.status,
                root_attestation,
                store.label + " completed staged prefix pre-publication");
            mutation_lease.verify_or_throw(
                store.root_authority,
                store.label +
                    " staged prefix pre-publication lease cutpoint");
            rename_noreplace_at_or_throw(
                root_descriptor.get(), prefix.basename, content_sha256,
                store.label + " staged prefix direct publication");
            fsync_or_throw(
                root_descriptor.get(),
                store.label + " staged prefix publication directory");
            struct stat published_prefix_status{};
            if (::fstat(prefix_file.get(), &published_prefix_status) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    store.label + " published staged prefix fstat failed: " +
                    error_text(error));
            }
            require_private_regular_file_or_throw(
                published_prefix_status, root_attestation,
                store.label + " published staged prefix payload");
            if (!same_regular_file_rename_transition(
                    prefix.status, published_prefix_status)) {
                throw std::runtime_error(
                    store.label +
                    " staged prefix changed across direct publication");
            }
            verify_named_regular_file_or_throw(
                root_descriptor.get(), content_sha256,
                published_prefix_status, root_attestation,
                store.label + " published staged prefix payload");

            // The current prefix name has already become the durable digest
            // name. Only rev0941 compatibility residues from the same content
            // identity are removed from the pre-publication scan.
            remove_matching_transients(final_scan, false);
            mutation_lease.verify_or_throw(
                store.root_authority,
                store.label +
                    " staged prefix completion final lease cutpoint");
            insert_payload_index_entry_or_throw(
                final_scan,
                PayloadIndexEntry{
                    content_sha256, total_size_bytes,
                    published_prefix_status},
                store.limits,
                store.label + " completed staged prefix index update");
            retain_completed_payload_verification_best_effort(
                store.root_authority, store.limits,
                store.expected_identity, mutation_lease,
                store.verification_cache, final_scan, total_size_bytes,
                store.label + " completed staged prefix");
            note_terminal_complete();
            return SyncReplicaFilePayloadStoreStageResult{
                SyncReplicaFilePayloadStoreStageDisposition::CompletedInserted,
                std::move(content_sha256), total_size_bytes,
                total_size_bytes, accepted_range_bytes,
                terminal_verification_steps, total_size_bytes};
        }
    }

    if (delegate_to_legacy_range_owner) {
        note_terminal_complete();
        return stage_payload_range_or_throw(
            std::move(content_sha256), total_size_bytes, offset_bytes,
            std::move(chunk_sha256), std::string(bytes));
    }
    throw std::logic_error(
        "staged payload prefix did not select a receiver owner");
}

SyncReplicaFilePayloadStoreStageResult
SyncReplicaFilePayloadStore::
continue_staged_payload_prefix_verification_or_throw(
    std::string content_sha256,
    std::uint64_t total_size_bytes) {
    return stage_payload_prefix_impl_or_throw(
        std::move(content_sha256), total_size_bytes, total_size_bytes,

        std::string{}, std::string_view{}, true, false);
}
}  // namespace anonsync

#endif
