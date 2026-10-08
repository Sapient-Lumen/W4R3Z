#include "sync_replica_folder_wake.hpp"

#if !defined(_WIN32)

#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;

static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFolderWakeOwner>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncReplicaFolderWakeOwner>);

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/anonsync-folder-wake-test-XXXXXX";
        std::vector<char> writable(pattern.begin(), pattern.end());
        writable.push_back('\0');
        char* selected = ::mkdtemp(writable.data());
        if (selected == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = selected;
        if (::chmod(path_.c_str(), 0700U) != 0) {
            throw std::runtime_error("temporary directory chmod failed");
        }
    }

    ~TemporaryDirectory() noexcept {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void write_bytes(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("could not open wake fixture");
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("could not write wake fixture");
}

template <typename Predicate>
anonsync::SyncReplicaFolderWakeObservation wait_for_observation(
    anonsync::SyncReplicaFolderWakeOwner& owner,
    Predicate&& predicate,
    std::string_view label,
    std::chrono::milliseconds timeout = 2000ms) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    anonsync::SyncReplicaFolderWakeObservation last;
    while (std::chrono::steady_clock::now() < deadline) {
        last = owner.observe_or_throw();
        if (predicate(last)) return last;
        std::this_thread::sleep_for(5ms);
    }
    throw std::runtime_error(
        std::string(label) + " was not observed before its deadline");
}

void test_recursive_wake_and_rebuild() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path() / "root";
    fs::create_directories(root / "nested" / "deeper");

    anonsync::SyncReplicaFolderWakeLimits limits;
    limits.retry_milliseconds = 20U;
    anonsync::SyncReplicaFolderWakeOwner owner(
        fs::absolute(root), limits, "recursive folder wake test");
    const auto initial = owner.snapshot();
#if defined(__linux__)
    require(initial.platform_supported, "Linux wake source must be supported");
    require(initial.active, "initial inotify source must be active");
    require(initial.complete, "small initial watch tree must be complete");
    require(initial.watch_count == 3U,
            "root and two nested directories must each own one watch");
    require(initial.rebuilds == 1U,
            "construction must build one initial watch set");
    require(!owner.observe_or_throw().wake_observed,
            "an idle watch set must not manufacture a wake");

    write_bytes(root / "alpha.txt", "alpha");
    const auto created = wait_for_observation(
        owner,
        [](const auto& observation) { return observation.wake_observed; },
        "root file creation wake");
    require(created.event_count != 0U,
            "file creation must retain a bounded event count");
    require(!created.kernel_queue_overflow,
            "ordinary file creation must not report kernel overflow");

    fs::create_directories(root / "new" / "branch");
    write_bytes(root / "new" / "branch" / "payload.txt", "payload");
    const auto topology = wait_for_observation(
        owner,
        [](const auto& observation) {
            return observation.wake_observed &&
                observation.watch_topology_changed;
        },
        "nested directory topology wake");
    require(topology.watch_set_rebuilt,
            "directory topology change must rebuild the recursive watch set");
    require(owner.snapshot().watch_count == 5U,
            "rebuilt watch set must cover the new nested directory chain");

    write_bytes(root / "new" / "branch" / "payload.txt", "revision");
    const auto nested_edit = wait_for_observation(
        owner,
        [](const auto& observation) { return observation.wake_observed; },
        "nested file edit wake");
    require(nested_edit.event_count != 0U,
            "newly watched nested file edit must wake the owner");

    std::error_code symlink_error;
    fs::create_directory_symlink(
        root / "nested", root / "directory-link", symlink_error);
    if (symlink_error) {
        throw std::runtime_error(
            "directory symlink fixture failed: " + symlink_error.message());
    }
    (void)wait_for_observation(
        owner,
        [](const auto& observation) { return observation.wake_observed; },
        "directory symlink wake");
    require(owner.snapshot().watch_count == 5U,
            "recursive watch rebuild must never follow a directory symlink");

    const auto snapshot = owner.snapshot();
    require(snapshot.wake_observations >= 4U,
            "cumulative snapshot must count observed wake batches");
    require(snapshot.events_observed >= 4U,
            "cumulative snapshot must count bounded events");
    require(snapshot.invalidations == 0U,
            "ordinary changes must not invalidate the root watch");
#else
    require(!initial.platform_supported,
            "non-Linux build must report an unsupported wake source");
    require(!initial.active,
            "unsupported wake source must remain inactive");
#endif
}

void test_bounded_event_drain_and_watch_count() {
#if defined(__linux__)
    TemporaryDirectory temporary;
    const fs::path budget_root = temporary.path() / "budget-root";
    fs::create_directory(budget_root);
    anonsync::SyncReplicaFolderWakeLimits budget_limits;
    budget_limits.maximum_events_per_observation = 1U;
    budget_limits.retry_milliseconds = 20U;
    anonsync::SyncReplicaFolderWakeOwner budget_owner(
        fs::absolute(budget_root), budget_limits,
        "bounded event drain test");
    for (int index = 0; index < 12; ++index) {
        write_bytes(
            budget_root / ("file-" + std::to_string(index)), "x");
    }
    const auto bounded = wait_for_observation(
        budget_owner,
        [](const auto& observation) {
            return observation.observation_budget_exhausted;
        },
        "bounded event observation exhaustion");
    require(bounded.wake_observed,
            "event budget exhaustion must still request one repair pass");
    require(bounded.event_count == 1U,
            "event observation must stop at its exact configured bound");
    require(bounded.watch_set_rebuilt,
            "discarded event suffix must rebuild the hint watch set");
    require(
        budget_owner.snapshot().observation_budget_exhaustions == 1U,
        "bounded event exhaustion must remain visible in status");

    const fs::path watch_root = temporary.path() / "watch-root";
    fs::create_directories(watch_root / "a" / "b" / "c" / "d");
    anonsync::SyncReplicaFolderWakeLimits watch_limits;
    watch_limits.maximum_watches = 2U;
    anonsync::SyncReplicaFolderWakeOwner watch_owner(
        fs::absolute(watch_root), watch_limits,
        "bounded watch count test");
    const auto limited = watch_owner.snapshot();
    require(limited.active,
            "partial recursive coverage must keep the root wake source active");
    require(!limited.complete,
            "watch-count truncation must be reported as incomplete");
    require(limited.watch_count <= 2U,
            "watch descriptor ownership must never exceed its bound");
    require(limited.watch_limit_hits == 1U,
            "watch-count truncation must remain visible in status");
    require(limited.diagnostic.has_value(),
            "incomplete watch coverage must expose a diagnostic");
#endif
}

void test_root_invalidation_and_retry() {
#if defined(__linux__)
    TemporaryDirectory temporary;
    const fs::path root = temporary.path() / "root";
    const fs::path moved = temporary.path() / "moved";
    fs::create_directory(root);
    anonsync::SyncReplicaFolderWakeLimits limits;
    limits.retry_milliseconds = 20U;
    anonsync::SyncReplicaFolderWakeOwner owner(
        fs::absolute(root), limits, "root invalidation test");

    fs::rename(root, moved);
    (void)wait_for_observation(
        owner,
        [&](const auto& observation) {
            return observation.wake_observed && !owner.snapshot().active;
        },
        "moved root invalidation");
    require(owner.snapshot().invalidations >= 1U,
            "root move must be counted as a watch invalidation");
    require(owner.snapshot().diagnostic.has_value(),
            "unavailable configured root must remain diagnosable");

    fs::rename(moved, root);
    const auto recovered = wait_for_observation(
        owner,
        [&](const auto& observation) {
            return observation.watch_set_rebuilt &&
                owner.snapshot().active;
        },
        "configured root watch recovery");
    require(recovered.wake_observed,
            "watch recovery must request a scan for events missed while absent");
    require(owner.snapshot().complete,
            "restored small root must regain complete watch coverage");
#endif
}

void test_validation() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path() / "root";
    fs::create_directory(root);
    require_throws(
        [&] {
            anonsync::SyncReplicaFolderWakeOwner owner(
                fs::path("relative"), {}, "relative wake root");
        },
        "relative wake roots must be rejected");
    require_throws(
        [&] {
            anonsync::SyncReplicaFolderWakeLimits limits;
            limits.maximum_watches = 0U;
            anonsync::SyncReplicaFolderWakeOwner owner(
                fs::absolute(root), limits, "zero watch bound");
        },
        "zero watch bounds must be rejected");
    require_throws(
        [&] {
            anonsync::SyncReplicaFolderWakeLimits limits;
            limits.maximum_events_per_observation = 0U;
            anonsync::SyncReplicaFolderWakeOwner owner(
                fs::absolute(root), limits, "zero event bound");
        },
        "zero event bounds must be rejected");
}

}  // namespace

int main() {
    try {
        test_recursive_wake_and_rebuild();
        test_bounded_event_drain_and_watch_count();
        test_root_invalidation_and_retry();
        test_validation();
        std::cout << "sync_replica_folder_wake_test: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync_replica_folder_wake_test failed after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}

#endif
