#include "test_harness.hpp"

#include "iotox/protocol/frame.hpp"
#include "iotox/state_store.hpp"
#include "iotox/transport.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <future>
#include <optional>
#include <string>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <vector>

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

std::filesystem::path unique_transport_directory(std::string_view suffix) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("iotox-transport-test-" + std::to_string(static_cast<long long>(::getpid())) +
            "-" + std::to_string(sequence.fetch_add(1U)) + "-" + std::string(suffix));
}

}  // namespace

IOTOX_TEST("transport validates the file callback pacing envelope") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const auto rejects = [mock_library](
                             std::size_t maximum,
                             std::size_t high,
                             std::size_t low,
                             std::chrono::microseconds hold,
                             std::size_t resume_batch = 1U) {
        iotox::ToxTransport::Config config;
        config.toxcore_library = mock_library;
        config.max_pending_events = maximum;
        config.file_pacing_high_watermark = high;
        config.file_pacing_low_watermark = low;
        config.file_pacing_minimum_hold = hold;
        config.file_pacing_resume_batch_limit = resume_batch;
        config.save_state_after_mutation = false;
        config.save_state_on_stop = false;
        iotox::ToxTransport transport(config);
        const iotox::Status status = transport.start();
        transport.stop();
        return status.code() == iotox::ErrorCode::invalid_argument;
    };

    IOTOX_CHECK(rejects(64U, 64U, 16U, std::chrono::milliseconds(5)));
    IOTOX_CHECK(rejects(128U, 64U, 64U, std::chrono::milliseconds(5)));
    IOTOX_CHECK(rejects(128U, 64U, 16U, std::chrono::microseconds(99)));
    IOTOX_CHECK(rejects(128U, 64U, 16U, std::chrono::seconds(2)));
    IOTOX_CHECK(rejects(
        128U, 64U, 16U, std::chrono::milliseconds(5), 0U));
    IOTOX_CHECK(rejects(
        128U, 64U, 16U, std::chrono::milliseconds(5), 129U));
}

IOTOX_TEST("transport expected identity is fenced before network startup") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const auto directory = unique_transport_directory("expected-identity");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    std::array<std::uint8_t, iotox::toxcore::abi::kPublicKeySize> wrong{};
    wrong.fill(0xFFU);
    config.expected_public_key = wrong;
    iotox::toxcore::BootstrapEndpoint endpoint;
    endpoint.host = "must-not-start.test";
    endpoint.port = 33445U;
    endpoint.public_key.fill(0xA5U);
    config.bootstrap_nodes.push_back(endpoint);

    iotox::ToxTransport transport(config);
    const auto started = transport.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(started.message().find("expected public key") !=
                std::string::npos);
    IOTOX_CHECK(!transport.running());
    IOTOX_CHECK(transport.address_hex().empty());
    IOTOX_CHECK(!std::filesystem::exists(config.state_path));
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("native TCP-only mode disables every UDP discovery seam") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const auto directory = unique_transport_directory("tcp-only");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    std::filesystem::create_directories(directory);
    const auto audit = directory / "options.audit";
    ScopedEnvironment audit_environment(
        "IOTOX_MOCK_OPTIONS_AUDIT", audit.c_str());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    config.native_udp_enabled = false;
    iotox::ToxTransport transport(config);
    const auto started = transport.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    transport.stop();

    std::ifstream input(audit);
    IOTOX_CHECK(input.is_open());
    std::string text;
    IOTOX_CHECK(static_cast<bool>(std::getline(input, text)));
    text.push_back('\n');
    IOTOX_CHECK(input.peek() == std::char_traits<char>::eof());
    IOTOX_CHECK(text ==
                "udp=0 local-discovery=0 dht-announcements=0 hole-punching=0 proxy=0 proxy-host= proxy-port=0 disable-dns=0\n");
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("offline transport retries configured TCP relays") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const auto directory = unique_transport_directory("relay-retry");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    std::filesystem::create_directories(directory);
    ScopedEnvironment suppress_connection(
        "IOTOX_MOCK_SUPPRESS_SELF_CONNECTION", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    config.native_udp_enabled = false;
    config.bootstrap_retry_interval = std::chrono::milliseconds(10);
    iotox::toxcore::BootstrapEndpoint relay;
    relay.host = "relay.test";
    relay.port = 33445U;
    relay.public_key.fill(0x5AU);
    config.tcp_relays.push_back(relay);

    iotox::ToxTransport transport(config);
    const auto started = transport.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    bool saw_startup = false;
    bool saw_retry = false;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (std::chrono::steady_clock::now() < deadline && !saw_retry) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
            if (event->kind != iotox::TransportEventKind::tcp_relay) {
                continue;
            }
            saw_startup = saw_startup || event->message.starts_with("startup accepted ");
            saw_retry = saw_retry || event->message.starts_with("retry accepted ");
        }
    }
    IOTOX_CHECK(saw_startup);
    IOTOX_CHECK(saw_retry);
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("C++ Tox owner thread integrates against the runtime ABI") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr, "test runner did not provide the mock c-toxcore path");

    const std::filesystem::path directory =
        std::filesystem::temp_directory_path() /
        ("iotox-transport-test-" + std::to_string(static_cast<long long>(::getpid())));
    const std::filesystem::path state_path = directory / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = state_path;
    iotox::toxcore::BootstrapEndpoint endpoint;
    endpoint.host = "bootstrap.test";
    endpoint.port = 33445U;
    endpoint.public_key.fill(0xA5U);
    config.bootstrap_nodes.push_back(endpoint);
    endpoint.host = "relay.test";
    endpoint.port = 443U;
    endpoint.public_key.fill(0x5AU);
    config.tcp_relays.push_back(endpoint);

    std::string first_address;
    {
        iotox::ToxTransport transport(config);
        const iotox::Status started = transport.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        IOTOX_CHECK(transport.running());
        first_address = transport.address_hex();
        IOTOX_CHECK(first_address.size() == 76U);

        bool saw_bootstrap = false;
        bool saw_relay = false;
        const auto setup_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (std::chrono::steady_clock::now() < setup_deadline &&
               (!saw_bootstrap || !saw_relay)) {
            if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
                saw_bootstrap = saw_bootstrap ||
                                event->kind == iotox::TransportEventKind::bootstrap;
                saw_relay = saw_relay ||
                            event->kind == iotox::TransportEventKind::tcp_relay;
            }
        }
        IOTOX_CHECK(saw_bootstrap);
        IOTOX_CHECK(saw_relay);

        std::vector<std::uint8_t> key(32U, 0x42U);
        auto friend_number = transport.accept_friend(key);
        IOTOX_CHECK_MSG(friend_number.ok(), friend_number.status().message());
        IOTOX_CHECK(friend_number.value() == 0U);

        iotox::protocol::Frame frame;
        frame.type = iotox::protocol::MessageType::hello;
        frame.message_id = 1001;
        frame.payload = {'j', 'u', 's', 't', '-', 'w', 'e', 'r', 'x'};
        auto packet = iotox::protocol::encode(frame);
        IOTOX_CHECK(packet);
        const iotox::Status sent = transport.send_sensitive_lossless(
            friend_number.value(), packet.value());
        IOTOX_CHECK_MSG(sent.ok(), sent.message());

        bool received_echo = false;
        const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (std::chrono::steady_clock::now() < deadline && !received_echo) {
            if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
                if (event->kind == iotox::TransportEventKind::lossless_packet) {
                    IOTOX_CHECK(event->friend_number == friend_number.value());
                    IOTOX_CHECK(event->data == packet.value());
                    received_echo = true;
                }
            }
        }
        IOTOX_CHECK(received_echo);

        const std::vector<std::uint8_t> reserved_lossy{0xC0U, 1U};
        const iotox::Status reserved_status = transport.send_lossy(
            friend_number.value(), reserved_lossy,
            iotox::TransportTrafficClass::interactive);
        IOTOX_CHECK(!reserved_status.ok());
        IOTOX_CHECK(
            reserved_status.code() == iotox::ErrorCode::invalid_argument);

        const std::vector<std::uint8_t> lossy{0xC8U, 1U, 2U, 3U};
        IOTOX_CHECK(transport.send_lossy(
            friend_number.value(), lossy,
            iotox::TransportTrafficClass::interactive).ok());
        bool received_lossy = false;
        const auto lossy_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (std::chrono::steady_clock::now() < lossy_deadline &&
               !received_lossy) {
            if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
                if (event->kind == iotox::TransportEventKind::lossy_packet) {
                    IOTOX_CHECK(event->friend_number == friend_number.value());
                    IOTOX_CHECK(event->data == lossy);
                    received_lossy = true;
                }
            }
        }
        IOTOX_CHECK(received_lossy);
        transport.stop();
    }

    IOTOX_CHECK(std::filesystem::exists(state_path));
    IOTOX_CHECK(std::filesystem::file_size(state_path) > 0U);

    {
        iotox::ToxTransport transport(config);
        const iotox::Status started = transport.start();
        IOTOX_CHECK_MSG(started.ok(), started.message());
        IOTOX_CHECK(transport.running());
        IOTOX_CHECK(transport.address_hex() == first_address);
        transport.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("lossless packet errors preserve retry and peer semantics") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr,
                    "test runner did not provide the mock c-toxcore path");

    const std::filesystem::path directory =
        unique_transport_directory("custom-packet-errors");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    ScopedEnvironment sendq_once(
        "IOTOX_MOCK_LOSSLESS_SENDQ_FAILURES", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());

    std::vector<std::uint8_t> key(32U, 0x51U);
    auto peer = transport.accept_friend(key);
    IOTOX_CHECK(peer);

    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::hello;
    frame.message_id = 901U;
    frame.payload = {'q'};
    auto packet = iotox::protocol::encode(frame);
    IOTOX_CHECK(packet);

    const iotox::Status pressured =
        transport.send_lossless(peer.value(), packet.value());
    IOTOX_CHECK(!pressured.ok());
    IOTOX_CHECK(pressured.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(pressured.message().find("retry after iteration") !=
                std::string::npos);

    IOTOX_CHECK(transport.send_lossless(peer.value(), packet.value()).ok());
    const iotox::Status missing =
        transport.send_lossless(peer.value() + 99U, packet.value());
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.code() == iotox::ErrorCode::not_found);
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("production Tox I2P requires the strict SOCKS topology") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.network = {iotox::TransportKind::tox, iotox::ToxRoute::i2p};
    config.save_state_on_stop = false;

    iotox::ToxTransport transport(config);
    const iotox::Status started = transport.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("Tox Tor installs one strict SOCKS5 and no native discovery seams") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const auto directory = unique_transport_directory("tox-tor-options");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    std::filesystem::create_directories(directory);
    const auto audit = directory / "options.audit";
    ScopedEnvironment audit_environment(
        "IOTOX_MOCK_OPTIONS_AUDIT", audit.c_str());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    config.network = {iotox::TransportKind::tox, iotox::ToxRoute::tor};
    config.native_udp_enabled = false;
    config.socks5_proxy = iotox::Socks5ProxyEndpoint{"127.0.0.1", 9050U};
    iotox::toxcore::BootstrapEndpoint relay;
    relay.host = "192.0.2.44";
    relay.port = 33445U;
    relay.public_key.fill(0x6BU);
    config.bootstrap_nodes.push_back(relay);
    config.tcp_relays.push_back(relay);

    iotox::ToxTransport transport(config);
    const auto started = transport.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    bool relay_configured = false;
    bool bootstrap_observed = false;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (std::chrono::steady_clock::now() < deadline &&
           !(relay_configured && bootstrap_observed)) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
            relay_configured = relay_configured ||
                event->kind == iotox::TransportEventKind::tcp_relay;
            bootstrap_observed = bootstrap_observed ||
                event->kind == iotox::TransportEventKind::bootstrap;
        }
    }
    IOTOX_CHECK(relay_configured);
    IOTOX_CHECK(bootstrap_observed);
    transport.stop();

    std::ifstream input(audit);
    IOTOX_CHECK(input.is_open());
    std::string text;
    IOTOX_CHECK(static_cast<bool>(std::getline(input, text)));
    text.push_back('\n');
    IOTOX_CHECK(input.peek() == std::char_traits<char>::eof());
    IOTOX_CHECK(text ==
                "udp=0 local-discovery=0 dht-announcements=0 hole-punching=0 proxy=2 proxy-host=127.0.0.1 proxy-port=9050 disable-dns=1\n");
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("Tox Tor rejects every incomplete or leak-prone topology") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    iotox::ToxTransport::Config exact;
    exact.toxcore_library = mock_library;
    exact.network = {iotox::TransportKind::tox, iotox::ToxRoute::tor};
    exact.native_udp_enabled = false;
    exact.socks5_proxy = iotox::Socks5ProxyEndpoint{"127.0.0.1", 9050U};
    iotox::toxcore::BootstrapEndpoint relay;
    relay.host = "192.0.2.44";
    relay.port = 33445U;
    relay.public_key.fill(0x7CU);
    exact.bootstrap_nodes.push_back(relay);
    exact.tcp_relays.push_back(relay);
    IOTOX_CHECK(iotox::ToxTransport::validate_route_config(exact).ok());

    const auto rejected = [](iotox::ToxTransport::Config candidate) {
        return !iotox::ToxTransport::validate_route_config(candidate).ok();
    };
    auto missing_proxy = exact;
    missing_proxy.socks5_proxy.reset();
    IOTOX_CHECK(rejected(missing_proxy));
    auto hostname_proxy = exact;
    hostname_proxy.socks5_proxy->host = "localhost";
    IOTOX_CHECK(rejected(hostname_proxy));
    auto udp = exact;
    udp.native_udp_enabled = true;
    IOTOX_CHECK(rejected(udp));
    auto no_bootstrap = exact;
    no_bootstrap.bootstrap_nodes.clear();
    IOTOX_CHECK(rejected(no_bootstrap));
    auto hostname_bootstrap = exact;
    hostname_bootstrap.bootstrap_nodes.front().host = "bootstrap.example";
    IOTOX_CHECK(rejected(hostname_bootstrap));
    auto no_relay = exact;
    no_relay.tcp_relays.clear();
    IOTOX_CHECK(rejected(no_relay));
    auto hostname_relay = exact;
    hostname_relay.tcp_relays.front().host = "relay.example";
    IOTOX_CHECK(rejected(hostname_relay));
    auto native_proxy = exact;
    native_proxy.network =
        {iotox::TransportKind::tox, iotox::ToxRoute::native};
    IOTOX_CHECK(rejected(native_proxy));
}

IOTOX_TEST("Tox I2P and its construction alias share one strict SOCKS topology") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const auto directory =
        unique_transport_directory("tox-i2p-construction-options");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    std::filesystem::create_directories(directory);
    const auto audit = directory / "options.audit";
    ScopedEnvironment audit_environment(
        "IOTOX_MOCK_OPTIONS_AUDIT", audit.c_str());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.tox-i2p.toxsave";
    config.network = {
        iotox::TransportKind::tox,
        iotox::ToxRoute::i2p_construction};
    config.native_udp_enabled = false;
    config.socks5_proxy =
        iotox::Socks5ProxyEndpoint{"127.0.0.1", 17656U};
    iotox::toxcore::BootstrapEndpoint relay;
    relay.host = "192.0.2.45";
    relay.port = 33445U;
    relay.public_key.fill(0x6CU);
    config.bootstrap_nodes.push_back(relay);
    config.tcp_relays.push_back(relay);

    IOTOX_CHECK(iotox::ToxTransport::validate_route_config(config).ok());
    iotox::ToxTransport transport(config);
    const auto started = transport.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    transport.stop();

    config.network = {iotox::TransportKind::tox, iotox::ToxRoute::i2p};
    IOTOX_CHECK(iotox::ToxTransport::validate_route_config(config).ok());
    iotox::ToxTransport production(config);
    const auto production_started = production.start();
    IOTOX_CHECK_MSG(production_started.ok(), production_started.message());
    production.stop();

    std::ifstream input(audit);
    IOTOX_CHECK(input.is_open());
    std::string construction_text;
    IOTOX_CHECK(static_cast<bool>(std::getline(input, construction_text)));
    construction_text.push_back('\n');
    std::string production_text;
    IOTOX_CHECK(static_cast<bool>(std::getline(input, production_text)));
    production_text.push_back('\n');
    IOTOX_CHECK(input.peek() == std::char_traits<char>::eof());
    IOTOX_CHECK(construction_text ==
                "udp=0 local-discovery=0 dht-announcements=0 hole-punching=0 proxy=2 proxy-host=127.0.0.1 proxy-port=17656 disable-dns=1\n");
    IOTOX_CHECK(production_text == construction_text);
    std::filesystem::remove_all(directory, ignored);
}


IOTOX_TEST("transport friendship lifecycle is listable, removable, and persistent") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory = unique_transport_directory("friends");
    const std::filesystem::path state = directory / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = state;

    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK(transport.start().ok());

        std::vector<std::uint8_t> accepted_key(32U, 0x41U);
        auto accepted = transport.accept_friend(accepted_key);
        IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
        IOTOX_CHECK(accepted.value() == 0U);

        std::vector<std::uint8_t> address(38U, 0x52U);
        auto requested = transport.request_friend(address, {'h', 'e', 'l', 'l', 'o'});
        IOTOX_CHECK_MSG(requested.ok(), requested.status().message());
        IOTOX_CHECK(requested.value() == 1U);

        auto listed = transport.list_friends();
        IOTOX_CHECK_MSG(listed.ok(), listed.status().message());
        IOTOX_CHECK(listed.value().size() == 2U);
        IOTOX_CHECK(listed.value()[0].friend_number == 0U);
        IOTOX_CHECK(listed.value()[0].public_key.front() == 0x41U);
        IOTOX_CHECK(listed.value()[1].friend_number == 1U);
        IOTOX_CHECK(listed.value()[1].public_key.front() == 0x52U);

        IOTOX_CHECK(transport.remove_friend(0U).ok());
        listed = transport.list_friends();
        IOTOX_CHECK(listed.ok());
        IOTOX_CHECK(listed.value().size() == 1U);
        IOTOX_CHECK(listed.value().front().friend_number == 1U);

        // c-toxcore may reuse a removed friend-number gap. Key-bound removal
        // performs lookup and deletion in one owner-thread turn, so a delayed
        // caller cannot accidentally delete whichever peer later occupies a
        // numeric handle it observed earlier.
        std::vector<std::uint8_t> replacement_key(32U, 0x63U);
        auto replacement = transport.accept_friend(replacement_key);
        IOTOX_CHECK_MSG(replacement.ok(), replacement.status().message());
        IOTOX_CHECK(replacement.value() == 0U);
        auto removed_by_key =
            transport.remove_friend_by_public_key(replacement_key);
        IOTOX_CHECK_MSG(
            removed_by_key.ok(), removed_by_key.status().message());
        IOTOX_CHECK(removed_by_key.value() == 0U);

        bool saw_key_bound_removal = false;
        const auto removal_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        while (std::chrono::steady_clock::now() < removal_deadline) {
            auto event =
                transport.poll_event(std::chrono::milliseconds(50));
            if (!event ||
                event->kind != iotox::TransportEventKind::friend_removed ||
                event->friend_number != 0U ||
                event->public_key.size() != replacement_key.size()) {
                continue;
            }
            saw_key_bound_removal = std::all_of(
                event->public_key.begin(), event->public_key.end(),
                [](std::uint8_t byte) { return byte == 0x63U; });
            if (saw_key_bound_removal) {
                break;
            }
        }
        IOTOX_CHECK(saw_key_bound_removal);

        auto duplicate_key_removal =
            transport.remove_friend_by_public_key(replacement_key);
        IOTOX_CHECK(!duplicate_key_removal.ok());
        IOTOX_CHECK(
            duplicate_key_removal.status().code() ==
            iotox::ErrorCode::not_found);
        transport.stop();
    }

    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK(transport.start().ok());
        auto listed = transport.list_friends();
        IOTOX_CHECK_MSG(listed.ok(), listed.status().message());
        IOTOX_CHECK(listed.value().size() == 1U);
        IOTOX_CHECK(listed.value().front().friend_number == 1U);
        IOTOX_CHECK(listed.value().front().public_key.front() == 0x52U);
        transport.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("bounded owner queue cancels only operations that have not begun") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    ScopedEnvironment delay("IOTOX_MOCK_SEND_DELAY_MS", "300");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_on_stop = false;
    config.owner_command_timeout = std::chrono::milliseconds(100);
    config.max_pending_commands = 1U;

    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x61U));
    IOTOX_CHECK(peer.ok());

    const std::vector<std::uint8_t> packet{69U, 1U};
    iotox::Status first_status;
    iotox::Status second_status;

    std::thread first([&] { first_status = transport.send_lossless(peer.value(), packet); });
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
    std::thread second([&] {
        second_status = transport.send_sensitive_lossless(
            peer.value(), packet);
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(20));

    const iotox::Status third_status = transport.send_sensitive_lossless(
        peer.value(), packet);
    IOTOX_CHECK(!third_status.ok());
    IOTOX_CHECK(third_status.code() == iotox::ErrorCode::resource_exhausted);

    second.join();
    first.join();
    IOTOX_CHECK(first_status.ok());
    IOTOX_CHECK(!second_status.ok());
    IOTOX_CHECK(second_status.code() == iotox::ErrorCode::timeout);

    const auto settle_deadline = std::chrono::steady_clock::now() + std::chrono::seconds(1);
    while (transport.stats().pending_commands != 0U &&
           std::chrono::steady_clock::now() < settle_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    IOTOX_CHECK(transport.stats().pending_commands == 0U);
    transport.stop();
}

IOTOX_TEST("owner scheduler advances interactive work ahead of queued control and bulk") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment delay("IOTOX_MOCK_SEND_DELAY_MS", "80");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_on_stop = false;
    config.owner_command_timeout = std::chrono::seconds(2);
    config.max_pending_commands = 8U;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x62U));
    IOTOX_CHECK(peer.ok());

    iotox::Status first_status;
    iotox::Status bulk_status;
    iotox::Status control_status;
    iotox::Status interactive_status;
    const std::vector<std::uint8_t> first{69U, 1U};
    const std::vector<std::uint8_t> bulk{69U, 2U};
    const std::vector<std::uint8_t> control{69U, 3U};
    const std::vector<std::uint8_t> interactive{69U, 4U};

    std::thread first_thread([&] {
        first_status = transport.send_lossless(
            peer.value(), first, iotox::TransportTrafficClass::control);
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    std::thread bulk_thread([&] {
        bulk_status = transport.send_lossless(
            peer.value(), bulk, iotox::TransportTrafficClass::bulk);
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    std::thread control_thread([&] {
        control_status = transport.send_lossless(
            peer.value(), control, iotox::TransportTrafficClass::control);
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    std::thread interactive_thread([&] {
        interactive_status = transport.send_lossless(
            peer.value(), interactive,
            iotox::TransportTrafficClass::interactive);
    });

    first_thread.join();
    bulk_thread.join();
    control_thread.join();
    interactive_thread.join();
    IOTOX_CHECK(first_status.ok());
    IOTOX_CHECK(bulk_status.ok());
    IOTOX_CHECK(control_status.ok());
    IOTOX_CHECK(interactive_status.ok());

    std::vector<std::uint8_t> observed;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (observed.size() < 4U &&
           std::chrono::steady_clock::now() < deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(20));
        if (event && event->kind == iotox::TransportEventKind::lossless_packet &&
            event->data.size() == 2U && event->data.front() == 69U) {
            observed.push_back(event->data[1U]);
        }
    }
    IOTOX_CHECK(observed == std::vector<std::uint8_t>({1U, 4U, 3U, 2U}));
    const iotox::TransportStats stats = transport.stats();
    IOTOX_CHECK(stats.pending_commands == 0U);
    IOTOX_CHECK(stats.interactive.executed_commands >= 1U);
    IOTOX_CHECK(stats.bulk.executed_commands >= 1U);
    IOTOX_CHECK(stats.interactive.maximum_queue_wait_us > 0U);
    IOTOX_CHECK(stats.interactive.queue_wait_p99_upper_bound_us >=
                stats.interactive.maximum_queue_wait_us);
    IOTOX_CHECK(stats.bulk.queue_wait_p99_upper_bound_us >=
                stats.bulk.maximum_queue_wait_us);
    IOTOX_CHECK(stats.interactive.queue_wait_at_or_above_2000_us >= 1U);
    transport.stop();
}

IOTOX_TEST("owner scheduler bounds toxcore's requested idle interval") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment requested_interval(
        "IOTOX_MOCK_ITERATION_INTERVAL_MS", "750");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_on_stop = false;
    config.maximum_iteration_interval = std::chrono::milliseconds(20);
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());

    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::milliseconds(200);
    iotox::TransportStats stats;
    while (std::chrono::steady_clock::now() < deadline) {
        stats = transport.stats();
        if (stats.iteration_count >= 3U) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    IOTOX_CHECK(stats.iteration_count >= 3U);
    IOTOX_CHECK(stats.requested_iteration_interval_ms == 750U);
    IOTOX_CHECK(stats.effective_iteration_interval_ms == 20U);
    IOTOX_CHECK(transport.set_maximum_iteration_interval(
                    std::chrono::milliseconds{750}).ok());
    const std::uint64_t before_relax = stats.iteration_count;
    const auto relaxed_deadline =
        std::chrono::steady_clock::now() + std::chrono::milliseconds{100};
    while (std::chrono::steady_clock::now() < relaxed_deadline) {
        stats = transport.stats();
        if (stats.iteration_count > before_relax &&
            stats.effective_iteration_interval_ms == 750U) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds{2});
    }
    IOTOX_CHECK(stats.iteration_count > before_relax);
    IOTOX_CHECK(stats.effective_iteration_interval_ms == 750U);
    const std::uint64_t before_tighten = stats.iteration_count;
    IOTOX_CHECK(transport.set_maximum_iteration_interval(
                    std::chrono::milliseconds{5}).ok());
    const auto tightened_deadline =
        std::chrono::steady_clock::now() + std::chrono::milliseconds{100};
    while (std::chrono::steady_clock::now() < tightened_deadline) {
        stats = transport.stats();
        if (stats.iteration_count >= before_tighten + 3U &&
            stats.effective_iteration_interval_ms == 5U) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds{2});
    }
    IOTOX_CHECK(stats.iteration_count >= before_tighten + 3U);
    IOTOX_CHECK(stats.effective_iteration_interval_ms == 5U);
    IOTOX_CHECK(!transport.set_maximum_iteration_interval(
                     std::chrono::milliseconds{0}).ok());
    IOTOX_CHECK(!transport.set_maximum_iteration_interval(
                     std::chrono::milliseconds{1001}).ok());
    transport.stop();
}

IOTOX_TEST("bounded event queue reports evidence loss instead of growing forever") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_on_stop = false;
    config.max_pending_events = 2U;
    config.file_pacing_high_watermark = 0U;
    config.file_pacing_low_watermark = 0U;
    for (std::uint8_t index = 0U; index < 4U; ++index) {
        iotox::toxcore::BootstrapEndpoint endpoint;
        endpoint.host = "bootstrap-" + std::to_string(index) + ".test";
        endpoint.port = static_cast<std::uint16_t>(33445U + index);
        endpoint.public_key.fill(index);
        config.bootstrap_nodes.push_back(endpoint);
        endpoint.host = "relay-" + std::to_string(index) + ".test";
        endpoint.port = static_cast<std::uint16_t>(440U + index);
        config.tcp_relays.push_back(endpoint);
    }

    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    std::this_thread::sleep_for(std::chrono::milliseconds(40));
    const iotox::TransportStats stats = transport.stats();
    IOTOX_CHECK(stats.pending_events <= 2U);
    IOTOX_CHECK(stats.dropped_events > 0U);

    auto event = transport.poll_event(std::chrono::milliseconds(100));
    IOTOX_CHECK(event.has_value());
    IOTOX_CHECK(event->dropped_events_before > 0U);
    transport.stop();
}

IOTOX_TEST("mutation persistence is independent of shutdown persistence") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        unique_transport_directory("mutation-save");
    const std::filesystem::path state = directory / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = state;
    config.save_state_after_mutation = true;
    config.save_state_on_stop = false;

    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK(transport.start().ok());
        auto added = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x73U));
        IOTOX_CHECK_MSG(added.ok(), added.status().message());
        IOTOX_CHECK(std::filesystem::exists(state));
        IOTOX_CHECK(std::filesystem::file_size(state) > 0U);
        transport.stop();
    }

    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK(transport.start().ok());
        auto peers = transport.list_friends();
        IOTOX_CHECK_MSG(peers.ok(), peers.status().message());
        IOTOX_CHECK(peers.value().size() == 1U);
        IOTOX_CHECK(peers.value().front().public_key.front() == 0x73U);
        transport.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("profile mutation reports savedata persistence failure") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        unique_transport_directory("profile-save-failure");
    const std::filesystem::path state = directory / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = state;
    config.save_state_after_mutation = true;
    config.save_state_on_stop = false;

    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    directory, std::vector<std::uint8_t>{0xAAU})
                    .ok());

    const iotox::Status changed =
        transport.set_self_status(iotox::PresenceStatus::busy);
    IOTOX_CHECK(!changed.ok());
    IOTOX_CHECK(changed.code() == iotox::ErrorCode::io_error);
    transport.stop();

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("required transport events apply backpressure instead of disappearing") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.max_pending_events = 1U;
    config.file_pacing_high_watermark = 0U;
    config.file_pacing_low_watermark = 0U;

    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());

    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x74U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    auto first = transport.poll_event(std::chrono::seconds(1));
    IOTOX_CHECK(first.has_value());
    IOTOX_CHECK(first->kind == iotox::TransportEventKind::friend_added);

    // Give the owner one complete iteration to fill the single required-event
    // slot and block on the next profile callback. Without this barrier a
    // heavily instrumented consumer can drain each callback before the owner
    // attempts its successor, making the intended backpressure branch a
    // scheduler lottery rather than a deterministic contract test.
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    // With a one-entry queue, profile callbacks intentionally apply
    // backpressure one by one. Drain through the final initial typing state
    // before asking the owner thread to perform another operation.
    bool saw_initial_typing = false;
    const auto profile_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (std::chrono::steady_clock::now() < profile_deadline &&
           !saw_initial_typing) {
        auto event = transport.poll_event(std::chrono::milliseconds(100));
        if (event && event->kind == iotox::TransportEventKind::friend_typing) {
            saw_initial_typing = true;
        }
    }
    IOTOX_CHECK(saw_initial_typing);

    const std::vector<std::uint8_t> packet{69U, 0xAAU, 0x55U};
    IOTOX_CHECK(transport.send_lossless(peer.value(), packet).ok());

    auto second = transport.poll_event(std::chrono::seconds(1));
    IOTOX_CHECK(second.has_value());
    IOTOX_CHECK(second->kind == iotox::TransportEventKind::lossless_packet);
    IOTOX_CHECK(second->data == packet);
    IOTOX_CHECK(transport.stats().dropped_events >= first->dropped_events_before);
    IOTOX_CHECK(second->dropped_events_before == transport.stats().dropped_events);
    IOTOX_CHECK(transport.stats().maximum_pending_events == 1U);
    IOTOX_CHECK(transport.stats().required_event_backpressure_count != 0U);
    transport.stop();
}

IOTOX_TEST("friend connection epoch events survive a saturated transport queue") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.max_pending_events = 1U;
    config.file_pacing_high_watermark = 0U;
    config.file_pacing_low_watermark = 0U;

    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());

    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x75U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    // friend_added occupies the only queue slot. During the next tox_iterate,
    // observational startup events may be discarded, but the online edge must
    // block behind friend_added rather than disappear. This edge is the sole
    // authority that opens the peer's IoTox online epoch.
    auto added = transport.poll_event(std::chrono::seconds(1));
    IOTOX_CHECK(added.has_value());
    IOTOX_CHECK(added->kind == iotox::TransportEventKind::friend_added);
    IOTOX_CHECK(added->friend_number == peer.value());

    // The consumer may win the scheduling race immediately after tox_iterate
    // publishes an observational self/backend event but before that same
    // iteration reaches the required friend callback. Such an observation is
    // allowed; the property under test is that the callback-owned connection
    // edge survives saturation and arrives before any later required friend
    // event. Do not mistake queue scheduling for lifecycle ordering.
    std::optional<iotox::TransportEvent> connected;
    const auto connection_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(1);
    while (std::chrono::steady_clock::now() < connection_deadline) {
        auto candidate = transport.poll_event(std::chrono::milliseconds(100));
        if (!candidate) {
            continue;
        }
        if (candidate->kind == iotox::TransportEventKind::friend_connection) {
            connected = std::move(candidate);
            break;
        }
        IOTOX_CHECK(
            candidate->kind == iotox::TransportEventKind::backend_ready ||
            candidate->kind == iotox::TransportEventKind::self_connection ||
            candidate->kind == iotox::TransportEventKind::bootstrap ||
            candidate->kind == iotox::TransportEventKind::tcp_relay ||
            candidate->kind == iotox::TransportEventKind::diagnostic);
    }
    IOTOX_CHECK(connected.has_value());
    IOTOX_CHECK(connected->friend_number == peer.value());
    IOTOX_CHECK(
        connected->connection_status ==
        static_cast<int>(iotox::toxcore::abi::kConnectionTcp));

    transport.stop();
}

IOTOX_TEST("toxcore file sender follows requested chunk positions and stable ids") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x81U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    iotox::FileId expected_id{};
    expected_id.fill(0x3CU);
    auto offered = transport.offer_file(
        peer.value(), iotox::toxcore::abi::kFileKindData, 6U, expected_id,
        {'r', 'a', 't', 'o', 'x', '.', 'b', 'i', 'n'});
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());

    auto id = transport.get_file_id(peer.value(), offered.value());
    IOTOX_CHECK_MSG(id.ok(), id.status().message());
    IOTOX_CHECK(id.value() == expected_id);
    auto found = transport.find_file(peer.value(), expected_id);
    IOTOX_CHECK_MSG(found.ok(), found.status().message());
    IOTOX_CHECK(found.value() == offered.value());

    std::vector<std::pair<std::uint64_t, std::size_t>> requests;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (requests.empty() && std::chrono::steady_clock::now() < deadline) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50));
            event && event->kind == iotox::TransportEventKind::file_chunk_request) {
            IOTOX_CHECK(event->file_number == offered.value());
            requests.emplace_back(event->file_position, event->requested_length);
        }
    }
    const std::vector<std::pair<std::uint64_t, std::size_t>> first_request{
        {0U, 4U}};
    IOTOX_CHECK(requests == first_request);
    IOTOX_CHECK(transport.send_file_chunk(
                    peer.value(), offered.value(), 0U, {'A', 'B', 'C', 'D'})
                    .ok());

    while (requests.size() < 2U && std::chrono::steady_clock::now() < deadline) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50));
            event && event->kind == iotox::TransportEventKind::file_chunk_request) {
            requests.emplace_back(event->file_position, event->requested_length);
        }
    }
    IOTOX_CHECK(requests.size() >= 2U);
    const std::pair<std::uint64_t, std::size_t> second_request{4U, 2U};
    IOTOX_CHECK(requests[1] == second_request);
    IOTOX_CHECK(transport.send_file_chunk(
                    peer.value(), offered.value(), 4U, {'E', 'F'})
                    .ok());

    while (requests.size() < 3U && std::chrono::steady_clock::now() < deadline) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50));
            event && event->kind == iotox::TransportEventKind::file_chunk_request) {
            requests.emplace_back(event->file_position, event->requested_length);
        }
    }
    IOTOX_CHECK(requests.size() >= 3U);
    const std::pair<std::uint64_t, std::size_t> completion_request{6U, 0U};
    IOTOX_CHECK(requests[2] == completion_request);
    // A zero-length chunk request is c-toxcore's terminal notification. The
    // sender releases resources; it does not answer with a zero-length chunk.
    transport.stop();
}

IOTOX_TEST("file callback pacing reserves event headroom and yields manual pause ownership") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.max_pending_events = 16U;
    config.file_pacing_high_watermark = 2U;
    config.file_pacing_low_watermark = 0U;
    config.file_pacing_minimum_hold = std::chrono::milliseconds(1);
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x82U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    while (transport.poll_event(std::chrono::milliseconds(20))) {
    }
    const std::vector<std::uint8_t> payload{
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'};
    const auto source =
        [payload](std::uint64_t position, std::size_t length)
        -> iotox::Result<std::vector<std::uint8_t>> {
        if (position > payload.size() ||
            length > payload.size() - static_cast<std::size_t>(position)) {
            return iotox::Status{
                iotox::ErrorCode::invalid_argument,
                "mock paced request exceeded payload"};
        }
        return std::vector<std::uint8_t>(
            payload.begin() + static_cast<std::ptrdiff_t>(position),
            payload.begin() +
                static_cast<std::ptrdiff_t>(position + length));
    };
    auto offered = transport.offer_file(
        peer.value(), iotox::toxcore::abi::kFileKindData, payload.size(),
        std::nullopt, {'p', 'a', 'c', 'e', 'd'}, source);
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());

    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (transport.stats().file_pacing_paused_transfers == 0U &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    IOTOX_CHECK(transport.stats().file_pacing_paused_transfers == 1U);
    IOTOX_CHECK(transport.stats().pending_events >= 2U);

    std::size_t nonterminal = 0U;
    bool completed = false;
    while (!completed && std::chrono::steady_clock::now() < deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        if (!event ||
            event->kind != iotox::TransportEventKind::file_chunk_request ||
            event->file_number != offered.value()) {
            continue;
        }
        if (event->requested_length == 0U) {
            completed = true;
        } else {
            ++nonterminal;
            IOTOX_CHECK(event->file_chunk_source_attempted);
            IOTOX_CHECK(event->file_chunk_sent_inline);
            IOTOX_CHECK(event->file_chunk_status.ok());
        }
    }
    IOTOX_CHECK(completed);
    IOTOX_CHECK(nonterminal == 3U);
    iotox::TransportStats stats = transport.stats();
    IOTOX_CHECK(stats.file_pacing_pause_count >= 1U);
    IOTOX_CHECK(stats.file_pacing_resume_count >= 1U);
    IOTOX_CHECK(stats.file_pacing_resume_batch_limit == 1U);
    IOTOX_CHECK(stats.file_pacing_resume_batch_count ==
                stats.file_pacing_resume_count);
    IOTOX_CHECK(stats.file_pacing_resume_batch_maximum == 1U);
    IOTOX_CHECK(stats.file_pacing_total_hold_us >= 1000U);
    IOTOX_CHECK(stats.file_pacing_paused_transfers == 0U);
    IOTOX_CHECK(stats.file_pacing_pause_failure_count == 0U);
    IOTOX_CHECK(stats.file_pacing_resume_failure_count == 0U);
    IOTOX_CHECK(stats.maximum_pending_events < config.max_pending_events);
    IOTOX_CHECK(stats.required_event_backpressure_count == 0U);

    auto manual = transport.offer_file(
        peer.value(), iotox::toxcore::abi::kFileKindData, payload.size(),
        std::nullopt, {'m', 'a', 'n', 'u', 'a', 'l'}, source);
    IOTOX_CHECK_MSG(manual.ok(), manual.status().message());
    const auto manual_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (transport.stats().file_pacing_paused_transfers == 0U &&
           std::chrono::steady_clock::now() < manual_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    IOTOX_CHECK(transport.stats().file_pacing_paused_transfers == 1U);
    IOTOX_CHECK(transport.control_file(
                    peer.value(), manual.value(),
                    iotox::TransferControl::pause)
                    .ok());
    IOTOX_CHECK(transport.stats().file_pacing_paused_transfers == 0U);
    IOTOX_CHECK(transport.control_file(
                    peer.value(), manual.value(),
                    iotox::TransferControl::resume)
                    .ok());
    completed = false;
    while (!completed &&
           std::chrono::steady_clock::now() < manual_deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        completed = event &&
            event->kind == iotox::TransportEventKind::file_chunk_request &&
            event->file_number == manual.value() &&
            event->requested_length == 0U;
    }
    IOTOX_CHECK(completed);
    stats = transport.stats();
    IOTOX_CHECK(stats.file_pacing_paused_transfers == 0U);
    IOTOX_CHECK(stats.file_pacing_pause_failure_count == 0U);
    IOTOX_CHECK(stats.file_pacing_resume_failure_count == 0U);
    transport.stop();
}

IOTOX_TEST("file callback pacing yields an already-paused transfer to its external owner") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment collision(
        "IOTOX_MOCK_FILE_PAUSE_ALREADY_PAUSED_COUNT", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.max_pending_events = 16U;
    config.file_pacing_high_watermark = 2U;
    config.file_pacing_low_watermark = 0U;
    config.file_pacing_minimum_hold = std::chrono::milliseconds(1);
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x85U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    while (transport.poll_event(std::chrono::milliseconds(20))) {
    }

    const std::vector<std::uint8_t> payload{
        'E', 'X', 'T', 'E', 'R', 'N', 'A', 'L', '-', 'O', 'W', 'N'};
    const auto source =
        [payload](std::uint64_t position, std::size_t length)
        -> iotox::Result<std::vector<std::uint8_t>> {
        if (position > payload.size() ||
            length > payload.size() - static_cast<std::size_t>(position)) {
            return iotox::Status{
                iotox::ErrorCode::invalid_argument,
                "mock external-pause request exceeded payload"};
        }
        return std::vector<std::uint8_t>(
            payload.begin() + static_cast<std::ptrdiff_t>(position),
            payload.begin() +
                static_cast<std::ptrdiff_t>(position + length));
    };
    auto offered = transport.offer_file(
        peer.value(), iotox::toxcore::abi::kFileKindData, payload.size(),
        std::nullopt, {'e', 'x', 't'}, source);
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());

    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (transport.stats().file_pacing_external_pause_count == 0U &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    iotox::TransportStats stats = transport.stats();
    IOTOX_CHECK(stats.file_pacing_external_pause_count == 1U);
    IOTOX_CHECK(stats.file_pacing_paused_transfers == 0U);
    IOTOX_CHECK(stats.file_pacing_pause_failure_count == 0U);
    IOTOX_CHECK(transport.control_file(
                    peer.value(), offered.value(),
                    iotox::TransferControl::resume)
                    .ok());

    bool completed = false;
    while (!completed && std::chrono::steady_clock::now() < deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        completed = event &&
            event->kind == iotox::TransportEventKind::file_chunk_request &&
            event->file_number == offered.value() &&
            event->requested_length == 0U;
    }
    IOTOX_CHECK(completed);
    stats = transport.stats();
    IOTOX_CHECK(stats.file_pacing_external_pause_count == 1U);
    IOTOX_CHECK(stats.file_pacing_pause_failure_count == 0U);
    IOTOX_CHECK(stats.file_pacing_resume_failure_count == 0U);
    transport.stop();
}

IOTOX_TEST("file callback pacing resumes multiple producers in oldest-first singleton batches") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.max_pending_events = 32U;
    config.file_pacing_high_watermark = 2U;
    config.file_pacing_low_watermark = 0U;
    config.file_pacing_minimum_hold = std::chrono::milliseconds(1);
    config.file_pacing_resume_batch_limit = 1U;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x83U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    while (transport.poll_event(std::chrono::milliseconds(20))) {
    }

    const std::vector<std::uint8_t> payload(64U, 0x5aU);
    const auto source =
        [payload](std::uint64_t position, std::size_t length)
        -> iotox::Result<std::vector<std::uint8_t>> {
        if (position > payload.size() ||
            length > payload.size() - static_cast<std::size_t>(position)) {
            return iotox::Status{
                iotox::ErrorCode::invalid_argument,
                "mock fair-paced request exceeded payload"};
        }
        return std::vector<std::uint8_t>(
            payload.begin() + static_cast<std::ptrdiff_t>(position),
            payload.begin() +
                static_cast<std::ptrdiff_t>(position + length));
    };
    std::vector<std::uint32_t> offered;
    for (std::uint8_t lane = 0U; lane < 3U; ++lane) {
        auto file = transport.offer_file(
            peer.value(), iotox::toxcore::abi::kFileKindData,
            payload.size(), std::nullopt, {'f', 'a', 'i', 'r', lane}, source);
        IOTOX_CHECK_MSG(file.ok(), file.status().message());
        offered.push_back(file.value());
    }

    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (transport.stats().file_pacing_paused_transfers < offered.size() &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    IOTOX_CHECK(transport.stats().file_pacing_paused_transfers ==
                offered.size());

    std::vector<std::uint32_t> completed;
    while (completed.size() < offered.size() &&
           std::chrono::steady_clock::now() < deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        if (!event ||
            event->kind != iotox::TransportEventKind::file_chunk_request ||
            std::find(offered.begin(), offered.end(), event->file_number) ==
                offered.end()) {
            continue;
        }
        if (event->requested_length != 0U) {
            IOTOX_CHECK(event->file_chunk_source_attempted);
            IOTOX_CHECK(event->file_chunk_sent_inline);
            IOTOX_CHECK(event->file_chunk_status.ok());
        }
        if (event->requested_length == 0U &&
            std::find(completed.begin(), completed.end(),
                      event->file_number) == completed.end()) {
            completed.push_back(event->file_number);
        }
    }
    IOTOX_CHECK(completed.size() == offered.size());
    const iotox::TransportStats stats = transport.stats();
    IOTOX_CHECK(stats.file_pacing_paused_transfers == 0U);
    IOTOX_CHECK(stats.file_pacing_resume_count >= offered.size());
    IOTOX_CHECK(stats.file_pacing_resume_batch_limit == 1U);
    IOTOX_CHECK(stats.file_pacing_resume_batch_count ==
                stats.file_pacing_resume_count);
    IOTOX_CHECK(stats.file_pacing_resume_batch_maximum == 1U);
    IOTOX_CHECK(stats.file_pacing_pause_failure_count == 0U);
    IOTOX_CHECK(stats.file_pacing_resume_failure_count == 0U);
    IOTOX_CHECK(stats.required_event_backpressure_count == 0U);
    transport.stop();
}

IOTOX_TEST("incoming file offers stay paused until explicit control and preserve completion") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    ScopedEnvironment offer_environment(
        "IOTOX_MOCK_INCOMING_FILE", "incoming-diagnostic.bin");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x82U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    std::optional<iotox::TransportEvent> offer;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (!offer && std::chrono::steady_clock::now() < deadline) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50));
            event && event->kind == iotox::TransportEventKind::file_offer) {
            offer = std::move(event);
        }
    }
    IOTOX_CHECK(offer.has_value());
    IOTOX_CHECK(offer->friend_number == peer.value());
    IOTOX_CHECK(offer->file_size == 4U);
    IOTOX_CHECK(offer->has_file_id);
    iotox::FileId incoming_id{};
    incoming_id.fill(0xD4U);
    IOTOX_CHECK(offer->file_id == incoming_id);
    IOTOX_CHECK(std::string(offer->filename.begin(), offer->filename.end()) ==
                "incoming-diagnostic.bin");

    IOTOX_CHECK(transport.seek_file(
                    peer.value(), offer->file_number, 0U)
                    .ok());
    IOTOX_CHECK(transport.control_file(
                    peer.value(), offer->file_number,
                    iotox::TransferControl::resume)
                    .ok());

    bool saw_unexpected_control_echo = false;
    bool saw_data = false;
    bool saw_completion = false;
    while (!(saw_data && saw_completion) &&
           std::chrono::steady_clock::now() < deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        if (!event || event->file_number != offer->file_number) {
            continue;
        }
        if (event->kind == iotox::TransportEventKind::file_control) {
            // tox_callback_file_recv_control reports control received from the
            // friend. A successful local tox_file_control(RESUME) must not be
            // reflected back through that callback.
            saw_unexpected_control_echo = true;
        } else if (event->kind == iotox::TransportEventKind::file_chunk &&
                   !event->data.empty()) {
            const std::vector<std::uint8_t> expected_data{'D', 'A', 'T', 'A'};
            saw_data = event->file_position == 0U &&
                       event->data == expected_data;
        } else if (event->kind == iotox::TransportEventKind::file_chunk &&
                   event->data.empty()) {
            saw_completion = event->file_position == 4U;
        }
    }
    IOTOX_CHECK(!saw_unexpected_control_echo);
    IOTOX_CHECK(saw_data);
    IOTOX_CHECK(saw_completion);
    transport.stop();
}

IOTOX_TEST("transport profile text typing and receipts survive the exact mock ABI") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr,
                    "test runner did not provide the mock c-toxcore path");

    const std::filesystem::path directory =
        unique_transport_directory("profile-text");
    const std::filesystem::path state = directory / "device.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = state;

    const std::vector<std::uint8_t> name{'I', 'o', 0U, 'T', 'o', 'x'};
    const std::vector<std::uint8_t> status_message{
        'w', 'a', 'k', 'e', '\n', 'f', 'r', 'o', 'm', ' ', 'a', 'm', 'n', 'e', 's', 'i', 'a'};
    const std::vector<std::uint8_t> action{'j', 'u', 's', 't', 0U, 'w', 'e', 'r', 'x'};

    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK_MSG(transport.start().ok(), "transport did not start");
        IOTOX_CHECK(transport.set_self_name(name).ok());
        IOTOX_CHECK(transport.set_self_status_message(status_message).ok());
        IOTOX_CHECK(transport.set_self_status(iotox::PresenceStatus::busy).ok());

        auto profile = transport.self_profile();
        IOTOX_CHECK_MSG(profile.ok(), profile.status().message());
        IOTOX_CHECK(profile.value().name == name);
        IOTOX_CHECK(profile.value().status_message == status_message);
        IOTOX_CHECK(profile.value().status == iotox::PresenceStatus::busy);

        auto friend_number =
            transport.accept_friend(std::vector<std::uint8_t>(32U, 0x42U));
        IOTOX_CHECK_MSG(friend_number.ok(), friend_number.status().message());

        auto message_id = transport.send_message(
            friend_number.value(), iotox::TextMessageKind::action, action);
        IOTOX_CHECK_MSG(message_id.ok(), message_id.status().message());
        IOTOX_CHECK(message_id.value() == 0U);
        IOTOX_CHECK(transport.set_typing(friend_number.value(), true).ok());

        bool saw_sent = false;
        bool saw_echo = false;
        bool saw_receipt = false;
        bool saw_typing = false;
        const auto deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(3);
        while (std::chrono::steady_clock::now() < deadline &&
               (!saw_sent || !saw_echo || !saw_receipt || !saw_typing)) {
            auto event = transport.poll_event(std::chrono::milliseconds(50));
            if (!event) {
                continue;
            }
            if (event->kind == iotox::TransportEventKind::message_sent) {
                IOTOX_CHECK(event->friend_number == friend_number.value());
                IOTOX_CHECK(event->text_kind == iotox::TextMessageKind::action);
                IOTOX_CHECK(event->message_id == message_id.value());
                IOTOX_CHECK(event->data == action);
                saw_sent = true;
            } else if (event->kind == iotox::TransportEventKind::friend_message) {
                IOTOX_CHECK(event->friend_number == friend_number.value());
                IOTOX_CHECK(event->text_kind == iotox::TextMessageKind::action);
                IOTOX_CHECK(event->data == action);
                saw_echo = true;
            } else if (event->kind ==
                       iotox::TransportEventKind::friend_read_receipt) {
                IOTOX_CHECK(event->friend_number == friend_number.value());
                IOTOX_CHECK(event->message_id == message_id.value());
                IOTOX_CHECK(event->text_kind == iotox::TextMessageKind::action);
                saw_receipt = true;
            } else if (event->kind == iotox::TransportEventKind::friend_typing &&
                       event->typing) {
                IOTOX_CHECK(event->friend_number == friend_number.value());
                saw_typing = true;
            }
        }
        IOTOX_CHECK(saw_sent);
        IOTOX_CHECK(saw_echo);
        IOTOX_CHECK(saw_receipt);
        IOTOX_CHECK(saw_typing);

        auto peers = transport.list_friends();
        IOTOX_CHECK_MSG(peers.ok(), peers.status().message());
        IOTOX_CHECK(peers.value().size() == 1U);
        IOTOX_CHECK(peers.value().front().name ==
                    std::vector<std::uint8_t>({'m', 'o', 'c', 'k', '-', 'p', 'e', 'e', 'r', '-', '0'}));
        IOTOX_CHECK(peers.value().front().status_message ==
                    std::vector<std::uint8_t>({'m', 'o', 'c', 'k', ' ', 't', 'r', 'a', 'n', 's', 'p', 'o', 'r', 't', ' ', 'p', 'e', 'e', 'r', ' ', '0'}));
        IOTOX_CHECK(peers.value().front().typing);
        transport.stop();
    }

    IOTOX_CHECK(std::filesystem::exists(state));
    {
        iotox::ToxTransport transport(config);
        IOTOX_CHECK(transport.start().ok());
        auto profile = transport.self_profile();
        IOTOX_CHECK_MSG(profile.ok(), profile.status().message());
        IOTOX_CHECK(profile.value().name == name);
        IOTOX_CHECK(profile.value().status_message == status_message);
        IOTOX_CHECK(profile.value().status == iotox::PresenceStatus::busy);
        auto peers = transport.list_friends();
        IOTOX_CHECK(peers.ok());
        IOTOX_CHECK(peers.value().size() == 1U);
        transport.stop();
    }

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("text receipt correlation is abandoned when c-toxcore disconnects the friend") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr,
                    "test runner did not provide the mock c-toxcore path");

    ScopedEnvironment disconnect_once(
        "IOTOX_MOCK_TEXT_DISCONNECTS_BEFORE_RECEIPT", "1");
    const std::filesystem::path directory =
        unique_transport_directory("text-disconnect-receipt");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";

    iotox::ToxTransport transport(config);
    IOTOX_CHECK_MSG(transport.start().ok(), "transport did not start");
    auto friend_number =
        transport.accept_friend(std::vector<std::uint8_t>(32U, 0x63U));
    IOTOX_CHECK_MSG(friend_number.ok(), friend_number.status().message());

    const std::vector<std::uint8_t> body{'g', 'o', 'n', 'e'};
    auto message_id = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, body);
    IOTOX_CHECK_MSG(message_id.ok(), message_id.status().message());

    bool saw_sent = false;
    bool saw_echo = false;
    bool saw_disconnect = false;
    bool saw_abandoned = false;
    bool saw_receipt = false;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < deadline &&
           (!saw_sent || !saw_echo || !saw_disconnect || !saw_abandoned)) {
        auto event = transport.poll_event(std::chrono::milliseconds(50));
        if (!event) {
            continue;
        }
        if (event->kind == iotox::TransportEventKind::message_sent &&
            event->friend_number == friend_number.value() &&
            event->message_id == message_id.value()) {
            saw_sent = true;
        } else if (event->kind == iotox::TransportEventKind::friend_message &&
                   event->friend_number == friend_number.value() &&
                   event->data == body) {
            saw_echo = true;
        } else if (event->kind ==
                       iotox::TransportEventKind::friend_connection &&
                   event->friend_number == friend_number.value() &&
                   event->connection_status ==
                       static_cast<int>(iotox::toxcore::abi::kConnectionNone)) {
            saw_disconnect = true;
        } else if (event->kind == iotox::TransportEventKind::diagnostic &&
                   event->friend_number == friend_number.value() &&
                   event->message.find(
                       "abandoned 1 pending c-toxcore text receipt correlation") !=
                       std::string::npos) {
            saw_abandoned = true;
        } else if (event->kind ==
                       iotox::TransportEventKind::friend_read_receipt &&
                   event->friend_number == friend_number.value() &&
                   event->message_id == message_id.value()) {
            saw_receipt = true;
        }
    }

    const auto quiet_deadline =
        std::chrono::steady_clock::now() + std::chrono::milliseconds(150);
    while (std::chrono::steady_clock::now() < quiet_deadline) {
        auto event = transport.poll_event(std::chrono::milliseconds(20));
        if (event && event->kind ==
                         iotox::TransportEventKind::friend_read_receipt &&
            event->friend_number == friend_number.value() &&
            event->message_id == message_id.value()) {
            saw_receipt = true;
        }
    }

    IOTOX_CHECK(saw_sent);
    IOTOX_CHECK(saw_echo);
    IOTOX_CHECK(saw_disconnect);
    IOTOX_CHECK(saw_abandoned);
    IOTOX_CHECK(!saw_receipt);

    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("transport preserves typed c-toxcore text-message failures") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK_MSG(mock_library != nullptr,
                    "test runner did not provide the mock c-toxcore path");

    ScopedEnvironment offline_once(
        "IOTOX_MOCK_TEXT_NOT_CONNECTED_FAILURES", "1");
    ScopedEnvironment sendq_once("IOTOX_MOCK_TEXT_SENDQ_FAILURES", "1");

    const std::filesystem::path directory =
        unique_transport_directory("typed-text-errors");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";

    iotox::ToxTransport transport(config);
    IOTOX_CHECK_MSG(transport.start().ok(), "transport did not start");

    const std::vector<std::uint8_t> body{'h', 'e', 'l', 'l', 'o'};
    auto missing = transport.send_message(
        999U, iotox::TextMessageKind::normal, body);
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.status().code() == iotox::ErrorCode::not_found);

    auto friend_number =
        transport.accept_friend(std::vector<std::uint8_t>(32U, 0x54U));
    IOTOX_CHECK_MSG(friend_number.ok(), friend_number.status().message());

    auto offline = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, body);
    IOTOX_CHECK(!offline.ok());
    IOTOX_CHECK(offline.status().code() == iotox::ErrorCode::unavailable);

    auto saturated = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, body);
    IOTOX_CHECK(!saturated.ok());
    IOTOX_CHECK(saturated.status().code() ==
                iotox::ErrorCode::resource_exhausted);

    auto accepted = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, body);
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value() == 0U);

    auto empty = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, {});
    IOTOX_CHECK(!empty.ok());
    IOTOX_CHECK(empty.status().code() == iotox::ErrorCode::invalid_argument);

    std::vector<std::uint8_t> oversized(
        iotox::toxcore::abi::kMaxMessageLength + 1U,
        static_cast<std::uint8_t>('x'));
    auto too_long = transport.send_message(
        friend_number.value(), iotox::TextMessageKind::normal, oversized);
    IOTOX_CHECK(!too_long.ok());
    IOTOX_CHECK(too_long.status().code() ==
                iotox::ErrorCode::invalid_argument);

    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("sensitive lossless telemetry classifies typed provider outcomes") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const auto directory = unique_transport_directory("sensitive-stats");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    ScopedEnvironment sendq_once("IOTOX_MOCK_LOSSLESS_SENDQ_FAILURES", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.state_path = directory / "device.toxsave";
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());

    const std::vector<std::uint8_t> empty;
    const iotox::Status invalid = transport.send_sensitive_lossless(0U, empty);
    IOTOX_CHECK(!invalid.ok());
    IOTOX_CHECK(invalid.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(transport.stats().sensitive_lossless.calls == 0U);

    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x77U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    const std::vector<std::uint8_t> packet{69U, 0x21U};

    const iotox::Status pressured =
        transport.send_sensitive_lossless(peer.value(), packet);
    IOTOX_CHECK(!pressured.ok());
    IOTOX_CHECK(pressured.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(transport.send_sensitive_lossless(peer.value(), packet).ok());
    const iotox::Status missing =
        transport.send_sensitive_lossless(peer.value() + 100U, packet);
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.code() == iotox::ErrorCode::not_found);

    const auto stats = transport.stats().sensitive_lossless;
    IOTOX_CHECK(stats.calls == 3U);
    IOTOX_CHECK(stats.toxcore_attempts == 3U);
    IOTOX_CHECK(stats.accepted == 1U);
    IOTOX_CHECK(stats.send_queue_full == 1U);
    IOTOX_CHECK(stats.peer_not_connected == 0U);
    IOTOX_CHECK(stats.peer_not_found == 1U);
    IOTOX_CHECK(stats.contract_rejections == 0U);
    IOTOX_CHECK(stats.other_failures == 0U);

    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("sensitive lossless telemetry snapshots preserve accounting invariants") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    ScopedEnvironment delay("IOTOX_MOCK_SEND_DELAY_MS", "2");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    config.owner_command_timeout = std::chrono::seconds(5);
    config.max_pending_commands = 128U;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x78U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    constexpr std::size_t kProducerCount = 8U;
    constexpr std::size_t kSendsPerProducer = 8U;
    const std::vector<std::uint8_t> packet{69U, 0x31U};
    std::atomic<bool> producers_done{false};
    std::atomic<bool> coherent_snapshots{true};

    std::thread observer([&] {
        while (!producers_done.load()) {
            const auto stats = transport.stats().sensitive_lossless;
            const std::uint64_t classified =
                stats.accepted + stats.send_queue_full +
                stats.peer_not_connected + stats.peer_not_found +
                stats.contract_rejections + stats.other_failures;
            if (stats.calls < stats.toxcore_attempts ||
                stats.toxcore_attempts < classified) {
                coherent_snapshots.store(false);
                return;
            }
            std::this_thread::yield();
        }
    });

    std::vector<std::thread> producers;
    producers.reserve(kProducerCount);
    std::atomic<bool> sends_ok{true};
    for (std::size_t producer = 0U; producer < kProducerCount; ++producer) {
        producers.emplace_back([&] {
            for (std::size_t index = 0U; index < kSendsPerProducer; ++index) {
                if (!transport.send_sensitive_lossless(peer.value(), packet).ok()) {
                    sends_ok.store(false);
                }
            }
        });
    }
    for (auto &producer : producers) {
        producer.join();
    }
    producers_done.store(true);
    observer.join();

    IOTOX_CHECK(sends_ok.load());
    IOTOX_CHECK(coherent_snapshots.load());
    const auto final_stats = transport.stats().sensitive_lossless;
    constexpr std::uint64_t kExpected =
        static_cast<std::uint64_t>(kProducerCount * kSendsPerProducer);
    IOTOX_CHECK(final_stats.calls == kExpected);
    IOTOX_CHECK(final_stats.toxcore_attempts == kExpected);
    IOTOX_CHECK(final_stats.accepted == kExpected);
    IOTOX_CHECK(final_stats.send_queue_full == 0U);
    IOTOX_CHECK(final_stats.peer_not_connected == 0U);
    IOTOX_CHECK(final_stats.peer_not_found == 0U);
    IOTOX_CHECK(final_stats.contract_rejections == 0U);
    IOTOX_CHECK(final_stats.other_failures == 0U);
    transport.stop();
}
