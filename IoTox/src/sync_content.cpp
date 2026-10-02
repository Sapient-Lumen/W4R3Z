#include "iotox/sync_content.hpp"

#include "iotox/sync_guarded_witness.hpp"

#include "iotox/sync_authorization.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_replica.hpp"
#include "iotox/sync_rollback.hpp"

#include "toxsync/content_fabric.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <exception>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <mutex>
#include <string>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

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

SyncContentObjectKind
from_toxsync(toxsync::ContentFabricObjectKind kind) noexcept {
  return kind == toxsync::ContentFabricObjectKind::manifest_page
             ? SyncContentObjectKind::manifest_page
             : SyncContentObjectKind::artifact_chunk;
}

SyncContentPhase from_toxsync(toxsync::ContentFabricPhase phase) noexcept {
  switch (phase) {
  case toxsync::ContentFabricPhase::unprepared:
    return SyncContentPhase::unprepared;
  case toxsync::ContentFabricPhase::manifest_pages:
    return SyncContentPhase::manifest_pages;
  case toxsync::ContentFabricPhase::artifact_chunks:
    return SyncContentPhase::artifact_chunks;
  case toxsync::ContentFabricPhase::complete:
    return SyncContentPhase::complete;
  }
  return SyncContentPhase::unprepared;
}

Status exception_status(std::string_view operation,
                        const std::exception &exception) {
  return Status{ErrorCode::io_error,
                std::string(operation) + ": " + exception.what()};
}

bool normalized_absolute(const std::filesystem::path &path) {
  return !path.empty() && path.is_absolute() && path.lexically_normal() == path;
}

int hex_nibble(char value) noexcept {
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return value - 'a' + 10;
  return -1;
}

Result<Digest> content_name_digest(std::string_view fanout,
                                   std::string_view leaf) {
  if (fanout.size() != 2U || leaf.size() != 62U) {
    return Status{ErrorCode::protocol_error,
                  "content store object name is not canonical"};
  }
  const std::string text = std::string(fanout) + std::string(leaf);
  Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    const int high = hex_nibble(text[index * 2U]);
    const int low = hex_nibble(text[index * 2U + 1U]);
    if (high < 0 || low < 0) {
      return Status{ErrorCode::protocol_error,
                    "content store object name is not lowercase hex"};
    }
    result[index] =
        static_cast<std::uint8_t>(static_cast<unsigned>(high * 16 + low));
  }
  return result;
}

Status inspect_content_directory(const std::filesystem::path &path,
                                 bool private_root,
                                 std::uint64_t expected_device = 0U) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content store directory: " +
                      std::string(std::strerror(errno))};
  }
  const mode_t mode = metadata.st_mode & static_cast<mode_t>(0777);
  if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() ||
      (expected_device != 0U &&
       static_cast<std::uint64_t>(metadata.st_dev) != expected_device) ||
      (private_root
           ? mode != static_cast<mode_t>(0700)
           : ((mode & static_cast<mode_t>(0700)) != static_cast<mode_t>(0700) ||
              (mode & static_cast<mode_t>(0022)) != 0))) {
    return Status{ErrorCode::protocol_error,
                  private_root
                      ? "content store root is not private and owner-owned"
                      : "content store fanout is not safe and owner-owned"};
  }
  return Status::success();
}

Result<std::uint64_t> inspect_content_file(const std::filesystem::path &path,
                                           std::uint64_t expected_device) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content store object: " +
                      std::string(std::strerror(errno))};
  }
  if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
      static_cast<std::uint64_t>(metadata.st_dev) != expected_device ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size <= 0) {
    return Status{ErrorCode::protocol_error,
                  "content store object is not one private owner-owned file"};
  }
  return static_cast<std::uint64_t>(metadata.st_size);
}

Status prepare_private_content_directory(const std::filesystem::path &path) {
  struct stat existing {};
  if (::lstat(path.c_str(), &existing) == 0) {
    return inspect_content_directory(path, true);
  }
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect private content directory: " +
                      std::string(std::strerror(errno))};
  }
  std::error_code error;
  std::filesystem::create_directory(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create private content directory: " +
                      error.message()};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure private content directory: " +
                      error.message()};
  }
  return inspect_content_directory(path, true);
}

bool path_beneath(const std::filesystem::path &root,
                  const std::filesystem::path &path) {
  if (!normalized_absolute(root) || !normalized_absolute(path))
    return false;
  const std::filesystem::path relative = path.lexically_relative(root);
  return !relative.empty() && !relative.is_absolute() &&
         *relative.begin() != "..";
}

} // namespace

std::filesystem::path sync_content_store_root(const NamespacePolicy &policy) {
  return std::filesystem::path(policy.root) / "content-v2";
}

std::filesystem::path sync_content_staging_root(const NamespacePolicy &policy) {
  return std::filesystem::path(policy.root) / "staging" / "content-v2";
}

std::filesystem::path sync_content_object_path(const NamespacePolicy &policy,
                                               const Digest &object) {
  return toxsync::content_store_path(sync_content_store_root(policy),
                                     to_toxsync(object));
}

Status prepare_sync_content_store(const NamespacePolicy &policy,
                                  const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content store requires content-v2 policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const std::filesystem::path root = sync_content_store_root(policy);
  return prepare_private_content_directory(root);
}

Status
prepare_sync_content_staging(const NamespacePolicy &policy,
                             const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content staging requires content-v2 policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status parent = prepare_private_content_directory(
      std::filesystem::path(policy.root) / "staging");
  if (!parent.ok())
    return parent;
  return prepare_private_content_directory(sync_content_staging_root(policy));
}

Result<SyncContentStoreInventory>
inspect_sync_content_store(const NamespacePolicy &policy, bool verify_objects) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  return inspect_sync_content_store(policy, transaction.value(),
                                    verify_objects);
}

Result<SyncContentStoreInventory>
inspect_sync_content_store(const NamespacePolicy &policy,
                           const SyncNamespaceTransaction &transaction,
                           bool verify_objects) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content store inventory requires content-v2 policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const std::filesystem::path root = sync_content_store_root(policy);
  struct stat root_metadata {};
  if (::lstat(root.c_str(), &root_metadata) != 0) {
    if (errno == ENOENT)
      return SyncContentStoreInventory{};
    return Status{ErrorCode::io_error,
                  "unable to inspect content store root: " +
                      std::string(std::strerror(errno))};
  }
  const Status root_valid = inspect_content_directory(root, true);
  if (!root_valid.ok())
    return root_valid;
  const std::uint64_t root_device =
      static_cast<std::uint64_t>(root_metadata.st_dev);

  SyncContentStoreInventory result;
  const std::filesystem::path algorithm_root = root / "sha256";
  bool found_algorithm = false;
  std::error_code root_error;
  for (std::filesystem::directory_iterator entry(root, root_error), end;
       !root_error && entry != end; entry.increment(root_error)) {
    if (found_algorithm || entry->path().filename() != "sha256") {
      return Status{ErrorCode::protocol_error,
                    "content store contains an unexpected algorithm entry"};
    }
    const Status algorithm_valid =
        inspect_content_directory(entry->path(), false, root_device);
    if (!algorithm_valid.ok())
      return algorithm_valid;
    found_algorithm = true;
  }
  if (root_error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate content store root: " +
                      root_error.message()};
  }
  if (!found_algorithm)
    return result;

  result.records.reserve(static_cast<std::size_t>(
      std::min<std::uint64_t>(policy.quotas.maximum_objects, 4096U)));
  std::size_t fanouts = 0U;
  std::error_code error;
  for (std::filesystem::directory_iterator outer(algorithm_root, error), end;
       !error && outer != end; outer.increment(error)) {
    if (++fanouts > 256U) {
      return Status{ErrorCode::resource_exhausted,
                    "content store fanout bound is exhausted"};
    }
    const std::string fanout = outer->path().filename().string();
    if (fanout.size() != 2U || hex_nibble(fanout[0U]) < 0 ||
        hex_nibble(fanout[1U]) < 0) {
      return Status{ErrorCode::protocol_error,
                    "content store contains an unexpected fanout"};
    }
    const Status fanout_valid =
        inspect_content_directory(outer->path(), false, root_device);
    if (!fanout_valid.ok())
      return fanout_valid;
    std::error_code inner_error;
    for (std::filesystem::directory_iterator inner(outer->path(), inner_error),
         inner_end;
         !inner_error && inner != inner_end; inner.increment(inner_error)) {
      if (result.objects >= policy.quotas.maximum_objects) {
        return Status{ErrorCode::resource_exhausted,
                      "content store object quota is exhausted"};
      }
      auto object =
          content_name_digest(fanout, inner->path().filename().string());
      if (!object)
        return object.status();
      auto bytes = inspect_content_file(inner->path(), root_device);
      if (!bytes)
        return bytes.status();
      if (bytes.value() > policy.quotas.maximum_store_bytes ||
          result.bytes > policy.quotas.maximum_store_bytes - bytes.value()) {
        return Status{ErrorCode::resource_exhausted,
                      "content store byte quota is exhausted"};
      }
      if (verify_objects) {
        auto observed = hash_sync_file_sha256(inner->path());
        if (!observed)
          return observed.status();
        if (observed.value() != object.value()) {
          return Status{ErrorCode::protocol_error,
                        "content store object digest conflicts with its name"};
        }
      }
      result.records.push_back(
          SyncContentStoredObject{object.value(), bytes.value()});
      ++result.objects;
      result.bytes += bytes.value();
    }
    if (inner_error) {
      return Status{ErrorCode::io_error,
                    "unable to enumerate content store fanout: " +
                        inner_error.message()};
    }
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate content store algorithm directory: " +
                      error.message()};
  }
  std::sort(result.records.begin(), result.records.end(),
            [](const SyncContentStoredObject &left,
               const SyncContentStoredObject &right) {
              return left.object < right.object;
            });
  if (std::adjacent_find(result.records.begin(), result.records.end(),
                         [](const SyncContentStoredObject &left,
                            const SyncContentStoredObject &right) {
                           return left.object == right.object;
                         }) != result.records.end()) {
    return Status{ErrorCode::protocol_error,
                  "content store duplicates an object identity"};
  }
  return result;
}

Result<SyncCombinedStoreInventory>
inspect_sync_combined_store(const NamespacePolicy &policy,
                            bool verify_content_objects) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  return inspect_sync_combined_store(policy, transaction.value(),
                                     verify_content_objects);
}

Result<SyncCombinedStoreInventory>
inspect_sync_combined_store(const NamespacePolicy &policy,
                            const SyncNamespaceTransaction &transaction,
                            bool verify_content_objects) {
  auto flat = inspect_sync_object_store(policy, transaction);
  if (!flat)
    return flat.status();
  auto content =
      inspect_sync_content_store(policy, transaction, verify_content_objects);
  if (!content)
    return content.status();
  if (flat.value().objects >
          policy.quotas.maximum_objects - content.value().objects ||
      flat.value().bytes >
          policy.quotas.maximum_store_bytes - content.value().bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "combined sync stores exceed namespace quotas"};
  }
  SyncCombinedStoreInventory result;
  result.flat = std::move(flat).value();
  result.content = std::move(content).value();
  result.objects = result.flat.objects + result.content.objects;
  result.bytes = result.flat.bytes + result.content.bytes;
  return result;
}

namespace {

struct ContentRevisionRoot {
  Digest artifact{};
  std::uint64_t artifact_bytes{0U};
  Digest manifest{};
  std::uint64_t manifest_bytes{0U};
  std::uint8_t source_mask{0U};
};

struct ContentFileIdentity {
  SyncContentStoredObject object;
  std::uint64_t device{0U};
  std::uint64_t inode{0U};
  std::uint64_t owner{0U};
  std::uint64_t group{0U};
  std::uint64_t links{0U};
  std::uint32_t mode{0U};
};

std::string content_digest_hex(const Digest &digest) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result;
  result.reserve(digest.size() * 2U);
  for (const std::uint8_t byte : digest) {
    result.push_back(digits[byte >> 4U]);
    result.push_back(digits[byte & 0x0fU]);
  }
  return result;
}

bool content_cancelled(const SyncContentMaintenanceSeams &seams) {
  return seams.cancel_requested && seams.cancel_requested();
}

Status sync_content_directory(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    return Status{ErrorCode::io_error,
                  "unable to open content maintenance directory: " +
                      std::string(std::strerror(errno))};
  }
  int synchronized = -1;
  do {
    synchronized = ::fsync(descriptor);
  } while (synchronized != 0 && errno == EINTR);
  const int saved = errno;
  static_cast<void>(::close(descriptor));
  if (synchronized != 0) {
    return Status{ErrorCode::io_error,
                  "unable to synchronize content maintenance directory: " +
                      std::string(std::strerror(saved))};
  }
  return Status::success();
}

Result<ContentFileIdentity>
capture_content_identity(const NamespacePolicy &policy,
                         const SyncContentStoredObject &object) {
  const std::filesystem::path path =
      sync_content_object_path(policy, object.object);
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content maintenance object: " +
                      std::string(std::strerror(errno))};
  }
  if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() || metadata.st_nlink != 1 ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size <= 0 ||
      static_cast<std::uint64_t>(metadata.st_size) != object.object_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content maintenance object identity is unsafe"};
  }
  return ContentFileIdentity{object,
                             static_cast<std::uint64_t>(metadata.st_dev),
                             static_cast<std::uint64_t>(metadata.st_ino),
                             static_cast<std::uint64_t>(metadata.st_uid),
                             static_cast<std::uint64_t>(metadata.st_gid),
                             static_cast<std::uint64_t>(metadata.st_nlink),
                             static_cast<std::uint32_t>(metadata.st_mode)};
}

bool same_content_identity(const struct stat &metadata,
                           const ContentFileIdentity &identity) noexcept {
  return S_ISREG(metadata.st_mode) && !S_ISLNK(metadata.st_mode) &&
         static_cast<std::uint64_t>(metadata.st_dev) == identity.device &&
         static_cast<std::uint64_t>(metadata.st_ino) == identity.inode &&
         static_cast<std::uint64_t>(metadata.st_uid) == identity.owner &&
         static_cast<std::uint64_t>(metadata.st_gid) == identity.group &&
         static_cast<std::uint64_t>(metadata.st_nlink) == identity.links &&
         static_cast<std::uint32_t>(metadata.st_mode) == identity.mode &&
         metadata.st_size > 0 &&
         static_cast<std::uint64_t>(metadata.st_size) ==
             identity.object.object_bytes;
}

Status add_content_expected(const NamespacePolicy &policy,
                            std::vector<SyncContentRootedObject> &expected,
                            const Digest &digest, std::uint64_t bytes,
                            std::uint8_t source_mask) {
  if (std::all_of(digest.begin(), digest.end(),
                  [](std::uint8_t byte) { return byte == 0U; }) ||
      bytes == 0U || bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content reachability root object is invalid"};
  }
  auto found = std::lower_bound(
      expected.begin(), expected.end(), digest,
      [](const SyncContentRootedObject &left, const Digest &right) {
        return left.object.object < right;
      });
  if (found != expected.end() && found->object.object == digest) {
    if (found->object.object_bytes != bytes) {
      return Status{ErrorCode::protocol_error,
                    "content roots disagree about one object size"};
    }
    found->source_mask |= source_mask;
    return Status::success();
  }
  if (expected.size() >= policy.quotas.maximum_objects) {
    return Status{ErrorCode::resource_exhausted,
                  "content live graph exceeds the object quota"};
  }
  expected.insert(
      found, SyncContentRootedObject{SyncContentStoredObject{digest, bytes},
                                     source_mask});
  return Status::success();
}

Status add_content_revision(const NamespacePolicy &policy,
                            std::vector<SyncContentRootedObject> &expected,
                            std::vector<ContentRevisionRoot> &revisions,
                            const Digest &artifact,
                            std::uint64_t artifact_bytes,
                            const Digest &manifest,
                            std::uint64_t manifest_bytes,
                            SyncContentRootSource source,
                            bool require_whole_artifact) {
  const std::uint8_t mask = static_cast<std::uint8_t>(source);
  Status added = Status::success();
  if (require_whole_artifact) {
    added =
        add_content_expected(policy, expected, artifact, artifact_bytes, mask);
    if (!added.ok())
      return added;
  }
  added =
      add_content_expected(policy, expected, manifest, manifest_bytes, mask);
  if (!added.ok())
    return added;
  auto existing = std::find_if(revisions.begin(), revisions.end(),
                               [&](const ContentRevisionRoot &root) {
                                 return root.manifest == manifest;
                               });
  if (existing != revisions.end()) {
    if (existing->manifest_bytes != manifest_bytes ||
        existing->artifact != artifact ||
        existing->artifact_bytes != artifact_bytes) {
      return Status{ErrorCode::protocol_error,
                    "content roots bind one manifest to conflicting artifacts"};
    }
    existing->source_mask |= mask;
  } else {
    revisions.push_back(ContentRevisionRoot{artifact, artifact_bytes, manifest,
                                            manifest_bytes, mask});
  }
  return Status::success();
}

const SyncContentStoredObject *
find_content_inventory(const std::vector<SyncContentStoredObject> &inventory,
                       const Digest &digest) {
  auto found =
      std::lower_bound(inventory.begin(), inventory.end(), digest,
                       [](const SyncContentStoredObject &left,
                          const Digest &right) { return left.object < right; });
  return found != inventory.end() && found->object == digest ? &*found
                                                             : nullptr;
}

Result<SyncContentReachabilityPlan> plan_content_reachability_in_transaction(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content reachability requires content-v2"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto inventory = inspect_sync_content_store(policy, transaction, false);
  if (!inventory)
    return inventory.status();
  auto roots =
      load_sync_rollback_roots(policy, expected_device, sodium, transaction);
  if (!roots)
    return roots.status();
  auto rollback =
      make_sync_rollback_head(policy, expected_device, roots.value(), sodium);
  if (!rollback)
    return rollback.status();
  SyncRollbackGuardStore guard(policy.root);
  auto guarded = guard.check(policy, rollback.value(), expected_device, sodium,
                             transaction);
  if (!guarded)
    return guarded.status();

  std::vector<SyncContentRootedObject> expected;
  std::vector<ContentRevisionRoot> revisions;
  const auto add_head = [&](const auto &head, SyncContentRootSource source,
                            bool require_whole_artifact) {
    return add_content_revision(
        policy, expected, revisions, head.artifact, head.artifact_bytes,
        head.manifest, head.manifest_bytes, source, require_whole_artifact);
  };
  Status added = Status::success();
  if (roots.value().published)
    added = add_head(*roots.value().published, SyncContentRootSource::published,
                     false);
  if (added.ok() && roots.value().accepted)
    added = add_head(*roots.value().accepted, SyncContentRootSource::accepted,
                     true);
  if (added.ok()) {
    ReplicaHeadStore replicas(policy.root);
    auto replica = replicas.load(policy, expected_device, sodium);
    if (!replica) return replica.status();
    if (replica.value()) {
      added = add_head(
          *replica.value(), SyncContentRootSource::replica, false);
    }
  }
  if (added.ok() && roots.value().activated) {
    added = add_content_expected(
        policy, expected, roots.value().activated->artifact,
        roots.value().activated->artifact_bytes,
        static_cast<std::uint8_t>(SyncContentRootSource::activated));
  }
  if (added.ok()) {
    for (const RetainedRevision &retained : roots.value().retained.revisions) {
      added = add_content_revision(policy, expected, revisions,
                                   retained.artifact, retained.artifact_bytes,
                                   retained.manifest, retained.manifest_bytes,
                                   SyncContentRootSource::retained, true);
      if (!added.ok())
        break;
    }
  }
  if (!added.ok())
    return added;

  bool traversal_complete = true;
  const std::filesystem::path store = sync_content_store_root(policy);
  for (const ContentRevisionRoot &revision : revisions) {
    const SyncContentStoredObject *root_inventory =
        find_content_inventory(inventory.value().records, revision.manifest);
    if (root_inventory == nullptr ||
        root_inventory->object_bytes != revision.manifest_bytes) {
      traversal_complete = false;
      continue;
    }
    const std::filesystem::path manifest =
        sync_content_object_path(policy, revision.manifest);
    auto observed_root = hash_sync_file_sha256(manifest);
    if (!observed_root || observed_root.value() != revision.manifest) {
      traversal_complete = false;
      continue;
    }
    try {
      std::uint64_t chunk_count = 0U;
      const toxsync::ContentManifestFormat format =
          toxsync::detect_content_manifest_format(manifest);
      if (format == toxsync::ContentManifestFormat::paged_v2) {
        const toxsync::PagedContentManifestMetadata metadata =
            toxsync::inspect_paged_content_manifest(manifest,
                                                    content_limits(policy));
        if (metadata.artifact_size != revision.artifact_bytes ||
            from_toxsync(metadata.artifact_digest) != revision.artifact ||
            metadata.encoded_size() != revision.manifest_bytes ||
            from_toxsync(metadata.root_digest) != revision.manifest) {
          return Status{ErrorCode::protocol_error,
                        "content root graph conflicts with signed revision"};
        }
        chunk_count = metadata.chunk_count;
        std::vector<toxsync::PagedContentPageRef> pages(
            std::min<std::uint64_t>(metadata.page_count, 256U));
        std::uint64_t first_page = 0U;
        bool pages_complete = true;
        while (first_page < metadata.page_count) {
          const std::size_t window =
              static_cast<std::size_t>(std::min<std::uint64_t>(
                  pages.size(), metadata.page_count - first_page));
          toxsync::PagedContentPageWindowOptions options;
          options.verify_root_manifest = true;
          options.root_buffer_bytes = std::min<std::size_t>(
              static_cast<std::size_t>(revision.manifest_bytes), 64U * 1024U);
          options.limits = content_limits(policy);
          const auto loaded = toxsync::read_paged_content_page_window(
              manifest, first_page,
              std::span<toxsync::PagedContentPageRef>{pages}.first(window),
              options);
          if (loaded.pages_loaded != window) {
            return Status{ErrorCode::protocol_error,
                          "content page graph window is incomplete"};
          }
          for (std::size_t index = 0U; index < window; ++index) {
            const Digest page_digest = from_toxsync(pages[index].digest);
            added = add_content_expected(policy, expected, page_digest,
                                         pages[index].encoded_size,
                                         revision.source_mask);
            if (!added.ok())
              return added;
            const SyncContentStoredObject *page_inventory =
                find_content_inventory(inventory.value().records, page_digest);
            if (page_inventory == nullptr ||
                page_inventory->object_bytes != pages[index].encoded_size ||
                !toxsync::content_object_available(
                    store, pages[index].digest, pages[index].encoded_size, true,
                    nullptr, 256U * 1024U)) {
              pages_complete = false;
            }
          }
          first_page = loaded.next_page;
        }
        if (!pages_complete) {
          traversal_complete = false;
          continue;
        }
      } else {
        const toxsync::ContentManifestMetadata metadata =
            toxsync::inspect_content_manifest(manifest, content_limits(policy));
        if (metadata.artifact_size != revision.artifact_bytes ||
            from_toxsync(metadata.artifact_digest) != revision.artifact ||
            metadata.encoded_size() != revision.manifest_bytes ||
            from_toxsync(metadata.manifest_digest) != revision.manifest) {
          return Status{
              ErrorCode::protocol_error,
              "content manifest graph conflicts with signed revision"};
        }
        chunk_count = metadata.chunk_count;
      }

      std::vector<toxsync::ContentChunkRef> chunks(
          std::min<std::uint64_t>(chunk_count, 256U));
      std::uint64_t first_chunk = 0U;
      std::uint64_t artifact_offset = 0U;
      while (first_chunk < chunk_count) {
        const std::size_t window = static_cast<std::size_t>(
            std::min<std::uint64_t>(chunks.size(), chunk_count - first_chunk));
        toxsync::ContentChunkWindowOptions options;
        options.artifact_offset_hint_valid = first_chunk != 0U;
        options.artifact_offset_hint = artifact_offset;
        options.verify_manifest = true;
        options.verify_page_digests = true;
        options.manifest_buffer_bytes = std::min<std::size_t>(
            static_cast<std::size_t>(revision.manifest_bytes), 64U * 1024U);
        options.limits = content_limits(policy);
        const auto loaded = toxsync::read_content_chunk_window(
            manifest, store, first_chunk,
            std::span<toxsync::ContentChunkRef>{chunks}.first(window), options);
        if (loaded.chunks_loaded != window ||
            loaded.artifact_size != revision.artifact_bytes ||
            from_toxsync(loaded.artifact_digest) != revision.artifact ||
            from_toxsync(loaded.manifest_digest) != revision.manifest) {
          return Status{ErrorCode::protocol_error,
                        "content chunk graph conflicts with signed revision"};
        }
        for (std::size_t index = 0U; index < window; ++index) {
          added = add_content_expected(
              policy, expected, from_toxsync(chunks[index].digest),
              chunks[index].length, revision.source_mask);
          if (!added.ok())
            return added;
        }
        first_chunk = loaded.next_chunk;
        artifact_offset = loaded.next_artifact_offset;
      }
    } catch (const std::exception &exception) {
      return exception_status("unable to walk content reachability graph",
                              exception);
    }
  }

  SyncContentReachabilityPlan plan;
  plan.traversal_complete = traversal_complete;
  plan.transaction_stable = true;
  plan.rollback_guard_consistent = true;
  for (const SyncContentRootedObject &root : expected) {
    const SyncContentStoredObject *found =
        find_content_inventory(inventory.value().records, root.object.object);
    if (found == nullptr) {
      constexpr std::uint8_t replica =
          static_cast<std::uint8_t>(SyncContentRootSource::replica);
      if ((root.source_mask & static_cast<std::uint8_t>(~replica)) != 0U)
        plan.missing.push_back(root);
    } else if (found->object_bytes != root.object.object_bytes) {
      plan.mismatched.push_back(
          SyncContentObjectMismatch{root, found->object_bytes});
    } else {
      plan.rooted.push_back(root);
      plan.rooted_bytes += root.object.object_bytes;
    }
  }
  if (traversal_complete) {
    for (const SyncContentStoredObject &object : inventory.value().records) {
      auto found = std::lower_bound(
          expected.begin(), expected.end(), object.object,
          [](const SyncContentRootedObject &left, const Digest &right) {
            return left.object.object < right;
          });
      if (found == expected.end() || found->object.object != object.object) {
        plan.unreferenced.push_back(object);
        plan.unreferenced_bytes += object.object_bytes;
      }
    }
  }
  return plan;
}

} // namespace

Result<SyncContentReachabilityPlan> plan_sync_content_reachability_from_store(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    std::shared_ptr<SyncGuardedStateWitness> witness) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  if (witness) {
    const Status verified = witness->verify_read(policy, transaction.value());
    if (!verified.ok()) return verified;
  }
  return plan_content_reachability_in_transaction(
      policy, expected_device, sodium, transaction.value());
}

Result<SyncContentRepairResult>
repair_sync_content_store(const NamespacePolicy &policy,
                          const SyncContentMaintenanceSeams &seams) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  auto inventory =
      inspect_sync_content_store(policy, transaction.value(), false);
  if (!inventory)
    return inventory.status();
  SyncContentRepairResult result;
  for (const SyncContentStoredObject &object : inventory.value().records) {
    if (content_cancelled(seams)) {
      return Status{ErrorCode::unavailable,
                    "content repair cancelled before quarantine"};
    }
    ++result.inspected_objects;
    result.inspected_bytes += object.object_bytes;
    auto digest =
        hash_sync_file_sha256(sync_content_object_path(policy, object.object));
    if (!digest)
      return digest.status();
    if (digest.value() == object.object) {
      ++result.verified_objects;
      continue;
    }
    result.quarantined.push_back(object);
    ++result.quarantined_objects;
    result.quarantined_bytes += object.object_bytes;
  }
  if (result.quarantined.empty())
    return result;
  const std::filesystem::path quarantine =
      std::filesystem::path(policy.root) / "content-quarantine";
  Status prepared = prepare_private_content_directory(quarantine);
  if (!prepared.ok())
    return prepared;
  for (std::size_t index = 0U; index < result.quarantined.size(); ++index) {
    const SyncContentStoredObject &object = result.quarantined[index];
    if (seams.before_move) {
      const Status injected = seams.before_move(index, object);
      if (!injected.ok())
        return injected;
    }
    auto identity = capture_content_identity(policy, object);
    if (!identity)
      return identity.status();
    const std::filesystem::path source =
        sync_content_object_path(policy, object.object);
    std::filesystem::path destination;
    for (std::uint64_t attempt = 1U; attempt <= 1024U; ++attempt) {
      const auto candidate =
          quarantine / (content_digest_hex(object.object) + ".corrupt-" +
                        std::to_string(attempt));
      struct stat existing {};
      if (::lstat(candidate.c_str(), &existing) != 0 && errno == ENOENT) {
        destination = candidate;
        break;
      }
    }
    if (destination.empty()) {
      return Status{ErrorCode::resource_exhausted,
                    "content repair quarantine name bound is exhausted"};
    }
    if (::syscall(SYS_renameat2, AT_FDCWD, source.c_str(), AT_FDCWD,
                  destination.c_str(), RENAME_NOREPLACE) != 0) {
      return Status{errno == ENOSYS ? ErrorCode::unsupported
                                    : ErrorCode::io_error,
                    "unable to quarantine corrupt content object: " +
                        std::string(std::strerror(errno))};
    }
    struct stat moved {};
    if (::lstat(destination.c_str(), &moved) != 0 ||
        !same_content_identity(moved, identity.value())) {
      return Status{ErrorCode::protocol_error,
                    "content repair moved an unexpected identity"};
    }
    prepared = sync_content_directory(source.parent_path());
    if (!prepared.ok())
      return prepared;
    prepared = sync_content_directory(quarantine);
    if (!prepared.ok())
      return prepared;
  }
  return result;
}

SyncContentGcOutcome quarantine_unreferenced_sync_content(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium, const SyncContentMaintenanceSeams &seams,
    std::shared_ptr<SyncGuardedStateWitness> witness) {
  SyncContentGcOutcome outcome;
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction) {
    outcome.status = transaction.status();
    return outcome;
  }
  if (witness) {
    const Status verified = witness->verify_read(policy, transaction.value());
    if (!verified.ok()) {
      outcome.status = verified;
      return outcome;
    }
  }
  auto plan = plan_content_reachability_in_transaction(
      policy, expected_device, sodium, transaction.value());
  if (!plan) {
    outcome.status = plan.status();
    return outcome;
  }
  outcome.plan.emplace(std::move(plan).value());
  if (!outcome.plan->consistent() || !outcome.plan->transaction_stable ||
      !outcome.plan->rollback_guard_consistent) {
    outcome.status = Status{
        ErrorCode::protocol_error,
        "content GC refuses quarantine while live-root evidence is incomplete"};
    return outcome;
  }
  if (outcome.plan->unreferenced.empty())
    return outcome;
  if (content_cancelled(seams)) {
    outcome.cancelled = true;
    outcome.status =
        Status{ErrorCode::unavailable, "content GC cancelled before mutation"};
    return outcome;
  }
  std::vector<ContentFileIdentity> identities;
  identities.reserve(outcome.plan->unreferenced.size());
  for (const SyncContentStoredObject &object : outcome.plan->unreferenced) {
    auto identity = capture_content_identity(policy, object);
    if (!identity) {
      outcome.status = identity.status();
      return outcome;
    }
    identities.push_back(std::move(identity).value());
  }
  auto unchanged =
      inspect_sync_content_store(policy, transaction.value(), false);
  if (!unchanged) {
    outcome.status = unchanged.status();
    return outcome;
  }
  const std::filesystem::path quarantine =
      std::filesystem::path(policy.root) / "content-gc-quarantine";
  struct stat prior {};
  const bool existed = ::lstat(quarantine.c_str(), &prior) == 0;
  Status prepared = prepare_private_content_directory(quarantine);
  if (!prepared.ok()) {
    outcome.status = prepared;
    return outcome;
  }
  outcome.quarantine_created = !existed;
  if (outcome.quarantine_created) {
    prepared = sync_content_directory(policy.root);
    if (!prepared.ok()) {
      outcome.status = prepared;
      return outcome;
    }
  }
  for (std::size_t index = 0U; index < identities.size(); ++index) {
    if (content_cancelled(seams)) {
      outcome.cancelled = true;
      outcome.status = Status{ErrorCode::unavailable,
                              "content GC cancelled during quarantine"};
      return outcome;
    }
    const ContentFileIdentity &identity = identities[index];
    if (seams.before_move) {
      const Status injected = seams.before_move(index, identity.object);
      if (!injected.ok()) {
        outcome.status = injected;
        return outcome;
      }
    }
    const std::filesystem::path source =
        sync_content_object_path(policy, identity.object.object);
    const std::filesystem::path destination =
        quarantine / content_digest_hex(identity.object.object);
    const int descriptor =
        ::open(source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    struct stat current {};
    if (descriptor < 0 || ::fstat(descriptor, &current) != 0 ||
        !same_content_identity(current, identity)) {
      if (descriptor >= 0)
        static_cast<void>(::close(descriptor));
      outcome.status = Status{ErrorCode::protocol_error,
                              "content GC candidate changed before move"};
      return outcome;
    }
    static_cast<void>(::close(descriptor));
    if (::syscall(SYS_renameat2, AT_FDCWD, source.c_str(), AT_FDCWD,
                  destination.c_str(), RENAME_NOREPLACE) != 0) {
      outcome.status =
          Status{errno == ENOSYS ? ErrorCode::unsupported : ErrorCode::io_error,
                 "unable to quarantine exact content GC candidate: " +
                     std::string(std::strerror(errno))};
      return outcome;
    }
    struct stat moved {};
    if (::lstat(destination.c_str(), &moved) != 0 ||
        !same_content_identity(moved, identity)) {
      outcome.status =
          Status{ErrorCode::protocol_error,
                 "content GC destination does not match frozen identity"};
      return outcome;
    }
    outcome.moved.push_back(identity.object);
    outcome.moved_bytes += identity.object.object_bytes;
    const Status source_synced = sync_content_directory(source.parent_path());
    const Status quarantine_synced = sync_content_directory(quarantine);
    if (!source_synced.ok() || !quarantine_synced.ok()) {
      outcome.status = !source_synced.ok() ? source_synced : quarantine_synced;
      return outcome;
    }
    ++outcome.durable_objects;
    outcome.durable_bytes += identity.object.object_bytes;
  }
  return outcome;
}

namespace {

struct ContentCommitAdmission {
  std::filesystem::path destination;
  bool destination_exists{false};
};

Result<ContentCommitAdmission>
admit_content_commit(const NamespacePolicy &policy, const Digest &object,
                     std::uint64_t object_bytes,
                     const std::filesystem::path &staging_path,
                     const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content commit requires content-v2 policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (std::all_of(object.begin(), object.end(),
                  [](std::uint8_t byte) { return byte == 0U; }) ||
      object_bytes == 0U ||
      object_bytes > policy.quotas.maximum_staging_bytes ||
      !path_beneath(sync_content_staging_root(policy), staging_path)) {
    return Status{ErrorCode::invalid_argument,
                  "content commit identity size or staging path is invalid"};
  }
  Status prepared = prepare_sync_content_store(policy, transaction);
  if (!prepared.ok())
    return prepared;
  prepared = prepare_sync_content_staging(policy, transaction);
  if (!prepared.ok())
    return prepared;
  struct stat root_metadata {};
  if (::lstat(policy.root.c_str(), &root_metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content namespace root: " +
                      std::string(std::strerror(errno))};
  }
  auto staged_bytes = inspect_content_file(
      staging_path, static_cast<std::uint64_t>(root_metadata.st_dev));
  if (!staged_bytes)
    return staged_bytes.status();
  if (staged_bytes.value() != object_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content staging size does not match its immutable identity"};
  }
  auto inventory = inspect_sync_combined_store(policy, transaction, false);
  if (!inventory)
    return inventory.status();
  ContentCommitAdmission result;
  result.destination = toxsync::content_store_path(
      sync_content_store_root(policy), to_toxsync(object));
  struct stat destination_metadata {};
  result.destination_exists =
      ::lstat(result.destination.c_str(), &destination_metadata) == 0;
  if (!result.destination_exists && errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content object destination: " +
                      std::string(std::strerror(errno))};
  }
  if (!result.destination_exists &&
      (inventory.value().objects >= policy.quotas.maximum_objects ||
       object_bytes > policy.quotas.maximum_store_bytes ||
       inventory.value().bytes >
           policy.quotas.maximum_store_bytes - object_bytes)) {
    return Status{
        ErrorCode::resource_exhausted,
        "content object commit would exceed combined namespace quotas"};
  }
  return result;
}

} // namespace

Result<SyncContentCommitResult>
commit_sync_content_staging(const NamespacePolicy &policy, const Digest &object,
                            std::uint64_t object_bytes,
                            const std::filesystem::path &staging_path,
                            const SyncNamespaceTransaction &transaction,
                            SyncContentCommitConfig config) {
  if (config.io_buffer_bytes == 0U ||
      config.io_buffer_bytes > policy.quotas.maximum_staging_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "content commit I/O buffer is outside policy bounds"};
  }
  auto admitted = admit_content_commit(policy, object, object_bytes,
                                       staging_path, transaction);
  if (!admitted)
    return admitted.status();
  try {
    toxsync::ContentObjectInstallOptions options;
    options.io_buffer_bytes = config.io_buffer_bytes;
    options.fsync_on_commit = config.fsync_on_commit;
    options.verify_existing_object = true;
    options.consume_source = true;
    options.prefer_hard_link = false;
    options.source_preverified = false;
    const toxsync::ContentObjectInstallStats installed =
        toxsync::install_content_object(
            staging_path, sync_content_store_root(policy), to_toxsync(object),
            object_bytes, options);
    const bool reused = installed.method ==
                        toxsync::ContentObjectInstallMethod::reused_existing;
    return SyncContentCommitResult{
        admitted.value().destination, object_bytes, installed.bytes_verified,
        installed.bytes_copied,       !reused,      reused};
  } catch (const std::exception &exception) {
    return exception_status("unable to commit content staging", exception);
  }
}

Result<SyncContentObjectDescriptor>
resolve_sync_content_object(const NamespacePolicy &policy,
                            const SignedHead &head, SyncContentObjectKind kind,
                            std::uint64_t logical_index) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (policy.engine != Engine::content_v2 ||
      head.engine != Engine::content_v2 || head.namespace_id != policy.id ||
      head.manifest_bytes == 0U || head.artifact_bytes == 0U) {
    return Status{
        ErrorCode::invalid_argument,
        "content object resolution requires a matching content-v2 HEAD"};
  }
  const SyncObjectRecord root_record{SyncObjectKind::manifest, head.manifest,
                                     head.manifest_bytes};
  const std::filesystem::path manifest = toxsync::content_store_path(
      sync_content_store_root(policy), to_toxsync(root_record.identity));
  std::error_code size_error;
  if (std::filesystem::file_size(manifest, size_error) != head.manifest_bytes ||
      size_error) {
    return Status{ErrorCode::not_found,
                  "content root manifest is absent or has the wrong size"};
  }
  auto manifest_digest = hash_sync_file_sha256(manifest);
  if (!manifest_digest || manifest_digest.value() != head.manifest) {
    return manifest_digest
               ? Status{ErrorCode::protocol_error,
                        "content root manifest digest conflicts with HEAD"}
               : manifest_digest.status();
  }
  if (kind == SyncContentObjectKind::root_manifest) {
    if (logical_index != 0U) {
      return Status{ErrorCode::not_found,
                    "content root manifest has only logical index zero"};
    }
    return SyncContentObjectDescriptor{kind, head.manifest, head.manifest_bytes,
                                       0U, manifest};
  }

  try {
    toxsync::Digest256 digest{};
    std::uint64_t bytes = 0U;
    const std::filesystem::path store = sync_content_store_root(policy);
    if (kind == SyncContentObjectKind::manifest_page) {
      if (toxsync::detect_content_manifest_format(manifest) !=
          toxsync::ContentManifestFormat::paged_v2) {
        return Status{ErrorCode::not_found,
                      "flat content manifest has no page objects"};
      }
      std::array<toxsync::PagedContentPageRef, 1U> page{};
      toxsync::PagedContentPageWindowOptions options;
      options.verify_root_manifest = true;
      options.root_buffer_bytes = std::min<std::size_t>(
          static_cast<std::size_t>(head.manifest_bytes), 64U * 1024U);
      options.limits = content_limits(policy);
      const auto loaded = toxsync::read_paged_content_page_window(
          manifest, logical_index, page, options);
      if (loaded.pages_loaded != 1U || page[0U].page_index != logical_index) {
        return Status{ErrorCode::not_found,
                      "content manifest page index is absent"};
      }
      if (from_toxsync(loaded.metadata.artifact_digest) != head.artifact ||
          loaded.metadata.artifact_size != head.artifact_bytes ||
          from_toxsync(loaded.metadata.root_digest) != head.manifest) {
        return Status{ErrorCode::protocol_error,
                      "content page root conflicts with signed HEAD"};
      }
      digest = page[0U].digest;
      bytes = page[0U].encoded_size;
    } else if (kind == SyncContentObjectKind::artifact_chunk) {
      std::array<toxsync::ContentChunkRef, 1U> chunk{};
      toxsync::ContentChunkWindowOptions options;
      options.verify_manifest = true;
      options.verify_page_digests = true;
      options.manifest_buffer_bytes = std::min<std::size_t>(
          static_cast<std::size_t>(head.manifest_bytes), 64U * 1024U);
      options.limits = content_limits(policy);
      const auto loaded = toxsync::read_content_chunk_window(
          manifest, store, logical_index, chunk, options);
      if (loaded.chunks_loaded != 1U || chunk[0U].index != logical_index) {
        return Status{ErrorCode::not_found,
                      "content artifact chunk index is absent"};
      }
      if (from_toxsync(loaded.artifact_digest) != head.artifact ||
          loaded.artifact_size != head.artifact_bytes ||
          from_toxsync(loaded.manifest_digest) != head.manifest) {
        return Status{ErrorCode::protocol_error,
                      "content chunk root conflicts with signed HEAD"};
      }
      digest = chunk[0U].digest;
      bytes = chunk[0U].length;
    } else {
      return Status{ErrorCode::invalid_argument,
                    "content object kind is invalid"};
    }
    const std::filesystem::path object =
        toxsync::content_store_path(store, digest);
    if (!toxsync::content_object_available(store, digest, bytes, true, nullptr,
                                           256U * 1024U)) {
      return Status{ErrorCode::not_found,
                    "content object is absent or corrupt"};
    }
    return SyncContentObjectDescriptor{kind, from_toxsync(digest), bytes,
                                       logical_index, object};
  } catch (const std::exception &exception) {
    return exception_status("unable to resolve content object", exception);
  }
}

Result<SyncContentAvailabilityDescriptor> resolve_sync_content_availability(
    const NamespacePolicy &policy, const SignedHead &head,
    SyncContentObjectKind kind, std::uint64_t first_object,
    std::uint32_t object_count) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (policy.engine != Engine::content_v2 ||
      head.engine != Engine::content_v2 || head.namespace_id != policy.id ||
      head.manifest_bytes == 0U || head.artifact_bytes == 0U ||
      object_count == 0U ||
      object_count > kSyncContentMaximumAvailabilityObjects) {
    return Status{
        ErrorCode::invalid_argument,
        "content availability requires a matching bounded content-v2 HEAD"};
  }
  const std::filesystem::path store = sync_content_store_root(policy);
  const std::filesystem::path manifest =
      toxsync::content_store_path(store, to_toxsync(head.manifest));
  std::error_code size_error;
  if (std::filesystem::file_size(manifest, size_error) != head.manifest_bytes ||
      size_error) {
    return Status{ErrorCode::not_found,
                  "content root manifest is absent or has the wrong size"};
  }
  auto digest = hash_sync_file_sha256(manifest);
  if (!digest || digest.value() != head.manifest) {
    return digest ? Status{ErrorCode::protocol_error,
                           "content root manifest digest conflicts with HEAD"}
                  : digest.status();
  }
  try {
    SyncContentAvailabilityDescriptor result;
    result.kind = kind;
    result.first_object = first_object;
    result.object_count = object_count;
    result.availability.assign(
        (static_cast<std::size_t>(object_count) + 7U) / 8U, 0U);
    auto bytes =
        std::as_writable_bytes(std::span<std::uint8_t>{result.availability});
    if (kind == SyncContentObjectKind::artifact_chunk) {
      const auto observed = toxsync::fill_content_availability(
          manifest, store, first_object, object_count, bytes, true, nullptr,
          content_limits(policy));
      if (observed.bit_count != object_count) {
        return Status{
            ErrorCode::not_found,
            "content chunk availability window is outside the manifest"};
      }
      result.available_objects = observed.available_count;
    } else if (kind == SyncContentObjectKind::manifest_page) {
      const auto observed = toxsync::fill_paged_content_page_availability(
          manifest, store, first_object, object_count, bytes, true, nullptr,
          content_limits(policy));
      if (observed.bit_count != object_count) {
        return Status{
            ErrorCode::not_found,
            "content page availability window is outside the manifest"};
      }
      result.available_objects = observed.available_count;
    } else {
      return Status{ErrorCode::invalid_argument,
                    "content availability object kind is invalid"};
    }
    return result;
  } catch (const std::exception &exception) {
    return exception_status("unable to resolve content availability",
                            exception);
  }
}

Status
verify_sync_content_revision(const NamespacePolicy &policy,
                             const AcceptedHead &head,
                             const std::filesystem::path &artifact,
                             const std::filesystem::path &root_manifest) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  const Status valid_head = validate_accepted_head(policy, head);
  if (!valid_head.ok())
    return valid_head;
  if (policy.engine != Engine::content_v2 ||
      head.engine != Engine::content_v2) {
    return Status{ErrorCode::invalid_argument,
                  "content revision verification requires content-v2"};
  }

  std::error_code error;
  if (std::filesystem::file_size(artifact, error) != head.artifact_bytes ||
      error) {
    return Status{ErrorCode::protocol_error,
                  "content artifact size conflicts with accepted HEAD"};
  }
  auto artifact_digest = hash_sync_file_sha256(artifact);
  if (!artifact_digest || artifact_digest.value() != head.artifact) {
    return artifact_digest
               ? Status{ErrorCode::protocol_error,
                        "content artifact digest conflicts with accepted HEAD"}
               : artifact_digest.status();
  }
  if (std::filesystem::file_size(root_manifest, error) != head.manifest_bytes ||
      error) {
    return Status{ErrorCode::protocol_error,
                  "content root manifest size conflicts with accepted HEAD"};
  }
  auto root_digest = hash_sync_file_sha256(root_manifest);
  if (!root_digest || root_digest.value() != head.manifest) {
    return root_digest ? Status{ErrorCode::protocol_error,
                                "content root manifest digest conflicts with "
                                "accepted HEAD"}
                       : root_digest.status();
  }

  try {
    const toxsync::ContentManifestFormat format =
        toxsync::detect_content_manifest_format(root_manifest);
    if (format == toxsync::ContentManifestFormat::paged_v2) {
      const toxsync::PagedContentManifestMetadata observed =
          toxsync::inspect_paged_content_manifest(root_manifest,
                                                  content_limits(policy));
      if (observed.artifact_size != head.artifact_bytes ||
          from_toxsync(observed.artifact_digest) != head.artifact ||
          observed.encoded_size() != head.manifest_bytes ||
          from_toxsync(observed.root_digest) != head.manifest) {
        return Status{
            ErrorCode::protocol_error,
            "paged content manifest semantics conflict with accepted HEAD"};
      }
    } else {
      const toxsync::ContentManifestMetadata observed =
          toxsync::inspect_content_manifest(root_manifest,
                                            content_limits(policy));
      if (observed.artifact_size != head.artifact_bytes ||
          from_toxsync(observed.artifact_digest) != head.artifact ||
          observed.encoded_size() != head.manifest_bytes ||
          from_toxsync(observed.manifest_digest) != head.manifest) {
        return Status{
            ErrorCode::protocol_error,
            "flat content manifest semantics conflict with accepted HEAD"};
      }
    }
    return Status::success();
  } catch (const std::exception &exception) {
    return exception_status("unable to verify content revision", exception);
  }
}

class SyncContentCoordinator::Impl final {
public:
  struct SourceBinding {
    SyncContentSource source;
    PrincipalId principal{};
    bool complete_window{false};
  };

  Impl(NamespacePolicy configured, AcceptedHead expected,
       std::filesystem::path manifest, std::filesystem::path store,
       std::filesystem::path staging, SyncContentConfig requested)
      : policy(std::move(configured)), expected_head(std::move(expected)),
        manifest_path(std::move(manifest)),
        content_store_root(std::move(store)), staging_root(std::move(staging)),
        config(requested) {}

  Status validate() const {
    const Status valid_policy = validate_namespace_policy(policy);
    if (!valid_policy.ok())
      return valid_policy;
    if (policy.engine != Engine::content_v2) {
      return Status{ErrorCode::unsupported,
                    "content coordinator requires content-v2 policy"};
    }
    const Status valid_head = validate_accepted_head(policy, expected_head);
    if (!valid_head.ok())
      return valid_head;
    if (!normalized_absolute(manifest_path) ||
        !normalized_absolute(content_store_root) ||
        !normalized_absolute(staging_root) ||
        content_store_root != sync_content_store_root(policy) ||
        staging_root != sync_content_staging_root(policy) ||
        content_store_root == staging_root) {
      return Status{
          ErrorCode::invalid_argument,
          "content coordinator paths must use the canonical namespace roots"};
    }
    if (config.maximum_window_objects == 0U ||
        config.maximum_page_window_objects == 0U ||
        config.workspace_budget_bytes == 0U ||
        config.object_io_buffer_bytes == 0U ||
        config.manifest_buffer_bytes == 0U ||
        policy.quotas.maximum_peers == 0U ||
        policy.quotas.maximum_lanes == 0U ||
        policy.quotas.maximum_outstanding_requests == 0U ||
        policy.quotas.maximum_objects == 0U ||
        policy.quotas.maximum_peers > std::numeric_limits<std::size_t>::max() ||
        policy.quotas.maximum_objects >
            std::numeric_limits<std::size_t>::max() ||
        policy.quotas.maximum_outstanding_requests >
            std::numeric_limits<std::size_t>::max() ||
        policy.quotas.maximum_lanes >
            std::numeric_limits<std::uint16_t>::max()) {
      return Status{ErrorCode::invalid_argument,
                    "content coordinator bounds are invalid"};
    }
    return Status::success();
  }

  toxsync::ContentFabricConfig fabric_config() const {
    toxsync::ContentFabricConfig result;
    result.chunk_window_objects = std::min<std::size_t>(
        config.maximum_window_objects,
        static_cast<std::size_t>(policy.quotas.maximum_objects));
    result.page_window_objects = std::min<std::size_t>(
        config.maximum_page_window_objects,
        static_cast<std::size_t>(policy.quotas.maximum_objects));
    result.scheduler.maximum_peers =
        static_cast<std::size_t>(policy.quotas.maximum_peers);
    result.scheduler.maximum_window_chunks =
        std::max(result.chunk_window_objects, result.page_window_objects);
    result.scheduler.maximum_lanes_per_peer =
        static_cast<std::uint16_t>(policy.quotas.maximum_lanes);
    result.scheduler.maximum_attempts_per_chunk = 8U;
    result.scheduler.maximum_inflight_requests =
        static_cast<std::size_t>(policy.quotas.maximum_outstanding_requests);
    result.scheduler.workspace_budget_bytes = config.workspace_budget_bytes;
    result.verify_manifest = true;
    result.verify_page_digests = true;
    result.verify_local_objects = config.verify_local_objects;
    result.fsync_on_commit = config.fsync_on_commit;
    result.prefer_hard_link_ingest = false;
    result.object_io_buffer_bytes = config.object_io_buffer_bytes;
    result.manifest_buffer_bytes = config.manifest_buffer_bytes;
    result.limits.max_artifact_size = policy.quotas.maximum_artifact_bytes;
    result.limits.max_chunks = policy.quotas.maximum_objects;
    result.limits.max_chunk_bytes = static_cast<std::uint32_t>(
        std::min<std::uint64_t>(policy.quotas.maximum_artifact_bytes,
                                std::numeric_limits<std::uint32_t>::max()));
    return result;
  }

  std::optional<std::size_t>
  binding_index(SyncContentSourceId source_id) const {
    const auto found =
        std::find_if(sources.begin(), sources.end(),
                     [source_id](const SourceBinding &binding) {
                       return binding.source.source_id == source_id;
                     });
    return found == sources.end()
               ? std::nullopt
               : std::optional<std::size_t>{
                     static_cast<std::size_t>(found - sources.begin())};
  }

  std::optional<std::size_t> assignment_index(std::uint64_t request_id) const {
    const auto found =
        std::find_if(active.begin(), active.end(),
                     [request_id](const SyncContentAssignment &assignment) {
                       return assignment.request_id == request_id;
                     });
    return found == active.end()
               ? std::nullopt
               : std::optional<std::size_t>{
                     static_cast<std::size_t>(found - active.begin())};
  }

  SyncContentAssignment
  convert(const toxsync::ContentFabricAssignment &assignment) const {
    return SyncContentAssignment{
        assignment.request_id,         assignment.peer_id,
        from_toxsync(assignment.kind), from_toxsync(assignment.object),
        assignment.object_size,        assignment.logical_index,
        assignment.staging_path};
  }

  NamespacePolicy policy;
  AcceptedHead expected_head;
  std::filesystem::path manifest_path;
  std::filesystem::path content_store_root;
  std::filesystem::path staging_root;
  SyncContentConfig config;
  std::unique_ptr<toxsync::ContentFabricSession> fabric;
  std::vector<SourceBinding> sources;
  std::vector<SyncContentAssignment> active;
  std::uint64_t fenced_requests{0U};
  mutable std::mutex mutex;
};

SyncContentCoordinator::SyncContentCoordinator(
    NamespacePolicy policy, AcceptedHead expected_head,
    std::filesystem::path manifest_path,
    std::filesystem::path content_store_root,
    std::filesystem::path staging_root, SyncContentConfig config)
    : impl_(std::make_unique<Impl>(
          std::move(policy), std::move(expected_head), std::move(manifest_path),
          std::move(content_store_root), std::move(staging_root), config)) {}

SyncContentCoordinator::~SyncContentCoordinator() = default;
SyncContentCoordinator::SyncContentCoordinator(
    SyncContentCoordinator &&) noexcept = default;
SyncContentCoordinator &
SyncContentCoordinator::operator=(SyncContentCoordinator &&) noexcept = default;

Status SyncContentCoordinator::prepare() {
  std::scoped_lock lock(impl_->mutex);
  const Status valid = impl_->validate();
  if (!valid.ok())
    return valid;
  if (impl_->fabric) {
    return Status{ErrorCode::invalid_argument,
                  "content coordinator is already prepared"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(impl_->policy);
  if (!transaction)
    return transaction.status();
  Status prepared =
      prepare_sync_content_store(impl_->policy, transaction.value());
  if (!prepared.ok())
    return prepared;
  prepared = prepare_sync_content_staging(impl_->policy, transaction.value());
  if (!prepared.ok())
    return prepared;
  auto inventory = inspect_sync_combined_store(
      impl_->policy, transaction.value(), impl_->config.verify_local_objects);
  if (!inventory)
    return inventory.status();
  std::error_code size_error;
  const std::uint64_t manifest_bytes =
      std::filesystem::file_size(impl_->manifest_path, size_error);
  if (size_error || manifest_bytes != impl_->expected_head.manifest_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content root manifest size does not match frozen HEAD"};
  }
  auto digest = hash_sync_file_sha256(impl_->manifest_path);
  if (!digest || digest.value() != impl_->expected_head.manifest) {
    return digest ? Status{ErrorCode::protocol_error,
                           "content root manifest digest does not match frozen "
                           "HEAD"}
                  : digest.status();
  }
  try {
    auto fabric = std::make_unique<toxsync::ContentFabricSession>(
        impl_->manifest_path, impl_->content_store_root, impl_->staging_root,
        impl_->fabric_config());
    fabric->prepare();
    const toxsync::ContentFabricStats observed = fabric->stats();
    if (from_toxsync(observed.artifact_digest) !=
            impl_->expected_head.artifact ||
        observed.artifact_size != impl_->expected_head.artifact_bytes ||
        from_toxsync(observed.manifest_digest) !=
            impl_->expected_head.manifest) {
      return Status{ErrorCode::protocol_error,
                    "content manifest semantics do not match frozen HEAD"};
    }
    impl_->fabric = std::move(fabric);
    return Status::success();
  } catch (const std::exception &exception) {
    return exception_status("unable to prepare content coordinator", exception);
  }
}

Status SyncContentCoordinator::upsert_complete_source(
    const SyncContentSource &source,
    const security::AuthoritySnapshot &current_authority) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  if (!source.content_transfer_negotiated || source.source_id == 0U ||
      source.maximum_lanes == 0U ||
      source.maximum_lanes > impl_->policy.quotas.maximum_lanes) {
    return Status{ErrorCode::invalid_argument,
                  "content source identity or lane bound is invalid"};
  }
  const SyncContentSourceAuthorizationResult admitted =
      evaluate_sync_content_source(impl_->policy, impl_->expected_head,
                                   source.advertised_head_record,
                                   current_authority, source.authority);
  if (!admitted.authorized()) {
    return Status{
        ErrorCode::unavailable,
        "content source authorization refused: " +
            std::string(sync_content_source_decision_name(admitted.decision))};
  }
  const auto existing = impl_->binding_index(source.source_id);
  if (existing.has_value()) {
    const Impl::SourceBinding &binding = impl_->sources[*existing];
    if (binding.principal != source.authority.remote_principal ||
        binding.source.advertised_head_record !=
            source.advertised_head_record) {
      return Status{ErrorCode::protocol_error,
                    "content source id cannot be rebound"};
    }
  } else if (impl_->sources.size() >= impl_->policy.quotas.maximum_peers) {
    return Status{ErrorCode::resource_exhausted,
                  "content source bound is exhausted"};
  }
  try {
    impl_->fabric->update_peer_complete_window(toxsync::SourcePeerUpdate{
        source.source_id, source.maximum_lanes, source.useful_bytes_per_second,
        source.recent_failures});
    if (existing.has_value()) {
      impl_->sources[*existing].source = source;
      impl_->sources[*existing].complete_window = true;
    } else {
      impl_->sources.push_back(
          Impl::SourceBinding{source, source.authority.remote_principal, true});
    }
    return Status::success();
  } catch (const std::exception &exception) {
    return exception_status("unable to update content source", exception);
  }
}

Status SyncContentCoordinator::upsert_source_window(
    const SyncContentSource &source,
    const security::AuthoritySnapshot &current_authority,
    SyncContentObjectKind kind, std::uint64_t first_object,
    std::uint32_t object_count, std::span<const std::uint8_t> availability) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  if (!source.content_transfer_negotiated || source.source_id == 0U ||
      source.maximum_lanes == 0U ||
      source.maximum_lanes > impl_->policy.quotas.maximum_lanes) {
    return Status{ErrorCode::invalid_argument,
                  "content source identity or lane bound is invalid"};
  }
  const SyncContentSourceAuthorizationResult admitted =
      evaluate_sync_content_source(impl_->policy, impl_->expected_head,
                                   source.advertised_head_record,
                                   current_authority, source.authority);
  if (!admitted.authorized()) {
    return Status{
        ErrorCode::unavailable,
        "content source authorization refused: " +
            std::string(sync_content_source_decision_name(admitted.decision))};
  }
  const toxsync::ContentFabricWindow window = impl_->fabric->window();
  const std::size_t required_bytes =
      (static_cast<std::size_t>(object_count) + 7U) / 8U;
  const SyncContentObjectKind current_kind = from_toxsync(window.kind);
  if (object_count == 0U || kind != current_kind ||
      first_object != window.first_object ||
      object_count != window.object_count ||
      availability.size() != required_bytes) {
    return Status{
        ErrorCode::protocol_error,
        "content source availability does not match the current window"};
  }
  const std::uint32_t remainder = object_count % 8U;
  if (remainder != 0U) {
    const std::uint8_t allowed = static_cast<std::uint8_t>(
        (std::uint32_t{1U} << remainder) - std::uint32_t{1U});
    if ((availability.back() & static_cast<std::uint8_t>(~allowed)) != 0U) {
      return Status{ErrorCode::protocol_error,
                    "content source availability tail bits are nonzero"};
    }
  }
  const auto existing = impl_->binding_index(source.source_id);
  if (existing.has_value()) {
    const Impl::SourceBinding &binding = impl_->sources[*existing];
    if (binding.principal != source.authority.remote_principal ||
        binding.source.advertised_head_record !=
            source.advertised_head_record) {
      return Status{ErrorCode::protocol_error,
                    "content source id cannot be rebound"};
    }
  } else if (impl_->sources.size() >= impl_->policy.quotas.maximum_peers) {
    return Status{ErrorCode::resource_exhausted,
                  "content source bound is exhausted"};
  }
  try {
    impl_->fabric->update_peer(
        toxsync::SourcePeerUpdate{source.source_id, source.maximum_lanes,
                                  source.useful_bytes_per_second,
                                  source.recent_failures},
        first_object, object_count, std::as_bytes(availability));
    if (existing.has_value()) {
      impl_->sources[*existing].source = source;
      impl_->sources[*existing].complete_window = false;
    } else {
      impl_->sources.push_back(Impl::SourceBinding{
          source, source.authority.remote_principal, false});
    }
    return Status::success();
  } catch (const std::exception &exception) {
    return exception_status("unable to update content source availability",
                            exception);
  }
}

Result<std::vector<SyncContentAssignment>>
SyncContentCoordinator::remove_source(SyncContentSourceId source_id) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  const auto binding = impl_->binding_index(source_id);
  if (!binding.has_value()) {
    return std::vector<SyncContentAssignment>{};
  }
  std::vector<SyncContentAssignment> fenced;
  for (const SyncContentAssignment &assignment : impl_->active) {
    if (assignment.source_id == source_id)
      fenced.push_back(assignment);
  }
  impl_->fabric->remove_peer(source_id);
  impl_->active.erase(
      std::remove_if(impl_->active.begin(), impl_->active.end(),
                     [source_id](const SyncContentAssignment &assignment) {
                       return assignment.source_id == source_id;
                     }),
      impl_->active.end());
  impl_->sources.erase(impl_->sources.begin() +
                       static_cast<std::ptrdiff_t>(*binding));
  impl_->fenced_requests += fenced.size();
  return fenced;
}

Result<std::optional<SyncContentAssignment>>
SyncContentCoordinator::next(std::uint64_t request_id) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  if (impl_->assignment_index(request_id).has_value()) {
    return Status{ErrorCode::invalid_argument,
                  "content request id is already active"};
  }
  try {
    const auto assigned = impl_->fabric->next(request_id);
    if (!assigned)
      return std::optional<SyncContentAssignment>{};
    SyncContentAssignment result = impl_->convert(*assigned);
    impl_->active.push_back(result);
    return std::optional<SyncContentAssignment>{std::move(result)};
  } catch (const std::exception &exception) {
    return exception_status("unable to assign content object", exception);
  }
}

std::optional<SyncContentAssignment>
SyncContentCoordinator::assignment(std::uint64_t request_id) const {
  std::scoped_lock lock(impl_->mutex);
  const auto found = impl_->assignment_index(request_id);
  return found.has_value()
             ? std::optional<SyncContentAssignment>{impl_->active[*found]}
             : std::nullopt;
}

Status SyncContentCoordinator::commit(
    std::uint64_t request_id,
    const std::filesystem::path &completed_staging_path) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  const auto active = impl_->assignment_index(request_id);
  if (!active.has_value()) {
    return Status{ErrorCode::not_found, "content request is not active"};
  }
  const SyncContentAssignment assignment = impl_->active[*active];
  const std::filesystem::path staging = completed_staging_path.empty()
                                            ? assignment.staging_path
                                            : completed_staging_path;
  if (staging != assignment.staging_path ||
      !path_beneath(impl_->staging_root, staging)) {
    return Status{ErrorCode::protocol_error,
                  "content completion path does not match its assignment"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(impl_->policy);
  if (!transaction)
    return transaction.status();
  auto admitted = admit_content_commit(impl_->policy, assignment.object,
                                       assignment.object_bytes, staging,
                                       transaction.value());
  if (!admitted)
    return admitted.status();
  try {
    static_cast<void>(impl_->fabric->commit(request_id, staging, false));
    impl_->active.erase(impl_->active.begin() +
                        static_cast<std::ptrdiff_t>(*active));
    return Status::success();
  } catch (const std::exception &exception) {
    impl_->active.erase(impl_->active.begin() +
                        static_cast<std::ptrdiff_t>(*active));
    return exception_status("unable to commit content object", exception);
  }
}

Status SyncContentCoordinator::fail(std::uint64_t request_id,
                                    SyncContentFailure failure) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  const auto active = impl_->assignment_index(request_id);
  if (!active.has_value()) {
    return Status{ErrorCode::not_found, "content request is not active"};
  }
  toxsync::SourceFailureDisposition disposition =
      toxsync::SourceFailureDisposition::retry_source;
  if (failure == SyncContentFailure::object_absent) {
    disposition = toxsync::SourceFailureDisposition::remove_source_for_chunk;
  } else if (failure == SyncContentFailure::permanent) {
    disposition = toxsync::SourceFailureDisposition::permanent;
  }
  if (!impl_->fabric->fail(request_id, disposition)) {
    return Status{ErrorCode::internal_error,
                  "content fabric did not retain the active request"};
  }
  impl_->active.erase(impl_->active.begin() +
                      static_cast<std::ptrdiff_t>(*active));
  return Status::success();
}

Result<bool> SyncContentCoordinator::advance_window() {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric) {
    return Status{ErrorCode::unavailable,
                  "content coordinator is not prepared"};
  }
  if (!impl_->active.empty()) {
    return Status{ErrorCode::unavailable,
                  "content window still has active requests"};
  }
  try {
    const bool advanced = impl_->fabric->advance_window();
    if (advanced && !impl_->fabric->complete()) {
      for (const Impl::SourceBinding &binding : impl_->sources) {
        if (!binding.complete_window)
          continue;
        const SyncContentSource &source = binding.source;
        impl_->fabric->update_peer_complete_window(toxsync::SourcePeerUpdate{
            source.source_id, source.maximum_lanes,
            source.useful_bytes_per_second, source.recent_failures});
      }
    }
    return advanced;
  } catch (const std::exception &exception) {
    return exception_status("unable to advance content window", exception);
  }
}

bool SyncContentCoordinator::complete() const {
  std::scoped_lock lock(impl_->mutex);
  return impl_->fabric && impl_->fabric->complete();
}

Result<SyncContentReconstruction>
SyncContentCoordinator::reconstruct(const std::filesystem::path &output_path) {
  std::scoped_lock lock(impl_->mutex);
  if (!impl_->fabric || !impl_->fabric->complete() ||
      !normalized_absolute(output_path)) {
    return Status{ErrorCode::invalid_argument,
                  "content reconstruction requires complete state and an "
                  "absolute output"};
  }
  try {
    toxsync::ContentReconstructOptions options;
    options.io_buffer_bytes = impl_->config.object_io_buffer_bytes;
    options.manifest_buffer_bytes = impl_->config.manifest_buffer_bytes;
    options.fsync_on_commit = impl_->config.fsync_on_commit;
    options.limits = impl_->fabric_config().limits;
    const toxsync::ContentReconstructStats rebuilt =
        impl_->fabric->reconstruct(output_path, options);
    if (from_toxsync(rebuilt.metadata.artifact_digest) !=
            impl_->expected_head.artifact ||
        rebuilt.metadata.artifact_size != impl_->expected_head.artifact_bytes) {
      return Status{ErrorCode::protocol_error,
                    "reconstructed content does not match frozen HEAD"};
    }
    return SyncContentReconstruction{
        from_toxsync(rebuilt.metadata.artifact_digest),
        rebuilt.metadata.artifact_size, rebuilt.chunks_read};
  } catch (const std::exception &exception) {
    return exception_status("unable to reconstruct content", exception);
  }
}

SyncContentSnapshot SyncContentCoordinator::snapshot() const {
  std::scoped_lock lock(impl_->mutex);
  SyncContentSnapshot result;
  result.sources = impl_->sources.size();
  result.active_requests = impl_->active.size();
  result.fenced_requests = impl_->fenced_requests;
  if (!impl_->fabric)
    return result;
  const toxsync::ContentFabricStats observed = impl_->fabric->stats();
  result.phase = from_toxsync(observed.phase);
  result.assignments = observed.requests_issued;
  result.request_failures = observed.request_failures;
  result.verification_failures = observed.verification_failures;
  result.page_objects_reused = observed.page_objects_reused;
  result.page_objects_fetched = observed.page_objects_fetched;
  result.chunk_objects_reused = observed.chunk_objects_reused;
  result.chunk_objects_fetched = observed.chunk_objects_fetched;
  result.chunk_bytes_reused = observed.chunk_bytes_reused;
  result.chunk_bytes_fetched = observed.chunk_bytes_fetched;
  result.resident_bytes = observed.resident_bytes;
  result.window_kind = from_toxsync(observed.window.kind);
  result.window_first_object = observed.window.first_object;
  result.window_object_count = observed.window.object_count;
  return result;
}

std::string_view sync_content_phase_name(SyncContentPhase phase) noexcept {
  switch (phase) {
  case SyncContentPhase::unprepared:
    return "unprepared";
  case SyncContentPhase::manifest_pages:
    return "manifest-pages";
  case SyncContentPhase::artifact_chunks:
    return "artifact-chunks";
  case SyncContentPhase::complete:
    return "complete";
  }
  return "unknown";
}

} // namespace iotox::sync
