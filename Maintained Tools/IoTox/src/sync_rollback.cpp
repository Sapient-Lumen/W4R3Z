#include "iotox/sync_rollback.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_guarded_witness.hpp"

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
                                                 'S', 'R', 'G', '1'};
constexpr std::uint8_t kFormat = 1U;
constexpr std::uint8_t kPending = 1U;
constexpr std::size_t kSignerOffset = 16U;
constexpr std::size_t kNamespaceOffset = 48U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kCommittedOffset = 112U;
constexpr std::size_t kPendingOffset = 272U;
constexpr std::size_t kHeadBytes = 160U;
constexpr std::size_t kBodyBytes = 432U;
constexpr std::size_t kGuardBytes =
    kBodyBytes + security::kSignatureBytes;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-rollback-guard-signature-v1";

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

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

Status validate_root(const SyncRollbackRoot &root, std::string_view label) {
  if ((root.counter == 0U) != all_zero(root.record)) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) +
                      " must be wholly absent or wholly initialized"};
  }
  return Status::success();
}

Status validate_head(const SyncRollbackHead &head, std::string_view label) {
  const std::array<std::pair<const SyncRollbackRoot *, std::string_view>, 4U>
      roots{{{&head.published, " published"},
             {&head.accepted, " accepted"},
             {&head.activated, " activated"},
             {&head.retained, " retained"}}};
  for (const auto &[root, suffix] : roots) {
    const Status valid =
        validate_root(*root, std::string(label) + std::string(suffix));
    if (!valid.ok())
      return valid;
  }
  return Status::success();
}

Status validate_guard(const SyncRollbackGuard &guard) {
  if (!valid_namespace_id(guard.namespace_id) || all_zero(guard.signer)) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard identity is invalid"};
  }
  Status valid = validate_head(guard.committed, "committed");
  if (!valid.ok())
    return valid;
  if (guard.pending.has_value()) {
    valid = validate_head(*guard.pending, "pending");
    if (!valid.ok())
      return valid;
    if (*guard.pending == guard.committed) {
      return Status{ErrorCode::protocol_error,
                    "sync rollback guard pending head is not a transition"};
    }
  }
  return Status::success();
}

void encode_root(const SyncRollbackRoot &root,
                 std::span<std::uint8_t> output, std::size_t offset) {
  write_u64(output, offset, root.counter);
  std::copy(root.record.begin(), root.record.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset + 8U));
}

SyncRollbackRoot decode_root(std::span<const std::uint8_t> input,
                             std::size_t offset) {
  SyncRollbackRoot root;
  root.counter = read_u64(input, offset);
  std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset + 8U),
              root.record.size(), root.record.begin());
  return root;
}

void encode_head(const SyncRollbackHead &head,
                 std::span<std::uint8_t> output, std::size_t offset) {
  encode_root(head.published, output, offset);
  encode_root(head.accepted, output, offset + 40U);
  encode_root(head.activated, output, offset + 80U);
  encode_root(head.retained, output, offset + 120U);
}

SyncRollbackHead decode_head(std::span<const std::uint8_t> input,
                             std::size_t offset) {
  return SyncRollbackHead{decode_root(input, offset),
                          decode_root(input, offset + 40U),
                          decode_root(input, offset + 80U),
                          decode_root(input, offset + 120U)};
}

Result<std::array<std::uint8_t, kBodyBytes>>
encode_guard_body(const SyncRollbackGuard &guard) {
  const Status valid = validate_guard(guard);
  if (!valid.ok())
    return valid;
  std::array<std::uint8_t, kBodyBytes> output{};
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = kFormat;
  output[9U] = guard.pending.has_value() ? kPending : 0U;
  output[10U] = static_cast<std::uint8_t>(guard.namespace_id.size());
  std::copy(guard.signer.begin(), guard.signer.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kSignerOffset));
  std::copy(guard.namespace_id.begin(), guard.namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
  encode_head(guard.committed, output, kCommittedOffset);
  if (guard.pending.has_value())
    encode_head(*guard.pending, output, kPendingOffset);
  return output;
}

Status sign_guard(SyncRollbackGuard &guard,
                  const security::DeviceIdentity &identity,
                  const security::Sodium &sodium) {
  guard.signer = identity.public_key();
  auto body = encode_guard_body(guard);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  guard.signature = signature.value();
  return Status::success();
}

Status ensure_private_directory(const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync rollback directory: " +
                      error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback directory is not real and owner-owned"};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure sync rollback directory: " +
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
                  "sync rollback directory is not private and owner-owned"};
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>> read_guard_file(
    const std::filesystem::path &path) {
  const int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT)
      return Status{ErrorCode::not_found, "sync rollback guard is absent"};
    return Status{ErrorCode::io_error,
                  "unable to open sync rollback guard: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0 ||
      !S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size != static_cast<off_t>(kGuardBytes)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard is not one exact private file"};
  }
  std::vector<std::uint8_t> bytes(kGuardBytes);
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
                  "unable to read complete sync rollback guard"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close sync rollback guard"};
  }
  return bytes;
}

Status write_guard_file(const std::filesystem::path &root,
                        const std::filesystem::path &path,
                        const SyncRollbackGuard &guard) {
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok())
    return prepared;
  prepared = ensure_private_directory(root / "rollback-guards");
  if (!prepared.ok())
    return prepared;
  auto encoded = encode_sync_rollback_guard(guard);
  if (!encoded.ok())
    return encoded.status();
  return StateStore::write_atomic(path, encoded.value());
}

} // namespace

bool SyncRollbackHead::empty() const noexcept {
  return !published.present() && !accepted.present() && !activated.present() &&
         !retained.present();
}

Result<std::vector<std::uint8_t>>
encode_sync_rollback_guard(const SyncRollbackGuard &guard) {
  auto body = encode_guard_body(guard);
  if (!body.ok())
    return body.status();
  std::vector<std::uint8_t> output(body.value().begin(), body.value().end());
  output.insert(output.end(), guard.signature.begin(), guard.signature.end());
  return output;
}

Result<SyncRollbackGuard>
decode_sync_rollback_guard(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kGuardBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] != kFormat || (bytes[9U] & ~kPending) != 0U ||
      bytes[10U] == 0U || bytes[10U] > kNamespaceBytes ||
      !all_zero(bytes.subspan(11U, 5U))) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard header is invalid"};
  }
  const std::size_t namespace_size = bytes[10U];
  if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_size,
                              kNamespaceBytes - namespace_size))) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard namespace padding is nonzero"};
  }
  SyncRollbackGuard guard;
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kSignerOffset),
              guard.signer.size(), guard.signer.begin());
  guard.namespace_id.assign(
      reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
      namespace_size);
  guard.committed = decode_head(bytes, kCommittedOffset);
  if ((bytes[9U] & kPending) != 0U) {
    guard.pending = decode_head(bytes, kPendingOffset);
  } else if (!all_zero(bytes.subspan(kPendingOffset, kHeadBytes))) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard has pending bytes without its flag"};
  }
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kBodyBytes),
              guard.signature.size(), guard.signature.begin());
  const Status valid = validate_guard(guard);
  if (!valid.ok())
    return valid;
  auto canonical = encode_sync_rollback_guard(guard);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard is not canonical"};
  }
  return guard;
}

Status verify_sync_rollback_guard(
    const NamespacePolicy &policy, const SyncRollbackGuard &guard,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (guard.namespace_id != policy.id || all_zero(expected_device) ||
      guard.signer != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard namespace or signer is unexpected"};
  }
  auto body = encode_guard_body(guard);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  return sodium.verify_detached(guard.signature, digest.value(), guard.signer);
}

Result<SyncRollbackHead> make_sync_rollback_head(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const SyncReachabilityRoots &roots, const security::Sodium &sodium) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "sync rollback expected device is zero"};
  }
  SyncRollbackHead head;
  if (roots.published.has_value()) {
    if (roots.published->writer != expected_device)
      return Status{ErrorCode::protocol_error,
                    "sync rollback published root has a foreign writer"};
    const Status verified = verify_signed_head(policy, *roots.published, sodium);
    if (!verified.ok())
      return verified;
    auto record = signed_head_record_digest(*roots.published, sodium);
    if (!record.ok())
      return record.status();
    head.published = {roots.published->generation, record.value()};
  }
  if (roots.accepted.has_value()) {
    const Status valid = validate_accepted_head(policy, *roots.accepted);
    if (!valid.ok())
      return valid;
    head.accepted = {roots.accepted->generation, roots.accepted->record};
  }
  if (roots.activated.has_value()) {
    auto canonical = encode_activated_revision(*roots.activated);
    if (!canonical.ok() || roots.activated->namespace_id != policy.id ||
        roots.activated->artifact_bytes >
            policy.quotas.maximum_artifact_bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync rollback activated root is invalid"};
    }
    head.activated = {roots.activated->generation,
                      roots.activated->record};
  }
  if (roots.retained.mutation != 0U) {
    const Status verified = verify_retention_snapshot(
        roots.retained, expected_device, sodium);
    if (!verified.ok())
      return verified;
    auto record = retention_snapshot_record_digest(roots.retained, sodium);
    if (!record.ok())
      return record.status();
    head.retained = {roots.retained.mutation, record.value()};
  } else if (roots.retained.namespace_id != policy.id ||
             !roots.retained.revisions.empty()) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback absent retention root is invalid"};
  }
  return head;
}

Result<SyncReachabilityRoots> load_sync_rollback_roots(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  SyncReachabilityRoots roots;
  SignedHeadStore published_store(policy.root);
  auto published = published_store.load(policy, sodium);
  if (!published.ok())
    return published.status();
  roots.published = std::move(published.value());
  AcceptedHeadStore accepted_store(policy.root);
  auto accepted = accepted_store.load(policy, expected_device, sodium);
  if (!accepted.ok())
    return accepted.status();
  roots.accepted = std::move(accepted.value());
  ActivatedRevisionStore activated_store(policy.root);
  auto activated = activated_store.load(policy, expected_device, sodium);
  if (!activated.ok())
    return activated.status();
  roots.activated = std::move(activated.value());
  RetentionStore retention_store(policy.root);
  auto retained = retention_store.load(policy, expected_device, sodium);
  if (!retained.ok())
    return retained.status();
  roots.retained = std::move(retained.value());
  return roots;
}

Status reconcile_sync_rollback_roots(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  auto current = make_sync_rollback_head(
      policy, identity.public_key(), roots.value(), sodium);
  if (!current.ok())
    return current.status();
  SyncRollbackGuardStore guard(policy.root);
  auto reconciled = guard.reconcile(policy, current.value(), identity, sodium,
                                    transaction);
  return reconciled.ok() ? Status::success() : reconciled.status();
}

Status guarded_sync_root_transition(
    const NamespacePolicy &policy, const SyncReachabilityRoots &current,
    const SyncReachabilityRoots &next,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    const SyncRootCommit &commit,
    SyncGuardedStateWitness *witness) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (!commit) {
    return Status{ErrorCode::invalid_argument,
                  "guarded sync transition requires one root commit"};
  }
  if (witness != nullptr) {
    return witness->transition(policy, current, next, transaction, commit);
  }
  auto current_head = make_sync_rollback_head(
      policy, identity.public_key(), current, sodium);
  if (!current_head.ok())
    return current_head.status();
  auto next_head =
      make_sync_rollback_head(policy, identity.public_key(), next, sodium);
  if (!next_head.ok())
    return next_head.status();
  SyncRollbackGuardStore guard(policy.root);
  const Status begun = guard.begin(policy, current_head.value(),
                                   next_head.value(), identity, sodium,
                                   transaction);
  if (!begun.ok())
    return begun;
  const Status committed = commit();
  if (!committed.ok())
    return committed;
  return guard.finish(policy, next_head.value(), identity, sodium,
                      transaction);
}

SyncRollbackGuardStore::SyncRollbackGuardStore(std::filesystem::path root)
    : root_(std::move(root)) {}

std::filesystem::path
SyncRollbackGuardStore::path_for(std::string_view namespace_id) const {
  return root_ / "rollback-guards" /
         (std::string(namespace_id) + ".rollback-guard");
}

Result<std::optional<SyncRollbackGuard>> SyncRollbackGuardStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "sync rollback expected device is zero"};
  }
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync rollback store does not match namespace policy"};
  }
  struct stat metadata {};
  if (::lstat(root_.c_str(), &metadata) != 0) {
    if (errno == ENOENT)
      return std::optional<SyncRollbackGuard>{};
    return Status{ErrorCode::io_error,
                  "unable to inspect sync rollback root: " +
                      std::string(std::strerror(errno))};
  }
  Status private_directory = validate_private_directory(root_);
  if (!private_directory.ok())
    return private_directory;
  const std::filesystem::path directory = root_ / "rollback-guards";
  if (::lstat(directory.c_str(), &metadata) != 0) {
    if (errno == ENOENT)
      return std::optional<SyncRollbackGuard>{};
    return Status{ErrorCode::io_error,
                  "unable to inspect sync rollback directory: " +
                      std::string(std::strerror(errno))};
  }
  private_directory = validate_private_directory(directory);
  if (!private_directory.ok())
    return private_directory;
  auto bytes = read_guard_file(path_for(policy.id));
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found)
      return std::optional<SyncRollbackGuard>{};
    return bytes.status();
  }
  auto guard = decode_sync_rollback_guard(bytes.value());
  if (!guard.ok())
    return guard.status();
  const Status verified =
      verify_sync_rollback_guard(policy, guard.value(), expected_device, sodium);
  if (!verified.ok())
    return verified;
  return std::optional<SyncRollbackGuard>{std::move(guard.value())};
}

Result<SyncRollbackReconcile> SyncRollbackGuardStore::reconcile(
    const NamespacePolicy &policy, const SyncRollbackHead &current,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status valid_current = validate_head(current, "current");
  if (!valid_current.ok())
    return valid_current;
  auto loaded = load(policy, identity.public_key(), sodium);
  if (!loaded.ok())
    return loaded.status();
  if (!loaded.value().has_value()) {
    if (current.empty())
      return SyncRollbackReconcile::absent_empty;
    return Status{ErrorCode::protocol_error,
                  "sync state exists without its rollback guard"};
  }
  SyncRollbackGuard guard = std::move(*loaded.value());
  const bool committed = guard.committed == current;
  const bool pending = guard.pending.has_value() && *guard.pending == current;
  if (!committed && !pending) {
    return Status{ErrorCode::protocol_error,
                  "sync root head diverges from its rollback guard"};
  }
  if (!guard.pending.has_value())
    return SyncRollbackReconcile::committed;
  const SyncRollbackReconcile result =
      pending ? SyncRollbackReconcile::recovered_after_state_commit
              : SyncRollbackReconcile::recovered_before_state_commit;
  if (pending)
    guard.committed = current;
  guard.pending.reset();
  const Status signed_guard = sign_guard(guard, identity, sodium);
  if (!signed_guard.ok())
    return signed_guard;
  const Status stored =
      write_guard_file(root_, path_for(policy.id), guard);
  if (!stored.ok())
    return stored;
  return result;
}

Result<SyncRollbackReconcile> SyncRollbackGuardStore::check(
    const NamespacePolicy &policy, const SyncRollbackHead &current,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const Status valid_current = validate_head(current, "current");
  if (!valid_current.ok())
    return valid_current;
  auto loaded = load(policy, expected_device, sodium);
  if (!loaded.ok())
    return loaded.status();
  if (!loaded.value().has_value()) {
    if (current.empty())
      return SyncRollbackReconcile::absent_empty;
    return Status{ErrorCode::protocol_error,
                  "sync state exists without its rollback guard"};
  }
  const SyncRollbackGuard &guard = *loaded.value();
  const bool committed = guard.committed == current;
  const bool pending = guard.pending.has_value() && *guard.pending == current;
  if (!committed && !pending) {
    return Status{ErrorCode::protocol_error,
                  "sync root head diverges from its rollback guard"};
  }
  if (!guard.pending.has_value())
    return SyncRollbackReconcile::committed;
  return pending ? SyncRollbackReconcile::recovered_after_state_commit
                 : SyncRollbackReconcile::recovered_before_state_commit;
}

Status SyncRollbackGuardStore::begin(
    const NamespacePolicy &policy, const SyncRollbackHead &current,
    const SyncRollbackHead &next,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  Status valid = validate_head(current, "current");
  if (!valid.ok())
    return valid;
  valid = validate_head(next, "next");
  if (!valid.ok())
    return valid;
  if (current == next) {
    return Status{ErrorCode::invalid_argument,
                  "sync rollback transition does not change the root head"};
  }
  auto reconciled = reconcile(policy, current, identity, sodium, transaction);
  if (!reconciled.ok())
    return reconciled.status();
  auto loaded = load(policy, identity.public_key(), sodium);
  if (!loaded.ok())
    return loaded.status();
  SyncRollbackGuard guard;
  if (loaded.value().has_value()) {
    guard = std::move(*loaded.value());
  } else {
    guard.namespace_id = policy.id;
    guard.committed = current;
  }
  guard.pending = next;
  const Status signed_guard = sign_guard(guard, identity, sodium);
  if (!signed_guard.ok())
    return signed_guard;
  return write_guard_file(root_, path_for(policy.id), guard);
}

Status SyncRollbackGuardStore::finish(
    const NamespacePolicy &policy, const SyncRollbackHead &current,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto loaded = load(policy, identity.public_key(), sodium);
  if (!loaded.ok())
    return loaded.status();
  if (!loaded.value().has_value()) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard disappeared before finish"};
  }
  SyncRollbackGuard guard = std::move(*loaded.value());
  if (!guard.pending.has_value()) {
    return guard.committed == current
               ? Status::success()
               : Status{ErrorCode::protocol_error,
                        "sync rollback guard committed head is stale"};
  }
  if (*guard.pending != current) {
    return Status{ErrorCode::protocol_error,
                  "sync rollback guard pending head was not committed"};
  }
  guard.committed = current;
  guard.pending.reset();
  const Status signed_guard = sign_guard(guard, identity, sodium);
  if (!signed_guard.ok())
    return signed_guard;
  return write_guard_file(root_, path_for(policy.id), guard);
}

} // namespace iotox::sync
