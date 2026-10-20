#pragma once

#include "iotox/terminal_cgroup.hpp"
#include "iotox/terminal_process.hpp"

#include <chrono>
#include <filesystem>
#include <string_view>
#include <utility>

namespace iotox::terminal {

inline constexpr std::string_view kInternalTerminalChildArgument =
    "__iotox-terminal-child-v1";
struct PosixPtyOptions {
    PosixPtyOptions() = default;
    PosixPtyOptions(
        std::filesystem::path helper,
        std::chrono::milliseconds timeout,
        std::filesystem::path cgroup_root = {},
        CgroupResourceLimits cgroup_limits = {},
        CgroupAggregateLimits aggregate_limits = {},
        CgroupPressureAdmissionLimits pressure_admission_limits = {})
        : helper_executable(std::move(helper)), startup_timeout(timeout),
          delegated_cgroup_root(std::move(cgroup_root)),
          cgroup_resource_limits(std::move(cgroup_limits)),
          cgroup_aggregate_limits(std::move(aggregate_limits)),
          cgroup_pressure_admission_limits(
              std::move(pressure_admission_limits)) {}

    std::filesystem::path helper_executable;
    std::chrono::milliseconds startup_timeout{3000};
    // Empty preserves the procfs/pidfd supervision contract. A nonempty
    // path names a securely delegated cgroup-v2 root under which each
    // hardened PTY receives one kernel-owned session leaf.
    std::filesystem::path delegated_cgroup_root;
    // Optional administrator-owned controller ceiling. A profile may only
    // tighten it. Any effective policy without a delegated root is rejected
    // before process or cgroup filesystem work.
    CgroupResourceLimits cgroup_resource_limits;
    // Optional host-wide exact reservation ceiling. Configured dimensions
    // require finite effective per-session maxima and are charged before any
    // cgroup leaf or PTY child can be created.
    CgroupAggregateLimits cgroup_aggregate_limits;
    // Optional host PSI load-shedding policy sampled from the exact delegated
    // root before aggregate reservation or any PTY/cgroup mutation.
    CgroupPressureAdmissionLimits cgroup_pressure_admission_limits;
};

class PosixPtyProcessFactory final : public PtyProcessFactory {
  public:
    explicit PosixPtyProcessFactory(PosixPtyOptions options);
    [[nodiscard]] Status configuration_status() const;
    [[nodiscard]] Result<std::unique_ptr<PtyProcess>> spawn(
        const ResolvedProfile &profile) override;
    [[nodiscard]] detail::CgroupAggregateSnapshot aggregate_snapshot() const;

  private:
    PosixPtyOptions options_;
    Status cgroup_configuration_status_{};
    std::shared_ptr<detail::CgroupAggregateAdmission> aggregate_admission_;
    std::shared_ptr<detail::CgroupPressureAdmission> pressure_admission_;
};

// These entrances are intentionally intercepted by main before the public CLI.
// They are implementation details, never network operations or advertised CLI.
[[nodiscard]] int run_internal_terminal_child() noexcept;

}  // namespace iotox::terminal
