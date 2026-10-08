#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaFolderWakeMaximumWatches = 262144U;
inline constexpr std::uint64_t
    kSyncReplicaFolderWakeMaximumEntriesPerRebuild = 1048576U;
inline constexpr std::uint64_t
    kSyncReplicaFolderWakeMaximumEventsPerObservation = 65536U;
inline constexpr std::uint64_t
    kSyncReplicaFolderWakeMaximumRetryMilliseconds = 60000U;

// The filesystem event stream is only a responsiveness hint. A bounded event
// observation may be incomplete, coalesced, overflowed, or absent after a
// restart. The configured-folder convergence pass remains the sole authority
// for what exists and what should be published or materialized.
struct SyncReplicaFolderWakeLimits final {
    std::uint64_t maximum_watches = 65536U;
    std::uint64_t maximum_entries_per_rebuild = 262144U;
    std::uint64_t maximum_events_per_observation = 4096U;
    std::uint64_t retry_milliseconds = 250U;

    bool operator==(const SyncReplicaFolderWakeLimits&) const = default;
};

void validate_sync_replica_folder_wake_limits_or_throw(
    const SyncReplicaFolderWakeLimits& limits,
    const std::string& label = "sync replica folder wake limits");

// Cumulative presentation state. None of these counters authorizes a folder
// mutation, deletion, rename, publication, or scheduling decision beyond
// requesting an ordinary bounded convergence pass.
struct SyncReplicaFolderWakeSnapshot final {
    bool platform_supported = false;
    bool active = false;
    bool complete = false;
    std::uint64_t watch_count = 0U;
    std::uint64_t observations = 0U;
    std::uint64_t wake_observations = 0U;
    std::uint64_t events_observed = 0U;
    std::uint64_t rebuilds = 0U;
    std::uint64_t watch_add_failures = 0U;
    std::uint64_t watch_limit_hits = 0U;
    std::uint64_t rebuild_entry_limit_hits = 0U;
    std::uint64_t kernel_queue_overflows = 0U;
    std::uint64_t observation_budget_exhaustions = 0U;
    std::uint64_t invalidations = 0U;
    std::optional<std::string> diagnostic;

    bool operator==(const SyncReplicaFolderWakeSnapshot&) const = default;
};

struct SyncReplicaFolderWakeObservation final {
    bool wake_observed = false;
    bool kernel_queue_overflow = false;
    bool observation_budget_exhausted = false;
    bool watch_topology_changed = false;
    bool watch_set_rebuilt = false;
    std::uint64_t event_count = 0U;
    std::uint64_t watch_count = 0U;
    std::optional<std::string> diagnostic;

    bool operator==(const SyncReplicaFolderWakeObservation&) const = default;
};

// Linux uses one nonblocking inotify descriptor on the service-owner thread.
// There is no watcher thread, catalog, queue, or second scanner. On unsupported
// platforms, root-watch failure, or descriptor failure this owner becomes
// inactive and periodically retries. A partially populated bounded watch set
// remains explicitly incomplete while the service continues to rely on its
// repair scan interval.
class SyncReplicaFolderWakeOwner final {
public:
    explicit SyncReplicaFolderWakeOwner(
        std::filesystem::path absolute_root,
        SyncReplicaFolderWakeLimits limits = {},
        std::string label = "sync replica folder wake owner");
    ~SyncReplicaFolderWakeOwner() noexcept;

    SyncReplicaFolderWakeOwner(const SyncReplicaFolderWakeOwner&) = delete;
    SyncReplicaFolderWakeOwner& operator=(
        const SyncReplicaFolderWakeOwner&) = delete;
    SyncReplicaFolderWakeOwner(SyncReplicaFolderWakeOwner&&) = delete;
    SyncReplicaFolderWakeOwner& operator=(
        SyncReplicaFolderWakeOwner&&) = delete;

    [[nodiscard]] const std::filesystem::path& root() const noexcept;
    [[nodiscard]] const SyncReplicaFolderWakeLimits& limits() const noexcept;
    [[nodiscard]] const SyncReplicaFolderWakeSnapshot& snapshot()
        const noexcept;

    [[nodiscard]] SyncReplicaFolderWakeObservation observe_or_throw();

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
