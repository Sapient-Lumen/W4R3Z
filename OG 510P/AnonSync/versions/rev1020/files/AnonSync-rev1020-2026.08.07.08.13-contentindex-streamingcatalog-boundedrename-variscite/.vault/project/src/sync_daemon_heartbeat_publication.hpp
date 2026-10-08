#pragma once

#include "sync_daemon_heartbeat_document.hpp"

#include <cstdint>
#include <string>

namespace anonsync {

struct SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions;
struct SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult;

// The single adapter from the broad daemon orchestration model into the small,
// owning publication value accepted by the heartbeat codec.  Callers provide
// the lifecycle transition fields that belong to this publication; every
// remaining field is copied from the exact options/result snapshot here.
[[nodiscard]] SyncDaemonHeartbeatPublication
make_sync_daemon_heartbeat_publication_or_throw(
    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& result,
    const std::string& state,
    std::uint64_t heartbeat_epoch,
    std::uint64_t stale_at_epoch,
    bool final,
    const std::string& reason);

}  // namespace anonsync
