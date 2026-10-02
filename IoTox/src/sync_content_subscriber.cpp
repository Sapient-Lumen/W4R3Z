#include "iotox/sync_content_subscriber.hpp"

#include "iotox/sync_guarded_witness.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace iotox::sync {

struct SyncContentSubscriberService::Lane {
  DurableSyncContentAttempt durable;
  protocol::Frame request;
  std::filesystem::path staging_path;
  std::optional<std::vector<std::uint8_t>> result_record;
  std::optional<FileTransferRecord> offer;
  std::optional<std::uint32_t> file_number;
  bool root_manifest{false};
  bool transport_admitted{false};
};

struct SyncContentSubscriberService::Source {
  std::uint64_t source_id{0U};
  SyncPeerContext context;
  std::optional<protocol::Frame> availability_request;
  std::optional<std::vector<std::uint8_t>> availability_result_record;
  std::uint64_t requested_objects{0U};
  std::uint64_t committed_objects{0U};
  std::uint64_t fetched_bytes{0U};
};

struct SyncContentSubscriberService::PullJob {
  SyncContentPullSnapshot status;
  NamespacePolicy policy;
  SyncPeerContext context;
  protocol::Frame head_request;
  std::optional<std::vector<std::uint8_t>> head_result_record;
  std::optional<SignedHead> head;
  std::optional<CandidateHead> candidate;
  std::unique_ptr<SyncContentAttemptStore> attempts;
  std::unique_ptr<SyncContentCoordinator> coordinator;
  std::vector<Source> sources;
  std::vector<Lane> lanes;
  bool root_reused{false};
};

SyncContentSubscriberService::~SyncContentSubscriberService() = default;

namespace {

bool same_authority_session(const SyncPeerContext &left,
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
         right.peer_authority.remote_authorized &&
         right.content_transfer_negotiated;
}

bool same_authority(const SyncPeerContext &left,
                    const SyncPeerContext &right) noexcept {
  return same_authority_session(left, right) &&
         left.transfer_carrier == right.transfer_carrier;
}

AcceptedHead accepted_from(const CandidateHead &candidate) {
  return AcceptedHead{candidate.namespace_id,   candidate.writer,
                      candidate.engine,         candidate.generation,
                      candidate.record,         candidate.parent,
                      candidate.artifact,       candidate.manifest,
                      candidate.artifact_bytes, candidate.manifest_bytes};
}

bool zero_file_id(const FileId &file_id) {
  return std::all_of(file_id.begin(), file_id.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

} // namespace

std::string_view
sync_content_pull_state_name(SyncContentPullState state) noexcept {
  switch (state) {
  case SyncContentPullState::awaiting_head:
    return "awaiting-head";
  case SyncContentPullState::awaiting_objects:
    return "awaiting-objects";
  case SyncContentPullState::complete:
    return "complete";
  case SyncContentPullState::failed:
    return "failed";
  case SyncContentPullState::cancelled:
    return "cancelled";
  }
  return "unknown";
}

SyncContentSubscriberService::SyncContentSubscriberService(
    const NamespaceRegistry &namespaces, SyncContentSubscriberSeams seams,
    Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {
  if (config_.maximum_jobs > 0U && config_.maximum_jobs <= 1024U)
    jobs_.reserve(config_.maximum_jobs);
}

Status SyncContentSubscriberService::validate_config() const {
  if (namespaces_ == nullptr || !seams_.make_message_id ||
      !seams_.make_file_id || !seams_.receive_to_path ||
      !seams_.cancel_transfer || !seams_.retire_transfer ||
      config_.identity == nullptr || config_.sodium == nullptr ||
      config_.maximum_jobs == 0U || config_.maximum_jobs > 1024U ||
      config_.maximum_lanes == 0U ||
      config_.maximum_lanes > std::numeric_limits<std::uint16_t>::max() ||
      jobs_.capacity() < config_.maximum_jobs) {
    return Status{ErrorCode::invalid_argument,
                  "sync content subscriber configuration is invalid"};
  }
  return Status::success();
}

Status SyncContentSubscriberService::authorize_publish(
    const SyncPeerContext &context, const NamespacePolicy &policy) const {
  const Status valid = validate_sync_peer_context(context);
  if (!valid.ok())
    return valid;
  if (!context.content_transfer_negotiated) {
    return Status{ErrorCode::unsupported,
                  "sync content transfer was not negotiated"};
  }
  const SyncAuthorizationResult authorized =
      evaluate_sync_authorization(SyncOperation::publish, policy,
                                  context.authority, context.peer_authority);
  return authorized.authorized()
             ? Status::success()
             : Status{ErrorCode::protocol_error,
                      "remote peer is not an authorized content publisher"};
}

Result<SyncContentDispatch>
SyncContentSubscriberService::begin_pull(const SyncPeerContext &context,
                                         std::string_view namespace_id) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok())
    return configured;
  auto policy = namespaces_->resolve(namespace_id);
  if (!policy)
    return policy.status();
  if (policy.value().engine != Engine::content_v2) {
    return Status{ErrorCode::unsupported,
                  "content subscriber requires a content-v2 namespace"};
  }
  const Status authorized = authorize_publish(context, policy.value());
  if (!authorized.ok())
    return authorized;
  const auto existing =
      std::find_if(jobs_.begin(), jobs_.end(), [&](const auto &job) {
        return job->status.friend_number == context.friend_number &&
               job->status.online_epoch == context.online_epoch &&
               job->status.namespace_id == namespace_id;
      });
  if (existing != jobs_.end()) {
    if (!same_authority((*existing)->context, context)) {
      return Status{ErrorCode::unavailable,
                    "content publisher authority changed before retry"};
    }
    if ((*existing)->status.state == SyncContentPullState::awaiting_head)
      return SyncContentDispatch{context, (*existing)->head_request};
    if ((*existing)->status.state == SyncContentPullState::awaiting_objects) {
      return Status{ErrorCode::unavailable,
                    "content pull already has active object work"};
    }
    jobs_.erase(existing);
  }
  if (jobs_.size() >= config_.maximum_jobs) {
    return Status{ErrorCode::resource_exhausted,
                  "sync content subscriber job bound is exhausted"};
  }
  auto message_id = seams_.make_message_id();
  if (!message_id || message_id.value() == 0U) {
    return !message_id ? Result<SyncContentDispatch>{message_id.status()}
                       : Result<SyncContentDispatch>{Status{
                             ErrorCode::protocol_error,
                             "content HEAD message allocator returned zero"}};
  }
  auto request = make_sync_head_request_frame({std::string(namespace_id)},
                                              message_id.value());
  if (!request)
    return request.status();
  auto job = std::make_unique<PullJob>();
  job->status.job_id = message_id.value();
  job->status.friend_number = context.friend_number;
  job->status.online_epoch = context.online_epoch;
  job->status.namespace_id = std::string(namespace_id);
  job->status.detail = "content signed HEAD requested";
  job->status.primary_source_carrier = context.transfer_carrier;
  job->policy = std::move(policy).value();
  job->context = context;
  job->head_request = request.value();
  SyncContentAttemptStore::Config attempt_config;
  attempt_config.maximum_active_attempts =
      static_cast<std::size_t>(job->policy.quotas.maximum_outstanding_requests);
  job->attempts = std::make_unique<SyncContentAttemptStore>(job->policy.root,
                                                            attempt_config);
  job->sources.push_back(Source{message_id.value(), context, {}, {}});
  job->status.sources = 1U;
  jobs_.push_back(std::move(job));
  return SyncContentDispatch{context, request.value()};
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::retry_pull(const SyncPeerContext &context,
                                         std::string_view namespace_id) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok())
    return configured;
  auto policy = namespaces_->resolve(namespace_id);
  if (!policy)
    return policy.status();
  const Status authorized = authorize_publish(context, policy.value());
  if (!authorized.ok())
    return authorized;
  const auto found = std::find_if(
      jobs_.begin(), jobs_.end(), [&](const auto &job) {
        return job->status.friend_number == context.friend_number &&
               job->status.online_epoch == context.online_epoch &&
               job->status.namespace_id == namespace_id;
      });
  if (found == jobs_.end()) {
    return Status{ErrorCode::not_found, "content pull job is absent"};
  }
  PullJob &job = **found;
  if (!same_authority(job.context, context)) {
    return Status{ErrorCode::unavailable,
                  "content publisher authority changed before retry"};
  }
  if (job.status.state == SyncContentPullState::awaiting_head)
    return std::vector<SyncContentDispatch>{{job.context, job.head_request}};
  if (job.status.state == SyncContentPullState::awaiting_objects &&
      !job.lanes.empty()) {
    std::vector<SyncContentDispatch> requests;
    requests.reserve(job.lanes.size());
    for (const Lane &lane : job.lanes) {
      Source *source = source_for(job, lane.durable.source_id);
      if (source == nullptr) {
        return Status{ErrorCode::internal_error,
                      "content lane source is absent before retry"};
      }
      requests.push_back({source->context, lane.request});
    }
    return requests;
  }
  std::vector<SyncContentDispatch> pending;
  for (const Source &source : job.sources) {
    if (source.availability_request &&
        !source.availability_result_record) {
      pending.push_back({source.context, *source.availability_request});
    }
  }
  return pending;
}

Result<std::optional<SyncContentDispatch>>
SyncContentSubscriberService::make_root_request(PullJob &job) {
  if (!job.head || !job.candidate || !job.lanes.empty()) {
    return Status{ErrorCode::internal_error,
                  "content root request state is incomplete"};
  }
  auto transaction = SyncNamespaceTransaction::acquire(job.policy);
  if (!transaction)
    return transaction.status();
  auto attempt_id = job.attempts->reserve_attempt_id(
      job.policy, *config_.identity, *config_.sodium, transaction.value());
  if (!attempt_id)
    return attempt_id.status();
  auto message_id = seams_.make_message_id();
  auto file_id = seams_.make_file_id();
  if (!message_id || !file_id || message_id.value() == 0U ||
      zero_file_id(file_id.value())) {
    return !message_id
               ? Result<std::optional<SyncContentDispatch>>{
                     message_id.status()}
           : !file_id
               ? Result<std::optional<SyncContentDispatch>>{file_id.status()}
               : Result<std::optional<SyncContentDispatch>>{Status{
                     ErrorCode::protocol_error,
                     "content root allocator returned zero"}};
  }
  DurableSyncContentAttempt durable;
  durable.attempt_id = attempt_id.value();
  durable.request_id = message_id.value();
  durable.source_id = job.status.job_id;
  durable.head_record = job.candidate->record;
  durable.kind = SyncContentObjectKind::root_manifest;
  durable.logical_index = 0U;
  durable.object = job.head->manifest;
  durable.object_bytes = job.head->manifest_bytes;
  durable.file_id = file_id.value();
  Source *source = source_for(job, job.status.job_id);
  if (source == nullptr) {
    return Status{ErrorCode::internal_error,
                  "content primary source is absent before root request"};
  }
  durable.carrier = source->context.transfer_carrier;
  durable.source_principal =
      source->context.peer_authority.remote_principal;
  auto request = make_sync_content_object_request_frame(
      {job.policy.id, durable.kind, durable.head_record, durable.object,
       durable.file_id, durable.logical_index, durable.object_bytes},
      message_id.value());
  if (!request)
    return request.status();
  auto staging = prepare_sync_content_attempt_staging(
      job.policy, durable.object, durable.request_id, transaction.value());
  if (!staging)
    return staging.status();
  auto begun = job.attempts->begin(job.policy, durable, *config_.identity,
                                   *config_.sodium, transaction.value());
  if (!begun) {
    const Status discarded = discard_sync_content_attempt_staging(
        job.policy, durable, transaction.value());
    return discarded.ok() ? begun.status() : discarded;
  }
  job.lanes.push_back(
      Lane{durable, request.value(), staging.value(), {}, {}, {}, true, false});
  ++job.status.requested_objects;
  ++source->requested_objects;
  job.status.detail = "content root manifest requested";
  return std::optional<SyncContentDispatch>{
      SyncContentDispatch{source->context, request.value()}};
}

Status SyncContentSubscriberService::prepare_coordinator(PullJob &job) {
  if (!job.head || !job.candidate || job.coordinator) {
    return Status{ErrorCode::internal_error,
                  "content coordinator preparation state is invalid"};
  }
  const std::filesystem::path manifest =
      sync_content_object_path(job.policy, job.head->manifest);
  job.coordinator = std::make_unique<SyncContentCoordinator>(
      job.policy, accepted_from(*job.candidate), manifest,
      sync_content_store_root(job.policy),
      sync_content_staging_root(job.policy), config_.content);
  const Status prepared = job.coordinator->prepare();
  if (!prepared.ok()) {
    job.coordinator.reset();
    return prepared;
  }
  if (job.sources.size() != 1U)
    return Status::success();
  SyncContentSource source;
  source.source_id = job.sources.front().source_id;
  source.advertised_head_record = job.candidate->record;
  source.authority = job.sources.front().context.peer_authority;
  source.maximum_lanes = source_lane_limit(job);
  source.content_transfer_negotiated = true;
  return job.coordinator->upsert_complete_source(
      source, job.sources.front().context.authority);
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::prepare_after_head(PullJob &job) {
  auto root = resolve_sync_content_object(
      job.policy, *job.head, SyncContentObjectKind::root_manifest, 0U);
  if (!root && root.status().code() != ErrorCode::not_found)
    return root.status();
  if (!root) {
    auto request = make_root_request(job);
    if (!request)
      return request.status();
    return request.value()
               ? std::vector<SyncContentDispatch>{*request.value()}
               : std::vector<SyncContentDispatch>{};
  }
  job.root_reused = true;
  ++job.status.reused_objects;
  const Status prepared = prepare_coordinator(job);
  if (!prepared.ok())
    return prepared;
  return job.sources.size() == 1U ? drive(job) : request_availability(job);
}

SyncContentSubscriberService::Source *
SyncContentSubscriberService::source_for(PullJob &job,
                                          std::uint64_t source_id) noexcept {
  const auto found =
      std::find_if(job.sources.begin(), job.sources.end(),
                   [source_id](const Source &source) {
                     return source.source_id == source_id;
                   });
  return found == job.sources.end() ? nullptr : &*found;
}

std::uint16_t
SyncContentSubscriberService::source_lane_limit(const PullJob &job) const {
  const std::uint64_t bounded = std::min<std::uint64_t>(
      {static_cast<std::uint64_t>(config_.maximum_lanes),
       job.policy.quotas.maximum_lanes,
       job.policy.quotas.maximum_outstanding_requests,
       static_cast<std::uint64_t>(
           std::numeric_limits<std::uint16_t>::max())});
  return static_cast<std::uint16_t>(bounded);
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::add_source(std::uint64_t job_id,
                                         const SyncPeerContext &context) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok())
    return configured;
  const auto found =
      std::find_if(jobs_.begin(), jobs_.end(), [job_id](const auto &job) {
        return job->status.job_id == job_id;
      });
  if (found == jobs_.end())
    return Status{ErrorCode::not_found, "content pull job is absent"};
  PullJob &job = **found;
  if (job.status.state != SyncContentPullState::awaiting_head &&
      job.status.state != SyncContentPullState::awaiting_objects) {
    return Status{ErrorCode::unavailable,
                  "content pull no longer accepts sources"};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok())
    return authorized;
  const auto pending_requests = [&job] {
    std::vector<SyncContentDispatch> pending;
    for (const Source &source : job.sources) {
      if (source.availability_request &&
          !source.availability_result_record) {
        pending.push_back(
            {source.context, *source.availability_request});
      }
    }
    return pending;
  };
  const auto carrier_duplicate =
      std::find_if(job.sources.begin(), job.sources.end(),
                   [&context](const Source &source) {
                     return source.context.transfer_carrier ==
                            context.transfer_carrier;
                   });
  if (carrier_duplicate != job.sources.end()) {
    if (!same_authority(carrier_duplicate->context, context)) {
      return Status{ErrorCode::unavailable,
                    "content source carrier is already registered"};
    }
    return pending_requests();
  }
  const auto duplicate =
      std::find_if(job.sources.begin(), job.sources.end(),
                   [&context](const Source &source) {
                     return source.context.friend_number ==
                                context.friend_number &&
                            source.context.online_epoch == context.online_epoch;
                   });
  if (duplicate != job.sources.end()) {
    if (!same_authority_session(duplicate->context, context)) {
      return Status{ErrorCode::unavailable,
                    "content source authority changed within its epoch"};
    }
    if (duplicate->context.transfer_carrier.carrier_class !=
            SyncCarrierClass::auxiliary ||
        context.transfer_carrier.carrier_class !=
            SyncCarrierClass::auxiliary) {
      return Status{
          ErrorCode::invalid_argument,
          "same-session content source paths require auxiliary carriers"};
    }
  }
  if (job.sources.size() >= job.policy.quotas.maximum_peers) {
    return Status{ErrorCode::resource_exhausted,
                  "content source bound is exhausted"};
  }
  auto source_id = seams_.make_message_id();
  if (!source_id || source_id.value() == 0U) {
    return !source_id
               ? Result<std::vector<SyncContentDispatch>>{source_id.status()}
               : Result<std::vector<SyncContentDispatch>>{Status{
                     ErrorCode::protocol_error,
                     "content source allocator returned zero"}};
  }
  if (source_for(job, source_id.value()) != nullptr) {
    return Status{ErrorCode::protocol_error,
                  "content source allocator reused a live identifier"};
  }
  job.sources.push_back(Source{source_id.value(), context, {}, {}});
  job.status.sources = static_cast<std::uint32_t>(job.sources.size());
  job.status.detail = "content source added; frozen HEAD unchanged";
  if (!job.coordinator || !job.lanes.empty())
    return std::vector<SyncContentDispatch>{};
  auto requested = request_availability(job);
  if (!requested) {
    job.sources.pop_back();
    job.status.sources = static_cast<std::uint32_t>(job.sources.size());
  }
  return requested;
}

Status SyncContentSubscriberService::bind_source_carrier(
    std::uint64_t job_id, const SyncPeerContext &context) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok())
    return configured;
  const auto found =
      std::find_if(jobs_.begin(), jobs_.end(), [job_id](const auto &job) {
        return job->status.job_id == job_id;
      });
  if (found == jobs_.end())
    return Status{ErrorCode::not_found, "content pull job is absent"};
  PullJob &job = **found;
  if (job.status.state != SyncContentPullState::awaiting_head ||
      job.head_result_record || job.head || job.candidate || job.coordinator ||
      !job.lanes.empty()) {
    return Status{
        ErrorCode::unavailable,
        "content source carrier freezes before signed HEAD admission"};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok())
    return authorized;
  const auto source = std::find_if(
      job.sources.begin(), job.sources.end(), [&context](const Source &item) {
        return item.context.friend_number == context.friend_number &&
               item.context.online_epoch == context.online_epoch;
      });
  if (source == job.sources.end()) {
    return Status{ErrorCode::not_found,
                  "content source is not registered with this job"};
  }
  if (!same_authority_session(source->context, context)) {
    return Status{ErrorCode::unavailable,
                  "content source authority changed before carrier binding"};
  }
  if (context.transfer_carrier.carrier_class !=
      SyncCarrierClass::auxiliary) {
    return Status{ErrorCode::invalid_argument,
                  "content source carrier binding requires an auxiliary route"};
  }
  source->context = context;
  if (source->source_id == job.status.job_id)
    job.status.primary_source_carrier = context.transfer_carrier;
  job.status.detail =
      "content source bound to an exact auxiliary carrier; HEAD unchanged";
  return Status::success();
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::request_availability(PullJob &job) {
  if (!job.coordinator || !job.candidate || !job.lanes.empty() ||
      job.sources.size() < 2U) {
    return Status{ErrorCode::internal_error,
                  "content availability request state is invalid"};
  }
  const SyncContentSnapshot observed = job.coordinator->snapshot();
  if (observed.window_object_count == 0U ||
      observed.window_object_count > kSyncContentMaximumAvailabilityObjects) {
    return Status{ErrorCode::protocol_error,
                  "content coordinator exposed an invalid availability window"};
  }
  std::vector<protocol::Frame> frames;
  frames.reserve(job.sources.size());
  while (frames.size() < job.sources.size()) {
    auto message_id = seams_.make_message_id();
    if (!message_id || message_id.value() == 0U) {
      return !message_id
                 ? Result<std::vector<SyncContentDispatch>>{message_id.status()}
                 : Result<std::vector<SyncContentDispatch>>{Status{
                       ErrorCode::protocol_error,
                       "content availability allocator returned zero"}};
    }
    auto request = make_sync_content_availability_request_frame(
        {job.policy.id, observed.window_kind, job.candidate->record,
         observed.window_first_object, observed.window_object_count},
        message_id.value());
    if (!request)
      return request.status();
    frames.push_back(std::move(request).value());
  }
  std::vector<SyncContentDispatch> requests;
  requests.reserve(job.sources.size());
  for (std::size_t index = 0U; index < job.sources.size(); ++index) {
    Source &source = job.sources[index];
    source.availability_request = frames[index];
    source.availability_result_record.reset();
    requests.push_back({source.context, std::move(frames[index])});
  }
  job.status.availability_requests +=
      static_cast<std::uint64_t>(requests.size());
  job.status.detail = "exact sparse content availability requested";
  return requests;
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::handle_availability_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_content_availability_result_frame(frame);
  if (!valid.ok())
    return valid;
  PullJob *selected_job = nullptr;
  Source *selected_source = nullptr;
  for (const auto &owned : jobs_) {
    PullJob &job = *owned;
    for (Source &source : job.sources) {
      if (source.context.friend_number == context.friend_number &&
          source.context.online_epoch == context.online_epoch &&
          source.availability_request &&
          source.availability_request->message_id == frame.correlation_id) {
        selected_job = &job;
        selected_source = &source;
        break;
      }
    }
    if (selected_job != nullptr)
      break;
  }
  if (selected_job == nullptr || selected_source == nullptr) {
    return Status{ErrorCode::not_found,
                  "content availability result has no active request"};
  }
  PullJob &job = *selected_job;
  Source &source = *selected_source;
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(source.context, context)) {
    fail(job, "content source authority changed before availability result");
    return authorized.ok()
               ? Result<std::vector<SyncContentDispatch>>{Status{
                     ErrorCode::unavailable,
                     "content source authority changed"}}
               : Result<std::vector<SyncContentDispatch>>{authorized};
  }
  auto canonical = protocol::encode(frame);
  if (!canonical) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, canonical.status().message());
    return canonical.status();
  }
  if (source.availability_result_record) {
    if (*source.availability_result_record != canonical.value()) {
      fail(job, "content availability result replay conflicted");
      return Status{ErrorCode::protocol_error,
                    "content availability result replay conflicted"};
    }
    return std::vector<SyncContentDispatch>{};
  }
  auto decoded = decode_sync_content_availability_result(frame.payload);
  if (!decoded)
    return decoded.status();
  auto requested = decode_sync_content_availability_request(
      source.availability_request->payload);
  if (!requested)
    return requested.status();
  const SyncContentAvailabilityResult &result = decoded.value();
  if (result.status != SyncContentAvailabilityResultStatus::available ||
      result.kind != requested.value().kind ||
      result.head_record != requested.value().head_record ||
      result.first_object != requested.value().first_object ||
      result.object_count != requested.value().object_count) {
    fail(job, "content source did not prove exact sparse availability");
    return Status{ErrorCode::unavailable,
                  "content source did not prove exact sparse availability"};
  }
  SyncContentSource admitted;
  admitted.source_id = source.source_id;
  admitted.advertised_head_record = result.head_record;
  admitted.authority = source.context.peer_authority;
  admitted.maximum_lanes = source_lane_limit(job);
  admitted.content_transfer_negotiated = true;
  const Status installed = job.coordinator->upsert_source_window(
      admitted, source.context.authority, result.kind, result.first_object,
      result.object_count, result.availability);
  if (!installed.ok()) {
    fail(job, installed.message());
    return installed;
  }
  source.availability_result_record = canonical.value();
  ++job.status.availability_results;
  const bool waiting =
      std::any_of(job.sources.begin(), job.sources.end(), [](const Source &item) {
        return item.availability_request &&
               !item.availability_result_record;
      });
  if (waiting)
    return std::vector<SyncContentDispatch>{};
  return drive(job);
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::handle_head_result(const SyncPeerContext &context,
                                                 const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_head_result_frame(frame);
  if (!valid.ok())
    return valid;
  const auto found = std::find_if(
      jobs_.begin(), jobs_.end(), [&context, &frame](const auto &job) {
        return job->status.friend_number == context.friend_number &&
               job->status.online_epoch == context.online_epoch &&
               job->head_request.message_id == frame.correlation_id;
      });
  if (found == jobs_.end()) {
    return Status{ErrorCode::not_found,
                  "content HEAD result has no active pull"};
  }
  PullJob &job = **found;
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(job.context, context)) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content publisher authority changed before HEAD result");
    return authorized.ok() ? Status{ErrorCode::unavailable,
                                    "content publisher authority changed"}
                           : authorized;
  }
  auto canonical = protocol::encode(frame);
  if (!canonical) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, canonical.status().message());
    return canonical.status();
  }
  if (job.head_result_record) {
    if (*job.head_result_record != canonical.value()) {
      static_cast<void>(settle_all_lanes(
          job, LaneTransportDisposition::cancel,
          SyncContentFailure::permanent));
      fail(job, "content HEAD result replay conflicted");
      return Status{ErrorCode::protocol_error,
                    "content HEAD result replay conflicted"};
    }
    if (job.lanes.empty())
      return std::vector<SyncContentDispatch>{};
    std::vector<SyncContentDispatch> requests;
    requests.reserve(job.lanes.size());
    for (const Lane &lane : job.lanes) {
      Source *source = source_for(job, lane.durable.source_id);
      if (source == nullptr) {
        static_cast<void>(settle_all_lanes(
            job, LaneTransportDisposition::cancel,
            SyncContentFailure::permanent));
        fail(job, "content replay lane source is absent");
        return Status{ErrorCode::internal_error,
                      "content replay lane source is absent"};
      }
      requests.push_back({source->context, lane.request});
    }
    return requests;
  }
  if (job.status.state != SyncContentPullState::awaiting_head) {
    return std::vector<SyncContentDispatch>{};
  }
  auto decoded = decode_sync_head_result(frame.payload);
  if (!decoded || decoded.value().status != SyncHeadResultStatus::available ||
      !decoded.value().head) {
    fail(job, "publisher did not provide a content signed HEAD");
    return decoded
               ? Result<std::vector<SyncContentDispatch>>{
                     std::vector<SyncContentDispatch>{}}
               : Result<std::vector<SyncContentDispatch>>{decoded.status()};
  }
  auto candidate = verified_candidate_head(job.policy, *decoded.value().head,
                                           *config_.sodium);
  if (!candidate ||
      decoded.value().head->writer != context.peer_authority.remote_principal) {
    const Status refused =
        !candidate ? candidate.status()
                   : Status{ErrorCode::protocol_error,
                            "content HEAD writer is not the proven publisher"};
    fail(job, refused.message());
    return refused;
  }
  Result<std::shared_ptr<SyncGuardedStateWitness>> witness{
      std::shared_ptr<SyncGuardedStateWitness>{}};
  if (config_.guarded_state_witness) {
    witness = config_.guarded_state_witness(job.policy);
    if (!witness) {
      fail(job, witness.status().message());
      return witness.status();
    }
  }
  HeadAcceptanceResult evaluated;
  {
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) {
      fail(job, transaction.status().message());
      return transaction.status();
    }
    if (witness.value()) {
      const Status verified = witness.value()->verify_read(
          job.policy, transaction.value());
      if (!verified.ok()) {
        fail(job, verified.message());
        return verified;
      }
    }
    AcceptedHeadStore accepted(job.policy.root, witness.value());
    auto current = accepted.load(job.policy, config_.identity->public_key(),
                                 *config_.sodium);
    if (!current) {
      fail(job, current.status().message());
      return current.status();
    }
    evaluated = evaluate_candidate_head(
        job.policy, candidate.value(), current.value());
  }
  if (!evaluated.accepted() &&
      evaluated.decision != HeadAcceptanceDecision::duplicate) {
    fail(job, "content signed HEAD transition was refused");
    return std::vector<SyncContentDispatch>{};
  }
  job.head_result_record = canonical.value();
  job.head = *decoded.value().head;
  job.candidate = candidate.value();
  job.status.state = SyncContentPullState::awaiting_objects;
  job.status.head_generation = job.head->generation;
  job.status.head_record = job.candidate->record;
  auto requests = prepare_after_head(job);
  if (!requests)
    fail(job, requests.status().message());
  return requests;
}

Status SyncContentSubscriberService::handle_object_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
  std::scoped_lock lock(mutex_);
  const Status valid = validate_sync_content_object_result_frame(frame);
  if (!valid.ok())
    return valid;
  auto decoded = decode_sync_content_object_result(frame.payload);
  if (!decoded)
    return decoded.status();
  PullJob *selected_job = nullptr;
  std::size_t selected_lane = 0U;
  for (const auto &owned : jobs_) {
    PullJob &job = *owned;
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
      Lane &lane = job.lanes[index];
      Source *source = source_for(job, lane.durable.source_id);
      if (lane.request.message_id == frame.correlation_id &&
          source != nullptr &&
          source->context.friend_number == context.friend_number &&
          source->context.online_epoch == context.online_epoch) {
        selected_job = &job;
        selected_lane = index;
        break;
      }
    }
    if (selected_job != nullptr)
      break;
  }
  if (selected_job == nullptr) {
    return Status{ErrorCode::not_found,
                  "content object result has no active request"};
  }
  PullJob &job = *selected_job;
  Lane &lane = job.lanes[selected_lane];
  Source *source = source_for(job, lane.durable.source_id);
  if (source == nullptr) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content lane source is absent");
    return Status{ErrorCode::internal_error,
                  "content lane source is absent"};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(source->context, context)) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content source authority changed before object result");
    return authorized.ok() ? Status{ErrorCode::unavailable,
                                    "content source authority changed"}
                           : authorized;
  }
  const DurableSyncContentAttempt &expected = lane.durable;
  if (decoded.value().kind != expected.kind ||
      decoded.value().head_record != expected.head_record ||
      decoded.value().object != expected.object ||
      decoded.value().transfer_id != expected.file_id ||
      decoded.value().logical_index != expected.logical_index ||
      decoded.value().object_bytes != expected.object_bytes) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content object result identity changed");
    return Status{ErrorCode::protocol_error,
                  "content object result identity changed"};
  }
  auto canonical = protocol::encode(frame);
  if (!canonical) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, canonical.status().message());
    return canonical.status();
  }
  if (lane.result_record && *lane.result_record != canonical.value()) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content object result replay conflicted");
    return Status{ErrorCode::protocol_error,
                  "content object result replay conflicted"};
  }
  lane.result_record = canonical.value();
  if (decoded.value().status != SyncContentObjectResultStatus::offered) {
    const Status settled = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        decoded.value().status == SyncContentObjectResultStatus::object_absent
            ? SyncContentFailure::object_absent
            : SyncContentFailure::permanent);
    fail(job, "publisher refused a content object");
    return settled;
  }
  return lane.offer ? admit_offer(job, lane) : Status::success();
}

Status SyncContentSubscriberService::admit_offer(PullJob &job, Lane &lane) {
  if (!lane.offer || !lane.result_record) {
    return Status{ErrorCode::internal_error,
                  "content offer admission state is incomplete"};
  }
  Source *source = source_for(job, lane.durable.source_id);
  if (source == nullptr) {
    return Status{ErrorCode::internal_error,
                  "content offer source is absent"};
  }
  const FileTransferRecord &offer = *lane.offer;
  if (lane.transport_admitted)
    return Status::success();
  auto accepted = seams_.receive_to_path(source->context.transfer_carrier,
                                         offer.file_number, lane.staging_path);
  if (!accepted) {
    if (accepted.status().code() == ErrorCode::resource_exhausted) {
      job.status.detail =
          "content offer retained behind the local receive ceiling";
      return Status::success();
    }
    const Status failure = accepted.status();
    const Status settled = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent);
    fail(job, failure.message());
    return settled.ok() ? failure : settled;
  }
  if (accepted.value().direction != FileTransferDirection::incoming ||
      accepted.value().friend_number != offer.friend_number ||
      accepted.value().file_number != offer.file_number ||
      accepted.value().file_size != offer.file_size ||
      accepted.value().local_path != lane.staging_path) {
    static_cast<void>(seams_.cancel_transfer(source->context.transfer_carrier,
                                             offer.file_number));
    const Status failure{ErrorCode::protocol_error,
                         "content receive admission changed its exact binding"};
    const Status settled = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent);
    fail(job, failure.message());
    return settled.ok() ? failure : settled;
  }
  lane.transport_admitted = true;
  job.status.detail = job.lanes.size() == 1U
                          ? "receiving one verified content object"
                          : "receiving verified content objects concurrently";
  return Status::success();
}

Result<bool>
SyncContentSubscriberService::handle_offer(const SyncPeerContext &context,
                                           const FileTransferRecord &offer) {
  std::scoped_lock lock(mutex_);
  if (offer.direction != FileTransferDirection::incoming || !offer.has_file_id)
    return false;
  PullJob *selected_job = nullptr;
  std::size_t selected_lane = 0U;
  for (const auto &owned : jobs_) {
    PullJob &job = *owned;
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
      Lane &lane = job.lanes[index];
      Source *source = source_for(job, lane.durable.source_id);
      if (lane.durable.file_id == offer.file_id && source != nullptr &&
          source->context.friend_number == context.friend_number &&
          source->context.online_epoch == context.online_epoch) {
        selected_job = &job;
        selected_lane = index;
        break;
      }
    }
    if (selected_job != nullptr)
      break;
  }
  if (selected_job == nullptr)
    return false;
  PullJob &job = *selected_job;
  Lane &lane = job.lanes[selected_lane];
  Source *source = source_for(job, lane.durable.source_id);
  if (source == nullptr) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content offer source is absent");
    return Status{ErrorCode::internal_error,
                  "content offer source is absent"};
  }
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(source->context, context)) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content source authority changed before file offer");
    return authorized.ok()
               ? Result<bool>{Status{ErrorCode::unavailable,
                                     "content source authority changed"}}
               : Result<bool>{authorized};
  }
  if (offer.friend_number != context.transfer_carrier.friend_number ||
      offer.file_size != lane.durable.object_bytes) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content file offer size or peer changed");
    return Status{ErrorCode::protocol_error,
                  "content file offer size or peer changed"};
  }
  if (lane.file_number && *lane.file_number != offer.file_number) {
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content FileId was reused by another file number");
    return Status{ErrorCode::protocol_error,
                  "content FileId was reused by another file number"};
  }
  if (lane.transport_admitted)
    return true;
  lane.offer = offer;
  lane.file_number = offer.file_number;
  if (!lane.result_record) {
    job.status.detail = "content offer retained until its exact result arrives";
    return true;
  }
  const Status admitted = admit_offer(job, lane);
  if (!admitted.ok())
    return admitted;
  return true;
}

Status SyncContentSubscriberService::settle_lane(
    PullJob &job, std::size_t lane_index,
    LaneTransportDisposition transport, SyncContentFailure failure) {
  if (lane_index >= job.lanes.size())
    return Status::success();
  Lane &lane = job.lanes[lane_index];
  Source *source = source_for(job, lane.durable.source_id);
  Status first = Status::success();
  if (lane.file_number && transport != LaneTransportDisposition::none) {
    const Status transport_status =
        source == nullptr
            ? Status{ErrorCode::internal_error,
                     "content lane source is absent"}
            : transport == LaneTransportDisposition::retire
                  ? seams_.retire_transfer(source->context.transfer_carrier,
                                           *lane.file_number)
                  : seams_.cancel_transfer(source->context.transfer_carrier,
                                           *lane.file_number);
    if (!transport_status.ok())
      first = transport_status;
  }
  if (!lane.root_manifest && job.coordinator) {
    const Status fenced =
        job.coordinator->fail(lane.durable.request_id, failure);
    if (!fenced.ok() && first.ok())
      first = fenced;
  }
  auto transaction = SyncNamespaceTransaction::acquire(job.policy);
  if (!transaction)
    return first.ok() ? transaction.status() : first;
  const Status discarded = discard_sync_content_attempt_staging(
      job.policy, lane.durable, transaction.value());
  if (!discarded.ok() && first.ok())
    first = discarded;
  if (discarded.ok()) {
    auto finished =
        job.attempts->finish(job.policy, lane.durable, *config_.identity,
                             *config_.sodium, transaction.value());
    if (!finished && first.ok())
      first = finished.status();
  }
  if (first.ok()) {
    job.lanes.erase(job.lanes.begin() +
                    static_cast<std::ptrdiff_t>(lane_index));
  }
  return first;
}

Status SyncContentSubscriberService::settle_all_lanes(
    PullJob &job, LaneTransportDisposition transport,
    SyncContentFailure failure,
    const std::optional<SyncTransferCarrier> &retired_carrier) {
  Status first = Status::success();
  for (std::size_t remaining = job.lanes.size(); remaining > 0U;
       --remaining) {
    const std::size_t index = remaining - 1U;
    const LaneTransportDisposition disposition =
        retired_carrier && job.lanes[index].durable.carrier == *retired_carrier
            ? LaneTransportDisposition::retire
            : transport;
    const Status settled = settle_lane(job, index, disposition, failure);
    if (!settled.ok() && first.ok())
      first = settled;
  }
  return first;
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::drive(PullJob &job) {
  if (!job.coordinator || !job.head || !job.candidate ||
      std::any_of(job.lanes.begin(), job.lanes.end(),
                  [](const Lane &lane) { return lane.root_manifest; })) {
    return Status{ErrorCode::internal_error,
                  "content subscriber drive state is invalid"};
  }
  if (job.sources.size() > 1U &&
      std::any_of(job.sources.begin(), job.sources.end(),
                  [](const Source &source) {
                    return !source.availability_request ||
                           !source.availability_result_record;
                  })) {
    return request_availability(job);
  }
  const auto abort_active = [this, &job](Status failure)
      -> Result<std::vector<SyncContentDispatch>> {
    const Status settled = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent);
    return settled.ok()
               ? Result<std::vector<SyncContentDispatch>>{std::move(failure)}
               : Result<std::vector<SyncContentDispatch>>{settled};
  };
  std::vector<SyncContentDispatch> requests;
  requests.reserve(source_lane_limit(job));
  const std::uint64_t loop_bound =
      std::min<std::uint64_t>(job.policy.quotas.maximum_objects, 65536U) + 2U;
  for (std::uint64_t step = 0U; step < loop_bound; ++step) {
    const SyncContentSnapshot observed = job.coordinator->snapshot();
    job.status.phase = observed.phase;
    job.status.reused_objects = observed.page_objects_reused +
                                observed.chunk_objects_reused +
                                (job.root_reused ? 1U : 0U);
    if (job.coordinator->complete()) {
      Result<std::shared_ptr<SyncGuardedStateWitness>> witness{
          std::shared_ptr<SyncGuardedStateWitness>{}};
      if (config_.guarded_state_witness) {
        witness = config_.guarded_state_witness(job.policy);
        if (!witness) return witness.status();
      }
      auto accepted = reconstruct_and_accept_sync_content_revision(
          job.policy, *job.head, *job.coordinator, *config_.identity,
          *config_.sodium, config_.acceptance,
          SyncContentAcceptanceSeams{{}, witness.value()});
      if (!accepted)
        return accepted.status();
      job.status.state = SyncContentPullState::complete;
      job.status.phase = SyncContentPhase::complete;
      job.status.detail =
          "content artifact reconstructed; signed HEAD accepted; not activated";
      return requests;
    }
    if (job.lanes.size() >= source_lane_limit(job))
      return requests;
    auto message_id = seams_.make_message_id();
    if (!message_id || message_id.value() == 0U) {
      return abort_active(
          !message_id
              ? message_id.status()
              : Status{ErrorCode::protocol_error,
                       "content object message allocator returned zero"});
    }
    auto assignment = job.coordinator->next(message_id.value());
    if (!assignment)
      return abort_active(assignment.status());
    if (!assignment.value()) {
      if (job.coordinator->snapshot().active_requests != 0U)
        return requests;
      auto advanced = job.coordinator->advance_window();
      if (!advanced)
        return abort_active(advanced.status());
      if (!advanced.value() && !job.coordinator->complete()) {
        return abort_active(
            Status{ErrorCode::unavailable,
                   "content source cannot satisfy the current window"});
      }
      if (advanced.value() && !job.coordinator->complete() &&
          job.sources.size() > 1U) {
        if (!requests.empty()) {
          return abort_active(Status{
              ErrorCode::internal_error,
              "content window advanced with newly active requests"});
        }
        return request_availability(job);
      }
      continue;
    }
    const SyncContentAssignment &assigned = *assignment.value();
    Source *source = source_for(job, assigned.source_id);
    if (source == nullptr) {
      static_cast<void>(job.coordinator->fail(
          assigned.request_id, SyncContentFailure::permanent));
      return abort_active(
          Status{ErrorCode::internal_error,
                 "content assignment named an absent source"});
    }
    std::uint64_t attempt_id_value = 0U;
    {
      auto transaction = SyncNamespaceTransaction::acquire(job.policy);
      if (!transaction) {
        static_cast<void>(job.coordinator->fail(
            assigned.request_id, SyncContentFailure::permanent));
        return abort_active(transaction.status());
      }
      auto attempt_id = job.attempts->reserve_attempt_id(
          job.policy, *config_.identity, *config_.sodium, transaction.value());
      if (!attempt_id) {
        static_cast<void>(job.coordinator->fail(
            assigned.request_id, SyncContentFailure::permanent));
        return abort_active(attempt_id.status());
      }
      attempt_id_value = attempt_id.value();
    }
    auto file_id = seams_.make_file_id();
    if (!file_id || zero_file_id(file_id.value())) {
      static_cast<void>(job.coordinator->fail(
          assigned.request_id, SyncContentFailure::permanent));
      return abort_active(
          !file_id
              ? file_id.status()
              : Status{ErrorCode::protocol_error,
                       "content object FileId allocator returned zero"});
    }
    DurableSyncContentAttempt durable;
    durable.attempt_id = attempt_id_value;
    durable.request_id = assigned.request_id;
    durable.source_id = assigned.source_id;
    durable.head_record = job.candidate->record;
    durable.kind = assigned.kind;
    durable.logical_index = assigned.logical_index;
    durable.object = assigned.object;
    durable.object_bytes = assigned.object_bytes;
    durable.file_id = file_id.value();
    durable.carrier = source->context.transfer_carrier;
    durable.source_principal =
        source->context.peer_authority.remote_principal;
    auto request = make_sync_content_object_request_frame(
        {job.policy.id, durable.kind, durable.head_record, durable.object,
         durable.file_id, durable.logical_index, durable.object_bytes},
        message_id.value());
    if (!request) {
      static_cast<void>(job.coordinator->fail(assigned.request_id,
                                              SyncContentFailure::permanent));
      return abort_active(request.status());
    }
    auto next_transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!next_transaction) {
      static_cast<void>(job.coordinator->fail(assigned.request_id,
                                              SyncContentFailure::permanent));
      return abort_active(next_transaction.status());
    }
    auto staging = prepare_sync_content_attempt_staging(
        job.policy, durable.object, durable.request_id,
        next_transaction.value());
    if (!staging || staging.value() != assigned.staging_path) {
      static_cast<void>(job.coordinator->fail(assigned.request_id,
                                              SyncContentFailure::permanent));
      return abort_active(
          !staging
              ? staging.status()
              : Status{ErrorCode::protocol_error,
                       "content coordinator staging identity changed"});
    }
    auto begun = job.attempts->begin(job.policy, durable, *config_.identity,
                                     *config_.sodium, next_transaction.value());
    if (!begun) {
      static_cast<void>(job.coordinator->fail(assigned.request_id,
                                              SyncContentFailure::permanent));
      const Status discarded = discard_sync_content_attempt_staging(
          job.policy, durable, next_transaction.value());
      return abort_active(discarded.ok() ? begun.status() : discarded);
    }
    job.lanes.push_back(Lane{
        durable, request.value(), staging.value(), {}, {}, {}, false, false});
    ++job.status.requested_objects;
    ++source->requested_objects;
    job.status.detail = job.lanes.size() == 1U
                            ? "content page/chunk requested"
                            : "content page/chunk lanes requested";
    requests.push_back({source->context, request.value()});
  }
  return abort_active(
      Status{ErrorCode::resource_exhausted,
             "content coordinator drive loop exceeded policy bounds"});
}

Result<std::vector<SyncContentDispatch>>
SyncContentSubscriberService::handle_terminal(
    const SyncPeerContext &context, const FileTransferRecord &transfer,
    routes::WorkerTransferOutcome outcome, ErrorCode failure) {
  std::scoped_lock lock(mutex_);
  PullJob *selected_job = nullptr;
  std::size_t selected_lane = 0U;
  for (const auto &owned : jobs_) {
    PullJob &job = *owned;
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
      Lane &lane = job.lanes[index];
      Source *source = source_for(job, lane.durable.source_id);
      if (lane.file_number && *lane.file_number == transfer.file_number &&
          source != nullptr && same_authority(source->context, context)) {
        selected_job = &job;
        selected_lane = index;
        break;
      }
    }
    if (selected_job != nullptr)
      break;
  }
  if (selected_job == nullptr) {
    return Status{ErrorCode::not_found,
                  "content terminal has no active binding"};
  }
  PullJob &job = *selected_job;
  Lane &lane = job.lanes[selected_lane];
  Source *source = source_for(job, lane.durable.source_id);
  if (source == nullptr) {
    const Status terminal_failure{ErrorCode::internal_error,
                                  "content terminal source is absent"};
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, terminal_failure.message());
    return terminal_failure;
  }
  const auto abort_terminal =
      [this, &job, selected_lane](Status terminal_failure)
      -> Result<std::vector<SyncContentDispatch>> {
    const Status selected = settle_lane(
        job, selected_lane, LaneTransportDisposition::none,
        SyncContentFailure::permanent);
    const Status remaining = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent);
    fail(job, terminal_failure.message());
    if (!selected.ok())
      return selected;
    if (!remaining.ok())
      return remaining;
    return terminal_failure;
  };
  const Status authorized = authorize_publish(context, job.policy);
  if (!authorized.ok() || !same_authority(source->context, context)) {
    static_cast<void>(settle_lane(
        job, selected_lane, LaneTransportDisposition::none,
        SyncContentFailure::permanent));
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content source authority changed before object commit");
    return authorized.ok() ? Status{ErrorCode::unavailable,
                                    "content source authority changed"}
                           : authorized;
  }
  if (!lane.result_record || !lane.transport_admitted) {
    static_cast<void>(settle_lane(
        job, selected_lane, LaneTransportDisposition::none,
        SyncContentFailure::permanent));
    static_cast<void>(settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent));
    fail(job, "content terminal arrived before exact result admission");
    return Status{ErrorCode::protocol_error,
                  "content terminal arrived before exact result admission"};
  }
  const bool complete =
      outcome == routes::WorkerTransferOutcome::completed &&
      failure == ErrorCode::ok &&
      transfer.direction == FileTransferDirection::incoming &&
      transfer.friend_number == context.transfer_carrier.friend_number &&
      transfer.file_size == lane.durable.object_bytes &&
      transfer.local_path == lane.staging_path;
  if (!complete) {
    const Status settled = settle_lane(
        job, selected_lane, LaneTransportDisposition::none,
        SyncContentFailure::permanent);
    const Status remaining = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent);
    fail(job, "content file transfer did not complete exactly");
    const Status cleanup = settled.ok() ? remaining : settled;
    return cleanup.ok()
               ? Result<std::vector<SyncContentDispatch>>{
                     std::vector<SyncContentDispatch>{}}
               : Result<std::vector<SyncContentDispatch>>{cleanup};
  }
  const bool root = lane.root_manifest;
  const DurableSyncContentAttempt durable = lane.durable;
  if (root) {
    {
      auto transaction = SyncNamespaceTransaction::acquire(job.policy);
      if (!transaction)
        return abort_terminal(transaction.status());
      SyncContentCommitConfig commit;
      commit.io_buffer_bytes = config_.acceptance.io_buffer_bytes;
      commit.fsync_on_commit = config_.acceptance.fsync_on_commit;
      auto committed = commit_sync_content_staging(
          job.policy, durable.object, durable.object_bytes, lane.staging_path,
          transaction.value(), commit);
      if (!committed) {
        return abort_terminal(committed.status());
      }
      auto finished =
          job.attempts->finish(job.policy, durable, *config_.identity,
                               *config_.sodium, transaction.value());
      if (!finished) {
        return abort_terminal(finished.status());
      }
    }
    ++job.status.committed_objects;
    job.status.fetched_bytes += durable.object_bytes;
    ++source->committed_objects;
    source->fetched_bytes += durable.object_bytes;
    job.lanes.erase(job.lanes.begin() +
                    static_cast<std::ptrdiff_t>(selected_lane));
    const Status prepared = prepare_coordinator(job);
    if (!prepared.ok()) {
      fail(job, prepared.message());
      return prepared;
    }
  } else {
    const Status committed =
        job.coordinator->commit(durable.request_id, lane.staging_path);
    if (!committed.ok()) {
      return abort_terminal(committed);
    }
    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction)
      return abort_terminal(transaction.status());
    auto finished = job.attempts->finish(job.policy, durable, *config_.identity,
                                         *config_.sodium, transaction.value());
    if (!finished) {
      return abort_terminal(finished.status());
    }
    ++job.status.committed_objects;
    job.status.fetched_bytes += durable.object_bytes;
    ++source->committed_objects;
    source->fetched_bytes += durable.object_bytes;
    job.lanes.erase(job.lanes.begin() +
                    static_cast<std::ptrdiff_t>(selected_lane));
  }
  for (Lane &pending : job.lanes) {
    if (pending.offer && pending.result_record &&
        !pending.transport_admitted) {
      const Status admitted = admit_offer(job, pending);
      if (!admitted.ok()) {
        static_cast<void>(settle_all_lanes(
            job, LaneTransportDisposition::cancel,
            SyncContentFailure::permanent));
        fail(job, admitted.message());
        return admitted;
      }
    }
  }
  auto requests = drive(job);
  if (!requests)
    fail(job, requests.status().message());
  return requests;
}

Status SyncContentSubscriberService::cancel_pull(std::uint64_t job_id) {
  std::scoped_lock lock(mutex_);
  const auto found =
      std::find_if(jobs_.begin(), jobs_.end(), [job_id](const auto &job) {
        return job->status.job_id == job_id;
      });
  if (found == jobs_.end()) {
    return Status{ErrorCode::not_found, "content pull job is absent"};
  }
  PullJob &job = **found;
  if (job.status.state == SyncContentPullState::complete ||
      job.status.state == SyncContentPullState::failed ||
      job.status.state == SyncContentPullState::cancelled) {
    return Status::success();
  }
  const Status settled = settle_all_lanes(
      job, LaneTransportDisposition::cancel,
      SyncContentFailure::permanent);
  if (!settled.ok())
    return settled;
  job.status.state = SyncContentPullState::cancelled;
  job.status.detail = "content pull cancelled and fenced";
  return Status::success();
}

void SyncContentSubscriberService::peer_offline(std::uint32_t friend_number,
                                                std::uint64_t online_epoch) {
  std::scoped_lock lock(mutex_);
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    const bool registered =
        std::any_of(job.sources.begin(), job.sources.end(),
                    [friend_number, online_epoch](const Source &source) {
                      return source.context.friend_number == friend_number &&
                             source.context.online_epoch == online_epoch;
                    });
    if (!registered ||
        (job.status.state != SyncContentPullState::awaiting_head &&
         job.status.state != SyncContentPullState::awaiting_objects)) {
      continue;
    }
    Status settled = Status::success();
    for (std::size_t remaining = job.lanes.size(); remaining > 0U;
         --remaining) {
      const std::size_t index = remaining - 1U;
      const SyncTransferCarrier &lane_carrier =
          job.lanes[index].durable.carrier;
      const bool primary_went_offline =
          lane_carrier.carrier_class == SyncCarrierClass::primary &&
          lane_carrier.friend_number == friend_number &&
          lane_carrier.online_epoch == online_epoch;
      const Status lane_settled = settle_lane(
          job, index,
          primary_went_offline ? LaneTransportDisposition::retire
                               : LaneTransportDisposition::cancel,
          SyncContentFailure::permanent);
      if (!lane_settled.ok() && settled.ok())
        settled = lane_settled;
    }
    fail(job,
         settled.ok() ? "registered content source went offline"
                      : settled.message());
  }
}

void SyncContentSubscriberService::carrier_offline(
    const SyncTransferCarrier &carrier) {
  std::scoped_lock lock(mutex_);
  for (auto &owned : jobs_) {
    PullJob &job = *owned;
    const bool registered =
        std::any_of(job.sources.begin(), job.sources.end(),
                    [&carrier](const Source &source) {
                      return source.context.transfer_carrier == carrier;
                    });
    if (!registered ||
        (job.status.state != SyncContentPullState::awaiting_head &&
         job.status.state != SyncContentPullState::awaiting_objects)) {
      continue;
    }
    const Status settled = settle_all_lanes(
        job, LaneTransportDisposition::cancel,
        SyncContentFailure::permanent, carrier);
    fail(job, settled.ok()
                  ? "exact auxiliary content carrier went offline"
                  : settled.message());
  }
}

void SyncContentSubscriberService::fail(PullJob &job,
                                        std::string detail) noexcept {
  job.status.state = SyncContentPullState::failed;
  job.status.detail = std::move(detail);
}

std::vector<SyncContentPullSnapshot>
SyncContentSubscriberService::snapshot() const {
  std::scoped_lock lock(mutex_);
  std::vector<SyncContentPullSnapshot> result;
  result.reserve(jobs_.size());
  for (const auto &job : jobs_) {
    SyncContentPullSnapshot observed = job->status;
    observed.active_lanes = static_cast<std::uint32_t>(job->lanes.size());
    observed.lane_bindings.reserve(job->lanes.size());
    for (const Lane &lane : job->lanes) {
      observed.lane_bindings.push_back(SyncContentLaneSnapshot{
          lane.durable.request_id,
          lane.durable.source_id,
          lane.durable.kind,
          lane.durable.logical_index,
          lane.durable.object_bytes,
          lane.durable.file_id,
          lane.file_number,
          lane.durable.carrier,
          lane.root_manifest,
          lane.transport_admitted,
      });
    }
    if (job->lanes.size() == 1U) {
      observed.active_file_id = job->lanes.front().durable.file_id;
      observed.active_file_number = job->lanes.front().file_number;
    } else {
      observed.active_file_id.reset();
      observed.active_file_number.reset();
    }
    observed.source_carriers.reserve(job->sources.size());
    for (const Source &source : job->sources) {
      observed.source_carriers.push_back(SyncContentSourceSnapshot{
          source.source_id,
          source.context.friend_number,
          source.context.online_epoch,
          source.context.peer_authority.remote_principal,
          source.context.authority_route_key,
          source.context.transfer_carrier,
          source.requested_objects,
          source.committed_objects,
          source.fetched_bytes,
      });
    }
    result.push_back(std::move(observed));
  }
  return result;
}

} // namespace iotox::sync
