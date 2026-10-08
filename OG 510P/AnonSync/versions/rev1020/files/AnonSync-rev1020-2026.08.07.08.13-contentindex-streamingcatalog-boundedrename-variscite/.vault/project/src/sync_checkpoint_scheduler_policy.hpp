#pragma once

#include "anonsync_core.hpp"

#include <cstdint>
#include <vector>

namespace anonsync::sync_checkpoint_scheduler_policy {

SyncValidationResult plan_resume_transfer_workorder_actions(
    const std::vector<SyncSessionCheckpointResumeTransferWorkorderQueueFact>& facts,
    std::uint64_t max_scheduler_actions,
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult& out);

}  // namespace anonsync::sync_checkpoint_scheduler_policy
