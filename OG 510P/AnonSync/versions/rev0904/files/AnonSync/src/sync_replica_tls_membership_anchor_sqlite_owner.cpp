#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
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
constexpr std::string_view kGenesisTransitionDigestDomain =
    "anonsync:sync-replica-tls-membership-anchor:genesis:v1";
constexpr std::string_view kTransitionDigestDomain =
    "anonsync:sync-replica-tls-membership-anchor:transition:v1";

constexpr std::string_view kMetaSchemaSql =
    "CREATE TABLE sync_replica_tls_membership_anchor_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=1),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
    "local_actor_epoch INTEGER NOT NULL CHECK(local_actor_epoch>0),"
    "transition_sequence INTEGER NOT NULL CHECK(transition_sequence>=0),"
    "current_state_generation INTEGER NOT NULL CHECK(current_state_generation>=0),"
    "current_chain_digest TEXT NOT NULL CHECK(length(current_chain_digest)=64),"
    "current_transition_digest TEXT NOT NULL CHECK(length(current_transition_digest)=64)) STRICT";

constexpr std::string_view kUpdatesSchemaSql =
    "CREATE TABLE sync_replica_tls_membership_anchor_updates("
    "transition_sequence INTEGER PRIMARY KEY CHECK(transition_sequence>0),"
    "previous_state_generation INTEGER NOT NULL CHECK(previous_state_generation>=0),"
    "previous_chain_digest TEXT NOT NULL CHECK(length(previous_chain_digest)=64),"
    "current_state_generation INTEGER NOT NULL CHECK(current_state_generation>previous_state_generation),"
    "current_chain_digest TEXT NOT NULL CHECK(length(current_chain_digest)=64),"
    "previous_transition_digest TEXT NOT NULL CHECK(length(previous_transition_digest)=64),"
    "transition_digest TEXT NOT NULL CHECK(length(transition_digest)=64)) STRICT";

struct SchemaDefinition final {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view sql;
};

constexpr std::array<SchemaDefinition, 2U> kSchema{{
    {"table", "sync_replica_tls_membership_anchor_meta",
     "sync_replica_tls_membership_anchor_meta", kMetaSchemaSql},
    {"table", "sync_replica_tls_membership_anchor_updates",
     "sync_replica_tls_membership_anchor_updates", kUpdatesSchemaSql},
}};

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

void append_actor(
    Sha256DigestBuilder& digest,
    const SyncReplicaActor& actor) {
    append_string(digest, actor.device_id);
    append_u64(digest, actor.epoch);
}

void append_anchor(
    Sha256DigestBuilder& digest,
    const SyncReplicaTlsMembershipAnchor& anchor) {
    append_u64(digest, anchor.state_generation);
    append_string(digest, anchor.chain_digest);
}

[[nodiscard]] std::string genesis_transition_digest(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    const SyncReplicaTlsMembershipAnchor& genesis_anchor) {
    Sha256DigestBuilder digest;
    append_string(digest, kGenesisTransitionDigestDomain);
    append_u64(digest, kSchemaVersion);
    append_string(digest, folder_id);
    append_actor(digest, local_actor);
    append_anchor(digest, genesis_anchor);
    return digest.finish_hex();
}

[[nodiscard]] std::string transition_digest(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::uint64_t transition_sequence,
    const SyncReplicaTlsMembershipAnchor& previous_anchor,
    const SyncReplicaTlsMembershipAnchor& current_anchor,
    std::string_view previous_transition_digest) {
    Sha256DigestBuilder digest;
    append_string(digest, kTransitionDigestDomain);
    append_u64(digest, kSchemaVersion);
    append_string(digest, folder_id);
    append_actor(digest, local_actor);
    append_u64(digest, transition_sequence);
    append_anchor(digest, previous_anchor);
    append_anchor(digest, current_anchor);
    append_string(digest, previous_transition_digest);
    return digest.finish_hex();
}

void validate_identity_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view label) {
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) +
            " folder_id is not a lowercase portable sync id");
    }
    if (!sync_id_is_valid(local_actor.device_id) ||
        local_actor.epoch == 0U ||
        local_actor.epoch > kMaxPersistentInteger) {
        throw std::invalid_argument(
            std::string(label) +
            " local actor identity is not persistable");
    }
}

[[nodiscard]] int step_row_or_done_or_throw(
    sqlite3_stmt* statement,
    const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW && result != SQLITE_DONE) {
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
    return result;
}

[[nodiscard]] std::uint64_t schema_object_count_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM main.sqlite_schema WHERE sql IS NOT NULL AND ("
        "name GLOB 'sync_replica_tls_membership_anchor_*' OR "
        "tbl_name IN ('sync_replica_tls_membership_anchor_meta',"
        "'sync_replica_tls_membership_anchor_updates'));",
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
        "name GLOB 'sync_replica_tls_membership_anchor_*' OR "
        "tbl_name IN ('sync_replica_tls_membership_anchor_meta',"
        "'sync_replica_tls_membership_anchor_updates'));",
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
    if (schema_object_count_or_throw(db, label) != kSchema.size()) {
        throw std::runtime_error(
            label + " membership anchor schema object count mismatch");
    }
    if (temp_schema_attachment_count_or_throw(db, label) != 0U) {
        throw std::runtime_error(
            label +
            " membership anchor tables have unowned temp schema attachments");
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
    SyncSqliteTransaction transaction(
        db, label + " schema initialization",
        SyncSqliteTransactionMode::Immediate);
    attest_sync_replica_tls_policy_sqlite_backend_or_throw(
        db, "membership anchor", label, backend_disposition);
    const std::uint64_t existing = schema_object_count_or_throw(db, label);
    if (existing == 0U) {
        const SyncReplicaTlsMembershipAnchor genesis =
            sync_replica_tls_membership_genesis_anchor_or_throw(
                folder_id, local_actor, label + " genesis");
        const std::string transition_genesis = genesis_transition_digest(
            folder_id, local_actor, genesis);
        for (const auto& definition : kSchema) {
            sqlite_exec_or_throw(
                db, std::string(definition.sql),
                label + " create " + std::string(definition.name));
        }
        SyncSqliteStmt insert = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_replica_tls_membership_anchor_meta("
            "id,schema_version,folder_id,local_device_id,local_actor_epoch,"
            "transition_sequence,current_state_generation,current_chain_digest,"
            "current_transition_digest)VALUES(1,1,?,?,?,0,0,?,?);",
            label + " initialize metadata prepare");
        sqlite_bind_text_or_throw(insert.stmt, 1, folder_id, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 2, local_actor.device_id, label);
        sqlite_bind_u64_or_throw(
            insert.stmt, 3, local_actor.epoch, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 4, genesis.chain_digest, label);
        sqlite_bind_text_or_throw(
            insert.stmt, 5, transition_genesis, label);
        sqlite_step_done_or_throw(
            insert.stmt, label + " initialize metadata step");
    }
    attest_schema_or_throw(db, label);
    transaction.commit();
}

[[nodiscard]] std::uint64_t history_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT count(*) FROM main."
        "sync_replica_tls_membership_anchor_updates;",
        label + " history row count prepare");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " history row count step") !=
        SQLITE_ROW) {
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

[[nodiscard]] SyncReplicaTlsMembershipAnchorSqliteSnapshot load_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    const SyncReplicaActor& expected_local_actor,
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
    const std::string& label) {
    attest_sync_replica_tls_policy_sqlite_backend_or_throw(
        db, "membership anchor", label, backend_disposition);
    attest_schema_or_throw(db, label);

    SyncReplicaTlsMembershipAnchorSqliteSnapshot snapshot;
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,local_device_id,local_actor_epoch,"
        "transition_sequence,current_state_generation,current_chain_digest,"
        "current_transition_digest FROM main."
        "sync_replica_tls_membership_anchor_meta WHERE id=1;",
        label + " metadata prepare");
    if (step_row_or_done_or_throw(meta.stmt, label + " metadata step") !=
        SQLITE_ROW) {
        throw std::runtime_error(
            label + " membership anchor metadata is missing");
    }
    const std::uint64_t schema_version = sqlite_column_u64_or_throw(
        meta.stmt, 0, label + " schema version");
    snapshot.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder identity");
    snapshot.local_actor.device_id = sqlite_column_text_or_throw(
        meta.stmt, 2, 128U, label + " local device identity");
    snapshot.local_actor.epoch = sqlite_column_u64_or_throw(
        meta.stmt, 3, label + " local actor epoch");
    snapshot.transition_sequence = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " transition sequence");
    snapshot.current_anchor.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " current state generation");
    snapshot.current_anchor.chain_digest = sqlite_column_text_or_throw(
        meta.stmt, 6, 64U, label + " current chain digest");
    snapshot.current_transition_digest = sqlite_column_text_or_throw(
        meta.stmt, 7, 64U, label + " current transition digest");
    if (step_row_or_done_or_throw(
            meta.stmt, label + " metadata trailing step") != SQLITE_DONE) {
        throw std::runtime_error(
            label + " membership anchor metadata is duplicated");
    }

    if (schema_version != kSchemaVersion) {
        throw std::runtime_error(
            label + " membership anchor schema version mismatch");
    }
    validate_identity_or_throw(
        snapshot.folder_id, snapshot.local_actor,
        label + " stored identity");
    if (snapshot.folder_id != expected_folder_id ||
        snapshot.local_actor != expected_local_actor) {
        throw std::runtime_error(
            label + " membership anchor database identity does not match owner");
    }
    if (snapshot.transition_sequence >
            kSyncReplicaTlsMembershipAnchorMaxTransitions ||
        snapshot.current_anchor.state_generation > kMaxPersistentInteger ||
        !is_lowercase_sha256_hex(snapshot.current_anchor.chain_digest) ||
        !is_lowercase_sha256_hex(snapshot.current_transition_digest)) {
        throw std::runtime_error(
            label + " membership anchor metadata is invalid");
    }

    const std::uint64_t history_rows = history_rows_or_throw(db, label);
    if (history_rows > kSyncReplicaTlsMembershipAnchorMaxTransitions) {
        throw std::runtime_error(
            label + " membership anchor history exceeds its hard ceiling");
    }
    snapshot.history.reserve(static_cast<std::size_t>(history_rows));

    SyncReplicaTlsMembershipAnchor previous_anchor =
        sync_replica_tls_membership_genesis_anchor_or_throw(
            snapshot.folder_id, snapshot.local_actor,
            label + " reconstructed genesis");
    std::string previous_transition_digest = genesis_transition_digest(
        snapshot.folder_id, snapshot.local_actor, previous_anchor);
    std::uint64_t expected_sequence = 1U;

    SyncSqliteStmt updates = sqlite_prepare_or_throw(
        db,
        "SELECT transition_sequence,previous_state_generation,"
        "previous_chain_digest,current_state_generation,current_chain_digest,"
        "previous_transition_digest,transition_digest FROM main."
        "sync_replica_tls_membership_anchor_updates "
        "ORDER BY transition_sequence;",
        label + " history prepare");
    for (;;) {
        const int step = step_row_or_done_or_throw(
            updates.stmt, label + " history step");
        if (step == SQLITE_DONE) break;

        SyncReplicaTlsMembershipAnchorTransition transition;
        transition.transition_sequence = sqlite_column_u64_or_throw(
            updates.stmt, 0, label + " transition sequence");
        transition.previous_anchor.state_generation =
            sqlite_column_u64_or_throw(
                updates.stmt, 1, label + " previous state generation");
        transition.previous_anchor.chain_digest =
            sqlite_column_text_or_throw(
                updates.stmt, 2, 64U, label + " previous chain digest");
        transition.current_anchor.state_generation =
            sqlite_column_u64_or_throw(
                updates.stmt, 3, label + " current state generation");
        transition.current_anchor.chain_digest =
            sqlite_column_text_or_throw(
                updates.stmt, 4, 64U, label + " current chain digest");
        transition.previous_transition_digest =
            sqlite_column_text_or_throw(
                updates.stmt, 5, 64U,
                label + " previous transition digest");
        transition.transition_digest = sqlite_column_text_or_throw(
            updates.stmt, 6, 64U, label + " transition digest");

        if (transition.transition_sequence != expected_sequence ||
            transition.transition_sequence >
                kSyncReplicaTlsMembershipAnchorMaxTransitions) {
            throw std::runtime_error(
                label +
                " membership anchor transition sequence is not contiguous");
        }
        validate_sync_replica_tls_membership_anchor_or_throw(
            transition.previous_anchor,
            label + " retained previous anchor");
        validate_sync_replica_tls_membership_anchor_or_throw(
            transition.current_anchor,
            label + " retained current anchor");
        if (transition.current_anchor.state_generation <=
            transition.previous_anchor.state_generation) {
            throw std::runtime_error(
                label + " membership anchor transition is not monotonic");
        }
        if (transition.previous_anchor != previous_anchor ||
            transition.previous_transition_digest !=
                previous_transition_digest) {
            throw std::runtime_error(
                label + " membership anchor history link is invalid");
        }
        const std::string derived = transition_digest(
            snapshot.folder_id, snapshot.local_actor,
            transition.transition_sequence, transition.previous_anchor,
            transition.current_anchor,
            transition.previous_transition_digest);
        if (derived != transition.transition_digest) {
            throw std::runtime_error(
                label + " membership anchor transition digest mismatch");
        }

        previous_anchor = transition.current_anchor;
        previous_transition_digest = transition.transition_digest;
        ++expected_sequence;
        snapshot.history.push_back(std::move(transition));
    }

    if (history_rows != snapshot.history.size() ||
        snapshot.transition_sequence != snapshot.history.size()) {
        throw std::runtime_error(
            label + " membership anchor metadata sequence does not match history");
    }
    if (snapshot.current_anchor != previous_anchor ||
        snapshot.current_transition_digest != previous_transition_digest) {
        throw std::runtime_error(
            label + " current membership anchor metadata is inconsistent");
    }
    return snapshot;
}

}  // namespace

SyncReplicaTlsMembershipAnchorSqliteOwner::
    SyncReplicaTlsMembershipAnchorSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        std::string label)
    : SyncReplicaTlsMembershipAnchorSqliteOwner(
          db, std::move(folder_id), std::move(local_actor),
          SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed,
          std::move(label)) {}

SyncReplicaTlsMembershipAnchorSqliteOwner::
    SyncReplicaTlsMembershipAnchorSqliteOwner(
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
    // DetachedBootstrapImage is a genesis-image construction authority only.
    // advance_or_throw() rejects it so an anonymous/private SQLite namespace
    // cannot become a durable membership-anchor history by accident.
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership anchor SQLite owner label must not be empty");
    }
    validate_identity_or_throw(folder_id_, local_actor_, label_);
    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership anchor owner construction");
    initialize_or_attest_schema_or_throw(
        database, folder_id_, local_actor_, backend_disposition_, label_);
    database_.require_current_or_throw(
        "membership anchor owner post-initialization");
    (void)snapshot_or_throw();
}

SyncReplicaTlsMembershipAnchorSqliteSnapshot
SyncReplicaTlsMembershipAnchorSqliteOwner::snapshot_or_throw() {
    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership anchor snapshot preflight");
    SyncSqliteTransaction transaction(
        database, label_ + " snapshot", SyncSqliteTransactionMode::Deferred);
    SyncReplicaTlsMembershipAnchorSqliteSnapshot snapshot =
        load_state_or_throw(
            database, folder_id_, local_actor_, backend_disposition_,
            label_ + " snapshot");
    transaction.commit();
    database_.require_current_or_throw(
        "membership anchor snapshot post-commit");
    return snapshot;
}

SyncReplicaTlsMembershipAnchorAdvanceResult
SyncReplicaTlsMembershipAnchorSqliteOwner::advance_or_throw(
    const SyncReplicaTlsMembershipAnchor& expected_current,
    const SyncReplicaTlsMembershipAnchor& next) {
    if (backend_disposition_ !=
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed) {
        throw std::logic_error(
            label_ +
            " detached bootstrap image cannot advance membership anchor");
    }
    validate_sync_replica_tls_membership_anchor_or_throw(
        expected_current, label_ + " expected current anchor");
    validate_sync_replica_tls_membership_anchor_or_throw(
        next, label_ + " next anchor");
    if (next.state_generation <= expected_current.state_generation) {
        throw std::invalid_argument(
            label_ + " next anchor must advance generation strictly");
    }

    SyncSqliteDbHandleSlot& database = database_.database_or_throw(
        "membership anchor advance preflight");
    SyncSqliteTransaction transaction(
        database, label_ + " advance", SyncSqliteTransactionMode::Immediate);
    SyncReplicaTlsMembershipAnchorSqliteSnapshot loaded =
        load_state_or_throw(
            database, folder_id_, local_actor_, backend_disposition_,
            label_ + " advance preflight");
    const SyncReplicaTlsMembershipAnchor observed = loaded.current_anchor;

    if (observed == next) {
        SyncReplicaTlsMembershipAnchorAdvanceResult result{
            SyncReplicaTlsMembershipAnchorAdvanceDisposition::AlreadyCurrent,
            observed,
            observed,
            loaded.transition_sequence,
            loaded.current_transition_digest};
        transaction.commit();
        database_.require_current_or_throw(
            "membership anchor idempotent advance post-commit");
        return result;
    }
    if (observed != expected_current) {
        SyncReplicaTlsMembershipAnchorAdvanceResult result{
            SyncReplicaTlsMembershipAnchorAdvanceDisposition::StaleExpected,
            observed,
            observed,
            loaded.transition_sequence,
            loaded.current_transition_digest};
        transaction.commit();
        database_.require_current_or_throw(
            "membership anchor stale advance post-commit");
        return result;
    }
    if (loaded.transition_sequence >=
        kSyncReplicaTlsMembershipAnchorMaxTransitions) {
        throw std::length_error(
            label_ + " membership anchor transition history is exhausted");
    }
    if (loaded.transition_sequence >= kMaxPersistentInteger) {
        throw std::runtime_error(
            label_ + " membership anchor transition sequence exhausted");
    }

    const std::uint64_t sequence = loaded.transition_sequence + 1U;
    const std::string previous_transition_digest =
        loaded.current_transition_digest;
    const std::string next_transition_digest = transition_digest(
        folder_id_, local_actor_, sequence, observed, next,
        previous_transition_digest);

    SyncSqliteStmt update = sqlite_prepare_or_throw(
        database,
        "INSERT INTO main.sync_replica_tls_membership_anchor_updates("
        "transition_sequence,previous_state_generation,previous_chain_digest,"
        "current_state_generation,current_chain_digest,"
        "previous_transition_digest,transition_digest)"
        "VALUES(?,?,?,?,?,?,?);",
        label_ + " advance history prepare");
    sqlite_bind_u64_or_throw(update.stmt, 1, sequence, label_);
    sqlite_bind_u64_or_throw(
        update.stmt, 2, observed.state_generation, label_);
    sqlite_bind_text_or_throw(
        update.stmt, 3, observed.chain_digest, label_);
    sqlite_bind_u64_or_throw(
        update.stmt, 4, next.state_generation, label_);
    sqlite_bind_text_or_throw(update.stmt, 5, next.chain_digest, label_);
    sqlite_bind_text_or_throw(
        update.stmt, 6, previous_transition_digest, label_);
    sqlite_bind_text_or_throw(
        update.stmt, 7, next_transition_digest, label_);
    sqlite_step_done_or_throw(
        update.stmt, label_ + " advance history step");

    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        database,
        "UPDATE main.sync_replica_tls_membership_anchor_meta SET "
        "transition_sequence=?,current_state_generation=?,"
        "current_chain_digest=?,current_transition_digest=? WHERE id=1;",
        label_ + " advance metadata prepare");
    sqlite_bind_u64_or_throw(meta.stmt, 1, sequence, label_);
    sqlite_bind_u64_or_throw(
        meta.stmt, 2, next.state_generation, label_);
    sqlite_bind_text_or_throw(meta.stmt, 3, next.chain_digest, label_);
    sqlite_bind_text_or_throw(
        meta.stmt, 4, next_transition_digest, label_);
    sqlite_step_done_or_throw(
        meta.stmt, label_ + " advance metadata step");
    if (sqlite3_changes(sqlite3_db_handle(meta.stmt)) != 1) {
        throw std::runtime_error(
            label_ +
            " membership anchor metadata update did not affect one row");
    }

    SyncReplicaTlsMembershipAnchorAdvanceResult result{
        SyncReplicaTlsMembershipAnchorAdvanceDisposition::Advanced,
        observed,
        next,
        sequence,
        next_transition_digest};
    transaction.commit();
    database_.require_current_or_throw(
        "membership anchor advance post-commit");
    return result;
}

}  // namespace anonsync
