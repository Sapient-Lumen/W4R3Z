#include "iotox/sync_content_attempt_store.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <string>
#include <sys/stat.h>
#include <tuple>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {'I', 'O', 'T', 'X',
                                                 'C', 'T', 'A', '1'};
constexpr std::string_view kSignatureDomain =
    "iotox-sync-content-attempt-signature-v1";
constexpr std::string_view kRecordDomain =
    "iotox-sync-content-attempt-record-v1";
constexpr std::size_t kHeaderBytes = 192U;
constexpr std::size_t kAttemptBytes = 288U;
constexpr std::size_t kSignerOffset = 40U;
constexpr std::size_t kPreviousOffset = 72U;
constexpr std::size_t kNamespaceOffset = 104U;
constexpr std::size_t kNamespaceBytes = 64U;

void write_u32(std::span<std::uint8_t> output, std::size_t offset,
               std::uint32_t value) {
  for (std::size_t index = 0U; index < 4U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> (24U - index * 8U));
  }
}

std::uint32_t read_u32(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  std::uint32_t value = 0U;
  for (std::size_t index = 0U; index < 4U; ++index) {
    value = static_cast<std::uint32_t>((value << 8U) | input[offset + index]);
  }
  return value;
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> (56U - index * 8U));
  }
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index) {
    value = (value << 8U) | input[offset + index];
  }
  return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
  std::copy(value.begin(), value.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
  std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), Size,
              value.begin());
}

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

bool valid_carrier(const SyncTransferCarrier &carrier) {
  if (carrier.worker_id == 0U || carrier.online_epoch == 0U ||
      all_zero(carrier.route_key)) {
    return false;
  }
  if (carrier.carrier_class == SyncCarrierClass::primary) {
    return carrier.worker_id == carrier.online_epoch &&
           carrier.remote_route_generation == 0U &&
           all_zero(carrier.remote_coordinator_route_key) &&
           carrier.primary_authority_online_epoch == 0U;
  }
  return carrier.carrier_class == SyncCarrierClass::auxiliary &&
         carrier.remote_route_generation != 0U &&
         !all_zero(carrier.remote_coordinator_route_key) &&
         carrier.primary_authority_online_epoch != 0U;
}

Status validate_attempt(const DurableSyncContentAttempt &attempt) {
  if (attempt.attempt_id == 0U || attempt.request_id == 0U ||
      attempt.source_id == 0U || all_zero(attempt.head_record) ||
      all_zero(attempt.object) || attempt.object_bytes == 0U ||
      all_zero(attempt.file_id) || all_zero(attempt.source_principal) ||
      (attempt.kind != SyncContentObjectKind::manifest_page &&
       attempt.kind != SyncContentObjectKind::artifact_chunk &&
       attempt.kind != SyncContentObjectKind::root_manifest) ||
      !valid_carrier(attempt.carrier)) {
    return Status{ErrorCode::invalid_argument,
                  "durable content attempt identity is invalid"};
  }
  return Status::success();
}

Status validate_journal_shape(const SyncContentAttemptJournal &journal,
                              std::size_t maximum_active_attempts) {
  if (!valid_namespace_id(journal.namespace_id) ||
      maximum_active_attempts == 0U || maximum_active_attempts > 65536U ||
      journal.active.size() > maximum_active_attempts ||
      journal.high_attempt_id == 0U || journal.mutation == 0U ||
      all_zero(journal.signer) ||
      (journal.mutation == 1U && !all_zero(journal.previous)) ||
      (journal.mutation != 1U && all_zero(journal.previous))) {
    return Status{ErrorCode::invalid_argument,
                  "content attempt journal header is invalid"};
  }
  std::uint64_t prior_attempt = 0U;
  std::vector<std::uint64_t> requests;
  std::vector<FileId> file_ids;
  std::vector<std::tuple<Digest, std::uint8_t, std::uint64_t>> logical;
  requests.reserve(journal.active.size());
  file_ids.reserve(journal.active.size());
  logical.reserve(journal.active.size());
  for (const DurableSyncContentAttempt &attempt : journal.active) {
    const Status valid = validate_attempt(attempt);
    if (!valid.ok() || attempt.attempt_id <= prior_attempt ||
        attempt.attempt_id > journal.high_attempt_id) {
      return Status{ErrorCode::invalid_argument,
                    "content attempt entries are invalid or unsorted"};
    }
    prior_attempt = attempt.attempt_id;
    requests.push_back(attempt.request_id);
    file_ids.push_back(attempt.file_id);
    logical.emplace_back(attempt.head_record,
                         static_cast<std::uint8_t>(attempt.kind),
                         attempt.logical_index);
  }
  std::sort(requests.begin(), requests.end());
  std::sort(file_ids.begin(), file_ids.end());
  std::sort(logical.begin(), logical.end());
  if (std::adjacent_find(requests.begin(), requests.end()) != requests.end() ||
      std::adjacent_find(file_ids.begin(), file_ids.end()) != file_ids.end() ||
      std::adjacent_find(logical.begin(), logical.end()) != logical.end()) {
    return Status{ErrorCode::invalid_argument,
                  "content attempt journal aliases active work"};
  }
  return Status::success();
}

Status validate_journal_policy(const SyncContentAttemptJournal &journal,
                               const NamespacePolicy &policy,
                               std::size_t maximum_active_attempts) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  const Status valid = validate_journal_shape(journal, maximum_active_attempts);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2 ||
      journal.namespace_id != policy.id ||
      journal.active.size() > policy.quotas.maximum_outstanding_requests) {
    return Status{ErrorCode::protocol_error,
                  "content attempt journal conflicts with namespace policy"};
  }
  for (const DurableSyncContentAttempt &attempt : journal.active) {
    const std::uint64_t kind_limit =
        (attempt.kind == SyncContentObjectKind::manifest_page ||
         attempt.kind == SyncContentObjectKind::root_manifest)
            ? policy.quotas.maximum_manifest_bytes
            : policy.quotas.maximum_artifact_bytes;
    if (attempt.object_bytes > kind_limit ||
        attempt.object_bytes > policy.quotas.maximum_staging_bytes ||
        attempt.object_bytes > policy.quotas.maximum_store_bytes) {
      return Status{ErrorCode::protocol_error,
                    "content attempt object exceeds namespace policy"};
    }
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_body(const SyncContentAttemptJournal &journal) {
  const Status valid = validate_journal_shape(journal, 65536U);
  if (!valid.ok())
    return valid;
  if (journal.active.size() >
      (std::numeric_limits<std::size_t>::max() - kHeaderBytes) /
          kAttemptBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "content attempt journal encoding is too large"};
  }
  std::vector<std::uint8_t> output(
      kHeaderBytes + journal.active.size() * kAttemptBytes, 0U);
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = static_cast<std::uint8_t>(journal.namespace_id.size());
  write_u64(output, 16U, journal.mutation);
  write_u64(output, 24U, journal.high_attempt_id);
  write_u64(output, 32U, journal.active.size());
  write_array(output, kSignerOffset, journal.signer);
  write_array(output, kPreviousOffset, journal.previous);
  std::copy(journal.namespace_id.begin(), journal.namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
  std::size_t offset = kHeaderBytes;
  for (const DurableSyncContentAttempt &attempt : journal.active) {
    write_u64(output, offset, attempt.attempt_id);
    output[offset + 8U] = static_cast<std::uint8_t>(attempt.kind);
    output[offset + 9U] =
        static_cast<std::uint8_t>(attempt.carrier.carrier_class);
    write_u64(output, offset + 16U, attempt.request_id);
    write_u64(output, offset + 24U, attempt.source_id);
    write_u64(output, offset + 32U, attempt.logical_index);
    write_u64(output, offset + 40U, attempt.object_bytes);
    write_u64(output, offset + 48U, attempt.carrier.worker_id);
    write_u64(output, offset + 56U, attempt.carrier.online_epoch);
    write_u64(output, offset + 64U, attempt.carrier.remote_route_generation);
    write_u64(output, offset + 72U,
              attempt.carrier.primary_authority_online_epoch);
    write_u32(output, offset + 80U, attempt.carrier.friend_number);
    write_array(output, offset + 96U, attempt.head_record);
    write_array(output, offset + 128U, attempt.object);
    write_array(output, offset + 160U, attempt.file_id);
    write_array(output, offset + 192U, attempt.carrier.route_key);
    write_array(output, offset + 224U,
                attempt.carrier.remote_coordinator_route_key);
    write_array(output, offset + 256U, attempt.source_principal);
    offset += kAttemptBytes;
  }
  return output;
}

Status prepare_private_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) == 0) {
    if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0700)) {
      return Status{ErrorCode::protocol_error,
                    "content attempt directory is not private and owner-owned"};
    }
    return Status::success();
  }
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt directory: " +
                      std::string(std::strerror(errno))};
  }
  std::error_code error;
  std::filesystem::create_directory(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create content attempt directory: " +
                      error.message()};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure content attempt directory: " +
                      error.message()};
  }
  return Status::success();
}

Status validate_private_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
      S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "content attempt directory is not private and owner-owned"};
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

Result<std::vector<std::uint8_t>>
read_private_file(const std::filesystem::path &path,
                  std::size_t maximum_active_attempts) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found, "content attempt journal is absent"};
    }
    return Status{ErrorCode::io_error,
                  "unable to open content attempt journal: " +
                      std::string(std::strerror(errno))};
  }
  struct stat before {};
  if (::fstat(descriptor, &before) != 0) {
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt journal: " +
                      std::string(std::strerror(saved))};
  }
  const std::uint64_t maximum_bytes =
      kHeaderBytes +
      static_cast<std::uint64_t>(maximum_active_attempts) * kAttemptBytes +
      security::kSignatureBytes;
  if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
      before.st_uid != ::geteuid() ||
      (before.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      before.st_size <
          static_cast<off_t>(kHeaderBytes + security::kSignatureBytes) ||
      static_cast<std::uint64_t>(before.st_size) > maximum_bytes) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "content attempt journal is not one bounded private file"};
  }
  std::vector<std::uint8_t> bytes(static_cast<std::size_t>(before.st_size));
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::read(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete content attempt journal"};
  }
  struct stat after {};
  if (::fstat(descriptor, &after) != 0 || !same_snapshot(before, after)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "content attempt journal changed while read"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close content attempt journal"};
  }
  return bytes;
}

Status validate_store(const std::filesystem::path &root,
                      const SyncContentAttemptStore::Config &config,
                      const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2 ||
      config.maximum_active_attempts == 0U ||
      config.maximum_active_attempts > 65536U ||
      root.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "content attempt store configuration is invalid"};
  }
  return Status::success();
}

Status prepare_parent(const std::filesystem::path &root) {
  const Status private_root = validate_private_directory(root);
  if (!private_root.ok())
    return private_root;
  return prepare_private_directory(root / "content-attempts");
}

Status advance_and_sign(SyncContentAttemptJournal &journal,
                        const security::DeviceIdentity &identity,
                        const security::Sodium &sodium) {
  if (journal.mutation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "content attempt mutation counter is exhausted"};
  }
  if (journal.mutation == 0U) {
    journal.mutation = 1U;
    journal.previous = Digest{};
  } else {
    auto previous = sync_content_attempt_journal_digest(journal, sodium);
    if (!previous)
      return previous.status();
    journal.previous = previous.value();
    ++journal.mutation;
  }
  journal.signer = identity.public_key();
  auto body = encode_body(journal);
  if (!body)
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest)
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature)
    return signature.status();
  journal.signature = signature.value();
  return Status::success();
}

Status fsync_directory(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
  if (descriptor < 0) {
    return Status{ErrorCode::io_error,
                  "unable to open content staging directory: " +
                      std::string(std::strerror(errno))};
  }
  const int result = ::fsync(descriptor);
  const int saved = errno;
  static_cast<void>(::close(descriptor));
  if (result != 0) {
    return Status{ErrorCode::io_error,
                  "unable to sync content staging directory: " +
                      std::string(std::strerror(saved))};
  }
  return Status::success();
}

bool lowercase_hex(std::string_view value) noexcept {
  return std::all_of(value.begin(), value.end(), [](char byte) {
    return (byte >= '0' && byte <= '9') || (byte >= 'a' && byte <= 'f');
  });
}

bool base62(std::string_view value) noexcept {
  return std::all_of(value.begin(), value.end(), [](char byte) {
    return (byte >= '0' && byte <= '9') || (byte >= 'A' && byte <= 'Z') ||
           (byte >= 'a' && byte <= 'z');
  });
}

bool canonical_attempt_filename(std::string_view name) noexcept {
  constexpr std::string_view suffix = ".part";
  if (name.size() <= 62U + 1U + suffix.size() ||
      !lowercase_hex(name.substr(0U, 62U)) || name[62U] != '.' ||
      !name.ends_with(suffix)) {
    return false;
  }
  const std::string_view request =
      name.substr(63U, name.size() - 63U - suffix.size());
  if (request.empty() || request.front() == '0' ||
      !std::all_of(request.begin(), request.end(),
                   [](char byte) { return byte >= '0' && byte <= '9'; })) {
    return false;
  }
  std::uint64_t parsed = 0U;
  const auto converted =
      std::from_chars(request.data(), request.data() + request.size(), parsed);
  return converted.ec == std::errc{} &&
         converted.ptr == request.data() + request.size() && parsed != 0U;
}

bool transport_attempt_filename(std::string_view name) noexcept {
  constexpr std::string_view prefix = ".iotox-";
  constexpr std::string_view marker = ".part-";
  constexpr std::size_t random_bytes = 6U;
  if (!name.starts_with(prefix) ||
      name.size() <= prefix.size() + marker.size() + random_bytes) {
    return false;
  }
  name.remove_prefix(prefix.size());
  const std::size_t marker_offset = name.size() - marker.size() - random_bytes;
  return name.substr(marker_offset, marker.size()) == marker &&
         canonical_attempt_filename(name.substr(0U, marker_offset)) &&
         base62(name.substr(marker_offset + marker.size(), random_bytes));
}

Status private_entry_on_device(const struct stat &metadata, dev_t device,
                               bool directory) {
  const bool expected_kind =
      directory ? S_ISDIR(metadata.st_mode) : S_ISREG(metadata.st_mode);
  const mode_t expected_mode =
      directory ? static_cast<mode_t>(0700) : static_cast<mode_t>(0600);
  if (!expected_kind || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() || metadata.st_dev != device ||
      (metadata.st_mode & static_cast<mode_t>(0777)) != expected_mode ||
      (!directory && metadata.st_nlink != 1U) ||
      (directory && metadata.st_nlink < 2U)) {
    return Status{ErrorCode::protocol_error,
                  "content attempt staging entry is unsafe"};
  }
  return Status::success();
}

Result<std::size_t> cleanup_transport_attempt_temporaries(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  struct stat namespace_metadata {};
  if (::lstat(policy.root.c_str(), &namespace_metadata) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt namespace root: " +
                      std::string(std::strerror(errno))};
  }
  const std::filesystem::path objects =
      sync_content_staging_root(policy) / "objects";
  struct stat objects_metadata {};
  if (::lstat(objects.c_str(), &objects_metadata) != 0) {
    if (errno == ENOENT)
      return std::size_t{0U};
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt object staging: " +
                      std::string(std::strerror(errno))};
  }
  Status safe = private_entry_on_device(objects_metadata,
                                        namespace_metadata.st_dev, true);
  if (!safe.ok())
    return safe;

  std::size_t removed = 0U;
  std::error_code error;
  std::filesystem::directory_iterator shards(objects, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate content attempt object staging: " +
                      error.message()};
  }
  for (; shards != std::filesystem::directory_iterator{};
       shards.increment(error)) {
    if (error) {
      return Status{ErrorCode::io_error,
                    "unable to enumerate content attempt object staging: " +
                        error.message()};
    }
    const auto &shard = *shards;
    const std::string shard_name = shard.path().filename().string();
    struct stat shard_metadata {};
    if (shard_name.size() != 2U || !lowercase_hex(shard_name) ||
        ::lstat(shard.path().c_str(), &shard_metadata) != 0) {
      return Status{ErrorCode::protocol_error,
                    "content attempt staging shard is invalid"};
    }
    safe = private_entry_on_device(shard_metadata, namespace_metadata.st_dev,
                                   true);
    if (!safe.ok())
      return safe;
    bool changed = false;
    std::filesystem::directory_iterator entries(shard.path(), error);
    if (error) {
      return Status{ErrorCode::io_error,
                    "unable to enumerate content attempt staging shard: " +
                        error.message()};
    }
    for (; entries != std::filesystem::directory_iterator{};
         entries.increment(error)) {
      if (error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate content attempt staging shard: " +
                          error.message()};
      }
      const auto &entry = *entries;
      const std::string name = entry.path().filename().string();
      const bool transport = transport_attempt_filename(name);
      if (!transport && canonical_attempt_filename(name))
        continue;
      if (!transport) {
        return Status{ErrorCode::protocol_error,
                      "content attempt staging filename is invalid"};
      }
      struct stat metadata {};
      if (::lstat(entry.path().c_str(), &metadata) != 0) {
        return Status{
            ErrorCode::io_error,
            "unable to inspect content attempt transport temporary: " +
                std::string(std::strerror(errno))};
      }
      safe =
          private_entry_on_device(metadata, namespace_metadata.st_dev, false);
      if (!safe.ok() || metadata.st_size < 0 ||
          static_cast<std::uint64_t>(metadata.st_size) >
              policy.quotas.maximum_staging_bytes) {
        return Status{ErrorCode::protocol_error,
                      "content attempt transport temporary is unsafe"};
      }
      if (::unlink(entry.path().c_str()) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to remove content attempt transport temporary: " +
                          std::string(std::strerror(errno))};
      }
      ++removed;
      changed = true;
    }
    if (error) {
      return Status{ErrorCode::io_error,
                    "unable to enumerate content attempt staging shard: " +
                        error.message()};
    }
    if (changed) {
      safe = fsync_directory(shard.path());
      if (!safe.ok())
        return safe;
    }
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate content attempt object staging: " +
                      error.message()};
  }
  return removed;
}

Status prepare_attempt_directory(const std::filesystem::path &path,
                                 dev_t expected_device) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    if (errno != ENOENT) {
      return Status{ErrorCode::io_error,
                    "unable to inspect content attempt directory: " +
                        std::string(std::strerror(errno))};
    }
    if (::mkdir(path.c_str(), static_cast<mode_t>(0700)) != 0) {
      return Status{ErrorCode::io_error,
                    "unable to create content attempt directory: " +
                        std::string(std::strerror(errno))};
    }
    if (::lstat(path.c_str(), &metadata) != 0) {
      return Status{ErrorCode::io_error,
                    "unable to reinspect content attempt directory"};
    }
  }
  if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_nlink < 2 || metadata.st_uid != ::geteuid() ||
      metadata.st_dev != expected_device ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "content attempt directory is unsafe"};
  }
  return Status::success();
}

Result<std::uint64_t>
inspect_attempt_staging(const NamespacePolicy &policy,
                        const DurableSyncContentAttempt &attempt) {
  const std::filesystem::path path = sync_content_attempt_staging_path(
      policy, attempt.object, attempt.request_id);
  struct stat root {};
  if (::lstat(policy.root.c_str(), &root) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content namespace root"};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found, "content attempt staging is absent"};
    }
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt staging: " +
                      std::string(std::strerror(errno))};
  }
  if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
      metadata.st_dev != root.st_dev ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size < 0 ||
      static_cast<std::uint64_t>(metadata.st_size) > attempt.object_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content attempt staging shape is unsafe"};
  }
  return static_cast<std::uint64_t>(metadata.st_size);
}

Status discard_attempt_staging(const NamespacePolicy &policy,
                               const DurableSyncContentAttempt &attempt) {
  auto inspected = inspect_attempt_staging(policy, attempt);
  if (!inspected) {
    return inspected.status().code() == ErrorCode::not_found
               ? Status::success()
               : inspected.status();
  }
  const std::filesystem::path path = sync_content_attempt_staging_path(
      policy, attempt.object, attempt.request_id);
  if (::unlink(path.c_str()) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to remove content attempt staging: " +
                      std::string(std::strerror(errno))};
  }
  return fsync_directory(path.parent_path());
}

} // namespace

std::filesystem::path
sync_content_attempt_staging_path(const NamespacePolicy &policy,
                                  const Digest &object,
                                  std::uint64_t request_id) {
  static constexpr std::array<char, 16U> digits = {'0', '1', '2', '3', '4', '5',
                                                   '6', '7', '8', '9', 'a', 'b',
                                                   'c', 'd', 'e', 'f'};
  std::string hex;
  hex.reserve(object.size() * 2U);
  for (std::uint8_t byte : object) {
    hex.push_back(digits[byte >> 4U]);
    hex.push_back(digits[byte & 0x0fU]);
  }
  return sync_content_staging_root(policy) / "objects" / hex.substr(0U, 2U) /
         (hex.substr(2U) + "." + std::to_string(request_id) + ".part");
}

Result<std::filesystem::path> prepare_sync_content_attempt_staging(
    const NamespacePolicy &policy, const Digest &object,
    std::uint64_t request_id, const SyncNamespaceTransaction &transaction) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (policy.engine != Engine::content_v2 || request_id == 0U ||
      all_zero(object)) {
    return Status{ErrorCode::invalid_argument,
                  "content attempt staging identity is invalid"};
  }
  const Status root_prepared =
      prepare_sync_content_staging(policy, transaction);
  if (!root_prepared.ok())
    return root_prepared;
  struct stat root {};
  if (::lstat(policy.root.c_str(), &root) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content namespace root"};
  }
  const std::filesystem::path objects =
      sync_content_staging_root(policy) / "objects";
  Status prepared = prepare_attempt_directory(objects, root.st_dev);
  if (!prepared.ok())
    return prepared;
  const std::filesystem::path path =
      sync_content_attempt_staging_path(policy, object, request_id);
  prepared = prepare_attempt_directory(path.parent_path(), root.st_dev);
  if (!prepared.ok())
    return prepared;
  struct stat existing {};
  if (::lstat(path.c_str(), &existing) == 0) {
    return Status{ErrorCode::protocol_error,
                  "content attempt staging already exists"};
  }
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content attempt staging destination"};
  }
  return path;
}

Status discard_sync_content_attempt_staging(
    const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status valid = validate_attempt(attempt);
  if (!valid.ok())
    return valid;
  return discard_attempt_staging(policy, attempt);
}

Result<std::vector<std::uint8_t>>
encode_sync_content_attempt_journal(const SyncContentAttemptJournal &journal) {
  auto body = encode_body(journal);
  if (!body)
    return body.status();
  std::vector<std::uint8_t> output = std::move(body).value();
  output.insert(output.end(), journal.signature.begin(),
                journal.signature.end());
  return output;
}

Result<SyncContentAttemptJournal>
decode_sync_content_attempt_journal(std::span<const std::uint8_t> bytes,
                                    std::size_t maximum_active_attempts) {
  if (maximum_active_attempts == 0U || maximum_active_attempts > 65536U ||
      bytes.size() < kHeaderBytes + security::kSignatureBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] == 0U || bytes[8U] > kNamespaceBytes ||
      !all_zero(bytes.subspan(9U, 7U)) || !all_zero(bytes.subspan(168U, 24U))) {
    return Status{ErrorCode::protocol_error,
                  "content attempt journal header is invalid"};
  }
  const std::uint64_t count = read_u64(bytes, 32U);
  if (count > maximum_active_attempts ||
      count > (std::numeric_limits<std::size_t>::max() - kHeaderBytes -
               security::kSignatureBytes) /
                  kAttemptBytes ||
      bytes.size() != kHeaderBytes +
                          static_cast<std::size_t>(count) * kAttemptBytes +
                          security::kSignatureBytes) {
    return Status{ErrorCode::protocol_error,
                  "content attempt journal count or size is invalid"};
  }
  const std::size_t namespace_size = bytes[8U];
  if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_size,
                              kNamespaceBytes - namespace_size))) {
    return Status{ErrorCode::protocol_error,
                  "content attempt namespace padding is nonzero"};
  }
  SyncContentAttemptJournal journal;
  journal.namespace_id.assign(
      reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
      namespace_size);
  journal.mutation = read_u64(bytes, 16U);
  journal.high_attempt_id = read_u64(bytes, 24U);
  read_array(bytes, kSignerOffset, journal.signer);
  read_array(bytes, kPreviousOffset, journal.previous);
  journal.active.reserve(static_cast<std::size_t>(count));
  std::size_t offset = kHeaderBytes;
  for (std::uint64_t index = 0U; index < count; ++index) {
    if (!all_zero(bytes.subspan(offset + 10U, 6U)) ||
        !all_zero(bytes.subspan(offset + 84U, 12U))) {
      return Status{ErrorCode::protocol_error,
                    "content attempt record padding is nonzero"};
    }
    DurableSyncContentAttempt attempt;
    attempt.attempt_id = read_u64(bytes, offset);
    attempt.kind = static_cast<SyncContentObjectKind>(bytes[offset + 8U]);
    attempt.carrier.carrier_class =
        static_cast<SyncCarrierClass>(bytes[offset + 9U]);
    attempt.request_id = read_u64(bytes, offset + 16U);
    attempt.source_id = read_u64(bytes, offset + 24U);
    attempt.logical_index = read_u64(bytes, offset + 32U);
    attempt.object_bytes = read_u64(bytes, offset + 40U);
    attempt.carrier.worker_id = read_u64(bytes, offset + 48U);
    attempt.carrier.online_epoch = read_u64(bytes, offset + 56U);
    attempt.carrier.remote_route_generation = read_u64(bytes, offset + 64U);
    attempt.carrier.primary_authority_online_epoch =
        read_u64(bytes, offset + 72U);
    attempt.carrier.friend_number = read_u32(bytes, offset + 80U);
    read_array(bytes, offset + 96U, attempt.head_record);
    read_array(bytes, offset + 128U, attempt.object);
    read_array(bytes, offset + 160U, attempt.file_id);
    read_array(bytes, offset + 192U, attempt.carrier.route_key);
    read_array(bytes, offset + 224U,
               attempt.carrier.remote_coordinator_route_key);
    read_array(bytes, offset + 256U, attempt.source_principal);
    journal.active.push_back(attempt);
    offset += kAttemptBytes;
  }
  read_array(bytes, offset, journal.signature);
  const Status valid = validate_journal_shape(journal, maximum_active_attempts);
  if (!valid.ok()) {
    return Status{ErrorCode::protocol_error, valid.message()};
  }
  auto canonical = encode_sync_content_attempt_journal(journal);
  if (!canonical || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "content attempt journal is not canonical"};
  }
  return journal;
}

Status verify_sync_content_attempt_journal(
    const SyncContentAttemptJournal &journal,
    const security::SigningPublicKey &expected_device,
    const NamespacePolicy &policy, const security::Sodium &sodium,
    std::size_t maximum_active_attempts) {
  const Status valid =
      validate_journal_policy(journal, policy, maximum_active_attempts);
  if (!valid.ok())
    return valid;
  if (all_zero(expected_device) || journal.signer != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "content attempt signer is not the expected device"};
  }
  auto body = encode_body(journal);
  if (!body)
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest)
    return digest.status();
  return sodium.verify_detached(journal.signature, digest.value(),
                                journal.signer);
}

Result<Digest>
sync_content_attempt_journal_digest(const SyncContentAttemptJournal &journal,
                                    const security::Sodium &sodium) {
  auto encoded = encode_sync_content_attempt_journal(journal);
  if (!encoded)
    return encoded.status();
  return sodium.hash(kRecordDomain, encoded.value());
}

SyncContentAttemptStore::SyncContentAttemptStore(std::filesystem::path root)
    : SyncContentAttemptStore(std::move(root), Config{}) {}

SyncContentAttemptStore::SyncContentAttemptStore(std::filesystem::path root,
                                                 Config config)
    : root_(std::move(root)), config_(config) {}

std::filesystem::path
SyncContentAttemptStore::path_for(std::string_view namespace_id) const {
  return root_ / "content-attempts" /
         (std::string(namespace_id) + ".active-content-attempts");
}

Result<SyncContentAttemptJournal>
SyncContentAttemptStore::load(const NamespacePolicy &policy,
                              const security::SigningPublicKey &expected_device,
                              const security::Sodium &sodium) const {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok())
    return configured;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "content attempt expected device is zero"};
  }
  auto bytes =
      read_private_file(path_for(policy.id), config_.maximum_active_attempts);
  if (!bytes) {
    if (bytes.status().code() == ErrorCode::not_found) {
      SyncContentAttemptJournal empty;
      empty.namespace_id = policy.id;
      empty.signer = expected_device;
      return empty;
    }
    return bytes.status();
  }
  Status parent = validate_private_directory(root_);
  if (!parent.ok())
    return parent;
  parent = validate_private_directory(root_ / "content-attempts");
  if (!parent.ok())
    return parent;
  auto journal = decode_sync_content_attempt_journal(
      bytes.value(), config_.maximum_active_attempts);
  if (!journal)
    return journal.status();
  const Status verified = verify_sync_content_attempt_journal(
      journal.value(), expected_device, policy, sodium,
      config_.maximum_active_attempts);
  if (!verified.ok())
    return verified;
  return journal;
}

Result<std::uint64_t> SyncContentAttemptStore::reserve_attempt_id(
    const NamespacePolicy &policy, const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok())
    return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal)
    return journal.status();
  if (journal.value().high_attempt_id ==
      std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "content attempt identifier space is exhausted"};
  }
  ++journal.value().high_attempt_id;
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_sync_content_attempt_journal(journal.value());
  if (!encoded)
    return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok())
    return stored;
  return journal.value().high_attempt_id;
}

Result<SyncContentAttemptBegin> SyncContentAttemptStore::begin(
    const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok())
    return configured;
  const Status valid = validate_attempt(attempt);
  if (!valid.ok())
    return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal)
    return journal.status();
  if (attempt.attempt_id > journal.value().high_attempt_id) {
    return Status{ErrorCode::protocol_error,
                  "content attempt identifier was not durably reserved"};
  }
  const auto same_id =
      std::lower_bound(journal.value().active.begin(),
                       journal.value().active.end(), attempt.attempt_id,
                       [](const DurableSyncContentAttempt &value,
                          std::uint64_t id) { return value.attempt_id < id; });
  if (same_id != journal.value().active.end() &&
      same_id->attempt_id == attempt.attempt_id) {
    return *same_id == attempt ? Result<SyncContentAttemptBegin>(
                                     SyncContentAttemptBegin::duplicate)
                               : Result<SyncContentAttemptBegin>(
                                     Status{ErrorCode::protocol_error,
                                            "content attempt identifier "
                                            "conflicts with durable state"});
  }
  SyncContentAttemptJournal candidate = journal.value();
  candidate.active.insert(
      candidate.active.begin() +
          static_cast<std::ptrdiff_t>(same_id - journal.value().active.begin()),
      attempt);
  const Status candidate_valid = validate_journal_policy(
      candidate, policy, config_.maximum_active_attempts);
  if (!candidate_valid.ok()) {
    return candidate.active.size() > config_.maximum_active_attempts ||
                   candidate.active.size() >
                       policy.quotas.maximum_outstanding_requests
               ? Status{ErrorCode::resource_exhausted,
                        "content active-attempt bound is exhausted"}
               : candidate_valid;
  }
  journal.value().active = std::move(candidate.active);
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_sync_content_attempt_journal(journal.value());
  if (!encoded)
    return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok())
    return stored;
  return SyncContentAttemptBegin::inserted;
}

Result<bool> SyncContentAttemptStore::finish(
    const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok())
    return configured;
  const Status valid = validate_attempt(attempt);
  if (!valid.ok())
    return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal)
    return journal.status();
  if (attempt.attempt_id > journal.value().high_attempt_id) {
    return Status{ErrorCode::protocol_error,
                  "content attempt finish names an unreserved identifier"};
  }
  const auto found =
      std::lower_bound(journal.value().active.begin(),
                       journal.value().active.end(), attempt.attempt_id,
                       [](const DurableSyncContentAttempt &value,
                          std::uint64_t id) { return value.attempt_id < id; });
  if (found == journal.value().active.end() ||
      found->attempt_id != attempt.attempt_id) {
    return false;
  }
  if (*found != attempt) {
    return Status{ErrorCode::protocol_error,
                  "content attempt finish conflicts with durable state"};
  }
  journal.value().active.erase(found);
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_sync_content_attempt_journal(journal.value());
  if (!encoded)
    return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok())
    return stored;
  return true;
}

Result<std::vector<RecoveredSyncContentAttempt>>
SyncContentAttemptStore::recover(const NamespacePolicy &policy,
                                 const security::DeviceIdentity &identity,
                                 const security::Sodium &sodium,
                                 const SyncNamespaceTransaction &transaction,
                                 SyncContentCommitConfig commit_config) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok())
    return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal)
    return journal.status();
  // Preserve all crash residue if signed restart truth is not authentic. Once
  // it is verified, transport-owned mkstemp files are never canonical attempt
  // prefixes and cannot be revived by a later carrier.
  auto cleaned = cleanup_transport_attempt_temporaries(policy, transaction);
  if (!cleaned)
    return cleaned.status();
  if (journal.value().active.empty()) {
    return std::vector<RecoveredSyncContentAttempt>{};
  }
  auto inventory = inspect_sync_content_store(policy, transaction, true);
  if (!inventory)
    return inventory.status();
  std::vector<RecoveredSyncContentAttempt> recovered;
  recovered.reserve(journal.value().active.size());
  for (const DurableSyncContentAttempt &attempt : journal.value().active) {
    const auto present = std::lower_bound(
        inventory.value().records.begin(), inventory.value().records.end(),
        attempt.object,
        [](const SyncContentStoredObject &record, const Digest &object) {
          return record.object < object;
        });
    if (present != inventory.value().records.end() &&
        present->object == attempt.object) {
      if (present->object_bytes != attempt.object_bytes) {
        return Status{ErrorCode::protocol_error,
                      "durable content object size conflicts with CAS"};
      }
      const Status discarded = discard_attempt_staging(policy, attempt);
      if (!discarded.ok())
        return discarded;
      recovered.push_back(RecoveredSyncContentAttempt{
          attempt, SyncContentAttemptRecoveryDisposition::committed});
      continue;
    }
    auto staged = inspect_attempt_staging(policy, attempt);
    if (!staged) {
      if (staged.status().code() != ErrorCode::not_found) {
        return staged.status();
      }
      recovered.push_back(RecoveredSyncContentAttempt{
          attempt, SyncContentAttemptRecoveryDisposition::fenced});
      continue;
    }
    if (staged.value() == attempt.object_bytes) {
      auto committed = commit_sync_content_staging(
          policy, attempt.object, attempt.object_bytes,
          sync_content_attempt_staging_path(policy, attempt.object,
                                            attempt.request_id),
          transaction, commit_config);
      if (!committed)
        return committed.status();
      recovered.push_back(RecoveredSyncContentAttempt{
          attempt, SyncContentAttemptRecoveryDisposition::committed});
      continue;
    }
    const Status discarded = discard_attempt_staging(policy, attempt);
    if (!discarded.ok())
      return discarded;
    recovered.push_back(RecoveredSyncContentAttempt{
        attempt, SyncContentAttemptRecoveryDisposition::fenced});
  }
  journal.value().active.clear();
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_sync_content_attempt_journal(journal.value());
  if (!encoded)
    return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok())
    return stored;
  return recovered;
}

} // namespace iotox::sync
