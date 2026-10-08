#include "sync_replica_file_effect_sqlite_owner.hpp"

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_effect_identity.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <limits>
#include <map>
#include <optional>
#include <span>
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

constexpr std::uint64_t kSchemaVersion = 3U;
constexpr std::uint64_t kLegacySchemaVersion = 2U;
constexpr std::uint64_t kMaxSchemaSqlBytes = 512U * 1024U;
constexpr std::uint64_t kMaxRootPathBytes = 32768U;

#if !defined(_WIN32)
[[nodiscard]] std::optional<std::uint64_t>
destination_component_byte_limit(
    const SyncDirectoryAttestation& attestation) noexcept {
    std::optional<std::uint64_t> limit;
    if (attestation.filesystem_name_maximum != 0U) {
        limit = attestation.filesystem_name_maximum;
    }
    if (attestation.path_name_maximum > 0) {
        const auto path_limit = static_cast<std::uint64_t>(
            attestation.path_name_maximum);
        limit = limit.has_value() ? std::min(*limit, path_limit)
                                  : path_limit;
    }
    return limit;
}

[[nodiscard]] bool destination_path_is_blocked(
    const SyncReplicaOperation& operation,
    const SyncDirectoryAuthority& root_authority) {
    const auto limit =
        destination_component_byte_limit(root_authority.attestation());
    if (!limit.has_value()) return false;
    const SyncValidationResult result =
        validate_sync_relative_path_component_byte_limit(
            operation.canonical_path, *limit);
    if (!result.ok &&
        result.reason !=
            "sync path component exceeds local filename byte limit") {
        throw std::logic_error(
            "validated file operation failed local path component preflight: " +
            result.reason);
    }
    return !result.ok;
}
#endif

struct SchemaDefinition final {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view stored_sql;
};

constexpr std::string_view kLegacyMetaSchemaSql =
    "CREATE TABLE sync_replica_file_effect_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=2),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "root_path TEXT NOT NULL CHECK(length(root_path) BETWEEN 1 AND 32768),"
    "root_authority_digest TEXT NOT NULL CHECK(length(root_authority_digest)=64),"
    "max_operations INTEGER NOT NULL CHECK(max_operations>0),"
    "max_context_entries INTEGER NOT NULL CHECK(max_context_entries>0),"
    "max_predecessor_ids INTEGER NOT NULL CHECK(max_predecessor_ids>0),"
    "max_canonical_operation_bytes INTEGER NOT NULL CHECK(max_canonical_operation_bytes>0),"
    "max_retained_canonical_bytes INTEGER NOT NULL CHECK(max_retained_canonical_bytes>0),"
    "max_retained_context_entries INTEGER NOT NULL CHECK(max_retained_context_entries>0),"
    "max_retained_predecessor_ids INTEGER NOT NULL CHECK(max_retained_predecessor_ids>0),"
    "max_effects INTEGER NOT NULL CHECK(max_effects>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "max_retained_payload_bytes INTEGER NOT NULL CHECK(max_retained_payload_bytes>0),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "effect_count INTEGER NOT NULL CHECK(effect_count>=0),"
    "published_count INTEGER NOT NULL CHECK(published_count>=0),"
    "retained_payload_bytes INTEGER NOT NULL CHECK(retained_payload_bytes>=0),"
    "effect_set_digest TEXT NOT NULL CHECK(length(effect_set_digest)=64),"
    "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT";

constexpr std::string_view kMetaSchemaSql =
    "CREATE TABLE sync_replica_file_effect_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=3),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "root_path TEXT NOT NULL CHECK(length(root_path) BETWEEN 1 AND 32768),"
    "root_authority_digest TEXT NOT NULL CHECK(length(root_authority_digest)=64),"
    "max_operations INTEGER NOT NULL CHECK(max_operations>0),"
    "max_context_entries INTEGER NOT NULL CHECK(max_context_entries>0),"
    "max_predecessor_ids INTEGER NOT NULL CHECK(max_predecessor_ids>0),"
    "max_canonical_operation_bytes INTEGER NOT NULL CHECK(max_canonical_operation_bytes>0),"
    "max_retained_canonical_bytes INTEGER NOT NULL CHECK(max_retained_canonical_bytes>0),"
    "max_retained_context_entries INTEGER NOT NULL CHECK(max_retained_context_entries>0),"
    "max_retained_predecessor_ids INTEGER NOT NULL CHECK(max_retained_predecessor_ids>0),"
    "max_effects INTEGER NOT NULL CHECK(max_effects>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "max_retained_payload_bytes INTEGER NOT NULL CHECK(max_retained_payload_bytes>0),"
    "max_effects_per_device INTEGER NOT NULL CHECK(max_effects_per_device>0),"
    "max_retained_payload_bytes_per_device INTEGER NOT NULL CHECK(max_retained_payload_bytes_per_device>0),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "effect_count INTEGER NOT NULL CHECK(effect_count>=0),"
    "published_count INTEGER NOT NULL CHECK(published_count>=0),"
    "retained_payload_bytes INTEGER NOT NULL CHECK(retained_payload_bytes>=0),"
    "device_count INTEGER NOT NULL CHECK(device_count>=0),"
    "effect_set_digest TEXT NOT NULL CHECK(length(effect_set_digest)=64),"
    "device_usage_digest TEXT NOT NULL CHECK(length(device_usage_digest)=64),"
    "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT";

constexpr std::string_view kEffectsSchemaSql =
    "CREATE TABLE sync_replica_file_effects("
    "operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),"
    "effect_id TEXT NOT NULL UNIQUE CHECK(length(effect_id)=64),"
    "canonical_operation BLOB NOT NULL,"
    "payload BLOB NOT NULL,"
    "canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
    "content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),"
    "size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),"
    "state TEXT NOT NULL CHECK(state IN ('staged','published')),"
    "staged_generation INTEGER NOT NULL CHECK(staged_generation>0),"
    "published_generation INTEGER NOT NULL CHECK(published_generation>=0),"
    "publication_digest TEXT NOT NULL CHECK(length(publication_digest) IN (0,64))) STRICT";

constexpr std::string_view kStateIndexSchemaSql =
    "CREATE INDEX sync_replica_file_effect_state ON sync_replica_file_effects(state,operation_id)";

constexpr std::array<SchemaDefinition, 3U> kLegacySchema{{
    {"table", "sync_replica_file_effect_meta",
     "sync_replica_file_effect_meta", kLegacyMetaSchemaSql},
    {"table", "sync_replica_file_effects", "sync_replica_file_effects",
     kEffectsSchemaSql},
    {"index", "sync_replica_file_effect_state",
     "sync_replica_file_effects", kStateIndexSchemaSql},
}};

constexpr std::array<SchemaDefinition, 3U> kSchema{{
    {"table", "sync_replica_file_effect_meta",
     "sync_replica_file_effect_meta", kMetaSchemaSql},
    {"table", "sync_replica_file_effects", "sync_replica_file_effects",
     kEffectsSchemaSql},
    {"index", "sync_replica_file_effect_state",
     "sync_replica_file_effects", kStateIndexSchemaSql},
}};

struct StoredEffect final {
    SyncReplicaFileEffectRecord record;
    std::string canonical_operation;
    std::string payload;

    bool operator==(const StoredEffect&) const = default;
};

struct LoadedState final {
    SyncReplicaFileEffectSqliteSnapshot snapshot;
    std::vector<StoredEffect> stored;

    bool operator==(const LoadedState&) const = default;
};

enum class SnapshotProjection {
    AuthorityOnly,
    PublicSnapshot,
};

struct DerivedAttestation final {
    std::uint64_t effect_count = 0U;
    std::uint64_t published_count = 0U;
    std::uint64_t retained_payload_bytes = 0U;
    std::vector<SyncReplicaFileEffectActorUsage> actor_usage;
    std::vector<SyncReplicaFileEffectDeviceUsage> device_usage;
    std::string effect_set_digest;
    std::string device_usage_digest;
    std::string cutpoint_digest;
};

[[nodiscard]] fs::path absolute_lexically_normal_path_or_throw(
    const fs::path& raw,
    const std::string& label) {
    if (raw.empty()) throw std::invalid_argument(label + " is empty");
    std::error_code error;
    fs::path absolute = fs::absolute(raw, error);
    if (error) {
        throw std::invalid_argument(label + " could not be resolved: " +
                                    error.message());
    }
    return absolute.lexically_normal();
}

[[nodiscard]] std::string normalized_root_text_or_throw(
    const fs::path& raw,
    const std::string& label) {
    const fs::path normalized =
        absolute_lexically_normal_path_or_throw(raw, label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(normalized, error);
    if (error || !fs::is_directory(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            label + " must be an existing non-symlink directory");
    }
    const std::string text = normalized.generic_string();
    if (text.empty() || text.size() > kMaxRootPathBytes) {
        throw std::invalid_argument(label + " exceeds its bounded text limit");
    }
    return text;
}

void checked_increment_or_throw(std::uint64_t& value,
                                const std::string& label) {
    if (value == std::numeric_limits<std::uint64_t>::max()) {
        throw std::runtime_error(label + " generation exhausted");
    }
    ++value;
}

void checked_add_or_throw(std::uint64_t& total,
                          std::uint64_t value,
                          const std::string& label) {
    if (value > std::numeric_limits<std::uint64_t>::max() - total) {
        throw std::runtime_error(label + " counter overflow");
    }
    total += value;
}

void validate_device_limits_or_throw(
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    const std::string& label) {
    if (limits.max_effects_per_device == 0U ||
        limits.max_retained_payload_bytes_per_device == 0U) {
        throw std::invalid_argument(
            label + " device effect limits must be positive");
    }
    (void)u64_to_sqlite_i64_or_throw(
        limits.max_effects_per_device,
        label + " max effects per device");
    (void)u64_to_sqlite_i64_or_throw(
        limits.max_retained_payload_bytes_per_device,
        label + " max retained payload bytes per device");
}

void validate_limits_or_throw(
    const std::string& folder_id,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    const std::string& label) {
    // The reference model is the shared validator for folder identity and all
    // canonical-operation bounds. The synthetic actor never mints evidence.
    (void)SyncReplicaModel(
        folder_id, SyncReplicaActor{"file-effect-limit-validator", 1U},
        limits.model);
    if (limits.max_effects == 0U || limits.max_payload_bytes == 0U ||
        limits.max_retained_payload_bytes == 0U) {
        throw std::invalid_argument(label + " effect limits must be positive");
    }
    validate_device_limits_or_throw(limits, label);
    if (limits.max_payload_bytes > limits.max_retained_payload_bytes) {
        throw std::invalid_argument(
            label + " per-payload limit exceeds retained-payload limit");
    }
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_operations, label + " max operations");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_context_entries, label + " max context entries");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_predecessor_ids, label + " max predecessor ids");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_canonical_operation_bytes,
        label + " max canonical operation bytes");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_retained_canonical_bytes,
        label + " max retained canonical bytes");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_retained_context_entries,
        label + " max retained context entries");
    (void)u64_to_sqlite_i64_or_throw(
        limits.model.max_retained_predecessor_ids,
        label + " max retained predecessor ids");
    (void)u64_to_sqlite_i64_or_throw(
        limits.max_effects, label + " max effects");
    (void)u64_to_sqlite_i64_or_throw(
        limits.max_payload_bytes, label + " max payload bytes");
    (void)u64_to_sqlite_i64_or_throw(
        limits.max_retained_payload_bytes,
        label + " max retained payload bytes");
}

[[nodiscard]] std::array<char, 8U> big_endian_u64(
    std::uint64_t value) noexcept {
    std::array<char, 8U> bytes{};
    for (std::size_t index = bytes.size(); index != 0U; --index) {
        bytes[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return bytes;
}

void digest_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    const auto bytes = big_endian_u64(value);
    digest.update(std::string_view(bytes.data(), bytes.size()));
}

void digest_field(Sha256DigestBuilder& digest, std::string_view value) {
    digest_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

[[nodiscard]] std::string publication_digest_or_throw(
    std::string_view root_path,
    std::string_view root_authority_digest,
    const SyncReplicaOperation& operation,
    std::string_view effect_id) {
    Sha256DigestBuilder digest;
    digest.update("anonsync-replica-file-effect-publication-v2");
    digest_field(digest, root_path);
    digest_field(digest, root_authority_digest);
    digest_field(digest, effect_id);
    digest_field(digest, operation.operation_id);
    digest_field(digest, operation.canonical_path);
    digest_field(digest, operation.content_sha256);
    digest_u64(digest, operation.size_bytes);
    return digest.finish_hex();
}

[[nodiscard]] std::string payload_from_span(
    std::span<const unsigned char> payload) {
    if (payload.empty()) return {};
    return {reinterpret_cast<const char*>(payload.data()), payload.size()};
}

[[nodiscard]] std::string_view payload_view_from_span(
    std::span<const unsigned char> payload) noexcept {
    if (payload.empty()) return {};
    return {reinterpret_cast<const char*>(payload.data()), payload.size()};
}

[[nodiscard]] std::string sha256_payload_span(
    std::span<const unsigned char> payload) {
    Sha256DigestBuilder digest;
    digest.update(payload_view_from_span(payload));
    return digest.finish_hex();
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& payload) noexcept {
    return {reinterpret_cast<const unsigned char*>(payload.data()),
            payload.size()};
}

[[nodiscard]] std::string_view state_text(
    SyncReplicaFileEffectState state) noexcept {
    switch (state) {
        case SyncReplicaFileEffectState::Staged:
            return "staged";
        case SyncReplicaFileEffectState::Published:
            return "published";
    }
    return "unknown";
}

[[nodiscard]] SyncReplicaFileEffectState parse_state_or_throw(
    std::string_view text,
    const std::string& label) {
    if (text == "staged") return SyncReplicaFileEffectState::Staged;
    if (text == "published") return SyncReplicaFileEffectState::Published;
    throw std::runtime_error(label + " has an unknown effect state");
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
            "file-effect schema definition has an unknown CREATE form");
    }
    statement.push_back(';');
    return statement;
}

using SchemaObject =
    std::tuple<std::string, std::string, std::string, std::string>;

[[nodiscard]] std::vector<SchemaObject> read_schema_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        // The deployment-binding table is owned and attested by the product
        // gate before this role owner is constructed. Exclude only that exact
        // namespace; every other foreign schema object remains a hard error.
        "SELECT type,name,tbl_name,sql FROM main.sqlite_schema "
        "WHERE name NOT GLOB 'sqlite_*' "
        "AND name<>'anonsync_store_set_binding' "
        "AND tbl_name<>'anonsync_store_set_binding' "
        "AND sql IS NOT NULL ORDER BY name;",
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
        constexpr std::size_t maximum_schema_objects =
            std::max(kSchema.size(), kLegacySchema.size());
        if (observed.size() >= maximum_schema_objects + 1U) {
            throw std::runtime_error(
                label + " schema object count exceeds its exact contract");
        }
        observed.emplace_back(
            sqlite_column_text_or_throw(
                statement.stmt, 0, 32U, label + " schema type"),
            sqlite_column_text_or_throw(
                statement.stmt, 1, 256U, label + " schema name"),
            sqlite_column_text_or_throw(
                statement.stmt, 2, 256U, label + " schema table"),
            sqlite_column_text_or_throw(
                statement.stmt, 3, kMaxSchemaSqlBytes,
                label + " schema SQL"));
    }
    return observed;
}

[[nodiscard]] bool schema_matches(
    const std::vector<SchemaObject>& observed,
    std::span<const SchemaDefinition> schema) {
    if (observed.size() != schema.size()) return false;
    std::map<std::string, const SchemaDefinition*> expected;
    for (const SchemaDefinition& definition : schema) {
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

void verify_schema_or_throw(SyncSqliteDbHandleSlot& db,
                            std::span<const SchemaDefinition> schema,
                            const std::string& label) {
    if (!schema_matches(read_schema_or_throw(db, label), schema)) {
        throw std::runtime_error(
            label + " exact sqlite_schema contract mismatch");
    }
}

void require_row_or_throw(sqlite3_stmt* statement,
                          const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW) {
        if (result == SQLITE_DONE) {
            throw std::runtime_error(label + " row is missing");
        }
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
}

void require_done_or_throw(sqlite3_stmt* statement,
                           const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result == SQLITE_ROW) {
        throw std::runtime_error(label + " returned more than one row");
    }
    if (result != SQLITE_DONE) {
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
}

[[nodiscard]] DerivedAttestation derive_content_attestation_or_throw(
    const std::vector<StoredEffect>& stored,
    const std::string& label) {
    DerivedAttestation out;
    out.effect_count = static_cast<std::uint64_t>(stored.size());

    Sha256DigestBuilder set_digest;
    set_digest.update("anonsync-replica-file-effect-set-v1");
    digest_u64(set_digest, out.effect_count);
    std::map<SyncReplicaActor, SyncReplicaFileEffectActorUsage>
        actor_usage;
    std::string prior_operation_id;
    for (const StoredEffect& effect : stored) {
        const SyncReplicaOperation& operation = effect.record.operation;
        if (!prior_operation_id.empty() &&
            operation.operation_id <= prior_operation_id) {
            throw std::runtime_error(
                label + " effects are not strictly ordered by operation id");
        }
        prior_operation_id = operation.operation_id;
        checked_add_or_throw(
            out.retained_payload_bytes,
            static_cast<std::uint64_t>(effect.payload.size()),
            label + " retained payload bytes");
        if (effect.record.state == SyncReplicaFileEffectState::Published) {
            checked_add_or_throw(
                out.published_count, 1U, label + " published count");
        }

        auto [usage, inserted] = actor_usage.try_emplace(
            operation.dot.actor);
        if (inserted) usage->second.actor = operation.dot.actor;
        checked_add_or_throw(
            usage->second.retained_effects, 1U,
            label + " actor retained effects");
        if (effect.record.state == SyncReplicaFileEffectState::Staged) {
            checked_add_or_throw(
                usage->second.staged_effects, 1U,
                label + " actor staged effects");
        } else {
            checked_add_or_throw(
                usage->second.published_effects, 1U,
                label + " actor published effects");
        }
        checked_add_or_throw(
            usage->second.retained_payload_bytes,
            static_cast<std::uint64_t>(effect.payload.size()),
            label + " actor retained payload bytes");

        digest_field(set_digest, operation.operation_id);
        digest_field(set_digest, effect.record.effect_id);
        digest_field(set_digest, effect.canonical_operation);
        digest_field(set_digest, effect.payload);
        digest_field(set_digest, state_text(effect.record.state));
        digest_u64(set_digest, effect.record.staged_generation);
        digest_u64(set_digest, effect.record.published_generation);
        digest_field(set_digest, effect.record.publication_digest);
    }
    out.effect_set_digest = set_digest.finish_hex();

    out.actor_usage.reserve(actor_usage.size());
    std::map<std::string, SyncReplicaFileEffectDeviceUsage> device_usage;
    for (auto& [actor, usage] : actor_usage) {
        (void)actor;
        auto [device, inserted] =
            device_usage.try_emplace(usage.actor.device_id);
        if (inserted) device->second.device_id = usage.actor.device_id;
        checked_add_or_throw(
            device->second.actor_epochs, 1U,
            label + " device actor epochs");
        checked_add_or_throw(
            device->second.retained_effects, usage.retained_effects,
            label + " device retained effects");
        checked_add_or_throw(
            device->second.staged_effects, usage.staged_effects,
            label + " device staged effects");
        checked_add_or_throw(
            device->second.published_effects, usage.published_effects,
            label + " device published effects");
        checked_add_or_throw(
            device->second.retained_payload_bytes,
            usage.retained_payload_bytes,
            label + " device retained payload bytes");
        out.actor_usage.push_back(std::move(usage));
    }
    out.device_usage.reserve(device_usage.size());
    for (auto& [device_id, usage] : device_usage) {
        (void)device_id;
        out.device_usage.push_back(std::move(usage));
    }

    Sha256DigestBuilder usage_digest;
    usage_digest.update("anonsync-replica-file-effect-device-usage-v1");
    digest_u64(
        usage_digest, static_cast<std::uint64_t>(out.device_usage.size()));
    for (const SyncReplicaFileEffectDeviceUsage& usage : out.device_usage) {
        digest_field(usage_digest, usage.device_id);
        digest_u64(usage_digest, usage.actor_epochs);
        digest_u64(usage_digest, usage.retained_effects);
        digest_u64(usage_digest, usage.staged_effects);
        digest_u64(usage_digest, usage.published_effects);
        digest_u64(usage_digest, usage.retained_payload_bytes);
    }
    out.device_usage_digest = usage_digest.finish_hex();
    return out;
}

void digest_legacy_policy(
    Sha256DigestBuilder& cutpoint,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits) {
    digest_u64(cutpoint, limits.model.max_operations);
    digest_u64(cutpoint, limits.model.max_context_entries);
    digest_u64(cutpoint, limits.model.max_predecessor_ids);
    digest_u64(cutpoint, limits.model.max_canonical_operation_bytes);
    digest_u64(cutpoint, limits.model.max_retained_canonical_bytes);
    digest_u64(cutpoint, limits.model.max_retained_context_entries);
    digest_u64(cutpoint, limits.model.max_retained_predecessor_ids);
    digest_u64(cutpoint, limits.max_effects);
    digest_u64(cutpoint, limits.max_payload_bytes);
    digest_u64(cutpoint, limits.max_retained_payload_bytes);
}

[[nodiscard]] DerivedAttestation derive_legacy_attestation_or_throw(
    const std::string& folder_id,
    std::string_view root_path,
    std::string_view root_authority_digest,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    const std::vector<StoredEffect>& stored,
    const std::string& label) {
    DerivedAttestation out =
        derive_content_attestation_or_throw(stored, label);
    Sha256DigestBuilder cutpoint;
    cutpoint.update("anonsync-replica-file-effect-cutpoint-v2");
    digest_u64(cutpoint, kLegacySchemaVersion);
    digest_field(cutpoint, folder_id);
    digest_field(cutpoint, root_path);
    digest_field(cutpoint, root_authority_digest);
    digest_legacy_policy(cutpoint, limits);
    digest_u64(cutpoint, state_generation);
    digest_u64(cutpoint, out.effect_count);
    digest_u64(cutpoint, out.published_count);
    digest_u64(cutpoint, out.retained_payload_bytes);
    digest_field(cutpoint, out.effect_set_digest);
    out.cutpoint_digest = cutpoint.finish_hex();
    return out;
}

[[nodiscard]] DerivedAttestation derive_attestation_or_throw(
    const std::string& folder_id,
    std::string_view root_path,
    std::string_view root_authority_digest,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    const std::vector<StoredEffect>& stored,
    const std::string& label) {
    DerivedAttestation out =
        derive_content_attestation_or_throw(stored, label);
    Sha256DigestBuilder cutpoint;
    cutpoint.update("anonsync-replica-file-effect-cutpoint-v3");
    digest_u64(cutpoint, kSchemaVersion);
    digest_field(cutpoint, folder_id);
    digest_field(cutpoint, root_path);
    digest_field(cutpoint, root_authority_digest);
    digest_legacy_policy(cutpoint, limits);
    digest_u64(cutpoint, limits.max_effects_per_device);
    digest_u64(
        cutpoint, limits.max_retained_payload_bytes_per_device);
    digest_u64(cutpoint, state_generation);
    digest_u64(cutpoint, out.effect_count);
    digest_u64(cutpoint, out.published_count);
    digest_u64(cutpoint, out.retained_payload_bytes);
    digest_u64(
        cutpoint, static_cast<std::uint64_t>(out.device_usage.size()));
    digest_field(cutpoint, out.effect_set_digest);
    digest_field(cutpoint, out.device_usage_digest);
    out.cutpoint_digest = cutpoint.finish_hex();
    return out;
}

void validate_stored_effect_or_throw(
    StoredEffect& stored,
    const std::string& expected_folder_id,
    std::string_view root_path,
    std::string_view root_authority_digest,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    const std::string& label) {
    SyncReplicaOperation operation =
        decode_sync_replica_operation_canonical_or_throw(
            stored.canonical_operation, limits.model);
    if (operation.operation_id != stored.record.operation.operation_id) {
        throw std::runtime_error(
            label + " canonical operation id does not match its row key");
    }
    if (operation.folder_id != expected_folder_id) {
        throw std::runtime_error(label + " operation belongs to another folder");
    }
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::runtime_error(label + " stores a non-file operation");
    }
    if (operation.canonical_path != stored.record.operation.canonical_path ||
        operation.content_sha256 != stored.record.operation.content_sha256 ||
        operation.size_bytes != stored.record.operation.size_bytes) {
        throw std::runtime_error(
            label + " redundant operation columns do not match canonical bytes");
    }
    if (operation.size_bytes != stored.payload.size() ||
        operation.size_bytes > limits.max_payload_bytes) {
        throw std::runtime_error(label + " payload size does not match operation");
    }
    if (sha256_hex(stored.payload) != operation.content_sha256) {
        throw std::runtime_error(label + " payload digest does not match operation");
    }
    const std::string expected_effect_id = make_sync_replica_file_effect_id_or_throw(operation);
    if (stored.record.effect_id != expected_effect_id) {
        throw std::runtime_error(label + " effect id mismatch");
    }
    if (stored.record.staged_generation == 0U ||
        stored.record.staged_generation > state_generation) {
        throw std::runtime_error(label + " staged generation is invalid");
    }
    if (stored.record.state == SyncReplicaFileEffectState::Staged) {
        if (stored.record.published_generation != 0U ||
            !stored.record.publication_digest.empty()) {
            throw std::runtime_error(
                label + " staged effect carries published authority");
        }
    } else {
        if (stored.record.published_generation <=
                stored.record.staged_generation ||
            stored.record.published_generation > state_generation) {
            throw std::runtime_error(
                label + " published generation is invalid");
        }
        const std::string expected_publication = publication_digest_or_throw(
            root_path, root_authority_digest, operation,
            stored.record.effect_id);
        if (stored.record.publication_digest != expected_publication) {
            throw std::runtime_error(label + " publication digest mismatch");
        }
    }
    stored.record.operation = std::move(operation);
}

void validate_transition_generations_or_throw(
    std::uint64_t state_generation,
    const std::vector<StoredEffect>& stored,
    const std::string& label) {
    std::vector<std::uint64_t> generations;
    if (stored.size() <=
        std::numeric_limits<std::size_t>::max() / 2U) {
        generations.reserve(stored.size() * 2U);
    }
    for (const StoredEffect& effect : stored) {
        generations.push_back(effect.record.staged_generation);
        if (effect.record.state == SyncReplicaFileEffectState::Published) {
            generations.push_back(effect.record.published_generation);
        }
    }
    if (state_generation !=
        static_cast<std::uint64_t>(generations.size())) {
        throw std::runtime_error(
            label +
            " state generation does not equal the retained transition count");
    }
    std::sort(generations.begin(), generations.end());
    for (std::size_t index = 0U; index < generations.size(); ++index) {
        const std::uint64_t expected =
            static_cast<std::uint64_t>(index) + 1U;
        if (generations[index] != expected) {
            throw std::runtime_error(
                label +
                " transition generations are not the exact gap-free sequence 1..state_generation");
        }
    }
}

void validate_loaded_identity_or_throw(
    const SyncReplicaFileEffectSqliteSnapshot& snapshot,
    std::string_view stored_root_path,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    const std::string& label) {
    if (snapshot.folder_id != expected_folder_id) {
        throw std::runtime_error(label + " folder identity mismatch");
    }
    if (stored_root_path != expected_root_path) {
        throw std::runtime_error(label + " root path identity mismatch");
    }
    if (snapshot.root_authority_digest !=
        expected_root_authority_digest) {
        throw std::runtime_error(
            label + " root directory authority identity mismatch");
    }
}

void load_effect_rows_or_throw(
    SyncSqliteDbHandleSlot& db,
    LoadedState& loaded,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    std::uint64_t stored_effect_count,
    const std::string& label) {
    const auto& limits = loaded.snapshot.limits;
    SyncSqliteStmt effects = sqlite_prepare_or_throw(
        db,
        "SELECT operation_id,effect_id,canonical_operation,payload,"
        "canonical_path,content_sha256,size_bytes,state,staged_generation,"
        "published_generation,publication_digest "
        "FROM main.sync_replica_file_effects ORDER BY operation_id;",
        label + " effects query prepare");
    loaded.stored.reserve(static_cast<std::size_t>(stored_effect_count));
    for (;;) {
        const int result = sqlite3_step(effects.stmt);
        if (result == SQLITE_DONE) break;
        if (result != SQLITE_ROW) {
            throw_sqlite_exception(
                sqlite3_db_handle(effects.stmt), result,
                label + " effects query");
        }
        if (loaded.stored.size() >= limits.max_effects) {
            throw std::runtime_error(label + " effect row count exceeds policy");
        }
        StoredEffect stored;
        stored.record.operation.operation_id = sqlite_column_text_or_throw(
            effects.stmt, 0, 64U, label + " operation id");
        stored.record.effect_id = sqlite_column_text_or_throw(
            effects.stmt, 1, 64U, label + " effect id");
        stored.canonical_operation = sqlite_column_blob_or_throw(
            effects.stmt, 2, limits.model.max_canonical_operation_bytes,
            label + " canonical operation");
        stored.payload = sqlite_column_blob_or_throw(
            effects.stmt, 3, limits.max_payload_bytes,
            label + " payload");
        stored.record.operation.canonical_path = sqlite_column_text_or_throw(
            effects.stmt, 4, 4096U, label + " canonical path");
        stored.record.operation.content_sha256 = sqlite_column_text_or_throw(
            effects.stmt, 5, 64U, label + " content digest");
        stored.record.operation.size_bytes = sqlite_column_u64_or_throw(
            effects.stmt, 6, label + " size bytes");
        stored.record.state = parse_state_or_throw(
            sqlite_column_text_or_throw(
                effects.stmt, 7, 16U, label + " effect state"),
            label);
        stored.record.staged_generation = sqlite_column_u64_or_throw(
            effects.stmt, 8, label + " staged generation");
        stored.record.published_generation = sqlite_column_u64_or_throw(
            effects.stmt, 9, label + " published generation");
        stored.record.publication_digest = sqlite_column_text_or_throw(
            effects.stmt, 10, 64U, label + " publication digest");
        validate_stored_effect_or_throw(
            stored, expected_folder_id, expected_root_path,
            expected_root_authority_digest, limits,
            loaded.snapshot.state_generation,
            label + " effect " + stored.record.operation.operation_id);
        loaded.stored.push_back(std::move(stored));
    }
    validate_transition_generations_or_throw(
        loaded.snapshot.state_generation, loaded.stored,
        label + " generation history");
}

void apply_derived_snapshot(
    LoadedState& loaded,
    DerivedAttestation&& derived,
    SnapshotProjection projection) {
    loaded.snapshot.retained_payload_bytes =
        derived.retained_payload_bytes;
    loaded.snapshot.actor_usage = std::move(derived.actor_usage);
    loaded.snapshot.device_usage = std::move(derived.device_usage);
    loaded.snapshot.effect_set_digest = std::move(derived.effect_set_digest);
    loaded.snapshot.device_usage_digest =
        std::move(derived.device_usage_digest);
    loaded.snapshot.cutpoint_digest = std::move(derived.cutpoint_digest);
    // Mutations consume the fully validated StoredEffect closure directly.
    // Constructing a second public record projection there copied every nested
    // operation and diagnostic string despite no caller observing it. Preserve
    // that O(history) copy only for the explicit public snapshot boundary.
    if (projection == SnapshotProjection::PublicSnapshot) {
        loaded.snapshot.effects.reserve(loaded.stored.size());
        for (StoredEffect& stored : loaded.stored) {
            loaded.snapshot.effects.push_back(std::move(stored.record));
        }
    }
}

[[nodiscard]] LoadedState load_legacy_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    const std::string& label,
    SnapshotProjection projection) {
    verify_schema_or_throw(db, kLegacySchema, label);

    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,root_path,root_authority_digest,max_operations,"
        "max_context_entries,max_predecessor_ids,"
        "max_canonical_operation_bytes,max_retained_canonical_bytes,"
        "max_retained_context_entries,max_retained_predecessor_ids,"
        "max_effects,max_payload_bytes,max_retained_payload_bytes,"
        "state_generation,effect_count,published_count,"
        "retained_payload_bytes,effect_set_digest,cutpoint_digest "
        "FROM main.sync_replica_file_effect_meta WHERE id=1 LIMIT 2;",
        label + " legacy meta query prepare");
    require_row_or_throw(meta.stmt, label + " legacy meta query");

    if (sqlite_column_u64_or_throw(
            meta.stmt, 0, label + " legacy schema version") !=
        kLegacySchemaVersion) {
        throw std::runtime_error(label + " legacy schema version mismatch");
    }
    LoadedState loaded;
    loaded.snapshot.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder id");
    const std::string root_path = sqlite_column_text_or_throw(
        meta.stmt, 2, kMaxRootPathBytes, label + " root path");
    loaded.snapshot.root_path = fs::path(root_path);
    loaded.snapshot.root_authority_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U, label + " root authority digest");
    auto& limits = loaded.snapshot.limits;
    limits.model.max_operations = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " max operations");
    limits.model.max_context_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " max context entries");
    limits.model.max_predecessor_ids = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " max predecessor ids");
    limits.model.max_canonical_operation_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " max canonical operation bytes");
    limits.model.max_retained_canonical_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " max retained canonical bytes");
    limits.model.max_retained_context_entries = sqlite_column_u64_or_throw(
        meta.stmt, 9, label + " max retained context entries");
    limits.model.max_retained_predecessor_ids = sqlite_column_u64_or_throw(
        meta.stmt, 10, label + " max retained predecessor ids");
    limits.max_effects = sqlite_column_u64_or_throw(
        meta.stmt, 11, label + " max effects");
    limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 12, label + " max payload bytes");
    limits.max_retained_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 13, label + " max retained payload bytes");
    // v2 had no device-isolation policy. These provisional values are used
    // only to run the shared structural validator before migration; the
    // constructor replaces them with the two explicitly supplied v3 fields.
    limits.max_effects_per_device = limits.max_effects;
    limits.max_retained_payload_bytes_per_device =
        limits.max_retained_payload_bytes;
    loaded.snapshot.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 14, label + " state generation");
    const std::uint64_t stored_effect_count = sqlite_column_u64_or_throw(
        meta.stmt, 15, label + " effect count");
    const std::uint64_t stored_published_count = sqlite_column_u64_or_throw(
        meta.stmt, 16, label + " published count");
    const std::uint64_t stored_retained_payload = sqlite_column_u64_or_throw(
        meta.stmt, 17, label + " retained payload bytes");
    const std::string stored_effect_set_digest = sqlite_column_text_or_throw(
        meta.stmt, 18, 64U, label + " effect set digest");
    const std::string stored_cutpoint_digest = sqlite_column_text_or_throw(
        meta.stmt, 19, 64U, label + " cutpoint digest");
    require_done_or_throw(meta.stmt, label + " legacy meta query");

    validate_loaded_identity_or_throw(
        loaded.snapshot, root_path, expected_folder_id, expected_root_path,
        expected_root_authority_digest, label);
    validate_limits_or_throw(
        loaded.snapshot.folder_id, limits, label + " persisted legacy limits");
    if (stored_effect_count > limits.max_effects) {
        throw std::runtime_error(label + " effect count exceeds policy");
    }
    load_effect_rows_or_throw(
        db, loaded, expected_folder_id, expected_root_path,
        expected_root_authority_digest, stored_effect_count, label);

    DerivedAttestation derived = derive_legacy_attestation_or_throw(
        expected_folder_id, expected_root_path,
        expected_root_authority_digest, limits,
        loaded.snapshot.state_generation, loaded.stored, label);
    if (derived.effect_count != stored_effect_count ||
        derived.published_count != stored_published_count ||
        derived.retained_payload_bytes != stored_retained_payload ||
        derived.effect_set_digest != stored_effect_set_digest ||
        derived.cutpoint_digest != stored_cutpoint_digest) {
        throw std::runtime_error(
            label + " durable legacy cutpoint attestation mismatch");
    }
    if (derived.retained_payload_bytes >
        limits.max_retained_payload_bytes) {
        throw std::runtime_error(
            label + " retained payload bytes exceed persisted policy");
    }
    apply_derived_snapshot(loaded, std::move(derived), projection);
    return loaded;
}

struct LoadedEffectMeta final {
    SyncReplicaFileEffectSqliteIdentityCutpoint identity;
    std::string root_path_text;
    std::uint64_t effect_count = 0U;
    std::uint64_t published_count = 0U;
    std::uint64_t retained_payload_bytes = 0U;
    std::uint64_t device_count = 0U;
    std::string effect_set_digest;
    std::string device_usage_digest;
    std::string cutpoint_digest;
};

[[nodiscard]] LoadedEffectMeta read_effect_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    SyncSqliteStmt meta = sqlite_prepare_or_throw(
        db,
        "SELECT schema_version,folder_id,root_path,root_authority_digest,max_operations,"
        "max_context_entries,max_predecessor_ids,"
        "max_canonical_operation_bytes,max_retained_canonical_bytes,"
        "max_retained_context_entries,max_retained_predecessor_ids,"
        "max_effects,max_payload_bytes,max_retained_payload_bytes,"
        "max_effects_per_device,max_retained_payload_bytes_per_device,"
        "state_generation,effect_count,published_count,"
        "retained_payload_bytes,device_count,effect_set_digest,"
        "device_usage_digest,cutpoint_digest "
        "FROM main.sync_replica_file_effect_meta WHERE id=1 LIMIT 2;",
        label + " meta query prepare");
    require_row_or_throw(meta.stmt, label + " meta query");
    if (sqlite_column_u64_or_throw(
            meta.stmt, 0, label + " schema version") != kSchemaVersion) {
        throw std::runtime_error(label + " schema version mismatch");
    }

    LoadedEffectMeta loaded;
    auto& identity = loaded.identity;
    identity.folder_id = sqlite_column_text_or_throw(
        meta.stmt, 1, 128U, label + " folder id");
    loaded.root_path_text = sqlite_column_text_or_throw(
        meta.stmt, 2, kMaxRootPathBytes, label + " root path");
    identity.root_path = fs::path(loaded.root_path_text);
    identity.root_authority_digest = sqlite_column_text_or_throw(
        meta.stmt, 3, 64U, label + " root authority digest");
    auto& limits = identity.limits;
    limits.model.max_operations = sqlite_column_u64_or_throw(
        meta.stmt, 4, label + " max operations");
    limits.model.max_context_entries = sqlite_column_u64_or_throw(
        meta.stmt, 5, label + " max context entries");
    limits.model.max_predecessor_ids = sqlite_column_u64_or_throw(
        meta.stmt, 6, label + " max predecessor ids");
    limits.model.max_canonical_operation_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 7, label + " max canonical operation bytes");
    limits.model.max_retained_canonical_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 8, label + " max retained canonical bytes");
    limits.model.max_retained_context_entries = sqlite_column_u64_or_throw(
        meta.stmt, 9, label + " max retained context entries");
    limits.model.max_retained_predecessor_ids = sqlite_column_u64_or_throw(
        meta.stmt, 10, label + " max retained predecessor ids");
    limits.max_effects = sqlite_column_u64_or_throw(
        meta.stmt, 11, label + " max effects");
    limits.max_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 12, label + " max payload bytes");
    limits.max_retained_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 13, label + " max retained payload bytes");
    limits.max_effects_per_device = sqlite_column_u64_or_throw(
        meta.stmt, 14, label + " max effects per device");
    limits.max_retained_payload_bytes_per_device =
        sqlite_column_u64_or_throw(
            meta.stmt, 15,
            label + " max retained payload bytes per device");
    identity.state_generation = sqlite_column_u64_or_throw(
        meta.stmt, 16, label + " state generation");
    loaded.effect_count = sqlite_column_u64_or_throw(
        meta.stmt, 17, label + " effect count");
    loaded.published_count = sqlite_column_u64_or_throw(
        meta.stmt, 18, label + " published count");
    loaded.retained_payload_bytes = sqlite_column_u64_or_throw(
        meta.stmt, 19, label + " retained payload bytes");
    loaded.device_count = sqlite_column_u64_or_throw(
        meta.stmt, 20, label + " device count");
    loaded.effect_set_digest = sqlite_column_text_or_throw(
        meta.stmt, 21, 64U, label + " effect set digest");
    loaded.device_usage_digest = sqlite_column_text_or_throw(
        meta.stmt, 22, 64U, label + " device usage digest");
    loaded.cutpoint_digest = sqlite_column_text_or_throw(
        meta.stmt, 23, 64U, label + " cutpoint digest");
    require_done_or_throw(meta.stmt, label + " meta query");
    return loaded;
}

void validate_effect_identity_cutpoint_or_throw(
    const LoadedEffectMeta& loaded,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    const std::string& label) {
    SyncReplicaFileEffectSqliteSnapshot identity;
    identity.folder_id = loaded.identity.folder_id;
    identity.root_path = loaded.identity.root_path;
    identity.root_authority_digest =
        loaded.identity.root_authority_digest;
    identity.limits = loaded.identity.limits;
    identity.state_generation = loaded.identity.state_generation;
    validate_loaded_identity_or_throw(
        identity, loaded.root_path_text, expected_folder_id,
        expected_root_path, expected_root_authority_digest, label);
    validate_limits_or_throw(
        loaded.identity.folder_id, loaded.identity.limits,
        label + " persisted limits");
}

[[nodiscard]] SyncReplicaFileEffectSqliteIdentityCutpoint
load_identity_cutpoint_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    const std::string& label) {
    verify_schema_or_throw(db, kSchema, label);
    LoadedEffectMeta loaded = read_effect_meta_or_throw(db, label);
    validate_effect_identity_cutpoint_or_throw(
        loaded, expected_folder_id, expected_root_path,
        expected_root_authority_digest, label);
    return std::move(loaded.identity);
}

[[nodiscard]] LoadedState load_state_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& expected_folder_id,
    std::string_view expected_root_path,
    std::string_view expected_root_authority_digest,
    const std::string& label,
    SnapshotProjection projection) {
    verify_schema_or_throw(db, kSchema, label);
    LoadedEffectMeta meta = read_effect_meta_or_throw(db, label);
    validate_effect_identity_cutpoint_or_throw(
        meta, expected_folder_id, expected_root_path,
        expected_root_authority_digest, label);

    LoadedState loaded;
    loaded.snapshot.folder_id = meta.identity.folder_id;
    loaded.snapshot.root_path = meta.identity.root_path;
    loaded.snapshot.root_authority_digest =
        meta.identity.root_authority_digest;
    loaded.snapshot.limits = meta.identity.limits;
    loaded.snapshot.state_generation = meta.identity.state_generation;
    const auto& limits = loaded.snapshot.limits;
    const std::uint64_t stored_effect_count = meta.effect_count;
    const std::uint64_t stored_published_count = meta.published_count;
    const std::uint64_t stored_retained_payload =
        meta.retained_payload_bytes;
    const std::uint64_t stored_device_count = meta.device_count;
    const std::string& stored_effect_set_digest = meta.effect_set_digest;
    const std::string& stored_device_usage_digest =
        meta.device_usage_digest;
    const std::string& stored_cutpoint_digest = meta.cutpoint_digest;

    if (stored_effect_count > limits.max_effects) {
        throw std::runtime_error(label + " effect count exceeds policy");
    }
    load_effect_rows_or_throw(
        db, loaded, expected_folder_id, expected_root_path,
        expected_root_authority_digest, stored_effect_count, label);

    DerivedAttestation derived = derive_attestation_or_throw(
        expected_folder_id, expected_root_path,
        expected_root_authority_digest, limits,
        loaded.snapshot.state_generation, loaded.stored, label);
    if (derived.effect_count != stored_effect_count ||
        derived.published_count != stored_published_count ||
        derived.retained_payload_bytes != stored_retained_payload ||
        static_cast<std::uint64_t>(derived.device_usage.size()) !=
            stored_device_count ||
        derived.effect_set_digest != stored_effect_set_digest ||
        derived.device_usage_digest != stored_device_usage_digest ||
        derived.cutpoint_digest != stored_cutpoint_digest) {
        throw std::runtime_error(label + " durable cutpoint attestation mismatch");
    }
    if (derived.retained_payload_bytes >
        limits.max_retained_payload_bytes) {
        throw std::runtime_error(
            label + " retained payload bytes exceed persisted policy");
    }
    // Existing retained rows may predate a stricter device-isolation policy.
    // They remain canonical authority and block only future unique admission;
    // reconstruction must never delete or rewrite them to satisfy a new cap.
    apply_derived_snapshot(loaded, std::move(derived), projection);
    return loaded;
}

void bind_limits_or_throw(sqlite3_stmt* statement,
                          int first_index,
                          const SyncReplicaFileEffectSqliteOwnerLimits& limits,
                          const std::string& label) {
    sqlite_bind_u64_or_throw(statement, first_index + 0,
                             limits.model.max_operations, label);
    sqlite_bind_u64_or_throw(statement, first_index + 1,
                             limits.model.max_context_entries, label);
    sqlite_bind_u64_or_throw(statement, first_index + 2,
                             limits.model.max_predecessor_ids, label);
    sqlite_bind_u64_or_throw(
        statement, first_index + 3,
        limits.model.max_canonical_operation_bytes, label);
    sqlite_bind_u64_or_throw(
        statement, first_index + 4,
        limits.model.max_retained_canonical_bytes, label);
    sqlite_bind_u64_or_throw(
        statement, first_index + 5,
        limits.model.max_retained_context_entries, label);
    sqlite_bind_u64_or_throw(
        statement, first_index + 6,
        limits.model.max_retained_predecessor_ids, label);
    sqlite_bind_u64_or_throw(statement, first_index + 7,
                             limits.max_effects, label);
    sqlite_bind_u64_or_throw(statement, first_index + 8,
                             limits.max_payload_bytes, label);
    sqlite_bind_u64_or_throw(statement, first_index + 9,
                             limits.max_retained_payload_bytes, label);
    sqlite_bind_u64_or_throw(statement, first_index + 10,
                             limits.max_effects_per_device, label);
    sqlite_bind_u64_or_throw(
        statement, first_index + 11,
        limits.max_retained_payload_bytes_per_device, label);
}

void insert_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_authority_digest,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    std::uint64_t state_generation,
    const std::vector<StoredEffect>& stored,
    const std::string& label) {
    const DerivedAttestation derived = derive_attestation_or_throw(
        folder_id, root_path, root_authority_digest, limits,
        state_generation, stored, label);
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_file_effect_meta("
        "id,schema_version,folder_id,root_path,root_authority_digest,max_operations,"
        "max_context_entries,max_predecessor_ids,"
        "max_canonical_operation_bytes,max_retained_canonical_bytes,"
        "max_retained_context_entries,max_retained_predecessor_ids,"
        "max_effects,max_payload_bytes,max_retained_payload_bytes,"
        "max_effects_per_device,max_retained_payload_bytes_per_device,"
        "state_generation,effect_count,published_count,"
        "retained_payload_bytes,device_count,effect_set_digest,"
        "device_usage_digest,cutpoint_digest) "
        "VALUES(1,3,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
        label + " meta prepare");
    sqlite_bind_text_or_throw(statement.stmt, 1, folder_id, label);
    sqlite_bind_text_or_throw(statement.stmt, 2, root_path, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 3, root_authority_digest, label);
    bind_limits_or_throw(statement.stmt, 4, limits, label);
    sqlite_bind_u64_or_throw(statement.stmt, 16, state_generation, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 17, derived.effect_count, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 18, derived.published_count, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 19, derived.retained_payload_bytes, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 20,
        static_cast<std::uint64_t>(derived.device_usage.size()), label);
    sqlite_bind_text_or_throw(
        statement.stmt, 21, derived.effect_set_digest, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 22, derived.device_usage_digest, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 23, derived.cutpoint_digest, label);
    sqlite_step_done_or_throw(statement.stmt, label + " meta insert");
}

void insert_initial_meta_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& folder_id,
    const std::string& root_path,
    const std::string& root_authority_digest,
    const SyncReplicaFileEffectSqliteOwnerLimits& limits,
    const std::string& label) {
    insert_meta_or_throw(
        db, folder_id, root_path, root_authority_digest, limits, 0U, {},
        label + " initial");
}

void update_meta_or_throw(SyncSqliteDbHandleSlot& db,
                          const LoadedState& state,
                          const std::string& root_path,
                          const std::string& root_authority_digest,
                          const std::string& label) {
    const DerivedAttestation derived = derive_attestation_or_throw(
        state.snapshot.folder_id, root_path, root_authority_digest,
        state.snapshot.limits, state.snapshot.state_generation, state.stored,
        label);
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_file_effect_meta SET "
        "state_generation=?,effect_count=?,published_count=?,"
        "retained_payload_bytes=?,device_count=?,effect_set_digest=?,"
        "device_usage_digest=?,cutpoint_digest=? WHERE id=1;",
        label + " meta update prepare");
    sqlite_bind_u64_or_throw(
        statement.stmt, 1, state.snapshot.state_generation, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 2, derived.effect_count, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 3, derived.published_count, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 4, derived.retained_payload_bytes, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 5,
        static_cast<std::uint64_t>(derived.device_usage.size()), label);
    sqlite_bind_text_or_throw(
        statement.stmt, 6, derived.effect_set_digest, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 7, derived.device_usage_digest, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 8, derived.cutpoint_digest, label);
    sqlite_step_done_or_throw(statement.stmt, label + " meta update");
    if (sqlite3_changes(sqlite3_db_handle(statement.stmt)) != 1) {
        throw std::runtime_error(label + " meta update did not own one row");
    }
}

void insert_effect_or_throw(SyncSqliteDbHandleSlot& db,
                            const StoredEffect& stored,
                            const std::string& label) {
    const SyncReplicaOperation& operation = stored.record.operation;
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_file_effects("
        "operation_id,effect_id,canonical_operation,payload,canonical_path,"
        "content_sha256,size_bytes,state,staged_generation,"
        "published_generation,publication_digest) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?);",
        label + " effect insert prepare");
    sqlite_bind_text_or_throw(
        statement.stmt, 1, operation.operation_id, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 2, stored.record.effect_id, label);
    sqlite_bind_blob_or_throw(
        statement.stmt, 3, stored.canonical_operation, label);
    sqlite_bind_blob_or_throw(statement.stmt, 4, stored.payload, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 5, operation.canonical_path, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 6, operation.content_sha256, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 7, operation.size_bytes, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 8, std::string(state_text(stored.record.state)), label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 9, stored.record.staged_generation, label);
    sqlite_bind_u64_or_throw(
        statement.stmt, 10, stored.record.published_generation, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 11, stored.record.publication_digest, label);
    sqlite_step_done_or_throw(statement.stmt, label + " effect insert");
}

void mark_effect_published_or_throw(SyncSqliteDbHandleSlot& db,
                                    const StoredEffect& stored,
                                    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_replica_file_effects SET "
        "state='published',published_generation=?,publication_digest=? "
        "WHERE operation_id=? AND state='staged' AND effect_id=?;",
        label + " publication update prepare");
    sqlite_bind_u64_or_throw(
        statement.stmt, 1, stored.record.published_generation, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 2, stored.record.publication_digest, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 3, stored.record.operation.operation_id, label);
    sqlite_bind_text_or_throw(
        statement.stmt, 4, stored.record.effect_id, label);
    sqlite_step_done_or_throw(statement.stmt, label + " publication update");
    if (sqlite3_changes(sqlite3_db_handle(statement.stmt)) != 1) {
        throw std::runtime_error(
            label + " publication transition did not own one staged row");
    }
}

[[nodiscard]] auto find_effect(std::vector<StoredEffect>& effects,
                               std::string_view operation_id) {
    return std::lower_bound(
        effects.begin(), effects.end(), operation_id,
        [](const StoredEffect& left, std::string_view right) {
            return left.record.operation.operation_id < right;
        });
}

[[nodiscard]] fs::path canonical_relative_effect_path_or_throw(
    const SyncReplicaOperation& operation,
    const std::string& label) {
    // Canonical operation validation already rejects empty, dot, dot-dot, and
    // nonportable separator components. Repeat the composition-boundary proof
    // before converting the durable string into a filesystem capability input.
    const fs::path relative(operation.canonical_path);
    if (relative.empty() || relative.is_absolute() ||
        relative.has_root_name() || relative.has_root_directory() ||
        relative.lexically_normal() != relative) {
        throw std::runtime_error(
            label + " operation path is not a canonical relative path");
    }
    for (const fs::path& component_path : relative) {
        const std::string component = component_path.string();
        if (component.empty() || component == "." || component == ".." ||
            component.find('/') != std::string::npos ||
            component.find('\\') != std::string::npos ||
            component.find('\0') != std::string::npos) {
            throw std::runtime_error(
                label + " operation path contains an unsafe component");
        }
    }
    return relative;
}

#if defined(_WIN32)
[[nodiscard]] fs::path destination_path_or_throw(
    const fs::path& root,
    const fs::path& canonical_relative_path,
    const std::string& label) {
    const fs::path destination =
        (root / canonical_relative_path).lexically_normal();
    const fs::path expected = root.lexically_normal();
    auto root_it = expected.begin();
    auto destination_it = destination.begin();
    for (; root_it != expected.end(); ++root_it, ++destination_it) {
        if (destination_it == destination.end() ||
            *destination_it != *root_it) {
            throw std::runtime_error(
                label + " operation path escapes the effect root");
        }
    }
    return destination;
}
#endif

void require_published_file_exact_or_throw(
    SyncImmutableFileReconciliationOutcome outcome,
    const std::string& label) {
    if (outcome ==
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        return;
    }
    if (outcome == SyncImmutableFileReconciliationOutcome::Absent) {
        throw std::runtime_error(
            label + " durable published state has no final file");
    }
    throw std::runtime_error(
        label + " durable published state conflicts with the final entry");
}

}  // namespace

SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_read_only_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    fs::path root_path,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file-effect read-only inspection label must not be empty");
    }
    const fs::path normalized_root = absolute_lexically_normal_path_or_throw(
        root_path, label + " root path");
    const std::string root_text = normalized_root_text_or_throw(
        normalized_root, label + " root path");
#if !defined(_WIN32)
    SyncDirectoryAuthority root_authority = SyncDirectoryAuthority::open_or_throw(
        normalized_root, label + " root authority");
    const std::string root_authority_digest =
        sync_directory_attestation_digest_or_throw(
            root_authority.attestation());
#else
    const std::string root_authority_digest = sha256_hex(
        std::string("anonsync-windows-file-effect-root-path-v1:") +
        root_text);
#endif
    {
        auto database = borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " read-only connection proof");
        if (sqlite3_db_readonly(database.get(), "main") != 1) {
            throw std::runtime_error(
                label + " requires a read-only main database connection");
        }
    }
#if !defined(_WIN32)
    root_authority.verify_or_throw(label + " snapshot root authority");
#endif
    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedState loaded = load_state_or_throw(
        db, folder_id, root_text, root_authority_digest,
        label + " snapshot", SnapshotProjection::PublicSnapshot);
#if !defined(_WIN32)
    root_authority.verify_or_throw(
        label + " snapshot pre-commit root authority");
#endif
    transaction.commit();
    return std::move(loaded.snapshot);
}

namespace {

[[nodiscard]] SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_impl_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    fs::path expected_root_path,
    bool attested_detached_image,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file-effect offline inspection label must not be empty");
    }
    if (folder_id.empty()) {
        throw std::invalid_argument(label + " folder identity is empty");
    }
    if (expected_root_path.empty() || !expected_root_path.is_absolute() ||
        expected_root_path.lexically_normal() != expected_root_path) {
        throw std::invalid_argument(
            label + " root path must be canonical and absolute");
    }
    const std::string expected_root_text =
        expected_root_path.generic_string();
    if (expected_root_text.empty() ||
        expected_root_text.size() > kMaxRootPathBytes ||
        expected_root_text.find('\0') != std::string::npos) {
        throw std::invalid_argument(
            label + " root path exceeds its bounded text contract");
    }
    if (!attested_detached_image) {
        auto database = borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " read-only connection proof");
        if (sqlite3_db_readonly(database.get(), "main") != 1) {
            throw std::runtime_error(
                label + " requires a read-only main database connection");
        }
    }

    SyncSqliteTransaction transaction(
        db, label + " snapshot", SyncSqliteTransactionMode::Deferred);
    verify_schema_or_throw(db, kSchema, label + " schema");
    SyncSqliteStmt identity = sqlite_prepare_or_throw(
        db,
        "SELECT folder_id,root_path,root_authority_digest "
        "FROM main.sync_replica_file_effect_meta WHERE id=1 LIMIT 2;",
        label + " persisted root identity prepare");
    require_row_or_throw(identity.stmt, label + " persisted root identity");
    const std::string stored_folder_id = sqlite_column_text_or_throw(
        identity.stmt, 0, 128U, label + " persisted folder identity");
    const std::string stored_root_path = sqlite_column_text_or_throw(
        identity.stmt, 1, kMaxRootPathBytes,
        label + " persisted root path");
    const std::string stored_root_authority_digest =
        sqlite_column_text_or_throw(
            identity.stmt, 2, 64U,
            label + " persisted root authority digest");
    require_done_or_throw(
        identity.stmt, label + " persisted root identity");
    const bool digest_valid =
        stored_root_authority_digest.size() == 64U &&
        std::all_of(
            stored_root_authority_digest.begin(),
            stored_root_authority_digest.end(),
            [](char value) {
                return (value >= '0' && value <= '9') ||
                       (value >= 'a' && value <= 'f');
            });
    if (stored_folder_id != folder_id ||
        stored_root_path != expected_root_text ||
        stored_root_path.find('\0') != std::string::npos ||
        !digest_valid) {
        throw std::runtime_error(
            label + " persisted root identity is invalid or mismatched");
    }

    LoadedState loaded = load_state_or_throw(
        db, folder_id, expected_root_text,
        stored_root_authority_digest, label + " snapshot",
        SnapshotProjection::PublicSnapshot);
    transaction.commit();
    return std::move(loaded.snapshot);
}

}  // namespace

SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    fs::path expected_root_path,
    std::string label) {
    return inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_impl_or_throw(
        db, std::move(folder_id), std::move(expected_root_path), false,
        std::move(label));
}

SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    fs::path expected_root_path,
    std::string label) {
    return inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_impl_or_throw(
        db, std::move(folder_id), std::move(expected_root_path), true,
        std::move(label));
}

const char* sync_replica_file_effect_state_name(
    SyncReplicaFileEffectState state) noexcept {
    switch (state) {
        case SyncReplicaFileEffectState::Staged:
            return "staged";
        case SyncReplicaFileEffectState::Published:
            return "published";
    }
    return "unknown";
}

const char* sync_replica_file_effect_stage_result_name(
    SyncReplicaFileEffectStageResult result) noexcept {
    switch (result) {
        case SyncReplicaFileEffectStageResult::Inserted:
            return "inserted";
        case SyncReplicaFileEffectStageResult::Duplicate:
            return "duplicate";
        case SyncReplicaFileEffectStageResult::CapacityBlocked:
            return "capacity_blocked";
        case SyncReplicaFileEffectStageResult::DestinationPathBlocked:
            return "destination_path_blocked";
    }
    return "unknown";
}

const char* sync_replica_file_effect_capacity_constraint_name(
    SyncReplicaFileEffectCapacityConstraint constraint) noexcept {
    switch (constraint) {
        case SyncReplicaFileEffectCapacityConstraint::None:
            return "none";
        case SyncReplicaFileEffectCapacityConstraint::FolderEffectCount:
            return "folder_effect_count";
        case SyncReplicaFileEffectCapacityConstraint::
            FolderRetainedPayloadBytes:
            return "folder_retained_payload_bytes";
        case SyncReplicaFileEffectCapacityConstraint::DeviceEffectCount:
            return "device_effect_count";
        case SyncReplicaFileEffectCapacityConstraint::
            DeviceRetainedPayloadBytes:
            return "device_retained_payload_bytes";
    }
    return "unknown";
}

const char* sync_replica_file_effect_materialize_result_name(
    SyncReplicaFileEffectMaterializeResult result) noexcept {
    switch (result) {
        case SyncReplicaFileEffectMaterializeResult::Published:
            return "published";
        case SyncReplicaFileEffectMaterializeResult::AlreadyPublished:
            return "already_published";
        case SyncReplicaFileEffectMaterializeResult::DestinationConflict:
            return "destination_conflict";
    }
    return "unknown";
}

SyncReplicaFileEffectSqliteOwner::SyncReplicaFileEffectSqliteOwner(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    fs::path root_path,
    SyncReplicaFileEffectSqliteOwnerLimits initial_limits,
    std::string label)
    : db_(db),
      folder_id_(std::move(folder_id)),
      root_path_(absolute_lexically_normal_path_or_throw(
          root_path, "sync replica file-effect root path")),
      root_path_text_(normalized_root_text_or_throw(
          root_path_, "sync replica file-effect root path")),
#if !defined(_WIN32)
      root_authority_(SyncDirectoryAuthority::open_or_throw(
          root_path_, "sync replica file-effect root authority")),
      root_authority_digest_(sync_directory_attestation_digest_or_throw(
          root_authority_.attestation())),
#else
      root_authority_digest_(sha256_hex(
          std::string("anonsync-windows-file-effect-root-path-v1:") +
          root_path_text_)),
#endif
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica file-effect SQLite owner label must not be empty");
    }
    sqlite_exec_or_throw(
        db_, "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;",
        label_ + " connection hardening");
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " schema initialization root authority");
#endif
    SyncSqliteTransaction transaction(
        db_, label_ + " schema initialization",
        SyncSqliteTransactionMode::Immediate);
    const auto observed = read_schema_or_throw(db_, label_);
    if (observed.empty()) {
        validate_limits_or_throw(folder_id_, initial_limits, label_);
        for (const SchemaDefinition& definition : kSchema) {
            sqlite_exec_or_throw(
                db_, create_statement(definition),
                label_ + " create " + std::string(definition.name));
        }
        verify_schema_or_throw(db_, kSchema, label_);
        insert_initial_meta_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            initial_limits, label_);
        (void)load_state_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " initial cutpoint attestation",
            SnapshotProjection::AuthorityOnly);
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " schema initialization pre-commit root authority");
#endif
        transaction.commit();
    } else if (schema_matches(observed, kSchema)) {
        (void)load_state_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " existing database",
            SnapshotProjection::AuthorityOnly);
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " existing database pre-commit root authority");
#endif
        transaction.commit();
    } else if (schema_matches(observed, kLegacySchema)) {
        // The two new device-isolation fields are the only caller policy
        // imported into an existing v2 database. Every v2 field is restored
        // and re-attested from durable metadata before any DDL occurs.
        validate_device_limits_or_throw(
            initial_limits, label_ + " migration policy");
        LoadedState legacy = load_legacy_state_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " legacy database",
            SnapshotProjection::AuthorityOnly);
        SyncReplicaFileEffectSqliteOwnerLimits migrated_limits =
            legacy.snapshot.limits;
        migrated_limits.max_effects_per_device =
            initial_limits.max_effects_per_device;
        migrated_limits.max_retained_payload_bytes_per_device =
            initial_limits.max_retained_payload_bytes_per_device;
        validate_limits_or_throw(
            folder_id_, migrated_limits, label_ + " migrated limits");

        sqlite_exec_or_throw(
            db_, "DROP TABLE main.sync_replica_file_effect_meta;",
            label_ + " drop legacy metadata");
        sqlite_exec_or_throw(
            db_, create_statement(kSchema.front()),
            label_ + " create v3 metadata");
        insert_meta_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            migrated_limits, legacy.snapshot.state_generation, legacy.stored,
            label_ + " migrated");
        verify_schema_or_throw(db_, kSchema, label_ + " migrated schema");
        const LoadedState migrated = load_state_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " migrated database",
            SnapshotProjection::AuthorityOnly);
        if (migrated.stored != legacy.stored ||
            migrated.snapshot.state_generation !=
                legacy.snapshot.state_generation ||
            migrated.snapshot.limits != migrated_limits) {
            throw std::runtime_error(
                label_ +
                " v2-to-v3 migration changed retained effect authority");
        }
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " migrated database pre-commit root authority");
#endif
        transaction.commit();
    } else {
        throw std::runtime_error(
            label_ +
            " database does not match exact file-effect schema v2 or v3");
    }
    (void)snapshot_or_throw();
}

SyncReplicaFileEffectSqliteSnapshot
SyncReplicaFileEffectSqliteOwner::snapshot_or_throw() {
#if !defined(_WIN32)
    root_authority_.verify_or_throw(label_ + " snapshot root authority");
#endif
    SyncSqliteTransaction transaction(
        db_, label_ + " snapshot", SyncSqliteTransactionMode::Deferred);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, root_path_text_, root_authority_digest_,
        label_ + " snapshot", SnapshotProjection::PublicSnapshot);
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " snapshot pre-commit root authority");
#endif
    transaction.commit();
    return std::move(loaded.snapshot);
}

SyncReplicaFileEffectSqliteIdentityCutpoint
SyncReplicaFileEffectSqliteOwner::identity_cutpoint_or_throw() {
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " identity cutpoint root authority");
#endif
    SyncSqliteTransaction transaction(
        db_, label_ + " identity cutpoint",
        SyncSqliteTransactionMode::Deferred);
    SyncReplicaFileEffectSqliteIdentityCutpoint cutpoint =
        load_identity_cutpoint_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " identity cutpoint");
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " identity cutpoint pre-commit root authority");
#endif
    transaction.commit();
    return cutpoint;
}

SyncReplicaFileEffectStageResult
SyncReplicaFileEffectSqliteOwner::stage_or_throw(
    const SyncReplicaOperation& operation,
    std::span<const unsigned char> payload_bytes) {
    return stage_with_diagnostics_or_throw(operation, payload_bytes).result;
}

SyncReplicaFileEffectStageOutcome
SyncReplicaFileEffectSqliteOwner::stage_with_diagnostics_or_throw(
    const SyncReplicaOperation& operation,
    std::span<const unsigned char> payload_bytes) {
#if !defined(_WIN32)
    root_authority_.verify_or_throw(label_ + " stage root authority");
#endif
    SyncSqliteTransaction transaction(
        db_, label_ + " stage", SyncSqliteTransactionMode::Immediate);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, root_path_text_, root_authority_digest_,
        label_ + " stage", SnapshotProjection::AuthorityOnly);
    const auto& limits = loaded.snapshot.limits;
    validate_sync_replica_operation_or_throw(operation, limits.model);
    if (operation.folder_id != folder_id_) {
        throw std::invalid_argument(
            label_ + " stage operation belongs to another folder");
    }
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            label_ + " stage supports file operations only");
    }
    if (payload_bytes.size() >
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::invalid_argument(
            label_ + " stage payload size exceeds uint64 authority");
    }
    const auto payload_size =
        static_cast<std::uint64_t>(payload_bytes.size());
    if (payload_size > limits.max_payload_bytes ||
        operation.size_bytes != payload_size) {
        throw std::invalid_argument(
            label_ + " stage payload size does not match operation");
    }
    if (sha256_payload_span(payload_bytes) != operation.content_sha256) {
        throw std::invalid_argument(
            label_ + " stage payload digest does not match operation");
    }

#if !defined(_WIN32)
    if (destination_path_is_blocked(operation, root_authority_)) {
        root_authority_.verify_or_throw(
            label_ + " path-blocked stage pre-commit root authority");
        transaction.commit();
        return {SyncReplicaFileEffectStageResult::DestinationPathBlocked,
                std::nullopt};
    }
#endif

    auto found = find_effect(loaded.stored, operation.operation_id);
    if (found != loaded.stored.end() &&
        found->record.operation.operation_id == operation.operation_id) {
        // Both retained and incoming operations have independently passed the
        // exact canonical codec/ID validator. Structural equality therefore
        // implies identical canonical bytes without allocating a second
        // canonical envelope on every retry.
        if (found->record.operation != operation ||
            std::string_view(found->payload) !=
                payload_view_from_span(payload_bytes)) {
            throw std::runtime_error(
                label_ + " stage operation identity maps to different effect bytes");
        }
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " duplicate stage pre-commit root authority");
#endif
        transaction.commit();
        return {SyncReplicaFileEffectStageResult::Duplicate, std::nullopt};
    }

    const auto actor = std::lower_bound(
        loaded.snapshot.actor_usage.begin(),
        loaded.snapshot.actor_usage.end(), operation.dot.actor,
        [](const SyncReplicaFileEffectActorUsage& usage,
           const SyncReplicaActor& candidate) {
            return usage.actor < candidate;
        });
    SyncReplicaFileEffectActorUsage actor_usage;
    if (actor != loaded.snapshot.actor_usage.end() &&
        actor->actor == operation.dot.actor) {
        actor_usage = *actor;
    } else {
        actor_usage.actor = operation.dot.actor;
    }
    const auto device = std::lower_bound(
        loaded.snapshot.device_usage.begin(),
        loaded.snapshot.device_usage.end(), operation.dot.actor.device_id,
        [](const SyncReplicaFileEffectDeviceUsage& usage,
           const std::string& candidate) {
            return usage.device_id < candidate;
        });
    SyncReplicaFileEffectDeviceUsage device_usage;
    if (device != loaded.snapshot.device_usage.end() &&
        device->device_id == operation.dot.actor.device_id) {
        device_usage = *device;
    } else {
        device_usage.device_id = operation.dot.actor.device_id;
    }

    const SyncReplicaResourceBudget effect_budget{
        static_cast<std::uint64_t>(loaded.stored.size()), 1U,
        limits.max_effects};
    const SyncReplicaResourceBudget payload_budget{
        loaded.snapshot.retained_payload_bytes, payload_size,
        limits.max_retained_payload_bytes};
    const SyncReplicaResourceBudget device_effect_budget{
        device_usage.retained_effects, 1U,
        limits.max_effects_per_device};
    const SyncReplicaResourceBudget device_payload_budget{
        device_usage.retained_payload_bytes, payload_size,
        limits.max_retained_payload_bytes_per_device};

    SyncReplicaFileEffectCapacityConstraint constraint =
        SyncReplicaFileEffectCapacityConstraint::None;
    if (effect_budget.would_exceed()) {
        constraint =
            SyncReplicaFileEffectCapacityConstraint::FolderEffectCount;
    } else if (payload_budget.would_exceed()) {
        constraint = SyncReplicaFileEffectCapacityConstraint::
            FolderRetainedPayloadBytes;
    } else if (device_effect_budget.would_exceed()) {
        constraint =
            SyncReplicaFileEffectCapacityConstraint::DeviceEffectCount;
    } else if (device_payload_budget.would_exceed()) {
        constraint = SyncReplicaFileEffectCapacityConstraint::
            DeviceRetainedPayloadBytes;
    }
    if (constraint != SyncReplicaFileEffectCapacityConstraint::None) {
        SyncReplicaFileEffectCapacityBlock block;
        block.state_generation = loaded.snapshot.state_generation;
        block.cutpoint_digest = loaded.snapshot.cutpoint_digest;
        block.constraint = constraint;
        block.effects = effect_budget;
        block.retained_payload_bytes = payload_budget;
        block.device_effects = device_effect_budget;
        block.device_retained_payload_bytes = device_payload_budget;
        block.actor_usage = std::move(actor_usage);
        block.device_usage = std::move(device_usage);
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " capacity stage pre-commit root authority");
#endif
        transaction.commit();
        return {SyncReplicaFileEffectStageResult::CapacityBlocked,
                std::move(block)};
    }

    // The retained-row payload copy and the second canonical encoding occur
    // only after path, duplicate, and capacity policy authorize a new row.
    // The shared operation validator above still constructs one bounded
    // canonical envelope to prove operation_id on every path.
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " stage mutation root authority");
#endif
    checked_increment_or_throw(
        loaded.snapshot.state_generation, label_ + " stage");
    StoredEffect inserted;
    inserted.record.effect_id =
        make_sync_replica_file_effect_id_or_throw(operation);
    inserted.record.operation = operation;
    inserted.record.state = SyncReplicaFileEffectState::Staged;
    inserted.record.staged_generation = loaded.snapshot.state_generation;
    inserted.canonical_operation =
        encode_sync_replica_operation_canonical_or_throw(
            operation, limits.model);
    inserted.payload = payload_from_span(payload_bytes);
    found = loaded.stored.insert(found, std::move(inserted));
    insert_effect_or_throw(db_, *found, label_ + " stage");
    update_meta_or_throw(
        db_, loaded, root_path_text_, root_authority_digest_,
        label_ + " stage");

    const LoadedState attested = load_state_or_throw(
        db_, folder_id_, root_path_text_, root_authority_digest_,
        label_ + " staged cutpoint", SnapshotProjection::AuthorityOnly);
    if (attested.stored != loaded.stored ||
        attested.snapshot.state_generation !=
            loaded.snapshot.state_generation) {
        throw std::runtime_error(
            label_ + " staged cutpoint differs from intended effect state");
    }
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " staged cutpoint pre-commit root authority");
#endif
    transaction.commit();
    return {SyncReplicaFileEffectStageResult::Inserted, std::nullopt};
}

SyncReplicaFileEffectMaterializeResult
SyncReplicaFileEffectSqliteOwner::materialize_or_throw(
    const std::string& operation_id) {
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " materialize root authority");
#endif
    StoredEffect effect;
    {
        SyncSqliteTransaction transaction(
            db_, label_ + " materialize read",
            SyncSqliteTransactionMode::Deferred);
        LoadedState loaded = load_state_or_throw(
            db_, folder_id_, root_path_text_, root_authority_digest_,
            label_ + " materialize read", SnapshotProjection::AuthorityOnly);
        const auto found = find_effect(loaded.stored, operation_id);
        if (found == loaded.stored.end() ||
            found->record.operation.operation_id != operation_id) {
            throw std::invalid_argument(
                label_ + " materialize operation is not staged");
        }
        effect = *found;
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " materialize read pre-commit root authority");
#endif
        transaction.commit();
    }

    const fs::path relative_destination =
        canonical_relative_effect_path_or_throw(
            effect.record.operation,
            label_ + " materialize destination");
#if defined(_WIN32)
    const fs::path destination = destination_path_or_throw(
        root_path_, relative_destination,
        label_ + " materialize destination");
#endif
    const auto reconcile_effect =
        [&](const std::string& proof_label) {
#if !defined(_WIN32)
            return reconcile_sync_immutable_file_create_new_under_directory_or_throw(
                root_authority_, relative_destination,
                byte_span(effect.payload), proof_label);
#else
            return reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
                destination, byte_span(effect.payload), proof_label);
#endif
        };
    const auto publish_effect =
        [&](const std::string& publication_label) {
#if !defined(_WIN32)
            write_sync_file_atomically_create_new_under_directory_or_throw(
                root_authority_, relative_destination,
                byte_span(effect.payload), publication_label);
#else
            write_sync_file_atomically_create_new_no_symlink_or_throw(
                destination, byte_span(effect.payload), publication_label);
#endif
        };

    SyncImmutableFileReconciliationOutcome reconciliation =
        reconcile_effect(label_ + " materialize reconciliation");

    if (effect.record.state == SyncReplicaFileEffectState::Published) {
        require_published_file_exact_or_throw(
            reconciliation, label_ + " materialize");
        return SyncReplicaFileEffectMaterializeResult::AlreadyPublished;
    }
    if (reconciliation ==
        SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        return SyncReplicaFileEffectMaterializeResult::DestinationConflict;
    }
    if (reconciliation == SyncImmutableFileReconciliationOutcome::Absent) {
        try {
            publish_effect(label_ + " materialize publication");
        } catch (const SyncAtomicFilePublicationError&) {
            // The create-new attempt may have published before its exception,
            // or a concurrent exact writer may have won. Only exact durable
            // reconciliation under the retained root can convert either
            // ambiguity into effect authority.
            reconciliation = reconcile_effect(
                label_ + " materialize publication recovery");
            if (reconciliation ==
                SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
                return SyncReplicaFileEffectMaterializeResult::
                    DestinationConflict;
            }
            if (reconciliation ==
                SyncImmutableFileReconciliationOutcome::Absent) {
                throw;
            }
        }
    }

    require_published_file_exact_or_throw(
        reconcile_effect(label_ + " materialize terminal proof"),
        label_ + " materialize terminal proof");

#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " publication mark root authority");
#endif
    SyncSqliteTransaction transaction(
        db_, label_ + " publication mark",
        SyncSqliteTransactionMode::Immediate);
    LoadedState loaded = load_state_or_throw(
        db_, folder_id_, root_path_text_, root_authority_digest_,
        label_ + " publication mark", SnapshotProjection::AuthorityOnly);
    auto found = find_effect(loaded.stored, operation_id);
    if (found == loaded.stored.end() ||
        found->record.operation.operation_id != operation_id) {
        throw std::runtime_error(
            label_ + " staged effect disappeared before publication mark");
    }
    if (found->canonical_operation != effect.canonical_operation ||
        found->payload != effect.payload ||
        found->record.effect_id != effect.record.effect_id) {
        throw std::runtime_error(
            label_ + " staged effect changed before publication mark");
    }
    if (found->record.state == SyncReplicaFileEffectState::Published) {
#if !defined(_WIN32)
        root_authority_.verify_or_throw(
            label_ + " concurrent mark pre-commit root authority");
#endif
        transaction.commit();

        // Another owner may have committed the Published transition after
        // this call's pre-transaction namespace proof. Re-prove the exact
        // immutable file after observing that independent durable cutpoint;
        // otherwise a concurrently removed or replaced file could receive a
        // terminal AlreadyPublished receipt from stale evidence.
        require_published_file_exact_or_throw(
            reconcile_effect(
                label_ + " post-concurrent-mark terminal proof"),
            label_ + " post-concurrent-mark terminal proof");
        return SyncReplicaFileEffectMaterializeResult::AlreadyPublished;
    }

#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " publication mark mutation root authority");
#endif
    checked_increment_or_throw(
        loaded.snapshot.state_generation, label_ + " publication mark");
    found->record.state = SyncReplicaFileEffectState::Published;
    found->record.published_generation = loaded.snapshot.state_generation;
    found->record.publication_digest = publication_digest_or_throw(
        root_path_text_, root_authority_digest_, found->record.operation,
        found->record.effect_id);
    mark_effect_published_or_throw(
        db_, *found, label_ + " publication mark");
    update_meta_or_throw(
        db_, loaded, root_path_text_, root_authority_digest_,
        label_ + " publication mark");

    const LoadedState attested = load_state_or_throw(
        db_, folder_id_, root_path_text_, root_authority_digest_,
        label_ + " published cutpoint", SnapshotProjection::AuthorityOnly);
    if (attested.stored != loaded.stored ||
        attested.snapshot.state_generation !=
            loaded.snapshot.state_generation) {
        throw std::runtime_error(
            label_ + " published cutpoint differs from intended effect state");
    }
#if !defined(_WIN32)
    root_authority_.verify_or_throw(
        label_ + " published cutpoint pre-commit root authority");
#endif
    transaction.commit();

    // The namespace proof that preceded the database transition cannot also
    // prove the file remained exact through that independent commit. Re-prove
    // the immutable effect after the Published mark is durable; a crash before
    // this proof is recovered by the Published branch on retry, while any
    // contradiction fails closed before a terminal receipt can be emitted.
    require_published_file_exact_or_throw(
        reconcile_effect(label_ + " post-mark terminal proof"),
        label_ + " post-mark terminal proof");
    return SyncReplicaFileEffectMaterializeResult::Published;
}

}  // namespace anonsync
