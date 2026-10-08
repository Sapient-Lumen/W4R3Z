#include "sync_checkpoint_owner_fence.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <filesystem>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using anonsync::SyncSessionCheckpointDaemonOwnerCapability;
using anonsync::SyncSqliteDb;
using anonsync::SyncSqliteStmt;
using anonsync::SyncSqliteTransaction;
using anonsync::SyncSqliteTransactionAuthority;
using anonsync::SyncSqliteTransactionMode;
using anonsync::sync_checkpoint_owner_fence_internal::MintedDaemonOwnerLockRecord;

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void check(bool condition, std::string_view label) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << label << '\n';
    }
};

class TemporaryPath final {
public:
    TemporaryPath() {
        const auto base = std::filesystem::temp_directory_path();
        for (std::uint64_t i = 1; i < 10000; ++i) {
            const auto candidate = base /
                ("anonsync-owner-fence-sqlite-" + std::to_string(i) + ".db");
            std::error_code ec;
            if (!std::filesystem::exists(candidate, ec)) {
                path_ = candidate;
                return;
            }
        }
        throw std::runtime_error("could not allocate temporary SQLite path");
    }

    ~TemporaryPath() {
        std::error_code ec;
        std::filesystem::remove(path_, ec);
        std::filesystem::remove(path_.string() + "-wal", ec);
        std::filesystem::remove(path_.string() + "-shm", ec);
        std::filesystem::remove(path_.string() + "-journal", ec);
    }

    [[nodiscard]] const std::filesystem::path& get() const noexcept {
        return path_;
    }

private:
    std::filesystem::path path_;
};

struct ModeSnapshot final {
    bool present = false;
    std::string ownership_mode;
    std::uint64_t latest_owner_lock_epoch = 0;
    std::uint64_t mode_updated_at_epoch = 0;
    std::string administrative_disable_evidence_id;
};

SyncSessionCheckpointDaemonOwnerCapability capability(
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t generation) {
    SyncSessionCheckpointDaemonOwnerCapability out;
    out.session_id = session_id;
    out.daemon_id = daemon_id;
    out.worker_id = worker_id;
    out.owner_lock_epoch = generation;
    out.owner_lock_id =
        anonsync::sync_checkpoint_owner_fence_internal::owner_lock_id_or_throw(
            session_id, daemon_id, worker_id, generation);
    return out;
}

SyncSessionCheckpointDaemonOwnerCapability capability_from_minted(
    const std::string& session_id,
    const MintedDaemonOwnerLockRecord& minted) {
    SyncSessionCheckpointDaemonOwnerCapability out;
    out.session_id = session_id;
    out.daemon_id = minted.daemon_id;
    out.worker_id = minted.worker_id;
    out.owner_lock_id = minted.owner_lock_id;
    out.owner_lock_epoch = minted.owner_lock_epoch;
    return out;
}

void insert_root(SyncSqliteDb& db, const std::string& session_id) {
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO sync_session_checkpoints(session_id) VALUES(?) "
        "ON CONFLICT(session_id) DO NOTHING;",
        "owner fence SQLite test insert checkpoint root");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, "insert checkpoint root session");
    anonsync::sqlite_step_done_or_throw(
        stmt.stmt, "insert checkpoint root row");
}

void create_schema(SyncSqliteDb& db) {
    anonsync::sqlite_exec_or_throw(
        db.db,
        "PRAGMA foreign_keys=ON;"
        "CREATE TABLE sync_session_checkpoints("
        "session_id TEXT PRIMARY KEY NOT NULL);"
        "CREATE TABLE sync_session_resume_transfer_daemon_owner_locks("
        "session_id TEXT NOT NULL PRIMARY KEY "
        "REFERENCES sync_session_checkpoints(session_id) ON DELETE CASCADE,"
        "daemon_id TEXT NOT NULL,"
        "worker_id TEXT NOT NULL,"
        "owner_lock_id TEXT NOT NULL,"
        "owner_lock_epoch INTEGER NOT NULL CHECK(owner_lock_epoch > 0),"
        "acquired_at_epoch INTEGER NOT NULL CHECK(acquired_at_epoch > 0),"
        "expires_at_epoch INTEGER NOT NULL "
        "CHECK(expires_at_epoch > acquired_at_epoch),"
        "released_at_epoch INTEGER NOT NULL "
        "CHECK(released_at_epoch = 0 OR released_at_epoch >= acquired_at_epoch),"
        "lock_state TEXT NOT NULL CHECK(lock_state IN ('held','released')),"
        "updated_at_epoch INTEGER NOT NULL "
        "CHECK(updated_at_epoch >= acquired_at_epoch));"
        "CREATE TABLE recipient_effects("
        "session_id TEXT PRIMARY KEY NOT NULL, effects INTEGER NOT NULL);"
        "INSERT INTO recipient_effects(session_id,effects) "
        "VALUES('session-a',0);",
        "owner fence SQLite test schema");

    for (const std::string session_id : {
             "session-a",
             "session-mint",
             "session-reset",
             "session-catch-commit",
             "session-legacy",
             "session-permit",
             "session-disabled"}) {
        insert_root(db, session_id);
    }
    anonsync::sync_checkpoint_owner_fence_internal::
        ensure_checkpoint_owner_mode_schema_or_throw(
            db.db, "owner fence SQLite test sticky schema");
}

void store_owner(SyncSqliteDb& db,
                 const SyncSessionCheckpointDaemonOwnerCapability& owner,
                 std::uint64_t acquired_at,
                 std::uint64_t expires_at,
                 std::uint64_t released_at,
                 std::uint64_t updated_at,
                 const std::string& state,
                 const std::string& override_lock_id = {}) {
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT OR REPLACE INTO sync_session_resume_transfer_daemon_owner_locks("
        "session_id,daemon_id,worker_id,owner_lock_id,owner_lock_epoch,"
        "acquired_at_epoch,expires_at_epoch,released_at_epoch,updated_at_epoch,"
        "lock_state) VALUES(?,?,?,?,?,?,?,?,?,?);",
        "owner fence SQLite test store owner");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 1, owner.session_id, "store session");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 2, owner.daemon_id, "store daemon");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 3, owner.worker_id, "store worker");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt,
        4,
        override_lock_id.empty() ? owner.owner_lock_id : override_lock_id,
        "store lock id");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 5, owner.owner_lock_epoch, "store generation");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 6, acquired_at, "store acquired");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 7, expires_at, "store expires");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 8, released_at, "store released");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 9, updated_at, "store updated");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 10, state, "store state");
    anonsync::sqlite_step_done_or_throw(stmt.stmt, "store owner row");
}

void store_disabled_mode(SyncSqliteDb& db,
                         const std::string& session_id,
                         std::uint64_t generation,
                         std::uint64_t updated_at_epoch) {
    const std::string evidence =
        "sync-checkpoint-owner-admin-disable:v1:" + std::string(64, 'a');
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO sync_session_checkpoint_owner_modes("
        "session_id,ownership_mode,latest_owner_lock_epoch,"
        "mode_updated_at_epoch,administrative_disable_evidence_id) "
        "VALUES(?,'administratively-disabled',?,?,?);",
        "owner fence SQLite test disabled mode prepare");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, "disabled mode session");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 2, generation, "disabled mode generation");
    anonsync::sqlite_bind_u64_or_throw(
        stmt.stmt, 3, updated_at_epoch, "disabled mode update");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 4, evidence, "disabled mode evidence");
    anonsync::sqlite_step_done_or_throw(
        stmt.stmt, "disabled mode row");
}

[[nodiscard]] bool throws_with(const std::function<void()>& operation,
                               std::string_view expected_text) {
    try {
        operation();
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(expected_text) !=
               std::string_view::npos;
    }
    return false;
}

[[nodiscard]] std::uint64_t session_count(SyncSqliteDb& db,
                                          const std::string& sql,
                                          const std::string& session_id,
                                          const std::string& label) {
    return anonsync::sqlite_count_for_session_or_throw(
        db.db, sql, session_id, label);
}

[[nodiscard]] std::uint64_t root_count(SyncSqliteDb& db,
                                       const std::string& session_id) {
    return session_count(
        db,
        "SELECT COUNT(*) FROM sync_session_checkpoints WHERE session_id=?;",
        session_id,
        "owner fence SQLite test checkpoint root count");
}

[[nodiscard]] std::uint64_t owner_count(SyncSqliteDb& db,
                                        const std::string& session_id) {
    return session_count(
        db,
        "SELECT COUNT(*) FROM "
        "sync_session_resume_transfer_daemon_owner_locks WHERE session_id=?;",
        session_id,
        "owner fence SQLite test owner count");
}

[[nodiscard]] ModeSnapshot mode_snapshot(SyncSqliteDb& db,
                                         const std::string& session_id) {
    ModeSnapshot out;
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "SELECT ownership_mode,latest_owner_lock_epoch,mode_updated_at_epoch,"
        "administrative_disable_evidence_id "
        "FROM sync_session_checkpoint_owner_modes WHERE session_id=?;",
        "owner fence SQLite test mode snapshot prepare");
    anonsync::sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, "mode snapshot session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return out;
    if (rc != SQLITE_ROW) {
        throw std::runtime_error("mode snapshot query failed");
    }
    out.present = true;
    out.ownership_mode = anonsync::sqlite_column_text_or_throw(
        stmt.stmt, 0, "mode snapshot state");
    out.latest_owner_lock_epoch = anonsync::sqlite_column_u64_or_throw(
        stmt.stmt, 1, "mode snapshot generation");
    out.mode_updated_at_epoch = anonsync::sqlite_column_u64_or_throw(
        stmt.stmt, 2, "mode snapshot update");
    out.administrative_disable_evidence_id =
        anonsync::sqlite_column_text_or_throw(
            stmt.stmt, 3, "mode snapshot disable evidence");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error("mode snapshot row is not unique");
    }
    return out;
}

[[nodiscard]] std::uint64_t effect_count(SyncSqliteDb& db) {
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "SELECT effects FROM recipient_effects WHERE session_id='session-a';",
        "owner fence SQLite test effect count");
    if (sqlite3_step(stmt.stmt) != SQLITE_ROW) {
        throw std::runtime_error("effect row missing");
    }
    const auto value = anonsync::sqlite_column_u64_or_throw(
        stmt.stmt, 0, "effect count");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error("effect row is not unique");
    }
    return value;
}

void apply_effect(SyncSqliteDb& db) {
    anonsync::sqlite_exec_or_throw(
        db.db,
        "UPDATE recipient_effects SET effects=effects+1 "
        "WHERE session_id='session-a';",
        "owner fence SQLite test apply effect");
}

[[nodiscard]] bool foreign_keys_enabled(SyncSqliteDb& db) {
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db, "PRAGMA foreign_keys;", "owner fence foreign key pragma");
    if (sqlite3_step(stmt.stmt) != SQLITE_ROW) {
        throw std::runtime_error("foreign key pragma row missing");
    }
    const bool enabled = anonsync::sqlite_column_u64_or_throw(
                             stmt.stmt, 0, "foreign key pragma value") == 1;
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error("foreign key pragma returned extra rows");
    }
    return enabled;
}

[[nodiscard]] bool mode_table_has_no_foreign_keys(SyncSqliteDb& db) {
    SyncSqliteStmt stmt = anonsync::sqlite_prepare_or_throw(
        db.db,
        "PRAGMA main.foreign_key_list(sync_session_checkpoint_owner_modes);",
        "owner fence mode foreign key list");
    return sqlite3_step(stmt.stmt) == SQLITE_DONE;
}

void test_hostile_mode_blocks_legacy_backfill(TestState& test) {
    SyncSqliteDb db;
    const int open_rc = sqlite3_open_v2(
        ":memory:",
        db.db.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (open_rc != SQLITE_OK) {
        throw std::runtime_error(
            "hostile owner schema fixture could not open SQLite database");
    }
    anonsync::sqlite_exec_or_throw(
        db.db,
        "PRAGMA foreign_keys=ON;"
        "CREATE TABLE main.sync_session_checkpoints("
        "session_id TEXT PRIMARY KEY NOT NULL);"
        "CREATE TABLE main.sync_session_resume_transfer_daemon_owner_locks("
        "session_id TEXT NOT NULL PRIMARY KEY REFERENCES "
        "sync_session_checkpoints(session_id) ON DELETE CASCADE,"
        "daemon_id TEXT NOT NULL,worker_id TEXT NOT NULL,"
        "owner_lock_id TEXT NOT NULL,"
        "owner_lock_epoch INTEGER NOT NULL CHECK(owner_lock_epoch > 0),"
        "acquired_at_epoch INTEGER NOT NULL CHECK(acquired_at_epoch > 0),"
        "expires_at_epoch INTEGER NOT NULL "
        "CHECK(expires_at_epoch > acquired_at_epoch),"
        "released_at_epoch INTEGER NOT NULL "
        "CHECK(released_at_epoch = 0 OR released_at_epoch >= acquired_at_epoch),"
        "lock_state TEXT NOT NULL CHECK(lock_state IN ('held','released')),"
        "updated_at_epoch INTEGER NOT NULL "
        "CHECK(updated_at_epoch >= acquired_at_epoch));"
        "CREATE TABLE main.sync_session_checkpoint_owner_modes("
        "session_id TEXT PRIMARY KEY NOT NULL,"
        "ownership_mode TEXT NOT NULL,"
        "latest_owner_lock_epoch INTEGER NOT NULL,"
        "mode_updated_at_epoch INTEGER NOT NULL,"
        "administrative_disable_evidence_id TEXT NOT NULL);",
        "hostile owner schema fixture");
    insert_root(db, "session-hostile-migration");
    const auto legacy = capability(
        "session-hostile-migration", "daemon-hostile", "worker-hostile", 1);
    store_owner(db, legacy, 10, 20, 20, 20, "released");

    test.check(
        throws_with(
            [&] {
                anonsync::sync_checkpoint_owner_fence_internal::
                    ensure_checkpoint_owner_mode_schema_or_throw(
                        db.db, "hostile legacy mode migration refusal");
            },
            "exact reviewed schema SQL does not match"),
        "hostile sticky-mode lookalike is rejected before legacy backfill");
    test.check(
        session_count(
            db,
            "SELECT COUNT(*) FROM main.sync_session_checkpoint_owner_modes "
            "WHERE session_id=?;",
            "session-hostile-migration",
            "hostile legacy mode migration row count") == 0,
        "hostile schema refusal produces no legacy owner-mode row");
}

}  // namespace

int main() {
    TestState test;
    try {
        test_hostile_mode_blocks_legacy_backfill(test);

        TemporaryPath temp;
        SyncSqliteDb db;
        const int open_rc = sqlite3_open_v2(
            temp.get().string().c_str(),
            db.db.out(),
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
            nullptr);
        if (open_rc != SQLITE_OK) {
            std::cerr << "could not open test database\n";
            return 2;
        }
        create_schema(db);

        const auto owner_a = capability(
            "session-a", "daemon-a", "worker-a", 1);
        SyncSessionCheckpointDaemonOwnerCapability empty;

        test.check(foreign_keys_enabled(db),
                   "foreign key cascades are active in the focused fixture");
        test.check(mode_table_has_no_foreign_keys(db),
                   "sticky owner mode is independent of checkpoint-root cascades");
        anonsync::sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TABLE sync_session_checkpoint_owner_modes("
            "session_id TEXT);",
            "owner fence TEMP shadow fixture");
        {
            SyncSqliteTransaction transaction(
                db.db,
                "owner fence TEMP shadow refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-permit",
                                empty,
                                1,
                                "owner fence TEMP shadow refusal");
                    },
                    "temporary schema object"),
                "recipient refuses TEMP schema shadow before interpreting owner evidence");
            transaction.rollback();
        }
        anonsync::sqlite_exec_or_throw(
            db.db,
            "DROP TABLE temp.sync_session_checkpoint_owner_modes;",
            "owner fence TEMP shadow cleanup");
        test.check(owner_a.owner_lock_id.starts_with(
                       "sync-resume-daemon-owner-lock:v1:"),
                   "canonical owner id namespace");
        test.check(owner_a.owner_lock_id.size() == 97,
                   "canonical owner id digest geometry");

        MintedDaemonOwnerLockRecord minted_one;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "database mint generation one",
                SyncSqliteTransactionMode::Immediate);
            minted_one = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-mint",
                    "daemon-mint-a",
                    "worker-mint-a",
                    100,
                    50,
                    "database mint generation one");
            transaction.commit();
        }
        const auto minted_one_capability =
            capability_from_minted("session-mint", minted_one);
        const auto mint_mode_one = mode_snapshot(db, "session-mint");
        test.check(minted_one.acquired && minted_one.owner_lock_epoch == 1 &&
                       minted_one.acquired_at_epoch == 100 &&
                       minted_one.expires_at_epoch == 150 &&
                       !minted_one.reclaimed_expired,
                   "database acquisition mints generation one from absent evidence");
        test.check(mint_mode_one.present &&
                       mint_mode_one.ownership_mode == "owner-required" &&
                       mint_mode_one.latest_owner_lock_epoch == 1 &&
                       mint_mode_one.mode_updated_at_epoch == 100 &&
                       mint_mode_one.administrative_disable_evidence_id.empty(),
                   "generation mint durably activates sticky owner-required mode");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "database live owner refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        (void)anonsync::sync_checkpoint_owner_fence_internal::
                            acquire_owner_generation_in_write_transaction_or_throw(
                                db.db,
                                "session-mint",
                                "daemon-mint-b",
                                "worker-mint-b",
                                149,
                                50,
                                "database live owner refusal");
                    },
                    "still live"),
                "database acquisition cannot overwrite a live generation");
            transaction.rollback();
        }

        {
            SyncSqliteTransaction transaction(
                db.db,
                "database exact release",
                SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                release_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-mint",
                    minted_one_capability,
                    120,
                    "database exact release");
            transaction.commit();
        }
        const auto released_mode = mode_snapshot(db, "session-mint");
        test.check(released_mode.present &&
                       released_mode.ownership_mode == "owner-required" &&
                       released_mode.latest_owner_lock_epoch == 1 &&
                       released_mode.mode_updated_at_epoch == 120,
                   "release preserves sticky owner-required mode and generation");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "database released empty refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-mint",
                                empty,
                                121,
                                "database released empty refusal");
                    },
                    "remains required after release"),
                "release cannot reopen capability-free mutation");
            transaction.rollback();
        }

        MintedDaemonOwnerLockRecord minted_two;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "database mint generation two",
                SyncSqliteTransactionMode::Immediate);
            minted_two = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-mint",
                    "daemon-mint-b",
                    "worker-mint-b",
                    121,
                    50,
                    "database mint generation two");
            transaction.commit();
        }
        const auto minted_two_capability =
            capability_from_minted("session-mint", minted_two);
        test.check(minted_two.acquired &&
                       minted_two.owner_lock_epoch == 2 &&
                       minted_two.owner_lock_id != minted_one.owner_lock_id &&
                       !minted_two.reclaimed_expired,
                   "release and reacquisition mint the next sticky generation");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "database stale release",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            release_owner_generation_in_write_transaction_or_throw(
                                db.db,
                                "session-mint",
                                minted_one_capability,
                                122,
                                "database stale release");
                    },
                    "does not match the live durable generation"),
                "stale generation cannot release its successor");
            transaction.rollback();
        }

        {
            SyncSqliteTransaction transaction(
                db.db,
                "database generation two recipient",
                SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db,
                    "session-mint",
                    minted_two_capability,
                    130,
                    "database generation two recipient");
            transaction.rollback();
        }
        test.check(true,
                   "newly minted durable generation authorizes its exact recipient");

        test.check(
            throws_with(
                [&] {
                    anonsync::sync_checkpoint_owner_fence_internal::
                        require_recipient_write_authority_or_throw(
                            db.db,
                            "session-a",
                            empty,
                            5,
                            "outside transaction");
                },
                "inside the recipient write transaction"),
            "recipient check refuses preflight-only observation");

        {
            SyncSqliteTransaction transaction(
                db.db, "absent owner", SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db, "session-a", empty, 5, "absent owner");
            apply_effect(db);
            transaction.commit();
        }
        test.check(effect_count(db) == 1,
                   "empty capability may mutate before ownership ever exists");

        {
            SyncSqliteTransaction transaction(
                db.db, "invented owner", SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-a",
                                owner_a,
                                5,
                                "invented owner");
                    },
                    "no durable owner row exists"),
                "capability cannot invent an absent durable owner");
            transaction.rollback();
        }

        store_owner(db, owner_a, 10, 30, 0, 10, "held");
        {
            SyncSqliteTransaction transaction(
                db.db, "legacy exact owner", SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db, "session-a", owner_a, 20, "legacy exact owner");
            apply_effect(db);
            transaction.commit();
        }
        const auto legacy_backfill = mode_snapshot(db, "session-a");
        test.check(effect_count(db) == 2,
                   "exact legacy generation authorizes recipient mutation");
        test.check(legacy_backfill.present &&
                       legacy_backfill.ownership_mode == "owner-required" &&
                       legacy_backfill.latest_owner_lock_epoch == 1 &&
                       legacy_backfill.mode_updated_at_epoch == 10,
                   "recipient boundary backfills legacy ownership as sticky");

        auto partial = owner_a;
        partial.owner_lock_id.clear();
        {
            SyncSqliteTransaction transaction(
                db.db, "partial capability", SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-a",
                                partial,
                                20,
                                "partial capability");
                    },
                    "partially populated"),
                "partial capability is rejected");
            transaction.rollback();
        }

        {
            SyncSqliteTransaction transaction(
                db.db, "session-a release", SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                release_owner_generation_in_write_transaction_or_throw(
                    db.db, "session-a", owner_a, 21, "session-a release");
            transaction.commit();
        }
        MintedDaemonOwnerLockRecord owner_b_minted;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "session-a successor",
                SyncSqliteTransactionMode::Immediate);
            owner_b_minted = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-a",
                    "daemon-b",
                    "worker-b",
                    22,
                    40,
                    "session-a successor");
            transaction.commit();
        }
        const auto owner_b = capability_from_minted(
            "session-a", owner_b_minted);
        {
            SyncSqliteTransaction transaction(
                db.db, "stale generation", SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-a",
                                owner_a,
                                23,
                                "stale generation");
                    },
                    "does not match the live durable generation"),
                "generation one is fenced after generation two takeover");
            transaction.rollback();
        }
        test.check(effect_count(db) == 2,
                   "stale generation produces no recipient effect");

        {
            SyncSqliteTransaction transaction(
                db.db, "exact owner b", SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db, "session-a", owner_b, 23, "exact owner b");
            apply_effect(db);
            transaction.commit();
        }
        test.check(effect_count(db) == 3,
                   "new durable generation can mutate after takeover");

        {
            SyncSqliteTransaction transaction(
                db.db, "expired owner b", SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-a",
                                owner_b,
                                62,
                                "expired owner b");
                    },
                    "expired"),
                "generation expires at its exclusive upper bound");
            transaction.rollback();
        }

        store_owner(
            db,
            owner_b,
            70,
            90,
            0,
            70,
            "held",
            "sync-resume-daemon-owner-lock:v1:" + std::string(64, '0'));
        {
            SyncSqliteTransaction transaction(
                db.db,
                "forged durable row",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-a",
                                owner_b,
                                80,
                                "forged durable row");
                    },
                    "does not bind"),
                "forged durable owner id fails canonical recomputation");
            transaction.rollback();
        }
        test.check(effect_count(db) == 3,
                   "malformed durable evidence produces no effect");

        const auto legacy_released = capability(
            "session-legacy", "daemon-legacy", "worker-legacy", 1);
        store_owner(db, legacy_released, 10, 30, 20, 20, "released");
        anonsync::sync_checkpoint_owner_fence_internal::
            ensure_checkpoint_owner_mode_schema_or_throw(
                db.db, "legacy released startup migration");
        {
            SyncSqliteTransaction transaction(
                db.db,
                "legacy released empty refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-legacy",
                                empty,
                                21,
                                "legacy released empty refusal");
                    },
                    "remains required after release"),
                "startup migration makes a legacy released owner sticky");
            transaction.rollback();
        }

        MintedDaemonOwnerLockRecord reset_owner;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "reset owner generation one",
                SyncSqliteTransactionMode::Immediate);
            reset_owner = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-reset",
                    "daemon-reset-a",
                    "worker-reset-a",
                    200,
                    100,
                    "reset owner generation one");
            transaction.commit();
        }
        const auto reset_capability =
            capability_from_minted("session-reset", reset_owner);
        {
            SyncSqliteTransaction transaction(
                db.db,
                "authorized checkpoint root reset",
                SyncSqliteTransactionMode::Immediate);
            auto permit = anonsync::sync_checkpoint_owner_fence_internal::
                authorize_checkpoint_root_reset_in_write_transaction_or_throw(
                    db.db,
                    transaction.authority(),
                    "session-reset",
                    reset_capability,
                    220,
                    "authorized checkpoint root reset");
            anonsync::sync_checkpoint_owner_fence_internal::
                delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
                    db.db, permit, "authorized checkpoint root reset");
            const auto reset_mode = mode_snapshot(db, "session-reset");
            test.check(root_count(db, "session-reset") == 0 &&
                           owner_count(db, "session-reset") == 0,
                       "root reset executes the real foreign-key owner cascade");
            test.check(reset_mode.present &&
                           reset_mode.ownership_mode == "owner-required" &&
                           reset_mode.latest_owner_lock_epoch == 1 &&
                           reset_mode.mode_updated_at_epoch == 220,
                       "sticky mode survives and advances across root cascade");
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
                                db.db,
                                permit,
                                "reused checkpoint root reset permit");
                    },
                    "already consumed"),
                "checkpoint root reset permit is single-use");
            insert_root(db, "session-reset");
            transaction.commit();
        }


        MintedDaemonOwnerLockRecord catch_commit_owner;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "caught reset failure owner generation",
                SyncSqliteTransactionMode::Immediate);
            catch_commit_owner = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-catch-commit",
                    "daemon-catch-commit",
                    "worker-catch-commit",
                    500,
                    100,
                    "caught reset failure owner generation");
            transaction.commit();
        }
        const auto catch_commit_capability = capability_from_minted(
            "session-catch-commit", catch_commit_owner);
        {
            SyncSqliteTransaction transaction(
                db.db,
                "caught reset failure outer transaction",
                SyncSqliteTransactionMode::Immediate);
            auto permit = anonsync::sync_checkpoint_owner_fence_internal::
                authorize_checkpoint_root_reset_in_write_transaction_or_throw(
                    db.db,
                    transaction.authority(),
                    "session-catch-commit",
                    catch_commit_capability,
                    520,
                    "caught reset failure permit");

            // Advance the sticky row after permit issuance. The reset DELETE
            // will cascade the owner row, then its stale compare-and-replace
            // must fail. A caller is allowed to catch that failure and commit
            // unrelated earlier work in this outer transaction.
            anonsync::sqlite_exec_or_throw(
                db.db,
                "UPDATE sync_session_checkpoint_owner_modes "
                "SET mode_updated_at_epoch=501 "
                "WHERE session_id='session-catch-commit';",
                "caught reset failure stale permit fixture");
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
                                db.db,
                                permit,
                                "caught reset failure compound transition");
                    },
                    "did not preserve and advance exact sticky owner mode evidence"),
                "late reset failure is surfaced to a caller that may catch it");
            transaction.commit();
        }
        const auto catch_commit_mode = mode_snapshot(
            db, "session-catch-commit");
        test.check(root_count(db, "session-catch-commit") == 1 &&
                       owner_count(db, "session-catch-commit") == 1,
                   "caught late reset failure cannot commit the destructive DELETE prefix");
        test.check(catch_commit_mode.present &&
                       catch_commit_mode.ownership_mode == "owner-required" &&
                       catch_commit_mode.latest_owner_lock_epoch == 1 &&
                       catch_commit_mode.mode_updated_at_epoch == 501,
                   "nested reset rollback preserves unrelated earlier outer-transaction work");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "post-reset empty refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-reset",
                                empty,
                                221,
                                "post-reset empty refusal");
                    },
                    "acquire a successor"),
                "checkpoint reset cannot launder ownership into unowned mode");
            transaction.rollback();
        }

        MintedDaemonOwnerLockRecord reset_successor;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "post-reset successor",
                SyncSqliteTransactionMode::Immediate);
            reset_successor = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-reset",
                    "daemon-reset-b",
                    "worker-reset-b",
                    221,
                    100,
                    "post-reset successor");
            transaction.commit();
        }
        const auto reset_successor_capability = capability_from_minted(
            "session-reset", reset_successor);
        test.check(reset_successor.acquired &&
                       reset_successor.owner_lock_epoch == 2,
                   "successor after root reset advances the surviving generation");
        {
            SyncSqliteTransaction transaction(
                db.db,
                "post-reset stale generation",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-reset",
                                reset_capability,
                                222,
                                "post-reset stale generation");
                    },
                    "does not match the live durable generation"),
                "pre-reset generation is fenced by the post-reset successor");
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db,
                    "session-reset",
                    reset_successor_capability,
                    222,
                    "post-reset exact successor");
            transaction.rollback();
        }
        test.check(true,
                   "post-reset successor authorizes its exact recipient");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "out-of-range unowned reset refusal",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        (void)anonsync::sync_checkpoint_owner_fence_internal::
                            authorize_checkpoint_root_reset_in_write_transaction_or_throw(
                                db.db,
                                transaction.authority(),
                                "session-permit",
                                empty,
                                static_cast<std::uint64_t>(
                                    std::numeric_limits<std::int64_t>::max()) + 1,
                                "out-of-range unowned reset refusal");
                    },
                    "SQLite signed integer range"),
                "unowned root reset rejects observation time outside durable integer range");
            transaction.rollback();
        }
        test.check(root_count(db, "session-permit") == 1,
                   "out-of-range reset leaves checkpoint root untouched");

        {
            SyncSqliteTransaction transaction(
                db.db,
                "default authority reset refusal",
                SyncSqliteTransactionMode::Immediate);
            const SyncSqliteTransactionAuthority no_authority;
            test.check(
                throws_with(
                    [&] {
                        (void)anonsync::sync_checkpoint_owner_fence_internal::
                            authorize_checkpoint_root_reset_in_write_transaction_or_throw(
                                db.db,
                                no_authority,
                                "session-permit",
                                empty,
                                300,
                                "default authority reset refusal");
                    },
                    "exact live typed write transaction authority"),
                "root reset refuses an observation-only transaction state");
            transaction.rollback();
        }

        {
            SyncSqliteTransaction first_transaction(
                db.db,
                "stale reset permit issue",
                SyncSqliteTransactionMode::Immediate);
            auto stale_permit = anonsync::sync_checkpoint_owner_fence_internal::
                authorize_checkpoint_root_reset_in_write_transaction_or_throw(
                    db.db,
                    first_transaction.authority(),
                    "session-permit",
                    empty,
                    301,
                    "stale reset permit issue");
            first_transaction.rollback();

            SyncSqliteTransaction second_transaction(
                db.db,
                "stale reset permit consume",
                SyncSqliteTransactionMode::Immediate);
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
                                db.db,
                                stale_permit,
                                "stale reset permit consume");
                    },
                    "does not bind this live write transaction"),
                "reset permit cannot cross typed transaction generations");
            second_transaction.rollback();
        }
        test.check(root_count(db, "session-permit") == 1,
                   "stale reset permit leaves checkpoint root untouched");

        store_disabled_mode(db, "session-disabled", 7, 400);
        {
            SyncSqliteTransaction transaction(
                db.db,
                "administratively disabled empty recipient",
                SyncSqliteTransactionMode::Immediate);
            anonsync::sync_checkpoint_owner_fence_internal::
                require_recipient_write_authority_or_throw(
                    db.db,
                    "session-disabled",
                    empty,
                    401,
                    "administratively disabled empty recipient");
            test.check(
                throws_with(
                    [&] {
                        anonsync::sync_checkpoint_owner_fence_internal::
                            require_recipient_write_authority_or_throw(
                                db.db,
                                "session-disabled",
                                owner_a,
                                401,
                                "administratively disabled owner recipient");
                    },
                    "after administrative disable"),
                "administrative disable rejects residual owner capabilities");
            transaction.rollback();
        }

        MintedDaemonOwnerLockRecord disabled_reactivated;
        {
            SyncSqliteTransaction transaction(
                db.db,
                "administratively disabled reactivation",
                SyncSqliteTransactionMode::Immediate);
            disabled_reactivated = anonsync::sync_checkpoint_owner_fence_internal::
                acquire_owner_generation_in_write_transaction_or_throw(
                    db.db,
                    "session-disabled",
                    "daemon-disabled-next",
                    "worker-disabled-next",
                    402,
                    50,
                    "administratively disabled reactivation");
            transaction.commit();
        }
        const auto reactivated_mode = mode_snapshot(db, "session-disabled");
        test.check(disabled_reactivated.owner_lock_epoch == 8 &&
                       reactivated_mode.present &&
                       reactivated_mode.ownership_mode == "owner-required" &&
                       reactivated_mode.latest_owner_lock_epoch == 8 &&
                       reactivated_mode.administrative_disable_evidence_id.empty(),
                   "new acquisition explicitly reactivates disabled mode at next generation");
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "UNCAUGHT: " << error.what() << '\n';
    }

    std::cout << "sync checkpoint owner fence SQLite checks: "
              << test.passed << '/' << (test.passed + test.failed)
              << " passed\n";
    return test.failed == 0 ? 0 : 1;
}
