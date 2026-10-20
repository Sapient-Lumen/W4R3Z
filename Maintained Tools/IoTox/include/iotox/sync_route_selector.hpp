#pragma once

#include "iotox/sync_service.hpp"

#include <cstdint>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::sync {

enum class SyncRouteSelectionPolicy : std::uint8_t {
  fixed = 1U,
  adaptive = 2U,
};

// Replacement policy is intentionally separate from initial placement. The
// fail-closed mode leaves a fenced pull awaiting explicit operator action
// after carrier loss; it never treats another ready route as equivalent.
enum class SyncRouteFailoverPolicy : std::uint8_t {
  available = 1U,
  fail_closed = 2U,
};

// Owner-local carrier network constraint. `any` preserves primary fallback;
// every named class requires an authenticated auxiliary worker constructed in
// that exact network context.
enum class SyncRouteClassConstraint : std::uint8_t {
  any = 1U,
  tox_native = 2U,
  tox_tor = 3U,
  tox_i2p = 4U,
};

struct SyncRouteCandidate {
  SyncTransferCarrier carrier;
  security::SigningPublicKey remote_principal{};
  NetworkStack network{};
  std::uint32_t maximum_work{0U};
  std::uint32_t admitted_work{0U};
  std::uint32_t restart_count{0U};
  bool range_transfer_negotiated{false};
  bool content_transfer_negotiated{false};

  // Load counters may change while one authenticated incarnation remains
  // present. Equality is intentionally incarnation/principal identity only.
  [[nodiscard]] bool operator==(const SyncRouteCandidate &other) const {
    return carrier == other.carrier &&
           remote_principal == other.remote_principal &&
           network == other.network &&
           range_transfer_negotiated == other.range_transfer_negotiated &&
           content_transfer_negotiated ==
               other.content_transfer_negotiated;
  }
};

[[nodiscard]] std::string_view to_string(
    SyncRouteSelectionPolicy policy) noexcept;
[[nodiscard]] Result<SyncRouteSelectionPolicy>
parse_sync_route_selection_policy(std::string_view value);
[[nodiscard]] std::string_view to_string(
    SyncRouteFailoverPolicy policy) noexcept;
[[nodiscard]] Result<SyncRouteFailoverPolicy>
parse_sync_route_failover_policy(std::string_view value);
[[nodiscard]] bool sync_route_reassignment_allowed(
    SyncRouteFailoverPolicy policy) noexcept;
[[nodiscard]] std::string_view to_string(
    SyncRouteClassConstraint constraint) noexcept;
[[nodiscard]] Result<SyncRouteClassConstraint>
parse_sync_route_class_constraint(std::string_view value);
[[nodiscard]] bool sync_route_class_matches(
    SyncRouteClassConstraint constraint,
    const NetworkStack &network) noexcept;

// Selects only a ready/authenticated candidate set supplied by the Agent.
// `fixed` preserves stable route-key order. `adaptive` minimizes exact current
// utilization, then restart history, then route key. Neither policy migrates
// healthy work or uses unverified performance claims.
[[nodiscard]] Result<SyncRouteCandidate> select_sync_route(
    SyncRouteSelectionPolicy policy,
    std::span<const SyncRouteCandidate> candidates,
    const security::SigningPublicKey &remote_principal,
    std::optional<SyncTransferCarrier> excluded = std::nullopt,
    std::uint32_t required_work = 1U,
    SyncRouteClassConstraint route_class = SyncRouteClassConstraint::any);

// Atomically plans one distinct carrier for every source-path record. A
// stable principal may repeat, but an exact carrier may not. This is initial
// placement only; it neither reserves provider work nor permits replacement.
[[nodiscard]] Result<std::vector<SyncRouteCandidate>>
select_distinct_sync_routes(
    SyncRouteSelectionPolicy policy,
    std::span<const SyncRouteCandidate> candidates,
    std::span<const security::SigningPublicKey> remote_principals,
    std::uint32_t required_work = 1U,
    SyncRouteClassConstraint route_class = SyncRouteClassConstraint::any);

} // namespace iotox::sync
