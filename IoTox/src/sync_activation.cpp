#include "iotox/sync_activation.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_guarded_witness.hpp"
#include "iotox/sync_rollback.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <locale>
#include <sstream>
#include <string>
#include <system_error>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::string_view kHeader = "iotox-sync-activated-revision-v1";
constexpr std::size_t kMaximumRecordBytes = 2048U;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-activated-revision-state-v1";
constexpr std::string_view kSignerPrefix = "signer=";
constexpr std::string_view kSignaturePrefix = "signature=";
constexpr std::size_t kAuthenticationSuffixBytes =
    kSignerPrefix.size() + security::kSigningPublicKeyBytes * 2U + 1U +
    kSignaturePrefix.size() + security::kSignatureBytes * 2U + 1U;

[[nodiscard]] bool all_zero(const Digest &digest) noexcept {
  return std::all_of(digest.begin(), digest.end(),
                     [](std::uint8_t value) { return value == 0U; });
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

[[nodiscard]] int hex_nibble(char character) noexcept {
  if (character >= '0' && character <= '9')
    return character - '0';
  if (character >= 'a' && character <= 'f')
    return 10 + character - 'a';
  return -1;
}

[[nodiscard]] Result<Digest> parse_digest(std::string_view value,
                                          std::string_view label) {
  if (value.size() != Digest{}.size() * 2U) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " has invalid hex length"};
  }
  Digest output{};
  for (std::size_t index = 0U; index < output.size(); ++index) {
    const int high = hex_nibble(value[index * 2U]);
    const int low = hex_nibble(value[index * 2U + 1U]);
    if (high < 0 || low < 0) {
      return Status{ErrorCode::protocol_error,
                    std::string(label) + " is not lowercase hex"};
    }
    output[index] = static_cast<std::uint8_t>((high << 4U) | low);
  }
  return output;
}

template <std::size_t Size>
[[nodiscard]] Result<std::array<std::uint8_t, Size>>
parse_array(std::string_view value, std::string_view label) {
  if (value.size() != Size * 2U) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " has invalid hex length"};
  }
  std::array<std::uint8_t, Size> output{};
  for (std::size_t index = 0U; index < Size; ++index) {
    const int high = hex_nibble(value[index * 2U]);
    const int low = hex_nibble(value[index * 2U + 1U]);
    if (high < 0 || low < 0) {
      return Status{ErrorCode::protocol_error,
                    std::string(label) + " is not lowercase hex"};
    }
    output[index] = static_cast<std::uint8_t>((high << 4U) | low);
  }
  return output;
}

[[nodiscard]] Result<std::uint64_t> parse_u64(std::string_view value,
                                              std::string_view label) {
  if (value.empty() || value.front() == '+' || value.front() == '-') {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not an unsigned integer"};
  }
  std::uint64_t parsed = 0U;
  const auto result =
      std::from_chars(value.data(), value.data() + value.size(), parsed);
  if (result.ec != std::errc{} || result.ptr != value.data() + value.size()) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not an unsigned integer"};
  }
  return parsed;
}

[[nodiscard]] Result<std::vector<std::string_view>>
split_lines(std::span<const std::uint8_t> bytes) {
  if (bytes.empty() || bytes.size() > kMaximumRecordBytes ||
      bytes.back() != static_cast<std::uint8_t>('\n')) {
    return Status{ErrorCode::protocol_error,
                  "activated revision size or final LF is invalid"};
  }
  const std::string_view text{reinterpret_cast<const char *>(bytes.data()),
                              bytes.size()};
  if (text.find('\0') != std::string_view::npos ||
      text.find('\r') != std::string_view::npos || text.ends_with("\n\n")) {
    return Status{ErrorCode::protocol_error,
                  "activated revision contains a forbidden byte or blank line"};
  }
  std::vector<std::string_view> lines;
  std::size_t offset = 0U;
  while (offset < text.size()) {
    const std::size_t end = text.find('\n', offset);
    if (end == std::string_view::npos)
      break;
    lines.push_back(text.substr(offset, end - offset));
    offset = end + 1U;
  }
  return lines;
}

[[nodiscard]] Result<std::string_view>
field(const std::vector<std::string_view> &lines, std::size_t &index,
      std::string_view key) {
  if (index >= lines.size() || !lines[index].starts_with(key)) {
    return Status{ErrorCode::protocol_error,
                  "activated revision field order or name is invalid"};
  }
  return lines[index++].substr(key.size());
}

[[nodiscard]] Status validate_revision(const ActivatedRevision &revision) {
  if (!valid_namespace_id(revision.namespace_id) || revision.generation == 0U ||
      all_zero(revision.record) || all_zero(revision.artifact) ||
      revision.artifact_bytes == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "activated revision identity or size is invalid"};
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>> encode_authenticated_revision(
    const ActivatedRevision &revision,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto body = encode_activated_revision(revision);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  const std::string suffix =
      std::string(kSignerPrefix) + hex_encode(identity.public_key()) + '\n' +
      std::string(kSignaturePrefix) + hex_encode(signature.value()) + '\n';
  body.value().insert(body.value().end(), suffix.begin(), suffix.end());
  return body;
}

Result<ActivatedRevision> decode_authenticated_revision(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  if (bytes.size() <= kAuthenticationSuffixBytes) {
    return Status{ErrorCode::protocol_error,
                  "activated revision authentication envelope is truncated"};
  }
  const std::size_t body_bytes = bytes.size() - kAuthenticationSuffixBytes;
  const std::string_view suffix(
      reinterpret_cast<const char *>(bytes.data() + body_bytes),
      kAuthenticationSuffixBytes);
  const std::size_t signer_bytes = security::kSigningPublicKeyBytes * 2U;
  const std::size_t signature_offset =
      kSignerPrefix.size() + signer_bytes + 1U;
  if (!suffix.starts_with(kSignerPrefix) ||
      suffix[kSignerPrefix.size() + signer_bytes] != '\n' ||
      suffix.substr(signature_offset, kSignaturePrefix.size()) !=
          kSignaturePrefix ||
      suffix.back() != '\n') {
    return Status{ErrorCode::protocol_error,
                  "activated revision authentication envelope is invalid"};
  }
  auto signer = parse_array<security::kSigningPublicKeyBytes>(
      suffix.substr(kSignerPrefix.size(), signer_bytes),
      "activated revision signer");
  if (!signer.ok())
    return signer.status();
  auto signature = parse_array<security::kSignatureBytes>(
      suffix.substr(signature_offset + kSignaturePrefix.size(),
                    security::kSignatureBytes * 2U),
      "activated revision signature");
  if (!signature.ok())
    return signature.status();
  if (signer.value() != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "activated revision signer is not the expected device"};
  }
  const auto body = bytes.first(body_bytes);
  auto digest = sodium.hash(kSignatureDomain, body);
  if (!digest.ok())
    return digest.status();
  const Status verified = sodium.verify_detached(
      signature.value(), digest.value(), signer.value());
  if (!verified.ok())
    return verified;
  return decode_activated_revision(body);
}

[[nodiscard]] std::filesystem::path
object_path(const std::filesystem::path &root, const Digest &artifact) {
  return root / "objects" / (hex_encode(artifact) + ".artifact");
}

[[nodiscard]] std::filesystem::path
manifest_path(const std::filesystem::path &root, const Digest &manifest) {
  return root / "objects" / (hex_encode(manifest) + ".manifest");
}

} // namespace

bool SyncActivationResult::active() const noexcept {
  return decision == ActivationDecision::activated ||
         decision == ActivationDecision::duplicate;
}

std::string_view
activation_decision_name(ActivationDecision decision) noexcept {
  switch (decision) {
  case ActivationDecision::activated:
    return "activated";
  case ActivationDecision::duplicate:
    return "duplicate";
  case ActivationDecision::disabled:
    return "disabled";
  case ActivationDecision::no_accepted_head:
    return "no-accepted-head";
  case ActivationDecision::accepted_head_mismatch:
    return "accepted-head-mismatch";
  case ActivationDecision::stale:
    return "stale";
  case ActivationDecision::fork:
    return "fork";
  case ActivationDecision::object_missing:
    return "object-missing";
  case ActivationDecision::object_size_mismatch:
    return "object-size-mismatch";
  case ActivationDecision::object_digest_mismatch:
    return "object-digest-mismatch";
  case ActivationDecision::manifest_missing:
    return "manifest-missing";
  case ActivationDecision::manifest_size_mismatch:
    return "manifest-size-mismatch";
  case ActivationDecision::manifest_digest_mismatch:
    return "manifest-digest-mismatch";
  }
  return "unknown";
}

Result<std::vector<std::uint8_t>>
encode_activated_revision(const ActivatedRevision &revision) {
  const Status valid = validate_revision(revision);
  if (!valid.ok())
    return valid;
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << kHeader << '\n'
         << "namespace=" << revision.namespace_id << '\n'
         << "generation=" << revision.generation << '\n'
         << "record=" << hex_encode(revision.record) << '\n'
         << "artifact=" << hex_encode(revision.artifact) << '\n'
         << "artifact-bytes=" << revision.artifact_bytes << '\n';
  const std::string text = output.str();
  if (text.size() > kMaximumRecordBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "activated revision exceeds its byte bound"};
  }
  return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<ActivatedRevision>
decode_activated_revision(std::span<const std::uint8_t> bytes) {
  auto lines = split_lines(bytes);
  if (!lines.ok())
    return lines.status();
  if (lines.value().size() != 6U || lines.value().front() != kHeader) {
    return Status{ErrorCode::protocol_error,
                  "activated revision header or field count is invalid"};
  }
  std::size_t index = 1U;
  ActivatedRevision revision;
  auto namespace_id = field(lines.value(), index, "namespace=");
  if (!namespace_id.ok())
    return namespace_id.status();
  revision.namespace_id = std::string(namespace_id.value());
  auto generation = field(lines.value(), index, "generation=");
  if (!generation.ok())
    return generation.status();
  auto parsed_generation =
      parse_u64(generation.value(), "activation generation");
  if (!parsed_generation.ok())
    return parsed_generation.status();
  revision.generation = parsed_generation.value();
  auto record = field(lines.value(), index, "record=");
  if (!record.ok())
    return record.status();
  auto parsed_record = parse_digest(record.value(), "activation record");
  if (!parsed_record.ok())
    return parsed_record.status();
  revision.record = parsed_record.value();
  auto artifact = field(lines.value(), index, "artifact=");
  if (!artifact.ok())
    return artifact.status();
  auto parsed_artifact = parse_digest(artifact.value(), "activation artifact");
  if (!parsed_artifact.ok())
    return parsed_artifact.status();
  revision.artifact = parsed_artifact.value();
  auto artifact_bytes = field(lines.value(), index, "artifact-bytes=");
  if (!artifact_bytes.ok())
    return artifact_bytes.status();
  auto parsed_artifact_bytes =
      parse_u64(artifact_bytes.value(), "activation artifact bytes");
  if (!parsed_artifact_bytes.ok())
    return parsed_artifact_bytes.status();
  revision.artifact_bytes = parsed_artifact_bytes.value();

  auto canonical = encode_activated_revision(revision);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "activated revision record is not canonical"};
  }
  return revision;
}

ActivatedRevisionStore::ActivatedRevisionStore(
    std::filesystem::path root,
    std::shared_ptr<SyncGuardedStateWitness> witness)
    : root_(std::move(root)), witness_(std::move(witness)) {}

std::filesystem::path
ActivatedRevisionStore::path_for(std::string_view namespace_id) const {
  return root_ / "activated-revisions" /
         (std::string(namespace_id) + ".activated-revision");
}

Result<std::optional<ActivatedRevision>>
ActivatedRevisionStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "activated revision expected device is zero"};
  }
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "sync activation store does not match namespace policy"};
  }
  auto bytes = StateStore::read(path_for(policy.id));
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found)
      return std::optional<ActivatedRevision>{};
    return bytes.status();
  }
  auto decoded =
      decode_authenticated_revision(bytes.value(), expected_device, sodium);
  if (!decoded.ok())
    return decoded.status();
  if (decoded.value().namespace_id != policy.id) {
    return Status{ErrorCode::protocol_error,
                  "activated revision path and record namespace differ"};
  }
  if (decoded.value().artifact_bytes >
      policy.quotas.maximum_artifact_bytes) {
    return Status{ErrorCode::protocol_error,
                  "activated revision exceeds namespace policy"};
  }
  return std::optional<ActivatedRevision>{std::move(decoded.value())};
}

Status ActivatedRevisionStore::store(const NamespacePolicy &policy,
                                     const ActivatedRevision &revision,
                                     const security::DeviceIdentity &identity,
                                     const security::Sodium &sodium) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root ||
      revision.namespace_id != policy.id) {
    return Status{ErrorCode::invalid_argument,
                  "sync activation store does not match namespace policy"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return store(policy, revision, identity, sodium, transaction.value());
}

Status ActivatedRevisionStore::store(
    const NamespacePolicy &policy, const ActivatedRevision &revision,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  if (root_.lexically_normal().string() != policy.root ||
      revision.namespace_id != policy.id ||
      revision.artifact_bytes > policy.quotas.maximum_artifact_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "sync activation store does not match namespace policy"};
  }
  auto encoded = encode_authenticated_revision(revision, identity, sodium);
  if (!encoded.ok())
    return encoded.status();
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  SyncReachabilityRoots next = roots.value();
  next.activated = revision;
  return guarded_sync_root_transition(
      policy, roots.value(), next, identity, sodium, transaction, [&]() {
        return StateStore::write_atomic(path_for(revision.namespace_id),
                                        encoded.value());
      }, witness_.get());
}

Result<SyncActivationResult>
activate_staged_artifact(const SyncActivationRequest &request,
                         const security::DeviceIdentity &identity,
                         const security::Sodium &sodium,
                         const SyncActivationSeams &seams) {
  const Status valid_policy = validate_namespace_policy(request.policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "sync activation requires a file hasher"};
  }

  SyncActivationResult result;
  if (request.policy.activation != ActivationMode::manual) {
    result.decision = ActivationDecision::disabled;
    return result;
  }

  auto transaction = SyncNamespaceTransaction::acquire(request.policy);
  if (!transaction.ok())
    return transaction.status();
  if (seams.guarded_state_witness) {
    const Status verified = seams.guarded_state_witness->verify_read(
        request.policy, transaction.value());
    if (!verified.ok()) return verified;
  }

  const std::filesystem::path root(request.policy.root);
  AcceptedHeadStore accepted_store(root);
  auto accepted = accepted_store.load(request.policy, identity.public_key(),
                                      sodium);
  if (!accepted.ok())
    return accepted.status();
  if (!accepted.value().has_value()) {
    result.decision = ActivationDecision::no_accepted_head;
    return result;
  }
  const Status valid_head =
      validate_accepted_head(request.policy, *accepted.value());
  if (!valid_head.ok())
    return valid_head;
  if (accepted.value()->record != request.expected_record) {
    result.decision = ActivationDecision::accepted_head_mismatch;
    return result;
  }

  ActivatedRevision revision{
      accepted.value()->namespace_id, accepted.value()->generation,
      accepted.value()->record, accepted.value()->artifact,
      accepted.value()->artifact_bytes};
  result.revision = revision;
  if (seams.resolve_artifact_path) {
    auto resolved =
        seams.resolve_artifact_path(request.policy, *accepted.value());
    if (!resolved.ok())
      return resolved.status();
    result.object_path = std::move(resolved).value();
  } else {
    result.object_path = object_path(root, revision.artifact);
  }

  std::filesystem::path manifest;
  if (seams.resolve_manifest_path) {
    auto resolved =
        seams.resolve_manifest_path(request.policy, *accepted.value());
    if (!resolved.ok())
      return resolved.status();
    manifest = std::move(resolved).value();
  } else {
    manifest = manifest_path(root, accepted.value()->manifest);
  }

  ActivatedRevisionStore activation_store(
      root, seams.guarded_state_witness);
  auto current =
      activation_store.load(request.policy, identity.public_key(), sodium);
  if (!current.ok())
    return current.status();
  if (current.value().has_value()) {
    if (*current.value() == revision) {
      const Status reconciled = seams.guarded_state_witness
          ? seams.guarded_state_witness->reconcile(
                request.policy, transaction.value())
          : reconcile_sync_rollback_roots(
                request.policy, identity, sodium, transaction.value());
      if (!reconciled.ok())
        return reconciled;
      if (seams.project_revision) {
        const Status projected = seams.project_revision(
            request.policy, revision, result.object_path,
            transaction.value());
        if (!projected.ok())
          return projected;
      }
      result.decision = ActivationDecision::duplicate;
      return result;
    }
    if (revision.generation < current.value()->generation) {
      result.decision = ActivationDecision::stale;
      return result;
    }
    if (revision.generation == current.value()->generation) {
      result.decision = ActivationDecision::fork;
      return result;
    }
  }

  std::error_code error;
  const auto status =
      std::filesystem::symlink_status(result.object_path, error);
  if (error || !std::filesystem::is_regular_file(status)) {
    result.decision = ActivationDecision::object_missing;
    return result;
  }
  const std::uint64_t bytes =
      std::filesystem::file_size(result.object_path, error);
  if (error || bytes != revision.artifact_bytes) {
    result.decision = ActivationDecision::object_size_mismatch;
    return result;
  }
  auto digest = seams.hash_file(result.object_path);
  if (!digest.ok())
    return digest.status();
  if (digest.value() != revision.artifact) {
    result.decision = ActivationDecision::object_digest_mismatch;
    return result;
  }

  const auto manifest_status = std::filesystem::symlink_status(manifest, error);
  if (error || !std::filesystem::is_regular_file(manifest_status)) {
    result.decision = ActivationDecision::manifest_missing;
    return result;
  }
  const std::uint64_t manifest_bytes = std::filesystem::file_size(manifest, error);
  if (error || manifest_bytes != accepted.value()->manifest_bytes) {
    result.decision = ActivationDecision::manifest_size_mismatch;
    return result;
  }
  auto manifest_digest = seams.hash_file(manifest);
  if (!manifest_digest.ok()) return manifest_digest.status();
  if (manifest_digest.value() != accepted.value()->manifest) {
    result.decision = ActivationDecision::manifest_digest_mismatch;
    return result;
  }
  if (seams.validate_revision) {
    const Status semantic = seams.validate_revision(
        request.policy, *accepted.value(), result.object_path, manifest);
    if (!semantic.ok()) return semantic;
  }

  const Status stored = activation_store.store(
      request.policy, revision, identity, sodium, transaction.value());
  if (!stored.ok())
    return stored;
  if (seams.project_revision) {
    const Status projected = seams.project_revision(
        request.policy, revision, result.object_path, transaction.value());
    if (!projected.ok())
      return projected;
  }
  result.decision = ActivationDecision::activated;
  return result;
}

} // namespace iotox::sync
