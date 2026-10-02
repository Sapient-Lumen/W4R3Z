#include "iotox/sync_source_watch.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <limits>
#include <set>
#include <system_error>
#include <unordered_map>
#include <utility>

#ifdef __linux__
#include <sys/inotify.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace iotox::sync {
namespace {

#ifdef __linux__
constexpr std::uint32_t kWatchMask =
    IN_ATTRIB | IN_CLOSE_WRITE | IN_CREATE | IN_DELETE | IN_DELETE_SELF |
    IN_MODIFY | IN_MOVE_SELF | IN_MOVED_FROM | IN_MOVED_TO;

class FileDescriptor final {
public:
  explicit FileDescriptor(int value = -1) noexcept : value_(value) {}
  ~FileDescriptor() {
    if (value_ >= 0)
      static_cast<void>(::close(value_));
  }

  FileDescriptor(const FileDescriptor &) = delete;
  FileDescriptor &operator=(const FileDescriptor &) = delete;

  FileDescriptor(FileDescriptor &&other) noexcept : value_(other.value_) {
    other.value_ = -1;
  }

  FileDescriptor &operator=(FileDescriptor &&other) noexcept {
    if (this != &other) {
      if (value_ >= 0)
        static_cast<void>(::close(value_));
      value_ = other.value_;
      other.value_ = -1;
    }
    return *this;
  }

  [[nodiscard]] int get() const noexcept { return value_; }
  [[nodiscard]] bool valid() const noexcept { return value_ >= 0; }

private:
  int value_{-1};
};

[[nodiscard]] bool directory_not_symlink(const std::filesystem::path &path) {
  struct stat metadata {};
  return ::lstat(path.c_str(), &metadata) == 0 &&
         S_ISDIR(metadata.st_mode) && !S_ISLNK(metadata.st_mode);
}

[[nodiscard]] bool regular_file_not_symlink(
    const std::filesystem::path &path) {
  struct stat metadata {};
  return ::lstat(path.c_str(), &metadata) == 0 &&
         S_ISREG(metadata.st_mode) && !S_ISLNK(metadata.st_mode);
}

[[nodiscard]] std::filesystem::path watch_anchor_for(
    const std::filesystem::path &source) {
  if (directory_not_symlink(source))
    return source;
  if (regular_file_not_symlink(source))
    return source.parent_path();
  return {};
}
#endif

} // namespace

struct SyncSourceWatchSet::Impl {
#ifdef __linux__
  struct Watch {
    std::filesystem::path path;
    std::vector<std::string> namespaces;
  };

  FileDescriptor descriptor;
  std::unordered_map<int, Watch> watches;
  std::vector<SyncSourceWatchRoot> roots;
#endif
  std::uint64_t events_seen{0U};
  std::uint64_t overflow_events{0U};
  ErrorCode last_error{ErrorCode::ok};
};

SyncSourceWatchSet::SyncSourceWatchSet() : impl_(std::make_unique<Impl>()) {}

SyncSourceWatchSet::~SyncSourceWatchSet() = default;

Status SyncSourceWatchSet::replace(
    std::span<const SyncSourceWatchRoot> roots) {
  if (roots.size() > kMaximumNamespaces) {
    return Status{ErrorCode::resource_exhausted,
                  "sync source watch root bound is exhausted"};
  }
  for (const SyncSourceWatchRoot &root : roots) {
    if (!valid_namespace_id(root.namespace_id) ||
        root.source_path.empty() || !root.source_path.is_absolute() ||
        root.source_path == root.source_path.root_path()) {
      return Status{ErrorCode::invalid_argument,
                    "sync source watch root is invalid"};
    }
  }

#ifndef __linux__
  auto next = std::make_unique<Impl>();
  next->last_error = roots.empty() ? ErrorCode::ok : ErrorCode::unsupported;
  impl_ = std::move(next);
  return roots.empty()
             ? Status::success()
             : Status{ErrorCode::unsupported,
                      "native sync source watch requires Linux inotify"};
#else
  auto next = std::make_unique<Impl>();
  next->roots.assign(roots.begin(), roots.end());
  if (roots.empty()) {
    impl_ = std::move(next);
    return Status::success();
  }

  next->descriptor =
      FileDescriptor(::inotify_init1(IN_NONBLOCK | IN_CLOEXEC));
  if (!next->descriptor.valid()) {
    next->last_error = errno == ENOSYS ? ErrorCode::unsupported
                                       : ErrorCode::unavailable;
    impl_ = std::move(next);
    return Status{next->last_error,
                  "unable to construct sync source watch: " +
                      std::string(std::strerror(errno))};
  }

  const auto add_watch =
      [&next](const std::filesystem::path &path,
              const std::vector<std::string> &namespaces) -> Status {
    if (next->watches.size() >= kMaximumSyncSourceWatchDirectories) {
      next->last_error = ErrorCode::resource_exhausted;
      return Status{
          ErrorCode::resource_exhausted,
          "sync source watch directory bound is exhausted"};
    }
    const int watch =
        ::inotify_add_watch(next->descriptor.get(), path.c_str(), kWatchMask);
    if (watch < 0) {
      next->last_error = errno == ENOSPC ? ErrorCode::resource_exhausted
                                         : ErrorCode::io_error;
      return Status{next->last_error,
                    "unable to add sync source watch: " +
                        std::string(std::strerror(errno))};
    }
    auto &entry = next->watches[watch];
    entry.path = path;
    entry.namespaces.insert(entry.namespaces.end(), namespaces.begin(),
                            namespaces.end());
    std::sort(entry.namespaces.begin(), entry.namespaces.end());
    entry.namespaces.erase(
        std::unique(entry.namespaces.begin(), entry.namespaces.end()),
        entry.namespaces.end());
    return Status::success();
  };

  const auto add_tree =
      [&add_watch](const std::filesystem::path &path,
                   const std::vector<std::string> &namespaces) -> Status {
    const Status watched = add_watch(path, namespaces);
    if (!watched.ok())
      return watched;
    std::error_code error;
    std::filesystem::recursive_directory_iterator iterator(
        path, std::filesystem::directory_options::skip_permission_denied,
        error);
    const std::filesystem::recursive_directory_iterator end;
    for (; !error && iterator != end; iterator.increment(error)) {
      const std::filesystem::path child = iterator->path();
      std::error_code status_error;
      const auto status = iterator->symlink_status(status_error);
      if (status_error || std::filesystem::is_symlink(status) ||
          !std::filesystem::is_directory(status)) {
        if (std::filesystem::is_symlink(status) ||
            !std::filesystem::is_directory(status))
          iterator.disable_recursion_pending();
        continue;
      }
      const Status child_watched = add_watch(child, namespaces);
      if (!child_watched.ok())
        return child_watched;
    }
    if (error) {
      return Status{ErrorCode::io_error,
                    "unable to enumerate sync source tree: " +
                        error.message()};
    }
    return Status::success();
  };

  std::set<std::pair<std::filesystem::path, std::string>> seen;
  for (const SyncSourceWatchRoot &root : roots) {
    const std::filesystem::path anchor = watch_anchor_for(root.source_path);
    if (anchor.empty()) {
      next->last_error = ErrorCode::not_found;
      continue;
    }
    if (!seen.insert({anchor, root.namespace_id}).second)
      continue;
    const Status watched = add_tree(anchor, {root.namespace_id});
    if (!watched.ok()) {
      impl_ = std::move(next);
      return watched;
    }
  }
  impl_ = std::move(next);
  return Status::success();
#endif
}

Result<std::vector<std::string>> SyncSourceWatchSet::drain() {
  std::vector<std::string> dirty;
#ifndef __linux__
  return dirty;
#else
  if (!impl_ || !impl_->descriptor.valid())
    return dirty;

  const auto mark_dirty = [&dirty](const std::vector<std::string> &namespaces) {
    dirty.insert(dirty.end(), namespaces.begin(), namespaces.end());
  };

  bool rebuild_requested = false;
  for (;;) {
    alignas(::inotify_event) std::array<char, 8192U> buffer{};
    const ssize_t bytes =
        ::read(impl_->descriptor.get(), buffer.data(), buffer.size());
    if (bytes < 0) {
      if (errno == EAGAIN || errno == EWOULDBLOCK)
        break;
      if (errno == EINTR)
        continue;
      impl_->last_error = ErrorCode::io_error;
      return Status{ErrorCode::io_error,
                    "unable to read sync source watch: " +
                        std::string(std::strerror(errno))};
    }
    if (bytes == 0)
      break;

    std::size_t offset = 0U;
    while (offset < static_cast<std::size_t>(bytes)) {
      const auto *event = reinterpret_cast<const ::inotify_event *>(
          buffer.data() + static_cast<std::ptrdiff_t>(offset));
      ++impl_->events_seen;
      if ((event->mask & IN_Q_OVERFLOW) != 0U) {
        ++impl_->overflow_events;
        impl_->last_error = ErrorCode::resource_exhausted;
        for (const SyncSourceWatchRoot &root : impl_->roots)
          dirty.push_back(root.namespace_id);
      } else if (const auto found = impl_->watches.find(event->wd);
                 found != impl_->watches.end()) {
        mark_dirty(found->second.namespaces);
        if ((event->mask & (IN_CREATE | IN_MOVED_TO)) != 0U &&
            (event->mask & IN_ISDIR) != 0U && event->len > 0U &&
            event->name[0] != '\0') {
          const std::filesystem::path child =
              found->second.path / std::string(event->name);
          if (directory_not_symlink(child)) {
            rebuild_requested = true;
            mark_dirty(found->second.namespaces);
          }
        }
      }
      offset += sizeof(::inotify_event) + event->len;
    }
  }
  if (rebuild_requested) {
    const std::uint64_t events_seen = impl_->events_seen;
    const std::uint64_t overflow_events = impl_->overflow_events;
    const ErrorCode last_error = impl_->last_error;
    const auto roots = impl_->roots;
    const Status rebuilt = replace(roots);
    if (rebuilt.ok()) {
      impl_->events_seen = events_seen;
      impl_->overflow_events = overflow_events;
      impl_->last_error = last_error;
    }
  }
  std::sort(dirty.begin(), dirty.end());
  dirty.erase(std::unique(dirty.begin(), dirty.end()), dirty.end());
  return dirty;
#endif
}

SyncSourceWatchSnapshot SyncSourceWatchSet::snapshot() const {
  SyncSourceWatchSnapshot snapshot;
  if (!impl_)
    return snapshot;
  snapshot.events_seen = impl_->events_seen;
  snapshot.overflow_events = impl_->overflow_events;
  snapshot.last_error = impl_->last_error;
#ifdef __linux__
  snapshot.configured_roots = impl_->roots.size();
  snapshot.active_watches = impl_->watches.size();
#endif
  return snapshot;
}

} // namespace iotox::sync
