#include "test_harness.hpp"

#include "iotox/sync_retention.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

using iotox::sync::AcceptedHead;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::RetainedRevision;
using iotox::sync::RetentionSnapshot;
using iotox::sync::RetentionStore;
using iotox::sync::RetentionUpdate;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-retention-XXXXXX";
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

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
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

PrincipalId principal(std::uint8_t value) {
  PrincipalId result{};
  result[0U] = value;
  return result;
}

NamespacePolicy policy(const std::filesystem::path &root,
                       std::uint64_t retained_count = 4U) {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = {principal(1U)};
  result.quotas.maximum_artifact_bytes = 4096U;
  result.quotas.maximum_manifest_bytes = 1024U;
  result.quotas.maximum_retained_revisions = retained_count;
  return result;
}

AcceptedHead head(std::uint64_t generation, std::uint8_t value) {
  AcceptedHead result;
  result.namespace_id = "field-notes";
  result.writer = principal(1U);
  result.engine = Engine::range_v1;
  result.generation = generation;
  result.record = digest(value);
  result.parent = generation == 1U
                      ? Digest{}
                      : digest(static_cast<std::uint8_t>(value - 1U));
  result.artifact = digest(static_cast<std::uint8_t>(value + 32U));
  result.manifest = digest(static_cast<std::uint8_t>(value + 64U));
  result.artifact_bytes = 100U + value;
  result.manifest_bytes = 20U + value;
  return result;
}

RetainedRevision retained(std::uint64_t generation, std::uint8_t value) {
  const AcceptedHead source = head(generation, value);
  return RetainedRevision{source.generation, source.record, source.artifact,
                          source.manifest, source.artifact_bytes,
                          source.manifest_bytes};
}

void overwrite(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("unable to overwrite retention fixture");
}

std::vector<std::uint8_t> read_all(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return std::vector<std::uint8_t>(std::istreambuf_iterator<char>(input),
                                   std::istreambuf_iterator<char>());
}

} // namespace

IOTOX_TEST("sync retention snapshot has one canonical bounded encoding") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  RetentionSnapshot snapshot{"field-notes",
                             {retained(1U, 1U), retained(2U, 2U)},
                             device.public_key(), 1U};
  auto body = iotox::sync::encode_retention_snapshot(snapshot);
  IOTOX_CHECK(body.ok());
  auto signing_digest = crypto.hash(
      "iotox-sync-retention-signature-v2",
      std::span<const std::uint8_t>(body.value()).first(body.value().size() -
                                                        iotox::security::kSignatureBytes));
  IOTOX_CHECK(signing_digest.ok());
  auto signature = device.sign(signing_digest.value());
  IOTOX_CHECK(signature.ok());
  snapshot.signature = signature.value();
  auto encoded = iotox::sync::encode_retention_snapshot(snapshot);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() == 464U);
  auto decoded = iotox::sync::decode_retention_snapshot(encoded.value(), 2U);
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == snapshot);
  IOTOX_CHECK(iotox::sync::verify_retention_snapshot(
                  decoded.value(), device.public_key(), crypto)
                  .ok());
  auto changed = encoded.value();
  changed[9U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_retention_snapshot(changed, 2U).ok());
  changed = encoded.value();
  changed.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_retention_snapshot(changed, 2U).ok());
  changed = encoded.value();
  changed[7U] = static_cast<std::uint8_t>('1');
  IOTOX_CHECK(!iotox::sync::decode_retention_snapshot(changed, 2U).ok());
  IOTOX_CHECK(!iotox::sync::decode_retention_snapshot(encoded.value(), 1U).ok());
}

IOTOX_TEST("sync retention pin is durable and idempotent") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  auto pinned = store.pin(configured, head(1U, 1U), device, crypto);
  IOTOX_CHECK(pinned.ok());
  IOTOX_CHECK(pinned.value() == RetentionUpdate::inserted);
  pinned = store.pin(configured, head(1U, 1U), device, crypto);
  IOTOX_CHECK(pinned.ok());
  IOTOX_CHECK(pinned.value() == RetentionUpdate::duplicate);
  auto loaded = RetentionStore(configured.root).load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().revisions ==
              std::vector<RetainedRevision>{retained(1U, 1U)});
}

IOTOX_TEST("sync retention sorts pins and persists unpin") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  IOTOX_CHECK(store.pin(configured, head(3U, 3U), device, crypto).ok());
  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  auto loaded = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().revisions[0U].generation == 1U);
  IOTOX_CHECK(loaded.value().revisions[1U].generation == 3U);
  auto removed = store.unpin(configured, digest(1U), device, crypto);
  IOTOX_CHECK(removed.ok());
  IOTOX_CHECK(removed.value());
  removed = store.unpin(configured, digest(1U), device, crypto);
  IOTOX_CHECK(removed.ok());
  IOTOX_CHECK(!removed.value());
  loaded = RetentionStore(configured.root)
               .load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().revisions.size() == 1U);
  IOTOX_CHECK(loaded.value().revisions[0U].record == digest(3U));
}

IOTOX_TEST("sync retention refuses capacity and generation forks") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", 1U);
  configured.quotas.maximum_objects = 1U;
  RetentionStore store(configured.root);
  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  auto denied = store.pin(configured, head(2U, 2U), device, crypto);
  IOTOX_CHECK(!denied.ok());
  IOTOX_CHECK(denied.status().code() == iotox::ErrorCode::resource_exhausted);
  denied = store.pin(configured, head(1U, 9U), device, crypto);
  IOTOX_CHECK(!denied.ok());
  IOTOX_CHECK(denied.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync retention validates heads against namespace policy") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  AcceptedHead invalid = head(1U, 1U);
  invalid.namespace_id = "other";
  IOTOX_CHECK(!store.pin(configured, invalid, device, crypto).ok());
  invalid = head(1U, 1U);
  invalid.artifact_bytes = configured.quotas.maximum_artifact_bytes + 1U;
  IOTOX_CHECK(!store.pin(configured, invalid, device, crypto).ok());
  IOTOX_CHECK(!std::filesystem::exists(configured.root));
}

IOTOX_TEST("sync retention refuses corrupt and noncanonical state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  const auto path = std::filesystem::path(configured.root) / "retention" /
                    "field-notes.retained-revisions";
  auto changed = read_all(path);
  changed[159U] ^= 1U;
  overwrite(path, changed);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
  IOTOX_CHECK(!store.pin(configured, head(2U, 2U), device, crypto).ok());
}

IOTOX_TEST("sync retention refuses weak linked and symlink state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  const auto path = std::filesystem::path(configured.root) / "retention" /
                    "field-notes.retained-revisions";
  std::filesystem::permissions(path, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
  std::filesystem::permissions(path, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);
  const auto lock = std::filesystem::path(configured.root) / "transactions" /
                    "field-notes.transaction.lock";
  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!store.pin(configured, head(2U, 2U), device, crypto).ok());
  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);
  const auto alias = path.parent_path() / "alias";
  std::filesystem::create_hard_link(path, alias);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
  std::filesystem::remove(alias);
  const auto backing = path.parent_path() / "backing";
  std::filesystem::rename(path, backing);
  std::filesystem::create_symlink(backing.filename(), path);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
}

IOTOX_TEST("sync retention store is namespace-root bound") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore misplaced(temporary.path() / "elsewhere");
  IOTOX_CHECK(!misplaced.load(configured, device.public_key(), crypto).ok());
  IOTOX_CHECK(!misplaced.pin(configured, head(1U, 1U), device, crypto).ok());
  IOTOX_CHECK(!std::filesystem::exists(temporary.path() / "elsewhere"));
}

IOTOX_TEST("sync retention authenticates the stable device and rejects tampering") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity stranger =
      identity(temporary.path() / "stranger.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  IOTOX_CHECK(!store.load(configured, stranger.public_key(), crypto).ok());
  IOTOX_CHECK(!store.unpin(configured, digest(1U), stranger, crypto).ok());

  const auto path = std::filesystem::path(configured.root) / "retention" /
                    "field-notes.retained-revisions";
  auto bytes = read_all(path);
  bytes.back() ^= 1U;
  overwrite(path, bytes);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
}

IOTOX_TEST("sync retention hash-links authenticated mutations") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  RetentionStore store(configured.root);
  const auto path = std::filesystem::path(configured.root) / "retention" /
                    "field-notes.retained-revisions";

  IOTOX_CHECK(store.pin(configured, head(1U, 1U), device, crypto).ok());
  auto first = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(first.ok());
  IOTOX_CHECK(first.value().mutation == 1U);
  IOTOX_CHECK(first.value().previous == Digest{});
  auto first_record =
      crypto.hash("iotox-sync-retention-record-v2", read_all(path));
  IOTOX_CHECK(first_record.ok());

  IOTOX_CHECK(store.pin(configured, head(2U, 2U), device, crypto).ok());
  auto second = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(second.value().mutation == 2U);
  IOTOX_CHECK(second.value().previous == first_record.value());
  auto second_record =
      crypto.hash("iotox-sync-retention-record-v2", read_all(path));
  IOTOX_CHECK(second_record.ok());

  auto removed = store.unpin(configured, digest(1U), device, crypto);
  IOTOX_CHECK(removed.ok());
  IOTOX_CHECK(removed.value());
  auto third = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(third.ok());
  IOTOX_CHECK(third.value().mutation == 3U);
  IOTOX_CHECK(third.value().previous == second_record.value());
}
