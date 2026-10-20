#include "iotox/sync_route_selector.hpp"

#include "test_harness.hpp"

#include <array>

namespace {

iotox::routes::ToxPublicKey key(std::uint8_t value) {
  iotox::routes::ToxPublicKey result{};
  result.fill(value);
  return result;
}

iotox::security::SigningPublicKey principal(std::uint8_t value) {
  iotox::security::SigningPublicKey result{};
  result.fill(value);
  return result;
}

iotox::sync::SyncRouteCandidate candidate(
    std::uint8_t route, std::uint32_t admitted, std::uint32_t maximum,
    std::uint32_t restarts = 0U, std::uint8_t owner = 0x71U,
    iotox::ToxRoute tox_route = iotox::ToxRoute::native) {
  iotox::sync::SyncRouteCandidate result;
  result.carrier.carrier_class = iotox::sync::SyncCarrierClass::auxiliary;
  result.carrier.route_key = key(route);
  result.carrier.worker_id = route;
  result.carrier.friend_number = route;
  result.carrier.online_epoch = 1U;
  result.carrier.remote_route_generation = 1U;
  result.carrier.remote_coordinator_route_key = key(0x11U);
  result.carrier.primary_authority_online_epoch = 1U;
  result.remote_principal = principal(owner);
  result.network.tox_route = tox_route;
  result.maximum_work = maximum;
  result.admitted_work = admitted;
  result.restart_count = restarts;
  return result;
}

} // namespace

IOTOX_TEST("sync fixed route selection preserves stable key order and skips full routes") {
  const std::array candidates{
      candidate(0x33U, 0U, 8U), candidate(0x22U, 8U, 8U),
      candidate(0x44U, 0U, 8U)};
  auto selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates,
      principal(0x71U));
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x33U));
}

IOTOX_TEST("sync adaptive route selection uses exact utilization restart and key ties") {
  const std::array candidates{
      candidate(0x22U, 4U, 8U), candidate(0x33U, 1U, 4U, 2U),
      candidate(0x44U, 2U, 8U, 1U), candidate(0x55U, 0U, 8U, 7U)};
  auto selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, candidates,
      principal(0x71U));
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x55U));

  const std::array tied{
      candidate(0x44U, 1U, 4U, 1U), candidate(0x33U, 2U, 8U, 2U),
      candidate(0x22U, 4U, 16U, 1U)};
  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, tied,
      principal(0x71U));
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x22U));
}

IOTOX_TEST("sync route selection fences principal exclusion capacity and malformed truth") {
  std::array candidates{
      candidate(0x22U, 0U, 8U), candidate(0x33U, 0U, 8U),
      candidate(0x44U, 0U, 8U, 0U, 0x72U)};
  auto selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, candidates,
      principal(0x71U), candidates[0U].carrier);
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x33U));

  candidates[1U].admitted_work = candidates[1U].maximum_work;
  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, candidates,
      principal(0x71U), candidates[0U].carrier);
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() == iotox::ErrorCode::unavailable);

  candidates[1U].admitted_work = candidates[1U].maximum_work + 1U;
  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates,
      principal(0x71U));
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync route selection reserves the complete requested work set") {
  std::array candidates{
      candidate(0x22U, 7U, 8U), candidate(0x33U, 6U, 8U)};
  auto selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates,
      principal(0x71U), std::nullopt, 2U);
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x33U));

  candidates[1U].admitted_work = 7U;
  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, candidates,
      principal(0x71U), std::nullopt, 2U);
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() == iotox::ErrorCode::unavailable);

  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates,
      principal(0x71U), std::nullopt, 0U);
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() ==
              iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST(
    "sync route set selection gives repeated principals distinct carriers") {
  const std::array candidates{
      candidate(0x22U, 0U, 8U),
      candidate(0x33U, 0U, 8U),
      candidate(0x44U, 0U, 8U, 0U, 0x72U)};
  const std::array principals{
      principal(0x71U), principal(0x71U), principal(0x72U)};
  auto selected = iotox::sync::select_distinct_sync_routes(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates, principals);
  IOTOX_CHECK(selected.ok() && selected.value().size() == 3U);
  IOTOX_CHECK(selected.value()[0U].carrier.route_key == key(0x22U));
  IOTOX_CHECK(selected.value()[1U].carrier.route_key == key(0x33U));
  IOTOX_CHECK(selected.value()[2U].carrier.route_key == key(0x44U));

  const std::array exhausted{
      principal(0x71U), principal(0x71U), principal(0x71U)};
  selected = iotox::sync::select_distinct_sync_routes(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates, exhausted);
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() == iotox::ErrorCode::unavailable);

  const std::array<iotox::security::SigningPublicKey, 0U> empty{};
  selected = iotox::sync::select_distinct_sync_routes(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates, empty);
  IOTOX_CHECK(!selected.ok());
  IOTOX_CHECK(selected.status().code() ==
              iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("sync route selection policy grammar is frozen") {
  IOTOX_CHECK(iotox::sync::parse_sync_route_selection_policy("fixed").ok());
  IOTOX_CHECK(iotox::sync::parse_sync_route_selection_policy("adaptive").ok());
  IOTOX_CHECK(!iotox::sync::parse_sync_route_selection_policy("round-robin").ok());
  IOTOX_CHECK(iotox::sync::to_string(
                  iotox::sync::SyncRouteSelectionPolicy::fixed) == "fixed");
  IOTOX_CHECK(iotox::sync::to_string(
                  iotox::sync::SyncRouteSelectionPolicy::adaptive) ==
              "adaptive");
}

IOTOX_TEST("sync route failover policy grammar is frozen") {
  auto available =
      iotox::sync::parse_sync_route_failover_policy("available");
  auto fail_closed =
      iotox::sync::parse_sync_route_failover_policy("fail-closed");
  IOTOX_CHECK(available.ok());
  IOTOX_CHECK(fail_closed.ok());
  IOTOX_CHECK(!iotox::sync::parse_sync_route_failover_policy("native").ok());
  IOTOX_CHECK(iotox::sync::to_string(available.value()) == "available");
  IOTOX_CHECK(iotox::sync::to_string(fail_closed.value()) == "fail-closed");
  IOTOX_CHECK(iotox::sync::sync_route_reassignment_allowed(
      available.value()));
  IOTOX_CHECK(!iotox::sync::sync_route_reassignment_allowed(
      fail_closed.value()));
  IOTOX_CHECK(iotox::sync::to_string(
                  static_cast<iotox::sync::SyncRouteFailoverPolicy>(0U)) ==
              "unknown");
}

IOTOX_TEST("sync route class filters exact constructed worker networks") {
  const std::array candidates{
      candidate(0x11U, 0U, 8U, 0U, 0x71U,
                iotox::ToxRoute::native),
      candidate(0x22U, 0U, 8U, 0U, 0x71U,
                iotox::ToxRoute::tor),
      candidate(0x33U, 0U, 8U, 0U, 0x71U,
                iotox::ToxRoute::i2p_construction)};
  auto selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::fixed, candidates,
      principal(0x71U), std::nullopt, 1U,
      iotox::sync::SyncRouteClassConstraint::tox_tor);
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x22U));

  selected = iotox::sync::select_sync_route(
      iotox::sync::SyncRouteSelectionPolicy::adaptive, candidates,
      principal(0x71U), std::nullopt, 1U,
      iotox::sync::SyncRouteClassConstraint::tox_i2p);
  IOTOX_CHECK(selected.ok());
  IOTOX_CHECK(selected.value().carrier.route_key == key(0x33U));

  IOTOX_CHECK(iotox::sync::parse_sync_route_class_constraint("any").ok());
  IOTOX_CHECK(iotox::sync::parse_sync_route_class_constraint("tox/native").ok());
  IOTOX_CHECK(iotox::sync::parse_sync_route_class_constraint("tox/tor").ok());
  IOTOX_CHECK(iotox::sync::parse_sync_route_class_constraint(
                  "tox/i2p-construction").ok());
  IOTOX_CHECK(iotox::sync::parse_sync_route_class_constraint("tox/i2p").ok());
  IOTOX_CHECK(iotox::sync::to_string(
                  iotox::sync::parse_sync_route_class_constraint(
                      "tox/i2p-construction").value()) == "tox/i2p");
  IOTOX_CHECK(iotox::sync::to_string(
                  iotox::sync::SyncRouteClassConstraint::tox_tor) ==
              "tox/tor");
}
