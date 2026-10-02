#include "iotox/sync_content_publication.hpp"

#include "iotox/sync_content_workspace.hpp"

#include "toxsync/content_store.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <exception>
#include <limits>
#include <string>
#include <sys/stat.h>
#include <utility>
#include <vector>

namespace iotox::sync {
namespace {

struct PublicationObject {
  Digest digest{};
  std::uint64_t bytes{0U};
};

class WorkspaceRemoval final {
public:
  WorkspaceRemoval(const NamespacePolicy &policy,
                   const SyncNamespaceTransaction &transaction,
                   std::filesystem::path path)
      : policy_(&policy), transaction_(&transaction), path_(std::move(path)) {}
  ~WorkspaceRemoval() {
    if (!path_.empty()) {
      static_cast<void>(remove_sync_content_workspace(
          *policy_, *transaction_, SyncContentWorkspaceClass::publication,
          path_));
    }
  }
  WorkspaceRemoval(const WorkspaceRemoval &) = delete;
  WorkspaceRemoval &operator=(const WorkspaceRemoval &) = delete;

private:
  const NamespacePolicy *policy_{nullptr};
  const SyncNamespaceTransaction *transaction_{nullptr};
  std::filesystem::path path_;
};

bool cancelled(const SyncContentPublicationSeams &seams) {
  return seams.cancel_requested && seams.cancel_requested();
}

Digest from_toxsync(const toxsync::Digest256 &digest) noexcept {
  Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    result[index] = std::to_integer<std::uint8_t>(digest.bytes[index]);
  }
  return result;
}

toxsync::Digest256 to_toxsync(const Digest &digest) noexcept {
  toxsync::Digest256 result{};
  for (std::size_t index = 0U; index < digest.size(); ++index) {
    result.bytes[index] = static_cast<std::byte>(digest[index]);
  }
  return result;
}

toxsync::ContentStoreLimits
content_limits(const NamespacePolicy &policy) noexcept {
  toxsync::ContentStoreLimits result;
  result.max_artifact_size = policy.quotas.maximum_artifact_bytes;
  result.max_chunks = policy.quotas.maximum_objects;
  result.max_chunk_bytes = static_cast<std::uint32_t>(
      std::min<std::uint64_t>(policy.quotas.maximum_artifact_bytes,
                              std::numeric_limits<std::uint32_t>::max()));
  return result;
}

Status validate_config(const NamespacePolicy &policy,
                       const SyncContentPublicationConfig &config) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2 ||
      (config.format != SyncContentPublicationFormat::automatic &&
       config.format != SyncContentPublicationFormat::flat &&
       config.format != SyncContentPublicationFormat::paged) ||
      config.minimum_chunk_bytes < 1024U ||
      config.minimum_chunk_bytes > config.average_chunk_bytes ||
      config.average_chunk_bytes > config.maximum_chunk_bytes ||
      config.maximum_chunk_bytes == 0U ||
      config.maximum_chunk_bytes > policy.quotas.maximum_artifact_bytes ||
      config.maximum_chunk_bytes > policy.quotas.maximum_staging_bytes ||
      config.entries_per_page == 0U || config.entries_per_page > 65536U ||
      config.io_buffer_bytes == 0U ||
      config.io_buffer_bytes > policy.quotas.maximum_staging_bytes ||
      config.manifest_buffer_bytes == 0U ||
      config.manifest_buffer_bytes > policy.quotas.maximum_manifest_bytes ||
      config.workspace_budget_bytes == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "content publication configuration is invalid"};
  }
  const std::uint64_t basic_workspace =
      static_cast<std::uint64_t>(config.maximum_chunk_bytes) +
      config.io_buffer_bytes + config.manifest_buffer_bytes;
  const std::uint64_t page_workspace =
      static_cast<std::uint64_t>(config.maximum_chunk_bytes) +
      config.io_buffer_bytes + config.manifest_buffer_bytes + 96U +
      static_cast<std::uint64_t>(config.entries_per_page) * 40U;
  if (basic_workspace > config.workspace_budget_bytes ||
      (config.format != SyncContentPublicationFormat::flat &&
       page_workspace > config.workspace_budget_bytes)) {
    return Status{ErrorCode::resource_exhausted,
                  "content publication workspace exceeds its memory budget"};
  }
  return Status::success();
}

bool same_snapshot(const struct stat &left, const struct stat &right) noexcept {
  return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
         left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
         left.st_uid == right.st_uid && left.st_size == right.st_size &&
         left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
         left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
         left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
         left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

void collect_chunk(void *context, const toxsync::ContentChunkRef &chunk) {
  auto *objects = static_cast<std::vector<PublicationObject> *>(context);
  objects->push_back(
      PublicationObject{from_toxsync(chunk.digest), chunk.length});
}

void collect_page(void *context, const toxsync::PagedContentPageRef &page) {
  auto *objects = static_cast<std::vector<PublicationObject> *>(context);
  objects->push_back(
      PublicationObject{from_toxsync(page.digest), page.encoded_size});
}

Status canonicalize_objects(std::vector<PublicationObject> &objects,
                            const NamespacePolicy &policy,
                            std::uint64_t &total_bytes) {
  std::sort(objects.begin(), objects.end(),
            [](const PublicationObject &left, const PublicationObject &right) {
              if (left.digest != right.digest)
                return left.digest < right.digest;
              return left.bytes < right.bytes;
            });
  std::vector<PublicationObject> unique;
  unique.reserve(objects.size());
  for (const PublicationObject &object : objects) {
    if (object.bytes == 0U) {
      return Status{ErrorCode::protocol_error,
                    "content publication described an empty object"};
    }
    if (!unique.empty() && unique.back().digest == object.digest) {
      if (unique.back().bytes != object.bytes) {
        return Status{ErrorCode::protocol_error,
                      "content publication reused a digest at two sizes"};
      }
      continue;
    }
    if (object.bytes >
        std::numeric_limits<std::uint64_t>::max() - total_bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "content publication object-byte total overflows"};
    }
    total_bytes += object.bytes;
    unique.push_back(object);
  }
  if (unique.size() > policy.quotas.maximum_objects ||
      total_bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "content publication object set exceeds namespace quota"};
  }
  objects = std::move(unique);
  return Status::success();
}

Status prospective_admission(const NamespacePolicy &policy,
                             const SyncCombinedStoreInventory &inventory,
                             const std::vector<PublicationObject> &objects) {
  std::uint64_t additional_objects = 0U;
  std::uint64_t additional_bytes = 0U;
  for (const PublicationObject &object : objects) {
    const auto found = std::lower_bound(
        inventory.content.records.begin(), inventory.content.records.end(),
        object.digest,
        [](const SyncContentStoredObject &record, const Digest &digest) {
          return record.object < digest;
        });
    if (found != inventory.content.records.end() &&
        found->object == object.digest) {
      if (found->object_bytes != object.bytes) {
        return Status{ErrorCode::protocol_error,
                      "content publication object size conflicts with CAS"};
      }
      continue;
    }
    if (additional_objects == std::numeric_limits<std::uint64_t>::max() ||
        object.bytes >
            std::numeric_limits<std::uint64_t>::max() - additional_bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "content publication admission totals overflow"};
    }
    ++additional_objects;
    additional_bytes += object.bytes;
  }
  if (additional_objects > policy.quotas.maximum_objects ||
      additional_bytes > policy.quotas.maximum_store_bytes ||
      inventory.objects > policy.quotas.maximum_objects - additional_objects ||
      inventory.bytes > policy.quotas.maximum_store_bytes - additional_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "content publication would exceed combined namespace quota"};
  }
  return Status::success();
}

} // namespace

Result<std::size_t> cleanup_sync_content_publication_staging(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  return cleanup_sync_content_workspaces(
      policy, transaction, SyncContentWorkspaceClass::publication);
}

Result<SyncContentPublicationResult> publish_local_content_revision(
    const NamespacePolicy &policy, const std::filesystem::path &artifact_source,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    SignedHeadStore &head_store, SyncContentPublicationConfig config,
    SyncContentPublicationSeams seams) {
  const Status configured = validate_config(policy, config);
  if (!configured.ok())
    return configured;
  if (artifact_source.empty() || !artifact_source.is_absolute() ||
      artifact_source.lexically_normal() != artifact_source) {
    return Status{
        ErrorCode::invalid_argument,
        "content publication source must be one normalized absolute path"};
  }
  struct stat source_metadata {};
  if (::lstat(artifact_source.c_str(), &source_metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content publication source: " +
                      std::string(std::strerror(errno))};
  }
  if (!S_ISREG(source_metadata.st_mode) || S_ISLNK(source_metadata.st_mode) ||
      source_metadata.st_size <= 0 ||
      static_cast<std::uint64_t>(source_metadata.st_size) >
          policy.quotas.maximum_artifact_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "content publication source is not one bounded regular file"};
  }
  if (!std::binary_search(policy.writers.begin(), policy.writers.end(),
                          identity.public_key())) {
    return Status{ErrorCode::invalid_argument,
                  "local device is not a writer for the content namespace"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  auto prior = head_store.load(policy, sodium, transaction.value());
  if (!prior)
    return prior.status();
  if (prior.value().has_value() &&
      prior.value()->writer != identity.public_key()) {
    return Status{ErrorCode::invalid_argument,
                  "content namespace predecessor belongs to another writer"};
  }
  const Status store_prepared =
      prepare_sync_content_store(policy, transaction.value());
  if (!store_prepared.ok())
    return store_prepared;
  const Status staging_prepared =
      prepare_sync_content_staging(policy, transaction.value());
  if (!staging_prepared.ok())
    return staging_prepared;
  auto removed =
      cleanup_sync_content_publication_staging(policy, transaction.value());
  if (!removed)
    return removed.status();
  auto workspace = create_sync_content_workspace(
      policy, transaction.value(), SyncContentWorkspaceClass::publication);
  if (!workspace)
    return workspace.status();
  WorkspaceRemoval remove_workspace(policy, transaction.value(),
                                    workspace.value());
  const std::filesystem::path scratch_store = workspace.value() / "store";
  const std::filesystem::path manifest_path =
      workspace.value() / "root.manifest";

  SyncContentPublicationResult result;
  std::vector<PublicationObject> objects;
  toxsync::ContentStoreWorkspace build_workspace;
  const toxsync::ContentStoreLimits limits = content_limits(policy);
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "content publication cancelled before build"};
  }
  try {
    SyncContentPublicationFormat format = config.format;
    if (format == SyncContentPublicationFormat::automatic) {
      toxsync::ContentChunkingAutoOptions automatic;
      automatic.metadata_budget_bytes = policy.quotas.maximum_manifest_bytes;
      automatic.preferred = {config.minimum_chunk_bytes,
                             config.average_chunk_bytes,
                             config.maximum_chunk_bytes};
      const auto estimate = toxsync::estimate_content_scale(
          static_cast<std::uint64_t>(source_metadata.st_size), automatic,
          limits);
      format = estimate.maximum_manifest_bytes <=
                           policy.quotas.maximum_manifest_bytes &&
                       estimate.maximum_chunks < policy.quotas.maximum_objects
                   ? SyncContentPublicationFormat::flat
                   : SyncContentPublicationFormat::paged;
    }
    if (format == SyncContentPublicationFormat::flat) {
      toxsync::ContentStoreOptions options;
      options.chunking = {config.minimum_chunk_bytes,
                          config.average_chunk_bytes,
                          config.maximum_chunk_bytes};
      options.auto_chunking = true;
      options.metadata_budget_bytes = policy.quotas.maximum_manifest_bytes;
      options.io_buffer_bytes = config.io_buffer_bytes;
      options.manifest_buffer_bytes = config.manifest_buffer_bytes;
      options.fsync_on_commit = config.fsync_on_commit;
      options.publish_manifest_to_store = true;
      options.verify_existing_chunks = true;
      options.limits = limits;
      const auto built =
          toxsync::build_content_store(artifact_source, scratch_store,
                                       manifest_path, build_workspace, options);
      result.format = SyncContentPublicationFormat::flat;
      result.artifact = from_toxsync(built.metadata.artifact_digest);
      result.manifest = from_toxsync(built.metadata.manifest_digest);
      result.artifact_bytes = built.metadata.artifact_size;
      result.manifest_bytes = built.metadata.encoded_size();
      result.chunks = built.metadata.chunk_count;
      toxsync::ContentManifestWalkOptions walk;
      walk.manifest_buffer_bytes = config.manifest_buffer_bytes;
      walk.limits = limits;
      const auto visited = toxsync::walk_content_manifest(
          manifest_path, build_workspace, collect_chunk, &objects, walk);
      if (visited.chunks_visited != result.chunks ||
          visited.bytes_visited != result.artifact_bytes) {
        return Status{ErrorCode::protocol_error,
                      "content publication flat manifest walk changed"};
      }
    } else {
      toxsync::PagedContentStoreOptions options;
      options.chunking = {config.minimum_chunk_bytes,
                          config.average_chunk_bytes,
                          config.maximum_chunk_bytes};
      options.auto_chunking = true;
      options.root_metadata_budget_bytes = policy.quotas.maximum_manifest_bytes;
      options.entries_per_page = config.entries_per_page;
      options.io_buffer_bytes = config.io_buffer_bytes;
      options.root_buffer_bytes = config.manifest_buffer_bytes;
      options.fsync_on_commit = config.fsync_on_commit;
      options.publish_root_to_store = true;
      options.verify_existing_objects = true;
      options.limits = limits;
      const auto built = toxsync::build_paged_content_store(
          artifact_source, scratch_store, manifest_path, build_workspace,
          options);
      result.format = SyncContentPublicationFormat::paged;
      result.artifact = from_toxsync(built.metadata.artifact_digest);
      result.manifest = from_toxsync(built.metadata.root_digest);
      result.artifact_bytes = built.metadata.artifact_size;
      result.manifest_bytes = built.metadata.encoded_size();
      result.chunks = built.metadata.chunk_count;
      result.pages = built.metadata.page_count;
      toxsync::PagedContentManifestWalkOptions walk;
      walk.verify_page_digests = true;
      walk.manifest_buffer_bytes = config.manifest_buffer_bytes;
      walk.limits = limits;
      const auto visited = toxsync::walk_paged_content_manifest(
          manifest_path, scratch_store, build_workspace, collect_page, &objects,
          collect_chunk, &objects, walk);
      if (visited.pages_visited != result.pages ||
          visited.chunks_visited != result.chunks ||
          visited.artifact_bytes_visited != result.artifact_bytes) {
        return Status{ErrorCode::protocol_error,
                      "content publication paged manifest walk changed"};
      }
    }
  } catch (const std::exception &exception) {
    return Status{ErrorCode::io_error, "unable to build content publication: " +
                                           std::string(exception.what())};
  }
  struct stat source_after {};
  if (::lstat(artifact_source.c_str(), &source_after) != 0 ||
      !same_snapshot(source_metadata, source_after)) {
    return Status{ErrorCode::protocol_error,
                  "content publication source changed while indexed"};
  }
  result.workspace_reserved_bytes = build_workspace.resident_bytes();
  if (result.workspace_reserved_bytes > config.workspace_budget_bytes ||
      result.manifest_bytes == 0U ||
      result.manifest_bytes > policy.quotas.maximum_manifest_bytes) {
    return Status{
        ErrorCode::resource_exhausted,
        "content publication exceeded its bounded workspace or manifest"};
  }
  objects.push_back(PublicationObject{result.manifest, result.manifest_bytes});
  std::uint64_t unique_bytes = 0U;
  const Status canonical = canonicalize_objects(objects, policy, unique_bytes);
  if (!canonical.ok())
    return canonical;
  result.unique_objects = objects.size();
  result.unique_object_bytes = unique_bytes;
  if (unique_bytes > policy.quotas.maximum_staging_bytes ||
      result.manifest_bytes >
          policy.quotas.maximum_staging_bytes - unique_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "content publication scratch set exceeds staging quota"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "content publication cancelled before CAS admission"};
  }
  auto inventory =
      inspect_sync_combined_store(policy, transaction.value(), true);
  if (!inventory)
    return inventory.status();
  const Status admitted =
      prospective_admission(policy, inventory.value(), objects);
  if (!admitted.ok())
    return admitted;

  SyncContentCommitConfig commit_config;
  commit_config.io_buffer_bytes = config.io_buffer_bytes;
  commit_config.fsync_on_commit = config.fsync_on_commit;
  for (const PublicationObject &object : objects) {
    if (cancelled(seams)) {
      return Status{ErrorCode::unavailable,
                    "content publication cancelled before HEAD commit"};
    }
    const std::filesystem::path source =
        toxsync::content_store_path(scratch_store, to_toxsync(object.digest));
    auto committed =
        commit_sync_content_staging(policy, object.digest, object.bytes, source,
                                    transaction.value(), commit_config);
    if (!committed)
      return committed.status();
    result.objects_installed += committed.value().installed ? 1U : 0U;
    result.objects_reused += committed.value().reused ? 1U : 0U;
    if (committed.value().bytes_copied >
        std::numeric_limits<std::uint64_t>::max() - result.bytes_copied) {
      return Status{ErrorCode::resource_exhausted,
                    "content publication copied-byte counter overflow"};
    }
    result.bytes_copied += committed.value().bytes_copied;
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "content publication cancelled before signed HEAD"};
  }
  auto published =
      head_store.publish(policy,
                         SignedHeadPublicationRequest{
                             result.artifact, result.manifest,
                             result.artifact_bytes, result.manifest_bytes},
                         identity, sodium, transaction.value());
  if (!published)
    return published.status();
  result.publication = std::move(published).value();
  return result;
}

} // namespace iotox::sync
