#include "test_harness.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_head.hpp"

#include <cstdint>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

using iotox::sync::AcceptedHead;
using iotox::sync::AcceptedHeadStore;
using iotox::sync::CandidateHead;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::HeadAcceptanceDecision;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-head-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) {
      throw std::runtime_error("mkdtemp failed");
    }
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

NamespacePolicy policy() {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = "/var/lib/iotox/sync/field-notes";
  result.engine = Engine::range_v1;
  result.writers = {principal(1U), principal(2U)};
  result.subscribers = {principal(3U)};
  return result;
}

CandidateHead candidate(std::uint64_t generation, std::uint8_t record,
                        Digest parent = {}) {
  CandidateHead result;
  result.namespace_id = "field-notes";
  result.writer = principal(1U);
  result.engine = Engine::range_v1;
  result.generation = generation;
  result.record = digest(record);
  result.parent = parent;
  result.artifact = digest(static_cast<std::uint8_t>(record + 64U));
  result.manifest = digest(static_cast<std::uint8_t>(record + 96U));
  result.artifact_bytes = 1024U;
  result.manifest_bytes = 128U;
  return result;
}

} // namespace

IOTOX_TEST("sync accepted head record round trips canonical state") {
  AcceptedHead head;
  head.namespace_id = "field-notes";
  head.writer = principal(1U);
  head.engine = Engine::range_v1;
  head.generation = 7U;
  head.record = digest(7U);
  head.parent = digest(6U);
  head.artifact = digest(8U);
  head.manifest = digest(9U);
  head.artifact_bytes = 1024U;
  head.manifest_bytes = 128U;

  IOTOX_CHECK(iotox::sync::validate_accepted_head(policy(), head).ok());
  auto encoded = iotox::sync::encode_accepted_head(head);
  IOTOX_CHECK(encoded.ok());
  auto decoded = iotox::sync::decode_accepted_head(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == head);

  NamespacePolicy tree_policy = policy();
  tree_policy.engine = Engine::treepack_v1;
  head.engine = Engine::treepack_v1;
  IOTOX_CHECK(iotox::sync::validate_accepted_head(tree_policy, head).ok());
  encoded = iotox::sync::encode_accepted_head(head);
  IOTOX_CHECK(encoded.ok());
  decoded = iotox::sync::decode_accepted_head(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == head);

  std::vector<std::uint8_t> changed = encoded.value();
  changed.insert(changed.end() - 1U,
                 {'u', 'n', 'k', 'n', 'o', 'w', 'n', '=', '1', '\n'});
  IOTOX_CHECK(!iotox::sync::decode_accepted_head(changed).ok());

  changed = encoded.value();
  changed.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_accepted_head(changed).ok());
}

IOTOX_TEST("sync accepted head evaluates genesis duplicate and advance") {
  NamespacePolicy namespace_policy = policy();
  auto first = candidate(1U, 1U);
  auto evaluated = iotox::sync::evaluate_candidate_head(namespace_policy, first,
                                                        std::nullopt);
  IOTOX_CHECK(evaluated.decision == HeadAcceptanceDecision::accept_genesis);
  IOTOX_CHECK(evaluated.accepted());

  AcceptedHead current;
  current.namespace_id = first.namespace_id;
  current.writer = first.writer;
  current.engine = first.engine;
  current.generation = first.generation;
  current.record = first.record;
  current.parent = first.parent;
  current.artifact = first.artifact;
  current.manifest = first.manifest;
  current.artifact_bytes = first.artifact_bytes;
  current.manifest_bytes = first.manifest_bytes;

  evaluated =
      iotox::sync::evaluate_candidate_head(namespace_policy, first, current);
  IOTOX_CHECK(evaluated.decision == HeadAcceptanceDecision::duplicate);
  IOTOX_CHECK(evaluated.accepted());

  auto second = candidate(2U, 2U, first.record);
  evaluated =
      iotox::sync::evaluate_candidate_head(namespace_policy, second, current);
  IOTOX_CHECK(evaluated.decision == HeadAcceptanceDecision::accept_advance);
  IOTOX_CHECK(evaluated.generation_delta == 1U);
}

IOTOX_TEST(
    "sync accepted head rejects rollback fork parent and policy violations") {
  NamespacePolicy namespace_policy = policy();
  AcceptedHead current;
  current.namespace_id = "field-notes";
  current.writer = principal(1U);
  current.engine = Engine::range_v1;
  current.generation = 5U;
  current.record = digest(5U);
  current.parent = digest(4U);
  current.artifact = digest(80U);
  current.manifest = digest(90U);
  current.artifact_bytes = 1024U;
  current.manifest_bytes = 128U;

  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(
                  namespace_policy, candidate(4U, 6U, current.record), current)
                  .decision == HeadAcceptanceDecision::stale);
  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(
                  namespace_policy, candidate(5U, 6U, current.parent), current)
                  .decision == HeadAcceptanceDecision::fork);
  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(
                  namespace_policy, candidate(6U, 6U, digest(99U)), current)
                  .decision == HeadAcceptanceDecision::parent_mismatch);

  auto wrong_namespace = candidate(6U, 6U, current.record);
  wrong_namespace.namespace_id = "other";
  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(namespace_policy,
                                                   wrong_namespace, current)
                  .decision == HeadAcceptanceDecision::wrong_namespace);

  auto wrong_writer = candidate(6U, 6U, current.record);
  wrong_writer.writer = principal(9U);
  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(namespace_policy,
                                                   wrong_writer, current)
                  .decision == HeadAcceptanceDecision::unauthorized_writer);

  auto oversized = candidate(6U, 6U, current.record);
  oversized.artifact_bytes =
      namespace_policy.quotas.maximum_artifact_bytes + 1U;
  IOTOX_CHECK(
      iotox::sync::evaluate_candidate_head(namespace_policy, oversized, current)
          .decision == HeadAcceptanceDecision::resource_limit);
}

IOTOX_TEST("sync accepted head store persists advances atomically") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  AcceptedHeadStore store(temporary.path());
  NamespacePolicy namespace_policy = policy();
  namespace_policy.root = temporary.path().lexically_normal().string();

  auto missing = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(missing.ok());
  IOTOX_CHECK(!missing.value().has_value());

  auto first = candidate(1U, 1U);
  auto accepted = store.accept(namespace_policy, first, device, crypto);
  IOTOX_CHECK(accepted.ok());
  IOTOX_CHECK(accepted.value().decision ==
              HeadAcceptanceDecision::accept_genesis);

  auto loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->record == first.record);

  auto stale = store.accept(namespace_policy, candidate(1U, 9U), device,
                            crypto);
  IOTOX_CHECK(stale.ok());
  IOTOX_CHECK(stale.value().decision == HeadAcceptanceDecision::fork);
  loaded = store.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value()->record == first.record);

  auto second = candidate(2U, 2U, first.record);
  accepted = store.accept(namespace_policy, second, device, crypto);
  IOTOX_CHECK(accepted.ok());
  IOTOX_CHECK(accepted.value().decision ==
              HeadAcceptanceDecision::accept_advance);

  AcceptedHeadStore reopened(temporary.path());
  loaded = reopened.load(namespace_policy, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->generation == 2U);
  IOTOX_CHECK(loaded.value()->record == second.record);
}

IOTOX_TEST("sync accepted head state authenticates the stable device") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity foreign =
      identity(temporary.path() / "foreign.identity", crypto);
  NamespacePolicy namespace_policy = policy();
  namespace_policy.root = temporary.path().lexically_normal().string();
  AcceptedHeadStore store(temporary.path());

  IOTOX_CHECK(store
                  .accept(namespace_policy, candidate(1U, 1U), device, crypto)
                  .ok());
  IOTOX_CHECK(
      !store.load(namespace_policy, foreign.public_key(), crypto).ok());

  const auto state_path =
      temporary.path() / "accepted-heads" / "field-notes.accepted-head";
  auto bytes = iotox::StateStore::read(state_path);
  IOTOX_CHECK(bytes.ok());
  bytes.value()[32U] ^= 0x01U;
  IOTOX_CHECK(iotox::StateStore::write_atomic(state_path, bytes.value()).ok());
  IOTOX_CHECK(
      !store.load(namespace_policy, device.public_key(), crypto).ok());
}

IOTOX_TEST(
    "sync accepted head store rejects path ids and invalid current anchors") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  AcceptedHeadStore store(temporary.path());
  NamespacePolicy namespace_policy = policy();
  namespace_policy.root = temporary.path().lexically_normal().string();

  NamespacePolicy escape = namespace_policy;
  escape.id = "../escape";
  IOTOX_CHECK(!store.load(escape, device.public_key(), crypto).ok());

  AcceptedHead bad_current;
  bad_current.namespace_id = "field-notes";
  bad_current.writer = principal(9U);
  bad_current.engine = Engine::range_v1;
  bad_current.generation = 1U;
  bad_current.record = digest(1U);
  bad_current.artifact = digest(2U);
  bad_current.manifest = digest(3U);
  bad_current.artifact_bytes = 1024U;
  bad_current.manifest_bytes = 128U;
  auto encoded = iotox::sync::encode_accepted_head(bad_current);
  IOTOX_CHECK(encoded.ok());
  const auto state_path =
      temporary.path() / "accepted-heads" / "field-notes.accepted-head";
  IOTOX_CHECK(
      iotox::StateStore::write_atomic(state_path, encoded.value()).ok());

  auto accepted = store.accept(namespace_policy,
                               candidate(2U, 2U, digest(1U)), device, crypto);
  IOTOX_CHECK(!accepted.ok());
}
