#pragma once

#include "sync_process_identity_observation.hpp"

#include <cstdint>
#include <string_view>

namespace anonsync::detail {

struct LinuxProcStatIdentity final {
    std::uint64_t process_id = 0;
    char state = '\0';
    std::uint64_t starttime_ticks = 0;
};

// Parses fields 1, 3, and 22 while treating the final ')' as the delimiter for
// comm.  Linux permits spaces and ')' inside comm, so whitespace tokenization
// of the complete line is not correct.
[[nodiscard]] LinuxProcStatIdentity
parse_linux_proc_pid_stat_identity_or_throw(
    std::string_view bytes,
    std::uint64_t expected_process_id);

[[nodiscard]] bool canonical_linux_boot_id(std::string_view value) noexcept;
[[nodiscard]] bool canonical_positive_decimal_token(
    std::string_view value) noexcept;

}  // namespace anonsync::detail
