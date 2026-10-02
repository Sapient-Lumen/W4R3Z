#include "iotox/sync_scheduler.hpp"

#include "iotox/security/random.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace iotox::sync {
namespace {

bool all_zero(const Digest &digest) {
  return std::all_of(digest.begin(), digest.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

} // namespace

SyncObjectScheduler::SyncObjectScheduler(routes::Coordinator &coordinator)
    : SyncObjectScheduler(coordinator, Config{}) {}

SyncObjectScheduler::SyncObjectScheduler(routes::Coordinator &coordinator,
                                         Config config)
    : SyncObjectScheduler(
          CapacitySeams{
              [&coordinator](const routes::ToxPublicKey &key,
                             std::uint64_t worker_id) {
                const routes::CoordinatorSnapshot state = coordinator.snapshot();
                const auto route = std::find_if(
                    state.members.begin(), state.members.end(),
                    [&key, worker_id](const routes::MemberSnapshot &member) {
                      return member.policy.tox_public_key == key &&
                             member.worker_id == worker_id;
                    });
                if (route == state.members.end() ||
                    route->policy.role != routes::Role::bulk ||
                    route->lifecycle != routes::Lifecycle::ready) {
                  return Status{ErrorCode::unavailable,
                                "sync objects require an exact ready bulk route"};
                }
                return coordinator.admit_work(key, worker_id, 1U);
              },
              [&coordinator](const routes::ToxPublicKey &key,
                             std::uint64_t worker_id) {
                return coordinator.release_work(key, worker_id, 1U);
              },
              [&coordinator](const routes::ToxPublicKey &key,
                             std::uint64_t worker_id) -> Result<bool> {
                const routes::CoordinatorSnapshot state = coordinator.snapshot();
                const auto route = std::find_if(
                    state.members.begin(), state.members.end(),
                    [&key, worker_id](const routes::MemberSnapshot &member) {
                      return member.policy.tox_public_key == key &&
                             member.worker_id == worker_id;
                    });
                return route != state.members.end() &&
                       route->admitted_work == 0U &&
                       route->lifecycle != routes::Lifecycle::ready;
              }},
          std::move(config)) {}

SyncObjectScheduler::SyncObjectScheduler(CapacitySeams capacity, Config config)
    : capacity_(std::move(capacity)), config_(std::move(config)) {
  if (!config_.make_attempt_id) {
    config_.make_attempt_id = [] { return security::random_u64_nonzero(); };
  }
}

SyncObjectScheduler::~SyncObjectScheduler() noexcept {
  try {
    (void)close();
  } catch (...) {
    // Destruction cannot report an allocation failure from the defensive
    // capacity-state query used only when its ordinary release rejects.
  }
}

Status SyncObjectScheduler::validate_config() const {
  if (!capacity_.admit || !capacity_.release ||
      !capacity_.already_released || config_.maximum_objects == 0U ||
      config_.maximum_objects > 65536U || config_.maximum_attempts == 0U ||
      config_.maximum_attempts > 1048576U ||
      config_.maximum_attempts < config_.maximum_objects ||
      config_.maximum_staging_bytes == 0U ||
      !config_.make_attempt_id) {
    return Status{ErrorCode::invalid_argument,
                  "sync object scheduler bounds are invalid"};
  }
  return Status::success();
}

Result<std::size_t> SyncObjectScheduler::object_index(
    SyncObjectKind kind, const Digest &identity) const {
  const auto found = std::find_if(
      objects_.begin(), objects_.end(),
      [kind, &identity](const ScheduledObjectSnapshot &object) {
        return object.object.kind == kind &&
               object.object.identity == identity;
      });
  if (found == objects_.end()) {
    return Status{ErrorCode::not_found,
                  "sync scheduler object is not registered"};
  }
  return static_cast<std::size_t>(found - objects_.begin());
}

Result<std::size_t> SyncObjectScheduler::attempt_index(
    std::uint64_t attempt_id) const {
  if (attempt_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync transfer attempt identifier zero is reserved"};
  }
  const auto found = std::find_if(
      attempts_.begin(), attempts_.end(),
      [attempt_id](const TransferAttemptSnapshot &attempt) {
        return attempt.attempt_id == attempt_id;
      });
  if (found == attempts_.end()) {
    return Status{ErrorCode::not_found,
                  "sync transfer attempt is not retained"};
  }
  return static_cast<std::size_t>(found - attempts_.begin());
}

Status SyncObjectScheduler::add_object(const SyncObjectRecord &object) {
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  if (closed_) {
    return Status{ErrorCode::unavailable,
                  "sync object scheduler is closed"};
  }
  if (all_zero(object.identity) || object.bytes == 0U ||
      (object.kind != SyncObjectKind::artifact &&
       object.kind != SyncObjectKind::manifest)) {
    return Status{ErrorCode::invalid_argument,
                  "sync scheduler object identity or kind is invalid"};
  }
  auto existing = object_index(object.kind, object.identity);
  if (existing) {
    return objects_[existing.value()].object == object
               ? Status::success()
               : Status{ErrorCode::protocol_error,
                        "sync scheduler object identity has conflicting size"};
  }
  if (objects_.size() >= config_.maximum_objects) {
    return Status{ErrorCode::resource_exhausted,
                  "sync scheduler object bound is exhausted"};
  }
  objects_.push_back(ScheduledObjectSnapshot{object});
  return Status::success();
}

Result<TransferAttemptSnapshot> SyncObjectScheduler::assign(
    SyncObjectKind kind, const Digest &identity,
    const routes::ToxPublicKey &route_key, std::uint64_t worker_id) {
  const Status configured = validate_config();
  if (!configured.ok()) return configured;
  if (closed_) {
    return Status{ErrorCode::unavailable,
                  "sync object scheduler is closed"};
  }
  auto object = object_index(kind, identity);
  if (!object) return object.status();
  ScheduledObjectSnapshot &scheduled = objects_[object.value()];
  if (scheduled.state != ScheduledObjectState::pending ||
      scheduled.current_attempt_id != 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync object already has an active or terminal assignment"};
  }
  if (attempts_.size() >= config_.maximum_attempts) {
    return Status{ErrorCode::resource_exhausted,
                  "sync scheduler attempt tombstone bound is exhausted"};
  }
  if (scheduled.object.bytes > config_.maximum_staging_bytes ||
      reserved_staging_bytes_ >
          config_.maximum_staging_bytes - scheduled.object.bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync scheduler staging-byte reservation is exhausted"};
  }
  auto attempt_id = config_.make_attempt_id();
  if (!attempt_id || attempt_id.value() == 0U) {
    return attempt_id ? Status{ErrorCode::protocol_error,
                               "sync attempt allocator returned zero"}
                      : attempt_id.status();
  }
  if (attempt_index(attempt_id.value())) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt allocator reused a retained identifier"};
  }
  TransferAttemptSnapshot attempt;
  attempt.attempt_id = attempt_id.value();
  attempt.object = scheduled.object;
  attempt.route_key = route_key;
  attempt.worker_id = worker_id;
  attempts_.push_back(attempt);
  const Status reserved = capacity_.admit(route_key, worker_id);
  if (!reserved.ok()) {
    attempts_.pop_back();
    return reserved;
  }
  attempts_.back().route_capacity_reserved = true;
  attempts_.back().staging_bytes_reserved = true;
  reserved_staging_bytes_ += scheduled.object.bytes;
  scheduled.state = ScheduledObjectState::assigned;
  scheduled.current_attempt_id = attempt.attempt_id;
  ++assignments_;
  return attempts_.back();
}

Status SyncObjectScheduler::release_reservations(
    TransferAttemptSnapshot &attempt) {
  if (attempt.staging_bytes_reserved &&
      attempt.object.bytes > reserved_staging_bytes_) {
    return Status{ErrorCode::internal_error,
                  "sync scheduler staging reservation underflow"};
  }
  if (attempt.route_capacity_reserved) {
    const Status released = capacity_.release(attempt.route_key,
                                              attempt.worker_id);
    if (!released.ok()) {
      // Authentication loss and recovery atomically withdraw coordinator work
      // before transport/scheduler cleanup observes the route. Treat only that
      // exact closed, zero-capacity incarnation as already released.
      auto already_released = capacity_.already_released(
          attempt.route_key, attempt.worker_id);
      if (!already_released) return already_released.status();
      if (!already_released.value()) {
        return released;
      }
    }
    attempt.route_capacity_reserved = false;
  }
  if (attempt.staging_bytes_reserved) {
    reserved_staging_bytes_ -= attempt.object.bytes;
    attempt.staging_bytes_reserved = false;
  }
  return Status::success();
}

Result<std::size_t> SyncObjectScheduler::fence_route(
    const routes::ToxPublicKey &route_key, std::uint64_t worker_id) {
  std::size_t fenced = 0U;
  for (TransferAttemptSnapshot &attempt : attempts_) {
    if (attempt.route_key != route_key || attempt.worker_id != worker_id ||
        (attempt.state != TransferAttemptState::active &&
         attempt.state != TransferAttemptState::verified)) {
      continue;
    }
    auto object = object_index(attempt.object.kind, attempt.object.identity);
    if (!object) return object.status();
    ScheduledObjectSnapshot &scheduled = objects_[object.value()];
    if (scheduled.current_attempt_id != attempt.attempt_id ||
        (scheduled.state != ScheduledObjectState::assigned &&
         scheduled.state != ScheduledObjectState::verified)) {
      return Status{ErrorCode::protocol_error,
                    "sync route fence does not own the current object"};
    }
    const Status released = release_reservations(attempt);
    if (!released.ok()) return released;
    scheduled.state = ScheduledObjectState::pending;
    scheduled.current_attempt_id = 0U;
    attempt.state = TransferAttemptState::fenced;
    ++fenced;
    ++fences_;
  }
  return fenced;
}

Status SyncObjectScheduler::fence_attempt(std::uint64_t attempt_id) {
  auto index = attempt_index(attempt_id);
  if (!index) return index.status();
  TransferAttemptSnapshot &attempt = attempts_[index.value()];
  if (attempt.state == TransferAttemptState::fenced) {
    return Status::success();
  }
  if (attempt.state == TransferAttemptState::committed) {
    return Status{ErrorCode::invalid_argument,
                  "committed sync attempt cannot be fenced"};
  }
  auto object = object_index(attempt.object.kind, attempt.object.identity);
  if (!object) return object.status();
  ScheduledObjectSnapshot &scheduled = objects_[object.value()];
  if (scheduled.current_attempt_id != attempt_id ||
      (scheduled.state != ScheduledObjectState::assigned &&
       scheduled.state != ScheduledObjectState::verified)) {
    return Status{ErrorCode::protocol_error,
                  "sync attempt fence does not own the current object"};
  }
  const Status released = release_reservations(attempt);
  if (!released.ok()) return released;
  scheduled.state = ScheduledObjectState::pending;
  scheduled.current_attempt_id = 0U;
  attempt.state = TransferAttemptState::fenced;
  ++fences_;
  return Status::success();
}

Status SyncObjectScheduler::complete(
    std::uint64_t attempt_id, const Digest &observed_identity,
    std::uint64_t observed_bytes) {
  auto index = attempt_index(attempt_id);
  if (!index) return index.status();
  TransferAttemptSnapshot &attempt = attempts_[index.value()];
  if (attempt.state == TransferAttemptState::fenced) {
    ++late_completions_;
    return Status{ErrorCode::unavailable,
                  "fenced sync transfer completion is stale"};
  }
  if (attempt.state == TransferAttemptState::verified ||
      attempt.state == TransferAttemptState::committed) {
    return attempt.object.identity == observed_identity &&
                   attempt.object.bytes == observed_bytes
               ? Status::success()
               : Status{ErrorCode::protocol_error,
                        "sync completion conflicts with retained verification"};
  }
  if (attempt.object.identity != observed_identity ||
      attempt.object.bytes != observed_bytes) {
    const Status released = release_reservations(attempt);
    if (!released.ok()) return released;
    auto object = object_index(attempt.object.kind, attempt.object.identity);
    if (!object) return object.status();
    objects_[object.value()].state = ScheduledObjectState::pending;
    objects_[object.value()].current_attempt_id = 0U;
    attempt.state = TransferAttemptState::fenced;
    ++verification_failures_;
    ++fences_;
    return Status{ErrorCode::protocol_error,
                  "sync transfer bytes do not match the immutable object"};
  }
  attempt.state = TransferAttemptState::verified;
  auto object = object_index(attempt.object.kind, attempt.object.identity);
  if (!object) return object.status();
  objects_[object.value()].state = ScheduledObjectState::verified;
  return Status::success();
}

Status SyncObjectScheduler::commit(std::uint64_t attempt_id) {
  auto index = attempt_index(attempt_id);
  if (!index) return index.status();
  TransferAttemptSnapshot &attempt = attempts_[index.value()];
  if (attempt.state == TransferAttemptState::committed) {
    return Status::success();
  }
  if (attempt.state != TransferAttemptState::verified) {
    return Status{ErrorCode::invalid_argument,
                  "sync object cannot commit before exact verification"};
  }
  auto object = object_index(attempt.object.kind, attempt.object.identity);
  if (!object) return object.status();
  ScheduledObjectSnapshot &scheduled = objects_[object.value()];
  if (scheduled.current_attempt_id != attempt_id ||
      scheduled.state != ScheduledObjectState::verified) {
    return Status{ErrorCode::protocol_error,
                  "sync commit does not own the current verified attempt"};
  }
  const Status released = release_reservations(attempt);
  if (!released.ok()) return released;
  scheduled.state = ScheduledObjectState::committed;
  attempt.state = TransferAttemptState::committed;
  ++commits_;
  return Status::success();
}

Status SyncObjectScheduler::close() {
  if (closed_) return Status::success();
  for (TransferAttemptSnapshot &attempt : attempts_) {
    if (attempt.state != TransferAttemptState::active &&
        attempt.state != TransferAttemptState::verified) {
      continue;
    }
    const Status released = release_reservations(attempt);
    if (!released.ok()) return released;
    auto object = object_index(attempt.object.kind, attempt.object.identity);
    if (!object) return object.status();
    objects_[object.value()].state = ScheduledObjectState::pending;
    objects_[object.value()].current_attempt_id = 0U;
    attempt.state = TransferAttemptState::fenced;
    ++fences_;
  }
  closed_ = true;
  return Status::success();
}

SyncSchedulerSnapshot SyncObjectScheduler::snapshot() const {
  return SyncSchedulerSnapshot{objects_, attempts_, assignments_, fences_,
                               late_completions_, verification_failures_,
                               commits_, reserved_staging_bytes_, closed_};
}

} // namespace iotox::sync
