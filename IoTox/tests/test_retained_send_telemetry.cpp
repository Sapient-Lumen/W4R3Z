#include "iotox/retained_send_telemetry.hpp"
#include "test_harness.hpp"

#include <chrono>

IOTOX_TEST("retained send telemetry separates lanes and preserves lifetime pressure") {
    using Telemetry = iotox::interactive::RetainedSendTelemetry;
    using Lane = iotox::interactive::RetainedSendLane;
    using namespace std::chrono_literals;

    Telemetry telemetry;
    const auto origin = Telemetry::TimePoint{};
    IOTOX_CHECK(telemetry.snapshot(origin) ==
                iotox::interactive::RetainedSendSnapshot{});

    telemetry.observe_retryable(Lane::controller, origin + 10us);
    telemetry.observe_retryable(Lane::controller, origin + 15us);
    telemetry.observe_retryable(Lane::host, origin + 20us);

    const auto active = telemetry.snapshot(origin + 30us);
    IOTOX_CHECK(active.controller.retryable_rejections == 2U);
    IOTOX_CHECK(active.controller.current_retry_streak == 2U);
    IOTOX_CHECK(active.controller.maximum_retry_streak == 2U);
    IOTOX_CHECK(active.controller.retry_age_us == 20U);
    IOTOX_CHECK(active.host.retryable_rejections == 1U);
    IOTOX_CHECK(active.host.current_retry_streak == 1U);
    IOTOX_CHECK(active.host.maximum_retry_streak == 1U);
    IOTOX_CHECK(active.host.retry_age_us == 10U);

    telemetry.clear(Lane::controller);
    const auto cleared = telemetry.snapshot(origin + 40us);
    IOTOX_CHECK(cleared.controller.retryable_rejections == 2U);
    IOTOX_CHECK(cleared.controller.current_retry_streak == 0U);
    IOTOX_CHECK(cleared.controller.maximum_retry_streak == 2U);
    IOTOX_CHECK(cleared.controller.retry_age_us == 0U);
    IOTOX_CHECK(cleared.host.current_retry_streak == 1U);

    telemetry.clear_all_active();
    const auto idle = telemetry.snapshot(origin + 50us);
    IOTOX_CHECK(idle.host.retryable_rejections == 1U);
    IOTOX_CHECK(idle.host.current_retry_streak == 0U);
    IOTOX_CHECK(idle.host.maximum_retry_streak == 1U);
    IOTOX_CHECK(idle.host.retry_age_us == 0U);
}

IOTOX_TEST("retained send telemetry clamps regressed observation time") {
    using Telemetry = iotox::interactive::RetainedSendTelemetry;
    using Lane = iotox::interactive::RetainedSendLane;
    using namespace std::chrono_literals;

    Telemetry telemetry;
    const auto origin = Telemetry::TimePoint{};
    telemetry.observe_retryable(Lane::host, origin + 20us);
    const auto regressed = telemetry.snapshot(origin + 10us);
    IOTOX_CHECK(regressed.host.current_retry_streak == 1U);
    IOTOX_CHECK(regressed.host.retry_age_us == 0U);
}
