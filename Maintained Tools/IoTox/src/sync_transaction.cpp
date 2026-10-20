#include "iotox/sync_transaction.hpp"

#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

[[nodiscard]] Status ensure_private_directory(
    const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create sync transaction directory: " +
                      error.message()};
  }
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 ||
      !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "sync transaction directory is not real and owner-owned"};
  }
  std::filesystem::permissions(path, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure sync transaction directory: " +
                      error.message()};
  }
  return Status::success();
}

} // namespace

SyncNamespaceTransaction::SyncNamespaceTransaction(
    std::filesystem::path root, std::string namespace_id, int descriptor,
    int root_descriptor, std::uint64_t root_device, std::uint64_t root_inode)
    : root_(std::move(root)), namespace_id_(std::move(namespace_id)),
      owner_process_(::getpid()),
      owner_thread_(std::this_thread::get_id()),
      descriptor_(descriptor), root_descriptor_(root_descriptor),
      root_device_(root_device), root_inode_(root_inode) {}

SyncNamespaceTransaction::~SyncNamespaceTransaction() {
  if (descriptor_ >= 0)
    static_cast<void>(::close(descriptor_));
  if (root_descriptor_ >= 0)
    static_cast<void>(::close(root_descriptor_));
}

SyncNamespaceTransaction::SyncNamespaceTransaction(
    SyncNamespaceTransaction &&other) noexcept
    : root_(std::move(other.root_)),
      namespace_id_(std::move(other.namespace_id_)),
      owner_process_(other.owner_process_),
      owner_thread_(other.owner_thread_),
      descriptor_(std::exchange(other.descriptor_, -1)),
      root_descriptor_(std::exchange(other.root_descriptor_, -1)),
      root_device_(other.root_device_), root_inode_(other.root_inode_) {}

SyncNamespaceTransaction &SyncNamespaceTransaction::operator=(
    SyncNamespaceTransaction &&other) noexcept {
  if (this != &other) {
    if (descriptor_ >= 0)
      static_cast<void>(::close(descriptor_));
    if (root_descriptor_ >= 0)
      static_cast<void>(::close(root_descriptor_));
    root_ = std::move(other.root_);
    namespace_id_ = std::move(other.namespace_id_);
    owner_process_ = other.owner_process_;
    owner_thread_ = other.owner_thread_;
    descriptor_ = std::exchange(other.descriptor_, -1);
    root_descriptor_ = std::exchange(other.root_descriptor_, -1);
    root_device_ = other.root_device_;
    root_inode_ = other.root_inode_;
  }
  return *this;
}

Result<SyncNamespaceTransaction>
SyncNamespaceTransaction::acquire(const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  const std::filesystem::path root{policy.root};
  Status prepared = ensure_private_directory(root);
  if (!prepared.ok())
    return prepared;
  const std::filesystem::path directory = root / "transactions";
  prepared = ensure_private_directory(directory);
  if (!prepared.ok())
    return prepared;
  const int root_descriptor =
      ::open(root.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (root_descriptor < 0) {
    return Status{ErrorCode::io_error,
                  "unable to pin sync transaction root: " +
                      std::string(std::strerror(errno))};
  }
  struct stat root_metadata {};
  if (::fstat(root_descriptor, &root_metadata) != 0 ||
      !S_ISDIR(root_metadata.st_mode) || root_metadata.st_uid != ::geteuid() ||
      (root_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync transaction root is not private and owner-owned"};
  }
  const int directory_descriptor =
      ::openat(root_descriptor, "transactions",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (directory_descriptor < 0) {
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::io_error,
                  "unable to pin sync transaction directory: " +
                      std::string(std::strerror(errno))};
  }
  struct stat directory_metadata {};
  if (::fstat(directory_descriptor, &directory_metadata) != 0 ||
      !S_ISDIR(directory_metadata.st_mode) ||
      directory_metadata.st_uid != ::geteuid() ||
      (directory_metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700) ||
      directory_metadata.st_dev != root_metadata.st_dev) {
    static_cast<void>(::close(directory_descriptor));
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync transaction directory crosses its private root"};
  }
  const std::string filename = policy.id + ".transaction.lock";
  const int descriptor =
      ::openat(directory_descriptor, filename.c_str(),
               O_RDWR | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
  if (descriptor < 0) {
    static_cast<void>(::close(directory_descriptor));
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::io_error,
                  "unable to open sync transaction lock: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
      metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
      metadata.st_dev != root_metadata.st_dev ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600)) {
    static_cast<void>(::close(descriptor));
    static_cast<void>(::close(directory_descriptor));
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync transaction lock is not one private owner file"};
  }
  while (::flock(descriptor, LOCK_EX) != 0) {
    if (errno == EINTR)
      continue;
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    static_cast<void>(::close(directory_descriptor));
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::io_error,
                  "unable to acquire sync transaction lock: " +
                      std::string(std::strerror(saved))};
  }
  struct stat path_root_metadata {};
  struct stat path_directory_metadata {};
  struct stat path_lock_metadata {};
  const bool stable =
      ::lstat(root.c_str(), &path_root_metadata) == 0 &&
      path_root_metadata.st_dev == root_metadata.st_dev &&
      path_root_metadata.st_ino == root_metadata.st_ino &&
      ::fstatat(root_descriptor, "transactions", &path_directory_metadata,
                AT_SYMLINK_NOFOLLOW) == 0 &&
      path_directory_metadata.st_dev == directory_metadata.st_dev &&
      path_directory_metadata.st_ino == directory_metadata.st_ino &&
      ::fstatat(directory_descriptor, filename.c_str(), &path_lock_metadata,
                AT_SYMLINK_NOFOLLOW) == 0 &&
      path_lock_metadata.st_dev == metadata.st_dev &&
      path_lock_metadata.st_ino == metadata.st_ino;
  static_cast<void>(::close(directory_descriptor));
  if (!stable) {
    static_cast<void>(::close(descriptor));
    static_cast<void>(::close(root_descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync transaction path changed while acquiring its lock"};
  }
  return SyncNamespaceTransaction{
      root,
      policy.id,
      descriptor,
      root_descriptor,
      static_cast<std::uint64_t>(root_metadata.st_dev),
      static_cast<std::uint64_t>(root_metadata.st_ino)};
}

bool SyncNamespaceTransaction::matches(
    const NamespacePolicy &policy) const noexcept {
  struct stat current_root {};
  return ::lstat(policy.root.c_str(), &current_root) == 0 && descriptor_ >= 0 &&
         namespace_id_ == policy.id && root_descriptor_ >= 0 &&
         root_.lexically_normal().string() == policy.root &&
         owner_process_ == ::getpid() &&
         owner_thread_ == std::this_thread::get_id() &&
         static_cast<std::uint64_t>(current_root.st_dev) == root_device_ &&
         static_cast<std::uint64_t>(current_root.st_ino) == root_inode_;
}

bool SyncNamespaceTransaction::pins_root(std::uint64_t device,
                                         std::uint64_t inode) const noexcept {
  return descriptor_ >= 0 && root_descriptor_ >= 0 &&
         owner_process_ == ::getpid() &&
         owner_thread_ == std::this_thread::get_id() &&
         root_device_ == device && root_inode_ == inode;
}

Status require_sync_transaction(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  if (!transaction.matches(policy)) {
    return Status{ErrorCode::invalid_argument,
                  "sync transaction does not match namespace policy"};
  }
  return Status::success();
}

} // namespace iotox::sync
