#include "iotox/sync_content_acceptance.hpp"
#include "iotox/sync_content_publication.hpp"
#include "iotox/sync_digest.hpp"

#include "test_harness.hpp"

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
    std::string pattern = "/tmp/iotox-content-accept-XXXXXX";
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

iotox::sync::NamespacePolicy
policy(const std::filesystem::path &root,
       const iotox::security::SigningPublicKey &writer,
       const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::NamespacePolicy result;
  result.id = "content-accept-test";
  result.root = root.lexically_normal().string();
  result.engine = iotox::sync::Engine::content_v2;
  result.activation = iotox::sync::ActivationMode::manual;
  result.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_staging_bytes = 4U * 1024U * 1024U;
  result.quotas.maximum_store_bytes = 16U * 1024U * 1024U;
  result.quotas.maximum_objects = 1024U;
  result.quotas.maximum_peers = 4U;
  result.quotas.maximum_lanes = 2U;
  result.quotas.maximum_outstanding_requests = 16U;
  result.writers = {writer};
  result.subscribers = {subscriber};
  return result;
}

void write_pattern(const std::filesystem::path &path, std::size_t bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  std::uint64_t state = 0x9e3779b97f4a7c15ULL;
  for (std::size_t index = 0U; index < bytes; ++index) {
    state ^= state << 13U;
    state ^= state >> 7U;
    state ^= state << 17U;
    output.put(static_cast<char>(state & 0xffU));
  }
  if (!output)
    throw std::runtime_error("pattern write failed");
}

iotox::sync::AcceptedHead
accepted_from(const iotox::sync::CandidateHead &candidate) {
  return iotox::sync::AcceptedHead{
      candidate.namespace_id,  candidate.writer,   candidate.engine,
      candidate.generation,    candidate.record,   candidate.parent,
      candidate.artifact,      candidate.manifest, candidate.artifact_bytes,
      candidate.manifest_bytes};
}

iotox::security::AuthoritySnapshot authority() {
  iotox::security::AuthoritySnapshot result;
  result.initialized = true;
  result.format = iotox::security::AuthorityLedgerFormat::v3;
  result.ownership_epoch = 2U;
  result.sequence = 3U;
  result.tail_digest[0U] = 0x71U;
  return result;
}

iotox::security::PeerAuthoritySnapshot
peer(const iotox::security::AuthoritySnapshot &current,
     const iotox::security::SigningPublicKey &publisher) {
  iotox::security::PeerAuthoritySnapshot result;
  result.connected = true;
  result.feature_negotiated = true;
  result.authority_v2_negotiated = true;
  result.authority_v3_negotiated = true;
  result.verifier_state = iotox::security::AuthorityVerifierState::authorized;
  result.remote_authorized = true;
  result.remote_principal = publisher;
  result.remote_capabilities =
      static_cast<std::uint64_t>(iotox::security::Capability::sync_publish);
  result.local_authority_format = current.format;
  result.local_authority_epoch = current.ownership_epoch;
  result.local_authority_sequence = current.sequence;
  result.local_authority_tail_digest = current.tail_digest;
  return result;
}

void copy_object(const iotox::sync::NamespacePolicy &remote,
                 const iotox::sync::SyncContentAssignment &assignment) {
  const auto source =
      iotox::sync::sync_content_object_path(remote, assignment.object);
  std::filesystem::create_directories(assignment.staging_path.parent_path());
  std::filesystem::copy_file(source, assignment.staging_path);
  if (::chmod(assignment.staging_path.c_str(), static_cast<mode_t>(0600)) !=
      0) {
    throw std::runtime_error("staging chmod failed");
  }
}

} // namespace

IOTOX_TEST(
    "content reconstruction commits whole CAS before accepting signed HEAD") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto remote = policy(temporary.path() / "remote",
                             publisher.public_key(), subscriber.public_key());
  const auto local = policy(temporary.path() / "local", publisher.public_key(),
                            subscriber.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 512U * 1024U);

  iotox::sync::SyncContentPublicationConfig publication_config;
  publication_config.format = iotox::sync::SyncContentPublicationFormat::flat;
  publication_config.minimum_chunk_bytes = 4096U;
  publication_config.average_chunk_bytes = 8192U;
  publication_config.maximum_chunk_bytes = 16384U;
  publication_config.io_buffer_bytes = 4096U;
  publication_config.manifest_buffer_bytes = 4096U;
  publication_config.workspace_budget_bytes = 1024U * 1024U;
  publication_config.fsync_on_commit = false;
  iotox::sync::SignedHeadStore published_heads(remote.root);
  auto published = iotox::sync::publish_local_content_revision(
      remote, source, publisher, crypto, published_heads, publication_config);
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  const iotox::sync::SignedHead head = published.value().publication.head;
  auto candidate = iotox::sync::verified_candidate_head(local, head, crypto);
  IOTOX_CHECK_MSG(candidate.ok(), candidate.status().message());

  std::filesystem::create_directory(local.root);
  IOTOX_CHECK(::chmod(local.root.c_str(), static_cast<mode_t>(0700)) == 0);
  std::filesystem::path root_manifest;
  {
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(local);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(
        iotox::sync::prepare_sync_content_staging(local, transaction.value())
            .ok());
    const auto staged =
        iotox::sync::sync_content_staging_root(local) / "root-manifest.part";
    std::filesystem::copy_file(
        iotox::sync::sync_content_object_path(remote, head.manifest), staged);
    IOTOX_CHECK(::chmod(staged.c_str(), static_cast<mode_t>(0600)) == 0);
    iotox::sync::SyncContentCommitConfig commit;
    commit.io_buffer_bytes = 4096U;
    commit.fsync_on_commit = false;
    auto committed = iotox::sync::commit_sync_content_staging(
        local, head.manifest, head.manifest_bytes, staged, transaction.value(),
        commit);
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    root_manifest = committed.value().object_path;
  }

  iotox::sync::SyncContentConfig content_config;
  content_config.maximum_window_objects = 17U;
  content_config.object_io_buffer_bytes = 4096U;
  content_config.manifest_buffer_bytes = 4096U;
  content_config.fsync_on_commit = false;
  iotox::sync::SyncContentCoordinator coordinator(
      local, accepted_from(candidate.value()), root_manifest,
      iotox::sync::sync_content_store_root(local),
      iotox::sync::sync_content_staging_root(local), content_config);
  IOTOX_CHECK_MSG(coordinator.prepare().ok(), "coordinator prepare failed");
  const auto current = authority();
  iotox::sync::SyncContentSource remote_source;
  remote_source.source_id = 91U;
  remote_source.advertised_head_record = candidate.value().record;
  remote_source.authority = peer(current, publisher.public_key());
  remote_source.maximum_lanes = 1U;
  remote_source.content_transfer_negotiated = true;
  IOTOX_CHECK(coordinator.upsert_complete_source(remote_source, current).ok());
  std::uint64_t request_id = 1000U;
  while (!coordinator.complete()) {
    auto assignment = coordinator.next(request_id++);
    IOTOX_CHECK(assignment.ok());
    if (assignment.value()) {
      copy_object(remote, *assignment.value());
      IOTOX_CHECK(coordinator.commit(assignment.value()->request_id).ok());
      continue;
    }
    auto advanced = coordinator.advance_window();
    IOTOX_CHECK(advanced.ok() && advanced.value());
  }

  iotox::sync::SyncContentAcceptanceConfig acceptance_config;
  acceptance_config.io_buffer_bytes = 4096U;
  acceptance_config.fsync_on_commit = false;
  std::size_t cancellation_checks = 0U;
  iotox::sync::SyncContentAcceptanceSeams acceptance_seams;
  acceptance_seams.cancel_requested = [&cancellation_checks] {
    ++cancellation_checks;
    return cancellation_checks == 3U;
  };
  auto interrupted = iotox::sync::reconstruct_and_accept_sync_content_revision(
      local, head, coordinator, subscriber, crypto, acceptance_config,
      std::move(acceptance_seams));
  IOTOX_CHECK_MSG(interrupted.status().code() == iotox::ErrorCode::unavailable,
                  interrupted.status().message());
  iotox::sync::AcceptedHeadStore accepted(local.root);
  auto absent = accepted.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(absent.ok() && !absent.value());
  IOTOX_CHECK(std::filesystem::exists(
      iotox::sync::sync_content_object_path(local, head.artifact)));

  auto retried = iotox::sync::reconstruct_and_accept_sync_content_revision(
      local, head, coordinator, subscriber, crypto, acceptance_config);
  IOTOX_CHECK_MSG(retried.ok(), retried.status().message());
  IOTOX_CHECK(!retried.value().reconstructed);
  IOTOX_CHECK(retried.value().artifact_commit.reused);
  IOTOX_CHECK(retried.value().acceptance.accepted());
  auto accepted_head = accepted.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(accepted_head.ok() && accepted_head.value());
  IOTOX_CHECK(accepted_head.value()->record == candidate.value().record);
  IOTOX_CHECK(iotox::sync::hash_sync_file_sha256(
                  iotox::sync::sync_content_object_path(local, head.artifact))
                  .value() == head.artifact);

  auto duplicate = iotox::sync::reconstruct_and_accept_sync_content_revision(
      local, head, coordinator, subscriber, crypto, acceptance_config);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().acceptance.decision ==
              iotox::sync::HeadAcceptanceDecision::duplicate);
}

IOTOX_TEST("content reconstruction cleanup refuses foreign workspace entries") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto configured =
      policy(temporary.path() / "namespace", publisher.public_key(),
             subscriber.public_key());
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  const auto parent =
      iotox::sync::sync_content_staging_root(configured) / "reconstructions";
  std::filesystem::create_directory(parent);
  IOTOX_CHECK(::chmod(parent.c_str(), static_cast<mode_t>(0700)) == 0);
  const auto abandoned = parent / "local-0123456789abcdef";
  std::filesystem::create_directory(abandoned);
  IOTOX_CHECK(::chmod(abandoned.c_str(), static_cast<mode_t>(0700)) == 0);
  write_pattern(abandoned / "partial", 1024U);
  auto cleaned = iotox::sync::cleanup_sync_content_reconstruction_staging(
      configured, transaction.value());
  IOTOX_CHECK(cleaned.ok() && cleaned.value() == 1U);
  const auto foreign = parent / "foreign";
  std::filesystem::create_directory(foreign);
  IOTOX_CHECK(::chmod(foreign.c_str(), static_cast<mode_t>(0700)) == 0);
  IOTOX_CHECK(!iotox::sync::cleanup_sync_content_reconstruction_staging(
                   configured, transaction.value())
                   .ok());
  IOTOX_CHECK(std::filesystem::exists(foreign));
}
