#pragma once

#if !defined(_WIN32)

#include "sync_replica_folder_scan_owner.hpp"

#include <cstdint>
#include <iosfwd>
#include <optional>
#include <string>

namespace anonsync {

// One completed history page is retained inside the owner status object served
// by the fixed one-megabyte local socket. Keep the inventory itself to one
// quarter of that envelope so configuration, health, failure, and lifecycle
// evidence retain independent headroom. This is a presentation boundary, not a
// causal-history retention or restore limit: a byte-truncated page carries the
// same exact operation cursor and source cutpoint as an entry-truncated page.
inline constexpr std::uint64_t
    kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes =
        256U * 1024U;
// Retention-plan entries have fixed-width digest identities and a 1,024-entry
// public page ceiling. Use a slightly tighter envelope than history so the
// independent encoded-byte frontier is reachable by a valid maximum page,
// remains covered by tests, and leaves extra room for the surrounding v19
// service status. Exact digest pagination makes the omitted suffix reachable.
inline constexpr std::uint64_t
    kSyncReplicaRetentionPlanMaximumStatusBytes = 224U * 1024U;

// Canonical JSON projections used both by the peer-service status renderer and
// by the exact byte frontier below. Keeping the counting and emitted forms on
// one implementation prevents a valid accepted page from exceeding the local
// status transport because two serializers disagreed about escaping or fields.
// Stream forms are the shipping status path. String renderers remain useful to
// focused tests and local callers, but the status owner does not allocate a
// second inventory-sized temporary merely to append canonical JSON.
void append_sync_replica_historical_version_query_json(
    std::ostream& output,
    const SyncReplicaHistoricalVersionQuery& query);

void append_sync_replica_historical_version_inventory_json(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionInventory>& inventory);

void append_sync_replica_retention_plan_query_json(
    std::ostream& output,
    const SyncReplicaRetentionPlanQuery& query);

void append_sync_replica_retention_plan_json(
    std::ostream& output,
    const std::optional<SyncReplicaRetentionPlan>& plan);

[[nodiscard]] std::string
render_sync_replica_historical_version_query_json(
    const SyncReplicaHistoricalVersionQuery& query);

[[nodiscard]] std::string
render_sync_replica_historical_version_inventory_json(
    const std::optional<SyncReplicaHistoricalVersionInventory>& inventory);

[[nodiscard]] std::string render_sync_replica_retention_plan_query_json(
    const SyncReplicaRetentionPlanQuery& query);

[[nodiscard]] std::string render_sync_replica_retention_plan_json(
    const std::optional<SyncReplicaRetentionPlan>& plan);

// Applies a deterministic prefix frontier to a completed owner inventory. The
// page always retains at least one entry when any entry existed, reports the
// byte stop separately from the owner's entry-count stop, and leaves all source
// counts untouched. Subsequent pages therefore remain reachable through the
// exact operation-ID cursor without another pagination protocol.
void bound_sync_replica_historical_version_inventory_for_status_or_throw(
    SyncReplicaHistoricalVersionInventory& inventory);

// Applies the same deterministic encoded-byte frontier to one physical-payload
// plan. The exact digest cursor and source cutpoint retain reachability of every
// omitted physical object without turning presentation truncation into policy.
void bound_sync_replica_retention_plan_for_status_or_throw(
    SyncReplicaRetentionPlan& plan);

}  // namespace anonsync

#endif
