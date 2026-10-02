#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace iotox {

// A fixed-allocation lifetime histogram for monotonic microsecond durations.
// Values through 4096 us are represented exactly so the owner scheduler's
// strict p99 < 2 ms decision boundary cannot be hidden by bucket rounding.
// Larger observations use conservative power-of-two upper bounds.
class LatencyHistogram {
  public:
    struct Percentile {
        std::uint64_t upper_bound_us{0U};
        bool exact{true};

        [[nodiscard]] bool operator==(const Percentile &) const = default;
    };

    struct Summary {
        Percentile p50{};
        Percentile p95{};
        Percentile p99{};
        std::uint64_t count{0U};
        std::uint64_t maximum_us{0U};
        std::uint64_t at_or_above_interactive_gate{0U};

        [[nodiscard]] bool operator==(const Summary &) const = default;
    };

    static constexpr std::uint64_t kInteractiveGateUs = 2000U;
    static constexpr std::uint64_t kExactMaximumUs = 4096U;
    static constexpr std::size_t kExactBucketCount =
        static_cast<std::size_t>(kExactMaximumUs) + 1U;
    static constexpr std::size_t kLogBucketCount =
        std::numeric_limits<std::uint64_t>::digits - 12U;
    static constexpr std::size_t kBucketCount =
        kExactBucketCount + kLogBucketCount;

    void observe(std::uint64_t microseconds) noexcept;

    [[nodiscard]] Percentile percentile(
        std::uint32_t percentage) const noexcept;
    [[nodiscard]] Summary summary() const noexcept;
    [[nodiscard]] std::uint64_t count() const noexcept { return count_; }
    [[nodiscard]] std::uint64_t maximum_us() const noexcept {
        return maximum_us_;
    }
    [[nodiscard]] std::uint64_t at_or_above_interactive_gate() const noexcept {
        return at_or_above_interactive_gate_;
    }

    void clear() noexcept {
        buckets_.fill(0U);
        count_ = 0U;
        maximum_us_ = 0U;
        at_or_above_interactive_gate_ = 0U;
        first_nonzero_bucket_ = kBucketCount;
        last_nonzero_bucket_ = 0U;
        cached_summary_ = Summary{};
        summary_valid_ = true;
    }

  private:
    static void saturating_increment(std::uint64_t &value) noexcept;
    [[nodiscard]] static std::uint64_t nearest_rank(
        std::uint64_t count, std::uint32_t percentage) noexcept;
    [[nodiscard]] static std::size_t bucket_index(
        std::uint64_t microseconds) noexcept;
    [[nodiscard]] static Percentile bucket_value(
        std::size_t index) noexcept;

    std::array<std::uint64_t, kBucketCount> buckets_{};
    std::uint64_t count_{0U};
    std::uint64_t maximum_us_{0U};
    std::uint64_t at_or_above_interactive_gate_{0U};
    std::size_t first_nonzero_bucket_{kBucketCount};
    std::size_t last_nonzero_bucket_{0U};
    mutable Summary cached_summary_{};
    mutable bool summary_valid_{true};
};

}  // namespace iotox
