#pragma once

#include "sync_replica_model.hpp"

#include <cstdint>
#include <string_view>
#include <vector>

namespace anonsync::detail {

void validate_sync_replica_model_limits_impl_or_throw(
    const SyncReplicaModelLimits& limits);

[[nodiscard]] std::uint64_t
    validate_sync_replica_operation_and_measure_or_throw(
        const SyncReplicaOperation& operation,
        const SyncReplicaModelLimits& limits);

void validate_sync_replica_actor_or_throw(
    const SyncReplicaActor& actor,
    std::string_view label);

[[nodiscard]] std::uint64_t sync_replica_context_counter(
    const std::vector<SyncReplicaClockEntry>& context,
    const SyncReplicaActor& actor) noexcept;

}  // namespace anonsync::detail
