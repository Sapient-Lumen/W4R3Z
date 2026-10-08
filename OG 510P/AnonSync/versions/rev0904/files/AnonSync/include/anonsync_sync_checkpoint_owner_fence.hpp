#pragma once

#include <cstdint>
#include <string>

namespace anonsync {

// A daemon-owner capability is not a descriptive lock observation. It is the
// exact, recipient-verifiable generation minted by the checkpoint database.
// Every field participates in the authority decision; partially populated
// values are invalid rather than being treated as an absent capability.
struct SyncSessionCheckpointDaemonOwnerCapability final {
    std::string session_id;
    std::string daemon_id;
    std::string worker_id;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
};

}  // namespace anonsync
