#include "iotox/latency_histogram.hpp"

#include <algorithm>
#include <bit>
#include <limits>

namespace iotox {
namespace {

constexpr std::uint32_t kFirstLogBitWidth = 13U;

}  // namespace

void LatencyHistogram::saturating_increment(std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) {
        ++value;
    }
}

std::uint64_t LatencyHistogram::nearest_rank(
    std::uint64_t count, std::uint32_t percentage) noexcept {
    percentage = std::clamp<std::uint32_t>(percentage, 1U, 100U);
    const std::uint64_t quotient = count / 100U;
    const std::uint64_t remainder = count % 100U;
    std::uint64_t rank = quotient * percentage;
    rank += (remainder * percentage + 99U) / 100U;
    return rank;
}

std::size_t LatencyHistogram::bucket_index(
    std::uint64_t microseconds) noexcept {
    if (microseconds <= kExactMaximumUs) {
        return static_cast<std::size_t>(microseconds);
    }
    const std::uint32_t width = static_cast<std::uint32_t>(
        std::bit_width(microseconds));
    return kExactBucketCount +
           static_cast<std::size_t>(width - kFirstLogBitWidth);
}

LatencyHistogram::Percentile LatencyHistogram::bucket_value(
    std::size_t index) noexcept {
    if (index < kExactBucketCount) {
        return Percentile{static_cast<std::uint64_t>(index), true};
    }
    const std::uint32_t width = kFirstLogBitWidth +
        static_cast<std::uint32_t>(index - kExactBucketCount);
    if (width >= std::numeric_limits<std::uint64_t>::digits) {
        return Percentile{std::numeric_limits<std::uint64_t>::max(), false};
    }
    return Percentile{(std::uint64_t{1U} << width) - 1U, false};
}

void LatencyHistogram::observe(std::uint64_t microseconds) noexcept {
    const std::size_t index = bucket_index(microseconds);
    if (buckets_[index] == 0U) {
        first_nonzero_bucket_ = std::min(first_nonzero_bucket_, index);
        last_nonzero_bucket_ = std::max(last_nonzero_bucket_, index);
    }
    saturating_increment(buckets_[index]);
    saturating_increment(count_);
    maximum_us_ = std::max(maximum_us_, microseconds);
    if (microseconds >= kInteractiveGateUs) {
        saturating_increment(at_or_above_interactive_gate_);
    }
    summary_valid_ = false;
}

LatencyHistogram::Percentile LatencyHistogram::percentile(
    std::uint32_t percentage) const noexcept {
    if (count_ == 0U) {
        return Percentile{};
    }
    percentage = std::clamp<std::uint32_t>(percentage, 1U, 100U);
    if (percentage == 50U) {
        return summary().p50;
    }
    if (percentage == 95U) {
        return summary().p95;
    }
    if (percentage == 99U) {
        return summary().p99;
    }

    std::uint64_t rank = nearest_rank(count_, percentage);
    for (std::size_t index = first_nonzero_bucket_;
         index <= last_nonzero_bucket_; ++index) {
        if (buckets_[index] >= rank) {
            return bucket_value(index);
        }
        rank -= buckets_[index];
    }
    return Percentile{std::numeric_limits<std::uint64_t>::max(), false};
}

LatencyHistogram::Summary LatencyHistogram::summary() const noexcept {
    if (summary_valid_) {
        return cached_summary_;
    }

    Summary result;
    result.count = count_;
    result.maximum_us = maximum_us_;
    result.at_or_above_interactive_gate =
        at_or_above_interactive_gate_;
    if (count_ == 0U) {
        cached_summary_ = result;
        summary_valid_ = true;
        return result;
    }

    std::array<std::uint64_t, 3U> remaining{
        nearest_rank(count_, 50U), nearest_rank(count_, 95U),
        nearest_rank(count_, 99U)};
    std::array<Percentile *, 3U> outputs{
        &result.p50, &result.p95, &result.p99};
    std::array<bool, 3U> resolved{};
    std::size_t unresolved = resolved.size();

    for (std::size_t index = first_nonzero_bucket_;
         index <= last_nonzero_bucket_ && unresolved != 0U; ++index) {
        const std::uint64_t bucket = buckets_[index];
        if (bucket == 0U) {
            continue;
        }
        for (std::size_t percentile_index = 0U;
             percentile_index < remaining.size(); ++percentile_index) {
            if (resolved[percentile_index]) {
                continue;
            }
            if (bucket >= remaining[percentile_index]) {
                *outputs[percentile_index] = bucket_value(index);
                resolved[percentile_index] = true;
                --unresolved;
            } else {
                remaining[percentile_index] -= bucket;
            }
        }
    }

    if (unresolved != 0U) {
        const Percentile fallback{
            std::numeric_limits<std::uint64_t>::max(), false};
        for (std::size_t index = 0U; index < resolved.size(); ++index) {
            if (!resolved[index]) {
                *outputs[index] = fallback;
            }
        }
    }

    cached_summary_ = result;
    summary_valid_ = true;
    return result;
}

}  // namespace iotox
