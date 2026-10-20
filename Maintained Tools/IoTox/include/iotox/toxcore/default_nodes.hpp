#pragma once

#include "iotox/toxcore/bootstrap.hpp"

#include <span>
#include <string_view>
#include <vector>

namespace iotox::toxcore {

enum class DefaultNodeRole {
    bootstrap,
    tcp_relay,
};

struct DefaultNodeRecord {
    DefaultNodeRole role{DefaultNodeRole::bootstrap};
    BootstrapEndpoint endpoint;
    std::string_view location;
};

inline constexpr std::string_view kDefaultNodeSnapshotDate = "2026-08-13";
inline constexpr std::string_view kDefaultNodeSource = "https://nodes.tox.chat/";

// A frozen, deliberately small startup catalog. It is reachability configuration,
// never authority. The catalog is expected to age; users can replace it entirely
// with explicit --bootstrap/--tcp-relay options.
[[nodiscard]] std::span<const DefaultNodeRecord> default_node_catalog();
[[nodiscard]] std::vector<BootstrapEndpoint> default_bootstrap_nodes();
[[nodiscard]] std::vector<BootstrapEndpoint> default_tcp_relays();
[[nodiscard]] std::string_view to_string(DefaultNodeRole role);

}  // namespace iotox::toxcore
