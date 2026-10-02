#include "iotox/sync_manifest.hpp"

#include "toxsync/index_file.hpp"

#include <algorithm>
#include <exception>
#include <limits>
#include <string>

namespace iotox::sync {
namespace {

bool all_zero(const Digest &digest) noexcept {
  return std::all_of(digest.begin(), digest.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

Digest from_toxsync(const toxsync::Digest256 &digest) noexcept {
  Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    result[index] = std::to_integer<std::uint8_t>(digest.bytes[index]);
  }
  return result;
}

toxsync::IndexLimits limits_for(const NamespacePolicy &policy) {
  toxsync::IndexLimits limits;
  limits.max_target_size = policy.quotas.maximum_artifact_bytes;
  const std::uint64_t records =
      policy.quotas.maximum_manifest_bytes <= toxsync::Index::kHeaderBytes
          ? 0U
          : (policy.quotas.maximum_manifest_bytes -
             toxsync::Index::kHeaderBytes) /
                toxsync::Index::kRecordBytes;
  limits.max_blocks = std::max<std::uint64_t>(records, 1U);
  return limits;
}

Status validate_common(const NamespacePolicy &policy,
                       const std::filesystem::path &artifact,
                       const std::filesystem::path &manifest) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (policy.engine != Engine::range_v1 &&
      policy.engine != Engine::treepack_v1) {
    return Status{ErrorCode::unsupported,
                  "sync manifests support range-v1 files and treepack-v1 artifacts"};
  }
  if (artifact.empty() || !artifact.is_absolute() || manifest.empty() ||
      !manifest.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "sync range manifest paths must be absolute"};
  }
  return Status::success();
}

} // namespace

Result<SyncRangeManifestInfo> build_sync_range_manifest(
    const NamespacePolicy &policy, const std::filesystem::path &artifact,
    const std::filesystem::path &output) {
  const Status valid = validate_common(policy, artifact, output);
  if (!valid.ok()) return valid;
  try {
    toxsync::IndexFileBuildOptions options;
    options.block_size = 0U;
    options.fsync_on_commit = true;
    options.limits = limits_for(policy);
    options.auto_block.metadata_budget_bytes =
        policy.quotas.maximum_manifest_bytes;
    options.auto_block.min_block_size = options.limits.min_block_size;
    options.auto_block.max_block_size = options.limits.max_block_size;
    const toxsync::IndexFileBuildStats built =
        toxsync::build_index_file(artifact, output, options);
    const std::uint64_t encoded = built.metadata.encoded_size();
    const Digest digest = from_toxsync(built.metadata.target_digest);
    if (built.metadata.target_size == 0U || all_zero(digest) ||
        encoded == 0U || encoded > policy.quotas.maximum_manifest_bytes ||
        built.metadata.target_size >
            policy.quotas.maximum_artifact_bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "built range-v1 manifest exceeds namespace quotas"};
    }
    return SyncRangeManifestInfo{
        digest, built.metadata.target_size, encoded,
        built.metadata.block_count, built.metadata.block_size};
  } catch (const std::exception &exception) {
    return Status{ErrorCode::io_error,
                  "unable to build range-v1 manifest: " +
                      std::string(exception.what())};
  }
}

Status verify_sync_range_manifest(
    const NamespacePolicy &policy, const std::filesystem::path &artifact,
    const std::filesystem::path &manifest, const Digest &expected_artifact,
    std::uint64_t expected_artifact_bytes,
    std::uint64_t expected_manifest_bytes) {
  const Status valid = validate_common(policy, artifact, manifest);
  if (!valid.ok()) return valid;
  if (all_zero(expected_artifact) || expected_artifact_bytes == 0U ||
      expected_manifest_bytes == 0U ||
      expected_artifact_bytes > policy.quotas.maximum_artifact_bytes ||
      expected_manifest_bytes > policy.quotas.maximum_manifest_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "range-v1 manifest expectation is invalid"};
  }
  try {
    const toxsync::IndexLimits limits = limits_for(policy);
    const toxsync::IndexFileMetadata metadata =
        toxsync::inspect_index_file(manifest, limits);
    std::error_code size_error;
    const std::uint64_t manifest_bytes =
        std::filesystem::file_size(manifest, size_error);
    if (size_error || manifest_bytes != expected_manifest_bytes ||
        metadata.encoded_size() != expected_manifest_bytes ||
        metadata.target_size != expected_artifact_bytes ||
        from_toxsync(metadata.target_digest) != expected_artifact ||
        !toxsync::verify_indexed_file(manifest, artifact, limits)) {
      return Status{ErrorCode::protocol_error,
                    "range-v1 manifest does not describe the exact immutable artifact"};
    }
    return Status::success();
  } catch (const std::exception &exception) {
    return Status{ErrorCode::protocol_error,
                  "range-v1 manifest validation failed: " +
                      std::string(exception.what())};
  }
}

} // namespace iotox::sync
