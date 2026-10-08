#include "sync_replica_deployment_binding.hpp"

#include "sha256_digest.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <cstdint>
#include <filesystem>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::string_view kBindingFormat =
    "anonsync-sqlite-deployment-binding-v1";
constexpr std::string_view kBindingDigestDomain =
    "anonsync:sqlite-deployment-binding:v1";
constexpr std::string_view kBindingTable =
    "anonsync_store_set_binding";
constexpr std::uint64_t kMaximumPathBytes = 32768U;
constexpr std::uint64_t kMaximumFieldBytes = 32768U;

// ASCII family "ASR" plus a role byte. These values are an internal early role
// fence, not a globally registered SQLite file(1) claim. Full authority remains
// the exact table below.
constexpr std::uint32_t kReplicaApplicationId = 0x41535201U;
constexpr std::uint32_t kFileEffectApplicationId = 0x41535202U;
constexpr std::uint32_t kTlsMembershipApplicationId = 0x41535203U;
constexpr std::uint32_t kTlsMembershipAnchorApplicationId = 0x41535204U;
static_assert(kTlsMembershipAnchorApplicationId <=
              static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max()));

constexpr std::string_view kStoredSchemaSql =
    "CREATE TABLE anonsync_store_set_binding("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "format TEXT NOT NULL CHECK(format='anonsync-sqlite-deployment-binding-v1'),"
    "deployment_id TEXT NOT NULL CHECK(length(deployment_id)=64),"
    "manifest_digest TEXT NOT NULL CHECK(length(manifest_digest)=64),"
    "manifest_path TEXT NOT NULL CHECK(length(manifest_path) BETWEEN 1 AND 32768),"
    "store_role TEXT NOT NULL CHECK(length(store_role) BETWEEN 1 AND 64),"
    "database_path TEXT NOT NULL CHECK(length(database_path) BETWEEN 1 AND 32768),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),"
    "local_epoch INTEGER NOT NULL CHECK(local_epoch>0),"
    "sqlite_application_id INTEGER NOT NULL CHECK(sqlite_application_id>0),"
    "binding_digest TEXT NOT NULL CHECK(length(binding_digest)=64)) STRICT";

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
            "SQLite deployment-binding digest field exceeds uint64 range");
    }
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

[[nodiscard]] std::string binding_digest_or_throw(
    const SyncReplicaSqliteDeploymentBinding& binding) {
    Sha256DigestBuilder digest;
    append_string(digest, kBindingDigestDomain);
    append_string(digest, kBindingFormat);
    append_string(digest, binding.deployment.deployment_id);
    append_string(digest, binding.deployment.manifest_digest);
    append_string(
        digest, binding.deployment.manifest_path.generic_string());
    append_string(digest, sync_replica_sqlite_deployment_role_name(binding.role));
    append_string(digest, binding.database_path.generic_string());
    append_string(digest, binding.deployment.folder_id);
    append_string(digest, binding.deployment.local_actor.device_id);
    append_u64(digest, binding.deployment.local_actor.epoch);
    append_u64(digest, sync_replica_sqlite_application_id(binding.role));
    return digest.finish_hex();
}

void require_canonical_absolute_path(
    const fs::path& path,
    const std::string& label) {
    if (path.native().find(fs::path::value_type{}) !=
        fs::path::string_type::npos) {
        throw std::invalid_argument(label + " database_path contains NUL");
    }
    if (path.empty() || !path.is_absolute()) {
        throw std::invalid_argument(label + " database_path must be absolute");
    }
    if (path.lexically_normal() != path) {
        throw std::invalid_argument(
            label + " database_path must be lexically normalized");
    }
    if (path.generic_string().size() > kMaximumPathBytes) {
        throw std::invalid_argument(
            label + " database_path exceeds the durable binding ceiling");
    }
}

[[nodiscard]] std::uint64_t scalar_u64_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database, sql, label + " prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        if (first == SQLITE_DONE) {
            throw std::runtime_error(label + " returned no row");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first, label + " step");
    }
    const std::uint64_t value = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(label + " returned excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " trailing step");
    }
    return value;
}

[[nodiscard]] std::string scalar_text_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database, sql, label + " prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        if (first == SQLITE_DONE) {
            throw std::runtime_error(label + " returned no row");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first, label + " step");
    }
    const std::string value = sqlite_column_text_or_throw(
        statement.stmt, 0, 128U, label + " value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(label + " returned excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " trailing step");
    }
    return value;
}

struct SchemaObject final {
    std::string type;
    std::string name;
    std::string table_name;
    std::string sql;
};

[[nodiscard]] std::vector<SchemaObject> read_binding_schema_or_throw(
    SyncSqliteDbHandleSlot& database,
    std::string_view schema,
    const std::string& label) {
    if (schema != "main" && schema != "temp") {
        throw std::logic_error(label + " received an invalid schema name");
    }
    const std::string sql =
        "SELECT type,name,tbl_name,coalesce(sql,'') FROM " +
        std::string(schema) +
        ".sqlite_schema WHERE name='anonsync_store_set_binding' OR "
        "tbl_name='anonsync_store_set_binding' ORDER BY name,type;";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database, sql, label + " schema query prepare");
    std::vector<SchemaObject> objects;
    for (;;) {
        const int result = sqlite3_step(statement.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), result,
                label + " schema query");
        }
        if (objects.size() >= 2U) {
            throw std::runtime_error(
                label + " binding schema has excess objects");
        }
        objects.push_back({
            sqlite_column_text_or_throw(
                statement.stmt, 0, 32U, label + " schema type"),
            sqlite_column_text_or_throw(
                statement.stmt, 1, 128U, label + " schema name"),
            sqlite_column_text_or_throw(
                statement.stmt, 2, 128U, label + " schema table name"),
            sqlite_column_text_or_throw(
                statement.stmt, 3, 64U * 1024U, label + " schema SQL"),
        });
    }
    return objects;
}

void require_exact_binding_schema_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    const std::vector<SchemaObject> main =
        read_binding_schema_or_throw(database, "main", label + " main");
    if (main.size() != 1U || main.front().type != "table" ||
        main.front().name != kBindingTable ||
        main.front().table_name != kBindingTable ||
        main.front().sql != kStoredSchemaSql) {
        throw std::runtime_error(
            label + " exact deployment-binding sqlite_schema mismatch");
    }
    const std::vector<SchemaObject> temporary =
        read_binding_schema_or_throw(database, "temp", label + " temp");
    if (!temporary.empty()) {
        throw std::runtime_error(
            label + " temporary deployment-binding shadow is forbidden");
    }
}

void require_opened_filename_or_throw(
    SyncSqliteDbHandleSlot& database,
    const fs::path& expected,
    const std::string& label) {
    auto borrow = database.borrow();
    const char* const opened = sqlite3_db_filename(borrow.get(), "main");
    if (opened == nullptr || *opened == '\0') {
        throw std::runtime_error(
            label + " could not prove the opened main-database filename");
    }
    const fs::path observed(opened);
    if (!observed.is_absolute() || observed.lexically_normal() != observed ||
        observed != expected) {
        throw std::runtime_error(
            label + " opened main-database filename conflicts with the binding");
    }
}

void require_detached_main_database_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    auto borrow = database.borrow();
    const char* const opened = sqlite3_db_filename(borrow.get(), "main");
    if (opened == nullptr || *opened != '\0') {
        throw std::runtime_error(
            label + " detached bootstrap image unexpectedly names a file");
    }
    const int read_only = sqlite3_db_readonly(borrow.get(), "main");
    if (read_only != 0) {
        throw std::runtime_error(
            label + (read_only > 0
                ? " detached bootstrap image is read-only"
                : " could not prove detached bootstrap image writability"));
    }

    // sqlite3_db_filename() also returns an empty name for an anonymous,
    // disk-backed temporary database. Such a database is not the private
    // namespace-free image promised by this initializer. MEMORY journaling is
    // the observable SQLite distinction used by the product's :memory: image.
    const std::string journal_mode = scalar_text_or_throw(
        database, "PRAGMA main.journal_mode;",
        label + " detached bootstrap image journal mode");
    if (journal_mode != "memory") {
        throw std::runtime_error(
            label + " detached bootstrap image journal mode is " +
            journal_mode + ", expected memory");
    }

}

void require_detached_bootstrap_image_empty_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    const std::uint64_t main_objects = scalar_u64_or_throw(
        database,
        "SELECT count(*) FROM main.sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%';",
        label + " persistent-schema count");
    const std::uint64_t temp_objects = scalar_u64_or_throw(
        database,
        "SELECT count(*) FROM temp.sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%';",
        label + " temporary-schema count");
    if (main_objects != 0U || temp_objects != 0U) {
        throw std::runtime_error(
            label + " must be schema-empty before deployment binding");
    }
}

enum class BindingFilenameAuthority : std::uint8_t {
    ExactOpenedPath = 1U,
    DetachedBootstrapImage = 2U,
};

void require_binding_filename_authority_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    BindingFilenameAuthority authority,
    const std::string& label) {
    switch (authority) {
        case BindingFilenameAuthority::ExactOpenedPath:
            require_opened_filename_or_throw(
                database, binding.database_path, label);
            return;
        case BindingFilenameAuthority::DetachedBootstrapImage:
            require_detached_main_database_or_throw(database, label);
            return;
    }
    throw std::invalid_argument(
        label + " binding filename authority is invalid");
}

void require_application_id_or_throw(
    SyncSqliteDbHandleSlot& database,
    std::uint32_t expected,
    const std::string& label) {
    const std::uint64_t observed = scalar_u64_or_throw(
        database, "PRAGMA main.application_id;", label + " application_id");
    if (observed != expected) {
        throw std::runtime_error(
            label + " SQLite application_id conflicts with the store role");
    }
}

void attest_binding_state_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    BindingFilenameAuthority filename_authority,
    const std::string& label) {
    require_binding_filename_authority_or_throw(
        database, binding, filename_authority, label);
    require_application_id_or_throw(
        database, sync_replica_sqlite_application_id(binding.role), label);
    require_exact_binding_schema_or_throw(database, label);

    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database,
        "SELECT id,format,deployment_id,manifest_digest,manifest_path,"
        "store_role,database_path,folder_id,local_device_id,local_epoch,"
        "sqlite_application_id,binding_digest FROM "
        "main.anonsync_store_set_binding ORDER BY id;",
        label + " row query prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        if (first == SQLITE_DONE) {
            throw std::runtime_error(label + " deployment binding row is absent");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first,
            label + " row query");
    }

    const std::uint64_t id = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " id");
    const std::string format = sqlite_column_text_or_throw(
        statement.stmt, 1, 128U, label + " format");
    const std::string deployment_id = sqlite_column_text_or_throw(
        statement.stmt, 2, 128U, label + " deployment_id");
    const std::string manifest_digest = sqlite_column_text_or_throw(
        statement.stmt, 3, 128U, label + " manifest_digest");
    const std::string manifest_path = sqlite_column_text_or_throw(
        statement.stmt, 4, kMaximumFieldBytes, label + " manifest_path");
    const std::string role = sqlite_column_text_or_throw(
        statement.stmt, 5, 128U, label + " store_role");
    const std::string database_path = sqlite_column_text_or_throw(
        statement.stmt, 6, kMaximumFieldBytes, label + " database_path");
    const std::string folder_id = sqlite_column_text_or_throw(
        statement.stmt, 7, 256U, label + " folder_id");
    const std::string local_device_id = sqlite_column_text_or_throw(
        statement.stmt, 8, 256U, label + " local_device_id");
    const std::uint64_t local_epoch = sqlite_column_u64_or_throw(
        statement.stmt, 9, label + " local_epoch");
    const std::uint64_t application_id = sqlite_column_u64_or_throw(
        statement.stmt, 10, label + " sqlite_application_id");
    const std::string binding_digest = sqlite_column_text_or_throw(
        statement.stmt, 11, 128U, label + " binding_digest");

    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " deployment binding contains excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " trailing row query");
    }

    const std::uint32_t expected_application_id =
        sync_replica_sqlite_application_id(binding.role);
    if (id != 1U || format != kBindingFormat ||
        deployment_id != binding.deployment.deployment_id ||
        manifest_digest != binding.deployment.manifest_digest ||
        manifest_path != binding.deployment.manifest_path.generic_string() ||
        role != sync_replica_sqlite_deployment_role_name(binding.role) ||
        database_path != binding.database_path.generic_string() ||
        folder_id != binding.deployment.folder_id ||
        local_device_id != binding.deployment.local_actor.device_id ||
        local_epoch != binding.deployment.local_actor.epoch ||
        application_id != expected_application_id ||
        binding_digest != binding_digest_or_throw(binding)) {
        throw std::runtime_error(
            label + " deployment binding does not match the selected manifest");
    }
}

void initialize_binding_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    BindingFilenameAuthority filename_authority,
    const std::string& label) {
    validate_sync_replica_sqlite_deployment_binding_or_throw(binding, label);
    require_binding_filename_authority_or_throw(
        database, binding, filename_authority, label);

    SyncSqliteTransaction transaction(
        database, label + " initialization",
        SyncSqliteTransactionMode::Immediate);
    const auto existing = read_binding_schema_or_throw(
        database, "main", label + " initialization main");
    const auto temporary = read_binding_schema_or_throw(
        database, "temp", label + " initialization temp");
    if (!existing.empty() || !temporary.empty()) {
        throw std::runtime_error(
            label + " deployment-binding namespace is already occupied");
    }
    const std::uint64_t prior_application_id = scalar_u64_or_throw(
        database, "PRAGMA main.application_id;",
        label + " prior application_id");
    if (prior_application_id != 0U) {
        throw std::runtime_error(
            label + " SQLite application_id is already occupied");
    }

    const std::uint32_t application_id =
        sync_replica_sqlite_application_id(binding.role);
    sqlite_exec_or_throw(
        database,
        "PRAGMA main.application_id=" + std::to_string(application_id) + ";",
        label + " application_id initialization");
    sqlite_exec_or_throw(
        database,
        "CREATE TABLE main." +
            std::string(kStoredSchemaSql).substr(
                std::string_view("CREATE TABLE ").size()) + ";",
        label + " table creation");

    SyncSqliteStmt insert = sqlite_prepare_or_throw(
        database,
        "INSERT INTO main.anonsync_store_set_binding("
        "id,format,deployment_id,manifest_digest,manifest_path,store_role,"
        "database_path,folder_id,local_device_id,local_epoch,"
        "sqlite_application_id,binding_digest) VALUES(1,?,?,?,?,?,?,?,?,?,?,?);",
        label + " row insert prepare");
    sqlite_bind_text_or_throw(
        insert.stmt, 1, std::string(kBindingFormat), label + " format bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 2, binding.deployment.deployment_id,
        label + " deployment_id bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 3, binding.deployment.manifest_digest,
        label + " manifest_digest bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 4, binding.deployment.manifest_path.generic_string(),
        label + " manifest_path bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 5,
        sync_replica_sqlite_deployment_role_name(binding.role),
        label + " store_role bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 6, binding.database_path.generic_string(),
        label + " database_path bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 7, binding.deployment.folder_id,
        label + " folder_id bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 8, binding.deployment.local_actor.device_id,
        label + " local_device_id bind");
    sqlite_bind_u64_or_throw(
        insert.stmt, 9, binding.deployment.local_actor.epoch,
        label + " local_epoch bind");
    sqlite_bind_u64_or_throw(
        insert.stmt, 10, application_id,
        label + " sqlite_application_id bind");
    sqlite_bind_text_or_throw(
        insert.stmt, 11, binding_digest_or_throw(binding),
        label + " binding_digest bind");
    sqlite_step_done_or_throw(insert.stmt, label + " row insert");

    attest_binding_state_or_throw(
        database, binding, filename_authority, label + " staged proof");
    transaction.commit();

    // Re-prove through a new read transaction after the durable/logical
    // boundary. A detached image has no filesystem durability yet, but this
    // still proves that the exact committed image is ready to be sealed.
    SyncSqliteTransaction proof(
        database, label + " committed proof attestation",
        SyncSqliteTransactionMode::Deferred);
    attest_binding_state_or_throw(
        database, binding, filename_authority, label + " committed proof");
    proof.commit();
}

}  // namespace

const char* sync_replica_sqlite_deployment_role_name(
    SyncReplicaSqliteDeploymentRole role) noexcept {
    switch (role) {
        case SyncReplicaSqliteDeploymentRole::Replica:
            return "replica";
        case SyncReplicaSqliteDeploymentRole::FileEffect:
            return "file-effect";
        case SyncReplicaSqliteDeploymentRole::TlsMembership:
            return "tls-membership";
        case SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor:
            return "tls-membership-anchor";
    }
    return "invalid";
}

std::uint32_t sync_replica_sqlite_application_id(
    SyncReplicaSqliteDeploymentRole role) {
    switch (role) {
        case SyncReplicaSqliteDeploymentRole::Replica:
            return kReplicaApplicationId;
        case SyncReplicaSqliteDeploymentRole::FileEffect:
            return kFileEffectApplicationId;
        case SyncReplicaSqliteDeploymentRole::TlsMembership:
            return kTlsMembershipApplicationId;
        case SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor:
            return kTlsMembershipAnchorApplicationId;
    }
    throw std::invalid_argument("SQLite deployment role is invalid");
}

void validate_sync_replica_sqlite_deployment_binding_or_throw(
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite deployment-binding validation label must not be empty");
    }
    validate_sync_replica_deployment_identity_or_throw(
        binding.deployment, label + " deployment identity");
    (void)sync_replica_sqlite_application_id(binding.role);
    require_canonical_absolute_path(binding.database_path, label);
    (void)binding_digest_or_throw(binding);
}

void initialize_sync_replica_sqlite_deployment_binding_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    initialize_binding_or_throw(
        database, binding, BindingFilenameAuthority::ExactOpenedPath, label);
}

void initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    require_detached_main_database_or_throw(database, label);
    require_detached_bootstrap_image_empty_or_throw(
        database, label + " detached bootstrap image");
    initialize_binding_or_throw(
        database, binding,
        BindingFilenameAuthority::DetachedBootstrapImage, label);
}

void attest_sync_replica_sqlite_deployment_binding_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    validate_sync_replica_sqlite_deployment_binding_or_throw(binding, label);
    SyncSqliteTransaction transaction(
        database, label + " attestation",
        SyncSqliteTransactionMode::Deferred);
    attest_binding_state_or_throw(
        database, binding, BindingFilenameAuthority::ExactOpenedPath, label);
    transaction.commit();
}

}  // namespace anonsync
