#include "iotox/sync_service.hpp"

#include <algorithm>
#include <utility>

namespace iotox::sync {
namespace {

SyncObjectRecord object_from_head(const SignedHead &head, SyncObjectKind kind) {
  if (kind == SyncObjectKind::artifact)
    return {kind, head.artifact, head.artifact_bytes};
  return {kind, head.manifest, head.manifest_bytes};
}

bool empty_route_key(const routes::ToxPublicKey &key) noexcept {
  return std::all_of(key.begin(), key.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

Result<std::string> request_namespace(const protocol::Frame &request) {
  if (request.type == protocol::MessageType::sync_head_request) {
    auto decoded = decode_sync_head_request(request.payload);
    if (!decoded) return decoded.status();
    return decoded.value().namespace_id;
  }
  if (request.type == protocol::MessageType::sync_object_request) {
    auto decoded = decode_sync_object_request(request.payload);
    if (!decoded) return decoded.status();
    return decoded.value().namespace_id;
  }
  if (request.type == protocol::MessageType::sync_range_request) {
    auto decoded = decode_sync_range_request(request.payload);
    if (!decoded) return decoded.status();
    return decoded.value().namespace_id;
  }
  return Status{ErrorCode::protocol_error,
                "sync replay request has no namespace"};
}

} // namespace

Status validate_sync_peer_context(const SyncPeerContext &context) {
  const SyncTransferCarrier &carrier = context.transfer_carrier;
  if (context.online_epoch == 0U || empty_route_key(context.authority_route_key) ||
      !context.peer_authority.connected ||
      context.peer_authority.friend_number != context.friend_number ||
      context.peer_authority.online_epoch != context.online_epoch ||
      carrier.worker_id == 0U || carrier.online_epoch == 0U ||
      empty_route_key(carrier.route_key)) {
    return Status{ErrorCode::invalid_argument,
                  "sync peer context has an invalid authority or carrier fence"};
  }
  if (carrier.carrier_class == SyncCarrierClass::primary) {
    if (carrier.route_key != context.authority_route_key ||
        carrier.worker_id != context.online_epoch ||
        carrier.friend_number != context.friend_number ||
        carrier.online_epoch != context.online_epoch ||
        carrier.remote_route_generation != 0U ||
        !empty_route_key(carrier.remote_coordinator_route_key) ||
        carrier.primary_authority_online_epoch != 0U) {
      return Status{ErrorCode::invalid_argument,
                    "primary sync carrier does not match its authority session"};
    }
    return Status::success();
  }
  if (carrier.carrier_class != SyncCarrierClass::auxiliary ||
      carrier.remote_route_generation == 0U ||
      empty_route_key(carrier.remote_coordinator_route_key) ||
      carrier.primary_authority_online_epoch == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "auxiliary sync carrier has an invalid route generation"};
  }
  return Status::success();
}

SyncPublisherService::SyncPublisherService(const NamespaceRegistry &namespaces,
                                           SyncPublisherSeams seams)
    : SyncPublisherService(namespaces, std::move(seams), Config{}) {}

SyncPublisherService::SyncPublisherService(const NamespaceRegistry &namespaces,
                                           SyncPublisherSeams seams, Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {}

Status SyncPublisherService::validate_config() const {
  if (namespaces_ == nullptr || !seams_.load_head || !seams_.head_record_digest ||
      !seams_.verify_object || !seams_.send_object || !seams_.make_message_id ||
      config_.maximum_replays == 0U || config_.maximum_replays > 65536U) {
    return Status{ErrorCode::invalid_argument, "sync publisher service configuration is invalid"};
  }
  return Status::success();
}

Result<std::uint64_t> SyncPublisherService::next_message_id() const {
  auto message_id = seams_.make_message_id();
  if (!message_id)
    return message_id.status();
  if (message_id.value() == 0U) {
    return Status{ErrorCode::protocol_error, "sync publisher message allocator returned zero"};
  }
  return message_id;
}

Result<SyncPublisherResult> SyncPublisherService::handle(const SyncPeerContext &context,
                                                         const protocol::Frame &request) {
  std::scoped_lock lock(mutex_);
  const Status configured = validate_config();
  if (!configured.ok())
    return configured;
  const Status context_valid = validate_sync_peer_context(context);
  if (!context_valid.ok()) return context_valid;
  if (context.transfer_carrier.carrier_class ==
          SyncCarrierClass::auxiliary &&
      request.type != protocol::MessageType::sync_object_request &&
      request.type != protocol::MessageType::sync_range_request) {
    return Status{ErrorCode::unsupported,
                  "auxiliary sync carriers permit only object/range requests"};
  }

  auto canonical = protocol::encode(request);
  if (!canonical)
    return canonical.status();
  const auto replay = std::find_if(
      replays_.begin(), replays_.end(), [&context, &request](const ReplayEntry &entry) {
        return entry.friend_number == context.friend_number &&
               entry.online_epoch == context.online_epoch &&
               entry.carrier == context.transfer_carrier &&
               entry.message_id == request.message_id;
      });
  if (replay != replays_.end()) {
    if (replay->request != canonical.value()) {
      ++statistics_.replay_conflicts;
      return Status{ErrorCode::protocol_error,
                    "sync request message identifier conflicts within epoch"};
    }
    if (replay->authority_format != context.authority.format ||
        replay->authority_epoch != context.authority.ownership_epoch ||
        replay->authority_sequence != context.authority.sequence ||
        replay->authority_tail != context.authority.tail_digest ||
        replay->remote_principal != context.peer_authority.remote_principal ||
        replay->remote_capabilities != context.peer_authority.remote_capabilities ||
        context.peer_authority.verifier_state != security::AuthorityVerifierState::authorized ||
        !context.peer_authority.remote_authorized) {
      return Status{ErrorCode::unavailable,
                    "sync replay authority changed within the online epoch"};
    }
    ++statistics_.replay_hits;
    SyncPublisherResult result = replay->result;
    result.replayed = true;
    result.file_offered = false;
    return result;
  }
  std::optional<PendingOffer> pending_offer;
  Result<SyncPublisherResult> result =
      request.type == protocol::MessageType::sync_head_request ? handle_head(context, request)
      : request.type == protocol::MessageType::sync_object_request
          ? handle_object(context, request, pending_offer)
      : request.type == protocol::MessageType::sync_range_request
          ? handle_range(context, request, pending_offer)
          : Result<SyncPublisherResult>{
                Status{ErrorCode::protocol_error, "sync publisher received a non-request frame"}};
  if (!result)
    return result.status();
  auto namespace_id = request_namespace(request);
  if (!namespace_id) return namespace_id.status();
  if (replays_.size() >= config_.maximum_replays) {
    replays_.pop_front();
    ++statistics_.replay_evictions;
  }
  replays_.push_back(ReplayEntry{
      context.friend_number, context.online_epoch, context.transfer_carrier,
      request.message_id, context.authority.format,
      context.authority.ownership_epoch, context.authority.sequence, context.authority.tail_digest,
      context.peer_authority.remote_principal, context.peer_authority.remote_capabilities,
      std::move(namespace_id).value(),
      std::move(canonical).value(), std::move(result).value()});
  ReplayEntry &retained = replays_.back();
  if (pending_offer) {
    auto offered = pending_offer->ranges.empty()
        ? seams_.send_object(pending_offer->carrier,
                             pending_offer->path, pending_offer->file_id)
        : seams_.send_ranges
              ? seams_.send_ranges(pending_offer->carrier,
                                    pending_offer->path,
                                    pending_offer->ranges,
                                    pending_offer->file_id)
              : Result<FileTransferRecord>{Status{
                    ErrorCode::unsupported,
                    "sync range sender is not constructed"}};
    if (offered) {
      retained.result.file_offered = true;
      ++statistics_.file_offers;
      if (!pending_offer->ranges.empty()) {
        ++statistics_.range_file_offers;
        statistics_.range_bytes_offered += offered.value().file_size;
      }
    } else {
      retained.result.response = std::move(pending_offer->failure_response);
    }
  }
  statistics_.retained_replays = replays_.size();
  return retained.result;
}

Result<SyncPublisherResult> SyncPublisherService::handle_head(const SyncPeerContext &context,
                                                              const protocol::Frame &request) {
  const Status valid = validate_sync_head_request_frame(request);
  if (!valid.ok())
    return valid;
  auto decoded = decode_sync_head_request(request.payload);
  if (!decoded)
    return decoded.status();
  ++statistics_.head_requests;

  SyncHeadResult body;
  SyncAuthorizationDecision decision = SyncAuthorizationDecision::invalid_policy;
  auto policy = namespaces_->resolve(decoded.value().namespace_id);
  if (policy) {
    const SyncAuthorizationResult authorized = evaluate_sync_authorization(
        SyncOperation::subscribe, policy.value(), context.authority, context.peer_authority);
    decision = authorized.decision;
    if (authorized.authorized()) {
      auto head = seams_.load_head(policy.value());
      if (head && head.value().has_value()) {
        body.status = SyncHeadResultStatus::available;
        body.head = std::move(head).value();
      } else if (head) {
        body.status = SyncHeadResultStatus::absent;
      } else {
        body.status = SyncHeadResultStatus::unavailable;
      }
    } else {
      body.status = SyncHeadResultStatus::denied;
      ++statistics_.denials;
    }
  } else {
    body.status = SyncHeadResultStatus::denied;
    ++statistics_.denials;
  }
  auto message_id = next_message_id();
  if (!message_id)
    return message_id.status();
  auto response = make_sync_head_result_frame(body, message_id.value(), request.message_id);
  if (!response)
    return response.status();
  return SyncPublisherResult{std::move(response).value(), decision, false, false};
}

Result<SyncPublisherResult>
SyncPublisherService::handle_object(const SyncPeerContext &context, const protocol::Frame &request,
                                    std::optional<PendingOffer> &pending_offer) {
  const Status valid = validate_sync_object_request_frame(request);
  if (!valid.ok())
    return valid;
  auto decoded = decode_sync_object_request(request.payload);
  if (!decoded)
    return decoded.status();
  ++statistics_.object_requests;

  SyncObjectResult body;
  body.kind = decoded.value().kind;
  body.head_record = decoded.value().head_record;
  body.transfer_id = decoded.value().transfer_id;
  body.status = SyncObjectResultStatus::denied;
  SyncAuthorizationDecision decision = SyncAuthorizationDecision::invalid_policy;
  std::optional<NamespacePolicy> admitted_policy;
  std::optional<SyncObjectRecord> admitted_object;

  auto policy = namespaces_->resolve(decoded.value().namespace_id);
  if (policy) {
    const SyncAuthorizationResult authorized = evaluate_sync_authorization(
        SyncOperation::subscribe, policy.value(), context.authority, context.peer_authority);
    decision = authorized.decision;
    if (authorized.authorized()) {
      auto head = seams_.load_head(policy.value());
      if (!head) {
        body.status = SyncObjectResultStatus::unavailable;
      } else if (!head.value().has_value()) {
        body.status = SyncObjectResultStatus::object_absent;
      } else {
        auto record = seams_.head_record_digest(*head.value());
        if (!record) {
          body.status = SyncObjectResultStatus::unavailable;
        } else if (record.value() != decoded.value().head_record) {
          body.status = SyncObjectResultStatus::stale_head;
        } else {
          SyncObjectRecord object = object_from_head(*head.value(), decoded.value().kind);
          const Status verified = seams_.verify_object(policy.value(), object);
          if (!verified.ok()) {
            body.status = verified.code() == ErrorCode::not_found
                              ? SyncObjectResultStatus::object_absent
                              : SyncObjectResultStatus::unavailable;
          } else {
            body.status = SyncObjectResultStatus::offered;
            admitted_policy = policy.value();
            admitted_object = object;
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
  if (!message_id)
    return message_id.status();
  auto response = make_sync_object_result_frame(body, message_id.value(), request.message_id);
  if (!response)
    return response.status();
  SyncPublisherResult result{std::move(response).value(), decision, false, false};
  if (admitted_policy && admitted_object) {
    body.status = SyncObjectResultStatus::unavailable;
    auto unavailable = make_sync_object_result_frame(body, message_id.value(), request.message_id);
    if (!unavailable)
      return unavailable.status();
    pending_offer =
        PendingOffer{context.transfer_carrier,
                     sync_object_path(*admitted_policy, *admitted_object),
                     decoded.value().transfer_id, {},
                     std::move(unavailable).value()};
  }
  return result;
}

Result<SyncPublisherResult>
SyncPublisherService::handle_range(
    const SyncPeerContext &context, const protocol::Frame &request,
    std::optional<PendingOffer> &pending_offer) {
  if (!context.range_transfer_negotiated) {
    return Status{ErrorCode::unsupported,
                  "sync range transfer was not negotiated"};
  }
  const Status valid = validate_sync_range_request_frame(request);
  if (!valid.ok()) return valid;
  auto decoded = decode_sync_range_request(request.payload);
  if (!decoded) return decoded.status();
  ++statistics_.range_requests;

  SyncRangeResult body;
  body.head_record = decoded.value().head_record;
  body.transfer_id = decoded.value().transfer_id;
  body.status = SyncRangeResultStatus::denied;
  SyncAuthorizationDecision decision =
      SyncAuthorizationDecision::invalid_policy;
  std::optional<NamespacePolicy> admitted_policy;
  std::optional<SyncObjectRecord> admitted_object;
  std::vector<FileByteRange> admitted_ranges;

  auto policy = namespaces_->resolve(decoded.value().namespace_id);
  if (policy) {
    const SyncAuthorizationResult authorized = evaluate_sync_authorization(
        SyncOperation::subscribe, policy.value(), context.authority,
        context.peer_authority);
    decision = authorized.decision;
    if (authorized.authorized()) {
      auto head = seams_.load_head(policy.value());
      if (!head) {
        body.status = SyncRangeResultStatus::unavailable;
      } else if (!head.value().has_value()) {
        body.status = SyncRangeResultStatus::artifact_absent;
      } else {
        auto record = seams_.head_record_digest(*head.value());
        if (!record) {
          body.status = SyncRangeResultStatus::unavailable;
        } else if (record.value() != decoded.value().head_record) {
          body.status = SyncRangeResultStatus::stale_head;
        } else {
          const SyncObjectRecord object = object_from_head(
              *head.value(), SyncObjectKind::artifact);
          std::uint64_t total = 0U;
          bool ranges_fit = decoded.value().ranges.size() <=
              policy.value().quotas.maximum_outstanding_requests;
          if (ranges_fit) {
            admitted_ranges.reserve(decoded.value().ranges.size());
            for (const SyncRangeRecord &range : decoded.value().ranges) {
              if (range.offset > object.bytes ||
                  range.length > object.bytes - range.offset ||
                  range.length > object.bytes - total) {
                ranges_fit = false;
                break;
              }
              total += range.length;
              admitted_ranges.push_back({range.offset, range.length});
            }
          }
          if (!ranges_fit || total == 0U || total >
                  policy.value().quotas.maximum_staging_bytes) {
            body.status = SyncRangeResultStatus::unavailable;
            admitted_ranges.clear();
          } else {
            const Status verified =
                seams_.verify_object(policy.value(), object);
            if (!verified.ok()) {
              body.status = verified.code() == ErrorCode::not_found
                  ? SyncRangeResultStatus::artifact_absent
                  : SyncRangeResultStatus::unavailable;
              admitted_ranges.clear();
            } else {
              body.status = SyncRangeResultStatus::offered;
              admitted_policy = policy.value();
              admitted_object = object;
            }
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
  auto response = make_sync_range_result_frame(
      body, message_id.value(), request.message_id);
  if (!response) return response.status();
  SyncPublisherResult result{
      std::move(response).value(), decision, false, false};
  if (admitted_policy && admitted_object) {
    body.status = SyncRangeResultStatus::unavailable;
    auto unavailable = make_sync_range_result_frame(
        body, message_id.value(), request.message_id);
    if (!unavailable) return unavailable.status();
    pending_offer = PendingOffer{
        context.transfer_carrier,
        sync_object_path(*admitted_policy, *admitted_object),
        decoded.value().transfer_id, std::move(admitted_ranges),
        std::move(unavailable).value()};
  }
  return result;
}

void SyncPublisherService::peer_offline(std::uint32_t friend_number, std::uint64_t online_epoch) {
  std::scoped_lock lock(mutex_);
  std::erase_if(replays_, [friend_number, online_epoch](const ReplayEntry &entry) {
    return entry.friend_number == friend_number && entry.online_epoch == online_epoch;
  });
  statistics_.retained_replays = replays_.size();
}

void SyncPublisherService::carrier_offline(
    const SyncTransferCarrier &carrier) {
  std::scoped_lock lock(mutex_);
  std::erase_if(replays_, [&carrier](const ReplayEntry &entry) {
    return entry.carrier == carrier;
  });
  statistics_.retained_replays = replays_.size();
}

std::size_t SyncPublisherService::retire_namespace_replays_for_additive_share(
    std::string_view namespace_id) {
  std::scoped_lock lock(mutex_);
  const std::size_t before = replays_.size();
  std::erase_if(replays_, [namespace_id](const ReplayEntry &entry) {
    return entry.namespace_id == namespace_id;
  });
  statistics_.retained_replays = replays_.size();
  return before - replays_.size();
}

SyncPublisherSnapshot SyncPublisherService::snapshot() const {
  std::scoped_lock lock(mutex_);
  SyncPublisherSnapshot result = statistics_;
  result.retained_replays = replays_.size();
  return result;
}

std::optional<SyncPublisherSnapshot>
SyncPublisherService::try_snapshot() const {
  std::unique_lock lock(mutex_, std::try_to_lock);
  if (!lock.owns_lock()) return std::nullopt;
  SyncPublisherSnapshot result = statistics_;
  result.retained_replays = replays_.size();
  return result;
}

} // namespace iotox::sync
