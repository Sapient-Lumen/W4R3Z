#include "iotox/sync_scheduler.hpp"

#include "test_harness.hpp"

#include <array>

namespace {

iotox::routes::ToxPublicKey route_key(std::uint8_t value) {
  iotox::routes::ToxPublicKey key{};
  key.fill(value);
  return key;
}

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest output{};
  output.fill(value);
  return output;
}

iotox::routes::Coordinator ready_coordinator() {
  iotox::routes::RouteSet set;
  set.generation = 1U;
  set.stable_device_principal.fill(0x71U);
  set.coordinator_tox_public_key = route_key(0x11U);
  set.members = {
      {route_key(0x11U), iotox::routes::Role::protected_route,
       iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
      {route_key(0x22U), iotox::routes::Role::bulk,
       iotox::routes::ConnectionClass::tcp, 2U, 1U, 0U},
      {route_key(0x33U), iotox::routes::Role::bulk,
       iotox::routes::ConnectionClass::tcp, 2U, 1U, 0U},
  };
  auto created = iotox::routes::Coordinator::create(set);
  IOTOX_CHECK(created.ok());
  auto coordinator = std::move(created).value();
  for (std::uint8_t value :
       std::array<std::uint8_t, 3U>{0x11U, 0x22U, 0x33U}) {
    const std::uint64_t worker = value;
    IOTOX_CHECK(coordinator.begin_connecting(route_key(value), worker).ok());
    iotox::routes::RouteProof proof{
        route_key(value), set.stable_device_principal, 1U,
        iotox::routes::kRouteProtocolVersion,
        iotox::routes::ConnectionClass::tcp, worker, true};
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(route_key(value), worker).ok());
  }
  return coordinator;
}

} // namespace

IOTOX_TEST("sync scheduler fences attempts and rejects late completion") {
  auto coordinator = ready_coordinator();
  std::uint64_t next_attempt = 100U;
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 4U;
  config.maximum_attempts = 8U;
  config.make_attempt_id = [&next_attempt]() -> iotox::Result<std::uint64_t> {
    return next_attempt++;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, digest(0x51U), 4096U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  IOTOX_CHECK(scheduler.add_object(object).ok());
  IOTOX_CHECK(!scheduler.assign(
                   object.kind, object.identity, route_key(0x11U), 0x11U).ok());

  auto first = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 0x22U);
  IOTOX_CHECK_MSG(first.ok(), first.status().message());
  IOTOX_CHECK(!scheduler.assign(
                   object.kind, object.identity, route_key(0x33U), 0x33U).ok());
  IOTOX_CHECK(coordinator.snapshot().members[1U].admitted_work == 1U);
  auto fenced = scheduler.fence_route(route_key(0x22U), 0x22U);
  IOTOX_CHECK(fenced.ok() && fenced.value() == 1U);
  IOTOX_CHECK(coordinator.snapshot().members[1U].admitted_work == 0U);

  auto second = scheduler.assign(
      object.kind, object.identity, route_key(0x33U), 0x33U);
  IOTOX_CHECK_MSG(second.ok(), second.status().message());
  IOTOX_CHECK(second.value().attempt_id != first.value().attempt_id);
  IOTOX_CHECK(!scheduler.complete(
                   first.value().attempt_id, object.identity,
                   object.bytes).ok());
  IOTOX_CHECK(coordinator.snapshot().members[2U].admitted_work == 1U);
  IOTOX_CHECK(scheduler.complete(
                  second.value().attempt_id, object.identity,
                  object.bytes).ok());
  IOTOX_CHECK(scheduler.commit(second.value().attempt_id).ok());
  IOTOX_CHECK(scheduler.commit(second.value().attempt_id).ok());
  IOTOX_CHECK(coordinator.snapshot().members[2U].admitted_work == 0U);

  const auto snapshot = scheduler.snapshot();
  IOTOX_CHECK(snapshot.objects.front().state ==
              iotox::sync::ScheduledObjectState::committed);
  IOTOX_CHECK(snapshot.attempts[0U].state ==
              iotox::sync::TransferAttemptState::fenced);
  IOTOX_CHECK(snapshot.attempts[1U].state ==
              iotox::sync::TransferAttemptState::committed);
  IOTOX_CHECK(snapshot.assignments == 2U);
  IOTOX_CHECK(snapshot.fences == 1U);
  IOTOX_CHECK(snapshot.late_completions == 1U);
  IOTOX_CHECK(snapshot.commits == 1U);
  IOTOX_CHECK(snapshot.reserved_staging_bytes == 0U);
}

IOTOX_TEST("sync scheduler accepts a bounded transport capacity adapter") {
  std::uint16_t admitted = 0U;
  bool ready = true;
  iotox::sync::SyncObjectScheduler::CapacitySeams capacity;
  capacity.admit = [&admitted, &ready](const auto &, std::uint64_t) {
    if (!ready || admitted != 0U) {
      return iotox::Status{iotox::ErrorCode::resource_exhausted,
                           "primary sync capacity is unavailable"};
    }
    ++admitted;
    return iotox::Status::success();
  };
  capacity.release = [&admitted, &ready](const auto &, std::uint64_t) {
    if (!ready) {
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "primary sync incarnation is closed"};
    }
    if (admitted == 0U) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "primary sync capacity underflow"};
    }
    --admitted;
    return iotox::Status::success();
  };
  capacity.already_released = [&admitted, &ready](const auto &,
                                                   std::uint64_t) {
    return iotox::Result<bool>{!ready && admitted == 0U};
  };
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 1U;
  config.maximum_attempts = 2U;
  config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 650U;
  };
  iotox::sync::SyncObjectScheduler scheduler(std::move(capacity),
                                              std::move(config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, digest(0x59U), 32U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(object.kind, object.identity,
                                  route_key(0x44U), 7U);
  IOTOX_CHECK(attempt.ok());
  IOTOX_CHECK(admitted == 1U);
  IOTOX_CHECK(scheduler.complete(attempt.value().attempt_id, object.identity,
                                 object.bytes).ok());
  IOTOX_CHECK(scheduler.commit(attempt.value().attempt_id).ok());
  IOTOX_CHECK(admitted == 0U);
}

IOTOX_TEST("sync scheduler verification failure frees only its route capacity") {
  auto coordinator = ready_coordinator();
  std::uint64_t attempt_id = 700U;
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 2U;
  config.maximum_attempts = 2U;
  config.make_attempt_id = [&attempt_id]() -> iotox::Result<std::uint64_t> {
    return attempt_id++;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord first{
      iotox::sync::SyncObjectKind::artifact, digest(0x61U), 10U};
  const iotox::sync::SyncObjectRecord second{
      iotox::sync::SyncObjectKind::manifest, digest(0x62U), 20U};
  IOTOX_CHECK(scheduler.add_object(first).ok());
  IOTOX_CHECK(scheduler.add_object(second).ok());
  auto first_attempt = scheduler.assign(
      first.kind, first.identity, route_key(0x22U), 0x22U);
  auto second_attempt = scheduler.assign(
      second.kind, second.identity, route_key(0x33U), 0x33U);
  IOTOX_CHECK(first_attempt.ok() && second_attempt.ok());
  IOTOX_CHECK(!scheduler.commit(first_attempt.value().attempt_id).ok());
  IOTOX_CHECK(!scheduler.complete(
                   first_attempt.value().attempt_id, digest(0x99U), 10U).ok());
  auto state = coordinator.snapshot();
  IOTOX_CHECK(state.members[1U].admitted_work == 0U);
  IOTOX_CHECK(state.members[2U].admitted_work == 1U);
  IOTOX_CHECK(scheduler.complete(
                  second_attempt.value().attempt_id, second.identity,
                  second.bytes).ok());
  IOTOX_CHECK(!scheduler.commit(first_attempt.value().attempt_id).ok());
  IOTOX_CHECK(scheduler.commit(second_attempt.value().attempt_id).ok());
  IOTOX_CHECK(scheduler.snapshot().verification_failures == 1U);
}

IOTOX_TEST("sync scheduler composes with coordinator authentication loss") {
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 1U;
  config.maximum_attempts = 2U;
  config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 901U;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, digest(0x81U), 50U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 0x22U);
  IOTOX_CHECK(attempt.ok());
  IOTOX_CHECK(coordinator.authentication_lost(
                  route_key(0x22U), 0x22U).ok());
  auto fenced = scheduler.fence_route(route_key(0x22U), 0x22U);
  IOTOX_CHECK_MSG(fenced.ok(), fenced.status().message());
  IOTOX_CHECK(fenced.value() == 1U);
  IOTOX_CHECK(!scheduler.complete(
                   attempt.value().attempt_id, object.identity,
                   object.bytes).ok());
  const auto snapshot = scheduler.snapshot();
  IOTOX_CHECK(!snapshot.attempts.front().route_capacity_reserved);
  IOTOX_CHECK(!snapshot.attempts.front().staging_bytes_reserved);
  IOTOX_CHECK(snapshot.objects.front().state ==
              iotox::sync::ScheduledObjectState::pending);
}

IOTOX_TEST("sync scheduler close fences work and is idempotent") {
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 1U;
  config.maximum_attempts = 2U;
  config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 1001U;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::manifest, digest(0x91U), 75U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  IOTOX_CHECK(scheduler.assign(
                  object.kind, object.identity, route_key(0x22U), 0x22U).ok());
  IOTOX_CHECK(scheduler.close().ok());
  IOTOX_CHECK(scheduler.close().ok());
  IOTOX_CHECK(coordinator.snapshot().members[1U].admitted_work == 0U);
  IOTOX_CHECK(scheduler.snapshot().closed);
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 0U);
  IOTOX_CHECK(!scheduler.assign(
                   object.kind, object.identity, route_key(0x22U), 0x22U).ok());
  IOTOX_CHECK(!scheduler.add_object(object).ok());
}

IOTOX_TEST("sync scheduler destruction releases ordinary live capacity") {
  auto coordinator = ready_coordinator();
  {
    iotox::sync::SyncObjectScheduler::Config config;
    config.maximum_objects = 1U;
    config.maximum_attempts = 1U;
    config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
      return 1101U;
    };
    iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
    const iotox::sync::SyncObjectRecord object{
        iotox::sync::SyncObjectKind::artifact, digest(0x92U), 80U};
    IOTOX_CHECK(scheduler.add_object(object).ok());
    IOTOX_CHECK(scheduler.assign(
                    object.kind, object.identity, route_key(0x33U), 0x33U).ok());
    IOTOX_CHECK(coordinator.snapshot().members[2U].admitted_work == 1U);
  }
  IOTOX_CHECK(coordinator.snapshot().members[2U].admitted_work == 0U);
}

IOTOX_TEST("sync scheduler reserves aggregate in-flight staging bytes") {
  auto coordinator = ready_coordinator();
  std::uint64_t attempt_id = 1201U;
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 2U;
  config.maximum_attempts = 3U;
  config.maximum_staging_bytes = 100U;
  config.make_attempt_id = [&attempt_id]() -> iotox::Result<std::uint64_t> {
    return attempt_id++;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord first{
      iotox::sync::SyncObjectKind::artifact, digest(0xa1U), 60U};
  const iotox::sync::SyncObjectRecord second{
      iotox::sync::SyncObjectKind::manifest, digest(0xa2U), 50U};
  IOTOX_CHECK(scheduler.add_object(first).ok());
  IOTOX_CHECK(scheduler.add_object(second).ok());
  auto first_attempt = scheduler.assign(
      first.kind, first.identity, route_key(0x22U), 0x22U);
  IOTOX_CHECK(first_attempt.ok());
  IOTOX_CHECK(first_attempt.value().staging_bytes_reserved);
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 60U);
  auto refused = scheduler.assign(
      second.kind, second.identity, route_key(0x33U), 0x33U);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::resource_exhausted);
  IOTOX_CHECK(coordinator.snapshot().members[2U].admitted_work == 0U);
  IOTOX_CHECK(scheduler.fence_route(route_key(0x22U), 0x22U).ok());
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 0U);
  auto second_attempt = scheduler.assign(
      second.kind, second.identity, route_key(0x33U), 0x33U);
  IOTOX_CHECK(second_attempt.ok());
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 50U);
  IOTOX_CHECK(scheduler.complete(second_attempt.value().attempt_id,
                                 second.identity, second.bytes).ok());
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 50U);
  IOTOX_CHECK(scheduler.commit(second_attempt.value().attempt_id).ok());
  IOTOX_CHECK(scheduler.snapshot().reserved_staging_bytes == 0U);
}

IOTOX_TEST("sync scheduler fences one attempt without disturbing its route peer") {
  auto coordinator = ready_coordinator();
  std::uint64_t attempt_id = 1301U;
  iotox::sync::SyncObjectScheduler::Config config;
  config.maximum_objects = 2U;
  config.maximum_attempts = 2U;
  config.maximum_staging_bytes = 100U;
  config.make_attempt_id = [&attempt_id]() -> iotox::Result<std::uint64_t> {
    return attempt_id++;
  };
  iotox::sync::SyncObjectScheduler scheduler(coordinator, std::move(config));
  const iotox::sync::SyncObjectRecord first{
      iotox::sync::SyncObjectKind::artifact, digest(0xb1U), 30U};
  const iotox::sync::SyncObjectRecord second{
      iotox::sync::SyncObjectKind::manifest, digest(0xb2U), 40U};
  IOTOX_CHECK(scheduler.add_object(first).ok());
  IOTOX_CHECK(scheduler.add_object(second).ok());
  auto first_attempt = scheduler.assign(
      first.kind, first.identity, route_key(0x22U), 0x22U);
  auto second_attempt = scheduler.assign(
      second.kind, second.identity, route_key(0x22U), 0x22U);
  IOTOX_CHECK(first_attempt.ok() && second_attempt.ok());
  IOTOX_CHECK(scheduler.fence_attempt(first_attempt.value().attempt_id).ok());
  IOTOX_CHECK(scheduler.fence_attempt(first_attempt.value().attempt_id).ok());
  const auto state = scheduler.snapshot();
  IOTOX_CHECK(state.attempts[0U].state ==
              iotox::sync::TransferAttemptState::fenced);
  IOTOX_CHECK(state.attempts[1U].state ==
              iotox::sync::TransferAttemptState::active);
  IOTOX_CHECK(state.reserved_staging_bytes == 40U);
  IOTOX_CHECK(coordinator.snapshot().members[1U].admitted_work == 1U);
}
