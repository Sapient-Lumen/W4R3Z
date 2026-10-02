#pragma once

#include "iotox/status.hpp"

#include <array>
#include <compare>
#include <cstdint>
#include <string>
#include <string_view>

namespace iotox::mutorr {

inline constexpr std::size_t kIdSize = 32U;

struct Id256 {
    std::array<std::uint8_t, kIdSize> bytes{};

    [[nodiscard]] bool is_zero() const noexcept;
    [[nodiscard]] std::string hex() const;
    [[nodiscard]] static Result<Id256> from_hex(std::string_view text);

    friend bool operator==(const Id256 &, const Id256 &) = default;
    friend auto operator<=>(const Id256 &, const Id256 &) = default;
};

// Deterministic synthetic identifiers for simulations, examples, and tests.
// They are not cryptographic keys and must not be used as production identities.
[[nodiscard]] Id256 synthetic_id(std::uint64_t value, std::uint64_t domain = 0U) noexcept;

}  // namespace iotox::mutorr
