#pragma once

#include "iotox/sync_service.hpp"
#include "iotox/sync_reconstruction.hpp"
#include "iotox/sync_route_selector.hpp"
#include "iotox/sync_transfer.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

namespace iotox::sync {

enum class SyncPullState : std::uint8_t {
  awaiting_head = 1U,
  awaiting_objects = 2U,
  complete = 3U,
  failed = 4U,
  cancelled = 5U,
};

struct SyncPullSnapshot {
  // A process-local, non-zero identifier retained for the lifetime of this
  // bounded job tombstone. It is also the original HEAD-request message ID.
  std::uint64_t job_id{0U};
  std::uint32_t friend_number{0U};
  std::uint64_t online_epoch{0U};
  SyncTransferCarrier transfer_carrier;
  // Frozen when the pull is admitted. Agent loss handling consults this
  // value, never the process default, so a running job cannot be weakened by
  // a later configuration choice or an ambiguous retry.
  SyncRouteFailoverPolicy route_failover_policy{
      SyncRouteFailoverPolicy::available};
  SyncRouteClassConstraint route_class{
      SyncRouteClassConstraint::any};
  std::string namespace_id;
  SyncPullState state{SyncPullState::awaiting_head};
  std::uint64_t head_request_message_id{0U};
  std::uint64_t head_generation{0U};
  Digest head_record{};
  std::size_t requested_objects{0U};
  std::size_t admitted_offers{0U};
  std::size_t pending_offers{0U};
  std::uint64_t admission_retries{0U};
  std::uint64_t object_result_retries{0U};
  std::size_t committed_objects{0U};
  // Content-free process-local fence history. Terminal attempts remain until
  // this job retires so delayed transport events cannot target successors.
  std::size_t scheduler_attempts{0U};
  std::size_t scheduler_attempt_bound{0U};
  std::uint64_t retained_partials{0U};
  std::uint64_t retained_attempts{0U};
  std::uint64_t retained_bytes{0U};
  std::uint64_t retention_fallbacks{0U};
  std::uint64_t resumed_attempts{0U};
  std::uint64_t resumed_bytes{0U};
  std::uint64_t restart_resumed_attempts{0U};
  std::uint64_t restart_resumed_bytes{0U};
  // Process-local cleanup truth. A cancelled state is fenced immediately;
  // this becomes true only after every transport, staging, attempt, and
  // scheduler cleanup effect has settled successfully.
  bool cancellation_settled{false};
  // Process-local transfer bindings used by Agent to join an auxiliary
  // worker's byte progress back to this exact pull. They are intentionally
  // not rendered; only aggregate content-free counters cross local control.
  std::vector<FileId> transfer_file_ids;
  bool range_transfer{false};
  // Process-local range-lane truth. These fields let local qualification
  // distinguish the prerequisite manifest receive from the subsequently
  // admitted bounded range bundle without exposing object identities.
  bool range_lane_active{false};
  std::uint64_t range_attempt_id{0U};
  std::uint64_t range_message_id{0U};
  std::uint64_t range_bundle_bytes{0U};
  bool range_fallback{false};
  std::size_t range_retries{0U};
  std::uint64_t range_discarded_bytes{0U};
  std::uint64_t range_retained_bytes{0U};
  std::uint64_t range_resumed_bytes{0U};
  std::uint64_t range_restart_resumed_attempts{0U};
  std::uint64_t range_restart_resumed_bytes{0U};
  std::uint64_t range_restart_suffix_bytes{0U};
  std::uint64_t range_retention_fallbacks{0U};
  std::uint64_t range_reused_bytes{0U};
  std::uint64_t range_fetched_bytes{0U};
  std::size_t range_count{0U};
  std::string detail;
};

struct SyncSubscriberSeams {
  std::function<Result<std::uint64_t>()> make_message_id;
  std::function<Result<FileId>()> make_file_id;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier, std::uint32_t file_number,
      const std::filesystem::path &destination)> receive_to_path;
  std::function<Result<FileTransferRecord>(
      const SyncTransferCarrier &carrier, std::uint32_t file_number,
      const std::filesystem::path &destination,
      std::uint64_t resume_offset)> receive_to_path_from_offset;
  std::function<Status(const SyncTransferCarrier &carrier,
                       std::uint32_t file_number)> cancel_transfer;
  // Local-only, idempotent receive retirement for a carrier that is already
  // offline. It closes the transport-owned descriptor before namespace
  // staging is inspected or removed and sends no impossible remote control.
  std::function<Status(const SyncTransferCarrier &carrier,
                       std::uint32_t file_number)> retire_transfer;
  // Optional product capacity adapter. The subscriber still owns its local
  // two-object bound; Agent supplies these seams to debit the signed route
  // coordinator for auxiliary carriers.
  std::function<Status(const SyncTransferCarrier &carrier)> admit_carrier;
  std::function<Status(const SyncTransferCarrier &carrier)> release_carrier;
  std::function<Result<bool>(const SyncTransferCarrier &carrier)>
      carrier_already_released;
  SyncInstallSeams install;
};

// One-complete-source subscriber. It requests the signed HEAD, binds whole
// objects or one negotiated bounded range bundle to explicit FileIds, journals
// each target attempt before resume, commits verified objects, and accepts the
// HEAD last. It never activates a revision.
class SyncSubscriberService {
public:
  struct Config {
    std::size_t maximum_jobs{8U};
    std::size_t maximum_objects_per_job{2U};
    std::size_t maximum_object_result_retries{8U};
    std::size_t maximum_range_retries{1U};
    const security::DeviceIdentity *identity{nullptr};
    const security::Sodium *sodium{nullptr};
  };

  SyncSubscriberService(const NamespaceRegistry &namespaces,
                        SyncSubscriberSeams seams, Config config);
  ~SyncSubscriberService() noexcept;

  SyncSubscriberService(const SyncSubscriberService &) = delete;
  SyncSubscriberService &operator=(const SyncSubscriberService &) = delete;

  [[nodiscard]] Result<protocol::Frame>
  begin_pull(const SyncPeerContext &context, std::string_view namespace_id,
             SyncRouteFailoverPolicy route_failover_policy =
                 SyncRouteFailoverPolicy::available,
             SyncRouteClassConstraint route_class =
                 SyncRouteClassConstraint::any);
  // Returns the exact retained HEAD or still-unanswered object requests for
  // an active job. Publisher replay makes re-enqueue after local SENDQ
  // pressure idempotent within the online epoch.
  [[nodiscard]] Result<std::vector<protocol::Frame>>
  retry_pull(const SyncPeerContext &context, std::string_view namespace_id,
             SyncRouteFailoverPolicy route_failover_policy =
                 SyncRouteFailoverPolicy::available,
             SyncRouteClassConstraint route_class =
                 SyncRouteClassConstraint::any);
  [[nodiscard]] Result<std::vector<protocol::Frame>>
  handle_head_result(const SyncPeerContext &context,
                     const protocol::Frame &frame);
  [[nodiscard]] Result<std::vector<protocol::Frame>> handle_object_result(
      const SyncPeerContext &context, const protocol::Frame &frame);
  [[nodiscard]] Status handle_range_result(
      const SyncPeerContext &context, const protocol::Frame &frame);
  // Returns true only when the offer's exact FileId belongs to this service.
  [[nodiscard]] Result<bool> handle_offer(
      const SyncPeerContext &context, const FileTransferRecord &offer);
  [[nodiscard]] Result<std::vector<protocol::Frame>> handle_terminal(
      const SyncPeerContext &context, const FileTransferRecord &transfer,
      routes::WorkerTransferOutcome outcome, ErrorCode failure,
      std::string detail = {});
  // Cancellation is local and terminal. It fences the job before touching
  // transport state, then closes admitted receives, discards staging, and
  // finishes durable attempt records. Exact retries resume cleanup.
  [[nodiscard]] Status cancel_pull(std::uint64_t job_id);
  // Fence the existing object's exact route incarnation and allocate fresh
  // request/FileId/attempt identities on the replacement carrier. The
  // primary authority and retained signed HEAD remain unchanged.
  [[nodiscard]] Result<std::vector<protocol::Frame>>
  reassign_transfer_carrier(std::uint64_t job_id,
                            const SyncPeerContext &context);
  // Policy mutation is allowed only after this namespace has no live work or
  // unresolved cleanup. Terminal settled tombstones do not retain effects.
  [[nodiscard]] Status namespace_mutation_ready(
      std::string_view namespace_id) const;
  void peer_offline(std::uint32_t friend_number,
                    std::uint64_t online_epoch);
  [[nodiscard]] Status carrier_offline(
      const SyncTransferCarrier &carrier);
  [[nodiscard]] std::vector<SyncPullSnapshot> snapshot() const;

private:
  enum class RangeAttemptReason : std::uint8_t {
    initial = 1U,
    retry = 2U,
    carrier_reassignment = 3U,
  };
  struct ObjectLane;
  struct RangeLane;
  struct PullJob;

  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Status authorize_publish(
      const SyncPeerContext &context,
      const NamespacePolicy &policy) const;
  [[nodiscard]] Result<std::size_t> job_index(
      std::uint32_t friend_number, std::uint64_t online_epoch,
      std::string_view namespace_id) const;
  [[nodiscard]] Result<std::size_t> correlated_job_index(
      std::uint32_t friend_number, std::uint64_t online_epoch,
      std::uint64_t correlation_id) const;
  [[nodiscard]] Result<std::size_t> job_id_index(
      std::uint64_t job_id) const;
  [[nodiscard]] Status prepare_objects(
      PullJob &job, const SyncPeerContext &context,
      const SignedHead &head, const CandidateHead &candidate,
      const std::optional<AcceptedHead> &current);
  [[nodiscard]] Result<std::vector<protocol::Frame>>
  prepare_artifact_after_manifest(PullJob &job);
  [[nodiscard]] Result<protocol::Frame>
  prepare_range_attempt(
      PullJob &job, SyncRangePlan plan, std::size_t retry_count,
      RangeAttemptReason reason,
      std::optional<std::uint64_t> retained_attempt_id = {},
      std::uint64_t retained_bytes = 0U,
      std::optional<DurableSyncAttempt> restart_retained = {});
  [[nodiscard]] Status settle_range_cleanup(
      PullJob &job, bool cancel_transport = true,
      bool record_discarded_bytes = false);
  [[nodiscard]] Status settle_pending_offers(PullJob &job);
  [[nodiscard]] Status maybe_accept_head(
      PullJob &job, const SyncPeerContext &context);
  [[nodiscard]] Status settle_failed_cleanup(PullJob &job);
  void fail_job(PullJob &job, std::string detail) noexcept;

  const NamespaceRegistry *namespaces_{nullptr};
  SyncSubscriberSeams seams_;
  Config config_;
  mutable std::mutex mutex_;
  std::vector<std::unique_ptr<PullJob>> jobs_;
};

[[nodiscard]] std::string_view sync_pull_state_name(
    SyncPullState state) noexcept;

} // namespace iotox::sync
