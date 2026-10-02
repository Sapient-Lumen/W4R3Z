#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::update {

inline constexpr std::size_t kUpdateManifestBodyBytes = 256U;
inline constexpr std::size_t kSignedUpdateManifestBytes =
    kUpdateManifestBodyBytes + security::kSignatureBytes;
inline constexpr std::size_t kMaximumUpdateSigners = 8U;
inline constexpr std::size_t kMaximumRevokedUpdateSigners = 32U;
inline constexpr std::size_t kMaximumUpdatePolicyBytes = 4096U;

using UpdateManifestBody =
    std::array<std::uint8_t, kUpdateManifestBodyBytes>;
using SignedUpdateManifestBytes =
    std::array<std::uint8_t, kSignedUpdateManifestBytes>;

enum class PayloadKind : std::uint8_t {
  opaque_slot_v1 = 1U,
  // One native Linux ELF service image consumed only by the separately
  // enabled linux-service-v1 deployment adapter. Staging remains inert.
  linux_service_v1 = 2U,
};

struct UpdatePolicy {
  std::string namespace_id;
  std::string target;
  std::filesystem::path root;
  std::uint64_t maximum_payload_bytes{64U * 1024U * 1024U};
  std::uint64_t health_timeout_ms{60U * 1000U};
  std::uint64_t signer_policy_epoch{0U};
  PayloadKind payload_kind{PayloadKind::opaque_slot_v1};
  std::vector<security::SigningPublicKey> trusted_signers;
  std::vector<security::SigningPublicKey> revoked_signers;

  [[nodiscard]] bool operator==(const UpdatePolicy &) const = default;
};

struct SignedUpdateManifest {
  PayloadKind payload_kind{PayloadKind::opaque_slot_v1};
  std::uint64_t release_sequence{0U};
  std::uint64_t payload_bytes{0U};
  sync::Digest payload_digest{};
  security::SigningPublicKey signer{};
  std::string namespace_id;
  std::string target;
  std::string version;
  security::Signature signature{};

  [[nodiscard]] bool operator==(const SignedUpdateManifest &) const = default;
};

struct UpdateBundleInfo {
  SignedUpdateManifest manifest;
  sync::Digest manifest_record{};
  std::filesystem::path path;

  [[nodiscard]] bool operator==(const UpdateBundleInfo &) const = default;
};

[[nodiscard]] std::string_view payload_kind_name(PayloadKind kind) noexcept;
[[nodiscard]] Status validate_update_policy(const UpdatePolicy &policy);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_update_policy(
    const UpdatePolicy &policy);
[[nodiscard]] Result<UpdatePolicy> decode_update_policy(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<UpdatePolicy> load_update_policy(
    const std::filesystem::path &path, std::uint32_t expected_owner_uid);
[[nodiscard]] Result<UpdateManifestBody> encode_update_manifest_body(
    const SignedUpdateManifest &manifest);
[[nodiscard]] Result<SignedUpdateManifestBytes> encode_signed_update_manifest(
    const SignedUpdateManifest &manifest);
[[nodiscard]] Result<SignedUpdateManifest> decode_signed_update_manifest(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_signed_update_manifest(
    const UpdatePolicy &policy, const SignedUpdateManifest &manifest,
    const security::Sodium &sodium);
[[nodiscard]] Result<sync::Digest> update_manifest_record_digest(
    const SignedUpdateManifest &manifest, const security::Sodium &sodium);

// Creates one no-clobber canonical bundle. PAYLOAD and OUTPUT must be absolute
// paths in owner-controlled directories. The payload is read from one stable
// descriptor, hashed before and during copy, and the complete output is
// independently inspected before success is returned. SIGNER must carry the
// explicit release identity role; a device-role identity is refused even when
// its public key appears in policy.
[[nodiscard]] Result<UpdateBundleInfo> create_signed_update_bundle(
    const UpdatePolicy &policy, const std::filesystem::path &payload,
    const std::filesystem::path &output, std::uint64_t release_sequence,
    std::string version, const security::DeviceIdentity &signer,
    const security::Sodium &sodium);

// Verifies exact file shape, policy binding, signature, payload size/digest,
// and a stable descriptor snapshot. It never executes, extracts, mounts, or
// interprets payload bytes.
[[nodiscard]] Result<UpdateBundleInfo> inspect_signed_update_bundle(
    const UpdatePolicy &policy, const std::filesystem::path &bundle,
    const security::Sodium &sodium);

} // namespace iotox::update
