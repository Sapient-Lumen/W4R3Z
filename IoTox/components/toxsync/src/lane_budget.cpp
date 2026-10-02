#include "toxsync/lane_budget.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>

namespace toxsync {
namespace {

void apply_limit(std::size_t value,
                 LaneLimitReason reason,
                 std::size_t& current,
                 LaneLimitReason& current_reason) noexcept {
    if (value == 0U) return;
    if (current == 0U || value < current) {
        current = value;
        current_reason = reason;
    }
}

[[nodiscard]] std::uint64_t goodput_per_second(
    long double bytes_per_microsecond) noexcept {
    if (bytes_per_microsecond <= 0.0L) return 0U;
    constexpr long double scale = 1'000'000.0L;
    const long double value = bytes_per_microsecond * scale;
    if (value >= static_cast<long double>(
            std::numeric_limits<std::uint64_t>::max())) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return static_cast<std::uint64_t>(value);
}

} // namespace

LaneBudgetDecision derive_lane_budget(const LaneResourceBudget& budget) noexcept {
    LaneBudgetDecision result;
    result.memory_reserved_bytes = budget.reserved_memory_bytes;
    result.memory_per_lane_bytes = budget.bytes_per_lane;

    std::size_t lanes{};
    LaneLimitReason reason = LaneLimitReason::none;
    apply_limit(budget.requested_lanes, LaneLimitReason::requested,
                lanes, reason);
    apply_limit(budget.peer_advertised_lanes,
                LaneLimitReason::peer_advertisement, lanes, reason);
    apply_limit(budget.transport_slots, LaneLimitReason::transport_slots,
                lanes, reason);
    apply_limit(budget.global_inflight_slots,
                LaneLimitReason::global_inflight, lanes, reason);
    apply_limit(budget.descriptor_slots, LaneLimitReason::file_descriptors,
                lanes, reason);
    apply_limit(budget.command_queue_slots, LaneLimitReason::command_queue,
                lanes, reason);

    if (budget.memory_budget_bytes != 0U && budget.bytes_per_lane != 0U) {
        if (budget.reserved_memory_bytes >= budget.memory_budget_bytes) {
            result.memory_lanes = 0U;
            result.lanes = 0U;
            result.limiting_reason = LaneLimitReason::resource_unavailable;
            return result;
        }
        result.memory_lanes =
            (budget.memory_budget_bytes - budget.reserved_memory_bytes) /
            budget.bytes_per_lane;
        if (result.memory_lanes == 0U) {
            result.lanes = 0U;
            result.limiting_reason = LaneLimitReason::resource_unavailable;
            return result;
        }
        apply_limit(result.memory_lanes, LaneLimitReason::memory_budget,
                    lanes, reason);
    }

    // All-zero constraints mean there is no executable local reservation. We
    // intentionally return zero rather than pretending unlimited resources.
    if (lanes == 0U) {
        result.limiting_reason = LaneLimitReason::resource_unavailable;
        return result;
    }
    result.lanes = lanes;
    result.limiting_reason = reason;
    return result;
}

const char* lane_limit_reason_name(LaneLimitReason reason) noexcept {
    switch (reason) {
        case LaneLimitReason::none: return "none";
        case LaneLimitReason::requested: return "requested";
        case LaneLimitReason::peer_advertisement: return "peer-advertisement";
        case LaneLimitReason::transport_slots: return "transport-slots";
        case LaneLimitReason::global_inflight: return "global-inflight";
        case LaneLimitReason::file_descriptors: return "file-descriptors";
        case LaneLimitReason::command_queue: return "command-queue";
        case LaneLimitReason::memory_budget: return "memory-budget";
        case LaneLimitReason::resource_unavailable: return "resource-unavailable";
    }
    return "unknown";
}

LaneTuner::LaneTuner(std::size_t budget_lanes, LaneTuningPolicy policy)
    : policy_(policy),
      budget_lanes_(budget_lanes),
      current_lanes_(budget_lanes == 0U ? 0U : 1U),
      accepted_lanes_(budget_lanes == 0U ? 0U : 1U) {
    if (policy_.minimum_gain_percent > 100U ||
        policy_.congestion_stall_percent > 100U ||
        policy_.additive_probe_until == 0U) {
        throw std::invalid_argument("invalid lane tuning policy");
    }
}

void LaneTuner::set_budget(std::size_t budget_lanes) noexcept {
    budget_lanes_ = budget_lanes;
    if (budget_lanes_ == 0U) {
        current_lanes_ = 0U;
        accepted_lanes_ = 0U;
        accepted_goodput_per_microsecond_ = 0.0L;
        probing_enabled_ = false;
        return;
    }
    if (accepted_lanes_ == 0U) accepted_lanes_ = 1U;
    accepted_lanes_ = std::min(accepted_lanes_, budget_lanes_);
    current_lanes_ = std::clamp(current_lanes_, std::size_t{1U}, budget_lanes_);
    if (current_lanes_ < accepted_lanes_) current_lanes_ = accepted_lanes_;
    if (budget_lanes_ > accepted_lanes_) probing_enabled_ = true;
}

std::size_t LaneTuner::next_probe(std::size_t accepted) const noexcept {
    if (accepted >= budget_lanes_) return budget_lanes_;
    std::size_t step = 1U;
    if (accepted >= policy_.additive_probe_until) {
        step = std::max<std::size_t>(1U, accepted / 4U);
    }
    if (step > budget_lanes_ - accepted) return budget_lanes_;
    return accepted + step;
}

std::size_t LaneTuner::observe(const LaneObservation& observation) {
    if (budget_lanes_ == 0U) {
        throw std::logic_error("cannot observe lanes with a zero resource budget");
    }
    if (observation.lanes == 0U ||
        observation.elapsed_microseconds == 0U ||
        observation.useful_bytes == 0U) {
        throw std::invalid_argument(
            "lane observation must contain progress and elapsed time");
    }
    if (observation.lanes != current_lanes_) {
        throw std::invalid_argument(
            "lane observation does not match the active probe");
    }

    const long double stall_percent =
        static_cast<long double>(observation.stalled_microseconds) * 100.0L /
        static_cast<long double>(observation.elapsed_microseconds);
    const bool congested = observation.retries != 0U ||
        stall_percent >=
            static_cast<long double>(policy_.congestion_stall_percent);
    const long double goodput =
        static_cast<long double>(observation.useful_bytes) /
        static_cast<long double>(observation.elapsed_microseconds);

    if (congested) {
        const auto halved = std::max<std::size_t>(1U, current_lanes_ / 2U);
        accepted_lanes_ = std::min(accepted_lanes_, halved);
        current_lanes_ = std::min(halved, budget_lanes_);
        accepted_goodput_per_microsecond_ = 0.0L;
        probing_enabled_ = false;
        return current_lanes_;
    }

    if (accepted_goodput_per_microsecond_ == 0.0L) {
        accepted_lanes_ = current_lanes_;
        accepted_goodput_per_microsecond_ = goodput;
        if (probing_enabled_ && accepted_lanes_ < budget_lanes_) {
            current_lanes_ = next_probe(accepted_lanes_);
        }
        return current_lanes_;
    }

    if (current_lanes_ > accepted_lanes_) {
        const long double required = accepted_goodput_per_microsecond_ *
            (100.0L + static_cast<long double>(policy_.minimum_gain_percent)) /
            100.0L;
        if (goodput >= required) {
            accepted_lanes_ = current_lanes_;
            accepted_goodput_per_microsecond_ = goodput;
            current_lanes_ = probing_enabled_
                ? next_probe(accepted_lanes_)
                : accepted_lanes_;
        } else {
            current_lanes_ = accepted_lanes_;
            probing_enabled_ = false;
        }
        return current_lanes_;
    }

    accepted_goodput_per_microsecond_ = goodput;
    current_lanes_ = accepted_lanes_;
    return current_lanes_;
}

std::size_t LaneTuner::backoff() noexcept {
    if (budget_lanes_ == 0U) return 0U;
    const auto basis = current_lanes_ == 0U ? std::size_t{1U} : current_lanes_;
    const auto reduced = std::max<std::size_t>(1U, basis / 2U);
    accepted_lanes_ = std::min(reduced, budget_lanes_);
    current_lanes_ = accepted_lanes_;
    accepted_goodput_per_microsecond_ = 0.0L;
    probing_enabled_ = false;
    return current_lanes_;
}

LaneTuningSnapshot LaneTuner::snapshot() const noexcept {
    return LaneTuningSnapshot{
        .budget_lanes = budget_lanes_,
        .active_lanes = current_lanes_,
        .accepted_lanes = accepted_lanes_,
        .next_probe_lanes = budget_lanes_ == 0U
            ? 0U
            : next_probe(accepted_lanes_),
        .accepted_goodput_bytes_per_second = goodput_per_second(
            accepted_goodput_per_microsecond_),
        .probing_enabled = probing_enabled_,
    };
}

void LaneTuner::reset() noexcept {
    current_lanes_ = budget_lanes_ == 0U ? 0U : 1U;
    accepted_lanes_ = current_lanes_;
    accepted_goodput_per_microsecond_ = 0.0L;
    probing_enabled_ = budget_lanes_ != 0U;
}

} // namespace toxsync
