#pragma once

#include "iotox/file_transfer.hpp"
#include "iotox/sync_content.hpp"
#include "iotox/sync_service.hpp"

#include <cstddef>
#include <cstdint>
#include <deque>
#include <filesystem>
#include <functional>
#include <mutex>
#include <optional>
#include <vector>

namespace iotox::sync {

struct SyncContentPublisherSeams {
  std::function<Result<std::optional<SignedHead>>(
      const NamespacePolicy &policy)> load_head;
  std::function<Result<Digest>(const SignedHead &head)> head_record_digest;
  std::function<Result<SyncContentObjectDescriptor>(
      const NamespacePolicy &policy, const SignedHead &head,
      SyncContentObjectKind kind, std::uint64_t logical_index)>
      resolve_object;
  std::function<Result<SyncContentAvailabilityDescriptor>(
      const NamespacePolicy &policy, const SignedHead &head,
      SyncContentObjectKind kind, std::uint64_t first_object,
      std::uint32_t object_count)>
      resolve_availability;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier,
      const std::filesystem::path &path, const FileId &file_id)>
      send_object;
  std::function<Result<std::uint64_t>()> make_message_id;
};

struct SyncContentPublisherResult {
  protocol::Frame response;
  SyncAuthorizationDecision authorization{
      SyncAuthorizationDecision::invalid_operation};
  bool replayed{false};
  bool file_offered{false};
};

struct SyncContentPublisherSnapshot {
  std::size_t retained_replays{0U};
  std::uint64_t object_requests{0U};
  std::uint64_t availability_requests{0U};
  std::uint64_t denials{0U};
  std::uint64_t replay_hits{0U};
  std::uint64_t replay_conflicts{0U};
  std::uint64_t replay_evictions{0U};
  std::uint64_t file_offers{0U};
};

class SyncContentPublisherService final {
public:
  struct Config {
    std::size_t maximum_replays{256U};
  };

  SyncContentPublisherService(const NamespaceRegistry &namespaces,
                              SyncContentPublisherSeams seams);
  SyncContentPublisherService(const NamespaceRegistry &namespaces,
                              SyncContentPublisherSeams seams,
                              Config config);
  SyncContentPublisherService(const SyncContentPublisherService &) = delete;
  SyncContentPublisherService &operator=(
      const SyncContentPublisherService &) = delete;

  [[nodiscard]] Result<SyncContentPublisherResult> handle(
      const SyncPeerContext &context, const protocol::Frame &request);
  [[nodiscard]] Result<SyncContentPublisherResult> handle_availability(
      const SyncPeerContext &context, const protocol::Frame &request);
  void peer_offline(std::uint32_t friend_number,
                    std::uint64_t online_epoch);
  void carrier_offline(const SyncTransferCarrier &carrier);
  [[nodiscard]] SyncContentPublisherSnapshot snapshot() const;
  [[nodiscard]] std::optional<SyncContentPublisherSnapshot>
  try_snapshot() const;

private:
  struct ReplayEntry {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    SyncTransferCarrier carrier;
    std::uint64_t message_id{0U};
    security::AuthorityLedgerFormat authority_format{
        security::AuthorityLedgerFormat::v1};
    std::uint64_t authority_epoch{0U};
    std::uint64_t authority_sequence{0U};
    security::Digest authority_tail{};
    security::SigningPublicKey remote_principal{};
    std::uint64_t remote_capabilities{0U};
    std::vector<std::uint8_t> request;
    SyncContentPublisherResult result;
  };

  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Result<std::uint64_t> next_message_id() const;

  const NamespaceRegistry *namespaces_{nullptr};
  SyncContentPublisherSeams seams_;
  Config config_;
  mutable std::mutex mutex_;
  std::deque<ReplayEntry> replays_;
  SyncContentPublisherSnapshot statistics_;
};

} // namespace iotox::sync
