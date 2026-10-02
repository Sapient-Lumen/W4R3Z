#pragma once

#include "iotox/status.hpp"

#include <iosfwd>
#include <span>
#include <string>
#include <string_view>

namespace iotox {

enum class CliCommandKind {
    agent,
    control,
    terminal,
    terminal_admin,
    witness,
    informational,
    compatibility,
};

struct CliCommandDescriptor {
    std::string_view name;
    CliCommandKind kind{CliCommandKind::control};
    // Non-empty only for an accepted compatibility spelling.
    std::string_view canonical_name;
};

[[nodiscard]] std::span<const CliCommandDescriptor>
cli_command_registry() noexcept;

[[nodiscard]] const CliCommandDescriptor *find_cli_command(
    std::string_view name) noexcept;

[[nodiscard]] bool is_cli_command_kind(
    std::string_view name, CliCommandKind kind) noexcept;

void write_cli_command_index(std::ostream &output);

[[nodiscard]] Result<std::string> generate_cli_completion(
    std::string_view shell);

}  // namespace iotox
