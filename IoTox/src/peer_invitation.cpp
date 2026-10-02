#include "iotox/peer_invitation.hpp"

#include "iotox/security/random.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <sstream>

namespace iotox::peer_invitation {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic{
    'I', 'O', 'T', 'X', 'I', 'N', 'V', '1'};
constexpr std::uint8_t kFormatVersion = 1U;
constexpr std::string_view kSignatureDomain = "peer-invitation-v1";
constexpr std::string_view kArtifactDomain = "peer-invitation-record-v1";
constexpr std::size_t kIssuedOffset = 16U;
constexpr std::size_t kExpiryOffset = 24U;
constexpr std::size_t kNonceOffset = 32U;
constexpr std::size_t kInviterOffset = 64U;
constexpr std::size_t kAddressOffset = 96U;
constexpr std::size_t kCapabilitiesOffset = 134U;
constexpr std::size_t kAliasOffset = 142U;

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[offset + index] = static_cast<std::uint8_t>(
            value >> static_cast<unsigned>((7U - index) * 8U));
    }
}

std::uint32_t read_u32(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>(
            (value << 8U) | input[offset + index]);
    }
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | input[offset + index];
    }
    return value;
}

bool nonzero(std::span<const std::uint8_t> bytes) noexcept {
    return std::any_of(bytes.begin(), bytes.end(), [](std::uint8_t byte) {
        return byte != 0U;
    });
}

Status validate_request(const CreateRequest &request) {
    if (request.lifetime_seconds < kMinimumLifetimeSeconds ||
        request.lifetime_seconds > kMaximumLifetimeSeconds) {
        return Status{
            ErrorCode::invalid_argument,
            "peer invitation lifetime must be 60..2592000 seconds"};
    }
    if ((request.requested_capabilities &
         ~security::kAuthorityV3Capabilities) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation requests an unknown capability bit"};
    }
    if (!request.suggested_alias.empty()) {
        const Status alias = peer_alias::validate_name(
            request.suggested_alias);
        if (!alias.ok()) return alias;
    }
    return Status::success();
}

Result<std::array<std::uint8_t, kBodyBytes>> encode_body(
    const Invitation &invitation) {
    if (invitation.issued_unix_ms == 0U ||
        invitation.expires_unix_ms <= invitation.issued_unix_ms ||
        invitation.expires_unix_ms - invitation.issued_unix_ms <
            static_cast<std::uint64_t>(kMinimumLifetimeSeconds) * 1000U ||
        invitation.expires_unix_ms - invitation.issued_unix_ms >
            static_cast<std::uint64_t>(kMaximumLifetimeSeconds) * 1000U ||
        !nonzero(invitation.nonce) || !nonzero(invitation.inviter) ||
        !nonzero(std::span<const std::uint8_t>{
            invitation.tox_address}.first(toxcore::abi::kPublicKeySize)) ||
        (invitation.requested_capabilities &
         ~security::kAuthorityV3Capabilities) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation fields are outside the frozen contract"};
    }
    if (!invitation.suggested_alias.empty()) {
        const Status alias = peer_alias::validate_name(
            invitation.suggested_alias);
        if (!alias.ok()) return alias;
    }
    std::array<std::uint8_t, kBodyBytes> output{};
    std::copy(kMagic.begin(), kMagic.end(), output.begin());
    output[8U] = kFormatVersion;
    output[9U] = static_cast<std::uint8_t>(
        invitation.suggested_alias.size());
    write_u64(output, kIssuedOffset, invitation.issued_unix_ms);
    write_u64(output, kExpiryOffset, invitation.expires_unix_ms);
    std::copy(invitation.nonce.begin(), invitation.nonce.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kNonceOffset));
    std::copy(invitation.inviter.begin(), invitation.inviter.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kInviterOffset));
    std::copy(invitation.tox_address.begin(), invitation.tox_address.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kAddressOffset));
    write_u64(output, kCapabilitiesOffset,
              invitation.requested_capabilities);
    std::copy(invitation.suggested_alias.begin(),
              invitation.suggested_alias.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kAliasOffset));
    return output;
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_create_request(
    const CreateRequest &request) {
    const Status valid = validate_request(request);
    if (!valid.ok()) return valid;
    std::vector<std::uint8_t> output;
    output.reserve(13U + request.suggested_alias.size());
    for (int shift = 24; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            request.lifetime_seconds >> static_cast<unsigned>(shift)));
    }
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            request.requested_capabilities >>
            static_cast<unsigned>(shift)));
    }
    output.push_back(static_cast<std::uint8_t>(
        request.suggested_alias.size()));
    output.insert(output.end(), request.suggested_alias.begin(),
                  request.suggested_alias.end());
    return output;
}

Result<CreateRequest> decode_create_request(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() < 13U ||
        bytes.size() != 13U + static_cast<std::size_t>(bytes[12U])) {
        return Status{ErrorCode::protocol_error,
                      "peer invitation create request is noncanonical"};
    }
    CreateRequest request;
    request.lifetime_seconds = read_u32(bytes, 0U);
    request.requested_capabilities = read_u64(bytes, 4U);
    request.suggested_alias.assign(
        reinterpret_cast<const char *>(bytes.data() + 13U), bytes[12U]);
    const Status valid = validate_request(request);
    if (!valid.ok()) {
        return Status{ErrorCode::protocol_error, valid.message()};
    }
    return request;
}

Result<ArtifactBytes> create(
    const CreateRequest &request, const ToxAddress &address,
    std::uint64_t now_unix_ms, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    const Status valid = validate_request(request);
    if (!valid.ok()) return valid;
    const std::uint64_t lifetime_ms =
        static_cast<std::uint64_t>(request.lifetime_seconds) * 1000U;
    if (now_unix_ms == 0U ||
        now_unix_ms > std::numeric_limits<std::uint64_t>::max() - lifetime_ms) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation creation time is invalid"};
    }
    Invitation invitation;
    invitation.issued_unix_ms = now_unix_ms;
    invitation.expires_unix_ms = now_unix_ms + lifetime_ms;
    invitation.inviter = identity.public_key();
    invitation.tox_address = address;
    invitation.requested_capabilities = request.requested_capabilities;
    invitation.suggested_alias = request.suggested_alias;
    const Status random = security::fill_random(invitation.nonce);
    if (!random.ok()) return random;
    auto body = encode_body(invitation);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    ArtifactBytes output{};
    std::copy(body.value().begin(), body.value().end(), output.begin());
    std::copy(signature.value().begin(), signature.value().end(),
              output.begin() + static_cast<std::ptrdiff_t>(kBodyBytes));
    return output;
}

Result<Inspection> inspect(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    if (bytes.size() != kArtifactBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[8U] != kFormatVersion ||
        bytes[9U] > peer_alias::kMaximumNameBytes ||
        !std::all_of(bytes.begin() + 10, bytes.begin() + 16,
                     [](std::uint8_t byte) { return byte == 0U; }) ||
        !std::all_of(
            bytes.begin() + static_cast<std::ptrdiff_t>(
                kAliasOffset + bytes[9U]),
            bytes.begin() + static_cast<std::ptrdiff_t>(kBodyBytes),
            [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::protocol_error,
                      "peer invitation shape, version, or padding is invalid"};
    }
    Invitation invitation;
    invitation.issued_unix_ms = read_u64(bytes, kIssuedOffset);
    invitation.expires_unix_ms = read_u64(bytes, kExpiryOffset);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kNonceOffset),
                invitation.nonce.size(), invitation.nonce.begin());
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kInviterOffset),
                invitation.inviter.size(), invitation.inviter.begin());
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kAddressOffset),
                invitation.tox_address.size(), invitation.tox_address.begin());
    invitation.requested_capabilities = read_u64(
        bytes, kCapabilitiesOffset);
    invitation.suggested_alias.assign(
        reinterpret_cast<const char *>(bytes.data() + kAliasOffset),
        bytes[9U]);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kBodyBytes),
                invitation.signature.size(), invitation.signature.begin());
    auto canonical = encode_body(invitation);
    if (!canonical || !std::equal(
            canonical.value().begin(), canonical.value().end(),
            bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "peer invitation fields are not canonical"};
    }
    auto signature_digest = sodium.hash(
        kSignatureDomain, bytes.first(kBodyBytes));
    if (!signature_digest) return signature_digest.status();
    const Status verified = sodium.verify_detached(
        invitation.signature, signature_digest.value(), invitation.inviter);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "peer invitation signature is invalid"};
    }
    auto artifact_id = sodium.hash(kArtifactDomain, bytes);
    if (!artifact_id) return artifact_id.status();
    return Inspection{std::move(invitation), artifact_id.value()};
}

Status validate_for_acceptance(
    const Inspection &inspection,
    const security::SigningPublicKey &expected_inviter,
    std::uint64_t now_unix_ms) {
    if (!security::constant_time_equal(
            inspection.invitation.inviter, expected_inviter)) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation inviter does not match the pinned expected identity"};
    }
    if (now_unix_ms == 0U ||
        (inspection.invitation.issued_unix_ms > now_unix_ms &&
         inspection.invitation.issued_unix_ms - now_unix_ms >
             kMaximumClockSkewMs)) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation is not yet valid on this clock"};
    }
    if (now_unix_ms >= inspection.invitation.expires_unix_ms) {
        return Status{ErrorCode::invalid_argument,
                      "peer invitation has expired"};
    }
    return Status::success();
}

peer_alias::PublicKey transport_public_key(
    const Invitation &invitation) noexcept {
    peer_alias::PublicKey key{};
    std::copy_n(invitation.tox_address.begin(), key.size(), key.begin());
    return key;
}

std::string render_inspection(
    const Inspection &inspection,
    const security::SigningPublicKey *expected_inviter) {
    const Invitation &invitation = inspection.invitation;
    std::ostringstream output;
    output << "iotox-peer-invitation-v1\n"
           << "artifact-id=" << security::hex(inspection.artifact_id) << '\n'
           << "inviter-stable-principal="
           << security::hex(invitation.inviter) << '\n'
           << "tox-address=" << security::hex(invitation.tox_address) << '\n'
           << "transport-public-key="
           << security::hex(transport_public_key(invitation)) << '\n'
           << "issued-unix-ms=" << invitation.issued_unix_ms << '\n'
           << "expires-unix-ms=" << invitation.expires_unix_ms << '\n'
           << "nonce=" << security::hex(invitation.nonce) << '\n'
           << "suggested-alias="
           << (invitation.suggested_alias.empty()
                   ? std::string{"-"}
                   : invitation.suggested_alias)
           << '\n'
           << "requested-capabilities="
           << (invitation.requested_capabilities == 0U
                   ? std::string{"-"}
                   : security::render_capability_set(
                         invitation.requested_capabilities))
           << '\n'
           << "signature-valid=1\n";
    if (expected_inviter == nullptr) {
        output << "inviter-trust=unestablished\n";
    } else {
        output << "expected-inviter-match="
               << (security::constant_time_equal(
                       invitation.inviter, *expected_inviter)
                       ? 1
                       : 0)
               << '\n';
    }
    output << "friendship-granted=0\nauthority-granted=0\n";
    return output.str();
}

}  // namespace iotox::peer_invitation
