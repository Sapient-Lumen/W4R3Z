#include "iotox/sync_attempt_store.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_reconstruction.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {'I', 'O', 'T', 'X',
                                                 'A', 'T', 'M', '1'};
constexpr std::string_view kSignatureDomain =
    "iotox-sync-attempt-journal-signature-v1";
constexpr std::string_view kRecordDomain =
    "iotox-sync-attempt-journal-record-v1";
constexpr std::size_t kHeaderBytes = 192U;
constexpr std::size_t kAttemptBytes = 96U;
constexpr std::size_t kSignerOffset = 40U;
constexpr std::size_t kPreviousOffset = 72U;
constexpr std::size_t kNamespaceOffset = 104U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kSignatureBytes = security::kSignatureBytes;

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

Status validate_attempt(const DurableSyncAttempt &attempt) {
  if (attempt.attempt_id == 0U || attempt.worker_id == 0U ||
      all_zero(attempt.object.identity) || all_zero(attempt.route_key) ||
      attempt.object.bytes == 0U ||
      (attempt.state != DurableSyncAttemptState::active &&
       attempt.state != DurableSyncAttemptState::restart_retained) ||
      (attempt.mode != DurableSyncAttemptMode::whole_object &&
       attempt.mode != DurableSyncAttemptMode::range_bundle) ||
      (attempt.binding != DurableSyncAttemptBinding::route_worker &&
       attempt.binding != DurableSyncAttemptBinding::range_plan_v1) ||
      (attempt.mode == DurableSyncAttemptMode::whole_object &&
       attempt.binding != DurableSyncAttemptBinding::route_worker) ||
      (attempt.state == DurableSyncAttemptState::restart_retained &&
       attempt.mode == DurableSyncAttemptMode::range_bundle &&
       attempt.binding != DurableSyncAttemptBinding::range_plan_v1) ||
      (attempt.mode == DurableSyncAttemptMode::range_bundle &&
       attempt.binding == DurableSyncAttemptBinding::range_plan_v1 &&
       (attempt.object.kind != SyncObjectKind::artifact ||
        attempt.worker_id >= attempt.object.bytes)) ||
      (attempt.object.kind != SyncObjectKind::artifact &&
       attempt.object.kind != SyncObjectKind::manifest)) {
    return Status{ErrorCode::invalid_argument,
                  "durable sync attempt identity is invalid"};
  }
  return Status::success();
}

Status validate_journal_shape(const SyncAttemptJournal &journal,
                              std::size_t maximum_active_attempts) {
  if (!valid_namespace_id(journal.namespace_id) ||
      maximum_active_attempts == 0U ||
      maximum_active_attempts > 65536U ||
      journal.active.size() > maximum_active_attempts ||
      journal.high_attempt_id == 0U || journal.mutation == 0U ||
      all_zero(journal.signer) ||
      (journal.mutation == 1U && !all_zero(journal.previous)) ||
      (journal.mutation != 1U && all_zero(journal.previous))) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt journal header is invalid"};
  }
  std::uint64_t prior_id = 0U;
  std::vector<std::pair<SyncObjectKind, Digest>> objects;
  objects.reserve(journal.active.size());
  for (const DurableSyncAttempt &attempt : journal.active) {
    const Status valid = validate_attempt(attempt);
    if (!valid.ok() || attempt.attempt_id <= prior_id ||
        attempt.attempt_id > journal.high_attempt_id) {
      return Status{ErrorCode::invalid_argument,
                    "sync attempt journal entries are invalid or unsorted"};
    }
    prior_id = attempt.attempt_id;
    objects.emplace_back(attempt.object.kind, attempt.object.identity);
  }
  std::sort(objects.begin(), objects.end());
  if (std::adjacent_find(objects.begin(), objects.end()) != objects.end()) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt journal assigns one object more than once"};
  }
  return Status::success();
}

Status validate_journal_policy(const SyncAttemptJournal &journal,
                               const NamespacePolicy &policy,
                               std::size_t maximum_active_attempts) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok()) return valid_policy;
  const Status valid = validate_journal_shape(journal, maximum_active_attempts);
  if (!valid.ok()) return valid;
  if (journal.namespace_id != policy.id ||
      journal.active.size() > policy.quotas.maximum_outstanding_requests) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal conflicts with namespace policy"};
  }
  for (const DurableSyncAttempt &attempt : journal.active) {
    const std::uint64_t kind_limit =
        attempt.object.kind == SyncObjectKind::artifact
            ? policy.quotas.maximum_artifact_bytes
            : policy.quotas.maximum_manifest_bytes;
    if (attempt.object.bytes > kind_limit ||
        attempt.object.bytes > policy.quotas.maximum_staging_bytes ||
        attempt.object.bytes > policy.quotas.maximum_store_bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync attempt journal object exceeds namespace policy"};
    }
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_journal_body(const SyncAttemptJournal &journal) {
  const Status valid = validate_journal_shape(journal, 65536U);
  if (!valid.ok()) return valid;
  if (journal.active.size() >
      (std::numeric_limits<std::size_t>::max() - kHeaderBytes) /
          kAttemptBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync attempt journal encoding is too large"};
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
  for (const DurableSyncAttempt &attempt : journal.active) {
    write_u64(output, offset, attempt.attempt_id);
    output[offset + 8U] = static_cast<std::uint8_t>(attempt.object.kind);
    output[offset + 9U] = static_cast<std::uint8_t>(attempt.state);
    output[offset + 10U] = static_cast<std::uint8_t>(attempt.mode);
    output[offset + 11U] = static_cast<std::uint8_t>(attempt.binding);
    write_array(output, offset + 16U, attempt.object.identity);
    write_u64(output, offset + 48U, attempt.object.bytes);
    write_array(output, offset + 56U, attempt.route_key);
    write_u64(output, offset + 88U, attempt.worker_id);
    offset += kAttemptBytes;
  }
  return output;
}

Status ensure_private_directory(const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync attempt directory: " +
                      error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt directory is not real and owner-owned"};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure sync attempt directory: " +
                      error.message()};
  }
  return Status::success();
}

Status validate_private_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt directory is not private and owner-owned"};
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path, std::size_t maximum_active_attempts) {
  const int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found, "sync attempt journal is absent"};
    }
    return Status{ErrorCode::io_error,
                  "unable to open sync attempt journal: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0) {
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to inspect sync attempt journal: " +
                      std::string(std::strerror(saved))};
  }
  const std::uint64_t maximum_bytes =
      kHeaderBytes +
      static_cast<std::uint64_t>(maximum_active_attempts) * kAttemptBytes +
      kSignatureBytes;
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size <
          static_cast<off_t>(kHeaderBytes + kSignatureBytes) ||
      static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal is not one bounded private file"};
  }
  std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::read(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete sync attempt journal"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close sync attempt journal"};
  }
  return bytes;
}

Status validate_store(const std::filesystem::path &root,
                      const SyncAttemptStore::Config &config,
                      const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (config.maximum_active_attempts == 0U ||
      config.maximum_active_attempts > 65536U ||
      root.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt store configuration is invalid"};
  }
  return Status::success();
}

Status prepare_parent(const std::filesystem::path &root) {
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok()) return prepared;
  return ensure_private_directory(root / "attempts");
}

Status advance_and_sign(SyncAttemptJournal &journal,
                        const security::DeviceIdentity &identity,
                        const security::Sodium &sodium) {
  if (journal.mutation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync attempt journal mutation counter is exhausted"};
  }
  if (journal.mutation == 0U) {
    journal.mutation = 1U;
    journal.previous = Digest{};
  } else {
    auto previous = sync_attempt_journal_digest(journal, sodium);
    if (!previous) return previous.status();
    journal.previous = previous.value();
    ++journal.mutation;
  }
  journal.signer = identity.public_key();
  auto body = encode_journal_body(journal);
  if (!body) return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest) return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature) return signature.status();
  journal.signature = signature.value();
  return Status::success();
}

} // namespace

Result<DurableSyncAttempt> make_durable_range_attempt(
    std::uint64_t attempt_id, const SyncRangePlan &plan,
    DurableSyncAttemptState state, const security::Sodium &sodium) {
  auto commitment = sync_range_plan_commitment(plan, sodium);
  if (!commitment) return commitment.status();
  DurableSyncAttempt attempt{
      attempt_id, plan.target, commitment.value(), plan.missing_bytes,
      state, DurableSyncAttemptMode::range_bundle,
      DurableSyncAttemptBinding::range_plan_v1};
  const Status valid = validate_attempt(attempt);
  if (!valid.ok()) return valid;
  return attempt;
}

Result<std::vector<std::uint8_t>>
encode_sync_attempt_journal(const SyncAttemptJournal &journal) {
  auto body = encode_journal_body(journal);
  if (!body) return body.status();
  std::vector<std::uint8_t> output = std::move(body).value();
  output.insert(output.end(), journal.signature.begin(),
                journal.signature.end());
  return output;
}

Result<SyncAttemptJournal>
decode_sync_attempt_journal(std::span<const std::uint8_t> bytes,
                            std::size_t maximum_active_attempts) {
  if (maximum_active_attempts == 0U || maximum_active_attempts > 65536U ||
      bytes.size() < kHeaderBytes + kSignatureBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] == 0U || bytes[8U] > kNamespaceBytes ||
      !all_zero(bytes.subspan(9U, 7U)) ||
      !all_zero(bytes.subspan(168U, 24U))) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal header is invalid"};
  }
  const std::uint64_t count = read_u64(bytes, 32U);
  if (count > maximum_active_attempts ||
      count > (std::numeric_limits<std::size_t>::max() - kHeaderBytes -
               kSignatureBytes) /
                  kAttemptBytes ||
      bytes.size() !=
          kHeaderBytes + static_cast<std::size_t>(count) * kAttemptBytes +
              kSignatureBytes) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal count or size is invalid"};
  }
  const std::size_t namespace_size = bytes[8U];
  if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_size,
                              kNamespaceBytes - namespace_size))) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt namespace padding is nonzero"};
  }
  SyncAttemptJournal journal;
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
    if (!all_zero(bytes.subspan(offset + 12U, 4U))) {
      return Status{ErrorCode::protocol_error,
                    "sync attempt record padding is nonzero"};
    }
    DurableSyncAttempt attempt;
    attempt.attempt_id = read_u64(bytes, offset);
    attempt.object.kind = static_cast<SyncObjectKind>(bytes[offset + 8U]);
    attempt.state = static_cast<DurableSyncAttemptState>(bytes[offset + 9U]);
    attempt.mode = static_cast<DurableSyncAttemptMode>(bytes[offset + 10U]);
    attempt.binding =
        static_cast<DurableSyncAttemptBinding>(bytes[offset + 11U]);
    read_array(bytes, offset + 16U, attempt.object.identity);
    attempt.object.bytes = read_u64(bytes, offset + 48U);
    read_array(bytes, offset + 56U, attempt.route_key);
    attempt.worker_id = read_u64(bytes, offset + 88U);
    journal.active.push_back(attempt);
    offset += kAttemptBytes;
  }
  read_array(bytes, offset, journal.signature);
  const Status valid =
      validate_journal_shape(journal, maximum_active_attempts);
  if (!valid.ok()) {
    return Status{ErrorCode::protocol_error, valid.message()};
  }
  auto canonical = encode_sync_attempt_journal(journal);
  if (!canonical || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal is not canonical"};
  }
  return journal;
}

Status verify_sync_attempt_journal(
    const SyncAttemptJournal &journal,
    const security::SigningPublicKey &expected_device,
    const NamespacePolicy &policy, const security::Sodium &sodium,
    std::size_t maximum_active_attempts) {
  const Status valid =
      validate_journal_policy(journal, policy, maximum_active_attempts);
  if (!valid.ok()) return valid;
  if (all_zero(expected_device) || journal.signer != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt journal signer is not the expected device"};
  }
  auto body = encode_journal_body(journal);
  if (!body) return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest) return digest.status();
  return sodium.verify_detached(journal.signature, digest.value(),
                                journal.signer);
}

Result<Digest> sync_attempt_journal_digest(
    const SyncAttemptJournal &journal, const security::Sodium &sodium) {
  auto encoded = encode_sync_attempt_journal(journal);
  if (!encoded) return encoded.status();
  return sodium.hash(kRecordDomain, encoded.value());
}

SyncAttemptStore::SyncAttemptStore(std::filesystem::path root)
    : SyncAttemptStore(std::move(root), Config{}) {}

SyncAttemptStore::SyncAttemptStore(std::filesystem::path root, Config config)
    : root_(std::move(root)), config_(config) {}

std::filesystem::path
SyncAttemptStore::path_for(std::string_view namespace_id) const {
  return root_ / "attempts" /
         (std::string(namespace_id) + ".active-attempts");
}

Result<SyncAttemptJournal> SyncAttemptStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt expected device is zero"};
  }
  auto bytes = read_private_file(path_for(policy.id),
                                 config_.maximum_active_attempts);
  if (!bytes) {
    if (bytes.status().code() == ErrorCode::not_found) {
      SyncAttemptJournal empty;
      empty.namespace_id = policy.id;
      empty.signer = expected_device;
      return empty;
    }
    return bytes.status();
  }
  Status parent = validate_private_directory(root_);
  if (!parent.ok()) return parent;
  parent = validate_private_directory(root_ / "attempts");
  if (!parent.ok()) return parent;
  auto journal = decode_sync_attempt_journal(
      bytes.value(), config_.maximum_active_attempts);
  if (!journal) return journal.status();
  const Status verified = verify_sync_attempt_journal(
      journal.value(), expected_device, policy, sodium,
      config_.maximum_active_attempts);
  if (!verified.ok()) return verified;
  return journal;
}

Result<std::uint64_t> SyncAttemptStore::reserve_attempt_id(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction) return transaction.status();
  return reserve_attempt_id(policy, identity, sodium, transaction.value());
}

Result<std::uint64_t> SyncAttemptStore::reserve_attempt_id(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok()) return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  if (journal.value().high_attempt_id ==
      std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync attempt identifier space is exhausted"};
  }
  ++journal.value().high_attempt_id;
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return journal.value().high_attempt_id;
}

Result<SyncAttemptBegin> SyncAttemptStore::begin(
    const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction) return transaction.status();
  return begin(policy, attempt, identity, sodium, transaction.value());
}

Result<SyncAttemptBegin> SyncAttemptStore::begin(
    const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status valid_attempt = validate_attempt(attempt);
  if (!valid_attempt.ok()) return valid_attempt;
  if (attempt.state != DurableSyncAttemptState::active) {
    return Status{ErrorCode::invalid_argument,
                  "a new sync attempt must begin in active state"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok()) return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  if (attempt.attempt_id > journal.value().high_attempt_id) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt identifier was not durably reserved"};
  }
  const auto same_id = std::lower_bound(
      journal.value().active.begin(), journal.value().active.end(),
      attempt.attempt_id,
      [](const DurableSyncAttempt &value, std::uint64_t id) {
        return value.attempt_id < id;
      });
  if (same_id != journal.value().active.end() &&
      same_id->attempt_id == attempt.attempt_id) {
    return *same_id == attempt
               ? Result<SyncAttemptBegin>(SyncAttemptBegin::duplicate)
               : Result<SyncAttemptBegin>(Status{
                     ErrorCode::protocol_error,
                     "sync attempt identifier has conflicting durable state"});
  }
  const auto same_object = std::find_if(
      journal.value().active.begin(), journal.value().active.end(),
      [&attempt](const DurableSyncAttempt &value) {
        return value.object.kind == attempt.object.kind &&
               value.object.identity == attempt.object.identity;
      });
  if (same_object != journal.value().active.end()) {
    return Status{ErrorCode::protocol_error,
                  "sync object already has a durable active attempt"};
  }
  const std::uint64_t policy_bound =
      policy.quotas.maximum_outstanding_requests;
  if (journal.value().active.size() >= config_.maximum_active_attempts ||
      journal.value().active.size() >= policy_bound) {
    return Status{ErrorCode::resource_exhausted,
                  "sync durable active-attempt bound is exhausted"};
  }
  journal.value().active.insert(same_id, attempt);
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return SyncAttemptBegin::inserted;
}

Result<bool> SyncAttemptStore::finish(
    const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction) return transaction.status();
  return finish(policy, attempt, identity, sodium, transaction.value());
}

Result<bool> SyncAttemptStore::finish(
    const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status valid_attempt = validate_attempt(attempt);
  if (!valid_attempt.ok()) return valid_attempt;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok()) return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  if (attempt.attempt_id > journal.value().high_attempt_id) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt finish names an unreserved identifier"};
  }
  const auto found = std::lower_bound(
      journal.value().active.begin(), journal.value().active.end(),
      attempt.attempt_id,
      [](const DurableSyncAttempt &value, std::uint64_t id) {
        return value.attempt_id < id;
      });
  if (found == journal.value().active.end() ||
      found->attempt_id != attempt.attempt_id) {
    return false;
  }
  if (*found != attempt) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt finish conflicts with durable state"};
  }
  journal.value().active.erase(found);
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return true;
}

Result<std::optional<DurableSyncAttempt>>
SyncAttemptStore::retained_attempt(
    const NamespacePolicy &policy, const SyncObjectRecord &object,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (object.bytes == 0U || all_zero(object.identity) ||
      (object.kind != SyncObjectKind::artifact &&
       object.kind != SyncObjectKind::manifest)) {
    return Status{ErrorCode::invalid_argument,
                  "restart-retained sync object identity is invalid"};
  }
  auto journal = load(policy, expected_device, sodium);
  if (!journal) return journal.status();
  const auto found = std::find_if(
      journal.value().active.begin(), journal.value().active.end(),
      [&object](const DurableSyncAttempt &attempt) {
        return attempt.state == DurableSyncAttemptState::restart_retained &&
               attempt.mode == DurableSyncAttemptMode::whole_object &&
               attempt.object == object;
      });
  if (found == journal.value().active.end()) {
    return std::optional<DurableSyncAttempt>{};
  }
  return std::optional<DurableSyncAttempt>{*found};
}

Result<std::optional<DurableSyncAttempt>>
SyncAttemptStore::retained_range_attempt(
    const NamespacePolicy &policy, const SyncObjectRecord &target,
    const Digest &plan_commitment, std::uint64_t bundle_bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (target.kind != SyncObjectKind::artifact || target.bytes == 0U ||
      all_zero(target.identity) || all_zero(plan_commitment) ||
      bundle_bytes == 0U || bundle_bytes >= target.bytes) {
    return Status{ErrorCode::invalid_argument,
                  "restart-retained range identity is invalid"};
  }
  auto journal = load(policy, expected_device, sodium);
  if (!journal) return journal.status();
  const auto found = std::find_if(
      journal.value().active.begin(), journal.value().active.end(),
      [&](const DurableSyncAttempt &attempt) {
        return attempt.state == DurableSyncAttemptState::restart_retained &&
               attempt.mode == DurableSyncAttemptMode::range_bundle &&
               attempt.binding == DurableSyncAttemptBinding::range_plan_v1 &&
               attempt.object == target &&
               attempt.route_key == plan_commitment &&
               attempt.worker_id == bundle_bytes;
      });
  if (found == journal.value().active.end()) {
    return std::optional<DurableSyncAttempt>{};
  }
  return std::optional<DurableSyncAttempt>{*found};
}

Result<std::size_t> SyncAttemptStore::fence_retained_ranges_except(
    const NamespacePolicy &policy, const SyncObjectRecord &target,
    const Digest &plan_commitment, std::uint64_t bundle_bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  const bool allow_none = all_zero(plan_commitment) && bundle_bytes == 0U;
  const bool allow_exact = !all_zero(plan_commitment) &&
                           bundle_bytes != 0U &&
                           bundle_bytes < target.bytes;
  if (target.kind != SyncObjectKind::artifact || target.bytes == 0U ||
      all_zero(target.identity) || (!allow_none && !allow_exact)) {
    return Status{ErrorCode::invalid_argument,
                  "retained range allowlist is invalid"};
  }
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  std::vector<DurableSyncAttempt> keep;
  keep.reserve(journal.value().active.size());
  std::size_t fenced = 0U;
  for (const DurableSyncAttempt &attempt : journal.value().active) {
    const bool candidate =
        attempt.state == DurableSyncAttemptState::restart_retained &&
        attempt.mode == DurableSyncAttemptMode::range_bundle &&
        attempt.binding == DurableSyncAttemptBinding::range_plan_v1 &&
        attempt.object == target;
    const bool allowed = allow_exact && candidate &&
                         attempt.route_key == plan_commitment &&
                         attempt.worker_id == bundle_bytes;
    if (!candidate || allowed) {
      keep.push_back(attempt);
      continue;
    }
    const Status discarded = discard_sync_attempt_staging(
        policy, attempt.attempt_id, transaction);
    if (!discarded.ok()) return discarded;
    ++fenced;
  }
  if (fenced == 0U) return fenced;
  journal.value().active = std::move(keep);
  const Status signed_state = advance_and_sign(
      journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return fenced;
}

Result<std::size_t> SyncAttemptStore::fence_retained_except(
    const NamespacePolicy &policy,
    std::span<const SyncObjectRecord> allowed_objects,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (allowed_objects.size() > 2U) {
    return Status{ErrorCode::invalid_argument,
                  "restart-retained allowlist exceeds one signed HEAD"};
  }
  for (const SyncObjectRecord &object : allowed_objects) {
    if (object.bytes == 0U || all_zero(object.identity) ||
        (object.kind != SyncObjectKind::artifact &&
         object.kind != SyncObjectKind::manifest)) {
      return Status{ErrorCode::invalid_argument,
                    "restart-retained allowlist object is invalid"};
    }
  }
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  std::size_t fenced = 0U;
  std::vector<DurableSyncAttempt> keep;
  keep.reserve(journal.value().active.size());
  for (const DurableSyncAttempt &attempt : journal.value().active) {
    const bool allowed = std::find(
        allowed_objects.begin(), allowed_objects.end(), attempt.object) !=
        allowed_objects.end();
    if (attempt.state != DurableSyncAttemptState::restart_retained ||
        allowed) {
      keep.push_back(attempt);
      continue;
    }
    const Status discarded = discard_sync_attempt_staging(
        policy, attempt.attempt_id, transaction);
    if (!discarded.ok()) return discarded;
    ++fenced;
  }
  if (fenced == 0U) return fenced;
  journal.value().active = std::move(keep);
  const Status signed_state = advance_and_sign(
      journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return fenced;
}

Result<std::vector<RecoveredSyncAttempt>> SyncAttemptStore::recover(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, const SyncInstallSeams &seams,
    std::uint64_t copy_chunk_bytes) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction) return transaction.status();
  return recover(policy, identity, sodium, seams, transaction.value(),
                 copy_chunk_bytes);
}

Result<std::vector<RecoveredSyncAttempt>> SyncAttemptStore::recover(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, const SyncInstallSeams &seams,
    const SyncNamespaceTransaction &transaction,
    std::uint64_t copy_chunk_bytes) {
  const Status configured = validate_store(root_, config_, policy);
  if (!configured.ok()) return configured;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (!seams.hash_file || copy_chunk_bytes == 0U ||
      copy_chunk_bytes > 1024U * 1024U) {
    return Status{ErrorCode::invalid_argument,
                  "sync attempt recovery configuration is invalid"};
  }
  const Status prepared = prepare_parent(root_);
  if (!prepared.ok()) return prepared;
  auto journal = load(policy, identity.public_key(), sodium);
  if (!journal) return journal.status();
  std::vector<std::uint64_t> active_attempt_ids;
  active_attempt_ids.reserve(journal.value().active.size());
  for (const DurableSyncAttempt &attempt : journal.value().active) {
    active_attempt_ids.push_back(attempt.attempt_id);
  }
  const Status inactive_cleanup = cleanup_inactive_sync_attempt_partials(
      policy, journal.value().high_attempt_id, active_attempt_ids,
      transaction);
  if (!inactive_cleanup.ok()) return inactive_cleanup;
  std::vector<RecoveredSyncAttempt> recovered;
  std::vector<DurableSyncAttempt> retained;
  recovered.reserve(journal.value().active.size());
  retained.reserve(journal.value().active.size());
  for (const DurableSyncAttempt &attempt : journal.value().active) {
    const Status existing = verify_sync_object(
        policy, attempt.object, transaction, seams);
    if (existing.ok()) {
      const Status discarded = discard_sync_attempt_staging(
          policy, attempt.attempt_id, transaction);
      if (!discarded.ok()) return discarded;
      recovered.push_back(RecoveredSyncAttempt{
          attempt, SyncAttemptRecoveryDisposition::committed});
      continue;
    }
    if (existing.code() != ErrorCode::not_found) return existing;
    auto committed = commit_sync_attempt_staging(
        policy, attempt.attempt_id, attempt.object, transaction, seams,
        copy_chunk_bytes);
    if (committed) {
      recovered.push_back(RecoveredSyncAttempt{
          attempt, SyncAttemptRecoveryDisposition::committed});
      continue;
    }
    if (committed.status().code() != ErrorCode::not_found &&
        committed.status().code() != ErrorCode::protocol_error) {
      return committed.status();
    }
    auto partial = inspect_sync_attempt_partial(
        policy, attempt.attempt_id, attempt.object, transaction);
    const bool retain_whole =
        attempt.mode == DurableSyncAttemptMode::whole_object;
    const bool retain_range =
        attempt.mode == DurableSyncAttemptMode::range_bundle && partial &&
        attempt.binding == DurableSyncAttemptBinding::range_plan_v1 &&
        partial.value().bytes < attempt.worker_id;
    if (partial && partial.value().bytes != 0U &&
        (retain_whole || retain_range)) {
      DurableSyncAttempt restart_attempt = attempt;
      restart_attempt.state = DurableSyncAttemptState::restart_retained;
      retained.push_back(restart_attempt);
      recovered.push_back(RecoveredSyncAttempt{
          restart_attempt, SyncAttemptRecoveryDisposition::retained});
      continue;
    }
    if (!partial && partial.status().code() != ErrorCode::not_found &&
        partial.status().code() != ErrorCode::protocol_error) {
      return partial.status();
    }
    const Status discarded = discard_sync_attempt_staging(
        policy, attempt.attempt_id, transaction);
    if (!discarded.ok()) return discarded;
    recovered.push_back(RecoveredSyncAttempt{
        attempt, SyncAttemptRecoveryDisposition::fenced});
  }
  if (recovered.empty()) return recovered;
  journal.value().active = std::move(retained);
  const Status signed_state =
      advance_and_sign(journal.value(), identity, sodium);
  if (!signed_state.ok()) return signed_state;
  auto encoded = encode_sync_attempt_journal(journal.value());
  if (!encoded) return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok()) return stored;
  return recovered;
}

} // namespace iotox::sync
