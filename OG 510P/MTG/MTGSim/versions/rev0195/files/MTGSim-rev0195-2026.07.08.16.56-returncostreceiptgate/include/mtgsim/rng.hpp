#pragma once

#include <algorithm>
#include <cstdint>
#include <iterator>

namespace mtgsim {

class SplitMix64 {
public:
    explicit SplitMix64(std::uint64_t seed) noexcept : state_(seed) {}

    [[nodiscard]] std::uint64_t state() const noexcept { return state_; }
    void set_state(std::uint64_t value) noexcept { state_ = value; }

    [[nodiscard]] std::uint64_t next_u64() noexcept;
    [[nodiscard]] std::uint32_t uniform_u32(std::uint32_t exclusive_upper_bound) noexcept;

    template <typename RandomIt>
    void shuffle(RandomIt first, RandomIt last) noexcept {
        using difference_type = typename std::iterator_traits<RandomIt>::difference_type;
        const auto n = static_cast<difference_type>(std::distance(first, last));
        for (difference_type i = n - 1; i > 0; --i) {
            const auto j = static_cast<difference_type>(uniform_u32(static_cast<std::uint32_t>(i + 1)));
            std::iter_swap(first + i, first + j);
        }
    }

private:
    std::uint64_t state_;
};

} // namespace mtgsim
