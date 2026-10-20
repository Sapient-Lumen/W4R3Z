#include "test_harness.hpp"

#include "iotox/peer_invitation.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"

#include <filesystem>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-peer-invitation-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data()); created != nullptr) {
            root_ = created;
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

iotox::peer_invitation::ToxAddress test_address() {
    iotox::peer_invitation::ToxAddress address{};
    for (std::size_t index = 0U; index < address.size(); ++index) {
        address[index] = static_cast<std::uint8_t>(index + 1U);
    }
    return address;
}

}  // namespace

IOTOX_TEST("peer invitation create request codec freezes bounds and vocabulary") {
    iotox::peer_invitation::CreateRequest request;
    request.lifetime_seconds = 3600U;
    request.requested_capabilities =
        static_cast<std::uint64_t>(
            iotox::security::Capability::read_telemetry) |
        static_cast<std::uint64_t>(
            iotox::security::Capability::interactive_terminal);
    request.suggested_alias = "workstation";
    auto encoded = iotox::peer_invitation::encode_create_request(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded = iotox::peer_invitation::decode_create_request(
        encoded.value());
    IOTOX_CHECK(decoded.ok() && decoded.value() == request);
    encoded.value().push_back(0U);
    IOTOX_CHECK(!iotox::peer_invitation::decode_create_request(
                     encoded.value()).ok());

    request.lifetime_seconds = 59U;
    IOTOX_CHECK(!iotox::peer_invitation::encode_create_request(request).ok());
    request.lifetime_seconds =
        iotox::peer_invitation::kMaximumLifetimeSeconds + 1U;
    IOTOX_CHECK(!iotox::peer_invitation::encode_create_request(request).ok());
    request.lifetime_seconds = 60U;
    request.requested_capabilities = 1ULL << 63U;
    IOTOX_CHECK(!iotox::peer_invitation::encode_create_request(request).ok());
    request.requested_capabilities = 0U;
    request.suggested_alias = "Not-Canonical";
    IOTOX_CHECK(!iotox::peer_invitation::encode_create_request(request).ok());
}

IOTOX_TEST("peer invitation binds signer address expiry nonce and requested capabilities") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    auto foreign = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "foreign.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok() && foreign.ok());

    iotox::peer_invitation::CreateRequest request;
    request.lifetime_seconds = 60U;
    request.requested_capabilities =
        static_cast<std::uint64_t>(
            iotox::security::Capability::sync_subscribe);
    request.suggested_alias = "publisher";
    const auto address = test_address();
    constexpr std::uint64_t now = 1'000'000U;
    auto artifact = iotox::peer_invitation::create(
        request, address, now, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(artifact.ok(), artifact.status().message());
    auto inspected = iotox::peer_invitation::inspect(
        artifact.value(), sodium.value());
    IOTOX_CHECK_MSG(inspected.ok(), inspected.status().message());
    IOTOX_CHECK(inspected.value().invitation.issued_unix_ms == now);
    IOTOX_CHECK(inspected.value().invitation.expires_unix_ms ==
                now + 60'000U);
    IOTOX_CHECK(inspected.value().invitation.inviter ==
                identity.value().public_key());
    IOTOX_CHECK(inspected.value().invitation.tox_address == address);
    IOTOX_CHECK(inspected.value().invitation.suggested_alias == "publisher");
    IOTOX_CHECK(inspected.value().invitation.requested_capabilities ==
                request.requested_capabilities);
    IOTOX_CHECK(iotox::peer_invitation::transport_public_key(
                    inspected.value().invitation).front() == 1U);
    IOTOX_CHECK(iotox::peer_invitation::validate_for_acceptance(
                    inspected.value(), identity.value().public_key(),
                    now + 1U).ok());
    IOTOX_CHECK(!iotox::peer_invitation::validate_for_acceptance(
                     inspected.value(), foreign.value().public_key(),
                     now + 1U).ok());
    IOTOX_CHECK(!iotox::peer_invitation::validate_for_acceptance(
                     inspected.value(), identity.value().public_key(),
                     now + 60'000U).ok());
    IOTOX_CHECK(!iotox::peer_invitation::validate_for_acceptance(
                     inspected.value(), identity.value().public_key(),
                     now - iotox::peer_invitation::kMaximumClockSkewMs - 1U)
                     .ok());
    const std::string rendered = iotox::peer_invitation::render_inspection(
        inspected.value(), &identity.value().public_key());
    IOTOX_CHECK(rendered.find("signature-valid=1\n") != std::string::npos &&
                rendered.find("expected-inviter-match=1\n") !=
                    std::string::npos &&
                rendered.find("authority-granted=0\n") !=
                    std::string::npos);

    auto tampered = artifact.value();
    tampered[142U] ^= 0x01U;
    IOTOX_CHECK(!iotox::peer_invitation::inspect(
                     tampered, sodium.value()).ok());
    tampered = artifact.value();
    tampered.back() ^= 0x01U;
    IOTOX_CHECK(!iotox::peer_invitation::inspect(
                     tampered, sodium.value()).ok());
}
