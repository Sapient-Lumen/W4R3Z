#include "test_harness.hpp"

#include "iotox/sync_replica.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::SigningPublicKey;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::ReplicaHeadImportDecision;
using iotox::sync::ReplicaHeadStore;
using iotox::sync::SignedHead;
using iotox::sync::SignedHeadPublicationRequest;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-replica-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
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
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
  auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
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
  result.id = "replica-test";
  result.root = root.lexically_normal().string();
  result.engine = Engine::content_v2;
  result.writers = std::move(writers);
  result.quotas.maximum_artifact_bytes = 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_staging_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_store_bytes = 4U * 1024U * 1024U;
  result.quotas.maximum_objects = 1024U;
  result.quotas.maximum_peers = 4U;
  result.quotas.maximum_lanes = 4U;
  result.quotas.maximum_outstanding_requests = 16U;
  return result;
}

SignedHeadPublicationRequest request(std::uint8_t value) {
  SignedHeadPublicationRequest result;
  result.artifact = digest(value);
  result.manifest = digest(static_cast<std::uint8_t>(value + 64U));
  result.artifact_bytes = 1000U + value;
  result.manifest_bytes = 100U + value;
  return result;
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return {std::istreambuf_iterator<char>(input),
          std::istreambuf_iterator<char>()};
}

void write_bytes(const std::filesystem::path &path,
                 const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("fixture write failed");
}

} // namespace

IOTOX_TEST("replica HEAD is foreign-authorized and locally authenticated") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", {writer.public_key()});
  auto head = iotox::sync::create_signed_head(configured, request(1U),
                                              std::nullopt, writer, crypto);
  IOTOX_CHECK(head.ok());

  ReplicaHeadStore replicas(configured.root);
  auto imported =
      replicas.import_head(configured, head.value(), device, crypto);
  IOTOX_CHECK_MSG(imported.ok(), imported.status().message());
  IOTOX_CHECK(imported.value().decision == ReplicaHeadImportDecision::imported);
  IOTOX_CHECK(!std::filesystem::exists(std::filesystem::path(configured.root) /
                                       "published-heads"));

  auto loaded = replicas.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value() == head.value());
  auto duplicate =
      replicas.import_head(configured, head.value(), device, crypto);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().decision ==
              ReplicaHeadImportDecision::duplicate);

  auto wrong_device =
      identity(temporary.path() / "wrong-device.identity", crypto);
  IOTOX_CHECK(
      !replicas.load(configured, wrong_device.public_key(), crypto).ok());

  const auto path = std::filesystem::path(configured.root) / "replica-heads" /
                    "replica-test.replica-head";
  auto encoded = read_bytes(path);
  IOTOX_CHECK(!encoded.empty());
  auto decoded = iotox::sync::decode_replica_head(encoded);
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value().custodian == device.public_key());
  IOTOX_CHECK(decoded.value().head == head.value());
  encoded.back() ^= 0x01U;
  write_bytes(path, encoded);
  IOTOX_CHECK(!replicas.load(configured, device.public_key(), crypto).ok());
  encoded.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_replica_head(encoded).ok());
}

IOTOX_TEST(
    "replica HEAD advances only through one exact foreign writer chain") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  auto other = identity(temporary.path() / "other.identity", crypto);
  auto configured =
      policy(temporary.path() / "namespace",
             {device.public_key(), writer.public_key(), other.public_key()});
  auto first = iotox::sync::create_signed_head(configured, request(1U),
                                               std::nullopt, writer, crypto);
  IOTOX_CHECK(first.ok());
  auto second = iotox::sync::create_signed_head(configured, request(2U),
                                                first.value(), writer, crypto);
  IOTOX_CHECK(second.ok());
  auto fork = iotox::sync::create_signed_head(configured, request(3U),
                                              first.value(), writer, crypto);
  IOTOX_CHECK(fork.ok());
  auto other_head = iotox::sync::create_signed_head(
      configured, request(4U), std::nullopt, other, crypto);
  IOTOX_CHECK(other_head.ok());
  auto local_head = iotox::sync::create_signed_head(
      configured, request(5U), std::nullopt, device, crypto);
  IOTOX_CHECK(local_head.ok());

  ReplicaHeadStore replicas(configured.root);
  IOTOX_CHECK(
      replicas.import_head(configured, first.value(), device, crypto).ok());
  auto advanced =
      replicas.import_head(configured, second.value(), device, crypto);
  IOTOX_CHECK_MSG(advanced.ok(), advanced.status().message());
  IOTOX_CHECK(advanced.value().decision == ReplicaHeadImportDecision::advanced);
  IOTOX_CHECK(
      !replicas.import_head(configured, first.value(), device, crypto).ok());
  IOTOX_CHECK(
      !replicas.import_head(configured, fork.value(), device, crypto).ok());
  IOTOX_CHECK(
      !replicas.import_head(configured, other_head.value(), device, crypto)
           .ok());
  IOTOX_CHECK(
      !replicas.import_head(configured, local_head.value(), device, crypto)
           .ok());
  auto loaded = replicas.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value() == second.value());
}

IOTOX_TEST("replica HEAD store refuses a symlinked custody directory") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", {writer.public_key()});
  auto head = iotox::sync::create_signed_head(configured, request(1U),
                                              std::nullopt, writer, crypto);
  IOTOX_CHECK(head.ok());
  std::filesystem::create_directory(configured.root);
  IOTOX_CHECK(::chmod(configured.root.c_str(), static_cast<mode_t>(0700)) == 0);
  std::filesystem::create_directory(temporary.path() / "outside");
  std::filesystem::create_directory_symlink(
      temporary.path() / "outside",
      std::filesystem::path(configured.root) / "replica-heads");

  ReplicaHeadStore replicas(configured.root);
  IOTOX_CHECK(
      !replicas.import_head(configured, head.value(), device, crypto).ok());
  IOTOX_CHECK(std::filesystem::is_empty(temporary.path() / "outside"));
}
