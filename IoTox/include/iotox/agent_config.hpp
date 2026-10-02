#pragma once

#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox {

inline constexpr std::size_t kMaximumAgentConfigArguments = 256U;
inline constexpr std::size_t kMaximumAgentConfigArgumentBytes = 4096U;
inline constexpr std::size_t kMaximumAgentConfigBytes = 256U * 1024U;

struct AgentConfigRecord {
    std::vector<std::string> arguments;

    [[nodiscard]] bool operator==(const AgentConfigRecord &) const = default;
};

// A canonical, shell-free owner-local deployment record:
//
//   iotox-agent-config-v1
//   argument-0000=--state
//   argument-0001=/var/lib/iotox/device.toxsave
//
// Fields must be contiguous and ordered, values contain no control bytes, and
// the record has exactly one trailing LF. Semantic validation remains owned by
// the ordinary Agent argument parser.
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_agent_config_record(const AgentConfigRecord &record);
[[nodiscard]] Result<AgentConfigRecord>
decode_agent_config_record(std::span<const std::uint8_t> bytes);

// PATH must be normalized, non-root, and absolute. The final component is
// opened no-follow and must be one single-link regular file owned by
// EXPECTED_OWNER_UID with no group/other permissions. A stable descriptor
// snapshot is required across the complete bounded read.
[[nodiscard]] Result<AgentConfigRecord> load_agent_config_record(
    const std::filesystem::path &path, std::uint32_t expected_owner_uid);

// Command-line fields replace same-named file fields. All instances of a
// repeatable file option are replaced when the command line supplies that
// option; command-line order is then retained. Non-repeatable duplicates are
// rejected on either side.
[[nodiscard]] Result<std::vector<std::string>> merge_agent_config_arguments(
    std::span<const std::string> file_arguments,
    std::span<const std::string_view> command_line_arguments);

}  // namespace iotox
