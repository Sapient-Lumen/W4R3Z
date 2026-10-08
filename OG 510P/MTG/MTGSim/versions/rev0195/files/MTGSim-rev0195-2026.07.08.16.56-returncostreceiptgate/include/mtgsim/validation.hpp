#pragma once

#include "mtgsim/types.hpp"

#include <string>
#include <vector>

namespace mtgsim {

enum class ViolationSeverity : u8 {
    Warning,
    Error
};

struct InvariantViolation {
    ViolationSeverity severity = ViolationSeverity::Error;
    std::string code;
    std::string detail;
};

[[nodiscard]] const char* to_string(ViolationSeverity severity) noexcept;
[[nodiscard]] std::vector<InvariantViolation> validate_game_state(const GameState& game);
void assert_valid_game_state(const GameState& game);

} // namespace mtgsim
