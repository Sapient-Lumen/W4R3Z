#include "iotox/sync_content_service.hpp"

#include "test_harness.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-content-service-XXXXXX";
    std::vector<char> storage(pattern.begin(), pattern.end());
    storage.push_back('\0');
    char *created = ::mkdtemp(storage.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
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

iotox::FileId file_id(std::uint8_t value) {
  iotox::FileId result{};
  result.fill(value);
  return result;
}

iotox::sync::NamespacePolicy policy(
    const std::filesystem::path &root,
    const iotox::security::SigningPublicKey &writer,
    const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = iotox::sync::Engine::content_v2;
  result.writers = {writer};
  result.subscribers = {subscriber};
  return result;
}

iotox::sync::SyncPeerContext context(
    const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::SyncPeerContext result;
  result.friend_number = 4U;
  result.online_epoch = 9U;
  result.authority_route_key.fill(0x71U);
  result.authority.initialized = true;
  result.authority.format =
      iotox::security::AuthorityLedgerFormat::v3;
  result.authority.ownership_epoch = 2U;
  result.authority.sequence = 7U;
  result.authority.tail_digest = digest(0x81U);
  result.peer_authority.friend_number = result.friend_number;
  result.peer_authority.online_epoch = result.online_epoch;
  result.peer_authority.connected = true;
  result.peer_authority.feature_negotiated = true;
  result.peer_authority.authority_v2_negotiated = true;
  result.peer_authority.authority_v3_negotiated = true;
  result.peer_authority.verifier_state =
      iotox::security::AuthorityVerifierState::authorized;
  result.peer_authority.remote_authorized = true;
  result.peer_authority.remote_principal = subscriber;
  result.peer_authority.remote_capabilities =
      static_cast<std::uint64_t>(
          iotox::security::Capability::sync_subscribe);
  result.peer_authority.local_authority_format = result.authority.format;
  result.peer_authority.local_authority_epoch =
      result.authority.ownership_epoch;
  result.peer_authority.local_authority_sequence =
      result.authority.sequence;
  result.peer_authority.local_authority_tail_digest =
      result.authority.tail_digest;
  result.transfer_carrier.route_key = result.authority_route_key;
  result.transfer_carrier.worker_id = result.online_epoch;
  result.transfer_carrier.friend_number = result.friend_number;
  result.transfer_carrier.online_epoch = result.online_epoch;
  result.content_transfer_negotiated = true;
  return result;
}

bool same_frame(const iotox::protocol::Frame &left,
                const iotox::protocol::Frame &right) {
  auto left_bytes = iotox::protocol::encode(left);
  auto right_bytes = iotox::protocol::encode(right);
  return left_bytes && right_bytes &&
         left_bytes.value() == right_bytes.value();
}

} // namespace

IOTOX_TEST("content publisher authorizes exact membership and offers once") {
  TempDirectory temporary;
  const auto writer = principal(0x31U);
  const auto subscriber = principal(0x41U);
  const auto configured =
      policy(temporary.path() / "namespace", writer, subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());

  iotox::sync::SignedHead head;
  head.namespace_id = configured.id;
  head.writer = writer;
  head.engine = configured.engine;
  head.generation = 1U;
  head.artifact = digest(0x51U);
  head.manifest = digest(0x52U);
  head.artifact_bytes = 1024U * 1024U;
  head.manifest_bytes = 4096U;
  head.signature.fill(0x53U);
  const auto head_record = digest(0x61U);
  const iotox::sync::SyncContentObjectDescriptor descriptor{
      iotox::sync::SyncContentObjectKind::artifact_chunk,
      digest(0x62U), 65536U, 7U,
      temporary.path() / "content-object"};

  std::uint64_t next_message = 800U;
  std::uint64_t loads = 0U;
  std::uint64_t resolves = 0U;
  std::uint64_t offers = 0U;
  iotox::FileId observed_file_id{};
  std::filesystem::path observed_path;
  iotox::sync::SyncContentPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    ++loads;
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  seams.head_record_digest = [&](const auto &) {
    return iotox::Result<iotox::sync::Digest>{head_record};
  };
  seams.resolve_object = [&](const auto &, const auto &, auto kind,
                             std::uint64_t logical_index) {
    ++resolves;
    IOTOX_CHECK(kind == descriptor.kind);
    IOTOX_CHECK(logical_index == descriptor.logical_index);
    return iotox::Result<iotox::sync::SyncContentObjectDescriptor>{
        descriptor};
  };
  seams.send_object = [&](const auto &, const auto &path,
                          const iotox::FileId &transfer_id) {
    ++offers;
    observed_path = path;
    observed_file_id = transfer_id;
    iotox::FileTransferRecord record;
    record.friend_number = 4U;
    record.file_id = transfer_id;
    record.has_file_id = true;
    record.file_size = descriptor.object_bytes;
    return iotox::Result<iotox::FileTransferRecord>{record};
  };
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return next_message++;
  };
  iotox::sync::SyncContentPublisherService::Config service_config;
  service_config.maximum_replays = 1U;
  iotox::sync::SyncContentPublisherService service(
      registry, std::move(seams), service_config);

  const iotox::FileId transfer_id = file_id(0x71U);
  const iotox::sync::SyncContentObjectRequest body{
      configured.id, descriptor.kind, head_record, descriptor.object,
      transfer_id, descriptor.logical_index, descriptor.object_bytes};
  auto request = iotox::sync::make_sync_content_object_request_frame(
      body, 101U);
  IOTOX_CHECK(request.ok());
  auto first = service.handle(context(subscriber), request.value());
  IOTOX_CHECK(first.ok() && first.value().file_offered);
  auto result = iotox::sync::decode_sync_content_object_result(
      first.value().response.payload);
  IOTOX_CHECK(result.ok());
  IOTOX_CHECK(result.value().status ==
              iotox::sync::SyncContentObjectResultStatus::offered);
  IOTOX_CHECK(observed_path == descriptor.path);
  IOTOX_CHECK(observed_file_id == transfer_id);

  auto replay = service.handle(context(subscriber), request.value());
  IOTOX_CHECK(replay.ok() && replay.value().replayed &&
              !replay.value().file_offered);
  IOTOX_CHECK(same_frame(first.value().response,
                         replay.value().response));
  IOTOX_CHECK(loads == 1U && resolves == 1U && offers == 1U);
  IOTOX_CHECK(service.snapshot().retained_replays == 1U);

  auto next_request = iotox::sync::make_sync_content_object_request_frame(
      body, 102U);
  IOTOX_CHECK(next_request.ok());
  auto next = service.handle(context(subscriber), next_request.value());
  IOTOX_CHECK(next.ok() && next.value().file_offered);
  IOTOX_CHECK(loads == 2U && resolves == 2U && offers == 2U);
  IOTOX_CHECK(service.snapshot().replay_evictions == 1U);
  auto retired = service.handle(context(subscriber), request.value());
  IOTOX_CHECK(retired.ok() && !retired.value().replayed &&
              retired.value().file_offered);
  IOTOX_CHECK(loads == 3U && resolves == 3U && offers == 3U);
  IOTOX_CHECK(service.snapshot().replay_evictions == 2U);
  service.peer_offline(4U, 9U);
  IOTOX_CHECK(service.snapshot().retained_replays == 0U);
}

IOTOX_TEST("content publisher refuses unnegotiated denied stale and false membership") {
  TempDirectory temporary;
  const auto writer = principal(0x32U);
  const auto subscriber = principal(0x42U);
  const auto configured =
      policy(temporary.path() / "namespace", writer, subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHead head;
  head.namespace_id = configured.id;
  head.writer = writer;
  head.engine = configured.engine;
  head.generation = 1U;
  head.artifact = digest(0x54U);
  head.manifest = digest(0x55U);
  head.artifact_bytes = 1024U;
  head.manifest_bytes = 512U;
  head.signature.fill(0x56U);
  const auto current_record = digest(0x64U);
  std::uint64_t offers = 0U;
  std::uint64_t message = 900U;
  iotox::sync::SyncContentPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  seams.head_record_digest = [&](const auto &) {
    return iotox::Result<iotox::sync::Digest>{current_record};
  };
  seams.resolve_object = [&](const auto &, const auto &, auto kind,
                             std::uint64_t index) {
    return iotox::Result<iotox::sync::SyncContentObjectDescriptor>{
        iotox::sync::SyncContentObjectDescriptor{
            kind, digest(0x65U), 128U, index,
            temporary.path() / "object"}};
  };
  seams.send_object = [&](const auto &, const auto &,
                          const iotox::FileId &) {
    ++offers;
    return iotox::Result<iotox::FileTransferRecord>{
        iotox::Status{iotox::ErrorCode::unavailable,
                      "offer must not run"}};
  };
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return message++;
  };
  iotox::sync::SyncContentPublisherService service(
      registry, std::move(seams));

  const iotox::sync::SyncContentObjectRequest body{
      configured.id,
      iotox::sync::SyncContentObjectKind::artifact_chunk,
      digest(0x66U), digest(0x67U), file_id(0x68U), 3U, 128U};
  auto request = iotox::sync::make_sync_content_object_request_frame(
      body, 201U);
  IOTOX_CHECK(request.ok());

  auto unnegotiated = context(subscriber);
  unnegotiated.content_transfer_negotiated = false;
  IOTOX_CHECK(!service.handle(unnegotiated, request.value()).ok());

  auto denied = service.handle(context(principal(0x99U)), request.value());
  IOTOX_CHECK(denied.ok());
  auto denied_body = iotox::sync::decode_sync_content_object_result(
      denied.value().response.payload);
  IOTOX_CHECK(denied_body.ok());
  IOTOX_CHECK(denied_body.value().status ==
              iotox::sync::SyncContentObjectResultStatus::denied);

  request = iotox::sync::make_sync_content_object_request_frame(
      body, 202U);
  IOTOX_CHECK(request.ok());
  auto stale = service.handle(context(subscriber), request.value());
  IOTOX_CHECK(stale.ok());
  auto stale_body = iotox::sync::decode_sync_content_object_result(
      stale.value().response.payload);
  IOTOX_CHECK(stale_body.ok());
  IOTOX_CHECK(stale_body.value().status ==
              iotox::sync::SyncContentObjectResultStatus::stale_head);

  auto exact = body;
  exact.head_record = current_record;
  auto false_member =
      iotox::sync::make_sync_content_object_request_frame(exact, 203U);
  IOTOX_CHECK(false_member.ok());
  auto refused = service.handle(context(subscriber), false_member.value());
  IOTOX_CHECK(refused.ok());
  auto refused_body = iotox::sync::decode_sync_content_object_result(
      refused.value().response.payload);
  IOTOX_CHECK(refused_body.ok());
  IOTOX_CHECK(refused_body.value().status ==
              iotox::sync::SyncContentObjectResultStatus::object_absent);
  IOTOX_CHECK(offers == 0U);
}

IOTOX_TEST("content publisher returns exact sparse availability once") {
  TempDirectory temporary;
  const auto writer = principal(0x33U);
  const auto subscriber = principal(0x43U);
  const auto configured =
      policy(temporary.path() / "namespace", writer, subscriber);
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({configured}).ok());
  iotox::sync::SignedHead head;
  head.namespace_id = configured.id;
  head.writer = writer;
  head.engine = configured.engine;
  head.generation = 1U;
  head.artifact = digest(0x57U);
  head.manifest = digest(0x58U);
  head.artifact_bytes = 4096U;
  head.manifest_bytes = 512U;
  head.signature.fill(0x59U);
  const auto head_record = digest(0x69U);
  std::uint64_t resolves = 0U;
  std::uint64_t next_message = 950U;
  iotox::sync::SyncContentPublisherSeams seams;
  seams.load_head = [&](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  seams.head_record_digest = [&](const auto &) {
    return iotox::Result<iotox::sync::Digest>{head_record};
  };
  seams.resolve_object = [&](const auto &, const auto &, auto,
                             std::uint64_t) {
    return iotox::Result<iotox::sync::SyncContentObjectDescriptor>{
        iotox::Status{iotox::ErrorCode::not_found, "unused"}};
  };
  seams.resolve_availability =
      [&](const auto &, const auto &, auto kind,
          std::uint64_t first, std::uint32_t count) {
        ++resolves;
        IOTOX_CHECK(kind ==
                    iotox::sync::SyncContentObjectKind::artifact_chunk);
        IOTOX_CHECK(first == 64U && count == 10U);
        return iotox::Result<
            iotox::sync::SyncContentAvailabilityDescriptor>{
            iotox::sync::SyncContentAvailabilityDescriptor{
                kind, first, count, 5U, {0x55U, 0x01U}}};
      };
  seams.send_object = [&](const auto &, const auto &,
                          const iotox::FileId &) {
    return iotox::Result<iotox::FileTransferRecord>{
        iotox::Status{iotox::ErrorCode::internal_error, "unused"}};
  };
  seams.make_message_id = [&]() -> iotox::Result<std::uint64_t> {
    return next_message++;
  };
  iotox::sync::SyncContentPublisherService service(
      registry, std::move(seams));

  const iotox::sync::SyncContentAvailabilityRequest body{
      configured.id,
      iotox::sync::SyncContentObjectKind::artifact_chunk,
      head_record, 64U, 10U};
  auto request =
      iotox::sync::make_sync_content_availability_request_frame(
          body, 301U);
  IOTOX_CHECK(request.ok());
  auto first = service.handle_availability(
      context(subscriber), request.value());
  IOTOX_CHECK(first.ok());
  auto result =
      iotox::sync::decode_sync_content_availability_result(
          first.value().response.payload);
  IOTOX_CHECK(result.ok());
  IOTOX_CHECK(
      result.value().status ==
      iotox::sync::SyncContentAvailabilityResultStatus::available);
  IOTOX_CHECK(result.value().availability ==
              std::vector<std::uint8_t>({0x55U, 0x01U}));
  auto replay = service.handle_availability(
      context(subscriber), request.value());
  IOTOX_CHECK(replay.ok() && replay.value().replayed);
  IOTOX_CHECK(same_frame(first.value().response,
                         replay.value().response));
  IOTOX_CHECK(resolves == 1U);
  IOTOX_CHECK(service.snapshot().availability_requests == 1U);
}
