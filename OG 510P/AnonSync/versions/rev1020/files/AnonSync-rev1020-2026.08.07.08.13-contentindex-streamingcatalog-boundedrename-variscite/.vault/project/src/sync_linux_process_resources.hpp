#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view kSyncLinuxProcessResourcesResponseSchema =
    "anonsync.local-process-resources.response.v1";
inline constexpr std::string_view kSyncLinuxProcessResourcesAggregateSchema =
    "anonsync.local-process-resources.aggregate.v1";
inline constexpr std::string_view kSyncLinuxProcessResourcesSeriesSchema =
    "anonsync.local-process-resources.series.v1";

// One bounded diagnostic observation of Linux process memory. Values are KiB
// exactly as reported by /proc/self/smaps_rollup. This is measurement evidence,
// never file, scheduler, retention, or synchronization authority.
struct SyncLinuxProcessMemorySnapshot final {
    std::uint64_t rss_kib = 0U;
    std::uint64_t pss_kib = 0U;
    std::uint64_t pss_dirty_kib = 0U;
    std::uint64_t pss_anon_kib = 0U;
    std::uint64_t pss_file_kib = 0U;
    std::uint64_t pss_shmem_kib = 0U;
    std::uint64_t shared_clean_kib = 0U;
    std::uint64_t shared_dirty_kib = 0U;
    std::uint64_t private_clean_kib = 0U;
    std::uint64_t private_dirty_kib = 0U;
    std::uint64_t referenced_kib = 0U;
    std::uint64_t anonymous_kib = 0U;
    std::uint64_t anonymous_huge_pages_kib = 0U;
    std::uint64_t shared_hugetlb_kib = 0U;
    std::uint64_t private_hugetlb_kib = 0U;
    std::uint64_t swap_kib = 0U;
    std::uint64_t swap_pss_kib = 0U;
    std::uint64_t locked_kib = 0U;

    [[nodiscard]] std::uint64_t private_resident_kib() const;
    [[nodiscard]] std::uint64_t shared_resident_kib() const;

    bool operator==(const SyncLinuxProcessMemorySnapshot&) const = default;
};

struct SyncLinuxProcessResourceSnapshot final {
    std::uint64_t server_pid = 0U;
    std::uint64_t process_start_time_clock_ticks = 0U;
    std::uint64_t clock_ticks_per_second = 0U;
    std::uint64_t page_size_bytes = 0U;
    std::uint64_t sample_monotonic_milliseconds = 0U;
    SyncLinuxProcessMemorySnapshot memory;
    std::uint64_t peak_rss_kib = 0U;
    std::uint64_t minor_page_faults = 0U;
    std::uint64_t major_page_faults = 0U;
    std::uint64_t filesystem_input_operations = 0U;
    std::uint64_t filesystem_output_operations = 0U;
    std::uint64_t voluntary_context_switches = 0U;
    std::uint64_t involuntary_context_switches = 0U;
    std::uint64_t open_file_descriptors = 0U;
    std::uint64_t threads = 0U;

    bool operator==(const SyncLinuxProcessResourceSnapshot&) const = default;
};

// Parses one complete smaps_rollup image. Every retained field must appear
// exactly once with the canonical "KEY: DECIMAL kB" spelling. Unknown kernel
// fields remain forward-compatible and are ignored.
[[nodiscard]] SyncLinuxProcessMemorySnapshot
parse_sync_linux_smaps_rollup_or_throw(
    std::string_view bytes,
    std::string_view label = "Linux smaps_rollup");

// Reads /proc/self/smaps_rollup through one bounded read(2), then observes
// rusage, process start ticks, descriptor count, and thread count. The
// individual measurements are intentionally not represented as one atomic
// kernel cutpoint.
[[nodiscard]] SyncLinuxProcessResourceSnapshot
observe_sync_linux_process_resources_or_throw(
    std::string_view label = "Linux process resources");

[[nodiscard]] std::string render_sync_linux_process_resources_response_json(
    const SyncLinuxProcessResourceSnapshot& snapshot);

// Strictly validates and decodes one response. expected_server_pid==0 disables
// PID comparison; callers connected over AF_UNIX should always provide the
// peer credential PID.
[[nodiscard]] SyncLinuxProcessResourceSnapshot
parse_sync_linux_process_resources_response_json_or_throw(
    std::string_view response_json,
    std::uint64_t expected_server_pid,
    std::string_view label = "Linux process resources response");

}  // namespace anonsync

#endif
