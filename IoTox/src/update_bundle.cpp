#include "iotox/update_bundle.hpp"

#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <sstream>
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
    'I', 'O', 'T', 'O', 'X', 'U', 'B', '1'};
constexpr std::uint8_t kFormatVersion = 1U;
constexpr std::string_view kSignatureDomain =
    "iotox-update-manifest-signature-v1";
constexpr std::string_view kRecordDomain =
    "iotox-update-manifest-record-v1";
constexpr std::size_t kNamespaceOffset = 96U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kTargetOffset = 160U;
constexpr std::size_t kTargetBytes = 64U;
constexpr std::size_t kVersionOffset = 224U;
constexpr std::size_t kVersionBytes = 32U;
constexpr std::uint64_t kMaximumPolicyPayloadBytes = 1ULL << 40U;
constexpr std::uint64_t kMinimumHealthTimeoutMs = 1000U;
constexpr std::uint64_t kMaximumHealthTimeoutMs = 24U * 60U * 60U * 1000U;
constexpr std::string_view kPolicyHeaderV1 = "iotox-update-policy-v1";
constexpr std::string_view kPolicyHeaderV2 = "iotox-update-policy-v2";
constexpr std::string_view kPolicyHeaderV3 = "iotox-update-policy-v3";

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
  UniqueFd(UniqueFd &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  UniqueFd &operator=(UniqueFd &&other) noexcept {
    if (this != &other) {
      if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
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

private:
  int descriptor_{-1};
};

class PathCleanup {
public:
  explicit PathCleanup(std::filesystem::path path)
      : path_(std::move(path)) {}
  ~PathCleanup() {
    if (armed_ && !path_.empty()) static_cast<void>(::unlink(path_.c_str()));
  }
  PathCleanup(const PathCleanup &) = delete;
  PathCleanup &operator=(const PathCleanup &) = delete;
  void reset(std::filesystem::path path) {
    if (armed_ && !path_.empty()) static_cast<void>(::unlink(path_.c_str()));
    path_ = std::move(path);
    armed_ = true;
  }
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
      value.front() == ' ' || value.back() == ' ') {
    return false;
  }
  return std::all_of(value.begin(), value.end(), [](char character) {
    const auto byte = static_cast<unsigned char>(character);
    return byte >= 0x20U && byte <= 0x7eU;
  });
}

[[nodiscard]] bool canonical_target(std::string_view value) noexcept {
  return value.size() < kTargetBytes && sync::valid_namespace_id(value);
}

[[nodiscard]] bool canonical_namespace(std::string_view value) noexcept {
  return value.size() < kNamespaceBytes && sync::valid_namespace_id(value);
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
                  std::string(label) + " length is not canonical"};
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

[[nodiscard]] bool signer_less(const security::SigningPublicKey &left,
                               const security::SigningPublicKey &right) {
  return std::lexicographical_compare(left.begin(), left.end(), right.begin(),
                                      right.end());
}

[[nodiscard]] bool signer_allowed(
    const UpdatePolicy &policy,
    const security::SigningPublicKey &signer) noexcept {
  return std::binary_search(policy.trusted_signers.begin(),
                            policy.trusted_signers.end(), signer,
                            signer_less);
}

[[nodiscard]] bool signer_list_canonical(
    const std::vector<security::SigningPublicKey> &signers,
    std::size_t maximum, bool require_non_empty) noexcept {
  if ((require_non_empty && signers.empty()) || signers.size() > maximum ||
      !std::is_sorted(signers.begin(), signers.end(), signer_less) ||
      std::adjacent_find(signers.begin(), signers.end()) != signers.end()) {
    return false;
  }
  return std::none_of(signers.begin(), signers.end(), [](const auto &signer) {
    return all_zero(signer);
  });
}

[[nodiscard]] bool signer_sets_overlap(
    const std::vector<security::SigningPublicKey> &active,
    const std::vector<security::SigningPublicKey> &revoked) noexcept {
  return std::any_of(active.begin(), active.end(), [&revoked](const auto &key) {
    return std::binary_search(revoked.begin(), revoked.end(), key,
                              signer_less);
  });
}

[[nodiscard]] Status validate_manifest_fields(
    const SignedUpdateManifest &manifest) {
  if (manifest.payload_kind != PayloadKind::opaque_slot_v1 &&
      manifest.payload_kind != PayloadKind::linux_service_v1) {
    return Status{ErrorCode::unsupported,
                  "signed update payload kind is unsupported"};
  }
  if (manifest.release_sequence == 0U || manifest.payload_bytes == 0U ||
      all_zero(manifest.payload_digest) || all_zero(manifest.signer) ||
      !canonical_namespace(manifest.namespace_id) ||
      !canonical_target(manifest.target) ||
      !canonical_version(manifest.version)) {
    return Status{ErrorCode::invalid_argument,
                  "signed update manifest contains an invalid field"};
  }
  return Status::success();
}

[[nodiscard]] bool same_snapshot(const struct stat &left,
                                 const struct stat &right) noexcept {
  return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
         left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
         left.st_uid == right.st_uid && left.st_size == right.st_size &&
         left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
         left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
         left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
         left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

[[nodiscard]] Status require_private_regular(
    const struct stat &metadata, const std::filesystem::path &path,
    std::string_view label) {
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() || metadata.st_size < 0 ||
      (metadata.st_mode & 0077U) != 0U ||
      (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0U) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not one owner-private regular file: " +
                      path.string()};
  }
  return Status::success();
}

[[nodiscard]] Status require_private_directory(
    const std::filesystem::path &path) {
  struct stat metadata{};
  if (::lstat(path.c_str(), &metadata) != 0) {
    return io_status("unable to inspect update output directory", path);
  }
  if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & 0077U) != 0U ||
      (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0U) {
    return Status{ErrorCode::protocol_error,
                  "update output directory is not owner-private: " +
                      path.string()};
  }
  return Status::success();
}

[[nodiscard]] Result<std::uint64_t> parse_canonical_u64(
    std::string_view value, std::string_view label) {
  if (value.empty() || (value.size() > 1U && value.front() == '0')) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not canonical decimal"};
  }
  std::uint64_t parsed = 0U;
  const auto result = std::from_chars(
      value.data(), value.data() + value.size(), parsed);
  if (result.ec != std::errc{} ||
      result.ptr != value.data() + value.size()) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not an unsigned integer"};
  }
  return parsed;
}

[[nodiscard]] Result<std::string> decode_policy_path(
    std::string_view encoded) {
  if (encoded.empty() || (encoded.size() % 2U) != 0U) {
    return Status{ErrorCode::protocol_error,
                  "update policy root hex is malformed"};
  }
  auto decoded = security::decode_hex_exact(
      encoded, encoded.size() / 2U, "update policy root");
  if (!decoded.ok()) return decoded.status();
  if (std::find(decoded.value().begin(), decoded.value().end(), 0U) !=
      decoded.value().end()) {
    return Status{ErrorCode::protocol_error,
                  "update policy root contains a zero byte"};
  }
  return std::string(decoded.value().begin(), decoded.value().end());
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_policy_file(
    const std::filesystem::path &path, std::uint32_t expected_owner_uid) {
  if (path.empty() || !path.is_absolute() || path.filename().empty() ||
      path.lexically_normal() != path) {
    return Status{ErrorCode::invalid_argument,
                  "update policy path must be normalized and absolute"};
  }
  UniqueFd descriptor(
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!descriptor) return io_status("unable to open update policy", path);
  struct stat before{};
  if (::fstat(descriptor.get(), &before) != 0)
    return io_status("unable to inspect update policy", path);
  if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
      before.st_uid != static_cast<uid_t>(expected_owner_uid) ||
      (before.st_mode & 0077U) != 0U ||
      (before.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0U || before.st_size <= 0 ||
      static_cast<std::uint64_t>(before.st_size) > kMaximumUpdatePolicyBytes) {
    return Status{ErrorCode::protocol_error,
                  "update policy is not one bounded owner-private regular file"};
  }
  std::vector<std::uint8_t> bytes(static_cast<std::size_t>(before.st_size));
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count = ::read(
        descriptor.get(), bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    return count == 0
        ? Status{ErrorCode::protocol_error, "update policy ended early"}
        : io_status("unable to read update policy", path);
  }
  struct stat after{};
  if (::fstat(descriptor.get(), &after) != 0)
    return io_status("unable to revalidate update policy", path);
  if (!same_snapshot(before, after)) {
    return Status{ErrorCode::protocol_error,
                  "update policy changed while it was read"};
  }
  return bytes;
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
    if (count == 0) {
      return Status{ErrorCode::protocol_error,
                    "signed update bundle ended before its manifest was complete"};
    }
    return io_status("unable to read signed update bundle", path);
  }
  return Status::success();
}

[[nodiscard]] Status write_all(int descriptor,
                               std::span<const std::uint8_t> bytes,
                               const std::filesystem::path &path) {
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::write(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    return io_status("unable to write signed update bundle", path);
  }
  return Status::success();
}

struct HashedBytes {
  sync::Digest digest{};
  std::uint64_t bytes{0U};
};

[[nodiscard]] Result<HashedBytes> hash_remaining(
    int descriptor, const std::filesystem::path &path,
    int copy_descriptor = -1) {
  toxsync::Sha256 hasher;
  std::array<std::byte, 64U * 1024U> buffer{};
  std::uint64_t observed = 0U;
  while (true) {
    const ssize_t count = ::read(descriptor, buffer.data(), buffer.size());
    if (count > 0) {
      const std::size_t amount = static_cast<std::size_t>(count);
      if (observed > std::numeric_limits<std::uint64_t>::max() - amount) {
        return Status{ErrorCode::resource_exhausted,
                      "signed update payload byte count overflows"};
      }
      observed += amount;
      hasher.update(std::span<const std::byte>(buffer.data(), amount));
      if (copy_descriptor >= 0) {
        const auto *data = reinterpret_cast<const std::uint8_t *>(buffer.data());
        const Status written = write_all(
            copy_descriptor, std::span<const std::uint8_t>(data, amount), path);
        if (!written.ok()) return written;
      }
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    if (count < 0) return io_status("unable to read update payload", path);
    break;
  }
  const toxsync::Digest256 value = hasher.finish();
  HashedBytes result;
  result.bytes = observed;
  for (std::size_t index = 0U; index < result.digest.size(); ++index) {
    result.digest[index] = std::to_integer<std::uint8_t>(value.bytes[index]);
  }
  return result;
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
  UniqueFd descriptor(
      ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (!descriptor) return io_status("unable to open update directory", path);
  if (::fsync(descriptor.get()) != 0)
    return io_status("unable to sync update directory", path);
  return Status::success();
}

} // namespace

std::string_view payload_kind_name(PayloadKind kind) noexcept {
  switch (kind) {
    case PayloadKind::opaque_slot_v1: return "opaque-slot-v1";
    case PayloadKind::linux_service_v1: return "linux-service-v1";
  }
  return "unknown";
}

Status validate_update_policy(const UpdatePolicy &policy) {
  if (!canonical_namespace(policy.namespace_id) ||
      !canonical_target(policy.target)) {
    return Status{ErrorCode::invalid_argument,
                  "update policy namespace or target is invalid"};
  }
  if (policy.root.empty() || !policy.root.is_absolute() ||
      policy.root == std::filesystem::path("/") ||
      policy.root.lexically_normal() != policy.root) {
    return Status{ErrorCode::invalid_argument,
                  "update policy root must be a normalized absolute non-root path"};
  }
  if (policy.maximum_payload_bytes == 0U ||
      policy.maximum_payload_bytes > kMaximumPolicyPayloadBytes ||
      policy.health_timeout_ms < kMinimumHealthTimeoutMs ||
      policy.health_timeout_ms > kMaximumHealthTimeoutMs) {
    return Status{ErrorCode::invalid_argument,
                  "update policy payload or health bound is invalid"};
  }
  if (policy.payload_kind != PayloadKind::opaque_slot_v1 &&
      policy.payload_kind != PayloadKind::linux_service_v1) {
    return Status{ErrorCode::invalid_argument,
                  "update policy payload kind is unsupported"};
  }
  if (policy.payload_kind == PayloadKind::linux_service_v1 &&
      policy.signer_policy_epoch == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "linux-service-v1 policy requires a positive signer epoch"};
  }
  if (!signer_list_canonical(policy.trusted_signers, kMaximumUpdateSigners,
                             true) ||
      !signer_list_canonical(policy.revoked_signers,
                             kMaximumRevokedUpdateSigners, false) ||
      signer_sets_overlap(policy.trusted_signers, policy.revoked_signers) ||
      (policy.signer_policy_epoch == 0U &&
       !policy.revoked_signers.empty())) {
    return Status{ErrorCode::invalid_argument,
                  "update policy release signers are not canonical"};
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>> encode_update_policy(
    const UpdatePolicy &policy) {
  const Status valid = validate_update_policy(policy);
  if (!valid.ok()) return valid;
  const std::string native_root = policy.root.string();
  const auto *root_data = reinterpret_cast<const std::uint8_t *>(
      native_root.data());
  const bool v3 = policy.payload_kind == PayloadKind::linux_service_v1;
  const bool v2 = !v3 && (policy.signer_policy_epoch != 0U ||
                          !policy.revoked_signers.empty());
  std::ostringstream output;
  output << (v3 ? kPolicyHeaderV3
                : v2 ? kPolicyHeaderV2 : kPolicyHeaderV1) << '\n'
         << "namespace=" << policy.namespace_id << '\n'
         << "target=" << policy.target << '\n'
         << "root-hex="
         << security::hex(std::span<const std::uint8_t>(
                root_data, native_root.size()))
         << '\n'
         << "maximum-payload-bytes=" << policy.maximum_payload_bytes << '\n'
         << "health-timeout-ms=" << policy.health_timeout_ms << '\n';
  if (v2) {
    output << "signer-policy-epoch=" << policy.signer_policy_epoch << '\n';
  }
  if (v3) {
    output << "signer-policy-epoch=" << policy.signer_policy_epoch << '\n'
           << "payload-kind=" << payload_kind_name(policy.payload_kind)
           << '\n';
  }
  for (const auto &signer : policy.trusted_signers) {
    output << "signer=" << security::hex(signer) << '\n';
  }
  for (const auto &signer : policy.revoked_signers) {
    output << "revoked-signer=" << security::hex(signer) << '\n';
  }
  const std::string text = output.str();
  if (text.size() > kMaximumUpdatePolicyBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "canonical update policy exceeds its byte bound"};
  }
  return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<UpdatePolicy> decode_update_policy(
    std::span<const std::uint8_t> bytes) {
  if (bytes.empty() || bytes.size() > kMaximumUpdatePolicyBytes ||
      bytes.back() != static_cast<std::uint8_t>('\n') ||
      std::find(bytes.begin(), bytes.end(), 0U) != bytes.end()) {
    return Status{ErrorCode::protocol_error,
                  "update policy size or termination is invalid"};
  }
  const std::string text(bytes.begin(), bytes.end());
  std::vector<std::string_view> lines;
  std::size_t first = 0U;
  while (first < text.size()) {
    const std::size_t newline = text.find('\n', first);
    if (newline == std::string::npos || newline == first) {
      return Status{ErrorCode::protocol_error,
                    "update policy contains an empty or unterminated line"};
    }
    lines.emplace_back(text.data() + first, newline - first);
    first = newline + 1U;
  }
  const bool v1 = lines[0U] == kPolicyHeaderV1;
  const bool v2 = lines[0U] == kPolicyHeaderV2;
  const bool v3 = lines[0U] == kPolicyHeaderV3;
  if ((!v1 && !v2 && !v3) ||
      (v1 && (lines.size() < 7U ||
              lines.size() > 6U + kMaximumUpdateSigners)) ||
      (v2 && (lines.size() < 8U ||
              lines.size() > 7U + kMaximumUpdateSigners +
                                  kMaximumRevokedUpdateSigners)) ||
      (v3 && (lines.size() < 9U ||
              lines.size() > 8U + kMaximumUpdateSigners +
                                  kMaximumRevokedUpdateSigners))) {
    return Status{ErrorCode::protocol_error,
                  "update policy header or field count is invalid"};
  }
  const auto field = [&lines](std::size_t index,
                              std::string_view prefix)
      -> Result<std::string_view> {
    if (!lines[index].starts_with(prefix) ||
        lines[index].size() == prefix.size()) {
      return Status{ErrorCode::protocol_error,
                    "update policy field is missing or out of order"};
    }
    return lines[index].substr(prefix.size());
  };
  auto namespace_id = field(1U, "namespace=");
  auto target = field(2U, "target=");
  auto root_hex = field(3U, "root-hex=");
  auto maximum = field(4U, "maximum-payload-bytes=");
  auto timeout = field(5U, "health-timeout-ms=");
  if (!namespace_id.ok()) return namespace_id.status();
  if (!target.ok()) return target.status();
  if (!root_hex.ok()) return root_hex.status();
  if (!maximum.ok()) return maximum.status();
  if (!timeout.ok()) return timeout.status();
  auto root = decode_policy_path(root_hex.value());
  if (!root.ok()) return root.status();
  auto maximum_value = parse_canonical_u64(
      maximum.value(), "update policy maximum payload bytes");
  if (!maximum_value.ok()) return maximum_value.status();
  auto timeout_value = parse_canonical_u64(
      timeout.value(), "update policy health timeout");
  if (!timeout_value.ok()) return timeout_value.status();

  UpdatePolicy policy;
  policy.namespace_id = namespace_id.value();
  policy.target = target.value();
  policy.root = root.value();
  policy.maximum_payload_bytes = maximum_value.value();
  policy.health_timeout_ms = timeout_value.value();
  std::size_t first_signer_index = 6U;
  if (v2 || v3) {
    auto epoch = field(6U, "signer-policy-epoch=");
    if (!epoch.ok()) return epoch.status();
    auto epoch_value = parse_canonical_u64(
        epoch.value(), "update policy signer epoch");
    if (!epoch_value.ok()) return epoch_value.status();
    if (epoch_value.value() == 0U) {
      return Status{ErrorCode::protocol_error,
                    "update policy signer epoch must be positive"};
    }
    policy.signer_policy_epoch = epoch_value.value();
    first_signer_index = 7U;
  }
  if (v3) {
    auto kind = field(7U, "payload-kind=");
    if (!kind.ok()) return kind.status();
    if (kind.value() !=
        payload_kind_name(PayloadKind::linux_service_v1)) {
      return Status{ErrorCode::protocol_error,
                    "v3 update policy payload kind is unsupported"};
    }
    policy.payload_kind = PayloadKind::linux_service_v1;
    first_signer_index = 8U;
  }
  bool revoked_section = false;
  for (std::size_t index = first_signer_index; index < lines.size(); ++index) {
    const bool revoked = lines[index].starts_with("revoked-signer=");
    const std::string_view prefix = revoked ? "revoked-signer=" : "signer=";
    if (revoked) {
      if (v1) {
        return Status{ErrorCode::protocol_error,
                      "v1 update policy cannot revoke signers"};
      }
      revoked_section = true;
    } else if (revoked_section) {
      return Status{ErrorCode::protocol_error,
                    "update policy active signer follows revoked signer"};
    }
    auto signer_hex = field(index, prefix);
    if (!signer_hex.ok()) return signer_hex.status();
    auto decoded = security::decode_hex_exact(
        signer_hex.value(), security::kSigningPublicKeyBytes,
        "update policy signer");
    if (!decoded.ok()) return decoded.status();
    security::SigningPublicKey signer{};
    std::copy(decoded.value().begin(), decoded.value().end(), signer.begin());
    if (revoked) {
      policy.revoked_signers.push_back(signer);
    } else {
      policy.trusted_signers.push_back(signer);
    }
  }
  const Status valid = validate_update_policy(policy);
  if (!valid.ok()) return Status{ErrorCode::protocol_error, valid.message()};
  auto canonical = encode_update_policy(policy);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "update policy is not canonically encoded"};
  }
  return policy;
}

Result<UpdatePolicy> load_update_policy(
    const std::filesystem::path &path, std::uint32_t expected_owner_uid) {
  auto bytes = read_policy_file(path, expected_owner_uid);
  if (!bytes.ok()) return bytes.status();
  return decode_update_policy(bytes.value());
}

Result<UpdateManifestBody> encode_update_manifest_body(
    const SignedUpdateManifest &manifest) {
  const Status valid = validate_manifest_fields(manifest);
  if (!valid.ok()) return valid;
  UpdateManifestBody output{};
  std::copy(kMagic.begin(), kMagic.end(), output.begin());
  output[8U] = kFormatVersion;
  output[9U] = static_cast<std::uint8_t>(manifest.payload_kind);
  write_u64(output, 16U, manifest.release_sequence);
  write_u64(output, 24U, manifest.payload_bytes);
  write_array(output, 32U, manifest.payload_digest);
  write_array(output, 64U, manifest.signer);
  write_fixed_string(output, kNamespaceOffset, kNamespaceBytes,
                     manifest.namespace_id);
  write_fixed_string(output, kTargetOffset, kTargetBytes, manifest.target);
  write_fixed_string(output, kVersionOffset, kVersionBytes, manifest.version);
  return output;
}

Result<SignedUpdateManifestBytes> encode_signed_update_manifest(
    const SignedUpdateManifest &manifest) {
  auto body = encode_update_manifest_body(manifest);
  if (!body.ok()) return body.status();
  SignedUpdateManifestBytes output{};
  std::copy(body.value().begin(), body.value().end(), output.begin());
  std::copy(manifest.signature.begin(), manifest.signature.end(),
            output.begin() +
                static_cast<std::ptrdiff_t>(kUpdateManifestBodyBytes));
  return output;
}

Result<SignedUpdateManifest> decode_signed_update_manifest(
    std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSignedUpdateManifestBytes) {
    return Status{ErrorCode::protocol_error,
                  "signed update manifest size is invalid"};
  }
  if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
      bytes[8U] != kFormatVersion ||
      (bytes[9U] != static_cast<std::uint8_t>(
                           PayloadKind::opaque_slot_v1) &&
       bytes[9U] != static_cast<std::uint8_t>(
                           PayloadKind::linux_service_v1)) ||
      !std::all_of(bytes.begin() + 10, bytes.begin() + 16,
                   [](std::uint8_t value) { return value == 0U; })) {
    return Status{ErrorCode::protocol_error,
                  "signed update manifest magic, format, kind, or reserved bytes are invalid"};
  }
  auto namespace_id = read_fixed_string(
      bytes, kNamespaceOffset, kNamespaceBytes, "update namespace");
  auto target = read_fixed_string(
      bytes, kTargetOffset, kTargetBytes, "update target");
  auto version = read_fixed_string(
      bytes, kVersionOffset, kVersionBytes, "update version");
  if (!namespace_id.ok()) return namespace_id.status();
  if (!target.ok()) return target.status();
  if (!version.ok()) return version.status();

  SignedUpdateManifest manifest;
  manifest.payload_kind = static_cast<PayloadKind>(bytes[9U]);
  manifest.release_sequence = read_u64(bytes, 16U);
  manifest.payload_bytes = read_u64(bytes, 24U);
  read_array(bytes, 32U, manifest.payload_digest);
  read_array(bytes, 64U, manifest.signer);
  manifest.namespace_id = std::move(namespace_id).value();
  manifest.target = std::move(target).value();
  manifest.version = std::move(version).value();
  read_array(bytes, kUpdateManifestBodyBytes, manifest.signature);
  const Status valid = validate_manifest_fields(manifest);
  if (!valid.ok()) {
    return Status{ErrorCode::protocol_error, valid.message()};
  }
  if (all_zero(manifest.signature)) {
    return Status{ErrorCode::protocol_error,
                  "signed update manifest signature is zero"};
  }
  auto canonical = encode_signed_update_manifest(manifest);
  if (!canonical.ok() || !std::equal(canonical.value().begin(),
                                    canonical.value().end(), bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "signed update manifest is not canonical"};
  }
  return manifest;
}

Status verify_signed_update_manifest(
    const UpdatePolicy &policy, const SignedUpdateManifest &manifest,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_update_policy(policy);
  if (!valid_policy.ok()) return valid_policy;
  const Status valid_manifest = validate_manifest_fields(manifest);
  if (!valid_manifest.ok()) return valid_manifest;
  if (manifest.namespace_id != policy.namespace_id ||
      manifest.target != policy.target ||
      manifest.payload_kind != policy.payload_kind ||
      manifest.payload_bytes > policy.maximum_payload_bytes ||
      !signer_allowed(policy, manifest.signer)) {
    return Status{ErrorCode::protocol_error,
                  "signed update manifest is not admitted by local policy"};
  }
  auto body = encode_update_manifest_body(manifest);
  if (!body.ok()) return body.status();
  auto digest = sodium.hash(kSignatureDomain, body.value());
  if (!digest.ok()) return digest.status();
  return sodium.verify_detached(manifest.signature, digest.value(),
                                manifest.signer);
}

Result<sync::Digest> update_manifest_record_digest(
    const SignedUpdateManifest &manifest, const security::Sodium &sodium) {
  auto encoded = encode_signed_update_manifest(manifest);
  if (!encoded.ok()) return encoded.status();
  return sodium.hash(kRecordDomain, encoded.value());
}

Result<UpdateBundleInfo> inspect_signed_update_bundle(
    const UpdatePolicy &policy, const std::filesystem::path &bundle,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_update_policy(policy);
  if (!valid_policy.ok()) return valid_policy;
  if (bundle.empty() || !bundle.is_absolute()) {
    return Status{ErrorCode::invalid_argument,
                  "signed update bundle path must be absolute"};
  }
  UniqueFd descriptor(
      ::open(bundle.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!descriptor) return io_status("unable to open signed update bundle", bundle);
  struct stat before{};
  if (::fstat(descriptor.get(), &before) != 0)
    return io_status("unable to inspect signed update bundle", bundle);
  const Status private_file =
      require_private_regular(before, bundle, "signed update bundle");
  if (!private_file.ok()) return private_file;
  if (before.st_size < static_cast<off_t>(kSignedUpdateManifestBytes)) {
    return Status{ErrorCode::protocol_error,
                  "signed update bundle is shorter than its manifest"};
  }
  SignedUpdateManifestBytes manifest_bytes{};
  const Status read = read_exact(descriptor.get(), manifest_bytes, bundle);
  if (!read.ok()) return read;
  auto manifest = decode_signed_update_manifest(manifest_bytes);
  if (!manifest.ok()) return manifest.status();
  const Status verified =
      verify_signed_update_manifest(policy, manifest.value(), sodium);
  if (!verified.ok()) return verified;
  if (manifest.value().payload_bytes >
      std::numeric_limits<std::uint64_t>::max() -
          kSignedUpdateManifestBytes ||
      static_cast<std::uint64_t>(before.st_size) !=
          kSignedUpdateManifestBytes + manifest.value().payload_bytes) {
    return Status{ErrorCode::protocol_error,
                  "signed update bundle payload length is not exact"};
  }
  auto hashed = hash_remaining(descriptor.get(), bundle);
  if (!hashed.ok()) return hashed.status();
  struct stat after{};
  if (::fstat(descriptor.get(), &after) != 0)
    return io_status("unable to revalidate signed update bundle", bundle);
  if (!same_snapshot(before, after) ||
      hashed.value().bytes != manifest.value().payload_bytes ||
      hashed.value().digest != manifest.value().payload_digest) {
    return Status{ErrorCode::protocol_error,
                  "signed update bundle payload or descriptor snapshot changed"};
  }
  auto record = update_manifest_record_digest(manifest.value(), sodium);
  if (!record.ok()) return record.status();
  return UpdateBundleInfo{manifest.value(), record.value(), bundle};
}

Result<UpdateBundleInfo> create_signed_update_bundle(
    const UpdatePolicy &policy, const std::filesystem::path &payload,
    const std::filesystem::path &output, std::uint64_t release_sequence,
    std::string version, const security::DeviceIdentity &signer,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_update_policy(policy);
  if (!valid_policy.ok()) return valid_policy;
  if (release_sequence == 0U || !canonical_version(version) ||
      signer.role() != security::SigningIdentityRole::release ||
      !signer_allowed(policy, signer.public_key())) {
    return Status{ErrorCode::invalid_argument,
                  "update bundle signer, sequence, or version is not admitted"};
  }
  if (payload.empty() || output.empty() || !payload.is_absolute() ||
      !output.is_absolute() || payload == output || output.filename().empty()) {
    return Status{ErrorCode::invalid_argument,
                  "update payload and output must be distinct absolute paths"};
  }
  const std::filesystem::path parent = output.parent_path();
  const Status private_parent = require_private_directory(parent);
  if (!private_parent.ok()) return private_parent;

  UniqueFd source(
      ::open(payload.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (!source) return io_status("unable to open update payload", payload);
  struct stat before{};
  if (::fstat(source.get(), &before) != 0)
    return io_status("unable to inspect update payload", payload);
  const Status private_file =
      require_private_regular(before, payload, "update payload");
  if (!private_file.ok()) return private_file;
  if (before.st_size == 0 ||
      static_cast<std::uint64_t>(before.st_size) >
          policy.maximum_payload_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "update payload size is outside policy"};
  }
  auto first_hash = hash_remaining(source.get(), payload);
  if (!first_hash.ok()) return first_hash.status();
  struct stat after_hash{};
  if (::fstat(source.get(), &after_hash) != 0)
    return io_status("unable to revalidate update payload", payload);
  if (!same_snapshot(before, after_hash) ||
      first_hash.value().bytes != static_cast<std::uint64_t>(before.st_size)) {
    return Status{ErrorCode::protocol_error,
                  "update payload changed while it was hashed"};
  }

  SignedUpdateManifest manifest;
  manifest.payload_kind = policy.payload_kind;
  manifest.release_sequence = release_sequence;
  manifest.payload_bytes = first_hash.value().bytes;
  manifest.payload_digest = first_hash.value().digest;
  manifest.signer = signer.public_key();
  manifest.namespace_id = policy.namespace_id;
  manifest.target = policy.target;
  manifest.version = std::move(version);
  auto body = encode_update_manifest_body(manifest);
  if (!body.ok()) return body.status();
  auto signing_digest = sodium.hash(kSignatureDomain, body.value());
  if (!signing_digest.ok()) return signing_digest.status();
  auto signature = signer.sign(signing_digest.value());
  if (!signature.ok()) return signature.status();
  manifest.signature = signature.value();
  const Status verified = verify_signed_update_manifest(policy, manifest, sodium);
  if (!verified.ok()) return verified;
  auto encoded = encode_signed_update_manifest(manifest);
  if (!encoded.ok()) return encoded.status();

  std::string pattern =
      (parent / ("." + output.filename().string() + ".part.XXXXXX")).string();
  std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
  mutable_pattern.push_back('\0');
  UniqueFd destination(::mkstemp(mutable_pattern.data()));
  if (!destination)
    return io_status("unable to create update bundle temporary", parent);
  const std::filesystem::path temporary{mutable_pattern.data()};
  PathCleanup cleanup(temporary);
  if (::fchmod(destination.get(), 0600) != 0)
    return io_status("unable to secure update bundle temporary", temporary);
  const Status wrote_manifest = write_all(
      destination.get(), encoded.value(), temporary);
  if (!wrote_manifest.ok()) return wrote_manifest;
  if (::lseek(source.get(), 0, SEEK_SET) != 0)
    return io_status("unable to rewind update payload", payload);
  auto copied = hash_remaining(source.get(), temporary, destination.get());
  if (!copied.ok()) return copied.status();
  struct stat after_copy{};
  if (::fstat(source.get(), &after_copy) != 0)
    return io_status("unable to revalidate copied update payload", payload);
  if (!same_snapshot(before, after_copy) ||
      copied.value().bytes != first_hash.value().bytes ||
      copied.value().digest != first_hash.value().digest) {
    return Status{ErrorCode::protocol_error,
                  "update payload changed while it was copied"};
  }
  if (::fsync(destination.get()) != 0)
    return io_status("unable to sync update bundle temporary", temporary);
  const int destination_fd = destination.release();
  if (::close(destination_fd) != 0)
    return io_status("unable to close update bundle temporary", temporary);
  const int source_fd = source.release();
  if (::close(source_fd) != 0)
    return io_status("unable to close update payload", payload);

  if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                output.c_str(), RENAME_NOREPLACE) != 0) {
    const int saved = errno;
    return Status{
        saved == EEXIST ? ErrorCode::invalid_argument : ErrorCode::io_error,
        saved == EEXIST
            ? "signed update bundle output already exists"
            : "unable to commit signed update bundle with no-replace: " +
                  std::string(std::strerror(saved))};
  }
  cleanup.reset(output);
  const Status synced = sync_directory(parent);
  if (!synced.ok()) return synced;
  auto inspected = inspect_signed_update_bundle(policy, output, sodium);
  if (!inspected.ok()) return inspected.status();
  if (inspected.value().manifest != manifest) {
    return Status{ErrorCode::internal_error,
                  "created update bundle did not round-trip exactly"};
  }
  cleanup.release();
  return inspected;
}

} // namespace iotox::update
