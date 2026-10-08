#include "sync_replica_tls_membership_sqlite_owner.hpp"

#include "sync_replica_tls_policy_sqlite_profile.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

constexpr std::uint64_t kSchemaVersion = 1U;
constexpr std::uint64_t kMaxPersistentInteger =
    static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());
constexpr std::string_view kGenesisDigestDomain =
    "anonsync:sync-replica-tls-membership-chain:genesis:v1";
constexpr std::string_view kUpdateDigestDomain =
    "anonsync:sync-replica-tls-membership-chain:update:v1";
constexpr std::string_view kNoSnapshotDigest =
    "0000000000000000000000000000000000000000000000000000000000000000";

constexpr std::string_view kMetaSchemaSql =
    "CREATE TABLE sync_replica_tls_membership_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=1),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
    "local_actor_epoch INTEGER NOT NULL CHECK(local_actor_epoch>0),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "current_policy_epoch INTEGER NOT NULL CHECK(current_policy_epoch>=0),"
    "current_entry_count INTEGER NOT NULL CHECK(current_entry_count>=0),"
    "current_snapshot_digest TEXT NOT NULL CHECK(length(current_snapshot_digest)=64),"
    "current_chain_digest TEXT NOT NULL CHECK(length(current_chain_digest)=64)) STRICT";

constexpr std::string_view kUpdatesSchemaSql =
    "CREATE TABLE sync_replica_tls_membership_updates("
    "state_generation INTEGER PRIMARY KEY CHECK(state_generation>0),"
    "policy_epoch INTEGER NOT NULL UNIQUE CHECK(policy_epoch>0),"
    "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
    "previous_chain_digest TEXT NOT NULL CHECK(length(previous_chain_digest)=64),"
    "snapshot_digest TEXT NOT NULL CHECK(length(snapshot_digest)=64),"
    "chain_digest TEXT NOT NULL UNIQUE CHECK(length(chain_digest)=64)) STRICT";

constexpr std::string_view kEntriesSchemaSql =
    "CREATE TABLE sync_replica_tls_membership_entries("
    "state_generation INTEGER NOT NULL CHECK(state_generation>0),"
    "spki_sha256 TEXT NOT NULL CHECK(length(spki_sha256)=64),"
    "actor_device_id TEXT NOT NULL CHECK(length(actor_device_id) BETWEEN 1 AND 128),"
    "actor_epoch INTEGER NOT NULL CHECK(actor_epoch>0),"
    "PRIMARY KEY(state_generation,spki_sha256)) STRICT";

struct SchemaDefinition final {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view sql;
};

constexpr std::array<SchemaDefinition, 3U> kSchema{{
    {"table", "sync_replica_tls_membership_meta",
     "sync_replica_tls_membership_meta", kMetaSchemaSql},
    {"table", "sync_replica_tls_membership_updates",
     "sync_replica_tls_membership_updates", kUpdatesSchemaSql},
    {"table", "sync_replica_tls_membership_entries",
     "sync_replica_tls_membership_entries", kEntriesSchemaSql},
}};

struct LoadedMembershipState final {
    SyncReplicaTlsMembershipSqliteSnapshot public_snapshot;
    std::optional<SyncReplicaTlsMembershipSnapshot> current_snapshot;
    std::uint64_t retained_entry_rows = 0U;
};

void append_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    std::array<char, 8U> encoded{};
    for (std::size_t index = encoded.size(); index != 0U; --index) {
        encoded[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(std::string_view(encoded.data(), encoded.size()));
}

void append_string(Sha256DigestBuilder& digest, std::string_view value) {
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

void append_actor(Sha256DigestBuilder& digest,
                  const SyncReplicaActor& actor) {
    append_string(digest, actor.device_id);
    append_u64(digest, actor.epoch);
}

[[nodiscard]] std::string genesis_chain_digest(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor) {
    Sha256DigestBuilder digest;
    append_string(digest, kGenesisDigestDomain);
    append_u64(digest, kSchemaVersion);
    append_string(digest, folder_id);
    append_actor(digest, local_actor);
    return digest.finish_hex();
}

[[nodiscard]] std::string update_chain_digest(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::uint64_t state_generation,
    std::uint64_t policy_epoch,
    std::uint64_t entry_count,
    std::string_view previous_chain_digest,
    std::string_view snapshot_digest) {
    Sha256DigestBuilder digest;
    append_string(digest, kUpdateDigestDomain);
    append_u64(digest, kSchemaVersion);
    append_string(digest, folder_id);
    append_actor(digest, local_actor);
    append_u64(digest, state_generation);
    append_u64(digest, policy_epoch);
    append_u64(digest, entry_count);
    append_string(digest, previous_chain_digest);
    append_string(digest, snapshot_digest);
    return digest.finish_hex();
}

void validate_identity_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view label) {
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " folder_id is not a lowercase portable sync id");
    }
    if (!sync_id_is_valid(local_actor.device_id) ||
        local_actor.epoch == 0U ||
        local_actor.epoch > kMaxPersistentInteger) {
        throw std::invalid_argument(
            std::string(label) + " local actor identity is not persistable");
    }
}

void validate_anchor_or_throw(
    const SyncReplicaTlsMembershipAnchor& anchor,
    std::string_view label) {
    if (anchor.state_generation > kMaxPersistentInteger) {
        throw std::invalid_argument(
            std::string(label) + " generation exceeds SQLite integer range");
    }
    if (!is_lowercase_sha256_hex(anchor.chain_digest)) {
        throw std::invalid_argument(
            std::string(label) + " chain digest is not lowercase SHA-256");
    }
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

[[nodiscard]] std::uint64_t schema_object_count_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM main.sqlite_schema WHERE sql IS NOT NULL AND ("
        "name GLOB 'sync_replica_tls_membership_*' OR "
        "tbl_name IN ('sync_replica_tls_membership_meta',"
        "'sync_replica_tls_membership_updates',"
        "'sync_replica_tls_membership_entries'));",
        label + " schema object count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema object count step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " schema object count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " schema object count");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema object count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " schema object count returned multiple rows");
    }
    return count;
}

[[nodiscard]] std::uint64_t temp_schema_attachment_count_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM temp.sqlite_schema WHERE sql IS NOT NULL AND ("
        "name GLOB 'sync_replica_tls_membership_*' OR "
        "tbl_name IN ('sync_replica_tls_membership_meta',"
        "'sync_replica_tls_membership_updates',"
        "'sync_replica_tls_membership_entries'));",
        label + " temp schema attachment count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " temp schema attachment count step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " temp schema attachment count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " temp schema attachment count");
    if (step_row_or_done_or_throw(
            statement.stmt,
            label + " temp schema attachment count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " temp schema attachment count returned multiple rows");
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
    const std::string actual_type = sqlite_column_text_or_throw(
        statement.stmt, 0, 16U, label + " schema object type");
    const std::string actual_table = sqlite_column_text_or_throw(
        statement.stmt, 1, 128U, label + " schema object table");
    const std::string actual_sql = sqlite_column_text_or_throw(
        statement.stmt, 2, 2048U, label + " schema object SQL");
    if (actual_type != expected.type || actual_table != expected.table_name ||
        actual_sql != expected.sql) {
        throw std::runtime_error(
            label + " schema definition mismatch for " +
            std::string(expected.name));
    }
    if (step_row_or_done_or_throw(
            statement.stmt, label + " schema definition trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " schema object name is not unique: " +
            std::string(expected.name));
    }
}

void attest_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    const std::uint64_t count = schema_object_count_or_throw(db, label);
    if (count != kSchema.size()) {
        throw std::runtime_error(
            label + " membership schema object count mismatch");
    }
    if (temp_schema_attachment_count_or_throw(db, label) != 0U) {
        throw std::runtime_error(
            label + " membership tables have unowned temp schema attachments");
    }
    for (const auto& definition : kSchema) {
        require_schema_definition_or_throw(db, definition, label);
    }
}

void initialize_or_attest_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
    const std::string& label) {
    // Serialize both backend-profile attestation and the emptiness decision
    // with schema creation. Two independent process-local owners may race on
    // first open; an observation made before BEGIN IMMEDIATE is not authority
    // to create after another owner commits or changes the journal profile.
    SyncSqliteTransaction transaction(
        db, label + " schema initialization",
        SyncSqliteTransactionMode::Immediate);
    attest_sync_replica_tls_policy_sqlite_backend_or_throw(
        db, "membership", label, backend_disposition);
    const std::uint64_t existing = schema_object_count_or_throw(db, label);
    if (existing == 0U) {
        const std::string genesis =
            genesis_chain_digest(folder_id, local_actor);
        for (const auto& definition : kSchema) {
            sqlite_exec_or_throw(
                db, std::string(definition.sql),
                label + " create " + std::string(definition.name));
        }
        SyncSqliteStmt insert = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_replica_tls_membership_meta("
            "id,schema_version,folder_id,local_device_id,local_actor_epoch,"
            "state_generation,current_policy_epoch,current_entry_count,"
            "current_snapshot_digest,current_chain_digest)"
            "VALUES(1,1,?,?,?,0,0,0,?,?);",
            label + " initialize metadata prepare");
        sqlite_bind_text_or_throw(insert.stmt, 1, folder_id, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 2, local_actor.device_id, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 3, local_actor.epoch, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 4, std::string(kNoSnapshotDigest), label);
        sqlite_bind_text_or_throw(insert.stmt, 5, genesis, label);
        sqlite_step_done_or_throw(
            insert.stmt, label + " initialize metadata step");
    }
    attest_schema_or_throw(db, label);
    transaction.commit();
}

[[nodiscard]] std::vector<SyncReplicaTlsMembershipEntry>
load_entries_for_generation_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::uint64_t state_generation,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT spki_sha256,actor_device_id,actor_epoch "
        "FROM main.sync_replica_tls_membership_entries "
        "WHERE state_generation=? ORDER BY spki_sha256;",
        label + " entries prepare");
    sqlite_bind_u64_or_throw(
        statement.stmt, 1, state_generation, label);
    std::vector<SyncReplicaTlsMembershipEntry> entries;
    for (;;) {
        const int step = step_row_or_done_or_throw(
            statement.stmt, label + " entries step");
        if (step == SQLITE_DONE) break;
        SyncReplicaTlsMembershipEntry entry;
        entry.spki_sha256 = sqlite_column_text_or_throw(
            statement.stmt, 0, 64U, label + " entry SPKI");
        entry.actor.device_id = sqlite_column_text_or_throw(
            statement.stmt, 1, 128U, label + " entry actor device");
        entry.actor.epoch = sqlite_column_u64_or_throw(
            statement.stmt, 2, label + " entry actor epoch");
        entries.push_back(std::move(entry));
        if (entries.size() > kSyncReplicaTlsMembershipMaxEntries) {
            throw std::runtime_error(
                label + " retained entry count exceeds hard ceiling");
        }
    }
    return entries;
}

[[nodiscard]] std::uint64_t history_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM main.sync_replica_tls_membership_updates;",
        label + " history row count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " history row count step") != SQLITE_ROW) {
        throw std::runtime_error(label + " history row count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " history row count");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " history row count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " history row count returned multiple rows");
    }
    return count;
}

[[nodiscard]] std::uint64_t total_entry_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM main.sync_replica_tls_membership_entries;",
        label + " total entry count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " total entry count step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " total entry count returned no row");
    }
    const std::uint64_t count = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " total entry count");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " total entry count trailing step") !=
        SQLITE_DONE) {
        throw std::runtime_error(
            label + " total entry count returned multiple rows");
    }
    return count;
}

[[nodiscard]] LoadedMembershipState load_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
    const std::string& label) {
    attest_sync_replica_tls_policy_sqlite_backend_or_throw(
        db, "membership", label, backend_disposition);
    attest_schema_or_throw(db, label);

    SyncReplicaTlsMembershipSqliteSnapshot snapshot;
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,local_device_id,local_actor_epoch,"
        "state_generation,current_policy_epoch,current_entry_count,"
        "current_snapshot_digest,current_chain_digest "
        "FROM main.sync_replica_tls_membership_meta WHERE id=1;",
        label + " metadata prepare");
    if (step_row_or_done_or_throw(meta.stmt, label + " metadata step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " membership metadata is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " schema version");
    snapshot.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder identity");
    snapshot.local_actor.device_id = sqlite_column_text_or_throw(
        meta.stmt, 2, 128U, label + " local device identity");
    snapshot.local_actor.epoch = sqlite_column_u64_or_throw(
        meta.stmt, 3, label + " local actor epoch");
    snapshot.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " state generation");
    snapshot.current_policy_epoch = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " current policy epoch");
    snapshot.current_entry_count = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " current entry count");
    snapshot.current_snapshot_digest = sqlite_column_text_or_throw(
        meta.stmt, 7, 64U, label + " current snapshot digest");
    snapshot.current_chain_digest = sqlite_column_text_or_throw(
        meta.stmt, 8, 64U, label + " current chain digest");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata trailing step") != SQLITE_DONE) {
        throw std::runtime_error(label + " membership metadata is duplicated");
    }

    if (schema_version != kSchemaVersion) {
        throw std::runtime_error(label + " membership schema version mismatch");
    }
    validate_identity_or_throw(
        snapshot.folder_id, snapshot.local_actor,
        label + " stored identity");
    if (snapshot.folder_id != expected_folder_id ||
        snapshot.local_actor != expected_local_actor) {
        throw std::runtime_error(
            label + " membership database identity does not match owner");
    }
    if (snapshot.state_generation > kMaxPersistentInteger ||
        snapshot.current_policy_epoch > kMaxPersistentInteger ||
        snapshot.current_entry_count >
            kSyncReplicaTlsMembershipMaxEntries ||
        !is_lowercase_sha256_hex(snapshot.current_snapshot_digest) ||
        !is_lowercase_sha256_hex(snapshot.current_chain_digest)) {
        throw std::runtime_error(label + " membership metadata is invalid");
    }

    const std::uint64_t history_rows = history_rows_or_throw(db, label);
    if (history_rows > kSyncReplicaTlsMembershipMaxHistoryRecords) {
        throw std::runtime_error(
            label + " membership history exceeds its hard ceiling");
    }
    const std::uint64_t retained_entry_rows =
        total_entry_rows_or_throw(db, label);
    if (retained_entry_rows >
        kSyncReplicaTlsMembershipMaxRetainedEntryRows) {
        throw std::runtime_error(
            label + " retained membership entries exceed their hard ceiling");
    }
    snapshot.history.reserve(static_cast<std::size_t>(history_rows));

    const std::string genesis = genesis_chain_digest(
        snapshot.folder_id, snapshot.local_actor);
    std::string previous_chain = genesis;
    std::uint64_t previous_policy_epoch = 0U;
    std::uint64_t expected_generation = 1U;
    std::uint64_t total_entries = 0U;
    std::optional<SyncReplicaTlsMembershipSnapshot> current_snapshot;

    SyncSqliteStmt updates = sqlite_prepare_or_throw(
        db,
        "SELECT state_generation,policy_epoch,entry_count,"
        "previous_chain_digest,snapshot_digest,chain_digest "
        "FROM main.sync_replica_tls_membership_updates "
        "ORDER BY state_generation;",
        label + " history prepare");
    for (;;) {
        const int step = step_row_or_done_or_throw(
            updates.stmt, label + " history step");
        if (step == SQLITE_DONE) break;

        SyncReplicaTlsMembershipHistoryRecord record;
        record.state_generation = sqlite_column_u64_or_throw(
            updates.stmt, 0, label + " history generation");
        record.policy_epoch = sqlite_column_u64_or_throw(
            updates.stmt, 1, label + " history policy epoch");
        record.entry_count = sqlite_column_u64_or_throw(
            updates.stmt, 2, label + " history entry count");
        record.previous_chain_digest = sqlite_column_text_or_throw(
            updates.stmt, 3, 64U, label + " history previous chain");
        record.snapshot_digest = sqlite_column_text_or_throw(
            updates.stmt, 4, 64U, label + " history snapshot digest");
        record.chain_digest = sqlite_column_text_or_throw(
            updates.stmt, 5, 64U, label + " history chain digest");

        if (record.state_generation != expected_generation ||
            record.state_generation > kMaxPersistentInteger) {
            throw std::runtime_error(
                label + " membership generations are not contiguous");
        }
        if (record.policy_epoch == 0U ||
            record.policy_epoch > kMaxPersistentInteger ||
            record.policy_epoch <= previous_policy_epoch) {
            throw std::runtime_error(
                label + " membership policy epochs are not strictly increasing");
        }
        if (record.entry_count > kSyncReplicaTlsMembershipMaxEntries ||
            !is_lowercase_sha256_hex(record.previous_chain_digest) ||
            !is_lowercase_sha256_hex(record.snapshot_digest) ||
            !is_lowercase_sha256_hex(record.chain_digest)) {
            throw std::runtime_error(
                label + " membership history record is invalid");
        }
        if (record.previous_chain_digest != previous_chain) {
            throw std::runtime_error(
                label + " membership history previous-chain link is invalid");
        }

        std::vector<SyncReplicaTlsMembershipEntry> entries =
            load_entries_for_generation_or_throw(
                db, record.state_generation, label);
        if (entries.size() != record.entry_count) {
            throw std::runtime_error(
                label + " membership history entry count mismatch");
        }
        if (total_entries >
            std::numeric_limits<std::uint64_t>::max() - record.entry_count) {
            throw std::runtime_error(
                label + " membership retained entry count overflow");
        }
        total_entries += record.entry_count;

        SyncReplicaTlsMembershipSnapshot restored(
            snapshot.folder_id, snapshot.local_actor, record.policy_epoch,
            std::move(entries), label + " restored snapshot");
        if (restored.snapshot_digest() != record.snapshot_digest) {
            throw std::runtime_error(
                label + " membership snapshot digest mismatch");
        }
        const std::string derived_chain = update_chain_digest(
            snapshot.folder_id, snapshot.local_actor,
            record.state_generation, record.policy_epoch, record.entry_count,
            record.previous_chain_digest, record.snapshot_digest);
        if (derived_chain != record.chain_digest) {
            throw std::runtime_error(
                label + " membership chain digest mismatch");
        }

        previous_policy_epoch = record.policy_epoch;
        previous_chain = record.chain_digest;
        ++expected_generation;
        snapshot.history.push_back(record);
        current_snapshot = std::move(restored);
    }

    if (retained_entry_rows != total_entries) {
        throw std::runtime_error(
            label + " membership entry table contains orphan rows");
    }
    if (history_rows != snapshot.history.size()) {
        throw std::runtime_error(
            label + " membership history row count changed within snapshot");
    }
    if (snapshot.state_generation != snapshot.history.size()) {
        throw std::runtime_error(
            label + " membership metadata generation does not match history");
    }
    if (snapshot.history.empty()) {
        if (snapshot.state_generation != 0U ||
            snapshot.current_policy_epoch != 0U ||
            snapshot.current_entry_count != 0U ||
            snapshot.current_snapshot_digest != kNoSnapshotDigest ||
            snapshot.current_chain_digest != genesis ||
            current_snapshot.has_value()) {
            throw std::runtime_error(
                label + " empty membership metadata is inconsistent");
        }
    } else {
        const auto& current = snapshot.history.back();
        if (snapshot.current_policy_epoch != current.policy_epoch ||
            snapshot.current_entry_count != current.entry_count ||
            snapshot.current_snapshot_digest != current.snapshot_digest ||
            snapshot.current_chain_digest != current.chain_digest ||
            !current_snapshot.has_value()) {
            throw std::runtime_error(
                label + " current membership metadata is inconsistent");
        }
    }

    return {
        std::move(snapshot), std::move(current_snapshot), retained_entry_rows};
}

void require_trusted_anchor_or_throw(
    const LoadedMembershipState& state,
    const SyncReplicaTlsMembershipAnchor& trusted,
    const std::string& label) {
    validate_anchor_or_throw(trusted, label + " trusted anchor");
    const auto& snapshot = state.public_snapshot;
    if (trusted.state_generation > snapshot.state_generation) {
        throw std::runtime_error(
            label + " membership database rolled back below trusted generation");
    }
    const std::string* observed = nullptr;
    std::string genesis;
    if (trusted.state_generation == 0U) {
        genesis = genesis_chain_digest(
            snapshot.folder_id, snapshot.local_actor);
        observed = &genesis;
    } else {
        observed = &snapshot.history.at(
            static_cast<std::size_t>(trusted.state_generation - 1U))
                        .chain_digest;
    }
    if (*observed != trusted.chain_digest) {
        throw std::runtime_error(
            label + " membership history diverges from trusted anchor");
    }
}

}  // namespace

void validate_sync_replica_tls_membership_anchor_or_throw(
    const SyncReplicaTlsMembershipAnchor& anchor,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership anchor label must not be empty");
    }
    validate_anchor_or_throw(anchor, label);
}

SyncReplicaTlsMembershipAnchor
sync_replica_tls_membership_genesis_anchor_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership genesis label must not be empty");
    }
    validate_identity_or_throw(folder_id, local_actor, label);
    return {0U, genesis_chain_digest(folder_id, local_actor)};
}

struct SyncReplicaTlsMembershipAuthority::State final {
    State(SyncReplicaTlsMembershipSnapshot snapshot_value,
          std::uint64_t state_generation_value,
          std::string previous_chain_digest_value,
          std::string chain_digest_value)
        : snapshot(std::move(snapshot_value)),
          state_generation(state_generation_value),
          previous_chain_digest(std::move(previous_chain_digest_value)),
          chain_digest(std::move(chain_digest_value)) {}

    SyncReplicaTlsMembershipSnapshot snapshot;
    std::uint64_t state_generation = 0U;
    std::string previous_chain_digest;
    std::string chain_digest;
};


SyncReplicaTlsMembershipSqliteSnapshot
inspect_sync_replica_tls_membership_sqlite_snapshot_read_only_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership read-only inspection label must not be empty");
    }
    validate_identity_or_throw(folder_id, local_actor, label);
    {
        auto database = borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " read-only connection proof");
        if (sqlite3_db_readonly(database.get(), "main") != 1) {
            throw std::runtime_error(
                label + " requires a read-only main database connection");
        }
    }
    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedMembershipState loaded = load_state_or_throw(
        db, folder_id, local_actor,
        SyncReplicaTlsPolicySqliteBackendDisposition::
            ForensicReadOnlyNamed,
        label + " snapshot");
    if (trusted_anchor.has_value()) {
        require_trusted_anchor_or_throw(
            loaded, *trusted_anchor, label + " snapshot");
    }
    if (loaded.current_snapshot.has_value()) {
        const auto& current = loaded.public_snapshot.history.back();
        auto state = std::make_shared<SyncReplicaTlsMembershipAuthority::State>(
            std::move(*loaded.current_snapshot), current.state_generation,
            current.previous_chain_digest, current.chain_digest);
        loaded.public_snapshot.current_authority =
            SyncReplicaTlsMembershipAuthority(std::move(state));
    }
    transaction.commit();
    return std::move(loaded.public_snapshot);
}


SyncReplicaTlsMembershipSqliteSnapshot
inspect_sync_replica_tls_membership_sqlite_snapshot_in_detached_read_only_image_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership detached read-only inspection label must not be empty");
    }
    validate_identity_or_throw(folder_id, local_actor, label);
    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedMembershipState loaded = load_state_or_throw(
        db, folder_id, local_actor,
        SyncReplicaTlsPolicySqliteBackendDisposition::
            ForensicReadOnlyDetached,
        label + " snapshot");
    if (trusted_anchor.has_value()) {
        require_trusted_anchor_or_throw(
            loaded, *trusted_anchor, label + " snapshot");
    }
    if (loaded.current_snapshot.has_value()) {
        const auto& current = loaded.public_snapshot.history.back();
        auto state = std::make_shared<SyncReplicaTlsMembershipAuthority::State>(
            std::move(*loaded.current_snapshot), current.state_generation,
            current.previous_chain_digest, current.chain_digest);
        loaded.public_snapshot.current_authority =
            SyncReplicaTlsMembershipAuthority(std::move(state));
    }
    transaction.commit();
    return std::move(loaded.public_snapshot);
}


const SyncReplicaTlsMembershipAuthority::State&
SyncReplicaTlsMembershipAuthority::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership authority label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " membership authority is inactive");
    }
    return *state_;
}

const SyncReplicaTlsMembershipSnapshot&
SyncReplicaTlsMembershipAuthority::snapshot() const {
    return require_state_or_throw("sync replica TLS membership authority")
        .snapshot;
}

std::uint64_t SyncReplicaTlsMembershipAuthority::state_generation() const {
    return require_state_or_throw("sync replica TLS membership generation")
        .state_generation;
}

const std::string&
SyncReplicaTlsMembershipAuthority::previous_chain_digest() const {
    return require_state_or_throw("sync replica TLS membership prior chain")
        .previous_chain_digest;
}

const std::string& SyncReplicaTlsMembershipAuthority::chain_digest() const {
    return require_state_or_throw("sync replica TLS membership chain")
        .chain_digest;
}

SyncReplicaTlsMembershipAnchor
SyncReplicaTlsMembershipAuthority::anchor() const {
    const State& state =
        require_state_or_throw("sync replica TLS membership anchor");
    return {state.state_generation, state.chain_digest};
}

SyncReplicaTlsMembershipSqliteOwner::SyncReplicaTlsMembershipSqliteOwner(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::string label)
    : SyncReplicaTlsMembershipSqliteOwner(
          db, std::move(folder_id), std::move(local_actor),
          SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed,
          std::move(label)) {}

SyncReplicaTlsMembershipSqliteOwner::SyncReplicaTlsMembershipSqliteOwner(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
    std::string label)
    : folder_id_(std::move(folder_id)),
      local_actor_(std::move(local_actor)),
      label_(std::move(label)),
      backend_disposition_(backend_disposition),
      database_(db, label_ + " exact database binding", backend_disposition_) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership SQLite owner label must not be empty");
    }
    validate_identity_or_throw(folder_id_, local_actor_, label_);
    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership owner construction");
    initialize_or_attest_schema_or_throw(
        database, folder_id_, local_actor_, backend_disposition_, label_);
    database_.require_current_or_throw(
        "membership owner post-initialization");
    (void)snapshot_or_throw();
}

SyncReplicaTlsMembershipSqliteSnapshot
SyncReplicaTlsMembershipSqliteOwner::snapshot_or_throw(
    std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor) {
    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership snapshot preflight");
    SyncSqliteTransaction transaction(
        database, label_ + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedMembershipState loaded = load_state_or_throw(
        database, folder_id_, local_actor_, backend_disposition_,
        label_ + " snapshot");
    if (trusted_anchor.has_value()) {
        require_trusted_anchor_or_throw(
            loaded, *trusted_anchor, label_ + " snapshot");
    }
    if (loaded.current_snapshot.has_value()) {
        const auto& current = loaded.public_snapshot.history.back();
        auto state = std::make_shared<SyncReplicaTlsMembershipAuthority::State>(
            std::move(*loaded.current_snapshot), current.state_generation,
            current.previous_chain_digest, current.chain_digest);
        loaded.public_snapshot.current_authority =
            SyncReplicaTlsMembershipAuthority(std::move(state));
    }
    transaction.commit();
    database_.require_current_or_throw(
        "membership snapshot post-commit");
    return std::move(loaded.public_snapshot);
}

SyncReplicaTlsMembershipAuthority
SyncReplicaTlsMembershipSqliteOwner::current_authority_or_throw(
    std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor) {
    SyncReplicaTlsMembershipSqliteSnapshot snapshot =
        snapshot_or_throw(std::move(trusted_anchor));
    if (!snapshot.current_authority.has_value()) {
        throw std::logic_error(
            label_ + " has no published membership authority");
    }
    return std::move(*snapshot.current_authority);
}

SyncReplicaTlsMembershipAuthority
SyncReplicaTlsMembershipSqliteOwner::publish_or_throw(
    const SyncReplicaTlsMembershipAnchor& expected_current,
    std::uint64_t policy_epoch,
    std::vector<SyncReplicaTlsMembershipEntry> entries) {
    if (backend_disposition_ !=
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed) {
        throw std::logic_error(
            label_ +
            " detached bootstrap image cannot publish membership authority");
    }
    validate_sync_replica_tls_membership_anchor_or_throw(
        expected_current, label_ + " expected current anchor");
    if (policy_epoch == 0U || policy_epoch > kMaxPersistentInteger) {
        throw std::invalid_argument(
            label_ + " policy epoch is not a positive SQLite integer");
    }

    // Complete caller-controlled allocation and canonical validation before the
    // SQLite writer cutpoint. No callback or external lookup runs while the
    // append transaction is live.
    SyncReplicaTlsMembershipSnapshot candidate(
        folder_id_, local_actor_, policy_epoch, std::move(entries),
        label_ + " candidate snapshot");
    for (const auto& entry : candidate.entries()) {
        if (entry.actor.epoch > kMaxPersistentInteger) {
            throw std::invalid_argument(
                label_ + " member actor epoch exceeds SQLite integer range");
        }
    }

    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership publish preflight");
    SyncSqliteTransaction transaction(
        database, label_ + " publish", SyncSqliteTransactionMode::Immediate);
    LoadedMembershipState loaded = load_state_or_throw(
        database, folder_id_, local_actor_, backend_disposition_,
        label_ + " publish preflight");
    const SyncReplicaTlsMembershipAnchor observed =
        loaded.public_snapshot.anchor();
    if (observed != expected_current) {
        throw std::runtime_error(
            label_ + " expected-current anchor is stale");
    }
    if (policy_epoch <= loaded.public_snapshot.current_policy_epoch) {
        throw std::invalid_argument(
            label_ + " policy epoch must advance monotonically");
    }
    if (!sync_replica_tls_membership_append_fits_hard_limits(
            loaded.public_snapshot.state_generation,
            loaded.retained_entry_rows,
            candidate.entry_count())) {
        throw std::length_error(
            label_ + " membership append exceeds retained-history hard ceilings");
    }
    if (loaded.public_snapshot.state_generation >= kMaxPersistentInteger) {
        throw std::runtime_error(
            label_ + " membership state generation exhausted");
    }

    const std::uint64_t generation =
        loaded.public_snapshot.state_generation + 1U;
    const std::uint64_t entry_count = candidate.entry_count();
    const std::string previous_chain =
        loaded.public_snapshot.current_chain_digest;
    const std::string snapshot_digest = candidate.snapshot_digest();
    const std::string chain_digest = update_chain_digest(
        folder_id_, local_actor_, generation, policy_epoch, entry_count,
        previous_chain, snapshot_digest);

    SyncSqliteStmt update = sqlite_prepare_or_throw(
        database,
        "INSERT INTO main.sync_replica_tls_membership_updates("
        "state_generation,policy_epoch,entry_count,previous_chain_digest,"
        "snapshot_digest,chain_digest) VALUES(?,?,?,?,?,?);",
        label_ + " publish history prepare");
    sqlite_bind_u64_or_throw(update.stmt, 1, generation, label_);
    sqlite_bind_u64_or_throw(update.stmt, 2, policy_epoch, label_);
    sqlite_bind_u64_or_throw(update.stmt, 3, entry_count, label_);
    sqlite_bind_text_or_throw(update.stmt, 4, previous_chain, label_);
    sqlite_bind_text_or_throw(update.stmt, 5, snapshot_digest, label_);
    sqlite_bind_text_or_throw(update.stmt, 6, chain_digest, label_);
    sqlite_step_done_or_throw(update.stmt, label_ + " publish history step");

    SyncSqliteStmt entry_insert = sqlite_prepare_or_throw(
        database,
        "INSERT INTO main.sync_replica_tls_membership_entries("
        "state_generation,spki_sha256,actor_device_id,actor_epoch)"
        "VALUES(?,?,?,?);",
        label_ + " publish entry prepare");
    for (const auto& entry : candidate.entries()) {
        sqlite_bind_u64_or_throw(
            entry_insert.stmt, 1, generation, label_);
        sqlite_bind_text_or_throw(
            entry_insert.stmt, 2, entry.spki_sha256, label_);
        sqlite_bind_text_or_throw(
            entry_insert.stmt, 3, entry.actor.device_id, label_);
        sqlite_bind_u64_or_throw(
            entry_insert.stmt, 4, entry.actor.epoch, label_);
        sqlite_step_done_or_throw(
            entry_insert.stmt, label_ + " publish entry step");
        const int reset = sqlite3_reset(entry_insert.stmt);
        if (reset != SQLITE_OK) {
            throw_sqlite_exception(
                sqlite3_db_handle(entry_insert.stmt), reset,
                label_ + " publish entry reset");
        }
        const int clear = sqlite3_clear_bindings(entry_insert.stmt);
        if (clear != SQLITE_OK) {
            throw_sqlite_exception(
                sqlite3_db_handle(entry_insert.stmt), clear,
                label_ + " publish entry clear");
        }
    }

    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        database,
        "UPDATE main.sync_replica_tls_membership_meta SET "
        "state_generation=?,current_policy_epoch=?,current_entry_count=?,"
        "current_snapshot_digest=?,current_chain_digest=? WHERE id=1;",
        label_ + " publish metadata prepare");
    sqlite_bind_u64_or_throw(meta.stmt, 1, generation, label_);
    sqlite_bind_u64_or_throw(meta.stmt, 2, policy_epoch, label_);
    sqlite_bind_u64_or_throw(meta.stmt, 3, entry_count, label_);
    sqlite_bind_text_or_throw(meta.stmt, 4, snapshot_digest, label_);
    sqlite_bind_text_or_throw(meta.stmt, 5, chain_digest, label_);
    sqlite_step_done_or_throw(meta.stmt, label_ + " publish metadata step");
    if (sqlite3_changes(sqlite3_db_handle(meta.stmt)) != 1) {
        throw std::runtime_error(
            label_ + " membership metadata update did not affect one row");
    }

    // Prepare every caller-visible return allocation before COMMIT. If local
    // allocation fails here, transaction teardown rolls the candidate policy
    // back instead of advancing durable membership without returning the
    // authority value the caller asked to publish.
    auto state = std::make_shared<SyncReplicaTlsMembershipAuthority::State>(
        std::move(candidate), generation, previous_chain, chain_digest);
    transaction.commit();
    database_.require_current_or_throw(
        "membership publish post-commit");
    return SyncReplicaTlsMembershipAuthority(std::move(state));
}

}  // namespace anonsync
