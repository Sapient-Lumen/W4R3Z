#include "sync_replica_deployment_manifest.hpp"

#include "anonsync_json_parser.hpp"
#include "sha256_digest.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_manifest_validation.hpp"

#include <array>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::string_view kFormat =
    "anonsync-replica-deployment-manifest-v2";
constexpr std::string_view kDigestDomain =
    "anonsync:replica-deployment-manifest:v2\n";
constexpr std::uint64_t kMaximumExactJsonInteger = 9007199254740991ULL;
constexpr std::array<std::string_view, 3> kSqliteSidecarSuffixes{
    "-journal",
    "-wal",
    "-shm",
};

constexpr std::array<std::string_view, 26> kExactFields{
    "format",
    "deployment_id",
    "profile",
    "folder_id",
    "local_device_id",
    "local_epoch",
    "max_payload_bytes",
    "manifest_path",
    "replica_db",
    "payload_root",
    "effect_db",
    "files_root",
    "membership_db",
    "anchor_db",
    "authority_resource_count",
    "sqlite_journal_mode",
    "sqlite_application_id_policy",
    "store_internal_deployment_binding",
    "bootstrap_store_adoption_policy",
    "operational_database_open_policy",
    "operational_payload_open_policy",
    "operational_configuration_source",
    "operational_manifest_required",
    "manifest_is_store_set_commit_marker",
    "cross_resource_atomicity",
    "manifest_digest",
};

[[nodiscard]] std::string quote_json(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

void append_optional_path_json(
    std::ostream& output,
    const std::optional<fs::path>& path) {
    if (path.has_value()) {
        output << quote_json(path->generic_string());
    } else {
        output << "null";
    }
}

[[nodiscard]] bool path_is_same_or_descendant(
    const fs::path& candidate,
    const fs::path& root) {
    const fs::path normalized_candidate = candidate.lexically_normal();
    const fs::path normalized_root = root.lexically_normal();
    auto candidate_part = normalized_candidate.begin();
    for (auto root_part = normalized_root.begin();
         root_part != normalized_root.end(); ++root_part, ++candidate_part) {
        if (candidate_part == normalized_candidate.end() ||
            *candidate_part != *root_part) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] fs::path append_ascii_path_suffix(
    const fs::path& path,
    std::string_view suffix) {
    fs::path::string_type native = path.native();
    for (const char byte : suffix) {
        native.push_back(static_cast<fs::path::value_type>(byte));
    }
    return fs::path(std::move(native));
}

void require_canonical_absolute_path(
    const fs::path& path,
    std::string_view field,
    const std::string& label) {
    if (path.native().find(fs::path::value_type{}) !=
        fs::path::string_type::npos) {
        throw std::invalid_argument(
            label + " field " + std::string(field) +
            " must not contain NUL");
    }
    if (path.empty() || !path.is_absolute()) {
        throw std::invalid_argument(
            label + " field " + std::string(field) +
            " must be an absolute path");
    }
    if (path.lexically_normal() != path) {
        throw std::invalid_argument(
            label + " field " + std::string(field) +
            " must be lexically normalized");
    }
}

void require_disjoint_paths(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label) {
    using NamedPath = std::pair<std::string, fs::path>;

    std::vector<NamedPath> files{
        {"manifest_path", manifest.manifest_path},
        {"replica_db", manifest.replica_db},
    };
    std::vector<NamedPath> sqlite_databases{
        {"replica_db", manifest.replica_db},
    };
    if (manifest.effect_db.has_value()) {
        files.emplace_back("effect_db", *manifest.effect_db);
        sqlite_databases.emplace_back("effect_db", *manifest.effect_db);
    }
    if (manifest.membership_db.has_value()) {
        files.emplace_back("membership_db", *manifest.membership_db);
        files.emplace_back("anchor_db", *manifest.anchor_db);
        sqlite_databases.emplace_back(
            "membership_db", *manifest.membership_db);
        sqlite_databases.emplace_back("anchor_db", *manifest.anchor_db);
    }

    std::map<fs::path, std::string> exact_paths;
    for (const auto& [field, path] : files) {
        const auto [found, inserted] = exact_paths.emplace(path, field);
        if (!inserted) {
            throw std::invalid_argument(
                label + " fields " + field + " and " + found->second +
                " must not name the same file path");
        }
    }

    // A SQLite database owns not just its main pathname but the exact rollback
    // journal and WAL/SHM names SQLite derives by appending fixed suffixes. A
    // second selected store, the manifest, or a mutable root must not occupy
    // any member of that family. Otherwise one authority can be mistaken for,
    // overwritten as, or unlinked as another database's live sidecar.
    std::vector<NamedPath> authority_paths = files;
    for (const auto& [field, database] : sqlite_databases) {
        for (const std::string_view suffix : kSqliteSidecarSuffixes) {
            authority_paths.emplace_back(
                field + " SQLite sidecar " + std::string(suffix),
                append_ascii_path_suffix(database, suffix));
        }
    }
    std::map<fs::path, std::string> authority_namespace;
    for (const auto& [field, path] : authority_paths) {
        const auto [found, inserted] = authority_namespace.emplace(path, field);
        if (!inserted) {
            throw std::invalid_argument(
                label + " authority paths " + field + " and " +
                found->second +
                " collide in a SQLite main/sidecar path family");
        }
    }

    std::vector<NamedPath> roots;
    if (manifest.payload_root.has_value()) {
        roots.emplace_back("payload_root", *manifest.payload_root);
    }
    if (manifest.files_root.has_value()) {
        roots.emplace_back("files_root", *manifest.files_root);
    }
    if (roots.size() == 2U &&
        (path_is_same_or_descendant(roots[0].second, roots[1].second) ||
         path_is_same_or_descendant(roots[1].second, roots[0].second))) {
        throw std::invalid_argument(
            label + " fields payload_root and files_root must not overlap");
    }
    for (const auto& [authority_field, authority_path] : authority_paths) {
        for (const auto& [root_field, root] : roots) {
            if (path_is_same_or_descendant(authority_path, root)) {
                throw std::invalid_argument(
                    label + " authority path " + authority_field +
                    " must not be inside " + root_field);
            }
            if (path_is_same_or_descendant(root, authority_path)) {
                throw std::invalid_argument(
                    label + " field " + root_field +
                    " must not be inside authority path " + authority_field);
            }
        }
    }
}

[[nodiscard]] const Json& require_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const auto found = root.o.find(std::string(field));
    if (found == root.o.end()) {
        throw std::runtime_error(
            label + " is missing field " + std::string(field));
    }
    return found->second;
}

[[nodiscard]] std::string require_string_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const Json& value = require_field(root, field, label);
    if (!value.is_string()) {
        throw std::runtime_error(
            label + " field " + std::string(field) + " must be a string");
    }
    return value.s;
}

[[nodiscard]] bool require_bool_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const Json& value = require_field(root, field, label);
    if (!value.is_bool()) {
        throw std::runtime_error(
            label + " field " + std::string(field) + " must be a boolean");
    }
    return value.b;
}

[[nodiscard]] std::uint64_t require_uint64_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const Json& value = require_field(root, field, label);
    if (!value.is_number()) {
        throw std::runtime_error(
            label + " field " + std::string(field) + " must be a number");
    }
    const long long parsed = value.integer();
    if (parsed < 0) {
        throw std::runtime_error(
            label + " field " + std::string(field) +
            " must be an unsigned integer");
    }
    return static_cast<std::uint64_t>(parsed);
}

[[nodiscard]] fs::path require_path_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const fs::path path(require_string_field(root, field, label));
    require_canonical_absolute_path(path, field, label);
    return path;
}

[[nodiscard]] std::optional<fs::path> require_optional_path_field(
    const Json& root,
    std::string_view field,
    const std::string& label) {
    const Json& value = require_field(root, field, label);
    if (value.is_null()) return std::nullopt;
    if (!value.is_string()) {
        throw std::runtime_error(
            label + " field " + std::string(field) +
            " must be null or a string");
    }
    const fs::path path(value.s);
    require_canonical_absolute_path(path, field, label);
    return path;
}

void require_exact_fields(const Json& root, const std::string& label) {
    if (!root.is_object()) {
        throw std::runtime_error(label + " must be one JSON object");
    }
    std::set<std::string> expected;
    for (const std::string_view field : kExactFields) {
        expected.emplace(field);
    }
    for (const auto& [field, ignored] : root.o) {
        (void)ignored;
        if (!expected.contains(field)) {
            throw std::runtime_error(
                label + " contains unknown field " + field);
        }
    }
    for (const std::string& field : expected) {
        if (!root.o.contains(field)) {
            throw std::runtime_error(label + " is missing field " + field);
        }
    }
}

[[nodiscard]] bool lowercase_sha256(std::string_view value) noexcept {
    if (value.size() != 64U) return false;
    for (const char byte : value) {
        if (!((byte >= '0' && byte <= '9') ||
              (byte >= 'a' && byte <= 'f'))) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] std::string canonical_unsigned_document(
    const SyncReplicaDeploymentManifest& manifest) {
    std::ostringstream unsigned_document;
    unsigned_document
        << "{\"format\":" << quote_json(kFormat)
        << ",\"deployment_id\":" << quote_json(manifest.deployment_id)
        << ",\"profile\":"
        << quote_json(sync_replica_deployment_profile_name(manifest))
        << ",\"folder_id\":" << quote_json(manifest.folder_id)
        << ",\"local_device_id\":"
        << quote_json(manifest.local_actor.device_id)
        << ",\"local_epoch\":" << manifest.local_actor.epoch
        << ",\"max_payload_bytes\":" << manifest.max_payload_bytes
        << ",\"manifest_path\":"
        << quote_json(manifest.manifest_path.generic_string())
        << ",\"replica_db\":"
        << quote_json(manifest.replica_db.generic_string())
        << ",\"payload_root\":";
    append_optional_path_json(unsigned_document, manifest.payload_root);
    unsigned_document << ",\"effect_db\":";
    append_optional_path_json(unsigned_document, manifest.effect_db);
    unsigned_document << ",\"files_root\":";
    append_optional_path_json(unsigned_document, manifest.files_root);
    unsigned_document << ",\"membership_db\":";
    append_optional_path_json(unsigned_document, manifest.membership_db);
    unsigned_document << ",\"anchor_db\":";
    append_optional_path_json(unsigned_document, manifest.anchor_db);
    unsigned_document
        << ",\"authority_resource_count\":"
        << sync_replica_deployment_authority_resource_count(manifest)
        << ",\"sqlite_journal_mode\":\"wal\""
        << ",\"sqlite_application_id_policy\":\"role-specific-v1\""
        << ",\"store_internal_deployment_binding\":\"required-v1\""
        << ",\"bootstrap_store_adoption_policy\":\"fresh-only-v1\""
        << ",\"operational_database_open_policy\":\"existing-only\""
        << ",\"operational_payload_open_policy\":\"existing-only\""
        << ",\"operational_configuration_source\":\"deployment-manifest\""
        << ",\"operational_manifest_required\":true"
        << ",\"manifest_is_store_set_commit_marker\":true"
        << ",\"cross_resource_atomicity\":false}";
    return unsigned_document.str();
}

}  // namespace

const char* sync_replica_deployment_profile_name(
    const SyncReplicaDeploymentManifest& manifest) noexcept {
    const bool payload = manifest.payload_root.has_value();
    const bool effect = manifest.effect_db.has_value();
    const bool membership = manifest.membership_db.has_value();
    if (payload && !effect && !membership) return "sender";
    if (!payload && effect && membership) return "receiver";
    if (payload && effect && membership) return "combined";
    if (!payload && !effect && !membership) return "replica-only";
    return "custom";
}

std::uint64_t sync_replica_deployment_authority_resource_count(
    const SyncReplicaDeploymentManifest& manifest) noexcept {
    std::uint64_t count = 1U;
    if (manifest.payload_root.has_value()) ++count;
    if (manifest.effect_db.has_value()) count += 2U;
    if (manifest.membership_db.has_value()) count += 2U;
    return count;
}

void validate_sync_replica_deployment_manifest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "deployment manifest validation label must not be empty");
    }
    if (!sync_replica_deployment_id_is_valid(manifest.deployment_id)) {
        throw std::invalid_argument(
            label + " deployment_id must be 64 lowercase hexadecimal characters");
    }
    if (!manifest.manifest_digest.empty() &&
        !is_lowercase_sha256_hex(manifest.manifest_digest)) {
        throw std::invalid_argument(
            label + " manifest_digest must be lowercase SHA-256 when populated");
    }
    require_canonical_absolute_path(
        manifest.manifest_path, "manifest_path", label);
    require_canonical_absolute_path(manifest.replica_db, "replica_db", label);
    if (manifest.payload_root.has_value()) {
        require_canonical_absolute_path(
            *manifest.payload_root, "payload_root", label);
    }
    if (manifest.effect_db.has_value() != manifest.files_root.has_value()) {
        throw std::invalid_argument(
            label + " effect_db and files_root must be selected together");
    }
    if (manifest.effect_db.has_value()) {
        require_canonical_absolute_path(*manifest.effect_db, "effect_db", label);
        require_canonical_absolute_path(*manifest.files_root, "files_root", label);
    }
    if (manifest.membership_db.has_value() != manifest.anchor_db.has_value()) {
        throw std::invalid_argument(
            label + " membership_db and anchor_db must be selected together");
    }
    if (manifest.membership_db.has_value()) {
        require_canonical_absolute_path(
            *manifest.membership_db, "membership_db", label);
        require_canonical_absolute_path(*manifest.anchor_db, "anchor_db", label);
    }
    if (!sync_id_is_valid(manifest.folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync ID");
    }
    if (!sync_id_is_valid(manifest.local_actor.device_id) ||
        manifest.local_actor.epoch == 0U ||
        manifest.local_actor.epoch > kMaximumExactJsonInteger) {
        throw std::invalid_argument(
            label + " local actor is invalid or exceeds exact JSON integer "
            "range");
    }
    if (manifest.max_payload_bytes == 0U ||
        manifest.max_payload_bytes >
            kSyncReplicaDeploymentManifestMaxPayloadBytes) {
        throw std::invalid_argument(
            label + " max_payload_bytes must be in [1, " +
            std::to_string(kSyncReplicaDeploymentManifestMaxPayloadBytes) +
            "]");
    }
    require_disjoint_paths(manifest, label);
}

std::string compute_sync_replica_deployment_manifest_digest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label) {
    validate_sync_replica_deployment_manifest_or_throw(manifest, label);
    const std::string digest = sha256_hex(
        std::string(kDigestDomain) + canonical_unsigned_document(manifest));
    if (!manifest.manifest_digest.empty() &&
        manifest.manifest_digest != digest) {
        throw std::invalid_argument(
            label + " manifest_digest conflicts with the canonical manifest");
    }
    return digest;
}

SyncReplicaDeploymentIdentity sync_replica_deployment_identity_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label) {
    const std::string digest =
        compute_sync_replica_deployment_manifest_digest_or_throw(
            manifest, label + " digest");
    if (manifest.manifest_digest.empty()) {
        throw std::invalid_argument(
            label + " manifest_digest must be populated before deriving "
                    "deployment identity");
    }
    SyncReplicaDeploymentIdentity identity{
        .deployment_id = manifest.deployment_id,
        .manifest_digest = digest,
        .manifest_path = manifest.manifest_path,
        .folder_id = manifest.folder_id,
        .local_actor = manifest.local_actor,
    };
    validate_sync_replica_deployment_identity_or_throw(identity, label);
    return identity;
}

std::string encode_sync_replica_deployment_manifest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label) {
    const std::string unsigned_json = canonical_unsigned_document(manifest);
    const std::string digest =
        compute_sync_replica_deployment_manifest_digest_or_throw(
            manifest, label);
    if (unsigned_json.empty() || unsigned_json.back() != '}') {
        throw std::logic_error(
            label + " canonical unsigned manifest is structurally invalid");
    }
    const std::string encoded =
        unsigned_json.substr(0U, unsigned_json.size() - 1U) +
        ",\"manifest_digest\":" + quote_json(digest) + "}\n";
    if (encoded.size() > kSyncReplicaDeploymentManifestMaxBytes) {
        throw std::invalid_argument(
            label + " encoded bytes exceed the deployment-manifest read "
            "ceiling");
    }
    // Programmatic paths can contain byte sequences that the platform accepts
    // but strict JSON does not. Prove the exact publication bytes parse before
    // init is allowed to create any selected authority store. This also keeps
    // the writer and operational reader on one syntax/Unicode contract.
    try {
        if (!parse_json_text(encoded).is_object()) {
            throw std::runtime_error("encoded value is not an object");
        }
    } catch (const std::exception& error) {
        throw std::invalid_argument(
            label + " cannot be encoded as strict UTF-8 JSON: " +
            error.what());
    }
    return encoded;
}

SyncReplicaDeploymentManifest decode_sync_replica_deployment_manifest_or_throw(
    std::string_view exact,
    const fs::path& expected_absolute_manifest_path,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "deployment manifest decode label must not be empty");
    }
    require_canonical_absolute_path(
        expected_absolute_manifest_path, "manifest_path", label);
    if (exact.size() > kSyncReplicaDeploymentManifestMaxBytes) {
        throw std::runtime_error(
            label + " exact bytes exceed the deployment-manifest read ceiling");
    }
    const std::string exact_bytes(exact);

    Json root;
    try {
        root = parse_json_text(exact_bytes);
    } catch (const std::exception& error) {
        throw std::runtime_error(
            label + " JSON parse failed: " + error.what());
    }
    require_exact_fields(root, label);

    SyncReplicaDeploymentManifest manifest;
    const std::string format = require_string_field(root, "format", label);
    if (format != kFormat) {
        throw std::runtime_error(label + " format is unsupported");
    }
    manifest.deployment_id =
        require_string_field(root, "deployment_id", label);
    manifest.folder_id = require_string_field(root, "folder_id", label);
    manifest.local_actor.device_id =
        require_string_field(root, "local_device_id", label);
    manifest.local_actor.epoch =
        require_uint64_field(root, "local_epoch", label);
    manifest.max_payload_bytes =
        require_uint64_field(root, "max_payload_bytes", label);
    manifest.manifest_path =
        require_path_field(root, "manifest_path", label);
    manifest.replica_db = require_path_field(root, "replica_db", label);
    manifest.payload_root =
        require_optional_path_field(root, "payload_root", label);
    manifest.effect_db =
        require_optional_path_field(root, "effect_db", label);
    manifest.files_root =
        require_optional_path_field(root, "files_root", label);
    manifest.membership_db =
        require_optional_path_field(root, "membership_db", label);
    manifest.anchor_db =
        require_optional_path_field(root, "anchor_db", label);
    manifest.manifest_digest =
        require_string_field(root, "manifest_digest", label);

    validate_sync_replica_deployment_manifest_or_throw(manifest, label);
    if (manifest.manifest_path != expected_absolute_manifest_path) {
        throw std::runtime_error(
            label + " manifest_path does not bind the expected final file name");
    }
    if (require_string_field(root, "profile", label) !=
        sync_replica_deployment_profile_name(manifest)) {
        throw std::runtime_error(label + " profile conflicts with selected stores");
    }
    if (require_uint64_field(root, "authority_resource_count", label) !=
        sync_replica_deployment_authority_resource_count(manifest)) {
        throw std::runtime_error(
            label + " authority_resource_count conflicts with selected stores");
    }
    if (require_string_field(root, "sqlite_journal_mode", label) != "wal" ||
        require_string_field(
            root, "sqlite_application_id_policy", label) !=
            "role-specific-v1" ||
        require_string_field(
            root, "store_internal_deployment_binding", label) !=
            "required-v1" ||
        require_string_field(
            root, "bootstrap_store_adoption_policy", label) !=
            "fresh-only-v1" ||
        require_string_field(
            root, "operational_database_open_policy", label) !=
            "existing-only" ||
        require_string_field(
            root, "operational_payload_open_policy", label) !=
            "existing-only" ||
        require_string_field(
            root, "operational_configuration_source", label) !=
            "deployment-manifest" ||
        !require_bool_field(root, "operational_manifest_required", label) ||
        !require_bool_field(
            root, "manifest_is_store_set_commit_marker", label) ||
        require_bool_field(root, "cross_resource_atomicity", label)) {
        throw std::runtime_error(label + " contains an unsupported authority policy");
    }
    if (!lowercase_sha256(manifest.manifest_digest)) {
        throw std::runtime_error(label + " manifest_digest is not lowercase SHA-256");
    }

    SyncReplicaDeploymentManifest canonical_manifest = manifest;
    canonical_manifest.manifest_digest.clear();
    const std::string canonical =
        encode_sync_replica_deployment_manifest_or_throw(
            canonical_manifest, label);
    if (std::string_view(canonical) != exact) {
        throw std::runtime_error(
            label + " exact bytes, canonical fields, or self-digest conflict");
    }
    return manifest;
}

SyncReplicaDeploymentManifest read_sync_replica_deployment_manifest_or_throw(
    const fs::path& absolute_manifest_path,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "deployment manifest read label must not be empty");
    }
    require_canonical_absolute_path(
        absolute_manifest_path, "manifest_path", label);
    const std::string exact =
        read_sync_bounded_regular_file_no_symlink_or_throw(
            absolute_manifest_path,
            kSyncReplicaDeploymentManifestMaxBytes,
            label + " exact file");
    try {
        return decode_sync_replica_deployment_manifest_or_throw(
            exact, absolute_manifest_path, label);
    } catch (const std::runtime_error& error) {
        constexpr std::string_view kExpected =
            "manifest_path does not bind the expected final file name";
        if (std::string_view(error.what()).find(kExpected) !=
            std::string_view::npos) {
            throw std::runtime_error(
                label + " manifest_path does not bind the opened file name");
        }
        throw;
    }
}

}  // namespace anonsync
