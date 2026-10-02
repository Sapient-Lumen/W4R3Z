#pragma once

#include "iotox/status.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace iotox::sync {

enum class SyncDoctorAccess : std::uint8_t {
  one_writer = 1U,
  read_write = 2U,
};

struct SyncDoctorOptions {
  std::filesystem::path source;
  SyncDoctorAccess access{SyncDoctorAccess::one_writer};
  std::uint64_t interval_seconds{30U};
  TreeV2ProjectionPolicy projection;
  Quotas quotas;
};

struct SyncDoctorReport {
  std::filesystem::path source;
  SyncDoctorAccess access{SyncDoctorAccess::one_writer};
  Engine engine{Engine::content_v2};
  std::uint64_t interval_seconds{30U};
  TreeV2ProjectionPolicy projection;
  Quotas quotas;
  std::uint64_t directories{0U};
  std::uint64_t files{0U};
  std::uint64_t entries{0U};
  std::uint64_t content_bytes{0U};
  std::uint64_t manifest_bytes{0U};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t estimated_objects{0U};
  std::uint64_t minimum_store_bytes{0U};
  std::uint64_t minimum_staging_bytes{0U};
  std::uint64_t source_filesystem_available_bytes{0U};
  bool managed_storage_probed{false};
  std::string configured_namespace;
  std::filesystem::path managed_root;
  std::uint64_t automation_generation{0U};
  std::uint64_t automation_interval_ms{0U};
  std::uint64_t managed_store_objects{0U};
  std::uint64_t managed_store_bytes{0U};
  std::uint64_t managed_staging_bytes{0U};
  std::uint64_t managed_store_headroom_bytes{0U};
  std::uint64_t managed_staging_headroom_bytes{0U};
  std::uint64_t managed_filesystem_available_bytes{0U};
  std::uint64_t managed_filesystem_capacity_bytes{0U};
  std::uint64_t managed_filesystem_required_bytes{0U};
  std::uint64_t source_filesystem_required_bytes{0U};
};

// Checks only the source filesystem shape used by the doctor. The walk is
// read-only and bounded by OPTIONS. It refuses metadata or allocation
// semantics that IoTox does not preserve.
[[nodiscard]] Status
inspect_sync_filesystem_contract(const SyncDoctorOptions &options);

[[nodiscard]] Result<SyncDoctorReport>
inspect_sync_source(const SyncDoctorOptions &options);

// Joins one source inspection to an already configured namespace. The caller
// must have loaded the exact owner-private namespace and authenticated
// automation records. This function acquires the existing namespace
// transaction, verifies current immutable-store occupancy, inventories live
// staging, and checks both quota and filesystem headroom. It creates no
// namespace paths or state.
[[nodiscard]] Result<SyncDoctorReport> inspect_sync_managed_storage(
    SyncDoctorReport report, const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium, std::uint64_t automation_generation,
    std::uint64_t automation_interval_ms);

[[nodiscard]] std::string render_sync_doctor_report(
    const SyncDoctorReport &report);

} // namespace iotox::sync
