#pragma once

#include "iotox/status.hpp"

#include <array>
#include <cstdint>
#include <span>

namespace iotox::security {

// Fill a caller-owned buffer from the operating system CSPRNG. IoTox never
// silently falls back to a deterministic pseudo-random generator for protocol
// nonces or message identifiers.
[[nodiscard]] Status fill_random(std::span<std::uint8_t> output);
[[nodiscard]] Result<std::uint64_t> random_u64_nonzero();
[[nodiscard]] Result<std::array<std::uint8_t, 16U>> random_nonce_128();

}  // namespace iotox::security
