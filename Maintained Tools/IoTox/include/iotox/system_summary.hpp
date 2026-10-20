#pragma once

#include "iotox/protocol/command.hpp"
#include "iotox/status.hpp"

namespace iotox {

// Collect the bounded Linux view used by system.summary. This API intentionally
// exposes no host name, address, mount, user, process name, or machine ID.
[[nodiscard]] Result<protocol::SystemSummary> collect_system_summary();

}  // namespace iotox
