#include "iotox/sync_publication.hpp"

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
                                                 'S', 'H', 'D', '1'};
constexpr std::string_view kSignatureDomain =
    "iotox-sync-head-signature-v1";
constexpr std::string_view kRecordDomain = "iotox-sync-head-record-v1";
constexpr std::size_t kNamespaceOffset = 168U;
constexpr std::size_t kNamespaceBytes = 64U;

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] = static_cast<std::uint8_t>(value >> (56U - index * 8U));
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
  std::copy(value.begin(), value.end(), output.begin() +
                                             static_cast<std::ptrdiff_t>(offset));
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

bool writer_allowed(const NamespacePolicy &policy,
                    const PrincipalId &writer) {
  return std::binary_search(policy.writers.begin(), policy.writers.end(),
                            writer);
}

Result<SignedHeadBytes> read_signed_head_file(
    const std::filesystem::path &path) {
  const int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT)
      return Status{ErrorCode::not_found,
                    "signed sync HEAD does not exist: " + path.string()};
    return Status{ErrorCode::io_error,
                  "unable to open signed sync HEAD '" + path.string() +
                      "': " + std::strerror(errno)};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0) {
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to inspect signed sync HEAD: " +
                      std::string(std::strerror(saved))};
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size != static_cast<off_t>(kSignedHeadBytes)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "signed sync HEAD is not one private fixed-size regular file"};
  }
  SignedHeadBytes bytes{};
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
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete signed sync HEAD: " +
                      std::string(std::strerror(saved))};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close signed sync HEAD: " +
                      std::string(std::strerror(errno))};
  }
  return bytes;
}

bool same_publication(const SignedHead &head,
                      const SignedHeadPublicationRequest &request) noexcept {
  return head.artifact == request.artifact &&
         head.manifest == request.manifest &&
         head.artifact_bytes == request.artifact_bytes &&
         head.manifest_bytes == request.manifest_bytes;
}

Status validate_unsigned_head(const NamespacePolicy &policy,
                              const SignedHead &head) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (head.namespace_id != policy.id || !valid_namespace_id(head.namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD namespace does not match policy"};
  }
  if (!writer_allowed(policy, head.writer) || all_zero(head.writer)) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD writer is not authorized"};
  }
  if (head.engine != policy.engine) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD engine does not match policy"};
  }
  if (head.generation == 0U || all_zero(head.artifact) ||
      all_zero(head.manifest) || head.artifact_bytes == 0U ||
      head.manifest_bytes == 0U ||
      head.artifact_bytes > policy.quotas.maximum_artifact_bytes ||
      head.manifest_bytes > policy.quotas.maximum_manifest_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD identity or size is invalid"};
  }
  const bool genesis = head.generation == 1U;
  if ((genesis && !all_zero(head.parent)) ||
      (!genesis && all_zero(head.parent))) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD generation and parent disagree"};
  }
  return Status::success();
}

Result<security::Digest> signing_digest(const SignedHead &head,
                                        const security::Sodium &sodium) {
  auto body = encode_signed_head_body(head);
  if (!body.ok())
    return body.status();
  return sodium.hash(kSignatureDomain, body.value());
}

} // namespace

Result<SignedHeadBody> encode_signed_head_body(const SignedHead &head) {
  if (!valid_namespace_id(head.namespace_id) ||
      head.namespace_id.size() > kNamespaceBytes ||
      (head.engine != Engine::range_v1 &&
       head.engine != Engine::content_v2 &&
       head.engine != Engine::treepack_v1) ||
      head.generation == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD contains an invalid field"};
  }
  SignedHeadBody output{};
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = static_cast<std::uint8_t>(head.engine);
  output[9U] = static_cast<std::uint8_t>(head.namespace_id.size());
  write_u64(output, 16U, head.generation);
  write_u64(output, 24U, head.artifact_bytes);
  write_u64(output, 32U, head.manifest_bytes);
  write_array(output, 40U, head.writer);
  write_array(output, 72U, head.parent);
  write_array(output, 104U, head.artifact);
  write_array(output, 136U, head.manifest);
  std::copy(head.namespace_id.begin(), head.namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
  return output;
}

Result<SignedHeadBytes> encode_signed_head(const SignedHead &head) {
  auto body = encode_signed_head_body(head);
  if (!body.ok())
    return body.status();
  SignedHeadBytes output{};
  std::copy(body.value().begin(), body.value().end(), output.begin());
  std::copy(head.signature.begin(), head.signature.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kSignedHeadBodyBytes));
  return output;
}

Result<SignedHead> decode_signed_head(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSignedHeadBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[9U] == 0U || bytes[9U] > kNamespaceBytes ||
      !all_zero(bytes.subspan(10U, 6U))) {
    return Status{ErrorCode::protocol_error,
                  "signed sync HEAD size, magic, or header is invalid"};
  }
  const std::size_t namespace_size = bytes[9U];
  if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_size,
                              kNamespaceBytes - namespace_size))) {
    return Status{ErrorCode::protocol_error,
                  "signed sync HEAD namespace padding is nonzero"};
  }
  SignedHead head;
  head.engine = static_cast<Engine>(bytes[8U]);
  head.namespace_id.assign(
      reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
      namespace_size);
  head.generation = read_u64(bytes, 16U);
  head.artifact_bytes = read_u64(bytes, 24U);
  head.manifest_bytes = read_u64(bytes, 32U);
  read_array(bytes, 40U, head.writer);
  read_array(bytes, 72U, head.parent);
  read_array(bytes, 104U, head.artifact);
  read_array(bytes, 136U, head.manifest);
  read_array(bytes, kSignedHeadBodyBytes, head.signature);
  auto canonical = encode_signed_head(head);
  if (!canonical.ok() || !std::equal(canonical.value().begin(),
                                     canonical.value().end(), bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "signed sync HEAD record is not canonical"};
  }
  return head;
}

Status verify_signed_head(const NamespacePolicy &policy, const SignedHead &head,
                          const security::Sodium &sodium) {
  const Status valid = validate_unsigned_head(policy, head);
  if (!valid.ok())
    return valid;
  auto digest = signing_digest(head, sodium);
  if (!digest.ok())
    return digest.status();
  return sodium.verify_detached(head.signature, digest.value(), head.writer);
}

Result<Digest> signed_head_record_digest(const SignedHead &head,
                                         const security::Sodium &sodium) {
  auto encoded = encode_signed_head(head);
  if (!encoded.ok())
    return encoded.status();
  return sodium.hash(kRecordDomain, encoded.value());
}

Result<CandidateHead> verified_candidate_head(const NamespacePolicy &policy,
                                              const SignedHead &head,
                                              const security::Sodium &sodium) {
  const Status verified = verify_signed_head(policy, head, sodium);
  if (!verified.ok())
    return verified;
  auto record = signed_head_record_digest(head, sodium);
  if (!record.ok())
    return record.status();
  return CandidateHead{head.namespace_id, head.writer, head.engine,
                       head.generation,     record.value(), head.parent,
                       head.artifact,       head.manifest,
                       head.artifact_bytes, head.manifest_bytes};
}

Result<SignedHead> create_signed_head(
    const NamespacePolicy &policy,
    const SignedHeadPublicationRequest &request,
    const std::optional<SignedHead> &previous,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  SignedHead head;
  head.namespace_id = policy.id;
  head.writer = identity.public_key();
  head.engine = policy.engine;
  head.artifact = request.artifact;
  head.manifest = request.manifest;
  head.artifact_bytes = request.artifact_bytes;
  head.manifest_bytes = request.manifest_bytes;
  head.generation = 1U;

  if (previous.has_value()) {
    const Status verified = verify_signed_head(policy, *previous, sodium);
    if (!verified.ok())
      return verified;
    if (previous->writer != identity.public_key()) {
      return Status{ErrorCode::invalid_argument,
                    "signed sync HEAD predecessor belongs to another writer"};
    }
    if (previous->generation == std::numeric_limits<std::uint64_t>::max()) {
      return Status{ErrorCode::resource_exhausted,
                    "signed sync HEAD generation is exhausted"};
    }
    head.generation = previous->generation + 1U;
    auto parent = signed_head_record_digest(*previous, sodium);
    if (!parent.ok())
      return parent.status();
    head.parent = parent.value();
  }

  const Status valid = validate_unsigned_head(policy, head);
  if (!valid.ok())
    return valid;
  auto digest = signing_digest(head, sodium);
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  head.signature = signature.value();
  const Status verified = verify_signed_head(policy, head, sodium);
  if (!verified.ok())
    return Status{ErrorCode::internal_error,
                  "new signed sync HEAD did not verify"};
  return head;
}

SignedHeadStore::SignedHeadStore(
    std::filesystem::path root,
    std::shared_ptr<SyncGuardedStateWitness> witness)
    : root_(std::move(root)), witness_(std::move(witness)) {}

std::filesystem::path
SignedHeadStore::path_for(std::string_view namespace_id) const {
  return root_ / "published-heads" /
         (std::string(namespace_id) + ".signed-head");
}

Result<std::optional<SignedHead>>
SignedHeadStore::load(const NamespacePolicy &policy,
                      const security::Sodium &sodium) const {
  std::scoped_lock lock(mutex_);
  return load_unlocked(policy, sodium);
}

Result<std::optional<SignedHead>> SignedHeadStore::load(
    const NamespacePolicy &policy, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
  std::scoped_lock lock(mutex_);
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  return load_unlocked(policy, sodium);
}

Result<std::optional<SignedHead>>
SignedHeadStore::load_unlocked(const NamespacePolicy &policy,
                               const security::Sodium &sodium) const {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD store root does not match namespace policy"};
  }
  auto bytes = read_signed_head_file(path_for(policy.id));
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found)
      return std::optional<SignedHead>{};
    return bytes.status();
  }
  auto decoded = decode_signed_head(bytes.value());
  if (!decoded.ok())
    return decoded.status();
  const Status verified = verify_signed_head(policy, decoded.value(), sodium);
  if (!verified.ok())
    return verified;
  return std::optional<SignedHead>{std::move(decoded.value())};
}

Result<SignedHeadPublicationResult> SignedHeadStore::publish(
    const NamespacePolicy &policy,
    const SignedHeadPublicationRequest &request,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD store root does not match namespace policy"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return publish(policy, request, identity, sodium, transaction.value());
}

Result<SignedHeadPublicationResult> SignedHeadStore::publish(
    const NamespacePolicy &policy,
    const SignedHeadPublicationRequest &request,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  std::scoped_lock lock(mutex_);
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD store root does not match namespace policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  auto previous = load_unlocked(policy, sodium);
  if (!previous.ok())
    return previous.status();
  if (previous.value().has_value() &&
      previous.value()->writer != identity.public_key()) {
    return Status{ErrorCode::invalid_argument,
                  "signed sync HEAD predecessor belongs to another writer"};
  }
  if (previous.value().has_value() &&
      same_publication(*previous.value(), request)) {
    const Status reconciled = witness_
        ? witness_->reconcile(policy, transaction)
        : reconcile_sync_rollback_roots(
              policy, identity, sodium, transaction);
    if (!reconciled.ok())
      return reconciled;
    auto record = signed_head_record_digest(*previous.value(), sodium);
    if (!record.ok())
      return record.status();
    return SignedHeadPublicationResult{*previous.value(), record.value(),
                                       false, true};
  }
  auto head = create_signed_head(policy, request, previous.value(), identity,
                                 sodium);
  if (!head.ok())
    return head.status();
  auto encoded = encode_signed_head(head.value());
  if (!encoded.ok())
    return encoded.status();
  auto record = signed_head_record_digest(head.value(), sodium);
  if (!record.ok())
    return record.status();
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  SyncReachabilityRoots next = roots.value();
  next.published = head.value();
  const Status stored = guarded_sync_root_transition(
      policy, roots.value(), next, identity, sodium, transaction, [&]() {
        return StateStore::write_atomic(path_for(policy.id), encoded.value());
      }, witness_.get());
  if (!stored.ok())
    return stored;
  return SignedHeadPublicationResult{std::move(head.value()), record.value(),
                                     !previous.value().has_value(), false};
}

} // namespace iotox::sync
