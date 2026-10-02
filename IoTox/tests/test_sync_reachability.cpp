#include "test_harness.hpp"

#include "iotox/sync_reachability.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <initializer_list>
#include <optional>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::AcceptedHead;
using iotox::sync::ActivatedRevision;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::RetentionSnapshot;
using iotox::sync::RetentionStore;
using iotox::sync::SignedHead;
using iotox::sync::SignedHeadPublicationRequest;
using iotox::sync::SignedHeadStore;
using iotox::sync::SyncObjectKind;
using iotox::sync::SyncObjectRecord;
using iotox::sync::SyncReachabilityRoots;
using iotox::sync::SyncRootSource;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-reachability-XXXXXX";
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
  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

private:
  std::filesystem::path path_;
};

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

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

NamespacePolicy policy(const std::filesystem::path &root,
                       const DeviceIdentity &device) {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = {device.public_key()};
  result.quotas.maximum_artifact_bytes = 4096U;
  result.quotas.maximum_manifest_bytes = 1024U;
  result.quotas.maximum_store_bytes = 16384U;
  result.quotas.maximum_staging_bytes = 8192U;
  result.quotas.maximum_objects = 16U;
  result.quotas.maximum_retained_revisions = 4U;
  return result;
}

SignedHead signed_head(const NamespacePolicy &configured,
                       const DeviceIdentity &device, const Sodium &crypto,
                       std::uint8_t value) {
  SignedHeadPublicationRequest request;
  request.artifact = digest(value);
  request.manifest = digest(static_cast<std::uint8_t>(value + 32U));
  request.artifact_bytes = 100U + value;
  request.manifest_bytes = 20U + value;
  auto created = iotox::sync::create_signed_head(
      configured, request, std::nullopt, device, crypto);
  if (!created.ok())
    throw std::runtime_error(created.status().message());
  return created.value();
}

AcceptedHead accepted(const NamespacePolicy &configured,
                      const SignedHead &head, const Sodium &crypto) {
  auto candidate =
      iotox::sync::verified_candidate_head(configured, head, crypto);
  if (!candidate.ok())
    throw std::runtime_error(candidate.status().message());
  return AcceptedHead{candidate.value().namespace_id,
                      candidate.value().writer,
                      candidate.value().engine,
                      candidate.value().generation,
                      candidate.value().record,
                      candidate.value().parent,
                      candidate.value().artifact,
                      candidate.value().manifest,
                      candidate.value().artifact_bytes,
                      candidate.value().manifest_bytes};
}

SyncObjectRecord artifact(std::uint8_t value, std::uint64_t bytes) {
  return SyncObjectRecord{SyncObjectKind::artifact, digest(value), bytes};
}

SyncObjectRecord manifest(std::uint8_t value, std::uint64_t bytes) {
  return SyncObjectRecord{SyncObjectKind::manifest, digest(value), bytes};
}

std::uint8_t source_mask(std::initializer_list<SyncRootSource> sources) {
  std::uint8_t result = 0U;
  for (const SyncRootSource source : sources)
    result |= static_cast<std::uint8_t>(source);
  return result;
}

std::string hex(const Digest &value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(value.size() * 2U);
  for (const std::uint8_t byte : value) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

void write_object(const std::filesystem::path &root,
                  const SyncObjectRecord &object) {
  const std::filesystem::path directory = root / "objects";
  std::filesystem::create_directories(directory);
  std::filesystem::permissions(directory, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace);
  const std::string suffix = object.kind == SyncObjectKind::artifact
                                 ? ".artifact"
                                 : ".manifest";
  const std::filesystem::path path = directory / (hex(object.identity) + suffix);
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  std::vector<char> bytes(static_cast<std::size_t>(object.bytes), 'x');
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  output.close();
  std::filesystem::permissions(
      path, std::filesystem::perms::owner_read |
                std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
}

} // namespace

IOTOX_TEST("sync reachability merges every current live-root source") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHead published = signed_head(configured, device, crypto, 1U);
  AcceptedHead current = accepted(configured, published, crypto);
  RetentionStore retention(configured.root);
  IOTOX_CHECK(retention.pin(configured, current, device, crypto).ok());
  auto retained = retention.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(retained.ok());

  SyncReachabilityRoots roots;
  roots.published = published;
  roots.accepted = current;
  roots.activated = ActivatedRevision{configured.id, current.generation,
                                      current.record, current.artifact,
                                      current.artifact_bytes};
  roots.retained = retained.value();
  std::vector<SyncObjectRecord> inventory{
      manifest(33U, 21U), artifact(9U, 50U), artifact(1U, 101U)};
  auto plan = iotox::sync::plan_sync_reachability(
      configured, device.public_key(), roots, inventory, crypto);
  IOTOX_CHECK(plan.ok());
  IOTOX_CHECK(plan.value().consistent());
  IOTOX_CHECK(plan.value().retention_authenticated);
  IOTOX_CHECK(plan.value().rooted.size() == 2U);
  IOTOX_CHECK(plan.value().unreferenced ==
              std::vector<SyncObjectRecord>{artifact(9U, 50U)});
  IOTOX_CHECK(plan.value().rooted[0U].source_mask ==
              source_mask({SyncRootSource::published,
                           SyncRootSource::accepted,
                           SyncRootSource::activated,
                           SyncRootSource::retained}));
  IOTOX_CHECK(plan.value().rooted[1U].source_mask ==
              source_mask({SyncRootSource::published,
                           SyncRootSource::accepted,
                           SyncRootSource::retained}));
  IOTOX_CHECK(plan.value().rooted_bytes == 122U);
  IOTOX_CHECK(plan.value().unreferenced_bytes == 50U);
}

IOTOX_TEST("sync reachability preserves distinct activated and retained roots") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHead published = signed_head(configured, device, crypto, 1U);
  AcceptedHead current = accepted(configured, published, crypto);
  AcceptedHead old = current;
  old.generation = 2U;
  old.record = digest(70U);
  old.parent = current.record;
  old.artifact = digest(2U);
  old.manifest = digest(34U);
  old.artifact_bytes = 102U;
  old.manifest_bytes = 22U;
  RetentionStore retention(configured.root);
  IOTOX_CHECK(retention.pin(configured, old, device, crypto).ok());
  auto retained = retention.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(retained.ok());
  SyncReachabilityRoots roots;
  roots.published = published;
  roots.activated = ActivatedRevision{configured.id, 3U, digest(80U),
                                      digest(3U), 103U};
  roots.retained = retained.value();
  auto plan = iotox::sync::plan_sync_reachability(
      configured, device.public_key(), roots,
      {artifact(1U, 101U), manifest(33U, 21U), artifact(2U, 102U),
       manifest(34U, 22U), artifact(3U, 103U)},
      crypto);
  IOTOX_CHECK(plan.ok());
  IOTOX_CHECK(plan.value().consistent());
  IOTOX_CHECK(plan.value().rooted.size() == 5U);
  IOTOX_CHECK(plan.value().unreferenced.empty());
}

IOTOX_TEST("sync reachability reports missing and mismatched live objects") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHead published = signed_head(configured, device, crypto, 1U);
  SyncReachabilityRoots roots;
  roots.published = published;
  roots.retained = RetentionSnapshot{configured.id, {}, device.public_key()};
  auto plan = iotox::sync::plan_sync_reachability(
      configured, device.public_key(), roots, {artifact(1U, 99U)}, crypto);
  IOTOX_CHECK(plan.ok());
  IOTOX_CHECK(!plan.value().consistent());
  IOTOX_CHECK(!plan.value().retention_authenticated);
  IOTOX_CHECK(plan.value().missing.size() == 1U);
  IOTOX_CHECK(plan.value().mismatched.size() == 1U);
  IOTOX_CHECK(plan.value().mismatched[0U].observed_bytes == 99U);
  IOTOX_CHECK(plan.value().unreferenced.empty());
}

IOTOX_TEST("sync reachability rejects foreign and altered authenticated roots") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity stranger =
      identity(temporary.path() / "stranger.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHead published = signed_head(configured, device, crypto, 1U);
  AcceptedHead current = accepted(configured, published, crypto);
  RetentionStore retention(configured.root);
  IOTOX_CHECK(retention.pin(configured, current, device, crypto).ok());
  auto retained = retention.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(retained.ok());
  SyncReachabilityRoots roots;
  roots.published = published;
  roots.retained = retained.value();
  IOTOX_CHECK(!iotox::sync::plan_sync_reachability(
                   configured, stranger.public_key(), roots, {}, crypto)
                   .ok());
  roots.retained.signature[0U] ^= 1U;
  IOTOX_CHECK(!iotox::sync::plan_sync_reachability(
                   configured, device.public_key(), roots, {}, crypto)
                   .ok());
}

IOTOX_TEST("sync reachability refuses conflicting roots and duplicate inventory") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHead published = signed_head(configured, device, crypto, 1U);
  AcceptedHead current = accepted(configured, published, crypto);
  current.artifact_bytes += 1U;
  SyncReachabilityRoots roots;
  roots.published = published;
  roots.accepted = current;
  roots.retained = RetentionSnapshot{configured.id, {}, device.public_key()};
  IOTOX_CHECK(!iotox::sync::plan_sync_reachability(
                   configured, device.public_key(), roots, {}, crypto)
                   .ok());
  roots.accepted.reset();
  IOTOX_CHECK(!iotox::sync::plan_sync_reachability(
                   configured, device.public_key(), roots,
                   {artifact(9U, 50U), artifact(9U, 50U)}, crypto)
                   .ok());
}

IOTOX_TEST("sync reachability loads one transaction-stable persisted snapshot") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHeadStore publisher(configured.root);
  SignedHeadPublicationRequest request{digest(1U), digest(33U), 101U, 21U};
  auto published = publisher.publish(configured, request, device, crypto);
  IOTOX_CHECK(published.ok());
  auto candidate = iotox::sync::verified_candidate_head(
      configured, published.value().head, crypto);
  IOTOX_CHECK(candidate.ok());
  iotox::sync::AcceptedHeadStore accepted_store(configured.root);
  auto accepted_result =
      accepted_store.accept(configured, candidate.value(), device, crypto);
  IOTOX_CHECK(accepted_result.ok());
  AcceptedHead current = accepted(configured, published.value().head, crypto);
  iotox::sync::ActivatedRevisionStore activated_store(configured.root);
  IOTOX_CHECK(activated_store
                  .store(configured,
                         ActivatedRevision{configured.id, current.generation,
                                           current.record, current.artifact,
                                           current.artifact_bytes},
                         device, crypto)
                  .ok());
  RetentionStore retention(configured.root);
  IOTOX_CHECK(retention.pin(configured, current, device, crypto).ok());
  write_object(configured.root, artifact(1U, 101U));
  write_object(configured.root, manifest(33U, 21U));

  auto plan = iotox::sync::plan_sync_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(plan.ok());
  IOTOX_CHECK(plan.value().transaction_stable);
  IOTOX_CHECK(plan.value().rollback_guard_consistent);
  IOTOX_CHECK(plan.value().retention_authenticated);
  IOTOX_CHECK(plan.value().consistent());
  IOTOX_CHECK(plan.value().rooted.size() == 2U);
  IOTOX_CHECK(plan.value().unreferenced.empty());
}
