#pragma once

#include "iotox/peer_alias.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"
#include "iotox/toxcore/abi.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::peer_invitation {

inline constexpr std::size_t kBodyBytes = 256U;
inline constexpr std::size_t kArtifactBytes =
    kBodyBytes + security::kSignatureBytes;
inline constexpr std::uint32_t kMinimumLifetimeSeconds = 60U;
inline constexpr std::uint32_t kMaximumLifetimeSeconds = 30U * 24U * 60U * 60U;
inline constexpr std::uint64_t kMaximumClockSkewMs = 5U * 60U * 1000U;

using ToxAddress =
    std::array<std::uint8_t, toxcore::abi::kAddressSize>;
using Nonce = std::array<std::uint8_t, 32U>;
using ArtifactBytes = std::array<std::uint8_t, kArtifactBytes>;

struct CreateRequest {
    std::uint32_t lifetime_seconds{0U};
    std::uint64_t requested_capabilities{0U};
    std::string suggested_alias;

    [[nodiscard]] bool operator==(const CreateRequest &) const = default;
};

struct Invitation {
    std::uint64_t issued_unix_ms{0U};
    std::uint64_t expires_unix_ms{0U};
    Nonce nonce{};
    security::SigningPublicKey inviter{};
    ToxAddress tox_address{};
    std::uint64_t requested_capabilities{0U};
    std::string suggested_alias;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const Invitation &) const = default;
};

struct Inspection {
    Invitation invitation;
    security::Digest artifact_id{};
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_create_request(
    const CreateRequest &request);
[[nodiscard]] Result<CreateRequest> decode_create_request(
    std::span<const std::uint8_t> bytes);

// Creates one self-contained shareable artifact signed by the stable device
// identity. The address remains a Tox transport address; the signature does
// not collapse transport friendship into IoTox authority.
[[nodiscard]] Result<ArtifactBytes> create(
    const CreateRequest &request, const ToxAddress &address,
    std::uint64_t now_unix_ms, const security::DeviceIdentity &identity,
    const security::Sodium &sodium);

// Strictly validates shape, canonical padding, domain-separated signature,
// and the closed capability vocabulary. Self-signature proves integrity and
// possession only; callers still pin the expected inviter out of band.
[[nodiscard]] Result<Inspection> inspect(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);

[[nodiscard]] Status validate_for_acceptance(
    const Inspection &inspection,
    const security::SigningPublicKey &expected_inviter,
    std::uint64_t now_unix_ms);

[[nodiscard]] peer_alias::PublicKey transport_public_key(
    const Invitation &invitation) noexcept;
[[nodiscard]] std::string render_inspection(
    const Inspection &inspection,
    const security::SigningPublicKey *expected_inviter = nullptr);

}  // namespace iotox::peer_invitation
