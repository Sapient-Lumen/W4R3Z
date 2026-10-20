#include "iotox/local/runtime_tree.hpp"
#include "test_harness.hpp"

#include <array>
#include <atomic>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <optional>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class ScopedEnvironment {
  public:
    explicit ScopedEnvironment(std::string name) : name_(std::move(name)) {
        if (const char *value = ::getenv(name_.c_str()); value != nullptr) {
            original_ = value;
        }
    }

    ~ScopedEnvironment() {
        if (original_) {
            static_cast<void>(::setenv(
                name_.c_str(), original_->c_str(), 1));
        } else {
            static_cast<void>(::unsetenv(name_.c_str()));
        }
    }

    ScopedEnvironment(const ScopedEnvironment &) = delete;
    ScopedEnvironment &operator=(const ScopedEnvironment &) = delete;

  private:
    std::string name_;
    std::optional<std::string> original_;
};

std::filesystem::path runtime_test_directory(std::string_view suffix) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("iotox-runtime-test-" + std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)) + "-" + std::string(suffix));
}

std::string read_text(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    std::ostringstream output;
    output << input.rdbuf();
    return output.str();
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

unsigned int permission_bits(const std::filesystem::path &path) {
    struct stat metadata {};
    IOTOX_CHECK(::lstat(path.c_str(), &metadata) == 0);
    return static_cast<unsigned int>(metadata.st_mode & 0777);
}

bool path_is_fifo(const std::filesystem::path &path) {
    struct stat metadata {};
    IOTOX_CHECK(::lstat(path.c_str(), &metadata) == 0);
    return S_ISFIFO(metadata.st_mode);
}

ino_t inode_number(const std::filesystem::path &path) {
    struct stat metadata {};
    IOTOX_CHECK(::lstat(path.c_str(), &metadata) == 0);
    return metadata.st_ino;
}

}  // namespace

IOTOX_TEST("default Tox savedata paths separate route identities") {
    ScopedEnvironment state_override{"IOTOX_STATE_PATH"};
    ScopedEnvironment xdg_state{"XDG_STATE_HOME"};
    IOTOX_CHECK(::unsetenv("IOTOX_STATE_PATH") == 0);
    IOTOX_CHECK(::setenv("XDG_STATE_HOME", "/tmp/iotox-route-state", 1) == 0);

    IOTOX_CHECK(
        iotox::local::default_state_path(iotox::ToxRoute::native) ==
        "/tmp/iotox-route-state/iotox/device.toxsave");
    IOTOX_CHECK(
        iotox::local::default_state_path(iotox::ToxRoute::tor) ==
        "/tmp/iotox-route-state/iotox/device.tox-tor.toxsave");
    IOTOX_CHECK(
        iotox::local::default_state_path(iotox::ToxRoute::i2p) ==
        "/tmp/iotox-route-state/iotox/device.tox-i2p.toxsave");
    IOTOX_CHECK(
        iotox::local::default_state_path(
            iotox::ToxRoute::i2p_construction) ==
        "/tmp/iotox-route-state/iotox/device.tox-i2p.toxsave");

    IOTOX_CHECK(::setenv(
        "IOTOX_STATE_PATH", "/tmp/operator-selected.toxsave", 1) == 0);
    IOTOX_CHECK(
        iotox::local::default_state_path(iotox::ToxRoute::native) ==
        "/tmp/operator-selected.toxsave");
    IOTOX_CHECK(
        iotox::local::default_state_path(iotox::ToxRoute::tor) ==
        "/tmp/operator-selected.toxsave");
}

IOTOX_TEST("runtime tree publishes a private ratox-inspired read surface") {
    const std::filesystem::path root = runtime_test_directory("surface");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    const iotox::Status prepared = tree.prepare();
    IOTOX_CHECK_MSG(prepared.ok(), prepared.message());
    IOTOX_CHECK(permission_bits(root) == 0700U);
    IOTOX_CHECK(permission_bits(root / "self") == 0700U);
    IOTOX_CHECK(permission_bits(root / "peers") == 0700U);
    IOTOX_CHECK(permission_bits(root / "transfers") == 0700U);

    iotox::local::RuntimeSnapshot snapshot;
    snapshot.phase = "running";
    snapshot.address = "ABCDEF";
    snapshot.backend = "mock toxcore";
    snapshot.self_connection = "tcp";
    snapshot.last_event = "backend-ready";
    snapshot.event_count = 4U;
    const iotox::Status published = tree.publish(snapshot);
    IOTOX_CHECK_MSG(published.ok(), published.message());

    const std::string status = read_text(root / "status");
    IOTOX_CHECK(status.find("phase=running") != std::string::npos);
    IOTOX_CHECK(status.find("address=ABCDEF") != std::string::npos);
    IOTOX_CHECK(status.find("event-count=4") != std::string::npos);
    IOTOX_CHECK(read_text(root / "self" / "address") == "ABCDEF\n");
    IOTOX_CHECK(permission_bits(root / "status") == 0600U);
    IOTOX_CHECK(permission_bits(root / "self" / "address") == 0600U);

    std::filesystem::remove_all(root, ignored);
}


IOTOX_TEST("runtime Ratox status and lifecycle journal are bounded and content free") {
    const std::filesystem::path root = runtime_test_directory("ratox-events");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree::Config config;
    config.root = root;
    config.ratox_rotation_bytes = 1U;
    iotox::local::RuntimeTree tree(config);
    IOTOX_CHECK(tree.prepare().ok());

    iotox::local::RuntimeSnapshot snapshot;
    snapshot.phase = "running";
    snapshot.ratox_enabled = true;
    snapshot.ratox_latency_mode_active = true;
    snapshot.ratox_active_service_interval_ms = 5U;
    snapshot.ratox_active_transport_iteration_interval_ms = 5U;
    snapshot.ratox_configuration_valid = true;
    snapshot.ratox_cgroup_host_budget_configured = true;
    snapshot.ratox_cgroup_aggregate_budget_configured = true;
    snapshot.ratox_cgroup_aggregate_pids_configured = true;
    snapshot.ratox_cgroup_aggregate_memory_configured = true;
    snapshot.ratox_cgroup_aggregate_swap_configured = true;
    snapshot.ratox_cgroup_aggregate_cpu_configured = true;
    snapshot.ratox_cgroup_aggregate_pids_max = 64U;
    snapshot.ratox_cgroup_aggregate_memory_max_bytes = 16384U;
    snapshot.ratox_cgroup_aggregate_swap_max_bytes = 0U;
    snapshot.ratox_cgroup_aggregate_cpu_quota_max_microseconds = 300000U;
    snapshot.ratox_cgroup_aggregate_cpu_period_microseconds = 100000U;
    snapshot.ratox_cgroup_aggregate_active_reservations = 2U;
    snapshot.ratox_cgroup_aggregate_peak_active_reservations = 4U;
    snapshot.ratox_cgroup_aggregate_reserved_processes = 32U;
    snapshot.ratox_cgroup_aggregate_reserved_memory_bytes = 4096U;
    snapshot.ratox_cgroup_aggregate_reserved_swap_bytes = 1024U;
    snapshot.ratox_cgroup_aggregate_reserved_cpu_quota_microseconds = 150000U;
    snapshot.ratox_cgroup_aggregate_peak_reserved_processes = 48U;
    snapshot.ratox_cgroup_aggregate_peak_reserved_memory_bytes = 8192U;
    snapshot.ratox_cgroup_aggregate_peak_reserved_swap_bytes = 2048U;
    snapshot.ratox_cgroup_aggregate_peak_reserved_cpu_quota_microseconds =
        300000U;
    snapshot.ratox_cgroup_aggregate_rejected_reservations = 3U;
    snapshot.ratox_cgroup_aggregate_stranded_reservations = 1U;
    snapshot.ratox_cgroup_pressure_admission_configured = true;
    snapshot.ratox_cgroup_pressure_admission_cpu_some_configured = true;
    snapshot.ratox_cgroup_pressure_admission_memory_full_configured = true;
    snapshot.ratox_cgroup_pressure_admission_io_full_configured = true;
    snapshot.ratox_cgroup_pressure_admission_cpu_some_avg10_max_basis_points =
        125U;
    snapshot
        .ratox_cgroup_pressure_admission_memory_full_avg10_max_basis_points =
        250U;
    snapshot.ratox_cgroup_pressure_admission_io_full_avg10_max_basis_points =
        375U;
    snapshot.ratox_cgroup_pressure_admission_hysteresis_basis_points = 25U;
    snapshot.ratox_cgroup_pressure_admission_cpu_some_trigger_configured = true;
    snapshot.ratox_cgroup_pressure_admission_memory_full_trigger_configured =
        true;
    snapshot.ratox_cgroup_pressure_admission_io_full_trigger_configured = true;
    snapshot.ratox_cgroup_pressure_admission_trigger_window_microseconds =
        2000000U;
    snapshot
        .ratox_cgroup_pressure_admission_cpu_some_trigger_stall_microseconds =
        250000U;
    snapshot
        .ratox_cgroup_pressure_admission_memory_full_trigger_stall_microseconds =
        100000U;
    snapshot
        .ratox_cgroup_pressure_admission_io_full_trigger_stall_microseconds =
        50000U;
    snapshot.ratox_cgroup_pressure_admission_closed = true;
    snapshot.ratox_cgroup_pressure_admission_checks = 201U;
    snapshot.ratox_cgroup_pressure_admission_admitted = 202U;
    snapshot.ratox_cgroup_pressure_admission_rejections = 203U;
    snapshot.ratox_cgroup_pressure_admission_sampling_failures = 204U;
    snapshot.ratox_cgroup_pressure_admission_closed_transitions = 205U;
    snapshot.ratox_cgroup_pressure_admission_reopened_transitions = 206U;
    snapshot.ratox_cgroup_pressure_admission_trigger_monitor_healthy = false;
    snapshot.ratox_cgroup_pressure_admission_trigger_hold_active = true;
    snapshot
        .ratox_cgroup_pressure_admission_trigger_hold_remaining_microseconds =
        750000U;
    snapshot.ratox_cgroup_pressure_admission_trigger_monitor_error_code =
        iotox::ErrorCode::unavailable;
    snapshot.ratox_cgroup_pressure_admission_trigger_events = 207U;
    snapshot.ratox_cgroup_pressure_admission_cpu_some_trigger_events = 208U;
    snapshot.ratox_cgroup_pressure_admission_memory_full_trigger_events = 209U;
    snapshot.ratox_cgroup_pressure_admission_io_full_trigger_events = 210U;
    snapshot.ratox_cgroup_pressure_admission_trigger_monitor_failures = 211U;
    snapshot.ratox_cgroup_pressure_admission_trigger_closed_transitions = 212U;
    snapshot.ratox_cgroup_pressure_admission_trigger_hold_rejections = 213U;
    snapshot.ratox_cgroup_pressure_admission_last_sample_valid = false;
    snapshot.ratox_cgroup_pressure_admission_last_sampling_error_code =
        iotox::ErrorCode::io_error;
    snapshot.ratox_cgroup_pressure_admission_last_cpu_some_observed = true;
    snapshot.ratox_cgroup_pressure_admission_last_memory_full_observed = true;
    snapshot.ratox_cgroup_pressure_admission_last_io_full_observed = true;
    snapshot
        .ratox_cgroup_pressure_admission_last_cpu_some_avg10_basis_points =
        126U;
    snapshot
        .ratox_cgroup_pressure_admission_last_memory_full_avg10_basis_points =
        251U;
    snapshot
        .ratox_cgroup_pressure_admission_last_io_full_avg10_basis_points =
        376U;
    snapshot.ratox_cgroup_completed_session_outcomes = 21U;
    snapshot.ratox_cgroup_incomplete_session_outcomes = 22U;
    snapshot.ratox_cgroup_pids_limit_hits = 23U;
    snapshot.ratox_cgroup_memory_high_events = 24U;
    snapshot.ratox_cgroup_memory_max_events = 25U;
    snapshot.ratox_cgroup_memory_oom_events = 26U;
    snapshot.ratox_cgroup_memory_oom_kills = 27U;
    snapshot.ratox_cgroup_memory_oom_group_kills = 28U;
    snapshot.ratox_cgroup_pids_peak_session_outcomes = 101U;
    snapshot.ratox_cgroup_pids_peak_sum = 102U;
    snapshot.ratox_cgroup_pids_peak_maximum = 103U;
    snapshot.ratox_cgroup_memory_peak_session_outcomes = 104U;
    snapshot.ratox_cgroup_memory_peak_sum_bytes = 105U;
    snapshot.ratox_cgroup_memory_peak_maximum_bytes = 106U;
    snapshot.ratox_cgroup_memory_swap_peak_session_outcomes = 107U;
    snapshot.ratox_cgroup_memory_swap_peak_sum_bytes = 108U;
    snapshot.ratox_cgroup_memory_swap_peak_maximum_bytes = 109U;
    snapshot.ratox_cgroup_memory_stat_session_outcomes = 117U;
    snapshot.ratox_cgroup_memory_reclaim_stat_session_outcomes = 118U;
    snapshot.ratox_cgroup_memory_swap_stat_session_outcomes = 119U;
    snapshot.ratox_cgroup_memory_page_faults = 120U;
    snapshot.ratox_cgroup_memory_major_page_faults = 121U;
    snapshot.ratox_cgroup_memory_pages_scanned = 122U;
    snapshot.ratox_cgroup_memory_pages_reclaimed = 123U;
    snapshot.ratox_cgroup_memory_pages_swapped_in = 124U;
    snapshot.ratox_cgroup_memory_pages_swapped_out = 125U;
    snapshot.ratox_cgroup_memory_swap_events_session_outcomes = 126U;
    snapshot.ratox_cgroup_memory_swap_high_events = 127U;
    snapshot.ratox_cgroup_memory_swap_max_events = 128U;
    snapshot.ratox_cgroup_memory_swap_fail_events = 129U;
    snapshot.ratox_cgroup_local_stat_session_outcomes = 130U;
    snapshot.ratox_cgroup_frozen_microseconds = 131U;
    snapshot.ratox_cgroup_cpu_stat_session_outcomes = 110U;
    snapshot.ratox_cgroup_cpu_bandwidth_stat_session_outcomes = 111U;
    snapshot.ratox_cgroup_cpu_burst_stat_session_outcomes = 112U;
    snapshot.ratox_cgroup_cpu_usage_microseconds = 29U;
    snapshot.ratox_cgroup_cpu_user_microseconds = 113U;
    snapshot.ratox_cgroup_cpu_system_microseconds = 114U;
    snapshot.ratox_cgroup_cpu_periods = 30U;
    snapshot.ratox_cgroup_cpu_throttled_periods = 31U;
    snapshot.ratox_cgroup_cpu_throttled_microseconds = 32U;
    snapshot.ratox_cgroup_cpu_burst_periods = 115U;
    snapshot.ratox_cgroup_cpu_burst_microseconds = 116U;
    snapshot.ratox_cgroup_io_read_bytes = 33U;
    snapshot.ratox_cgroup_io_write_bytes = 34U;
    snapshot.ratox_cgroup_io_read_operations = 35U;
    snapshot.ratox_cgroup_io_write_operations = 36U;
    snapshot.ratox_cgroup_io_discard_bytes = 37U;
    snapshot.ratox_cgroup_io_discard_operations = 38U;
    snapshot.ratox_cgroup_cpu_pressure_session_outcomes = 39U;
    snapshot.ratox_cgroup_cpu_pressure_full_session_outcomes = 40U;
    snapshot.ratox_cgroup_cpu_pressure_some_microseconds = 41U;
    snapshot.ratox_cgroup_cpu_pressure_full_microseconds = 42U;
    snapshot.ratox_cgroup_memory_pressure_session_outcomes = 43U;
    snapshot.ratox_cgroup_memory_pressure_full_session_outcomes = 44U;
    snapshot.ratox_cgroup_memory_pressure_some_microseconds = 45U;
    snapshot.ratox_cgroup_memory_pressure_full_microseconds = 46U;
    snapshot.ratox_cgroup_io_pressure_session_outcomes = 47U;
    snapshot.ratox_cgroup_io_pressure_full_session_outcomes = 48U;
    snapshot.ratox_cgroup_io_pressure_some_microseconds = 49U;
    snapshot.ratox_cgroup_io_pressure_full_microseconds = 50U;
    snapshot.ratox_cgroup_irq_pressure_session_outcomes = 51U;
    snapshot.ratox_cgroup_irq_pressure_full_microseconds = 52U;
    snapshot.ratox_cgroup_profile_budget_count = 14U;
    snapshot.ratox_cgroup_preflight_policy_count = 15U;
    snapshot.ratox_cgroup_recovery_reserved_names = 16U;
    snapshot.ratox_cgroup_recovery_live_incarnations = 17U;
    snapshot.ratox_cgroup_recovery_stale_incarnations = 18U;
    snapshot.ratox_cgroup_recovery_recovered_incarnations = 19U;
    snapshot.ratox_cgroup_recovery_empty_legacy_removed = 20U;
    snapshot.ratox_session_count = 3U;
    snapshot.ratox_live_session_count = 2U;
    snapshot.ratox_running_process_count = 2U;
    snapshot.ratox_attached_session_count = 1U;
    snapshot.ratox_admission_replay_count = 4U;
    snapshot.ratox_outbound_packet_count = 5U;
    snapshot.ratox_event_count = 6U;
    snapshot.ratox_dropped_event_count = 7U;
    snapshot.ratox_controller_retryable_send_rejections = 8U;
    snapshot.ratox_controller_current_retry_streak = 9U;
    snapshot.ratox_controller_maximum_retry_streak = 10U;
    snapshot.ratox_controller_retry_age_us = 11U;
    snapshot.ratox_host_retryable_send_rejections = 12U;
    snapshot.ratox_host_current_retry_streak = 13U;
    snapshot.ratox_host_maximum_retry_streak = 14U;
    snapshot.ratox_host_retry_age_us = 15U;
    snapshot.transport_stats.pending_events = 16U;
    snapshot.transport_stats.maximum_pending_events = 17U;
    snapshot.transport_stats.required_event_backpressure_count = 19U;
    snapshot.transport_stats.required_event_backpressure_total_us = 20U;
    snapshot.transport_stats.required_event_backpressure_maximum_us = 21U;
    snapshot.transport_stats.file_pacing_paused_transfers = 2U;
    snapshot.transport_stats.file_pacing_high_watermark = 64U;
    snapshot.transport_stats.file_pacing_low_watermark = 16U;
    snapshot.transport_stats.file_pacing_minimum_hold_us = 5000U;
    snapshot.transport_stats.file_pacing_resume_batch_limit = 2U;
    snapshot.transport_stats.file_pacing_pause_count = 22U;
    snapshot.transport_stats.file_pacing_resume_count = 20U;
    snapshot.transport_stats.file_pacing_resume_batch_count = 11U;
    snapshot.transport_stats.file_pacing_resume_batch_maximum = 2U;
    snapshot.transport_stats.file_pacing_external_pause_count = 2U;
    snapshot.transport_stats.file_pacing_pause_failure_count = 3U;
    snapshot.transport_stats.file_pacing_resume_failure_count = 4U;
    snapshot.transport_stats.file_pacing_total_hold_us = 123456U;
    snapshot.transport_stats.file_pacing_maximum_hold_us = 9000U;
    snapshot.file_carrier_stats.window_per_peer = 1U;
    snapshot.file_carrier_stats.rotation_quantum_ms = 20U;
    snapshot.file_carrier_stats.runnable_receives = 2U;
    snapshot.file_carrier_stats.waiting_receives = 3U;
    snapshot.file_carrier_stats.admission_count = 44U;
    snapshot.file_carrier_stats.rotation_count = 33U;
    snapshot.file_carrier_stats.pause_count = 34U;
    snapshot.file_carrier_stats.resume_count = 44U;
    snapshot.file_carrier_stats.control_failure_count = 1U;
    snapshot.file_carrier_stats.total_wait_us = 567890U;
    snapshot.file_carrier_stats.maximum_wait_us = 45678U;
    snapshot.transport_stats.interactive.total_queue_wait_us = 1234U;
    snapshot.transport_stats.interactive.queue_wait_p99_upper_bound_us = 1999U;
    snapshot.transport_stats.interactive.queue_wait_p99_exact = true;
    snapshot.transport_stats.interactive.queue_wait_at_or_above_2000_us = 3U;
    snapshot.transport_stats.control.queue_wait_p95_upper_bound_us = 8191U;
    snapshot.transport_stats.control.queue_wait_p95_exact = false;
    snapshot.transport_stats.bulk.queue_wait_p50_upper_bound_us = 41U;
    snapshot.transport_stats.sensitive_lossless.calls = 11U;
    snapshot.transport_stats.sensitive_lossless.toxcore_attempts = 10U;
    snapshot.transport_stats.sensitive_lossless.accepted = 8U;
    snapshot.transport_stats.sensitive_lossless.send_queue_full = 2U;
    IOTOX_CHECK(tree.publish(snapshot).ok());
    const std::string status = read_text(root / "status");
    IOTOX_CHECK(status.find("ratox-enabled=1") != std::string::npos);
    IOTOX_CHECK(status.find("ratox-latency-mode-active=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-active-service-interval-ms=5") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-active-transport-iteration-interval-ms=5") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-configuration-valid=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-host-budget-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-budget-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-pids-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-memory-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-swap-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-cpu-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-pids-max=64") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-memory-max-bytes=16384") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-swap-max-bytes=0") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-cpu-quota-max-us=300000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-cpu-period-us=100000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-active-reservations=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-peak-active-reservations=4") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-reserved-processes=32") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-reserved-memory-bytes=4096") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-reserved-swap-bytes=1024") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-reserved-cpu-quota-us=150000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-peak-reserved-processes=48") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-peak-reserved-memory-bytes=8192") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-peak-reserved-swap-bytes=2048") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-peak-reserved-cpu-quota-us=300000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-rejected-reservations=3") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-aggregate-stranded-reservations=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-cpu-some-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-memory-full-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-io-full-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-cpu-some-avg10-max-bp=125") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-memory-full-avg10-max-bp=250") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-io-full-avg10-max-bp=375") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-hysteresis-bp=25") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-cpu-some-trigger-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-memory-full-trigger-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-io-full-trigger-configured=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-window-us=2000000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-cpu-some-trigger-stall-us=250000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-memory-full-trigger-stall-us=100000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-io-full-trigger-stall-us=50000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-closed=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-checks=201") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-admitted=202") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-rejections=203") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-sampling-failures=204") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-closed-transitions=205") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-reopened-transitions=206") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-monitor-healthy=0") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-hold-active=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-hold-remaining-us=750000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-monitor-error-code=unavailable") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-events=207") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-cpu-some-trigger-events=208") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-memory-full-trigger-events=209") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-io-full-trigger-events=210") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-monitor-failures=211") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-closed-transitions=212") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-trigger-hold-rejections=213") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-sample-valid=0") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-sampling-error-code=io-error") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-cpu-some-observed=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-memory-full-observed=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-io-full-observed=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-cpu-some-avg10-bp=126") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-memory-full-avg10-bp=251") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pressure-admission-last-io-full-avg10-bp=376") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-completed-session-outcomes=21") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-incomplete-session-outcomes=22") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-pids-limit-hits=23") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-high-events=24") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-max-events=25") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-oom-events=26") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-oom-kills=27") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-oom-group-kills=28") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-pids-peak-session-outcomes=101") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-pids-peak-sum=102") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-pids-peak-max=103") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-peak-session-outcomes=104") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-peak-sum-bytes=105") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-peak-max-bytes=106") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-peak-session-outcomes=107") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-peak-sum-bytes=108") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-peak-max-bytes=109") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-stat-session-outcomes=117") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-reclaim-stat-session-outcomes=118") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-stat-session-outcomes=119") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-page-faults=120") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-major-page-faults=121") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pages-scanned=122") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pages-reclaimed=123") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pages-swapped-in=124") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pages-swapped-out=125") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-events-session-outcomes=126") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-high-events=127") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-max-events=128") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-swap-fail-events=129") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-local-stat-session-outcomes=130") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-frozen-us=131") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-stat-session-outcomes=110") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-bandwidth-stat-session-outcomes=111") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-burst-stat-session-outcomes=112") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-usage-us=29") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-user-us=113") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-system-us=114") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-periods=30") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-throttled-periods=31") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-throttled-us=32") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-burst-periods=115") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-burst-us=116") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-read-bytes=33") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-write-bytes=34") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-read-operations=35") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-write-operations=36") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-discard-bytes=37") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-discard-operations=38") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-pressure-session-outcomes=39") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-cpu-pressure-full-session-outcomes=40") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-pressure-some-us=41") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-cpu-pressure-full-us=42") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pressure-session-outcomes=43") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-memory-pressure-full-session-outcomes=44") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-pressure-some-us=45") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-memory-pressure-full-us=46") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-io-pressure-session-outcomes=47") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-io-pressure-full-session-outcomes=48") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-pressure-some-us=49") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-io-pressure-full-us=50") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-irq-pressure-session-outcomes=51") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-cgroup-irq-pressure-full-us=52") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-profile-budget-count=14") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-preflight-policy-count=15") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-recovery-reserved-names=16") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-recovery-live-incarnations=17") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-recovery-stale-incarnations=18") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-recovery-recovered-incarnations=19") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-cgroup-recovery-empty-legacy-removed=20") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-live-session-count=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-outbound-packet-count=5") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-dropped-event-count=7") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-controller-retryable-send-rejections=8") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-controller-current-retry-streak=9") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "ratox-controller-maximum-retry-streak=10") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-controller-retry-age-us=11") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-host-retryable-send-rejections=12") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-host-current-retry-streak=13") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-host-maximum-retry-streak=14") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-host-retry-age-us=15") !=
                std::string::npos);
    IOTOX_CHECK(status.find("transport-pending-events=16") !=
                std::string::npos);
    IOTOX_CHECK(status.find("transport-maximum-pending-events=17") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-required-event-backpressure-count=19") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-required-event-backpressure-total-us=20") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-required-event-backpressure-maximum-us=21") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-paused-transfers=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-high-watermark=64") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-low-watermark=16") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-minimum-hold-us=5000") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-resume-batch-limit=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-pause-count=22") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-resume-count=20") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-resume-batch-count=11") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-resume-batch-maximum=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-external-pause-count=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-pause-failure-count=3") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-resume-failure-count=4") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-total-hold-us=123456") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-file-pacing-maximum-hold-us=9000") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-window-per-peer=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-rotation-quantum-ms=20") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-runnable-receives=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-waiting-receives=3") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-admission-count=44") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-rotation-count=33") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-pause-count=34") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-resume-count=44") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-control-failure-count=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-total-wait-us=567890") !=
                std::string::npos);
    IOTOX_CHECK(status.find("file-carrier-maximum-wait-us=45678") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-interactive-total-queue-wait-us=1234") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-interactive-queue-wait-p99-upper-bound-us=1999") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-interactive-queue-wait-p99-exact=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-interactive-queue-wait-at-or-above-2000-us=3") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-control-queue-wait-p95-upper-bound-us=8191") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-control-queue-wait-p95-exact=0") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-bulk-queue-wait-p50-upper-bound-us=41") !=
                std::string::npos);
    IOTOX_CHECK(status.find("transport-sensitive-lossless-calls=11") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-sensitive-lossless-toxcore-attempts=10") !=
                std::string::npos);
    IOTOX_CHECK(status.find("transport-sensitive-lossless-accepted=8") !=
                std::string::npos);
    IOTOX_CHECK(status.find(
                    "transport-sensitive-lossless-send-queue-full=2") !=
                std::string::npos);

    iotox::interactive::RatoxServiceEvent first;
    first.ordinal = 1U;
    first.steady_time_us = 17U;
    first.kind = iotox::interactive::RatoxServiceEventKind::opened;
    first.friend_number = 9U;
    first.online_epoch = 11U;
    first.session_id.fill(0xA5U);
    first.principal_id.fill(0x5AU);
    first.frame_type = iotox::protocol::ratox::FrameType::open;
    first.incarnation = 2U;
    first.generation = 3U;
    first.message_id = 0x1122334455667788ULL;
    first.sequence = 4U;
    first.next_sequence = 8U;
    first.event_bytes = 4U;
    first.next_input_sequence = 4U;
    first.output_base_sequence = 5U;
    first.output_next_sequence = 6U;
    IOTOX_CHECK(tree.append_ratox_event(first).ok());

    iotox::interactive::RatoxServiceEvent second = first;
    second.ordinal = 2U;
    second.kind =
        iotox::interactive::RatoxServiceEventKind::authority_revoked;
    second.error_code = iotox::ErrorCode::unavailable;
    IOTOX_CHECK(tree.append_ratox_event(second).ok());

    const std::string current = read_text(root / "ratox-events");
    const std::string previous = read_text(root / "ratox-events.previous");
    IOTOX_CHECK(current.find("ordinal=2") != std::string::npos);
    IOTOX_CHECK(current.find("kind=authority-revoked") !=
                std::string::npos);
    IOTOX_CHECK(previous.find("ordinal=1") != std::string::npos);
    IOTOX_CHECK(previous.find("steady-us=17") != std::string::npos);
    IOTOX_CHECK(previous.find("kind=opened") != std::string::npos);
    IOTOX_CHECK(current.find("friend-number=9") != std::string::npos);
    IOTOX_CHECK(current.find("online-epoch=11") != std::string::npos);
    IOTOX_CHECK(current.find("frame-type=OPEN") != std::string::npos);
    IOTOX_CHECK(previous.find("message-id=1234605616436508552") !=
                std::string::npos);
    IOTOX_CHECK(previous.find("sequence=4") != std::string::npos);
    IOTOX_CHECK(previous.find("next-sequence=8") != std::string::npos);
    IOTOX_CHECK(previous.find("event-bytes=4") != std::string::npos);
    IOTOX_CHECK(current.find("terminal-input") == std::string::npos);
    IOTOX_CHECK(current.find("terminal-output") == std::string::npos);
    IOTOX_CHECK(current.find("argv") == std::string::npos);
    IOTOX_CHECK(current.find("environment") == std::string::npos);
    IOTOX_CHECK(permission_bits(root / "ratox-events") == 0600U);

    first.ordinal = 0U;
    IOTOX_CHECK(!tree.append_ratox_event(first).ok());
    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime event journal records metadata without copying packet contents") {
    const std::filesystem::path root = runtime_test_directory("events");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportEvent event;
    event.kind = iotox::TransportEventKind::lossless_packet;
    event.friend_number = 9U;
    event.data = {'S', 'U', 'P', 'E', 'R', 'S', 'E', 'C', 'R', 'E', 'T'};
    event.message = "packet\nreceived";
    const iotox::Status appended = tree.append_event(event);
    IOTOX_CHECK_MSG(appended.ok(), appended.message());

    const std::string journal = read_text(tree.event_path());
    IOTOX_CHECK(journal.find("kind=lossless-packet") != std::string::npos);
    IOTOX_CHECK(journal.find("payload-bytes=11") != std::string::npos);
    IOTOX_CHECK(journal.find("SUPERSECRET") == std::string::npos);
    IOTOX_CHECK(journal.find("packet\\nreceived") != std::string::npos);
    IOTOX_CHECK(permission_bits(tree.event_path()) == 0600U);

    event.message.assign(3000U, 'A');
    IOTOX_CHECK(tree.append_event(event).ok());
    event.message.assign(3000U, 'B');
    IOTOX_CHECK(tree.append_event(event).ok());
    IOTOX_CHECK(std::filesystem::exists(root / "events.previous"));
    IOTOX_CHECK(read_text(root / "events.previous").find("AAAA") != std::string::npos);
    IOTOX_CHECK(read_text(root / "events").find("BBBB") != std::string::npos);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree rejects relative roots") {
    iotox::local::RuntimeTree tree({"relative/iotox", 4096U});
    const iotox::Status prepared = tree.prepare();
    IOTOX_CHECK(!prepared.ok());
    IOTOX_CHECK(prepared.code() == iotox::ErrorCode::invalid_argument);
}


IOTOX_TEST("runtime tree projects and withdraws transport peers by public key") {
    const std::filesystem::path root = runtime_test_directory("peers");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportPeer first;
    first.friend_number = 7U;
    first.public_key.fill(0x11U);
    first.connection_status = 1;
    iotox::TransportPeer second;
    second.friend_number = 9U;
    second.public_key.fill(0x22U);
    second.connection_status = 0;
    const std::array peers{first, second};
    IOTOX_CHECK(tree.publish_peers(peers).ok());

    const std::string first_key(64U, '1');
    const std::string second_key(64U, '2');
    IOTOX_CHECK(read_text(root / "peers" / first_key / "number") == "7\n");
    IOTOX_CHECK(read_text(root / "peers" / first_key / "connection") == "tcp\n");
    IOTOX_CHECK(read_text(root / "peers" / first_key / "online") == "1\n");
    IOTOX_CHECK(read_text(root / "peers" / second_key / "online") == "0\n");
    IOTOX_CHECK(permission_bits(root / "peers" / first_key) == 0700U);
    IOTOX_CHECK(permission_bits(root / "peers" / first_key / "public-key") == 0600U);

    const std::array remaining{second};
    IOTOX_CHECK(tree.publish_peers(remaining).ok());
    IOTOX_CHECK(!std::filesystem::exists(root / "peers" / first_key));
    IOTOX_CHECK(std::filesystem::exists(root / "peers" / second_key));

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime peer projection owns private command and human text FIFOs") {
    const std::filesystem::path root = runtime_test_directory("command-surface");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportPeer peer;
    peer.friend_number = 11U;
    peer.public_key.fill(0xABU);
    const std::array peers{peer};
    IOTOX_CHECK(tree.publish_peers(peers).ok());

    const std::string key = std::string(64U, 'A').replace(
        0U, 64U,
        "ABABABABABABABABABABABABABABABAB"
        "ABABABABABABABABABABABABABABABAB");
    const std::filesystem::path directory = root / "peers" / key;
    IOTOX_CHECK(path_is_fifo(directory / "command"));
    IOTOX_CHECK(permission_bits(directory / "command") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "command.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "command-events") == 0600U);
    const std::string help = read_text(directory / "command.help");
    IOTOX_CHECK(help.find("operation=device.describe") != std::string::npos);
    IOTOX_CHECK(help.find("operation=system.summary") != std::string::npos);
    IOTOX_CHECK(help.find(
                    "operation=profile.status.set available|away|busy") !=
                std::string::npos);
    IOTOX_CHECK(help.find("only an admitted durable command is authoritative") !=
                std::string::npos);
    IOTOX_CHECK(read_text(directory / "command-events").empty());
    IOTOX_CHECK(path_is_fifo(directory / "message"));
    IOTOX_CHECK(path_is_fifo(directory / "action"));
    IOTOX_CHECK(permission_bits(directory / "message") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "action") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "message.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "message-events") == 0600U);
    const std::string message_help = read_text(directory / "message.help");
    IOTOX_CHECK(message_help.find("message=normal Tox text FIFO") !=
                std::string::npos);
    IOTOX_CHECK(message_help.find("action=Tox action text FIFO") !=
                std::string::npos);
    IOTOX_CHECK(message_help.find("not a durable offline queue") !=
                std::string::npos);
    IOTOX_CHECK(message_help.find("not device authorization") !=
                std::string::npos);
    IOTOX_CHECK(message_help.find("expects valid UTF-8") !=
                std::string::npos);
    IOTOX_CHECK(message_help.find("disconnect abandons") !=
                std::string::npos);
    IOTOX_CHECK(read_text(directory / "message-events").empty());

    IOTOX_CHECK(path_is_fifo(directory / "file-send"));
    IOTOX_CHECK(path_is_fifo(directory / "file-receive"));
    IOTOX_CHECK(path_is_fifo(directory / "file-control"));
    IOTOX_CHECK(permission_bits(directory / "file-send") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-receive") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-control") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-send.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-receive.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-control.help") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "file-events") == 0600U);
    const std::string file_help = read_text(directory / "file.help");
    IOTOX_CHECK(file_help.find("FIFO names local paths; file bytes never pass") !=
                std::string::npos);
    IOTOX_CHECK(file_help.find("file-receive=<decimal file number><TAB><absolute destination path>") !=
                std::string::npos);
    IOTOX_CHECK(file_help.find("file-control=<decimal file number><TAB><pause|resume|cancel>") !=
                std::string::npos);
    IOTOX_CHECK(file_help.find("FIFO write success means only that the kernel accepted bytes") !=
                std::string::npos);
    IOTOX_CHECK(file_help.find("not an offline file queue") !=
                std::string::npos);
    IOTOX_CHECK(read_text(directory / "file-events").empty());
    IOTOX_CHECK(permission_bits(directory / "files") == 0700U);
    IOTOX_CHECK(permission_bits(directory / "files" / "incoming") == 0700U);
    IOTOX_CHECK(permission_bits(directory / "files" / "outgoing") == 0700U);
    IOTOX_CHECK(path_is_fifo(directory / "remove"));
    IOTOX_CHECK(permission_bits(directory / "remove") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "lifecycle.help") == 0600U);
    const std::string lifecycle_help = read_text(directory / "lifecycle.help");
    IOTOX_CHECK(lifecycle_help.find("write exactly remove") !=
                std::string::npos);
    IOTOX_CHECK(lifecycle_help.find("does not revoke") !=
                std::string::npos);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime message ingress journal preserves bytes message id zero and rotates") {
    const std::filesystem::path root =
        runtime_test_directory("message-ingress-events");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());
    const std::string key(64U, 'D');

    iotox::local::PeerMessageIngressEvent event;
    event.unix_ms = 5678U;
    event.ingress_sequence = 1U;
    event.kind = iotox::TextMessageKind::action;
    event.disposition = "accepted";
    event.error_code = iotox::ErrorCode::ok;
    event.has_message_id = true;
    event.message_id = 0U;
    event.body = {'w', 'a', 'v', 'e', 0U, 0xFFU, '\r'};
    event.detail = "queued\nlocally";
    IOTOX_CHECK(tree.append_peer_message_ingress(key, event).ok());

    const std::filesystem::path journal =
        root / "peers" / key / "message-events";
    const std::string first = read_text(journal);
    IOTOX_CHECK(first.find("ingress-sequence=1") != std::string::npos);
    IOTOX_CHECK(first.find("kind=action") != std::string::npos);
    IOTOX_CHECK(first.find("disposition=accepted") != std::string::npos);
    IOTOX_CHECK(first.find("message-id=0") != std::string::npos);
    IOTOX_CHECK(first.find("payload-bytes=7") != std::string::npos);
    IOTOX_CHECK(first.find("body=wave\\x00\\xFF\\r") !=
                std::string::npos);
    IOTOX_CHECK(first.find("detail=queued\\nlocally") !=
                std::string::npos);
    IOTOX_CHECK(permission_bits(journal) == 0600U);

    event.ingress_sequence = 2U;
    event.has_message_id = false;
    event.disposition = "rejected";
    event.error_code = iotox::ErrorCode::unavailable;
    event.body.assign(4000U, 'X');
    event.detail = "friend offline";
    IOTOX_CHECK(tree.append_peer_message_ingress(key, event).ok());
    IOTOX_CHECK(std::filesystem::exists(
        root / "peers" / key / "message-events.previous"));
    IOTOX_CHECK(read_text(
                    root / "peers" / key / "message-events.previous") ==
                first);
    const std::string current = read_text(journal);
    IOTOX_CHECK(current.find("ingress-sequence=2") != std::string::npos);
    IOTOX_CHECK(current.find("message-id=unassigned") != std::string::npos);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime command journal renders exact ingress evidence and rotates") {
    const std::filesystem::path root = runtime_test_directory("command-events");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());
    const std::string key(64U, 'C');

    iotox::local::PeerCommandEvent event;
    event.unix_ms = 1234U;
    event.ingress_sequence = 1U;
    event.operation = "device.describe";
    event.disposition = "admitted";
    event.error_code = iotox::ErrorCode::ok;
    event.sender_epoch = 77U;
    event.message_id = 88U;
    event.state = "send-failed";
    event.detail = "retry\\nrequired";
    IOTOX_CHECK(tree.append_peer_command_event(key, event).ok());

    const std::filesystem::path journal =
        root / "peers" / key / "command-events";
    const std::string first = read_text(journal);
    IOTOX_CHECK(first.find("ingress-sequence=1") != std::string::npos);
    IOTOX_CHECK(first.find("operation=device.describe") != std::string::npos);
    IOTOX_CHECK(first.find("disposition=admitted") != std::string::npos);
    IOTOX_CHECK(first.find("sender-epoch=77") != std::string::npos);
    IOTOX_CHECK(first.find("message-id=88") != std::string::npos);
    IOTOX_CHECK(first.find("detail=retry\\\\nrequired") != std::string::npos);
    IOTOX_CHECK(permission_bits(journal) == 0600U);

    event.ingress_sequence = 2U;
    event.detail.assign(4000U, 'X');
    IOTOX_CHECK(tree.append_peer_command_event(key, event).ok());
    IOTOX_CHECK(std::filesystem::exists(
        root / "peers" / key / "command-events.previous"));
    IOTOX_CHECK(read_text(root / "peers" / key / "command-events.previous") ==
                first);
    IOTOX_CHECK(read_text(journal).find("ingress-sequence=2") !=
                std::string::npos);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree projects incoming friend requests without path injection") {
    const std::filesystem::path root = runtime_test_directory("requests");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportEvent event;
    event.kind = iotox::TransportEventKind::friend_request;
    event.public_key.assign(32U, 0xABU);
    event.data = {'h', 'i', 0U, 'x'};
    IOTOX_CHECK(tree.publish_friend_request(event).ok());

    std::string key;
    for (std::size_t index = 0U; index < 32U; ++index) {
        key += "AB";
    }
    const std::filesystem::path directory = root / "requests" / key;
    IOTOX_CHECK(read_text(directory / "public-key") == key + "\n");
    IOTOX_CHECK(read_bytes(directory / "message") == event.data);
    IOTOX_CHECK(read_text(directory / "message-bytes") == "4\n");
    IOTOX_CHECK(permission_bits(directory) == 0700U);
    IOTOX_CHECK(permission_bits(directory / "message") == 0600U);
    IOTOX_CHECK(path_is_fifo(directory / "accept"));
    IOTOX_CHECK(path_is_fifo(directory / "reject"));
    IOTOX_CHECK(permission_bits(directory / "accept") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "reject") == 0600U);
    IOTOX_CHECK(permission_bits(directory / "request.help") == 0600U);
    const std::string help = read_text(directory / "request.help");
    IOTOX_CHECK(help.find("accept calls tox_friend_add_norequest") !=
                std::string::npos);
    IOTOX_CHECK(help.find("grants no IoTox role") != std::string::npos);

    IOTOX_CHECK(tree.remove_friend_request(event.public_key).ok());
    IOTOX_CHECK(!std::filesystem::exists(directory));

    event.public_key.assign(31U, 0U);
    IOTOX_CHECK(!tree.publish_friend_request(event).ok());
    std::filesystem::remove_all(root, ignored);
}



IOTOX_TEST("runtime tree exposes outgoing request help and explicit keyless evidence") {
    const std::filesystem::path root =
        runtime_test_directory("outgoing-request-root");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    IOTOX_CHECK(tree.prepare().ok());
    IOTOX_CHECK(path_is_fifo(root / "request"));
    IOTOX_CHECK(permission_bits(root / "request") == 0600U);
    IOTOX_CHECK(permission_bits(root / "request.help") == 0600U);
    const std::string help = read_text(root / "request.help");
    IOTOX_CHECK(help.find("76 hexadecimal Tox address") !=
                std::string::npos);
    IOTOX_CHECK(help.find("maximum-record-bytes=998") !=
                std::string::npos);
    IOTOX_CHECK(help.find("grants no IoTox role") !=
                std::string::npos);

    iotox::local::FriendLifecycleEvent keyless;
    keyless.unix_ms = 100U;
    keyless.sequence = 1U;
    keyless.source = "local-fifo";
    keyless.operation = "request-send";
    keyless.has_public_key = false;
    keyless.disposition = "rejected";
    keyless.error_code = iotox::ErrorCode::invalid_argument;
    keyless.detail = "record was shorter than one public-key prefix";
    IOTOX_CHECK(tree.append_friend_lifecycle(keyless).ok());
    const std::string evidence = read_text(root / "friend-events");
    IOTOX_CHECK(evidence.find("public-key=unknown") != std::string::npos);
    IOTOX_CHECK(evidence.find("operation=request-send") !=
                std::string::npos);

    keyless.sequence = 2U;
    keyless.public_key = std::string(64U, '0');
    IOTOX_CHECK(!tree.append_friend_lifecycle(keyless).ok());

    keyless.has_public_key = true;
    keyless.public_key.clear();
    IOTOX_CHECK(!tree.append_friend_lifecycle(keyless).ok());

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime friendship journal records bounded lifecycle evidence and rotates") {
    const std::filesystem::path root =
        runtime_test_directory("friendship-events");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree::Config config;
    config.root = root;
    config.event_rotation_bytes = 4096U;
    config.friendship_rotation_bytes = 4096U;
    iotox::local::RuntimeTree tree(config);
    IOTOX_CHECK(tree.prepare().ok());
    IOTOX_CHECK(permission_bits(root / "friend-events") == 0600U);
    IOTOX_CHECK(permission_bits(root / "friendship.help") == 0600U);

    iotox::local::FriendLifecycleEvent event;
    event.unix_ms = 1234U;
    event.sequence = 1U;
    event.source = "local-fifo";
    event.operation = "request-accept";
    event.public_key = std::string(64U, 'A');
    event.disposition = "accepted";
    event.error_code = iotox::ErrorCode::ok;
    event.has_friend_number = true;
    event.friend_number = 7U;
    event.detail = "transport friendship only; authority unchanged";
    IOTOX_CHECK(tree.append_friend_lifecycle(event).ok());

    const std::string first = read_text(root / "friend-events");
    IOTOX_CHECK(first.find("source=local-fifo") != std::string::npos);
    IOTOX_CHECK(first.find("operation=request-accept") != std::string::npos);
    IOTOX_CHECK(first.find("friend-number=7") != std::string::npos);
    IOTOX_CHECK(first.find("authority unchanged") != std::string::npos);

    event.sequence = 2U;
    event.detail.assign(5000U, 'X');
    IOTOX_CHECK(tree.append_friend_lifecycle(event).ok());
    IOTOX_CHECK(std::filesystem::exists(root / "friend-events.previous"));
    IOTOX_CHECK(read_text(root / "friend-events.previous") == first);
    IOTOX_CHECK(!tree.append_friend_lifecycle(
        iotox::local::FriendLifecycleEvent{}).ok());

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree transactionally projects and withdraws live file transfers") {
    const std::filesystem::path root = runtime_test_directory("transfers");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::FileTransferRecord transfer;
    transfer.direction = iotox::FileTransferDirection::incoming;
    transfer.state = iotox::FileTransferState::offered;
    transfer.friend_number = 3U;
    transfer.file_number = 1U << 16U;
    transfer.file_kind = iotox::toxcore::abi::kFileKindData;
    transfer.file_size = 17U;
    transfer.position = 0U;
    transfer.file_id.fill(0x5AU);
    transfer.has_file_id = true;
    transfer.filename = {'b', 'i', 'n', 0U, '.', 'd', 'a', 't'};
    transfer.local_path = "/tmp/target\nname";
    transfer.detail = "paused\nfor-owner";

    const std::array transfers{transfer};
    IOTOX_CHECK(tree.publish_transfers(transfers).ok());
    const std::filesystem::path directory =
        root / "transfers" / "incoming-3-65536";
    IOTOX_CHECK(read_text(directory / "direction") == "incoming\n");
    IOTOX_CHECK(read_text(directory / "state") == "offered\n");
    IOTOX_CHECK(read_text(directory / "friend-number") == "3\n");
    IOTOX_CHECK(read_text(directory / "file-number") == "65536\n");
    IOTOX_CHECK(read_text(directory / "size") == "17\n");
    IOTOX_CHECK(read_text(directory / "position") == "0\n");
    IOTOX_CHECK(read_text(directory / "filename-bytes") == "8\n");
    IOTOX_CHECK(read_bytes(directory / "filename") == transfer.filename);
    IOTOX_CHECK(read_text(directory / "local-path") == "/tmp/target\\nname\n");
    IOTOX_CHECK(read_text(directory / "detail") == "paused\\nfor-owner\n");
    IOTOX_CHECK(read_text(directory / "file-id") ==
                std::string("5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A") +
                    "5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A\n");
    IOTOX_CHECK(permission_bits(directory) == 0700U);
    IOTOX_CHECK(permission_bits(directory / "filename") == 0600U);

    const ino_t unchanged_inode = inode_number(directory);
    IOTOX_CHECK(tree.publish_transfers(transfers).ok());
    IOTOX_CHECK(inode_number(directory) == unchanged_inode);
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(tree.publish_transfers(transfers).ok());
    IOTOX_CHECK(read_text(directory / "position") == "0\n");

    for (const auto &entry : std::filesystem::directory_iterator(root / "transfers")) {
        IOTOX_CHECK(entry.path().filename().string().find(".transfer-") != 0U);
    }

    IOTOX_CHECK(tree.publish_transfers({}).ok());
    IOTOX_CHECK(!std::filesystem::exists(directory));
    IOTOX_CHECK(std::filesystem::is_empty(root / "transfers"));

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree projects per-peer finite files and journals local plus toxcore truth") {
    const std::filesystem::path root = runtime_test_directory("peer-file-surface");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportPeer peer;
    peer.friend_number = 3U;
    peer.public_key.fill(0xA7U);
    const std::array peers{peer};
    IOTOX_CHECK(tree.publish_peers(peers).ok());
    const std::string key =
        "A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7"
        "A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7";

    iotox::FileTransferRecord incoming;
    incoming.direction = iotox::FileTransferDirection::incoming;
    incoming.state = iotox::FileTransferState::offered;
    incoming.friend_number = 3U;
    incoming.file_number = 65541U;
    incoming.file_kind = iotox::toxcore::abi::kFileKindData;
    incoming.file_size = 17U;
    incoming.local_paused = true;
    incoming.file_id.fill(0x33U);
    incoming.has_file_id = true;
    incoming.filename = {'i', 'n', '.', 'b', 'i', 'n'};
    incoming.local_path = "/tmp/incoming.bin";
    incoming.detail = "paused until destination admission";

    iotox::FileTransferRecord outgoing;
    outgoing.direction = iotox::FileTransferDirection::outgoing;
    outgoing.state = iotox::FileTransferState::active;
    outgoing.friend_number = 3U;
    outgoing.file_number = 8U;
    outgoing.file_kind = iotox::toxcore::abi::kFileKindData;
    outgoing.file_size = 23U;
    outgoing.position = 7U;
    outgoing.peer_paused = true;
    outgoing.state = iotox::FileTransferState::paused;
    outgoing.filename = {'o', 'u', 't', '.', 'b', 'i', 'n'};
    outgoing.local_path = "/tmp/outgoing.bin";
    outgoing.detail = "serving exact requested chunks";

    const std::array transfers{incoming, outgoing};
    IOTOX_CHECK(tree.publish_peer_transfers(key, transfers).ok());
    const std::filesystem::path peer_root = root / "peers" / key;
    const std::filesystem::path incoming_root =
        peer_root / "files" / "incoming" / "65541";
    const std::filesystem::path outgoing_root =
        peer_root / "files" / "outgoing" / "8";
    IOTOX_CHECK(read_text(incoming_root / "direction") == "incoming\n");
    IOTOX_CHECK(read_text(incoming_root / "state") == "offered\n");
    IOTOX_CHECK(read_text(incoming_root / "size") == "17\n");
    IOTOX_CHECK(read_text(incoming_root / "local-paused") == "1\n");
    IOTOX_CHECK(read_text(incoming_root / "peer-paused") == "0\n");
    IOTOX_CHECK(read_bytes(incoming_root / "filename") == incoming.filename);
    IOTOX_CHECK(read_text(outgoing_root / "direction") == "outgoing\n");
    IOTOX_CHECK(read_text(outgoing_root / "position") == "7\n");
    IOTOX_CHECK(read_text(outgoing_root / "state") == "paused\n");
    IOTOX_CHECK(read_text(outgoing_root / "local-paused") == "0\n");
    IOTOX_CHECK(read_text(outgoing_root / "peer-paused") == "1\n");
    IOTOX_CHECK(permission_bits(incoming_root) == 0700U);
    IOTOX_CHECK(permission_bits(outgoing_root / "local-path") == 0600U);

    const ino_t unchanged_outgoing_inode = inode_number(outgoing_root);
    IOTOX_CHECK(tree.publish_peer_transfers(key, transfers).ok());
    IOTOX_CHECK(inode_number(outgoing_root) == unchanged_outgoing_inode);
    std::filesystem::remove_all(outgoing_root, ignored);
    IOTOX_CHECK(tree.publish_peer_transfers(key, transfers).ok());
    IOTOX_CHECK(read_text(outgoing_root / "position") == "7\n");

    iotox::local::PeerFileIngressEvent ingress;
    ingress.unix_ms = 4100U;
    ingress.ingress_sequence = 9U;
    ingress.operation = "file-receive";
    ingress.disposition = "accepted";
    ingress.error_code = iotox::ErrorCode::ok;
    ingress.has_transfer = true;
    ingress.transfer = incoming;
    ingress.has_file_number = true;
    ingress.file_number = incoming.file_number;
    ingress.local_path = "/tmp/target\nname";
    ingress.detail = "private temporary file acquired; resume accepted";
    IOTOX_CHECK(tree.append_peer_file_ingress(key, ingress).ok());

    iotox::TransportEvent transport;
    transport.kind = iotox::TransportEventKind::file_chunk;
    transport.friend_number = 3U;
    transport.file_number = incoming.file_number;
    transport.file_position = 0U;
    transport.data = {'D', 'A', 'T', 'A'};
    transport.message = "incoming chunk accepted";
    iotox::local::PeerFileTransportEvent progress;
    progress.unix_ms = 4200U;
    progress.event = transport;
    progress.manager_status = iotox::Status::success();
    progress.has_transfer = true;
    progress.transfer = incoming;
    progress.transfer.state = iotox::FileTransferState::active;
    progress.transfer.position = 4U;
    IOTOX_CHECK(tree.append_peer_file_transport(key, progress).ok());

    const std::string journal = read_text(peer_root / "file-events");
    IOTOX_CHECK(journal.find("source=local-fifo") != std::string::npos);
    IOTOX_CHECK(journal.find("operation=file-receive") != std::string::npos);
    IOTOX_CHECK(journal.find("disposition=accepted") != std::string::npos);
    IOTOX_CHECK(journal.find("file-number=65541") != std::string::npos);
    IOTOX_CHECK(journal.find("local-path=/tmp/target\\nname") !=
                std::string::npos);
    IOTOX_CHECK(journal.find("source=toxcore") != std::string::npos);
    IOTOX_CHECK(journal.find("event=file-chunk") != std::string::npos);
    IOTOX_CHECK(journal.find("payload-bytes=4") != std::string::npos);
    IOTOX_CHECK(journal.find("DATA") == std::string::npos);

    IOTOX_CHECK(tree.publish_peer_transfers(key, {}).ok());
    IOTOX_CHECK(std::filesystem::is_empty(peer_root / "files" / "incoming"));
    IOTOX_CHECK(std::filesystem::is_empty(peer_root / "files" / "outgoing"));
    IOTOX_CHECK(!tree.publish_peer_transfers("bad-key", transfers).ok());

    ingress.ingress_sequence = 10U;
    ingress.detail.assign(5000U, 'X');
    IOTOX_CHECK(tree.append_peer_file_ingress(key, ingress).ok());
    IOTOX_CHECK(std::filesystem::exists(peer_root / "file-events.previous"));

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree projects Tox profile presence and byte-preserving peer journals") {
    const std::filesystem::path root = runtime_test_directory("profile-messages");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::local::RuntimeSnapshot snapshot;
    snapshot.phase = "running";
    snapshot.profile.name = {'I', 'o', 0U, 'T', 'o', 'x'};
    snapshot.profile.status_message = {'j', 'u', 's', 't', '\n', 'w', 'e', 'r', 'x'};
    snapshot.profile.status = iotox::PresenceStatus::busy;
    IOTOX_CHECK(tree.publish(snapshot).ok());
    IOTOX_CHECK(read_bytes(root / "self" / "name") == snapshot.profile.name);
    IOTOX_CHECK(read_text(root / "self" / "name-bytes") == "6\n");
    IOTOX_CHECK(read_bytes(root / "self" / "status-message") ==
                snapshot.profile.status_message);
    IOTOX_CHECK(read_text(root / "self" / "status") == "busy\n");
    IOTOX_CHECK(read_text(root / "status").find("self-name-bytes=6") !=
                std::string::npos);

    iotox::TransportPeer peer;
    peer.friend_number = 3U;
    peer.public_key.fill(0xABU);
    peer.connection_status = 2;
    peer.name = {'p', 'e', 'e', 'r', 0U, '3'};
    peer.status_message = {'r', 'e', 'a', 'd', 'y'};
    peer.status = iotox::PresenceStatus::away;
    peer.typing = true;
    const std::array peers{peer};
    IOTOX_CHECK(tree.publish_peers(peers).ok());

    std::string key;
    for (std::size_t index = 0U; index < 32U; ++index) {
        key += "AB";
    }
    IOTOX_CHECK(read_bytes(root / "peers" / key / "name") == peer.name);
    IOTOX_CHECK(read_text(root / "peers" / key / "name-bytes") == "6\n");
    IOTOX_CHECK(read_text(root / "peers" / key / "status") == "away\n");
    IOTOX_CHECK(read_text(root / "peers" / key / "typing") == "1\n");

    iotox::TransportEvent message;
    message.kind = iotox::TransportEventKind::message_sent;
    message.friend_number = peer.friend_number;
    message.text_kind = iotox::TextMessageKind::action;
    message.message_id = 17U;
    message.data = {'h', 'i', 0U, '\n', 'x'};
    message.message = "accepted\nby toxcore";
    IOTOX_CHECK(tree.append_peer_message(key, message).ok());

    const std::string journal = read_text(root / "peers" / key / "messages");
    IOTOX_CHECK(journal.find("direction=outgoing") != std::string::npos);
    IOTOX_CHECK(journal.find("kind=action") != std::string::npos);
    IOTOX_CHECK(journal.find("message-id=17") != std::string::npos);
    IOTOX_CHECK(journal.find("payload-bytes=5") != std::string::npos);
    IOTOX_CHECK(journal.find("body=hi\\x00\\nx") != std::string::npos);
    IOTOX_CHECK(journal.find("note=accepted\\nby toxcore") != std::string::npos);
    IOTOX_CHECK(permission_bits(root / "peers" / key / "messages") == 0600U);

    iotox::protocol::Frame hello;
    hello.type = iotox::protocol::MessageType::hello;
    hello.message_id = 42U;
    hello.payload = {'j', 'u', 's', 't', 0U, 'w', 'e', 'r', 'x'};
    IOTOX_CHECK(tree.append_peer_protocol(key, "outgoing", hello).ok());
    IOTOX_CHECK(tree.append_peer_protocol(key, "incoming", hello).ok());
    const std::string protocol_journal =
        read_text(root / "peers" / key / "protocol");
    IOTOX_CHECK(protocol_journal.find(
                    "direction=outgoing protocol=1.0 type=hello") !=
                std::string::npos);
    IOTOX_CHECK(protocol_journal.find(
                    "direction=incoming protocol=1.0 type=hello") !=
                std::string::npos);
    IOTOX_CHECK(protocol_journal.find("message-id=42") != std::string::npos);
    IOTOX_CHECK(protocol_journal.find("payload=just\\x00werx") !=
                std::string::npos);
    IOTOX_CHECK(permission_bits(root / "peers" / key / "protocol") == 0600U);

    message.kind = iotox::TransportEventKind::friend_read_receipt;
    message.data.clear();
    message.message.assign(5000U, 'R');
    IOTOX_CHECK(tree.append_peer_message(key, message).ok());
    IOTOX_CHECK(std::filesystem::exists(
        root / "peers" / key / "messages.previous"));

    hello.payload.assign(5000U, 'P');
    IOTOX_CHECK(tree.append_peer_protocol(key, "outgoing", hello).ok());
    IOTOX_CHECK(std::filesystem::exists(
        root / "peers" / key / "protocol.previous"));

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree publishes transcript-confirmed session without implying authority") {
    const std::filesystem::path root = runtime_test_directory("session-projection");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    iotox::TransportPeer peer;
    peer.friend_number = 4U;
    peer.public_key.fill(0x42U);
    peer.connection_status = 1;
    const std::array peers{peer};
    IOTOX_CHECK(tree.publish_peers(peers).ok());

    std::string key;
    for (std::size_t index = 0U; index < peer.public_key.size(); ++index) {
        key += "42";
    }

    iotox::protocol::SessionNonce local_nonce{};
    iotox::protocol::SessionNonce peer_nonce{};
    local_nonce.fill(0x11U);
    peer_nonce.fill(0x22U);

    iotox::protocol::PeerSessionSnapshot session;
    session.friend_number = peer.friend_number;
    session.public_key = key;
    session.state = iotox::protocol::PeerSessionState::confirmed;
    session.connected = true;
    session.connection_status = 1;
    session.online_epoch = 3U;
    session.hello_sent = true;
    session.hello_received = true;
    session.confirmation_sent = true;
    session.confirmation_received = true;
    session.application_ready = true;
    session.local_role_known = true;
    session.local_role = iotox::protocol::SessionRole::lower_transport_key;
    session.local_hello_message_id = 41U;
    session.peer_hello_message_id = 42U;
    session.local_confirmation_message_id = 43U;
    session.peer_confirmation_message_id = 44U;
    session.local = iotox::protocol::make_local_hello(4096U, local_nonce);
    session.peer = iotox::protocol::make_local_hello(2048U, peer_nonce);
    session.negotiated =
        iotox::protocol::negotiate_protocol(session.local, session.peer);
    session.detail = "both canonical confirmations accepted";

    IOTOX_CHECK(tree.publish_peer_session(key, session).ok());
    const std::filesystem::path peer_root = root / "peers" / key;
    const std::string committed = read_text(peer_root / "session");
    IOTOX_CHECK(committed.find("state=confirmed") != std::string::npos);
    IOTOX_CHECK(committed.find("application-ready=1") != std::string::npos);
    IOTOX_CHECK(committed.find("authorization=separate-authority-session") !=
                std::string::npos);
    IOTOX_CHECK(read_text(peer_root / "iotox" / "hello-compatible") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "transcript-confirmed") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "established") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "application-ready") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "confirmation-sent") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "confirmation-received") == "1\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "local-role") ==
                "lower-transport-key\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "protocol") == "1.0\n");
    IOTOX_CHECK(read_text(peer_root / "iotox" / "max-finite-file-bytes") ==
                "2048\n");
    IOTOX_CHECK(permission_bits(peer_root / "session") == 0600U);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree commits a bound peer device description") {
    const std::filesystem::path root = runtime_test_directory("peer-description");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    iotox::local::RuntimeTree tree({root, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    std::string key;
    for (std::size_t index = 0U; index < 32U; ++index) {
        key += "A5";
    }
    iotox::protocol::DeviceDescription device;
    device.revision_number = 10U;
    device.version_major = 0U;
    device.version_minor = 10U;
    device.version_patch = 0U;
    device.protocol = {1U, 0U};
    device.device_principal.fill(0x6BU);
    device.supported_features = iotox::protocol::kImplementedFeatureMask;
    device.offered_operations = iotox::protocol::kDeviceDescribeOperationBit;

    iotox::protocol::PeerDescriptionSnapshot description;
    description.friend_number = 7U;
    description.online_epoch = 3U;
    description.state = iotox::protocol::PeerDescriptionState::succeeded;
    description.request_message_id = 101U;
    description.result_message_id = 102U;
    description.outcome = iotox::protocol::CommandOutcome::succeeded;
    description.description = device;
    description.send_attempts = 2U;
    description.detail = "bound to authority challenge principal";
    description.updated_unix_ms = 123456U;

    IOTOX_CHECK(tree.publish_peer_description(key, description).ok());
    const std::filesystem::path peer = root / "peers" / key;
    const std::filesystem::path fields = peer / "iotox" / "description";
    IOTOX_CHECK(read_text(fields / "state") == "succeeded\n");
    IOTOX_CHECK(read_text(fields / "online-epoch") == "3\n");
    IOTOX_CHECK(read_text(fields / "send-attempts") == "2\n");
    IOTOX_CHECK(read_text(fields / "version") == "0.10.0\n");
    IOTOX_CHECK(read_text(fields / "revision") == "rev0010\n");
    IOTOX_CHECK(read_text(fields / "protocol") == "1.0\n");
    IOTOX_CHECK(read_text(fields / "device-principal") ==
                std::string(64U, '0').replace(0U, 64U,
                    "6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B"
                    "6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B") + "\n");
    IOTOX_CHECK(read_text(peer / "description").find("state=succeeded") !=
                std::string::npos);
    IOTOX_CHECK(permission_bits(peer / "description") == 0600U);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("runtime tree projects exact durable command frames behind a generation marker") {
    using namespace iotox;
    const std::filesystem::path root = runtime_test_directory("durable-commands");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);

    local::RuntimeTree tree({root, 4096U, 4096U, 4096U});
    IOTOX_CHECK(tree.prepare().ok());

    auto request_payload = protocol::encode_command_request(
        protocol::CommandRequest{protocol::CommandOperation::device_describe});
    IOTOX_CHECK(request_payload.ok());
    protocol::Frame request;
    request.type = protocol::MessageType::command;
    request.message_id = 23U;
    request.sequence = 17U;
    request.payload.assign(
        request_payload.value().begin(), request_payload.value().end());
    auto canonical_request = protocol::encode(request);
    IOTOX_CHECK(canonical_request.ok());

    auto receipt_payload = protocol::encode_command_receipt(
        protocol::CommandReceipt{protocol::CommandReceiptStage::received});
    IOTOX_CHECK(receipt_payload.ok());
    protocol::Frame receipt;
    receipt.type = protocol::MessageType::acknowledgement;
    receipt.message_id = 24U;
    receipt.correlation_id = request.message_id;
    receipt.sequence = request.sequence;
    receipt.payload.assign(
        receipt_payload.value().begin(), receipt_payload.value().end());
    auto canonical_receipt = protocol::encode(receipt);
    IOTOX_CHECK(canonical_receipt.ok());

    protocol::CommandResultPayload result_payload;
    result_payload.operation = protocol::CommandOperation::device_describe;
    result_payload.outcome = protocol::CommandOutcome::denied;
    auto encoded_result_payload = protocol::encode_command_result(result_payload);
    IOTOX_CHECK(encoded_result_payload.ok());
    protocol::Frame result;
    result.type = protocol::MessageType::command_result;
    result.message_id = 25U;
    result.correlation_id = request.message_id;
    result.sequence = request.sequence;
    result.payload = encoded_result_payload.value();
    auto canonical_result = protocol::encode(result);
    IOTOX_CHECK(canonical_result.ok());

    DurableCommandRecord record;
    record.key.direction = CommandDirection::outgoing;
    record.key.peer_public_key.fill(0x11U);
    record.key.sender_epoch = request.sequence;
    record.key.message_id = request.message_id;
    record.direction = CommandDirection::outgoing;
    record.lifecycle = CommandLifecycle::failed;
    record.operation = protocol::CommandOperation::device_describe;
    record.outcome = protocol::CommandOutcome::denied;
    record.receipt_delivery = CommandDeliveryState::observed;
    record.result_delivery = CommandDeliveryState::observed;
    record.result_message_id = result.message_id;
    record.correlation_id = request.message_id;
    record.created_unix_ms = 1000U;
    record.updated_unix_ms = 1001U;
    record.canonical_request = canonical_request.value();
    record.canonical_receipt = canonical_receipt.value();
    record.canonical_result = canonical_result.value();

    DurableCommandSnapshot snapshot;
    snapshot.generation = 2U;
    snapshot.local_sender_epoch = 99U;
    snapshot.records.push_back(record);
    IOTOX_CHECK_MSG(tree.publish_commands(snapshot).ok(),
                    "durable command projection must commit");

    const std::string peer(64U, '1');
    const std::filesystem::path projected =
        root / "commands" / "outgoing" / peer / "17-23";
    IOTOX_CHECK(read_text(root / "commands" / "summary").find(
        "format=IoTox-Durable-Commands-v3") != std::string::npos);
    IOTOX_CHECK(read_text(root / "commands" / "summary").find(
                    "generation=2") != std::string::npos);
    IOTOX_CHECK(read_text(projected / "direction") == "outgoing\n");
    IOTOX_CHECK(read_text(projected / "lifecycle") == "failed\n");
    IOTOX_CHECK(read_text(projected / "operation") == "device.describe\n");
    IOTOX_CHECK(read_text(projected / "receipt-delivery") == "observed\n");
    IOTOX_CHECK(read_bytes(projected / "request.frame") == canonical_request.value());
    IOTOX_CHECK(read_bytes(projected / "receipt.frame") == canonical_receipt.value());
    IOTOX_CHECK(read_bytes(projected / "result.frame") == canonical_result.value());
    IOTOX_CHECK(permission_bits(projected / "request.frame") == 0600U);

    DurableCommandSnapshot empty;
    empty.generation = 3U;
    empty.local_sender_epoch = 99U;
    IOTOX_CHECK(tree.publish_commands(empty).ok());
    IOTOX_CHECK(!std::filesystem::exists(projected));
    IOTOX_CHECK(read_text(root / "commands" / "summary").find(
                    "generation=3") != std::string::npos);

    std::filesystem::remove_all(root, ignored);
}
