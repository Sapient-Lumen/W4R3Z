#pragma once

#include "slopos/e0/dispatch_cut.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <tuple>

namespace slopos::e0::winner_intent {

// WinnerIntentJoin V1 closes one exact representation seam. A provider winner
// *value* is copyable evidence. The model's premise instead contains one
// hypothetical, externally constituted, noncopyable live winner lease bound to
// one exact operation and one exact recipient interface. The only positive
// transition consumes that shared lease and atomically creates one retained
// DispatchCut C2 intent. No response bytes, query, restart, recovery path, or
// detached replay can create or restore the lease.
//
// The premise is deliberately not constructible from local evidence. This
// relation does not identify a real provider, prove atomic durability, install
// owner policy, authenticate a recipient, or prove global one-use across
// clones/restores of the complete premise.
enum class Phase : std::uint8_t {
  winner_live = 0,
  query_only,
  dispatch_active,
  fail_stop,
};

enum class Lease : std::uint8_t {
  live = 0,
  consumed,
  lost,
};

enum class Recipient : std::uint8_t {
  none = 0,
  a,
  b,
};

enum class Outcome : std::uint8_t {
  applied = 0,
  rejected,
  environment_impossible,
};

enum class Event : std::uint8_t {
  copy_winner_to_a = 0,
  copy_winner_to_b,
  join_a_exact,
  join_b_exact,
  join_a_subject_mismatch,
  join_b_subject_mismatch,
  join_a_route_mismatch,
  join_b_route_mismatch,
  join_a_malformed,
  join_b_malformed,
  drop_winner,
  query_provider_applied,
  query_provider_unknown,
  detached_winner_replay,
  restart,
  recover_join_attempt,
  dispatch_activate_exact_readback,
  dispatch_activate_readback_mismatch,
  dispatch_enter_exact,
  dispatch_enter_subject_mismatch,
  dispatch_enter_malformed,
  dispatch_enter_route_override,
  dispatch_endpoint_effect,
  dispatch_endpoint_serialized_no_effect,
  dispatch_endpoint_nonreturn,
  dispatch_endpoint_malformed,
  dispatch_retain_result1,
  dispatch_publish_result1,
  dispatch_query_exact_effect,
  dispatch_query_serialized_no_effect,
  dispatch_query_absent,
  dispatch_query_unavailable,
  dispatch_query_malformed,
  dispatch_query_wrong_binding,
  dispatch_query_split_view,
  dispatch_retain_result2,
  dispatch_publish_result2,
  dispatch_recover_mint_attempt,
  dispatch_recover_submit_attempt,
};

inline constexpr std::array<Event, 39U> kEvents{{
    Event::copy_winner_to_a,
    Event::copy_winner_to_b,
    Event::join_a_exact,
    Event::join_b_exact,
    Event::join_a_subject_mismatch,
    Event::join_b_subject_mismatch,
    Event::join_a_route_mismatch,
    Event::join_b_route_mismatch,
    Event::join_a_malformed,
    Event::join_b_malformed,
    Event::drop_winner,
    Event::query_provider_applied,
    Event::query_provider_unknown,
    Event::detached_winner_replay,
    Event::restart,
    Event::recover_join_attempt,
    Event::dispatch_activate_exact_readback,
    Event::dispatch_activate_readback_mismatch,
    Event::dispatch_enter_exact,
    Event::dispatch_enter_subject_mismatch,
    Event::dispatch_enter_malformed,
    Event::dispatch_enter_route_override,
    Event::dispatch_endpoint_effect,
    Event::dispatch_endpoint_serialized_no_effect,
    Event::dispatch_endpoint_nonreturn,
    Event::dispatch_endpoint_malformed,
    Event::dispatch_retain_result1,
    Event::dispatch_publish_result1,
    Event::dispatch_query_exact_effect,
    Event::dispatch_query_serialized_no_effect,
    Event::dispatch_query_absent,
    Event::dispatch_query_unavailable,
    Event::dispatch_query_malformed,
    Event::dispatch_query_wrong_binding,
    Event::dispatch_query_split_view,
    Event::dispatch_retain_result2,
    Event::dispatch_publish_result2,
    Event::dispatch_recover_mint_attempt,
    Event::dispatch_recover_submit_attempt,
}};

struct State final {
  Phase phase{Phase::winner_live};
  Lease lease{Lease::live};
  Recipient recipient{Recipient::none};
  bool a_copy_observed{false};
  bool b_copy_observed{false};
  bool restarted{false};
  dispatch::State downstream{dispatch::c1_model_premise()};

  [[nodiscard]] friend constexpr bool operator==(
      const State&, const State&) noexcept = default;
  [[nodiscard]] friend constexpr bool operator<(
      const State& lhs, const State& rhs) noexcept {
    return std::tie(lhs.phase, lhs.lease, lhs.recipient,
                    lhs.a_copy_observed, lhs.b_copy_observed, lhs.restarted,
                    lhs.downstream) <
           std::tie(rhs.phase, rhs.lease, rhs.recipient,
                    rhs.a_copy_observed, rhs.b_copy_observed, rhs.restarted,
                    rhs.downstream);
  }
};

struct ReopenView final {
  bool intent_persisted{false};
  Recipient recipient{Recipient::none};
  bool restarted{true};
  dispatch::ReopenView downstream{};

  [[nodiscard]] friend constexpr bool operator==(
      const ReopenView&, const ReopenView&) noexcept = default;
  [[nodiscard]] friend constexpr bool operator<(
      const ReopenView& lhs, const ReopenView& rhs) noexcept {
    return std::tie(lhs.intent_persisted, lhs.recipient, lhs.restarted,
                    lhs.downstream) <
           std::tie(rhs.intent_persisted, rhs.recipient, rhs.restarted,
                    rhs.downstream);
  }
};

struct Step final {
  Outcome outcome{Outcome::rejected};
  State state{};
  bool winner_value_copied{false};
  bool lease_consumed{false};
  bool recipient_bound{false};
  bool intent_persisted{false};
  bool validation_failed{false};
  bool observation_only{false};
  bool query_observed{false};
  bool response_lost{false};
  bool downstream_effect_emitted{false};
  bool downstream_pending_activation_consumed{false};
  bool downstream_permit_consumed{false};
  bool downstream_result_retained{false};
  bool downstream_publication_appended{false};

  [[nodiscard]] friend constexpr bool operator==(
      const Step&, const Step&) noexcept = default;
};

[[nodiscard]] State winner_lease_model_premise() noexcept;
[[nodiscard]] bool invariant(const State& state) noexcept;
[[nodiscard]] Step step(const State& state, Event event) noexcept;
[[nodiscard]] ReopenView reopen_view(const State& state) noexcept;

[[nodiscard]] constexpr bool authority_adapter_present() noexcept {
  return false;
}
[[nodiscard]] constexpr bool provider_adapter_present() noexcept {
  return false;
}
[[nodiscard]] constexpr bool response_value_can_mint_lease() noexcept {
  return false;
}
[[nodiscard]] constexpr bool detached_response_can_mint_lease() noexcept {
  return false;
}
[[nodiscard]] constexpr bool query_can_mint_lease() noexcept {
  return false;
}
[[nodiscard]] constexpr bool recovery_can_join() noexcept {
  return false;
}
[[nodiscard]] constexpr bool exact_join_is_atomic_in_model() noexcept {
  return true;
}
[[nodiscard]] constexpr bool global_one_use_proved() noexcept {
  return false;
}

[[nodiscard]] constexpr std::uint8_t persisted_intent_count(
    const State& state) noexcept {
  return state.phase == Phase::dispatch_active ? 1U : 0U;
}
[[nodiscard]] constexpr std::uint8_t live_lease_count(
    const State& state) noexcept {
  return state.lease == Lease::live ? 1U : 0U;
}

[[nodiscard]] std::string_view to_string(Phase value) noexcept;
[[nodiscard]] std::string_view to_string(Lease value) noexcept;
[[nodiscard]] std::string_view to_string(Recipient value) noexcept;
[[nodiscard]] std::string_view to_string(Outcome value) noexcept;
[[nodiscard]] std::string_view to_string(Event value) noexcept;
[[nodiscard]] std::string state_key(const State& state);
[[nodiscard]] std::string reopen_view_key(const ReopenView& view);
[[nodiscard]] std::string reopen_view_key(const State& state);

}  // namespace slopos::e0::winner_intent
