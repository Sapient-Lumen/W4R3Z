#pragma once

#include "iotox/status.hpp"

namespace iotox::security {

// Seals the long-lived agent process before a remote terminal host can cause it
// to hold both device secrets and same-UID PTY children. The operation is
// idempotent and fail-closed: core dumps are disabled at the hard limit and the
// process is made non-dumpable before any Agent state is constructed.
[[nodiscard]] Status seal_remote_terminal_host_process();

}  // namespace iotox::security
