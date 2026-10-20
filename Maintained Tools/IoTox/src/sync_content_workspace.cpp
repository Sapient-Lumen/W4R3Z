#include "iotox/sync_content_workspace.hpp"

#include "iotox/security/random.hpp"
#include "iotox/sync_content.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iomanip>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace iotox::sync {
namespace {

std::string_view
class_directory(SyncContentWorkspaceClass workspace_class) noexcept {
  if (workspace_class == SyncContentWorkspaceClass::publication)
    return "publications";
  if (workspace_class == SyncContentWorkspaceClass::reconstruction)
    return "reconstructions";
  return {};
}

bool workspace_name(std::string_view name) noexcept {
  if (name.size() != 22U || !name.starts_with("local-"))
    return false;
  return std::all_of(name.begin() + 6, name.end(), [](char value) {
    return (value >= '0' && value <= '9') || (value >= 'a' && value <= 'f');
  });
}

Result<std::uint64_t> namespace_device(const NamespacePolicy &policy) {
  struct stat metadata {};
  if (::lstat(policy.root.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "content namespace root is not private and owner-owned"};
  }
  return static_cast<std::uint64_t>(metadata.st_dev);
}

Status inspect_directory(const std::filesystem::path &path,
                         std::uint64_t expected_device) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
      S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      static_cast<std::uint64_t>(metadata.st_dev) != expected_device ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  "content workspace directory is not private and owner-owned"};
  }
  return Status::success();
}

Status ensure_private_directory(const std::filesystem::path &path,
                                std::uint64_t expected_device) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) == 0)
    return inspect_directory(path, expected_device);
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect content workspace directory: " +
                      std::string(std::strerror(errno))};
  }
  std::error_code error;
  std::filesystem::create_directory(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create content workspace directory: " +
                      error.message()};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure content workspace directory: " +
                      error.message()};
  }
  return inspect_directory(path, expected_device);
}

Status sync_directory(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
  if (descriptor < 0) {
    return Status{ErrorCode::io_error,
                  "unable to open content workspace directory for sync: " +
                      std::string(std::strerror(errno))};
  }
  const int result = ::fsync(descriptor);
  const int saved = errno;
  static_cast<void>(::close(descriptor));
  if (result != 0) {
    return Status{ErrorCode::io_error,
                  "unable to sync content workspace directory: " +
                      std::string(std::strerror(saved))};
  }
  return Status::success();
}

Result<std::filesystem::path>
workspace_parent(const NamespacePolicy &policy,
                 const SyncNamespaceTransaction &transaction,
                 SyncContentWorkspaceClass workspace_class, bool create) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  const std::string_view directory = class_directory(workspace_class);
  if (directory.empty()) {
    return Status{ErrorCode::invalid_argument,
                  "content workspace class is invalid"};
  }
  auto device = namespace_device(policy);
  if (!device)
    return device.status();
  const std::filesystem::path parent =
      sync_content_staging_root(policy) / directory;
  if (create) {
    const Status prepared = ensure_private_directory(parent, device.value());
    if (!prepared.ok())
      return prepared;
  }
  return parent;
}

} // namespace

Result<std::filesystem::path>
create_sync_content_workspace(const NamespacePolicy &policy,
                              const SyncNamespaceTransaction &transaction,
                              SyncContentWorkspaceClass workspace_class) {
  auto parent = workspace_parent(policy, transaction, workspace_class, true);
  if (!parent)
    return parent.status();
  auto device = namespace_device(policy);
  if (!device)
    return device.status();
  for (std::size_t attempt = 0U; attempt < 8U; ++attempt) {
    auto random = security::random_u64_nonzero();
    if (!random)
      return random.status();
    std::ostringstream name;
    name << "local-" << std::hex << std::nouppercase << std::setfill('0')
         << std::setw(16) << random.value();
    const std::filesystem::path workspace = parent.value() / name.str();
    if (::mkdir(workspace.c_str(), static_cast<mode_t>(0700)) == 0) {
      const Status valid = inspect_directory(workspace, device.value());
      return valid.ok() ? Result<std::filesystem::path>{workspace}
                        : Result<std::filesystem::path>{valid};
    }
    if (errno != EEXIST) {
      return Status{ErrorCode::io_error,
                    "unable to create content workspace: " +
                        std::string(std::strerror(errno))};
    }
  }
  return Status{ErrorCode::resource_exhausted,
                "unable to allocate a unique content workspace"};
}

Status
remove_sync_content_workspace(const NamespacePolicy &policy,
                              const SyncNamespaceTransaction &transaction,
                              SyncContentWorkspaceClass workspace_class,
                              const std::filesystem::path &workspace) {
  auto parent = workspace_parent(policy, transaction, workspace_class, false);
  if (!parent)
    return parent.status();
  if (workspace.empty() || !workspace.is_absolute() ||
      workspace.lexically_normal() != workspace ||
      workspace.parent_path() != parent.value() ||
      !workspace_name(workspace.filename().string())) {
    return Status{ErrorCode::invalid_argument,
                  "content workspace path is not exact"};
  }
  struct stat metadata {};
  if (::lstat(workspace.c_str(), &metadata) != 0) {
    return errno == ENOENT ? Status::success()
                           : Status{ErrorCode::io_error,
                                    "unable to inspect content workspace: " +
                                        std::string(std::strerror(errno))};
  }
  auto device = namespace_device(policy);
  if (!device)
    return device.status();
  const Status valid = inspect_directory(workspace, device.value());
  if (!valid.ok())
    return valid;
  std::error_code error;
  static_cast<void>(std::filesystem::remove_all(workspace, error));
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to remove content workspace: " + error.message()};
  }
  return sync_directory(parent.value());
}

Result<std::size_t>
cleanup_sync_content_workspaces(const NamespacePolicy &policy,
                                const SyncNamespaceTransaction &transaction,
                                SyncContentWorkspaceClass workspace_class) {
  auto parent = workspace_parent(policy, transaction, workspace_class, false);
  if (!parent)
    return parent.status();
  struct stat metadata {};
  if (::lstat(parent.value().c_str(), &metadata) != 0) {
    if (errno == ENOENT)
      return 0U;
    return Status{ErrorCode::io_error,
                  "unable to inspect content workspace staging: " +
                      std::string(std::strerror(errno))};
  }
  auto device = namespace_device(policy);
  if (!device)
    return device.status();
  const Status valid = inspect_directory(parent.value(), device.value());
  if (!valid.ok())
    return valid;
  std::error_code error;
  std::vector<std::filesystem::path> abandoned;
  for (std::filesystem::directory_iterator iterator(parent.value(), error), end;
       !error && iterator != end; iterator.increment(error)) {
    if (!workspace_name(iterator->path().filename().string())) {
      return Status{ErrorCode::protocol_error,
                    "content workspace staging has an unexpected entry"};
    }
    const Status child = inspect_directory(iterator->path(), device.value());
    if (!child.ok())
      return child;
    abandoned.push_back(iterator->path());
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate content workspace staging: " +
                      error.message()};
  }
  for (const std::filesystem::path &path : abandoned) {
    static_cast<void>(std::filesystem::remove_all(path, error));
    if (error) {
      return Status{ErrorCode::io_error,
                    "unable to remove abandoned content workspace: " +
                        error.message()};
    }
  }
  if (!abandoned.empty()) {
    const Status synced = sync_directory(parent.value());
    if (!synced.ok())
      return synced;
  }
  return abandoned.size();
}

} // namespace iotox::sync
