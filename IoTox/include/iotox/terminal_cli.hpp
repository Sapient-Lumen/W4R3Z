#pragma once

#include <span>
#include <string_view>

namespace iotox {

[[nodiscard]] bool is_terminal_cli_invocation(
    std::span<const std::string_view> arguments) noexcept;
[[nodiscard]] int run_terminal_cli(
    std::span<const std::string_view> arguments);

}  // namespace iotox
