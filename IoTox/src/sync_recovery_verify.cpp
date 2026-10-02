#include "iotox/sync_recovery_verify.hpp"

#include "iotox/security/sodium.hpp"
#include "iotox/sync_doctor.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"
#include "iotox/sync_namespace.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <sstream>
#include <string_view>
#include <sys/stat.h>

namespace iotox::sync {
namespace {

[[nodiscard]] std::string hex_path(const std::filesystem::path &path) {
  return security::hex(std::span<const std::uint8_t>{
      reinterpret_cast<const std::uint8_t *>(path.native().data()),
      path.native().size()});
}

[[nodiscard]] std::string hex_text(std::string_view text) {
  return security::hex(std::span<const std::uint8_t>{
      reinterpret_cast<const std::uint8_t *>(text.data()), text.size()});
}

[[nodiscard]] Status validate_operator_field(
    const std::optional<std::string> &field, std::string_view label) {
  if (!field) {
    return Status::success();
  }
  if (field->empty() || field->size() > 256U ||
      std::any_of(field->begin(), field->end(), [](unsigned char byte) {
        return byte < 0x20U || byte == 0x7fU;
      })) {
    return Status{ErrorCode::invalid_argument,
                  std::string(label) +
                      " must contain 1..256 printable bytes"};
  }
  return Status::success();
}

[[nodiscard]] Status validate_operator_provenance(
    const SyncRecoveryVerifyOptions &options) {
  const std::array<const std::optional<std::string> *, 4U> fields{
      &options.backup_system, &options.backup_generation,
      &options.backup_failure_domain, &options.restore_provenance};
  const std::size_t present = static_cast<std::size_t>(std::count_if(
      fields.begin(), fields.end(), [](const auto *field) {
        return field->has_value();
      }));
  if (present != 0U && present != fields.size()) {
    return Status{
        ErrorCode::invalid_argument,
        "sync recovery operator provenance requires backup-system, "
        "backup-generation, backup-failure-domain, and restore-provenance "
        "together"};
  }
  Status valid = validate_operator_field(options.backup_system,
                                         "backup-system");
  if (!valid.ok()) return valid;
  valid = validate_operator_field(options.backup_generation,
                                  "backup-generation");
  if (!valid.ok()) return valid;
  valid = validate_operator_field(options.backup_failure_domain,
                                  "backup-failure-domain");
  if (!valid.ok()) return valid;
  return validate_operator_field(options.restore_provenance,
                                 "restore-provenance");
}

[[nodiscard]] bool path_contains(const std::filesystem::path &parent,
                                 const std::filesystem::path &child) {
  auto parent_component = parent.begin();
  auto child_component = child.begin();
  while (parent_component != parent.end() && child_component != child.end() &&
         *parent_component == *child_component) {
    ++parent_component;
    ++child_component;
  }
  return parent_component == parent.end();
}

[[nodiscard]] Result<std::filesystem::path>
canonical_root(const std::filesystem::path &path, std::string_view label) {
  if (path.empty() || !path.is_absolute() || path.lexically_normal() != path ||
      path == path.root_path()) {
    return Status{ErrorCode::invalid_argument,
                  std::string(label) +
                      " must be one normalized absolute non-root path"};
  }
  std::error_code error;
  const std::filesystem::path canonical =
      std::filesystem::canonical(path, error);
  if (error || canonical.empty() || !canonical.is_absolute() ||
      canonical == canonical.root_path()) {
    return Status{ErrorCode::io_error, "unable to resolve " +
                                           std::string(label) + ": " +
                                           error.message()};
  }
  struct stat metadata {};
  if (::lstat(canonical.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode)) {
    return Status{ErrorCode::invalid_argument,
                  std::string(label) + " must resolve to a directory"};
  }
  return canonical;
}

[[nodiscard]] NamespacePolicy recovery_policy(std::uint64_t maximum_bytes,
                                              std::uint64_t maximum_entries,
                                              const PrincipalId &writer) {
  NamespacePolicy policy;
  policy.id = "recovery-verify";
  policy.root = "/var/lib/iotox/recovery-verify";
  policy.engine = Engine::tree_v2;
  policy.activation = ActivationMode::manual;
  policy.writers = {writer};
  policy.projection.metadata = TreeV2MetadataMode::owner_mode_v2;
  policy.quotas.maximum_artifact_bytes = maximum_bytes;
  policy.quotas.maximum_manifest_bytes = maximum_bytes;
  policy.quotas.maximum_store_bytes = maximum_bytes;
  policy.quotas.maximum_staging_bytes = maximum_bytes;
  policy.quotas.maximum_objects = maximum_entries;
  policy.quotas.maximum_retained_revisions = 1U;
  policy.quotas.maximum_peers = 1U;
  policy.quotas.maximum_lanes = 1U;
  policy.quotas.maximum_outstanding_requests = 1U;
  return policy;
}

[[nodiscard]] Status
require_conflict_free_tree(const std::filesystem::path &root,
                           std::string_view label) {
  const std::filesystem::path conflicts =
      root / std::string(kTreeV2ConflictRoot);
  struct stat metadata {};
  if (::lstat(conflicts.c_str(), &metadata) == 0) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) +
                      " contains an unresolved IoTox conflict projection"};
  }
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error, "unable to inspect " +
                                           std::string(label) + ": " +
                                           std::strerror(errno)};
  }
  return Status::success();
}

[[nodiscard]] bool equivalent_scan(const TreeV2ScanResult &left,
                                   const TreeV2ScanResult &right) {
  return left.manifest == right.manifest &&
         left.directories == right.directories &&
         left.files.size() == right.files.size() &&
         left.file_bytes == right.file_bytes;
}

} // namespace

Result<SyncRecoveryVerifyReport>
verify_sync_recovery_trees(const SyncRecoveryVerifyOptions &options,
                           const security::Sodium &sodium) {
  if (options.maximum_bytes == 0U ||
      options.maximum_bytes > (std::uint64_t{1U} << 60U) ||
      options.maximum_entries == 0U ||
      options.maximum_entries > (std::uint64_t{1U} << 32U)) {
    return Status{ErrorCode::invalid_argument,
                  "sync recovery verification bounds are outside the "
                  "supported range"};
  }
  const Status valid_operator_provenance =
      validate_operator_provenance(options);
  if (!valid_operator_provenance.ok()) return valid_operator_provenance;
  auto backup = canonical_root(options.backup_root, "backup root");
  if (!backup)
    return backup.status();
  auto restored = canonical_root(options.restored_root, "restored root");
  if (!restored)
    return restored.status();
  if (path_contains(backup.value(), restored.value()) ||
      path_contains(restored.value(), backup.value())) {
    return Status{ErrorCode::invalid_argument,
                  "backup and restored roots must be disjoint"};
  }
  struct stat backup_metadata {};
  struct stat restored_metadata {};
  if (::lstat(backup.value().c_str(), &backup_metadata) != 0 ||
      ::lstat(restored.value().c_str(), &restored_metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect recovery verification roots"};
  }
  if (backup_metadata.st_dev == restored_metadata.st_dev &&
      backup_metadata.st_ino == restored_metadata.st_ino) {
    return Status{ErrorCode::invalid_argument,
                  "backup and restored roots resolve to one directory"};
  }
  Status conflict_free =
      require_conflict_free_tree(backup.value(), "backup root");
  if (!conflict_free.ok())
    return conflict_free;
  conflict_free = require_conflict_free_tree(restored.value(), "restored root");
  if (!conflict_free.ok())
    return conflict_free;

  PrincipalId writer{};
  writer.front() = 1U;
  const NamespacePolicy policy =
      recovery_policy(options.maximum_bytes, options.maximum_entries, writer);
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;

  SyncDoctorOptions contract;
  contract.access = SyncDoctorAccess::read_write;
  contract.projection = policy.projection;
  contract.quotas = policy.quotas;
  contract.source = backup.value();
  Status valid_contract = inspect_sync_filesystem_contract(contract);
  if (!valid_contract.ok())
    return valid_contract;
  contract.source = restored.value();
  valid_contract = inspect_sync_filesystem_contract(contract);
  if (!valid_contract.ok())
    return valid_contract;

  auto backup_first =
      scan_tree_v2_worktree(policy, backup.value(), std::nullopt, writer, 1U);
  if (!backup_first)
    return backup_first.status();
  auto restored_first =
      scan_tree_v2_worktree(policy, restored.value(), std::nullopt, writer, 1U);
  if (!restored_first)
    return restored_first.status();
  auto backup_second =
      scan_tree_v2_worktree(policy, backup.value(), std::nullopt, writer, 1U);
  if (!backup_second)
    return backup_second.status();
  auto restored_second =
      scan_tree_v2_worktree(policy, restored.value(), std::nullopt, writer, 1U);
  if (!restored_second)
    return restored_second.status();

  contract.source = backup.value();
  valid_contract = inspect_sync_filesystem_contract(contract);
  if (!valid_contract.ok())
    return valid_contract;
  contract.source = restored.value();
  valid_contract = inspect_sync_filesystem_contract(contract);
  if (!valid_contract.ok())
    return valid_contract;
  if (!equivalent_scan(backup_first.value(), backup_second.value()) ||
      !equivalent_scan(restored_first.value(), restored_second.value())) {
    return Status{ErrorCode::protocol_error,
                  "recovery verification tree changed between scans"};
  }

  auto backup_digest =
      tree_v2_manifest_digest(policy, backup_second.value().manifest, sodium);
  if (!backup_digest)
    return backup_digest.status();
  auto restored_digest =
      tree_v2_manifest_digest(policy, restored_second.value().manifest, sodium);
  if (!restored_digest)
    return restored_digest.status();

  SyncRecoveryVerifyReport report;
  report.backup_root = backup.value();
  report.restored_root = restored.value();
  report.backup_manifest = backup_digest.value();
  report.restored_manifest = restored_digest.value();
  report.backup_directories = backup_second.value().directories;
  report.backup_files = backup_second.value().files.size();
  report.backup_entries = backup_second.value().manifest.entries.size();
  report.backup_bytes = backup_second.value().file_bytes;
  report.restored_directories = restored_second.value().directories;
  report.restored_files = restored_second.value().files.size();
  report.restored_entries = restored_second.value().manifest.entries.size();
  report.restored_bytes = restored_second.value().file_bytes;
  report.maximum_bytes = options.maximum_bytes;
  report.maximum_entries = options.maximum_entries;
  report.roots_on_distinct_devices =
      backup_metadata.st_dev != restored_metadata.st_dev;
  report.operator_provenance_present = options.backup_system.has_value();
  report.backup_system = options.backup_system;
  report.backup_generation = options.backup_generation;
  report.backup_failure_domain = options.backup_failure_domain;
  report.restore_provenance = options.restore_provenance;
  report.matches =
      backup_second.value().manifest == restored_second.value().manifest &&
      report.backup_directories == report.restored_directories &&
      report.backup_files == report.restored_files &&
      report.backup_entries == report.restored_entries &&
      report.backup_bytes == report.restored_bytes;
  return report;
}

std::string
render_sync_recovery_verify_report(const SyncRecoveryVerifyReport &report) {
  const bool provenance_present =
      report.operator_provenance_present && report.backup_system &&
      report.backup_generation && report.backup_failure_domain &&
      report.restore_provenance;
  std::ostringstream output;
  output << "iotox-sync-recovery-verify-v1\n"
         << "decision=" << (report.matches ? "match" : "mismatch") << '\n'
         << "model=tree-v2-owner-mode-v2\n"
         << "backup-path-hex=" << hex_path(report.backup_root) << '\n'
         << "restored-path-hex=" << hex_path(report.restored_root) << '\n'
         << "backup-manifest=" << security::hex(report.backup_manifest) << '\n'
         << "restored-manifest=" << security::hex(report.restored_manifest)
         << '\n'
         << "backup-directories=" << report.backup_directories << '\n'
         << "backup-files=" << report.backup_files << '\n'
         << "backup-entries=" << report.backup_entries << '\n'
         << "backup-bytes=" << report.backup_bytes << '\n'
         << "restored-directories=" << report.restored_directories << '\n'
         << "restored-files=" << report.restored_files << '\n'
         << "restored-entries=" << report.restored_entries << '\n'
         << "restored-bytes=" << report.restored_bytes << '\n'
         << "maximum-bytes=" << report.maximum_bytes << '\n'
         << "maximum-entries=" << report.maximum_entries << '\n'
         << "root-devices-differ="
         << (report.roots_on_distinct_devices ? 1 : 0) << '\n'
         << "filesystem-contract=ready\n"
         << "stable-double-scan=ready\n"
         << "iotox-live-state-read=0\n"
         << "operator-provenance="
         << (provenance_present ? "present" : "absent")
         << '\n';
  if (provenance_present) {
    output << "backup-system-hex=" << hex_text(*report.backup_system) << '\n'
           << "backup-generation-hex="
           << hex_text(*report.backup_generation) << '\n'
           << "backup-failure-domain-hex="
           << hex_text(*report.backup_failure_domain) << '\n'
           << "restore-provenance-hex="
           << hex_text(*report.restore_provenance) << '\n';
  }
  output
         << "backup-independence=not-assessed\n"
         << "restore-provenance=not-assessed\n";
  return output.str();
}

} // namespace iotox::sync
