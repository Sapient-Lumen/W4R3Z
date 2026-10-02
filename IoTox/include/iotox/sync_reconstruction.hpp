#pragma once

#include "iotox/sync_job.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <span>
#include <vector>

namespace iotox::sync {

struct SyncMissingRange {
  std::uint64_t offset{0U};
  std::uint64_t length{0U};

  [[nodiscard]] bool operator==(const SyncMissingRange &) const = default;
};

// A process-local plan bound to three already verified immutable objects: the
// target artifact named by the candidate HEAD, its range-v1 manifest, and one
// complete local artifact used as the basis. It is never accepted from wire.
struct SyncRangePlan {
  SyncObjectRecord target;
  SyncObjectRecord manifest;
  SyncObjectRecord basis;
  std::uint32_t block_bytes{0U};
  std::uint64_t blocks{0U};
  std::uint64_t basis_bytes{0U};
  std::uint64_t reused_bytes{0U};
  std::uint64_t missing_bytes{0U};
  std::uint64_t basis_read_calls{0U};
  std::uint64_t temporary_bytes_peak{0U};
  std::vector<std::uint64_t> basis_offsets;
  std::vector<SyncMissingRange> missing_ranges;

  [[nodiscard]] bool complete_without_source() const noexcept {
    return missing_bytes == 0U;
  }
};

struct SyncRangeReconstructionSeams {
  SyncInstallSeams install;
  // Reads bytes from the target artifact's address space. The implementation
  // may satisfy them from one local file, a verified range bundle, or a
  // bounded network adapter. Returning zero before filling a requested range
  // is terminal.
  std::function<Result<std::size_t>(std::uint64_t offset,
                                    std::span<std::uint8_t> output)>
      read_range;
  std::function<bool()> cancelled;
};

struct SyncRangeReconstructionResult {
  std::uint64_t attempt_id{0U};
  std::filesystem::path staging_path;
  Digest artifact{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t reused_bytes{0U};
  std::uint64_t fetched_bytes{0U};
  std::uint64_t source_read_calls{0U};
  std::uint64_t basis_read_calls{0U};
  std::uint64_t output_write_calls{0U};
};

// Commits the exact local interpretation of one range bundle: immutable
// target/manifest/basis records plus the derived block mapping and ordered
// missing spans. A restart may reuse prefix bytes only when a fresh authorized
// pull independently derives this same commitment.
[[nodiscard]] Result<Digest> sync_range_plan_commitment(
    const SyncRangePlan &plan, const security::Sodium &sodium);

// Plans against an exact digest-named local basis while the namespace
// transaction excludes cooperating publication, activation, retention, and
// collection mutations. Both the manifest and basis are rehashed first.
[[nodiscard]] Result<SyncRangePlan> plan_sync_range_reconstruction(
    const NamespacePolicy &policy, const SyncObjectRecord &target,
    const SyncObjectRecord &manifest, const SyncObjectRecord &basis,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams);

// Revalidates the plan and its immutable inputs, reconstructs into the sole
// private path derived from ATTEMPT_ID, and verifies the complete target SHA-
// 256. It does not commit an object, accept a HEAD, or activate a revision.
// On every failure it removes only its exact reconstruction partial/final.
[[nodiscard]] Result<SyncRangeReconstructionResult>
reconstruct_sync_range_artifact(
    const NamespacePolicy &policy, const SyncRangePlan &plan,
    std::uint64_t attempt_id,
    const SyncNamespaceTransaction &transaction,
    const SyncRangeReconstructionSeams &seams);

} // namespace iotox::sync
