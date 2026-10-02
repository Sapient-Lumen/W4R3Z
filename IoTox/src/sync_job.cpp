#include "iotox/sync_job.hpp"

#include "iotox/sync_guarded_witness.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <optional>
#include <span>
#include <string>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::sync {
namespace {

class UniqueFd {
public:
  UniqueFd() = default;
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() { reset(); }

  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;

  UniqueFd(UniqueFd &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  UniqueFd &operator=(UniqueFd &&other) noexcept {
    if (this != &other) {
      reset();
      descriptor_ = std::exchange(other.descriptor_, -1);
    }
    return *this;
  }

  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept { return descriptor_ >= 0; }

  void reset(int descriptor = -1) noexcept {
    if (descriptor_ >= 0) {
      int result = -1;
      do {
        result = ::close(descriptor_);
      } while (result != 0 && errno == EINTR);
    }
    descriptor_ = descriptor;
  }

private:
  int descriptor_{-1};
};

[[nodiscard]] Status system_status(ErrorCode code, std::string operation,
                                   const std::filesystem::path &path) {
  operation += " '" + path.string() + "': ";
  operation += std::strerror(errno);
  return Status{code, std::move(operation)};
}

[[nodiscard]] std::string hex_encode(std::span<const std::uint8_t> bytes) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(bytes.size() * 2U);
  for (const std::uint8_t byte : bytes) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

[[nodiscard]] std::string attempt_hex(std::uint64_t attempt_id) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output(16U, '0');
  for (std::size_t index = 0U; index < output.size(); ++index) {
    const std::size_t shift = (output.size() - index - 1U) * 4U;
    output[index] = digits[(attempt_id >> shift) & 0x0fU];
  }
  return output;
}

[[nodiscard]] std::optional<std::uint64_t>
parse_attempt_staging_name(std::string_view name) noexcept {
  constexpr std::string_view prefix = "attempt-";
  constexpr std::string_view suffix = ".part";
  if (name.size() != prefix.size() + 16U + suffix.size() ||
      !name.starts_with(prefix) || !name.ends_with(suffix)) {
    return std::nullopt;
  }
  std::uint64_t value = 0U;
  for (const char character :
       name.substr(prefix.size(), 16U)) {
    std::uint8_t nibble = 0U;
    if (character >= '0' && character <= '9') {
      nibble = static_cast<std::uint8_t>(character - '0');
    } else if (character >= 'a' && character <= 'f') {
      nibble = static_cast<std::uint8_t>(character - 'a' + 10);
    } else {
      return std::nullopt;
    }
    value = (value << 4U) | nibble;
  }
  return value;
}

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t value) { return value == 0U; });
}

[[nodiscard]] bool valid_object_name(std::string_view name,
                                     std::string_view suffix) noexcept {
  if (name.size() != 64U + suffix.size() || !name.ends_with(suffix))
    return false;
  return std::all_of(name.begin(), name.begin() + 64,
                     [](char value) {
                       return (value >= '0' && value <= '9') ||
                              (value >= 'a' && value <= 'f');
                     });
}

[[nodiscard]] int hex_nibble(char value) noexcept {
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return 10 + value - 'a';
  return -1;
}

[[nodiscard]] Digest object_name_digest(std::string_view name) noexcept {
  Digest output{};
  for (std::size_t index = 0U; index < output.size(); ++index) {
    const int high = hex_nibble(name[index * 2U]);
    const int low = hex_nibble(name[index * 2U + 1U]);
    output[index] = static_cast<std::uint8_t>((high << 4U) | low);
  }
  return output;
}

[[nodiscard]] bool cancelled(const SyncInstallSeams &seams) {
  return seams.cancel_requested && seams.cancel_requested();
}

[[nodiscard]] Status validate_staged_object(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (attempt_id == 0U || all_zero(object.identity) || object.bytes == 0U ||
      (object.kind != SyncObjectKind::artifact &&
       object.kind != SyncObjectKind::manifest)) {
    return Status{ErrorCode::invalid_argument,
                  "sync staged object identity is invalid"};
  }
  const std::uint64_t kind_limit =
      object.kind == SyncObjectKind::artifact
          ? policy.quotas.maximum_artifact_bytes
          : policy.quotas.maximum_manifest_bytes;
  if (object.bytes > kind_limit ||
      object.bytes > policy.quotas.maximum_staging_bytes ||
      object.bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync staged object exceeds namespace quotas"};
  }
  return Status::success();
}

[[nodiscard]] std::filesystem::path staged_attempt_path(
    const NamespacePolicy &policy, std::uint64_t attempt_id) {
  return std::filesystem::path(policy.root) / "staging" /
         ("attempt-" + attempt_hex(attempt_id) + ".part");
}

[[nodiscard]] std::string transport_staging_prefix(
    std::uint64_t attempt_id) {
  return ".iotox-attempt-" + attempt_hex(attempt_id) + ".part.part-";
}

[[nodiscard]] bool valid_mkstemp_suffix(std::string_view suffix) noexcept {
  return suffix.size() == 6U &&
         std::all_of(suffix.begin(), suffix.end(), [](char value) {
           return (value >= '0' && value <= '9') ||
                  (value >= 'A' && value <= 'Z') ||
                  (value >= 'a' && value <= 'z');
         });
}

} // namespace

std::filesystem::path sync_object_path(
    const NamespacePolicy &policy, const SyncObjectRecord &object) {
  return std::filesystem::path(policy.root) / "objects" /
         (hex_encode(object.identity) +
          (object.kind == SyncObjectKind::artifact ? ".artifact" :
                                                     ".manifest"));
}

namespace {

[[nodiscard]] Status ensure_private_directory(const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync directory '" + path.string() +
                      "': " + error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync directory", path);
  }
  if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "sync directory is not a real owner-owned directory: " +
                      path.string()};
  }
  std::filesystem::permissions(
      path, std::filesystem::perms::owner_all,
      std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to set sync directory permissions '" + path.string() +
                      "': " + error.message()};
  }
  return Status::success();
}

[[nodiscard]] Status fsync_directory(const std::filesystem::path &directory) {
  UniqueFd descriptor(::open(directory.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC));
  if (!descriptor) {
    return system_status(ErrorCode::io_error, "unable to open sync directory", directory);
  }
  if (::fsync(descriptor.get()) != 0) {
    return system_status(ErrorCode::io_error, "unable to fsync sync directory", directory);
  }
  return Status::success();
}

[[nodiscard]] Result<std::uint64_t>
regular_file_size(const std::filesystem::path &path, std::string_view label) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to stat " + std::string(label), path);
  }
  if (!S_ISREG(metadata.st_mode)) {
    return Status{ErrorCode::invalid_argument,
                  std::string(label) + " is not a regular file: " + path.string()};
  }
  if (metadata.st_size < 0) {
    return Status{ErrorCode::invalid_argument,
                  std::string(label) + " has negative size: " + path.string()};
  }
  return static_cast<std::uint64_t>(metadata.st_size);
}

[[nodiscard]] Result<std::uint64_t>
private_object_size(const std::filesystem::path &path) {
  UniqueFd descriptor(
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!descriptor) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found,
                    "sync object is absent: " + path.string()};
    }
    return system_status(ErrorCode::io_error,
                         "unable to open sync object", path);
  }
  struct stat metadata {};
  if (::fstat(descriptor.get(), &metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync object", path);
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size < 0) {
    return Status{ErrorCode::protocol_error,
                  "sync object is not one private owner file: " +
                      path.string()};
  }
  return static_cast<std::uint64_t>(metadata.st_size);
}

[[nodiscard]] Status write_all(int descriptor, std::span<const std::uint8_t> bytes,
                               const std::filesystem::path &path) {
  std::size_t written = 0U;
  while (written < bytes.size()) {
    const ssize_t count =
        ::write(descriptor, bytes.data() + written, bytes.size() - written);
    if (count < 0) {
      if (errno == EINTR) {
        continue;
      }
      return system_status(ErrorCode::io_error,
                           "unable to write sync temporary object", path);
    }
    if (count == 0) {
      return Status{ErrorCode::io_error,
                    "sync temporary object write made no progress: " + path.string()};
    }
    written += static_cast<std::size_t>(count);
  }
  return Status::success();
}

[[nodiscard]] Status copy_exclusive(const std::filesystem::path &source,
                                    const std::filesystem::path &target,
                                    const std::filesystem::path &staging_dir,
                                    std::uint64_t chunk_bytes,
                                    const SyncInstallSeams &seams) {
  if (chunk_bytes == 0U || chunk_bytes > 1024U * 1024U) {
    return Status{ErrorCode::invalid_argument,
                  "sync copy chunk size must be in the range 1..1048576"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable, "sync install cancelled before copy"};
  }

  UniqueFd input(
      ::open(source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!input) {
    return system_status(ErrorCode::io_error, "unable to open sync source", source);
  }
  struct stat input_metadata {};
  if (::fstat(input.get(), &input_metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect opened sync source", source);
  }
  if (!S_ISREG(input_metadata.st_mode)) {
    return Status{ErrorCode::invalid_argument,
                  "opened sync source is not a regular file: " +
                      source.string()};
  }

  const std::string temporary_pattern =
      (staging_dir / ("." + target.filename().string() + ".tmp.XXXXXX"))
          .string();
  std::vector<char> mutable_pattern(temporary_pattern.begin(),
                                    temporary_pattern.end());
  mutable_pattern.push_back('\0');
  UniqueFd output(::mkstemp(mutable_pattern.data()));
  if (!output) {
    return system_status(ErrorCode::io_error,
                         "unable to create sync temporary object",
                         temporary_pattern);
  }
  const std::filesystem::path temporary{mutable_pattern.data()};
  const int descriptor_flags = ::fcntl(output.get(), F_GETFD);
  if (descriptor_flags < 0 ||
      ::fcntl(output.get(), F_SETFD, descriptor_flags | FD_CLOEXEC) != 0 ||
      ::fchmod(output.get(), S_IRUSR | S_IWUSR) != 0) {
    const Status status = system_status(
        ErrorCode::io_error, "unable to secure sync temporary object", temporary);
    output.reset();
    std::error_code ignored;
    std::filesystem::remove(temporary, ignored);
    return status;
  }

  Status status = Status::success();
  std::vector<std::uint8_t> buffer(static_cast<std::size_t>(chunk_bytes));
  while (status.ok()) {
    if (cancelled(seams)) {
      status = Status{ErrorCode::unavailable, "sync install cancelled during copy"};
      break;
    }
    const ssize_t count = ::read(input.get(), buffer.data(), buffer.size());
    if (count < 0) {
      if (errno == EINTR) {
        continue;
      }
      status = system_status(ErrorCode::io_error, "unable to read sync source", source);
      break;
    }
    if (count == 0) {
      break;
    }
    status =
        write_all(output.get(), std::span<const std::uint8_t>(
                                    buffer.data(), static_cast<std::size_t>(count)),
                  temporary);
  }

  if (status.ok() && ::fsync(output.get()) != 0) {
    status = system_status(ErrorCode::io_error,
                           "unable to fsync sync temporary object", temporary);
  }
  output.reset();
  if (!status.ok()) {
    std::error_code ignored;
    std::filesystem::remove(temporary, ignored);
    return status;
  }

  if (::link(temporary.c_str(), target.c_str()) != 0) {
    if (errno == EEXIST) {
      std::error_code ignored;
      std::filesystem::remove(temporary, ignored);
      return Status{ErrorCode::io_error,
                    "sync object appeared during exclusive publication: " +
                        target.string()};
    }
    const Status link_status =
        system_status(ErrorCode::io_error, "unable to publish sync object", target);
    std::error_code ignored;
    std::filesystem::remove(temporary, ignored);
    return link_status;
  }
  status = fsync_directory(target.parent_path());
  std::error_code ignored;
  std::filesystem::remove(temporary, ignored);
  if (!status.ok()) {
    return status;
  }
  return fsync_directory(staging_dir);
}

[[nodiscard]] Result<bool> ensure_object(const std::filesystem::path &source,
                                         const std::filesystem::path &object,
                                         const std::filesystem::path &staging,
                                         const Digest &expected_digest,
                                         std::uint64_t expected_bytes,
                                         std::uint64_t chunk_bytes,
                                         const SyncInstallSeams &seams) {
  std::error_code exists_error;
  const bool exists = std::filesystem::exists(object, exists_error);
  if (exists_error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect sync object '" + object.string() +
                      "': " + exists_error.message()};
  }
  if (exists) {
    auto size = private_object_size(object);
    if (!size.ok()) {
      return size.status();
    }
    if (size.value() != expected_bytes) {
      return Status{ErrorCode::protocol_error,
                    "existing sync object size does not match accepted artifact"};
    }
    auto object_digest = seams.hash_file(object);
    if (!object_digest.ok()) {
      return object_digest.status();
    }
    if (object_digest.value() != expected_digest) {
      return Status{ErrorCode::protocol_error,
                    "existing sync object digest does not match its identity"};
    }
    return false;
  }
  const Status copied = copy_exclusive(source, object, staging, chunk_bytes, seams);
  if (!copied.ok()) {
    return copied;
  }
  auto copied_size = private_object_size(object);
  auto copied_digest = seams.hash_file(object);
  if (!copied_size.ok() || !copied_digest.ok() ||
      copied_size.value() != expected_bytes ||
      copied_digest.value() != expected_digest) {
    std::error_code ignored;
    std::filesystem::remove(object, ignored);
    static_cast<void>(fsync_directory(object.parent_path()));
    if (!copied_size.ok())
      return copied_size.status();
    if (!copied_digest.ok())
      return copied_digest.status();
    return Status{ErrorCode::protocol_error,
                  "new sync object changed while being committed"};
  }
  return true;
}

} // namespace

Result<std::filesystem::path> prepare_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_staged_object(policy, attempt_id, object);
  if (!valid.ok()) return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const std::filesystem::path root{policy.root};
  const std::filesystem::path staging = root / "staging";
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok()) return prepared;
  prepared = ensure_private_directory(staging);
  if (!prepared.ok()) return prepared;
  const std::filesystem::path path = staged_attempt_path(policy, attempt_id);
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) == 0) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt staging destination already exists: " +
                      path.string()};
  }
  if (errno != ENOENT) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync attempt staging path", path);
  }
  return path;
}

Result<SyncAttemptPartial> create_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction) {
  auto prepared = prepare_sync_attempt_staging(
      policy, attempt_id, object, transaction);
  if (!prepared) return prepared.status();
  UniqueFd descriptor(::open(
      prepared.value().c_str(),
      O_RDWR | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
      S_IRUSR | S_IWUSR));
  if (!descriptor) {
    return system_status(ErrorCode::io_error,
                         "unable to create sync attempt partial",
                         prepared.value());
  }
  struct stat metadata {};
  Status status = Status::success();
  if (::fstat(descriptor.get(), &metadata) != 0) {
    status = system_status(ErrorCode::io_error,
                           "unable to inspect sync attempt partial",
                           prepared.value());
  } else if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
             metadata.st_uid != ::geteuid() ||
             (metadata.st_mode & static_cast<mode_t>(0777)) !=
                 static_cast<mode_t>(0600) || metadata.st_size != 0) {
    status = Status{ErrorCode::protocol_error,
                    "new sync attempt partial is not one empty private owner file"};
  } else if (::fsync(descriptor.get()) != 0) {
    status = system_status(ErrorCode::io_error,
                           "unable to fsync sync attempt partial",
                           prepared.value());
  }
  descriptor.reset();
  if (!status.ok()) {
    static_cast<void>(::unlink(prepared.value().c_str()));
    return status;
  }
  status = fsync_directory(prepared.value().parent_path());
  if (!status.ok()) {
    static_cast<void>(::unlink(prepared.value().c_str()));
    static_cast<void>(fsync_directory(prepared.value().parent_path()));
    return status;
  }
  return SyncAttemptPartial{prepared.value(), 0U};
}

Result<SyncAttemptPartial> inspect_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_staged_object(policy, attempt_id, object);
  if (!valid.ok()) return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const std::filesystem::path path =
      staged_attempt_path(policy, attempt_id);
  auto bytes = private_object_size(path);
  if (!bytes) return bytes.status();
  if (bytes.value() >= object.bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt partial is not an incomplete object"};
  }
  return SyncAttemptPartial{path, bytes.value()};
}

Result<SyncAttemptPartial> handoff_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t prior_attempt_id,
    std::uint64_t next_attempt_id, const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_staged_object(
      policy, prior_attempt_id, object);
  if (!valid.ok()) return valid;
  const Status next_valid = validate_staged_object(
      policy, next_attempt_id, object);
  if (!next_valid.ok()) return next_valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (prior_attempt_id == next_attempt_id) {
    return Status{ErrorCode::invalid_argument,
                  "sync partial handoff requires distinct attempts"};
  }
  auto inspected = inspect_sync_attempt_partial(
      policy, prior_attempt_id, object, transaction);
  const std::filesystem::path prior =
      staged_attempt_path(policy, prior_attempt_id);
  const std::filesystem::path next =
      staged_attempt_path(policy, next_attempt_id);
  if (!inspected) {
    if (inspected.status().code() != ErrorCode::not_found) {
      return inspected.status();
    }
    auto moved_bytes = private_object_size(next);
    if (!moved_bytes) return moved_bytes.status();
    if (moved_bytes.value() >= object.bytes) {
      return Status{ErrorCode::protocol_error,
                    "moved sync partial is not an incomplete object"};
    }
    return SyncAttemptPartial{next, moved_bytes.value()};
  }
  struct stat target {};
  if (::lstat(next.c_str(), &target) == 0) {
    return Status{ErrorCode::invalid_argument,
                  "next sync attempt staging path already exists"};
  }
  if (errno != ENOENT) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect next sync attempt path", next);
  }
#if defined(SYS_renameat2) && defined(RENAME_NOREPLACE)
  if (::syscall(SYS_renameat2, AT_FDCWD, prior.c_str(), AT_FDCWD,
                next.c_str(), RENAME_NOREPLACE) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to hand off sync attempt partial", next);
  }
#else
  return Status{ErrorCode::unsupported,
                "atomic no-clobber sync partial handoff is unavailable"};
#endif
  const Status synced = fsync_directory(next.parent_path());
  if (!synced.ok()) return synced;
  auto moved_bytes = private_object_size(next);
  if (!moved_bytes) return moved_bytes.status();
  if (moved_bytes.value() != inspected.value().bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync partial changed across attempt handoff"};
  }
  return SyncAttemptPartial{next, moved_bytes.value()};
}

Status cleanup_inactive_sync_attempt_partials(
    const NamespacePolicy &policy, std::uint64_t high_attempt_id,
    std::span<const std::uint64_t> active_attempt_ids,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if ((high_attempt_id == 0U && !active_attempt_ids.empty()) ||
      std::any_of(
          active_attempt_ids.begin(), active_attempt_ids.end(),
          [high_attempt_id](std::uint64_t attempt_id) {
            return attempt_id == 0U || attempt_id > high_attempt_id;
          })) {
    return Status{ErrorCode::invalid_argument,
                  "inactive sync partial cleanup bounds are invalid"};
  }
  const std::filesystem::path staging =
      std::filesystem::path(policy.root) / "staging";
  struct stat directory_metadata {};
  if (::lstat(staging.c_str(), &directory_metadata) != 0) {
    return errno == ENOENT
        ? Status::success()
        : system_status(ErrorCode::io_error,
                        "unable to inspect sync staging directory", staging);
  }
  if (!S_ISDIR(directory_metadata.st_mode) ||
      directory_metadata.st_uid != ::geteuid() ||
      (directory_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync staging directory is not private and owner-owned"};
  }

  std::size_t inspected = 0U;
  bool removed = false;
  std::error_code error;
  for (std::filesystem::directory_iterator iterator(staging, error), end;
       !error && iterator != end; iterator.increment(error)) {
    if (++inspected > 65536U) {
      return Status{ErrorCode::resource_exhausted,
                    "sync staging recovery entry bound is exhausted"};
    }
    const auto attempt_id = parse_attempt_staging_name(
        iterator->path().filename().string());
    if (!attempt_id) continue;
    if (*attempt_id == 0U || *attempt_id > high_attempt_id) {
      return Status{ErrorCode::protocol_error,
                    "sync staging contains an unburned canonical attempt path"};
    }
    if (std::find(
            active_attempt_ids.begin(), active_attempt_ids.end(),
            *attempt_id) != active_attempt_ids.end()) {
      continue;
    }
    auto shape = private_object_size(iterator->path());
    if (!shape) return shape.status();
    if (::unlink(iterator->path().c_str()) != 0) {
      return system_status(ErrorCode::io_error,
                           "unable to remove inactive sync attempt partial",
                           iterator->path());
    }
    removed = true;
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync staging recovery: " +
                      error.message()};
  }
  return removed ? fsync_directory(staging) : Status::success();
}

Result<SyncStagedObjectCommitResult> commit_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams, std::uint64_t copy_chunk_bytes) {
  const Status valid = validate_staged_object(policy, attempt_id, object);
  if (!valid.ok()) return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync staged commit requires an injected file hasher"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync staged commit cancelled before verification"};
  }

  SyncStagedObjectCommitResult result;
  result.object = object;
  result.staging_path = staged_attempt_path(policy, attempt_id);
  result.object_path = sync_object_path(policy, object);
  auto staged_bytes = private_object_size(result.staging_path);
  if (!staged_bytes.ok()) return staged_bytes.status();
  if (staged_bytes.value() != object.bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync staged file size does not match immutable object"};
  }
  auto staged_digest = seams.hash_file(result.staging_path);
  if (!staged_digest.ok()) return staged_digest.status();
  if (staged_digest.value() != object.identity) {
    return Status{ErrorCode::protocol_error,
                  "sync staged file digest does not match immutable object"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync staged commit cancelled after verification"};
  }

  const std::filesystem::path objects = std::filesystem::path(policy.root) /
                                        "objects";
  Status prepared = ensure_private_directory(objects);
  if (!prepared.ok()) return prepared;
  auto inventory = inspect_sync_object_store(policy, transaction);
  if (!inventory.ok()) return inventory.status();
  struct stat existing {};
  const bool object_exists = ::lstat(result.object_path.c_str(), &existing) == 0;
  if (!object_exists && errno != ENOENT) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync object destination",
                         result.object_path);
  }
  const std::uint64_t added_objects = object_exists ? 0U : 1U;
  const std::uint64_t added_bytes = object_exists ? 0U : object.bytes;
  if (inventory.value().objects >
          policy.quotas.maximum_objects - added_objects ||
      inventory.value().bytes >
          policy.quotas.maximum_store_bytes - added_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync staged commit would exceed whole-store quotas"};
  }
  auto installed = ensure_object(
      result.staging_path, result.object_path,
      std::filesystem::path(policy.root) / "staging", object.identity,
      object.bytes, copy_chunk_bytes, seams);
  if (!installed.ok()) return installed.status();
  result.installed = installed.value();
  if (::unlink(result.staging_path.c_str()) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to remove committed sync staging file",
                         result.staging_path);
  }
  const Status synced = fsync_directory(result.staging_path.parent_path());
  if (!synced.ok()) return synced;
  return result;
}

Status discard_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (attempt_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt identifier zero is reserved"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const std::filesystem::path path = staged_attempt_path(policy, attempt_id);
  const std::filesystem::path staging = path.parent_path();
  std::filesystem::path reconstruction_partial = path;
  reconstruction_partial += ".toxsync.part";
  bool removed = false;
  bool final_present = false;
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) == 0) {
    auto shape = private_object_size(path);
    if (!shape.ok()) return shape.status();
    final_present = true;
  } else if (errno != ENOENT) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync attempt staging path", path);
  }

  struct stat directory_metadata {};
  if (::lstat(staging.c_str(), &directory_metadata) != 0) {
    if (errno == ENOENT && !removed) return Status::success();
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync staging directory", staging);
  }
  if (!S_ISDIR(directory_metadata.st_mode) ||
      directory_metadata.st_uid != ::geteuid() ||
      (directory_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync staging directory is not private and owner-owned"};
  }

  const std::string prefix = transport_staging_prefix(attempt_id);
  std::vector<std::filesystem::path> transport_temporaries;
  std::error_code error;
  for (std::filesystem::directory_iterator iterator(staging, error), end;
       !error && iterator != end; iterator.increment(error)) {
    const std::string name = iterator->path().filename().string();
    if (!name.starts_with(prefix)) continue;
    if (!valid_mkstemp_suffix(
            std::string_view{name}.substr(prefix.size()))) {
      return Status{ErrorCode::protocol_error,
                    "sync attempt transport temporary name is invalid"};
    }
    auto shape = private_object_size(iterator->path());
    if (!shape.ok()) return shape.status();
    transport_temporaries.push_back(iterator->path());
    if (transport_temporaries.size() > 1U) {
      return Status{ErrorCode::protocol_error,
                    "sync attempt has multiple transport temporaries"};
    }
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync staging directory: " +
                      error.message()};
  }
  if (final_present) {
    if (::unlink(path.c_str()) != 0) {
      return system_status(ErrorCode::io_error,
                           "unable to discard sync attempt staging file", path);
    }
    removed = true;
  }
  struct stat partial_metadata {};
  if (::lstat(reconstruction_partial.c_str(), &partial_metadata) == 0) {
    auto shape = private_object_size(reconstruction_partial);
    if (!shape.ok()) return shape.status();
    if (::unlink(reconstruction_partial.c_str()) != 0) {
      return system_status(
          ErrorCode::io_error,
          "unable to discard sync range reconstruction partial",
          reconstruction_partial);
    }
    removed = true;
  } else if (errno != ENOENT) {
    return system_status(
        ErrorCode::io_error,
        "unable to inspect sync range reconstruction partial",
        reconstruction_partial);
  }
  for (const std::filesystem::path &temporary : transport_temporaries) {
    if (::unlink(temporary.c_str()) != 0) {
      return system_status(
          ErrorCode::io_error,
          "unable to discard sync attempt transport temporary", temporary);
    }
    removed = true;
  }
  return removed ? fsync_directory(staging) : Status::success();
}

Status verify_sync_object(
    const NamespacePolicy &policy, const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams) {
  const Status valid = validate_staged_object(policy, 1U, object);
  if (!valid.ok()) return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync object verification requires an injected file hasher"};
  }
  auto records = inspect_sync_object_records(policy, transaction);
  if (!records) return records.status();
  const auto found = std::find_if(
      records.value().begin(), records.value().end(),
      [&object](const SyncObjectRecord &record) {
        return record.kind == object.kind &&
               record.identity == object.identity;
      });
  if (found == records.value().end()) {
    return Status{ErrorCode::not_found,
                  "sync immutable object is absent"};
  }
  if (found->bytes != object.bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync immutable object size conflicts with its record"};
  }
  auto observed = seams.hash_file(sync_object_path(policy, object));
  if (!observed) return observed.status();
  if (observed.value() != object.identity) {
    return Status{ErrorCode::protocol_error,
                  "sync immutable object digest conflicts with its name"};
  }
  return Status::success();
}

Result<SyncObjectInventory>
inspect_sync_object_store(const NamespacePolicy &policy) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return inspect_sync_object_store(policy, transaction.value());
}

Result<SyncObjectInventory>
inspect_sync_object_store(const NamespacePolicy &policy,
                          const SyncNamespaceTransaction &transaction) {
  auto records = inspect_sync_object_records(policy, transaction);
  if (!records.ok())
    return records.status();
  SyncObjectInventory inventory;
  for (const SyncObjectRecord &record : records.value()) {
    ++inventory.objects;
    inventory.bytes += record.bytes;
    inventory.artifacts += record.kind == SyncObjectKind::artifact ? 1U : 0U;
    inventory.manifests += record.kind == SyncObjectKind::manifest ? 1U : 0U;
  }
  return inventory;
}

Result<std::vector<SyncObjectRecord>>
inspect_sync_object_records(const NamespacePolicy &policy) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return inspect_sync_object_records(policy, transaction.value());
}

Result<std::vector<SyncObjectRecord>> inspect_sync_object_records(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const std::filesystem::path objects =
      std::filesystem::path(policy.root) / "objects";
  struct stat directory_metadata {};
  if (::lstat(objects.c_str(), &directory_metadata) != 0) {
    if (errno == ENOENT)
      return std::vector<SyncObjectRecord>{};
    return system_status(ErrorCode::io_error,
                         "unable to inspect sync object directory", objects);
  }
  if (!S_ISDIR(directory_metadata.st_mode) ||
      directory_metadata.st_uid != ::geteuid() ||
      (directory_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync object directory is not private and owner-owned"};
  }

  std::vector<SyncObjectRecord> records;
  std::uint64_t total_bytes = 0U;
  std::error_code error;
  for (std::filesystem::directory_iterator iterator(objects, error), end;
       !error && iterator != end; iterator.increment(error)) {
    const std::string name = iterator->path().filename().string();
    const bool artifact = valid_object_name(name, ".artifact");
    const bool manifest = valid_object_name(name, ".manifest");
    if (!artifact && !manifest) {
      return Status{ErrorCode::protocol_error,
                    "sync object directory contains an unexpected entry"};
    }
    auto size = private_object_size(iterator->path());
    if (!size.ok())
      return size.status();
    if (size.value() == 0U ||
        (artifact &&
         size.value() > policy.quotas.maximum_artifact_bytes) ||
        (manifest &&
         size.value() > policy.quotas.maximum_manifest_bytes) ||
        records.size() >= policy.quotas.maximum_objects ||
        total_bytes >
            std::numeric_limits<std::uint64_t>::max() - size.value()) {
      return Status{ErrorCode::resource_exhausted,
                    "sync object inventory size is invalid"};
    }
    records.push_back(SyncObjectRecord{
        artifact ? SyncObjectKind::artifact : SyncObjectKind::manifest,
        object_name_digest(name), size.value()});
    total_bytes += size.value();
    if (total_bytes > policy.quotas.maximum_store_bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "sync object store exceeds namespace quotas"};
    }
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync object directory: " +
                      error.message()};
  }
  std::sort(records.begin(), records.end(),
            [](const SyncObjectRecord &left, const SyncObjectRecord &right) {
              if (left.kind != right.kind)
                return left.kind < right.kind;
              return left.identity < right.identity;
            });
  if (std::adjacent_find(
          records.begin(), records.end(),
          [](const SyncObjectRecord &left, const SyncObjectRecord &right) {
            return left.kind == right.kind && left.identity == right.identity;
          }) != records.end()) {
    return Status{ErrorCode::protocol_error,
                  "sync object inventory contains duplicate identities"};
  }
  return records;
}

Result<SyncObjectStoreRepairResult>
repair_sync_object_store(const NamespacePolicy &policy,
                         const SyncInstallSeams &seams) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return repair_sync_object_store(policy, transaction.value(), seams);
}

Result<SyncObjectStoreRepairResult>
repair_sync_object_store(const NamespacePolicy &policy,
                         const SyncNamespaceTransaction &transaction,
                         const SyncInstallSeams &seams) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync object repair requires an injected file hasher"};
  }
  auto records = inspect_sync_object_records(policy, transaction);
  if (!records.ok())
    return records.status();

  SyncObjectStoreRepairResult result;
  result.quarantined.reserve(records.value().size());
  for (const SyncObjectRecord &record : records.value()) {
    ++result.inspected_objects;
    result.inspected_bytes += record.bytes;
    auto observed = seams.hash_file(sync_object_path(policy, record));
    if (!observed.ok())
      return observed.status();
    if (observed.value() == record.identity) {
      ++result.verified_objects;
      continue;
    }
    result.quarantined.push_back(record);
    ++result.quarantined_objects;
    result.quarantined_bytes += record.bytes;
  }
  if (result.quarantined.empty())
    return result;

  const std::filesystem::path root{policy.root};
  const std::filesystem::path objects = root / "objects";
  const std::filesystem::path quarantine = root / "quarantine";
  Status prepared = ensure_private_directory(quarantine);
  if (!prepared.ok())
    return prepared;

  std::uint64_t sequence = 0U;
  for (const SyncObjectRecord &record : result.quarantined) {
    const std::filesystem::path source = sync_object_path(policy, record);
    std::filesystem::path destination;
    for (std::uint64_t attempt = 1U; attempt <= 1024U; ++attempt) {
      const std::string name =
          source.filename().string() + ".corrupt-" + attempt_hex(sequence + attempt);
      const std::filesystem::path candidate = quarantine / name;
      struct stat candidate_metadata {};
      if (::lstat(candidate.c_str(), &candidate_metadata) != 0) {
        if (errno == ENOENT) {
          destination = candidate;
          sequence += attempt;
          break;
        }
        return system_status(ErrorCode::io_error,
                             "unable to inspect sync quarantine target",
                             candidate);
      }
    }
    if (destination.empty()) {
      return Status{ErrorCode::resource_exhausted,
                    "sync quarantine destination bound is exhausted"};
    }
    auto shape = private_object_size(source);
    if (!shape.ok())
      return shape.status();
    if (shape.value() != record.bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync object changed before quarantine"};
    }
    if (::rename(source.c_str(), destination.c_str()) != 0) {
      return system_status(ErrorCode::io_error,
                           "unable to quarantine corrupt sync object", source);
    }
  }
  Status synced = fsync_directory(objects);
  if (!synced.ok())
    return synced;
  synced = fsync_directory(quarantine);
  if (!synced.ok())
    return synced;
  return result;
}

Result<SyncInstallResult>
install_local_artifact(const SyncInstallRequest &request,
                       const security::DeviceIdentity &identity,
                       const security::Sodium &sodium,
                       const SyncInstallSeams &seams) {
  const Status valid_policy = validate_namespace_policy(request.policy);
  if (!valid_policy.ok()) {
    return valid_policy;
  }
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync install requires an injected file hasher"};
  }
  if (request.source_path.empty() || !request.source_path.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "sync source path must be absolute"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable, "sync install cancelled before evaluation"};
  }

  const std::filesystem::path root{request.policy.root};
  SyncInstallResult result;
  result.object_path = root / "objects" /
                       (hex_encode(request.candidate.artifact) + ".artifact");
  result.bytes = request.candidate.artifact_bytes;
  const HeadAcceptanceResult preflight = evaluate_candidate_head(
      request.policy, request.candidate, std::nullopt, request.acceptance);
  if (preflight.decision == HeadAcceptanceDecision::wrong_namespace ||
      preflight.decision == HeadAcceptanceDecision::unauthorized_writer ||
      preflight.decision == HeadAcceptanceDecision::engine_mismatch ||
      preflight.decision == HeadAcceptanceDecision::resource_limit) {
    result.head = preflight;
    return result;
  }

  auto transaction = SyncNamespaceTransaction::acquire(request.policy);
  if (!transaction.ok())
    return transaction.status();

  Result<std::shared_ptr<SyncGuardedStateWitness>> witness{
      std::shared_ptr<SyncGuardedStateWitness>{}};
  if (seams.guarded_state_witness) {
    witness = seams.guarded_state_witness(request.policy);
    if (!witness) return witness.status();
  }
  if (witness.value()) {
    const Status verified = witness.value()->verify_read(
        request.policy, transaction.value());
    if (!verified.ok()) return verified;
  }
  AcceptedHeadStore store(root, witness.value());
  auto current = store.load(request.policy, identity.public_key(), sodium);
  if (!current.ok()) {
    return current.status();
  }
  HeadAcceptanceResult evaluated =
      evaluate_candidate_head(request.policy, request.candidate, current.value(),
                              request.acceptance);
  result.head = evaluated;
  if (!evaluated.accepted() ||
      evaluated.decision == HeadAcceptanceDecision::duplicate) {
    return result;
  }

  auto source_size = regular_file_size(request.source_path, "sync source");
  if (!source_size.ok()) {
    return source_size.status();
  }
  if (source_size.value() != request.candidate.artifact_bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync source size does not match candidate artifact size"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable, "sync install cancelled before hash"};
  }

  auto source_digest = seams.hash_file(request.source_path);
  if (!source_digest.ok()) {
    return source_digest.status();
  }
  if (source_digest.value() != request.candidate.artifact) {
    return Status{ErrorCode::protocol_error,
                  "sync source digest does not match candidate artifact"};
  }

  const std::filesystem::path objects = root / "objects";
  const std::filesystem::path staging = root / "staging";
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok()) {
    return prepared;
  }
  prepared = ensure_private_directory(objects);
  if (!prepared.ok()) {
    return prepared;
  }
  prepared = ensure_private_directory(staging);
  if (!prepared.ok()) {
    return prepared;
  }

  auto inventory =
      inspect_sync_object_store(request.policy, transaction.value());
  if (!inventory.ok())
    return inventory.status();
  std::error_code object_exists_error;
  const bool object_exists =
      std::filesystem::exists(result.object_path, object_exists_error);
  if (object_exists_error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect accepted artifact identity"};
  }
  const std::uint64_t added_objects = object_exists ? 0U : 1U;
  const std::uint64_t added_bytes = object_exists ? 0U : result.bytes;
  if (inventory.value().objects >
          request.policy.quotas.maximum_objects - added_objects ||
      inventory.value().bytes >
          request.policy.quotas.maximum_store_bytes - added_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync install would exceed whole-store quotas"};
  }

  auto installed =
      ensure_object(request.source_path, result.object_path, staging,
                    request.candidate.artifact, request.candidate.artifact_bytes,
                    request.copy_chunk_bytes, seams);
  if (!installed.ok()) {
    return installed.status();
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync install cancelled before accepted-head commit"};
  }

  auto accepted = store.accept(request.policy, request.candidate, identity,
                               sodium, request.acceptance,
                               transaction.value());
  if (!accepted.ok()) {
    return accepted.status();
  }
  result.head = accepted.value();
  result.installed = installed.value();
  result.activated = false;
  return result;
}

Result<SyncPublishJobResult> publish_local_revision(
    const SyncPublishJobRequest &request,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    SignedHeadStore &store, const SyncInstallSeams &seams) {
  const Status valid_policy = validate_namespace_policy(request.policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync publication requires an injected file hasher"};
  }
  if (request.artifact_source_path.empty() ||
      !request.artifact_source_path.is_absolute() ||
      request.manifest_source_path.empty() ||
      !request.manifest_source_path.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "sync publication source paths must be absolute"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync publication cancelled before source inspection"};
  }

  auto artifact_bytes =
      regular_file_size(request.artifact_source_path, "sync artifact source");
  if (!artifact_bytes.ok())
    return artifact_bytes.status();
  auto manifest_bytes =
      regular_file_size(request.manifest_source_path, "sync manifest source");
  if (!manifest_bytes.ok())
    return manifest_bytes.status();
  if (artifact_bytes.value() == 0U || manifest_bytes.value() == 0U ||
      artifact_bytes.value() > request.policy.quotas.maximum_artifact_bytes ||
      manifest_bytes.value() > request.policy.quotas.maximum_manifest_bytes ||
      manifest_bytes.value() > request.policy.quotas.maximum_store_bytes ||
      artifact_bytes.value() >
          request.policy.quotas.maximum_store_bytes - manifest_bytes.value()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync publication inputs exceed namespace quotas"};
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync publication cancelled before source hashing"};
  }
  auto artifact_digest = seams.hash_file(request.artifact_source_path);
  if (!artifact_digest.ok())
    return artifact_digest.status();
  auto manifest_digest = seams.hash_file(request.manifest_source_path);
  if (!manifest_digest.ok())
    return manifest_digest.status();
  if (all_zero(artifact_digest.value()) || all_zero(manifest_digest.value())) {
    return Status{ErrorCode::protocol_error,
                  "sync publication source digest is zero"};
  }
  if (seams.validate_revision_sources) {
    const Status semantic = seams.validate_revision_sources(
        request.artifact_source_path, request.manifest_source_path,
        artifact_digest.value(), artifact_bytes.value(),
        manifest_bytes.value());
    if (!semantic.ok()) return semantic;
  }
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync publication cancelled before object commit"};
  }

  auto transaction = SyncNamespaceTransaction::acquire(request.policy);
  if (!transaction.ok())
    return transaction.status();

  const std::filesystem::path root{request.policy.root};
  const std::filesystem::path objects = root / "objects";
  const std::filesystem::path staging = root / "staging";
  SyncPublishJobResult result;
  result.artifact_object_path =
      objects / (hex_encode(artifact_digest.value()) + ".artifact");
  result.manifest_object_path =
      objects / (hex_encode(manifest_digest.value()) + ".manifest");

  Status prepared = ensure_private_directory(root);
  if (!prepared.ok())
    return prepared;
  prepared = ensure_private_directory(objects);
  if (!prepared.ok())
    return prepared;
  prepared = ensure_private_directory(staging);
  if (!prepared.ok())
    return prepared;

  auto inventory =
      inspect_sync_object_store(request.policy, transaction.value());
  if (!inventory.ok())
    return inventory.status();
  std::error_code artifact_exists_error;
  const bool artifact_exists =
      std::filesystem::exists(result.artifact_object_path,
                              artifact_exists_error);
  if (artifact_exists_error)
    return Status{ErrorCode::io_error, "unable to inspect artifact identity"};
  std::error_code manifest_exists_error;
  const bool manifest_exists =
      std::filesystem::exists(result.manifest_object_path,
                              manifest_exists_error);
  if (manifest_exists_error)
    return Status{ErrorCode::io_error, "unable to inspect manifest identity"};
  const std::uint64_t added_objects =
      (artifact_exists ? 0U : 1U) + (manifest_exists ? 0U : 1U);
  const std::uint64_t added_bytes =
      (artifact_exists ? 0U : artifact_bytes.value()) +
      (manifest_exists ? 0U : manifest_bytes.value());
  if (added_objects > request.policy.quotas.maximum_objects ||
      added_bytes > request.policy.quotas.maximum_store_bytes ||
      inventory.value().objects >
          request.policy.quotas.maximum_objects - added_objects ||
      inventory.value().bytes >
          request.policy.quotas.maximum_store_bytes - added_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync publication would exceed whole-store quotas"};
  }

  auto artifact_installed = ensure_object(
      request.artifact_source_path, result.artifact_object_path, staging,
      artifact_digest.value(), artifact_bytes.value(), request.copy_chunk_bytes,
      seams);
  if (!artifact_installed.ok())
    return artifact_installed.status();
  result.artifact_installed = artifact_installed.value();
  auto manifest_installed = ensure_object(
      request.manifest_source_path, result.manifest_object_path, staging,
      manifest_digest.value(), manifest_bytes.value(), request.copy_chunk_bytes,
      seams);
  if (!manifest_installed.ok())
    return manifest_installed.status();
  result.manifest_installed = manifest_installed.value();
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "sync publication cancelled before signed HEAD commit"};
  }

  SignedHeadPublicationRequest publication;
  publication.artifact = artifact_digest.value();
  publication.manifest = manifest_digest.value();
  publication.artifact_bytes = artifact_bytes.value();
  publication.manifest_bytes = manifest_bytes.value();
  auto published = store.publish(request.policy, publication, identity, sodium,
                                 transaction.value());
  if (!published.ok())
    return published.status();
  result.publication = std::move(published.value());
  return result;
}

} // namespace iotox::sync
