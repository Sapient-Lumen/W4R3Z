#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>

#if !defined(_WIN32)
#include <sys/types.h>
#endif

namespace anonsync::sync_bounded_regular_file_detail {

inline constexpr std::size_t kReadChunkBytes = 8192U;

[[nodiscard]] inline std::size_t checked_maximum_size_or_throw(
    std::uint64_t maximum_bytes,
    const std::string& label) {
    if (maximum_bytes == 0) {
        throw std::runtime_error(label + " maximum bytes must be positive");
    }
    if (maximum_bytes >
        static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        throw std::runtime_error(label +
                                 " maximum bytes exceed addressable memory");
    }
    const std::size_t maximum_size =
        static_cast<std::size_t>(maximum_bytes);
    if (maximum_size > std::string{}.max_size()) {
        throw std::runtime_error(label +
                                 " maximum bytes exceed string capacity");
    }
#if !defined(_WIN32)
    if (maximum_bytes >
        static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        throw std::runtime_error(label +
                                 " maximum bytes exceed positional-read range");
    }
#endif
    return maximum_size;
}

[[nodiscard]] inline std::size_t next_read_size(
    std::size_t current_size,
    std::size_t maximum_size) noexcept {
    const std::size_t remaining = maximum_size - current_size;
    if (remaining < kReadChunkBytes) {
        return remaining + 1U;  // One-byte sentinel proves the ceiling.
    }
    return kReadChunkBytes;
}

}  // namespace anonsync::sync_bounded_regular_file_detail
