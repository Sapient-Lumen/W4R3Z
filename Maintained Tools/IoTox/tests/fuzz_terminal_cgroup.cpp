#include "iotox/terminal_cgroup.hpp"

#include <cstddef>
#include <cstdint>
#include <string_view>

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    const std::string_view record(
        reinterpret_cast<const char *>(data), size);

    // Exercise every bounded parser that consumes kernel-owned cgroup text.
    // Inputs accepted by one grammar are intentionally also offered to the
    // others so cross-format aliases, spacing, duplicate keys, truncation, and
    // future fields stay fail closed without requiring a fuzzer-side selector.
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_pids_events(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_memory_events(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_memory_stat(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_memory_swap_events(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_local_stat(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_cpu_stat(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_peak(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_pressure(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_irq_pressure(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_io_max(record));
    static_cast<void>(
        iotox::terminal::detail::parse_cgroup_io_stat(record));
    return 0;
}
