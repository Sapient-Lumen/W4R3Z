#include "iotox/sync_digest.hpp"

#include "toxsync/hash.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <span>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

class UniqueFd {
public:
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() {
    if (descriptor_ < 0)
      return;
    int result = -1;
    do {
      result = ::close(descriptor_);
    } while (result != 0 && errno == EINTR);
  }

  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;

  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept { return descriptor_ >= 0; }

private:
  int descriptor_{-1};
};

[[nodiscard]] Status io_status(std::string operation, const std::filesystem::path &path) {
  operation += " '" + path.string() + "': ";
  operation += std::strerror(errno);
  return Status{ErrorCode::io_error, std::move(operation)};
}

[[nodiscard]] bool same_snapshot(const struct stat &left, const struct stat &right) noexcept {
  return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
         left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
         left.st_uid == right.st_uid && left.st_size == right.st_size &&
         left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
         left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
         left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
         left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

} // namespace

Result<Digest> hash_sync_file_sha256(const std::filesystem::path &path) {
  if (path.empty() || !path.is_absolute()) {
    return Status{ErrorCode::invalid_argument, "sync hash path must be absolute"};
  }
  UniqueFd descriptor(::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!descriptor) {
    if (errno == ELOOP)
      return Status{ErrorCode::protocol_error, "sync hash source must not be a symbolic link"};
    return io_status("unable to open sync hash source", path);
  }
  struct stat before{};
  if (::fstat(descriptor.get(), &before) != 0)
    return io_status("unable to inspect sync hash source", path);
  if (!S_ISREG(before.st_mode) || before.st_size < 0) {
    return Status{ErrorCode::invalid_argument,
                  "sync hash source is not a regular file: " + path.string()};
  }

  toxsync::Sha256 hasher;
  std::array<std::byte, 64U * 1024U> buffer{};
  std::uint64_t observed = 0U;
  while (true) {
    const ssize_t count = ::read(descriptor.get(), buffer.data(), buffer.size());
    if (count < 0) {
      if (errno == EINTR)
        continue;
      return io_status("unable to read sync hash source", path);
    }
    if (count == 0)
      break;
    const auto bytes = static_cast<std::size_t>(count);
    if (observed > std::numeric_limits<std::uint64_t>::max() - bytes) {
      return Status{ErrorCode::resource_exhausted, "sync hash byte count overflow"};
    }
    observed += bytes;
    hasher.update(std::span<const std::byte>(buffer.data(), bytes));
  }

  struct stat after{};
  if (::fstat(descriptor.get(), &after) != 0)
    return io_status("unable to revalidate sync hash source", path);
  if (!same_snapshot(before, after) || observed != static_cast<std::uint64_t>(before.st_size)) {
    return Status{ErrorCode::protocol_error, "sync hash source changed while it was read"};
  }
  const toxsync::Digest256 source = hasher.finish();
  Digest digest{};
  for (std::size_t index = 0U; index < digest.size(); ++index)
    digest[index] = std::to_integer<std::uint8_t>(source.bytes[index]);
  return digest;
}

} // namespace iotox::sync
