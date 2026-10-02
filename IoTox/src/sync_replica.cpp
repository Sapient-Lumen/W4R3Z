#include "iotox/sync_replica.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {'I', 'O', 'T', 'X',
                                                 'R', 'P', 'H', '1'};
constexpr std::uint8_t kFormat = 1U;
constexpr std::size_t kCustodianOffset = 16U;
constexpr std::size_t kHeadOffset = 48U;
constexpr std::size_t kBodyBytes = kHeadOffset + kSignedHeadBytes;
constexpr std::size_t kReplicaBytes = kBodyBytes + security::kSignatureBytes;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-replica-head-signature-v1";

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

Result<std::array<std::uint8_t, kBodyBytes>>
encode_replica_body(const ReplicaHead &replica) {
  if (all_zero(replica.custodian)) {
    return Status{ErrorCode::invalid_argument,
                  "sync replica custodian is zero"};
  }
  auto head = encode_signed_head(replica.head);
  if (!head.ok())
    return head.status();
  std::array<std::uint8_t, kBodyBytes> body{};
  std::copy(kMagic.begin(), kMagic.end(), body.begin());
  body[8U] = kFormat;
  std::copy(replica.custodian.begin(), replica.custodian.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kCustodianOffset));
  std::copy(head.value().begin(), head.value().end(),
            body.begin() + static_cast<std::ptrdiff_t>(kHeadOffset));
  return body;
}

Status sign_replica(ReplicaHead &replica,
                    const security::DeviceIdentity &identity,
                    const security::Sodium &sodium) {
  replica.custodian = identity.public_key();
  auto body = encode_replica_body(replica);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  replica.signature = signature.value();
  return Status::success();
}

Result<std::vector<std::uint8_t>>
read_replica_file(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found, "sync replica HEAD does not exist"};
    }
    return Status{ErrorCode::io_error, "unable to open sync replica HEAD: " +
                                           std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
      metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size != static_cast<off_t>(kReplicaBytes)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync replica HEAD is not one private fixed-size file"};
  }
  std::vector<std::uint8_t> bytes(kReplicaBytes);
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
                  "unable to read complete sync replica HEAD"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error, "unable to close sync replica HEAD"};
  }
  return bytes;
}

Status inspect_replica_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
      S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "sync replica directory is not private and owner-owned"};
  }
  return Status::success();
}

Status prepare_replica_directory(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) == 0)
    return inspect_replica_directory(path);
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect sync replica directory: " +
                      std::string(std::strerror(errno))};
  }
  std::error_code error;
  std::filesystem::create_directory(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync replica directory: " +
                      error.message()};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure sync replica directory: " +
                      error.message()};
  }
  return inspect_replica_directory(path);
}

AcceptedHead accepted_from_replica(const SignedHead &head,
                                   const Digest &record) {
  return AcceptedHead{head.namespace_id,  head.writer,   head.engine,
                      head.generation,    record,        head.parent,
                      head.artifact,      head.manifest, head.artifact_bytes,
                      head.manifest_bytes};
}

} // namespace

std::string_view
replica_head_import_decision_name(ReplicaHeadImportDecision decision) noexcept {
  switch (decision) {
  case ReplicaHeadImportDecision::imported:
    return "imported";
  case ReplicaHeadImportDecision::advanced:
    return "advanced";
  case ReplicaHeadImportDecision::duplicate:
    return "duplicate";
  }
  return "unknown";
}

Result<std::vector<std::uint8_t>>
encode_replica_head(const ReplicaHead &replica) {
  auto body = encode_replica_body(replica);
  if (!body.ok())
    return body.status();
  std::vector<std::uint8_t> output(body.value().begin(), body.value().end());
  output.insert(output.end(), replica.signature.begin(),
                replica.signature.end());
  return output;
}

Result<ReplicaHead> decode_replica_head(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kReplicaBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] != kFormat || !all_zero(bytes.subspan(9U, 7U))) {
    return Status{ErrorCode::protocol_error,
                  "sync replica HEAD header is invalid"};
  }
  ReplicaHead replica;
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kCustodianOffset),
              replica.custodian.size(), replica.custodian.begin());
  auto head = decode_signed_head(bytes.subspan(kHeadOffset, kSignedHeadBytes));
  if (!head.ok())
    return head.status();
  replica.head = std::move(head).value();
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kBodyBytes),
              replica.signature.size(), replica.signature.begin());
  auto canonical = encode_replica_head(replica);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync replica HEAD record is not canonical"};
  }
  return replica;
}

Status verify_replica_head(const NamespacePolicy &policy,
                           const ReplicaHead &replica,
                           const security::SigningPublicKey &expected_device,
                           const security::Sodium &sodium) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::content_v2 || all_zero(expected_device) ||
      replica.custodian != expected_device ||
      replica.head.writer == expected_device) {
    return Status{ErrorCode::protocol_error,
                  "sync replica identity or engine is invalid"};
  }
  const Status verified = verify_signed_head(policy, replica.head, sodium);
  if (!verified.ok())
    return verified;
  auto body = encode_replica_body(replica);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  return sodium.verify_detached(replica.signature, digest.value(),
                                replica.custodian);
}

ReplicaHeadStore::ReplicaHeadStore(std::filesystem::path root)
    : root_(std::move(root)) {}

std::filesystem::path
ReplicaHeadStore::path_for(std::string_view namespace_id) const {
  return root_ / "replica-heads" /
         (std::string(namespace_id) + ".replica-head");
}

Result<std::optional<SignedHead>>
ReplicaHeadStore::load(const NamespacePolicy &policy,
                       const security::SigningPublicKey &expected_device,
                       const security::Sodium &sodium) const {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync replica store does not match namespace policy"};
  }
  struct stat directory {};
  const auto replica_directory = root_ / "replica-heads";
  if (::lstat(replica_directory.c_str(), &directory) != 0) {
    if (errno == ENOENT)
      return std::optional<SignedHead>{};
    return Status{ErrorCode::io_error,
                  "unable to inspect sync replica directory: " +
                      std::string(std::strerror(errno))};
  }
  const Status safe_directory = inspect_replica_directory(replica_directory);
  if (!safe_directory.ok())
    return safe_directory;
  auto bytes = read_replica_file(path_for(policy.id));
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found)
      return std::optional<SignedHead>{};
    return bytes.status();
  }
  auto replica = decode_replica_head(bytes.value());
  if (!replica.ok())
    return replica.status();
  const Status verified =
      verify_replica_head(policy, replica.value(), expected_device, sodium);
  if (!verified.ok())
    return verified;
  return std::optional<SignedHead>{std::move(replica.value().head)};
}

Result<ReplicaHeadImportResult> ReplicaHeadStore::import_head(
    const NamespacePolicy &policy, const SignedHead &head,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return import_head(policy, head, identity, sodium, transaction.value());
}

Result<ReplicaHeadImportResult> ReplicaHeadStore::import_head(
    const NamespacePolicy &policy, const SignedHead &head,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync replica store does not match namespace policy"};
  }
  if (head.writer == identity.public_key()) {
    return Status{ErrorCode::invalid_argument,
                  "locally authored HEAD belongs in the publication store"};
  }
  auto candidate = verified_candidate_head(policy, head, sodium);
  if (!candidate.ok())
    return candidate.status();
  auto record = signed_head_record_digest(head, sodium);
  if (!record.ok())
    return record.status();
  auto current = load(policy, identity.public_key(), sodium);
  if (!current.ok())
    return current.status();

  ReplicaHeadImportDecision decision = ReplicaHeadImportDecision::imported;
  if (current.value().has_value()) {
    auto current_record = signed_head_record_digest(*current.value(), sodium);
    if (!current_record.ok())
      return current_record.status();
    if (current_record.value() == record.value()) {
      return ReplicaHeadImportResult{ReplicaHeadImportDecision::duplicate,
                                     record.value()};
    }
    if (current.value()->writer != head.writer) {
      return Status{ErrorCode::protocol_error,
                    "sync replica writer cannot change implicitly"};
    }
    const AcceptedHead current_head =
        accepted_from_replica(*current.value(), current_record.value());
    const HeadAcceptanceResult evaluated = evaluate_candidate_head(
        policy, candidate.value(), std::optional<AcceptedHead>{current_head});
    if (evaluated.decision != HeadAcceptanceDecision::accept_advance) {
      return Status{ErrorCode::protocol_error,
                    "sync replica HEAD is not an exact linked advance"};
    }
    decision = ReplicaHeadImportDecision::advanced;
  }

  ReplicaHead replica;
  replica.head = head;
  const Status signed_record = sign_replica(replica, identity, sodium);
  if (!signed_record.ok())
    return signed_record;
  const Status prepared = prepare_replica_directory(root_ / "replica-heads");
  if (!prepared.ok())
    return prepared;
  auto encoded = encode_replica_head(replica);
  if (!encoded.ok())
    return encoded.status();
  const Status stored =
      StateStore::write_atomic(path_for(policy.id), encoded.value());
  if (!stored.ok())
    return stored;
  return ReplicaHeadImportResult{decision, record.value()};
}

} // namespace iotox::sync
