#include "iotox/sync_subscriber.hpp"

#include "iotox/sync_guarded_witness.hpp"

#include "iotox/sync_manifest.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {

struct SyncSubscriberService::ObjectLane {
  SyncObjectRecord object;
  FileId file_id{};
  std::uint64_t request_message_id{0U};
  std::uint64_t attempt_id{0U};
  std::optional<std::uint32_t> file_number;
  std::optional<std::vector<std::uint8_t>> result_record;
  bool result_offered{false};
  bool transport_admitted{false};
  bool carrier_admission_lost{false};
  std::size_t result_retries{0U};
};

struct SyncSubscriberService::RangeLane {
  SyncRangePlan plan;
  FileId file_id{};
  std::uint64_t request_message_id{0U};
  std::uint64_t attempt_id{0U};
  std::uint64_t bundle_bytes{0U};
  std::uint64_t resume_offset{0U};
  std::filesystem::path staging_path;
  std::optional<std::uint32_t> file_number;
  std::optional<std::vector<std::uint8_t>> result_record;
  bool result_offered{false};
  bool offer_pending{false};
  bool transport_admitted{false};
  bool journal_active{false};
  bool committed{false};
  bool carrier_lost{false};
  bool restart_resumed{false};
  std::size_t retries{0U};
};

struct SyncSubscriberService::PullJob {
  SyncPullSnapshot status;
  NamespacePolicy policy;
  SyncPeerContext authority_context;
  SyncTransferCarrier carrier;
  protocol::Frame head_request;
  std::optional<std::vector<std::uint8_t>> head_result_record;
  std::optional<SignedHead> signed_head;
  std::optional<CandidateHead> candidate;
  Digest head_record{};
  std::vector<ObjectLane> lanes;
  std::optional<AcceptedHead> basis_head;
  std::optional<RangeLane> range_lane;
  bool range_mode{false};
  bool capacity_ready{true};
  std::uint16_t admitted_capacity{0U};
  std::unique_ptr<SyncAttemptStore> attempt_store;
  std::unique_ptr<SyncObjectScheduler> scheduler;
  std::unique_ptr<SyncTransferCoordinator> transfers;
  bool cancellation_settled{false};
  bool failed_cleanup_settled{true};
};

namespace {

bool same_authority(const SyncPeerContext &left,
                    const SyncPeerContext &right) noexcept {
  return left.friend_number == right.friend_number &&
         left.online_epoch == right.online_epoch &&
         left.authority_route_key == right.authority_route_key &&
         left.authority.format == right.authority.format &&
         left.authority.ownership_epoch == right.authority.ownership_epoch &&
         left.authority.sequence == right.authority.sequence &&
         left.authority.tail_digest == right.authority.tail_digest &&
         left.peer_authority.remote_principal ==
             right.peer_authority.remote_principal &&
         left.peer_authority.remote_capabilities ==
             right.peer_authority.remote_capabilities &&
         right.peer_authority.verifier_state ==
             security::AuthorityVerifierState::authorized &&
         right.peer_authority.remote_authorized;
}

SyncObjectRecord object_from_candidate(const CandidateHead &candidate,
                                       SyncObjectKind kind) {
  if (kind == SyncObjectKind::artifact)
    return {kind, candidate.artifact, candidate.artifact_bytes};
  return {kind, candidate.manifest, candidate.manifest_bytes};
}

class UniqueFd {
public:
  UniqueFd() = default;
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() {
    if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
  }
  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;
  UniqueFd(UniqueFd &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept {
    return descriptor_ >= 0;
  }

private:
  int descriptor_{-1};
};

Status errno_status(std::string_view operation,
                    const std::filesystem::path &path) {
  return Status{ErrorCode::io_error,
                std::string(operation) + " '" + path.string() + "': " +
                    std::strerror(errno)};
}

Result<UniqueFd> open_range_bundle(const std::filesystem::path &path,
                                   std::uint64_t expected_bytes) {
  UniqueFd descriptor(::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
  if (!descriptor) return errno_status("unable to open sync range bundle", path);
  struct stat metadata {};
  if (::fstat(descriptor.get(), &metadata) != 0) {
    return errno_status("unable to inspect sync range bundle", path);
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) || metadata.st_size < 0 ||
      static_cast<std::uint64_t>(metadata.st_size) != expected_bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync range bundle shape or size is invalid"};
  }
  return descriptor;
}

Result<std::size_t> read_range_bundle(
    int descriptor, const SyncRangePlan &plan, std::uint64_t target_offset,
    std::span<std::uint8_t> output) {
  if (output.empty()) return 0U;
  std::uint64_t bundle_offset = 0U;
  for (const SyncMissingRange &range : plan.missing_ranges) {
    if (target_offset < range.offset ||
        target_offset >= range.offset + range.length) {
      bundle_offset += range.length;
      continue;
    }
    const std::uint64_t within = target_offset - range.offset;
    if (output.size() > range.length - within ||
        bundle_offset >
            static_cast<std::uint64_t>(std::numeric_limits<off_t>::max()) -
                within) {
      return Status{ErrorCode::protocol_error,
                    "range reconstruction read escapes its bundle map"};
    }
    std::size_t done = 0U;
    while (done < output.size()) {
      const std::uint64_t absolute = bundle_offset + within + done;
      if (absolute >
          static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        return Status{ErrorCode::resource_exhausted,
                      "range bundle offset exceeds platform limits"};
      }
      const ssize_t count = ::pread(
          descriptor, output.data() + done, output.size() - done,
          static_cast<off_t>(absolute));
      if (count < 0) {
        if (errno == EINTR) continue;
        return Status{ErrorCode::io_error,
                      "unable to read sync range bundle: " +
                          std::string(std::strerror(errno))};
      }
      if (count == 0) {
        return Status{ErrorCode::protocol_error,
                      "sync range bundle ended before its requested bytes"};
      }
      done += static_cast<std::size_t>(count);
    }
    return done;
  }
  return Status{ErrorCode::protocol_error,
                "range reconstruction requested a reused target span"};
}

} // namespace

std::string_view sync_pull_state_name(SyncPullState state) noexcept {
  switch (state) {
  case SyncPullState::awaiting_head:
    return "awaiting-head";
  case SyncPullState::awaiting_objects:
    return "awaiting-objects";
  case SyncPullState::complete:
    return "complete";
  case SyncPullState::failed:
    return "failed";
  case SyncPullState::cancelled:
    return "cancelled";
  }
  return "unknown";
}

SyncSubscriberService::SyncSubscriberService(
    const NamespaceRegistry &namespaces, SyncSubscriberSeams seams,
    Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {
  if (config_.maximum_jobs > 0U && config_.maximum_jobs <= 1024U)
    jobs_.reserve(config_.maximum_jobs);
}

SyncSubscriberService::~SyncSubscriberService() noexcept {
  std::scoped_lock lock(mutex_);
  for (auto &job : jobs_) {
    static_cast<void>(settle_range_cleanup(*job));
    if (job->transfers) static_cast<void>(job->transfers->close());
    if (job->scheduler) static_cast<void>(job->scheduler->close());
  }
}

Status SyncSubscriberService::validate_config() const {
  if (namespaces_ == nullptr || !seams_.make_message_id ||
      !seams_.make_file_id || !seams_.receive_to_path ||
      !seams_.cancel_transfer || !seams_.retire_transfer ||
      !seams_.install.hash_file ||
      config_.identity == nullptr || config_.sodium == nullptr ||
      config_.maximum_jobs == 0U || config_.maximum_jobs > 1024U ||
      config_.maximum_objects_per_job != 2U ||
      config_.maximum_object_result_retries == 0U ||
      config_.maximum_object_result_retries > 64U ||
      config_.maximum_range_retries > 8U ||
      jobs_.capacity() < config_.maximum_jobs) {
    return Status{ErrorCode::invalid_argument,
                  "sync subscriber service configuration is invalid"};
  }
  return Status::success();
}

Status SyncSubscriberService::authorize_publish(
    const SyncPeerContext &context,
    const NamespacePolicy &policy) const {
  const Status context_valid = validate_sync_peer_context(context);
  if (!context_valid.ok()) return context_valid;
  const SyncAuthorizationResult authorized = evaluate_sync_authorization(
      SyncOperation::publish, policy, context.authority,
      context.peer_authority);
  if (!authorized.authorized()) {
    return Status{ErrorCode::unavailable,
                  "sync publisher authorization denied: " +
                      std::string(sync_authorization_decision_name(
                          authorized.decision))};
  }
  return Status::success();
}

Result<std::size_t> SyncSubscriberService::job_index(
    std::uint32_t friend_number, std::uint64_t online_epoch,
    std::string_view namespace_id) const {
  const auto found = std::find_if(
      jobs_.begin(), jobs_.end(),
      [friend_number, online_epoch, namespace_id](const auto &job) {
        return job->status.friend_number == friend_number &&
               job->status.online_epoch == online_epoch &&
               job->status.namespace_id == namespace_id;
      });
  if (found == jobs_.end())
    return Status{ErrorCode::not_found, "sync pull job is absent"};
  return static_cast<std::size_t>(found - jobs_.begin());
}

Result<std::size_t> SyncSubscriberService::correlated_job_index(
    std::uint32_t friend_number, std::uint64_t online_epoch,
    std::uint64_t correlation_id) const {
  const auto found = std::find_if(
      jobs_.begin(), jobs_.end(),
      [friend_number, online_epoch, correlation_id](const auto &job) {
        return job->status.friend_number == friend_number &&
               job->status.online_epoch == online_epoch &&
               job->head_request.message_id == correlation_id;
      });
  if (found == jobs_.end())
    return Status{ErrorCode::not_found,
                  "sync HEAD result has no current request"};
  return static_cast<std::size_t>(found - jobs_.begin());
}

Result<std::size_t> SyncSubscriberService::job_id_index(
    std::uint64_t job_id) const {
  if (job_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync pull job identifier zero is reserved"};
  }
  const auto found = std::find_if(
      jobs_.begin(), jobs_.end(), [job_id](const auto &job) {
        return job->status.job_id == job_id;
      });
  if (found == jobs_.end()) {
    return Status{ErrorCode::not_found, "sync pull job is absent"};
  }
  return static_cast<std::size_t>(found - jobs_.begin());
}

Result<protocol::Frame> SyncSubscriberService::begin_pull(
    const SyncPeerContext &context, std::string_view namespace_id,
    SyncRouteFailoverPolicy route_failover_policy,
    SyncRouteClassConstraint route_class) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  auto policy = namespaces_->resolve(namespace_id);
  if (!policy) return policy.status();
  if (policy.value().engine != Engine::range_v1 &&
      policy.value().engine != Engine::treepack_v1) {
    return Status{ErrorCode::unsupported,
                  "the Agent subscriber supports only range-v1 and treepack-v1 namespaces"};
  }
  const Status authorized = authorize_publish(context, policy.value());
  if (!authorized.ok()) return authorized;
  // A new authenticated epoch may supersede only terminal local truth. Fence
  // an unexpectedly retained active old epoch, settle failed cleanup, and
  // retire bounded tombstones before admitting new work for the same peer and
  // namespace.
  for (auto &retained : jobs_) {
    if (retained->status.friend_number != context.friend_number ||
        retained->status.namespace_id != namespace_id ||
        retained->status.online_epoch == context.online_epoch) {
      continue;
    }
    if (retained->status.state == SyncPullState::awaiting_head ||
        retained->status.state == SyncPullState::awaiting_objects) {
      fail_job(*retained,
               "new online epoch fenced the prior sync attempt");
    }
    if (retained->status.state == SyncPullState::failed &&
        !retained->failed_cleanup_settled) {
      const Status settled = settle_failed_cleanup(*retained);
      if (!settled.ok()) {
        return Status{ErrorCode::unavailable,
                      "prior sync pull cleanup is unresolved: " +
                          settled.message()};
      }
    }
    if (retained->status.state == SyncPullState::cancelled &&
        !retained->cancellation_settled) {
      return Status{ErrorCode::unavailable,
                    "prior sync pull cancellation requires a cleanup retry"};
    }
  }
  std::erase_if(jobs_, [&](const auto &retained) {
    if (retained->status.friend_number != context.friend_number ||
        retained->status.namespace_id != namespace_id ||
        retained->status.online_epoch == context.online_epoch) {
      return false;
    }
    return retained->status.state == SyncPullState::complete ||
           (retained->status.state == SyncPullState::failed &&
            retained->failed_cleanup_settled) ||
           (retained->status.state == SyncPullState::cancelled &&
            retained->cancellation_settled);
  });
  auto existing = job_index(context.friend_number, context.online_epoch,
                            namespace_id);
  if (existing) {
    PullJob &job = *jobs_[existing.value()];
    if (!same_authority(job.authority_context, context)) {
      return Status{ErrorCode::unavailable,
                    "sync publisher authority changed before retry"};
    }
    if (job.status.state == SyncPullState::awaiting_head ||
        job.status.state == SyncPullState::awaiting_objects) {
      if (job.status.route_failover_policy != route_failover_policy ||
          job.status.route_class != route_class) {
        return Status{
            ErrorCode::unavailable,
            "sync pull retry conflicts with its frozen route policy"};
      }
    }
    if (job.status.state == SyncPullState::awaiting_head) {
      return job.head_request;
    }
    if (job.status.state == SyncPullState::awaiting_objects) {
      return Status{ErrorCode::unavailable,
                    "sync pull already has active object requests"};
    }
    if (job.status.state == SyncPullState::cancelled &&
        !job.cancellation_settled) {
      return Status{ErrorCode::unavailable,
                    "sync pull cancellation requires a cleanup retry"};
    }
    if (job.status.state == SyncPullState::failed &&
        !job.failed_cleanup_settled) {
      const Status settled = settle_failed_cleanup(job);
      if (!settled.ok()) {
        return Status{ErrorCode::unavailable,
                      "sync pull failure cleanup is unresolved: " +
                          settled.message()};
      }
    }
    // Frozen routing intent belongs to one live pull, not to the namespace.
    // Once the prior job is terminal and cleanup is settled, preserve its
    // authority fence but allow the next signed revision to select a new
    // failover policy or route class.
    jobs_.erase(jobs_.begin() + static_cast<std::ptrdiff_t>(existing.value()));
  }
  if (jobs_.size() >= config_.maximum_jobs) {
    return Status{ErrorCode::resource_exhausted,
                  "sync subscriber job bound is exhausted"};
  }
  Result<std::uint64_t> message_id = Status{
      ErrorCode::unavailable,
      "unable to allocate a unique sync pull job identifier"};
  for (std::size_t attempt = 0U; attempt < 8U; ++attempt) {
    message_id = seams_.make_message_id();
    if (!message_id) return message_id.status();
    if (message_id.value() == 0U) {
      return Status{ErrorCode::protocol_error,
                    "sync message allocator returned zero"};
    }
    if (!job_id_index(message_id.value())) break;
    if (attempt == 7U) {
      return Status{ErrorCode::unavailable,
                    "unable to allocate a unique sync pull job identifier"};
    }
  }
  auto frame = make_sync_head_request_frame(
      {std::string(namespace_id)}, message_id.value());
  if (!frame) return frame.status();
  auto job = std::make_unique<PullJob>();
  job->status.job_id = message_id.value();
  job->status.friend_number = context.friend_number;
  job->status.online_epoch = context.online_epoch;
  job->status.transfer_carrier = context.transfer_carrier;
  job->status.route_failover_policy = route_failover_policy;
  job->status.route_class = route_class;
  job->status.namespace_id = std::string(namespace_id);
  job->status.head_request_message_id = message_id.value();
  job->status.detail = "signed HEAD requested";
  job->policy = std::move(policy).value();
  job->authority_context = context;
  job->carrier = context.transfer_carrier;
  job->head_request = frame.value();
  jobs_.push_back(std::move(job));
  return frame;
}

Result<std::vector<protocol::Frame>> SyncSubscriberService::retry_pull(
    const SyncPeerContext &context, std::string_view namespace_id,
    SyncRouteFailoverPolicy route_failover_policy,
    SyncRouteClassConstraint route_class) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  auto index = job_index(context.friend_number, context.online_epoch,
                         namespace_id);
  if (!index) return index.status();
  PullJob &job = *jobs_[index.value()];
  if (job.status.route_failover_policy != route_failover_policy ||
      job.status.route_class != route_class) {
    return Status{
        ErrorCode::unavailable,
        "sync pull retry conflicts with its frozen route policy"};
  }
  if (job.status.state == SyncPullState::cancelled) {
    return std::vector<protocol::Frame>{};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok()) return authorized;
  if (!same_authority(job.authority_context, context)) {
    return Status{ErrorCode::unavailable,
                  "sync publisher authority changed before retry"};
  }
  if (job.status.state == SyncPullState::awaiting_head) {
    return std::vector<protocol::Frame>{job.head_request};
  }
  if (job.status.state != SyncPullState::awaiting_objects) {
    return Status{ErrorCode::unavailable,
                  "sync pull is not retryable in its terminal state"};
  }
  std::vector<protocol::Frame> requests;
  requests.reserve(job.lanes.size());
  for (const ObjectLane &lane : job.lanes) {
    if (lane.result_record.has_value()) continue;
    auto request = make_sync_object_request_frame(
        {job.policy.id, lane.object.kind, job.head_record, lane.file_id},
        lane.request_message_id);
    if (!request) return request.status();
    requests.push_back(std::move(request).value());
  }
  if (job.range_lane && !job.range_lane->result_record) {
    if (job.range_lane->carrier_lost) {
      return Status{ErrorCode::unavailable,
                    "sync range is waiting for a replacement carrier"};
    }
    std::vector<SyncRangeRecord> ranges;
    ranges.reserve(job.range_lane->plan.missing_ranges.size());
    for (const SyncMissingRange &range :
         job.range_lane->plan.missing_ranges) {
      ranges.push_back({range.offset, range.length});
    }
    auto request = make_sync_range_request_frame(
        {job.policy.id, job.head_record, job.range_lane->file_id,
         std::move(ranges)},
        job.range_lane->request_message_id);
    if (!request) return request.status();
    requests.push_back(std::move(request).value());
  }
  return requests;
}

Status SyncSubscriberService::prepare_objects(
    PullJob &job, const SyncPeerContext &context,
    const SignedHead &head, const CandidateHead &candidate,
    const std::optional<AcceptedHead> &current) {
  if (head.writer != context.peer_authority.remote_principal) {
    return Status{ErrorCode::protocol_error,
                  "sync HEAD writer is not the proven remote publisher"};
  }
  job.carrier = context.transfer_carrier;
  job.status.transfer_carrier = context.transfer_carrier;
  auto record = signed_head_record_digest(head, *config_.sodium);
  if (!record) return record.status();
  job.head_record = record.value();
  job.status.head_record = record.value();
  job.signed_head = head;
  job.candidate = candidate;
  job.range_mode = job.policy.engine == Engine::range_v1 &&
                   context.range_transfer_negotiated && current.has_value();
  job.basis_head = job.range_mode ? current : std::nullopt;
  job.status.range_transfer = job.range_mode;

  SyncAttemptStore::Config attempt_config;
  attempt_config.maximum_active_attempts = static_cast<std::size_t>(
      job.policy.quotas.maximum_outstanding_requests);
  job.attempt_store = std::make_unique<SyncAttemptStore>(
      job.policy.root, attempt_config);
  {
    const std::array<SyncObjectRecord, 2U> candidate_objects{
        object_from_candidate(candidate, SyncObjectKind::artifact),
        object_from_candidate(candidate, SyncObjectKind::manifest)};
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    auto fenced = job.attempt_store->fence_retained_except(
        job.policy, candidate_objects, *config_.identity, *config_.sodium,
        transaction.value());
    if (!fenced) return fenced.status();
  }
  SyncObjectScheduler::CapacitySeams capacity;
  PullJob *stable_job = &job;
  capacity.admit = [stable_job, this](
                       const routes::ToxPublicKey &route,
                       std::uint64_t worker) {
    if (!stable_job->capacity_ready ||
        route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id ||
        stable_job->admitted_capacity >= 2U) {
      return Status{ErrorCode::resource_exhausted,
                    "primary sync capacity is unavailable"};
    }
    if (seams_.admit_carrier) {
      const Status admitted =
          seams_.admit_carrier(stable_job->carrier);
      if (!admitted.ok()) return admitted;
    }
    ++stable_job->admitted_capacity;
    return Status::success();
  };
  capacity.release = [stable_job, this](
                         const routes::ToxPublicKey &route,
                         std::uint64_t worker) {
    if (!stable_job->capacity_ready ||
        route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id ||
        stable_job->admitted_capacity == 0U) {
      return Status{ErrorCode::unavailable,
                    "primary sync capacity cannot be released"};
    }
    if (seams_.release_carrier) {
      const Status released =
          seams_.release_carrier(stable_job->carrier);
      if (!released.ok()) return released;
    }
    --stable_job->admitted_capacity;
    return Status::success();
  };
  capacity.already_released = [stable_job, this](
      const routes::ToxPublicKey &route,
      std::uint64_t worker) -> Result<bool> {
    if (route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id) {
      return false;
    }
    if (!stable_job->capacity_ready &&
        stable_job->admitted_capacity == 0U) {
      if (seams_.carrier_already_released) {
        return seams_.carrier_already_released(stable_job->carrier);
      }
      return true;
    }
    if (seams_.carrier_already_released) {
      return seams_.carrier_already_released(stable_job->carrier);
    }
    return false;
  };
  SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 2U;
  // Retained attempt tombstones are part of this pull's bounded request
  // history. Use the already validated host-local namespace ceiling instead
  // of a hidden four-record limit that can contradict the operator policy.
  scheduler_config.maximum_attempts = static_cast<std::size_t>(
      job.policy.quotas.maximum_outstanding_requests);
  scheduler_config.maximum_staging_bytes =
      job.policy.quotas.maximum_staging_bytes;
  scheduler_config.make_attempt_id = [stable_job, this]() {
    return stable_job->attempt_store->reserve_attempt_id(
        stable_job->policy, *config_.identity, *config_.sodium);
  };
  job.scheduler = std::make_unique<SyncObjectScheduler>(
      std::move(capacity), std::move(scheduler_config));

  SyncTransferCoordinator::Config transfer_config;
  transfer_config.policy = job.policy;
  transfer_config.maximum_bindings = 2U;
  transfer_config.maximum_events_per_service = 2U;
  transfer_config.attempt_store = job.attempt_store.get();
  transfer_config.identity = config_.identity;
  transfer_config.sodium = config_.sodium;
  transfer_config.seams.install = seams_.install;
  transfer_config.seams.receive_to_path = [this, stable_job](
      const routes::ToxPublicKey &route, std::uint64_t worker,
      std::uint32_t file_number,
      const std::filesystem::path &destination) {
    if (route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id) {
      return Result<FileTransferRecord>{Status{
          ErrorCode::protocol_error,
          "primary sync receive route changed before admission"}};
    }
    return seams_.receive_to_path(stable_job->carrier, file_number,
                                  destination);
  };
  if (seams_.receive_to_path_from_offset) {
    transfer_config.seams.receive_to_path_from_offset =
        [this, stable_job](
            const routes::ToxPublicKey &route, std::uint64_t worker,
            std::uint32_t file_number,
            const std::filesystem::path &destination,
            std::uint64_t resume_offset) {
          if (route != stable_job->carrier.route_key ||
              worker != stable_job->carrier.worker_id) {
            return Result<FileTransferRecord>{Status{
                ErrorCode::protocol_error,
                "primary sync resume route changed before admission"}};
          }
          return seams_.receive_to_path_from_offset(
              stable_job->carrier, file_number, destination,
              resume_offset);
        };
  }
  transfer_config.seams.cancel_transfer = [this, stable_job](
      const routes::ToxPublicKey &route, std::uint64_t worker,
      std::uint32_t file_number) {
    if (route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id) {
      return Status{ErrorCode::protocol_error,
                    "primary sync cancel route changed"};
    }
    return seams_.cancel_transfer(stable_job->carrier, file_number);
  };
  transfer_config.seams.retire_transfer = [this, stable_job](
      const routes::ToxPublicKey &route, std::uint64_t worker,
      std::uint32_t file_number) {
    if (route != stable_job->carrier.route_key ||
        worker != stable_job->carrier.worker_id) {
      return Status{ErrorCode::protocol_error,
                    "primary sync retirement route changed"};
    }
    return seams_.retire_transfer(stable_job->carrier, file_number);
  };
  job.transfers = std::make_unique<SyncTransferCoordinator>(
      *job.scheduler, std::move(transfer_config));

  const std::array<SyncObjectKind, 2U> whole_kinds{
      SyncObjectKind::artifact, SyncObjectKind::manifest};
  const std::array<SyncObjectKind, 1U> range_kinds{
      SyncObjectKind::manifest};
  const std::span<const SyncObjectKind> kinds = job.range_mode
      ? std::span<const SyncObjectKind>(range_kinds)
      : std::span<const SyncObjectKind>(whole_kinds);
  job.lanes.reserve(2U);
  for (const SyncObjectKind kind : kinds) {
    const SyncObjectRecord object = object_from_candidate(candidate, kind);
    const Status added = job.scheduler->add_object(object);
    if (!added.ok()) return added;

    // A failed earlier pull may have durably committed only one candidate
    // object. Every retry, including a range pull's manifest prerequisite,
    // proves and reuses that exact digest-named object instead of spending
    // another transport lane on bytes already in the immutable store. A
    // malformed existing object remains a hard error: repair/quarantine is
    // explicit and a pull never overwrites local truth.
    bool exists = false;
    {
      // Release this transaction before scheduler assignment: the scheduler
      // reserves its durable attempt id under the same non-recursive local
      // namespace lock.
      auto transaction = SyncNamespaceTransaction::acquire(job.policy);
      if (!transaction) return transaction.status();
      SyncInstallSeams install;
      install.hash_file = seams_.install.hash_file;
      const Status verified = verify_sync_object(
          job.policy, object, transaction.value(), install);
      if (verified.ok()) {
        exists = true;
        auto retained = job.attempt_store->retained_attempt(
            job.policy, object, config_.identity->public_key(),
            *config_.sodium, transaction.value());
        if (!retained) return retained.status();
        if (retained.value()) {
          const Status discarded = discard_sync_attempt_staging(
              job.policy, retained.value()->attempt_id,
              transaction.value());
          if (!discarded.ok()) return discarded;
          auto finished = job.attempt_store->finish(
              job.policy, *retained.value(), *config_.identity,
              *config_.sodium, transaction.value());
          if (!finished) return finished.status();
          if (!finished.value()) {
            return Status{
                ErrorCode::protocol_error,
                "restart-retained sync attempt disappeared during local reuse"};
          }
        }
      } else if (verified.code() != ErrorCode::not_found) {
        return verified;
      }
    }
    auto assigned = job.scheduler->assign(
        kind, object.identity, job.carrier.route_key,
        job.carrier.worker_id);
    if (!assigned) return assigned.status();
    if (exists) {
      const Status complete = job.scheduler->complete(
          assigned.value().attempt_id, object.identity, object.bytes);
      if (!complete.ok()) return complete;
      const Status committed = job.scheduler->commit(
          assigned.value().attempt_id);
      if (!committed.ok()) return committed;
      continue;
    }
    auto file_id = seams_.make_file_id();
    auto message_id = seams_.make_message_id();
    if (!file_id || !message_id || message_id.value() == 0U ||
        std::all_of(file_id.value().begin(), file_id.value().end(),
                    [](std::uint8_t byte) { return byte == 0U; })) {
      return !file_id ? file_id.status()
             : !message_id ? message_id.status()
                           : Status{ErrorCode::protocol_error,
                                    "sync object request allocator returned zero"};
    }
    ObjectLane lane;
    lane.object = object;
    lane.file_id = file_id.value();
    lane.request_message_id = message_id.value();
    lane.attempt_id = assigned.value().attempt_id;
    job.lanes.push_back(std::move(lane));
  }
  job.status.state = SyncPullState::awaiting_objects;
  job.status.head_generation = candidate.generation;
  job.status.requested_objects = job.lanes.size();
  if (job.range_mode) {
    job.status.detail = job.lanes.empty()
        ? "verified manifest reused locally; planning bounded range"
        : "manifest requested before range planning";
  } else if (job.lanes.size() == 2U) {
    job.status.detail = "artifact and manifest requested";
  } else if (job.lanes.size() == 1U) {
    job.status.detail =
        "one missing immutable object requested; one verified object reused locally";
  } else {
    job.status.detail = "candidate objects verified and reused locally";
  }
  return Status::success();
}

Result<std::vector<protocol::Frame>>
SyncSubscriberService::prepare_artifact_after_manifest(
    PullJob &job) {
  if (!job.range_mode || !job.candidate || !job.basis_head ||
      job.range_lane.has_value()) {
    return Status{ErrorCode::internal_error,
                  "sync range planning state is incomplete"};
  }
  const SyncObjectRecord target = object_from_candidate(
      *job.candidate, SyncObjectKind::artifact);
  const SyncObjectRecord manifest = object_from_candidate(
      *job.candidate, SyncObjectKind::manifest);
  const SyncObjectRecord basis{
      SyncObjectKind::artifact, job.basis_head->artifact,
      job.basis_head->artifact_bytes};
  SyncInstallSeams install;
  install.hash_file = seams_.install.hash_file;
  bool target_exists = false;
  bool whole_fallback = false;
  bool basis_fallback = false;
  std::optional<SyncRangePlan> planned;
  std::optional<DurableSyncAttempt> restart_retained;
  std::uint64_t restart_retained_bytes = 0U;

  // A previously committed but not-yet-accepted target object is the safest
  // reuse case: prove it now and advance scheduler truth without transport.
  // Release the namespace transaction before scheduler assignment: assigning
  // reserves a durable attempt id under its own transaction and local flock
  // locks are deliberately non-recursive.
  {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    const Status existing = verify_sync_object(
        job.policy, target, transaction.value(), install);
    if (existing.ok()) {
      target_exists = true;
    } else if (existing.code() != ErrorCode::not_found) {
      return existing;
    } else {
      // The manifest was just committed, so corruption there is candidate
      // failure. The accepted basis is only an optimization: if its exact
      // digest-named object is absent or corrupt, retain the signed accepted
      // state and fall back to the ordinary fully verified artifact path.
      const Status manifest_valid = verify_sync_object(
          job.policy, manifest, transaction.value(), install);
      if (!manifest_valid.ok()) return manifest_valid;
      const Status basis_valid = verify_sync_object(
          job.policy, basis, transaction.value(), install);
      basis_fallback =
          basis_valid.code() == ErrorCode::not_found ||
          basis_valid.code() == ErrorCode::protocol_error;
      if (!basis_valid.ok() && !basis_fallback) return basis_valid;
      if (basis_fallback) {
        whole_fallback = true;
      } else {
        auto plan = plan_sync_range_reconstruction(
            job.policy, target, manifest, basis, transaction.value(), install);
        whole_fallback =
            (!plan &&
             plan.status().code() == ErrorCode::resource_exhausted) ||
            (plan && plan.value().reused_bytes == 0U);
        if (!plan && !whole_fallback) return plan.status();
        if (plan && !whole_fallback) {
          planned.emplace(std::move(plan).value());
        }
      }
    }
  }

  {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    if (planned) {
      auto commitment = sync_range_plan_commitment(
          *planned, *config_.sodium);
      if (!commitment) return commitment.status();
      auto fenced = job.attempt_store->fence_retained_ranges_except(
          job.policy, target, commitment.value(), planned->missing_bytes,
          *config_.identity, *config_.sodium, transaction.value());
      if (!fenced) return fenced.status();
      auto retained = job.attempt_store->retained_range_attempt(
          job.policy, target, commitment.value(), planned->missing_bytes,
          config_.identity->public_key(), *config_.sodium,
          transaction.value());
      if (!retained) return retained.status();
      if (retained.value()) {
        auto partial = inspect_sync_attempt_partial(
            job.policy, retained.value()->attempt_id, target,
            transaction.value());
        if (!partial || partial.value().bytes == 0U ||
            partial.value().bytes >= planned->missing_bytes) {
          return !partial
              ? partial.status()
              : Status{ErrorCode::protocol_error,
                       "restart-retained range prefix has invalid size"};
        }
        restart_retained = *retained.value();
        restart_retained_bytes = partial.value().bytes;
      }
    } else {
      auto fenced = job.attempt_store->fence_retained_ranges_except(
          job.policy, target, Digest{}, 0U, *config_.identity,
          *config_.sodium, transaction.value());
      if (!fenced) return fenced.status();
    }
  }

  if (target_exists) {
    const Status added = job.scheduler->add_object(target);
    if (!added.ok()) return added;
    auto assigned = job.scheduler->assign(
        target.kind, target.identity, job.carrier.route_key,
        job.carrier.worker_id);
    if (!assigned) return assigned.status();
    const Status complete = job.scheduler->complete(
        assigned.value().attempt_id, target.identity, target.bytes);
    if (!complete.ok()) return complete;
    const Status committed = job.scheduler->commit(
        assigned.value().attempt_id);
    if (!committed.ok()) return committed;
    job.status.range_reused_bytes = target.bytes;
    job.status.range_fetched_bytes = 0U;
    job.status.range_count = 0U;
    job.status.detail =
        "target artifact already verified locally; no range transfer needed";
    return std::vector<protocol::Frame>{};
  }

  const Status added = job.scheduler->add_object(target);
  if (!added.ok()) return added;

  if (whole_fallback) {
    auto assigned = job.scheduler->assign(
        target.kind, target.identity, job.carrier.route_key,
        job.carrier.worker_id);
    if (!assigned) return assigned.status();
    auto file_id = seams_.make_file_id();
    auto message_id = seams_.make_message_id();
    if (!file_id || !message_id || message_id.value() == 0U ||
        std::all_of(file_id.value().begin(), file_id.value().end(),
                    [](std::uint8_t byte) { return byte == 0U; })) {
      return !file_id ? file_id.status()
             : !message_id ? message_id.status()
                           : Status{ErrorCode::protocol_error,
                                    "sync artifact fallback allocator returned zero"};
    }
    ObjectLane lane;
    lane.object = target;
    lane.file_id = file_id.value();
    lane.request_message_id = message_id.value();
    lane.attempt_id = assigned.value().attempt_id;
    job.lanes.push_back(std::move(lane));
    job.range_mode = false;
    job.status.range_transfer = false;
    job.status.range_fallback = true;
    ++job.status.requested_objects;
    job.status.detail = basis_fallback
        ? "accepted range basis absent or corrupt; whole artifact requested"
        : "range plan offered no bounded reuse; whole artifact requested";
    auto request = make_sync_object_request_frame(
        {job.policy.id, target.kind, job.head_record,
         job.lanes.back().file_id},
        job.lanes.back().request_message_id);
    if (!request) return request.status();
    return std::vector<protocol::Frame>{std::move(request).value()};
  }

  if (!planned) {
    return Status{ErrorCode::internal_error,
                  "sync range planner returned no reusable plan"};
  }
  job.status.range_reused_bytes = planned->reused_bytes;
  job.status.range_count = planned->missing_ranges.size();
  auto request = prepare_range_attempt(
      job, std::move(*planned), 0U, RangeAttemptReason::initial,
      restart_retained ? std::optional<std::uint64_t>{
                             restart_retained->attempt_id}
                       : std::nullopt,
      restart_retained_bytes, restart_retained);
  if (!request) return request.status();
  return std::vector<protocol::Frame>{std::move(request).value()};
}

Result<protocol::Frame> SyncSubscriberService::prepare_range_attempt(
    PullJob &job, SyncRangePlan plan, std::size_t retry_count,
    RangeAttemptReason reason,
    std::optional<std::uint64_t> retained_attempt_id,
    std::uint64_t retained_bytes,
    std::optional<DurableSyncAttempt> restart_retained) {
  if (job.range_lane ||
      (reason == RangeAttemptReason::retry && retry_count == 0U) ||
      (reason == RangeAttemptReason::initial && retry_count != 0U) ||
      retry_count > config_.maximum_range_retries ||
      plan.missing_ranges.empty() || plan.missing_bytes == 0U ||
      (retained_attempt_id.has_value() != (retained_bytes != 0U)) ||
      (restart_retained.has_value() &&
       (!retained_attempt_id ||
        restart_retained->attempt_id != *retained_attempt_id)) ||
      retained_bytes >= plan.missing_bytes) {
    return Status{ErrorCode::internal_error,
                  "sync range retry state is inconsistent"};
  }
  if (restart_retained) {
    auto expected = make_durable_range_attempt(
        restart_retained->attempt_id, plan,
        DurableSyncAttemptState::restart_retained, *config_.sodium);
    if (!expected || expected.value() != *restart_retained) {
      return Status{ErrorCode::protocol_error,
                    "restart-retained range plan binding changed"};
    }
  }
  const auto discard_retained = [&]() -> Status {
    if (!retained_attempt_id || restart_retained) return Status::success();
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    return discard_sync_attempt_staging(
        job.policy, *retained_attempt_id, transaction.value());
  };
  auto assigned = job.scheduler->assign(
      plan.target.kind, plan.target.identity, job.carrier.route_key,
      job.carrier.worker_id);
  if (!assigned) {
    const Status discarded = discard_retained();
    return discarded.ok() ? assigned.status() : discarded;
  }
  auto file_id = seams_.make_file_id();
  auto message_id = seams_.make_message_id();
  if (!file_id || !message_id || message_id.value() == 0U ||
      std::all_of(file_id.value().begin(), file_id.value().end(),
                  [](std::uint8_t byte) { return byte == 0U; })) {
    const Status fenced = job.scheduler->fence_attempt(
        assigned.value().attempt_id);
    const Status discarded = discard_retained();
    if (!fenced.ok()) return fenced;
    if (!discarded.ok()) return discarded;
    return !file_id ? file_id.status()
           : !message_id ? message_id.status()
                         : Status{ErrorCode::protocol_error,
                                  "sync range retry allocator returned zero"};
  }
  RangeLane lane;
  lane.plan = std::move(plan);
  lane.file_id = file_id.value();
  lane.request_message_id = message_id.value();
  lane.attempt_id = assigned.value().attempt_id;
  lane.bundle_bytes = lane.plan.missing_bytes;
  lane.retries = retry_count;
  std::vector<SyncRangeRecord> ranges;
  ranges.reserve(lane.plan.missing_ranges.size());
  for (const SyncMissingRange &range : lane.plan.missing_ranges) {
    ranges.push_back({range.offset, range.length});
  }
  auto request = make_sync_range_request_frame(
      {job.policy.id, job.head_record, lane.file_id, std::move(ranges)},
      lane.request_message_id);
  if (!request) {
    const Status fenced = job.scheduler->fence_attempt(lane.attempt_id);
    const Status discarded = discard_retained();
    if (!discarded.ok()) return discarded;
    return fenced.ok() ? Result<protocol::Frame>{request.status()}
                       : Result<protocol::Frame>{fenced};
  }
  if (retained_attempt_id) {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) {
      static_cast<void>(job.scheduler->fence_attempt(lane.attempt_id));
      return transaction.status();
    }
    if (restart_retained) {
      auto finished = job.attempt_store->finish(
          job.policy, *restart_retained, *config_.identity,
          *config_.sodium, transaction.value());
      if (!finished) {
        static_cast<void>(job.scheduler->fence_attempt(lane.attempt_id));
        return finished.status();
      }
      if (!finished.value()) {
        static_cast<void>(job.scheduler->fence_attempt(lane.attempt_id));
        return Status{ErrorCode::protocol_error,
                      "restart-retained range attempt disappeared"};
      }
    }
    auto partial = handoff_sync_attempt_partial(
        job.policy, *retained_attempt_id, lane.attempt_id,
        lane.plan.target, transaction.value());
    if (!partial || partial.value().bytes != retained_bytes) {
      const Status handoff_failure = !partial
          ? partial.status()
          : Status{ErrorCode::protocol_error,
                   "retained range prefix size changed before handoff"};
      const Status discarded_prior = discard_sync_attempt_staging(
          job.policy, *retained_attempt_id, transaction.value());
      const Status discarded_next = discard_sync_attempt_staging(
          job.policy, lane.attempt_id, transaction.value());
      const Status fenced = job.scheduler->fence_attempt(lane.attempt_id);
      if (!discarded_prior.ok()) return discarded_prior;
      if (!discarded_next.ok()) return discarded_next;
      if (!fenced.ok()) return fenced;
      return handoff_failure;
    }
    auto durable = make_durable_range_attempt(
        lane.attempt_id, lane.plan, DurableSyncAttemptState::active,
        *config_.sodium);
    if (!durable) return durable.status();
    auto begun = job.attempt_store->begin(
        job.policy, durable.value(), *config_.identity, *config_.sodium,
        transaction.value());
    if (!begun) {
      const Status discarded = discard_sync_attempt_staging(
          job.policy, lane.attempt_id, transaction.value());
      const Status fenced = job.scheduler->fence_attempt(lane.attempt_id);
      if (!discarded.ok()) return discarded;
      if (!fenced.ok()) return fenced;
      return begun.status();
    }
    lane.staging_path = partial.value().path;
    lane.resume_offset = retained_bytes;
    lane.journal_active = true;
    lane.restart_resumed = restart_retained.has_value();
    job.status.range_retained_bytes =
        retained_bytes > std::numeric_limits<std::uint64_t>::max() -
                             job.status.range_retained_bytes
            ? std::numeric_limits<std::uint64_t>::max()
            : job.status.range_retained_bytes + retained_bytes;
  }
  job.range_lane.emplace(std::move(lane));
  if (reason == RangeAttemptReason::initial) {
    ++job.status.requested_objects;
    job.status.detail = restart_retained
        ? "restart-retained range prefix handed to fresh authorized attempt"
        : "bounded missing-range bundle requested after manifest verification";
  } else if (reason == RangeAttemptReason::retry) {
    ++job.status.requested_objects;
    job.status.range_retries = retry_count;
    job.status.detail = retained_attempt_id
        ? "bounded range prefix retained for fresh-identity retry"
        : "bounded range attempt cleared and retried with fresh transport identity";
  } else {
    job.status.detail = retained_attempt_id
        ? "range prefix handed to fresh attempt on replacement carrier"
        : "range attempt reassigned from byte zero on replacement carrier";
  }
  return std::move(request).value();
}

Result<std::vector<protocol::Frame>>
SyncSubscriberService::handle_head_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_head_result_frame(frame);
  if (!valid.ok()) return valid;
  auto index = correlated_job_index(context.friend_number,
                                    context.online_epoch,
                                    frame.correlation_id);
  if (!index) return index.status();
  PullJob &job = *jobs_[index.value()];
  if (job.status.state == SyncPullState::cancelled) {
    return std::vector<protocol::Frame>{};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(job.authority_context, context)) {
    fail_job(job, "publisher authority changed before HEAD result");
    return authorized.ok()
               ? Status{ErrorCode::unavailable,
                        "sync publisher authority changed"}
               : authorized;
  }
  auto canonical = protocol::encode(frame);
  if (!canonical) return canonical.status();
  if (job.head_result_record) {
    if (*job.head_result_record != canonical.value()) {
      return Status{ErrorCode::protocol_error,
                    "sync HEAD result conflicts with retained response"};
    }
  } else {
    job.head_result_record = canonical.value();
  }
  if (job.status.state == SyncPullState::awaiting_objects) {
    if (job.carrier != context.transfer_carrier) {
      return Status{ErrorCode::unavailable,
                    "sync object retry carrier changed without reassignment"};
    }
    std::vector<protocol::Frame> requests;
    requests.reserve(job.lanes.size() + (job.range_lane ? 1U : 0U));
    for (const ObjectLane &lane : job.lanes) {
      if (lane.result_record) continue;
      auto request = make_sync_object_request_frame(
          {job.policy.id, lane.object.kind, job.head_record, lane.file_id},
          lane.request_message_id);
      if (!request) return request.status();
      requests.push_back(std::move(request).value());
    }
    if (job.range_lane && !job.range_lane->result_record) {
      std::vector<SyncRangeRecord> ranges;
      ranges.reserve(job.range_lane->plan.missing_ranges.size());
      for (const SyncMissingRange &range :
           job.range_lane->plan.missing_ranges) {
        ranges.push_back({range.offset, range.length});
      }
      auto request = make_sync_range_request_frame(
          {job.policy.id, job.head_record, job.range_lane->file_id,
           std::move(ranges)},
          job.range_lane->request_message_id);
      if (!request) return request.status();
      requests.push_back(std::move(request).value());
    }
    return requests;
  }
  if (job.status.state != SyncPullState::awaiting_head) {
    return std::vector<protocol::Frame>{};
  }
  auto decoded = decode_sync_head_result(frame.payload);
  if (!decoded) return decoded.status();
  if (decoded.value().status != SyncHeadResultStatus::available ||
      !decoded.value().head) {
    fail_job(job, "publisher did not provide an available signed HEAD");
    return std::vector<protocol::Frame>{};
  }
  auto candidate = verified_candidate_head(
      job.policy, *decoded.value().head, *config_.sodium);
  if (!candidate) {
    fail_job(job, candidate.status().message());
    return candidate.status();
  }
  Result<std::shared_ptr<SyncGuardedStateWitness>> witness{
      std::shared_ptr<SyncGuardedStateWitness>{}};
  if (seams_.install.guarded_state_witness) {
    witness = seams_.install.guarded_state_witness(job.policy);
    if (!witness) {
      fail_job(job, witness.status().message());
      return witness.status();
    }
  }
  std::optional<AcceptedHead> current_head;
  HeadAcceptanceResult evaluated;
  {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) {
      fail_job(job, transaction.status().message());
      return transaction.status();
    }
    if (witness.value()) {
      const Status verified = witness.value()->verify_read(
          job.policy, transaction.value());
      if (!verified.ok()) {
        fail_job(job, verified.message());
        return verified;
      }
    }
    AcceptedHeadStore accepted(job.policy.root, witness.value());
    auto current = accepted.load(job.policy, config_.identity->public_key(),
                                 *config_.sodium);
    if (!current) {
      fail_job(job, current.status().message());
      return current.status();
    }
    current_head = current.value();
    evaluated = evaluate_candidate_head(
        job.policy, candidate.value(), current_head);
  }
  if (!evaluated.accepted()) {
    fail_job(job, std::string("signed HEAD refused: ") +
                      std::string(head_acceptance_decision_name(
                          evaluated.decision)));
    return std::vector<protocol::Frame>{};
  }
  const Status prepared = prepare_objects(
      job, context, *decoded.value().head, candidate.value(),
      current_head);
  if (!prepared.ok()) {
    fail_job(job, prepared.message());
    return prepared;
  }
  std::vector<protocol::Frame> immediate_requests;
  if (job.range_mode && job.lanes.empty() && !job.range_lane) {
    auto range = prepare_artifact_after_manifest(job);
    if (!range) {
      fail_job(job, range.status().message());
      return range.status();
    }
    immediate_requests = std::move(range).value();
  }
  const Status accepted_status = maybe_accept_head(job, context);
  if (!accepted_status.ok()) return accepted_status;
  if (job.status.state == SyncPullState::complete) {
    return std::vector<protocol::Frame>{};
  }
  if (!immediate_requests.empty()) return immediate_requests;
  std::vector<protocol::Frame> requests;
  requests.reserve(job.lanes.size());
  for (const ObjectLane &lane : job.lanes) {
    auto request = make_sync_object_request_frame(
        {job.policy.id, lane.object.kind, job.head_record, lane.file_id},
        lane.request_message_id);
    if (!request) return request.status();
    requests.push_back(std::move(request).value());
  }
  return requests;
}

Result<std::vector<protocol::Frame>>
SyncSubscriberService::handle_object_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_object_result_frame(frame);
  if (!valid.ok()) return valid;
  auto decoded = decode_sync_object_result(frame.payload);
  if (!decoded) return decoded.status();
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    if (job.status.friend_number != context.friend_number ||
        job.status.online_epoch != context.online_epoch ||
        job.status.state != SyncPullState::awaiting_objects ||
        job.carrier != context.transfer_carrier)
      continue;
    const auto lane = std::find_if(
        job.lanes.begin(), job.lanes.end(),
        [&frame](const ObjectLane &candidate) {
          return candidate.request_message_id == frame.correlation_id;
        });
    if (lane == job.lanes.end()) continue;
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok() || !same_authority(job.authority_context, context)) {
      fail_job(job, "publisher authority changed before object result");
      return authorized.ok()
                 ? Status{ErrorCode::unavailable,
                          "sync publisher authority changed"}
                 : authorized;
    }
    if (decoded.value().kind != lane->object.kind ||
        decoded.value().head_record != job.head_record ||
        decoded.value().transfer_id != lane->file_id) {
      fail_job(job, "sync object result identity changed");
      return Status{ErrorCode::protocol_error,
                    "sync object result identity changed"};
    }
    auto canonical = protocol::encode(frame);
    if (!canonical) return canonical.status();
    if (lane->result_record && *lane->result_record != canonical.value()) {
      fail_job(job, "sync object result replay conflicted");
      return Status{ErrorCode::protocol_error,
                    "sync object result replay conflicted"};
    }
    if (decoded.value().status == SyncObjectResultStatus::unavailable) {
      if (lane->result_record || lane->result_offered ||
          lane->file_number || lane->transport_admitted) {
        fail_job(job,
                 "publisher availability changed after an immutable object offer");
        return Status{ErrorCode::protocol_error,
                      "sync object availability changed after offer"};
      }
      if (lane->result_retries >=
          config_.maximum_object_result_retries) {
        fail_job(job,
                 "publisher unavailable retry bound exhausted");
        return std::vector<protocol::Frame>{};
      }
      auto file_id = seams_.make_file_id();
      auto message_id = seams_.make_message_id();
      if (!file_id || !message_id || message_id.value() == 0U ||
          std::all_of(file_id.value().begin(), file_id.value().end(),
                      [](std::uint8_t byte) { return byte == 0U; })) {
        const Status allocated = !file_id
            ? file_id.status()
            : !message_id
                ? message_id.status()
                : Status{ErrorCode::protocol_error,
                         "sync object retry allocator returned zero"};
        fail_job(job, allocated.message());
        return allocated;
      }
      lane->file_id = file_id.value();
      lane->request_message_id = message_id.value();
      ++lane->result_retries;
      if (job.status.object_result_retries !=
          std::numeric_limits<std::uint64_t>::max()) {
        ++job.status.object_result_retries;
      }
      job.status.detail =
          "publisher temporarily unavailable; immutable object retried with fresh transport identity";
      auto retry = make_sync_object_request_frame(
          {job.policy.id, lane->object.kind, job.head_record,
           lane->file_id},
          lane->request_message_id);
      if (!retry) {
        fail_job(job, retry.status().message());
        return retry.status();
      }
      return std::vector<protocol::Frame>{std::move(retry).value()};
    }
    lane->result_record = canonical.value();
    lane->result_offered =
        decoded.value().status == SyncObjectResultStatus::offered;
    if (!lane->result_offered) {
      fail_job(job, "publisher refused an immutable object");
      return std::vector<protocol::Frame>{};
    }
    return std::vector<protocol::Frame>{};
  }
  return Status{ErrorCode::not_found,
                "sync object result has no active request"};
}

Status SyncSubscriberService::handle_range_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_range_result_frame(frame);
  if (!valid.ok()) return valid;
  auto decoded = decode_sync_range_result(frame.payload);
  if (!decoded) return decoded.status();
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    if (job.status.friend_number != context.friend_number ||
        job.status.online_epoch != context.online_epoch ||
        job.status.state != SyncPullState::awaiting_objects ||
        job.carrier != context.transfer_carrier ||
        !job.range_lane ||
        job.range_lane->carrier_lost ||
        job.range_lane->request_message_id != frame.correlation_id) {
      continue;
    }
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok() || !same_authority(job.authority_context, context)) {
      fail_job(job, "publisher authority changed before range result");
      return authorized.ok()
                 ? Status{ErrorCode::unavailable,
                          "sync publisher authority changed"}
                 : authorized;
    }
    RangeLane &lane = *job.range_lane;
    if (decoded.value().head_record != job.head_record ||
        decoded.value().transfer_id != lane.file_id) {
      fail_job(job, "sync range result identity changed");
      return Status{ErrorCode::protocol_error,
                    "sync range result identity changed"};
    }
    auto canonical = protocol::encode(frame);
    if (!canonical) return canonical.status();
    if (lane.result_record && *lane.result_record != canonical.value()) {
      fail_job(job, "sync range result replay conflicted");
      return Status{ErrorCode::protocol_error,
                    "sync range result replay conflicted"};
    }
    lane.result_record = canonical.value();
    lane.result_offered =
        decoded.value().status == SyncRangeResultStatus::offered;
    if (!lane.result_offered) {
      fail_job(job, "publisher refused a bounded range bundle");
    }
    return Status::success();
  }
  return Status{ErrorCode::not_found,
                "sync range result has no active request"};
}

Result<bool> SyncSubscriberService::handle_offer(
    const SyncPeerContext &context, const FileTransferRecord &offer) {
  std::scoped_lock lock(mutex_);
  if (offer.direction != FileTransferDirection::incoming ||
      !offer.has_file_id)
    return false;
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    if (job.status.friend_number != context.friend_number ||
        job.status.online_epoch != context.online_epoch ||
        job.status.state != SyncPullState::awaiting_objects ||
        job.carrier != context.transfer_carrier)
      continue;
    if (job.range_lane && job.range_lane->file_id == offer.file_id) {
      RangeLane &range = *job.range_lane;
      if (range.carrier_lost) {
        return Status{ErrorCode::unavailable,
                      "sync range carrier is fenced pending reassignment"};
      }
      const Status authorized = authorize_publish(context, job.policy);
      if (!authorized.ok() ||
          !same_authority(job.authority_context, context)) {
        fail_job(job, "publisher authority changed before range offer");
        return authorized.ok()
                   ? Result<bool>{Status{
                         ErrorCode::unavailable,
                         "sync publisher authority changed"}}
                   : Result<bool>{authorized};
      }
      if (offer.friend_number != job.carrier.friend_number ||
          offer.file_size != range.bundle_bytes) {
        fail_job(job, "sync range offer size or peer changed");
        return Status{ErrorCode::protocol_error,
                      "sync range offer size or peer changed"};
      }
      if (range.file_number && *range.file_number != offer.file_number) {
        return Status{ErrorCode::protocol_error,
                      "sync range FileId was reused by another file number"};
      }
      if (range.transport_admitted) return true;
      const bool already_pending = range.offer_pending;
      range.file_number = offer.file_number;
      range.offer_pending = true;
      const Status admitted = [&]() -> Status {
        auto transaction = SyncNamespaceTransaction::acquire(job.policy);
        if (!transaction) return transaction.status();
        const bool resume = range.resume_offset != 0U;
        const bool receive_in_place =
            static_cast<bool>(seams_.receive_to_path_from_offset);
        std::filesystem::path staging_path;
        if (resume) {
          if (!receive_in_place ||
              !range.journal_active || range.staging_path.empty()) {
            return Status{ErrorCode::internal_error,
                          "retained range prefix lost its receive contract"};
          }
          auto partial = inspect_sync_attempt_partial(
              job.policy, range.attempt_id, range.plan.target,
              transaction.value());
          if (!partial || partial.value().path != range.staging_path ||
              partial.value().bytes != range.resume_offset) {
            return !partial
                ? partial.status()
                : Status{ErrorCode::protocol_error,
                         "retained range prefix changed before receive"};
          }
          staging_path = partial.value().path;
        } else if (receive_in_place && range.journal_active &&
                   !range.staging_path.empty()) {
          // A receive-ceiling deferral may leave the exact empty attempt
          // inode and its signed journal entry behind the same FileId. Reuse
          // that inert local state instead of allocating a second attempt.
          auto partial = inspect_sync_attempt_partial(
              job.policy, range.attempt_id, range.plan.target,
              transaction.value());
          if (!partial || partial.value().path != range.staging_path ||
              partial.value().bytes != 0U) {
            return !partial
                ? partial.status()
                : Status{ErrorCode::protocol_error,
                         "deferred empty range partial changed before receive"};
          }
          staging_path = partial.value().path;
        } else if (receive_in_place) {
          auto partial = create_sync_attempt_partial(
              job.policy, range.attempt_id, range.plan.target,
              transaction.value());
          if (!partial) return partial.status();
          staging_path = partial.value().path;
        } else {
          auto staging = prepare_sync_attempt_staging(
              job.policy, range.attempt_id, range.plan.target,
              transaction.value());
          if (!staging) return staging.status();
          staging_path = staging.value();
        }
        auto durable = make_durable_range_attempt(
            range.attempt_id, range.plan, DurableSyncAttemptState::active,
            *config_.sodium);
        if (!durable) return durable.status();
        if (!range.journal_active) {
          auto begun = job.attempt_store->begin(
              job.policy, durable.value(), *config_.identity,
              *config_.sodium,
              transaction.value());
          if (!begun) {
            if (receive_in_place) {
              const Status discarded = discard_sync_attempt_staging(
                  job.policy, range.attempt_id, transaction.value());
              if (!discarded.ok()) return discarded;
            }
            return begun.status();
          }
          range.journal_active = true;
        }
        range.staging_path = staging_path;
        auto accepted = receive_in_place
            ? seams_.receive_to_path_from_offset(
                  job.carrier, offer.file_number, staging_path,
                  range.resume_offset)
            : seams_.receive_to_path(
                  job.carrier, offer.file_number, staging_path);
        if (!accepted ||
            accepted.value().direction != FileTransferDirection::incoming ||
            accepted.value().file_number != offer.file_number ||
            accepted.value().file_size != range.bundle_bytes ||
            accepted.value().position != range.resume_offset ||
            accepted.value().local_path != staging_path) {
          const Status failure = !accepted
              ? accepted.status()
              : Status{ErrorCode::protocol_error,
                       "worker accepted record conflicts with range bundle"};
          // A receive-ceiling deferral has admitted no transport effect. A
          // prepared private prefix and its signed attempt remain exact, so
          // keep both behind the same FileId offer for bounded retry.
          if (!accepted && receive_in_place &&
              failure.code() == ErrorCode::resource_exhausted) {
            return failure;
          }
          if (accepted) {
            static_cast<void>(seams_.cancel_transfer(
                job.carrier, offer.file_number));
          }
          const Status discarded = discard_sync_attempt_staging(
              job.policy, range.attempt_id, transaction.value());
          auto finished = discarded.ok()
              ? job.attempt_store->finish(
                    job.policy, durable.value(), *config_.identity,
                    *config_.sodium,
                    transaction.value())
              : Result<bool>{discarded};
          range.journal_active = !finished;
          if (finished) {
            if (resume &&
                job.status.range_retention_fallbacks !=
                    std::numeric_limits<std::uint64_t>::max()) {
              ++job.status.range_retention_fallbacks;
            }
            range.resume_offset = 0U;
            range.staging_path.clear();
          }
          if (failure.code() != ErrorCode::resource_exhausted) {
            static_cast<void>(
                job.scheduler->fence_attempt(range.attempt_id));
          }
          return finished ? failure : finished.status();
        }
        if (resume) {
          job.status.range_resumed_bytes =
              range.resume_offset >
                      std::numeric_limits<std::uint64_t>::max() -
                          job.status.range_resumed_bytes
                  ? std::numeric_limits<std::uint64_t>::max()
                  : job.status.range_resumed_bytes + range.resume_offset;
          if (range.restart_resumed) {
            if (job.status.range_restart_resumed_attempts !=
                std::numeric_limits<std::uint64_t>::max()) {
              ++job.status.range_restart_resumed_attempts;
            }
            job.status.range_restart_resumed_bytes =
                range.resume_offset >
                        std::numeric_limits<std::uint64_t>::max() -
                            job.status.range_restart_resumed_bytes
                    ? std::numeric_limits<std::uint64_t>::max()
                    : job.status.range_restart_resumed_bytes +
                          range.resume_offset;
            job.status.range_restart_suffix_bytes =
                range.bundle_bytes - range.resume_offset;
          }
        }
        return Status::success();
      }();
      if (!admitted.ok()) {
        if (admitted.code() == ErrorCode::resource_exhausted) {
          if (!already_pending) ++job.status.pending_offers;
          if (job.status.admission_retries !=
              std::numeric_limits<std::uint64_t>::max()) {
            ++job.status.admission_retries;
          }
          job.status.detail =
              "range offer retained behind the Agent receive ceiling";
          return true;
        }
        fail_job(job, admitted.message());
        return admitted;
      }
      range.transport_admitted = true;
      range.offer_pending = false;
      if (already_pending && job.status.pending_offers != 0U)
        --job.status.pending_offers;
      ++job.status.admitted_offers;
      job.status.detail = "receiving bounded missing-range bundle";
      return true;
    }
    const auto lane = std::find_if(
        job.lanes.begin(), job.lanes.end(),
        [&offer](const ObjectLane &candidate) {
          return candidate.file_id == offer.file_id;
        });
    if (lane == job.lanes.end()) continue;
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok() || !same_authority(job.authority_context, context)) {
      fail_job(job, "publisher authority changed before file offer");
      return authorized.ok()
                 ? Result<bool>{Status{ErrorCode::unavailable,
                                       "sync publisher authority changed"}}
                 : Result<bool>{authorized};
    }
    if (offer.friend_number != job.carrier.friend_number ||
        offer.file_size != lane->object.bytes) {
      fail_job(job, "sync file offer size or peer changed");
      return Status{ErrorCode::protocol_error,
                    "sync file offer size or peer changed"};
    }
    if (lane->file_number && *lane->file_number != offer.file_number) {
      return Status{ErrorCode::protocol_error,
                    "sync FileId was reused by another file number"};
    }
    if (lane->transport_admitted) return true;
    if (lane->carrier_admission_lost) return true;
    const bool already_pending = lane->file_number.has_value();
    lane->file_number = offer.file_number;
    auto accepted = job.transfers->accept_offer(
        lane->attempt_id, offer.file_number);
    if (!accepted) {
      if (accepted.status().code() == ErrorCode::resource_exhausted) {
        if (!already_pending) ++job.status.pending_offers;
        if (job.status.admission_retries !=
            std::numeric_limits<std::uint64_t>::max()) {
          ++job.status.admission_retries;
        }
        job.status.detail =
            "immutable object offer retained behind the Agent receive ceiling";
        return true;
      }
      if (job.carrier.carrier_class == SyncCarrierClass::auxiliary &&
          accepted.status().code() == ErrorCode::unavailable) {
        // Worker liveness can change after the parent revalidates a queued
        // offer but before the supervisor admits the receive. The transfer
        // coordinator has already discarded/fenced its provisional attempt.
        // Keep the pull live until the authoritative carrier-offline pass
        // applies failover policy; never turn that race into a terminal job
        // or repeat the same stale offer against a burned attempt ID.
        lane->carrier_admission_lost = true;
        lane->file_number.reset();
        job.capacity_ready = false;
        job.admitted_capacity = 0U;
        job.status.detail =
            "auxiliary receive admission lost its carrier; awaiting route fencing";
        return true;
      }
      fail_job(job, accepted.status().message());
      return accepted.status();
    }
    lane->transport_admitted = true;
    if (already_pending && job.status.pending_offers != 0U)
      --job.status.pending_offers;
    ++job.status.admitted_offers;
    job.status.detail = "receiving verified immutable objects";
    return true;
  }
  return false;
}

Status SyncSubscriberService::maybe_accept_head(
    PullJob &job, const SyncPeerContext &context) {
  if (!same_authority(job.authority_context, context)) {
    fail_job(job, "publisher authority changed before HEAD acceptance");
    return Status{ErrorCode::unavailable,
                  "sync publisher authority changed"};
  }
  const SyncSchedulerSnapshot state = job.scheduler->snapshot();
  job.status.committed_objects = static_cast<std::size_t>(std::count_if(
      state.objects.begin(), state.objects.end(), [](const auto &object) {
        return object.state == ScheduledObjectState::committed;
      }));
  if (state.objects.size() != 2U || job.status.committed_objects != 2U)
    return Status::success();
  if (!job.candidate) {
    return Status{ErrorCode::internal_error,
                  "sync pull lost its verified candidate HEAD"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(job.policy);
  if (!transaction) {
    fail_job(job, transaction.status().message());
    return transaction.status();
  }
  SyncInstallSeams install;
  install.hash_file = seams_.install.hash_file;
  const SyncObjectRecord artifact = object_from_candidate(
      *job.candidate, SyncObjectKind::artifact);
  const SyncObjectRecord manifest = object_from_candidate(
      *job.candidate, SyncObjectKind::manifest);
  const Status artifact_valid = verify_sync_object(
      job.policy, artifact, transaction.value(), install);
  if (!artifact_valid.ok()) {
    fail_job(job, artifact_valid.message());
    return artifact_valid;
  }
  const Status manifest_valid = verify_sync_object(
      job.policy, manifest, transaction.value(), install);
  if (!manifest_valid.ok()) {
    fail_job(job, manifest_valid.message());
    return manifest_valid;
  }
  const Status semantics = verify_sync_range_manifest(
      job.policy, sync_object_path(job.policy, artifact),
      sync_object_path(job.policy, manifest), artifact.identity,
      artifact.bytes, manifest.bytes);
  if (!semantics.ok()) {
    fail_job(job, semantics.message());
    return semantics;
  }
  Result<std::shared_ptr<SyncGuardedStateWitness>> witness{
      std::shared_ptr<SyncGuardedStateWitness>{}};
  if (seams_.install.guarded_state_witness) {
    witness = seams_.install.guarded_state_witness(job.policy);
    if (!witness) {
      fail_job(job, witness.status().message());
      return witness.status();
    }
  }
  AcceptedHeadStore accepted(job.policy.root, witness.value());
  auto committed = accepted.accept(job.policy, *job.candidate,
                                   *config_.identity, *config_.sodium, {},
                                   transaction.value());
  if (!committed) {
    fail_job(job, committed.status().message());
    return committed.status();
  }
  job.status.state = SyncPullState::complete;
  job.status.detail = "objects committed; signed HEAD accepted; not activated";
  return Status::success();
}

Result<std::vector<protocol::Frame>> SyncSubscriberService::handle_terminal(
    const SyncPeerContext &context, const FileTransferRecord &transfer,
    routes::WorkerTransferOutcome outcome, ErrorCode failure,
    std::string detail) {
  std::scoped_lock lock(mutex_);
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    if (job.status.friend_number != context.friend_number ||
        job.status.online_epoch != context.online_epoch ||
        job.status.state != SyncPullState::awaiting_objects ||
        job.carrier != context.transfer_carrier)
      continue;
    if (job.range_lane && job.range_lane->file_number &&
        *job.range_lane->file_number == transfer.file_number) {
      RangeLane &range = *job.range_lane;
      const Status authorized = authorize_publish(context, job.policy);
      if (!authorized.ok() ||
          !same_authority(job.authority_context, context)) {
        fail_job(job, "publisher authority changed before range commit");
        return authorized.ok()
                   ? Result<std::vector<protocol::Frame>>{Status{
                         ErrorCode::unavailable,
                         "sync publisher authority changed"}}
                   : Result<std::vector<protocol::Frame>>{authorized};
      }
      range.transport_admitted = false;
      range.offer_pending = false;
      range.file_number.reset();
      const bool complete =
          outcome == routes::WorkerTransferOutcome::completed &&
          failure == ErrorCode::ok &&
          transfer.direction == FileTransferDirection::incoming &&
          transfer.friend_number == job.carrier.friend_number &&
          transfer.file_size == range.bundle_bytes &&
          transfer.local_path == range.staging_path;
      bool range_retry_ready = false;
      std::optional<std::uint64_t> retained_attempt_id;
      std::uint64_t retained_bytes = 0U;
      const Status range_commit = [&]() -> Status {
        auto transaction = SyncNamespaceTransaction::acquire(job.policy);
        if (!transaction) return transaction.status();
        auto durable = make_durable_range_attempt(
            range.attempt_id, range.plan, DurableSyncAttemptState::active,
            *config_.sodium);
        if (!durable) return durable.status();
        if (!complete) {
          const bool retention_candidate =
              range.retries < config_.maximum_range_retries &&
              static_cast<bool>(seams_.receive_to_path_from_offset) &&
              transfer.position > 0U &&
              transfer.position < range.bundle_bytes &&
              transfer.local_path == range.staging_path;
          bool retained = false;
          if (retention_candidate) {
            auto partial = inspect_sync_attempt_partial(
                job.policy, range.attempt_id, range.plan.target,
                transaction.value());
            retained = partial &&
                       partial.value().path == range.staging_path &&
                       partial.value().bytes == transfer.position;
            if (!retained &&
                job.status.range_retention_fallbacks !=
                    std::numeric_limits<std::uint64_t>::max()) {
              ++job.status.range_retention_fallbacks;
            }
          }
          const Status discarded = retained
              ? Status::success()
              : discard_sync_attempt_staging(
                    job.policy, range.attempt_id, transaction.value());
          Result<bool> finished{Status{
              ErrorCode::unavailable,
              "sync range staging cleanup did not complete"}};
          if (discarded.ok()) {
            finished = job.attempt_store->finish(
                job.policy, durable.value(), *config_.identity,
                *config_.sodium,
                transaction.value());
            range.journal_active = !finished;
          }
          Status fenced{ErrorCode::unavailable,
                        "sync range attempt cleanup did not reach fencing"};
          if (discarded.ok() && finished) {
            fenced = job.scheduler->fence_attempt(range.attempt_id);
          }
          if (discarded.ok() && finished && fenced.ok()) {
            range_retry_ready = true;
            if (retained) {
              retained_attempt_id = range.attempt_id;
              retained_bytes = transfer.position;
            } else {
              const std::uint64_t discarded_bytes =
                  std::min(transfer.position, range.bundle_bytes);
              job.status.range_discarded_bytes =
                  discarded_bytes >
                          std::numeric_limits<std::uint64_t>::max() -
                              job.status.range_discarded_bytes
                      ? std::numeric_limits<std::uint64_t>::max()
                      : job.status.range_discarded_bytes + discarded_bytes;
            }
          }
          const Status terminal = !discarded.ok()
              ? discarded
              : !finished ? finished.status()
              : !fenced.ok() ? fenced
              : Status{
                    failure == ErrorCode::ok ? ErrorCode::io_error : failure,
                    detail.empty()
                        ? "sync range transfer ended before completion"
                        : std::move(detail)};
          return terminal;
        }

        auto bundle = open_range_bundle(
            range.staging_path, range.bundle_bytes);
        if (!bundle) return bundle.status();
        if (::unlink(range.staging_path.c_str()) != 0) {
          return errno_status(
              "unable to unlink admitted sync range bundle",
              range.staging_path);
        }
        SyncRangeReconstructionSeams reconstruction;
        reconstruction.install = seams_.install;
        const int bundle_descriptor = bundle.value().get();
        const SyncRangePlan *stable_plan = &range.plan;
        reconstruction.read_range =
            [bundle_descriptor, stable_plan](
                std::uint64_t offset,
                std::span<std::uint8_t> output) {
              return read_range_bundle(
                  bundle_descriptor, *stable_plan, offset, output);
            };
        auto reconstructed = reconstruct_sync_range_artifact(
            job.policy, range.plan, range.attempt_id,
            transaction.value(), reconstruction);
        if (!reconstructed) {
          auto failed_finish = job.attempt_store->finish(
              job.policy, durable.value(), *config_.identity,
              *config_.sodium,
              transaction.value());
          range.journal_active = !failed_finish;
          Status fenced{ErrorCode::unavailable,
                        "failed range reconstruction was not fenced"};
          if (failed_finish) {
            fenced = job.scheduler->fence_attempt(range.attempt_id);
          }
          if (failed_finish && fenced.ok()) {
            range_retry_ready = true;
            job.status.range_discarded_bytes =
                range.bundle_bytes >
                        std::numeric_limits<std::uint64_t>::max() -
                            job.status.range_discarded_bytes
                    ? std::numeric_limits<std::uint64_t>::max()
                    : job.status.range_discarded_bytes + range.bundle_bytes;
          }
          const Status reconstruction_failure =
              !failed_finish ? failed_finish.status()
              : !fenced.ok() ? fenced
                             : reconstructed.status();
          return reconstruction_failure;
        }
        auto committed = commit_sync_attempt_staging(
            job.policy, range.attempt_id, range.plan.target,
            transaction.value(), seams_.install);
        if (!committed) return committed.status();
        auto finished = job.attempt_store->finish(
            job.policy, durable.value(), *config_.identity,
            *config_.sodium,
            transaction.value());
        if (!finished) return finished.status();
        range.journal_active = false;
        const Status verified = job.scheduler->complete(
            range.attempt_id, range.plan.target.identity,
            range.plan.target.bytes);
        if (!verified.ok()) return verified;
        const Status finalized = job.scheduler->commit(range.attempt_id);
        if (!finalized.ok()) return finalized;
        range.committed = true;
        job.status.range_fetched_bytes =
            reconstructed.value().fetched_bytes;
        return Status::success();
      }();
      if (!range_commit.ok()) {
        if (range_retry_ready &&
            range.retries < config_.maximum_range_retries) {
          RangeLane prior = std::move(range);
          SyncRangePlan retry_plan = prior.plan;
          const std::size_t retry_count = prior.retries + 1U;
          job.range_lane.reset();
          auto retry = prepare_range_attempt(
              job, std::move(retry_plan), retry_count,
              RangeAttemptReason::retry,
              retained_attempt_id, retained_bytes);
          if (retry) {
            return std::vector<protocol::Frame>{
                std::move(retry).value()};
          }
          // Preserve the old inert lane until fail_job can settle any prefix
          // that the fresh-attempt transaction could not consume.
          job.range_lane.emplace(std::move(prior));
          fail_job(job, retry.status().message());
          return retry.status();
        }
        fail_job(job, range_commit.message());
        return range_commit;
      }
      const Status accepted = maybe_accept_head(job, context);
      if (!accepted.ok()) return accepted;
      return std::vector<protocol::Frame>{};
    }
    const auto lane = std::find_if(
        job.lanes.begin(), job.lanes.end(),
        [&transfer](const ObjectLane &candidate) {
          return candidate.file_number.has_value() &&
                 *candidate.file_number == transfer.file_number;
        });
    if (lane == job.lanes.end()) continue;
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok() || !same_authority(job.authority_context, context)) {
      fail_job(job, "publisher authority changed before object commit");
      return authorized.ok()
                 ? Status{ErrorCode::unavailable,
                          "sync publisher authority changed"}
                 : authorized;
    }
    const SyncObjectKind completed_kind = lane->object.kind;
    routes::WorkerTransferTerminalEvent event;
    event.route_key = job.carrier.route_key;
    event.worker_id = job.carrier.worker_id;
    event.transfer = transfer;
    event.transfer.detail = std::move(detail);
    event.outcome = outcome;
    event.failure = failure;
    const Status applied = job.transfers->handle_terminal(std::move(event));
    if (!applied.ok()) {
      fail_job(job, applied.message());
      return applied;
    }
    std::vector<protocol::Frame> followup;
    if (job.range_mode && completed_kind == SyncObjectKind::manifest &&
        !job.range_lane) {
      auto prepared = prepare_artifact_after_manifest(job);
      if (!prepared) {
        fail_job(job, prepared.status().message());
        return prepared.status();
      }
      followup = std::move(prepared).value();
    }
    const Status accepted = maybe_accept_head(job, context);
    if (!accepted.ok()) return accepted;
    return followup;
  }
  return Status{ErrorCode::not_found,
                "sync terminal event has no active binding"};
}

Status SyncSubscriberService::cancel_pull(std::uint64_t job_id) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  auto index = job_id_index(job_id);
  if (!index) return index.status();
  PullJob &job = *jobs_[index.value()];
  if (job.status.state == SyncPullState::complete ||
      job.status.state == SyncPullState::failed) {
    return Status{ErrorCode::unavailable,
                  "sync pull job is already terminal"};
  }

  // Fence message, offer, and terminal dispatch before cancellation invokes
  // the transport seam. A failed cleanup therefore cannot make late network
  // truth eligible for object or HEAD commit.
  job.status.state = SyncPullState::cancelled;
  job.cancellation_settled = false;
  Status first = settle_pending_offers(job);
  const Status range = settle_range_cleanup(job);
  if (!range.ok() && first.ok()) first = range;
  if (job.transfers) {
    const Status closed = job.transfers->close();
    if (!closed.ok() && first.ok()) first = closed;
  }
  if (job.scheduler) {
    const Status closed = job.scheduler->close();
    if (!closed.ok() && first.ok()) first = closed;
  }
  if (!first.ok()) {
    const bool transfers_closed =
        !job.transfers || job.transfers->snapshot().closed;
    const bool scheduler_closed =
        !job.scheduler || job.scheduler->snapshot().closed;
    job.status.detail = transfers_closed && scheduler_closed
        ? "cancelled; local cleanup fenced; retry required after transport cancellation error: " +
              first.message()
        : "cancelled; cleanup incomplete and will be retried: " +
              first.message();
    return first;
  }
  job.status.detail =
      "cancelled; transfers fenced; staging and attempt records closed";
  job.cancellation_settled = true;
  return Status::success();
}

Result<std::vector<protocol::Frame>>
SyncSubscriberService::reassign_transfer_carrier(
    std::uint64_t job_id, const SyncPeerContext &context) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  auto index = job_id_index(job_id);
  if (!index) return index.status();
  PullJob &job = *jobs_[index.value()];
  const bool range_reassignment =
      job.range_mode && job.range_lane &&
      job.range_lane->carrier_lost;
  if (job.status.state != SyncPullState::awaiting_objects ||
      !job.scheduler || !job.transfers ||
      (!range_reassignment && (job.range_mode || job.range_lane))) {
    return Status{ErrorCode::unsupported,
                  "sync job has no reassignable carrier state"};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok()) return authorized;
  if (!same_authority(job.authority_context, context)) {
    return Status{ErrorCode::unavailable,
                  "sync publisher authority changed before carrier reassignment"};
  }
  if (job.carrier == context.transfer_carrier) {
    return Status{ErrorCode::invalid_argument,
                  "sync replacement carrier is unchanged"};
  }

  if (range_reassignment) {
    if (!context.range_transfer_negotiated) {
      return Status{
          ErrorCode::unsupported,
          "replacement carrier did not negotiate bounded ranges"};
    }
    RangeLane prior = std::move(*job.range_lane);
    const std::optional<std::uint64_t> retained_attempt_id =
        prior.resume_offset == 0U
            ? std::nullopt
            : std::optional<std::uint64_t>{prior.attempt_id};
    const std::uint64_t retained_bytes = prior.resume_offset;
    SyncRangePlan plan = prior.plan;
    const std::size_t retry_count = prior.retries;
    job.range_lane.reset();
    job.capacity_ready = true;
    job.admitted_capacity = 0U;
    job.carrier = context.transfer_carrier;
    job.status.transfer_carrier = context.transfer_carrier;
    auto request = prepare_range_attempt(
        job, std::move(plan), retry_count,
        RangeAttemptReason::carrier_reassignment,
        retained_attempt_id, retained_bytes);
    if (!request) {
      // A failed fresh-attempt transition may still own the inactive old
      // prefix. Give terminal cleanup that exact lane instead of orphaning
      // bytes merely because the namespace transaction was unavailable.
      job.range_lane.emplace(std::move(prior));
      fail_job(job, request.status().message());
      return request.status();
    }
    return std::vector<protocol::Frame>{std::move(request).value()};
  }

  if (job.capacity_ready) {
    const Status pending = settle_pending_offers(job);
    if (!pending.ok()) return pending;
  } else {
    for (ObjectLane &lane : job.lanes) {
      if (!lane.transport_admitted) lane.file_number.reset();
    }
    job.status.pending_offers = 0U;
  }
  auto fenced = job.transfers->fence_route(
      job.carrier.route_key, job.carrier.worker_id,
      job.capacity_ready);
  if (!fenced) {
    fail_job(job, fenced.status().message());
    return fenced.status();
  }
  job.capacity_ready = true;
  job.admitted_capacity = 0U;
  job.carrier = context.transfer_carrier;
  job.status.transfer_carrier = context.transfer_carrier;

  const SyncSchedulerSnapshot scheduler_state = job.scheduler->snapshot();
  std::vector<protocol::Frame> requests;
  requests.reserve(job.lanes.size());
  for (ObjectLane &lane : job.lanes) {
    const auto object = std::find_if(
        scheduler_state.objects.begin(), scheduler_state.objects.end(),
        [&lane](const ScheduledObjectSnapshot &candidate) {
          return candidate.object == lane.object;
        });
    if (object == scheduler_state.objects.end()) {
      fail_job(job, "sync reassignment lost its immutable object");
      return Status{ErrorCode::internal_error,
                    "sync reassignment lost its immutable object"};
    }
    if (object->state == ScheduledObjectState::committed) {
      lane.file_number.reset();
      lane.result_record.reset();
      lane.result_offered = false;
      lane.transport_admitted = false;
      continue;
    }
    if (object->state != ScheduledObjectState::pending) {
      fail_job(job, "sync prior carrier was not completely fenced");
      return Status{ErrorCode::unavailable,
                    "sync prior carrier was not completely fenced"};
    }
    auto file_id = seams_.make_file_id();
    auto message_id = seams_.make_message_id();
    if (!file_id || !message_id || message_id.value() == 0U ||
        std::all_of(file_id.value().begin(), file_id.value().end(),
                    [](std::uint8_t byte) { return byte == 0U; })) {
      const Status failure =
          !file_id ? file_id.status()
          : !message_id ? message_id.status()
          : Status{ErrorCode::protocol_error,
                   "sync reassignment allocator returned zero"};
      fail_job(job, failure.message());
      return failure;
    }
    auto assigned = job.scheduler->assign(
        lane.object.kind, lane.object.identity, job.carrier.route_key,
        job.carrier.worker_id);
    if (!assigned) {
      fail_job(job, assigned.status().message());
      return assigned.status();
    }
    lane.file_id = file_id.value();
    lane.request_message_id = message_id.value();
    lane.attempt_id = assigned.value().attempt_id;
    lane.file_number.reset();
    lane.result_record.reset();
    lane.result_offered = false;
    lane.transport_admitted = false;
    auto request = make_sync_object_request_frame(
        {job.policy.id, lane.object.kind, job.head_record, lane.file_id},
        lane.request_message_id);
    if (!request) {
      fail_job(job, request.status().message());
      return request.status();
    }
    requests.push_back(std::move(request).value());
  }
  job.status.detail = "prior carrier fenced; immutable objects reassigned";
  return requests;
}

Status SyncSubscriberService::settle_range_cleanup(
    PullJob &job, bool cancel_transport, bool record_discarded_bytes) {
  if (!job.range_lane || job.range_lane->committed)
    return Status::success();
  RangeLane &range = *job.range_lane;
  Status first = Status::success();
  if (record_discarded_bytes && !range.staging_path.empty()) {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) {
      first = transaction.status();
    } else {
      auto partial = inspect_sync_attempt_partial(
          job.policy, range.attempt_id, range.plan.target,
          transaction.value());
      if (partial) {
        const std::uint64_t discarded =
            std::min(partial.value().bytes, range.bundle_bytes);
        job.status.range_discarded_bytes =
            discarded > std::numeric_limits<std::uint64_t>::max() -
                            job.status.range_discarded_bytes
                ? std::numeric_limits<std::uint64_t>::max()
                : job.status.range_discarded_bytes + discarded;
      }
    }
  }
  if ((range.offer_pending || range.transport_admitted) &&
      range.file_number) {
    const Status cancelled = cancel_transport
        ? seams_.cancel_transfer(job.carrier, *range.file_number)
        : seams_.retire_transfer(job.carrier, *range.file_number);
    const bool was_pending = range.offer_pending;
    range.offer_pending = false;
    range.transport_admitted = false;
    range.file_number.reset();
    if (was_pending && job.status.pending_offers != 0U)
      --job.status.pending_offers;
    if (!cancelled.ok()) first = cancelled;
  }
  if (!range.journal_active && range.staging_path.empty()) return first;
  auto transaction = SyncNamespaceTransaction::acquire(job.policy);
  if (!transaction) return first.ok() ? transaction.status() : first;
  const Status discarded = discard_sync_attempt_staging(
      job.policy, range.attempt_id, transaction.value());
  if (!discarded.ok() && first.ok()) first = discarded;
  if (discarded.ok() && range.journal_active) {
    auto durable = make_durable_range_attempt(
        range.attempt_id, range.plan, DurableSyncAttemptState::active,
        *config_.sodium);
    if (!durable) {
      if (first.ok()) first = durable.status();
    } else {
      auto finished = job.attempt_store->finish(
          job.policy, durable.value(), *config_.identity, *config_.sodium,
          transaction.value());
      if (!finished) {
        if (first.ok()) first = finished.status();
      } else {
        range.journal_active = false;
      }
    }
  }
  if (discarded.ok() && !range.journal_active) {
    range.staging_path.clear();
    range.resume_offset = 0U;
  }
  return first;
}

Status SyncSubscriberService::settle_pending_offers(PullJob &job) {
  Status first = Status::success();
  for (ObjectLane &lane : job.lanes) {
    if (!lane.file_number || lane.transport_admitted) continue;
    const Status cancelled = seams_.cancel_transfer(
        job.carrier, *lane.file_number);
    lane.file_number.reset();
    if (job.status.pending_offers != 0U)
      --job.status.pending_offers;
    if (!cancelled.ok() && first.ok()) first = cancelled;
  }
  return first;
}

Status SyncSubscriberService::settle_failed_cleanup(PullJob &job) {
  Status first = settle_pending_offers(job);
  const Status range = settle_range_cleanup(job);
  if (!range.ok() && first.ok()) first = range;
  if (job.transfers) {
    const Status closed = job.transfers->close();
    if (!closed.ok() && first.ok()) first = closed;
  }
  if (job.scheduler) {
    const Status closed = job.scheduler->close();
    if (!closed.ok() && first.ok()) first = closed;
  }
  job.failed_cleanup_settled = first.ok();
  return first;
}

Status SyncSubscriberService::namespace_mutation_ready(
    std::string_view namespace_id) const {
  std::scoped_lock lock(mutex_);
  if (!valid_namespace_id(namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync namespace id is invalid"};
  }
  for (const auto &job : jobs_) {
    if (job->status.namespace_id != namespace_id) continue;
    if (job->status.state == SyncPullState::awaiting_head ||
        job->status.state == SyncPullState::awaiting_objects) {
      return Status{ErrorCode::unavailable,
                    "sync namespace has a live subscriber job"};
    }
    if (job->status.state == SyncPullState::failed &&
        !job->failed_cleanup_settled) {
      return Status{ErrorCode::unavailable,
                    "sync namespace has unresolved failed-job cleanup"};
    }
    if (job->status.state == SyncPullState::cancelled &&
        !job->cancellation_settled) {
      return Status{ErrorCode::unavailable,
                    "sync namespace has unresolved cancellation cleanup"};
    }
  }
  return Status::success();
}

void SyncSubscriberService::fail_job(PullJob &job,
                                     std::string detail) noexcept {
  job.status.state = SyncPullState::failed;
  job.failed_cleanup_settled = false;
  const Status cleanup = settle_failed_cleanup(job);
  job.status.detail = std::move(detail);
  if (!cleanup.ok()) {
    job.status.detail +=
        "; local cleanup fenced but requires retry: " + cleanup.message();
  }
}

void SyncSubscriberService::peer_offline(std::uint32_t friend_number,
                                         std::uint64_t online_epoch) {
  std::scoped_lock lock(mutex_);
  for (auto &job : jobs_) {
    if (job->status.friend_number == friend_number &&
        job->status.online_epoch == online_epoch &&
        (job->status.state == SyncPullState::awaiting_head ||
         job->status.state == SyncPullState::awaiting_objects)) {
      job->capacity_ready = false;
      job->admitted_capacity = 0U;
      // toxcore has already purged unaccepted offers for this offline epoch.
      // They own no staging or durable active record, so retire their local
      // correlations without issuing impossible cancellation controls.
      for (ObjectLane &lane : job->lanes) {
        if (!lane.transport_admitted) lane.file_number.reset();
      }
      if (job->range_lane && job->range_lane->offer_pending) {
        job->range_lane->offer_pending = false;
        job->range_lane->file_number.reset();
      }
      job->status.pending_offers = 0U;
      fail_job(*job, "peer went offline; sync attempt fenced");
    }
  }
}

Status SyncSubscriberService::carrier_offline(
    const SyncTransferCarrier &carrier) {
  std::scoped_lock lock(mutex_);
  if (carrier.carrier_class != SyncCarrierClass::auxiliary) {
    return Status{ErrorCode::invalid_argument,
                  "primary authority loss must use peer_offline"};
  }
  Status first = Status::success();
  for (auto &job : jobs_) {
    if (job->carrier != carrier ||
        job->status.state != SyncPullState::awaiting_objects) {
      continue;
    }
    // range_mode is selected before the prerequisite manifest is fetched.
    // Only a concrete range lane owns range-bundle staging; otherwise the
    // live receive belongs to the whole-object coordinator and must be
    // fenced through that coordinator.
    if (job->range_lane) {
      if (job->range_lane->carrier_lost) {
        // Carrier inventory reconciliation may repeat the same absence.
        // The first edge already retired transport truth and fenced the old
        // attempt; a duplicate must not discard an inert retained prefix.
        continue;
      }
      job->capacity_ready = false;
      job->admitted_capacity = 0U;
      const bool reassign = sync_route_reassignment_allowed(
          job->status.route_failover_policy);
      if (!reassign) {
        const std::uint64_t range_attempt =
            job->range_lane->attempt_id;
        const Status cleaned = settle_range_cleanup(
            *job, false, true);
        if (!cleaned.ok()) {
          fail_job(*job, cleaned.message());
          if (first.ok()) first = cleaned;
          continue;
        }
        if (job->scheduler) {
          const Status fenced =
              job->scheduler->fence_attempt(range_attempt);
          if (!fenced.ok()) {
            fail_job(*job, fenced.message());
            if (first.ok()) first = fenced;
            continue;
          }
        }
        // The dead worker can no longer deliver authoritative transport
        // truth. Retire its FileId/request/attempt correlation atomically
        // with the route fence so delayed events are unclaimable.
        job->range_lane.reset();
        job->status.detail =
            "auxiliary range carrier lost; partial bundle discarded; fail-closed pull blocked";
        continue;
      }

      RangeLane &range = *job->range_lane;
      if ((range.offer_pending || range.transport_admitted) &&
          range.file_number) {
        const Status retired = seams_.retire_transfer(
            job->carrier, *range.file_number);
        const bool was_pending = range.offer_pending;
        range.offer_pending = false;
        range.transport_admitted = false;
        range.file_number.reset();
        if (was_pending && job->status.pending_offers != 0U) {
          --job->status.pending_offers;
        }
        if (!retired.ok()) {
          fail_job(*job, retired.message());
          if (first.ok()) first = retired;
          continue;
        }
      }

      std::uint64_t observed_bytes = 0U;
      bool retained = false;
      if (range.journal_active) {
        auto transaction = SyncNamespaceTransaction::acquire(job->policy);
        if (!transaction) {
          fail_job(*job, transaction.status().message());
          if (first.ok()) first = transaction.status();
          continue;
        }
        auto partial = inspect_sync_attempt_partial(
            job->policy, range.attempt_id, range.plan.target,
            transaction.value());
        if (partial) {
          observed_bytes =
              std::min(partial.value().bytes, range.bundle_bytes);
          retained = static_cast<bool>(
                         seams_.receive_to_path_from_offset) &&
                     partial.value().path == range.staging_path &&
                     partial.value().bytes > 0U &&
                     partial.value().bytes < range.bundle_bytes;
          if (observed_bytes != 0U && !retained &&
              job->status.range_retention_fallbacks !=
                  std::numeric_limits<std::uint64_t>::max()) {
            ++job->status.range_retention_fallbacks;
          }
        }
        if (!retained) {
          const Status discarded = discard_sync_attempt_staging(
              job->policy, range.attempt_id, transaction.value());
          if (!discarded.ok()) {
            fail_job(*job, discarded.message());
            if (first.ok()) first = discarded;
            continue;
          }
        }
        auto durable = make_durable_range_attempt(
            range.attempt_id, range.plan, DurableSyncAttemptState::active,
            *config_.sodium);
        if (!durable) {
          fail_job(*job, durable.status().message());
          if (first.ok()) first = durable.status();
          continue;
        }
        auto finished = job->attempt_store->finish(
            job->policy, durable.value(), *config_.identity,
            *config_.sodium,
            transaction.value());
        if (!finished) {
          fail_job(*job, finished.status().message());
          if (first.ok()) first = finished.status();
          continue;
        }
        range.journal_active = false;
      }
      const Status fenced =
          job->scheduler->fence_attempt(range.attempt_id);
      if (!fenced.ok()) {
        fail_job(*job, fenced.message());
        if (first.ok()) first = fenced;
        continue;
      }
      if (retained) {
        range.resume_offset = observed_bytes;
      } else {
        job->status.range_discarded_bytes =
            observed_bytes > std::numeric_limits<std::uint64_t>::max() -
                                 job->status.range_discarded_bytes
                ? std::numeric_limits<std::uint64_t>::max()
                : job->status.range_discarded_bytes + observed_bytes;
        range.resume_offset = 0U;
        range.staging_path.clear();
      }
      range.result_record.reset();
      range.result_offered = false;
      range.carrier_lost = true;
      job->status.detail = retained
          ? "auxiliary range carrier lost; exact prefix retained for replacement"
          : "auxiliary range carrier lost; replacement required from byte zero";
      continue;
    }
    if (!job->transfers) {
      fail_job(*job, "auxiliary object carrier has no transfer coordinator");
      if (first.ok()) {
        first = Status{ErrorCode::internal_error,
                       "auxiliary object carrier has no transfer coordinator"};
      }
      continue;
    }
    job->capacity_ready = false;
    job->admitted_capacity = 0U;
    for (ObjectLane &lane : job->lanes) {
      if (!lane.transport_admitted) lane.file_number.reset();
    }
    job->status.pending_offers = 0U;
    auto fenced = job->transfers->fence_route(
        carrier.route_key, carrier.worker_id, false,
        sync_route_reassignment_allowed(
            job->status.route_failover_policy));
    if (!fenced) {
      fail_job(*job, fenced.status().message());
      if (first.ok()) first = fenced.status();
      continue;
    }
    for (ObjectLane &lane : job->lanes) {
      lane.file_number.reset();
      lane.result_record.reset();
      lane.result_offered = false;
      lane.transport_admitted = false;
      lane.carrier_admission_lost = false;
    }
    job->status.detail = sync_route_reassignment_allowed(
                             job->status.route_failover_policy)
        ? "auxiliary carrier lost; old attempts fenced; replacement required"
        : job->range_mode
              ? "auxiliary prerequisite carrier lost; partial manifest discarded; fail-closed pull blocked"
              : "auxiliary carrier lost; partial objects discarded; fail-closed pull blocked";
  }
  return first;
}

std::vector<SyncPullSnapshot> SyncSubscriberService::snapshot() const {
  std::scoped_lock lock(mutex_);
  std::vector<SyncPullSnapshot> result;
  result.reserve(jobs_.size());
  for (const auto &job : jobs_) {
    SyncPullSnapshot snapshot = job->status;
    snapshot.cancellation_settled = job->cancellation_settled;
    snapshot.scheduler_attempt_bound = static_cast<std::size_t>(
        job->policy.quotas.maximum_outstanding_requests);
    if (job->scheduler) {
      snapshot.scheduler_attempts =
          job->scheduler->snapshot().attempts.size();
    }
    if (job->transfers) {
      const SyncTransferCoordinatorSnapshot transfers =
          job->transfers->snapshot();
      snapshot.retained_partials = transfers.retained_partials;
      snapshot.retained_attempts = transfers.retained_attempts;
      snapshot.retained_bytes = transfers.retained_bytes;
      snapshot.retention_fallbacks = transfers.retention_fallbacks;
      snapshot.resumed_attempts = transfers.resumed_attempts;
      snapshot.resumed_bytes = transfers.resumed_bytes;
      snapshot.restart_resumed_attempts =
          transfers.restart_resumed_attempts;
      snapshot.restart_resumed_bytes = transfers.restart_resumed_bytes;
    }
    snapshot.transfer_file_ids.reserve(
        job->lanes.size() + (job->range_lane ? 1U : 0U));
    for (const ObjectLane &lane : job->lanes) {
      snapshot.transfer_file_ids.push_back(lane.file_id);
    }
    if (job->range_lane) {
      if (!job->range_lane->carrier_lost) {
        snapshot.transfer_file_ids.push_back(job->range_lane->file_id);
      }
      snapshot.range_lane_active = !job->range_lane->committed;
      snapshot.range_attempt_id = job->range_lane->attempt_id;
      snapshot.range_message_id = job->range_lane->request_message_id;
      snapshot.range_bundle_bytes = job->range_lane->bundle_bytes;
    }
    result.push_back(std::move(snapshot));
  }
  return result;
}

} // namespace iotox::sync
