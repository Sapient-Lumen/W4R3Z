#pragma once

#include <cstddef>
#include <cstdint>

namespace toxsync {

// Zero-valued resource fields mean "not constrained by this layer". The
// resulting lane count is therefore governed by actual negotiated and local
// resources, not a project-wide magic maximum. A result of zero means the
// caller currently lacks enough resources to open even one lane.
struct LaneResourceBudget {
    std::size_t requested_lanes{};
    std::size_t peer_advertised_lanes{};
    std::size_t transport_slots{};
    std::size_t global_inflight_slots{};
    std::size_t descriptor_slots{};
    std::size_t command_queue_slots{};
    std::size_t memory_budget_bytes{};
    std::size_t reserved_memory_bytes{};
    std::size_t bytes_per_lane{};
};

enum class LaneLimitReason : std::uint8_t {
    none,
    requested,
    peer_advertisement,
    transport_slots,
    global_inflight,
    file_descriptors,
    command_queue,
    memory_budget,
    resource_unavailable,
};

struct LaneBudgetDecision {
    std::size_t lanes{};
    LaneLimitReason limiting_reason{LaneLimitReason::none};
    std::size_t memory_lanes{};
    std::size_t memory_reserved_bytes{};
    std::size_t memory_per_lane_bytes{};

    [[nodiscard]] bool usable() const noexcept { return lanes != 0U; }
};

[[nodiscard]] LaneBudgetDecision derive_lane_budget(
    const LaneResourceBudget& budget) noexcept;
[[nodiscard]] const char* lane_limit_reason_name(LaneLimitReason reason) noexcept;

struct LaneObservation {
    std::size_t lanes{1U};
    std::uint64_t useful_bytes{};
    std::uint64_t elapsed_microseconds{};
    std::uint64_t stalled_microseconds{};
    std::uint32_t retries{};
};

struct LaneTuningPolicy {
    std::uint8_t minimum_gain_percent{10U};
    std::uint8_t congestion_stall_percent{20U};
    // Below this accepted width probes grow one lane at a time. Above it the
    // probe step grows by 25 percent, so a large negotiated budget converges
    // without requiring thousands of measurement intervals.
    std::size_t additive_probe_until{8U};
};

struct LaneTuningSnapshot {
    std::size_t budget_lanes{};
    std::size_t active_lanes{};
    std::size_t accepted_lanes{};
    std::size_t next_probe_lanes{};
    std::uint64_t accepted_goodput_bytes_per_second{};
    bool probing_enabled{true};
};

// Stateful goodput tuner with a runtime lane budget. The budget may grow or
// shrink as peers reconnect, descriptors become available, or queue pressure
// changes. It never allocates and has no built-in lane-count ceiling.
class LaneTuner final {
public:
    explicit LaneTuner(std::size_t budget_lanes = 1U,
                       LaneTuningPolicy policy = {});

    void set_budget(std::size_t budget_lanes) noexcept;
    [[nodiscard]] std::size_t budget() const noexcept { return budget_lanes_; }
    [[nodiscard]] std::size_t current_lanes() const noexcept {
        return current_lanes_;
    }
    [[nodiscard]] std::size_t observe(const LaneObservation& observation);
    // Immediate congestion/failure response when no useful-byte observation
    // exists. Halves the active/accepted width, disables the next probe, and
    // never allocates. A later set_budget() or reset() may re-enable probing.
    [[nodiscard]] std::size_t backoff() noexcept;
    [[nodiscard]] LaneTuningSnapshot snapshot() const noexcept;
    void reset() noexcept;

private:
    [[nodiscard]] std::size_t next_probe(std::size_t accepted) const noexcept;

    LaneTuningPolicy policy_{};
    std::size_t budget_lanes_{1U};
    std::size_t current_lanes_{1U};
    std::size_t accepted_lanes_{1U};
    long double accepted_goodput_per_microsecond_{};
    bool probing_enabled_{true};
};

} // namespace toxsync
