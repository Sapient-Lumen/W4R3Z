#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace iotox::sync {

inline constexpr std::size_t kMaximumSyncSourceWatchDirectories = 4096U;

struct SyncSourceWatchRoot {
  std::string namespace_id;
  std::filesystem::path source_path;
};

struct SyncSourceWatchSnapshot {
  std::size_t configured_roots{0U};
  std::size_t active_watches{0U};
  std::uint64_t events_seen{0U};
  std::uint64_t overflow_events{0U};
  ErrorCode last_error{ErrorCode::ok};
};

// Best-effort native filesystem watcher for synchronization source trees.
//
// This is intentionally not part of the signed sync policy. It is only a
// latency accelerator: callers still keep their periodic scan/retry loop as
// the source of truth. Linux uses inotify with bounded recursive directory
// watches; other platforms report unsupported from replace().
class SyncSourceWatchSet final {
public:
  SyncSourceWatchSet();
  ~SyncSourceWatchSet();

  SyncSourceWatchSet(const SyncSourceWatchSet &) = delete;
  SyncSourceWatchSet &operator=(const SyncSourceWatchSet &) = delete;

  [[nodiscard]] Status replace(std::span<const SyncSourceWatchRoot> roots);
  [[nodiscard]] Result<std::vector<std::string>> drain();
  [[nodiscard]] SyncSourceWatchSnapshot snapshot() const;

private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};

} // namespace iotox::sync
