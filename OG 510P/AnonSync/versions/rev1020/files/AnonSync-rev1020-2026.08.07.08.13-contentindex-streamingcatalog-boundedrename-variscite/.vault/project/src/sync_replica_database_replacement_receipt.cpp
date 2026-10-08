#include "sync_replica_database_replacement_receipt_internal.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_replica_database_artifact_internal.hpp"

#include <charconv>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

namespace anonsync::sync_replica_database_replacement_detail {

namespace fs = std::filesystem;
namespace artifact_detail = sync_replica_database_artifact_detail;
using namespace std::literals;

namespace {

constexpr std::string_view kReceiptMagic =
    "anonsync:replica-database-replacement-receipt:v1"sv;
constexpr std::string_view kReceiptPathDigestDomain =
    "anonsync:replica-database-replacement-receipt:path:v1\0"sv;
constexpr std::string_view kReceiptActionDigestDomain =
    "anonsync:replica-database-replacement-receipt:action:v1\0"sv;
constexpr std::string_view kReceiptRecordDigestDomain =
    "anonsync:replica-database-replacement-receipt:record:v1\0"sv;
static_assert(kReceiptPathDigestDomain.back() == '\0');
static_assert(kReceiptActionDigestDomain.back() == '\0');
static_assert(kReceiptRecordDigestDomain.back() == '\0');
constexpr std::uint64_t kMaximumReceiptBytes = 8U * 1024U;

[[noreturn]] void receipt_invalid(
    const std::string& label,
    const std::string& reason) {
    throw std::runtime_error(label + " replacement receipt " + reason);
}

[[nodiscard]] std::string path_digest(const fs::path& path) {
    Sha256DigestBuilder digest;
    digest.update(kReceiptPathDigestDomain);
    digest.update(path.generic_string());
    return digest.finish_hex();
}

void append_field(
    std::string& output,
    std::string_view name,
    std::string_view value) {
    if (name.empty() || name.find_first_of("=\r\n") != std::string_view::npos ||
        value.find_first_of("\r\n") != std::string_view::npos) {
        throw std::logic_error(
            "replacement receipt canonical field contains a delimiter");
    }
    output.append(name);
    output.push_back('=');
    output.append(value);
    output.push_back('\n');
}

void append_u64(
    std::string& output,
    std::string_view name,
    std::uint64_t value) {
    append_field(output, name, std::to_string(value));
}

void append_cutpoint_fields(
    std::string& output,
    std::string_view prefix,
    const SyncReplicaDatabaseBackupCutpoint& cutpoint) {
    const std::string p(prefix);
    append_field(output, p + "_database_incarnation_sha256",
                 cutpoint.database_incarnation_sha256);
    append_u64(output, p + "_database_recovery_epoch",
               cutpoint.database_recovery_epoch);
    append_u64(output, p + "_state_generation", cutpoint.state_generation);
    append_u64(output, p + "_policy_generation", cutpoint.policy_generation);
    append_u64(output, p + "_outbox_time_high_water_epoch",
               cutpoint.outbox_time_high_water_epoch);
    append_field(output, p + "_local_operation_digest",
                 cutpoint.local_operation_digest);
    append_field(output, p + "_operation_set_digest",
                 cutpoint.operation_set_digest);
    append_field(output, p + "_evidence_set_digest",
                 cutpoint.evidence_set_digest);
    append_field(output, p + "_visible_state_digest",
                 cutpoint.visible_state_digest);
    append_field(output, p + "_outbox_digest", cutpoint.outbox_digest);
    append_field(output, p + "_outbox_clock_digest",
                 cutpoint.outbox_clock_digest);
    append_u64(output, p + "_historical_version_pin_count",
               cutpoint.historical_version_pin_count);
    append_field(output, p + "_historical_version_pin_set_digest",
                 cutpoint.historical_version_pin_set_digest);
    append_field(output, p + "_cutpoint_digest", cutpoint.cutpoint_digest);
}

void append_artifact_fields(
    std::string& output,
    std::string_view prefix,
    const ReplacementReceiptArtifact& artifact) {
    const std::string p(prefix);
    append_field(output, p + "_artifact_sha256", artifact.artifact_sha256);
    append_u64(output, p + "_artifact_bytes", artifact.artifact_bytes);
    append_u64(output, p + "_sqlite_page_size", artifact.sqlite_page_size);
    append_u64(output, p + "_sqlite_page_count", artifact.sqlite_page_count);
    append_cutpoint_fields(output, p, artifact.source_cutpoint);
}

[[nodiscard]] ReplacementReceiptArtifact receipt_artifact(
    const SyncReplicaDatabaseBackupArtifactObservation& observed) {
    return {
        .artifact_sha256 = observed.artifact_sha256,
        .artifact_bytes = observed.artifact_bytes,
        .sqlite_page_size = observed.sqlite_page_size,
        .sqlite_page_count = observed.sqlite_page_count,
        .source_cutpoint = observed.source_cutpoint,
    };
}

void require_digest(
    std::string_view value,
    std::string_view field,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(value)) {
        receipt_invalid(label, std::string(field) + " digest is invalid");
    }
}

void validate_cutpoint(
    const SyncReplicaDatabaseBackupCutpoint& cutpoint,
    std::string_view prefix,
    const std::string& label) {
    require_digest(cutpoint.database_incarnation_sha256,
                   std::string(prefix) + " database incarnation", label);
    if (cutpoint.database_recovery_epoch == 0U) {
        receipt_invalid(label,
                        std::string(prefix) + " recovery epoch is zero");
    }
    for (const auto& [name, value] : {
             std::pair<std::string_view, const std::string&>{
                 "local operation", cutpoint.local_operation_digest},
             {"operation set", cutpoint.operation_set_digest},
             {"evidence set", cutpoint.evidence_set_digest},
             {"visible state", cutpoint.visible_state_digest},
             {"outbox", cutpoint.outbox_digest},
             {"outbox clock", cutpoint.outbox_clock_digest},
             {"historical version pin set",
              cutpoint.historical_version_pin_set_digest},
             {"cutpoint", cutpoint.cutpoint_digest},
         }) {
        require_digest(value, std::string(prefix) + " " + std::string(name),
                       label);
    }
}

void validate_artifact(
    const ReplacementReceiptArtifact& artifact,
    std::string_view prefix,
    const std::string& label) {
    require_digest(artifact.artifact_sha256,
                   std::string(prefix) + " artifact", label);
    if (artifact.artifact_bytes == 0U || artifact.sqlite_page_size == 0U ||
        artifact.sqlite_page_count == 0U ||
        artifact.artifact_bytes !=
            static_cast<std::uint64_t>(artifact.sqlite_page_size) *
                static_cast<std::uint64_t>(artifact.sqlite_page_count)) {
        receipt_invalid(label,
                        std::string(prefix) + " artifact geometry is invalid");
    }
    validate_cutpoint(artifact.source_cutpoint, prefix, label);
}

[[nodiscard]] std::string immutable_receipt_fields(
    const ReplacementReceipt& receipt) {
    std::string output;
    output.reserve(4096U);
    append_field(output, "deployment_id", receipt.deployment_id);
    append_field(output, "manifest_digest", receipt.manifest_digest);
    append_field(output, "manifest_path_sha256",
                 receipt.manifest_path_sha256);
    append_field(output, "replica_database_path_sha256",
                 receipt.replica_database_path_sha256);
    append_field(output, "candidate_path_sha256",
                 receipt.candidate_path_sha256);
    append_field(output, "rollback_path_sha256",
                 receipt.rollback_path_sha256);
    append_field(output, "receipt_path_sha256", receipt.receipt_path_sha256);
    append_field(output, "expected_database_incarnation_sha256",
                 receipt.expected_current.database_incarnation_sha256);
    append_u64(output, "expected_database_recovery_epoch",
               receipt.expected_current.database_recovery_epoch);
    append_field(output, "expected_cutpoint_digest",
                 receipt.expected_current.cutpoint_digest);
    append_artifact_fields(output, "candidate", receipt.candidate);
    append_artifact_fields(output, "rollback", receipt.rollback);
    return output;
}

[[nodiscard]] std::string action_digest(
    const ReplacementReceipt& receipt) {
    Sha256DigestBuilder digest;
    digest.update(kReceiptActionDigestDomain);
    digest.update(immutable_receipt_fields(receipt));
    return digest.finish_hex();
}

void validate_receipt(
    const ReplacementReceipt& receipt,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(receipt.deployment_id) ||
        !is_lowercase_sha256_hex(receipt.manifest_digest)) {
        receipt_invalid(label, "deployment binding is invalid");
    }
    for (const auto& [name, value] : {
             std::pair<std::string_view, const std::string&>{
                 "manifest path", receipt.manifest_path_sha256},
             {"replica database path", receipt.replica_database_path_sha256},
             {"candidate path", receipt.candidate_path_sha256},
             {"rollback path", receipt.rollback_path_sha256},
             {"receipt path", receipt.receipt_path_sha256},
         }) {
        require_digest(value, name, label);
    }
    require_digest(receipt.expected_current.database_incarnation_sha256,
                   "expected database incarnation", label);
    if (receipt.expected_current.database_recovery_epoch == 0U) {
        receipt_invalid(label, "expected recovery epoch is zero");
    }
    require_digest(receipt.expected_current.cutpoint_digest,
                   "expected cutpoint", label);
    validate_artifact(receipt.candidate, "candidate", label);
    validate_artifact(receipt.rollback, "rollback", label);
    require_digest(receipt.action_sha256, "action", label);
    if (action_digest(receipt) != receipt.action_sha256) {
        receipt_invalid(label, "action digest is inconsistent");
    }
}

[[nodiscard]] std::string serialize_receipt(
    const ReplacementReceipt& receipt,
    const std::string& label) {
    validate_receipt(receipt, label);
    std::string encoded;
    encoded.reserve(6144U);
    encoded.append(kReceiptMagic);
    encoded.push_back('\n');
    encoded.append(immutable_receipt_fields(receipt));
    append_field(encoded, "action_sha256", receipt.action_sha256);
    Sha256DigestBuilder digest;
    digest.update(kReceiptRecordDigestDomain);
    digest.update(encoded);
    append_field(encoded, "record_sha256", digest.finish_hex());
    if (encoded.size() > kMaximumReceiptBytes) {
        throw std::length_error(label + " replacement receipt exceeds 8 KiB");
    }
    return encoded;
}

class LineCursor final {
public:
    LineCursor(std::string_view bytes, std::string label)
        : bytes_(bytes), label_(std::move(label)) {
        if (bytes_.empty() || bytes_.back() != '\n' ||
            bytes_.find('\r') != std::string_view::npos ||
            bytes_.find('\0') != std::string_view::npos) {
            receipt_invalid(label_, "framing is invalid");
        }
    }

    [[nodiscard]] std::string take_line() {
        const std::size_t end = bytes_.find('\n', position_);
        if (end == std::string_view::npos) {
            receipt_invalid(label_, "is truncated");
        }
        std::string line(bytes_.substr(position_, end - position_));
        position_ = end + 1U;
        return line;
    }

    [[nodiscard]] std::string take_field(std::string_view expected_name) {
        const std::string line = take_line();
        const std::string prefix = std::string(expected_name) + "=";
        if (!line.starts_with(prefix)) {
            receipt_invalid(label_,
                            "field order changed at " +
                                std::string(expected_name));
        }
        return line.substr(prefix.size());
    }

    [[nodiscard]] std::uint64_t take_u64(std::string_view name) {
        const std::string value = take_field(name);
        if (value.empty() || (value.size() > 1U && value.front() == '0')) {
            receipt_invalid(label_,
                            std::string(name) + " integer is noncanonical");
        }
        std::uint64_t parsed = 0U;
        const auto result = std::from_chars(
            value.data(), value.data() + value.size(), parsed);
        if (result.ec != std::errc{} ||
            result.ptr != value.data() + value.size()) {
            receipt_invalid(label_, std::string(name) + " integer is invalid");
        }
        return parsed;
    }

    [[nodiscard]] bool exhausted() const noexcept {
        return position_ == bytes_.size();
    }

private:
    std::string_view bytes_;
    std::string label_;
    std::size_t position_ = 0U;
};

[[nodiscard]] SyncReplicaDatabaseBackupCutpoint parse_cutpoint(
    LineCursor& cursor,
    std::string_view prefix) {
    const std::string p(prefix);
    SyncReplicaDatabaseBackupCutpoint out;
    out.database_incarnation_sha256 =
        cursor.take_field(p + "_database_incarnation_sha256");
    out.database_recovery_epoch =
        cursor.take_u64(p + "_database_recovery_epoch");
    out.state_generation = cursor.take_u64(p + "_state_generation");
    out.policy_generation = cursor.take_u64(p + "_policy_generation");
    out.outbox_time_high_water_epoch =
        cursor.take_u64(p + "_outbox_time_high_water_epoch");
    out.local_operation_digest =
        cursor.take_field(p + "_local_operation_digest");
    out.operation_set_digest = cursor.take_field(p + "_operation_set_digest");
    out.evidence_set_digest = cursor.take_field(p + "_evidence_set_digest");
    out.visible_state_digest = cursor.take_field(p + "_visible_state_digest");
    out.outbox_digest = cursor.take_field(p + "_outbox_digest");
    out.outbox_clock_digest = cursor.take_field(p + "_outbox_clock_digest");
    out.historical_version_pin_count =
        cursor.take_u64(p + "_historical_version_pin_count");
    out.historical_version_pin_set_digest =
        cursor.take_field(p + "_historical_version_pin_set_digest");
    out.cutpoint_digest = cursor.take_field(p + "_cutpoint_digest");
    return out;
}

[[nodiscard]] ReplacementReceiptArtifact parse_artifact(
    LineCursor& cursor,
    std::string_view prefix,
    const std::string& label) {
    const std::string p(prefix);
    ReplacementReceiptArtifact out;
    out.artifact_sha256 = cursor.take_field(p + "_artifact_sha256");
    out.artifact_bytes = cursor.take_u64(p + "_artifact_bytes");
    const std::uint64_t page_size = cursor.take_u64(p + "_sqlite_page_size");
    const std::uint64_t page_count = cursor.take_u64(p + "_sqlite_page_count");
    if (page_size > std::numeric_limits<std::uint32_t>::max() ||
        page_count > std::numeric_limits<std::uint32_t>::max()) {
        receipt_invalid(label, p + " SQLite geometry overflows");
    }
    out.sqlite_page_size = static_cast<std::uint32_t>(page_size);
    out.sqlite_page_count = static_cast<std::uint32_t>(page_count);
    out.source_cutpoint = parse_cutpoint(cursor, p);
    return out;
}

[[nodiscard]] ReplacementReceipt parse_receipt(
    std::string_view bytes,
    const std::string& label,
    std::string* record_sha256_out) {
    if (bytes.size() > kMaximumReceiptBytes) {
        receipt_invalid(label, "exceeds 8 KiB");
    }
    LineCursor cursor(bytes, label);
    if (cursor.take_line() != kReceiptMagic) {
        receipt_invalid(label, "magic is invalid");
    }
    ReplacementReceipt receipt;
    receipt.deployment_id = cursor.take_field("deployment_id");
    receipt.manifest_digest = cursor.take_field("manifest_digest");
    receipt.manifest_path_sha256 = cursor.take_field("manifest_path_sha256");
    receipt.replica_database_path_sha256 =
        cursor.take_field("replica_database_path_sha256");
    receipt.candidate_path_sha256 = cursor.take_field("candidate_path_sha256");
    receipt.rollback_path_sha256 = cursor.take_field("rollback_path_sha256");
    receipt.receipt_path_sha256 = cursor.take_field("receipt_path_sha256");
    receipt.expected_current.database_incarnation_sha256 =
        cursor.take_field("expected_database_incarnation_sha256");
    receipt.expected_current.database_recovery_epoch =
        cursor.take_u64("expected_database_recovery_epoch");
    receipt.expected_current.cutpoint_digest =
        cursor.take_field("expected_cutpoint_digest");
    receipt.candidate = parse_artifact(cursor, "candidate", label);
    receipt.rollback = parse_artifact(cursor, "rollback", label);
    receipt.action_sha256 = cursor.take_field("action_sha256");
    const std::string record_sha256 = cursor.take_field("record_sha256");
    if (!cursor.exhausted()) {
        receipt_invalid(label, "contains trailing fields");
    }
    require_digest(record_sha256, "record", label);

    const std::size_t record_line_bytes =
        std::string("record_sha256=").size() + record_sha256.size() + 1U;
    if (bytes.size() < record_line_bytes) {
        receipt_invalid(label, "record framing underflowed");
    }
    Sha256DigestBuilder digest;
    digest.update(kReceiptRecordDigestDomain);
    digest.update(bytes.substr(0U, bytes.size() - record_line_bytes));
    if (digest.finish_hex() != record_sha256) {
        receipt_invalid(label, "checksum is invalid");
    }
    validate_receipt(receipt, label);
    if (serialize_receipt(receipt, label) != bytes) {
        receipt_invalid(label, "encoding is noncanonical");
    }
    if (record_sha256_out != nullptr) *record_sha256_out = record_sha256;
    return receipt;
}

[[nodiscard]] std::pair<ReplacementReceipt, ReplacementReceiptObservation>
read_receipt_or_throw(
    const fs::path& receipt_path,
    const std::string& label) {
    const std::string bytes =
        read_sync_bounded_private_regular_file_no_symlink_or_throw(
            receipt_path, kMaximumReceiptBytes, label);
    std::string record_sha256;
    ReplacementReceipt receipt = parse_receipt(bytes, label, &record_sha256);
    return {
        receipt,
        {
            .receipt_path = receipt_path,
            .action_sha256 = receipt.action_sha256,
            .record_sha256 = std::move(record_sha256),
            .byte_count = static_cast<std::uint64_t>(bytes.size()),
        },
    };
}

[[nodiscard]] bool receipt_path_collides_with_family(
    const fs::path& receipt_path,
    const fs::path& artifact_path) {
    for (const fs::path& member :
         artifact_detail::sqlite_artifact_family_paths(artifact_path)) {
        if (receipt_path == member) return true;
    }
    return false;
}

}  // namespace

void validate_external_receipt_path_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& candidate_path,
    const fs::path& rollback_path,
    const fs::path& receipt_path,
    const std::string& label) {
    artifact_detail::validate_artifact_path_or_throw(
        deployment, receipt_path, label);
    if (receipt_path_collides_with_family(receipt_path, candidate_path) ||
        receipt_path_collides_with_family(receipt_path, rollback_path)) {
        throw std::invalid_argument(
            label + " collides with a selected SQLite artifact family");
    }
}

ReplacementReceipt make_replacement_receipt_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& candidate_path,
    const fs::path& rollback_path,
    const fs::path& receipt_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current,
    const SyncReplicaDatabaseBackupArtifactObservation& candidate,
    const SyncReplicaDatabaseBackupArtifactObservation& rollback,
    const std::string& label) {
    ReplacementReceipt receipt{
        .deployment_id = deployment.deployment_id,
        .manifest_digest = deployment.manifest_digest,
        .manifest_path_sha256 = path_digest(deployment.manifest_path),
        .replica_database_path_sha256 = path_digest(deployment.replica_db),
        .candidate_path_sha256 = path_digest(candidate_path),
        .rollback_path_sha256 = path_digest(rollback_path),
        .receipt_path_sha256 = path_digest(receipt_path),
        .expected_current = expected_current,
        .candidate = receipt_artifact(candidate),
        .rollback = receipt_artifact(rollback),
        .action_sha256 = {},
    };
    receipt.action_sha256 = action_digest(receipt);
    validate_receipt(receipt, label);
    return receipt;
}

std::optional<ReplacementReceipt>
read_replacement_receipt_if_present_or_throw(
    const fs::path& receipt_path,
    const std::string& label) {
    try {
        return read_receipt_or_throw(receipt_path, label).first;
    } catch (...) {
        const std::exception_ptr read_failure = std::current_exception();
        artifact_detail::require_exact_path_absence_or_rethrow(
            receipt_path, read_failure);
        preflight_sync_file_create_new_no_symlink_or_throw(
            receipt_path, label + " absent receipt preflight");
        return std::nullopt;
    }
}

ReplacementReceiptObservation
publish_replacement_receipt_create_new_or_throw(
    const fs::path& receipt_path,
    const ReplacementReceipt& receipt,
    const std::string& label) {
    const std::string encoded = serialize_receipt(receipt, label);
    write_sync_file_atomically_create_new_no_symlink_or_throw(
        receipt_path,
        std::span<const unsigned char>(
            reinterpret_cast<const unsigned char*>(encoded.data()),
            encoded.size()),
        label + " publication");
    return reprove_replacement_receipt_or_throw(
        receipt_path, receipt, label + " postpublication reproof");
}

ReplacementReceiptObservation reprove_replacement_receipt_or_throw(
    const fs::path& receipt_path,
    const ReplacementReceipt& expected,
    const std::string& label) {
    auto [observed, observation] = read_receipt_or_throw(receipt_path, label);
    if (observed != expected) {
        receipt_invalid(label, "changed");
    }
    return observation;
}

void require_replacement_receipt_selection_matches_or_throw(
    const ReplacementReceipt& receipt,
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& candidate_path,
    const fs::path& rollback_path,
    const fs::path& receipt_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current,
    const SyncReplicaDatabaseBackupArtifactObservation& candidate,
    const std::string& label) {
    if (receipt.deployment_id != deployment.deployment_id ||
        receipt.manifest_digest != deployment.manifest_digest ||
        receipt.manifest_path_sha256 != path_digest(deployment.manifest_path) ||
        receipt.replica_database_path_sha256 !=
            path_digest(deployment.replica_db) ||
        receipt.candidate_path_sha256 != path_digest(candidate_path) ||
        receipt.rollback_path_sha256 != path_digest(rollback_path) ||
        receipt.receipt_path_sha256 != path_digest(receipt_path) ||
        receipt.expected_current.database_incarnation_sha256 !=
            expected_current.database_incarnation_sha256 ||
        receipt.expected_current.database_recovery_epoch !=
            expected_current.database_recovery_epoch ||
        receipt.expected_current.cutpoint_digest !=
            expected_current.cutpoint_digest ||
        receipt.candidate != receipt_artifact(candidate)) {
        receipt_invalid(label, "does not match the selected action");
    }
}

void require_replacement_receipt_artifact_matches_or_throw(
    const ReplacementReceiptArtifact& expected,
    const SyncReplicaDatabaseBackupArtifactObservation& observed,
    const std::string& artifact_name,
    const std::string& label) {
    if (expected != receipt_artifact(observed)) {
        receipt_invalid(label, artifact_name + " artifact changed");
    }
}

}  // namespace anonsync::sync_replica_database_replacement_detail

#endif
