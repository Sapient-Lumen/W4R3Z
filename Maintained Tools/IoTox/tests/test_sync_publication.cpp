#include "test_harness.hpp"

#include "iotox/sync_publication.hpp"

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::SigningPublicKey;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::SignedHead;
using iotox::sync::SignedHeadPublicationRequest;
using iotox::sync::SignedHeadStore;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-publication-XXXXXX";
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
                       std::vector<SigningPublicKey> writers) {
  std::sort(writers.begin(), writers.end());
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = std::move(writers);
  result.quotas.maximum_artifact_bytes = 4096U;
  result.quotas.maximum_manifest_bytes = 1024U;
  return result;
}

SignedHeadPublicationRequest request(std::uint8_t value) {
  SignedHeadPublicationRequest result;
  result.artifact = digest(value);
  result.manifest = digest(static_cast<std::uint8_t>(value + 64U));
  result.artifact_bytes = 100U + value;
  result.manifest_bytes = 20U + value;
  return result;
}

void resign(SignedHead &head, const DeviceIdentity &writer,
            const Sodium &crypto) {
  auto body = iotox::sync::encode_signed_head_body(head);
  if (!body.ok())
    throw std::runtime_error(body.status().message());
  auto signing_digest =
      crypto.hash("iotox-sync-head-signature-v1", body.value());
  if (!signing_digest.ok())
    throw std::runtime_error(signing_digest.status().message());
  auto signature = writer.sign(signing_digest.value());
  if (!signature.ok())
    throw std::runtime_error(signature.status().message());
  head.signature = signature.value();
}

void overwrite(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("unable to overwrite fixture");
}

} // namespace

IOTOX_TEST("signed sync HEAD has one fixed canonical binary representation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});

  auto created = iotox::sync::create_signed_head(
      configured, request(1U), std::nullopt, writer, crypto);
  IOTOX_CHECK(created.ok());
  IOTOX_CHECK(created.value().generation == 1U);
  IOTOX_CHECK(created.value().writer == writer.public_key());
  IOTOX_CHECK(created.value().parent == Digest{});
  IOTOX_CHECK(iotox::sync::verify_signed_head(configured, created.value(),
                                              crypto)
                  .ok());

  auto encoded = iotox::sync::encode_signed_head(created.value());
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() == iotox::sync::kSignedHeadBytes);
  auto decoded = iotox::sync::decode_signed_head(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == created.value());
  auto reencoded = iotox::sync::encode_signed_head(decoded.value());
  IOTOX_CHECK(reencoded.ok());
  IOTOX_CHECK(reencoded.value() == encoded.value());
}

IOTOX_TEST("signed sync HEAD verifies before becoming an acceptance candidate") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});
  auto created = iotox::sync::create_signed_head(
      configured, request(2U), std::nullopt, writer, crypto);
  IOTOX_CHECK(created.ok());

  auto candidate =
      iotox::sync::verified_candidate_head(configured, created.value(), crypto);
  IOTOX_CHECK(candidate.ok());
  IOTOX_CHECK(candidate.value().namespace_id == configured.id);
  IOTOX_CHECK(candidate.value().writer == writer.public_key());
  IOTOX_CHECK(candidate.value().generation == 1U);
  auto record =
      iotox::sync::signed_head_record_digest(created.value(), crypto);
  IOTOX_CHECK(record.ok());
  IOTOX_CHECK(candidate.value().record == record.value());
  IOTOX_CHECK(iotox::sync::evaluate_candidate_head(
                  configured, candidate.value(), std::nullopt)
                  .accepted());
}

IOTOX_TEST("signed sync HEAD rejects body signature and padding tampering") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});
  auto created = iotox::sync::create_signed_head(
      configured, request(3U), std::nullopt, writer, crypto);
  IOTOX_CHECK(created.ok());
  auto encoded = iotox::sync::encode_signed_head(created.value());
  IOTOX_CHECK(encoded.ok());

  auto changed = encoded.value();
  changed[104U] ^= 0x01U;
  auto decoded = iotox::sync::decode_signed_head(changed);
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(!iotox::sync::verify_signed_head(configured, decoded.value(),
                                               crypto)
                   .ok());

  changed = encoded.value();
  changed[iotox::sync::kSignedHeadBodyBytes] ^= 0x01U;
  decoded = iotox::sync::decode_signed_head(changed);
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(!iotox::sync::verify_signed_head(configured, decoded.value(),
                                               crypto)
                   .ok());

  changed = encoded.value();
  changed[200U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_signed_head(changed).ok());
  IOTOX_CHECK(!iotox::sync::decode_signed_head(
                   std::span<const std::uint8_t>(changed).first(changed.size() - 1U))
                   .ok());
}

IOTOX_TEST("signed sync HEAD is bound to writer namespace engine and quotas") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  DeviceIdentity stranger =
      identity(temporary.path() / "stranger.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});

  auto denied = iotox::sync::create_signed_head(
      configured, request(4U), std::nullopt, stranger, crypto);
  IOTOX_CHECK(!denied.ok());

  auto oversized = request(4U);
  oversized.artifact_bytes = configured.quotas.maximum_artifact_bytes + 1U;
  denied = iotox::sync::create_signed_head(
      configured, oversized, std::nullopt, writer, crypto);
  IOTOX_CHECK(!denied.ok());

  auto created = iotox::sync::create_signed_head(
      configured, request(4U), std::nullopt, writer, crypto);
  IOTOX_CHECK(created.ok());
  NamespacePolicy other = configured;
  other.id = "other";
  IOTOX_CHECK(!iotox::sync::verify_signed_head(other, created.value(), crypto)
                   .ok());
  other = configured;
  other.engine = Engine::content_v2;
  IOTOX_CHECK(!iotox::sync::verify_signed_head(other, created.value(), crypto)
                   .ok());

  SignedHead malformed = created.value();
  malformed.parent = digest(99U);
  resign(malformed, writer, crypto);
  IOTOX_CHECK(!iotox::sync::verify_signed_head(configured, malformed, crypto)
                   .ok());
  malformed = created.value();
  malformed.generation = 2U;
  resign(malformed, writer, crypto);
  IOTOX_CHECK(!iotox::sync::verify_signed_head(configured, malformed, crypto)
                   .ok());
}

IOTOX_TEST("signed sync HEAD successors link exact records and advance once") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});
  auto first = iotox::sync::create_signed_head(
      configured, request(5U), std::nullopt, writer, crypto);
  IOTOX_CHECK(first.ok());
  auto second = iotox::sync::create_signed_head(
      configured, request(6U), first.value(), writer, crypto);
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(second.value().generation == 2U);
  auto first_record =
      iotox::sync::signed_head_record_digest(first.value(), crypto);
  IOTOX_CHECK(first_record.ok());
  IOTOX_CHECK(second.value().parent == first_record.value());
  auto second_candidate =
      iotox::sync::verified_candidate_head(configured, second.value(), crypto);
  IOTOX_CHECK(second_candidate.ok());
  auto first_candidate =
      iotox::sync::verified_candidate_head(configured, first.value(), crypto);
  IOTOX_CHECK(first_candidate.ok());
  iotox::sync::AcceptedHead accepted{
      first_candidate.value().namespace_id,
      first_candidate.value().writer,
      first_candidate.value().engine,
      first_candidate.value().generation,
      first_candidate.value().record,
      first_candidate.value().parent,
      first_candidate.value().artifact,
      first_candidate.value().manifest,
      first_candidate.value().artifact_bytes,
      first_candidate.value().manifest_bytes};
  const auto evaluated = iotox::sync::evaluate_candidate_head(
      configured, second_candidate.value(), accepted);
  IOTOX_CHECK(evaluated.decision ==
              iotox::sync::HeadAcceptanceDecision::accept_advance);
}

IOTOX_TEST("signed sync HEAD refuses a predecessor from another writer") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity first_writer =
      identity(temporary.path() / "first.identity", crypto);
  DeviceIdentity second_writer =
      identity(temporary.path() / "second.identity", crypto);
  NamespacePolicy configured = policy(
      temporary.path() / "sync",
      {first_writer.public_key(), second_writer.public_key()});
  auto first = iotox::sync::create_signed_head(
      configured, request(7U), std::nullopt, first_writer, crypto);
  IOTOX_CHECK(first.ok());
  auto denied = iotox::sync::create_signed_head(
      configured, request(8U), first.value(), second_writer, crypto);
  IOTOX_CHECK(!denied.ok());
}

IOTOX_TEST("signed sync HEAD store commits genesis then linked successor") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root, {writer.public_key()});
  SignedHeadStore store(root);

  auto first = store.publish(configured, request(9U), writer, crypto);
  IOTOX_CHECK(first.ok());
  IOTOX_CHECK(first.value().genesis);
  IOTOX_CHECK(!first.value().duplicate);
  IOTOX_CHECK(first.value().head.generation == 1U);
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(*loaded.value() == first.value().head);

  auto duplicate = store.publish(configured, request(9U), writer, crypto);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().duplicate);
  IOTOX_CHECK(duplicate.value().head == first.value().head);
  IOTOX_CHECK(duplicate.value().record == first.value().record);

  auto second = store.publish(configured, request(10U), writer, crypto);
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(!second.value().genesis);
  IOTOX_CHECK(!second.value().duplicate);
  IOTOX_CHECK(second.value().head.generation == 2U);
  IOTOX_CHECK(second.value().head.parent == first.value().record);
  loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(*loaded.value() == second.value().head);
}

IOTOX_TEST("signed sync HEAD store refuses corruption and preserves prior state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root, {writer.public_key()});
  SignedHeadStore store(root);
  auto first = store.publish(configured, request(11U), writer, crypto);
  IOTOX_CHECK(first.ok());

  auto invalid = request(12U);
  invalid.manifest_bytes = configured.quotas.maximum_manifest_bytes + 1U;
  IOTOX_CHECK(!store.publish(configured, invalid, writer, crypto).ok());
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(*loaded.value() == first.value().head);

  const auto path = root / "published-heads" / "field-notes.signed-head";
  overwrite(path, {1U, 2U, 3U});
  IOTOX_CHECK(!store.load(configured, crypto).ok());
  IOTOX_CHECK(!store.publish(configured, request(12U), writer, crypto).ok());
}

IOTOX_TEST("signed sync HEAD store cannot change publisher identity mid-chain") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity first_writer =
      identity(temporary.path() / "first.identity", crypto);
  DeviceIdentity second_writer =
      identity(temporary.path() / "second.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(
      root, {first_writer.public_key(), second_writer.public_key()});
  SignedHeadStore store(root);
  auto first = store.publish(configured, request(13U), first_writer, crypto);
  IOTOX_CHECK(first.ok());
  IOTOX_CHECK(!store.publish(configured, request(14U), second_writer, crypto)
                   .ok());
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(*loaded.value() == first.value().head);
}

IOTOX_TEST("signed sync HEAD store refuses links permissions and wrong size") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root, {writer.public_key()});
  SignedHeadStore store(root);
  IOTOX_CHECK(store.publish(configured, request(15U), writer, crypto).ok());
  const auto path = root / "published-heads" / "field-notes.signed-head";

  std::filesystem::permissions(path, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!store.load(configured, crypto).ok());
  std::filesystem::permissions(path, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);
  IOTOX_CHECK(store.load(configured, crypto).ok());

  const auto alias = path.parent_path() / "alias";
  std::filesystem::create_hard_link(path, alias);
  IOTOX_CHECK(!store.load(configured, crypto).ok());
  std::filesystem::remove(alias);
  IOTOX_CHECK(store.load(configured, crypto).ok());

  const auto backing = path.parent_path() / "backing";
  std::filesystem::rename(path, backing);
  std::filesystem::create_symlink(backing.filename(), path);
  IOTOX_CHECK(!store.load(configured, crypto).ok());
  std::filesystem::remove(path);
  std::filesystem::rename(backing, path);

  std::vector<std::uint8_t> oversized(iotox::sync::kSignedHeadBytes + 1U, 0U);
  overwrite(path, oversized);
  IOTOX_CHECK(!store.load(configured, crypto).ok());
}

IOTOX_TEST("signed sync HEAD store is bound to the namespace policy root") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  NamespacePolicy configured =
      policy(temporary.path() / "sync", {writer.public_key()});
  SignedHeadStore misplaced(temporary.path() / "elsewhere");
  IOTOX_CHECK(!misplaced.load(configured, crypto).ok());
  IOTOX_CHECK(!misplaced.publish(configured, request(15U), writer, crypto).ok());
}

IOTOX_TEST("signed sync HEAD store serializes concurrent local publications") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root, {writer.public_key()});
  SignedHeadStore store(root);
  std::atomic<unsigned> failures{0U};
  std::vector<std::thread> workers;
  for (std::uint8_t index = 0U; index < 8U; ++index) {
    workers.emplace_back([&, index]() {
      if (!store.publish(configured, request(static_cast<std::uint8_t>(32U + index)),
                         writer, crypto)
               .ok()) {
        failures.fetch_add(1U, std::memory_order_relaxed);
      }
    });
  }
  for (auto &worker : workers)
    worker.join();
  IOTOX_CHECK(failures.load(std::memory_order_relaxed) == 0U);
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->generation == 8U);
}

IOTOX_TEST("signed sync HEAD publisher lock rejects weak or linked state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root, {writer.public_key()});
  SignedHeadStore store(root);
  IOTOX_CHECK(store.publish(configured, request(80U), writer, crypto).ok());
  const std::filesystem::path lock =
      root / "transactions" / "field-notes.transaction.lock";

  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!store.publish(configured, request(81U), writer, crypto).ok());
  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);
  const std::filesystem::path alias = lock.parent_path() / "lock-alias";
  std::filesystem::create_hard_link(lock, alias);
  IOTOX_CHECK(!store.publish(configured, request(81U), writer, crypto).ok());
  std::filesystem::remove(alias);
  auto second = store.publish(configured, request(81U), writer, crypto);
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(second.value().head.generation == 2U);
}
