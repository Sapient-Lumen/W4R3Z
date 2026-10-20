#include "iotox/security/authority.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "test_harness.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <string>
#include <system_error>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        const auto ticks = std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
                ("iotox-authority-test-" + std::to_string(::getpid()) + "-" +
                 std::to_string(ticks));
        std::filesystem::create_directories(path_);
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &path() const noexcept { return path_; }

  private:
    std::filesystem::path path_;
};

std::array<std::uint8_t, iotox::security::kSigningSeedBytes> seed_from_hex(
    std::string_view value) {
    auto decoded = iotox::security::decode_hex_exact(
        value, iotox::security::kSigningSeedBytes, "test seed");
    IOTOX_CHECK(decoded.ok());
    std::array<std::uint8_t, iotox::security::kSigningSeedBytes> output{};
    std::copy(decoded.value().begin(), decoded.value().end(), output.begin());
    return output;
}

std::array<std::uint8_t, iotox::security::kSigningPublicKeyBytes> public_from_hex(
    std::string_view value) {
    auto decoded = iotox::security::decode_hex_exact(
        value, iotox::security::kSigningPublicKeyBytes, "test public key");
    IOTOX_CHECK(decoded.ok());
    std::array<std::uint8_t, iotox::security::kSigningPublicKeyBytes> output{};
    std::copy(decoded.value().begin(), decoded.value().end(), output.begin());
    return output;
}

std::array<std::uint8_t, iotox::security::kSignatureBytes> signature_from_hex(
    std::string_view value) {
    auto decoded = iotox::security::decode_hex_exact(
        value, iotox::security::kSignatureBytes, "test signature");
    IOTOX_CHECK(decoded.ok());
    std::array<std::uint8_t, iotox::security::kSignatureBytes> output{};
    std::copy(decoded.value().begin(), decoded.value().end(), output.begin());
    return output;
}

std::vector<std::uint8_t> read_file_bytes(
    const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    IOTOX_CHECK(input.good());
    return std::vector<std::uint8_t>{
        std::istreambuf_iterator<char>{input},
        std::istreambuf_iterator<char>{}};
}

void write_private_file(
    const std::filesystem::path &path,
    std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    IOTOX_CHECK(output.good());
    output.write(
        reinterpret_cast<const char *>(bytes.data()),
        static_cast<std::streamsize>(bytes.size()));
    output.close();
    IOTOX_CHECK(output.good());
    std::filesystem::permissions(
        path,
        std::filesystem::perms::owner_read |
            std::filesystem::perms::owner_write,
        std::filesystem::perm_options::replace);
}

}  // namespace

IOTOX_TEST("libsodium Ed25519 adapter matches RFC 8032 test vector 1") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());

    auto seed = seed_from_hex(
        "9D61B19DEFFD5A60BA844AF492EC2CC44449C5697B326919703BAC031CAE7F60");
    auto keys = sodium.value().signing_keypair_from_seed(seed);
    IOTOX_CHECK_MSG(keys.ok(), keys.status().message());
    IOTOX_CHECK(keys.value().public_key() == public_from_hex(
        "D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A"));

    const std::array<std::uint8_t, 0U> empty{};
    auto signature = sodium.value().sign_detached(empty, keys.value().secret_key());
    IOTOX_CHECK_MSG(signature.ok(), signature.status().message());
    IOTOX_CHECK(signature.value() == signature_from_hex(
        "E5564300C360AC729086E2CC806E828A"
        "84877F1EB8E5D974D873E06522490155"
        "5FB8821590A33BACC61E39701CF9B46BD"
        "25BF5F0595BBE24655141438E7A100B"));
    IOTOX_CHECK(sodium.value().verify_detached(
        signature.value(), empty, keys.value().public_key()).ok());

    signature.value()[0U] ^= 0x01U;
    IOTOX_CHECK(!sodium.value().verify_detached(
        signature.value(), empty, keys.value().public_key()).ok());
    iotox::security::secure_wipe(seed);
}

IOTOX_TEST("device identity is private stable and detects seed-public mismatch") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    const auto path = temporary.path() / "device.identity";

    auto first = iotox::security::DeviceIdentity::load_or_create(
        path, sodium.value(), true);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    const auto public_key = first.value().public_key();
    auto second = iotox::security::DeviceIdentity::load(path, sodium.value());
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().public_key() == public_key);
    IOTOX_CHECK(std::filesystem::file_size(path) == iotox::security::kDeviceIdentityFileBytes);
    IOTOX_CHECK((std::filesystem::status(path).permissions() &
                 (std::filesystem::perms::group_all | std::filesystem::perms::others_all)) ==
                std::filesystem::perms::none);

    std::fstream file(path, std::ios::binary | std::ios::in | std::ios::out);
    IOTOX_CHECK(file.good());
    file.seekp(48);
    const char changed = static_cast<char>(public_key[0U] ^ 0x80U);
    file.write(&changed, 1);
    file.close();
    auto corrupted = iotox::security::DeviceIdentity::load(path, sodium.value());
    IOTOX_CHECK(!corrupted.ok());
    IOTOX_CHECK(corrupted.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("signed authority ledger bootstraps grants revokes and replays") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;

    auto device_seed = seed_from_hex(
        "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F");
    auto owner_seed = seed_from_hex(
        "202122232425262728292A2B2C2D2E2F303132333435363738393A3B3C3D3E3F");
    auto operator_seed = seed_from_hex(
        "404142434445464748494A4B4C4D4E4F505152535455565758595A5B5C5D5E5F");
    auto device_keys = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner_keys = sodium.value().signing_keypair_from_seed(owner_seed);
    auto operator_keys = sodium.value().signing_keypair_from_seed(operator_seed);
    IOTOX_CHECK(device_keys.ok() && owner_keys.ok() && operator_keys.ok());

    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device_keys.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());
    IOTOX_CHECK(!ledger.value()->snapshot().initialized);

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAllCapabilities;
    bootstrap.issuer = owner_keys.value().public_key();
    bootstrap.subject = owner_keys.value().public_key();
    auto bootstrap_body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK_MSG(bootstrap_body.ok(), bootstrap_body.status().message());
    auto bootstrap_record = sign_authority_record_body(
        bootstrap_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(bootstrap_record.ok(), bootstrap_record.status().message());
    const iotox::Status bootstrap_appended =
        ledger.value()->append(bootstrap_record.value());
    IOTOX_CHECK_MSG(bootstrap_appended.ok(), bootstrap_appended.message());

    AuthorityPrepareRequest grant;
    grant.action = AuthorityAction::grant;
    grant.role = PrincipalRole::operator_role;
    grant.capabilities = static_cast<std::uint64_t>(Capability::read_telemetry) |
                         static_cast<std::uint64_t>(Capability::actuate);
    grant.issuer = owner_keys.value().public_key();
    grant.subject = operator_keys.value().public_key();
    auto grant_body = ledger.value()->prepare(grant);
    IOTOX_CHECK_MSG(grant_body.ok(), grant_body.status().message());
    auto grant_record = sign_authority_record_body(
        grant_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(grant_record.ok(), grant_record.status().message());
    const iotox::Status grant_appended =
        ledger.value()->append(grant_record.value());
    IOTOX_CHECK_MSG(grant_appended.ok(), grant_appended.message());
    IOTOX_CHECK(ledger.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::actuate)));
    IOTOX_CHECK(!ledger.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::install_firmware)));

    AuthorityRecordBytes tampered = grant_record.value();
    tampered[120U] ^= 0x01U;
    IOTOX_CHECK(!ledger.value()->append(tampered).ok());
    IOTOX_CHECK(ledger.value()->snapshot().record_count == 2U);

    AuthorityPrepareRequest revoke;
    revoke.action = AuthorityAction::revoke;
    revoke.role = PrincipalRole::none;
    revoke.capabilities = 0U;
    revoke.issuer = owner_keys.value().public_key();
    revoke.subject = operator_keys.value().public_key();
    auto revoke_body = ledger.value()->prepare(revoke);
    IOTOX_CHECK_MSG(revoke_body.ok(), revoke_body.status().message());
    auto revoke_record = sign_authority_record_body(
        revoke_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(revoke_record.ok(), revoke_record.status().message());
    const iotox::Status appended = ledger.value()->append(revoke_record.value());
    IOTOX_CHECK_MSG(appended.ok(), appended.message());
    IOTOX_CHECK(!ledger.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::read_telemetry)));

    auto reloaded = AuthorityLedger::open(
        config, device_keys.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(reloaded.ok(), reloaded.status().message());
    const AuthoritySnapshot snapshot = reloaded.value()->snapshot();
    IOTOX_CHECK(snapshot.initialized);
    IOTOX_CHECK(snapshot.sequence == 3U);
    IOTOX_CHECK(snapshot.record_count == 3U);
    IOTOX_CHECK(snapshot.ownership_epoch == 1U);
    IOTOX_CHECK(!reloaded.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::read_telemetry)));

    AuthorityPrepareRequest revoke_owner = revoke;
    revoke_owner.subject = owner_keys.value().public_key();
    auto revoke_owner_body = reloaded.value()->prepare(revoke_owner);
    IOTOX_CHECK(!revoke_owner_body.ok());
    IOTOX_CHECK(revoke_owner_body.status().code() == iotox::ErrorCode::protocol_error);

    iotox::security::secure_wipe(device_seed);
    iotox::security::secure_wipe(owner_seed);
    iotox::security::secure_wipe(operator_seed);
}

IOTOX_TEST("authority policy blocks implicit owner demotion and requires explicit succession") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;

    auto device_seed = seed_from_hex(
        "606162636465666768696A6B6C6D6E6F707172737475767778797A7B7C7D7E7F");
    auto owner_seed = seed_from_hex(
        "808182838485868788898A8B8C8D8E8F909192939495969798999A9B9C9D9E9F");
    auto admin_seed = seed_from_hex(
        "A0A1A2A3A4A5A6A7A8A9AAABACADAEAFB0B1B2B3B4B5B6B7B8B9BABBBCBDBEBF");
    auto successor_seed = seed_from_hex(
        "C0C1C2C3C4C5C6C7C8C9CACBCCCDCECFD0D1D2D3D4D5D6D7D8D9DADBDCDDDEDF");
    auto device_keys = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner_keys = sodium.value().signing_keypair_from_seed(owner_seed);
    auto admin_keys = sodium.value().signing_keypair_from_seed(admin_seed);
    auto successor_keys = sodium.value().signing_keypair_from_seed(successor_seed);
    IOTOX_CHECK(device_keys.ok() && owner_keys.ok() && admin_keys.ok() &&
                successor_keys.ok());

    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device_keys.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAllCapabilities;
    bootstrap.issuer = owner_keys.value().public_key();
    bootstrap.subject = owner_keys.value().public_key();
    auto bootstrap_body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK_MSG(bootstrap_body.ok(), bootstrap_body.status().message());
    auto bootstrap_record = sign_authority_record_body(
        bootstrap_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(bootstrap_record.ok(), bootstrap_record.status().message());
    IOTOX_CHECK_MSG(
        ledger.value()->append(bootstrap_record.value()).ok(),
        "owner bootstrap must append");

    AuthorityPrepareRequest grant_admin;
    grant_admin.action = AuthorityAction::grant;
    grant_admin.role = PrincipalRole::administrator;
    grant_admin.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry) |
        static_cast<std::uint64_t>(Capability::write_settings) |
        static_cast<std::uint64_t>(Capability::manage_principals);
    grant_admin.issuer = owner_keys.value().public_key();
    grant_admin.subject = admin_keys.value().public_key();
    auto admin_body = ledger.value()->prepare(grant_admin);
    IOTOX_CHECK_MSG(admin_body.ok(), admin_body.status().message());
    auto admin_record = sign_authority_record_body(
        admin_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(admin_record.ok(), admin_record.status().message());
    IOTOX_CHECK_MSG(ledger.value()->append(admin_record.value()).ok(),
                    "administrator grant must append");

    AuthorityPrepareRequest implicit_demotion;
    implicit_demotion.action = AuthorityAction::grant;
    implicit_demotion.role = PrincipalRole::viewer;
    implicit_demotion.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    implicit_demotion.issuer = admin_keys.value().public_key();
    implicit_demotion.subject = owner_keys.value().public_key();
    auto rejected_prepare = ledger.value()->prepare(implicit_demotion);
    IOTOX_CHECK(!rejected_prepare.ok());
    IOTOX_CHECK(rejected_prepare.status().code() == iotox::ErrorCode::protocol_error);

    // Preparation is a convenience and race-reduction boundary, not the security
    // boundary. A caller may construct bytes directly, so append/replay must
    // independently reject the same owner-demotion attempt.
    AuthorityRecord forged_demotion;
    forged_demotion.action = AuthorityAction::grant;
    forged_demotion.role = PrincipalRole::viewer;
    forged_demotion.sequence = 3U;
    forged_demotion.ownership_epoch = 1U;
    forged_demotion.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    forged_demotion.device = device_keys.value().public_key();
    forged_demotion.issuer = admin_keys.value().public_key();
    forged_demotion.subject = owner_keys.value().public_key();
    forged_demotion.previous_digest = ledger.value()->snapshot().tail_digest;
    auto forged_body = encode_authority_record_body(forged_demotion);
    IOTOX_CHECK_MSG(forged_body.ok(), forged_body.status().message());
    auto forged_record = sign_authority_record_body(
        forged_body.value(), admin_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(forged_record.ok(), forged_record.status().message());
    const iotox::Status rejected_append = ledger.value()->append(forged_record.value());
    IOTOX_CHECK(!rejected_append.ok());
    IOTOX_CHECK(rejected_append.code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(ledger.value()->snapshot().sequence == 2U);

    AuthorityPrepareRequest revoke_missing;
    revoke_missing.action = AuthorityAction::revoke;
    revoke_missing.role = PrincipalRole::none;
    revoke_missing.capabilities = 0U;
    revoke_missing.issuer = owner_keys.value().public_key();
    revoke_missing.subject = successor_keys.value().public_key();
    IOTOX_CHECK(!ledger.value()->prepare(revoke_missing).ok());

    AuthorityPrepareRequest grant_successor;
    grant_successor.action = AuthorityAction::grant;
    grant_successor.role = PrincipalRole::owner;
    grant_successor.capabilities = kAllCapabilities;
    grant_successor.issuer = owner_keys.value().public_key();
    grant_successor.subject = successor_keys.value().public_key();
    auto successor_body = ledger.value()->prepare(grant_successor);
    IOTOX_CHECK_MSG(successor_body.ok(), successor_body.status().message());
    auto successor_record = sign_authority_record_body(
        successor_body.value(), owner_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(successor_record.ok(), successor_record.status().message());
    IOTOX_CHECK_MSG(ledger.value()->append(successor_record.value()).ok(),
                    "successor owner grant must append");

    AuthorityPrepareRequest revoke_original;
    revoke_original.action = AuthorityAction::revoke;
    revoke_original.role = PrincipalRole::none;
    revoke_original.capabilities = 0U;
    revoke_original.issuer = successor_keys.value().public_key();
    revoke_original.subject = owner_keys.value().public_key();
    auto revoke_body = ledger.value()->prepare(revoke_original);
    IOTOX_CHECK_MSG(revoke_body.ok(), revoke_body.status().message());
    auto revoke_record = sign_authority_record_body(
        revoke_body.value(), successor_keys.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(revoke_record.ok(), revoke_record.status().message());
    IOTOX_CHECK_MSG(ledger.value()->append(revoke_record.value()).ok(),
                    "explicit owner succession must append");
    IOTOX_CHECK(!ledger.value()->authorized(owner_keys.value().public_key(), 0U));
    IOTOX_CHECK(ledger.value()->authorized(successor_keys.value().public_key(),
                                           kAllCapabilities));

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(admin_seed);
    secure_wipe(successor_seed);
}

IOTOX_TEST("ownership epoch transition requires an adjacent successor nomination") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;

    auto device_seed = seed_from_hex(
        "0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F20");
    auto owner_seed = seed_from_hex(
        "2122232425262728292A2B2C2D2E2F303132333435363738393A3B3C3D3E3F40");
    auto delegate_seed = seed_from_hex(
        "4142434445464748494A4B4C4D4E4F505152535455565758595A5B5C5D5E5F60");
    auto successor_seed = seed_from_hex(
        "6162636465666768696A6B6C6D6E6F707172737475767778797A7B7C7D7E7F80");
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto delegate = sodium.value().signing_keypair_from_seed(delegate_seed);
    auto successor = sodium.value().signing_keypair_from_seed(successor_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && delegate.ok() && successor.ok());

    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    const auto append_request = [&](const AuthorityPrepareRequest &request,
                                    std::span<const std::uint8_t,
                                              kSigningSecretKeyBytes> secret) {
        auto body = ledger.value()->prepare(request);
        IOTOX_CHECK_MSG(body.ok(), body.status().message());
        auto record = sign_authority_record_body(body.value(), secret, sodium.value());
        IOTOX_CHECK_MSG(record.ok(), record.status().message());
        IOTOX_CHECK_MSG(ledger.value()->append(record.value()).ok(),
                        "prepared authority record must append");
        return record.value();
    };

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAllCapabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    (void)append_request(bootstrap, owner.value().secret_key());

    AuthorityPrepareRequest grant_delegate;
    grant_delegate.action = AuthorityAction::grant;
    grant_delegate.role = PrincipalRole::administrator;
    grant_delegate.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry) |
        static_cast<std::uint64_t>(Capability::manage_principals);
    grant_delegate.issuer = owner.value().public_key();
    grant_delegate.subject = delegate.value().public_key();
    (void)append_request(grant_delegate, owner.value().secret_key());

    AuthorityPrepareRequest transition;
    transition.action = AuthorityAction::epoch_transition;
    transition.role = PrincipalRole::owner;
    transition.capabilities = kAllCapabilities;
    transition.issuer = successor.value().public_key();
    transition.subject = successor.value().public_key();
    IOTOX_CHECK(!ledger.value()->prepare(transition).ok());

    AuthorityPrepareRequest nominate;
    nominate.action = AuthorityAction::grant;
    nominate.role = PrincipalRole::owner;
    nominate.capabilities = kAllCapabilities;
    nominate.issuer = owner.value().public_key();
    nominate.subject = successor.value().public_key();
    (void)append_request(nominate, owner.value().secret_key());
    IOTOX_CHECK(ledger.value()->snapshot().nominated_successor ==
                successor.value().public_key());

    // Any intervening mutation consumes the adjacency required by the
    // nomination, even when the successor remains an active owner.
    AuthorityPrepareRequest update_delegate = grant_delegate;
    update_delegate.role = PrincipalRole::viewer;
    update_delegate.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    (void)append_request(update_delegate, owner.value().secret_key());
    IOTOX_CHECK(!ledger.value()->prepare(transition).ok());

    AuthorityPrepareRequest revoke_successor;
    revoke_successor.action = AuthorityAction::revoke;
    revoke_successor.role = PrincipalRole::none;
    revoke_successor.capabilities = 0U;
    revoke_successor.issuer = owner.value().public_key();
    revoke_successor.subject = successor.value().public_key();
    (void)append_request(revoke_successor, owner.value().secret_key());
    (void)append_request(nominate, owner.value().secret_key());

    auto transition_body = ledger.value()->prepare(transition);
    IOTOX_CHECK_MSG(transition_body.ok(), transition_body.status().message());
    AuthorityRecordBody altered_body = transition_body.value();
    // Epoch is at body bytes 16..23; changing it invalidates the successor
    // signature/continuity pair even when re-signed correctly.
    altered_body[23U] = 3U;
    auto skipped_epoch = sign_authority_record_body(
        altered_body, successor.value().secret_key(), sodium.value());
    IOTOX_CHECK(skipped_epoch.ok());
    IOTOX_CHECK(!ledger.value()->append(skipped_epoch.value()).ok());

    auto transition_record = sign_authority_record_body(
        transition_body.value(), successor.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(transition_record.ok(), transition_record.status().message());
    IOTOX_CHECK_MSG(ledger.value()->append(transition_record.value()).ok(),
                    "nominated successor transition must append");

    const AuthoritySnapshot transitioned = ledger.value()->snapshot();
    IOTOX_CHECK(transitioned.ownership_epoch == 2U);
    IOTOX_CHECK(transitioned.sequence == 1U);
    IOTOX_CHECK(transitioned.record_count == 7U);
    IOTOX_CHECK(transitioned.principals.size() == 1U);
    IOTOX_CHECK(transitioned.principals.front().public_key ==
                successor.value().public_key());
    IOTOX_CHECK(transitioned.principals.front().role == PrincipalRole::owner);
    IOTOX_CHECK(transitioned.principals.front().active);
    IOTOX_CHECK(!ledger.value()->authorized(owner.value().public_key(), 0U));
    IOTOX_CHECK(!ledger.value()->authorized(delegate.value().public_key(), 0U));
    IOTOX_CHECK(ledger.value()->authorized(
        successor.value().public_key(), kAllCapabilities));

    ledger.value().reset();
    auto reopened = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().ownership_epoch == 2U);
    IOTOX_CHECK(reopened.value()->snapshot().sequence == 1U);
    IOTOX_CHECK(reopened.value()->snapshot().record_count == 7U);
    IOTOX_CHECK(reopened.value()->snapshot().principals.size() == 1U);
    IOTOX_CHECK(reopened.value()->authorized(
        successor.value().public_key(), kAllCapabilities));
    IOTOX_CHECK(!reopened.value()->prepare(grant_delegate).ok());

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(delegate_seed);
    secure_wipe(successor_seed);
}

IOTOX_TEST("authority ledger v2 migration is explicit non-widening and durable") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;

    auto device_seed = seed_from_hex(
        "1112131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F30");
    auto owner_seed = seed_from_hex(
        "3132333435363738393A3B3C3D3E3F404142434445464748494A4B4C4D4E4F50");
    auto operator_seed = seed_from_hex(
        "5152535455565758595A5B5C5D5E5F606162636465666768696A6B6C6D6E6F70");
    auto successor_seed = seed_from_hex(
        "7172737475767778797A7B7C7D7E7F808182838485868788898A8B8C8D8E8F90");
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto operator_keys = sodium.value().signing_keypair_from_seed(operator_seed);
    auto successor = sodium.value().signing_keypair_from_seed(successor_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && operator_keys.ok() && successor.ok());

    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    const auto append_request = [&](const AuthorityPrepareRequest &request,
                                    std::span<const std::uint8_t,
                                              kSigningSecretKeyBytes> secret) {
        auto body = ledger.value()->prepare(request);
        IOTOX_CHECK_MSG(body.ok(), body.status().message());
        auto record = sign_authority_record_body(
            body.value(), secret, sodium.value());
        IOTOX_CHECK_MSG(record.ok(), record.status().message());
        IOTOX_CHECK_MSG(ledger.value()->append(record.value()).ok(),
                        "prepared authority record must append");
        return record.value();
    };

    const auto terminal =
        static_cast<std::uint64_t>(Capability::interactive_terminal);
    const auto read = static_cast<std::uint64_t>(Capability::read_telemetry);
    const auto actuate = static_cast<std::uint64_t>(Capability::actuate);

    auto legacy_all = parse_capability_set("all");
    auto explicit_v1 = parse_capability_set("all-v1");
    auto explicit_v2 = parse_capability_set("all-v2");
    auto terminal_only = parse_capability_set("interactive.terminal");
    IOTOX_CHECK(legacy_all.ok() && explicit_v1.ok() && explicit_v2.ok() &&
                terminal_only.ok());
    IOTOX_CHECK(legacy_all.value() == kAuthorityV1Capabilities);
    IOTOX_CHECK(explicit_v1.value() == kAuthorityV1Capabilities);
    IOTOX_CHECK(explicit_v2.value() == kAuthorityV2Capabilities);
    IOTOX_CHECK(terminal_only.value() == terminal);
    IOTOX_CHECK(kAllCapabilities == kAuthorityV1Capabilities);
    IOTOX_CHECK((role_capability_ceiling(PrincipalRole::operator_role) &
                 terminal) == 0U);
    IOTOX_CHECK((role_capability_ceiling(
                     PrincipalRole::operator_role,
                     AuthorityLedgerFormat::v2) & terminal) != 0U);

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAuthorityV1Capabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    (void)append_request(bootstrap, owner.value().secret_key());

    AuthorityPrepareRequest grant_operator;
    grant_operator.action = AuthorityAction::grant;
    grant_operator.role = PrincipalRole::operator_role;
    grant_operator.capabilities = read | actuate;
    grant_operator.issuer = owner.value().public_key();
    grant_operator.subject = operator_keys.value().public_key();
    (void)append_request(grant_operator, owner.value().secret_key());

    const std::vector<std::uint8_t> v1_bytes = read_file_bytes(config.path);
    const std::filesystem::path guard_path =
        default_authority_rollback_guard_path(config.path);
    const std::vector<std::uint8_t> v1_guard_bytes =
        read_file_bytes(guard_path);
    IOTOX_CHECK(v1_bytes.size() ==
                kAuthorityLedgerHeaderBytes + 2U * kAuthorityRecordBytes);
    IOTOX_CHECK(v1_guard_bytes.size() == kAuthorityRollbackGuardBytes);
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(v1_guard_bytes.data()), 8U) ==
                "IOTOXAG2");
    IOTOX_CHECK(v1_guard_bytes[8U] == 2U && v1_guard_bytes[9U] == 0U);
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(v1_bytes.data()), 8U) ==
                "IOTOXAL1");
    IOTOX_CHECK(v1_bytes[8U] == 1U && v1_bytes[9U] == 1U);
    IOTOX_CHECK(ledger.value()->snapshot().format == AuthorityLedgerFormat::v1);
    IOTOX_CHECK(!ledger.value()->authorized(
        owner.value().public_key(), terminal));
    IOTOX_CHECK(!ledger.value()->authorized(
        operator_keys.value().public_key(), terminal));

    AuthorityPrepareRequest premature_terminal = grant_operator;
    premature_terminal.capabilities |= terminal;
    auto premature = ledger.value()->prepare(premature_terminal);
    IOTOX_CHECK(!premature.ok());
    IOTOX_CHECK(premature.status().code() == iotox::ErrorCode::invalid_argument);

    AuthorityPrepareRequest migrate;
    migrate.action = AuthorityAction::migrate_v2;
    migrate.role = PrincipalRole::owner;
    migrate.capabilities = kAuthorityV1Capabilities;
    migrate.issuer = owner.value().public_key();
    migrate.subject = owner.value().public_key();
    auto migration_body = ledger.value()->prepare(migrate);
    IOTOX_CHECK_MSG(migration_body.ok(), migration_body.status().message());
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(migration_body.value().data()),
                    4U) == "IAL2");
    IOTOX_CHECK(migration_body.value()[4U] == 2U);
    IOTOX_CHECK(migration_body.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityAction::migrate_v2));
    auto migration_record = sign_authority_record_body(
        migration_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(migration_record.ok(), migration_record.status().message());
    IOTOX_CHECK_MSG(ledger.value()->append(migration_record.value()).ok(),
                    "signed v2 migration must append");

    const AuthoritySnapshot migrated = ledger.value()->snapshot();
    IOTOX_CHECK(migrated.format == AuthorityLedgerFormat::v2);
    IOTOX_CHECK(migrated.ownership_epoch == 1U);
    IOTOX_CHECK(migrated.sequence == 3U);
    IOTOX_CHECK(migrated.record_count == 3U);
    auto migrated_owner = ledger.value()->principal(owner.value().public_key());
    auto migrated_operator = ledger.value()->principal(
        operator_keys.value().public_key());
    IOTOX_CHECK(migrated_owner.ok() && migrated_operator.ok());
    IOTOX_CHECK(migrated_owner.value().capabilities ==
                kAuthorityV1Capabilities);
    IOTOX_CHECK(migrated_operator.value().capabilities == (read | actuate));
    IOTOX_CHECK(!ledger.value()->authorized(
        owner.value().public_key(), terminal));
    IOTOX_CHECK(!ledger.value()->authorized(
        operator_keys.value().public_key(), terminal));

    const std::vector<std::uint8_t> migrated_bytes = read_file_bytes(config.path);
    IOTOX_CHECK(migrated_bytes.size() ==
                kAuthorityLedgerHeaderBytes + 3U * kAuthorityRecordBytes);
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(migrated_bytes.data()), 8U) ==
                "IOTOXAL2");
    IOTOX_CHECK(migrated_bytes[8U] == 2U && migrated_bytes[9U] == 0U);
    const std::size_t record0 = kAuthorityLedgerHeaderBytes;
    const std::size_t record1 = record0 + kAuthorityRecordBytes;
    const std::size_t record2 = record1 + kAuthorityRecordBytes;
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(migrated_bytes.data() + record0),
                    4U) == "IAL1");
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(migrated_bytes.data() + record1),
                    4U) == "IAL1");
    IOTOX_CHECK(std::string(
                    reinterpret_cast<const char *>(migrated_bytes.data() + record2),
                    4U) == "IAL2");
    const std::vector<std::uint8_t> migrated_guard_bytes =
        read_file_bytes(guard_path);
    IOTOX_CHECK(migrated_guard_bytes.size() ==
                kAuthorityRollbackGuardBytes);
    IOTOX_CHECK(migrated_guard_bytes[9U] == 0U);

    IOTOX_CHECK(!ledger.value()->prepare(migrate).ok());
    AuthorityPrepareRequest unknown = grant_operator;
    unknown.capabilities = 1ULL << 8U;
    IOTOX_CHECK(!ledger.value()->prepare(unknown).ok());

    AuthorityPrepareRequest activate_owner;
    activate_owner.action = AuthorityAction::grant;
    activate_owner.role = PrincipalRole::owner;
    activate_owner.capabilities = kAuthorityV2Capabilities;
    activate_owner.issuer = owner.value().public_key();
    activate_owner.subject = owner.value().public_key();

    // Recreate the exact on-disk state left when the v2 ledger replace lands
    // but final guard promotion does not: the committed head is still the v1
    // tail and the pending head is the current migrated v2 tail. A live next
    // append must promote that exact pending head and continue without a
    // restart. Any third head remains a hard failure.
    std::vector<std::uint8_t> interrupted_guard = v1_guard_bytes;
    interrupted_guard[9U] = 1U;
    std::copy_n(
        migrated_guard_bytes.begin() + 48U, 64U,
        interrupted_guard.begin() + 112U);
    write_private_file(guard_path, interrupted_guard);
    (void)append_request(activate_owner, owner.value().secret_key());
    IOTOX_CHECK(ledger.value()->authorized(
        owner.value().public_key(), terminal));

    AuthorityPrepareRequest grant_terminal = grant_operator;
    grant_terminal.capabilities = read | actuate | terminal;
    (void)append_request(grant_terminal, owner.value().secret_key());
    IOTOX_CHECK(ledger.value()->authorized(
        operator_keys.value().public_key(), terminal));

    const AuthoritySnapshot v2_head = ledger.value()->snapshot();
    AuthorityRecord stale_v1;
    stale_v1.format = AuthorityLedgerFormat::v1;
    stale_v1.action = AuthorityAction::grant;
    stale_v1.role = PrincipalRole::viewer;
    stale_v1.sequence = v2_head.sequence + 1U;
    stale_v1.ownership_epoch = v2_head.ownership_epoch;
    stale_v1.capabilities = read;
    stale_v1.device = v2_head.device;
    stale_v1.issuer = owner.value().public_key();
    stale_v1.subject = successor.value().public_key();
    stale_v1.previous_digest = v2_head.tail_digest;
    auto stale_v1_body = encode_authority_record_body(stale_v1);
    IOTOX_CHECK(stale_v1_body.ok());
    auto stale_v1_record = sign_authority_record_body(
        stale_v1_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(stale_v1_record.ok());
    IOTOX_CHECK(!ledger.value()->append(stale_v1_record.value()).ok());
    IOTOX_CHECK(ledger.value()->snapshot().sequence == v2_head.sequence);

    const std::vector<std::uint8_t> current_v2_bytes =
        read_file_bytes(config.path);
    const std::vector<std::uint8_t> current_guard_bytes =
        read_file_bytes(guard_path);

    AuthorityLedger::Config rollback_config;
    rollback_config.path = temporary.path() / "rollback.ledger";
    write_private_file(rollback_config.path, v1_bytes);
    write_private_file(
        default_authority_rollback_guard_path(rollback_config.path),
        current_guard_bytes);
    auto rolled_back = AuthorityLedger::open(
        rollback_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!rolled_back.ok());
    IOTOX_CHECK(rolled_back.status().code() ==
                iotox::ErrorCode::protocol_error);

    AuthorityLedger::Config deleted_config;
    deleted_config.path = temporary.path() / "deleted.ledger";
    write_private_file(
        default_authority_rollback_guard_path(deleted_config.path),
        current_guard_bytes);
    auto deleted = AuthorityLedger::open(
        deleted_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!deleted.ok());
    IOTOX_CHECK(deleted.status().code() == iotox::ErrorCode::protocol_error);

    AuthorityLedger::Config missing_guard_config;
    missing_guard_config.path = temporary.path() / "missing-guard-v2.ledger";
    write_private_file(missing_guard_config.path, current_v2_bytes);
    auto missing_guard = AuthorityLedger::open(
        missing_guard_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!missing_guard.ok());
    IOTOX_CHECK(missing_guard.status().code() ==
                iotox::ErrorCode::protocol_error);

    AuthorityLedger::Config legacy_adoption_config;
    legacy_adoption_config.path = temporary.path() / "legacy-adoption.ledger";
    write_private_file(legacy_adoption_config.path, v1_bytes);
    auto legacy_adopted = AuthorityLedger::open(
        legacy_adoption_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(legacy_adopted.ok(),
                    legacy_adopted.status().message());
    IOTOX_CHECK(std::filesystem::exists(
        default_authority_rollback_guard_path(legacy_adoption_config.path)));

    ledger.value().reset();
    auto reopened = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().format == AuthorityLedgerFormat::v2);
    IOTOX_CHECK(reopened.value()->authorized(
        owner.value().public_key(), terminal));
    IOTOX_CHECK(reopened.value()->authorized(
        operator_keys.value().public_key(), terminal));
    ledger = std::move(reopened);

    std::vector<std::uint8_t> false_v2 = v1_bytes;
    std::copy_n("IOTOXAL2", 8U, false_v2.begin());
    false_v2[8U] = 2U;
    false_v2[9U] = 0U;
    AuthorityLedger::Config false_v2_config;
    false_v2_config.path = temporary.path() / "false-v2.ledger";
    write_private_file(false_v2_config.path, false_v2);
    auto false_v2_open = AuthorityLedger::open(
        false_v2_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!false_v2_open.ok());
    IOTOX_CHECK(false_v2_open.status().code() ==
                iotox::ErrorCode::protocol_error);

    std::vector<std::uint8_t> downgraded = read_file_bytes(config.path);
    std::copy_n("IOTOXAL1", 8U, downgraded.begin());
    downgraded[8U] = 1U;
    downgraded[9U] = 1U;
    AuthorityLedger::Config downgraded_config;
    downgraded_config.path = temporary.path() / "downgraded.ledger";
    write_private_file(downgraded_config.path, downgraded);
    auto downgraded_open = AuthorityLedger::open(
        downgraded_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!downgraded_open.ok());
    IOTOX_CHECK(downgraded_open.status().code() ==
                iotox::ErrorCode::protocol_error);

    AuthorityPrepareRequest nominate;
    nominate.action = AuthorityAction::grant;
    nominate.role = PrincipalRole::owner;
    nominate.capabilities = kAuthorityV1Capabilities;
    nominate.issuer = owner.value().public_key();
    nominate.subject = successor.value().public_key();
    (void)append_request(nominate, owner.value().secret_key());

    AuthorityPrepareRequest transition;
    transition.action = AuthorityAction::epoch_transition;
    transition.role = PrincipalRole::owner;
    transition.capabilities = kAuthorityV1Capabilities;
    transition.issuer = successor.value().public_key();
    transition.subject = successor.value().public_key();
    (void)append_request(transition, successor.value().secret_key());

    const AuthoritySnapshot transitioned = ledger.value()->snapshot();
    IOTOX_CHECK(transitioned.format == AuthorityLedgerFormat::v2);
    IOTOX_CHECK(transitioned.ownership_epoch == 2U);
    IOTOX_CHECK(transitioned.sequence == 1U);
    IOTOX_CHECK(transitioned.principals.size() == 1U);
    IOTOX_CHECK(transitioned.principals.front().public_key ==
                successor.value().public_key());
    IOTOX_CHECK(transitioned.principals.front().capabilities ==
                kAuthorityV1Capabilities);
    IOTOX_CHECK(!ledger.value()->authorized(
        successor.value().public_key(), terminal));

    ledger.value().reset();
    auto transitioned_reopen = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(transitioned_reopen.ok(),
                    transitioned_reopen.status().message());
    IOTOX_CHECK(transitioned_reopen.value()->snapshot().format ==
                AuthorityLedgerFormat::v2);
    IOTOX_CHECK(transitioned_reopen.value()->snapshot().ownership_epoch == 2U);
    IOTOX_CHECK(!transitioned_reopen.value()->authorized(
        successor.value().public_key(), terminal));

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(operator_seed);
    secure_wipe(successor_seed);
}
IOTOX_TEST("authority ledger v3 migration preserves grants before explicit "
           "sync activation") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;

    auto device_seed = seed_from_hex(
        "12131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F3031");
    auto owner_seed = seed_from_hex(
        "32333435363738393A3B3C3D3E3F404142434445464748494A4B4C4D4E4F5051");
    auto viewer_seed = seed_from_hex(
        "52535455565758595A5B5C5D5E5F606162636465666768696A6B6C6D6E6F7071");
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto viewer = sodium.value().signing_keypair_from_seed(viewer_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && viewer.ok());

    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority-v3.ledger";
    auto ledger = AuthorityLedger::open(config, device.value().public_key(),
                                        sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    const auto append_request =
        [&](const AuthorityPrepareRequest &request,
            std::span<const std::uint8_t, kSigningSecretKeyBytes> secret) {
            auto body = ledger.value()->prepare(request);
            IOTOX_CHECK_MSG(body.ok(), body.status().message());
            auto record = sign_authority_record_body(body.value(), secret,
                                                     sodium.value());
            IOTOX_CHECK_MSG(record.ok(), record.status().message());
            IOTOX_CHECK_MSG(ledger.value()->append(record.value()).ok(),
                            "prepared v3 authority record must append");
            return record.value();
        };

    const auto read = static_cast<std::uint64_t>(Capability::read_telemetry);
    const auto terminal =
        static_cast<std::uint64_t>(Capability::interactive_terminal);
    const auto sync_admin = static_cast<std::uint64_t>(Capability::sync_admin);
    const auto sync_publish =
        static_cast<std::uint64_t>(Capability::sync_publish);
    const auto sync_subscribe =
        static_cast<std::uint64_t>(Capability::sync_subscribe);
    const auto sync_activate =
        static_cast<std::uint64_t>(Capability::sync_activate);
    const std::uint64_t sync_all =
        sync_admin | sync_publish | sync_subscribe | sync_activate;

    auto explicit_v3 = parse_capability_set("all-v3");
    auto named_sync = parse_capability_set(
        "sync.admin,sync.publish,sync.subscribe,sync.activate");
    IOTOX_CHECK(explicit_v3.ok() && named_sync.ok());
    IOTOX_CHECK(explicit_v3.value() == kAuthorityV3Capabilities);
    IOTOX_CHECK(named_sync.value() == sync_all);
    IOTOX_CHECK(parse_capability_set("all").value() ==
                kAuthorityV1Capabilities);
    IOTOX_CHECK(parse_capability_set("all-v2").value() ==
                kAuthorityV2Capabilities);
    IOTOX_CHECK(render_capability_set(sync_all) ==
                "sync.admin,sync.publish,sync.subscribe,sync.activate");
    IOTOX_CHECK(authority_capability_mask(AuthorityLedgerFormat::v2) ==
                kAuthorityV2Capabilities);
    IOTOX_CHECK(authority_capability_mask(AuthorityLedgerFormat::v3) ==
                kAuthorityV3Capabilities);
    IOTOX_CHECK((role_capability_ceiling(PrincipalRole::viewer,
                                         AuthorityLedgerFormat::v3) &
                 sync_subscribe) != 0U);
    IOTOX_CHECK((role_capability_ceiling(PrincipalRole::viewer,
                                         AuthorityLedgerFormat::v3) &
                 sync_activate) == 0U);
    IOTOX_CHECK((role_capability_ceiling(PrincipalRole::administrator,
                                         AuthorityLedgerFormat::v3) &
                 sync_admin) != 0U);

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAuthorityV1Capabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    (void)append_request(bootstrap, owner.value().secret_key());

    AuthorityPrepareRequest migrate_v2;
    migrate_v2.action = AuthorityAction::migrate_v2;
    migrate_v2.role = PrincipalRole::owner;
    migrate_v2.capabilities = kAuthorityV1Capabilities;
    migrate_v2.issuer = owner.value().public_key();
    migrate_v2.subject = owner.value().public_key();
    (void)append_request(migrate_v2, owner.value().secret_key());

    AuthorityPrepareRequest activate_terminal;
    activate_terminal.action = AuthorityAction::grant;
    activate_terminal.role = PrincipalRole::owner;
    activate_terminal.capabilities = kAuthorityV2Capabilities;
    activate_terminal.issuer = owner.value().public_key();
    activate_terminal.subject = owner.value().public_key();
    (void)append_request(activate_terminal, owner.value().secret_key());

    AuthorityPrepareRequest premature_sync;
    premature_sync.action = AuthorityAction::grant;
    premature_sync.role = PrincipalRole::viewer;
    premature_sync.capabilities = read | sync_subscribe;
    premature_sync.issuer = owner.value().public_key();
    premature_sync.subject = viewer.value().public_key();
    IOTOX_CHECK(!ledger.value()->prepare(premature_sync).ok());

    AuthorityPrepareRequest widened_migration;
    widened_migration.action = AuthorityAction::migrate_v3;
    widened_migration.role = PrincipalRole::owner;
    widened_migration.capabilities = kAuthorityV3Capabilities;
    widened_migration.issuer = owner.value().public_key();
    widened_migration.subject = owner.value().public_key();
    IOTOX_CHECK(!ledger.value()->prepare(widened_migration).ok());

    AuthorityPrepareRequest migrate_v3 = widened_migration;
    migrate_v3.capabilities = kAuthorityV2Capabilities;
    auto migration_body = ledger.value()->prepare(migrate_v3);
    IOTOX_CHECK_MSG(migration_body.ok(), migration_body.status().message());
    IOTOX_CHECK(std::string(reinterpret_cast<const char *>(
                                migration_body.value().data()),
                            4U) == "IAL3");
    IOTOX_CHECK(migration_body.value()[4U] == 3U);
    IOTOX_CHECK(migration_body.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityAction::migrate_v3));
    auto migration_record = sign_authority_record_body(
        migration_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(migration_record.ok());
    IOTOX_CHECK_MSG(ledger.value()->append(migration_record.value()).ok(),
                    "signed v3 migration must append");

    const AuthoritySnapshot migrated = ledger.value()->snapshot();
    IOTOX_CHECK(migrated.format == AuthorityLedgerFormat::v3);
    IOTOX_CHECK(migrated.sequence == 4U);
    IOTOX_CHECK(migrated.record_count == 4U);
    auto migrated_owner = ledger.value()->principal(owner.value().public_key());
    IOTOX_CHECK(migrated_owner.ok());
    IOTOX_CHECK(migrated_owner.value().capabilities ==
                kAuthorityV2Capabilities);
    IOTOX_CHECK(
        ledger.value()->authorized(owner.value().public_key(), terminal));
    IOTOX_CHECK(
        !ledger.value()->authorized(owner.value().public_key(), sync_all));
    IOTOX_CHECK(!ledger.value()->prepare(premature_sync).ok());
    IOTOX_CHECK(!ledger.value()->prepare(migrate_v3).ok());

    const std::vector<std::uint8_t> migrated_bytes =
        read_file_bytes(config.path);
    IOTOX_CHECK(
        std::string(reinterpret_cast<const char *>(migrated_bytes.data()),
                    8U) == "IOTOXAL3");
    IOTOX_CHECK(migrated_bytes[8U] == 3U && migrated_bytes[9U] == 0U);
    const std::size_t last_record =
        kAuthorityLedgerHeaderBytes + 3U * kAuthorityRecordBytes;
    IOTOX_CHECK(std::string(reinterpret_cast<const char *>(
                                migrated_bytes.data() + last_record),
                            4U) == "IAL3");

    AuthorityPrepareRequest activate_sync = activate_terminal;
    activate_sync.capabilities = kAuthorityV3Capabilities;
    AuthorityPrepareRequest mixed_remove_and_widen = activate_sync;
    mixed_remove_and_widen.capabilities &= ~terminal;
    IOTOX_CHECK(!ledger.value()->prepare(mixed_remove_and_widen).ok());
    (void)append_request(activate_sync, owner.value().secret_key());
    IOTOX_CHECK(
        ledger.value()->authorized(owner.value().public_key(), sync_all));

    AuthorityPrepareRequest invalid_viewer = premature_sync;
    invalid_viewer.capabilities = read | sync_activate;
    IOTOX_CHECK(!ledger.value()->prepare(invalid_viewer).ok());
    (void)append_request(premature_sync, owner.value().secret_key());
    IOTOX_CHECK(ledger.value()->authorized(viewer.value().public_key(),
                                           sync_subscribe));
    IOTOX_CHECK(!ledger.value()->authorized(viewer.value().public_key(),
                                            sync_activate));

    AuthorityPrepareRequest unknown = premature_sync;
    unknown.capabilities = 1ULL << 12U;
    IOTOX_CHECK(!encode_authority_prepare_request(unknown).ok());
    IOTOX_CHECK(!ledger.value()->prepare(unknown).ok());

    const std::vector<std::uint8_t> v3_bytes = read_file_bytes(config.path);
    const std::vector<std::uint8_t> v3_guard =
        read_file_bytes(default_authority_rollback_guard_path(config.path));
    ledger.value().reset();
    auto reopened = AuthorityLedger::open(config, device.value().public_key(),
                                          sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().format ==
                AuthorityLedgerFormat::v3);
    IOTOX_CHECK(reopened.value()->authorized(viewer.value().public_key(),
                                             sync_subscribe));

    AuthorityLedger::Config missing_guard_config;
    missing_guard_config.path = temporary.path() / "missing-v3-guard.ledger";
    write_private_file(missing_guard_config.path, v3_bytes);
    auto missing_guard = AuthorityLedger::open(
        missing_guard_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!missing_guard.ok());
    IOTOX_CHECK(missing_guard.status().code() ==
                iotox::ErrorCode::protocol_error);

    std::vector<std::uint8_t> false_v3 = v3_bytes;
    std::copy_n("IOTOXAL2", 8U, false_v3.begin());
    false_v3[8U] = 2U;
    AuthorityLedger::Config false_v3_config;
    false_v3_config.path = temporary.path() / "false-v3.ledger";
    write_private_file(false_v3_config.path, false_v3);
    write_private_file(
        default_authority_rollback_guard_path(false_v3_config.path), v3_guard);
    auto false_v3_open = AuthorityLedger::open(
        false_v3_config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!false_v3_open.ok());
    IOTOX_CHECK(false_v3_open.status().code() ==
                iotox::ErrorCode::protocol_error);

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(viewer_seed);
}
