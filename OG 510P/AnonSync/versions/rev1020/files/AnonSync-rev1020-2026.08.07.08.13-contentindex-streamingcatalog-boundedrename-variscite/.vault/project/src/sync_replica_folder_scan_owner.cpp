#include "sync_replica_folder_scan_owner.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_directory_authority_internal.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_posix_directory_resolution.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

#include <sqlite3.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

// One canonical physical-content key and root-mask vocabulary is shared by
// historical reachability accounting and the deletion-free retention planner.
// Keeping this definition here prevents two independently evolving judgments
// about whether one exact (digest, size) object is current, historical, pinned,
// or merely physically present.
struct HistoricalPayloadReferenceKey final {
    std::string_view content_sha256;
    std::uint64_t size_bytes = 0U;
};

struct HistoricalPayloadReferenceKeyLess final {
    [[nodiscard]] bool operator()(
        const HistoricalPayloadReferenceKey& left,
        const HistoricalPayloadReferenceKey& right) const noexcept {
        if (left.content_sha256 != right.content_sha256) {
            return left.content_sha256 < right.content_sha256;
        }
        return left.size_bytes < right.size_bytes;
    }
};

[[nodiscard]] constexpr bool historical_payload_reference_key_equal(
    const HistoricalPayloadReferenceKey& left,
    const HistoricalPayloadReferenceKey& right) noexcept {
    return left.content_sha256 == right.content_sha256 &&
           left.size_bytes == right.size_bytes;
}

// The retention planner first records borrowed references without allocating
// one tree node per key. It then sorts, folds duplicate roots in place, and
// linearly merges this projection with the canonical physical inventory.
// string_view remains valid because the restored model owns every operation
// for the complete duration of the plan.
struct HistoricalPayloadReferenceProjectionEntry final {
    HistoricalPayloadReferenceKey key;
    std::uint8_t root_mask = 0U;
};

constexpr std::uint8_t kHistoricalPayloadCurrentVisibleMask = 1U;
constexpr std::uint8_t kHistoricalPayloadSupersededActiveMask = 2U;
constexpr std::uint8_t kHistoricalPayloadInactiveEvidenceMask = 4U;
constexpr std::uint8_t kHistoricalPayloadExplicitPinMask = 8U;

constexpr std::string_view
    kRetentionPlanUnreferencedCandidateSetDigestDomain =
        "anonsync:sync-replica-retention-plan-unreferenced-candidates:v1";
constexpr std::string_view kRetentionPlanDurableCandidateWitnessDigestDomain =
    "anonsync:sync-replica-retention-plan-durable-candidate-witness:v2";
constexpr std::string_view kRetentionPlanDeletionFreeMarkDigestDomain =
    "anonsync:sync-replica-retention-plan-deletion-free-mark:v5";
constexpr std::string_view kRetentionPlanWriterFencedCandidatePageDigestDomain =
    "anonsync:sync-replica-retention-plan-writer-fenced-candidate-page:v2";

[[nodiscard]] constexpr bool historical_payload_mask_has(
    std::uint8_t mask,
    std::uint8_t value) noexcept {
    return (mask & value) != 0U;
}

[[nodiscard]] constexpr SyncReplicaRetentionPlanDisposition
retention_plan_disposition_from_root_mask(std::uint8_t mask) noexcept {
    if (historical_payload_mask_has(
            mask, kHistoricalPayloadCurrentVisibleMask) ||
        historical_payload_mask_has(
            mask, kHistoricalPayloadExplicitPinMask)) {
        return SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin;
    }
    if (historical_payload_mask_has(
            mask, kHistoricalPayloadSupersededActiveMask) ||
        historical_payload_mask_has(
            mask, kHistoricalPayloadInactiveEvidenceMask)) {
        return SyncReplicaRetentionPlanDisposition::RetainedHistoryOrEvidence;
    }
    return SyncReplicaRetentionPlanDisposition::UnreferencedByRetainedFileOperations;
}

constexpr std::uint64_t kLegacySchemaVersion = 1U;
constexpr std::uint64_t kPreviousSchemaVersion = 2U;
constexpr std::uint64_t kFairScanSchemaVersion = 3U;
constexpr std::uint64_t kCyclicSchemaVersion = 4U;
constexpr std::uint64_t kPreselectionSchemaVersion = 5U;
constexpr std::uint64_t kSelectiveSyncSchemaVersion = 6U;
constexpr std::uint64_t kSchemaVersion = 7U;
constexpr std::uint64_t kMaxPersistentInteger =
    static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());
constexpr std::string_view kLegacyCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v1";
constexpr std::string_view kPreviousCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v2";
constexpr std::string_view kFairScanCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v3";
constexpr std::string_view kCyclicCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v4";
constexpr std::string_view kPreselectionCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v5";
constexpr std::string_view kSelectiveSyncCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v6";
constexpr std::string_view kCatalogDigestDomain =
    "anonsync:sync-replica-folder-catalog:v7";
constexpr std::string_view kRemoteInspectionSweepBasisDigestDomain =
    "anonsync:sync-replica-folder-remote-inspection-sweep-basis:v1";
constexpr std::string_view kFolderScanSeenChainDigestDomain =
    "anonsync:sync-replica-folder-scan-seen-chain:v1";
constexpr std::string_view kSourceSnapshotDigestDomain =
    "anonsync:sync-replica-folder-source-snapshot:v1";

constexpr std::string_view kPreselectionMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=5),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kSelectiveSyncMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=6),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "content_catalog_digest TEXT NOT NULL CHECK(length(content_catalog_digest)=64),"
    "selection_generation INTEGER NOT NULL CHECK(selection_generation>0),"
    "selection_absence_fence_generation INTEGER NOT NULL "
    "CHECK(selection_absence_fence_generation=0 OR "
    "selection_absence_fence_generation=selection_generation),"
    "selection_default_mode INTEGER NOT NULL CHECK(selection_default_mode IN (1,2)),"
    "selection_rule_count INTEGER NOT NULL CHECK(selection_rule_count BETWEEN 0 AND 1024),"
    "selection_rule_path_bytes INTEGER NOT NULL CHECK(selection_rule_path_bytes BETWEEN 0 AND 49152),"
    "selection_digest TEXT NOT NULL CHECK(length(selection_digest)=64),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=7),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "content_catalog_digest TEXT NOT NULL CHECK(length(content_catalog_digest)=64),"
    "selection_generation INTEGER NOT NULL CHECK(selection_generation>0),"
    "selection_absence_fence_generation INTEGER NOT NULL "
    "CHECK(selection_absence_fence_generation=0 OR "
    "selection_absence_fence_generation=selection_generation),"
    "selection_default_mode INTEGER NOT NULL CHECK(selection_default_mode IN (1,2)),"
    "selection_rule_count INTEGER NOT NULL CHECK(selection_rule_count BETWEEN 0 AND 1024),"
    "selection_rule_path_bytes INTEGER NOT NULL CHECK(selection_rule_path_bytes BETWEEN 0 AND 49152),"
    "selection_digest TEXT NOT NULL CHECK(length(selection_digest)=64),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kSelectionRulesSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_selection_rules("
    "canonical_path TEXT PRIMARY KEY CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
    "selection_mode INTEGER NOT NULL CHECK(selection_mode IN (1,2))) STRICT";

constexpr std::string_view kEntriesSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_entries("
    "canonical_path TEXT PRIMARY KEY CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
    "value_kind INTEGER NOT NULL CHECK(value_kind IN (1,2)),"
    "size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),"
    "content_sha256 TEXT NOT NULL,"
    "operation_id TEXT NOT NULL CHECK(length(operation_id)=64),"
    "source_snapshot_sha256 TEXT NOT NULL,"
    "last_seen_generation INTEGER NOT NULL CHECK(last_seen_generation>0),"
    "CHECK((value_kind=1 AND length(content_sha256)=64 AND "
    "length(source_snapshot_sha256)=64) OR (value_kind=2 AND size_bytes=0 AND "
    "content_sha256='' AND source_snapshot_sha256=''))) STRICT";

constexpr std::string_view kEntriesFileContentIndexSchemaSql =
    "CREATE INDEX sync_replica_folder_catalog_file_content ON "
    "sync_replica_folder_catalog_entries("
    "value_kind,content_sha256,size_bytes,canonical_path,operation_id)";

constexpr std::string_view kScanProgressSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_scan_progress("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "scan_epoch INTEGER NOT NULL CHECK(scan_epoch>0),"
    "resume_after_path TEXT NOT NULL CHECK(length(resume_after_path)<=4096),"
    "seen_path_count INTEGER NOT NULL CHECK(seen_path_count>=0),"
    "seen_path_bytes INTEGER NOT NULL CHECK(seen_path_bytes>=0),"
    "seen_chain_digest TEXT NOT NULL CHECK(length(seen_chain_digest)=64)) STRICT";

constexpr std::string_view kScanSeenSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_scan_seen("
    "ordinal INTEGER PRIMARY KEY CHECK(ordinal>0),"
    "scan_epoch INTEGER NOT NULL CHECK(scan_epoch>0),"
    "canonical_path TEXT NOT NULL UNIQUE CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
    "chain_digest TEXT NOT NULL CHECK(length(chain_digest)=64)) STRICT";

constexpr std::string_view kRemoteApplyProgressSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_remote_apply_progress("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "resume_after_path TEXT NOT NULL CHECK(length(resume_after_path)<=4096),"
    "inspection_sweep_basis_digest TEXT NOT NULL "
    "CHECK(length(inspection_sweep_basis_digest) IN (0,64)),"
    "inspection_sweep_started_after_path TEXT NOT NULL "
    "CHECK(length(inspection_sweep_started_after_path)<=4096),"
    "inspection_sweep_seen_path_count INTEGER NOT NULL "
    "CHECK(inspection_sweep_seen_path_count>=0),"
    "inspection_sweep_had_unresolved_paths INTEGER NOT NULL "
    "CHECK(inspection_sweep_had_unresolved_paths IN (0,1)),"
    "CHECK((inspection_sweep_basis_digest='' AND "
    "inspection_sweep_started_after_path='' AND "
    "inspection_sweep_seen_path_count=0 AND "
    "inspection_sweep_had_unresolved_paths=0) OR "
    "(length(inspection_sweep_basis_digest)=64 AND "
    "inspection_sweep_seen_path_count>0))) STRICT";

// Exact rev0951 cyclic remote-work definitions. They are accepted only long
// enough to prove the complete v4 catalog, authenticated local scan journal,
// and path cursor; then the cursor is retained while the new cutpoint-bound
// inspection sweep starts at genesis under the v5 digest domain.
constexpr std::string_view kCyclicMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=4),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kCyclicRemoteApplyProgressSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_remote_apply_progress("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "resume_after_path TEXT NOT NULL CHECK(length(resume_after_path)<=4096)) STRICT";

// Exact rev0950 durable fair-scan definitions. They are accepted only long
// enough to prove the complete v3 catalog and authenticated scan journal, add
// the independent remote scheduling cursor, and advance the catalog digest
// domain transactionally. The rooted scan journal is copied nowhere and loses
// no continuation state during this migration.
constexpr std::string_view kFairScanMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=3),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

// Exact rev0946 file/tombstone catalog definitions. They are accepted only
// long enough to prove the complete v2 cutpoint, add the authenticated scan
// journal plus independent remote scheduling cursor, and migrate directly to
// the current v5 digest domain transactionally.
constexpr std::string_view kPreviousMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=2),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kPreviousEntriesSchemaSql = kEntriesSchemaSql;

// Exact rev0939 file-only catalog definitions. They are accepted only long
// enough to prove the complete old cutpoint and migrate it transactionally to
// v4. A near-match is neither repaired nor partially adopted.
constexpr std::string_view kLegacyMetaSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=1),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
    "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
    "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
    "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT";

constexpr std::string_view kLegacyEntriesSchemaSql =
    "CREATE TABLE sync_replica_folder_catalog_entries("
    "canonical_path TEXT PRIMARY KEY CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
    "size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),"
    "content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),"
    "operation_id TEXT NOT NULL CHECK(length(operation_id)=64),"
    "source_snapshot_sha256 TEXT NOT NULL CHECK(length(source_snapshot_sha256)=64),"
    "last_seen_generation INTEGER NOT NULL CHECK(last_seen_generation>0)) STRICT";

struct SchemaDefinition final {
    std::string_view name;
    std::string_view sql;
};

constexpr std::array<SchemaDefinition, 7U> kSchema{{
    {"sync_replica_folder_catalog_meta", kMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kEntriesSchemaSql},
    {"sync_replica_folder_catalog_scan_progress", kScanProgressSchemaSql},
    {"sync_replica_folder_catalog_scan_seen", kScanSeenSchemaSql},
    {"sync_replica_folder_catalog_remote_apply_progress",
     kRemoteApplyProgressSchemaSql},
    {"sync_replica_folder_catalog_selection_rules",
     kSelectionRulesSchemaSql},
    {"sync_replica_folder_catalog_file_content",
     kEntriesFileContentIndexSchemaSql},
}};

constexpr std::array<SchemaDefinition, 6U> kSelectiveSyncSchema{{
    {"sync_replica_folder_catalog_meta", kSelectiveSyncMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kEntriesSchemaSql},
    {"sync_replica_folder_catalog_scan_progress", kScanProgressSchemaSql},
    {"sync_replica_folder_catalog_scan_seen", kScanSeenSchemaSql},
    {"sync_replica_folder_catalog_remote_apply_progress",
     kRemoteApplyProgressSchemaSql},
    {"sync_replica_folder_catalog_selection_rules",
     kSelectionRulesSchemaSql},
}};

constexpr std::array<SchemaDefinition, 5U> kPreselectionSchema{{
    {"sync_replica_folder_catalog_meta", kPreselectionMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kEntriesSchemaSql},
    {"sync_replica_folder_catalog_scan_progress", kScanProgressSchemaSql},
    {"sync_replica_folder_catalog_scan_seen", kScanSeenSchemaSql},
    {"sync_replica_folder_catalog_remote_apply_progress",
     kRemoteApplyProgressSchemaSql},
}};

constexpr std::array<SchemaDefinition, 5U> kCyclicSchema{{
    {"sync_replica_folder_catalog_meta", kCyclicMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kEntriesSchemaSql},
    {"sync_replica_folder_catalog_scan_progress", kScanProgressSchemaSql},
    {"sync_replica_folder_catalog_scan_seen", kScanSeenSchemaSql},
    {"sync_replica_folder_catalog_remote_apply_progress",
     kCyclicRemoteApplyProgressSchemaSql},
}};

constexpr std::array<SchemaDefinition, 4U> kFairScanSchema{{
    {"sync_replica_folder_catalog_meta", kFairScanMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kEntriesSchemaSql},
    {"sync_replica_folder_catalog_scan_progress", kScanProgressSchemaSql},
    {"sync_replica_folder_catalog_scan_seen", kScanSeenSchemaSql},
}};

constexpr std::array<SchemaDefinition, 2U> kPreviousSchema{{
    {"sync_replica_folder_catalog_meta", kPreviousMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kPreviousEntriesSchemaSql},
}};

constexpr std::array<SchemaDefinition, 2U> kLegacySchema{{
    {"sync_replica_folder_catalog_meta", kLegacyMetaSchemaSql},
    {"sync_replica_folder_catalog_entries", kLegacyEntriesSchemaSql},
}};

class ScopedFd final {
public:
    explicit ScopedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~ScopedFd() noexcept { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept
        : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

private:
    int descriptor_ = -1;
};

void append_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    std::array<char, 8U> encoded{};
    for (std::size_t index = encoded.size(); index != 0U; --index) {
        encoded[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(std::string_view(encoded.data(), encoded.size()));
}

void append_i64(Sha256DigestBuilder& digest, std::int64_t value) {
    append_u64(digest, static_cast<std::uint64_t>(value));
}

void append_string(Sha256DigestBuilder& digest, std::string_view value) {
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

[[nodiscard]] std::uint64_t catalog_value_kind_integer_or_throw(
    SyncReplicaValueKind kind,
    std::string_view label) {
    switch (kind) {
        case SyncReplicaValueKind::File:
            return 1U;
        case SyncReplicaValueKind::Tombstone:
            return 2U;
    }
    throw std::invalid_argument(
        std::string(label) + " catalog value kind is invalid");
}

[[nodiscard]] SyncReplicaValueKind catalog_value_kind_from_integer_or_throw(
    std::uint64_t value,
    std::string_view label) {
    switch (value) {
        case 1U:
            return SyncReplicaValueKind::File;
        case 2U:
            return SyncReplicaValueKind::Tombstone;
        default:
            throw std::runtime_error(
                std::string(label) + " catalog value kind is invalid");
    }
}

[[nodiscard]] std::uint64_t add_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    std::string_view label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(std::string(label) + " overflowed");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t increment_or_throw(
    std::uint64_t value,
    std::string_view label) {
    const std::uint64_t out = add_or_throw(value, 1U, label);
    if (out > kMaxPersistentInteger) {
        throw std::overflow_error(
            std::string(label) + " exceeded SQLite integer range");
    }
    return out;
}

[[nodiscard]] int step_row_or_done_or_throw(
    sqlite3_stmt* statement,
    const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW && result != SQLITE_DONE) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement), result, label);
    }
    return result;
}

[[nodiscard]] std::vector<std::string> split_canonical_path(
    std::string_view canonical_path) {
    std::vector<std::string> components;
    std::size_t begin = 0U;
    for (std::size_t index = 0U; index <= canonical_path.size(); ++index) {
        if (index != canonical_path.size() && canonical_path[index] != '/') {
            continue;
        }
        components.emplace_back(
            canonical_path.substr(begin, index - begin));
        begin = index + 1U;
    }
    return components;
}

void reject_reserved_internal_path_components_or_throw(
    std::string_view canonical_path,
    const std::string& label) {
    for (const std::string& component : split_canonical_path(canonical_path)) {
        if (sync_atomic_file_publication_temp_basename_is_exact(component)) {
            throw std::invalid_argument(
                label +
                " path uses AnonSync's reserved atomic-publication namespace");
        }
    }
}

void validate_canonical_path_for_root_or_throw(
    std::string_view canonical_path,
    const SyncDirectoryAuthority& root,
    const std::string& label) {
    const SyncValidationResult canonical =
        validate_sync_relative_path(canonical_path);
    if (!canonical.ok) {
        throw std::invalid_argument(
            label + " path is not canonical: " + canonical.reason);
    }
    reject_reserved_internal_path_components_or_throw(
        canonical_path, label);
    const std::uint64_t name_maximum =
        root.attestation().filesystem_name_maximum;
    if (name_maximum == 0U) {
        throw std::runtime_error(
            label + " root has no usable filename-component limit");
    }
    const SyncValidationResult local =
        validate_sync_relative_path_component_byte_limit(
            canonical_path, name_maximum);
    if (!local.ok) {
        throw std::invalid_argument(
            label + " path is not representable under the root: " +
            local.reason);
    }
}

struct ResolvedRelativeParent final {
    ScopedFd descriptor;
    std::string basename;
    fs::path display_path;
    SyncPosixDirectoryResolutionCapability capability =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity mount_identity;
};

[[nodiscard]] std::optional<ResolvedRelativeParent>
resolve_optional_relative_parent_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;

    root.verify_or_throw(label + " root before traversal");
    auto lease = Access::duplicate_shared_open_description_or_throw(
        root, label + " root traversal");
    const SyncPosixDirectoryResolutionCapability capability =
        lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity = lease.mount_identity();
    ScopedFd current(lease.release_descriptor());
    const std::vector<std::string> components =
        split_canonical_path(canonical_path);
    fs::path display = root.path();

    for (std::size_t index = 0U; index + 1U < components.size(); ++index) {
        display /= components[index];
        std::optional<SyncPosixOpenedDirectory> opened =
            sync_posix_open_optional_directory_component_or_throw(
                current.get(), components[index], display,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                capability, mount_identity, label);
        if (!opened.has_value()) {
            root.verify_or_throw(label + " root after absent traversal");
            return std::nullopt;
        }
        current.reset(opened->descriptor);
    }

    display /= components.back();
    root.verify_or_throw(label + " root after parent traversal");
    return ResolvedRelativeParent{
        std::move(current), components.back(), std::move(display),
        capability, mount_identity};
}

[[nodiscard]] ResolvedRelativeParent
resolve_relative_parent_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    std::optional<ResolvedRelativeParent> parent =
        resolve_optional_relative_parent_beneath_root_or_throw(
            root, canonical_path, label);
    if (!parent.has_value()) {
        throw std::runtime_error(label + " parent path is absent");
    }
    return std::move(*parent);
}

[[nodiscard]] std::optional<ScopedFd>
open_optional_regular_file_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    std::optional<ResolvedRelativeParent> parent =
        resolve_optional_relative_parent_beneath_root_or_throw(
            root, canonical_path, label);
    if (!parent.has_value()) return std::nullopt;
    struct stat status {};
    if (::fstatat(parent->descriptor.get(), parent->basename.c_str(), &status,
                  AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        if (error == ENOENT) {
            root.verify_or_throw(label + " root after absent inspection");
            return std::nullopt;
        }
        throw std::runtime_error(
            label + " final path inspection failed: " +
            std::strerror(error));
    }
    if (S_ISLNK(status.st_mode)) {
        throw std::runtime_error(label + " final path must not be a symlink");
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(
            label + " final path must be absent or a regular file");
    }

    SyncPosixOpenedRegularFile opened =
        sync_posix_open_regular_file_component_or_throw(
            parent->descriptor.get(), parent->basename, parent->display_path,
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            parent->capability, parent->mount_identity, label);
    ScopedFd file(opened.descriptor);
    root.verify_or_throw(label + " root after traversal");
    return std::optional<ScopedFd>(std::move(file));
}

[[nodiscard]] ScopedFd open_regular_file_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    std::optional<ScopedFd> file =
        open_optional_regular_file_beneath_root_or_throw(
            root, canonical_path, label);
    if (!file.has_value()) {
        throw std::runtime_error(label + " regular file is absent");
    }
    return std::move(*file);
}

[[nodiscard]] std::string source_snapshot_digest(
    std::string_view root_attestation_digest,
    std::string_view canonical_path,
    const SyncPosixRegularFileSnapshotMetadata& observation,
    std::string_view content_sha256) {
    Sha256DigestBuilder digest;
    append_string(digest, kSourceSnapshotDigestDomain);
    append_string(digest, root_attestation_digest);
    append_string(digest, canonical_path);
    append_u64(digest, observation.device);
    append_u64(digest, observation.inode);
    append_u64(digest, observation.link_count);
    append_u64(digest, observation.size_bytes);
    append_u64(digest, observation.owner_user_id);
    append_u64(digest, observation.owner_group_id);
    append_u64(digest, observation.mode);
    append_i64(digest, observation.modification_seconds);
    append_u64(digest, observation.modification_nanoseconds);
    append_i64(digest, observation.status_change_seconds);
    append_u64(digest, observation.status_change_nanoseconds);
    append_string(digest, content_sha256);
    return digest.finish_hex();
}

struct StableRegularFileObservation final {
    ScopedFd descriptor;
    SyncPosixRegularFileSnapshotMetadata metadata;
    std::string content_sha256;
    std::string source_snapshot_sha256;
};

[[nodiscard]] std::optional<StableRegularFileObservation>
observe_optional_regular_file_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view root_attestation_digest,
    std::string_view canonical_path,
    std::uint64_t maximum_bytes,
    const std::string& label) {
    std::optional<ScopedFd> file =
        open_optional_regular_file_beneath_root_or_throw(
            root, canonical_path, label + " file");
    if (!file.has_value()) return std::nullopt;

    const SyncPosixRegularFileDigestObservation digest_observation =
        hash_sync_posix_regular_file_descriptor_or_throw(
            file->get(), maximum_bytes,
            SyncPosixDescriptorLinkPolicy::stable_named_object,
            label + " streaming snapshot");
    const SyncPosixRegularFileSnapshotMetadata metadata =
        digest_observation.metadata;
    const std::string& content_sha256 =
        digest_observation.content_sha256;

    // The retained descriptor proves one stable object; this second open binds
    // that object back to the configured root-relative pathname after the byte
    // read and hash.
    ScopedFd named = open_regular_file_beneath_root_or_throw(
        root, canonical_path, label + " pathname reproof");
    const SyncPosixRegularFileSnapshotMetadata named_metadata =
        observe_sync_posix_regular_file_descriptor_or_throw(
            named.get(), SyncPosixDescriptorLinkPolicy::stable_named_object,
            label + " pathname reproof");
    if (named_metadata != metadata) {
        throw std::runtime_error(
            label + " pathname changed after its stable byte observation");
    }

    return StableRegularFileObservation{
        std::move(*file), metadata, digest_observation.content_sha256,
        source_snapshot_digest(
            root_attestation_digest, canonical_path, metadata,
            content_sha256)};
}

void fsync_descriptor_or_throw(
    int descriptor,
    const std::string& label) {
    for (;;) {
        if (::fsync(descriptor) == 0) return;
        const int error = errno;
        if (error == EINTR) continue;
        throw std::runtime_error(
            label + " fsync failed: " + std::strerror(error));
    }
}

void ensure_relative_parent_beneath_root_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;

    root.verify_or_throw(label + " root before parent creation");
    auto lease = Access::duplicate_shared_open_description_or_throw(
        root, label + " root parent creation");
    const SyncPosixDirectoryResolutionCapability capability =
        lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity = lease.mount_identity();
    ScopedFd current(lease.release_descriptor());
    const std::vector<std::string> components =
        split_canonical_path(canonical_path);
    fs::path display = root.path();

    for (std::size_t index = 0U; index + 1U < components.size(); ++index) {
        display /= components[index];
        std::optional<SyncPosixOpenedDirectory> opened =
            sync_posix_open_optional_directory_component_or_throw(
                current.get(), components[index], display,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                capability, mount_identity, label);
        if (!opened.has_value()) {
            int create_result;
            do {
                create_result = ::mkdirat(
                    current.get(), components[index].c_str(), 0700);
            } while (create_result != 0 && errno == EINTR);
            const int create_error = create_result == 0 ? 0 : errno;
            if (create_result != 0 && create_error != EEXIST) {
                throw std::runtime_error(
                    label + " could not create parent directory " +
                    display.generic_string() + ": " +
                    std::strerror(create_error));
            }

            opened = sync_posix_open_optional_directory_component_or_throw(
                current.get(), components[index], display,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                capability, mount_identity, label);
            if (!opened.has_value()) {
                throw std::runtime_error(
                    label + " parent directory disappeared during creation: " +
                    display.generic_string());
            }
            if (create_result == 0) {
                // Persist each newly linked directory before descending. The
                // final file publication synchronizes its immediate parent;
                // these barriers cover the previously absent ancestors.
                fsync_descriptor_or_throw(
                    current.get(), label + " created-parent namespace");
            }
        }
        current.reset(opened->descriptor);
    }

    root.verify_or_throw(label + " root after parent creation");
}

void synchronize_regular_file_descriptor_and_parent_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    int descriptor,
    const SyncPosixRegularFileSnapshotMetadata& observation,
    const std::string& label) {
    fsync_descriptor_or_throw(descriptor, label + " file");
    const SyncPosixRegularFileSnapshotMetadata retained =
        observe_sync_posix_regular_file_descriptor_or_throw(
            descriptor, SyncPosixDescriptorLinkPolicy::stable_named_object,
            label + " retained file");
    if (retained != observation) {
        throw std::runtime_error(label + " file changed during synchronization");
    }

    ResolvedRelativeParent parent =
        resolve_relative_parent_beneath_root_or_throw(
            root, canonical_path, label + " parent");
    struct stat named {};
    if (::fstatat(parent.descriptor.get(), parent.basename.c_str(), &named,
                  AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " pathname reproof failed: " + std::strerror(error));
    }
    if (!sync_posix_regular_file_snapshot_metadata_matches_status(
            observation, named)) {
        throw std::runtime_error(
            label + " pathname changed before directory synchronization");
    }
    fsync_descriptor_or_throw(
        parent.descriptor.get(), label + " parent directory");

    struct stat named_after {};
    if (::fstatat(parent.descriptor.get(), parent.basename.c_str(),
                  &named_after, AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " post-sync pathname reproof failed: " +
            std::strerror(error));
    }
    if (!sync_posix_regular_file_snapshot_metadata_matches_status(
            observation, named_after)) {
        throw std::runtime_error(
            label + " pathname changed during directory synchronization");
    }
    root.verify_or_throw(label + " root after synchronization");
}

void synchronize_observed_regular_file_and_parent_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const StableRegularFileObservation& observation,
    const std::string& label) {
    synchronize_regular_file_descriptor_and_parent_or_throw(
        root, canonical_path, observation.descriptor.get(),
        observation.metadata, label);
}

void synchronize_absent_path_parent_or_throw(
    const SyncDirectoryAuthority& root,
    std::string_view canonical_path,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;

    root.verify_or_throw(label + " root before absence synchronization");
    auto lease = Access::duplicate_shared_open_description_or_throw(
        root, label + " root absence synchronization");
    const SyncPosixDirectoryResolutionCapability capability =
        lease.resolution_capability();
    const SyncPosixMountIdentity mount_identity = lease.mount_identity();
    ScopedFd current(lease.release_descriptor());
    const std::vector<std::string> components =
        split_canonical_path(canonical_path);
    fs::path display = root.path();

    // If an intermediate directory is absent, the durable namespace fact is
    // the absence of that first missing component—not the unreachable final
    // basename. Synchronize the deepest retained parent and then prove the
    // component remained absent across that barrier. Merely verifying the root
    // descriptor would not persist a deletion beneath an existing ancestor.
    for (std::size_t index = 0U; index + 1U < components.size(); ++index) {
        display /= components[index];
        std::optional<SyncPosixOpenedDirectory> opened =
            sync_posix_open_optional_directory_component_or_throw(
                current.get(), components[index], display,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                capability, mount_identity,
                label + " absent-parent traversal");
        if (opened.has_value()) {
            current.reset(opened->descriptor);
            continue;
        }

        fsync_descriptor_or_throw(
            current.get(), label + " deepest existing parent directory");
        opened = sync_posix_open_optional_directory_component_or_throw(
            current.get(), components[index], display,
            SyncPosixDirectoryComponentRole::RootedDescendant,
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            capability, mount_identity,
            label + " absent-parent reproof");
        if (opened.has_value()) {
            throw std::runtime_error(
                label + " missing parent appeared during synchronization");
        }
        root.verify_or_throw(
            label + " root after missing-parent synchronization");
        return;
    }

    struct stat status {};
    if (::fstatat(current.get(), components.back().c_str(), &status,
                  AT_SYMLINK_NOFOLLOW) == 0) {
        throw std::runtime_error(
            label + " path is no longer absent before synchronization");
    }
    const int inspection_error = errno;
    if (inspection_error != ENOENT) {
        throw std::runtime_error(
            label + " absence inspection failed: " +
            std::strerror(inspection_error));
    }
    fsync_descriptor_or_throw(
        current.get(), label + " parent directory");

    if (::fstatat(current.get(), components.back().c_str(), &status,
                  AT_SYMLINK_NOFOLLOW) == 0) {
        throw std::runtime_error(
            label + " path appeared during absence synchronization");
    }
    const int reproof_error = errno;
    if (reproof_error != ENOENT) {
        throw std::runtime_error(
            label + " post-sync absence inspection failed: " +
            std::strerror(reproof_error));
    }
    root.verify_or_throw(label + " root after absence synchronization");
}

[[nodiscard]] std::string modern_catalog_digest(
    std::string_view digest_domain,
    std::uint64_t schema_version,
    std::string_view digest_label,
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    Sha256DigestBuilder digest;
    append_string(digest, digest_domain);
    append_u64(digest, schema_version);
    append_string(digest, folder_id);
    append_string(digest, absolute_root_path);
    append_string(digest, root_attestation_digest);
    append_u64(digest, limits.max_catalog_entries);
    append_u64(digest, limits.max_catalog_path_bytes);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, state_generation);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    for (const auto& entry : entries) {
        append_string(digest, entry.canonical_path);
        append_u64(
            digest,
            catalog_value_kind_integer_or_throw(
                entry.kind, digest_label));
        append_u64(digest, entry.size_bytes);
        append_string(digest, entry.content_sha256);
        append_string(digest, entry.operation_id);
        append_string(digest, entry.source_snapshot_sha256);
        append_u64(digest, entry.last_seen_generation);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string preselection_catalog_digest(
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    return modern_catalog_digest(
        kPreselectionCatalogDigestDomain, kPreselectionSchemaVersion,
        "preselection folder catalog digest", folder_id,
        absolute_root_path, root_attestation_digest, limits,
        state_generation, entries);
}

[[nodiscard]] std::string selective_catalog_digest(
    std::string_view domain,
    std::uint64_t schema_version,
    std::string_view content_catalog_digest,
    const SyncReplicaSelectiveSyncPolicy& policy) {
    if (!is_lowercase_sha256_hex(content_catalog_digest)) {
        throw std::invalid_argument(
            "folder catalog digest requires a canonical content digest");
    }
    validate_sync_replica_selective_sync_policy_or_throw(
        policy, "folder catalog selective-sync policy");
    Sha256DigestBuilder digest;
    append_string(digest, domain);
    append_u64(digest, schema_version);
    append_string(digest, content_catalog_digest);
    append_u64(digest, policy.generation);
    append_u64(
        digest, static_cast<std::uint64_t>(policy.default_mode));
    append_u64(digest, static_cast<std::uint64_t>(policy.rules.size()));
    append_u64(digest, policy.rule_path_bytes);
    append_string(digest, policy.policy_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string selective_sync_catalog_digest(
    std::string_view content_catalog_digest,
    const SyncReplicaSelectiveSyncPolicy& policy) {
    return selective_catalog_digest(
        kSelectiveSyncCatalogDigestDomain, kSelectiveSyncSchemaVersion,
        content_catalog_digest, policy);
}

[[nodiscard]] std::string catalog_digest(
    std::string_view content_catalog_digest,
    const SyncReplicaSelectiveSyncPolicy& policy) {
    return selective_catalog_digest(
        kCatalogDigestDomain, kSchemaVersion,
        content_catalog_digest, policy);
}

[[nodiscard]] std::string cyclic_catalog_digest(
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    return modern_catalog_digest(
        kCyclicCatalogDigestDomain, kCyclicSchemaVersion,
        "cyclic folder catalog digest", folder_id, absolute_root_path,
        root_attestation_digest, limits, state_generation, entries);
}

[[nodiscard]] std::string remote_inspection_sweep_basis_digest_or_throw(
    std::string_view catalog_cutpoint_digest,
    std::string_view replica_visible_state_digest,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(catalog_cutpoint_digest) ||
        !is_lowercase_sha256_hex(replica_visible_state_digest)) {
        throw std::invalid_argument(
            label + " requires lowercase SHA-256 cutpoint digests");
    }
    Sha256DigestBuilder digest;
    append_string(digest, kRemoteInspectionSweepBasisDigestDomain);
    append_string(digest, catalog_cutpoint_digest);
    append_string(digest, replica_visible_state_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string previous_catalog_digest(
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    return modern_catalog_digest(
        kPreviousCatalogDigestDomain, kPreviousSchemaVersion,
        "previous folder catalog digest", folder_id, absolute_root_path,
        root_attestation_digest, limits, state_generation, entries);
}

[[nodiscard]] std::string fair_scan_catalog_digest(
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    return modern_catalog_digest(
        kFairScanCatalogDigestDomain, kFairScanSchemaVersion,
        "fair-scan folder catalog digest", folder_id, absolute_root_path,
        root_attestation_digest, limits, state_generation, entries);
}

[[nodiscard]] std::string legacy_catalog_digest(
    std::string_view folder_id,
    std::string_view absolute_root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::vector<SyncReplicaFolderCatalogEntry>& entries) {
    Sha256DigestBuilder digest;
    append_string(digest, kLegacyCatalogDigestDomain);
    append_u64(digest, kLegacySchemaVersion);
    append_string(digest, folder_id);
    append_string(digest, absolute_root_path);
    append_string(digest, root_attestation_digest);
    append_u64(digest, limits.max_catalog_entries);
    append_u64(digest, limits.max_catalog_path_bytes);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, state_generation);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    for (const auto& entry : entries) {
        if (entry.kind != SyncReplicaValueKind::File) {
            throw std::logic_error(
                "legacy folder catalog digest received a non-file entry");
        }
        append_string(digest, entry.canonical_path);
        append_u64(digest, entry.size_bytes);
        append_string(digest, entry.content_sha256);
        append_string(digest, entry.operation_id);
        append_string(digest, entry.source_snapshot_sha256);
        append_u64(digest, entry.last_seen_generation);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string scan_seen_genesis_digest(
    std::uint64_t scan_epoch) {
    Sha256DigestBuilder digest;
    append_string(digest, kFolderScanSeenChainDigestDomain);
    append_u64(digest, scan_epoch);
    append_u64(digest, 0U);
    return digest.finish_hex();
}

[[nodiscard]] std::string scan_seen_next_digest(
    std::uint64_t scan_epoch,
    std::uint64_t ordinal,
    std::string_view previous_digest,
    std::string_view canonical_path) {
    Sha256DigestBuilder digest;
    append_string(digest, kFolderScanSeenChainDigestDomain);
    append_u64(digest, scan_epoch);
    append_u64(digest, ordinal);
    append_string(digest, previous_digest);
    append_string(digest, canonical_path);
    return digest.finish_hex();
}

[[nodiscard]] std::uint64_t own_schema_object_count_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label,
    bool temporary) {
    const std::string schema = temporary ? "temp" : "main";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM " + schema +
            ".sqlite_schema WHERE sql IS NOT NULL AND "
            "name GLOB 'sync_replica_folder_catalog_*';",
        label + " schema count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema count step") != SQLITE_ROW) {
        throw std::runtime_error(label + " schema count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " schema count");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " schema count returned multiple rows");
    }
    return count;
}

[[nodiscard]] std::uint64_t total_user_schema_object_count_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label,
    bool temporary = false) {
    const std::string schema = temporary ? "temp" : "main";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM " + schema +
            ".sqlite_schema WHERE sql IS NOT NULL AND "
            "name NOT GLOB 'sqlite_*';",
        label + " total schema count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " total schema count step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " total schema count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " total schema count");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " total schema count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " total schema count returned multiple rows");
    }
    return count;
}

void require_schema_definition_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SchemaDefinition& expected,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT type,tbl_name,sql FROM main.sqlite_schema WHERE name=?;",
        label + " schema definition prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, std::string(expected.name), label);
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema definition step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " required schema object is missing: " +
            std::string(expected.name));
    }
    const std::string type = sqlite_column_text_or_throw(
        statement.stmt, 0, 16U, label + " schema object type");
    const std::string table = sqlite_column_text_or_throw(
        statement.stmt, 1, 128U, label + " schema object table");
    const std::string sql = sqlite_column_text_or_throw(
        statement.stmt, 2, 4096U, label + " schema object SQL");
    const bool expected_index =
        expected.name == "sync_replica_folder_catalog_file_content";
    const std::string_view expected_type = expected_index ? "index" : "table";
    const std::string_view expected_table = expected_index
        ? "sync_replica_folder_catalog_entries"
        : expected.name;
    if (type != expected_type || table != expected_table ||
        sql != expected.sql) {
        throw std::runtime_error(
            label + " schema definition mismatch for " +
            std::string(expected.name));
    }
    if (step_row_or_done_or_throw(
            statement.stmt,
            label + " schema definition trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " schema object name is not unique: " +
            std::string(expected.name));
    }
}

template <std::size_t Size>
void attest_schema_family_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::array<SchemaDefinition, Size>& schema,
    bool deployment_bound,
    const std::string& label) {
    const std::uint64_t expected_owned =
        static_cast<std::uint64_t>(schema.size());
    const std::uint64_t expected_total =
        expected_owned + (deployment_bound ? 1U : 0U);
    const std::uint64_t observed_owned =
        own_schema_object_count_or_throw(db, label, false);
    const std::uint64_t observed_total =
        total_user_schema_object_count_or_throw(db, label);
    if (observed_owned != expected_owned ||
        observed_total != expected_total) {
        throw std::runtime_error(
            label + " catalog schema object count mismatch: expected " +
            std::to_string(expected_owned) + " owned / " +
            std::to_string(expected_total) + " total, observed " +
            std::to_string(observed_owned) + " owned / " +
            std::to_string(observed_total) + " total");
    }
    if (own_schema_object_count_or_throw(db, label, true) != 0U ||
        total_user_schema_object_count_or_throw(db, label, true) != 0U) {
        throw std::runtime_error(
            label + " catalog has unowned temp schema objects");
    }
    for (const auto& definition : schema) {
        require_schema_definition_or_throw(db, definition, label);
    }
}

void attest_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(db, kSchema, deployment_bound, label);
}

void attest_selective_sync_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kSelectiveSyncSchema, deployment_bound, label);
}

void attest_preselection_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kPreselectionSchema, deployment_bound, label);
}

void attest_cyclic_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kCyclicSchema, deployment_bound, label);
}

void attest_fair_scan_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kFairScanSchema, deployment_bound, label);
}

void attest_previous_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kPreviousSchema, deployment_bound, label);
}

void attest_legacy_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    bool deployment_bound,
    const std::string& label) {
    attest_schema_family_or_throw(
        db, kLegacySchema, deployment_bound, label);
}

void validate_catalog_entry_or_throw(
    const SyncReplicaFolderCatalogEntry& entry,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::string& label) {
    const SyncValidationResult path =
        validate_sync_relative_path(entry.canonical_path);
    if (!path.ok) {
        throw std::runtime_error(
            label + " catalog path is invalid: " + path.reason);
    }
    try {
        reject_reserved_internal_path_components_or_throw(
            entry.canonical_path, label + " catalog");
    } catch (const std::invalid_argument& error) {
        throw std::runtime_error(error.what());
    }
    if (!is_lowercase_sha256_hex(entry.operation_id)) {
        throw std::runtime_error(
            label + " catalog contains an invalid SHA-256 identity");
    }
    switch (entry.kind) {
        case SyncReplicaValueKind::File:
            if (entry.size_bytes > limits.max_payload_bytes) {
                throw std::runtime_error(
                    label + " catalog payload exceeds its persisted limit");
            }
            if (!is_lowercase_sha256_hex(entry.content_sha256) ||
                !is_lowercase_sha256_hex(
                    entry.source_snapshot_sha256)) {
                throw std::runtime_error(
                    label + " catalog contains an invalid file identity");
            }
            break;
        case SyncReplicaValueKind::Tombstone:
            if (entry.size_bytes != 0U ||
                !entry.content_sha256.empty() ||
                !entry.source_snapshot_sha256.empty()) {
                throw std::runtime_error(
                    label + " catalog tombstone retains file material");
            }
            break;
        default:
            throw std::runtime_error(
                label + " catalog value kind is invalid");
    }
    if (entry.last_seen_generation == 0U ||
        entry.last_seen_generation > state_generation) {
        throw std::runtime_error(
            label + " catalog entry generation is outside the cutpoint");
    }
}

[[nodiscard]] SyncReplicaFolderCatalogEntry
load_modern_catalog_entry_row_or_throw(
    sqlite3_stmt* statement,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::string& label) {
    SyncReplicaFolderCatalogEntry entry;
    entry.canonical_path = sqlite_column_text_or_throw(
        statement, 0, 4096U, label + " entry path");
    entry.kind = catalog_value_kind_from_integer_or_throw(
        sqlite_column_u64_or_throw(
            statement, 1, label + " entry value kind"),
        label);
    entry.size_bytes = sqlite_column_u64_or_throw(
        statement, 2, label + " entry size");
    entry.content_sha256 = sqlite_column_text_or_throw(
        statement, 3, 64U, label + " entry content digest");
    entry.operation_id = sqlite_column_text_or_throw(
        statement, 4, 64U, label + " entry operation identity");
    entry.source_snapshot_sha256 = sqlite_column_text_or_throw(
        statement, 5, 64U, label + " entry source digest");
    entry.last_seen_generation = sqlite_column_u64_or_throw(
        statement, 6, label + " entry generation");
    validate_catalog_entry_or_throw(
        entry, limits, state_generation, label);
    return entry;
}

using ModernCatalogDigestFunction = std::string (*)(
    std::string_view,
    std::string_view,
    std::string_view,
    const SyncReplicaFolderScanLimits&,
    std::uint64_t,
    const std::vector<SyncReplicaFolderCatalogEntry>&);

using CatalogSchemaAttester = void (*)(
    SyncSqliteDbHandleSlot&,
    bool,
    const std::string&);

// Current-format catalogs from v2 onward share the same entry representation.
// Keep their exact schema and digest identities distinct, but centralize the
// proof walk so migrations cannot silently diverge in path, capacity, or entry
// validation merely because another scheduling table was added later.
[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_modern_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    std::uint64_t expected_schema_version,
    CatalogSchemaAttester schema_attester,
    ModernCatalogDigestFunction digest_function,
    bool detached_binding,
    bool deployment_binding_already_attested = false,
    std::string_view digest_column = "catalog_digest") {
    if (schema_attester == nullptr || digest_function == nullptr) {
        throw std::logic_error(label + " catalog load profile is incomplete");
    }
    if (detached_binding && deployment_binding == nullptr) {
        throw std::logic_error(label + " detached catalog binding is absent");
    }
    if (deployment_binding_already_attested && deployment_binding != nullptr) {
        throw std::logic_error(
            label + " catalog binding proof mode is ambiguous");
    }
    if (deployment_binding != nullptr) {
        if (detached_binding) {
            attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
                db, *deployment_binding, label + " detached deployment binding");
        } else {
            attest_sync_replica_sqlite_deployment_binding_state_or_throw(
                db, *deployment_binding, label + " deployment binding");
        }
    }
    schema_attester(
        db, deployment_binding != nullptr ||
                deployment_binding_already_attested,
        label);

    if (digest_column != "catalog_digest" &&
        digest_column != "content_catalog_digest") {
        throw std::logic_error(label + " catalog digest column is invalid");
    }
    const std::string metadata_sql =
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes," + std::string(digest_column) +
        " FROM main.sync_replica_folder_catalog_meta WHERE id=1;";
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db, metadata_sql, label + " metadata prepare");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata step") != SQLITE_ROW) {
        throw std::runtime_error(label + " catalog metadata row is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " schema version");
    SyncReplicaFolderCatalogSnapshot snapshot;
    snapshot.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder identity");
    snapshot.absolute_root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " root path");
    snapshot.root_attestation_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U, label + " root attestation digest");
    snapshot.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " state generation");
    snapshot.limits.max_catalog_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " entry limit");
    snapshot.limits.max_catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " path byte limit");
    snapshot.limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " payload byte limit");
    const std::uint64_t expected_entry_count = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " entry count");
    const std::uint64_t expected_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 9, label + " path bytes");
    snapshot.content_catalog_digest = sqlite_column_text_or_throw(
        meta.stmt, 10, 64U, label + " content catalog digest");
    snapshot.catalog_digest = snapshot.content_catalog_digest;
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " catalog metadata identity is not unique");
    }

    if (schema_version != expected_schema_version ||
        snapshot.folder_id != expected_folder_id ||
        snapshot.absolute_root_path != expected_root_path ||
        snapshot.root_attestation_digest !=
            expected_root_attestation_digest) {
        throw std::runtime_error(
            label + " catalog identity does not match the configured folder");
    }
    validate_sync_replica_folder_scan_limits_or_throw(snapshot.limits);
    if (snapshot.state_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(snapshot.root_attestation_digest) ||
        !is_lowercase_sha256_hex(snapshot.content_catalog_digest)) {
        throw std::runtime_error(label + " catalog metadata is invalid");
    }

    SyncSqliteStmt entries = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries "
        "ORDER BY canonical_path;",
        label + " entries prepare");
    std::uint64_t path_bytes = 0U;
    for (;;) {
        const int step = step_row_or_done_or_throw(
            entries.stmt, label + " entries step");
        if (step == SQLITE_DONE) break;
        SyncReplicaFolderCatalogEntry entry =
            load_modern_catalog_entry_row_or_throw(
                entries.stmt, snapshot.limits,
                snapshot.state_generation, label);
        path_bytes = add_or_throw(
            path_bytes,
            static_cast<std::uint64_t>(entry.canonical_path.size()),
            label + " path bytes");
        snapshot.entries.push_back(std::move(entry));
        if (snapshot.entries.size() > snapshot.limits.max_catalog_entries) {
            throw std::runtime_error(
                label + " catalog exceeds its persisted entry limit");
        }
    }

    if (snapshot.entries.size() != expected_entry_count ||
        path_bytes != expected_path_bytes ||
        path_bytes > snapshot.limits.max_catalog_path_bytes ||
        digest_function(
            snapshot.folder_id, snapshot.absolute_root_path,
            snapshot.root_attestation_digest, snapshot.limits,
            snapshot.state_generation, snapshot.entries) !=
            snapshot.content_catalog_digest) {
        throw std::runtime_error(
            label + " catalog cutpoint attestation failed");
    }
    return snapshot;
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_preselection_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    return load_modern_catalog_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kPreselectionSchemaVersion, &attest_preselection_schema_or_throw,
        &preselection_catalog_digest, detached_binding);
}

// Selection changes are bounded operator metadata, not a reason to retain the
// complete file catalog in memory.  This cutpoint deliberately carries only
// the current catalog identity needed to compose and publish a new selection
// digest plus the at-most-1,024 canonical prefix rules.  The stored content
// digest is not treated as a fresh proof of every catalog row; ordinary
// convergence and full snapshots remain the owners of that expensive proof.
// Exact schema attestation excludes triggers and unknown schema objects, so the
// bounded replacement below can change selection/journal rows without granting
// an indirect write path into file-content authority.
struct FolderSelectiveSyncCutpoint final {
    std::string folder_id;
    std::string absolute_root_path;
    std::string root_attestation_digest;
    std::uint64_t state_generation = 0U;
    SyncReplicaFolderScanLimits limits;
    std::uint64_t entry_count = 0U;
    std::uint64_t catalog_path_bytes = 0U;
    std::string content_catalog_digest;
    SyncReplicaSelectiveSyncPolicy policy;
    std::uint64_t absence_inference_fence_generation = 0U;
    std::string catalog_digest;

    bool operator==(const FolderSelectiveSyncCutpoint&) const = default;
};

[[nodiscard]] FolderSelectiveSyncCutpoint
load_selective_sync_cutpoint_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const std::string& label,
    std::uint64_t expected_schema_version = kSchemaVersion,
    std::string (*digest_function)(
        std::string_view,
        const SyncReplicaSelectiveSyncPolicy&) = &catalog_digest) {
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,content_catalog_digest,selection_generation,"
        "selection_absence_fence_generation,selection_default_mode,"
        "selection_rule_count,"
        "selection_rule_path_bytes,selection_digest,catalog_digest "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1;",
        label + " selective-sync metadata prepare");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " selective-sync metadata step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " selective-sync metadata row is missing");
    }

    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " selective-sync schema version");
    FolderSelectiveSyncCutpoint cutpoint;
    cutpoint.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " selective-sync folder identity");
    cutpoint.absolute_root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " selective-sync root path");
    cutpoint.root_attestation_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U,
        label + " selective-sync root attestation digest");
    cutpoint.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " selective-sync state generation");
    cutpoint.limits.max_catalog_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " selective-sync entry limit");
    cutpoint.limits.max_catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " selective-sync path-byte limit");
    cutpoint.limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " selective-sync payload-byte limit");
    cutpoint.entry_count = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " selective-sync entry count");
    cutpoint.catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 9, label + " selective-sync catalog path bytes");
    cutpoint.content_catalog_digest = sqlite_column_text_or_throw(
        meta.stmt, 10, 64U,
        label + " selective-sync content catalog digest");
    cutpoint.policy.generation = sqlite_column_u64_or_throw(
        meta.stmt, 11, label + " selective-sync generation");
    cutpoint.absence_inference_fence_generation =
        sqlite_column_u64_or_throw(
            meta.stmt, 12,
            label + " selective-sync absence-inference fence generation");
    const std::uint64_t default_mode = sqlite_column_u64_or_throw(
        meta.stmt, 13, label + " selective-sync default mode");
    switch (default_mode) {
        case 1U:
            cutpoint.policy.default_mode =
                SyncReplicaSelectiveSyncMode::Materialize;
            break;
        case 2U:
            cutpoint.policy.default_mode =
                SyncReplicaSelectiveSyncMode::MetadataOnly;
            break;
        default:
            throw std::runtime_error(
                label + " selective-sync default mode is invalid");
    }
    const std::uint64_t expected_rule_count = sqlite_column_u64_or_throw(
        meta.stmt, 14, label + " selective-sync rule count");
    cutpoint.policy.rule_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 15, label + " selective-sync rule-path bytes");
    cutpoint.policy.policy_digest = sqlite_column_text_or_throw(
        meta.stmt, 16, 64U, label + " selective-sync digest");
    cutpoint.catalog_digest = sqlite_column_text_or_throw(
        meta.stmt, 17, 64U, label + " catalog digest");
    if (step_row_or_done_or_throw(
            meta.stmt,
            label + " selective-sync metadata trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " selective-sync metadata identity is not unique");
    }

    if (schema_version != expected_schema_version ||
        cutpoint.folder_id != expected_folder_id ||
        cutpoint.absolute_root_path != expected_root_path ||
        cutpoint.root_attestation_digest !=
            expected_root_attestation_digest) {
        throw std::runtime_error(
            label + " selective-sync catalog identity does not match the configured folder");
    }
    validate_sync_replica_folder_scan_limits_or_throw(cutpoint.limits);
    if (cutpoint.state_generation > kMaxPersistentInteger ||
        cutpoint.entry_count > cutpoint.limits.max_catalog_entries ||
        cutpoint.catalog_path_bytes >
            cutpoint.limits.max_catalog_path_bytes ||
        (cutpoint.absence_inference_fence_generation != 0U &&
         cutpoint.absence_inference_fence_generation !=
             cutpoint.policy.generation) ||
        expected_rule_count > kSyncReplicaSelectiveSyncMaximumRules ||
        cutpoint.policy.rule_path_bytes >
            kSyncReplicaSelectiveSyncMaximumRulePathBytes ||
        !is_lowercase_sha256_hex(cutpoint.root_attestation_digest) ||
        !is_lowercase_sha256_hex(cutpoint.content_catalog_digest) ||
        !is_lowercase_sha256_hex(cutpoint.catalog_digest)) {
        throw std::runtime_error(
            label + " selective-sync metadata is outside its bounds");
    }

    SyncSqliteStmt rules = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,selection_mode FROM "
        "main.sync_replica_folder_catalog_selection_rules "
        "ORDER BY canonical_path;",
        label + " selective-sync rules prepare");
    cutpoint.policy.rules.reserve(
        static_cast<std::size_t>(expected_rule_count));
    for (;;) {
        const int step = step_row_or_done_or_throw(
            rules.stmt, label + " selective-sync rules step");
        if (step == SQLITE_DONE) break;
        SyncReplicaSelectiveSyncRule rule;
        rule.canonical_path = sqlite_column_text_or_throw(
            rules.stmt, 0, 4096U, label + " selective-sync rule path");
        const std::uint64_t mode = sqlite_column_u64_or_throw(
            rules.stmt, 1, label + " selective-sync rule mode");
        if (mode == 1U) {
            rule.mode = SyncReplicaSelectiveSyncMode::Materialize;
        } else if (mode == 2U) {
            rule.mode = SyncReplicaSelectiveSyncMode::MetadataOnly;
        } else {
            throw std::runtime_error(
                label + " selective-sync rule mode is invalid");
        }
        cutpoint.policy.rules.push_back(std::move(rule));
        if (cutpoint.policy.rules.size() >
            kSyncReplicaSelectiveSyncMaximumRules) {
            throw std::runtime_error(
                label + " selective-sync rule count exceeds its limit");
        }
    }
    if (cutpoint.policy.rules.size() != expected_rule_count) {
        throw std::runtime_error(
            label + " selective-sync rule count is not exact");
    }
    try {
        validate_sync_replica_selective_sync_policy_or_throw(
            cutpoint.policy, label + " selective-sync policy");
    } catch (const std::exception& error) {
        throw std::runtime_error(error.what());
    }
    if (digest_function(
            cutpoint.content_catalog_digest, cutpoint.policy) !=
        cutpoint.catalog_digest) {
        throw std::runtime_error(
            label + " selective-sync catalog cutpoint attestation failed");
    }
    return cutpoint;
}

// One-path publication reproof must not reload the complete catalog.  The
// owner has already attested the exact trigger-free schema at construction;
// this read transaction pins the current metadata row and one PRIMARY KEY
// entry in a single SQLite snapshot.  The selection generation and digest are
// sufficient to prove that the previously evaluated bounded policy did not
// change.  This is deliberately path-local authority: it does not claim a
// fresh proof of unrelated rows or of the stored aggregate catalog digest.
struct FolderCatalogPathCutpoint final {
    std::uint64_t state_generation = 0U;
    SyncReplicaFolderScanLimits limits;
    std::uint64_t selection_generation = 0U;
    std::uint64_t selection_absence_fence_generation = 0U;
    std::string selection_digest;
    std::optional<SyncReplicaFolderCatalogEntry> entry;

    bool operator==(const FolderCatalogPathCutpoint&) const = default;
};

[[nodiscard]] FolderCatalogPathCutpoint
load_folder_catalog_path_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaFolderScanLimits& expected_limits,
    const std::string& canonical_path,
    const std::string& label) {
    const SyncValidationResult path =
        validate_sync_relative_path(canonical_path);
    if (!path.ok) {
        throw std::invalid_argument(
            label + " catalog path is invalid: " + path.reason);
    }

    SyncSqliteTransaction transaction(
        db, label + " path cutpoint", SyncSqliteTransactionMode::Deferred);
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,selection_generation,"
        "selection_absence_fence_generation,selection_digest "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1;",
        label + " path metadata prepare");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " path metadata step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " path metadata row is missing");
    }

    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " path schema version");
    const std::string folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " path folder identity");
    const std::string root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " path root path");
    const std::string root_attestation_digest =
        sqlite_column_text_or_throw(
            meta.stmt, 3, 64U, label + " path root attestation digest");

    FolderCatalogPathCutpoint cutpoint;
    cutpoint.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " path state generation");
    cutpoint.limits.max_catalog_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " path entry limit");
    cutpoint.limits.max_catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " path path-byte limit");
    cutpoint.limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " path payload-byte limit");
    cutpoint.selection_generation = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " path selection generation");
    cutpoint.selection_absence_fence_generation =
        sqlite_column_u64_or_throw(
            meta.stmt, 9, label + " path selection absence fence");
    cutpoint.selection_digest = sqlite_column_text_or_throw(
        meta.stmt, 10, 64U, label + " path selection digest");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " path metadata trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " path metadata identity is not unique");
    }

    if (schema_version != kSchemaVersion ||
        folder_id != expected_folder_id ||
        root_path != expected_root_path ||
        root_attestation_digest != expected_root_attestation_digest ||
        cutpoint.limits != expected_limits) {
        throw std::runtime_error(
            label + " path cutpoint identity does not match the configured folder");
    }
    validate_sync_replica_folder_scan_limits_or_throw(cutpoint.limits);
    if (cutpoint.state_generation > kMaxPersistentInteger ||
        cutpoint.selection_generation == 0U ||
        cutpoint.selection_generation > kMaxPersistentInteger ||
        (cutpoint.selection_absence_fence_generation != 0U &&
         cutpoint.selection_absence_fence_generation !=
             cutpoint.selection_generation) ||
        !is_lowercase_sha256_hex(root_attestation_digest) ||
        !is_lowercase_sha256_hex(cutpoint.selection_digest)) {
        throw std::runtime_error(
            label + " path cutpoint metadata is invalid");
    }

    SyncSqliteStmt entry = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,"
        "operation_id,source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries "
        "WHERE canonical_path=?;",
        label + " exact path prepare");
    sqlite_bind_text_or_throw(entry.stmt, 1, canonical_path, label);
    const int entry_step = step_row_or_done_or_throw(
        entry.stmt, label + " exact path step");
    if (entry_step == SQLITE_ROW) {
        SyncReplicaFolderCatalogEntry observed =
            load_modern_catalog_entry_row_or_throw(
                entry.stmt, cutpoint.limits,
                cutpoint.state_generation, label + " exact path");
        if (observed.canonical_path != canonical_path) {
            throw std::runtime_error(
                label + " exact path query returned a different path");
        }
        cutpoint.entry = std::move(observed);
        if (step_row_or_done_or_throw(
                entry.stmt, label + " exact path trailing step") !=
            SQLITE_DONE) {
            throw std::runtime_error(
                label + " exact path entry is not unique");
        }
    }

    transaction.commit();
    return cutpoint;
}


// One bounded exact-content lookup over the startup-attested catalog index.
// At most two rows are decoded: a sole match can participate in conservative
// rename planning, while a second match makes identity ambiguous.  The query
// proves exact canonical row bytes and the catalog identity in one deferred
// SQLite snapshot; it does not claim complete catalog authority.
struct FolderCatalogFileContentCutpoint final {
    std::optional<SyncReplicaFolderCatalogEntry> sole_file_entry;
    bool ambiguous = false;

    bool operator==(const FolderCatalogFileContentCutpoint&) const = default;
};

[[nodiscard]] FolderCatalogFileContentCutpoint
load_folder_catalog_file_content_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    std::uint64_t size_bytes,
    const std::string& content_sha256,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            label + " content digest is not canonical SHA-256");
    }
    if (size_bytes > kMaxPersistentInteger) {
        throw std::invalid_argument(
            label + " content size is outside the SQLite integer range");
    }

    SyncSqliteTransaction transaction(
        db, label + " file-content cutpoint",
        SyncSqliteTransactionMode::Deferred);
    if (deployment_binding != nullptr) {
        attest_sync_replica_sqlite_deployment_binding_state_or_throw(
            db, *deployment_binding, label + " deployment binding");
    }
    attest_schema_or_throw(
        db, deployment_binding != nullptr, label + " schema");

    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1;",
        label + " metadata prepare");
    if (step_row_or_done_or_throw(meta.stmt, label + " metadata step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " metadata row is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " schema version");
    const std::string folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder identity");
    const std::string root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " root path");
    const std::string root_attestation_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U, label + " root attestation digest");
    const std::uint64_t state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " state generation");
    SyncReplicaFolderScanLimits limits;
    limits.max_catalog_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " entry limit");
    limits.max_catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " path-byte limit");
    limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " payload-byte limit");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata trailing step") != SQLITE_DONE) {
        throw std::runtime_error(label + " metadata identity is not unique");
    }
    if (schema_version != kSchemaVersion ||
        folder_id != expected_folder_id ||
        root_path != expected_root_path ||
        root_attestation_digest != expected_root_attestation_digest) {
        throw std::runtime_error(
            label + " catalog identity does not match the configured folder");
    }
    validate_sync_replica_folder_scan_limits_or_throw(limits);
    if (state_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(root_attestation_digest)) {
        throw std::runtime_error(label + " catalog metadata is invalid");
    }

    SyncSqliteStmt rows = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,"
        "operation_id,source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries INDEXED BY "
        "sync_replica_folder_catalog_file_content "
        "WHERE value_kind=1 AND content_sha256=? AND size_bytes=? "
        "ORDER BY canonical_path,operation_id LIMIT 2;",
        label + " indexed rows prepare");
    sqlite_bind_text_or_throw(rows.stmt, 1, content_sha256, label);
    sqlite_bind_u64_or_throw(rows.stmt, 2, size_bytes, label);

    FolderCatalogFileContentCutpoint cutpoint;
    std::optional<SyncReplicaFolderCatalogEntry> first;
    for (std::uint64_t row_count = 0U;;) {
        const int step = step_row_or_done_or_throw(
            rows.stmt, label + " indexed rows step");
        if (step == SQLITE_DONE) break;
        row_count = increment_or_throw(row_count, label + " indexed row count");
        SyncReplicaFolderCatalogEntry entry =
            load_modern_catalog_entry_row_or_throw(
                rows.stmt, limits, state_generation,
                label + " indexed row");
        if (entry.kind != SyncReplicaValueKind::File ||
            entry.size_bytes != size_bytes ||
            entry.content_sha256 != content_sha256) {
            throw std::runtime_error(
                label + " indexed content row disagrees with its lookup key");
        }
        if (row_count == 1U) {
            first = std::move(entry);
        } else if (row_count == 2U) {
            cutpoint.ambiguous = true;
        } else {
            throw std::logic_error(
                label + " indexed query exceeded its LIMIT 2 bound");
        }
    }
    if (!cutpoint.ambiguous) {
        cutpoint.sole_file_entry = std::move(first);
    }
    transaction.commit();
    return cutpoint;
}

[[nodiscard]] FolderSelectiveSyncCutpoint
load_selective_sync_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label) {
    if (deployment_binding != nullptr) {
        attest_sync_replica_sqlite_deployment_binding_state_or_throw(
            db, *deployment_binding, label + " deployment binding");
    }
    attest_schema_or_throw(
        db, deployment_binding != nullptr, label);
    return load_selective_sync_cutpoint_rows_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, label);
}

[[nodiscard]] SyncReplicaFolderSelectiveSyncSnapshot
public_selective_sync_snapshot(
    const FolderSelectiveSyncCutpoint& cutpoint) {
    SyncReplicaFolderSelectiveSyncSnapshot snapshot;
    snapshot.folder_id = cutpoint.folder_id;
    snapshot.absolute_root_path = cutpoint.absolute_root_path;
    snapshot.limits = cutpoint.limits;
    snapshot.state_generation = cutpoint.state_generation;
    snapshot.catalog_entry_count = cutpoint.entry_count;
    snapshot.catalog_path_bytes = cutpoint.catalog_path_bytes;
    snapshot.content_catalog_digest = cutpoint.content_catalog_digest;
    snapshot.policy = cutpoint.policy;
    snapshot.absence_inference_fence_generation =
        cutpoint.absence_inference_fence_generation;
    snapshot.catalog_digest = cutpoint.catalog_digest;
    return snapshot;
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_selective_catalog_for_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    std::uint64_t expected_schema_version,
    void (*schema_attester)(
        SyncSqliteDbHandleSlot&, bool, const std::string&),
    std::string (*digest_function)(
        std::string_view,
        const SyncReplicaSelectiveSyncPolicy&),
    bool detached_binding = false,
    bool deployment_binding_already_attested = false) {
    SyncReplicaFolderCatalogSnapshot snapshot =
        load_modern_catalog_or_throw(
            db, expected_folder_id, expected_root_path,
            expected_root_attestation_digest, deployment_binding, label,
            expected_schema_version, schema_attester,
            &preselection_catalog_digest, detached_binding,
            deployment_binding_already_attested,
            "content_catalog_digest");

    const FolderSelectiveSyncCutpoint selection =
        load_selective_sync_cutpoint_rows_or_throw(
            db, expected_folder_id, expected_root_path,
            expected_root_attestation_digest,
            label + " bounded selective-sync cutpoint",
            expected_schema_version, digest_function);
    if (selection.folder_id != snapshot.folder_id ||
        selection.absolute_root_path != snapshot.absolute_root_path ||
        selection.root_attestation_digest !=
            snapshot.root_attestation_digest ||
        selection.state_generation != snapshot.state_generation ||
        selection.limits != snapshot.limits ||
        selection.entry_count != snapshot.entries.size() ||
        selection.content_catalog_digest !=
            snapshot.content_catalog_digest) {
        throw std::runtime_error(
            label + " selective-sync cutpoint disagrees with the content catalog");
    }
    std::uint64_t catalog_path_bytes = 0U;
    for (const SyncReplicaFolderCatalogEntry& entry : snapshot.entries) {
        catalog_path_bytes = add_or_throw(
            catalog_path_bytes,
            static_cast<std::uint64_t>(entry.canonical_path.size()),
            label + " selective-sync catalog path-byte reproof");
    }
    if (selection.catalog_path_bytes != catalog_path_bytes) {
        throw std::runtime_error(
            label + " selective-sync path-byte cutpoint disagrees with the content catalog");
    }
    snapshot.selective_sync_policy = selection.policy;
    snapshot.selective_sync_absence_fence_generation =
        selection.absence_inference_fence_generation;
    snapshot.catalog_digest = selection.catalog_digest;
    return snapshot;
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_selective_sync_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    return load_selective_catalog_for_schema_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kSelectiveSyncSchemaVersion, &attest_selective_sync_schema_or_throw,
        &selective_sync_catalog_digest, detached_binding);
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot load_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false,
    bool deployment_binding_already_attested = false) {
    return load_selective_catalog_for_schema_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kSchemaVersion, &attest_schema_or_throw, &catalog_digest,
        detached_binding, deployment_binding_already_attested);
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_cyclic_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    return load_modern_catalog_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kCyclicSchemaVersion, &attest_cyclic_schema_or_throw,
        &cyclic_catalog_digest, detached_binding);
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_fair_scan_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    return load_modern_catalog_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kFairScanSchemaVersion, &attest_fair_scan_schema_or_throw,
        &fair_scan_catalog_digest, detached_binding);
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot load_previous_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    return load_modern_catalog_or_throw(
        db, expected_folder_id, expected_root_path,
        expected_root_attestation_digest, deployment_binding, label,
        kPreviousSchemaVersion, &attest_previous_schema_or_throw,
        &previous_catalog_digest, detached_binding);
}


[[nodiscard]] std::uint64_t catalog_schema_version_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version FROM main.sync_replica_folder_catalog_meta "
        "WHERE id=1;",
        label + " schema-version prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema-version step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " catalog metadata row is missing");
    }
    const std::uint64_t version = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " schema version");
    if (step_row_or_done_or_throw(
            statement.stmt,
            label + " schema-version trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " catalog metadata identity is not unique");
    }
    return version;
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
load_legacy_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding = false) {
    if (detached_binding && deployment_binding == nullptr) {
        throw std::logic_error(
            label + " detached legacy catalog binding is absent");
    }
    if (deployment_binding != nullptr) {
        if (detached_binding) {
            attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
                db, *deployment_binding,
                label + " detached deployment binding");
        } else {
            attest_sync_replica_sqlite_deployment_binding_state_or_throw(
                db, *deployment_binding, label + " deployment binding");
        }
    }
    attest_legacy_schema_or_throw(
        db, deployment_binding != nullptr, label);

    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1;",
        label + " metadata prepare");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " legacy catalog metadata row is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " schema version");
    SyncReplicaFolderCatalogSnapshot snapshot;
    snapshot.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder identity");
    snapshot.absolute_root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " root path");
    snapshot.root_attestation_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U, label + " root attestation digest");
    snapshot.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " state generation");
    snapshot.limits.max_catalog_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " entry limit");
    snapshot.limits.max_catalog_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " path byte limit");
    snapshot.limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " payload byte limit");
    const std::uint64_t expected_entry_count = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " entry count");
    const std::uint64_t expected_path_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 9, label + " path bytes");
    snapshot.catalog_digest = sqlite_column_text_or_throw(
        meta.stmt, 10, 64U, label + " catalog digest");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " legacy catalog metadata identity is not unique");
    }

    if (schema_version != kLegacySchemaVersion ||
        snapshot.folder_id != expected_folder_id ||
        snapshot.absolute_root_path != expected_root_path ||
        snapshot.root_attestation_digest !=
            expected_root_attestation_digest) {
        throw std::runtime_error(
            label +
            " legacy catalog identity does not match the configured folder");
    }
    validate_sync_replica_folder_scan_limits_or_throw(snapshot.limits);
    if (snapshot.state_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(snapshot.root_attestation_digest) ||
        !is_lowercase_sha256_hex(snapshot.catalog_digest)) {
        throw std::runtime_error(
            label + " legacy catalog metadata is invalid");
    }

    SyncSqliteStmt entries = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries "
        "ORDER BY canonical_path;",
        label + " entries prepare");
    std::uint64_t path_bytes = 0U;
    for (;;) {
        const int step = step_row_or_done_or_throw(
            entries.stmt, label + " entries step");
        if (step == SQLITE_DONE) break;
        SyncReplicaFolderCatalogEntry entry;
        entry.canonical_path = sqlite_column_text_or_throw(
            entries.stmt, 0, 4096U, label + " entry path");
        entry.kind = SyncReplicaValueKind::File;
        entry.size_bytes = sqlite_column_u64_or_throw(
            entries.stmt, 1, label + " entry size");
        entry.content_sha256 = sqlite_column_text_or_throw(
            entries.stmt, 2, 64U, label + " entry content digest");
        entry.operation_id = sqlite_column_text_or_throw(
            entries.stmt, 3, 64U, label + " entry operation identity");
        entry.source_snapshot_sha256 = sqlite_column_text_or_throw(
            entries.stmt, 4, 64U, label + " entry source digest");
        entry.last_seen_generation = sqlite_column_u64_or_throw(
            entries.stmt, 5, label + " entry generation");
        validate_catalog_entry_or_throw(
            entry, snapshot.limits, snapshot.state_generation, label);
        path_bytes = add_or_throw(
            path_bytes,
            static_cast<std::uint64_t>(entry.canonical_path.size()),
            label + " path bytes");
        snapshot.entries.push_back(std::move(entry));
        if (snapshot.entries.size() > snapshot.limits.max_catalog_entries) {
            throw std::runtime_error(
                label + " legacy catalog exceeds its persisted entry limit");
        }
    }

    if (snapshot.entries.size() != expected_entry_count ||
        path_bytes != expected_path_bytes ||
        path_bytes > snapshot.limits.max_catalog_path_bytes ||
        legacy_catalog_digest(
            snapshot.folder_id, snapshot.absolute_root_path,
            snapshot.root_attestation_digest, snapshot.limits,
            snapshot.state_generation, snapshot.entries) !=
            snapshot.catalog_digest) {
        throw std::runtime_error(
            label + " legacy catalog cutpoint attestation failed");
    }
    return snapshot;
}

struct FolderScanProgressHead final {
    std::uint64_t scan_epoch = 0U;
    std::string resume_after_path;
    std::uint64_t seen_path_count = 0U;
    std::uint64_t seen_path_bytes = 0U;
    std::string seen_chain_digest;

    bool operator==(const FolderScanProgressHead&) const = default;
};

void validate_scan_progress_path_or_throw(
    std::string_view canonical_path,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    if (canonical_path.empty() ||
        canonical_path.size() > limits.max_catalog_path_bytes ||
        canonical_path.size() > 4096U) {
        throw std::runtime_error(
            label + " scan-progress path exceeds its persisted limit");
    }
    const SyncValidationResult validation =
        validate_sync_relative_path(canonical_path);
    if (!validation.ok) {
        throw std::runtime_error(
            label + " scan-progress path is invalid: " +
            validation.reason);
    }
    try {
        reject_reserved_internal_path_components_or_throw(
            canonical_path, label + " scan progress");
    } catch (const std::invalid_argument& error) {
        throw std::runtime_error(error.what());
    }
}

[[nodiscard]] FolderScanProgressHead load_scan_progress_head_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    SyncSqliteStmt progress = sqlite_prepare_or_throw(
        db,
        "SELECT scan_epoch,resume_after_path,seen_path_count,seen_path_bytes,"
        "seen_chain_digest FROM "
        "main.sync_replica_folder_catalog_scan_progress WHERE id=1;",
        label + " scan-progress prepare");
    if (step_row_or_done_or_throw(
            progress.stmt, label + " scan-progress step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " scan-progress singleton is missing");
    }
    FolderScanProgressHead head;
    head.scan_epoch = sqlite_column_u64_or_throw(
        progress.stmt, 0, label + " scan epoch");
    head.resume_after_path = sqlite_column_text_or_throw(
        progress.stmt, 1, 4096U, label + " scan cursor");
    head.seen_path_count = sqlite_column_u64_or_throw(
        progress.stmt, 2, label + " scan seen count");
    head.seen_path_bytes = sqlite_column_u64_or_throw(
        progress.stmt, 3, label + " scan seen path bytes");
    head.seen_chain_digest = sqlite_column_text_or_throw(
        progress.stmt, 4, 64U, label + " scan seen digest");
    if (step_row_or_done_or_throw(
            progress.stmt,
            label + " scan-progress trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " scan-progress singleton is not unique");
    }

    if (head.scan_epoch == 0U ||
        head.scan_epoch > kMaxPersistentInteger ||
        head.seen_path_count > limits.max_catalog_entries ||
        head.seen_path_count > kMaxPersistentInteger ||
        head.seen_path_bytes > limits.max_catalog_path_bytes ||
        head.seen_path_bytes > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(head.seen_chain_digest)) {
        throw std::runtime_error(
            label + " scan-progress metadata is invalid");
    }

    SyncSqliteStmt first = sqlite_prepare_or_throw(
        db,
        "SELECT ordinal FROM main.sync_replica_folder_catalog_scan_seen "
        "ORDER BY ordinal LIMIT 1;",
        label + " scan-progress first-row prepare");
    const int first_step = step_row_or_done_or_throw(
        first.stmt, label + " scan-progress first-row step");
    if (head.seen_path_count == 0U) {
        if (!head.resume_after_path.empty() || head.seen_path_bytes != 0U ||
            head.seen_chain_digest !=
                scan_seen_genesis_digest(head.scan_epoch) ||
            first_step != SQLITE_DONE) {
            throw std::runtime_error(
                label + " empty scan-progress cutpoint is inconsistent");
        }
        return head;
    }
    if (first_step != SQLITE_ROW ||
        sqlite_column_u64_or_throw(
            first.stmt, 0, label + " scan-progress first ordinal") != 1U ||
        step_row_or_done_or_throw(
            first.stmt,
            label + " scan-progress first-row trailing step") !=
            SQLITE_DONE) {
        throw std::runtime_error(
            label + " scan-progress first row is inconsistent");
    }

    validate_scan_progress_path_or_throw(
        head.resume_after_path, limits, label);
    if (head.seen_path_bytes < head.resume_after_path.size()) {
        throw std::runtime_error(
            label + " scan-progress path-byte count is inconsistent");
    }
    SyncSqliteStmt tail = sqlite_prepare_or_throw(
        db,
        "SELECT scan_epoch,canonical_path,chain_digest FROM "
        "main.sync_replica_folder_catalog_scan_seen WHERE ordinal=?;",
        label + " scan-progress tail prepare");
    sqlite_bind_u64_or_throw(
        tail.stmt, 1, head.seen_path_count, label);
    if (step_row_or_done_or_throw(
            tail.stmt, label + " scan-progress tail step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " scan-progress tail row is missing");
    }
    const std::uint64_t tail_epoch = sqlite_column_u64_or_throw(
        tail.stmt, 0, label + " scan-progress tail epoch");
    const std::string tail_path = sqlite_column_text_or_throw(
        tail.stmt, 1, 4096U, label + " scan-progress tail path");
    const std::string tail_digest = sqlite_column_text_or_throw(
        tail.stmt, 2, 64U, label + " scan-progress tail digest");
    if (step_row_or_done_or_throw(
            tail.stmt,
            label + " scan-progress tail trailing step") != SQLITE_DONE ||
        tail_epoch != head.scan_epoch ||
        tail_path != head.resume_after_path ||
        tail_digest != head.seen_chain_digest) {
        throw std::runtime_error(
            label + " scan-progress tail does not match its head");
    }

    SyncSqliteStmt beyond = sqlite_prepare_or_throw(
        db,
        "SELECT ordinal FROM main.sync_replica_folder_catalog_scan_seen "
        "WHERE ordinal>? ORDER BY ordinal LIMIT 1;",
        label + " scan-progress beyond-tail prepare");
    sqlite_bind_u64_or_throw(
        beyond.stmt, 1, head.seen_path_count, label);
    if (step_row_or_done_or_throw(
            beyond.stmt,
            label + " scan-progress beyond-tail step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " scan-progress contains rows beyond its head");
    }
    return head;
}

[[nodiscard]] std::vector<std::string>
load_complete_scan_seen_paths_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t expected_scan_epoch,
    const std::string& label) {
    const FolderScanProgressHead head =
        load_scan_progress_head_or_throw(db, limits, label);
    if (head.scan_epoch != expected_scan_epoch) {
        throw std::runtime_error(
            label + " scan epoch changed before completion proof");
    }

    SyncSqliteStmt rows = sqlite_prepare_or_throw(
        db,
        "SELECT ordinal,scan_epoch,canonical_path,chain_digest FROM "
        "main.sync_replica_folder_catalog_scan_seen ORDER BY ordinal;",
        label + " scan seen rows prepare");
    std::vector<std::string> paths;
    paths.reserve(static_cast<std::size_t>(head.seen_path_count));
    std::uint64_t expected_ordinal = 1U;
    std::uint64_t path_bytes = 0U;
    std::string chain = scan_seen_genesis_digest(expected_scan_epoch);
    for (;;) {
        const int step = step_row_or_done_or_throw(
            rows.stmt, label + " scan seen rows step");
        if (step == SQLITE_DONE) break;
        const std::uint64_t ordinal = sqlite_column_u64_or_throw(
            rows.stmt, 0, label + " scan seen ordinal");
        const std::uint64_t epoch = sqlite_column_u64_or_throw(
            rows.stmt, 1, label + " scan seen epoch");
        std::string path = sqlite_column_text_or_throw(
            rows.stmt, 2, 4096U, label + " scan seen path");
        const std::string retained_chain = sqlite_column_text_or_throw(
            rows.stmt, 3, 64U, label + " scan seen chain");
        validate_scan_progress_path_or_throw(path, limits, label);
        if (ordinal != expected_ordinal || epoch != expected_scan_epoch ||
            (!paths.empty() &&
             !sync_replica_folder_traversal_path_less(
                 paths.back(), path))) {
            throw std::runtime_error(
                label + " scan seen rows are not one complete ordered prefix");
        }
        path_bytes = add_or_throw(
            path_bytes, static_cast<std::uint64_t>(path.size()),
            label + " scan seen path bytes");
        chain = scan_seen_next_digest(
            expected_scan_epoch, ordinal, chain, path);
        if (retained_chain != chain) {
            throw std::runtime_error(
                label + " scan seen hash chain is invalid");
        }
        paths.push_back(std::move(path));
        expected_ordinal = increment_or_throw(
            expected_ordinal, label + " scan seen ordinal");
    }
    if (paths.size() != head.seen_path_count ||
        path_bytes != head.seen_path_bytes ||
        chain != head.seen_chain_digest ||
        (paths.empty() ? !head.resume_after_path.empty()
                       : paths.back() != head.resume_after_path)) {
        throw std::runtime_error(
            label + " scan seen cutpoint attestation failed");
    }
    return paths;
}

[[nodiscard]] FolderScanProgressHead record_scan_seen_paths_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t expected_scan_epoch,
    const std::vector<std::string>& canonical_paths,
    const std::string& label) {
    SyncSqliteTransaction transaction(
        db, label + " scan cursor publication",
        SyncSqliteTransactionMode::Immediate);
    const FolderScanProgressHead current =
        load_scan_progress_head_or_throw(db, limits, label + " current");
    if (current.scan_epoch != expected_scan_epoch) {
        throw std::runtime_error(
            label + " scan epoch changed before cursor publication");
    }
    if (canonical_paths.empty()) {
        transaction.commit();
        return current;
    }

    // Path effects are independently idempotent and have already committed.
    // Publish the cooperative scheduling journal once for the complete segment,
    // rather than forcing one SQLite transaction (and potentially one durable
    // sync boundary) per observed file. If this transaction fails or the process
    // stops before it commits, the next pass safely replays the segment effects.
    std::uint64_t next_count = current.seen_path_count;
    std::uint64_t next_path_bytes = current.seen_path_bytes;
    std::string next_chain = current.seen_chain_digest;
    std::string previous_path = current.resume_after_path;

    SyncSqliteStmt insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_scan_seen("
        "ordinal,scan_epoch,canonical_path,chain_digest) VALUES(?,?,?,?);",
        label + " scan seen insert prepare");
    for (const std::string& canonical_path : canonical_paths) {
        validate_scan_progress_path_or_throw(
            canonical_path, limits, label);
        if (!previous_path.empty() &&
            !sync_replica_folder_traversal_path_less(
                previous_path, canonical_path)) {
            throw std::runtime_error(
                label + " scan cursor did not advance in traversal order");
        }
        next_count = increment_or_throw(
            next_count, label + " scan seen count");
        if (next_count > limits.max_catalog_entries) {
            throw std::length_error(
                label + " scan seen entry limit is exhausted");
        }
        next_path_bytes = add_or_throw(
            next_path_bytes,
            static_cast<std::uint64_t>(canonical_path.size()),
            label + " scan seen path bytes");
        if (next_path_bytes > limits.max_catalog_path_bytes ||
            next_path_bytes > kMaxPersistentInteger) {
            throw std::length_error(
                label + " scan seen path-byte limit is exhausted");
        }
        next_chain = scan_seen_next_digest(
            expected_scan_epoch, next_count, next_chain, canonical_path);

        sqlite_bind_u64_or_throw(
            insert.stmt, 1, next_count, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 2, expected_scan_epoch, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 3, canonical_path, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 4, next_chain, label);
        sqlite_step_done_or_throw(
            insert.stmt, label + " scan seen insert step");
        previous_path = canonical_path;
    }

    SyncSqliteStmt update = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_scan_progress SET "
        "resume_after_path=?,seen_path_count=?,seen_path_bytes=?,"
        "seen_chain_digest=? WHERE id=1 AND scan_epoch=? AND "
        "seen_path_count=? AND seen_path_bytes=? AND "
        "resume_after_path=? AND seen_chain_digest=?;",
        label + " scan-progress update prepare");
    sqlite_bind_text_or_throw(update.stmt, 1, previous_path, label);
    sqlite_bind_u64_or_throw(update.stmt, 2, next_count, label);
    sqlite_bind_u64_or_throw(update.stmt, 3, next_path_bytes, label);
    sqlite_bind_text_or_throw(update.stmt, 4, next_chain, label);
    sqlite_bind_u64_or_throw(update.stmt, 5, expected_scan_epoch, label);
    sqlite_bind_u64_or_throw(
        update.stmt, 6, current.seen_path_count, label);
    sqlite_bind_u64_or_throw(
        update.stmt, 7, current.seen_path_bytes, label);
    sqlite_bind_text_or_throw(
        update.stmt, 8, current.resume_after_path, label);
    sqlite_bind_text_or_throw(
        update.stmt, 9, current.seen_chain_digest, label);
    sqlite_step_done_or_throw(
        update.stmt, label + " scan-progress update step");

    const FolderScanProgressHead staged =
        load_scan_progress_head_or_throw(db, limits, label + " staged");
    const FolderScanProgressHead expected{
        expected_scan_epoch, previous_path, next_count, next_path_bytes,
        next_chain};
    if (staged != expected) {
        throw std::runtime_error(
            label + " staged scan cursor did not retain the exact segment");
    }
    transaction.commit();
    return staged;
}

[[nodiscard]] FolderScanProgressHead reset_scan_progress_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t expected_scan_epoch,
    const std::string& label) {
    SyncSqliteTransaction transaction(
        db, label + " scan epoch reset",
        SyncSqliteTransactionMode::Immediate);
    const FolderScanProgressHead current =
        load_scan_progress_head_or_throw(db, limits, label + " current");
    if (current.scan_epoch != expected_scan_epoch) {
        throw std::runtime_error(
            label + " scan epoch changed before reset");
    }
    const std::uint64_t next_epoch =
        current.scan_epoch == kMaxPersistentInteger
            ? 1U
            : current.scan_epoch + 1U;
    sqlite_exec_or_throw(
        db,
        "DELETE FROM main.sync_replica_folder_catalog_scan_seen;",
        label + " clear completed scan paths");
    SyncSqliteStmt update = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_scan_progress SET "
        "scan_epoch=?,resume_after_path='',seen_path_count=0,"
        "seen_path_bytes=0,seen_chain_digest=? WHERE id=1 AND scan_epoch=?;",
        label + " scan epoch reset prepare");
    sqlite_bind_u64_or_throw(update.stmt, 1, next_epoch, label);
    sqlite_bind_text_or_throw(
        update.stmt, 2, scan_seen_genesis_digest(next_epoch), label);
    sqlite_bind_u64_or_throw(update.stmt, 3, expected_scan_epoch, label);
    sqlite_step_done_or_throw(update.stmt, label + " scan epoch reset step");
    const FolderScanProgressHead staged =
        load_scan_progress_head_or_throw(db, limits, label + " staged");
    const FolderScanProgressHead expected{
        next_epoch, {}, 0U, 0U, scan_seen_genesis_digest(next_epoch)};
    if (staged != expected) {
        throw std::runtime_error(
            label + " staged scan epoch did not reset exactly");
    }
    transaction.commit();
    return staged;
}

void insert_genesis_scan_progress_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::uint64_t scan_epoch,
    const std::string& label) {
    if (scan_epoch == 0U || scan_epoch > kMaxPersistentInteger) {
        throw std::invalid_argument(
            label + " scan epoch is outside the persistent range");
    }
    SyncSqliteStmt insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_scan_progress("
        "id,scan_epoch,resume_after_path,seen_path_count,seen_path_bytes,"
        "seen_chain_digest) VALUES(1,?,'',0,0,?);",
        label + " scan-progress genesis prepare");
    sqlite_bind_u64_or_throw(insert.stmt, 1, scan_epoch, label);
    sqlite_bind_text_or_throw(
        insert.stmt, 2, scan_seen_genesis_digest(scan_epoch), label);
    sqlite_step_done_or_throw(
        insert.stmt, label + " scan-progress genesis step");
}

struct FolderRemoteWorkProgressHead final {
    std::string resume_after_path;
    std::string inspection_sweep_basis_digest;
    std::string inspection_sweep_started_after_path;
    std::uint64_t inspection_sweep_seen_path_count = 0U;
    bool inspection_sweep_had_unresolved_paths = false;

    bool operator==(const FolderRemoteWorkProgressHead&) const = default;
};

// Compact current-schema identity needed by the cross-owner terminal fence.
// A complete catalog snapshot is taken before the replica writer guard so the
// expensive entry/digest proof does not hold two SQLite writer capabilities at
// once. This head is then reloaded under BEGIN IMMEDIATE while the replica guard
// is live, proving that the already-attested snapshot is still the exact
// catalog authority at progress publication.
struct FolderCatalogCutpointHead final {
    std::uint64_t state_generation = 0U;
    std::uint64_t selection_absence_fence_generation = 0U;
    std::string catalog_digest;

    bool operator==(const FolderCatalogCutpointHead&) const = default;
};

[[nodiscard]] FolderCatalogCutpointHead
folder_catalog_cutpoint_head_or_throw(
    const SyncReplicaFolderCatalogSnapshot& snapshot,
    const std::string& label) {
    if (snapshot.state_generation > kMaxPersistentInteger ||
        snapshot.selective_sync_absence_fence_generation >
            kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(snapshot.catalog_digest)) {
        throw std::invalid_argument(
            label + " catalog cutpoint snapshot is invalid");
    }
    return {
        snapshot.state_generation,
        snapshot.selective_sync_absence_fence_generation,
        snapshot.catalog_digest};
}

[[nodiscard]] FolderCatalogCutpointHead
load_folder_catalog_cutpoint_head_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const std::string& label) {
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,"
        "selection_absence_fence_generation,catalog_digest "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1;",
        label + " catalog cutpoint prepare");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " catalog cutpoint step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " catalog cutpoint metadata row is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " catalog schema version");
    const std::string folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " catalog folder identity");
    const std::string root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, 16384U, label + " catalog root path");
    const std::string root_attestation_digest =
        sqlite_column_text_or_throw(
            meta.stmt, 3, 64U,
            label + " catalog root attestation digest");
    FolderCatalogCutpointHead head;
    head.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " catalog state generation");
    head.selection_absence_fence_generation =
        sqlite_column_u64_or_throw(
            meta.stmt, 5,
            label + " catalog selection absence fence generation");
    head.catalog_digest = sqlite_column_text_or_throw(
        meta.stmt, 6, 64U, label + " catalog digest");
    if (step_row_or_done_or_throw(
            meta.stmt,
            label + " catalog cutpoint trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " catalog cutpoint metadata identity is not unique");
    }
    if (schema_version != kSchemaVersion ||
        folder_id != expected_folder_id ||
        root_path != expected_root_path ||
        root_attestation_digest != expected_root_attestation_digest ||
        head.state_generation > kMaxPersistentInteger ||
        head.selection_absence_fence_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(root_attestation_digest) ||
        !is_lowercase_sha256_hex(head.catalog_digest)) {
        throw std::runtime_error(
            label + " catalog cutpoint identity is invalid");
    }
    return head;
}

void validate_remote_work_progress_path_or_throw(
    std::string_view canonical_path,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    if (canonical_path.empty()) return;
    validate_scan_progress_path_or_throw(
        canonical_path, limits, label + " remote-apply cursor");
}

void validate_remote_work_progress_head_or_throw(
    const FolderRemoteWorkProgressHead& head,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    validate_remote_work_progress_path_or_throw(
        head.resume_after_path, limits, label);
    validate_remote_work_progress_path_or_throw(
        head.inspection_sweep_started_after_path, limits,
        label + " inspection-sweep origin");
    if (head.inspection_sweep_basis_digest.empty()) {
        if (!head.inspection_sweep_started_after_path.empty() ||
            head.inspection_sweep_seen_path_count != 0U ||
            head.inspection_sweep_had_unresolved_paths) {
            throw std::runtime_error(
                label + " inactive remote inspection sweep retains state");
        }
        return;
    }
    if (!is_lowercase_sha256_hex(
            head.inspection_sweep_basis_digest) ||
        head.resume_after_path.empty() ||
        head.inspection_sweep_seen_path_count == 0U ||
        head.inspection_sweep_seen_path_count >
            limits.max_catalog_entries ||
        head.inspection_sweep_seen_path_count > kMaxPersistentInteger) {
        throw std::runtime_error(
            label + " remote inspection sweep state is invalid");
    }
}

[[nodiscard]] FolderRemoteWorkProgressHead
load_remote_work_progress_head_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    SyncSqliteStmt progress = sqlite_prepare_or_throw(
        db,
        "SELECT resume_after_path,inspection_sweep_basis_digest,"
        "inspection_sweep_started_after_path,"
        "inspection_sweep_seen_path_count,"
        "inspection_sweep_had_unresolved_paths FROM "
        "main.sync_replica_folder_catalog_remote_apply_progress WHERE id=1;",
        label + " remote-work progress prepare");
    if (step_row_or_done_or_throw(
            progress.stmt,
            label + " remote-work progress step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " remote-work progress singleton is missing");
    }
    FolderRemoteWorkProgressHead head;
    head.resume_after_path = sqlite_column_text_or_throw(
        progress.stmt, 0, 4096U, label + " remote-apply cursor");
    head.inspection_sweep_basis_digest = sqlite_column_text_or_throw(
        progress.stmt, 1, 64U,
        label + " remote inspection sweep basis");
    head.inspection_sweep_started_after_path = sqlite_column_text_or_throw(
        progress.stmt, 2, 4096U,
        label + " remote inspection sweep origin");
    head.inspection_sweep_seen_path_count = sqlite_column_u64_or_throw(
        progress.stmt, 3,
        label + " remote inspection sweep seen count");
    head.inspection_sweep_had_unresolved_paths =
        sqlite_column_u64_or_throw(
            progress.stmt, 4,
            label + " remote inspection sweep unresolved flag") != 0U;
    if (step_row_or_done_or_throw(
            progress.stmt,
            label + " remote-work progress trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " remote-work progress singleton is not unique");
    }
    validate_remote_work_progress_head_or_throw(head, limits, label);
    return head;
}

[[nodiscard]] SyncReplicaSelectiveSyncPolicy
replace_selective_sync_policy_in_transaction_or_throw(
    SyncSqliteDbHandleSlot& db,
    const FolderSelectiveSyncCutpoint& current,
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules,
    const std::string& label) {
    for (const SyncReplicaSelectiveSyncRule& rule : rules) {
        reject_reserved_internal_path_components_or_throw(
            rule.canonical_path, label + " selective-sync rule");
    }
    SyncReplicaSelectiveSyncPolicy candidate =
        make_sync_replica_selective_sync_policy_or_throw(
            default_mode, std::move(rules), current.policy.generation);
    if (sync_replica_selective_sync_policy_semantically_equal(
            candidate, current.policy)) {
        return current.policy;
    }
    if (current.policy.generation >= kMaxPersistentInteger) {
        throw std::overflow_error(
            label + " selective-sync generation is exhausted");
    }
    candidate = make_sync_replica_selective_sync_policy_or_throw(
        candidate.default_mode, std::move(candidate.rules),
        current.policy.generation + 1U);
    const bool retain_absence_fence =
        current.absence_inference_fence_generation != 0U ||
        sync_replica_selective_sync_policy_materializes_new_paths(
            current.policy, candidate);
    const std::uint64_t successor_absence_fence_generation =
        retain_absence_fence ? candidate.generation : 0U;

    sqlite_exec_or_throw(
        db,
        "DELETE FROM main.sync_replica_folder_catalog_selection_rules;",
        label + " selective-sync clear rules");
    SyncSqliteStmt insert_rule = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_selection_rules("
        "canonical_path,selection_mode) VALUES(?,?);",
        label + " selective-sync rule prepare");
    for (const SyncReplicaSelectiveSyncRule& rule : candidate.rules) {
        sqlite_bind_text_or_throw(
            insert_rule.stmt, 1, rule.canonical_path, label);
        sqlite_bind_u64_or_throw(
            insert_rule.stmt, 2,
            static_cast<std::uint64_t>(rule.mode), label);
        sqlite_step_done_or_throw(
            insert_rule.stmt, label + " selective-sync rule step");
        const int reset_result = sqlite3_reset(insert_rule.stmt);
        if (reset_result != SQLITE_OK) {
            throw_sqlite_exception(
                sqlite3_db_handle(insert_rule.stmt), reset_result,
                label + " selective-sync rule reset");
        }
        const int clear_result = sqlite3_clear_bindings(insert_rule.stmt);
        if (clear_result != SQLITE_OK) {
            throw_sqlite_exception(
                sqlite3_db_handle(insert_rule.stmt), clear_result,
                label + " selective-sync rule clear bindings");
        }
    }

    const std::string composed_digest = catalog_digest(
        current.content_catalog_digest, candidate);
    SyncSqliteStmt update_meta = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_meta SET "
        "selection_generation=?,selection_absence_fence_generation=?,"
        "selection_default_mode=?,selection_rule_count=?,"
        "selection_rule_path_bytes=?,selection_digest=?,catalog_digest=? "
        "WHERE id=1 AND "
        "selection_generation=? AND catalog_digest=?;",
        label + " selective-sync metadata prepare");
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 1, candidate.generation, label);
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 2, successor_absence_fence_generation, label);
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 3,
        static_cast<std::uint64_t>(candidate.default_mode), label);
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 4,
        static_cast<std::uint64_t>(candidate.rules.size()), label);
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 5, candidate.rule_path_bytes, label);
    sqlite_bind_text_or_throw(
        update_meta.stmt, 6, candidate.policy_digest, label);
    sqlite_bind_text_or_throw(
        update_meta.stmt, 7, composed_digest, label);
    sqlite_bind_u64_or_throw(
        update_meta.stmt, 8, current.policy.generation, label);
    sqlite_bind_text_or_throw(
        update_meta.stmt, 9, current.catalog_digest, label);
    sqlite_step_done_or_throw(
        update_meta.stmt, label + " selective-sync metadata step");

    // A changed selection invalidates both resumable scheduling frontiers. A
    // newly included lexical prefix must not wait for an old scan cursor to
    // wrap. Only an expansion opens (or an already-open transition carries)
    // the absence fence; pure exclusions cannot create new local-file absence
    // authority and therefore must not delay unrelated selected deletions.
    // Resetting only bounded journals leaves file/content catalog state untouched.
    const FolderScanProgressHead scan = load_scan_progress_head_or_throw(
        db, current.limits, label + " selective-sync scan head");
    const std::uint64_t next_scan_epoch =
        scan.scan_epoch == kMaxPersistentInteger
            ? 1U
            : scan.scan_epoch + 1U;
    sqlite_exec_or_throw(
        db,
        "DELETE FROM main.sync_replica_folder_catalog_scan_seen;",
        label + " selective-sync clear scan journal");
    SyncSqliteStmt reset_scan = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_scan_progress SET "
        "scan_epoch=?,resume_after_path='',seen_path_count=0,"
        "seen_path_bytes=0,seen_chain_digest=? WHERE id=1 AND scan_epoch=?;",
        label + " selective-sync reset scan prepare");
    sqlite_bind_u64_or_throw(
        reset_scan.stmt, 1, next_scan_epoch, label);
    sqlite_bind_text_or_throw(
        reset_scan.stmt, 2,
        scan_seen_genesis_digest(next_scan_epoch), label);
    sqlite_bind_u64_or_throw(
        reset_scan.stmt, 3, scan.scan_epoch, label);
    sqlite_step_done_or_throw(
        reset_scan.stmt, label + " selective-sync reset scan step");
    sqlite_exec_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_remote_apply_progress SET "
        "resume_after_path='',inspection_sweep_basis_digest='',"
        "inspection_sweep_started_after_path='',"
        "inspection_sweep_seen_path_count=0,"
        "inspection_sweep_had_unresolved_paths=0 WHERE id=1;",
        label + " selective-sync reset remote work");

    FolderSelectiveSyncCutpoint expected = current;
    expected.policy = candidate;
    expected.absence_inference_fence_generation =
        successor_absence_fence_generation;
    expected.catalog_digest = composed_digest;
    const FolderSelectiveSyncCutpoint staged =
        load_selective_sync_cutpoint_rows_or_throw(
            db, current.folder_id, current.absolute_root_path,
            current.root_attestation_digest,
            label + " selective-sync staged");
    if (staged != expected) {
        throw std::runtime_error(
            label + " selective-sync replacement changed content authority");
    }
    const FolderScanProgressHead staged_scan =
        load_scan_progress_head_or_throw(
            db, staged.limits, label + " selective-sync staged scan");
    const FolderRemoteWorkProgressHead staged_remote =
        load_remote_work_progress_head_or_throw(
            db, staged.limits, label + " selective-sync staged remote work");
    if (staged_scan != FolderScanProgressHead{
            next_scan_epoch, {}, 0U, 0U,
            scan_seen_genesis_digest(next_scan_epoch)} ||
        staged_remote != FolderRemoteWorkProgressHead{}) {
        throw std::runtime_error(
            label + " selective-sync replacement did not reset scheduling frontiers");
    }
    return candidate;
}

[[nodiscard]] std::string load_cyclic_remote_work_cursor_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& label) {
    SyncSqliteStmt progress = sqlite_prepare_or_throw(
        db,
        "SELECT resume_after_path FROM "
        "main.sync_replica_folder_catalog_remote_apply_progress WHERE id=1;",
        label + " cyclic remote-work progress prepare");
    if (step_row_or_done_or_throw(
            progress.stmt,
            label + " cyclic remote-work progress step") != SQLITE_ROW) {
        throw std::runtime_error(
            label + " cyclic remote-work progress singleton is missing");
    }
    std::string cursor = sqlite_column_text_or_throw(
        progress.stmt, 0, 4096U, label + " cyclic remote-work cursor");
    if (step_row_or_done_or_throw(
            progress.stmt,
            label + " cyclic remote-work trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " cyclic remote-work progress singleton is not unique");
    }
    validate_remote_work_progress_path_or_throw(cursor, limits, label);
    return cursor;
}

void insert_genesis_remote_work_progress_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    sqlite_exec_or_throw(
        db,
        "INSERT INTO "
        "main.sync_replica_folder_catalog_remote_apply_progress("
        "id,resume_after_path,inspection_sweep_basis_digest,"
        "inspection_sweep_started_after_path,"
        "inspection_sweep_seen_path_count,"
        "inspection_sweep_had_unresolved_paths) "
        "VALUES(1,'','','',0,0);",
        label + " remote-work progress genesis");
}

[[nodiscard]] std::optional<FolderRemoteWorkProgressHead>
publish_remote_work_progress_at_catalog_cutpoint_or_none(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const FolderCatalogCutpointHead& expected_catalog_cutpoint,
    const FolderScanProgressHead& expected_scan_progress,
    const FolderRemoteWorkProgressHead& expected,
    const FolderRemoteWorkProgressHead& wanted,
    std::optional<std::uint64_t>
        clear_selection_absence_fence_generation,
    const std::string& label) {
    if (expected_catalog_cutpoint.state_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(
            expected_catalog_cutpoint.catalog_digest)) {
        throw std::invalid_argument(
            label + " expected catalog cutpoint is invalid");
    }
    if (clear_selection_absence_fence_generation.has_value() &&
        (*clear_selection_absence_fence_generation == 0U ||
         expected_catalog_cutpoint.selection_absence_fence_generation !=
             *clear_selection_absence_fence_generation)) {
        throw std::invalid_argument(
            label + " selection absence fence clear request is invalid");
    }
    validate_remote_work_progress_head_or_throw(
        expected, limits, label + " expected");
    validate_remote_work_progress_head_or_throw(
        wanted, limits, label + " wanted");

    SyncSqliteTransaction transaction(
        db, label + " remote-work progress publication",
        SyncSqliteTransactionMode::Immediate);
    const FolderCatalogCutpointHead current_catalog_cutpoint =
        load_folder_catalog_cutpoint_head_or_throw(
            db, expected_folder_id, expected_root_path,
            expected_root_attestation_digest, label + " current");
    const FolderScanProgressHead current_scan_progress =
        load_scan_progress_head_or_throw(
            db, limits, label + " current scan progress");
    const FolderRemoteWorkProgressHead current =
        load_remote_work_progress_head_or_throw(
            db, limits, label + " current");
    if (current_catalog_cutpoint != expected_catalog_cutpoint ||
        current_scan_progress != expected_scan_progress ||
        current != expected) {
        transaction.commit();
        return std::nullopt;
    }

    if (wanted != expected) {
        SyncSqliteStmt update = sqlite_prepare_or_throw(
            db,
            "UPDATE "
            "main.sync_replica_folder_catalog_remote_apply_progress SET "
            "resume_after_path=?,inspection_sweep_basis_digest=?,"
            "inspection_sweep_started_after_path=?,"
            "inspection_sweep_seen_path_count=?,"
            "inspection_sweep_had_unresolved_paths=? WHERE id=1 AND "
            "resume_after_path=? AND inspection_sweep_basis_digest=? AND "
            "inspection_sweep_started_after_path=? AND "
            "inspection_sweep_seen_path_count=? AND "
            "inspection_sweep_had_unresolved_paths=?;",
            label + " remote-work progress update prepare");
        sqlite_bind_text_or_throw(
            update.stmt, 1, wanted.resume_after_path, label);
        sqlite_bind_text_or_throw(
            update.stmt, 2, wanted.inspection_sweep_basis_digest, label);
        sqlite_bind_text_or_throw(
            update.stmt, 3, wanted.inspection_sweep_started_after_path, label);
        sqlite_bind_u64_or_throw(
            update.stmt, 4, wanted.inspection_sweep_seen_path_count, label);
        sqlite_bind_u64_or_throw(
            update.stmt, 5,
            wanted.inspection_sweep_had_unresolved_paths ? 1U : 0U, label);
        sqlite_bind_text_or_throw(
            update.stmt, 6, expected.resume_after_path, label);
        sqlite_bind_text_or_throw(
            update.stmt, 7, expected.inspection_sweep_basis_digest, label);
        sqlite_bind_text_or_throw(
            update.stmt, 8, expected.inspection_sweep_started_after_path,
            label);
        sqlite_bind_u64_or_throw(
            update.stmt, 9, expected.inspection_sweep_seen_path_count, label);
        sqlite_bind_u64_or_throw(
            update.stmt, 10,
            expected.inspection_sweep_had_unresolved_paths ? 1U : 0U,
            label);
        sqlite_step_done_or_throw(
            update.stmt, label + " remote-work progress update step");
    }

    FolderCatalogCutpointHead wanted_catalog_cutpoint =
        expected_catalog_cutpoint;
    if (clear_selection_absence_fence_generation.has_value()) {
        SyncSqliteStmt clear_fence = sqlite_prepare_or_throw(
            db,
            "UPDATE main.sync_replica_folder_catalog_meta SET "
            "selection_absence_fence_generation=0 WHERE id=1 AND "
            "selection_generation=? AND "
            "selection_absence_fence_generation=?;",
            label + " selection absence fence clear prepare");
        sqlite_bind_u64_or_throw(
            clear_fence.stmt, 1,
            *clear_selection_absence_fence_generation, label);
        sqlite_bind_u64_or_throw(
            clear_fence.stmt, 2,
            *clear_selection_absence_fence_generation, label);
        sqlite_step_done_or_throw(
            clear_fence.stmt,
            label + " selection absence fence clear step");
        if (sqlite3_changes(sqlite3_db_handle(clear_fence.stmt)) != 1) {
            throw std::runtime_error(
                label + " selection absence fence did not clear exactly");
        }
        wanted_catalog_cutpoint.selection_absence_fence_generation = 0U;
    }

    const FolderCatalogCutpointHead staged_catalog_cutpoint =
        load_folder_catalog_cutpoint_head_or_throw(
            db, expected_folder_id, expected_root_path,
            expected_root_attestation_digest,
            label + " staged catalog cutpoint");
    if (staged_catalog_cutpoint != wanted_catalog_cutpoint) {
        throw std::runtime_error(
            label + " staged catalog cutpoint did not publish exactly");
    }

    const FolderRemoteWorkProgressHead staged =
        load_remote_work_progress_head_or_throw(
            db, limits, label + " staged");
    if (staged != wanted) {
        throw std::runtime_error(
            label + " staged remote-work progress did not publish exactly");
    }
    transaction.commit();
    return staged;
}

// Establishes one terminal cross-owner observation. The replica guard is
// acquired first and kept live while the catalog writer transaction verifies
// the exact pre-attested catalog, authenticated local scan head, and remote
// progress head. This prevents a completed sweep from being published against
// an older visible projection while still keeping the expensive full-state
// proof outside the short two-database writer overlap.
[[nodiscard]] std::optional<FolderRemoteWorkProgressHead>
publish_remote_work_progress_at_terminal_cutpoint_or_none(
    SyncReplicaSqliteOwner& replica_owner,
    const std::string& expected_visible_state_digest,
    SyncSqliteDbHandleSlot& catalog_db,
    const SyncReplicaFolderScanLimits& limits,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& expected_root_attestation_digest,
    const FolderCatalogCutpointHead& expected_catalog_cutpoint,
    const FolderScanProgressHead& expected_scan_progress,
    const FolderRemoteWorkProgressHead& expected_remote_work_progress,
    const FolderRemoteWorkProgressHead& wanted_remote_work_progress,
    std::optional<std::uint64_t>
        clear_selection_absence_fence_generation,
    const std::string& label) {
    std::unique_ptr<SyncReplicaSqliteProjectionGuard> replica_guard =
        replica_owner.guard_visible_state_at_digest_or_throw(
            expected_visible_state_digest);
    if (!replica_guard) return std::nullopt;

    std::optional<FolderRemoteWorkProgressHead> published =
        publish_remote_work_progress_at_catalog_cutpoint_or_none(
            catalog_db, limits, expected_folder_id, expected_root_path,
            expected_root_attestation_digest, expected_catalog_cutpoint,
            expected_scan_progress, expected_remote_work_progress,
            wanted_remote_work_progress,
            clear_selection_absence_fence_generation, label);
    if (!published.has_value()) return std::nullopt;

    replica_guard->commit_or_throw();
    return published;
}

void migrate_legacy_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot legacy =
        load_legacy_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " legacy proof", detached_binding);

    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v1;"
        "ALTER TABLE main.sync_replica_folder_catalog_entries "
        "RENAME TO sync_replica_folder_catalog_entries_v1;",
        label + " legacy table rename");
    for (const auto& definition : kPreselectionSchema) {
        sqlite_exec_or_throw(
            db, std::string(definition.sql),
            label + " create " + std::string(definition.name));
    }

    const std::string migrated_digest = preselection_catalog_digest(
        legacy.folder_id, legacy.absolute_root_path,
        legacy.root_attestation_digest, legacy.limits,
        legacy.state_generation, legacy.entries);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest)"
        "SELECT id,5,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM main.sync_replica_folder_catalog_meta_v1 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, migrated_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");
    sqlite_exec_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_entries("
        "canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation) "
        "SELECT canonical_path,1,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries_v1 "
        "ORDER BY canonical_path;",
        label + " migrate legacy entries");
    insert_genesis_scan_progress_or_throw(db, 1U, label);
    insert_genesis_remote_work_progress_or_throw(db, label);
    sqlite_exec_or_throw(
        db,
        "DROP TABLE main.sync_replica_folder_catalog_entries_v1;"
        "DROP TABLE main.sync_replica_folder_catalog_meta_v1;",
        label + " retire legacy tables");

    const SyncReplicaFolderCatalogSnapshot migrated =
        load_preselection_catalog_or_throw(
        db, folder_id, root_path, root_attestation_digest,
        deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = legacy;
    expected.content_catalog_digest = migrated_digest;
    expected.catalog_digest = migrated_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed legacy authority");
    }
}

void migrate_previous_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot previous =
        load_previous_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " v2 proof", detached_binding);

    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v2;"
        "ALTER TABLE main.sync_replica_folder_catalog_entries "
        "RENAME TO sync_replica_folder_catalog_entries_v2;",
        label + " v2 table rename");
    for (const auto& definition : kPreselectionSchema) {
        sqlite_exec_or_throw(
            db, std::string(definition.sql),
            label + " create " + std::string(definition.name));
    }

    const std::string migrated_digest = preselection_catalog_digest(
        previous.folder_id, previous.absolute_root_path,
        previous.root_attestation_digest, previous.limits,
        previous.state_generation, previous.entries);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest)"
        "SELECT id,5,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM main.sync_replica_folder_catalog_meta_v2 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, migrated_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");
    sqlite_exec_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_entries("
        "canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation) "
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,"
        "operation_id,source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries_v2 "
        "ORDER BY canonical_path;",
        label + " migrate v2 entries");
    insert_genesis_scan_progress_or_throw(db, 1U, label);
    insert_genesis_remote_work_progress_or_throw(db, label);
    sqlite_exec_or_throw(
        db,
        "DROP TABLE main.sync_replica_folder_catalog_entries_v2;"
        "DROP TABLE main.sync_replica_folder_catalog_meta_v2;",
        label + " retire v2 tables");

    const SyncReplicaFolderCatalogSnapshot migrated =
        load_preselection_catalog_or_throw(
        db, folder_id, root_path, root_attestation_digest,
        deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = previous;
    expected.content_catalog_digest = migrated_digest;
    expected.catalog_digest = migrated_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed v2 authority");
    }
}

void migrate_fair_scan_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot fair_scan =
        load_fair_scan_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " v3 proof", detached_binding);
    const FolderScanProgressHead retained_scan_progress =
        load_scan_progress_head_or_throw(
            db, fair_scan.limits, label + " v3 scan-progress proof");

    // The v3 entries and authenticated scan journal already have their final
    // representation. Rename only metadata, add the independent scheduling
    // singleton, and change the catalog digest domain. This avoids copying a
    // potentially large journal merely to add state that authorizes no content.
    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v3;",
        label + " v3 metadata rename");
    sqlite_exec_or_throw(
        db, std::string(kPreselectionMetaSchemaSql),
        label + " create v5 metadata");
    sqlite_exec_or_throw(
        db, std::string(kRemoteApplyProgressSchemaSql),
        label + " create remote-apply progress");

    const std::string migrated_digest = preselection_catalog_digest(
        fair_scan.folder_id, fair_scan.absolute_root_path,
        fair_scan.root_attestation_digest, fair_scan.limits,
        fair_scan.state_generation, fair_scan.entries);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest)"
        "SELECT id,5,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM main.sync_replica_folder_catalog_meta_v3 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, migrated_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");
    insert_genesis_remote_work_progress_or_throw(db, label);
    sqlite_exec_or_throw(
        db,
        "DROP TABLE main.sync_replica_folder_catalog_meta_v3;",
        label + " retire v3 metadata");

    const SyncReplicaFolderCatalogSnapshot migrated =
        load_preselection_catalog_or_throw(
        db, folder_id, root_path, root_attestation_digest,
        deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = fair_scan;
    expected.content_catalog_digest = migrated_digest;
    expected.catalog_digest = migrated_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed v3 authority");
    }
    const FolderScanProgressHead migrated_scan_progress =
        load_scan_progress_head_or_throw(
            db, migrated.limits, label + " migrated scan-progress proof");
    if (migrated_scan_progress != retained_scan_progress) {
        throw std::runtime_error(
            label + " migration changed authenticated scan continuation");
    }
    const FolderRemoteWorkProgressHead remote_work_progress =
        load_remote_work_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated remote-apply progress proof");
    if (remote_work_progress != FolderRemoteWorkProgressHead{}) {
        throw std::runtime_error(
            label + " migrated remote-work progress is not genesis");
    }
}

void migrate_cyclic_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot cyclic =
        load_cyclic_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " v4 proof", detached_binding);
    const FolderScanProgressHead retained_scan_progress =
        load_scan_progress_head_or_throw(
            db, cyclic.limits, label + " v4 scan-progress proof");
    const std::string retained_remote_work_cursor =
        load_cyclic_remote_work_cursor_or_throw(
            db, cyclic.limits, label + " v4 remote-work proof");

    // The content catalog and authenticated local scan journal already have
    // their final representation. Replace only metadata and the scheduling
    // singleton so the proven v4 cursor survives while the cutpoint-bound
    // inspection sweep begins conservatively at genesis.
    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v4;"
        "ALTER TABLE main.sync_replica_folder_catalog_remote_apply_progress "
        "RENAME TO sync_replica_folder_catalog_remote_apply_progress_v4;",
        label + " v4 scheduling table rename");
    sqlite_exec_or_throw(
        db, std::string(kPreselectionMetaSchemaSql),
        label + " create v5 metadata");
    sqlite_exec_or_throw(
        db, std::string(kRemoteApplyProgressSchemaSql),
        label + " create v5 remote-work progress");

    const std::string migrated_digest = preselection_catalog_digest(
        cyclic.folder_id, cyclic.absolute_root_path,
        cyclic.root_attestation_digest, cyclic.limits,
        cyclic.state_generation, cyclic.entries);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest)"
        "SELECT id,5,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM main.sync_replica_folder_catalog_meta_v4 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, migrated_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");

    SyncSqliteStmt insert_progress = sqlite_prepare_or_throw(
        db,
        "INSERT INTO "
        "main.sync_replica_folder_catalog_remote_apply_progress("
        "id,resume_after_path,inspection_sweep_basis_digest,"
        "inspection_sweep_started_after_path,"
        "inspection_sweep_seen_path_count,"
        "inspection_sweep_had_unresolved_paths) "
        "VALUES(1,?,'','',0,0);",
        label + " migrated remote-work progress prepare");
    sqlite_bind_text_or_throw(
        insert_progress.stmt, 1, retained_remote_work_cursor, label);
    sqlite_step_done_or_throw(
        insert_progress.stmt,
        label + " migrated remote-work progress step");

    sqlite_exec_or_throw(
        db,
        "DROP TABLE "
        "main.sync_replica_folder_catalog_remote_apply_progress_v4;"
        "DROP TABLE main.sync_replica_folder_catalog_meta_v4;",
        label + " retire v4 scheduling tables");

    const SyncReplicaFolderCatalogSnapshot migrated =
        load_preselection_catalog_or_throw(
        db, folder_id, root_path, root_attestation_digest,
        deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = cyclic;
    expected.content_catalog_digest = migrated_digest;
    expected.catalog_digest = migrated_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed v4 authority");
    }
    const FolderScanProgressHead migrated_scan_progress =
        load_scan_progress_head_or_throw(
            db, migrated.limits, label + " migrated scan-progress proof");
    if (migrated_scan_progress != retained_scan_progress) {
        throw std::runtime_error(
            label + " migration changed authenticated scan continuation");
    }
    const FolderRemoteWorkProgressHead migrated_remote_work =
        load_remote_work_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated remote-work progress proof");
    if (migrated_remote_work.resume_after_path !=
            retained_remote_work_cursor ||
        !migrated_remote_work.inspection_sweep_basis_digest.empty() ||
        !migrated_remote_work.inspection_sweep_started_after_path.empty() ||
        migrated_remote_work.inspection_sweep_seen_path_count != 0U ||
        migrated_remote_work.inspection_sweep_had_unresolved_paths) {
        throw std::runtime_error(
            label + " migration changed the v4 remote-work cursor");
    }
}

void migrate_preselection_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot preselection =
        load_preselection_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " v5 proof", detached_binding);
    const FolderScanProgressHead retained_scan_progress =
        load_scan_progress_head_or_throw(
            db, preselection.limits,
            label + " v5 scan-progress proof");
    const FolderRemoteWorkProgressHead retained_remote_work =
        load_remote_work_progress_head_or_throw(
            db, preselection.limits,
            label + " v5 remote-work proof");

    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v5;",
        label + " v5 metadata rename");
    sqlite_exec_or_throw(
        db, std::string(kSelectiveSyncMetaSchemaSql),
        label + " create v6 metadata");
    sqlite_exec_or_throw(
        db, std::string(kSelectionRulesSchemaSql),
        label + " create selective-sync rules");

    const SyncReplicaSelectiveSyncPolicy policy =
        sync_replica_default_selective_sync_policy();
    const std::string composed_digest = selective_sync_catalog_digest(
        preselection.catalog_digest, policy);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,content_catalog_digest,selection_generation,"
        "selection_absence_fence_generation,selection_default_mode,"
        "selection_rule_count,"
        "selection_rule_path_bytes,selection_digest,catalog_digest) "
        "SELECT id,6,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,catalog_digest,"
        "?, 0, ?, 0, 0, ?, ? FROM "
        "main.sync_replica_folder_catalog_meta_v5 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_u64_or_throw(
        insert_meta.stmt, 1, policy.generation, label);
    sqlite_bind_u64_or_throw(
        insert_meta.stmt, 2,
        static_cast<std::uint64_t>(policy.default_mode), label);
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 3, policy.policy_digest, label);
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 4, composed_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");
    sqlite_exec_or_throw(
        db,
        "DROP TABLE main.sync_replica_folder_catalog_meta_v5;",
        label + " retire v5 metadata");

    const SyncReplicaFolderCatalogSnapshot migrated =
        load_selective_sync_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = preselection;
    expected.content_catalog_digest = preselection.catalog_digest;
    expected.selective_sync_policy = policy;
    expected.catalog_digest = composed_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed v5 content authority");
    }
    if (load_scan_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated scan-progress proof") !=
            retained_scan_progress ||
        load_remote_work_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated remote-work proof") !=
            retained_remote_work) {
        throw std::runtime_error(
            label + " migration changed scheduling authority");
    }
}


void migrate_selective_sync_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label,
    bool detached_binding) {
    const SyncReplicaFolderCatalogSnapshot selective =
        load_selective_sync_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label + " v6 proof", detached_binding);
    const FolderScanProgressHead retained_scan_progress =
        load_scan_progress_head_or_throw(
            db, selective.limits, label + " v6 scan-progress proof");
    const FolderRemoteWorkProgressHead retained_remote_work =
        load_remote_work_progress_head_or_throw(
            db, selective.limits, label + " v6 remote-work proof");

    sqlite_exec_or_throw(
        db,
        "ALTER TABLE main.sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v6;",
        label + " v6 metadata rename");
    sqlite_exec_or_throw(
        db, std::string(kMetaSchemaSql), label + " create v7 metadata");
    sqlite_exec_or_throw(
        db, std::string(kEntriesFileContentIndexSchemaSql),
        label + " create file-content index");

    const std::string composed_digest = catalog_digest(
        selective.content_catalog_digest, selective.selective_sync_policy);
    SyncSqliteStmt insert_meta = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,content_catalog_digest,selection_generation,"
        "selection_absence_fence_generation,selection_default_mode,"
        "selection_rule_count,selection_rule_path_bytes,selection_digest,"
        "catalog_digest) "
        "SELECT id,7,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,"
        "content_catalog_digest,selection_generation,"
        "selection_absence_fence_generation,selection_default_mode,"
        "selection_rule_count,selection_rule_path_bytes,selection_digest,? "
        "FROM main.sync_replica_folder_catalog_meta_v6 WHERE id=1;",
        label + " migrated metadata prepare");
    sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, composed_digest, label);
    sqlite_step_done_or_throw(
        insert_meta.stmt, label + " migrated metadata step");
    sqlite_exec_or_throw(
        db,
        "DROP TABLE main.sync_replica_folder_catalog_meta_v6;",
        label + " retire v6 metadata");

    const SyncReplicaFolderCatalogSnapshot migrated = load_catalog_or_throw(
        db, folder_id, root_path, root_attestation_digest,
        deployment_binding, label + " migrated proof", detached_binding);
    SyncReplicaFolderCatalogSnapshot expected = selective;
    expected.catalog_digest = composed_digest;
    if (migrated != expected) {
        throw std::runtime_error(
            label + " migrated catalog changed v6 content or selection authority");
    }
    if (load_scan_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated scan-progress proof") !=
            retained_scan_progress ||
        load_remote_work_progress_head_or_throw(
            db, migrated.limits,
            label + " migrated remote-work proof") !=
            retained_remote_work) {
        throw std::runtime_error(
            label + " migration changed scheduling authority");
    }
}

void initialize_or_attest_catalog_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaFolderScanLimits& initial_limits,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    SyncReplicaFolderCatalogOpenDisposition disposition,
    const std::string& label,
    bool detached_binding = false) {
    switch (disposition) {
        case SyncReplicaFolderCatalogOpenDisposition::ExistingOnly:
        case SyncReplicaFolderCatalogOpenDisposition::CreateIfMissing:
            break;
        default:
            throw std::invalid_argument(
                label + " catalog open disposition is invalid");
    }

    const bool binding_exists = sqlite_table_exists_or_throw(
        db, "anonsync_store_set_binding",
        label + " deployment-binding presence");
    if (detached_binding && deployment_binding == nullptr) {
        throw std::logic_error(
            label + " detached catalog binding is absent");
    }
    if (deployment_binding != nullptr) {
        if (detached_binding) {
            if (!binding_exists) {
                throw std::runtime_error(
                    label + " detached catalog image has no deployment binding");
            }
            attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
                db, *deployment_binding,
                label + " detached deployment binding");
        } else if (!binding_exists) {
            if (disposition ==
                SyncReplicaFolderCatalogOpenDisposition::ExistingOnly) {
                throw std::runtime_error(
                    label + " product-bound catalog requires explicit "
                            "bootstrap");
            }
            if (total_user_schema_object_count_or_throw(db, label) != 0U) {
                throw std::runtime_error(
                    label + " catalog database contains unbound schema");
            }
            initialize_sync_replica_sqlite_deployment_binding_or_throw(
                db, *deployment_binding,
                label + " deployment binding initialization");
        } else {
            attest_sync_replica_sqlite_deployment_binding_state_or_throw(
                db, *deployment_binding, label + " deployment binding");
        }
    } else if (binding_exists) {
        throw std::runtime_error(
            label + " standalone catalog cannot adopt a product binding");
    }

    SyncSqliteTransaction transaction(
        db, label + " schema initialization",
        SyncSqliteTransactionMode::Immediate);
    const std::uint64_t existing =
        own_schema_object_count_or_throw(db, label, false);
    if (existing == 0U) {
        if (disposition ==
            SyncReplicaFolderCatalogOpenDisposition::ExistingOnly) {
            throw std::runtime_error(
                label + " catalog schema requires explicit bootstrap");
        }
        const std::uint64_t expected_existing =
            deployment_binding != nullptr ? 1U : 0U;
        if (total_user_schema_object_count_or_throw(db, label) !=
            expected_existing) {
            throw std::runtime_error(
                label + " catalog database is not dedicated and empty");
        }
        for (const auto& definition : kSchema) {
            sqlite_exec_or_throw(
                db, std::string(definition.sql),
                label + " create " + std::string(definition.name));
        }
        const std::vector<SyncReplicaFolderCatalogEntry> empty;
        const SyncReplicaSelectiveSyncPolicy policy =
            sync_replica_default_selective_sync_policy();
        const std::string content_digest = preselection_catalog_digest(
            folder_id, root_path, root_attestation_digest,
            initial_limits, 0U, empty);
        const std::string digest = catalog_digest(content_digest, policy);
        SyncSqliteStmt insert = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_replica_folder_catalog_meta("
            "id,schema_version,folder_id,absolute_root_path,"
            "root_attestation_digest,state_generation,max_catalog_entries,"
            "max_catalog_path_bytes,max_payload_bytes,entry_count,"
            "catalog_path_bytes,content_catalog_digest,selection_generation,"
            "selection_absence_fence_generation,selection_default_mode,"
            "selection_rule_count,"
            "selection_rule_path_bytes,selection_digest,catalog_digest)"
            "VALUES(1,7,?,?,?,0,?,?,?,0,0,?,?,0,?,0,0,?,?);",
            label + " initialize metadata prepare");
        sqlite_bind_text_or_throw(insert.stmt, 1, folder_id, label);
        sqlite_bind_text_or_throw(insert.stmt, 2, root_path, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 3, root_attestation_digest, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 4, initial_limits.max_catalog_entries, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 5, initial_limits.max_catalog_path_bytes, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 6, initial_limits.max_payload_bytes, label);
        sqlite_bind_text_or_throw(insert.stmt, 7, content_digest, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 8, policy.generation, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 9,
            static_cast<std::uint64_t>(policy.default_mode), label);
        sqlite_bind_text_or_throw(
            insert.stmt, 10, policy.policy_digest, label);
        sqlite_bind_text_or_throw(insert.stmt, 11, digest, label);
        sqlite_step_done_or_throw(
            insert.stmt, label + " initialize metadata step");
        insert_genesis_scan_progress_or_throw(db, 1U, label);
        insert_genesis_remote_work_progress_or_throw(db, label);
    } else {
        std::uint64_t version = catalog_schema_version_or_throw(
            db, label + " existing catalog");
        if (version == kLegacySchemaVersion) {
            migrate_legacy_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v1 to v5 migration",
                detached_binding);
        } else if (version == kPreviousSchemaVersion) {
            migrate_previous_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v2 to v5 migration",
                detached_binding);
        } else if (version == kFairScanSchemaVersion) {
            migrate_fair_scan_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v3 to v5 migration",
                detached_binding);
        } else if (version == kCyclicSchemaVersion) {
            migrate_cyclic_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v4 to v5 migration",
                detached_binding);
        } else if (version != kPreselectionSchemaVersion &&
                   version != kSelectiveSyncSchemaVersion &&
                   version != kSchemaVersion) {
            throw std::runtime_error(
                label + " catalog schema version is unsupported");
        }
        if (version <= kPreselectionSchemaVersion) {
            migrate_preselection_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v5 to v6 migration",
                detached_binding);
            version = kSelectiveSyncSchemaVersion;
        }
        if (version == kSelectiveSyncSchemaVersion) {
            migrate_selective_sync_catalog_or_throw(
                db, folder_id, root_path, root_attestation_digest,
                deployment_binding, label + " catalog v6 to v7 migration",
                detached_binding);
        }
    }
    const SyncReplicaFolderCatalogSnapshot initialized =
        load_catalog_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            deployment_binding, label, detached_binding);
    (void)load_scan_progress_head_or_throw(
        db, initialized.limits, label + " scan-progress proof");
    (void)load_remote_work_progress_head_or_throw(
        db, initialized.limits, label + " remote-apply progress proof");
    transaction.commit();
}

[[nodiscard]] std::optional<SyncReplicaFolderCatalogEntry>
find_catalog_entry(
    const SyncReplicaFolderCatalogSnapshot& snapshot,
    std::string_view canonical_path) {
    const auto found = std::lower_bound(
        snapshot.entries.begin(), snapshot.entries.end(), canonical_path,
        [](const SyncReplicaFolderCatalogEntry& entry,
           std::string_view path) {
            return entry.canonical_path < path;
        });
    if (found == snapshot.entries.end() ||
        found->canonical_path != canonical_path) {
        return std::nullopt;
    }
    return *found;
}

struct CatalogRecordResult final {
    SyncReplicaFolderCatalogEntry entry;
    bool changed = false;
};

[[nodiscard]] bool same_catalog_entry_without_generation(
    const SyncReplicaFolderCatalogEntry& left,
    const SyncReplicaFolderCatalogEntry& right) noexcept {
    return left.canonical_path == right.canonical_path &&
           left.kind == right.kind &&
           left.size_bytes == right.size_bytes &&
           left.content_sha256 == right.content_sha256 &&
           left.operation_id == right.operation_id &&
           left.source_snapshot_sha256 == right.source_snapshot_sha256;
}

void upsert_catalog_entry_row_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderCatalogEntry& entry,
    const std::string& label) {
    SyncSqliteStmt upsert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_folder_catalog_entries("
        "canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation)"
        "VALUES(?,?,?,?,?,?,?) ON CONFLICT(canonical_path) DO UPDATE SET "
        "value_kind=excluded.value_kind,"
        "size_bytes=excluded.size_bytes,"
        "content_sha256=excluded.content_sha256,"
        "operation_id=excluded.operation_id,"
        "source_snapshot_sha256=excluded.source_snapshot_sha256,"
        "last_seen_generation=excluded.last_seen_generation;",
        label + " entry upsert prepare");
    sqlite_bind_text_or_throw(
        upsert.stmt, 1, entry.canonical_path, label);
    sqlite_bind_u64_or_throw(
        upsert.stmt, 2,
        catalog_value_kind_integer_or_throw(entry.kind, label), label);
    sqlite_bind_u64_or_throw(upsert.stmt, 3, entry.size_bytes, label);
    sqlite_bind_text_or_throw(
        upsert.stmt, 4, entry.content_sha256, label);
    sqlite_bind_text_or_throw(
        upsert.stmt, 5, entry.operation_id, label);
    sqlite_bind_text_or_throw(
        upsert.stmt, 6, entry.source_snapshot_sha256, label);
    sqlite_bind_u64_or_throw(
        upsert.stmt, 7, entry.last_seen_generation, label);
    sqlite_step_done_or_throw(upsert.stmt, label + " entry upsert step");
}


struct StreamedCatalogContentProof final {
    std::uint64_t entry_count = 0U;
    std::uint64_t catalog_path_bytes = 0U;
    std::string content_catalog_digest;

    bool operator==(const StreamedCatalogContentProof&) const = default;
};

[[nodiscard]] StreamedCatalogContentProof
stream_catalog_content_proof_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view folder_id,
    std::string_view root_path,
    std::string_view root_attestation_digest,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    std::uint64_t expected_entry_count,
    std::uint64_t expected_catalog_path_bytes,
    const std::string& label) {
    validate_sync_replica_folder_scan_limits_or_throw(limits);
    if (state_generation > kMaxPersistentInteger ||
        expected_entry_count > limits.max_catalog_entries ||
        expected_catalog_path_bytes > limits.max_catalog_path_bytes ||
        !is_lowercase_sha256_hex(root_attestation_digest)) {
        throw std::runtime_error(label + " catalog proof metadata is invalid");
    }

    Sha256DigestBuilder digest;
    append_string(digest, kPreselectionCatalogDigestDomain);
    append_u64(digest, kPreselectionSchemaVersion);
    append_string(digest, folder_id);
    append_string(digest, root_path);
    append_string(digest, root_attestation_digest);
    append_u64(digest, limits.max_catalog_entries);
    append_u64(digest, limits.max_catalog_path_bytes);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, state_generation);
    append_u64(digest, expected_entry_count);

    SyncSqliteStmt rows = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,"
        "operation_id,source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries "
        "ORDER BY canonical_path;",
        label + " rows prepare");
    StreamedCatalogContentProof proof;
    std::string previous_path;
    for (;;) {
        const int step = step_row_or_done_or_throw(
            rows.stmt, label + " rows step");
        if (step == SQLITE_DONE) break;
        SyncReplicaFolderCatalogEntry entry =
            load_modern_catalog_entry_row_or_throw(
                rows.stmt, limits, state_generation, label + " row");
        if (!previous_path.empty() &&
            previous_path >= entry.canonical_path) {
            throw std::runtime_error(
                label + " catalog row order is not canonical");
        }
        previous_path = entry.canonical_path;
        proof.entry_count = increment_or_throw(
            proof.entry_count, label + " entry count");
        proof.catalog_path_bytes = add_or_throw(
            proof.catalog_path_bytes,
            static_cast<std::uint64_t>(entry.canonical_path.size()),
            label + " path bytes");
        if (proof.entry_count > expected_entry_count ||
            proof.catalog_path_bytes > expected_catalog_path_bytes) {
            throw std::runtime_error(
                label + " catalog rows exceed their metadata cutpoint");
        }
        append_string(digest, entry.canonical_path);
        append_u64(
            digest,
            catalog_value_kind_integer_or_throw(
                entry.kind, label + " row kind"));
        append_u64(digest, entry.size_bytes);
        append_string(digest, entry.content_sha256);
        append_string(digest, entry.operation_id);
        append_string(digest, entry.source_snapshot_sha256);
        append_u64(digest, entry.last_seen_generation);
    }
    if (proof.entry_count != expected_entry_count ||
        proof.catalog_path_bytes != expected_catalog_path_bytes) {
        throw std::runtime_error(
            label + " catalog rows do not match their metadata cutpoint");
    }
    proof.content_catalog_digest = digest.finish_hex();
    return proof;
}

[[nodiscard]] std::optional<SyncReplicaFolderCatalogEntry>
load_exact_catalog_entry_row_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaFolderScanLimits& limits,
    std::uint64_t state_generation,
    const std::string& canonical_path,
    const std::string& label) {
    SyncSqliteStmt row = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,"
        "operation_id,source_snapshot_sha256,last_seen_generation "
        "FROM main.sync_replica_folder_catalog_entries "
        "WHERE canonical_path=?;",
        label + " prepare");
    sqlite_bind_text_or_throw(row.stmt, 1, canonical_path, label);
    const int step = step_row_or_done_or_throw(row.stmt, label + " step");
    if (step == SQLITE_DONE) return std::nullopt;
    SyncReplicaFolderCatalogEntry entry =
        load_modern_catalog_entry_row_or_throw(
            row.stmt, limits, state_generation, label);
    if (entry.canonical_path != canonical_path ||
        step_row_or_done_or_throw(row.stmt, label + " trailing step") !=
            SQLITE_DONE) {
        throw std::runtime_error(
            label + " exact catalog path is not unique");
    }
    return entry;
}

void attest_catalog_mutation_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::string& label) {
    if (deployment_binding != nullptr) {
        attest_sync_replica_sqlite_deployment_binding_state_or_throw(
            db, *deployment_binding, label + " deployment binding");
    }
    attest_schema_or_throw(
        db, deployment_binding != nullptr, label + " schema");
}

[[nodiscard]] CatalogRecordResult record_catalog_entry_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const std::optional<SyncReplicaFolderCatalogEntry>& expected_current,
    SyncReplicaFolderCatalogEntry entry,
    const std::string& label) {
    SyncSqliteTransaction transaction(
        db, label + " catalog publication",
        SyncSqliteTransactionMode::Immediate);
    attest_catalog_mutation_schema_or_throw(
        db, deployment_binding, label + " current");
    const FolderSelectiveSyncCutpoint current =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            label + " current metadata");
    const StreamedCatalogContentProof current_proof =
        stream_catalog_content_proof_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            current.limits, current.state_generation,
            current.entry_count, current.catalog_path_bytes,
            label + " current content proof");
    if (current_proof.content_catalog_digest !=
        current.content_catalog_digest) {
        throw std::runtime_error(
            label + " current catalog content digest mismatch");
    }

    const std::optional<SyncReplicaFolderCatalogEntry> actual_current =
        load_exact_catalog_entry_row_or_throw(
            db, current.limits, current.state_generation,
            entry.canonical_path, label + " current path");
    if (actual_current != expected_current) {
        // A concurrent owner may already have committed the exact terminal
        // mapping we intended. Treat that as idempotent success; every other
        // same-path change invalidates this plan. Unrelated paths never enter
        // this comparison.
        if (actual_current.has_value() &&
            same_catalog_entry_without_generation(*actual_current, entry)) {
            transaction.commit();
            return {*actual_current, false};
        }
        throw std::runtime_error(
            label + " catalog path changed after its planning cutpoint");
    }
    if (actual_current.has_value() &&
        same_catalog_entry_without_generation(*actual_current, entry)) {
        transaction.commit();
        return {*actual_current, false};
    }

    const bool inserted = !actual_current.has_value();
    std::uint64_t entry_count = current.entry_count;
    std::uint64_t path_bytes = current.catalog_path_bytes;
    if (inserted) {
        if (entry_count >= current.limits.max_catalog_entries) {
            throw std::length_error(
                label + " catalog entry limit is exhausted");
        }
        entry_count = increment_or_throw(
            entry_count, label + " entry count");
        path_bytes = add_or_throw(
            path_bytes,
            static_cast<std::uint64_t>(entry.canonical_path.size()),
            label + " path bytes");
        if (path_bytes > current.limits.max_catalog_path_bytes) {
            throw std::length_error(
                label + " catalog path-byte limit is exhausted");
        }
    }

    entry.last_seen_generation = increment_or_throw(
        current.state_generation, label + " catalog generation");
    validate_catalog_entry_or_throw(
        entry, current.limits, entry.last_seen_generation, label);
    upsert_catalog_entry_row_or_throw(db, entry, label);

    const StreamedCatalogContentProof staged_content =
        stream_catalog_content_proof_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            current.limits, entry.last_seen_generation,
            entry_count, path_bytes, label + " staged content proof");
    const std::string digest = catalog_digest(
        staged_content.content_catalog_digest, current.policy);
    SyncSqliteStmt update = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_meta SET "
        "state_generation=?,entry_count=?,catalog_path_bytes=?,"
        "content_catalog_digest=?,catalog_digest=? WHERE id=1;",
        label + " metadata update prepare");
    sqlite_bind_u64_or_throw(
        update.stmt, 1, entry.last_seen_generation, label);
    sqlite_bind_u64_or_throw(update.stmt, 2, entry_count, label);
    sqlite_bind_u64_or_throw(update.stmt, 3, path_bytes, label);
    sqlite_bind_text_or_throw(
        update.stmt, 4, staged_content.content_catalog_digest, label);
    sqlite_bind_text_or_throw(update.stmt, 5, digest, label);
    sqlite_step_done_or_throw(update.stmt, label + " metadata update step");

    const FolderSelectiveSyncCutpoint staged =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            label + " staged metadata");
    const std::optional<SyncReplicaFolderCatalogEntry> staged_entry =
        load_exact_catalog_entry_row_or_throw(
            db, staged.limits, staged.state_generation,
            entry.canonical_path, label + " staged path");
    if (staged.state_generation != entry.last_seen_generation ||
        staged.limits != current.limits ||
        staged.entry_count != entry_count ||
        staged.catalog_path_bytes != path_bytes ||
        staged.content_catalog_digest !=
            staged_content.content_catalog_digest ||
        staged.policy != current.policy ||
        staged.absence_inference_fence_generation !=
            current.absence_inference_fence_generation ||
        staged.catalog_digest != digest ||
        staged_entry !=
            std::optional<SyncReplicaFolderCatalogEntry>{entry}) {
        throw std::runtime_error(
            label + " staged catalog did not retain the exact entry");
    }
    transaction.commit();
    return {std::move(entry), true};
}

struct CatalogRenameRecordResult final {
    SyncReplicaFolderCatalogEntry source_tombstone_entry;
    SyncReplicaFolderCatalogEntry destination_file_entry;
    bool changed = false;
};

[[nodiscard]] CatalogRenameRecordResult
record_catalog_identity_preserving_rename_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_attestation_digest,
    const SyncReplicaSqliteDeploymentBinding* deployment_binding,
    const SyncReplicaFolderCatalogEntry& expected_source,
    const std::optional<SyncReplicaFolderCatalogEntry>& expected_destination,
    SyncReplicaFolderCatalogEntry source_tombstone,
    SyncReplicaFolderCatalogEntry destination_file,
    const std::string& label) {
    if (expected_source.canonical_path ==
            destination_file.canonical_path ||
        source_tombstone.canonical_path !=
            expected_source.canonical_path ||
        (expected_destination.has_value() &&
         expected_destination->canonical_path !=
             destination_file.canonical_path) ||
        source_tombstone.kind != SyncReplicaValueKind::Tombstone ||
        destination_file.kind != SyncReplicaValueKind::File) {
        throw std::logic_error(
            label + " invalid catalog rename composition");
    }

    SyncSqliteTransaction transaction(
        db, label + " catalog publication",
        SyncSqliteTransactionMode::Immediate);
    attest_catalog_mutation_schema_or_throw(
        db, deployment_binding, label + " current");
    const FolderSelectiveSyncCutpoint current =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            label + " current metadata");
    const StreamedCatalogContentProof current_proof =
        stream_catalog_content_proof_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            current.limits, current.state_generation,
            current.entry_count, current.catalog_path_bytes,
            label + " current content proof");
    if (current_proof.content_catalog_digest !=
        current.content_catalog_digest) {
        throw std::runtime_error(
            label + " current catalog content digest mismatch");
    }

    const std::optional<SyncReplicaFolderCatalogEntry> actual_source =
        load_exact_catalog_entry_row_or_throw(
            db, current.limits, current.state_generation,
            expected_source.canonical_path, label + " current source");
    const std::optional<SyncReplicaFolderCatalogEntry> actual_destination =
        load_exact_catalog_entry_row_or_throw(
            db, current.limits, current.state_generation,
            destination_file.canonical_path,
            label + " current destination");

    const bool terminal_already_present =
        actual_source.has_value() &&
        actual_destination.has_value() &&
        same_catalog_entry_without_generation(
            *actual_source, source_tombstone) &&
        same_catalog_entry_without_generation(
            *actual_destination, destination_file);
    if (terminal_already_present) {
        transaction.commit();
        return {*actual_source, *actual_destination, false};
    }
    if (actual_source !=
            std::optional<SyncReplicaFolderCatalogEntry>{expected_source} ||
        actual_destination != expected_destination) {
        throw std::runtime_error(
            label + " catalog rename paths changed after their planning cutpoint");
    }

    const bool destination_inserted = !actual_destination.has_value();
    std::uint64_t entry_count = current.entry_count;
    std::uint64_t path_bytes = current.catalog_path_bytes;
    if (destination_inserted) {
        if (entry_count >= current.limits.max_catalog_entries) {
            throw std::length_error(
                label + " catalog entry limit is exhausted");
        }
        entry_count = increment_or_throw(
            entry_count, label + " entry count");
        path_bytes = add_or_throw(
            path_bytes,
            static_cast<std::uint64_t>(
                destination_file.canonical_path.size()),
            label + " path bytes");
        if (path_bytes > current.limits.max_catalog_path_bytes) {
            throw std::length_error(
                label + " catalog path-byte limit is exhausted");
        }
    }

    const std::uint64_t generation = increment_or_throw(
        current.state_generation, label + " catalog generation");
    source_tombstone.last_seen_generation = generation;
    destination_file.last_seen_generation = generation;
    validate_catalog_entry_or_throw(
        source_tombstone, current.limits, generation, label + " source");
    validate_catalog_entry_or_throw(
        destination_file, current.limits, generation,
        label + " destination");

    upsert_catalog_entry_row_or_throw(
        db, source_tombstone, label + " source");
    upsert_catalog_entry_row_or_throw(
        db, destination_file, label + " destination");

    const StreamedCatalogContentProof staged_content =
        stream_catalog_content_proof_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            current.limits, generation, entry_count, path_bytes,
            label + " staged content proof");
    const std::string digest = catalog_digest(
        staged_content.content_catalog_digest, current.policy);
    SyncSqliteStmt update = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_folder_catalog_meta SET "
        "state_generation=?,entry_count=?,catalog_path_bytes=?,"
        "content_catalog_digest=?,catalog_digest=? WHERE id=1;",
        label + " metadata update prepare");
    sqlite_bind_u64_or_throw(update.stmt, 1, generation, label);
    sqlite_bind_u64_or_throw(update.stmt, 2, entry_count, label);
    sqlite_bind_u64_or_throw(update.stmt, 3, path_bytes, label);
    sqlite_bind_text_or_throw(
        update.stmt, 4, staged_content.content_catalog_digest, label);
    sqlite_bind_text_or_throw(update.stmt, 5, digest, label);
    sqlite_step_done_or_throw(update.stmt, label + " metadata update step");

    const FolderSelectiveSyncCutpoint staged =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_path, root_attestation_digest,
            label + " staged metadata");
    const std::optional<SyncReplicaFolderCatalogEntry> staged_source =
        load_exact_catalog_entry_row_or_throw(
            db, staged.limits, staged.state_generation,
            source_tombstone.canonical_path, label + " staged source");
    const std::optional<SyncReplicaFolderCatalogEntry> staged_destination =
        load_exact_catalog_entry_row_or_throw(
            db, staged.limits, staged.state_generation,
            destination_file.canonical_path,
            label + " staged destination");
    if (staged.state_generation != generation ||
        staged.limits != current.limits ||
        staged.entry_count != entry_count ||
        staged.catalog_path_bytes != path_bytes ||
        staged.content_catalog_digest !=
            staged_content.content_catalog_digest ||
        staged.policy != current.policy ||
        staged.absence_inference_fence_generation !=
            current.absence_inference_fence_generation ||
        staged.catalog_digest != digest ||
        staged_source !=
            std::optional<SyncReplicaFolderCatalogEntry>{source_tombstone} ||
        staged_destination !=
            std::optional<SyncReplicaFolderCatalogEntry>{destination_file}) {
        throw std::runtime_error(
            label + " staged catalog did not retain the exact rename pair");
    }
    transaction.commit();
    return {std::move(source_tombstone),
            std::move(destination_file), true};
}

[[nodiscard]] std::vector<std::string> visible_operation_ids(
    const SyncReplicaModel& model,
    const std::string& canonical_path) {
    const auto view = model.visible_path(canonical_path);
    return view.has_value() ? view->visible_operation_ids
                            : std::vector<std::string>{};
}

[[nodiscard]] std::vector<SyncReplicaOperation> visible_operations(
    const SyncReplicaModel& model,
    const std::string& canonical_path) {
    std::vector<SyncReplicaOperation> out;
    for (const std::string& operation_id :
         visible_operation_ids(model, canonical_path)) {
        const auto operation = model.operation_by_id(operation_id);
        if (!operation.has_value()) {
            throw std::logic_error(
                "sync replica folder scan visible operation disappeared");
        }
        out.push_back(*operation);
    }
    return out;
}

[[nodiscard]] std::vector<std::string> operation_ids(
    const std::vector<SyncReplicaOperation>& operations) {
    std::vector<std::string> out;
    out.reserve(operations.size());
    for (const auto& operation : operations) {
        out.push_back(operation.operation_id);
    }
    return out;
}

[[nodiscard]] bool operation_matches_file(
    const SyncReplicaOperation& operation,
    std::string_view canonical_path,
    std::uint64_t size_bytes,
    std::string_view content_sha256) noexcept {
    return operation.kind == SyncReplicaValueKind::File &&
           operation.canonical_path == canonical_path &&
           operation.size_bytes == size_bytes &&
           operation.content_sha256 == content_sha256;
}

[[nodiscard]] bool operation_matches_catalog_entry(
    const SyncReplicaOperation& operation,
    const SyncReplicaFolderCatalogEntry& entry) noexcept {
    if (operation.canonical_path != entry.canonical_path ||
        operation.kind != entry.kind) {
        return false;
    }
    if (entry.kind == SyncReplicaValueKind::Tombstone) {
        return operation.size_bytes == 0U &&
               operation.content_sha256.empty();
    }
    return operation.size_bytes == entry.size_bytes &&
           operation.content_sha256 == entry.content_sha256;
}

struct LocalIdentityPreservingRenameCandidate final {
    SyncReplicaFolderCatalogEntry source_catalog_entry;
    SyncReplicaOperation source_file_operation;
};

[[nodiscard]] std::optional<LocalIdentityPreservingRenameCandidate>
find_unique_absent_identity_preserving_rename_source_or_none(
    const FolderCatalogFileContentCutpoint& catalog_content,
    const SyncReplicaSqliteVisibleFileContentCutpoint& replica_content,
    const SyncReplicaSelectiveSyncPolicy& selective_sync_policy,
    const SyncDirectoryAuthority& root,
    std::string_view destination_canonical_path,
    std::uint64_t size_bytes,
    std::string_view content_sha256,
    const std::string& label) {
    if (catalog_content.ambiguous || replica_content.ambiguous ||
        !catalog_content.sole_file_entry.has_value() ||
        !replica_content.sole_visible_file_operation.has_value()) {
        return std::nullopt;
    }

    const SyncReplicaFolderCatalogEntry& entry =
        *catalog_content.sole_file_entry;
    const SyncReplicaOperation& operation =
        *replica_content.sole_visible_file_operation;
    if (entry.canonical_path == destination_canonical_path ||
        entry.kind != SyncReplicaValueKind::File ||
        entry.size_bytes != size_bytes ||
        entry.content_sha256 != content_sha256 ||
        operation.operation_id != entry.operation_id ||
        operation.canonical_path != entry.canonical_path ||
        operation.kind != SyncReplicaValueKind::File ||
        operation.size_bytes != size_bytes ||
        operation.content_sha256 != content_sha256 ||
        !operation_matches_catalog_entry(operation, entry)) {
        return std::nullopt;
    }

    // Both startup-attested content indexes found exactly one current file with
    // this immutable payload identity.  Identity still requires a materialized
    // source whose rooted name is absent; a metadata-only omission or surviving
    // copy falls back to ordinary create/delete semantics before any payload or
    // database effect.
    if (!sync_replica_selective_sync_path_is_materialized(
            selective_sync_policy, entry.canonical_path) ||
        open_optional_regular_file_beneath_root_or_throw(
            root, entry.canonical_path,
            label + " candidate-source absence reproof").has_value()) {
        return std::nullopt;
    }
    return LocalIdentityPreservingRenameCandidate{entry, operation};
}

[[nodiscard]] std::optional<SyncReplicaOperation>
matching_visible_operation(
    const std::vector<SyncReplicaOperation>& operations,
    std::string_view canonical_path,
    std::uint64_t size_bytes,
    std::string_view content_sha256) {
    for (const auto& operation : operations) {
        if (operation_matches_file(
                operation, canonical_path, size_bytes, content_sha256)) {
            return operation;
        }
    }
    return std::nullopt;
}

[[nodiscard]] SyncReplicaOperation
require_sole_visible_operation_or_throw(
    const SyncReplicaModel& model,
    const std::string& operation_id,
    SyncReplicaValueKind expected_kind,
    std::string_view expected_label,
    const std::string& label) {
    const auto operation = model.operation_by_id(operation_id);
    if (!operation.has_value()) {
        throw std::invalid_argument(
            label + " operation is not active replica evidence");
    }
    if (operation->kind != expected_kind) {
        throw std::invalid_argument(
            label + " operation is not a " + std::string(expected_label) +
            " value");
    }
    const auto view = model.visible_path(operation->canonical_path);
    if (!view.has_value() || view->visible_operation_ids.size() != 1U ||
        view->visible_operation_ids.front() != operation->operation_id) {
        throw std::runtime_error(
            label +
            " operation is not the sole visible value for its path");
    }
    return *operation;
}

[[nodiscard]] SyncReplicaOperation
require_sole_visible_file_operation_or_throw(
    const SyncReplicaModel& model,
    const std::string& operation_id,
    const std::string& label) {
    return require_sole_visible_operation_or_throw(
        model, operation_id, SyncReplicaValueKind::File,
        "regular-file", label);
}

[[nodiscard]] SyncReplicaOperation
require_sole_visible_tombstone_operation_or_throw(
    const SyncReplicaModel& model,
    const std::string& operation_id,
    const std::string& label) {
    return require_sole_visible_operation_or_throw(
        model, operation_id, SyncReplicaValueKind::Tombstone,
        "tombstone", label);
}

[[nodiscard]] SyncReplicaOperation
require_catalog_operation_or_throw(
    const SyncReplicaModel& model,
    const SyncReplicaFolderCatalogEntry& entry,
    const std::string& label) {
    const auto operation = model.evidence_operation_by_id(entry.operation_id);
    if (!operation.has_value() ||
        !operation_matches_catalog_entry(*operation, entry)) {
        throw std::runtime_error(
            label +
            " catalog mapping disagrees with retained replica evidence");
    }
    return *operation;
}

[[nodiscard]] bool observation_matches_operation(
    const StableRegularFileObservation& observation,
    const SyncReplicaOperation& operation) noexcept {
    return observation.metadata.size_bytes == operation.size_bytes &&
           observation.content_sha256 == operation.content_sha256;
}

[[nodiscard]] bool observation_matches_catalog_entry(
    const StableRegularFileObservation& observation,
    const SyncReplicaFolderCatalogEntry& entry) noexcept {
    return entry.kind == SyncReplicaValueKind::File &&
           observation.metadata.size_bytes == entry.size_bytes &&
           observation.content_sha256 == entry.content_sha256 &&
           observation.source_snapshot_sha256 ==
               entry.source_snapshot_sha256;
}

void validate_convergence_pass_limits_or_throw(
    const SyncReplicaFolderConvergencePassLimits& limits,
    const SyncReplicaFolderScanLimits& owner_limits,
    const SyncReplicaFilePayloadStoreLimits& payload_store_limits,
    const std::string& label) {
    SyncReplicaFolderObservationLimits traversal_limits;
    traversal_limits.maximum_entries = limits.maximum_entries;
    traversal_limits.maximum_regular_files = limits.maximum_regular_files;
    traversal_limits.maximum_file_bytes = limits.maximum_file_bytes;
    traversal_limits.maximum_total_file_bytes =
        limits.maximum_total_file_bytes;
    traversal_limits.maximum_relative_path_bytes =
        limits.maximum_relative_path_bytes;
    traversal_limits.maximum_directory_depth =
        limits.maximum_directory_depth;
    validate_sync_replica_folder_observation_limits_or_throw(
        traversal_limits, label + " pass traversal limits");
    if (limits.maximum_file_bytes > limits.maximum_total_file_bytes) {
        throw std::invalid_argument(
            label +
            " pass file-byte limit exceeds its aggregate byte limit");
    }

    if (limits.maximum_file_bytes > owner_limits.max_payload_bytes) {
        throw std::invalid_argument(
            label + " pass file-byte limit exceeds the folder owner limit");
    }
    if (limits.maximum_relative_path_bytes >
        owner_limits.max_catalog_path_bytes) {
        throw std::invalid_argument(
            label +
            " pass relative-path limit exceeds the catalog byte budget");
    }
    if (limits.maximum_regular_files > owner_limits.max_catalog_entries) {
        throw std::invalid_argument(
            label +
            " pass regular-file limit exceeds the retained catalog capacity");
    }
    if (limits.maximum_remote_paths > owner_limits.max_catalog_entries) {
        throw std::invalid_argument(
            label +
            " pass remote-path limit exceeds the retained catalog capacity");
    }
    if (limits.maximum_regular_files > payload_store_limits.max_entries) {
        throw std::invalid_argument(
            label +
            " pass regular-file limit exceeds the retained payload-store capacity");
    }
    if (limits.maximum_remote_paths > payload_store_limits.max_entries) {
        throw std::invalid_argument(
            label +
            " pass remote-path limit exceeds the retained payload-store capacity");
    }
    if (limits.maximum_remote_paths == 0U ||
        limits.maximum_remote_paths >
            kSyncReplicaFolderScanMaxCatalogEntries) {
        throw std::invalid_argument(
            label + " pass remote-path limit is invalid");
    }
    if (limits.maximum_remote_inspection_paths == 0U ||
        limits.maximum_remote_inspection_paths >
            kSyncReplicaFolderScanMaxCatalogEntries) {
        throw std::invalid_argument(
            label + " pass remote-inspection path limit is invalid");
    }
    SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files =
        limits.maximum_local_scan_segment_regular_files;
    validate_sync_replica_folder_traversal_segment_limits_or_throw(
        segment_limits, label + " pass local scan segment limits");
    if (limits.maximum_local_scan_segment_regular_files >
        limits.maximum_regular_files) {
        throw std::invalid_argument(
            label +
            " pass local scan segment regular-file limit exceeds the whole-folder regular-file limit");
    }
    if (limits.maximum_remote_apply_operations == 0U ||
        limits.maximum_remote_apply_operations >
            kSyncReplicaFolderScanMaxCatalogEntries) {
        throw std::invalid_argument(
            label + " pass remote-apply operation limit is invalid");
    }
    if (limits.maximum_payload_batch_puts == 0U ||
        limits.maximum_payload_batch_puts >
            kSyncReplicaFolderObservationMaximumEntries) {
        throw std::invalid_argument(
            label + " pass payload-batch put limit is invalid");
    }
    if (limits.maximum_payload_batch_work_bytes == 0U) {
        throw std::invalid_argument(
            label + " pass payload-batch work-byte limit is invalid");
    }
}

struct RemoteProjectionEntry final {
    const SyncReplicaOperation* operation;
};

enum class RemoteApplyCandidateKind : std::uint8_t {
    ApplyVisibleOperation = 1U,
    DematerializeMetadataOnlyFile = 2U,
};

struct RemoteApplyCandidate final {
    std::size_t projection_index = 0U;
    RemoteApplyCandidateKind kind =
        RemoteApplyCandidateKind::ApplyVisibleOperation;
    std::uint64_t planned_file_bytes = 0U;
};

enum class MetadataOnlyDematerializationDisposition : std::uint8_t {
    Removed = 1U,
    AlreadyAbsent = 2U,
    BlockedLocalState = 3U,
    BlockedPayloadUnavailable = 4U,
};

struct MetadataOnlyDematerializationResult final {
    MetadataOnlyDematerializationDisposition disposition =
        MetadataOnlyDematerializationDisposition::BlockedLocalState;
    std::uint64_t removed_bytes = 0U;
};

// Safety admission and work scheduling are deliberately separate. This helper
// validates the complete sole-visible projection before the caller performs a
// single rooted path inspection or catalog/filesystem effect. The returned
// projection borrows active-operation addresses from the supplied immutable
// model and is canonical-path ordered, making it suitable for a durable path
// cursor. The caller must keep that exact model alive and unmodified through
// projection use. Multihead paths remain unresolved diagnostics rather than
// work items, exactly as in the one-path apply owner.
[[nodiscard]] std::vector<RemoteProjectionEntry>
validated_remote_projection_or_throw(
    const SyncReplicaModel& remote_model,
    const std::vector<SyncReplicaPathView>& remote_paths,
    const SyncReplicaFolderConvergencePassLimits& limits,
    SyncReplicaFolderConvergencePassReport& report,
    const std::string& label) {
    std::vector<RemoteProjectionEntry> projection;
    projection.reserve(remote_paths.size());
    std::string_view previous_path;
    bool have_previous_path = false;
    for (const SyncReplicaPathView& path : remote_paths) {
        if (have_previous_path && !(previous_path < path.canonical_path)) {
            throw std::logic_error(
                label + " remote projection is not strictly path ordered");
        }
        previous_path = path.canonical_path;
        have_previous_path = true;

        if (path.visible_operation_ids.size() != 1U) {
            ++report.skipped_conflicted_remote_path_count;
            continue;
        }
        if (path.canonical_path.size() >
            limits.maximum_relative_path_bytes) {
            throw std::runtime_error(
                label +
                " remote path exceeds its relative-path byte limit");
        }
        const std::uint64_t path_depth = static_cast<std::uint64_t>(
            std::count(
                path.canonical_path.begin(), path.canonical_path.end(), '/'));
        if (path_depth > limits.maximum_directory_depth) {
            throw std::runtime_error(
                label + " remote path exceeds its directory-depth limit");
        }

        const std::string& operation_id =
            path.visible_operation_ids.front();
        const SyncReplicaOperation* operation =
            remote_model.active_operation_by_id_or_none(operation_id);
        if (operation == nullptr ||
            operation->kind != path.primary_kind ||
            operation->canonical_path != path.canonical_path) {
            throw std::logic_error(
                label +
                " remote projection disagrees with active evidence");
        }
        if (operation->kind == SyncReplicaValueKind::File &&
            operation->size_bytes > limits.maximum_file_bytes) {
            throw std::runtime_error(
                label + " remote file exceeds its per-file byte limit");
        }
        projection.push_back(RemoteProjectionEntry{operation});
    }
    return projection;
}

struct CyclicRemoteProjectionStart final {
    std::size_t index = 0U;
    bool wrapped_before_first_path = false;
};

[[nodiscard]] CyclicRemoteProjectionStart
cyclic_remote_projection_start_after(
    const std::vector<RemoteProjectionEntry>& projection,
    std::string_view resume_after_path) {
    if (projection.empty() || resume_after_path.empty()) return {};
    const auto start = std::upper_bound(
        projection.begin(), projection.end(), resume_after_path,
        [](std::string_view cursor, const RemoteProjectionEntry& retained) {
            return cursor < retained.operation->canonical_path;
        });
    const std::size_t index = static_cast<std::size_t>(
        std::distance(projection.begin(), start));
    if (index == projection.size()) return {0U, true};
    return {index, false};
}

void validate_continuing_remote_inspection_sweep_or_throw(
    const FolderRemoteWorkProgressHead& progress,
    const std::vector<RemoteProjectionEntry>& projection,
    const std::string& label) {
    if (progress.inspection_sweep_basis_digest.empty()) {
        throw std::logic_error(
            label + " continuing remote inspection sweep has no basis");
    }
    const std::uint64_t projection_path_count =
        static_cast<std::uint64_t>(projection.size());
    if (progress.inspection_sweep_seen_path_count == 0U ||
        progress.inspection_sweep_seen_path_count >= projection_path_count) {
        throw std::runtime_error(
            label +
            " persisted remote inspection sweep already reached its projection");
    }

    const CyclicRemoteProjectionStart origin =
        cyclic_remote_projection_start_after(
            projection, progress.inspection_sweep_started_after_path);
    const std::size_t acknowledged_offset = static_cast<std::size_t>(
        progress.inspection_sweep_seen_path_count - 1U);
    const std::size_t expected_index =
        (origin.index + acknowledged_offset) % projection.size();
    const std::string& expected_cursor =
        projection[expected_index].operation->canonical_path;
    if (progress.resume_after_path != expected_cursor) {
        throw std::runtime_error(
            label +
            " remote inspection sweep cursor/count disagrees with its projection origin");
    }
}

void record_scan_disposition(
    SyncReplicaFolderConvergencePassReport& report,
    SyncReplicaFolderScanDisposition disposition) {
    switch (disposition) {
        case SyncReplicaFolderScanDisposition::Published:
            ++report.local_published_count;
            return;
        case SyncReplicaFolderScanDisposition::AdoptedVisibleOperation:
            ++report.local_adopted_visible_count;
            return;
        case SyncReplicaFolderScanDisposition::CatalogNoOp:
            ++report.local_catalog_no_op_count;
            return;
        case SyncReplicaFolderScanDisposition::CatalogRefreshed:
            ++report.local_catalog_refreshed_count;
            return;
    }
    throw std::logic_error(
        "sync replica folder pass received an unknown scan disposition");
}

void record_apply_disposition(
    SyncReplicaFolderConvergencePassReport& report,
    SyncReplicaFolderApplyDisposition disposition) {
    if (report.remote_apply_operation_count ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::logic_error(
            "sync replica folder pass remote apply count exceeds uint64 range");
    }
    ++report.remote_apply_operation_count;
    switch (disposition) {
        case SyncReplicaFolderApplyDisposition::Applied:
            ++report.remote_applied_count;
            return;
        case SyncReplicaFolderApplyDisposition::AdoptedExactTarget:
            ++report.remote_adopted_exact_count;
            return;
        case SyncReplicaFolderApplyDisposition::CatalogNoOp:
            ++report.remote_catalog_no_op_count;
            return;
    }
    throw std::logic_error(
        "sync replica folder pass received an unknown apply disposition");
}

}  // namespace

SyncReplicaFolderConvergencePassLimits
sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
    std::uint64_t maximum_payload_bytes,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder convergence limit label is empty");
    }
    if (maximum_payload_bytes == 0U ||
        maximum_payload_bytes > kSyncReplicaFolderScanMaxPayloadBytes) {
        throw std::invalid_argument(
            label + " maximum payload bytes are outside the folder ceiling");
    }
    SyncReplicaFolderConvergencePassLimits limits;
    limits.maximum_file_bytes = maximum_payload_bytes;
    limits.maximum_total_file_bytes = std::max<std::uint64_t>(
        limits.maximum_total_file_bytes, maximum_payload_bytes);
    return limits;
}

struct SyncReplicaPreparedRegularFile::State final {
    std::shared_ptr<const unsigned char> owner_token;
    int descriptor = -1;
    std::string canonical_path;
    std::string content_sha256;
    std::string source_snapshot_sha256;
    std::uint64_t selective_sync_policy_generation = 0U;
    std::string selective_sync_policy_digest;
    SyncPosixRegularFileSnapshotMetadata observation;
    std::vector<std::string> observed_visible_operation_ids;

    ~State() noexcept {
        if (descriptor >= 0) (void)::close(descriptor);
    }
};

struct SyncReplicaFolderScanOwner::State final {
    SyncSqliteDbHandleSlot* catalog_db = nullptr;
    std::string folder_id;
    std::string absolute_root_path;
    std::string root_attestation_digest;
    SyncReplicaFolderScanLimits limits;
    std::string label;
    SyncDirectoryAuthority root_authority;
    SyncReplicaSqliteOwner* replica_owner = nullptr;
    SyncReplicaFilePayloadStore* payload_store = nullptr;
    std::optional<SyncReplicaSqliteDeploymentBinding> catalog_binding;
    std::shared_ptr<const unsigned char> owner_token =
        std::make_shared<const unsigned char>(0U);
};

void validate_sync_replica_folder_scan_limits_or_throw(
    const SyncReplicaFolderScanLimits& limits) {
    if (limits.max_catalog_entries == 0U ||
        limits.max_catalog_entries > kSyncReplicaFolderScanMaxCatalogEntries ||
        limits.max_catalog_entries > kMaxPersistentInteger) {
        throw std::invalid_argument(
            "sync replica folder scan catalog entry limit is invalid");
    }
    if (limits.max_catalog_path_bytes == 0U ||
        limits.max_catalog_path_bytes > kMaxPersistentInteger) {
        throw std::invalid_argument(
            "sync replica folder scan path-byte limit is invalid");
    }
    if (limits.max_payload_bytes == 0U ||
        limits.max_payload_bytes > kSyncReplicaFolderScanMaxPayloadBytes ||
        limits.max_payload_bytes > kMaxPersistentInteger ||
        limits.max_payload_bytes >
            static_cast<std::uint64_t>(
                std::numeric_limits<std::size_t>::max())) {
        throw std::invalid_argument(
            "sync replica folder scan payload limit is invalid");
    }
}


namespace {

[[nodiscard]] std::string
canonical_offline_catalog_root_text_or_throw(
    const fs::path& expected_root_path,
    const std::string& label) {
    if (expected_root_path.empty() || !expected_root_path.is_absolute() ||
        expected_root_path.lexically_normal() != expected_root_path) {
        throw std::invalid_argument(
            label + " root path must be canonical and absolute");
    }
    const std::string root_text = expected_root_path.generic_string();
    if (root_text.empty() || root_text.size() > 16384U ||
        root_text.find('\0') != std::string::npos) {
        throw std::invalid_argument(
            label + " root path exceeds its bounded text contract");
    }
    return root_text;
}

[[nodiscard]] std::string
persisted_catalog_root_attestation_digest_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const std::string& expected_root_path,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest "
        "FROM main.sync_replica_folder_catalog_meta WHERE id=1 LIMIT 2;",
        label + " persisted root identity prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " persisted root identity step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " persisted root identity is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " schema version");
    const std::string folder_id = sqlite_column_text_or_throw(
        statement.stmt, 1, 128U, label + " folder identity");
    const std::string root_path = sqlite_column_text_or_throw(
        statement.stmt, 2, 16384U, label + " root path");
    const std::string root_digest = sqlite_column_text_or_throw(
        statement.stmt, 3, 64U, label + " root attestation digest");
    if (step_row_or_done_or_throw(
            statement.stmt,
            label + " persisted root identity trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " persisted root identity is not unique");
    }
    if (schema_version != kSchemaVersion ||
        folder_id != expected_folder_id ||
        root_path != expected_root_path ||
        root_path.find('\0') != std::string::npos ||
        !is_lowercase_sha256_hex(root_digest)) {
        throw std::runtime_error(
            label + " persisted root identity is invalid or mismatched");
    }
    return root_digest;
}

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
inspect_catalog_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    fs::path expected_root_path,
    bool detached_image,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder-catalog offline inspection label is empty");
    }
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_binding, label + " deployment binding");
    if (catalog_binding.role !=
        SyncReplicaSqliteDeploymentRole::FolderCatalog) {
        throw std::invalid_argument(
            label + " deployment binding has the wrong SQLite role");
    }
    if (folder_id != catalog_binding.deployment.folder_id) {
        throw std::invalid_argument(
            label + " folder identity conflicts with the deployment binding");
    }
    const std::string root_text =
        canonical_offline_catalog_root_text_or_throw(
            expected_root_path, label);
    if (!detached_image) {
        auto database = borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " read-only connection proof");
        if (sqlite3_db_readonly(database.get(), "main") != 1) {
            throw std::runtime_error(
                label + " requires a read-only named main database connection");
        }
    }

    if (detached_image) {
        attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw(
            db, catalog_binding, label + " detached deployment binding");
    } else {
        attest_sync_replica_sqlite_deployment_binding_or_throw(
            db, catalog_binding, label + " named deployment binding");
    }
    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    attest_schema_or_throw(db, true, label + " schema");
    const std::string root_digest =
        persisted_catalog_root_attestation_digest_or_throw(
            db, folder_id, root_text, label);
    SyncReplicaFolderCatalogSnapshot snapshot;
    if (detached_image) {
        snapshot = load_catalog_or_throw(
            db, folder_id, root_text, root_digest, nullptr,
            label + " snapshot", false, true);
    } else {
        snapshot = load_catalog_or_throw(
            db, folder_id, root_text, root_digest,
            &catalog_binding, label + " snapshot");
    }
    transaction.commit();
    return snapshot;
}

}  // namespace

SyncReplicaFolderCatalogSnapshot
inspect_sync_replica_folder_catalog_snapshot_read_only_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    fs::path expected_root_path,
    std::string label) {
    return inspect_catalog_without_root_access_or_throw(
        db, catalog_binding, std::move(folder_id),
        std::move(expected_root_path), false, std::move(label));
}

SyncReplicaFolderCatalogSnapshot
inspect_sync_replica_folder_catalog_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    fs::path expected_root_path,
    std::string label) {
    return inspect_catalog_without_root_access_or_throw(
        db, catalog_binding, std::move(folder_id),
        std::move(expected_root_path), true, std::move(label));
}

SyncReplicaFolderSelectiveSyncSnapshot
inspect_sync_replica_folder_selective_sync_snapshot_read_only_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    fs::path expected_root_path,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica selective-sync offline inspection label is empty");
    }
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_binding, label + " deployment binding");
    if (catalog_binding.role !=
        SyncReplicaSqliteDeploymentRole::FolderCatalog) {
        throw std::invalid_argument(
            label + " deployment binding has the wrong SQLite role");
    }
    if (folder_id != catalog_binding.deployment.folder_id) {
        throw std::invalid_argument(
            label + " folder identity conflicts with the deployment binding");
    }
    const std::string root_text =
        canonical_offline_catalog_root_text_or_throw(
            expected_root_path, label);
    auto database = borrow_sync_sqlite_serialized_db_or_throw(
        db, label + " read-only connection proof");
    if (sqlite3_db_readonly(database.get(), "main") != 1) {
        throw std::runtime_error(
            label + " requires a read-only named main database connection");
    }

    attest_sync_replica_sqlite_deployment_binding_or_throw(
        db, catalog_binding, label + " deployment binding");
    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    attest_schema_or_throw(db, true, label + " schema");
    const std::string root_digest =
        persisted_catalog_root_attestation_digest_or_throw(
            db, folder_id, root_text, label);
    const FolderSelectiveSyncCutpoint cutpoint =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_text, root_digest, label + " cutpoint");
    transaction.commit();
    return public_selective_sync_snapshot(cutpoint);
}

SyncReplicaFolderSelectiveSyncSnapshot
replace_sync_replica_folder_selective_sync_policy_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    fs::path expected_root_path,
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica selective-sync offline replacement label is empty");
    }
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_binding, label + " deployment binding");
    if (catalog_binding.role !=
        SyncReplicaSqliteDeploymentRole::FolderCatalog) {
        throw std::invalid_argument(
            label + " deployment binding has the wrong SQLite role");
    }
    if (folder_id != catalog_binding.deployment.folder_id) {
        throw std::invalid_argument(
            label + " folder identity conflicts with the deployment binding");
    }
    const std::string root_text =
        canonical_offline_catalog_root_text_or_throw(
            expected_root_path, label);
    auto database = borrow_sync_sqlite_serialized_db_or_throw(
        db, label + " writable connection proof");
    if (sqlite3_db_readonly(database.get(), "main") != 0) {
        throw std::runtime_error(
            label + " requires a writable named main database connection");
    }

    SyncSqliteTransaction transaction(
        db, label + " transaction", SyncSqliteTransactionMode::Immediate);
    attest_sync_replica_sqlite_deployment_binding_state_or_throw(
        db, catalog_binding, label + " deployment binding");
    attest_schema_or_throw(db, true, label + " schema");
    const std::string root_digest =
        persisted_catalog_root_attestation_digest_or_throw(
            db, folder_id, root_text, label);
    const FolderSelectiveSyncCutpoint current =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_text, root_digest, label + " current");
    (void)replace_selective_sync_policy_in_transaction_or_throw(
        db, current, default_mode, std::move(rules), label);
    const FolderSelectiveSyncCutpoint completed =
        load_selective_sync_cutpoint_rows_or_throw(
            db, folder_id, root_text, root_digest, label + " completed");
    transaction.commit();
    return public_selective_sync_snapshot(completed);
}

void initialize_sync_replica_folder_catalog_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& catalog_db,
    SyncReplicaSqliteDeploymentBinding catalog_binding,
    fs::path absolute_root_directory,
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaFolderScanLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "detached folder-catalog bootstrap label must not be empty");
    }
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_binding, label + " deployment binding");
    if (catalog_binding.role !=
        SyncReplicaSqliteDeploymentRole::FolderCatalog) {
        throw std::invalid_argument(
            label + " deployment binding has the wrong SQLite store role");
    }
    validate_sync_replica_folder_scan_limits_or_throw(limits);
    if (payload_store.folder_id() !=
        catalog_binding.deployment.folder_id) {
        throw std::invalid_argument(
            label + " payload store belongs to another folder");
    }
    if (limits.max_payload_bytes > payload_store.limits().max_payload_bytes) {
        throw std::invalid_argument(
            label + " folder scan payload limit exceeds the payload-store limit");
    }

    SyncDirectoryAuthority root = SyncDirectoryAuthority::open_or_throw(
        absolute_root_directory, label + " root");
    const std::string root_path = root.path().generic_string();
    const std::string root_attestation_digest =
        sync_directory_attestation_digest_or_throw(root.attestation());

    const SyncReplicaSqliteSnapshot replica =
        replica_owner.snapshot_or_throw();
    if (replica.durable.folder_id !=
            catalog_binding.deployment.folder_id ||
        replica.durable.local_actor !=
            catalog_binding.deployment.local_actor) {
        throw std::invalid_argument(
            label + " replica owner conflicts with the selected deployment");
    }
    // Product payload identity is materialized and re-attested only by a
    // snapshot/open operation. Bootstrap proves it before minting the catalog
    // image so a wrong or absent payload root cannot acquire catalog state.
    (void)payload_store.snapshot_or_throw();
    root.verify_or_throw(label + " root before detached catalog mutation");

    sqlite_exec_or_throw(
        catalog_db,
        "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;",
        label + " detached connection hardening");
    initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
        catalog_db, catalog_binding, label + " deployment binding");
    initialize_or_attest_catalog_or_throw(
        catalog_db, catalog_binding.deployment.folder_id, root_path,
        root_attestation_digest, limits, &catalog_binding,
        SyncReplicaFolderCatalogOpenDisposition::CreateIfMissing,
        label + " catalog", true);
    const SyncReplicaFolderCatalogSnapshot snapshot = load_catalog_or_throw(
        catalog_db, catalog_binding.deployment.folder_id, root_path,
        root_attestation_digest, &catalog_binding,
        label + " completed image", true);
    if (snapshot.state_generation != 0U || !snapshot.entries.empty()) {
        throw std::logic_error(
            label + " detached catalog image is not at genesis");
    }
    root.verify_or_throw(label + " root after detached catalog mutation");
}

SyncReplicaPreparedRegularFile::~SyncReplicaPreparedRegularFile() noexcept =
    default;

SyncReplicaPreparedRegularFile::SyncReplicaPreparedRegularFile(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaPreparedRegularFile::SyncReplicaPreparedRegularFile(
    SyncReplicaPreparedRegularFile&&) noexcept = default;

SyncReplicaPreparedRegularFile& SyncReplicaPreparedRegularFile::operator=(
    SyncReplicaPreparedRegularFile&&) noexcept = default;

bool SyncReplicaPreparedRegularFile::active() const noexcept {
    return static_cast<bool>(state_);
}

SyncReplicaPreparedRegularFile::State&
SyncReplicaPreparedRegularFile::require_state_or_throw(
    std::string_view label) {
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " prepared file is inactive");
    }
    return *state_;
}

const SyncReplicaPreparedRegularFile::State&
SyncReplicaPreparedRegularFile::require_state_or_throw(
    std::string_view label) const {
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " prepared file is inactive");
    }
    return *state_;
}

const std::string& SyncReplicaPreparedRegularFile::canonical_path() const {
    return require_state_or_throw(
               "sync replica prepared regular file path")
        .canonical_path;
}

std::uint64_t SyncReplicaPreparedRegularFile::size_bytes() const {
    return require_state_or_throw(
               "sync replica prepared regular file size")
        .observation.size_bytes;
}

const std::string& SyncReplicaPreparedRegularFile::content_sha256() const {
    return require_state_or_throw(
               "sync replica prepared regular file content digest")
        .content_sha256;
}

const std::vector<std::string>&
SyncReplicaPreparedRegularFile::observed_visible_operation_ids() const {
    return require_state_or_throw(
               "sync replica prepared regular file observed heads")
        .observed_visible_operation_ids;
}

SyncReplicaFolderScanOwner::SyncReplicaFolderScanOwner(
    SyncSqliteDbHandleSlot& catalog_db,
    std::string folder_id,
    fs::path absolute_root_directory,
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaFolderScanLimits limits,
    std::string label) {
    initialize_or_throw(
        catalog_db, std::move(folder_id),
        std::move(absolute_root_directory), replica_owner, payload_store,
        limits, std::move(label), std::nullopt,
        SyncReplicaFolderCatalogOpenDisposition::CreateIfMissing);
}

SyncReplicaFolderScanOwner::SyncReplicaFolderScanOwner(
    SyncSqliteDbHandleSlot& catalog_db,
    SyncReplicaSqliteDeploymentBinding catalog_binding,
    fs::path absolute_root_directory,
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaFolderCatalogOpenDisposition disposition,
    SyncReplicaFolderScanLimits limits,
    std::string label) {
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_binding, label + " catalog deployment binding");
    if (catalog_binding.role !=
        SyncReplicaSqliteDeploymentRole::FolderCatalog) {
        throw std::invalid_argument(
            label + " catalog binding has the wrong SQLite store role");
    }
    std::string folder_id = catalog_binding.deployment.folder_id;
    initialize_or_throw(
        catalog_db, std::move(folder_id),
        std::move(absolute_root_directory), replica_owner, payload_store,
        limits, std::move(label), std::move(catalog_binding), disposition);
}

void SyncReplicaFolderScanOwner::initialize_or_throw(
    SyncSqliteDbHandleSlot& catalog_db,
    std::string folder_id,
    fs::path absolute_root_directory,
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaFolderScanLimits limits,
    std::string label,
    std::optional<SyncReplicaSqliteDeploymentBinding> catalog_binding,
    SyncReplicaFolderCatalogOpenDisposition disposition) {
    if (state_) {
        throw std::logic_error(
            "sync replica folder scan owner is already initialized");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder scan owner label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    switch (disposition) {
        case SyncReplicaFolderCatalogOpenDisposition::ExistingOnly:
        case SyncReplicaFolderCatalogOpenDisposition::CreateIfMissing:
            break;
        default:
            throw std::invalid_argument(
                label + " catalog open disposition is invalid");
    }
    validate_sync_replica_folder_scan_limits_or_throw(limits);
    sqlite_exec_or_throw(
        catalog_db,
        "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;",
        label + " catalog connection hardening");
    if (payload_store.folder_id() != folder_id) {
        throw std::invalid_argument(
            label + " payload store belongs to another folder");
    }

    auto state = std::make_unique<State>();
    state->catalog_db = &catalog_db;
    state->folder_id = std::move(folder_id);
    state->limits = limits;
    state->label = std::move(label);
    state->root_authority = SyncDirectoryAuthority::open_or_throw(
        absolute_root_directory, state->label + " root");
    state->absolute_root_path =
        state->root_authority.path().generic_string();
    state->root_attestation_digest =
        sync_directory_attestation_digest_or_throw(
            state->root_authority.attestation());
    state->replica_owner = &replica_owner;
    state->payload_store = &payload_store;
    state->catalog_binding = std::move(catalog_binding);

    const SyncReplicaSqliteSnapshot replica =
        state->replica_owner->snapshot_or_throw();
    if (replica.durable.folder_id != state->folder_id) {
        throw std::invalid_argument(
            state->label + " replica owner belongs to another folder");
    }
    if (state->catalog_binding.has_value()) {
        const SyncReplicaDeploymentIdentity& deployment =
            state->catalog_binding->deployment;
        if (replica.durable.local_actor != deployment.local_actor) {
            throw std::invalid_argument(
                state->label +
                " replica owner local actor conflicts with the deployment");
        }
    }
    initialize_or_attest_catalog_or_throw(
        *state->catalog_db, state->folder_id, state->absolute_root_path,
        state->root_attestation_digest, state->limits,
        state->catalog_binding ? &*state->catalog_binding : nullptr,
        disposition, state->label);
    const SyncReplicaFolderCatalogSnapshot catalog = load_catalog_or_throw(
        *state->catalog_db, state->folder_id, state->absolute_root_path,
        state->root_attestation_digest,
        state->catalog_binding ? &*state->catalog_binding : nullptr,
        state->label);
    state->limits = catalog.limits;
    if (state->limits.max_payload_bytes >
        payload_store.limits().max_payload_bytes) {
        throw std::invalid_argument(
            state->label +
            " folder scan payload limit exceeds the payload-store limit");
    }
    state_ = std::move(state);
}

SyncReplicaFolderScanOwner::~SyncReplicaFolderScanOwner() noexcept = default;

SyncReplicaFolderCatalogSnapshot
SyncReplicaFolderScanOwner::snapshot_or_throw() {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    SyncSqliteTransaction transaction(
        *state_->catalog_db, state_->label + " snapshot",
        SyncSqliteTransactionMode::Deferred);
    SyncReplicaFolderCatalogSnapshot snapshot = load_catalog_or_throw(
        *state_->catalog_db, state_->folder_id, state_->absolute_root_path,
        state_->root_attestation_digest,
        state_->catalog_binding ? &*state_->catalog_binding : nullptr,
        state_->label + " snapshot");
    transaction.commit();
    return snapshot;
}

const std::string& SyncReplicaFolderScanOwner::folder_id() const {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    return state_->folder_id;
}

SyncReplicaSelectiveSyncPolicy
SyncReplicaFolderScanOwner::selective_sync_policy_snapshot_or_throw() {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    SyncSqliteTransaction transaction(
        *state_->catalog_db, state_->label + " selective-sync snapshot",
        SyncSqliteTransactionMode::Deferred);
    const FolderSelectiveSyncCutpoint cutpoint =
        load_selective_sync_cutpoint_or_throw(
            *state_->catalog_db, state_->folder_id,
            state_->absolute_root_path, state_->root_attestation_digest,
            state_->catalog_binding ? &*state_->catalog_binding : nullptr,
            state_->label + " selective-sync snapshot");
    transaction.commit();
    return cutpoint.policy;
}

SyncReplicaSelectiveSyncPolicy
SyncReplicaFolderScanOwner::replace_selective_sync_policy_or_throw(
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    SyncSqliteTransaction transaction(
        *state_->catalog_db, state_->label + " selective-sync replacement",
        SyncSqliteTransactionMode::Immediate);
    const FolderSelectiveSyncCutpoint current =
        load_selective_sync_cutpoint_or_throw(
            *state_->catalog_db, state_->folder_id,
            state_->absolute_root_path, state_->root_attestation_digest,
            state_->catalog_binding ? &*state_->catalog_binding : nullptr,
            state_->label + " selective-sync current");
    SyncReplicaSelectiveSyncPolicy result =
        replace_selective_sync_policy_in_transaction_or_throw(
            *state_->catalog_db, current, default_mode, std::move(rules),
            state_->label);
    transaction.commit();
    return result;
}

SyncReplicaFolderScanProgressSnapshot
SyncReplicaFolderScanOwner::scan_progress_snapshot_or_throw() {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    SyncSqliteTransaction transaction(
        *state_->catalog_db, state_->label + " scan-progress snapshot",
        SyncSqliteTransactionMode::Deferred);
    const FolderScanProgressHead head = load_scan_progress_head_or_throw(
        *state_->catalog_db, state_->limits,
        state_->label + " scan-progress snapshot");
    const FolderRemoteWorkProgressHead remote_apply =
        load_remote_work_progress_head_or_throw(
            *state_->catalog_db, state_->limits,
            state_->label + " remote-apply progress snapshot");
    SyncReplicaFolderScanProgressSnapshot snapshot{
        .scan_epoch = head.scan_epoch,
        .resume_after_path = head.resume_after_path,
        .seen_path_count = head.seen_path_count,
        .seen_path_bytes = head.seen_path_bytes,
        .seen_chain_digest = head.seen_chain_digest,
        .remote_apply_resume_after_path = remote_apply.resume_after_path,
        .remote_inspection_sweep_basis_digest =
            remote_apply.inspection_sweep_basis_digest,
        .remote_inspection_sweep_started_after_path =
            remote_apply.inspection_sweep_started_after_path,
        .remote_inspection_sweep_seen_path_count =
            remote_apply.inspection_sweep_seen_path_count,
        .remote_inspection_sweep_had_unresolved_paths =
            remote_apply.inspection_sweep_had_unresolved_paths,
    };
    transaction.commit();
    return snapshot;
}

SyncReplicaPreparedRegularFile
SyncReplicaFolderScanOwner::prepare_regular_file_or_throw(
    std::string canonical_path) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    return prepare_regular_file_bounded_or_throw(
        std::move(canonical_path), state_->limits.max_payload_bytes);
}

SyncReplicaPreparedRegularFile
SyncReplicaFolderScanOwner::prepare_regular_file_bounded_or_throw(
    std::string canonical_path,
    std::uint64_t maximum_bytes) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    const SyncReplicaSelectiveSyncPolicy selective_sync_policy =
        selective_sync_policy_snapshot_or_throw();
    return prepare_regular_file_bounded_for_policy_or_throw(
        std::move(canonical_path), maximum_bytes, selective_sync_policy);
}

SyncReplicaPreparedRegularFile
SyncReplicaFolderScanOwner::prepare_regular_file_bounded_for_policy_or_throw(
    std::string canonical_path,
    std::uint64_t maximum_bytes,
    const SyncReplicaSelectiveSyncPolicy& selective_sync_policy) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_sync_replica_selective_sync_policy_or_throw(
        selective_sync_policy, state_->label + " prepared-file policy");
    if (maximum_bytes == 0U ||
        maximum_bytes > state_->limits.max_payload_bytes) {
        throw std::invalid_argument(
            state_->label +
            " prepared-file byte limit must be positive and no greater "
            "than the persisted folder limit");
    }
    validate_canonical_path_for_root_or_throw(
        canonical_path, state_->root_authority,
        state_->label + " prepare");
    if (!sync_replica_selective_sync_path_is_materialized(
            selective_sync_policy, canonical_path)) {
        throw std::runtime_error(
            state_->label +
            " prepared file is metadata-only under the current "
            "selective-sync policy");
    }

    const SyncReplicaSqliteTargetedPathCutpoint replica_path =
        state_->replica_owner->targeted_path_cutpoint_or_throw(
            canonical_path);
    std::vector<std::string> observed_visible_operation_ids;
    if (replica_path.sole_visible_operation.has_value()) {
        observed_visible_operation_ids.push_back(
            replica_path.sole_visible_operation->operation_id);
    } else if (replica_path.conflicted) {
        observed_visible_operation_ids.reserve(
            replica_path.bounded_conflict_visible_operations.size());
        for (const SyncReplicaOperation& operation :
             replica_path.bounded_conflict_visible_operations) {
            observed_visible_operation_ids.push_back(operation.operation_id);
        }
    }

    std::optional<StableRegularFileObservation> observed =
        observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            canonical_path, maximum_bytes,
            state_->label + " prepare");
    if (!observed.has_value()) {
        throw std::runtime_error(
            state_->label + " prepare regular file is absent");
    }

    auto prepared = std::make_unique<SyncReplicaPreparedRegularFile::State>();
    prepared->owner_token = state_->owner_token;
    prepared->descriptor = observed->descriptor.release();
    prepared->canonical_path = std::move(canonical_path);
    prepared->content_sha256 = std::move(observed->content_sha256);
    prepared->source_snapshot_sha256 =
        std::move(observed->source_snapshot_sha256);
    prepared->selective_sync_policy_generation =
        selective_sync_policy.generation;
    prepared->selective_sync_policy_digest =
        selective_sync_policy.policy_digest;
    prepared->observation = observed->metadata;
    prepared->observed_visible_operation_ids =
        std::move(observed_visible_operation_ids);
    return SyncReplicaPreparedRegularFile(std::move(prepared));
}

SyncReplicaFolderScanResult
SyncReplicaFolderScanOwner::commit_prepared_regular_file_or_throw(
    SyncReplicaPreparedRegularFile prepared) {
    return commit_prepared_regular_file_with_payload_batch_or_throw(
        std::move(prepared), nullptr, nullptr);
}

SyncReplicaFolderScanResult
SyncReplicaFolderScanOwner::
commit_prepared_regular_file_with_payload_batch_or_throw(
    SyncReplicaPreparedRegularFile prepared,
    SyncReplicaFilePayloadStoreMutationBatch* payload_batch,
    const SyncReplicaFilePayloadStoreSnapshot* retained_payload_snapshot) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    auto& observation = prepared.require_state_or_throw(
        state_->label + " commit");
    if (observation.owner_token.get() != state_->owner_token.get()) {
        throw std::invalid_argument(
            state_->label + " prepared file belongs to another owner");
    }

    const auto reprove_prepared_file_or_throw =
        [&](std::string_view phase) {
            const std::string phase_label =
                state_->label + " " + std::string(phase);
            const SyncPosixRegularFileSnapshotMetadata retained =
                observe_sync_posix_regular_file_descriptor_or_throw(
                    observation.descriptor,
                    SyncPosixDescriptorLinkPolicy::stable_named_object,
                    phase_label + " retained descriptor");
            if (retained != observation.observation) {
                throw std::runtime_error(
                    phase_label + " prepared file changed");
            }
            ScopedFd named = open_regular_file_beneath_root_or_throw(
                state_->root_authority, observation.canonical_path,
                phase_label + " pathname");
            const SyncPosixRegularFileSnapshotMetadata named_observation =
                observe_sync_posix_regular_file_descriptor_or_throw(
                    named.get(),
                    SyncPosixDescriptorLinkPolicy::stable_named_object,
                    phase_label + " pathname");
            if (named_observation != observation.observation) {
                throw std::runtime_error(
                    phase_label +
                    " configured pathname no longer names the prepared file");
            }
        };

    reprove_prepared_file_or_throw("initial reproof");

    const SyncReplicaSelectiveSyncPolicy selective_sync_policy =
        selective_sync_policy_snapshot_or_throw();
    if (selective_sync_policy.generation !=
            observation.selective_sync_policy_generation ||
        selective_sync_policy.policy_digest !=
            observation.selective_sync_policy_digest ||
        !sync_replica_selective_sync_path_is_materialized(
            selective_sync_policy, observation.canonical_path)) {
        throw std::runtime_error(
            state_->label +
            " prepared file selective-sync authority changed or the path "
            "is now metadata-only");
    }
    const FolderCatalogPathCutpoint catalog_path =
        load_folder_catalog_path_cutpoint_or_throw(
            *state_->catalog_db, state_->folder_id,
            state_->absolute_root_path, state_->root_attestation_digest,
            state_->limits, observation.canonical_path,
            state_->label + " prepared-file catalog path");
    if (catalog_path.selection_generation !=
            observation.selective_sync_policy_generation ||
        catalog_path.selection_digest !=
            observation.selective_sync_policy_digest) {
        throw std::runtime_error(
            state_->label +
            " prepared file catalog selection cutpoint changed");
    }
    const std::optional<SyncReplicaFolderCatalogEntry> prior =
        catalog_path.entry;
    const auto require_prepared_selection_still_current_or_throw = [&]() {
        const SyncReplicaSelectiveSyncPolicy current =
            selective_sync_policy_snapshot_or_throw();
        if (current.generation !=
                observation.selective_sync_policy_generation ||
            current.policy_digest !=
                observation.selective_sync_policy_digest ||
            !sync_replica_selective_sync_path_is_materialized(
                current, observation.canonical_path)) {
            throw std::runtime_error(
                state_->label +
                " prepared file selective-sync authority changed before "
                "publication");
        }
    };

    const SyncReplicaSqliteTargetedPathCutpoint fresh_path =
        state_->replica_owner->targeted_path_cutpoint_or_throw(
            observation.canonical_path,
            prior.has_value()
                ? std::optional<std::string>{prior->operation_id}
                : std::nullopt);
    std::vector<SyncReplicaOperation> fresh_visible;
    std::vector<std::string> fresh_ids;
    if (fresh_path.sole_visible_operation.has_value()) {
        fresh_visible.push_back(*fresh_path.sole_visible_operation);
        fresh_ids.push_back(
            fresh_path.sole_visible_operation->operation_id);
    } else if (fresh_path.conflicted) {
        fresh_visible = fresh_path.bounded_conflict_visible_operations;
        fresh_ids.reserve(fresh_visible.size());
        for (const SyncReplicaOperation& operation : fresh_visible) {
            fresh_ids.push_back(operation.operation_id);
        }
    }
    const std::vector<std::string>& observed_ids =
        observation.observed_visible_operation_ids;

    std::optional<SyncReplicaOperation> prior_operation;
    bool prior_is_visible = false;
    if (prior.has_value()) {
        const SyncReplicaOperation* retained =
            fresh_path.requested_retained_operation_or_none();
        if (retained == nullptr ||
            !operation_matches_catalog_entry(*retained, *prior)) {
            throw std::runtime_error(
                state_->label +
                " catalog mapping disagrees with retained replica evidence");
        }
        prior_operation = *retained;
        prior_is_visible = std::find(
            fresh_ids.begin(), fresh_ids.end(), prior->operation_id) !=
            fresh_ids.end();
    }

    SyncReplicaFolderScanDisposition disposition =
        SyncReplicaFolderScanDisposition::CatalogNoOp;
    std::optional<SyncReplicaOperation> selected;
    std::optional<SyncReplicaOperation> published;
    std::optional<SyncReplicaSqlitePreparedLocalFilePublication>
        publication_plan;
    std::optional<LocalIdentityPreservingRenameCandidate> rename_candidate;
    std::optional<SyncReplicaSqliteLocalRenamePublicationResult>
        rename_publication;

    // Prefer the exact cataloged operation when it is still visible and still
    // describes the materialized bytes. This keeps duplicate watcher hints from
    // switching between equivalent concurrent evidence records.
    if (prior.has_value() && prior_is_visible &&
        prior->size_bytes == observation.observation.size_bytes &&
        prior->content_sha256 == observation.content_sha256) {
        selected = *prior_operation;
        disposition = SyncReplicaFolderScanDisposition::CatalogNoOp;
    } else if (const auto matching = matching_visible_operation(
                   fresh_visible, observation.canonical_path,
                   observation.observation.size_bytes,
                   observation.content_sha256);
               matching.has_value()) {
        selected = *matching;
        disposition =
            SyncReplicaFolderScanDisposition::AdoptedVisibleOperation;
    } else {
        if (fresh_ids != observed_ids) {
            throw std::runtime_error(
                state_->label +
                " replica path heads changed after file observation");
        }

        // A cataloged operation is the causal base of the materialized local
        // file. If that operation is no longer a visible head, current replica
        // evidence has advanced beyond the working tree. Publishing the bytes as
        // a successor of the newer head would falsely claim that the local edit
        // observed and superseded it. The apply/reconciliation owner must first
        // establish a new materialized base (or an explicit conflict decision).
        if (prior.has_value() && !prior_is_visible) {
            throw std::runtime_error(
                state_->label +
                " replica path advanced beyond the cataloged local base; "
                "apply or reconcile before local publication");
        }

        // With no cataloged base, differing local and replicated values are a
        // populated-target collision. There is no evidence that the local bytes
        // observed the existing replica head, so ordinary scanning cannot turn
        // them into its successor.
        if (!prior.has_value() && !fresh_ids.empty()) {
            throw std::runtime_error(
                state_->label +
                " uncataloged local file collides with an existing replica "
                "path; explicit adoption or conflict handling is required");
        }
        if (fresh_ids.size() > 1U) {
            throw std::runtime_error(
                state_->label +
                " unresolved path conflict requires explicit resolution");
        }
        // A newly observed destination with no causal value may be the other
        // half of one exact-content local move. Both durable owners answer the
        // content query through startup-attested indexes and decode at most two
        // rows. Any catalog/replica disagreement or duplicate content falls back
        // to ordinary create/delete semantics before payload authority.
        if (!prior.has_value() && fresh_ids.empty()) {
            const FolderCatalogFileContentCutpoint catalog_content =
                load_folder_catalog_file_content_cutpoint_or_throw(
                    *state_->catalog_db, state_->folder_id,
                    state_->absolute_root_path,
                    state_->root_attestation_digest,
                    state_->catalog_binding
                        ? &*state_->catalog_binding
                        : nullptr,
                    observation.observation.size_bytes,
                    observation.content_sha256,
                    state_->label + " local rename catalog content");
            const SyncReplicaSqliteVisibleFileContentCutpoint replica_content =
                state_->replica_owner->
                    visible_file_content_cutpoint_or_throw(
                        observation.observation.size_bytes,
                        observation.content_sha256);
            rename_candidate =
                find_unique_absent_identity_preserving_rename_source_or_none(
                    catalog_content, replica_content,
                    selective_sync_policy, state_->root_authority,
                    observation.canonical_path,
                    observation.observation.size_bytes,
                    observation.content_sha256,
                    state_->label + " local rename planning");
        }
        if (!rename_candidate.has_value()) {
            publication_plan =
                state_->replica_owner->
                    prepare_local_file_from_observed_heads_or_throw(
                        observation.canonical_path, observed_ids,
                        observation.observation.size_bytes,
                        observation.content_sha256);
        }
    }

    // Indexed planning remains bounded but crosses two durable owners. Re-prove
    // the exact descriptor and root-relative name after those cutpoints, before
    // durable payload admission or evidence publication.
    reprove_prepared_file_or_throw("pre-payload reproof");
    const SyncReplicaOperation& payload_operation = selected.has_value()
        ? *selected
        : publication_plan.has_value()
            ? publication_plan->operation
            : rename_candidate->source_file_operation;
    const auto require_retained_payload_match_or_throw = [&] (
        const SyncReplicaFilePayloadStoreOpenedPayload& retained_payload,
        std::string_view stage) {
        if (!retained_payload.active() ||
            retained_payload.size_bytes() !=
                observation.observation.size_bytes ||
            retained_payload.content_sha256() !=
                observation.content_sha256) {
            throw std::logic_error(
                state_->label + " " + std::string(stage) +
                " changed the observed content");
        }
    };

    bool retained_payload_proved = false;
    bool targeted_payload_reuse = false;
    // Keep both the bounded targeted owner and the exact-inode payload
    // capability alive until the function returns. Cooperative quarantine or
    // collection cannot invalidate the payload-before-metadata cutpoint between
    // this proof and replica/catalog publication.
    std::optional<SyncReplicaFilePayloadStoreTargetedAccess>
        targeted_payload_access;
    std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
        retained_payload_lease;
    if (retained_payload_snapshot != nullptr) {
        retained_payload_lease.emplace(
            retained_payload_snapshot->open_payload_for_operation_or_throw(
                payload_operation,
                state_->label + " retained payload reproof"));
        require_retained_payload_match_or_throw(
            *retained_payload_lease, "retained payload proof");
        retained_payload_proved = true;
    } else if (payload_batch == nullptr && !publication_plan.has_value()) {
        // A direct exact-content scan has already selected one retained file
        // operation (or one retained rename source). Re-open that digest through
        // the bounded targeted lane instead of rereading a potentially
        // multi-terabyte descriptor merely to rediscover its immutable payload.
        // This targeted proof is deliberately not complete payload-namespace
        // health or capacity authority; the ordinary convergence snapshot keeps
        // that role. Genuine absence falls through to descriptor admission.
        targeted_payload_access.emplace(
            state_->payload_store->begin_targeted_access_or_throw(
                state_->label + " direct retained payload reuse"));
        retained_payload_lease =
            targeted_payload_access->
                open_optional_payload_for_operation_or_throw(
                    payload_operation,
                    state_->label + " direct retained payload reuse");
        if (retained_payload_lease.has_value()) {
            require_retained_payload_match_or_throw(
                *retained_payload_lease,
                "targeted retained payload proof");
            retained_payload_proved = true;
            targeted_payload_reuse = true;
        } else {
            targeted_payload_access.reset();
        }
    }
    if (!retained_payload_proved) {
        const SyncReplicaFilePayloadStorePutResult payload =
            payload_batch == nullptr
                ? state_->payload_store->
                      put_payload_from_borrowed_descriptor_or_throw(
                          observation.descriptor, observation.observation,
                          observation.content_sha256)
                : payload_batch->put_payload_from_borrowed_descriptor_or_throw(
                      observation.descriptor, observation.observation,
                      observation.content_sha256);
        if (payload.size_bytes != observation.observation.size_bytes ||
            payload.content_sha256 != observation.content_sha256) {
            throw std::logic_error(
                state_->label + " payload store changed the observed content");
        }
    }

    if (rename_candidate.has_value()) {
        require_prepared_selection_still_current_or_throw();
        const SyncReplicaSelectiveSyncPolicy selection_reproof =
            selective_sync_policy_snapshot_or_throw();
        if (selection_reproof.generation !=
                observation.selective_sync_policy_generation ||
            selection_reproof.policy_digest !=
                observation.selective_sync_policy_digest ||
            !sync_replica_selective_sync_path_is_materialized(
                selection_reproof,
                rename_candidate->source_catalog_entry.canonical_path)) {
            throw std::runtime_error(
                state_->label +
                " local rename source selective-sync authority changed");
        }
        const SyncReplicaSqliteTargetedPathCutpoint source_replica_reproof =
            state_->replica_owner->targeted_path_cutpoint_or_throw(
                rename_candidate->source_catalog_entry.canonical_path,
                rename_candidate->source_file_operation.operation_id);
        const SyncReplicaOperation* retained_source =
            source_replica_reproof.requested_retained_operation_or_none();
        if (source_replica_reproof.conflicted ||
            !source_replica_reproof.sole_visible_operation.has_value() ||
            source_replica_reproof.sole_visible_operation->operation_id !=
                rename_candidate->source_file_operation.operation_id ||
            retained_source == nullptr ||
            *retained_source != rename_candidate->source_file_operation) {
            throw std::runtime_error(
                state_->label +
                " local rename source replica authority changed");
        }

        reprove_prepared_file_or_throw("rename destination durability reproof");
        if (open_optional_regular_file_beneath_root_or_throw(
                state_->root_authority,
                rename_candidate->source_catalog_entry.canonical_path,
                state_->label + " local rename source prepublication")
                .has_value()) {
            throw std::runtime_error(
                state_->label +
                " local rename source reappeared before publication");
        }

        // The causal pair claims both a durable destination name and durable
        // source absence. Synchronize both rooted namespace facts before the
        // database can publish them, then re-prove both facts across the barriers.
        synchronize_regular_file_descriptor_and_parent_or_throw(
            state_->root_authority, observation.canonical_path,
            observation.descriptor, observation.observation,
            state_->label + " local rename destination");
        synchronize_absent_path_parent_or_throw(
            state_->root_authority,
            rename_candidate->source_catalog_entry.canonical_path,
            state_->label + " local rename source");
        reprove_prepared_file_or_throw("rename destination prepublication");
        if (open_optional_regular_file_beneath_root_or_throw(
                state_->root_authority,
                rename_candidate->source_catalog_entry.canonical_path,
                state_->label + " local rename source terminal reproof")
                .has_value()) {
            throw std::runtime_error(
                state_->label +
                " local rename source appeared during synchronization");
        }

        rename_publication = state_->replica_owner->
            publish_local_identity_preserving_rename_from_observed_heads_or_throw(
                rename_candidate->source_catalog_entry.canonical_path,
                std::vector<std::string>{
                    rename_candidate->source_file_operation.operation_id},
                observation.canonical_path, observed_ids,
                observation.observation.size_bytes,
                observation.content_sha256);
        selected = rename_publication->destination_file_operation;
        published = rename_publication->destination_file_operation;
        disposition = SyncReplicaFolderScanDisposition::Published;
    }

    if (publication_plan.has_value()) {
        require_prepared_selection_still_current_or_throw();
        const SyncReplicaSqlitePreparedPublicationResult publication =
            state_->replica_owner->commit_prepared_local_file_or_throw(
                *publication_plan);
        if (publication.disposition ==
            SyncReplicaSqlitePreparedPublicationDisposition::StaleCutpoint) {
            throw std::runtime_error(
                state_->label +
                " replica publication cutpoint changed after payload admission");
        }
        selected = publication_plan->operation;
        if (publication.disposition ==
            SyncReplicaSqlitePreparedPublicationDisposition::Published) {
            published = publication_plan->operation;
            disposition = SyncReplicaFolderScanDisposition::Published;
        } else {
            disposition =
                SyncReplicaFolderScanDisposition::AdoptedVisibleOperation;
        }
    }

    // A publication can become durable before a catalog transaction. Refusing
    // a changed file here leaves the catalog untouched; the next scan adopts
    // the exact retained operation instead of minting another one.
    reprove_prepared_file_or_throw("pre-catalog reproof");
    require_prepared_selection_still_current_or_throw();

    if (!selected.has_value()) {
        throw std::logic_error(
            state_->label + " did not select a catalog operation");
    }
    SyncReplicaFolderCatalogEntry entry;
    entry.canonical_path = observation.canonical_path;
    entry.kind = SyncReplicaValueKind::File;
    entry.size_bytes = observation.observation.size_bytes;
    entry.content_sha256 = observation.content_sha256;
    entry.operation_id = selected->operation_id;
    entry.source_snapshot_sha256 = observation.source_snapshot_sha256;

    if (rename_publication.has_value()) {
        if (!rename_candidate.has_value()) {
            throw std::logic_error(
                state_->label + " local rename lost its source candidate");
        }
        if (open_optional_regular_file_beneath_root_or_throw(
                state_->root_authority,
                rename_candidate->source_catalog_entry.canonical_path,
                state_->label + " local rename pre-catalog source reproof")
                .has_value()) {
            throw std::runtime_error(
                state_->label +
                " local rename source appeared before catalog commit");
        }
        SyncReplicaFolderCatalogEntry source_tombstone;
        source_tombstone.canonical_path =
            rename_candidate->source_catalog_entry.canonical_path;
        source_tombstone.kind = SyncReplicaValueKind::Tombstone;
        source_tombstone.operation_id =
            rename_publication->source_tombstone_operation.operation_id;
        CatalogRenameRecordResult recorded =
            record_catalog_identity_preserving_rename_or_throw(
                *state_->catalog_db, state_->folder_id,
                state_->absolute_root_path,
                state_->root_attestation_digest,
                state_->catalog_binding ? &*state_->catalog_binding : nullptr,
                rename_candidate->source_catalog_entry, prior,
                std::move(source_tombstone), std::move(entry),
                state_->label + " local rename");
        return {
            disposition,
            std::move(recorded.destination_file_entry),
            std::move(published),
            rename_publication->identity,
            targeted_payload_reuse};
    }

    CatalogRecordResult recorded = record_catalog_entry_or_throw(
        *state_->catalog_db, state_->folder_id, state_->absolute_root_path,
        state_->root_attestation_digest,
        state_->catalog_binding ? &*state_->catalog_binding : nullptr,
        prior, std::move(entry),
        state_->label);
    if (disposition == SyncReplicaFolderScanDisposition::CatalogNoOp &&
        recorded.changed) {
        disposition = SyncReplicaFolderScanDisposition::CatalogRefreshed;
    }

    return {
        disposition, std::move(recorded.entry), std::move(published),
        std::nullopt, targeted_payload_reuse};
}

SyncReplicaFolderScanResult
SyncReplicaFolderScanOwner::scan_regular_file_or_throw(
    std::string canonical_path) {
    return commit_prepared_regular_file_or_throw(
        prepare_regular_file_or_throw(std::move(canonical_path)));
}

SyncReplicaFolderScanResult
SyncReplicaFolderScanOwner::commit_complete_scan_absence_or_throw(
    std::string canonical_path) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_canonical_path_for_root_or_throw(
        canonical_path, state_->root_authority,
        state_->label + " complete-scan absence");

    const SyncReplicaFolderCatalogSnapshot catalog = snapshot_or_throw();
    const std::optional<SyncReplicaFolderCatalogEntry> prior =
        find_catalog_entry(catalog, canonical_path);
    if (!prior.has_value() ||
        prior->kind != SyncReplicaValueKind::File) {
        throw std::logic_error(
            state_->label +
            " complete-scan absence requires one cataloged file base");
    }
    if (observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            canonical_path, state_->limits.max_payload_bytes,
            state_->label + " complete-scan absence reproof")
            .has_value()) {
        throw std::runtime_error(
            state_->label +
            " complete-scan absent path became a regular file");
    }

    const SyncReplicaSqliteSnapshot replica_snapshot =
        state_->replica_owner->snapshot_or_throw();
    const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
        replica_snapshot.durable, replica_snapshot.limits.model);
    const SyncReplicaOperation prior_operation =
        require_catalog_operation_or_throw(
            model, *prior, state_->label + " complete-scan absence");
    const std::vector<SyncReplicaOperation> visible =
        visible_operations(model, canonical_path);
    const std::vector<std::string> observed_ids = operation_ids(visible);
    if (visible.size() != 1U) {
        throw std::runtime_error(
            state_->label +
            " local deletion conflicts with unresolved replica path heads");
    }

    SyncReplicaOperation selected;
    std::optional<SyncReplicaOperation> published;
    SyncReplicaFolderScanDisposition disposition =
        SyncReplicaFolderScanDisposition::AdoptedVisibleOperation;
    if (visible.front().kind == SyncReplicaValueKind::Tombstone) {
        if (!sync_replica_operation_supersedes(
                visible.front(), prior_operation)) {
            throw std::runtime_error(
                state_->label +
                " visible tombstone does not cover the cataloged file base");
        }
        selected = visible.front();
    } else if (visible.front().operation_id == prior->operation_id) {
        // The complete traversal established absence. Synchronize the retained
        // parent and then bind publication to the exact path heads observed
        // above; a remote edit admitted in either gap invalidates the mint.
        synchronize_absent_path_parent_or_throw(
            state_->root_authority, canonical_path,
            state_->label + " local deletion");
        if (observe_optional_regular_file_beneath_root_or_throw(
                state_->root_authority, state_->root_attestation_digest,
                canonical_path, state_->limits.max_payload_bytes,
                state_->label + " local deletion prepublication")
                .has_value()) {
            throw std::runtime_error(
                state_->label +
                " local deletion path appeared before publication");
        }
        selected = state_->replica_owner->
            publish_local_tombstone_from_observed_heads_or_throw(
                canonical_path, observed_ids);
        published = selected;
        disposition = SyncReplicaFolderScanDisposition::Published;
    } else {
        throw std::runtime_error(
            state_->label +
            " local deletion conflicts with a newer visible file value");
    }

    if (observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            canonical_path, state_->limits.max_payload_bytes,
            state_->label + " local deletion terminal reproof")
            .has_value()) {
        throw std::runtime_error(
            state_->label +
            " local deletion path appeared before catalog commit");
    }
    const SyncReplicaSqliteSnapshot terminal_snapshot =
        state_->replica_owner->snapshot_or_throw();
    const SyncReplicaModel terminal_model = SyncReplicaModel::restore_or_throw(
        terminal_snapshot.durable, terminal_snapshot.limits.model);
    const SyncReplicaOperation terminal =
        require_sole_visible_tombstone_operation_or_throw(
            terminal_model, selected.operation_id,
            state_->label + " local deletion terminal");
    if (terminal != selected) {
        throw std::runtime_error(
            state_->label +
            " local deletion target changed before catalog commit");
    }

    SyncReplicaFolderCatalogEntry entry;
    entry.canonical_path = canonical_path;
    entry.kind = SyncReplicaValueKind::Tombstone;
    entry.operation_id = selected.operation_id;
    CatalogRecordResult recorded = record_catalog_entry_or_throw(
        *state_->catalog_db, state_->folder_id, state_->absolute_root_path,
        state_->root_attestation_digest,
        state_->catalog_binding ? &*state_->catalog_binding : nullptr,
        prior, std::move(entry), state_->label + " local deletion");
    if (disposition == SyncReplicaFolderScanDisposition::AdoptedVisibleOperation &&
        !recorded.changed) {
        disposition = SyncReplicaFolderScanDisposition::CatalogNoOp;
    }
    return {
        disposition, std::move(recorded.entry), std::move(published),
        std::nullopt};
}

SyncReplicaFolderApplyResult
SyncReplicaFolderScanOwner::apply_visible_tombstone_or_throw(
    std::string operation_id) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }

    const auto load_target_or_throw = [&]() {
        const SyncReplicaSqliteSnapshot replica_snapshot =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
            replica_snapshot.durable, replica_snapshot.limits.model);
        return require_sole_visible_tombstone_operation_or_throw(
            model, operation_id, state_->label + " tombstone apply");
    };

    const SyncReplicaOperation target = load_target_or_throw();
    validate_canonical_path_for_root_or_throw(
        target.canonical_path, state_->root_authority,
        state_->label + " tombstone apply");

    const SyncReplicaFolderCatalogSnapshot catalog = snapshot_or_throw();
    const std::optional<SyncReplicaFolderCatalogEntry> prior =
        find_catalog_entry(catalog, target.canonical_path);
    if (prior.has_value()) {
        const SyncReplicaSqliteSnapshot replica_snapshot =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
            replica_snapshot.durable, replica_snapshot.limits.model);
        const SyncReplicaOperation prior_operation =
            require_catalog_operation_or_throw(
                model, *prior, state_->label + " tombstone apply");
        if (target.operation_id != prior_operation.operation_id &&
            !sync_replica_operation_supersedes(target, prior_operation)) {
            throw std::runtime_error(
                state_->label +
                " tombstone does not causally supersede the cataloged local "
                "base");
        }
    }

    const auto observe_path_or_throw = [&]() {
        return observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            target.canonical_path, state_->limits.max_payload_bytes,
            state_->label + " tombstone target");
    };
    const auto require_target_still_current_or_throw = [&]() {
        const SyncReplicaOperation current = load_target_or_throw();
        if (current != target) {
            throw std::runtime_error(
                state_->label +
                " tombstone target changed after its planning cutpoint");
        }
    };
    const auto require_catalog_path_still_prior_or_throw = [&]() {
        const SyncReplicaFolderCatalogSnapshot fresh = snapshot_or_throw();
        if (find_catalog_entry(fresh, target.canonical_path) != prior) {
            throw std::runtime_error(
                state_->label +
                " catalog path changed before tombstone completion");
        }
    };
    const auto finish_absent_or_throw =
        [&](SyncReplicaFolderApplyDisposition disposition,
            bool synchronize_absence) {
            require_target_still_current_or_throw();
            require_catalog_path_still_prior_or_throw();
            if (observe_path_or_throw().has_value()) {
                throw std::runtime_error(
                    state_->label +
                    " tombstone target is no longer absent");
            }
            if (synchronize_absence) {
                synchronize_absent_path_parent_or_throw(
                    state_->root_authority, target.canonical_path,
                    state_->label + " tombstone recovery");
            }
            require_target_still_current_or_throw();
            require_catalog_path_still_prior_or_throw();
            if (observe_path_or_throw().has_value()) {
                throw std::runtime_error(
                    state_->label +
                    " tombstone target appeared before catalog commit");
            }

            SyncReplicaFolderCatalogEntry entry;
            entry.canonical_path = target.canonical_path;
            entry.kind = SyncReplicaValueKind::Tombstone;
            entry.operation_id = target.operation_id;
            CatalogRecordResult recorded = record_catalog_entry_or_throw(
                *state_->catalog_db, state_->folder_id,
                state_->absolute_root_path,
                state_->root_attestation_digest,
                state_->catalog_binding ? &*state_->catalog_binding : nullptr,
                prior, std::move(entry),
                state_->label + " tombstone apply");
            if (!recorded.changed) {
                disposition =
                    SyncReplicaFolderApplyDisposition::CatalogNoOp;
            }
            return SyncReplicaFolderApplyResult{
                disposition, std::move(recorded.entry), target};
        };

    std::optional<StableRegularFileObservation> current =
        observe_path_or_throw();
    if (!current.has_value()) {
        if (prior.has_value() &&
            prior->kind == SyncReplicaValueKind::Tombstone &&
            prior->operation_id == target.operation_id) {
            require_target_still_current_or_throw();
            return SyncReplicaFolderApplyResult{
                SyncReplicaFolderApplyDisposition::CatalogNoOp,
                *prior, target};
        }
        return finish_absent_or_throw(
            SyncReplicaFolderApplyDisposition::AdoptedExactTarget, true);
    }

    if (!prior.has_value()) {
        throw std::runtime_error(
            state_->label +
            " uncataloged local file collides with the remote tombstone");
    }
    if (prior->kind != SyncReplicaValueKind::File ||
        !observation_matches_catalog_entry(*current, *prior)) {
        throw std::runtime_error(
            state_->label +
            " local path changed from the cataloged predecessor before "
            "tombstone apply");
    }

    require_target_still_current_or_throw();
    require_catalog_path_still_prior_or_throw();
    std::optional<StableRegularFileObservation> unlink_base =
        observe_path_or_throw();
    if (!unlink_base.has_value() ||
        !observation_matches_catalog_entry(*unlink_base, *prior) ||
        unlink_base->metadata != current->metadata) {
        throw std::runtime_error(
            state_->label +
            " local predecessor changed before tombstone unlink");
    }
    remove_sync_file_atomically_if_expected_under_directory_or_throw(
        state_->root_authority, fs::path(target.canonical_path),
        unlink_base->metadata, state_->label + " tombstone removal");
    return finish_absent_or_throw(
        SyncReplicaFolderApplyDisposition::Applied, false);
}

SyncReplicaFolderApplyResult
SyncReplicaFolderScanOwner::apply_visible_regular_file_or_throw(
    std::string operation_id) {
    return apply_visible_regular_file_with_payload_snapshot_or_throw(
        std::move(operation_id), nullptr);
}

SyncReplicaFolderApplyResult
SyncReplicaFolderScanOwner::
    apply_visible_regular_file_with_payload_snapshot_or_throw(
        std::string operation_id,
        const SyncReplicaFilePayloadStoreSnapshot*
            retained_payload_snapshot) {
    std::optional<SyncReplicaFolderApplyResult> applied =
        apply_visible_regular_file_with_payload_strategy_or_throw(
            std::move(operation_id), retained_payload_snapshot, nullptr);
    if (!applied.has_value()) {
        throw std::logic_error(
            "snapshot-backed remote apply reported an absent payload");
    }
    return std::move(*applied);
}

std::optional<SyncReplicaFolderApplyResult>
SyncReplicaFolderScanOwner::
    try_apply_visible_regular_file_with_targeted_payload_or_throw(
        std::string operation_id,
        SyncReplicaFilePayloadStoreTargetedAccess&
            targeted_payload_access) {
    return apply_visible_regular_file_with_payload_strategy_or_throw(
        std::move(operation_id), nullptr, &targeted_payload_access);
}

std::optional<SyncReplicaFolderApplyResult>
SyncReplicaFolderScanOwner::
    apply_visible_regular_file_with_payload_strategy_or_throw(
        std::string operation_id,
        const SyncReplicaFilePayloadStoreSnapshot*
            retained_payload_snapshot,
        SyncReplicaFilePayloadStoreTargetedAccess*
            targeted_payload_access) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }

    const auto load_target_or_throw = [&]() {
        const SyncReplicaSqliteSnapshot replica_snapshot =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
            replica_snapshot.durable, replica_snapshot.limits.model);
        return require_sole_visible_file_operation_or_throw(
            model, operation_id, state_->label + " apply");
    };

    const SyncReplicaOperation target = load_target_or_throw();
    validate_canonical_path_for_root_or_throw(
        target.canonical_path, state_->root_authority,
        state_->label + " apply");

    const SyncReplicaFolderCatalogSnapshot catalog = snapshot_or_throw();
    if (!sync_replica_selective_sync_path_is_materialized(
            catalog.selective_sync_policy, target.canonical_path)) {
        throw std::runtime_error(
            state_->label +
            " apply target is metadata-only under the current "
            "selective-sync policy");
    }

    // Retain the exact opened payload descriptor through the filesystem/catalog
    // protocol. The public one-path API and any pass that already owns a complete
    // inventory use snapshot selection. A remote-only bounded pass instead uses
    // the store's one-digest lease-proved selection and can report exact absence
    // without scanning unrelated payloads. In both lanes the returned descriptor
    // remains the byte capability and carries a shared exact-inode use lease;
    // no store-wide lease is held across potentially large destination I/O.
    std::optional<SyncReplicaFilePayloadStoreSnapshot> owned_payload_snapshot;
    std::optional<SyncReplicaFilePayloadStoreOpenedPayload> selected_payload;
    if (targeted_payload_access != nullptr) {
        if (retained_payload_snapshot != nullptr) {
            throw std::logic_error(
                state_->label +
                " targeted payload selection cannot consume a full snapshot");
        }
        std::optional<SyncReplicaFilePayloadStoreOpenedPayload> selected =
            targeted_payload_access->
                open_optional_payload_for_operation_or_throw(
                    target, state_->label + " targeted apply payload");
        if (!selected.has_value()) return std::nullopt;
        selected_payload.emplace(std::move(*selected));
    } else {
        if (retained_payload_snapshot == nullptr) {
            owned_payload_snapshot.emplace(
                state_->payload_store->snapshot_or_throw());
            retained_payload_snapshot = &*owned_payload_snapshot;
        }
        retained_payload_snapshot->require_folder_or_throw(
            state_->folder_id, state_->label + " apply payload snapshot");
        selected_payload.emplace(
            retained_payload_snapshot->open_payload_for_operation_or_throw(
                target, state_->label + " apply payload"));
    }
    SyncReplicaFilePayloadStoreOpenedPayload& payload = *selected_payload;
    if (payload.size_bytes() != target.size_bytes ||
        payload.content_sha256() != target.content_sha256) {
        throw std::logic_error(
            state_->label + " payload lookup changed the target identity");
    }

    const std::optional<SyncReplicaFolderCatalogEntry> prior =
        find_catalog_entry(catalog, target.canonical_path);
    const bool selection_rehydration_fence_active =
        catalog.selective_sync_absence_fence_generation != 0U &&
        catalog.selective_sync_absence_fence_generation ==
            catalog.selective_sync_policy.generation &&
        sync_replica_selective_sync_path_is_materialized(
            catalog.selective_sync_policy, target.canonical_path);

    if (prior.has_value()) {
        const SyncReplicaSqliteSnapshot replica_snapshot =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
            replica_snapshot.durable, replica_snapshot.limits.model);
        const SyncReplicaOperation prior_operation =
            require_catalog_operation_or_throw(
                model, *prior, state_->label + " apply");
        if (target.operation_id != prior_operation.operation_id &&
            !sync_replica_operation_supersedes(target, prior_operation)) {
            throw std::runtime_error(
                state_->label +
                " apply target does not causally supersede the cataloged "
                "local base");
        }
    }

    const auto observe_path_or_throw = [&]() {
        return observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            target.canonical_path, state_->limits.max_payload_bytes,
            state_->label + " apply target");
    };

    const auto require_target_still_current_or_throw = [&]() {
        const SyncReplicaOperation current = load_target_or_throw();
        if (current != target) {
            throw std::runtime_error(
                state_->label +
                " apply target changed after its planning cutpoint");
        }
    };

    const auto finish_exact_target_or_throw =
        [&](StableRegularFileObservation observation,
            SyncReplicaFolderApplyDisposition disposition,
            bool synchronize_before_catalog) {
            require_target_still_current_or_throw();
            if (!observation_matches_operation(observation, target)) {
                throw std::runtime_error(
                    state_->label +
                    " apply terminal file does not match the target "
                    "operation");
            }
            if (synchronize_before_catalog) {
                synchronize_observed_regular_file_and_parent_or_throw(
                    state_->root_authority, target.canonical_path,
                    observation, state_->label + " apply recovery");
                std::optional<StableRegularFileObservation> reproved =
                    observe_path_or_throw();
                if (!reproved.has_value() ||
                    !observation_matches_operation(*reproved, target)) {
                    throw std::runtime_error(
                        state_->label +
                        " apply recovery target changed after durability "
                        "synchronization");
                }
                observation = std::move(*reproved);
            }
            require_target_still_current_or_throw();

            SyncReplicaFolderCatalogEntry entry;
            entry.canonical_path = target.canonical_path;
            entry.kind = SyncReplicaValueKind::File;
            entry.size_bytes = target.size_bytes;
            entry.content_sha256 = target.content_sha256;
            entry.operation_id = target.operation_id;
            entry.source_snapshot_sha256 =
                observation.source_snapshot_sha256;
            CatalogRecordResult recorded = record_catalog_entry_or_throw(
                *state_->catalog_db, state_->folder_id,
                state_->absolute_root_path,
                state_->root_attestation_digest,
                state_->catalog_binding ? &*state_->catalog_binding : nullptr,
                prior, std::move(entry), state_->label + " apply");
            if (!recorded.changed) {
                disposition =
                    SyncReplicaFolderApplyDisposition::CatalogNoOp;
            }
            return SyncReplicaFolderApplyResult{
                disposition, std::move(recorded.entry), target};
        };

    std::optional<StableRegularFileObservation> current =
        observe_path_or_throw();
    bool rehydrating_cataloged_exact_target = false;
    if (current.has_value() &&
        observation_matches_operation(*current, target)) {
        if (prior.has_value() &&
            prior->operation_id == target.operation_id &&
            observation_matches_catalog_entry(*current, *prior)) {
            require_target_still_current_or_throw();
            return SyncReplicaFolderApplyResult{
                SyncReplicaFolderApplyDisposition::CatalogNoOp,
                *prior, target};
        }
        return finish_exact_target_or_throw(
            std::move(*current),
            SyncReplicaFolderApplyDisposition::AdoptedExactTarget, true);
    }

    if (!prior.has_value()) {
        if (current.has_value()) {
            throw std::runtime_error(
                state_->label +
                " uncataloged local file collides with the remote apply "
                "target");
        }
    } else if (prior->kind == SyncReplicaValueKind::File) {
        if (!current.has_value() && selection_rehydration_fence_active) {
            // The prior metadata-only policy deliberately withheld local
            // absence authority. Its exact expansion fence therefore permits
            // materializing either the retained catalog head or a current
            // causal successor without requiring the intentionally removed
            // predecessor to reappear first. The causal supersession check
            // above and the policy/fence reproof below remain mandatory.
            rehydrating_cataloged_exact_target = true;
        }
        if (target.operation_id == prior->operation_id &&
            !rehydrating_cataloged_exact_target) {
            if (current.has_value()) {
                throw std::runtime_error(
                    state_->label +
                    " cataloged target bytes changed before remote apply");
            }
            throw std::runtime_error(
                state_->label +
                " cataloged target is no longer materialized at its path");
        }
        if (!current.has_value() &&
            !rehydrating_cataloged_exact_target) {
            throw std::runtime_error(
                state_->label +
                " cataloged predecessor is absent before remote apply");
        }
        if (!rehydrating_cataloged_exact_target &&
            !observation_matches_catalog_entry(*current, *prior)) {
            throw std::runtime_error(
                state_->label +
                " local path changed from the cataloged predecessor before "
                "remote apply");
        }
    } else {
        if (current.has_value()) {
            throw std::runtime_error(
                state_->label +
                " local file collides with a remote resurrection over the "
                "cataloged tombstone");
        }
    }

    const auto require_catalog_path_still_prior_or_throw = [&]() {
        const SyncReplicaFolderCatalogSnapshot catalog_reproof =
            snapshot_or_throw();
        if (find_catalog_entry(catalog_reproof, target.canonical_path) != prior) {
            throw std::runtime_error(
                state_->label +
                " catalog path changed before remote apply publication");
        }
        if (catalog_reproof.selective_sync_policy.generation !=
                catalog.selective_sync_policy.generation ||
            catalog_reproof.selective_sync_policy.policy_digest !=
                catalog.selective_sync_policy.policy_digest ||
            !sync_replica_selective_sync_path_is_materialized(
                catalog_reproof.selective_sync_policy,
                target.canonical_path)) {
            throw std::runtime_error(
                state_->label +
                " selective-sync materialization authority changed before "
                "remote apply publication");
        }
        if (rehydrating_cataloged_exact_target &&
            (catalog_reproof.selective_sync_policy !=
                 catalog.selective_sync_policy ||
             catalog_reproof.selective_sync_absence_fence_generation !=
                 catalog.selective_sync_absence_fence_generation)) {
            throw std::runtime_error(
                state_->label +
                " selective-sync materialization authority changed before publication");
        }
    };

    // Recheck both path-local owners immediately before the namespace effect.
    // Unrelated catalog and replica activity is allowed; only this path's exact
    // materialized base and sole visible target are fenced.
    require_target_still_current_or_throw();
    require_catalog_path_still_prior_or_throw();
    std::optional<StableRegularFileObservation> publication_base =
        observe_path_or_throw();
    if (prior.has_value() &&
        prior->kind == SyncReplicaValueKind::File &&
        !rehydrating_cataloged_exact_target) {
        if (!publication_base.has_value() ||
            !observation_matches_catalog_entry(*publication_base, *prior) ||
            publication_base->metadata != current->metadata) {
            throw std::runtime_error(
                state_->label +
                " local predecessor changed before atomic replacement");
        }
    } else {
        if (publication_base.has_value()) {
            if (observation_matches_operation(*publication_base, target)) {
                return finish_exact_target_or_throw(
                    std::move(*publication_base),
                    SyncReplicaFolderApplyDisposition::AdoptedExactTarget,
                    true);
            }
            throw std::runtime_error(
                state_->label +
                " remote apply target appeared after absence observation");
        }

        // Directories are currently structural rather than replicated values.
        // Create only the missing parent chain, rooted beneath the retained
        // folder descriptor, after every remote candidate has passed the
        // whole-pass preflight. Unsafe or mount-crossing components still stop.
        ensure_relative_parent_beneath_root_or_throw(
            state_->root_authority, target.canonical_path,
            state_->label + " apply parent");
        require_target_still_current_or_throw();
        require_catalog_path_still_prior_or_throw();
        publication_base = observe_path_or_throw();
        if (publication_base.has_value()) {
            if (observation_matches_operation(*publication_base, target)) {
                return finish_exact_target_or_throw(
                    std::move(*publication_base),
                    SyncReplicaFolderApplyDisposition::AdoptedExactTarget,
                    true);
            }
            throw std::runtime_error(
                state_->label +
                " remote apply target appeared during parent creation");
        }
    }

    try {
        if (prior.has_value() &&
            prior->kind == SyncReplicaValueKind::File &&
            !rehydrating_cataloged_exact_target) {
            copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw(
                state_->root_authority, fs::path(target.canonical_path),
                payload.borrowed_descriptor(), payload.metadata(),
                payload.content_sha256(), publication_base->metadata,
                state_->label + " apply replacement");
        } else {
            copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
                state_->root_authority, fs::path(target.canonical_path),
                payload.borrowed_descriptor(), payload.metadata(),
                payload.content_sha256(),
                state_->label + " apply creation");
        }
    } catch (const SyncAtomicFilePublicationError& publication_error) {
        std::optional<StableRegularFileObservation> recovered =
            observe_path_or_throw();
        if (!recovered.has_value() ||
            !observation_matches_operation(*recovered, target)) {
            throw;
        }
        // Namespace publication may have completed before a later durability
        // failure or simulated crash cutpoint. Exact-file and parent-directory
        // synchronization repairs that seam before catalog authority advances.
        (void)publication_error;
        return finish_exact_target_or_throw(
            std::move(*recovered),
            SyncReplicaFolderApplyDisposition::AdoptedExactTarget,
            true);
    }

    std::optional<StableRegularFileObservation> applied =
        observe_path_or_throw();
    if (!applied.has_value() ||
        !observation_matches_operation(*applied, target)) {
        throw std::runtime_error(
            state_->label +
            " atomic publication did not leave the exact target file");
    }
    return finish_exact_target_or_throw(
        std::move(*applied), SyncReplicaFolderApplyDisposition::Applied,
        false);
}

SyncReplicaHistoricalVersionInventory
SyncReplicaFolderScanOwner::inspect_historical_versions_or_throw(
    std::uint64_t maximum_entries) {
    SyncReplicaHistoricalVersionQuery query;
    query.maximum_entries = maximum_entries;
    return inspect_historical_versions_or_throw(std::move(query));
}

SyncReplicaHistoricalVersionInventory
SyncReplicaFolderScanOwner::inspect_historical_versions_or_throw(
    SyncReplicaHistoricalVersionQuery query) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_sync_replica_historical_version_query_or_throw(
        query, state_->label + " historical-version inspection");

    // Observe and validate the complete causal selector before touching the
    // payload namespace. A stale bound continuation or stale cursor therefore
    // cannot pay for an O(payload namespace) scan. The payload observation is
    // later bracketed by a second replica snapshot so one returned page never
    // combines a causal model with bytes observed across an intervening change
    // to the exact active operation set. Unrelated liveness writes are not part
    // of this browse authority and therefore do not manufacture false drift.
    const SyncReplicaSqliteSnapshot replica_snapshot =
        state_->replica_owner->snapshot_or_throw();
    if (query.expected_source_cutpoint.has_value() &&
        query.expected_source_cutpoint->operation_set_digest !=
            replica_snapshot.operation_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetBeforePayloadObservation,
            state_->label +
                " historical-version operation set changed before payload "
                "observation; restart pagination");
    }
    if (query.expected_source_cutpoint.has_value() &&
        query.expected_source_cutpoint->evidence_set_digest.has_value() &&
        *query.expected_source_cutpoint->evidence_set_digest !=
            replica_snapshot.evidence_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetBeforePayloadObservation,
            state_->label +
                " historical-version retained evidence set changed before "
                "payload observation; restart pagination");
    }
    if (query.expected_source_cutpoint.has_value() &&
        ((query.expected_source_cutpoint->
                  historical_version_pin_set_digest.has_value() &&
          *query.expected_source_cutpoint->
                  historical_version_pin_set_digest !=
              replica_snapshot.historical_version_pin_set_digest) ||
         (!query.expected_source_cutpoint->
                   historical_version_pin_set_digest.has_value() &&
          replica_snapshot.historical_version_pin_count != 0U))) {
        // A pre-rev0973 source token could not bind pin policy. Preserve its
        // useful compatibility only while the pin set remains empty; treating
        // the missing field as a wildcard would let a later page silently mix
        // different retention roots while still returning `pinned` entries.
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetBeforePayloadObservation,
            state_->label +
                " historical-version retention pin set changed before "
                "payload observation; restart pagination");
    }
    const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
        replica_snapshot.durable, replica_snapshot.limits.model);

    const auto entry_precedes = [](
        const SyncReplicaHistoricalVersionEntry& left,
        const SyncReplicaHistoricalVersionEntry& right) {
        if (left.canonical_path != right.canonical_path) {
            return left.canonical_path < right.canonical_path;
        }
        if (left.actor.device_id != right.actor.device_id) {
            return left.actor.device_id < right.actor.device_id;
        }
        if (left.actor.epoch != right.actor.epoch) {
            return left.actor.epoch < right.actor.epoch;
        }
        if (left.counter != right.counter) {
            return left.counter > right.counter;
        }
        return left.operation_id < right.operation_id;
    };

    // A cursor is advisory browse state, not authority. It must still name an
    // exact active superseded file operation in the selected current scope;
    // otherwise a changed replica cannot silently turn stale pagination into
    // omission. The source generation/digests in every result let callers
    // recognize that separately requested pages came from different cutpoints.
    std::optional<SyncReplicaHistoricalVersionEntry> cursor_entry;
    if (query.start_after_operation_id.has_value()) {
        const std::optional<SyncReplicaOperation> cursor_operation =
            model.operation_by_id(*query.start_after_operation_id);
        if (!cursor_operation.has_value() ||
            cursor_operation->kind != SyncReplicaValueKind::File) {
            throw std::runtime_error(
                state_->label +
                " historical-version cursor is not one active file operation");
        }
        if (query.canonical_path.has_value() &&
            cursor_operation->canonical_path != *query.canonical_path) {
            throw std::runtime_error(
                state_->label +
                " historical-version cursor is outside the selected path");
        }
        const std::optional<SyncReplicaPathView> cursor_view =
            model.visible_path(cursor_operation->canonical_path);
        if (!cursor_view.has_value() ||
            cursor_view->visible_operation_ids.empty() ||
            std::binary_search(
                cursor_view->visible_operation_ids.begin(),
                cursor_view->visible_operation_ids.end(),
                cursor_operation->operation_id)) {
            throw std::runtime_error(
                state_->label +
                " historical-version cursor is no longer superseded");
        }
        cursor_entry.emplace();
        cursor_entry->operation_id = cursor_operation->operation_id;
        cursor_entry->canonical_path = cursor_operation->canonical_path;
        cursor_entry->actor = cursor_operation->dot.actor;
        cursor_entry->counter = cursor_operation->dot.counter;
    }

    // Exact availability inspection deliberately pays for one complete payload
    // observation and brackets it with the operation-set owner. Metadata-only
    // inspection stops at the immutable causal snapshot above: it must not open
    // the payload store, acquire its lease, enumerate its namespace, or invent
    // negative availability evidence.
    std::optional<SyncReplicaFilePayloadStoreSnapshot> payload_snapshot;
    if (query.inspection_mode ==
        SyncReplicaHistoricalVersionInspectionMode::
            ExactPayloadAvailability) {
        payload_snapshot.emplace(
            state_->payload_store->snapshot_or_throw());
        payload_snapshot->require_folder_or_throw(
            state_->folder_id,
            state_->label + " historical-version payload snapshot");
        const SyncReplicaSqliteSnapshot replica_after_payload =
            state_->replica_owner->snapshot_or_throw();
        if (replica_snapshot.operation_set_digest !=
            replica_after_payload.operation_set_digest) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    OperationSetDuringPayloadObservation,
                state_->label +
                    " historical-version operation set changed during payload "
                    "observation; restart pagination");
        }
        if (replica_snapshot.evidence_set_digest !=
            replica_after_payload.evidence_set_digest) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    EvidenceSetDuringPayloadObservation,
                state_->label +
                    " historical-version retained evidence set changed during "
                    "payload observation; restart pagination");
        }
        if (replica_snapshot.historical_version_pin_set_digest !=
            replica_after_payload.historical_version_pin_set_digest) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    HistoricalVersionPinSetDuringPayloadObservation,
                state_->label +
                    " historical-version retention pin set changed during "
                    "payload observation; restart pagination");
        }
        if (query.expected_source_cutpoint.has_value() &&
            query.expected_source_cutpoint->payload_snapshot_digest !=
                std::optional<std::string>(
                    payload_snapshot->snapshot_digest())) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    PayloadSnapshot,
                state_->label +
                    " historical-version payload snapshot changed; restart "
                    "pagination");
        }
    }

    SyncReplicaHistoricalVersionInventory inventory;
    inventory.query = query;
    inventory.source_replica_state_generation =
        replica_snapshot.state_generation;
    inventory.source_operation_set_digest =
        replica_snapshot.operation_set_digest;
    inventory.source_historical_version_pin_set_digest =
        replica_snapshot.historical_version_pin_set_digest;
    inventory.historical_version_pin_count =
        replica_snapshot.historical_version_pin_count;
    inventory.source_visible_state_digest =
        replica_snapshot.visible_state_digest;
    if (payload_snapshot.has_value()) {
        inventory.source_evidence_set_digest =
            replica_snapshot.evidence_set_digest;
        inventory.source_payload_snapshot_digest =
            payload_snapshot->snapshot_digest();
        inventory.payload_scan_hashed_entry_count =
            payload_snapshot->scan_hashed_entry_count();
        inventory.payload_scan_hashed_bytes =
            payload_snapshot->scan_hashed_bytes();
        inventory.payload_scan_reused_entry_count =
            payload_snapshot->scan_reused_entry_count();
        inventory.payload_scan_reused_bytes =
            payload_snapshot->scan_reused_bytes();
        inventory.payload_present_count = 0U;
        inventory.restore_ready_count = 0U;
    }
    inventory.entries.reserve(
        static_cast<std::size_t>(query.maximum_entries));

    const auto increment_or_throw = [&](std::uint64_t& value,
                                        std::string_view field) {
        if (value == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                state_->label + " historical-version " +
                std::string(field) + " count overflows");
        }
        ++value;
    };

    std::map<HistoricalPayloadReferenceKey, std::uint8_t,
             HistoricalPayloadReferenceKeyLess>
        payload_references;
    const auto operation_is_pinned = [&](std::string_view operation_id) {
        return std::binary_search(
            replica_snapshot.historical_version_pins.begin(),
            replica_snapshot.historical_version_pins.end(), operation_id);
    };
    std::uint64_t observed_pinned_file_operations = 0U;

    const auto add_or_throw = [&](std::uint64_t& destination,
                                  std::uint64_t amount,
                                  std::string_view field) {
        if (amount >
            std::numeric_limits<std::uint64_t>::max() - destination) {
            throw std::overflow_error(
                state_->label + " historical-version " +
                std::string(field) + " overflows");
        }
        destination += amount;
    };

    if (payload_snapshot.has_value()) {
        inventory.retained_payload_reachability.emplace();
        inventory.retained_payload_reachability->payload_entry_count =
            payload_snapshot->entry_count();
        inventory.retained_payload_reachability->payload_indexed_bytes =
            payload_snapshot->indexed_bytes();
    }

    const auto mark_payload_reference = [&]
        (const SyncReplicaOperation& operation,
         std::uint8_t class_mask,
         SyncReplicaHistoricalVersionPayloadReachabilityClass& classification,
         bool contributes_to_retained_union) {
        if (!inventory.retained_payload_reachability.has_value()) return;
        increment_or_throw(classification.file_operation_count,
                           "reachability file-operation");
        if (contributes_to_retained_union) {
            increment_or_throw(
                inventory.retained_payload_reachability->retained_union.
                    file_operation_count,
                "retained-union file-operation");
        }
        const HistoricalPayloadReferenceKey key{
            .content_sha256 = operation.content_sha256,
            .size_bytes = operation.size_bytes,
        };
        const auto [position, inserted] =
            payload_references.try_emplace(key, 0U);
        if ((position->second & class_mask) == 0U) {
            increment_or_throw(classification.distinct_content_count,
                               "reachability distinct-content");
        }
        if (contributes_to_retained_union && inserted) {
            increment_or_throw(
                inventory.retained_payload_reachability->retained_union.
                    distinct_content_count,
                "retained-union distinct-content");
        }
        position->second = static_cast<std::uint8_t>(
            position->second | class_mask);
    };

    const auto mark_explicit_pin = [&](const SyncReplicaOperation& operation) {
        if (!inventory.retained_payload_reachability.has_value() ||
            !operation_is_pinned(operation.operation_id)) {
            return;
        }
        increment_or_throw(
            observed_pinned_file_operations,
            "observed pinned file-operation");
        mark_payload_reference(
            operation, kHistoricalPayloadExplicitPinMask,
            inventory.retained_payload_reachability->explicit_pins, false);
    };

    const auto consider_operation = [&]
        (const SyncReplicaOperation& operation,
         const SyncReplicaPathView& view,
         bool operation_is_visible) {
        if (operation.kind != SyncReplicaValueKind::File) return;
        if (query.canonical_path.has_value() &&
            operation.canonical_path != *query.canonical_path) {
            return;
        }
        // visible_operation_ids is canonical operation-ID order. A binary
        // membership test prevents a path with many concurrent visible heads
        // from reintroducing the all-pairs cost removed by the grouped causal
        // projection.
        if (operation_is_visible) return;
        increment_or_throw(
            inventory.historical_file_operation_count,
            "operation");

        const SyncReplicaOperation* current =
            model.active_operation_by_id_or_none(
                view.primary_operation_id);
        if (current == nullptr) {
            throw std::logic_error(
                state_->label +
                " historical-version primary operation is inactive");
        }

        std::optional<bool> payload_present;
        std::optional<bool> restore_ready;
        if (payload_snapshot.has_value()) {
            payload_present =
                payload_snapshot->payload_size_or_none(
                    operation.content_sha256) ==
                std::optional<std::uint64_t>(operation.size_bytes);
            if (*payload_present) {
                increment_or_throw(
                    *inventory.payload_present_count,
                    "payload-present");
            }
            const bool changes_current_value =
                current->kind == SyncReplicaValueKind::Tombstone ||
                current->size_bytes != operation.size_bytes ||
                current->content_sha256 != operation.content_sha256;
            restore_ready =
                *payload_present &&
                view.visible_operation_ids.size() == 1U &&
                changes_current_value;
            if (*restore_ready) {
                increment_or_throw(
                    *inventory.restore_ready_count,
                    "restore-ready");
            }
        }

        SyncReplicaHistoricalVersionEntry candidate{
            .operation_id = operation.operation_id,
            .canonical_path = operation.canonical_path,
            .size_bytes = operation.size_bytes,
            .content_sha256 = operation.content_sha256,
            .actor = operation.dot.actor,
            .counter = operation.dot.counter,
            .visible_head_count = static_cast<std::uint64_t>(
                view.visible_operation_ids.size()),
            .current_primary_operation_id =
                view.primary_operation_id,
            .current_primary_kind = view.primary_kind,
            .payload_present = payload_present,
            .restore_ready = restore_ready,
            .pinned = operation_is_pinned(operation.operation_id),
        };
        if (cursor_entry.has_value() &&
            !entry_precedes(*cursor_entry, candidate)) {
            return;
        }
        increment_or_throw(
            inventory.historical_file_operation_count_after_cursor,
            "operation-after-cursor");

        if (inventory.entries.size() <
            static_cast<std::size_t>(query.maximum_entries)) {
            inventory.entries.push_back(std::move(candidate));
            std::push_heap(
                inventory.entries.begin(), inventory.entries.end(),
                entry_precedes);
            return;
        }
        if (!entry_precedes(candidate, inventory.entries.front())) {
            return;
        }
        std::pop_heap(
            inventory.entries.begin(), inventory.entries.end(),
            entry_precedes);
        inventory.entries.back() = std::move(candidate);
        std::push_heap(
            inventory.entries.begin(), inventory.entries.end(),
            entry_precedes);
    };

    const auto visit_active_path = [&]
        (const SyncReplicaPathView& view,
         std::span<const SyncReplicaOperation* const> operations) {
        for (const SyncReplicaOperation* operation : operations) {
            if (operation == nullptr) {
                throw std::logic_error(
                    state_->label +
                    " historical-version path group contains a null operation");
            }
            const bool operation_is_visible = std::binary_search(
                view.visible_operation_ids.begin(),
                view.visible_operation_ids.end(),
                operation->operation_id);
            if (operation->kind == SyncReplicaValueKind::File &&
                inventory.retained_payload_reachability.has_value()) {
                if (operation_is_visible) {
                    mark_payload_reference(
                        *operation, kHistoricalPayloadCurrentVisibleMask,
                        inventory.retained_payload_reachability->
                            current_visible,
                        true);
                } else {
                    mark_payload_reference(
                        *operation, kHistoricalPayloadSupersededActiveMask,
                        inventory.retained_payload_reachability->
                            superseded_active,
                        true);
                }
                mark_explicit_pin(*operation);
            }
            consider_operation(*operation, view, operation_is_visible);
        }
    };

    if (inventory.retained_payload_reachability.has_value() ||
        !query.canonical_path.has_value()) {
        // Exact inspection is share-global because its reachability result must
        // not hide references outside a path-filtered page. This grouped
        // borrowed traversal simultaneously feeds the bounded page and active
        // reachability classes, avoiding a second active-model pass.
        model.for_each_active_path(visit_active_path);
    } else {
        const std::optional<SyncReplicaPathView> selected_view =
            model.visible_path(*query.canonical_path);
        if (selected_view.has_value()) {
            model.for_each_active_operation(
                [&](const SyncReplicaOperation& operation) {
                    if (operation.canonical_path != *query.canonical_path) {
                        return;
                    }
                    const bool operation_is_visible = std::binary_search(
                        selected_view->visible_operation_ids.begin(),
                        selected_view->visible_operation_ids.end(),
                        operation.operation_id);
                    consider_operation(
                        operation, *selected_view, operation_is_visible);
                });
        }
    }

    if (inventory.retained_payload_reachability.has_value()) {
        // Inactive pending/quarantined evidence is still retained evidence. It
        // participates in the diagnostic mark even though it cannot appear in
        // the active history page. The compile-time borrowed visitor keeps this
        // pass linear and avoids one lookup/copy per retained operation.
        model.for_each_evidence_operation(
            [&](const SyncReplicaOperation& operation,
                SyncReplicaEvidenceState evidence_state) {
                if (evidence_state == SyncReplicaEvidenceState::Active ||
                    operation.kind != SyncReplicaValueKind::File) {
                    return;
                }
                mark_payload_reference(
                    operation, kHistoricalPayloadInactiveEvidenceMask,
                    inventory.retained_payload_reachability->
                        inactive_evidence,
                    true);
                mark_explicit_pin(operation);
            });

        auto& reachability = *inventory.retained_payload_reachability;
        const auto account_present = [&]
            (SyncReplicaHistoricalVersionPayloadReachabilityClass& value,
             std::uint64_t size_bytes,
             std::string_view field) {
            increment_or_throw(value.present_content_count, field);
            add_or_throw(value.present_content_bytes, size_bytes, field);
        };
        const SyncReplicaFileContentInventory content_inventory =
            payload_snapshot->content_inventory();
        const std::span<const std::string> payload_digests =
            content_inventory.content_sha256s();
        if (payload_digests.size() !=
            static_cast<std::size_t>(reachability.payload_entry_count)) {
            throw std::logic_error(
                state_->label +
                " historical-version payload inventory cardinality drifted");
        }
        for (const std::string& digest : payload_digests) {
            const std::optional<std::uint64_t> payload_size =
                payload_snapshot->payload_size_or_none(digest);
            if (!payload_size.has_value()) {
                throw std::logic_error(
                    state_->label +
                    " historical-version payload inventory lost one digest");
            }
            const auto found = payload_references.find(HistoricalPayloadReferenceKey{
                .content_sha256 = digest,
                .size_bytes = *payload_size,
            });
            if (found == payload_references.end()) {
                increment_or_throw(
                    reachability.unreferenced_payload_count,
                    "unreferenced payload");
                add_or_throw(
                    reachability.unreferenced_payload_bytes, *payload_size,
                    "unreferenced payload bytes");
                continue;
            }
            const std::uint8_t mask = found->second;
            if ((mask & kHistoricalPayloadCurrentVisibleMask) != 0U) {
                account_present(
                    reachability.current_visible, *payload_size,
                    "current-visible present content");
            }
            if ((mask & kHistoricalPayloadSupersededActiveMask) != 0U) {
                account_present(
                    reachability.superseded_active, *payload_size,
                    "superseded-active present content");
            }
            if ((mask & kHistoricalPayloadInactiveEvidenceMask) != 0U) {
                account_present(
                    reachability.inactive_evidence, *payload_size,
                    "inactive-evidence present content");
            }
            if ((mask & kHistoricalPayloadExplicitPinMask) != 0U) {
                account_present(
                    reachability.explicit_pins, *payload_size,
                    "explicit-pin present content");
            }
            account_present(
                reachability.retained_union, *payload_size,
                "retained-union present content");
            payload_references.erase(found);
        }

        for (const auto& [reference, mask] : payload_references) {
            (void)reference;
            if ((mask & kHistoricalPayloadCurrentVisibleMask) != 0U) {
                increment_or_throw(
                    reachability.current_visible.missing_content_count,
                    "current-visible missing content");
            }
            if ((mask & kHistoricalPayloadSupersededActiveMask) != 0U) {
                increment_or_throw(
                    reachability.superseded_active.missing_content_count,
                    "superseded-active missing content");
            }
            if ((mask & kHistoricalPayloadInactiveEvidenceMask) != 0U) {
                increment_or_throw(
                    reachability.inactive_evidence.missing_content_count,
                    "inactive-evidence missing content");
            }
            if ((mask & kHistoricalPayloadExplicitPinMask) != 0U) {
                increment_or_throw(
                    reachability.explicit_pins.missing_content_count,
                    "explicit-pin missing content");
            }
            increment_or_throw(
                reachability.retained_union.missing_content_count,
                "retained-union missing content");
        }

        const auto validate_class = [&]
            (const SyncReplicaHistoricalVersionPayloadReachabilityClass& value,
             std::string_view label) {
            if (value.present_content_count >
                    value.distinct_content_count ||
                value.missing_content_count !=
                    value.distinct_content_count -
                        value.present_content_count) {
                throw std::logic_error(
                    state_->label + " historical-version " +
                    std::string(label) +
                    " reachability partition is inconsistent");
            }
        };
        validate_class(reachability.current_visible, "current-visible");
        validate_class(reachability.superseded_active, "superseded-active");
        validate_class(reachability.inactive_evidence, "inactive-evidence");
        validate_class(reachability.explicit_pins, "explicit-pins");
        validate_class(reachability.retained_union, "retained-union");

        std::uint64_t physical_entry_partition =
            reachability.retained_union.present_content_count;
        add_or_throw(
            physical_entry_partition,
            reachability.unreferenced_payload_count,
            "physical payload entry partition");
        std::uint64_t physical_byte_partition =
            reachability.retained_union.present_content_bytes;
        add_or_throw(
            physical_byte_partition,
            reachability.unreferenced_payload_bytes,
            "physical payload byte partition");
        std::uint64_t operation_partition =
            reachability.current_visible.file_operation_count;
        add_or_throw(
            operation_partition,
            reachability.superseded_active.file_operation_count,
            "retained file-operation partition");
        add_or_throw(
            operation_partition,
            reachability.inactive_evidence.file_operation_count,
            "retained file-operation partition");
        if (physical_entry_partition != reachability.payload_entry_count ||
            physical_byte_partition != reachability.payload_indexed_bytes ||
            operation_partition !=
                reachability.retained_union.file_operation_count ||
            observed_pinned_file_operations !=
                replica_snapshot.historical_version_pin_count ||
            reachability.explicit_pins.file_operation_count !=
                replica_snapshot.historical_version_pin_count) {
            throw std::logic_error(
                state_->label +
                " historical-version retained payload reachability is inconsistent");
        }
    }

    std::sort_heap(
        inventory.entries.begin(), inventory.entries.end(),
        entry_precedes);
    inventory.entry_limit_frontier_reached =
        inventory.historical_file_operation_count_after_cursor >
        static_cast<std::uint64_t>(inventory.entries.size());
    inventory.truncated = inventory.entry_limit_frontier_reached;
    if (inventory.truncated) {
        if (inventory.entries.empty()) {
            throw std::logic_error(
                state_->label +
                " historical-version truncated page retained no cursor");
        }
        inventory.next_start_after_operation_id =
            inventory.entries.back().operation_id;
    }
    return inventory;
}

SyncReplicaRetentionPlan
SyncReplicaFolderScanOwner::plan_payload_retention_or_throw(
    SyncReplicaRetentionPlanQuery query) {
    return plan_payload_retention_impl_or_throw(
        std::move(query), nullptr, nullptr);
}

SyncReplicaFilePayloadRetentionMarkPublication
SyncReplicaFolderScanOwner::mark_payload_retention_or_throw(
    SyncReplicaPayloadRetentionMarkRequest request) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_sync_replica_historical_version_source_cutpoint_or_throw(
        request.expected_source_cutpoint,
        state_->label + " payload retention mark source cutpoint");
    if (request.expected_source_cutpoint.inspection_mode !=
            SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability ||
        !request.expected_source_cutpoint.evidence_set_digest.has_value() ||
        !request.expected_source_cutpoint
            .historical_version_pin_set_digest.has_value() ||
        !request.expected_source_cutpoint.payload_snapshot_digest.has_value()) {
        throw std::invalid_argument(
            state_->label +
            " payload retention mark requires one current exact v4 cutpoint");
    }
    if (!is_lowercase_sha256_hex(
            request.expected_source_replica_database_incarnation_sha256) ||
        request.expected_source_replica_database_recovery_epoch == 0U ||
        request.expected_source_replica_state_generation == 0U) {
        throw std::invalid_argument(
            state_->label +
            " payload retention mark source database lineage is invalid");
    }
    if (!is_lowercase_sha256_hex(
            request.expected_durable_candidate_witness_digest)) {
        throw std::invalid_argument(
            state_->label +
            " payload retention mark candidate witness is invalid");
    }
    const SyncReplicaFilePayloadStoreLimits& payload_store_limits =
        state_->payload_store->limits();
    validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
        request.policy, request.marked_at_unix_seconds,
        payload_store_limits.max_entries,
        payload_store_limits.max_indexed_bytes,
        state_->label + " payload retention mark policy");

    SyncReplicaRetentionPlanQuery query;
    query.maximum_entries = 1U;
    query.expected_source_cutpoint = request.expected_source_cutpoint;
    SyncReplicaFilePayloadRetentionMarkPublication publication;
    const SyncReplicaRetentionPlan plan =
        plan_payload_retention_impl_or_throw(
            std::move(query), &request, &publication);
    if (publication.mark.source_replica_state_generation !=
            plan.source_replica_state_generation ||
        publication.mark.durable_candidate_witness_digest !=
            plan.durable_candidate_witness_digest) {
        throw std::logic_error(
            state_->label +
            " payload retention mark publication escaped its exact plan");
    }
    return publication;
}

SyncReplicaRetentionPlan
SyncReplicaFolderScanOwner::plan_payload_retention_impl_or_throw(
    SyncReplicaRetentionPlanQuery query,
    const SyncReplicaPayloadRetentionMarkRequest* mark_request,
    SyncReplicaFilePayloadRetentionMarkPublication* mark_publication) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_sync_replica_retention_plan_query_or_throw(
        query, state_->label + " retention-plan inspection");
    if ((mark_request == nullptr) != (mark_publication == nullptr)) {
        throw std::logic_error(
            state_->label +
            " retention-plan mark request/publication pairing is invalid");
    }
    if (mark_request != nullptr &&
        (query.maximum_entries != 1U ||
         query.start_after_content_sha256.has_value() ||
         !query.expected_source_cutpoint.has_value() ||
         *query.expected_source_cutpoint !=
             mark_request->expected_source_cutpoint)) {
        throw std::logic_error(
            state_->label +
            " payload retention mark escaped its exact planner query");
    }

    // The planner consumes exactly the same four owners as exact historical
    // reachability. A stale bound page is rejected before the payload scan
    // whenever possible; the complete payload observation is then bracketed by
    // a second replica snapshot so no page combines roots from one cutpoint
    // with physical objects from another.
    const SyncReplicaSqliteSnapshot replica_snapshot =
        state_->replica_owner->snapshot_or_throw();
    if (mark_request != nullptr &&
        (mark_request->expected_source_replica_database_incarnation_sha256 !=
             replica_snapshot.database_incarnation_sha256 ||
         mark_request->expected_source_replica_database_recovery_epoch !=
             replica_snapshot.database_recovery_epoch ||
         mark_request->expected_source_replica_state_generation !=
             replica_snapshot.state_generation)) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                RetentionMarkPublication,
            state_->label +
                " payload retention mark source database lineage changed "
                "before payload observation; recompute the mark");
    }
    if (query.expected_source_cutpoint.has_value() &&
        query.expected_source_cutpoint->operation_set_digest !=
            replica_snapshot.operation_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetBeforePayloadObservation,
            state_->label +
                " retention-plan operation set changed before payload "
                "observation; restart pagination");
    }
    if (query.expected_source_cutpoint.has_value() &&
        *query.expected_source_cutpoint->evidence_set_digest !=
            replica_snapshot.evidence_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetBeforePayloadObservation,
            state_->label +
                " retention-plan retained evidence set changed before payload "
                "observation; restart pagination");
    }
    if (query.expected_source_cutpoint.has_value() &&
        *query.expected_source_cutpoint->historical_version_pin_set_digest !=
            replica_snapshot.historical_version_pin_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetBeforePayloadObservation,
            state_->label +
                " retention-plan pin set changed before payload observation; "
                "restart pagination");
    }

    const SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
        replica_snapshot.durable, replica_snapshot.limits.model);
    SyncReplicaRetentionPlan plan;
    plan.query = query;
    plan.source_replica_database_incarnation_sha256 =
        replica_snapshot.database_incarnation_sha256;
    plan.source_replica_database_recovery_epoch =
        replica_snapshot.database_recovery_epoch;
    plan.source_replica_state_generation = replica_snapshot.state_generation;
    plan.source_operation_set_digest = replica_snapshot.operation_set_digest;
    plan.source_evidence_set_digest = replica_snapshot.evidence_set_digest;
    plan.source_historical_version_pin_set_digest =
        replica_snapshot.historical_version_pin_set_digest;
    plan.historical_version_pin_count =
        replica_snapshot.historical_version_pin_count;
    plan.source_visible_state_digest = replica_snapshot.visible_state_digest;
    plan.entries.reserve(static_cast<std::size_t>(query.maximum_entries));

    const auto increment_or_throw = [&](std::uint64_t& value,
                                        std::string_view field) {
        if (value == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                state_->label + " retention-plan " + std::string(field) +
                " count overflows");
        }
        ++value;
    };
    const auto add_or_throw = [&](std::uint64_t& destination,
                                  std::uint64_t amount,
                                  std::string_view field) {
        if (amount >
            std::numeric_limits<std::uint64_t>::max() - destination) {
            throw std::overflow_error(
                state_->label + " retention-plan " + std::string(field) +
                " overflows");
        }
        destination += amount;
    };

    std::vector<HistoricalPayloadReferenceProjectionEntry> payload_references;
    if (replica_snapshot.historical_version_pins.size() >
        std::numeric_limits<std::size_t>::max() -
            replica_snapshot.durable.operations.size()) {
        throw std::overflow_error(
            state_->label +
            " retention-plan reference projection capacity overflows");
    }
    payload_references.reserve(
        replica_snapshot.durable.operations.size() +
        replica_snapshot.historical_version_pins.size());
    const auto operation_is_pinned = [&](std::string_view operation_id) {
        return std::binary_search(
            replica_snapshot.historical_version_pins.begin(),
            replica_snapshot.historical_version_pins.end(), operation_id);
    };
    std::uint64_t observed_pinned_file_operations = 0U;
    auto& reachability = plan.retained_payload_reachability;

    const auto mark_payload_reference = [&]
        (const SyncReplicaOperation& operation,
         std::uint8_t class_mask,
         SyncReplicaHistoricalVersionPayloadReachabilityClass& classification,
         bool contributes_to_retained_union) {
        increment_or_throw(
            classification.file_operation_count,
            "reachability file-operation");
        if (contributes_to_retained_union) {
            increment_or_throw(
                reachability.retained_union.file_operation_count,
                "retained-union file-operation");
        }
        payload_references.push_back(
            HistoricalPayloadReferenceProjectionEntry{
                .key = HistoricalPayloadReferenceKey{
                    .content_sha256 = operation.content_sha256,
                    .size_bytes = operation.size_bytes,
                },
                .root_mask = class_mask,
            });
    };

    const auto mark_explicit_pin = [&](const SyncReplicaOperation& operation) {
        if (!operation_is_pinned(operation.operation_id)) return;
        increment_or_throw(
            observed_pinned_file_operations,
            "observed pinned file-operation");
        mark_payload_reference(
            operation, kHistoricalPayloadExplicitPinMask,
            reachability.explicit_pins, false);
    };

    model.for_each_active_path(
        [&](const SyncReplicaPathView& view,
            std::span<const SyncReplicaOperation* const> operations) {
            for (const SyncReplicaOperation* operation : operations) {
                if (operation == nullptr) {
                    throw std::logic_error(
                        state_->label +
                        " retention-plan path group contains a null operation");
                }
                if (operation->kind != SyncReplicaValueKind::File) continue;
                const bool visible = std::binary_search(
                    view.visible_operation_ids.begin(),
                    view.visible_operation_ids.end(),
                    operation->operation_id);
                if (visible) {
                    mark_payload_reference(
                        *operation, kHistoricalPayloadCurrentVisibleMask,
                        reachability.current_visible, true);
                } else {
                    mark_payload_reference(
                        *operation, kHistoricalPayloadSupersededActiveMask,
                        reachability.superseded_active, true);
                }
                mark_explicit_pin(*operation);
            }
        });
    model.for_each_evidence_operation(
        [&](const SyncReplicaOperation& operation,
            SyncReplicaEvidenceState evidence_state) {
            if (evidence_state == SyncReplicaEvidenceState::Active ||
                operation.kind != SyncReplicaValueKind::File) {
                return;
            }
            mark_payload_reference(
                operation, kHistoricalPayloadInactiveEvidenceMask,
                reachability.inactive_evidence, true);
            mark_explicit_pin(operation);
        });

    const HistoricalPayloadReferenceKeyLess reference_key_less;
    std::sort(
        payload_references.begin(), payload_references.end(),
        [&](const HistoricalPayloadReferenceProjectionEntry& left,
            const HistoricalPayloadReferenceProjectionEntry& right) {
            return reference_key_less(left.key, right.key);
        });
    std::size_t compacted_reference_count = 0U;
    for (std::size_t read_index = 0U;
         read_index < payload_references.size(); ++read_index) {
        if (compacted_reference_count != 0U &&
            historical_payload_reference_key_equal(
                payload_references[compacted_reference_count - 1U].key,
                payload_references[read_index].key)) {
            payload_references[compacted_reference_count - 1U].root_mask =
                static_cast<std::uint8_t>(
                    payload_references[compacted_reference_count - 1U]
                        .root_mask |
                    payload_references[read_index].root_mask);
            continue;
        }
        if (compacted_reference_count != read_index) {
            payload_references[compacted_reference_count] =
                payload_references[read_index];
        }
        ++compacted_reference_count;
    }
    payload_references.resize(compacted_reference_count);

    constexpr std::uint8_t kRetainedUnionRootMask =
        kHistoricalPayloadCurrentVisibleMask |
        kHistoricalPayloadSupersededActiveMask |
        kHistoricalPayloadInactiveEvidenceMask;
    for (const HistoricalPayloadReferenceProjectionEntry& reference :
         payload_references) {
        if (historical_payload_mask_has(
                reference.root_mask,
                kHistoricalPayloadCurrentVisibleMask)) {
            increment_or_throw(
                reachability.current_visible.distinct_content_count,
                "current-visible distinct content");
        }
        if (historical_payload_mask_has(
                reference.root_mask,
                kHistoricalPayloadSupersededActiveMask)) {
            increment_or_throw(
                reachability.superseded_active.distinct_content_count,
                "superseded-active distinct content");
        }
        if (historical_payload_mask_has(
                reference.root_mask,
                kHistoricalPayloadInactiveEvidenceMask)) {
            increment_or_throw(
                reachability.inactive_evidence.distinct_content_count,
                "inactive-evidence distinct content");
        }
        if (historical_payload_mask_has(
                reference.root_mask,
                kHistoricalPayloadExplicitPinMask)) {
            increment_or_throw(
                reachability.explicit_pins.distinct_content_count,
                "explicit-pin distinct content");
        }
        if ((reference.root_mask & kRetainedUnionRootMask) == 0U) {
            throw std::logic_error(
                state_->label +
                " retention-plan explicit pin lacks one retained File "
                "operation root");
        }
        increment_or_throw(
            reachability.retained_union.distinct_content_count,
            "retained-union distinct content");
    }

    // The causal projection above is bound to replica_snapshot but does not
    // require payload namespace exclusion. Perform its allocations and sort
    // before taking the global writer fence so ordinary synchronization is
    // stalled only for the complete physical merge and bounded inode probes.
    SyncReplicaFilePayloadStoreSnapshot payload_snapshot =
        state_->payload_store->
            snapshot_writer_fenced_for_retention_or_throw();
    payload_snapshot.require_folder_or_throw(
        state_->folder_id, state_->label + " retention-plan payload snapshot");
    const SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
        live_capabilities_before =
            state_->payload_store->
                live_capability_cutpoint_excluding_snapshot_or_throw(
                    payload_snapshot,
                    state_->label +
                        " retention-plan live-capability opening cutpoint");
    const SyncReplicaSqliteSnapshot replica_after_payload =
        state_->replica_owner->snapshot_or_throw();
    if (replica_snapshot.operation_set_digest !=
        replica_after_payload.operation_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetDuringPayloadObservation,
            state_->label +
                " retention-plan operation set changed during payload "
                "observation; restart pagination");
    }
    if (replica_snapshot.evidence_set_digest !=
        replica_after_payload.evidence_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetDuringPayloadObservation,
            state_->label +
                " retention-plan retained evidence set changed during payload "
                "observation; restart pagination");
    }
    if (replica_snapshot.historical_version_pin_set_digest !=
        replica_after_payload.historical_version_pin_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetDuringPayloadObservation,
            state_->label +
                " retention-plan pin set changed during payload observation; "
                "restart pagination");
    }
    if (query.expected_source_cutpoint.has_value() &&
        *query.expected_source_cutpoint->payload_snapshot_digest !=
            payload_snapshot.snapshot_digest()) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::PayloadSnapshot,
            state_->label +
                " retention-plan payload snapshot changed; restart pagination");
    }

    plan.source_payload_snapshot_digest = payload_snapshot.snapshot_digest();
    plan.source_payload_transient_namespace_digest =
        payload_snapshot.transient_namespace_digest();
    plan.payload_transient_entry_count =
        payload_snapshot.transient_entry_count();
    plan.payload_transient_bytes = payload_snapshot.transient_bytes();
    plan.payload_transient_reserved_bytes =
        payload_snapshot.transient_reserved_bytes();
    plan.payload_scan_hashed_entry_count =
        payload_snapshot.scan_hashed_entry_count();
    plan.payload_scan_hashed_bytes = payload_snapshot.scan_hashed_bytes();
    plan.payload_scan_reused_entry_count =
        payload_snapshot.scan_reused_entry_count();
    plan.payload_scan_reused_bytes = payload_snapshot.scan_reused_bytes();
    plan.writer_fenced_observation = true;
    plan.cooperating_new_namespace_activity_excluded_during_observation = true;
    plan.live_capability_process_store_scope_digest =
        live_capabilities_before.process_store_scope_digest;
    plan.live_capability_process_store_scope_incarnation_digest =
        live_capabilities_before.process_store_scope_incarnation_digest;
    plan.live_capability_set_digest =
        live_capabilities_before.capability_set_digest;
    plan.live_snapshot_count = live_capabilities_before.snapshot_count;
    plan.live_opened_payload_count =
        live_capabilities_before.opened_payload_count;
    plan.live_targeted_access_count =
        live_capabilities_before.targeted_access_count;
    plan.live_mutation_batch_count =
        live_capabilities_before.mutation_batch_count;
    plan.distinct_live_opened_payload_root_count =
        live_capabilities_before.distinct_opened_payload_root_count;
    plan.distinct_live_opened_payload_root_bytes =
        live_capabilities_before.distinct_opened_payload_root_bytes;
    plan.live_capabilities_may_reopen_all_current_payloads =
        live_capabilities_before.all_current_payloads_may_be_reopened();
    plan.retained_payload_reachability.payload_entry_count =
        payload_snapshot.entry_count();
    plan.retained_payload_reachability.payload_indexed_bytes =
        payload_snapshot.indexed_bytes();

    const auto account_present = [&]
        (SyncReplicaHistoricalVersionPayloadReachabilityClass& value,
         std::uint64_t size_bytes,
         std::string_view field) {
        increment_or_throw(value.present_content_count, field);
        add_or_throw(value.present_content_bytes, size_bytes, field);
    };
    const auto account_plan_class = [&]
        (SyncReplicaRetentionPlanClass& value,
         std::uint64_t size_bytes,
         std::string_view field) {
        increment_or_throw(value.payload_count, field);
        add_or_throw(value.payload_bytes, size_bytes, field);
    };
    const auto account_missing_reference = [&](std::uint8_t root_mask) {
        if (historical_payload_mask_has(
                root_mask, kHistoricalPayloadCurrentVisibleMask)) {
            increment_or_throw(
                reachability.current_visible.missing_content_count,
                "current-visible missing content");
        }
        if (historical_payload_mask_has(
                root_mask, kHistoricalPayloadSupersededActiveMask)) {
            increment_or_throw(
                reachability.superseded_active.missing_content_count,
                "superseded-active missing content");
        }
        if (historical_payload_mask_has(
                root_mask, kHistoricalPayloadInactiveEvidenceMask)) {
            increment_or_throw(
                reachability.inactive_evidence.missing_content_count,
                "inactive-evidence missing content");
        }
        if (historical_payload_mask_has(
                root_mask, kHistoricalPayloadExplicitPinMask)) {
            increment_or_throw(
                reachability.explicit_pins.missing_content_count,
                "explicit-pin missing content");
        }
        increment_or_throw(
            reachability.retained_union.missing_content_count,
            "retained-union missing content");
    };

    const SyncReplicaFileContentInventory content_inventory =
        payload_snapshot.content_inventory();
    const std::span<const std::string> payload_digests =
        content_inventory.content_sha256s();
    if (payload_digests.size() !=
        static_cast<std::size_t>(reachability.payload_entry_count)) {
        throw std::logic_error(
            state_->label +
            " retention-plan payload inventory cardinality drifted");
    }

    std::size_t first_page_index = 0U;
    if (query.start_after_content_sha256.has_value()) {
        const auto cursor = std::lower_bound(
            payload_digests.begin(), payload_digests.end(),
            *query.start_after_content_sha256);
        if (cursor == payload_digests.end() ||
            *cursor != *query.start_after_content_sha256) {
            throw std::runtime_error(
                state_->label +
                " retention-plan cursor is not one current physical payload");
        }
        first_page_index = static_cast<std::size_t>(
            std::distance(payload_digests.begin(), cursor)) + 1U;
    }

    Sha256DigestBuilder candidate_set_digest;
    append_string(
        candidate_set_digest,
        kRetentionPlanUnreferencedCandidateSetDigestDomain);
    std::size_t reference_index = 0U;
    std::size_t live_opened_root_index = 0U;
    const auto live_opened_root_less_than_physical = [](
        const SyncReplicaFilePayloadStoreLiveOpenedPayloadRoot& live_root,
        const HistoricalPayloadReferenceKey& physical) noexcept {
        if (live_root.content_sha256 != physical.content_sha256) {
            return live_root.content_sha256 < physical.content_sha256;
        }
        return live_root.size_bytes < physical.size_bytes;
    };
    for (std::size_t index = 0U; index < payload_digests.size(); ++index) {
        const std::string& digest = payload_digests[index];
        const std::optional<std::uint64_t> payload_size =
            payload_snapshot.payload_size_or_none(digest);
        if (!payload_size.has_value()) {
            throw std::logic_error(
                state_->label +
                " retention-plan payload inventory lost one digest");
        }

        std::uint8_t root_mask = 0U;
        const HistoricalPayloadReferenceKey physical_key{
            .content_sha256 = digest,
            .size_bytes = *payload_size,
        };
        while (live_opened_root_index <
                   live_capabilities_before.opened_payload_roots.size() &&
               live_opened_root_less_than_physical(
                   live_capabilities_before
                       .opened_payload_roots[live_opened_root_index],
                   physical_key)) {
            ++live_opened_root_index;
        }
        const bool exact_opened_payload_root =
            live_opened_root_index <
                live_capabilities_before.opened_payload_roots.size() &&
            live_capabilities_before
                    .opened_payload_roots[live_opened_root_index]
                    .content_sha256 == physical_key.content_sha256 &&
            live_capabilities_before
                    .opened_payload_roots[live_opened_root_index]
                    .size_bytes == physical_key.size_bytes;
        const bool same_process_store_live_capability =
            plan.live_capabilities_may_reopen_all_current_payloads ||
            exact_opened_payload_root;
        if (same_process_store_live_capability) {
            increment_or_throw(
                plan.live_capability_rooted_physical_payload_count,
                "live-capability rooted physical payload");
            add_or_throw(
                plan.live_capability_rooted_physical_payload_bytes,
                *payload_size,
                "live-capability rooted physical payload bytes");
        }
        while (reference_index < payload_references.size() &&
               reference_key_less(
                   payload_references[reference_index].key, physical_key)) {
            account_missing_reference(
                payload_references[reference_index].root_mask);
            ++reference_index;
        }
        if (reference_index == payload_references.size() ||
            !historical_payload_reference_key_equal(
                payload_references[reference_index].key, physical_key)) {
            increment_or_throw(
                reachability.unreferenced_payload_count,
                "unreferenced payload");
            add_or_throw(
                reachability.unreferenced_payload_bytes, *payload_size,
                "unreferenced payload bytes");
            append_string(candidate_set_digest, digest);
            append_u64(candidate_set_digest, *payload_size);
            if (same_process_store_live_capability) {
                increment_or_throw(
                    plan.unreferenced_live_capability_rooted_payload_count,
                    "unreferenced live-capability rooted payload");
                add_or_throw(
                    plan.unreferenced_live_capability_rooted_payload_bytes,
                    *payload_size,
                    "unreferenced live-capability rooted payload bytes");
            }
        } else {
            root_mask = payload_references[reference_index].root_mask;
            if (historical_payload_mask_has(
                    root_mask, kHistoricalPayloadCurrentVisibleMask)) {
                account_present(
                    reachability.current_visible, *payload_size,
                    "current-visible present content");
            }
            if (historical_payload_mask_has(
                    root_mask, kHistoricalPayloadSupersededActiveMask)) {
                account_present(
                    reachability.superseded_active, *payload_size,
                    "superseded-active present content");
            }
            if (historical_payload_mask_has(
                    root_mask, kHistoricalPayloadInactiveEvidenceMask)) {
                account_present(
                    reachability.inactive_evidence, *payload_size,
                    "inactive-evidence present content");
            }
            if (historical_payload_mask_has(
                    root_mask, kHistoricalPayloadExplicitPinMask)) {
                account_present(
                    reachability.explicit_pins, *payload_size,
                    "explicit-pin present content");
            }
            account_present(
                reachability.retained_union, *payload_size,
                "retained-union present content");
            ++reference_index;
        }

        const SyncReplicaRetentionPlanDisposition disposition =
            retention_plan_disposition_from_root_mask(root_mask);
        switch (disposition) {
            case SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin:
                account_plan_class(
                    plan.current_or_explicit_pin, *payload_size,
                    "required-current-or-pin payload");
                break;
            case SyncReplicaRetentionPlanDisposition::RetainedHistoryOrEvidence:
                account_plan_class(
                    plan.retained_history_or_evidence, *payload_size,
                    "recoverable-history-only payload");
                break;
            case SyncReplicaRetentionPlanDisposition::
                    UnreferencedByRetainedFileOperations:
                account_plan_class(
                    plan.unreferenced_by_retained_file_operations, *payload_size,
                    "unreferenced-physical payload");
                break;
        }

        if (index < first_page_index) continue;
        increment_or_throw(
            plan.physical_payload_count_after_cursor,
            "physical payload after cursor");
        if (plan.entries.size() >=
            static_cast<std::size_t>(query.maximum_entries)) {
            continue;
        }
        plan.entries.push_back(SyncReplicaRetentionPlanEntry{
            .content_sha256 = digest,
            .size_bytes = *payload_size,
            .current_visible = historical_payload_mask_has(
                root_mask, kHistoricalPayloadCurrentVisibleMask),
            .superseded_active = historical_payload_mask_has(
                root_mask, kHistoricalPayloadSupersededActiveMask),
            .inactive_evidence = historical_payload_mask_has(
                root_mask, kHistoricalPayloadInactiveEvidenceMask),
            .explicit_pin = historical_payload_mask_has(
                root_mask, kHistoricalPayloadExplicitPinMask),
            .same_process_store_live_capability =
                same_process_store_live_capability,
            .disposition = disposition,
        });
    }

    while (reference_index < payload_references.size()) {
        account_missing_reference(
            payload_references[reference_index].root_mask);
        ++reference_index;
    }

    append_u64(
        candidate_set_digest,
        reachability.unreferenced_payload_count);
    append_u64(
        candidate_set_digest,
        reachability.unreferenced_payload_bytes);
    plan.unreferenced_candidate_set_digest =
        candidate_set_digest.finish_hex();

    // A grace-period identity must survive process restart. The process-store
    // incarnation and live-capability generation intentionally do not, so they
    // remain in the same-process deletion-free mark only. Future collection
    // must reacquire the global writer fence, re-prove every durable root and
    // transient obligation, and separately exclude current payload-use leases.
    Sha256DigestBuilder durable_candidate_witness;
    append_string(
        durable_candidate_witness,
        kRetentionPlanDurableCandidateWitnessDigestDomain);
    append_string(durable_candidate_witness, state_->folder_id);
    append_string(
        durable_candidate_witness,
        plan.source_replica_database_incarnation_sha256);
    append_u64(
        durable_candidate_witness,
        plan.source_replica_database_recovery_epoch);
    append_u64(
        durable_candidate_witness, plan.source_replica_state_generation);
    append_string(
        durable_candidate_witness, plan.source_operation_set_digest);
    append_string(
        durable_candidate_witness, plan.source_evidence_set_digest);
    append_string(
        durable_candidate_witness,
        plan.source_historical_version_pin_set_digest);
    append_string(
        durable_candidate_witness, plan.source_visible_state_digest);
    append_string(
        durable_candidate_witness, plan.source_payload_snapshot_digest);
    append_string(
        durable_candidate_witness,
        plan.source_payload_transient_namespace_digest);
    append_u64(
        durable_candidate_witness, plan.payload_transient_entry_count);
    append_u64(
        durable_candidate_witness, plan.payload_transient_bytes);
    append_u64(
        durable_candidate_witness, plan.payload_transient_reserved_bytes);
    append_string(
        durable_candidate_witness,
        plan.unreferenced_candidate_set_digest);
    append_u64(
        durable_candidate_witness,
        reachability.unreferenced_payload_count);
    append_u64(
        durable_candidate_witness,
        reachability.unreferenced_payload_bytes);
    plan.durable_candidate_witness_digest =
        durable_candidate_witness.finish_hex();

    // The complete physical observation remains beneath the store-global EX
    // fence while each bounded returned candidate is tested against the exact
    // inode-use protocol. A busy result is retained as evidence rather than
    // escalated into whole-plan lease deferral: it proves that an already-open
    // cooperating descriptor outlived its namespace observation. The probe is
    // deliberately page-bounded; unreturned candidates remain unclassified.
    Sha256DigestBuilder writer_fenced_candidate_page_digest;
    append_string(
        writer_fenced_candidate_page_digest,
        kRetentionPlanWriterFencedCandidatePageDigestDomain);
    append_string(
        writer_fenced_candidate_page_digest,
        kSyncReplicaFilePayloadUseLeaseProtocol);
    append_string(writer_fenced_candidate_page_digest, state_->folder_id);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.source_replica_database_incarnation_sha256);
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.source_replica_database_recovery_epoch);
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.source_replica_state_generation);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.source_operation_set_digest);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.source_evidence_set_digest);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.source_historical_version_pin_set_digest);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.source_payload_snapshot_digest);
    append_string(
        writer_fenced_candidate_page_digest,
        plan.unreferenced_candidate_set_digest);
    append_u64(
        writer_fenced_candidate_page_digest,
        query.start_after_content_sha256.has_value() ? 1U : 0U);
    if (query.start_after_content_sha256.has_value()) {
        append_string(
            writer_fenced_candidate_page_digest,
            *query.start_after_content_sha256);
    }
    append_u64(
        writer_fenced_candidate_page_digest, query.maximum_entries);
    plan.writer_fenced_candidate_page_entry_count =
        static_cast<std::uint64_t>(plan.entries.size());
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.writer_fenced_candidate_page_entry_count);
    for (SyncReplicaRetentionPlanEntry& entry : plan.entries) {
        if (entry.disposition ==
            SyncReplicaRetentionPlanDisposition::
                UnreferencedByRetainedFileOperations) {
            increment_or_throw(
                plan.returned_unreferenced_candidate_count,
                "returned unreferenced candidate");
            const bool exclusive_available =
                state_->payload_store->
                    writer_fenced_payload_use_exclusive_available_or_throw(
                        payload_snapshot, entry.content_sha256,
                        entry.size_bytes,
                        state_->label +
                            " retention-plan returned candidate payload-use "
                            "probe");
            if (exclusive_available) {
                entry.payload_use_disposition =
                    SyncReplicaRetentionPlanPayloadUseDisposition::
                        ExclusiveAvailableAtCutpoint;
                increment_or_throw(
                    plan.
                        returned_candidate_payload_use_exclusive_available_count,
                    "returned candidate exclusive payload-use availability");
            } else {
                entry.payload_use_disposition =
                    SyncReplicaRetentionPlanPayloadUseDisposition::
                        BusyAtCutpoint;
                increment_or_throw(
                    plan.returned_candidate_payload_use_busy_count,
                    "returned candidate busy payload-use lease");
            }
        }
        append_string(
            writer_fenced_candidate_page_digest, entry.content_sha256);
        append_u64(writer_fenced_candidate_page_digest, entry.size_bytes);
        append_u64(
            writer_fenced_candidate_page_digest,
            static_cast<std::uint64_t>(entry.disposition));
        append_u64(
            writer_fenced_candidate_page_digest,
            static_cast<std::uint64_t>(entry.payload_use_disposition));
    }
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.returned_unreferenced_candidate_count);
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.returned_candidate_payload_use_exclusive_available_count);
    append_u64(
        writer_fenced_candidate_page_digest,
        plan.returned_candidate_payload_use_busy_count);
    plan.writer_fenced_candidate_page_digest =
        writer_fenced_candidate_page_digest.finish_hex();

    const SyncReplicaSqliteSnapshot replica_final =
        state_->replica_owner->snapshot_or_throw();
    if (replica_snapshot.database_incarnation_sha256 !=
            replica_final.database_incarnation_sha256 ||
        replica_snapshot.database_recovery_epoch !=
            replica_final.database_recovery_epoch ||
        replica_snapshot.state_generation != replica_final.state_generation) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                RetentionMarkPublication,
            state_->label +
                " retention-plan source database lineage changed during "
                "writer-fenced projection; restart pagination");
    }
    if (replica_snapshot.operation_set_digest !=
        replica_final.operation_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetDuringPayloadObservation,
            state_->label +
                " retention-plan operation set changed during writer-fenced "
                "projection; restart pagination");
    }
    if (replica_snapshot.evidence_set_digest !=
        replica_final.evidence_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetDuringPayloadObservation,
            state_->label +
                " retention-plan retained evidence set changed during "
                "writer-fenced projection; restart pagination");
    }
    if (replica_snapshot.historical_version_pin_set_digest !=
        replica_final.historical_version_pin_set_digest) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetDuringPayloadObservation,
            state_->label +
                " retention-plan pin set changed during writer-fenced "
                "projection; restart pagination");
    }
    state_->payload_store->verify_writer_fenced_retention_snapshot_or_throw(
        payload_snapshot,
        state_->label + " retention-plan final writer-fence cutpoint");

    const SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
        live_capabilities_after =
            state_->payload_store->
                live_capability_cutpoint_excluding_snapshot_or_throw(
                    payload_snapshot,
                    state_->label +
                        " retention-plan live-capability final cutpoint");
    if (live_capabilities_after != live_capabilities_before) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                RetentionLiveCapabilitySet,
            state_->label +
                " retention-plan live payload capability set changed during "
                "projection; restart pagination");
    }

    Sha256DigestBuilder deletion_free_mark_digest;
    append_string(
        deletion_free_mark_digest,
        kRetentionPlanDeletionFreeMarkDigestDomain);
    append_string(
        deletion_free_mark_digest,
        kSyncReplicaFilePayloadUseLeaseProtocol);
    append_string(deletion_free_mark_digest, state_->folder_id);
    append_string(
        deletion_free_mark_digest,
        plan.source_replica_database_incarnation_sha256);
    append_u64(
        deletion_free_mark_digest,
        plan.source_replica_database_recovery_epoch);
    append_u64(
        deletion_free_mark_digest, plan.source_replica_state_generation);
    append_string(
        deletion_free_mark_digest, plan.source_operation_set_digest);
    append_string(
        deletion_free_mark_digest, plan.source_evidence_set_digest);
    append_string(
        deletion_free_mark_digest,
        plan.source_historical_version_pin_set_digest);
    append_string(
        deletion_free_mark_digest, plan.source_visible_state_digest);
    append_string(
        deletion_free_mark_digest, plan.source_payload_snapshot_digest);
    append_string(
        deletion_free_mark_digest,
        plan.source_payload_transient_namespace_digest);
    append_u64(
        deletion_free_mark_digest, plan.payload_transient_entry_count);
    append_u64(
        deletion_free_mark_digest, plan.payload_transient_bytes);
    append_u64(
        deletion_free_mark_digest, plan.payload_transient_reserved_bytes);
    append_string(
        deletion_free_mark_digest,
        plan.live_capability_process_store_scope_digest);
    append_string(
        deletion_free_mark_digest,
        plan.live_capability_process_store_scope_incarnation_digest);
    append_string(
        deletion_free_mark_digest, plan.live_capability_set_digest);
    append_u64(
        deletion_free_mark_digest, plan.live_snapshot_count);
    append_u64(
        deletion_free_mark_digest, plan.live_opened_payload_count);
    append_u64(
        deletion_free_mark_digest, plan.live_targeted_access_count);
    append_u64(
        deletion_free_mark_digest, plan.live_mutation_batch_count);
    append_u64(
        deletion_free_mark_digest,
        plan.distinct_live_opened_payload_root_count);
    append_u64(
        deletion_free_mark_digest,
        plan.distinct_live_opened_payload_root_bytes);
    append_u64(
        deletion_free_mark_digest,
        plan.live_capability_rooted_physical_payload_count);
    append_u64(
        deletion_free_mark_digest,
        plan.live_capability_rooted_physical_payload_bytes);
    append_u64(
        deletion_free_mark_digest,
        plan.unreferenced_live_capability_rooted_payload_count);
    append_u64(
        deletion_free_mark_digest,
        plan.unreferenced_live_capability_rooted_payload_bytes);
    append_string(
        deletion_free_mark_digest,
        plan.unreferenced_candidate_set_digest);
    append_u64(
        deletion_free_mark_digest,
        reachability.unreferenced_payload_count);
    append_u64(
        deletion_free_mark_digest,
        reachability.unreferenced_payload_bytes);
    plan.exact_deletion_free_mark_digest =
        deletion_free_mark_digest.finish_hex();

    const auto validate_class = [&]
        (const SyncReplicaHistoricalVersionPayloadReachabilityClass& value,
         std::string_view label) {
        if (value.present_content_count > value.distinct_content_count ||
            value.missing_content_count !=
                value.distinct_content_count - value.present_content_count) {
            throw std::logic_error(
                state_->label + " retention-plan " + std::string(label) +
                " reachability partition is inconsistent");
        }
    };
    validate_class(reachability.current_visible, "current-visible");
    validate_class(reachability.superseded_active, "superseded-active");
    validate_class(reachability.inactive_evidence, "inactive-evidence");
    validate_class(reachability.explicit_pins, "explicit-pins");
    validate_class(reachability.retained_union, "retained-union");

    std::uint64_t physical_entry_partition =
        reachability.retained_union.present_content_count;
    add_or_throw(
        physical_entry_partition, reachability.unreferenced_payload_count,
        "physical payload entry partition");
    std::uint64_t physical_byte_partition =
        reachability.retained_union.present_content_bytes;
    add_or_throw(
        physical_byte_partition, reachability.unreferenced_payload_bytes,
        "physical payload byte partition");
    std::uint64_t operation_partition =
        reachability.current_visible.file_operation_count;
    add_or_throw(
        operation_partition,
        reachability.superseded_active.file_operation_count,
        "retained file-operation partition");
    add_or_throw(
        operation_partition,
        reachability.inactive_evidence.file_operation_count,
        "retained file-operation partition");
    std::uint64_t planned_payload_partition =
        plan.current_or_explicit_pin.payload_count;
    add_or_throw(
        planned_payload_partition,
        plan.retained_history_or_evidence.payload_count,
        "planned payload partition");
    add_or_throw(
        planned_payload_partition,
        plan.unreferenced_by_retained_file_operations.payload_count,
        "planned payload partition");
    std::uint64_t planned_byte_partition =
        plan.current_or_explicit_pin.payload_bytes;
    add_or_throw(
        planned_byte_partition,
        plan.retained_history_or_evidence.payload_bytes,
        "planned byte partition");
    add_or_throw(
        planned_byte_partition,
        plan.unreferenced_by_retained_file_operations.payload_bytes,
        "planned byte partition");
    std::uint64_t returned_unreferenced_candidate_count = 0U;
    for (const SyncReplicaRetentionPlanEntry& entry : plan.entries) {
        if (entry.disposition ==
            SyncReplicaRetentionPlanDisposition::
                UnreferencedByRetainedFileOperations) {
            increment_or_throw(
                returned_unreferenced_candidate_count,
                "returned unreferenced candidate consistency count");
            if (entry.payload_use_disposition ==
                SyncReplicaRetentionPlanPayloadUseDisposition::
                    NotApplicable) {
                throw std::logic_error(
                    state_->label +
                    " retention-plan returned candidate lacks an exact-inode "
                    "payload-use observation");
            }
        } else if (entry.payload_use_disposition !=
                   SyncReplicaRetentionPlanPayloadUseDisposition::
                       NotApplicable) {
            throw std::logic_error(
                state_->label +
                " retention-plan retained payload carried a candidate-only "
                "payload-use observation");
        }
    }
    std::uint64_t returned_candidate_payload_use_partition =
        plan.returned_candidate_payload_use_exclusive_available_count;
    add_or_throw(
        returned_candidate_payload_use_partition,
        plan.returned_candidate_payload_use_busy_count,
        "returned candidate payload-use partition");
    if (physical_entry_partition != reachability.payload_entry_count ||
        physical_byte_partition != reachability.payload_indexed_bytes ||
        operation_partition != reachability.retained_union.file_operation_count ||
        observed_pinned_file_operations !=
            replica_snapshot.historical_version_pin_count ||
        reachability.explicit_pins.file_operation_count !=
            replica_snapshot.historical_version_pin_count ||
        planned_payload_partition != reachability.payload_entry_count ||
        planned_byte_partition != reachability.payload_indexed_bytes ||
        plan.unreferenced_by_retained_file_operations.payload_count !=
            reachability.unreferenced_payload_count ||
        plan.unreferenced_by_retained_file_operations.payload_bytes !=
            reachability.unreferenced_payload_bytes ||
        plan.live_capability_rooted_physical_payload_count >
            reachability.payload_entry_count ||
        plan.live_capability_rooted_physical_payload_bytes >
            reachability.payload_indexed_bytes ||
        plan.unreferenced_live_capability_rooted_payload_count >
            reachability.unreferenced_payload_count ||
        plan.unreferenced_live_capability_rooted_payload_bytes >
            reachability.unreferenced_payload_bytes ||
        returned_unreferenced_candidate_count !=
            plan.returned_unreferenced_candidate_count ||
        plan.writer_fenced_candidate_page_entry_count !=
            static_cast<std::uint64_t>(plan.entries.size()) ||
        returned_candidate_payload_use_partition !=
            plan.returned_unreferenced_candidate_count ||
        (plan.live_capabilities_may_reopen_all_current_payloads &&
         (plan.live_capability_rooted_physical_payload_count !=
              reachability.payload_entry_count ||
          plan.live_capability_rooted_physical_payload_bytes !=
              reachability.payload_indexed_bytes))) {
        throw std::logic_error(
            state_->label + " retention-plan projection is inconsistent");
    }

    plan.entry_limit_frontier_reached =
        plan.physical_payload_count_after_cursor >
        static_cast<std::uint64_t>(plan.entries.size());
    plan.truncated = plan.entry_limit_frontier_reached;
    if (plan.truncated) {
        if (plan.entries.empty()) {
            throw std::logic_error(
                state_->label +
                " retention-plan truncated page retained no cursor");
        }
        plan.next_start_after_content_sha256 =
            plan.entries.back().content_sha256;
    }

    if (mark_request != nullptr) {
        if (mark_publication == nullptr) {
            throw std::logic_error(
                state_->label +
                " payload retention mark lacks its publication result");
        }
        if (mark_request->
                    expected_source_replica_database_incarnation_sha256 !=
                plan.source_replica_database_incarnation_sha256 ||
            mark_request->expected_source_replica_database_recovery_epoch !=
                plan.source_replica_database_recovery_epoch ||
            mark_request->expected_source_replica_state_generation !=
                plan.source_replica_state_generation ||
            replica_final.database_incarnation_sha256 !=
                plan.source_replica_database_incarnation_sha256 ||
            replica_final.database_recovery_epoch !=
                plan.source_replica_database_recovery_epoch ||
            replica_final.state_generation !=
                plan.source_replica_state_generation) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RetentionMarkPublication,
                state_->label +
                    " payload retention mark source database lineage changed "
                    "before publication; recompute the mark");
        }
        if (mark_request->expected_durable_candidate_witness_digest !=
                plan.durable_candidate_witness_digest) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RetentionMarkPublication,
                state_->label +
                    " payload retention mark candidate witness changed before "
                    "publication; recompute the mark");
        }
        if (reachability.unreferenced_payload_count == 0U) {
            throw std::runtime_error(
                state_->label +
                " payload retention mark has no unreferenced candidates");
        }

        SyncReplicaFilePayloadRetentionMark mark;
        mark.marked_at_unix_seconds =
            mark_request->marked_at_unix_seconds;
        mark.policy = mark_request->policy;
        mark.source_replica_state_generation =
            plan.source_replica_state_generation;
        mark.source_operation_set_digest =
            plan.source_operation_set_digest;
        mark.source_evidence_set_digest =
            plan.source_evidence_set_digest;
        mark.source_historical_version_pin_set_digest =
            plan.source_historical_version_pin_set_digest;
        mark.source_visible_state_digest =
            plan.source_visible_state_digest;
        mark.source_payload_snapshot_digest =
            plan.source_payload_snapshot_digest;
        mark.source_payload_transient_namespace_digest =
            plan.source_payload_transient_namespace_digest;
        mark.unreferenced_candidate_set_digest =
            plan.unreferenced_candidate_set_digest;
        mark.durable_candidate_witness_digest =
            plan.durable_candidate_witness_digest;
        mark.unreferenced_candidate_payload_count =
            reachability.unreferenced_payload_count;
        mark.unreferenced_candidate_payload_bytes =
            reachability.unreferenced_payload_bytes;
        state_->payload_store->
            verify_writer_fenced_retention_snapshot_or_throw(
                payload_snapshot,
                state_->label +
                    " payload retention mark prepublication cutpoint");
        const SyncReplicaFilePayloadRetentionMarkPublication publication =
            state_->payload_store->publish_retention_mark_or_throw(
                payload_snapshot, std::move(mark));

        // SQLite is intentionally not held across the complete payload scan or
        // the atomic metadata publication. A concurrent owner change therefore
        // becomes a typed failure after publication. The committed record binds
        // the earlier monotonic generation, so it remains visible historical
        // evidence but can never inherit grace after that change.
        const SyncReplicaSqliteSnapshot replica_after_mark =
            state_->replica_owner->snapshot_or_throw();
        if (replica_after_mark.database_incarnation_sha256 !=
                plan.source_replica_database_incarnation_sha256 ||
            replica_after_mark.database_recovery_epoch !=
                plan.source_replica_database_recovery_epoch ||
            replica_after_mark.state_generation !=
                plan.source_replica_state_generation ||
            replica_after_mark.operation_set_digest !=
                plan.source_operation_set_digest ||
            replica_after_mark.evidence_set_digest !=
                plan.source_evidence_set_digest ||
            replica_after_mark.historical_version_pin_set_digest !=
                plan.source_historical_version_pin_set_digest ||
            replica_after_mark.visible_state_digest !=
                plan.source_visible_state_digest) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RetentionMarkPublication,
                state_->label +
                    " payload retention mark source changed during durable "
                    "publication; recompute the mark");
        }
        state_->payload_store->
            verify_writer_fenced_retention_snapshot_or_throw(
                payload_snapshot,
                state_->label +
                    " payload retention mark final writer-fence cutpoint");
        *mark_publication = publication;
    }
    return plan;
}

SyncReplicaSqliteHistoricalVersionPinResult
SyncReplicaFolderScanOwner::pin_historical_version_or_throw(
    std::string operation_id) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    return state_->replica_owner->pin_historical_version_or_throw(
        std::move(operation_id));
}

SyncReplicaSqliteHistoricalVersionPinResult
SyncReplicaFolderScanOwner::unpin_historical_version_or_throw(
    std::string operation_id) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    return state_->replica_owner->unpin_historical_version_or_throw(
        std::move(operation_id));
}

SyncReplicaHistoricalVersionRestoreResult
SyncReplicaFolderScanOwner::restore_historical_version_or_throw(
    std::string operation_id) {
    return restore_historical_version_or_throw(
        SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = std::move(operation_id),
            .expected_current_operation_id = std::nullopt,
        });
}

SyncReplicaHistoricalVersionRestoreResult
SyncReplicaFolderScanOwner::restore_historical_version_or_throw(
    SyncReplicaHistoricalVersionRestoreRequest request) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_sync_replica_historical_version_restore_request_or_throw(
        request, state_->label + " historical-version restore");
    const std::string& operation_id = request.operation_id;

    const SyncReplicaSqliteSnapshot replica_before =
        state_->replica_owner->snapshot_or_throw();
    const SyncReplicaModel model_before = SyncReplicaModel::restore_or_throw(
        replica_before.durable, replica_before.limits.model);
    const std::optional<SyncReplicaOperation> historical_optional =
        model_before.operation_by_id(operation_id);
    if (!historical_optional.has_value() ||
        historical_optional->kind != SyncReplicaValueKind::File) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore requires one active file operation");
    }
    const SyncReplicaOperation historical = *historical_optional;

    const std::optional<SyncReplicaPathView> path_view =
        model_before.visible_path(historical.canonical_path);
    if (request.expected_current_operation_id.has_value()) {
        const bool exact_current =
            path_view.has_value() &&
            path_view->visible_operation_ids.size() == 1U &&
            path_view->primary_operation_id ==
                *request.expected_current_operation_id &&
            path_view->visible_operation_ids.front() ==
                *request.expected_current_operation_id;
        if (!exact_current) {
            throw SyncReplicaHistoricalVersionSourceChangedError(
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RestoreCurrentOperation,
                state_->label +
                    " historical-version restore current operation changed from the inspected head");
        }
    }
    validate_canonical_path_for_root_or_throw(
        historical.canonical_path, state_->root_authority,
        state_->label + " historical-version restore");

    if (!path_view.has_value() || path_view->visible_operation_ids.empty()) {
        throw std::logic_error(
            state_->label +
            " historical-version restore path has no visible operation");
    }
    if (std::find(
            path_view->visible_operation_ids.begin(),
            path_view->visible_operation_ids.end(), historical.operation_id) !=
        path_view->visible_operation_ids.end()) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore operation is already visible");
    }
    if (path_view->visible_operation_ids.size() != 1U) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore refuses an unresolved path conflict");
    }
    const std::optional<SyncReplicaOperation> current_optional =
        model_before.operation_by_id(path_view->primary_operation_id);
    if (!current_optional.has_value()) {
        throw std::logic_error(
            state_->label +
            " historical-version restore current operation is inactive");
    }
    const SyncReplicaOperation current = *current_optional;
    if (request.expected_current_operation_id.has_value() &&
        current.operation_id != *request.expected_current_operation_id) {
        throw SyncReplicaHistoricalVersionSourceChangedError(
            SyncReplicaHistoricalVersionSourceChangeStage::
                RestoreCurrentOperation,
            state_->label +
                " historical-version restore current operation changed during selection");
    }
    if (current.kind == SyncReplicaValueKind::File &&
        current.size_bytes == historical.size_bytes &&
        current.content_sha256 == historical.content_sha256) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore would not change current file bytes");
    }

    const SyncReplicaFolderCatalogSnapshot catalog_before =
        snapshot_or_throw();
    if (!sync_replica_selective_sync_path_is_materialized(
            catalog_before.selective_sync_policy,
            historical.canonical_path)) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore path is metadata-only under the "
            "current selective-sync policy");
    }
    const std::optional<SyncReplicaFolderCatalogEntry> prior =
        find_catalog_entry(catalog_before, historical.canonical_path);
    if (!prior.has_value() ||
        !operation_matches_catalog_entry(current, *prior)) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore catalog is not at the current visible head");
    }

    const auto require_restore_catalog_cutpoint_or_throw = [&]() {
        const SyncReplicaFolderCatalogSnapshot current_catalog =
            snapshot_or_throw();
        if (find_catalog_entry(
                current_catalog, historical.canonical_path) != prior ||
            current_catalog.selective_sync_policy.generation !=
                catalog_before.selective_sync_policy.generation ||
            current_catalog.selective_sync_policy.policy_digest !=
                catalog_before.selective_sync_policy.policy_digest ||
            !sync_replica_selective_sync_path_is_materialized(
                current_catalog.selective_sync_policy,
                historical.canonical_path)) {
            throw std::runtime_error(
                state_->label +
                " historical-version restore catalog or selective-sync "
                "authority changed before publication");
        }
    };

    const auto observe_current_or_throw = [&]() {
        return observe_optional_regular_file_beneath_root_or_throw(
            state_->root_authority, state_->root_attestation_digest,
            historical.canonical_path, state_->limits.max_payload_bytes,
            state_->label + " historical-version restore current path");
    };
    std::optional<StableRegularFileObservation> current_observation =
        observe_current_or_throw();
    if (current.kind == SyncReplicaValueKind::File) {
        if (!current_observation.has_value() ||
            !observation_matches_operation(*current_observation, current) ||
            !observation_matches_catalog_entry(*current_observation, *prior)) {
            throw std::runtime_error(
                state_->label +
                " historical-version restore current file changed from its cataloged head");
        }
    } else if (current_observation.has_value()) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore tombstoned path is no longer absent");
    }

    SyncReplicaFilePayloadStoreTargetedAccess targeted =
        state_->payload_store->begin_targeted_access_or_throw(
            state_->label + " historical-version targeted payload access");
    std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
        targeted.open_optional_payload_for_operation_or_throw(
            historical,
            state_->label + " historical-version payload selection");
    if (!opened.has_value()) {
        throw std::runtime_error(
            state_->label +
            " historical-version payload is no longer retained");
    }
    SyncReplicaFilePayloadStoreOpenedPayload& payload = *opened;

    // Keep causal writers excluded while the exact current head and rooted
    // destination are changed. The guard is committed before the ordinary
    // scanner publishes a new local operation; its prepared observed-head
    // cutpoint then rejects any writer that wins after this guard is released.
    std::unique_ptr<SyncReplicaSqliteProjectionGuard> replica_guard =
        state_->replica_owner->guard_visible_state_at_digest_or_throw(
            replica_before.visible_state_digest);
    if (!replica_guard) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore visible projection changed before publication");
    }
    const SyncReplicaModel guarded_model = SyncReplicaModel::restore_or_throw(
        replica_guard->snapshot().durable,
        replica_guard->snapshot().limits.model);
    const std::optional<SyncReplicaOperation> guarded_historical =
        guarded_model.operation_by_id(historical.operation_id);
    const std::optional<SyncReplicaOperation> guarded_current =
        guarded_model.operation_by_id(current.operation_id);
    const std::optional<SyncReplicaPathView> guarded_view =
        guarded_model.visible_path(historical.canonical_path);
    if (!guarded_historical.has_value() ||
        *guarded_historical != historical || !guarded_current.has_value() ||
        *guarded_current != current || !guarded_view.has_value() ||
        guarded_view->visible_operation_ids !=
            path_view->visible_operation_ids) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore causal cutpoint changed");
    }
    require_restore_catalog_cutpoint_or_throw();
    std::optional<StableRegularFileObservation> publication_base =
        observe_current_or_throw();
    if (current.kind == SyncReplicaValueKind::File) {
        if (!publication_base.has_value() ||
            !observation_matches_catalog_entry(*publication_base, *prior) ||
            publication_base->metadata != current_observation->metadata) {
            throw std::runtime_error(
                state_->label +
                " historical-version restore current file changed before atomic replacement");
        }
    } else {
        if (publication_base.has_value()) {
            throw std::runtime_error(
                state_->label +
                " historical-version restore target appeared before creation");
        }
        ensure_relative_parent_beneath_root_or_throw(
            state_->root_authority, historical.canonical_path,
            state_->label + " historical-version restore parent");
        require_restore_catalog_cutpoint_or_throw();
        publication_base = observe_current_or_throw();
        if (publication_base.has_value()) {
            throw std::runtime_error(
                state_->label +
                " historical-version restore target appeared during parent creation");
        }
    }

    const auto publish_historical_bytes_or_throw = [&]() {
        require_restore_catalog_cutpoint_or_throw();
        if (current.kind == SyncReplicaValueKind::File) {
            copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw(
                state_->root_authority,
                fs::path(historical.canonical_path),
                payload.borrowed_descriptor(), payload.metadata(),
                payload.content_sha256(), publication_base->metadata,
                state_->label + " historical-version replacement");
        } else {
            copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
                state_->root_authority,
                fs::path(historical.canonical_path),
                payload.borrowed_descriptor(), payload.metadata(),
                payload.content_sha256(),
                state_->label + " historical-version creation");
        }
    };
    try {
        publish_historical_bytes_or_throw();
    } catch (const SyncAtomicFilePublicationError&) {
        std::optional<StableRegularFileObservation> recovered =
            observe_current_or_throw();
        if (!recovered.has_value() ||
            !observation_matches_operation(*recovered, historical)) {
            throw;
        }
        synchronize_observed_regular_file_and_parent_or_throw(
            state_->root_authority, historical.canonical_path, *recovered,
            state_->label + " historical-version publication recovery");
        recovered = observe_current_or_throw();
        if (!recovered.has_value() ||
            !observation_matches_operation(*recovered, historical)) {
            throw std::runtime_error(
                state_->label +
                " historical-version publication recovery lost exact bytes");
        }
    }

    const std::optional<StableRegularFileObservation> published_observation =
        observe_current_or_throw();
    if (!published_observation.has_value() ||
        !observation_matches_operation(*published_observation, historical)) {
        throw std::runtime_error(
            state_->label +
            " historical-version atomic publication did not leave exact bytes");
    }
    replica_guard->commit_or_throw();

    SyncReplicaPreparedRegularFile prepared =
        prepare_regular_file_bounded_for_policy_or_throw(
            historical.canonical_path, state_->limits.max_payload_bytes,
            catalog_before.selective_sync_policy);
    if (prepared.size_bytes() != historical.size_bytes ||
        prepared.content_sha256() != historical.content_sha256 ||
        prepared.observed_visible_operation_ids() !=
            path_view->visible_operation_ids) {
        throw std::runtime_error(
            state_->label +
            " historical-version restore publication cutpoint changed before local minting");
    }
    SyncReplicaFolderScanResult scanned =
        commit_prepared_regular_file_or_throw(std::move(prepared));
    if (scanned.disposition != SyncReplicaFolderScanDisposition::Published &&
        scanned.disposition !=
            SyncReplicaFolderScanDisposition::AdoptedVisibleOperation) {
        throw std::logic_error(
            state_->label +
            " historical-version restore did not create or adopt a causal successor");
    }

    SyncReplicaOperation restored;
    if (scanned.published_operation.has_value()) {
        restored = *scanned.published_operation;
    } else {
        const SyncReplicaSqliteSnapshot replica_after =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel model_after = SyncReplicaModel::restore_or_throw(
            replica_after.durable, replica_after.limits.model);
        const std::optional<SyncReplicaOperation> selected =
            model_after.operation_by_id(scanned.entry.operation_id);
        if (!selected.has_value()) {
            throw std::logic_error(
                state_->label +
                " historical-version restore selected an inactive successor");
        }
        restored = *selected;
    }
    if (restored.operation_id == historical.operation_id ||
        restored.operation_id == current.operation_id ||
        restored.kind != SyncReplicaValueKind::File ||
        restored.canonical_path != historical.canonical_path ||
        restored.size_bytes != historical.size_bytes ||
        restored.content_sha256 != historical.content_sha256 ||
        !sync_replica_operation_supersedes(restored, current)) {
        throw std::logic_error(
            state_->label +
            " historical-version restore did not publish the required new causal successor");
    }

    return SyncReplicaHistoricalVersionRestoreResult{
        .disposition = scanned.disposition ==
                SyncReplicaFolderScanDisposition::Published
            ? SyncReplicaHistoricalVersionRestoreDisposition::Published
            : SyncReplicaHistoricalVersionRestoreDisposition::
                  AdoptedVisibleOperation,
        .historical_operation = historical,
        .replaced_visible_operation = current,
        .restored_entry = std::move(scanned.entry),
        .restored_operation = std::move(restored),
    };
}

SyncReplicaFolderConvergencePassReport
SyncReplicaFolderScanOwner::run_convergence_pass_or_throw(
    const SyncReplicaFolderConvergencePassLimits& limits) {
    return run_convergence_pass_impl_or_throw(limits, std::nullopt);
}

SyncReplicaFolderConvergencePassReport
SyncReplicaFolderScanOwner::
run_convergence_pass_with_payload_snapshot_or_throw(
    SyncReplicaFilePayloadStoreSnapshot payload_snapshot,
    const SyncReplicaFolderConvergencePassLimits& limits) {
    std::optional<SyncReplicaFilePayloadStoreSnapshot> retained;
    retained.emplace(std::move(payload_snapshot));
    return run_convergence_pass_impl_or_throw(
        limits, std::move(retained));
}

SyncReplicaFolderConvergencePassReport
SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw(
    const SyncReplicaFolderConvergencePassLimits& limits,
    std::optional<SyncReplicaFilePayloadStoreSnapshot> payload_cutpoint) {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder scan owner is inactive");
    }
    validate_convergence_pass_limits_or_throw(
        limits, state_->limits, state_->payload_store->limits(),
        state_->label);

    SyncReplicaFolderConvergencePassReport report;
    if (payload_cutpoint.has_value()) {
        state_->payload_store->require_exact_snapshot_origin_or_throw(
            *payload_cutpoint,
            state_->label + " convergence payload snapshot handoff");
        report.payload_snapshot_handoff_count = 1U;
        report.payload_snapshot_handoff_entry_count =
            payload_cutpoint->entry_count();
    }
    const auto observe_payload_snapshot_or_throw = [&]() {
        SyncReplicaFilePayloadStoreSnapshot observed =
            state_->payload_store->snapshot_or_throw();
        report.payload_snapshot_observation_count = add_or_throw(
            report.payload_snapshot_observation_count, 1U,
            state_->label + " convergence payload snapshot observations");
        report.payload_snapshot_observed_entry_count = add_or_throw(
            report.payload_snapshot_observed_entry_count,
            observed.entry_count(),
            state_->label +
                " convergence payload snapshot observed entries");
        return observed;
    };

    // This pass-local catalog is a performance hint only. The one-path commit
    // and apply owners still load and compare current durable state before every
    // effect, so a concurrent same-path change can invalidate this hint but can
    // never authorize stale publication. Avoiding one complete catalog reload
    // per visited file matters because the correctness-first catalog owner is
    // intentionally O(catalog) per authoritative mutation.
    SyncReplicaFolderCatalogSnapshot catalog_hints = snapshot_or_throw();
    FolderScanProgressHead scan_progress =
        load_scan_progress_head_or_throw(
            *state_->catalog_db, state_->limits,
            state_->label + " pass scan-progress start");
    FolderRemoteWorkProgressHead remote_work_progress =
        load_remote_work_progress_head_or_throw(
            *state_->catalog_db, state_->limits,
            state_->label + " pass remote-apply progress start");
    const std::uint64_t active_scan_epoch = scan_progress.scan_epoch;
    report.local_scan_epoch = active_scan_epoch;
    report.local_scan_seen_path_count = scan_progress.seen_path_count;
    report.local_scan_resume_after_path =
        scan_progress.resume_after_path;
    report.remote_apply_started_after_path =
        remote_work_progress.resume_after_path;
    report.remote_apply_resume_after_path =
        remote_work_progress.resume_after_path;
    const auto update_catalog_hint =
        [&](const SyncReplicaFolderCatalogEntry& entry) {
            const auto found = std::lower_bound(
                catalog_hints.entries.begin(), catalog_hints.entries.end(),
                entry.canonical_path,
                [](const SyncReplicaFolderCatalogEntry& retained,
                   std::string_view path) {
                    return retained.canonical_path < path;
                });
            if (found != catalog_hints.entries.end() &&
                found->canonical_path == entry.canonical_path) {
                *found = entry;
            } else {
                catalog_hints.entries.insert(found, entry);
            }
        };

    SyncReplicaFolderObservationLimits traversal_limits;
    traversal_limits.maximum_entries = limits.maximum_entries;
    traversal_limits.maximum_regular_files = limits.maximum_regular_files;
    traversal_limits.maximum_file_bytes = limits.maximum_file_bytes;
    traversal_limits.maximum_total_file_bytes =
        limits.maximum_total_file_bytes;
    traversal_limits.maximum_relative_path_bytes =
        limits.maximum_relative_path_bytes;
    traversal_limits.maximum_directory_depth =
        limits.maximum_directory_depth;
    SyncReplicaFolderTraversalSegmentLimits local_scan_segment_limits;
    local_scan_segment_limits.maximum_regular_files =
        limits.maximum_local_scan_segment_regular_files;

    // The ordinary path-local owner is intentionally conservative: each file
    // reloads and reattests the complete reference catalog, replica, and
    // payload inventory before deciding whether a mutation is needed. That is
    // an excellent fallback oracle, but it made an unchanged N-file folder
    // perform roughly N complete O(history) authority observations. A
    // continuously running sync product spends most passes idle, so first try
    // one bounded read-only observation of the catalog, replica, and append-only
    // payload inventory, then re-prove the mutable database cutpoints. Any
    // missing payload, changed file, stale catalog mapping, remote apply
    // candidate, or cutpoint movement abandons this optimization and enters the
    // existing authoritative path below. This path can therefore skip work,
    // never authorize work.
    // Keep the exact append-only payload cutpoint outside the speculative idle
    // attempt. A single changed path may invalidate the all-idle conclusion,
    // but it does not invalidate the already verified content-addressed payload
    // inventory. The authoritative fallback can reuse that proof for unchanged
    // files instead of asking the exclusive mutation owner to hash every source
    // file a second time.
    struct IdleFastPathMiss final {};
    const auto try_idle_fast_path = [&]()
        -> std::optional<SyncReplicaFolderConvergencePassReport> {
        SyncReplicaFolderConvergencePassReport idle;

        // An idle proof is still path-local work: it reopens and hashes every
        // cataloged file and inspects every tombstoned pathname before it can
        // prove that no effect is needed. Gate on all retained mappings before
        // taking a speculative replica snapshot or even counting File rows, so
        // a known-large or tombstone-heavy catalog enters the authoritative
        // segmented path without duplicating whole-history projection work.
        // This only bounds optimization duplication; completed-epoch absence
        // adjudication remains authoritative whole-catalog work.
        if (static_cast<std::uint64_t>(catalog_hints.entries.size()) >
            local_scan_segment_limits.maximum_regular_files) {
            return std::nullopt;
        }
        const std::uint64_t catalog_regular_file_count =
            static_cast<std::uint64_t>(std::count_if(
                catalog_hints.entries.begin(), catalog_hints.entries.end(),
                [&](const SyncReplicaFolderCatalogEntry& entry) {
                    return entry.kind == SyncReplicaValueKind::File &&
                        sync_replica_selective_sync_path_is_materialized(
                            catalog_hints.selective_sync_policy,
                            entry.canonical_path);
                }));

        const SyncReplicaSqliteSnapshot replica_cutpoint =
            state_->replica_owner->snapshot_or_throw();
        const SyncReplicaModel replica_model =
            SyncReplicaModel::restore_or_throw(
                replica_cutpoint.durable,
                replica_cutpoint.limits.model);
        const std::vector<SyncReplicaPathView> remote_paths =
            replica_model.visible_paths();
        if (remote_paths.size() > limits.maximum_remote_paths) {
            // Preserve the ordinary pass's effect ordering. It may make
            // bounded local progress before diagnosing this remote bound.
            return std::nullopt;
        }
        if (remote_paths.size() >
                limits.maximum_remote_inspection_paths ||
            !remote_work_progress.inspection_sweep_basis_digest.empty()) {
            // A whole-projection idle proof must not exceed the ordinary rooted
            // inspection budget or bypass an already durable partial sweep.
            return std::nullopt;
        }

        // One lazily acquired snapshot proves every content-addressed payload
        // used by a catalog no-op. Snapshot construction holds the shared store
        // lease while it hashes the inventory, but the returned snapshot does
        // not retain that global lease. Each later byte reopen now re-enters the
        // current shared store reader fence and transfers the exact selected
        // inode into a descriptor-owned shared use lease. A future collector
        // must use the inverse side of that same fixed order—global store EX,
        // then candidate inode EX—while separately proving the still-unmodeled
        // active-pass and receiver roots. Keeping the snapshot lazy means an
        // actually empty folder does not gain a new payload-store dependency. A
        // payload already missing at observation falls back so the local file
        // can repair it through the ordinary put owner.
        const auto find_remote_path =
            [&](std::string_view canonical_path)
            -> const SyncReplicaPathView* {
            const auto found = std::lower_bound(
                remote_paths.begin(), remote_paths.end(), canonical_path,
                [](const SyncReplicaPathView& retained,
                   std::string_view path) {
                    return retained.canonical_path < path;
                });
            if (found == remote_paths.end() ||
                found->canonical_path != canonical_path) {
                return nullptr;
            }
            return &*found;
        };

        std::uint64_t idle_regular_file_count = 0U;
        try {
            const SyncReplicaFolderTraversalSegment idle_segment =
                visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                    state_->root_authority, {},
                    [&](const std::string& canonical_path,
                        std::uint64_t classified_size_bytes) {
                    const std::optional<
                        SyncReplicaFolderCatalogEntry> prior =
                        find_catalog_entry(catalog_hints, canonical_path);
                    if (!prior.has_value() ||
                        prior->kind != SyncReplicaValueKind::File ||
                        classified_size_bytes != prior->size_bytes) {
                        throw IdleFastPathMiss{};
                    }
                    const SyncReplicaOperation prior_operation =
                        require_catalog_operation_or_throw(
                            replica_model, *prior,
                            state_->label + " idle catalog base");
                    const SyncReplicaPathView* visible =
                        find_remote_path(canonical_path);
                    if (visible == nullptr ||
                        std::find(
                            visible->visible_operation_ids.begin(),
                            visible->visible_operation_ids.end(),
                            prior_operation.operation_id) ==
                            visible->visible_operation_ids.end()) {
                        throw IdleFastPathMiss{};
                    }

                    if (!payload_cutpoint.has_value()) {
                        payload_cutpoint.emplace(
                            observe_payload_snapshot_or_throw());
                    }
                    const std::optional<std::uint64_t> payload_size =
                        payload_cutpoint->payload_size_or_none(
                            prior->content_sha256);
                    if (!payload_size.has_value() ||
                        *payload_size != prior->size_bytes) {
                        throw IdleFastPathMiss{};
                    }

                    const std::uint64_t remaining =
                        limits.maximum_total_file_bytes -
                        idle.exact_local_file_bytes;
                    if (classified_size_bytes > remaining) {
                        throw std::runtime_error(
                            state_->label +
                            " idle classification exceeds its remaining "
                            "exact file-byte budget");
                    }
                    const std::uint64_t exact_read_limit = std::min(
                        limits.maximum_file_bytes,
                        std::max<std::uint64_t>(remaining, 1U));
                    std::optional<StableRegularFileObservation> observed =
                        observe_optional_regular_file_beneath_root_or_throw(
                            state_->root_authority,
                            state_->root_attestation_digest,
                            canonical_path, exact_read_limit,
                            state_->label + " idle observation");
                    if (!observed.has_value() ||
                        !observation_matches_catalog_entry(
                            *observed, *prior)) {
                        throw IdleFastPathMiss{};
                    }
                    if (observed->metadata.size_bytes > remaining) {
                        throw std::runtime_error(
                            state_->label +
                            " idle exact file bytes exceed the remaining "
                            "budget");
                    }
                    idle.exact_local_file_bytes = add_or_throw(
                        idle.exact_local_file_bytes,
                        observed->metadata.size_bytes,
                        state_->label + " idle exact local file bytes");
                    ++idle.local_catalog_no_op_count;
                    },
                    catalog_hints.selective_sync_policy,
                    traversal_limits, local_scan_segment_limits,
                    state_->label + " idle traversal");
            idle.traversal = idle_segment.traversal;
            idle.local_scan_stop_reason = idle_segment.stop_reason;
            idle.local_directory_enumeration_pass_count =
                idle_segment.directory_enumeration_pass_count;
            idle.local_peak_buffered_directory_component_batch_count =
                idle_segment.peak_buffered_directory_component_batch_count;
            idle.local_peak_simultaneously_buffered_directory_component_count =
                idle_segment
                    .peak_simultaneously_buffered_directory_component_count;
            idle_regular_file_count =
                idle_segment.traversal.regular_file_count;
            if (!idle_segment.completed) return std::nullopt;
        } catch (const IdleFastPathMiss&) {
            return std::nullopt;
        }

        // Every delivered regular path already proved a distinct File catalog
        // mapping in the callback. Equality of the two counts therefore proves
        // that no cataloged file was omitted, without retaining and re-sorting
        // a whole-tree duplicate path vector merely to perform set equality.
        if (idle_regular_file_count != catalog_regular_file_count) {
            return std::nullopt;
        }
        for (const SyncReplicaFolderCatalogEntry& entry :
             catalog_hints.entries) {
            if (entry.kind == SyncReplicaValueKind::File) {
                if (!sync_replica_selective_sync_path_is_materialized(
                        catalog_hints.selective_sync_policy,
                        entry.canonical_path)) {
                    idle.local_metadata_only_absence_suppressed_count =
                        add_or_throw(
                            idle.local_metadata_only_absence_suppressed_count,
                            1U,
                            state_->label +
                                " idle metadata-only absence suppressions");
                }
                continue;
            }
            // An ignored symlink or special object at a tombstoned pathname is
            // not absence. The no-follow inspector throws in that case, making
            // the unsupported substitution visible rather than a false idle.
            if (open_optional_regular_file_beneath_root_or_throw(
                    state_->root_authority, entry.canonical_path,
                    state_->label + " idle tombstone inspection")
                    .has_value()) {
                return std::nullopt;
            }
        }

        // Reproduce the no-effect classifications of the ordinary remote
        // phase. A sole-visible file whose pathname is absent requires an
        // actual apply and therefore exits to the authoritative fallback.
        for (const SyncReplicaPathView& path : remote_paths) {
            idle.remote_inspected_path_count = add_or_throw(
                idle.remote_inspected_path_count, 1U,
                state_->label + " idle inspected remote paths");
            if (path.visible_operation_ids.size() != 1U) {
                ++idle.skipped_conflicted_remote_path_count;
                continue;
            }
            if (path.canonical_path.size() >
                limits.maximum_relative_path_bytes) {
                return std::nullopt;
            }
            const std::uint64_t path_depth =
                static_cast<std::uint64_t>(std::count(
                    path.canonical_path.begin(),
                    path.canonical_path.end(), '/'));
            if (path_depth > limits.maximum_directory_depth) {
                return std::nullopt;
            }

            const std::string& operation_id =
                path.visible_operation_ids.front();
            const std::optional<SyncReplicaOperation> operation =
                replica_model.operation_by_id(operation_id);
            if (!operation.has_value() ||
                operation->kind != path.primary_kind ||
                operation->canonical_path != path.canonical_path) {
                throw std::logic_error(
                    state_->label +
                    " idle remote projection disagrees with active "
                    "evidence");
            }

            if (operation->kind == SyncReplicaValueKind::File &&
                !sync_replica_selective_sync_path_is_materialized(
                    catalog_hints.selective_sync_policy,
                    path.canonical_path)) {
                idle.remote_metadata_only_file_count = add_or_throw(
                    idle.remote_metadata_only_file_count, 1U,
                    state_->label + " idle metadata-only remote files");
                if (open_optional_regular_file_beneath_root_or_throw(
                        state_->root_authority, path.canonical_path,
                        state_->label +
                            " idle metadata-only rooted inspection")
                        .has_value()) {
                    // A present excluded file requires the authoritative
                    // dematerialization path. The idle oracle may skip work,
                    // but it must not declare a space-reclaiming policy settled
                    // while bytes are still rooted beneath the share.
                    return std::nullopt;
                }
                idle.remote_metadata_only_already_absent_file_count =
                    add_or_throw(
                        idle.remote_metadata_only_already_absent_file_count,
                        1U,
                        state_->label +
                            " idle metadata-only already-absent files");
                idle.remote_acknowledged_path_count = add_or_throw(
                    idle.remote_acknowledged_path_count, 1U,
                    state_->label + " idle acknowledged remote paths");
                continue;
            }

            std::optional<ScopedFd> local =
                open_optional_regular_file_beneath_root_or_throw(
                    state_->root_authority, path.canonical_path,
                    state_->label + " idle remote-path inspection");
            const std::optional<SyncReplicaFolderCatalogEntry> prior =
                find_catalog_entry(catalog_hints, path.canonical_path);
            if (operation->kind == SyncReplicaValueKind::File) {
                if (!local.has_value()) return std::nullopt;
                idle.remote_acknowledged_path_count = add_or_throw(
                    idle.remote_acknowledged_path_count, 1U,
                    state_->label + " idle acknowledged remote paths");
                continue;
            }
            if (local.has_value() || !prior.has_value() ||
                prior->kind != SyncReplicaValueKind::Tombstone ||
                prior->operation_id != operation->operation_id) {
                return std::nullopt;
            }
            ++idle.remote_catalog_no_op_count;
            idle.remote_acknowledged_path_count = add_or_throw(
                idle.remote_acknowledged_path_count, 1U,
                state_->label + " idle acknowledged remote paths");
        }

        if (payload_cutpoint.has_value()) {
            payload_cutpoint->preflight_or_throw(
                state_->label + " idle payload cutpoint reproof");
        }
        const SyncReplicaFolderCatalogSnapshot fresh_catalog =
            snapshot_or_throw();
        const FolderScanProgressHead fresh_scan_progress =
            load_scan_progress_head_or_throw(
                *state_->catalog_db, state_->limits,
                state_->label + " idle scan-progress reproof");
        const SyncReplicaSqliteSnapshot fresh_replica =
            state_->replica_owner->snapshot_or_throw();
        const FolderRemoteWorkProgressHead fresh_remote_work_progress =
            load_remote_work_progress_head_or_throw(
                *state_->catalog_db, state_->limits,
                state_->label + " idle remote-apply progress reproof");
        if (fresh_catalog != catalog_hints ||
            fresh_scan_progress != scan_progress ||
            fresh_replica != replica_cutpoint ||
            fresh_remote_work_progress != remote_work_progress) {
            return std::nullopt;
        }

        const bool idle_remote_sweep_had_unresolved_paths =
            idle.skipped_conflicted_remote_path_count != 0U ||
            idle.skipped_tombstone_remote_path_count != 0U;
        const std::optional<std::uint64_t> idle_fence_clear_generation =
            !idle_remote_sweep_had_unresolved_paths &&
                    fresh_catalog.selective_sync_absence_fence_generation != 0U
                ? std::optional<std::uint64_t>{
                      fresh_catalog.selective_sync_absence_fence_generation}
                : std::nullopt;
        const std::optional<FolderRemoteWorkProgressHead>
            terminal_remote_work_progress =
                publish_remote_work_progress_at_terminal_cutpoint_or_none(
                    *state_->replica_owner,
                    replica_cutpoint.visible_state_digest,
                    *state_->catalog_db, state_->limits,
                    state_->folder_id, state_->absolute_root_path,
                    state_->root_attestation_digest,
                    folder_catalog_cutpoint_head_or_throw(
                        fresh_catalog,
                        state_->label + " idle terminal cutpoint"),
                    fresh_scan_progress, fresh_remote_work_progress,
                    fresh_remote_work_progress,
                    idle_fence_clear_generation,
                    state_->label + " idle terminal cutpoint");
        if (!terminal_remote_work_progress.has_value()) {
            return std::nullopt;
        }

        idle.used_idle_fast_path = true;
        idle.payload_snapshot_handoff_count =
            report.payload_snapshot_handoff_count;
        idle.payload_snapshot_handoff_entry_count =
            report.payload_snapshot_handoff_entry_count;
        idle.payload_snapshot_observation_count =
            report.payload_snapshot_observation_count;
        idle.payload_snapshot_observed_entry_count =
            report.payload_snapshot_observed_entry_count;
        idle.local_scan_epoch = active_scan_epoch;
        idle.completed_local_scan_epoch = true;
        idle.local_scan_seen_path_count = 0U;
        idle.remote_apply_started_after_path =
            remote_work_progress.resume_after_path;
        idle.remote_apply_resume_after_path =
            remote_work_progress.resume_after_path;
        idle.remote_inspection_sweep_started_after_path =
            remote_work_progress.resume_after_path;
        idle.remote_inspection_sweep_seen_path_count =
            idle.remote_acknowledged_path_count;
        idle.completed_remote_inspection_sweep = true;
        idle.remote_inspection_sweep_had_unresolved_paths =
            idle_remote_sweep_had_unresolved_paths;
        idle.remote_inspection_terminal_cutpoint_reproved = true;
        idle.remote_inspection_terminal_catalog_digest =
            fresh_catalog.catalog_digest;
        idle.remote_inspection_terminal_visible_state_digest =
            replica_cutpoint.visible_state_digest;
        idle.remote_apply_stop_reason =
            SyncReplicaFolderRemoteApplyStopReason::EndOfProjection;
        return idle;
    };

    try {
        if (scan_progress.seen_path_count == 0U) {
            if (auto idle = try_idle_fast_path(); idle.has_value()) {
                return std::move(*idle);
            }
        }
    } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
        // A read-only optimization must not create a new terminal outcome.
        // Re-enter the ordinary owner, whose exact mutation attempt will make
        // the authoritative availability decision for the selected path.
    }

    // An early idle miss (for example, a newly sorted first path or a changed
    // classified size) can occur before the lazy payload cutpoint was needed.
    // Do not immediately turn that miss into a complete payload inventory: a
    // remote-only pass, an all-absent local namespace, or a tombstone-only
    // catalog has no local byte candidate that could use it. The fallback below
    // makes at most one best-effort shared snapshot only when traversal actually
    // reaches a regular file that can use the inventory. A busy
    // lease remains only an optimization miss; the exact mutation owner is the
    // authoritative fallback.
    bool fallback_payload_cutpoint_attempted = payload_cutpoint.has_value();
    const auto try_acquire_fallback_payload_cutpoint = [&]() {
        if (payload_cutpoint.has_value() ||
            fallback_payload_cutpoint_attempted) {
            return;
        }
        fallback_payload_cutpoint_attempted = true;
        try {
            payload_cutpoint.emplace(
                observe_payload_snapshot_or_throw());
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
        }
    };

    std::vector<std::string> blocked_absent_paths;
    // A present remote successor is eligible for later cyclic materialization
    // only after this invocation opened and hashed the exact cataloged
    // predecessor. Retain just those canonical paths; the authoritative apply
    // owner reopens and revalidates every selected predecessor immediately
    // before its effect.
    std::vector<std::string> observed_remote_successor_paths;
    // The traversal's delivered-file frontier bounds both this in-memory
    // acknowledgement set and the subsequent immediate journal transaction.
    // The whole-tree entry ceiling remains independent and still accounts for
    // directories and ignored namespace objects encountered by the walk.
    std::vector<std::string> segment_seen_paths;
    segment_seen_paths.reserve(static_cast<std::size_t>(
        std::min(
            limits.maximum_regular_files,
            limits.maximum_local_scan_segment_regular_files)));

    // A fallback pass can visit thousands of unchanged files after one path
    // invalidates the idle proof. Reuse one verified payload index across a
    // bounded segment of sequential local commits, not across the whole tree.
    // Count and exact-work ceilings bound the cooperative exclusive lease; a
    // snapshot-backed no-op releases it before catalog work, and every remote
    // apply releases it before taking shared payload authority. No network wait
    // occurs while a batch is live.
    std::optional<SyncReplicaFilePayloadStoreMutationBatch> payload_batch;
    std::uint64_t payload_batch_prepared_work_bytes = 0U;
    const auto require_payload_batch = [&]()
        -> SyncReplicaFilePayloadStoreMutationBatch& {
        if (!payload_batch.has_value()) {
            payload_batch.emplace(
                state_->payload_store->begin_mutation_batch_or_throw());
            payload_batch_prepared_work_bytes = 0U;
        }
        return *payload_batch;
    };
    const auto current_payload_batch_work_bytes = [&]() {
        if (!payload_batch.has_value()) return std::uint64_t{0U};
        return add_or_throw(
            add_or_throw(
                payload_batch->scan_hashed_bytes(),
                payload_batch->source_bytes(),
                state_->label +
                    " payload mutation scanned/source work bytes"),
            payload_batch_prepared_work_bytes,
            state_->label + " payload mutation current work bytes");
    };
    const auto release_payload_batch = [&]() {
        if (!payload_batch.has_value()) return;
        const std::uint64_t batch_work_bytes =
            current_payload_batch_work_bytes();
        report.payload_mutation_batch_count = add_or_throw(
            report.payload_mutation_batch_count, 1U,
            state_->label + " payload mutation batch count");
        report.payload_mutation_full_scan_count = add_or_throw(
            report.payload_mutation_full_scan_count,
            payload_batch->full_scan_count(),
            state_->label + " payload mutation full-scan count");
        report.payload_mutation_scan_hashed_entry_count = add_or_throw(
            report.payload_mutation_scan_hashed_entry_count,
            payload_batch->scan_hashed_entry_count(),
            state_->label + " payload mutation scan hashed entry count");
        report.payload_mutation_scan_hashed_bytes = add_or_throw(
            report.payload_mutation_scan_hashed_bytes,
            payload_batch->scan_hashed_bytes(),
            state_->label + " payload mutation scan hashed bytes");
        report.payload_mutation_scan_reused_entry_count = add_or_throw(
            report.payload_mutation_scan_reused_entry_count,
            payload_batch->scan_reused_entry_count(),
            state_->label + " payload mutation scan reused entry count");
        report.payload_mutation_scan_reused_bytes = add_or_throw(
            report.payload_mutation_scan_reused_bytes,
            payload_batch->scan_reused_bytes(),
            state_->label + " payload mutation scan reused bytes");
        report.payload_mutation_scan_process_reused_entry_count = add_or_throw(
            report.payload_mutation_scan_process_reused_entry_count,
            payload_batch->scan_process_reused_entry_count(),
            state_->label +
                " payload mutation scan process reused entry count");
        report.payload_mutation_scan_process_reused_bytes = add_or_throw(
            report.payload_mutation_scan_process_reused_bytes,
            payload_batch->scan_process_reused_bytes(),
            state_->label + " payload mutation scan process reused bytes");
        report.payload_mutation_scan_durable_reused_entry_count = add_or_throw(
            report.payload_mutation_scan_durable_reused_entry_count,
            payload_batch->scan_durable_reused_entry_count(),
            state_->label +
                " payload mutation scan durable reused entry count");
        report.payload_mutation_scan_durable_reused_bytes = add_or_throw(
            report.payload_mutation_scan_durable_reused_bytes,
            payload_batch->scan_durable_reused_bytes(),
            state_->label + " payload mutation scan durable reused bytes");
        report.payload_mutation_put_count = add_or_throw(
            report.payload_mutation_put_count, payload_batch->put_count(),
            state_->label + " payload mutation put count");
        report.payload_mutation_source_bytes = add_or_throw(
            report.payload_mutation_source_bytes,
            payload_batch->source_bytes(),
            state_->label + " payload mutation source bytes");
        report.payload_mutation_work_bytes = add_or_throw(
            report.payload_mutation_work_bytes, batch_work_bytes,
            state_->label + " payload mutation work bytes");
        report.payload_mutation_peak_batch_put_count = std::max(
            report.payload_mutation_peak_batch_put_count,
            payload_batch->put_count());
        report.payload_mutation_peak_batch_work_bytes = std::max(
            report.payload_mutation_peak_batch_work_bytes,
            batch_work_bytes);
        report.payload_mutation_inserted_count = add_or_throw(
            report.payload_mutation_inserted_count,
            payload_batch->inserted_count(),
            state_->label + " payload mutation inserted count");
        report.payload_mutation_already_present_count = add_or_throw(
            report.payload_mutation_already_present_count,
            payload_batch->already_present_count(),
            state_->label + " payload mutation already-present count");
        payload_batch.reset();
        payload_batch_prepared_work_bytes = 0U;
    };
    const auto batch_would_cross_work = [&](std::uint64_t next_bytes) {
        if (!payload_batch.has_value()) return false;
        const std::uint64_t used = current_payload_batch_work_bytes();
        return next_bytes > limits.maximum_payload_batch_work_bytes ||
            used > limits.maximum_payload_batch_work_bytes - next_bytes;
    };
    const auto release_saturated_payload_batch = [&]() {
        if (!payload_batch.has_value()) return;
        if (payload_batch->put_count() >=
                limits.maximum_payload_batch_puts ||
            current_payload_batch_work_bytes() >=
                limits.maximum_payload_batch_work_bytes) {
            release_payload_batch();
        }
    };

    const SyncReplicaFolderTraversalSegment local_segment =
        visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            state_->root_authority, scan_progress.resume_after_path,
            [&](const std::string& canonical_path,
                std::uint64_t classified_size_bytes) {
                // A matching cataloged extent is only a scheduling hint, but
                // it is a valuable one: the overwhelmingly common case is an
                // unchanged file. Do not retain an unrelated exclusive
                // payload-store batch while that likely no-op is opened and
                // completely hashed. A same-size edit simply acquires a fresh
                // batch after its exact digest proves that mutation is needed.
                // The commit owner still reloads and compares authoritative
                // state, so this hint can only shorten exclusion; it cannot
                // authorize a no-op or publication.
                try_acquire_fallback_payload_cutpoint();
                const std::optional<SyncReplicaFolderCatalogEntry> prior_hint =
                    find_catalog_entry(catalog_hints, canonical_path);
                if (payload_batch.has_value() && prior_hint.has_value() &&
                    prior_hint->kind == SyncReplicaValueKind::File &&
                    classified_size_bytes == prior_hint->size_bytes) {
                    release_payload_batch();
                }
                const std::uint64_t remaining =
                    limits.maximum_total_file_bytes -
                    report.exact_local_file_bytes;
                if (classified_size_bytes > remaining) {
                    throw std::runtime_error(
                        state_->label +
                        " pass classification exceeds its remaining exact "
                        "file-byte budget");
                }
                // The classified extent is a pre-read scheduling hint only.
                // Release the prior segment before opening and hashing this
                // path when that work would cross its exact-work frontier.
                if (batch_would_cross_work(classified_size_bytes)) {
                    release_payload_batch();
                }
                const bool batch_live_during_prepare =
                    payload_batch.has_value();
                const std::uint64_t exact_read_limit = std::min(
                    limits.maximum_file_bytes,
                    std::max<std::uint64_t>(remaining, 1U));
                SyncReplicaPreparedRegularFile prepared =
                    prepare_regular_file_bounded_for_policy_or_throw(
                        canonical_path, exact_read_limit,
                        catalog_hints.selective_sync_policy);
                auto& observation = prepared.require_state_or_throw(
                    state_->label + " pass prepared path");
                const std::uint64_t exact_size =
                    observation.observation.size_bytes;
                if (exact_size > remaining) {
                    throw std::runtime_error(
                        state_->label +
                        " pass exact file bytes exceed the remaining budget");
                }
                if (batch_live_during_prepare &&
                    payload_batch.has_value()) {
                    payload_batch_prepared_work_bytes = add_or_throw(
                        payload_batch_prepared_work_bytes, exact_size,
                        state_->label +
                            " payload mutation prepared work bytes");
                    // Classification can race a size change before the stable
                    // open. The read has already happened, but release now so
                    // no further work compounds that one-file overshoot.
                    if (current_payload_batch_work_bytes() >
                        limits.maximum_payload_batch_work_bytes) {
                        release_payload_batch();
                    }
                }

                bool handled_without_local_publication = false;
                const std::optional<SyncReplicaFolderCatalogEntry>& prior =
                    prior_hint;
                // Preparation already captured the exact visible head IDs
                // before reading the file. Only a sole head different from the
                // cataloged base can be a remote-successor candidate. Ordinary
                // no-op/local paths therefore avoid an otherwise redundant
                // complete replica snapshot and model restore; the commit owner
                // still performs its fresh authoritative comparison.
                if (prior.has_value() &&
                    prior->kind == SyncReplicaValueKind::File &&
                    observation.observed_visible_operation_ids.size() == 1U &&
                    observation.observed_visible_operation_ids.front() !=
                        prior->operation_id) {
                    const SyncReplicaSqliteSnapshot replica_snapshot =
                        state_->replica_owner->snapshot_or_throw();
                    const SyncReplicaModel model =
                        SyncReplicaModel::restore_or_throw(
                            replica_snapshot.durable,
                            replica_snapshot.limits.model);
                    const SyncReplicaOperation prior_operation =
                        require_catalog_operation_or_throw(
                            model, *prior,
                            state_->label + " pass catalog base");
                    const std::vector<SyncReplicaOperation> visible =
                        visible_operations(model, canonical_path);
                    if (visible.size() == 1U &&
                        visible.front().operation_id !=
                            prior_operation.operation_id &&
                        sync_replica_operation_supersedes(
                            visible.front(), prior_operation)) {
                        if (!(
                                observation.observation.size_bytes ==
                                    prior->size_bytes &&
                                observation.content_sha256 ==
                                    prior->content_sha256 &&
                                observation.source_snapshot_sha256 ==
                                    prior->source_snapshot_sha256)) {
                            // A remote successor and independently changed local
                            // bytes are a conflict. Preserve the local file and
                            // retained remote value; ordinary scanning must not
                            // manufacture a winner or terminate the service.
                            ++report.skipped_conflicted_remote_path_count;
                            blocked_absent_paths.push_back(canonical_path);
                            handled_without_local_publication = true;
                        } else {
                            // Do not let traversal order choose a remote winner.
                            // The exact predecessor proof above makes this path
                            // eligible, but all remote file/tombstone effects are
                            // selected later through one crash-surviving cyclic
                            // cursor. This prevents a continuously changing early
                            // pathname from consuming every bounded pass before a
                            // later remote path is ever considered.
                            observed_remote_successor_paths.push_back(
                                canonical_path);
                            handled_without_local_publication = true;
                        }
                    }
                }

                if (handled_without_local_publication) {
                    // A preserved conflict or a predecessor reserved for the
                    // cyclic remote planner must not leave a local exclusive
                    // payload lease spanning the next unrelated path.
                    release_payload_batch();
                } else {
                    const SyncReplicaFilePayloadStoreSnapshot*
                        retained_payload = nullptr;
                    if (payload_cutpoint.has_value()) {
                        const std::optional<std::uint64_t> retained_size =
                            payload_cutpoint->payload_size_or_none(
                                observation.content_sha256);
                        if (retained_size.has_value() &&
                            *retained_size == exact_size) {
                            retained_payload = &*payload_cutpoint;
                        }
                    }

                    // A catalog no-op or content-addressed duplicate needs no
                    // store mutation when the exact retained snapshot can reopen
                    // and re-prove its payload. Release a preceding mutation
                    // segment before that no-op commit. A genuinely new/missing
                    // digest may join the current segment only when the next put
                    // stays within both the put and exact-work frontiers.
                    SyncReplicaFilePayloadStoreMutationBatch* batch = nullptr;
                    if (retained_payload != nullptr) {
                        release_payload_batch();
                    } else {
                        if (payload_batch.has_value() &&
                            (payload_batch->put_count() >=
                                 limits.maximum_payload_batch_puts ||
                             batch_would_cross_work(exact_size))) {
                            release_payload_batch();
                        }
                        batch = &require_payload_batch();
                    }
                    const SyncReplicaFolderScanResult scanned =
                        commit_prepared_regular_file_with_payload_batch_or_throw(
                            std::move(prepared), batch, retained_payload);
                    record_scan_disposition(
                        report, scanned.disposition);
                    if (scanned.published_identity_preserving_rename
                            .has_value()) {
                        report.local_identity_preserving_rename_count =
                            add_or_throw(
                                report.local_identity_preserving_rename_count,
                                1U, state_->label +
                                    " local identity-preserving rename count");
                        // The paired catalog transaction already replaced the
                        // source File with its Tombstone. Keep the pass-local
                        // hint coherent with that exact terminal pair so the
                        // completed-epoch absence phase does not perform a
                        // redundant authoritative source-path observation.
                        SyncReplicaFolderCatalogEntry source_hint;
                        source_hint.canonical_path =
                            scanned.published_identity_preserving_rename->
                                source_canonical_path;
                        source_hint.kind = SyncReplicaValueKind::Tombstone;
                        source_hint.operation_id =
                            scanned.published_identity_preserving_rename->
                                source_tombstone_operation_id;
                        source_hint.last_seen_generation =
                            scanned.entry.last_seen_generation;
                        update_catalog_hint(source_hint);
                    }
                    update_catalog_hint(scanned.entry);
                    release_saturated_payload_batch();
                }
                report.exact_local_file_bytes = add_or_throw(
                    report.exact_local_file_bytes, exact_size,
                    state_->label + " pass exact local file bytes");
                // The path-local effect above is independently committed and
                // idempotent. Stage its scheduling acknowledgement in memory so
                // one pass publishes one authenticated journal segment instead
                // of one SQLite transaction per file.
                segment_seen_paths.push_back(canonical_path);
            },
            catalog_hints.selective_sync_policy,
            traversal_limits, local_scan_segment_limits,
            state_->label + " pass traversal");
    report.traversal = local_segment.traversal;
    report.local_scan_stop_reason = local_segment.stop_reason;
    report.local_directory_enumeration_pass_count =
        local_segment.directory_enumeration_pass_count;
    report.local_peak_buffered_directory_component_batch_count =
        local_segment.peak_buffered_directory_component_batch_count;
    report.local_peak_simultaneously_buffered_directory_component_count =
        local_segment.peak_simultaneously_buffered_directory_component_count;

    release_payload_batch();
    if (payload_cutpoint.has_value()) {
        payload_cutpoint->preflight_or_throw(
            state_->label + " fallback payload cutpoint reproof");
    }
    if (!segment_seen_paths.empty()) {
        scan_progress = record_scan_seen_paths_or_throw(
            *state_->catalog_db, state_->limits, active_scan_epoch,
            segment_seen_paths, state_->label + " pass scan progress");
        report.local_scan_seen_path_count = scan_progress.seen_path_count;
        report.local_scan_resume_after_path =
            scan_progress.resume_after_path;
    }

    // Only a fully consumed durable epoch can authorize absence. The seen
    // journal is rehashed in traversal order before it is compared with a fresh
    // catalog cutpoint. If a cataloged file omitted from that journal is still
    // present, the bounded suffix did not observe one coherent namespace;
    // restart the epoch without classifying any path as deleted. A path already
    // in the journal may change later and will be revisited in the next epoch.
    if (local_segment.completed) {
        std::vector<std::string> seen_regular_paths =
            load_complete_scan_seen_paths_or_throw(
                *state_->catalog_db, state_->limits, active_scan_epoch,
                state_->label + " complete scan epoch");
        std::sort(seen_regular_paths.begin(), seen_regular_paths.end());
        catalog_hints = snapshot_or_throw();

        std::vector<std::string> absence_candidates;
        absence_candidates.reserve(catalog_hints.entries.size());
        const bool selection_change_absence_fenced =
            catalog_hints.selective_sync_absence_fence_generation != 0U &&
            catalog_hints.selective_sync_absence_fence_generation ==
                catalog_hints.selective_sync_policy.generation;
        bool namespace_changed_behind_cursor = false;
        for (const SyncReplicaFolderCatalogEntry& entry :
             catalog_hints.entries) {
            if (entry.kind != SyncReplicaValueKind::File) {
                continue;
            }
            if (!sync_replica_selective_sync_path_is_materialized(
                    catalog_hints.selective_sync_policy,
                    entry.canonical_path)) {
                report.local_metadata_only_absence_suppressed_count =
                    add_or_throw(
                        report.local_metadata_only_absence_suppressed_count,
                        1U,
                        state_->label +
                            " metadata-only absence suppressions");
                continue;
            }
            if (std::binary_search(
                    seen_regular_paths.begin(), seen_regular_paths.end(),
                    entry.canonical_path)) {
                continue;
            }
            if (open_optional_regular_file_beneath_root_or_throw(
                    state_->root_authority, entry.canonical_path,
                    state_->label +
                        " completed epoch unseen-path inspection")
                    .has_value()) {
                namespace_changed_behind_cursor = true;
                break;
            }
            if (selection_change_absence_fenced) {
                report.local_selection_change_absence_suppressed_count =
                    add_or_throw(
                        report.local_selection_change_absence_suppressed_count,
                        1U,
                        state_->label +
                            " selection-change absence suppressions");
                continue;
            }
            absence_candidates.push_back(entry.canonical_path);
        }

        if (namespace_changed_behind_cursor) {
            scan_progress = reset_scan_progress_or_throw(
                *state_->catalog_db, state_->limits, active_scan_epoch,
                state_->label + " restart changed scan epoch");
            report.restarted_local_scan_epoch = true;
        } else {
            const SyncReplicaSqliteSnapshot absence_snapshot =
                state_->replica_owner->snapshot_or_throw();
            const SyncReplicaModel absence_model =
                SyncReplicaModel::restore_or_throw(
                    absence_snapshot.durable,
                    absence_snapshot.limits.model);
            for (const std::string& canonical_path : absence_candidates) {
                const std::optional<SyncReplicaFolderCatalogEntry> prior =
                    find_catalog_entry(catalog_hints, canonical_path);
                if (!prior.has_value() ||
                    prior->kind != SyncReplicaValueKind::File) {
                    continue;
                }
                const SyncReplicaOperation prior_operation =
                    require_catalog_operation_or_throw(
                        absence_model, *prior,
                        state_->label + " complete-scan absence base");
                const std::vector<SyncReplicaOperation> visible =
                    visible_operations(absence_model, canonical_path);
                const bool can_commit_absence =
                    visible.size() == 1U &&
                    (visible.front().operation_id ==
                         prior_operation.operation_id ||
                     (visible.front().kind ==
                          SyncReplicaValueKind::Tombstone &&
                      sync_replica_operation_supersedes(
                          visible.front(), prior_operation)));
                if (!can_commit_absence) {
                    ++report.skipped_conflicted_remote_path_count;
                    blocked_absent_paths.push_back(canonical_path);
                    continue;
                }
                const SyncReplicaFolderScanResult absent =
                    commit_complete_scan_absence_or_throw(canonical_path);
                record_scan_disposition(report, absent.disposition);
                update_catalog_hint(absent.entry);
            }
            scan_progress = reset_scan_progress_or_throw(
                *state_->catalog_db, state_->limits, active_scan_epoch,
                state_->label + " complete scan epoch reset");
            report.completed_local_scan_epoch = true;
        }
        report.local_scan_seen_path_count = scan_progress.seen_path_count;
        report.local_scan_resume_after_path =
            scan_progress.resume_after_path;
    }
    std::sort(blocked_absent_paths.begin(), blocked_absent_paths.end());
    blocked_absent_paths.erase(
        std::unique(
            blocked_absent_paths.begin(), blocked_absent_paths.end()),
        blocked_absent_paths.end());

    // Plan current sole-visible remote values only after local publication and
    // complete-scan absence handling. Files materialize missing paths or replace
    // an exact predecessor observed by this invocation; tombstones remove that
    // same proven predecessor or adopt already durable absence. Paths blocked
    // above remain untouched in both directions. Reload the exact durable catalog
    // cutpoint: the incrementally maintained vector above is a path lookup hint,
    // not a digest-bearing authority suitable for a cross-pass sweep basis.
    catalog_hints = snapshot_or_throw();
    const SyncReplicaSqliteSnapshot remote_snapshot =
        state_->replica_owner->snapshot_or_throw();
    const SyncReplicaModel remote_model = SyncReplicaModel::restore_or_throw(
        remote_snapshot.durable, remote_snapshot.limits.model);
    std::vector<RemoteProjectionEntry> remote_projection;
    {
        // visible_paths() carries conflict-preservation diagnostics that rooted
        // apply scheduling does not need after complete admission. Keep it in a
        // narrow scope, then retain only borrowed pointers into the immutable
        // remote model. The model outlives the projection and is never mutated,
        // so the subsequent descriptor walk avoids a second vector of canonical
        // paths, operation IDs, causal context, and predecessor IDs.
        const std::vector<SyncReplicaPathView> remote_paths =
            remote_model.visible_paths();
        if (remote_paths.size() > limits.maximum_remote_paths) {
            throw std::runtime_error(
                state_->label + " pass exceeds its remote-path limit");
        }
        remote_projection = validated_remote_projection_or_throw(
            remote_model, remote_paths, limits, report,
            state_->label + " pass");
    }

    // Refresh immediately before planning. Local scanning can be long-lived,
    // while this cursor is independent scheduling state and may have advanced in
    // another process. The optimistic publication below still rejects movement
    // between this cutpoint and completion of the selected effects.
    remote_work_progress = load_remote_work_progress_head_or_throw(
        *state_->catalog_db, state_->limits,
        state_->label + " pass remote-apply planning cursor");
    report.remote_apply_started_after_path =
        remote_work_progress.resume_after_path;
    report.remote_apply_resume_after_path =
        remote_work_progress.resume_after_path;

    std::sort(
        observed_remote_successor_paths.begin(),
        observed_remote_successor_paths.end());
    observed_remote_successor_paths.erase(
        std::unique(
            observed_remote_successor_paths.begin(),
            observed_remote_successor_paths.end()),
        observed_remote_successor_paths.end());

    // First perform hard admission over the complete sole-visible projection.
    // No post-scan filesystem or catalog effect occurs until even the cyclic
    // suffix has passed path, depth, evidence, and per-file limits. Scheduling
    // may rotate; safety admission never does.
    const std::string remote_inspection_sweep_basis =
        remote_inspection_sweep_basis_digest_or_throw(
            catalog_hints.catalog_digest,
            remote_snapshot.visible_state_digest,
            state_->label + " pass remote inspection sweep basis");
    const bool continuing_remote_inspection_sweep =
        remote_work_progress.inspection_sweep_basis_digest ==
        remote_inspection_sweep_basis;
    report.remote_inspection_sweep_started_after_path =
        continuing_remote_inspection_sweep
            ? remote_work_progress.inspection_sweep_started_after_path
            : remote_work_progress.resume_after_path;
    const std::uint64_t prior_remote_inspection_sweep_seen_path_count =
        continuing_remote_inspection_sweep
            ? remote_work_progress.inspection_sweep_seen_path_count
            : 0U;
    const bool prior_remote_inspection_sweep_had_unresolved_paths =
        continuing_remote_inspection_sweep &&
        remote_work_progress.inspection_sweep_had_unresolved_paths;
    const std::uint64_t remote_projection_path_count =
        static_cast<std::uint64_t>(remote_projection.size());
    if (continuing_remote_inspection_sweep) {
        validate_continuing_remote_inspection_sweep_or_throw(
            remote_work_progress, remote_projection,
            state_->label + " pass");
    }
    const std::uint64_t remote_inspection_sweep_remaining_path_count =
        remote_projection_path_count -
        prior_remote_inspection_sweep_seen_path_count;

    // A payload snapshot retained from the speculative/local phase predates
    // every digest for which this pass had to enter mutation put authority. A
    // put may report AlreadyPresent when another append became visible after
    // the frozen inventory, so inserted_count is not a sufficient freshness
    // fence. The historical snapshot remains exact for its frozen entries,
    // but it cannot prove presence of that later digest. Discard it after any
    // put attempt. Bounded remote work then performs exact one-digest selection
    // instead of falsely deferring ready bytes or turning one selected path
    // into a complete cold payload-root scan.
    if (report.payload_mutation_put_count != 0U) {
        payload_cutpoint.reset();
    }
    const auto require_retained_remote_payload_snapshot = [&]()
        -> const SyncReplicaFilePayloadStoreSnapshot& {
        if (!payload_cutpoint.has_value()) {
            throw std::logic_error(
                state_->label +
                " remote payload snapshot reuse requires a retained cutpoint");
        }
        if (report.remote_payload_snapshot_observation_count == 0U) {
            report.remote_payload_snapshot_observation_count = 1U;
            report.remote_payload_snapshot_entry_count =
                payload_cutpoint->entry_count();
        }
        return *payload_cutpoint;
    };
    std::optional<SyncReplicaFilePayloadStoreTargetedAccess>
        targeted_payload_access;
    const auto require_targeted_remote_payload_access = [&]()
        -> SyncReplicaFilePayloadStoreTargetedAccess& {
        if (!targeted_payload_access.has_value()) {
            targeted_payload_access.emplace(
                state_->payload_store->begin_targeted_access_or_throw(
                    state_->label + " remote targeted payload access"));
            report.remote_targeted_payload_access_count = add_or_throw(
                report.remote_targeted_payload_access_count, 1U,
                state_->label + " remote targeted payload accesses");
        }
        return *targeted_payload_access;
    };

    if (report.remote_apply_operation_count >
        limits.maximum_remote_apply_operations) {
        throw std::logic_error(
            state_->label +
            " local traversal exceeded the remote-apply operation frontier");
    }
    const std::uint64_t remaining_remote_apply_operations =
        limits.maximum_remote_apply_operations -
        report.remote_apply_operation_count;
    std::vector<RemoteApplyCandidate> remote_candidates;
    remote_candidates.reserve(static_cast<std::size_t>(
        std::min<std::uint64_t>(
            static_cast<std::uint64_t>(remote_projection.size()),
            remaining_remote_apply_operations)));
    std::uint64_t remote_candidate_bytes =
        report.exact_remote_file_bytes;

    // Rotate after the last completely acknowledged remote-work path. The
    // cursor prevents prefix monopoly; the authenticated sweep basis prevents
    // that rotation from being mistaken for completion across different catalog
    // or replica cutpoints. A continuing sweep visits only its unacknowledged
    // remainder, so a stable N-path projection completes after exactly N
    // acknowledgements even when the per-pass inspection frontier is smaller.
    const CyclicRemoteProjectionStart cyclic_start =
        cyclic_remote_projection_start_after(
            remote_projection, remote_work_progress.resume_after_path);
    const std::size_t start_index = cyclic_start.index;
    report.remote_apply_wrapped_projection =
        cyclic_start.wrapped_before_first_path;
    std::optional<std::string> last_acknowledged_remote_path;
    bool segment_had_unresolved_paths =
        report.skipped_conflicted_remote_path_count != 0U ||
        report.skipped_tombstone_remote_path_count != 0U;
    const auto mark_remote_path_unresolved = [&]() {
        segment_had_unresolved_paths = true;
    };
    const auto acknowledge_remote_path =
        [&](const std::string& canonical_path) {
            last_acknowledged_remote_path = canonical_path;
            report.remote_acknowledged_path_count = add_or_throw(
                report.remote_acknowledged_path_count, 1U,
                state_->label + " acknowledged remote work paths");
        };

    std::uint64_t offset = 0U;
    for (; offset < remote_inspection_sweep_remaining_path_count; ++offset) {
        if (report.remote_inspected_path_count >=
            limits.maximum_remote_inspection_paths) {
            report.remote_apply_stop_reason =
                SyncReplicaFolderRemoteApplyStopReason::
                    InspectionPathFrontier;
            break;
        }

        const std::size_t unwrapped_index = start_index +
            static_cast<std::size_t>(offset);
        if (unwrapped_index >= remote_projection.size()) {
            report.remote_apply_wrapped_projection = true;
        }
        const std::size_t projection_index =
            unwrapped_index % remote_projection.size();
        const RemoteProjectionEntry& projected =
            remote_projection[projection_index];
        const std::string& canonical_path =
            projected.operation->canonical_path;
        const SyncReplicaOperation& operation = *projected.operation;
        report.remote_inspected_path_count = add_or_throw(
            report.remote_inspected_path_count, 1U,
            state_->label + " inspected remote work paths");

        if (operation.kind == SyncReplicaValueKind::File &&
            !sync_replica_selective_sync_path_is_materialized(
                catalog_hints.selective_sync_policy, canonical_path)) {
            report.remote_metadata_only_file_count = add_or_throw(
                report.remote_metadata_only_file_count, 1U,
                state_->label + " metadata-only remote files");

            // Metadata-only is a rooted absence contract, not merely a network
            // omission hint. A path that has never been materialized needs no
            // effect. A present path is admitted as one bounded candidate so the
            // effect phase can re-prove its exact catalog predecessor, current
            // causal target, private retained payload, and current selection
            // before performing a conditional atomic removal. Planning reads no
            // file bytes and grants no unlink authority.
            std::optional<ScopedFd> local =
                open_optional_regular_file_beneath_root_or_throw(
                    state_->root_authority, canonical_path,
                    state_->label +
                        " metadata-only rooted-presence inspection");
            if (!local.has_value()) {
                report.remote_metadata_only_already_absent_file_count =
                    add_or_throw(
                        report.remote_metadata_only_already_absent_file_count,
                        1U,
                        state_->label +
                            " metadata-only already-absent files");
                acknowledge_remote_path(canonical_path);
                continue;
            }

            const SyncPosixRegularFileSnapshotMetadata local_metadata =
                observe_sync_posix_regular_file_descriptor_or_throw(
                    local->get(),
                    SyncPosixDescriptorLinkPolicy::stable_named_object,
                    state_->label +
                        " metadata-only rooted-presence metadata");
            if (local_metadata.size_bytes > limits.maximum_file_bytes) {
                report
                    .remote_metadata_only_dematerialization_blocked_file_count =
                    add_or_throw(
                        report
                            .remote_metadata_only_dematerialization_blocked_file_count,
                        1U,
                        state_->label +
                            " metadata-only dematerialization blocked files");
                mark_remote_path_unresolved();
                acknowledge_remote_path(canonical_path);
                continue;
            }

            const std::uint64_t selected_operation_count =
                static_cast<std::uint64_t>(remote_candidates.size());
            const bool operation_count_full =
                selected_operation_count >= remaining_remote_apply_operations;
            const bool aggregate_file_bytes_full =
                remote_candidate_bytes > limits.maximum_total_file_bytes ||
                local_metadata.size_bytes >
                    limits.maximum_total_file_bytes - remote_candidate_bytes;
            if (operation_count_full || aggregate_file_bytes_full) {
                report.remote_apply_stop_reason = operation_count_full
                    ? SyncReplicaFolderRemoteApplyStopReason::
                          OperationCountFrontier
                    : SyncReplicaFolderRemoteApplyStopReason::
                          AggregateFileByteFrontier;
                report.deferred_remote_apply_candidate_count = 1U;
                break;
            }

            remote_candidate_bytes = add_or_throw(
                remote_candidate_bytes, local_metadata.size_bytes,
                state_->label +
                    " planned metadata-only dematerialization bytes");
            remote_candidates.push_back(RemoteApplyCandidate{
                projection_index,
                RemoteApplyCandidateKind::DematerializeMetadataOnlyFile,
                local_metadata.size_bytes});
            acknowledge_remote_path(canonical_path);
            continue;
        }

        if (std::binary_search(
                blocked_absent_paths.begin(), blocked_absent_paths.end(),
                canonical_path)) {
            mark_remote_path_unresolved();
            if (operation.kind == SyncReplicaValueKind::Tombstone) {
                ++report.skipped_tombstone_remote_path_count;
            }
            acknowledge_remote_path(canonical_path);
            continue;
        }

        std::optional<ScopedFd> local =
            open_optional_regular_file_beneath_root_or_throw(
                state_->root_authority, canonical_path,
                state_->label + " pass remote-path inspection");
        const std::optional<SyncReplicaFolderCatalogEntry> prior =
            find_catalog_entry(catalog_hints, canonical_path);
        if (local.has_value()) {
            // A current-pass observation already hashed the exact cataloged
            // predecessor. Otherwise the durable catalog may nominate the path
            // only after fresh rooted descriptor metadata reproduces its source
            // snapshot. Neither route authorizes bytes: the selected apply owner
            // reopens, hashes, and compares the file immediately before effect.
            const bool observed_this_pass = std::binary_search(
                observed_remote_successor_paths.begin(),
                observed_remote_successor_paths.end(), canonical_path);
            if (!prior.has_value() ||
                prior->kind != SyncReplicaValueKind::File) {
                ++report.skipped_conflicted_remote_path_count;
                mark_remote_path_unresolved();
                if (operation.kind == SyncReplicaValueKind::Tombstone) {
                    ++report.skipped_tombstone_remote_path_count;
                }
                acknowledge_remote_path(canonical_path);
                continue;
            }
            const SyncReplicaOperation prior_operation =
                require_catalog_operation_or_throw(
                    remote_model, *prior,
                    state_->label + " cyclic remote catalog base");
            if (operation.operation_id == prior_operation.operation_id) {
                acknowledge_remote_path(canonical_path);
                continue;
            }
            bool revalidated_catalog_predecessor = false;
            if (!observed_this_pass) {
                const SyncPosixRegularFileSnapshotMetadata metadata =
                    observe_sync_posix_regular_file_descriptor_or_throw(
                        local->get(),
                        SyncPosixDescriptorLinkPolicy::stable_named_object,
                        state_->label +
                            " catalog predecessor metadata reproof");
                if (metadata.size_bytes != prior->size_bytes ||
                    source_snapshot_digest(
                        state_->root_attestation_digest, canonical_path,
                        metadata, prior->content_sha256) !=
                        prior->source_snapshot_sha256) {
                    ++report.skipped_conflicted_remote_path_count;
                    mark_remote_path_unresolved();
                    if (operation.kind ==
                        SyncReplicaValueKind::Tombstone) {
                        ++report.skipped_tombstone_remote_path_count;
                    }
                    acknowledge_remote_path(canonical_path);
                    continue;
                }
                revalidated_catalog_predecessor = true;
            }
            if (!sync_replica_operation_supersedes(
                    operation, prior_operation)) {
                ++report.skipped_conflicted_remote_path_count;
                mark_remote_path_unresolved();
                acknowledge_remote_path(canonical_path);
                continue;
            }
            if (revalidated_catalog_predecessor) {
                report.remote_apply_revalidated_catalog_predecessor_count =
                    add_or_throw(
                        report
                            .remote_apply_revalidated_catalog_predecessor_count,
                        1U,
                        state_->label +
                            " revalidated catalog predecessors");
            }
        } else if (operation.kind == SyncReplicaValueKind::Tombstone) {
            if (prior.has_value() &&
                prior->kind == SyncReplicaValueKind::Tombstone &&
                prior->operation_id == operation.operation_id) {
                acknowledge_remote_path(canonical_path);
                continue;
            }
        } else {
            // A cataloged file that is now absent and whose sole-visible
            // operation is still the exact catalog predecessor is a potential
            // local deletion. Never restore that baseline here. An incomplete
            // epoch may not have reached the path, while a nominally completed
            // segmented epoch may have seen it in an earlier pass and then lost
            // it before the final suffix. Distinct remote successors remain
            // eligible and retain their established priority.
            if (prior.has_value() &&
                prior->kind == SyncReplicaValueKind::File &&
                prior->operation_id == operation.operation_id &&
                catalog_hints.selective_sync_absence_fence_generation == 0U) {
                ++report
                    .deferred_unadjudicated_local_absence_remote_file_count;
                mark_remote_path_unresolved();
                acknowledge_remote_path(canonical_path);
                continue;
            }
        }

        // Remote evidence can arrive before the corresponding bounded payload
        // transfer completes. When local work already produced a complete
        // payload cutpoint, use it to skip missing candidates before the effect
        // frontier. A remote-only pass performs a descriptor-rooted target-name
        // probe under the shared store lease. That probe reads no payload bytes
        // and makes no complete-namespace claim, but it preserves the established
        // rule that unavailable prefixes do not consume effect slots or block a
        // ready suffix. Selected present files receive their exact SHA-256 proof
        // only if the atomic publication owner consumes their descriptor below.
        if (operation.kind == SyncReplicaValueKind::File) {
            std::optional<std::uint64_t> indexed_size;
            if (payload_cutpoint.has_value()) {
                const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot =
                    require_retained_remote_payload_snapshot();
                indexed_size = payload_snapshot.payload_size_or_none(
                    operation.content_sha256);
            } else {
                report.remote_targeted_payload_probe_count = add_or_throw(
                    report.remote_targeted_payload_probe_count, 1U,
                    state_->label + " targeted remote payload probes");
                indexed_size = require_targeted_remote_payload_access().
                    observe_optional_payload_size_for_operation_or_throw(
                        operation,
                        state_->label + " remote payload availability probe");
            }
            if (!indexed_size.has_value()) {
                report.deferred_remote_payload_candidate_count = add_or_throw(
                    report.deferred_remote_payload_candidate_count, 1U,
                    state_->label +
                        " deferred remote payload candidates");
                mark_remote_path_unresolved();
                acknowledge_remote_path(canonical_path);
                continue;
            }
            if (*indexed_size != operation.size_bytes) {
                throw std::logic_error(
                    state_->label +
                    " remote payload inventory size disagrees with visible operation");
            }
        }

        const std::uint64_t selected_operation_count =
            static_cast<std::uint64_t>(remote_candidates.size());
        const bool operation_count_full =
            selected_operation_count >= remaining_remote_apply_operations;
        const bool aggregate_file_bytes_full =
            operation.kind == SyncReplicaValueKind::File &&
            (remote_candidate_bytes > limits.maximum_total_file_bytes ||
             operation.size_bytes >
                 limits.maximum_total_file_bytes - remote_candidate_bytes);
        if (operation_count_full || aggregate_file_bytes_full) {
            report.remote_apply_stop_reason = operation_count_full
                ? SyncReplicaFolderRemoteApplyStopReason::
                      OperationCountFrontier
                : SyncReplicaFolderRemoteApplyStopReason::
                      AggregateFileByteFrontier;
            report.deferred_remote_apply_candidate_count = 1U;
            break;
        }

        if (operation.kind == SyncReplicaValueKind::File) {
            remote_candidate_bytes = add_or_throw(
                remote_candidate_bytes, operation.size_bytes,
                state_->label + " planned remote file bytes");
        }
        // The projection is immutable and remains alive through execution.
        // Retain only its index rather than duplicating the operation ID and
        // file metadata for every bounded candidate.
        remote_candidates.push_back(RemoteApplyCandidate{
            projection_index,
            RemoteApplyCandidateKind::ApplyVisibleOperation,
            operation.kind == SyncReplicaValueKind::File
                ? operation.size_bytes
                : 0U});
        acknowledge_remote_path(canonical_path);
    }

    report.remote_inspection_sweep_seen_path_count = add_or_throw(
        prior_remote_inspection_sweep_seen_path_count,
        report.remote_acknowledged_path_count,
        state_->label + " remote inspection sweep seen paths");
    if (report.remote_inspection_sweep_seen_path_count >
        remote_projection_path_count) {
        throw std::logic_error(
            state_->label +
            " remote inspection sweep exceeded its projection");
    }
    report.completed_remote_inspection_sweep =
        report.remote_inspection_sweep_seen_path_count ==
        remote_projection_path_count;
    report.remote_inspection_sweep_had_unresolved_paths =
        prior_remote_inspection_sweep_had_unresolved_paths ||
        segment_had_unresolved_paths;
    report.deferred_remote_inspection_path_count =
        remote_projection_path_count -
        report.remote_inspection_sweep_seen_path_count;
    if (report.completed_remote_inspection_sweep) {
        report.remote_apply_stop_reason =
            SyncReplicaFolderRemoteApplyStopReason::EndOfProjection;
    } else if (report.remote_apply_stop_reason ==
               SyncReplicaFolderRemoteApplyStopReason::NotStarted) {
        throw std::logic_error(
            state_->label +
            " incomplete remote inspection sweep has no stop reason");
    }

    const auto dematerialize_metadata_only_file_or_throw =
        [&](const SyncReplicaOperation& planned_target,
            std::uint64_t planned_file_bytes)
        -> MetadataOnlyDematerializationResult {
        if (planned_target.kind != SyncReplicaValueKind::File) {
            throw std::logic_error(
                state_->label +
                " metadata-only dematerialization target is not a file");
        }
        validate_canonical_path_for_root_or_throw(
            planned_target.canonical_path, state_->root_authority,
            state_->label + " metadata-only dematerialization");

        const auto load_targeted_catalog_path_cutpoint_or_throw =
            [&](std::string_view stage) {
            report.remote_targeted_catalog_path_cutpoint_count = add_or_throw(
                report.remote_targeted_catalog_path_cutpoint_count, 1U,
                state_->label + " targeted catalog path cutpoints");
            return load_folder_catalog_path_cutpoint_or_throw(
                *state_->catalog_db, state_->folder_id,
                state_->absolute_root_path,
                state_->root_attestation_digest, state_->limits,
                planned_target.canonical_path,
                state_->label + " metadata-only " + std::string(stage));
        };

        const auto require_targeted_replica_path_cutpoint_or_throw =
            [&](const std::optional<SyncReplicaFolderCatalogEntry>&
                    expected_prior,
                std::string_view stage)
            -> std::optional<SyncReplicaOperation> {
            report.remote_targeted_replica_path_cutpoint_count = add_or_throw(
                report.remote_targeted_replica_path_cutpoint_count, 1U,
                state_->label + " targeted replica path cutpoints");
            SyncReplicaSqliteTargetedPathCutpoint current_replica =
                state_->replica_owner->targeted_path_cutpoint_or_throw(
                    planned_target.canonical_path,
                    expected_prior.has_value()
                        ? std::optional<std::string>{
                              expected_prior->operation_id}
                        : std::nullopt);
            if (!current_replica.sole_visible_operation.has_value() ||
                *current_replica.sole_visible_operation != planned_target) {
                throw std::runtime_error(
                    state_->label + " metadata-only " +
                    std::string(stage) + " causal target changed");
            }
            if (!expected_prior.has_value()) return std::nullopt;

            std::optional<SyncReplicaOperation> prior_operation;
            if (current_replica
                    .requested_retained_operation_is_sole_visible) {
                prior_operation =
                    std::move(*current_replica.sole_visible_operation);
            } else if (
                current_replica.distinct_retained_operation.has_value()) {
                prior_operation =
                    std::move(*current_replica.distinct_retained_operation);
            }
            if (!prior_operation.has_value() ||
                !operation_matches_catalog_entry(
                    *prior_operation, *expected_prior)) {
                throw std::runtime_error(
                    state_->label + " metadata-only " +
                    std::string(stage) +
                    " catalog mapping disagrees with retained replica evidence");
            }
            return prior_operation;
        };

        const auto require_target_and_catalog_cutpoint_or_throw =
            [&](std::uint64_t expected_selection_generation,
                std::string_view expected_selection_digest,
                const std::optional<SyncReplicaFolderCatalogEntry>&
                    expected_prior,
                std::string_view stage) {
            const FolderCatalogPathCutpoint current_catalog =
                load_targeted_catalog_path_cutpoint_or_throw(stage);
            if (current_catalog.selection_generation !=
                    expected_selection_generation ||
                current_catalog.selection_digest !=
                    expected_selection_digest ||
                current_catalog.entry != expected_prior) {
                throw std::runtime_error(
                    state_->label + " metadata-only " +
                    std::string(stage) +
                    " catalog or selection authority changed");
            }

            (void)require_targeted_replica_path_cutpoint_or_throw(
                expected_prior, stage);
        };

        const FolderCatalogPathCutpoint catalog_before =
            load_targeted_catalog_path_cutpoint_or_throw(
                "dematerialization planning reproof");
        if (catalog_before.selection_generation !=
                catalog_hints.selective_sync_policy.generation ||
            catalog_before.selection_digest !=
                catalog_hints.selective_sync_policy.policy_digest) {
            throw std::runtime_error(
                state_->label +
                " metadata-only dematerialization selection changed after planning");
        }
        const std::optional<SyncReplicaFolderCatalogEntry> prior =
            catalog_before.entry;

        std::optional<StableRegularFileObservation> local =
            observe_optional_regular_file_beneath_root_or_throw(
                state_->root_authority,
                state_->root_attestation_digest,
                planned_target.canonical_path,
                limits.maximum_file_bytes,
                state_->label + " metadata-only dematerialization source");
        if (!local.has_value()) {
            require_target_and_catalog_cutpoint_or_throw(
                catalog_before.selection_generation,
                catalog_before.selection_digest, prior,
                "already-absent reproof");
            return {
                MetadataOnlyDematerializationDisposition::AlreadyAbsent,
                0U};
        }
        if (local->metadata.size_bytes != planned_file_bytes ||
            !prior.has_value() ||
            prior->kind != SyncReplicaValueKind::File ||
            !observation_matches_catalog_entry(*local, *prior)) {
            return {
                MetadataOnlyDematerializationDisposition::BlockedLocalState,
                0U};
        }

        std::optional<SyncReplicaOperation> targeted_prior =
            require_targeted_replica_path_cutpoint_or_throw(
                prior, "dematerialization planning reproof");
        if (!targeted_prior.has_value()) {
            throw std::logic_error(
                state_->label +
                " metadata-only dematerialization lost its catalog base");
        }
        const SyncReplicaOperation prior_operation =
            std::move(*targeted_prior);
        if (planned_target.operation_id != prior_operation.operation_id &&
            !sync_replica_operation_supersedes(
                planned_target, prior_operation)) {
            return {
                MetadataOnlyDematerializationDisposition::BlockedLocalState,
                0U};
        }

        // Do not remove the synchronized tree's only proved copy. Retain one
        // exact immutable private-payload descriptor through the unlink. The
        // complete snapshot path and targeted path both enter the current
        // store reader fence and transfer the selected inode into its shared
        // use lease before this code gains deletion authority.
        std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
            retained_private_payload;
        if (payload_cutpoint.has_value()) {
            const SyncReplicaFilePayloadStoreSnapshot& retained_snapshot =
                require_retained_remote_payload_snapshot();
            const std::optional<std::uint64_t> retained_size =
                retained_snapshot.payload_size_or_none(
                    prior_operation.content_sha256);
            if (!retained_size.has_value()) {
                return {
                    MetadataOnlyDematerializationDisposition::
                        BlockedPayloadUnavailable,
                    0U};
            }
            if (*retained_size != prior_operation.size_bytes) {
                throw std::logic_error(
                    state_->label +
                    " metadata-only retained payload size disagrees with catalog evidence");
            }
            retained_private_payload.emplace(
                retained_snapshot.open_payload_for_operation_or_throw(
                    prior_operation,
                    state_->label +
                        " metadata-only retained predecessor payload"));
        } else {
            std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
                require_targeted_remote_payload_access().
                    open_optional_payload_for_operation_or_throw(
                        prior_operation,
                        state_->label +
                            " metadata-only targeted predecessor payload");
            if (!opened.has_value()) {
                return {
                    MetadataOnlyDematerializationDisposition::
                        BlockedPayloadUnavailable,
                    0U};
            }
            report.remote_targeted_payload_selection_count = add_or_throw(
                report.remote_targeted_payload_selection_count, 1U,
                state_->label +
                    " metadata-only targeted payload selections");
            report.remote_targeted_payload_selected_bytes = add_or_throw(
                report.remote_targeted_payload_selected_bytes,
                prior_operation.size_bytes,
                state_->label +
                    " metadata-only targeted payload selected bytes");
            retained_private_payload.emplace(std::move(*opened));
        }
        if (retained_private_payload->content_sha256() !=
                prior_operation.content_sha256 ||
            retained_private_payload->size_bytes() !=
                prior_operation.size_bytes) {
            throw std::logic_error(
                state_->label +
                " metadata-only private payload selection changed identity");
        }

        require_target_and_catalog_cutpoint_or_throw(
            catalog_before.selection_generation,
            catalog_before.selection_digest, prior,
            "pre-unlink reproof");
        const SyncPosixRegularFileSnapshotMetadata descriptor_now =
            observe_sync_posix_regular_file_descriptor_or_throw(
                local->descriptor.get(),
                SyncPosixDescriptorLinkPolicy::stable_named_object,
                state_->label +
                    " metadata-only retained source descriptor");
        if (descriptor_now != local->metadata) {
            return {
                MetadataOnlyDematerializationDisposition::BlockedLocalState,
                0U};
        }

        remove_sync_file_atomically_if_expected_content_under_directory_or_throw(
            state_->root_authority,
            fs::path(planned_target.canonical_path),
            local->metadata,
            local->content_sha256,
            state_->label + " metadata-only dematerialization removal");

        if (open_optional_regular_file_beneath_root_or_throw(
                state_->root_authority, planned_target.canonical_path,
                state_->label +
                    " metadata-only post-removal rooted inspection")
                .has_value()) {
            throw std::runtime_error(
                state_->label +
                " metadata-only path reappeared after dematerialization");
        }
        require_target_and_catalog_cutpoint_or_throw(
            catalog_before.selection_generation,
            catalog_before.selection_digest, prior,
            "post-unlink reproof");
        return {
            MetadataOnlyDematerializationDisposition::Removed,
            local->metadata.size_bytes};
    };

    bool completed_selected_remote_apply = false;
    for (const RemoteApplyCandidate& candidate : remote_candidates) {
        if (report.remote_apply_operation_count >=
            limits.maximum_remote_apply_operations) {
            throw std::logic_error(
                state_->label +
                " remote apply plan exceeded its operation frontier");
        }
        if (candidate.projection_index >= remote_projection.size()) {
            throw std::logic_error(
                state_->label +
                " remote apply candidate escaped its admitted projection");
        }
        const SyncReplicaOperation& operation =
            *remote_projection[candidate.projection_index].operation;

        if (candidate.kind ==
            RemoteApplyCandidateKind::DematerializeMetadataOnlyFile) {
            report.remote_metadata_only_dematerialization_attempt_count =
                add_or_throw(
                    report
                        .remote_metadata_only_dematerialization_attempt_count,
                    1U,
                    state_->label +
                        " metadata-only dematerialization attempts");
            const MetadataOnlyDematerializationResult dematerialized =
                dematerialize_metadata_only_file_or_throw(
                    operation, candidate.planned_file_bytes);
            switch (dematerialized.disposition) {
                case MetadataOnlyDematerializationDisposition::Removed:
                    if (dematerialized.removed_bytes !=
                        candidate.planned_file_bytes) {
                        throw std::logic_error(
                            state_->label +
                            " metadata-only removal bytes changed after planning");
                    }
                    report.remote_apply_operation_count = add_or_throw(
                        report.remote_apply_operation_count, 1U,
                        state_->label +
                            " remote apply operation count");
                    report
                        .remote_metadata_only_dematerialized_file_count =
                        add_or_throw(
                            report
                                .remote_metadata_only_dematerialized_file_count,
                            1U,
                            state_->label +
                                " metadata-only dematerialized files");
                    report.remote_metadata_only_dematerialized_bytes =
                        add_or_throw(
                            report.remote_metadata_only_dematerialized_bytes,
                            dematerialized.removed_bytes,
                            state_->label +
                                " metadata-only dematerialized bytes");
                    completed_selected_remote_apply = true;
                    continue;
                case MetadataOnlyDematerializationDisposition::AlreadyAbsent:
                    report.remote_apply_operation_count = add_or_throw(
                        report.remote_apply_operation_count, 1U,
                        state_->label +
                            " remote apply operation count");
                    report.remote_metadata_only_already_absent_file_count =
                        add_or_throw(
                            report
                                .remote_metadata_only_already_absent_file_count,
                            1U,
                            state_->label +
                                " metadata-only already-absent files");
                    completed_selected_remote_apply = true;
                    continue;
                case MetadataOnlyDematerializationDisposition::
                    BlockedPayloadUnavailable:
                    report
                        .remote_metadata_only_dematerialization_payload_unavailable_count =
                        add_or_throw(
                            report
                                .remote_metadata_only_dematerialization_payload_unavailable_count,
                            1U,
                            state_->label +
                                " metadata-only unavailable predecessor payloads");
                    [[fallthrough]];
                case MetadataOnlyDematerializationDisposition::
                    BlockedLocalState:
                    report
                        .remote_metadata_only_dematerialization_blocked_file_count =
                        add_or_throw(
                            report
                                .remote_metadata_only_dematerialization_blocked_file_count,
                            1U,
                            state_->label +
                                " metadata-only dematerialization blocked files");
                    mark_remote_path_unresolved();
                    continue;
            }
            throw std::logic_error(
                state_->label +
                " metadata-only dematerialization returned an unknown disposition");
        }
        if (candidate.kind !=
            RemoteApplyCandidateKind::ApplyVisibleOperation) {
            throw std::logic_error(
                state_->label +
                " remote apply candidate has an unknown kind");
        }

        std::optional<SyncReplicaFolderApplyResult> applied;
        if (operation.kind == SyncReplicaValueKind::File) {
            if (payload_cutpoint.has_value()) {
                applied =
                    apply_visible_regular_file_with_payload_snapshot_or_throw(
                        operation.operation_id, &*payload_cutpoint);
            } else {
                applied =
                    try_apply_visible_regular_file_with_targeted_payload_or_throw(
                        operation.operation_id,
                        require_targeted_remote_payload_access());
                if (!applied.has_value()) {
                    report.deferred_remote_payload_candidate_count =
                        add_or_throw(
                            report.deferred_remote_payload_candidate_count, 1U,
                            state_->label +
                                " deferred remote payload candidates");
                    mark_remote_path_unresolved();
                    continue;
                }
                report.remote_targeted_payload_selection_count = add_or_throw(
                    report.remote_targeted_payload_selection_count, 1U,
                    state_->label + " targeted remote payload selections");
                report.remote_targeted_payload_selected_bytes = add_or_throw(
                    report.remote_targeted_payload_selected_bytes,
                    operation.size_bytes,
                    state_->label + " targeted remote payload selected bytes");
            }
        } else {
            applied =
                apply_visible_tombstone_or_throw(operation.operation_id);
        }
        if (!applied.has_value()) {
            throw std::logic_error(
                state_->label + " remote apply produced no disposition");
        }
        completed_selected_remote_apply = true;
        record_apply_disposition(report, applied->disposition);
        update_catalog_hint(applied->entry);
        if (operation.kind == SyncReplicaValueKind::File) {
            report.exact_remote_file_bytes = add_or_throw(
                report.exact_remote_file_bytes, operation.size_bytes,
                state_->label + " pass exact remote file bytes");
        }
    }

    // Targeted absence is discovered after projection acknowledgement and can
    // therefore strengthen, but never weaken, the segment's unresolved result.
    report.remote_inspection_sweep_had_unresolved_paths =
        prior_remote_inspection_sweep_had_unresolved_paths ||
        segment_had_unresolved_paths;

    FolderRemoteWorkProgressHead wanted_remote_work_progress =
        remote_work_progress;
    if (last_acknowledged_remote_path.has_value()) {
        wanted_remote_work_progress.resume_after_path =
            *last_acknowledged_remote_path;
    }
    const auto reset_wanted_remote_inspection_sweep = [&]() {
        wanted_remote_work_progress.inspection_sweep_basis_digest.clear();
        wanted_remote_work_progress
            .inspection_sweep_started_after_path.clear();
        wanted_remote_work_progress.inspection_sweep_seen_path_count = 0U;
        wanted_remote_work_progress
            .inspection_sweep_had_unresolved_paths = false;
    };
    if (report.completed_remote_inspection_sweep ||
        completed_selected_remote_apply) {
        // Completion needs no retained journal. Any selected effect changes the
        // catalog cutpoint and invalidates an incomplete pre-effect sweep, even
        // when the apply owner discovers an idempotent no-op. A targeted payload
        // absence completed no apply owner and therefore preserves the exact
        // acknowledged sweep segment instead of discarding useful progress.
        reset_wanted_remote_inspection_sweep();
    } else if (
        report.remote_inspection_sweep_seen_path_count != 0U) {
        wanted_remote_work_progress.inspection_sweep_basis_digest =
            remote_inspection_sweep_basis;
        wanted_remote_work_progress.inspection_sweep_started_after_path =
            report.remote_inspection_sweep_started_after_path;
        wanted_remote_work_progress.inspection_sweep_seen_path_count =
            report.remote_inspection_sweep_seen_path_count;
        wanted_remote_work_progress
            .inspection_sweep_had_unresolved_paths =
            report.remote_inspection_sweep_had_unresolved_paths;
    } else {
        // A stale basis with no acknowledged path is not progress. Retire it so
        // the next pass starts a clean sweep at the retained fairness cursor.
        reset_wanted_remote_inspection_sweep();
    }

    // A completed rooted sweep is meaningful only for the exact catalog and
    // replica projection it inspected. Re-prove the full catalog first, then
    // acquire the replica writer guard and atomically compare the lightweight
    // catalog/scan/progress heads while that guard is live. Effects already
    // committed by this pass remain safe and idempotent if the fence misses;
    // only scheduling progress and settlement authority are withheld.
    const SyncReplicaFolderCatalogSnapshot terminal_catalog =
        snapshot_or_throw();
    const std::optional<std::uint64_t> terminal_fence_clear_generation =
        report.completed_remote_inspection_sweep &&
                !report.remote_inspection_sweep_had_unresolved_paths &&
                terminal_catalog.selective_sync_absence_fence_generation != 0U
            ? std::optional<std::uint64_t>{
                  terminal_catalog.selective_sync_absence_fence_generation}
            : std::nullopt;
    const std::optional<FolderRemoteWorkProgressHead>
        terminal_remote_work_progress =
            publish_remote_work_progress_at_terminal_cutpoint_or_none(
                *state_->replica_owner,
                remote_snapshot.visible_state_digest,
                *state_->catalog_db, state_->limits,
                state_->folder_id, state_->absolute_root_path,
                state_->root_attestation_digest,
                folder_catalog_cutpoint_head_or_throw(
                    terminal_catalog,
                    state_->label + " pass terminal cutpoint"),
                scan_progress, remote_work_progress,
                wanted_remote_work_progress,
                terminal_fence_clear_generation,
                state_->label + " pass terminal cutpoint");
    if (!terminal_remote_work_progress.has_value()) {
        report.completed_remote_inspection_sweep = false;
        report.remote_inspection_sweep_seen_path_count = 0U;
        report.deferred_remote_inspection_path_count =
            remote_projection_path_count;
        report.remote_apply_stop_reason =
            SyncReplicaFolderRemoteApplyStopReason::AuthorityCutpointChanged;
        report.remote_apply_resume_after_path =
            remote_work_progress.resume_after_path;
        return report;
    }
    remote_work_progress = *terminal_remote_work_progress;
    report.remote_inspection_terminal_cutpoint_reproved = true;
    report.remote_inspection_terminal_catalog_digest =
        terminal_catalog.catalog_digest;
    report.remote_inspection_terminal_visible_state_digest =
        remote_snapshot.visible_state_digest;
    report.remote_apply_resume_after_path =
        remote_work_progress.resume_after_path;

    return report;
}

}  // namespace anonsync

#endif
