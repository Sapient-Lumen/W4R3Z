#include "sync_local_share_setup.hpp"

#if !defined(_WIN32)

#include "sync_manifest_validation.hpp"
#include "sync_replica_bootstrap_record.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_sibling_process.hpp"

#include <filesystem>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <openssl/err.h>
#include <openssl/rand.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

[[nodiscard]] std::string openssl_errors() {
    std::string output;
    for (unsigned long code = ERR_get_error(); code != 0UL;
         code = ERR_get_error()) {
        char text[256]{};
        ERR_error_string_n(code, text, sizeof(text));
        if (!output.empty()) output += "; ";
        output += text;
    }
    return output.empty() ? "no OpenSSL detail" : output;
}

[[nodiscard]] std::string random_hex_token_or_throw(
    std::size_t byte_count,
    std::string_view label) {
    if (byte_count == 0U ||
        byte_count > static_cast<std::size_t>(
                         std::numeric_limits<int>::max())) {
        throw std::invalid_argument(
            std::string(label) + " random-token size is invalid");
    }
    std::vector<unsigned char> bytes(byte_count);
    ERR_clear_error();
    if (RAND_bytes(bytes.data(), static_cast<int>(bytes.size())) != 1) {
        throw std::runtime_error(
            std::string(label) + " could not generate random bytes: " +
            openssl_errors());
    }
    constexpr std::string_view hex = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(bytes.size() * 2U);
    for (const unsigned char byte : bytes) {
        encoded.push_back(hex[byte >> 4U]);
        encoded.push_back(hex[byte & 0x0fU]);
    }
    return encoded;
}

[[nodiscard]] std::string generated_sync_id_or_throw(
    std::string_view prefix,
    std::string_view label) {
    std::string value(prefix);
    value += random_hex_token_or_throw(16U, label);
    if (!sync_id_is_valid(value)) {
        throw std::logic_error(
            std::string(label) + " generated an invalid sync ID");
    }
    return value;
}

[[nodiscard]] bool regular_file_is_present_or_throw(
    const fs::path& path,
    std::string_view label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error) {
        if (error == std::errc::no_such_file_or_directory) return false;
        throw std::runtime_error(
            std::string(label) + " could not inspect " +
            path.generic_string() + ": " + error.message());
    }
    if (status.type() == fs::file_type::not_found) return false;
    if (fs::is_symlink(status) || !fs::is_regular_file(status)) {
        throw std::runtime_error(
            std::string(label) +
            " must be absent or a non-symlink regular file: " +
            path.generic_string());
    }
    return true;
}

void require_deployment_matches_layout_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const SyncLocalShareUserLayout& layout,
    std::string_view label) {
    const bool exact =
        deployment.manifest_path == layout.manifest_path &&
        deployment.replica_db == layout.replica_database_path &&
        deployment.payload_root == std::optional<fs::path>(layout.payload_root) &&
        deployment.effect_db ==
            std::optional<fs::path>(layout.effect_database_path) &&
        deployment.files_root == std::optional<fs::path>(layout.files_root) &&
        deployment.membership_db ==
            std::optional<fs::path>(layout.membership_database_path) &&
        deployment.anchor_db ==
            std::optional<fs::path>(layout.membership_anchor_database_path);
    if (!exact) {
        throw std::runtime_error(
            std::string(label) +
            " existing deployment does not match the selected local-share layout");
    }
}

void require_optional_identity_matches_or_throw(
    const SyncLocalShareSetupRequest& request,
    const SyncReplicaDeploymentManifest& deployment) {
    if (request.folder_id.has_value() &&
        *request.folder_id != deployment.folder_id) {
        throw std::invalid_argument(
            "requested folder ID conflicts with the existing deployment");
    }
    if (request.local_device_id.has_value() &&
        *request.local_device_id != deployment.local_actor.device_id) {
        throw std::invalid_argument(
            "requested local device ID conflicts with the existing deployment");
    }
    if (request.local_epoch.has_value() &&
        *request.local_epoch != deployment.local_actor.epoch) {
        throw std::invalid_argument(
            "requested local epoch conflicts with the existing deployment");
    }
    if (request.max_payload_bytes.has_value() &&
        *request.max_payload_bytes != deployment.max_payload_bytes) {
        throw std::invalid_argument(
            "requested maximum payload bytes conflicts with the existing deployment");
    }
}

[[nodiscard]] std::uint64_t selected_max_payload_or_throw(
    const SyncLocalShareSetupRequest& request) {
    const std::uint64_t selected = request.max_payload_bytes.value_or(
        kSyncReplicaDeploymentManifestDefaultMaxPayloadBytes);
    if (selected == 0U ||
        selected > kSyncReplicaDeploymentManifestMaxPayloadBytes) {
        throw std::invalid_argument(
            "maximum payload bytes must be in [1, " +
            std::to_string(kSyncReplicaDeploymentManifestMaxPayloadBytes) +
            "]");
    }
    return selected;
}

[[nodiscard]] SyncReplicaFolderConvergencePassLimits
folder_limits_or_throw(
    const SyncLocalShareSetupRequest& request,
    const SyncReplicaDeploymentManifest& deployment) {
    SyncReplicaFolderConvergencePassLimits limits =
        sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            deployment.max_payload_bytes,
            "local share folder convergence limits");
    const auto& selected = request.folder_limit_overrides;
    limits.maximum_entries =
        selected.maximum_entries.value_or(limits.maximum_entries);
    limits.maximum_regular_files = selected.maximum_regular_files.value_or(
        limits.maximum_regular_files);
    limits.maximum_file_bytes =
        selected.maximum_file_bytes.value_or(deployment.max_payload_bytes);
    limits.maximum_total_file_bytes = selected.maximum_total_file_bytes.value_or(
        limits.maximum_total_file_bytes);
    limits.maximum_relative_path_bytes =
        selected.maximum_relative_path_bytes.value_or(
            limits.maximum_relative_path_bytes);
    limits.maximum_directory_depth =
        selected.maximum_directory_depth.value_or(
            limits.maximum_directory_depth);
    limits.maximum_remote_paths =
        selected.maximum_remote_paths.value_or(limits.maximum_remote_paths);
    limits.maximum_remote_inspection_paths =
        selected.maximum_remote_inspection_paths.value_or(
            limits.maximum_remote_inspection_paths);
    if (limits.maximum_file_bytes > deployment.max_payload_bytes) {
        throw std::invalid_argument(
            "maximum file bytes exceeds deployment max_payload_bytes");
    }
    return limits;
}

void append_initial_files_arguments(
    std::vector<std::string>& arguments,
    SyncLocalShareInitialFilesPolicy policy) {
    if (policy == SyncLocalShareInitialFilesPolicy::AdoptExisting) {
        arguments.emplace_back("--initial-files");
        arguments.emplace_back("adopt-existing");
    }
}

}  // namespace

const char* sync_local_share_initial_files_policy_name(
    SyncLocalShareInitialFilesPolicy policy) noexcept {
    switch (policy) {
        case SyncLocalShareInitialFilesPolicy::RequireEmpty:
            return "empty";
        case SyncLocalShareInitialFilesPolicy::AdoptExisting:
            return "adopt_existing";
    }
    return "unknown";
}

const char* sync_local_share_deployment_disposition_name(
    SyncLocalShareDeploymentDisposition disposition) noexcept {
    switch (disposition) {
        case SyncLocalShareDeploymentDisposition::Initialized:
            return "initialized";
        case SyncLocalShareDeploymentDisposition::ResumedExact:
            return "resumed_exact";
    }
    return "unknown";
}

const char* sync_local_share_catalog_disposition_name(
    SyncLocalShareCatalogDisposition disposition) noexcept {
    switch (disposition) {
        case SyncLocalShareCatalogDisposition::Initialized:
            return "initialized";
        case SyncLocalShareCatalogDisposition::ReusedExisting:
            return "reused_existing";
    }
    return "unknown";
}

SyncLocalShareSetupResult create_or_resume_sync_local_share_or_throw(
    SyncLocalShareSetupRequest request,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument("sync local-share setup label is empty");
    }
    if (request.home_directory.empty() ||
        !request.home_directory.is_absolute() ||
        request.home_directory.lexically_normal() != request.home_directory) {
        throw std::invalid_argument(
            label + " home directory must be a normalized absolute path");
    }

    SyncLocalShareSetupResult result;
    result.initial_files_policy = request.initial_files_policy;
    result.layout_preparation = prepare_sync_local_share_user_layout_or_throw(
        request.instance, request.state_directory, request.files_root,
        child_label(label, "layout"));
    const SyncLocalShareUserLayout& layout = result.layout_preparation.layout;

    const fs::path replica_executable =
        resolve_sync_sibling_executable_or_throw(
            "anonsync_replica", child_label(label, "replica executable"));
    const fs::path folder_executable =
        resolve_sync_sibling_executable_or_throw(
            "anonsync_folder", child_label(label, "folder executable"));

    const fs::path bootstrap_record_path =
        sync_replica_bootstrap_record_path_or_throw(
            layout.manifest_path, child_label(label, "bootstrap record"));
    const bool manifest_was_present = regular_file_is_present_or_throw(
        layout.manifest_path, child_label(label, "deployment manifest"));
    const bool record_was_present = regular_file_is_present_or_throw(
        bootstrap_record_path, child_label(label, "bootstrap record"));

    if (manifest_was_present) {
        const SyncReplicaDeploymentManifest existing =
            read_sync_replica_deployment_manifest_or_throw(
                layout.manifest_path,
                child_label(label, "existing deployment preflight"));
        require_deployment_matches_layout_or_throw(existing, layout, label);
        require_optional_identity_matches_or_throw(request, existing);
    }

    if (manifest_was_present || record_was_present) {
        std::vector<std::string> arguments{
            "init-resume", "--manifest", layout.manifest_path.generic_string()};
        // A committed deployment is already a live share. Its ordinary files
        // must never make an idempotent setup replay look like a fresh-folder
        // policy violation. A record-only interrupted bootstrap still obeys the
        // originally selected fresh-folder policy.
        append_initial_files_arguments(
            arguments,
            manifest_was_present
                ? SyncLocalShareInitialFilesPolicy::AdoptExisting
                : request.initial_files_policy);
        (void)run_sync_sibling_process_or_throw(
            replica_executable, arguments,
            kSyncReplicaDeploymentManifestMaxBytes + 4096U,
            child_label(label, "replica resume"));
        result.deployment_disposition =
            SyncLocalShareDeploymentDisposition::ResumedExact;
    } else {
        const std::string folder_id = request.folder_id.value_or(
            generated_sync_id_or_throw(
                "share-", child_label(label, "folder ID")));
        const std::string local_device = request.local_device_id.value_or(
            generated_sync_id_or_throw(
                "device-", child_label(label, "device ID")));
        const std::uint64_t local_epoch = request.local_epoch.value_or(1U);
        const std::uint64_t max_payload_bytes =
            selected_max_payload_or_throw(request);
        if (!sync_id_is_valid(folder_id)) {
            throw std::invalid_argument(
                "requested folder ID is not a lowercase portable sync ID");
        }
        if (!sync_id_is_valid(local_device)) {
            throw std::invalid_argument(
                "requested local device ID is not a lowercase portable sync ID");
        }
        if (local_epoch == 0U) {
            throw std::invalid_argument("requested local epoch must be positive");
        }

        std::vector<std::string> arguments{
            "init",
            "--manifest", layout.manifest_path.generic_string(),
            "--replica-db", layout.replica_database_path.generic_string(),
            "--payload-root", layout.payload_root.generic_string(),
            "--effect-db", layout.effect_database_path.generic_string(),
            "--files-root", layout.files_root.generic_string(),
            "--membership-db", layout.membership_database_path.generic_string(),
            "--anchor-db",
            layout.membership_anchor_database_path.generic_string(),
            "--folder", folder_id,
            "--local-device", local_device,
            "--local-epoch", std::to_string(local_epoch),
            "--max-payload-bytes", std::to_string(max_payload_bytes)};
        append_initial_files_arguments(arguments, request.initial_files_policy);
        (void)run_sync_sibling_process_or_throw(
            replica_executable, arguments,
            kSyncReplicaDeploymentManifestMaxBytes + 4096U,
            child_label(label, "replica initialization"));
        result.deployment_disposition =
            SyncLocalShareDeploymentDisposition::Initialized;
    }

    result.deployment = read_sync_replica_deployment_manifest_or_throw(
        layout.manifest_path, child_label(label, "committed deployment"));
    require_deployment_matches_layout_or_throw(
        result.deployment, layout, label);
    require_optional_identity_matches_or_throw(request, result.deployment);

    const SyncLocalShareUserLayoutPreparation reproved =
        prepare_sync_local_share_user_layout_or_throw(
            request.instance, layout.state_directory, layout.files_root,
            child_label(label, "post-bootstrap layout reproof"));
    if (reproved.layout != layout) {
        throw std::logic_error(label + " layout changed during bootstrap");
    }

    result.catalog_path = sync_replica_folder_catalog_path_or_throw(
        result.deployment, child_label(label, "folder catalog"));
    const bool catalog_was_present = regular_file_is_present_or_throw(
        result.catalog_path, child_label(label, "folder catalog"));
    if (!catalog_was_present) {
        (void)run_sync_sibling_process_or_throw(
            folder_executable,
            {"init", "--manifest", layout.manifest_path.generic_string()},
            64U * 1024U,
            child_label(label, "folder-catalog initialization"));
        result.catalog_disposition =
            SyncLocalShareCatalogDisposition::Initialized;
    } else {
        result.catalog_disposition =
            SyncLocalShareCatalogDisposition::ReusedExisting;
    }

    result.folder_limits = folder_limits_or_throw(request, result.deployment);
    SyncReplicaFolderProcessOwner folder_owner(
        result.deployment, child_label(label, "folder owner"));
    result.catalog_before = folder_owner.catalog_snapshot_or_throw();
    result.replica_before = folder_owner.replica_snapshot_or_throw();
    result.initial_pass = folder_owner.run_convergence_pass_or_throw(
        result.folder_limits);
    result.catalog_after = folder_owner.catalog_snapshot_or_throw();
    result.replica_after = folder_owner.replica_snapshot_or_throw();

    const SyncLinkedPeerIdentityLayout identity_layout =
        prepare_sync_linked_peer_identity_layout_or_throw(
            request.instance, request.home_directory,
            child_label(label, "identity layout"));
    result.identity = create_or_resume_sync_linked_peer_identity_or_throw(
        identity_layout, result.deployment,
        child_label(label, "identity"));
    result.pairing_card_sha256 = sync_linked_peer_card_sha256_or_throw(
        result.identity.card, child_label(label, "pairing card"));
    result.pairing_verification_code =
        sync_linked_peer_card_verification_code_or_throw(
            result.identity.card,
            child_label(label, "pairing verification code"));

    return result;
}

}  // namespace anonsync

#endif
