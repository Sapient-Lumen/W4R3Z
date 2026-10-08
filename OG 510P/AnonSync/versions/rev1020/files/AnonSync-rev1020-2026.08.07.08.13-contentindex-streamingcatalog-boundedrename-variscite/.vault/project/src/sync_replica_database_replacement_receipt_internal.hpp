#pragma once

#if !defined(_WIN32)

#include "sync_replica_database_replacement.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>

namespace anonsync::sync_replica_database_replacement_detail {

struct ReplacementReceiptArtifact final {
    std::string artifact_sha256;
    std::uint64_t artifact_bytes = 0U;
    std::uint32_t sqlite_page_size = 0U;
    std::uint32_t sqlite_page_count = 0U;
    SyncReplicaDatabaseBackupCutpoint source_cutpoint;

    bool operator==(const ReplacementReceiptArtifact&) const = default;
};

struct ReplacementReceipt final {
    std::string deployment_id;
    std::string manifest_digest;
    std::string manifest_path_sha256;
    std::string replica_database_path_sha256;
    std::string candidate_path_sha256;
    std::string rollback_path_sha256;
    std::string receipt_path_sha256;
    SyncReplicaDatabaseReplacementExpectation expected_current;
    ReplacementReceiptArtifact candidate;
    ReplacementReceiptArtifact rollback;
    std::string action_sha256;

    bool operator==(const ReplacementReceipt&) const = default;
};

struct ReplacementReceiptObservation final {
    std::filesystem::path receipt_path;
    std::string action_sha256;
    std::string record_sha256;
    std::uint64_t byte_count = 0U;

    bool operator==(const ReplacementReceiptObservation&) const = default;
};

void validate_external_receipt_path_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::filesystem::path& candidate_path,
    const std::filesystem::path& rollback_path,
    const std::filesystem::path& receipt_path,
    const std::string& label);

[[nodiscard]] ReplacementReceipt make_replacement_receipt_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::filesystem::path& candidate_path,
    const std::filesystem::path& rollback_path,
    const std::filesystem::path& receipt_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current,
    const SyncReplicaDatabaseBackupArtifactObservation& candidate,
    const SyncReplicaDatabaseBackupArtifactObservation& rollback,
    const std::string& label);

[[nodiscard]] std::optional<ReplacementReceipt>
read_replacement_receipt_if_present_or_throw(
    const std::filesystem::path& receipt_path,
    const std::string& label);

[[nodiscard]] ReplacementReceiptObservation
publish_replacement_receipt_create_new_or_throw(
    const std::filesystem::path& receipt_path,
    const ReplacementReceipt& receipt,
    const std::string& label);

[[nodiscard]] ReplacementReceiptObservation
reprove_replacement_receipt_or_throw(
    const std::filesystem::path& receipt_path,
    const ReplacementReceipt& expected,
    const std::string& label);

void require_replacement_receipt_selection_matches_or_throw(
    const ReplacementReceipt& receipt,
    const SyncReplicaDeploymentManifest& deployment,
    const std::filesystem::path& candidate_path,
    const std::filesystem::path& rollback_path,
    const std::filesystem::path& receipt_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current,
    const SyncReplicaDatabaseBackupArtifactObservation& candidate,
    const std::string& label);

void require_replacement_receipt_artifact_matches_or_throw(
    const ReplacementReceiptArtifact& expected,
    const SyncReplicaDatabaseBackupArtifactObservation& observed,
    const std::string& artifact_name,
    const std::string& label);

}  // namespace anonsync::sync_replica_database_replacement_detail

#endif
