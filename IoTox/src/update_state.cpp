#include "iotox/update_state.hpp"

#include "iotox/update_witness.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_digest.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::update {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {
    'I', 'O', 'T', 'O', 'X', 'U', 'S', '1'};
constexpr std::uint8_t kFormatVersion = 1U;
constexpr std::string_view kSignatureDomain = "iotox-update-state-signature-v1";
constexpr std::string_view kHealthTokenDomain = "iotox-update-health-token-v1";
constexpr std::size_t kConfirmedVersionOffset = 128U;
constexpr std::size_t kCandidateVersionOffset = 240U;
constexpr std::size_t kVersionBytes = 32U;
constexpr std::size_t kNamespaceOffset = 344U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kTargetOffset = 408U;
constexpr std::size_t kTargetBytes = 64U;
constexpr std::size_t kDeviceOffset = 472U;
constexpr std::size_t kReservedOffset = 504U;
constexpr std::size_t kMaximumSlots = 8U;
constexpr std::size_t kMaximumQuarantinedSlots = 256U;
std::atomic<std::uint64_t> g_pointer_sequence{1U};

class UniqueFd {
public:
  UniqueFd() = default;
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() {
    if (descriptor_ < 0) return;
    int result = -1;
    do {
      result = ::close(descriptor_);
    } while (result != 0 && errno == EINTR);
  }
  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;
  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept {
    return descriptor_ >= 0;
  }

private:
  int descriptor_{-1};
};

class PathCleanup {
public:
  explicit PathCleanup(std::filesystem::path path)
      : path_(std::move(path)) {}
  ~PathCleanup() {
    if (armed_) static_cast<void>(::unlink(path_.c_str()));
  }
  PathCleanup(const PathCleanup &) = delete;
  PathCleanup &operator=(const PathCleanup &) = delete;
  void release() noexcept { armed_ = false; }

private:
  std::filesystem::path path_;
  bool armed_{true};
};

[[nodiscard]] Status io_status(std::string operation,
                               const std::filesystem::path &path,
                               int error = errno) {
  return Status{ErrorCode::io_error,
                std::move(operation) + " '" + path.string() + "': " +
                    std::strerror(error)};
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> (56U - index * 8U));
  }
}

[[nodiscard]] std::uint64_t read_u64(
    std::span<const std::uint8_t> input, std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index) {
    value = (value << 8U) | input[offset + index];
  }
  return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
  std::copy(value.begin(), value.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
  std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), Size,
              value.begin());
}

[[nodiscard]] bool all_zero(
    std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t value) { return value == 0U; });
}

[[nodiscard]] bool canonical_version(std::string_view value) noexcept {
  if (value.empty() || value.size() >= kVersionBytes ||
      value.front() == ' ' || value.back() == ' ') return false;
  return std::all_of(value.begin(), value.end(), [](char character) {
    const auto byte = static_cast<unsigned char>(character);
    return byte >= 0x20U && byte <= 0x7eU;
  });
}

void write_optional_string(std::span<std::uint8_t> output,
                           std::size_t offset, std::string_view value) {
  if (value.empty()) {
    std::fill(output.begin() + static_cast<std::ptrdiff_t>(offset),
              output.begin() +
                  static_cast<std::ptrdiff_t>(offset + kVersionBytes),
              0U);
    return;
  }
  output[offset] = static_cast<std::uint8_t>(value.size());
  std::copy(value.begin(), value.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset + 1U));
  std::fill(output.begin() +
                static_cast<std::ptrdiff_t>(offset + 1U + value.size()),
            output.begin() +
                static_cast<std::ptrdiff_t>(offset + kVersionBytes),
            0U);
}

[[nodiscard]] Result<std::string> read_optional_string(
    std::span<const std::uint8_t> input, std::size_t offset,
    std::string_view label) {
  const std::size_t length = input[offset];
  if (length >= kVersionBytes) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " length is invalid"};
  }
  const auto first = input.begin() + static_cast<std::ptrdiff_t>(offset + 1U);
  const auto padding = first + static_cast<std::ptrdiff_t>(length);
  const auto end = input.begin() +
      static_cast<std::ptrdiff_t>(offset + kVersionBytes);
  if (!std::all_of(padding, end,
                   [](std::uint8_t value) { return value == 0U; })) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " padding is not zero"};
  }
  if (length == 0U) return std::string{};
  return std::string(reinterpret_cast<const char *>(&*first), length);
}

void write_fixed_string(std::span<std::uint8_t> output, std::size_t offset,
                        std::size_t field_bytes, std::string_view value) {
  output[offset] = static_cast<std::uint8_t>(value.size());
  std::copy(value.begin(), value.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset + 1U));
  std::fill(output.begin() + static_cast<std::ptrdiff_t>(offset + 1U +
                                                         value.size()),
            output.begin() + static_cast<std::ptrdiff_t>(offset + field_bytes),
            0U);
}

[[nodiscard]] Result<std::string> read_fixed_string(
    std::span<const std::uint8_t> input, std::size_t offset,
    std::size_t field_bytes, std::string_view label) {
  const std::size_t length = input[offset];
  if (length == 0U || length >= field_bytes) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " length is invalid"};
  }
  const auto first = input.begin() + static_cast<std::ptrdiff_t>(offset + 1U);
  const auto padding = first + static_cast<std::ptrdiff_t>(length);
  const auto end = input.begin() +
      static_cast<std::ptrdiff_t>(offset + field_bytes);
  if (!std::all_of(padding, end,
                   [](std::uint8_t value) { return value == 0U; })) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " padding is not zero"};
  }
  return std::string(reinterpret_cast<const char *>(&*first), length);
}

[[nodiscard]] Status validate_revision(const UpdateRevision &revision,
                                       bool required) {
  if (!revision.present()) {
    if (required ||
        revision.payload_kind != PayloadKind::opaque_slot_v1 ||
        revision.payload_bytes != 0U ||
        !all_zero(revision.payload_digest) ||
        !all_zero(revision.manifest_record) || !revision.version.empty()) {
      return Status{ErrorCode::invalid_argument,
                    "absent update revision contains state"};
    }
    return Status::success();
  }
  if ((revision.payload_kind != PayloadKind::opaque_slot_v1 &&
       revision.payload_kind != PayloadKind::linux_service_v1) ||
      revision.payload_bytes == 0U || all_zero(revision.payload_digest) ||
      all_zero(revision.manifest_record) ||
      !canonical_version(revision.version)) {
    return Status{ErrorCode::invalid_argument,
                  "present update revision is incomplete"};
  }
  return Status::success();
}

[[nodiscard]] Status validate_state_fields(const UpdatePolicy *policy,
                                           const UpdateState &state) {
  if (!sync::valid_namespace_id(state.namespace_id) ||
      state.namespace_id.size() >= kNamespaceBytes ||
      !sync::valid_namespace_id(state.target) ||
      state.target.size() >= kTargetBytes || all_zero(state.device) ||
      state.generation == 0U || state.boot_attempts > 1U) {
    return Status{ErrorCode::invalid_argument,
                  "signed update state has an invalid identity or counter"};
  }
  if (policy != nullptr &&
      (state.namespace_id != policy->namespace_id ||
       state.target != policy->target ||
       (state.confirmed.present() &&
        state.confirmed.payload_kind != policy->payload_kind) ||
       (state.candidate.present() &&
        state.candidate.payload_kind != policy->payload_kind))) {
    return Status{ErrorCode::protocol_error,
                  "signed update state is bound to another policy"};
  }
  const bool candidate_required =
      state.phase == UpdatePhase::staged ||
      state.phase == UpdatePhase::pending_restart ||
      state.phase == UpdatePhase::awaiting_health;
  const Status confirmed = validate_revision(state.confirmed, false);
  const Status candidate =
      validate_revision(state.candidate, candidate_required);
  if (!confirmed.ok()) return confirmed;
  if (!candidate.ok()) return candidate;
  if (candidate_required && state.candidate.sequence <=
                                state.confirmed.sequence) {
    return Status{ErrorCode::protocol_error,
                  "update candidate does not advance the confirmed sequence"};
  }
  const bool failed_present = state.last_failed_sequence != 0U;
  if (failed_present == all_zero(state.last_failed_digest)) {
    return Status{ErrorCode::protocol_error,
                  "update failure sequence and digest disagree"};
  }
  switch (state.phase) {
    case UpdatePhase::staged:
      if (state.applied_incarnation != 0U ||
          state.health_incarnation != 0U || state.boot_attempts != 0U ||
          !all_zero(state.health_token_digest)) {
        return Status{ErrorCode::protocol_error,
                      "staged update has pending health state"};
      }
      break;
    case UpdatePhase::pending_restart:
      if (state.applied_incarnation == 0U ||
          state.health_incarnation != 0U || state.boot_attempts != 0U ||
          all_zero(state.health_token_digest)) {
        return Status{ErrorCode::protocol_error,
                      "pending update state is incomplete"};
      }
      break;
    case UpdatePhase::awaiting_health:
      if (state.applied_incarnation == 0U ||
          state.health_incarnation <= state.applied_incarnation ||
          state.boot_attempts != 1U ||
          all_zero(state.health_token_digest)) {
        return Status{ErrorCode::protocol_error,
                      "awaiting-health update state is incomplete"};
      }
      break;
    case UpdatePhase::confirmed:
      if (!state.confirmed.present() || state.candidate.present() ||
          state.applied_incarnation != 0U ||
          state.health_incarnation != 0U || state.boot_attempts != 0U ||
          !all_zero(state.health_token_digest)) {
        return Status{ErrorCode::protocol_error,
                      "confirmed update state contains a candidate"};
      }
      break;
    case UpdatePhase::idle_after_rollback:
      if (state.confirmed.present() || state.candidate.present() ||
          state.applied_incarnation != 0U ||
          state.health_incarnation != 0U || state.boot_attempts != 0U ||
          !all_zero(state.health_token_digest) ||
          state.rollback_count == 0U || !failed_present) {
        return Status{ErrorCode::protocol_error,
                      "idle rollback state is not canonical"};
      }
      break;
    default:
      return Status{ErrorCode::unsupported,
                    "signed update state phase is unsupported"};
  }
  return Status::success();
}

[[nodiscard]] bool canonical_decimal(std::string_view value) noexcept {
  if (value.empty() || value.front() < '1' || value.front() > '9')
    return false;
  return std::all_of(value.begin() + 1, value.end(), [](char character) {
    return character >= '0' && character <= '9';
  });
}

[[nodiscard]] bool canonical_hex(std::string_view value) noexcept {
  return value.size() == sync::Digest{}.size() * 2U &&
      std::all_of(value.begin(), value.end(), [](char character) {
        return (character >= '0' && character <= '9') ||
               (character >= 'A' && character <= 'F');
      });
}

[[nodiscard]] bool canonical_slot_name(std::string_view value) noexcept {
  constexpr std::string_view suffix = ".payload";
  if (!value.ends_with(suffix)) return false;
  value.remove_suffix(suffix.size());
  const std::size_t separator = value.find('-');
  return separator != std::string_view::npos &&
      canonical_decimal(value.substr(0U, separator)) &&
      canonical_hex(value.substr(separator + 1U));
}

[[nodiscard]] bool canonical_slot_temporary(std::string_view value) noexcept {
  constexpr std::string_view prefix = ".slot.part.";
  if (!value.starts_with(prefix) || value.size() != prefix.size() + 6U)
    return false;
  value.remove_prefix(prefix.size());
  return std::all_of(value.begin(), value.end(), [](char character) {
    return (character >= '0' && character <= '9') ||
           (character >= 'A' && character <= 'Z') ||
           (character >= 'a' && character <= 'z');
  });
}

[[nodiscard]] bool canonical_quarantine_name(
    std::string_view value) noexcept {
  constexpr std::string_view marker = ".q.";
  const std::size_t separator = value.rfind(marker);
  return separator != std::string_view::npos &&
      canonical_slot_name(value.substr(0U, separator)) &&
      canonical_decimal(value.substr(separator + marker.size()));
}

[[nodiscard]] bool canonical_pointer_temporary(
    std::string_view value) noexcept {
  constexpr std::string_view prefix = ".current.part.";
  if (!value.starts_with(prefix)) return false;
  value.remove_prefix(prefix.size());
  const std::size_t separator = value.find('.');
  return separator != std::string_view::npos &&
      value.find('.', separator + 1U) == std::string_view::npos &&
      canonical_decimal(value.substr(0U, separator)) &&
      canonical_decimal(value.substr(separator + 1U));
}

[[nodiscard]] Status require_private_directory(
    const std::filesystem::path &path) {
  struct stat metadata{};
  if (::lstat(path.c_str(), &metadata) != 0)
    return io_status("unable to inspect update state directory", path);
  if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & 0077U) != 0U ||
      (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0U) {
    return Status{ErrorCode::protocol_error,
                  "update state path is not an owner-private directory: " +
                      path.string()};
  }
  return Status::success();
}

[[nodiscard]] Status ensure_private_child_directory(
    const std::filesystem::path &path) {
  if (::mkdir(path.c_str(), 0700) != 0 && errno != EEXIST)
    return io_status("unable to create update state directory", path);
  return require_private_directory(path);
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
  UniqueFd descriptor(
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (!descriptor) return io_status("unable to open update state directory", path);
  if (::fsync(descriptor.get()) != 0)
    return io_status("unable to sync update state directory", path);
  return Status::success();
}

[[nodiscard]] std::filesystem::path relative_slot_target(
    const UpdateRevision &revision) {
  return std::filesystem::path("slots") /
      (std::to_string(revision.sequence) + "-" +
       security::hex(revision.payload_digest) + ".payload");
}

[[nodiscard]] Result<std::optional<std::filesystem::path>> current_target(
    const UpdatePolicy &policy) {
  const std::filesystem::path current = policy.root / "current";
  struct stat metadata{};
  if (::lstat(current.c_str(), &metadata) != 0) {
    if (errno == ENOENT) return std::optional<std::filesystem::path>{};
    return io_status("unable to inspect update current pointer", current);
  }
  if (!S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
    return Status{ErrorCode::protocol_error,
                  "update current pointer is not an owner symbolic link"};
  }
  std::error_code error;
  const std::filesystem::path target =
      std::filesystem::read_symlink(current, error);
  if (error || target.empty() || target.is_absolute() ||
      target != target.lexically_normal() ||
      target.parent_path() != std::filesystem::path("slots") ||
      !canonical_slot_name(target.filename().string())) {
    return Status{ErrorCode::protocol_error,
                  "update current pointer target is not canonical"};
  }
  return std::optional<std::filesystem::path>{target};
}

[[nodiscard]] Status switch_pointer(
    const UpdatePolicy &policy,
    const std::optional<std::filesystem::path> &target) {
  const std::filesystem::path current = policy.root / "current";
  if (!target.has_value()) {
    if (::unlink(current.c_str()) != 0 && errno != ENOENT)
      return io_status("unable to remove update current pointer", current);
    return sync_directory(policy.root);
  }
  if (target->empty() || target->is_absolute() ||
      target->parent_path() != std::filesystem::path("slots") ||
      !canonical_slot_name(target->filename().string())) {
    return Status{ErrorCode::internal_error,
                  "refusing a noncanonical update pointer target"};
  }
  const std::uint64_t ordinal = g_pointer_sequence.fetch_add(1U);
  if (ordinal == 0U) {
    return Status{ErrorCode::resource_exhausted,
                  "update pointer temporary sequence is exhausted"};
  }
  const std::filesystem::path temporary =
      policy.root /
      (".current.part." + std::to_string(::getpid()) + "." +
       std::to_string(ordinal));
  if (::symlink(target->c_str(), temporary.c_str()) != 0)
    return io_status("unable to prepare update current pointer", temporary);
  PathCleanup cleanup(temporary);
  if (::rename(temporary.c_str(), current.c_str()) != 0)
    return io_status("unable to commit update current pointer", current);
  cleanup.release();
  return sync_directory(policy.root);
}

[[nodiscard]] Status cleanup_root(const UpdatePolicy &policy) {
  try {
    for (const auto &entry : std::filesystem::directory_iterator(policy.root)) {
      const std::string name = entry.path().filename().string();
      if (name == "slots" || name == "state" || name == "quarantine" ||
          name == "current") continue;
      if (!canonical_pointer_temporary(name)) {
        return Status{ErrorCode::protocol_error,
                      "update root contains an ambiguous entry"};
      }
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0 ||
          !S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::protocol_error,
                      "update pointer temporary has an unsafe shape"};
      }
      std::error_code error;
      const auto target = std::filesystem::read_symlink(entry.path(), error);
      if (error || target.is_absolute() ||
          target.parent_path() != std::filesystem::path("slots") ||
          !canonical_slot_name(target.filename().string())) {
        return Status{ErrorCode::protocol_error,
                      "update pointer temporary target is invalid"};
      }
      if (::unlink(entry.path().c_str()) != 0)
        return io_status("unable to remove update pointer temporary", entry.path());
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update root: " +
                      std::string(error.what())};
  }
  return sync_directory(policy.root);
}

[[nodiscard]] Result<std::size_t> validate_quarantine(
    const UpdatePolicy &policy) {
  const auto quarantine = policy.root / "quarantine";
  std::size_t retained = 0U;
  try {
    for (const auto &entry :
         std::filesystem::directory_iterator(quarantine)) {
      const std::string name = entry.path().filename().string();
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0)
        return io_status("unable to inspect quarantined update slot",
                         entry.path());
      if (!canonical_quarantine_name(name) ||
          !S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
          metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0777U) != 0400U) {
        return Status{ErrorCode::protocol_error,
                      "update quarantine contains an unsafe entry"};
      }
      ++retained;
      if (retained > kMaximumQuarantinedSlots) {
        return Status{ErrorCode::resource_exhausted,
                      "recoverable update quarantine bound is exhausted"};
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update quarantine: " +
                      std::string(error.what())};
  }
  return retained;
}

[[nodiscard]] Status cleanup_slots(const UpdatePolicy &policy) {
  const auto slots = policy.root / "slots";
  std::size_t retained = 0U;
  try {
    for (const auto &entry : std::filesystem::directory_iterator(slots)) {
      const std::string name = entry.path().filename().string();
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0)
        return io_status("unable to inspect update slot entry", entry.path());
      if (canonical_slot_temporary(name)) {
        if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
            metadata.st_uid != ::geteuid() ||
            (metadata.st_mode & 0777U) != 0600U) {
          return Status{ErrorCode::protocol_error,
                        "update slot temporary has an unsafe shape"};
        }
        if (::unlink(entry.path().c_str()) != 0)
          return io_status("unable to remove update slot temporary", entry.path());
        continue;
      }
      if (!canonical_slot_name(name) || !S_ISREG(metadata.st_mode) ||
          metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0777U) != 0400U) {
        return Status{ErrorCode::protocol_error,
                      "update slot directory contains an unsafe entry"};
      }
      ++retained;
      if (retained > kMaximumSlots) {
        return Status{ErrorCode::resource_exhausted,
                      "update slot retention bound is exhausted"};
      }
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update slots: " +
                      std::string(error.what())};
  }
  return sync_directory(slots);
}

[[nodiscard]] Status require_slot_capacity(
    const UpdatePolicy &policy,
    const std::filesystem::path &destination) {
  const auto slots = policy.root / "slots";
  std::size_t retained = 0U;
  bool destination_present = false;
  try {
    for (const auto &entry : std::filesystem::directory_iterator(slots)) {
      const std::string name = entry.path().filename().string();
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0) {
        return io_status("unable to inspect retained update slot", entry.path());
      }
      if (!canonical_slot_name(name) || !S_ISREG(metadata.st_mode) ||
          metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0777U) != 0400U) {
        return Status{ErrorCode::protocol_error,
                      "update slot capacity contains an unsafe entry"};
      }
      ++retained;
      destination_present = destination_present || entry.path() == destination;
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update slot capacity: " +
                      std::string(error.what())};
  }
  if (!destination_present && retained >= kMaximumSlots) {
    return Status{ErrorCode::resource_exhausted,
                  "update slot retention bound is exhausted"};
  }
  return Status::success();
}

[[nodiscard]] Status cleanup_state_temporaries(const UpdatePolicy &policy) {
  const auto state_root = policy.root / "state";
  constexpr std::string_view prefix = ".iotox-update.state.tmp.";
  try {
    for (const auto &entry : std::filesystem::directory_iterator(state_root)) {
      const std::string name = entry.path().filename().string();
      if (name == "update.state") continue;
      if (!name.starts_with(prefix) || name.size() != prefix.size() + 6U) {
        return Status{ErrorCode::protocol_error,
                      "update state directory contains an ambiguous entry"};
      }
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0 ||
          !S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
          metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0777U) != 0600U) {
        return Status{ErrorCode::protocol_error,
                      "update state temporary has an unsafe shape"};
      }
      if (::unlink(entry.path().c_str()) != 0)
        return io_status("unable to remove update state temporary", entry.path());
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update state directory: " +
                      std::string(error.what())};
  }
  return sync_directory(state_root);
}

[[nodiscard]] Status read_exact(int descriptor,
                                std::span<std::uint8_t> output,
                                const std::filesystem::path &path) {
  std::size_t offset = 0U;
  while (offset < output.size()) {
    const ssize_t count =
        ::read(descriptor, output.data() + offset, output.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    if (count == 0)
      return Status{ErrorCode::protocol_error,
                    "signed update state ended early"};
    return io_status("unable to read signed update state", path);
  }
  return Status::success();
}

[[nodiscard]] Status copy_bundle_payload(
    const UpdatePolicy &policy, const UpdateBundleInfo &bundle,
    const UpdateRevision &revision, const std::filesystem::path &destination,
    const security::Sodium &sodium) {
  const Status capacity = require_slot_capacity(policy, destination);
  if (!capacity.ok()) return capacity;
  struct stat existing{};
  if (::lstat(destination.c_str(), &existing) == 0) return Status::success();
  if (errno != ENOENT)
    return io_status("unable to inspect update slot destination", destination);

  UniqueFd source(::open(bundle.path.c_str(),
                         O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!source) return io_status("unable to reopen signed update bundle", bundle.path);
  if (::lseek(source.get(),
              static_cast<off_t>(kSignedUpdateManifestBytes), SEEK_SET) < 0) {
    return io_status("unable to seek signed update payload", bundle.path);
  }
  const auto slots = policy.root / "slots";
  std::string pattern = (slots / ".slot.part.XXXXXX").string();
  std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
  mutable_pattern.push_back('\0');
  UniqueFd output(::mkstemp(mutable_pattern.data()));
  if (!output) return io_status("unable to create update slot temporary", slots);
  const std::filesystem::path temporary{mutable_pattern.data()};
  PathCleanup cleanup(temporary);
  if (::fchmod(output.get(), 0600) != 0)
    return io_status("unable to secure update slot temporary", temporary);

  std::array<std::uint8_t, 64U * 1024U> buffer{};
  std::uint64_t copied = 0U;
  while (copied < revision.payload_bytes) {
    const std::uint64_t remaining = revision.payload_bytes - copied;
    const std::size_t request = static_cast<std::size_t>(
        std::min<std::uint64_t>(remaining, buffer.size()));
    const ssize_t count = ::read(source.get(), buffer.data(), request);
    if (count < 0 && errno == EINTR) continue;
    if (count <= 0) {
      return count == 0
          ? Status{ErrorCode::protocol_error,
                   "signed update payload ended during slot staging"}
          : io_status("unable to read signed update payload", bundle.path);
    }
    std::size_t written = 0U;
    const std::size_t amount = static_cast<std::size_t>(count);
    while (written < amount) {
      const ssize_t result =
          ::write(output.get(), buffer.data() + written, amount - written);
      if (result < 0 && errno == EINTR) continue;
      if (result <= 0)
        return io_status("unable to write update slot temporary", temporary);
      written += static_cast<std::size_t>(result);
    }
    copied += amount;
  }
  std::uint8_t trailing = 0U;
  const ssize_t extra = ::read(source.get(), &trailing, 1U);
  if (extra != 0) {
    if (extra < 0 && errno == EINTR) {
      return Status{ErrorCode::unavailable,
                    "signed update payload trailing-byte check was interrupted"};
    }
    return extra > 0
        ? Status{ErrorCode::protocol_error,
                 "signed update bundle has trailing payload bytes"}
        : io_status("unable to finish signed update payload", bundle.path);
  }
  if (::fsync(output.get()) != 0)
    return io_status("unable to sync update slot temporary", temporary);
  if (::fchmod(output.get(), 0400) != 0)
    return io_status("unable to freeze update slot temporary", temporary);
  if (::fsync(output.get()) != 0)
    return io_status("unable to sync frozen update slot temporary", temporary);
  if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                destination.c_str(), RENAME_NOREPLACE) != 0) {
    if (errno != EEXIST)
      return io_status("unable to commit update slot with no-replace", destination);
  } else {
    cleanup.release();
    const Status synced = sync_directory(slots);
    if (!synced.ok()) return synced;
  }
  auto reinspected = inspect_signed_update_bundle(policy, bundle.path, sodium);
  if (!reinspected.ok() ||
      reinspected.value().manifest_record != revision.manifest_record) {
    return Status{ErrorCode::protocol_error,
                  "signed update bundle changed across staging"};
  }
  return Status::success();
}

} // namespace

std::string_view update_phase_name(UpdatePhase phase) noexcept {
  switch (phase) {
    case UpdatePhase::staged: return "staged";
    case UpdatePhase::pending_restart: return "pending-restart";
    case UpdatePhase::awaiting_health: return "awaiting-health";
    case UpdatePhase::confirmed: return "confirmed";
    case UpdatePhase::idle_after_rollback: return "idle-after-rollback";
  }
  return "unknown";
}

std::string_view startup_disposition_name(
    StartupDisposition disposition) noexcept {
  switch (disposition) {
    case StartupDisposition::empty: return "empty";
    case StartupDisposition::unchanged: return "unchanged";
    case StartupDisposition::health_window_opened:
      return "health-window-opened";
    case StartupDisposition::incomplete_apply_rolled_back:
      return "incomplete-apply-rolled-back";
    case StartupDisposition::unconfirmed_restart_rolled_back:
      return "unconfirmed-restart-rolled-back";
  }
  return "unknown";
}

Result<UpdateStateBody> encode_update_state_body(const UpdateState &state) {
  const Status valid = validate_state_fields(nullptr, state);
  if (!valid.ok()) return valid;
  UpdateStateBody output{};
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = kFormatVersion;
  output[9U] = static_cast<std::uint8_t>(state.phase);
  output[10U] = state.boot_attempts;
  // Zero preserves the canonical encoding of every pre-adapter
  // opaque-slot-v1 state. The only nonzero extension value is the distinct
  // executable service kind.
  output[11U] = state.confirmed.present() &&
                        state.confirmed.payload_kind ==
                            PayloadKind::linux_service_v1
                    ? static_cast<std::uint8_t>(
                          PayloadKind::linux_service_v1)
                    : 0U;
  output[12U] = state.candidate.present() &&
                        state.candidate.payload_kind ==
                            PayloadKind::linux_service_v1
                    ? static_cast<std::uint8_t>(
                          PayloadKind::linux_service_v1)
                    : 0U;
  write_u64(output, 16U, state.generation);
  write_u64(output, 24U, state.rollback_count);
  write_u64(output, 32U, state.applied_incarnation);
  write_u64(output, 40U, state.health_incarnation);
  write_u64(output, 48U, state.confirmed.sequence);
  write_u64(output, 56U, state.confirmed.payload_bytes);
  write_array(output, 64U, state.confirmed.payload_digest);
  write_array(output, 96U, state.confirmed.manifest_record);
  write_optional_string(output, kConfirmedVersionOffset,
                        state.confirmed.version);
  write_u64(output, 160U, state.candidate.sequence);
  write_u64(output, 168U, state.candidate.payload_bytes);
  write_array(output, 176U, state.candidate.payload_digest);
  write_array(output, 208U, state.candidate.manifest_record);
  write_optional_string(output, kCandidateVersionOffset,
                        state.candidate.version);
  write_array(output, 272U, state.health_token_digest);
  write_u64(output, 304U, state.last_failed_sequence);
  write_array(output, 312U, state.last_failed_digest);
  write_fixed_string(output, kNamespaceOffset, kNamespaceBytes,
                     state.namespace_id);
  write_fixed_string(output, kTargetOffset, kTargetBytes, state.target);
  write_array(output, kDeviceOffset, state.device);
  return output;
}

Result<SignedUpdateStateBytes> encode_signed_update_state(
    const UpdateState &state) {
  auto body = encode_update_state_body(state);
  if (!body.ok()) return body.status();
  SignedUpdateStateBytes output{};
  std::copy(body.value().begin(), body.value().end(), output.begin());
  std::copy(state.signature.begin(), state.signature.end(),
            output.begin() + static_cast<std::ptrdiff_t>(kUpdateStateBodyBytes));
  return output;
}

Result<UpdateState> decode_signed_update_state(
    std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSignedUpdateStateBytes ||
      !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] != kFormatVersion ||
      (bytes[11U] != 0U &&
       bytes[11U] !=
           static_cast<std::uint8_t>(PayloadKind::linux_service_v1)) ||
      (bytes[12U] != 0U &&
       bytes[12U] !=
           static_cast<std::uint8_t>(PayloadKind::linux_service_v1)) ||
      !std::all_of(bytes.begin() + 13,
                   bytes.begin() + static_cast<std::ptrdiff_t>(16U),
                   [](std::uint8_t value) { return value == 0U; }) ||
      !std::all_of(bytes.begin() +
                       static_cast<std::ptrdiff_t>(kReservedOffset),
                   bytes.begin() +
                       static_cast<std::ptrdiff_t>(kUpdateStateBodyBytes),
                   [](std::uint8_t value) { return value == 0U; })) {
    return Status{ErrorCode::protocol_error,
                  "signed update state header or reserved bytes are invalid"};
  }
  auto confirmed_version = read_optional_string(
      bytes, kConfirmedVersionOffset, "confirmed update version");
  auto candidate_version = read_optional_string(
      bytes, kCandidateVersionOffset, "candidate update version");
  auto namespace_id = read_fixed_string(
      bytes, kNamespaceOffset, kNamespaceBytes, "update state namespace");
  auto target = read_fixed_string(
      bytes, kTargetOffset, kTargetBytes, "update state target");
  if (!confirmed_version.ok()) return confirmed_version.status();
  if (!candidate_version.ok()) return candidate_version.status();
  if (!namespace_id.ok()) return namespace_id.status();
  if (!target.ok()) return target.status();

  UpdateState state;
  state.phase = static_cast<UpdatePhase>(bytes[9U]);
  state.boot_attempts = bytes[10U];
  state.generation = read_u64(bytes, 16U);
  state.rollback_count = read_u64(bytes, 24U);
  state.applied_incarnation = read_u64(bytes, 32U);
  state.health_incarnation = read_u64(bytes, 40U);
  state.confirmed.sequence = read_u64(bytes, 48U);
  state.confirmed.payload_kind =
      bytes[11U] == static_cast<std::uint8_t>(
                          PayloadKind::linux_service_v1)
          ? PayloadKind::linux_service_v1
          : PayloadKind::opaque_slot_v1;
  state.confirmed.payload_bytes = read_u64(bytes, 56U);
  read_array(bytes, 64U, state.confirmed.payload_digest);
  read_array(bytes, 96U, state.confirmed.manifest_record);
  state.confirmed.version = std::move(confirmed_version).value();
  state.candidate.sequence = read_u64(bytes, 160U);
  state.candidate.payload_kind =
      bytes[12U] == static_cast<std::uint8_t>(
                          PayloadKind::linux_service_v1)
          ? PayloadKind::linux_service_v1
          : PayloadKind::opaque_slot_v1;
  state.candidate.payload_bytes = read_u64(bytes, 168U);
  read_array(bytes, 176U, state.candidate.payload_digest);
  read_array(bytes, 208U, state.candidate.manifest_record);
  state.candidate.version = std::move(candidate_version).value();
  read_array(bytes, 272U, state.health_token_digest);
  state.last_failed_sequence = read_u64(bytes, 304U);
  read_array(bytes, 312U, state.last_failed_digest);
  state.namespace_id = std::move(namespace_id).value();
  state.target = std::move(target).value();
  read_array(bytes, kDeviceOffset, state.device);
  read_array(bytes, kUpdateStateBodyBytes, state.signature);
  const Status valid = validate_state_fields(nullptr, state);
  if (!valid.ok()) return Status{ErrorCode::protocol_error, valid.message()};
  if (all_zero(state.signature)) {
    return Status{ErrorCode::protocol_error,
                  "signed update state signature is zero"};
  }
  auto canonical = encode_signed_update_state(state);
  if (!canonical.ok() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "signed update state is not canonical"};
  }
  return state;
}

Status verify_signed_update_state(
    const UpdatePolicy &policy, const UpdateState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_update_policy(policy);
  if (!valid_policy.ok()) return valid_policy;
  const Status valid = validate_state_fields(&policy, state);
  if (!valid.ok()) return valid;
  if (state.device != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "signed update state belongs to another device"};
  }
  auto body = encode_update_state_body(state);
  if (!body.ok()) return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok()) return digest.status();
  return sodium.verify_detached(state.signature, digest.value(), state.device);
}

Result<std::unique_ptr<UpdateStore>> UpdateStore::open(
    UpdatePolicy policy, const security::DeviceIdentity &identity,
    const security::Sodium &sodium, std::uint64_t process_incarnation,
    std::shared_ptr<LifecycleWitness> witness) {
  const Status valid = validate_update_policy(policy);
  if (!valid.ok()) return valid;
  auto store = std::unique_ptr<UpdateStore>(
      new UpdateStore(std::move(policy), identity, sodium,
                      std::move(witness)));
  const Status initialized = store->initialize(process_incarnation);
  if (!initialized.ok()) return initialized;
  return store;
}

Status UpdateStore::initialize(std::uint64_t process_incarnation) {
  if (process_incarnation == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "update store process incarnation must be nonzero"};
  }
  const Status root = require_private_directory(policy_.root);
  if (!root.ok()) return root;
  const Status slots = ensure_private_child_directory(policy_.root / "slots");
  if (!slots.ok()) return slots;
  const Status state_dir = ensure_private_child_directory(policy_.root / "state");
  if (!state_dir.ok()) return state_dir;
  const Status quarantine =
      ensure_private_child_directory(policy_.root / "quarantine");
  if (!quarantine.ok()) return quarantine;
  const Status clean_root = cleanup_root(policy_);
  if (!clean_root.ok()) return clean_root;
  const Status clean_slots = cleanup_slots(policy_);
  if (!clean_slots.ok()) return clean_slots;
  const Status clean_state = cleanup_state_temporaries(policy_);
  if (!clean_state.ok()) return clean_state;
  auto clean_quarantine = validate_quarantine(policy_);
  if (!clean_quarantine.ok()) return clean_quarantine.status();

  if (witness_) {
    auto verified = witness_->verify_and_recover(
        [this]() { return load_state_bytes(); },
        [this](const SignedUpdateStateBytes &bytes) {
          return install_state_bytes(bytes);
        });
    if (!verified) return verified.status();
  }

  auto loaded = load_state();
  if (!loaded.ok()) return loaded.status();
  state_ = loaded.value();
  auto pointer = current_target(policy_);
  if (!pointer.ok()) return pointer.status();
  if (!state_.has_value()) {
    if (pointer.value().has_value()) {
      return Status{ErrorCode::protocol_error,
                    "update current pointer exists without signed state"};
    }
    startup_ = UpdateStartupResult{StartupDisposition::empty, std::nullopt};
    return Status::success();
  }
  UpdateState &state = *state_;
  if (state.confirmed.present()) {
    const Status valid_confirmed = validate_slot(state.confirmed);
    if (!valid_confirmed.ok()) return valid_confirmed;
  }
  if (state.candidate.present()) {
    const Status valid_candidate = validate_slot(state.candidate);
    if (!valid_candidate.ok()) return valid_candidate;
  }
  const std::optional<std::filesystem::path> confirmed_target =
      state.confirmed.present()
          ? std::optional<std::filesystem::path>{
                relative_slot_target(state.confirmed)}
          : std::nullopt;
  const std::optional<std::filesystem::path> candidate_target =
      state.candidate.present()
          ? std::optional<std::filesystem::path>{
                relative_slot_target(state.candidate)}
          : std::nullopt;

  if (state.phase == UpdatePhase::confirmed) {
    if (pointer.value() != confirmed_target) {
      const Status repaired = switch_pointer(policy_, confirmed_target);
      if (!repaired.ok()) return repaired;
    }
    startup_ = UpdateStartupResult{StartupDisposition::unchanged, state};
    return Status::success();
  }
  if (state.phase == UpdatePhase::idle_after_rollback) {
    if (pointer.value().has_value()) {
      const Status repaired = switch_pointer(policy_, std::nullopt);
      if (!repaired.ok()) return repaired;
    }
    startup_ = UpdateStartupResult{StartupDisposition::unchanged, state};
    return Status::success();
  }
  if (state.phase == UpdatePhase::staged) {
    if (pointer.value() != confirmed_target) {
      if (!witness_) {
        return Status{ErrorCode::protocol_error,
                      "staged update pointer differs from confirmed state"};
      }
      const Status repaired = switch_pointer(policy_, confirmed_target);
      if (!repaired.ok()) return repaired;
    }
    startup_ = UpdateStartupResult{StartupDisposition::unchanged, state};
    return Status::success();
  }
  if (state.phase == UpdatePhase::pending_restart) {
    if (witness_ && pointer.value() == confirmed_target) {
      const Status repaired = switch_pointer(policy_, candidate_target);
      if (!repaired.ok()) return repaired;
      pointer = candidate_target;
    }
    if (pointer.value() == candidate_target) {
      if (process_incarnation < state.applied_incarnation) {
        return Status{ErrorCode::protocol_error,
                      "update process incarnation rolled backward"};
      }
      if (process_incarnation == state.applied_incarnation) {
        startup_ = UpdateStartupResult{StartupDisposition::unchanged, state};
        return Status::success();
      }
      if (state.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "update state generation is exhausted"};
      }
      state.phase = UpdatePhase::awaiting_health;
      state.health_incarnation = process_incarnation;
      state.boot_attempts = 1U;
      ++state.generation;
      const Status stored = store_state(state);
      if (!stored.ok()) return stored;
      startup_ = UpdateStartupResult{
          StartupDisposition::health_window_opened, state};
      return Status::success();
    }
    if (pointer.value() == confirmed_target) {
      auto rolled = rollback_candidate(
          state, StartupDisposition::incomplete_apply_rolled_back);
      return rolled.ok() ? Status::success() : rolled.status();
    }
    return Status{ErrorCode::protocol_error,
                  "pending update pointer names an unrelated slot"};
  }
  if (state.phase == UpdatePhase::awaiting_health) {
    if (witness_ && pointer.value() == confirmed_target) {
      const Status repaired = switch_pointer(policy_, candidate_target);
      if (!repaired.ok()) return repaired;
      pointer = candidate_target;
    }
    if (pointer.value() == confirmed_target) {
      auto rolled = rollback_candidate(
          state, StartupDisposition::unconfirmed_restart_rolled_back);
      return rolled.ok() ? Status::success() : rolled.status();
    }
    if (pointer.value() != candidate_target) {
      return Status{ErrorCode::protocol_error,
                    "awaiting-health pointer differs from candidate"};
    }
    if (process_incarnation < state.health_incarnation) {
      return Status{ErrorCode::protocol_error,
                    "update health incarnation rolled backward"};
    }
    if (process_incarnation == state.health_incarnation) {
      startup_ = UpdateStartupResult{StartupDisposition::unchanged, state};
      return Status::success();
    }
    auto rolled = rollback_candidate(
        state, StartupDisposition::unconfirmed_restart_rolled_back);
    return rolled.ok() ? Status::success() : rolled.status();
  }
  return Status{ErrorCode::unsupported, "update state phase is unsupported"};
}

UpdateStartupResult UpdateStore::startup_result() const {
  std::scoped_lock lock(mutex_);
  return startup_;
}

std::optional<UpdateState> UpdateStore::snapshot() const {
  std::scoped_lock lock(mutex_);
  return state_;
}

Result<std::optional<UpdateSelectedSlot>>
UpdateStore::selected_slot() const {
  std::scoped_lock lock(mutex_);
  if (!state_.has_value()) {
    return std::optional<UpdateSelectedSlot>{};
  }
  const bool candidate =
      state_->phase == UpdatePhase::pending_restart ||
      state_->phase == UpdatePhase::awaiting_health;
  const UpdateRevision &revision =
      candidate ? state_->candidate : state_->confirmed;
  if (!revision.present()) {
    return std::optional<UpdateSelectedSlot>{};
  }
  const Status valid = validate_slot(revision);
  if (!valid.ok()) return valid;
  auto pointer = current_target(policy_);
  if (!pointer.ok()) return pointer.status();
  if (pointer.value() !=
      std::optional<std::filesystem::path>{
          relative_slot_target(revision)}) {
    return Status{ErrorCode::protocol_error,
                  "update selected slot differs from current pointer"};
  }
  return std::optional<UpdateSelectedSlot>{
      UpdateSelectedSlot{revision, slot_path(revision), candidate}};
}

Result<std::optional<UpdateState>> UpdateStore::load_state() const {
  auto bytes = load_state_bytes();
  if (!bytes.ok()) return bytes.status();
  if (!bytes.value().has_value()) return std::optional<UpdateState>{};
  auto decoded = decode_signed_update_state(*bytes.value());
  if (!decoded.ok()) return decoded.status();
  const Status verified = verify_signed_update_state(
      policy_, decoded.value(), identity_->public_key(), *sodium_);
  if (!verified.ok()) return verified;
  return std::optional<UpdateState>{std::move(decoded).value()};
}

Result<std::optional<SignedUpdateStateBytes>>
UpdateStore::load_state_bytes() const {
  const auto path = policy_.root / "state" / "update.state";
  UniqueFd descriptor(::open(path.c_str(),
                             O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!descriptor) {
    if (errno == ENOENT) return std::optional<SignedUpdateStateBytes>{};
    return io_status("unable to open signed update state", path);
  }
  struct stat metadata{};
  if (::fstat(descriptor.get(), &metadata) != 0)
    return io_status("unable to inspect signed update state", path);
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & 0777U) != 0600U ||
      metadata.st_size != static_cast<off_t>(kSignedUpdateStateBytes)) {
    return Status{ErrorCode::protocol_error,
                  "signed update state is not one private fixed-size file"};
  }
  SignedUpdateStateBytes bytes{};
  const Status read = read_exact(descriptor.get(), bytes, path);
  if (!read.ok()) return read;
  return std::optional<SignedUpdateStateBytes>{bytes};
}

Status UpdateStore::install_state_bytes(
    const SignedUpdateStateBytes &bytes) const {
  auto decoded = decode_signed_update_state(bytes);
  if (!decoded.ok()) return decoded.status();
  const Status verified = verify_signed_update_state(
      policy_, decoded.value(), identity_->public_key(), *sodium_);
  if (!verified.ok()) return verified;
  return StateStore::write_atomic(
      policy_.root / "state" / "update.state", bytes);
}

Status UpdateStore::store_state(UpdateState &state) const {
  state.device = identity_->public_key();
  state.signature = {};
  auto body = encode_update_state_body(state);
  if (!body.ok()) return body.status();
  auto digest = sodium_->hash(kSignatureDomain, body.value());
  if (!digest.ok()) return digest.status();
  auto signature = identity_->sign(digest.value());
  if (!signature.ok()) return signature.status();
  state.signature = signature.value();
  const Status verified = verify_signed_update_state(
      policy_, state, identity_->public_key(), *sodium_);
  if (!verified.ok()) return verified;
  auto encoded = encode_signed_update_state(state);
  if (!encoded.ok()) return encoded.status();
  if (!witness_) return install_state_bytes(encoded.value());
  auto committed = witness_->transition(
      encoded.value(), [this]() { return load_state_bytes(); },
      [this](const SignedUpdateStateBytes &bytes) {
        return install_state_bytes(bytes);
      });
  return committed ? Status::success() : committed.status();
}

std::filesystem::path UpdateStore::slot_path(
    const UpdateRevision &revision) const {
  return policy_.root / relative_slot_target(revision);
}

Status UpdateStore::validate_slot(const UpdateRevision &revision) const {
  const Status valid_revision = validate_revision(revision, true);
  if (!valid_revision.ok()) return valid_revision;
  const auto path = slot_path(revision);
  struct stat metadata{};
  if (::lstat(path.c_str(), &metadata) != 0)
    return io_status("unable to inspect update slot", path);
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & 0777U) != 0400U || metadata.st_size < 0 ||
      static_cast<std::uint64_t>(metadata.st_size) !=
          revision.payload_bytes) {
    return Status{ErrorCode::protocol_error,
                  "update slot shape or size is invalid: " + path.string()};
  }
  auto digest = sync::hash_sync_file_sha256(path);
  if (!digest.ok()) return digest.status();
  if (digest.value() != revision.payload_digest) {
    return Status{ErrorCode::protocol_error,
                  "update slot digest does not match signed state"};
  }
  return Status::success();
}

Result<UpdateStageResult> UpdateStore::stage(
    const std::filesystem::path &bundle_path) {
  std::scoped_lock lock(mutex_);
  auto bundle = inspect_signed_update_bundle(policy_, bundle_path, *sodium_);
  if (!bundle.ok()) return bundle.status();
  UpdateRevision revision;
  revision.payload_kind = bundle.value().manifest.payload_kind;
  revision.sequence = bundle.value().manifest.release_sequence;
  revision.payload_bytes = bundle.value().manifest.payload_bytes;
  revision.payload_digest = bundle.value().manifest.payload_digest;
  revision.manifest_record = bundle.value().manifest_record;
  revision.version = bundle.value().manifest.version;
  const std::uint64_t confirmed_sequence =
      state_.has_value() ? state_->confirmed.sequence : 0U;
  if (revision.sequence <= confirmed_sequence) {
    return Status{ErrorCode::protocol_error,
                  "update release sequence does not advance confirmed state"};
  }
  if (state_.has_value() && state_->candidate.present()) {
    if (state_->candidate == revision && state_->phase == UpdatePhase::staged) {
      const Status valid = validate_slot(revision);
      if (!valid.ok()) return valid;
      return UpdateStageResult{*state_, true, slot_path(revision)};
    }
    return Status{ErrorCode::unavailable,
                  "another update candidate is already staged or pending"};
  }
  const auto destination = slot_path(revision);
  const Status copied = copy_bundle_payload(
      policy_, bundle.value(), revision, destination, *sodium_);
  if (!copied.ok()) return copied;
  const Status valid_slot = validate_slot(revision);
  if (!valid_slot.ok()) return valid_slot;

  UpdateState next = state_.value_or(UpdateState{});
  next.namespace_id = policy_.namespace_id;
  next.target = policy_.target;
  next.phase = UpdatePhase::staged;
  if (next.generation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "update state generation is exhausted"};
  }
  ++next.generation;
  next.candidate = revision;
  next.applied_incarnation = 0U;
  next.health_incarnation = 0U;
  next.boot_attempts = 0U;
  next.health_token_digest = {};
  const Status stored = store_state(next);
  if (!stored.ok()) return stored;
  state_ = next;
  return UpdateStageResult{next, false, destination};
}

Result<UpdateApplyResult> UpdateStore::apply(
    const sync::Digest &expected_manifest_record,
    std::uint64_t process_incarnation) {
  std::scoped_lock lock(mutex_);
  if (process_incarnation == 0U || !state_.has_value() ||
      state_->phase != UpdatePhase::staged ||
      state_->candidate.manifest_record != expected_manifest_record) {
    return Status{ErrorCode::invalid_argument,
                  "update apply requires the exact staged manifest record"};
  }
  const Status valid_slot = validate_slot(state_->candidate);
  if (!valid_slot.ok()) return valid_slot;
  HealthToken token{};
  const Status random = security::fill_random(token);
  if (!random.ok()) return random;
  if (all_zero(token)) {
    return Status{ErrorCode::internal_error,
                  "operating system returned a zero update health token"};
  }
  auto token_digest = sodium_->hash(kHealthTokenDomain, token);
  if (!token_digest.ok()) return token_digest.status();
  if (all_zero(token_digest.value())) {
    return Status{ErrorCode::internal_error,
                  "update health token digest is zero"};
  }
  if (state_->generation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "update state generation is exhausted"};
  }
  UpdateState next = *state_;
  next.phase = UpdatePhase::pending_restart;
  ++next.generation;
  next.applied_incarnation = process_incarnation;
  next.health_incarnation = 0U;
  next.boot_attempts = 0U;
  next.health_token_digest = token_digest.value();
  const Status stored = store_state(next);
  if (!stored.ok()) return stored;
  state_ = next;
  const Status switched = switch_pointer(
      policy_, relative_slot_target(next.candidate));
  if (!switched.ok()) return switched;
  return UpdateApplyResult{next, token, slot_path(next.candidate)};
}

Result<UpdateState> UpdateStore::confirm(
    const HealthToken &token, std::uint64_t process_incarnation) {
  std::scoped_lock lock(mutex_);
  if (!state_.has_value() || state_->phase != UpdatePhase::awaiting_health ||
      process_incarnation == 0U ||
      process_incarnation != state_->health_incarnation) {
    return Status{ErrorCode::unavailable,
                  "update confirmation requires the admitted health incarnation"};
  }
  auto observed = sodium_->hash(kHealthTokenDomain, token);
  if (!observed.ok()) return observed.status();
  if (!security::constant_time_equal(observed.value(),
                                     state_->health_token_digest)) {
    return Status{ErrorCode::protocol_error,
                  "update health token does not match pending state"};
  }
  const Status valid_slot = validate_slot(state_->candidate);
  if (!valid_slot.ok()) return valid_slot;
  auto pointer = current_target(policy_);
  if (!pointer.ok()) return pointer.status();
  if (pointer.value() !=
      std::optional<std::filesystem::path>{
          relative_slot_target(state_->candidate)}) {
    return Status{ErrorCode::protocol_error,
                  "update current pointer changed before health confirmation"};
  }
  if (state_->generation == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "update state generation is exhausted"};
  }
  UpdateState next = *state_;
  next.phase = UpdatePhase::confirmed;
  ++next.generation;
  next.confirmed = next.candidate;
  next.candidate = {};
  next.applied_incarnation = 0U;
  next.health_incarnation = 0U;
  next.boot_attempts = 0U;
  next.health_token_digest = {};
  const Status stored = store_state(next);
  if (!stored.ok()) return stored;
  state_ = next;
  return next;
}

Result<UpdateState> UpdateStore::rollback_candidate(
    UpdateState state, StartupDisposition disposition) {
  if (!state.candidate.present()) {
    return Status{ErrorCode::internal_error,
                  "update rollback has no candidate"};
  }
  if (state.generation == std::numeric_limits<std::uint64_t>::max() ||
      state.rollback_count == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "update rollback counter is exhausted"};
  }
  const std::optional<std::filesystem::path> rollback_target =
      state.confirmed.present()
          ? std::optional<std::filesystem::path>{
                relative_slot_target(state.confirmed)}
          : std::nullopt;
  if (!witness_) {
    const Status switched = switch_pointer(policy_, rollback_target);
    if (!switched.ok()) return switched;
  }
  state.last_failed_sequence = state.candidate.sequence;
  state.last_failed_digest = state.candidate.payload_digest;
  state.candidate = {};
  state.phase = state.confirmed.present()
      ? UpdatePhase::confirmed
      : UpdatePhase::idle_after_rollback;
  ++state.generation;
  ++state.rollback_count;
  state.applied_incarnation = 0U;
  state.health_incarnation = 0U;
  state.boot_attempts = 0U;
  state.health_token_digest = {};
  const Status stored = store_state(state);
  if (!stored.ok()) return stored;
  state_ = state;
  if (witness_) {
    const Status switched = switch_pointer(policy_, rollback_target);
    if (!switched.ok()) return switched;
  }
  startup_ = UpdateStartupResult{disposition, state};
  return state;
}

Result<UpdateState> UpdateStore::expire_health(
    std::uint64_t process_incarnation) {
  std::scoped_lock lock(mutex_);
  if (!state_.has_value() || state_->phase != UpdatePhase::awaiting_health ||
      process_incarnation == 0U ||
      process_incarnation != state_->health_incarnation) {
    return Status{ErrorCode::unavailable,
                  "update health expiry requires the admitted health incarnation"};
  }
  return rollback_candidate(
      *state_, StartupDisposition::unconfirmed_restart_rolled_back);
}

Result<UpdateRetentionResult> UpdateStore::retain_slots(
    UpdateRetentionMode mode) {
  std::scoped_lock lock(mutex_);
  if (mode != UpdateRetentionMode::dry_run &&
      mode != UpdateRetentionMode::quarantine) {
    return Status{ErrorCode::invalid_argument,
                  "update retention mode is unsupported"};
  }
  if (!state_.has_value()) {
    return Status{ErrorCode::unavailable,
                  "update retention requires signed lifecycle state"};
  }
  const UpdateState &state = *state_;
  const std::string confirmed_name = state.confirmed.present()
      ? relative_slot_target(state.confirmed).filename().string()
      : std::string{};
  const std::string candidate_name = state.candidate.present()
      ? relative_slot_target(state.candidate).filename().string()
      : std::string{};

  struct EligibleSlot {
    std::string name;
    std::uint64_t bytes{0U};
  };
  std::vector<EligibleSlot> eligible;
  UpdateRetentionResult result;
  result.state_generation = state.generation;
  try {
    for (const auto &entry :
         std::filesystem::directory_iterator(policy_.root / "slots")) {
      const std::string name = entry.path().filename().string();
      struct stat metadata{};
      if (::lstat(entry.path().c_str(), &metadata) != 0)
        return io_status("unable to inspect retained update slot",
                         entry.path());
      if (!canonical_slot_name(name) || !S_ISREG(metadata.st_mode) ||
          metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
          (metadata.st_mode & 0777U) != 0400U || metadata.st_size < 0) {
        return Status{ErrorCode::protocol_error,
                      "update retention encountered an unsafe slot"};
      }
      ++result.active_slots;
      if (name == confirmed_name || name == candidate_name) {
        ++result.protected_slots;
        continue;
      }
      const auto bytes = static_cast<std::uint64_t>(metadata.st_size);
      if (result.eligible_bytes >
          std::numeric_limits<std::uint64_t>::max() - bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "update retention byte total is exhausted"};
      }
      result.eligible_bytes += bytes;
      eligible.push_back(EligibleSlot{name, bytes});
    }
  } catch (const std::filesystem::filesystem_error &error) {
    return Status{ErrorCode::io_error,
                  "unable to inspect update retention inventory: " +
                      std::string(error.what())};
  }
  std::sort(eligible.begin(), eligible.end(),
            [](const EligibleSlot &left, const EligibleSlot &right) {
              return left.name < right.name;
            });
  result.eligible_slots = eligible.size();
  auto prior = validate_quarantine(policy_);
  if (!prior.ok()) return prior.status();
  result.prior_quarantine_slots = prior.value();
  if (mode == UpdateRetentionMode::dry_run || eligible.empty()) return result;
  if (eligible.size() >
      kMaximumQuarantinedSlots - result.prior_quarantine_slots) {
    return Status{ErrorCode::resource_exhausted,
                  "recoverable update quarantine lacks capacity"};
  }

  const auto slots = policy_.root / "slots";
  const auto quarantine = policy_.root / "quarantine";
  for (const EligibleSlot &slot : eligible) {
    const std::string destination = slot.name + ".q." +
        std::to_string(state.generation);
    if (::syscall(SYS_renameat2, AT_FDCWD,
                  (slots / slot.name).c_str(), AT_FDCWD,
                  (quarantine / destination).c_str(),
                  RENAME_NOREPLACE) != 0) {
      return errno == EEXIST
          ? Status{ErrorCode::invalid_argument,
                   "update quarantine already contains the exact retention name"}
          : io_status("unable to quarantine update slot",
                      slots / slot.name);
    }
    ++result.quarantined_slots;
    result.quarantined_bytes += slot.bytes;
  }
  const Status synced_slots = sync_directory(slots);
  if (!synced_slots.ok()) return synced_slots;
  const Status synced_quarantine = sync_directory(quarantine);
  if (!synced_quarantine.ok()) return synced_quarantine;
  return result;
}

} // namespace iotox::update
