#include "iotox/update_service.hpp"

#include "iotox/security/identity.hpp"
#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/memfd.h>
#include <poll.h>
#include <spawn.h>
#include <span>
#include <string>
#include <string_view>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::update {
namespace {

constexpr std::array<std::uint8_t, 8U> kReadyMagic = {
    'I', 'O', 'T', 'O', 'X', 'S', 'R', '1'};
constexpr int kImageDescriptor = 4;
constexpr int kStatusDescriptor = 5;
constexpr int kFirstUnreservedDescriptor = 6;
constexpr std::string_view kInternalMarker =
    "IOTOX_INTERNAL_UPDATE_SERVICE_CHILD=1";
constexpr std::string_view kReadyFdEnvironment =
    "IOTOX_SERVICE_READY_FD=3";

class UniqueFd {
public:
  UniqueFd() = default;
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() { reset(); }
  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;
  UniqueFd(UniqueFd &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  UniqueFd &operator=(UniqueFd &&other) noexcept {
    if (this != &other) {
      reset();
      descriptor_ = std::exchange(other.descriptor_, -1);
    }
    return *this;
  }
  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept {
    return descriptor_ >= 0;
  }
  [[nodiscard]] int release() noexcept {
    return std::exchange(descriptor_, -1);
  }
  void reset(int descriptor = -1) noexcept {
    if (descriptor_ >= 0) {
      int result = -1;
      do {
        result = ::close(descriptor_);
      } while (result != 0 && errno == EINTR);
    }
    descriptor_ = descriptor;
  }

private:
  int descriptor_{-1};
};

class SpawnActions {
public:
  SpawnActions() : error_(::posix_spawn_file_actions_init(&actions_)) {}
  ~SpawnActions() {
    if (error_ == 0) {
      static_cast<void>(::posix_spawn_file_actions_destroy(&actions_));
    }
  }
  SpawnActions(const SpawnActions &) = delete;
  SpawnActions &operator=(const SpawnActions &) = delete;
  [[nodiscard]] int error() const noexcept { return error_; }
  [[nodiscard]] posix_spawn_file_actions_t *get() noexcept {
    return &actions_;
  }

private:
  posix_spawn_file_actions_t actions_{};
  int error_{0};
};

class SpawnAttributes {
public:
  SpawnAttributes() : error_(::posix_spawnattr_init(&attributes_)) {}
  ~SpawnAttributes() {
    if (error_ == 0) {
      static_cast<void>(::posix_spawnattr_destroy(&attributes_));
    }
  }
  SpawnAttributes(const SpawnAttributes &) = delete;
  SpawnAttributes &operator=(const SpawnAttributes &) = delete;
  [[nodiscard]] int error() const noexcept { return error_; }
  [[nodiscard]] posix_spawnattr_t *get() noexcept { return &attributes_; }

private:
  posix_spawnattr_t attributes_{};
  int error_{0};
};

struct ChildFailure {
  std::uint32_t stage{0U};
  std::int32_t error{0};
};

enum class ChildStage : std::uint32_t {
  marker = 1U,
  descriptors = 2U,
  parent_death = 3U,
  no_new_privileges = 4U,
  session = 5U,
  directory = 6U,
  descriptor_hygiene = 7U,
  final_exec = 8U,
};

[[nodiscard]] std::string_view child_stage_name(ChildStage stage) noexcept {
  switch (stage) {
    case ChildStage::marker: return "marker";
    case ChildStage::descriptors: return "descriptor contract";
    case ChildStage::parent_death: return "parent-death contract";
    case ChildStage::no_new_privileges: return "no-new-privileges";
    case ChildStage::session: return "service session";
    case ChildStage::directory: return "working directory";
    case ChildStage::descriptor_hygiene: return "descriptor hygiene";
    case ChildStage::final_exec: return "final fexecve";
  }
  return "unknown";
}

[[nodiscard]] Status errno_status(
    ErrorCode code, std::string operation, int error = errno) {
  return Status{code, std::move(operation) + ": " + std::strerror(error)};
}

[[nodiscard]] Status path_errno_status(
    std::string operation, const std::filesystem::path &path,
    int error = errno) {
  return Status{ErrorCode::io_error,
                std::move(operation) + " '" + path.string() + "': " +
                    std::strerror(error)};
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) noexcept {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> (56U - index * 8U));
  }
}

[[nodiscard]] bool same_snapshot(
    const struct stat &left, const struct stat &right) noexcept {
  return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
      left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
      left.st_uid == right.st_uid && left.st_size == right.st_size &&
      left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
      left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
      left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
      left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

[[nodiscard]] Status write_all(
    int descriptor, std::span<const std::byte> bytes,
    std::string_view label) {
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count = ::write(
        descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    return errno_status(ErrorCode::io_error, std::string(label));
  }
  return Status::success();
}

[[nodiscard]] Result<UniqueFd> duplicate_spawn_source(int descriptor) {
  const int duplicate = ::fcntl(descriptor, F_DUPFD_CLOEXEC, 64);
  if (duplicate < 0) {
    return errno_status(
        ErrorCode::io_error, "duplicate update service spawn descriptor");
  }
  return UniqueFd(duplicate);
}

[[nodiscard]] Result<UniqueFd> open_helper(
    const std::filesystem::path &path) {
  if (path.empty() || !path.is_absolute() ||
      path.lexically_normal() != path) {
    return Status{ErrorCode::invalid_argument,
                  "update service helper must be a normalized absolute path"};
  }
  UniqueFd descriptor(
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
  if (!descriptor) {
    return path_errno_status("unable to open update service helper", path);
  }
  struct stat metadata{};
  if (::fstat(descriptor.get(), &metadata) != 0) {
    return path_errno_status("unable to inspect update service helper", path);
  }
  UniqueFd running(::open("/proc/self/exe", O_RDONLY | O_CLOEXEC));
  struct stat running_metadata{};
  if (!running || ::fstat(running.get(), &running_metadata) != 0) {
    return errno_status(
        ErrorCode::unavailable, "unable to pin running IoTox executable");
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink == 0 ||
      (metadata.st_mode & 0111U) == 0U ||
      (metadata.st_mode & 0022U) != 0U ||
      (metadata.st_mode &
       static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) != 0U ||
      (metadata.st_uid != ::geteuid() && metadata.st_uid != 0U)) {
    return Status{ErrorCode::protocol_error,
                  "update service helper is not an executable regular file"};
  }
  if (metadata.st_dev != running_metadata.st_dev ||
      metadata.st_ino != running_metadata.st_ino) {
    return Status{
        ErrorCode::protocol_error,
        "update service helper is not the exact running IoTox executable"};
  }
  return descriptor;
}

struct SealedImage {
  UniqueFd descriptor;
  std::uint64_t bytes{0U};
};

[[nodiscard]] Result<SealedImage> prepare_image(
    const UpdateSelectedSlot &selected) {
  if (selected.revision.payload_kind != PayloadKind::linux_service_v1 ||
      !selected.revision.present() || selected.path.empty() ||
      !selected.path.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "linux-service-v1 requires one exact selected service slot"};
  }
  UniqueFd source(::open(
      selected.path.c_str(),
      O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!source) {
    return path_errno_status(
        "unable to open selected update service slot", selected.path);
  }
  struct stat before{};
  if (::fstat(source.get(), &before) != 0) {
    return path_errno_status(
        "unable to inspect selected update service slot", selected.path);
  }
  if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
      before.st_uid != ::geteuid() ||
      (before.st_mode & 0777U) != 0400U || before.st_size <= 0 ||
      static_cast<std::uint64_t>(before.st_size) !=
          selected.revision.payload_bytes) {
    return Status{ErrorCode::protocol_error,
                  "selected update service slot shape or size is invalid"};
  }
#ifdef SYS_memfd_create
  const int image_fd = static_cast<int>(::syscall(
      SYS_memfd_create, "iotox-linux-service-v1",
      static_cast<unsigned int>(MFD_CLOEXEC | MFD_ALLOW_SEALING)));
#else
  const int image_fd = -1;
  errno = ENOSYS;
#endif
  UniqueFd image(image_fd);
  if (!image) {
    return errno_status(
        errno == ENOSYS ? ErrorCode::unsupported : ErrorCode::io_error,
        "create sealed update service image");
  }
  if (::fchmod(image.get(), 0700) != 0) {
    return errno_status(
        ErrorCode::io_error, "make update service image executable");
  }

  toxsync::Sha256 hasher;
  std::array<std::byte, 64U * 1024U> buffer{};
  std::uint64_t observed = 0U;
  while (true) {
    const ssize_t count =
        ::read(source.get(), buffer.data(), buffer.size());
    if (count > 0) {
      const std::size_t amount = static_cast<std::size_t>(count);
      if (observed >
          std::numeric_limits<std::uint64_t>::max() - amount) {
        return Status{ErrorCode::resource_exhausted,
                      "update service image byte count overflow"};
      }
      observed += amount;
      if (observed > selected.revision.payload_bytes) {
        return Status{ErrorCode::protocol_error,
                      "selected update service slot grew while copied"};
      }
      hasher.update(std::span<const std::byte>(buffer.data(), amount));
      const Status written = write_all(
          image.get(),
          std::span<const std::byte>(buffer.data(), amount),
          "write sealed update service image");
      if (!written.ok()) return written;
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    if (count < 0) {
      return path_errno_status(
          "unable to read selected update service slot", selected.path);
    }
    break;
  }
  struct stat after{};
  if (::fstat(source.get(), &after) != 0) {
    return path_errno_status(
        "unable to revalidate selected update service slot", selected.path);
  }
  const toxsync::Digest256 digest = hasher.finish();
  sync::Digest observed_digest{};
  for (std::size_t index = 0U; index < observed_digest.size(); ++index) {
    observed_digest[index] =
        std::to_integer<std::uint8_t>(digest.bytes[index]);
  }
  if (!same_snapshot(before, after) ||
      observed != selected.revision.payload_bytes ||
      observed_digest != selected.revision.payload_digest) {
    return Status{ErrorCode::protocol_error,
                  "selected update service slot changed or failed digest verification"};
  }
  if (::fcntl(
          image.get(), F_ADD_SEALS,
          F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL) != 0) {
    return errno_status(
        ErrorCode::unsupported, "seal update service image");
  }
  const int seals = ::fcntl(image.get(), F_GET_SEALS);
  constexpr int required =
      F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
  if (seals < 0 || (seals & required) != required) {
    return Status{ErrorCode::unavailable,
                  "update service image sealing did not converge"};
  }
  if (::lseek(image.get(), 0, SEEK_SET) < 0) {
    return errno_status(
        ErrorCode::io_error, "rewind sealed update service image");
  }
  return SealedImage{std::move(image), observed};
}

[[nodiscard]] Status configure_spawn_actions(
    posix_spawn_file_actions_t *actions, int ready, int status, int image,
    int null_descriptor) {
  for (const auto &[source, destination] : std::array{
           std::pair{ready, kUpdateServiceReadyDescriptor},
           std::pair{image, kImageDescriptor},
           std::pair{status, kStatusDescriptor},
           std::pair{null_descriptor, STDIN_FILENO}}) {
    const int result =
        ::posix_spawn_file_actions_adddup2(actions, source, destination);
    if (result != 0) {
      return errno_status(
          ErrorCode::io_error,
          "configure update service spawn descriptor", result);
    }
  }
  return Status::success();
}

[[nodiscard]] Status configure_spawn_attributes(
    posix_spawnattr_t *attributes) {
  sigset_t empty{};
  sigset_t defaults{};
  if (::sigemptyset(&empty) != 0 || ::sigemptyset(&defaults) != 0) {
    return errno_status(
        ErrorCode::io_error, "initialize update service signal sets");
  }
  for (int signal = 1; signal < NSIG; ++signal) {
    if (signal == SIGKILL || signal == SIGSTOP) continue;
    static_cast<void>(::sigaddset(&defaults, signal));
  }
  int result = ::posix_spawnattr_setsigmask(attributes, &empty);
  if (result == 0) {
    result = ::posix_spawnattr_setsigdefault(attributes, &defaults);
  }
  if (result == 0) {
    result = ::posix_spawnattr_setflags(
        attributes,
        static_cast<short>(
            POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_SETSIGDEF));
  }
  if (result != 0) {
    return errno_status(
        ErrorCode::io_error,
        "configure update service spawn attributes", result);
  }
  return Status::success();
}

[[nodiscard]] Status wait_for_helper_exec(
    int descriptor, std::chrono::milliseconds timeout) {
  const auto deadline = std::chrono::steady_clock::now() + timeout;
  ChildFailure failure{};
  std::size_t offset = 0U;
  while (true) {
    const auto now = std::chrono::steady_clock::now();
    if (now >= deadline) {
      return Status{ErrorCode::timeout,
                    "update service helper startup timed out"};
    }
    const auto remaining =
        std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now);
    pollfd item{descriptor, POLLIN | POLLHUP, 0};
    const int waited = ::poll(
        &item, 1,
        static_cast<int>(std::max<std::int64_t>(
            1, std::min<std::int64_t>(remaining.count(), 100))));
    if (waited < 0 && errno == EINTR) continue;
    if (waited < 0) {
      return errno_status(
          ErrorCode::io_error, "poll update service helper status");
    }
    if (waited == 0) continue;
    const ssize_t count = ::read(
        descriptor,
        reinterpret_cast<std::byte *>(&failure) + offset,
        sizeof(failure) - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      if (offset == sizeof(failure)) {
        return Status{
            ErrorCode::protocol_error,
            "update service helper failed at " +
                std::string(child_stage_name(
                    static_cast<ChildStage>(failure.stage))) +
                ": " + std::strerror(failure.error)};
      }
      continue;
    }
    if (count == 0) {
      return offset == 0U
          ? Status::success()
          : Status{ErrorCode::protocol_error,
                   "update service helper status ended mid-record"};
    }
    if (errno == EINTR) continue;
    return errno_status(
        ErrorCode::io_error, "read update service helper status");
  }
}

[[noreturn]] void child_fail(ChildStage stage, int error) noexcept {
  const ChildFailure failure{
      static_cast<std::uint32_t>(stage),
      static_cast<std::int32_t>(error == 0 ? EPROTO : error)};
  const auto *bytes = reinterpret_cast<const std::byte *>(&failure);
  std::size_t offset = 0U;
  while (offset < sizeof(failure)) {
    const ssize_t count =
        ::write(kStatusDescriptor, bytes + offset, sizeof(failure) - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    break;
  }
  ::_exit(126);
}

[[nodiscard]] bool descriptor_is_pipe(int descriptor) noexcept {
  struct stat metadata{};
  return ::fstat(descriptor, &metadata) == 0 &&
      S_ISFIFO(metadata.st_mode);
}

[[nodiscard]] bool descriptor_is_sealed_image(int descriptor) noexcept {
  struct stat metadata{};
  if (::fstat(descriptor, &metadata) != 0 ||
      !S_ISREG(metadata.st_mode) || metadata.st_size <= 0 ||
      (metadata.st_mode & 0111U) == 0U) {
    return false;
  }
  const int seals = ::fcntl(descriptor, F_GET_SEALS);
  constexpr int required =
      F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
  return seals >= 0 && (seals & required) == required;
}

[[nodiscard]] bool close_ambient_descriptors() noexcept {
#ifdef SYS_close_range
  return ::syscall(
          SYS_close_range,
          static_cast<unsigned int>(kFirstUnreservedDescriptor),
          std::numeric_limits<unsigned int>::max(), 0U) == 0;
#else
  errno = ENOSYS;
  return false;
#endif
}

[[nodiscard]] bool set_close_on_exec(int descriptor) noexcept {
  const int flags = ::fcntl(descriptor, F_GETFD);
  return flags >= 0 &&
      ::fcntl(descriptor, F_SETFD, flags | FD_CLOEXEC) == 0;
}

[[nodiscard]] Status set_nonblocking(int descriptor) {
  const int flags = ::fcntl(descriptor, F_GETFL);
  if (flags < 0 || ::fcntl(descriptor, F_SETFL, flags | O_NONBLOCK) != 0) {
    return errno_status(
        ErrorCode::io_error,
        "make update service readiness channel nonblocking");
  }
  return Status::success();
}

} // namespace

UpdateServiceReadyRecord encode_update_service_ready_record(
    std::uint64_t release_sequence) noexcept {
  UpdateServiceReadyRecord output{};
  std::copy(kReadyMagic.begin(), kReadyMagic.end(), output.begin());
  write_u64(output, 8U, release_sequence);
  return output;
}

std::string_view linux_service_phase_name(
    LinuxServicePhase phase) noexcept {
  switch (phase) {
    case LinuxServicePhase::starting: return "starting";
    case LinuxServicePhase::ready: return "ready";
    case LinuxServicePhase::exited: return "exited";
    case LinuxServicePhase::failed: return "failed";
    case LinuxServicePhase::stopped: return "stopped";
  }
  return "unknown";
}

LinuxServiceAdapter::LinuxServiceAdapter(
    LinuxServiceConfig config, UpdateSelectedSlot slot)
    : config_(std::move(config)), slot_(std::move(slot)) {
  snapshot_.phase = LinuxServicePhase::starting;
  snapshot_.release_sequence = slot_.revision.sequence;
  snapshot_.payload_bytes = slot_.revision.payload_bytes;
  snapshot_.candidate = slot_.candidate;
}

LinuxServiceAdapter::~LinuxServiceAdapter() {
  static_cast<void>(stop());
}

Result<std::unique_ptr<LinuxServiceAdapter>>
LinuxServiceAdapter::start(
    LinuxServiceConfig config, const UpdateSelectedSlot &slot) {
  if (config.helper_startup_timeout.count() <= 0 ||
      config.helper_startup_timeout > std::chrono::seconds(30) ||
      config.readiness_timeout.count() <= 0 ||
      config.readiness_timeout > std::chrono::hours(24) ||
      config.shutdown_timeout.count() <= 0 ||
      config.shutdown_timeout > std::chrono::seconds(30)) {
    return Status{ErrorCode::invalid_argument,
                  "update service timeouts are outside their bounds"};
  }
  auto result = std::unique_ptr<LinuxServiceAdapter>(
      new LinuxServiceAdapter(std::move(config), slot));
  const Status launched = result->launch();
  if (!launched.ok()) return launched;
  return result;
}

Status LinuxServiceAdapter::launch() {
  auto image = prepare_image(slot_);
  if (!image.ok()) return image.status();
  auto helper = open_helper(config_.helper_executable);
  if (!helper.ok()) return helper.status();
  UniqueFd null_descriptor(::open("/dev/null", O_RDONLY | O_CLOEXEC));
  if (!null_descriptor) {
    return errno_status(ErrorCode::io_error, "open update service stdin");
  }
  int ready_pipe[2]{-1, -1};
  int status_pipe[2]{-1, -1};
  if (::pipe2(ready_pipe, O_CLOEXEC) != 0) {
    return errno_status(
        ErrorCode::io_error, "create update service readiness pipe");
  }
  UniqueFd ready_parent(ready_pipe[0]);
  UniqueFd ready_child(ready_pipe[1]);
  if (::pipe2(status_pipe, O_CLOEXEC) != 0) {
    return errno_status(
        ErrorCode::io_error, "create update service status pipe");
  }
  UniqueFd status_parent(status_pipe[0]);
  UniqueFd status_child(status_pipe[1]);
  const Status nonblocking = set_nonblocking(ready_parent.get());
  if (!nonblocking.ok()) return nonblocking;

  auto spawn_ready = duplicate_spawn_source(ready_child.get());
  auto spawn_status = duplicate_spawn_source(status_child.get());
  auto spawn_image = duplicate_spawn_source(image.value().descriptor.get());
  auto spawn_null = duplicate_spawn_source(null_descriptor.get());
  auto spawn_helper = duplicate_spawn_source(helper.value().get());
  if (!spawn_ready.ok()) return spawn_ready.status();
  if (!spawn_status.ok()) return spawn_status.status();
  if (!spawn_image.ok()) return spawn_image.status();
  if (!spawn_null.ok()) return spawn_null.status();
  if (!spawn_helper.ok()) return spawn_helper.status();

  SpawnActions actions;
  if (actions.error() != 0) {
    return errno_status(
        ErrorCode::io_error,
        "initialize update service spawn actions", actions.error());
  }
  const Status configured = configure_spawn_actions(
      actions.get(), spawn_ready.value().get(),
      spawn_status.value().get(), spawn_image.value().get(),
      spawn_null.value().get());
  if (!configured.ok()) return configured;
  SpawnAttributes attributes;
  if (attributes.error() != 0) {
    return errno_status(
        ErrorCode::io_error,
        "initialize update service spawn attributes", attributes.error());
  }
  const Status attributes_configured =
      configure_spawn_attributes(attributes.get());
  if (!attributes_configured.ok()) return attributes_configured;

  const std::string helper_path =
      "/proc/self/fd/" +
      std::to_string(spawn_helper.value().get());
  std::array<std::string, 2U> argument_storage{
      "iotox-update-service-child",
      std::string{kInternalUpdateServiceChildArgument}};
  std::array<char *, 3U> arguments{
      argument_storage[0U].data(), argument_storage[1U].data(), nullptr};
  std::array<std::string, 5U> environment_storage{
      std::string{kInternalMarker},
      std::string{kReadyFdEnvironment},
      "IOTOX_UPDATE_SEQUENCE=" +
          std::to_string(slot_.revision.sequence),
      "IOTOX_UPDATE_VERSION=" + slot_.revision.version,
      "IOTOX_UPDATE_PAYLOAD_DIGEST=" +
          security::hex(slot_.revision.payload_digest)};
  std::array<char *, 6U> environment{};
  for (std::size_t index = 0U; index < environment_storage.size(); ++index) {
    environment[index] = environment_storage[index].data();
  }

  pid_t child = -1;
  const int spawned = ::posix_spawn(
      &child, helper_path.c_str(), actions.get(), attributes.get(),
      arguments.data(), environment.data());
  if (spawned != 0) {
    return errno_status(
        ErrorCode::io_error, "spawn update service helper", spawned);
  }
  spawn_ready.value().reset();
  spawn_status.value().reset();
  spawn_image.value().reset();
  spawn_null.value().reset();
  spawn_helper.value().reset();
  ready_child.reset();
  status_child.reset();
  const auto kill_and_reap = [&]() {
    static_cast<void>(::kill(child, SIGKILL));
    int status = 0;
    while (::waitpid(child, &status, 0) < 0 && errno == EINTR) {
    }
  };
  const Status exec = wait_for_helper_exec(
      status_parent.get(), config_.helper_startup_timeout);
  if (!exec.ok()) {
    kill_and_reap();
    return exec;
  }

  {
    std::scoped_lock lock(mutex_);
    ready_descriptor_ = ready_parent.release();
    child_ = static_cast<std::int64_t>(child);
    readiness_deadline_ =
        std::chrono::steady_clock::now() + config_.readiness_timeout;
    snapshot_.process_id = child_;
    snapshot_.image_sealed = true;
    snapshot_.detail = "sealed image exec admitted; awaiting exact readiness";
  }
  return Status::success();
}

Status LinuxServiceAdapter::poll() {
  std::scoped_lock lock(mutex_);
  return poll_locked();
}

Status LinuxServiceAdapter::poll_locked() {
  if (child_ <= 0 ||
      snapshot_.phase == LinuxServicePhase::exited ||
      snapshot_.phase == LinuxServicePhase::failed ||
      snapshot_.phase == LinuxServicePhase::stopped) {
    return Status::success();
  }
  int status = 0;
  const pid_t waited = ::waitpid(
      static_cast<pid_t>(child_), &status, WNOHANG);
  if (waited < 0 && errno != EINTR) {
    snapshot_.phase = LinuxServicePhase::failed;
    snapshot_.detail = "unable to observe update service child: " +
        std::string(std::strerror(errno));
    return Status{ErrorCode::io_error, snapshot_.detail};
  }
  if (waited == static_cast<pid_t>(child_)) {
    // The helper made the payload a process-group leader. A service that
    // exits must not leave same-group descendants behind after supervision
    // truth becomes terminal.
    static_cast<void>(::kill(-static_cast<pid_t>(child_), SIGKILL));
    if (WIFEXITED(status)) snapshot_.exit_status = WEXITSTATUS(status);
    if (WIFSIGNALED(status)) {
      snapshot_.terminating_signal = WTERMSIG(status);
    }
    child_ = -1;
    snapshot_.process_id = -1;
    if (ready_descriptor_ >= 0) {
      static_cast<void>(::close(ready_descriptor_));
      ready_descriptor_ = -1;
    }
    snapshot_.phase = LinuxServicePhase::exited;
    snapshot_.detail = "update service exited";
    return Status::success();
  }

  if (snapshot_.phase == LinuxServicePhase::starting &&
      ready_descriptor_ >= 0) {
    std::array<std::uint8_t, kUpdateServiceReadyRecordBytes + 1U> bytes{};
    const std::size_t remaining =
        kUpdateServiceReadyRecordBytes - ready_record_bytes_;
    const ssize_t count = ::read(
        ready_descriptor_, bytes.data(), remaining + 1U);
    if (count > 0) {
      const std::size_t amount = static_cast<std::size_t>(count);
      if (amount > remaining) {
        snapshot_.phase = LinuxServicePhase::failed;
        snapshot_.detail =
            "update service emitted a malformed readiness record";
        return terminate_locked(false);
      }
      std::copy_n(
          bytes.begin(), amount,
          ready_record_.begin() +
              static_cast<std::ptrdiff_t>(ready_record_bytes_));
      ready_record_bytes_ += amount;
      if (ready_record_bytes_ == kUpdateServiceReadyRecordBytes) {
        const auto expected =
            encode_update_service_ready_record(slot_.revision.sequence);
        if (ready_record_ != expected) {
          snapshot_.phase = LinuxServicePhase::failed;
          snapshot_.detail =
              "update service emitted a malformed readiness record";
          return terminate_locked(false);
        }
        snapshot_.readiness_record_complete = true;
        snapshot_.phase = LinuxServicePhase::ready;
        snapshot_.detail =
            "exact readiness record accepted from live sealed image";
        static_cast<void>(::close(ready_descriptor_));
        ready_descriptor_ = -1;
      }
    } else if (count == 0) {
      snapshot_.phase = LinuxServicePhase::failed;
      snapshot_.detail =
          "update service readiness channel closed before readiness";
      return terminate_locked(false);
    } else if (errno != EAGAIN && errno != EWOULDBLOCK &&
               errno != EINTR) {
      snapshot_.phase = LinuxServicePhase::failed;
      snapshot_.detail =
          "update service readiness read failed: " +
          std::string(std::strerror(errno));
      return terminate_locked(false);
    }
  }
  if (snapshot_.phase == LinuxServicePhase::starting &&
      std::chrono::steady_clock::now() >= readiness_deadline_) {
    snapshot_.phase = LinuxServicePhase::failed;
    snapshot_.detail = "update service readiness timed out";
    return terminate_locked(false);
  }
  return Status::success();
}

Status LinuxServiceAdapter::terminate_locked(bool requested) {
  if (ready_descriptor_ >= 0) {
    static_cast<void>(::close(ready_descriptor_));
    ready_descriptor_ = -1;
  }
  if (child_ <= 0) {
    if (requested) {
      snapshot_.phase = LinuxServicePhase::stopped;
      snapshot_.detail = "update service stopped";
    }
    snapshot_.process_id = -1;
    return Status::success();
  }
  const pid_t child = static_cast<pid_t>(child_);
  if (::kill(-child, SIGTERM) != 0 && errno != ESRCH) {
    return errno_status(
        ErrorCode::io_error, "terminate update service child");
  }
  const auto deadline =
      std::chrono::steady_clock::now() + config_.shutdown_timeout;
  int status = 0;
  while (std::chrono::steady_clock::now() < deadline) {
    const pid_t waited = ::waitpid(child, &status, WNOHANG);
    if (waited == child || (waited < 0 && errno == ECHILD)) {
      child_ = -1;
      snapshot_.process_id = -1;
      if (requested) {
        snapshot_.phase = LinuxServicePhase::stopped;
        snapshot_.detail = "update service stopped";
      }
      return Status::success();
    }
    if (waited < 0 && errno != EINTR) {
      return errno_status(
          ErrorCode::io_error, "reap update service child");
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }
  if (::kill(-child, SIGKILL) != 0 && errno != ESRCH) {
    return errno_status(
        ErrorCode::io_error, "kill update service child");
  }
  while (::waitpid(child, &status, 0) < 0 && errno == EINTR) {
  }
  child_ = -1;
  snapshot_.process_id = -1;
  if (requested) {
    snapshot_.phase = LinuxServicePhase::stopped;
    snapshot_.detail = "update service stopped after kill escalation";
  }
  return Status::success();
}

Status LinuxServiceAdapter::stop() {
  std::scoped_lock lock(mutex_);
  return terminate_locked(true);
}

Status LinuxServiceAdapter::mark_confirmed() {
  std::scoped_lock lock(mutex_);
  if (snapshot_.phase != LinuxServicePhase::ready || child_ <= 0 ||
      !snapshot_.candidate) {
    return Status{ErrorCode::unavailable,
                  "update service candidate is not live and ready"};
  }
  snapshot_.candidate = false;
  snapshot_.detail =
      "exact readiness retained after signed update confirmation";
  return Status::success();
}

bool LinuxServiceAdapter::healthy() const {
  std::scoped_lock lock(mutex_);
  return snapshot_.phase == LinuxServicePhase::ready && child_ > 0;
}

LinuxServiceSnapshot LinuxServiceAdapter::snapshot() const {
  std::scoped_lock lock(mutex_);
  return snapshot_;
}

int run_internal_update_service_child() noexcept {
  const char *marker =
      ::getenv("IOTOX_INTERNAL_UPDATE_SERVICE_CHILD");
  if (marker == nullptr || std::string_view(marker) != "1") {
    child_fail(ChildStage::marker, EPERM);
  }
  if (!descriptor_is_pipe(kUpdateServiceReadyDescriptor) ||
      !descriptor_is_sealed_image(kImageDescriptor) ||
      !descriptor_is_pipe(kStatusDescriptor) ||
      !set_close_on_exec(kImageDescriptor) ||
      !set_close_on_exec(kStatusDescriptor)) {
    child_fail(ChildStage::descriptors, EPROTO);
  }
  const pid_t parent = ::getppid();
  if (parent <= 1 ||
      ::prctl(PR_SET_PDEATHSIG, SIGKILL, 0, 0, 0) != 0 ||
      ::getppid() != parent) {
    child_fail(ChildStage::parent_death, EPIPE);
  }
  if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 ||
      ::prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) != 1) {
    child_fail(ChildStage::no_new_privileges, EPERM);
  }
  if (::setsid() < 0 || ::getpgrp() != ::getpid()) {
    child_fail(ChildStage::session, errno);
  }
  if (::chdir("/") != 0) {
    child_fail(ChildStage::directory, errno);
  }
  ::umask(static_cast<mode_t>(0077));
  if (!close_ambient_descriptors()) {
    child_fail(ChildStage::descriptor_hygiene, errno);
  }
  const char *sequence = ::getenv("IOTOX_UPDATE_SEQUENCE");
  const char *version = ::getenv("IOTOX_UPDATE_VERSION");
  const char *digest = ::getenv("IOTOX_UPDATE_PAYLOAD_DIGEST");
  if (sequence == nullptr || version == nullptr || digest == nullptr) {
    child_fail(ChildStage::marker, EPROTO);
  }
  std::array<std::string, 4U> environment_storage{
      std::string{kReadyFdEnvironment},
      std::string{"IOTOX_UPDATE_SEQUENCE="} + sequence,
      std::string{"IOTOX_UPDATE_VERSION="} + version,
      std::string{"IOTOX_UPDATE_PAYLOAD_DIGEST="} + digest};
  std::array<char *, 5U> environment{};
  for (std::size_t index = 0U; index < environment_storage.size(); ++index) {
    environment[index] = environment_storage[index].data();
  }
  std::array<std::string, 1U> argument_storage{
      "iotox-linux-service-v1"};
  std::array<char *, 2U> arguments{
      argument_storage[0U].data(), nullptr};
  ::fexecve(kImageDescriptor, arguments.data(), environment.data());
  child_fail(ChildStage::final_exec, errno);
}

} // namespace iotox::update
