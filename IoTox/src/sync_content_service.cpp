#include "iotox/sync_content_service.hpp"

#include <algorithm>
#include <utility>

namespace iotox::sync {

SyncContentPublisherService::SyncContentPublisherService(
    const NamespaceRegistry &namespaces, SyncContentPublisherSeams seams)
    : SyncContentPublisherService(namespaces, std::move(seams), Config{}) {}

SyncContentPublisherService::SyncContentPublisherService(
    const NamespaceRegistry &namespaces, SyncContentPublisherSeams seams,
    Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {}

Status SyncContentPublisherService::validate_config() const {
  if (namespaces_ == nullptr || !seams_.load_head ||
      !seams_.head_record_digest || !seams_.resolve_object ||
      !seams_.send_object || !seams_.make_message_id ||
      config_.maximum_replays == 0U ||
      config_.maximum_replays > 65536U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content publisher configuration is invalid"};
  }
  return Status::success();
}

Result<std::uint64_t> SyncContentPublisherService::next_message_id() const {
  auto result = seams_.make_message_id();
  if (!result) return result.status();
  if (result.value() == 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync content publisher message allocator returned zero"};
  }
  return result;
}

Result<SyncContentPublisherResult> SyncContentPublisherService::handle(
    const SyncPeerContext &context, const protocol::Frame &request) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  const Status context_valid = validate_sync_peer_context(context);
  if (!context_valid.ok()) return context_valid;
  if (!context.content_transfer_negotiated) {
    return Status{ErrorCode::unsupported,
                  "sync content transfer was not negotiated"};
  }
  const Status frame_valid =
      validate_sync_content_object_request_frame(request);
  if (!frame_valid.ok()) return frame_valid;
  auto canonical = protocol::encode(request);
  if (!canonical) return canonical.status();

  const auto replay = std::find_if(
      replays_.begin(), replays_.end(),
      [&context, &request](const ReplayEntry &entry) {
        return entry.friend_number == context.friend_number &&
               entry.online_epoch == context.online_epoch &&
               entry.carrier == context.transfer_carrier &&
               entry.message_id == request.message_id;
      });
  if (replay != replays_.end()) {
    if (replay->request != canonical.value()) {
      ++statistics_.replay_conflicts;
      return Status{ErrorCode::protocol_error,
                    "sync content request id conflicts within epoch"};
    }
    if (replay->authority_format != context.authority.format ||
        replay->authority_epoch != context.authority.ownership_epoch ||
        replay->authority_sequence != context.authority.sequence ||
        replay->authority_tail != context.authority.tail_digest ||
        replay->remote_principal !=
            context.peer_authority.remote_principal ||
        replay->remote_capabilities !=
            context.peer_authority.remote_capabilities ||
        context.peer_authority.verifier_state !=
            security::AuthorityVerifierState::authorized ||
        !context.peer_authority.remote_authorized) {
      return Status{ErrorCode::unavailable,
                    "sync content replay authority changed within epoch"};
    }
    ++statistics_.replay_hits;
    SyncContentPublisherResult result = replay->result;
    result.replayed = true;
    result.file_offered = false;
    return result;
  }
  auto decoded = decode_sync_content_object_request(request.payload);
  if (!decoded) return decoded.status();
  ++statistics_.object_requests;
  SyncContentObjectResult body{
      SyncContentObjectResultStatus::denied,
      decoded.value().kind,
      decoded.value().head_record,
      decoded.value().object,
      decoded.value().transfer_id,
      decoded.value().logical_index,
      decoded.value().object_bytes};
  SyncAuthorizationDecision decision =
      SyncAuthorizationDecision::invalid_policy;
  std::optional<SyncContentObjectDescriptor> admitted;

  auto policy = namespaces_->resolve(decoded.value().namespace_id);
  if (policy && policy.value().engine == Engine::content_v2) {
    const SyncAuthorizationResult authorization =
        evaluate_sync_authorization(
            SyncOperation::subscribe, policy.value(), context.authority,
            context.peer_authority);
    decision = authorization.decision;
    if (authorization.authorized()) {
      auto head = seams_.load_head(policy.value());
      if (!head) {
        body.status = SyncContentObjectResultStatus::unavailable;
      } else if (!head.value().has_value()) {
        body.status = SyncContentObjectResultStatus::object_absent;
      } else {
        auto record = seams_.head_record_digest(*head.value());
        if (!record) {
          body.status = SyncContentObjectResultStatus::unavailable;
        } else if (record.value() != decoded.value().head_record) {
          body.status = SyncContentObjectResultStatus::stale_head;
        } else {
          auto object = seams_.resolve_object(
              policy.value(), *head.value(), decoded.value().kind,
              decoded.value().logical_index);
          if (!object) {
            body.status = object.status().code() == ErrorCode::not_found
                              ? SyncContentObjectResultStatus::object_absent
                              : SyncContentObjectResultStatus::unavailable;
          } else if (object.value().kind != decoded.value().kind ||
                     object.value().logical_index !=
                         decoded.value().logical_index ||
                     object.value().object != decoded.value().object ||
                     object.value().object_bytes !=
                         decoded.value().object_bytes) {
            body.status = SyncContentObjectResultStatus::object_absent;
          } else {
            body.status = SyncContentObjectResultStatus::offered;
            admitted = std::move(object).value();
          }
        }
      }
    } else {
      ++statistics_.denials;
    }
  } else {
    ++statistics_.denials;
  }

  auto message_id = next_message_id();
  if (!message_id) return message_id.status();
  auto response = make_sync_content_object_result_frame(
      body, message_id.value(), request.message_id);
  if (!response) return response.status();
  SyncContentPublisherResult result{
      std::move(response).value(), decision, false, false};
  if (replays_.size() >= config_.maximum_replays) {
    replays_.pop_front();
    ++statistics_.replay_evictions;
  }
  replays_.push_back(ReplayEntry{
      context.friend_number, context.online_epoch,
      context.transfer_carrier, request.message_id,
      context.authority.format, context.authority.ownership_epoch,
      context.authority.sequence, context.authority.tail_digest,
      context.peer_authority.remote_principal,
      context.peer_authority.remote_capabilities,
      std::move(canonical).value(), std::move(result)});
  ReplayEntry &retained = replays_.back();
  if (admitted.has_value()) {
    auto offered = seams_.send_object(
        context.transfer_carrier, admitted->path,
        decoded.value().transfer_id);
    if (offered) {
      retained.result.file_offered = true;
      ++statistics_.file_offers;
    } else {
      body.status = SyncContentObjectResultStatus::unavailable;
      auto unavailable = make_sync_content_object_result_frame(
          body, message_id.value(), request.message_id);
      if (!unavailable) return unavailable.status();
      retained.result.response = std::move(unavailable).value();
    }
  }
  statistics_.retained_replays = replays_.size();
  return retained.result;
}

Result<SyncContentPublisherResult>
SyncContentPublisherService::handle_availability(
    const SyncPeerContext &context, const protocol::Frame &request) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  if (!seams_.resolve_availability) {
    return Status{ErrorCode::unsupported,
                  "sync content availability is not configured"};
  }
  const Status context_valid = validate_sync_peer_context(context);
  if (!context_valid.ok()) return context_valid;
  if (!context.content_transfer_negotiated) {
    return Status{ErrorCode::unsupported,
                  "sync content transfer was not negotiated"};
  }
  const Status frame_valid =
      validate_sync_content_availability_request_frame(request);
  if (!frame_valid.ok()) return frame_valid;
  auto canonical = protocol::encode(request);
  if (!canonical) return canonical.status();

  const auto replay = std::find_if(
      replays_.begin(), replays_.end(),
      [&context, &request](const ReplayEntry &entry) {
        return entry.friend_number == context.friend_number &&
               entry.online_epoch == context.online_epoch &&
               entry.carrier == context.transfer_carrier &&
               entry.message_id == request.message_id;
      });
  if (replay != replays_.end()) {
    if (replay->request != canonical.value()) {
      ++statistics_.replay_conflicts;
      return Status{ErrorCode::protocol_error,
                    "sync content availability request id conflicts within epoch"};
    }
    if (replay->authority_format != context.authority.format ||
        replay->authority_epoch != context.authority.ownership_epoch ||
        replay->authority_sequence != context.authority.sequence ||
        replay->authority_tail != context.authority.tail_digest ||
        replay->remote_principal !=
            context.peer_authority.remote_principal ||
        replay->remote_capabilities !=
            context.peer_authority.remote_capabilities ||
        context.peer_authority.verifier_state !=
            security::AuthorityVerifierState::authorized ||
        !context.peer_authority.remote_authorized) {
      return Status{ErrorCode::unavailable,
                    "sync content availability replay authority changed within epoch"};
    }
    ++statistics_.replay_hits;
    SyncContentPublisherResult result = replay->result;
    result.replayed = true;
    result.file_offered = false;
    return result;
  }
  auto decoded =
      decode_sync_content_availability_request(request.payload);
  if (!decoded) return decoded.status();
  ++statistics_.availability_requests;
  SyncContentAvailabilityResult body{
      SyncContentAvailabilityResultStatus::denied,
      decoded.value().kind,
      decoded.value().head_record,
      decoded.value().first_object,
      decoded.value().object_count,
      std::vector<std::uint8_t>(
          (static_cast<std::size_t>(decoded.value().object_count) + 7U) /
              8U,
          0U)};
  SyncAuthorizationDecision decision =
      SyncAuthorizationDecision::invalid_policy;

  auto policy = namespaces_->resolve(decoded.value().namespace_id);
  if (policy && policy.value().engine == Engine::content_v2) {
    const SyncAuthorizationResult authorization =
        evaluate_sync_authorization(
            SyncOperation::subscribe, policy.value(), context.authority,
            context.peer_authority);
    decision = authorization.decision;
    if (authorization.authorized()) {
      auto head = seams_.load_head(policy.value());
      if (!head || !head.value().has_value()) {
        body.status = SyncContentAvailabilityResultStatus::unavailable;
      } else {
        auto record = seams_.head_record_digest(*head.value());
        if (!record) {
          body.status = SyncContentAvailabilityResultStatus::unavailable;
        } else if (record.value() != decoded.value().head_record) {
          body.status = SyncContentAvailabilityResultStatus::stale_head;
        } else {
          auto availability = seams_.resolve_availability(
              policy.value(), *head.value(), decoded.value().kind,
              decoded.value().first_object,
              decoded.value().object_count);
          if (!availability ||
              availability.value().kind != decoded.value().kind ||
              availability.value().first_object !=
                  decoded.value().first_object ||
              availability.value().object_count !=
                  decoded.value().object_count ||
              availability.value().availability.size() !=
                  body.availability.size()) {
            body.status = SyncContentAvailabilityResultStatus::unavailable;
          } else {
            body.status = SyncContentAvailabilityResultStatus::available;
            body.availability =
                std::move(availability).value().availability;
          }
        }
      }
    } else {
      ++statistics_.denials;
    }
  } else {
    ++statistics_.denials;
  }

  auto message_id = next_message_id();
  if (!message_id) return message_id.status();
  auto response = make_sync_content_availability_result_frame(
      body, message_id.value(), request.message_id);
  if (!response) return response.status();
  SyncContentPublisherResult result{
      std::move(response).value(), decision, false, false};
  if (replays_.size() >= config_.maximum_replays) {
    replays_.pop_front();
    ++statistics_.replay_evictions;
  }
  replays_.push_back(ReplayEntry{
      context.friend_number, context.online_epoch,
      context.transfer_carrier, request.message_id,
      context.authority.format, context.authority.ownership_epoch,
      context.authority.sequence, context.authority.tail_digest,
      context.peer_authority.remote_principal,
      context.peer_authority.remote_capabilities,
      std::move(canonical).value(), std::move(result)});
  statistics_.retained_replays = replays_.size();
  return replays_.back().result;
}

void SyncContentPublisherService::peer_offline(
    std::uint32_t friend_number, std::uint64_t online_epoch) {
  std::scoped_lock lock(mutex_);
  std::erase_if(
      replays_, [friend_number, online_epoch](const ReplayEntry &entry) {
        return entry.friend_number == friend_number &&
               entry.online_epoch == online_epoch;
      });
  statistics_.retained_replays = replays_.size();
}

void SyncContentPublisherService::carrier_offline(
    const SyncTransferCarrier &carrier) {
  std::scoped_lock lock(mutex_);
  std::erase_if(replays_, [&carrier](const ReplayEntry &entry) {
    return entry.carrier == carrier;
  });
  statistics_.retained_replays = replays_.size();
}

SyncContentPublisherSnapshot SyncContentPublisherService::snapshot() const {
  std::scoped_lock lock(mutex_);
  return statistics_;
}

std::optional<SyncContentPublisherSnapshot>
SyncContentPublisherService::try_snapshot() const {
  std::unique_lock lock(mutex_, std::try_to_lock);
  return lock.owns_lock()
             ? std::optional<SyncContentPublisherSnapshot>{statistics_}
             : std::nullopt;
}

} // namespace iotox::sync
