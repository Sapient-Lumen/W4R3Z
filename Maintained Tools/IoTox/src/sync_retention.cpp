#include "iotox/sync_retention.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_guarded_witness.hpp"
#include "iotox/sync_rollback.hpp"

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
                                                 'R', 'T', 'N', '2'};
constexpr std::string_view kSignatureDomain =
    "iotox-sync-retention-signature-v2";
constexpr std::string_view kRecordDomain = "iotox-sync-retention-record-v2";
constexpr std::size_t kHeaderBytes = 160U;
constexpr std::size_t kRevisionBytes = 120U;
constexpr std::size_t kSignerOffset = 32U;
constexpr std::size_t kPreviousOffset = 64U;
constexpr std::size_t kNamespaceOffset = 96U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kSignatureBytes = security::kSignatureBytes;

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index)
    output[offset + index] =
        static_cast<std::uint8_t>(value >> (56U - index * 8U));
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index)
    value = (value << 8U) | input[offset + index];
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
                     [](std::uint8_t value) { return value == 0U; });
}

Status validate_snapshot(const RetentionSnapshot &snapshot,
                         std::uint64_t maximum_revisions) {
  if (!valid_namespace_id(snapshot.namespace_id) ||
      snapshot.revisions.size() > maximum_revisions ||
      all_zero(snapshot.signer) || snapshot.mutation == 0U ||
      (snapshot.mutation == 1U && !all_zero(snapshot.previous)) ||
      (snapshot.mutation != 1U && all_zero(snapshot.previous))) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention identity, mutation, or count is invalid"};
  }
  std::uint64_t previous_generation = 0U;
  std::vector<Digest> records;
  records.reserve(snapshot.revisions.size());
  for (const RetainedRevision &revision : snapshot.revisions) {
    if (revision.generation == 0U ||
        revision.generation <= previous_generation || all_zero(revision.record) ||
        all_zero(revision.artifact) || all_zero(revision.manifest) ||
        revision.artifact_bytes == 0U || revision.manifest_bytes == 0U) {
      return Status{ErrorCode::invalid_argument,
                    "sync retained revision is invalid or unsorted"};
    }
    previous_generation = revision.generation;
    records.push_back(revision.record);
  }
  std::sort(records.begin(), records.end());
  if (std::adjacent_find(records.begin(), records.end()) != records.end()) {
    return Status{ErrorCode::invalid_argument,
                  "sync retained revision records are duplicated"};
  }
  return Status::success();
}

Status ensure_private_directory(const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync retention directory: " +
                      error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "sync retention directory is not real and owner-owned"};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure sync retention directory: " +
                      error.message()};
  }
  return Status::success();
}

Status validate_private_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync retention directory is not private and owner-owned"};
  }
  return Status::success();
}

Status prepare_retention_parent(const std::filesystem::path &root) {
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok())
    return prepared;
  return ensure_private_directory(root / "retention");
}

Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path, std::uint64_t maximum_revisions) {
  const int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT)
      return Status{ErrorCode::not_found, "sync retention state is absent"};
    return Status{ErrorCode::io_error,
                  "unable to open sync retention state: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0) {
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to inspect sync retention state: " +
                      std::string(std::strerror(saved))};
  }
  const std::uint64_t maximum_bytes =
      kHeaderBytes + maximum_revisions * kRevisionBytes + kSignatureBytes;
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size < static_cast<off_t>(kHeaderBytes) ||
      static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync retention state is not one bounded private file"};
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
    if (count < 0 && errno == EINTR)
      continue;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete sync retention state"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close sync retention state"};
  }
  return bytes;
}

RetainedRevision retained_from_head(const AcceptedHead &head) {
  return RetainedRevision{head.generation, head.record, head.artifact,
                          head.manifest,   head.artifact_bytes,
                          head.manifest_bytes};
}

Result<std::vector<std::uint8_t>>
encode_retention_body(const RetentionSnapshot &snapshot) {
  const Status valid = validate_snapshot(
      snapshot, std::numeric_limits<std::uint64_t>::max());
  if (!valid.ok())
    return valid;
  if (snapshot.revisions.size() >
      (std::numeric_limits<std::size_t>::max() - kHeaderBytes) /
          kRevisionBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync retention encoding is too large"};
  }
  std::vector<std::uint8_t> output(
      kHeaderBytes + snapshot.revisions.size() * kRevisionBytes, 0U);
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = static_cast<std::uint8_t>(snapshot.namespace_id.size());
  write_u64(output, 16U, snapshot.mutation);
  write_u64(output, 24U, snapshot.revisions.size());
  write_array(output, kSignerOffset, snapshot.signer);
  write_array(output, kPreviousOffset, snapshot.previous);
  std::copy(snapshot.namespace_id.begin(), snapshot.namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
  std::size_t offset = kHeaderBytes;
  for (const RetainedRevision &revision : snapshot.revisions) {
    write_u64(output, offset, revision.generation);
    write_array(output, offset + 8U, revision.record);
    write_array(output, offset + 40U, revision.artifact);
    write_array(output, offset + 72U, revision.manifest);
    write_u64(output, offset + 104U, revision.artifact_bytes);
    write_u64(output, offset + 112U, revision.manifest_bytes);
    offset += kRevisionBytes;
  }
  return output;
}

Status sign_snapshot(RetentionSnapshot &snapshot,
                     const security::DeviceIdentity &identity,
                     const security::Sodium &sodium) {
  snapshot.signer = identity.public_key();
  auto body = encode_retention_body(snapshot);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  snapshot.signature = signature.value();
  return verify_retention_snapshot(snapshot, identity.public_key(), sodium);
}

} // namespace

Result<std::vector<std::uint8_t>>
encode_retention_snapshot(const RetentionSnapshot &snapshot) {
  auto body = encode_retention_body(snapshot);
  if (!body.ok())
    return body.status();
  std::vector<std::uint8_t> output = std::move(body.value());
  output.insert(output.end(), snapshot.signature.begin(),
                snapshot.signature.end());
  return output;
}

Result<RetentionSnapshot>
decode_retention_snapshot(std::span<const std::uint8_t> bytes,
                          std::uint64_t maximum_revisions) {
  if (bytes.size() < kHeaderBytes + kSignatureBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] == 0U || bytes[8U] > kNamespaceBytes ||
      !all_zero(bytes.subspan(9U, 7U))) {
    return Status{ErrorCode::protocol_error,
                  "sync retention header is invalid"};
  }
  const std::uint64_t count = read_u64(bytes, 24U);
  if (count > maximum_revisions ||
      count > (std::numeric_limits<std::size_t>::max() - kHeaderBytes -
               kSignatureBytes) /
                  kRevisionBytes ||
      bytes.size() != kHeaderBytes + static_cast<std::size_t>(count) *
                                        kRevisionBytes + kSignatureBytes) {
    return Status{ErrorCode::protocol_error,
                  "sync retention count or size is invalid"};
  }
  const std::size_t namespace_size = bytes[8U];
  if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_size,
                              kNamespaceBytes - namespace_size))) {
    return Status{ErrorCode::protocol_error,
                  "sync retention namespace padding is nonzero"};
  }
  RetentionSnapshot snapshot;
  snapshot.namespace_id.assign(
      reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
      namespace_size);
  snapshot.mutation = read_u64(bytes, 16U);
  read_array(bytes, kSignerOffset, snapshot.signer);
  read_array(bytes, kPreviousOffset, snapshot.previous);
  snapshot.revisions.reserve(static_cast<std::size_t>(count));
  std::size_t offset = kHeaderBytes;
  for (std::uint64_t index = 0U; index < count; ++index) {
    RetainedRevision revision;
    revision.generation = read_u64(bytes, offset);
    read_array(bytes, offset + 8U, revision.record);
    read_array(bytes, offset + 40U, revision.artifact);
    read_array(bytes, offset + 72U, revision.manifest);
    revision.artifact_bytes = read_u64(bytes, offset + 104U);
    revision.manifest_bytes = read_u64(bytes, offset + 112U);
    snapshot.revisions.push_back(revision);
    offset += kRevisionBytes;
  }
  read_array(bytes, offset, snapshot.signature);
  const Status valid = validate_snapshot(snapshot, maximum_revisions);
  if (!valid.ok())
    return Status{ErrorCode::protocol_error, valid.message()};
  auto canonical = encode_retention_snapshot(snapshot);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync retention state is not canonical"};
  }
  return snapshot;
}

Status verify_retention_snapshot(
    const RetentionSnapshot &snapshot,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  if (all_zero(expected_device) || snapshot.signer != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "sync retention signer is not the expected device"};
  }
  auto body = encode_retention_body(snapshot);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  return sodium.verify_detached(snapshot.signature, digest.value(),
                                snapshot.signer);
}

Result<Digest> retention_snapshot_record_digest(
    const RetentionSnapshot &snapshot, const security::Sodium &sodium) {
  auto encoded = encode_retention_snapshot(snapshot);
  if (!encoded.ok())
    return encoded.status();
  return sodium.hash(kRecordDomain, encoded.value());
}

RetentionStore::RetentionStore(
    std::filesystem::path root,
    std::shared_ptr<SyncGuardedStateWitness> witness)
    : root_(std::move(root)), witness_(std::move(witness)) {}

std::filesystem::path
RetentionStore::path_for(std::string_view namespace_id) const {
  return root_ / "retention" /
         (std::string(namespace_id) + ".retained-revisions");
}

Result<RetentionSnapshot>
RetentionStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention expected device is zero"};
  }
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention root does not match namespace policy"};
  }
  auto bytes =
      read_private_file(path_for(policy.id),
                        policy.quotas.maximum_retained_revisions);
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found)
      return RetentionSnapshot{policy.id, {}, expected_device};
    return bytes.status();
  }
  auto snapshot = decode_retention_snapshot(
      bytes.value(), policy.quotas.maximum_retained_revisions);
  Status private_parent = validate_private_directory(root_);
  if (!private_parent.ok())
    return private_parent;
  private_parent = validate_private_directory(root_ / "retention");
  if (!private_parent.ok())
    return private_parent;
  if (!snapshot.ok())
    return snapshot.status();
  if (snapshot.value().namespace_id != policy.id) {
    return Status{ErrorCode::protocol_error,
                  "sync retention path and namespace differ"};
  }
  const Status authenticated =
      verify_retention_snapshot(snapshot.value(), expected_device, sodium);
  if (!authenticated.ok())
    return authenticated;
  for (const RetainedRevision &revision : snapshot.value().revisions) {
    if (revision.artifact_bytes > policy.quotas.maximum_artifact_bytes ||
        revision.manifest_bytes > policy.quotas.maximum_manifest_bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync retained revision exceeds namespace quotas"};
    }
  }
  return snapshot;
}

Result<RetentionUpdate> RetentionStore::pin(const NamespacePolicy &policy,
                                             const AcceptedHead &head,
                                             const security::DeviceIdentity &identity,
                                             const security::Sodium &sodium) {
  const Status valid_head = validate_accepted_head(policy, head);
  if (!valid_head.ok())
    return valid_head;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention root does not match namespace policy"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return pin(policy, head, identity, sodium, transaction.value());
}

Result<RetentionUpdate> RetentionStore::pin(
    const NamespacePolicy &policy, const AcceptedHead &head,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status valid_head = validate_accepted_head(policy, head);
  if (!valid_head.ok())
    return valid_head;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention root does not match namespace policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  const Status prepared = prepare_retention_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto snapshot = load(policy, identity.public_key(), sodium);
  if (!snapshot.ok())
    return snapshot.status();
  const RetainedRevision revision = retained_from_head(head);
  for (const RetainedRevision &existing : snapshot.value().revisions) {
    if (existing.record == revision.record) {
      if (existing != revision) {
        return Status{ErrorCode::protocol_error,
                      "sync retention record identity conflicts"};
      }
      const Status reconciled = witness_
          ? witness_->reconcile(policy, transaction)
          : reconcile_sync_rollback_roots(
                policy, identity, sodium, transaction);
      if (!reconciled.ok())
        return reconciled;
      return RetentionUpdate::duplicate;
    }
    if (existing.generation == revision.generation) {
      return Status{ErrorCode::protocol_error,
                    "sync retention generation fork is refused"};
    }
  }
  if (snapshot.value().revisions.size() >=
      policy.quotas.maximum_retained_revisions) {
    return Status{ErrorCode::resource_exhausted,
                  "sync retained revision capacity is exhausted"};
  }
  Digest previous_record{};
  if (snapshot.value().mutation != 0U) {
    auto previous =
        retention_snapshot_record_digest(snapshot.value(), sodium);
    if (!previous.ok())
      return previous.status();
    previous_record = previous.value();
  }
  auto position = std::lower_bound(
      snapshot.value().revisions.begin(), snapshot.value().revisions.end(),
      revision.generation,
      [](const RetainedRevision &value, std::uint64_t generation) {
        return value.generation < generation;
      });
  snapshot.value().revisions.insert(position, revision);
  if (snapshot.value().mutation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync retention mutation counter is exhausted"};
  }
  if (snapshot.value().mutation == 0U) {
    snapshot.value().mutation = 1U;
    snapshot.value().previous = Digest{};
  } else {
    snapshot.value().previous = previous_record;
    ++snapshot.value().mutation;
  }
  const Status signed_state = sign_snapshot(snapshot.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_retention_snapshot(snapshot.value());
  if (!encoded.ok())
    return encoded.status();
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  SyncReachabilityRoots next = roots.value();
  next.retained = snapshot.value();
  const Status stored = guarded_sync_root_transition(
      policy, roots.value(), next, identity, sodium, transaction, [&]() {
        return StateStore::write_atomic(path_for(policy.id), encoded.value());
      }, witness_.get());
  if (!stored.ok())
    return stored;
  return RetentionUpdate::inserted;
}

Result<bool> RetentionStore::unpin(const NamespacePolicy &policy,
                                   const Digest &record,
                                   const security::DeviceIdentity &identity,
                                   const security::Sodium &sodium) {
  if (all_zero(record)) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention record identity is zero"};
  }
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention root does not match namespace policy"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return unpin(policy, record, identity, sodium, transaction.value());
}

Result<bool> RetentionStore::unpin(
    const NamespacePolicy &policy, const Digest &record,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  if (all_zero(record)) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention record identity is zero"};
  }
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync retention root does not match namespace policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  const Status prepared = prepare_retention_parent(root_);
  if (!prepared.ok())
    return prepared;
  auto snapshot = load(policy, identity.public_key(), sodium);
  if (!snapshot.ok())
    return snapshot.status();
  auto position = std::find_if(
      snapshot.value().revisions.begin(), snapshot.value().revisions.end(),
      [&](const RetainedRevision &revision) {
        return revision.record == record;
      });
  if (position == snapshot.value().revisions.end()) {
    const Status reconciled = witness_
        ? witness_->reconcile(policy, transaction)
        : reconcile_sync_rollback_roots(
              policy, identity, sodium, transaction);
    if (!reconciled.ok())
      return reconciled;
    return false;
  }
  if (snapshot.value().mutation == 0U ||
      snapshot.value().mutation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::protocol_error,
                  "sync retention mutation counter cannot advance"};
  }
  auto previous = retention_snapshot_record_digest(snapshot.value(), sodium);
  if (!previous.ok())
    return previous.status();
  snapshot.value().revisions.erase(position);
  snapshot.value().previous = previous.value();
  ++snapshot.value().mutation;
  const Status signed_state = sign_snapshot(snapshot.value(), identity, sodium);
  if (!signed_state.ok())
    return signed_state;
  auto encoded = encode_retention_snapshot(snapshot.value());
  if (!encoded.ok())
    return encoded.status();
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  SyncReachabilityRoots next = roots.value();
  next.retained = snapshot.value();
  const Status stored = guarded_sync_root_transition(
      policy, roots.value(), next, identity, sodium, transaction, [&]() {
        return StateStore::write_atomic(path_for(policy.id), encoded.value());
      }, witness_.get());
  if (!stored.ok())
    return stored;
  return true;
}

} // namespace iotox::sync
