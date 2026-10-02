#pragma once

#include "iotox/file_transfer.hpp"
#include "iotox/route_inventory.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/sync_authorization.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_wire.hpp"

#include <cstddef>
#include <cstdint>
#include <deque>
#include <filesystem>
#include <functional>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

enum class SyncCarrierClass : std::uint8_t {
  primary = 1U,
  auxiliary = 2U,
};

// Transport identity for immutable-object negotiation and file bytes. It is
// deliberately separate from the primary authority session below: an
// auxiliary route may carry bytes but can never become the authorization
// principal merely by being selected as a carrier.
struct SyncTransferCarrier {
  SyncCarrierClass carrier_class{SyncCarrierClass::primary};
  routes::ToxPublicKey route_key{};
  std::uint64_t worker_id{0U};
  std::uint32_t friend_number{0U};
  std::uint64_t online_epoch{0U};
  std::uint64_t remote_route_generation{0U};
  routes::ToxPublicKey remote_coordinator_route_key{};
  std::uint64_t primary_authority_online_epoch{0U};

  [[nodiscard]] bool operator==(const SyncTransferCarrier &) const = default;
};

struct SyncPeerContext {
  // The primary session is the only authority and signed-HEAD lane.
  std::uint32_t friend_number{0U};
  std::uint64_t online_epoch{0U};
  routes::ToxPublicKey authority_route_key{};
  security::AuthoritySnapshot authority;
  security::PeerAuthoritySnapshot peer_authority;
  // Object request/result records and their exact FileId transfer use this
  // independently fenced carrier. Primary operation names the primary
  // session here; multi-route operation names an authenticated bulk worker.
  SyncTransferCarrier transfer_carrier;
  bool range_transfer_negotiated{false};
  bool content_transfer_negotiated{false};
  bool tree_transfer_negotiated{false};
  bool tree_checkpoint_negotiated{false};
};

[[nodiscard]] Status validate_sync_peer_context(
    const SyncPeerContext &context);

struct SyncPublisherSeams {
  std::function<Result<std::optional<SignedHead>>(const NamespacePolicy &policy)> load_head;
  std::function<Result<Digest>(const SignedHead &head)> head_record_digest;
  std::function<Status(const NamespacePolicy &policy, const SyncObjectRecord &object)>
      verify_object;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier, const std::filesystem::path &path,
      const FileId &file_id)>
      send_object;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier, const std::filesystem::path &path,
      std::span<const FileByteRange> ranges, const FileId &file_id)>
      send_ranges;
  std::function<Result<std::uint64_t>()> make_message_id;
};

struct SyncPublisherResult {
  protocol::Frame response;
  SyncAuthorizationDecision authorization{SyncAuthorizationDecision::invalid_operation};
  bool replayed{false};
  bool file_offered{false};
};

struct SyncPublisherSnapshot {
  std::size_t retained_replays{0U};
  std::uint64_t head_requests{0U};
  std::uint64_t object_requests{0U};
  std::uint64_t range_requests{0U};
  std::uint64_t denials{0U};
  std::uint64_t replay_hits{0U};
  std::uint64_t replay_conflicts{0U};
  std::uint64_t replay_evictions{0U};
  std::uint64_t file_offers{0U};
  std::uint64_t range_file_offers{0U};
  std::uint64_t range_bytes_offered{0U};
};

// Publisher-side request admission for the first Agent sync slice. Every
// effect is evaluated against the caller-supplied exact v3 authority snapshot.
// Replay retention is a bounded FIFO exact-replay window. Requests retained in
// the window replay their exact result; an older request is admitted as fresh
// read-only work and is re-authorized against the current session and HEAD.
class SyncPublisherService {
public:
  struct Config {
    std::size_t maximum_replays{256U};
  };

  SyncPublisherService(const NamespaceRegistry &namespaces, SyncPublisherSeams seams);
  SyncPublisherService(const NamespaceRegistry &namespaces, SyncPublisherSeams seams,
                       Config config);

  SyncPublisherService(const SyncPublisherService &) = delete;
  SyncPublisherService &operator=(const SyncPublisherService &) = delete;

  [[nodiscard]] Result<SyncPublisherResult> handle(const SyncPeerContext &context,
                                                   const protocol::Frame &request);
  void peer_offline(std::uint32_t friend_number, std::uint64_t online_epoch);
  void carrier_offline(const SyncTransferCarrier &carrier);
  // Replay-cache retention is distinct from transfer lifetime. An additive
  // namespace membership change may retire these entries while its caller
  // holds the Agent authority/effect fence; a repeated request is then
  // re-authorized against the successor policy. This neither cancels a
  // transfer nor acts as a revocation/drain primitive.
  [[nodiscard]] std::size_t
  retire_namespace_replays_for_additive_share(std::string_view namespace_id);
  [[nodiscard]] SyncPublisherSnapshot snapshot() const;
  // Status/telemetry callers must not wait behind filesystem verification or
  // a c-toxcore file-offer effect retained under the replay mutex. Absence is
  // an explicit busy observation; callers may still report independent worker
  // queue counters without perturbing the active operation.
  [[nodiscard]] std::optional<SyncPublisherSnapshot> try_snapshot() const;

private:
  struct PendingOffer {
    SyncTransferCarrier carrier;
    std::filesystem::path path;
    FileId file_id{};
    std::vector<FileByteRange> ranges;
    protocol::Frame failure_response;
  };

  struct ReplayEntry {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    SyncTransferCarrier carrier;
    std::uint64_t message_id{0U};
    security::AuthorityLedgerFormat authority_format{security::AuthorityLedgerFormat::v1};
    std::uint64_t authority_epoch{0U};
    std::uint64_t authority_sequence{0U};
    security::Digest authority_tail{};
    security::SigningPublicKey remote_principal{};
    std::uint64_t remote_capabilities{0U};
    std::string namespace_id;
    std::vector<std::uint8_t> request;
    SyncPublisherResult result;
  };

  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Result<SyncPublisherResult> handle_head(const SyncPeerContext &context,
                                                        const protocol::Frame &request);
  [[nodiscard]] Result<SyncPublisherResult>
  handle_object(const SyncPeerContext &context, const protocol::Frame &request,
                std::optional<PendingOffer> &pending_offer);
  [[nodiscard]] Result<SyncPublisherResult>
  handle_range(const SyncPeerContext &context, const protocol::Frame &request,
               std::optional<PendingOffer> &pending_offer);
  [[nodiscard]] Result<std::uint64_t> next_message_id() const;

  const NamespaceRegistry *namespaces_{nullptr};
  SyncPublisherSeams seams_;
  Config config_;
  mutable std::mutex mutex_;
  std::deque<ReplayEntry> replays_;
  SyncPublisherSnapshot statistics_;
};

} // namespace iotox::sync
