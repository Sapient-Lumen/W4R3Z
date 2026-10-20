#include "iotox/sync_content_publication.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_replica.hpp"

#include "test_harness.hpp"

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

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-content-publish-XXXXXX";
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

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity
identity(const std::filesystem::path &path,
         const iotox::security::Sodium &crypto) {
  auto loaded =
      iotox::security::DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::sync::PrincipalId principal(std::uint8_t value) {
  iotox::sync::PrincipalId result{};
  result[0U] = value;
  return result;
}

iotox::sync::NamespacePolicy
policy(const std::filesystem::path &root,
       const iotox::security::SigningPublicKey &writer) {
  iotox::sync::NamespacePolicy result;
  result.id = "content-publish-test";
  result.root = root.lexically_normal().string();
  result.engine = iotox::sync::Engine::content_v2;
  result.activation = iotox::sync::ActivationMode::manual;
  result.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_staging_bytes = 4U * 1024U * 1024U;
  result.quotas.maximum_store_bytes = 16U * 1024U * 1024U;
  result.quotas.maximum_objects = 1024U;
  result.quotas.maximum_retained_revisions = 4U;
  result.quotas.maximum_peers = 4U;
  result.quotas.maximum_lanes = 4U;
  result.quotas.maximum_outstanding_requests = 16U;
  result.writers = {writer};
  result.subscribers = {principal(0x42U)};
  return result;
}

void write_pattern(const std::filesystem::path &path, std::size_t bytes,
                   std::uint8_t salt = 0U) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  std::uint64_t state = 0x9e3779b97f4a7c15ULL ^ salt;
  for (std::size_t index = 0U; index < bytes; ++index) {
    state ^= state << 13U;
    state ^= state >> 7U;
    state ^= state << 17U;
    output.put(static_cast<char>(state & 0xffU));
  }
  if (!output)
    throw std::runtime_error("pattern write failed");
}

iotox::sync::SyncContentPublicationConfig
config(iotox::sync::SyncContentPublicationFormat format) {
  iotox::sync::SyncContentPublicationConfig result;
  result.format = format;
  result.minimum_chunk_bytes = 4096U;
  result.average_chunk_bytes = 8192U;
  result.maximum_chunk_bytes = 16384U;
  result.entries_per_page = 4U;
  result.io_buffer_bytes = 4096U;
  result.manifest_buffer_bytes = 4096U;
  result.workspace_budget_bytes = 1024U * 1024U;
  result.fsync_on_commit = false;
  return result;
}

bool inventory_contains(const iotox::sync::SyncContentStoreInventory &inventory,
                        const iotox::sync::Digest &digest,
                        std::uint64_t bytes) {
  return std::any_of(inventory.records.begin(), inventory.records.end(),
                     [&](const iotox::sync::SyncContentStoredObject &record) {
                       return record.object == digest &&
                              record.object_bytes == bytes;
                     });
}

} // namespace

IOTOX_TEST("content publication imports flat CAS and signs HEAD last") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 512U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto published = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(published.value().format ==
              iotox::sync::SyncContentPublicationFormat::flat);
  IOTOX_CHECK(published.value().publication.head.engine ==
              iotox::sync::Engine::content_v2);
  IOTOX_CHECK(published.value().publication.head.generation == 1U);
  IOTOX_CHECK(published.value().chunks > 1U && published.value().pages == 0U);
  IOTOX_CHECK(published.value().objects_installed ==
              published.value().unique_objects);
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto inventory = iotox::sync::inspect_sync_content_store(
        configured, transaction.value(), true);
    IOTOX_CHECK(inventory.ok());
    IOTOX_CHECK(inventory.value().objects == published.value().unique_objects);
    IOTOX_CHECK(inventory_contains(inventory.value(),
                                   published.value().manifest,
                                   published.value().manifest_bytes));
  }
  auto first = iotox::sync::resolve_sync_content_object(
      configured, published.value().publication.head,
      iotox::sync::SyncContentObjectKind::artifact_chunk, 0U);
  IOTOX_CHECK(first.ok() && first.value().object_bytes != 0U);
  auto duplicate = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK(duplicate.ok() && duplicate.value().publication.duplicate);
  IOTOX_CHECK(duplicate.value().publication.head.generation == 1U);
  IOTOX_CHECK(duplicate.value().objects_installed == 0U);
  IOTOX_CHECK(duplicate.value().objects_reused ==
              duplicate.value().unique_objects);
}

IOTOX_TEST("content publication imports paged metadata and advances exactly") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 768U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto first = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::paged));
  IOTOX_CHECK_MSG(first.ok(), first.status().message());
  IOTOX_CHECK(first.value().format ==
              iotox::sync::SyncContentPublicationFormat::paged);
  IOTOX_CHECK(first.value().chunks > 4U && first.value().pages > 1U);
  auto page = iotox::sync::resolve_sync_content_object(
      configured, first.value().publication.head,
      iotox::sync::SyncContentObjectKind::manifest_page, 0U);
  IOTOX_CHECK(page.ok() && page.value().object_bytes != 0U);

  write_pattern(source, 768U * 1024U, 0x5aU);
  auto second = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::paged));
  IOTOX_CHECK_MSG(second.ok(), second.status().message());
  IOTOX_CHECK(!second.value().publication.duplicate);
  IOTOX_CHECK(second.value().publication.head.generation == 2U);
  IOTOX_CHECK(second.value().publication.head.parent ==
              first.value().publication.record);
}

IOTOX_TEST("content publication refuses whole-set quota before CAS or HEAD") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto configured = policy(temporary.path() / "namespace", device.public_key());
  configured.quotas.maximum_artifact_bytes = 64U * 1024U;
  configured.quotas.maximum_manifest_bytes = 16U * 1024U;
  configured.quotas.maximum_staging_bytes = 64U * 1024U;
  configured.quotas.maximum_store_bytes = 64U * 1024U;
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 64U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto refused = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK_MSG(refused.status().code() ==
                      iotox::ErrorCode::resource_exhausted,
                  refused.status().message());
  auto head = heads.load(configured, crypto);
  IOTOX_CHECK(head.ok() && !head.value().has_value());
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto inventory = iotox::sync::inspect_sync_content_store(
      configured, transaction.value(), true);
  IOTOX_CHECK(inventory.ok() && inventory.value().objects == 0U);
}

IOTOX_TEST("content publication refuses an unauthorized local writer before "
           "mutation") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto other = identity(temporary.path() / "other.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", other.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 64U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto refused = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK_MSG(refused.status().code() == iotox::ErrorCode::invalid_argument,
                  refused.status().message());
  IOTOX_CHECK(!std::filesystem::exists(configured.root));
}

IOTOX_TEST(
    "content publication refuses an impossible workspace before mutation") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 64U * 1024U);
  auto bounded = config(iotox::sync::SyncContentPublicationFormat::paged);
  bounded.workspace_budget_bytes = 8U * 1024U;
  iotox::sync::SignedHeadStore heads(configured.root);
  auto refused = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads, bounded);
  IOTOX_CHECK_MSG(refused.status().code() ==
                      iotox::ErrorCode::resource_exhausted,
                  refused.status().message());
  IOTOX_CHECK(!std::filesystem::exists(configured.root));
}

IOTOX_TEST(
    "content publication cancellation may retain CAS but never signs HEAD") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 512U * 1024U);
  std::size_t cancellation_checks = 0U;
  iotox::sync::SyncContentPublicationSeams seams;
  seams.cancel_requested = [&cancellation_checks] {
    ++cancellation_checks;
    return cancellation_checks == 4U;
  };
  iotox::sync::SignedHeadStore heads(configured.root);
  auto cancelled = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat),
      std::move(seams));
  IOTOX_CHECK_MSG(cancelled.status().code() == iotox::ErrorCode::unavailable,
                  cancelled.status().message());
  auto head = heads.load(configured, crypto);
  IOTOX_CHECK(head.ok() && !head.value().has_value());
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto inventory = iotox::sync::inspect_sync_content_store(
      configured, transaction.value(), true);
  IOTOX_CHECK(inventory.ok());
  IOTOX_CHECK(inventory.value().objects == 1U);
}

IOTOX_TEST("content publication cleanup is exact and refuses foreign entries") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  const auto parent =
      iotox::sync::sync_content_staging_root(configured) / "publications";
  std::filesystem::create_directory(parent);
  IOTOX_CHECK(::chmod(parent.c_str(), static_cast<mode_t>(0700)) == 0);
  const auto abandoned = parent / "local-0123456789abcdef";
  std::filesystem::create_directory(abandoned);
  IOTOX_CHECK(::chmod(abandoned.c_str(), static_cast<mode_t>(0700)) == 0);
  write_pattern(abandoned / "partial", 1024U);
  auto cleaned = iotox::sync::cleanup_sync_content_publication_staging(
      configured, transaction.value());
  IOTOX_CHECK(cleaned.ok() && cleaned.value() == 1U);
  IOTOX_CHECK(!std::filesystem::exists(abandoned));
  const auto foreign = parent / "unexpected";
  std::filesystem::create_directory(foreign);
  IOTOX_CHECK(::chmod(foreign.c_str(), static_cast<mode_t>(0700)) == 0);
  IOTOX_CHECK(!iotox::sync::cleanup_sync_content_publication_staging(
                   configured, transaction.value())
                   .ok());
  IOTOX_CHECK(std::filesystem::exists(foreign));
}

IOTOX_TEST("content reachability walks paged roots and quarantines only "
           "unreferenced CAS") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 768U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto published = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::paged));
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  auto clean = iotox::sync::plan_sync_content_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK_MSG(clean.ok(), clean.status().message());
  IOTOX_CHECK(clean.value().consistent());
  IOTOX_CHECK(clean.value().unreferenced.empty());
  IOTOX_CHECK(clean.value().rooted.size() == published.value().unique_objects);

  const auto extra_source = temporary.path() / "extra.bin";
  write_pattern(extra_source, 8193U, 0x66U);
  auto extra_digest = iotox::sync::hash_sync_file_sha256(extra_source);
  IOTOX_CHECK(extra_digest.ok());
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::prepare_sync_content_staging(configured,
                                                          transaction.value())
                    .ok());
    const auto staged =
        iotox::sync::sync_content_staging_root(configured) / "extra.part";
    IOTOX_CHECK(std::filesystem::copy_file(extra_source, staged));
    IOTOX_CHECK(::chmod(staged.c_str(), static_cast<mode_t>(0600)) == 0);
    iotox::sync::SyncContentCommitConfig commit;
    commit.fsync_on_commit = false;
    auto installed = iotox::sync::commit_sync_content_staging(
        configured, extra_digest.value(), std::filesystem::file_size(staged),
        staged, transaction.value(), commit);
    IOTOX_CHECK_MSG(installed.ok(), installed.status().message());
  }
  auto with_extra = iotox::sync::plan_sync_content_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK_MSG(with_extra.ok(), with_extra.status().message());
  IOTOX_CHECK(with_extra.value().consistent());
  IOTOX_CHECK(with_extra.value().unreferenced.size() == 1U);
  IOTOX_CHECK(with_extra.value().unreferenced.front().object ==
              extra_digest.value());

  auto quarantined = iotox::sync::quarantine_unreferenced_sync_content(
      configured, device.public_key(), crypto);
  IOTOX_CHECK_MSG(quarantined.ok(), quarantined.status.message());
  IOTOX_CHECK(quarantined.moved.size() == 1U);
  IOTOX_CHECK(quarantined.durable_objects == 1U);
  IOTOX_CHECK(!std::filesystem::exists(
      iotox::sync::sync_content_object_path(configured, extra_digest.value())));
  clean = iotox::sync::plan_sync_content_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(clean.ok() && clean.value().consistent());
  IOTOX_CHECK(clean.value().unreferenced.empty());

  auto first_page = iotox::sync::resolve_sync_content_object(
      configured, published.value().publication.head,
      iotox::sync::SyncContentObjectKind::manifest_page, 0U);
  IOTOX_CHECK(first_page.ok());
  const auto held_page = temporary.path() / "held-page";
  std::filesystem::rename(first_page.value().path, held_page);
  auto incomplete = iotox::sync::plan_sync_content_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(incomplete.ok());
  IOTOX_CHECK(!incomplete.value().traversal_complete);
  IOTOX_CHECK(incomplete.value().unreferenced.empty());
  auto refused = iotox::sync::quarantine_unreferenced_sync_content(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status.code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST(
    "content repair quarantines digest drift without touching rooted bytes") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", device.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 256U * 1024U);
  iotox::sync::SignedHeadStore heads(configured.root);
  auto published = iotox::sync::publish_local_content_revision(
      configured, source, device, crypto, heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK_MSG(published.ok(), published.status().message());

  const auto corrupt_source = temporary.path() / "corrupt-source.bin";
  write_pattern(corrupt_source, 12289U, 0x99U);
  auto expected = iotox::sync::hash_sync_file_sha256(corrupt_source);
  IOTOX_CHECK(expected.ok());
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::prepare_sync_content_staging(configured,
                                                          transaction.value())
                    .ok());
    const auto staged =
        iotox::sync::sync_content_staging_root(configured) / "corrupt.part";
    IOTOX_CHECK(std::filesystem::copy_file(corrupt_source, staged));
    IOTOX_CHECK(::chmod(staged.c_str(), static_cast<mode_t>(0600)) == 0);
    iotox::sync::SyncContentCommitConfig commit;
    commit.fsync_on_commit = false;
    auto installed = iotox::sync::commit_sync_content_staging(
        configured, expected.value(), std::filesystem::file_size(staged),
        staged, transaction.value(), commit);
    IOTOX_CHECK(installed.ok());
  }
  const auto corrupt_path =
      iotox::sync::sync_content_object_path(configured, expected.value());
  std::fstream corrupt(corrupt_path,
                       std::ios::binary | std::ios::in | std::ios::out);
  char byte = 0;
  corrupt.read(&byte, 1);
  IOTOX_CHECK(static_cast<bool>(corrupt));
  byte = static_cast<char>(static_cast<unsigned char>(byte) ^ 0x5aU);
  corrupt.seekp(0);
  corrupt.write(&byte, 1);
  corrupt.close();
  auto repaired = iotox::sync::repair_sync_content_store(configured);
  IOTOX_CHECK_MSG(repaired.ok(), repaired.status().message());
  IOTOX_CHECK(repaired.value().quarantined_objects == 1U);
  IOTOX_CHECK(repaired.value().quarantined.front().object == expected.value());
  IOTOX_CHECK(!std::filesystem::exists(corrupt_path));
  auto clean = iotox::sync::plan_sync_content_reachability_from_store(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(clean.ok() && clean.value().consistent());
  IOTOX_CHECK(clean.value().unreferenced.empty());
}

IOTOX_TEST(
    "partial replica graph survives restart planning without publication authority") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto remote =
      policy(temporary.path() / "remote-namespace", writer.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 512U * 1024U, 0x81U);
  iotox::sync::SignedHeadStore remote_heads(remote.root);
  auto published = iotox::sync::publish_local_content_revision(
      remote, source, writer, crypto, remote_heads,
      config(iotox::sync::SyncContentPublicationFormat::flat));
  IOTOX_CHECK_MSG(published.ok(), published.status().message());

  auto local = policy(temporary.path() / "local-namespace",
                      writer.public_key());
  std::filesystem::create_directory(local.root);
  IOTOX_CHECK(::chmod(local.root.c_str(), static_cast<mode_t>(0700)) == 0);
  std::filesystem::copy(
      std::filesystem::path(remote.root) / "content-v2",
      std::filesystem::path(local.root) / "content-v2",
      std::filesystem::copy_options::recursive);
  IOTOX_CHECK(!std::filesystem::exists(
      std::filesystem::path(local.root) / "published-heads"));

  auto missing_chunk = iotox::sync::resolve_sync_content_object(
      local, published.value().publication.head,
      iotox::sync::SyncContentObjectKind::artifact_chunk, 0U);
  IOTOX_CHECK_MSG(missing_chunk.ok(), missing_chunk.status().message());
  IOTOX_CHECK(std::filesystem::remove(missing_chunk.value().path));

  iotox::sync::ReplicaHeadStore replicas(local.root);
  auto imported = replicas.import_head(
      local, published.value().publication.head, device, crypto);
  IOTOX_CHECK_MSG(imported.ok(), imported.status().message());
  const auto &head = published.value().publication.head;
  iotox::sync::AcceptedHead expected{
      head.namespace_id, head.writer, head.engine, head.generation,
      imported.value().record, head.parent, head.artifact, head.manifest,
      head.artifact_bytes, head.manifest_bytes};
  iotox::sync::SyncContentCoordinator restarted(
      local, expected,
      iotox::sync::sync_content_object_path(local, head.manifest),
      iotox::sync::sync_content_store_root(local),
      iotox::sync::sync_content_staging_root(local));
  const iotox::Status prepared = restarted.prepare();
  IOTOX_CHECK_MSG(prepared.ok(), prepared.message());

  auto plan = iotox::sync::plan_sync_content_reachability_from_store(
      local, device.public_key(), crypto);
  IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
  IOTOX_CHECK(plan.value().consistent());
  IOTOX_CHECK(plan.value().traversal_complete);
  IOTOX_CHECK(plan.value().missing.empty());
  IOTOX_CHECK(plan.value().unreferenced.empty());
  IOTOX_CHECK(!plan.value().rooted.empty());
  IOTOX_CHECK(std::all_of(
      plan.value().rooted.begin(), plan.value().rooted.end(),
      [](const iotox::sync::SyncContentRootedObject &root) {
        return (root.source_mask &
                static_cast<std::uint8_t>(
                    iotox::sync::SyncContentRootSource::replica)) != 0U;
      }));
  IOTOX_CHECK(!std::filesystem::exists(missing_chunk.value().path));
}
