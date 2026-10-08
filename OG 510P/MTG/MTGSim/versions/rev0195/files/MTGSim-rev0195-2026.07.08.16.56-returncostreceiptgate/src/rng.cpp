#include "mtgsim/rng.hpp"

#include <limits>

namespace mtgsim {

std::uint64_t SplitMix64::next_u64() noexcept {
    std::uint64_t z = (state_ += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27U)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31U);
}

std::uint32_t SplitMix64::uniform_u32(std::uint32_t exclusive_upper_bound) noexcept {
    if (exclusive_upper_bound == 0U) {
        return 0U;
    }
    const std::uint64_t bound = static_cast<std::uint64_t>(exclusive_upper_bound);
    const std::uint64_t threshold = (std::numeric_limits<std::uint64_t>::max() - bound + 1ULL) % bound;
    for (;;) {
        const std::uint64_t value = next_u64();
        if (value >= threshold) {
            return static_cast<std::uint32_t>(value % bound);
        }
    }
}

} // namespace mtgsim
