#include "iotox/retained_send_telemetry.hpp"

#include <algorithm>
#include <limits>

namespace iotox::interactive {

std::size_t RetainedSendTelemetry::index(RetainedSendLane lane) noexcept {
    return static_cast<std::size_t>(lane);
}

void RetainedSendTelemetry::saturating_increment(
    std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) {
        ++value;
    }
}

void RetainedSendTelemetry::observe_retryable(
    RetainedSendLane lane, TimePoint now) noexcept {
    std::scoped_lock lock(mutex_);
    LaneState &state = lanes_[index(lane)];
    saturating_increment(state.retryable_rejections);
    if (state.current_retry_streak == 0U) {
        state.retry_started_at = now;
    }
    saturating_increment(state.current_retry_streak);
    state.maximum_retry_streak = std::max(
        state.maximum_retry_streak, state.current_retry_streak);
}

void RetainedSendTelemetry::clear(RetainedSendLane lane) noexcept {
    std::scoped_lock lock(mutex_);
    LaneState &state = lanes_[index(lane)];
    state.current_retry_streak = 0U;
    state.retry_started_at.reset();
}

void RetainedSendTelemetry::clear_all_active() noexcept {
    std::scoped_lock lock(mutex_);
    for (LaneState &state : lanes_) {
        state.current_retry_streak = 0U;
        state.retry_started_at.reset();
    }
}

RetainedSendLaneSnapshot RetainedSendTelemetry::project(
    const LaneState &state, TimePoint now) noexcept {
    RetainedSendLaneSnapshot result;
    result.retryable_rejections = state.retryable_rejections;
    result.current_retry_streak = state.current_retry_streak;
    result.maximum_retry_streak = state.maximum_retry_streak;
    if (state.current_retry_streak == 0U ||
        !state.retry_started_at.has_value() ||
        now <= *state.retry_started_at) {
        return result;
    }

    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
        now - *state.retry_started_at).count();
    if (elapsed <= 0) {
        return result;
    }
    result.retry_age_us = static_cast<std::uint64_t>(elapsed);
    return result;
}

RetainedSendSnapshot RetainedSendTelemetry::snapshot(TimePoint now) const noexcept {
    std::scoped_lock lock(mutex_);
    return RetainedSendSnapshot{
        project(lanes_[index(RetainedSendLane::controller)], now),
        project(lanes_[index(RetainedSendLane::host)], now)};
}

}  // namespace iotox::interactive
