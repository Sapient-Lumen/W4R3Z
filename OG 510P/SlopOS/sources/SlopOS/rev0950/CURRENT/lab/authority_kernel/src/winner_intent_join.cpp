#include "slopos/e0/winner_intent_join.hpp"

#include <optional>
#include <sstream>

namespace slopos::e0::winner_intent {
namespace {

struct Flags final {
  bool copied{false};
  bool consumed{false};
  bool bound{false};
  bool intent{false};
  bool validation_failed{false};
  bool observation{false};
  bool query{false};
  bool lost{false};
  bool effect{false};
  bool pending_consumed{false};
  bool permit_consumed{false};
  bool result_retained{false};
  bool publication{false};
};

[[nodiscard]] Step accept(const State& state,
                          const Flags flags = {}) noexcept {
  return Step{Outcome::applied,
              state,
              flags.copied,
              flags.consumed,
              flags.bound,
              flags.intent,
              flags.validation_failed,
              flags.observation,
              flags.query,
              flags.lost,
              flags.effect,
              flags.pending_consumed,
              flags.permit_consumed,
              flags.result_retained,
              flags.publication};
}

[[nodiscard]] Step reject(const State& state) noexcept {
  return Step{Outcome::rejected, state};
}

[[nodiscard]] Step impossible(const State& state) noexcept {
  return Step{Outcome::environment_impossible, state};
}

[[nodiscard]] constexpr bool is_join_exact(const Event event) noexcept {
  return event == Event::join_a_exact || event == Event::join_b_exact;
}

[[nodiscard]] constexpr bool is_join_invalid(const Event event) noexcept {
  switch (event) {
    case Event::join_a_subject_mismatch:
    case Event::join_b_subject_mismatch:
    case Event::join_a_route_mismatch:
    case Event::join_b_route_mismatch:
    case Event::join_a_malformed:
    case Event::join_b_malformed:
      return true;
    default:
      return false;
  }
}

[[nodiscard]] constexpr Recipient join_recipient(const Event event) noexcept {
  switch (event) {
    case Event::join_a_exact:
    case Event::join_a_subject_mismatch:
    case Event::join_a_route_mismatch:
    case Event::join_a_malformed:
      return Recipient::a;
    case Event::join_b_exact:
    case Event::join_b_subject_mismatch:
    case Event::join_b_route_mismatch:
    case Event::join_b_malformed:
      return Recipient::b;
    default:
      return Recipient::none;
  }
}

[[nodiscard]] std::optional<dispatch::Event> downstream_event(
    const Event event) noexcept {
  switch (event) {
    case Event::dispatch_activate_exact_readback:
      return dispatch::Event::activate_exact_readback;
    case Event::dispatch_activate_readback_mismatch:
      return dispatch::Event::activate_readback_mismatch;
    case Event::dispatch_enter_exact:
      return dispatch::Event::enter_exact;
    case Event::dispatch_enter_subject_mismatch:
      return dispatch::Event::enter_subject_mismatch;
    case Event::dispatch_enter_malformed:
      return dispatch::Event::enter_malformed;
    case Event::dispatch_enter_route_override:
      return dispatch::Event::enter_route_override;
    case Event::dispatch_endpoint_effect:
      return dispatch::Event::endpoint_effect;
    case Event::dispatch_endpoint_serialized_no_effect:
      return dispatch::Event::endpoint_serialized_no_effect;
    case Event::dispatch_endpoint_nonreturn:
      return dispatch::Event::endpoint_nonreturn;
    case Event::dispatch_endpoint_malformed:
      return dispatch::Event::endpoint_malformed;
    case Event::dispatch_retain_result1:
      return dispatch::Event::retain_result1;
    case Event::dispatch_publish_result1:
      return dispatch::Event::publish_result1;
    case Event::dispatch_query_exact_effect:
      return dispatch::Event::query_exact_effect;
    case Event::dispatch_query_serialized_no_effect:
      return dispatch::Event::query_serialized_no_effect;
    case Event::dispatch_query_absent:
      return dispatch::Event::query_absent;
    case Event::dispatch_query_unavailable:
      return dispatch::Event::query_unavailable;
    case Event::dispatch_query_malformed:
      return dispatch::Event::query_malformed;
    case Event::dispatch_query_wrong_binding:
      return dispatch::Event::query_wrong_binding;
    case Event::dispatch_query_split_view:
      return dispatch::Event::query_split_view;
    case Event::dispatch_retain_result2:
      return dispatch::Event::retain_result2;
    case Event::dispatch_publish_result2:
      return dispatch::Event::publish_result2;
    case Event::dispatch_recover_mint_attempt:
      return dispatch::Event::recover_mint_attempt;
    case Event::dispatch_recover_submit_attempt:
      return dispatch::Event::recover_submit_attempt;
    default:
      return std::nullopt;
  }
}

[[nodiscard]] State cold_no_intent(State state) noexcept {
  state.phase = Phase::query_only;
  state.lease = Lease::lost;
  state.recipient = Recipient::none;
  state.a_copy_observed = false;
  state.b_copy_observed = false;
  state.restarted = true;
  state.downstream = dispatch::c1_model_premise();
  return state;
}

}  // namespace

State winner_lease_model_premise() noexcept { return State{}; }

bool invariant(const State& state) noexcept {
  if (!dispatch::invariant(state.downstream)) return false;

  const bool c1 = state.downstream == dispatch::c1_model_premise();
  switch (state.phase) {
    case Phase::winner_live:
      return state.lease == Lease::live &&
             state.recipient == Recipient::none && c1 && !state.restarted;
    case Phase::query_only:
      return state.lease == Lease::lost &&
             state.recipient == Recipient::none &&
             !state.a_copy_observed && !state.b_copy_observed && c1;
    case Phase::dispatch_active:
      return state.lease == Lease::consumed &&
             state.recipient != Recipient::none &&
             !state.a_copy_observed && !state.b_copy_observed && !c1;
    case Phase::fail_stop:
      return state.lease == Lease::consumed &&
             state.recipient == Recipient::none &&
             !state.a_copy_observed && !state.b_copy_observed && c1;
  }
  return false;
}

ReopenView reopen_view(const State& state) noexcept {
  if (state.phase == Phase::dispatch_active) {
    State cold = state;
    const dispatch::Step restarted =
        dispatch::step(cold.downstream, dispatch::Event::restart);
    if (restarted.outcome == dispatch::Outcome::applied) {
      cold.downstream = restarted.state;
    }
    return ReopenView{true, state.recipient, true,
                      dispatch::reopen_view(cold.downstream)};
  }
  return ReopenView{false, Recipient::none, true,
                    dispatch::reopen_view(dispatch::c1_model_premise())};
}

Step step(const State& before, const Event event) noexcept {
  if (event == Event::copy_winner_to_a ||
      event == Event::copy_winner_to_b) {
    if (before.phase != Phase::winner_live || before.lease != Lease::live) {
      return reject(before);
    }
    State after = before;
    if (event == Event::copy_winner_to_a) {
      after.a_copy_observed = true;
    } else {
      after.b_copy_observed = true;
    }
    return accept(after, Flags{.copied = true, .observation = true});
  }

  if (is_join_exact(event)) {
    if (before.phase != Phase::winner_live || before.lease != Lease::live) {
      return reject(before);
    }
    const dispatch::Step plan =
        dispatch::step(before.downstream, dispatch::Event::plan_dispatch);
    if (plan.outcome != dispatch::Outcome::applied) return reject(before);
    State after = before;
    after.phase = Phase::dispatch_active;
    after.lease = Lease::consumed;
    after.recipient = join_recipient(event);
    after.a_copy_observed = false;
    after.b_copy_observed = false;
    after.downstream = plan.state;
    return accept(after, Flags{.consumed = true,
                               .bound = true,
                               .intent = true});
  }

  if (is_join_invalid(event)) {
    if (before.phase != Phase::winner_live || before.lease != Lease::live) {
      return reject(before);
    }
    State after = before;
    after.phase = Phase::fail_stop;
    after.lease = Lease::consumed;
    after.recipient = Recipient::none;
    after.a_copy_observed = false;
    after.b_copy_observed = false;
    return accept(after, Flags{.consumed = true,
                               .validation_failed = true});
  }

  if (event == Event::drop_winner) {
    if (before.phase != Phase::winner_live || before.lease != Lease::live) {
      return reject(before);
    }
    State after = before;
    after.phase = Phase::query_only;
    after.lease = Lease::lost;
    after.a_copy_observed = false;
    after.b_copy_observed = false;
    return accept(after, Flags{.lost = true});
  }

  if (event == Event::query_provider_applied ||
      event == Event::query_provider_unknown) {
    return accept(before, Flags{.observation = true, .query = true});
  }

  if (event == Event::detached_winner_replay) {
    return accept(before, Flags{.observation = true});
  }

  if (event == Event::recover_join_attempt) return reject(before);

  if (event == Event::restart) {
    if (before.phase == Phase::winner_live ||
        before.phase == Phase::fail_stop) {
      return accept(cold_no_intent(before));
    }
    if (before.phase == Phase::query_only) {
      State after = before;
      after.restarted = true;
      return accept(after);
    }
    const dispatch::Step downstream =
        dispatch::step(before.downstream, dispatch::Event::restart);
    if (downstream.outcome != dispatch::Outcome::applied) {
      return reject(before);
    }
    State after = before;
    after.restarted = true;
    after.downstream = downstream.state;
    return accept(after, Flags{.effect = downstream.effect_emitted,
                               .pending_consumed =
                                   downstream.pending_activation_consumed,
                               .permit_consumed = downstream.permit_consumed,
                               .result_retained = downstream.result_retained,
                               .publication =
                                   downstream.publication_appended});
  }

  const std::optional<dispatch::Event> mapped = downstream_event(event);
  if (!mapped.has_value() || before.phase != Phase::dispatch_active) {
    return reject(before);
  }
  const dispatch::Step downstream = dispatch::step(before.downstream, *mapped);
  if (downstream.outcome == dispatch::Outcome::rejected) return reject(before);
  if (downstream.outcome == dispatch::Outcome::environment_impossible) {
    return impossible(before);
  }
  State after = before;
  after.downstream = downstream.state;
  return accept(after, Flags{.effect = downstream.effect_emitted,
                             .pending_consumed =
                                 downstream.pending_activation_consumed,
                             .permit_consumed = downstream.permit_consumed,
                             .result_retained = downstream.result_retained,
                             .publication =
                                 downstream.publication_appended});
}

std::string_view to_string(const Phase value) noexcept {
  switch (value) {
    case Phase::winner_live: return "winner_live";
    case Phase::query_only: return "query_only";
    case Phase::dispatch_active: return "dispatch_active";
    case Phase::fail_stop: return "fail_stop";
  }
  return "invalid_phase";
}

std::string_view to_string(const Lease value) noexcept {
  switch (value) {
    case Lease::live: return "live";
    case Lease::consumed: return "consumed";
    case Lease::lost: return "lost";
  }
  return "invalid_lease";
}

std::string_view to_string(const Recipient value) noexcept {
  switch (value) {
    case Recipient::none: return "none";
    case Recipient::a: return "a";
    case Recipient::b: return "b";
  }
  return "invalid_recipient";
}

std::string_view to_string(const Outcome value) noexcept {
  switch (value) {
    case Outcome::applied: return "applied";
    case Outcome::rejected: return "rejected";
    case Outcome::environment_impossible: return "environment_impossible";
  }
  return "invalid_outcome";
}

std::string_view to_string(const Event value) noexcept {
  switch (value) {
    case Event::copy_winner_to_a: return "copy_winner_to_a";
    case Event::copy_winner_to_b: return "copy_winner_to_b";
    case Event::join_a_exact: return "join_a_exact";
    case Event::join_b_exact: return "join_b_exact";
    case Event::join_a_subject_mismatch: return "join_a_subject_mismatch";
    case Event::join_b_subject_mismatch: return "join_b_subject_mismatch";
    case Event::join_a_route_mismatch: return "join_a_route_mismatch";
    case Event::join_b_route_mismatch: return "join_b_route_mismatch";
    case Event::join_a_malformed: return "join_a_malformed";
    case Event::join_b_malformed: return "join_b_malformed";
    case Event::drop_winner: return "drop_winner";
    case Event::query_provider_applied: return "query_provider_applied";
    case Event::query_provider_unknown: return "query_provider_unknown";
    case Event::detached_winner_replay: return "detached_winner_replay";
    case Event::restart: return "restart";
    case Event::recover_join_attempt: return "recover_join_attempt";
    case Event::dispatch_activate_exact_readback:
      return "dispatch_activate_exact_readback";
    case Event::dispatch_activate_readback_mismatch:
      return "dispatch_activate_readback_mismatch";
    case Event::dispatch_enter_exact: return "dispatch_enter_exact";
    case Event::dispatch_enter_subject_mismatch:
      return "dispatch_enter_subject_mismatch";
    case Event::dispatch_enter_malformed: return "dispatch_enter_malformed";
    case Event::dispatch_enter_route_override:
      return "dispatch_enter_route_override";
    case Event::dispatch_endpoint_effect: return "dispatch_endpoint_effect";
    case Event::dispatch_endpoint_serialized_no_effect:
      return "dispatch_endpoint_serialized_no_effect";
    case Event::dispatch_endpoint_nonreturn:
      return "dispatch_endpoint_nonreturn";
    case Event::dispatch_endpoint_malformed:
      return "dispatch_endpoint_malformed";
    case Event::dispatch_retain_result1: return "dispatch_retain_result1";
    case Event::dispatch_publish_result1: return "dispatch_publish_result1";
    case Event::dispatch_query_exact_effect:
      return "dispatch_query_exact_effect";
    case Event::dispatch_query_serialized_no_effect:
      return "dispatch_query_serialized_no_effect";
    case Event::dispatch_query_absent: return "dispatch_query_absent";
    case Event::dispatch_query_unavailable:
      return "dispatch_query_unavailable";
    case Event::dispatch_query_malformed: return "dispatch_query_malformed";
    case Event::dispatch_query_wrong_binding:
      return "dispatch_query_wrong_binding";
    case Event::dispatch_query_split_view:
      return "dispatch_query_split_view";
    case Event::dispatch_retain_result2: return "dispatch_retain_result2";
    case Event::dispatch_publish_result2: return "dispatch_publish_result2";
    case Event::dispatch_recover_mint_attempt:
      return "dispatch_recover_mint_attempt";
    case Event::dispatch_recover_submit_attempt:
      return "dispatch_recover_submit_attempt";
  }
  return "invalid_event";
}

std::string state_key(const State& state) {
  std::ostringstream out;
  out << to_string(state.phase) << '|' << to_string(state.lease) << '|'
      << to_string(state.recipient) << "|copy_a="
      << (state.a_copy_observed ? '1' : '0') << "|copy_b="
      << (state.b_copy_observed ? '1' : '0') << "|restarted="
      << (state.restarted ? '1' : '0') << "|dispatch="
      << dispatch::state_key(state.downstream);
  return out.str();
}

std::string reopen_view_key(const ReopenView& view) {
  std::ostringstream out;
  out << "intent=" << (view.intent_persisted ? '1' : '0') << "|recipient="
      << to_string(view.recipient) << "|restarted="
      << (view.restarted ? '1' : '0') << "|dispatch="
      << dispatch::reopen_view_key(view.downstream);
  return out.str();
}

std::string reopen_view_key(const State& state) {
  return reopen_view_key(reopen_view(state));
}

}  // namespace slopos::e0::winner_intent
