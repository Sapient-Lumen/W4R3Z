#include "iotox/sync_tree.hpp"

#include "iotox/sync_digest.hpp"
#include "toxsync/treepack.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::sync {
namespace {

std::atomic<std::uint64_t> g_tree_sequence{1U};

class ExactPathCleanup {
public:
  explicit ExactPathCleanup(std::filesystem::path path)
      : path_(std::move(path)) {}
  ~ExactPathCleanup() {
    if (!armed_)
      return;
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  ExactPathCleanup(const ExactPathCleanup &) = delete;
  ExactPathCleanup &operator=(const ExactPathCleanup &) = delete;
  void release() noexcept { armed_ = false; }

private:
  std::filesystem::path path_;
  bool armed_{true};
};

[[nodiscard]] Status system_status(std::string_view operation,
                                   const std::filesystem::path &path,
                                   int error = errno) {
  return Status{ErrorCode::io_error,
                std::string(operation) + " " + path.string() + ": " +
                    std::strerror(error)};
}

[[nodiscard]] std::string hex(std::span<const std::uint8_t> bytes) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(bytes.size() * 2U);
  for (const std::uint8_t byte : bytes) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

[[nodiscard]] Result<toxsync::TreePackLimits>
limits_for(const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::treepack_v1) {
    return Status{ErrorCode::unsupported,
                  "treepack operation requires a treepack-v1 namespace"};
  }
  const std::uint64_t entries = std::min<std::uint64_t>(
      policy.quotas.maximum_objects, kMaximumTreepackEntries);
  constexpr std::uint64_t per_path =
      sizeof(std::string) + kMaximumTreepackPathBytes;
  if (entries >
      (std::numeric_limits<std::uint64_t>::max() - 1U) / per_path) {
    return Status{ErrorCode::resource_exhausted,
                  "treepack sort-memory bound overflows"};
  }
  const std::uint64_t sort_bytes = entries * per_path + 1U;
  if (sort_bytes > policy.quotas.maximum_staging_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "treepack path population exceeds staging memory quota"};
  }
  toxsync::TreePackLimits limits;
  limits.max_entries = entries;
  limits.max_file_size = policy.quotas.maximum_artifact_bytes;
  limits.max_artifact_bytes = policy.quotas.maximum_artifact_bytes;
  limits.max_path_bytes = kMaximumTreepackPathBytes;
  // This exact upper bound keeps the production adapter on treepack's
  // in-memory canonical sort path; no system temporary directory is used.
  limits.sort_memory_bytes = sort_bytes;
  limits.max_open_sort_runs = 2U;
  return limits;
}

[[nodiscard]] Status require_private_source(
    const std::filesystem::path &source,
    const toxsync::TreePackLimits &limits) {
  struct stat root {};
  if (::lstat(source.c_str(), &root) != 0) {
    return system_status("unable to inspect treepack source", source);
  }
  if (!S_ISDIR(root.st_mode) || root.st_uid != ::geteuid() ||
      (root.st_mode & 0022U) != 0U) {
    return Status{ErrorCode::protocol_error,
                  "treepack source root must be an owner-controlled directory"};
  }
  std::uint64_t entries = 0U;
  try {
    for (std::filesystem::recursive_directory_iterator iterator(source), end;
         iterator != end; ++iterator) {
      struct stat metadata {};
      if (::lstat(iterator->path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect treepack source entry",
                             iterator->path());
      }
      if (metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0022U) != 0U ||
          (!S_ISDIR(metadata.st_mode) &&
           (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1))) {
        return Status{ErrorCode::protocol_error,
                      "treepack source contains a mutable, linked, or special entry"};
      }
      ++entries;
      if (entries > limits.max_entries) {
        return Status{ErrorCode::resource_exhausted,
                      "treepack source entry population exceeds quota"};
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate treepack source: " +
                      std::string(error.what())};
  }
  return Status::success();
}

[[nodiscard]] Status require_reserved_output(
    const std::filesystem::path &output) {
  struct stat metadata {};
  if (::lstat(output.c_str(), &metadata) != 0) {
    return system_status("unable to inspect reserved treepack output", output);
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      metadata.st_nlink != 1 || (metadata.st_mode & 0777U) != 0600U) {
    return Status{ErrorCode::protocol_error,
                  "reserved treepack output is not one private owner file"};
  }
  return Status::success();
}

[[nodiscard]] Status ensure_private_directory(
    const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create tree activation directory: " +
                      error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "tree activation path is not a real owner directory"};
  }
  if (::chmod(path.c_str(), 0700) != 0) {
    return system_status("unable to secure tree activation directory", path);
  }
  return Status::success();
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0)
    return system_status("unable to open tree activation directory", path);
  const int result = ::fsync(descriptor);
  const int saved = errno;
  static_cast<void>(::close(descriptor));
  return result == 0
      ? Status::success()
      : system_status("unable to sync tree activation directory", path, saved);
}

[[nodiscard]] bool canonical_decimal(std::string_view value) noexcept {
  if (value.empty() || value.front() < '1' || value.front() > '9')
    return false;
  return std::all_of(value.begin() + 1, value.end(), [](char byte) {
    return byte >= '0' && byte <= '9';
  });
}

[[nodiscard]] bool canonical_digest(std::string_view value) noexcept {
  return value.size() == Digest{}.size() * 2U &&
         std::all_of(value.begin(), value.end(), [](char byte) {
           return (byte >= '0' && byte <= '9') ||
                  (byte >= 'a' && byte <= 'f');
         });
}

[[nodiscard]] bool canonical_revision_name(std::string_view value) noexcept {
  const std::size_t separator = value.find('-');
  return separator != std::string_view::npos &&
         canonical_decimal(value.substr(0U, separator)) &&
         canonical_digest(value.substr(separator + 1U));
}

[[nodiscard]] bool canonical_staging_name(std::string_view value) noexcept {
  if (!value.starts_with('.'))
    return false;
  value.remove_prefix(1U);
  constexpr std::string_view marker = ".part.";
  const std::size_t marker_offset = value.find(marker);
  if (marker_offset == std::string_view::npos ||
      !canonical_revision_name(value.substr(0U, marker_offset))) {
    return false;
  }
  value.remove_prefix(marker_offset + marker.size());
  const std::size_t separator = value.find('.');
  return separator != std::string_view::npos &&
         value.find('.', separator + 1U) == std::string_view::npos &&
         canonical_decimal(value.substr(0U, separator)) &&
         canonical_decimal(value.substr(separator + 1U));
}

[[nodiscard]] bool
canonical_pointer_staging_name(std::string_view value) noexcept {
  constexpr std::string_view prefix = ".current.part.";
  if (!value.starts_with(prefix))
    return false;
  value.remove_prefix(prefix.size());
  const std::size_t separator = value.find('.');
  return separator != std::string_view::npos &&
         value.find('.', separator + 1U) == std::string_view::npos &&
         canonical_decimal(value.substr(0U, separator)) &&
         canonical_decimal(value.substr(separator + 1U));
}

[[nodiscard]] bool
canonical_pointer_target(const std::filesystem::path &target) {
  return !target.empty() && !target.is_absolute() &&
         target == target.lexically_normal() &&
         target.parent_path() == std::filesystem::path("revisions") &&
         canonical_revision_name(target.filename().string());
}

[[nodiscard]] Status require_owned_tree_directory(
    const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0)
    return system_status("unable to inspect materialized tree directory", path);
  if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & 0022U) != 0U) {
    return Status{ErrorCode::protocol_error,
                  "materialized tree directory shape is unsafe"};
  }
  return Status::success();
}

[[nodiscard]] Result<std::uint64_t> recover_pointer_temporaries(
    const std::filesystem::path &activation, std::uint64_t maximum_entries) {
  std::vector<std::filesystem::path> abandoned;
  try {
    for (const auto &entry : std::filesystem::directory_iterator(activation)) {
      const std::string name = entry.path().filename().string();
      struct stat metadata {};
      if (::lstat(entry.path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect tree activation entry",
                             entry.path());
      }
      if (name == "revisions") {
        const Status safe = require_owned_tree_directory(entry.path());
        if (!safe.ok())
          return safe;
        continue;
      }
      if (name == "current") {
        if (!S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
          return Status{ErrorCode::protocol_error,
                        "tree activation current pointer is unsafe"};
        }
        continue;
      }
      if (!canonical_pointer_staging_name(name)) {
        return Status{ErrorCode::protocol_error,
                      "tree activation directory contains an ambiguous entry"};
      }
      if (!S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::protocol_error,
                      "tree activation pointer temporary is unsafe"};
      }
      std::error_code error;
      const std::filesystem::path target =
          std::filesystem::read_symlink(entry.path(), error);
      if (error || !canonical_pointer_target(target)) {
        return Status{ErrorCode::protocol_error,
                      "tree activation pointer temporary target is invalid"};
      }
      if (abandoned.size() >= maximum_entries) {
        return Status{ErrorCode::resource_exhausted,
                      "tree activation pointer temporary population exceeds quota"};
      }
      abandoned.push_back(entry.path());
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect tree activation directory: " +
                      std::string(error.what())};
  }

  // Classification is complete before the first unlink, matching stale-tree
  // cleanup: an ambiguous neighbor cannot turn recovery into a partial effect.
  for (const auto &path : abandoned) {
    if (::unlink(path.c_str()) != 0) {
      return system_status("unable to remove tree pointer temporary", path);
    }
  }
  if (!abandoned.empty()) {
    const Status synced = sync_directory(activation);
    if (!synced.ok())
      return synced;
  }
  return static_cast<std::uint64_t>(abandoned.size());
}

[[nodiscard]] Status projection_point(
    const SyncTreeProjectionSeams &seams, SyncTreeProjectionPoint point) {
  return seams.after_step ? seams.after_step(point) : Status::success();
}

[[nodiscard]] Status prepare_owned_tree_for_removal(
    const std::filesystem::path &root) {
  std::vector<std::filesystem::path> directories;
  directories.push_back(root);
  try {
    for (std::filesystem::recursive_directory_iterator iterator(root), end;
         iterator != end; ++iterator) {
      struct stat metadata {};
      if (::lstat(iterator->path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect stale materialized tree entry",
                             iterator->path());
      }
      if (metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0022U) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "stale materialized tree entry has unsafe ownership or permissions"};
      }
      if (S_ISDIR(metadata.st_mode)) {
        directories.push_back(iterator->path());
        continue;
      }
      if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1) {
        return Status{ErrorCode::protocol_error,
                      "stale materialized tree contains a linked or special entry"};
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to validate stale materialized tree: " +
                      std::string(error.what())};
  }

  // Validation is deliberately complete before permissions are changed. The
  // tree is derived, owner-only state; write permission is needed only on its
  // directories so remove_all can unlink their children without weakening the
  // frozen regular files themselves.
  for (const auto &directory : directories) {
    if (::chmod(directory.c_str(), 0700) != 0) {
      return system_status("unable to prepare stale materialized tree",
                           directory);
    }
  }
  return Status::success();
}

[[nodiscard]] Result<std::uint64_t> remove_materialized_directories(
    const std::filesystem::path &revisions, std::string_view keep_revision,
    bool staging_only, std::uint64_t maximum_entries) {
  struct Candidate {
    std::filesystem::path path;
    bool remove{false};
  };
  std::vector<Candidate> candidates;
  std::uint64_t removed = 0U;
  try {
    for (const auto &entry : std::filesystem::directory_iterator(revisions)) {
      const std::string name = entry.path().filename().string();
      const bool staging = canonical_staging_name(name);
      const bool revision_name = canonical_revision_name(name);
      if (!staging && !revision_name) {
        return Status{ErrorCode::protocol_error,
                      "materialized tree revision directory contains an ambiguous entry"};
      }
      const Status safe = require_owned_tree_directory(entry.path());
      if (!safe.ok())
        return safe;
      const bool remove = staging ||
          (!staging_only && name != keep_revision);
      // One complete predecessor plus the candidate is a normal atomic-switch
      // state, so revision projection admits one transient entry beyond the
      // namespace's immutable-object population.
      if (candidates.size() >= maximum_entries + 1U) {
        return Status{ErrorCode::resource_exhausted,
                      "materialized tree revision population exceeds quota"};
      }
      candidates.push_back(Candidate{entry.path(), remove});
    }

    // Do not mutate anything until every top-level entry is classified. Then
    // validate every selected subtree before deleting the first one, so an
    // ambiguous or linked neighbor cannot turn cleanup into a partial effect.
    for (const Candidate &candidate : candidates) {
      if (!candidate.remove)
        continue;
      const Status prepared = prepare_owned_tree_for_removal(candidate.path);
      if (!prepared.ok())
        return prepared;
    }
    for (const Candidate &candidate : candidates) {
      if (!candidate.remove)
        continue;
      std::error_code error;
      const std::uintmax_t count =
          std::filesystem::remove_all(candidate.path, error);
      if (error || count == 0U) {
        return Status{ErrorCode::io_error,
                      "unable to remove stale materialized tree: " +
                          error.message()};
      }
      ++removed;
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect materialized tree revisions: " +
                      std::string(error.what())};
  }
  if (removed != 0U) {
    const Status synced = sync_directory(revisions);
    if (!synced.ok())
      return synced;
  }
  return removed;
}

[[nodiscard]] Status freeze_and_sync_tree(
    const std::filesystem::path &root) {
  std::vector<std::filesystem::path> directories;
  directories.push_back(root);
  try {
    for (std::filesystem::recursive_directory_iterator iterator(root), end;
         iterator != end; ++iterator) {
      struct stat metadata {};
      if (::lstat(iterator->path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect materialized tree entry",
                             iterator->path());
      }
      if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::protocol_error,
                      "materialized tree contains a foreign-owned entry"};
      }
      if (S_ISDIR(metadata.st_mode)) {
        directories.push_back(iterator->path());
        continue;
      }
      if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1) {
        return Status{ErrorCode::protocol_error,
                      "materialized tree contains an unsafe entry"};
      }
      const mode_t mode = (metadata.st_mode & S_IXUSR) != 0 ? 0500 : 0400;
      if (::chmod(iterator->path().c_str(), mode) != 0) {
        return system_status("unable to freeze materialized tree file",
                             iterator->path());
      }
      const int descriptor = ::open(
          iterator->path().c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
      if (descriptor < 0) {
        return system_status("unable to open materialized tree file",
                             iterator->path());
      }
      const int synced = ::fsync(descriptor);
      const int saved = errno;
      static_cast<void>(::close(descriptor));
      if (synced != 0) {
        return system_status("unable to sync materialized tree file",
                             iterator->path(), saved);
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to freeze materialized tree: " +
                      std::string(error.what())};
  }
  std::reverse(directories.begin(), directories.end());
  for (const auto &directory : directories) {
    if (::chmod(directory.c_str(), 0500) != 0) {
      return system_status("unable to freeze materialized tree directory",
                           directory);
    }
    const Status synced = sync_directory(directory);
    if (!synced.ok())
      return synced;
  }
  return Status::success();
}

[[nodiscard]] Result<std::filesystem::path> reserve_verification_file(
    const NamespacePolicy &policy) {
  const std::filesystem::path staging =
      std::filesystem::path(policy.root) / "staging";
  const Status secured = ensure_private_directory(staging);
  if (!secured.ok())
    return secured;
  for (std::size_t attempt = 0U; attempt < 16U; ++attempt) {
    const std::uint64_t sequence = g_tree_sequence.fetch_add(1U);
    const std::filesystem::path path = staging /
        ("tree-verify-" + std::to_string(::getpid()) + "-" +
         std::to_string(sequence) + ".txtree");
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        0600);
    if (descriptor >= 0) {
      if (::close(descriptor) != 0) {
        std::error_code ignored;
        std::filesystem::remove(path, ignored);
        return Status{ErrorCode::io_error,
                      "unable to close reserved tree verification file"};
      }
      return path;
    }
    if (errno != EEXIST) {
      return system_status("unable to reserve tree verification file", path);
    }
  }
  return Status{ErrorCode::resource_exhausted,
                "tree verification filename population is exhausted"};
}

[[nodiscard]] Result<SyncTreepackStats> repack_and_verify(
    const NamespacePolicy &policy, const std::filesystem::path &tree,
    const Digest &expected) {
  auto temporary = reserve_verification_file(policy);
  if (!temporary.ok())
    return temporary.status();
  ExactPathCleanup remove(temporary.value());
  auto packed = build_sync_treepack(policy, tree, temporary.value());
  if (!packed.ok())
    return packed.status();
  auto digest = hash_sync_file_sha256(temporary.value());
  if (!digest.ok())
    return digest.status();
  if (digest.value() != expected) {
    return Status{ErrorCode::protocol_error,
                  "materialized tree does not reproduce its signed treepack"};
  }
  return packed.value();
}

} // namespace

std::string_view
sync_tree_projection_point_name(SyncTreeProjectionPoint point) noexcept {
  switch (point) {
  case SyncTreeProjectionPoint::unpacked:
    return "unpacked";
  case SyncTreeProjectionPoint::frozen:
    return "frozen";
  case SyncTreeProjectionPoint::revision_committed:
    return "revision-committed";
  case SyncTreeProjectionPoint::revision_synced:
    return "revision-synced";
  case SyncTreeProjectionPoint::pointer_prepared:
    return "pointer-prepared";
  case SyncTreeProjectionPoint::pointer_committed:
    return "pointer-committed";
  case SyncTreeProjectionPoint::pointer_synced:
    return "pointer-synced";
  case SyncTreeProjectionPoint::stale_projections_pruned:
    return "stale-projections-pruned";
  }
  return "unknown";
}

Result<SyncTreepackStats> build_sync_treepack(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::filesystem::path &output) {
  auto limits = limits_for(policy);
  if (!limits.ok())
    return limits.status();
  if (source.empty() || !source.is_absolute() || output.empty() ||
      !output.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "treepack paths must be absolute"};
  }
  const Status controlled = require_private_source(source, limits.value());
  if (!controlled.ok())
    return controlled;
  const Status reserved = require_reserved_output(output);
  if (!reserved.ok())
    return reserved;
  try {
    const toxsync::TreePackStats packed =
        toxsync::pack_tree(source, output, limits.value());
    return SyncTreepackStats{packed.directories, packed.files,
                             packed.content_bytes, packed.artifact_bytes};
  } catch (const std::invalid_argument &error) {
    return Status{ErrorCode::invalid_argument,
                  "unable to build treepack: " + std::string(error.what())};
  } catch (const std::exception &error) {
    return Status{ErrorCode::io_error,
                  "unable to build treepack: " + std::string(error.what())};
  }
}

Result<SyncTreeActivationResult> materialize_sync_treepack(
    const NamespacePolicy &policy, const ActivatedRevision &revision,
    const std::filesystem::path &artifact,
    const SyncNamespaceTransaction &transaction,
    const SyncTreeProjectionSeams &seams) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto limits = limits_for(policy);
  if (!limits.ok())
    return limits.status();
  if (revision.namespace_id != policy.id || revision.generation == 0U ||
      revision.artifact_bytes == 0U || artifact.empty() ||
      !artifact.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "tree activation request is incomplete"};
  }

  const std::filesystem::path activation =
      std::filesystem::path(policy.root) / "materialized-trees";
  const std::filesystem::path revisions = activation / "revisions";
  Status prepared = ensure_private_directory(activation);
  if (!prepared.ok())
    return prepared;
  prepared = ensure_private_directory(revisions);
  if (!prepared.ok())
    return prepared;

  const std::string name = std::to_string(revision.generation) + "-" +
                           hex(revision.record);
  const std::filesystem::path final = revisions / name;
  const std::filesystem::path relative =
      std::filesystem::path("revisions") / name;
  SyncTreeActivationResult result;

  auto recovered_pointers =
      recover_pointer_temporaries(activation, limits.value().max_entries);
  if (!recovered_pointers.ok())
    return recovered_pointers.status();
  result.recovered_pointer_temporaries = recovered_pointers.value();

  auto recovered = remove_materialized_directories(
      revisions, name, true, limits.value().max_entries);
  if (!recovered.ok())
    return recovered.status();
  result.recovered_staging_trees = recovered.value();

  struct stat final_metadata {};
  if (::lstat(final.c_str(), &final_metadata) == 0) {
    if (!S_ISDIR(final_metadata.st_mode) ||
        final_metadata.st_uid != ::geteuid()) {
      return Status{ErrorCode::protocol_error,
                    "tree activation revision path is unsafe"};
    }
    auto verified = repack_and_verify(policy, final, revision.artifact);
    if (!verified.ok())
      return verified.status();
    result.tree = verified.value();
    const Status synced = sync_directory(revisions);
    if (!synced.ok())
      return synced;
  } else if (errno == ENOENT) {
    const std::uint64_t sequence = g_tree_sequence.fetch_add(1U);
    const std::filesystem::path staging = revisions /
        ("." + name + ".part." + std::to_string(::getpid()) + "." +
         std::to_string(sequence));
    ExactPathCleanup remove_staging(staging);
    try {
      const toxsync::TreePackStats unpacked =
          toxsync::unpack_tree(artifact, staging, limits.value());
      result.tree = SyncTreepackStats{
          unpacked.directories, unpacked.files, unpacked.content_bytes,
          unpacked.artifact_bytes};
    } catch (const std::exception &error) {
      return Status{ErrorCode::protocol_error,
                    "unable to materialize verified treepack: " +
                        std::string(error.what())};
    }
    Status checkpoint =
        projection_point(seams, SyncTreeProjectionPoint::unpacked);
    if (!checkpoint.ok())
      return checkpoint;
    auto reproduced = repack_and_verify(policy, staging, revision.artifact);
    if (!reproduced.ok())
      return reproduced.status();
    result.tree = reproduced.value();
    const Status frozen = freeze_and_sync_tree(staging);
    if (!frozen.ok())
      return frozen;
    checkpoint = projection_point(seams, SyncTreeProjectionPoint::frozen);
    if (!checkpoint.ok())
      return checkpoint;
    if (::rename(staging.c_str(), final.c_str()) != 0) {
      return system_status("unable to commit materialized tree", staging);
    }
    remove_staging.release();
    checkpoint =
        projection_point(seams, SyncTreeProjectionPoint::revision_committed);
    if (!checkpoint.ok())
      return checkpoint;
    const Status synced = sync_directory(revisions);
    if (!synced.ok())
      return synced;
    checkpoint =
        projection_point(seams, SyncTreeProjectionPoint::revision_synced);
    if (!checkpoint.ok())
      return checkpoint;
    result.materialized = true;
  } else {
    return system_status("unable to inspect tree activation revision", final);
  }

  const std::filesystem::path current = activation / "current";
  struct stat current_metadata {};
  if (::lstat(current.c_str(), &current_metadata) == 0) {
    if (!S_ISLNK(current_metadata.st_mode)) {
      return Status{ErrorCode::protocol_error,
                    "tree activation current pointer is not a symlink"};
    }
    std::error_code error;
    if (std::filesystem::read_symlink(current, error) == relative && !error) {
      const Status synced = sync_directory(activation);
      if (!synced.ok())
        return synced;
      auto pruned = remove_materialized_directories(
          revisions, name, false, limits.value().max_entries);
      if (!pruned.ok())
        return pruned.status();
      result.pruned_revision_trees = pruned.value();
      const Status checkpoint = projection_point(
          seams, SyncTreeProjectionPoint::stale_projections_pruned);
      if (!checkpoint.ok())
        return checkpoint;
      result.already_current = true;
      return result;
    }
  } else if (errno != ENOENT) {
    return system_status("unable to inspect tree activation pointer", current);
  }

  const std::uint64_t sequence = g_tree_sequence.fetch_add(1U);
  const std::filesystem::path temporary = activation /
      (".current.part." + std::to_string(::getpid()) + "." +
       std::to_string(sequence));
  if (::symlink(relative.c_str(), temporary.c_str()) != 0) {
    return system_status("unable to create tree activation pointer",
                         temporary);
  }
  Status checkpoint =
      projection_point(seams, SyncTreeProjectionPoint::pointer_prepared);
  if (!checkpoint.ok())
    return checkpoint;
  if (::rename(temporary.c_str(), current.c_str()) != 0) {
    const int saved = errno;
    static_cast<void>(::unlink(temporary.c_str()));
    return system_status("unable to switch tree activation pointer", current,
                         saved);
  }
  checkpoint =
      projection_point(seams, SyncTreeProjectionPoint::pointer_committed);
  if (!checkpoint.ok())
    return checkpoint;
  const Status synced = sync_directory(activation);
  if (!synced.ok())
    return synced;
  checkpoint = projection_point(seams, SyncTreeProjectionPoint::pointer_synced);
  if (!checkpoint.ok())
    return checkpoint;
  auto pruned = remove_materialized_directories(
      revisions, name, false, limits.value().max_entries);
  if (!pruned.ok())
    return pruned.status();
  result.pruned_revision_trees = pruned.value();
  checkpoint = projection_point(
      seams, SyncTreeProjectionPoint::stale_projections_pruned);
  if (!checkpoint.ok())
    return checkpoint;
  return result;
}

} // namespace iotox::sync
