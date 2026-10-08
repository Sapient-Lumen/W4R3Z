#include "sync_replica_sqlite_owner.hpp"

#include "sha256_digest.hpp"
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
#include <utility>
#include <vector>

#include <openssl/rand.h>

#include <sqlite3.h>

namespace anonsync {
namespace {

constexpr std::uint64_t kLegacySchemaVersion = 1U;
constexpr std::uint64_t kPreviousSchemaVersion = 2U;
constexpr std::uint64_t kClockSchemaVersion = 3U;
constexpr std::uint64_t kRetryProvenanceSchemaVersion = 4U;
constexpr std::uint64_t kSchemaVersion = 5U;
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

// Current schema owns liveness time. The exact accepted/rejected host-clock
// observation is durable evidence, the policy is part of the cutpoint, and a
// quarantined row cannot silently mint lease or retry authority.
constexpr std::array<SchemaDefinition, 10> kSchema{{
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

struct DurableMeta final {
    std::uint64_t schema_version = kSchemaVersion;
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t last_local_counter = 0;
    std::uint64_t state_generation = 0;
    std::uint64_t policy_generation = 0;
    SyncReplicaSqliteOwnerLimits limits;
    std::uint64_t evidence_count = 0;
    std::uint64_t active_count = 0;
    std::uint64_t retained_canonical_bytes = 0;
    std::uint64_t retained_context_entries = 0;
    std::uint64_t retained_predecessor_ids = 0;
    std::uint64_t outbox_intent_count = 0;
    std::uint64_t outbox_destination_bytes = 0;
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

[[nodiscard]] SyncReplicaOutboxClockPolicy outbox_clock_policy(
    const SyncReplicaSqliteOwnerLimits& limits) {
    return {limits.max_outbox_clock_uncertainty_ns,
            limits.max_outbox_clock_forward_step_seconds,
            limits.max_outbox_clock_realtime_lag_seconds};
}

[[nodiscard]] std::string cutpoint_digest_or_throw(
    const DurableMeta& meta) {
    if (meta.schema_version != kSchemaVersion) {
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
    const bool current_schema = expected_schema_version == kSchemaVersion;
    const std::string query = current_schema
        ? "SELECT schema_version,folder_id,local_device_id,local_epoch_be,"
          "last_local_counter_be,state_generation_be,policy_generation_be,"
          "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
          "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
          "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
          "max_outbox_intents_be,max_outbox_destination_bytes_be,"
          "max_outbox_clock_uncertainty_ns_be,"
          "max_outbox_clock_forward_step_seconds_be,"
          "max_outbox_clock_realtime_lag_seconds_be,"
          "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
          "retained_context_entries_be,retained_predecessor_ids_be,"
          "outbox_intent_count_be,outbox_destination_bytes_be,"
          "local_actor_compromised,local_operation_digest,operation_set_digest,"
          "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest "
          "FROM main.sync_replica_meta WHERE id=1 LIMIT 2;"
        : "SELECT schema_version,folder_id,local_device_id,local_epoch_be,"
          "last_local_counter_be,state_generation_be,policy_generation_be,"
          "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
          "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
          "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
          "max_outbox_intents_be,max_outbox_destination_bytes_be,"
          "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
          "retained_context_entries_be,retained_predecessor_ids_be,"
          "outbox_intent_count_be,outbox_destination_bytes_be,"
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
         observed_schema_version != kSchemaVersion)) {
        throw std::runtime_error(label + " schema version is unsupported");
    }

    DurableMeta meta;
    meta.schema_version = observed_schema_version;
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
    if (current_schema) {
        meta.limits.max_outbox_clock_uncertainty_ns = column_u64_be_or_throw(
            statement.stmt, index++, label + " max outbox clock uncertainty");
        meta.limits.max_outbox_clock_forward_step_seconds = column_u64_be_or_throw(
            statement.stmt, index++, label + " max outbox clock forward step");
        meta.limits.max_outbox_clock_realtime_lag_seconds = column_u64_be_or_throw(
            statement.stmt, index++, label + " max outbox clock realtime lag");
    }
    meta.evidence_count = column_u64_be_or_throw(
        statement.stmt, index++, label + " evidence count");
    meta.active_count = column_u64_be_or_throw(
        statement.stmt, index++, label + " active count");
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
    if (!is_lowercase_sha256_hex(meta.local_operation_digest) ||
        !is_lowercase_sha256_hex(meta.operation_set_digest) ||
        !is_lowercase_sha256_hex(meta.evidence_set_digest) ||
        !is_lowercase_sha256_hex(meta.visible_state_digest) ||
        !is_lowercase_sha256_hex(meta.outbox_digest) ||
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
    } else {
        expected_cutpoint = cutpoint_digest_or_throw(meta);
    }
    if (expected_cutpoint != meta.cutpoint_digest) {
        throw std::runtime_error(label + " durable cutpoint digest mismatch");
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
        "id,schema_version,folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,state_generation_be,policy_generation_be,"
        "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,"
        "max_outbox_clock_uncertainty_ns_be,"
        "max_outbox_clock_forward_step_seconds_be,"
        "max_outbox_clock_realtime_lag_seconds_be,"
        "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
        "retained_context_entries_be,retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,"
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest)"
        "VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
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
    meta.folder_id = folder_id;
    meta.local_actor = local_actor;
    meta.state_generation = 1U;
    meta.policy_generation = 1U;
    meta.limits = limits;
    meta.local_operation_digest = local_operation_digest_or_throw(
        folder_id, local_actor, empty.local_operation_ids());
    meta.operation_set_digest = empty.operation_set_digest();
    meta.evidence_set_digest = empty.evidence_set_digest();
    meta.visible_state_digest = empty.visible_state_digest();
    meta.outbox_digest = outbox_digest_or_throw(folder_id, {});
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
        const std::string operation_id = sqlite_column_text_or_throw(
            statement.stmt, 0, 64U, label + " operation id");
        const std::string canonical = sqlite_column_blob_or_throw(
            statement.stmt, 1,
            meta.limits.model.max_canonical_operation_bytes,
            label + " canonical operation");
        const std::uint64_t canonical_size = column_u64_be_or_throw(
            statement.stmt, 2, label + " canonical operation size");
        const std::uint64_t context_count = column_u64_be_or_throw(
            statement.stmt, 3, label + " context count");
        const std::uint64_t predecessor_count = column_u64_be_or_throw(
            statement.stmt, 4, label + " predecessor count");
        const SyncReplicaEvidenceState state = parse_evidence_state_or_throw(
            sqlite_column_text_or_throw(
                statement.stmt, 5, 64U, label + " evidence state"),
            label);
        SyncReplicaOperation operation =
            decode_sync_replica_operation_canonical_or_throw(
                canonical, meta.limits.model);
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
        if (!states.emplace(operation_id, state).second) {
            throw std::runtime_error(label + " duplicate operation row");
        }
        operations.push_back(std::move(operation));
    }
    return {std::move(operations), std::move(states)};
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

using VisibleRow =
    std::tuple<std::string, std::uint64_t, std::string, bool, bool>;

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
            rows.emplace_back(
                view.canonical_path,
                static_cast<std::uint64_t>(index),
                operation_id,
                operation_id == view.primary_operation_id,
                preserved.contains(operation_id));
        }
    }
    return rows;
}

void verify_visible_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaModel& model,
    const std::string& label) {
    const std::vector<VisibleRow> expected = expected_visible_rows(model);
    const std::uint64_t row_count = count_rows_or_throw(
        db, "SELECT count(*) FROM main.sync_replica_visible;",
        label + " visible row count");
    if (row_count != size_to_u64_or_throw(
                         expected.size(), label + " visible rows")) {
        throw std::runtime_error(label + " visible row count mismatch");
    }
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT canonical_path,visible_ordinal,operation_id,is_primary,"
        "preserve_file FROM main.sync_replica_visible "
        "ORDER BY canonical_path,visible_ordinal;",
        label + " visible query prepare");
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
        const VisibleRow observed{
            sqlite_column_text_or_throw(
                statement.stmt, 0, kSyncManifestRelativePathMaxBytes,
                label + " visible path"),
            sqlite_column_u64_or_throw(
                statement.stmt, 1, label + " visible ordinal"),
            sqlite_column_text_or_throw(
                statement.stmt, 2, 64U, label + " visible operation id"),
            sqlite_column_bool_or_throw(
                statement.stmt, 3, label + " visible primary"),
            sqlite_column_bool_or_throw(
                statement.stmt, 4, label + " visible preserve")};
        if (observed != expected[index]) {
            throw std::runtime_error(label + " visible projection mismatch");
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
    verify_parent_edges_or_throw(db, operations, meta, label);
    SyncReplicaDurableState durable;
    durable.folder_id = meta.folder_id;
    durable.local_actor = meta.local_actor;
    durable.last_local_counter = meta.last_local_counter;
    durable.local_operation_ids =
        read_local_operation_ids_or_throw(db, meta, label);
    if (local_operation_digest_or_throw(
            meta.folder_id, meta.local_actor, durable.local_operation_ids) !=
        meta.local_operation_digest) {
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
        model.local_actor_compromised() != meta.local_actor_compromised ||
        model.operation_set_digest() != meta.operation_set_digest ||
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
    verify_visible_or_throw(db, model, label);
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
        : (schema_version == kSchemaVersion
               ? read_current_outbox_clock_or_throw(
                     db, meta.folder_id, meta.local_actor, label)
               : read_legacy_outbox_clock_or_throw(db, meta, label));
    if (outbox_clock.state.high_water_epoch < migration_floor) {
        throw std::runtime_error(
            label + " outbox clock predates retained lease authority");
    }
    if (schema_version == kSchemaVersion) {
        validate_sync_replica_outbox_clock_state_against_policy_or_throw(
            outbox_clock.state, outbox_clock_policy(meta.limits),
            label + " durable outbox clock");
    }
    return {std::move(meta), std::move(outbox_clock), std::move(model),
            std::move(stored_states), std::move(outbox)};
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

[[nodiscard]] DurableMeta meta_from_state_or_throw(
    const SyncReplicaModel& model,
    const SyncReplicaSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    std::uint64_t policy_generation,
    const std::vector<SyncReplicaSqliteOutboxIntent>& outbox) {
    DurableMeta meta;
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
    meta.local_actor_compromised = model.local_actor_compromised();
    meta.local_operation_digest = local_operation_digest_or_throw(
        model.folder_id(), model.local_actor(), model.local_operation_ids());
    meta.operation_set_digest = model.operation_set_digest();
    meta.evidence_set_digest = model.evidence_set_digest();
    meta.visible_state_digest = model.visible_state_digest();
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
        "folder_id=?,local_device_id=?,local_epoch_be=?,"
        "last_local_counter_be=?,state_generation_be=?,policy_generation_be=?,"
        "max_operations_be=?,max_context_entries_be=?,max_predecessor_ids_be=?,"
        "max_canonical_operation_bytes_be=?,max_retained_canonical_bytes_be=?,"
        "max_retained_context_entries_be=?,max_retained_predecessor_ids_be=?,"
        "max_outbox_intents_be=?,max_outbox_destination_bytes_be=?,"
        "max_outbox_clock_uncertainty_ns_be=?,"
        "max_outbox_clock_forward_step_seconds_be=?,"
        "max_outbox_clock_realtime_lag_seconds_be=?,"
        "evidence_count_be=?,active_count_be=?,retained_canonical_bytes_be=?,"
        "retained_context_entries_be=?,retained_predecessor_ids_be=?,"
        "outbox_intent_count_be=?,outbox_destination_bytes_be=?,"
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
        "canonical_path,visible_ordinal,operation_id,is_primary,preserve_file)"
        "VALUES(?,?,?,?,?);",
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
    snapshot.visible_state_digest = loaded.meta.visible_state_digest;
    snapshot.outbox_digest = loaded.meta.outbox_digest;
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
    const std::string& label) {
    LoadedState observed = load_state_or_throw(
        db, folder_id, local_actor, label + " staged re-attestation");
    if (observed.meta != expected_meta ||
        observed.outbox_clock != expected_outbox_clock ||
        observed.model.durable_state() != expected_model.durable_state() ||
        observed.outbox != expected_outbox) {
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
    const std::string& label) {
    attest_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, expected_model,
        expected_meta, expected_outbox_clock, expected_outbox, label);
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
        loaded.outbox_clock, loaded.outbox, label + " quarantine publication");
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
        loaded.outbox_clock, loaded.outbox, label);
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
        loaded.model, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox);
    update_meta_or_throw(db, meta, label);
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox, label);
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
        prior.meta.schema_version != kRetryProvenanceSchemaVersion) {
        throw std::logic_error(
            label + " migration source is not schema v1, v2, v3, or v4");
    }
    const std::uint64_t generation = increment_or_throw(
        prior.meta.state_generation, label + " migration state generation");

    // Keep canonical evidence and projections in place. Replace only the
    // meta/outbox protocol surfaces after exact prior-version restoration.
    if (prior.meta.schema_version == kPreviousSchemaVersion ||
        prior.meta.schema_version == kClockSchemaVersion ||
        prior.meta.schema_version == kRetryProvenanceSchemaVersion) {
        sqlite_exec_or_throw(
            db, "DROP INDEX main.sync_replica_outbox_schedule;",
            label + " retire previous outbox schedule index");
    }
    std::string retire_sql =
        "DROP INDEX main.sync_replica_outbox_operation;"
        "DROP TABLE main.sync_replica_outbox;";
    if (prior.meta.schema_version == kClockSchemaVersion ||
        prior.meta.schema_version == kRetryProvenanceSchemaVersion) {
        retire_sql += "DROP TABLE main.sync_replica_outbox_clock;";
    }
    retire_sql += "DROP TABLE main.sync_replica_meta;";
    sqlite_exec_or_throw(db, retire_sql, label + " retire prior outbox schema");
    for (const SchemaDefinition& definition : kSchema) {
        if (definition.name == "sync_replica_meta" ||
            definition.name == "sync_replica_outbox" ||
            definition.name == "sync_replica_outbox_clock" ||
            definition.name == "sync_replica_outbox_operation" ||
            definition.name == "sync_replica_outbox_schedule") {
            sqlite_exec_or_throw(
                db, create_statement(definition),
                label + " create " + std::string(definition.name));
        }
    }
    verify_schema_or_throw(db, label + " migrated schema");

    const DurableMeta meta = meta_from_state_or_throw(
        prior.model, prior.meta.limits, generation,
        prior.meta.policy_generation, prior.outbox);
    insert_meta_row_or_throw(db, meta, label + " migrated");
    insert_outbox_intents_or_throw(db, prior.outbox, label + " migrated");
    insert_outbox_clock_or_throw(
        db, prior.outbox_clock, label + " migrated");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db, folder_id, local_actor, prior.model, meta,
        prior.outbox_clock, prior.outbox, label + " migration publication");
}

}  // namespace

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
            outbox_clock, {}, label_ + " schema initialization");
    } else if (schema_matches(observed, kSchema)) {
        (void)load_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " existing database");
        require_write_authority_or_throw(
            transaction, db_, label_ + " existing database");
        transaction.commit();
    } else if (schema_matches(observed, kLegacySchema)) {
        LoadedState legacy = load_legacy_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " legacy database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(legacy), folder_id_, local_actor_,
            label_ + " schema v1 to v5");
    } else if (schema_matches(observed, kPreviousSchema)) {
        LoadedState previous = load_previous_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " previous database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(previous), folder_id_, local_actor_,
            label_ + " schema v2 to v5");
    } else if (schema_matches(observed, kClockSchema)) {
        LoadedState clock = load_clock_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v3 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(clock), folder_id_, local_actor_,
            label_ + " schema v3 to v5");
    } else if (schema_matches(observed, kRetryProvenanceSchema)) {
        LoadedState retry = load_retry_provenance_state_or_throw(
            db_, folder_id_, local_actor_, label_ + " schema v4 database");
        migrate_prior_schema_or_throw(
            transaction, db_, std::move(retry), folder_id_, local_actor_,
            label_ + " schema v4 to v5");
    } else {
        throw std::runtime_error(
            label_ + " database does not match schema v5, exact rev0873 v4, "
                     "exact rev0872 v3, exact rev0871 v2, or exact rev0869 v1");
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

SyncReplicaOperation SyncReplicaSqliteOwner::create_local_file_or_throw(
    std::string canonical_path,
    std::uint64_t size_bytes,
    std::string content_sha256,
    std::span<const std::string> destination_device_ids) {
    SyncSqliteTransaction transaction(
        db_, label_ + " local file publication",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " local file publication");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " local file publication");
    const std::vector<std::string> destinations =
        validate_destinations_or_throw(
            destination_device_ids, local_actor_.device_id,
            label_ + " local file publication");
    require_outbox_capacity_or_throw(
        loaded, destinations, label_ + " local file publication");

    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " state generation");
    SyncReplicaOperation operation = loaded.model.create_local_file_or_throw(
        std::move(canonical_path), size_bytes, std::move(content_sha256));
    const auto state = loaded.model.evidence_state(operation.operation_id);
    if (state != SyncReplicaEvidenceState::Active) {
        throw std::logic_error(
            label_ + " locally minted file did not project active");
    }

    std::vector<SyncReplicaSqliteOutboxIntent> added;
    added.reserve(destinations.size());
    for (const std::string& destination : destinations) {
        added.push_back({destination, operation.operation_id, generation, {}});
    }
    loaded.outbox.insert(
        loaded.outbox.end(), added.begin(), added.end());
    std::sort(
        loaded.outbox.begin(), loaded.outbox.end(),
        [](const auto& left, const auto& right) {
            return std::tie(left.destination_device_id, left.operation_id) <
                   std::tie(right.destination_device_id, right.operation_id);
        });

    insert_operation_rows_or_throw(
        db_, operation, *state, loaded.meta.limits.model, true,
        label_ + " local file publication");
    insert_outbox_intents_or_throw(
        db_, added, label_ + " local file publication");
    rewrite_projection_or_throw(
        db_, loaded.model, loaded.persisted_states,
        label_ + " local file publication");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox);
    update_meta_or_throw(
        db_, meta, label_ + " local file publication");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox, label_ + " local file publication");
    return operation;
}

SyncReplicaOperation SyncReplicaSqliteOwner::create_local_tombstone_or_throw(
    std::string canonical_path,
    std::span<const std::string> destination_device_ids) {
    SyncSqliteTransaction transaction(
        db_, label_ + " local tombstone publication",
        SyncSqliteTransactionMode::Immediate);
    require_write_authority_or_throw(
        transaction, db_, label_ + " local tombstone publication");
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, local_actor_, label_ + " local tombstone publication");
    const std::vector<std::string> destinations =
        validate_destinations_or_throw(
            destination_device_ids, local_actor_.device_id,
            label_ + " local tombstone publication");
    require_outbox_capacity_or_throw(
        loaded, destinations, label_ + " local tombstone publication");

    const std::uint64_t generation = increment_or_throw(
        loaded.meta.state_generation,
        label_ + " state generation");
    SyncReplicaOperation operation =
        loaded.model.create_local_tombstone_or_throw(
            std::move(canonical_path));
    const auto state = loaded.model.evidence_state(operation.operation_id);
    if (state != SyncReplicaEvidenceState::Active) {
        throw std::logic_error(
            label_ + " locally minted tombstone did not project active");
    }

    std::vector<SyncReplicaSqliteOutboxIntent> added;
    added.reserve(destinations.size());
    for (const std::string& destination : destinations) {
        added.push_back({destination, operation.operation_id, generation, {}});
    }
    loaded.outbox.insert(
        loaded.outbox.end(), added.begin(), added.end());
    std::sort(
        loaded.outbox.begin(), loaded.outbox.end(),
        [](const auto& left, const auto& right) {
            return std::tie(left.destination_device_id, left.operation_id) <
                   std::tie(right.destination_device_id, right.operation_id);
        });

    insert_operation_rows_or_throw(
        db_, operation, *state, loaded.meta.limits.model, true,
        label_ + " local tombstone publication");
    insert_outbox_intents_or_throw(
        db_, added, label_ + " local tombstone publication");
    rewrite_projection_or_throw(
        db_, loaded.model, loaded.persisted_states,
        label_ + " local tombstone publication");
    const DurableMeta meta = meta_from_state_or_throw(
        loaded.model, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox);
    update_meta_or_throw(
        db_, meta, label_ + " local tombstone publication");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox, label_ + " local tombstone publication");
    return operation;
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
        loaded.model, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox);
    update_meta_or_throw(db_, meta, label_ + " remote admission");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox, label_ + " remote admission");
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
                    " first ready matching outbox operation exceeds delivery wire policy before claim"));
            }
        }
        if (max_file_payload_bytes.has_value() &&
            operation->size_bytes > *max_file_payload_bytes) {
            throw std::runtime_error(
                label_ +
                " first ready matching file operation exceeds delivery payload policy before claim");
        }
        if (available_file_content.has_value() &&
            !std::binary_search(
                available_file_content_sha256s.begin(),
                available_file_content_sha256s.end(),
                operation->content_sha256)) {
            continue;
        }
        found = candidate;
        selected_operation = std::move(operation);
        break;
    }
    if (found == loaded.outbox.end()) {
        attest_and_commit_clock_observation_or_throw(
            transaction, db_, folder_id_, local_actor_, loaded,
            label_ + " outbox claim no-ready-intent");
        return std::nullopt;
    }

    const SyncReplicaOutboxLeaseState previous = found->lease;
    found->lease = claim_sync_replica_outbox_lease_or_throw(
        previous, folder_id_, found->destination_device_id,
        found->operation_id, found->enqueued_generation,
        loaded.meta.cutpoint_digest, worker_id, now_epoch,
        lease_seconds, claim_entropy, label_ + " outbox claim");

    if (!selected_operation.has_value()) {
        throw std::logic_error(
            label_ + " claimed intent lost its selected operation owner");
    }
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
        loaded.model, loaded.meta.limits, generation,
        loaded.meta.policy_generation, loaded.outbox);
    update_meta_or_throw(db_, meta, label_ + " outbox settlement");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, loaded.model, meta,
        loaded.outbox_clock, loaded.outbox,
        label_ + " outbox settlement");
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
        replacement_model, replacement, state_generation,
        policy_generation, loaded.outbox);
    update_meta_or_throw(db_, meta, label_ + " policy replacement");
    attest_and_commit_staged_cutpoint_or_throw(
        transaction, db_, folder_id_, local_actor_, replacement_model, meta,
        loaded.outbox_clock, loaded.outbox, label_ + " policy replacement");
}

}  // namespace anonsync
