#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>

namespace iotox {

inline constexpr std::size_t kTerminalCgroupInterfaceCount = 12U;

// This is a local administrative snapshot and may contain host paths/text.
// Callers exporting diagnostics must explicitly reduce it to a closed schema.
struct TerminalHostCapabilities {
    std::string pidfd;
    std::string seccomp;
    std::string mdwe;
    std::string landlock;
    std::uint32_t landlock_abi{0U};
    std::string privilege_escalation;
    std::string sudo_path;
    std::string sudo_mechanism;
    std::string sudo_policy{"not-probed"};
    std::string cgroup_v2;
    std::filesystem::path cgroup_root;
    std::string cgroup_delegation;
    std::string cgroup_controllers;
    std::array<std::string, kTerminalCgroupInterfaceCount> cgroup_interfaces;
};

[[nodiscard]] TerminalHostCapabilities probe_terminal_host_capabilities(
    const std::filesystem::path &cgroup_root, bool live_confinement_probes);
[[nodiscard]] std::string render_terminal_host_capabilities(
    const TerminalHostCapabilities &capabilities);

[[nodiscard]] bool is_terminal_admin_cli_invocation(
    std::span<const std::string_view> arguments) noexcept;
[[nodiscard]] int run_terminal_admin_cli(
    std::span<const std::string_view> arguments);

}  // namespace iotox
