#include "iotox/sync_digest.hpp"
#include "iotox/sync_manifest.hpp"
#include "iotox/sync_subscriber.hpp"

#include "test_harness.hpp"

#include <filesystem>
#include <fstream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-subscriber-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
  }
  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const { return path_; }

private:
  std::filesystem::path path_;
};

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity identity(
    const std::filesystem::path &path,
    const iotox::security::Sodium &crypto) {
  auto loaded = iotox::security::DeviceIdentity::load_or_create(
      path, crypto, true);
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

void write_private(const std::filesystem::path &path,
                   std::string_view bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  if (!output) throw std::runtime_error("fixture write failed");
  output.close();
  if (::chmod(path.c_str(), S_IRUSR | S_IWUSR) != 0)
    throw std::runtime_error("fixture chmod failed");
}

iotox::sync::NamespacePolicy policy(
    const std::filesystem::path &root,
    const iotox::security::SigningPublicKey &writer) {
  iotox::sync::NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.writers = {writer};
  result.quotas.maximum_artifact_bytes = 4096U;
  result.quotas.maximum_manifest_bytes = 4096U;
  result.quotas.maximum_store_bytes = 16384U;
  result.quotas.maximum_staging_bytes = 8192U;
  result.quotas.maximum_outstanding_requests = 4U;
  return result;
}

iotox::sync::SyncPeerContext context(
    const iotox::security::SigningPublicKey &publisher) {
  iotox::sync::SyncPeerContext result;
  result.friend_number = 6U;
  result.online_epoch = 11U;
  result.authority_route_key.fill(0x72U);
  result.authority.initialized = true;
  result.authority.format = iotox::security::AuthorityLedgerFormat::v3;
  result.authority.ownership_epoch = 3U;
  result.authority.sequence = 8U;
  result.authority.tail_digest[0U] = 0x31U;
  result.peer_authority.friend_number = result.friend_number;
  result.peer_authority.online_epoch = result.online_epoch;
  result.peer_authority.connected = true;
  result.peer_authority.feature_negotiated = true;
  result.peer_authority.authority_v2_negotiated = true;
  result.peer_authority.authority_v3_negotiated = true;
  result.peer_authority.verifier_state =
      iotox::security::AuthorityVerifierState::authorized;
  result.peer_authority.remote_authorized = true;
  result.peer_authority.remote_principal = publisher;
  result.peer_authority.remote_capabilities = static_cast<std::uint64_t>(
      iotox::security::Capability::sync_publish);
  result.peer_authority.local_authority_format = result.authority.format;
  result.peer_authority.local_authority_epoch =
      result.authority.ownership_epoch;
  result.peer_authority.local_authority_sequence = result.authority.sequence;
  result.peer_authority.local_authority_tail_digest =
      result.authority.tail_digest;
  result.transfer_carrier.route_key = result.authority_route_key;
  result.transfer_carrier.worker_id = result.online_epoch;
  result.transfer_carrier.friend_number = result.friend_number;
  result.transfer_carrier.online_epoch = result.online_epoch;
  return result;
}

} // namespace

IOTOX_TEST("sync subscriber commits two reordered FileId offers before accepting HEAD") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto local = identity(temporary.path() / "local.identity", crypto);
  auto remote = identity(temporary.path() / "remote.identity", crypto);
  const auto namespace_root = temporary.path() / "namespace";
  std::filesystem::create_directories(namespace_root);
  std::filesystem::permissions(
      namespace_root, std::filesystem::perms::owner_all,
      std::filesystem::perm_options::replace);
  const auto artifact_source = temporary.path() / "artifact";
  const auto manifest_source = temporary.path() / "manifest";
  const std::string artifact_bytes = "immutable artifact bytes";
  write_private(artifact_source, artifact_bytes);
  const auto configured = policy(namespace_root, remote.public_key());
  auto built_manifest = iotox::sync::build_sync_range_manifest(
      configured, artifact_source, manifest_source);
  IOTOX_CHECK_MSG(built_manifest.ok(),
                  built_manifest.status().message());
  std::ifstream manifest_input(manifest_source, std::ios::binary);
  std::ostringstream manifest_output;
  manifest_output << manifest_input.rdbuf();
  const std::string manifest_bytes = manifest_output.str();
  IOTOX_CHECK(!manifest_bytes.empty());
  auto artifact_digest =
      iotox::sync::hash_sync_file_sha256(artifact_source);
  auto manifest_digest =
      iotox::sync::hash_sync_file_sha256(manifest_source);
  IOTOX_CHECK(artifact_digest.ok() && manifest_digest.ok());

  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHeadPublicationRequest publication;
  publication.artifact = artifact_digest.value();
  publication.manifest = manifest_digest.value();
  publication.artifact_bytes = artifact_bytes.size();
  publication.manifest_bytes = manifest_bytes.size();
  auto signed_head = iotox::sync::create_signed_head(
      configured, publication, std::nullopt, remote, crypto);
  IOTOX_CHECK(signed_head.ok());

  std::uint64_t next_message_id = 100U;
  std::uint8_t next_file_id = 0x41U;
  std::uint64_t cancellations = 0U;
  std::uint64_t cancellation_failures = 0U;
  std::uint64_t admission_deferrals = 0U;
  std::uint64_t admission_carrier_losses = 0U;
  std::map<std::uint32_t, std::filesystem::path> destinations;
  std::map<std::uint32_t, std::uint64_t> sizes;
  iotox::sync::SyncSubscriberSeams seams;
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return next_message_id++;
  };
  seams.make_file_id = [&]() -> iotox::Result<iotox::FileId> {
    iotox::FileId result{};
    result.fill(next_file_id++);
    return result;
  };
  seams.receive_to_path = [&](const iotox::sync::SyncTransferCarrier &carrier,
                              std::uint32_t file_number,
                              const std::filesystem::path &destination) {
    if (admission_carrier_losses != 0U) {
      --admission_carrier_losses;
      return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
          iotox::ErrorCode::unavailable,
          "injected worker loss at receive admission"}};
    }
    if (admission_deferrals != 0U) {
      --admission_deferrals;
      return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
          iotox::ErrorCode::resource_exhausted,
          "injected Agent receive-ceiling admission deferral"}};
    }
    const bool artifact =
        file_number == 31U || file_number == 41U || file_number == 51U;
    const std::string_view content = artifact
        ? std::string_view(artifact_bytes)
        : std::string_view(manifest_bytes);
    write_private(destination, content);
    destinations[file_number] = destination;
    sizes[file_number] = content.size();
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::active;
    record.friend_number = carrier.friend_number;
    record.file_number = file_number;
    record.file_size = content.size();
    record.local_path = destination;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.cancel_transfer = [&](const iotox::sync::SyncTransferCarrier &,
                              std::uint32_t) {
    ++cancellations;
    if (cancellation_failures != 0U) {
      --cancellation_failures;
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected cancel send failure"};
    }
    return iotox::Status::success();
  };
  seams.retire_transfer = [](
      const iotox::sync::SyncTransferCarrier &, std::uint32_t) {
    return iotox::Status::success();
  };
  seams.install.hash_file = iotox::sync::hash_sync_file_sha256;
  iotox::sync::SyncSubscriberService::Config service_config;
  service_config.identity = &local;
  service_config.sodium = &crypto;
  iotox::sync::SyncSubscriberService service(
      registry, std::move(seams), service_config);
  auto peer = context(remote.public_key());

  auto head_request = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(head_request.ok());
  IOTOX_CHECK(head_request.value().message_id == 100U);
  IOTOX_CHECK(service.snapshot().front().route_failover_policy ==
              iotox::sync::SyncRouteFailoverPolicy::available);
  IOTOX_CHECK(service.snapshot().front().route_class ==
              iotox::sync::SyncRouteClassConstraint::any);
  IOTOX_CHECK(!service.begin_pull(
                   peer, configured.id,
                   iotox::sync::SyncRouteFailoverPolicy::fail_closed)
                   .ok());
  IOTOX_CHECK(!service.begin_pull(
                   peer, configured.id,
                   iotox::sync::SyncRouteFailoverPolicy::available,
                   iotox::sync::SyncRouteClassConstraint::tox_tor)
                   .ok());
  IOTOX_CHECK(!service.retry_pull(
                   peer, configured.id,
                   iotox::sync::SyncRouteFailoverPolicy::fail_closed)
                   .ok());
  IOTOX_CHECK(!service.namespace_mutation_ready(configured.id).ok());
  auto head_retry = service.retry_pull(peer, configured.id);
  IOTOX_CHECK(head_retry.ok() && head_retry.value().size() == 1U);
  auto encoded_head_retry =
      iotox::protocol::encode(head_retry.value().front());
  auto encoded_head_request =
      iotox::protocol::encode(head_request.value());
  IOTOX_CHECK(encoded_head_retry.ok() && encoded_head_request.ok());
  IOTOX_CHECK(encoded_head_retry.value() == encoded_head_request.value());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, signed_head.value()},
      200U, head_request.value().message_id);
  IOTOX_CHECK(head_result.ok());
  auto first_carrier = peer;
  first_carrier.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::auxiliary;
  first_carrier.transfer_carrier.route_key.fill(0x91U);
  first_carrier.transfer_carrier.worker_id = 91U;
  first_carrier.transfer_carrier.friend_number = 21U;
  first_carrier.transfer_carrier.online_epoch = 3U;
  first_carrier.transfer_carrier.remote_route_generation = 4U;
  first_carrier.transfer_carrier.remote_coordinator_route_key.fill(0x31U);
  first_carrier.transfer_carrier.primary_authority_online_epoch =
      first_carrier.online_epoch;
  auto requests = service.handle_head_result(
      first_carrier, head_result.value());
  IOTOX_CHECK(requests.ok() && requests.value().size() == 2U);
  const auto first_requests = requests.value();
  auto admission_loss_request = iotox::sync::decode_sync_object_request(
      first_requests.front().payload);
  IOTOX_CHECK(admission_loss_request.ok());
  iotox::FileTransferRecord admission_loss_offer;
  admission_loss_offer.direction =
      iotox::FileTransferDirection::incoming;
  admission_loss_offer.state = iotox::FileTransferState::offered;
  admission_loss_offer.friend_number =
      first_carrier.transfer_carrier.friend_number;
  admission_loss_offer.file_number = 30U;
  admission_loss_offer.file_size =
      admission_loss_request.value().kind ==
              iotox::sync::SyncObjectKind::artifact
          ? publication.artifact_bytes
          : publication.manifest_bytes;
  admission_loss_offer.file_id =
      admission_loss_request.value().transfer_id;
  admission_loss_offer.has_file_id = true;
  admission_carrier_losses = 1U;
  auto admission_loss_claimed = service.handle_offer(
      first_carrier, admission_loss_offer);
  IOTOX_CHECK(admission_loss_claimed.ok() &&
              admission_loss_claimed.value());
  IOTOX_CHECK(service.snapshot().front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  auto duplicate_admission_loss = service.handle_offer(
      first_carrier, admission_loss_offer);
  IOTOX_CHECK(duplicate_admission_loss.ok() &&
              duplicate_admission_loss.value());
  IOTOX_CHECK(service.carrier_offline(
                  first_carrier.transfer_carrier).ok());
  auto fenced_state = service.snapshot();
  IOTOX_CHECK(fenced_state.size() == 1U);
  IOTOX_CHECK(fenced_state.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(fenced_state.front().detail.find("replacement required") !=
              std::string::npos);

  peer = first_carrier;
  peer.transfer_carrier.route_key.fill(0x92U);
  peer.transfer_carrier.worker_id = 92U;
  peer.transfer_carrier.friend_number = 22U;
  peer.transfer_carrier.online_epoch = 5U;
  peer.transfer_carrier.remote_route_generation = 5U;
  peer.transfer_carrier.remote_coordinator_route_key.fill(0x31U);
  peer.transfer_carrier.primary_authority_online_epoch =
      peer.online_epoch;
  auto reassigned = service.reassign_transfer_carrier(
      head_request.value().message_id, peer);
  IOTOX_CHECK(reassigned.ok() && reassigned.value().size() == 2U);
  requests = reassigned;
  IOTOX_CHECK(service.snapshot().front().transfer_carrier ==
              peer.transfer_carrier);
  for (std::size_t index = 0U; index < requests.value().size(); ++index) {
    auto old_request = iotox::sync::decode_sync_object_request(
        first_requests[index].payload);
    auto replacement_request = iotox::sync::decode_sync_object_request(
        requests.value()[index].payload);
    IOTOX_CHECK(old_request.ok() && replacement_request.ok());
    IOTOX_CHECK(first_requests[index].message_id !=
                requests.value()[index].message_id);
    IOTOX_CHECK(old_request.value().transfer_id !=
                replacement_request.value().transfer_id);
  }
  auto stale_request = iotox::sync::decode_sync_object_request(
      first_requests.front().payload);
  IOTOX_CHECK(stale_request.ok());
  auto stale_result = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered,
       stale_request.value().kind, stale_request.value().head_record,
       stale_request.value().transfer_id},
      299U, first_requests.front().message_id);
  IOTOX_CHECK(stale_result.ok());
  IOTOX_CHECK(!service.handle_object_result(
                   first_carrier, stale_result.value()).ok());
  auto object_retries = service.retry_pull(peer, configured.id);
  IOTOX_CHECK(object_retries.ok());
  IOTOX_CHECK(object_retries.value().size() == requests.value().size());
  for (std::size_t index = 0U; index < requests.value().size(); ++index) {
    auto encoded_retry = iotox::protocol::encode(
        object_retries.value()[index]);
    auto encoded_request = iotox::protocol::encode(
        requests.value()[index]);
    IOTOX_CHECK(encoded_retry.ok() && encoded_request.ok());
    IOTOX_CHECK(encoded_retry.value() == encoded_request.value());
  }

  struct RequestLane {
    iotox::sync::SyncObjectRequest request;
    std::uint64_t message_id{0U};
    std::uint32_t file_number{0U};
    std::uint64_t bytes{0U};
  };
  std::vector<RequestLane> lanes;
  for (const auto &frame : requests.value()) {
    auto decoded = iotox::sync::decode_sync_object_request(frame.payload);
    IOTOX_CHECK(decoded.ok());
    const bool artifact = decoded.value().kind ==
                          iotox::sync::SyncObjectKind::artifact;
    lanes.push_back({decoded.value(), frame.message_id,
                     artifact ? 31U : 32U,
                     artifact ? publication.artifact_bytes
                              : publication.manifest_bytes});
  }

  // A provider can release receiver-visible signed work before its outgoing
  // toxcore terminal has been reaped. `unavailable` is therefore a bounded
  // retry signal, not terminal object truth. The retry keeps the scheduler
  // attempt but burns fresh message/FileId identities so publisher replay
  // cannot pin the transient refusal forever.
  const RequestLane refused_lane = lanes.front();
  auto unavailable = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::unavailable,
       refused_lane.request.kind, refused_lane.request.head_record,
       refused_lane.request.transfer_id},
      299U, refused_lane.message_id);
  IOTOX_CHECK(unavailable.ok());
  auto availability_retry = service.handle_object_result(
      peer, unavailable.value());
  IOTOX_CHECK(availability_retry.ok() &&
              availability_retry.value().size() == 1U);
  auto retried_request = iotox::sync::decode_sync_object_request(
      availability_retry.value().front().payload);
  IOTOX_CHECK(retried_request.ok());
  IOTOX_CHECK(availability_retry.value().front().message_id !=
              refused_lane.message_id);
  IOTOX_CHECK(retried_request.value().transfer_id !=
              refused_lane.request.transfer_id);
  lanes.front().request = retried_request.value();
  lanes.front().message_id = availability_retry.value().front().message_id;
  auto availability_state = service.snapshot();
  IOTOX_CHECK(availability_state.size() == 1U);
  IOTOX_CHECK(availability_state.front().object_result_retries == 1U);
  IOTOX_CHECK(availability_state.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  const auto stale_unavailable = service.handle_object_result(
      peer, unavailable.value());
  IOTOX_CHECK(!stale_unavailable.ok());
  IOTOX_CHECK(stale_unavailable.status().code() ==
              iotox::ErrorCode::not_found);
  IOTOX_CHECK(service.snapshot().front().state ==
              iotox::sync::SyncPullState::awaiting_objects);

  // File offers deliberately arrive before their small object-result frames.
  // The first exact offer also hits the global receive ceiling once; retry
  // must retain its FileId, file number, object, and scheduler attempt.
  admission_deferrals = 1U;
  std::optional<iotox::FileTransferRecord> deferred_offer;
  for (auto iterator = lanes.rbegin(); iterator != lanes.rend(); ++iterator) {
    iotox::FileTransferRecord offer;
    offer.direction = iotox::FileTransferDirection::incoming;
    offer.state = iotox::FileTransferState::offered;
    offer.friend_number = peer.transfer_carrier.friend_number;
    offer.file_number = iterator->file_number;
    offer.file_size = iterator->bytes;
    offer.file_id = iterator->request.transfer_id;
    offer.has_file_id = true;
    auto claimed = service.handle_offer(peer, offer);
    IOTOX_CHECK(claimed.ok() && claimed.value());
    if (!deferred_offer) deferred_offer = offer;
  }
  auto deferred_state = service.snapshot();
  IOTOX_CHECK(deferred_state.size() == 1U);
  IOTOX_CHECK(deferred_state.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(deferred_state.front().pending_offers == 1U);
  IOTOX_CHECK(deferred_state.front().admitted_offers == 1U);
  IOTOX_CHECK(deferred_state.front().admission_retries == 1U);
  IOTOX_CHECK(deferred_state.front().transfer_file_ids.size() == 2U);
  for (const RequestLane &lane : lanes) {
    IOTOX_CHECK(std::find(
                    deferred_state.front().transfer_file_ids.begin(),
                    deferred_state.front().transfer_file_ids.end(),
                    lane.request.transfer_id) !=
                deferred_state.front().transfer_file_ids.end());
  }
  IOTOX_CHECK(deferred_offer.has_value());
  auto retried_offer = service.handle_offer(peer, *deferred_offer);
  IOTOX_CHECK(retried_offer.ok() && retried_offer.value());
  deferred_state = service.snapshot();
  IOTOX_CHECK(deferred_state.front().pending_offers == 0U);
  IOTOX_CHECK(deferred_state.front().admitted_offers == 2U);
  IOTOX_CHECK(deferred_state.front().admission_retries == 1U);
  for (const RequestLane &lane : lanes) {
    auto result = iotox::sync::make_sync_object_result_frame(
        {iotox::sync::SyncObjectResultStatus::offered,
         lane.request.kind, lane.request.head_record,
         lane.request.transfer_id},
        300U + lane.file_number, lane.message_id);
    IOTOX_CHECK(result.ok());
    IOTOX_CHECK(service.handle_object_result(peer, result.value()).ok());
  }
  auto answered_retry = service.retry_pull(peer, configured.id);
  IOTOX_CHECK(answered_retry.ok() && answered_retry.value().empty());
  for (const RequestLane &lane : lanes) {
    iotox::FileTransferRecord terminal;
    terminal.direction = iotox::FileTransferDirection::incoming;
    terminal.state = iotox::FileTransferState::completed;
    terminal.friend_number = peer.transfer_carrier.friend_number;
    terminal.file_number = lane.file_number;
    terminal.file_size = sizes[lane.file_number];
    terminal.position = terminal.file_size;
    terminal.local_path = destinations[lane.file_number];
    IOTOX_CHECK(service.handle_terminal(
                    peer, terminal,
                    iotox::routes::WorkerTransferOutcome::completed,
                    iotox::ErrorCode::ok).ok());
  }

  const auto state = service.snapshot();
  IOTOX_CHECK(state.size() == 1U);
  IOTOX_CHECK(state.front().state == iotox::sync::SyncPullState::complete);
  IOTOX_CHECK(state.front().committed_objects == 2U);
  IOTOX_CHECK(state.front().detail.find("not activated") != std::string::npos);
  IOTOX_CHECK(service.namespace_mutation_ready(configured.id).ok());
  IOTOX_CHECK(!service.namespace_mutation_ready("Invalid").ok());
  iotox::sync::AcceptedHeadStore accepted(namespace_root);
  auto stored = accepted.load(configured, local.public_key(), crypto);
  IOTOX_CHECK(stored.ok() && stored.value().has_value());
  IOTOX_CHECK(stored.value()->generation == signed_head.value().generation);
  IOTOX_CHECK(std::filesystem::exists(iotox::sync::sync_object_path(
      configured, {iotox::sync::SyncObjectKind::artifact,
                   publication.artifact, publication.artifact_bytes})));
  IOTOX_CHECK(std::filesystem::exists(iotox::sync::sync_object_path(
      configured, {iotox::sync::SyncObjectKind::manifest,
                   publication.manifest, publication.manifest_bytes})));

  auto changed_authority = peer;
  changed_authority.authority.tail_digest[1U] ^= 0x80U;
  auto changed_retry = service.begin_pull(
      changed_authority, configured.id);
  IOTOX_CHECK(!changed_retry.ok());
  IOTOX_CHECK(changed_retry.status().code() ==
              iotox::ErrorCode::unavailable);

  IOTOX_CHECK(!service.cancel_pull(100U).ok());
  auto changed_policy = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::fail_closed,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(changed_policy.ok());
  const std::uint64_t changed_policy_job =
      changed_policy.value().message_id;
  IOTOX_CHECK(changed_policy_job != 0U && changed_policy_job != 100U);
  IOTOX_CHECK(service.cancel_pull(changed_policy_job).ok());
  auto replacement = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(replacement.ok());
  const std::uint64_t replacement_job = replacement.value().message_id;
  IOTOX_CHECK(replacement_job != 0U && replacement_job != 100U &&
              replacement_job != changed_policy_job);
  IOTOX_CHECK(service.cancel_pull(replacement_job).ok());
  IOTOX_CHECK(service.cancel_pull(replacement_job).ok());
  auto late_head = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, signed_head.value()},
      901U, replacement_job);
  IOTOX_CHECK(late_head.ok());
  auto late_result = service.handle_head_result(peer, late_head.value());
  IOTOX_CHECK(late_result.ok() && late_result.value().empty());
  const auto cancelled = service.snapshot();
  IOTOX_CHECK(cancelled.size() == 1U);
  IOTOX_CHECK(cancelled.front().job_id == replacement_job);
  IOTOX_CHECK(cancelled.front().state ==
              iotox::sync::SyncPullState::cancelled);
  IOTOX_CHECK(cancelled.front().cancellation_settled);
  IOTOX_CHECK(cancelled.front().detail.find("transfers fenced") !=
              std::string::npos);
  IOTOX_CHECK(service.namespace_mutation_ready(configured.id).ok());

  auto successor = iotox::sync::create_signed_head(
      configured, publication, signed_head.value(), remote, crypto);
  IOTOX_CHECK(successor.ok() && successor.value().generation == 2U);

  const iotox::sync::SyncObjectRecord artifact_object{
      iotox::sync::SyncObjectKind::artifact,
      publication.artifact, publication.artifact_bytes};
  const iotox::sync::SyncObjectRecord manifest_object{
      iotox::sync::SyncObjectKind::manifest,
      publication.manifest, publication.manifest_bytes};
  const auto artifact_object_path =
      iotox::sync::sync_object_path(configured, artifact_object);
  const auto manifest_object_path =
      iotox::sync::sync_object_path(configured, manifest_object);
  IOTOX_CHECK(std::filesystem::remove(artifact_object_path));
  auto partial_request = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(partial_request.ok());
  const std::uint64_t partial_job = partial_request.value().message_id;
  auto partial_head = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, successor.value()},
      902U, partial_job);
  IOTOX_CHECK(partial_head.ok());
  auto partial_requests = service.handle_head_result(
      peer, partial_head.value());
  IOTOX_CHECK(partial_requests.ok() &&
              partial_requests.value().size() == 1U);
  auto partial_lane = iotox::sync::decode_sync_object_request(
      partial_requests.value().front().payload);
  IOTOX_CHECK(partial_lane.ok());
  IOTOX_CHECK(partial_lane.value().kind ==
              iotox::sync::SyncObjectKind::artifact);
  const auto partial_state = service.snapshot();
  IOTOX_CHECK(partial_state.size() == 1U);
  IOTOX_CHECK(partial_state.front().job_id == partial_job);
  IOTOX_CHECK(partial_state.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(partial_state.front().requested_objects == 1U);
  IOTOX_CHECK(partial_state.front().admitted_offers == 0U);
  IOTOX_CHECK(partial_state.front().committed_objects == 1U);
  IOTOX_CHECK(partial_state.front().transfer_file_ids.size() == 1U);
  IOTOX_CHECK(partial_state.front().transfer_file_ids.front() ==
              partial_lane.value().transfer_id);
  IOTOX_CHECK(partial_state.front().detail.find("reused locally") !=
              std::string::npos);

  auto partial_result = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered,
       partial_lane.value().kind, partial_lane.value().head_record,
       partial_lane.value().transfer_id},
      905U, partial_requests.value().front().message_id);
  IOTOX_CHECK(partial_result.ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, partial_result.value()).ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, partial_result.value()).ok());
  auto conflicting_result = partial_result.value();
  ++conflicting_result.message_id;
  const auto conflict = service.handle_object_result(
      peer, conflicting_result);
  IOTOX_CHECK(!conflict.ok());
  IOTOX_CHECK(conflict.status().code() ==
              iotox::ErrorCode::protocol_error);
  const auto conflicted_state = service.snapshot();
  IOTOX_CHECK(conflicted_state.size() == 1U);
  IOTOX_CHECK(conflicted_state.front().job_id == partial_job);
  IOTOX_CHECK(conflicted_state.front().state ==
              iotox::sync::SyncPullState::failed);
  IOTOX_CHECK(conflicted_state.front().detail.find("replay conflicted") !=
              std::string::npos);
  IOTOX_CHECK(cancellations == 0U);
  IOTOX_CHECK(std::filesystem::remove(manifest_object_path));

  auto active_request = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(active_request.ok());
  const std::uint64_t active_job = active_request.value().message_id;
  auto successor_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, successor.value()},
      903U, active_job);
  IOTOX_CHECK(successor_result.ok());
  auto active_requests = service.handle_head_result(
      peer, successor_result.value());
  IOTOX_CHECK(active_requests.ok() && active_requests.value().size() == 2U);

  std::vector<iotox::FileTransferRecord> active_transfers;
  std::uint32_t active_file_number = 41U;
  admission_deferrals = 1U;
  for (const auto &active_frame : active_requests.value()) {
    auto active_lane = iotox::sync::decode_sync_object_request(
        active_frame.payload);
    IOTOX_CHECK(active_lane.ok());
    iotox::FileTransferRecord offer;
    offer.direction = iotox::FileTransferDirection::incoming;
    offer.state = iotox::FileTransferState::offered;
    offer.friend_number = peer.transfer_carrier.friend_number;
    offer.file_number = active_file_number++;
    offer.file_size = active_lane.value().kind ==
                              iotox::sync::SyncObjectKind::artifact
                          ? publication.artifact_bytes
                          : publication.manifest_bytes;
    offer.file_id = active_lane.value().transfer_id;
    offer.has_file_id = true;
    auto claimed = service.handle_offer(peer, offer);
    IOTOX_CHECK(claimed.ok() && claimed.value());
    active_transfers.push_back(offer);
  }
  IOTOX_CHECK(cancellations == 0U);
  std::size_t admitted_paths = 0U;
  for (const auto &transfer : active_transfers) {
    if (destinations.contains(transfer.file_number) &&
        std::filesystem::exists(destinations[transfer.file_number])) {
      ++admitted_paths;
    }
  }
  IOTOX_CHECK(admitted_paths == 1U);
  const auto one_pending = service.snapshot();
  IOTOX_CHECK(one_pending.front().pending_offers == 1U);
  IOTOX_CHECK(one_pending.front().admitted_offers == 1U);
  IOTOX_CHECK(one_pending.front().admission_retries == 1U);
  iotox::sync::SyncAttemptStore active_attempts(namespace_root);
  auto attempt_truth = active_attempts.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(attempt_truth.ok() &&
              attempt_truth.value().active.size() == 1U);

  cancellation_failures = 1U;
  IOTOX_CHECK(!service.cancel_pull(active_job).ok());
  const auto cleanup_pending = service.snapshot();
  IOTOX_CHECK(cleanup_pending.front().state ==
              iotox::sync::SyncPullState::cancelled);
  IOTOX_CHECK(!cleanup_pending.front().cancellation_settled);
  IOTOX_CHECK(cleanup_pending.front().pending_offers == 0U);
  IOTOX_CHECK(cleanup_pending.front().detail.find(
                  "local cleanup fenced") != std::string::npos);
  IOTOX_CHECK(service.cancel_pull(active_job).ok());
  IOTOX_CHECK(service.snapshot().front().cancellation_settled);
  IOTOX_CHECK(cancellations == 2U);
  for (const auto &transfer : active_transfers) {
    IOTOX_CHECK(!std::filesystem::exists(
        destinations[transfer.file_number]));
  }
  attempt_truth = active_attempts.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(attempt_truth.ok() && attempt_truth.value().active.empty());
  iotox::FileTransferRecord late_transfer = active_transfers.front();
  late_transfer.state = iotox::FileTransferState::completed;
  late_transfer.local_path = destinations[late_transfer.file_number];
  IOTOX_CHECK(!service.handle_terminal(
      peer, late_transfer,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok).ok());
  auto retained_head = accepted.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(retained_head.ok() && retained_head.value().has_value());
  IOTOX_CHECK(retained_head.value()->generation == 1U);
  const auto active_cancelled = service.snapshot();
  IOTOX_CHECK(active_cancelled.size() == 1U);
  IOTOX_CHECK(active_cancelled.front().job_id == active_job);
  IOTOX_CHECK(active_cancelled.front().state ==
              iotox::sync::SyncPullState::cancelled);

  auto disconnect_request = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(disconnect_request.ok());
  const std::uint64_t disconnect_job =
      disconnect_request.value().message_id;
  auto disconnect_head = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, successor.value()},
      904U, disconnect_job);
  IOTOX_CHECK(disconnect_head.ok());
  auto disconnect_requests = service.handle_head_result(
      peer, disconnect_head.value());
  IOTOX_CHECK(disconnect_requests.ok() &&
              disconnect_requests.value().size() == 2U);
  std::vector<iotox::FileTransferRecord> disconnect_transfers;
  std::uint32_t disconnect_file_number = 51U;
  for (const auto &disconnect_frame : disconnect_requests.value()) {
    auto lane = iotox::sync::decode_sync_object_request(
        disconnect_frame.payload);
    IOTOX_CHECK(lane.ok());
    iotox::FileTransferRecord offer;
    offer.direction = iotox::FileTransferDirection::incoming;
    offer.state = iotox::FileTransferState::offered;
    offer.friend_number = peer.transfer_carrier.friend_number;
    offer.file_number = disconnect_file_number++;
    offer.file_size = lane.value().kind ==
                              iotox::sync::SyncObjectKind::artifact
                          ? publication.artifact_bytes
                          : publication.manifest_bytes;
    offer.file_id = lane.value().transfer_id;
    offer.has_file_id = true;
    auto claimed = service.handle_offer(peer, offer);
    IOTOX_CHECK(claimed.ok() && claimed.value());
    disconnect_transfers.push_back(offer);
  }
  cancellation_failures = 1U;
  service.peer_offline(peer.friend_number, peer.online_epoch);
  const auto disconnected = service.snapshot();
  IOTOX_CHECK(disconnected.size() == 1U);
  IOTOX_CHECK(disconnected.front().job_id == disconnect_job);
  IOTOX_CHECK(disconnected.front().state ==
              iotox::sync::SyncPullState::failed);
  IOTOX_CHECK(disconnected.front().detail.find("peer went offline") !=
              std::string::npos);
  IOTOX_CHECK(disconnected.front().detail.find("requires retry") !=
              std::string::npos);
  IOTOX_CHECK(cancellations == 4U);
  for (const auto &transfer : disconnect_transfers) {
    IOTOX_CHECK(!std::filesystem::exists(
        destinations[transfer.file_number]));
  }
  attempt_truth = active_attempts.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(attempt_truth.ok() && attempt_truth.value().active.empty());

  auto recovered_peer = peer;
  ++recovered_peer.online_epoch;
  recovered_peer.peer_authority.online_epoch =
      recovered_peer.online_epoch;
  recovered_peer.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::primary;
  recovered_peer.transfer_carrier.route_key =
      recovered_peer.authority_route_key;
  recovered_peer.transfer_carrier.friend_number =
      recovered_peer.friend_number;
  recovered_peer.transfer_carrier.worker_id =
      recovered_peer.online_epoch;
  recovered_peer.transfer_carrier.online_epoch =
      recovered_peer.online_epoch;
  recovered_peer.transfer_carrier.remote_route_generation = 0U;
  recovered_peer.transfer_carrier.remote_coordinator_route_key.fill(0U);
  recovered_peer.transfer_carrier.primary_authority_online_epoch = 0U;
  auto recovered_request = service.begin_pull(
      recovered_peer, configured.id);
  IOTOX_CHECK(recovered_request.ok());
  IOTOX_CHECK(recovered_request.value().message_id != disconnect_job);
  IOTOX_CHECK(cancellations == 4U);
}

IOTOX_TEST("sync subscriber reconstructs one range and falls back from a corrupt accepted basis") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto local = identity(temporary.path() / "local.identity", crypto);
  auto remote = identity(temporary.path() / "remote.identity", crypto);
  const auto namespace_root = temporary.path() / "namespace";
  IOTOX_CHECK(std::filesystem::create_directories(namespace_root));
  IOTOX_CHECK(::chmod(namespace_root.c_str(), S_IRWXU) == 0);
  auto configured = policy(namespace_root, remote.public_key());
  // One manifest plus an initial range and three replacement carriers need
  // five retained scheduler records. This verifies that the subscriber uses
  // the explicit namespace ceiling instead of its historical constant four.
  configured.quotas.maximum_outstanding_requests = 5U;
  configured.quotas.maximum_artifact_bytes = 16384U;
  configured.quotas.maximum_store_bytes = 131072U;
  configured.quotas.maximum_staging_bytes = 32768U;

  std::string basis_bytes(16384U, '\0');
  for (std::size_t index = 0U; index < basis_bytes.size(); ++index) {
    basis_bytes[index] = static_cast<char>(
        (index * 29U + index / 31U + 7U) & 0xffU);
  }
  std::string target_bytes = basis_bytes;
  std::fill(target_bytes.begin() + 1536,
            target_bytes.begin() + 1792, '\x5a');
  const auto basis_source = temporary.path() / "basis";
  const auto target_source = temporary.path() / "target";
  const auto basis_manifest_source = temporary.path() / "basis.index";
  const auto target_manifest_source = temporary.path() / "target.index";
  write_private(basis_source, basis_bytes);
  write_private(target_source, target_bytes);
  auto basis_manifest = iotox::sync::build_sync_range_manifest(
      configured, basis_source, basis_manifest_source);
  auto target_manifest = iotox::sync::build_sync_range_manifest(
      configured, target_source, target_manifest_source);
  IOTOX_CHECK(basis_manifest.ok() && target_manifest.ok());
  auto basis_manifest_digest =
      iotox::sync::hash_sync_file_sha256(basis_manifest_source);
  auto target_manifest_digest =
      iotox::sync::hash_sync_file_sha256(target_manifest_source);
  IOTOX_CHECK(basis_manifest_digest.ok() && target_manifest_digest.ok());

  iotox::sync::SignedHeadPublicationRequest basis_publication;
  basis_publication.artifact = basis_manifest.value().artifact;
  basis_publication.manifest = basis_manifest_digest.value();
  basis_publication.artifact_bytes = basis_bytes.size();
  basis_publication.manifest_bytes = basis_manifest.value().manifest_bytes;
  auto basis_head = iotox::sync::create_signed_head(
      configured, basis_publication, std::nullopt, remote, crypto);
  IOTOX_CHECK(basis_head.ok());
  iotox::sync::SignedHeadPublicationRequest target_publication;
  target_publication.artifact = target_manifest.value().artifact;
  target_publication.manifest = target_manifest_digest.value();
  target_publication.artifact_bytes = target_bytes.size();
  target_publication.manifest_bytes = target_manifest.value().manifest_bytes;
  auto target_head = iotox::sync::create_signed_head(
      configured, target_publication, basis_head.value(), remote, crypto);
  IOTOX_CHECK(target_head.ok());

  auto basis_candidate = iotox::sync::verified_candidate_head(
      configured, basis_head.value(), crypto);
  IOTOX_CHECK(basis_candidate.ok());
  iotox::sync::AcceptedHeadStore accepted(namespace_root);
  auto accepted_basis = accepted.accept(
      configured, basis_candidate.value(), local, crypto);
  IOTOX_CHECK(accepted_basis.ok() && accepted_basis.value().accepted());
  const iotox::sync::SyncObjectRecord basis_object{
      iotox::sync::SyncObjectKind::artifact,
      basis_publication.artifact, basis_publication.artifact_bytes};
  const auto objects = namespace_root / "objects";
  IOTOX_CHECK(std::filesystem::create_directories(objects));
  IOTOX_CHECK(::chmod(objects.c_str(), S_IRWXU) == 0);
  IOTOX_CHECK(std::filesystem::copy_file(
      basis_source,
      iotox::sync::sync_object_path(configured, basis_object)));
  IOTOX_CHECK(::chmod(iotox::sync::sync_object_path(
                          configured, basis_object).c_str(),
                      S_IRUSR | S_IWUSR) == 0);

  std::ifstream manifest_input(target_manifest_source, std::ios::binary);
  std::ostringstream manifest_stream;
  manifest_stream << manifest_input.rdbuf();
  const std::string manifest_bytes = manifest_stream.str();
  std::map<std::uint32_t, std::string> incoming;
  std::map<std::uint32_t, std::filesystem::path> destinations;
  std::map<std::uint32_t, std::uint64_t> resume_offsets;
  std::uint64_t next_message_id = 1000U;
  std::uint8_t next_file_id = 0x81U;
  std::uint64_t admission_deferrals = 0U;
  std::uint64_t cancellations = 0U;
  std::uint64_t retirements = 0U;
  bool retirement_publishes_content = true;
  iotox::sync::SyncSubscriberSeams seams;
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return next_message_id++;
  };
  seams.make_file_id = [&]() -> iotox::Result<iotox::FileId> {
    iotox::FileId value{};
    value.fill(next_file_id++);
    return value;
  };
  seams.receive_to_path = [&](const iotox::sync::SyncTransferCarrier &carrier,
                              std::uint32_t file_number,
                              const std::filesystem::path &destination) {
    if (admission_deferrals != 0U) {
      --admission_deferrals;
      return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
          iotox::ErrorCode::resource_exhausted,
          "injected Agent receive-ceiling admission deferral"}};
    }
    const auto content = incoming.find(file_number);
    if (content == incoming.end()) {
      return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
          iotox::ErrorCode::not_found, "missing range fixture"}};
    }
    write_private(destination, content->second);
    destinations[file_number] = destination;
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::active;
    record.friend_number = carrier.friend_number;
    record.file_number = file_number;
    record.file_size = content->second.size();
    record.local_path = destination;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.receive_to_path_from_offset =
      [&](const iotox::sync::SyncTransferCarrier &carrier,
          std::uint32_t file_number,
          const std::filesystem::path &destination,
          std::uint64_t resume_offset) {
        if (resume_offset == 0U) {
          if (admission_deferrals != 0U) {
            --admission_deferrals;
            return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
                iotox::ErrorCode::resource_exhausted,
                "injected Agent receive-ceiling admission deferral"}};
          }
          const auto initial = incoming.find(file_number);
          if (initial == incoming.end()) {
            return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
                iotox::ErrorCode::not_found, "missing range fixture"}};
          }
          if (!std::filesystem::exists(destination) ||
              std::filesystem::file_size(destination) != 0U) {
            return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
                iotox::ErrorCode::protocol_error,
                "initial range receive did not create an exact empty partial"}};
          }
          write_private(destination, initial->second);
          destinations[file_number] = destination;
          resume_offsets[file_number] = 0U;
          iotox::FileTransferRecord record;
          record.direction = iotox::FileTransferDirection::incoming;
          record.state = iotox::FileTransferState::active;
          record.friend_number = carrier.friend_number;
          record.file_number = file_number;
          record.file_size = initial->second.size();
          record.local_path = destination;
          return iotox::Result<iotox::FileTransferRecord>{record};
        }
        if (admission_deferrals != 0U) {
          --admission_deferrals;
          return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
              iotox::ErrorCode::resource_exhausted,
              "injected retained-prefix admission deferral"}};
        }
        const auto content = incoming.find(file_number);
        if (content == incoming.end() ||
            resume_offset >= content->second.size() ||
            std::filesystem::file_size(destination) != resume_offset) {
          return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
              iotox::ErrorCode::protocol_error,
              "invalid retained range fixture"}};
        }
        std::ofstream output(
            destination, std::ios::binary | std::ios::app);
        output.write(
            content->second.data() +
                static_cast<std::ptrdiff_t>(resume_offset),
            static_cast<std::streamsize>(
                content->second.size() - resume_offset));
        output.close();
        destinations[file_number] = destination;
        resume_offsets[file_number] = resume_offset;
        iotox::FileTransferRecord record;
        record.direction = iotox::FileTransferDirection::incoming;
        record.state = iotox::FileTransferState::active;
        record.friend_number = carrier.friend_number;
        record.file_number = file_number;
        record.file_size = content->second.size();
        record.position = resume_offset;
        record.local_path = destination;
        return iotox::Result<iotox::FileTransferRecord>{record};
      };
  seams.cancel_transfer = [&](const iotox::sync::SyncTransferCarrier &,
                              std::uint32_t) {
    ++cancellations;
    return iotox::Status::success();
  };
  seams.retire_transfer = [&destinations, &incoming, &retirements,
                           &retirement_publishes_content](
      const iotox::sync::SyncTransferCarrier &,
      std::uint32_t file_number) {
    ++retirements;
    const auto destination = destinations.find(file_number);
    const auto content = incoming.find(file_number);
    if (retirement_publishes_content &&
        destination != destinations.end() && content != incoming.end()) {
      // Model the transport-owned receive still publishing local state as the
      // parent carrier fence arrives. Subscriber cleanup must happen after
      // this local-only retirement boundary.
      write_private(destination->second, content->second);
    }
    return iotox::Status::success();
  };
  seams.install.hash_file = iotox::sync::hash_sync_file_sha256;
  iotox::sync::SyncSubscriberService::Config service_config;
  service_config.identity = &local;
  service_config.sodium = &crypto;
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SyncSubscriberService service(
      registry, std::move(seams), service_config);
  auto peer = context(remote.public_key());
  peer.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::auxiliary;
  peer.transfer_carrier.route_key.fill(0x93U);
  peer.transfer_carrier.worker_id = 0x9003U;
  peer.transfer_carrier.friend_number = peer.friend_number;
  peer.transfer_carrier.online_epoch = peer.online_epoch;
  peer.transfer_carrier.remote_route_generation = 5U;
  peer.transfer_carrier.remote_coordinator_route_key =
      peer.authority_route_key;
  peer.transfer_carrier.primary_authority_online_epoch =
      peer.online_epoch;
  peer.range_transfer_negotiated = true;

  auto head_request = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::fail_closed,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(head_request.ok());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, target_head.value()},
      1100U, head_request.value().message_id);
  IOTOX_CHECK(head_result.ok());
  auto manifest_requests = service.handle_head_result(
      peer, head_result.value());
  IOTOX_CHECK(manifest_requests.ok() &&
              manifest_requests.value().size() == 1U);
  auto manifest_request = iotox::sync::decode_sync_object_request(
      manifest_requests.value().front().payload);
  IOTOX_CHECK(manifest_request.ok());
  IOTOX_CHECK(manifest_request.value().kind ==
              iotox::sync::SyncObjectKind::manifest);
  incoming[70U] = manifest_bytes;
  iotox::FileTransferRecord manifest_offer;
  manifest_offer.direction = iotox::FileTransferDirection::incoming;
  manifest_offer.state = iotox::FileTransferState::offered;
  manifest_offer.friend_number = peer.friend_number;
  manifest_offer.file_number = 70U;
  manifest_offer.file_size = manifest_bytes.size();
  manifest_offer.file_id = manifest_request.value().transfer_id;
  manifest_offer.has_file_id = true;
  auto manifest_claimed = service.handle_offer(peer, manifest_offer);
  IOTOX_CHECK(manifest_claimed.ok() && manifest_claimed.value());

  // A range-capable pull is not yet a range-bundle pull while its signed
  // manifest prerequisite is live. Carrier loss must retire and discard the
  // whole-object receive through its coordinator, leaving no staging, and
  // must not misclassify the manifest as a range bundle.
  const std::uint64_t prerequisite_job =
      head_request.value().message_id;
  const auto prerequisite_staging = destinations[70U];
  IOTOX_CHECK(std::filesystem::exists(prerequisite_staging));
  auto prerequisite_active = service.snapshot();
  IOTOX_CHECK(prerequisite_active.size() == 1U);
  IOTOX_CHECK(prerequisite_active.front().range_transfer);
  IOTOX_CHECK(!prerequisite_active.front().range_lane_active);
  IOTOX_CHECK(prerequisite_active.front().range_attempt_id == 0U);
  IOTOX_CHECK(prerequisite_active.front().range_bundle_bytes == 0U);
  IOTOX_CHECK(service.carrier_offline(peer.transfer_carrier).ok());
  auto prerequisite_blocked = service.snapshot();
  IOTOX_CHECK(prerequisite_blocked.size() == 1U);
  IOTOX_CHECK(prerequisite_blocked.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(prerequisite_blocked.front().detail.find(
                  "prerequisite carrier lost") != std::string::npos);
  IOTOX_CHECK(prerequisite_blocked.front().detail.find(
                  "fail-closed pull blocked") != std::string::npos);
  IOTOX_CHECK(!std::filesystem::exists(prerequisite_staging));
  IOTOX_CHECK(cancellations == 0U);
  IOTOX_CHECK(retirements == 1U);
  IOTOX_CHECK(service.cancel_pull(prerequisite_job).ok());
  IOTOX_CHECK(service.snapshot().front().cancellation_settled);

  head_request = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::fail_closed,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(head_request.ok());
  IOTOX_CHECK(head_request.value().message_id != prerequisite_job);
  head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, target_head.value()},
      1104U, head_request.value().message_id);
  IOTOX_CHECK(head_result.ok());
  manifest_requests = service.handle_head_result(peer, head_result.value());
  IOTOX_CHECK(manifest_requests.ok() &&
              manifest_requests.value().size() == 1U);
  manifest_request = iotox::sync::decode_sync_object_request(
      manifest_requests.value().front().payload);
  IOTOX_CHECK(manifest_request.ok());
  IOTOX_CHECK(manifest_request.value().kind ==
              iotox::sync::SyncObjectKind::manifest);
  incoming[74U] = manifest_bytes;
  manifest_offer.file_number = 74U;
  manifest_offer.file_id = manifest_request.value().transfer_id;
  manifest_claimed = service.handle_offer(peer, manifest_offer);
  IOTOX_CHECK(manifest_claimed.ok() && manifest_claimed.value());

  auto manifest_result = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered,
       manifest_request.value().kind,
       manifest_request.value().head_record,
       manifest_request.value().transfer_id},
      1101U, manifest_requests.value().front().message_id);
  IOTOX_CHECK(manifest_result.ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, manifest_result.value()).ok());
  iotox::FileTransferRecord manifest_terminal = manifest_offer;
  manifest_terminal.state = iotox::FileTransferState::completed;
  manifest_terminal.local_path = destinations[74U];
  auto range_requests = service.handle_terminal(
      peer, manifest_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(range_requests.ok(), range_requests.status().message());
  IOTOX_CHECK(range_requests.value().size() == 1U);
  IOTOX_CHECK(range_requests.value().front().type ==
              iotox::protocol::MessageType::sync_range_request);
  auto range_request = iotox::sync::decode_sync_range_request(
      range_requests.value().front().payload);
  IOTOX_CHECK(range_request.ok());
  const auto initial_ranges = range_request.value().ranges;
  std::string range_bundle;
  for (const iotox::sync::SyncRangeRecord &range :
       range_request.value().ranges) {
    range_bundle.append(
        target_bytes.substr(static_cast<std::size_t>(range.offset),
                            static_cast<std::size_t>(range.length)));
  }
  IOTOX_CHECK(!range_bundle.empty());
  IOTOX_CHECK(range_bundle.size() < target_bytes.size());
  incoming[71U] = range_bundle;
  iotox::FileTransferRecord range_offer;
  range_offer.direction = iotox::FileTransferDirection::incoming;
  range_offer.state = iotox::FileTransferState::offered;
  range_offer.friend_number = peer.friend_number;
  range_offer.file_number = 71U;
  range_offer.file_size = range_bundle.size();
  range_offer.file_id = range_request.value().transfer_id;
  range_offer.has_file_id = true;
  admission_deferrals = 1U;
  auto range_claimed = service.handle_offer(peer, range_offer);
  IOTOX_CHECK_MSG(range_claimed.ok(), range_claimed.status().message());
  IOTOX_CHECK(range_claimed.value());
  auto range_deferred = service.snapshot();
  IOTOX_CHECK(range_deferred.size() == 1U);
  IOTOX_CHECK(std::find(
                  range_deferred.front().transfer_file_ids.begin(),
                  range_deferred.front().transfer_file_ids.end(),
                  range_request.value().transfer_id) !=
              range_deferred.front().transfer_file_ids.end());
  IOTOX_CHECK(range_deferred.front().pending_offers == 1U);
  IOTOX_CHECK(range_deferred.front().admission_retries == 1U);
  IOTOX_CHECK(!destinations.contains(range_offer.file_number));
  range_claimed = service.handle_offer(peer, range_offer);
  IOTOX_CHECK_MSG(range_claimed.ok(), range_claimed.status().message());
  IOTOX_CHECK(range_claimed.value());
  range_deferred = service.snapshot();
  IOTOX_CHECK(range_deferred.front().pending_offers == 0U);
  IOTOX_CHECK(range_deferred.front().admission_retries == 1U);
  IOTOX_CHECK(range_deferred.front().range_lane_active);
  IOTOX_CHECK(range_deferred.front().range_attempt_id != 0U);
  IOTOX_CHECK(range_deferred.front().range_bundle_bytes ==
              range_bundle.size());
  auto range_result = iotox::sync::make_sync_range_result_frame(
      {iotox::sync::SyncRangeResultStatus::offered,
       range_request.value().head_record,
       range_request.value().transfer_id},
      1102U, range_requests.value().front().message_id);
  IOTOX_CHECK(range_result.ok());
  IOTOX_CHECK(service.handle_range_result(peer, range_result.value()).ok());

  const std::uint64_t lost_job = head_request.value().message_id;
  const auto lost_staging = destinations[71U];
  IOTOX_CHECK(std::filesystem::exists(lost_staging));
  IOTOX_CHECK(service.carrier_offline(peer.transfer_carrier).ok());
  const auto blocked = service.snapshot();
  IOTOX_CHECK(blocked.size() == 1U);
  IOTOX_CHECK(blocked.front().job_id == lost_job);
  IOTOX_CHECK(blocked.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(blocked.front().route_failover_policy ==
              iotox::sync::SyncRouteFailoverPolicy::fail_closed);
  IOTOX_CHECK(blocked.front().route_class ==
              iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(blocked.front().detail.find("fail-closed pull blocked") !=
              std::string::npos);
  IOTOX_CHECK(std::find(
                  blocked.front().transfer_file_ids.begin(),
                  blocked.front().transfer_file_ids.end(),
                  range_offer.file_id) ==
              blocked.front().transfer_file_ids.end());
  IOTOX_CHECK(blocked.front().range_discarded_bytes == range_bundle.size());
  IOTOX_CHECK(!std::filesystem::exists(lost_staging));
  IOTOX_CHECK(cancellations == 0U);
  IOTOX_CHECK(retirements == 2U);

  iotox::FileTransferRecord stale_terminal = range_offer;
  stale_terminal.state = iotox::FileTransferState::completed;
  stale_terminal.position = range_bundle.size();
  stale_terminal.local_path = lost_staging;
  auto stale = service.handle_terminal(
      peer, stale_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK(!stale.ok());
  IOTOX_CHECK(stale.status().code() == iotox::ErrorCode::not_found);
  IOTOX_CHECK(service.snapshot().front().state ==
              iotox::sync::SyncPullState::awaiting_objects);

  IOTOX_CHECK(service.cancel_pull(lost_job).ok());
  IOTOX_CHECK(service.snapshot().front().cancellation_settled);

  // A digest-named prerequisite is reusable only after exact local proof.
  // Corrupt bytes at that immutable path must fail the fresh job locally;
  // they are never hidden by asking the publisher for a replacement.
  const iotox::sync::SyncObjectRecord target_manifest_object{
      iotox::sync::SyncObjectKind::manifest,
      target_publication.manifest, target_publication.manifest_bytes};
  const auto target_manifest_path =
      iotox::sync::sync_object_path(configured, target_manifest_object);
  write_private(target_manifest_path,
                std::string(manifest_bytes.size(), '\x45'));
  auto corrupt_manifest_job = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::fail_closed,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(corrupt_manifest_job.ok());
  auto corrupt_manifest_head = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, target_head.value()},
      1109U, corrupt_manifest_job.value().message_id);
  IOTOX_CHECK(corrupt_manifest_head.ok());
  auto corrupt_manifest_result = service.handle_head_result(
      peer, corrupt_manifest_head.value());
  IOTOX_CHECK(!corrupt_manifest_result.ok());
  IOTOX_CHECK(corrupt_manifest_result.status().code() ==
              iotox::ErrorCode::protocol_error);
  const auto corrupt_manifest_state = service.snapshot();
  IOTOX_CHECK(corrupt_manifest_state.size() == 1U);
  IOTOX_CHECK(corrupt_manifest_state.front().state ==
              iotox::sync::SyncPullState::failed);
  IOTOX_CHECK(corrupt_manifest_state.front().requested_objects == 0U);
  write_private(target_manifest_path, manifest_bytes);

  // Model an abrupt daemon exit after a positive range-bundle prefix. ATM1
  // keeps the exact locally derived plan commitment and bundle length. Startup
  // classifies the bytes as restart-retained; the next authorized pull must
  // independently derive the same plan before it can hand them to a fresh
  // attempt, message ID, and FileId.
  const iotox::sync::SyncObjectRecord target_object{
      iotox::sync::SyncObjectKind::artifact,
      target_publication.artifact, target_publication.artifact_bytes};
  iotox::sync::SyncRangePlan restart_plan;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto planned = iotox::sync::plan_sync_range_reconstruction(
        configured, target_object, target_manifest_object, basis_object,
        transaction.value(),
        iotox::sync::SyncInstallSeams{
            iotox::sync::hash_sync_file_sha256, {}, {}, {}});
    IOTOX_CHECK(planned.ok());
    restart_plan = std::move(planned).value();
  }
  IOTOX_CHECK(restart_plan.missing_bytes == range_bundle.size());
  const std::uint64_t restart_prefix_bytes = range_bundle.size() / 2U;
  iotox::sync::SyncAttemptStore restart_attempts(namespace_root);
  auto crashed_attempt_id = restart_attempts.reserve_attempt_id(
      configured, local, crypto);
  IOTOX_CHECK(crashed_attempt_id.ok());
  auto crashed_attempt = iotox::sync::make_durable_range_attempt(
      crashed_attempt_id.value(), restart_plan,
      iotox::sync::DurableSyncAttemptState::active, crypto);
  IOTOX_CHECK(crashed_attempt.ok());
  IOTOX_CHECK(restart_attempts.begin(
                  configured, crashed_attempt.value(), local, crypto).ok());
  std::filesystem::path crashed_prefix;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto partial = iotox::sync::create_sync_attempt_partial(
        configured, crashed_attempt_id.value(), target_object,
        transaction.value());
    IOTOX_CHECK(partial.ok());
    crashed_prefix = partial.value().path;
    write_private(crashed_prefix,
                  range_bundle.substr(0U, restart_prefix_bytes));
  }
  iotox::sync::SyncInstallSeams recovery_seams;
  recovery_seams.hash_file = iotox::sync::hash_sync_file_sha256;
  auto recovered_range = restart_attempts.recover(
      configured, local, crypto, recovery_seams);
  IOTOX_CHECK(recovered_range.ok() && recovered_range.value().size() == 1U);
  IOTOX_CHECK(recovered_range.value().front().disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::retained);
  IOTOX_CHECK(std::filesystem::file_size(crashed_prefix) ==
              restart_prefix_bytes);

  head_request = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::fail_closed,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(head_request.ok());
  IOTOX_CHECK(head_request.value().message_id != lost_job);
  head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, target_head.value()},
      1110U, head_request.value().message_id);
  IOTOX_CHECK(head_result.ok());
  // The failed range job durably committed its exact immutable manifest
  // before carrier loss. A fresh job proves and reuses that prerequisite,
  // then emits only a new bounded-range request. Failed range bytes remain
  // discarded and both the message and FileId identities are fresh.
  range_requests = service.handle_head_result(peer, head_result.value());
  IOTOX_CHECK_MSG(range_requests.ok(), range_requests.status().message());
  IOTOX_CHECK(range_requests.value().size() == 1U);
  IOTOX_CHECK(range_requests.value().front().type ==
              iotox::protocol::MessageType::sync_range_request);
  range_request = iotox::sync::decode_sync_range_request(
      range_requests.value().front().payload);
  IOTOX_CHECK(range_request.ok());
  IOTOX_CHECK(range_request.value().ranges == initial_ranges);
  IOTOX_CHECK(range_request.value().transfer_id !=
              range_offer.file_id);
  const auto manifest_reused = service.snapshot();
  IOTOX_CHECK(manifest_reused.size() == 1U);
  IOTOX_CHECK(manifest_reused.front().job_id ==
              head_request.value().message_id);
  IOTOX_CHECK(manifest_reused.front().requested_objects == 1U);
  IOTOX_CHECK(manifest_reused.front().committed_objects == 1U);
  IOTOX_CHECK(manifest_reused.front().range_lane_active);
  IOTOX_CHECK(manifest_reused.front().range_retained_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(manifest_reused.front().range_restart_resumed_attempts == 0U);
  const std::uint64_t restart_message_id =
      manifest_reused.front().range_message_id;
  IOTOX_CHECK(restart_message_id != 0U);
  IOTOX_CHECK(manifest_reused.front().detail.find(
                  "restart-retained range prefix") !=
              std::string::npos);
  incoming[76U] = range_bundle;
  range_offer.file_number = 76U;
  range_offer.file_id = range_request.value().transfer_id;
  admission_deferrals = 1U;
  range_claimed = service.handle_offer(peer, range_offer);
  IOTOX_CHECK(range_claimed.ok() && range_claimed.value());
  IOTOX_CHECK(!resume_offsets.contains(76U));
  const auto initial_range_deferred = service.snapshot();
  IOTOX_CHECK(initial_range_deferred.size() == 1U);
  IOTOX_CHECK(initial_range_deferred.front().pending_offers == 1U);
  IOTOX_CHECK(initial_range_deferred.front().range_retained_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(initial_range_deferred.front().range_retention_fallbacks == 0U);
  range_claimed = service.handle_offer(peer, range_offer);
  IOTOX_CHECK(range_claimed.ok() && range_claimed.value());
  IOTOX_CHECK(resume_offsets.contains(76U));
  IOTOX_CHECK(resume_offsets[76U] == restart_prefix_bytes);
  IOTOX_CHECK(!std::filesystem::exists(crashed_prefix));
  auto restart_admitted = service.snapshot();
  IOTOX_CHECK(restart_admitted.front().range_restart_resumed_attempts == 1U);
  IOTOX_CHECK(restart_admitted.front().range_restart_resumed_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(restart_admitted.front().range_restart_suffix_bytes ==
              range_bundle.size() - restart_prefix_bytes);
  range_result = iotox::sync::make_sync_range_result_frame(
      {iotox::sync::SyncRangeResultStatus::offered,
       range_request.value().head_record,
       range_request.value().transfer_id},
      1112U, range_requests.value().front().message_id);
  IOTOX_CHECK(range_result.ok());
  IOTOX_CHECK(service.handle_range_result(peer, range_result.value()).ok());

  iotox::FileTransferRecord range_terminal = range_offer;
  range_terminal.state = iotox::FileTransferState::failed;
  range_terminal.position = range_bundle.size() / 2U;
  range_terminal.local_path = destinations[76U];
  write_private(
      range_terminal.local_path,
      range_bundle.substr(0U, range_bundle.size() / 2U));
  auto retried = service.handle_terminal(
      peer, range_terminal,
      iotox::routes::WorkerTransferOutcome::failed,
      iotox::ErrorCode::io_error, "injected partial range failure");
  IOTOX_CHECK_MSG(retried.ok(), retried.status().message());
  IOTOX_CHECK(retried.value().size() == 1U);
  IOTOX_CHECK(retried.value().front().type ==
              iotox::protocol::MessageType::sync_range_request);
  auto retry_request = iotox::sync::decode_sync_range_request(
      retried.value().front().payload);
  IOTOX_CHECK(retry_request.ok());
  IOTOX_CHECK(retry_request.value().ranges == range_request.value().ranges);
  IOTOX_CHECK(retry_request.value().head_record ==
              range_request.value().head_record);
  IOTOX_CHECK(retry_request.value().transfer_id !=
              range_request.value().transfer_id);
  IOTOX_CHECK(!std::filesystem::exists(destinations[76U]));
  IOTOX_CHECK(cancellations == 0U);
  const auto retained_retry = service.snapshot();
  IOTOX_CHECK(retained_retry.size() == 1U);
  IOTOX_CHECK(retained_retry.front().range_retained_bytes ==
              restart_prefix_bytes + range_bundle.size() / 2U);
  IOTOX_CHECK(retained_retry.front().range_resumed_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(retained_retry.front().range_restart_resumed_attempts == 1U);
  IOTOX_CHECK(retained_retry.front().range_restart_resumed_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(retained_retry.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(retained_retry.front().range_retention_fallbacks == 0U);
  auto accepted_during_retry = accepted.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(accepted_during_retry.ok() &&
              accepted_during_retry.value().has_value());
  IOTOX_CHECK(accepted_during_retry.value()->generation == 1U);

  incoming[72U] = range_bundle;
  iotox::FileTransferRecord retry_offer = range_offer;
  retry_offer.file_number = 72U;
  retry_offer.file_id = retry_request.value().transfer_id;
  admission_deferrals = 1U;
  auto retry_claimed = service.handle_offer(peer, retry_offer);
  IOTOX_CHECK(retry_claimed.ok() && retry_claimed.value());
  IOTOX_CHECK(!resume_offsets.contains(72U));
  const auto retained_deferred = service.snapshot();
  IOTOX_CHECK(retained_deferred.size() == 1U);
  IOTOX_CHECK(retained_deferred.front().pending_offers == 1U);
  IOTOX_CHECK(retained_deferred.front().range_retained_bytes ==
              restart_prefix_bytes + range_bundle.size() / 2U);
  IOTOX_CHECK(retained_deferred.front().range_retention_fallbacks == 0U);
  retry_claimed = service.handle_offer(peer, retry_offer);
  IOTOX_CHECK(retry_claimed.ok() && retry_claimed.value());
  IOTOX_CHECK(resume_offsets[72U] == range_bundle.size() / 2U);
  auto retry_result = iotox::sync::make_sync_range_result_frame(
      {iotox::sync::SyncRangeResultStatus::offered,
       retry_request.value().head_record,
       retry_request.value().transfer_id},
      1103U, retried.value().front().message_id);
  IOTOX_CHECK(retry_result.ok());
  IOTOX_CHECK(service.handle_range_result(peer, retry_result.value()).ok());
  iotox::FileTransferRecord retry_terminal = retry_offer;
  retry_terminal.state = iotox::FileTransferState::completed;
  retry_terminal.position = range_bundle.size();
  retry_terminal.local_path = destinations[72U];
  auto completed = service.handle_terminal(
      peer, retry_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(completed.ok(), completed.status().message());
  IOTOX_CHECK(completed.value().empty());
  IOTOX_CHECK(cancellations == 0U);

  const auto state = service.snapshot();
  IOTOX_CHECK(state.size() == 1U);
  IOTOX_CHECK(state.front().state == iotox::sync::SyncPullState::complete);
  IOTOX_CHECK(state.front().range_transfer);
  IOTOX_CHECK(state.front().transfer_carrier == peer.transfer_carrier);
  IOTOX_CHECK(state.front().range_retries == 1U);
  IOTOX_CHECK(state.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(state.front().range_retained_bytes ==
              restart_prefix_bytes + range_bundle.size() / 2U);
  IOTOX_CHECK(state.front().range_resumed_bytes ==
              restart_prefix_bytes + range_bundle.size() / 2U);
  IOTOX_CHECK(state.front().range_restart_resumed_attempts == 1U);
  IOTOX_CHECK(state.front().range_restart_resumed_bytes ==
              restart_prefix_bytes);
  IOTOX_CHECK(state.front().range_restart_suffix_bytes ==
              range_bundle.size() - restart_prefix_bytes);
  IOTOX_CHECK(state.front().range_message_id != 0U);
  IOTOX_CHECK(state.front().range_message_id != restart_message_id);
  IOTOX_CHECK(state.front().range_retention_fallbacks == 0U);
  IOTOX_CHECK(state.front().range_count ==
              range_request.value().ranges.size());
  IOTOX_CHECK(state.front().range_reused_bytes > 0U);
  IOTOX_CHECK(state.front().range_fetched_bytes == range_bundle.size());
  IOTOX_CHECK(state.front().range_reused_bytes +
                  state.front().range_fetched_bytes ==
              target_bytes.size());
  std::ifstream reconstructed(
      iotox::sync::sync_object_path(configured, target_object),
      std::ios::binary);
  std::ostringstream reconstructed_stream;
  reconstructed_stream << reconstructed.rdbuf();
  IOTOX_CHECK(reconstructed_stream.str() == target_bytes);
  auto accepted_target = accepted.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(accepted_target.ok() && accepted_target.value().has_value());
  IOTOX_CHECK(accepted_target.value()->generation == 2U);
  iotox::sync::SyncAttemptStore attempts(namespace_root);
  auto attempt_truth = attempts.load(configured, local.public_key(), crypto);
  IOTOX_CHECK(attempt_truth.ok() && attempt_truth.value().active.empty());
  IOTOX_CHECK(!std::filesystem::exists(destinations[72U]));

  // Corrupt the now-accepted generation-2 artifact without changing its
  // strict file shape. A later signed successor must not use those bytes as
  // a range basis, but it can recover by requesting and fully verifying the
  // complete generation-3 artifact before accepting that HEAD.
  std::string repaired_bytes = target_bytes;
  std::fill(repaired_bytes.begin() + 8192,
            repaired_bytes.begin() + 8448, '\x37');
  const auto repaired_source = temporary.path() / "repaired";
  const auto repaired_manifest_source = temporary.path() / "repaired.index";
  write_private(repaired_source, repaired_bytes);
  auto repaired_manifest = iotox::sync::build_sync_range_manifest(
      configured, repaired_source, repaired_manifest_source);
  IOTOX_CHECK(repaired_manifest.ok());
  auto repaired_manifest_digest =
      iotox::sync::hash_sync_file_sha256(repaired_manifest_source);
  IOTOX_CHECK(repaired_manifest_digest.ok());
  iotox::sync::SignedHeadPublicationRequest repaired_publication;
  repaired_publication.artifact = repaired_manifest.value().artifact;
  repaired_publication.manifest = repaired_manifest_digest.value();
  repaired_publication.artifact_bytes = repaired_bytes.size();
  repaired_publication.manifest_bytes =
      repaired_manifest.value().manifest_bytes;
  auto repaired_head = iotox::sync::create_signed_head(
      configured, repaired_publication, target_head.value(), remote, crypto);
  IOTOX_CHECK(repaired_head.ok() && repaired_head.value().generation == 3U);

  write_private(iotox::sync::sync_object_path(configured, target_object),
                std::string(target_bytes.size(), '\x66'));
  auto corrupt_basis_digest = iotox::sync::hash_sync_file_sha256(
      iotox::sync::sync_object_path(configured, target_object));
  IOTOX_CHECK(corrupt_basis_digest.ok());
  IOTOX_CHECK(corrupt_basis_digest.value() != target_object.identity);

  std::ifstream repaired_manifest_input(
      repaired_manifest_source, std::ios::binary);
  std::ostringstream repaired_manifest_stream;
  repaired_manifest_stream << repaired_manifest_input.rdbuf();
  const std::string repaired_manifest_bytes =
      repaired_manifest_stream.str();
  auto repair_head_request = service.begin_pull(peer, configured.id);
  IOTOX_CHECK(repair_head_request.ok());
  auto repair_head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available,
       repaired_head.value()},
      1200U, repair_head_request.value().message_id);
  IOTOX_CHECK(repair_head_result.ok());
  auto repair_manifest_requests = service.handle_head_result(
      peer, repair_head_result.value());
  IOTOX_CHECK(repair_manifest_requests.ok() &&
              repair_manifest_requests.value().size() == 1U);
  auto repair_manifest_request = iotox::sync::decode_sync_object_request(
      repair_manifest_requests.value().front().payload);
  IOTOX_CHECK(repair_manifest_request.ok());
  IOTOX_CHECK(repair_manifest_request.value().kind ==
              iotox::sync::SyncObjectKind::manifest);

  incoming[73U] = repaired_manifest_bytes;
  iotox::FileTransferRecord repair_manifest_offer;
  repair_manifest_offer.direction = iotox::FileTransferDirection::incoming;
  repair_manifest_offer.state = iotox::FileTransferState::offered;
  repair_manifest_offer.friend_number = peer.friend_number;
  repair_manifest_offer.file_number = 73U;
  repair_manifest_offer.file_size = repaired_manifest_bytes.size();
  repair_manifest_offer.file_id =
      repair_manifest_request.value().transfer_id;
  repair_manifest_offer.has_file_id = true;
  auto repair_manifest_claimed = service.handle_offer(
      peer, repair_manifest_offer);
  IOTOX_CHECK(repair_manifest_claimed.ok() &&
              repair_manifest_claimed.value());
  auto repair_manifest_result = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered,
       repair_manifest_request.value().kind,
       repair_manifest_request.value().head_record,
       repair_manifest_request.value().transfer_id},
      1201U, repair_manifest_requests.value().front().message_id);
  IOTOX_CHECK(repair_manifest_result.ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, repair_manifest_result.value()).ok());
  iotox::FileTransferRecord repair_manifest_terminal =
      repair_manifest_offer;
  repair_manifest_terminal.state = iotox::FileTransferState::completed;
  repair_manifest_terminal.local_path = destinations[73U];
  auto repair_artifact_requests = service.handle_terminal(
      peer, repair_manifest_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(repair_artifact_requests.ok(),
                  repair_artifact_requests.status().message());
  IOTOX_CHECK(repair_artifact_requests.value().size() == 1U);
  IOTOX_CHECK(repair_artifact_requests.value().front().type ==
              iotox::protocol::MessageType::sync_object_request);
  auto repair_artifact_request = iotox::sync::decode_sync_object_request(
      repair_artifact_requests.value().front().payload);
  IOTOX_CHECK(repair_artifact_request.ok());
  IOTOX_CHECK(repair_artifact_request.value().kind ==
              iotox::sync::SyncObjectKind::artifact);
  const auto fallback_state = service.snapshot();
  IOTOX_CHECK(fallback_state.size() == 1U);
  IOTOX_CHECK(fallback_state.front().range_fallback);
  IOTOX_CHECK(!fallback_state.front().range_transfer);
  IOTOX_CHECK(fallback_state.front().detail.find("basis absent or corrupt") !=
              std::string::npos);

  incoming[74U] = repaired_bytes;
  iotox::FileTransferRecord repair_artifact_offer;
  repair_artifact_offer.direction = iotox::FileTransferDirection::incoming;
  repair_artifact_offer.state = iotox::FileTransferState::offered;
  repair_artifact_offer.friend_number = peer.friend_number;
  repair_artifact_offer.file_number = 74U;
  repair_artifact_offer.file_size = repaired_bytes.size();
  repair_artifact_offer.file_id =
      repair_artifact_request.value().transfer_id;
  repair_artifact_offer.has_file_id = true;
  auto repair_artifact_claimed = service.handle_offer(
      peer, repair_artifact_offer);
  IOTOX_CHECK(repair_artifact_claimed.ok() &&
              repair_artifact_claimed.value());
  auto repair_artifact_result = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered,
       repair_artifact_request.value().kind,
       repair_artifact_request.value().head_record,
       repair_artifact_request.value().transfer_id},
      1202U, repair_artifact_requests.value().front().message_id);
  IOTOX_CHECK(repair_artifact_result.ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, repair_artifact_result.value()).ok());
  iotox::FileTransferRecord repair_artifact_terminal =
      repair_artifact_offer;
  repair_artifact_terminal.state = iotox::FileTransferState::completed;
  repair_artifact_terminal.local_path = destinations[74U];
  auto repair_complete = service.handle_terminal(
      peer, repair_artifact_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(repair_complete.ok(),
                  repair_complete.status().message());
  IOTOX_CHECK(repair_complete.value().empty());
  const auto repaired_state = service.snapshot();
  IOTOX_CHECK(repaired_state.size() == 1U);
  IOTOX_CHECK(repaired_state.front().state ==
              iotox::sync::SyncPullState::complete);
  IOTOX_CHECK(repaired_state.front().range_fallback);
  auto accepted_repaired = accepted.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(accepted_repaired.ok() &&
              accepted_repaired.value().has_value());
  IOTOX_CHECK(accepted_repaired.value()->generation == 3U);
  const iotox::sync::SyncObjectRecord repaired_object{
      iotox::sync::SyncObjectKind::artifact,
      repaired_publication.artifact, repaired_publication.artifact_bytes};
  std::ifstream repaired_artifact(
      iotox::sync::sync_object_path(configured, repaired_object),
      std::ios::binary);
  std::ostringstream repaired_artifact_stream;
  repaired_artifact_stream << repaired_artifact.rdbuf();
  IOTOX_CHECK(repaired_artifact_stream.str() == repaired_bytes);
  // Automatic scrubbing/deletion is a separate gate. Recovery never mutates
  // the prior digest path merely because it is unusable as an optimization.
  corrupt_basis_digest = iotox::sync::hash_sync_file_sha256(
      iotox::sync::sync_object_path(configured, target_object));
  IOTOX_CHECK(corrupt_basis_digest.ok());
  IOTOX_CHECK(corrupt_basis_digest.value() != target_object.identity);

  // An available-policy range may retain one exact private prefix across
  // auxiliary carrier loss. The old attempt and FileId remain fenced; a
  // fresh attempt on a distinct authenticated carrier inherits the inode and
  // seeks before receiving only the suffix.
  std::string routed_bytes = repaired_bytes;
  std::fill(routed_bytes.begin() + 4096,
            routed_bytes.begin() + 4352, '\x24');
  const auto routed_source = temporary.path() / "routed";
  const auto routed_manifest_source =
      temporary.path() / "routed.index";
  write_private(routed_source, routed_bytes);
  auto routed_manifest = iotox::sync::build_sync_range_manifest(
      configured, routed_source, routed_manifest_source);
  IOTOX_CHECK(routed_manifest.ok());
  auto routed_manifest_digest =
      iotox::sync::hash_sync_file_sha256(routed_manifest_source);
  IOTOX_CHECK(routed_manifest_digest.ok());
  iotox::sync::SignedHeadPublicationRequest routed_publication;
  routed_publication.artifact = routed_manifest.value().artifact;
  routed_publication.manifest = routed_manifest_digest.value();
  routed_publication.artifact_bytes = routed_bytes.size();
  routed_publication.manifest_bytes =
      routed_manifest.value().manifest_bytes;
  auto routed_head = iotox::sync::create_signed_head(
      configured, routed_publication, repaired_head.value(), remote,
      crypto);
  IOTOX_CHECK(routed_head.ok() && routed_head.value().generation == 4U);
  std::ifstream routed_manifest_input(
      routed_manifest_source, std::ios::binary);
  std::ostringstream routed_manifest_stream;
  routed_manifest_stream << routed_manifest_input.rdbuf();
  const std::string routed_manifest_bytes =
      routed_manifest_stream.str();

  auto routed_head_request = service.begin_pull(
      peer, configured.id,
      iotox::sync::SyncRouteFailoverPolicy::available,
      iotox::sync::SyncRouteClassConstraint::any);
  IOTOX_CHECK(routed_head_request.ok());
  auto routed_head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available,
       routed_head.value()},
      1300U, routed_head_request.value().message_id);
  IOTOX_CHECK(routed_head_result.ok());
  auto routed_manifest_requests = service.handle_head_result(
      peer, routed_head_result.value());
  IOTOX_CHECK(routed_manifest_requests.ok() &&
              routed_manifest_requests.value().size() == 1U);
  auto routed_manifest_request =
      iotox::sync::decode_sync_object_request(
          routed_manifest_requests.value().front().payload);
  IOTOX_CHECK(routed_manifest_request.ok());
  IOTOX_CHECK(routed_manifest_request.value().kind ==
              iotox::sync::SyncObjectKind::manifest);
  incoming[77U] = routed_manifest_bytes;
  iotox::FileTransferRecord routed_manifest_offer;
  routed_manifest_offer.direction =
      iotox::FileTransferDirection::incoming;
  routed_manifest_offer.state = iotox::FileTransferState::offered;
  routed_manifest_offer.friend_number = peer.friend_number;
  routed_manifest_offer.file_number = 77U;
  routed_manifest_offer.file_size = routed_manifest_bytes.size();
  routed_manifest_offer.file_id =
      routed_manifest_request.value().transfer_id;
  routed_manifest_offer.has_file_id = true;
  auto routed_manifest_claimed = service.handle_offer(
      peer, routed_manifest_offer);
  IOTOX_CHECK(routed_manifest_claimed.ok() &&
              routed_manifest_claimed.value());
  auto routed_manifest_result =
      iotox::sync::make_sync_object_result_frame(
          {iotox::sync::SyncObjectResultStatus::offered,
           routed_manifest_request.value().kind,
           routed_manifest_request.value().head_record,
           routed_manifest_request.value().transfer_id},
          1301U, routed_manifest_requests.value().front().message_id);
  IOTOX_CHECK(routed_manifest_result.ok());
  IOTOX_CHECK(service.handle_object_result(
      peer, routed_manifest_result.value()).ok());
  iotox::FileTransferRecord routed_manifest_terminal =
      routed_manifest_offer;
  routed_manifest_terminal.state =
      iotox::FileTransferState::completed;
  routed_manifest_terminal.position = routed_manifest_bytes.size();
  routed_manifest_terminal.local_path = destinations[77U];
  auto routed_range_requests = service.handle_terminal(
      peer, routed_manifest_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(routed_range_requests.ok(),
                  routed_range_requests.status().message());
  IOTOX_CHECK(routed_range_requests.value().size() == 1U);
  auto routed_range_request = iotox::sync::decode_sync_range_request(
      routed_range_requests.value().front().payload);
  IOTOX_CHECK(routed_range_request.ok());
  std::string routed_range_bundle;
  for (const iotox::sync::SyncRangeRecord &range :
       routed_range_request.value().ranges) {
    routed_range_bundle.append(routed_bytes.substr(
        static_cast<std::size_t>(range.offset),
        static_cast<std::size_t>(range.length)));
  }
  IOTOX_CHECK(!routed_range_bundle.empty());
  incoming[78U] = routed_range_bundle;
  iotox::FileTransferRecord routed_range_offer;
  routed_range_offer.direction =
      iotox::FileTransferDirection::incoming;
  routed_range_offer.state = iotox::FileTransferState::offered;
  routed_range_offer.friend_number = peer.friend_number;
  routed_range_offer.file_number = 78U;
  routed_range_offer.file_size = routed_range_bundle.size();
  routed_range_offer.file_id =
      routed_range_request.value().transfer_id;
  routed_range_offer.has_file_id = true;
  auto routed_range_claimed = service.handle_offer(
      peer, routed_range_offer);
  IOTOX_CHECK(routed_range_claimed.ok() &&
              routed_range_claimed.value());
  auto routed_range_result =
      iotox::sync::make_sync_range_result_frame(
          {iotox::sync::SyncRangeResultStatus::offered,
           routed_range_request.value().head_record,
           routed_range_request.value().transfer_id},
          1302U, routed_range_requests.value().front().message_id);
  IOTOX_CHECK(routed_range_result.ok());
  IOTOX_CHECK(service.handle_range_result(
      peer, routed_range_result.value()).ok());

  const std::filesystem::path routed_prefix_path = destinations[78U];
  const std::uint64_t routed_prefix_bytes =
      routed_range_bundle.size() / 2U;
  IOTOX_CHECK(routed_prefix_bytes > 0U);
  write_private(
      routed_prefix_path,
      routed_range_bundle.substr(
          0U, static_cast<std::size_t>(routed_prefix_bytes)));
  retirement_publishes_content = false;
  IOTOX_CHECK(service.carrier_offline(
      peer.transfer_carrier).ok());
  auto routed_lost = service.snapshot();
  IOTOX_CHECK(routed_lost.size() == 1U);
  IOTOX_CHECK(routed_lost.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(routed_lost.front().range_lane_active);
  IOTOX_CHECK(routed_lost.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(routed_lost.front().range_retained_bytes == 0U);
  IOTOX_CHECK(routed_lost.front().transfer_file_ids.size() == 1U);
  IOTOX_CHECK(std::find(
      routed_lost.front().transfer_file_ids.begin(),
      routed_lost.front().transfer_file_ids.end(),
      routed_range_request.value().transfer_id) ==
      routed_lost.front().transfer_file_ids.end());
  IOTOX_CHECK(std::filesystem::file_size(routed_prefix_path) ==
              routed_prefix_bytes);
  IOTOX_CHECK(service.carrier_offline(
      peer.transfer_carrier).ok());
  IOTOX_CHECK(std::filesystem::file_size(routed_prefix_path) ==
              routed_prefix_bytes);
  const auto routed_duplicate_loss = service.snapshot();
  IOTOX_CHECK(routed_duplicate_loss.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(routed_duplicate_loss.front().range_retention_fallbacks == 0U);
  auto stale_routed_offer = service.handle_offer(
      peer, routed_range_offer);
  IOTOX_CHECK(!stale_routed_offer.ok());
  IOTOX_CHECK(stale_routed_offer.status().code() ==
              iotox::ErrorCode::unavailable);

  auto replacement = peer;
  replacement.transfer_carrier.route_key.fill(0x94U);
  replacement.transfer_carrier.worker_id = 0x9004U;
  replacement.transfer_carrier.remote_route_generation = 6U;
  auto incapable_replacement = replacement;
  incapable_replacement.range_transfer_negotiated = false;
  auto incapable_requests = service.reassign_transfer_carrier(
      routed_head_request.value().message_id, incapable_replacement);
  IOTOX_CHECK(!incapable_requests.ok());
  IOTOX_CHECK(incapable_requests.status().code() ==
              iotox::ErrorCode::unsupported);
  IOTOX_CHECK(std::filesystem::file_size(routed_prefix_path) ==
              routed_prefix_bytes);
  auto replacement_requests = service.reassign_transfer_carrier(
      routed_head_request.value().message_id, replacement);
  IOTOX_CHECK_MSG(replacement_requests.ok(),
                  replacement_requests.status().message());
  IOTOX_CHECK(replacement_requests.value().size() == 1U);
  IOTOX_CHECK(replacement_requests.value().front().type ==
              iotox::protocol::MessageType::sync_range_request);
  auto replacement_request = iotox::sync::decode_sync_range_request(
      replacement_requests.value().front().payload);
  IOTOX_CHECK(replacement_request.ok());
  IOTOX_CHECK(replacement_request.value().ranges ==
              routed_range_request.value().ranges);
  IOTOX_CHECK(replacement_request.value().head_record ==
              routed_range_request.value().head_record);
  IOTOX_CHECK(replacement_request.value().transfer_id !=
              routed_range_request.value().transfer_id);
  IOTOX_CHECK(!std::filesystem::exists(routed_prefix_path));
  auto routed_reassigned = service.snapshot();
  IOTOX_CHECK(routed_reassigned.front().transfer_carrier ==
              replacement.transfer_carrier);
  IOTOX_CHECK(routed_reassigned.front().requested_objects == 2U);
  IOTOX_CHECK(routed_reassigned.front().committed_objects == 1U);
  IOTOX_CHECK(routed_reassigned.front().range_retries == 0U);
  IOTOX_CHECK(routed_reassigned.front().range_retained_bytes ==
              routed_prefix_bytes);

  incoming[79U] = routed_range_bundle;
  iotox::FileTransferRecord replacement_offer = routed_range_offer;
  replacement_offer.file_number = 79U;
  replacement_offer.file_id = replacement_request.value().transfer_id;
  auto replacement_claimed = service.handle_offer(
      replacement, replacement_offer);
  IOTOX_CHECK(replacement_claimed.ok() &&
              replacement_claimed.value());
  IOTOX_CHECK(resume_offsets[79U] == routed_prefix_bytes);
  auto stale_routed_terminal = service.handle_terminal(
      peer, routed_range_offer,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK(!stale_routed_terminal.ok());
  IOTOX_CHECK(stale_routed_terminal.status().code() ==
              iotox::ErrorCode::not_found);
  auto replacement_result =
      iotox::sync::make_sync_range_result_frame(
          {iotox::sync::SyncRangeResultStatus::offered,
           replacement_request.value().head_record,
           replacement_request.value().transfer_id},
          1303U, replacement_requests.value().front().message_id);
  IOTOX_CHECK(replacement_result.ok());
  IOTOX_CHECK(service.handle_range_result(
      replacement, replacement_result.value()).ok());

  // Lose the replacement too, after it has extended the same private inode.
  // This proves carrier-loss continuation is a repeatable attempt boundary,
  // not a hidden one-shot exception tied to the first worker.
  const std::filesystem::path replacement_prefix_path = destinations[79U];
  const std::uint64_t replacement_prefix_bytes =
      routed_range_bundle.size() * 3U / 4U;
  IOTOX_CHECK(replacement_prefix_bytes > routed_prefix_bytes);
  IOTOX_CHECK(replacement_prefix_bytes < routed_range_bundle.size());
  write_private(
      replacement_prefix_path,
      routed_range_bundle.substr(
          0U, static_cast<std::size_t>(replacement_prefix_bytes)));
  IOTOX_CHECK(service.carrier_offline(
      replacement.transfer_carrier).ok());
  const auto replacement_lost = service.snapshot();
  IOTOX_CHECK(replacement_lost.size() == 1U);
  IOTOX_CHECK(replacement_lost.front().state ==
              iotox::sync::SyncPullState::awaiting_objects);
  IOTOX_CHECK(replacement_lost.front().range_lane_active);
  IOTOX_CHECK(replacement_lost.front().range_retries == 0U);
  IOTOX_CHECK(replacement_lost.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(replacement_lost.front().range_retention_fallbacks == 0U);
  IOTOX_CHECK(std::filesystem::file_size(replacement_prefix_path) ==
              replacement_prefix_bytes);
  IOTOX_CHECK(service.carrier_offline(
      replacement.transfer_carrier).ok());
  IOTOX_CHECK(std::filesystem::file_size(replacement_prefix_path) ==
              replacement_prefix_bytes);
  auto stale_replacement_offer = service.handle_offer(
      replacement, replacement_offer);
  IOTOX_CHECK(!stale_replacement_offer.ok());
  IOTOX_CHECK(stale_replacement_offer.status().code() ==
              iotox::ErrorCode::unavailable);

  auto final_carrier = replacement;
  final_carrier.transfer_carrier.route_key.fill(0x95U);
  final_carrier.transfer_carrier.worker_id = 0x9005U;
  final_carrier.transfer_carrier.remote_route_generation = 7U;
  auto final_requests = service.reassign_transfer_carrier(
      routed_head_request.value().message_id, final_carrier);
  IOTOX_CHECK_MSG(final_requests.ok(),
                  final_requests.status().message());
  IOTOX_CHECK(final_requests.value().size() == 1U);
  auto final_request = iotox::sync::decode_sync_range_request(
      final_requests.value().front().payload);
  IOTOX_CHECK(final_request.ok());
  IOTOX_CHECK(final_request.value().ranges ==
              routed_range_request.value().ranges);
  IOTOX_CHECK(final_request.value().head_record ==
              routed_range_request.value().head_record);
  IOTOX_CHECK(final_request.value().transfer_id !=
              routed_range_request.value().transfer_id);
  IOTOX_CHECK(final_request.value().transfer_id !=
              replacement_request.value().transfer_id);
  IOTOX_CHECK(!std::filesystem::exists(replacement_prefix_path));
  const auto twice_reassigned = service.snapshot();
  IOTOX_CHECK(twice_reassigned.front().transfer_carrier ==
              final_carrier.transfer_carrier);
  IOTOX_CHECK(twice_reassigned.front().requested_objects == 2U);
  IOTOX_CHECK(twice_reassigned.front().committed_objects == 1U);
  IOTOX_CHECK(twice_reassigned.front().scheduler_attempts == 4U);
  IOTOX_CHECK(twice_reassigned.front().scheduler_attempt_bound == 5U);
  IOTOX_CHECK(twice_reassigned.front().range_retries == 0U);
  IOTOX_CHECK(twice_reassigned.front().range_retained_bytes ==
              routed_prefix_bytes + replacement_prefix_bytes);

  incoming[80U] = routed_range_bundle;
  iotox::FileTransferRecord final_offer = replacement_offer;
  final_offer.file_number = 80U;
  final_offer.file_id = final_request.value().transfer_id;
  auto final_claimed = service.handle_offer(final_carrier, final_offer);
  IOTOX_CHECK(final_claimed.ok() && final_claimed.value());
  IOTOX_CHECK(resume_offsets[80U] == replacement_prefix_bytes);
  iotox::FileTransferRecord replacement_terminal = replacement_offer;
  replacement_terminal.state = iotox::FileTransferState::completed;
  replacement_terminal.position = routed_range_bundle.size();
  replacement_terminal.local_path = replacement_prefix_path;
  auto stale_replacement_terminal = service.handle_terminal(
      replacement, replacement_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK(!stale_replacement_terminal.ok());
  IOTOX_CHECK(stale_replacement_terminal.status().code() ==
              iotox::ErrorCode::not_found);

  // Lose a third carrier after growing the same prefix again. A fifth
  // scheduler record is the minimum safe successor because all four prior
  // records remain as late-event fences for this pull.
  const std::filesystem::path final_prefix_path = destinations[80U];
  const std::uint64_t final_prefix_bytes =
      routed_range_bundle.size() * 7U / 8U;
  IOTOX_CHECK(final_prefix_bytes > replacement_prefix_bytes);
  IOTOX_CHECK(final_prefix_bytes < routed_range_bundle.size());
  write_private(
      final_prefix_path,
      routed_range_bundle.substr(
          0U, static_cast<std::size_t>(final_prefix_bytes)));
  IOTOX_CHECK(service.carrier_offline(
      final_carrier.transfer_carrier).ok());

  auto terminal_carrier = final_carrier;
  terminal_carrier.transfer_carrier.route_key.fill(0x96U);
  terminal_carrier.transfer_carrier.worker_id = 0x9006U;
  terminal_carrier.transfer_carrier.remote_route_generation = 8U;
  auto terminal_requests = service.reassign_transfer_carrier(
      routed_head_request.value().message_id, terminal_carrier);
  IOTOX_CHECK_MSG(terminal_requests.ok(),
                  terminal_requests.status().message());
  IOTOX_CHECK(terminal_requests.value().size() == 1U);
  auto terminal_request = iotox::sync::decode_sync_range_request(
      terminal_requests.value().front().payload);
  IOTOX_CHECK(terminal_request.ok());
  IOTOX_CHECK(terminal_request.value().ranges ==
              routed_range_request.value().ranges);
  IOTOX_CHECK(terminal_request.value().transfer_id !=
              final_request.value().transfer_id);
  const auto thrice_reassigned = service.snapshot();
  IOTOX_CHECK(thrice_reassigned.front().scheduler_attempts == 5U);
  IOTOX_CHECK(thrice_reassigned.front().scheduler_attempt_bound == 5U);

  incoming[81U] = routed_range_bundle;
  iotox::FileTransferRecord terminal_offer = final_offer;
  terminal_offer.file_number = 81U;
  terminal_offer.file_id = terminal_request.value().transfer_id;
  auto terminal_claimed = service.handle_offer(
      terminal_carrier, terminal_offer);
  IOTOX_CHECK(terminal_claimed.ok() && terminal_claimed.value());
  IOTOX_CHECK(resume_offsets[81U] == final_prefix_bytes);
  auto final_result = iotox::sync::make_sync_range_result_frame(
      {iotox::sync::SyncRangeResultStatus::offered,
       terminal_request.value().head_record,
       terminal_request.value().transfer_id},
      1304U, terminal_requests.value().front().message_id);
  IOTOX_CHECK(final_result.ok());
  IOTOX_CHECK(service.handle_range_result(
      terminal_carrier, final_result.value()).ok());
  iotox::FileTransferRecord final_terminal = terminal_offer;
  final_terminal.state = iotox::FileTransferState::completed;
  final_terminal.position = routed_range_bundle.size();
  final_terminal.local_path = destinations[81U];
  auto routed_complete = service.handle_terminal(
      terminal_carrier, final_terminal,
      iotox::routes::WorkerTransferOutcome::completed,
      iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(routed_complete.ok(),
                  routed_complete.status().message());
  IOTOX_CHECK(routed_complete.value().empty());
  retirement_publishes_content = true;

  const auto routed_state = service.snapshot();
  IOTOX_CHECK(routed_state.size() == 1U);
  IOTOX_CHECK(routed_state.front().state ==
              iotox::sync::SyncPullState::complete);
  IOTOX_CHECK(routed_state.front().transfer_carrier ==
              terminal_carrier.transfer_carrier);
  IOTOX_CHECK(routed_state.front().range_retries == 0U);
  IOTOX_CHECK(routed_state.front().range_retained_bytes ==
              routed_prefix_bytes + replacement_prefix_bytes +
                  final_prefix_bytes);
  IOTOX_CHECK(routed_state.front().range_resumed_bytes ==
              routed_prefix_bytes + replacement_prefix_bytes +
                  final_prefix_bytes);
  IOTOX_CHECK(routed_state.front().range_discarded_bytes == 0U);
  IOTOX_CHECK(routed_state.front().range_retention_fallbacks == 0U);
  auto accepted_routed = accepted.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(accepted_routed.ok() &&
              accepted_routed.value().has_value());
  IOTOX_CHECK(accepted_routed.value()->generation == 4U);
  const iotox::sync::SyncObjectRecord routed_object{
      iotox::sync::SyncObjectKind::artifact,
      routed_publication.artifact, routed_publication.artifact_bytes};
  std::ifstream routed_artifact(
      iotox::sync::sync_object_path(configured, routed_object),
      std::ios::binary);
  std::ostringstream routed_artifact_stream;
  routed_artifact_stream << routed_artifact.rdbuf();
  IOTOX_CHECK(routed_artifact_stream.str() == routed_bytes);
  attempt_truth = attempts.load(
      configured, local.public_key(), crypto);
  IOTOX_CHECK(attempt_truth.ok() && attempt_truth.value().active.empty());
}

IOTOX_TEST("sync subscriber requires proven publisher authority before request") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto local = identity(temporary.path() / "local.identity", crypto);
  auto remote = identity(temporary.path() / "remote.identity", crypto);
  auto configured = policy(temporary.path() / "namespace",
                           remote.public_key());
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SyncSubscriberSeams seams;
  seams.make_message_id = []() -> iotox::Result<std::uint64_t> {
    return 1U;
  };
  seams.make_file_id = []() -> iotox::Result<iotox::FileId> {
    iotox::FileId value{};
    value[0U] = 1U;
    return value;
  };
  seams.receive_to_path = [](const iotox::sync::SyncTransferCarrier &,
                             std::uint32_t,
                             const std::filesystem::path &) {
    return iotox::Result<iotox::FileTransferRecord>{
        iotox::Status{iotox::ErrorCode::unavailable, "unused"}};
  };
  seams.cancel_transfer = [](const iotox::sync::SyncTransferCarrier &,
                             std::uint32_t) {
    return iotox::Status::success();
  };
  seams.retire_transfer = [](const iotox::sync::SyncTransferCarrier &,
                             std::uint32_t) {
    return iotox::Status::success();
  };
  seams.install.hash_file = iotox::sync::hash_sync_file_sha256;
  iotox::sync::SyncSubscriberService::Config service_config;
  service_config.identity = &local;
  service_config.sodium = &crypto;
  iotox::sync::SyncSubscriberService service(
      registry, std::move(seams), service_config);
  auto denied = context(remote.public_key());
  denied.peer_authority.remote_capabilities = 0U;
  IOTOX_CHECK(!service.begin_pull(denied, configured.id).ok());
  IOTOX_CHECK(service.snapshot().empty());
}
