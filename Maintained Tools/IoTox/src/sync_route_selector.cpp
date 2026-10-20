#include "iotox/sync_route_selector.hpp"

#include <algorithm>
#include <limits>

namespace iotox::sync {
namespace {

bool empty_principal(const security::SigningPublicKey &principal) {
  return std::all_of(principal.begin(), principal.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

bool candidate_valid(const SyncRouteCandidate &candidate) {
  return candidate.carrier.carrier_class == SyncCarrierClass::auxiliary &&
         candidate.carrier.worker_id != 0U &&
         candidate.carrier.online_epoch != 0U &&
         candidate.carrier.remote_route_generation != 0U &&
         candidate.carrier.primary_authority_online_epoch != 0U &&
         !empty_principal(candidate.remote_principal) &&
         candidate.maximum_work != 0U &&
         candidate.admitted_work <= candidate.maximum_work;
}

bool fixed_before(const SyncRouteCandidate &left,
                  const SyncRouteCandidate &right) {
  if (left.carrier.route_key != right.carrier.route_key) {
    return left.carrier.route_key < right.carrier.route_key;
  }
  return left.carrier.worker_id < right.carrier.worker_id;
}

bool adaptive_before(const SyncRouteCandidate &left,
                     const SyncRouteCandidate &right) {
  const std::uint64_t left_scaled =
      static_cast<std::uint64_t>(left.admitted_work) * right.maximum_work;
  const std::uint64_t right_scaled =
      static_cast<std::uint64_t>(right.admitted_work) * left.maximum_work;
  if (left_scaled != right_scaled) return left_scaled < right_scaled;
  if (left.restart_count != right.restart_count) {
    return left.restart_count < right.restart_count;
  }
  return fixed_before(left, right);
}

} // namespace

std::string_view to_string(SyncRouteSelectionPolicy policy) noexcept {
  switch (policy) {
    case SyncRouteSelectionPolicy::fixed: return "fixed";
    case SyncRouteSelectionPolicy::adaptive: return "adaptive";
  }
  return "unknown";
}

Result<SyncRouteSelectionPolicy>
parse_sync_route_selection_policy(std::string_view value) {
  if (value == "fixed") return SyncRouteSelectionPolicy::fixed;
  if (value == "adaptive") return SyncRouteSelectionPolicy::adaptive;
  return Status{ErrorCode::invalid_argument,
                "sync route selection policy must be fixed or adaptive"};
}

std::string_view to_string(SyncRouteFailoverPolicy policy) noexcept {
  switch (policy) {
    case SyncRouteFailoverPolicy::available: return "available";
    case SyncRouteFailoverPolicy::fail_closed: return "fail-closed";
  }
  return "unknown";
}

Result<SyncRouteFailoverPolicy>
parse_sync_route_failover_policy(std::string_view value) {
  if (value == "available") return SyncRouteFailoverPolicy::available;
  if (value == "fail-closed") return SyncRouteFailoverPolicy::fail_closed;
  return Status{
      ErrorCode::invalid_argument,
      "sync route failover policy must be available or fail-closed"};
}

bool sync_route_reassignment_allowed(
    SyncRouteFailoverPolicy policy) noexcept {
  return policy == SyncRouteFailoverPolicy::available;
}

std::string_view to_string(SyncRouteClassConstraint constraint) noexcept {
  switch (constraint) {
    case SyncRouteClassConstraint::any: return "any";
    case SyncRouteClassConstraint::tox_native: return "tox/native";
    case SyncRouteClassConstraint::tox_tor: return "tox/tor";
    case SyncRouteClassConstraint::tox_i2p: return "tox/i2p";
  }
  return "unknown";
}

Result<SyncRouteClassConstraint>
parse_sync_route_class_constraint(std::string_view value) {
  if (value == "any") return SyncRouteClassConstraint::any;
  if (value == "tox/native") return SyncRouteClassConstraint::tox_native;
  if (value == "tox/tor") return SyncRouteClassConstraint::tox_tor;
  if (value == "tox/i2p" || value == "tox/i2p-construction") {
    return SyncRouteClassConstraint::tox_i2p;
  }
  return Status{
      ErrorCode::invalid_argument,
      "sync route class must be any, tox/native, tox/tor, or tox/i2p"};
}

bool sync_route_class_matches(
    SyncRouteClassConstraint constraint,
    const NetworkStack &network) noexcept {
  if (network.transport != TransportKind::tox) return false;
  switch (constraint) {
    case SyncRouteClassConstraint::any: return true;
    case SyncRouteClassConstraint::tox_native:
      return network.tox_route == ToxRoute::native;
    case SyncRouteClassConstraint::tox_tor:
      return network.tox_route == ToxRoute::tor;
    case SyncRouteClassConstraint::tox_i2p:
      return network.tox_route == ToxRoute::i2p ||
             network.tox_route == ToxRoute::i2p_construction;
  }
  return false;
}

Result<SyncRouteCandidate> select_sync_route(
    SyncRouteSelectionPolicy policy,
    std::span<const SyncRouteCandidate> candidates,
    const security::SigningPublicKey &remote_principal,
    std::optional<SyncTransferCarrier> excluded,
    std::uint32_t required_work,
    SyncRouteClassConstraint route_class) {
  if (policy != SyncRouteSelectionPolicy::fixed &&
      policy != SyncRouteSelectionPolicy::adaptive) {
    return Status{ErrorCode::invalid_argument,
                  "sync route selection policy is unknown"};
  }
  if (empty_principal(remote_principal)) {
    return Status{ErrorCode::invalid_argument,
                  "sync route selection principal is empty"};
  }
  if (required_work == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync route selection required work is zero"};
  }
  if (route_class != SyncRouteClassConstraint::any &&
      route_class != SyncRouteClassConstraint::tox_native &&
      route_class != SyncRouteClassConstraint::tox_tor &&
      route_class != SyncRouteClassConstraint::tox_i2p) {
    return Status{ErrorCode::invalid_argument,
                  "sync route class constraint is unknown"};
  }

  const SyncRouteCandidate *selected = nullptr;
  for (const SyncRouteCandidate &candidate : candidates) {
    if (!candidate_valid(candidate)) {
      return Status{ErrorCode::protocol_error,
                    "sync route candidate is malformed"};
    }
    if (candidate.remote_principal != remote_principal ||
        !sync_route_class_matches(route_class, candidate.network) ||
        required_work >
            candidate.maximum_work - candidate.admitted_work ||
        (excluded && candidate.carrier == *excluded)) {
      continue;
    }
    if (selected == nullptr ||
        (policy == SyncRouteSelectionPolicy::adaptive
             ? adaptive_before(candidate, *selected)
             : fixed_before(candidate, *selected))) {
      selected = &candidate;
    }
  }
  if (selected == nullptr) {
    return Status{ErrorCode::unavailable,
                  "no eligible authenticated bulk route is available"};
  }
  return *selected;
}

Result<std::vector<SyncRouteCandidate>> select_distinct_sync_routes(
    SyncRouteSelectionPolicy policy,
    std::span<const SyncRouteCandidate> candidates,
    std::span<const security::SigningPublicKey> remote_principals,
    std::uint32_t required_work,
    SyncRouteClassConstraint route_class) {
  if (remote_principals.empty()) {
    return Status{ErrorCode::invalid_argument,
                  "sync route source-path set is empty"};
  }
  std::vector<SyncRouteCandidate> remaining(candidates.begin(),
                                            candidates.end());
  std::vector<SyncRouteCandidate> selected;
  selected.reserve(remote_principals.size());
  for (const security::SigningPublicKey &principal : remote_principals) {
    auto route = select_sync_route(policy, remaining, principal,
                                   std::nullopt, required_work, route_class);
    if (!route)
      return route.status();
    selected.push_back(route.value());
    const SyncTransferCarrier selected_carrier = route.value().carrier;
    remaining.erase(
        std::remove_if(
            remaining.begin(), remaining.end(),
            [&selected_carrier](const SyncRouteCandidate &candidate) {
              return candidate.carrier == selected_carrier;
            }),
        remaining.end());
  }
  return selected;
}

} // namespace iotox::sync
