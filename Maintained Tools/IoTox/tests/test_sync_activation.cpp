#include "test_harness.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_activation.hpp"
#include "iotox/sync_head.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unistd.h>
#include <vector>

namespace {

using iotox::Result;
using iotox::Status;
using iotox::sync::AcceptedHeadStore;
using iotox::sync::ActivatedRevision;
using iotox::sync::ActivatedRevisionStore;
using iotox::sync::ActivationDecision;
using iotox::sync::ActivationMode;
using iotox::sync::CandidateHead;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncActivationRequest;
using iotox::sync::SyncActivationSeams;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-activation-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr)
      throw std::runtime_error("mkdtemp failed");
    path_ = created;
  }

  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }

  TempDirectory(const TempDirectory &) = delete;
  TempDirectory &operator=(const TempDirectory &) = delete;

  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

private:
  std::filesystem::path path_;
};

PrincipalId principal(std::uint8_t value) {
  PrincipalId result{};
  result[0U] = value;
  return result;
}

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  return result;
}

Sodium sodium() {
  auto loaded = Sodium::load();
  if (!loaded.ok())
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded.value());
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
  auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded.ok())
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded.value());
}

std::vector<std::uint8_t> bytes(std::string_view text) {
  return {reinterpret_cast<const std::uint8_t *>(text.data()),
          reinterpret_cast<const std::uint8_t *>(text.data()) + text.size()};
}

Digest toy_digest(std::span<const std::uint8_t> input) {
  Digest result{};
  std::uint8_t value = 0U;
  for (const std::uint8_t byte : input)
    value = static_cast<std::uint8_t>((value * 33U) ^ byte);
  result[0U] = value;
  result[1U] = static_cast<std::uint8_t>(input.size());
  return result;
}

std::string hex_encode(const Digest &value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(value.size() * 2U);
  for (const std::uint8_t byte : value) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

void write_file(const std::filesystem::path &path, std::string_view text) {
  std::filesystem::create_directories(path.parent_path());
  std::ofstream output(path, std::ios::binary);
  output << text;
  if (!output)
    throw std::runtime_error("unable to write fixture: " + path.string());
}

Result<Digest> hash_file(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    return Status{iotox::ErrorCode::io_error,
                  "unable to read hash fixture: " + path.string()};
  }
  std::vector<std::uint8_t> contents((std::istreambuf_iterator<char>(input)),
                                     std::istreambuf_iterator<char>());
  return toy_digest(contents);
}

SyncActivationSeams seams() {
  SyncActivationSeams result;
  result.hash_file = hash_file;
  return result;
}

NamespacePolicy policy(const std::filesystem::path &root) {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.activation = ActivationMode::manual;
  result.writers = {principal(1U)};
  result.subscribers = {principal(2U)};
  result.quotas.maximum_artifact_bytes = 128U;
  result.quotas.maximum_manifest_bytes = 32U;
  return result;
}

CandidateHead candidate(const NamespacePolicy &namespace_policy,
                        std::uint64_t generation, std::uint8_t record,
                        Digest parent, std::string_view artifact) {
  CandidateHead result;
  result.namespace_id = namespace_policy.id;
  result.writer = principal(1U);
  result.engine = namespace_policy.engine;
  result.generation = generation;
  result.record = digest(record);
  result.parent = parent;
  result.artifact = toy_digest(bytes(artifact));
  result.manifest = toy_digest(bytes("manifest"));
  result.artifact_bytes = artifact.size();
  result.manifest_bytes = 8U;
  return result;
}

std::filesystem::path object_path(const NamespacePolicy &namespace_policy,
                                  const CandidateHead &head) {
  return std::filesystem::path(namespace_policy.root) / "objects" /
         (hex_encode(head.artifact) + ".artifact");
}

std::filesystem::path manifest_path(const NamespacePolicy &namespace_policy,
                                    const CandidateHead &head) {
  return std::filesystem::path(namespace_policy.root) / "objects" /
         (hex_encode(head.manifest) + ".manifest");
}

void accept(const NamespacePolicy &namespace_policy,
            const CandidateHead &head, const DeviceIdentity &device,
            const Sodium &crypto) {
  AcceptedHeadStore store(namespace_policy.root);
  auto accepted = store.accept(namespace_policy, head, device, crypto);
  if (!accepted.ok() || !accepted.value().accepted())
    throw std::runtime_error("unable to accept fixture HEAD");
  write_file(manifest_path(namespace_policy, head), "manifest");
}

} // namespace

IOTOX_TEST("sync activated revision record is canonical and strict") {
  ActivatedRevision revision{"field-notes", 7U, digest(7U), digest(8U), 1024U};
  auto encoded = iotox::sync::encode_activated_revision(revision);
  IOTOX_CHECK(encoded.ok());
  auto decoded = iotox::sync::decode_activated_revision(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == revision);

  std::vector<std::uint8_t> changed = encoded.value();
  changed.insert(changed.end() - 1U,
                 {'u', 'n', 'k', 'n', 'o', 'w', 'n', '=', '1', '\n'});
  IOTOX_CHECK(!iotox::sync::decode_activated_revision(changed).ok());
  changed = encoded.value();
  changed.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_activated_revision(changed).ok());
}

IOTOX_TEST("sync activation state authenticates the stable device") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity foreign =
      identity(temporary.path() / "foreign.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  ActivatedRevision revision{namespace_policy.id, 1U, digest(1U), digest(2U),
                             5U};
  ActivatedRevisionStore store(namespace_policy.root);
  IOTOX_CHECK(
      store.store(namespace_policy, revision, device, crypto).ok());
  auto loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == revision);
  IOTOX_CHECK(
      !store.load(namespace_policy, foreign.public_key(), crypto).ok());

  const auto state_path = std::filesystem::path(namespace_policy.root) /
                          "activated-revisions" /
                          "field-notes.activated-revision";
  auto persisted = iotox::StateStore::read(state_path);
  IOTOX_CHECK(persisted.ok());
  persisted.value()[40U] ^= 0x01U;
  IOTOX_CHECK(
      iotox::StateStore::write_atomic(state_path, persisted.value()).ok());
  IOTOX_CHECK(
      !store.load(namespace_policy, device.public_key(), crypto).ok());

  auto legacy = iotox::sync::encode_activated_revision(revision);
  IOTOX_CHECK(legacy.ok());
  IOTOX_CHECK(iotox::StateStore::write_atomic(state_path, legacy.value()).ok());
  IOTOX_CHECK(
      !store.load(namespace_policy, device.public_key(), crypto).ok());
}

IOTOX_TEST("sync activation is default denied before accepted head lookup") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  namespace_policy.activation = ActivationMode::disabled;
  SyncActivationRequest request{namespace_policy, digest(1U)};

  auto activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::disabled);
  IOTOX_CHECK(!activated.value().active());
  IOTOX_CHECK(!std::filesystem::exists(
      std::filesystem::path(namespace_policy.root) / "activated-revisions"));
}

IOTOX_TEST("sync activation requires an exact accepted head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");

  auto activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, digest(1U)}, device, crypto,
      seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::no_accepted_head);

  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, digest(9U)}, device, crypto,
      seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::accepted_head_mismatch);
}

IOTOX_TEST("sync activation verifies object and commits durable pointer") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  write_file(object_path(namespace_policy, head), "alpha");

  const SyncActivationRequest request{namespace_policy, head.record};
  auto activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::activated);
  IOTOX_CHECK(activated.value().active());
  IOTOX_CHECK(activated.value().revision.has_value());
  IOTOX_CHECK(activated.value().revision->record == head.record);

  ActivatedRevisionStore store(namespace_policy.root);
  auto loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == activated.value().revision);

  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::duplicate);
  IOTOX_CHECK(activated.value().active());

  const CandidateHead second =
      candidate(namespace_policy, 2U, 2U, head.record, "bravo");
  accept(namespace_policy, second, device, crypto);
  write_file(object_path(namespace_policy, second), "bravo");
  activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, second.record}, device, crypto,
      seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::activated);
  loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->generation == 2U);
  IOTOX_CHECK(loaded.value()->record == second.record);
}

IOTOX_TEST("sync activation commits signed state before retryable projection") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  write_file(object_path(namespace_policy, head), "alpha");
  const SyncActivationRequest request{namespace_policy, head.record};
  ActivatedRevisionStore store(namespace_policy.root);

  bool observed_committed_state = false;
  SyncActivationSeams interrupted = seams();
  interrupted.project_revision =
      [&](const NamespacePolicy &, const ActivatedRevision &revision,
          const std::filesystem::path &,
          const iotox::sync::SyncNamespaceTransaction &) {
        auto loaded = store.load(namespace_policy, device.public_key(), crypto);
        observed_committed_state = loaded.ok() && loaded.value().has_value() &&
                                   *loaded.value() == revision;
        return Status{iotox::ErrorCode::io_error,
                      "injected projection interruption"};
      };
  auto activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, interrupted);
  IOTOX_CHECK(!activated.ok());
  IOTOX_CHECK(observed_committed_state);

  bool reconciled = false;
  SyncActivationSeams retry = seams();
  retry.project_revision =
      [&](const NamespacePolicy &, const ActivatedRevision &,
          const std::filesystem::path &,
          const iotox::sync::SyncNamespaceTransaction &) {
        reconciled = true;
        return Status::success();
      };
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, retry);
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::duplicate);
  IOTOX_CHECK(reconciled);
}

IOTOX_TEST("sync activation refuses missing short and corrupt objects") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  const SyncActivationRequest request{namespace_policy, head.record};

  auto activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::object_missing);

  write_file(object_path(namespace_policy, head), "a");
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::object_size_mismatch);

  write_file(object_path(namespace_policy, head), "omega");
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::object_digest_mismatch);

  ActivatedRevisionStore store(namespace_policy.root);
  auto loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(!loaded.value().has_value());
}

IOTOX_TEST("sync activation verifies the exact manifest and semantic pair") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  write_file(object_path(namespace_policy, head), "alpha");
  const SyncActivationRequest request{namespace_policy, head.record};

  std::filesystem::remove(manifest_path(namespace_policy, head));
  auto activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::manifest_missing);

  write_file(manifest_path(namespace_policy, head), "m");
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::manifest_size_mismatch);

  write_file(manifest_path(namespace_policy, head), "mismatch");
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision ==
              ActivationDecision::manifest_digest_mismatch);

  write_file(manifest_path(namespace_policy, head), "manifest");
  SyncActivationSeams semantic = seams();
  semantic.validate_revision =
      [](const NamespacePolicy &, const iotox::sync::AcceptedHead &,
         const std::filesystem::path &, const std::filesystem::path &) {
        return Status{iotox::ErrorCode::protocol_error,
                      "semantic artifact/manifest mismatch"};
      };
  activated = iotox::sync::activate_staged_artifact(
      request, device, crypto, semantic);
  IOTOX_CHECK(!activated.ok());
  IOTOX_CHECK(activated.status().code() == iotox::ErrorCode::protocol_error);

  ActivatedRevisionStore store(namespace_policy.root);
  auto loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(!loaded.value().has_value());
}

IOTOX_TEST("sync activation refuses rollback fork and corrupt prior state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy namespace_policy = policy(temporary.path() / "sync");
  const CandidateHead head = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  accept(namespace_policy, head, device, crypto);
  write_file(object_path(namespace_policy, head), "alpha");

  ActivatedRevisionStore store(namespace_policy.root);
  IOTOX_CHECK(store
                  .store(namespace_policy,
                         ActivatedRevision{namespace_policy.id, 2U, digest(2U),
                                           digest(3U), 5U},
                         device, crypto)
                  .ok());
  auto activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, head.record}, device, crypto,
      seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::stale);

  IOTOX_CHECK(store
                  .store(namespace_policy,
                         ActivatedRevision{namespace_policy.id, 1U, digest(9U),
                                           digest(3U), 5U},
                         device, crypto)
                  .ok());
  activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, head.record}, device, crypto,
      seams());
  IOTOX_CHECK(activated.ok());
  IOTOX_CHECK(activated.value().decision == ActivationDecision::fork);

  const std::filesystem::path activation_path =
      std::filesystem::path(namespace_policy.root) / "activated-revisions" /
      "field-notes.activated-revision";
  write_file(activation_path, "truncated");
  activated = iotox::sync::activate_staged_artifact(
      SyncActivationRequest{namespace_policy, head.record}, device, crypto,
      seams());
  IOTOX_CHECK(!activated.ok());
  IOTOX_CHECK(activated.status().code() == iotox::ErrorCode::protocol_error);
}
