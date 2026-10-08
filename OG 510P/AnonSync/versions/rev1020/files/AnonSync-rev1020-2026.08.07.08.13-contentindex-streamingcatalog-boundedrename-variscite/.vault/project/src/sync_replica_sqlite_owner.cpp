#include "sync_replica_sqlite_owner.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_digest_accumulator.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <array>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <limits>
#include <map>
#include <set>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include <openssl/rand.h>

#include <sqlite3.h>

namespace anonsync {
namespace {

static_assert(
    std::is_nothrow_move_constructible_v<
        SyncReplicaSqliteDatabaseRecoveryEpochResult>,
    "database recovery result must cross the committed cutpoint without allocation");

constexpr std::uint64_t kLegacySchemaVersion = 1U;
constexpr std::uint64_t kPreviousSchemaVersion = 2U;
constexpr std::uint64_t kClockSchemaVersion = 3U;
constexpr std::uint64_t kRetryProvenanceSchemaVersion = 4U;
constexpr std::uint64_t kRetentionRootSchemaVersion = 5U;
constexpr std::uint64_t kHistoricalPinSchemaVersion = 6U;
constexpr std::uint64_t kDatabaseLineageSchemaVersion = 7U;
constexpr std::uint64_t kVisiblePathSchemaVersion = 8U;
constexpr std::uint64_t kSchemaVersion = 9U;
constexpr std::uint64_t kMaxSchemaSqlBytes = 1024U * 1024U;

struct SchemaDefinition final {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view stored_sql;
};

// Rev0869 schema retained as an exact migration source. Migration is attempted
// only after this complete sqlite_schema contract and the full legacy cutpoint
// have been independently attested inside one IMMEDIATE transaction.
constexpr std::array<SchemaDefinition, 8> kLegacySchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=1),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
}};

// sqlite_schema.sql is protocol evidence. These are the exact strings SQLite
// stores after the main-qualified CREATE statements emitted below.
// Rev0871 schema retained as an exact migration source. Like the rev0869
// source below, it is accepted only after complete schema and cutpoint
// attestation inside the migration transaction.
constexpr std::array<SchemaDefinition, 9> kPreviousSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=2),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

// Rev0872 schema retained as an exact migration source. It added the
// digest-bound liveness fence but retained only a retry deadline, so migration
// must preserve that epistemic gap rather than inventing a release timestamp.
constexpr std::array<SchemaDefinition, 10> kClockSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=3),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "high_water_epoch_be BLOB NOT NULL CHECK(length(high_water_epoch_be)=8),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};


// Rev0873 schema retained as an exact migration source. It records the
// caller-provided high-water fence and exact retry-release provenance.
constexpr std::array<SchemaDefinition, 10> kRetryProvenanceSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=4),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "high_water_epoch_be BLOB NOT NULL CHECK(length(high_water_epoch_be)=8),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

// Rev0874 schema retained as an exact migration source. It owns the complete
// outbox-clock policy but predates explicit historical-version retention roots. The exact accepted/rejected host-clock
// observation is durable evidence, the policy is part of the cutpoint, and a
// quarantined row cannot silently mint lease or retry authority.
constexpr std::array<SchemaDefinition, 10> kRetentionRootSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=5),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "max_outbox_clock_uncertainty_ns_be BLOB NOT NULL CHECK(length(max_outbox_clock_uncertainty_ns_be)=8),"
     "max_outbox_clock_forward_step_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_forward_step_seconds_be)=8),"
     "max_outbox_clock_realtime_lag_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_realtime_lag_seconds_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "clock_state_bytes BLOB NOT NULL CHECK(length(clock_state_bytes) BETWEEN 1 AND 512),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};


// Rev0973 schema retained as an exact migration source. It adds explicit
// local retention roots over exact immutable File operations but predates a
// database-incarnation and recovery-epoch identity. Exact v6 restoration is
// required before migration can mint the new lineage.
constexpr std::array<SchemaDefinition, 11> kHistoricalPinSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=6),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "max_outbox_clock_uncertainty_ns_be BLOB NOT NULL CHECK(length(max_outbox_clock_uncertainty_ns_be)=8),"
     "max_outbox_clock_forward_step_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_forward_step_seconds_be)=8),"
     "max_outbox_clock_realtime_lag_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_realtime_lag_seconds_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "historical_version_pin_count_be BLOB NOT NULL CHECK(length(historical_version_pin_count_be)=8),"
     "historical_version_pin_set_digest TEXT NOT NULL CHECK(length(historical_version_pin_set_digest)=64),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_history_pins", "sync_replica_history_pins",
     "CREATE TABLE sync_replica_history_pins("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "clock_state_bytes BLOB NOT NULL CHECK(length(clock_state_bytes) BETWEEN 1 AND 512),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

// Current schema binds every cutpoint to one randomly minted database
// incarnation and a monotonic operator-controlled recovery epoch. The lineage
// distinguishes independent database files with otherwise identical contents;
// the epoch lets an explicit recovery invalidate stale same-incarnation
// evidence. Because both fields live inside SQLite, exact whole-image rollback
// still requires an external anchor or an explicit post-restore epoch advance.
constexpr std::array<SchemaDefinition, 11> kDatabaseLineageSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=7),"
     "database_incarnation_sha256 TEXT NOT NULL CHECK(length(database_incarnation_sha256)=64),"
     "database_recovery_epoch_be BLOB NOT NULL CHECK(length(database_recovery_epoch_be)=8),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "max_outbox_clock_uncertainty_ns_be BLOB NOT NULL CHECK(length(max_outbox_clock_uncertainty_ns_be)=8),"
     "max_outbox_clock_forward_step_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_forward_step_seconds_be)=8),"
     "max_outbox_clock_realtime_lag_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_realtime_lag_seconds_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "historical_version_pin_count_be BLOB NOT NULL CHECK(length(historical_version_pin_count_be)=8),"
     "historical_version_pin_set_digest TEXT NOT NULL CHECK(length(historical_version_pin_set_digest)=64),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_history_pins", "sync_replica_history_pins",
     "CREATE TABLE sync_replica_history_pins("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "clock_state_bytes BLOB NOT NULL CHECK(length(clock_state_bytes) BETWEEN 1 AND 512),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

// Rev0991 schema changes the three complete-projection digests into separately
// counted commutative 256-bit accumulators, chains the local actor operation
// authority incrementally, and adds one redundant exact canonical-path index.
// Complete restores still verify every row against the causal model. Ordinary
// local-file prepare and commit can therefore touch only the global causal-head
// frontier and the retained history for one path instead of decoding unrelated
// retained operations.
// Rev1019 schema retained as an exact migration source. The complete v8
// operation-path and visible-projection witnesses are restored before the
// normalized visible-content acceleration is rebuilt transactionally.
constexpr std::array<SchemaDefinition, 14> kVisiblePathSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=8),"
     "database_incarnation_sha256 TEXT NOT NULL CHECK(length(database_incarnation_sha256)=64),"
     "database_recovery_epoch_be BLOB NOT NULL CHECK(length(database_recovery_epoch_be)=8),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "max_outbox_clock_uncertainty_ns_be BLOB NOT NULL CHECK(length(max_outbox_clock_uncertainty_ns_be)=8),"
     "max_outbox_clock_forward_step_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_forward_step_seconds_be)=8),"
     "max_outbox_clock_realtime_lag_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_realtime_lag_seconds_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "visible_path_count_be BLOB NOT NULL CHECK(length(visible_path_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "historical_version_pin_count_be BLOB NOT NULL CHECK(length(historical_version_pin_count_be)=8),"
     "historical_version_pin_set_digest TEXT NOT NULL CHECK(length(historical_version_pin_set_digest)=64),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_operation_paths", "sync_replica_operation_paths",
     "CREATE TABLE sync_replica_operation_paths("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_history_pins", "sync_replica_history_pins",
     "CREATE TABLE sync_replica_history_pins("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "clock_state_bytes BLOB NOT NULL CHECK(length(clock_state_bytes) BETWEEN 1 AND 512),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_operation_paths_path", "sync_replica_operation_paths",
     "CREATE INDEX sync_replica_operation_paths_path ON sync_replica_operation_paths(canonical_path,operation_id)"},
    {"index", "sync_replica_parent_edges_parent", "sync_replica_parent_edges",
     "CREATE INDEX sync_replica_parent_edges_parent ON sync_replica_parent_edges(parent_operation_id,child_operation_id)"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

// Current schema adds a startup-attested normalized value projection to each
// visible row. The index is acceleration only: complete snapshots still
// decode every operation and verify every redundant value before authority
// is published. Bounded rename planning reads at most two matching rows.
constexpr std::array<SchemaDefinition, 15> kSchema{{
    {"table", "sync_replica_meta", "sync_replica_meta",
     "CREATE TABLE sync_replica_meta("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "schema_version INTEGER NOT NULL CHECK(schema_version=9),"
     "database_incarnation_sha256 TEXT NOT NULL CHECK(length(database_incarnation_sha256)=64),"
     "database_recovery_epoch_be BLOB NOT NULL CHECK(length(database_recovery_epoch_be)=8),"
     "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
     "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
     "local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),"
     "last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),"
     "state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),"
     "policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),"
     "max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),"
     "max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),"
     "max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),"
     "max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),"
     "max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),"
     "max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),"
     "max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),"
     "max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),"
     "max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),"
     "max_outbox_clock_uncertainty_ns_be BLOB NOT NULL CHECK(length(max_outbox_clock_uncertainty_ns_be)=8),"
     "max_outbox_clock_forward_step_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_forward_step_seconds_be)=8),"
     "max_outbox_clock_realtime_lag_seconds_be BLOB NOT NULL CHECK(length(max_outbox_clock_realtime_lag_seconds_be)=8),"
     "evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),"
     "active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),"
     "visible_path_count_be BLOB NOT NULL CHECK(length(visible_path_count_be)=8),"
     "retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),"
     "retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),"
     "retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),"
     "outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),"
     "outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),"
     "historical_version_pin_count_be BLOB NOT NULL CHECK(length(historical_version_pin_count_be)=8),"
     "historical_version_pin_set_digest TEXT NOT NULL CHECK(length(historical_version_pin_set_digest)=64),"
     "local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),"
     "local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),"
     "operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),"
     "evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),"
     "visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),"
     "outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),"
     "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT"},
    {"table", "sync_replica_operations", "sync_replica_operations",
     "CREATE TABLE sync_replica_operations("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_bytes BLOB NOT NULL,"
     "canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),"
     "context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),"
     "predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),"
     "evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT"},
    {"table", "sync_replica_operation_paths", "sync_replica_operation_paths",
     "CREATE TABLE sync_replica_operation_paths("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_history_pins", "sync_replica_history_pins",
     "CREATE TABLE sync_replica_history_pins("
     "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_parent_edges", "sync_replica_parent_edges",
     "CREATE TABLE sync_replica_parent_edges("
     "child_operation_id TEXT NOT NULL,"
     "parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),"
     "parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),"
     "PRIMARY KEY(child_operation_id,parent_ordinal),"
     "UNIQUE(child_operation_id,parent_operation_id),"
     "FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT"},
    {"table", "sync_replica_local_operations", "sync_replica_local_operations",
     "CREATE TABLE sync_replica_local_operations("
     "counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),"
     "operation_id TEXT NOT NULL UNIQUE,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_heads", "sync_replica_heads",
     "CREATE TABLE sync_replica_heads("
     "operation_id TEXT PRIMARY KEY,"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_visible", "sync_replica_visible",
     "CREATE TABLE sync_replica_visible("
     "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
     "visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),"
     "operation_id TEXT NOT NULL,"
     "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),"
     "preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),"
     "value_kind INTEGER NOT NULL CHECK(value_kind IN (1,2)),"
     "size_bytes_be BLOB NOT NULL CHECK(length(size_bytes_be)=8),"
     "content_sha256 TEXT NOT NULL,"
     "CHECK((value_kind=1 AND length(content_sha256)=64) OR "
     "(value_kind=2 AND content_sha256='' AND size_bytes_be=x'0000000000000000')),"
     "PRIMARY KEY(canonical_path,visible_ordinal),"
     "UNIQUE(canonical_path,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox", "sync_replica_outbox",
     "CREATE TABLE sync_replica_outbox("
     "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
     "operation_id TEXT NOT NULL,"
     "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
     "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
     "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
     "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
     "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
     "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
     "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
     "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
     "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
     "PRIMARY KEY(destination_device_id,operation_id),"
     "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT"},
    {"table", "sync_replica_outbox_clock", "sync_replica_outbox_clock",
     "CREATE TABLE sync_replica_outbox_clock("
     "id INTEGER PRIMARY KEY CHECK(id=1),"
     "clock_state_bytes BLOB NOT NULL CHECK(length(clock_state_bytes) BETWEEN 1 AND 512),"
     "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT"},
    {"index", "sync_replica_visible_file_content", "sync_replica_visible",
     "CREATE INDEX sync_replica_visible_file_content ON sync_replica_visible(value_kind,content_sha256,size_bytes_be,canonical_path,operation_id)"},
    {"index", "sync_replica_operation_paths_path", "sync_replica_operation_paths",
     "CREATE INDEX sync_replica_operation_paths_path ON sync_replica_operation_paths(canonical_path,operation_id)"},
    {"index", "sync_replica_parent_edges_parent", "sync_replica_parent_edges",
     "CREATE INDEX sync_replica_parent_edges_parent ON sync_replica_parent_edges(parent_operation_id,child_operation_id)"},
    {"index", "sync_replica_outbox_operation", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id)"},
    {"index", "sync_replica_outbox_schedule", "sync_replica_outbox",
     "CREATE INDEX sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id)"},
}};

struct DurableMeta final {
    std::uint64_t schema_version = kSchemaVersion;
    std::string database_incarnation_sha256;
    std::uint64_t database_recovery_epoch = 0U;
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t last_local_counter = 0;
    std::uint64_t state_generation = 0;
    std::uint64_t policy_generation = 0;
    SyncReplicaSqliteOwnerLimits limits;
    std::uint64_t evidence_count = 0;
    std::uint64_t active_count = 0;
    std::uint64_t visible_path_count = 0;
    std::uint64_t retained_canonical_bytes = 0;
    std::uint64_t retained_context_entries = 0;
    std::uint64_t retained_predecessor_ids = 0;
    std::uint64_t outbox_intent_count = 0;
    std::uint64_t outbox_destination_bytes = 0;
    std::uint64_t historical_version_pin_count = 0;
    std::string historical_version_pin_set_digest;
    bool local_actor_compromised = false;
    std::string local_operation_digest;
    std::string operation_set_digest;
    std::string evidence_set_digest;
    std::string visible_state_digest;
    std::string outbox_digest;
    std::string cutpoint_digest;

    bool operator==(const DurableMeta&) const = default;
};

struct DurableOutboxClock final {
    SyncReplicaOutboxClockState state;
    std::string state_bytes;
    std::string clock_digest;

    bool operator==(const DurableOutboxClock&) const = default;
};

struct LoadedState final {
    DurableMeta meta;
    DurableOutboxClock outbox_clock;
    SyncReplicaModel model;
    std::map<std::string, SyncReplicaEvidenceState> persisted_states;
    std::vector<SyncReplicaSqliteOutboxIntent> outbox;
    std::vector<std::string> historical_version_pins;
};

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if (std::cmp_greater(value, std::numeric_limits<std::uint64_t>::max())) {
        throw std::overflow_error(label + " does not fit uint64_t");
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::size_t u64_to_size_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (std::cmp_greater(value, std::numeric_limits<std::size_t>::max())) {
        throw std::overflow_error(label + " does not fit size_t");
    }
    return static_cast<std::size_t>(value);
}

[[nodiscard]] std::string u64_be(std::uint64_t value) {
    std::string out(8, '\0');
    for (std::size_t index = 0; index < 8; ++index) {
        out[7U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::uint64_t parse_u64_be_or_throw(
    std::string_view bytes,
    const std::string& label) {
    if (bytes.size() != 8U) {
        throw std::runtime_error(label + " is not an exact 8-byte uint64");
    }
    std::uint64_t value = 0;
    for (const unsigned char byte : bytes) {
        value = (value << 8U) | static_cast<std::uint64_t>(byte);
    }
    return value;
}

void bind_u64_be_or_throw(
    sqlite3_stmt* statement,
    int index,
    std::uint64_t value,
    const std::string& label) {
    sqlite_bind_blob_or_throw(statement, index, u64_be(value), label);
}

[[nodiscard]] std::uint64_t column_u64_be_or_throw(
    sqlite3_stmt* statement,
    int column,
    const std::string& label) {
    return parse_u64_be_or_throw(
        sqlite_column_blob_or_throw(statement, column, 8U, label), label);
}

[[nodiscard]] SyncReplicaOutboxRetryReleaseProvenance
retry_release_provenance_from_u64_or_throw(
    std::uint64_t value,
    const std::string& label) {
    switch (value) {
        case 0U:
            return SyncReplicaOutboxRetryReleaseProvenance::None;
        case 1U:
            return SyncReplicaOutboxRetryReleaseProvenance::Exact;
        case 2U:
            return SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven;
    }
    throw std::runtime_error(
        label + " retry release provenance is unsupported");
}

void require_row_or_throw(sqlite3_stmt* statement, const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW) {
        if (result == SQLITE_DONE) {
            throw std::runtime_error(label + " row is missing");
        }
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
}

void require_done_or_throw(sqlite3_stmt* statement, const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_DONE) {
        if (result == SQLITE_ROW) {
            throw std::runtime_error(label + " has more than one row");
        }
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
}

void reset_statement_or_throw(
    sqlite3_stmt* statement,
    const std::string& label) {
    const int reset_result = sqlite3_reset(statement);
    if (reset_result != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement), reset_result, label + " reset");
    }
    const int clear_result = sqlite3_clear_bindings(statement);
    if (clear_result != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement), clear_result,
            label + " clear bindings");
    }
}

[[nodiscard]] std::uint64_t increment_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " is exhausted");
    }
    return value + 1U;
}

[[nodiscard]] std::uint64_t checked_add_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(label + " overflows uint64_t");
    }
    return left + right;
}

void append_framed(
    Sha256DigestBuilder& digest,
    std::string_view bytes) {
    digest.update(u64_be(size_to_u64_or_throw(
        bytes.size(), "sync replica SQLite digest frame length")));
    digest.update(bytes);
}

[[nodiscard]] std::string mint_database_incarnation_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::string& label) {
    std::string entropy(32U, '\0');
    const int result = RAND_bytes(
        reinterpret_cast<unsigned char*>(entropy.data()),
        static_cast<int>(entropy.size()));
    if (result != 1) {
        throw std::runtime_error(
            label + " database-incarnation CSPRNG failed");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-database-incarnation-v1");
    append_framed(digest, folder_id);
    append_framed(digest, local_actor.device_id);
    digest.update(u64_be(local_actor.epoch));
    append_framed(digest, entropy);
    return digest.finish_hex();
}

[[nodiscard]] std::string legacy_outbox_digest_or_throw(
    const std::string& folder_id,
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v1");
    append_framed(digest, folder_id);
    digest.update(u64_be(size_to_u64_or_throw(
        outbox.size(), "sync replica SQLite legacy outbox count")));
    for (const SyncReplicaSqliteOutboxIntent& intent : outbox) {
        if (intent.lease != SyncReplicaOutboxLeaseState{}) {
            throw std::logic_error(
                "sync replica SQLite legacy outbox has lease metadata");
        }
        append_framed(digest, intent.destination_device_id);
        append_framed(digest, intent.operation_id);
        digest.update(u64_be(intent.enqueued_generation));
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string prior_outbox_digest_or_throw(
    const std::string& folder_id,
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v2");
    append_framed(digest, folder_id);
    digest.update(u64_be(size_to_u64_or_throw(
        outbox.size(), "sync replica SQLite outbox count")));
    for (const SyncReplicaSqliteOutboxIntent& intent : outbox) {
        validate_sync_replica_outbox_lease_state_or_throw(
            intent.lease, "sync replica SQLite outbox digest lease");
        append_framed(digest, intent.destination_device_id);
        append_framed(digest, intent.operation_id);
        digest.update(u64_be(intent.enqueued_generation));
        digest.update(u64_be(intent.lease.dispatch_attempts));
        append_framed(digest, intent.lease.claim_id);
        append_framed(digest, intent.lease.worker_id);
        digest.update(u64_be(intent.lease.claimed_at_epoch));
        digest.update(u64_be(intent.lease.lease_expires_at_epoch));
        digest.update(u64_be(intent.lease.retry_not_before_epoch));
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string outbox_digest_or_throw(
    const std::string& folder_id,
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v3");
    append_framed(digest, folder_id);
    digest.update(u64_be(size_to_u64_or_throw(
        outbox.size(), "sync replica SQLite outbox count")));
    for (const SyncReplicaSqliteOutboxIntent& intent : outbox) {
        validate_sync_replica_outbox_lease_state_or_throw(
            intent.lease, "sync replica SQLite outbox digest lease");
        append_framed(digest, intent.destination_device_id);
        append_framed(digest, intent.operation_id);
        digest.update(u64_be(intent.enqueued_generation));
        digest.update(u64_be(intent.lease.dispatch_attempts));
        append_framed(digest, intent.lease.claim_id);
        append_framed(digest, intent.lease.worker_id);
        digest.update(u64_be(intent.lease.claimed_at_epoch));
        digest.update(u64_be(intent.lease.lease_expires_at_epoch));
        digest.update(u64_be(intent.lease.retry_not_before_epoch));
        digest.update(u64_be(intent.lease.retry_released_at_epoch));
        digest.update(u64_be(static_cast<std::uint64_t>(
            intent.lease.retry_release_provenance)));
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string local_operation_digest_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::vector<std::string>& local_operation_ids) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-local-authority-v1");
    append_framed(digest, folder_id);
    append_framed(digest, local_actor.device_id);
    digest.update(u64_be(local_actor.epoch));
    digest.update(u64_be(size_to_u64_or_throw(
        local_operation_ids.size(),
        "sync replica SQLite local operation count")));
    for (const std::string& operation_id : local_operation_ids) {
        append_framed(digest, operation_id);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string local_operation_chain_seed_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-local-authority-chain-seed-v1");
    append_framed(digest, folder_id);
    append_framed(digest, local_actor.device_id);
    digest.update(u64_be(local_actor.epoch));
    return digest.finish_hex();
}

[[nodiscard]] std::string local_operation_chain_advance_or_throw(
    std::string_view prior_digest,
    std::uint64_t counter,
    std::string_view operation_id) {
    if (!is_lowercase_sha256_hex(prior_digest) || counter == 0U ||
        !is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            "sync replica SQLite local operation chain input is invalid");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-local-authority-chain-step-v1");
    append_framed(digest, prior_digest);
    digest.update(u64_be(counter));
    append_framed(digest, operation_id);
    return digest.finish_hex();
}

[[nodiscard]] std::string local_operation_chain_digest_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    std::span<const std::string> local_operation_ids) {
    std::string digest =
        local_operation_chain_seed_or_throw(folder_id, local_actor);
    std::uint64_t counter = 0U;
    for (const std::string& operation_id : local_operation_ids) {
        counter = increment_or_throw(
            counter, "sync replica SQLite local operation chain counter");
        digest = local_operation_chain_advance_or_throw(
            digest, counter, operation_id);
    }
    return digest;
}

[[nodiscard]] std::string historical_version_pin_set_digest_or_throw(
    const std::string& folder_id,
    std::span<const std::string> operation_ids,
    const std::string& label =
        "sync replica SQLite historical-version pin set") {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-historical-version-pin-set-v1");
    append_framed(digest, folder_id);
    digest.update(u64_be(size_to_u64_or_throw(
        operation_ids.size(), label + " count")));
    std::string_view previous;
    bool first = true;
    for (const std::string& operation_id : operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                label + " contains a noncanonical operation ID");
        }
        if (!first && previous >= operation_id) {
            throw std::invalid_argument(
                label + " is not strictly ordered and unique");
        }
        append_framed(digest, operation_id);
        previous = operation_id;
        first = false;
    }
    return digest.finish_hex();
}

void append_cutpoint_authority(
    Sha256DigestBuilder& digest,
    const DurableMeta& meta) {
    append_framed(digest, meta.folder_id);
    append_framed(digest, meta.local_actor.device_id);
    digest.update(u64_be(meta.local_actor.epoch));
    digest.update(u64_be(meta.last_local_counter));
    digest.update(u64_be(meta.state_generation));
    digest.update(u64_be(meta.policy_generation));
    digest.update(u64_be(meta.limits.model.max_operations));
    digest.update(u64_be(meta.limits.model.max_context_entries));
    digest.update(u64_be(meta.limits.model.max_predecessor_ids));
    digest.update(u64_be(meta.limits.model.max_canonical_operation_bytes));
    digest.update(u64_be(meta.limits.model.max_retained_canonical_bytes));
    digest.update(u64_be(meta.limits.model.max_retained_context_entries));
    digest.update(u64_be(meta.limits.model.max_retained_predecessor_ids));
    digest.update(u64_be(meta.limits.max_outbox_intents));
    digest.update(u64_be(meta.limits.max_outbox_destination_bytes));
    digest.update(u64_be(meta.evidence_count));
    digest.update(u64_be(meta.active_count));
    digest.update(u64_be(meta.retained_canonical_bytes));
    digest.update(u64_be(meta.retained_context_entries));
    digest.update(u64_be(meta.retained_predecessor_ids));
    digest.update(u64_be(meta.outbox_intent_count));
    digest.update(u64_be(meta.outbox_destination_bytes));
    digest.update(meta.local_actor_compromised ? std::string_view("1")
                                               : std::string_view("0"));
    append_framed(digest, meta.local_operation_digest);
    append_framed(digest, meta.operation_set_digest);
    append_framed(digest, meta.evidence_set_digest);
    append_framed(digest, meta.visible_state_digest);
    append_framed(digest, meta.outbox_digest);
}

[[nodiscard]] std::string legacy_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v1");
    append_cutpoint_authority(digest, meta);
    return digest.finish_hex();
}

[[nodiscard]] std::string versioned_cutpoint_digest_or_throw(
    const DurableMeta& meta,
    std::uint64_t expected_schema_version,
    std::string_view domain,
    const std::string& label) {
    if (meta.schema_version != expected_schema_version) {
        throw std::logic_error(label + " cutpoint has wrong schema version");
    }
    Sha256DigestBuilder digest;
    digest.update(domain);
    digest.update(u64_be(meta.schema_version));
    append_cutpoint_authority(digest, meta);
    return digest.finish_hex();
}

[[nodiscard]] std::string previous_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    return versioned_cutpoint_digest_or_throw(
        meta, kPreviousSchemaVersion,
        "anonsync-sync-replica-sqlite-cutpoint-v2",
        "sync replica SQLite v2");
}

[[nodiscard]] std::string clock_schema_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    return versioned_cutpoint_digest_or_throw(
        meta, kClockSchemaVersion,
        "anonsync-sync-replica-sqlite-cutpoint-v3",
        "sync replica SQLite v3");
}

[[nodiscard]] std::string retry_provenance_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    return versioned_cutpoint_digest_or_throw(
        meta, kRetryProvenanceSchemaVersion,
        "anonsync-sync-replica-sqlite-cutpoint-v4",
        "sync replica SQLite v4");
}

[[nodiscard]] std::string retention_root_schema_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kRetentionRootSchemaVersion) {
        throw std::logic_error(
            "sync replica SQLite v5 cutpoint has wrong schema version");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v5");
    digest.update(u64_be(meta.schema_version));
    append_cutpoint_authority(digest, meta);
    digest.update(u64_be(meta.limits.max_outbox_clock_uncertainty_ns));
    digest.update(u64_be(meta.limits.max_outbox_clock_forward_step_seconds));
    digest.update(u64_be(meta.limits.max_outbox_clock_realtime_lag_seconds));
    return digest.finish_hex();
}

[[nodiscard]] SyncReplicaOutboxClockPolicy outbox_clock_policy(
    const SyncReplicaSqliteOwnerLimits& limits) {
    return {limits.max_outbox_clock_uncertainty_ns,
            limits.max_outbox_clock_forward_step_seconds,
            limits.max_outbox_clock_realtime_lag_seconds};
}

[[nodiscard]] std::string historical_pin_schema_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kHistoricalPinSchemaVersion) {
        throw std::logic_error(
            "sync replica SQLite v6 cutpoint has wrong schema version");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v6");
    digest.update(u64_be(meta.schema_version));
    append_cutpoint_authority(digest, meta);
    digest.update(u64_be(meta.limits.max_outbox_clock_uncertainty_ns));
    digest.update(u64_be(meta.limits.max_outbox_clock_forward_step_seconds));
    digest.update(u64_be(meta.limits.max_outbox_clock_realtime_lag_seconds));
    digest.update(u64_be(meta.historical_version_pin_count));
    append_framed(digest, meta.historical_version_pin_set_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string database_lineage_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kDatabaseLineageSchemaVersion) {
        throw std::logic_error(
            "sync replica SQLite v7 cutpoint has wrong schema version");
    }
    if (!is_lowercase_sha256_hex(meta.database_incarnation_sha256) ||
        meta.database_recovery_epoch == 0U) {
        throw std::logic_error(
            "sync replica SQLite v7 cutpoint has invalid database lineage");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v7");
    digest.update(u64_be(meta.schema_version));
    append_framed(digest, meta.database_incarnation_sha256);
    digest.update(u64_be(meta.database_recovery_epoch));
    append_cutpoint_authority(digest, meta);
    digest.update(u64_be(meta.limits.max_outbox_clock_uncertainty_ns));
    digest.update(u64_be(meta.limits.max_outbox_clock_forward_step_seconds));
    digest.update(u64_be(meta.limits.max_outbox_clock_realtime_lag_seconds));
    digest.update(u64_be(meta.historical_version_pin_count));
    append_framed(digest, meta.historical_version_pin_set_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string visible_path_schema_cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kVisiblePathSchemaVersion) {
        throw std::logic_error(
            "sync replica SQLite v8 cutpoint has wrong schema version");
    }
    if (!is_lowercase_sha256_hex(meta.database_incarnation_sha256) ||
        meta.database_recovery_epoch == 0U) {
        throw std::logic_error(
            "sync replica SQLite v8 cutpoint has invalid database lineage");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v8");
    digest.update(u64_be(meta.schema_version));
    append_framed(digest, meta.database_incarnation_sha256);
    digest.update(u64_be(meta.database_recovery_epoch));
    append_cutpoint_authority(digest, meta);
    digest.update(u64_be(meta.visible_path_count));
    digest.update(u64_be(meta.limits.max_outbox_clock_uncertainty_ns));
    digest.update(u64_be(meta.limits.max_outbox_clock_forward_step_seconds));
    digest.update(u64_be(meta.limits.max_outbox_clock_realtime_lag_seconds));
    digest.update(u64_be(meta.historical_version_pin_count));
    append_framed(digest, meta.historical_version_pin_set_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kSchemaVersion) {
        throw std::logic_error(
            "sync replica SQLite v9 cutpoint has wrong schema version");
    }
    if (!is_lowercase_sha256_hex(meta.database_incarnation_sha256) ||
        meta.database_recovery_epoch == 0U) {
        throw std::logic_error(
            "sync replica SQLite v9 cutpoint has invalid database lineage");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v9");
    digest.update(u64_be(meta.schema_version));
    append_framed(digest, meta.database_incarnation_sha256);
    digest.update(u64_be(meta.database_recovery_epoch));
    append_cutpoint_authority(digest, meta);
    digest.update(u64_be(meta.visible_path_count));
    digest.update(u64_be(meta.limits.max_outbox_clock_uncertainty_ns));
    digest.update(u64_be(meta.limits.max_outbox_clock_forward_step_seconds));
    digest.update(u64_be(meta.limits.max_outbox_clock_realtime_lag_seconds));
    digest.update(u64_be(meta.historical_version_pin_count));
    append_framed(digest, meta.historical_version_pin_set_digest);
    return digest.finish_hex();
}

[[nodiscard]] std::string legacy_outbox_clock_digest_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    std::uint64_t high_water_epoch) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-outbox-clock-v1");
    append_framed(digest, folder_id);
    append_framed(digest, local_actor.device_id);
    digest.update(u64_be(local_actor.epoch));
    digest.update(u64_be(high_water_epoch));
    return digest.finish_hex();
}

[[nodiscard]] std::string outbox_clock_digest_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view state_bytes) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-outbox-clock-v2");
    append_framed(digest, folder_id);
    append_framed(digest, local_actor.device_id);
    digest.update(u64_be(local_actor.epoch));
    append_framed(digest, state_bytes);
    return digest.finish_hex();
}

[[nodiscard]] DurableOutboxClock make_outbox_clock_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    SyncReplicaOutboxClockState state,
    const std::string& label) {
    validate_sync_replica_outbox_clock_state_or_throw(state, label);
    std::string state_bytes =
        encode_sync_replica_outbox_clock_state_canonical_or_throw(state, label);
    return {std::move(state), state_bytes,
            outbox_clock_digest_or_throw(
                folder_id, local_actor, state_bytes)};
}

[[nodiscard]] SyncReplicaOutboxClockState migrated_clock_state_or_throw(
    std::uint64_t high_water_epoch,
    const std::string& label) {
    if (high_water_epoch == 0U) return {};
    return make_legacy_unbound_sync_replica_outbox_clock_state_or_throw(
        high_water_epoch, label);
}

[[nodiscard]] std::uint64_t outbox_destination_bytes_or_throw(
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox) {
    std::uint64_t total = 0;
    for (const SyncReplicaSqliteOutboxIntent& intent : outbox) {
        total = checked_add_or_throw(
            total,
            size_to_u64_or_throw(
                intent.destination_device_id.size(),
                "sync replica SQLite outbox destination bytes"),
            "sync replica SQLite outbox destination bytes");
    }
    return total;
}

[[nodiscard]] std::uint64_t visible_value_kind_integer_or_throw(
    SyncReplicaValueKind kind,
    std::string_view label) {
    switch (kind) {
        case SyncReplicaValueKind::File:
            return 1U;
        case SyncReplicaValueKind::Tombstone:
            return 2U;
    }
    throw std::invalid_argument(
        std::string(label) + " visible value kind is invalid");
}

[[nodiscard]] std::string_view evidence_state_text(
    SyncReplicaEvidenceState state) noexcept {
    switch (state) {
        case SyncReplicaEvidenceState::Active:
            return "active";
        case SyncReplicaEvidenceState::PendingMissingDependency:
            return "pending_missing_dependency";
        case SyncReplicaEvidenceState::QuarantinedDotFork:
            return "quarantined_dot_fork";
        case SyncReplicaEvidenceState::QuarantinedDependency:
            return "quarantined_dependency";
        case SyncReplicaEvidenceState::QuarantinedCausalEnvelope:
            return "quarantined_causal_envelope";
        case SyncReplicaEvidenceState::QuarantinedDependencyCycle:
            return "quarantined_dependency_cycle";
    }
    return "unknown";
}

[[nodiscard]] SyncReplicaEvidenceState parse_evidence_state_or_throw(
    std::string_view text,
    const std::string& label) {
    if (text == "active") return SyncReplicaEvidenceState::Active;
    if (text == "pending_missing_dependency") {
        return SyncReplicaEvidenceState::PendingMissingDependency;
    }
    if (text == "quarantined_dot_fork") {
        return SyncReplicaEvidenceState::QuarantinedDotFork;
    }
    if (text == "quarantined_dependency") {
        return SyncReplicaEvidenceState::QuarantinedDependency;
    }
    if (text == "quarantined_causal_envelope") {
        return SyncReplicaEvidenceState::QuarantinedCausalEnvelope;
    }
    if (text == "quarantined_dependency_cycle") {
        return SyncReplicaEvidenceState::QuarantinedDependencyCycle;
    }
    throw std::runtime_error(label + " has an unknown evidence state");
}

void validate_owner_limits_or_throw(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaSqliteOwnerLimits& limits,
    const std::string& label) {
    (void)SyncReplicaModel(folder_id, local_actor, limits.model);
    if (limits.max_outbox_intents == 0U ||
        limits.max_outbox_destination_bytes == 0U) {
        throw std::invalid_argument(
            label + " outbox limits must be positive");
    }
    validate_sync_replica_outbox_clock_policy_or_throw(
        outbox_clock_policy(limits), label + " outbox clock");
}

[[nodiscard]] std::string create_statement(
    const SchemaDefinition& definition) {
    constexpr std::string_view table_prefix = "CREATE TABLE ";
    constexpr std::string_view index_prefix = "CREATE INDEX ";
    std::string statement;
    if (definition.stored_sql.starts_with(table_prefix)) {
        statement = "CREATE TABLE main.";
        statement.append(definition.stored_sql.substr(table_prefix.size()));
    } else if (definition.stored_sql.starts_with(index_prefix)) {
        statement = "CREATE INDEX main.";
        statement.append(definition.stored_sql.substr(index_prefix.size()));
    } else {
        throw std::logic_error(
            "sync replica SQLite schema definition has an unknown CREATE form");
    }
    statement.push_back(';');
    return statement;
}

using SchemaObject =
    std::tuple<std::string, std::string, std::string, std::string>;

[[nodiscard]] std::vector<SchemaObject> read_schema_objects_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT type,name,tbl_name,sql FROM main.sqlite_schema "
        "WHERE (name GLOB 'sync_replica_*' OR "
        "tbl_name GLOB 'sync_replica_*') AND sql IS NOT NULL "
        "ORDER BY name;",
        label + " schema query prepare");
    std::vector<SchemaObject> observed;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " schema query");
        }
        if (observed.size() >= kSchema.size() + 1U) {
            throw std::runtime_error(
                label + " schema object count exceeds its exact contract");
        }
        observed.emplace_back(
            sqlite_column_text_or_throw(
                statement.stmt, 0, 32U, label + " schema type"),
            sqlite_column_text_or_throw(
                statement.stmt, 1, 256U, label + " schema name"),
            sqlite_column_text_or_throw(
                statement.stmt, 2, 256U, label + " schema table name"),
            sqlite_column_text_or_throw(
                statement.stmt, 3, kMaxSchemaSqlBytes,
                label + " schema SQL"));
    }
    return observed;
}

[[nodiscard]] bool schema_matches(
    const std::vector<SchemaObject>& observed,
    std::span<const SchemaDefinition> definitions) {
    if (observed.size() != definitions.size()) return false;
    std::map<std::string, const SchemaDefinition*> expected;
    for (const SchemaDefinition& definition : definitions) {
        expected.emplace(std::string(definition.name), &definition);
    }
    for (const auto& [type, name, table_name, sql] : observed) {
        const auto found = expected.find(name);
        if (found == expected.end()) return false;
        const SchemaDefinition& definition = *found->second;
        if (type != definition.type || table_name != definition.table_name ||
            sql != definition.stored_sql) {
            return false;
        }
        expected.erase(found);
    }
    return expected.empty();
}

void verify_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::span<const SchemaDefinition> definitions,
    const std::string& label) {
    const auto observed = read_schema_objects_or_throw(db, label);
    if (!schema_matches(observed, definitions)) {
        throw std::runtime_error(
            label + " exact sqlite_schema contract mismatch");
    }
}

void verify_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    verify_schema_or_throw(db, kSchema, label);
}

void require_foreign_keys_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, "PRAGMA foreign_keys;", label + " foreign_keys query prepare");
    require_row_or_throw(statement.stmt, label + " foreign_keys query");
    const std::uint64_t enabled = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " foreign_keys value");
    require_done_or_throw(statement.stmt, label + " foreign_keys query");
    if (enabled != 1U) {
        throw std::runtime_error(
            label + " requires SQLite foreign key enforcement");
    }
}

void require_no_foreign_key_violations_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, "PRAGMA main.foreign_key_check;",
        label + " foreign_key_check prepare");
    const int result = sqlite3_step(statement.stmt);
    if (result == SQLITE_ROW) {
        throw std::runtime_error(
            label + " found a durable foreign-key violation");
    }
    if (result != SQLITE_DONE) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), result,
            label + " foreign_key_check");
    }
}

[[nodiscard]] DurableMeta read_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::uint64_t expected_schema_version,
    const std::string& label) {
    const bool has_clock_policy =
        expected_schema_version == kRetentionRootSchemaVersion ||
        expected_schema_version == kHistoricalPinSchemaVersion ||
        expected_schema_version == kDatabaseLineageSchemaVersion ||
        expected_schema_version == kVisiblePathSchemaVersion ||
        expected_schema_version == kSchemaVersion;
    const bool has_historical_version_pins =
        expected_schema_version == kHistoricalPinSchemaVersion ||
        expected_schema_version == kDatabaseLineageSchemaVersion ||
        expected_schema_version == kVisiblePathSchemaVersion ||
        expected_schema_version == kSchemaVersion;
    const bool has_database_lineage =
        expected_schema_version == kDatabaseLineageSchemaVersion ||
        expected_schema_version == kVisiblePathSchemaVersion ||
        expected_schema_version == kSchemaVersion;
    const bool has_visible_path_count =
        expected_schema_version == kVisiblePathSchemaVersion ||
        expected_schema_version == kSchemaVersion;

    std::string query = "SELECT schema_version,";
    if (has_database_lineage) {
        query +=
            "database_incarnation_sha256,database_recovery_epoch_be,";
    }
    query +=
        "folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,state_generation_be,policy_generation_be,"
        "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,";
    if (has_clock_policy) {
        query +=
            "max_outbox_clock_uncertainty_ns_be,"
            "max_outbox_clock_forward_step_seconds_be,"
            "max_outbox_clock_realtime_lag_seconds_be,";
    }
    query += "evidence_count_be,active_count_be,";
    if (has_visible_path_count) {
        query += "visible_path_count_be,";
    }
    query +=
        "retained_canonical_bytes_be,retained_context_entries_be,"
        "retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,";
    if (has_historical_version_pins) {
        query +=
            "historical_version_pin_count_be,"
            "historical_version_pin_set_digest,";
    }
    query +=
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest "
        "FROM main.sync_replica_meta WHERE id=1 LIMIT 2;";

    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, query, label + " meta query prepare");
    require_row_or_throw(statement.stmt, label + " meta query");
    int index = 0;
    const std::uint64_t observed_schema_version = sqlite_column_u64_or_throw(
        statement.stmt, index++, label + " schema version");
    if (observed_schema_version != expected_schema_version ||
        (observed_schema_version != kLegacySchemaVersion &&
         observed_schema_version != kPreviousSchemaVersion &&
         observed_schema_version != kClockSchemaVersion &&
         observed_schema_version != kRetryProvenanceSchemaVersion &&
         observed_schema_version != kRetentionRootSchemaVersion &&
         observed_schema_version != kHistoricalPinSchemaVersion &&
         observed_schema_version != kDatabaseLineageSchemaVersion &&
         observed_schema_version != kVisiblePathSchemaVersion &&
         observed_schema_version != kSchemaVersion)) {
        throw std::runtime_error(label + " schema version is unsupported");
    }

    DurableMeta meta;
    meta.schema_version = observed_schema_version;
    if (has_database_lineage) {
        meta.database_incarnation_sha256 = sqlite_column_text_or_throw(
            statement.stmt, index++, 64U,
            label + " database incarnation digest");
        meta.database_recovery_epoch = column_u64_be_or_throw(
            statement.stmt, index++, label + " database recovery epoch");
    }
    meta.folder_id = sqlite_column_text_or_throw(
        statement.stmt, index++, kSyncManifestIdMaxBytes, label + " folder id");
    meta.local_actor.device_id = sqlite_column_text_or_throw(
        statement.stmt, index++, kSyncManifestIdMaxBytes,
        label + " local device id");
    meta.local_actor.epoch = column_u64_be_or_throw(
        statement.stmt, index++, label + " local epoch");
    meta.last_local_counter = column_u64_be_or_throw(
        statement.stmt, index++, label + " last local counter");
    meta.state_generation = column_u64_be_or_throw(
        statement.stmt, index++, label + " state generation");
    meta.policy_generation = column_u64_be_or_throw(
        statement.stmt, index++, label + " policy generation");
    meta.limits.model.max_operations = column_u64_be_or_throw(
        statement.stmt, index++, label + " max operations");
    meta.limits.model.max_context_entries = column_u64_be_or_throw(
        statement.stmt, index++, label + " max context entries");
    meta.limits.model.max_predecessor_ids = column_u64_be_or_throw(
        statement.stmt, index++, label + " max predecessor ids");
    meta.limits.model.max_canonical_operation_bytes = column_u64_be_or_throw(
        statement.stmt, index++, label + " max canonical operation bytes");
    meta.limits.model.max_retained_canonical_bytes = column_u64_be_or_throw(
        statement.stmt, index++, label + " max retained canonical bytes");
    meta.limits.model.max_retained_context_entries = column_u64_be_or_throw(
        statement.stmt, index++, label + " max retained context entries");
    meta.limits.model.max_retained_predecessor_ids = column_u64_be_or_throw(
        statement.stmt, index++, label + " max retained predecessor ids");
    meta.limits.max_outbox_intents = column_u64_be_or_throw(
        statement.stmt, index++, label + " max outbox intents");
    meta.limits.max_outbox_destination_bytes = column_u64_be_or_throw(
        statement.stmt, index++, label + " max outbox destination bytes");
    if (has_clock_policy) {
        meta.limits.max_outbox_clock_uncertainty_ns = column_u64_be_or_throw(
            statement.stmt, index++, label + " max outbox clock uncertainty");
        meta.limits.max_outbox_clock_forward_step_seconds =
            column_u64_be_or_throw(
                statement.stmt, index++,
                label + " max outbox clock forward step");
        meta.limits.max_outbox_clock_realtime_lag_seconds =
            column_u64_be_or_throw(
                statement.stmt, index++,
                label + " max outbox clock realtime lag");
    }
    meta.evidence_count = column_u64_be_or_throw(
        statement.stmt, index++, label + " evidence count");
    meta.active_count = column_u64_be_or_throw(
        statement.stmt, index++, label + " active count");
    if (has_visible_path_count) {
        meta.visible_path_count = column_u64_be_or_throw(
            statement.stmt, index++, label + " visible path count");
    }
    meta.retained_canonical_bytes = column_u64_be_or_throw(
        statement.stmt, index++, label + " retained canonical bytes");
    meta.retained_context_entries = column_u64_be_or_throw(
        statement.stmt, index++, label + " retained context entries");
    meta.retained_predecessor_ids = column_u64_be_or_throw(
        statement.stmt, index++, label + " retained predecessor ids");
    meta.outbox_intent_count = column_u64_be_or_throw(
        statement.stmt, index++, label + " outbox intent count");
    meta.outbox_destination_bytes = column_u64_be_or_throw(
        statement.stmt, index++, label + " outbox destination bytes");
    if (has_historical_version_pins) {
        meta.historical_version_pin_count = column_u64_be_or_throw(
            statement.stmt, index++, label + " historical-version pin count");
        meta.historical_version_pin_set_digest = sqlite_column_text_or_throw(
            statement.stmt, index++, 64U,
            label + " historical-version pin-set digest");
    }
    meta.local_actor_compromised = sqlite_column_bool_or_throw(
        statement.stmt, index++, label + " local actor compromised");
    meta.local_operation_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " local operation digest");
    meta.operation_set_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " operation digest");
    meta.evidence_set_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " evidence digest");
    meta.visible_state_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " visible digest");
    meta.outbox_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " outbox digest");
    meta.cutpoint_digest = sqlite_column_text_or_throw(
        statement.stmt, index++, 64U, label + " cutpoint digest");
    require_done_or_throw(statement.stmt, label + " meta query");

    if (meta.state_generation == 0U || meta.policy_generation == 0U) {
        throw std::runtime_error(label + " durable generation is zero");
    }
    if (has_database_lineage &&
        (!is_lowercase_sha256_hex(meta.database_incarnation_sha256) ||
         meta.database_recovery_epoch == 0U)) {
        throw std::runtime_error(
            label + " durable database lineage is noncanonical");
    }
    if (!is_lowercase_sha256_hex(meta.local_operation_digest) ||
        !is_lowercase_sha256_hex(meta.operation_set_digest) ||
        !is_lowercase_sha256_hex(meta.evidence_set_digest) ||
        !is_lowercase_sha256_hex(meta.visible_state_digest) ||
        !is_lowercase_sha256_hex(meta.outbox_digest) ||
        (has_historical_version_pins &&
         !is_lowercase_sha256_hex(
             meta.historical_version_pin_set_digest)) ||
        !is_lowercase_sha256_hex(meta.cutpoint_digest)) {
        throw std::runtime_error(label + " durable digest is noncanonical");
    }
    validate_owner_limits_or_throw(
        meta.folder_id, meta.local_actor, meta.limits, label + " policy");
    std::string expected_cutpoint;
    if (meta.schema_version == kLegacySchemaVersion) {
        expected_cutpoint = legacy_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kPreviousSchemaVersion) {
        expected_cutpoint = previous_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kClockSchemaVersion) {
        expected_cutpoint = clock_schema_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kRetryProvenanceSchemaVersion) {
        expected_cutpoint = retry_provenance_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kRetentionRootSchemaVersion) {
        expected_cutpoint = retention_root_schema_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kHistoricalPinSchemaVersion) {
        expected_cutpoint = historical_pin_schema_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kDatabaseLineageSchemaVersion) {
        expected_cutpoint = database_lineage_cutpoint_digest_or_throw(meta);
    } else if (meta.schema_version == kVisiblePathSchemaVersion) {
        expected_cutpoint = visible_path_schema_cutpoint_digest_or_throw(meta);
    } else {
        expected_cutpoint = cutpoint_digest_or_throw(meta);
    }
    if (expected_cutpoint != meta.cutpoint_digest) {
        throw std::runtime_error(
            label + " durable cutpoint digest mismatch: expected " +
            expected_cutpoint + ", observed " + meta.cutpoint_digest);
    }
    return meta;
}

[[nodiscard]] DurableMeta read_current_owner_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    verify_schema_or_throw(db, label + " schema");
    require_foreign_keys_or_throw(db, label);
    DurableMeta meta = read_meta_or_throw(db, kSchemaVersion, label);
    if (meta.folder_id != expected_folder_id ||
        meta.local_actor != expected_local_actor) {
        throw std::runtime_error(label + " owner identity mismatch");
    }
    return meta;
}

void bind_meta_common_or_throw(
    sqlite3_stmt* statement,
    int first_index,
    const DurableMeta& meta,
    const std::string& label) {
    int index = first_index;
    sqlite_bind_text_or_throw(
        statement, index++, meta.database_incarnation_sha256,
        label + " bind database incarnation");
    bind_u64_be_or_throw(
        statement, index++, meta.database_recovery_epoch,
        label + " bind database recovery epoch");
    sqlite_bind_text_or_throw(
        statement, index++, meta.folder_id, label + " bind folder");
    sqlite_bind_text_or_throw(
        statement, index++, meta.local_actor.device_id,
        label + " bind local device");
    bind_u64_be_or_throw(
        statement, index++, meta.local_actor.epoch,
        label + " bind local epoch");
    bind_u64_be_or_throw(
        statement, index++, meta.last_local_counter,
        label + " bind local counter");
    bind_u64_be_or_throw(
        statement, index++, meta.state_generation,
        label + " bind state generation");
    bind_u64_be_or_throw(
        statement, index++, meta.policy_generation,
        label + " bind policy generation");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_operations,
        label + " bind max operations");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_context_entries,
        label + " bind max context entries");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_predecessor_ids,
        label + " bind max predecessor ids");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_canonical_operation_bytes,
        label + " bind max canonical bytes");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_retained_canonical_bytes,
        label + " bind max retained canonical bytes");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_retained_context_entries,
        label + " bind max retained context entries");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.model.max_retained_predecessor_ids,
        label + " bind max retained predecessor ids");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.max_outbox_intents,
        label + " bind max outbox intents");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.max_outbox_destination_bytes,
        label + " bind max outbox destination bytes");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.max_outbox_clock_uncertainty_ns,
        label + " bind max outbox clock uncertainty");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.max_outbox_clock_forward_step_seconds,
        label + " bind max outbox clock forward step");
    bind_u64_be_or_throw(
        statement, index++, meta.limits.max_outbox_clock_realtime_lag_seconds,
        label + " bind max outbox clock realtime lag");
    bind_u64_be_or_throw(
        statement, index++, meta.evidence_count,
        label + " bind evidence count");
    bind_u64_be_or_throw(
        statement, index++, meta.active_count,
        label + " bind active count");
    bind_u64_be_or_throw(
        statement, index++, meta.visible_path_count,
        label + " bind visible path count");
    bind_u64_be_or_throw(
        statement, index++, meta.retained_canonical_bytes,
        label + " bind retained canonical bytes");
    bind_u64_be_or_throw(
        statement, index++, meta.retained_context_entries,
        label + " bind retained context entries");
    bind_u64_be_or_throw(
        statement, index++, meta.retained_predecessor_ids,
        label + " bind retained predecessor ids");
    bind_u64_be_or_throw(
        statement, index++, meta.outbox_intent_count,
        label + " bind outbox count");
    bind_u64_be_or_throw(
        statement, index++, meta.outbox_destination_bytes,
        label + " bind outbox destination bytes");
    bind_u64_be_or_throw(
        statement, index++, meta.historical_version_pin_count,
        label + " bind historical-version pin count");
    sqlite_bind_text_or_throw(
        statement, index++, meta.historical_version_pin_set_digest,
        label + " bind historical-version pin-set digest");
    sqlite_bind_bool_or_throw(
        statement, index++, meta.local_actor_compromised,
        label + " bind actor compromised");
    sqlite_bind_text_or_throw(
        statement, index++, meta.local_operation_digest,
        label + " bind local operation digest");
    sqlite_bind_text_or_throw(
        statement, index++, meta.operation_set_digest,
        label + " bind operation digest");
    sqlite_bind_text_or_throw(
        statement, index++, meta.evidence_set_digest,
        label + " bind evidence digest");
    sqlite_bind_text_or_throw(
        statement, index++, meta.visible_state_digest,
        label + " bind visible digest");
    sqlite_bind_text_or_throw(
        statement, index++, meta.outbox_digest,
        label + " bind outbox digest");
    sqlite_bind_text_or_throw(
        statement, index++, meta.cutpoint_digest,
        label + " bind cutpoint digest");
}

void insert_meta_row_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_meta("
        "id,schema_version,database_incarnation_sha256,"
        "database_recovery_epoch_be,folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,state_generation_be,policy_generation_be,"
        "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,"
        "max_outbox_clock_uncertainty_ns_be,"
        "max_outbox_clock_forward_step_seconds_be,"
        "max_outbox_clock_realtime_lag_seconds_be,"
        "evidence_count_be,active_count_be,visible_path_count_be,"
        "retained_canonical_bytes_be,retained_context_entries_be,"
        "retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,"
        "historical_version_pin_count_be,historical_version_pin_set_digest,"
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest)"
        "VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
        label + " meta insert prepare");
    sqlite_bind_u64_or_throw(
        statement.stmt, 1, meta.schema_version,
        label + " bind schema version");
    bind_meta_common_or_throw(statement.stmt, 2, meta, label + " meta insert");
    sqlite_step_done_or_throw(statement.stmt, label + " meta insert");
}

[[nodiscard]] DurableMeta insert_initial_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaSqliteOwnerLimits& limits,
    const std::string& label) {
    SyncReplicaModel empty(folder_id, local_actor, limits.model);
    DurableMeta meta;
    meta.database_incarnation_sha256 = mint_database_incarnation_or_throw(
        folder_id, local_actor, label + " initial");
    meta.database_recovery_epoch = 1U;
    meta.folder_id = folder_id;
    meta.local_actor = local_actor;
    meta.state_generation = 1U;
    meta.policy_generation = 1U;
    meta.limits = limits;
    meta.local_operation_digest = local_operation_chain_digest_or_throw(
        folder_id, local_actor, empty.local_operation_ids());
    meta.operation_set_digest = empty.operation_set_accumulator_digest();
    meta.evidence_set_digest = empty.evidence_set_accumulator_digest();
    meta.visible_path_count = empty.visible_path_count();
    meta.visible_state_digest = empty.visible_state_accumulator_digest();
    meta.outbox_digest = outbox_digest_or_throw(folder_id, {});
    meta.historical_version_pin_set_digest =
        historical_version_pin_set_digest_or_throw(folder_id, {});
    meta.cutpoint_digest = cutpoint_digest_or_throw(meta);

    insert_meta_row_or_throw(db, meta, label + " initial");
    return meta;
}

[[nodiscard]] DurableOutboxClock read_current_outbox_clock_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT clock_state_bytes,clock_digest "
        "FROM main.sync_replica_outbox_clock WHERE id=1 LIMIT 2;",
        label + " outbox clock query prepare");
    require_row_or_throw(statement.stmt, label + " outbox clock query");
    DurableOutboxClock clock;
    clock.state_bytes = sqlite_column_blob_or_throw(
        statement.stmt, 0, kSyncReplicaOutboxClockStateMaxCanonicalBytes,
        label + " outbox clock state");
    clock.clock_digest = sqlite_column_text_or_throw(
        statement.stmt, 1, 64U, label + " outbox clock digest");
    require_done_or_throw(statement.stmt, label + " outbox clock query");
    clock.state = decode_sync_replica_outbox_clock_state_canonical_or_throw(
        clock.state_bytes, label + " outbox clock state");
    if (encode_sync_replica_outbox_clock_state_canonical_or_throw(
            clock.state, label + " outbox clock canonical round trip") !=
        clock.state_bytes) {
        throw std::runtime_error(
            label + " outbox clock state is not canonical");
    }
    if (!is_lowercase_sha256_hex(clock.clock_digest) ||
        clock.clock_digest != outbox_clock_digest_or_throw(
                                  folder_id, local_actor, clock.state_bytes)) {
        throw std::runtime_error(label + " outbox clock attestation mismatch");
    }
    return clock;
}

[[nodiscard]] DurableOutboxClock read_legacy_outbox_clock_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT high_water_epoch_be,clock_digest "
        "FROM main.sync_replica_outbox_clock WHERE id=1 LIMIT 2;",
        label + " legacy outbox clock query prepare");
    require_row_or_throw(statement.stmt, label + " legacy outbox clock query");
    const std::uint64_t high_water_epoch = column_u64_be_or_throw(
        statement.stmt, 0, label + " legacy outbox time high water");
    const std::string legacy_digest = sqlite_column_text_or_throw(
        statement.stmt, 1, 64U, label + " legacy outbox clock digest");
    require_done_or_throw(statement.stmt, label + " legacy outbox clock query");
    if (!is_lowercase_sha256_hex(legacy_digest) ||
        legacy_digest != legacy_outbox_clock_digest_or_throw(
                             meta.folder_id, meta.local_actor,
                             high_water_epoch)) {
        throw std::runtime_error(
            label + " legacy outbox clock attestation mismatch");
    }
    return make_outbox_clock_or_throw(
        meta.folder_id, meta.local_actor,
        migrated_clock_state_or_throw(
            high_water_epoch, label + " legacy outbox clock migration"),
        label + " migrated legacy outbox clock");
}

void insert_outbox_clock_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableOutboxClock& clock,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_outbox_clock("
        "id,clock_state_bytes,clock_digest) VALUES(1,?,?);",
        label + " outbox clock insert prepare");
    sqlite_bind_blob_or_throw(
        statement.stmt, 1, clock.state_bytes,
        label + " bind outbox clock state");
    sqlite_bind_text_or_throw(
        statement.stmt, 2, clock.clock_digest,
        label + " bind outbox clock digest");
    sqlite_step_done_or_throw(statement.stmt, label + " outbox clock insert");
}

void update_outbox_clock_exact_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableOutboxClock& next,
    const DurableOutboxClock& previous,
    const std::string& label) {
    if (next == previous) return;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_outbox_clock SET "
        "clock_state_bytes=?,clock_digest=? "
        "WHERE id=1 AND clock_state_bytes=? AND clock_digest=?;",
        label + " outbox clock update prepare");
    sqlite_bind_blob_or_throw(
        statement.stmt, 1, next.state_bytes,
        label + " bind next outbox clock state");
    sqlite_bind_text_or_throw(
        statement.stmt, 2, next.clock_digest,
        label + " bind next outbox clock digest");
    sqlite_bind_blob_or_throw(
        statement.stmt, 3, previous.state_bytes,
        label + " bind previous outbox clock state");
    sqlite_bind_text_or_throw(
        statement.stmt, 4, previous.clock_digest,
        label + " bind previous outbox clock digest");
    sqlite_step_done_or_throw(statement.stmt, label + " outbox clock update");
    auto borrow = db.borrow();
    if (sqlite3_changes(borrow.get()) != 1) {
        throw std::runtime_error(
            label + " outbox clock update lost exact durable authority");
    }
}

[[nodiscard]] std::uint64_t count_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, sql, label + " prepare");
    require_row_or_throw(statement.stmt, label);
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " count");
    require_done_or_throw(statement.stmt, label);
    return count;
}

[[nodiscard]] std::vector<std::string> read_local_operation_ids_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_local_operations;",
        label + " local operation count");
    if (row_count != meta.last_local_counter ||
        row_count > meta.limits.model.max_operations) {
        throw std::runtime_error(
            label + " local operation count disagrees with authority");
    }
    std::vector<std::string> ids;
    ids.reserve(u64_to_size_or_throw(row_count, label + " local operation count"));
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT counter_be,operation_id "
        "FROM main.sync_replica_local_operations ORDER BY counter_be;",
        label + " local operation query prepare");
    std::uint64_t expected_counter = 1U;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " local operation query");
        }
        const std::uint64_t counter = column_u64_be_or_throw(
            statement.stmt, 0, label + " local operation counter");
        if (counter != expected_counter) {
            throw std::runtime_error(
                label + " local operation sequence has a gap or reordering");
        }
        ids.push_back(sqlite_column_text_or_throw(
            statement.stmt, 1, 64U, label + " local operation id"));
        ++expected_counter;
    }
    return ids;
}

struct StoredOperationRow final {
    SyncReplicaOperation operation;
    SyncReplicaEvidenceState evidence_state =
        SyncReplicaEvidenceState::PendingMissingDependency;
};

[[nodiscard]] StoredOperationRow load_stored_operation_row_or_throw(
    sqlite3_stmt* statement,
    int first_column,
    const SyncReplicaModelLimits& limits,
    const std::string& label) {
    int column = first_column;
    const std::string operation_id = sqlite_column_text_or_throw(
        statement, column++, 64U, label + " operation id");
    const std::string canonical = sqlite_column_blob_or_throw(
        statement, column++, limits.max_canonical_operation_bytes,
        label + " canonical operation");
    const std::uint64_t canonical_size = column_u64_be_or_throw(
        statement, column++, label + " canonical operation size");
    const std::uint64_t context_count = column_u64_be_or_throw(
        statement, column++, label + " context count");
    const std::uint64_t predecessor_count = column_u64_be_or_throw(
        statement, column++, label + " predecessor count");
    const SyncReplicaEvidenceState evidence_state =
        parse_evidence_state_or_throw(
            sqlite_column_text_or_throw(
                statement, column++, 64U, label + " evidence state"),
            label);
    SyncReplicaOperation operation =
        decode_sync_replica_operation_canonical_or_throw(canonical, limits);
    if (operation.operation_id != operation_id ||
        canonical_size != size_to_u64_or_throw(
            canonical.size(), label + " canonical size") ||
        context_count != size_to_u64_or_throw(
            operation.causal_context.size(), label + " context count") ||
        predecessor_count != size_to_u64_or_throw(
            operation.predecessor_operation_ids.size(),
            label + " predecessor count")) {
        throw std::runtime_error(
            label + " canonical operation row attestation mismatch");
    }
    return {std::move(operation), evidence_state};
}

[[nodiscard]] std::optional<StoredOperationRow>
read_exact_operation_row_or_none_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& operation_id,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(label + " operation identity is invalid");
    }
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id,canonical_bytes,canonical_size_be,"
        "context_count_be,predecessor_count_be,evidence_state "
        "FROM main.sync_replica_operations WHERE operation_id=?;",
        label + " exact operation prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, operation_id,
        label + " exact operation bind");
    const int result = sqlite3_step(statement.stmt);
    if (result == SQLITE_DONE) return std::nullopt;
    if (result != SQLITE_ROW) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), result,
            label + " exact operation query");
    }
    StoredOperationRow row = load_stored_operation_row_or_throw(
        statement.stmt, 0, meta.limits.model,
        label + " exact operation");
    if (row.operation.operation_id != operation_id) {
        throw std::runtime_error(
            label + " exact operation query returned a different identity");
    }
    require_done_or_throw(
        statement.stmt, label + " exact operation query");
    return row;
}

[[nodiscard]] std::pair<
    std::vector<SyncReplicaOperation>,
    std::map<std::string, SyncReplicaEvidenceState>>
read_operations_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_operations;",
        label + " operation count");
    if (row_count != meta.evidence_count ||
        row_count > meta.limits.model.max_operations) {
        throw std::runtime_error(
            label + " operation row count disagrees with durable metadata");
    }

    std::vector<SyncReplicaOperation> operations;
    operations.reserve(u64_to_size_or_throw(row_count, label + " operation count"));
    std::map<std::string, SyncReplicaEvidenceState> states;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id,canonical_bytes,canonical_size_be,"
        "context_count_be,predecessor_count_be,evidence_state "
        "FROM main.sync_replica_operations ORDER BY operation_id;",
        label + " operation query prepare");
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " operation query");
        }
        StoredOperationRow row = load_stored_operation_row_or_throw(
            statement.stmt, 0, meta.limits.model, label);
        const std::string operation_id = row.operation.operation_id;
        if (!states.emplace(operation_id, row.evidence_state).second) {
            throw std::runtime_error(label + " duplicate operation row");
        }
        operations.push_back(std::move(row.operation));
    }
    return {std::move(operations), std::move(states)};
}

struct TargetedVisiblePathState final {
    std::vector<std::string> visible_operation_ids;
    std::optional<SyncReplicaOperation> sole_visible_operation;
    bool conflicted = false;
};

[[nodiscard]] TargetedVisiblePathState read_targeted_visible_path_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& canonical_path,
    const std::string& label) {
    struct Row final {
        std::uint64_t ordinal = 0U;
        std::string operation_id;
        bool is_primary = false;
        bool preserve_file = false;
    };
    std::array<Row, 2U> rows;
    std::size_t count = 0U;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT visible_ordinal,operation_id,is_primary,preserve_file "
        "FROM main.sync_replica_visible WHERE canonical_path=? "
        "ORDER BY visible_ordinal LIMIT 2;",
        label + " visible path prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, canonical_path, label + " visible path bind");
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " visible path query");
        }
        if (count >= rows.size()) {
            throw std::logic_error(label + " visible path exceeded SQL limit");
        }
        Row& row = rows[count];
        row.ordinal = sqlite_column_u64_or_throw(
            statement.stmt, 0, label + " visible ordinal");
        row.operation_id = sqlite_column_text_or_throw(
            statement.stmt, 1, 64U, label + " visible operation identity");
        row.is_primary = sqlite_column_bool_or_throw(
            statement.stmt, 2, label + " visible primary flag");
        row.preserve_file = sqlite_column_bool_or_throw(
            statement.stmt, 3, label + " visible preservation flag");
        if (row.ordinal != count ||
            !is_lowercase_sha256_hex(row.operation_id) ||
            (count != 0U && row.operation_id == rows[0].operation_id)) {
            throw std::runtime_error(
                label + " visible path row is noncanonical");
        }
        ++count;
    }

    TargetedVisiblePathState state;
    state.visible_operation_ids.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        state.visible_operation_ids.push_back(rows[index].operation_id);
    }
    state.conflicted = count > 1U;
    if (count == 1U) {
        const Row& row = rows[0];
        if (!row.is_primary || row.preserve_file) {
            throw std::runtime_error(
                label + " sole-visible projection is malformed");
        }
        std::optional<StoredOperationRow> stored =
            read_exact_operation_row_or_none_or_throw(
                db, meta, row.operation_id,
                label + " sole-visible operation");
        if (!stored.has_value() ||
            stored->evidence_state != SyncReplicaEvidenceState::Active ||
            stored->operation.folder_id != meta.folder_id ||
            stored->operation.canonical_path != canonical_path) {
            throw std::runtime_error(
                label + " sole-visible projection disagrees with active evidence");
        }
        state.sole_visible_operation = std::move(stored->operation);
    }
    return state;
}

[[nodiscard]] SyncReplicaSqliteVisibleFileContentCutpoint
read_visible_file_content_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    std::uint64_t size_bytes,
    const std::string& content_sha256,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            label + " visible content digest is invalid");
    }

    SyncReplicaSqliteVisibleFileContentCutpoint cutpoint;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,visible_ordinal,operation_id,is_primary,"
        "preserve_file,value_kind,size_bytes_be,content_sha256 "
        "FROM main.sync_replica_visible "
        "INDEXED BY sync_replica_visible_file_content "
        "WHERE value_kind=1 AND content_sha256=? AND size_bytes_be=? "
        "ORDER BY canonical_path,visible_ordinal LIMIT 2;",
        label + " visible content lookup prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, content_sha256,
        label + " visible content digest bind");
    bind_u64_be_or_throw(
        statement.stmt, 2, size_bytes,
        label + " visible content size bind");

    std::array<SyncReplicaOperation, 2U> matches;
    std::size_t match_count = 0U;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " visible content lookup");
        }
        if (match_count >= matches.size()) {
            throw std::logic_error(
                label + " visible content lookup exceeded SQL limit");
        }
        const std::string canonical_path = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestRelativePathMaxBytes,
            label + " visible content path");
        (void)sqlite_column_u64_or_throw(
            statement.stmt, 1, label + " visible content ordinal");
        const std::string operation_id = sqlite_column_text_or_throw(
            statement.stmt, 2, 64U,
            label + " visible content operation identity");
        const bool is_primary = sqlite_column_bool_or_throw(
            statement.stmt, 3, label + " visible content primary flag");
        const bool preserve_file = sqlite_column_bool_or_throw(
            statement.stmt, 4,
            label + " visible content preservation flag");
        const std::uint64_t value_kind = sqlite_column_u64_or_throw(
            statement.stmt, 5, label + " visible content value kind");
        const std::uint64_t indexed_size = column_u64_be_or_throw(
            statement.stmt, 6, label + " visible content indexed size");
        const std::string indexed_content = sqlite_column_text_or_throw(
            statement.stmt, 7, 64U,
            label + " visible content indexed digest");
        if (!is_lowercase_sha256_hex(operation_id) ||
            value_kind != 1U || indexed_size != size_bytes ||
            indexed_content != content_sha256 ||
            preserve_file != !is_primary) {
            throw std::runtime_error(
                label + " visible content projection is noncanonical");
        }
        std::optional<StoredOperationRow> stored =
            read_exact_operation_row_or_none_or_throw(
                db, meta, operation_id,
                label + " visible content operation");
        if (!stored.has_value() ||
            stored->evidence_state != SyncReplicaEvidenceState::Active ||
            stored->operation.folder_id != meta.folder_id ||
            stored->operation.canonical_path != canonical_path ||
            stored->operation.operation_id != operation_id ||
            stored->operation.kind != SyncReplicaValueKind::File ||
            stored->operation.size_bytes != size_bytes ||
            stored->operation.content_sha256 != content_sha256) {
            throw std::runtime_error(
                label +
                " visible content projection disagrees with active evidence");
        }
        matches[match_count++] = std::move(stored->operation);
    }
    if (match_count == 1U) {
        cutpoint.sole_visible_file_operation = std::move(matches[0]);
    } else if (match_count > 1U) {
        cutpoint.ambiguous = true;
    }
    return cutpoint;
}

void verify_streamed_visible_projection_witness_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    if (meta.schema_version != kSchemaVersion ||
        !is_lowercase_sha256_hex(meta.visible_state_digest)) {
        throw std::invalid_argument(
            label + " visible projection witness metadata is invalid");
    }

    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,visible_ordinal,operation_id,is_primary,"
        "preserve_file,value_kind,size_bytes_be,content_sha256 "
        "FROM main.sync_replica_visible "
        "ORDER BY canonical_path,visible_ordinal;",
        label + " visible projection witness prepare");

    std::string accumulator = sync_replica_digest_accumulator_zero();
    std::uint64_t path_count = 0U;
    SyncReplicaPathView current;
    bool have_path = false;
    std::string previous_operation_id;
    std::uint64_t primary_count = 0U;

    const auto finish_path_or_throw = [&]() {
        if (!have_path) return;
        if (primary_count != 1U) {
            throw std::runtime_error(
                label + " visible projection path has no exact primary");
        }
        accumulator = sync_replica_digest_accumulator_add_or_throw(
            accumulator,
            sync_replica_visible_path_accumulator_element_digest_or_throw(
                current));
        path_count = increment_or_throw(
            path_count, label + " visible path count");
        current = {};
        previous_operation_id.clear();
        primary_count = 0U;
        have_path = false;
    };

    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " visible projection witness query");
        }
        const std::string canonical_path = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestRelativePathMaxBytes,
            label + " visible projection path");
        const std::uint64_t ordinal = sqlite_column_u64_or_throw(
            statement.stmt, 1, label + " visible projection ordinal");
        const std::string operation_id = sqlite_column_text_or_throw(
            statement.stmt, 2, 64U,
            label + " visible projection operation identity");
        const bool is_primary = sqlite_column_bool_or_throw(
            statement.stmt, 3, label + " visible projection primary flag");
        const bool preserve_file = sqlite_column_bool_or_throw(
            statement.stmt, 4,
            label + " visible projection preservation flag");
        const std::uint64_t encoded_kind = sqlite_column_u64_or_throw(
            statement.stmt, 5, label + " visible projection value kind");
        const std::uint64_t size_bytes = column_u64_be_or_throw(
            statement.stmt, 6, label + " visible projection file size");
        const std::string content_sha256 = sqlite_column_text_or_throw(
            statement.stmt, 7, 64U,
            label + " visible projection content digest");
        const SyncReplicaValueKind kind = encoded_kind == 1U
            ? SyncReplicaValueKind::File
            : encoded_kind == 2U
                ? SyncReplicaValueKind::Tombstone
                : throw std::runtime_error(
                      label + " visible projection value kind is invalid");
        const SyncValidationResult path_validation =
            validate_sync_relative_path(canonical_path);
        if (!path_validation.ok ||
            !is_lowercase_sha256_hex(operation_id) ||
            (kind == SyncReplicaValueKind::File &&
             !is_lowercase_sha256_hex(content_sha256)) ||
            (kind == SyncReplicaValueKind::Tombstone &&
             (size_bytes != 0U || !content_sha256.empty())) ||
            (preserve_file &&
             (is_primary || kind != SyncReplicaValueKind::File))) {
            throw std::runtime_error(
                label + " visible projection row is noncanonical");
        }

        if (!have_path || canonical_path != current.canonical_path) {
            finish_path_or_throw();
            current.canonical_path = canonical_path;
            have_path = true;
        }
        if (ordinal != current.visible_operation_ids.size() ||
            (!previous_operation_id.empty() &&
             previous_operation_id >= operation_id)) {
            throw std::runtime_error(
                label + " visible projection row order is noncanonical");
        }
        current.visible_operation_ids.push_back(operation_id);
        previous_operation_id = operation_id;
        if (is_primary) {
            ++primary_count;
            current.primary_operation_id = operation_id;
            current.primary_kind = kind;
        }
        if (preserve_file) {
            current.preserved_file_operation_ids.push_back(operation_id);
        }
    }
    finish_path_or_throw();
    if (path_count != meta.visible_path_count ||
        accumulator != meta.visible_state_digest) {
        throw std::runtime_error(
            label + " visible projection witness disagrees with metadata");
    }
}

void require_unique_visible_file_content_source_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    std::string_view source_canonical_path,
    std::string_view source_operation_id,
    std::uint64_t size_bytes,
    const std::string& content_sha256,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(source_operation_id) ||
        !is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            label + " unique-content source identity is invalid");
    }
    const SyncReplicaSqliteVisibleFileContentCutpoint cutpoint =
        read_visible_file_content_cutpoint_or_throw(
            db, meta, size_bytes, content_sha256, label);
    if (cutpoint.ambiguous) {
        throw std::runtime_error(
            label +
            " content is ambiguous across visible file paths");
    }
    if (!cutpoint.sole_visible_file_operation.has_value() ||
        cutpoint.sole_visible_file_operation->canonical_path !=
            source_canonical_path ||
        cutpoint.sole_visible_file_operation->operation_id !=
            source_operation_id) {
        throw std::runtime_error(
            label +
            " exact source is not the sole visible file with this content");
    }
}

struct TargetedPathHistoryCutpoint final {
    std::uint64_t retained_operation_count = 0U;
    std::uint64_t canonical_bytes_observed = 0U;
    std::string digest;
};

[[nodiscard]] TargetedPathHistoryCutpoint
read_targeted_path_history_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& canonical_path,
    const std::string& label) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-targeted-path-history-v1");
    append_framed(digest, meta.folder_id);
    append_framed(digest, meta.database_incarnation_sha256);
    digest.update(u64_be(meta.database_recovery_epoch));
    append_framed(digest, canonical_path);

    TargetedPathHistoryCutpoint cutpoint;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT o.operation_id,o.canonical_bytes,o.canonical_size_be,"
        "o.context_count_be,o.predecessor_count_be,o.evidence_state,"
        "p.canonical_path "
        "FROM main.sync_replica_operation_paths AS p "
        "JOIN main.sync_replica_operations AS o "
        "ON o.operation_id=p.operation_id "
        "WHERE p.canonical_path=? ORDER BY p.operation_id;",
        label + " path history prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, canonical_path, label + " path history bind");
    // Retain the prior identity by value. Each decoded row owns its string;
    // a string_view would dangle as soon as that row leaves this iteration and
    // could turn exact lexical-order reproof into undefined behavior.
    std::string previous_operation_id;
    bool first = true;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " path history query");
        }
        StoredOperationRow row = load_stored_operation_row_or_throw(
            statement.stmt, 0, meta.limits.model,
            label + " path history operation");
        const std::string indexed_path = sqlite_column_text_or_throw(
            statement.stmt, 6, 4096U, label + " path history index value");
        if (indexed_path != canonical_path ||
            row.operation.folder_id != meta.folder_id ||
            row.operation.canonical_path != canonical_path ||
            (!first && previous_operation_id >= row.operation.operation_id)) {
            throw std::runtime_error(
                label + " path history index or ordering mismatch");
        }
        previous_operation_id = row.operation.operation_id;
        first = false;
        cutpoint.retained_operation_count = increment_or_throw(
            cutpoint.retained_operation_count,
            label + " path history operation count");
        if (cutpoint.retained_operation_count > meta.evidence_count) {
            throw std::runtime_error(
                label + " path history exceeds retained evidence count");
        }
        cutpoint.canonical_bytes_observed = checked_add_or_throw(
            cutpoint.canonical_bytes_observed,
            sync_replica_operation_canonical_size_or_throw(
                row.operation, meta.limits.model),
            label + " path history canonical bytes");
        append_framed(digest, row.operation.operation_id);
        append_framed(digest, evidence_state_text(row.evidence_state));
    }
    digest.update(u64_be(cutpoint.retained_operation_count));
    digest.update(u64_be(cutpoint.canonical_bytes_observed));
    cutpoint.digest = digest.finish_hex();
    return cutpoint;
}

[[nodiscard]] std::vector<SyncReplicaOperation>
read_active_causal_head_operations_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    std::vector<SyncReplicaOperation> heads;
    heads.reserve(static_cast<std::size_t>(std::min<std::uint64_t>(
        meta.limits.model.max_predecessor_ids, 256U)));
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT o.operation_id,o.canonical_bytes,o.canonical_size_be,"
        "o.context_count_be,o.predecessor_count_be,o.evidence_state,"
        "p.canonical_path "
        "FROM main.sync_replica_heads AS h "
        "JOIN main.sync_replica_operations AS o "
        "ON o.operation_id=h.operation_id "
        "JOIN main.sync_replica_operation_paths AS p "
        "ON p.operation_id=o.operation_id "
        "ORDER BY h.operation_id;",
        label + " causal head prepare");
    // Keep lexical reproof independent of the current decoded row lifetime.
    std::string previous_operation_id;
    bool first = true;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " causal head query");
        }
        if (heads.size() >= meta.limits.model.max_predecessor_ids) {
            throw std::length_error(
                label + " active causal heads exceed predecessor limit");
        }
        StoredOperationRow row = load_stored_operation_row_or_throw(
            statement.stmt, 0, meta.limits.model,
            label + " causal head operation");
        const std::string indexed_path = sqlite_column_text_or_throw(
            statement.stmt, 6, 4096U, label + " causal head path");
        if (row.evidence_state != SyncReplicaEvidenceState::Active ||
            row.operation.folder_id != meta.folder_id ||
            indexed_path != row.operation.canonical_path ||
            (!first && previous_operation_id >= row.operation.operation_id)) {
            throw std::runtime_error(
                label + " causal head projection is noncanonical");
        }
        previous_operation_id = row.operation.operation_id;
        first = false;
        heads.push_back(std::move(row.operation));
    }
    return heads;
}

[[nodiscard]] std::optional<std::string>
read_exact_operation_path_or_none_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& operation_id,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path FROM main.sync_replica_operation_paths "
        "WHERE operation_id=? LIMIT 2;",
        label + " operation path prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, operation_id, label + " operation path bind");
    const int result = sqlite3_step(statement.stmt);
    if (result == SQLITE_DONE) return std::nullopt;
    if (result != SQLITE_ROW) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), result,
            label + " operation path query");
    }
    std::string path = sqlite_column_text_or_throw(
        statement.stmt, 0, 4096U, label + " operation path value");
    require_done_or_throw(statement.stmt, label + " operation path query");
    return path;
}

[[nodiscard]] std::vector<SyncReplicaOperation>
read_exact_active_predecessors_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const SyncReplicaOperation& operation,
    const std::string& label) {
    if (operation.predecessor_operation_ids.size() >
        meta.limits.model.max_predecessor_ids) {
        throw std::length_error(label + " predecessor set exceeds policy");
    }
    std::vector<SyncReplicaOperation> predecessors;
    predecessors.reserve(operation.predecessor_operation_ids.size());
    for (const std::string& operation_id :
         operation.predecessor_operation_ids) {
        std::optional<StoredOperationRow> row =
            read_exact_operation_row_or_none_or_throw(
                db, meta, operation_id, label + " predecessor");
        const std::optional<std::string> indexed_path =
            read_exact_operation_path_or_none_or_throw(
                db, operation_id, label + " predecessor");
        if (!row.has_value() || !indexed_path.has_value() ||
            row->evidence_state != SyncReplicaEvidenceState::Active ||
            row->operation.folder_id != meta.folder_id ||
            *indexed_path != row->operation.canonical_path) {
            throw std::runtime_error(
                label + " prepared predecessor is no longer exact active evidence");
        }
        predecessors.push_back(std::move(row->operation));
    }
    return predecessors;
}

[[nodiscard]] bool has_retained_child_reference_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& parent_operation_id,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT 1 FROM main.sync_replica_parent_edges "
        "WHERE parent_operation_id=? LIMIT 1;",
        label + " reverse dependency prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, parent_operation_id,
        label + " reverse dependency bind");
    const int result = sqlite3_step(statement.stmt);
    if (result == SQLITE_DONE) return false;
    if (result != SQLITE_ROW) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), result,
            label + " reverse dependency query");
    }
    require_done_or_throw(
        statement.stmt, label + " reverse dependency query");
    return true;
}

[[nodiscard]] bool has_exact_local_operation_binding_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaOperation& operation,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id FROM main.sync_replica_local_operations "
        "WHERE counter_be=? LIMIT 2;",
        label + " local operation binding prepare");
    bind_u64_be_or_throw(
        statement.stmt, 1, operation.dot.counter,
        label + " local operation counter bind");
    const int result = sqlite3_step(statement.stmt);
    if (result == SQLITE_DONE) return false;
    if (result != SQLITE_ROW) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), result,
            label + " local operation binding query");
    }
    const std::string operation_id = sqlite_column_text_or_throw(
        statement.stmt, 0, 64U, label + " local operation binding identity");
    require_done_or_throw(
        statement.stmt, label + " local operation binding query");
    return operation_id == operation.operation_id;
}

void require_no_temporary_triggers_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM temp.sqlite_schema "
        "WHERE type='trigger' AND sql IS NOT NULL;",
        label + " temporary trigger query prepare");
    require_row_or_throw(statement.stmt, label + " temporary trigger query");
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " temporary trigger count");
    require_done_or_throw(statement.stmt, label + " temporary trigger query");
    if (count != 0U) {
        throw std::runtime_error(
            label + " cannot use targeted publication while TEMP triggers exist");
    }
}

void verify_operation_paths_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::vector<SyncReplicaOperation>& operations,
    const DurableMeta& meta,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_operation_paths;",
        label + " operation path count");
    if (row_count != meta.evidence_count ||
        row_count != size_to_u64_or_throw(
            operations.size(), label + " operation path expected count")) {
        throw std::runtime_error(
            label + " operation path count disagrees with retained evidence");
    }
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id,canonical_path "
        "FROM main.sync_replica_operation_paths ORDER BY operation_id;",
        label + " operation path query prepare");
    std::size_t index = 0U;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " operation path query");
        }
        if (index >= operations.size()) {
            throw std::runtime_error(label + " has an extra operation path row");
        }
        const std::string operation_id = sqlite_column_text_or_throw(
            statement.stmt, 0, 64U, label + " operation path identity");
        const std::string canonical_path = sqlite_column_text_or_throw(
            statement.stmt, 1, 4096U, label + " operation path value");
        if (operation_id != operations[index].operation_id ||
            canonical_path != operations[index].canonical_path) {
            throw std::runtime_error(
                label + " operation path projection mismatch");
        }
        ++index;
    }
    if (index != operations.size()) {
        throw std::runtime_error(label + " is missing an operation path row");
    }
}

void insert_operation_path_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::span<const SyncReplicaOperation> operations,
    const std::string& label) {
    if (operations.empty()) return;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_operation_paths("
        "operation_id,canonical_path) VALUES(?,?);",
        label + " operation path insert prepare");
    for (const SyncReplicaOperation& operation : operations) {
        sqlite_bind_text_or_throw(
            statement.stmt, 1, operation.operation_id,
            label + " bind operation path identity");
        sqlite_bind_text_or_throw(
            statement.stmt, 2, operation.canonical_path,
            label + " bind operation path value");
        sqlite_step_done_or_throw(
            statement.stmt, label + " operation path insert");
        reset_statement_or_throw(
            statement.stmt, label + " operation path insert");
    }
}

void verify_parent_edges_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::vector<SyncReplicaOperation>& operations,
    const DurableMeta& meta,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_parent_edges;",
        label + " parent edge count");
    if (row_count != meta.retained_predecessor_ids) {
        throw std::runtime_error(
            label + " parent edge count disagrees with retained charge");
    }
    std::vector<std::tuple<std::string, std::uint64_t, std::string>> expected;
    expected.reserve(u64_to_size_or_throw(row_count, label + " parent edge count"));
    for (const SyncReplicaOperation& operation : operations) {
        for (std::size_t index = 0;
             index < operation.predecessor_operation_ids.size(); ++index) {
            expected.emplace_back(
                operation.operation_id,
                static_cast<std::uint64_t>(index),
                operation.predecessor_operation_ids[index]);
        }
    }
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT child_operation_id,parent_ordinal,parent_operation_id "
        "FROM main.sync_replica_parent_edges "
        "ORDER BY child_operation_id,parent_ordinal;",
        label + " parent edge query prepare");
    std::size_t index = 0;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " parent edge query");
        }
        if (index >= expected.size()) {
            throw std::runtime_error(label + " has an extra parent edge");
        }
        const auto observed = std::tuple{
            sqlite_column_text_or_throw(
                statement.stmt, 0, 64U, label + " parent child id"),
            sqlite_column_u64_or_throw(
                statement.stmt, 1, label + " parent ordinal"),
            sqlite_column_text_or_throw(
                statement.stmt, 2, 64U, label + " parent id")};
        if (observed != expected[index]) {
            throw std::runtime_error(label + " parent edge attestation mismatch");
        }
        ++index;
    }
    if (index != expected.size()) {
        throw std::runtime_error(label + " is missing a parent edge");
    }
}

void verify_heads_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaModel& model,
    const std::string& label) {
    const std::vector<std::string> expected =
        model.causal_head_operation_ids();
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_heads;",
        label + " head count");
    if (row_count != size_to_u64_or_throw(expected.size(), label + " heads")) {
        throw std::runtime_error(label + " head row count mismatch");
    }
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id FROM main.sync_replica_heads "
        "ORDER BY operation_id;",
        label + " head query prepare");
    std::size_t index = 0;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " head query");
        }
        if (index >= expected.size() ||
            sqlite_column_text_or_throw(
                statement.stmt, 0, 64U, label + " head id") !=
                expected[index]) {
            throw std::runtime_error(label + " head projection mismatch");
        }
        ++index;
    }
}

using VisibleRow = std::tuple<
    std::string, std::uint64_t, std::string, bool, bool,
    SyncReplicaValueKind, std::uint64_t, std::string>;

[[nodiscard]] std::vector<VisibleRow> expected_visible_rows(
    const SyncReplicaModel& model) {
    std::vector<VisibleRow> rows;
    for (const SyncReplicaPathView& view : model.visible_paths()) {
        const std::set<std::string> preserved(
            view.preserved_file_operation_ids.begin(),
            view.preserved_file_operation_ids.end());
        for (std::size_t index = 0;
             index < view.visible_operation_ids.size(); ++index) {
            const std::string& operation_id = view.visible_operation_ids[index];
            const auto operation = model.operation_by_id(operation_id);
            if (!operation.has_value() ||
                operation->canonical_path != view.canonical_path) {
                throw std::logic_error(
                    "sync replica visible projection lost its operation");
            }
            rows.emplace_back(
                view.canonical_path,
                static_cast<std::uint64_t>(index),
                operation_id,
                operation_id == view.primary_operation_id,
                preserved.contains(operation_id),
                operation->kind,
                operation->size_bytes,
                operation->content_sha256);
        }
    }
    return rows;
}

void verify_visible_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaModel& model,
    std::uint64_t schema_version,
    const std::string& label) {
    if (schema_version < kLegacySchemaVersion ||
        schema_version > kSchemaVersion) {
        throw std::logic_error(label + " visible schema version is unsupported");
    }
    const bool has_value_projection = schema_version == kSchemaVersion;
    const std::vector<VisibleRow> expected = expected_visible_rows(model);
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_visible;",
        label + " visible row count");
    if (row_count != size_to_u64_or_throw(
                         expected.size(), label + " visible rows")) {
        throw std::runtime_error(label + " visible row count mismatch");
    }
    const std::string query = has_value_projection
        ? "SELECT canonical_path,visible_ordinal,operation_id,is_primary,"
          "preserve_file,value_kind,size_bytes_be,content_sha256 "
          "FROM main.sync_replica_visible "
          "ORDER BY canonical_path,visible_ordinal;"
        : "SELECT canonical_path,visible_ordinal,operation_id,is_primary,"
          "preserve_file FROM main.sync_replica_visible "
          "ORDER BY canonical_path,visible_ordinal;";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, query, label + " visible query prepare");
    std::size_t index = 0;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " visible query");
        }
        if (index >= expected.size()) {
            throw std::runtime_error(label + " has an extra visible row");
        }
        const VisibleRow& wanted = expected[index];
        const std::string observed_path = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestRelativePathMaxBytes,
            label + " visible path");
        const std::uint64_t observed_ordinal = sqlite_column_u64_or_throw(
            statement.stmt, 1, label + " visible ordinal");
        const std::string observed_operation_id = sqlite_column_text_or_throw(
            statement.stmt, 2, 64U, label + " visible operation id");
        const bool observed_primary = sqlite_column_bool_or_throw(
            statement.stmt, 3, label + " visible primary");
        const bool observed_preserve = sqlite_column_bool_or_throw(
            statement.stmt, 4, label + " visible preserve");
        if (observed_path != std::get<0>(wanted) ||
            observed_ordinal != std::get<1>(wanted) ||
            observed_operation_id != std::get<2>(wanted) ||
            observed_primary != std::get<3>(wanted) ||
            observed_preserve != std::get<4>(wanted)) {
            throw std::runtime_error(label + " visible projection mismatch");
        }
        if (has_value_projection) {
            const std::uint64_t observed_kind = sqlite_column_u64_or_throw(
                statement.stmt, 5, label + " visible value kind");
            const std::uint64_t observed_size = column_u64_be_or_throw(
                statement.stmt, 6, label + " visible file size");
            const std::string observed_content = sqlite_column_text_or_throw(
                statement.stmt, 7, 64U, label + " visible content digest");
            const std::uint64_t expected_kind =
                visible_value_kind_integer_or_throw(
                    std::get<5>(wanted), label);
            if (observed_kind != expected_kind ||
                observed_size != std::get<6>(wanted) ||
                observed_content != std::get<7>(wanted)) {
                throw std::runtime_error(
                    label + " visible value projection mismatch");
            }
        }
        ++index;
    }
    if (index != expected.size()) {
        throw std::runtime_error(label + " is missing a visible row");
    }
}

void validate_outbox_intent_or_throw(
    const SyncReplicaSqliteOutboxIntent& intent,
    const DurableMeta& meta,
    const std::map<std::string, SyncReplicaEvidenceState>& operation_ids,
    const std::string& label) {
    if (!sync_id_is_valid(intent.destination_device_id) ||
        !is_lowercase_sha256_hex(intent.operation_id) ||
        !operation_ids.contains(intent.operation_id) ||
        intent.enqueued_generation == 0U ||
        intent.enqueued_generation > meta.state_generation) {
        throw std::runtime_error(label + " outbox intent is invalid");
    }
    validate_sync_replica_outbox_lease_state_or_throw(
        intent.lease, label + " outbox lease");
}

[[nodiscard]] std::uint64_t attest_outbox_shape_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_outbox;",
        label + " outbox count");
    if (row_count != meta.outbox_intent_count ||
        row_count > meta.limits.max_outbox_intents) {
        throw std::runtime_error(
            label + " outbox row count disagrees with durable policy");
    }
    return row_count;
}

[[nodiscard]] std::vector<SyncReplicaSqliteOutboxIntent>
read_legacy_outbox_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::map<std::string, SyncReplicaEvidenceState>& operation_ids,
    const std::string& label) {
    const std::uint64_t row_count = attest_outbox_shape_or_throw(
        db, meta, label);
    std::vector<SyncReplicaSqliteOutboxIntent> outbox;
    outbox.reserve(u64_to_size_or_throw(row_count, label + " outbox count"));
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT destination_device_id,operation_id,enqueued_generation_be "
        "FROM main.sync_replica_outbox "
        "ORDER BY destination_device_id,operation_id;",
        label + " legacy outbox query prepare");
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " legacy outbox query");
        }
        SyncReplicaSqliteOutboxIntent intent;
        intent.destination_device_id = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestIdMaxBytes,
            label + " outbox destination");
        intent.operation_id = sqlite_column_text_or_throw(
            statement.stmt, 1, 64U, label + " outbox operation id");
        intent.enqueued_generation = column_u64_be_or_throw(
            statement.stmt, 2, label + " outbox generation");
        validate_outbox_intent_or_throw(
            intent, meta, operation_ids, label);
        outbox.push_back(std::move(intent));
    }
    const std::uint64_t destination_bytes =
        outbox_destination_bytes_or_throw(outbox);
    if (destination_bytes != meta.outbox_destination_bytes ||
        destination_bytes > meta.limits.max_outbox_destination_bytes ||
        legacy_outbox_digest_or_throw(meta.folder_id, outbox) !=
            meta.outbox_digest) {
        throw std::runtime_error(label + " legacy outbox attestation mismatch");
    }
    return outbox;
}

[[nodiscard]] std::vector<SyncReplicaSqliteOutboxIntent>
read_outbox_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::map<std::string, SyncReplicaEvidenceState>& operation_ids,
    bool has_retry_release_provenance,
    const std::string& label) {
    const std::uint64_t row_count = attest_outbox_shape_or_throw(
        db, meta, label);
    std::vector<SyncReplicaSqliteOutboxIntent> outbox;
    outbox.reserve(u64_to_size_or_throw(row_count, label + " outbox count"));
    const std::string query = has_retry_release_provenance
        ? "SELECT destination_device_id,operation_id,enqueued_generation_be,"
          "dispatch_attempts_be,claim_id,worker_id,claimed_at_epoch_be,"
          "lease_expires_at_epoch_be,retry_not_before_epoch_be,"
          "retry_released_at_epoch_be,retry_release_provenance "
          "FROM main.sync_replica_outbox "
          "ORDER BY destination_device_id,operation_id;"
        : "SELECT destination_device_id,operation_id,enqueued_generation_be,"
          "dispatch_attempts_be,claim_id,worker_id,claimed_at_epoch_be,"
          "lease_expires_at_epoch_be,retry_not_before_epoch_be "
          "FROM main.sync_replica_outbox "
          "ORDER BY destination_device_id,operation_id;";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, query, label + " outbox query prepare");
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " outbox query");
        }
        SyncReplicaSqliteOutboxIntent intent;
        intent.destination_device_id = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestIdMaxBytes,
            label + " outbox destination");
        intent.operation_id = sqlite_column_text_or_throw(
            statement.stmt, 1, 64U, label + " outbox operation id");
        intent.enqueued_generation = column_u64_be_or_throw(
            statement.stmt, 2, label + " outbox generation");
        intent.lease.dispatch_attempts = column_u64_be_or_throw(
            statement.stmt, 3, label + " outbox dispatch attempts");
        intent.lease.claim_id = sqlite_column_text_or_throw(
            statement.stmt, 4, 64U, label + " outbox claim id");
        intent.lease.worker_id = sqlite_column_text_or_throw(
            statement.stmt, 5, kSyncManifestIdMaxBytes,
            label + " outbox worker id");
        intent.lease.claimed_at_epoch = column_u64_be_or_throw(
            statement.stmt, 6, label + " outbox claimed at");
        intent.lease.lease_expires_at_epoch = column_u64_be_or_throw(
            statement.stmt, 7, label + " outbox lease expiry");
        intent.lease.retry_not_before_epoch = column_u64_be_or_throw(
            statement.stmt, 8, label + " outbox retry not before");
        if (has_retry_release_provenance) {
            intent.lease.retry_released_at_epoch = column_u64_be_or_throw(
                statement.stmt, 9, label + " outbox retry released at");
            intent.lease.retry_release_provenance =
                retry_release_provenance_from_u64_or_throw(
                    sqlite_column_u64_or_throw(
                        statement.stmt, 10,
                        label + " outbox retry release provenance"),
                    label + " outbox");
        } else if (intent.lease.dispatch_attempts != 0U &&
                   intent.lease.claim_id.empty()) {
            // Schema v2/v3 retained the deadline but discarded the accepted
            // observation that minted it. Keep the gap explicit; never infer
            // an exact release time from a maximum-delay policy bound.
            intent.lease.retry_release_provenance =
                SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven;
        }
        validate_outbox_intent_or_throw(
            intent, meta, operation_ids, label);
        outbox.push_back(std::move(intent));
    }
    const std::uint64_t destination_bytes =
        outbox_destination_bytes_or_throw(outbox);
    const std::string observed_digest = has_retry_release_provenance
        ? outbox_digest_or_throw(meta.folder_id, outbox)
        : prior_outbox_digest_or_throw(meta.folder_id, outbox);
    if (destination_bytes != meta.outbox_destination_bytes ||
        destination_bytes > meta.limits.max_outbox_destination_bytes ||
        observed_digest != meta.outbox_digest) {
        throw std::runtime_error(label + " outbox attestation mismatch");
    }
    return outbox;
}

[[nodiscard]] std::vector<std::string>
read_historical_version_pins_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const SyncReplicaModel& model,
    const std::string& label) {
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_history_pins;",
        label + " historical-version pin count");
    if (row_count != meta.historical_version_pin_count ||
        row_count > meta.evidence_count) {
        throw std::runtime_error(
            label + " historical-version pin count disagrees with evidence");
    }

    std::vector<std::string> pins;
    pins.reserve(u64_to_size_or_throw(
        row_count, label + " historical-version pin count"));
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id FROM main.sync_replica_history_pins "
        "ORDER BY operation_id;",
        label + " historical-version pin query prepare");
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " historical-version pin query");
        }
        std::string operation_id = sqlite_column_text_or_throw(
            statement.stmt, 0, 64U,
            label + " historical-version pin operation ID");
        if (!is_lowercase_sha256_hex(operation_id) ||
            (!pins.empty() && pins.back() >= operation_id)) {
            throw std::runtime_error(
                label + " historical-version pin order is noncanonical");
        }
        const std::optional<SyncReplicaOperation> operation =
            model.evidence_operation_by_id(operation_id);
        if (!operation.has_value() ||
            operation->kind != SyncReplicaValueKind::File) {
            throw std::runtime_error(
                label + " historical-version pin does not name retained file evidence");
        }
        pins.push_back(std::move(operation_id));
    }
    if (pins.size() != static_cast<std::size_t>(row_count) ||
        historical_version_pin_set_digest_or_throw(
            meta.folder_id, pins, label + " historical-version pin set") !=
            meta.historical_version_pin_set_digest) {
        throw std::runtime_error(
            label + " historical-version pin-set attestation mismatch");
    }
    return pins;
}

[[nodiscard]] std::uint64_t outbox_clock_migration_floor_or_throw(
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox,
    const std::string& label) {
    std::uint64_t floor = 0U;
    for (const SyncReplicaSqliteOutboxIntent& intent : outbox) {
        validate_sync_replica_outbox_lease_state_or_throw(intent.lease, label);
        if (!intent.lease.claim_id.empty()) {
            floor = std::max(floor, intent.lease.claimed_at_epoch);
        } else if (intent.lease.dispatch_attempts != 0U) {
            std::uint64_t release_floor = 0U;
            if (intent.lease.retry_release_provenance ==
                SyncReplicaOutboxRetryReleaseProvenance::Exact) {
                release_floor = intent.lease.retry_released_at_epoch;
            } else {
                // A released v2/v3 attempt proves that release time was
                // positive and no earlier than deadline minus the fixed retry
                // budget. The exact observation was discarded, so retain only
                // the strongest lower bound the old row actually proves.
                release_floor =
                    intent.lease.retry_not_before_epoch >
                            kSyncReplicaOutboxMaxRetryDelaySeconds
                        ? intent.lease.retry_not_before_epoch -
                              kSyncReplicaOutboxMaxRetryDelaySeconds
                        : 1U;
            }
            floor = std::max(floor, release_floor);
        }
    }
    return floor;
}

[[nodiscard]] LoadedState load_state_for_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    std::span<const SchemaDefinition> schema,
    std::uint64_t schema_version,
    bool legacy_outbox,
    bool has_retry_release_provenance,
    bool has_outbox_clock,
    const std::string& label) {
    verify_schema_or_throw(db, schema, label);
    require_foreign_keys_or_throw(db, label);
    require_no_foreign_key_violations_or_throw(db, label);
    DurableMeta meta = read_meta_or_throw(db, schema_version, label);
    if (meta.folder_id != expected_folder_id ||
        meta.local_actor != expected_local_actor) {
        throw std::runtime_error(
            label + " folder or local actor identity mismatch");
    }

    auto [operations, stored_states] =
        read_operations_or_throw(db, meta, label);
    if (schema_version == kVisiblePathSchemaVersion ||
        schema_version == kSchemaVersion) {
        verify_operation_paths_or_throw(db, operations, meta, label);
    }
    verify_parent_edges_or_throw(db, operations, meta, label);
    SyncReplicaDurableState durable;
    durable.folder_id = meta.folder_id;
    durable.local_actor = meta.local_actor;
    durable.last_local_counter = meta.last_local_counter;
    durable.local_operation_ids =
        read_local_operation_ids_or_throw(db, meta, label);
    const std::string observed_local_operation_digest =
        (schema_version == kVisiblePathSchemaVersion ||
         schema_version == kSchemaVersion)
            ? local_operation_chain_digest_or_throw(
                  meta.folder_id, meta.local_actor,
                  durable.local_operation_ids)
            : local_operation_digest_or_throw(
                  meta.folder_id, meta.local_actor,
                  durable.local_operation_ids);
    if (observed_local_operation_digest != meta.local_operation_digest) {
        throw std::runtime_error(
            label + " local operation authority digest mismatch");
    }
    durable.operations = std::move(operations);
    SyncReplicaModel model = SyncReplicaModel::restore_or_throw(
        std::move(durable), meta.limits.model);

    if (size_to_u64_or_throw(model.evidence_count(), label + " evidence count") !=
            meta.evidence_count ||
        size_to_u64_or_throw(model.operation_count(), label + " active count") !=
            meta.active_count ||
        model.retained_canonical_bytes() != meta.retained_canonical_bytes ||
        model.retained_context_entry_count() !=
            meta.retained_context_entries ||
        model.retained_predecessor_id_count() !=
            meta.retained_predecessor_ids ||
        model.local_actor_compromised() != meta.local_actor_compromised) {
        throw std::runtime_error(label + " durable model metadata mismatch");
    }
    if (schema_version == kVisiblePathSchemaVersion ||
        schema_version == kSchemaVersion) {
        if (model.operation_set_accumulator_digest() !=
                meta.operation_set_digest ||
            model.evidence_set_accumulator_digest() !=
                meta.evidence_set_digest ||
            model.visible_path_count() != meta.visible_path_count ||
            model.visible_state_accumulator_digest() !=
                meta.visible_state_digest) {
            throw std::runtime_error(
                label + " durable incremental projection metadata mismatch");
        }
    } else if (model.operation_set_digest() != meta.operation_set_digest ||
               model.evidence_set_digest() != meta.evidence_set_digest ||
               model.visible_state_digest() != meta.visible_state_digest) {
        throw std::runtime_error(label + " durable model metadata mismatch");
    }
    for (const auto& [operation_id, stored_state] : stored_states) {
        if (model.evidence_state(operation_id) != stored_state) {
            throw std::runtime_error(
                label + " stored evidence projection mismatch");
        }
    }
    verify_heads_or_throw(db, model, label);
    verify_visible_or_throw(db, model, schema_version, label);
    std::vector<SyncReplicaSqliteOutboxIntent> outbox = legacy_outbox
        ? read_legacy_outbox_or_throw(db, meta, stored_states, label)
        : read_outbox_or_throw(
              db, meta, stored_states, has_retry_release_provenance, label);
    const std::uint64_t migration_floor =
        outbox_clock_migration_floor_or_throw(outbox, label + " outbox clock");
    DurableOutboxClock outbox_clock = !has_outbox_clock
        ? make_outbox_clock_or_throw(
              meta.folder_id, meta.local_actor,
              migrated_clock_state_or_throw(
                  migration_floor, label + " synthetic legacy clock"),
              label + " synthetic legacy outbox clock")
        : (schema_version == kSchemaVersion ||
                   schema_version == kVisiblePathSchemaVersion ||
                   schema_version == kDatabaseLineageSchemaVersion ||
                   schema_version == kHistoricalPinSchemaVersion ||
                   schema_version == kRetentionRootSchemaVersion
               ? read_current_outbox_clock_or_throw(
                     db, meta.folder_id, meta.local_actor, label)
               : read_legacy_outbox_clock_or_throw(db, meta, label));
    if (outbox_clock.state.high_water_epoch < migration_floor) {
        throw std::runtime_error(
            label + " outbox clock predates retained lease authority");
    }
    if (schema_version == kSchemaVersion ||
        schema_version == kVisiblePathSchemaVersion ||
        schema_version == kDatabaseLineageSchemaVersion ||
        schema_version == kHistoricalPinSchemaVersion ||
        schema_version == kRetentionRootSchemaVersion) {
        validate_sync_replica_outbox_clock_state_against_policy_or_throw(
            outbox_clock.state, outbox_clock_policy(meta.limits),
            label + " durable outbox clock");
    }
    std::vector<std::string> historical_version_pins =
        (schema_version == kSchemaVersion ||
         schema_version == kVisiblePathSchemaVersion ||
         schema_version == kDatabaseLineageSchemaVersion ||
         schema_version == kHistoricalPinSchemaVersion)
            ? read_historical_version_pins_or_throw(
                  db, meta, model, label)
            : std::vector<std::string>{};
    return {std::move(meta), std::move(outbox_clock), std::move(model),
            std::move(stored_states), std::move(outbox),
            std::move(historical_version_pins)};
}

[[nodiscard]] LoadedState load_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor, kSchema,
        kSchemaVersion, false, true, true, label);
}

[[nodiscard]] LoadedState load_visible_path_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor, kVisiblePathSchema,
        kVisiblePathSchemaVersion, false, true, true, label);
}

[[nodiscard]] LoadedState load_legacy_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor, kLegacySchema,
        kLegacySchemaVersion, true, false, false, label);
}

[[nodiscard]] LoadedState load_previous_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor, kPreviousSchema,
        kPreviousSchemaVersion, false, false, false, label);
}

[[nodiscard]] LoadedState load_clock_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor, kClockSchema,
        kClockSchemaVersion, false, false, true, label);
}

[[nodiscard]] LoadedState load_retry_provenance_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor,
        kRetryProvenanceSchema, kRetryProvenanceSchemaVersion,
        false, true, true, label);
}

[[nodiscard]] LoadedState load_retention_root_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor,
        kRetentionRootSchema, kRetentionRootSchemaVersion,
        false, true, true, label);
}

[[nodiscard]] LoadedState load_historical_pin_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor,
        kHistoricalPinSchema, kHistoricalPinSchemaVersion,
        false, true, true, label);
}

[[nodiscard]] LoadedState load_database_lineage_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    const std::string& label) {
    return load_state_for_schema_or_throw(
        db, expected_folder_id, expected_local_actor,
        kDatabaseLineageSchema, kDatabaseLineageSchemaVersion,
        false, true, true, label);
}

[[nodiscard]] DurableMeta meta_from_state_or_throw(
    const SyncReplicaModel& model,
    std::string database_incarnation_sha256,
    std::uint64_t database_recovery_epoch,
    const SyncReplicaSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    std::uint64_t policy_generation,
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox,
    std::span<const std::string> historical_version_pins) {
    if (!is_lowercase_sha256_hex(database_incarnation_sha256) ||
        database_recovery_epoch == 0U) {
        throw std::invalid_argument(
            "sync replica SQLite database lineage is invalid");
    }
    DurableMeta meta;
    meta.database_incarnation_sha256 =
        std::move(database_incarnation_sha256);
    meta.database_recovery_epoch = database_recovery_epoch;
    meta.folder_id = model.folder_id();
    meta.local_actor = model.local_actor();
    meta.last_local_counter = model.last_local_counter();
    meta.state_generation = state_generation;
    meta.policy_generation = policy_generation;
    meta.limits = limits;
    meta.evidence_count = size_to_u64_or_throw(
        model.evidence_count(), "sync replica SQLite evidence count");
    meta.active_count = size_to_u64_or_throw(
        model.operation_count(), "sync replica SQLite active count");
    meta.retained_canonical_bytes = model.retained_canonical_bytes();
    meta.retained_context_entries = model.retained_context_entry_count();
    meta.retained_predecessor_ids = model.retained_predecessor_id_count();
    meta.outbox_intent_count = size_to_u64_or_throw(
        outbox.size(), "sync replica SQLite outbox count");
    meta.outbox_destination_bytes =
        outbox_destination_bytes_or_throw(outbox);
    meta.historical_version_pin_count = size_to_u64_or_throw(
        historical_version_pins.size(),
        "sync replica SQLite historical-version pin count");
    if (meta.historical_version_pin_count > meta.evidence_count) {
        throw std::logic_error(
            "sync replica SQLite historical-version pin count exceeds evidence");
    }
    meta.historical_version_pin_set_digest =
        historical_version_pin_set_digest_or_throw(
            model.folder_id(), historical_version_pins);
    meta.local_actor_compromised = model.local_actor_compromised();
    meta.local_operation_digest = local_operation_chain_digest_or_throw(
        model.folder_id(), model.local_actor(), model.local_operation_ids());
    meta.operation_set_digest = model.operation_set_accumulator_digest();
    meta.evidence_set_digest = model.evidence_set_accumulator_digest();
    meta.visible_path_count = model.visible_path_count();
    meta.visible_state_digest = model.visible_state_accumulator_digest();
    meta.outbox_digest = outbox_digest_or_throw(model.folder_id(), outbox);
    meta.cutpoint_digest = cutpoint_digest_or_throw(meta);
    return meta;
}

void update_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const DurableMeta& meta,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_meta SET "
        "database_incarnation_sha256=?,database_recovery_epoch_be=?,"
        "folder_id=?,local_device_id=?,local_epoch_be=?,"
        "last_local_counter_be=?,state_generation_be=?,policy_generation_be=?,"
        "max_operations_be=?,max_context_entries_be=?,max_predecessor_ids_be=?,"
        "max_canonical_operation_bytes_be=?,max_retained_canonical_bytes_be=?,"
        "max_retained_context_entries_be=?,max_retained_predecessor_ids_be=?,"
        "max_outbox_intents_be=?,max_outbox_destination_bytes_be=?,"
        "max_outbox_clock_uncertainty_ns_be=?,"
        "max_outbox_clock_forward_step_seconds_be=?,"
        "max_outbox_clock_realtime_lag_seconds_be=?,"
        "evidence_count_be=?,active_count_be=?,visible_path_count_be=?,"
        "retained_canonical_bytes_be=?,retained_context_entries_be=?,"
        "retained_predecessor_ids_be=?,"
        "outbox_intent_count_be=?,outbox_destination_bytes_be=?,"
        "historical_version_pin_count_be=?,historical_version_pin_set_digest=?,"
        "local_actor_compromised=?,local_operation_digest=?,operation_set_digest=?,"
        "evidence_set_digest=?,visible_state_digest=?,outbox_digest=?,"
        "cutpoint_digest=? WHERE id=1;",
        label + " meta update prepare");
    bind_meta_common_or_throw(statement.stmt, 1, meta, label + " meta update");
    sqlite_step_done_or_throw(statement.stmt, label + " meta update");
    auto borrow = db.borrow();
    if (sqlite3_changes(borrow.get()) != 1) {
        throw std::runtime_error(label + " meta update did not affect one row");
    }
}

void insert_operation_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaOperation& operation,
    SyncReplicaEvidenceState state,
    const SyncReplicaModelLimits& limits,
    bool local_operation,
    const std::string& label) {
    const std::string canonical =
        encode_sync_replica_operation_canonical_or_throw(operation, limits);
    SyncSqliteStmt operation_insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_operations("
        "operation_id,canonical_bytes,canonical_size_be,context_count_be,"
        "predecessor_count_be,evidence_state) VALUES(?,?,?,?,?,?);",
        label + " operation insert prepare");
    sqlite_bind_text_or_throw(
        operation_insert.stmt, 1, operation.operation_id,
        label + " bind operation id");
    sqlite_bind_blob_or_throw(
        operation_insert.stmt, 2, canonical,
        label + " bind canonical operation");
    bind_u64_be_or_throw(
        operation_insert.stmt, 3,
        size_to_u64_or_throw(canonical.size(), label + " canonical size"),
        label + " bind canonical size");
    bind_u64_be_or_throw(
        operation_insert.stmt, 4,
        size_to_u64_or_throw(
            operation.causal_context.size(), label + " context count"),
        label + " bind context count");
    bind_u64_be_or_throw(
        operation_insert.stmt, 5,
        size_to_u64_or_throw(
            operation.predecessor_operation_ids.size(),
            label + " predecessor count"),
        label + " bind predecessor count");
    sqlite_bind_text_or_throw(
        operation_insert.stmt, 6, std::string(evidence_state_text(state)),
        label + " bind evidence state");
    sqlite_step_done_or_throw(
        operation_insert.stmt, label + " operation insert");
    insert_operation_path_rows_or_throw(
        db, std::span<const SyncReplicaOperation>(&operation, 1U), label);

    if (!operation.predecessor_operation_ids.empty()) {
        SyncSqliteStmt parent_insert = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_replica_parent_edges("
            "child_operation_id,parent_ordinal,parent_operation_id)"
            "VALUES(?,?,?);",
            label + " parent insert prepare");
        for (std::size_t index = 0;
             index < operation.predecessor_operation_ids.size(); ++index) {
            sqlite_bind_text_or_throw(
                parent_insert.stmt, 1, operation.operation_id,
                label + " bind parent child");
            sqlite_bind_u64_or_throw(
                parent_insert.stmt, 2,
                static_cast<std::uint64_t>(index),
                label + " bind parent ordinal");
            sqlite_bind_text_or_throw(
                parent_insert.stmt, 3,
                operation.predecessor_operation_ids[index],
                label + " bind parent id");
            sqlite_step_done_or_throw(
                parent_insert.stmt, label + " parent insert");
            reset_statement_or_throw(
                parent_insert.stmt, label + " parent insert");
        }
    }

    if (local_operation) {
        SyncSqliteStmt local_insert = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_replica_local_operations("
            "counter_be,operation_id) VALUES(?,?);",
            label + " local operation insert prepare");
        bind_u64_be_or_throw(
            local_insert.stmt, 1, operation.dot.counter,
            label + " bind local counter");
        sqlite_bind_text_or_throw(
            local_insert.stmt, 2, operation.operation_id,
            label + " bind local operation id");
        sqlite_step_done_or_throw(
            local_insert.stmt, label + " local operation insert");
    }
}

void rewrite_projection_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaModel& model,
    const std::map<std::string, SyncReplicaEvidenceState>& persisted_states,
    const std::string& label) {
    SyncSqliteStmt state_update = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_operations SET evidence_state=? "
        "WHERE operation_id=?;",
        label + " evidence state update prepare");
    for (const SyncReplicaOperation& operation :
         model.all_evidence_operations()) {
        const auto state = model.evidence_state(operation.operation_id);
        if (!state.has_value()) {
            throw std::logic_error(
                label + " model omitted an evidence state");
        }
        const auto persisted = persisted_states.find(operation.operation_id);
        // New rows were inserted with their final state. Existing rows are
        // rewritten only when new evidence actually changes their projection.
        if (persisted == persisted_states.end() ||
            persisted->second == *state) {
            continue;
        }
        sqlite_bind_text_or_throw(
            state_update.stmt, 1,
            std::string(evidence_state_text(*state)),
            label + " bind evidence state");
        sqlite_bind_text_or_throw(
            state_update.stmt, 2, operation.operation_id,
            label + " bind evidence operation id");
        sqlite_step_done_or_throw(
            state_update.stmt, label + " evidence state update");
        auto borrow = db.borrow();
        if (sqlite3_changes(borrow.get()) != 1) {
            throw std::runtime_error(
                label + " evidence state update missed its row");
        }
        reset_statement_or_throw(
            state_update.stmt, label + " evidence state update");
    }

    sqlite_exec_or_throw(
        db,
        "DELETE FROM main.sync_replica_heads;"
        "DELETE FROM main.sync_replica_visible;",
        label + " clear derived projection");

    SyncSqliteStmt head_insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_heads(operation_id) VALUES(?);",
        label + " head insert prepare");
    for (const std::string& operation_id :
         model.causal_head_operation_ids()) {
        sqlite_bind_text_or_throw(
            head_insert.stmt, 1, operation_id,
            label + " bind head id");
        sqlite_step_done_or_throw(
            head_insert.stmt, label + " head insert");
        reset_statement_or_throw(
            head_insert.stmt, label + " head insert");
    }

    SyncSqliteStmt visible_insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_visible("
        "canonical_path,visible_ordinal,operation_id,is_primary,preserve_file,"
        "value_kind,size_bytes_be,content_sha256)"
        "VALUES(?,?,?,?,?,?,?,?);",
        label + " visible insert prepare");
    for (const VisibleRow& row : expected_visible_rows(model)) {
        sqlite_bind_text_or_throw(
            visible_insert.stmt, 1, std::get<0>(row),
            label + " bind visible path");
        sqlite_bind_u64_or_throw(
            visible_insert.stmt, 2, std::get<1>(row),
            label + " bind visible ordinal");
        sqlite_bind_text_or_throw(
            visible_insert.stmt, 3, std::get<2>(row),
            label + " bind visible operation");
        sqlite_bind_bool_or_throw(
            visible_insert.stmt, 4, std::get<3>(row),
            label + " bind visible primary");
        sqlite_bind_bool_or_throw(
            visible_insert.stmt, 5, std::get<4>(row),
            label + " bind visible preserve");
        sqlite_bind_u64_or_throw(
            visible_insert.stmt, 6,
            visible_value_kind_integer_or_throw(std::get<5>(row), label),
            label + " bind visible value kind");
        bind_u64_be_or_throw(
            visible_insert.stmt, 7, std::get<6>(row),
            label + " bind visible size");
        sqlite_bind_text_or_throw(
            visible_insert.stmt, 8, std::get<7>(row),
            label + " bind visible content digest");
        sqlite_step_done_or_throw(
            visible_insert.stmt, label + " visible insert");
        reset_statement_or_throw(
            visible_insert.stmt, label + " visible insert");
    }
}

void bind_outbox_lease_or_throw(
    sqlite3_stmt* statement,
    int first_index,
    const SyncReplicaOutboxLeaseState& lease,
    const std::string& label) {
    validate_sync_replica_outbox_lease_state_or_throw(lease, label);
    int index = first_index;
    bind_u64_be_or_throw(
        statement, index++, lease.dispatch_attempts,
        label + " bind dispatch attempts");
    sqlite_bind_text_or_throw(
        statement, index++, lease.claim_id, label + " bind claim id");
    sqlite_bind_text_or_throw(
        statement, index++, lease.worker_id, label + " bind worker id");
    bind_u64_be_or_throw(
        statement, index++, lease.claimed_at_epoch,
        label + " bind claimed at");
    bind_u64_be_or_throw(
        statement, index++, lease.lease_expires_at_epoch,
        label + " bind lease expiry");
    bind_u64_be_or_throw(
        statement, index++, lease.retry_not_before_epoch,
        label + " bind retry not before");
    bind_u64_be_or_throw(
        statement, index++, lease.retry_released_at_epoch,
        label + " bind retry released at");
    sqlite_bind_u64_or_throw(
        statement, index++,
        static_cast<std::uint64_t>(lease.retry_release_provenance),
        label + " bind retry release provenance");
}

void insert_outbox_intents_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::vector<SyncReplicaSqliteOutboxIntent>& intents,
    const std::string& label) {
    if (intents.empty()) return;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_outbox("
        "destination_device_id,operation_id,enqueued_generation_be,"
        "dispatch_attempts_be,claim_id,worker_id,claimed_at_epoch_be,"
        "lease_expires_at_epoch_be,retry_not_before_epoch_be,"
        "retry_released_at_epoch_be,retry_release_provenance)"
        "VALUES(?,?,?,?,?,?,?,?,?,?,?);",
        label + " outbox insert prepare");
    for (const SyncReplicaSqliteOutboxIntent& intent : intents) {
        sqlite_bind_text_or_throw(
            statement.stmt, 1, intent.destination_device_id,
            label + " bind outbox destination");
        sqlite_bind_text_or_throw(
            statement.stmt, 2, intent.operation_id,
            label + " bind outbox operation");
        bind_u64_be_or_throw(
            statement.stmt, 3, intent.enqueued_generation,
            label + " bind outbox generation");
        bind_outbox_lease_or_throw(
            statement.stmt, 4, intent.lease,
            label + " outbox lease");
        sqlite_step_done_or_throw(
            statement.stmt, label + " outbox insert");
        reset_statement_or_throw(
            statement.stmt, label + " outbox insert");
    }
}

void update_outbox_lease_exact_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteOutboxIntent& intent,
    const SyncReplicaOutboxLeaseState& previous,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_outbox SET "
        "dispatch_attempts_be=?,claim_id=?,worker_id=?,claimed_at_epoch_be=?,"
        "lease_expires_at_epoch_be=?,retry_not_before_epoch_be=?,"
        "retry_released_at_epoch_be=?,retry_release_provenance=? "
        "WHERE destination_device_id=? AND operation_id=? "
        "AND enqueued_generation_be=? AND dispatch_attempts_be=? "
        "AND claim_id=? AND worker_id=? AND claimed_at_epoch_be=? "
        "AND lease_expires_at_epoch_be=? AND retry_not_before_epoch_be=? "
        "AND retry_released_at_epoch_be=? "
        "AND retry_release_provenance=?;",
        label + " outbox lease update prepare");
    bind_outbox_lease_or_throw(
        statement.stmt, 1, intent.lease, label + " next lease");
    sqlite_bind_text_or_throw(
        statement.stmt, 9, intent.destination_device_id,
        label + " bind destination");
    sqlite_bind_text_or_throw(
        statement.stmt, 10, intent.operation_id,
        label + " bind operation");
    bind_u64_be_or_throw(
        statement.stmt, 11, intent.enqueued_generation,
        label + " bind generation");
    bind_outbox_lease_or_throw(
        statement.stmt, 12, previous, label + " previous lease");
    sqlite_step_done_or_throw(statement.stmt, label + " outbox lease update");
    auto borrow = db.borrow();
    if (sqlite3_changes(borrow.get()) != 1) {
        throw std::runtime_error(
            label + " outbox lease update missed its exact prior state");
    }
}

void delete_outbox_intent_exact_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteOutboxIntent& intent,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "DELETE FROM main.sync_replica_outbox "
        "WHERE destination_device_id=? AND operation_id=? "
        "AND enqueued_generation_be=? AND dispatch_attempts_be=? "
        "AND claim_id=? AND worker_id=? AND claimed_at_epoch_be=? "
        "AND lease_expires_at_epoch_be=? AND retry_not_before_epoch_be=? "
        "AND retry_released_at_epoch_be=? "
        "AND retry_release_provenance=?;",
        label + " outbox delete prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, intent.destination_device_id,
        label + " bind destination");
    sqlite_bind_text_or_throw(
        statement.stmt, 2, intent.operation_id,
        label + " bind operation");
    bind_u64_be_or_throw(
        statement.stmt, 3, intent.enqueued_generation,
        label + " bind generation");
    bind_outbox_lease_or_throw(
        statement.stmt, 4, intent.lease, label + " exact lease");
    sqlite_step_done_or_throw(statement.stmt, label + " outbox delete");
    auto borrow = db.borrow();
    if (sqlite3_changes(borrow.get()) != 1) {
        throw std::runtime_error(
            label + " outbox delete missed its exact prior state");
    }
}

[[nodiscard]] std::string random_claim_entropy_or_throw(
    const std::string& label) {
    std::string entropy(32U, '\0');
    const int result = RAND_bytes(
        reinterpret_cast<unsigned char*>(entropy.data()),
        static_cast<int>(entropy.size()));
    if (result != 1) {
        throw std::runtime_error(label + " CSPRNG claim entropy failed");
    }
    return entropy;
}

[[nodiscard]] std::vector<SyncReplicaSqliteOutboxIntent>::iterator
find_outbox_intent(
    std::vector<SyncReplicaSqliteOutboxIntent>& outbox,
    std::string_view destination_device_id,
    std::string_view operation_id) {
    const std::pair<std::string_view, std::string_view> key{
        destination_device_id, operation_id};
    auto found = std::lower_bound(
        outbox.begin(), outbox.end(), key,
        [](const SyncReplicaSqliteOutboxIntent& intent,
           const std::pair<std::string_view, std::string_view>& candidate) {
            return std::pair<std::string_view, std::string_view>{
                       intent.destination_device_id, intent.operation_id} <
                   candidate;
        });
    if (found == outbox.end() ||
        found->destination_device_id != destination_device_id ||
        found->operation_id != operation_id) {
        return outbox.end();
    }
    return found;
}



[[nodiscard]] std::vector<std::string> validate_destinations_or_throw(
    std::span<const std::string> destinations,
    const std::string& local_device_id,
    const std::string& label) {
    std::vector<std::string> canonical(destinations.begin(), destinations.end());
    for (const std::string& destination : canonical) {
        if (!sync_id_is_valid(destination)) {
            throw std::invalid_argument(label + " destination id is invalid");
        }
        if (destination == local_device_id) {
            throw std::invalid_argument(
                label + " refuses a self-directed outbox intent");
        }
    }
    std::sort(canonical.begin(), canonical.end());
    if (std::adjacent_find(canonical.begin(), canonical.end()) !=
        canonical.end()) {
        throw std::invalid_argument(
            label + " destination list contains a duplicate");
    }
    return canonical;
}

void require_outbox_capacity_or_throw(
    const LoadedState& state,
    const std::vector<std::string>& destinations,
    const std::string& label) {
    const std::uint64_t added_count = size_to_u64_or_throw(
        destinations.size(), label + " destination count");
    const std::uint64_t prospective_count = checked_add_or_throw(
        state.meta.outbox_intent_count, added_count,
        label + " outbox intent count");
    if (prospective_count > state.meta.limits.max_outbox_intents) {
        throw std::length_error(
            label + " outbox intent capacity would be exceeded");
    }
    std::uint64_t added_bytes = 0;
    for (const std::string& destination : destinations) {
        added_bytes = checked_add_or_throw(
            added_bytes,
            size_to_u64_or_throw(destination.size(), label + " destination bytes"),
            label + " destination bytes");
    }
    const std::uint64_t prospective_bytes = checked_add_or_throw(
        state.meta.outbox_destination_bytes, added_bytes,
        label + " outbox destination bytes");
    if (prospective_bytes >
        state.meta.limits.max_outbox_destination_bytes) {
        throw std::length_error(
            label + " outbox destination-byte capacity would be exceeded");
    }
}

void require_write_authority_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    auto borrow = db.borrow();
    if (!transaction.authorizes_write(borrow.get())) {
        throw std::logic_error(
            label + " typed transaction did not mint write authority");
    }
}

void require_snapshot_authority_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    auto borrow = db.borrow();
    if (!transaction.authorizes_snapshot(borrow.get())) {
        throw std::logic_error(
            label + " typed transaction did not pin snapshot authority");
    }
}

[[nodiscard]] SyncReplicaSqliteSnapshot snapshot_from_loaded(
    const LoadedState& loaded) {
    SyncReplicaSqliteSnapshot snapshot;
    snapshot.durable = loaded.model.durable_state();
    snapshot.limits = loaded.meta.limits;
    snapshot.database_incarnation_sha256 =
        loaded.meta.database_incarnation_sha256;
    snapshot.database_recovery_epoch = loaded.meta.database_recovery_epoch;
    snapshot.state_generation = loaded.meta.state_generation;
    snapshot.policy_generation = loaded.meta.policy_generation;
    snapshot.outbox = loaded.outbox;
    snapshot.outbox_clock_state = loaded.outbox_clock.state;
    snapshot.outbox_time_high_water_epoch =
        loaded.outbox_clock.state.high_water_epoch;
    snapshot.outbox_clock_digest = loaded.outbox_clock.clock_digest;
    snapshot.local_operation_digest = loaded.meta.local_operation_digest;
    snapshot.operation_set_digest = loaded.meta.operation_set_digest;
    snapshot.evidence_set_digest = loaded.meta.evidence_set_digest;
    snapshot.visible_path_count = loaded.meta.visible_path_count;
    snapshot.visible_state_digest = loaded.meta.visible_state_digest;
    snapshot.outbox_digest = loaded.meta.outbox_digest;
    snapshot.historical_version_pins = loaded.historical_version_pins;
    snapshot.historical_version_pin_count =
        loaded.meta.historical_version_pin_count;
    snapshot.historical_version_pin_set_digest =
        loaded.meta.historical_version_pin_set_digest;
    snapshot.cutpoint_digest = loaded.meta.cutpoint_digest;
    return snapshot;
}

// SQLite executes connection-local TEMP triggers inside the caller's
// transaction. A trigger can therefore succeed while silently changing a row
// after the owner's insert/update statement. Reload the complete staged state
// through the independent restore path and compare it with the intended
// cutpoint before COMMIT. Any mismatch or restore failure unwinds the typed
// transaction, preventing a corrupted generation from being published.
void attest_staged_cutpoint_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaModel& expected_model,
    const DurableMeta& expected_meta,
    const DurableOutboxClock& expected_outbox_clock,
    const std::vector<SyncReplicaSqliteOutboxIntent>& expected_outbox,
    std::span<const std::string> expected_historical_version_pins,
    const std::string& label) {
    LoadedState observed = load_state_or_throw(
        db, folder_id, local_actor, label + " staged re-attestation");
    if (observed.meta != expected_meta ||
        observed.outbox_clock != expected_outbox_clock ||
        observed.model.durable_state() != expected_model.durable_state() ||
        observed.outbox != expected_outbox ||
        observed.historical_version_pins.size() !=
            expected_historical_version_pins.size() ||
        !std::equal(
            observed.historical_version_pins.begin(),
            observed.historical_version_pins.end(),
            expected_historical_version_pins.begin())) {
        throw std::runtime_error(
            label + " staged cutpoint does not match intended publication");
    }
    require_write_authority_or_throw(
        transaction, db, label + " staged authority");
}

void attest_and_commit_staged_cutpoint_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaModel& expected_model,
    const DurableMeta& expected_meta,
    const DurableOutboxClock& expected_outbox_clock,
    const std::vector<SyncReplicaSqliteOutboxIntent>& expected_outbox,
    std::span<const std::string> expected_historical_version_pins,
    const std::string& label) {
    attest_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, expected_model,
        expected_meta, expected_outbox_clock, expected_outbox,
        expected_historical_version_pins, label);
    transaction.commit();
}

[[nodiscard]] SyncReplicaOutboxClockObservationResult
publish_outbox_clock_observation_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    LoadedState& loaded,
    const SyncReplicaOutboxClockObservation& observation,
    const std::string& label) {
    const SyncReplicaOutboxClockObservationResult result =
        observe_sync_replica_outbox_clock_or_throw(
            loaded.outbox_clock.state, observation,
            outbox_clock_policy(loaded.meta.limits), label);
    if (result.changed) {
        const DurableOutboxClock previous = loaded.outbox_clock;
        loaded.outbox_clock = make_outbox_clock_or_throw(
            folder_id, local_actor, result.state,
            label + " durable clock state");
        update_outbox_clock_exact_or_throw(
            db, loaded.outbox_clock, previous, label);
    }
    require_write_authority_or_throw(
        transaction, db, label + " publication authority");
    return result;
}

[[nodiscard]] std::uint64_t
accept_outbox_clock_observation_or_commit_quarantine_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    LoadedState& loaded,
    const SyncReplicaOutboxClockObservation& observation,
    const std::string& label) {
    const SyncReplicaOutboxClockObservationResult result =
        publish_outbox_clock_observation_or_throw(
            transaction, db, folder_id, local_actor, loaded, observation,
            label);
    if (result.outcome == SyncReplicaOutboxClockObservationOutcome::Accepted) {
        return result.usable_epoch;
    }

    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, loaded.model, loaded.meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label + " quarantine publication");
    throw std::runtime_error(
        label + " clock is quarantined: " +
        std::string(sync_replica_outbox_clock_anomaly_name(
            loaded.outbox_clock.state.anomaly)));
}

void attest_and_commit_clock_observation_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const LoadedState& loaded,
    const std::string& label) {
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, loaded.model, loaded.meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label);
}

void publish_outbox_lease_update_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    LoadedState& loaded,
    SyncReplicaSqliteOutboxIntent& intent,
    const SyncReplicaOutboxLeaseState& previous,
    const std::string& label) {
    update_outbox_lease_exact_or_throw(db, intent, previous, label);
    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation, label + " state generation");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db, meta, label);
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label);
}

void migrate_prior_schema_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    LoadedState prior,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::string& label) {
    if (prior.meta.schema_version != kLegacySchemaVersion &&
        prior.meta.schema_version != kPreviousSchemaVersion &&
        prior.meta.schema_version != kClockSchemaVersion &&
        prior.meta.schema_version != kRetryProvenanceSchemaVersion &&
        prior.meta.schema_version != kRetentionRootSchemaVersion &&
        prior.meta.schema_version != kHistoricalPinSchemaVersion &&
        prior.meta.schema_version != kDatabaseLineageSchemaVersion &&
        prior.meta.schema_version != kVisiblePathSchemaVersion) {
        throw std::logic_error(
            label + " migration source is not schema v1 through v8");
    }
    const bool source_has_visible_path_projection =
        prior.meta.schema_version == kVisiblePathSchemaVersion;
    const bool source_has_database_lineage =
        prior.meta.schema_version == kDatabaseLineageSchemaVersion ||
        source_has_visible_path_projection;
    const bool source_has_historical_version_pins =
        prior.meta.schema_version == kHistoricalPinSchemaVersion ||
        source_has_database_lineage;
    if (!source_has_historical_version_pins &&
        !prior.historical_version_pins.empty()) {
        throw std::logic_error(
            label + " pre-v6 migration source unexpectedly has history pins");
    }
    const std::uint64_t generation = increment_or_throw(
        prior.meta.state_generation, label + " migration state generation");
    const std::string database_incarnation_sha256 =
        source_has_database_lineage
            ? prior.meta.database_incarnation_sha256
            : mint_database_incarnation_or_throw(
                  folder_id, local_actor, label + " migration");
    const std::uint64_t database_recovery_epoch =
        source_has_database_lineage
            ? prior.meta.database_recovery_epoch
            : 1U;

    // Keep canonical evidence and projections in place. Replace only the
    // meta/outbox protocol surfaces after exact prior-version restoration.
    if (prior.meta.schema_version == kPreviousSchemaVersion ||
        prior.meta.schema_version == kClockSchemaVersion ||
        prior.meta.schema_version == kRetryProvenanceSchemaVersion ||
        prior.meta.schema_version == kRetentionRootSchemaVersion ||
        prior.meta.schema_version == kHistoricalPinSchemaVersion ||
        prior.meta.schema_version == kDatabaseLineageSchemaVersion ||
        prior.meta.schema_version == kVisiblePathSchemaVersion) {
        sqlite_exec_or_throw(
            db, "DROP INDEX main.sync_replica_outbox_schedule;",
            label + " retire previous outbox schedule index");
    }
    std::string retire_sql =
        "DROP INDEX main.sync_replica_outbox_operation;"
        "DROP TABLE main.sync_replica_outbox;";
    if (prior.meta.schema_version == kClockSchemaVersion ||
        prior.meta.schema_version == kRetryProvenanceSchemaVersion ||
        prior.meta.schema_version == kRetentionRootSchemaVersion ||
        prior.meta.schema_version == kHistoricalPinSchemaVersion ||
        prior.meta.schema_version == kDatabaseLineageSchemaVersion ||
        prior.meta.schema_version == kVisiblePathSchemaVersion) {
        retire_sql += "DROP TABLE main.sync_replica_outbox_clock;";
    }
    retire_sql +=
        "DROP TABLE main.sync_replica_visible;"
        "DROP TABLE main.sync_replica_meta;";
    sqlite_exec_or_throw(db, retire_sql, label + " retire prior outbox schema");
    for (const SchemaDefinition& definition : kSchema) {
        const bool selected =
            definition.name == "sync_replica_meta" ||
            definition.name == "sync_replica_outbox" ||
            definition.name == "sync_replica_outbox_clock" ||
            definition.name == "sync_replica_outbox_operation" ||
            definition.name == "sync_replica_outbox_schedule" ||
            definition.name == "sync_replica_visible" ||
            definition.name == "sync_replica_visible_file_content" ||
            (definition.name == "sync_replica_operation_paths" &&
             !source_has_visible_path_projection) ||
            (definition.name == "sync_replica_operation_paths_path" &&
             !source_has_visible_path_projection) ||
            (definition.name == "sync_replica_parent_edges_parent" &&
             !source_has_visible_path_projection) ||
            (definition.name == "sync_replica_history_pins" &&
             !source_has_historical_version_pins);
        if (selected) {
            sqlite_exec_or_throw(
                db, create_statement(definition),
                label + " create " + std::string(definition.name));
        }
    }
    verify_schema_or_throw(db, label + " migrated schema");
    const std::vector<SyncReplicaOperation> migration_operations =
        prior.model.all_evidence_operations();
    if (!source_has_visible_path_projection) {
        insert_operation_path_rows_or_throw(
            db, migration_operations, label + " migrated");
    }
    rewrite_projection_or_throw(
        db, prior.model, prior.persisted_states,
        label + " migrated visible projection");

    const DurableMeta meta = meta_from_state_or_throw(
        prior.model, database_incarnation_sha256, database_recovery_epoch,
        prior.meta.limits, generation, prior.meta.policy_generation,
        prior.outbox, prior.historical_version_pins);
    insert_meta_row_or_throw(db, meta, label + " migrated");
    insert_outbox_intents_or_throw(db, prior.outbox, label + " migrated");
    insert_outbox_clock_or_throw(
        db, prior.outbox_clock, label + " migrated");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, prior.model, meta,
        prior.outbox_clock, prior.outbox, prior.historical_version_pins,
        label + " migration publication");
}

[[nodiscard]] std::string local_publication_cutpoint_base_digest_or_throw(
    const DurableMeta& meta,
    std::string_view canonical_path,
    const TargetedPathHistoryCutpoint& path_history,
    std::span<const std::string> visible_operation_ids) {
    if (meta.schema_version != kSchemaVersion ||
        !is_lowercase_sha256_hex(meta.database_incarnation_sha256) ||
        meta.database_recovery_epoch == 0U ||
        !is_lowercase_sha256_hex(meta.local_operation_digest) ||
        !is_lowercase_sha256_hex(path_history.digest)) {
        throw std::invalid_argument(
            "sync replica targeted local publication cutpoint input is invalid");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-local-publication-cutpoint-base-v4");
    digest.update(u64_be(meta.schema_version));
    append_framed(digest, meta.database_incarnation_sha256);
    digest.update(u64_be(meta.database_recovery_epoch));
    append_framed(digest, meta.folder_id);
    append_framed(digest, meta.local_actor.device_id);
    digest.update(u64_be(meta.local_actor.epoch));
    digest.update(u64_be(meta.last_local_counter));
    digest.update(u64_be(meta.policy_generation));
    digest.update(meta.local_actor_compromised ? std::string_view("1")
                                               : std::string_view("0"));
    append_framed(digest, meta.local_operation_digest);
    append_framed(digest, canonical_path);
    digest.update(u64_be(path_history.retained_operation_count));
    digest.update(u64_be(path_history.canonical_bytes_observed));
    append_framed(digest, path_history.digest);
    digest.update(u64_be(size_to_u64_or_throw(
        visible_operation_ids.size(),
        "sync replica targeted local publication visible count")));
    for (const std::string& operation_id : visible_operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                "sync replica targeted local publication visible identity is invalid");
        }
        append_framed(digest, operation_id);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string seal_prepared_local_publication_or_throw(
    std::string_view base_digest,
    const SyncReplicaOperation& operation,
    std::span<const std::string> observed_visible_operation_ids) {
    if (!is_lowercase_sha256_hex(base_digest) ||
        !is_lowercase_sha256_hex(operation.operation_id)) {
        throw std::invalid_argument(
            "sync replica prepared local publication seal input is invalid");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-prepared-local-publication-seal-v2");
    append_framed(digest, base_digest);
    append_framed(digest, operation.operation_id);
    digest.update(u64_be(static_cast<std::uint64_t>(
        observed_visible_operation_ids.size())));
    for (const std::string& operation_id :
         observed_visible_operation_ids) {
        append_framed(digest, operation_id);
    }
    return digest.finish_hex();
}

struct LocalPublicationCommitCutpoint final {
    std::uint64_t state_generation = 0;
    std::string cutpoint_digest;
};

[[nodiscard]] LocalPublicationCommitCutpoint
persist_staged_local_publications_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    LoadedState& loaded,
    std::span<const SyncReplicaOperation* const> operations,
    std::span<const std::string> destinations,
    std::uint64_t generation,
    const std::string& label) {
    if (operations.empty()) {
        throw std::logic_error(label + " has no staged local publications");
    }
    for (const SyncReplicaOperation* operation : operations) {
        if (operation == nullptr) {
            throw std::logic_error(label + " has a null staged publication");
        }
        const auto state = loaded.model.evidence_state(operation->operation_id);
        if (state != SyncReplicaEvidenceState::Active) {
            throw std::logic_error(label + " did not project active");
        }
    }

    if (!destinations.empty() &&
        operations.size() >
            std::numeric_limits<std::size_t>::max() / destinations.size()) {
        throw std::length_error(label + " outbox publication fanout overflow");
    }
    std::vector<SyncReplicaSqliteOutboxIntent> added;
    added.reserve(operations.size() * destinations.size());
    for (const SyncReplicaOperation* operation : operations) {
        for (const std::string& destination : destinations) {
            added.push_back(
                {destination, operation->operation_id, generation, {}});
        }
    }
    loaded.outbox.insert(
        loaded.outbox.end(), added.begin(), added.end());
    std::sort(
        loaded.outbox.begin(), loaded.outbox.end(),
        [](const auto& left, const auto& right) {
            return std::tie(left.destination_device_id, left.operation_id) <
                   std::tie(right.destination_device_id, right.operation_id);
        });

    for (const SyncReplicaOperation* operation : operations) {
        const auto state = loaded.model.evidence_state(operation->operation_id);
        insert_operation_rows_or_throw(
            db, *operation, *state, loaded.meta.limits.model, true, label);
    }
    insert_outbox_intents_or_throw(db, added, label);
    rewrite_projection_or_throw(
        db, loaded.model, loaded.persisted_states, label);
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db, meta, label);
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label);
    return {meta.state_generation, meta.cutpoint_digest};
}

[[nodiscard]] LocalPublicationCommitCutpoint
persist_staged_local_publication_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    LoadedState& loaded,
    const SyncReplicaOperation& operation,
    std::span<const std::string> destinations,
    std::uint64_t generation,
    const std::string& label) {
    const std::array<const SyncReplicaOperation*, 1U> publications{
        &operation};
    return persist_staged_local_publications_or_throw(
        transaction, db, folder_id, local_actor, loaded, publications,
        destinations, generation, label);
}

void validate_prepared_visible_operation_ids_or_throw(
    const std::vector<std::string>& operation_ids,
    const std::string& label) {
    for (const std::string& operation_id : operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id)) {
            throw std::invalid_argument(
                label + " observed path head is not a lowercase SHA-256 identity");
        }
    }
    if (!std::is_sorted(operation_ids.begin(), operation_ids.end()) ||
        std::adjacent_find(operation_ids.begin(), operation_ids.end()) !=
            operation_ids.end()) {
        throw std::invalid_argument(
            label + " observed path heads must be strictly sorted and unique");
    }
}

void validate_prepared_local_file_basics_or_throw(
    const SyncReplicaSqlitePreparedLocalFilePublication& prepared,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(
            prepared.expected_publication_cutpoint_digest)) {
        throw std::invalid_argument(
            label + " expected publication cutpoint digest is invalid");
    }
    validate_prepared_visible_operation_ids_or_throw(
        prepared.observed_visible_operation_ids, label);
    const SyncReplicaOperation& operation = prepared.operation;
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            label + " prepared operation is not a file publication");
    }
    if (operation.folder_id != folder_id || operation.dot.actor != local_actor) {
        throw std::invalid_argument(
            label + " prepared operation identity binding is invalid");
    }
    if (operation.dot.counter == 0U ||
        !is_lowercase_sha256_hex(operation.operation_id) ||
        !is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            label + " prepared operation identity is invalid");
    }
}

// Merge the exact operation derived by a prior pinned read into a newer model
// whose local minting authority and target-path heads are unchanged. Unrelated
// remote evidence may have arrived in the meantime. Re-deriving against that
// larger global frontier would change causal context and falsely make unrelated
// activity a publication conflict; rebuilding from durable bytes lets the
// reference model validate the exact prepared operation against the evidence
// superset without weakening local actor/counter authority.
[[nodiscard]] SyncReplicaModel stage_exact_prepared_local_operation_or_throw(
    const SyncReplicaModel& current,
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits,
    const std::string& label) {
    if (current.local_actor_compromised()) {
        throw std::runtime_error(
            label + " local actor epoch is compromised");
    }
    if (operation.folder_id != current.folder_id() ||
        operation.dot.actor != current.local_actor() ||
        current.last_local_counter() ==
            std::numeric_limits<std::uint64_t>::max() ||
        operation.dot.counter != current.last_local_counter() + 1U) {
        throw std::runtime_error(
            label + " prepared operation no longer owns the next local dot");
    }
    if (current.evidence_operation_by_id(operation.operation_id).has_value()) {
        throw std::logic_error(
            label + " prepared operation unexpectedly already exists");
    }

    SyncReplicaDurableState durable = current.durable_state();
    const auto insertion = std::lower_bound(
        durable.operations.begin(), durable.operations.end(),
        operation.operation_id,
        [](const SyncReplicaOperation& retained, std::string_view identity) {
            return retained.operation_id < identity;
        });
    if (insertion != durable.operations.end() &&
        insertion->operation_id == operation.operation_id) {
        throw std::logic_error(
            label + " prepared operation became a duplicate during staging");
    }
    durable.operations.insert(insertion, operation);
    durable.last_local_counter = operation.dot.counter;
    durable.local_operation_ids.push_back(operation.operation_id);

    SyncReplicaModel staged = SyncReplicaModel::restore_or_throw(
        std::move(durable), limits);
    const auto retained = staged.evidence_operation_by_id(operation.operation_id);
    if (!retained.has_value() || *retained != operation ||
        staged.evidence_state(operation.operation_id) !=
            SyncReplicaEvidenceState::Active ||
        staged.local_actor_compromised() ||
        staged.local_operation_ids().empty() ||
        staged.local_operation_ids().back() != operation.operation_id) {
        throw std::runtime_error(
            label +
            " exact prepared operation is not active under the current evidence superset");
    }
    return staged;
}

[[nodiscard]] SyncReplicaPathView sole_visible_path_view_or_throw(
    const SyncReplicaOperation& operation) {
    if (!is_lowercase_sha256_hex(operation.operation_id)) {
        throw std::invalid_argument(
            "sync replica sole-visible operation identity is invalid");
    }
    SyncReplicaPathView view;
    view.canonical_path = operation.canonical_path;
    view.visible_operation_ids = {operation.operation_id};
    view.primary_operation_id = operation.operation_id;
    view.primary_kind = operation.kind;
    return view;
}

[[nodiscard]] DurableMeta advance_meta_for_targeted_local_publication_or_throw(
    const DurableMeta& current,
    const SyncReplicaOperation& operation,
    const TargetedVisiblePathState& prior_visible,
    const std::string& label) {
    if (current.schema_version != kSchemaVersion ||
        operation.folder_id != current.folder_id ||
        operation.dot.actor != current.local_actor ||
        operation.dot.counter != current.last_local_counter + 1U ||
        current.local_actor_compromised || prior_visible.conflicted) {
        throw std::runtime_error(
            label + " targeted publication authority is inconsistent");
    }
    validate_sync_replica_operation_or_throw(
        operation, current.limits.model);
    const std::uint64_t canonical_size =
        sync_replica_operation_canonical_size_or_throw(
            operation, current.limits.model);
    const std::uint64_t context_count = size_to_u64_or_throw(
        operation.causal_context.size(), label + " context count");
    const std::uint64_t predecessor_count = size_to_u64_or_throw(
        operation.predecessor_operation_ids.size(),
        label + " predecessor count");

    DurableMeta next = current;
    next.last_local_counter = operation.dot.counter;
    next.state_generation = increment_or_throw(
        current.state_generation, label + " state generation");
    next.evidence_count = increment_or_throw(
        current.evidence_count, label + " evidence count");
    next.active_count = increment_or_throw(
        current.active_count, label + " active count");
    next.retained_canonical_bytes = checked_add_or_throw(
        current.retained_canonical_bytes, canonical_size,
        label + " retained canonical bytes");
    next.retained_context_entries = checked_add_or_throw(
        current.retained_context_entries, context_count,
        label + " retained context entries");
    next.retained_predecessor_ids = checked_add_or_throw(
        current.retained_predecessor_ids, predecessor_count,
        label + " retained predecessor IDs");
    if (next.evidence_count > current.limits.model.max_operations ||
        next.active_count > next.evidence_count ||
        next.retained_canonical_bytes >
            current.limits.model.max_retained_canonical_bytes ||
        next.retained_context_entries >
            current.limits.model.max_retained_context_entries ||
        next.retained_predecessor_ids >
            current.limits.model.max_retained_predecessor_ids) {
        throw std::length_error(
            label + " targeted publication exceeds retained evidence capacity");
    }

    next.local_operation_digest = local_operation_chain_advance_or_throw(
        current.local_operation_digest, operation.dot.counter,
        operation.operation_id);
    next.operation_set_digest = sync_replica_digest_accumulator_add_or_throw(
        current.operation_set_digest,
        sync_replica_active_operation_accumulator_element_digest_or_throw(
            operation.operation_id));
    next.evidence_set_digest = sync_replica_digest_accumulator_add_or_throw(
        current.evidence_set_digest,
        sync_replica_evidence_operation_accumulator_element_digest_or_throw(
            operation.operation_id));

    std::string visible_accumulator = current.visible_state_digest;
    if (prior_visible.sole_visible_operation.has_value()) {
        visible_accumulator =
            sync_replica_digest_accumulator_subtract_or_throw(
                visible_accumulator,
                sync_replica_visible_path_accumulator_element_digest_or_throw(
                    sole_visible_path_view_or_throw(
                        *prior_visible.sole_visible_operation)));
    } else {
        next.visible_path_count = increment_or_throw(
            current.visible_path_count, label + " visible path count");
    }
    visible_accumulator = sync_replica_digest_accumulator_add_or_throw(
        visible_accumulator,
        sync_replica_visible_path_accumulator_element_digest_or_throw(
            sole_visible_path_view_or_throw(operation)));
    next.visible_state_digest = std::move(visible_accumulator);
    next.cutpoint_digest = cutpoint_digest_or_throw(next);
    return next;
}

void rewrite_targeted_local_projection_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaOperation& operation,
    const TargetedVisiblePathState& prior_visible,
    const std::string& label) {
    SyncSqliteStmt head_delete = sqlite_prepare_or_throw(
        db,
        "DELETE FROM main.sync_replica_heads WHERE operation_id=?;",
        label + " predecessor head delete prepare");
    for (const std::string& predecessor_id :
         operation.predecessor_operation_ids) {
        sqlite_bind_text_or_throw(
            head_delete.stmt, 1, predecessor_id,
            label + " predecessor head bind");
        sqlite_step_done_or_throw(
            head_delete.stmt, label + " predecessor head delete");
        reset_statement_or_throw(
            head_delete.stmt, label + " predecessor head delete");
    }

    SyncSqliteStmt head_insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_heads(operation_id) VALUES(?);",
        label + " new head insert prepare");
    sqlite_bind_text_or_throw(
        head_insert.stmt, 1, operation.operation_id,
        label + " new head bind");
    sqlite_step_done_or_throw(
        head_insert.stmt, label + " new head insert");

    SyncSqliteStmt visible_delete = sqlite_prepare_or_throw(
        db,
        "DELETE FROM main.sync_replica_visible WHERE canonical_path=?;",
        label + " visible path delete prepare");
    sqlite_bind_text_or_throw(
        visible_delete.stmt, 1, operation.canonical_path,
        label + " visible path delete bind");
    sqlite_step_done_or_throw(
        visible_delete.stmt, label + " visible path delete");
    {
        auto borrow = db.borrow();
        const std::uint64_t changed = static_cast<std::uint64_t>(
            sqlite3_changes(borrow.get()));
        if (changed != size_to_u64_or_throw(
                prior_visible.visible_operation_ids.size(),
                label + " prior visible row count")) {
            throw std::runtime_error(
                label + " visible path changed during targeted publication");
        }
    }

    SyncSqliteStmt visible_insert = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_visible("
        "canonical_path,visible_ordinal,operation_id,is_primary,preserve_file,"
        "value_kind,size_bytes_be,content_sha256)"
        "VALUES(?,0,?,1,0,?,?,?);",
        label + " visible path insert prepare");
    sqlite_bind_text_or_throw(
        visible_insert.stmt, 1, operation.canonical_path,
        label + " visible path insert bind");
    sqlite_bind_text_or_throw(
        visible_insert.stmt, 2, operation.operation_id,
        label + " visible operation insert bind");
    sqlite_bind_u64_or_throw(
        visible_insert.stmt, 3,
        visible_value_kind_integer_or_throw(operation.kind, label),
        label + " visible value kind insert bind");
    bind_u64_be_or_throw(
        visible_insert.stmt, 4, operation.size_bytes,
        label + " visible size insert bind");
    sqlite_bind_text_or_throw(
        visible_insert.stmt, 5, operation.content_sha256,
        label + " visible content insert bind");
    sqlite_step_done_or_throw(
        visible_insert.stmt, label + " visible path insert");
}

void attest_targeted_local_publication_or_throw(
    SyncSqliteTransaction& transaction,
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaOperation& operation,
    const TargetedPathHistoryCutpoint& prior_path_history,
    const DurableMeta& expected_meta,
    const std::string& label) {
    verify_schema_or_throw(db, label + " targeted staged schema");
    require_foreign_keys_or_throw(db, label + " targeted staged foreign keys");
    require_no_temporary_triggers_or_throw(
        db, label + " targeted staged trigger fence");
    const DurableMeta observed_meta = read_meta_or_throw(
        db, kSchemaVersion, label + " targeted staged meta");
    if (observed_meta != expected_meta ||
        observed_meta.folder_id != folder_id ||
        observed_meta.local_actor != local_actor) {
        throw std::runtime_error(
            label + " targeted staged metadata mismatch");
    }

    const std::optional<StoredOperationRow> stored =
        read_exact_operation_row_or_none_or_throw(
            db, observed_meta, operation.operation_id,
            label + " targeted staged operation");
    const std::optional<std::string> indexed_path =
        read_exact_operation_path_or_none_or_throw(
            db, operation.operation_id,
            label + " targeted staged operation");
    if (!stored.has_value() || !indexed_path.has_value() ||
        stored->operation != operation ||
        stored->evidence_state != SyncReplicaEvidenceState::Active ||
        *indexed_path != operation.canonical_path ||
        !has_exact_local_operation_binding_or_throw(
            db, operation, label + " targeted staged operation")) {
        throw std::runtime_error(
            label + " targeted staged operation binding mismatch");
    }

    SyncSqliteStmt parents = sqlite_prepare_or_throw(
        db,
        "SELECT parent_ordinal,parent_operation_id "
        "FROM main.sync_replica_parent_edges "
        "WHERE child_operation_id=? ORDER BY parent_ordinal;",
        label + " targeted staged parent prepare");
    sqlite_bind_text_or_throw(
        parents.stmt, 1, operation.operation_id,
        label + " targeted staged parent bind");
    std::size_t parent_index = 0U;
    for (;;) {
        const int result = sqlite3_step(parents.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(parents.stmt), result,
                label + " targeted staged parent query");
        }
        if (parent_index >= operation.predecessor_operation_ids.size() ||
            sqlite_column_u64_or_throw(
                parents.stmt, 0,
                label + " targeted staged parent ordinal") != parent_index ||
            sqlite_column_text_or_throw(
                parents.stmt, 1, 64U,
                label + " targeted staged parent identity") !=
                operation.predecessor_operation_ids[parent_index]) {
            throw std::runtime_error(
                label + " targeted staged parent projection mismatch");
        }
        ++parent_index;
    }
    if (parent_index != operation.predecessor_operation_ids.size()) {
        throw std::runtime_error(
            label + " targeted staged parent projection is incomplete");
    }

    const auto require_head_presence = [&](
        const std::string& operation_id, bool expected_present,
        const std::string& stage) {
        SyncSqliteStmt head = sqlite_prepare_or_throw(
            db,
            "SELECT 1 FROM main.sync_replica_heads "
            "WHERE operation_id=? LIMIT 1;",
            label + " " + stage + " head prepare");
        sqlite_bind_text_or_throw(
            head.stmt, 1, operation_id,
            label + " " + stage + " head bind");
        const int result = sqlite3_step(head.stmt);
        if (result != SQLITE_ROW && result != SQLITE_DONE) {
            throw_sqlite_exception(
                sqlite3_db_handle(head.stmt), result,
                label + " " + stage + " head query");
        }
        const bool present = result == SQLITE_ROW;
        if (present) {
            require_done_or_throw(
                head.stmt, label + " " + stage + " head query");
        }
        if (present != expected_present) {
            throw std::runtime_error(
                label + " " + stage + " head projection mismatch");
        }
    };
    require_head_presence(operation.operation_id, true, "new");
    for (const std::string& predecessor_id :
         operation.predecessor_operation_ids) {
        require_head_presence(predecessor_id, false, "predecessor");
    }

    const TargetedVisiblePathState visible =
        read_targeted_visible_path_or_throw(
            db, observed_meta, operation.canonical_path,
            label + " targeted staged");
    if (visible.conflicted ||
        visible.visible_operation_ids !=
            std::vector<std::string>{operation.operation_id} ||
        !visible.sole_visible_operation.has_value() ||
        *visible.sole_visible_operation != operation) {
        throw std::runtime_error(
            label + " targeted staged visible projection mismatch");
    }
    const TargetedPathHistoryCutpoint path_history =
        read_targeted_path_history_cutpoint_or_throw(
            db, observed_meta, operation.canonical_path,
            label + " targeted staged");
    if (path_history.retained_operation_count !=
            increment_or_throw(
                prior_path_history.retained_operation_count,
                label + " targeted staged path history count") ||
        path_history.canonical_bytes_observed != checked_add_or_throw(
            prior_path_history.canonical_bytes_observed,
            sync_replica_operation_canonical_size_or_throw(
                operation, observed_meta.limits.model),
            label + " targeted staged path history bytes")) {
        throw std::runtime_error(
            label + " targeted staged path history mismatch");
    }
    if (has_retained_child_reference_or_throw(
            db, operation.operation_id,
            label + " targeted staged reverse dependency")) {
        throw std::runtime_error(
            label + " targeted staged operation unexpectedly has a retained child");
    }
    require_write_authority_or_throw(
        transaction, db, label + " targeted staged authority");
}


}  // namespace

void validate_sync_replica_sqlite_evidence_page_limits_or_throw(
    const SyncReplicaSqliteEvidencePageLimits& limits) {
    if (limits.max_operations == 0U || limits.max_canonical_bytes == 0U) {
        throw std::invalid_argument(
            "sync replica SQLite evidence page limits must be positive");
    }
    (void)u64_to_size_or_throw(
        limits.max_operations,
        "sync replica SQLite evidence page operation limit");
    (void)u64_to_size_or_throw(
        limits.max_canonical_bytes,
        "sync replica SQLite evidence page canonical byte limit");
}


void validate_sync_replica_sqlite_visible_file_candidate_page_limits_or_throw(
    const SyncReplicaSqliteVisibleFileCandidatePageLimits& limits) {
    if (limits.max_visible_paths == 0U ||
        limits.max_visible_paths >
            kSyncReplicaSqliteVisibleFileCandidateMaximumPaths ||
        limits.max_canonical_bytes == 0U ||
        limits.max_canonical_bytes >
            kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes) {
        throw std::invalid_argument(
            "sync replica SQLite visible-file candidate page limits are outside the product frontier");
    }
    (void)u64_to_size_or_throw(
        limits.max_visible_paths,
        "sync replica SQLite visible-file candidate path limit");
    (void)u64_to_size_or_throw(
        limits.max_canonical_bytes,
        "sync replica SQLite visible-file candidate canonical byte limit");
}

SyncReplicaSqliteSnapshot
inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica read-only SQLite inspection label must not be empty");
    }
    validate_owner_limits_or_throw(
        folder_id, local_actor, SyncReplicaSqliteOwnerLimits{}, label);
    {
        auto database = borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " read-only connection proof");
        if (sqlite3_db_readonly(database.get(), "main") != 1) {
            throw std::runtime_error(
                label + " requires a read-only main database connection");
        }
    }
    require_foreign_keys_or_throw(db, label);

    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedState loaded = load_state_or_throw(
        db, folder_id, local_actor, label + " snapshot");
    require_snapshot_authority_or_throw(
        transaction, db, label + " snapshot");
    SyncReplicaSqliteSnapshot snapshot = snapshot_from_loaded(loaded);
    transaction.commit();
    return snapshot;
}

SyncReplicaSqliteSnapshot
inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& binding,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica detached read-only SQLite inspection label must not be empty");
    }
    validate_owner_limits_or_throw(
        folder_id, local_actor, SyncReplicaSqliteOwnerLimits{}, label);
    require_foreign_keys_or_throw(db, label);

    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    attest_sync_replica_sqlite_deployment_binding_state_in_read_only_detached_image_or_throw(
        db, binding, transaction.authority(),
        label + " deployment binding");
    LoadedState loaded = load_state_or_throw(
        db, folder_id, local_actor, label + " snapshot");
    require_snapshot_authority_or_throw(
        transaction, db, label + " snapshot");
    SyncReplicaSqliteSnapshot snapshot = snapshot_from_loaded(loaded);
    transaction.commit();
    return snapshot;
}

SyncReplicaSqliteProjectionGuard::SyncReplicaSqliteProjectionGuard(
    std::unique_ptr<SyncSqliteTransaction> transaction,
    SyncReplicaSqliteSnapshot snapshot,
    std::string label)
    : transaction_(std::move(transaction)),
      snapshot_(std::move(snapshot)),
      label_(std::move(label)) {
    if (transaction_ == nullptr || !transaction_->active()) {
        throw std::invalid_argument(
            label_ + " projection guard requires a live transaction");
    }
}

bool SyncReplicaSqliteProjectionGuard::active() const noexcept {
    return transaction_ != nullptr && transaction_->active();
}

void SyncReplicaSqliteProjectionGuard::commit_or_throw() {
    if (!active()) {
        throw std::logic_error(
            label_ + " projection guard is not active");
    }
    transaction_->commit();
    transaction_.reset();
}

SyncReplicaSqliteOutboxDispatchGuard::
    SyncReplicaSqliteOutboxDispatchGuard(
        std::unique_ptr<SyncSqliteTransaction> transaction,
        SyncReplicaSqliteOutboxClaim claim,
        std::uint64_t observed_epoch,
        std::string label)
    : transaction_(std::move(transaction)),
      claim_(std::move(claim)),
      observed_epoch_(observed_epoch),
      label_(std::move(label)) {
    if (transaction_ == nullptr || !transaction_->active()) {
        throw std::invalid_argument(
            label_ + " outbox dispatch guard requires a live transaction");
    }
    if (observed_epoch_ == 0U) {
        throw std::invalid_argument(
            label_ + " outbox dispatch guard requires an owned epoch");
    }
    if (claim_.intent.operation_id != claim_.operation.operation_id ||
        claim_.intent.lease.claim_id.empty()) {
        throw std::invalid_argument(
            label_ + " outbox dispatch guard claim is inconsistent");
    }
}

bool SyncReplicaSqliteOutboxDispatchGuard::active() const noexcept {
    return transaction_ != nullptr && transaction_->active();
}

void SyncReplicaSqliteOutboxDispatchGuard::commit_or_throw() {
    if (!active()) {
        throw std::logic_error(
            label_ + " outbox dispatch guard is not active");
    }
    transaction_->commit();
    transaction_.reset();
}

SyncReplicaSqliteOwner::SyncReplicaSqliteOwner(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    SyncReplicaSqliteOwnerLimits initial_limits,
    std::string label,
    std::unique_ptr<SyncReplicaOutboxClockSource> clock_source)
    : db_(db),
      folder_id_(std::move(folder_id)),
      local_actor_(std::move(local_actor)),
      label_(std::move(label)),
      clock_source_(std::move(clock_source)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica SQLite owner label must not be empty");
    }
    if (!clock_source_) {
        clock_source_ = make_system_sync_replica_outbox_clock_source();
    }
    if (!clock_source_) {
        throw std::runtime_error(
            label_ + " could not create an outbox clock source");
    }
    validate_owner_limits_or_throw(
        folder_id_, local_actor_, initial_limits, label_);

    sqlite_exec_or_throw(
        db_, "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;",
        label_ + " connection hardening");
    require_foreign_keys_or_throw(db_, label_);

    SyncSqliteTransaction transaction(
        db_, label_ + " schema initialization",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " schema initialization");
    const auto observed = read_schema_objects_or_throw(db_, label_);
    if (observed.empty()) {
        for (const SchemaDefinition& definition : kSchema) {
            sqlite_exec_or_throw(
                db_, create_statement(definition),
                label_ + " create " + std::string(definition.name));
        }
        verify_schema_or_throw(db_, label_);
        const DurableMeta meta = insert_initial_meta_or_throw(
            db_, folder_id_, local_actor_, initial_limits, label_);
        const DurableOutboxClock outbox_clock = make_outbox_clock_or_throw(
            folder_id_, local_actor_, SyncReplicaOutboxClockState{},
            label_ + " initial outbox clock");
        insert_outbox_clock_or_throw(
            db_, outbox_clock, label_ + " initial");
        const SyncReplicaModel empty(
            folder_id_, local_actor_, initial_limits.model);
        attest_and_commit_staged_cutpoint_or_throw(
            transaction, db_, folder_id_, local_actor_, empty, meta,
            outbox_clock, {}, {}, label_ + " schema initialization");
    } else if (schema_matches(observed, kSchema)) {
        (void)load_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " existing database");
        require_write_authority_or_throw(
            transaction, db_, label_ + " existing database");
        transaction.commit();
    } else if (schema_matches(observed, kVisiblePathSchema)) {
        LoadedState visible_path = load_visible_path_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v8 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(visible_path), folder_id_,
            local_actor_, label_ + " schema v8 to v9");
    } else if (schema_matches(observed, kDatabaseLineageSchema)) {
        LoadedState database_lineage = load_database_lineage_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v7 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(database_lineage), folder_id_,
            local_actor_, label_ + " schema v7 to v9");
    } else if (schema_matches(observed, kHistoricalPinSchema)) {
        LoadedState historical_pin = load_historical_pin_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v6 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(historical_pin), folder_id_,
            local_actor_, label_ + " schema v6 to v9");
    } else if (schema_matches(observed, kLegacySchema)) {
        LoadedState legacy = load_legacy_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " legacy database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(legacy), folder_id_, local_actor_,
            label_ + " schema v1 to v9");
    } else if (schema_matches(observed, kPreviousSchema)) {
        LoadedState previous = load_previous_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " previous database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(previous), folder_id_, local_actor_,
            label_ + " schema v2 to v9");
    } else if (schema_matches(observed, kClockSchema)) {
        LoadedState clock = load_clock_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v3 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(clock), folder_id_, local_actor_,
            label_ + " schema v3 to v9");
    } else if (schema_matches(observed, kRetryProvenanceSchema)) {
        LoadedState retry = load_retry_provenance_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v4 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(retry), folder_id_, local_actor_,
            label_ + " schema v4 to v9");
    } else if (schema_matches(observed, kRetentionRootSchema)) {
        LoadedState retention_root = load_retention_root_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v5 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(retention_root), folder_id_,
            local_actor_, label_ + " schema v5 to v9");
    } else {
        throw std::runtime_error(
            label_ + " database does not match schema v9, exact rev1019 v8, "
                     "exact rev0980 v7, "
                     "exact rev0973 v6, "
                     "exact rev0874 v5, exact rev0873 v4, exact rev0872 v3, "
                     "exact rev0871 v2, or exact rev0869 v1");
    }

    // Constructor publication is withheld until every exact operation and
    // redundant projection row has been independently restored and attested.
    (void)snapshot_or_throw();
}

SyncReplicaSqliteSnapshot SyncReplicaSqliteOwner::snapshot_or_throw() {
    SyncSqliteTransaction transaction(
        db_, label_ + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " snapshot");
    // A deferred SQLite transaction acquires snapshot authority on its first
    // read, not at BEGIN. Verify the typed guard after the exact restore has
    // pinned that read view and before publishing any derived state.
    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " snapshot");
    SyncReplicaSqliteSnapshot snapshot = snapshot_from_loaded(loaded);
    transaction.commit();
    return snapshot;
}

SyncReplicaSqliteIdentityCutpoint
SyncReplicaSqliteOwner::identity_cutpoint_or_throw() {
    SyncSqliteTransaction transaction(
        db_, label_ + " identity cutpoint",
        SyncSqliteTransactionMode::Deferred);
    const DurableMeta meta = read_current_owner_meta_or_throw(
        db_, folder_id_, local_actor_, label_ + " identity cutpoint");
    SyncReplicaSqliteIdentityCutpoint cutpoint{
        meta.folder_id,
        meta.local_actor,
        meta.limits,
        meta.database_incarnation_sha256,
        meta.database_recovery_epoch,
    };
    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " identity cutpoint");
    transaction.commit();
    return cutpoint;
}

SyncReplicaSqliteTargetedPathCutpoint
SyncReplicaSqliteOwner::targeted_path_cutpoint_or_throw(
    std::string canonical_path,
    std::optional<std::string> retained_operation_id) {
    const SyncValidationResult path_validation =
        validate_sync_relative_path(canonical_path);
    if (!path_validation.ok) {
        throw std::invalid_argument(
            label_ + " targeted path is invalid: " +
            path_validation.reason);
    }
    if (retained_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*retained_operation_id)) {
        throw std::invalid_argument(
            label_ + " targeted retained operation identity is invalid");
    }

    SyncSqliteTransaction transaction(
        db_, label_ + " targeted path cutpoint",
        SyncSqliteTransactionMode::Deferred);
    // The targeted reader publishes current path-local authority, so it
    // re-attests the exact trigger-free schema, foreign-key mode, and typed
    // owner metadata in the same pinned read transaction. That fixed work is
    // independent of retained operation history.
    const DurableMeta meta = read_current_owner_meta_or_throw(
        db_, folder_id_, local_actor_,
        label_ + " targeted path cutpoint");

    struct VisibleRow final {
        std::uint64_t ordinal = 0U;
        std::string operation_id;
        bool is_primary = false;
        bool preserve_file = false;
    };
    std::array<VisibleRow, 2U> visible_rows;
    std::size_t visible_row_count = 0U;
    SyncSqliteStmt visible = sqlite_prepare_or_throw(
        db_,
        "SELECT visible_ordinal,operation_id,is_primary,preserve_file "
        "FROM main.sync_replica_visible WHERE canonical_path=? "
        "ORDER BY visible_ordinal LIMIT 2;",
        label_ + " targeted visible path prepare");
    sqlite_bind_text_or_throw(
        visible.stmt, 1, canonical_path,
        label_ + " targeted visible path bind");
    for (;;) {
        const int result = sqlite3_step(visible.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(visible.stmt), result,
                label_ + " targeted visible path query");
        }
        if (visible_row_count >= visible_rows.size()) {
            throw std::logic_error(
                label_ + " targeted visible path exceeded SQL limit");
        }
        VisibleRow& row = visible_rows[visible_row_count];
        row.ordinal = sqlite_column_u64_or_throw(
            visible.stmt, 0,
            label_ + " targeted visible ordinal");
        row.operation_id = sqlite_column_text_or_throw(
            visible.stmt, 1, 64U,
            label_ + " targeted visible operation identity");
        row.is_primary = sqlite_column_bool_or_throw(
            visible.stmt, 2,
            label_ + " targeted visible primary flag");
        row.preserve_file = sqlite_column_bool_or_throw(
            visible.stmt, 3,
            label_ + " targeted visible preservation flag");
        if (row.ordinal != visible_row_count ||
            !is_lowercase_sha256_hex(row.operation_id) ||
            (visible_row_count != 0U &&
             row.operation_id == visible_rows[0].operation_id)) {
            throw std::runtime_error(
                label_ + " targeted visible path row is noncanonical");
        }
        ++visible_row_count;
    }

    SyncReplicaSqliteTargetedPathCutpoint cutpoint;
    cutpoint.conflicted = visible_row_count > 1U;

    if (visible_row_count == 1U) {
        const VisibleRow& row = visible_rows[0];
        if (!row.is_primary || row.preserve_file) {
            throw std::runtime_error(
                label_ + " targeted sole-visible projection is malformed");
        }
        std::optional<StoredOperationRow> stored =
            read_exact_operation_row_or_none_or_throw(
                db_, meta, row.operation_id,
                label_ + " targeted sole-visible operation");
        if (!stored.has_value() ||
            stored->evidence_state != SyncReplicaEvidenceState::Active ||
            stored->operation.folder_id != folder_id_ ||
            stored->operation.canonical_path != canonical_path) {
            throw std::runtime_error(
                label_ +
                " targeted sole-visible projection disagrees with active evidence");
        }
        cutpoint.sole_visible_operation = std::move(stored->operation);
    } else if (visible_row_count > 1U) {
        cutpoint.bounded_conflict_visible_operations.reserve(
            visible_row_count);
        for (std::size_t index = 0U; index < visible_row_count; ++index) {
            const VisibleRow& row = visible_rows[index];
            std::optional<StoredOperationRow> stored =
                read_exact_operation_row_or_none_or_throw(
                    db_, meta, row.operation_id,
                    label_ + " targeted conflict operation");
            if (!stored.has_value() ||
                stored->evidence_state != SyncReplicaEvidenceState::Active ||
                stored->operation.folder_id != folder_id_ ||
                stored->operation.canonical_path != canonical_path) {
                throw std::runtime_error(
                    label_ +
                    " targeted conflict projection disagrees with active evidence");
            }
            cutpoint.bounded_conflict_visible_operations.push_back(
                std::move(stored->operation));
        }
    }

    if (retained_operation_id.has_value()) {
        if (cutpoint.sole_visible_operation.has_value() &&
            cutpoint.sole_visible_operation->operation_id ==
                *retained_operation_id) {
            cutpoint.requested_retained_operation_is_sole_visible = true;
        } else if (const auto found = std::find_if(
                       cutpoint.bounded_conflict_visible_operations.begin(),
                       cutpoint.bounded_conflict_visible_operations.end(),
                       [&](const SyncReplicaOperation& operation) {
                           return operation.operation_id ==
                               *retained_operation_id;
                       });
                   found !=
                       cutpoint.bounded_conflict_visible_operations.end()) {
            cutpoint.requested_retained_operation_bounded_conflict_index =
                static_cast<std::size_t>(std::distance(
                    cutpoint.bounded_conflict_visible_operations.begin(),
                    found));
        } else {
            std::optional<StoredOperationRow> retained =
                read_exact_operation_row_or_none_or_throw(
                    db_, meta, *retained_operation_id,
                    label_ + " targeted retained operation");
            if (retained.has_value()) {
                if (retained->operation.folder_id != folder_id_ ||
                    retained->operation.canonical_path != canonical_path) {
                    throw std::runtime_error(
                        label_ +
                        " targeted retained operation escaped its path or folder");
                }
                cutpoint.distinct_retained_operation =
                    std::move(retained->operation);
            }
        }
    }

    // The first metadata read pinned the deferred transaction. Re-prove the
    // typed snapshot capability only after every targeted row has been decoded
    // and before publishing the path-local result.
    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " targeted path cutpoint");
    transaction.commit();
    return cutpoint;
}

SyncReplicaSqliteVisibleFileContentCutpoint
SyncReplicaSqliteOwner::visible_file_content_cutpoint_or_throw(
    std::uint64_t size_bytes,
    std::string content_sha256) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            label_ + " visible content digest is invalid");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " visible content cutpoint",
        SyncSqliteTransactionMode::Deferred);
    const DurableMeta meta = read_current_owner_meta_or_throw(
        db_, folder_id_, local_actor_,
        label_ + " visible content cutpoint");
    SyncReplicaSqliteVisibleFileContentCutpoint cutpoint =
        read_visible_file_content_cutpoint_or_throw(
            db_, meta, size_bytes, content_sha256,
            label_ + " visible content cutpoint");
    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " visible content cutpoint");
    transaction.commit();
    return cutpoint;
}

SyncReplicaSqliteDatabaseRecoveryEpochResult
SyncReplicaSqliteOwner::advance_database_recovery_epoch_or_throw(
    std::string expected_database_incarnation_sha256,
    std::uint64_t expected_database_recovery_epoch,
    std::string expected_cutpoint_digest) {
    if (!is_lowercase_sha256_hex(expected_database_incarnation_sha256) ||
        expected_database_recovery_epoch == 0U ||
        !is_lowercase_sha256_hex(expected_cutpoint_digest)) {
        throw std::invalid_argument(
            label_ + " database recovery expectation is invalid");
    }

    SyncSqliteTransaction transaction(
        db_, label_ + " database recovery epoch advance",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " database recovery epoch advance");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_,
        label_ + " database recovery epoch advance");
    if (loaded.meta.database_incarnation_sha256 !=
            expected_database_incarnation_sha256 ||
        loaded.meta.database_recovery_epoch !=
            expected_database_recovery_epoch ||
        loaded.meta.cutpoint_digest != expected_cutpoint_digest) {
        throw std::runtime_error(
            label_ + " database recovery expectation is stale");
    }

    const std::uint64_t recovery_epoch = increment_or_throw(
        loaded.meta.database_recovery_epoch,
        label_ + " database recovery epoch");
    const std::uint64_t state_generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " database recovery state generation");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        recovery_epoch, loaded.meta.limits, state_generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(
        db_, meta, label_ + " database recovery epoch advance");

    // Materialize every owning result field before COMMIT. After SQLite has
    // published the new epoch, returning this result is a nothrow move rather
    // than an avoidable allocation that could report failure after success.
    SyncReplicaSqliteDatabaseRecoveryEpochResult result{
        meta.database_incarnation_sha256,
        expected_database_recovery_epoch,
        meta.database_recovery_epoch,
        meta.state_generation,
        meta.cutpoint_digest,
    };
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins,
        label_ + " database recovery epoch publication");
    return result;
}

SyncReplicaSqliteEvidencePage
SyncReplicaSqliteOwner::evidence_page_or_throw(
    std::optional<std::string> after_operation_id,
    std::optional<std::string> expected_source_evidence_set_digest,
    SyncReplicaSqliteEvidencePageLimits limits) {
    validate_sync_replica_sqlite_evidence_page_limits_or_throw(limits);
    if (after_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*after_operation_id)) {
        throw std::invalid_argument(
            label_ + " evidence page cursor is invalid");
    }
    if (expected_source_evidence_set_digest.has_value() &&
        !is_lowercase_sha256_hex(
            *expected_source_evidence_set_digest)) {
        throw std::invalid_argument(
            label_ + " evidence page source digest is invalid");
    }
    if (after_operation_id.has_value() &&
        !expected_source_evidence_set_digest.has_value()) {
        throw std::invalid_argument(
            label_ + " evidence page cursor lacks its source digest");
    }

    SyncSqliteTransaction transaction(
        db_, label_ + " evidence page", SyncSqliteTransactionMode::Deferred);
    const DurableMeta meta = read_current_owner_meta_or_throw(
        db_, folder_id_, local_actor_, label_ + " evidence page");

    SyncReplicaSqliteEvidencePage page;
    page.source_state_generation = meta.state_generation;
    page.source_evidence_count = meta.evidence_count;
    page.source_evidence_set_digest = meta.evidence_set_digest;

    if (expected_source_evidence_set_digest.has_value() &&
        *expected_source_evidence_set_digest != meta.evidence_set_digest) {
        page.disposition =
            SyncReplicaSqliteEvidencePageDisposition::SourceChanged;
        require_snapshot_authority_or_throw(
            transaction, db_, label_ + " evidence page");
        transaction.commit();
        return page;
    }

    if (after_operation_id.has_value()) {
        const std::optional<StoredOperationRow> cursor =
            read_exact_operation_row_or_none_or_throw(
                db_, meta, *after_operation_id,
                label_ + " evidence page cursor");
        if (!cursor.has_value()) {
            throw std::runtime_error(
                label_ + " evidence page cursor is absent from the pinned source digest");
        }
        page.next_after_operation_id = *after_operation_id;
    }

    const std::size_t maximum_operations = u64_to_size_or_throw(
        limits.max_operations,
        label_ + " evidence page operation limit");
    const std::uint64_t reserve_count = std::min<std::uint64_t>(
        limits.max_operations, meta.evidence_count);
    page.operations.reserve(u64_to_size_or_throw(
        reserve_count, label_ + " evidence page reserve count"));

    // Lowercase SHA-256 operation IDs sort after the empty first-page bound.
    // The primary-key range walk stops after the bounded page plus at most one
    // decoded lookahead row; it never reconstructs or sorts retained history.
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db_,
        "SELECT operation_id,canonical_bytes,canonical_size_be,"
        "context_count_be,predecessor_count_be,evidence_state "
        "FROM main.sync_replica_operations WHERE operation_id>? "
        "ORDER BY operation_id LIMIT ?;",
        label_ + " evidence page range prepare");
    const std::string lower_bound =
        after_operation_id.value_or(std::string{});
    sqlite_bind_text_or_throw(
        statement.stmt, 1, lower_bound,
        label_ + " evidence page range bind");
    sqlite_bind_u64_or_throw(
        statement.stmt, 2,
        checked_add_or_throw(
            limits.max_operations, 1U,
            label_ + " evidence page lookahead limit"),
        label_ + " evidence page range limit bind");
    std::string previous_operation_id = lower_bound;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label_ + " evidence page range query");
        }
        StoredOperationRow row = load_stored_operation_row_or_throw(
            statement.stmt, 0, meta.limits.model,
            label_ + " evidence page operation");
        if (row.operation.operation_id <= previous_operation_id) {
            throw std::runtime_error(
                label_ + " evidence page primary-key range is noncanonical");
        }
        previous_operation_id = row.operation.operation_id;

        if (page.operations.size() >= maximum_operations) {
            page.has_more = true;
            break;
        }
        const std::uint64_t canonical_bytes =
            sync_replica_operation_canonical_size_or_throw(
                row.operation, meta.limits.model);
        if (canonical_bytes >
            limits.max_canonical_bytes - page.canonical_bytes) {
            if (page.operations.empty()) {
                throw std::runtime_error(
                    label_ + " evidence page byte budget cannot represent one retained operation");
            }
            page.has_more = true;
            break;
        }
        page.canonical_bytes += canonical_bytes;
        page.next_after_operation_id = row.operation.operation_id;
        page.operations.push_back(std::move(row.operation));
    }

    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " evidence page");
    transaction.commit();
    return page;
}

SyncReplicaSqliteVisibleFileCandidatePage
SyncReplicaSqliteOwner::visible_file_candidate_page_or_throw(
    std::optional<std::string> after_canonical_path,
    std::optional<std::string> expected_source_visible_state_digest,
    SyncReplicaSqliteVisibleFileCandidatePageLimits limits) {
    validate_sync_replica_sqlite_visible_file_candidate_page_limits_or_throw(
        limits);
    if (after_canonical_path.has_value()) {
        const SyncValidationResult validation =
            validate_sync_relative_path(*after_canonical_path);
        if (!validation.ok) {
            throw std::invalid_argument(
                label_ + " visible-file candidate cursor is invalid: " +
                validation.reason);
        }
    }
    if (expected_source_visible_state_digest.has_value() &&
        !is_lowercase_sha256_hex(
            *expected_source_visible_state_digest)) {
        throw std::invalid_argument(
            label_ + " visible-file candidate source digest is invalid");
    }
    if (after_canonical_path.has_value() &&
        !expected_source_visible_state_digest.has_value()) {
        throw std::invalid_argument(
            label_ + " visible-file candidate cursor lacks its source digest");
    }

    SyncSqliteTransaction transaction(
        db_, label_ + " visible-file candidate page",
        SyncSqliteTransactionMode::Deferred);
    const DurableMeta meta = read_current_owner_meta_or_throw(
        db_, folder_id_, local_actor_,
        label_ + " visible-file candidate page");

    SyncReplicaSqliteVisibleFileCandidatePage page;
    page.source_state_generation = meta.state_generation;
    page.source_visible_path_count = meta.visible_path_count;
    page.source_visible_state_digest = meta.visible_state_digest;

    if (expected_source_visible_state_digest.has_value() &&
        *expected_source_visible_state_digest != meta.visible_state_digest) {
        page.disposition =
            SyncReplicaSqliteVisibleFileCandidatePageDisposition::SourceChanged;
        require_snapshot_authority_or_throw(
            transaction, db_, label_ + " visible-file candidate page");
        transaction.commit();
        return page;
    }

    if (after_canonical_path.has_value()) {
        SyncSqliteStmt cursor = sqlite_prepare_or_throw(
            db_,
            "SELECT operation_id FROM main.sync_replica_visible "
            "WHERE canonical_path=? AND is_primary=1 "
            "ORDER BY visible_ordinal LIMIT 2;",
            label_ + " visible-file candidate cursor prepare");
        sqlite_bind_text_or_throw(
            cursor.stmt, 1, *after_canonical_path,
            label_ + " visible-file candidate cursor bind");
        std::size_t primary_rows = 0U;
        for (;;) {
            const int result = sqlite3_step(cursor.stmt);
            if (result == SQLITE_DONE) break;
            if (result != SQLITE_ROW) {
                throw_sqlite_exception(
                    sqlite3_db_handle(cursor.stmt), result,
                    label_ + " visible-file candidate cursor query");
            }
            const std::string operation_id = sqlite_column_text_or_throw(
                cursor.stmt, 0, 64U,
                label_ + " visible-file candidate cursor operation");
            if (!is_lowercase_sha256_hex(operation_id)) {
                throw std::runtime_error(
                    label_ + " visible-file candidate cursor projection is noncanonical");
            }
            ++primary_rows;
        }
        if (primary_rows != 1U) {
            throw std::runtime_error(
                label_ + " visible-file candidate cursor is absent from the pinned source digest");
        }
        page.next_after_canonical_path = *after_canonical_path;
    }

    const std::size_t maximum_visible_paths = u64_to_size_or_throw(
        limits.max_visible_paths,
        label_ + " visible-file candidate path limit");
    const std::uint64_t reserve_count = std::min<std::uint64_t>(
        limits.max_visible_paths, meta.visible_path_count);
    page.file_operations.reserve(u64_to_size_or_throw(
        reserve_count,
        label_ + " visible-file candidate reserve count"));

    // One primary row represents each visible path. The join is a bounded
    // canonical-path range walk over the already materialized projection; it
    // neither sorts nor reconstructs the retained causal graph.
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db_,
        "SELECT v.canonical_path,v.visible_ordinal,v.operation_id,"
        "v.preserve_file,o.operation_id,o.canonical_bytes,"
        "o.canonical_size_be,o.context_count_be,o.predecessor_count_be,"
        "o.evidence_state FROM main.sync_replica_visible AS v "
        "JOIN main.sync_replica_operations AS o "
        "ON o.operation_id=v.operation_id "
        "WHERE v.canonical_path>? AND v.is_primary=1 "
        "ORDER BY v.canonical_path LIMIT ?;",
        label_ + " visible-file candidate range prepare");
    const std::string lower_bound =
        after_canonical_path.value_or(std::string{});
    sqlite_bind_text_or_throw(
        statement.stmt, 1, lower_bound,
        label_ + " visible-file candidate range bind");
    sqlite_bind_u64_or_throw(
        statement.stmt, 2,
        checked_add_or_throw(
            limits.max_visible_paths, 1U,
            label_ + " visible-file candidate lookahead limit"),
        label_ + " visible-file candidate range limit bind");

    std::string previous_canonical_path = lower_bound;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label_ + " visible-file candidate range query");
        }
        const std::string canonical_path = sqlite_column_text_or_throw(
            statement.stmt, 0, kSyncManifestRelativePathMaxBytes,
            label_ + " visible-file candidate path");
        const std::uint64_t visible_ordinal = sqlite_column_u64_or_throw(
            statement.stmt, 1,
            label_ + " visible-file candidate ordinal");
        const std::string visible_operation_id = sqlite_column_text_or_throw(
            statement.stmt, 2, 64U,
            label_ + " visible-file candidate visible operation");
        const bool preserve_file = sqlite_column_bool_or_throw(
            statement.stmt, 3,
            label_ + " visible-file candidate preservation flag");
        if (canonical_path <= previous_canonical_path ||
            !is_lowercase_sha256_hex(visible_operation_id) ||
            preserve_file) {
            throw std::runtime_error(
                label_ + " visible-file candidate primary projection is noncanonical");
        }
        previous_canonical_path = canonical_path;

        if (page.scanned_visible_paths >=
            static_cast<std::uint64_t>(maximum_visible_paths)) {
            page.has_more = true;
            break;
        }

        StoredOperationRow row = load_stored_operation_row_or_throw(
            statement.stmt, 4, meta.limits.model,
            label_ + " visible-file candidate operation");
        if (visible_ordinal >= meta.evidence_count ||
            row.operation.operation_id != visible_operation_id ||
            row.operation.folder_id != folder_id_ ||
            row.operation.canonical_path != canonical_path ||
            row.evidence_state != SyncReplicaEvidenceState::Active) {
            throw std::runtime_error(
                label_ + " visible-file candidate projection disagrees with active evidence");
        }
        const std::uint64_t canonical_bytes =
            sync_replica_operation_canonical_size_or_throw(
                row.operation, meta.limits.model);
        if (canonical_bytes >
            limits.max_canonical_bytes - page.canonical_bytes) {
            if (page.scanned_visible_paths == 0U) {
                throw std::runtime_error(
                    label_ + " visible-file candidate byte budget cannot represent one primary operation");
            }
            page.has_more = true;
            break;
        }
        page.canonical_bytes += canonical_bytes;
        page.scanned_visible_paths = increment_or_throw(
            page.scanned_visible_paths,
            label_ + " visible-file candidate scanned path count");
        page.next_after_canonical_path = canonical_path;
        if (row.operation.kind == SyncReplicaValueKind::File) {
            page.file_operations.push_back(std::move(row.operation));
        }
    }

    require_snapshot_authority_or_throw(
        transaction, db_, label_ + " visible-file candidate page");
    transaction.commit();
    return page;
}

SyncReplicaSqliteHistoricalVersionPinResult
SyncReplicaSqliteOwner::pin_historical_version_or_throw(
    std::string operation_id) {
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            label_ + " historical-version pin operation ID is invalid");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " historical-version pin",
        SyncSqliteTransactionMode::Immediate);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " historical-version pin");
    require_write_authority_or_throw(
        transaction, db_, label_ + " historical-version pin");

    const std::optional<SyncReplicaOperation> operation =
        loaded.model.evidence_operation_by_id(operation_id);
    if (!operation.has_value() ||
        operation->kind != SyncReplicaValueKind::File) {
        throw std::runtime_error(
            label_ + " historical-version pin requires one retained file operation");
    }
    const auto position = std::lower_bound(
        loaded.historical_version_pins.begin(),
        loaded.historical_version_pins.end(), operation_id);
    if (position != loaded.historical_version_pins.end() &&
        *position == operation_id) {
        transaction.commit();
        return {
            SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyPinned,
            std::move(operation_id), loaded.meta.state_generation,
            loaded.meta.historical_version_pin_count,
            loaded.meta.historical_version_pin_set_digest};
    }

    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db_,
        "INSERT INTO main.sync_replica_history_pins(operation_id) VALUES(?);",
        label_ + " historical-version pin insert prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, operation_id,
        label_ + " historical-version pin bind operation ID");
    sqlite_step_done_or_throw(
        statement.stmt, label_ + " historical-version pin insert");
    {
        auto borrow = db_.borrow();
        if (sqlite3_changes(borrow.get()) != 1) {
            throw std::runtime_error(
                label_ +
                " historical-version pin insert did not affect one row");
        }
    }
    loaded.historical_version_pins.insert(position, operation_id);
    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " historical-version pin state generation");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, label_ + " historical-version pin");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins,
        label_ + " historical-version pin publication");
    return {
        SyncReplicaSqliteHistoricalVersionPinDisposition::Pinned,
        std::move(operation_id), meta.state_generation,
        meta.historical_version_pin_count,
        meta.historical_version_pin_set_digest};
}

SyncReplicaSqliteHistoricalVersionPinResult
SyncReplicaSqliteOwner::unpin_historical_version_or_throw(
    std::string operation_id) {
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            label_ + " historical-version unpin operation ID is invalid");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " historical-version unpin",
        SyncSqliteTransactionMode::Immediate);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " historical-version unpin");
    require_write_authority_or_throw(
        transaction, db_, label_ + " historical-version unpin");

    const auto position = std::lower_bound(
        loaded.historical_version_pins.begin(),
        loaded.historical_version_pins.end(), operation_id);
    if (position == loaded.historical_version_pins.end() ||
        *position != operation_id) {
        transaction.commit();
        return {
            SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyUnpinned,
            std::move(operation_id), loaded.meta.state_generation,
            loaded.meta.historical_version_pin_count,
            loaded.meta.historical_version_pin_set_digest};
    }

    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db_,
        "DELETE FROM main.sync_replica_history_pins WHERE operation_id=?;",
        label_ + " historical-version unpin delete prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, operation_id,
        label_ + " historical-version unpin bind operation ID");
    sqlite_step_done_or_throw(
        statement.stmt, label_ + " historical-version unpin delete");
    {
        auto borrow = db_.borrow();
        if (sqlite3_changes(borrow.get()) != 1) {
            throw std::runtime_error(
                label_ +
                " historical-version unpin delete did not affect one row");
        }
    }
    loaded.historical_version_pins.erase(position);
    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " historical-version unpin state generation");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, label_ + " historical-version unpin");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins,
        label_ + " historical-version unpin publication");
    return {
        SyncReplicaSqliteHistoricalVersionPinDisposition::Unpinned,
        std::move(operation_id), meta.state_generation,
        meta.historical_version_pin_count,
        meta.historical_version_pin_set_digest};
}

SyncReplicaOperation SyncReplicaSqliteOwner::publish_local_file_or_throw(
    std::string canonical_path,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256), std::nullopt,
        LocalPublicationPurpose::Ordinary, {});
}

SyncReplicaOperation
SyncReplicaSqliteOwner::publish_local_file_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            observed_visible_operation_ids.begin(),
            observed_visible_operation_ids.end()),
        LocalPublicationPurpose::Ordinary, {});
}

SyncReplicaSqlitePreparedLocalFilePublication
SyncReplicaSqliteOwner::prepare_local_file_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    const std::string operation_label =
        label_ + " targeted prepared observed local file publication";
    std::vector<std::string> observed_heads(
        observed_visible_operation_ids.begin(),
        observed_visible_operation_ids.end());
    validate_prepared_visible_operation_ids_or_throw(
        observed_heads, operation_label);
    const SyncValidationResult path_validation =
        validate_sync_relative_path(canonical_path);
    if (!path_validation.ok) {
        throw std::invalid_argument(
            operation_label + " path is invalid: " + path_validation.reason);
    }

    SyncSqliteTransaction transaction(
        db_, operation_label, SyncSqliteTransactionMode::Deferred);
    verify_schema_or_throw(db_, operation_label + " schema");
    require_foreign_keys_or_throw(db_, operation_label);
    const DurableMeta meta = read_meta_or_throw(
        db_, kSchemaVersion, operation_label);
    if (meta.folder_id != folder_id_ || meta.local_actor != local_actor_) {
        throw std::runtime_error(
            operation_label + " owner identity mismatch");
    }
    if (meta.local_actor_compromised) {
        throw std::runtime_error(
            operation_label + " local actor epoch is compromised");
    }

    const TargetedVisiblePathState visible =
        read_targeted_visible_path_or_throw(
            db_, meta, canonical_path, operation_label);
    if (visible.conflicted) {
        throw std::runtime_error(
            operation_label +
            " path has unresolved conflict; explicit resolution is required");
    }
    if (visible.visible_operation_ids != observed_heads) {
        throw std::runtime_error(
            operation_label +
            " observed path heads changed before local publication");
    }
    const TargetedPathHistoryCutpoint path_history =
        read_targeted_path_history_cutpoint_or_throw(
            db_, meta, canonical_path, operation_label);
    const std::vector<SyncReplicaOperation> causal_heads =
        read_active_causal_head_operations_or_throw(
            db_, meta, operation_label);

    SyncReplicaSqlitePreparedLocalFilePublication prepared;
    prepared.observed_state_generation = meta.state_generation;
    prepared.observed_visible_operation_ids = observed_heads;
    prepared.operation =
        make_sync_replica_local_operation_from_causal_heads_or_throw(
            folder_id_, local_actor_, meta.last_local_counter,
            canonical_path, SyncReplicaValueKind::File, size_bytes,
            std::move(content_sha256), causal_heads, meta.limits.model);
    // Preparation performs the exact prospective charge arithmetic as commit so
    // a catalog never persists work that was already impossible at its pinned
    // replica cutpoint. The value is discarded; no durable state is changed.
    (void)advance_meta_for_targeted_local_publication_or_throw(
        meta, prepared.operation, visible, operation_label);
    prepared.expected_publication_cutpoint_digest =
        seal_prepared_local_publication_or_throw(
            local_publication_cutpoint_base_digest_or_throw(
                meta, canonical_path, path_history,
                visible.visible_operation_ids),
            prepared.operation, prepared.observed_visible_operation_ids);

    require_snapshot_authority_or_throw(
        transaction, db_, operation_label);
    transaction.commit();
    return prepared;
}

SyncReplicaSqlitePreparedPublicationResult
SyncReplicaSqliteOwner::commit_prepared_local_file_or_throw(
    const SyncReplicaSqlitePreparedLocalFilePublication& prepared) {
    const std::string operation_label =
        label_ + " targeted prepared local file publication commit";
    validate_prepared_local_file_basics_or_throw(
        prepared, folder_id_, local_actor_, operation_label);

    SyncSqliteTransaction transaction(
        db_, operation_label, SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(transaction, db_, operation_label);
    verify_schema_or_throw(db_, operation_label + " schema");
    require_foreign_keys_or_throw(db_, operation_label);
    // The complete-model publication path historically detected connection-local
    // TEMP-trigger mutations by rebuilding every retained row. The targeted path
    // instead rejects executable TEMP schema before its first effect. Main-schema
    // triggers remain excluded by the exact sqlite_schema contract above.
    require_no_temporary_triggers_or_throw(db_, operation_label);
    const DurableMeta meta = read_meta_or_throw(
        db_, kSchemaVersion, operation_label);
    if (meta.folder_id != folder_id_ || meta.local_actor != local_actor_) {
        throw std::runtime_error(
            operation_label + " owner identity mismatch");
    }
    validate_sync_replica_operation_or_throw(
        prepared.operation, meta.limits.model);

    const std::optional<StoredOperationRow> existing =
        read_exact_operation_row_or_none_or_throw(
            db_, meta, prepared.operation.operation_id,
            operation_label + " existing operation");
    if (existing.has_value()) {
        const std::optional<std::string> indexed_path =
            read_exact_operation_path_or_none_or_throw(
                db_, prepared.operation.operation_id,
                operation_label + " existing operation");
        if (existing->operation != prepared.operation ||
            !indexed_path.has_value() ||
            *indexed_path != prepared.operation.canonical_path) {
            throw std::invalid_argument(
                operation_label +
                " operation ID names different retained evidence");
        }
        if (!has_exact_local_operation_binding_or_throw(
                db_, prepared.operation,
                operation_label + " existing operation")) {
            throw std::runtime_error(
                operation_label +
                " retained operation is not bound to local minting authority");
        }
        if (existing->evidence_state != SyncReplicaEvidenceState::Active ||
            meta.local_actor_compromised) {
            throw std::runtime_error(
                operation_label +
                " retained operation no longer carries active local minting authority");
        }
        const SyncReplicaSqlitePreparedPublicationResult result{
            SyncReplicaSqlitePreparedPublicationDisposition::AlreadyPublished,
            meta.state_generation,
            meta.cutpoint_digest};
        transaction.commit();
        return result;
    }

    const TargetedVisiblePathState visible =
        read_targeted_visible_path_or_throw(
            db_, meta, prepared.operation.canonical_path,
            operation_label);
    const TargetedPathHistoryCutpoint path_history =
        read_targeted_path_history_cutpoint_or_throw(
            db_, meta, prepared.operation.canonical_path,
            operation_label);
    const std::string current_publication_cutpoint =
        seal_prepared_local_publication_or_throw(
            local_publication_cutpoint_base_digest_or_throw(
                meta, prepared.operation.canonical_path, path_history,
                visible.visible_operation_ids),
            prepared.operation,
            prepared.observed_visible_operation_ids);
    if (visible.conflicted ||
        current_publication_cutpoint !=
            prepared.expected_publication_cutpoint_digest) {
        const SyncReplicaSqlitePreparedPublicationResult result{
            SyncReplicaSqlitePreparedPublicationDisposition::StaleCutpoint,
            meta.state_generation,
            meta.cutpoint_digest};
        transaction.commit();
        return result;
    }

    if (meta.local_actor_compromised ||
        meta.last_local_counter == std::numeric_limits<std::uint64_t>::max() ||
        prepared.operation.dot.counter != meta.last_local_counter + 1U) {
        throw std::runtime_error(
            operation_label +
            " prepared operation no longer owns the next local dot");
    }
    const std::vector<SyncReplicaOperation> predecessors =
        read_exact_active_predecessors_or_throw(
            db_, meta, prepared.operation, operation_label);
    const SyncReplicaOperation rederived =
        make_sync_replica_local_operation_from_causal_heads_or_throw(
            folder_id_, local_actor_, meta.last_local_counter,
            prepared.operation.canonical_path,
            prepared.operation.kind,
            prepared.operation.size_bytes,
            prepared.operation.content_sha256,
            predecessors, meta.limits.model);
    if (rederived != prepared.operation) {
        throw std::runtime_error(
            operation_label +
            " prepared operation no longer matches its active causal frontier");
    }

    // A retained pending operation may have guessed this future operation ID as
    // a missing predecessor. Inserting the ID could then activate an unrelated
    // dependency cascade. The indexed reverse-edge probe keeps the ordinary path
    // bounded; that rare adversarial case falls back to the complete reference
    // projector so every resulting evidence-state transition is still exact.
    if (has_retained_child_reference_or_throw(
            db_, prepared.operation.operation_id,
            operation_label + " prepublication")) {
        LoadedState loaded = load_state_or_throw(
            db_, folder_id_, local_actor_,
            operation_label + " dependency fallback");
        const std::string fallback_cutpoint =
            seal_prepared_local_publication_or_throw(
                local_publication_cutpoint_base_digest_or_throw(
                    loaded.meta, prepared.operation.canonical_path,
                    path_history, visible.visible_operation_ids),
                prepared.operation,
                prepared.observed_visible_operation_ids);
        if (fallback_cutpoint !=
            prepared.expected_publication_cutpoint_digest) {
            const SyncReplicaSqlitePreparedPublicationResult result{
                SyncReplicaSqlitePreparedPublicationDisposition::StaleCutpoint,
                loaded.meta.state_generation,
                loaded.meta.cutpoint_digest};
            transaction.commit();
            return result;
        }
        const std::uint64_t generation = increment_or_throw(
            loaded.meta.state_generation,
            operation_label + " fallback state generation");
        loaded.model = stage_exact_prepared_local_operation_or_throw(
            loaded.model, prepared.operation, loaded.meta.limits.model,
            operation_label + " dependency fallback");
        const LocalPublicationCommitCutpoint committed =
            persist_staged_local_publication_or_throw(
                transaction, db_, folder_id_, local_actor_, loaded,
                prepared.operation, std::span<const std::string>{}, generation,
                operation_label + " dependency fallback");
        return {
            SyncReplicaSqlitePreparedPublicationDisposition::Published,
            committed.state_generation,
            committed.cutpoint_digest};
    }

    const DurableMeta next_meta =
        advance_meta_for_targeted_local_publication_or_throw(
            meta, prepared.operation, visible, operation_label);
    insert_operation_rows_or_throw(
        db_, prepared.operation, SyncReplicaEvidenceState::Active,
        meta.limits.model, true, operation_label);
    rewrite_targeted_local_projection_or_throw(
        db_, prepared.operation, visible, operation_label);
    update_meta_or_throw(db_, next_meta, operation_label);
    attest_targeted_local_publication_or_throw(
        transaction, db_, folder_id_, local_actor_, prepared.operation,
        path_history, next_meta, operation_label);
    transaction.commit();
    return {
        SyncReplicaSqlitePreparedPublicationDisposition::Published,
        next_meta.state_generation,
        next_meta.cutpoint_digest};
}

SyncReplicaOperation
SyncReplicaSqliteOwner::resolve_published_local_file_conflict_or_throw(
    std::string canonical_path,
    std::span<const std::string> expected_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            expected_visible_operation_ids.begin(),
            expected_visible_operation_ids.end()),
        LocalPublicationPurpose::ConflictResolution, {});
}

SyncReplicaOperation SyncReplicaSqliteOwner::create_local_file_or_throw(
    std::string canonical_path,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const std::string> destination_device_ids) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256), std::nullopt,
        LocalPublicationPurpose::Ordinary, destination_device_ids);
}

SyncReplicaOperation
SyncReplicaSqliteOwner::create_local_file_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const std::string> destination_device_ids) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            observed_visible_operation_ids.begin(),
            observed_visible_operation_ids.end()),
        LocalPublicationPurpose::Ordinary, destination_device_ids);
}

SyncReplicaOperation
SyncReplicaSqliteOwner::resolve_local_file_conflict_or_throw(
    std::string canonical_path,
    std::span<const std::string> expected_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const std::string> destination_device_ids) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::File, size_bytes,
        std::move(content_sha256),
        std::vector<std::string>(
            expected_visible_operation_ids.begin(),
            expected_visible_operation_ids.end()),
        LocalPublicationPurpose::ConflictResolution,
        destination_device_ids);
}

SyncReplicaOperation SyncReplicaSqliteOwner::publish_local_tombstone_or_throw(
    std::string canonical_path) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::Tombstone, 0U, {},
        std::nullopt, LocalPublicationPurpose::Ordinary, {});
}

SyncReplicaOperation
SyncReplicaSqliteOwner::publish_local_tombstone_from_observed_heads_or_throw(
    std::string canonical_path,
    std::span<const std::string> observed_visible_operation_ids) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::Tombstone, 0U, {},
        std::vector<std::string>(
            observed_visible_operation_ids.begin(),
            observed_visible_operation_ids.end()),
        LocalPublicationPurpose::Ordinary, {});
}

SyncReplicaOperation SyncReplicaSqliteOwner::create_local_tombstone_or_throw(
    std::string canonical_path,
    std::span<const std::string> destination_device_ids) {
    return create_local_publication_or_throw(
        std::move(canonical_path), SyncReplicaValueKind::Tombstone, 0U, {},
        std::nullopt, LocalPublicationPurpose::Ordinary,
        destination_device_ids);
}

SyncReplicaSqliteLocalRenamePublicationResult
SyncReplicaSqliteOwner::
publish_local_identity_preserving_rename_from_observed_heads_or_throw(
    std::string source_canonical_path,
    std::span<const std::string> observed_source_visible_operation_ids,
    std::string destination_canonical_path,
    std::span<const std::string> observed_destination_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    const std::string operation_label =
        label_ + " local identity-preserving rename publication";
    if (source_canonical_path == destination_canonical_path) {
        throw std::invalid_argument(
            operation_label + " source and destination paths are identical");
    }
    const SyncValidationResult source_validation =
        validate_sync_relative_path(source_canonical_path);
    const SyncValidationResult destination_validation =
        validate_sync_relative_path(destination_canonical_path);
    if (!source_validation.ok || !destination_validation.ok) {
        throw std::invalid_argument(
            operation_label + " path is invalid: " +
            (!source_validation.ok ? source_validation.reason
                                   : destination_validation.reason));
    }
    std::vector<std::string> source_heads(
        observed_source_visible_operation_ids.begin(),
        observed_source_visible_operation_ids.end());
    std::vector<std::string> destination_heads(
        observed_destination_visible_operation_ids.begin(),
        observed_destination_visible_operation_ids.end());
    validate_prepared_visible_operation_ids_or_throw(
        source_heads, operation_label + " source");
    validate_prepared_visible_operation_ids_or_throw(
        destination_heads, operation_label + " destination");
    if (source_heads.size() != 1U) {
        throw std::invalid_argument(
            operation_label + " source must have exactly one visible head");
    }
    if (!destination_heads.empty()) {
        throw std::invalid_argument(
            operation_label + " destination must be causally absent");
    }
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            operation_label + " content digest is invalid");
    }

    SyncSqliteTransaction transaction(
        db_, operation_label, SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(transaction, db_, operation_label);
    verify_schema_or_throw(db_, operation_label + " schema");
    require_foreign_keys_or_throw(db_, operation_label);
    require_no_temporary_triggers_or_throw(db_, operation_label);
    const DurableMeta meta = read_meta_or_throw(
        db_, kSchemaVersion, operation_label);
    if (meta.folder_id != folder_id_ || meta.local_actor != local_actor_) {
        throw std::runtime_error(
            operation_label + " owner identity mismatch");
    }
    if (meta.local_actor_compromised) {
        throw std::runtime_error(
            operation_label + " local actor epoch is compromised");
    }
    if (meta.last_local_counter >
        std::numeric_limits<std::uint64_t>::max() - 2U) {
        throw std::overflow_error(
            operation_label +
            " requires two remaining local counters; rotate actor epoch");
    }
    if (meta.limits.model.max_operations < 2U ||
        meta.evidence_count > meta.limits.model.max_operations - 2U) {
        throw std::length_error(
            operation_label +
            " two-operation publication exceeds the retained operation limit");
    }

    const TargetedVisiblePathState source_visible =
        read_targeted_visible_path_or_throw(
            db_, meta, source_canonical_path, operation_label + " source");
    const TargetedVisiblePathState destination_visible =
        read_targeted_visible_path_or_throw(
            db_, meta, destination_canonical_path,
            operation_label + " destination");
    if (source_visible.conflicted ||
        source_visible.visible_operation_ids != source_heads ||
        !source_visible.sole_visible_operation.has_value()) {
        throw std::runtime_error(
            operation_label + " source path heads changed before publication");
    }
    if (destination_visible.conflicted ||
        destination_visible.visible_operation_ids != destination_heads ||
        destination_visible.sole_visible_operation.has_value()) {
        throw std::runtime_error(
            operation_label +
            " destination path heads changed before publication");
    }
    const SyncReplicaOperation& source_operation =
        *source_visible.sole_visible_operation;
    if (source_operation.operation_id != source_heads.front() ||
        source_operation.kind != SyncReplicaValueKind::File ||
        source_operation.canonical_path != source_canonical_path ||
        source_operation.size_bytes != size_bytes ||
        source_operation.content_sha256 != content_sha256) {
        throw std::runtime_error(
            operation_label +
            " source head does not match the exact retained file content");
    }
    verify_streamed_visible_projection_witness_or_throw(
        db_, meta, operation_label);
    require_unique_visible_file_content_source_or_throw(
        db_, meta, source_canonical_path, source_operation.operation_id,
        size_bytes, content_sha256, operation_label);

    const TargetedPathHistoryCutpoint source_history =
        read_targeted_path_history_cutpoint_or_throw(
            db_, meta, source_canonical_path, operation_label + " source");
    const TargetedPathHistoryCutpoint destination_history =
        read_targeted_path_history_cutpoint_or_throw(
            db_, meta, destination_canonical_path,
            operation_label + " destination");
    const std::vector<SyncReplicaOperation> causal_heads =
        read_active_causal_head_operations_or_throw(
            db_, meta, operation_label);

    const SyncReplicaOperation destination_file =
        make_sync_replica_local_operation_from_causal_heads_or_throw(
            folder_id_, local_actor_, meta.last_local_counter,
            destination_canonical_path, SyncReplicaValueKind::File,
            size_bytes, content_sha256, causal_heads, meta.limits.model);
    const SyncReplicaOperation source_tombstone =
        make_sync_replica_local_operation_from_causal_heads_or_throw(
            folder_id_, local_actor_, destination_file.dot.counter,
            source_canonical_path, SyncReplicaValueKind::Tombstone, 0U, {},
            std::span<const SyncReplicaOperation>(&destination_file, 1U),
            meta.limits.model);

    if (destination_file.dot.actor != local_actor_ ||
        source_tombstone.dot.actor != local_actor_ ||
        source_tombstone.dot.counter != destination_file.dot.counter + 1U ||
        source_tombstone.predecessor_operation_ids !=
            std::vector<std::string>{destination_file.operation_id} ||
        !sync_replica_context_covers_dot(
            destination_file.causal_context, source_operation.dot) ||
        !sync_replica_context_covers_dot(
            source_tombstone.causal_context, destination_file.dot)) {
        throw std::logic_error(
            operation_label + " did not derive the canonical rename pair");
    }
    if (has_retained_child_reference_or_throw(
            db_, destination_file.operation_id,
            operation_label + " destination prepublication") ||
        has_retained_child_reference_or_throw(
            db_, source_tombstone.operation_id,
            operation_label + " source prepublication")) {
        throw std::runtime_error(
            operation_label +
            " future operation identity already has retained dependency references");
    }
    if (read_exact_operation_row_or_none_or_throw(
            db_, meta, destination_file.operation_id,
            operation_label + " destination prepublication").has_value() ||
        read_exact_operation_row_or_none_or_throw(
            db_, meta, source_tombstone.operation_id,
            operation_label + " source prepublication").has_value()) {
        throw std::runtime_error(
            operation_label + " future operation identity is already retained");
    }

    const DurableMeta destination_meta =
        advance_meta_for_targeted_local_publication_or_throw(
            meta, destination_file, destination_visible,
            operation_label + " destination");
    DurableMeta final_meta =
        advance_meta_for_targeted_local_publication_or_throw(
            destination_meta, source_tombstone, source_visible,
            operation_label + " source");
    // The two immutable operations are one atomic local observation. They use
    // consecutive dots, but publish one externally visible durable generation.
    final_meta.state_generation = destination_meta.state_generation;
    final_meta.cutpoint_digest = cutpoint_digest_or_throw(final_meta);

    insert_operation_rows_or_throw(
        db_, destination_file, SyncReplicaEvidenceState::Active,
        meta.limits.model, true, operation_label + " destination");
    rewrite_targeted_local_projection_or_throw(
        db_, destination_file, destination_visible,
        operation_label + " destination");
    update_meta_or_throw(
        db_, destination_meta, operation_label + " destination");
    attest_targeted_local_publication_or_throw(
        transaction, db_, folder_id_, local_actor_, destination_file,
        destination_history, destination_meta,
        operation_label + " destination");

    insert_operation_rows_or_throw(
        db_, source_tombstone, SyncReplicaEvidenceState::Active,
        meta.limits.model, true, operation_label + " source");
    rewrite_targeted_local_projection_or_throw(
        db_, source_tombstone, source_visible,
        operation_label + " source");
    update_meta_or_throw(db_, final_meta, operation_label + " source");
    attest_targeted_local_publication_or_throw(
        transaction, db_, folder_id_, local_actor_, source_tombstone,
        source_history, final_meta, operation_label + " source");

    const TargetedVisiblePathState final_destination_visible =
        read_targeted_visible_path_or_throw(
            db_, final_meta, destination_canonical_path,
            operation_label + " final destination");
    const TargetedPathHistoryCutpoint final_destination_history =
        read_targeted_path_history_cutpoint_or_throw(
            db_, final_meta, destination_canonical_path,
            operation_label + " final destination");
    if (final_destination_visible.conflicted ||
        final_destination_visible.visible_operation_ids !=
            std::vector<std::string>{destination_file.operation_id} ||
        !final_destination_visible.sole_visible_operation.has_value() ||
        *final_destination_visible.sole_visible_operation != destination_file ||
        final_destination_history.retained_operation_count !=
            increment_or_throw(
                destination_history.retained_operation_count,
                operation_label + " final destination history count") ||
        final_destination_history.canonical_bytes_observed !=
            checked_add_or_throw(
                destination_history.canonical_bytes_observed,
                sync_replica_operation_canonical_size_or_throw(
                    destination_file, final_meta.limits.model),
                operation_label + " final destination history bytes")) {
        throw std::runtime_error(
            operation_label + " final destination reproof failed");
    }

    const SyncReplicaIdentityPreservingRename identity{
        source_canonical_path,
        destination_canonical_path,
        source_operation.operation_id,
        destination_file.operation_id,
        source_tombstone.operation_id,
        size_bytes,
        content_sha256};
    require_write_authority_or_throw(
        transaction, db_, operation_label + " final authority");
    transaction.commit();
    return {identity, destination_file, source_tombstone,
            final_meta.state_generation, final_meta.cutpoint_digest};
}

SyncReplicaOperation SyncReplicaSqliteOwner::create_local_publication_or_throw(
    std::string canonical_path,
    SyncReplicaValueKind kind,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::optional<std::vector<std::string>> expected_visible_operation_ids,
    LocalPublicationPurpose purpose,
    std::span<const std::string> destination_device_ids) {
    if (kind == SyncReplicaValueKind::Tombstone &&
        (purpose != LocalPublicationPurpose::Ordinary || size_bytes != 0U ||
         !content_sha256.empty())) {
        throw std::logic_error(
            label_ + " invalid local tombstone publication composition");
    }

    const std::string action =
        purpose == LocalPublicationPurpose::ConflictResolution
            ? "local file conflict resolution"
            : kind == SyncReplicaValueKind::Tombstone
                ? "local tombstone publication"
                : expected_visible_operation_ids.has_value()
                    ? "observed local file publication"
                    : "local file publication";
    const std::string operation_label = label_ + " " + action;

    SyncSqliteTransaction transaction(
        db_, operation_label, SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(transaction, db_, operation_label);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, operation_label);
    const std::vector<std::string> destinations =
        validate_destinations_or_throw(
            destination_device_ids, local_actor_.device_id,
            operation_label);
    require_outbox_capacity_or_throw(loaded, destinations, operation_label);

    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " state generation");
    SyncReplicaOperation operation;
    if (kind == SyncReplicaValueKind::Tombstone) {
        if (expected_visible_operation_ids.has_value()) {
            operation = loaded.model.
                create_local_tombstone_from_observed_heads_or_throw(
                    std::move(canonical_path),
                    expected_visible_operation_ids.value());
        } else {
            operation = loaded.model.create_local_tombstone_or_throw(
                std::move(canonical_path));
        }
    } else if (purpose == LocalPublicationPurpose::ConflictResolution) {
        if (!expected_visible_operation_ids.has_value()) {
            throw std::logic_error(
                label_ + " conflict resolution lost its expected path heads");
        }
        operation = loaded.model.resolve_local_file_conflict_or_throw(
            std::move(canonical_path), expected_visible_operation_ids.value(),
            size_bytes, std::move(content_sha256));
    } else if (expected_visible_operation_ids.has_value()) {
        operation = loaded.model.create_local_file_from_observed_heads_or_throw(
            std::move(canonical_path), expected_visible_operation_ids.value(),
            size_bytes, std::move(content_sha256));
    } else {
        operation = loaded.model.create_local_file_or_throw(
            std::move(canonical_path), size_bytes,
            std::move(content_sha256));
    }
    (void)persist_staged_local_publication_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded, operation,
        destinations, generation, operation_label);
    return operation;
}

SyncReplicaSqliteOutboxEnqueueResult
SyncReplicaSqliteOwner::enqueue_operation_for_destinations_or_throw(
    const std::string& operation_id,
    std::span<const std::string> destination_device_ids) {
    const std::string operation_label = label_ + " outbox derivation";
    if (!is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            operation_label + " operation identity is invalid");
    }
    const std::vector<std::string> destinations =
        validate_destinations_or_throw(
            destination_device_ids, local_actor_.device_id,
            operation_label);

    SyncSqliteTransaction transaction(
        db_, operation_label, SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(transaction, db_, operation_label);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, operation_label);
    const std::optional<SyncReplicaEvidenceState> evidence_state =
        loaded.model.evidence_state(operation_id);
    if (!evidence_state.has_value()) {
        throw std::invalid_argument(
            operation_label + " operation is not retained evidence");
    }
    if (*evidence_state != SyncReplicaEvidenceState::Active ||
        !loaded.model.operation_by_id(operation_id).has_value()) {
        throw std::invalid_argument(
            operation_label + " operation is not active evidence");
    }

    std::vector<std::string> missing_destinations;
    missing_destinations.reserve(destinations.size());
    std::uint64_t already_present = 0U;
    for (const std::string& destination : destinations) {
        if (find_outbox_intent(
                loaded.outbox, destination, operation_id) !=
            loaded.outbox.end()) {
            already_present = increment_or_throw(
                already_present,
                operation_label + " existing intent count");
        } else {
            missing_destinations.push_back(destination);
        }
    }

    if (missing_destinations.empty()) {
        const std::uint64_t generation = loaded.meta.state_generation;
        transaction.commit();
        return {0U, already_present, generation};
    }
    require_outbox_capacity_or_throw(
        loaded, missing_destinations, operation_label);
    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        operation_label + " state generation");

    std::vector<SyncReplicaSqliteOutboxIntent> added;
    added.reserve(missing_destinations.size());
    for (const std::string& destination : missing_destinations) {
        added.push_back({destination, operation_id, generation, {}});
    }
    insert_outbox_intents_or_throw(db_, added, operation_label);
    loaded.outbox.insert(
        loaded.outbox.end(), added.begin(), added.end());
    std::sort(
        loaded.outbox.begin(), loaded.outbox.end(),
        [](const auto& left, const auto& right) {
            return std::tie(left.destination_device_id, left.operation_id) <
                   std::tie(right.destination_device_id, right.operation_id);
        });

    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, operation_label);
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, operation_label);
    return {
        size_to_u64_or_throw(
            added.size(), operation_label + " added intent count"),
        already_present,
        generation};
}

SyncReplicaSqliteRemoteAdmissionResult
SyncReplicaSqliteOwner::accept_remote_with_cutpoint_or_throw(
    const SyncReplicaOperation& operation) {
    SyncSqliteTransaction transaction(
        db_, label_ + " remote admission",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " remote admission");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " remote admission");
    const SyncReplicaAdmission admission =
        loaded.model.accept_remote_or_throw(operation);
    const auto evidence_state =
        loaded.model.evidence_state(operation.operation_id);
    if (admission == SyncReplicaAdmission::Duplicate ||
        admission == SyncReplicaAdmission::CapacityBlocked) {
        if ((admission == SyncReplicaAdmission::Duplicate) !=
            evidence_state.has_value()) {
            throw std::logic_error(
                label_ + " remote admission no-op has inconsistent retained evidence");
        }
        SyncReplicaSqliteRemoteAdmissionResult result{
            admission,
            evidence_state,
            loaded.meta.state_generation,
            loaded.meta.cutpoint_digest,
        };
        transaction.commit();
        return result;
    }

    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " state generation");
    if (!evidence_state.has_value()) {
        throw std::logic_error(
            label_ + " admitted remote operation has no evidence state");
    }
    insert_operation_rows_or_throw(
        db_, operation, *evidence_state, loaded.meta.limits.model, false,
        label_ + " remote admission");
    rewrite_projection_or_throw(
        db_, loaded.model, loaded.persisted_states,
        label_ + " remote admission");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, label_ + " remote admission");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label_ + " remote admission");
    return {
        admission,
        evidence_state,
        generation,
        meta.cutpoint_digest,
    };
}

SyncReplicaAdmission SyncReplicaSqliteOwner::accept_remote_or_throw(
    const SyncReplicaOperation& operation) {
    return accept_remote_with_cutpoint_or_throw(operation).admission;
}

std::unique_ptr<SyncReplicaSqliteProjectionGuard>
SyncReplicaSqliteOwner::guard_visible_state_at_digest_or_throw(
    const std::string& expected_visible_state_digest) {
    if (!is_lowercase_sha256_hex(expected_visible_state_digest)) {
        throw std::invalid_argument(
            label_ + " projection guard visible-state digest is invalid");
    }

    auto transaction = std::make_unique<SyncSqliteTransaction>(
        db_, label_ + " visible projection guard",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        *transaction, db_, label_ + " visible projection guard");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " visible projection guard");
    SyncReplicaSqliteSnapshot snapshot = snapshot_from_loaded(loaded);
    if (snapshot.visible_state_digest != expected_visible_state_digest) {
        transaction->commit();
        return {};
    }

    return std::unique_ptr<SyncReplicaSqliteProjectionGuard>(
        new SyncReplicaSqliteProjectionGuard(
            std::move(transaction), std::move(snapshot),
            label_ + " visible projection guard"));
}

std::unique_ptr<SyncReplicaSqliteProjectionGuard>
SyncReplicaSqliteOwner::guard_unambiguous_file_primary_at_cutpoint_or_throw(
    const SyncReplicaOperation& operation,
    std::uint64_t expected_state_generation,
    const std::string& expected_cutpoint_digest) {
    if (expected_state_generation == 0U ||
        !is_lowercase_sha256_hex(expected_cutpoint_digest)) {
        throw std::invalid_argument(
            label_ + " projection guard expected cutpoint is invalid");
    }

    auto transaction = std::make_unique<SyncSqliteTransaction>(
        db_, label_ + " projection guard",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        *transaction, db_, label_ + " projection guard");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " projection guard");
    SyncReplicaSqliteSnapshot snapshot = snapshot_from_loaded(loaded);

    // The evidence receipt owns one exact admission cutpoint. Do not silently
    // upgrade it to a later state: an unrelated writer, retry transition, or
    // projection change requires a fresh duplicate admission/receipt cycle.
    if (snapshot.state_generation != expected_state_generation ||
        snapshot.cutpoint_digest != expected_cutpoint_digest) {
        transaction->commit();
        return {};
    }

    validate_sync_replica_operation_or_throw(
        operation, snapshot.limits.model);
    const std::optional<SyncReplicaOperation> retained =
        loaded.model.evidence_operation_by_id(operation.operation_id);
    if (!retained.has_value() || *retained != operation) {
        throw std::logic_error(
            label_ +
            " projection guard cutpoint lost exact operation evidence");
    }

    bool unambiguous_primary = false;
    if (operation.kind == SyncReplicaValueKind::File &&
        loaded.model.evidence_state(operation.operation_id) ==
            SyncReplicaEvidenceState::Active) {
        const std::optional<SyncReplicaPathView> view =
            loaded.model.visible_path(operation.canonical_path);
        unambiguous_primary =
            view.has_value() &&
            view->primary_operation_id == operation.operation_id &&
            view->primary_kind == SyncReplicaValueKind::File &&
            view->visible_operation_ids.size() == 1U &&
            view->preserved_file_operation_ids.empty();
    }
    if (!unambiguous_primary) {
        transaction->commit();
        return {};
    }

    return std::unique_ptr<SyncReplicaSqliteProjectionGuard>(
        new SyncReplicaSqliteProjectionGuard(
            std::move(transaction), std::move(snapshot),
            label_ + " projection guard"));
}

std::optional<SyncReplicaSqliteOutboxClaim>
SyncReplicaSqliteOwner::claim_next_outbox_or_throw(
    std::string worker_id,
    std::uint64_t lease_seconds,
    std::optional<std::string> destination_device_id,
    std::optional<SyncReplicaValueKind> operation_kind) {
    return claim_next_outbox_impl_or_throw(
        std::move(worker_id), lease_seconds,
        std::move(destination_device_id), operation_kind, nullptr,
        std::nullopt, std::nullopt);
}

std::optional<SyncReplicaSqliteOutboxClaim>
SyncReplicaSqliteOwner::claim_next_outbox_for_delivery_or_throw(
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaModelLimits& delivery_operation_limits,
    std::optional<std::string> destination_device_id,
    std::optional<SyncReplicaValueKind> operation_kind,
    std::optional<std::uint64_t> max_file_payload_bytes,
    std::optional<SyncReplicaFileContentInventory>
        available_file_content) {
    validate_sync_replica_model_limits_or_throw(delivery_operation_limits);
    return claim_next_outbox_impl_or_throw(
        std::move(worker_id), lease_seconds,
        std::move(destination_device_id), operation_kind,
        &delivery_operation_limits, max_file_payload_bytes,
        std::move(available_file_content));
}

std::optional<SyncReplicaSqliteOutboxClaim>
SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw(
    std::string worker_id,
    std::uint64_t lease_seconds,
    std::optional<std::string> destination_device_id,
    std::optional<SyncReplicaValueKind> operation_kind,
    const SyncReplicaModelLimits* delivery_operation_limits,
    std::optional<std::uint64_t> max_file_payload_bytes,
    std::optional<SyncReplicaFileContentInventory>
        available_file_content) {
    if (!sync_id_is_valid(worker_id)) {
        throw std::invalid_argument(
            label_ + " outbox claim worker identity is invalid");
    }
    if (destination_device_id.has_value() &&
        !sync_id_is_valid(*destination_device_id)) {
        throw std::invalid_argument(
            label_ + " outbox claim destination identity is invalid");
    }
    if (operation_kind.has_value() &&
        *operation_kind != SyncReplicaValueKind::File &&
        *operation_kind != SyncReplicaValueKind::Tombstone) {
        throw std::invalid_argument(
            label_ + " outbox claim operation kind is invalid");
    }
    if (max_file_payload_bytes.has_value() &&
        (*max_file_payload_bytes == 0U ||
         operation_kind != SyncReplicaValueKind::File)) {
        throw std::invalid_argument(
            label_ +
            " outbox claim file payload preflight requires a positive limit and File operation kind");
    }
    if (available_file_content.has_value() &&
        operation_kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            label_ +
            " outbox claim payload inventory requires File operation kind");
    }
    if (available_file_content.has_value()) {
        available_file_content->require_folder_or_throw(
            folder_id_, label_ + " outbox claim payload inventory");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label_ + " outbox claim lease_seconds must be in 1..86400");
    }

    // Entropy does not encode liveness authority and may be acquired before
    // waiting for SQLite's writer slot. Host time is intentionally sampled only
    // after BEGIN IMMEDIATE and complete-state restore: a pre-lock sample can
    // age past an expiry while an unrelated writer holds the database lock.
    const std::string claim_entropy =
        random_claim_entropy_or_throw(label_ + " outbox claim");
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox claim", SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox claim");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox claim");
    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox claim host clock observation");
    const std::uint64_t now_epoch =
        accept_outbox_clock_observation_or_commit_quarantine_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox claim time observation");
    if (lease_seconds >
        std::numeric_limits<std::uint64_t>::max() - now_epoch) {
        throw std::overflow_error(
            label_ + " outbox claim lease deadline overflows uint64_t");
    }

    std::span<const std::string> available_file_content_sha256s;
    if (available_file_content.has_value()) {
        available_file_content_sha256s =
            available_file_content->content_sha256s();
    }

    auto found = loaded.outbox.end();
    std::optional<SyncReplicaOperation> selected_operation;
    const auto precedes_for_claim = [](
        const SyncReplicaSqliteOutboxIntent& lhs,
        const SyncReplicaSqliteOutboxIntent& rhs) noexcept {
        if (lhs.enqueued_generation != rhs.enqueued_generation) {
            return lhs.enqueued_generation < rhs.enqueued_generation;
        }
        if (lhs.destination_device_id != rhs.destination_device_id) {
            return lhs.destination_device_id < rhs.destination_device_id;
        }
        return lhs.operation_id < rhs.operation_id;
    };
    for (auto candidate = loaded.outbox.begin();
         candidate != loaded.outbox.end(); ++candidate) {
        if (destination_device_id.has_value() &&
            candidate->destination_device_id != *destination_device_id) {
            continue;
        }
        if (!sync_replica_outbox_lease_is_claimable_at_or_throw(
                candidate->lease, now_epoch,
                label_ + " outbox claim candidate")) {
            continue;
        }
        const std::optional<SyncReplicaOperation> operation =
            loaded.model.evidence_operation_by_id(candidate->operation_id);
        if (!operation.has_value()) {
            throw std::logic_error(
                label_ +
                " claimable intent lost its canonical operation owner");
        }
        if (operation_kind.has_value() &&
            operation->kind != *operation_kind) {
            continue;
        }
        if (delivery_operation_limits != nullptr) {
            try {
                validate_sync_replica_operation_or_throw(
                    *operation, *delivery_operation_limits);
            } catch (...) {
                std::throw_with_nested(std::runtime_error(
                    label_ +
                    " ready matching outbox operation exceeds delivery wire policy before claim"));
            }
        }
        if (max_file_payload_bytes.has_value() &&
            operation->size_bytes > *max_file_payload_bytes) {
            throw std::runtime_error(
                label_ +
                " ready matching file operation exceeds delivery payload policy before claim");
        }
        if (available_file_content.has_value() &&
            !std::binary_search(
                available_file_content_sha256s.begin(),
                available_file_content_sha256s.end(),
                operation->content_sha256)) {
            continue;
        }
        if (found != loaded.outbox.end() &&
            !precedes_for_claim(*candidate, *found)) {
            continue;
        }
        found = candidate;
        selected_operation = operation;
    }
    if (found == loaded.outbox.end()) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox claim no-ready-intent");
        return std::nullopt;
    }

    if (!selected_operation.has_value()) {
        throw std::logic_error(
            label_ + " selected intent lost its canonical operation owner");
    }
    const SyncReplicaOutboxLeaseState previous = found->lease;
    found->lease = claim_sync_replica_outbox_lease_or_throw(
        previous, folder_id_, found->destination_device_id,
        found->operation_id, found->enqueued_generation,
        loaded.meta.cutpoint_digest, worker_id, now_epoch,
        lease_seconds, claim_entropy, label_ + " outbox claim");
    const SyncReplicaSqliteOutboxClaim claim{*found, *selected_operation};
    publish_outbox_lease_update_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded, *found,
        previous, label_ + " outbox claim");
    return claim;
}

SyncReplicaSqliteOutboxDispatchGuardResult
SyncReplicaSqliteOwner::guard_outbox_claim_for_dispatch_or_throw(
    const SyncReplicaSqliteOutboxClaim& expected_claim) {
    const SyncReplicaSqliteOutboxIntent& expected_intent =
        expected_claim.intent;
    if (!sync_id_is_valid(expected_intent.destination_device_id) ||
        !is_lowercase_sha256_hex(expected_intent.operation_id) ||
        expected_intent.enqueued_generation == 0U ||
        expected_intent.operation_id !=
            expected_claim.operation.operation_id) {
        throw std::invalid_argument(
            label_ + " outbox dispatch guard identity is invalid");
    }
    validate_sync_replica_outbox_lease_state_or_throw(
        expected_intent.lease,
        label_ + " outbox dispatch guard expected lease");
    if (expected_intent.lease.claim_id.empty()) {
        throw std::invalid_argument(
            label_ + " outbox dispatch guard requires an active claim");
    }

    auto transaction = std::make_unique<SyncSqliteTransaction>(
        db_, label_ + " outbox dispatch guard",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        *transaction, db_, label_ + " outbox dispatch guard");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox dispatch guard");
    auto found = find_outbox_intent(
        loaded.outbox, expected_intent.destination_device_id,
        expected_intent.operation_id);
    if (found == loaded.outbox.end()) {
        transaction->commit();
        return {
            SyncReplicaSqliteOutboxDispatchGuardDisposition::IntentMissing,
            {}};
    }
    if (found->lease.claim_id != expected_intent.lease.claim_id) {
        transaction->commit();
        return {
            SyncReplicaSqliteOutboxDispatchGuardDisposition::StaleClaim,
            {}};
    }

    // A valid heartbeat may extend the deadline without changing receipt
    // identity. Every other row field is exact attempt authority and must still
    // match the claim originally returned to the caller.
    SyncReplicaSqliteOutboxIntent expected_with_current_deadline =
        expected_intent;
    expected_with_current_deadline.lease.lease_expires_at_epoch =
        found->lease.lease_expires_at_epoch;
    if (*found != expected_with_current_deadline ||
        found->lease.lease_expires_at_epoch <
            expected_intent.lease.lease_expires_at_epoch) {
        throw std::runtime_error(
            label_ +
            " outbox dispatch guard found the exact claim row changed outside bounded renewal");
    }

    // Exact intent/claim identity precedes the liveness sample. A missing or
    // stale callback result has no authority to ratchet the durable clock.
    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox dispatch guard host clock observation");
    const std::uint64_t now_epoch =
        accept_outbox_clock_observation_or_commit_quarantine_or_throw(
            *transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox dispatch guard time observation");
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            found->lease, expected_intent.lease.claim_id, now_epoch,
            label_ + " outbox dispatch guard");
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::logic_error(
            label_ + " outbox dispatch guard lost exact claim authority");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        attest_and_commit_clock_observation_or_throw(
            *transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox dispatch guard expired claim");
        return {
            SyncReplicaSqliteOutboxDispatchGuardDisposition::ExpiredClaim,
            {}};
    }

    validate_sync_replica_operation_or_throw(
        expected_claim.operation, loaded.meta.limits.model);
    const std::optional<SyncReplicaOperation> retained =
        loaded.model.evidence_operation_by_id(expected_intent.operation_id);
    if (!retained.has_value() || *retained != expected_claim.operation) {
        throw std::runtime_error(
            label_ +
            " outbox dispatch guard lost exact canonical operation evidence");
    }

    // A clock update may have fired connection-local TEMP triggers. Re-enter
    // through the independent full restore path before this transaction escapes
    // as a capability. BEGIN IMMEDIATE then keeps the attested row stable until
    // the bounded frame construction commits or guard destruction rolls back.
    attest_staged_cutpoint_or_throw(
        *transaction, db_, folder_id_, local_actor_, loaded.model,
        loaded.meta, loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins,
        label_ + " outbox dispatch guard");
    SyncReplicaSqliteOutboxClaim current_claim{*found, *retained};
    return {
        SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired,
        std::unique_ptr<SyncReplicaSqliteOutboxDispatchGuard>(
            new SyncReplicaSqliteOutboxDispatchGuard(
                std::move(transaction), std::move(current_claim), now_epoch,
                label_ + " outbox dispatch guard"))};
}

SyncReplicaSqliteOutboxReceiptResult
SyncReplicaSqliteOwner::settle_outbox_or_throw(
    const std::string& destination_device_id,
    const std::string& operation_id,
    const std::string& claim_id) {
    if (!sync_id_is_valid(destination_device_id) ||
        !is_lowercase_sha256_hex(operation_id) ||
        !is_lowercase_sha256_hex(claim_id)) {
        throw std::invalid_argument(
            label_ + " outbox settlement identity is invalid");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox settlement",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox settlement");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox settlement");
    const auto found = find_outbox_intent(
        loaded.outbox, destination_device_id, operation_id);
    if (found == loaded.outbox.end()) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::IntentMissing;
    }
    if (found->lease.claim_id != claim_id) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::StaleClaim;
    }

    // Exact intent/claim identity is checked before a clock sample because a
    // missing or stale receipt has no liveness authority to evaluate.
    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox settlement host clock observation");
    const std::uint64_t now_epoch =
        accept_outbox_clock_observation_or_commit_quarantine_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox settlement time observation");
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            found->lease, claim_id, now_epoch,
            label_ + " outbox settlement");
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::logic_error(
            label_ + " outbox settlement lost exact claim authority");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox settlement expired receipt");
        return SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim;
    }

    delete_outbox_intent_exact_or_throw(
        db_, *found, label_ + " outbox settlement");
    loaded.outbox.erase(found);
    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation, label_ + " state generation");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, label_ + " outbox settlement");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label_ + " outbox settlement");
    return SyncReplicaSqliteOutboxReceiptResult::Applied;
}

SyncReplicaSqliteOutboxReceiptResult
SyncReplicaSqliteOwner::renew_outbox_lease_or_throw(
    const std::string& destination_device_id,
    const std::string& operation_id,
    const std::string& claim_id,
    std::uint64_t lease_seconds) {
    if (!sync_id_is_valid(destination_device_id) ||
        !is_lowercase_sha256_hex(operation_id) ||
        !is_lowercase_sha256_hex(claim_id)) {
        throw std::invalid_argument(
            label_ + " outbox renewal identity is invalid");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label_ + " outbox renewal lease_seconds must be in 1..86400");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox renewal",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox renewal");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox renewal");
    const auto found = find_outbox_intent(
        loaded.outbox, destination_device_id, operation_id);
    if (found == loaded.outbox.end()) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::IntentMissing;
    }
    if (found->lease.claim_id != claim_id) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::StaleClaim;
    }

    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox renewal host clock observation");
    const std::uint64_t now_epoch =
        accept_outbox_clock_observation_or_commit_quarantine_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox renewal time observation");
    if (lease_seconds >
        std::numeric_limits<std::uint64_t>::max() - now_epoch) {
        throw std::overflow_error(
            label_ + " outbox renewal lease deadline overflows uint64_t");
    }
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            found->lease, claim_id, now_epoch,
            label_ + " outbox renewal");
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::logic_error(
            label_ + " outbox renewal lost exact claim authority");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox renewal expired receipt");
        return SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim;
    }

    const SyncReplicaOutboxLeaseState previous = found->lease;
    const SyncReplicaOutboxLeaseState renewed =
        renew_sync_replica_outbox_lease_or_throw(
            previous, claim_id, now_epoch, lease_seconds,
            label_ + " outbox renewal");
    if (renewed == previous) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox renewal already covered");
        return SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered;
    }
    found->lease = renewed;
    publish_outbox_lease_update_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded, *found,
        previous, label_ + " outbox renewal");
    return SyncReplicaSqliteOutboxReceiptResult::Applied;
}

SyncReplicaSqliteOutboxReceiptResult
SyncReplicaSqliteOwner::release_outbox_for_retry_or_throw(
    const std::string& destination_device_id,
    const std::string& operation_id,
    const std::string& claim_id,
    std::uint64_t retry_delay_seconds) {
    if (!sync_id_is_valid(destination_device_id) ||
        !is_lowercase_sha256_hex(operation_id) ||
        !is_lowercase_sha256_hex(claim_id)) {
        throw std::invalid_argument(
            label_ + " outbox release identity is invalid");
    }
    if (retry_delay_seconds > kSyncReplicaOutboxMaxRetryDelaySeconds) {
        throw std::invalid_argument(
            label_ + " outbox release retry delay exceeds the fixed retry budget");
    }
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox release",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox release");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox release");
    const auto found = find_outbox_intent(
        loaded.outbox, destination_device_id, operation_id);
    if (found == loaded.outbox.end()) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::IntentMissing;
    }
    if (found->lease.claim_id != claim_id) {
        transaction.commit();
        return SyncReplicaSqliteOutboxReceiptResult::StaleClaim;
    }

    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox release host clock observation");
    const std::uint64_t now_epoch =
        accept_outbox_clock_observation_or_commit_quarantine_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox release time observation");
    if (retry_delay_seconds >
        std::numeric_limits<std::uint64_t>::max() - now_epoch) {
        throw std::overflow_error(
            label_ + " outbox release retry deadline overflows uint64_t");
    }
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            found->lease, claim_id, now_epoch,
            label_ + " outbox release");
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::logic_error(
            label_ + " outbox release lost exact claim authority");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox release expired receipt");
        return SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim;
    }

    const SyncReplicaOutboxLeaseState previous = found->lease;
    found->lease = release_sync_replica_outbox_lease_or_throw(
        previous, claim_id, now_epoch, retry_delay_seconds,
        label_ + " outbox release");
    publish_outbox_lease_update_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded, *found,
        previous, label_ + " outbox release");
    return SyncReplicaSqliteOutboxReceiptResult::Applied;
}

SyncReplicaOutboxClockObservationResult
SyncReplicaSqliteOwner::observe_outbox_clock_or_throw() {
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox clock observation",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox clock observation");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox clock observation");
    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox clock host observation");
    const SyncReplicaOutboxClockObservationResult result =
        publish_outbox_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded, observation,
            label_ + " outbox clock observation");
    attest_and_commit_clock_observation_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded,
        label_ + " outbox clock observation");
    return result;
}

SyncReplicaOutboxClockState
SyncReplicaSqliteOwner::recover_outbox_clock_or_throw(
    std::uint64_t expected_observation_generation) {
    SyncSqliteTransaction transaction(
        db_, label_ + " outbox clock recovery",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " outbox clock recovery");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " outbox clock recovery");
    const SyncReplicaOutboxClockObservation observation =
        clock_source_->observe_or_throw(
            label_ + " outbox clock recovery host observation");
    const SyncReplicaOutboxClockState recovered =
        recover_sync_replica_outbox_clock_or_throw(
            loaded.outbox_clock.state, observation,
            outbox_clock_policy(loaded.meta.limits),
            expected_observation_generation,
            label_ + " outbox clock recovery");
    const DurableOutboxClock previous = loaded.outbox_clock;
    loaded.outbox_clock = make_outbox_clock_or_throw(
        folder_id_, local_actor_, recovered,
        label_ + " recovered outbox clock");
    update_outbox_clock_exact_or_throw(
        db_, loaded.outbox_clock, previous,
        label_ + " outbox clock recovery");
    attest_and_commit_clock_observation_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded,
        label_ + " outbox clock recovery");
    return recovered;
}

void SyncReplicaSqliteOwner::replace_limits_or_throw(
    const SyncReplicaSqliteOwnerLimits& replacement) {
    validate_owner_limits_or_throw(
        folder_id_, local_actor_, replacement,
        label_ + " replacement policy");
    SyncSqliteTransaction transaction(
        db_, label_ + " policy replacement",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " policy replacement");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " policy replacement");
    if (loaded.meta.limits == replacement) {
        transaction.commit();
        return;
    }

    // Restoration under the replacement policy proves every retained envelope
    // and aggregate charge fits before the durable policy changes.
    SyncReplicaModel replacement_model = SyncReplicaModel::restore_or_throw(
        loaded.model.durable_state(), replacement.model);
    if (size_to_u64_or_throw(
            loaded.outbox.size(), label_ + " replacement outbox count") >
            replacement.max_outbox_intents ||
        outbox_destination_bytes_or_throw(loaded.outbox) >
            replacement.max_outbox_destination_bytes) {
        throw std::length_error(
            label_ + " retained outbox does not fit replacement policy");
    }
    try {
        validate_sync_replica_outbox_clock_state_against_policy_or_throw(
            loaded.outbox_clock.state, outbox_clock_policy(replacement),
            label_ + " replacement outbox clock");
    } catch (const std::exception& error) {
        throw std::length_error(
            label_ + " retained outbox clock does not fit replacement policy: " +
            error.what());
    }
    const std::uint64_t state_generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " state generation");
    const std::uint64_t policy_generation = increment_or_throw(
        loaded.meta.policy_generation,
        label_ + " policy generation");
    const DurableMeta meta = meta_from_state_or_throw(
        replacement_model, loaded.meta.database_incarnation_sha256,
        loaded.meta.database_recovery_epoch, replacement, state_generation,
        policy_generation, loaded.outbox,
        loaded.historical_version_pins);
    update_meta_or_throw(db_, meta, label_ + " policy replacement");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, replacement_model, meta,
        loaded.outbox_clock, loaded.outbox,
        loaded.historical_version_pins, label_ + " policy replacement");
}

}  // namespace anonsync
