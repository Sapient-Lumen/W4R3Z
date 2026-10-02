#include "test_harness.hpp"

#include "iotox/sync_gc.hpp"
#include "iotox/sync_publication.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::Status;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::SignedHeadPublicationRequest;
using iotox::sync::SignedHeadStore;
using iotox::sync::SyncGcSeams;
using iotox::sync::SyncObjectKind;
using iotox::sync::SyncObjectRecord;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-gc-XXXXXX";
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
  result.id = "gc-fixture";
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

SyncObjectRecord artifact(std::uint8_t value, std::uint64_t bytes) {
  return SyncObjectRecord{SyncObjectKind::artifact, digest(value), bytes};
}

std::filesystem::path write_object(const NamespacePolicy &configured,
                                   const SyncObjectRecord &object,
                                   char fill = 'x') {
  const std::filesystem::path root{configured.root};
  const std::filesystem::path directory = root / "objects";
  std::filesystem::create_directories(directory);
  std::filesystem::permissions(root, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace);
  std::filesystem::permissions(directory, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace);
  const std::filesystem::path path =
      iotox::sync::sync_object_path(configured, object);
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  std::vector<char> bytes(static_cast<std::size_t>(object.bytes), fill);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  output.close();
  std::filesystem::permissions(path,
                               std::filesystem::perms::owner_read |
                                   std::filesystem::perms::owner_write,
                               std::filesystem::perm_options::replace);
  return path;
}

void write_text(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output << text;
}

std::string read_text(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  const auto bytes = std::filesystem::file_size(path);
  std::string result(static_cast<std::size_t>(bytes), '\0');
  input.read(result.data(), static_cast<std::streamsize>(result.size()));
  return result;
}

} // namespace

IOTOX_TEST("sync GC dry run freezes identities and quarantine never purges") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  const SyncObjectRecord unused = artifact(9U, 73U);
  const std::filesystem::path source = write_object(configured, unused);
  const std::filesystem::path sentinel = temporary.path() / "outside-sentinel";
  write_text(sentinel, "outside-is-untouched\n");

  auto plan = iotox::sync::plan_sync_gc_quarantine(configured,
                                                   device.public_key(), crypto);
  IOTOX_CHECK(plan.ok());
  IOTOX_CHECK(plan.value().descriptor_pinned);
  IOTOX_CHECK(plan.value().reachability.consistent());
  IOTOX_CHECK(plan.value().inventory.size() == 1U);
  IOTOX_CHECK(plan.value().candidates.size() == 1U);
  IOTOX_CHECK(plan.value().candidates[0U].object == unused);
  IOTOX_CHECK(plan.value().candidates[0U].inode != 0U);
  IOTOX_CHECK(std::filesystem::exists(source));
  IOTOX_CHECK(!std::filesystem::exists(std::filesystem::path(configured.root) /
                                       "gc-quarantine"));

  auto quarantined = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(quarantined.ok());
  IOTOX_CHECK(quarantined.quarantine_created);
  IOTOX_CHECK(quarantined.moved == std::vector<SyncObjectRecord>{unused});
  IOTOX_CHECK(quarantined.moved_bytes == unused.bytes);
  IOTOX_CHECK(quarantined.durable_objects == 1U);
  IOTOX_CHECK(quarantined.durable_bytes == unused.bytes);
  IOTOX_CHECK(!std::filesystem::exists(source));
  IOTOX_CHECK(std::filesystem::exists(std::filesystem::path(configured.root) /
                                      "gc-quarantine" / source.filename()));
  IOTOX_CHECK(read_text(sentinel) == "outside-is-untouched\n");

  auto repeated = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(repeated.ok());
  IOTOX_CHECK(repeated.moved.empty());
  IOTOX_CHECK(std::filesystem::exists(std::filesystem::path(configured.root) /
                                      "gc-quarantine" / source.filename()));
}

IOTOX_TEST("sync GC refuses inconsistent live roots before mutation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  SignedHeadStore publisher(configured.root);
  SignedHeadPublicationRequest request{digest(1U), digest(33U), 101U, 21U};
  IOTOX_CHECK(publisher.publish(configured, request, device, crypto).ok());
  const SyncObjectRecord unused = artifact(9U, 73U);
  const std::filesystem::path source = write_object(configured, unused);

  auto outcome = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(!outcome.ok());
  IOTOX_CHECK(outcome.status.code() == ErrorCode::protocol_error);
  IOTOX_CHECK(outcome.plan.has_value());
  IOTOX_CHECK(!outcome.plan->reachability.consistent());
  IOTOX_CHECK(outcome.moved.empty());
  IOTOX_CHECK(std::filesystem::exists(source));
  IOTOX_CHECK(!std::filesystem::exists(std::filesystem::path(configured.root) /
                                       "gc-quarantine"));
}

IOTOX_TEST("sync GC rejects hard links and symlinks during dry run") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);

  NamespacePolicy linked = policy(temporary.path() / "linked", device);
  const std::filesystem::path linked_source =
      write_object(linked, artifact(4U, 40U));
  std::filesystem::create_hard_link(linked_source,
                                    temporary.path() / "outside-hardlink");
  auto hardlink_plan =
      iotox::sync::plan_sync_gc_quarantine(linked, device.public_key(), crypto);
  IOTOX_CHECK(!hardlink_plan.ok());
  IOTOX_CHECK(hardlink_plan.status().code() == ErrorCode::protocol_error);

  NamespacePolicy symlinked = policy(temporary.path() / "symlinked", device);
  static_cast<void>(write_object(symlinked, artifact(5U, 41U)));
  std::filesystem::create_symlink(temporary.path() / "outside-hardlink",
                                  std::filesystem::path(symlinked.root) /
                                      "objects" / "unexpected-link");
  auto symlink_plan = iotox::sync::plan_sync_gc_quarantine(
      symlinked, device.public_key(), crypto);
  IOTOX_CHECK(!symlink_plan.ok());
  IOTOX_CHECK(symlink_plan.status().code() == ErrorCode::protocol_error);
}

IOTOX_TEST("sync GC refuses inode substitution immediately before rename") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  const SyncObjectRecord unused = artifact(6U, 64U);
  const std::filesystem::path source = write_object(configured, unused, 'a');
  const std::filesystem::path replacement = temporary.path() / "replacement";
  write_text(replacement, std::string(64U, 'b'));
  std::filesystem::permissions(replacement,
                               std::filesystem::perms::owner_read |
                                   std::filesystem::perms::owner_write,
                               std::filesystem::perm_options::replace);
  SyncGcSeams seams;
  seams.before_move = [&](std::size_t, const auto &) {
    std::error_code error;
    std::filesystem::rename(replacement, source, error);
    return error ? Status{ErrorCode::io_error, error.message()}
                 : Status::success();
  };
  auto outcome = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto, seams);
  IOTOX_CHECK(!outcome.ok());
  IOTOX_CHECK(outcome.status.code() == ErrorCode::protocol_error);
  IOTOX_CHECK(outcome.moved.empty());
  IOTOX_CHECK(std::filesystem::exists(source));
}

IOTOX_TEST("sync GC cancellation reports an exact durable prefix") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  static_cast<void>(write_object(configured, artifact(7U, 70U)));
  static_cast<void>(write_object(configured, artifact(8U, 80U)));
  std::uint64_t checks = 0U;
  SyncGcSeams seams;
  seams.cancel_requested = [&] { return ++checks == 3U; };
  auto outcome = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto, seams);
  IOTOX_CHECK(!outcome.ok());
  IOTOX_CHECK(outcome.cancelled);
  IOTOX_CHECK(outcome.status.code() == ErrorCode::unavailable);
  IOTOX_CHECK(outcome.plan.has_value());
  IOTOX_CHECK(outcome.plan->candidates.size() == 2U);
  IOTOX_CHECK(outcome.moved.size() == 1U);
  IOTOX_CHECK(outcome.durable_objects == 1U);
  IOTOX_CHECK(outcome.durable_bytes == outcome.moved_bytes);
}

IOTOX_TEST("sync GC fsync failure distinguishes moved from durable") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync", device);
  const SyncObjectRecord unused = artifact(10U, 90U);
  const std::filesystem::path source = write_object(configured, unused);
  std::uint64_t synchronizations = 0U;
  SyncGcSeams seams;
  seams.sync_directory = [&](int) {
    ++synchronizations;
    if (synchronizations == 2U) {
      return Status{ErrorCode::io_error,
                    "injected post-rename directory sync failure"};
    }
    return Status::success();
  };
  auto outcome = iotox::sync::quarantine_unreferenced_sync_objects(
      configured, device.public_key(), crypto, seams);
  IOTOX_CHECK(!outcome.ok());
  IOTOX_CHECK(outcome.status.code() == ErrorCode::io_error);
  IOTOX_CHECK(outcome.moved == std::vector<SyncObjectRecord>{unused});
  IOTOX_CHECK(outcome.moved_bytes == unused.bytes);
  IOTOX_CHECK(outcome.durable_objects == 0U);
  IOTOX_CHECK(outcome.durable_bytes == 0U);
  IOTOX_CHECK(!std::filesystem::exists(source));
}
