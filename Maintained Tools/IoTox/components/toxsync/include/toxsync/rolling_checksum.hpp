#pragma once

#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace toxsync {

struct RollingChecksum {
    std::uint32_t a{};
    std::uint32_t b{};
    std::uint32_t window{};

    [[nodiscard]] static RollingChecksum compute(std::span<const std::byte> bytes) noexcept;

    void roll(std::byte outgoing, std::byte incoming) noexcept {
        const auto old_value = std::to_integer<std::uint32_t>(outgoing);
        const auto new_value = std::to_integer<std::uint32_t>(incoming);
        a = (a - old_value + new_value) & 0xffffU;
        b = (b - window * old_value + a) & 0xffffU;
    }

    [[nodiscard]] constexpr std::uint32_t value() const noexcept {
        return (b << 16U) | a;
    }
};

[[nodiscard]] std::string_view rolling_checksum_backend_name() noexcept;

} // namespace toxsync
