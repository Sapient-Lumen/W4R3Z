#include "iotox/agent.hpp"
#include "iotox/cli.hpp"
#include "iotox/interactive_incarnation.hpp"
#include "iotox/local/control_protocol.hpp"
#include "iotox/local/control_socket.hpp"
#include "iotox/local/terminal_protocol.hpp"
#include "iotox/local/terminal_socket.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/ratox.hpp"
#include "iotox/route_inventory.hpp"
#include "iotox/route_worker.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_activation.hpp"
#include "iotox/sync_content.hpp"
#include "iotox/sync_content_publication.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_manifest.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/update_bundle.hpp"
#include "iotox/update_state.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <optional>
#include <span>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

std::filesystem::path agent_test_directory() {
    static std::atomic<unsigned int> sequence{0U};
    const char *override_root = std::getenv("IOTOX_TEST_SHORT_TMPDIR");
    const std::filesystem::path root =
        (override_root != nullptr && override_root[0] != '\0') ?
            std::filesystem::path(override_root) :
            std::filesystem::path("/tmp");
    return root /
           ("iotox-agent-test-" + std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)));
}

std::filesystem::path self_test_executable() {
    std::vector<char> buffer(4096U);
    const ssize_t count =
        ::readlink("/proc/self/exe", buffer.data(), buffer.size() - 1U);
    IOTOX_CHECK(count > 0);
    return std::string(buffer.data(), static_cast<std::size_t>(count));
}

std::filesystem::path update_service_fixture() {
    return IOTOX_UPDATE_SERVICE_FIXTURE_PATH;
}

int bind_active_terminal_socket(const std::filesystem::path &path) {
    const std::string text = path.string();
    IOTOX_CHECK(text.size() < sizeof(sockaddr_un::sun_path));
    const int descriptor =
        ::socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
    IOTOX_CHECK(descriptor >= 0);
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, text.c_str(), text.size() + 1U);
    IOTOX_CHECK(::bind(
                    descriptor,
                    reinterpret_cast<const sockaddr *>(&address),
                    sizeof(address)) == 0);
    IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0600)) == 0);
    IOTOX_CHECK(::listen(descriptor, 4) == 0);
    return descriptor;
}

std::string read_text(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    std::ostringstream output;
    output << input.rdbuf();
    return output.str();
}

std::size_t count_occurrences(std::string_view text, std::string_view needle) {
    std::size_t count = 0U;
    std::size_t offset = 0U;
    while (true) {
        offset = text.find(needle, offset);
        if (offset == std::string_view::npos) {
            return count;
        }
        ++count;
        offset += needle.size();
    }
}

void write_fifo_record(
    const std::filesystem::path &path, std::string_view record) {
    IOTOX_CHECK(!record.empty());
    IOTOX_CHECK(record.back() == '\n');
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    int descriptor = -1;
    while (std::chrono::steady_clock::now() < deadline) {
        descriptor = ::open(
            path.c_str(), O_WRONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor >= 0) {
            break;
        }
        IOTOX_CHECK(errno == ENXIO || errno == ENOENT || errno == EINTR);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(
        descriptor >= 0,
        "ratox-style FIFO did not acquire its daemon reader before the deadline");

    ssize_t written = -1;
    do {
        written = ::write(descriptor, record.data(), record.size());
    } while (written < 0 && errno == EINTR);
    const int close_result = ::close(descriptor);
    IOTOX_CHECK(written == static_cast<ssize_t>(record.size()));
    IOTOX_CHECK(close_result == 0);
}

iotox::local::ControlPacket request(
    iotox::local::ControlOperation operation,
    std::uint64_t id,
    std::vector<std::uint8_t> payload = {}) {
    iotox::local::ControlPacket packet;
    packet.operation = operation;
    packet.request_id = id;
    packet.payload = std::move(payload);
    return packet;
}

std::uint32_t read_u32(const std::vector<std::uint8_t> &bytes) {
    IOTOX_CHECK(bytes.size() == 4U);
    std::uint32_t value = 0U;
    for (const std::uint8_t byte : bytes) {
        value = static_cast<std::uint32_t>((value << 8U) | byte);
    }
    return value;
}

void append_u32(std::vector<std::uint8_t> &bytes, std::uint32_t value) {
    bytes.push_back(static_cast<std::uint8_t>((value >> 24U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>((value >> 16U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_u16(std::vector<std::uint8_t> &bytes, std::uint16_t value) {
    bytes.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_u64(std::vector<std::uint8_t> &bytes, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        bytes.push_back(static_cast<std::uint8_t>(
            (value >> static_cast<unsigned int>(shift)) & 0xFFU));
    }
}

std::uint64_t read_u64_at(
    const std::vector<std::uint8_t> &bytes, std::size_t offset) {
    IOTOX_CHECK(bytes.size() >= offset + 8U);
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

std::uint16_t read_u16_at(
    const std::vector<std::uint8_t> &bytes, std::size_t offset) {
    IOTOX_CHECK(bytes.size() >= offset + 2U);
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        static_cast<std::uint16_t>(bytes[offset + 1U]));
}


std::string line_with_prefix(
    std::string_view text, std::string_view prefix) {
    const std::size_t start = text.find(prefix);
    if (start == std::string_view::npos) {
        return {};
    }
    const std::size_t end = text.find('\n', start);
    return std::string(text.substr(
        start, end == std::string_view::npos ? text.size() - start : end - start));
}

void make_private_directory(const std::filesystem::path &path) {
    IOTOX_CHECK(std::filesystem::create_directory(path));
    IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0700)) == 0);
}

void write_private_record(
    const std::filesystem::path &path,
    const std::vector<std::uint8_t> &bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    IOTOX_CHECK(output.good());
    output.write(
        reinterpret_cast<const char *>(bytes.data()),
        static_cast<std::streamsize>(bytes.size()));
    output.close();
    IOTOX_CHECK(output.good());
    IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0600)) == 0);
}

iotox::terminal::PrincipalId mock_authority_principal() {
    return iotox::terminal::PrincipalId{
        0xD7U, 0x5AU, 0x98U, 0x01U, 0x82U, 0xB1U, 0x0AU, 0xB7U,
        0xD5U, 0x4BU, 0xFEU, 0xD3U, 0xC9U, 0x64U, 0x07U, 0x3AU,
        0x0EU, 0xE1U, 0x72U, 0xF3U, 0xDAU, 0xA6U, 0x23U, 0x25U,
        0xAFU, 0x02U, 0x1AU, 0x68U, 0xF7U, 0x07U, 0x51U, 0x1AU};
}

iotox::security::DeviceIdentity mock_sync_publisher_identity(
    const std::filesystem::path &path,
    const iotox::security::Sodium &sodium) {
    constexpr iotox::security::SigningSeed seed{
        0x9DU, 0x61U, 0xB1U, 0x9DU, 0xEFU, 0xFDU, 0x5AU, 0x60U,
        0xBAU, 0x84U, 0x4AU, 0xF4U, 0x92U, 0xECU, 0x2CU, 0xC4U,
        0x44U, 0x49U, 0xC5U, 0x69U, 0x7BU, 0x32U, 0x69U, 0x19U,
        0x70U, 0x3BU, 0xACU, 0x03U, 0x1CU, 0xAEU, 0x7FU, 0x60U};
    std::array<std::uint8_t,
               iotox::security::kDeviceIdentityFileBytes> bytes{};
    constexpr std::array<std::uint8_t, 8U> magic{
        'I', 'O', 'T', 'O', 'X', 'I', 'D', '1'};
    std::copy(magic.begin(), magic.end(), bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = 1U;
    std::copy(seed.begin(), seed.end(), bytes.begin() + 16U);
    const auto public_key = mock_authority_principal();
    std::copy(public_key.begin(), public_key.end(), bytes.begin() + 48U);
    write_private_record(
        path, std::vector<std::uint8_t>(bytes.begin(), bytes.end()));
    auto identity = iotox::security::DeviceIdentity::load(path, sodium);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    return std::move(identity).value();
}

iotox::terminal::PrincipalId default_profile_principal() {
    iotox::terminal::PrincipalId principal{};
    principal.fill(0x33U);
    return principal;
}

iotox::security::SigningSeed mock_terminal_owner_seed() {
    return iotox::security::SigningSeed{
        0x10U, 0x21U, 0x32U, 0x43U, 0x54U, 0x65U, 0x76U, 0x87U,
        0x98U, 0xA9U, 0xBAU, 0xCBU, 0xDCU, 0xEDU, 0xFEU, 0x0FU,
        0x1EU, 0x2DU, 0x3CU, 0x4BU, 0x5AU, 0x69U, 0x78U, 0x87U,
        0x96U, 0xA5U, 0xB4U, 0xC3U, 0xD2U, 0xE1U, 0xF0U, 0x0AU};
}

void append_authority_request(
    iotox::security::AuthorityLedger &ledger,
    const iotox::security::AuthorityPrepareRequest &request,
    std::span<const std::uint8_t, iotox::security::kSigningSecretKeyBytes> secret_key,
    const iotox::security::Sodium &sodium) {
    auto body = ledger.prepare(request);
    IOTOX_CHECK_MSG(body.ok(), body.status().message());
    auto record = iotox::security::sign_authority_record_body(
        body.value(), secret_key, sodium);
    IOTOX_CHECK_MSG(record.ok(), record.status().message());
    const iotox::Status appended = ledger.append(record.value());
    IOTOX_CHECK_MSG(appended.ok(), appended.message());
}

std::string lowercase_principal_hex(
    const iotox::terminal::PrincipalId &principal) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(principal.size() * 2U);
    for (const std::uint8_t byte : principal) {
        encoded.push_back(digits[byte >> 4U]);
        encoded.push_back(digits[byte & 0x0FU]);
    }
    return encoded;
}

struct RatoxProfileStoreFixture {
    std::filesystem::path root;
    iotox::terminal::PrincipalId principal{};

    explicit RatoxProfileStoreFixture(const std::filesystem::path &parent)
        : RatoxProfileStoreFixture(parent, default_profile_principal()) {}

    RatoxProfileStoreFixture(
        const std::filesystem::path &parent,
        iotox::terminal::PrincipalId bound_principal)
        : root(parent / "ratox-profiles"),
          principal(bound_principal) {
        make_private_directory(root);
        const std::filesystem::path profiles = root / "profiles";
        const std::filesystem::path bindings = root / "bindings";
        make_private_directory(profiles);
        make_private_directory(bindings);

        iotox::terminal::Profile profile;
        profile.id = "agent-terminal";
        profile.enabled = true;
        profile.arguments = {"/bin/echo", "fixed-agent-terminal"};
        profile.working_directory = "/tmp";
        profile.environment = {
            iotox::terminal::EnvironmentEntry{"IOTOX_FIXED", "1"},
        };
        iotox::terminal::Binding binding;
        binding.principal_id = principal;
        binding.profile_id = profile.id;
        binding.enabled = true;

        auto profile_bytes = iotox::terminal::encode_profile_record(profile);
        auto binding_bytes = iotox::terminal::encode_binding_record(binding);
        IOTOX_CHECK(profile_bytes.ok());
        IOTOX_CHECK(binding_bytes.ok());
        write_private_record(
            profiles / (profile.id + ".profile"), profile_bytes.value());
        write_private_record(
            bindings / (lowercase_principal_hex(principal) + ".binding"),
            binding_bytes.value());
    }
};

void rewrite_profile_for_cgroup_containment(
    const RatoxProfileStoreFixture &fixture) {
    iotox::terminal::Profile profile;
    profile.id = "agent-terminal";
    profile.enabled = true;
    profile.arguments = {"/bin/echo", "fixed-agent-terminal"};
    profile.working_directory = "/tmp";
    profile.environment = {
        iotox::terminal::EnvironmentEntry{"IOTOX_FIXED", "1"},
    };
    profile.identity.mode = iotox::terminal::IdentityMode::exact;
    const std::uint64_t effective_uid =
        static_cast<std::uint64_t>(::geteuid());
    profile.identity.uid = effective_uid == 65534U ? 65533U : 65534U;
    profile.identity.gid = profile.identity.uid;
    profile.identity.clear_supplementary_groups = true;
    profile.confinement = iotox::terminal::ConfinementMode::baseline;

    auto profile_bytes = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(profile_bytes.ok());
    write_private_record(
        fixture.root / "profiles" / (profile.id + ".profile"),
        profile_bytes.value());
}

void rewrite_profile_with_cgroup_budget(
    const RatoxProfileStoreFixture &fixture) {
    iotox::terminal::Profile profile;
    profile.id = "agent-terminal";
    profile.enabled = true;
    profile.arguments = {"/bin/echo", "fixed-agent-terminal"};
    profile.working_directory = "/tmp";
    profile.environment = {
        iotox::terminal::EnvironmentEntry{"IOTOX_FIXED", "1"},
    };
    profile.cgroup_limits.maximum_processes = 3U;

    auto profile_bytes = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(profile_bytes.ok());
    write_private_record(
        fixture.root / "profiles" / (profile.id + ".profile"),
        profile_bytes.value());
}

void initialize_mock_v1_authority(iotox::Agent::Config &config) {
    const std::filesystem::path state_directory =
        config.transport.state_path.parent_path();
    if (!std::filesystem::exists(state_directory)) {
        IOTOX_CHECK(std::filesystem::create_directories(state_directory));
    }
    IOTOX_CHECK(::chmod(
        state_directory.c_str(), static_cast<mode_t>(0700)) == 0);

    config.security.device_identity_path =
        state_directory / "device.identity";
    config.security.authority_ledger_path =
        state_directory / "authority.ledger";

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::security::AuthorityLedger::Config ledger_config;
    ledger_config.path = config.security.authority_ledger_path;
    ledger_config.maximum_records = config.security.maximum_authority_records;
    auto ledger = iotox::security::AuthorityLedger::open(
        ledger_config, identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    std::array<std::uint8_t, iotox::security::kSigningSeedBytes> owner_seed{
        0x9DU, 0x61U, 0xB1U, 0x9DU, 0xEFU, 0xFDU, 0x5AU, 0x60U,
        0xBAU, 0x84U, 0x4AU, 0xF4U, 0x92U, 0xECU, 0x2CU, 0xC4U,
        0x44U, 0x49U, 0xC5U, 0x69U, 0x7BU, 0x32U, 0x69U, 0x19U,
        0x70U, 0x3BU, 0xACU, 0x03U, 0x1CU, 0xAEU, 0x7FU, 0x60U};
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());
    IOTOX_CHECK(owner.value().public_key() == mock_authority_principal());

    iotox::security::AuthorityPrepareRequest bootstrap;
    bootstrap.action = iotox::security::AuthorityAction::bootstrap;
    bootstrap.role = iotox::security::PrincipalRole::owner;
    bootstrap.capabilities = iotox::security::kAuthorityV1Capabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    auto body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK_MSG(body.ok(), body.status().message());
    auto record = iotox::security::sign_authority_record_body(
        body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(record.ok(), record.status().message());
    const iotox::Status appended = ledger.value()->append(record.value());
    IOTOX_CHECK_MSG(appended.ok(), appended.message());
    iotox::security::secure_wipe(owner_seed);
}

void initialize_mock_v2_terminal_authority(iotox::Agent::Config &config) {
    const std::filesystem::path state_directory =
        config.transport.state_path.parent_path();
    if (!std::filesystem::exists(state_directory)) {
        IOTOX_CHECK(std::filesystem::create_directories(state_directory));
    }
    IOTOX_CHECK(::chmod(
        state_directory.c_str(), static_cast<mode_t>(0700)) == 0);

    config.security.device_identity_path =
        state_directory / "device.identity";
    config.security.authority_ledger_path =
        state_directory / "authority.ledger";

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::security::AuthorityLedger::Config ledger_config;
    ledger_config.path = config.security.authority_ledger_path;
    ledger_config.maximum_records = config.security.maximum_authority_records;
    auto ledger = iotox::security::AuthorityLedger::open(
        ledger_config, identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    auto owner_seed = mock_terminal_owner_seed();
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());
    IOTOX_CHECK(owner.value().public_key() != mock_authority_principal());

    iotox::security::AuthorityPrepareRequest bootstrap;
    bootstrap.action = iotox::security::AuthorityAction::bootstrap;
    bootstrap.role = iotox::security::PrincipalRole::owner;
    bootstrap.capabilities = iotox::security::kAuthorityV1Capabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    append_authority_request(
        *ledger.value(), bootstrap, owner.value().secret_key(), sodium.value());

    iotox::security::AuthorityPrepareRequest migrate;
    migrate.action = iotox::security::AuthorityAction::migrate_v2;
    migrate.role = iotox::security::PrincipalRole::owner;
    migrate.capabilities = iotox::security::kAuthorityV1Capabilities;
    migrate.issuer = owner.value().public_key();
    migrate.subject = owner.value().public_key();
    append_authority_request(
        *ledger.value(), migrate, owner.value().secret_key(), sodium.value());

    iotox::security::AuthorityPrepareRequest activate_owner;
    activate_owner.action = iotox::security::AuthorityAction::grant;
    activate_owner.role = iotox::security::PrincipalRole::owner;
    activate_owner.capabilities = iotox::security::kAuthorityV2Capabilities;
    activate_owner.issuer = owner.value().public_key();
    activate_owner.subject = owner.value().public_key();
    append_authority_request(
        *ledger.value(), activate_owner, owner.value().secret_key(),
        sodium.value());

    iotox::security::AuthorityPrepareRequest grant;
    grant.action = iotox::security::AuthorityAction::grant;
    grant.role = iotox::security::PrincipalRole::operator_role;
    grant.capabilities = static_cast<std::uint64_t>(
        iotox::security::Capability::interactive_terminal);
    grant.issuer = owner.value().public_key();
    grant.subject = mock_authority_principal();
    append_authority_request(
        *ledger.value(), grant, owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(ledger.value()->authorized(
        mock_authority_principal(), grant.capabilities));
    iotox::security::secure_wipe(owner_seed);
}

void initialize_mock_v3_sync_authority(iotox::Agent::Config &config) {
    initialize_mock_v2_terminal_authority(config);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), false);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    iotox::security::AuthorityLedger::Config ledger_config;
    ledger_config.path = config.security.authority_ledger_path;
    ledger_config.maximum_records = config.security.maximum_authority_records;
    auto ledger = iotox::security::AuthorityLedger::open(
        ledger_config, identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());
    auto owner_seed = mock_terminal_owner_seed();
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());

    iotox::security::AuthorityPrepareRequest migrate;
    migrate.action = iotox::security::AuthorityAction::migrate_v3;
    migrate.role = iotox::security::PrincipalRole::owner;
    migrate.capabilities = iotox::security::kAuthorityV2Capabilities;
    migrate.issuer = owner.value().public_key();
    migrate.subject = owner.value().public_key();
    append_authority_request(
        *ledger.value(), migrate, owner.value().secret_key(),
        sodium.value());

    iotox::security::AuthorityPrepareRequest activate;
    activate.action = iotox::security::AuthorityAction::grant;
    activate.role = iotox::security::PrincipalRole::owner;
    activate.capabilities = iotox::security::kAuthorityV3Capabilities;
    activate.issuer = owner.value().public_key();
    activate.subject = owner.value().public_key();
    append_authority_request(
        *ledger.value(), activate, owner.value().secret_key(),
        sodium.value());

    iotox::security::AuthorityPrepareRequest publisher;
    publisher.action = iotox::security::AuthorityAction::grant;
    publisher.role = iotox::security::PrincipalRole::automation;
    publisher.capabilities = static_cast<std::uint64_t>(
        iotox::security::Capability::sync_publish);
    publisher.issuer = owner.value().public_key();
    publisher.subject = mock_authority_principal();
    append_authority_request(
        *ledger.value(), publisher, owner.value().secret_key(),
        sodium.value());
    IOTOX_CHECK(ledger.value()->snapshot().format ==
                iotox::security::AuthorityLedgerFormat::v3);
    IOTOX_CHECK(ledger.value()->authorized(
        mock_authority_principal(),
        static_cast<std::uint64_t>(
            iotox::security::Capability::sync_publish)));
    iotox::security::secure_wipe(owner_seed);
}

void append_live_authority_request(
    const std::filesystem::path &control_socket,
    const iotox::security::AuthorityPrepareRequest &mutation,
    std::span<const std::uint8_t, iotox::security::kSigningSecretKeyBytes> secret_key,
    const iotox::security::Sodium &sodium,
    std::uint64_t request_id) {
    auto encoded =
        iotox::security::encode_authority_prepare_request(mutation);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto prepared = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::authority_prepare,
            request_id, std::move(encoded.value())));
    IOTOX_CHECK_MSG(prepared.ok(), prepared.status().message());
    IOTOX_CHECK_MSG(
        prepared.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(prepared.value().payload));
    IOTOX_CHECK(
        prepared.value().payload.size() ==
        iotox::security::kAuthorityRecordBodyBytes);
    iotox::security::AuthorityRecordBody body{};
    std::copy(
        prepared.value().payload.begin(), prepared.value().payload.end(),
        body.begin());
    auto signed_record = iotox::security::sign_authority_record_body(
        body, secret_key, sodium);
    IOTOX_CHECK_MSG(signed_record.ok(), signed_record.status().message());
    std::vector<std::uint8_t> record(
        signed_record.value().begin(), signed_record.value().end());
    auto appended = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::authority_append,
            request_id + 1U, std::move(record)));
    IOTOX_CHECK_MSG(appended.ok(), appended.status().message());
    IOTOX_CHECK_MSG(
        appended.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(appended.value().payload));
}

class NeverSpawnPtyFactory final : public iotox::terminal::PtyProcessFactory {
  public:
    std::atomic<std::size_t> spawn_count{0U};

    iotox::Result<std::unique_ptr<iotox::terminal::PtyProcess>> spawn(
        const iotox::terminal::ResolvedProfile &) override {
        ++spawn_count;
        return iotox::Status{
            iotox::ErrorCode::unavailable,
            "agent integration test must not spawn a PTY"};
    }
};

struct TrackingPtyState {
    std::atomic<std::size_t> hangup_signals{0U};
    std::atomic<std::size_t> terminate_signals{0U};
    std::atomic<std::size_t> kill_signals{0U};
    std::atomic<bool> exited{false};
};

class TrackingPtyProcess final : public iotox::terminal::PtyProcess {
  public:
    explicit TrackingPtyProcess(std::shared_ptr<TrackingPtyState> state)
        : state_(std::move(state)) {}

    iotox::Result<iotox::terminal::WriteResult> write(
        std::span<const std::uint8_t> bytes) override {
        return iotox::terminal::WriteResult{
            iotox::terminal::IoDisposition::progress, bytes.size()};
    }

    iotox::Result<iotox::terminal::ReadResult> read(
        std::size_t) override {
        return iotox::terminal::ReadResult{
            state_->exited.load()
                ? iotox::terminal::IoDisposition::closed
                : iotox::terminal::IoDisposition::would_block,
            {}};
    }

    iotox::Status resize(
        const iotox::terminal::Dimensions &) override {
        return iotox::Status::success();
    }

    iotox::Status send_signal(
        iotox::terminal::ProcessSignal signal) override {
        switch (signal) {
            case iotox::terminal::ProcessSignal::hangup:
                ++state_->hangup_signals;
                break;
            case iotox::terminal::ProcessSignal::terminate:
                ++state_->terminate_signals;
                break;
            case iotox::terminal::ProcessSignal::kill:
                ++state_->kill_signals;
                break;
        }
        state_->exited.store(true);
        return iotox::Status::success();
    }

    iotox::Result<std::optional<iotox::terminal::ProcessExit>> poll_exit() override {
        if (!state_->exited.load()) {
            return std::optional<iotox::terminal::ProcessExit>{};
        }
        return std::optional<iotox::terminal::ProcessExit>{
            iotox::terminal::ProcessExit{
                iotox::terminal::ExitKind::signaled, 1, false}};
    }

  private:
    std::shared_ptr<TrackingPtyState> state_;
};

class TrackingPtyFactory final : public iotox::terminal::PtyProcessFactory {
  public:
    std::atomic<std::size_t> spawn_count{0U};

    iotox::Result<std::unique_ptr<iotox::terminal::PtyProcess>> spawn(
        const iotox::terminal::ResolvedProfile &) override {
        auto state = std::make_shared<TrackingPtyState>();
        {
            std::scoped_lock lock(mutex_);
            latest_ = state;
        }
        ++spawn_count;
        return std::unique_ptr<iotox::terminal::PtyProcess>(
            new TrackingPtyProcess(std::move(state)));
    }

    std::shared_ptr<TrackingPtyState> latest() const {
        std::scoped_lock lock(mutex_);
        return latest_;
    }

  private:
    mutable std::mutex mutex_;
    std::shared_ptr<TrackingPtyState> latest_;
};

class ScopedEnvironment {
  public:
    ScopedEnvironment(const char *name, const char *value) : name_(name) {
        if (const char *existing = std::getenv(name); existing != nullptr) {
            previous_ = existing;
        }
        IOTOX_CHECK(::setenv(name, value, 1) == 0);
    }

    ~ScopedEnvironment() {
        if (previous_) {
            static_cast<void>(::setenv(name_.c_str(), previous_->c_str(), 1));
        } else {
            static_cast<void>(::unsetenv(name_.c_str()));
        }
    }

  private:
    std::string name_;
    std::optional<std::string> previous_;
};

}  // namespace

IOTOX_TEST("ratox successor agent exposes files and structured local control "
           "over mock toxcore") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr, "test runner did not provide mock toxcore");

    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state" / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state;
    config.runtime.root = runtime;

    std::string first_address;
    {
        // The first protocol packet is rejected with the official SENDQ
        // condition. The event pump must retry after tox_iterate progress and
        // still establish the machine session without operator intervention.
        ScopedEnvironment hello_sendq_once(
            "IOTOX_MOCK_HELLO_SENDQ_FAILURES", "1");
        ScopedEnvironment confirmation_sendq_once(
            "IOTOX_MOCK_CONFIRMATION_SENDQ_FAILURES", "1");
        iotox::Agent agent(config);
        const iotox::Status started = agent.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        IOTOX_CHECK(agent.running());
        first_address = agent.snapshot().address;
        IOTOX_CHECK(first_address.size() == 76U);

        const std::filesystem::path socket = runtime / "control.sock";
        auto ping = iotox::local::control_request(
            socket, request(iotox::local::ControlOperation::ping, 1U));
        IOTOX_CHECK_MSG(ping.ok(), ping.status().message());
        IOTOX_CHECK(ping.value().status == iotox::ErrorCode::ok);
        IOTOX_CHECK(iotox::local::payload_text(ping.value().payload) == "pong\n");

        auto inspect = iotox::local::control_request(
            socket, request(iotox::local::ControlOperation::inspect, 2U));
        IOTOX_CHECK(inspect.ok());
        const std::string inspection = iotox::local::payload_text(inspect.value().payload);
        IOTOX_CHECK(inspection.find("phase=running") != std::string::npos);
        IOTOX_CHECK(inspection.find("address=" + first_address) != std::string::npos);

        auto routes = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::route_inventory_show, 90U));
        IOTOX_CHECK(routes.ok());
        IOTOX_CHECK(iotox::local::payload_text(routes.value().payload) ==
                    "mode=single\nroute-set-configured=0\n");

        std::vector<std::uint8_t> public_key(32U, 0x42U);
        auto add = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::transport_peer_add, 3U, public_key));
        IOTOX_CHECK_MSG(add.ok(), add.status().message());
        IOTOX_CHECK(add.value().status == iotox::ErrorCode::ok);
        const std::uint32_t friend_number = read_u32(add.value().payload);
        IOTOX_CHECK(friend_number == 0U);

        bool saw_session = false;
        // Adding the friend causes the agent to emit its canonical HELLO. The
        // exact-ABI mock behaves as a second IoTox endpoint: it constructs a
        // distinct HELLO and the matching transcript confirmation on later
        // tox_iterate calls. This exercises the owner thread, callbacks,
        // canonical decoder, session gate and ratox-style projection.
        const std::string peer_key = [] {
            std::string value;
            value.reserve(64U);
            for (std::size_t index = 0U; index < 32U; ++index) {
                value += "42";
            }
            return value;
        }();
        const std::filesystem::path session_path =
            runtime / "peers" / peer_key / "session";
        const auto deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(10);
        while (std::chrono::steady_clock::now() < deadline && !saw_session) {
            if (std::filesystem::exists(session_path)) {
                const std::string session = read_text(session_path);
                saw_session =
                    session.find("state=confirmed") != std::string::npos &&
                    session.find("hello-sent=1") != std::string::npos &&
                    session.find("hello-received=1") != std::string::npos &&
                    session.find("confirmation-sent=1") != std::string::npos &&
                    session.find("confirmation-received=1") != std::string::npos &&
                    session.find("application-ready=1") != std::string::npos;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        IOTOX_CHECK(saw_session);

        std::vector<std::uint8_t> session_selector;
        append_u32(session_selector, friend_number);
        auto session_before_health = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::protocol_session_show,
                301U, session_selector));
        IOTOX_CHECK(session_before_health);
        IOTOX_CHECK(
            session_before_health.value().status == iotox::ErrorCode::ok);

        auto carrier_health = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::transport_route_health,
                302U));
        IOTOX_CHECK(carrier_health);
        IOTOX_CHECK(carrier_health.value().status == iotox::ErrorCode::ok);
        const std::string carrier_health_text =
            iotox::local::payload_text(carrier_health.value().payload);
        IOTOX_CHECK(
            carrier_health_text.find("network=Tox/native\n") !=
            std::string::npos);
        IOTOX_CHECK(
            carrier_health_text.find("carrier-connection=tcp\n") !=
            std::string::npos);
        IOTOX_CHECK(
            carrier_health_text.find("local-boundary=not-applicable\n") !=
            std::string::npos);
        IOTOX_CHECK(
            carrier_health_text.find("application=not-sampled\n") !=
            std::string::npos);

        std::vector<std::uint8_t> health_payload;
        append_u32(health_payload, friend_number);
        append_u32(health_payload, 2000U);
        auto application_health = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::transport_route_health,
                303U, health_payload),
            std::chrono::seconds(3));
        IOTOX_CHECK(application_health);
        IOTOX_CHECK(
            application_health.value().status == iotox::ErrorCode::ok);
        const std::string application_health_text =
            iotox::local::payload_text(application_health.value().payload);
        IOTOX_CHECK(
            application_health_text.find("application=responsive\n") !=
            std::string::npos);
        IOTOX_CHECK(
            application_health_text.find("application-rtt-us=not-sampled\n") ==
            std::string::npos);
        IOTOX_CHECK(
            application_health_text.find("application-error=none\n") !=
            std::string::npos);

        auto session_after_health = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::protocol_session_show,
                304U, session_selector));
        IOTOX_CHECK(session_after_health);
        IOTOX_CHECK(
            session_after_health.value().payload ==
            session_before_health.value().payload);

        std::vector<std::uint8_t> probe_payload;
        append_u32(probe_payload, friend_number);
        append_u32(probe_payload, 2000U);
        probe_payload.insert(
            probe_payload.end(), {'r', 'a', 't', 'o', 'x', '-', 'r', 't', 't'});
        auto probe = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::transport_message_probe,
                31U, probe_payload),
            std::chrono::seconds(3));
        IOTOX_CHECK_MSG(probe.ok(), probe.status().message());
        IOTOX_CHECK(probe.value().status == iotox::ErrorCode::ok);
        IOTOX_CHECK(probe.value().payload.size() == 12U);
        IOTOX_CHECK(read_u64_at(probe.value().payload, 4U) > 0U);

        for (const std::uint8_t carrier :
             std::array<std::uint8_t, 2U>{1U, 2U}) {
            std::vector<std::uint8_t> packet_probe_payload;
            append_u32(packet_probe_payload, friend_number);
            append_u32(packet_probe_payload, 2000U);
            packet_probe_payload.push_back(carrier);
            auto packet_probe = iotox::local::control_request(
                socket,
                request(
                    iotox::local::ControlOperation::transport_packet_probe,
                    36U + carrier, packet_probe_payload),
                std::chrono::seconds(3));
            IOTOX_CHECK_MSG(
                packet_probe.ok(), packet_probe.status().message());
            IOTOX_CHECK(packet_probe.value().status == iotox::ErrorCode::ok);
            IOTOX_CHECK(packet_probe.value().payload.size() == 16U);
            IOTOX_CHECK(read_u64_at(packet_probe.value().payload, 0U) > 0U);
            IOTOX_CHECK(read_u64_at(packet_probe.value().payload, 8U) > 0U);
        }

        std::vector<std::uint8_t> burst_payload;
        append_u32(burst_payload, friend_number);
        // The deterministic mock returns every successfully queued probe, but
        // the callbacks still cross the real owner/event/control threads. Give
        // heavily contended qualification hosts enough scheduling margin so a
        // local pause cannot masquerade as transport loss. The request returns
        // immediately once all six successful sends have replies.
        append_u32(burst_payload, 5000U);
        burst_payload.push_back(2U);
        burst_payload.insert(burst_payload.end(), {0U, 8U, 0U, 0U});
        burst_payload.insert(burst_payload.end(), {4U, 0xB0U});
        ScopedEnvironment probe_sendq_failures(
            "IOTOX_MOCK_PROBE_SENDQ_FAILURES", "2");
        auto burst = iotox::local::control_request(
            socket,
            request(
                iotox::local::ControlOperation::transport_packet_probe_burst,
                39U, burst_payload),
            std::chrono::seconds(7));
        IOTOX_CHECK_MSG(burst.ok(), burst.status().message());
        IOTOX_CHECK(burst.value().status == iotox::ErrorCode::ok);
        IOTOX_CHECK(burst.value().payload.size() == 2U + 8U * 24U);
        IOTOX_CHECK(read_u16_at(burst.value().payload, 0U) == 8U);
        std::vector<bool> arrival_ranks(9U, false);
        for (std::size_t index = 0U; index < 8U; ++index) {
            const std::size_t offset = 2U + index * 24U;
            IOTOX_CHECK(read_u16_at(burst.value().payload, offset) == index + 1U);
            IOTOX_CHECK(read_u64_at(burst.value().payload, offset + 2U) > 0U);
            if (index < 2U) {
                IOTOX_CHECK(read_u64_at(
                    burst.value().payload, offset + 10U) ==
                    std::numeric_limits<std::uint64_t>::max());
                IOTOX_CHECK(read_u16_at(
                    burst.value().payload, offset + 18U) == 0U);
                IOTOX_CHECK(read_u16_at(
                    burst.value().payload, offset + 20U) == 0U);
                IOTOX_CHECK(read_u16_at(
                    burst.value().payload, offset + 22U) ==
                    static_cast<std::uint16_t>(
                        iotox::ErrorCode::resource_exhausted));
                continue;
            }
            IOTOX_CHECK(read_u64_at(burst.value().payload, offset + 10U) > 0U);
            const std::uint16_t arrival_rank =
                read_u16_at(burst.value().payload, offset + 18U);
            IOTOX_CHECK(arrival_rank >= 1U && arrival_rank <= 6U);
            IOTOX_CHECK(!arrival_ranks[arrival_rank]);
            arrival_ranks[arrival_rank] = true;
            IOTOX_CHECK(read_u16_at(burst.value().payload, offset + 20U) == 1U);
            IOTOX_CHECK(read_u16_at(burst.value().payload, offset + 22U) == 0U);
        }
        const std::string protocol_journal =
            read_text(runtime / "peers" / peer_key / "protocol");
        IOTOX_CHECK(protocol_journal.find(
                        "direction=outgoing protocol=1.0 type=hello") !=
                    std::string::npos);
        IOTOX_CHECK(protocol_journal.find(
                        "direction=incoming protocol=1.0 type=hello") !=
                    std::string::npos);
        IOTOX_CHECK(protocol_journal.find("payload-bytes=64") !=
                    std::string::npos);
        IOTOX_CHECK(protocol_journal.find(
                        "direction=outgoing protocol=1.0 type=capabilities") !=
                    std::string::npos);
        IOTOX_CHECK(protocol_journal.find(
                        "direction=incoming protocol=1.0 type=capabilities") !=
                    std::string::npos);
        IOTOX_CHECK(protocol_journal.find("payload-bytes=256") !=
                    std::string::npos);

        auto sessions = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::protocol_session_list, 4U));
        IOTOX_CHECK_MSG(sessions.ok(), sessions.status().message());
        IOTOX_CHECK(sessions.value().status == iotox::ErrorCode::ok);
        const std::string session_list =
            iotox::local::payload_text(sessions.value().payload);
        IOTOX_CHECK(session_list.find("friend-number=0") != std::string::npos);
        IOTOX_CHECK(session_list.find("public-key=" + peer_key) !=
                    std::string::npos);
        IOTOX_CHECK(session_list.find("state=confirmed") != std::string::npos);
        IOTOX_CHECK(session_list.find("application-ready=1") !=
                    std::string::npos);
        IOTOX_CHECK(session_list.find("negotiated-protocol=1.0") !=
                    std::string::npos);
        IOTOX_CHECK(session_list.find("capability-session-v1") !=
                    std::string::npos);

        std::vector<std::uint8_t> show_payload;
        append_u32(show_payload, friend_number);
        auto shown = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::protocol_session_show, 5U,
                    show_payload));
        IOTOX_CHECK_MSG(shown.ok(), shown.status().message());
        IOTOX_CHECK(shown.value().status == iotox::ErrorCode::ok);
        const std::string session_detail =
            iotox::local::payload_text(shown.value().payload);
        // One transport connection callback must create exactly one online
        // epoch even while the control worker and event pump both refresh the
        // peer projection. An older offline snapshot may never overwrite the
        // newer transition.
        IOTOX_CHECK_MSG(
            session_detail.find("online-epoch=1") != std::string::npos,
            "inventory refresh manufactured a false reconnect epoch:\n" +
                session_detail);
        IOTOX_CHECK(session_detail.find("hello-sent=1") != std::string::npos);
        IOTOX_CHECK(session_detail.find("hello-received=1") !=
                    std::string::npos);
        IOTOX_CHECK_MSG(
            session_detail.find("hello-send-attempts=2") != std::string::npos,
            "unexpected session retry evidence:\n" + session_detail);
        IOTOX_CHECK(session_detail.find("last-hello-send-error=") ==
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("confirmation-sent=1") !=
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("confirmation-received=1") !=
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("confirmation-send-attempts=2") !=
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("last-confirmation-send-error=") ==
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("application-ready=1") !=
                    std::string::npos);
        IOTOX_CHECK(session_detail.find("negotiated-compatible=1") !=
                    std::string::npos);
        IOTOX_CHECK(session_detail.find(
                        "authorization=separate-authority-session") !=
                    std::string::npos);

        std::vector<std::uint8_t> confirm_payload;
        append_u32(confirm_payload, friend_number);
        auto confirmed_again = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::protocol_send_confirmation,
                    6U, confirm_payload));
        IOTOX_CHECK_MSG(confirmed_again.ok(),
                        confirmed_again.status().message());
        IOTOX_CHECK(confirmed_again.value().status == iotox::ErrorCode::ok);
        IOTOX_CHECK(iotox::local::payload_text(
                        confirmed_again.value().payload) ==
                    "transcript-confirmation-queued\n");

        // The explicit confirmation command is a real idempotent resend. It
        // must add another outgoing CAPABILITIES record while preserving the
        // first epoch message ID and canonical payload.
        const std::filesystem::path protocol_path =
            runtime / "peers" / peer_key / "protocol";
        const auto retry_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (count_occurrences(
                   read_text(protocol_path),
                   "direction=outgoing protocol=1.0 type=capabilities") < 2U &&
               std::chrono::steady_clock::now() < retry_deadline) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        const std::string retried_protocol_journal = read_text(protocol_path);
        IOTOX_CHECK(count_occurrences(
                        retried_protocol_journal,
                        "direction=outgoing protocol=1.0 type=capabilities") >=
                    2U);

        // A confirmed session opens only the framing gate. Exercise the raw
        // local-control -> agent -> toxcore path with a deliberately malformed
        // COMMAND payload. The exact mock consumes it as an IoTox command and
        // correctly emits no response rather than echoing application bytes.
        iotox::protocol::Frame command;
        command.type = iotox::protocol::MessageType::command;
        command.message_id = 0x1122334455667788ULL;
        command.payload = {'p', 'r', 'o', 'b', 'e'};
        auto encoded_command = iotox::protocol::encode(command);
        IOTOX_CHECK(encoded_command);
        std::vector<std::uint8_t> command_request;
        append_u32(command_request, friend_number);
        command_request.insert(command_request.end(),
                               encoded_command.value().begin(),
                               encoded_command.value().end());
        auto command_sent = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::transport_send_lossless,
                    7U, command_request));
        IOTOX_CHECK_MSG(command_sent.ok(), command_sent.status().message());
        IOTOX_CHECK(command_sent.value().status == iotox::ErrorCode::ok);

        const auto command_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (count_occurrences(read_text(protocol_path), "type=command") < 1U &&
               std::chrono::steady_clock::now() < command_deadline) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        const std::string command_journal = read_text(protocol_path);
        IOTOX_CHECK(command_journal.find(
                        "direction=outgoing protocol=1.0 type=command") !=
                    std::string::npos);
        // The exact mock may independently issue a valid device.describe
        // command after authority is established. Prove only that this exact
        // malformed frame was not reflected back as an incoming command.
        IOTOX_CHECK_MSG(
            command_journal.find(
                "direction=incoming protocol=1.0 type=command flags=0 "
                "message-id=1234605616436508552") == std::string::npos,
            "malformed outgoing command was reflected back as incoming:\n" +
                command_journal);

        // The generic lossless seam may not be used to forge a second HELLO
        // around the canonical session registry.
        iotox::protocol::Frame forged_hello;
        forged_hello.type = iotox::protocol::MessageType::hello;
        forged_hello.message_id = 99U;
        forged_hello.sequence = 1U;
        forged_hello.payload.assign(iotox::protocol::kHelloPayloadSize, 0U);
        auto encoded_forged_hello = iotox::protocol::encode(forged_hello);
        IOTOX_CHECK(encoded_forged_hello);
        std::vector<std::uint8_t> forged_request;
        append_u32(forged_request, friend_number);
        forged_request.insert(forged_request.end(),
                              encoded_forged_hello.value().begin(),
                              encoded_forged_hello.value().end());
        auto forged = iotox::local::control_request(
            socket,
            request(iotox::local::ControlOperation::transport_send_lossless,
                    8U, forged_request));
        IOTOX_CHECK_MSG(forged.ok(), forged.status().message());
        IOTOX_CHECK(forged.value().status == iotox::ErrorCode::unsupported);

        const std::filesystem::path iotox_peer =
            runtime / "peers" / peer_key / "iotox";
        IOTOX_CHECK(read_text(iotox_peer / "hello-compatible") == "1\n");
        IOTOX_CHECK(read_text(iotox_peer / "transcript-confirmed") == "1\n");
        IOTOX_CHECK(read_text(iotox_peer / "established") == "1\n");
        IOTOX_CHECK(read_text(iotox_peer / "application-ready") == "1\n");
        IOTOX_CHECK(read_text(iotox_peer / "protocol") == "1.0\n");
        IOTOX_CHECK(read_text(runtime / "self" / "address") ==
                    first_address + "\n");
        const std::string runtime_status = read_text(runtime / "status");
        IOTOX_CHECK(runtime_status.find("self-connection=tcp") !=
                    std::string::npos);
        IOTOX_CHECK(runtime_status.find("protocol-session-count=1") !=
                    std::string::npos);
        IOTOX_CHECK(runtime_status.find(
                        "compatible-protocol-session-count=1") !=
                    std::string::npos);
        IOTOX_CHECK(runtime_status.find(
                        "established-protocol-session-count=1") !=
                    std::string::npos);

        auto shutdown = iotox::local::control_request(
            socket, request(iotox::local::ControlOperation::shutdown, 9U));
        IOTOX_CHECK(shutdown.ok());
        IOTOX_CHECK(shutdown.value().status == iotox::ErrorCode::ok);
        IOTOX_CHECK(agent.shutdown_requested());
        agent.stop();
        IOTOX_CHECK(!agent.running());
        IOTOX_CHECK(!std::filesystem::exists(socket));
    }

    IOTOX_CHECK(std::filesystem::exists(state));
    IOTOX_CHECK(std::filesystem::file_size(state) > 0U);

    {
        iotox::Agent restarted(config);
        const iotox::Status started = restarted.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        IOTOX_CHECK(restarted.snapshot().address == first_address);
        restarted.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent refuses empty savedata before creating cwd durable state") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(started.message().find("explicit Tox savedata path") !=
                std::string::npos);
    IOTOX_CHECK(!std::filesystem::exists(config.runtime.root));
    IOTOX_CHECK(!std::filesystem::exists(directory));
}

IOTOX_TEST("agent loads authenticated route inventory before transport and "
           "exposes it") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    config.security.route_set_path = directory / "state" / "routes.signed";
    config.security.route_generation_state_path =
        directory / "state" / "routes.generation";
    initialize_mock_v1_authority(config);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, sodium.value());
    IOTOX_CHECK(identity.ok());
    iotox::routes::RouteSet route_set;
    route_set.generation = 3U;
    route_set.stable_device_principal = identity.value().public_key();
    for (std::size_t index = 0U;
         index < route_set.coordinator_tox_public_key.size(); ++index) {
        route_set.coordinator_tox_public_key[index] =
            static_cast<std::uint8_t>((index * 7U + 3U) & 0xFFU);
    }
    iotox::routes::MemberPolicy protected_route;
    protected_route.tox_public_key.fill(0x11U);
    protected_route.role = iotox::routes::Role::protected_route;
    protected_route.connection_class = iotox::routes::ConnectionClass::tcp;
    protected_route.maximum_active_work = 1U;
    protected_route.restart_budget = 1U;
    iotox::routes::MemberPolicy bulk_route;
    bulk_route.tox_public_key.fill(0x22U);
    bulk_route.role = iotox::routes::Role::bulk;
    bulk_route.connection_class = iotox::routes::ConnectionClass::tcp;
    bulk_route.maximum_active_work = 8U;
    bulk_route.restart_budget = 2U;
    route_set.members = {protected_route, bulk_route};
    auto signed_set =
        iotox::routes::sign_route_set(route_set, identity.value());
    IOTOX_CHECK(signed_set.ok());
    write_private_record(config.security.route_set_path, signed_set.value());

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    auto routes = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::route_inventory_show, 91U));
    IOTOX_CHECK(routes.ok());
    IOTOX_CHECK(routes.value().status == iotox::ErrorCode::ok);
    const std::string text =
        iotox::local::payload_text(routes.value().payload);
    IOTOX_CHECK(text.find("mode=coordinated\n") == 0U);
    IOTOX_CHECK(text.find("route-set-generation=3\n") != std::string::npos);
    IOTOX_CHECK(text.find("route-count=2\n") != std::string::npos);
    IOTOX_CHECK(text.find("maximum-active-work=8") != std::string::npos);
    IOTOX_CHECK(text.find(
                    "restart-budget=2 restart-budget-remaining=2") !=
                std::string::npos);
    IOTOX_CHECK(text.find("auxiliary-worker-count=0\n") !=
                std::string::npos);
    IOTOX_CHECK(std::filesystem::file_size(
                    config.security.route_generation_state_path) == 152U);
    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent explicitly starts exact-key auxiliary route workers") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    config.security.route_set_path = directory / "state" / "routes.signed";
    config.security.route_generation_state_path =
        directory / "state" / "routes.generation";
    config.security.route_workers_enabled = true;
    config.security.route_worker_state_root = directory / "route-workers";
    initialize_mock_v1_authority(config);
    make_private_directory(config.security.route_worker_state_root);

    iotox::ToxTransport::Config primary_config = config.transport;
    primary_config.save_state_on_stop = true;
    iotox::ToxTransport primary(primary_config);
    IOTOX_CHECK(primary.start().ok());
    IOTOX_CHECK(primary.accept_friend(
                    std::vector<std::uint8_t>(32U, 0x42U)).ok());
    primary.stop();

    const auto provisional =
        config.security.route_worker_state_root / "provisional.toxsave";
    iotox::ToxTransport::Config auxiliary_config = config.transport;
    auxiliary_config.state_path = provisional;
    auxiliary_config.save_state_on_stop = true;
    iotox::ToxTransport auxiliary(auxiliary_config);
    IOTOX_CHECK(auxiliary.start().ok());
    IOTOX_CHECK(auxiliary.accept_friend(
                    std::vector<std::uint8_t>(32U, 0x43U)).ok());
    const std::string auxiliary_address = auxiliary.address_hex();
    auxiliary.stop();
    auto savedata = iotox::StateStore::read(provisional);
    IOTOX_CHECK(savedata.ok());
    IOTOX_CHECK(savedata.value().size() > 4U);
    savedata.value()[4U] ^= 0x80U;
    write_private_record(provisional, savedata.value());

    iotox::routes::ToxPublicKey auxiliary_key{};
    for (std::size_t index = 0U; index < auxiliary_key.size(); ++index) {
        const auto decode = [](char value) -> std::uint8_t {
            if (value <= '9') {
                return static_cast<std::uint8_t>(value - '0');
            }
            return static_cast<std::uint8_t>(value - 'A' + 10);
        };
        auxiliary_key[index] = static_cast<std::uint8_t>(
            (decode(auxiliary_address[index * 2U]) << 4U) |
            decode(auxiliary_address[index * 2U + 1U]));
    }
    auxiliary_key[0U] ^= 0x80U;
    std::filesystem::rename(
        provisional, iotox::routes::WorkerSupervisor::state_path_for(
                         config.security.route_worker_state_root,
                         auxiliary_key));

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, sodium.value());
    IOTOX_CHECK(identity.ok());
    iotox::routes::ToxPublicKey coordinator_key{};
    for (std::size_t index = 0U; index < coordinator_key.size(); ++index) {
        coordinator_key[index] =
            static_cast<std::uint8_t>((index * 7U + 3U) & 0xFFU);
    }
    iotox::routes::RouteSet route_set;
    route_set.generation = 4U;
    route_set.stable_device_principal = identity.value().public_key();
    route_set.coordinator_tox_public_key = coordinator_key;
    route_set.members = {
        {auxiliary_key, iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {coordinator_key, iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
    };
    auto signed_set = iotox::routes::sign_route_set(route_set, identity.value());
    IOTOX_CHECK(signed_set.ok());
    write_private_record(config.security.route_set_path, signed_set.value());

    iotox::Agent agent(config);
    const auto started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    std::string text;
    const auto deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(4);
    do {
        auto routes = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::route_inventory_show,
                    92U));
        IOTOX_CHECK(routes.ok());
        text = iotox::local::payload_text(routes.value().payload);
        if (text.find("lifecycle=ready") != std::string::npos) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    } while (std::chrono::steady_clock::now() < deadline);
    IOTOX_CHECK(text.find("lifecycle=ready") != std::string::npos);
    const std::size_t ready = text.find("lifecycle=ready");
    const std::size_t line_end = text.find('\n', ready);
    IOTOX_CHECK(text.substr(ready, line_end - ready).find(
                    "worker-id=0") == std::string::npos);
    const std::string worker_prefix =
        "auxiliary-worker=" + iotox::security::hex(auxiliary_key) + " ";
    const std::size_t worker_begin = text.find(worker_prefix);
    IOTOX_CHECK(worker_begin != std::string::npos);
    const std::size_t worker_end = text.find('\n', worker_begin);
    const std::string worker_line =
        text.substr(worker_begin, worker_end - worker_begin);
    IOTOX_CHECK(worker_line.find(" worker-id=0 ") == std::string::npos);
    IOTOX_CHECK(worker_line.find(" network-class=tox/native ") !=
                std::string::npos);
    IOTOX_CHECK(worker_line.find(" transport-running=1 ") !=
                std::string::npos);
    IOTOX_CHECK(worker_line.find(" application-ready=1 ") !=
                std::string::npos);
    IOTOX_CHECK(worker_line.find(" online-epoch=1 ") !=
                std::string::npos);
    IOTOX_CHECK(worker_line.find(" last-failure=none") !=
                std::string::npos);
    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent admits a private primary inventory before a mixed-context "
           "member proof") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    iotox::toxcore::BootstrapEndpoint endpoint;
    endpoint.host = "192.0.2.44";
    endpoint.port = 33445U;
    endpoint.public_key.fill(0x6BU);
    config.transport.bootstrap_nodes.push_back(endpoint);
    config.transport.tcp_relays.push_back(endpoint);
    config.runtime.root = directory / "run";
    config.security.route_set_path = directory / "state" / "routes.signed";
    config.security.route_generation_state_path =
        directory / "state" / "routes.generation";
    config.security.route_workers_enabled = true;
    config.security.private_route_bindings_enabled = true;
    config.security.route_worker_state_root = directory / "route-workers";
    initialize_mock_v1_authority(config);
    make_private_directory(config.security.route_worker_state_root);

    iotox::ToxTransport::Config primary_config = config.transport;
    primary_config.save_state_on_stop = true;
    iotox::ToxTransport primary(primary_config);
    IOTOX_CHECK(primary.start().ok());
    IOTOX_CHECK(primary.accept_friend(
                    std::vector<std::uint8_t>(32U, 0x42U)).ok());
    primary.stop();

    const auto provisional =
        config.security.route_worker_state_root / "provisional.toxsave";
    iotox::ToxTransport::Config auxiliary_config = config.transport;
    auxiliary_config.state_path = provisional;
    auxiliary_config.save_state_on_stop = true;
    iotox::ToxTransport auxiliary(auxiliary_config);
    IOTOX_CHECK(auxiliary.start().ok());
    IOTOX_CHECK(auxiliary.accept_friend(
                    std::vector<std::uint8_t>(32U, 0x43U)).ok());
    const std::string auxiliary_address = auxiliary.address_hex();
    auxiliary.stop();
    auto savedata = iotox::StateStore::read(provisional);
    IOTOX_CHECK(savedata.ok());
    IOTOX_CHECK(savedata.value().size() > 4U);
    savedata.value()[4U] ^= 0x80U;
    write_private_record(provisional, savedata.value());

    iotox::routes::ToxPublicKey auxiliary_key{};
    for (std::size_t index = 0U; index < auxiliary_key.size(); ++index) {
        const auto decode = [](char value) -> std::uint8_t {
            if (value <= '9') {
                return static_cast<std::uint8_t>(value - '0');
            }
            return static_cast<std::uint8_t>(value - 'A' + 10);
        };
        auxiliary_key[index] = static_cast<std::uint8_t>(
            (decode(auxiliary_address[index * 2U]) << 4U) |
            decode(auxiliary_address[index * 2U + 1U]));
    }
    auxiliary_key[0U] ^= 0x80U;
    std::filesystem::rename(
        provisional, iotox::routes::WorkerSupervisor::state_path_for(
                         config.security.route_worker_state_root,
                         auxiliary_key));
    config.security.route_worker_network_overrides.push_back(
        iotox::routes::WorkerNetworkOverride{
            auxiliary_key,
            {iotox::TransportKind::tox, iotox::ToxRoute::tor},
            iotox::Socks5ProxyEndpoint{"127.0.0.1", 9050U}, {}, {}});

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, sodium.value());
    IOTOX_CHECK(identity.ok());
    iotox::routes::ToxPublicKey coordinator_key{};
    for (std::size_t index = 0U; index < coordinator_key.size(); ++index) {
        coordinator_key[index] =
            static_cast<std::uint8_t>((index * 7U + 3U) & 0xFFU);
    }
    iotox::routes::RouteSet route_set;
    route_set.generation = 6U;
    route_set.stable_device_principal = identity.value().public_key();
    route_set.coordinator_tox_public_key = coordinator_key;
    route_set.members = {
        {auxiliary_key, iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 4U, 1U, 0U},
        {coordinator_key, iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
    };
    auto signed_set = iotox::routes::sign_route_set(
        route_set, identity.value());
    IOTOX_CHECK(signed_set.ok());
    write_private_record(config.security.route_set_path, signed_set.value());

    const std::string audit_path =
        (directory / "private-route-audit.log").string();
    const std::string options_audit_path =
        (directory / "private-route-options.log").string();
    ScopedEnvironment audit(
        "IOTOX_MOCK_AUTHORITY_AUDIT", audit_path.c_str());
    ScopedEnvironment options_audit(
        "IOTOX_MOCK_OPTIONS_AUDIT", options_audit_path.c_str());
    iotox::Agent agent(config);
    const auto started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::string route_status;
    std::string audit_text;
    const auto deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(6);
    std::uint64_t request_id = 930U;
    do {
        auto routes = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::route_inventory_show,
                    request_id++));
        IOTOX_CHECK_MSG(routes.ok(), routes.status().message());
        route_status = iotox::local::payload_text(routes.value().payload);
        audit_text = read_text(audit_path);
        if (route_status.find("lifecycle=ready") != std::string::npos &&
            audit_text.find("private-route-inventory-verified") !=
                std::string::npos &&
            audit_text.find("private-route-member-verified") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    } while (std::chrono::steady_clock::now() < deadline);
    IOTOX_CHECK_MSG(
        route_status.find("lifecycle=ready") != std::string::npos,
        route_status);
    IOTOX_CHECK(audit_text.find("private-route-inventory-verified") !=
                std::string::npos);
    IOTOX_CHECK(audit_text.find("private-route-member-verified") !=
                std::string::npos);
    const std::string options_text = read_text(options_audit_path);
    IOTOX_CHECK(
        options_text.find(
            "udp=1 local-discovery=1 dht-announcements=1 hole-punching=1 "
            "proxy=0 proxy-host= proxy-port=0 disable-dns=0") !=
        std::string::npos);
    IOTOX_CHECK(options_text.find(
                    "udp=0 local-discovery=0 dht-announcements=0 "
                    "hole-punching=0 proxy=2 "
                    "proxy-host=127.0.0.1 proxy-port=9050 disable-dns=1") !=
                std::string::npos);

    std::vector<std::uint8_t> remove_primary;
    append_u32(remove_primary, 0U);
    auto removed = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(
            iotox::local::ControlOperation::transport_peer_remove,
            request_id++, std::move(remove_primary)));
    IOTOX_CHECK_MSG(removed.ok(), removed.status().message());
    IOTOX_CHECK(removed.value().status == iotox::ErrorCode::ok);
    const auto withdrawal_deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(4);
    do {
        auto routes = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::route_inventory_show,
                    request_id++));
        IOTOX_CHECK_MSG(routes.ok(), routes.status().message());
        route_status = iotox::local::payload_text(routes.value().payload);
        if (route_status.find("lifecycle=ready") == std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    } while (std::chrono::steady_clock::now() < withdrawal_deadline);
    IOTOX_CHECK_MSG(
        route_status.find("lifecycle=ready") == std::string::npos,
        route_status);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent rejects invalid route inventory before toxcore creates savedata") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    config.security.route_set_path = directory / "state" / "routes.signed";
    initialize_mock_v1_authority(config);
    write_private_record(config.security.route_set_path,
                         std::vector<std::uint8_t>(252U, 0U));

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.message().find(
                    "unable to load authenticated IoTox route inventory") !=
                std::string::npos);
    IOTOX_CHECK(!std::filesystem::exists(config.transport.state_path));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent rejects a v2 signed primary network mismatch before toxcore") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    config.security.route_set_path = directory / "state" / "routes.signed";
    config.security.route_generation_state_path =
        directory / "state" / "routes.generation";
    initialize_mock_v1_authority(config);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, sodium.value());
    IOTOX_CHECK(identity.ok());
    iotox::routes::RouteSet route_set;
    route_set.format_version =
        iotox::routes::kRouteSetFormatVersionV2;
    route_set.generation = 1U;
    route_set.stable_device_principal = identity.value().public_key();
    route_set.coordinator_tox_public_key.fill(0x11U);
    iotox::routes::MemberPolicy primary;
    primary.tox_public_key = route_set.coordinator_tox_public_key;
    primary.role = iotox::routes::Role::protected_route;
    primary.connection_class = iotox::routes::ConnectionClass::tcp;
    primary.maximum_active_work = 1U;
    primary.restart_budget = 1U;
    primary.network_class = iotox::routes::NetworkClass::tox_tor;
    iotox::routes::MemberPolicy bulk;
    bulk.tox_public_key.fill(0x22U);
    bulk.role = iotox::routes::Role::bulk;
    bulk.connection_class = iotox::routes::ConnectionClass::tcp;
    bulk.maximum_active_work = 8U;
    bulk.restart_budget = 1U;
    bulk.network_class = iotox::routes::NetworkClass::tox_native;
    route_set.members = {primary, bulk};
    auto signed_set = iotox::routes::sign_route_set(
        route_set, identity.value());
    IOTOX_CHECK(signed_set.ok());
    write_private_record(config.security.route_set_path, signed_set.value());

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.message().find(
                    "primary network violates signed route-set-v2") !=
                std::string::npos);
    IOTOX_CHECK(!std::filesystem::exists(config.transport.state_path));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent exposes the controller terminal socket only behind explicit "
           "client activation") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path terminal_socket = runtime / "terminal.sock";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.interactive.client_enabled = true;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(agent.running());
    IOTOX_CHECK(agent.snapshot().ratox_enabled);
    IOTOX_CHECK(agent.snapshot().ratox_configuration_valid);

    struct stat socket_metadata {};
    IOTOX_CHECK(::lstat(terminal_socket.c_str(), &socket_metadata) == 0);
    IOTOX_CHECK(S_ISSOCK(socket_metadata.st_mode));
    IOTOX_CHECK(socket_metadata.st_uid == ::geteuid());
    IOTOX_CHECK((socket_metadata.st_mode & 0077) == 0);
    const std::string status = read_text(runtime / "status");
    IOTOX_CHECK(status.find("ratox-enabled=1") != std::string::npos);
    IOTOX_CHECK(status.find("ratox-configuration-valid=1") !=
                std::string::npos);

    auto connection = iotox::local::TerminalConnection::connect(
        terminal_socket, std::chrono::seconds(2));
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());

    iotox::local::TerminalOpenRequest request;
    request.peer_public_key.fill(0x52U);
    request.columns = 120U;
    request.rows = 40U;
    request.mode = iotox::local::TerminalOpenMode::new_session;
    auto payload = iotox::local::encode_terminal_open(request);
    IOTOX_CHECK_MSG(payload.ok(), payload.status().message());

    iotox::local::TerminalPacket open;
    open.type = iotox::local::TerminalPacketType::open;
    open.stream_id = 0x1020304050607080ULL;
    open.payload = std::move(payload).value();
    IOTOX_CHECK_MSG(
        connection.value().send(open, std::chrono::seconds(2)).ok(),
        "controller OPEN did not reach the Agent terminal server");

    auto denied = connection.value().receive(std::chrono::seconds(2));
    IOTOX_CHECK_MSG(denied.ok(), denied.status().message());
    IOTOX_CHECK(denied.value().type ==
                iotox::local::TerminalPacketType::error);
    IOTOX_CHECK(denied.value().stream_id == open.stream_id);
    IOTOX_CHECK(denied.value().status == iotox::ErrorCode::not_found);
    IOTOX_CHECK(std::string(
                    denied.value().payload.begin(), denied.value().payload.end())
                    .find("live friend map") != std::string::npos);

    connection.value().close();
    agent.stop();
    IOTOX_CHECK(!std::filesystem::exists(terminal_socket));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent terminal PING traverses Ratox and survives exact resume") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment ratox_peer("IOTOX_MOCK_RATOX_INTERACTIVE", "1");
    ScopedEnvironment ratox_host("IOTOX_MOCK_RATOX_HOST", "1");
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path control_socket = runtime / "control.sock";
    const std::filesystem::path terminal_socket = runtime / "terminal.sock";
    const std::filesystem::path transport_audit =
        directory / "ratox-client-transport.audit";
    ScopedEnvironment audit_path(
        "IOTOX_MOCK_AUTHORITY_AUDIT", transport_audit.c_str());
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.interactive.client_enabled = true;
    initialize_mock_v2_terminal_authority(config);

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> public_key(32U, 0x54U);
    auto add_peer = [&]() {
        return iotox::local::control_request(
            control_socket,
            request(
                iotox::local::ControlOperation::transport_peer_add,
                0x7001U, public_key));
    };
    auto added = add_peer();
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    std::uint32_t friend_number = read_u32(added.value().payload);
    const std::string peer_key(64U, '5');
    std::string exact_peer_key;
    exact_peer_key.reserve(64U);
    for (std::size_t index = 0U; index < 32U; ++index) {
        exact_peer_key += "54";
    }
    IOTOX_CHECK(exact_peer_key.size() == peer_key.size());
    const std::filesystem::path session_path =
        runtime / "peers" / exact_peer_key / "session";
    const std::filesystem::path authority_path =
        runtime / "peers" / exact_peer_key / "iotox" / "authority";
    const std::string principal_hex =
        "D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A";

    auto wait_for_authenticated_route = [&](std::size_t proof_count) {
        const auto deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(10);
        while (std::chrono::steady_clock::now() < deadline) {
            if (std::filesystem::exists(session_path) &&
                std::filesystem::exists(authority_path / "remote-principal")) {
                const std::string session = read_text(session_path);
                if (session.find("state=confirmed") != std::string::npos &&
                    line_with_prefix(session, "negotiated-features=")
                            .find("ratox-interactive-v1") !=
                        std::string::npos &&
                    read_text(authority_path / "remote-principal") ==
                        principal_hex + "\n" &&
                    read_text(authority_path / "remote-authorized") == "1\n" &&
                    count_occurrences(
                        read_text(transport_audit),
                        "agent-proof-verified principal=") >= proof_count) {
                    return true;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        return false;
    };
    IOTOX_CHECK(wait_for_authenticated_route(1U));

    auto connection = iotox::local::TerminalConnection::connect(
        terminal_socket, std::chrono::seconds(2));
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    iotox::local::TerminalOpenRequest open_request;
    open_request.peer_public_key.fill(0x54U);
    open_request.columns = 100U;
    open_request.rows = 30U;
    open_request.mode = iotox::local::TerminalOpenMode::new_session;
    auto open_payload = iotox::local::encode_terminal_open(open_request);
    IOTOX_CHECK_MSG(open_payload.ok(), open_payload.status().message());
    iotox::local::TerminalPacket open;
    open.type = iotox::local::TerminalPacketType::open;
    open.stream_id = 0x7000000000000001ULL;
    open.payload = std::move(open_payload).value();
    IOTOX_CHECK(connection.value().send(open, std::chrono::seconds(2)).ok());
    auto opened_packet = connection.value().receive(std::chrono::seconds(5));
    IOTOX_CHECK_MSG(opened_packet.ok(), opened_packet.status().message());
    IOTOX_CHECK_MSG(
        opened_packet.value().type ==
            iotox::local::TerminalPacketType::opened,
        "type=" + std::string(iotox::local::to_string(
                       opened_packet.value().type)) +
            " status=" + std::to_string(static_cast<unsigned int>(
                            opened_packet.value().status)) +
            " payload=" + std::string(
                            opened_packet.value().payload.begin(),
                            opened_packet.value().payload.end()));
    auto opened = iotox::local::decode_terminal_opened(
        opened_packet.value().payload);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().generation == 1U);

    iotox::local::TerminalPacket ping;
    ping.type = iotox::local::TerminalPacketType::ping;
    ping.stream_id = open.stream_id;
    IOTOX_CHECK(connection.value().send(ping, std::chrono::seconds(2)).ok());
    auto first_pong = connection.value().receive(std::chrono::seconds(5));
    IOTOX_CHECK_MSG(first_pong.ok(), first_pong.status().message());
    IOTOX_CHECK(first_pong.value().type ==
                iotox::local::TerminalPacketType::pong);
    IOTOX_CHECK(connection.value().send(ping, std::chrono::seconds(2)).ok());
    auto second_pong = connection.value().receive(std::chrono::seconds(5));
    IOTOX_CHECK_MSG(second_pong.ok(), second_pong.status().message());
    IOTOX_CHECK(second_pong.value().type ==
                iotox::local::TerminalPacketType::pong);

    std::vector<std::uint8_t> remove_payload;
    append_u32(remove_payload, friend_number);
    auto removed = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_peer_remove,
            0x7002U, std::move(remove_payload)));
    IOTOX_CHECK_MSG(removed.ok(), removed.status().message());
    IOTOX_CHECK(removed.value().status == iotox::ErrorCode::ok);
    auto route_lost = connection.value().receive(std::chrono::seconds(5));
    IOTOX_CHECK_MSG(route_lost.ok(), route_lost.status().message());
    IOTOX_CHECK(route_lost.value().type ==
                iotox::local::TerminalPacketType::error);
    IOTOX_CHECK(route_lost.value().status == iotox::ErrorCode::unavailable);
    connection.value().close();

    auto route_lost_list = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::ratox_client_session_list,
            0x7003U));
    IOTOX_CHECK_MSG(
        route_lost_list.ok(), route_lost_list.status().message());
    IOTOX_CHECK(route_lost_list.value().status == iotox::ErrorCode::ok);
    const std::string route_lost_text(
        route_lost_list.value().payload.begin(),
        route_lost_list.value().payload.end());
    IOTOX_CHECK(
        route_lost_text.find(
            "session=" + iotox::security::hex(opened.value().session_id)) !=
        std::string::npos);
    IOTOX_CHECK(route_lost_text.find(" peer=" + exact_peer_key) !=
                std::string::npos);
    IOTOX_CHECK(route_lost_text.find(" state=detached") != std::string::npos);

    added = add_peer();
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    friend_number = read_u32(added.value().payload);
    IOTOX_CHECK(wait_for_authenticated_route(2U));

    auto resumed_connection = iotox::local::TerminalConnection::connect(
        terminal_socket, std::chrono::seconds(2));
    IOTOX_CHECK_MSG(
        resumed_connection.ok(), resumed_connection.status().message());
    iotox::local::TerminalOpenRequest resume_request;
    resume_request.peer_public_key.fill(0x54U);
    resume_request.session_id = opened.value().session_id;
    resume_request.columns = 100U;
    resume_request.rows = 30U;
    resume_request.mode = iotox::local::TerminalOpenMode::resume_only;
    auto resume_payload = iotox::local::encode_terminal_open(resume_request);
    IOTOX_CHECK_MSG(resume_payload.ok(), resume_payload.status().message());
    iotox::local::TerminalPacket resume;
    resume.type = iotox::local::TerminalPacketType::open;
    resume.stream_id = 0x7000000000000002ULL;
    resume.payload = std::move(resume_payload).value();
    IOTOX_CHECK(resumed_connection.value()
                    .send(resume, std::chrono::seconds(2))
                    .ok());
    auto resumed_packet = resumed_connection.value().receive(
        std::chrono::seconds(5));
    IOTOX_CHECK_MSG(resumed_packet.ok(), resumed_packet.status().message());
    IOTOX_CHECK_MSG(
        resumed_packet.value().type ==
            iotox::local::TerminalPacketType::opened,
        "type=" + std::string(iotox::local::to_string(
                       resumed_packet.value().type)) +
            " status=" + std::to_string(static_cast<unsigned int>(
                            resumed_packet.value().status)) +
            " payload=" + std::string(
                            resumed_packet.value().payload.begin(),
                            resumed_packet.value().payload.end()));
    auto resumed = iotox::local::decode_terminal_opened(
        resumed_packet.value().payload);
    IOTOX_CHECK_MSG(resumed.ok(), resumed.status().message());
    IOTOX_CHECK(resumed.value().session_id == opened.value().session_id);
    IOTOX_CHECK(resumed.value().incarnation == opened.value().incarnation);
    IOTOX_CHECK(resumed.value().generation == opened.value().generation + 1U);

    ping.stream_id = resume.stream_id;
    IOTOX_CHECK(resumed_connection.value()
                    .send(ping, std::chrono::seconds(2))
                    .ok());
    auto resumed_pong = resumed_connection.value().receive(
        std::chrono::seconds(5));
    IOTOX_CHECK_MSG(resumed_pong.ok(), resumed_pong.status().message());
    IOTOX_CHECK(resumed_pong.value().type ==
                iotox::local::TerminalPacketType::pong);

    iotox::local::TerminalPacket detach;
    detach.type = iotox::local::TerminalPacketType::detach;
    detach.stream_id = resume.stream_id;
    IOTOX_CHECK(resumed_connection.value()
                    .send(detach, std::chrono::seconds(2))
                    .ok());
    auto detached = resumed_connection.value().receive(std::chrono::seconds(5));
    IOTOX_CHECK_MSG(detached.ok(), detached.status().message());
    IOTOX_CHECK(detached.value().type ==
                iotox::local::TerminalPacketType::detached);
    resumed_connection.value().close();

    auto listed = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::ratox_client_session_list,
            0x7004U));
    IOTOX_CHECK_MSG(listed.ok(), listed.status().message());
    IOTOX_CHECK(listed.value().status == iotox::ErrorCode::ok);
    const std::string listed_text(
        listed.value().payload.begin(), listed.value().payload.end());
    IOTOX_CHECK(
        listed_text.find(
            "session=" + iotox::security::hex(opened.value().session_id)) !=
        std::string::npos);
    IOTOX_CHECK(listed_text.find(" peer=" + exact_peer_key) !=
                std::string::npos);
    IOTOX_CHECK(listed_text.find(" state=detached") != std::string::npos);
    IOTOX_CHECK(listed_text.find("principal=") != std::string::npos);

    std::vector<std::uint8_t> close_payload(
        opened.value().session_id.begin(), opened.value().session_id.end());
    close_payload.insert(close_payload.end(), 32U, 0x54U);
    auto closed = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::ratox_client_session_close,
            0x7005U, std::move(close_payload)));
    IOTOX_CHECK_MSG(closed.ok(), closed.status().message());
    IOTOX_CHECK(closed.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(
        std::string(closed.value().payload.begin(), closed.value().payload.end()) ==
        "close=resume-then-close-queued\n");

    const auto close_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < close_deadline &&
           read_text(transport_audit).find("ratox-sent type=CLOSE") ==
               std::string::npos) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    const std::string audit = read_text(transport_audit);
    IOTOX_CHECK(count_occurrences(audit, "ratox-sent type=PING") == 3U);
    IOTOX_CHECK(audit.find("ratox-sent type=OPEN") != std::string::npos);
    IOTOX_CHECK(audit.find("ratox-sent type=RESUME") != std::string::npos);
    IOTOX_CHECK(audit.find("ratox-sent type=CLOSE") != std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent refuses an occupied terminal socket before toxcore startup") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path terminal_socket = runtime / "terminal.sock";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(runtime));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(runtime.c_str(), static_cast<mode_t>(0700)) == 0);

    const int incumbent = bind_active_terminal_socket(terminal_socket);
    struct stat before {};
    IOTOX_CHECK(::lstat(terminal_socket.c_str(), &before) == 0);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.interactive.client_enabled = true;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(started.message().find("already listening") !=
                std::string::npos);
    IOTOX_CHECK(!agent.running());
    IOTOX_CHECK(agent.snapshot().phase == "failed");
    IOTOX_CHECK(agent.snapshot().self_connection == "offline");
    IOTOX_CHECK(!std::filesystem::exists(config.transport.state_path));

    struct stat after {};
    IOTOX_CHECK(::lstat(terminal_socket.c_str(), &after) == 0);
    IOTOX_CHECK(before.st_dev == after.st_dev);
    IOTOX_CHECK(before.st_ino == after.st_ino);
    auto still_live = iotox::local::TerminalConnection::connect(
        terminal_socket, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(still_live.ok(), still_live.status().message());
    still_live.value().close();

    agent.stop();
    IOTOX_CHECK(agent.snapshot().phase == "failed");
    IOTOX_CHECK(read_text(runtime / "status").find("phase=failed") !=
                std::string::npos);
    IOTOX_CHECK(::close(incumbent) == 0);
    IOTOX_CHECK(::unlink(terminal_socket.c_str()) == 0);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent Ratox activation fails closed before transport without a "
           "profile store") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    config.interactive.enabled = true;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(started.message().find("profile store root") !=
                std::string::npos);
    IOTOX_CHECK(!agent.running());
    const auto snapshot = agent.snapshot();
    IOTOX_CHECK(snapshot.ratox_enabled);
    IOTOX_CHECK(!snapshot.ratox_configuration_valid);
    IOTOX_CHECK(snapshot.phase == "failed");
    IOTOX_CHECK(read_text(config.runtime.root / "status").find(
                    "ratox-configuration-valid=0") != std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent validates delegated cgroup containment before transport startup") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    RatoxProfileStoreFixture profile_store(directory);

    iotox::Agent::Config base;
    base.transport.toxcore_library = mock_library;
    base.transport.state_path = directory / "state" / "device.toxsave";
    base.transport.save_state_on_stop = false;
    base.interactive.enabled = true;
    base.interactive.profile_store_root = profile_store.root;
    base.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    base.interactive.helper_executable = "/bin/true";

    iotox::Agent::Config unrooted_limits = base;
    unrooted_limits.runtime.root = directory / "run-unrooted-limits";
    unrooted_limits.interactive.cgroup_resource_limits.maximum_processes = 4U;
    iotox::Agent unrooted_limits_agent(unrooted_limits);
    const iotox::Status unrooted_limits_started =
        unrooted_limits_agent.start();
    IOTOX_CHECK(!unrooted_limits_started.ok());
    IOTOX_CHECK(
        unrooted_limits_started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(unrooted_limits_started.message().find(
                    "resource limits and aggregate reservations require an "
                    "explicit delegated cgroup root") != std::string::npos);
    unrooted_limits_agent.stop();

    iotox::Agent::Config unrooted_aggregate = base;
    unrooted_aggregate.runtime.root = directory / "run-unrooted-aggregate";
    unrooted_aggregate.interactive.cgroup_aggregate_limits
        .maximum_reserved_processes = 4U;
    iotox::Agent unrooted_aggregate_agent(unrooted_aggregate);
    const iotox::Status unrooted_aggregate_started =
        unrooted_aggregate_agent.start();
    IOTOX_CHECK(!unrooted_aggregate_started.ok());
    IOTOX_CHECK(
        unrooted_aggregate_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(unrooted_aggregate_started.message().find(
                    "aggregate reservations require an explicit delegated cgroup root") !=
                std::string::npos);
    IOTOX_CHECK(
        unrooted_aggregate_agent.snapshot()
            .ratox_cgroup_aggregate_budget_configured);
    unrooted_aggregate_agent.stop();

    iotox::Agent::Config unrooted_pressure = base;
    unrooted_pressure.runtime.root = directory / "run-unrooted-pressure";
    unrooted_pressure.interactive.cgroup_pressure_admission_limits
        .maximum_cpu_some_average_10_basis_points = 125U;
    unrooted_pressure.interactive.cgroup_pressure_admission_limits
        .hysteresis_basis_points = 25U;
    unrooted_pressure.interactive.cgroup_pressure_admission_limits
        .trigger_window_microseconds = 2000000U;
    unrooted_pressure.interactive.cgroup_pressure_admission_limits
        .cpu_some_trigger_stall_microseconds = 250000U;
    iotox::Agent unrooted_pressure_agent(unrooted_pressure);
    const iotox::Status unrooted_pressure_started =
        unrooted_pressure_agent.start();
    IOTOX_CHECK(!unrooted_pressure_started.ok());
    IOTOX_CHECK(
        unrooted_pressure_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(unrooted_pressure_started.message().find(
                    "pressure admission requires the same root") !=
                std::string::npos);
    const auto unrooted_pressure_snapshot =
        unrooted_pressure_agent.snapshot();
    IOTOX_CHECK(
        unrooted_pressure_snapshot.ratox_cgroup_pressure_admission_configured);
    IOTOX_CHECK(unrooted_pressure_snapshot
                    .ratox_cgroup_pressure_admission_cpu_some_configured);
    IOTOX_CHECK(
        unrooted_pressure_snapshot
            .ratox_cgroup_pressure_admission_cpu_some_avg10_max_basis_points ==
        125U);
    IOTOX_CHECK(
        unrooted_pressure_snapshot
            .ratox_cgroup_pressure_admission_hysteresis_basis_points == 25U);
    IOTOX_CHECK(
        unrooted_pressure_snapshot
            .ratox_cgroup_pressure_admission_cpu_some_trigger_configured);
    IOTOX_CHECK(
        unrooted_pressure_snapshot
            .ratox_cgroup_pressure_admission_trigger_window_microseconds ==
        2000000U);
    IOTOX_CHECK(
        unrooted_pressure_snapshot
            .ratox_cgroup_pressure_admission_cpu_some_trigger_stall_microseconds ==
        250000U);
    unrooted_pressure_agent.stop();

    iotox::Agent::Config invalid_pressure = base;
    invalid_pressure.runtime.root = directory / "run-invalid-pressure";
    invalid_pressure.interactive.cgroup_pressure_admission_limits
        .maximum_memory_full_average_10_basis_points = 20U;
    invalid_pressure.interactive.cgroup_pressure_admission_limits
        .hysteresis_basis_points = 21U;
    iotox::Agent invalid_pressure_agent(invalid_pressure);
    const iotox::Status invalid_pressure_started =
        invalid_pressure_agent.start();
    IOTOX_CHECK(!invalid_pressure_started.ok());
    IOTOX_CHECK(
        invalid_pressure_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(invalid_pressure_started.message().find(
                    "invalid Ratox cgroup pressure admission policy") !=
                std::string::npos);
    IOTOX_CHECK(invalid_pressure_started.message().find(
                    "hysteresis must not exceed") != std::string::npos);
    invalid_pressure_agent.stop();

    iotox::Agent::Config missing_aggregate_dimension = base;
    missing_aggregate_dimension.runtime.root =
        directory / "run-missing-aggregate-dimension";
    missing_aggregate_dimension.interactive.delegated_cgroup_root =
        directory / "not-opened-cgroup-root";
    missing_aggregate_dimension.interactive.cgroup_aggregate_limits
        .maximum_reserved_processes = 4U;
    iotox::Agent missing_aggregate_dimension_agent(
        missing_aggregate_dimension);
    const iotox::Status missing_aggregate_dimension_started =
        missing_aggregate_dimension_agent.start();
    IOTOX_CHECK(!missing_aggregate_dimension_started.ok());
    IOTOX_CHECK(
        missing_aggregate_dimension_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(missing_aggregate_dimension_started.message().find(
                    "profile 'agent-terminal'") != std::string::npos);
    IOTOX_CHECK(missing_aggregate_dimension_started.message().find(
                    "finite per-session") != std::string::npos);
    missing_aggregate_dimension_agent.stop();

    iotox::Agent::Config oversized_aggregate_dimension = base;
    oversized_aggregate_dimension.runtime.root =
        directory / "run-oversized-aggregate-dimension";
    oversized_aggregate_dimension.interactive.delegated_cgroup_root =
        directory / "not-opened-cgroup-root";
    oversized_aggregate_dimension.interactive.cgroup_resource_limits
        .maximum_processes = 8U;
    oversized_aggregate_dimension.interactive.cgroup_aggregate_limits
        .maximum_reserved_processes = 4U;
    iotox::Agent oversized_aggregate_dimension_agent(
        oversized_aggregate_dimension);
    const iotox::Status oversized_aggregate_dimension_started =
        oversized_aggregate_dimension_agent.start();
    IOTOX_CHECK(!oversized_aggregate_dimension_started.ok());
    IOTOX_CHECK(
        oversized_aggregate_dimension_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(oversized_aggregate_dimension_started.message().find(
                    "exceeds the aggregate host ceiling") !=
                std::string::npos);
    oversized_aggregate_dimension_agent.stop();

    iotox::Agent::Config missing_aggregate_cpu = base;
    missing_aggregate_cpu.runtime.root =
        directory / "run-missing-aggregate-cpu";
    missing_aggregate_cpu.interactive.delegated_cgroup_root =
        directory / "not-opened-cgroup-root";
    missing_aggregate_cpu.interactive.cgroup_aggregate_limits
        .maximum_reserved_cpu_quota_microseconds = 100000U;
    missing_aggregate_cpu.interactive.cgroup_aggregate_limits
        .cpu_period_microseconds = 100000U;
    iotox::Agent missing_aggregate_cpu_agent(missing_aggregate_cpu);
    const iotox::Status missing_aggregate_cpu_started =
        missing_aggregate_cpu_agent.start();
    IOTOX_CHECK(!missing_aggregate_cpu_started.ok());
    IOTOX_CHECK(
        missing_aggregate_cpu_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(missing_aggregate_cpu_started.message().find(
                    "finite per-session") != std::string::npos);
    const auto missing_cpu_snapshot =
        missing_aggregate_cpu_agent.snapshot();
    IOTOX_CHECK(missing_cpu_snapshot.ratox_cgroup_aggregate_cpu_configured);
    IOTOX_CHECK(
        missing_cpu_snapshot
            .ratox_cgroup_aggregate_cpu_quota_max_microseconds == 100000U);
    IOTOX_CHECK(
        missing_cpu_snapshot.ratox_cgroup_aggregate_cpu_period_microseconds ==
        100000U);
    missing_aggregate_cpu_agent.stop();

    iotox::Agent::Config unrepresentable_aggregate_cpu = base;
    unrepresentable_aggregate_cpu.runtime.root =
        directory / "run-unrepresentable-aggregate-cpu";
    unrepresentable_aggregate_cpu.interactive.delegated_cgroup_root =
        directory / "not-opened-cgroup-root";
    unrepresentable_aggregate_cpu.interactive.cgroup_resource_limits
        .cpu_quota_microseconds = 1000U;
    unrepresentable_aggregate_cpu.interactive.cgroup_resource_limits
        .cpu_period_microseconds = 3000U;
    unrepresentable_aggregate_cpu.interactive.cgroup_aggregate_limits
        .maximum_reserved_cpu_quota_microseconds = 100000U;
    unrepresentable_aggregate_cpu.interactive.cgroup_aggregate_limits
        .cpu_period_microseconds = 100000U;
    iotox::Agent unrepresentable_aggregate_cpu_agent(
        unrepresentable_aggregate_cpu);
    const iotox::Status unrepresentable_aggregate_cpu_started =
        unrepresentable_aggregate_cpu_agent.start();
    IOTOX_CHECK(!unrepresentable_aggregate_cpu_started.ok());
    IOTOX_CHECK(
        unrepresentable_aggregate_cpu_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(unrepresentable_aggregate_cpu_started.message().find(
                    "exactly representable") != std::string::npos);
    IOTOX_CHECK(unrepresentable_aggregate_cpu_started.message().find(
                    "profile 'agent-terminal'") != std::string::npos);
    unrepresentable_aggregate_cpu_agent.stop();

    rewrite_profile_with_cgroup_budget(profile_store);
    iotox::Agent::Config unrooted_profile_budget = base;
    unrooted_profile_budget.runtime.root =
        directory / "run-unrooted-profile-budget";
    iotox::Agent unrooted_profile_budget_agent(unrooted_profile_budget);
    const iotox::Status unrooted_profile_budget_started =
        unrooted_profile_budget_agent.start();
    IOTOX_CHECK(!unrooted_profile_budget_started.ok());
    IOTOX_CHECK(
        unrooted_profile_budget_started.code() ==
        iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(unrooted_profile_budget_started.message().find(
                    "profile 'agent-terminal'") != std::string::npos);
    IOTOX_CHECK(unrooted_profile_budget_started.message().find(
                    "cgroup resource budget") != std::string::npos);
    unrooted_profile_budget_agent.stop();

    iotox::Agent::Config malformed_limits = base;
    malformed_limits.runtime.root = directory / "run-malformed-limits";
    malformed_limits.interactive.delegated_cgroup_root =
        directory / "unopened-cgroup-root";
    malformed_limits.interactive.cgroup_resource_limits.cpu_period_microseconds =
        100000U;
    iotox::Agent malformed_limits_agent(malformed_limits);
    const iotox::Status malformed_limits_started =
        malformed_limits_agent.start();
    IOTOX_CHECK(!malformed_limits_started.ok());
    IOTOX_CHECK(
        malformed_limits_started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(malformed_limits_started.message().find(
                    "cpu period requires an explicit cpu quota") !=
                std::string::npos);
    malformed_limits_agent.stop();

    iotox::Agent::Config relative = base;
    relative.runtime.root = directory / "run-relative";
    relative.interactive.delegated_cgroup_root = "relative/cgroup";
    iotox::Agent relative_agent(relative);
    const iotox::Status relative_started = relative_agent.start();
    IOTOX_CHECK(!relative_started.ok());
    IOTOX_CHECK(relative_started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(relative_started.message().find("normalized non-root absolute") !=
                std::string::npos);
    relative_agent.stop();

    iotox::Agent::Config injected = base;
    injected.runtime.root = directory / "run-injected";
    injected.interactive.delegated_cgroup_root = directory / "cgroup-root";
    injected.interactive.process_factory =
        std::make_shared<NeverSpawnPtyFactory>();
    iotox::Agent injected_agent(injected);
    const iotox::Status injected_started = injected_agent.start();
    IOTOX_CHECK(!injected_started.ok());
    IOTOX_CHECK(injected_started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(injected_started.message().find("injected PTY process factory") !=
                std::string::npos);
    injected_agent.stop();

    iotox::Agent::Config inherited = base;
    inherited.runtime.root = directory / "run-inherited";
    inherited.interactive.delegated_cgroup_root = directory / "cgroup-root";
    iotox::Agent inherited_agent(inherited);
    const iotox::Status inherited_started = inherited_agent.start();
    IOTOX_CHECK(!inherited_started.ok());
    IOTOX_CHECK(inherited_started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(inherited_started.message().find("non-root exact uid") !=
                std::string::npos);
    inherited_agent.stop();

    rewrite_profile_for_cgroup_containment(profile_store);
    const std::filesystem::path ordinary_root = directory / "cgroup-root";
    IOTOX_CHECK(std::filesystem::create_directory(ordinary_root));
    IOTOX_CHECK(::chmod(ordinary_root.c_str(), static_cast<mode_t>(0700)) == 0);

    iotox::Agent::Config lease_owner = base;
    lease_owner.runtime.root = directory / "run-cgroup-lease-owner";
    lease_owner.interactive.process_factory =
        std::make_shared<NeverSpawnPtyFactory>();
    iotox::Agent lease_owner_agent(lease_owner);
    const iotox::Status lease_owner_started = lease_owner_agent.start();
    IOTOX_CHECK_MSG(lease_owner_started.ok(), lease_owner_started.message());

    iotox::Agent::Config serialized = base;
    serialized.runtime.root = directory / "run-serialized-cgroup";
    serialized.interactive.delegated_cgroup_root = ordinary_root;
    iotox::Agent serialized_agent(serialized);
    const iotox::Status serialized_started = serialized_agent.start();
    IOTOX_CHECK(!serialized_started.ok());
    IOTOX_CHECK(
        serialized_started.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(serialized_started.message().find("already owns") !=
                std::string::npos);
    IOTOX_CHECK(serialized_started.message().find("cgroup v2") ==
                std::string::npos);
    serialized_agent.stop();
    lease_owner_agent.stop();

    iotox::Agent::Config ordinary = base;
    ordinary.runtime.root = directory / "run-ordinary-cgroup";
    ordinary.interactive.delegated_cgroup_root = ordinary_root;
    iotox::Agent ordinary_agent(ordinary);
    const iotox::Status ordinary_started = ordinary_agent.start();
    IOTOX_CHECK(!ordinary_started.ok());
    IOTOX_CHECK(ordinary_started.code() == iotox::ErrorCode::unsupported);
    IOTOX_CHECK(ordinary_started.message().find(
                    "validate delegated Ratox cgroup resource policy before recovery") !=
                std::string::npos);
    IOTOX_CHECK(ordinary_started.message().find("cgroup v2") !=
                std::string::npos);
    ordinary_agent.stop();

    IOTOX_CHECK(!std::filesystem::exists(base.transport.state_path));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent explicitly advertises Ratox only after secure activation") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    RatoxProfileStoreFixture profile_store(directory);
    auto factory = std::make_shared<NeverSpawnPtyFactory>();

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.interactive.enabled = true;
    config.interactive.profile_store_root = profile_store.root;
    config.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    config.interactive.process_factory = factory;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(agent.running());
    IOTOX_CHECK(agent.snapshot().ratox_enabled);
    IOTOX_CHECK(agent.snapshot().ratox_configuration_valid);
    const std::string status = read_text(runtime / "status");
    IOTOX_CHECK(status.find("ratox-enabled=1") != std::string::npos);
    IOTOX_CHECK(status.find("ratox-configuration-valid=1") !=
                std::string::npos);

    std::vector<std::uint8_t> public_key(32U, 0x52U);
    auto added = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::transport_peer_add,
            401U, public_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);

    std::string peer_key(64U, '0');
    for (std::size_t index = 0U; index < 32U; ++index) {
        peer_key[index * 2U] = '5';
        peer_key[index * 2U + 1U] = '2';
    }
    const std::filesystem::path session_path =
        runtime / "peers" / peer_key / "session";
    std::string session_projection;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < deadline) {
        if (std::filesystem::exists(session_path)) {
            session_projection = read_text(session_path);
            if (session_projection.find("state=confirmed") !=
                std::string::npos) {
                break;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(session_projection.find("state=confirmed") !=
                std::string::npos);
    const std::string local_features = line_with_prefix(
        session_projection, "local-supported-features=");
    const std::string peer_features = line_with_prefix(
        session_projection, "peer-supported-features=");
    const std::string shared_features = line_with_prefix(
        session_projection, "negotiated-features=");
    IOTOX_CHECK(local_features.find("ratox-interactive-v1") !=
                std::string::npos);
    IOTOX_CHECK(peer_features.find("ratox-interactive-v1") ==
                std::string::npos);
    IOTOX_CHECK(shared_features.find("ratox-interactive-v1") ==
                std::string::npos);
    IOTOX_CHECK(factory->spawn_count.load() == 0U);

    agent.stop();
    IOTOX_CHECK(factory->spawn_count.load() == 0U);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent advertises sync only after strict construction and exposes "
           "local state") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path policy_root = directory / "sync-policy";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(
        (policy_root / "namespaces").c_str(),
        static_cast<mode_t>(0700)) == 0);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    auto status = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_status, 451U));
    IOTOX_CHECK_MSG(status.ok(), status.status().message());
    IOTOX_CHECK(status.value().status == iotox::ErrorCode::ok);
    const std::string rendered_status =
        iotox::local::payload_text(status.value().payload);
    IOTOX_CHECK(rendered_status.find(
                    "enabled=1 feature=state-sync-v1 "
                    "range-feature=state-sync-ranges-v1 namespaces=0") !=
                std::string::npos);

    std::vector<std::uint8_t> absent_job;
    append_u64(absent_job, 77U);
    auto absent_cancel = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_cancel, 4511U,
                std::move(absent_job)));
    IOTOX_CHECK_MSG(absent_cancel.ok(),
                    absent_cancel.status().message());
    IOTOX_CHECK(absent_cancel.value().status ==
                iotox::ErrorCode::not_found);

    std::vector<std::uint8_t> absent_source;
    append_u64(absent_source, 77U);
    append_u32(absent_source, 0U);
    auto source_add = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_content_source_add,
                4512U, std::move(absent_source)));
    IOTOX_CHECK_MSG(source_add.ok(), source_add.status().message());
    IOTOX_CHECK(source_add.value().status ==
                iotox::ErrorCode::not_found);

    auto malformed_multi = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_content_pull_multi,
                4513U, {1U}));
    IOTOX_CHECK_MSG(malformed_multi.ok(),
                    malformed_multi.status().message());
    IOTOX_CHECK(malformed_multi.value().status ==
                iotox::ErrorCode::invalid_argument);

    auto malformed_routed_multi = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::
                    sync_content_pull_multi_route,
                45131U, {3U, 1U}));
    IOTOX_CHECK_MSG(malformed_routed_multi.ok(),
                    malformed_routed_multi.status().message());
    IOTOX_CHECK(malformed_routed_multi.value().status ==
                iotox::ErrorCode::invalid_argument);

    std::vector<std::uint8_t> repeated_routed_source{
        static_cast<std::uint8_t>(
            iotox::sync::SyncRouteClassConstraint::tox_native),
        1U};
    append_u32(repeated_routed_source, 0U);
    append_u32(repeated_routed_source, 0U);
    repeated_routed_source.push_back('x');
    auto repeated_routed = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::
                    sync_content_pull_multi_route,
                45132U, std::move(repeated_routed_source)));
    IOTOX_CHECK_MSG(repeated_routed.ok(),
                    repeated_routed.status().message());
    IOTOX_CHECK(repeated_routed.value().status ==
                iotox::ErrorCode::not_found);

    auto malformed_replica = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_content_replica_import,
                4514U, {1U}));
    IOTOX_CHECK_MSG(malformed_replica.ok(),
                    malformed_replica.status().message());
    IOTOX_CHECK(malformed_replica.value().status ==
                iotox::ErrorCode::invalid_argument);

    auto namespaces = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_list, 452U));
    IOTOX_CHECK_MSG(namespaces.ok(), namespaces.status().message());
    IOTOX_CHECK(namespaces.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(namespaces.value().payload) ==
                "generation=1 namespaces=0 activation-enabled=0\n");

    const std::filesystem::path namespace_root =
        directory / "installed-namespace";
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(::chmod(namespace_root.c_str(),
                        static_cast<mode_t>(0700)) == 0);
    iotox::sync::NamespacePolicy namespace_policy;
    namespace_policy.id = "field-notes";
    namespace_policy.root = namespace_root.string();
    namespace_policy.activation = iotox::sync::ActivationMode::manual;
    namespace_policy.writers = {mock_authority_principal()};
    auto namespace_record =
        iotox::sync::encode_namespace_policy(namespace_policy);
    IOTOX_CHECK_MSG(namespace_record.ok(),
                    namespace_record.status().message());
    auto installed = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_install,
            453U, namespace_record.value()));
    IOTOX_CHECK_MSG(installed.ok(), installed.status().message());
    IOTOX_CHECK_MSG(
        installed.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(installed.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(
        installed.value().payload) ==
        "namespace=field-notes decision=installed generation=2 namespaces=1\n");
    auto installed_store = iotox::sync::load_namespace_store(
        policy_root, static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK(installed_store.ok());
    std::vector<iotox::sync::NamespacePolicy> expected_installed_store;
    expected_installed_store.push_back(namespace_policy);
    IOTOX_CHECK(installed_store.value() == expected_installed_store);

    auto duplicate_install = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_install,
            454U, namespace_record.value()));
    IOTOX_CHECK_MSG(duplicate_install.ok(),
                    duplicate_install.status().message());
    IOTOX_CHECK(duplicate_install.value().status ==
                iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(
        duplicate_install.value().payload) ==
        "namespace=field-notes decision=duplicate generation=2 namespaces=1\n");

    iotox::sync::NamespacePolicy conflicting_policy = namespace_policy;
    conflicting_policy.activation = iotox::sync::ActivationMode::disabled;
    auto conflicting_record =
        iotox::sync::encode_namespace_policy(conflicting_policy);
    IOTOX_CHECK(conflicting_record.ok());
    auto conflict = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_install,
            455U, conflicting_record.value()));
    IOTOX_CHECK_MSG(conflict.ok(), conflict.status().message());
    IOTOX_CHECK(conflict.value().status == iotox::ErrorCode::unavailable);
    namespaces = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_list, 456U));
    IOTOX_CHECK(namespaces.ok());
    IOTOX_CHECK(iotox::local::payload_text(
        namespaces.value().payload).find(
            "generation=2 namespaces=1 activation-enabled=1\n") == 0U);

    auto updated = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_update,
            4561U, conflicting_record.value()));
    IOTOX_CHECK_MSG(updated.ok(), updated.status().message());
    IOTOX_CHECK_MSG(
        updated.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(updated.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(updated.value().payload) ==
                "namespace=field-notes decision=updated generation=3 namespaces=1\n");

    const std::vector<std::uint8_t> namespace_id{
        conflicting_policy.id.begin(), conflicting_policy.id.end()};
    auto repaired = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_repair,
            45611U, namespace_id));
    IOTOX_CHECK_MSG(repaired.ok(), repaired.status().message());
    IOTOX_CHECK(repaired.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(
        iotox::local::payload_text(repaired.value().payload) ==
        "namespace=field-notes inspected=0 inspected-bytes=0 verified=0 "
        "quarantined=0 quarantined-bytes=0\n");

    std::vector<std::uint8_t> gc_dry_run{0U};
    gc_dry_run.insert(gc_dry_run.end(), namespace_id.begin(),
                      namespace_id.end());
    auto gc_plan = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_gc, 45612U,
                gc_dry_run));
    IOTOX_CHECK_MSG(gc_plan.ok(), gc_plan.status().message());
    IOTOX_CHECK(gc_plan.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(gc_plan.value().payload) ==
                "namespace=field-notes mode=dry-run consistent=1 "
                "descriptor-pinned=1 rooted=0 rooted-bytes=0 candidates=0 "
                "candidate-bytes=0 purge=disabled\n");

    gc_dry_run[0U] = 1U;
    auto gc_quarantine = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_gc, 45613U,
                gc_dry_run));
    IOTOX_CHECK_MSG(gc_quarantine.ok(),
                    gc_quarantine.status().message());
    IOTOX_CHECK(gc_quarantine.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(
        iotox::local::payload_text(gc_quarantine.value().payload) ==
        "namespace=field-notes mode=quarantine candidates=0 moved=0 "
        "moved-bytes=0 durable=0 durable-bytes=0 cancelled=0 purge=disabled\n");

    auto duplicate_update = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_update,
            4562U, conflicting_record.value()));
    IOTOX_CHECK_MSG(duplicate_update.ok(),
                    duplicate_update.status().message());
    IOTOX_CHECK(duplicate_update.value().status ==
                iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(
        duplicate_update.value().payload) ==
        "namespace=field-notes decision=duplicate generation=3 namespaces=1\n");

    iotox::sync::NamespacePolicy quota_change = conflicting_policy;
    ++quota_change.quotas.maximum_store_bytes;
    auto quota_record =
        iotox::sync::encode_namespace_policy(quota_change);
    IOTOX_CHECK(quota_record.ok());
    auto refused_update = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_update,
            4563U, quota_record.value()));
    IOTOX_CHECK_MSG(refused_update.ok(),
                    refused_update.status().message());
    IOTOX_CHECK(refused_update.value().status ==
                iotox::ErrorCode::invalid_argument);

    auto removed = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_remove,
            4564U, namespace_id));
    IOTOX_CHECK_MSG(removed.ok(), removed.status().message());
    IOTOX_CHECK(removed.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(removed.value().payload) ==
                "namespace=field-notes decision=removed generation=4 namespaces=0\n");
    auto absent_remove = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_remove,
            4565U, namespace_id));
    IOTOX_CHECK_MSG(absent_remove.ok(),
                    absent_remove.status().message());
    IOTOX_CHECK(absent_remove.value().status ==
                iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(
        absent_remove.value().payload) ==
        "namespace=field-notes decision=absent generation=4 namespaces=0\n");

    auto reinstalled = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::sync_namespace_install,
            4566U, conflicting_record.value()));
    IOTOX_CHECK_MSG(reinstalled.ok(), reinstalled.status().message());
    IOTOX_CHECK(reinstalled.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(reinstalled.value().payload) ==
                "namespace=field-notes decision=installed generation=5 namespaces=1\n");

    std::vector<std::uint8_t> public_key(32U, 0x62U);
    auto added = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::transport_peer_add,
            457U, public_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);

    std::string peer_key;
    peer_key.reserve(64U);
    for (std::size_t index = 0U; index < 32U; ++index) peer_key += "62";
    std::string session_projection;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < deadline) {
        const auto projected = runtime / "peers" / peer_key / "session";
        if (std::filesystem::exists(projected)) {
            session_projection = read_text(projected);
            if (session_projection.find("state=confirmed") !=
                std::string::npos) {
                break;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(session_projection.find("state=confirmed") !=
                std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "local-supported-features=").find(
            "state-sync-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "local-supported-features=").find(
            "state-sync-ranges-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "peer-supported-features=").find(
            "state-sync-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "peer-supported-features=").find(
            "state-sync-ranges-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "negotiated-features=").find(
            "state-sync-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(
        session_projection, "negotiated-features=").find(
            "state-sync-ranges-v1") != std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent publishes one range revision through typed local control") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path artifact = directory / "artifact.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(namespace_root.c_str(),
                        static_cast<mode_t>(0700)) == 0);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const std::filesystem::path identity_path = state / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::sync::NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = namespace_root.lexically_normal().string();
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {identity.value().public_key()};
    policy.quotas.maximum_artifact_bytes = 4096U;
    policy.quotas.maximum_manifest_bytes = 4096U;
    policy.quotas.maximum_store_bytes = 16384U;
    policy.quotas.maximum_staging_bytes = 8192U;
    auto encoded_policy = iotox::sync::encode_namespace_policy(policy);
    IOTOX_CHECK_MSG(encoded_policy.ok(), encoded_policy.status().message());
    write_private_record(
        policy_root / "namespaces" / "field-notes.namespace",
        encoded_policy.value());
    const std::string artifact_bytes = "locally published range-v1 bytes";
    write_private_record(
        artifact,
        std::vector<std::uint8_t>(artifact_bytes.begin(),
                                  artifact_bytes.end()));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.security.device_identity_path = identity_path;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> payload;
    payload.push_back(static_cast<std::uint8_t>(policy.id.size()));
    payload.insert(payload.end(), policy.id.begin(), policy.id.end());
    const std::string artifact_path = artifact.string();
    payload.insert(payload.end(), artifact_path.begin(), artifact_path.end());
    auto published = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_publish, 460U,
                payload));
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK_MSG(
        published.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(published.value().payload));
    const std::string first =
        iotox::local::payload_text(published.value().payload);
    IOTOX_CHECK(first.find("generation=1") != std::string::npos);
    IOTOX_CHECK(first.find("duplicate=0") != std::string::npos);

    auto duplicate = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_publish, 461U,
                payload));
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK(duplicate.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(
        duplicate.value().payload).find("duplicate=1") !=
        std::string::npos);

    const std::string successor_bytes =
        "locally published range-v1 bytes, successor";
    write_private_record(
        artifact,
        std::vector<std::uint8_t>(successor_bytes.begin(),
                                  successor_bytes.end()));
    auto successor = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_publish, 462U,
                payload));
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK_MSG(
        successor.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(successor.value().payload));
    const std::string second =
        iotox::local::payload_text(successor.value().payload);
    IOTOX_CHECK(second.find("generation=2") != std::string::npos);
    IOTOX_CHECK(second.find("duplicate=0") != std::string::npos);

    agent.stop();
    iotox::sync::SignedHeadStore store(namespace_root);
    auto head = store.load(policy, sodium.value());
    IOTOX_CHECK_MSG(head.ok(), head.status().message());
    IOTOX_CHECK(head.value().has_value());
    IOTOX_CHECK(head.value()->generation == 2U);
    IOTOX_CHECK(head.value()->writer == identity.value().public_key());
    const iotox::sync::SyncObjectRecord artifact_object{
        iotox::sync::SyncObjectKind::artifact, head.value()->artifact,
        head.value()->artifact_bytes};
    const iotox::sync::SyncObjectRecord manifest_object{
        iotox::sync::SyncObjectKind::manifest, head.value()->manifest,
        head.value()->manifest_bytes};
    IOTOX_CHECK(iotox::sync::verify_sync_range_manifest(
        policy, iotox::sync::sync_object_path(policy, artifact_object),
        iotox::sync::sync_object_path(policy, manifest_object),
        artifact_object.identity, artifact_object.bytes,
        manifest_object.bytes).ok());
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent automatically publishes one durable namespace across restart") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root =
        policy_root / "data" / "automatic-notes";
    const std::filesystem::path policy_alias = directory / "policy-alias";
    const std::filesystem::path artifact = directory / "artifact.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(policy_root / "data"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    std::filesystem::create_directory_symlink(policy_root, policy_alias);
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "data").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const std::filesystem::path identity_path = state / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::sync::NamespacePolicy policy;
    policy.id = "automatic-notes";
    policy.root = namespace_root.lexically_normal().string();
    policy.engine = iotox::sync::Engine::content_v2;
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {identity.value().public_key()};
    const auto write_artifact = [&artifact](std::string_view value) {
        write_private_record(
            artifact,
            std::vector<std::uint8_t>(value.begin(), value.end()));
    };
    write_artifact("automatic generation one");

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.security.device_identity_path = identity_path;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;

    const auto wait_for_generation =
        [&policy, &sodium](std::uint64_t expected) {
            iotox::sync::SignedHeadStore store(policy.root);
            const auto deadline = std::chrono::steady_clock::now() +
                                  std::chrono::seconds(5);
            while (std::chrono::steady_clock::now() < deadline) {
                auto head = store.load(policy, sodium.value());
                if (head.ok() && head.value() &&
                    head.value()->generation >= expected) {
                    return true;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
            return false;
        };

    {
        iotox::Agent agent(config);
        const iotox::Status started = agent.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        const std::string recursive_namespace = "recursive-notes";
        std::vector<std::uint8_t> recursive_payload;
        append_u32(recursive_payload, 1000U);
        recursive_payload.push_back(
            static_cast<std::uint8_t>(recursive_namespace.size()));
        recursive_payload.insert(recursive_payload.end(),
                                 recursive_namespace.begin(),
                                 recursive_namespace.end());
        const std::string recursive_source =
            (policy_alias / "data").string();
        recursive_payload.insert(recursive_payload.end(),
                                 recursive_source.begin(),
                                 recursive_source.end());
        auto recursive = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_create,
                    4620U, std::move(recursive_payload)));
        IOTOX_CHECK_MSG(recursive.ok(), recursive.status().message());
        IOTOX_CHECK(recursive.value().status ==
                    iotox::ErrorCode::invalid_argument);
        IOTOX_CHECK(!std::filesystem::exists(
            policy_root / "data" / recursive_namespace));

        std::vector<std::uint8_t> payload;
        append_u32(payload, 1000U);
        payload.push_back(static_cast<std::uint8_t>(policy.id.size()));
        payload.insert(payload.end(), policy.id.begin(), policy.id.end());
        const std::string source = artifact.string();
        payload.insert(payload.end(), source.begin(), source.end());
        auto enabled = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_create,
                    4621U, std::move(payload)));
        IOTOX_CHECK_MSG(enabled.ok(), enabled.status().message());
        IOTOX_CHECK_MSG(enabled.value().status == iotox::ErrorCode::ok,
                        iotox::local::payload_text(enabled.value().payload));
        IOTOX_CHECK(iotox::local::payload_text(enabled.value().payload)
                        .find("decision=created engine=content-v2") !=
                    std::string::npos);
        IOTOX_CHECK(std::filesystem::is_directory(namespace_root));
        const bool first_generation = wait_for_generation(1U);
        if (!first_generation) {
            auto diagnostics = iotox::local::control_request(
                runtime / "control.sock",
                request(iotox::local::ControlOperation::sync_automation_list,
                        4623U));
            IOTOX_CHECK_MSG(
                first_generation,
                diagnostics.ok()
                    ? iotox::local::payload_text(
                          diagnostics.value().payload)
                    : diagnostics.status().message());
        }

        write_artifact("automatic generation two");
        IOTOX_CHECK(wait_for_generation(2U));
        auto listing = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_automation_list,
                    4622U));
        IOTOX_CHECK_MSG(listing.ok(), listing.status().message());
        IOTOX_CHECK(listing.value().status == iotox::ErrorCode::ok);
        const std::string text =
            iotox::local::payload_text(listing.value().payload);
        IOTOX_CHECK(text.find("namespace=automatic-notes mode=publish") !=
                    std::string::npos);
        IOTOX_CHECK(text.find("periodic-successes=") != std::string::npos);
        agent.stop();
    }

    std::filesystem::remove_all(runtime, ignored);
    {
        iotox::Agent restarted(config);
        const iotox::Status started = restarted.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        write_artifact("automatic generation three after restart");
        IOTOX_CHECK(wait_for_generation(3U));
        restarted.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent publishes one content revision through verified CAS control") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path artifact = directory / "artifact.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(namespace_root.c_str(),
                        static_cast<mode_t>(0700)) == 0);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const std::filesystem::path identity_path = state / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::sync::NamespacePolicy policy;
    policy.id = "content-notes";
    policy.root = namespace_root.lexically_normal().string();
    policy.engine = iotox::sync::Engine::content_v2;
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {identity.value().public_key()};
    policy.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
    policy.quotas.maximum_manifest_bytes = 128U * 1024U;
    policy.quotas.maximum_store_bytes = 8U * 1024U * 1024U;
    policy.quotas.maximum_staging_bytes = 4U * 1024U * 1024U;
    auto encoded_policy = iotox::sync::encode_namespace_policy(policy);
    IOTOX_CHECK_MSG(encoded_policy.ok(), encoded_policy.status().message());
    write_private_record(
        policy_root / "namespaces" / "content-notes.namespace",
        encoded_policy.value());
    std::vector<std::uint8_t> artifact_bytes(512U * 1024U);
    std::uint64_t random_state = 0x9e3779b97f4a7c15ULL;
    for (std::uint8_t &byte : artifact_bytes) {
        random_state ^= random_state << 13U;
        random_state ^= random_state >> 7U;
        random_state ^= random_state << 17U;
        byte = static_cast<std::uint8_t>(random_state & 0xffU);
    }
    write_private_record(artifact, artifact_bytes);

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.security.device_identity_path = identity_path;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> payload;
    payload.push_back(static_cast<std::uint8_t>(policy.id.size()));
    payload.insert(payload.end(), policy.id.begin(), policy.id.end());
    const std::string artifact_path = artifact.string();
    payload.insert(payload.end(), artifact_path.begin(), artifact_path.end());
    auto published = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_publish, 463U,
                payload));
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK_MSG(
        published.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(published.value().payload));
    const std::string text =
        iotox::local::payload_text(published.value().payload);
    IOTOX_CHECK(text.find("generation=1") != std::string::npos);
    IOTOX_CHECK(text.find("kind=content-v2") != std::string::npos);
    IOTOX_CHECK(text.find("format=flat") != std::string::npos);
    IOTOX_CHECK(text.find("objects-installed=") != std::string::npos);
    agent.stop();

    iotox::sync::SignedHeadStore heads(namespace_root);
    auto head = heads.load(policy, sodium.value());
    IOTOX_CHECK_MSG(head.ok(), head.status().message());
    IOTOX_CHECK(head.value().has_value());
    IOTOX_CHECK(head.value()->engine == iotox::sync::Engine::content_v2);
    IOTOX_CHECK(head.value()->generation == 1U);
    auto chunk = iotox::sync::resolve_sync_content_object(
        policy, *head.value(),
        iotox::sync::SyncContentObjectKind::artifact_chunk, 0U);
    IOTOX_CHECK_MSG(chunk.ok(), chunk.status().message());
    IOTOX_CHECK(chunk.value().object_bytes != 0U);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent automatically follows and activates one paged content "
           "revision through mock toxcore") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path local_root = directory / "local-namespace";
    const std::filesystem::path remote_root = directory / "remote-namespace";
    const std::filesystem::path artifact = directory / "remote-artifact.bin";
    const std::filesystem::path remote_policy_path =
        directory / "remote.namespace";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(
        std::filesystem::create_directories(policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(local_root));
    IOTOX_CHECK(std::filesystem::create_directory(remote_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(local_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(remote_root.c_str(), static_cast<mode_t>(0700)) == 0);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto publisher = mock_sync_publisher_identity(
        directory / "mock-content-publisher.identity", sodium.value());
    iotox::sync::NamespacePolicy remote_policy;
    remote_policy.id = "content-notes";
    remote_policy.root = remote_root.lexically_normal().string();
    remote_policy.engine = iotox::sync::Engine::content_v2;
    remote_policy.activation = iotox::sync::ActivationMode::manual;
    remote_policy.writers = {publisher.public_key()};
    remote_policy.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
    remote_policy.quotas.maximum_manifest_bytes = 128U * 1024U;
    remote_policy.quotas.maximum_store_bytes = 8U * 1024U * 1024U;
    remote_policy.quotas.maximum_staging_bytes = 4U * 1024U * 1024U;
    remote_policy.quotas.maximum_objects = 256U;
    remote_policy.quotas.maximum_lanes = 2U;
    remote_policy.quotas.maximum_outstanding_requests = 8U;
    remote_policy.quotas.maximum_peers = 2U;
    std::vector<std::uint8_t> artifact_bytes(384U * 1024U + 37U);
    std::uint64_t random_state = 0xd1b54a32d192ed03ULL;
    for (std::uint8_t &byte : artifact_bytes) {
        random_state ^= random_state << 13U;
        random_state ^= random_state >> 7U;
        random_state ^= random_state << 17U;
        byte = static_cast<std::uint8_t>(random_state & 0xffU);
    }
    write_private_record(artifact, artifact_bytes);
    iotox::sync::SyncContentPublicationConfig publication_config;
    publication_config.format =
        iotox::sync::SyncContentPublicationFormat::paged;
    publication_config.minimum_chunk_bytes = 4096U;
    publication_config.average_chunk_bytes = 8192U;
    publication_config.maximum_chunk_bytes = 16384U;
    publication_config.entries_per_page = 4U;
    publication_config.io_buffer_bytes = 4096U;
    publication_config.manifest_buffer_bytes = 4096U;
    publication_config.workspace_budget_bytes = 1024U * 1024U;
    publication_config.fsync_on_commit = false;
    iotox::sync::SignedHeadStore remote_heads(remote_root);
    auto published = iotox::sync::publish_local_content_revision(
        remote_policy, artifact, publisher, sodium.value(), remote_heads,
        publication_config);
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK(published.value().pages > 1U);
    auto encoded_remote_policy =
        iotox::sync::encode_namespace_policy(remote_policy);
    IOTOX_CHECK_MSG(encoded_remote_policy.ok(),
                    encoded_remote_policy.status().message());
    write_private_record(remote_policy_path, encoded_remote_policy.value());

    iotox::sync::NamespacePolicy local_policy = remote_policy;
    local_policy.root = local_root.lexically_normal().string();
    auto encoded_local_policy =
        iotox::sync::encode_namespace_policy(local_policy);
    IOTOX_CHECK_MSG(encoded_local_policy.ok(),
                    encoded_local_policy.status().message());
    write_private_record(policy_root / "namespaces" / "content-notes.namespace",
                         encoded_local_policy.value());

    ScopedEnvironment mock_namespace("IOTOX_MOCK_SYNC_NAMESPACE",
                                     local_policy.id.c_str());
    const std::string remote_policy_text = remote_policy_path.string();
    ScopedEnvironment mock_content_policy("IOTOX_MOCK_SYNC_CONTENT_POLICY",
                                          remote_policy_text.c_str());
    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    initialize_mock_v3_sync_authority(config);

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    std::vector<std::uint8_t> transport_key(32U, 0x62U);
    auto added = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_add, 464U,
                transport_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    const std::uint32_t friend_number = read_u32(added.value().payload);

    std::vector<std::uint8_t> follow_payload;
    append_u32(follow_payload, 1000U);
    follow_payload.push_back(2U);
    append_u32(follow_payload, friend_number);
    follow_payload.insert(follow_payload.end(), local_policy.id.begin(),
                          local_policy.id.end());
    bool follow_installed = false;
    std::uint64_t request_id = 465U;
    const auto authority_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < authority_deadline) {
        auto follow = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_automation_follow,
                    request_id++, follow_payload));
        IOTOX_CHECK_MSG(follow.ok(), follow.status().message());
        if (follow.value().status == iotox::ErrorCode::ok) {
            follow_installed = true;
            break;
        }
        IOTOX_CHECK_MSG(
            follow.value().status == iotox::ErrorCode::unavailable ||
                follow.value().status == iotox::ErrorCode::not_found ||
                follow.value().status == iotox::ErrorCode::protocol_error,
            "unexpected automatic follow status=" +
                std::to_string(
                    static_cast<unsigned int>(follow.value().status)) +
                " payload=" +
                iotox::local::payload_text(follow.value().payload));
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(
        follow_installed,
        "automatic follow never passed feature and v3 authority gates");

    std::string sync_status;
    const auto completion_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(15);
    while (std::chrono::steady_clock::now() < completion_deadline) {
        auto status = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_status, request_id++));
        IOTOX_CHECK_MSG(status.ok(), status.status().message());
        IOTOX_CHECK(status.value().status == iotox::ErrorCode::ok);
        sync_status = iotox::local::payload_text(status.value().payload);
        if (sync_status.find("content-job=") != std::string::npos &&
            (sync_status.find("state=complete") != std::string::npos ||
             sync_status.find("state=failed") != std::string::npos)) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(sync_status.find("content-job=") != std::string::npos &&
                        sync_status.find("state=complete") != std::string::npos,
                    sync_status);
    IOTOX_CHECK(sync_status.find("content-feature=state-sync-content-v2") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("phase=complete") != std::string::npos);
    IOTOX_CHECK(sync_status.find("committed=") != std::string::npos);
    IOTOX_CHECK(sync_status.find("content-source-job=") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" principal=") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" authority-route=") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" carrier=primary ") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" route-generation=0 ") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find(" requested=") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" committed=") != std::string::npos);
    IOTOX_CHECK(sync_status.find(" fetched-bytes=") != std::string::npos);

    auto local_identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), false);
    IOTOX_CHECK_MSG(local_identity.ok(), local_identity.status().message());
    iotox::sync::ActivatedRevisionStore active_store(local_root);
    bool automatically_activated = false;
    const auto activation_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < activation_deadline) {
        auto active = active_store.load(
            local_policy, local_identity.value().public_key(), sodium.value());
        IOTOX_CHECK_MSG(active.ok(), active.status().message());
        if (active.value() &&
            active.value()->record == published.value().publication.record) {
            automatically_activated = true;
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    IOTOX_CHECK_MSG(automatically_activated,
                    "verified automation did not activate the accepted HEAD");
    auto automation = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_automation_list,
                request_id++));
    IOTOX_CHECK_MSG(automation.ok(), automation.status().message());
    IOTOX_CHECK(automation.value().status == iotox::ErrorCode::ok);
    const std::string automation_text =
        iotox::local::payload_text(automation.value().payload);
    IOTOX_CHECK(automation_text.find(
                    "namespace=content-notes mode=follow activation=verified") !=
                std::string::npos);
    IOTOX_CHECK(automation_text.find(
                    "source-principal=" +
                    iotox::security::hex(publisher.public_key())) !=
                std::string::npos);

    auto owner_seed = mock_terminal_owner_seed();
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());
    std::vector<std::uint8_t> share_prepare_payload;
    append_u32(share_prepare_payload, friend_number);
    share_prepare_payload.insert(
        share_prepare_payload.end(), owner.value().public_key().begin(),
        owner.value().public_key().end());
    share_prepare_payload.insert(share_prepare_payload.end(),
                                 local_policy.id.begin(),
                                 local_policy.id.end());
    auto share_prepared = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_share_prepare,
                request_id++, std::move(share_prepare_payload)));
    IOTOX_CHECK_MSG(share_prepared.ok(),
                    share_prepared.status().message());
    IOTOX_CHECK_MSG(share_prepared.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(
                        share_prepared.value().payload));
    IOTOX_CHECK(
        share_prepared.value().payload.size() ==
        1U + iotox::security::kSigningPublicKeyBytes +
            iotox::security::kAuthorityRecordBodyBytes);
    IOTOX_CHECK(share_prepared.value().payload[0U] == 1U);
    iotox::security::SigningPublicKey shared_principal{};
    std::copy_n(share_prepared.value().payload.begin() + 1,
                shared_principal.size(), shared_principal.begin());
    IOTOX_CHECK(shared_principal == publisher.public_key());
    iotox::security::AuthorityRecordBody share_body{};
    std::copy_n(
        share_prepared.value().payload.begin() + 1U +
            static_cast<std::ptrdiff_t>(shared_principal.size()),
        share_body.size(), share_body.begin());
    auto share_record = iotox::security::sign_authority_record_body(
        share_body, owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(share_record.ok(), share_record.status().message());
    std::vector<std::uint8_t> share_commit_payload;
    append_u32(share_commit_payload, friend_number);
    share_commit_payload.push_back(
        static_cast<std::uint8_t>(local_policy.id.size()));
    share_commit_payload.insert(share_commit_payload.end(),
                                local_policy.id.begin(),
                                local_policy.id.end());
    share_commit_payload.insert(share_commit_payload.end(),
                                shared_principal.begin(),
                                shared_principal.end());
    share_commit_payload.insert(share_commit_payload.end(),
                                share_record.value().begin(),
                                share_record.value().end());
    auto shared = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_share_commit,
                request_id++, std::move(share_commit_payload)));
    IOTOX_CHECK_MSG(shared.ok(), shared.status().message());
    IOTOX_CHECK_MSG(shared.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(shared.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(shared.value().payload)
                    .find("access=read-only") != std::string::npos);
    IOTOX_CHECK(iotox::local::payload_text(shared.value().payload)
                    .find("authority=granted membership=added") !=
                std::string::npos);
    auto shared_policies = iotox::sync::load_namespace_store(
        policy_root, static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK_MSG(shared_policies.ok(),
                    shared_policies.status().message());
    IOTOX_CHECK(shared_policies.value().size() == 1U);
    IOTOX_CHECK(shared_policies.value().front().subscribers ==
                std::vector<iotox::sync::PrincipalId>{shared_principal});

    const std::filesystem::path writable_tree = directory / "writable-tree";
    make_private_directory(writable_tree);
    write_private_record(writable_tree / "note.txt",
                         std::vector<std::uint8_t>{'l', 'o', 'c', 'a', 'l'});
    constexpr std::string_view writable_namespace = "shared-notes";
    constexpr std::string_view included_path = "note.txt";
    constexpr std::string_view excluded_path = "cache";
    std::vector<std::uint8_t> create_payload;
    append_u32(create_payload, 1000U);
    create_payload.push_back(static_cast<std::uint8_t>(
        writable_namespace.size() | static_cast<std::size_t>(0x80U)));
    create_payload.push_back(3U);
    append_u16(create_payload,
               static_cast<std::uint16_t>(writable_tree.string().size()));
    create_payload.push_back(static_cast<std::uint8_t>(
        iotox::sync::TreeV2MetadataMode::owner_mode_v2));
    create_payload.push_back(1U);
    create_payload.push_back(1U);
    create_payload.insert(create_payload.end(), writable_namespace.begin(),
                          writable_namespace.end());
    const std::string writable_path = writable_tree.string();
    create_payload.insert(create_payload.end(), writable_path.begin(),
                          writable_path.end());
    append_u16(create_payload,
               static_cast<std::uint16_t>(included_path.size()));
    create_payload.insert(create_payload.end(), included_path.begin(),
                          included_path.end());
    append_u16(create_payload,
               static_cast<std::uint16_t>(excluded_path.size()));
    create_payload.insert(create_payload.end(), excluded_path.begin(),
                          excluded_path.end());
    auto created_writable = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_create, request_id++,
                std::move(create_payload)));
    IOTOX_CHECK_MSG(created_writable.ok(), created_writable.status().message());
    IOTOX_CHECK_MSG(
        created_writable.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(created_writable.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(created_writable.value().payload)
                    .find("engine=tree-v2 access=read-write") !=
                std::string::npos);
    IOTOX_CHECK(iotox::local::payload_text(created_writable.value().payload)
                    .find("metadata=owner-mode-v2 includes=1 excludes=1") !=
                std::string::npos);

    std::vector<std::uint8_t> interest_show_payload{
        static_cast<std::uint8_t>(writable_namespace.size()), 0U, 0U};
    interest_show_payload.insert(interest_show_payload.end(),
                                 writable_namespace.begin(),
                                 writable_namespace.end());
    auto interest_shown = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_interest,
                request_id++, interest_show_payload));
    IOTOX_CHECK_MSG(interest_shown.ok(),
                    interest_shown.status().message());
    IOTOX_CHECK_MSG(
        interest_shown.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(interest_shown.value().payload));
    const std::string interest_text =
        iotox::local::payload_text(interest_shown.value().payload);
    IOTOX_CHECK(interest_text.find("custody-intent=partial") !=
                std::string::npos);
    IOTOX_CHECK(interest_text.find("includes=1 excludes=1") !=
                std::string::npos);
    IOTOX_CHECK(interest_text.find("remote-path-authority=none") !=
                std::string::npos);

    auto interest_cleared = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_interest_clear,
                request_id++,
                std::vector<std::uint8_t>(writable_namespace.begin(),
                                          writable_namespace.end())));
    IOTOX_CHECK_MSG(interest_cleared.ok(),
                    interest_cleared.status().message());
    IOTOX_CHECK_MSG(
        interest_cleared.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(interest_cleared.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(
                    interest_cleared.value().payload)
                    .find("decision=updated custody-intent=complete") !=
                std::string::npos);

    std::vector<std::uint8_t> interest_restore_payload{
        static_cast<std::uint8_t>(writable_namespace.size()), 1U, 1U};
    interest_restore_payload.insert(interest_restore_payload.end(),
                                    writable_namespace.begin(),
                                    writable_namespace.end());
    append_u16(interest_restore_payload,
               static_cast<std::uint16_t>(included_path.size()));
    interest_restore_payload.insert(interest_restore_payload.end(),
                                    included_path.begin(), included_path.end());
    append_u16(interest_restore_payload,
               static_cast<std::uint16_t>(excluded_path.size()));
    interest_restore_payload.insert(interest_restore_payload.end(),
                                    excluded_path.begin(), excluded_path.end());
    auto interest_restored = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_interest,
                request_id++, std::move(interest_restore_payload)));
    IOTOX_CHECK_MSG(interest_restored.ok(),
                    interest_restored.status().message());
    IOTOX_CHECK_MSG(
        interest_restored.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(interest_restored.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(
                    interest_restored.value().payload)
                    .find("decision=updated custody-intent=partial") !=
                std::string::npos);

    std::vector<std::uint8_t> writable_prepare_payload;
    append_u32(writable_prepare_payload, friend_number);
    writable_prepare_payload.insert(writable_prepare_payload.end(),
                                    owner.value().public_key().begin(),
                                    owner.value().public_key().end());
    writable_prepare_payload.insert(writable_prepare_payload.end(),
                                    writable_namespace.begin(),
                                    writable_namespace.end());
    auto writable_prepared = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_share_read_write_prepare,
                request_id++, std::move(writable_prepare_payload)));
    IOTOX_CHECK_MSG(writable_prepared.ok(),
                    writable_prepared.status().message());
    IOTOX_CHECK_MSG(
        writable_prepared.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(writable_prepared.value().payload));
    const std::size_t writable_prefix =
        1U + iotox::security::kSigningPublicKeyBytes;
    IOTOX_CHECK(writable_prepared.value().payload.size() == writable_prefix ||
                writable_prepared.value().payload.size() ==
                    writable_prefix +
                        iotox::security::kAuthorityRecordBodyBytes);
    IOTOX_CHECK(writable_prepared.value().payload[0U] <= 1U);
    std::optional<iotox::security::AuthorityRecordBytes> writable_record;
    if (writable_prepared.value().payload[0U] == 1U) {
        iotox::security::AuthorityRecordBody writable_body{};
        std::copy_n(writable_prepared.value().payload.begin() +
                        static_cast<std::ptrdiff_t>(writable_prefix),
                    writable_body.size(), writable_body.begin());
        auto signed_record = iotox::security::sign_authority_record_body(
            writable_body, owner.value().secret_key(), sodium.value());
        IOTOX_CHECK_MSG(signed_record.ok(), signed_record.status().message());
        writable_record = signed_record.value();
    }
    std::vector<std::uint8_t> writable_commit_payload;
    append_u32(writable_commit_payload, friend_number);
    writable_commit_payload.push_back(
        static_cast<std::uint8_t>(writable_namespace.size()));
    writable_commit_payload.insert(writable_commit_payload.end(),
                                   writable_namespace.begin(),
                                   writable_namespace.end());
    writable_commit_payload.insert(writable_commit_payload.end(),
                                   shared_principal.begin(),
                                   shared_principal.end());
    if (writable_record) {
        writable_commit_payload.insert(writable_commit_payload.end(),
                                       writable_record->begin(),
                                       writable_record->end());
    }
    auto writable_shared = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_share_read_write_commit,
                request_id++, std::move(writable_commit_payload)));
    IOTOX_CHECK_MSG(writable_shared.ok(), writable_shared.status().message());
    IOTOX_CHECK_MSG(
        writable_shared.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(writable_shared.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(writable_shared.value().payload)
                    .find("access=read-write") != std::string::npos);
    auto writable_policies = iotox::sync::load_namespace_store(
        policy_root, static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK_MSG(writable_policies.ok(),
                    writable_policies.status().message());
    const auto writable_policy = std::find_if(
        writable_policies.value().begin(), writable_policies.value().end(),
        [](const auto &candidate) { return candidate.id == "shared-notes"; });
    IOTOX_CHECK(writable_policy != writable_policies.value().end());
    IOTOX_CHECK(writable_policy->engine == iotox::sync::Engine::tree_v2);
    IOTOX_CHECK(writable_policy->projection.metadata ==
                iotox::sync::TreeV2MetadataMode::owner_mode_v2);
    IOTOX_CHECK(writable_policy->projection.includes ==
                std::vector<std::string>{"note.txt"});
    IOTOX_CHECK(writable_policy->projection.excludes ==
                std::vector<std::string>{"cache"});
    IOTOX_CHECK(std::binary_search(writable_policy->writers.begin(),
                                   writable_policy->writers.end(),
                                   shared_principal));
    IOTOX_CHECK(std::binary_search(writable_policy->subscribers.begin(),
                                   writable_policy->subscribers.end(),
                                   shared_principal));
    auto writable_automation = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_automation_list,
                request_id++));
    IOTOX_CHECK_MSG(writable_automation.ok(),
                    writable_automation.status().message());
    IOTOX_CHECK(iotox::local::payload_text(writable_automation.value().payload)
                    .find("namespace=shared-notes mode=bidirectional") !=
                std::string::npos);
    IOTOX_CHECK(iotox::local::payload_text(writable_automation.value().payload)
                    .find("record-format=2") != std::string::npos);
    IOTOX_CHECK(iotox::local::payload_text(writable_automation.value().payload)
                    .find("source-principals=1") != std::string::npos);

    auto checkpointed = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_checkpoint,
                request_id++,
                std::vector<std::uint8_t>(writable_namespace.begin(),
                                          writable_namespace.end())));
    IOTOX_CHECK_MSG(checkpointed.ok(), checkpointed.status().message());
    IOTOX_CHECK_MSG(
        checkpointed.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(checkpointed.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(checkpointed.value().payload)
                    .find("checkpoint=1") != std::string::npos);

    iotox::sync::Digest checkpoint_record{};
    {
        auto tree_transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(*writable_policy);
        IOTOX_CHECK(tree_transaction.ok());
        iotox::sync::TreeV2BranchStore tree_branches(writable_policy->root);
        auto tree_frontier = tree_branches.load_frontier(
            *writable_policy, sodium.value(), tree_transaction.value());
        IOTOX_CHECK(tree_frontier.ok());
        const auto checkpoint_head = std::find_if(
            tree_frontier.value().begin(), tree_frontier.value().end(),
            [&local_identity](const auto &snapshot) {
                return snapshot.head.writer ==
                       local_identity.value().public_key();
            });
        IOTOX_CHECK(checkpoint_head != tree_frontier.value().end());
        IOTOX_CHECK(checkpoint_head->head.checkpoint);
        auto record = iotox::sync::tree_v2_branch_record_digest(
            *writable_policy, checkpoint_head->head, sodium.value());
        IOTOX_CHECK(record.ok());
        checkpoint_record = record.value();
    }

    std::vector<std::uint8_t> pin_payload{
        static_cast<std::uint8_t>(writable_namespace.size())};
    pin_payload.insert(pin_payload.end(), writable_namespace.begin(),
                       writable_namespace.end());
    pin_payload.insert(pin_payload.end(), checkpoint_record.begin(),
                       checkpoint_record.end());
    auto pinned = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_pin, request_id++,
                pin_payload));
    IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
    IOTOX_CHECK_MSG(pinned.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(pinned.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(pinned.value().payload)
                    .find("pins=1") != std::string::npos);
    auto retention = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_maintenance_show,
                request_id++,
                std::vector<std::uint8_t>(writable_namespace.begin(),
                                          writable_namespace.end())));
    IOTOX_CHECK_MSG(retention.ok(), retention.status().message());
    IOTOX_CHECK(iotox::local::payload_text(retention.value().payload)
                    .find("pins=1") != std::string::npos);

    write_private_record(writable_tree / "note.txt",
                         std::vector<std::uint8_t>{'n', 'e', 'w', 'e', 'r'});
    auto advanced_checkpoint = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_checkpoint,
                request_id++,
                std::vector<std::uint8_t>(writable_namespace.begin(),
                                          writable_namespace.end())));
    IOTOX_CHECK_MSG(advanced_checkpoint.ok(),
                    advanced_checkpoint.status().message());
    IOTOX_CHECK_MSG(
        advanced_checkpoint.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(advanced_checkpoint.value().payload));
    iotox::sync::Digest advanced_record{};
    {
        auto tree_transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(*writable_policy);
        IOTOX_CHECK(tree_transaction.ok());
        iotox::sync::TreeV2BranchStore tree_branches(writable_policy->root);
        auto tree_frontier = tree_branches.load_frontier(
            *writable_policy, sodium.value(), tree_transaction.value());
        IOTOX_CHECK(tree_frontier.ok());
        const auto local = std::find_if(
            tree_frontier.value().begin(), tree_frontier.value().end(),
            [&local_identity](const auto &snapshot) {
                return snapshot.head.writer ==
                       local_identity.value().public_key();
            });
        IOTOX_CHECK(local != tree_frontier.value().end());
        auto record = iotox::sync::tree_v2_branch_record_digest(
            *writable_policy, local->head, sodium.value());
        IOTOX_CHECK(record.ok());
        advanced_record = record.value();
    }
    IOTOX_CHECK(advanced_record != checkpoint_record);

    std::vector<std::uint8_t> history_payload{0U, 16U};
    history_payload.insert(history_payload.end(), writable_namespace.begin(),
                           writable_namespace.end());
    auto history = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_history,
                request_id++, std::move(history_payload)));
    IOTOX_CHECK_MSG(history.ok(), history.status().message());
    IOTOX_CHECK_MSG(history.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(history.value().payload));
    const std::string history_text =
        iotox::local::payload_text(history.value().payload);
    IOTOX_CHECK(history_text.find("backup=0") != std::string::npos);
    IOTOX_CHECK(history_text.find(iotox::security::hex(checkpoint_record)) !=
                std::string::npos);
    IOTOX_CHECK(history_text.find(iotox::security::hex(advanced_record)) !=
                std::string::npos);

    std::vector<std::uint8_t> diff_payload{
        static_cast<std::uint8_t>(writable_namespace.size())};
    diff_payload.insert(diff_payload.end(), writable_namespace.begin(),
                        writable_namespace.end());
    diff_payload.insert(diff_payload.end(), checkpoint_record.begin(),
                        checkpoint_record.end());
    diff_payload.insert(diff_payload.end(), advanced_record.begin(),
                        advanced_record.end());
    auto diff = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_diff, request_id++,
                std::move(diff_payload)));
    IOTOX_CHECK_MSG(diff.ok(), diff.status().message());
    IOTOX_CHECK_MSG(diff.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(diff.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(diff.value().payload)
                    .find("projected-content-changes=1") !=
                std::string::npos);

    std::vector<std::uint8_t> conflicts_payload{
        static_cast<std::uint8_t>(writable_namespace.size())};
    conflicts_payload.insert(conflicts_payload.end(),
                             writable_namespace.begin(),
                             writable_namespace.end());
    auto conflicts = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_conflicts,
                request_id++, std::move(conflicts_payload)));
    IOTOX_CHECK_MSG(conflicts.ok(), conflicts.status().message());
    IOTOX_CHECK_MSG(conflicts.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(conflicts.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(conflicts.value().payload)
                    .find("conflicts=0") != std::string::npos);

    std::vector<std::uint8_t> restore_plan_payload{
        static_cast<std::uint8_t>(writable_namespace.size())};
    restore_plan_payload.insert(restore_plan_payload.end(),
                                writable_namespace.begin(),
                                writable_namespace.end());
    restore_plan_payload.insert(restore_plan_payload.end(),
                                checkpoint_record.begin(),
                                checkpoint_record.end());
    auto restore_plan = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_restore_plan,
                request_id++, std::move(restore_plan_payload)));
    IOTOX_CHECK_MSG(restore_plan.ok(), restore_plan.status().message());
    IOTOX_CHECK_MSG(restore_plan.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(restore_plan.value().payload));
    const std::string restore_plan_text =
        iotox::local::payload_text(restore_plan.value().payload);
    IOTOX_CHECK(restore_plan_text.find("ready=1") != std::string::npos);
    const std::size_t plan_start = restore_plan_text.find(" plan=");
    IOTOX_CHECK(plan_start != std::string::npos);
    auto restore_plan_id = iotox::security::decode_hex_exact(
        restore_plan_text.substr(plan_start + 6U, 64U), 32U,
        "tree-v2 restore plan");
    IOTOX_CHECK_MSG(restore_plan_id.ok(),
                    restore_plan_id.status().message());
    std::vector<std::uint8_t> restore_forward_payload{
        static_cast<std::uint8_t>(writable_namespace.size())};
    restore_forward_payload.insert(restore_forward_payload.end(),
                                   writable_namespace.begin(),
                                   writable_namespace.end());
    restore_forward_payload.insert(restore_forward_payload.end(),
                                   checkpoint_record.begin(),
                                   checkpoint_record.end());
    restore_forward_payload.insert(restore_forward_payload.end(),
                                   restore_plan_id.value().begin(),
                                   restore_plan_id.value().end());
    auto restored_forward = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_restore_forward,
                request_id++, std::move(restore_forward_payload)));
    IOTOX_CHECK_MSG(restored_forward.ok(),
                    restored_forward.status().message());
    IOTOX_CHECK_MSG(
        restored_forward.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(restored_forward.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(restored_forward.value().payload)
                    .find("applied=1") != std::string::npos);
    const std::string restored_contents =
        read_text(writable_tree / "note.txt");
    IOTOX_CHECK(restored_contents == "local");

    std::vector<std::uint8_t> health_payload{1U};
    health_payload.insert(health_payload.end(), writable_namespace.begin(),
                          writable_namespace.end());
    auto health = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_namespace_health,
                request_id++, health_payload));
    IOTOX_CHECK_MSG(health.ok(), health.status().message());
    IOTOX_CHECK_MSG(health.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(health.value().payload));
    const std::string health_text =
        iotox::local::payload_text(health.value().payload);
    IOTOX_CHECK(health_text.find(
                    "iotox-sync-health-v1 namespace=shared-notes observation=fresh sequence=1 level=green") !=
                std::string::npos);
    IOTOX_CHECK(health_text.find("custody=partial") != std::string::npos);
    IOTOX_CHECK(health_text.find("missing-objects=0") !=
                std::string::npos);
    IOTOX_CHECK(health_text.find("backup-certified=0") !=
                std::string::npos);
    health_payload.front() = 0U;
    auto cached_health = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_namespace_health,
                request_id++, std::move(health_payload)));
    IOTOX_CHECK_MSG(cached_health.ok(), cached_health.status().message());
    IOTOX_CHECK_MSG(cached_health.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(cached_health.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(cached_health.value().payload)
                    .find("observation=cached sequence=1 level=green policy-current=1") !=
                std::string::npos);
    auto diagnostic_health = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::diagnostics_export,
                request_id++));
    IOTOX_CHECK_MSG(diagnostic_health.ok(),
                    diagnostic_health.status().message());
    IOTOX_CHECK_MSG(
        diagnostic_health.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(diagnostic_health.value().payload));
    const std::string diagnostic_health_text =
        iotox::local::payload_text(diagnostic_health.value().payload);
    IOTOX_CHECK(diagnostic_health_text.starts_with(
        "iotox-diagnostics-redacted-v3\n"));
    IOTOX_CHECK(diagnostic_health_text.find(
                    "namespace-health-total=1\nnamespace-health-verified=1\n") !=
                std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(
                    "namespace-health-green=1\nnamespace-health-yellow=0\nnamespace-health-red=0\n") !=
                std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(
                    "namespace-health-custody-partial=1\n") !=
                std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(
                    "namespace-health-backup-certified=0\n") !=
                std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(
                    "host-capabilities-probe=passive-no-fork\n") !=
                std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(
                    "host-capabilities-seccomp=") != std::string::npos);
    IOTOX_CHECK(diagnostic_health_text.find(writable_namespace) ==
                std::string::npos);

    const std::vector<std::uint8_t> writable_namespace_payload(
        writable_namespace.begin(), writable_namespace.end());
    auto tree_repaired = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_repair, request_id++,
                writable_namespace_payload));
    IOTOX_CHECK_MSG(tree_repaired.ok(), tree_repaired.status().message());
    IOTOX_CHECK_MSG(
        tree_repaired.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(tree_repaired.value().payload));
    const std::string tree_repair_text =
        iotox::local::payload_text(tree_repaired.value().payload);
    IOTOX_CHECK(
        tree_repair_text.find(
            "engine=tree-v2 branches=1 metadata=verified ") !=
        std::string::npos);
    IOTOX_CHECK(tree_repair_text.find("rollback-witness=0") !=
                std::string::npos);
    IOTOX_CHECK(
        tree_repair_text.find("workspace=present maintenance=present") !=
        std::string::npos);

    // A content-verification command must not report success while a signed
    // semantic root is corrupt, and it must not silently delete or rewrite
    // those authority-bearing bytes.
    const std::filesystem::path maintenance_path =
        std::filesystem::path(writable_policy->root) / "tree-v2" /
        "maintenance.state";
    auto maintenance_original = iotox::StateStore::read(maintenance_path);
    IOTOX_CHECK_MSG(maintenance_original.ok(),
                    maintenance_original.status().message());
    std::vector<std::uint8_t> maintenance_corrupt =
        maintenance_original.value();
    IOTOX_CHECK(!maintenance_corrupt.empty());
    maintenance_corrupt.back() ^= 0x01U;
    IOTOX_CHECK(
        iotox::StateStore::write_atomic(maintenance_path, maintenance_corrupt)
            .ok());
    auto corrupt_repair = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_repair, request_id++,
                writable_namespace_payload));
    IOTOX_CHECK_MSG(corrupt_repair.ok(), corrupt_repair.status().message());
    IOTOX_CHECK(corrupt_repair.value().status ==
                iotox::ErrorCode::protocol_error);
    auto maintenance_retained = iotox::StateStore::read(maintenance_path);
    IOTOX_CHECK(maintenance_retained.ok());
    IOTOX_CHECK(maintenance_retained.value() == maintenance_corrupt);
    IOTOX_CHECK(
        iotox::StateStore::write_atomic(maintenance_path,
                                        maintenance_original.value())
            .ok());
    auto restored_repair = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_repair, request_id++,
                writable_namespace_payload));
    IOTOX_CHECK_MSG(restored_repair.ok(), restored_repair.status().message());
    IOTOX_CHECK_MSG(
        restored_repair.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(restored_repair.value().payload));

    auto unpinned = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_unpin, request_id++,
                pin_payload));
    IOTOX_CHECK_MSG(unpinned.ok(), unpinned.status().message());
    IOTOX_CHECK(unpinned.value().status == iotox::ErrorCode::ok);
    std::vector<std::uint8_t> tree_gc_payload{0U};
    tree_gc_payload.insert(tree_gc_payload.end(), writable_namespace.begin(),
                           writable_namespace.end());
    auto tree_gc = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_gc, request_id++,
                tree_gc_payload));
    IOTOX_CHECK_MSG(tree_gc.ok(), tree_gc.status().message());
    IOTOX_CHECK_MSG(tree_gc.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(tree_gc.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(tree_gc.value().payload)
                    .find("engine=tree-v2 mode=dry-run") !=
                std::string::npos);
    auto restored_tree = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_tree_restore,
                request_id++,
                std::vector<std::uint8_t>(writable_namespace.begin(),
                                          writable_namespace.end())));
    IOTOX_CHECK_MSG(restored_tree.ok(), restored_tree.status().message());
    IOTOX_CHECK(restored_tree.value().status == iotox::ErrorCode::ok);
    iotox::security::secure_wipe(owner_seed);

    auto repaired = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_repair, request_id++,
                std::vector<std::uint8_t>(local_policy.id.begin(),
                                          local_policy.id.end())));
    IOTOX_CHECK_MSG(repaired.ok(), repaired.status().message());
    IOTOX_CHECK_MSG(repaired.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(repaired.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(repaired.value().payload)
                    .find("engine=content-v2") != std::string::npos);
    std::vector<std::uint8_t> gc_payload{0U};
    gc_payload.insert(gc_payload.end(), local_policy.id.begin(),
                      local_policy.id.end());
    auto gc = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_gc, request_id++,
                std::move(gc_payload)));
    IOTOX_CHECK_MSG(gc.ok(), gc.status().message());
    IOTOX_CHECK_MSG(gc.value().status == iotox::ErrorCode::ok,
                    iotox::local::payload_text(gc.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(gc.value().payload)
                    .find("consistent=1 traversal-complete=1") !=
                std::string::npos);
    agent.stop();

    iotox::sync::AcceptedHeadStore accepted(local_root);
    auto accepted_head = accepted.load(
        local_policy, local_identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(accepted_head.ok(), accepted_head.status().message());
    IOTOX_CHECK(accepted_head.value().has_value());
    IOTOX_CHECK(accepted_head.value()->record ==
                published.value().publication.record);
    const auto installed = iotox::sync::sync_content_object_path(
        local_policy, published.value().artifact);
    IOTOX_CHECK(read_text(installed) ==
                std::string(artifact_bytes.begin(), artifact_bytes.end()));
    IOTOX_CHECK(std::filesystem::exists(local_root / "activated-revisions" /
                                        "content-notes.activated-revision"));
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(!ignored);
}

IOTOX_TEST("agent stages confirms and expires signed updates") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path update_root = directory / "update-root";
    const std::filesystem::path update_policy_path =
        directory / "update.policy";
    const std::filesystem::path payload_path = directory / "payload.bin";
    const std::filesystem::path bundle_path = directory / "release.iub";
    const std::filesystem::path payload2_path = directory / "payload-2.bin";
    const std::filesystem::path bundle2_path = directory / "release-2.iub";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(std::filesystem::create_directory(update_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(namespace_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(update_root.c_str(), static_cast<mode_t>(0700)) == 0);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const std::filesystem::path identity_path = state / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    auto release_signer =
        iotox::security::DeviceIdentity::create_new_release(
            state / "release.identity", sodium.value());
    IOTOX_CHECK_MSG(release_signer.ok(),
                    release_signer.status().message());

    iotox::sync::NamespacePolicy namespace_policy;
    namespace_policy.id = "system-image";
    namespace_policy.root = namespace_root.lexically_normal().string();
    namespace_policy.engine = iotox::sync::Engine::range_v1;
    namespace_policy.activation = iotox::sync::ActivationMode::manual;
    namespace_policy.writers = {identity.value().public_key()};
    namespace_policy.quotas.maximum_artifact_bytes = 64U * 1024U;
    namespace_policy.quotas.maximum_manifest_bytes = 64U * 1024U;
    namespace_policy.quotas.maximum_store_bytes = 1024U * 1024U;
    namespace_policy.quotas.maximum_staging_bytes = 128U * 1024U;
    auto namespace_record =
        iotox::sync::encode_namespace_policy(namespace_policy);
    IOTOX_CHECK_MSG(namespace_record.ok(),
                    namespace_record.status().message());
    write_private_record(
        policy_root / "namespaces" / "system-image.namespace",
        namespace_record.value());

    iotox::update::UpdatePolicy update_policy;
    update_policy.namespace_id = namespace_policy.id;
    update_policy.target = "iotox-test-x86_64";
    update_policy.root = update_root;
    update_policy.maximum_payload_bytes = 64U * 1024U;
    update_policy.health_timeout_ms = 1000U;
    update_policy.trusted_signers = {
        release_signer.value().public_key()};
    auto encoded_update_policy =
        iotox::update::encode_update_policy(update_policy);
    IOTOX_CHECK_MSG(encoded_update_policy.ok(),
                    encoded_update_policy.status().message());
    write_private_record(update_policy_path,
                         encoded_update_policy.value());
    const std::string payload_bytes = "inert signed slot payload\n";
    write_private_record(
        payload_path,
        std::vector<std::uint8_t>(payload_bytes.begin(),
                                  payload_bytes.end()));
    auto bundle = iotox::update::create_signed_update_bundle(
        update_policy, payload_path, bundle_path, 1U, "1.0.0",
        release_signer.value(), sodium.value());
    IOTOX_CHECK_MSG(bundle.ok(), bundle.status().message());
    const std::string payload2_bytes = "unhealthy inert slot payload\n";
    write_private_record(
        payload2_path,
        std::vector<std::uint8_t>(payload2_bytes.begin(),
                                  payload2_bytes.end()));
    auto bundle2 = iotox::update::create_signed_update_bundle(
        update_policy, payload2_path, bundle2_path, 2U, "2.0.0",
        release_signer.value(), sodium.value());
    IOTOX_CHECK_MSG(bundle2.ok(), bundle2.status().message());

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run-first";
    config.security.device_identity_path = identity_path;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    config.update.enabled = true;
    config.update.policy_path = update_policy_path;
    initialize_mock_v1_authority(config);

    const std::filesystem::path update_head_signal =
        directory / "mock-update-stage-head";
    const std::string update_head_signal_native =
        update_head_signal.string();
    ScopedEnvironment remote_update_command(
        "IOTOX_MOCK_UPDATE_STAGE_HEAD_FILE",
        update_head_signal_native.c_str());

    iotox::update::HealthToken health_token{};
    {
        iotox::Agent agent(config);
        const iotox::Status started = agent.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        std::vector<std::uint8_t> mock_peer_key(32U, 0x42U);
        auto added_peer = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::transport_peer_add,
                    479U, std::move(mock_peer_key)));
        IOTOX_CHECK_MSG(added_peer.ok(), added_peer.status().message());
        IOTOX_CHECK_MSG(
            added_peer.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(added_peer.value().payload));
        IOTOX_CHECK(read_u32(added_peer.value().payload) == 0U);
        auto empty = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_status, 480U));
        IOTOX_CHECK_MSG(empty.ok(), empty.status().message());
        IOTOX_CHECK(iotox::local::payload_text(empty.value().payload).find(
                        "enabled=1 namespace=system-image") == 0U);
        IOTOX_CHECK(iotox::local::payload_text(empty.value().payload).find(
                        "phase=empty") != std::string::npos);

        std::vector<std::uint8_t> publish_payload;
        publish_payload.push_back(
            static_cast<std::uint8_t>(namespace_policy.id.size()));
        publish_payload.insert(publish_payload.end(), namespace_policy.id.begin(),
                               namespace_policy.id.end());
        const std::string bundle_native = bundle_path.string();
        publish_payload.insert(publish_payload.end(), bundle_native.begin(),
                               bundle_native.end());
        auto published = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::sync_publish, 481U,
                    publish_payload));
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
        IOTOX_CHECK_MSG(
            published.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(published.value().payload));

        iotox::sync::SignedHeadStore published_heads(namespace_root);
        auto signed_head = published_heads.load(namespace_policy,
                                                sodium.value());
        IOTOX_CHECK_MSG(signed_head.ok(), signed_head.status().message());
        IOTOX_CHECK(signed_head.value().has_value());
        auto candidate = iotox::sync::verified_candidate_head(
            namespace_policy, *signed_head.value(), sodium.value());
        IOTOX_CHECK_MSG(candidate.ok(), candidate.status().message());
        iotox::sync::AcceptedHeadStore accepted_heads(namespace_root);
        auto accepted = accepted_heads.accept(
            namespace_policy, candidate.value(), identity.value(),
            sodium.value());
        IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
        IOTOX_CHECK(accepted.value().accepted());

        const std::string accepted_head_text =
            iotox::security::hex(candidate.value().record) + "\n";
        write_private_record(
            update_head_signal,
            std::vector<std::uint8_t>(accepted_head_text.begin(),
                                      accepted_head_text.end()));
        std::string staged_text;
        for (std::uint64_t attempt = 0U; attempt < 100U; ++attempt) {
            auto staged = iotox::local::control_request(
                config.runtime.root / "control.sock",
                request(iotox::local::ControlOperation::update_status,
                        482U + attempt));
            IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
            IOTOX_CHECK_MSG(
                staged.value().status == iotox::ErrorCode::ok,
                iotox::local::payload_text(staged.value().payload));
            staged_text =
                iotox::local::payload_text(staged.value().payload);
            if (staged_text.find("phase=staged") !=
                std::string::npos) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        IOTOX_CHECK(staged_text.find("phase=staged") !=
                    std::string::npos);
        IOTOX_CHECK(staged_text.find("candidate-sequence=1") !=
                    std::string::npos);

        auto commands = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::command_store_show,
                    583U));
        IOTOX_CHECK_MSG(commands.ok(), commands.status().message());
        IOTOX_CHECK(commands.value().status == iotox::ErrorCode::ok);
        const std::string command_text =
            iotox::local::payload_text(commands.value().payload);
        IOTOX_CHECK(command_text.find("operation=update.stage") !=
                    std::string::npos);
        IOTOX_CHECK(command_text.find("lifecycle=succeeded") !=
                    std::string::npos);
        IOTOX_CHECK(command_text.find(
                        "expected-update-head=" +
                        iotox::security::hex(candidate.value().record)) !=
                    std::string::npos);
        IOTOX_CHECK(command_text.find(
                        "update-manifest-record=" +
                        iotox::security::hex(
                            bundle.value().manifest_record)) !=
                    std::string::npos);
        auto sessions = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::protocol_session_list,
                    584U));
        IOTOX_CHECK_MSG(sessions.ok(), sessions.status().message());
        IOTOX_CHECK(iotox::local::payload_text(
                        sessions.value().payload).find("signed-ota-v1") !=
                    std::string::npos);

        std::vector<std::uint8_t> manifest_record(
            bundle.value().manifest_record.begin(),
            bundle.value().manifest_record.end());
        auto applied = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_apply, 483U,
                    manifest_record));
        IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
        IOTOX_CHECK_MSG(
            applied.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(applied.value().payload));
        const std::string applied_text =
            iotox::local::payload_text(applied.value().payload);
        const std::size_t token_start =
            applied_text.find("health-token=");
        IOTOX_CHECK(token_start == 0U);
        const std::string token_hex = applied_text.substr(13U, 64U);
        auto decoded_token = iotox::security::decode_hex_exact(
            token_hex, health_token.size(), "update health token");
        IOTOX_CHECK_MSG(decoded_token.ok(),
                        decoded_token.status().message());
        std::copy(decoded_token.value().begin(), decoded_token.value().end(),
                  health_token.begin());
        IOTOX_CHECK(applied_text.find("restart-required=1") !=
                    std::string::npos);
        agent.stop();
    }

    config.runtime.root = directory / "run-second";
    {
        iotox::Agent restarted(config);
        const iotox::Status started = restarted.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        auto pending = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_status, 484U));
        IOTOX_CHECK_MSG(pending.ok(), pending.status().message());
        const std::string pending_text =
            iotox::local::payload_text(pending.value().payload);
        IOTOX_CHECK(pending_text.find("startup=health-window-opened") !=
                    std::string::npos);
        IOTOX_CHECK(pending_text.find("phase=awaiting-health") !=
                    std::string::npos);
        auto confirmed = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(
                iotox::local::ControlOperation::update_confirm, 485U,
                std::vector<std::uint8_t>(health_token.begin(),
                                          health_token.end())));
        IOTOX_CHECK_MSG(confirmed.ok(), confirmed.status().message());
        IOTOX_CHECK_MSG(
            confirmed.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(confirmed.value().payload));
        const std::string confirmed_text =
            iotox::local::payload_text(confirmed.value().payload);
        IOTOX_CHECK(confirmed_text.find("phase=confirmed") !=
                    std::string::npos);
        IOTOX_CHECK(confirmed_text.find("confirmed-sequence=1") !=
                    std::string::npos);

        std::vector<std::uint8_t> publish_payload;
        publish_payload.push_back(
            static_cast<std::uint8_t>(namespace_policy.id.size()));
        publish_payload.insert(publish_payload.end(), namespace_policy.id.begin(),
                               namespace_policy.id.end());
        const std::string bundle2_native = bundle2_path.string();
        publish_payload.insert(publish_payload.end(), bundle2_native.begin(),
                               bundle2_native.end());
        auto published = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::sync_publish, 486U,
                    publish_payload));
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
        IOTOX_CHECK_MSG(
            published.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(published.value().payload));

        iotox::sync::SignedHeadStore published_heads(namespace_root);
        auto signed_head = published_heads.load(namespace_policy,
                                                sodium.value());
        IOTOX_CHECK_MSG(signed_head.ok(), signed_head.status().message());
        IOTOX_CHECK(signed_head.value().has_value());
        IOTOX_CHECK(signed_head.value()->generation == 2U);
        auto candidate = iotox::sync::verified_candidate_head(
            namespace_policy, *signed_head.value(), sodium.value());
        IOTOX_CHECK_MSG(candidate.ok(), candidate.status().message());
        iotox::sync::AcceptedHeadStore accepted_heads(namespace_root);
        auto accepted = accepted_heads.accept(
            namespace_policy, candidate.value(), identity.value(),
            sodium.value());
        IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
        IOTOX_CHECK(accepted.value().accepted());

        std::vector<std::uint8_t> stage_payload;
        stage_payload.push_back(
            static_cast<std::uint8_t>(namespace_policy.id.size()));
        stage_payload.insert(stage_payload.end(), namespace_policy.id.begin(),
                             namespace_policy.id.end());
        stage_payload.insert(stage_payload.end(), candidate.value().record.begin(),
                             candidate.value().record.end());
        auto staged = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_stage, 487U,
                    stage_payload));
        IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
        IOTOX_CHECK_MSG(
            staged.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(staged.value().payload));
        IOTOX_CHECK(iotox::local::payload_text(staged.value().payload).find(
                        "candidate-sequence=2") != std::string::npos);

        auto applied = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(
                iotox::local::ControlOperation::update_apply, 488U,
                std::vector<std::uint8_t>(
                    bundle2.value().manifest_record.begin(),
                    bundle2.value().manifest_record.end())));
        IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
        IOTOX_CHECK_MSG(
            applied.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(applied.value().payload));
        IOTOX_CHECK(iotox::local::payload_text(applied.value().payload).find(
                        "candidate-sequence=2") != std::string::npos);
        restarted.stop();
    }

    config.runtime.root = directory / "run-third";
    {
        iotox::Agent unhealthy(config);
        const iotox::Status started = unhealthy.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        auto pending = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_status, 489U));
        IOTOX_CHECK_MSG(pending.ok(), pending.status().message());
        const std::string pending_text =
            iotox::local::payload_text(pending.value().payload);
        IOTOX_CHECK(pending_text.find("startup=health-window-opened") !=
                    std::string::npos);
        IOTOX_CHECK(pending_text.find("phase=awaiting-health") !=
                    std::string::npos);
        IOTOX_CHECK(pending_text.find("candidate-sequence=2") !=
                    std::string::npos);

        std::string expired_text;
        for (std::uint64_t attempt = 0U; attempt < 100U; ++attempt) {
            auto status = iotox::local::control_request(
                config.runtime.root / "control.sock",
                request(iotox::local::ControlOperation::update_status,
                        490U + attempt));
            IOTOX_CHECK_MSG(status.ok(), status.status().message());
            IOTOX_CHECK_MSG(
                status.value().status == iotox::ErrorCode::ok,
                iotox::local::payload_text(status.value().payload));
            expired_text =
                iotox::local::payload_text(status.value().payload);
            if (expired_text.find("phase=confirmed") !=
                std::string::npos) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        IOTOX_CHECK(expired_text.find("phase=confirmed") !=
                    std::string::npos);
        IOTOX_CHECK(expired_text.find("rollback-count=1") !=
                    std::string::npos);
        IOTOX_CHECK(expired_text.find("confirmed-sequence=1") !=
                    std::string::npos);
        IOTOX_CHECK(expired_text.find("candidate-sequence=0") !=
                    std::string::npos);
        IOTOX_CHECK(expired_text.find("last-failed-sequence=2") !=
                    std::string::npos);
        unhealthy.stop();
    }

    config.runtime.root = directory / "run-fourth";
    {
        iotox::Agent rolled_back(config);
        const iotox::Status started = rolled_back.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        auto status = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_status, 600U));
        IOTOX_CHECK_MSG(status.ok(), status.status().message());
        const std::string status_text =
            iotox::local::payload_text(status.value().payload);
        IOTOX_CHECK(status_text.find("startup=unchanged") !=
                    std::string::npos);
        IOTOX_CHECK(status_text.find("phase=confirmed") !=
                    std::string::npos);
        IOTOX_CHECK(status_text.find("rollback-count=1") !=
                    std::string::npos);
        IOTOX_CHECK(status_text.find("confirmed-sequence=1") !=
                    std::string::npos);
        IOTOX_CHECK(status_text.find("candidate-sequence=0") !=
                    std::string::npos);
        IOTOX_CHECK(status_text.find("last-failed-sequence=2") !=
                    std::string::npos);
        auto planned = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_gc, 601U,
                    std::vector<std::uint8_t>{0U}));
        IOTOX_CHECK_MSG(planned.ok(), planned.status().message());
        IOTOX_CHECK_MSG(
            planned.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(planned.value().payload));
        const std::string planned_text =
            iotox::local::payload_text(planned.value().payload);
        IOTOX_CHECK(planned_text.find("mode=dry-run") == 0U);
        IOTOX_CHECK(planned_text.find("active-slots=2") !=
                    std::string::npos);
        IOTOX_CHECK(planned_text.find("protected-slots=1") !=
                    std::string::npos);
        IOTOX_CHECK(planned_text.find("eligible-slots=1") !=
                    std::string::npos);
        IOTOX_CHECK(planned_text.find("quarantined-slots=0") !=
                    std::string::npos);
        IOTOX_CHECK(planned_text.find("purge=absent") !=
                    std::string::npos);
        auto quarantined = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(iotox::local::ControlOperation::update_gc, 602U,
                    std::vector<std::uint8_t>{1U}));
        IOTOX_CHECK_MSG(quarantined.ok(), quarantined.status().message());
        IOTOX_CHECK_MSG(
            quarantined.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(quarantined.value().payload));
        const std::string quarantined_text =
            iotox::local::payload_text(quarantined.value().payload);
        IOTOX_CHECK(quarantined_text.find("mode=quarantine") == 0U);
        IOTOX_CHECK(quarantined_text.find("quarantined-slots=1") !=
                    std::string::npos);
        IOTOX_CHECK(quarantined_text.find("prior-quarantine-slots=0") !=
                    std::string::npos);
        rolled_back.stop();
    }
    IOTOX_CHECK(read_text(update_root / "current") == payload_bytes);
    IOTOX_CHECK(std::distance(
                    std::filesystem::directory_iterator(update_root / "slots"),
                    std::filesystem::directory_iterator{}) == 1);
    IOTOX_CHECK(std::distance(
                    std::filesystem::directory_iterator(
                        update_root / "quarantine"),
                    std::filesystem::directory_iterator{}) == 1);
    iotox::security::secure_wipe(health_token);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent gates linux service confirmation and recovers failed candidate") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path update_root = directory / "update-root";
    const std::filesystem::path update_policy_path =
        directory / "update.policy";
    const std::filesystem::path service_payload =
        directory / "service.elf";
    const std::filesystem::path bundle1_path =
        directory / "service-1.iub";
    const std::filesystem::path bundle2_path =
        directory / "service-2.iub";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(std::filesystem::create_directory(update_root));
    for (const auto &path : {
             directory, state, policy_root,
             policy_root / "namespaces", namespace_root, update_root}) {
        IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0700)) == 0);
    }

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.security.protocol_incarnation_state_path =
        state / "protocol.incarnation";
    initialize_mock_v1_authority(config);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, sodium.value());
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    auto release =
        iotox::security::DeviceIdentity::create_new_release(
            state / "release.identity", sodium.value());
    IOTOX_CHECK_MSG(release.ok(), release.status().message());

    iotox::sync::NamespacePolicy namespace_policy;
    namespace_policy.id = "service-image";
    namespace_policy.root = namespace_root.lexically_normal().string();
    namespace_policy.engine = iotox::sync::Engine::range_v1;
    namespace_policy.activation = iotox::sync::ActivationMode::manual;
    namespace_policy.writers = {identity.value().public_key()};
    namespace_policy.quotas.maximum_artifact_bytes = 256U * 1024U * 1024U;
    namespace_policy.quotas.maximum_manifest_bytes = 64U * 1024U;
    namespace_policy.quotas.maximum_store_bytes = 512U * 1024U * 1024U;
    namespace_policy.quotas.maximum_staging_bytes = 256U * 1024U * 1024U;
    auto namespace_record =
        iotox::sync::encode_namespace_policy(namespace_policy);
    IOTOX_CHECK_MSG(namespace_record.ok(),
                    namespace_record.status().message());
    write_private_record(
        policy_root / "namespaces" / "service-image.namespace",
        namespace_record.value());

    iotox::update::UpdatePolicy update_policy;
    update_policy.namespace_id = namespace_policy.id;
    update_policy.target = "iotox-test-linux-service-x86_64";
    update_policy.root = update_root;
    update_policy.maximum_payload_bytes = 256U * 1024U * 1024U;
    update_policy.health_timeout_ms = 5000U;
    update_policy.signer_policy_epoch = 1U;
    update_policy.payload_kind =
        iotox::update::PayloadKind::linux_service_v1;
    update_policy.trusted_signers = {release.value().public_key()};
    auto update_policy_bytes =
        iotox::update::encode_update_policy(update_policy);
    IOTOX_CHECK_MSG(update_policy_bytes.ok(),
                    update_policy_bytes.status().message());
    write_private_record(update_policy_path, update_policy_bytes.value());

    std::filesystem::copy_file(
        update_service_fixture(), service_payload,
        std::filesystem::copy_options::none);
    IOTOX_CHECK(::chmod(service_payload.c_str(), 0600) == 0);
    auto bundle1 = iotox::update::create_signed_update_bundle(
        update_policy, service_payload, bundle1_path, 1U,
        "delayed-ready", release.value(), sodium.value());
    IOTOX_CHECK_MSG(bundle1.ok(), bundle1.status().message());
    auto bundle2 = iotox::update::create_signed_update_bundle(
        update_policy, service_payload, bundle2_path, 2U,
        "exit-before-ready", release.value(), sodium.value());
    IOTOX_CHECK_MSG(bundle2.ok(), bundle2.status().message());

    auto first_lease =
        iotox::interactive::RatoxIncarnationLease::acquire(
            config.security.protocol_incarnation_state_path,
            identity.value(), sodium.value());
    IOTOX_CHECK_MSG(first_lease.ok(), first_lease.status().message());
    const std::uint64_t first_incarnation =
        first_lease.value().incarnation();
    auto initial_store = iotox::update::UpdateStore::open(
        update_policy, identity.value(), sodium.value(),
        first_incarnation);
    IOTOX_CHECK_MSG(initial_store.ok(), initial_store.status().message());
    auto staged1 = initial_store.value()->stage(bundle1_path);
    IOTOX_CHECK_MSG(staged1.ok(), staged1.status().message());
    auto applied1 = initial_store.value()->apply(
        staged1.value().state.candidate.manifest_record,
        first_incarnation);
    IOTOX_CHECK_MSG(applied1.ok(), applied1.status().message());
    const iotox::update::HealthToken token1 =
        applied1.value().health_token;
    initial_store.value().reset();
    first_lease.value().reset();

    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    config.update.enabled = true;
    config.update.policy_path = update_policy_path;
    config.update.linux_service_enabled = true;
    config.update.service_helper_executable = self_test_executable();
    config.update.service_helper_startup_timeout =
        std::chrono::seconds(3);
    config.update.service_shutdown_timeout =
        std::chrono::seconds(1);
    config.runtime.root = directory / "run-candidate";
    {
        iotox::Agent candidate(config);
        const iotox::Status started = candidate.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        auto premature = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(
                iotox::local::ControlOperation::update_confirm, 700U,
                std::vector<std::uint8_t>(
                    token1.begin(), token1.end())));
        IOTOX_CHECK_MSG(premature.ok(), premature.status().message());
        IOTOX_CHECK(
            premature.value().status == iotox::ErrorCode::unavailable);

        std::string ready_text;
        for (std::uint64_t attempt = 0U; attempt < 100U; ++attempt) {
            auto status = iotox::local::control_request(
                config.runtime.root / "control.sock",
                request(iotox::local::ControlOperation::update_status,
                        701U + attempt));
            IOTOX_CHECK_MSG(status.ok(), status.status().message());
            ready_text =
                iotox::local::payload_text(status.value().payload);
            if (ready_text.find("service-phase=ready") !=
                std::string::npos) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        IOTOX_CHECK(ready_text.find("phase=awaiting-health") !=
                    std::string::npos);
        IOTOX_CHECK(ready_text.find("payload-kind=linux-service-v1") !=
                    std::string::npos);
        IOTOX_CHECK(ready_text.find("service-phase=ready") !=
                    std::string::npos);
        IOTOX_CHECK(ready_text.find("service-sequence=1") !=
                    std::string::npos);
        IOTOX_CHECK(ready_text.find("service-candidate=1") !=
                    std::string::npos);
        IOTOX_CHECK(ready_text.find("service-image-sealed=1") !=
                    std::string::npos);

        auto confirmed = iotox::local::control_request(
            config.runtime.root / "control.sock",
            request(
                iotox::local::ControlOperation::update_confirm, 802U,
                std::vector<std::uint8_t>(
                    token1.begin(), token1.end())));
        IOTOX_CHECK_MSG(confirmed.ok(), confirmed.status().message());
        IOTOX_CHECK_MSG(
            confirmed.value().status == iotox::ErrorCode::ok,
            iotox::local::payload_text(confirmed.value().payload));
        const std::string confirmed_text =
            iotox::local::payload_text(confirmed.value().payload);
        IOTOX_CHECK(confirmed_text.find("phase=confirmed") !=
                    std::string::npos);
        IOTOX_CHECK(confirmed_text.find("service-candidate=0") !=
                    std::string::npos);
        candidate.stop();
    }

    auto second_lease =
        iotox::interactive::RatoxIncarnationLease::acquire(
            config.security.protocol_incarnation_state_path,
            identity.value(), sodium.value());
    IOTOX_CHECK_MSG(second_lease.ok(), second_lease.status().message());
    const std::uint64_t second_incarnation =
        second_lease.value().incarnation();
    auto second_store = iotox::update::UpdateStore::open(
        update_policy, identity.value(), sodium.value(),
        second_incarnation);
    IOTOX_CHECK_MSG(second_store.ok(), second_store.status().message());
    auto staged2 = second_store.value()->stage(bundle2_path);
    IOTOX_CHECK_MSG(staged2.ok(), staged2.status().message());
    auto applied2 = second_store.value()->apply(
        staged2.value().state.candidate.manifest_record,
        second_incarnation);
    IOTOX_CHECK_MSG(applied2.ok(), applied2.status().message());
    second_store.value().reset();
    second_lease.value().reset();

    config.runtime.root = directory / "run-failed-candidate";
    {
        iotox::Agent recovered(config);
        const iotox::Status started = recovered.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        std::string recovered_text;
        for (std::uint64_t attempt = 0U; attempt < 140U; ++attempt) {
            auto status = iotox::local::control_request(
                config.runtime.root / "control.sock",
                request(iotox::local::ControlOperation::update_status,
                        900U + attempt));
            IOTOX_CHECK_MSG(status.ok(), status.status().message());
            recovered_text =
                iotox::local::payload_text(status.value().payload);
            if (recovered_text.find("phase=confirmed") !=
                    std::string::npos &&
                recovered_text.find("service-phase=ready") !=
                    std::string::npos) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        IOTOX_CHECK(recovered_text.find("phase=confirmed") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("rollback-count=1") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("confirmed-sequence=1") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("candidate-sequence=0") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("last-failed-sequence=2") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("service-sequence=1") !=
                    std::string::npos);
        IOTOX_CHECK(recovered_text.find("service-candidate=0") !=
                    std::string::npos);
        recovered.stop();
    }
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent publishes and atomically activates one deterministic tree") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path source = directory / "source-tree";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(std::filesystem::create_directory(source));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(state.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((policy_root / "namespaces").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(namespace_root.c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(source.c_str(), static_cast<mode_t>(0700)) == 0);
    make_private_directory(source / "bin");
    make_private_directory(source / "empty");
    const std::string notes = "deterministic tree notes\n";
    write_private_record(
        source / "notes.txt",
        std::vector<std::uint8_t>(notes.begin(), notes.end()));
    const std::string probe = "#!/bin/sh\nexit 0\n";
    write_private_record(
        source / "bin" / "probe",
        std::vector<std::uint8_t>(probe.begin(), probe.end()));
    IOTOX_CHECK(::chmod((source / "bin" / "probe").c_str(),
                        static_cast<mode_t>(0700)) == 0);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const std::filesystem::path identity_path = state / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::sync::NamespacePolicy policy;
    policy.id = "site-tree";
    policy.root = namespace_root.lexically_normal().string();
    policy.engine = iotox::sync::Engine::treepack_v1;
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {identity.value().public_key()};
    policy.quotas.maximum_artifact_bytes = 64U * 1024U;
    policy.quotas.maximum_manifest_bytes = 64U * 1024U;
    policy.quotas.maximum_store_bytes = 4U * 1024U * 1024U;
    policy.quotas.maximum_staging_bytes = 1024U * 1024U;
    policy.quotas.maximum_objects = 64U;
    auto encoded_policy = iotox::sync::encode_namespace_policy(policy);
    IOTOX_CHECK_MSG(encoded_policy.ok(), encoded_policy.status().message());
    write_private_record(
        policy_root / "namespaces" / "site-tree.namespace",
        encoded_policy.value());

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = state / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.security.device_identity_path = identity_path;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> publish_payload;
    publish_payload.push_back(static_cast<std::uint8_t>(policy.id.size()));
    publish_payload.insert(publish_payload.end(), policy.id.begin(),
                           policy.id.end());
    const std::string source_path = source.string();
    publish_payload.insert(publish_payload.end(), source_path.begin(),
                           source_path.end());
    auto published = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_publish, 470U,
                publish_payload));
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK_MSG(
        published.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(published.value().payload));
    const std::string publication =
        iotox::local::payload_text(published.value().payload);
    IOTOX_CHECK(publication.find("generation=1") != std::string::npos);
    IOTOX_CHECK(publication.find("kind=treepack") != std::string::npos);
    IOTOX_CHECK(publication.find("directories=2") != std::string::npos);
    IOTOX_CHECK(publication.find("files=2") != std::string::npos);

    iotox::sync::SignedHeadStore head_store(namespace_root);
    auto signed_head = head_store.load(policy, sodium.value());
    IOTOX_CHECK_MSG(signed_head.ok(), signed_head.status().message());
    IOTOX_CHECK(signed_head.value().has_value());
    auto candidate = iotox::sync::verified_candidate_head(
        policy, *signed_head.value(), sodium.value());
    IOTOX_CHECK_MSG(candidate.ok(), candidate.status().message());
    iotox::sync::AcceptedHeadStore accepted_store(namespace_root);
    auto accepted = accepted_store.accept(
        policy, candidate.value(), identity.value(), sodium.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().accepted());

    std::vector<std::uint8_t> activate_payload;
    activate_payload.push_back(static_cast<std::uint8_t>(policy.id.size()));
    activate_payload.insert(activate_payload.end(), policy.id.begin(),
                            policy.id.end());
    activate_payload.insert(activate_payload.end(),
                            candidate.value().record.begin(),
                            candidate.value().record.end());
    auto activated = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_activate, 471U,
                activate_payload));
    IOTOX_CHECK_MSG(activated.ok(), activated.status().message());
    IOTOX_CHECK_MSG(
        activated.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(activated.value().payload));
    const std::string activation =
        iotox::local::payload_text(activated.value().payload);
    IOTOX_CHECK(activation.find("decision=activated") != std::string::npos);
    IOTOX_CHECK(activation.find("kind=treepack") != std::string::npos);
    IOTOX_CHECK(activation.find("materialized=1") != std::string::npos);
    const auto current = namespace_root / "materialized-trees" / "current";
    IOTOX_CHECK(read_text(current / "notes.txt") == notes);
    struct stat mode {};
    IOTOX_CHECK(::lstat((current / "bin" / "probe").c_str(), &mode) == 0);
    IOTOX_CHECK((mode.st_mode & static_cast<mode_t>(0777)) ==
                static_cast<mode_t>(0500));

    auto duplicate = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_activate, 472U,
                activate_payload));
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK_MSG(
        duplicate.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(duplicate.value().payload));
    const std::string retry =
        iotox::local::payload_text(duplicate.value().payload);
    IOTOX_CHECK(retry.find("decision=duplicate") != std::string::npos);
    IOTOX_CHECK(retry.find("already-current=1") != std::string::npos);

    agent.stop();
    try {
        for (std::filesystem::recursive_directory_iterator iterator(
                 namespace_root / "materialized-trees"), end;
             iterator != end; ++iterator) {
            if (iterator->is_directory(ignored)) {
                IOTOX_CHECK(::chmod(iterator->path().c_str(),
                                    static_cast<mode_t>(0700)) == 0);
            }
            ignored.clear();
        }
    } catch (const std::filesystem::filesystem_error &error) {
        IOTOX_CHECK_MSG(false, error.what());
    }
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(!ignored);
}

void run_agent_signed_mock_revision_route_loss(bool fail_closed) {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path artifact_source = directory / "artifact.in";
    const std::filesystem::path manifest_source = directory / "manifest.in";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(
        (policy_root / "namespaces").c_str(),
        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(
        namespace_root.c_str(), static_cast<mode_t>(0700)) == 0);
    const std::string artifact_bytes = "mock-sync-artifact-v1";
    write_private_record(
        artifact_source,
        std::vector<std::uint8_t>(
            artifact_bytes.begin(), artifact_bytes.end()));

    iotox::sync::NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = namespace_root.lexically_normal().string();
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {mock_authority_principal()};
    policy.quotas.maximum_artifact_bytes = 4096U;
    policy.quotas.maximum_manifest_bytes = 4096U;
    policy.quotas.maximum_store_bytes = 16384U;
    policy.quotas.maximum_staging_bytes = 8192U;
    policy.quotas.maximum_outstanding_requests = 4U;
    auto built_manifest = iotox::sync::build_sync_range_manifest(
        policy, artifact_source, manifest_source);
    IOTOX_CHECK_MSG(built_manifest.ok(),
                    built_manifest.status().message());
    const std::string manifest_bytes = read_text(manifest_source);
    auto policy_record = iotox::sync::encode_namespace_policy(policy);
    IOTOX_CHECK_MSG(policy_record.ok(), policy_record.status().message());
    write_private_record(
        policy_root / "namespaces" / "field-notes.namespace",
        policy_record.value());

    ScopedEnvironment mock_namespace(
        "IOTOX_MOCK_SYNC_NAMESPACE", policy.id.c_str());
    const std::string artifact_path = artifact_source.string();
    const std::string manifest_path = manifest_source.string();
    ScopedEnvironment mock_artifact(
        "IOTOX_MOCK_SYNC_ARTIFACT", artifact_path.c_str());
    ScopedEnvironment mock_manifest(
        "IOTOX_MOCK_SYNC_MANIFEST", manifest_path.c_str());
    const std::string route_audit_path =
        (directory / "sync-route-audit.log").string();
    ScopedEnvironment mock_route_audit(
        "IOTOX_MOCK_AUTHORITY_AUDIT", route_audit_path.c_str());
    ScopedEnvironment mock_route_loss(
        "IOTOX_MOCK_SYNC_DISCONNECT_SELF_FIRST_BYTE", "67");
    ScopedEnvironment mock_route_loss_after_bytes(
        "IOTOX_MOCK_SYNC_DISCONNECT_AFTER_FILE_BYTES", "3");

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    config.sync.route_selection_policy =
        iotox::sync::SyncRouteSelectionPolicy::adaptive;
    // Deliberately configure the opposite process default. The versioned
    // local request below must freeze its own policy on the pull.
    config.sync.route_failover_policy =
        fail_closed
            ? iotox::sync::SyncRouteFailoverPolicy::available
            : iotox::sync::SyncRouteFailoverPolicy::fail_closed;
    initialize_mock_v3_sync_authority(config);

    config.security.route_set_path =
        directory / "state" / "routes.signed";
    config.security.route_generation_state_path =
        directory / "state" / "routes.generation";
    config.security.route_workers_enabled = true;
    config.security.route_worker_state_root =
        directory / "route-workers";
    make_private_directory(config.security.route_worker_state_root);

    iotox::ToxTransport::Config primary_config = config.transport;
    primary_config.save_state_on_stop = true;
    iotox::ToxTransport primary(primary_config);
    IOTOX_CHECK(primary.start().ok());
    IOTOX_CHECK(primary.accept_friend(
                    std::vector<std::uint8_t>(32U, 0x42U)).ok());
    primary.stop();

    const auto decode_hex_nibble = [](char value) -> std::uint8_t {
        if (value <= '9') {
            return static_cast<std::uint8_t>(value - '0');
        }
        return static_cast<std::uint8_t>(value - 'A' + 10);
    };
    const auto provision_auxiliary =
        [&](std::uint8_t identity_mask, std::string_view label) {
            const auto provisional =
                config.security.route_worker_state_root /
                (std::string(label) + ".toxsave");
            iotox::ToxTransport::Config auxiliary_config = config.transport;
            auxiliary_config.state_path = provisional;
            auxiliary_config.save_state_on_stop = true;
            iotox::ToxTransport auxiliary(auxiliary_config);
            IOTOX_CHECK(auxiliary.start().ok());
            IOTOX_CHECK(auxiliary.accept_friend(
                            std::vector<std::uint8_t>(32U, 0x43U)).ok());
            const std::string auxiliary_address = auxiliary.address_hex();
            auxiliary.stop();
            auto auxiliary_savedata = iotox::StateStore::read(provisional);
            IOTOX_CHECK(auxiliary_savedata.ok());
            IOTOX_CHECK(auxiliary_savedata.value().size() > 4U);
            auxiliary_savedata.value()[4U] ^= identity_mask;
            write_private_record(provisional, auxiliary_savedata.value());

            iotox::routes::ToxPublicKey auxiliary_key{};
            for (std::size_t index = 0U;
                 index < auxiliary_key.size(); ++index) {
                auxiliary_key[index] = static_cast<std::uint8_t>(
                    (decode_hex_nibble(
                         auxiliary_address[index * 2U]) << 4U) |
                    decode_hex_nibble(
                        auxiliary_address[index * 2U + 1U]));
            }
            auxiliary_key[0U] ^= identity_mask;
            std::filesystem::rename(
                provisional,
                iotox::routes::WorkerSupervisor::state_path_for(
                    config.security.route_worker_state_root,
                    auxiliary_key));
            return auxiliary_key;
        };
    const iotox::routes::ToxPublicKey first_auxiliary_key =
        provision_auxiliary(0x40U, "sync-bulk-a");
    const iotox::routes::ToxPublicKey second_auxiliary_key =
        provision_auxiliary(0x80U, "sync-bulk-b");

    auto route_sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(route_sodium.ok(), route_sodium.status().message());
    auto route_identity = iotox::security::DeviceIdentity::load(
        config.security.device_identity_path, route_sodium.value());
    IOTOX_CHECK_MSG(route_identity.ok(), route_identity.status().message());
    iotox::routes::ToxPublicKey coordinator_key{};
    for (std::size_t index = 0U; index < coordinator_key.size(); ++index) {
        coordinator_key[index] =
            static_cast<std::uint8_t>((index * 7U + 3U) & 0xFFU);
    }
    iotox::routes::RouteSet route_set;
    route_set.generation = 5U;
    route_set.stable_device_principal =
        route_identity.value().public_key();
    route_set.coordinator_tox_public_key = coordinator_key;
    route_set.members = {
        {coordinator_key, iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {first_auxiliary_key, iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 1U, 0U},
        {second_auxiliary_key, iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 1U, 0U},
    };
    auto signed_routes =
        iotox::routes::sign_route_set(route_set, route_identity.value());
    IOTOX_CHECK_MSG(signed_routes.ok(), signed_routes.status().message());
    write_private_record(
        config.security.route_set_path, signed_routes.value());

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    std::string route_status;
    const auto route_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    std::uint64_t request_id = 461U;
    while (std::chrono::steady_clock::now() < route_deadline) {
        auto routes = iotox::local::control_request(
            runtime / "control.sock",
            request(
                iotox::local::ControlOperation::route_inventory_show,
                request_id++));
        IOTOX_CHECK_MSG(routes.ok(), routes.status().message());
        IOTOX_CHECK(routes.value().status == iotox::ErrorCode::ok);
        route_status =
            iotox::local::payload_text(routes.value().payload);
        if (count_occurrences(route_status, "role=bulk") == 2U &&
            count_occurrences(route_status, "lifecycle=ready") >= 2U) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(
        count_occurrences(route_status, "role=bulk") == 2U &&
            count_occurrences(route_status, "lifecycle=ready") >= 2U,
        route_status);

    bool pull_queued = false;
    const std::string runtime_text = runtime.string();
    const std::string failover_text =
        fail_closed ? "fail-closed" : "available";
    const std::vector<std::string_view> pull_arguments{
        "--runtime", runtime_text, "sync-pull", "0", policy.id,
        failover_text, "tox/native"};
    std::string pull_output;
    const auto authority_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < authority_deadline) {
        std::ostringstream output;
        std::ostringstream errors;
        std::streambuf *prior_output = std::cout.rdbuf(output.rdbuf());
        std::streambuf *prior_errors = std::cerr.rdbuf(errors.rdbuf());
        const int exit_code = iotox::run_cli(pull_arguments);
        std::cout.rdbuf(prior_output);
        std::cerr.rdbuf(prior_errors);
        pull_output = output.str() + errors.str();
        if (exit_code == 0) {
            pull_queued = true;
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(
        pull_queued,
        "CLI sync pull never passed exact v3 authority: " + pull_output);

    std::string sync_status;
    const auto completion_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < completion_deadline) {
        auto status = iotox::local::control_request(
            runtime / "control.sock",
            request(
                iotox::local::ControlOperation::sync_status,
                request_id++));
        IOTOX_CHECK_MSG(status.ok(), status.status().message());
        IOTOX_CHECK(status.value().status == iotox::ErrorCode::ok);
        sync_status = iotox::local::payload_text(status.value().payload);
        if ((!fail_closed &&
             (sync_status.find("state=complete") != std::string::npos ||
              sync_status.find("state=failed") != std::string::npos)) ||
            (fail_closed &&
             sync_status.find("auxiliary-carrier-losses=1") !=
                 std::string::npos &&
             sync_status.find("auxiliary-fail-closed-jobs=1") !=
                 std::string::npos)) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(sync_status.find("qualification-deferred-frames=0") !=
                std::string::npos);
    IOTOX_CHECK(
        sync_status.find("qualification-deferred-frame-releases=0") !=
        std::string::npos);
    if (fail_closed) {
        IOTOX_CHECK_MSG(
            sync_status.find("state=awaiting-objects") != std::string::npos,
            sync_status);
        IOTOX_CHECK(sync_status.find("auxiliary-reassignments=0") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("auxiliary-failover-policy=available") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("failover=fail-closed") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("route-class=tox/native") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("auxiliary-fail-closed-jobs=1") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("auxiliary-adaptive-selections=1") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("retained-partials=0") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("retained-attempts=0") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("retained-bytes=0") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("retention-fallbacks=0") !=
                    std::string::npos);
        IOTOX_CHECK(sync_status.find("resumed-attempts=0") !=
                    std::string::npos);
        IOTOX_CHECK(
            sync_status.find(
                "carrier-route=" +
                iotox::security::hex(first_auxiliary_key)) !=
            std::string::npos);
        IOTOX_CHECK(
            read_text(route_audit_path)
                .find("sync-forced-disconnect self-first-byte=67 friend=0 "
                      "after-file-bytes=3") != std::string::npos);
        agent.stop();
        std::filesystem::remove_all(directory, ignored);
        IOTOX_CHECK(!ignored);
        return;
    }
    IOTOX_CHECK_MSG(
        sync_status.find("state=complete") != std::string::npos,
        sync_status);
    IOTOX_CHECK(sync_status.find("committed=2") != std::string::npos);
    IOTOX_CHECK(sync_status.find("scheduler-attempts=") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("scheduler-attempt-bound=4") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-route-policy=adaptive") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-failover-policy=fail-closed") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("failover=available") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("route-class=tox/native") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-fail-closed-jobs=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-ready-routes=1") !=
                std::string::npos);
    IOTOX_CHECK(
        sync_status.find(
            "auxiliary-route=" +
            iotox::security::hex(second_auxiliary_key) +
            " worker=") != std::string::npos);
    IOTOX_CHECK(
        sync_status.find(
            " principal=" +
            iotox::security::hex(mock_authority_principal()) +
            " admitted-work=0 maximum-work=8") !=
        std::string::npos);
    IOTOX_CHECK(sync_status.find(" range-negotiated=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-fixed-selections=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("auxiliary-adaptive-selections=2") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("not activated") != std::string::npos);
    IOTOX_CHECK(sync_status.find("carrier=auxiliary") != std::string::npos);
    IOTOX_CHECK(sync_status.find("carrier-worker=0") == std::string::npos);
    IOTOX_CHECK(
        sync_status.find(
            "carrier-active-receives=0 carrier-receive-position=0 "
            "carrier-receive-bytes=0") != std::string::npos);
    IOTOX_CHECK(
        sync_status.find(
            "carrier-route=" +
            iotox::security::hex(second_auxiliary_key)) !=
        std::string::npos);
    iotox::routes::ToxPublicKey remote_coordinator_key{};
    remote_coordinator_key.fill(0x42U);
    IOTOX_CHECK(
        sync_status.find(
            "carrier-coordinator=" +
            iotox::security::hex(remote_coordinator_key)) !=
        std::string::npos);
    IOTOX_CHECK(sync_status.find("carrier-primary-epoch=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("retained-partials=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("retained-attempts=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("retained-bytes=3") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("retention-fallbacks=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("resumed-attempts=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("resumed-bytes=3") !=
                std::string::npos);
    IOTOX_CHECK(read_text(route_audit_path)
                    .find("sync-forced-disconnect self-first-byte=67 friend=0 "
                          "after-file-bytes=3") != std::string::npos);

    const std::string record_token = " head-record=";
    const std::size_t record_offset = sync_status.find(record_token);
    IOTOX_CHECK(record_offset != std::string::npos);
    const std::string record_hex = sync_status.substr(
        record_offset + record_token.size(), 64U);
    auto record = iotox::security::decode_hex_exact(
        record_hex, 32U, "sync HEAD record");
    IOTOX_CHECK_MSG(record.ok(), record.status().message());
    std::vector<std::uint8_t> activate_payload;
    activate_payload.push_back(
        static_cast<std::uint8_t>(policy.id.size()));
    activate_payload.insert(activate_payload.end(), policy.id.begin(),
                            policy.id.end());
    activate_payload.insert(activate_payload.end(), record.value().begin(),
                            record.value().end());
    auto activated = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::sync_activate,
                request_id++, std::move(activate_payload)));
    IOTOX_CHECK_MSG(activated.ok(), activated.status().message());
    IOTOX_CHECK_MSG(
        activated.value().status == iotox::ErrorCode::ok,
        iotox::local::payload_text(activated.value().payload));
    IOTOX_CHECK(iotox::local::payload_text(
        activated.value().payload).find("decision=activated") !=
        std::string::npos);

    agent.stop();
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto local_identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), false);
    IOTOX_CHECK_MSG(local_identity.ok(), local_identity.status().message());
    iotox::sync::AcceptedHeadStore accepted(namespace_root);
    auto head = accepted.load(
        policy, local_identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(head.ok(), head.status().message());
    IOTOX_CHECK(head.value().has_value());
    IOTOX_CHECK(head.value()->writer == mock_authority_principal());
    IOTOX_CHECK(std::filesystem::exists(
        namespace_root / "activated-revisions" /
            "field-notes.activated-revision"));
    const auto artifact_digest =
        iotox::sync::hash_sync_file_sha256(artifact_source);
    const auto manifest_digest =
        iotox::sync::hash_sync_file_sha256(manifest_source);
    IOTOX_CHECK(artifact_digest.ok() && manifest_digest.ok());
    IOTOX_CHECK(read_text(iotox::sync::sync_object_path(
        policy, {iotox::sync::SyncObjectKind::artifact,
                 artifact_digest.value(),
                 static_cast<std::uint64_t>(artifact_bytes.size())})) ==
        artifact_bytes);
    IOTOX_CHECK(read_text(iotox::sync::sync_object_path(
        policy, {iotox::sync::SyncObjectKind::manifest,
                 manifest_digest.value(),
                 static_cast<std::uint64_t>(manifest_bytes.size())})) ==
        manifest_bytes);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent converges a signed mock revision through real control and "
           "file events") {
    run_agent_signed_mock_revision_route_loss(false);
}

IOTOX_TEST(
    "agent fail-closed route loss never selects an available replacement") {
    run_agent_signed_mock_revision_route_loss(true);
}

IOTOX_TEST(
    "agent reconstructs a signed successor from one negotiated range bundle") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path policy_root = directory / "sync-policy";
    const std::filesystem::path namespace_root = directory / "namespace";
    const std::filesystem::path basis_source = directory / "basis.in";
    const std::filesystem::path target_source = directory / "target.in";
    const std::filesystem::path basis_manifest_source =
        directory / "basis.index";
    const std::filesystem::path target_manifest_source =
        directory / "target.index";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(
        policy_root / "namespaces"));
    IOTOX_CHECK(std::filesystem::create_directory(namespace_root));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(policy_root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(
        (policy_root / "namespaces").c_str(),
        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(
        namespace_root.c_str(), static_cast<mode_t>(0700)) == 0);

    std::vector<std::uint8_t> basis_bytes(16384U, 0U);
    for (std::size_t index = 0U; index < basis_bytes.size(); ++index) {
        basis_bytes[index] = static_cast<std::uint8_t>(
            (index * 29U + index / 31U + (index / 4096U) * 17U) &
            0xffU);
    }
    std::vector<std::uint8_t> target_bytes = basis_bytes;
    std::fill(target_bytes.begin() + 4096, target_bytes.begin() + 8192,
              static_cast<std::uint8_t>(0x5AU));
    write_private_record(basis_source, basis_bytes);
    write_private_record(target_source, target_bytes);

    iotox::sync::NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = namespace_root.lexically_normal().string();
    policy.activation = iotox::sync::ActivationMode::manual;
    policy.writers = {mock_authority_principal()};
    policy.quotas.maximum_artifact_bytes = 32768U;
    policy.quotas.maximum_manifest_bytes = 4096U;
    policy.quotas.maximum_store_bytes = 131072U;
    policy.quotas.maximum_staging_bytes = 65536U;
    policy.quotas.maximum_outstanding_requests = 8U;
    auto basis_manifest = iotox::sync::build_sync_range_manifest(
        policy, basis_source, basis_manifest_source);
    auto target_manifest = iotox::sync::build_sync_range_manifest(
        policy, target_source, target_manifest_source);
    IOTOX_CHECK_MSG(basis_manifest.ok(),
                    basis_manifest.status().message());
    IOTOX_CHECK_MSG(target_manifest.ok(),
                    target_manifest.status().message());
    IOTOX_CHECK(basis_manifest.value().block_bytes ==
                target_manifest.value().block_bytes);
    auto encoded_policy = iotox::sync::encode_namespace_policy(policy);
    IOTOX_CHECK_MSG(encoded_policy.ok(),
                    encoded_policy.status().message());
    write_private_record(
        policy_root / "namespaces" / "field-notes.namespace",
        encoded_policy.value());

    const std::string target_path = target_source.string();
    const std::string target_manifest_path = target_manifest_source.string();
    const std::string basis_path = basis_source.string();
    const std::string basis_manifest_path = basis_manifest_source.string();
    ScopedEnvironment mock_namespace(
        "IOTOX_MOCK_SYNC_NAMESPACE", policy.id.c_str());
    ScopedEnvironment mock_artifact(
        "IOTOX_MOCK_SYNC_ARTIFACT", target_path.c_str());
    ScopedEnvironment mock_manifest(
        "IOTOX_MOCK_SYNC_MANIFEST", target_manifest_path.c_str());
    ScopedEnvironment mock_parent_artifact(
        "IOTOX_MOCK_SYNC_PARENT_ARTIFACT", basis_path.c_str());
    ScopedEnvironment mock_parent_manifest(
        "IOTOX_MOCK_SYNC_PARENT_MANIFEST", basis_manifest_path.c_str());

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    config.sync.enabled = true;
    config.sync.policy_store_root = policy_root;
    initialize_mock_v3_sync_authority(config);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto local_identity = iotox::security::DeviceIdentity::load_or_create(
        config.security.device_identity_path, sodium.value(), false);
    IOTOX_CHECK_MSG(local_identity.ok(),
                    local_identity.status().message());
    auto publisher_identity = mock_sync_publisher_identity(
        directory / "mock-publisher.identity", sodium.value());
    auto basis_manifest_digest =
        iotox::sync::hash_sync_file_sha256(basis_manifest_source);
    IOTOX_CHECK_MSG(basis_manifest_digest.ok(),
                    basis_manifest_digest.status().message());
    iotox::sync::SignedHeadPublicationRequest basis_publication;
    basis_publication.artifact = basis_manifest.value().artifact;
    basis_publication.manifest = basis_manifest_digest.value();
    basis_publication.artifact_bytes = basis_bytes.size();
    basis_publication.manifest_bytes =
        basis_manifest.value().manifest_bytes;
    auto basis_head = iotox::sync::create_signed_head(
        policy, basis_publication, std::nullopt, publisher_identity,
        sodium.value());
    IOTOX_CHECK_MSG(basis_head.ok(), basis_head.status().message());
    auto basis_candidate = iotox::sync::verified_candidate_head(
        policy, basis_head.value(), sodium.value());
    IOTOX_CHECK_MSG(basis_candidate.ok(),
                    basis_candidate.status().message());
    iotox::sync::AcceptedHeadStore accepted(namespace_root);
    auto accepted_basis = accepted.accept(
        policy, basis_candidate.value(), local_identity.value(),
        sodium.value());
    IOTOX_CHECK_MSG(accepted_basis.ok(),
                    accepted_basis.status().message());
    IOTOX_CHECK(accepted_basis.value().accepted());
    IOTOX_CHECK(std::filesystem::create_directories(
        namespace_root / "objects"));
    IOTOX_CHECK(::chmod(
        (namespace_root / "objects").c_str(),
        static_cast<mode_t>(0700)) == 0);
    const iotox::sync::SyncObjectRecord basis_object{
        iotox::sync::SyncObjectKind::artifact,
        basis_publication.artifact, basis_publication.artifact_bytes};
    const std::filesystem::path installed_basis =
        iotox::sync::sync_object_path(policy, basis_object);
    IOTOX_CHECK(std::filesystem::copy_file(
        basis_source, installed_basis));
    IOTOX_CHECK(::chmod(
        installed_basis.c_str(), static_cast<mode_t>(0600)) == 0);

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    std::vector<std::uint8_t> transport_key(32U, 0x62U);
    auto added = iotox::local::control_request(
        runtime / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_add,
                470U, transport_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    const std::uint32_t friend_number = read_u32(added.value().payload);

    std::vector<std::uint8_t> pull_payload;
    append_u32(pull_payload, friend_number);
    pull_payload.insert(
        pull_payload.end(), policy.id.begin(), policy.id.end());
    bool pull_queued = false;
    std::uint64_t request_id = 471U;
    const auto authority_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < authority_deadline) {
        auto pull = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_pull,
                    request_id++, pull_payload));
        IOTOX_CHECK_MSG(pull.ok(), pull.status().message());
        if (pull.value().status == iotox::ErrorCode::ok) {
            pull_queued = true;
            break;
        }
        IOTOX_CHECK(
            pull.value().status == iotox::ErrorCode::unavailable ||
            pull.value().status == iotox::ErrorCode::not_found);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(pull_queued,
                    "range pull never passed exact v3 authority");

    std::string sync_status;
    const auto completion_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < completion_deadline) {
        auto status = iotox::local::control_request(
            runtime / "control.sock",
            request(iotox::local::ControlOperation::sync_status,
                    request_id++));
        IOTOX_CHECK_MSG(status.ok(), status.status().message());
        IOTOX_CHECK(status.value().status == iotox::ErrorCode::ok);
        sync_status = iotox::local::payload_text(status.value().payload);
        if (sync_status.find("state=complete") != std::string::npos ||
            sync_status.find("state=failed") != std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK_MSG(
        sync_status.find("state=complete") != std::string::npos,
        sync_status);
    IOTOX_CHECK(sync_status.find("range-transfer=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("scheduler-attempts=") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("scheduler-attempt-bound=8") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-lane-active=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-attempt=") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-bundle-bytes=4096") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-fallback=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-retries=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-discarded-bytes=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-retained-bytes=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-resumed-bytes=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-retention-fallbacks=0") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-count=1") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-reused-bytes=12288") !=
                std::string::npos);
    IOTOX_CHECK(sync_status.find("range-fetched-bytes=4096") !=
                std::string::npos);

    agent.stop();
    auto accepted_target = accepted.load(
        policy, local_identity.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(accepted_target.ok(),
                    accepted_target.status().message());
    IOTOX_CHECK(accepted_target.value().has_value());
    IOTOX_CHECK(accepted_target.value()->generation == 2U);
    const iotox::sync::SyncObjectRecord target_object{
        iotox::sync::SyncObjectKind::artifact,
        target_manifest.value().artifact,
        static_cast<std::uint64_t>(target_bytes.size())};
    IOTOX_CHECK(read_text(
        iotox::sync::sync_object_path(policy, target_object)) ==
        std::string(target_bytes.begin(), target_bytes.end()));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent durable Ratox incarnation excludes competitors and advances "
           "on restart") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    RatoxProfileStoreFixture profile_store(directory);
    auto factory = std::make_shared<NeverSpawnPtyFactory>();

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run-first";
    config.interactive.enabled = true;
    config.interactive.profile_store_root = profile_store.root;
    config.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    config.interactive.process_factory = factory;

    iotox::Agent first(config);
    const iotox::Status first_started = first.start();
    IOTOX_CHECK_MSG(first_started.ok(), first_started.message());
    const auto first_snapshot = first.snapshot();
    IOTOX_CHECK(first_snapshot.ratox_host_incarnation != 0U);
    IOTOX_CHECK(first_snapshot.ratox_incarnation_lease_held);
    const std::uint64_t first_incarnation =
        first_snapshot.ratox_host_incarnation;
    const std::string first_status =
        read_text(config.runtime.root / "status");
    IOTOX_CHECK(first_status.find(
                    "ratox-host-incarnation=" +
                    std::to_string(first_incarnation)) != std::string::npos);
    IOTOX_CHECK(first_status.find("ratox-incarnation-lease-held=1") !=
                std::string::npos);

    const std::filesystem::path state =
        directory / "state" / "ratox" / "incarnation.state";
    struct stat state_metadata {};
    IOTOX_CHECK(::lstat(state.c_str(), &state_metadata) == 0);
    IOTOX_CHECK(S_ISREG(state_metadata.st_mode));
    IOTOX_CHECK(state_metadata.st_uid == ::geteuid());
    IOTOX_CHECK(state_metadata.st_nlink == 1);
    IOTOX_CHECK((state_metadata.st_mode & 07777U) == 0600U);
    IOTOX_CHECK(state_metadata.st_size == 128);

    iotox::Agent::Config competing_config = config;
    competing_config.runtime.root = directory / "run-competing";
    iotox::Agent competing(competing_config);
    const iotox::Status blocked = competing.start();
    IOTOX_CHECK(!blocked.ok());
    IOTOX_CHECK(blocked.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(blocked.message().find("already owns") != std::string::npos);
    IOTOX_CHECK(first.snapshot().ratox_host_incarnation == first_incarnation);
    competing.stop();

    first.stop();
    IOTOX_CHECK(!first.snapshot().ratox_incarnation_lease_held);
    IOTOX_CHECK(first.snapshot().ratox_host_incarnation == 0U);

    iotox::Agent::Config successor_config = config;
    successor_config.runtime.root = directory / "run-successor";
    iotox::Agent successor(successor_config);
    const iotox::Status successor_started = successor.start();
    IOTOX_CHECK_MSG(successor_started.ok(), successor_started.message());
    IOTOX_CHECK(successor.snapshot().ratox_incarnation_lease_held);
    IOTOX_CHECK(
        successor.snapshot().ratox_host_incarnation == first_incarnation + 1U);
    successor.stop();

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent dispatches negotiated Ratox packets through the live "
           "authority gate") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment ratox_peer("IOTOX_MOCK_RATOX_INTERACTIVE", "1");

    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path transport_audit =
        directory / "ratox-transport.audit";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    ScopedEnvironment audit_path(
        "IOTOX_MOCK_AUTHORITY_AUDIT", transport_audit.c_str());
    RatoxProfileStoreFixture profile_store(directory);
    auto factory = std::make_shared<NeverSpawnPtyFactory>();

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    initialize_mock_v1_authority(config);
    config.interactive.enabled = true;
    config.interactive.profile_store_root = profile_store.root;
    config.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    config.interactive.process_factory = factory;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> public_key(32U, 0x53U);
    auto added = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::transport_peer_add,
            410U, public_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    const std::uint32_t friend_number = read_u32(added.value().payload);

    std::string normalized_peer_key;
    normalized_peer_key.reserve(64U);
    for (std::size_t index = 0U; index < 32U; ++index) {
        normalized_peer_key += "53";
    }
    const std::filesystem::path session_path =
        runtime / "peers" / normalized_peer_key / "session";
    const std::filesystem::path authority_path =
        runtime / "peers" / normalized_peer_key / "iotox" / "authority";
    const std::string principal_hex =
        "D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A";

    std::string session_projection;
    std::string remote_principal;
    const auto negotiated_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < negotiated_deadline) {
        session_projection = read_text(session_path);
        remote_principal = read_text(authority_path / "remote-principal");
        if (session_projection.find("state=confirmed") != std::string::npos &&
            line_with_prefix(session_projection, "negotiated-features=")
                    .find("ratox-interactive-v1") != std::string::npos &&
            remote_principal == principal_hex + "\n") {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(session_projection.find("state=confirmed") !=
                std::string::npos);
    IOTOX_CHECK(line_with_prefix(session_projection, "local-supported-features=")
                    .find("ratox-interactive-v1") != std::string::npos);
    IOTOX_CHECK(line_with_prefix(session_projection, "peer-supported-features=")
                    .find("ratox-interactive-v1") != std::string::npos);
    IOTOX_CHECK_MSG(
        line_with_prefix(session_projection, "negotiated-features=")
                .find("ratox-interactive-v1") != std::string::npos,
        "negotiated session projection did not contain Ratox:\n" +
            session_projection);
    IOTOX_CHECK(remote_principal == principal_hex + "\n");
    IOTOX_CHECK(read_text(authority_path / "remote-authorized") == "1\n");

    iotox::protocol::ratox::Frame open;
    open.type = iotox::protocol::ratox::FrameType::open;
    open.message_id = 0x1020304050607080ULL;
    open.session_id.front() = 0x71U;
    open.principal_id = mock_authority_principal();
    open.attachment_nonce.front() = 0x72U;
    open.payload.assign(12U, 0U);
    open.payload[0U] = 1U;
    open.payload[2U] = 0U;
    open.payload[3U] = 80U;
    open.payload[4U] = 0U;
    open.payload[5U] = 24U;
    auto encoded = iotox::protocol::ratox::encode(open);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    std::vector<std::uint8_t> send_payload;
    append_u32(send_payload, friend_number);
    send_payload.insert(
        send_payload.end(), encoded.value().begin(), encoded.value().end());
    auto sent = iotox::local::control_request(
        runtime / "control.sock",
        request(
            iotox::local::ControlOperation::transport_send_lossless,
            411U, std::move(send_payload)));
    IOTOX_CHECK_MSG(sent.ok(), sent.status().message());
    IOTOX_CHECK(sent.value().status == iotox::ErrorCode::ok);

    std::string journal;
    std::string audit;
    const auto dispatch_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < dispatch_deadline) {
        journal = read_text(runtime / "ratox-events");
        audit = read_text(transport_audit);
        if (journal.find("kind=open-denied") != std::string::npos &&
            audit.find("ratox-sent type=OPEN_RESULT") != std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(journal.find("kind=open-denied") != std::string::npos);
    IOTOX_CHECK(journal.find("frame-type=OPEN") != std::string::npos);
    IOTOX_CHECK(journal.find("principal-id=" + principal_hex) !=
                std::string::npos);
    IOTOX_CHECK(audit.find("ratox-sent type=OPEN_RESULT") !=
                std::string::npos);
    IOTOX_CHECK(journal.find("kind=opened") == std::string::npos);
    IOTOX_CHECK(factory->spawn_count.load() == 0U);

    agent.stop();
    IOTOX_CHECK(factory->spawn_count.load() == 0U);
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent revokes a detached Ratox PTY at the next signed authority head") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment ratox_peer("IOTOX_MOCK_RATOX_INTERACTIVE", "1");

    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path control_socket = runtime / "control.sock";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    RatoxProfileStoreFixture profile_store(
        directory, mock_authority_principal());
    auto factory = std::make_shared<TrackingPtyFactory>();

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    initialize_mock_v2_terminal_authority(config);
    config.interactive.enabled = true;
    config.interactive.profile_store_root = profile_store.root;
    config.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    config.interactive.process_factory = factory;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> public_key(32U, 0x54U);
    auto added = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_peer_add,
            420U, public_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    const std::uint32_t friend_number = read_u32(added.value().payload);

    const std::string normalized_peer_key(64U, '5');
    std::string peer_key = normalized_peer_key;
    for (std::size_t index = 1U; index < peer_key.size(); index += 2U) {
        peer_key[index] = '4';
    }
    const std::filesystem::path session_path =
        runtime / "peers" / peer_key / "session";
    const std::filesystem::path authority_path =
        runtime / "peers" / peer_key / "iotox" / "authority";
    const std::string principal_hex =
        "D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A";

    std::string session_projection;
    const auto negotiated_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < negotiated_deadline) {
        session_projection = read_text(session_path);
        if (session_projection.find("state=confirmed") != std::string::npos &&
            line_with_prefix(session_projection, "negotiated-features=")
                    .find("ratox-interactive-v1") != std::string::npos &&
            read_text(authority_path / "remote-principal") ==
                principal_hex + "\n" &&
            read_text(authority_path / "remote-authorized") == "1\n") {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(session_projection.find("state=confirmed") !=
                std::string::npos);
    IOTOX_CHECK(read_text(authority_path / "remote-principal") ==
                principal_hex + "\n");
    IOTOX_CHECK(read_text(authority_path / "remote-authorized") == "1\n");

    iotox::protocol::ratox::Frame open;
    open.type = iotox::protocol::ratox::FrameType::open;
    open.message_id = 0x2030405060708090ULL;
    open.session_id.front() = 0x81U;
    open.principal_id = mock_authority_principal();
    open.attachment_nonce.front() = 0x82U;
    open.payload.assign(12U, 0U);
    open.payload[0U] = 1U;
    open.payload[2U] = 0U;
    open.payload[3U] = 80U;
    open.payload[4U] = 0U;
    open.payload[5U] = 24U;
    auto encoded = iotox::protocol::ratox::encode(open);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    std::vector<std::uint8_t> send_payload;
    append_u32(send_payload, friend_number);
    send_payload.insert(
        send_payload.end(), encoded.value().begin(), encoded.value().end());
    auto sent = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_send_lossless,
            421U, std::move(send_payload)));
    IOTOX_CHECK_MSG(sent.ok(), sent.status().message());
    IOTOX_CHECK(sent.value().status == iotox::ErrorCode::ok);

    std::string journal;
    const auto open_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < open_deadline) {
        journal = read_text(runtime / "ratox-events");
        if (factory->spawn_count.load() == 1U &&
            journal.find("kind=opened") != std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(factory->spawn_count.load() == 1U);
    IOTOX_CHECK(journal.find("kind=opened") != std::string::npos);
    std::shared_ptr<TrackingPtyState> process = factory->latest();
    IOTOX_CHECK(process != nullptr);
    IOTOX_CHECK(process->hangup_signals.load() == 0U);

    std::vector<std::uint8_t> remove_payload;
    append_u32(remove_payload, friend_number);
    auto removed = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_peer_remove,
            422U, std::move(remove_payload)));
    IOTOX_CHECK_MSG(removed.ok(), removed.status().message());
    IOTOX_CHECK(removed.value().status == iotox::ErrorCode::ok);

    const auto detach_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < detach_deadline) {
        journal = read_text(runtime / "ratox-events");
        if (journal.find("kind=peer-detached") != std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(journal.find("kind=peer-detached") != std::string::npos);
    IOTOX_CHECK(process->hangup_signals.load() == 0U);
    IOTOX_CHECK(!process->exited.load());

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner_seed = mock_terminal_owner_seed();
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());

    iotox::security::AuthorityPrepareRequest revoke;
    revoke.action = iotox::security::AuthorityAction::revoke;
    revoke.role = iotox::security::PrincipalRole::none;
    revoke.capabilities = 0U;
    revoke.issuer = owner.value().public_key();
    revoke.subject = mock_authority_principal();
    append_live_authority_request(
        control_socket, revoke, owner.value().secret_key(), sodium.value(),
        423U);
    iotox::security::secure_wipe(owner_seed);

    std::string status;
    const auto revoke_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(8);
    while (std::chrono::steady_clock::now() < revoke_deadline) {
        journal = read_text(runtime / "ratox-events");
        status = read_text(runtime / "status");
        if (process->hangup_signals.load() == 1U &&
            journal.find("kind=authority-revoked") != std::string::npos &&
            status.find("ratox-running-process-count=0") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(process->hangup_signals.load() == 1U);
    IOTOX_CHECK(process->terminate_signals.load() == 0U);
    IOTOX_CHECK(process->kill_signals.load() == 0U);
    IOTOX_CHECK(process->exited.load());
    IOTOX_CHECK(journal.find("kind=authority-revoked") != std::string::npos);
    IOTOX_CHECK(journal.find("principal-id=" + principal_hex) !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-running-process-count=0") !=
                std::string::npos);
    IOTOX_CHECK(factory->spawn_count.load() == 1U);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent purges a SENDQ-retained Ratox result at signed revocation") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment ratox_peer("IOTOX_MOCK_RATOX_INTERACTIVE", "1");
    ScopedEnvironment retained_result(
        "IOTOX_MOCK_RATOX_OPEN_RESULT_SENDQ_FAILURES", "100000");

    const std::filesystem::path directory = agent_test_directory();
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path control_socket = runtime / "control.sock";
    const std::filesystem::path transport_audit =
        directory / "ratox-transport.audit";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), static_cast<mode_t>(0700)) == 0);
    ScopedEnvironment audit_path(
        "IOTOX_MOCK_AUTHORITY_AUDIT", transport_audit.c_str());
    RatoxProfileStoreFixture profile_store(
        directory, mock_authority_principal());
    auto factory = std::make_shared<TrackingPtyFactory>();

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = runtime;
    initialize_mock_v2_terminal_authority(config);
    config.interactive.enabled = true;
    config.interactive.profile_store_root = profile_store.root;
    config.interactive.expected_profile_owner_uid =
        static_cast<std::uint32_t>(::geteuid());
    config.interactive.process_factory = factory;

    iotox::Agent agent(config);
    const iotox::Status started = agent.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    std::vector<std::uint8_t> public_key(32U, 0x55U);
    auto added = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_peer_add,
            430U, public_key));
    IOTOX_CHECK_MSG(added.ok(), added.status().message());
    IOTOX_CHECK(added.value().status == iotox::ErrorCode::ok);
    const std::uint32_t friend_number = read_u32(added.value().payload);

    const std::string peer_key(64U, '5');
    const std::filesystem::path session_path =
        runtime / "peers" / peer_key / "session";
    const std::filesystem::path authority_path =
        runtime / "peers" / peer_key / "iotox" / "authority";
    const std::string principal_hex =
        "D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A";

    std::string session_projection;
    const auto negotiated_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < negotiated_deadline) {
        session_projection = read_text(session_path);
        if (session_projection.find("state=confirmed") != std::string::npos &&
            line_with_prefix(session_projection, "negotiated-features=")
                    .find("ratox-interactive-v1") != std::string::npos &&
            read_text(authority_path / "remote-principal") ==
                principal_hex + "\n" &&
            read_text(authority_path / "remote-authorized") == "1\n") {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(session_projection.find("state=confirmed") !=
                std::string::npos);
    IOTOX_CHECK(line_with_prefix(session_projection, "negotiated-features=")
                    .find("ratox-interactive-v1") != std::string::npos);
    IOTOX_CHECK(read_text(authority_path / "remote-principal") ==
                principal_hex + "\n");
    IOTOX_CHECK(read_text(authority_path / "remote-authorized") == "1\n");

    iotox::protocol::ratox::Frame open;
    open.type = iotox::protocol::ratox::FrameType::open;
    open.message_id = 0x30405060708090A0ULL;
    open.session_id.front() = 0x91U;
    open.principal_id = mock_authority_principal();
    open.attachment_nonce.front() = 0x92U;
    open.payload.assign(12U, 0U);
    open.payload[0U] = 1U;
    open.payload[2U] = 0U;
    open.payload[3U] = 80U;
    open.payload[4U] = 0U;
    open.payload[5U] = 24U;
    auto encoded = iotox::protocol::ratox::encode(open);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    std::vector<std::uint8_t> send_payload;
    append_u32(send_payload, friend_number);
    send_payload.insert(
        send_payload.end(), encoded.value().begin(), encoded.value().end());
    auto sent = iotox::local::control_request(
        control_socket,
        request(
            iotox::local::ControlOperation::transport_send_lossless,
            431U, std::move(send_payload)));
    IOTOX_CHECK_MSG(sent.ok(), sent.status().message());
    IOTOX_CHECK(sent.value().status == iotox::ErrorCode::ok);

    std::string status;
    std::string audit;
    const auto retained_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < retained_deadline) {
        status = read_text(runtime / "status");
        audit = read_text(transport_audit);
        if (factory->spawn_count.load() == 1U &&
            status.find("ratox-outbound-packet-count=1") !=
                std::string::npos &&
            audit.find("ratox-open-result-sendq") != std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(factory->spawn_count.load() == 1U);
    IOTOX_CHECK(status.find("ratox-outbound-packet-count=1") !=
                std::string::npos);
    IOTOX_CHECK(audit.find("ratox-open-result-sendq") !=
                std::string::npos);
    IOTOX_CHECK(audit.find("ratox-sent type=OPEN_RESULT") ==
                std::string::npos);
    std::shared_ptr<TrackingPtyState> process = factory->latest();
    IOTOX_CHECK(process != nullptr);

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner_seed = mock_terminal_owner_seed();
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());

    iotox::security::AuthorityPrepareRequest revoke;
    revoke.action = iotox::security::AuthorityAction::revoke;
    revoke.role = iotox::security::PrincipalRole::none;
    revoke.capabilities = 0U;
    revoke.issuer = owner.value().public_key();
    revoke.subject = mock_authority_principal();
    append_live_authority_request(
        control_socket, revoke, owner.value().secret_key(), sodium.value(),
        432U);
    iotox::security::secure_wipe(owner_seed);

    const std::size_t attempts_after_append = count_occurrences(
        read_text(transport_audit), "ratox-open-result-sendq");
    IOTOX_CHECK(attempts_after_append != 0U);

    std::string journal;
    const auto revoked_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(8);
    while (std::chrono::steady_clock::now() < revoked_deadline) {
        journal = read_text(runtime / "ratox-events");
        status = read_text(runtime / "status");
        if (process->hangup_signals.load() == 1U &&
            journal.find("kind=authority-revoked") != std::string::npos &&
            status.find("ratox-outbound-packet-count=0") !=
                std::string::npos &&
            status.find("ratox-running-process-count=0") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(process->hangup_signals.load() == 1U);
    IOTOX_CHECK(process->exited.load());
    IOTOX_CHECK(journal.find("kind=authority-revoked") != std::string::npos);
    IOTOX_CHECK(status.find("ratox-outbound-packet-count=0") !=
                std::string::npos);
    IOTOX_CHECK(status.find("ratox-outbound-bytes=0") != std::string::npos);
    IOTOX_CHECK(status.find("ratox-running-process-count=0") !=
                std::string::npos);

    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    audit = read_text(transport_audit);
    IOTOX_CHECK(count_occurrences(
                    audit, "ratox-open-result-sendq") ==
                attempts_after_append);
    IOTOX_CHECK(audit.find("ratox-sent type=OPEN_RESULT") ==
                std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("agent keeps malformed local transport commands away from toxcore") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK(agent.start().ok());

    auto bad_key = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_add, 10U,
                std::vector<std::uint8_t>(31U, 0U)));
    IOTOX_CHECK(bad_key.ok());
    IOTOX_CHECK(bad_key.value().status == iotox::ErrorCode::invalid_argument);

    auto bad_send = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::transport_send_lossless, 11U,
                std::vector<std::uint8_t>(4U, 0U)));
    IOTOX_CHECK(bad_send.ok());
    IOTOX_CHECK(bad_send.value().status == iotox::ErrorCode::invalid_argument);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("outgoing friend request binds lifecycle evidence to the address "
           "public key") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK(agent.start().ok());

    std::vector<std::uint8_t> address(38U, 0U);
    std::fill_n(address.begin(), 32U, static_cast<std::uint8_t>(0xC5U));
    address[32U] = 0x10U;
    address[33U] = 0x20U;
    address[34U] = 0x30U;
    address[35U] = 0x40U;
    address[36U] = 0x50U;
    address[37U] = 0x60U;
    const std::vector<std::uint8_t> message{
        'p', 'u', 'b', 'l', 'i', 'c', '-', 'k', 'e', 'y', '-', 'f', 'i', 'r', 's', 't'};
    std::vector<std::uint8_t> payload = address;
    payload.insert(payload.end(), message.begin(), message.end());

    auto requested = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_request,
                26U, payload));
    IOTOX_CHECK_MSG(requested.ok(), requested.status().message());
    IOTOX_CHECK(requested.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(read_u32(requested.value().payload) == 0U);

    auto peers = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_list, 27U));
    IOTOX_CHECK_MSG(peers.ok(), peers.status().message());
    auto decoded_peers = iotox::local::decode_peer_list(peers.value().payload);
    IOTOX_CHECK_MSG(decoded_peers.ok(), decoded_peers.status().message());
    IOTOX_CHECK(decoded_peers.value().size() == 1U);
    IOTOX_CHECK(decoded_peers.value().front().friend_number == 0U);
    IOTOX_CHECK(std::all_of(
        decoded_peers.value().front().public_key.begin(),
        decoded_peers.value().front().public_key.end(),
        [](std::uint8_t byte) { return byte == 0xC5U; }));

    // Build the actual repeated C5 hexadecimal public key explicitly rather
    // than treating a friend number as durable identity.
    std::string expected_key;
    for (std::size_t index = 0U; index < 32U; ++index) {
        expected_key += "C5";
    }
    IOTOX_CHECK(std::filesystem::exists(
        config.runtime.root / "peers" / expected_key));
    const std::string evidence =
        read_text(config.runtime.root / "friend-events");
    IOTOX_CHECK(evidence.find(
                    "source=control-socket operation=request-send public-key=" +
                    expected_key + " disposition=requested") !=
                std::string::npos);
    IOTOX_CHECK(evidence.find(
                    "IoTox authority is unchanged") != std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("root request FIFO admits one exact outgoing friend request") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK_MSG(agent.start().ok(), "agent did not start");

    const std::filesystem::path request_fifo = config.runtime.root / "request";
    IOTOX_CHECK(std::filesystem::is_fifo(request_fifo));
    const std::string help = read_text(config.runtime.root / "request.help");
    IOTOX_CHECK(help.find("<76 hexadecimal Tox address bytes><TAB>") !=
                std::string::npos);
    IOTOX_CHECK(help.find("does not prove remote receipt or acceptance") !=
                std::string::npos);

    // A complete LF-framed record that cannot establish even a public-key
    // prefix must remain observable without inventing a fake peer identity.
    write_fifo_record(request_fifo, "too-short\n");

    const std::string public_key_lower(64U, 'c');
    const std::string address_lower = public_key_lower + "102030402060";
    const std::string message{"root\tfifo\0request", 17U};
    write_fifo_record(
        request_fifo, address_lower + "\t" + message + "\n");

    const std::string expected_key(64U, 'C');
    const std::filesystem::path peer_directory =
        config.runtime.root / "peers" / expected_key;
    std::string evidence;
    std::string status;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < deadline) {
        evidence = read_text(config.runtime.root / "friend-events");
        status = read_text(config.runtime.root / "status");
        if (std::filesystem::exists(peer_directory) &&
            evidence.find(
                "source=local-fifo operation=request-send public-key=" +
                expected_key + " disposition=requested") != std::string::npos &&
            evidence.find("source=local-fifo operation=request-send "
                          "public-key=unknown disposition=rejected") !=
                std::string::npos &&
            status.find("request-send-fifo-count=1") != std::string::npos &&
            status.find("friendship-fifo-record-count=2") !=
                std::string::npos &&
            status.find("friendship-fifo-rejected-count=1") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    IOTOX_CHECK(std::filesystem::exists(peer_directory));
    IOTOX_CHECK(evidence.find(
                    "source=local-fifo operation=request-send public-key=" +
                    expected_key + " disposition=requested") !=
                std::string::npos);
    IOTOX_CHECK(evidence.find("source=local-fifo operation=request-send "
                              "public-key=unknown disposition=rejected") !=
                std::string::npos);
    IOTOX_CHECK(evidence.find(
                    "not evidence of remote receipt or acceptance") !=
                std::string::npos);
    IOTOX_CHECK(status.find("request-send-fifo-count=1") !=
                std::string::npos);
    IOTOX_CHECK(status.find("friendship-fifo-record-count=2") !=
                std::string::npos);
    IOTOX_CHECK(status.find("friendship-fifo-rejected-count=1") !=
                std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("ratox friendship FIFOs accept a live request and remove the "
           "key-bound peer") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment incoming("IOTOX_MOCK_INCOMING_FRIEND_REQUEST", "hello-from-peer");

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK(agent.start().ok());

    std::string key;
    for (std::size_t index = 0U; index < 32U; ++index) {
        key += "A7";
    }
    const std::filesystem::path request_directory =
        config.runtime.root / "requests" / key;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (!std::filesystem::exists(request_directory) &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(std::filesystem::exists(request_directory));
    IOTOX_CHECK(read_text(request_directory / "message") == "hello-from-peer");
    IOTOX_CHECK(std::filesystem::is_fifo(request_directory / "accept"));
    IOTOX_CHECK(std::filesystem::is_fifo(request_directory / "reject"));
    const auto pending_count_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (read_text(config.runtime.root / "status").find("pending-request-count=1") ==
               std::string::npos &&
           std::chrono::steady_clock::now() < pending_count_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(read_text(config.runtime.root / "status").find(
                    "pending-request-count=1") != std::string::npos);

    write_fifo_record(request_directory / "accept", "accept\n");
    const std::filesystem::path peer_directory =
        config.runtime.root / "peers" / key;
    const auto accepted_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while ((std::filesystem::exists(request_directory) ||
            !std::filesystem::exists(peer_directory / "remove")) &&
           std::chrono::steady_clock::now() < accepted_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(!std::filesystem::exists(request_directory));
    IOTOX_CHECK(std::filesystem::exists(peer_directory));
    IOTOX_CHECK(std::filesystem::is_fifo(peer_directory / "remove"));
    const auto request_count_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (read_text(config.runtime.root / "status").find(
               "pending-request-count=0") == std::string::npos &&
           std::chrono::steady_clock::now() < request_count_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(read_text(config.runtime.root / "status").find(
                    "pending-request-count=0") != std::string::npos);

    write_fifo_record(peer_directory / "remove", "remove\n");
    const auto removed_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::filesystem::exists(peer_directory) &&
           std::chrono::steady_clock::now() < removed_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(!std::filesystem::exists(peer_directory));

    const std::filesystem::path friendship_events =
        config.runtime.root / "friend-events";
    std::string evidence;
    const auto evidence_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < evidence_deadline) {
        evidence = read_text(friendship_events);
        const std::string status = read_text(config.runtime.root / "status");
        if (evidence.find("source=toxcore operation=request-received") !=
                std::string::npos &&
            evidence.find("source=local-fifo operation=request-accept") !=
                std::string::npos &&
            evidence.find("source=local-fifo operation=peer-remove") !=
                std::string::npos &&
            status.find("friendship-fifo-record-count=2") !=
                std::string::npos &&
            status.find("friendship-fifo-rejected-count=0") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(
        evidence.find("source=toxcore operation=request-received") !=
        std::string::npos);
    IOTOX_CHECK(
        evidence.find("source=local-fifo operation=request-accept") !=
        std::string::npos);
    IOTOX_CHECK(
        evidence.find("source=local-fifo operation=peer-remove") !=
        std::string::npos);
    IOTOX_CHECK(evidence.find("IoTox authority is unchanged") !=
                std::string::npos);
    const std::string final_status = read_text(config.runtime.root / "status");
    IOTOX_CHECK(final_status.find("friendship-fifo-record-count=2") !=
                std::string::npos);
    IOTOX_CHECK(final_status.find("friendship-fifo-rejected-count=0") !=
                std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("request acceptance requires a live matching inbox record") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK(agent.start().ok());

    std::vector<std::uint8_t> public_key(32U, 0xB6U);
    auto accepted = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(
            iotox::local::ControlOperation::transport_friend_request_accept,
            24U, public_key));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().status == iotox::ErrorCode::not_found);

    auto peers = iotox::local::control_request(
        config.runtime.root / "control.sock",
        request(iotox::local::ControlOperation::transport_peer_list, 25U));
    IOTOX_CHECK_MSG(peers.ok(), peers.status().message());
    auto decoded_peers = iotox::local::decode_peer_list(peers.value().payload);
    IOTOX_CHECK_MSG(decoded_peers.ok(), decoded_peers.status().message());
    IOTOX_CHECK(decoded_peers.value().empty());

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}


IOTOX_TEST("ratox reject FIFO withdraws a live request without creating a peer") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment incoming(
        "IOTOX_MOCK_INCOMING_FRIEND_REQUEST", "reject-this-request");

    const std::filesystem::path directory = agent_test_directory();
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));

    iotox::Agent::Config config;
    config.transport.toxcore_library = mock_library;
    config.transport.state_path = directory / "state" / "device.toxsave";
    config.transport.save_state_on_stop = false;
    config.runtime.root = directory / "run";
    iotox::Agent agent(config);
    IOTOX_CHECK(agent.start().ok());

    const std::filesystem::path socket = config.runtime.root / "control.sock";
    std::vector<std::uint8_t> public_key(32U, 0xA7U);
    std::string key;
    for (std::size_t index = 0U; index < public_key.size(); ++index) {
        key += "A7";
    }
    const std::filesystem::path request_directory =
        config.runtime.root / "requests" / key;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (!std::filesystem::exists(request_directory) &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(std::filesystem::exists(request_directory));
    IOTOX_CHECK(std::filesystem::is_fifo(request_directory / "accept"));
    IOTOX_CHECK(std::filesystem::is_fifo(request_directory / "reject"));

    auto listed = iotox::local::control_request(
        socket,
        request(iotox::local::ControlOperation::transport_friend_request_list,
                31U));
    IOTOX_CHECK_MSG(listed.ok(), listed.status().message());
    IOTOX_CHECK(listed.value().status == iotox::ErrorCode::ok);
    auto requests =
        iotox::local::decode_friend_request_list(listed.value().payload);
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    IOTOX_CHECK(requests.value().size() == 1U);
    IOTOX_CHECK(requests.value().front().message ==
                std::vector<std::uint8_t>({'r', 'e', 'j', 'e', 'c', 't', '-',
                                           't', 'h', 'i', 's', '-', 'r', 'e',
                                           'q', 'u', 'e', 's', 't'}));

    write_fifo_record(request_directory / "reject", "reject\n");
    const auto rejected_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::filesystem::exists(request_directory) &&
           std::chrono::steady_clock::now() < rejected_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(!std::filesystem::exists(request_directory));

    auto peers = iotox::local::control_request(
        socket,
        request(iotox::local::ControlOperation::transport_peer_list, 33U));
    IOTOX_CHECK_MSG(peers.ok(), peers.status().message());
    IOTOX_CHECK(peers.value().status == iotox::ErrorCode::ok);
    auto decoded_peers = iotox::local::decode_peer_list(peers.value().payload);
    IOTOX_CHECK_MSG(decoded_peers.ok(), decoded_peers.status().message());
    IOTOX_CHECK(decoded_peers.value().empty());

    auto duplicate = iotox::local::control_request(
        socket,
        request(
            iotox::local::ControlOperation::transport_friend_request_reject,
            34U, public_key));
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK(duplicate.value().status == iotox::ErrorCode::not_found);

    std::string evidence;
    const auto evidence_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < evidence_deadline) {
        evidence = read_text(config.runtime.root / "friend-events");
        const std::string status = read_text(config.runtime.root / "status");
        if (evidence.find("source=local-fifo operation=request-reject") !=
                std::string::npos &&
            status.find("friendship-fifo-record-count=1") !=
                std::string::npos &&
            status.find("friendship-fifo-rejected-count=0") !=
                std::string::npos) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(
        evidence.find("source=local-fifo operation=request-reject") !=
        std::string::npos);
    IOTOX_CHECK(evidence.find("c-toxcore has no pending-request object") !=
                std::string::npos);
    const std::string final_status = read_text(config.runtime.root / "status");
    IOTOX_CHECK(final_status.find("friendship-fifo-record-count=1") !=
                std::string::npos);
    IOTOX_CHECK(final_status.find("friendship-fifo-rejected-count=0") !=
                std::string::npos);

    agent.stop();
    std::filesystem::remove_all(directory, ignored);
}
