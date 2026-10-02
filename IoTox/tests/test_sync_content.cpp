#include "iotox/sync_content.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_job.hpp"

#include "test_harness.hpp"

#include "toxsync/content_store.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-content-XXXXXX";
    std::vector<char> storage(pattern.begin(), pattern.end());
    storage.push_back('\0');
    char *created = ::mkdtemp(storage.data());
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

iotox::sync::PrincipalId principal(std::uint8_t value) {
  iotox::sync::PrincipalId result{};
  result[0U] = value;
  return result;
}

iotox::sync::Digest from_toxsync(const toxsync::Digest256 &digest) {
  iotox::sync::Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    result[index] = std::to_integer<std::uint8_t>(digest.bytes[index]);
  }
  return result;
}

toxsync::Digest256 to_toxsync(const iotox::sync::Digest &digest) {
  toxsync::Digest256 result;
  for (std::size_t index = 0U; index < digest.size(); ++index) {
    result.bytes[index] = static_cast<std::byte>(digest[index]);
  }
  return result;
}

iotox::security::AuthoritySnapshot authority() {
  iotox::security::AuthoritySnapshot result;
  result.initialized = true;
  result.format = iotox::security::AuthorityLedgerFormat::v3;
  result.ownership_epoch = 7U;
  result.sequence = 19U;
  result.tail_digest[0U] = 42U;
  return result;
}

iotox::security::PeerAuthoritySnapshot
peer(const iotox::security::AuthoritySnapshot &current,
     const iotox::sync::PrincipalId &remote) {
  iotox::security::PeerAuthoritySnapshot result;
  result.connected = true;
  result.feature_negotiated = true;
  result.authority_v2_negotiated = true;
  result.authority_v3_negotiated = true;
  result.verifier_state = iotox::security::AuthorityVerifierState::authorized;
  result.remote_authorized = true;
  result.remote_principal = remote;
  result.remote_capabilities =
      static_cast<std::uint64_t>(iotox::security::Capability::sync_publish);
  result.local_authority_format = current.format;
  result.local_authority_epoch = current.ownership_epoch;
  result.local_authority_sequence = current.sequence;
  result.local_authority_tail_digest = current.tail_digest;
  return result;
}

void write_pattern_file(const std::filesystem::path &path,
                        std::uint64_t bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  for (std::uint64_t index = 0U; index < bytes; ++index) {
    const char byte =
        static_cast<char>((index * 131U + index / 97U + 17U) & 0xffU);
    output.put(byte);
  }
  if (!output)
    throw std::runtime_error("artifact fixture write failed");
  output.close();
  if (::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0) {
    throw std::runtime_error("artifact fixture chmod failed");
  }
}

void write_artifact(const std::filesystem::path &path) {
  write_pattern_file(path, 768U * 1024U + 137U);
}

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root) {
  iotox::sync::NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = iotox::sync::Engine::content_v2;
  result.activation = iotox::sync::ActivationMode::manual;
  result.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_store_bytes = 8U * 1024U * 1024U;
  result.quotas.maximum_staging_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_objects = 512U;
  result.quotas.maximum_peers = 4U;
  result.quotas.maximum_lanes = 2U;
  result.quotas.maximum_outstanding_requests = 8U;
  result.writers = {principal(1U), principal(3U)};
  result.subscribers = {principal(2U)};
  return result;
}

iotox::sync::AcceptedHead
accepted_head(const iotox::sync::NamespacePolicy &configured,
              const toxsync::ContentStoreBuildStats &built,
              const std::filesystem::path &manifest) {
  iotox::sync::AcceptedHead result;
  result.namespace_id = configured.id;
  result.writer = principal(1U);
  result.engine = configured.engine;
  result.generation = 1U;
  result.record[0U] = 91U;
  result.artifact = from_toxsync(built.metadata.artifact_digest);
  result.manifest = from_toxsync(built.metadata.manifest_digest);
  result.artifact_bytes = built.metadata.artifact_size;
  result.manifest_bytes = std::filesystem::file_size(manifest);
  return result;
}

iotox::sync::AcceptedHead
accepted_head(const iotox::sync::NamespacePolicy &configured,
              const toxsync::PagedContentStoreBuildStats &built,
              const std::filesystem::path &manifest) {
  iotox::sync::AcceptedHead result;
  result.namespace_id = configured.id;
  result.writer = principal(1U);
  result.engine = configured.engine;
  result.generation = 1U;
  result.record[0U] = 92U;
  result.artifact = from_toxsync(built.metadata.artifact_digest);
  result.manifest = from_toxsync(built.metadata.root_digest);
  result.artifact_bytes = built.metadata.artifact_size;
  result.manifest_bytes = std::filesystem::file_size(manifest);
  return result;
}

iotox::sync::SyncContentSource
source(std::uint64_t source_id, std::uint8_t principal_id,
       const iotox::sync::AcceptedHead &head,
       const iotox::security::AuthoritySnapshot &current) {
  iotox::sync::SyncContentSource result;
  result.source_id = source_id;
  result.advertised_head_record = head.record;
  result.authority = peer(current, principal(principal_id));
  result.maximum_lanes = 1U;
  result.useful_bytes_per_second =
      (principal_id == 1U ? 8U : 4U) * 1024U * 1024U;
  result.content_transfer_negotiated = true;
  return result;
}

void copy_remote_object(const std::filesystem::path &remote_store,
                        const iotox::sync::SyncContentAssignment &assignment) {
  const std::filesystem::path remote =
      toxsync::content_store_path(remote_store, to_toxsync(assignment.object));
  std::filesystem::create_directories(assignment.staging_path.parent_path());
  std::filesystem::copy_file(remote, assignment.staging_path,
                             std::filesystem::copy_options::none);
}

} // namespace

IOTOX_TEST("content coordinator stripes exact objects and survives source "
           "disappearance") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto remote_manifest = temporary.path() / "remote.txc";
  write_artifact(artifact);

  toxsync::ContentStoreOptions build_options;
  build_options.chunking = {4096U, 8192U, 16384U};
  build_options.io_buffer_bytes = 8192U;
  build_options.manifest_buffer_bytes = 4096U;
  build_options.fsync_on_commit = false;
  const toxsync::ContentStoreBuildStats built = toxsync::build_content_store(
      artifact, remote_store, remote_manifest, build_options);
  const iotox::sync::AcceptedHead expected =
      accepted_head(configured, built, remote_manifest);
  std::filesystem::path local_manifest;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::prepare_sync_content_staging(configured,
                                                          transaction.value())
                    .ok());
    const auto staged_manifest =
        iotox::sync::sync_content_staging_root(configured) /
        "root-manifest.part";
    std::filesystem::copy_file(remote_manifest, staged_manifest);
    IOTOX_CHECK(::chmod(staged_manifest.c_str(), static_cast<mode_t>(0600)) ==
                0);
    iotox::sync::SyncContentCommitConfig commit_config;
    commit_config.io_buffer_bytes = 4096U;
    commit_config.fsync_on_commit = false;
    auto committed = iotox::sync::commit_sync_content_staging(
        configured, expected.manifest, expected.manifest_bytes, staged_manifest,
        transaction.value(), commit_config);
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    local_manifest = committed.value().object_path;
  }

  iotox::sync::SyncContentConfig content_config;
  content_config.maximum_window_objects = 17U;
  content_config.maximum_page_window_objects = 4U;
  content_config.object_io_buffer_bytes = 8192U;
  content_config.manifest_buffer_bytes = 4096U;
  content_config.verify_local_objects = true;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, local_manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  const iotox::Status prepared = coordinator.prepare();
  IOTOX_CHECK_MSG(prepared.ok(), prepared.message());

  const auto current = authority();
  const auto first_source = source(11U, 1U, expected, current);
  const auto second_source = source(22U, 3U, expected, current);
  IOTOX_CHECK(coordinator.upsert_complete_source(first_source, current).ok());
  IOTOX_CHECK(coordinator.upsert_complete_source(second_source, current).ok());

  auto first = coordinator.next(1U);
  auto second = coordinator.next(2U);
  IOTOX_CHECK(first.ok() && first.value().has_value());
  IOTOX_CHECK(second.ok() && second.value().has_value());
  IOTOX_CHECK(first.value()->source_id != second.value()->source_id);

  const std::uint64_t removed_source = first.value()->source_id;
  auto fenced = coordinator.remove_source(removed_source);
  IOTOX_CHECK(fenced.ok() && fenced.value().size() == 1U);
  IOTOX_CHECK(fenced.value().front().request_id == 1U);
  IOTOX_CHECK(!coordinator.commit(1U).ok());

  copy_remote_object(remote_store, *second.value());
  IOTOX_CHECK(coordinator.commit(2U).ok());
  std::uint64_t next_request = 3U;
  while (!coordinator.complete()) {
    auto assignment = coordinator.next(next_request++);
    IOTOX_CHECK(assignment.ok());
    if (assignment.value().has_value()) {
      IOTOX_CHECK(assignment.value()->source_id != removed_source);
      copy_remote_object(remote_store, *assignment.value());
      IOTOX_CHECK(coordinator.commit(assignment.value()->request_id).ok());
      continue;
    }
    auto advanced = coordinator.advance_window();
    IOTOX_CHECK(advanced.ok() && advanced.value());
  }

  const auto rebuilt = temporary.path() / "rebuilt.bin";
  auto reconstructed = coordinator.reconstruct(rebuilt);
  IOTOX_CHECK(reconstructed.ok());
  IOTOX_CHECK(reconstructed.value().artifact == expected.artifact);
  IOTOX_CHECK(reconstructed.value().artifact_bytes == expected.artifact_bytes);
  IOTOX_CHECK(std::filesystem::file_size(rebuilt) ==
              std::filesystem::file_size(artifact));
  IOTOX_CHECK(toxsync::sha256_file(rebuilt.string()) ==
              toxsync::sha256_file(artifact.string()));
  const auto observed = coordinator.snapshot();
  IOTOX_CHECK(observed.phase == iotox::sync::SyncContentPhase::complete);
  IOTOX_CHECK(observed.sources == 1U);
  IOTOX_CHECK(observed.fenced_requests == 1U);
  IOTOX_CHECK(observed.chunk_objects_fetched == built.metadata.chunk_count);
  IOTOX_CHECK(observed.chunk_bytes_fetched == expected.artifact_bytes);
  IOTOX_CHECK(observed.resident_bytes < 2U * 1024U * 1024U);
}

IOTOX_TEST("content coordinator refuses wrong HEAD and source rebinding") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions build_options;
  build_options.chunking = {4096U, 8192U, 16384U};
  build_options.fsync_on_commit = false;
  const auto built = toxsync::build_content_store(artifact, remote_store,
                                                  manifest, build_options);
  const auto expected = accepted_head(configured, built, manifest);
  iotox::sync::SyncContentConfig content_config;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator noncanonical(
      configured, expected, manifest, temporary.path() / "local-store",
      temporary.path() / "incoming", content_config);
  IOTOX_CHECK(!noncanonical.prepare().ok());
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  IOTOX_CHECK(coordinator.prepare().ok());

  const auto current = authority();
  auto candidate = source(11U, 1U, expected, current);
  candidate.advertised_head_record[0U] ^= 1U;
  IOTOX_CHECK(!coordinator.upsert_complete_source(candidate, current).ok());
  candidate = source(11U, 1U, expected, current);
  IOTOX_CHECK(coordinator.upsert_complete_source(candidate, current).ok());
  candidate.authority = peer(current, principal(3U));
  IOTOX_CHECK(!coordinator.upsert_complete_source(candidate, current).ok());
  IOTOX_CHECK(iotox::sync::sync_content_phase_name(
                  iotox::sync::SyncContentPhase::artifact_chunks) ==
              "artifact-chunks");
  IOTOX_CHECK(iotox::sync::sync_content_phase_name(
                  static_cast<iotox::sync::SyncContentPhase>(255U)) ==
              "unknown");
}

IOTOX_TEST("content coordinator converges exact complementary source windows") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions build_options;
  build_options.chunking = {4096U, 8192U, 16384U};
  build_options.fsync_on_commit = false;
  const auto built = toxsync::build_content_store(artifact, remote_store,
                                                  manifest, build_options);
  IOTOX_CHECK(built.metadata.chunk_count > 2U);
  const auto expected = accepted_head(configured, built, manifest);
  iotox::sync::SyncContentConfig content_config;
  content_config.maximum_window_objects = 13U;
  content_config.object_io_buffer_bytes = 8192U;
  content_config.manifest_buffer_bytes = 4096U;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  IOTOX_CHECK(coordinator.prepare().ok());
  const auto current = authority();
  const auto even_source = source(41U, 1U, expected, current);
  const auto odd_source = source(42U, 3U, expected, current);

  const auto install_window = [&] {
    const auto window = coordinator.snapshot();
    IOTOX_CHECK(window.phase == iotox::sync::SyncContentPhase::artifact_chunks);
    const std::size_t bitmap_bytes =
        (static_cast<std::size_t>(window.window_object_count) + 7U) / 8U;
    std::vector<std::uint8_t> even(bitmap_bytes, 0U);
    std::vector<std::uint8_t> odd(bitmap_bytes, 0U);
    for (std::uint32_t local = 0U; local < window.window_object_count;
         ++local) {
      auto &bits =
          ((window.window_first_object + local) % 2U == 0U) ? even : odd;
      bits[local / 8U] |= static_cast<std::uint8_t>(1U << (local % 8U));
    }
    IOTOX_CHECK(coordinator
                    .upsert_source_window(even_source, current,
                                          window.window_kind,
                                          window.window_first_object,
                                          window.window_object_count, even)
                    .ok());
    IOTOX_CHECK(coordinator
                    .upsert_source_window(odd_source, current,
                                          window.window_kind,
                                          window.window_first_object,
                                          window.window_object_count, odd)
                    .ok());
  };

  install_window();
  bool saw_even = false;
  bool saw_odd = false;
  std::uint64_t request_id = 500U;
  while (!coordinator.complete()) {
    auto assignment = coordinator.next(request_id++);
    IOTOX_CHECK(assignment.ok());
    if (assignment.value().has_value()) {
      const bool even = assignment.value()->logical_index % 2U == 0U;
      IOTOX_CHECK(assignment.value()->source_id ==
                  (even ? even_source.source_id : odd_source.source_id));
      saw_even = saw_even || even;
      saw_odd = saw_odd || !even;
      copy_remote_object(remote_store, *assignment.value());
      IOTOX_CHECK(coordinator.commit(assignment.value()->request_id).ok());
      continue;
    }
    auto advanced = coordinator.advance_window();
    IOTOX_CHECK(advanced.ok() && advanced.value());
    if (!coordinator.complete())
      install_window();
  }
  IOTOX_CHECK(saw_even && saw_odd);
  auto rebuilt =
      coordinator.reconstruct(temporary.path() / "complementary.bin");
  IOTOX_CHECK(rebuilt.ok());
  IOTOX_CHECK(rebuilt.value().artifact == expected.artifact);
}

IOTOX_TEST("content coordinator bootstraps paged metadata through one source") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto remote_manifest = temporary.path() / "remote.txp";
  const auto local_manifest = temporary.path() / "local.txp";
  write_artifact(artifact);

  toxsync::PagedContentStoreOptions build_options;
  build_options.chunking = {4096U, 8192U, 16384U};
  build_options.entries_per_page = 4U;
  build_options.io_buffer_bytes = 8192U;
  build_options.root_buffer_bytes = 4096U;
  build_options.fsync_on_commit = false;
  const auto built = toxsync::build_paged_content_store(
      artifact, remote_store, remote_manifest, build_options);
  std::filesystem::copy_file(remote_manifest, local_manifest);
  const auto expected = accepted_head(configured, built, local_manifest);

  iotox::sync::SyncContentConfig content_config;
  content_config.maximum_window_objects = 11U;
  content_config.maximum_page_window_objects = 3U;
  content_config.object_io_buffer_bytes = 8192U;
  content_config.manifest_buffer_bytes = 4096U;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, local_manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  IOTOX_CHECK(coordinator.prepare().ok());
  IOTOX_CHECK(coordinator.snapshot().phase ==
              iotox::sync::SyncContentPhase::manifest_pages);
  const auto current = authority();
  IOTOX_CHECK(
      coordinator
          .upsert_complete_source(source(33U, 1U, expected, current), current)
          .ok());

  std::uint64_t request_id = 100U;
  while (!coordinator.complete()) {
    auto assignment = coordinator.next(request_id++);
    IOTOX_CHECK(assignment.ok());
    if (assignment.value().has_value()) {
      copy_remote_object(remote_store, *assignment.value());
      IOTOX_CHECK(coordinator.commit(assignment.value()->request_id).ok());
      continue;
    }
    auto advanced = coordinator.advance_window();
    IOTOX_CHECK(advanced.ok() && advanced.value());
  }
  auto reconstructed =
      coordinator.reconstruct(temporary.path() / "paged-rebuilt.bin");
  IOTOX_CHECK(reconstructed.ok());
  IOTOX_CHECK(reconstructed.value().artifact == expected.artifact);
  const auto observed = coordinator.snapshot();
  IOTOX_CHECK(observed.page_objects_fetched == built.metadata.page_count);
  IOTOX_CHECK(observed.chunk_objects_fetched == built.metadata.chunk_count);
}

IOTOX_TEST("content coordinator preserves an exact staging file on combined "
           "quota refusal") {
  TempDirectory temporary;
  auto configured = policy(temporary.path() / "namespace");
  configured.quotas.maximum_store_bytes = 2U * 1024U * 1024U;
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions options;
  options.chunking = {4096U, 8192U, 16384U};
  options.fsync_on_commit = false;
  const auto built =
      toxsync::build_content_store(artifact, remote_store, manifest, options);
  const auto expected = accepted_head(configured, built, manifest);

  const auto flat_source = temporary.path() / "flat.bin";
  write_pattern_file(flat_source, 2U * 1024U * 1024U - 1U);
  auto flat_digest = iotox::sync::hash_sync_file_sha256(flat_source);
  IOTOX_CHECK(flat_digest.ok());
  const iotox::sync::SyncObjectRecord flat_record{
      iotox::sync::SyncObjectKind::artifact, flat_digest.value(),
      std::filesystem::file_size(flat_source)};
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    const auto objects = std::filesystem::path(configured.root) / "objects";
    std::filesystem::create_directory(objects);
    IOTOX_CHECK(::chmod(objects.c_str(), static_cast<mode_t>(0700)) == 0);
    const auto flat_path =
        iotox::sync::sync_object_path(configured, flat_record);
    std::filesystem::copy_file(flat_source, flat_path);
    IOTOX_CHECK(::chmod(flat_path.c_str(), static_cast<mode_t>(0600)) == 0);
  }

  iotox::sync::SyncContentConfig content_config;
  content_config.object_io_buffer_bytes = 8192U;
  content_config.manifest_buffer_bytes = 4096U;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  IOTOX_CHECK(coordinator.prepare().ok());
  const auto current = authority();
  IOTOX_CHECK(
      coordinator
          .upsert_complete_source(source(77U, 1U, expected, current), current)
          .ok());
  auto assignment = coordinator.next(900U);
  IOTOX_CHECK(assignment.ok() && assignment.value().has_value());
  copy_remote_object(remote_store, *assignment.value());
  const iotox::Status committed = coordinator.commit(900U);
  IOTOX_CHECK(committed.code() == iotox::ErrorCode::resource_exhausted);
  IOTOX_CHECK(coordinator.assignment(900U).has_value());
  IOTOX_CHECK(std::filesystem::exists(assignment.value()->staging_path));
  IOTOX_CHECK(!std::filesystem::exists(toxsync::content_store_path(
      iotox::sync::sync_content_store_root(configured),
      to_toxsync(assignment.value()->object))));
}

IOTOX_TEST("content coordinator rejects path substitution and linked staging") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto remote_store = temporary.path() / "remote-store";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions options;
  options.chunking = {4096U, 8192U, 16384U};
  options.fsync_on_commit = false;
  const auto built =
      toxsync::build_content_store(artifact, remote_store, manifest, options);
  const auto expected = accepted_head(configured, built, manifest);
  iotox::sync::SyncContentConfig content_config;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      configured, expected, manifest,
      iotox::sync::sync_content_store_root(configured),
      iotox::sync::sync_content_staging_root(configured), content_config);
  IOTOX_CHECK(coordinator.prepare().ok());
  const auto current = authority();
  IOTOX_CHECK(
      coordinator
          .upsert_complete_source(source(88U, 1U, expected, current), current)
          .ok());
  auto assignment = coordinator.next(901U);
  IOTOX_CHECK(assignment.ok() && assignment.value().has_value());
  copy_remote_object(remote_store, *assignment.value());
  IOTOX_CHECK(!coordinator.commit(901U, temporary.path() / "substitute").ok());
  IOTOX_CHECK(coordinator.assignment(901U).has_value());
  const auto alias = temporary.path() / "staging-alias";
  std::filesystem::create_hard_link(assignment.value()->staging_path, alias);
  IOTOX_CHECK(!coordinator.commit(901U).ok());
  IOTOX_CHECK(coordinator.assignment(901U).has_value());
  IOTOX_CHECK(
      coordinator.fail(901U, iotox::sync::SyncContentFailure::permanent).ok());
  IOTOX_CHECK(!coordinator.assignment(901U).has_value());
  IOTOX_CHECK(!std::filesystem::exists(toxsync::content_store_path(
      iotox::sync::sync_content_store_root(configured),
      to_toxsync(assignment.value()->object))));
}

IOTOX_TEST("content object resolver derives membership and refuses missing CAS "
           "bytes") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact.bin";
  const auto manifest_source = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions build_options;
  build_options.chunking = {4096U, 8192U, 16384U};
  build_options.fsync_on_commit = false;
  const auto built = toxsync::build_content_store(
      artifact, iotox::sync::sync_content_store_root(configured),
      manifest_source, build_options);
  const auto expected = accepted_head(configured, built, manifest_source);
  iotox::sync::SignedHead head;
  head.namespace_id = expected.namespace_id;
  head.writer = expected.writer;
  head.engine = expected.engine;
  head.generation = expected.generation;
  head.parent = expected.parent;
  head.artifact = expected.artifact;
  head.manifest = expected.manifest;
  head.artifact_bytes = expected.artifact_bytes;
  head.manifest_bytes = expected.manifest_bytes;
  head.signature.fill(1U);
  auto root = iotox::sync::resolve_sync_content_object(
      configured, head, iotox::sync::SyncContentObjectKind::root_manifest, 0U);
  IOTOX_CHECK(root.ok());
  IOTOX_CHECK(root.value().object == head.manifest);
  IOTOX_CHECK(root.value().object_bytes == head.manifest_bytes);
  IOTOX_CHECK(!iotox::sync::resolve_sync_content_object(
                   configured, head,
                   iotox::sync::SyncContentObjectKind::root_manifest, 1U)
                   .ok());
  auto resolved = iotox::sync::resolve_sync_content_object(
      configured, head, iotox::sync::SyncContentObjectKind::artifact_chunk, 0U);
  IOTOX_CHECK(resolved.ok());
  IOTOX_CHECK(resolved.value().logical_index == 0U);
  IOTOX_CHECK(resolved.value().object_bytes > 0U);
  IOTOX_CHECK(std::filesystem::exists(resolved.value().path));
  auto availability = iotox::sync::resolve_sync_content_availability(
      configured, head, iotox::sync::SyncContentObjectKind::artifact_chunk, 0U,
      static_cast<std::uint32_t>(built.metadata.chunk_count));
  IOTOX_CHECK(availability.ok());
  IOTOX_CHECK(availability.value().available_objects ==
              built.metadata.chunk_count);
  std::filesystem::remove(resolved.value().path);
  IOTOX_CHECK(!iotox::sync::resolve_sync_content_object(
                   configured, head,
                   iotox::sync::SyncContentObjectKind::artifact_chunk, 0U)
                   .ok());
  availability = iotox::sync::resolve_sync_content_availability(
      configured, head, iotox::sync::SyncContentObjectKind::artifact_chunk, 0U,
      static_cast<std::uint32_t>(built.metadata.chunk_count));
  IOTOX_CHECK(availability.ok());
  IOTOX_CHECK(availability.value().available_objects + 1U ==
              built.metadata.chunk_count);
}

IOTOX_TEST("content store inventory rejects aliases drift and corrupt bytes") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_store(configured, transaction.value())
          .ok());

  const auto artifact = temporary.path() / "artifact.bin";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions options;
  options.chunking = {4096U, 8192U, 16384U};
  options.fsync_on_commit = false;
  const auto built = toxsync::build_content_store(
      artifact, iotox::sync::sync_content_store_root(configured), manifest,
      options);

  auto inventory = iotox::sync::inspect_sync_content_store(
      configured, transaction.value(), true);
  IOTOX_CHECK_MSG(inventory.ok(), inventory.status().message());
  IOTOX_CHECK(inventory.value().objects == inventory.value().records.size());
  IOTOX_CHECK(inventory.value().objects >= 2U);
  IOTOX_CHECK(inventory.value().objects <= built.metadata.chunk_count + 1U);
  const auto root_object = std::find_if(
      inventory.value().records.begin(), inventory.value().records.end(),
      [&](const iotox::sync::SyncContentStoredObject &record) {
        return record.object == from_toxsync(built.metadata.manifest_digest);
      });
  IOTOX_CHECK(root_object != inventory.value().records.end());

  const auto root = iotox::sync::sync_content_store_root(configured);
  IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0755)) == 0);
  IOTOX_CHECK(
      !iotox::sync::inspect_sync_content_store(configured, transaction.value())
           .ok());
  IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
  std::filesystem::create_directory(root / "GG");
  IOTOX_CHECK(
      !iotox::sync::inspect_sync_content_store(configured, transaction.value())
           .ok());
  std::filesystem::remove(root / "GG");

  const auto root_path =
      toxsync::content_store_path(root, built.metadata.manifest_digest);
  const auto alias = temporary.path() / "hard-link";
  std::filesystem::create_hard_link(root_path, alias);
  IOTOX_CHECK(
      !iotox::sync::inspect_sync_content_store(configured, transaction.value())
           .ok());
  std::filesystem::remove(alias);
  IOTOX_CHECK(iotox::sync::inspect_sync_content_store(configured,
                                                      transaction.value(), true)
                  .ok());

  std::fstream corrupted(root_path,
                         std::ios::binary | std::ios::in | std::ios::out);
  char first = 0;
  corrupted.read(&first, 1);
  IOTOX_CHECK(static_cast<bool>(corrupted));
  first = static_cast<char>(static_cast<unsigned char>(first) ^ 0x5aU);
  corrupted.seekp(0);
  corrupted.write(&first, 1);
  corrupted.close();
  IOTOX_CHECK(iotox::sync::inspect_sync_content_store(
                  configured, transaction.value(), false)
                  .ok());
  IOTOX_CHECK(!iotox::sync::inspect_sync_content_store(
                   configured, transaction.value(), true)
                   .ok());
}

IOTOX_TEST("content store and flat objects share count and byte quotas") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_store(configured, transaction.value())
          .ok());

  const auto artifact = temporary.path() / "artifact.bin";
  const auto manifest = temporary.path() / "root.txc";
  write_artifact(artifact);
  toxsync::ContentStoreOptions options;
  options.chunking = {4096U, 8192U, 16384U};
  options.fsync_on_commit = false;
  static_cast<void>(toxsync::build_content_store(
      artifact, iotox::sync::sync_content_store_root(configured), manifest,
      options));

  const auto flat_source = temporary.path() / "flat.bin";
  write_pattern_file(flat_source, 1536U * 1024U + 29U);
  auto flat_digest = iotox::sync::hash_sync_file_sha256(flat_source);
  IOTOX_CHECK(flat_digest.ok());
  const iotox::sync::SyncObjectRecord flat_record{
      iotox::sync::SyncObjectKind::artifact, flat_digest.value(),
      std::filesystem::file_size(flat_source)};
  const auto objects = std::filesystem::path(configured.root) / "objects";
  std::filesystem::create_directory(objects);
  IOTOX_CHECK(::chmod(objects.c_str(), static_cast<mode_t>(0700)) == 0);
  const auto flat_path = iotox::sync::sync_object_path(configured, flat_record);
  std::filesystem::copy_file(flat_source, flat_path);
  IOTOX_CHECK(::chmod(flat_path.c_str(), static_cast<mode_t>(0600)) == 0);

  auto combined = iotox::sync::inspect_sync_combined_store(
      configured, transaction.value(), true);
  IOTOX_CHECK_MSG(combined.ok(), combined.status().message());
  IOTOX_CHECK(combined.value().flat.objects == 1U);
  IOTOX_CHECK(combined.value().objects ==
              combined.value().content.objects + 1U);
  IOTOX_CHECK(combined.value().bytes ==
              combined.value().content.bytes + flat_record.bytes);

  auto count_limited = configured;
  count_limited.quotas.maximum_objects = combined.value().content.objects;
  IOTOX_CHECK(
      iotox::sync::inspect_sync_object_store(count_limited, transaction.value())
          .ok());
  IOTOX_CHECK(iotox::sync::inspect_sync_content_store(count_limited,
                                                      transaction.value())
                  .ok());
  IOTOX_CHECK(!iotox::sync::inspect_sync_combined_store(count_limited,
                                                        transaction.value())
                   .ok());

  auto byte_limited = configured;
  byte_limited.quotas.maximum_store_bytes = 2U * 1024U * 1024U;
  IOTOX_CHECK(
      iotox::sync::inspect_sync_object_store(byte_limited, transaction.value())
          .ok());
  IOTOX_CHECK(
      iotox::sync::inspect_sync_content_store(byte_limited, transaction.value())
          .ok());
  IOTOX_CHECK(!iotox::sync::inspect_sync_combined_store(byte_limited,
                                                        transaction.value())
                   .ok());
}

IOTOX_TEST(
    "content staging commit copies verifies consumes and reuses one object") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  const auto first =
      iotox::sync::sync_content_staging_root(configured) / "first.part";
  write_pattern_file(first, 192U * 1024U + 17U);
  auto digest = iotox::sync::hash_sync_file_sha256(first);
  IOTOX_CHECK(digest.ok());
  iotox::sync::SyncContentCommitConfig commit_config;
  commit_config.io_buffer_bytes = 4096U;
  commit_config.fsync_on_commit = false;
  auto committed = iotox::sync::commit_sync_content_staging(
      configured, digest.value(), std::filesystem::file_size(first), first,
      transaction.value(), commit_config);
  IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
  IOTOX_CHECK(committed.value().installed);
  IOTOX_CHECK(!committed.value().reused);
  IOTOX_CHECK(committed.value().bytes_verified ==
              committed.value().object_bytes);
  IOTOX_CHECK(committed.value().bytes_copied == committed.value().object_bytes);
  IOTOX_CHECK(!std::filesystem::exists(first));
  IOTOX_CHECK(std::filesystem::exists(committed.value().object_path));

  const auto duplicate =
      iotox::sync::sync_content_staging_root(configured) / "duplicate.part";
  write_pattern_file(duplicate, committed.value().object_bytes);
  auto reused = iotox::sync::commit_sync_content_staging(
      configured, digest.value(), committed.value().object_bytes, duplicate,
      transaction.value(), commit_config);
  IOTOX_CHECK(reused.ok());
  IOTOX_CHECK(!reused.value().installed && reused.value().reused);
  IOTOX_CHECK(!std::filesystem::exists(duplicate));
  auto inventory = iotox::sync::inspect_sync_combined_store(
      configured, transaction.value(), true);
  IOTOX_CHECK(inventory.ok());
  IOTOX_CHECK(inventory.value().content.objects == 1U);
  IOTOX_CHECK(inventory.value().content.bytes ==
              committed.value().object_bytes);

  const auto corrupt =
      iotox::sync::sync_content_staging_root(configured) / "corrupt.part";
  write_pattern_file(corrupt, 4097U);
  auto wrong = digest.value();
  wrong[0U] ^= 0xffU;
  IOTOX_CHECK(!iotox::sync::commit_sync_content_staging(
                   configured, wrong, std::filesystem::file_size(corrupt),
                   corrupt, transaction.value(), commit_config)
                   .ok());
  IOTOX_CHECK(std::filesystem::exists(corrupt));
  IOTOX_CHECK(!std::filesystem::exists(toxsync::content_store_path(
      iotox::sync::sync_content_store_root(configured), to_toxsync(wrong))));
}

IOTOX_TEST(
    "content store preparation refuses a symlink without touching its target") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  const auto victim = temporary.path() / "victim";
  std::filesystem::create_directory(victim);
  IOTOX_CHECK(::chmod(victim.c_str(), static_cast<mode_t>(0755)) == 0);
  std::filesystem::create_directory_symlink(
      victim, iotox::sync::sync_content_store_root(configured));
  IOTOX_CHECK(
      !iotox::sync::prepare_sync_content_store(configured, transaction.value())
           .ok());
  struct stat metadata {};
  IOTOX_CHECK(::stat(victim.c_str(), &metadata) == 0);
  IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
              static_cast<mode_t>(0755));
}
