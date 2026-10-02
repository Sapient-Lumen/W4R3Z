#include "iotox/latency_histogram.hpp"
#include "test_harness.hpp"

#include <cstdint>
#include <limits>

IOTOX_TEST("latency histogram reports exact nearest-rank scheduler percentiles") {
    iotox::LatencyHistogram histogram;
    IOTOX_CHECK(histogram.count() == 0U);
    IOTOX_CHECK(histogram.percentile(99U) == iotox::LatencyHistogram::Percentile{});

    for (std::uint64_t value = 1U; value <= 100U; ++value) {
        histogram.observe(value);
    }
    IOTOX_CHECK(histogram.count() == 100U);
    IOTOX_CHECK(histogram.maximum_us() == 100U);
    IOTOX_CHECK((histogram.percentile(50U) ==
                 iotox::LatencyHistogram::Percentile{50U, true}));
    IOTOX_CHECK((histogram.percentile(95U) ==
                 iotox::LatencyHistogram::Percentile{95U, true}));
    IOTOX_CHECK((histogram.percentile(99U) ==
                 iotox::LatencyHistogram::Percentile{99U, true}));
    IOTOX_CHECK(histogram.at_or_above_interactive_gate() == 0U);

    const auto summary = histogram.summary();
    IOTOX_CHECK(summary.count == 100U);
    IOTOX_CHECK(summary.maximum_us == 100U);
    IOTOX_CHECK(summary.at_or_above_interactive_gate == 0U);
    IOTOX_CHECK((summary.p50 ==
                 iotox::LatencyHistogram::Percentile{50U, true}));
    IOTOX_CHECK((summary.p95 ==
                 iotox::LatencyHistogram::Percentile{95U, true}));
    IOTOX_CHECK((summary.p99 ==
                 iotox::LatencyHistogram::Percentile{99U, true}));

    histogram.observe(101U);
    const auto advanced = histogram.summary();
    IOTOX_CHECK(advanced.count == 101U);
    IOTOX_CHECK(advanced.maximum_us == 101U);
    IOTOX_CHECK((advanced.p99 ==
                 iotox::LatencyHistogram::Percentile{100U, true}));
}

IOTOX_TEST("latency histogram preserves the exact two-millisecond gate") {
    iotox::LatencyHistogram histogram;
    histogram.observe(0U);
    histogram.observe(1999U);
    histogram.observe(2000U);
    histogram.observe(2001U);

    IOTOX_CHECK(histogram.count() == 4U);
    IOTOX_CHECK(histogram.maximum_us() == 2001U);
    IOTOX_CHECK(histogram.at_or_above_interactive_gate() == 2U);
    IOTOX_CHECK((histogram.percentile(50U) ==
                 iotox::LatencyHistogram::Percentile{1999U, true}));
    IOTOX_CHECK((histogram.percentile(75U) ==
                 iotox::LatencyHistogram::Percentile{2000U, true}));
    IOTOX_CHECK((histogram.percentile(99U) ==
                 iotox::LatencyHistogram::Percentile{2001U, true}));
}

IOTOX_TEST("latency histogram censors large values conservatively and clears") {
    iotox::LatencyHistogram histogram;
    histogram.observe(4096U);
    histogram.observe(4097U);
    histogram.observe(5000U);
    histogram.observe(std::numeric_limits<std::uint64_t>::max());

    IOTOX_CHECK((histogram.percentile(25U) ==
                 iotox::LatencyHistogram::Percentile{4096U, true}));
    IOTOX_CHECK((histogram.percentile(50U) ==
                 iotox::LatencyHistogram::Percentile{8191U, false}));
    IOTOX_CHECK((histogram.percentile(75U) ==
                 iotox::LatencyHistogram::Percentile{8191U, false}));
    IOTOX_CHECK((histogram.percentile(100U) ==
                 iotox::LatencyHistogram::Percentile{
                     std::numeric_limits<std::uint64_t>::max(), false}));

    histogram.clear();
    IOTOX_CHECK(histogram.count() == 0U);
    IOTOX_CHECK(histogram.maximum_us() == 0U);
    IOTOX_CHECK(histogram.at_or_above_interactive_gate() == 0U);
    IOTOX_CHECK(histogram.percentile(50U) ==
                iotox::LatencyHistogram::Percentile{});
}
