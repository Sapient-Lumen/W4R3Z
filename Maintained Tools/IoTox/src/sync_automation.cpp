#include "iotox/sync_automation.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagicV1 = {'I', 'O', 'T', 'X',
                                                   'S', 'A', 'U', '1'};
constexpr std::array<std::uint8_t, 8U> kMagicV2 = {'I', 'O', 'T', 'X',
                                                   'S', 'A', 'U', '2'};
constexpr std::uint8_t kFormatV1 = 1U;
constexpr std::uint8_t kFormatV2 = kCurrentSyncAutomationRecordFormat;
constexpr std::size_t kSignerOffset = 40U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kV1PrincipalOffset = 72U;
constexpr std::size_t kV1NamespaceOffset = 104U;
constexpr std::size_t kV1PathOffset = kV1NamespaceOffset + kNamespaceBytes;
constexpr std::size_t kV1BodyBytes =
    kV1PathOffset + kMaximumSyncAutomationPathBytes;
constexpr std::size_t kV1RecordBytes =
    kV1BodyBytes + security::kSignatureBytes;
constexpr std::size_t kV2NamespaceOffset = 72U;
constexpr std::size_t kV2PrincipalOffset =
    kV2NamespaceOffset + kNamespaceBytes;
constexpr std::size_t kV2PrincipalSlots = 16U;
constexpr std::size_t kV2PrincipalsBytes =
    kV2PrincipalSlots * security::kSigningPublicKeyBytes;
constexpr std::size_t kV2PathOffset =
    kV2PrincipalOffset + kV2PrincipalsBytes;
constexpr std::size_t kV2BodyBytes =
    kV2PathOffset + kMaximumSyncAutomationPathBytes;
constexpr std::size_t kV2RecordBytes =
    kV2BodyBytes + security::kSignatureBytes;
constexpr std::string_view kSignatureDomainV1 =
    "iotox-sync-automation-policy-signature-v1";
constexpr std::string_view kSignatureDomainV2 =
    "iotox-sync-automation-policy-signature-v2";

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

void write_u16(std::span<std::uint8_t> output, std::size_t offset,
               std::uint16_t value) {
  output[offset] = static_cast<std::uint8_t>((value >> 8U) & 0xffU);
  output[offset + 1U] = static_cast<std::uint8_t>(value & 0xffU);
}

void write_u32(std::span<std::uint8_t> output, std::size_t offset,
               std::uint32_t value) {
  for (std::size_t index = 0U; index < 4U; ++index) {
    const unsigned int shift = static_cast<unsigned int>((3U - index) * 8U);
    output[offset + index] =
        static_cast<std::uint8_t>((value >> shift) & 0xffU);
  }
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    const unsigned int shift = static_cast<unsigned int>((7U - index) * 8U);
    output[offset + index] =
        static_cast<std::uint8_t>((value >> shift) & 0xffU);
  }
}

std::uint16_t read_u16(std::span<const std::uint8_t> bytes,
                       std::size_t offset) {
  return static_cast<std::uint16_t>(
      (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
      static_cast<std::uint16_t>(bytes[offset + 1U]));
}

std::uint32_t read_u32(std::span<const std::uint8_t> bytes,
                       std::size_t offset) {
  std::uint32_t value = 0U;
  for (std::size_t index = 0U; index < 4U; ++index)
    value = static_cast<std::uint32_t>((value << 8U) | bytes[offset + index]);
  return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                       std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index)
    value = (value << 8U) | bytes[offset + index];
  return value;
}

bool canonical_absolute_path(std::string_view text) {
  if (text.empty() || text.size() > kMaximumSyncAutomationPathBytes ||
      text.find('\0') != std::string_view::npos) {
    return false;
  }
  const std::filesystem::path path{text};
  return path.is_absolute() && path != path.root_path() &&
         path.lexically_normal().string() == text;
}

Status inspect_private_directory(const std::filesystem::path &path,
                                 std::string_view label) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
      S_ISLNK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0700)) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) +
                      " is not one private owner-owned directory"};
  }
  return Status::success();
}

Status prepare_automation_directory(const std::filesystem::path &root) {
  const Status parent = inspect_private_directory(root.parent_path(),
                                                  "sync policy root");
  if (!parent.ok())
    return parent;
  struct stat metadata {};
  if (::lstat(root.c_str(), &metadata) == 0)
    return inspect_private_directory(root, "sync automation directory");
  if (errno != ENOENT) {
    return Status{ErrorCode::io_error,
                  "unable to inspect sync automation directory: " +
                      std::string(std::strerror(errno))};
  }
  if (::mkdir(root.c_str(), static_cast<mode_t>(0700)) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to create sync automation directory: " +
                      std::string(std::strerror(errno))};
  }
  return inspect_private_directory(root, "sync automation directory");
}

Result<std::vector<std::uint8_t>> read_policy_file(
    const std::filesystem::path &path) {
  const int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    return Status{errno == ENOENT ? ErrorCode::not_found : ErrorCode::io_error,
                  "unable to open sync automation record: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
      metadata.st_nlink != 1 || metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      (metadata.st_size != static_cast<off_t>(kV1RecordBytes) &&
       metadata.st_size != static_cast<off_t>(kV2RecordBytes))) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "sync automation record is not one private fixed-size file"};
  }
  std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::read(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete sync automation record"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close sync automation record"};
  }
  return bytes;
}

Result<std::vector<std::uint8_t>> encode_body_v1(
    const SyncAutomationPolicy &policy) {
  const Status valid = validate_sync_automation_spec(policy);
  if (!valid.ok())
    return valid;
  if (policy.record_format != kFormatV1 || policy.generation == 0U ||
      all_zero(policy.signer) || policy.source_principals.size() > 1U) {
    return Status{ErrorCode::invalid_argument,
                  "legacy sync automation policy metadata is invalid"};
  }
  std::vector<std::uint8_t> body(kV1BodyBytes);
  std::copy(kMagicV1.begin(), kMagicV1.end(), body.begin());
  body[8U] = kFormatV1;
  body[9U] = static_cast<std::uint8_t>(policy.mode);
  body[10U] = static_cast<std::uint8_t>(policy.activation);
  body[11U] = static_cast<std::uint8_t>(policy.namespace_id.size());
  write_u16(body, 12U, static_cast<std::uint16_t>(policy.source_path.size()));
  write_u64(body, 16U, policy.generation);
  write_u32(body, 24U, policy.interval_ms);
  write_u32(body, 28U, policy.retry_initial_ms);
  write_u32(body, 32U, policy.retry_maximum_ms);
  std::copy(policy.signer.begin(), policy.signer.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kSignerOffset));
  if (!policy.source_principals.empty()) {
    std::copy(policy.source_principals.front().begin(),
              policy.source_principals.front().end(),
              body.begin() + static_cast<std::ptrdiff_t>(kV1PrincipalOffset));
  }
  std::copy(policy.namespace_id.begin(), policy.namespace_id.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kV1NamespaceOffset));
  std::copy(policy.source_path.begin(), policy.source_path.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kV1PathOffset));
  return body;
}

Result<std::vector<std::uint8_t>> encode_body_v2(
    const SyncAutomationPolicy &policy) {
  const Status valid = validate_sync_automation_spec(policy);
  if (!valid.ok())
    return valid;
  if (policy.record_format != kFormatV2 || policy.generation == 0U ||
      all_zero(policy.signer)) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation policy generation, format, or signer is invalid"};
  }
  std::vector<std::uint8_t> body(kV2BodyBytes);
  std::copy(kMagicV2.begin(), kMagicV2.end(), body.begin());
  body[8U] = kFormatV2;
  body[9U] = static_cast<std::uint8_t>(policy.mode);
  body[10U] = static_cast<std::uint8_t>(policy.activation);
  body[11U] = static_cast<std::uint8_t>(policy.namespace_id.size());
  write_u16(body, 12U, static_cast<std::uint16_t>(policy.source_path.size()));
  body[14U] = static_cast<std::uint8_t>(policy.source_principals.size());
  write_u64(body, 16U, policy.generation);
  write_u32(body, 24U, policy.interval_ms);
  write_u32(body, 28U, policy.retry_initial_ms);
  write_u32(body, 32U, policy.retry_maximum_ms);
  std::copy(policy.signer.begin(), policy.signer.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kSignerOffset));
  std::copy(policy.namespace_id.begin(), policy.namespace_id.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kV2NamespaceOffset));
  for (std::size_t index = 0U; index < policy.source_principals.size();
       ++index) {
    std::copy(policy.source_principals[index].begin(),
              policy.source_principals[index].end(),
              body.begin() + static_cast<std::ptrdiff_t>(
                                 kV2PrincipalOffset +
                                 index * security::kSigningPublicKeyBytes));
  }
  std::copy(policy.source_path.begin(), policy.source_path.end(),
            body.begin() + static_cast<std::ptrdiff_t>(kV2PathOffset));
  return body;
}

Result<std::vector<std::uint8_t>> encode_body(
    const SyncAutomationPolicy &policy) {
  if (policy.record_format == kFormatV1)
    return encode_body_v1(policy);
  return encode_body_v2(policy);
}

std::string_view signature_domain(std::uint8_t format) {
  return format == kFormatV1 ? kSignatureDomainV1 : kSignatureDomainV2;
}

bool same_spec(const SyncAutomationPolicy &policy,
               const SyncAutomationSpec &spec) {
  return static_cast<const SyncAutomationSpec &>(policy) == spec;
}

void saturating_increment(std::uint64_t &value) noexcept {
  if (value != std::numeric_limits<std::uint64_t>::max())
    ++value;
}

std::uint64_t saturating_add(std::uint64_t left,
                             std::uint64_t right) noexcept {
  if (right > std::numeric_limits<std::uint64_t>::max() - left)
    return std::numeric_limits<std::uint64_t>::max();
  return left + right;
}

std::uint64_t retry_delay(const SyncAutomationPolicy &policy,
                          std::uint64_t failures) noexcept {
  std::uint64_t delay = policy.retry_initial_ms;
  for (std::uint64_t step = 1U; step < failures &&
                               delay < policy.retry_maximum_ms;
       ++step) {
    delay = std::min<std::uint64_t>(policy.retry_maximum_ms,
                                    saturating_add(delay, delay));
  }
  return std::min<std::uint64_t>(delay, policy.retry_maximum_ms);
}

template <typename Entry>
void apply_source_republish_delay(Entry &entry,
                                  std::uint64_t now_ms) noexcept {
  if (!entry.next_source_publish_ms || entry.source_republish_delay_ms == 0U)
    return;
  const std::uint64_t delayed =
      saturating_add(now_ms, entry.source_republish_delay_ms);
  if (*entry.next_source_publish_ms < delayed)
    entry.next_source_publish_ms = delayed;
}

template <typename Entry>
void refresh_source_publish_pending(Entry &entry) noexcept {
  entry.runtime.source_publish_pending = entry.next_source_publish_ms.has_value();
  if (!entry.runtime.source_publish_pending)
    entry.source_republish_delay_ms = 0U;
}

template <typename Entry>
bool delayed_source_republish_pending(const Entry &entry) noexcept {
  return entry.next_source_publish_ms.has_value() &&
         entry.source_republish_delay_ms != 0U;
}

} // namespace

std::string_view
sync_automation_mode_name(SyncAutomationMode mode) noexcept {
  switch (mode) {
  case SyncAutomationMode::disabled:
    return "disabled";
  case SyncAutomationMode::publish:
    return "publish";
  case SyncAutomationMode::follow:
    return "follow";
  case SyncAutomationMode::writable:
      return "writable";
  case SyncAutomationMode::bidirectional:
      return "bidirectional";
  }
  return "unknown";
}

std::string_view sync_automation_activation_name(
    SyncAutomationActivation activation) noexcept {
  switch (activation) {
  case SyncAutomationActivation::pull_only:
    return "pull";
  case SyncAutomationActivation::verified:
    return "verified";
  }
  return "unknown";
}

std::string_view sync_automation_store_decision_name(
    SyncAutomationStoreDecision decision) noexcept {
  switch (decision) {
  case SyncAutomationStoreDecision::created:
    return "created";
  case SyncAutomationStoreDecision::replaced:
    return "replaced";
  case SyncAutomationStoreDecision::disabled:
    return "disabled";
  case SyncAutomationStoreDecision::duplicate:
    return "duplicate";
  }
  return "unknown";
}

Status validate_sync_automation_spec(const SyncAutomationSpec &spec) {
  if (!valid_namespace_id(spec.namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation namespace id is invalid"};
  }
  if (spec.interval_ms < 1000U || spec.interval_ms > 86400000U ||
      spec.retry_initial_ms < 100U ||
      spec.retry_initial_ms > spec.retry_maximum_ms ||
      spec.retry_maximum_ms > 86400000U) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation timing bounds are invalid"};
  }
  if (spec.source_principals.size() >
          kMaximumSyncAutomationSourcePrincipals ||
      !std::is_sorted(spec.source_principals.begin(),
                      spec.source_principals.end()) ||
      std::adjacent_find(spec.source_principals.begin(),
                         spec.source_principals.end()) !=
          spec.source_principals.end() ||
      std::any_of(spec.source_principals.begin(),
                  spec.source_principals.end(), [](const auto &principal) {
                    return all_zero(principal);
                  })) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation source principals are not canonical"};
  }
  if (spec.mode == SyncAutomationMode::disabled) {
    if (spec.activation != SyncAutomationActivation::pull_only ||
        !spec.source_principals.empty() || !spec.source_path.empty()) {
      return Status{ErrorCode::invalid_argument,
                    "disabled sync automation retains an effect"};
    }
    return Status::success();
  }
  if (spec.mode == SyncAutomationMode::publish) {
    if (spec.activation != SyncAutomationActivation::pull_only ||
        !spec.source_principals.empty() ||
        !canonical_absolute_path(spec.source_path)) {
      return Status{ErrorCode::invalid_argument,
                    "automatic publication policy is invalid"};
    }
    return Status::success();
  }
  if (spec.mode == SyncAutomationMode::follow) {
    if ((spec.activation != SyncAutomationActivation::pull_only &&
         spec.activation != SyncAutomationActivation::verified) ||
        spec.source_principals.size() != 1U || !spec.source_path.empty()) {
      return Status{ErrorCode::invalid_argument,
                    "automatic follow policy is invalid"};
    }
    return Status::success();
  }
  if (spec.mode == SyncAutomationMode::bidirectional) {
      if (spec.activation != SyncAutomationActivation::pull_only ||
          spec.source_principals.empty() ||
          !canonical_absolute_path(spec.source_path)) {
          return Status{ErrorCode::invalid_argument,
                        "bidirectional sync automation policy is invalid"};
      }
      return Status::success();
  }
  if (spec.mode == SyncAutomationMode::writable) {
      if (spec.activation != SyncAutomationActivation::pull_only ||
          !spec.source_principals.empty() ||
          !canonical_absolute_path(spec.source_path)) {
          return Status{ErrorCode::invalid_argument,
                        "writable sync automation policy is invalid"};
      }
      return Status::success();
  }
  return Status{ErrorCode::invalid_argument,
                "sync automation mode is invalid"};
}

Result<std::vector<std::uint8_t>>
encode_sync_automation_policy(const SyncAutomationPolicy &policy) {
  auto body = encode_body(policy);
  if (!body.ok())
    return body.status();
  std::vector<std::uint8_t> output(body.value().begin(), body.value().end());
  output.insert(output.end(), policy.signature.begin(), policy.signature.end());
  return output;
}

Result<SyncAutomationPolicy>
decode_sync_automation_policy(std::span<const std::uint8_t> bytes) {
  const bool v1 = bytes.size() == kV1RecordBytes &&
                  std::equal(kMagicV1.begin(), kMagicV1.end(), bytes.begin()) &&
                  bytes[8U] == kFormatV1;
  const bool v2 = bytes.size() == kV2RecordBytes &&
                  std::equal(kMagicV2.begin(), kMagicV2.end(), bytes.begin()) &&
                  bytes[8U] == kFormatV2;
  if ((!v1 && !v2) || bytes[11U] == 0U ||
      bytes[11U] > kNamespaceBytes ||
      (v1 && !all_zero(bytes.subspan(14U, 2U))) ||
      (v2 && (bytes[14U] > kMaximumSyncAutomationSourcePrincipals ||
              bytes[15U] != 0U)) ||
      !all_zero(bytes.subspan(36U, 4U))) {
    return Status{ErrorCode::protocol_error,
                  "sync automation record header is invalid"};
  }
  const std::size_t namespace_bytes = bytes[11U];
  const std::size_t path_bytes = read_u16(bytes, 12U);
  const std::size_t namespace_offset =
      v1 ? kV1NamespaceOffset : kV2NamespaceOffset;
  const std::size_t path_offset = v1 ? kV1PathOffset : kV2PathOffset;
  if (path_bytes > kMaximumSyncAutomationPathBytes ||
      !all_zero(bytes.subspan(namespace_offset + namespace_bytes,
                              kNamespaceBytes - namespace_bytes)) ||
      !all_zero(bytes.subspan(path_offset + path_bytes,
                              kMaximumSyncAutomationPathBytes - path_bytes))) {
    return Status{ErrorCode::protocol_error,
                  "sync automation record padding is invalid"};
  }
  SyncAutomationPolicy policy;
  policy.record_format = v1 ? kFormatV1 : kFormatV2;
  policy.mode = static_cast<SyncAutomationMode>(bytes[9U]);
  policy.activation = static_cast<SyncAutomationActivation>(bytes[10U]);
  policy.generation = read_u64(bytes, 16U);
  policy.interval_ms = read_u32(bytes, 24U);
  policy.retry_initial_ms = read_u32(bytes, 28U);
  policy.retry_maximum_ms = read_u32(bytes, 32U);
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kSignerOffset),
              policy.signer.size(), policy.signer.begin());
  if (v1) {
    PrincipalId principal{};
    std::copy_n(
        bytes.begin() + static_cast<std::ptrdiff_t>(kV1PrincipalOffset),
        principal.size(), principal.begin());
    if (!all_zero(principal))
      policy.source_principals.push_back(principal);
  } else {
    const std::size_t principal_count = bytes[14U];
    policy.source_principals.reserve(principal_count);
    for (std::size_t index = 0U; index < principal_count; ++index) {
      PrincipalId principal{};
      std::copy_n(
          bytes.begin() + static_cast<std::ptrdiff_t>(
                              kV2PrincipalOffset +
                              index * security::kSigningPublicKeyBytes),
          principal.size(), principal.begin());
      policy.source_principals.push_back(principal);
    }
    const std::size_t used =
        principal_count * security::kSigningPublicKeyBytes;
    if (!all_zero(bytes.subspan(kV2PrincipalOffset + used,
                                kV2PrincipalsBytes - used))) {
      return Status{ErrorCode::protocol_error,
                    "sync automation principal padding is invalid"};
    }
  }
  policy.namespace_id.assign(
      reinterpret_cast<const char *>(bytes.data() + namespace_offset),
      namespace_bytes);
  policy.source_path.assign(
      reinterpret_cast<const char *>(bytes.data() + path_offset), path_bytes);
  const std::size_t body_bytes = v1 ? kV1BodyBytes : kV2BodyBytes;
  std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(body_bytes),
              policy.signature.size(), policy.signature.begin());
  auto canonical = encode_sync_automation_policy(policy);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync automation record is not canonical"};
  }
  return policy;
}

Status verify_sync_automation_policy(
    const SyncAutomationPolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  if (all_zero(expected_device) || policy.signer != expected_device) {
    return Status{ErrorCode::protocol_error,
                  "sync automation policy signer is not this device"};
  }
  auto body = encode_body(policy);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(signature_domain(policy.record_format),
                            body.value());
  if (!digest.ok())
    return digest.status();
  return sodium.verify_detached(policy.signature, digest.value(),
                                policy.signer);
}

SyncAutomationStore::SyncAutomationStore(std::filesystem::path policy_root)
    : root_(std::move(policy_root) / "automation") {}

std::filesystem::path
SyncAutomationStore::path_for(std::string_view namespace_id) const {
  return root_ / (std::string(namespace_id) + ".automation");
}

Result<std::vector<SyncAutomationPolicy>> SyncAutomationStore::load(
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) const {
  struct stat metadata {};
  if (::lstat(root_.c_str(), &metadata) != 0) {
    if (errno == ENOENT)
      return std::vector<SyncAutomationPolicy>{};
    return Status{ErrorCode::io_error,
                  "unable to inspect sync automation directory: " +
                      std::string(std::strerror(errno))};
  }
  const Status safe =
      inspect_private_directory(root_, "sync automation directory");
  if (!safe.ok())
    return safe;
  std::vector<SyncAutomationPolicy> policies;
  std::error_code error;
  for (std::filesystem::directory_iterator iterator(root_, error), end;
       !error && iterator != end; iterator.increment(error)) {
    const std::filesystem::path path = iterator->path();
    const std::string name = path.filename().string();
    constexpr std::string_view suffix = ".automation";
    if (name.size() <= suffix.size() ||
        name.substr(name.size() - suffix.size()) != suffix) {
      return Status{ErrorCode::protocol_error,
                    "sync automation directory has an unexpected entry"};
    }
    const std::string namespace_id =
        name.substr(0U, name.size() - suffix.size());
    if (!valid_namespace_id(namespace_id)) {
      return Status{ErrorCode::protocol_error,
                    "sync automation filename is invalid"};
    }
    auto bytes = read_policy_file(path);
    if (!bytes.ok())
      return bytes.status();
    auto policy = decode_sync_automation_policy(bytes.value());
    if (!policy.ok())
      return policy.status();
    if (policy.value().namespace_id != namespace_id) {
      return Status{ErrorCode::protocol_error,
                    "sync automation filename and record disagree"};
    }
    const Status verified = verify_sync_automation_policy(
        policy.value(), expected_device, sodium);
    if (!verified.ok())
      return verified;
    policies.push_back(std::move(policy).value());
    if (policies.size() > kMaximumNamespaces) {
      return Status{ErrorCode::resource_exhausted,
                    "sync automation policy population exceeds the namespace bound"};
    }
  }
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to enumerate sync automation directory: " +
                      error.message()};
  }
  std::sort(policies.begin(), policies.end(),
            [](const SyncAutomationPolicy &left,
               const SyncAutomationPolicy &right) {
              return left.namespace_id < right.namespace_id;
            });
  return policies;
}

Result<SyncAutomationStoreResult> SyncAutomationStore::put(
    const SyncAutomationSpec &spec, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  const Status valid = validate_sync_automation_spec(spec);
  if (!valid.ok())
    return valid;
  const Status prepared = prepare_automation_directory(root_);
  if (!prepared.ok())
    return prepared;
  auto current = load(identity.public_key(), sodium);
  if (!current.ok())
    return current.status();
  const auto found = std::find_if(
      current.value().begin(), current.value().end(),
      [&spec](const SyncAutomationPolicy &candidate) {
        return candidate.namespace_id == spec.namespace_id;
      });
  if (found != current.value().end() && same_spec(*found, spec)) {
    return SyncAutomationStoreResult{SyncAutomationStoreDecision::duplicate,
                                     *found};
  }
  SyncAutomationPolicy policy;
  static_cast<SyncAutomationSpec &>(policy) = spec;
  policy.record_format = kFormatV2;
  policy.generation = found == current.value().end() ? 1U : found->generation;
  if (found != current.value().end()) {
    if (policy.generation == std::numeric_limits<std::uint64_t>::max()) {
      return Status{ErrorCode::resource_exhausted,
                    "sync automation policy generation is exhausted"};
    }
    ++policy.generation;
  }
  policy.signer = identity.public_key();
  auto body = encode_body(policy);
  if (!body.ok())
    return body.status();
  auto digest = sodium.hash(kSignatureDomainV2, body.value());
  if (!digest.ok())
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature.ok())
    return signature.status();
  policy.signature = signature.value();
  const Status verified =
      verify_sync_automation_policy(policy, identity.public_key(), sodium);
  if (!verified.ok())
    return verified;
  auto encoded = encode_sync_automation_policy(policy);
  if (!encoded.ok())
    return encoded.status();
  const Status stored = StateStore::write_atomic(
      path_for(policy.namespace_id), encoded.value());
  if (!stored.ok())
    return stored;
  SyncAutomationStoreDecision decision =
      found == current.value().end()
          ? SyncAutomationStoreDecision::created
          : SyncAutomationStoreDecision::replaced;
  if (policy.mode == SyncAutomationMode::disabled)
    decision = SyncAutomationStoreDecision::disabled;
  return SyncAutomationStoreResult{decision, std::move(policy)};
}

Result<SyncAutomationStoreResult> SyncAutomationStore::disable(
    std::string_view namespace_id,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  SyncAutomationSpec spec;
  spec.namespace_id = std::string(namespace_id);
  spec.mode = SyncAutomationMode::disabled;
  return put(spec, identity, sodium);
}

Status SyncAutomationScheduler::replace(
    std::vector<SyncAutomationPolicy> policies, std::uint64_t now_ms) {
  if (policies.size() > kMaximumNamespaces) {
    return Status{ErrorCode::resource_exhausted,
                  "sync automation scheduler policy bound is exhausted"};
  }
  std::sort(policies.begin(), policies.end(),
            [](const SyncAutomationPolicy &left,
               const SyncAutomationPolicy &right) {
              return left.namespace_id < right.namespace_id;
            });
  for (std::size_t index = 0U; index < policies.size(); ++index) {
    const Status valid = validate_sync_automation_spec(policies[index]);
    if (!valid.ok() || policies[index].generation == 0U ||
        (index != 0U && policies[index - 1U].namespace_id ==
                            policies[index].namespace_id)) {
      return Status{ErrorCode::invalid_argument,
                    "sync automation scheduler policies are invalid"};
    }
  }
  std::scoped_lock lock(mutex_);
  std::vector<Entry> replacement;
  replacement.reserve(policies.size());
  for (SyncAutomationPolicy &policy : policies) {
    const auto prior = std::find_if(
        entries_.begin(), entries_.end(),
        [&policy](const Entry &entry) { return entry.policy == policy; });
    if (prior != entries_.end()) {
      replacement.push_back(*prior);
      continue;
    }
    SyncAutomationRuntimeSnapshot runtime;
    runtime.namespace_id = policy.namespace_id;
    runtime.mode = policy.mode;
    runtime.activation = policy.activation;
    runtime.policy_generation = policy.generation;
    runtime.next_periodic_ms = now_ms;
    runtime.next_activation_ms = now_ms;
    Entry entry;
    entry.peer_runtime.resize(policy.source_principals.size(),
                              PeerRuntime{now_ms, 0U});
    entry.policy = std::move(policy);
    entry.runtime = std::move(runtime);
    replacement.push_back(std::move(entry));
  }
  entries_ = std::move(replacement);
  return Status::success();
}

std::vector<SyncAutomationAction>
SyncAutomationScheduler::claim_periodic(std::uint64_t now_ms) {
  std::scoped_lock lock(mutex_);
  std::vector<SyncAutomationAction> actions;
  for (Entry &entry : entries_) {
    if (entry.policy.mode == SyncAutomationMode::disabled ||
        entry.runtime.periodic_busy ||
        now_ms < entry.runtime.next_periodic_ms) {
      continue;
    }
    if ((entry.policy.mode == SyncAutomationMode::publish ||
         entry.policy.mode == SyncAutomationMode::writable) &&
        delayed_source_republish_pending(entry) &&
        *entry.next_source_publish_ms > now_ms) {
      entry.runtime.next_periodic_ms = *entry.next_source_publish_ms;
      continue;
    }
    SyncAutomationAction action;
    action.policy = entry.policy;
    if ((entry.policy.mode == SyncAutomationMode::publish ||
         entry.policy.mode == SyncAutomationMode::writable ||
         entry.policy.mode == SyncAutomationMode::bidirectional) &&
        entry.next_source_publish_ms &&
        *entry.next_source_publish_ms <= now_ms) {
      action.kind = SyncAutomationActionKind::publish;
      entry.next_source_publish_ms.reset();
      entry.source_republish_delay_ms = 0U;
    } else {
      action.kind = (entry.policy.mode == SyncAutomationMode::publish ||
                     entry.policy.mode == SyncAutomationMode::writable)
                        ? SyncAutomationActionKind::publish
                        : SyncAutomationActionKind::pull;
    }
    if (entry.policy.mode == SyncAutomationMode::bidirectional &&
        action.kind == SyncAutomationActionKind::pull) {
      const std::size_t count = entry.policy.source_principals.size();
      std::optional<std::size_t> selected;
      std::uint64_t earliest = std::numeric_limits<std::uint64_t>::max();
      for (std::size_t offset = 0U; offset < count; ++offset) {
        const std::size_t index = (entry.next_source_index + offset) % count;
        earliest = std::min(earliest, entry.peer_runtime[index].next_ms);
        if (!selected && entry.peer_runtime[index].next_ms <= now_ms)
          selected = index;
      }
      if (!selected) {
        entry.runtime.next_periodic_ms = earliest;
        if (entry.next_source_publish_ms) {
          entry.runtime.next_periodic_ms =
              std::min(entry.runtime.next_periodic_ms,
                       *entry.next_source_publish_ms);
        }
        continue;
      }
      action.source_principal = entry.policy.source_principals[*selected];
      entry.next_source_index = (*selected + 1U) % count;
    } else if (action.kind == SyncAutomationActionKind::pull) {
      action.source_principal = entry.policy.source_principals.front();
    }
    entry.runtime.periodic_busy = true;
    saturating_increment(entry.runtime.periodic_attempts);
    actions.push_back(std::move(action));
  }
  return actions;
}

Status SyncAutomationScheduler::trigger_source_change(
    std::string_view namespace_id, std::uint64_t now_ms,
    std::uint32_t debounce_ms, std::uint32_t busy_republish_delay_ms) {
  std::scoped_lock lock(mutex_);
  const auto found = std::find_if(
      entries_.begin(), entries_.end(), [namespace_id](const Entry &entry) {
        return entry.policy.namespace_id == namespace_id;
      });
  if (found == entries_.end()) {
    return Status{ErrorCode::not_found,
                  "sync automation policy is absent"};
  }
  if (found->policy.mode != SyncAutomationMode::publish &&
      found->policy.mode != SyncAutomationMode::writable &&
      found->policy.mode != SyncAutomationMode::bidirectional) {
    return Status{ErrorCode::unsupported,
                  "sync automation policy has no local source"};
  }
  if (found->policy.source_path.empty()) {
    return Status{ErrorCode::protocol_error,
                  "sync automation local source is absent"};
  }
  const std::uint64_t due_ms = saturating_add(now_ms, debounce_ms);
  if (!found->next_source_publish_ms ||
      due_ms < *found->next_source_publish_ms) {
    found->next_source_publish_ms = due_ms;
  }
  found->source_republish_delay_ms =
      std::max(found->source_republish_delay_ms, busy_republish_delay_ms);
  found->runtime.source_publish_pending = true;
  if (*found->next_source_publish_ms < found->runtime.next_periodic_ms)
    found->runtime.next_periodic_ms = *found->next_source_publish_ms;
  return Status::success();
}

Result<SyncAutomationAction> SyncAutomationScheduler::claim_activation(
    std::string_view namespace_id, std::uint64_t now_ms) {
  std::scoped_lock lock(mutex_);
  const auto found = std::find_if(
      entries_.begin(), entries_.end(),
      [namespace_id](const Entry &entry) {
        return entry.policy.namespace_id == namespace_id;
      });
  if (found == entries_.end()) {
    return Status{ErrorCode::not_found,
                  "sync automation policy is absent"};
  }
  if (found->policy.mode != SyncAutomationMode::follow ||
      found->policy.activation != SyncAutomationActivation::verified) {
    return Status{ErrorCode::unsupported,
                  "sync automation policy does not permit activation"};
  }
  if (found->runtime.activation_busy ||
      now_ms < found->runtime.next_activation_ms) {
    return Status{ErrorCode::unavailable,
                  "sync automation activation is not due"};
  }
  found->runtime.activation_busy = true;
  saturating_increment(found->runtime.activation_attempts);
  SyncAutomationAction action;
  action.kind = SyncAutomationActionKind::activate;
  action.policy = found->policy;
  action.source_principal = found->policy.source_principals.front();
  return action;
}

Status SyncAutomationScheduler::complete(const SyncAutomationAction &action,
                                         ErrorCode outcome,
                                         std::uint64_t now_ms) {
  std::scoped_lock lock(mutex_);
  const auto found = std::find_if(
      entries_.begin(), entries_.end(),
      [&action](const Entry &entry) {
        return entry.policy.namespace_id == action.policy.namespace_id;
      });
  if (found == entries_.end() ||
      found->policy.generation != action.policy.generation ||
      found->policy != action.policy) {
    return Status::success();
  }
  const bool activation =
      action.kind == SyncAutomationActionKind::activate;
  bool &busy = activation ? found->runtime.activation_busy
                          : found->runtime.periodic_busy;
  if (!busy) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation completion has no claimed action"};
  }
  if (!activation && action.kind == SyncAutomationActionKind::pull &&
      found->policy.mode == SyncAutomationMode::bidirectional &&
      !std::binary_search(found->policy.source_principals.begin(),
                          found->policy.source_principals.end(),
                          action.source_principal)) {
    return Status{ErrorCode::invalid_argument,
                  "sync automation action names an unknown source"};
  }
  busy = false;
  std::uint64_t &successes =
      activation ? found->runtime.activation_successes
                 : found->runtime.periodic_successes;
  std::uint64_t &failures =
      activation ? found->runtime.activation_failures
                 : found->runtime.periodic_failures;
  std::uint64_t &streak =
      activation ? found->runtime.consecutive_activation_failures
                 : found->runtime.consecutive_periodic_failures;
  ErrorCode &last = activation ? found->runtime.last_activation_error
                               : found->runtime.last_periodic_error;
  std::uint64_t &next = activation ? found->runtime.next_activation_ms
                                   : found->runtime.next_periodic_ms;
  if (!activation && found->policy.mode == SyncAutomationMode::bidirectional &&
      action.kind == SyncAutomationActionKind::pull) {
    const auto principal = std::lower_bound(
        found->policy.source_principals.begin(),
        found->policy.source_principals.end(), action.source_principal);
    const std::size_t index = static_cast<std::size_t>(
        std::distance(found->policy.source_principals.begin(), principal));
    PeerRuntime &peer = found->peer_runtime[index];
    if (outcome == ErrorCode::ok) {
      saturating_increment(successes);
      peer.consecutive_failures = 0U;
      peer.next_ms = saturating_add(now_ms, found->policy.interval_ms);
    } else {
      saturating_increment(failures);
      saturating_increment(peer.consecutive_failures);
      peer.next_ms = saturating_add(
          now_ms, retry_delay(found->policy, peer.consecutive_failures));
    }
    last = outcome;
    streak = 0U;
    next = std::numeric_limits<std::uint64_t>::max();
    for (const PeerRuntime &candidate : found->peer_runtime) {
      streak = std::max(streak, candidate.consecutive_failures);
      next = std::min(next, candidate.next_ms);
    }
    if (found->next_source_publish_ms)
      next = std::min(next, *found->next_source_publish_ms);
    found->runtime.source_publish_pending =
        found->next_source_publish_ms.has_value();
    return Status::success();
  }
  last = outcome;
  if (outcome == ErrorCode::ok) {
    saturating_increment(successes);
    streak = 0U;
    if (!activation && action.kind == SyncAutomationActionKind::publish &&
        (found->policy.mode == SyncAutomationMode::publish ||
         found->policy.mode == SyncAutomationMode::writable ||
         found->policy.mode == SyncAutomationMode::bidirectional)) {
      next = std::numeric_limits<std::uint64_t>::max();
      if (found->policy.mode == SyncAutomationMode::bidirectional) {
        for (const PeerRuntime &candidate : found->peer_runtime) {
          streak = std::max(streak, candidate.consecutive_failures);
          next = std::min(next, candidate.next_ms);
        }
      } else {
        next = saturating_add(now_ms, found->policy.interval_ms);
      }
      const bool delayed_republish =
          delayed_source_republish_pending(*found);
      if (found->next_source_publish_ms)
        apply_source_republish_delay(*found, now_ms);
      if (found->next_source_publish_ms) {
        if (delayed_republish &&
            (found->policy.mode == SyncAutomationMode::publish ||
             found->policy.mode == SyncAutomationMode::writable)) {
          next = *found->next_source_publish_ms;
        } else {
          next = std::min(next, *found->next_source_publish_ms);
        }
      }
      refresh_source_publish_pending(*found);
    } else {
      next = saturating_add(now_ms, found->policy.interval_ms);
      refresh_source_publish_pending(*found);
    }
    return Status::success();
  }
  saturating_increment(failures);
  saturating_increment(streak);
  const std::uint64_t retry_at =
      saturating_add(now_ms, retry_delay(found->policy, streak));
  if (!activation && action.kind == SyncAutomationActionKind::publish &&
      (found->policy.mode == SyncAutomationMode::publish ||
       found->policy.mode == SyncAutomationMode::writable ||
       found->policy.mode == SyncAutomationMode::bidirectional)) {
    apply_source_republish_delay(*found, now_ms);
    if (!found->next_source_publish_ms ||
        retry_at < *found->next_source_publish_ms)
      found->next_source_publish_ms = retry_at;
    next = found->policy.mode == SyncAutomationMode::bidirectional
               ? std::numeric_limits<std::uint64_t>::max()
               : retry_at;
    if (found->policy.mode == SyncAutomationMode::bidirectional) {
      for (const PeerRuntime &candidate : found->peer_runtime)
        next = std::min(next, candidate.next_ms);
    }
    next = std::min(next, *found->next_source_publish_ms);
    found->runtime.source_publish_pending = true;
  } else {
    next = retry_at;
    refresh_source_publish_pending(*found);
  }
  return Status::success();
}

std::vector<SyncAutomationRuntimeSnapshot>
SyncAutomationScheduler::snapshot() const {
  std::scoped_lock lock(mutex_);
  std::vector<SyncAutomationRuntimeSnapshot> result;
  result.reserve(entries_.size());
  for (const Entry &entry : entries_)
    result.push_back(entry.runtime);
  return result;
}

} // namespace iotox::sync
