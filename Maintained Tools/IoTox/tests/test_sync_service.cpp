#include "iotox/sync_service.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <condition_variable>
#include <filesystem>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <string>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-service-XXXXXX";
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
  [[nodiscard]] const std::filesystem::path &path() const { return path_; }

private:
  std::filesystem::path path_;
};

iotox::security::SigningPublicKey principal(std::uint8_t value) {
  iotox::security::SigningPublicKey result{};
  result[0U] = value;
  return result;
}

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity identity(const std::filesystem::path &path,
                                         const iotox::security::Sodium &crypto) {
  auto loaded = iotox::security::DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root,
                                    const iotox::security::SigningPublicKey &writer,
                                    const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.writers = {writer};
  result.subscribers = {subscriber};
  return result;
}

iotox::sync::SyncPeerContext context(const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::SyncPeerContext result;
  result.friend_number = 4U;
  result.online_epoch = 9U;
  result.authority_route_key.fill(0x71U);
  result.authority.initialized = true;
  result.authority.format = iotox::security::AuthorityLedgerFormat::v3;
  result.authority.ownership_epoch = 2U;
  result.authority.sequence = 7U;
  result.authority.tail_digest = digest(0x81U);
  result.peer_authority.friend_number = result.friend_number;
  result.peer_authority.online_epoch = result.online_epoch;
  result.peer_authority.connected = true;
  result.peer_authority.feature_negotiated = true;
  result.peer_authority.authority_v2_negotiated = true;
  result.peer_authority.authority_v3_negotiated = true;
  result.peer_authority.verifier_state = iotox::security::AuthorityVerifierState::authorized;
  result.peer_authority.remote_authorized = true;
  result.peer_authority.remote_principal = subscriber;
  result.peer_authority.remote_capabilities =
      static_cast<std::uint64_t>(iotox::security::Capability::sync_subscribe);
  result.peer_authority.local_authority_format = result.authority.format;
  result.peer_authority.local_authority_epoch = result.authority.ownership_epoch;
  result.peer_authority.local_authority_sequence = result.authority.sequence;
  result.peer_authority.local_authority_tail_digest = result.authority.tail_digest;
  result.transfer_carrier.route_key = result.authority_route_key;
  result.transfer_carrier.worker_id = result.online_epoch;
  result.transfer_carrier.friend_number = result.friend_number;
  result.transfer_carrier.online_epoch = result.online_epoch;
  return result;
}

bool same_frame(const iotox::protocol::Frame &left, const iotox::protocol::Frame &right) {
  auto encoded_left = iotox::protocol::encode(left);
  auto encoded_right = iotox::protocol::encode(right);
  return encoded_left && encoded_right && encoded_left.value() == encoded_right.value();
}

} // namespace

IOTOX_TEST("sync publisher authorizes HEAD and offers exact immutable objects once") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto subscriber = principal(0x44U);
  const auto configured = policy(temporary.path() / "namespace", writer.public_key(), subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHeadPublicationRequest publication;
  publication.artifact = digest(0x21U);
  publication.manifest = digest(0x22U);
  publication.artifact_bytes = 100U;
  publication.manifest_bytes = 30U;
  auto head =
      iotox::sync::create_signed_head(configured, publication, std::nullopt, writer, crypto);
  IOTOX_CHECK(head.ok());
  auto head_record = iotox::sync::signed_head_record_digest(head.value(), crypto);
  IOTOX_CHECK(head_record.ok());

  std::uint64_t next_message = 500U;
  std::uint64_t loads = 0U;
  std::uint64_t verifies = 0U;
  std::uint64_t offers = 0U;
  iotox::FileId observed_file_id{};
  std::filesystem::path observed_path;
  iotox::sync::SyncTransferCarrier observed_carrier;
  iotox::sync::SyncPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    ++loads;
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head.value()}};
  };
  seams.head_record_digest = [&](const auto &value) {
    return iotox::sync::signed_head_record_digest(value, crypto);
  };
  seams.verify_object = [&](const auto &, const auto &) {
    ++verifies;
    return iotox::Status::success();
  };
  seams.send_object = [&](const iotox::sync::SyncTransferCarrier &carrier,
                          const auto &path,
                          const iotox::FileId &file_id) {
    ++offers;
    observed_path = path;
    observed_file_id = file_id;
    observed_carrier = carrier;
    iotox::FileTransferRecord record;
    record.friend_number = carrier.friend_number;
    record.file_id = file_id;
    record.has_file_id = true;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> { return next_message++; };
  iotox::sync::SyncPublisherService service(registry, std::move(seams));
  const auto peer = context(subscriber);

  auto head_request = iotox::sync::make_sync_head_request_frame({configured.id}, 101U);
  IOTOX_CHECK(head_request.ok());
  auto first = service.handle(peer, head_request.value());
  IOTOX_CHECK(first.ok());
  auto head_result = iotox::sync::decode_sync_head_result(first.value().response.payload);
  IOTOX_CHECK(head_result.ok());
  IOTOX_CHECK(head_result.value().status == iotox::sync::SyncHeadResultStatus::available);
  auto replay = service.handle(peer, head_request.value());
  IOTOX_CHECK(replay.ok() && replay.value().replayed);
  IOTOX_CHECK(same_frame(first.value().response, replay.value().response));
  IOTOX_CHECK(loads == 1U);

  iotox::FileId transfer_id{};
  transfer_id.fill(0x63U);
  auto object_request = iotox::sync::make_sync_object_request_frame(
      {configured.id, iotox::sync::SyncObjectKind::artifact, head_record.value(), transfer_id},
      102U);
  IOTOX_CHECK(object_request.ok());
  auto object = service.handle(peer, object_request.value());
  IOTOX_CHECK(object.ok() && object.value().file_offered);
  auto object_result = iotox::sync::decode_sync_object_result(object.value().response.payload);
  IOTOX_CHECK(object_result.ok());
  IOTOX_CHECK(object_result.value().status == iotox::sync::SyncObjectResultStatus::offered);
  IOTOX_CHECK(observed_file_id == transfer_id);
  IOTOX_CHECK(observed_path == iotox::sync::sync_object_path(
                                   configured, {iotox::sync::SyncObjectKind::artifact,
                                                publication.artifact, publication.artifact_bytes}));
  auto object_replay = service.handle(peer, object_request.value());
  IOTOX_CHECK(object_replay.ok() && object_replay.value().replayed);
  IOTOX_CHECK(!object_replay.value().file_offered);
  IOTOX_CHECK(offers == 1U && verifies == 1U && loads == 2U);
  IOTOX_CHECK(service.snapshot().retained_replays == 2U);

  auto auxiliary = peer;
  auxiliary.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::auxiliary;
  auxiliary.transfer_carrier.route_key.fill(0x93U);
  auxiliary.transfer_carrier.worker_id = 0x9001U;
  auxiliary.transfer_carrier.friend_number = 17U;
  auxiliary.transfer_carrier.online_epoch = 4U;
  auxiliary.transfer_carrier.remote_route_generation = 3U;
  auxiliary.transfer_carrier.remote_coordinator_route_key.fill(0x51U);
  auxiliary.transfer_carrier.primary_authority_online_epoch =
      auxiliary.online_epoch;
  IOTOX_CHECK(!service.handle(auxiliary, head_request.value()).ok());
  auto auxiliary_object = service.handle(auxiliary, object_request.value());
  IOTOX_CHECK(auxiliary_object.ok() &&
              auxiliary_object.value().file_offered);
  IOTOX_CHECK(observed_carrier == auxiliary.transfer_carrier);
  IOTOX_CHECK(offers == 2U && service.snapshot().retained_replays == 3U);
  auto auxiliary_replay = service.handle(auxiliary, object_request.value());
  IOTOX_CHECK(auxiliary_replay.ok() &&
              auxiliary_replay.value().replayed &&
              !auxiliary_replay.value().file_offered);
  service.carrier_offline(auxiliary.transfer_carrier);
  IOTOX_CHECK(service.snapshot().retained_replays == 2U);
  auxiliary_object = service.handle(auxiliary, object_request.value());
  IOTOX_CHECK(auxiliary_object.ok() &&
              auxiliary_object.value().file_offered);
  IOTOX_CHECK(offers == 3U);
  IOTOX_CHECK(
      service.retire_namespace_replays_for_additive_share("other") == 0U);
  IOTOX_CHECK(
      service.retire_namespace_replays_for_additive_share(configured.id) ==
      3U);
  IOTOX_CHECK(service.snapshot().retained_replays == 0U);
  auto readmitted = service.handle(peer, head_request.value());
  IOTOX_CHECK(readmitted.ok() && !readmitted.value().replayed);
  IOTOX_CHECK(loads == 5U);
}

IOTOX_TEST("sync publisher authorizes one bounded range view and retains offer replay before effect") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto subscriber = principal(0x45U);
  auto configured = policy(
      temporary.path() / "namespace", writer.public_key(), subscriber);
  configured.quotas.maximum_artifact_bytes = 128U;
  configured.quotas.maximum_manifest_bytes = 64U;
  configured.quotas.maximum_staging_bytes = 128U;
  configured.quotas.maximum_store_bytes = 512U;
  configured.quotas.maximum_outstanding_requests = 4U;
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHeadPublicationRequest publication;
  publication.artifact = digest(0x31U);
  publication.manifest = digest(0x32U);
  publication.artifact_bytes = 100U;
  publication.manifest_bytes = 30U;
  auto head = iotox::sync::create_signed_head(
      configured, publication, std::nullopt, writer, crypto);
  IOTOX_CHECK(head.ok());
  auto head_record =
      iotox::sync::signed_head_record_digest(head.value(), crypto);
  IOTOX_CHECK(head_record.ok());

  std::uint64_t next_message = 550U;
  std::uint64_t loads = 0U;
  std::uint64_t verifies = 0U;
  std::uint64_t offers = 0U;
  std::vector<iotox::FileByteRange> observed_ranges;
  iotox::sync::SyncTransferCarrier observed_carrier;
  iotox::sync::SyncPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    ++loads;
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head.value()}};
  };
  seams.head_record_digest = [&](const auto &value) {
    return iotox::sync::signed_head_record_digest(value, crypto);
  };
  seams.verify_object = [&](const auto &, const auto &object) {
    ++verifies;
    IOTOX_CHECK(object.kind == iotox::sync::SyncObjectKind::artifact);
    return iotox::Status::success();
  };
  seams.send_object = [](const iotox::sync::SyncTransferCarrier &,
                         const auto &, const iotox::FileId &) {
    return iotox::Result<iotox::FileTransferRecord>{iotox::Status{
        iotox::ErrorCode::internal_error, "whole object path not expected"}};
  };
  seams.send_ranges = [&](const iotox::sync::SyncTransferCarrier &carrier,
                          const auto &path,
                          std::span<const iotox::FileByteRange> ranges,
                          const iotox::FileId &file_id) {
    ++offers;
    observed_carrier = carrier;
    IOTOX_CHECK(path == iotox::sync::sync_object_path(
        configured, {iotox::sync::SyncObjectKind::artifact,
                     publication.artifact, publication.artifact_bytes}));
    observed_ranges.assign(ranges.begin(), ranges.end());
    iotox::FileTransferRecord record;
    record.friend_number = carrier.friend_number;
    record.file_id = file_id;
    record.has_file_id = true;
    record.file_size = 30U;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return next_message++;
  };
  iotox::sync::SyncPublisherService service(registry, std::move(seams));
  auto peer = context(subscriber);
  iotox::FileId transfer_id{};
  transfer_id.fill(0x64U);
  auto request = iotox::sync::make_sync_range_request_frame(
      {configured.id, head_record.value(), transfer_id,
       {{5U, 10U}, {40U, 20U}}},
      151U);
  IOTOX_CHECK(request.ok());
  IOTOX_CHECK(!service.handle(peer, request.value()).ok());
  IOTOX_CHECK(loads == 0U && offers == 0U);
  peer.range_transfer_negotiated = true;
  auto first = service.handle(peer, request.value());
  IOTOX_CHECK(first.ok() && first.value().file_offered);
  auto result =
      iotox::sync::decode_sync_range_result(first.value().response.payload);
  IOTOX_CHECK(result.ok());
  IOTOX_CHECK(result.value().status ==
              iotox::sync::SyncRangeResultStatus::offered);
  IOTOX_CHECK(observed_ranges ==
              std::vector<iotox::FileByteRange>(
                  {{5U, 10U}, {40U, 20U}}));
  auto replay = service.handle(peer, request.value());
  IOTOX_CHECK(replay.ok() && replay.value().replayed);
  IOTOX_CHECK(!replay.value().file_offered);
  IOTOX_CHECK(loads == 1U && verifies == 1U && offers == 1U);
  const auto snapshot = service.snapshot();
  IOTOX_CHECK(snapshot.range_requests == 1U);
  IOTOX_CHECK(snapshot.range_file_offers == 1U);
  IOTOX_CHECK(snapshot.range_bytes_offered == 30U);

  auto auxiliary = peer;
  auxiliary.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::auxiliary;
  auxiliary.transfer_carrier.route_key.fill(0x94U);
  auxiliary.transfer_carrier.worker_id = 0x9002U;
  auxiliary.transfer_carrier.friend_number = 18U;
  auxiliary.transfer_carrier.online_epoch = 5U;
  auxiliary.transfer_carrier.remote_route_generation = 4U;
  auxiliary.transfer_carrier.remote_coordinator_route_key.fill(0x52U);
  auxiliary.transfer_carrier.primary_authority_online_epoch =
      auxiliary.online_epoch;
  auxiliary.range_transfer_negotiated = false;
  IOTOX_CHECK(!service.handle(auxiliary, request.value()).ok());
  IOTOX_CHECK(loads == 1U && verifies == 1U && offers == 1U);

  auxiliary.range_transfer_negotiated = true;
  auto auxiliary_first = service.handle(auxiliary, request.value());
  IOTOX_CHECK(auxiliary_first.ok() &&
              auxiliary_first.value().file_offered);
  IOTOX_CHECK(observed_carrier == auxiliary.transfer_carrier);
  auto auxiliary_replay = service.handle(auxiliary, request.value());
  IOTOX_CHECK(auxiliary_replay.ok() &&
              auxiliary_replay.value().replayed &&
              !auxiliary_replay.value().file_offered);
  IOTOX_CHECK(loads == 2U && verifies == 2U && offers == 2U);
  IOTOX_CHECK(service.snapshot().retained_replays == 2U);
  service.carrier_offline(auxiliary.transfer_carrier);
  IOTOX_CHECK(service.snapshot().retained_replays == 1U);
  auxiliary_first = service.handle(auxiliary, request.value());
  IOTOX_CHECK(auxiliary_first.ok() &&
              auxiliary_first.value().file_offered);
  IOTOX_CHECK(loads == 3U && verifies == 3U && offers == 3U);
}

IOTOX_TEST("sync publisher fails closed on denial conflict and changed authority") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto subscriber = principal(0x54U);
  const auto configured = policy(temporary.path() / "namespace", writer.public_key(), subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  std::uint64_t loads = 0U;
  std::uint64_t offers = 0U;
  iotox::sync::SyncPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    ++loads;
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{}};
  };
  seams.head_record_digest = [&](const auto &head) {
    return iotox::sync::signed_head_record_digest(head, crypto);
  };
  seams.verify_object = [](const auto &, const auto &) { return iotox::Status::success(); };
  seams.send_object = [&](const iotox::sync::SyncTransferCarrier &,
                          const auto &, const iotox::FileId &) {
    ++offers;
    return iotox::Result<iotox::FileTransferRecord>{
        iotox::Status{iotox::ErrorCode::unavailable, "unexpected"}};
  };
  std::uint64_t message_id = 900U;
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> { return message_id++; };
  iotox::sync::SyncPublisherService::Config service_config;
  service_config.maximum_replays = 2U;
  iotox::sync::SyncPublisherService service(registry, std::move(seams), service_config);

  auto denied_peer = context(principal(0x99U));
  auto request = iotox::sync::make_sync_head_request_frame({configured.id}, 201U);
  IOTOX_CHECK(request.ok());
  auto denied = service.handle(denied_peer, request.value());
  IOTOX_CHECK(denied.ok());
  auto denied_body = iotox::sync::decode_sync_head_result(denied.value().response.payload);
  IOTOX_CHECK(denied_body.ok());
  IOTOX_CHECK(denied_body.value().status == iotox::sync::SyncHeadResultStatus::denied);
  IOTOX_CHECK(loads == 0U && offers == 0U);

  auto conflict = iotox::sync::make_sync_head_request_frame({"other"}, 201U);
  IOTOX_CHECK(conflict.ok());
  IOTOX_CHECK(!service.handle(denied_peer, conflict.value()).ok());
  denied_peer.authority.sequence += 1U;
  IOTOX_CHECK(!service.handle(denied_peer, request.value()).ok());
  IOTOX_CHECK(service.snapshot().replay_conflicts == 1U);

  // The bound is an exact-replay window, not a lifetime request budget.
  // Entries still in the window replay byte-for-byte. An older id that has
  // fallen out is processed as fresh read-only work under current authority.
  const auto authorized_peer = context(subscriber);
  auto request_202 =
      iotox::sync::make_sync_head_request_frame({configured.id}, 202U);
  auto request_203 =
      iotox::sync::make_sync_head_request_frame({configured.id}, 203U);
  auto request_204 =
      iotox::sync::make_sync_head_request_frame({configured.id}, 204U);
  IOTOX_CHECK(request_202.ok() && request_203.ok() && request_204.ok());
  auto first_202 = service.handle(authorized_peer, request_202.value());
  IOTOX_CHECK(first_202.ok() && loads == 1U);
  IOTOX_CHECK(service.handle(authorized_peer, request_203.value()).ok());
  IOTOX_CHECK(loads == 2U && service.snapshot().replay_evictions == 1U);
  auto retained_202 = service.handle(authorized_peer, request_202.value());
  IOTOX_CHECK(retained_202.ok() && retained_202.value().replayed);
  IOTOX_CHECK(same_frame(first_202.value().response,
                         retained_202.value().response));
  IOTOX_CHECK(loads == 2U);
  IOTOX_CHECK(service.handle(authorized_peer, request_204.value()).ok());
  IOTOX_CHECK(loads == 3U && service.snapshot().replay_evictions == 2U);
  auto retired_202 = service.handle(authorized_peer, request_202.value());
  IOTOX_CHECK(retired_202.ok() && !retired_202.value().replayed);
  IOTOX_CHECK(!same_frame(first_202.value().response,
                          retired_202.value().response));
  IOTOX_CHECK(loads == 4U && service.snapshot().replay_evictions == 3U);
  IOTOX_CHECK(service.snapshot().retained_replays == 2U);
}

IOTOX_TEST("sync publisher busy snapshot never waits behind object verification") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  const auto subscriber = principal(0x65U);
  const auto configured =
      policy(temporary.path() / "namespace", writer.public_key(), subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHeadPublicationRequest publication;
  publication.artifact = digest(0x71U);
  publication.manifest = digest(0x72U);
  publication.artifact_bytes = 100U;
  publication.manifest_bytes = 30U;
  auto head = iotox::sync::create_signed_head(
      configured, publication, std::nullopt, writer, crypto);
  IOTOX_CHECK(head.ok());
  auto head_record =
      iotox::sync::signed_head_record_digest(head.value(), crypto);
  IOTOX_CHECK(head_record.ok());

  std::mutex gate_mutex;
  std::condition_variable gate_cv;
  bool verification_entered = false;
  bool release_verification = false;
  iotox::sync::SyncPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head.value()}};
  };
  seams.head_record_digest = [&](const auto &value) {
    return iotox::sync::signed_head_record_digest(value, crypto);
  };
  seams.verify_object = [&](const auto &, const auto &) {
    std::unique_lock lock(gate_mutex);
    verification_entered = true;
    gate_cv.notify_all();
    gate_cv.wait(lock, [&] { return release_verification; });
    return iotox::Status::success();
  };
  seams.send_object = [](const iotox::sync::SyncTransferCarrier &carrier,
                         const auto &,
                         const iotox::FileId &file_id) {
    iotox::FileTransferRecord record;
    record.friend_number = carrier.friend_number;
    record.file_id = file_id;
    record.has_file_id = true;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.make_message_id = []() -> iotox::Result<std::uint64_t> {
    return 1200U;
  };
  iotox::sync::SyncPublisherService service(registry, std::move(seams));
  iotox::FileId transfer_id{};
  transfer_id.fill(0x73U);
  auto request = iotox::sync::make_sync_object_request_frame(
      {configured.id, iotox::sync::SyncObjectKind::artifact,
       head_record.value(), transfer_id},
      301U);
  IOTOX_CHECK(request.ok());
  std::optional<iotox::Result<iotox::sync::SyncPublisherResult>> outcome;
  std::thread worker([&] {
    outcome.emplace(service.handle(context(subscriber), request.value()));
  });
  {
    std::unique_lock lock(gate_mutex);
    gate_cv.wait(lock, [&] { return verification_entered; });
  }
  const bool publisher_was_busy = !service.try_snapshot().has_value();
  {
    std::scoped_lock lock(gate_mutex);
    release_verification = true;
  }
  gate_cv.notify_all();
  worker.join();
  IOTOX_CHECK(publisher_was_busy);
  IOTOX_CHECK(outcome.has_value());
  IOTOX_CHECK(outcome->ok());
  IOTOX_CHECK(outcome->value().file_offered);
  const auto observed = service.try_snapshot();
  IOTOX_CHECK(observed.has_value());
  IOTOX_CHECK(observed->retained_replays == 1U);
  IOTOX_CHECK(observed->object_requests == 1U);
}
