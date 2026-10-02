#pragma once

#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>

namespace iotox::sync {

struct SyncRecoveryVerifyOptions {
  std::filesystem::path backup_root;
  std::filesystem::path restored_root;
  std::uint64_t maximum_bytes{64U * 1024U * 1024U};
  std::uint64_t maximum_entries{4096U};
  std::optional<std::string> backup_system;
  std::optional<std::string> backup_generation;
  std::optional<std::string> backup_failure_domain;
  std::optional<std::string> restore_provenance;
};

struct SyncRecoveryVerifyReport {
  std::filesystem::path backup_root;
  std::filesystem::path restored_root;
  Digest backup_manifest{};
  Digest restored_manifest{};
  std::uint64_t backup_directories{0U};
  std::uint64_t backup_files{0U};
  std::uint64_t backup_entries{0U};
  std::uint64_t backup_bytes{0U};
  std::uint64_t restored_directories{0U};
  std::uint64_t restored_files{0U};
  std::uint64_t restored_entries{0U};
  std::uint64_t restored_bytes{0U};
  std::uint64_t maximum_bytes{0U};
  std::uint64_t maximum_entries{0U};
  bool roots_on_distinct_devices{false};
  bool operator_provenance_present{false};
  std::optional<std::string> backup_system;
  std::optional<std::string> backup_generation;
  std::optional<std::string> backup_failure_domain;
  std::optional<std::string> restore_provenance;
  bool matches{false};
};

// Compares an externally restored ordinary tree to an operator-supplied
// backup tree. Neither tree may alias or contain the other. Both are scanned
// twice under the strict doctor filesystem contract; no IoTox live state is
// read and neither tree is modified.
[[nodiscard]] Result<SyncRecoveryVerifyReport>
verify_sync_recovery_trees(const SyncRecoveryVerifyOptions &options,
                           const security::Sodium &sodium);

[[nodiscard]] std::string
render_sync_recovery_verify_report(const SyncRecoveryVerifyReport &report);

} // namespace iotox::sync
