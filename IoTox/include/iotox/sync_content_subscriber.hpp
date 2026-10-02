#pragma once

#include "iotox/route_worker.hpp"
#include "iotox/sync_content_acceptance.hpp"
#include "iotox/sync_content_attempt_store.hpp"
#include "iotox/sync_content_service.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

enum class SyncContentPullState : std::uint8_t {
  awaiting_head = 1U,
  awaiting_objects = 2U,
  complete = 3U,
  failed = 4U,
  cancelled = 5U,
};

// Bounded owner-local evidence for one registered content source. Authority
// and transfer identities remain separate even when the transfer carrier is
// the primary session; routed multi-source qualification must be able to bind
// every source rather than only the HEAD source.
struct SyncContentSourceSnapshot {
  std::uint64_t source_id{0U};
  std::uint32_t friend_number{0U};
  std::uint64_t online_epoch{0U};
  security::SigningPublicKey stable_principal{};
  routes::ToxPublicKey authority_route_key{};
  SyncTransferCarrier transfer_carrier;
  std::uint64_t requested_objects{0U};
  std::uint64_t committed_objects{0U};
  std::uint64_t fetched_bytes{0U};
};

// One owner-private, content-free binding for an active immutable-object
// receive. Multiple records may belong to the same source and exact carrier;
// request/FileId identity keeps their transport and durable effects separate.
struct SyncContentLaneSnapshot {
  std::uint64_t request_id{0U};
  std::uint64_t source_id{0U};
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  std::uint64_t logical_index{0U};
  std::uint64_t object_bytes{0U};
  FileId file_id{};
  std::optional<std::uint32_t> file_number;
  SyncTransferCarrier transfer_carrier;
  bool root_manifest{false};
  bool transport_admitted{false};
};

struct SyncContentPullSnapshot {
  std::uint64_t job_id{0U};
  std::uint32_t friend_number{0U};
  std::uint64_t online_epoch{0U};
  std::string namespace_id;
  SyncContentPullState state{SyncContentPullState::awaiting_head};
  std::uint64_t head_generation{0U};
  Digest head_record{};
  SyncContentPhase phase{SyncContentPhase::unprepared};
  std::uint64_t requested_objects{0U};
  std::uint64_t committed_objects{0U};
  std::uint64_t reused_objects{0U};
  std::uint64_t fetched_bytes{0U};
  std::uint32_t sources{0U};
  SyncTransferCarrier primary_source_carrier;
  std::vector<SyncContentSourceSnapshot> source_carriers;
  std::uint64_t availability_requests{0U};
  std::uint64_t availability_results{0U};
  std::uint32_t active_lanes{0U};
  std::vector<SyncContentLaneSnapshot> lane_bindings;
  // Compatibility projection for the unambiguous zero/one-lane case. A
  // multi-lane job exposes every exact binding above and leaves these empty.
  std::optional<FileId> active_file_id;
  std::optional<std::uint32_t> active_file_number;
  std::string detail;
};

struct SyncContentDispatch {
  SyncPeerContext context;
  protocol::Frame frame;
};

struct SyncContentSubscriberSeams {
  std::function<Result<std::uint64_t>()> make_message_id;
  std::function<Result<FileId>()> make_file_id;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier, std::uint32_t file_number,
      const std::filesystem::path &destination)>
      receive_to_path;
  std::function<Status(const SyncTransferCarrier &carrier,
                       std::uint32_t file_number)>
      cancel_transfer;
  std::function<Status(const SyncTransferCarrier &carrier,
                       std::uint32_t file_number)>
      retire_transfer;
};

// Content-v2 subscriber: one frozen authoritative HEAD, an explicitly bounded
// set of independently authenticated sources, exact sparse availability, one
// request at a time, CTA1 before every file effect, root-manifest bootstrap,
// bounded reconstruction, whole-artifact CAS commit, and accepted HEAD last.
// A source-path record may bind its object/availability lane to one exact
// authenticated auxiliary worker before HEAD admission. Multiple records may
// retain the same stable principal and primary authority session when every
// transfer carrier is distinct. The primary session remains the only HEAD and
// authority lane, and every binding freezes with the HEAD.
class SyncContentSubscriberService final {
public:
  struct Config {
    std::size_t maximum_jobs{4U};
    // Process ceiling for simultaneous page/chunk receives in one job. One is
    // the conservative default; namespace maximum-lanes and outstanding-
    // request quotas may only tighten it. The root manifest remains serial.
    std::size_t maximum_lanes{1U};
    SyncContentConfig content;
    SyncContentAcceptanceConfig acceptance;
    const security::DeviceIdentity *identity{nullptr};
    const security::Sodium *sodium{nullptr};
    std::function<Result<std::shared_ptr<SyncGuardedStateWitness>>(
        const NamespacePolicy &policy)>
        guarded_state_witness;
  };

  SyncContentSubscriberService(const NamespaceRegistry &namespaces,
                               SyncContentSubscriberSeams seams, Config config);
  ~SyncContentSubscriberService();
  SyncContentSubscriberService(const SyncContentSubscriberService &) = delete;
  SyncContentSubscriberService &
  operator=(const SyncContentSubscriberService &) = delete;

  [[nodiscard]] Result<SyncContentDispatch>
  begin_pull(const SyncPeerContext &context, std::string_view namespace_id);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  retry_pull(const SyncPeerContext &context, std::string_view namespace_id);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  handle_head_result(const SyncPeerContext &context,
                     const protocol::Frame &frame);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  add_source(std::uint64_t job_id, const SyncPeerContext &context);
  [[nodiscard]] Status bind_source_carrier(
      std::uint64_t job_id, const SyncPeerContext &context);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  handle_availability_result(const SyncPeerContext &context,
                             const protocol::Frame &frame);
  [[nodiscard]] Status handle_object_result(const SyncPeerContext &context,
                                            const protocol::Frame &frame);
  [[nodiscard]] Result<bool> handle_offer(const SyncPeerContext &context,
                                          const FileTransferRecord &offer);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  handle_terminal(const SyncPeerContext &context,
                  const FileTransferRecord &transfer,
                  routes::WorkerTransferOutcome outcome, ErrorCode failure);
  [[nodiscard]] Status cancel_pull(std::uint64_t job_id);
  void peer_offline(std::uint32_t friend_number, std::uint64_t online_epoch);
  void carrier_offline(const SyncTransferCarrier &carrier);
  [[nodiscard]] std::vector<SyncContentPullSnapshot> snapshot() const;

private:
  enum class LaneTransportDisposition : std::uint8_t {
    none = 0U,
    cancel = 1U,
    retire = 2U,
  };
  struct Lane;
  struct PullJob;
  struct Source;

  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Status authorize_publish(const SyncPeerContext &context,
                                         const NamespacePolicy &policy) const;
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  prepare_after_head(PullJob &job);
  [[nodiscard]] Result<std::optional<SyncContentDispatch>>
  make_root_request(PullJob &job);
  [[nodiscard]] Status prepare_coordinator(PullJob &job);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>>
  request_availability(PullJob &job);
  [[nodiscard]] Result<std::vector<SyncContentDispatch>> drive(PullJob &job);
  [[nodiscard]] Source *source_for(PullJob &job,
                                   std::uint64_t source_id) noexcept;
  [[nodiscard]] std::uint16_t source_lane_limit(const PullJob &job) const;
  [[nodiscard]] Status admit_offer(PullJob &job, Lane &lane);
  [[nodiscard]] Status settle_lane(PullJob &job, std::size_t lane_index,
                                   LaneTransportDisposition transport,
                                   SyncContentFailure failure);
  [[nodiscard]] Status settle_all_lanes(
      PullJob &job, LaneTransportDisposition transport,
      SyncContentFailure failure,
      const std::optional<SyncTransferCarrier> &retired_carrier = {});
  void fail(PullJob &job, std::string detail) noexcept;

  const NamespaceRegistry *namespaces_{nullptr};
  SyncContentSubscriberSeams seams_;
  Config config_;
  mutable std::mutex mutex_;
  std::vector<std::unique_ptr<PullJob>> jobs_;
};

[[nodiscard]] std::string_view
sync_content_pull_state_name(SyncContentPullState state) noexcept;

} // namespace iotox::sync
