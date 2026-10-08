#include "sync_peer_ingress_schema.hpp"

#include "anonsync_core_internal.hpp"
#include "sync_peer_ingress_payload_store.hpp"
#include "sync_peer_ingress_schema_sql.hpp"
#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_schema_identity.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

struct ObservedSchemaObject final {
    std::string type;
    std::string name;
    std::string table_name;
    std::string normalized_sql;
};

std::string lower_ascii_copy(std::string_view value) {
    std::string out;
    out.reserve(value.size());
    for (const char c : value) {
        const unsigned char uc = static_cast<unsigned char>(c);
        if (uc >= 'A' && uc <= 'Z') {
            out.push_back(static_cast<char>(uc - 'A' + 'a'));
        } else {
            out.push_back(c);
        }
    }
    return out;
}

std::uint64_t scalar_nonnegative_i64_or_throw(sqlite3* db,
                                               const std::string& sql,
                                               const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " query");
    const std::uint64_t value = sqlite_column_u64_or_throw(
        stmt.stmt, 0, label + " exact scalar");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " returned more than one row");
    }
    return value;
}

std::vector<ObservedSchemaObject> expected_schema_objects() {
    std::vector<ObservedSchemaObject> out;
    out.reserve(kPeerTransportIngressSchemaSqlObjects.size());
    for (const PeerTransportIngressSchemaSqlObject& object :
         kPeerTransportIngressSchemaSqlObjects) {
        out.push_back({std::string(object.type),
                       std::string(object.name),
                       std::string(object.table_name),
                       canonicalize_sqlite_schema_sql_or_throw(object.ddl)});
    }
    std::sort(out.begin(), out.end(), [](const auto& left, const auto& right) {
        return std::tie(left.type, left.name, left.table_name) <
               std::tie(right.type, right.name, right.table_name);
    });
    return out;
}

std::vector<ObservedSchemaObject> load_reserved_schema_objects_or_throw(
    sqlite3* db,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT type, name, tbl_name, sql FROM main.sqlite_schema "
        "WHERE sql IS NOT NULL AND ("
        "name GLOB 'sync_peer_transport_*' OR "
        "name GLOB 'idx_sync_peer_transport_*' OR "
        "tbl_name GLOB 'sync_peer_transport_*') "
        "ORDER BY type, name, tbl_name;",
        label + " reserved schema manifest");
    std::vector<ObservedSchemaObject> out;
    for (;;) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, label + " reserved schema manifest query");
        }
        out.push_back({
            sqlite_column_text_or_throw(stmt.stmt, 0, label + " object type"),
            sqlite_column_text_or_throw(stmt.stmt, 1, label + " object name"),
            sqlite_column_text_or_throw(stmt.stmt, 2, label + " object table"),
            canonicalize_sqlite_schema_sql_or_throw(
                sqlite_column_text_or_throw(stmt.stmt, 3, label + " object SQL"))});
    }
    return out;
}

bool is_peer_transport_schema_name(std::string_view raw_name) {
    const std::string name = lower_ascii_copy(raw_name);
    return name.rfind("sync_peer_transport_", 0) == 0 ||
           name.rfind("idx_sync_peer_transport_", 0) == 0;
}

bool is_reviewed_sync_session_checkpoint_host_or_throw(
    sqlite3* db,
    const std::string& label);

void verify_no_virtual_or_cross_domain_dependencies_or_throw(
    sqlite3* db,
    const std::string& label) {
    SyncSqliteStmt tables = sqlite_prepare_or_throw(
        db, "PRAGMA main.table_list;", label + " table-list inspection");
    std::vector<std::string> foreign_tables;
    for (;;) {
        const int rc = sqlite3_step(tables.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, label + " table-list query");
        }
        const std::string schema =
            sqlite_column_text_or_throw(tables.stmt, 0, label + " table schema");
        const std::string name =
            sqlite_column_text_or_throw(tables.stmt, 1, label + " table name");
        const std::string type =
            sqlite_column_text_or_throw(tables.stmt, 2, label + " table type");
        if (schema != "main") continue;
        if (type == "virtual" || type == "shadow") {
            throw std::runtime_error(
                label + " found unsupported virtual/shadow table " + name);
        }
        if (type != "table" || name.rfind("sqlite_", 0) == 0 ||
            is_peer_transport_schema_name(name)) {
            continue;
        }
        foreign_tables.push_back(name);
    }

    for (const std::string& child_table : foreign_tables) {
        SyncSqliteStmt foreign_keys = sqlite_prepare_or_throw(
            db,
            "SELECT \"table\" FROM pragma_foreign_key_list(?, 'main') "
            "ORDER BY id, seq;",
            label + " foreign-key inspection");
        sqlite_bind_text_or_throw(foreign_keys.stmt,
                                  1,
                                  child_table,
                                  label + " foreign-key child table");
        for (;;) {
            const int rc = sqlite3_step(foreign_keys.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) {
                throw_sqlite_exception(db, rc, label + " foreign-key query");
            }
            const std::string parent_table = sqlite_column_text_or_throw(
                foreign_keys.stmt, 0, label + " foreign-key parent table");
            if (is_peer_transport_schema_name(parent_table)) {
                throw std::runtime_error(
                    label + " foreign table " + child_table +
                    " has a cross-domain foreign key into peer-ingress table " +
                    parent_table);
            }
        }
    }
}

void verify_reviewed_cohost_boundary_or_throw(sqlite3* db,
                                               const std::string& label) {
    const std::uint64_t cohost_objects = scalar_nonnegative_i64_or_throw(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE sql IS NOT NULL "
        "AND name NOT GLOB 'sqlite_*' "
        "AND name NOT GLOB 'sync_peer_transport_*' "
        "AND name NOT GLOB 'idx_sync_peer_transport_*' "
        "AND tbl_name NOT GLOB 'sync_peer_transport_*';",
        label + " cohost schema object count");
    if (cohost_objects != 0 &&
        !is_reviewed_sync_session_checkpoint_host_or_throw(
            db, label + " checkpoint cohost inspection")) {
        throw std::runtime_error(
            label + " peer-ingress schema is cohosted with an unreviewed schema");
    }
    verify_no_virtual_or_cross_domain_dependencies_or_throw(db, label);
}

std::string schema_manifest_material(
    const std::vector<ObservedSchemaObject>& objects) {
    std::string material = "anonsync-peer-transport-ingress-schema-manifest-v1\n";
    for (const ObservedSchemaObject& object : objects) {
        material.append(std::to_string(object.type.size()));
        material.push_back(':');
        material.append(object.type);
        material.push_back('\n');
        material.append(std::to_string(object.name.size()));
        material.push_back(':');
        material.append(object.name);
        material.push_back('\n');
        material.append(std::to_string(object.table_name.size()));
        material.push_back(':');
        material.append(object.table_name);
        material.push_back('\n');
        material.append(std::to_string(object.normalized_sql.size()));
        material.push_back(':');
        material.append(object.normalized_sql);
        material.push_back('\n');
    }
    return material;
}

void verify_no_attached_or_temp_schema_or_throw(sqlite3* db,
                                                 const std::string& label) {
    {
        SyncSqliteStmt stmt = sqlite_prepare_or_throw(
            db, "PRAGMA database_list;", label + " database list");
        for (;;) {
            const int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) {
                throw_sqlite_exception(db, rc, label + " database list query");
            }
            const std::string name =
                sqlite_column_text_or_throw(stmt.stmt, 1, label + " database name");
            if (name != "main" && name != "temp") {
                throw std::runtime_error(label +
                                         " found an attached database outside main/temp");
            }
        }
    }
    const std::uint64_t temp_objects = scalar_nonnegative_i64_or_throw(
        db,
        "SELECT COUNT(*) FROM sqlite_temp_schema WHERE sql IS NOT NULL;",
        label + " temporary schema object count");
    if (temp_objects != 0) {
        throw std::runtime_error(label +
                                 " found temporary schema objects that could shadow main");
    }
}

void verify_no_schema_programs_or_throw(sqlite3* db,
                                         const std::string& label) {
    const std::uint64_t programs = scalar_nonnegative_i64_or_throw(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema "
        "WHERE sql IS NOT NULL AND type IN ('trigger','view');",
        label + " trigger/view count");
    if (programs != 0) {
        throw std::runtime_error(label +
                                 " found trigger or view schema programs in the authority database");
    }
}

std::string verify_exact_reserved_schema_or_throw(sqlite3* db,
                                                   const std::string& label) {
    verify_no_attached_or_temp_schema_or_throw(db, label);
    verify_no_schema_programs_or_throw(db, label);
    verify_reviewed_cohost_boundary_or_throw(db, label);

    const std::vector<ObservedSchemaObject> expected = expected_schema_objects();
    const std::vector<ObservedSchemaObject> observed =
        load_reserved_schema_objects_or_throw(db, label);
    if (observed.size() != expected.size()) {
        throw std::runtime_error(
            label + " reserved schema object count mismatch (expected " +
            std::to_string(expected.size()) + ", observed " +
            std::to_string(observed.size()) + ")");
    }
    for (std::size_t i = 0; i < expected.size(); ++i) {
        const ObservedSchemaObject& wanted = expected[i];
        const ObservedSchemaObject& found = observed[i];
        if (wanted.type != found.type || wanted.name != found.name ||
            wanted.table_name != found.table_name) {
            throw std::runtime_error(
                label + " required schema object " + wanted.name +
                " is missing, reordered, or shadowed");
        }
        if (wanted.normalized_sql != found.normalized_sql) {
            throw std::runtime_error(
                label + " schema definition mismatch for reviewed object " +
                wanted.name);
        }
    }

    // Retain the specialized payload verifier as an independent structural
    // check.  The manifest catches any SQL drift; table_xinfo/FK checks catch
    // parser or normalization surprises without trusting the same mechanism.
    verify_peer_transport_ingress_payload_store_schema_or_throw(
        db, label + " payload-store structural verification");

    return sha256_hex(schema_manifest_material(observed));
}

std::uint64_t reserved_schema_object_count_or_throw(sqlite3* db,
                                                     const std::string& label) {
    return static_cast<std::uint64_t>(
        load_reserved_schema_objects_or_throw(db, label).size());
}

bool is_reviewed_sync_session_checkpoint_host_or_throw(
    sqlite3* db,
    const std::string& label) {
    const std::uint64_t meta_tables = scalar_nonnegative_i64_or_throw(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
        "AND name='sync_session_schema_meta';",
        label + " checkpoint meta table count");
    if (meta_tables == 0) return false;
    if (meta_tables != 1) {
        throw std::runtime_error(label + " checkpoint meta table identity is ambiguous");
    }

    SyncSqliteStmt definition = sqlite_prepare_or_throw(
        db,
        "SELECT sql FROM main.sqlite_schema WHERE type='table' "
        "AND name='sync_session_schema_meta';",
        label + " checkpoint meta definition");
    int rc = sqlite3_step(definition.stmt);
    if (rc != SQLITE_ROW) {
        throw_sqlite_exception(db, rc, label + " checkpoint meta definition query");
    }
    const std::string observed_definition =
        canonicalize_sqlite_schema_sql_or_throw(sqlite_column_text_or_throw(
            definition.stmt, 0, label + " checkpoint meta SQL"));
    if (sqlite3_step(definition.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " checkpoint meta definition is ambiguous");
    }
    static constexpr std::string_view kExpectedCheckpointMetaSql =
        "CREATE TABLE sync_session_schema_meta("
        "key TEXT PRIMARY KEY NOT NULL,value TEXT NOT NULL)";
    if (observed_definition !=
        canonicalize_sqlite_schema_sql_or_throw(kExpectedCheckpointMetaSql)) {
        throw std::runtime_error(
            label + " checkpoint meta table differs from the reviewed host anchor");
    }

    SyncSqliteStmt version = sqlite_prepare_or_throw(
        db,
        "SELECT value FROM sync_session_schema_meta WHERE key='schema_version';",
        label + " checkpoint schema version");
    rc = sqlite3_step(version.stmt);
    if (rc != SQLITE_ROW) {
        if (rc == SQLITE_DONE) {
            throw std::runtime_error(
                label + " checkpoint host anchor has no schema_version value");
        }
        throw_sqlite_exception(db, rc, label + " checkpoint schema version query");
    }
    const std::string schema_version = sqlite_column_text_or_throw(
        version.stmt, 0, label + " checkpoint schema version value");
    if (sqlite3_step(version.stmt) != SQLITE_DONE) {
        throw std::runtime_error(
            label + " checkpoint host anchor has ambiguous schema_version values");
    }
    if (schema_version != "rev0688-sync-session-checkpoint-v3" &&
        schema_version != "rev0720-sync-session-checkpoint-v4") {
        throw std::runtime_error(
            label + " checkpoint host schema_version is not recognized");
    }

    const std::uint64_t foreign_namespace_objects = scalar_nonnegative_i64_or_throw(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE sql IS NOT NULL "
        "AND name NOT GLOB 'sqlite_*' "
        "AND name NOT GLOB 'sync_session_*' "
        "AND name NOT GLOB 'idx_sync_session_*' "
        "AND name NOT GLOB 'sync_peer_transport_*' "
        "AND name NOT GLOB 'idx_sync_peer_transport_*' "
        "AND tbl_name NOT GLOB 'sync_peer_transport_*';",
        label + " checkpoint host namespace count");
    if (foreign_namespace_objects != 0) {
        throw std::runtime_error(
            label + " checkpoint host contains objects outside the reviewed sync_session namespace");
    }
    return true;
}

void require_marker_pair_or_throw(std::uint64_t application_id,
                                  std::uint64_t user_version,
                                  bool allow_legacy,
                                  bool& legacy_unmarked,
                                  const std::string& label) {
    legacy_unmarked = false;
    if (application_id == kPeerTransportIngressSqliteApplicationId &&
        user_version == kPeerTransportIngressSqliteUserVersion) {
        return;
    }
    if (allow_legacy && application_id == 0 && user_version == 0) {
        legacy_unmarked = true;
        return;
    }
    throw std::runtime_error(
        label + " application_id/user_version pair does not identify the reviewed schema");
}

void set_and_verify_markers_or_throw(sqlite3* db,
                                     const std::string& label) {
    sqlite_exec_or_throw(
        db,
        "PRAGMA application_id=" +
            std::to_string(kPeerTransportIngressSqliteApplicationId) + ";",
        label + " set application_id");
    sqlite_exec_or_throw(
        db,
        "PRAGMA user_version=" +
            std::to_string(kPeerTransportIngressSqliteUserVersion) + ";",
        label + " set user_version");
    const std::uint64_t application_id = scalar_nonnegative_i64_or_throw(
        db, "PRAGMA application_id;", label + " verify application_id");
    const std::uint64_t user_version = scalar_nonnegative_i64_or_throw(
        db, "PRAGMA user_version;", label + " verify user_version");
    bool legacy_unmarked = false;
    require_marker_pair_or_throw(application_id,
                                 user_version,
                                 false,
                                 legacy_unmarked,
                                 label + " marker verification");
}

bool protected_pragma_write(std::string_view raw_name,
                            const char* raw_argument) {
    if (raw_argument == nullptr) return false;
    const std::string name = lower_ascii_copy(raw_name);
    static constexpr std::array<std::string_view, 13> protected_names{{
        "application_id",
        "user_version",
        "schema_version",
        "writable_schema",
        "foreign_keys",
        "defer_foreign_keys",
        "ignore_check_constraints",
        "trusted_schema",
        "recursive_triggers",
        "query_only",
        "journal_mode",
        "synchronous",
        "secure_delete"
    }};
    return std::find(protected_names.begin(), protected_names.end(), name) !=
           protected_names.end();
}

bool schema_table_name(const char* raw_name) {
    if (raw_name == nullptr) return false;
    const std::string name = lower_ascii_copy(raw_name);
    return name == "sqlite_master" || name == "sqlite_schema" ||
           name == "sqlite_temp_master" || name == "sqlite_temp_schema";
}

int peer_transport_ingress_schema_authorizer(void*,
                                              int action,
                                              const char* argument1,
                                              const char* argument2,
                                              const char*,
                                              const char*) noexcept {
    switch (action) {
        case SQLITE_CREATE_INDEX:
        case SQLITE_CREATE_TABLE:
        case SQLITE_CREATE_TEMP_INDEX:
        case SQLITE_CREATE_TEMP_TABLE:
        case SQLITE_CREATE_TEMP_TRIGGER:
        case SQLITE_CREATE_TEMP_VIEW:
        case SQLITE_CREATE_TRIGGER:
        case SQLITE_CREATE_VIEW:
        case SQLITE_DROP_INDEX:
        case SQLITE_DROP_TABLE:
        case SQLITE_DROP_TEMP_INDEX:
        case SQLITE_DROP_TEMP_TABLE:
        case SQLITE_DROP_TEMP_TRIGGER:
        case SQLITE_DROP_TEMP_VIEW:
        case SQLITE_DROP_TRIGGER:
        case SQLITE_DROP_VIEW:
        case SQLITE_ALTER_TABLE:
        case SQLITE_REINDEX:
        case SQLITE_ANALYZE:
        case SQLITE_CREATE_VTABLE:
        case SQLITE_DROP_VTABLE:
        case SQLITE_ATTACH:
        case SQLITE_DETACH:
            return SQLITE_DENY;
        case SQLITE_PRAGMA:
            return protected_pragma_write(argument1 != nullptr ? argument1 : "",
                                          argument2)
                ? SQLITE_DENY
                : SQLITE_OK;
        case SQLITE_INSERT:
        case SQLITE_UPDATE:
        case SQLITE_DELETE:
            return schema_table_name(argument1) ? SQLITE_DENY : SQLITE_OK;
        default:
            return SQLITE_OK;
    }
}

SyncSqliteConnectionAuthorityProof install_schema_authorizer_or_throw(
    sqlite3* db,
    const std::string& label) {
    return install_sync_sqlite_connection_authority_or_throw(
        db,
        peer_transport_ingress_schema_authorizer,
        nullptr,
        label + " install schema mutation fence");
}

std::uint64_t current_schema_version_or_throw(sqlite3* db,
                                               const std::string& label) {
    return scalar_nonnegative_i64_or_throw(
        db, "PRAGMA schema_version;", label + " schema_version");
}

}  // namespace

PeerTransportIngressSchemaAttestation::PeerTransportIngressSchemaAttestation(
    sqlite3* db,
    std::uint64_t schema_version,
    std::string manifest_sha256,
    SyncSqliteConnectionAuthorityProof connection_authority,
    bool schema_present,
    bool legacy_unmarked)
    : db_(db),
      schema_version_(schema_version),
      manifest_sha256_(std::move(manifest_sha256)),
      connection_authority_(std::move(connection_authority)),
      schema_present_(schema_present),
      legacy_unmarked_(legacy_unmarked) {}

bool PeerTransportIngressSchemaAttestation::authorizes(sqlite3* db) const noexcept {
    if (db_ == nullptr || db_ != db || !connection_authority_.valid()) return false;
    try {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db, connection_authority_, "peer-ingress attestation authority probe");
        return lease.active();
    } catch (...) {
        return false;
    }
}

bool PeerTransportIngressSchemaAttestation::schema_present() const noexcept {
    return schema_present_;
}

bool PeerTransportIngressSchemaAttestation::legacy_unmarked() const noexcept {
    return legacy_unmarked_;
}

std::uint64_t PeerTransportIngressSchemaAttestation::schema_version() const noexcept {
    return schema_version_;
}

std::uint64_t
PeerTransportIngressSchemaAttestation::authorizer_generation() const noexcept {
    return connection_authority_.authorizer_generation();
}

const std::string&
PeerTransportIngressSchemaAttestation::manifest_sha256() const noexcept {
    return manifest_sha256_;
}

PeerTransportIngressSchemaAttestation
initialize_or_inspect_peer_transport_ingress_schema_or_throw(
    sqlite3* db,
    bool writable,
    bool allow_absent,
    const std::string& label) {
    if (db == nullptr) throw std::invalid_argument(label + " database handle is null");
    if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(label +
                               " schema attestation must begin outside a transaction");
    }

    struct InspectionResult final {
        bool needs_write_snapshot = false;
        bool schema_present = false;
        bool legacy_unmarked = false;
        std::string manifest_sha256;
    };

    const auto inspect_snapshot = [&](bool may_mutate) -> InspectionResult {
        InspectionResult result;
        verify_no_attached_or_temp_schema_or_throw(db, label);
        const std::uint64_t application_id = scalar_nonnegative_i64_or_throw(
            db, "PRAGMA application_id;", label + " application_id");
        const std::uint64_t user_version = scalar_nonnegative_i64_or_throw(
            db, "PRAGMA user_version;", label + " user_version");
        const std::uint64_t reserved_count =
            reserved_schema_object_count_or_throw(db, label);

        result.schema_present = reserved_count != 0;
        if (!result.schema_present) {
            if (!writable) {
                if (!allow_absent) {
                    throw std::runtime_error(label +
                                             " peer-ingress schema is absent");
                }
                if (application_id != 0 || user_version != 0) {
                    throw std::runtime_error(
                        label + " absent peer-ingress schema carries nonzero database markers");
                }
                verify_no_schema_programs_or_throw(db, label);
                return result;
            }

            if (application_id != 0 || user_version != 0) {
                throw std::runtime_error(
                    label + " refused to bootstrap over nonzero database markers");
            }
            const std::uint64_t foreign_objects = scalar_nonnegative_i64_or_throw(
                db,
                "SELECT COUNT(*) FROM main.sqlite_schema "
                "WHERE sql IS NOT NULL AND name NOT GLOB 'sqlite_*';",
                label + " foreign schema object count");
            if (foreign_objects != 0 &&
                !is_reviewed_sync_session_checkpoint_host_or_throw(
                    db, label + " cohost inspection")) {
                throw std::runtime_error(
                    label + " refused to claim a nonempty foreign SQLite database");
            }
            if (!may_mutate) {
                result.needs_write_snapshot = true;
                return result;
            }

            for (const PeerTransportIngressSchemaSqlObject& object :
                 kPeerTransportIngressSchemaSqlObjects) {
                sqlite_exec_or_throw(db,
                                     std::string(object.ddl) + ";",
                                     label + " create reviewed schema object " +
                                         std::string(object.name));
            }
            result.schema_present = true;
            result.manifest_sha256 = verify_exact_reserved_schema_or_throw(
                db, label + " post-bootstrap");
            set_and_verify_markers_or_throw(db, label);
            return result;
        }

        result.manifest_sha256 = verify_exact_reserved_schema_or_throw(db, label);
        require_marker_pair_or_throw(application_id,
                                     user_version,
                                     true,
                                     result.legacy_unmarked,
                                     label);
        if (result.legacy_unmarked && writable) {
            if (!may_mutate) {
                result.needs_write_snapshot = true;
                return result;
            }
            set_and_verify_markers_or_throw(db, label + " legacy marker migration");
            result.legacy_unmarked = false;
        }
        return result;
    };

    // A prior attestation leaves process-local client data on this handle even
    // if an alien caller replaces SQLite's callback. Typed BEGIN must not run
    // through that alien callback. Reinstall the restrictive schema policy
    // before opening the inspection snapshot; a handle with prior authority is
    // never a legitimate first-bootstrap or legacy-migration target. Failed
    // re-inspection therefore leaves the connection more restrictive, not less.
    SyncSqliteConnectionAuthorityProof connection_authority;
    const bool authority_state_present =
        sync_sqlite_connection_authority_state_present_or_throw(
            db, label + " prior authority inspection");
    if (authority_state_present) {
        connection_authority = install_schema_authorizer_or_throw(
            db, label + " recover prior connection authority");
    }

    // Existing marked databases are inspected under a read snapshot. This is
    // deliberate: taking BEGIN IMMEDIATE merely to inspect would move lock
    // contention out of the operation that owns and reports it. Only first
    // bootstrap and exact legacy-marker migration escalate to a write snapshot,
    // and both re-inspect after escalation so the mutation decision cannot race.
    auto transaction = std::make_unique<SyncSqliteTransaction>(
        db,
        label + " schema attestation read snapshot",
        SyncSqliteTransactionMode::Deferred);
    InspectionResult inspection = inspect_snapshot(false);
    if (inspection.needs_write_snapshot) {
        transaction->rollback();
        transaction = std::make_unique<SyncSqliteTransaction>(
            db, label + " atomic schema mutation");
        inspection = inspect_snapshot(true);
        if (inspection.needs_write_snapshot) {
            throw std::logic_error(label +
                                   " schema mutation snapshot did not resolve escalation");
        }
    }

    transaction->commit();
    const std::uint64_t schema_version =
        current_schema_version_or_throw(db, label + " committed attestation");
    if (!authority_state_present) {
        connection_authority = install_schema_authorizer_or_throw(db, label);
    }
    return PeerTransportIngressSchemaAttestation(
        db,
        schema_version,
        std::move(inspection.manifest_sha256),
        std::move(connection_authority),
        inspection.schema_present,
        inspection.legacy_unmarked);
}

SyncSqliteConnectionAuthorityLease
verify_peer_transport_ingress_schema_attestation_current_or_throw(
    sqlite3* db,
    const PeerTransportIngressSchemaAttestation& attestation,
    const std::string& label) {
    if (attestation.db_ == nullptr || attestation.db_ != db) {
        throw std::invalid_argument(
            label + " schema attestation does not authorize this SQLite handle");
    }
    SyncSqliteConnectionAuthorityLease authority_lease =
        acquire_sync_sqlite_connection_authority_or_throw(
            db, attestation.connection_authority_, label + " connection authority");
    const std::uint64_t schema_version =
        current_schema_version_or_throw(db, label);
    if (schema_version != attestation.schema_version()) {
        throw std::runtime_error(
            label + " SQLite schema generation changed after attestation");
    }

    verify_no_attached_or_temp_schema_or_throw(db, label);
    const std::uint64_t application_id = scalar_nonnegative_i64_or_throw(
        db, "PRAGMA application_id;", label + " application_id");
    const std::uint64_t user_version = scalar_nonnegative_i64_or_throw(
        db, "PRAGMA user_version;", label + " user_version");

    if (!attestation.schema_present()) {
        if (reserved_schema_object_count_or_throw(db, label) != 0 ||
            application_id != 0 || user_version != 0) {
            throw std::runtime_error(
                label + " absent schema attestation no longer matches the snapshot");
        }
        verify_no_schema_programs_or_throw(db, label);
        return authority_lease;
    }

    bool legacy_unmarked = false;
    require_marker_pair_or_throw(application_id,
                                 user_version,
                                 attestation.legacy_unmarked(),
                                 legacy_unmarked,
                                 label);
    if (legacy_unmarked != attestation.legacy_unmarked()) {
        throw std::runtime_error(
            label + " database marker state changed after attestation");
    }
    const std::string manifest_sha256 =
        verify_exact_reserved_schema_or_throw(db, label);
    if (manifest_sha256 != attestation.manifest_sha256()) {
        throw std::runtime_error(
            label + " schema manifest commitment changed after attestation");
    }
    return authority_lease;
}

std::string expected_peer_transport_ingress_schema_manifest_sha256() {
    return sha256_hex(schema_manifest_material(expected_schema_objects()));
}

}  // namespace anonsync
