#include "iotox/sync_content_publication.hpp"
#include "iotox/sync_content_service.hpp"
#include "iotox/sync_content_subscriber.hpp"
#include "iotox/sync_digest.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <cstdint>
#include <deque>
#include <filesystem>
#include <fstream>
#include <limits>
#include <optional>
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
    std::string pattern = "/tmp/iotox-content-subscriber-XXXXXX";
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
       const iotox::security::SigningPublicKey &publisher,
       const iotox::security::SigningPublicKey &subscriber) {
  iotox::sync::NamespacePolicy result;
  result.id = "content-subscriber-test";
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
  result.quotas.maximum_lanes = 2U;
  result.quotas.maximum_outstanding_requests = 16U;
  result.writers = {publisher};
  result.subscribers = {subscriber};
  return result;
}

void write_pattern(const std::filesystem::path &path, std::size_t bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  std::uint64_t state = 0xd1b54a32d192ed03ULL;
  for (std::size_t index = 0U; index < bytes; ++index) {
    state ^= state << 13U;
    state ^= state >> 7U;
    state ^= state << 17U;
    output.put(static_cast<char>(state & 0xffU));
  }
  if (!output)
    throw std::runtime_error("pattern write failed");
}

iotox::sync::SyncContentPublicationConfig publication_config() {
  iotox::sync::SyncContentPublicationConfig result;
  result.format = iotox::sync::SyncContentPublicationFormat::paged;
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

iotox::sync::SyncPeerContext
context(const iotox::security::SigningPublicKey &remote,
        iotox::security::Capability capability,
        std::uint32_t friend_number = 7U,
        std::uint64_t online_epoch = 11U) {
  iotox::sync::SyncPeerContext result;
  result.friend_number = friend_number;
  result.online_epoch = online_epoch;
  result.authority_route_key.fill(
      static_cast<std::uint8_t>(0x40U + friend_number));
  result.authority.initialized = true;
  result.authority.format = iotox::security::AuthorityLedgerFormat::v3;
  result.authority.ownership_epoch = 3U;
  result.authority.sequence = 5U;
  result.authority.tail_digest.fill(0x71U);
  result.peer_authority.friend_number = result.friend_number;
  result.peer_authority.online_epoch = result.online_epoch;
  result.peer_authority.connected = true;
  result.peer_authority.feature_negotiated = true;
  result.peer_authority.authority_v2_negotiated = true;
  result.peer_authority.authority_v3_negotiated = true;
  result.peer_authority.verifier_state =
      iotox::security::AuthorityVerifierState::authorized;
  result.peer_authority.remote_authorized = true;
  result.peer_authority.remote_principal = remote;
  result.peer_authority.remote_capabilities =
      static_cast<std::uint64_t>(capability);
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
  result.content_transfer_negotiated = true;
  return result;
}

iotox::sync::SyncPeerContext auxiliary_context(
    iotox::sync::SyncPeerContext result, std::uint8_t route_seed,
    std::uint64_t worker_id, std::uint32_t carrier_friend_number,
    std::uint64_t carrier_online_epoch) {
  result.transfer_carrier.carrier_class =
      iotox::sync::SyncCarrierClass::auxiliary;
  result.transfer_carrier.route_key.fill(route_seed);
  result.transfer_carrier.worker_id = worker_id;
  result.transfer_carrier.friend_number = carrier_friend_number;
  result.transfer_carrier.online_epoch = carrier_online_epoch;
  result.transfer_carrier.remote_route_generation = 9U;
  result.transfer_carrier.remote_coordinator_route_key =
      result.authority_route_key;
  result.transfer_carrier.primary_authority_online_epoch =
      result.online_epoch;
  return result;
}

class TransferBridge final {
public:
  struct Pending {
    iotox::FileId file_id{};
    std::filesystem::path source;
    std::filesystem::path destination;
    std::uint32_t file_number{0U};
    std::uint64_t bytes{0U};
  };

  [[nodiscard]] iotox::Result<iotox::FileTransferRecord>
  send(const iotox::sync::SyncTransferCarrier &carrier,
       const std::filesystem::path &path, const iotox::FileId &file_id) {
    std::error_code error;
    const std::uintmax_t raw_bytes = std::filesystem::file_size(path, error);
    if (error || raw_bytes > std::numeric_limits<std::uint64_t>::max()) {
      return iotox::Status{iotox::ErrorCode::io_error,
                           "bridge source size is unavailable"};
    }
    if (std::any_of(pending_.begin(), pending_.end(),
                    [&file_id](const Pending &entry) {
                      return entry.file_id == file_id;
                    })) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "bridge FileId was reused"};
    }
    Pending pending;
    pending.file_id = file_id;
    pending.source = path;
    pending.file_number = next_file_number_++;
    pending.bytes = static_cast<std::uint64_t>(raw_bytes);
    pending_.push_back(pending);
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::outgoing;
    record.state = iotox::FileTransferState::offered;
    record.friend_number = carrier.friend_number;
    record.file_number = pending.file_number;
    record.file_size = pending.bytes;
    record.file_id = file_id;
    record.has_file_id = true;
    record.local_path = path;
    return record;
  }

  [[nodiscard]] iotox::Result<iotox::FileTransferRecord>
  receive(const iotox::sync::SyncTransferCarrier &carrier,
          std::uint32_t file_number, const std::filesystem::path &destination) {
    auto found = find_number(file_number);
    if (found == pending_.end()) {
      return iotox::Status{iotox::ErrorCode::not_found,
                           "bridge transfer is absent"};
    }
    std::error_code error;
    const bool copied =
        std::filesystem::copy_file(found->source, destination, error);
    if (!copied || error ||
        ::chmod(destination.c_str(), static_cast<mode_t>(0600)) != 0) {
      return iotox::Status{iotox::ErrorCode::io_error,
                           "bridge receive copy failed"};
    }
    found->destination = destination;
    ++receive_count_;
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::active;
    record.friend_number = carrier.friend_number;
    record.file_number = found->file_number;
    record.file_size = found->bytes;
    record.file_id = found->file_id;
    record.has_file_id = true;
    record.local_path = destination;
    return record;
  }

  [[nodiscard]] iotox::Result<iotox::FileTransferRecord>
  offer(const iotox::FileId &file_id, std::uint32_t friend_number) const {
    const auto found = std::find_if(
        pending_.begin(), pending_.end(),
        [&file_id](const Pending &entry) { return entry.file_id == file_id; });
    if (found == pending_.end()) {
      return iotox::Status{iotox::ErrorCode::not_found,
                           "bridge offer is absent"};
    }
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::offered;
    record.friend_number = friend_number;
    record.file_number = found->file_number;
    record.file_size = found->bytes;
    record.file_id = found->file_id;
    record.has_file_id = true;
    return record;
  }

  [[nodiscard]] iotox::Result<iotox::FileTransferRecord>
  terminal(std::uint32_t file_number, std::uint32_t friend_number) const {
    const auto found = std::find_if(pending_.begin(), pending_.end(),
                                    [file_number](const Pending &entry) {
                                      return entry.file_number == file_number;
                                    });
    if (found == pending_.end() || found->destination.empty()) {
      return iotox::Status{iotox::ErrorCode::not_found,
                           "bridge terminal is absent"};
    }
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::completed;
    record.friend_number = friend_number;
    record.file_number = found->file_number;
    record.file_size = found->bytes;
    record.position = found->bytes;
    record.file_id = found->file_id;
    record.has_file_id = true;
    record.local_path = found->destination;
    return record;
  }

  [[nodiscard]] iotox::Status cancel(std::uint32_t file_number) {
    if (find_number(file_number) == pending_.end()) {
      return iotox::Status{iotox::ErrorCode::not_found,
                           "bridge cancellation is absent"};
    }
    ++cancel_count_;
    return iotox::Status::success();
  }

  [[nodiscard]] iotox::Status retire(std::uint32_t file_number) {
    if (find_number(file_number) == pending_.end()) {
      return iotox::Status{iotox::ErrorCode::not_found,
                           "bridge retirement is absent"};
    }
    ++retire_count_;
    return iotox::Status::success();
  }

  [[nodiscard]] std::uint64_t receive_count() const noexcept {
    return receive_count_;
  }
  [[nodiscard]] std::uint64_t cancel_count() const noexcept {
    return cancel_count_;
  }
  [[nodiscard]] std::uint64_t retire_count() const noexcept {
    return retire_count_;
  }

private:
  [[nodiscard]] std::vector<Pending>::iterator
  find_number(std::uint32_t file_number) {
    return std::find_if(pending_.begin(), pending_.end(),
                        [file_number](const Pending &entry) {
                          return entry.file_number == file_number;
                        });
  }

  std::vector<Pending> pending_;
  std::uint32_t next_file_number_{41U};
  std::uint64_t receive_count_{0U};
  std::uint64_t cancel_count_{0U};
  std::uint64_t retire_count_{0U};
};

iotox::FileId numbered_file_id(std::uint64_t value) {
  iotox::FileId result{};
  for (std::size_t index = 0U; index < sizeof(value); ++index) {
    result[index] = static_cast<std::uint8_t>(value & 0xffU);
    value >>= 8U;
  }
  return result;
}

iotox::sync::SyncContentSubscriberService::Config
subscriber_config(const iotox::security::DeviceIdentity &subscriber,
                  const iotox::security::Sodium &crypto) {
  iotox::sync::SyncContentSubscriberService::Config result;
  result.maximum_jobs = 4U;
  result.content.maximum_window_objects = 11U;
  result.content.maximum_page_window_objects = 7U;
  result.content.workspace_budget_bytes = 1024U * 1024U;
  result.content.object_io_buffer_bytes = 4096U;
  result.content.manifest_buffer_bytes = 4096U;
  result.content.fsync_on_commit = false;
  result.acceptance.io_buffer_bytes = 4096U;
  result.acceptance.fsync_on_commit = false;
  result.identity = &subscriber;
  result.sodium = &crypto;
  return result;
}

iotox::sync::SyncContentSubscriberSeams
subscriber_seams(TransferBridge &bridge, std::uint64_t &next_message,
                 std::uint64_t &next_file_id) {
  iotox::sync::SyncContentSubscriberSeams seams;
  seams.make_message_id = [&next_message]() -> iotox::Result<std::uint64_t> {
    return next_message++;
  };
  seams.make_file_id = [&next_file_id]() -> iotox::Result<iotox::FileId> {
    return numbered_file_id(next_file_id++);
  };
  seams.receive_to_path =
      [&bridge](const iotox::sync::SyncTransferCarrier &carrier,
                std::uint32_t file_number,
                const std::filesystem::path &destination) {
        return bridge.receive(carrier, file_number, destination);
      };
  seams.cancel_transfer = [&bridge](const iotox::sync::SyncTransferCarrier &,
                                    std::uint32_t file_number) {
    return bridge.cancel(file_number);
  };
  seams.retire_transfer = [&bridge](const iotox::sync::SyncTransferCarrier &,
                                    std::uint32_t file_number) {
    return bridge.retire(file_number);
  };
  return seams;
}

} // namespace

IOTOX_TEST("content subscriber converges a real paged publication HEAD last") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto remote = policy(temporary.path() / "remote",
                             publisher.public_key(), subscriber.public_key());
  const auto local = policy(temporary.path() / "local", publisher.public_key(),
                            subscriber.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 384U * 1024U);
  iotox::sync::SignedHeadStore remote_heads(remote.root);
  auto published = iotox::sync::publish_local_content_revision(
      remote, source, publisher, crypto, remote_heads, publication_config());
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(published.value().pages > 1U && published.value().chunks > 4U);
  const iotox::sync::SignedHead head = published.value().publication.head;

  iotox::sync::NamespaceRegistry remote_registry;
  iotox::sync::NamespaceRegistry local_registry;
  IOTOX_CHECK(remote_registry.replace({remote}).ok());
  IOTOX_CHECK(local_registry.replace({local}).ok());
  TransferBridge bridge;
  std::uint64_t publisher_message = 7000U;
  iotox::sync::SyncContentPublisherSeams publisher_seams;
  publisher_seams.load_head = [&head](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  publisher_seams.head_record_digest = [&crypto](const auto &candidate) {
    return iotox::sync::signed_head_record_digest(candidate, crypto);
  };
  publisher_seams.resolve_object = [](const auto &configured,
                                      const auto &candidate, auto kind,
                                      std::uint64_t logical_index) {
    return iotox::sync::resolve_sync_content_object(configured, candidate, kind,
                                                    logical_index);
  };
  publisher_seams.send_object = [&bridge](const auto &carrier, const auto &path,
                                          const auto &file_id) {
    return bridge.send(carrier, path, file_id);
  };
  publisher_seams.make_message_id =
      [&publisher_message]() -> iotox::Result<std::uint64_t> {
    return publisher_message++;
  };
  iotox::sync::SyncContentPublisherService publisher_service(
      remote_registry, std::move(publisher_seams));

  std::uint64_t subscriber_message = 100U;
  std::uint64_t subscriber_file_id = 1U;
  iotox::sync::SyncContentSubscriberService subscriber_service(
      local_registry,
      subscriber_seams(bridge, subscriber_message, subscriber_file_id),
      subscriber_config(subscriber, crypto));
  const auto publisher_context = context(
      publisher.public_key(), iotox::security::Capability::sync_publish);
  const auto subscriber_context = context(
      subscriber.public_key(), iotox::security::Capability::sync_subscribe);

  auto head_request =
      subscriber_service.begin_pull(publisher_context, local.id);
  IOTOX_CHECK_MSG(head_request.ok(), head_request.status().message());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head}, 9000U,
      head_request.value().frame.message_id);
  IOTOX_CHECK(head_result.ok());
  auto requests = subscriber_service.handle_head_result(publisher_context,
                                                        head_result.value());
  IOTOX_CHECK_MSG(requests.ok(), requests.status().message());

  bool tested_early_offer = false;
  std::uint64_t completed_transfers = 0U;
  for (std::size_t step = 0U; step < 2048U && !requests.value().empty();
       ++step) {
    IOTOX_CHECK(requests.value().size() == 1U);
    const iotox::protocol::Frame request = requests.value().front().frame;
    auto request_body =
        iotox::sync::decode_sync_content_object_request(request.payload);
    IOTOX_CHECK(request_body.ok());
    auto served = publisher_service.handle(subscriber_context, request);
    IOTOX_CHECK_MSG(served.ok(), served.status().message());
    IOTOX_CHECK(served.value().file_offered);
    auto offer = bridge.offer(request_body.value().transfer_id,
                              publisher_context.friend_number);
    IOTOX_CHECK(offer.ok());
    if (!tested_early_offer) {
      auto retained =
          subscriber_service.handle_offer(publisher_context, offer.value());
      IOTOX_CHECK(retained.ok() && retained.value());
      IOTOX_CHECK(bridge.receive_count() == 0U);
      tested_early_offer = true;
    }
    const auto result_status = subscriber_service.handle_object_result(
        publisher_context, served.value().response);
    IOTOX_CHECK_MSG(result_status.ok(), result_status.message());
    if (bridge.receive_count() == completed_transfers) {
      auto admitted =
          subscriber_service.handle_offer(publisher_context, offer.value());
      IOTOX_CHECK(admitted.ok() && admitted.value());
    }
    IOTOX_CHECK(bridge.receive_count() == completed_transfers + 1U);
    auto terminal = bridge.terminal(offer.value().file_number,
                                    publisher_context.friend_number);
    IOTOX_CHECK(terminal.ok());
    requests = subscriber_service.handle_terminal(
        publisher_context, terminal.value(),
        iotox::routes::WorkerTransferOutcome::completed, iotox::ErrorCode::ok);
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    ++completed_transfers;
  }
  IOTOX_CHECK(tested_early_offer && requests.ok() && requests.value().empty());
  const auto snapshots = subscriber_service.snapshot();
  IOTOX_CHECK(snapshots.size() == 1U);
  IOTOX_CHECK(snapshots.front().state ==
              iotox::sync::SyncContentPullState::complete);
  IOTOX_CHECK(snapshots.front().committed_objects == completed_transfers);
  IOTOX_CHECK(completed_transfers > 5U);
  IOTOX_CHECK(bridge.cancel_count() == 0U && bridge.retire_count() == 0U);

  iotox::sync::AcceptedHeadStore accepted(local.root);
  auto accepted_head = accepted.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(accepted_head.ok() && accepted_head.value());
  IOTOX_CHECK(accepted_head.value()->record ==
              published.value().publication.record);
  const auto local_artifact =
      iotox::sync::sync_content_object_path(local, head.artifact);
  IOTOX_CHECK(std::filesystem::exists(local_artifact));
  auto source_digest = iotox::sync::hash_sync_file_sha256(source);
  auto local_digest = iotox::sync::hash_sync_file_sha256(local_artifact);
  IOTOX_CHECK(source_digest.ok() && local_digest.ok());
  IOTOX_CHECK(source_digest.value() == local_digest.value());
  iotox::sync::SyncContentAttemptStore attempts(
      local.root,
      {static_cast<std::size_t>(local.quotas.maximum_outstanding_requests)});
  auto journal = attempts.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
  // Window transitions may burn an attempt ID before the coordinator reports
  // that no assignment exists in the exhausted window. IDs are monotonic
  // replay fences, not a transfer counter.
  IOTOX_CHECK(journal.value().high_attempt_id >= completed_transfers);
}

IOTOX_TEST("content subscriber overlaps two exact lanes from one source") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto remote = policy(temporary.path() / "remote",
                             publisher.public_key(), subscriber.public_key());
  const auto local = policy(temporary.path() / "local", publisher.public_key(),
                            subscriber.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 384U * 1024U);
  iotox::sync::SignedHeadStore remote_heads(remote.root);
  auto published = iotox::sync::publish_local_content_revision(
      remote, source, publisher, crypto, remote_heads, publication_config());
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(published.value().pages > 2U && published.value().chunks > 4U);
  const iotox::sync::SignedHead head = published.value().publication.head;

  iotox::sync::NamespaceRegistry remote_registry;
  iotox::sync::NamespaceRegistry local_registry;
  IOTOX_CHECK(remote_registry.replace({remote}).ok());
  IOTOX_CHECK(local_registry.replace({local}).ok());
  TransferBridge bridge;
  std::uint64_t publisher_message = 17000U;
  iotox::sync::SyncContentPublisherSeams publisher_seams;
  publisher_seams.load_head = [&head](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  publisher_seams.head_record_digest = [&crypto](const auto &candidate) {
    return iotox::sync::signed_head_record_digest(candidate, crypto);
  };
  publisher_seams.resolve_object = [](const auto &configured,
                                      const auto &candidate, auto kind,
                                      std::uint64_t logical_index) {
    return iotox::sync::resolve_sync_content_object(configured, candidate, kind,
                                                    logical_index);
  };
  publisher_seams.send_object = [&bridge](const auto &carrier,
                                          const auto &path,
                                          const auto &file_id) {
    return bridge.send(carrier, path, file_id);
  };
  publisher_seams.make_message_id =
      [&publisher_message]() -> iotox::Result<std::uint64_t> {
    return publisher_message++;
  };
  iotox::sync::SyncContentPublisherService publisher_service(
      remote_registry, std::move(publisher_seams));

  std::uint64_t subscriber_message = 500U;
  std::uint64_t subscriber_file_id = 200U;
  auto config = subscriber_config(subscriber, crypto);
  config.maximum_lanes = 2U;
  iotox::sync::SyncContentSubscriberService subscriber_service(
      local_registry,
      subscriber_seams(bridge, subscriber_message, subscriber_file_id),
      config);
  const auto publisher_context = context(
      publisher.public_key(), iotox::security::Capability::sync_publish);
  const auto subscriber_context = context(
      subscriber.public_key(), iotox::security::Capability::sync_subscribe);

  auto head_request =
      subscriber_service.begin_pull(publisher_context, local.id);
  IOTOX_CHECK_MSG(head_request.ok(), head_request.status().message());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head}, 18000U,
      head_request.value().frame.message_id);
  IOTOX_CHECK(head_result.ok());
  auto root_requests = subscriber_service.handle_head_result(
      publisher_context, head_result.value());
  IOTOX_CHECK(root_requests.ok() && root_requests.value().size() == 1U);

  const auto serve_to_terminal =
      [&](iotox::sync::SyncContentSubscriberService &service,
          const iotox::sync::SyncContentDispatch &dispatch)
      -> iotox::Result<iotox::FileTransferRecord> {
    auto body = iotox::sync::decode_sync_content_object_request(
        dispatch.frame.payload);
    if (!body)
      return body.status();
    auto served = publisher_service.handle(subscriber_context, dispatch.frame);
    if (!served)
      return served.status();
    if (!served.value().file_offered) {
      return iotox::Status{
          iotox::ErrorCode::protocol_error,
          "publisher did not offer a requested content object"};
    }
    const iotox::Status result = service.handle_object_result(
        dispatch.context, served.value().response);
    if (!result.ok())
      return result;
    auto offer = bridge.offer(body.value().transfer_id,
                              dispatch.context.transfer_carrier.friend_number);
    if (!offer)
      return offer.status();
    auto admitted = service.handle_offer(dispatch.context, offer.value());
    if (!admitted)
      return admitted.status();
    if (!admitted.value()) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "subscriber did not admit its exact offer"};
    }
    return bridge.terminal(offer.value().file_number,
                           dispatch.context.transfer_carrier.friend_number);
  };

  auto root_terminal =
      serve_to_terminal(subscriber_service, root_requests.value().front());
  IOTOX_CHECK_MSG(root_terminal.ok(), root_terminal.status().message());
  auto first_wave = subscriber_service.handle_terminal(
      publisher_context, root_terminal.value(),
      iotox::routes::WorkerTransferOutcome::completed, iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(first_wave.ok(), first_wave.status().message());
  IOTOX_CHECK(first_wave.value().size() == 2U);

  auto lane_zero = serve_to_terminal(subscriber_service, first_wave.value()[0]);
  auto lane_one = serve_to_terminal(subscriber_service, first_wave.value()[1]);
  IOTOX_CHECK_MSG(lane_zero.ok(), lane_zero.status().message());
  IOTOX_CHECK_MSG(lane_one.ok(), lane_one.status().message());
  auto active = subscriber_service.snapshot();
  IOTOX_CHECK(active.size() == 1U && active.front().active_lanes == 2U);
  IOTOX_CHECK(active.front().lane_bindings.size() == 2U);
  IOTOX_CHECK(!active.front().active_file_id &&
              !active.front().active_file_number);
  IOTOX_CHECK(active.front().lane_bindings[0].source_id ==
              active.front().lane_bindings[1].source_id);
  IOTOX_CHECK(active.front().lane_bindings[0].request_id !=
              active.front().lane_bindings[1].request_id);
  IOTOX_CHECK(active.front().lane_bindings[0].file_id !=
              active.front().lane_bindings[1].file_id);
  IOTOX_CHECK(active.front().lane_bindings[0].transport_admitted &&
              active.front().lane_bindings[1].transport_admitted);

  // Complete the later-issued lane first. The subscriber must correlate it
  // independently and refill only the vacated slot.
  auto after_one = subscriber_service.handle_terminal(
      publisher_context, lane_one.value(),
      iotox::routes::WorkerTransferOutcome::completed, iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(after_one.ok(), after_one.status().message());
  IOTOX_CHECK(after_one.value().size() == 1U);
  active = subscriber_service.snapshot();
  IOTOX_CHECK(active.front().active_lanes == 2U);
  auto after_zero = subscriber_service.handle_terminal(
      publisher_context, lane_zero.value(),
      iotox::routes::WorkerTransferOutcome::completed, iotox::ErrorCode::ok);
  IOTOX_CHECK_MSG(after_zero.ok(), after_zero.status().message());

  std::deque<iotox::sync::SyncContentDispatch> work;
  work.insert(work.end(), after_one.value().begin(), after_one.value().end());
  work.insert(work.end(), after_zero.value().begin(), after_zero.value().end());
  std::uint32_t maximum_active_lanes = 2U;
  for (std::size_t step = 0U; step < 4096U && !work.empty(); ++step) {
    const auto dispatch = work.front();
    work.pop_front();
    auto terminal = serve_to_terminal(subscriber_service, dispatch);
    IOTOX_CHECK_MSG(terminal.ok(), terminal.status().message());
    auto next = subscriber_service.handle_terminal(
        dispatch.context, terminal.value(),
        iotox::routes::WorkerTransferOutcome::completed,
        iotox::ErrorCode::ok);
    IOTOX_CHECK_MSG(next.ok(), next.status().message());
    work.insert(work.end(), next.value().begin(), next.value().end());
    const auto observed = subscriber_service.snapshot();
    IOTOX_CHECK(observed.size() == 1U && observed.front().active_lanes <= 2U);
    maximum_active_lanes =
        std::max(maximum_active_lanes, observed.front().active_lanes);
  }
  IOTOX_CHECK(work.empty());
  const auto complete = subscriber_service.snapshot();
  IOTOX_CHECK(complete.size() == 1U);
  IOTOX_CHECK(complete.front().state ==
              iotox::sync::SyncContentPullState::complete);
  IOTOX_CHECK(complete.front().active_lanes == 0U);
  IOTOX_CHECK(complete.front().lane_bindings.empty());
  IOTOX_CHECK(maximum_active_lanes == 2U);
  IOTOX_CHECK(complete.front().requested_objects ==
              complete.front().committed_objects);
  auto expected = iotox::sync::hash_sync_file_sha256(source);
  auto observed = iotox::sync::hash_sync_file_sha256(
      iotox::sync::sync_content_object_path(local, head.artifact));
  IOTOX_CHECK(expected.ok() && observed.ok());
  IOTOX_CHECK(expected.value() == observed.value());

  // A terminal failure in either lane fails the atomic job, fences that exact
  // attempt, cancels its still-live sibling, and leaves no active CTA1 state.
  const auto failed_local = policy(temporary.path() / "failed-local",
                                   publisher.public_key(),
                                   subscriber.public_key());
  iotox::sync::NamespaceRegistry failed_registry;
  IOTOX_CHECK(failed_registry.replace({failed_local}).ok());
  iotox::sync::SyncContentSubscriberService failed_service(
      failed_registry,
      subscriber_seams(bridge, subscriber_message, subscriber_file_id),
      config);
  auto failed_head = failed_service.begin_pull(publisher_context,
                                               failed_local.id);
  IOTOX_CHECK(failed_head.ok());
  auto failed_head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head}, 19000U,
      failed_head.value().frame.message_id);
  IOTOX_CHECK(failed_head_result.ok());
  auto failed_root = failed_service.handle_head_result(
      publisher_context, failed_head_result.value());
  IOTOX_CHECK(failed_root.ok() && failed_root.value().size() == 1U);
  auto failed_root_terminal =
      serve_to_terminal(failed_service, failed_root.value().front());
  IOTOX_CHECK(failed_root_terminal.ok());
  auto failed_wave = failed_service.handle_terminal(
      publisher_context, failed_root_terminal.value(),
      iotox::routes::WorkerTransferOutcome::completed, iotox::ErrorCode::ok);
  IOTOX_CHECK(failed_wave.ok() && failed_wave.value().size() == 2U);
  auto failed_zero = serve_to_terminal(failed_service, failed_wave.value()[0]);
  auto failed_one = serve_to_terminal(failed_service, failed_wave.value()[1]);
  IOTOX_CHECK(failed_zero.ok() && failed_one.ok());
  const std::uint64_t cancels_before_failure = bridge.cancel_count();
  auto failed_terminal = failed_service.handle_terminal(
      publisher_context, failed_one.value(),
      iotox::routes::WorkerTransferOutcome::failed,
      iotox::ErrorCode::io_error);
  IOTOX_CHECK(failed_terminal.ok() && failed_terminal.value().empty());
  const auto failed_snapshot = failed_service.snapshot();
  IOTOX_CHECK(failed_snapshot.size() == 1U);
  IOTOX_CHECK(failed_snapshot.front().state ==
              iotox::sync::SyncContentPullState::failed);
  IOTOX_CHECK(failed_snapshot.front().active_lanes == 0U);
  IOTOX_CHECK(bridge.cancel_count() == cancels_before_failure + 1U);
  iotox::sync::SyncContentAttemptStore failed_attempts(
      failed_local.root,
      {static_cast<std::size_t>(
          failed_local.quotas.maximum_outstanding_requests)});
  auto failed_journal = failed_attempts.load(
      failed_local, subscriber.public_key(), crypto);
  IOTOX_CHECK(failed_journal.ok() && failed_journal.value().active.empty());
}

void run_complementary_auxiliary_sources(bool same_principal) {
  TempDirectory temporary;
  auto crypto = sodium();
  auto writer = identity(temporary.path() / "writer.identity", crypto);
  auto second_source =
      identity(temporary.path() / "second-source.identity", crypto);
  auto subscriber =
      identity(temporary.path() / "subscriber.identity", crypto);
  auto remote_a = policy(temporary.path() / "remote-a", writer.public_key(),
                         subscriber.public_key());
  auto remote_b = policy(temporary.path() / "remote-b", writer.public_key(),
                         subscriber.public_key());
  auto local = policy(temporary.path() / "local", writer.public_key(),
                      subscriber.public_key());
  remote_a.writers.push_back(second_source.public_key());
  remote_b.writers.push_back(second_source.public_key());
  local.writers.push_back(second_source.public_key());
  std::sort(remote_a.writers.begin(), remote_a.writers.end());
  std::sort(remote_b.writers.begin(), remote_b.writers.end());
  std::sort(local.writers.begin(), local.writers.end());

  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 384U * 1024U);
  iotox::sync::SignedHeadStore heads_a(remote_a.root);
  iotox::sync::SignedHeadStore heads_b(remote_b.root);
  auto published_a = iotox::sync::publish_local_content_revision(
      remote_a, source, writer, crypto, heads_a, publication_config());
  auto published_b = iotox::sync::publish_local_content_revision(
      remote_b, source, writer, crypto, heads_b, publication_config());
  IOTOX_CHECK_MSG(published_a.ok(), published_a.status().message());
  IOTOX_CHECK_MSG(published_b.ok(), published_b.status().message());
  IOTOX_CHECK(published_a.value().publication.record ==
              published_b.value().publication.record);
  IOTOX_CHECK(published_a.value().pages > 1U &&
              published_a.value().chunks > 4U);
  const iotox::sync::SignedHead head =
      published_a.value().publication.head;

  // Model an explicit retry after a failed whole pull: the verified root
  // manifest is an immutable prerequisite retained from the earlier attempt.
  // With both sources registered before HEAD dispatch, the subscriber must
  // request exact availability immediately instead of assuming the primary is
  // complete and racing into an object that only the auxiliary source holds.
  std::filesystem::create_directory(local.root);
  IOTOX_CHECK(::chmod(local.root.c_str(), static_cast<mode_t>(0700)) == 0);
  {
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(local);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(
        iotox::sync::prepare_sync_content_staging(local, transaction.value())
            .ok());
    const auto staged =
        iotox::sync::sync_content_staging_root(local) / "root-manifest.part";
    IOTOX_CHECK(std::filesystem::copy_file(
        iotox::sync::sync_content_object_path(remote_a, head.manifest), staged));
    IOTOX_CHECK(::chmod(staged.c_str(), static_cast<mode_t>(0600)) == 0);
    iotox::sync::SyncContentCommitConfig commit;
    commit.io_buffer_bytes = 4096U;
    commit.fsync_on_commit = false;
    auto committed = iotox::sync::commit_sync_content_staging(
        local, head.manifest, head.manifest_bytes, staged, transaction.value(),
        commit);
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
  }

  const auto split_kind = [&](iotox::sync::SyncContentObjectKind kind,
                              std::uint64_t objects) {
    for (std::uint64_t index = 0U; index < objects; ++index) {
      auto object_a = iotox::sync::resolve_sync_content_object(
          remote_a, head, kind, index);
      auto object_b = iotox::sync::resolve_sync_content_object(
          remote_b, head, kind, index);
      IOTOX_CHECK_MSG(
          object_a.ok() && object_b.ok(),
          "split resolve kind=" + std::to_string(static_cast<unsigned>(kind)) +
              " index=" + std::to_string(index) + " a=" +
              (object_a.ok() ? std::string{"ok"}
                             : object_a.status().message()) +
              " b=" +
              (object_b.ok() ? std::string{"ok"}
                             : object_b.status().message()));
      std::error_code error;
      const bool removed = std::filesystem::remove(
          (index % 2U) == 0U ? object_b.value().path
                             : object_a.value().path,
          error);
      IOTOX_CHECK(removed && !error);
    }
  };
  split_kind(iotox::sync::SyncContentObjectKind::artifact_chunk,
             published_a.value().chunks);

  iotox::sync::NamespaceRegistry registry_a;
  iotox::sync::NamespaceRegistry registry_b;
  iotox::sync::NamespaceRegistry local_registry;
  IOTOX_CHECK(registry_a.replace({remote_a}).ok());
  IOTOX_CHECK(registry_b.replace({remote_b}).ok());
  IOTOX_CHECK(local_registry.replace({local}).ok());
  TransferBridge bridge;
  std::uint64_t publisher_message = 12000U;
  const auto make_publisher_seams =
      [&](const iotox::sync::SignedHead &served_head) {
        iotox::sync::SyncContentPublisherSeams seams;
        seams.load_head = [served_head](const auto &) {
          return iotox::Result<std::optional<iotox::sync::SignedHead>>{
              std::optional<iotox::sync::SignedHead>{served_head}};
        };
        seams.head_record_digest = [&crypto](const auto &candidate) {
          return iotox::sync::signed_head_record_digest(candidate, crypto);
        };
        seams.resolve_object = [](const auto &configured,
                                  const auto &candidate, auto kind,
                                  std::uint64_t index) {
          return iotox::sync::resolve_sync_content_object(
              configured, candidate, kind, index);
        };
        seams.resolve_availability = [](const auto &configured,
                                        const auto &candidate, auto kind,
                                        std::uint64_t first,
                                        std::uint32_t count) {
          return iotox::sync::resolve_sync_content_availability(
              configured, candidate, kind, first, count);
        };
        seams.send_object = [&bridge](const auto &carrier, const auto &path,
                                      const auto &file_id) {
          return bridge.send(carrier, path, file_id);
        };
        seams.make_message_id =
            [&publisher_message]() -> iotox::Result<std::uint64_t> {
          return publisher_message++;
        };
        return seams;
      };
  iotox::sync::SyncContentPublisherService publisher_a(
      registry_a, make_publisher_seams(head));
  iotox::sync::SyncContentPublisherService publisher_b(
      registry_b, make_publisher_seams(head));

  std::uint64_t subscriber_message = 300U;
  std::uint64_t subscriber_file_id = 100U;
  iotox::sync::SyncContentSubscriberService subscriber_service(
      local_registry,
      subscriber_seams(bridge, subscriber_message, subscriber_file_id),
      subscriber_config(subscriber, crypto));
  const auto source_a_primary_context =
      context(writer.public_key(), iotox::security::Capability::sync_publish,
              7U, 11U);
  const auto source_a_context = auxiliary_context(
      source_a_primary_context, 0xA1U, 101U, 70U, 21U);
  const auto source_b_primary_context =
      same_principal
          ? source_a_primary_context
          : context(second_source.public_key(),
                    iotox::security::Capability::sync_publish, 8U, 12U);
  const auto source_b_context = auxiliary_context(
      source_b_primary_context, 0xB1U, 102U,
      same_principal ? 70U : 80U, 22U);
  const auto subscriber_a_context = auxiliary_context(
      context(subscriber.public_key(),
              iotox::security::Capability::sync_subscribe, 7U, 11U),
      0xA2U, 201U, 71U, 31U);
  const auto subscriber_b_primary_context =
      same_principal
          ? context(subscriber.public_key(),
                    iotox::security::Capability::sync_subscribe, 7U, 11U)
          : context(subscriber.public_key(),
                    iotox::security::Capability::sync_subscribe, 8U, 12U);
  const auto subscriber_b_context = auxiliary_context(
      subscriber_b_primary_context, 0xB2U, 202U,
      same_principal ? 71U : 81U, 32U);

  auto head_request =
      subscriber_service.begin_pull(source_a_primary_context, local.id);
  IOTOX_CHECK_MSG(head_request.ok(), head_request.status().message());
  IOTOX_CHECK(head_request.value().context.transfer_carrier.carrier_class ==
              iotox::sync::SyncCarrierClass::primary);
  IOTOX_CHECK(subscriber_service
                  .bind_source_carrier(
                      head_request.value().frame.message_id,
                      source_a_context)
                  .ok());
  auto wrong_principal = source_a_context;
  wrong_principal.peer_authority.remote_principal =
      second_source.public_key();
  const auto wrong_binding = subscriber_service.bind_source_carrier(
      head_request.value().frame.message_id, wrong_principal);
  IOTOX_CHECK(!wrong_binding.ok() &&
              wrong_binding.code() == iotox::ErrorCode::unavailable);
  const auto unauthorized_source_b = context(
      second_source.public_key(),
      iotox::security::Capability::sync_subscribe, 8U, 12U);
  auto refused = subscriber_service.add_source(
      head_request.value().frame.message_id, unauthorized_source_b);
  IOTOX_CHECK(!refused.ok() &&
              refused.status().code() == iotox::ErrorCode::protocol_error);
  auto added = subscriber_service.add_source(
      head_request.value().frame.message_id, source_b_context);
  IOTOX_CHECK_MSG(added.ok(), added.status().message());
  IOTOX_CHECK(added.value().empty());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head}, 13000U,
      head_request.value().frame.message_id);
  IOTOX_CHECK(head_result.ok());
  auto initial = subscriber_service.handle_head_result(
      source_a_primary_context, head_result.value());
  IOTOX_CHECK_MSG(initial.ok(), initial.status().message());
  IOTOX_CHECK(initial.value().size() == 2U);
  IOTOX_CHECK(std::all_of(
      initial.value().begin(), initial.value().end(), [](const auto &item) {
        return item.frame.type == iotox::protocol::MessageType::
                                      sync_content_availability_request;
      }));
  IOTOX_CHECK(std::all_of(
      initial.value().begin(), initial.value().end(), [](const auto &item) {
        return item.context.transfer_carrier.carrier_class ==
               iotox::sync::SyncCarrierClass::auxiliary;
      }));
  auto changed_carrier = source_a_context;
  changed_carrier.transfer_carrier.worker_id = 999U;
  const auto frozen_binding = subscriber_service.bind_source_carrier(
      head_request.value().frame.message_id, changed_carrier);
  IOTOX_CHECK(!frozen_binding.ok() &&
              frozen_binding.code() == iotox::ErrorCode::unavailable);
  std::deque<iotox::sync::SyncContentDispatch> work(
      initial.value().begin(), initial.value().end());
  std::uint64_t objects_a = 0U;
  std::uint64_t objects_b = 0U;
  std::uint64_t availability_a = 0U;
  std::uint64_t availability_b = 0U;
  bool source_add_retry_exercised = false;
  for (std::size_t step = 0U; step < 4096U && !work.empty(); ++step) {
    const iotox::sync::SyncContentDispatch dispatch = work.front();
    work.pop_front();
    const bool from_a = dispatch.context.transfer_carrier ==
                        source_a_context.transfer_carrier;
    auto &publisher = from_a ? publisher_a : publisher_b;
    const auto &subscriber_context =
        from_a ? subscriber_a_context : subscriber_b_context;
    if (dispatch.frame.type ==
        iotox::protocol::MessageType::sync_content_availability_request) {
      auto served = publisher.handle_availability(subscriber_context,
                                                  dispatch.frame);
      IOTOX_CHECK_MSG(served.ok(), served.status().message());
      auto next = subscriber_service.handle_availability_result(
          dispatch.context, served.value().response);
      IOTOX_CHECK_MSG(next.ok(), next.status().message());
      work.insert(work.end(), next.value().begin(), next.value().end());
      if (from_a)
        ++availability_a;
      else
        ++availability_b;
      continue;
    }
    IOTOX_CHECK(dispatch.frame.type ==
                iotox::protocol::MessageType::sync_content_object_request);
    auto body = iotox::sync::decode_sync_content_object_request(
        dispatch.frame.payload);
    IOTOX_CHECK(body.ok());
    auto served = publisher.handle(subscriber_context, dispatch.frame);
    IOTOX_CHECK_MSG(served.ok(), served.status().message());
    IOTOX_CHECK(served.value().file_offered);
    IOTOX_CHECK(subscriber_service
                    .handle_object_result(dispatch.context,
                                          served.value().response)
                    .ok());
    auto offer = bridge.offer(body.value().transfer_id,
                              dispatch.context.transfer_carrier.friend_number);
    IOTOX_CHECK(offer.ok());
    auto admitted =
        subscriber_service.handle_offer(dispatch.context, offer.value());
    IOTOX_CHECK(admitted.ok() && admitted.value());
    auto terminal = bridge.terminal(offer.value().file_number,
                                    dispatch.context.transfer_carrier
                                        .friend_number);
    IOTOX_CHECK(terminal.ok());
    auto next = subscriber_service.handle_terminal(
        dispatch.context, terminal.value(),
        iotox::routes::WorkerTransferOutcome::completed,
        iotox::ErrorCode::ok);
    IOTOX_CHECK_MSG(next.ok(), next.status().message());
    if (!source_add_retry_exercised && next.value().size() == 2U &&
        std::all_of(next.value().begin(), next.value().end(),
                    [](const auto &item) {
                      return item.frame.type == iotox::protocol::MessageType::
                                                    sync_content_availability_request;
                    })) {
      // The owner-local mutation is retry-safe even if its first multi-frame
      // response was only partly sent: every pending exact request returns.
      auto retried_add = subscriber_service.add_source(
          head_request.value().frame.message_id, source_b_context);
      IOTOX_CHECK_MSG(retried_add.ok(), retried_add.status().message());
      IOTOX_CHECK(retried_add.value().size() == next.value().size());
      work.insert(work.end(), retried_add.value().begin(),
                  retried_add.value().end());
      source_add_retry_exercised = true;
    } else {
      work.insert(work.end(), next.value().begin(), next.value().end());
    }
    if (from_a)
      ++objects_a;
    else
      ++objects_b;
  }
  IOTOX_CHECK(work.empty());
  IOTOX_CHECK(source_add_retry_exercised);
  const auto snapshots = subscriber_service.snapshot();
  IOTOX_CHECK(snapshots.size() == 1U);
  IOTOX_CHECK(snapshots.front().state ==
              iotox::sync::SyncContentPullState::complete);
  IOTOX_CHECK(snapshots.front().sources == 2U);
  IOTOX_CHECK(snapshots.front().primary_source_carrier ==
              source_a_context.transfer_carrier);
  IOTOX_CHECK(snapshots.front().source_carriers.size() == 2U);
  IOTOX_CHECK(snapshots.front().source_carriers[0].source_id ==
              head_request.value().frame.message_id);
  IOTOX_CHECK(snapshots.front().source_carriers[0].stable_principal ==
              source_a_context.peer_authority.remote_principal);
  IOTOX_CHECK(snapshots.front().source_carriers[0].authority_route_key ==
              source_a_context.authority_route_key);
  IOTOX_CHECK(snapshots.front().source_carriers[0].transfer_carrier ==
              source_a_context.transfer_carrier);
  IOTOX_CHECK(snapshots.front().source_carriers[1].stable_principal ==
              source_b_context.peer_authority.remote_principal);
  IOTOX_CHECK(snapshots.front().source_carriers[1].authority_route_key ==
              source_b_context.authority_route_key);
  IOTOX_CHECK(snapshots.front().source_carriers[1].transfer_carrier ==
              source_b_context.transfer_carrier);
  IOTOX_CHECK(snapshots.front().source_carriers[0].requested_objects ==
              objects_a);
  IOTOX_CHECK(snapshots.front().source_carriers[0].committed_objects ==
              objects_a);
  IOTOX_CHECK(snapshots.front().source_carriers[0].fetched_bytes > 0U);
  IOTOX_CHECK(snapshots.front().source_carriers[1].requested_objects ==
              objects_b);
  IOTOX_CHECK(snapshots.front().source_carriers[1].committed_objects ==
              objects_b);
  IOTOX_CHECK(snapshots.front().source_carriers[1].fetched_bytes > 0U);
  if (same_principal) {
    IOTOX_CHECK(snapshots.front().source_carriers[0].stable_principal ==
                snapshots.front().source_carriers[1].stable_principal);
    IOTOX_CHECK(snapshots.front().source_carriers[0].authority_route_key ==
                snapshots.front().source_carriers[1].authority_route_key);
    IOTOX_CHECK(snapshots.front().source_carriers[0].friend_number ==
                snapshots.front().source_carriers[1].friend_number);
    IOTOX_CHECK(snapshots.front().source_carriers[0]
                    .transfer_carrier.friend_number ==
                snapshots.front().source_carriers[1]
                    .transfer_carrier.friend_number);
    IOTOX_CHECK(snapshots.front().source_carriers[0].transfer_carrier !=
                snapshots.front().source_carriers[1].transfer_carrier);
  }
  IOTOX_CHECK(snapshots.front().availability_requests ==
              snapshots.front().availability_results);
  IOTOX_CHECK(objects_a > 0U && objects_b > 0U);
  IOTOX_CHECK(availability_a > 0U && availability_b > 0U);

  const auto local_artifact =
      iotox::sync::sync_content_object_path(local, head.artifact);
  auto expected_digest = iotox::sync::hash_sync_file_sha256(source);
  auto observed_digest =
      iotox::sync::hash_sync_file_sha256(local_artifact);
  IOTOX_CHECK(expected_digest.ok() && observed_digest.ok());
  IOTOX_CHECK(expected_digest.value() == observed_digest.value());
  iotox::sync::AcceptedHeadStore accepted(local.root);
  auto accepted_head = accepted.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(accepted_head.ok() && accepted_head.value());
  IOTOX_CHECK(accepted_head.value()->record ==
              published_a.value().publication.record);
}

IOTOX_TEST(
    "content subscriber converges from two complementary authenticated sources") {
  run_complementary_auxiliary_sources(false);
}

IOTOX_TEST(
    "content subscriber distributes one principal over two exact auxiliary paths") {
  run_complementary_auxiliary_sources(true);
}

IOTOX_TEST("content subscriber fails closed on its exact auxiliary carrier loss") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto local = policy(temporary.path() / "local",
                            publisher.public_key(), subscriber.public_key());
  iotox::sync::NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace({local}).ok());
  TransferBridge bridge;
  std::uint64_t next_message = 41U;
  std::uint64_t next_file_id = 91U;
  iotox::sync::SyncContentSubscriberService service(
      registry, subscriber_seams(bridge, next_message, next_file_id),
      subscriber_config(subscriber, crypto));
  const auto primary = context(
      publisher.public_key(), iotox::security::Capability::sync_publish,
      7U, 11U);
  const auto auxiliary_a =
      auxiliary_context(primary, 0xC1U, 301U, 72U, 41U);
  const auto auxiliary_b =
      auxiliary_context(primary, 0xC2U, 302U, 73U, 42U);
  auto head = service.begin_pull(primary, local.id);
  IOTOX_CHECK_MSG(head.ok(), head.status().message());
  IOTOX_CHECK(service.bind_source_carrier(
                         head.value().frame.message_id, auxiliary_a)
                  .ok());
  auto added = service.add_source(
      head.value().frame.message_id, auxiliary_b);
  IOTOX_CHECK_MSG(added.ok() && added.value().empty(),
                  added.status().message());
  auto snapshots = service.snapshot();
  IOTOX_CHECK(snapshots.size() == 1U);
  IOTOX_CHECK(snapshots.front().sources == 2U);
  IOTOX_CHECK(snapshots.front().source_carriers.size() == 2U);
  IOTOX_CHECK(snapshots.front().source_carriers[0].stable_principal ==
              snapshots.front().source_carriers[1].stable_principal);
  IOTOX_CHECK(snapshots.front().source_carriers[0].authority_route_key ==
              snapshots.front().source_carriers[1].authority_route_key);
  auto unrelated = auxiliary_b.transfer_carrier;
  unrelated.worker_id += 1U;
  service.carrier_offline(unrelated);
  snapshots = service.snapshot();
  IOTOX_CHECK(snapshots.size() == 1U);
  IOTOX_CHECK(snapshots.front().state ==
              iotox::sync::SyncContentPullState::awaiting_head);
  service.carrier_offline(auxiliary_b.transfer_carrier);
  snapshots = service.snapshot();
  IOTOX_CHECK(snapshots.front().state ==
              iotox::sync::SyncContentPullState::failed);
  IOTOX_CHECK(snapshots.front().detail ==
              "exact auxiliary content carrier went offline");
}

IOTOX_TEST("content subscriber cancels an early offer before file effect") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto publisher = identity(temporary.path() / "publisher.identity", crypto);
  auto subscriber = identity(temporary.path() / "subscriber.identity", crypto);
  const auto remote = policy(temporary.path() / "remote",
                             publisher.public_key(), subscriber.public_key());
  const auto local = policy(temporary.path() / "local", publisher.public_key(),
                            subscriber.public_key());
  const auto source = temporary.path() / "source.bin";
  write_pattern(source, 64U * 1024U);
  iotox::sync::SignedHeadStore remote_heads(remote.root);
  auto published = iotox::sync::publish_local_content_revision(
      remote, source, publisher, crypto, remote_heads, publication_config());
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  const iotox::sync::SignedHead head = published.value().publication.head;
  iotox::sync::NamespaceRegistry remote_registry;
  iotox::sync::NamespaceRegistry local_registry;
  IOTOX_CHECK(remote_registry.replace({remote}).ok());
  IOTOX_CHECK(local_registry.replace({local}).ok());
  TransferBridge bridge;
  std::uint64_t publisher_message = 8000U;
  iotox::sync::SyncContentPublisherSeams publisher_seams;
  publisher_seams.load_head = [&head](const auto &) {
    return iotox::Result<std::optional<iotox::sync::SignedHead>>{
        std::optional<iotox::sync::SignedHead>{head}};
  };
  publisher_seams.head_record_digest = [&crypto](const auto &candidate) {
    return iotox::sync::signed_head_record_digest(candidate, crypto);
  };
  publisher_seams.resolve_object = [](const auto &configured,
                                      const auto &candidate, auto kind,
                                      std::uint64_t index) {
    return iotox::sync::resolve_sync_content_object(configured, candidate, kind,
                                                    index);
  };
  publisher_seams.send_object = [&bridge](const auto &carrier, const auto &path,
                                          const auto &file_id) {
    return bridge.send(carrier, path, file_id);
  };
  publisher_seams.make_message_id =
      [&publisher_message]() -> iotox::Result<std::uint64_t> {
    return publisher_message++;
  };
  iotox::sync::SyncContentPublisherService publisher_service(
      remote_registry, std::move(publisher_seams));
  std::uint64_t subscriber_message = 200U;
  std::uint64_t subscriber_file_id = 50U;
  iotox::sync::SyncContentSubscriberService subscriber_service(
      local_registry,
      subscriber_seams(bridge, subscriber_message, subscriber_file_id),
      subscriber_config(subscriber, crypto));
  const auto publisher_context = context(
      publisher.public_key(), iotox::security::Capability::sync_publish);
  const auto subscriber_context = context(
      subscriber.public_key(), iotox::security::Capability::sync_subscribe);
  auto head_request =
      subscriber_service.begin_pull(publisher_context, local.id);
  IOTOX_CHECK(head_request.ok());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head}, 9100U,
      head_request.value().frame.message_id);
  IOTOX_CHECK(head_result.ok());
  auto requests = subscriber_service.handle_head_result(publisher_context,
                                                        head_result.value());
  IOTOX_CHECK(requests.ok() && requests.value().size() == 1U);
  auto request_body = iotox::sync::decode_sync_content_object_request(
      requests.value().front().frame.payload);
  IOTOX_CHECK(request_body.ok());
  auto served =
      publisher_service.handle(subscriber_context,
                               requests.value().front().frame);
  IOTOX_CHECK(served.ok() && served.value().file_offered);
  auto offer = bridge.offer(request_body.value().transfer_id,
                            publisher_context.friend_number);
  IOTOX_CHECK(offer.ok());
  auto retained =
      subscriber_service.handle_offer(publisher_context, offer.value());
  IOTOX_CHECK(retained.ok() && retained.value());
  IOTOX_CHECK(bridge.receive_count() == 0U);
  IOTOX_CHECK(
      subscriber_service.cancel_pull(head_request.value().frame.message_id)
          .ok());
  IOTOX_CHECK(bridge.receive_count() == 0U && bridge.cancel_count() == 1U);
  const auto snapshots = subscriber_service.snapshot();
  IOTOX_CHECK(snapshots.size() == 1U);
  IOTOX_CHECK(snapshots.front().state ==
              iotox::sync::SyncContentPullState::cancelled);
  iotox::sync::AcceptedHeadStore accepted(local.root);
  auto absent = accepted.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(absent.ok() && !absent.value());
  iotox::sync::SyncContentAttemptStore attempts(
      local.root,
      {static_cast<std::size_t>(local.quotas.maximum_outstanding_requests)});
  auto journal = attempts.load(local, subscriber.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
  IOTOX_CHECK(journal.value().high_attempt_id == 1U);
  IOTOX_CHECK(
      subscriber_service
          .handle_object_result(publisher_context, served.value().response)
          .code() == iotox::ErrorCode::not_found);
}
