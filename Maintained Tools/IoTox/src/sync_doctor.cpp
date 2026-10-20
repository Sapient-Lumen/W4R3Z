#include "iotox/sync_doctor.hpp"

#include "iotox/sync_content_publication.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"
#include "iotox/sync_transaction.hpp"
#include "iotox/sync_tree.hpp"

#include "toxsync/content_store.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <optional>
#include <set>
#include <sstream>
#include <string_view>
#include <sys/stat.h>
#include <sys/xattr.h>
#include <unistd.h>

namespace iotox::sync {
namespace {

constexpr std::uint64_t kTreepackHeaderBytes = 16U;
constexpr std::uint64_t kTreepackEntryBytes = 20U;

[[nodiscard]] Status system_status(std::string_view operation,
                                   const std::filesystem::path &path,
                                   int error = errno) {
  return Status{ErrorCode::io_error, std::string(operation) + " '" +
                                         path.string() +
                                         "': " + std::strerror(error)};
}

[[nodiscard]] Result<std::uint64_t>
add_bounded(std::uint64_t left, std::uint64_t right, std::string_view label) {
  if (right > std::numeric_limits<std::uint64_t>::max() - left) {
    return Status{ErrorCode::resource_exhausted,
                  std::string(label) + " overflows"};
  }
  return left + right;
}

[[nodiscard]] Result<std::uint64_t> subtract_bounded(std::uint64_t total,
                                                     std::uint64_t used,
                                                     std::string_view label) {
  if (used > total) {
    return Status{ErrorCode::resource_exhausted,
                  std::string(label) + " exceeds its configured quota"};
  }
  return total - used;
}

[[nodiscard]] std::string hex_path(const std::filesystem::path &path) {
  static constexpr char digits[] = "0123456789abcdef";
  const std::string native = path.native();
  std::string result;
  result.reserve(native.size() * 2U);
  for (const char character : native) {
    const auto byte = static_cast<unsigned char>(character);
    result.push_back(digits[byte >> 4U]);
    result.push_back(digits[byte & 0x0fU]);
  }
  return result;
}

[[nodiscard]] std::string_view access_name(SyncDoctorAccess access) noexcept {
  return access == SyncDoctorAccess::read_write ? "read-write" : "one-writer";
}

struct TreepackInspection {
  std::uint64_t directories{0U};
  std::uint64_t files{0U};
  std::uint64_t content_bytes{0U};
  std::uint64_t artifact_bytes{kTreepackHeaderBytes + kTreepackEntryBytes};
};

[[nodiscard]] bool same_snapshot(const struct stat &left,
                                 const struct stat &right) noexcept {
  return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
         left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
         left.st_uid == right.st_uid && left.st_size == right.st_size &&
         left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
         left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
         left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
         left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

[[nodiscard]] Status
validate_no_extended_metadata(const std::filesystem::path &path) {
  errno = 0;
  const ssize_t bytes = ::llistxattr(path.c_str(), nullptr, 0U);
  if (bytes < 0) {
    if (errno == ENOTSUP || errno == EOPNOTSUPP)
      return Status::success();
    return system_status("unable to inspect sync-doctor extended metadata",
                         path);
  }
  if (bytes != 0) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor filesystem contract refuses ACLs or extended "
                  "attributes: " +
                      path.string()};
  }
  return Status::success();
}

[[nodiscard]] Status
validate_dense_regular_file(const std::filesystem::path &path,
                            const struct stat &metadata) {
  if (metadata.st_size == 0)
    return Status::success();
  const int raw = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (raw < 0) {
    return system_status("unable to open sync-doctor regular file", path);
  }
  struct Descriptor {
    int value;
    ~Descriptor() {
      if (value >= 0)
        ::close(value);
    }
  } descriptor{raw};
  struct stat opened {};
  if (::fstat(descriptor.value, &opened) != 0) {
    return system_status("unable to inspect opened sync-doctor regular file",
                         path);
  }
  if (!S_ISREG(opened.st_mode) || !same_snapshot(metadata, opened)) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor regular file changed while inspected"};
  }

  errno = 0;
  const off_t hole = ::lseek(descriptor.value, 0, SEEK_HOLE);
  if (hole >= 0) {
    if (hole < opened.st_size) {
      return Status{ErrorCode::protocol_error,
                    "sync-doctor filesystem contract refuses sparse files: " +
                        path.string()};
    }
    if (hole != opened.st_size) {
      return Status{ErrorCode::protocol_error,
                    "sync-doctor filesystem allocation result is invalid: " +
                        path.string()};
    }
    return Status::success();
  }
  const int seek_error = errno;
  if (seek_error != EINVAL && seek_error != ENOTSUP &&
      seek_error != EOPNOTSUPP) {
    return system_status("unable to inspect sync-doctor file allocation", path,
                         seek_error);
  }
  constexpr std::uint64_t kStatBlockBytes = 512U;
  if (opened.st_blocks < 0 ||
      static_cast<std::uint64_t>(opened.st_blocks) >
          std::numeric_limits<std::uint64_t>::max() / kStatBlockBytes) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor filesystem allocation accounting is invalid: " +
                      path.string()};
  }
  const auto blocks = static_cast<std::uint64_t>(opened.st_blocks);
  if (blocks * kStatBlockBytes < static_cast<std::uint64_t>(opened.st_size)) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor filesystem contract cannot prove a dense "
                  "regular file: " +
                      path.string()};
  }
  return Status::success();
}

[[nodiscard]] Status validate_contract_entry(const std::filesystem::path &path,
                                             const struct stat &metadata) {
  if (metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor filesystem contract requires owner-controlled "
                  "entries: " +
                      path.string()};
  }
  if (S_ISREG(metadata.st_mode)) {
    if (metadata.st_nlink != 1 || metadata.st_size < 0 ||
        (metadata.st_mode & static_cast<mode_t>(S_IRUSR)) == 0U) {
      return Status{ErrorCode::protocol_error,
                    "sync-doctor filesystem contract refuses linked or "
                    "unreadable files: " +
                        path.string()};
    }
  } else if (!S_ISDIR(metadata.st_mode)) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor filesystem contract refuses symlinks and "
                  "special files: " +
                      path.string()};
  }
  const Status metadata_status = validate_no_extended_metadata(path);
  if (!metadata_status.ok())
    return metadata_status;
  return S_ISREG(metadata.st_mode) ? validate_dense_regular_file(path, metadata)
                                   : Status::success();
}

[[nodiscard]] std::string ascii_case_key(std::string value) {
  for (char &character : value) {
    if (character >= 'A' && character <= 'Z') {
      character = static_cast<char>(character - 'A' + 'a');
    }
  }
  return value;
}

[[nodiscard]] Status
validate_filesystem_contract(const std::filesystem::path &source,
                             bool ignore_conflict_projection,
                             std::uint64_t maximum_entries) {
  struct stat root {};
  if (::lstat(source.c_str(), &root) != 0) {
    return system_status("unable to inspect sync-doctor contract root", source);
  }
  const Status root_status = validate_contract_entry(source, root);
  if (!root_status.ok())
    return root_status;
  if (S_ISREG(root.st_mode))
    return Status::success();

  std::set<std::string> case_keys;
  std::uint64_t entries = 0U;
  try {
    for (std::filesystem::recursive_directory_iterator iterator(source), end;
         iterator != end; ++iterator) {
      const std::filesystem::path relative_path =
          iterator->path().lexically_relative(source);
      if (ignore_conflict_projection &&
          relative_path.begin() != relative_path.end() &&
          relative_path.begin()->string() == kTreeV2ConflictRoot) {
        if (relative_path ==
            std::filesystem::path(std::string(kTreeV2ConflictRoot))) {
          iterator.disable_recursion_pending();
        }
        continue;
      }
      struct stat metadata {};
      if (::lstat(iterator->path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect sync-doctor contract entry",
                             iterator->path());
      }
      const Status entry_status =
          validate_contract_entry(iterator->path(), metadata);
      if (!entry_status.ok())
        return entry_status;
      const std::string relative = relative_path.generic_string();
      if (!case_keys.insert(ascii_case_key(relative)).second) {
        return Status{
            ErrorCode::protocol_error,
            "sync-doctor filesystem contract refuses an ASCII case-fold "
            "collision: " +
                relative};
      }
      if (entries >= maximum_entries) {
        return Status{ErrorCode::resource_exhausted,
                      "sync-doctor filesystem-contract entry population "
                      "exceeds quota"};
      }
      ++entries;
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync-doctor filesystem contract: " +
                      std::string(error.what())};
  }
  return Status::success();
}

[[nodiscard]] Result<TreepackInspection>
inspect_treepack(const std::filesystem::path &source, const Quotas &quotas) {
  struct stat root {};
  if (::lstat(source.c_str(), &root) != 0) {
    return system_status("unable to inspect sync-doctor directory", source);
  }
  if (!S_ISDIR(root.st_mode) || root.st_uid != ::geteuid() ||
      (root.st_mode & static_cast<mode_t>(0022)) != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor directory is not owner-controlled"};
  }

  TreepackInspection report;
  std::uint64_t entries = 0U;
  try {
    for (std::filesystem::recursive_directory_iterator iterator(source), end;
         iterator != end; ++iterator) {
      struct stat metadata {};
      if (::lstat(iterator->path().c_str(), &metadata) != 0) {
        return system_status("unable to inspect sync-doctor entry",
                             iterator->path());
      }
      if (metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & static_cast<mode_t>(0022)) != 0U ||
          (!S_ISDIR(metadata.st_mode) &&
           (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
            metadata.st_size < 0))) {
        return Status{
            ErrorCode::protocol_error,
            "sync-doctor found a mutable, linked, or special treepack entry: " +
                iterator->path().string()};
      }
      const std::filesystem::path relative_path =
          iterator->path().lexically_relative(source);
      const std::string relative = relative_path.generic_string();
      if (relative.empty() || relative.front() == '/' ||
          relative.size() > kMaximumTreepackPathBytes ||
          relative.find('\0') != std::string::npos) {
        return Status{ErrorCode::invalid_argument,
                      "sync-doctor found an unsupported treepack path"};
      }
      ++entries;
      if (entries > std::min<std::uint64_t>(quotas.maximum_objects,
                                            kMaximumTreepackEntries)) {
        return Status{ErrorCode::resource_exhausted,
                      "sync-doctor treepack entry population exceeds quota"};
      }
      const std::uint64_t content =
          S_ISREG(metadata.st_mode)
              ? static_cast<std::uint64_t>(metadata.st_size)
              : 0U;
      if (content > quotas.maximum_artifact_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "sync-doctor treepack file exceeds artifact quota"};
      }
      auto path_accounted = add_bounded(
          report.artifact_bytes,
          kTreepackEntryBytes + static_cast<std::uint64_t>(relative.size()),
          "sync-doctor treepack artifact size");
      if (!path_accounted)
        return path_accounted.status();
      auto content_accounted =
          add_bounded(path_accounted.value(), content,
                      "sync-doctor treepack artifact size");
      if (!content_accounted)
        return content_accounted.status();
      report.artifact_bytes = content_accounted.value();
      if (report.artifact_bytes > quotas.maximum_artifact_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "sync-doctor treepack artifact exceeds quota"};
      }
      if (S_ISDIR(metadata.st_mode)) {
        ++report.directories;
      } else {
        auto digest = hash_sync_file_sha256(iterator->path());
        if (!digest)
          return digest.status();
        struct stat after {};
        if (::lstat(iterator->path().c_str(), &after) != 0 ||
            !same_snapshot(metadata, after)) {
          return Status{ErrorCode::protocol_error,
                        "sync-doctor treepack source changed while hashed"};
        }
        auto total = add_bounded(report.content_bytes, content,
                                 "sync-doctor content byte count");
        if (!total)
          return total.status();
        report.content_bytes = total.value();
        ++report.files;
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync-doctor source: " +
                      std::string(error.what())};
  }
  return report;
}

[[nodiscard]] Result<std::uint64_t>
available_bytes(const std::filesystem::path &source) {
  std::error_code error;
  const auto space = std::filesystem::space(source, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect sync-doctor source filesystem: " +
                      error.message()};
  }
  return space.available;
}

} // namespace

Status inspect_sync_filesystem_contract(const SyncDoctorOptions &options) {
  const std::uint64_t maximum_entries =
      options.access == SyncDoctorAccess::read_write
          ? options.quotas.maximum_objects
          : std::min<std::uint64_t>(options.quotas.maximum_objects,
                                    kMaximumTreepackEntries);
  return validate_filesystem_contract(
      options.source, options.access == SyncDoctorAccess::read_write,
      maximum_entries);
}

Result<SyncDoctorReport> inspect_sync_source(const SyncDoctorOptions &options) {
  if (options.source.empty() || !options.source.is_absolute() ||
      options.source.lexically_normal() != options.source ||
      options.source == options.source.root_path() ||
      options.interval_seconds == 0U || options.interval_seconds > 86400U) {
    return Status{ErrorCode::invalid_argument,
                  "sync-doctor source or interval is invalid"};
  }

  struct stat supplied {};
  if (::lstat(options.source.c_str(), &supplied) != 0) {
    return system_status("unable to inspect sync-doctor source",
                         options.source);
  }
  if (S_ISLNK(supplied.st_mode) ||
      (!S_ISREG(supplied.st_mode) && !S_ISDIR(supplied.st_mode))) {
    return Status{ErrorCode::invalid_argument,
                  "sync-doctor source must be one regular file or directory"};
  }
  if (options.access == SyncDoctorAccess::read_write &&
      !S_ISDIR(supplied.st_mode)) {
    return Status{ErrorCode::invalid_argument,
                  "sync-doctor read-write source must be a directory"};
  }

  std::error_code canonical_error;
  const std::filesystem::path source =
      std::filesystem::canonical(options.source, canonical_error);
  if (canonical_error || source.empty() || !source.is_absolute() ||
      source == source.root_path()) {
    return Status{ErrorCode::io_error,
                  "unable to resolve sync-doctor source: " +
                      canonical_error.message()};
  }

  SyncDoctorReport report;
  report.source = source;
  report.access = options.access;
  report.interval_seconds = options.interval_seconds;
  report.projection = options.projection;
  report.quotas = options.quotas;

  SyncDoctorOptions contract_options = options;
  contract_options.source = source;
  Status contract = inspect_sync_filesystem_contract(contract_options);
  if (!contract.ok())
    return contract;

  if (options.access == SyncDoctorAccess::read_write) {
    NamespacePolicy policy;
    policy.id = "sync-doctor";
    policy.root = "/var/lib/iotox/sync-doctor";
    policy.engine = Engine::tree_v2;
    policy.activation = ActivationMode::manual;
    PrincipalId writer{};
    writer.front() = 1U;
    policy.writers = {writer};
    policy.projection = options.projection;
    policy.quotas = options.quotas;
    auto scan = scan_tree_v2_worktree(policy, source, std::nullopt, writer, 1U);
    if (!scan)
      return scan.status();
    auto manifest = encode_tree_v2_manifest(policy, scan.value().manifest);
    if (!manifest)
      return manifest.status();
    report.engine = Engine::tree_v2;
    report.directories = scan.value().directories;
    report.files = scan.value().files.size();
    report.entries = scan.value().manifest.entries.size();
    report.content_bytes = scan.value().file_bytes;
    report.manifest_bytes = manifest.value().size();
    report.artifact_bytes = report.content_bytes;
    std::set<Digest> unique;
    std::uint64_t unique_bytes = 0U;
    for (const TreeV2ScannedFile &file : scan.value().files) {
      if (unique.insert(file.content).second) {
        auto total = add_bounded(unique_bytes, file.content_bytes,
                                 "sync-doctor unique object bytes");
        if (!total)
          return total.status();
        unique_bytes = total.value();
      }
    }
    report.estimated_objects = unique.size() + 1U;
    auto store = add_bounded(unique_bytes, report.manifest_bytes,
                             "sync-doctor store estimate");
    if (!store)
      return store.status();
    report.minimum_store_bytes = store.value();
    auto staging = add_bounded(report.content_bytes, report.manifest_bytes,
                               "sync-doctor staging estimate");
    if (!staging)
      return staging.status();
    report.minimum_staging_bytes = staging.value();
  } else if (S_ISDIR(supplied.st_mode)) {
    auto inspected = inspect_treepack(source, options.quotas);
    if (!inspected)
      return inspected.status();
    report.engine = Engine::treepack_v1;
    report.directories = inspected.value().directories;
    report.files = inspected.value().files;
    report.entries = report.directories + report.files;
    report.content_bytes = inspected.value().content_bytes;
    report.artifact_bytes = inspected.value().artifact_bytes;
    report.estimated_objects = 1U;
    report.minimum_store_bytes = report.artifact_bytes;
    constexpr std::uint64_t kTreepackSortBytesPerEntry =
        sizeof(std::string) + kMaximumTreepackPathBytes;
    auto sort_bytes =
        add_bounded(report.entries * kTreepackSortBytesPerEntry, 1U,
                    "sync-doctor treepack sort-memory estimate");
    if (!sort_bytes)
      return sort_bytes.status();
    report.minimum_staging_bytes =
        std::max(report.artifact_bytes, sort_bytes.value());
  } else {
    if (supplied.st_size <= 0 || static_cast<std::uint64_t>(supplied.st_size) >
                                     options.quotas.maximum_artifact_bytes) {
      return Status{
          ErrorCode::invalid_argument,
          "sync-doctor content source is not one bounded nonempty file"};
    }
    auto digest = hash_sync_file_sha256(source);
    if (!digest)
      return digest.status();
    struct stat source_after {};
    if (::lstat(source.c_str(), &source_after) != 0 ||
        !same_snapshot(supplied, source_after)) {
      return Status{ErrorCode::protocol_error,
                    "sync-doctor content source changed while hashed"};
    }
    const std::uint64_t bytes = static_cast<std::uint64_t>(supplied.st_size);
    toxsync::ContentChunkingAutoOptions automatic;
    automatic.metadata_budget_bytes = options.quotas.maximum_manifest_bytes;
    const toxsync::ContentStoreLimits limits{
        options.quotas.maximum_artifact_bytes, options.quotas.maximum_objects,
        1024U,
        static_cast<std::uint32_t>(std::min<std::uint64_t>(
            options.quotas.maximum_artifact_bytes,
            std::numeric_limits<std::uint32_t>::max()))};
    const auto estimate =
        toxsync::estimate_content_scale(bytes, automatic, limits);
    if (estimate.maximum_manifest_bytes >
            options.quotas.maximum_manifest_bytes ||
        estimate.maximum_chunks >= options.quotas.maximum_objects) {
      return Status{ErrorCode::resource_exhausted,
                    "sync-doctor content manifest exceeds namespace quota"};
    }
    report.engine = Engine::content_v2;
    report.files = 1U;
    report.entries = 1U;
    report.content_bytes = bytes;
    report.artifact_bytes = bytes;
    report.manifest_bytes = estimate.maximum_manifest_bytes;
    report.estimated_objects = estimate.maximum_chunks + 1U;
    auto estimate_bytes = add_bounded(bytes, report.manifest_bytes,
                                      "sync-doctor content store estimate");
    if (!estimate_bytes)
      return estimate_bytes.status();
    report.minimum_store_bytes = estimate_bytes.value();
    report.minimum_staging_bytes = estimate_bytes.value();
  }

  if (report.minimum_store_bytes > options.quotas.maximum_store_bytes ||
      report.minimum_staging_bytes > options.quotas.maximum_staging_bytes ||
      report.estimated_objects > options.quotas.maximum_objects) {
    return Status{
        ErrorCode::resource_exhausted,
        "sync-doctor source exceeds default storage or staging quota"};
  }
  contract = inspect_sync_filesystem_contract(contract_options);
  if (!contract.ok())
    return contract;
  auto available = available_bytes(source);
  if (!available)
    return available.status();
  report.source_filesystem_available_bytes = available.value();
  return report;
}

namespace {

[[nodiscard]] Status
require_existing_transaction_paths(const NamespacePolicy &policy) {
  const std::filesystem::path directory =
      std::filesystem::path(policy.root) / "transactions";
  const std::filesystem::path lock =
      directory / (policy.id + ".transaction.lock");
  struct stat directory_metadata {};
  struct stat lock_metadata {};
  if (::lstat(directory.c_str(), &directory_metadata) != 0) {
    if (errno == ENOENT) {
      return Status{
          ErrorCode::not_found,
          "configured sync namespace has no existing transaction directory"};
    }
    return system_status(
        "unable to inspect configured sync transaction directory", directory);
  }
  if (!S_ISDIR(directory_metadata.st_mode) ||
      directory_metadata.st_uid != ::geteuid() ||
      (directory_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{
        ErrorCode::protocol_error,
        "configured sync transaction directory is not private and owner-owned"};
  }
  if (::lstat(lock.c_str(), &lock_metadata) != 0) {
    if (errno == ENOENT) {
      return Status{
          ErrorCode::not_found,
          "configured sync namespace has no existing transaction lock"};
    }
    return system_status("unable to inspect configured sync transaction lock",
                         lock);
  }
  if (!S_ISREG(lock_metadata.st_mode) || lock_metadata.st_nlink != 1 ||
      lock_metadata.st_uid != ::geteuid() ||
      lock_metadata.st_dev != directory_metadata.st_dev ||
      (lock_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600)) {
    return Status{
        ErrorCode::protocol_error,
        "configured sync transaction lock is not one private owner file"};
  }
  return Status::success();
}

[[nodiscard]] Result<std::uint64_t>
inspect_staging_tree(const std::filesystem::path &root,
                     std::uint64_t maximum_entries) {
  struct stat root_metadata {};
  if (::lstat(root.c_str(), &root_metadata) != 0) {
    if (errno == ENOENT)
      return 0U;
    return system_status("unable to inspect sync-doctor staging root", root);
  }
  if (!S_ISDIR(root_metadata.st_mode) || root_metadata.st_uid != ::geteuid() ||
      (root_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync-doctor staging root is not private and owner-owned"};
  }
  std::uint64_t entries = 0U;
  std::uint64_t bytes = 0U;
  std::error_code error;
  for (std::filesystem::recursive_directory_iterator iterator(root, error), end;
       !error && iterator != end; iterator.increment(error)) {
    if (++entries > maximum_entries) {
      return Status{ErrorCode::resource_exhausted,
                    "sync-doctor staging inventory exceeds its bound"};
    }
    struct stat metadata {};
    if (::lstat(iterator->path().c_str(), &metadata) != 0) {
      return system_status("unable to inspect sync-doctor staging entry",
                           iterator->path());
    }
    const bool private_directory =
        S_ISDIR(metadata.st_mode) &&
        (metadata.st_mode & static_cast<mode_t>(0777)) ==
            static_cast<mode_t>(0700);
    const bool private_file = S_ISREG(metadata.st_mode) &&
                              metadata.st_nlink == 1 && metadata.st_size >= 0 &&
                              (metadata.st_mode & static_cast<mode_t>(0777)) ==
                                  static_cast<mode_t>(0600);
    if (metadata.st_uid != ::geteuid() ||
        (!private_directory && !private_file)) {
      return Status{ErrorCode::protocol_error,
                    "sync-doctor staging inventory contains an unsafe entry"};
    }
    if (!S_ISREG(metadata.st_mode))
      continue;
    auto total =
        add_bounded(bytes, static_cast<std::uint64_t>(metadata.st_size),
                    "sync-doctor staging inventory");
    if (!total)
      return total.status();
    bytes = total.value();
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync-doctor staging inventory: " +
                      error.message()};
  }
  return bytes;
}

[[nodiscard]] Result<std::pair<std::uint64_t, std::uint64_t>>
inspect_managed_store(const NamespacePolicy &policy,
                      const security::SigningPublicKey &expected_device,
                      const security::Sodium &sodium,
                      const SyncNamespaceTransaction &transaction) {
  if (policy.engine == Engine::tree_v2) {
    auto plan = plan_tree_v2_gc(policy, expected_device, sodium, transaction);
    if (!plan)
      return plan.status();
    auto bytes =
        add_bounded(plan.value().reachable_bytes, plan.value().candidate_bytes,
                    "sync-doctor tree-v2 store inventory");
    if (!bytes)
      return bytes.status();
    const std::uint64_t objects =
        static_cast<std::uint64_t>(plan.value().reachable.size()) +
        static_cast<std::uint64_t>(plan.value().candidates.size());
    return std::pair{objects, bytes.value()};
  }
  auto records = inspect_sync_object_records(policy, transaction);
  if (!records)
    return records.status();
  std::uint64_t bytes = 0U;
  for (const SyncObjectRecord &record : records.value()) {
    auto total =
        add_bounded(bytes, record.bytes, "sync-doctor managed store inventory");
    if (!total)
      return total.status();
    bytes = total.value();
  }
  return std::pair{static_cast<std::uint64_t>(records.value().size()), bytes};
}

} // namespace

Result<SyncDoctorReport> inspect_sync_managed_storage(
    SyncDoctorReport report, const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium, std::uint64_t automation_generation,
    std::uint64_t automation_interval_ms) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (report.engine != policy.engine || report.quotas != policy.quotas ||
      report.projection != policy.projection || automation_generation == 0U ||
      automation_interval_ms < 1000U || automation_interval_ms > 86400000U) {
    return Status{ErrorCode::invalid_argument,
                  "configured sync-doctor source and namespace policy differ"};
  }
  const Status existing = require_existing_transaction_paths(policy);
  if (!existing.ok())
    return existing;
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  auto store = inspect_managed_store(policy, expected_device, sodium,
                                     transaction.value());
  if (!store)
    return store.status();

  std::uint64_t staging_bound = policy.quotas.maximum_objects;
  if (staging_bound > (std::numeric_limits<std::uint64_t>::max() - 64U) / 4U) {
    staging_bound = std::numeric_limits<std::uint64_t>::max();
  } else {
    staging_bound = staging_bound * 4U + 64U;
  }
  const std::filesystem::path staging =
      policy.engine == Engine::tree_v2
          ? std::filesystem::path(policy.root) / "tree-v2" / "incoming"
          : std::filesystem::path(policy.root) / "staging";
  auto staging_bytes = inspect_staging_tree(staging, staging_bound);
  if (!staging_bytes)
    return staging_bytes.status();

  auto store_headroom =
      subtract_bounded(policy.quotas.maximum_store_bytes, store.value().second,
                       "sync-doctor managed store occupancy");
  if (!store_headroom)
    return store_headroom.status();
  auto staging_headroom = subtract_bounded(
      policy.quotas.maximum_staging_bytes, staging_bytes.value(),
      "sync-doctor managed staging occupancy");
  if (!staging_headroom)
    return staging_headroom.status();
  if (store.value().first > policy.quotas.maximum_objects) {
    return Status{
        ErrorCode::resource_exhausted,
        "sync-doctor managed object occupancy exceeds its configured quota"};
  }
  if (report.minimum_store_bytes > store_headroom.value() ||
      report.minimum_staging_bytes > staging_headroom.value() ||
      report.estimated_objects >
          policy.quotas.maximum_objects - store.value().first) {
    return Status{
        ErrorCode::resource_exhausted,
        "configured sync namespace lacks conservative quota headroom"};
  }

  auto managed_required =
      add_bounded(report.minimum_store_bytes, report.minimum_staging_bytes,
                  "sync-doctor managed filesystem requirement");
  if (!managed_required)
    return managed_required.status();
  const std::uint64_t source_required =
      report.access == SyncDoctorAccess::read_write ? report.content_bytes : 0U;

  std::error_code space_error;
  const auto managed_space = std::filesystem::space(policy.root, space_error);
  if (space_error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect configured sync filesystem: " +
                      space_error.message()};
  }
  struct stat source_metadata {};
  struct stat managed_metadata {};
  if (::lstat(report.source.c_str(), &source_metadata) != 0 ||
      ::lstat(policy.root.c_str(), &managed_metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to compare configured sync filesystems"};
  }
  std::uint64_t managed_filesystem_required = managed_required.value();
  if (source_required != 0U &&
      source_metadata.st_dev == managed_metadata.st_dev) {
    auto combined = add_bounded(managed_filesystem_required, source_required,
                                "sync-doctor shared filesystem requirement");
    if (!combined)
      return combined.status();
    managed_filesystem_required = combined.value();
  } else if (source_required > report.source_filesystem_available_bytes) {
    return Status{
        ErrorCode::resource_exhausted,
        "configured sync source filesystem lacks projection staging headroom"};
  }
  if (managed_filesystem_required > managed_space.available) {
    return Status{
        ErrorCode::resource_exhausted,
        "configured sync filesystem lacks conservative free-space headroom"};
  }
  const Status still_held =
      require_sync_transaction(policy, transaction.value());
  if (!still_held.ok())
    return still_held;

  report.managed_storage_probed = true;
  report.configured_namespace = policy.id;
  report.managed_root = policy.root;
  report.automation_generation = automation_generation;
  report.automation_interval_ms = automation_interval_ms;
  report.managed_store_objects = store.value().first;
  report.managed_store_bytes = store.value().second;
  report.managed_staging_bytes = staging_bytes.value();
  report.managed_store_headroom_bytes = store_headroom.value();
  report.managed_staging_headroom_bytes = staging_headroom.value();
  report.managed_filesystem_available_bytes = managed_space.available;
  report.managed_filesystem_capacity_bytes = managed_space.capacity;
  report.managed_filesystem_required_bytes = managed_filesystem_required;
  report.source_filesystem_required_bytes = source_required;
  return report;
}

std::string render_sync_doctor_report(const SyncDoctorReport &report) {
  std::ostringstream output;
  output << (report.managed_storage_probed ? "iotox-sync-doctor-v4\n"
                                           : "iotox-sync-doctor-v3\n")
         << "decision=ready\n"
         << "path-hex=" << hex_path(report.source) << '\n'
         << "access=" << access_name(report.access) << '\n'
         << "engine=" << engine_name(report.engine) << '\n'
         << "interval-seconds=" << report.interval_seconds << '\n'
         << "metadata="
         << tree_v2_metadata_mode_name(report.projection.metadata) << '\n'
         << "include-rules=" << report.projection.includes.size() << '\n'
         << "exclude-rules=" << report.projection.excludes.size() << '\n'
         << "directories=" << report.directories << '\n'
         << "files=" << report.files << '\n'
         << "entries=" << report.entries << '\n'
         << "content-bytes=" << report.content_bytes << '\n'
         << "manifest-bytes=" << report.manifest_bytes << '\n'
         << "artifact-bytes=" << report.artifact_bytes << '\n'
         << "estimated-objects=" << report.estimated_objects << '\n'
         << "minimum-store-bytes=" << report.minimum_store_bytes << '\n'
         << "minimum-staging-bytes=" << report.minimum_staging_bytes << '\n'
         << "source-filesystem-available-bytes="
         << report.source_filesystem_available_bytes << '\n'
         << "quota-artifact-bytes=" << report.quotas.maximum_artifact_bytes
         << '\n'
         << "quota-manifest-bytes=" << report.quotas.maximum_manifest_bytes
         << '\n'
         << "quota-store-bytes=" << report.quotas.maximum_store_bytes << '\n'
         << "quota-staging-bytes=" << report.quotas.maximum_staging_bytes
         << '\n'
         << "quota-objects=" << report.quotas.maximum_objects << '\n'
         << "filesystem-contract=ready\n"
         << "path-model=byte-exact-case-sensitive-required\n"
         << "ascii-case-collisions=refused\n"
         << "ownership=agent-owner-required-local-owner-projected\n"
         << "hard-links=refused\n"
         << "symlinks=refused\n"
         << "special-files=refused\n"
         << "acl-xattrs=refused\n"
         << "sparse-layout=refused\n"
         << "timestamps=not-preserved\n";
  if (report.managed_storage_probed) {
    output << "configured-namespace=" << report.configured_namespace << '\n'
           << "automation-generation=" << report.automation_generation << '\n'
           << "automation-interval-ms=" << report.automation_interval_ms << '\n'
           << "managed-root-path-hex=" << hex_path(report.managed_root) << '\n'
           << "managed-store-objects=" << report.managed_store_objects << '\n'
           << "managed-store-bytes=" << report.managed_store_bytes << '\n'
           << "managed-staging-bytes=" << report.managed_staging_bytes << '\n'
           << "managed-store-headroom-bytes="
           << report.managed_store_headroom_bytes << '\n'
           << "managed-staging-headroom-bytes="
           << report.managed_staging_headroom_bytes << '\n'
           << "managed-filesystem-available-bytes="
           << report.managed_filesystem_available_bytes << '\n'
           << "managed-filesystem-capacity-bytes="
           << report.managed_filesystem_capacity_bytes << '\n'
           << "managed-filesystem-required-bytes="
           << report.managed_filesystem_required_bytes << '\n'
           << "source-filesystem-required-bytes="
           << report.source_filesystem_required_bytes << '\n'
           << "managed-storage-headroom=ready\n";
  } else {
    output << "managed-storage-headroom=not-probed\n";
  }
  output << "backup=not-assessed\n";
  if (report.engine == Engine::tree_v2) {
    output << "transformations="
           << (report.projection.metadata == TreeV2MetadataMode::owner_mode_v2
                   ? "directory-modes-normalized,owner-rwx-preserved"
                   : "directory-modes-normalized,executable-bit-preserved")
           << "\n";
  } else if (report.engine == Engine::treepack_v1) {
    output << "transformations=directory-modes-normalized,executable-bit-"
              "preserved\n";
  } else {
    output << "transformations=content-chunking\n";
  }
  return output.str();
}

} // namespace iotox::sync
