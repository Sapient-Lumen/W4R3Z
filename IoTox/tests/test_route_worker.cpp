#include "iotox/route_worker.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_content_wire.hpp"
#include "iotox/sync_wire.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <optional>
#include <thread>
#include <sys/stat.h>
#include <unistd.h>

namespace {

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

iotox::routes::ToxPublicKey key(std::uint8_t value) {
    iotox::routes::ToxPublicKey result{};
    result.fill(value);
    return result;
}

iotox::routes::ToxPublicKey decode_public_key(std::string_view address) {
    IOTOX_CHECK(address.size() >= 64U);
    const auto nibble = [](char value) -> unsigned {
        if (value >= '0' && value <= '9') {
            return static_cast<unsigned>(value - '0');
        }
        if (value >= 'A' && value <= 'F') {
            return static_cast<unsigned>(value - 'A') + 10U;
        }
        if (value >= 'a' && value <= 'f') {
            return static_cast<unsigned>(value - 'a') + 10U;
        }
        IOTOX_CHECK_MSG(false, "invalid hexadecimal Tox address");
        return 0U;
    };
    iotox::routes::ToxPublicKey result{};
    for (std::size_t index = 0U; index < result.size(); ++index) {
        result[index] = static_cast<std::uint8_t>(
            (nibble(address[index * 2U]) << 4U) |
            nibble(address[index * 2U + 1U]));
    }
    return result;
}

std::filesystem::path unique_root(std::string_view suffix) {
    static std::atomic<unsigned> sequence{0U};
    return std::filesystem::temp_directory_path() /
        ("iotox-route-worker-" + std::to_string(::getpid()) + "-" +
         std::to_string(sequence.fetch_add(1U)) + "-" + std::string(suffix));
}

struct ProvisionedWorker {
    std::filesystem::path root;
    iotox::routes::ToxPublicKey public_key{};
};

ProvisionedWorker provision_worker(const char *mock_library,
                                   std::string_view suffix,
                                   std::uint8_t friend_key = 0x42U) {
    ProvisionedWorker result;
    result.root = unique_root(suffix);
    std::filesystem::create_directories(result.root);
    IOTOX_CHECK(::chmod(result.root.c_str(), static_cast<mode_t>(0700)) == 0);
    const auto temporary = result.root / "provisioning.toxsave";
    iotox::ToxTransport::Config transport_config;
    transport_config.toxcore_library = mock_library;
    transport_config.state_path = temporary;
    iotox::ToxTransport transport(transport_config);
    IOTOX_CHECK(transport.start().ok());
    auto friend_number = transport.accept_friend(
        std::vector<std::uint8_t>(32U, friend_key));
    IOTOX_CHECK(friend_number.ok());
    result.public_key = decode_public_key(transport.address_hex());
    transport.stop();
    const auto final_path = iotox::routes::WorkerSupervisor::state_path_for(
        result.root, result.public_key);
    std::filesystem::rename(temporary, final_path);
    return result;
}

iotox::routes::RouteSet route_set_for(
    const iotox::routes::ToxPublicKey &worker_key) {
    iotox::routes::RouteSet set;
    set.generation = 1U;
    set.stable_device_principal.fill(0x31U);
    set.coordinator_tox_public_key = key(0x71U);
    set.members = {
        {worker_key, iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {set.coordinator_tox_public_key, iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
    };
    return set;
}

iotox::security::SigningPublicKey mock_remote_principal() {
    return {
        0xD7U, 0x5AU, 0x98U, 0x01U, 0x82U, 0xB1U, 0x0AU, 0xB7U,
        0xD5U, 0x4BU, 0xFEU, 0xD3U, 0xC9U, 0x64U, 0x07U, 0x3AU,
        0x0EU, 0xE1U, 0x72U, 0xF3U, 0xDAU, 0xA6U, 0x23U, 0x25U,
        0xAFU, 0x02U, 0x1AU, 0x68U, 0xF7U, 0x07U, 0x51U, 0x1AU,
    };
}

iotox::protocol::PeerSessionSnapshot private_primary_session(
    const iotox::routes::ToxPublicKey &local_coordinator) {
    using namespace iotox::protocol;
    SessionNonce local_nonce{};
    SessionNonce remote_nonce{};
    local_nonce.fill(0x31U);
    remote_nonce.fill(0x51U);
    const std::uint64_t features =
        kImplementedFeatureMask |
        feature_bit(Feature::route_binding_v1) |
        feature_bit(Feature::private_route_binding_v2);
    const HelloPayload local = make_local_hello(
        4096U, local_nonce, features);
    const HelloPayload remote = make_local_hello(
        4096U, remote_nonce, features);
    PeerSessionSnapshot session;
    session.friend_number = 77U;
    session.public_key = iotox::public_key_hex(key(0x42U));
    session.local_public_key =
        iotox::public_key_hex(local_coordinator);
    session.connection_status = 1;
    session.state = PeerSessionState::confirmed;
    session.connected = session.hello_sent = session.hello_received = true;
    session.confirmation_sent = session.confirmation_received = true;
    session.application_ready = session.local_role_known = true;
    session.local_role = SessionRole::higher_transport_key;
    session.online_epoch = 1U;
    session.local_hello_message_id = 101U;
    session.peer_hello_message_id = 201U;
    session.local_confirmation_message_id = 102U;
    session.peer_confirmation_message_id = 202U;
    session.local = local;
    session.peer = remote;
    session.negotiated = negotiate_protocol(local, remote);
    IOTOX_CHECK(session.negotiated.compatible);
    return session;
}

}  // namespace

IOTOX_TEST("route worker supervisor owns one exact auxiliary transport") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(mock_library, "start");
    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = route_set_for(provisioned.public_key);
    config.session_incarnation = 1U;
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    const auto started = supervisor.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(supervisor.running());
    const auto snapshot = supervisor.snapshot();
    IOTOX_CHECK(snapshot.size() == 1U);
    IOTOX_CHECK(snapshot.front().policy.tox_public_key ==
                provisioned.public_key);
    IOTOX_CHECK(snapshot.front().worker_id != 0U);
    IOTOX_CHECK(snapshot.front().transport_running);
    IOTOX_CHECK(snapshot.front().unique_peer);
    IOTOX_CHECK(supervisor.transfers().empty());
    IOTOX_CHECK(!supervisor.take_transfer_terminal_events(0U).ok());
    auto terminal = supervisor.take_transfer_terminal_events(1U);
    IOTOX_CHECK(terminal.ok() && terminal.value().empty());
    IOTOX_CHECK(!supervisor.take_sync_frame_events(1U).ok());
    IOTOX_CHECK(!supervisor.receive_to_path(
                     provisioned.public_key, snapshot.front().worker_id, 7U,
                     provisioned.root / "must-not-exist.bin").ok());
    IOTOX_CHECK(!supervisor.cancel_transfer(
                     provisioned.public_key, snapshot.front().worker_id,
                     7U).ok());
    iotox::FileId explicit_id{};
    explicit_id.fill(0x5CU);
    IOTOX_CHECK(!supervisor.send_path_with_file_id(
                     provisioned.public_key, snapshot.front().worker_id,
                     provisioned.root / "must-not-exist.bin", explicit_id).ok());
    IOTOX_CHECK(!std::filesystem::exists(
        provisioned.root / "must-not-exist.bin"));
    supervisor.stop();
    IOTOX_CHECK(!supervisor.running());
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker retries accepted but unobserved handshake records") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(
        mock_library, "accepted-handshake-drop");
    ScopedEnvironment drop_first_hello(
        "IOTOX_MOCK_HELLO_ACCEPTED_DROPS", "1");
    ScopedEnvironment drop_first_confirmation(
        "IOTOX_MOCK_CONFIRMATION_ACCEPTED_DROPS", "1");

    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = route_set_for(provisioned.public_key);
    config.session_incarnation = 1U;
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    IOTOX_CHECK(supervisor.start().ok());

    iotox::routes::WorkerSessionSnapshot recovered;
    const auto deadline = std::chrono::steady_clock::now() +
                          std::chrono::seconds(5);
    do {
        recovered = supervisor.snapshot().front();
        if (recovered.application_ready) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < deadline);
    IOTOX_CHECK(recovered.application_ready);
    IOTOX_CHECK(recovered.hello_sent);
    IOTOX_CHECK(recovered.hello_received);
    IOTOX_CHECK(recovered.confirmation_sent);
    IOTOX_CHECK(recovered.confirmation_received);
    // HELLO continues at the same bounded cadence while the deliberately
    // dropped confirmation leaves the application transcript incomplete.
    IOTOX_CHECK(recovered.hello_send_attempts >= 2U);
    IOTOX_CHECK(recovered.hello_send_attempts <= 4U);
    IOTOX_CHECK(recovered.confirmation_send_attempts >= 2U);
    IOTOX_CHECK(recovered.confirmation_send_attempts <= 3U);

    supervisor.stop();
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker binds one exact member to a strict Tor context") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(
        mock_library, "network-override");
    const auto audit = provisioned.root / "options.audit";
    ScopedEnvironment audit_environment(
        "IOTOX_MOCK_OPTIONS_AUDIT", audit.c_str());

    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    iotox::toxcore::BootstrapEndpoint endpoint;
    // The primary template is intentionally unusable under strict Tor. The
    // exact worker replacement below is what makes this configuration valid.
    endpoint.host = "fixture.invalid.example";
    endpoint.port = 33445U;
    endpoint.public_key.fill(0x6BU);
    config.transport_template.bootstrap_nodes.push_back(endpoint);
    config.transport_template.tcp_relays.push_back(endpoint);
    config.state_root = provisioned.root;
    config.route_set = route_set_for(provisioned.public_key);
    config.route_set.format_version =
        iotox::routes::kRouteSetFormatVersionV2;
    config.route_set.members.front().role =
        iotox::routes::Role::bulk;
    config.route_set.members.front().network_class =
        iotox::routes::NetworkClass::tox_tor;
    config.route_set.members.back().role =
        iotox::routes::Role::protected_route;
    config.route_set.members.back().network_class =
        iotox::routes::NetworkClass::tox_native;
    config.session_incarnation = 2U;
    iotox::routes::WorkerNetworkOverride network_override;
    network_override.tox_public_key = provisioned.public_key;
    network_override.network =
        {iotox::TransportKind::tox, iotox::ToxRoute::tor};
    network_override.socks5_proxy =
        iotox::Socks5ProxyEndpoint{"127.0.0.1", 9050U};
    endpoint.host = "192.0.2.44";
    network_override.bootstrap_nodes.push_back(endpoint);
    network_override.tcp_relays.push_back(endpoint);
    const auto effective_transport =
        iotox::routes::apply_worker_network_override(
            config.transport_template, network_override);
    IOTOX_CHECK(effective_transport.network == network_override.network);
    IOTOX_CHECK(effective_transport.socks5_proxy ==
                network_override.socks5_proxy);
    IOTOX_CHECK(effective_transport.bootstrap_nodes ==
                network_override.bootstrap_nodes);
    IOTOX_CHECK(effective_transport.tcp_relays ==
                network_override.tcp_relays);
    auto inherited_override = network_override;
    inherited_override.bootstrap_nodes.clear();
    inherited_override.tcp_relays.clear();
    const auto inherited_transport =
        iotox::routes::apply_worker_network_override(
            config.transport_template, inherited_override);
    IOTOX_CHECK(inherited_transport.bootstrap_nodes ==
                config.transport_template.bootstrap_nodes);
    IOTOX_CHECK(inherited_transport.tcp_relays ==
                config.transport_template.tcp_relays);
    config.network_overrides.push_back(std::move(network_override));
    iotox::routes::WorkerSupervisor supervisor(config);
    const auto started = supervisor.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    const auto snapshot = supervisor.snapshot();
    IOTOX_CHECK(snapshot.size() == 1U);
    IOTOX_CHECK(snapshot.front().network.transport ==
                iotox::TransportKind::tox);
    IOTOX_CHECK(snapshot.front().network.tox_route ==
                iotox::ToxRoute::tor);
    supervisor.stop();

    std::ifstream input(audit);
    IOTOX_CHECK(input.is_open());
    std::string options;
    IOTOX_CHECK(static_cast<bool>(std::getline(input, options)));
    IOTOX_CHECK(input.peek() == std::char_traits<char>::eof());
    IOTOX_CHECK(options ==
                "udp=0 local-discovery=0 dht-announcements=0 hole-punching=0 proxy=2 proxy-host=127.0.0.1 proxy-port=9050 disable-dns=1");

    auto signed_mismatch = config;
    signed_mismatch.route_set.members.front().network_class =
        iotox::routes::NetworkClass::tox_native;
    iotox::routes::WorkerSupervisor mismatch_supervisor(
        std::move(signed_mismatch));
    const auto mismatched = mismatch_supervisor.start();
    IOTOX_CHECK(!mismatched.ok());
    IOTOX_CHECK(mismatched.message().find("signed member policy") !=
                std::string::npos);

    auto inherited = config;
    inherited.network_overrides.front().bootstrap_nodes.clear();
    inherited.network_overrides.front().tcp_relays.clear();
    iotox::routes::WorkerSupervisor inherited_supervisor(
        std::move(inherited));
    IOTOX_CHECK(!inherited_supervisor.start().ok());

    auto endpoint_bound = config;
    endpoint_bound.network_overrides.front().bootstrap_nodes.assign(
        17U, endpoint);
    iotox::routes::WorkerSupervisor endpoint_bound_supervisor(
        std::move(endpoint_bound));
    IOTOX_CHECK(!endpoint_bound_supervisor.start().ok());

    auto duplicate_endpoint = config;
    duplicate_endpoint.network_overrides.front().tcp_relays.push_back(
        endpoint);
    iotox::routes::WorkerSupervisor duplicate_endpoint_supervisor(
        std::move(duplicate_endpoint));
    IOTOX_CHECK(!duplicate_endpoint_supervisor.start().ok());

    auto duplicate = config;
    duplicate.network_overrides.push_back(
        duplicate.network_overrides.front());
    iotox::routes::WorkerSupervisor duplicate_supervisor(
        std::move(duplicate));
    IOTOX_CHECK(!duplicate_supervisor.start().ok());

    auto coordinator = config;
    coordinator.network_overrides.front().tox_public_key =
        coordinator.route_set.coordinator_tox_public_key;
    iotox::routes::WorkerSupervisor coordinator_supervisor(
        std::move(coordinator));
    IOTOX_CHECK(!coordinator_supervisor.start().ok());

    auto udp = config;
    udp.route_set.members.front().connection_class =
        iotox::routes::ConnectionClass::udp;
    iotox::routes::WorkerSupervisor udp_supervisor(std::move(udp));
    IOTOX_CHECK(!udp_supervisor.start().ok());

    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker readiness qualification advances one exact identity first") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto first = provision_worker(mock_library, "readiness-first", 0x41U);
    auto second = provision_worker(mock_library, "readiness-second", 0x42U);
    const auto original_second_state =
        iotox::routes::WorkerSupervisor::state_path_for(
            second.root, second.public_key);
    auto second_savedata = iotox::StateStore::read(original_second_state);
    IOTOX_CHECK(second_savedata.ok());
    IOTOX_CHECK(second_savedata.value().size() > 4U);
    second_savedata.value()[4U] ^= 0x80U;
    {
        std::ofstream output(
            original_second_state, std::ios::binary | std::ios::trunc);
        output.write(
            reinterpret_cast<const char *>(second_savedata.value().data()),
            static_cast<std::streamsize>(second_savedata.value().size()));
        IOTOX_CHECK(output.good());
    }
    second.public_key[0U] ^= 0x80U;
    const auto combined_second_state =
        iotox::routes::WorkerSupervisor::state_path_for(
            first.root, second.public_key);
    std::filesystem::rename(original_second_state, combined_second_state);
    std::error_code ignored;
    std::filesystem::remove_all(second.root, ignored);

    auto set = route_set_for(first.public_key);
    set.members.front().role = iotox::routes::Role::bulk;
    set.members.insert(
        set.members.begin() + 1,
        iotox::routes::MemberPolicy{
            second.public_key, iotox::routes::Role::bulk,
            iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U});

    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = first.root;
    config.route_set = set;
    config.session_incarnation = 2U;
    config.qualification_first_worker = second.public_key;
    config.qualification_other_worker_delay = std::chrono::seconds(2);
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    IOTOX_CHECK(supervisor.start().ok());

    const auto initial = supervisor.snapshot();
    IOTOX_CHECK(initial.size() == 2U);
    const auto selected = std::find_if(
        initial.begin(), initial.end(), [&second](const auto &worker) {
            return worker.policy.tox_public_key == second.public_key;
        });
    const auto held = std::find_if(
        initial.begin(), initial.end(), [&first](const auto &worker) {
            return worker.policy.tox_public_key == first.public_key;
        });
    IOTOX_CHECK(selected != initial.end());
    IOTOX_CHECK(held != initial.end());
    IOTOX_CHECK(selected->transport_running);
    IOTOX_CHECK(!selected->qualification_held);
    IOTOX_CHECK(held->transport_running);
    IOTOX_CHECK(held->qualification_held);

    bool selected_ready = false;
    const auto selected_deadline = std::chrono::steady_clock::now() +
                                   std::chrono::seconds(2);
    while (std::chrono::steady_clock::now() < selected_deadline) {
        const auto snapshots = supervisor.snapshot();
        const auto current_selected = std::find_if(
            snapshots.begin(), snapshots.end(), [&second](const auto &worker) {
                return worker.policy.tox_public_key == second.public_key;
            });
        const auto current_held = std::find_if(
            snapshots.begin(), snapshots.end(), [&first](const auto &worker) {
                return worker.policy.tox_public_key == first.public_key;
            });
        selected_ready = current_selected != snapshots.end() &&
                         current_selected->application_ready;
        if (selected_ready) {
            IOTOX_CHECK(current_held != snapshots.end());
            IOTOX_CHECK(current_held->qualification_held);
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(selected_ready);
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    const auto during_hold = supervisor.snapshot();
    const auto still_held = std::find_if(
        during_hold.begin(), during_hold.end(), [&first](const auto &worker) {
            return worker.policy.tox_public_key == first.public_key;
        });
    IOTOX_CHECK(still_held != during_hold.end());
    IOTOX_CHECK(still_held->qualification_held);
    IOTOX_CHECK(!still_held->application_ready);

    bool both_ready = false;
    const auto both_deadline = std::chrono::steady_clock::now() +
                               std::chrono::seconds(4);
    while (std::chrono::steady_clock::now() < both_deadline) {
        const auto snapshots = supervisor.snapshot();
        both_ready = std::all_of(
            snapshots.begin(), snapshots.end(), [](const auto &worker) {
                return worker.application_ready;
            });
        if (both_ready) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(both_ready);
    const auto released = supervisor.snapshot();
    IOTOX_CHECK(std::none_of(
        released.begin(), released.end(), [](const auto &worker) {
            return worker.qualification_held;
        }));

    supervisor.stop();
    std::filesystem::remove_all(first.root, ignored);
}

IOTOX_TEST("route worker readiness qualification rejects a negative delay") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(mock_library, "readiness-negative");
    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = route_set_for(provisioned.public_key);
    config.session_incarnation = 3U;
    config.qualification_other_worker_delay = std::chrono::milliseconds(-1);
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    const auto started = supervisor.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker readiness qualification requires an auxiliary member") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(mock_library, "readiness-member");
    const auto set = route_set_for(provisioned.public_key);
    const auto make_config = [&](const iotox::routes::ToxPublicKey &target) {
        iotox::routes::WorkerSupervisor::Config config;
        config.transport_template.toxcore_library = mock_library;
        config.state_root = provisioned.root;
        config.route_set = set;
        config.session_incarnation = 4U;
        config.qualification_first_worker = target;
        config.qualification_other_worker_delay =
            std::chrono::milliseconds(1);
        return config;
    };
    {
        iotox::routes::WorkerSupervisor supervisor(
            make_config(set.coordinator_tox_public_key));
        const auto started = supervisor.start();
        IOTOX_CHECK(!started.ok());
        IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    }
    {
        iotox::routes::WorkerSupervisor supervisor(make_config(key(0x99U)));
        const auto started = supervisor.start();
        IOTOX_CHECK(!started.ok());
        IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    }
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker supervisor rejects cross-wired savedata") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(mock_library, "crosswire");
    const auto actual_path = iotox::routes::WorkerSupervisor::state_path_for(
        provisioned.root, provisioned.public_key);
    const auto wrong_key = key(0x91U);
    const auto wrong_path = iotox::routes::WorkerSupervisor::state_path_for(
        provisioned.root, wrong_key);
    std::filesystem::rename(actual_path, wrong_path);
    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = route_set_for(wrong_key);
    config.session_incarnation = 5U;
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    const auto started = supervisor.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.message().find("expected public key") !=
                std::string::npos);
    IOTOX_CHECK(!supervisor.running());
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("route worker freezes and sends one binding after confirmation") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(mock_library, "binding-send");
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        provisioned.root / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    auto set = route_set_for(provisioned.public_key);
    set.stable_device_principal = identity.value().public_key();
    auto signed_set = iotox::routes::sign_route_set(set, identity.value());
    IOTOX_CHECK(signed_set.ok());

    std::atomic<unsigned> factory_calls{0U};
    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = set;
    config.session_incarnation = 6U;
    config.sodium = &sodium.value();
    config.make_binding_frame =
        [&factory_calls, &identity, &sodium, signed_set, set](
            const iotox::routes::MemberPolicy &member,
            const iotox::protocol::PeerSessionSnapshot &session,
            std::uint64_t message_id) {
            ++factory_calls;
            return iotox::routes::make_route_binding_frame(
                signed_set.value(), set, member.tox_public_key, session,
                identity.value(), sodium.value(), message_id);
        };
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    IOTOX_CHECK(supervisor.start().ok());
    iotox::routes::WorkerSessionSnapshot observed;
    const auto deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < deadline) {
        const auto snapshots = supervisor.snapshot();
        IOTOX_CHECK(snapshots.size() == 1U);
        observed = snapshots.front();
        if (observed.local_binding_sent) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(observed.application_ready);
    IOTOX_CHECK(observed.local_binding_sent);
    IOTOX_CHECK(observed.local_binding_message_id != 0U);
    IOTOX_CHECK(!observed.remote_binding_authenticated);
    IOTOX_CHECK(factory_calls.load() == 1U);
    supervisor.stop();
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("private route worker waits for primary inventory and revokes with it") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(
        mock_library, "private-binding", 0x43U);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        provisioned.root / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());

    auto local_set = route_set_for(provisioned.public_key);
    local_set.stable_device_principal = identity.value().public_key();
    local_set.members.front().role = iotox::routes::Role::bulk;
    local_set.members.back().role =
        iotox::routes::Role::protected_route;
    auto signed_local = iotox::routes::sign_route_set(
        local_set, identity.value());
    IOTOX_CHECK(signed_local.ok());

    constexpr iotox::security::SigningSeed mock_seed{
        0x9D, 0x61, 0xB1, 0x9D, 0xEF, 0xFD, 0x5A, 0x60,
        0xBA, 0x84, 0x4A, 0xF4, 0x92, 0xEC, 0x2C, 0xC4,
        0x44, 0x49, 0xC5, 0x69, 0x7B, 0x32, 0x69, 0x19,
        0x70, 0x3B, 0xAC, 0x03, 0x1C, 0xAE, 0x7F, 0x60,
    };
    std::array<std::uint8_t, iotox::security::kDeviceIdentityFileBytes>
        mock_identity_bytes{};
    constexpr std::array<std::uint8_t, 8U> identity_magic{
        'I', 'O', 'T', 'O', 'X', 'I', 'D', '1'};
    std::copy(identity_magic.begin(), identity_magic.end(),
              mock_identity_bytes.begin());
    mock_identity_bytes[8U] = 1U;
    mock_identity_bytes[9U] = 1U;
    std::copy(mock_seed.begin(), mock_seed.end(),
              mock_identity_bytes.begin() + 16U);
    const auto remote_principal = mock_remote_principal();
    std::copy(remote_principal.begin(), remote_principal.end(),
              mock_identity_bytes.begin() + 48U);
    const auto mock_identity_path =
        provisioned.root / "mock-remote.identity";
    {
        std::ofstream output(
            mock_identity_path, std::ios::binary | std::ios::trunc);
        output.write(
            reinterpret_cast<const char *>(mock_identity_bytes.data()),
            static_cast<std::streamsize>(mock_identity_bytes.size()));
        IOTOX_CHECK(output.good());
    }
    IOTOX_CHECK(::chmod(
        mock_identity_path.c_str(), static_cast<mode_t>(0600)) == 0);
    auto mock_identity = iotox::security::DeviceIdentity::load(
        mock_identity_path, sodium.value());
    IOTOX_CHECK(mock_identity.ok());
    IOTOX_CHECK(mock_identity.value().public_key() ==
                mock_remote_principal());

    iotox::routes::RouteSet remote_set;
    remote_set.generation = 1U;
    remote_set.stable_device_principal = mock_remote_principal();
    remote_set.coordinator_tox_public_key = key(0x42U);
    remote_set.members = {
        {key(0x42U), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {key(0x43U), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 1U, 0U},
    };
    auto signed_remote = iotox::routes::sign_route_set(
        remote_set, mock_identity.value());
    IOTOX_CHECK(signed_remote.ok());
    auto remote_digest = iotox::routes::route_set_artifact_digest(
        signed_remote.value(), sodium.value());
    IOTOX_CHECK(remote_digest.ok());

    iotox::routes::PrivateRoutePrimaryContext context;
    context.inventory.route_set = remote_set;
    context.inventory.artifact_digest = remote_digest.value();
    context.session = private_primary_session(
        local_set.coordinator_tox_public_key);
    context.inventory.primary_friend_number =
        context.session.friend_number;
    context.inventory.primary_online_epoch =
        context.session.online_epoch;
    context.authority.friend_number = context.session.friend_number;
    context.authority.transport_public_key = context.session.public_key;
    context.authority.online_epoch = context.session.online_epoch;
    context.authority.connected = true;
    context.authority.feature_negotiated = true;
    context.authority.remote_authorized = true;
    context.authority.remote_principal = mock_remote_principal();
    auto primary_digest =
        iotox::security::authority_session_transcript_digest(
            context.session, sodium.value());
    IOTOX_CHECK(primary_digest.ok());
    context.authority.session_transcript_digest = primary_digest.value();

    std::atomic<unsigned> factory_calls{0U};
    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = local_set;
    config.session_incarnation = 61U;
    config.sodium = &sodium.value();
    config.make_private_binding_frame =
        [&factory_calls, &identity, &sodium, signed_local, local_set](
            const iotox::routes::MemberPolicy &member,
            const iotox::routes::PrivateRoutePrimaryContext &remote,
            const iotox::protocol::PeerSessionSnapshot &session,
            std::uint64_t message_id) {
            ++factory_calls;
            auto frame =
                iotox::routes::make_private_route_member_binding_frame(
                    signed_local.value(), local_set,
                    member.tox_public_key, remote.inventory,
                    remote.session, session, remote.authority,
                    identity.value(), sodium.value(), message_id);
            if (frame) {
                IOTOX_CHECK(frame.value().type ==
                    iotox::protocol::MessageType::
                        private_route_member_binding);
                IOTOX_CHECK(frame.value().payload.size() ==
                    iotox::routes::
                        kPrivateRouteMemberBindingArtifactBytes);
            }
            return frame;
        };
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    IOTOX_CHECK(supervisor.start().ok());

    iotox::routes::WorkerSessionSnapshot before_inventory;
    const auto application_deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(3);
    do {
        before_inventory = supervisor.snapshot().front();
        if (before_inventory.application_ready) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < application_deadline);
    IOTOX_CHECK(before_inventory.application_ready);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    before_inventory = supervisor.snapshot().front();
    IOTOX_CHECK(!before_inventory.local_binding_sent);
    IOTOX_CHECK(!before_inventory.remote_binding_authenticated);
    IOTOX_CHECK(factory_calls.load() == 0U);

    IOTOX_CHECK(supervisor.replace_private_route_contexts({context}).ok());
    iotox::routes::WorkerSessionSnapshot bound;
    const auto binding_deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(3);
    do {
        bound = supervisor.snapshot().front();
        if (bound.local_binding_sent &&
            bound.remote_binding_authenticated) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < binding_deadline);
    IOTOX_CHECK(bound.local_binding_sent);
    IOTOX_CHECK(bound.remote_binding_authenticated);
    IOTOX_CHECK(bound.remote_route_generation == remote_set.generation);
    IOTOX_CHECK(bound.remote_stable_principal ==
                remote_set.stable_device_principal);
    IOTOX_CHECK(bound.remote_coordinator_route_key ==
                remote_set.coordinator_tox_public_key);
    IOTOX_CHECK(bound.primary_authority_online_epoch ==
                context.session.online_epoch);
    IOTOX_CHECK(factory_calls.load() == 1U);

    // The primary edge can advance after the reciprocal auxiliary proof has
    // already arrived.  Replacing that context must retain and immediately
    // re-evaluate the proof instead of creating a one-shot exchange deadlock.
    auto advanced_context = context;
    ++advanced_context.session.online_epoch;
    advanced_context.inventory.primary_online_epoch =
        advanced_context.session.online_epoch;
    advanced_context.authority.online_epoch =
        advanced_context.session.online_epoch;
    auto advanced_primary_digest =
        iotox::security::authority_session_transcript_digest(
            advanced_context.session, sodium.value());
    IOTOX_CHECK(advanced_primary_digest.ok());
    advanced_context.authority.session_transcript_digest =
        advanced_primary_digest.value();
    IOTOX_CHECK(supervisor.replace_private_route_contexts(
        {advanced_context}).ok());
    auto rebased = supervisor.snapshot().front();
    IOTOX_CHECK(rebased.remote_binding_authenticated);
    IOTOX_CHECK(rebased.primary_authority_online_epoch ==
                advanced_context.session.online_epoch);
    const auto rebinding_deadline = std::chrono::steady_clock::now() +
        std::chrono::seconds(3);
    do {
        rebased = supervisor.snapshot().front();
        if (rebased.local_binding_sent &&
            rebased.remote_binding_authenticated &&
            factory_calls.load() == 2U) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < rebinding_deadline);
    IOTOX_CHECK(rebased.local_binding_sent);
    IOTOX_CHECK(rebased.remote_binding_authenticated);
    IOTOX_CHECK(rebased.primary_authority_online_epoch ==
                advanced_context.session.online_epoch);
    IOTOX_CHECK(factory_calls.load() == 2U);

    IOTOX_CHECK(supervisor.replace_private_route_contexts({}).ok());
    const auto revoked = supervisor.snapshot().front();
    IOTOX_CHECK(!revoked.local_binding_sent);
    IOTOX_CHECK(!revoked.remote_binding_authenticated);
    IOTOX_CHECK(revoked.remote_route_generation == 0U);

    supervisor.stop();
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}

IOTOX_TEST("authenticated bulk worker binds an explicit file ID through outgoing terminal truth") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    auto provisioned = provision_worker(
        mock_library, "explicit-send", 0x43U);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        provisioned.root / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());

    auto set = route_set_for(provisioned.public_key);
    set.stable_device_principal = identity.value().public_key();
    set.members.front().role = iotox::routes::Role::bulk;
    set.members.front().maximum_active_work = 2U;
    set.members.back().role = iotox::routes::Role::protected_route;
    auto signed_set = iotox::routes::sign_route_set(set, identity.value());
    IOTOX_CHECK(signed_set.ok());

    iotox::routes::WorkerSupervisor::Config config;
    config.transport_template.toxcore_library = mock_library;
    config.state_root = provisioned.root;
    config.route_set = set;
    config.session_incarnation = 7U;
    config.maximum_finite_file_bytes = 4096U;
    config.maximum_sync_frame_events = 1U;
    config.sync_frames_enabled = true;
    config.sync_content_frames_enabled = false;
    config.sodium = &sodium.value();
    config.make_binding_frame =
        [&identity, &sodium, signed_set, set](
            const iotox::routes::MemberPolicy &member,
            const iotox::protocol::PeerSessionSnapshot &session,
            std::uint64_t message_id) {
            return iotox::routes::make_route_binding_frame(
                signed_set.value(), set, member.tox_public_key, session,
                identity.value(), sodium.value(), message_id);
        };
    iotox::routes::WorkerSupervisor supervisor(std::move(config));
    IOTOX_CHECK(supervisor.set_sync_content_frames_enabled(true).ok());
    IOTOX_CHECK(supervisor.start().ok());
    IOTOX_CHECK(!supervisor.set_sync_content_frames_enabled(false).ok());
    iotox::routes::RemoteRouteTrust trust;
    trust.stable_device_principal = mock_remote_principal();
    trust.coordinator_tox_public_key = key(0x42U);
    trust.minimum_generation = 1U;
    trust.primary_online_epoch = 1U;
    IOTOX_CHECK(supervisor.replace_remote_trust({trust}).ok());

    iotox::routes::WorkerSessionSnapshot ready;
    const auto ready_deadline = std::chrono::steady_clock::now() +
                                std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < ready_deadline) {
        const auto snapshots = supervisor.snapshot();
        IOTOX_CHECK(snapshots.size() == 1U);
        ready = snapshots.front();
        if (ready.remote_binding_authenticated) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(ready.application_ready);
    IOTOX_CHECK(ready.remote_binding_authenticated);
    IOTOX_CHECK(ready.remote_stable_principal == mock_remote_principal());
    IOTOX_CHECK(ready.remote_coordinator_route_key ==
                trust.coordinator_tox_public_key);
    IOTOX_CHECK(ready.primary_authority_online_epoch ==
                trust.primary_online_epoch);
    IOTOX_CHECK(ready.range_transfer_negotiated);
    IOTOX_CHECK(ready.content_transfer_negotiated);

    const auto source = std::filesystem::absolute(
        provisioned.root / "immutable-object.bin");
    {
        std::ofstream output(source, std::ios::binary | std::ios::trunc);
        output << "immutable-worker-object";
        IOTOX_CHECK(output.good());
    }
    iotox::FileId transfer_id{};
    transfer_id.fill(0xA6U);
    auto offered = supervisor.send_path_with_file_id(
        provisioned.public_key, ready.worker_id, source, transfer_id);
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());
    IOTOX_CHECK(offered.value().direction ==
                iotox::FileTransferDirection::outgoing);
    IOTOX_CHECK(offered.value().file_id == transfer_id);

    std::optional<iotox::routes::WorkerTransferTerminalEvent> terminal;
    const auto terminal_deadline = std::chrono::steady_clock::now() +
                                   std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < terminal_deadline) {
        auto events = supervisor.take_transfer_terminal_events(4U);
        IOTOX_CHECK_MSG(events.ok(), events.status().message());
        if (!events.value().empty()) {
            IOTOX_CHECK(events.value().size() == 1U);
            terminal = std::move(events.value().front());
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(terminal.has_value());
    IOTOX_CHECK(terminal->route_key == provisioned.public_key);
    IOTOX_CHECK(terminal->worker_id == ready.worker_id);
    IOTOX_CHECK(terminal->outcome ==
                iotox::routes::WorkerTransferOutcome::completed);
    IOTOX_CHECK(terminal->failure == iotox::ErrorCode::ok);
    IOTOX_CHECK(terminal->transfer.direction ==
                iotox::FileTransferDirection::outgoing);
    IOTOX_CHECK(terminal->transfer.file_id == transfer_id);
    IOTOX_CHECK(supervisor.transfers().empty());

    iotox::FileId range_transfer_id{};
    range_transfer_id.fill(0xA7U);
    const std::vector<iotox::FileByteRange> source_ranges{
        {0U, 4U}, {10U, 3U}};
    auto range_offered = supervisor.send_path_ranges_with_file_id(
        provisioned.public_key, ready.worker_id, source, source_ranges,
        range_transfer_id);
    IOTOX_CHECK_MSG(range_offered.ok(), range_offered.status().message());
    IOTOX_CHECK(range_offered.value().direction ==
                iotox::FileTransferDirection::outgoing);
    IOTOX_CHECK(range_offered.value().file_id == range_transfer_id);
    IOTOX_CHECK(range_offered.value().file_size == 7U);
    terminal.reset();
    const auto range_terminal_deadline = std::chrono::steady_clock::now() +
                                         std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < range_terminal_deadline) {
        auto events = supervisor.take_transfer_terminal_events(4U);
        IOTOX_CHECK_MSG(events.ok(), events.status().message());
        if (!events.value().empty()) {
            IOTOX_CHECK(events.value().size() == 1U);
            terminal = std::move(events.value().front());
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    IOTOX_CHECK(terminal.has_value());
    IOTOX_CHECK(terminal->outcome ==
                iotox::routes::WorkerTransferOutcome::completed);
    IOTOX_CHECK(terminal->transfer.file_id == range_transfer_id);
    IOTOX_CHECK(terminal->transfer.file_size == 7U);
    IOTOX_CHECK(supervisor.transfers().empty());

    iotox::sync::SyncObjectResult result;
    result.status = iotox::sync::SyncObjectResultStatus::object_absent;
    result.kind = iotox::sync::SyncObjectKind::artifact;
    result.head_record.fill(0x37U);
    result.transfer_id.fill(0x91U);
    auto first_frame = iotox::sync::make_sync_object_result_frame(
        result, 0x8101U, 0x7101U);
    auto second_frame = iotox::sync::make_sync_object_result_frame(
        result, 0x8102U, 0x7102U);
    auto third_frame = iotox::sync::make_sync_object_result_frame(
        result, 0x8103U, 0x7103U);
    IOTOX_CHECK(first_frame.ok());
    IOTOX_CHECK(second_frame.ok());
    IOTOX_CHECK(third_frame.ok());
    IOTOX_CHECK(!supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id + 1U,
        first_frame.value()).ok());
    iotox::protocol::Frame forbidden;
    forbidden.type = iotox::protocol::MessageType::sync_head_request;
    IOTOX_CHECK(!supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id, forbidden).ok());

    IOTOX_CHECK(supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        first_frame.value()).ok());
    const auto first_queue_deadline = std::chrono::steady_clock::now() +
                                      std::chrono::seconds(3);
    iotox::routes::WorkerSessionSnapshot application_snapshot;
    do {
        application_snapshot = supervisor.snapshot().front();
        if (application_snapshot.sync_frame_events_queued == 1U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < first_queue_deadline);
    IOTOX_CHECK(application_snapshot.sync_frame_events_queued == 1U);
    IOTOX_CHECK(application_snapshot.sync_frames_received == 1U);

    IOTOX_CHECK(supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        second_frame.value()).ok());
    const auto rejection_deadline = std::chrono::steady_clock::now() +
                                    std::chrono::seconds(3);
    do {
        application_snapshot = supervisor.snapshot().front();
        if (application_snapshot.sync_frames_rejected == 1U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < rejection_deadline);
    IOTOX_CHECK(application_snapshot.sync_frame_events_queued == 1U);
    IOTOX_CHECK(application_snapshot.sync_frames_received == 1U);
    IOTOX_CHECK(application_snapshot.sync_frames_rejected == 1U);
    IOTOX_CHECK(!supervisor.take_sync_frame_events(0U).ok());
    auto application_events = supervisor.take_sync_frame_events(1U);
    IOTOX_CHECK(application_events.ok());
    IOTOX_CHECK(application_events.value().size() == 1U);
    const auto &application = application_events.value().front();
    IOTOX_CHECK(application.route_key == provisioned.public_key);
    IOTOX_CHECK(application.worker_id == ready.worker_id);
    IOTOX_CHECK(application.friend_number == ready.friend_number);
    IOTOX_CHECK(application.online_epoch == ready.online_epoch);
    IOTOX_CHECK(application.remote_route_generation == 1U);
    IOTOX_CHECK(application.remote_stable_principal ==
                mock_remote_principal());
    IOTOX_CHECK(application.remote_coordinator_route_key ==
                trust.coordinator_tox_public_key);
    IOTOX_CHECK(application.primary_authority_online_epoch ==
                trust.primary_online_epoch);
    IOTOX_CHECK(application.frame.message_id == 0x8101U);
    IOTOX_CHECK(application.frame.correlation_id == 0x7101U);
    IOTOX_CHECK(application.frame.type ==
                iotox::protocol::MessageType::sync_object_result);

    iotox::sync::SyncRangeResult range_result;
    range_result.status = iotox::sync::SyncRangeResultStatus::offered;
    range_result.head_record.fill(0x38U);
    range_result.transfer_id.fill(0x92U);
    auto range_frame = iotox::sync::make_sync_range_result_frame(
        range_result, 0x8201U, 0x7201U);
    IOTOX_CHECK(range_frame.ok());
    IOTOX_CHECK(supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        range_frame.value()).ok());
    const auto range_queue_deadline = std::chrono::steady_clock::now() +
                                      std::chrono::seconds(3);
    do {
        application_snapshot = supervisor.snapshot().front();
        if (application_snapshot.sync_frame_events_queued == 1U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < range_queue_deadline);
    application_events = supervisor.take_sync_frame_events(1U);
    IOTOX_CHECK(application_events.ok());
    IOTOX_CHECK(application_events.value().size() == 1U);
    IOTOX_CHECK(application_events.value().front().frame.type ==
                iotox::protocol::MessageType::sync_range_result);
    IOTOX_CHECK(application_events.value().front().frame.message_id ==
                0x8201U);

    iotox::sync::SyncContentAvailabilityResult content_result;
    content_result.status =
        iotox::sync::SyncContentAvailabilityResultStatus::available;
    content_result.kind =
        iotox::sync::SyncContentObjectKind::artifact_chunk;
    content_result.head_record.fill(0x39U);
    content_result.first_object = 4U;
    content_result.object_count = 3U;
    content_result.availability = {0x05U};
    auto content_frame =
        iotox::sync::make_sync_content_availability_result_frame(
            content_result, 0x8301U, 0x7301U);
    IOTOX_CHECK(content_frame.ok());
    IOTOX_CHECK(supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        content_frame.value()).ok());
    const auto content_queue_deadline = std::chrono::steady_clock::now() +
                                        std::chrono::seconds(3);
    do {
        application_snapshot = supervisor.snapshot().front();
        if (application_snapshot.sync_frame_events_queued == 1U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < content_queue_deadline);
    application_events = supervisor.take_sync_frame_events(1U);
    IOTOX_CHECK(application_events.ok());
    IOTOX_CHECK(application_events.value().size() == 1U);
    IOTOX_CHECK(application_events.value().front().frame.type ==
                iotox::protocol::MessageType::
                    sync_content_availability_result);
    IOTOX_CHECK(application_events.value().front().frame.message_id ==
                0x8301U);

    IOTOX_CHECK(supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        third_frame.value()).ok());
    const auto purge_deadline = std::chrono::steady_clock::now() +
                                std::chrono::seconds(3);
    do {
        application_snapshot = supervisor.snapshot().front();
        if (application_snapshot.sync_frame_events_queued == 1U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    } while (std::chrono::steady_clock::now() < purge_deadline);
    IOTOX_CHECK(application_snapshot.sync_frame_events_queued == 1U);
    IOTOX_CHECK(supervisor.replace_remote_trust({}).ok());
    application_events = supervisor.take_sync_frame_events(1U);
    IOTOX_CHECK(application_events.ok());
    IOTOX_CHECK(application_events.value().empty());
    IOTOX_CHECK(!supervisor.send_sync_frame(
        provisioned.public_key, ready.worker_id,
        third_frame.value()).ok());

    IOTOX_CHECK(!supervisor.stop_worker_for_qualification(
        provisioned.public_key, ready.worker_id + 1U).ok());
    IOTOX_CHECK(supervisor.stop_worker_for_qualification(
        provisioned.public_key, ready.worker_id).ok());
    const auto stopped = supervisor.snapshot();
    IOTOX_CHECK(stopped.size() == 1U);
    IOTOX_CHECK(!stopped.front().transport_running);
    IOTOX_CHECK(stopped.front().last_failure ==
                iotox::routes::Failure::transport);
    IOTOX_CHECK(!supervisor.stop_worker_for_qualification(
        provisioned.public_key, ready.worker_id).ok());

    auto restarted = supervisor.restart_worker_for_qualification(
        provisioned.public_key, ready.worker_id);
    IOTOX_CHECK_MSG(restarted.ok(), restarted.status().message());
    IOTOX_CHECK(restarted.value() != 0U);
    IOTOX_CHECK(restarted.value() != ready.worker_id);
    const auto recovered = supervisor.snapshot();
    IOTOX_CHECK(recovered.size() == 1U);
    IOTOX_CHECK(recovered.front().transport_running);
    IOTOX_CHECK(recovered.front().worker_id == restarted.value());
    IOTOX_CHECK(!supervisor.restart_worker_for_qualification(
        provisioned.public_key, restarted.value()).ok());

    supervisor.stop();
    std::error_code ignored;
    std::filesystem::remove_all(provisioned.root, ignored);
}
