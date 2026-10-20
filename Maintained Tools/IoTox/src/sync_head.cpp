#include "iotox/sync_head.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_guarded_witness.hpp"
#include "iotox/sync_rollback.hpp"

#include <algorithm>
#include <charconv>
#include <locale>
#include <sstream>
#include <string>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::string_view kHeader = "iotox-sync-accepted-head-v1";
constexpr std::size_t kMaximumAcceptedHeadBytes = 4096U;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-accepted-head-state-v1";
constexpr std::string_view kSignerPrefix = "signer=";
constexpr std::string_view kSignaturePrefix = "signature=";
constexpr std::size_t kAuthenticationSuffixBytes =
    kSignerPrefix.size() + security::kSigningPublicKeyBytes * 2U + 1U +
    kSignaturePrefix.size() + security::kSignatureBytes * 2U + 1U;

[[nodiscard]] bool all_zero(const Digest &digest) noexcept {
  return std::all_of(digest.begin(), digest.end(),
                     [](std::uint8_t value) { return value == 0U; });
}

[[nodiscard]] bool contains_principal(const std::vector<PrincipalId> &values,
                                      const PrincipalId &principal) {
  return std::binary_search(
      values.begin(), values.end(), principal,
      [](const PrincipalId &left, const PrincipalId &right) {
        return std::lexicographical_compare(left.begin(), left.end(),
                                            right.begin(), right.end());
      });
}

[[nodiscard]] bool engine_matches(Engine left, Engine right) noexcept {
  return left == right;
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

template <std::size_t Size>
[[nodiscard]] Result<std::array<std::uint8_t, Size>>
hex_array(std::string_view value, std::string_view label) {
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

Result<std::vector<std::uint8_t>> encode_authenticated_head(
    const AcceptedHead &head, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto body = encode_accepted_head(head);
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

Result<AcceptedHead> decode_authenticated_head(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  if (bytes.size() <= kAuthenticationSuffixBytes) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head authentication envelope is truncated"};
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
                  "accepted sync head authentication envelope is invalid"};
  }
  auto signer = hex_array<security::kSigningPublicKeyBytes>(
      suffix.substr(kSignerPrefix.size(), signer_bytes),
      "accepted sync head signer");
  if (!signer.ok())
    return signer.status();
  auto signature = hex_array<security::kSignatureBytes>(
      suffix.substr(signature_offset + kSignaturePrefix.size(),
                    security::kSignatureBytes * 2U),
      "accepted sync head signature");
  if (!signature.ok())
    return signature.status();
  if (signer.value() != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head signer is not the expected device"};
  }
  const auto body = bytes.first(body_bytes);
  auto digest = sodium.hash(kSignatureDomain, body);
  if (!digest.ok())
    return digest.status();
  const Status verified = sodium.verify_detached(
      signature.value(), digest.value(), signer.value());
  if (!verified.ok())
    return verified;
  return decode_accepted_head(body);
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
  if (bytes.empty() || bytes.size() > kMaximumAcceptedHeadBytes ||
      bytes.back() != static_cast<std::uint8_t>('\n')) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head size or final LF is invalid"};
  }
  const std::string_view text{reinterpret_cast<const char *>(bytes.data()),
                              bytes.size()};
  if (text.find('\0') != std::string_view::npos ||
      text.find('\r') != std::string_view::npos || text.ends_with("\n\n")) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head contains a forbidden byte or blank line"};
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
                  "accepted sync head field order or name is invalid"};
  }
  return lines[index++].substr(key.size());
}

[[nodiscard]] Status parse_engine(std::string_view text, Engine &engine) {
  if (text == "range-v1") {
    engine = Engine::range_v1;
    return Status::success();
  }
  if (text == "content-v2") {
    engine = Engine::content_v2;
    return Status::success();
  }
  if (text == "treepack-v1") {
    engine = Engine::treepack_v1;
    return Status::success();
  }
  return Status{ErrorCode::protocol_error,
                "accepted sync head engine is invalid"};
}

[[nodiscard]] AcceptedHead
accepted_from_candidate(const CandidateHead &candidate) {
  return AcceptedHead{candidate.namespace_id,   candidate.writer,
                      candidate.engine,         candidate.generation,
                      candidate.record,         candidate.parent,
                      candidate.artifact,       candidate.manifest,
                      candidate.artifact_bytes, candidate.manifest_bytes};
}

} // namespace

bool HeadAcceptanceResult::accepted() const noexcept {
  return decision == HeadAcceptanceDecision::accept_genesis ||
         decision == HeadAcceptanceDecision::accept_advance ||
         decision == HeadAcceptanceDecision::duplicate;
}

std::string_view
head_acceptance_decision_name(HeadAcceptanceDecision decision) noexcept {
  switch (decision) {
  case HeadAcceptanceDecision::accept_genesis:
    return "accept-genesis";
  case HeadAcceptanceDecision::accept_advance:
    return "accept-advance";
  case HeadAcceptanceDecision::duplicate:
    return "duplicate";
  case HeadAcceptanceDecision::stale:
    return "stale";
  case HeadAcceptanceDecision::fork:
    return "fork";
  case HeadAcceptanceDecision::wrong_namespace:
    return "wrong-namespace";
  case HeadAcceptanceDecision::unauthorized_writer:
    return "unauthorized-writer";
  case HeadAcceptanceDecision::parent_mismatch:
    return "parent-mismatch";
  case HeadAcceptanceDecision::generation_gap:
    return "generation-gap";
  case HeadAcceptanceDecision::engine_mismatch:
    return "engine-mismatch";
  case HeadAcceptanceDecision::resource_limit:
    return "resource-limit";
  }
  return "unknown";
}

Status validate_accepted_head(const NamespacePolicy &policy,
                              const AcceptedHead &head) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (head.namespace_id != policy.id) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head namespace does not match policy"};
  }
  if (!contains_principal(policy.writers, head.writer)) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head writer is not authorized"};
  }
  if (!engine_matches(policy.engine, head.engine)) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head engine does not match namespace policy"};
  }
  if (head.generation == 0U || all_zero(head.record) ||
      all_zero(head.artifact) || all_zero(head.manifest) ||
      head.artifact_bytes == 0U || head.manifest_bytes == 0U ||
      head.artifact_bytes > policy.quotas.maximum_artifact_bytes ||
      head.manifest_bytes > policy.quotas.maximum_manifest_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head identity or size is invalid"};
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_accepted_head(const AcceptedHead &head) {
  if (!valid_namespace_id(head.namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head namespace is invalid"};
  }
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << kHeader << '\n'
         << "namespace=" << head.namespace_id << '\n'
         << "writer=" << hex_encode(head.writer) << '\n'
         << "engine=" << engine_name(head.engine) << '\n'
         << "generation=" << head.generation << '\n'
         << "record=" << hex_encode(head.record) << '\n'
         << "parent=" << hex_encode(head.parent) << '\n'
         << "artifact=" << hex_encode(head.artifact) << '\n'
         << "manifest=" << hex_encode(head.manifest) << '\n'
         << "artifact-bytes=" << head.artifact_bytes << '\n'
         << "manifest-bytes=" << head.manifest_bytes << '\n';
  const std::string text = output.str();
  if (text.size() > kMaximumAcceptedHeadBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "accepted sync head exceeds its byte bound"};
  }
  return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<AcceptedHead> decode_accepted_head(std::span<const std::uint8_t> bytes) {
  auto lines = split_lines(bytes);
  if (!lines.ok())
    return lines.status();
  if (lines.value().size() != 11U || lines.value().front() != kHeader) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head header or field count is invalid"};
  }
  std::size_t index = 1U;
  AcceptedHead head;
  auto namespace_id = field(lines.value(), index, "namespace=");
  if (!namespace_id.ok())
    return namespace_id.status();
  head.namespace_id = std::string(namespace_id.value());
  auto writer = field(lines.value(), index, "writer=");
  if (!writer.ok())
    return writer.status();
  auto parsed_writer =
      hex_array<32U>(writer.value(), "accepted sync head writer");
  if (!parsed_writer.ok())
    return parsed_writer.status();
  head.writer = parsed_writer.value();
  auto engine = field(lines.value(), index, "engine=");
  if (!engine.ok())
    return engine.status();
  Status parsed_engine = parse_engine(engine.value(), head.engine);
  if (!parsed_engine.ok())
    return parsed_engine;
  auto generation = field(lines.value(), index, "generation=");
  if (!generation.ok())
    return generation.status();
  auto parsed_generation =
      parse_u64(generation.value(), "accepted sync head generation");
  if (!parsed_generation.ok())
    return parsed_generation.status();
  head.generation = parsed_generation.value();
  auto record = field(lines.value(), index, "record=");
  if (!record.ok())
    return record.status();
  auto parsed_record =
      hex_array<32U>(record.value(), "accepted sync head record");
  if (!parsed_record.ok())
    return parsed_record.status();
  head.record = parsed_record.value();
  auto parent = field(lines.value(), index, "parent=");
  if (!parent.ok())
    return parent.status();
  auto parsed_parent =
      hex_array<32U>(parent.value(), "accepted sync head parent");
  if (!parsed_parent.ok())
    return parsed_parent.status();
  head.parent = parsed_parent.value();
  auto artifact = field(lines.value(), index, "artifact=");
  if (!artifact.ok())
    return artifact.status();
  auto parsed_artifact =
      hex_array<32U>(artifact.value(), "accepted sync head artifact");
  if (!parsed_artifact.ok())
    return parsed_artifact.status();
  head.artifact = parsed_artifact.value();
  auto manifest = field(lines.value(), index, "manifest=");
  if (!manifest.ok())
    return manifest.status();
  auto parsed_manifest =
      hex_array<32U>(manifest.value(), "accepted sync head manifest");
  if (!parsed_manifest.ok())
    return parsed_manifest.status();
  head.manifest = parsed_manifest.value();
  auto artifact_bytes = field(lines.value(), index, "artifact-bytes=");
  if (!artifact_bytes.ok())
    return artifact_bytes.status();
  auto parsed_artifact_bytes =
      parse_u64(artifact_bytes.value(), "accepted sync head artifact bytes");
  if (!parsed_artifact_bytes.ok())
    return parsed_artifact_bytes.status();
  head.artifact_bytes = parsed_artifact_bytes.value();
  auto manifest_bytes = field(lines.value(), index, "manifest-bytes=");
  if (!manifest_bytes.ok())
    return manifest_bytes.status();
  auto parsed_manifest_bytes =
      parse_u64(manifest_bytes.value(), "accepted sync head manifest bytes");
  if (!parsed_manifest_bytes.ok())
    return parsed_manifest_bytes.status();
  head.manifest_bytes = parsed_manifest_bytes.value();

  auto canonical = encode_accepted_head(head);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head record is not canonical"};
  }
  return head;
}

HeadAcceptanceResult
evaluate_candidate_head(const NamespacePolicy &policy,
                        const CandidateHead &candidate,
                        const std::optional<AcceptedHead> &current,
                        const HeadAcceptancePolicy &acceptance) {
  HeadAcceptanceResult result;
  AcceptedHead head = accepted_from_candidate(candidate);
  const Status valid = validate_accepted_head(policy, head);
  if (!valid.ok()) {
    if (!contains_principal(policy.writers, candidate.writer)) {
      result.decision = HeadAcceptanceDecision::unauthorized_writer;
    } else if (candidate.namespace_id != policy.id) {
      result.decision = HeadAcceptanceDecision::wrong_namespace;
    } else if (!engine_matches(policy.engine, candidate.engine)) {
      result.decision = HeadAcceptanceDecision::engine_mismatch;
    } else {
      result.decision = HeadAcceptanceDecision::resource_limit;
    }
    return result;
  }
  if (!current.has_value()) {
    if (!all_zero(candidate.parent)) {
      result.decision = HeadAcceptanceDecision::parent_mismatch;
      return result;
    }
    result.decision = HeadAcceptanceDecision::accept_genesis;
    return result;
  }
  if (current->namespace_id != policy.id) {
    result.decision = HeadAcceptanceDecision::wrong_namespace;
    return result;
  }
  if (candidate.record == current->record) {
    result.decision = HeadAcceptanceDecision::duplicate;
    return result;
  }
  if (candidate.generation < current->generation) {
    result.decision = HeadAcceptanceDecision::stale;
    return result;
  }
  if (candidate.generation == current->generation) {
    result.decision = HeadAcceptanceDecision::fork;
    return result;
  }
  result.generation_delta = candidate.generation - current->generation;
  if (result.generation_delta > acceptance.maximum_generation_jump) {
    result.decision = HeadAcceptanceDecision::generation_gap;
    return result;
  }
  if (candidate.parent != current->record) {
    result.decision = HeadAcceptanceDecision::parent_mismatch;
    return result;
  }
  result.decision = HeadAcceptanceDecision::accept_advance;
  return result;
}

AcceptedHeadStore::AcceptedHeadStore(
    std::filesystem::path root,
    std::shared_ptr<SyncGuardedStateWitness> witness)
    : root_(std::move(root)), witness_(std::move(witness)) {}

std::filesystem::path
AcceptedHeadStore::path_for(std::string_view namespace_id) const {
  return root_ / "accepted-heads" /
         (std::string(namespace_id) + ".accepted-head");
}

Result<std::optional<AcceptedHead>>
AcceptedHeadStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head expected device is zero"};
  }
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head store does not match namespace policy"};
  }
  auto bytes = StateStore::read(path_for(policy.id));
  if (!bytes.ok()) {
    if (bytes.status().code() == ErrorCode::not_found) {
      return std::optional<AcceptedHead>{};
    }
    return bytes.status();
  }
  auto decoded =
      decode_authenticated_head(bytes.value(), expected_device, sodium);
  if (!decoded.ok())
    return decoded.status();
  if (decoded.value().namespace_id != policy.id) {
    return Status{ErrorCode::protocol_error,
                  "accepted sync head path and record namespace differ"};
  }
  return std::optional<AcceptedHead>{std::move(decoded.value())};
}

Result<HeadAcceptanceResult>
AcceptedHeadStore::accept(const NamespacePolicy &policy,
                          const CandidateHead &candidate,
                          const security::DeviceIdentity &identity,
                          const security::Sodium &sodium,
                          const HeadAcceptancePolicy &acceptance) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head store does not match namespace policy"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return accept(policy, candidate, identity, sodium, acceptance,
                transaction.value());
}

Result<HeadAcceptanceResult>
AcceptedHeadStore::accept(const NamespacePolicy &policy,
                          const CandidateHead &candidate,
                          const security::DeviceIdentity &identity,
                          const security::Sodium &sodium,
                          const HeadAcceptancePolicy &acceptance,
                          const SyncNamespaceTransaction &transaction) {
  if (root_.lexically_normal().string() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "accepted sync head store does not match namespace policy"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness_) {
    const Status verified = witness_->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }
  auto current = load(policy, identity.public_key(), sodium);
  if (!current.ok())
    return current.status();
  if (current.value().has_value()) {
    const Status current_valid =
        validate_accepted_head(policy, *current.value());
    if (!current_valid.ok())
      return current_valid;
  }
  HeadAcceptanceResult result =
      evaluate_candidate_head(policy, candidate, current.value(), acceptance);
  if (result.decision == HeadAcceptanceDecision::duplicate) {
    const Status reconciled = witness_
        ? witness_->reconcile(policy, transaction)
        : reconcile_sync_rollback_roots(
              policy, identity, sodium, transaction);
    if (!reconciled.ok())
      return reconciled;
    return result;
  }
  if (!result.accepted()) {
    return result;
  }
  AcceptedHead accepted = accepted_from_candidate(candidate);
  auto encoded = encode_authenticated_head(accepted, identity, sodium);
  if (!encoded.ok())
    return encoded.status();
  auto roots = load_sync_rollback_roots(policy, identity.public_key(), sodium,
                                        transaction);
  if (!roots.ok())
    return roots.status();
  SyncReachabilityRoots next = roots.value();
  next.accepted = accepted;
  const Status stored = guarded_sync_root_transition(
      policy, roots.value(), next, identity, sodium, transaction, [&]() {
        return StateStore::write_atomic(path_for(policy.id), encoded.value());
      }, witness_.get());
  if (!stored.ok())
    return stored;
  return result;
}

} // namespace iotox::sync
