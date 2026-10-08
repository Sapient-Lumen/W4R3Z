#include "sync_checkpoint_owner_schema.hpp"

#include "persistence/sqlite_exact_value.hpp"
#include "sync_sqlite_schema_identity.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <array>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync::sync_checkpoint_owner_schema_internal {
namespace {

constexpr std::string_view kCheckpointRootTable = "sync_session_checkpoints";
constexpr std::string_view kOwnerLockTable =
    "sync_session_resume_transfer_daemon_owner_locks";
constexpr std::string_view kOwnerModeTable =
    "sync_session_checkpoint_owner_modes";

constexpr std::string_view kOwnerModeStoredDdl =
    "CREATE TABLE sync_session_checkpoint_owner_modes("
    "session_id TEXT NOT NULL PRIMARY KEY,"
    "ownership_mode TEXT NOT NULL CHECK(ownership_mode IN "
    "('owner-required','administratively-disabled')),"
    "latest_owner_lock_epoch INTEGER NOT NULL "
    "CHECK(latest_owner_lock_epoch > 0),"
    "mode_updated_at_epoch INTEGER NOT NULL "
    "CHECK(mode_updated_at_epoch > 0),"
    "administrative_disable_evidence_id TEXT NOT NULL,"
    "CHECK((ownership_mode='owner-required' AND "
    "administrative_disable_evidence_id='') OR "
    "(ownership_mode='administratively-disabled' AND "
    "administrative_disable_evidence_id LIKE "
    "'sync-checkpoint-owner-admin-disable:v1:%')))";

constexpr std::string_view kOwnerModeCreateDdl =
    "CREATE TABLE main.sync_session_checkpoint_owner_modes("
    "session_id TEXT NOT NULL PRIMARY KEY,"
    "ownership_mode TEXT NOT NULL CHECK(ownership_mode IN "
    "('owner-required','administratively-disabled')),"
    "latest_owner_lock_epoch INTEGER NOT NULL "
    "CHECK(latest_owner_lock_epoch > 0),"
    "mode_updated_at_epoch INTEGER NOT NULL "
    "CHECK(mode_updated_at_epoch > 0),"
    "administrative_disable_evidence_id TEXT NOT NULL,"
    "CHECK((ownership_mode='owner-required' AND "
    "administrative_disable_evidence_id='') OR "
    "(ownership_mode='administratively-disabled' AND "
    "administrative_disable_evidence_id LIKE "
    "'sync-checkpoint-owner-admin-disable:v1:%')))";

constexpr std::string_view kOwnerLockStoredDdl =
    "CREATE TABLE sync_session_resume_transfer_daemon_owner_locks("
    "session_id TEXT NOT NULL PRIMARY KEY REFERENCES "
    "sync_session_checkpoints(session_id) ON DELETE CASCADE,"
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
    "CHECK(updated_at_epoch >= acquired_at_epoch))";

struct ExpectedColumn final {
    std::string_view name;
    std::string_view declared_type;
    int not_null = 0;
    int primary_key_rank = 0;
};

constexpr std::array<ExpectedColumn, 5> kOwnerModeColumns{{
    {"session_id", "text", 1, 1},
    {"ownership_mode", "text", 1, 0},
    {"latest_owner_lock_epoch", "integer", 1, 0},
    {"mode_updated_at_epoch", "integer", 1, 0},
    {"administrative_disable_evidence_id", "text", 1, 0},
}};

constexpr std::array<ExpectedColumn, 10> kOwnerLockColumns{{
    {"session_id", "text", 1, 1},
    {"daemon_id", "text", 1, 0},
    {"worker_id", "text", 1, 0},
    {"owner_lock_id", "text", 1, 0},
    {"owner_lock_epoch", "integer", 1, 0},
    {"acquired_at_epoch", "integer", 1, 0},
    {"expires_at_epoch", "integer", 1, 0},
    {"released_at_epoch", "integer", 1, 0},
    {"lock_state", "text", 1, 0},
    {"updated_at_epoch", "integer", 1, 0},
}};

std::string lower_ascii_copy(std::string_view value) {
    std::string out;
    out.reserve(value.size());
    for (const char raw : value) {
        const unsigned char c = static_cast<unsigned char>(raw);
        if (c >= 'A' && c <= 'Z') {
            out.push_back(static_cast<char>(c - 'A' + 'a'));
        } else {
            out.push_back(raw);
        }
    }
    return out;
}

bool ascii_case_equal(std::string_view left, std::string_view right) noexcept {
    if (left.size() != right.size()) return false;
    for (std::size_t i = 0; i < left.size(); ++i) {
        const auto fold = [](char raw) noexcept {
            const unsigned char c = static_cast<unsigned char>(raw);
            return c >= 'A' && c <= 'Z'
                ? static_cast<char>(c - 'A' + 'a')
                : raw;
        };
        if (fold(left[i]) != fold(right[i])) return false;
    }
    return true;
}

bool is_checkpoint_owner_authority_name(std::string_view name) noexcept {
    return ascii_case_equal(name, kCheckpointRootTable) ||
           ascii_case_equal(name, kOwnerLockTable) ||
           ascii_case_equal(name, kOwnerModeTable);
}

std::int64_t exact_i64_or_throw(sqlite3_stmt* stmt,
                                int column,
                                const std::string& context) {
    return sqlite_column_i64_or_throw(stmt, column, context);
}

std::int64_t scalar_pragma_i64_or_throw(sqlite3* db,
                                       std::string_view sql,
                                       const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db, std::string(sql), context + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        throw_sqlite_exception(db, rc, context + " query");
    }
    const std::int64_t value =
        exact_i64_or_throw(stmt.stmt, 0, context + " value");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(context + " returned more than one row");
    }
    return value;
}

void verify_constraint_enforcement_profile_or_throw(
    sqlite3* db,
    const std::string& context) {
    if (scalar_pragma_i64_or_throw(
            db,
            "PRAGMA foreign_keys;",
            context + " foreign-key enforcement") != 1) {
        throw std::runtime_error(
            context + " checkpoint owner authority requires foreign-key enforcement");
    }
    if (scalar_pragma_i64_or_throw(
            db,
            "PRAGMA ignore_check_constraints;",
            context + " CHECK-constraint enforcement") != 0) {
        throw std::runtime_error(
            context + " checkpoint owner authority requires CHECK-constraint enforcement");
    }
}

struct SchemaObject final {
    std::string type;
    std::string name;
    std::string table_name;
    std::string sql;
};

std::vector<SchemaObject> load_sql_bearing_objects_or_throw(
    sqlite3* db,
    std::string_view reserved_name,
    const std::string& context) {
    // SQLite resolves unquoted object names case-insensitively, while equality
    // in sqlite_schema queries is normally BINARY.  Scan and fold in C++ so a
    // hostile mixed-case alias cannot be misclassified as an absent object.
    // Avoid SQL lower()/collations: both are connection-programmable surfaces.
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT type,name,tbl_name,sql FROM main.sqlite_schema "
        "WHERE sql IS NOT NULL ORDER BY type,name,tbl_name;",
        context + " main schema objects prepare");

    std::vector<SchemaObject> objects;
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, context + " main schema objects query");
        }
        SchemaObject object{
            sqlite_column_text_or_throw(
                stmt.stmt, 0, context + " schema object type"),
            sqlite_column_text_or_throw(
                stmt.stmt, 1, context + " schema object name"),
            sqlite_column_text_or_throw(
                stmt.stmt, 2, context + " schema object table"),
            sqlite_column_text_or_throw(
                stmt.stmt, 3, context + " schema object SQL"),
        };
        if (ascii_case_equal(object.name, reserved_name) ||
            ascii_case_equal(object.table_name, reserved_name)) {
            objects.push_back(std::move(object));
        }
    }
    return objects;
}

bool exact_table_object_present_or_throw(sqlite3* db,
                                         std::string_view table_name,
                                         std::string_view expected_stored_ddl,
                                         bool allow_absent,
                                         const std::string& context) {
    const std::vector<SchemaObject> objects = load_sql_bearing_objects_or_throw(
        db, table_name, context);
    if (objects.empty()) {
        if (allow_absent) return false;
        throw std::runtime_error(
            context + " reviewed main-schema table object is absent");
    }
    if (objects.size() != 1) {
        throw std::runtime_error(
            context + " has unexpected SQL-bearing index, trigger, or alias objects");
    }

    const SchemaObject& object = objects.front();
    if (object.type != "table" || object.name != table_name ||
        object.table_name != table_name) {
        throw std::runtime_error(
            context + " reserved authority name is not the exact main table object");
    }

    const std::string expected_identity =
        canonicalize_sqlite_schema_sql_or_throw(expected_stored_ddl);
    const std::string observed_identity =
        canonicalize_sqlite_schema_sql_or_throw(object.sql);
    if (observed_identity != expected_identity) {
        throw std::runtime_error(
            context + " exact reviewed schema SQL does not match");
    }
    return true;
}

void verify_no_relevant_temp_objects_or_throw(sqlite3* db,
                                               const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT name,tbl_name FROM sqlite_temp_schema "
        "WHERE sql IS NOT NULL ORDER BY type,name,tbl_name;",
        context + " temporary authority objects prepare");
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) return;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, context + " temporary authority objects query");
        }
        const std::string name = sqlite_column_text_or_throw(
            stmt.stmt, 0, context + " temporary object name");
        const std::string table = sqlite_column_text_or_throw(
            stmt.stmt, 1, context + " temporary object table");
        if (is_checkpoint_owner_authority_name(name) ||
            is_checkpoint_owner_authority_name(table)) {
            // Hostile schema bytes are deliberately omitted from diagnostics.
            throw std::runtime_error(
                context + " found a temporary schema object that can shadow or "
                "program checkpoint owner authority");
        }
    }
}

void verify_no_checkpoint_root_triggers_or_throw(sqlite3* db,
                                                 const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT tbl_name FROM main.sqlite_schema "
        "WHERE type='trigger' AND sql IS NOT NULL ORDER BY name;",
        context + " checkpoint root trigger prepare");
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) return;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, context + " checkpoint root trigger query");
        }
        if (ascii_case_equal(
                sqlite_column_text_or_throw(
                    stmt.stmt, 0, context + " checkpoint root trigger table"),
                kCheckpointRootTable)) {
            throw std::runtime_error(
                context + " checkpoint root has an unreviewed trigger");
        }
    }
}

struct TableListRow final {
    std::string schema;
    std::string name;
    std::string type;
    std::int64_t columns = -1;
    std::int64_t without_rowid = -1;
    std::int64_t strict = -1;
};

TableListRow exact_table_list_row_or_throw(sqlite3* db,
                                           std::string_view table_name,
                                           std::size_t expected_columns,
                                           const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db, "PRAGMA main.table_list;", context + " table_list prepare");
    std::optional<TableListRow> observed;
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, context + " table_list query");
        }
        const std::string name = sqlite_column_text_or_throw(
            stmt.stmt, 1, context + " table_list name");
        if (!ascii_case_equal(name, table_name)) continue;
        if (observed.has_value()) {
            throw std::runtime_error(
                context + " table_list returned an ambiguous authority table");
        }
        observed = TableListRow{
            sqlite_column_text_or_throw(
                stmt.stmt, 0, context + " table_list schema"),
            name,
            sqlite_column_text_or_throw(
                stmt.stmt, 2, context + " table_list type"),
            exact_i64_or_throw(stmt.stmt, 3, context + " table_list columns"),
            exact_i64_or_throw(
                stmt.stmt, 4, context + " table_list without-rowid"),
            exact_i64_or_throw(stmt.stmt, 5, context + " table_list strict"),
        };
    }
    if (!observed.has_value()) {
        throw std::runtime_error(
            context + " table_list did not expose the reviewed authority table");
    }
    if (observed->schema != "main" || observed->type != "table" ||
        observed->columns != static_cast<std::int64_t>(expected_columns) ||
        observed->without_rowid != 0 || observed->strict != 0) {
        throw std::runtime_error(
            context + " table_list geometry does not match the reviewed table");
    }
    return *observed;
}

template <std::size_t N>
void verify_exact_columns_or_throw(
    sqlite3* db,
    std::string_view table_name,
    const std::array<ExpectedColumn, N>& expected,
    const std::string& context) {
    const std::string sql =
        "SELECT cid,name,type,\"notnull\",dflt_value,pk,hidden "
        "FROM pragma_table_xinfo(?, 'main') ORDER BY cid;";
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db, sql, context + " table_xinfo prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        1,
        std::string(table_name),
        context + " table_xinfo table");

    std::size_t index = 0;
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, context + " table_xinfo query");
        }
        if (index >= expected.size()) {
            throw std::runtime_error(
                context + " table_xinfo exposed an unexpected extra column");
        }
        const ExpectedColumn& wanted = expected[index];
        const std::int64_t cid = exact_i64_or_throw(
            stmt.stmt, 0, context + " table_xinfo cid");
        const std::string name = lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 1, context + " table_xinfo name"));
        const std::string type = lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 2, context + " table_xinfo type"));
        const std::int64_t not_null = exact_i64_or_throw(
            stmt.stmt, 3, context + " table_xinfo notnull");
        const bool default_is_null =
            !persistence::sqlite_exact_optional_text_or_throw(
                 stmt.stmt,
                 4,
                 context + " table_xinfo default value")
                 .has_value();
        const std::int64_t primary_key_rank = exact_i64_or_throw(
            stmt.stmt, 5, context + " table_xinfo primary-key rank");
        const std::int64_t hidden = exact_i64_or_throw(
            stmt.stmt, 6, context + " table_xinfo hidden");
        if (cid != static_cast<std::int64_t>(index) || name != wanted.name ||
            type != wanted.declared_type || not_null != wanted.not_null ||
            !default_is_null ||
            primary_key_rank != wanted.primary_key_rank || hidden != 0) {
            throw std::runtime_error(
                context + " table_xinfo column geometry does not match at " +
                std::string(wanted.name));
        }
        ++index;
    }
    if (index != expected.size()) {
        throw std::runtime_error(
            context + " table_xinfo omitted reviewed authority columns");
    }
}

void verify_no_foreign_keys_or_throw(sqlite3* db,
                                     std::string_view table_name,
                                     const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT id,seq,\"table\",\"from\",\"to\",on_update,on_delete,match "
        "FROM pragma_foreign_key_list(?, 'main') ORDER BY id,seq;",
        context + " foreign_key_list prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        1,
        std::string(table_name),
        context + " foreign_key_list table");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return;
    if (rc != SQLITE_ROW) {
        throw_sqlite_exception(db, rc, context + " foreign_key_list query");
    }
    throw std::runtime_error(
        context + " sticky owner mode unexpectedly has a foreign key");
}

void verify_exact_owner_lock_foreign_key_or_throw(
    sqlite3* db,
    const std::string& context) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT id,seq,\"table\",\"from\",\"to\",on_update,on_delete,match "
        "FROM pragma_foreign_key_list(?, 'main') ORDER BY id,seq;",
        context + " owner foreign_key_list prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        1,
        std::string(kOwnerLockTable),
        context + " owner foreign_key_list table");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        if (rc == SQLITE_DONE) {
            throw std::runtime_error(
                context + " owner lock table has no checkpoint-root foreign key");
        }
        throw_sqlite_exception(
            db, rc, context + " owner foreign_key_list query");
    }
    const bool exact =
        exact_i64_or_throw(stmt.stmt, 0, context + " foreign key id") == 0 &&
        exact_i64_or_throw(stmt.stmt, 1, context + " foreign key seq") == 0 &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 2, context + " foreign key parent")) ==
            kCheckpointRootTable &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 3, context + " foreign key child column")) ==
            "session_id" &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 4, context + " foreign key parent column")) ==
            "session_id" &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 5, context + " foreign key update action")) ==
            "no action" &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 6, context + " foreign key delete action")) ==
            "cascade" &&
        lower_ascii_copy(sqlite_column_text_or_throw(
            stmt.stmt, 7, context + " foreign key match")) == "none";
    if (!exact) {
        throw std::runtime_error(
            context + " owner lock foreign-key geometry does not match");
    }
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(
            context + " owner lock table has unexpected extra foreign keys");
    }
}

void verify_checkpoint_root_anchor_or_throw(sqlite3* db,
                                            const std::string& context) {
    SyncSqliteStmt schema_stmt = sqlite_prepare_or_throw(
        db,
        "SELECT type,name,tbl_name FROM main.sqlite_schema "
        "WHERE sql IS NOT NULL ORDER BY type,name,tbl_name;",
        context + " checkpoint root object prepare");
    bool found = false;
    for (;;) {
        const int rc = sqlite3_step(schema_stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, context + " checkpoint root object query");
        }
        const std::string type = sqlite_column_text_or_throw(
            schema_stmt.stmt, 0, context + " checkpoint root object type");
        const std::string name = sqlite_column_text_or_throw(
            schema_stmt.stmt, 1, context + " checkpoint root object name");
        const std::string table = sqlite_column_text_or_throw(
            schema_stmt.stmt, 2, context + " checkpoint root object table");
        if (!ascii_case_equal(name, kCheckpointRootTable)) continue;
        if (found || type != "table" || name != kCheckpointRootTable ||
            table != kCheckpointRootTable) {
            throw std::runtime_error(
                context +
                " checkpoint root reserved name is not one exact main table");
        }
        found = true;
    }
    if (!found) {
        throw std::runtime_error(context + " checkpoint root table is absent");
    }

    SyncSqliteStmt columns = sqlite_prepare_or_throw(
        db,
        "SELECT name,type,\"notnull\",pk,hidden "
        "FROM pragma_table_xinfo(?, 'main') ORDER BY cid;",
        context + " checkpoint root anchor prepare");
    sqlite_bind_text_or_throw(
        columns.stmt,
        1,
        std::string(kCheckpointRootTable),
        context + " checkpoint root anchor table");
    bool anchor_found = false;
    for (;;) {
        const int rc = sqlite3_step(columns.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, context + " checkpoint root anchor query");
        }
        const std::string name = sqlite_column_text_or_throw(
            columns.stmt, 0, context + " checkpoint root anchor name");
        if (!ascii_case_equal(name, "session_id")) continue;
        if (anchor_found) {
            throw std::runtime_error(
                context + " checkpoint root has ambiguous session_id anchors");
        }
        anchor_found = true;
        const bool exact_anchor =
            lower_ascii_copy(sqlite_column_text_or_throw(
                columns.stmt, 1, context + " checkpoint root anchor type")) ==
                "text" &&
            exact_i64_or_throw(
                columns.stmt, 2, context + " checkpoint root anchor notnull") == 1 &&
            exact_i64_or_throw(
                columns.stmt, 3, context + " checkpoint root anchor pk") == 1 &&
            exact_i64_or_throw(
                columns.stmt, 4, context + " checkpoint root anchor hidden") == 0;
        if (!exact_anchor) {
            throw std::runtime_error(
                context +
                " checkpoint root session_id anchor geometry does not match");
        }
    }
    if (!anchor_found) {
        throw std::runtime_error(
            context + " checkpoint root has no session_id anchor");
    }
}

void attest_mode_table_or_throw(sqlite3* db,
                                const std::string& context) {
    (void)exact_table_object_present_or_throw(
        db,
        kOwnerModeTable,
        kOwnerModeStoredDdl,
        false,
        context + " sticky owner mode object");
    (void)exact_table_list_row_or_throw(
        db,
        kOwnerModeTable,
        kOwnerModeColumns.size(),
        context + " sticky owner mode");
    verify_exact_columns_or_throw(
        db,
        kOwnerModeTable,
        kOwnerModeColumns,
        context + " sticky owner mode");
    verify_no_foreign_keys_or_throw(
        db,
        kOwnerModeTable,
        context + " sticky owner mode");
}

bool attest_optional_owner_lock_table_or_throw(sqlite3* db,
                                                const std::string& context) {
    if (!exact_table_object_present_or_throw(
            db,
            kOwnerLockTable,
            kOwnerLockStoredDdl,
            true,
            context + " owner lock object")) {
        return false;
    }
    verify_checkpoint_root_anchor_or_throw(
        db, context + " owner lock parent");
    (void)exact_table_list_row_or_throw(
        db,
        kOwnerLockTable,
        kOwnerLockColumns.size(),
        context + " owner lock");
    verify_exact_columns_or_throw(
        db,
        kOwnerLockTable,
        kOwnerLockColumns,
        context + " owner lock");
    verify_exact_owner_lock_foreign_key_or_throw(
        db, context + " owner lock");
    return true;
}

}  // namespace

void attest_checkpoint_owner_schema_or_throw(
    sqlite3* db,
    const std::string& context) {
    if (db == nullptr) {
        throw std::invalid_argument(context + " database handle is null");
    }
    verify_constraint_enforcement_profile_or_throw(db, context);
    verify_no_relevant_temp_objects_or_throw(db, context);
    verify_no_checkpoint_root_triggers_or_throw(db, context);
    attest_mode_table_or_throw(db, context);
    (void)attest_optional_owner_lock_table_or_throw(db, context);
}

void ensure_checkpoint_owner_schema_or_throw(
    sqlite3* db,
    const std::string& context) {
    if (db == nullptr) {
        throw std::invalid_argument(context + " database handle is null");
    }

    SyncSqliteSavepoint migration(
        db, context + " atomic checkpoint owner-schema migration");
    verify_constraint_enforcement_profile_or_throw(db, context);
    verify_no_relevant_temp_objects_or_throw(db, context);
    verify_no_checkpoint_root_triggers_or_throw(db, context);

    // Validate any legacy owner evidence before creating the new sticky-mode
    // object. A hostile preexisting lock table must not cause even a partial
    // migration side effect.
    const bool owner_lock_present =
        attest_optional_owner_lock_table_or_throw(db, context);

    const bool mode_present = exact_table_object_present_or_throw(
        db,
        kOwnerModeTable,
        kOwnerModeStoredDdl,
        true,
        context + " sticky owner mode bootstrap object");
    if (!mode_present) {
        sqlite_exec_or_throw(
            db,
            std::string(kOwnerModeCreateDdl) + ";",
            context + " create exact sticky owner mode table");
    }

    attest_mode_table_or_throw(db, context);
    if (owner_lock_present) {
        sqlite_exec_or_throw(
            db,
            "INSERT INTO main.sync_session_checkpoint_owner_modes"
            "(session_id, ownership_mode, latest_owner_lock_epoch, "
            "mode_updated_at_epoch, administrative_disable_evidence_id) "
            "SELECT owner.session_id, 'owner-required', "
            "owner.owner_lock_epoch, owner.updated_at_epoch, '' "
            "FROM main.sync_session_resume_transfer_daemon_owner_locks AS owner "
            "WHERE NOT EXISTS(SELECT 1 FROM "
            "main.sync_session_checkpoint_owner_modes AS mode "
            "WHERE mode.session_id=owner.session_id);",
            context + " atomically backfill legacy sticky owner modes");
    }

    // Re-attest before publication so creation, migration, and the exact
    // schema proof are one typed SQLite savepoint unit.
    attest_checkpoint_owner_schema_or_throw(
        db, context + " post-migration attestation");
    migration.release();
}

}  // namespace anonsync::sync_checkpoint_owner_schema_internal
