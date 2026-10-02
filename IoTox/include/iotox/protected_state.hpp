#pragma once

#include "iotox/agent.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <string>

namespace iotox::protected_state {

struct Inspection {
    bool enabled{false};
    std::string policy_identifier;
    std::size_t configured_paths{0U};
    std::size_t verified_inodes{0U};
    std::size_t protected_symlinks{0U};
    bool runtime_tmpfs{false};
};

// Side-effect-free, descriptor-pinned deployment boundary. In required mode
// this verifies one externally unlocked fscrypt-v2 policy, the complete
// configured durable-path closure, every extant inode below the root, and a
// tmpfs (or same-policy) runtime before any listener, network, PTY, update, or
// synchronization surface may start.
[[nodiscard]] Result<Inspection> inspect(const Agent::Config &config);

}  // namespace iotox::protected_state
