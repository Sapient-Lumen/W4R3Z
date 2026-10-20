#pragma once

#include "iotox/agent.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <string>

namespace iotox {

struct AgentPreflightReport {
    std::string network;
    std::string toxcore_provider;
    std::string sodium_provider;
    std::string runtime;
    std::string protected_state;
    std::string savedata;
    std::string identity;
    std::string authority_ledger;
    std::string authority_rollback_witness;
    std::string command_store;
    std::string diagnostics_store;
    std::string peer_alias_store;
    std::string route_inventory;
    std::string synchronization;
    std::string signed_updates;
    std::string ratox;
    std::string cgroup;
    std::string kernel_child_confinement;
    std::size_t namespaces{0U};
    std::size_t terminal_profiles{0U};
    std::size_t terminal_bindings{0U};
};

// Validates one already parsed and normalized Agent configuration without
// creating a listener, network identity, runtime tree, durable record, PTY,
// cgroup, lock, or temporary file. Existing canonical policy stores and route
// inventory are decoded. Durable authority/command/incarnation recovery is
// deliberately left to startup and named as such in the rendered report.
[[nodiscard]] Result<AgentPreflightReport>
preflight_agent_config(const Agent::Config &config);

[[nodiscard]] std::string
render_agent_preflight_report(const AgentPreflightReport &report,
                              bool file_backed);

}  // namespace iotox
