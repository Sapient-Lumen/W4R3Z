#include "iotox/system_summary.hpp"

#include <sys/sysinfo.h>

#include <algorithm>
#include <cstdint>
#include <limits>

namespace iotox {
namespace {

std::uint32_t saturate(std::uint64_t value) noexcept {
    return static_cast<std::uint32_t>(std::min<std::uint64_t>(
        value, std::numeric_limits<std::uint32_t>::max()));
}

}  // namespace

Result<protocol::SystemSummary> collect_system_summary() {
    struct sysinfo info {};
    if (::sysinfo(&info) != 0) {
        return Status{ErrorCode::io_error, "sysinfo failed"};
    }

    protocol::SystemSummary summary;
    summary.health = protocol::SystemHealth::healthy;
    summary.flags = protocol::kSystemSummaryMemoryValid |
                    protocol::kSystemSummaryLoadValid |
                    protocol::kSystemSummaryProcessCountValid;
    summary.uptime_minutes = saturate(
        static_cast<std::uint64_t>(std::max<long>(info.uptime, 0L)) / 60U);

    constexpr std::uint64_t kBucketBytes = 64ULL * 1024ULL * 1024ULL;
    const auto memory_unit = static_cast<std::uint64_t>(info.mem_unit);
    const auto total_bytes = static_cast<std::uint64_t>(info.totalram) * memory_unit;
    const auto available_bytes =
        (static_cast<std::uint64_t>(info.freeram) +
         static_cast<std::uint64_t>(info.bufferram)) * memory_unit;
    summary.memory_total_64mib = saturate(total_bytes / kBucketBytes);
    summary.memory_available_64mib = saturate(
        std::min(available_bytes, total_bytes) / kBucketBytes);

    // sysinfo loads use SI_LOAD_SHIFT fixed point. Round down to the privacy
    // contract's tenths, represented as milli-load units.
    constexpr std::uint64_t kLoadScale = 1ULL << SI_LOAD_SHIFT;
    const auto raw_milli =
        (static_cast<std::uint64_t>(info.loads[0]) * 1000ULL) / kLoadScale;
    summary.load_milli = saturate((raw_milli / 100ULL) * 100ULL);
    summary.process_count = static_cast<std::uint32_t>(info.procs);
    return summary;
}

}  // namespace iotox
