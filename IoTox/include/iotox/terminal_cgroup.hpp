#pragma once

#include "iotox/status.hpp"
#include "iotox/terminal_profile.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <sys/types.h>
#include <vector>

namespace iotox::terminal {

namespace detail {

struct CgroupEvents {
    bool populated{false};
    std::optional<bool> frozen;

    [[nodiscard]] bool operator==(const CgroupEvents &) const = default;
};

// Parse the kernel's flat-keyed cgroup.events record. Unknown future fields
// are accepted only when they retain the documented key/value grammar;
// populated remains mandatory and unique.
[[nodiscard]] Result<CgroupEvents> parse_cgroup_events(
    std::string_view record);

// A delegated session cgroup names the exact daemon incarnation that created
// it. Boot identity prevents cross-boot PID aliasing; /proc starttime prevents
// same-boot PID reuse from turning orphan cleanup into a numeric-PID guess.
struct CgroupOwnerIdentity {
    std::array<std::uint8_t, 16U> boot_id{};
    std::uint64_t process_id{0U};
    std::uint64_t start_time_ticks{0U};

    [[nodiscard]] bool operator==(const CgroupOwnerIdentity &) const = default;
};

struct SessionCgroupName {
    CgroupOwnerIdentity owner;
    std::uint64_t sequence{0U};

    [[nodiscard]] bool operator==(const SessionCgroupName &) const = default;
};

struct CgroupRecoveryConfig {
    std::size_t maximum_candidates{64U};
    std::chrono::milliseconds maximum_wait{5000};
};

struct CgroupRecoveryReport {
    std::size_t reserved_names{0U};
    std::size_t live_incarnations{0U};
    std::size_t stale_incarnations{0U};
    std::size_t recovered_incarnations{0U};
    std::size_t empty_legacy_removed{0U};

    [[nodiscard]] bool operator==(const CgroupRecoveryReport &) const = default;
};

// Cumulative Pressure Stall Information (PSI) for one resource. The kernel
// reports absolute totals in microseconds. Older CPU PSI interfaces may omit
// the `full` line; preserving that absence prevents a zero value from being
// mistaken for positive support.
struct CgroupPressure {
    std::uint64_t some_total_microseconds{0U};
    std::optional<std::uint64_t> full_total_microseconds;

    [[nodiscard]] bool operator==(const CgroupPressure &) const = default;
};

// Exact semantic representation of one PSI class. Percentage averages are
// retained as integer basis points so admission decisions never depend on
// locale, binary floating point, or textual round trips.
struct CgroupPressureClassSample {
    std::uint16_t average_10_basis_points{0U};
    std::uint16_t average_60_basis_points{0U};
    std::uint16_t average_300_basis_points{0U};
    std::uint64_t total_microseconds{0U};

    [[nodiscard]] bool operator==(
        const CgroupPressureClassSample &) const = default;
};

struct CgroupPressureSample {
    std::optional<CgroupPressureClassSample> some;
    std::optional<CgroupPressureClassSample> full;

    [[nodiscard]] bool operator==(const CgroupPressureSample &) const = default;
};

struct CgroupPressureAdmissionObservation {
    std::optional<std::uint16_t> cpu_some_average_10_basis_points;
    std::optional<std::uint16_t> memory_full_average_10_basis_points;
    std::optional<std::uint16_t> io_full_average_10_basis_points;

    [[nodiscard]] bool operator==(
        const CgroupPressureAdmissionObservation &) const = default;
};

struct CgroupPressureAdmissionDecision {
    bool admitted{true};
    bool closed{false};
    bool closed_transition{false};
    bool reopened_transition{false};

    [[nodiscard]] bool operator==(
        const CgroupPressureAdmissionDecision &) const = default;
};

// Stable cumulative work counters from memory.stat. Reclaim and swap tuples
// are optional capabilities because older kernels or configurations may omit
// them; partial tuples are rejected instead of being silently zero-filled.
struct CgroupMemoryReclaimStat {
    std::uint64_t pages_scanned{0U};
    std::uint64_t pages_reclaimed{0U};

    [[nodiscard]] bool operator==(const CgroupMemoryReclaimStat &) const =
        default;
};

struct CgroupMemorySwapStat {
    std::uint64_t pages_in{0U};
    std::uint64_t pages_out{0U};

    [[nodiscard]] bool operator==(const CgroupMemorySwapStat &) const =
        default;
};

struct CgroupMemoryStat {
    std::uint64_t page_faults{0U};
    std::uint64_t major_page_faults{0U};
    std::optional<CgroupMemoryReclaimStat> reclaim;
    std::optional<CgroupMemorySwapStat> swap;

    [[nodiscard]] bool operator==(const CgroupMemoryStat &) const = default;
};

struct CgroupMemorySwapEvents {
    std::uint64_t high{0U};
    std::uint64_t maximum{0U};
    std::uint64_t fail{0U};

    [[nodiscard]] bool operator==(const CgroupMemorySwapEvents &) const =
        default;
};

struct CgroupLocalStat {
    std::uint64_t frozen_microseconds{0U};

    [[nodiscard]] bool operator==(const CgroupLocalStat &) const = default;
};

// IRQ/SOFTIRQ PSI exposes only the FULL pressure class in current kernels.
// Keep a dedicated semantic type so absence remains distinguishable from a
// supported interface that observed zero stall time.
struct CgroupIrqPressure {
    std::uint64_t full_total_microseconds{0U};

    [[nodiscard]] bool operator==(const CgroupIrqPressure &) const = default;
};

// Content-free kernel evidence attributed to one exact session cgroup. The
// counters are read only after recursive populated=0 and before the pinned leaf
// is removed, so no command, terminal, or peer content is retained.
struct CgroupSessionOutcome {
    bool telemetry_complete{true};
    // Any protected kernel-record read or parse failure makes the observation
    // incomplete. Incomplete outcomes contribute no partial counter values, so
    // the aggregate never mixes trusted totals with an unproved subset.
    std::uint64_t pids_limit_hits{0U};
    std::uint64_t memory_high_events{0U};
    std::uint64_t memory_max_events{0U};
    std::uint64_t memory_oom_events{0U};
    std::uint64_t memory_oom_kills{0U};
    std::uint64_t memory_oom_group_kills{0U};
    // Peak files are optional controller capabilities. A present value is the
    // exact lifetime high-water mark observed through a descriptor pinned
    // before the first payload task entered the leaf.
    std::optional<std::uint64_t> pids_peak;
    std::optional<std::uint64_t> memory_peak_bytes;
    std::optional<std::uint64_t> memory_swap_peak_bytes;
    std::optional<CgroupMemoryStat> memory_stat;
    std::optional<CgroupMemorySwapEvents> memory_swap_events;
    std::optional<CgroupLocalStat> local_stat;
    // cpu.stat exists independently of a configured quota on modern cgroup-v2
    // kernels. Capability flags keep absent optional tuples distinguishable
    // from legitimate zero work, throttling, or burst activity.
    bool cpu_stat_observed{false};
    bool cpu_bandwidth_stat_observed{false};
    bool cpu_burst_stat_observed{false};
    std::uint64_t cpu_usage_microseconds{0U};
    std::uint64_t cpu_user_microseconds{0U};
    std::uint64_t cpu_system_microseconds{0U};
    std::uint64_t cpu_periods{0U};
    std::uint64_t cpu_throttled_periods{0U};
    std::uint64_t cpu_throttled_microseconds{0U};
    std::uint64_t cpu_burst_periods{0U};
    std::uint64_t cpu_burst_microseconds{0U};
    std::uint64_t io_read_bytes{0U};
    std::uint64_t io_write_bytes{0U};
    std::uint64_t io_read_operations{0U};
    std::uint64_t io_write_operations{0U};
    std::uint64_t io_discard_bytes{0U};
    std::uint64_t io_discard_operations{0U};
    // PSI files are optional kernel capabilities. A present value means the
    // protected file existed, parsed completely, and began at zero in the
    // freshly created leaf. Missing values are retained as unavailable rather
    // than converted into fabricated zero-pressure evidence.
    std::optional<CgroupPressure> cpu_pressure;
    std::optional<CgroupPressure> memory_pressure;
    std::optional<CgroupPressure> io_pressure;
    std::optional<CgroupIrqPressure> irq_pressure;

    [[nodiscard]] bool operator==(const CgroupSessionOutcome &) const = default;
};

struct CgroupPidsEvents {
    std::uint64_t maximum_hits{0U};

    [[nodiscard]] bool operator==(const CgroupPidsEvents &) const = default;
};

struct CgroupMemoryEvents {
    std::uint64_t high{0U};
    std::uint64_t maximum{0U};
    std::uint64_t oom{0U};
    std::uint64_t oom_kill{0U};
    std::uint64_t oom_group_kill{0U};

    [[nodiscard]] bool operator==(const CgroupMemoryEvents &) const = default;
};

struct CgroupCpuBurstStat {
    std::uint64_t periods{0U};
    std::uint64_t microseconds{0U};

    [[nodiscard]] bool operator==(const CgroupCpuBurstStat &) const = default;
};

struct CgroupCpuBandwidthStat {
    std::uint64_t periods{0U};
    std::uint64_t throttled_periods{0U};
    std::uint64_t throttled_microseconds{0U};
    std::optional<CgroupCpuBurstStat> burst;

    [[nodiscard]] bool operator==(const CgroupCpuBandwidthStat &) const = default;
};

struct CgroupCpuStat {
    std::uint64_t usage_microseconds{0U};
    std::uint64_t user_microseconds{0U};
    std::uint64_t system_microseconds{0U};
    std::optional<CgroupCpuBandwidthStat> bandwidth;

    [[nodiscard]] bool operator==(const CgroupCpuStat &) const = default;
};

// Saturated totals across all device lines in one cgroup-v2 io.stat record.
// The parser accepts documented future numeric fields while requiring the
// four stable read/write counters on every nonempty device line.
struct CgroupIoStat {
    std::uint64_t read_bytes{0U};
    std::uint64_t write_bytes{0U};
    std::uint64_t read_operations{0U};
    std::uint64_t write_operations{0U};
    std::uint64_t discard_bytes{0U};
    std::uint64_t discard_operations{0U};

    [[nodiscard]] bool operator==(const CgroupIoStat &) const = default;
};

// Semantic form of one cgroup-v2 io.max device line. `std::nullopt`
// represents the kernel's `max` token. Device lines and nested keys are not
// ordered by the kernel, so callers compare these values rather than bytes.
struct CgroupIoMax {
    CgroupIoDevice device{};
    std::optional<std::uint64_t> read_bytes_per_second;
    std::optional<std::uint64_t> write_bytes_per_second;
    std::optional<std::uint64_t> read_operations_per_second;
    std::optional<std::uint64_t> write_operations_per_second;

    [[nodiscard]] bool operator==(const CgroupIoMax &) const = default;
};

[[nodiscard]] Result<CgroupPidsEvents> parse_cgroup_pids_events(
    std::string_view record);
[[nodiscard]] Result<CgroupMemoryEvents> parse_cgroup_memory_events(
    std::string_view record);
[[nodiscard]] Result<CgroupMemoryStat> parse_cgroup_memory_stat(
    std::string_view record);
[[nodiscard]] Result<CgroupMemorySwapEvents> parse_cgroup_memory_swap_events(
    std::string_view record);
[[nodiscard]] Result<CgroupLocalStat> parse_cgroup_local_stat(
    std::string_view record);
[[nodiscard]] Result<CgroupCpuStat> parse_cgroup_cpu_stat(
    std::string_view record);
[[nodiscard]] Result<std::uint64_t> parse_cgroup_peak(
    std::string_view record);
[[nodiscard]] Result<CgroupPressure> parse_cgroup_pressure(
    std::string_view record);
[[nodiscard]] Result<CgroupPressureSample> parse_cgroup_pressure_sample(
    std::string_view record);

// Canonical binary PSI trigger classes. IoTox intentionally encodes only the
// portable unprivileged ABI: a 2-second window quantum avoids silently
// depending on CAP_SYS_RESOURCE and avoids requesting a kernel realtime poll
// worker. The returned record includes the terminating NUL required by the
// documented Linux userspace contract and never includes a newline.
enum class CgroupPressureTriggerClass : std::uint8_t {
    some = 1U,
    full = 2U,
};

[[nodiscard]] Result<std::string> encode_cgroup_pressure_trigger(
    CgroupPressureTriggerClass pressure_class,
    std::uint64_t stall_microseconds,
    std::uint64_t window_microseconds);

// Pure classification of one poll(2) readiness mask used by the continuous
// PSI monitor. Keeping the kernel bit grammar independently testable prevents
// an unknown readiness class or a dead descriptor from being mistaken for a
// valid trigger or a clean shutdown.
enum class CgroupPressureMonitorDescriptorRole : std::uint8_t {
    stop = 1U,
    trigger = 2U,
};

struct CgroupPressureMonitorPollDecision {
    bool stop_requested{false};
    bool trigger_observed{false};
    ErrorCode failure_code{ErrorCode::ok};

    [[nodiscard]] bool operator==(
        const CgroupPressureMonitorPollDecision &) const = default;
};

[[nodiscard]] CgroupPressureMonitorPollDecision
classify_cgroup_pressure_monitor_poll_events(
    CgroupPressureMonitorDescriptorRole role,
    std::uint16_t events) noexcept;

[[nodiscard]] Result<CgroupIrqPressure> parse_cgroup_irq_pressure(
    std::string_view record);
[[nodiscard]] Result<CgroupIoStat> parse_cgroup_io_stat(
    std::string_view record);
[[nodiscard]] Result<std::vector<CgroupIoMax>> parse_cgroup_io_max(
    std::string_view record);

[[nodiscard]] Result<CgroupPressureAdmissionDecision>
evaluate_cgroup_pressure_admission(
    const CgroupPressureAdmissionLimits &limits,
    const CgroupPressureAdmissionObservation &observation,
    bool currently_closed,
    bool trigger_hold_active = false);

struct CgroupPressureAdmissionSnapshot {
    CgroupPressureAdmissionLimits limits{};
    bool closed{false};
    std::uint64_t checks{0U};
    std::uint64_t admitted{0U};
    std::uint64_t rejections{0U};
    std::uint64_t sampling_failures{0U};
    std::uint64_t closed_transitions{0U};
    std::uint64_t reopened_transitions{0U};
    bool trigger_monitor_healthy{true};
    bool trigger_hold_active{false};
    std::uint64_t trigger_hold_remaining_microseconds{0U};
    ErrorCode trigger_monitor_error_code{ErrorCode::ok};
    std::uint64_t trigger_events{0U};
    std::uint64_t cpu_some_trigger_events{0U};
    std::uint64_t memory_full_trigger_events{0U};
    std::uint64_t io_full_trigger_events{0U};
    std::uint64_t trigger_monitor_failures{0U};
    std::uint64_t trigger_closed_transitions{0U};
    std::uint64_t trigger_hold_rejections{0U};
    bool last_sample_valid{false};
    ErrorCode last_sampling_error_code{ErrorCode::ok};
    CgroupPressureAdmissionObservation last_observation{};

    [[nodiscard]] bool operator==(
        const CgroupPressureAdmissionSnapshot &) const = default;
};

// Thread-safe host-local load-shedding gate. Configured PSI files are opened
// once beneath the exact delegated cgroup-v2 root and kept descriptor-pinned.
// Every check revalidates cgroup.pressure=1, parses the complete canonical PSI
// records, and updates a latched hysteresis state. Optional dedicated O_RDWR
// descriptors register per-cgroup PSI triggers and one bounded monitor thread
// closes the gate between checks. A trigger holds the gate closed for at least
// one complete tracking window; any trigger-monitor, read, or parse failure
// fails closed. Reopening always requires a later complete avg10 sample that
// satisfies every lower hysteresis boundary.
class CgroupPressureAdmission {
  public:
    [[nodiscard]] static Result<std::shared_ptr<CgroupPressureAdmission>> create(
        const std::filesystem::path &delegated_root,
        CgroupPressureAdmissionLimits limits);

    [[nodiscard]] Status admit();
    [[nodiscard]] CgroupPressureAdmissionSnapshot snapshot() const;

  private:
    struct State;
    explicit CgroupPressureAdmission(std::shared_ptr<State> state) noexcept;

    std::shared_ptr<State> state_;
};

struct CgroupAggregateSnapshot {
    CgroupAggregateLimits limits{};
    std::size_t active_reservations{0U};
    std::size_t peak_active_reservations{0U};
    std::uint64_t reserved_processes{0U};
    std::uint64_t reserved_memory_bytes{0U};
    std::uint64_t reserved_swap_bytes{0U};
    std::uint64_t reserved_cpu_quota_microseconds{0U};
    std::uint64_t peak_reserved_processes{0U};
    std::uint64_t peak_reserved_memory_bytes{0U};
    std::uint64_t peak_reserved_swap_bytes{0U};
    std::uint64_t peak_reserved_cpu_quota_microseconds{0U};
    std::uint64_t rejected_reservations{0U};
    std::uint64_t stranded_reservations{0U};
    std::uint64_t completed_session_outcomes{0U};
    std::uint64_t incomplete_session_outcomes{0U};
    std::uint64_t pids_limit_hits{0U};
    std::uint64_t memory_high_events{0U};
    std::uint64_t memory_max_events{0U};
    std::uint64_t memory_oom_events{0U};
    std::uint64_t memory_oom_kills{0U};
    std::uint64_t memory_oom_group_kills{0U};
    std::uint64_t pids_peak_session_outcomes{0U};
    std::uint64_t pids_peak_sum{0U};
    std::uint64_t pids_peak_maximum{0U};
    std::uint64_t memory_peak_session_outcomes{0U};
    std::uint64_t memory_peak_sum_bytes{0U};
    std::uint64_t memory_peak_maximum_bytes{0U};
    std::uint64_t memory_swap_peak_session_outcomes{0U};
    std::uint64_t memory_swap_peak_sum_bytes{0U};
    std::uint64_t memory_swap_peak_maximum_bytes{0U};
    std::uint64_t memory_stat_session_outcomes{0U};
    std::uint64_t memory_reclaim_stat_session_outcomes{0U};
    std::uint64_t memory_swap_stat_session_outcomes{0U};
    std::uint64_t memory_page_faults{0U};
    std::uint64_t memory_major_page_faults{0U};
    std::uint64_t memory_pages_scanned{0U};
    std::uint64_t memory_pages_reclaimed{0U};
    std::uint64_t memory_pages_swapped_in{0U};
    std::uint64_t memory_pages_swapped_out{0U};
    std::uint64_t memory_swap_events_session_outcomes{0U};
    std::uint64_t memory_swap_high_events{0U};
    std::uint64_t memory_swap_max_events{0U};
    std::uint64_t memory_swap_fail_events{0U};
    std::uint64_t local_stat_session_outcomes{0U};
    std::uint64_t frozen_microseconds{0U};
    std::uint64_t cpu_stat_session_outcomes{0U};
    std::uint64_t cpu_bandwidth_stat_session_outcomes{0U};
    std::uint64_t cpu_burst_stat_session_outcomes{0U};
    std::uint64_t cpu_usage_microseconds{0U};
    std::uint64_t cpu_user_microseconds{0U};
    std::uint64_t cpu_system_microseconds{0U};
    std::uint64_t cpu_periods{0U};
    std::uint64_t cpu_throttled_periods{0U};
    std::uint64_t cpu_throttled_microseconds{0U};
    std::uint64_t cpu_burst_periods{0U};
    std::uint64_t cpu_burst_microseconds{0U};
    std::uint64_t io_read_bytes{0U};
    std::uint64_t io_write_bytes{0U};
    std::uint64_t io_read_operations{0U};
    std::uint64_t io_write_operations{0U};
    std::uint64_t io_discard_bytes{0U};
    std::uint64_t io_discard_operations{0U};
    std::uint64_t cpu_pressure_session_outcomes{0U};
    std::uint64_t cpu_pressure_full_session_outcomes{0U};
    std::uint64_t cpu_pressure_some_microseconds{0U};
    std::uint64_t cpu_pressure_full_microseconds{0U};
    std::uint64_t memory_pressure_session_outcomes{0U};
    std::uint64_t memory_pressure_full_session_outcomes{0U};
    std::uint64_t memory_pressure_some_microseconds{0U};
    std::uint64_t memory_pressure_full_microseconds{0U};
    std::uint64_t io_pressure_session_outcomes{0U};
    std::uint64_t io_pressure_full_session_outcomes{0U};
    std::uint64_t io_pressure_some_microseconds{0U};
    std::uint64_t io_pressure_full_microseconds{0U};
    std::uint64_t irq_pressure_session_outcomes{0U};
    std::uint64_t irq_pressure_full_microseconds{0U};
    CgroupPressureAdmissionSnapshot pressure_admission{};

    [[nodiscard]] bool operator==(const CgroupAggregateSnapshot &) const = default;
};

// Thread-safe, exact host-local reservation ledger. It performs no kernel or
// filesystem work. A successful Reservation is move-only and releases its
// accounted maxima exactly once when rollback or complete teardown is proved.
// If post-spawn teardown cannot be proved, the token may strand its exact charge
// so later admissions fail closed until restart recovery.
class CgroupAggregateAdmission {
  public:
    class Reservation {
      public:
        Reservation() noexcept;
        ~Reservation();

        Reservation(const Reservation &) = delete;
        Reservation &operator=(const Reservation &) = delete;
        Reservation(Reservation &&) noexcept;
        Reservation &operator=(Reservation &&) noexcept;

        [[nodiscard]] bool active() const noexcept;
        void record_outcome(const CgroupSessionOutcome &outcome) noexcept;
        void release() noexcept;
        // Detach this token without subtracting its charge. Used only when
        // complete process/cgroup teardown cannot be proved; the factory then
        // remains conservatively saturated until restart recovery.
        void strand() noexcept;

      private:
        struct State;
        friend class CgroupAggregateAdmission;
        Reservation(
            std::shared_ptr<State> state,
            std::uint64_t processes,
            std::uint64_t memory_bytes,
            std::uint64_t swap_bytes,
            std::uint64_t cpu_quota_microseconds,
            bool charged) noexcept;

        std::shared_ptr<State> state_;
        std::uint64_t processes_{0U};
        std::uint64_t memory_bytes_{0U};
        std::uint64_t swap_bytes_{0U};
        std::uint64_t cpu_quota_microseconds_{0U};
        bool charged_{false};
        bool outcome_recorded_{false};
    };

    [[nodiscard]] static Result<std::shared_ptr<CgroupAggregateAdmission>> create(
        CgroupAggregateLimits limits);

    [[nodiscard]] Result<Reservation> reserve(
        const CgroupResourceLimits &session_limits);
    [[nodiscard]] CgroupAggregateSnapshot snapshot() const;

  private:
    explicit CgroupAggregateAdmission(std::shared_ptr<Reservation::State> state)
        noexcept;

    std::shared_ptr<Reservation::State> state_;
};

[[nodiscard]] Result<std::array<std::uint8_t, 16U>> parse_boot_id(
    std::string_view record);
[[nodiscard]] Result<CgroupOwnerIdentity> current_cgroup_owner_identity();
[[nodiscard]] Result<SessionCgroupName> parse_session_cgroup_name(
    std::string_view name);
[[nodiscard]] Result<std::string> format_session_cgroup_name(
    const SessionCgroupName &name);
// True means the exact owner process is still live. False means the boot,
// starttime, or terminal process state proves that incarnation is gone.
// Inaccessible or malformed procfs evidence returns an error instead of
// authorizing cleanup.
[[nodiscard]] Result<bool> cgroup_owner_is_live(
    const CgroupOwnerIdentity &owner);

// One exact cgroup-v2 leaf owned by the PTY supervisor. Instances are created
// only for explicitly configured hardened sessions. Destruction is fail-safe:
// it requests cgroup.kill, waits for the recursive populated bit to clear for
// a bounded interval, and removes the exact inode when possible.
class SessionCgroup {
  public:
    SessionCgroup() noexcept;
    ~SessionCgroup();

    SessionCgroup(const SessionCgroup &) = delete;
    SessionCgroup &operator=(const SessionCgroup &) = delete;
    SessionCgroup(SessionCgroup &&) noexcept;
    SessionCgroup &operator=(SessionCgroup &&) noexcept;

    [[nodiscard]] static Status validate_resource_limits(
        const CgroupResourceLimits &resource_limits);

    [[nodiscard]] static Result<SessionCgroup> create(
        const std::filesystem::path &delegated_root,
        const IdentityPolicy &payload_identity,
        CgroupResourceLimits resource_limits = {});

    // Exercise the exact delegated root, identity boundary, requested
    // controllers, writable leaf controls, and read-back contract without
    // attaching a payload. The temporary leaf is removed before success is
    // returned. Agent startup uses this before advertising Ratox networking.
    [[nodiscard]] static Status preflight(
        const std::filesystem::path &delegated_root,
        const IdentityPolicy &payload_identity,
        CgroupResourceLimits resource_limits = {});

    // Reclaim only reserved cgroups whose boot/process incarnation is proven
    // dead. Legacy names are removed only when already empty; a populated
    // legacy leaf fails closed because its old numeric PID cannot be made
    // reuse-safe after the fact.
    [[nodiscard]] static Result<CgroupRecoveryReport> recover_orphans(
        const std::filesystem::path &delegated_root,
        CgroupRecoveryConfig config = {});

    [[nodiscard]] Status attach(pid_t process);
    [[nodiscard]] Status kill_all();
    [[nodiscard]] Result<bool> populated();
    [[nodiscard]] Status remove_if_empty();
    // Returns the teardown evidence once after the exact leaf was removed.
    [[nodiscard]] std::optional<CgroupSessionOutcome> take_outcome() noexcept;
    [[nodiscard]] bool best_effort_kill_and_remove(
        std::chrono::milliseconds maximum_wait) noexcept;

  private:
    class Impl;
    explicit SessionCgroup(std::unique_ptr<Impl> implementation) noexcept;

    std::unique_ptr<Impl> implementation_;
};

}  // namespace detail
}  // namespace iotox::terminal
