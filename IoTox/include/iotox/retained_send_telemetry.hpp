#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <optional>

namespace iotox::interactive {

// Separates the two retained Ratox send heads. A controller packet and a host
// packet can independently remain at the front of their bounded queues while
// toxcore reports transient SENDQ/connection pressure.
enum class RetainedSendLane : std::size_t {
    controller = 0U,
    host = 1U,
};

struct RetainedSendLaneSnapshot {
    std::uint64_t retryable_rejections{0U};
    std::uint64_t current_retry_streak{0U};
    std::uint64_t maximum_retry_streak{0U};
    std::uint64_t retry_age_us{0U};

    [[nodiscard]] bool operator==(
        const RetainedSendLaneSnapshot &) const = default;
};

struct RetainedSendSnapshot {
    RetainedSendLaneSnapshot controller{};
    RetainedSendLaneSnapshot host{};

    [[nodiscard]] bool operator==(const RetainedSendSnapshot &) const = default;
};

// Thread-safe, fixed-allocation lifetime telemetry. A retryable rejection keeps
// the head active and advances its streak. Any accepted, fatal, or explicitly
// purged head clears only the active streak; lifetime totals remain available.
class RetainedSendTelemetry {
  public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    void observe_retryable(
        RetainedSendLane lane, TimePoint now = Clock::now()) noexcept;
    void clear(RetainedSendLane lane) noexcept;
    void clear_all_active() noexcept;

    [[nodiscard]] RetainedSendSnapshot snapshot(
        TimePoint now = Clock::now()) const noexcept;

  private:
    struct LaneState {
        std::uint64_t retryable_rejections{0U};
        std::uint64_t current_retry_streak{0U};
        std::uint64_t maximum_retry_streak{0U};
        std::optional<TimePoint> retry_started_at;
    };

    [[nodiscard]] static std::size_t index(RetainedSendLane lane) noexcept;
    static void saturating_increment(std::uint64_t &value) noexcept;
    [[nodiscard]] static RetainedSendLaneSnapshot project(
        const LaneState &state, TimePoint now) noexcept;

    mutable std::mutex mutex_;
    std::array<LaneState, 2U> lanes_{};
};

}  // namespace iotox::interactive
