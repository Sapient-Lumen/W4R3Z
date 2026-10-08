#include "sync_replica_folder_wake.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <system_error>
#include <unordered_set>
#include <utility>

#if defined(__linux__)
#include <sys/inotify.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;
using Milliseconds = std::chrono::milliseconds;

[[nodiscard]] Clock::time_point add_milliseconds_or_max(
    Clock::time_point base,
    std::uint64_t amount) noexcept {
    if (amount > static_cast<std::uint64_t>(
                     std::numeric_limits<Milliseconds::rep>::max())) {
        return Clock::time_point::max();
    }
    const Milliseconds duration(static_cast<Milliseconds::rep>(amount));
    if (duration.count() > 0 &&
        base > Clock::time_point::max() - duration) {
        return Clock::time_point::max();
    }
    return base + duration;
}

[[nodiscard]] std::string system_error_text(
    std::string_view action,
    int error) {
    return std::string(action) + " failed: " + std::strerror(error) +
        " (errno " + std::to_string(error) + ")";
}

}  // namespace

void validate_sync_replica_folder_wake_limits_or_throw(
    const SyncReplicaFolderWakeLimits& limits,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder wake limits label must not be empty");
    }
    if (limits.maximum_watches == 0U ||
        limits.maximum_watches > kSyncReplicaFolderWakeMaximumWatches) {
        throw std::invalid_argument(
            label + " maximum_watches must be in [1, 262144]");
    }
    if (limits.maximum_entries_per_rebuild == 0U ||
        limits.maximum_entries_per_rebuild >
            kSyncReplicaFolderWakeMaximumEntriesPerRebuild) {
        throw std::invalid_argument(
            label +
            " maximum_entries_per_rebuild must be in [1, 1048576]");
    }
    if (limits.maximum_events_per_observation == 0U ||
        limits.maximum_events_per_observation >
            kSyncReplicaFolderWakeMaximumEventsPerObservation) {
        throw std::invalid_argument(
            label +
            " maximum_events_per_observation must be in [1, 65536]");
    }
    if (limits.retry_milliseconds == 0U ||
        limits.retry_milliseconds >
            kSyncReplicaFolderWakeMaximumRetryMilliseconds) {
        throw std::invalid_argument(
            label + " retry_milliseconds must be in [1, 60000]");
    }
}

struct SyncReplicaFolderWakeOwner::State final {
    fs::path root;
    SyncReplicaFolderWakeLimits limits;
    SyncReplicaFolderWakeSnapshot snapshot;
    Clock::time_point retry_at = Clock::time_point::min();
    std::string label;

#if defined(__linux__)
    int descriptor = -1;
    std::unordered_set<int> watch_descriptors;
#endif

    State(
        fs::path selected_root,
        SyncReplicaFolderWakeLimits selected_limits,
        std::string owner_label)
        : root(std::move(selected_root)),
          limits(std::move(selected_limits)),
          label(std::move(owner_label)) {
#if defined(__linux__)
        snapshot.platform_supported = true;
        (void)rebuild();
#else
        snapshot.platform_supported = false;
        snapshot.diagnostic =
            "filesystem wake hints are unavailable on this platform";
#endif
    }

    ~State() noexcept {
#if defined(__linux__)
        close_descriptor();
#endif
    }

#if defined(__linux__)
    static constexpr std::uint32_t kWatchMask =
        IN_ATTRIB | IN_CLOSE_WRITE | IN_CREATE | IN_DELETE |
        IN_DELETE_SELF | IN_MODIFY | IN_MOVE_SELF | IN_MOVED_FROM |
        IN_MOVED_TO | IN_UNMOUNT | IN_ONLYDIR | IN_DONT_FOLLOW |
        IN_EXCL_UNLINK;

    void close_descriptor() noexcept {
        if (descriptor >= 0) {
            (void)::close(descriptor);
            descriptor = -1;
        }
        watch_descriptors.clear();
        snapshot.active = false;
        snapshot.complete = false;
        snapshot.watch_count = 0U;
    }

    void schedule_retry() noexcept {
        retry_at = add_milliseconds_or_max(
            Clock::now(), limits.retry_milliseconds);
    }

    void deactivate_with_diagnostic(std::string diagnostic) noexcept {
        close_descriptor();
        snapshot.diagnostic = std::move(diagnostic);
        schedule_retry();
    }

    [[nodiscard]] bool add_watch(
        int target_descriptor,
        const fs::path& directory,
        std::unordered_set<int>& target_watches,
        bool root_watch,
        bool& complete,
        std::optional<std::string>& diagnostic) {
        if (target_watches.size() >= limits.maximum_watches) {
            ++snapshot.watch_limit_hits;
            complete = false;
            diagnostic = label + " reached its bounded watch count";
            return false;
        }
        const int watch = ::inotify_add_watch(
            target_descriptor, directory.c_str(), kWatchMask);
        if (watch < 0) {
            const int error = errno;
            ++snapshot.watch_add_failures;
            complete = false;
            diagnostic = system_error_text(
                label + " inotify_add_watch " + directory.generic_string(),
                error);
            return !root_watch;
        }
        target_watches.insert(watch);
        return true;
    }

    [[nodiscard]] bool rebuild() {
        const int next_descriptor =
            ::inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
        if (next_descriptor < 0) {
            deactivate_with_diagnostic(system_error_text(
                label + " inotify_init1", errno));
            return false;
        }

        std::unordered_set<int> next_watches;
        next_watches.reserve(static_cast<std::size_t>(
            std::min<std::uint64_t>(limits.maximum_watches, 4096U)));
        bool complete = true;
        std::optional<std::string> diagnostic;
        if (!add_watch(
                next_descriptor, root, next_watches, true, complete,
                diagnostic)) {
            const int saved_error = errno;
            (void)::close(next_descriptor);
            if (!diagnostic.has_value()) {
                diagnostic = system_error_text(
                    label + " root watch", saved_error);
            }
            deactivate_with_diagnostic(std::move(*diagnostic));
            return false;
        }

        std::error_code iteration_error;
        fs::recursive_directory_iterator iterator(
            root, fs::directory_options::skip_permission_denied,
            iteration_error);
        const fs::recursive_directory_iterator end;
        if (iteration_error) {
            complete = false;
            diagnostic = label + " could not begin recursive watch rebuild: " +
                iteration_error.message();
            iteration_error.clear();
        }

        std::uint64_t visited_entries = 0U;
        while (iterator != end) {
            if (visited_entries >= limits.maximum_entries_per_rebuild) {
                ++snapshot.rebuild_entry_limit_hits;
                complete = false;
                diagnostic = label +
                    " reached its bounded rebuild entry count";
                break;
            }
            ++visited_entries;

            std::error_code status_error;
            const fs::file_status status = iterator->symlink_status(status_error);
            if (status_error) {
                complete = false;
                diagnostic = label + " could not classify " +
                    iterator->path().generic_string() + ": " +
                    status_error.message();
            } else if (fs::is_directory(status)) {
                if (!add_watch(
                        next_descriptor, iterator->path(), next_watches,
                        false, complete, diagnostic) &&
                    next_watches.size() >= limits.maximum_watches) {
                    break;
                }
            }

            iterator.increment(iteration_error);
            if (iteration_error) {
                complete = false;
                diagnostic = label + " recursive watch rebuild advanced with " +
                    iteration_error.message();
                iteration_error.clear();
            }
        }

        close_descriptor();
        descriptor = next_descriptor;
        watch_descriptors = std::move(next_watches);
        snapshot.active = true;
        snapshot.complete = complete;
        snapshot.watch_count = static_cast<std::uint64_t>(
            watch_descriptors.size());
        snapshot.diagnostic = std::move(diagnostic);
        retry_at = Clock::time_point::min();
        ++snapshot.rebuilds;
        return true;
    }
#endif
};

SyncReplicaFolderWakeOwner::SyncReplicaFolderWakeOwner(
    fs::path absolute_root,
    SyncReplicaFolderWakeLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder wake owner label must not be empty");
    }
    if (absolute_root.empty() || !absolute_root.is_absolute()) {
        throw std::invalid_argument(
            label + " root must be an absolute path");
    }
    validate_sync_replica_folder_wake_limits_or_throw(
        limits, label + " limits");
    state_ = std::make_unique<State>(
        std::move(absolute_root), std::move(limits), std::move(label));
}

SyncReplicaFolderWakeOwner::~SyncReplicaFolderWakeOwner() noexcept = default;

const fs::path& SyncReplicaFolderWakeOwner::root() const noexcept {
    return state_->root;
}

const SyncReplicaFolderWakeLimits&
SyncReplicaFolderWakeOwner::limits() const noexcept {
    return state_->limits;
}

const SyncReplicaFolderWakeSnapshot&
SyncReplicaFolderWakeOwner::snapshot() const noexcept {
    return state_->snapshot;
}

SyncReplicaFolderWakeObservation
SyncReplicaFolderWakeOwner::observe_or_throw() {
    if (!state_) {
        throw std::logic_error(
            "sync replica folder wake owner is inactive");
    }
    SyncReplicaFolderWakeObservation observation;
    ++state_->snapshot.observations;

#if !defined(__linux__)
    observation.diagnostic = state_->snapshot.diagnostic;
    return observation;
#else
    if (state_->descriptor < 0) {
        if (Clock::now() >= state_->retry_at) {
            observation.watch_set_rebuilt = state_->rebuild();
            observation.wake_observed = observation.watch_set_rebuilt;
        }
        observation.watch_count = state_->snapshot.watch_count;
        observation.diagnostic = state_->snapshot.diagnostic;
        if (observation.wake_observed) {
            ++state_->snapshot.wake_observations;
        }
        return observation;
    }

    alignas(inotify_event) std::array<std::byte, 64U * 1024U> buffer{};
    bool rebuild_requested = false;
    bool stop_drain = false;
    for (;;) {
        const ssize_t received = ::read(
            state_->descriptor, buffer.data(), buffer.size());
        if (received < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
            const std::string diagnostic = system_error_text(
                state_->label + " inotify read", errno);
            state_->deactivate_with_diagnostic(diagnostic);
            observation.diagnostic = diagnostic;
            observation.wake_observed = true;
            rebuild_requested = false;
            break;
        }
        if (received == 0) {
            const std::string diagnostic =
                state_->label + " inotify descriptor reached end of stream";
            state_->deactivate_with_diagnostic(diagnostic);
            observation.diagnostic = diagnostic;
            observation.wake_observed = true;
            rebuild_requested = false;
            break;
        }

        std::size_t offset = 0U;
        const std::size_t exact_received =
            static_cast<std::size_t>(received);
        while (offset < exact_received) {
            if (exact_received - offset < sizeof(inotify_event)) {
                throw std::runtime_error(
                    state_->label + " received a truncated inotify header");
            }
            const auto* event = reinterpret_cast<const inotify_event*>(
                buffer.data() + offset);
            const std::size_t record_size =
                sizeof(inotify_event) + static_cast<std::size_t>(event->len);
            if (record_size > exact_received - offset) {
                throw std::runtime_error(
                    state_->label + " received a truncated inotify record");
            }

            if (observation.event_count >=
                state_->limits.maximum_events_per_observation) {
                observation.observation_budget_exhausted = true;
                observation.wake_observed = true;
                rebuild_requested = true;
                stop_drain = true;
                break;
            }

            ++observation.event_count;
            observation.wake_observed = true;
            if ((event->mask & IN_Q_OVERFLOW) != 0U) {
                observation.kernel_queue_overflow = true;
                rebuild_requested = true;
            }
            if ((event->mask &
                 (IN_IGNORED | IN_DELETE_SELF | IN_MOVE_SELF | IN_UNMOUNT)) !=
                0U) {
                ++state_->snapshot.invalidations;
                rebuild_requested = true;
            }
            if ((event->mask & IN_ISDIR) != 0U &&
                (event->mask &
                 (IN_CREATE | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO)) !=
                    0U) {
                observation.watch_topology_changed = true;
                rebuild_requested = true;
            }
            offset += record_size;
        }
        if (stop_drain) break;
    }

    if (observation.event_count != 0U) {
        state_->snapshot.events_observed += observation.event_count;
    }
    if (observation.kernel_queue_overflow) {
        ++state_->snapshot.kernel_queue_overflows;
    }
    if (observation.observation_budget_exhausted) {
        ++state_->snapshot.observation_budget_exhaustions;
    }
    if (observation.wake_observed) {
        ++state_->snapshot.wake_observations;
    }
    if (rebuild_requested && state_->descriptor >= 0) {
        observation.watch_set_rebuilt = state_->rebuild();
    }

    observation.watch_count = state_->snapshot.watch_count;
    if (!observation.diagnostic.has_value()) {
        observation.diagnostic = state_->snapshot.diagnostic;
    }
    return observation;
#endif
}

}  // namespace anonsync

#endif
