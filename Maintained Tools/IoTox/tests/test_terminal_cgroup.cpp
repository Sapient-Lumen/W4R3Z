#include "test_harness.hpp"

#include "iotox/terminal_cgroup.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <limits>
#include <optional>
#include <poll.h>
#include <stdexcept>
#include <string>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::terminal::CgroupAggregateLimits;
using iotox::terminal::CgroupIoDevice;
using iotox::terminal::CgroupPressureAdmissionLimits;
using iotox::terminal::CgroupResourceLimits;
using iotox::terminal::IdentityMode;
using iotox::terminal::IdentityPolicy;
using iotox::terminal::detail::CgroupEvents;
using iotox::terminal::detail::CgroupAggregateAdmission;
using iotox::terminal::detail::CgroupCpuBandwidthStat;
using iotox::terminal::detail::CgroupCpuBurstStat;
using iotox::terminal::detail::CgroupCpuStat;
using iotox::terminal::detail::CgroupIoMax;
using iotox::terminal::detail::CgroupIoStat;
using iotox::terminal::detail::CgroupIrqPressure;
using iotox::terminal::detail::CgroupLocalStat;
using iotox::terminal::detail::CgroupMemoryEvents;
using iotox::terminal::detail::CgroupMemoryReclaimStat;
using iotox::terminal::detail::CgroupMemoryStat;
using iotox::terminal::detail::CgroupMemorySwapEvents;
using iotox::terminal::detail::CgroupMemorySwapStat;
using iotox::terminal::detail::CgroupOwnerIdentity;
using iotox::terminal::detail::CgroupPidsEvents;
using iotox::terminal::detail::CgroupPressure;
using iotox::terminal::detail::CgroupPressureAdmissionObservation;
using iotox::terminal::detail::CgroupPressureMonitorDescriptorRole;
using iotox::terminal::detail::CgroupPressureTriggerClass;
using iotox::terminal::detail::CgroupRecoveryConfig;
using iotox::terminal::detail::CgroupSessionOutcome;
using iotox::terminal::detail::SessionCgroup;
using iotox::terminal::detail::SessionCgroupName;
using iotox::terminal::detail::cgroup_owner_is_live;
using iotox::terminal::detail::classify_cgroup_pressure_monitor_poll_events;
using iotox::terminal::detail::current_cgroup_owner_identity;
using iotox::terminal::detail::format_session_cgroup_name;
using iotox::terminal::detail::parse_boot_id;
using iotox::terminal::detail::parse_cgroup_events;
using iotox::terminal::detail::parse_cgroup_cpu_stat;
using iotox::terminal::detail::parse_cgroup_io_max;
using iotox::terminal::detail::parse_cgroup_io_stat;
using iotox::terminal::detail::parse_cgroup_irq_pressure;
using iotox::terminal::detail::parse_cgroup_local_stat;
using iotox::terminal::detail::parse_cgroup_memory_events;
using iotox::terminal::detail::parse_cgroup_memory_stat;
using iotox::terminal::detail::parse_cgroup_memory_swap_events;
using iotox::terminal::detail::parse_cgroup_peak;
using iotox::terminal::detail::parse_cgroup_pids_events;
using iotox::terminal::detail::parse_cgroup_pressure;
using iotox::terminal::detail::parse_cgroup_pressure_sample;
using iotox::terminal::detail::parse_session_cgroup_name;
using iotox::terminal::detail::evaluate_cgroup_pressure_admission;
using iotox::terminal::detail::encode_cgroup_pressure_trigger;

class TempDirectory {
  public:
    TempDirectory() {
        std::array<char, 64U> pattern{};
        const std::string value = "/tmp/iotox-cgroup-unit-XXXXXX";
        std::copy(value.begin(), value.end(), pattern.begin());
        char *created = ::mkdtemp(pattern.data());
        if (created == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = created;
    }

    ~TempDirectory() { std::filesystem::remove_all(path_); }

    TempDirectory(const TempDirectory &) = delete;
    TempDirectory &operator=(const TempDirectory &) = delete;

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

[[nodiscard]] std::uint32_t distinct_nonroot_uid() {
    const std::uint64_t current = static_cast<std::uint64_t>(::geteuid());
    if (current != 65534U) return 65534U;
    return 65533U;
}

[[nodiscard]] IdentityPolicy exact_distinct_identity() {
    IdentityPolicy identity;
    identity.mode = IdentityMode::exact;
    identity.uid = distinct_nonroot_uid();
    identity.gid = identity.uid;
    identity.clear_supplementary_groups = true;
    return identity;
}

IOTOX_TEST("cgroup events parser accepts the canonical recursive state") {
    auto parsed = parse_cgroup_events("populated 1\nfrozen 0\n");
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK(parsed.value() ==
                (CgroupEvents{true, std::optional<bool>{false}}));
}

IOTOX_TEST("cgroup events parser remains strict but future-field compatible") {
    auto parsed = parse_cgroup_events(
        "future_counter 17\nfrozen 1\npopulated 0\n");
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK(!parsed.value().populated);
    IOTOX_CHECK(parsed.value().frozen == std::optional<bool>{true});
}

IOTOX_TEST("cgroup events parser requires one populated field") {
    auto missing = parse_cgroup_events("frozen 0\n");
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.status().code() == ErrorCode::protocol_error);

    auto duplicate = parse_cgroup_events("populated 0\npopulated 1\n");
    IOTOX_CHECK(!duplicate.ok());
    IOTOX_CHECK(duplicate.status().code() == ErrorCode::protocol_error);
}

IOTOX_TEST("cgroup events parser rejects nonboolean kernel state") {
    auto populated = parse_cgroup_events("populated 2\n");
    IOTOX_CHECK(!populated.ok());
    IOTOX_CHECK(populated.status().code() == ErrorCode::protocol_error);

    auto frozen = parse_cgroup_events("populated 0\nfrozen 7\n");
    IOTOX_CHECK(!frozen.ok());
    IOTOX_CHECK(frozen.status().code() == ErrorCode::protocol_error);
}

IOTOX_TEST("cgroup events parser rejects ambiguous record grammar") {
    for (const std::string &record : {
             std::string{},
             std::string{"populated 0"},
             std::string{"populated  0\n"},
             std::string{"Populated 0\n"},
             std::string{"populated +0\n"},
             std::string{"populated 00\n"},
             std::string{"populated 0\n\n"}}) {
        auto parsed = parse_cgroup_events(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup outcome parsers accept keyed counters and future fields") {
    auto pids = parse_cgroup_pids_events("future 9\nmax 3\n");
    IOTOX_CHECK(pids.ok());
    IOTOX_CHECK(pids.value() == CgroupPidsEvents{3U});

    auto memory = parse_cgroup_memory_events(
        "low 1\nhigh 2\nmax 3\noom 4\noom_kill 5\n"
        "oom_group_kill 6\nfuture_counter 7\n");
    IOTOX_CHECK(memory.ok());
    IOTOX_CHECK((
        memory.value() == CgroupMemoryEvents{2U, 3U, 4U, 5U, 6U}));

    auto older_memory = parse_cgroup_memory_events(
        "low 1\nhigh 2\nmax 3\noom 4\noom_kill 5\n");
    IOTOX_CHECK(older_memory.ok());
    IOTOX_CHECK((
        older_memory.value() == CgroupMemoryEvents{2U, 3U, 4U, 5U, 0U}));

    auto cpu = parse_cgroup_cpu_stat(
        "usage_usec 11\nuser_usec 5\nsystem_usec 6\nnr_periods 7\n"
        "nr_throttled 3\nthrottled_usec 13\nnr_bursts 1\n"
        "burst_usec 17\nfuture_counter 19\n");
    IOTOX_CHECK(cpu.ok());
    IOTOX_CHECK((cpu.value() == CgroupCpuStat{
        11U,
        5U,
        6U,
        CgroupCpuBandwidthStat{
            7U, 3U, 13U, CgroupCpuBurstStat{1U, 17U}}}));

    auto controller_disabled = parse_cgroup_cpu_stat(
        "usage_usec 23\nuser_usec 17\nsystem_usec 6\n");
    IOTOX_CHECK(controller_disabled.ok());
    IOTOX_CHECK((controller_disabled.value() ==
                 CgroupCpuStat{23U, 17U, 6U, std::nullopt}));

    auto older_bandwidth = parse_cgroup_cpu_stat(
        "usage_usec 29\nuser_usec 19\nsystem_usec 10\n"
        "nr_periods 5\nnr_throttled 2\nthrottled_usec 7\n");
    IOTOX_CHECK(older_bandwidth.ok());
    IOTOX_CHECK((older_bandwidth.value() == CgroupCpuStat{
        29U,
        19U,
        10U,
        CgroupCpuBandwidthStat{5U, 2U, 7U, std::nullopt}}));
}

IOTOX_TEST("cgroup outcome parsers reject missing duplicate and ambiguous fields") {
    for (const std::string &record : {
             std::string{"future 1\n"},
             std::string{"max 1\nmax 2\n"},
             std::string{"max +1\n"},
             std::string{"max 01\n"},
             std::string{"max 1"}}) {
        auto parsed = parse_cgroup_pids_events(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }

    auto missing_memory = parse_cgroup_memory_events(
        "high 1\nmax 2\noom 3\n");
    IOTOX_CHECK(!missing_memory.ok());
    for (const std::string &record : {
             std::string{"usage_usec 1\nuser_usec 1\n"},
             std::string{
                 "usage_usec 1\nuser_usec 1\nsystem_usec 0\n"
                 "nr_periods 2\nnr_throttled 3\n"},
             std::string{
                 "usage_usec 1\nuser_usec 1\nsystem_usec 0\n"
                 "nr_periods 2\nnr_throttled 3\nthrottled_usec 4\n"
                 "nr_bursts 5\n"},
             std::string{
                 "usage_usec 1\nuser_usec 1\nsystem_usec 0\n"
                 "nr_bursts 5\nburst_usec 6\n"}}) {
        auto parsed = parse_cgroup_cpu_stat(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup memory work parsers retain complete capability tuples") {
    auto complete = parse_cgroup_memory_stat(
        "anon 4096\npgmajfault 3\npgscan 5\nfuture 17\n"
        "pswpout 11\npgfault 2\npgsteal 7\npswpin 13\n");
    IOTOX_CHECK(complete.ok());
    IOTOX_CHECK((complete.value() == CgroupMemoryStat{
        2U,
        3U,
        CgroupMemoryReclaimStat{5U, 7U},
        CgroupMemorySwapStat{13U, 11U}}));

    auto older = parse_cgroup_memory_stat(
        "pgfault 19\npgmajfault 23\nfuture_counter 29\n");
    IOTOX_CHECK(older.ok());
    IOTOX_CHECK((older.value() ==
                 CgroupMemoryStat{19U, 23U, std::nullopt, std::nullopt}));

    auto swap_events = parse_cgroup_memory_swap_events(
        "fail 31\nfuture 37\nhigh 41\nmax 43\n");
    IOTOX_CHECK(swap_events.ok());
    IOTOX_CHECK((swap_events.value() ==
                 CgroupMemorySwapEvents{41U, 43U, 31U}));

    auto local = parse_cgroup_local_stat(
        "future 47\nfrozen_usec 53\n");
    IOTOX_CHECK(local.ok());
    IOTOX_CHECK(local.value() == CgroupLocalStat{53U});
}

IOTOX_TEST("cgroup memory work parsers reject partial or ambiguous evidence") {
    for (const std::string &record : {
             std::string{"pgfault 1\n"},
             std::string{"pgfault 1\npgmajfault 2\npgscan 3\n"},
             std::string{"pgfault 1\npgmajfault 2\npswpout 3\n"},
             std::string{"pgfault 1\npgfault 2\npgmajfault 3\n"}}) {
        auto parsed = parse_cgroup_memory_stat(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
    for (const std::string &record : {
             std::string{"high 1\nmax 2\n"},
             std::string{"high 1\nmax 2\nfail 3\nfail 4\n"},
             std::string{"high 1\nmax 2\nfail +3\n"}}) {
        auto parsed = parse_cgroup_memory_swap_events(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
    for (const std::string &record : {
             std::string{"future 1\n"},
             std::string{"frozen_usec 1\nfrozen_usec 2\n"},
             std::string{"frozen_usec 01\n"}}) {
        auto parsed = parse_cgroup_local_stat(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup peak parser accepts one canonical saturated counter") {
    auto zero = parse_cgroup_peak("0\n");
    IOTOX_CHECK(zero.ok());
    IOTOX_CHECK(zero.value() == 0U);

    auto maximum = parse_cgroup_peak("18446744073709551615\n");
    IOTOX_CHECK(maximum.ok());
    IOTOX_CHECK(maximum.value() == std::numeric_limits<std::uint64_t>::max());
}

IOTOX_TEST("cgroup peak parser rejects ambiguous or unbounded records") {
    for (const std::string &record : {
             std::string{},
             std::string{"0"},
             std::string{"00\n"},
             std::string{"+1\n"},
             std::string{"-1\n"},
             std::string{"1 \n"},
             std::string{"1\n2\n"},
             std::string{"18446744073709551616\n"},
             std::string(64U, '9') + "\n"}) {
        auto parsed = parse_cgroup_peak(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup pressure parser retains absolute some and optional full totals") {
    auto parsed = parse_cgroup_pressure(
        "full total=73 avg300=0.03 avg10=100.00 future=17 avg60=2.50\n"
        "some avg60=0.20 avg10=0.10 total=59 avg300=0.30\n");
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK((parsed.value() ==
                 CgroupPressure{59U, std::optional<std::uint64_t>{73U}}));

    auto older_cpu = parse_cgroup_pressure(
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=11\n");
    IOTOX_CHECK(older_cpu.ok());
    IOTOX_CHECK((older_cpu.value() == CgroupPressure{11U, std::nullopt}));

    auto future_class = parse_cgroup_pressure(
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1\n"
        "burst window=1.25 total=9\n");
    IOTOX_CHECK(future_class.ok());
    IOTOX_CHECK((future_class.value() == CgroupPressure{1U, std::nullopt}));
}

IOTOX_TEST("cgroup pressure sample parser retains exact canonical averages") {
    auto parsed = parse_cgroup_pressure_sample(
        "some avg10=12.34 avg60=0.01 avg300=99.99 total=59\n"
        "full avg10=100.00 avg60=2.50 avg300=0.00 total=73\n");
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK(parsed.value().some.has_value());
    IOTOX_CHECK(parsed.value().full.has_value());
    IOTOX_CHECK(parsed.value().some->average_10_basis_points == 1234U);
    IOTOX_CHECK(parsed.value().some->average_60_basis_points == 1U);
    IOTOX_CHECK(parsed.value().some->average_300_basis_points == 9999U);
    IOTOX_CHECK(parsed.value().some->total_microseconds == 59U);
    IOTOX_CHECK(parsed.value().full->average_10_basis_points == 10000U);
    IOTOX_CHECK(parsed.value().full->average_60_basis_points == 250U);
    IOTOX_CHECK(parsed.value().full->average_300_basis_points == 0U);
    IOTOX_CHECK(parsed.value().full->total_microseconds == 73U);
}

IOTOX_TEST("cgroup pressure trigger encoder freezes the portable kernel ABI") {
    auto some = encode_cgroup_pressure_trigger(
        CgroupPressureTriggerClass::some, 250000U, 2000000U);
    IOTOX_CHECK(some.ok());
    std::string expected_some{"some 250000 2000000"};
    expected_some.push_back('\0');
    IOTOX_CHECK(some.value() == expected_some);
    IOTOX_CHECK(some.value().back() == '\0');
    IOTOX_CHECK(some.value().find('\n') == std::string::npos);

    auto full = encode_cgroup_pressure_trigger(
        CgroupPressureTriggerClass::full, 10000000U, 10000000U);
    IOTOX_CHECK(full.ok());
    std::string expected_full{"full 10000000 10000000"};
    expected_full.push_back('\0');
    IOTOX_CHECK(full.value() == expected_full);

    for (auto invalid : {
             encode_cgroup_pressure_trigger(
                 static_cast<CgroupPressureTriggerClass>(0U),
                 1U, 2000000U),
             encode_cgroup_pressure_trigger(
                 CgroupPressureTriggerClass::some, 1U, 1999999U),
             encode_cgroup_pressure_trigger(
                 CgroupPressureTriggerClass::some, 1U, 2500000U),
             encode_cgroup_pressure_trigger(
                 CgroupPressureTriggerClass::some, 1U, 10000001U),
             encode_cgroup_pressure_trigger(
                 CgroupPressureTriggerClass::some, 0U, 2000000U),
             encode_cgroup_pressure_trigger(
                 CgroupPressureTriggerClass::some, 2000001U, 2000000U),
         }) {
        IOTOX_CHECK(!invalid.ok());
        IOTOX_CHECK(invalid.status().code() == ErrorCode::invalid_argument);
    }
}

IOTOX_TEST("cgroup pressure monitor classifies poll readiness fail closed") {
    const auto quiet_stop = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::stop, 0U);
    IOTOX_CHECK(!quiet_stop.stop_requested);
    IOTOX_CHECK(!quiet_stop.trigger_observed);
    IOTOX_CHECK(quiet_stop.failure_code == ErrorCode::ok);

    const auto stop = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::stop,
        static_cast<std::uint16_t>(POLLIN));
    IOTOX_CHECK(stop.stop_requested);
    IOTOX_CHECK(!stop.trigger_observed);
    IOTOX_CHECK(stop.failure_code == ErrorCode::ok);

    const auto quiet_trigger = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::trigger, 0U);
    IOTOX_CHECK(!quiet_trigger.stop_requested);
    IOTOX_CHECK(!quiet_trigger.trigger_observed);
    IOTOX_CHECK(quiet_trigger.failure_code == ErrorCode::ok);

    const auto trigger = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::trigger,
        static_cast<std::uint16_t>(POLLPRI));
    IOTOX_CHECK(!trigger.stop_requested);
    IOTOX_CHECK(trigger.trigger_observed);
    IOTOX_CHECK(trigger.failure_code == ErrorCode::ok);

    const auto vanished_after_trigger =
        classify_cgroup_pressure_monitor_poll_events(
            CgroupPressureMonitorDescriptorRole::trigger,
            static_cast<std::uint16_t>(POLLPRI | POLLERR));
    IOTOX_CHECK(vanished_after_trigger.trigger_observed);
    IOTOX_CHECK(
        vanished_after_trigger.failure_code == ErrorCode::unavailable);

    for (const short terminal : std::array{
             static_cast<short>(POLLERR),
             static_cast<short>(POLLHUP),
             static_cast<short>(POLLNVAL)}) {
        const auto dead_trigger = classify_cgroup_pressure_monitor_poll_events(
            CgroupPressureMonitorDescriptorRole::trigger,
            static_cast<std::uint16_t>(terminal));
        IOTOX_CHECK(!dead_trigger.trigger_observed);
        IOTOX_CHECK(dead_trigger.failure_code == ErrorCode::unavailable);
    }

    const auto broken_stop = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::stop,
        static_cast<std::uint16_t>(POLLIN | POLLHUP));
    IOTOX_CHECK(!broken_stop.stop_requested);
    IOTOX_CHECK(broken_stop.failure_code == ErrorCode::io_error);

    const auto unknown = classify_cgroup_pressure_monitor_poll_events(
        CgroupPressureMonitorDescriptorRole::trigger,
        static_cast<std::uint16_t>(POLLOUT));
    IOTOX_CHECK(!unknown.trigger_observed);
    IOTOX_CHECK(unknown.failure_code == ErrorCode::protocol_error);

    const auto invalid_role = classify_cgroup_pressure_monitor_poll_events(
        static_cast<CgroupPressureMonitorDescriptorRole>(0U), 0U);
    IOTOX_CHECK(invalid_role.failure_code == ErrorCode::protocol_error);
}

IOTOX_TEST("cgroup pressure admission applies exact latched hysteresis") {
    CgroupPressureAdmissionLimits limits;
    limits.maximum_cpu_some_average_10_basis_points = 100U;
    limits.maximum_memory_full_average_10_basis_points = 200U;
    limits.maximum_io_full_average_10_basis_points = 300U;
    limits.hysteresis_basis_points = 25U;

    CgroupPressureAdmissionObservation observation;
    observation.cpu_some_average_10_basis_points = 100U;
    observation.memory_full_average_10_basis_points = 200U;
    observation.io_full_average_10_basis_points = 300U;
    auto boundary = evaluate_cgroup_pressure_admission(
        limits, observation, false);
    IOTOX_CHECK(boundary.ok());
    IOTOX_CHECK(boundary.value().admitted);
    IOTOX_CHECK(!boundary.value().closed);

    observation.cpu_some_average_10_basis_points = 101U;
    auto closed = evaluate_cgroup_pressure_admission(
        limits, observation, false);
    IOTOX_CHECK(closed.ok());
    IOTOX_CHECK(!closed.value().admitted);
    IOTOX_CHECK(closed.value().closed);
    IOTOX_CHECK(closed.value().closed_transition);
    IOTOX_CHECK(!closed.value().reopened_transition);

    observation.cpu_some_average_10_basis_points = 75U;
    observation.memory_full_average_10_basis_points = 176U;
    observation.io_full_average_10_basis_points = 275U;
    auto latched = evaluate_cgroup_pressure_admission(
        limits, observation, true);
    IOTOX_CHECK(latched.ok());
    IOTOX_CHECK(!latched.value().admitted);
    IOTOX_CHECK(latched.value().closed);
    IOTOX_CHECK(!latched.value().closed_transition);
    IOTOX_CHECK(!latched.value().reopened_transition);

    observation.memory_full_average_10_basis_points = 175U;
    auto reopened = evaluate_cgroup_pressure_admission(
        limits, observation, true);
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value().admitted);
    IOTOX_CHECK(!reopened.value().closed);
    IOTOX_CHECK(reopened.value().reopened_transition);

    observation.memory_full_average_10_basis_points.reset();
    auto missing = evaluate_cgroup_pressure_admission(
        limits, observation, false);
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.status().code() == ErrorCode::protocol_error);
}

IOTOX_TEST("cgroup pressure trigger hold closes and gates hysteresis recovery") {
    CgroupPressureAdmissionLimits limits;
    limits.maximum_cpu_some_average_10_basis_points = 500U;
    limits.hysteresis_basis_points = 100U;
    limits.trigger_window_microseconds = 2000000U;
    limits.cpu_some_trigger_stall_microseconds = 250000U;

    CgroupPressureAdmissionObservation observation;
    observation.cpu_some_average_10_basis_points = 0U;

    auto tripped = evaluate_cgroup_pressure_admission(
        limits, observation, false, true);
    IOTOX_CHECK(tripped.ok());
    IOTOX_CHECK(!tripped.value().admitted);
    IOTOX_CHECK(tripped.value().closed);
    IOTOX_CHECK(tripped.value().closed_transition);
    IOTOX_CHECK(!tripped.value().reopened_transition);

    auto held = evaluate_cgroup_pressure_admission(
        limits, observation, true, true);
    IOTOX_CHECK(held.ok());
    IOTOX_CHECK(!held.value().admitted);
    IOTOX_CHECK(held.value().closed);
    IOTOX_CHECK(!held.value().closed_transition);
    IOTOX_CHECK(!held.value().reopened_transition);

    observation.cpu_some_average_10_basis_points = 401U;
    auto still_latched = evaluate_cgroup_pressure_admission(
        limits, observation, true, false);
    IOTOX_CHECK(still_latched.ok());
    IOTOX_CHECK(!still_latched.value().admitted);
    IOTOX_CHECK(still_latched.value().closed);

    observation.cpu_some_average_10_basis_points = 400U;
    auto recovered = evaluate_cgroup_pressure_admission(
        limits, observation, true, false);
    IOTOX_CHECK(recovered.ok());
    IOTOX_CHECK(recovered.value().admitted);
    IOTOX_CHECK(!recovered.value().closed);
    IOTOX_CHECK(recovered.value().reopened_transition);
}

IOTOX_TEST("cgroup pressure admission preserves exact zero and full-range boundaries") {
    CgroupPressureAdmissionObservation observation;
    auto disabled = evaluate_cgroup_pressure_admission(
        CgroupPressureAdmissionLimits{}, observation, true);
    IOTOX_CHECK(disabled.ok());
    IOTOX_CHECK(disabled.value().admitted);
    IOTOX_CHECK(!disabled.value().closed);
    IOTOX_CHECK(!disabled.value().closed_transition);
    IOTOX_CHECK(!disabled.value().reopened_transition);

    CgroupPressureAdmissionLimits zero;
    zero.maximum_cpu_some_average_10_basis_points = 0U;
    observation.cpu_some_average_10_basis_points = 0U;
    auto zero_boundary = evaluate_cgroup_pressure_admission(
        zero, observation, false);
    IOTOX_CHECK(zero_boundary.ok());
    IOTOX_CHECK(zero_boundary.value().admitted);

    observation.cpu_some_average_10_basis_points = 1U;
    auto zero_closed = evaluate_cgroup_pressure_admission(
        zero, observation, false);
    IOTOX_CHECK(zero_closed.ok());
    IOTOX_CHECK(!zero_closed.value().admitted);
    IOTOX_CHECK(zero_closed.value().closed_transition);

    observation.cpu_some_average_10_basis_points = 0U;
    auto zero_reopened = evaluate_cgroup_pressure_admission(
        zero, observation, true);
    IOTOX_CHECK(zero_reopened.ok());
    IOTOX_CHECK(zero_reopened.value().admitted);
    IOTOX_CHECK(zero_reopened.value().reopened_transition);

    CgroupPressureAdmissionLimits full_range;
    full_range.maximum_cpu_some_average_10_basis_points = 10000U;
    full_range.hysteresis_basis_points = 10000U;
    observation.cpu_some_average_10_basis_points = 1U;
    auto full_range_latched = evaluate_cgroup_pressure_admission(
        full_range, observation, true);
    IOTOX_CHECK(full_range_latched.ok());
    IOTOX_CHECK(full_range_latched.value().closed);
    observation.cpu_some_average_10_basis_points = 0U;
    auto full_range_reopened = evaluate_cgroup_pressure_admission(
        full_range, observation, true);
    IOTOX_CHECK(full_range_reopened.ok());
    IOTOX_CHECK(full_range_reopened.value().reopened_transition);
}

IOTOX_TEST("cgroup pressure admission rejects invalid limits before sampling") {
    CgroupPressureAdmissionObservation observation;
    observation.cpu_some_average_10_basis_points = 0U;

    CgroupPressureAdmissionLimits detached_hysteresis;
    detached_hysteresis.hysteresis_basis_points = 1U;
    auto detached = evaluate_cgroup_pressure_admission(
        detached_hysteresis, observation, false);
    IOTOX_CHECK(!detached.ok());
    IOTOX_CHECK(detached.status().code() == ErrorCode::invalid_argument);

    CgroupPressureAdmissionLimits wider_than_threshold;
    wider_than_threshold.maximum_cpu_some_average_10_basis_points = 10U;
    wider_than_threshold.hysteresis_basis_points = 11U;
    auto wider = evaluate_cgroup_pressure_admission(
        wider_than_threshold, observation, true);
    IOTOX_CHECK(!wider.ok());
    IOTOX_CHECK(wider.status().code() == ErrorCode::invalid_argument);
}

IOTOX_TEST("cgroup pressure parser rejects ambiguous or incomplete evidence") {
    const std::vector<std::string> invalid{
        "",
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1",
        "full avg10=0.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=0.00 avg60=0.00 total=1\n",
        "some avg10=0.00 avg60=0.00 avg300=0.00\n",
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1\n"
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=2\n",
        "some avg10=0.00 avg10=0.01 avg60=0.00 avg300=0.00 total=1\n",
        "some  avg10=0.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=0.0 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=0.000 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=0. avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=+0.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=-0.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=100.01 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=101.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=00.00 avg60=0.00 avg300=0.00 total=1\n",
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=01\n",
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1 future=nan\n",
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1\n\n"};
    for (const std::string &record : invalid) {
        auto parsed = parse_cgroup_pressure(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup IRQ pressure parser requires full stall evidence") {
    auto full_only = parse_cgroup_irq_pressure(
        "full avg60=0.20 total=59 avg300=0.30 avg10=0.10\n");
    IOTOX_CHECK(full_only.ok());
    IOTOX_CHECK(full_only.value() == CgroupIrqPressure{59U});

    auto future_some = parse_cgroup_irq_pressure(
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1\n"
        "full avg10=0.00 avg60=0.00 avg300=0.00 total=2\n"
        "future window=1.25 total=3\n");
    IOTOX_CHECK(future_some.ok());
    IOTOX_CHECK(future_some.value() == CgroupIrqPressure{2U});

    for (const std::string &record : {
             std::string{
                 "some avg10=0.00 avg60=0.00 avg300=0.00 total=1\n"},
             std::string{
                 "full avg10=0.00 avg60=0.00 total=1\n"},
             std::string{
                 "full avg10=0.00 avg60=0.00 avg300=0.00 total=1\n"
                 "full avg10=0.00 avg60=0.00 avg300=0.00 total=2\n"}}) {
        auto parsed = parse_cgroup_irq_pressure(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup io.max parser normalizes unordered nested keys and devices") {
    auto parsed = parse_cgroup_io_max(
        "259:1 wiops=max future=0 rbps=4096 riops=25 wbps=max\n"
        "8:16 wbps=8192 riops=max rbps=max wiops=7 extension=max\n");
    IOTOX_CHECK(parsed.ok());
    const std::vector<CgroupIoMax> expected{
        CgroupIoMax{
            CgroupIoDevice{8U, 16U},
            std::nullopt,
            std::optional<std::uint64_t>{8192U},
            std::nullopt,
            std::optional<std::uint64_t>{7U}},
        CgroupIoMax{
            CgroupIoDevice{259U, 1U},
            std::optional<std::uint64_t>{4096U},
            std::nullopt,
            std::optional<std::uint64_t>{25U},
            std::nullopt}};
    IOTOX_CHECK(parsed.value() == expected);
}

IOTOX_TEST("cgroup io.max parser rejects ambiguous and incomplete policy") {
    const std::vector<std::string> invalid{
        "",
        "8:16 rbps=1 wbps=2 riops=3 wiops=4",
        "\n",
        "0:0 rbps=1 wbps=2 riops=3 wiops=4\n",
        "08:16 rbps=1 wbps=2 riops=3 wiops=4\n",
        "4294967296:16 rbps=1 wbps=2 riops=3 wiops=4\n",
        "8:16 rbps=1 wbps=2 riops=3 wiops=4\n"
        "8:16 rbps=5 wbps=6 riops=7 wiops=8\n",
        "8:16 rbps=1 rbps=2 wbps=3 riops=4 wiops=5\n",
        "8:16 rbps=1 wbps=2 riops=3\n",
        "8:16 rbps=0 wbps=2 riops=3 wiops=4\n",
        "8:16 rbps=+1 wbps=2 riops=3 wiops=4\n",
        "8:16 rbps=01 wbps=2 riops=3 wiops=4\n",
        "8:16  rbps=1 wbps=2 riops=3 wiops=4\n",
        "8:16 rbps=1 wbps=2 riops=3 wiops=4 \n",
        "8:16 rbps=1 wbps=2 riops=3 wiops=4\n\n"};
    for (const std::string &record : invalid) {
        auto parsed = parse_cgroup_io_max(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("cgroup io.stat parser totals unordered devices and saturates") {
    auto empty = parse_cgroup_io_stat("");
    IOTOX_CHECK(empty.ok());
    IOTOX_CHECK(empty.value() == CgroupIoStat{});

    auto zero_device = parse_cgroup_io_stat("8:16\n259:1 \n");
    IOTOX_CHECK(zero_device.ok());
    IOTOX_CHECK(zero_device.value() == CgroupIoStat{});

    auto parsed = parse_cgroup_io_stat(
        "7:0\n"
        "8:16 wios=4 rbytes=10 future=0 wbytes=20 rios=3 dios=2 dbytes=7\n"
        "259:1 wbytes=5 rbytes=2 rios=1 wios=2\n");
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK((parsed.value() == CgroupIoStat{12U, 25U, 4U, 6U, 7U, 2U}));

    auto saturated = parse_cgroup_io_stat(
        "8:16 rbytes=18446744073709551612 wbytes=18446744073709551615 "
        "rios=18446744073709551614 wios=1 "
        "dbytes=18446744073709551615 dios=18446744073709551613\n"
        "259:1 rbytes=4 wbytes=1 rios=2 wios=18446744073709551615 "
        "dbytes=1 dios=3\n");
    IOTOX_CHECK(saturated.ok());
    const std::uint64_t maximum = std::numeric_limits<std::uint64_t>::max();
    IOTOX_CHECK((saturated.value() ==
                 CgroupIoStat{maximum, maximum, maximum,
                              maximum, maximum, maximum}));
}

IOTOX_TEST("cgroup io.stat parser rejects aliased or partial kernel evidence") {
    const std::vector<std::string> invalid{
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4",
        "\n",
        "8:16 rbytes=1 wbytes=2 rios=3\n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4\n"
        "8:16 rbytes=5 wbytes=6 rios=7 wios=8\n",
        "8:16 rbytes=1 rbytes=2 wbytes=3 rios=4 wios=5\n",
        "0:0 rbytes=1 wbytes=2 rios=3 wios=4\n",
        "08:16 rbytes=1 wbytes=2 rios=3 wios=4\n",
        "8:16 rbytes=01 wbytes=2 rios=3 wios=4\n",
        "8:16 rbytes=+1 wbytes=2 rios=3 wios=4\n",
        "8:16  rbytes=1 wbytes=2 rios=3 wios=4\n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4 \n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4 future=max\n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4 dbytes=5\n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4 dios=6\n",
        "8:16 rbytes=18446744073709551616 wbytes=2 rios=3 wios=4\n",
        "8:16 rbytes=1 wbytes=2 rios=3 wios=4\n\n"};
    for (const std::string &record : invalid) {
        auto parsed = parse_cgroup_io_stat(record);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("boot identity parser accepts only the kernel canonical form") {
    auto parsed = parse_boot_id(
        "00112233-4455-6677-8899-aabbccddeeff\n");
    IOTOX_CHECK(parsed.ok());
    const std::array<std::uint8_t, 16U> expected{
        0x00U, 0x11U, 0x22U, 0x33U, 0x44U, 0x55U, 0x66U, 0x77U,
        0x88U, 0x99U, 0xaaU, 0xbbU, 0xccU, 0xddU, 0xeeU, 0xffU};
    IOTOX_CHECK(parsed.value() == expected);

    auto without_newline = parse_boot_id(
        "00112233-4455-6677-8899-aabbccddeeff");
    IOTOX_CHECK(without_newline.ok());

    for (const std::string &record : {
             std::string{"001122334455-6677-8899-aabbccddeeff\n"},
             std::string{"00112233-4455-6677-8899-Aabbccddeeff\n"},
             std::string{"00112233-4455-6677-8899-aabbccddeefg\n"},
             std::string{"00112233-4455-6677-8899-aabbccddeeff\n\n"}}) {
        auto rejected = parse_boot_id(record);
        IOTOX_CHECK(!rejected.ok());
        IOTOX_CHECK(rejected.status().code() == ErrorCode::protocol_error);
    }
}

IOTOX_TEST("session cgroup names round trip exact daemon incarnations") {
    SessionCgroupName identity;
    identity.owner.boot_id = {
        0x00U, 0x11U, 0x22U, 0x33U, 0x44U, 0x55U, 0x66U, 0x77U,
        0x88U, 0x99U, 0xaaU, 0xbbU, 0xccU, 0xddU, 0xeeU, 0xffU};
    identity.owner.process_id = 1234U;
    identity.owner.start_time_ticks = 987654321U;
    identity.sequence = 17U;

    auto formatted = format_session_cgroup_name(identity);
    IOTOX_CHECK(formatted.ok());
    IOTOX_CHECK(
        formatted.value() ==
        "_iotox_session_v2_00112233445566778899aabbccddeeff_1234_987654321_17");
    auto parsed = parse_session_cgroup_name(formatted.value());
    IOTOX_CHECK(parsed.ok());
    IOTOX_CHECK(parsed.value() == identity);
}

IOTOX_TEST("session cgroup names reject aliasing and malformed ownership") {
    for (const std::string &name : {
             std::string{"_iotox_session_1234_1"},
             std::string{"_iotox_session_v2_00112233445566778899aabbccddeeff_01234_7_1"},
             std::string{"_iotox_session_v2_00112233445566778899aabbccddeeff_1234_0_1"},
             std::string{"_iotox_session_v2_00112233445566778899aabbccddeeff_1234_7_1_extra"},
             std::string{"_iotox_session_v2_00112233445566778899Aabbccddeeff_1234_7_1"}}) {
        auto parsed = parse_session_cgroup_name(name);
        IOTOX_CHECK(!parsed.ok());
        IOTOX_CHECK(parsed.status().code() == ErrorCode::invalid_argument);
    }

    SessionCgroupName invalid;
    invalid.owner.process_id = 1U;
    invalid.owner.start_time_ticks = 1U;
    auto rejected = format_session_cgroup_name(invalid);
    IOTOX_CHECK(!rejected.ok());
}

IOTOX_TEST("current daemon incarnation is live and mutations are stale") {
    auto current = current_cgroup_owner_identity();
    IOTOX_CHECK(current.ok());
    IOTOX_CHECK(current.value().process_id ==
                static_cast<std::uint64_t>(::getpid()));
    IOTOX_CHECK(current.value().start_time_ticks > 0U);

    auto live = cgroup_owner_is_live(current.value());
    IOTOX_CHECK(live.ok());
    IOTOX_CHECK(live.value());

    CgroupOwnerIdentity wrong_boot = current.value();
    wrong_boot.boot_id[0U] ^= 0x01U;
    auto boot_stale = cgroup_owner_is_live(wrong_boot);
    IOTOX_CHECK(boot_stale.ok());
    IOTOX_CHECK(!boot_stale.value());

    CgroupOwnerIdentity wrong_start = current.value();
    ++wrong_start.start_time_ticks;
    auto start_stale = cgroup_owner_is_live(wrong_start);
    IOTOX_CHECK(start_stale.ok());
    IOTOX_CHECK(!start_stale.value());
}

IOTOX_TEST("pidfd-backed owner validation treats a zombie as stale") {
    std::array<int, 2U> pipe_descriptors{-1, -1};
    IOTOX_CHECK(::pipe(pipe_descriptors.data()) == 0);
    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        static_cast<void>(::close(pipe_descriptors[0U]));
        auto identity = current_cgroup_owner_identity();
        if (!identity.ok()) ::_exit(111);
        const auto *bytes = reinterpret_cast<const std::uint8_t *>(
            &identity.value());
        std::size_t offset = 0U;
        while (offset < sizeof(CgroupOwnerIdentity)) {
            ssize_t count = ::write(
                pipe_descriptors[1U], bytes + offset,
                sizeof(CgroupOwnerIdentity) - offset);
            if (count < 0 && errno == EINTR) continue;
            if (count <= 0) ::_exit(112);
            offset += static_cast<std::size_t>(count);
        }
        static_cast<void>(::close(pipe_descriptors[1U]));
        ::_exit(0);
    }

    static_cast<void>(::close(pipe_descriptors[1U]));
    CgroupOwnerIdentity identity;
    auto *bytes = reinterpret_cast<std::uint8_t *>(&identity);
    std::size_t offset = 0U;
    while (offset < sizeof(identity)) {
        ssize_t count = ::read(
            pipe_descriptors[0U], bytes + offset, sizeof(identity) - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) break;
        offset += static_cast<std::size_t>(count);
    }
    static_cast<void>(::close(pipe_descriptors[0U]));

    siginfo_t child_info{};
    const int observed = ::waitid(
        P_PID, static_cast<id_t>(child), &child_info, WEXITED | WNOWAIT);
    auto live = cgroup_owner_is_live(identity);
    int child_status = 0;
    const pid_t reaped = ::waitpid(child, &child_status, 0);

    IOTOX_CHECK(offset == sizeof(identity));
    IOTOX_CHECK(observed == 0);
    IOTOX_CHECK(child_info.si_pid == child);
    IOTOX_CHECK(reaped == child);
    IOTOX_CHECK(WIFEXITED(child_status));
    IOTOX_CHECK(WEXITSTATUS(child_status) == 0);
    IOTOX_CHECK(live.ok());
    IOTOX_CHECK(!live.value());
}

IOTOX_TEST("cgroup recovery validates bounded startup policy first") {
    CgroupRecoveryConfig no_candidates;
    no_candidates.maximum_candidates = 0U;
    auto candidates = SessionCgroup::recover_orphans(
        "/unused", no_candidates);
    IOTOX_CHECK(!candidates.ok());
    IOTOX_CHECK(candidates.status().code() == ErrorCode::invalid_argument);

    CgroupRecoveryConfig no_wait;
    no_wait.maximum_wait = std::chrono::milliseconds{0};
    auto wait = SessionCgroup::recover_orphans("/unused", no_wait);
    IOTOX_CHECK(!wait.ok());
    IOTOX_CHECK(wait.status().code() == ErrorCode::invalid_argument);
}

IOTOX_TEST("session cgroup rejects identities that can control the boundary") {
    IdentityPolicy inherited;
    auto inherited_result = SessionCgroup::create("/unused", inherited);
    IOTOX_CHECK(!inherited_result.ok());
    IOTOX_CHECK(inherited_result.status().code() == ErrorCode::invalid_argument);

    IdentityPolicy root = exact_distinct_identity();
    root.uid = 0U;
    auto root_result = SessionCgroup::create("/unused", root);
    IOTOX_CHECK(!root_result.ok());
    IOTOX_CHECK(root_result.status().code() == ErrorCode::invalid_argument);

    const std::uint64_t effective_uid =
        static_cast<std::uint64_t>(::geteuid());
    if (effective_uid <=
        static_cast<std::uint64_t>(std::numeric_limits<std::uint32_t>::max())) {
        IdentityPolicy same = exact_distinct_identity();
        same.uid = static_cast<std::uint32_t>(effective_uid);
        auto same_result = SessionCgroup::create("/unused", same);
        IOTOX_CHECK(!same_result.ok());
        IOTOX_CHECK(same_result.status().code() == ErrorCode::invalid_argument);
    }
}

IOTOX_TEST("session cgroup resource policy rejects ambiguous kernel limits first") {
    auto rejects = [](CgroupResourceLimits limits) {
        auto result = SessionCgroup::create(
            "/unused", exact_distinct_identity(), std::move(limits));
        IOTOX_CHECK(!result.ok());
        IOTOX_CHECK(result.status().code() == ErrorCode::invalid_argument);
    };

    CgroupResourceLimits no_processes;
    no_processes.maximum_processes = 0U;
    rejects(no_processes);

    CgroupResourceLimits excessive_processes;
    excessive_processes.maximum_processes =
        static_cast<std::uint64_t>(std::numeric_limits<pid_t>::max()) + 1U;
    rejects(excessive_processes);

    CgroupResourceLimits period_without_quota;
    period_without_quota.cpu_period_microseconds = 100000U;
    rejects(period_without_quota);

    CgroupResourceLimits tiny_quota;
    tiny_quota.cpu_quota_microseconds = 999U;
    rejects(tiny_quota);

    CgroupResourceLimits tiny_period;
    tiny_period.cpu_quota_microseconds = 1000U;
    tiny_period.cpu_period_microseconds = 999U;
    rejects(tiny_period);

    CgroupResourceLimits excessive_period;
    excessive_period.cpu_quota_microseconds = 1000U;
    excessive_period.cpu_period_microseconds = 1000001U;
    rejects(excessive_period);

    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 1);
    CgroupResourceLimits unaligned_memory;
    unaligned_memory.maximum_memory_bytes =
        static_cast<std::uint64_t>(page_size) + 1U;
    rejects(unaligned_memory);

    CgroupResourceLimits unaligned_memory_high;
    unaligned_memory_high.maximum_memory_high_bytes = 1U;
    rejects(unaligned_memory_high);

    CgroupResourceLimits inverted_memory;
    inverted_memory.maximum_memory_high_bytes =
        static_cast<std::uint64_t>(page_size) * 2U;
    inverted_memory.maximum_memory_bytes =
        static_cast<std::uint64_t>(page_size);
    rejects(inverted_memory);

    CgroupResourceLimits unaligned_swap;
    unaligned_swap.maximum_swap_bytes = 1U;
    rejects(unaligned_swap);

    CgroupResourceLimits valid;
    valid.maximum_processes = 4U;
    valid.maximum_memory_high_bytes =
        static_cast<std::uint64_t>(page_size) * 8U;
    valid.maximum_memory_bytes = static_cast<std::uint64_t>(page_size) * 16U;
    valid.maximum_swap_bytes = 0U;
    valid.cpu_quota_microseconds = 1000U;
    const iotox::Status accepted =
        SessionCgroup::validate_resource_limits(valid);
    IOTOX_CHECK(accepted.ok());
    valid.cpu_period_microseconds = 1000000U;
    IOTOX_CHECK(SessionCgroup::validate_resource_limits(valid).ok());
}

IOTOX_TEST("aggregate cgroup admission reserves atomically and releases exactly once") {
    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    const auto page = static_cast<std::uint64_t>(page_size);

    CgroupAggregateLimits aggregate;
    aggregate.maximum_reserved_processes = 10U;
    aggregate.maximum_reserved_memory_bytes = 4U * page;
    aggregate.maximum_reserved_swap_bytes = 2U * page;
    aggregate.maximum_reserved_cpu_quota_microseconds = 300000U;
    aggregate.cpu_period_microseconds = 100000U;
    auto admission = CgroupAggregateAdmission::create(aggregate);
    IOTOX_CHECK(admission.ok());

    CgroupResourceLimits session;
    session.maximum_processes = 4U;
    session.maximum_memory_bytes = 2U * page;
    session.maximum_swap_bytes = page;
    session.cpu_quota_microseconds = 75000U;
    session.cpu_period_microseconds = 50000U;

    auto first = admission.value()->reserve(session);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().active());
    auto second = admission.value()->reserve(session);
    IOTOX_CHECK(second.ok());

    auto full = admission.value()->snapshot();
    IOTOX_CHECK(full.active_reservations == 2U);
    IOTOX_CHECK(full.reserved_processes == 8U);
    IOTOX_CHECK(full.reserved_memory_bytes == 4U * page);
    IOTOX_CHECK(full.reserved_swap_bytes == 2U * page);
    IOTOX_CHECK(full.reserved_cpu_quota_microseconds == 300000U);

    auto rejected = admission.value()->reserve(session);
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.status().code() == ErrorCode::resource_exhausted);
    IOTOX_CHECK(admission.value()->snapshot().rejected_reservations == 1U);

    CgroupAggregateAdmission::Reservation moved =
        std::move(first).value();
    IOTOX_CHECK(moved.active());
    moved.release();
    moved.release();
    IOTOX_CHECK(!moved.active());

    auto after_release = admission.value()->snapshot();
    IOTOX_CHECK(after_release.active_reservations == 1U);
    IOTOX_CHECK(after_release.reserved_processes == 4U);
    IOTOX_CHECK(after_release.peak_active_reservations == 2U);
    IOTOX_CHECK(after_release.peak_reserved_processes == 8U);
    IOTOX_CHECK(
        after_release.reserved_cpu_quota_microseconds == 150000U);
    IOTOX_CHECK(
        after_release.peak_reserved_cpu_quota_microseconds == 300000U);

    auto replacement = admission.value()->reserve(session);
    IOTOX_CHECK(replacement.ok());
    replacement.value().release();
    second.value().release();
    const auto empty = admission.value()->snapshot();
    IOTOX_CHECK(empty.active_reservations == 0U);
    IOTOX_CHECK(empty.reserved_processes == 0U);
    IOTOX_CHECK(empty.reserved_memory_bytes == 0U);
    IOTOX_CHECK(empty.reserved_swap_bytes == 0U);
    IOTOX_CHECK(empty.reserved_cpu_quota_microseconds == 0U);
    IOTOX_CHECK(
        empty.peak_reserved_cpu_quota_microseconds == 300000U);
    IOTOX_CHECK(empty.rejected_reservations == 1U);

    CgroupAggregateLimits exact_aggregate;
    exact_aggregate.maximum_reserved_processes = 4U;
    exact_aggregate.maximum_reserved_memory_bytes = 2U * page;
    exact_aggregate.maximum_reserved_swap_bytes = page;
    exact_aggregate.maximum_reserved_cpu_quota_microseconds = 150000U;
    exact_aggregate.cpu_period_microseconds = 100000U;
    auto stranded_admission = CgroupAggregateAdmission::create(exact_aggregate);
    IOTOX_CHECK(stranded_admission.ok());
    auto stranded = stranded_admission.value()->reserve(session);
    IOTOX_CHECK(stranded.ok());
    stranded.value().strand();
    stranded.value().strand();
    auto refused_after_strand = stranded_admission.value()->reserve(session);
    IOTOX_CHECK(!refused_after_strand.ok());
    IOTOX_CHECK(
        refused_after_strand.status().code() == ErrorCode::resource_exhausted);
    const auto stranded_snapshot = stranded_admission.value()->snapshot();
    IOTOX_CHECK(stranded_snapshot.active_reservations == 1U);
    IOTOX_CHECK(stranded_snapshot.reserved_processes == 4U);
    IOTOX_CHECK(stranded_snapshot.reserved_memory_bytes == 2U * page);
    IOTOX_CHECK(stranded_snapshot.reserved_swap_bytes == page);
    IOTOX_CHECK(
        stranded_snapshot.reserved_cpu_quota_microseconds == 150000U);
    IOTOX_CHECK(
        stranded_snapshot.peak_reserved_cpu_quota_microseconds == 150000U);
    IOTOX_CHECK(stranded_snapshot.rejected_reservations == 1U);
    IOTOX_CHECK(stranded_snapshot.stranded_reservations == 1U);
}

IOTOX_TEST("aggregate cgroup admission rejects unaccountable sessions before charging") {
    CgroupAggregateLimits aggregate;
    aggregate.maximum_reserved_processes = 8U;
    auto admission = CgroupAggregateAdmission::create(aggregate);
    IOTOX_CHECK(admission.ok());

    CgroupResourceLimits missing;
    auto rejected = admission.value()->reserve(missing);
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.status().code() == ErrorCode::invalid_argument);
    const auto snapshot = admission.value()->snapshot();
    IOTOX_CHECK(snapshot.active_reservations == 0U);
    IOTOX_CHECK(snapshot.rejected_reservations == 0U);

    CgroupAggregateLimits cpu_aggregate;
    cpu_aggregate.maximum_reserved_cpu_quota_microseconds = 100000U;
    cpu_aggregate.cpu_period_microseconds = 100000U;
    auto cpu_admission = CgroupAggregateAdmission::create(cpu_aggregate);
    IOTOX_CHECK(cpu_admission.ok());
    auto missing_cpu = cpu_admission.value()->reserve(missing);
    IOTOX_CHECK(!missing_cpu.ok());
    IOTOX_CHECK(
        missing_cpu.status().code() == ErrorCode::invalid_argument);

    CgroupResourceLimits unrepresentable_cpu;
    unrepresentable_cpu.cpu_quota_microseconds = 1000U;
    unrepresentable_cpu.cpu_period_microseconds = 3000U;
    auto rounded = cpu_admission.value()->reserve(unrepresentable_cpu);
    IOTOX_CHECK(!rounded.ok());
    IOTOX_CHECK(rounded.status().message().find("exactly representable") !=
                std::string::npos);
    const auto cpu_snapshot = cpu_admission.value()->snapshot();
    IOTOX_CHECK(cpu_snapshot.active_reservations == 0U);
    IOTOX_CHECK(cpu_snapshot.reserved_cpu_quota_microseconds == 0U);
    IOTOX_CHECK(cpu_snapshot.rejected_reservations == 0U);

    CgroupAggregateLimits empty_limits;
    auto disabled = CgroupAggregateAdmission::create(empty_limits);
    IOTOX_CHECK(disabled.ok());
    auto no_charge = disabled.value()->reserve(missing);
    IOTOX_CHECK(no_charge.ok());
    IOTOX_CHECK(!no_charge.value().active());
}

IOTOX_TEST("cgroup outcome aggregation is exact content free and independent of ceilings") {
    auto admission = CgroupAggregateAdmission::create(CgroupAggregateLimits{});
    IOTOX_CHECK(admission.ok());

    auto first = admission.value()->reserve(CgroupResourceLimits{});
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(!first.value().active());
    CgroupSessionOutcome outcome;
    outcome.pids_limit_hits = 2U;
    outcome.memory_high_events = 3U;
    outcome.memory_max_events = 5U;
    outcome.memory_oom_events = 7U;
    outcome.memory_oom_kills = 11U;
    outcome.memory_oom_group_kills = 13U;
    outcome.pids_peak = 17U;
    outcome.memory_peak_bytes = 19U;
    outcome.memory_swap_peak_bytes = 23U;
    outcome.cpu_stat_observed = true;
    outcome.cpu_bandwidth_stat_observed = true;
    outcome.cpu_burst_stat_observed = true;
    outcome.cpu_usage_microseconds = 29U;
    outcome.cpu_user_microseconds = 31U;
    outcome.cpu_system_microseconds = 37U;
    outcome.cpu_periods = 41U;
    outcome.cpu_throttled_periods = 43U;
    outcome.cpu_throttled_microseconds = 47U;
    outcome.cpu_burst_periods = 53U;
    outcome.cpu_burst_microseconds = 59U;
    outcome.io_read_bytes = 61U;
    outcome.io_write_bytes = 67U;
    outcome.io_read_operations = 71U;
    outcome.io_write_operations = 73U;
    outcome.io_discard_bytes = 79U;
    outcome.io_discard_operations = 83U;
    outcome.cpu_pressure = CgroupPressure{89U, 97U};
    outcome.memory_pressure = CgroupPressure{101U, 103U};
    outcome.io_pressure = CgroupPressure{107U, std::nullopt};
    outcome.memory_stat = CgroupMemoryStat{
        109U,
        113U,
        CgroupMemoryReclaimStat{127U, 131U},
        CgroupMemorySwapStat{137U, 139U}};
    outcome.memory_swap_events = CgroupMemorySwapEvents{149U, 151U, 157U};
    outcome.local_stat = CgroupLocalStat{163U};
    outcome.irq_pressure = CgroupIrqPressure{167U};
    first.value().record_outcome(outcome);
    first.value().record_outcome(outcome);
    first.value().release();

    auto second = admission.value()->reserve(CgroupResourceLimits{});
    IOTOX_CHECK(second.ok());
    CgroupSessionOutcome incomplete;
    incomplete.telemetry_complete = false;
    second.value().record_outcome(incomplete);
    second.value().release();

    const auto snapshot = admission.value()->snapshot();
    IOTOX_CHECK(snapshot.completed_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.incomplete_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.pids_limit_hits == 2U);
    IOTOX_CHECK(snapshot.memory_high_events == 3U);
    IOTOX_CHECK(snapshot.memory_max_events == 5U);
    IOTOX_CHECK(snapshot.memory_oom_events == 7U);
    IOTOX_CHECK(snapshot.memory_oom_kills == 11U);
    IOTOX_CHECK(snapshot.memory_oom_group_kills == 13U);
    IOTOX_CHECK(snapshot.pids_peak_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.pids_peak_sum == 17U);
    IOTOX_CHECK(snapshot.pids_peak_maximum == 17U);
    IOTOX_CHECK(snapshot.memory_peak_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_peak_sum_bytes == 19U);
    IOTOX_CHECK(snapshot.memory_peak_maximum_bytes == 19U);
    IOTOX_CHECK(snapshot.memory_swap_peak_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_swap_peak_sum_bytes == 23U);
    IOTOX_CHECK(snapshot.memory_swap_peak_maximum_bytes == 23U);
    IOTOX_CHECK(snapshot.cpu_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.cpu_bandwidth_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.cpu_burst_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.cpu_usage_microseconds == 29U);
    IOTOX_CHECK(snapshot.cpu_user_microseconds == 31U);
    IOTOX_CHECK(snapshot.cpu_system_microseconds == 37U);
    IOTOX_CHECK(snapshot.cpu_periods == 41U);
    IOTOX_CHECK(snapshot.cpu_throttled_periods == 43U);
    IOTOX_CHECK(snapshot.cpu_throttled_microseconds == 47U);
    IOTOX_CHECK(snapshot.cpu_burst_periods == 53U);
    IOTOX_CHECK(snapshot.cpu_burst_microseconds == 59U);
    IOTOX_CHECK(snapshot.io_read_bytes == 61U);
    IOTOX_CHECK(snapshot.io_write_bytes == 67U);
    IOTOX_CHECK(snapshot.io_read_operations == 71U);
    IOTOX_CHECK(snapshot.io_write_operations == 73U);
    IOTOX_CHECK(snapshot.io_discard_bytes == 79U);
    IOTOX_CHECK(snapshot.io_discard_operations == 83U);
    IOTOX_CHECK(snapshot.cpu_pressure_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.cpu_pressure_full_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.cpu_pressure_some_microseconds == 89U);
    IOTOX_CHECK(snapshot.cpu_pressure_full_microseconds == 97U);
    IOTOX_CHECK(snapshot.memory_pressure_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_pressure_full_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_pressure_some_microseconds == 101U);
    IOTOX_CHECK(snapshot.memory_pressure_full_microseconds == 103U);
    IOTOX_CHECK(snapshot.io_pressure_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.io_pressure_full_session_outcomes == 0U);
    IOTOX_CHECK(snapshot.io_pressure_some_microseconds == 107U);
    IOTOX_CHECK(snapshot.io_pressure_full_microseconds == 0U);
    IOTOX_CHECK(snapshot.memory_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_reclaim_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_swap_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_page_faults == 109U);
    IOTOX_CHECK(snapshot.memory_major_page_faults == 113U);
    IOTOX_CHECK(snapshot.memory_pages_scanned == 127U);
    IOTOX_CHECK(snapshot.memory_pages_reclaimed == 131U);
    IOTOX_CHECK(snapshot.memory_pages_swapped_in == 137U);
    IOTOX_CHECK(snapshot.memory_pages_swapped_out == 139U);
    IOTOX_CHECK(snapshot.memory_swap_events_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.memory_swap_high_events == 149U);
    IOTOX_CHECK(snapshot.memory_swap_max_events == 151U);
    IOTOX_CHECK(snapshot.memory_swap_fail_events == 157U);
    IOTOX_CHECK(snapshot.local_stat_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.frozen_microseconds == 163U);
    IOTOX_CHECK(snapshot.irq_pressure_session_outcomes == 1U);
    IOTOX_CHECK(snapshot.irq_pressure_full_microseconds == 167U);

    auto saturation = admission.value()->reserve(CgroupResourceLimits{});
    IOTOX_CHECK(saturation.ok());
    CgroupSessionOutcome maximum;
    maximum.pids_limit_hits = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_high_events = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_max_events = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_oom_events = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_oom_kills = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_oom_group_kills =
        std::numeric_limits<std::uint64_t>::max();
    maximum.pids_peak = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_peak_bytes = std::numeric_limits<std::uint64_t>::max();
    maximum.memory_swap_peak_bytes =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_stat_observed = true;
    maximum.cpu_bandwidth_stat_observed = true;
    maximum.cpu_burst_stat_observed = true;
    maximum.cpu_usage_microseconds =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_user_microseconds =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_system_microseconds =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_periods = std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_throttled_periods =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_throttled_microseconds =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_burst_periods =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_burst_microseconds =
        std::numeric_limits<std::uint64_t>::max();
    maximum.io_read_bytes = std::numeric_limits<std::uint64_t>::max();
    maximum.io_write_bytes = std::numeric_limits<std::uint64_t>::max();
    maximum.io_read_operations = std::numeric_limits<std::uint64_t>::max();
    maximum.io_write_operations = std::numeric_limits<std::uint64_t>::max();
    maximum.io_discard_bytes = std::numeric_limits<std::uint64_t>::max();
    maximum.io_discard_operations =
        std::numeric_limits<std::uint64_t>::max();
    maximum.cpu_pressure = CgroupPressure{
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max()};
    maximum.memory_pressure = CgroupPressure{
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max()};
    maximum.io_pressure = CgroupPressure{
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max()};
    maximum.memory_stat = CgroupMemoryStat{
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max(),
        CgroupMemoryReclaimStat{
            std::numeric_limits<std::uint64_t>::max(),
            std::numeric_limits<std::uint64_t>::max()},
        CgroupMemorySwapStat{
            std::numeric_limits<std::uint64_t>::max(),
            std::numeric_limits<std::uint64_t>::max()}};
    maximum.memory_swap_events = CgroupMemorySwapEvents{
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max()};
    maximum.local_stat =
        CgroupLocalStat{std::numeric_limits<std::uint64_t>::max()};
    maximum.irq_pressure =
        CgroupIrqPressure{std::numeric_limits<std::uint64_t>::max()};
    saturation.value().record_outcome(maximum);
    saturation.value().release();

    auto overflow = admission.value()->reserve(CgroupResourceLimits{});
    IOTOX_CHECK(overflow.ok());
    overflow.value().record_outcome(outcome);
    overflow.value().release();
    const auto saturated = admission.value()->snapshot();
    IOTOX_CHECK(saturated.completed_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.pids_limit_hits ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_high_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_max_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_oom_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_oom_kills ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_oom_group_kills ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.pids_peak_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.pids_peak_sum ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.pids_peak_maximum ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.memory_peak_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.memory_peak_sum_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_peak_maximum_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.memory_swap_peak_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.memory_swap_peak_sum_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_swap_peak_maximum_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.cpu_stat_session_outcomes == 3U);
    IOTOX_CHECK(saturated.cpu_bandwidth_stat_session_outcomes == 3U);
    IOTOX_CHECK(saturated.cpu_burst_stat_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.cpu_usage_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_user_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_system_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_periods ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_throttled_periods ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_throttled_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_burst_periods ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_burst_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_read_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_write_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_read_operations ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_write_operations ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_discard_bytes ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_discard_operations ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.cpu_pressure_session_outcomes == 3U);
    IOTOX_CHECK(saturated.cpu_pressure_full_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.cpu_pressure_some_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.cpu_pressure_full_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.memory_pressure_session_outcomes == 3U);
    IOTOX_CHECK(saturated.memory_pressure_full_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.memory_pressure_some_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_pressure_full_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.io_pressure_session_outcomes == 3U);
    IOTOX_CHECK(saturated.io_pressure_full_session_outcomes == 1U);
    IOTOX_CHECK(
        saturated.io_pressure_some_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.io_pressure_full_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.memory_stat_session_outcomes == 3U);
    IOTOX_CHECK(saturated.memory_reclaim_stat_session_outcomes == 3U);
    IOTOX_CHECK(saturated.memory_swap_stat_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.memory_page_faults ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_major_page_faults ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_pages_scanned ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_pages_reclaimed ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_pages_swapped_in ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_pages_swapped_out ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.memory_swap_events_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.memory_swap_high_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_swap_max_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(
        saturated.memory_swap_fail_events ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.local_stat_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.frozen_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(saturated.irq_pressure_session_outcomes == 3U);
    IOTOX_CHECK(
        saturated.irq_pressure_full_microseconds ==
        std::numeric_limits<std::uint64_t>::max());
}

IOTOX_TEST("aggregate cgroup admission serializes concurrent capacity claims") {
    CgroupAggregateLimits aggregate;
    aggregate.maximum_reserved_processes = 4U;
    aggregate.maximum_reserved_cpu_quota_microseconds = 100000U;
    aggregate.cpu_period_microseconds = 100000U;
    auto admission = CgroupAggregateAdmission::create(aggregate);
    IOTOX_CHECK(admission.ok());

    CgroupResourceLimits session;
    session.maximum_processes = 1U;
    session.cpu_quota_microseconds = 25000U;
    session.cpu_period_microseconds = 100000U;
    constexpr std::size_t kClaimants = 12U;
    std::atomic<bool> start{false};
    std::atomic<bool> release{false};
    std::atomic<std::size_t> attempted{0U};
    std::atomic<std::size_t> accepted{0U};
    std::atomic<std::size_t> rejected{0U};
    std::atomic<std::size_t> wrong_error{0U};
    std::vector<std::thread> claimants;
    claimants.reserve(kClaimants);
    for (std::size_t index = 0U; index < kClaimants; ++index) {
        claimants.emplace_back([&] {
            while (!start.load()) std::this_thread::yield();
            auto reservation = admission.value()->reserve(session);
            if (reservation.ok()) {
                accepted.fetch_add(1U);
                attempted.fetch_add(1U);
                while (!release.load()) std::this_thread::yield();
            } else {
                if (reservation.status().code() !=
                    ErrorCode::resource_exhausted) {
                    wrong_error.fetch_add(1U);
                }
                rejected.fetch_add(1U);
                attempted.fetch_add(1U);
            }
        });
    }
    start.store(true);
    while (attempted.load() != kClaimants) std::this_thread::yield();

    const auto saturated = admission.value()->snapshot();
    IOTOX_CHECK(accepted.load() == 4U);
    IOTOX_CHECK(rejected.load() == 8U);
    IOTOX_CHECK(wrong_error.load() == 0U);
    IOTOX_CHECK(saturated.active_reservations == 4U);
    IOTOX_CHECK(saturated.reserved_processes == 4U);
    IOTOX_CHECK(saturated.reserved_cpu_quota_microseconds == 100000U);
    IOTOX_CHECK(saturated.rejected_reservations == 8U);

    release.store(true);
    for (std::thread &claimant : claimants) claimant.join();
    const auto drained = admission.value()->snapshot();
    IOTOX_CHECK(drained.active_reservations == 0U);
    IOTOX_CHECK(drained.reserved_processes == 0U);
    IOTOX_CHECK(drained.reserved_cpu_quota_microseconds == 0U);
    IOTOX_CHECK(drained.peak_active_reservations == 4U);
    IOTOX_CHECK(
        drained.peak_reserved_cpu_quota_microseconds == 100000U);
}

IOTOX_TEST("session cgroup refuses a lookalike ordinary directory") {
    TempDirectory temporary;
    auto created = SessionCgroup::create(
        temporary.path(), exact_distinct_identity());
    IOTOX_CHECK(!created.ok());
    IOTOX_CHECK(created.status().code() == ErrorCode::unsupported);
    IOTOX_CHECK(created.status().message().find("cgroup v2") !=
                std::string::npos);
}

IOTOX_TEST("cgroup recovery refuses a lookalike ordinary directory") {
    TempDirectory temporary;
    auto recovered = SessionCgroup::recover_orphans(temporary.path());
    IOTOX_CHECK(!recovered.ok());
    IOTOX_CHECK(recovered.status().code() == ErrorCode::unsupported);
    IOTOX_CHECK(recovered.status().message().find("cgroup v2") !=
                std::string::npos);
}

}  // namespace
