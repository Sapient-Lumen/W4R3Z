#include "sync_checkpoint_owner_fence.hpp"

#include "sha256_digest.hpp"
#include "sync_checkpoint_owner_fence_policy.hpp"
#include "sync_checkpoint_owner_schema.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <initializer_list>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::sync_checkpoint_owner_fence_internal {
namespace {

constexpr std::string_view kOwnerModeTable =
    "sync_session_checkpoint_owner_modes";
constexpr std::string_view kOwnerLockTable =
    "sync_session_resume_transfer_daemon_owner_locks";
constexpr std::string_view kOwnerRequiredMode = "owner-required";

bool ascii_lower_alnum(char c) noexcept {
    return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

bool portable_sync_id(std::string_view value) noexcept {
    if (value.empty() || value.size() > 128) return false;
    if (!ascii_lower_alnum(value.front()) ||
        !ascii_lower_alnum(value.back())) {
        return false;
    }
    for (const char raw_c : value) {
        const unsigned char c = static_cast<unsigned char>(raw_c);
        if (ascii_lower_alnum(static_cast<char>(c)) || c == '.' || c == '_' ||
            c == '-') {
            continue;
        }
        return false;
    }
    return true;
}

std::string length_prefixed_owner_tuple(
    const std::string& domain,
    std::initializer_list<std::pair<std::string_view, std::string>> fields) {
    // Deliberately duplicates the tiny canonical framing algorithm rather than
    // depending on the JSON/crypto monolith. This invariant owner must stay a
    // focused SQLite + SHA-256 boundary so recipient checks remain cheap to
    // compile, test, and reuse.
    std::string out = "anonsync-length-prefixed-tuple-v1";
    const auto append_component = [&out](std::string_view value) {
        out += std::to_string(value.size());
        out.push_back(':');
        out.append(value.data(), value.size());
    };
    append_component(domain);
    for (const auto& [name, value] : fields) {
        append_component(name);
        append_component(value);
    }
    return out;
}

void require_write_transaction_or_throw(sqlite3* db,
                                        const std::string& context) {
    if (db == nullptr) {
        throw std::invalid_argument(context + " database handle is null");
    }
    if (sqlite3_txn_state(db, "main") != SQLITE_TXN_WRITE) {
        throw std::logic_error(
            context +
            " owner fence must run inside the recipient write transaction");
    }
}

bool owner_mode_table_exists_or_throw(sqlite3* db,
                                      const std::string& context) {
    return sqlite_table_exists_or_throw(
        db, std::string(kOwnerModeTable), context + " owner mode table probe");
}

sync_checkpoint_owner_fence_policy::StoredOwnerLockEvidence
load_stored_owner_lock_evidence_or_throw(sqlite3* db,
                                         const std::string& session_id,
                                         const std::string& context) {
    using Evidence =
        sync_checkpoint_owner_fence_policy::StoredOwnerLockEvidence;
    Evidence stored;

    // Older checkpoint databases legitimately predate the owner table. An
    // absent table is represented as absent durable ownership. Once the table
    // is present, every row is interpreted exactly and malformed evidence
    // fails closed.
    if (!sqlite_table_exists_or_throw(
            db, std::string(kOwnerLockTable), context + " owner table probe")) {
        return stored;
    }

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT session_id, daemon_id, worker_id, owner_lock_id, "
        "owner_lock_epoch, acquired_at_epoch, expires_at_epoch, "
        "released_at_epoch, updated_at_epoch, lock_state "
        "FROM main.sync_session_resume_transfer_daemon_owner_locks "
        "WHERE session_id=?;",
        context + " owner row prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, context + " owner row session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return stored;
    if (rc != SQLITE_ROW) {
        throw std::runtime_error(
            sqlite_error_message(db, context + " owner row query"));
    }

    stored.present = true;
    stored.session_id = sqlite_column_text_or_throw(
        stmt.stmt, 0, context + " owner row session column");
    stored.daemon_id = sqlite_column_text_or_throw(
        stmt.stmt, 1, context + " owner row daemon column");
    stored.worker_id = sqlite_column_text_or_throw(
        stmt.stmt, 2, context + " owner row worker column");
    stored.owner_lock_id = sqlite_column_text_or_throw(
        stmt.stmt, 3, context + " owner row id column");
    stored.owner_lock_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 4, context + " owner row generation column");
    stored.acquired_at_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 5, context + " owner row acquisition column");
    stored.expires_at_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 6, context + " owner row expiration column");
    stored.released_at_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 7, context + " owner row release column");
    stored.updated_at_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 8, context + " owner row update column");
    stored.lock_state = sqlite_column_text_or_throw(
        stmt.stmt, 9, context + " owner row state column");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(context + " owner row is not unique");
    }

    try {
        stored.owner_lock_id_is_canonical =
            stored.owner_lock_id == owner_lock_id_or_throw(
                stored.session_id,
                stored.daemon_id,
                stored.worker_id,
                stored.owner_lock_epoch);
    } catch (const std::exception&) {
        stored.owner_lock_id_is_canonical = false;
    }
    return stored;
}

sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence
load_stored_owner_mode_evidence_or_throw(sqlite3* db,
                                         const std::string& session_id,
                                         const std::string& context) {
    using Evidence =
        sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence;
    Evidence mode;
    if (!owner_mode_table_exists_or_throw(db, context)) return mode;

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT session_id, ownership_mode, latest_owner_lock_epoch, "
        "mode_updated_at_epoch, administrative_disable_evidence_id "
        "FROM main.sync_session_checkpoint_owner_modes WHERE session_id=?;",
        context + " owner mode row prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, context + " owner mode row session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return mode;
    if (rc != SQLITE_ROW) {
        throw std::runtime_error(
            sqlite_error_message(db, context + " owner mode row query"));
    }

    mode.present = true;
    mode.session_id = sqlite_column_text_or_throw(
        stmt.stmt, 0, context + " owner mode session column");
    mode.ownership_mode = sqlite_column_text_or_throw(
        stmt.stmt, 1, context + " owner mode state column");
    mode.latest_owner_lock_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 2, context + " owner mode generation column");
    mode.mode_updated_at_epoch = sqlite_column_u64_or_throw(
        stmt.stmt, 3, context + " owner mode update column");
    mode.administrative_disable_evidence_id = sqlite_column_text_or_throw(
        stmt.stmt, 4, context + " owner mode disable evidence column");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(context + " owner mode row is not unique");
    }
    return mode;
}

sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence
backfill_legacy_owner_mode_in_write_transaction_or_throw(
    sqlite3* db,
    const sync_checkpoint_owner_fence_policy::StoredOwnerLockEvidence& stored,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    if (!stored.present) return {};
    if (!owner_mode_table_exists_or_throw(db, context)) {
        throw std::runtime_error(
            context +
            " sticky owner mode table is missing for durable owner evidence");
    }

    SyncSqliteStmt insert_stmt = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_session_checkpoint_owner_modes"
        "(session_id, ownership_mode, latest_owner_lock_epoch, "
        "mode_updated_at_epoch, administrative_disable_evidence_id) "
        "SELECT ?, 'owner-required', ?, ?, '' "
        "WHERE NOT EXISTS(SELECT 1 FROM main.sync_session_checkpoint_owner_modes "
        "WHERE session_id=?);",
        context + " legacy owner mode backfill prepare");
    sqlite_bind_text_or_throw(
        insert_stmt.stmt, 1, stored.session_id, context + " legacy mode session");
    sqlite_bind_u64_or_throw(
        insert_stmt.stmt,
        2,
        stored.owner_lock_epoch,
        context + " legacy mode generation");
    sqlite_bind_u64_or_throw(
        insert_stmt.stmt,
        3,
        stored.updated_at_epoch,
        context + " legacy mode update");
    sqlite_bind_text_or_throw(
        insert_stmt.stmt, 4, stored.session_id, context + " legacy mode guard");
    sqlite_step_done_or_throw(
        insert_stmt.stmt, context + " legacy owner mode backfill");

    const auto mode = load_stored_owner_mode_evidence_or_throw(
        db, stored.session_id, context + " legacy mode proof");
    if (!mode.present || mode.session_id != stored.session_id ||
        mode.ownership_mode != kOwnerRequiredMode ||
        mode.latest_owner_lock_epoch != stored.owner_lock_epoch ||
        mode.mode_updated_at_epoch != stored.updated_at_epoch ||
        !mode.administrative_disable_evidence_id.empty()) {
        throw std::runtime_error(
            context + " legacy owner mode backfill did not reload exact evidence");
    }
    return mode;
}

sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence
load_or_backfill_owner_mode_in_write_transaction_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const sync_checkpoint_owner_fence_policy::StoredOwnerLockEvidence& stored,
    const std::string& context) {
    auto mode = load_stored_owner_mode_evidence_or_throw(db, session_id, context);
    if (!mode.present && stored.present) {
        mode = backfill_legacy_owner_mode_in_write_transaction_or_throw(
            db, stored, context);
    }
    return mode;
}

void write_next_owner_mode_generation_or_throw(
    sqlite3* db,
    const sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence& existing,
    const std::string& session_id,
    std::uint64_t next_generation,
    std::uint64_t acquired_at_epoch,
    const std::string& context) {
    if (!owner_mode_table_exists_or_throw(db, context)) {
        throw std::runtime_error(
            context +
            " cannot mint owner authority without the sticky owner mode table");
    }

    if (!existing.present) {
        SyncSqliteStmt insert_stmt = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_session_checkpoint_owner_modes"
            "(session_id, ownership_mode, latest_owner_lock_epoch, "
            "mode_updated_at_epoch, administrative_disable_evidence_id) "
            "VALUES(?,'owner-required',?,?,'');",
            context + " owner mode insert prepare");
        sqlite_bind_text_or_throw(
            insert_stmt.stmt, 1, session_id, context + " owner mode insert session");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt,
            2,
            next_generation,
            context + " owner mode insert generation");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt,
            3,
            acquired_at_epoch,
            context + " owner mode insert update");
        sqlite_step_done_or_throw(
            insert_stmt.stmt, context + " owner mode insert row");
        if (sqlite3_changes(db) != 1) {
            throw std::runtime_error(
                context + " owner mode insert did not affect exactly one row");
        }
        return;
    }

    SyncSqliteStmt update_stmt = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_session_checkpoint_owner_modes "
        "SET ownership_mode='owner-required', latest_owner_lock_epoch=?, "
        "mode_updated_at_epoch=?, administrative_disable_evidence_id='' "
        "WHERE session_id=? AND ownership_mode=? "
        "AND latest_owner_lock_epoch=? AND mode_updated_at_epoch=? "
        "AND administrative_disable_evidence_id=?;",
        context + " owner mode update prepare");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt,
        1,
        next_generation,
        context + " owner mode next generation");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt,
        2,
        acquired_at_epoch,
        context + " owner mode next update");
    sqlite_bind_text_or_throw(
        update_stmt.stmt, 3, session_id, context + " owner mode update session");
    sqlite_bind_text_or_throw(
        update_stmt.stmt,
        4,
        existing.ownership_mode,
        context + " owner mode prior state");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt,
        5,
        existing.latest_owner_lock_epoch,
        context + " owner mode prior generation");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt,
        6,
        existing.mode_updated_at_epoch,
        context + " owner mode prior update");
    sqlite_bind_text_or_throw(
        update_stmt.stmt,
        7,
        existing.administrative_disable_evidence_id,
        context + " owner mode prior disable evidence");
    sqlite_step_done_or_throw(
        update_stmt.stmt, context + " owner mode compare-and-replace");
    if (sqlite3_changes(db) != 1) {
        throw std::runtime_error(
            context +
            " owner mode compare-and-replace did not affect exactly one row");
    }
}

}  // namespace

void ensure_checkpoint_owner_mode_schema_or_throw(
    sqlite3* db,
    const std::string& context) {
    sync_checkpoint_owner_schema_internal::
        ensure_checkpoint_owner_schema_or_throw(
            db, context + " exact checkpoint owner schema");
}

std::string owner_lock_id_or_throw(const std::string& session_id,
                                   const std::string& daemon_id,
                                   const std::string& worker_id,
                                   std::uint64_t owner_lock_epoch) {
    if (!portable_sync_id(session_id) || !portable_sync_id(daemon_id) ||
        !portable_sync_id(worker_id)) {
        throw std::runtime_error(
            "sync session checkpoint daemon owner lock requires portable sync ids");
    }
    if (owner_lock_epoch == 0) {
        throw std::runtime_error(
            "sync session checkpoint daemon owner generation must be positive");
    }
    const std::string material = length_prefixed_owner_tuple(
        "anonsync-sync-checkpoint-resume-transfer-daemon-owner-lock-v1",
        {{"session_id", session_id},
         {"daemon_id", daemon_id},
         {"worker_id", worker_id},
         {"owner_lock_epoch", std::to_string(owner_lock_epoch)}});
    return "sync-resume-daemon-owner-lock:v1:" + sha256_hex(material);
}

MintedDaemonOwnerLockRecord
acquire_owner_generation_in_write_transaction_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t acquired_at_epoch,
    std::uint64_t owner_lock_seconds,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    sync_checkpoint_owner_schema_internal::
        attest_checkpoint_owner_schema_or_throw(
            db, context + " checkpoint owner schema attestation");

    const auto existing =
        load_stored_owner_lock_evidence_or_throw(db, session_id, context);
    const auto mode =
        load_stored_owner_mode_evidence_or_throw(db, session_id, context);
    sync_checkpoint_owner_fence_policy::AcquisitionRequest request;
    request.session_id = session_id;
    request.daemon_id = daemon_id;
    request.worker_id = worker_id;
    request.acquired_at_epoch = acquired_at_epoch;
    request.owner_lock_seconds = owner_lock_seconds;
    const auto decision = sync_checkpoint_owner_fence_policy::plan_acquisition(
        mode, existing, request);
    if (!decision.allowed) {
        std::string detail = decision.reason;
        if (existing.present && existing.lock_state == "held") {
            detail += " (durable owner=" + existing.daemon_id +
                      ", generation=" +
                      std::to_string(existing.owner_lock_epoch) +
                      ", expires=" +
                      std::to_string(existing.expires_at_epoch) + ")";
        }
        throw std::runtime_error(context + " acquisition rejected: " + detail);
    }

    MintedDaemonOwnerLockRecord out;
    out.daemon_id = daemon_id;
    out.worker_id = worker_id;
    out.owner_lock_epoch = decision.owner_lock_epoch;
    out.acquired_at_epoch = acquired_at_epoch;
    out.expires_at_epoch = decision.expires_at_epoch;
    out.acquired = true;
    out.reclaimed_expired = decision.reclaimed_expired;
    out.owner_lock_id = owner_lock_id_or_throw(
        session_id, daemon_id, worker_id, out.owner_lock_epoch);

    write_next_owner_mode_generation_or_throw(
        db,
        mode,
        session_id,
        out.owner_lock_epoch,
        out.acquired_at_epoch,
        context);

    if (existing.present) {
        SyncSqliteStmt update_stmt = sqlite_prepare_or_throw(
            db,
            "UPDATE main.sync_session_resume_transfer_daemon_owner_locks "
            "SET daemon_id=?, worker_id=?, owner_lock_id=?, owner_lock_epoch=?, "
            "acquired_at_epoch=?, expires_at_epoch=?, released_at_epoch=0, "
            "lock_state='held', updated_at_epoch=? "
            "WHERE session_id=? AND owner_lock_epoch=?;",
            context + " update prepare");
        sqlite_bind_text_or_throw(
            update_stmt.stmt, 1, daemon_id, context + " update daemon");
        sqlite_bind_text_or_throw(
            update_stmt.stmt, 2, worker_id, context + " update worker");
        sqlite_bind_text_or_throw(
            update_stmt.stmt, 3, out.owner_lock_id, context + " update id");
        sqlite_bind_u64_or_throw(
            update_stmt.stmt, 4, out.owner_lock_epoch, context + " update epoch");
        sqlite_bind_u64_or_throw(
            update_stmt.stmt,
            5,
            out.acquired_at_epoch,
            context + " update acquired");
        sqlite_bind_u64_or_throw(
            update_stmt.stmt,
            6,
            out.expires_at_epoch,
            context + " update expires");
        sqlite_bind_u64_or_throw(
            update_stmt.stmt,
            7,
            out.acquired_at_epoch,
            context + " update updated");
        sqlite_bind_text_or_throw(
            update_stmt.stmt, 8, session_id, context + " update session");
        sqlite_bind_u64_or_throw(
            update_stmt.stmt,
            9,
            existing.owner_lock_epoch,
            context + " update prior epoch");
        sqlite_step_done_or_throw(update_stmt.stmt, context + " update row");
        if (sqlite3_changes(db) != 1) {
            throw std::runtime_error(
                context +
                " compare-and-replace did not affect exactly one row");
        }
    } else {
        SyncSqliteStmt insert_stmt = sqlite_prepare_or_throw(
            db,
            "INSERT INTO main.sync_session_resume_transfer_daemon_owner_locks"
            "(session_id, daemon_id, worker_id, owner_lock_id, owner_lock_epoch, "
            "acquired_at_epoch, expires_at_epoch, released_at_epoch, lock_state, "
            "updated_at_epoch) VALUES(?,?,?,?,?,?,?,0,'held',?);",
            context + " insert prepare");
        sqlite_bind_text_or_throw(
            insert_stmt.stmt, 1, session_id, context + " insert session");
        sqlite_bind_text_or_throw(
            insert_stmt.stmt, 2, daemon_id, context + " insert daemon");
        sqlite_bind_text_or_throw(
            insert_stmt.stmt, 3, worker_id, context + " insert worker");
        sqlite_bind_text_or_throw(
            insert_stmt.stmt, 4, out.owner_lock_id, context + " insert id");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt, 5, out.owner_lock_epoch, context + " insert epoch");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt,
            6,
            out.acquired_at_epoch,
            context + " insert acquired");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt,
            7,
            out.expires_at_epoch,
            context + " insert expires");
        sqlite_bind_u64_or_throw(
            insert_stmt.stmt,
            8,
            out.acquired_at_epoch,
            context + " insert updated");
        sqlite_step_done_or_throw(insert_stmt.stmt, context + " insert row");
        if (sqlite3_changes(db) != 1) {
            throw std::runtime_error(
                context + " insert did not affect exactly one row");
        }
    }

    SyncSqliteStmt proof_stmt = sqlite_prepare_or_throw(
        db,
        "SELECT daemon_id, worker_id, owner_lock_id, owner_lock_epoch, "
        "acquired_at_epoch, expires_at_epoch, released_at_epoch, lock_state, "
        "updated_at_epoch FROM main.sync_session_resume_transfer_daemon_owner_locks "
        "WHERE session_id=?;",
        context + " proof prepare");
    sqlite_bind_text_or_throw(
        proof_stmt.stmt, 1, session_id, context + " proof session");
    if (sqlite3_step(proof_stmt.stmt) != SQLITE_ROW) {
        throw std::runtime_error(context + " proof row is missing");
    }
    const bool exact =
        sqlite_column_text_or_throw(
            proof_stmt.stmt, 0, context + " proof daemon") == daemon_id &&
        sqlite_column_text_or_throw(
            proof_stmt.stmt, 1, context + " proof worker") == worker_id &&
        sqlite_column_text_or_throw(
            proof_stmt.stmt, 2, context + " proof id") == out.owner_lock_id &&
        sqlite_column_u64_or_throw(
            proof_stmt.stmt, 3, context + " proof epoch") ==
            out.owner_lock_epoch &&
        sqlite_column_u64_or_throw(
            proof_stmt.stmt, 4, context + " proof acquired") ==
            out.acquired_at_epoch &&
        sqlite_column_u64_or_throw(
            proof_stmt.stmt, 5, context + " proof expires") ==
            out.expires_at_epoch &&
        sqlite_column_u64_or_throw(
            proof_stmt.stmt, 6, context + " proof released") == 0 &&
        sqlite_column_text_or_throw(
            proof_stmt.stmt, 7, context + " proof state") == "held" &&
        sqlite_column_u64_or_throw(
            proof_stmt.stmt, 8, context + " proof updated") ==
            out.acquired_at_epoch;
    if (!exact || sqlite3_step(proof_stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(
            context + " proof did not reload exact minted evidence");
    }

    const auto mode_proof = load_stored_owner_mode_evidence_or_throw(
        db, session_id, context + " owner mode proof");
    if (!mode_proof.present ||
        mode_proof.ownership_mode != kOwnerRequiredMode ||
        mode_proof.latest_owner_lock_epoch != out.owner_lock_epoch ||
        mode_proof.mode_updated_at_epoch != out.acquired_at_epoch ||
        !mode_proof.administrative_disable_evidence_id.empty()) {
        throw std::runtime_error(
            context + " proof did not reload exact sticky owner mode evidence");
    }
    return out;
}

void release_owner_generation_in_write_transaction_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t released_at_epoch,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    if (released_at_epoch == 0) {
        throw std::runtime_error(context + " release time must be positive");
    }
    require_recipient_write_authority_or_throw(
        db, session_id, capability, released_at_epoch, context);

    SyncSqliteStmt acquired_stmt = sqlite_prepare_or_throw(
        db,
        "SELECT acquired_at_epoch FROM "
        "sync_session_resume_transfer_daemon_owner_locks "
        "WHERE session_id=? AND owner_lock_id=? AND owner_lock_epoch=? "
        "AND daemon_id=? AND worker_id=? AND lock_state='held' "
        "AND released_at_epoch=0;",
        context + " release proof prepare");
    sqlite_bind_text_or_throw(
        acquired_stmt.stmt, 1, session_id, context + " release proof session");
    sqlite_bind_text_or_throw(
        acquired_stmt.stmt,
        2,
        capability.owner_lock_id,
        context + " release proof id");
    sqlite_bind_u64_or_throw(
        acquired_stmt.stmt,
        3,
        capability.owner_lock_epoch,
        context + " release proof epoch");
    sqlite_bind_text_or_throw(
        acquired_stmt.stmt,
        4,
        capability.daemon_id,
        context + " release proof daemon");
    sqlite_bind_text_or_throw(
        acquired_stmt.stmt,
        5,
        capability.worker_id,
        context + " release proof worker");
    if (sqlite3_step(acquired_stmt.stmt) != SQLITE_ROW) {
        throw std::runtime_error(context + " exact owner row was not found");
    }
    const std::uint64_t acquired_at_epoch = sqlite_column_u64_or_throw(
        acquired_stmt.stmt, 0, context + " release acquired");
    if (sqlite3_step(acquired_stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(context + " release row is not unique");
    }
    if (released_at_epoch < acquired_at_epoch) {
        throw std::runtime_error(context + " release time predates acquisition");
    }

    SyncSqliteStmt update_stmt = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_session_resume_transfer_daemon_owner_locks "
        "SET released_at_epoch=?, lock_state='released', updated_at_epoch=? "
        "WHERE session_id=? AND daemon_id=? AND worker_id=? AND owner_lock_id=? "
        "AND owner_lock_epoch=? AND lock_state='held' AND released_at_epoch=0;",
        context + " release update prepare");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt, 1, released_at_epoch, context + " release released");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt, 2, released_at_epoch, context + " release updated");
    sqlite_bind_text_or_throw(
        update_stmt.stmt, 3, session_id, context + " release session");
    sqlite_bind_text_or_throw(
        update_stmt.stmt, 4, capability.daemon_id, context + " release daemon");
    sqlite_bind_text_or_throw(
        update_stmt.stmt, 5, capability.worker_id, context + " release worker");
    sqlite_bind_text_or_throw(
        update_stmt.stmt, 6, capability.owner_lock_id, context + " release id");
    sqlite_bind_u64_or_throw(
        update_stmt.stmt,
        7,
        capability.owner_lock_epoch,
        context + " release epoch");
    sqlite_step_done_or_throw(update_stmt.stmt, context + " release row");
    if (sqlite3_changes(db) != 1) {
        throw std::runtime_error(
            context + " release did not affect exactly one live generation");
    }

    const auto mode = load_stored_owner_mode_evidence_or_throw(
        db, session_id, context + " release owner mode");
    if (!mode.present) {
        throw std::runtime_error(
            context + " release lost sticky owner mode evidence");
    }
    SyncSqliteStmt mode_stmt = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_session_checkpoint_owner_modes "
        "SET mode_updated_at_epoch=? "
        "WHERE session_id=? AND ownership_mode='owner-required' "
        "AND latest_owner_lock_epoch=? AND mode_updated_at_epoch=? "
        "AND administrative_disable_evidence_id='';",
        context + " release owner mode prepare");
    sqlite_bind_u64_or_throw(
        mode_stmt.stmt, 1, released_at_epoch, context + " release mode update");
    sqlite_bind_text_or_throw(
        mode_stmt.stmt, 2, session_id, context + " release mode session");
    sqlite_bind_u64_or_throw(
        mode_stmt.stmt,
        3,
        capability.owner_lock_epoch,
        context + " release mode generation");
    sqlite_bind_u64_or_throw(
        mode_stmt.stmt,
        4,
        mode.mode_updated_at_epoch,
        context + " release mode prior update");
    sqlite_step_done_or_throw(
        mode_stmt.stmt, context + " release owner mode row");
    if (sqlite3_changes(db) != 1) {
        throw std::runtime_error(
            context + " release did not advance exact sticky owner mode row");
    }
}

void require_recipient_write_authority_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t observed_at_epoch,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    sync_checkpoint_owner_schema_internal::
        attest_checkpoint_owner_schema_or_throw(
            db, context + " checkpoint owner schema attestation");

    const auto stored = load_stored_owner_lock_evidence_or_throw(
        db, session_id, context);
    const auto mode = load_or_backfill_owner_mode_in_write_transaction_or_throw(
        db, session_id, stored, context);
    sync_checkpoint_owner_fence_policy::RecipientRequest request;
    request.session_id = session_id;
    request.observed_at_epoch = observed_at_epoch;
    request.capability = capability;
    const auto decision = sync_checkpoint_owner_fence_policy::authorize_recipient(
        mode, stored, request);
    if (!decision.allowed) {
        throw std::runtime_error(
            context + " recipient owner fence rejected: " + decision.reason);
    }
}

CheckpointRootResetPermit::CheckpointRootResetPermit(
    SyncSqliteTransactionAuthority transaction_authority,
    sqlite3* db,
    std::string session_id,
    bool owner_mode_present,
    std::string ownership_mode,
    std::uint64_t latest_owner_lock_epoch,
    std::uint64_t previous_mode_updated_at_epoch,
    std::string administrative_disable_evidence_id,
    std::uint64_t reset_at_epoch)
    : transaction_authority_(std::move(transaction_authority)),
      db_(db),
      session_id_(std::move(session_id)),
      owner_mode_present_(owner_mode_present),
      ownership_mode_(std::move(ownership_mode)),
      latest_owner_lock_epoch_(latest_owner_lock_epoch),
      previous_mode_updated_at_epoch_(previous_mode_updated_at_epoch),
      administrative_disable_evidence_id_(
          std::move(administrative_disable_evidence_id)),
      reset_at_epoch_(reset_at_epoch) {}

CheckpointRootResetPermit
authorize_checkpoint_root_reset_in_write_transaction_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionAuthority& transaction_authority,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t reset_at_epoch,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    if (!transaction_authority.authorizes_write(db)) {
        throw std::logic_error(
            context +
            " checkpoint root reset requires the exact live typed write transaction authority");
    }
    require_recipient_write_authority_or_throw(
        db, session_id, capability, reset_at_epoch, context);

    const auto mode = load_stored_owner_mode_evidence_or_throw(
        db, session_id, context + " reset mode snapshot");
    return CheckpointRootResetPermit(
        transaction_authority,
        db,
        session_id,
        mode.present,
        mode.ownership_mode,
        mode.latest_owner_lock_epoch,
        mode.mode_updated_at_epoch,
        mode.administrative_disable_evidence_id,
        reset_at_epoch);
}

void delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
    sqlite3* db,
    CheckpointRootResetPermit& permit,
    const std::string& context) {
    require_write_transaction_or_throw(db, context);
    if (permit.consumed_) {
        throw std::logic_error(
            context + " checkpoint root reset permit was already consumed");
    }
    if (permit.db_ == nullptr || permit.db_ != db ||
        !permit.transaction_authority_.authorizes_write(db)) {
        throw std::logic_error(
            context +
            " checkpoint root reset permit does not bind this live write transaction");
    }
    if (!portable_sync_id(permit.session_id_) || permit.reset_at_epoch_ == 0) {
        throw std::logic_error(
            context + " checkpoint root reset permit contains malformed evidence");
    }
    sync_checkpoint_owner_schema_internal::
        attest_checkpoint_owner_schema_or_throw(
            db, context + " checkpoint owner schema attestation");

    // The reset permit authorizes one compound state transition, not merely a
    // DELETE statement. Keep the cascade and the sticky-mode compare/reload in
    // an exact nested savepoint so a caller that catches an exception and then
    // commits the outer transaction cannot publish a partial reset.
    SyncSqliteSavepoint reset(
        db,
        permit.transaction_authority_,
        context + " atomic checkpoint root reset");

    SyncSqliteStmt delete_stmt = sqlite_prepare_or_throw(
        db,
        "DELETE FROM main.sync_session_checkpoints WHERE session_id=?;",
        context + " checkpoint root delete prepare");
    sqlite_bind_text_or_throw(
        delete_stmt.stmt,
        1,
        permit.session_id_,
        context + " checkpoint root delete session");
    sqlite_step_done_or_throw(
        delete_stmt.stmt, context + " checkpoint root delete row");

    if (permit.owner_mode_present_) {
        SyncSqliteStmt mode_stmt = sqlite_prepare_or_throw(
            db,
            "UPDATE main.sync_session_checkpoint_owner_modes "
            "SET mode_updated_at_epoch=? "
            "WHERE session_id=? AND ownership_mode=? "
            "AND latest_owner_lock_epoch=? AND mode_updated_at_epoch=? "
            "AND administrative_disable_evidence_id=?;",
            context + " checkpoint root reset sticky mode prepare");
        sqlite_bind_u64_or_throw(
            mode_stmt.stmt,
            1,
            permit.reset_at_epoch_,
            context + " checkpoint root reset mode update");
        sqlite_bind_text_or_throw(
            mode_stmt.stmt,
            2,
            permit.session_id_,
            context + " checkpoint root reset mode session");
        sqlite_bind_text_or_throw(
            mode_stmt.stmt,
            3,
            permit.ownership_mode_,
            context + " checkpoint root reset mode state");
        sqlite_bind_u64_or_throw(
            mode_stmt.stmt,
            4,
            permit.latest_owner_lock_epoch_,
            context + " checkpoint root reset mode generation");
        sqlite_bind_u64_or_throw(
            mode_stmt.stmt,
            5,
            permit.previous_mode_updated_at_epoch_,
            context + " checkpoint root reset prior mode update");
        sqlite_bind_text_or_throw(
            mode_stmt.stmt,
            6,
            permit.administrative_disable_evidence_id_,
            context + " checkpoint root reset disable evidence");
        sqlite_step_done_or_throw(
            mode_stmt.stmt, context + " checkpoint root reset sticky mode row");
        if (sqlite3_changes(db) != 1) {
            throw std::runtime_error(
                context +
                " checkpoint root reset did not preserve and advance exact sticky owner mode evidence");
        }

        const auto proof = load_stored_owner_mode_evidence_or_throw(
            db, permit.session_id_, context + " checkpoint root reset mode proof");
        if (!proof.present || proof.session_id != permit.session_id_ ||
            proof.ownership_mode != permit.ownership_mode_ ||
            proof.latest_owner_lock_epoch != permit.latest_owner_lock_epoch_ ||
            proof.mode_updated_at_epoch != permit.reset_at_epoch_ ||
            proof.administrative_disable_evidence_id !=
                permit.administrative_disable_evidence_id_) {
            throw std::runtime_error(
                context +
                " checkpoint root reset did not reload exact sticky owner mode evidence");
        }
    } else {
        const auto proof = load_stored_owner_mode_evidence_or_throw(
            db, permit.session_id_, context + " unowned reset mode proof");
        if (proof.present) {
            throw std::runtime_error(
                context + " unowned checkpoint root reset gained unexpected owner mode");
        }
    }

    reset.release();
    permit.consumed_ = true;
}

}  // namespace anonsync::sync_checkpoint_owner_fence_internal
