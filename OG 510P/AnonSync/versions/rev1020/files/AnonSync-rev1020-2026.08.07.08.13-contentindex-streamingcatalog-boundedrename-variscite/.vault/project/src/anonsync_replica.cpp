#include "sha256_digest.hpp"
#include "sqlite_path_security.hpp"
#include "sqlite_snapshot_seal.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_bootstrap_record.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_numeric_listener.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_session_supervisor.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_replica_stream_connector.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_replica_tls_transport.hpp"
#include "sync_sqlite_support.hpp"

#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/ssl.h>
#include <openssl/x509.h>
#include <sqlite3.h>


namespace {

namespace fs = std::filesystem;
using SslContextOwner = std::unique_ptr<SSL_CTX, decltype(&SSL_CTX_free)>;
using BioOwner = std::unique_ptr<BIO, decltype(&BIO_free)>;
using CertificateOwner = std::unique_ptr<X509, decltype(&X509_free)>;

constexpr std::uint64_t kDefaultMaxPayloadBytes =
    4ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kMaximumCliPayloadBytes =
    anonsync::kSyncReplicaDeploymentManifestMaxPayloadBytes;
constexpr std::uint64_t kDefaultTimeoutSeconds = 10U;
constexpr std::uint64_t kDefaultI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMinimumI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMaximumTimeoutSeconds = 3600U;
constexpr std::uint64_t kMaximumI2pPrivateDestinationBytes = 8192U;
constexpr std::uint64_t kDefaultI2pTunnelQuantity = 2U;
constexpr std::uint64_t kMaximumI2pTunnelQuantity = 16U;
constexpr std::uint64_t kMaximumBatchSessions =
    anonsync::kSyncReplicaSessionSupervisorMaximumSessions;
constexpr std::uint64_t kMaximumRuntimeSeconds =
    anonsync::kSyncReplicaSessionSupervisorMaximumRuntimeSeconds;
constexpr std::uint64_t kMaximumBootstrapSqliteImageBytes =
    64ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kMaximumBootstrapSqliteImagePages = 16384ULL;

[[nodiscard]] std::string openssl_errors() {
    std::string output;
    for (unsigned long code = ERR_get_error(); code != 0UL;
         code = ERR_get_error()) {
        char text[256]{};
        ERR_error_string_n(code, text, sizeof(text));
        if (!output.empty()) output += "; ";
        output += text;
    }
    return output.empty() ? "no OpenSSL detail" : output;
}

[[noreturn]] void throw_openssl(const std::string& message) {
    throw std::runtime_error(message + ": " + openssl_errors());
}

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

[[nodiscard]] const char* json_bool(bool value) noexcept {
    return value ? "true" : "false";
}

class Options final {
public:
    Options(int argc, char** argv, int first) {
        for (int index = first; index < argc; ++index) {
            std::string token = argv[index];
            if (!token.starts_with("--") || token.size() <= 2U) {
                throw std::invalid_argument(
                    "unexpected positional argument: " + token);
            }
            token.erase(0U, 2U);
            std::string key;
            std::string value;
            const std::size_t equals = token.find('=');
            if (equals != std::string::npos) {
                key = token.substr(0U, equals);
                value = token.substr(equals + 1U);
            } else {
                key = std::move(token);
                if (index + 1 >= argc ||
                    std::string_view(argv[index + 1]).starts_with("--")) {
                    throw std::invalid_argument(
                        "missing value for --" + key);
                }
                value = argv[++index];
            }
            if (key.empty()) {
                throw std::invalid_argument("empty option name");
            }
            values_[std::move(key)].push_back(std::move(value));
        }
    }

    void require_only(std::initializer_list<std::string_view> allowed) const {
        std::set<std::string_view> accepted(allowed.begin(), allowed.end());
        for (const auto& [key, ignored] : values_) {
            (void)ignored;
            if (!accepted.contains(key)) {
                throw std::invalid_argument("unknown option --" + key);
            }
        }
    }

    [[nodiscard]] bool has(std::string_view key) const {
        return values_.contains(std::string(key));
    }

    [[nodiscard]] const std::vector<std::string>& all(
        std::string_view key) const {
        static const std::vector<std::string> empty;
        const auto found = values_.find(std::string(key));
        return found == values_.end() ? empty : found->second;
    }

    [[nodiscard]] std::string one(std::string_view key) const {
        const auto& values = all(key);
        if (values.empty()) {
            throw std::invalid_argument(
                "required option --" + std::string(key) + " is missing");
        }
        if (values.size() != 1U) {
            throw std::invalid_argument(
                "option --" + std::string(key) +
                " must appear exactly once");
        }
        if (values.front().empty()) {
            throw std::invalid_argument(
                "option --" + std::string(key) + " must not be empty");
        }
        return values.front();
    }

    [[nodiscard]] std::string one_or(
        std::string_view key,
        std::string fallback) const {
        return has(key) ? one(key) : std::move(fallback);
    }

private:
    std::map<std::string, std::vector<std::string>> values_;
};

[[nodiscard]] std::uint64_t parse_uint64(
    std::string_view value,
    std::string_view label) {
    std::uint64_t parsed = 0U;
    const char* const begin = value.data();
    const char* const end = value.data() + value.size();
    const auto result = std::from_chars(begin, end, parsed, 10);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw std::invalid_argument(
            std::string(label) + " is not an unsigned decimal integer");
    }
    return parsed;
}

[[nodiscard]] std::uint16_t parse_port(
    std::string_view value,
    std::string_view label) {
    const std::uint64_t parsed = parse_uint64(value, label);
    if (parsed == 0U || parsed > 65535U) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, 65535]");
    }
    return static_cast<std::uint16_t>(parsed);
}

[[nodiscard]] std::uint64_t option_uint64_or(
    const Options& options,
    std::string_view key,
    std::uint64_t fallback) {
    return options.has(key)
        ? parse_uint64(options.one(key), std::string("--") + std::string(key))
        : fallback;
}

[[nodiscard]] fs::path require_absolute_path(
    std::string value,
    std::string_view label) {
    fs::path path(std::move(value));
    if (!path.is_absolute()) {
        throw std::invalid_argument(
            std::string(label) + " must be an absolute path");
    }
    return path.lexically_normal();
}

[[nodiscard]] fs::path require_existing_directory(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error || !fs::is_directory(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            std::string(label) +
            " must name an existing non-symlink directory");
    }
    return path;
}

[[nodiscard]] fs::path require_database_path(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    const fs::path parent = path.parent_path();
    if (parent.empty()) {
        throw std::invalid_argument(
            std::string(label) + " has no parent directory");
    }
    std::error_code error;
    const fs::file_status parent_status = fs::symlink_status(parent, error);
    if (error || !fs::is_directory(parent_status) ||
        fs::is_symlink(parent_status)) {
        throw std::invalid_argument(
            std::string(label) +
            " parent must be an existing non-symlink directory");
    }
    return path;
}

[[nodiscard]] fs::path require_existing_regular_file(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error || !fs::is_regular_file(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            std::string(label) +
            " must name an existing non-symlink regular file");
    }
    return path;
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    std::string_view bytes) noexcept {
    return {
        reinterpret_cast<const unsigned char*>(bytes.data()),
        bytes.size(),
    };
}

[[nodiscard]] fs::path append_ascii_path_suffix(
    const fs::path& path,
    std::string_view suffix) {
    fs::path::string_type native = path.native();
    for (const char byte : suffix) {
        native.push_back(static_cast<fs::path::value_type>(byte));
    }
    return fs::path(std::move(native));
}

[[nodiscard]] bool path_is_absent_or_throw(
    const fs::path& path,
    const std::string& label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (!error && status.type() == fs::file_type::not_found) return true;
    if (error == std::errc::no_such_file_or_directory) return true;
    if (error) {
        throw std::runtime_error(
            label + " could not prove path absence: " + error.message());
    }
    return false;
}

void require_path_absent_for_fresh_bootstrap_or_throw(
    const fs::path& path,
    const std::string& label) {
    if (path_is_absent_or_throw(path, label)) return;
    throw std::runtime_error(
        label + " must be absent for fresh bootstrap: " +
        path.generic_string());
}

void require_fresh_database_family_or_throw(
    const fs::path& database_path,
    const std::string& label) {
    require_path_absent_for_fresh_bootstrap_or_throw(
        database_path, label + " main database");
    for (const std::string_view suffix :
         {std::string_view("-journal"), std::string_view("-wal"),
          std::string_view("-shm")}) {
        require_path_absent_for_fresh_bootstrap_or_throw(
            append_ascii_path_suffix(database_path, suffix),
            label + " SQLite sidecar " + std::string(suffix));
    }
}

[[nodiscard]] bool directory_is_empty_or_throw(
    const fs::path& directory,
    const std::string& label) {
    std::error_code error;
    fs::directory_iterator cursor(directory, error);
    if (error) {
        throw std::runtime_error(
            label + " could not inspect directory: " + error.message());
    }
    return cursor == fs::directory_iterator{};
}

void require_empty_directory_for_fresh_bootstrap_or_throw(
    const fs::path& directory,
    const std::string& label) {
    if (!directory_is_empty_or_throw(directory, label)) {
        throw std::runtime_error(
            label + " must be empty for fresh bootstrap: " +
            directory.generic_string());
    }
}

[[nodiscard]] anonsync::SyncReplicaActor actor_from_options(
    const Options& options,
    std::string_view device_option,
    std::string_view epoch_option,
    std::string_view label) {
    anonsync::SyncReplicaActor actor{
        options.one(device_option),
        parse_uint64(options.one(epoch_option), epoch_option)};
    if (!anonsync::sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(
            std::string(label) + " actor is invalid");
    }
    return actor;
}

[[nodiscard]] anonsync::SyncReplicaTlsPeerPolicy
expected_peer_from_options_or_throw(const Options& options) {
    const anonsync::SyncReplicaActor remote_actor = actor_from_options(
        options, "remote-device", "remote-epoch", "remote");
    const std::string remote_spki = options.one("remote-spki");
    if (!anonsync::is_lowercase_sha256_hex(remote_spki)) {
        throw std::invalid_argument(
            "--remote-spki must be lowercase SHA-256");
    }
    return {remote_actor, remote_spki};
}

[[nodiscard]] std::uint64_t max_payload_from_options(
    const Options& options) {
    const std::uint64_t maximum = option_uint64_or(
        options, "max-payload-bytes", kDefaultMaxPayloadBytes);
    if (maximum == 0U || maximum > kMaximumCliPayloadBytes) {
        throw std::invalid_argument(
            "--max-payload-bytes must be in [1, " +
            std::to_string(kMaximumCliPayloadBytes) + "]");
    }
    return maximum;
}

[[nodiscard]] bool adopt_existing_initial_files_from_options_or_throw(
    const Options& options) {
    const std::string mode = options.one_or("initial-files", "empty");
    if (mode == "empty") return false;
    if (mode == "adopt-existing") return true;
    throw std::invalid_argument(
        "--initial-files must be empty or adopt-existing");
}

[[nodiscard]] std::string random_hex_token_or_throw(
    std::size_t byte_count,
    std::string_view label) {
    if (byte_count == 0U ||
        byte_count > static_cast<std::size_t>(
                         std::numeric_limits<int>::max())) {
        throw std::invalid_argument(
            std::string(label) + " random-token size is invalid");
    }
    std::vector<unsigned char> bytes(byte_count);
    ERR_clear_error();
    if (RAND_bytes(bytes.data(), static_cast<int>(bytes.size())) != 1) {
        throw_openssl(std::string(label) + " could not generate random bytes");
    }
    constexpr std::string_view hex = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(bytes.size() * 2U);
    for (const unsigned char byte : bytes) {
        encoded.push_back(hex[byte >> 4U]);
        encoded.push_back(hex[byte & 0x0fU]);
    }
    return encoded;
}

void reject_route_options_or_throw(
    const Options& options,
    std::initializer_list<std::string_view> rejected,
    std::string_view selected_transport) {
    for (const std::string_view key : rejected) {
        if (options.has(key)) {
            throw std::invalid_argument(
                "--" + std::string(key) + " is not valid with --transport " +
                std::string(selected_transport));
        }
    }
}

[[nodiscard]] std::string read_i2p_private_destination_or_throw(
    const Options& options) {
    if (!options.has("i2p-private-destination-file")) {
        return "TRANSIENT";
    }
    const fs::path path = require_absolute_path(
        options.one("i2p-private-destination-file"),
        "--i2p-private-destination-file");
    std::string destination =
        anonsync::read_sync_bounded_private_regular_file_no_symlink_or_throw(
            path, kMaximumI2pPrivateDestinationBytes,
            "anonsync_replica I2P private destination");
    if (destination.ends_with('\n')) {
        destination.pop_back();
        if (destination.ends_with('\r')) destination.pop_back();
    }
    if (destination.empty()) {
        throw std::invalid_argument(
            "--i2p-private-destination-file is empty");
    }
    return destination;
}

[[nodiscard]] std::uint32_t i2p_tunnel_quantity_from_options(
    const Options& options,
    std::string_view key) {
    const std::uint64_t quantity = option_uint64_or(
        options, key, kDefaultI2pTunnelQuantity);
    if (quantity == 0U || quantity > kMaximumI2pTunnelQuantity) {
        throw std::invalid_argument(
            "--" + std::string(key) + " must be in [1, 16]");
    }
    return static_cast<std::uint32_t>(quantity);
}

[[nodiscard]] anonsync::SyncReplicaStreamRoute
stream_route_from_options_or_throw(const Options& options) {
    const std::string transport = options.one_or("transport", "direct");
    anonsync::SyncReplicaStreamRoute route;
    if (transport == "direct") {
        reject_route_options_or_throw(
            options,
            {"tor-socks-address", "tor-socks-port", "onion-address",
             "onion-port", "tor-isolation-token", "i2p-sam-address",
             "i2p-sam-port", "i2p-destination", "i2p-session-id",
             "i2p-private-destination-file", "i2p-inbound-quantity",
             "i2p-outbound-quantity"},
            transport);
        route = anonsync::SyncReplicaDirectTcpRoute{
            anonsync::SyncReplicaNumericStreamEndpoint{
                options.one("address"),
                parse_port(options.one("port"), "--port")}};
    } else if (transport == "tor") {
        reject_route_options_or_throw(
            options,
            {"address", "port", "i2p-sam-address", "i2p-sam-port",
             "i2p-destination", "i2p-session-id",
             "i2p-private-destination-file", "i2p-inbound-quantity",
             "i2p-outbound-quantity"},
            transport);
        route = anonsync::SyncReplicaTorSocks5Route{
            .proxy = {
                options.one_or("tor-socks-address", "127.0.0.1"),
                parse_port(
                    options.one_or("tor-socks-port", "9050"),
                    "--tor-socks-port")},
            .onion_service = options.one("onion-address"),
            .service_port =
                parse_port(options.one("onion-port"), "--onion-port"),
            .isolation_token = options.has("tor-isolation-token")
                ? options.one("tor-isolation-token")
                : random_hex_token_or_throw(
                      32U, "anonsync_replica Tor command isolation")};
    } else if (transport == "i2p") {
        reject_route_options_or_throw(
            options,
            {"address", "port", "tor-socks-address", "tor-socks-port",
             "onion-address", "onion-port", "tor-isolation-token"},
            transport);
        route = anonsync::SyncReplicaI2pSamRoute{
            .bridge = {
                options.one_or("i2p-sam-address", "127.0.0.1"),
                parse_port(
                    options.one_or("i2p-sam-port", "7656"),
                    "--i2p-sam-port")},
            .session_id = options.has("i2p-session-id")
                ? options.one("i2p-session-id")
                : "anonsync-" + random_hex_token_or_throw(
                      16U, "anonsync_replica I2P SAM session"),
            .peer_destination = options.one("i2p-destination"),
            .session_destination =
                read_i2p_private_destination_or_throw(options),
            .inbound_quantity = i2p_tunnel_quantity_from_options(
                options, "i2p-inbound-quantity"),
            .outbound_quantity = i2p_tunnel_quantity_from_options(
                options, "i2p-outbound-quantity")};
    } else {
        throw std::invalid_argument(
            "--transport must be one of direct, tor, or i2p");
    }
    anonsync::validate_sync_replica_stream_route_or_throw(
        route, "anonsync_replica outbound stream route");
    return route;
}

[[nodiscard]] std::uint64_t sender_timeout_from_options(
    const Options& options,
    anonsync::SyncReplicaStreamRouteKind route_kind) {
    const std::uint64_t fallback =
        route_kind == anonsync::SyncReplicaStreamRouteKind::I2pSam
        ? kDefaultI2pTimeoutSeconds
        : kDefaultTimeoutSeconds;
    const std::uint64_t timeout = option_uint64_or(
        options, "timeout-seconds", fallback);
    if (timeout == 0U || timeout > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            "--timeout-seconds must be in [1, 3600]");
    }
    if (route_kind == anonsync::SyncReplicaStreamRouteKind::I2pSam &&
        timeout < kMinimumI2pTimeoutSeconds) {
        throw std::invalid_argument(
            "--timeout-seconds must be at least 180 for --transport i2p");
    }
    return timeout;
}

[[nodiscard]] std::uint64_t reconciliation_max_round_trips_from_options(
    const Options& options) {
    const std::uint64_t maximum = option_uint64_or(
        options, "max-round-trips",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxRoundTrips);
    if (maximum == 0U ||
        maximum > anonsync::kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            "--max-round-trips must be in [1, 4096]");
    }
    return maximum;
}

[[nodiscard]] std::uint64_t reconciliation_max_source_resets_from_options(
    const Options& options) {
    const std::uint64_t maximum = option_uint64_or(
        options, "max-source-resets",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxSourceResets);
    if (maximum > anonsync::kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            "--max-source-resets must be in [0, 4096]");
    }
    return maximum;
}

enum class ServePublicationKind {
    DirectTcp,
    TorOnionService,
    I2pSamForward,
};

[[nodiscard]] std::string_view serve_publication_kind_name(
    ServePublicationKind kind) noexcept {
    switch (kind) {
        case ServePublicationKind::DirectTcp: return "direct_tcp";
        case ServePublicationKind::TorOnionService:
            return "tor_onion_service";
        case ServePublicationKind::I2pSamForward:
            return "i2p_sam_forward";
    }
    return "unknown";
}

struct ServeRouteSelection final {
    ServePublicationKind kind = ServePublicationKind::DirectTcp;
    anonsync::SyncReplicaNumericStreamEndpoint listener_endpoint;
    std::optional<std::string> onion_service;
    std::optional<std::uint16_t> onion_service_port;
    std::optional<anonsync::SyncReplicaI2pSamForwardRoute> i2p_forward;
};

[[nodiscard]] ServeRouteSelection serve_route_from_options_or_throw(
    const Options& options) {
    ServeRouteSelection selection;
    selection.listener_endpoint = {
        options.one("bind-address"),
        parse_port(options.one("port"), "--port")};
    const std::string transport = options.one_or("transport", "direct");
    if (transport == "direct") {
        reject_route_options_or_throw(
            options,
            {"onion-address", "onion-port", "tor-socks-address",
             "tor-socks-port", "tor-isolation-token", "i2p-sam-address",
             "i2p-sam-port", "i2p-destination", "i2p-session-id",
             "i2p-private-destination-file", "i2p-inbound-quantity",
             "i2p-outbound-quantity"},
            transport);
        anonsync::validate_sync_replica_stream_route_or_throw(
            anonsync::SyncReplicaDirectTcpRoute{
                selection.listener_endpoint},
            "anonsync_replica direct listener endpoint");
        selection.kind = ServePublicationKind::DirectTcp;
    } else if (transport == "tor") {
        reject_route_options_or_throw(
            options,
            {"tor-socks-address", "tor-socks-port", "tor-isolation-token",
             "i2p-sam-address", "i2p-sam-port", "i2p-destination",
             "i2p-session-id", "i2p-private-destination-file",
             "i2p-inbound-quantity", "i2p-outbound-quantity"},
            transport);
        if (!anonsync::sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
                selection.listener_endpoint,
                "anonsync_replica Tor onion-service listener")) {
            throw std::invalid_argument(
                "--transport tor requires a loopback --bind-address because "
                "the Tor daemon owns external publication");
        }
        selection.onion_service = options.one("onion-address");
        anonsync::validate_sync_replica_tor_v3_onion_service_or_throw(
            *selection.onion_service,
            "anonsync_replica inbound Tor onion service");
        selection.onion_service_port =
            parse_port(options.one("onion-port"), "--onion-port");
        selection.kind = ServePublicationKind::TorOnionService;
    } else if (transport == "i2p") {
        reject_route_options_or_throw(
            options,
            {"onion-address", "onion-port", "tor-socks-address",
             "tor-socks-port", "tor-isolation-token", "i2p-destination"},
            transport);
        if (!options.has("i2p-private-destination-file")) {
            throw std::invalid_argument(
                "--transport i2p serving requires "
                "--i2p-private-destination-file for a persistent service identity");
        }
        anonsync::SyncReplicaI2pSamForwardRoute forward{
            .bridge = {
                options.one_or("i2p-sam-address", "127.0.0.1"),
                parse_port(
                    options.one_or("i2p-sam-port", "7656"),
                    "--i2p-sam-port")},
            .session_id = options.has("i2p-session-id")
                ? options.one("i2p-session-id")
                : "anonsync-serve-" + random_hex_token_or_throw(
                      16U, "anonsync_replica inbound I2P SAM session"),
            .session_destination =
                read_i2p_private_destination_or_throw(options),
            .forward_endpoint = selection.listener_endpoint,
            .inbound_quantity = i2p_tunnel_quantity_from_options(
                options, "i2p-inbound-quantity"),
            .outbound_quantity = i2p_tunnel_quantity_from_options(
                options, "i2p-outbound-quantity")};
        anonsync::validate_sync_replica_i2p_sam_forward_route_or_throw(
            forward, "anonsync_replica inbound I2P SAM forward route");
        selection.i2p_forward = std::move(forward);
        selection.kind = ServePublicationKind::I2pSamForward;
    } else {
        throw std::invalid_argument(
            "--transport must be one of direct, tor, or i2p");
    }
    return selection;
}

[[nodiscard]] std::uint64_t receiver_timeout_from_options(
    const Options& options,
    ServePublicationKind publication_kind) {
    const std::uint64_t fallback =
        publication_kind == ServePublicationKind::I2pSamForward
        ? kDefaultI2pTimeoutSeconds
        : kDefaultTimeoutSeconds;
    const std::uint64_t timeout = option_uint64_or(
        options, "timeout-seconds", fallback);
    if (timeout == 0U || timeout > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            "--timeout-seconds must be in [1, 3600]");
    }
    if (publication_kind == ServePublicationKind::I2pSamForward &&
        timeout < kMinimumI2pTimeoutSeconds) {
        throw std::invalid_argument(
            "--timeout-seconds must be at least 180 for --transport i2p");
    }
    return timeout;
}

[[nodiscard]] std::uint64_t max_sessions_from_options(
    const Options& options) {
    const std::uint64_t maximum = parse_uint64(
        options.one("max-sessions"), "--max-sessions");
    if (maximum == 0U || maximum > kMaximumBatchSessions) {
        throw std::invalid_argument(
            "--max-sessions must be in [1, 256]");
    }
    return maximum;
}

[[nodiscard]] std::uint64_t max_runtime_from_options(
    const Options& options) {
    const std::uint64_t maximum = parse_uint64(
        options.one("max-runtime-seconds"), "--max-runtime-seconds");
    if (maximum == 0U || maximum > kMaximumRuntimeSeconds) {
        throw std::invalid_argument(
            "--max-runtime-seconds must be in [1, 86400]");
    }
    return maximum;
}

[[nodiscard]] std::unique_ptr<anonsync::SyncReplicaOutboxClockSource>
outbox_clock_source_from_options(const Options& options) {
    const bool has_authority = options.has("operator-clock-authority-id");
    const bool has_uncertainty =
        options.has("operator-clock-uncertainty-ns");
    if (has_authority != has_uncertainty) {
        throw std::invalid_argument(
            "--operator-clock-authority-id and "
            "--operator-clock-uncertainty-ns must be supplied together");
    }
    if (!has_authority) return {};
    return anonsync::
        make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
            {options.one("operator-clock-authority-id"),
             parse_uint64(
                 options.one("operator-clock-uncertainty-ns"),
                 "--operator-clock-uncertainty-ns")});
}

[[nodiscard]] anonsync::SyncReplicaFileDeliveryServiceLimits
file_service_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaFileDeliveryServiceLimits limits;
    // The legacy file-delivery protocol owns one complete payload inside one
    // frame. Keep that compatibility surface at its reviewed 4 MiB ceiling;
    // larger configured files travel through resumable reconciliation ranges.
    const std::uint64_t bounded_payload_bytes =
        anonsync::sync_replica_file_delivery_single_frame_payload_limit(
            max_payload_bytes);
    limits.max_payload_bytes = bounded_payload_bytes;

    // Preserve the protocol's reviewed default non-payload headroom instead
    // of guessing that a small fixed increment can contain the independently
    // bounded evidence request. The service constructor still validates the
    // complete relationship before any durable or network authority is spent.
    static_assert(
        anonsync::kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes >=
        anonsync::kSyncReplicaFileDeliveryDefaultMaxPayloadBytes);
    constexpr std::uint64_t kDefaultNonPayloadHeadroom =
        anonsync::kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes -
        anonsync::kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
    if (bounded_payload_bytes >
        std::numeric_limits<std::uint64_t>::max() -
            kDefaultNonPayloadHeadroom) {
        throw std::invalid_argument("payload request-frame ceiling overflow");
    }
    limits.max_request_frame_bytes =
        bounded_payload_bytes + kDefaultNonPayloadHeadroom;
    return limits;
}

[[nodiscard]] anonsync::SyncReplicaReconciliationProtocolLimits
reconciliation_protocol_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaReconciliationProtocolLimits limits;
    limits.max_single_payload_bytes =
        anonsync::sync_replica_reconciliation_single_payload_limit(
            max_payload_bytes);
    // Complete file extent is deployment-specific; each response remains
    // independently bounded by the reviewed range and page ceilings.
    limits.max_payload_bytes_per_page =
        anonsync::kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;
    limits.max_payload_extent_bytes = max_payload_bytes;
    anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
        limits);
    return limits;
}

[[nodiscard]] anonsync::SyncReplicaFilePayloadStoreLimits
payload_store_limits(std::uint64_t max_payload_bytes) {
    return anonsync::
        sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
            max_payload_bytes,
            "anonsync_replica payload-store production limits");
}

[[nodiscard]] anonsync::SyncReplicaFileEffectSqliteOwnerLimits
effect_owner_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits limits;
    // The durable effect owner belongs only to the legacy one-frame delivery
    // path. Resumable reconciliation owns larger configured file extents, so
    // widening this whole-payload store would add memory authority without a
    // shipping caller that can use it.
    limits.max_payload_bytes =
        anonsync::sync_replica_file_delivery_single_frame_payload_limit(
            max_payload_bytes);
    return limits;
}

enum class DatabaseOpenDisposition : std::uint8_t {
    ExistingOperational = 1U,
    ExistingBootstrapCandidate = 2U,
    ExistingForensicReadOnly = 3U,
};

void validate_database_open_disposition_or_throw(
    DatabaseOpenDisposition disposition,
    const std::string& label) {
    switch (disposition) {
        case DatabaseOpenDisposition::ExistingOperational:
        case DatabaseOpenDisposition::ExistingBootstrapCandidate:
        case DatabaseOpenDisposition::ExistingForensicReadOnly:
            return;
    }
    throw std::invalid_argument(
        label + " database open disposition is invalid");
}

class UnadoptedSqliteConnection final {
public:
    UnadoptedSqliteConnection() = default;
    ~UnadoptedSqliteConnection() noexcept {
        if (handle_ == nullptr) return;
        if (sqlite3_close(handle_) != SQLITE_OK) {
            // A fresh open candidate cannot legitimately own statements or
            // backups. close_v2 is only the no-throw last resort for an
            // exceptional SQLite implementation path during stack unwind.
            (void)sqlite3_close_v2(handle_);
        }
        handle_ = nullptr;
    }

    UnadoptedSqliteConnection(const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection& operator=(
        const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection(UnadoptedSqliteConnection&&) = delete;
    UnadoptedSqliteConnection& operator=(
        UnadoptedSqliteConnection&&) = delete;

    [[nodiscard]] sqlite3** out() noexcept { return &handle_; }
    [[nodiscard]] sqlite3* get() const noexcept { return handle_; }

    [[nodiscard]] sqlite3* release() noexcept {
        sqlite3* released = handle_;
        handle_ = nullptr;
        return released;
    }

    [[nodiscard]] int close_noexcept() noexcept {
        if (handle_ == nullptr) return SQLITE_OK;
        const int result = sqlite3_close(handle_);
        if (result == SQLITE_OK) handle_ = nullptr;
        return result;
    }

private:
    sqlite3* handle_ = nullptr;
};


// Product file-backed SQLite authority. Declaration order is intentional:
// reverse destruction closes the exact connection before unregistering its
// private descriptor-rooted VFS, then releases the retained path guard.
class ProductSqliteDatabaseAuthority final {
private:
    anonsync::SqlitePathFamilyGuard path_guard_;
    std::unique_ptr<anonsync::SqliteDescriptorRootedVfs> rooted_vfs_;

public:
    anonsync::SyncSqliteDbHandleSlot db;

    ProductSqliteDatabaseAuthority() = default;
    ProductSqliteDatabaseAuthority(
        anonsync::SqlitePathFamilyGuard path_guard,
        std::unique_ptr<anonsync::SqliteDescriptorRootedVfs> rooted_vfs)
        : path_guard_(std::move(path_guard)),
          rooted_vfs_(std::move(rooted_vfs)) {
        if (!rooted_vfs_) {
            throw std::invalid_argument(
                "product SQLite authority requires a rooted VFS");
        }
    }
    ~ProductSqliteDatabaseAuthority() = default;
    ProductSqliteDatabaseAuthority(
        const ProductSqliteDatabaseAuthority&) = delete;
    ProductSqliteDatabaseAuthority& operator=(
        const ProductSqliteDatabaseAuthority&) = delete;
    ProductSqliteDatabaseAuthority(
        ProductSqliteDatabaseAuthority&& other) noexcept
        : path_guard_(std::move(other.path_guard_)),
          rooted_vfs_(std::move(other.rooted_vfs_)),
          db(std::move(other.db)) {}
    ProductSqliteDatabaseAuthority& operator=(
        ProductSqliteDatabaseAuthority&& other) noexcept {
        if (this == &other) return *this;

        // Move assignment is also an authority replacement boundary. Revoke
        // in reverse ownership order before acquiring the incoming family.
        db = anonsync::SyncSqliteDbHandleSlot{};
        rooted_vfs_.reset();
        path_guard_ = anonsync::SqlitePathFamilyGuard{};
        path_guard_ = std::move(other.path_guard_);
        rooted_vfs_ = std::move(other.rooted_vfs_);
        db = std::move(other.db);
        return *this;
    }

    [[nodiscard]] const char* vfs_name_or_throw(
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(label + " has no descriptor-rooted VFS");
        }
        return rooted_vfs_->name();
    }

    void verify_open_database_or_throw(const std::string& label) {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = db.borrow();
        rooted_vfs_->verify_open_database_or_throw(
            borrow.get(), label + " descriptor-rooted connection proof");
        path_guard_.verify_open_database_or_throw(
            borrow.get(), label + " logical-path authority proof");
    }

    [[nodiscard]] std::string
    read_bounded_main_file_before_open_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        return rooted_vfs_->read_bounded_main_file_before_open_or_throw(
            maximum_bytes, label);
    }

    [[nodiscard]] std::string read_bounded_main_file_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " live main-file read");
        return rooted_vfs_->read_bounded_main_file_or_throw(
            borrow.get(), maximum_bytes, label);
    }

    void verify_sidecars_absent_or_throw(const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        rooted_vfs_->verify_sidecars_absent_or_throw(label);
    }

    void verify_sidecar_absent_or_throw(
        std::string_view suffix,
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        rooted_vfs_->verify_sidecar_absent_or_throw(suffix, label);
    }

    void sync_main_file_and_parent_directory_or_throw(
        const std::string& label) const {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " live main-file sync");
        rooted_vfs_->sync_main_file_and_parent_directory_or_throw(
            borrow.get(), label);
    }
};

[[noreturn]] void reject_unadopted_database_handle_or_throw(
    UnadoptedSqliteConnection& candidate,
    std::string message) {
    // sqlite3_open_v2 usually returns a diagnostic handle even on failure.
    // Until writability has been proved, that handle has not crossed the
    // product's connection-authority frontier and must never enter the strict
    // SyncSqliteDbHandleSlot.
    if (candidate.close_noexcept() != SQLITE_OK) {
        message += "; unadopted SQLite handle could not be closed";
    }
    throw std::runtime_error(std::move(message));
}

[[nodiscard]] bool database_has_persistent_schema_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database,
        "SELECT 1 FROM main.sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%' LIMIT 1;",
        label + " persistent-schema probe");
    const int row = sqlite3_step(statement.stmt);
    if (row == SQLITE_DONE) return false;
    if (row != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " persistent-schema probe");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " persistent-schema probe returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " persistent-schema trailing-row probe");
    }
    return true;
}

[[nodiscard]] std::string database_journal_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database, "PRAGMA main.journal_mode;",
        label + " journal-mode probe");
    const int row = sqlite3_step(statement.stmt);
    if (row == SQLITE_DONE) {
        throw std::runtime_error(
            label + " journal-mode probe returned no row");
    }
    if (row != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " journal-mode probe");
    }
    const std::string mode = anonsync::sqlite_column_text_or_throw(
        statement.stmt, 0, label + " journal-mode value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " journal-mode probe returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " journal-mode trailing-row probe");
    }
    return mode;
}

void require_wal_journal_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    const std::string mode = database_journal_mode_or_throw(database, label);
    if (mode != "wal") {
        throw std::runtime_error(
            label + " journal mode is " + mode + ", expected wal");
    }
}

void require_sealed_rollback_sidecars_absent_or_throw(
    const ProductSqliteDatabaseAuthority& database,
    const std::string& label) {
    try {
        database.verify_sidecars_absent_or_throw(label);
    } catch (const std::runtime_error& error) {
        const std::string detail(error.what());
        if (detail.find("SQLite sidecar must be absent") ==
            std::string::npos) {
            throw;
        }
        throw std::runtime_error(
            label + " sealed rollback bootstrap candidate has sidecar: " +
            detail);
    }
}

void require_bootstrap_candidate_header_and_namespace_or_throw(
    const ProductSqliteDatabaseAuthority& database,
    const std::string& label) {
    constexpr std::string_view kSqliteHeader("SQLite format 3\0", 16U);
    constexpr std::size_t kMinimumDatabaseHeaderBytes = 100U;
    const std::string image =
        database.read_bounded_main_file_before_open_or_throw(
            kMaximumBootstrapSqliteImageBytes,
            label + " immutable main-file preflight");
    if (image.size() < kMinimumDatabaseHeaderBytes ||
        std::string_view(image.data(), kSqliteHeader.size()) != kSqliteHeader) {
        throw std::runtime_error(
            label + " main file is not a complete SQLite database image");
    }

    const auto write_version =
        static_cast<unsigned char>(image[18]);
    const auto read_version =
        static_cast<unsigned char>(image[19]);
    if (write_version == 1U && read_version == 1U) {
        // A sealed genesis image is a self-contained rollback-mode main file.
        // Reject every sidecar before SQLite gets an opportunity to interpret,
        // recover, delete, or otherwise mutate a contaminated namespace.
        require_sealed_rollback_sidecars_absent_or_throw(database, label);
        return;
    }
    if (write_version == 2U && read_version == 2U) {
        database.verify_sidecar_absent_or_throw(
            "-journal", label + " WAL bootstrap candidate");
        return;
    }
    throw std::runtime_error(
        label + " SQLite header has unsupported read/write journal versions " +
        std::to_string(read_version) + "/" +
        std::to_string(write_version));
}

void retain_exclusive_connection_locking_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database, "PRAGMA main.locking_mode=EXCLUSIVE;",
        label + " exclusive locking-mode prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        if (row == SQLITE_DONE) {
            throw std::runtime_error(
                label + " exclusive locking-mode request returned no row");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " exclusive locking-mode request");
    }
    const std::string mode = anonsync::sqlite_column_text_or_throw(
        statement.stmt, 0, label + " exclusive locking-mode value");
    if (mode != "exclusive") {
        throw std::runtime_error(
            label + " could not retain exclusive SQLite locking mode");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " exclusive locking-mode request returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " exclusive locking-mode trailing step");
    }
}

void configure_operational_database_profile_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    require_wal_journal_mode_or_throw(database, label);
    anonsync::sqlite_exec_or_throw(
        database,
        "PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;"
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " durability profile");
}

void configure_forensic_database_profile_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    // Retain an exclusive connection-local lock before the first page read.
    // SQLite then keeps the WAL index in heap memory instead of joining or
    // creating a persistent -shm coordination domain. The forensic VFS gives
    // SQLite a private anonymous WAL snapshot and independently denies all
    // mutation of the selected deployment's database family.
    retain_exclusive_connection_locking_mode_or_throw(
        database, label + " connection-local WAL index");
    anonsync::configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw(
        database, label + " closed connection profile");
    anonsync::sqlite_exec_or_throw(
        database,
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;",
        label + " observer pragmas");
}

[[nodiscard]] ProductSqliteDatabaseAuthority open_database_or_throw(
    const fs::path& path,
    const std::string& label,
    DatabaseOpenDisposition disposition) {
    validate_database_open_disposition_or_throw(disposition, label);

    anonsync::SqlitePathFamilyGuard path_guard =
        anonsync::guard_sqlite_path_family_or_throw(
            path, false, {"-journal", "-wal", "-shm"},
            label + " path authority");
    if (!path_guard.parent_exists() ||
        !path_guard.database_existed_at_preflight()) {
        throw std::runtime_error(
            label + " unable to open database file: requires an existing "
                    "guarded main database");
    }
    const fs::path logical_path = path_guard.database_path();

    const bool forensic_read_only =
        disposition == DatabaseOpenDisposition::ExistingForensicReadOnly;
    auto rooted_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            path_guard,
            forensic_read_only
                ? anonsync::SqliteDescriptorRootedVfsAccess::ReadOnlyExisting
                : anonsync::SqliteDescriptorRootedVfsAccess::ReadWriteExisting,
            label + " descriptor-rooted VFS");
    ProductSqliteDatabaseAuthority database(
        std::move(path_guard), std::move(rooted_vfs));
    if (disposition ==
        DatabaseOpenDisposition::ExistingBootstrapCandidate) {
        // The retained parent descriptor and frozen main-file identity define
        // the exact namespace that both this preflight and every later SQLite
        // family operation will inspect. Ambient ancestor rebinding cannot
        // splice a different image or sidecar set between preflight and xOpen.
        require_bootstrap_candidate_header_and_namespace_or_throw(
            database, label + " bootstrap candidate pre-open");
    }

    int flags = (forensic_read_only ? SQLITE_OPEN_READONLY
                                    : SQLITE_OPEN_READWRITE) |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    UnadoptedSqliteConnection candidate;
    const int opened = sqlite3_open_v2(
        logical_path.string().c_str(), candidate.out(), flags,
        database.vfs_name_or_throw(label));
    if (opened != SQLITE_OK) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            anonsync::sqlite_error_message(candidate.get(), label + " open"));
    }
    if (candidate.get() == nullptr) {
        throw std::runtime_error(label + " open returned no SQLite handle");
    }
    const int read_only = sqlite3_db_readonly(candidate.get(), "main");
    if ((!forensic_read_only && read_only != 0) ||
        (forensic_read_only && read_only != 1)) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            label + (forensic_read_only
                ? " open could not prove main-database read-only authority"
                : (read_only > 0
                    ? " open fell back to a read-only main database"
                    : " open could not prove main-database writability")));
    }

    {
        auto output = database.db.out();
        sqlite3** destination = output.get();
        *destination = candidate.release();
    }
    database.verify_open_database_or_throw(
        label + " post-open path attestation");
    anonsync::sqlite_set_busy_timeout_or_throw(
        database.db, 5000, label + " busy timeout");
    if (disposition ==
        DatabaseOpenDisposition::ExistingBootstrapCandidate) {
        // The first subsequent database read obtains and retains SQLite's file
        // lock for this exact connection. That closes the ordinary-writer gap
        // between set-wide identity proof, durability reconciliation, WAL
        // promotion, and role-state attestation. Descriptor-rooted sidecars
        // prevent a parent-path substitution from redirecting that lock family.
        retain_exclusive_connection_locking_mode_or_throw(
            database.db, label + " bootstrap candidate");
    } else if (forensic_read_only) {
        configure_forensic_database_profile_or_throw(
            database.db, label + " forensic read-only");
    }
    const bool has_persistent_schema =
        database_has_persistent_schema_or_throw(database.db, label);
    if (!has_persistent_schema) {
        throw std::runtime_error(
            label + " has no persistent schema and requires explicit "
            "bootstrap");
    }
    if (disposition == DatabaseOpenDisposition::ExistingOperational) {
        // journal_mode is persistent. Operational commands observe the
        // reviewed profile instead of silently rewriting an unrelated or
        // incompletely initialized target before its exact owner attests it.
        configure_operational_database_profile_or_throw(database.db, label);
    } else if (disposition ==
               DatabaseOpenDisposition::ExistingBootstrapCandidate) {
        const std::string mode =
            database_journal_mode_or_throw(database.db, label);
        if (mode != "delete" && mode != "wal") {
            throw std::runtime_error(
                label + " bootstrap candidate journal mode is " + mode +
                ", expected delete or wal");
        }
    }
    database.verify_open_database_or_throw(
        label + " post-profile path attestation");
    return database;
}

[[nodiscard]] anonsync::SyncSqliteDb
open_detached_bootstrap_database_or_throw(const std::string& label) {
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    UnadoptedSqliteConnection candidate;
    const int opened = sqlite3_open_v2(
        ":memory:", candidate.out(), flags, nullptr);
    if (opened != SQLITE_OK) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            anonsync::sqlite_error_message(candidate.get(), label + " open"));
    }
    if (candidate.get() == nullptr) {
        throw std::runtime_error(
            label + " detached open returned no SQLite handle");
    }
    const char* const filename = sqlite3_db_filename(candidate.get(), "main");
    if (filename == nullptr || *filename != '\0') {
        reject_unadopted_database_handle_or_throw(
            candidate, label + " detached bootstrap database names a file");
    }

    anonsync::SyncSqliteDb database;
    {
        auto output = database.db.out();
        sqlite3** destination = output.get();
        *destination = candidate.release();
    }
    if (database_has_persistent_schema_or_throw(database.db, label)) {
        throw std::logic_error(
            label + " detached bootstrap database is not empty");
    }
    anonsync::sqlite_exec_or_throw(
        database.db,
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " detached profile");
    return database;
}

[[nodiscard]] anonsync::SyncReplicaSqliteDeploymentBinding
sqlite_deployment_binding_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    return anonsync::SyncReplicaSqliteDeploymentBinding{
        .deployment = anonsync::sync_replica_deployment_identity_or_throw(
            deployment, label + " deployment identity"),
        .role = role,
        .database_path = database_path,
    };
}

[[nodiscard]] ProductSqliteDatabaseAuthority
open_bound_operational_database_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    ProductSqliteDatabaseAuthority database = open_database_or_throw(
        database_path, label,
        DatabaseOpenDisposition::ExistingOperational);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db,
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label),
        label + " store-set binding");
    return database;
}

[[nodiscard]] ProductSqliteDatabaseAuthority
open_bound_forensic_database_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    ProductSqliteDatabaseAuthority database = open_database_or_throw(
        database_path, label,
        DatabaseOpenDisposition::ExistingForensicReadOnly);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db,
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label),
        label + " store-set binding");
    return database;
}

[[nodiscard]] ProductSqliteDatabaseAuthority
open_bound_bootstrap_candidate_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    ProductSqliteDatabaseAuthority database = open_database_or_throw(
        database_path, label,
        DatabaseOpenDisposition::ExistingBootstrapCandidate);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db,
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label),
        label + " store-set binding");
    return database;
}

void initialize_detached_sqlite_deployment_binding_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    anonsync::
        initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
            database,
            sqlite_deployment_binding_or_throw(
                deployment, database_path, role, label),
            label + " detached store-set binding");
}

void acquire_bootstrap_candidate_read_lock_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database,
        "SELECT id FROM main.anonsync_store_set_binding WHERE id=1;",
        label + " read-lock prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        if (row == SQLITE_DONE) {
            throw std::runtime_error(
                label + " binding row disappeared before durability repair");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " read-lock step");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " binding read-lock query returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " read-lock trailing step");
    }
}

void promote_bound_bootstrap_candidate_to_operational_or_throw(
    ProductSqliteDatabaseAuthority& database,
    const anonsync::SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    const std::string mode = database_journal_mode_or_throw(database.db, label);
    if (mode == "delete") {
        require_sealed_rollback_sidecars_absent_or_throw(database, label);

        // Pin a rollback-mode read transaction while the exact main-file image
        // is read and flushed through SQLite's already-open main sqlite3_file.
        // This is essential on POSIX: opening and then closing an independent
        // descriptor for the same inode can release locks held by SQLite in the
        // process. The retained parent descriptor still prevents ambient
        // ancestor rebinding from substituting the bytes or directory.
        anonsync::SyncSqliteTransaction pin(
            database.db, label + " durability pin",
            anonsync::SyncSqliteTransactionMode::Deferred);
        acquire_bootstrap_candidate_read_lock_or_throw(
            database.db, label + " durability pin");
        const std::string exact_before =
            database.read_bounded_main_file_or_throw(
                kMaximumBootstrapSqliteImageBytes,
                label + " exact sealed image before durability flush");
        database.sync_main_file_and_parent_directory_or_throw(
            label + " sealed image durability flush");
        const std::string exact_after =
            database.read_bounded_main_file_or_throw(
                kMaximumBootstrapSqliteImageBytes,
                label + " exact sealed image after durability flush");
        if (exact_before != exact_after) {
            throw std::runtime_error(
                label + " sealed image changed across durability flush");
        }
        pin.commit();

        anonsync::sqlite_exec_or_throw(
            database.db, "PRAGMA main.journal_mode=WAL;",
            label + " WAL promotion");
        require_wal_journal_mode_or_throw(
            database.db, label + " WAL promotion");
    } else if (mode != "wal") {
        throw std::runtime_error(
            label + " bootstrap candidate journal mode is " + mode +
            ", expected delete or wal");
    }

    configure_operational_database_profile_or_throw(database.db, label);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, binding, label + " post-promotion binding");
    database.verify_open_database_or_throw(
        label + " post-promotion path attestation");
}

template <typename InitializeAndVerifyRole>
void create_sealed_bootstrap_database_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label,
    InitializeAndVerifyRole&& initialize_and_verify_role) {
    const anonsync::SyncReplicaSqliteDeploymentBinding binding =
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label);
    anonsync::persistence::SealedSqliteSnapshot sealed = [&] {
        anonsync::SyncSqliteDb detached =
            open_detached_bootstrap_database_or_throw(
                label + " detached genesis image");
        initialize_detached_sqlite_deployment_binding_or_throw(
            detached.db, deployment, database_path, role,
            label + " detached genesis image");
        initialize_and_verify_role(detached.db);
        auto source = detached.db.borrow();
        return anonsync::persistence::SealedSqliteSnapshot::capture_database(
            source.get(),
            label + " sealed genesis image",
            anonsync::persistence::SqliteSnapshotSealPolicy{
                .maximum_bytes = kMaximumBootstrapSqliteImageBytes,
                .maximum_pages = kMaximumBootstrapSqliteImagePages,
            });
    }();
    // The earlier store-set inventory is only a planning observation. Reprove
    // the entire SQLite namespace family at the publication boundary so that
    // a late main file or sidecar cannot be silently adopted or combined with
    // this sealed genesis image. The create-new publisher independently makes
    // the final main-file transition no-replace atomic.
    require_fresh_database_family_or_throw(
        database_path, label + " prepublication namespace");
    sealed.publish_exact_copy_atomically_create_new_or_throw(
        database_path, label + " immutable genesis publication");

    ProductSqliteDatabaseAuthority published =
        open_bound_bootstrap_candidate_or_throw(
            deployment, database_path, role,
            label + " published genesis");
    promote_bound_bootstrap_candidate_to_operational_or_throw(
        published, binding, label + " published genesis");
}

[[nodiscard]] SslContextOwner load_tls_context_or_throw(
    const fs::path& certificate,
    const fs::path& private_key,
    const fs::path& ca_file,
    bool server,
    const std::string& label) {
    SslContextOwner context(SSL_CTX_new(TLS_method()), SSL_CTX_free);
    if (!context) throw_openssl(label + " could not allocate SSL_CTX");

    if (server) {
        anonsync::configure_sync_replica_tls13_server_context_or_throw(
            context.get(), label + " profile");
    } else {
        anonsync::configure_sync_replica_tls13_client_context_or_throw(
            context.get(), label + " profile");
    }

    ERR_clear_error();
    if (SSL_CTX_use_certificate_chain_file(
            context.get(), certificate.string().c_str()) != 1) {
        throw_openssl(label + " could not load certificate chain");
    }
    ERR_clear_error();
    if (SSL_CTX_use_PrivateKey_file(
            context.get(), private_key.string().c_str(),
            SSL_FILETYPE_PEM) != 1) {
        throw_openssl(label + " could not load private key");
    }
    ERR_clear_error();
    if (SSL_CTX_check_private_key(context.get()) != 1) {
        throw_openssl(label + " certificate/private key mismatch");
    }
    ERR_clear_error();
    if (SSL_CTX_load_verify_locations(
            context.get(), ca_file.string().c_str(), nullptr) != 1) {
        throw_openssl(label + " could not load CA trust file");
    }
    SSL_CTX_set_verify_depth(context.get(), 4);
    return context;
}

[[nodiscard]] const char* payload_put_name(
    anonsync::SyncReplicaFilePayloadStorePutDisposition disposition) noexcept {
    switch (disposition) {
        case anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted:
            return "inserted";
        case anonsync::SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent:
            return "already_present";
    }
    return "unknown";
}

[[nodiscard]] const char* receipt_apply_name(
    anonsync::SyncReplicaFileDeliveryReceiptApplyResult result) noexcept {
    using Result = anonsync::SyncReplicaFileDeliveryReceiptApplyResult;
    switch (result) {
        case Result::EffectSettled: return "effect_settled";
        case Result::ReceiverEffectCapacityBlocked:
            return "receiver_effect_capacity_blocked";
        case Result::ReceiverEffectPathBlocked:
            return "receiver_effect_path_blocked";
        case Result::ReceiverEvidenceCapacityBlocked:
            return "receiver_evidence_capacity_blocked";
        case Result::ReceiverEvidencePending:
            return "receiver_evidence_pending";
        case Result::ReceiverEvidenceQuarantined:
            return "receiver_evidence_quarantined";
        case Result::ReceiverProjectionBlocked:
            return "receiver_projection_blocked";
        case Result::ReceiverDestinationConflict:
            return "receiver_destination_conflict";
        case Result::IntentMissing: return "intent_missing";
        case Result::StaleClaim: return "stale_claim";
        case Result::ExpiredClaim: return "expired_claim";
    }
    return "unknown";
}

[[nodiscard]] const char* server_disposition_name(
    anonsync::SyncReplicaFileTlsServerDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileTlsServerDisposition;
    switch (disposition) {
        case Disposition::AcceptDeadlineExpired:
            return "accept_deadline_expired";
        case Disposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case Disposition::HandshakeRejected: return "handshake_rejected";
        case Disposition::PeerUnauthorized: return "peer_unauthorized";
        case Disposition::PeerClosed: return "peer_closed";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ReceiptDeadlineExpired:
            return "receipt_deadline_expired";
        case Disposition::ReceiptSent: return "receipt_sent";
    }
    return "unknown";
}

[[nodiscard]] const char* server_shutdown_name(
    anonsync::SyncReplicaFileTlsServerShutdownDisposition disposition) noexcept {
    using Disposition =
        anonsync::SyncReplicaFileTlsServerShutdownDisposition;
    switch (disposition) {
        case Disposition::NotAttempted: return "not_attempted";
        case Disposition::CloseNotifySent: return "close_notify_sent";
        case Disposition::Complete: return "complete";
        case Disposition::DeadlineExpired: return "deadline_expired";
        case Disposition::Failed: return "failed";
    }
    return "unknown";
}

[[nodiscard]] const char* receive_disposition_name(
    anonsync::SyncReplicaFileTlsReceiveDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileTlsReceiveDisposition;
    switch (disposition) {
        case Disposition::PeerClosed: return "peer_closed";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ReceiptDeadlineExpired:
            return "receipt_deadline_expired";
        case Disposition::ReceiptSent: return "receipt_sent";
    }
    return "unknown";
}

[[nodiscard]] const char* file_receipt_disposition_name(
    anonsync::SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileDeliveryReceiptDisposition;
    switch (disposition) {
        case Disposition::Published: return "published";
        case Disposition::AlreadyPublished: return "already_published";
        case Disposition::EffectCapacityBlocked:
            return "effect_capacity_blocked";
        case Disposition::EvidenceCapacityBlocked:
            return "evidence_capacity_blocked";
        case Disposition::EvidencePending: return "evidence_pending";
        case Disposition::EvidenceQuarantined:
            return "evidence_quarantined";
        case Disposition::ProjectionBlocked: return "projection_blocked";
        case Disposition::DestinationConflict:
            return "destination_conflict";
        case Disposition::EffectPathBlocked: return "effect_path_blocked";
    }
    return "unknown";
}

[[nodiscard]] const char* peer_server_disposition_name(
    anonsync::SyncReplicaPeerTlsServerDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaPeerTlsServerDisposition;
    switch (disposition) {
        case Disposition::AcceptDeadlineExpired:
            return "accept_deadline_expired";
        case Disposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case Disposition::HandshakeRejected: return "handshake_rejected";
        case Disposition::PeerUnauthorized: return "peer_unauthorized";
        case Disposition::ApplicationServed: return "application_served";
    }
    return "unknown";
}

[[nodiscard]] const char* reconciliation_pull_disposition_name(
    anonsync::SyncReplicaReconciliationTlsPullDisposition disposition) noexcept {
    using Disposition =
        anonsync::SyncReplicaReconciliationTlsPullDisposition;
    switch (disposition) {
        case Disposition::Complete: return "complete";
        case Disposition::RoundTripLimitReached:
            return "round_trip_limit_reached";
        case Disposition::SourceChangedLimitReached:
            return "source_changed_limit_reached";
        case Disposition::SourcePayloadUnavailable:
            return "source_payload_unavailable";
        case Disposition::SourcePayloadPreparing:
            return "source_payload_preparing";
        case Disposition::ReceiverCapacityBlocked:
            return "receiver_capacity_blocked";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ResponseDeadlineExpired:
            return "response_deadline_expired";
        case Disposition::PeerClosed: return "peer_closed";
    }
    return "unknown";
}

[[nodiscard]] const char* reconciliation_serve_disposition_name(
    anonsync::SyncReplicaReconciliationTlsServeDisposition disposition) noexcept {
    using Disposition =
        anonsync::SyncReplicaReconciliationTlsServeDisposition;
    switch (disposition) {
        case Disposition::Complete: return "complete";
        case Disposition::RoundTripLimitReached:
            return "round_trip_limit_reached";
        case Disposition::SourcePayloadUnavailable:
            return "source_payload_unavailable";
        case Disposition::SourcePayloadPreparing:
            return "source_payload_preparing";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ResponseDeadlineExpired:
            return "response_deadline_expired";
        case Disposition::PeerClosed: return "peer_closed";
    }
    return "unknown";
}

void append_client_session_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaFileTlsClientResult& result,
    bool include_transport = true) {
    const anonsync::SyncReplicaStreamConnectReport& route =
        result.stream_connect;
    output
        << ",\"disposition\":"
        << json_quote(anonsync::sync_replica_file_tls_client_disposition_name(
               result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(
               anonsync::
                   sync_replica_file_tls_client_shutdown_disposition_name(
                       result.shutdown_disposition))
        << ",\"connected\":" << json_bool(result.connected)
        << ",\"handshake_complete\":"
        << json_bool(result.handshake_complete)
        << ",\"peer_authenticated\":"
        << json_bool(result.peer_authenticated);
    if (include_transport) {
        output << ",\"transport\":"
               << json_quote(anonsync::sync_replica_stream_route_kind_name(
                      route.route_kind));
    }
    output
        << ",\"route_disposition\":"
        << json_quote(anonsync::sync_replica_stream_connect_disposition_name(
               route.disposition))
        << ",\"route_terminal_stage\":"
        << json_quote(anonsync::sync_replica_stream_route_stage_name(
               route.terminal_stage))
        << ",\"route_negotiated\":" << json_bool(route.route_negotiated)
        << ",\"route_bytes_written\":" << route.route_bytes_written
        << ",\"route_bytes_received\":" << route.route_bytes_received
        << ",\"route_numeric_connect_attempts\":"
        << route.numeric_connect_attempts
        << ",\"route_control_session_created\":"
        << json_bool(route.control_session_created)
        << ",\"route_control_session_reused\":"
        << json_bool(route.control_session_reused)
        << ",\"route_control_session_stale_detected\":"
        << json_bool(route.control_session_stale_detected)
        << ",\"route_control_session_recovered\":"
        << json_bool(route.control_session_recovered)
        << ",\"connect_attempts\":" << result.connect_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts
        << ",\"request_frame_bytes\":" << result.request_frame_bytes
        << ",\"request_body_bytes_written\":"
        << result.request_body_bytes_written
        << ",\"receipt_frame_bytes\":" << result.receipt_frame_bytes;
    if (result.operation_id.has_value()) {
        output << ",\"operation_id\":" << json_quote(*result.operation_id);
    }
    if (result.claim_id.has_value()) {
        output << ",\"claim_id\":" << json_quote(*result.claim_id);
    }
    if (result.peer_spki_sha256.has_value()) {
        output << ",\"peer_spki_sha256\":"
               << json_quote(*result.peer_spki_sha256);
    }
    if (result.receipt_apply_result.has_value()) {
        output << ",\"receipt_apply_result\":"
               << json_quote(receipt_apply_name(
                      *result.receipt_apply_result));
    }
    if (result.connect_error.has_value()) {
        output << ",\"connect_error\":" << *result.connect_error;
    }
    if (route.socks5_reply.has_value()) {
        output << ",\"route_socks5_reply\":"
               << static_cast<unsigned int>(*route.socks5_reply);
    }
    if (route.sam_result.has_value()) {
        output << ",\"route_sam_result\":"
               << json_quote(anonsync::sync_replica_i2p_sam_result_name(
                      *route.sam_result));
    }
}

void append_file_receive_json_fields(
    std::ostream& output,
    const std::optional<anonsync::SyncReplicaFileTlsReceiveResult>& receive) {
    if (!receive.has_value()) return;
    output
        << ",\"receive_disposition\":"
        << json_quote(receive_disposition_name(receive->disposition))
        << ",\"request_prefix_bytes_received\":"
        << receive->request_prefix_bytes_received
        << ",\"request_frame_bytes\":" << receive->request_frame_bytes
        << ",\"request_body_bytes_received\":"
        << receive->request_body_bytes_received
        << ",\"receipt_write_started\":"
        << json_bool(receive->receipt_write_started)
        << ",\"receipt_prefix_bytes_written\":"
        << receive->receipt_prefix_bytes_written
        << ",\"receipt_prefix_accepted\":"
        << json_bool(receive->receipt_prefix_accepted)
        << ",\"receipt_frame_bytes\":" << receive->receipt_frame_bytes
        << ",\"receipt_body_bytes_written\":"
        << receive->receipt_body_bytes_written;
    if (receive->inbound.has_value()) {
        output << ",\"receipt_disposition\":"
               << json_quote(file_receipt_disposition_name(
                      receive->inbound->receipt.disposition))
               << ",\"operation_id\":"
               << json_quote(
                      receive->inbound->request.evidence_request.operation
                          .operation_id);
    }
}

void append_reconciliation_payload_continuation_json_fields(
    std::ostream& output,
    const std::optional<
        anonsync::SyncReplicaReconciliationPayloadContinuation>& continuation,
    std::string_view field_prefix = {}) {
    if (!continuation.has_value()) return;
    output
        << ",\"" << field_prefix << "payload_operation_id\":"
        << json_quote(continuation->operation_id)
        << ",\"" << field_prefix << "payload_content_sha256\":"
        << json_quote(continuation->content_sha256)
        << ",\"" << field_prefix << "payload_total_size_bytes\":"
        << continuation->total_size_bytes
        << ",\"" << field_prefix << "payload_next_offset_bytes\":"
        << continuation->next_offset_bytes;
}

void append_reconciliation_serve_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaReconciliationTlsServeResult& result) {
    output
        << ",\"reconciliation_disposition\":"
        << json_quote(reconciliation_serve_disposition_name(
               result.disposition))
        << ",\"reconciliation_requests_received\":"
        << result.requests_received
        << ",\"reconciliation_responses_written\":"
        << result.responses_written
        << ",\"reconciliation_pages_served\":" << result.pages_served
        << ",\"reconciliation_source_changed_responses\":"
        << result.source_changed_responses
        << ",\"reconciliation_payload_unavailable_responses\":"
        << result.payload_unavailable_responses
        << ",\"reconciliation_payload_targeted_access_births\":"
        << result.payload_targeted_access_births
        << ",\"reconciliation_payload_targeted_open_attempts\":"
        << result.payload_targeted_open_attempts
        << ",\"reconciliation_payload_targeted_opens\":"
        << result.payload_targeted_opens
        << ",\"reconciliation_content_defined_manifest_scans\":"
        << result.content_defined_manifest_scans
        << ",\"reconciliation_content_defined_manifest_reuses\":"
        << result.content_defined_manifest_reuses
        << ",\"reconciliation_content_defined_manifest_hashed_bytes\":"
        << result.content_defined_manifest_hashed_bytes
        << ",\"reconciliation_content_defined_manifest_projection_steps\":"
        << result.content_defined_manifest_projection_steps
        << ",\"reconciliation_content_defined_manifest_projection_restarts\":"
        << result.content_defined_manifest_projection_restarts
        << ",\"reconciliation_source_payload_preparing_responses\":"
        << result.source_payload_preparing_responses
        << ",\"reconciliation_content_defined_manifest_publications\":"
        << result.content_defined_manifest_publications
        << ",\"reconciliation_content_defined_manifest_references\":"
        << result.content_defined_manifest_references
        << ",\"reconciliation_content_defined_chunk_index_builds\":"
        << result.content_defined_chunk_index_builds
        << ",\"reconciliation_content_defined_chunk_index_reuses\":"
        << result.content_defined_chunk_index_reuses
        << ",\"reconciliation_content_defined_chunk_index_lookups\":"
        << result.content_defined_chunk_index_lookups
        << ",\"reconciliation_ranged_payload_windows\":"
        << result.ranged_payload_windows
        << ",\"reconciliation_ranged_payload_ranges\":"
        << result.ranged_payload_ranges
        << ",\"reconciliation_ranged_payload_bytes\":"
        << result.ranged_payload_bytes
        << ",\"reconciliation_request_frame_bytes_received\":"
        << result.request_frame_bytes_received
        << ",\"reconciliation_response_frame_bytes_written\":"
        << result.response_frame_bytes_written
        << ",\"reconciliation_response_direct_source_frames\":"
        << result.response_direct_source_frames
        << ",\"reconciliation_response_direct_source_frame_payload_bytes\":"
        << result.response_direct_source_frame_payload_bytes
        << ",\"reconciliation_response_direct_source_frame_maximum_staging_bytes\":"
        << result.response_direct_source_frame_maximum_staging_bytes
        << ",\"reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation\":"
        << result.response_direct_source_frame_payload_page_bytes_at_reservation
        << ",\"reconciliation_response_direct_source_frame_maximum_open_descriptors\":"
        << result.response_direct_source_frame_maximum_open_descriptors
        << ",\"reconciliation_response_frame_owned_handoffs\":"
        << result.response_frame_owned_handoffs
        << ",\"reconciliation_source_state_generation\":"
        << result.source_state_generation
        << ",\"reconciliation_source_evidence_count\":"
        << result.source_evidence_count
        << ",\"reconciliation_source_evidence_set_digest\":"
        << json_quote(result.source_evidence_set_digest)
        << ",\"reconciliation_has_more\":" << json_bool(result.has_more);
    if (result.next_after_operation_id.has_value()) {
        output << ",\"reconciliation_next_after_operation_id\":"
               << json_quote(*result.next_after_operation_id);
    }
    if (result.blocked_operation_id.has_value()) {
        output << ",\"reconciliation_blocked_operation_id\":"
               << json_quote(*result.blocked_operation_id);
    }
    append_reconciliation_payload_continuation_json_fields(
        output, result.payload_continuation, "reconciliation_");
}

void append_reconciliation_pull_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaReconciliationTlsPullResult& result) {
    output
        << ",\"pull_disposition\":"
        << json_quote(reconciliation_pull_disposition_name(result.disposition))
        << ",\"round_trips\":" << result.round_trips
        << ",\"pages_applied\":" << result.pages_applied
        << ",\"source_resets\":" << result.source_resets
        << ",\"source_payload_preparing_responses\":"
        << result.source_payload_preparing_responses
        << ",\"inserted_active\":" << result.inserted_active
        << ",\"inserted_pending\":" << result.inserted_pending
        << ",\"inserted_quarantined\":" << result.inserted_quarantined
        << ",\"duplicate_operations\":" << result.duplicate_operations
        << ",\"inserted_payloads\":" << result.inserted_payloads
        << ",\"existing_payloads\":" << result.existing_payloads
        << ",\"staged_payload_ranges\":"
        << result.staged_payload_ranges
        << ",\"staged_payload_bytes\":" << result.staged_payload_bytes
        << ",\"terminal_verification_steps\":"
        << result.terminal_verification_steps
        << ",\"terminal_verification_local_continuation_steps\":"
        << result.terminal_verification_local_continuation_steps
        << ",\"terminal_verification_step_budget_exhaustions\":"
        << result.terminal_verification_step_budget_exhaustions
        << ",\"reused_payload_chunks\":" << result.reused_payload_chunks
        << ",\"reused_payload_ranges\":" << result.reused_payload_ranges
        << ",\"reused_payload_bytes\":" << result.reused_payload_bytes
        << ",\"delta_local_reuse_read_ranges\":"
        << result.delta_local_reuse_read_ranges
        << ",\"delta_local_reuse_read_bytes\":"
        << result.delta_local_reuse_read_bytes
        << ",\"delta_local_reuse_maximum_read_range_bytes\":"
        << result.delta_local_reuse_maximum_read_range_bytes
        << ",\"delta_local_reuse_budget_exhaustions\":"
        << result.delta_local_reuse_budget_exhaustions
        << ",\"delta_local_reuse_interior_resumptions\":"
        << result.delta_local_reuse_interior_resumptions
        << ",\"delta_wire_already_durable_ranges\":"
        << result.delta_wire_already_durable_ranges
        << ",\"delta_wire_already_durable_bytes\":"
        << result.delta_wire_already_durable_bytes
        << ",\"delta_wire_overlap_trimmed_ranges\":"
        << result.delta_wire_overlap_trimmed_ranges
        << ",\"delta_predecessor_manifest_scans\":"
        << result.delta_predecessor_manifest_scans
        << ",\"delta_predecessor_manifest_reuses\":"
        << result.delta_predecessor_manifest_reuses
        << ",\"delta_predecessor_manifest_hashed_bytes\":"
        << result.delta_predecessor_manifest_hashed_bytes
        << ",\"target_content_defined_manifest_publications\":"
        << result.target_content_defined_manifest_publications
        << ",\"target_content_defined_manifest_reuses\":"
        << result.target_content_defined_manifest_reuses
        << ",\"delta_predecessor_index_builds\":"
        << result.delta_predecessor_index_builds
        << ",\"delta_predecessor_index_reuses\":"
        << result.delta_predecessor_index_reuses
        << ",\"delta_cross_file_candidate_pages\":"
        << result.delta_cross_file_candidate_pages
        << ",\"delta_cross_file_candidate_paths_scanned\":"
        << result.delta_cross_file_candidate_paths_scanned
        << ",\"delta_cross_file_unavailable_candidates\":"
        << result.delta_cross_file_unavailable_candidates
        << ",\"delta_cross_file_availability_generation_restarts\":"
        << result.delta_cross_file_availability_generation_restarts
        << ",\"delta_cross_file_manifest_scan_steps\":"
        << result.delta_cross_file_manifest_scan_steps
        << ",\"delta_cross_file_manifest_scans\":"
        << result.delta_cross_file_manifest_scans
        << ",\"delta_cross_file_manifest_reuses\":"
        << result.delta_cross_file_manifest_reuses
        << ",\"delta_cross_file_manifest_hashed_bytes\":"
        << result.delta_cross_file_manifest_hashed_bytes
        << ",\"delta_cross_file_candidate_matches\":"
        << result.delta_cross_file_candidate_matches
        << ",\"delta_cross_file_index_builds\":"
        << result.delta_cross_file_index_builds
        << ",\"delta_cross_file_index_reuses\":"
        << result.delta_cross_file_index_reuses
        << ",\"request_frame_bytes_written\":"
        << result.request_frame_bytes_written
        << ",\"response_frame_bytes_received\":"
        << result.response_frame_bytes_received
        << ",\"source_state_generation\":"
        << result.source_state_generation
        << ",\"source_evidence_count\":" << result.source_evidence_count
        << ",\"source_evidence_set_digest\":"
        << json_quote(result.source_evidence_set_digest)
        << ",\"has_more\":" << json_bool(result.has_more);
    if (result.next_after_operation_id.has_value()) {
        output << ",\"next_after_operation_id\":"
               << json_quote(*result.next_after_operation_id);
    }
    if (result.blocked_operation_id.has_value()) {
        output << ",\"blocked_operation_id\":"
               << json_quote(*result.blocked_operation_id);
    }
    append_reconciliation_payload_continuation_json_fields(
        output, result.payload_continuation);
}

void append_reconciliation_client_session_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaReconciliationTlsClientResult& result) {
    const anonsync::SyncReplicaStreamConnectReport& route =
        result.stream_connect;
    output
        << ",\"disposition\":"
        << json_quote(
               anonsync::sync_replica_reconciliation_tls_client_disposition_name(
                   result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(
               anonsync::
                   sync_replica_file_tls_client_shutdown_disposition_name(
                       result.shutdown_disposition))
        << ",\"connected\":" << json_bool(result.connected)
        << ",\"handshake_complete\":"
        << json_bool(result.handshake_complete)
        << ",\"peer_authenticated\":"
        << json_bool(result.peer_authenticated)
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(
               route.route_kind))
        << ",\"route_disposition\":"
        << json_quote(anonsync::sync_replica_stream_connect_disposition_name(
               route.disposition))
        << ",\"route_terminal_stage\":"
        << json_quote(anonsync::sync_replica_stream_route_stage_name(
               route.terminal_stage))
        << ",\"route_negotiated\":" << json_bool(route.route_negotiated)
        << ",\"route_bytes_written\":" << route.route_bytes_written
        << ",\"route_bytes_received\":" << route.route_bytes_received
        << ",\"route_numeric_connect_attempts\":"
        << route.numeric_connect_attempts
        << ",\"route_control_session_created\":"
        << json_bool(route.control_session_created)
        << ",\"route_control_session_reused\":"
        << json_bool(route.control_session_reused)
        << ",\"route_control_session_stale_detected\":"
        << json_bool(route.control_session_stale_detected)
        << ",\"route_control_session_recovered\":"
        << json_bool(route.control_session_recovered)
        << ",\"connect_attempts\":" << result.connect_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts;
    if (result.peer_spki_sha256.has_value()) {
        output << ",\"peer_spki_sha256\":"
               << json_quote(*result.peer_spki_sha256);
    }
    if (result.peer_actor.has_value()) {
        output << ",\"peer_device_id\":"
               << json_quote(result.peer_actor->device_id)
               << ",\"peer_epoch\":" << result.peer_actor->epoch;
    }
    if (result.connect_error.has_value()) {
        output << ",\"connect_error\":" << *result.connect_error;
    }
    if (route.socks5_reply.has_value()) {
        output << ",\"route_socks5_reply\":"
               << static_cast<unsigned int>(*route.socks5_reply);
    }
    if (route.sam_result.has_value()) {
        output << ",\"route_sam_result\":"
               << json_quote(anonsync::sync_replica_i2p_sam_result_name(
                      *route.sam_result));
    }
    if (result.pull.has_value()) {
        append_reconciliation_pull_json_fields(output, *result.pull);
    }
}

void append_server_session_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaFileTlsServerResult& result) {
    output
        << ",\"disposition\":"
        << json_quote(server_disposition_name(result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(server_shutdown_name(result.shutdown_disposition))
        << ",\"accepted\":" << json_bool(result.accepted)
        << ",\"handshake_complete\":"
        << json_bool(result.handshake_complete)
        << ",\"accept_attempts\":" << result.accept_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts
        << ",\"membership_state_generation\":"
        << result.membership_state_generation
        << ",\"membership_policy_epoch\":"
        << result.membership_policy_epoch;
    if (result.peer_spki_sha256.has_value()) {
        output << ",\"peer_spki_sha256\":"
               << json_quote(*result.peer_spki_sha256);
    }
    if (result.peer_actor.has_value()) {
        output << ",\"peer_device_id\":"
               << json_quote(result.peer_actor->device_id)
               << ",\"peer_epoch\":" << result.peer_actor->epoch;
    }
    append_file_receive_json_fields(output, result.receive);
}

void append_peer_server_session_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaPeerTlsServerResult& result) {
    output
        << ",\"disposition\":"
        << json_quote(peer_server_disposition_name(result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(server_shutdown_name(result.shutdown_disposition))
        << ",\"accepted\":" << json_bool(result.accepted)
        << ",\"handshake_complete\":"
        << json_bool(result.handshake_complete)
        << ",\"accept_attempts\":" << result.accept_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts
        << ",\"membership_state_generation\":"
        << result.membership_state_generation
        << ",\"membership_policy_epoch\":"
        << result.membership_policy_epoch;
    if (result.peer_spki_sha256.has_value()) {
        output << ",\"peer_spki_sha256\":"
               << json_quote(*result.peer_spki_sha256);
    }
    if (result.peer_actor.has_value()) {
        output << ",\"peer_device_id\":"
               << json_quote(result.peer_actor->device_id)
               << ",\"peer_epoch\":" << result.peer_actor->epoch;
    }
    if (!result.application.has_value()) return;
    output
        << ",\"application_disposition\":"
        << json_quote(anonsync::sync_replica_peer_tls_serve_disposition_name(
               result.application->disposition))
        << ",\"first_request_prefix_bytes_received\":"
        << result.application->first_request_prefix_bytes_received
        << ",\"first_request_frame_bytes\":"
        << result.application->first_request_frame_bytes
        << ",\"first_request_body_bytes_received\":"
        << result.application->first_request_body_bytes_received;
    append_file_receive_json_fields(output, result.application->file_delivery);
    if (result.application->reconciliation.has_value()) {
        append_reconciliation_serve_json_fields(
            output, *result.application->reconciliation);
    }
}

[[nodiscard]] const char* outbox_clock_health_name(
    anonsync::SyncReplicaOutboxClockHealth health) noexcept {
    switch (health) {
        case anonsync::SyncReplicaOutboxClockHealth::Uninitialized:
            return "uninitialized";
        case anonsync::SyncReplicaOutboxClockHealth::Healthy:
            return "healthy";
        case anonsync::SyncReplicaOutboxClockHealth::Quarantined:
            return "quarantined";
    }
    return "unknown";
}

[[nodiscard]] const char* outbox_clock_observation_outcome_name(
    anonsync::SyncReplicaOutboxClockObservationOutcome outcome) noexcept {
    using Outcome = anonsync::SyncReplicaOutboxClockObservationOutcome;
    switch (outcome) {
        case Outcome::Accepted: return "accepted";
        case Outcome::Quarantined: return "quarantined";
        case Outcome::AlreadyQuarantined: return "already_quarantined";
    }
    return "unknown";
}

[[nodiscard]] const char* clock_profile_name(bool operator_trusted) noexcept {
    return operator_trusted ? "operator-trusted" : "system";
}

void append_outbox_clock_state_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaOutboxClockState& state) {
    output
        << ",\"clock_health\":"
        << json_quote(outbox_clock_health_name(state.health))
        << ",\"clock_anomaly\":"
        << json_quote(anonsync::sync_replica_outbox_clock_anomaly_name(
               state.anomaly))
        << ",\"clock_high_water_epoch\":" << state.high_water_epoch
        << ",\"clock_observation_generation\":"
        << state.observation_generation
        << ",\"clock_recovery_generation\":"
        << state.recovery_generation
        << ",\"clock_accepted_observation_present\":"
        << json_bool(state.accepted.has_value())
        << ",\"clock_rejected_observation_present\":"
        << json_bool(state.rejected.has_value());
}

struct ProductStatusOutboxCounts final {
    std::uint64_t intents = 0U;
    std::uint64_t unclaimed = 0U;
    std::uint64_t claimable_at_high_water = 0U;
    std::uint64_t claimed_live_at_high_water = 0U;
    std::uint64_t expired_at_high_water = 0U;
    std::uint64_t retry_waiting_at_high_water = 0U;
    std::uint64_t dispatch_attempts = 0U;
};

[[nodiscard]] ProductStatusOutboxCounts summarize_outbox_at_high_water_or_throw(
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent>& outbox,
    std::uint64_t high_water_epoch) {
    ProductStatusOutboxCounts counts;
    counts.intents = static_cast<std::uint64_t>(outbox.size());
    for (const auto& intent : outbox) {
        const auto& lease = intent.lease;
        counts.dispatch_attempts += lease.dispatch_attempts;
        const bool claimable = high_water_epoch != 0U &&
            anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                lease, high_water_epoch, "anonsync_replica status outbox");
        if (claimable) ++counts.claimable_at_high_water;
        if (lease.claim_id.empty()) {
            if (lease.retry_not_before_epoch != 0U &&
                (high_water_epoch == 0U ||
                 lease.retry_not_before_epoch > high_water_epoch)) {
                ++counts.retry_waiting_at_high_water;
            } else {
                ++counts.unclaimed;
            }
            continue;
        }
        if (lease.lease_expires_at_epoch <= high_water_epoch) {
            ++counts.expired_at_high_water;
        } else {
            ++counts.claimed_live_at_high_water;
        }
    }
    return counts;
}

struct ProductStatusEffectCounts final {
    std::uint64_t staged = 0U;
    std::uint64_t published = 0U;
};

[[nodiscard]] ProductStatusEffectCounts summarize_effects(
    const std::vector<anonsync::SyncReplicaFileEffectRecord>& effects) {
    ProductStatusEffectCounts counts;
    for (const auto& effect : effects) {
        switch (effect.state) {
            case anonsync::SyncReplicaFileEffectState::Staged:
                ++counts.staged;
                break;
            case anonsync::SyncReplicaFileEffectState::Published:
                ++counts.published;
                break;
        }
    }
    return counts;
}

void require_paired_options(
    const Options& options,
    std::string_view first,
    std::string_view second) {
    if (options.has(first) != options.has(second)) {
        throw std::invalid_argument(
            "--" + std::string(first) + " and --" + std::string(second) +
            " must be supplied together");
    }
}

void require_all_or_none_options(
    const Options& options,
    std::initializer_list<std::string_view> names) {
    std::size_t supplied = 0U;
    for (const std::string_view name : names) {
        if (options.has(name)) ++supplied;
    }
    if (supplied == 0U || supplied == names.size()) return;

    std::ostringstream message;
    bool first = true;
    for (const std::string_view name : names) {
        if (!first) message << ", ";
        message << "--" << name;
        first = false;
    }
    throw std::invalid_argument(
        message.str() + " must be supplied together or all omitted");
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest
load_operational_deployment_manifest_or_throw(
    const Options& options,
    std::string_view command) {
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    return anonsync::read_sync_replica_deployment_manifest_or_throw(
        manifest_path,
        "anonsync_replica " + std::string(command) + " deployment manifest");
}


void append_deployment_authority_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment) {
    output
        << ",\"deployment_id\":"
        << json_quote(deployment.deployment_id)
        << ",\"deployment_manifest_digest\":"
        << json_quote(deployment.manifest_digest);
}

[[nodiscard]] const fs::path& require_payload_root(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.payload_root.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires a payload_root in the deployment manifest");
    }
    return *deployment.payload_root;
}

void require_effect_store(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.effect_db.has_value() ||
        !deployment.files_root.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires effect_db and files_root in the deployment manifest");
    }
}

void require_membership_store(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.membership_db.has_value() ||
        !deployment.anchor_db.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires membership_db and anchor_db in the deployment manifest");
    }
}

[[nodiscard]] anonsync::SyncReplicaTlsMembershipEntry parse_peer_entry(
    std::string_view encoded) {
    const std::size_t first = encoded.find(':');
    const std::size_t second = first == std::string_view::npos
        ? std::string_view::npos
        : encoded.find(':', first + 1U);
    if (first == std::string_view::npos ||
        second == std::string_view::npos ||
        encoded.find(':', second + 1U) != std::string_view::npos) {
        throw std::invalid_argument(
            "--peer must be DEVICE_ID:EPOCH:LOWERCASE_SPKI_SHA256");
    }
    anonsync::SyncReplicaTlsMembershipEntry entry;
    entry.actor.device_id = std::string(encoded.substr(0U, first));
    entry.actor.epoch = parse_uint64(
        encoded.substr(first + 1U, second - first - 1U), "peer epoch");
    entry.spki_sha256 = std::string(encoded.substr(second + 1U));
    if (!anonsync::sync_id_is_valid(entry.actor.device_id) ||
        entry.actor.epoch == 0U ||
        !anonsync::is_lowercase_sha256_hex(entry.spki_sha256)) {
        throw std::invalid_argument("--peer contains invalid actor or SPKI");
    }
    return entry;
}


struct BootstrapResourceInventory final {
    bool replica_database_present = false;
    bool payload_store_present = false;
    bool effect_database_present = false;
    bool membership_database_present = false;
    bool anchor_database_present = false;
    bool files_root_empty = true;

    [[nodiscard]] std::uint64_t missing_store_count(
        const anonsync::SyncReplicaDeploymentManifest& deployment) const
        noexcept {
        std::uint64_t missing = replica_database_present ? 0U : 1U;
        if (deployment.payload_root.has_value() && !payload_store_present) {
            ++missing;
        }
        if (deployment.effect_db.has_value() && !effect_database_present) {
            ++missing;
        }
        if (deployment.membership_db.has_value()) {
            if (!membership_database_present) ++missing;
            if (!anchor_database_present) ++missing;
        }
        return missing;
    }
};

struct BootstrapExistingSqliteAuthorities final {
    std::optional<ProductSqliteDatabaseAuthority> replica;
    std::optional<ProductSqliteDatabaseAuthority> effect;
    std::optional<ProductSqliteDatabaseAuthority> membership;
    std::optional<ProductSqliteDatabaseAuthority> anchor;
};

[[nodiscard]] bool database_main_is_present_for_resume_or_throw(
    const fs::path& database_path,
    const std::string& label) {
    if (path_is_absent_or_throw(database_path, label + " main database")) {
        for (const std::string_view suffix :
             {std::string_view("-journal"), std::string_view("-wal"),
              std::string_view("-shm")}) {
            const fs::path sidecar_path =
                append_ascii_path_suffix(database_path, suffix);
            if (!path_is_absent_or_throw(
                    sidecar_path,
                    label + " orphan SQLite sidecar " + std::string(suffix))) {
                throw std::runtime_error(
                    label + " orphan SQLite sidecar " + std::string(suffix) +
                    " must be absent when the main database is absent: " +
                    sidecar_path.generic_string());
            }
        }
        return false;
    }

    std::error_code error;
    const fs::file_status status = fs::symlink_status(database_path, error);
    if (error || fs::is_symlink(status) || !fs::is_regular_file(status)) {
        throw std::runtime_error(
            label + " main database must be a non-symlink regular file: " +
            database_path.generic_string());
    }
    return true;
}

void require_existing_deployment_directory_or_throw(
    const fs::path& directory,
    const std::string& label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(directory, error);
    if (error || fs::is_symlink(status) || !fs::is_directory(status)) {
        throw std::runtime_error(
            label + " must be an existing non-symlink directory: " +
            directory.generic_string());
    }
}

[[nodiscard]] BootstrapResourceInventory
inspect_bootstrap_resource_inventory_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    BootstrapResourceInventory inventory;
    inventory.replica_database_present =
        database_main_is_present_for_resume_or_throw(
            deployment.replica_db, label + " replica database");

    if (deployment.payload_root.has_value()) {
        require_existing_deployment_directory_or_throw(
            *deployment.payload_root, label + " payload root");
        inventory.payload_store_present = !directory_is_empty_or_throw(
            *deployment.payload_root, label + " payload root");
    }
    if (deployment.effect_db.has_value()) {
        require_existing_deployment_directory_or_throw(
            *deployment.files_root, label + " files root");
        inventory.effect_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.effect_db, label + " effect database");
        inventory.files_root_empty = directory_is_empty_or_throw(
            *deployment.files_root, label + " files root");
    }
    if (deployment.membership_db.has_value()) {
        inventory.membership_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.membership_db,
                label + " membership database");
        inventory.anchor_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.anchor_db,
                label + " membership anchor database");
    }
    return inventory;
}

[[nodiscard]] BootstrapExistingSqliteAuthorities
attest_existing_bootstrap_resource_identities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    DatabaseOpenDisposition disposition,
    const std::string& label) {
    BootstrapExistingSqliteAuthorities authorities;
    const auto open_bound = [&](
                                const fs::path& path,
                                anonsync::SyncReplicaSqliteDeploymentRole role,
                                const std::string& resource_label) {
        if (disposition == DatabaseOpenDisposition::ExistingOperational) {
            return open_bound_operational_database_or_throw(
                deployment, path, role, resource_label);
        }
        return open_bound_bootstrap_candidate_or_throw(
            deployment, path, role, resource_label);
    };

    // Identity is the first phase. Every existing SQLite main file must prove
    // the exact record-selected deployment, role, and pathname before any role
    // owner or WAL promotion is allowed to mutate another resource. Handles
    // remain retained so the role-state phase cannot accidentally reopen a
    // different pathname object after identity attestation.
    if (inventory.replica_database_present) {
        authorities.replica.emplace(open_bound(
            deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            label + " replica database"));
    }
    if (inventory.effect_database_present) {
        authorities.effect.emplace(open_bound(
            *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database"));
    }
    if (inventory.membership_database_present) {
        authorities.membership.emplace(open_bound(
            *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database"));
    }
    if (inventory.anchor_database_present) {
        authorities.anchor.emplace(open_bound(
            *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database"));
    }
    if (inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore payload_store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, label + " payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        (void)payload_store.snapshot_or_throw();
    }
    return authorities;
}

void promote_existing_bootstrap_sqlite_authorities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    BootstrapExistingSqliteAuthorities& authorities,
    const std::string& label) {
    const auto promote = [&](
                             std::optional<ProductSqliteDatabaseAuthority>& database,
                             const fs::path& path,
                             anonsync::SyncReplicaSqliteDeploymentRole role,
                             const std::string& resource_label) {
        if (!database.has_value()) return;
        promote_bound_bootstrap_candidate_to_operational_or_throw(
            *database,
            sqlite_deployment_binding_or_throw(
                deployment, path, role, resource_label),
            resource_label);
    };
    promote(
        authorities.replica, deployment.replica_db,
        anonsync::SyncReplicaSqliteDeploymentRole::Replica,
        label + " replica database");
    if (deployment.effect_db.has_value()) {
        promote(
            authorities.effect, *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database");
    }
    if (deployment.membership_db.has_value()) {
        promote(
            authorities.membership, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database");
    }
    if (deployment.anchor_db.has_value()) {
        promote(
            authorities.anchor, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database");
    }
}

[[nodiscard]] bool replica_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 1U &&
        snapshot.policy_generation == 1U &&
        snapshot.durable.last_local_counter == 0U &&
        snapshot.durable.local_operation_ids.empty() &&
        snapshot.durable.operations.empty() && snapshot.outbox.empty() &&
        snapshot.outbox_clock_state == anonsync::SyncReplicaOutboxClockState{};
}

[[nodiscard]] bool payload_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaFilePayloadStoreSnapshot& snapshot) {
    return snapshot.entry_count() == 0U && snapshot.indexed_bytes() == 0U &&
        snapshot.transient_entry_count() == 0U &&
        snapshot.transient_bytes() == 0U;
}

[[nodiscard]] bool effect_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 0U &&
        snapshot.retained_payload_bytes == 0U && snapshot.effects.empty() &&
        snapshot.actor_usage.empty() && snapshot.device_usage.empty();
}

[[nodiscard]] bool membership_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaTlsMembershipSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 0U &&
        snapshot.current_policy_epoch == 0U &&
        snapshot.current_entry_count == 0U && snapshot.history.empty() &&
        !snapshot.current_authority.has_value();
}

[[nodiscard]] bool membership_anchor_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaTlsMembershipAnchorSqliteSnapshot& snapshot,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    return snapshot.transition_sequence == 0U && snapshot.history.empty() &&
        snapshot.current_anchor ==
            anonsync::sync_replica_tls_membership_genesis_anchor_or_throw(
                deployment.folder_id, deployment.local_actor,
                label + " expected genesis");
}

struct BootstrapPresentResourceAttestation final {
    bool all_present_resources_are_genesis = true;
};

[[nodiscard]] BootstrapPresentResourceAttestation
attest_existing_bootstrap_role_state_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    BootstrapExistingSqliteAuthorities& authorities,
    bool populated_files_root_is_explicit_bootstrap_input,
    const std::string& label) {
    BootstrapPresentResourceAttestation result;

    if (inventory.replica_database_present) {
        if (!authorities.replica.has_value()) {
            throw std::logic_error(
                label + " retained replica authority is absent");
        }
        anonsync::SyncReplicaSqliteOwner owner(
            authorities.replica->db, deployment.folder_id,
            deployment.local_actor, {},
            label + " replica owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            replica_snapshot_is_bootstrap_genesis(owner.snapshot_or_throw());
    }

    if (inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, label + " payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            payload_snapshot_is_bootstrap_genesis(store.snapshot_or_throw());
    }

    if (inventory.effect_database_present) {
        if (!authorities.effect.has_value()) {
            throw std::logic_error(
                label + " retained effect authority is absent");
        }
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            authorities.effect->db, deployment.folder_id,
            *deployment.files_root,
            effect_owner_limits(deployment.max_payload_bytes),
            label + " effect owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            effect_snapshot_is_bootstrap_genesis(owner.snapshot_or_throw());
    }
    if (deployment.effect_db.has_value() && !inventory.files_root_empty &&
        !populated_files_root_is_explicit_bootstrap_input) {
        result.all_present_resources_are_genesis = false;
    }

    if (inventory.membership_database_present) {
        if (!authorities.membership.has_value()) {
            throw std::logic_error(
                label + " retained membership authority is absent");
        }
        anonsync::SyncReplicaTlsMembershipSqliteOwner owner(
            authorities.membership->db, deployment.folder_id,
            deployment.local_actor,
            label + " membership owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            membership_snapshot_is_bootstrap_genesis(
                owner.snapshot_or_throw());
    }

    if (inventory.anchor_database_present) {
        if (!authorities.anchor.has_value()) {
            throw std::logic_error(
                label + " retained membership-anchor authority is absent");
        }
        anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            authorities.anchor->db, deployment.folder_id,
            deployment.local_actor,
            label + " membership anchor owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            membership_anchor_snapshot_is_bootstrap_genesis(
                owner.snapshot_or_throw(), deployment,
                label + " membership anchor");
    }
    return result;
}

void create_missing_bootstrap_resources_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    const std::string& label) {
    const anonsync::SyncReplicaDeploymentIdentity deployment_identity =
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, label + " deployment identity");

    if (!inventory.replica_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            label + " replica database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor, {},
                    label + " replica owner");
                if (!replica_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created replica database is not at genesis");
                }
            });
    }

    if (deployment.payload_root.has_value() &&
        !inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore store(
            deployment_identity, *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        if (!payload_snapshot_is_bootstrap_genesis(store.snapshot_or_throw())) {
            throw std::logic_error(
                label + " newly created payload store is not at genesis");
        }
    }

    if (deployment.effect_db.has_value() &&
        !inventory.effect_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaFileEffectSqliteOwner owner(
                    database, deployment.folder_id, *deployment.files_root,
                    effect_owner_limits(deployment.max_payload_bytes),
                    label + " effect owner");
                if (!effect_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created effect database is not at genesis");
                }
            });
    }

    if (deployment.membership_db.has_value() &&
        !inventory.membership_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaTlsMembershipSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor,
                    anonsync::SyncReplicaTlsPolicySqliteBackendDisposition::
                        DetachedBootstrapImage,
                    label + " membership owner");
                if (!membership_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created membership database is not at genesis");
                }
            });
    }

    if (deployment.anchor_db.has_value() &&
        !inventory.anchor_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor,
                    anonsync::SyncReplicaTlsPolicySqliteBackendDisposition::
                        DetachedBootstrapImage,
                    label + " membership anchor owner");
                if (!membership_anchor_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw(), deployment,
                        label + " membership anchor")) {
                    throw std::logic_error(
                        label + " newly created membership anchor database "
                                "is not at genesis");
                }
            });
    }
}

void reconcile_complete_bootstrap_membership_pair_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (!deployment.membership_db.has_value()) return;
    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database");
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, deployment.folder_id, deployment.local_actor,
        label + " membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, deployment.folder_id, deployment.local_actor,
        label + " membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner, label + " anchored coordinator");
    (void)coordinator.reconcile_or_throw();
}

struct CompleteBootstrapStoreAuthorities final {
    BootstrapResourceInventory inventory;
    BootstrapExistingSqliteAuthorities sqlite;
};

[[nodiscard]] CompleteBootstrapStoreAuthorities
attest_complete_bootstrap_store_identities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(deployment, label);
    const std::uint64_t missing = inventory.missing_store_count(deployment);
    if (missing != 0U) {
        throw std::runtime_error(
            label + " selected store set remains incomplete after bootstrap: " +
            std::to_string(missing) + " store(s) missing");
    }
    BootstrapExistingSqliteAuthorities authorities =
        attest_existing_bootstrap_resource_identities_or_throw(
            deployment, inventory,
            DatabaseOpenDisposition::ExistingOperational,
            label + " identity attestation");
    return CompleteBootstrapStoreAuthorities{
        .inventory = inventory,
        .sqlite = std::move(authorities),
    };
}

void attest_complete_bootstrap_store_set_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    bool populated_files_root_is_explicit_bootstrap_input,
    const std::string& label) {
    CompleteBootstrapStoreAuthorities authorities =
        attest_complete_bootstrap_store_identities_or_throw(
            deployment, label);
    (void)attest_existing_bootstrap_role_state_or_throw(
        deployment, authorities.inventory, authorities.sqlite,
        populated_files_root_is_explicit_bootstrap_input,
        label + " role-state attestation");
    reconcile_complete_bootstrap_membership_pair_or_throw(
        deployment, label + " membership reconciliation");
}

void require_fresh_inventory_after_bootstrap_record_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    bool populated_files_root_is_explicit_bootstrap_input,
    const std::string& label) {
    if (inventory.replica_database_present || inventory.payload_store_present ||
        inventory.effect_database_present ||
        inventory.membership_database_present ||
        inventory.anchor_database_present ||
        (!inventory.files_root_empty &&
         !populated_files_root_is_explicit_bootstrap_input)) {
        throw std::runtime_error(
            label +
            " selected namespace changed after the durable bootstrap record "
            "was published; use init-resume to attest the exact recorded "
            "deployment instead of adopting observed resources");
    }
    if (inventory.missing_store_count(deployment) == 0U) {
        throw std::logic_error(
            label + " fresh inventory unexpectedly selects no creatable store");
    }
}

void attest_committed_manifest_matches_bootstrap_record_or_throw(
    const anonsync::SyncReplicaBootstrapRecord& record,
    const std::string& label) {
    const std::string exact =
        anonsync::read_sync_bounded_regular_file_no_symlink_or_throw(
            record.deployment.manifest_path,
            anonsync::kSyncReplicaDeploymentManifestMaxBytes,
            label + " exact final manifest");
    const anonsync::SyncReplicaDeploymentManifest committed =
        anonsync::decode_sync_replica_deployment_manifest_or_throw(
            exact, record.deployment.manifest_path,
            label + " final manifest bytes");
    if (exact != record.exact_manifest_bytes ||
        committed != record.deployment) {
        throw std::runtime_error(
            label +
            " final deployment manifest conflicts with the immutable "
            "bootstrap record");
    }
    const anonsync::SyncImmutableFileReconciliationOutcome durability =
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            record.deployment.manifest_path, byte_span(exact),
            label + " durability reconciliation");
    if (durability != anonsync::SyncImmutableFileReconciliationOutcome::
                          ExactAndDirectorySynced) {
        throw std::runtime_error(
            label + " final deployment manifest could not be reconciled as "
            "exact and directory-synced: " +
            anonsync::sync_immutable_file_reconciliation_outcome_name(
                durability));
    }
}

int command_init(const Options& options) {
    options.require_only({
        "manifest", "replica-db", "payload-root", "effect-db",
        "files-root", "membership-db", "anchor-db", "folder",
        "local-device", "local-epoch", "max-payload-bytes",
        "initial-files"});
    require_paired_options(options, "effect-db", "files-root");
    require_paired_options(options, "membership-db", "anchor-db");
    const bool adopt_existing_initial_files =
        adopt_existing_initial_files_from_options_or_throw(options);

    anonsync::SyncReplicaDeploymentManifest deployment;
    deployment.deployment_id =
        anonsync::generate_sync_replica_deployment_id_or_throw(
            "anonsync_replica init");
    deployment.manifest_path = require_database_path(
        options.one("manifest"), "--manifest");
    deployment.replica_db = require_database_path(
        options.one("replica-db"), "--replica-db");
    if (options.has("payload-root")) {
        deployment.payload_root = require_existing_directory(
            options.one("payload-root"), "--payload-root");
    }
    if (options.has("effect-db")) {
        deployment.effect_db = require_database_path(
            options.one("effect-db"), "--effect-db");
        deployment.files_root = require_existing_directory(
            options.one("files-root"), "--files-root");
    }
    if (options.has("membership-db")) {
        deployment.membership_db = require_database_path(
            options.one("membership-db"), "--membership-db");
        deployment.anchor_db = require_database_path(
            options.one("anchor-db"), "--anchor-db");
    }
    deployment.folder_id = options.one("folder");
    if (!anonsync::sync_id_is_valid(deployment.folder_id)) {
        throw std::invalid_argument(
            "--folder is not a lowercase portable sync ID");
    }
    deployment.local_actor = actor_from_options(
        options, "local-device", "local-epoch", "local");
    deployment.max_payload_bytes = max_payload_from_options(options);
    deployment.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            deployment, "anonsync_replica init deployment manifest");
    anonsync::validate_sync_replica_bootstrap_record_namespace_or_throw(
        deployment, "anonsync_replica init bootstrap record");

    // Fresh init has no implicit adoption semantics. Every durable authority
    // remains absent/empty. Only an explicit adopt-existing selection permits
    // pre-existing ordinary files in the selected folder root; the later
    // folder pass still observes and publishes each file through the normal
    // product path.
    require_path_absent_for_fresh_bootstrap_or_throw(
        deployment.manifest_path,
        "anonsync_replica init deployment manifest");
    const fs::path record_path =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            deployment.manifest_path,
            "anonsync_replica init bootstrap record");
    require_path_absent_for_fresh_bootstrap_or_throw(
        record_path, "anonsync_replica init bootstrap record");
    require_fresh_database_family_or_throw(
        deployment.replica_db,
        "anonsync_replica init replica database");
    if (deployment.effect_db.has_value()) {
        require_fresh_database_family_or_throw(
            *deployment.effect_db,
            "anonsync_replica init effect database");
    }
    if (deployment.membership_db.has_value()) {
        require_fresh_database_family_or_throw(
            *deployment.membership_db,
            "anonsync_replica init membership database");
        require_fresh_database_family_or_throw(
            *deployment.anchor_db,
            "anonsync_replica init membership anchor database");
    }
    if (deployment.payload_root.has_value()) {
        require_empty_directory_for_fresh_bootstrap_or_throw(
            *deployment.payload_root,
            "anonsync_replica init payload root");
    }
    if (deployment.files_root.has_value() &&
        !adopt_existing_initial_files) {
        require_empty_directory_for_fresh_bootstrap_or_throw(
            *deployment.files_root,
            "anonsync_replica init files root");
    }

    // Prepare the final create-new cutpoint before the first durable mutation.
    // The immutable record is then published first and carries the exact future
    // manifest bytes, making a later restart's authority explicit rather than
    // inferred from path presence or from partially materialized stores.
    const std::string exact_manifest =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            deployment, "anonsync_replica init deployment manifest");
    auto manifest_publication =
        anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
            deployment.manifest_path, exact_manifest,
            "anonsync_replica deployment manifest");
    const anonsync::SyncReplicaBootstrapRecord record =
        anonsync::create_sync_replica_bootstrap_record_or_throw(
            deployment, "anonsync_replica init bootstrap record");
    if (record.deployment != deployment ||
        record.exact_manifest_bytes != exact_manifest) {
        throw std::logic_error(
            "anonsync_replica init bootstrap record readback conflicts with "
            "the prepared deployment");
    }

    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(
            deployment, "anonsync_replica init post-record inventory");
    require_fresh_inventory_after_bootstrap_record_or_throw(
        deployment, inventory, adopt_existing_initial_files,
        "anonsync_replica init");
    create_missing_bootstrap_resources_or_throw(
        deployment, inventory, "anonsync_replica init store creation");
    attest_complete_bootstrap_store_set_or_throw(
        deployment, adopt_existing_initial_files,
        "anonsync_replica init complete-store attestation");
    anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
        record, "anonsync_replica init pre-commit record attestation");
    manifest_publication.publish_or_throw();
    std::cout << exact_manifest;
    return 0;
}

int command_init_resume(const Options& options) {
    options.require_only({"manifest", "initial-files"});
    const bool adopt_existing_initial_files =
        adopt_existing_initial_files_from_options_or_throw(options);
    const fs::path manifest_path = require_database_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaBootstrapRecord record =
        anonsync::read_sync_replica_bootstrap_record_or_throw(
            manifest_path, "anonsync_replica init-resume bootstrap record");
    const anonsync::SyncReplicaDeploymentManifest& deployment =
        record.deployment;

    if (!path_is_absent_or_throw(
            manifest_path,
            "anonsync_replica init-resume deployment manifest")) {
        // A committed deployment is not repaired by creating a missing
        // authority store, initializing role schema, or reconciling membership.
        // Idempotence requires exact final bytes plus a complete identity-bound
        // store set; ordinary operational commands own later role-state work.
        attest_committed_manifest_matches_bootstrap_record_or_throw(
            record, "anonsync_replica init-resume committed deployment");
        (void)attest_complete_bootstrap_store_identities_or_throw(
            deployment,
            "anonsync_replica init-resume committed store-set attestation");
        anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
            record,
            "anonsync_replica init-resume committed record attestation");
        std::cout << record.exact_manifest_bytes;
        return 0;
    }

    // Retain the exact final publication authority before any recovery-time
    // schema initialization or missing-store creation. The record bytes—not
    // observed resource names—select the deployment being resumed.
    auto manifest_publication =
        anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
            deployment.manifest_path, record.exact_manifest_bytes,
            "anonsync_replica init-resume deployment manifest");
    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(
            deployment, "anonsync_replica init-resume inventory");

    // Three phases are deliberate: every present resource first proves exact
    // record-selected identity without application-level writes. Rollback-mode
    // candidates are namespace-preflighted before SQLite reads; after the whole
    // set passes, sealed images may be durability-reconciled and promoted to
    // WAL. Role owners then inspect those same retained handles.
    BootstrapExistingSqliteAuthorities existing =
        attest_existing_bootstrap_resource_identities_or_throw(
            deployment, inventory,
            DatabaseOpenDisposition::ExistingBootstrapCandidate,
            "anonsync_replica init-resume identity phase");
    promote_existing_bootstrap_sqlite_authorities_or_throw(
        deployment, existing,
        "anonsync_replica init-resume WAL-promotion phase");
    const BootstrapPresentResourceAttestation present_state =
        attest_existing_bootstrap_role_state_or_throw(
            deployment, inventory, existing, adopt_existing_initial_files,
            "anonsync_replica init-resume role-state phase");
    const std::uint64_t missing = inventory.missing_store_count(deployment);
    if (missing != 0U &&
        !present_state.all_present_resources_are_genesis) {
        throw std::runtime_error(
            "anonsync_replica init-resume refuses to create " +
            std::to_string(missing) +
            " missing store(s) because at least one present resource or the "
            "files root has advanced beyond bootstrap genesis");
    }

    // Bootstrap-candidate handles deliberately retain EXCLUSIVE locking mode
    // across identity, promotion, and role-state proof. Release those exact
    // handles only after the recomposition decision is final, before opening a
    // second operational authority set for complete-store attestation.
    existing = BootstrapExistingSqliteAuthorities{};

    create_missing_bootstrap_resources_or_throw(
        deployment, inventory,
        "anonsync_replica init-resume missing-store creation");
    attest_complete_bootstrap_store_set_or_throw(
        deployment, adopt_existing_initial_files,
        "anonsync_replica init-resume complete-store attestation");
    anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
        record, "anonsync_replica init-resume pre-commit record attestation");
    manifest_publication.publish_or_throw();
    std::cout << record.exact_manifest_bytes;
    return 0;
}

int command_status(const Options& options) {
    options.require_only({"manifest"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "status");

    ProductSqliteDatabaseAuthority replica_database =
        open_bound_forensic_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica status replica database");
    const anonsync::SyncReplicaSqliteSnapshot replica =
        anonsync::inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
            replica_database.db, deployment.folder_id,
            deployment.local_actor,
            "anonsync_replica status replica inspection");
    const anonsync::SyncReplicaModel model =
        anonsync::SyncReplicaModel::restore_or_throw(
            replica.durable, replica.limits.model);
    const ProductStatusOutboxCounts outbox =
        summarize_outbox_at_high_water_or_throw(
            replica.outbox, replica.outbox_time_high_water_epoch);
    const std::vector<anonsync::SyncReplicaPathView> visible_paths =
        model.visible_paths();
    const std::vector<std::string> causal_heads =
        model.causal_head_operation_ids();
    const std::vector<std::string> missing_predecessors =
        model.missing_predecessor_operation_ids();

    bool payload_present = false;
    std::uint64_t payload_entries = 0U;
    std::uint64_t payload_indexed_bytes = 0U;
    std::uint64_t payload_transient_entries = 0U;
    std::uint64_t payload_transient_bytes = 0U;
    std::string payload_snapshot_digest;
    if (deployment.payload_root.has_value()) {
        anonsync::SyncReplicaFilePayloadStore payload_store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, "anonsync_replica status payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
            payload_store_limits(deployment.max_payload_bytes),
            "anonsync_replica status payload store");
        const anonsync::SyncReplicaFilePayloadStoreSnapshot payload =
            payload_store.snapshot_or_throw();
        payload_present = true;
        payload_entries = payload.entry_count();
        payload_indexed_bytes = payload.indexed_bytes();
        payload_transient_entries = payload.transient_entry_count();
        payload_transient_bytes = payload.transient_bytes();
        payload_snapshot_digest = payload.snapshot_digest();
    }

    bool effect_present = false;
    std::uint64_t effect_state_generation = 0U;
    std::uint64_t effect_total = 0U;
    std::uint64_t effect_staged = 0U;
    std::uint64_t effect_published = 0U;
    std::uint64_t effect_retained_payload_bytes = 0U;
    std::string effect_cutpoint_digest;
    if (deployment.effect_db.has_value()) {
        ProductSqliteDatabaseAuthority effect_database =
            open_bound_forensic_database_or_throw(
                deployment, *deployment.effect_db,
                anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
                "anonsync_replica status effect database");
        const anonsync::SyncReplicaFileEffectSqliteSnapshot effect =
            anonsync::
                inspect_sync_replica_file_effect_sqlite_snapshot_read_only_or_throw(
                    effect_database.db, deployment.folder_id,
                    *deployment.files_root,
                    "anonsync_replica status effect inspection");
        const ProductStatusEffectCounts effect_counts =
            summarize_effects(effect.effects);
        effect_present = true;
        effect_state_generation = effect.state_generation;
        effect_total = static_cast<std::uint64_t>(effect.effects.size());
        effect_staged = effect_counts.staged;
        effect_published = effect_counts.published;
        effect_retained_payload_bytes = effect.retained_payload_bytes;
        effect_cutpoint_digest = effect.cutpoint_digest;
    }

    bool membership_present = false;
    std::uint64_t membership_state_generation = 0U;
    std::uint64_t membership_policy_epoch = 0U;
    std::uint64_t membership_entry_count = 0U;
    std::string membership_chain_digest;
    std::uint64_t membership_anchor_generation = 0U;
    std::uint64_t membership_anchor_transition_sequence = 0U;
    bool membership_anchor_matches_current = false;
    if (deployment.membership_db.has_value()) {
        ProductSqliteDatabaseAuthority membership_database =
            open_bound_forensic_database_or_throw(
                deployment, *deployment.membership_db,
                anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
                "anonsync_replica status membership database");
        ProductSqliteDatabaseAuthority anchor_database =
            open_bound_forensic_database_or_throw(
                deployment, *deployment.anchor_db,
                anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
                "anonsync_replica status membership anchor database");
        const auto anchor = anonsync::
            inspect_sync_replica_tls_membership_anchor_sqlite_snapshot_read_only_or_throw(
                anchor_database.db, deployment.folder_id,
                deployment.local_actor,
                "anonsync_replica status membership anchor inspection");
        const auto membership = anonsync::
            inspect_sync_replica_tls_membership_sqlite_snapshot_read_only_or_throw(
                membership_database.db, deployment.folder_id,
                deployment.local_actor, anchor.current_anchor,
                "anonsync_replica status membership inspection");
        membership_present = true;
        membership_state_generation = membership.state_generation;
        membership_policy_epoch = membership.current_policy_epoch;
        membership_entry_count = membership.current_entry_count;
        membership_chain_digest = membership.current_chain_digest;
        membership_anchor_generation = anchor.current_anchor.state_generation;
        membership_anchor_transition_sequence = anchor.transition_sequence;
        membership_anchor_matches_current =
            anchor.current_anchor == membership.anchor();
    }

    std::cout << "{\"command\":\"status\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"replica_state_generation\":" << replica.state_generation
        << ",\"replica_policy_generation\":" << replica.policy_generation
        << ",\"replica_evidence_operations\":" << model.evidence_count()
        << ",\"replica_active_operations\":" << model.operation_count()
        << ",\"replica_pending_operations\":" << model.pending_operation_count()
        << ",\"replica_quarantined_operations\":" << model.quarantined_operation_count()
        << ",\"replica_visible_paths\":" << visible_paths.size()
        << ",\"replica_causal_heads\":" << causal_heads.size()
        << ",\"replica_missing_predecessors\":" << missing_predecessors.size()
        << ",\"replica_local_counter\":" << model.last_local_counter()
        << ",\"replica_local_actor_compromised\":"
        << json_bool(model.local_actor_compromised())
        << ",\"replica_retained_canonical_bytes\":"
        << model.retained_canonical_bytes()
        << ",\"replica_outbox_intents\":" << outbox.intents
        << ",\"replica_outbox_unclaimed\":" << outbox.unclaimed
        << ",\"replica_outbox_claimable_at_high_water\":"
        << outbox.claimable_at_high_water
        << ",\"replica_outbox_claimed_live_at_high_water\":"
        << outbox.claimed_live_at_high_water
        << ",\"replica_outbox_expired_at_high_water\":"
        << outbox.expired_at_high_water
        << ",\"replica_outbox_retry_waiting_at_high_water\":"
        << outbox.retry_waiting_at_high_water
        << ",\"replica_outbox_dispatch_attempts\":"
        << outbox.dispatch_attempts
        << ",\"replica_outbox_time_high_water_epoch\":"
        << replica.outbox_time_high_water_epoch
        << ",\"replica_outbox_clock_health\":"
        << json_quote(outbox_clock_health_name(
               replica.outbox_clock_state.health))
        << ",\"replica_outbox_clock_anomaly\":"
        << json_quote(anonsync::sync_replica_outbox_clock_anomaly_name(
               replica.outbox_clock_state.anomaly))
        << ",\"replica_outbox_clock_observation_generation\":"
        << replica.outbox_clock_state.observation_generation
        << ",\"replica_outbox_clock_recovery_generation\":"
        << replica.outbox_clock_state.recovery_generation
        << ",\"replica_operation_set_digest\":"
        << json_quote(replica.operation_set_digest)
        << ",\"replica_evidence_set_digest\":"
        << json_quote(replica.evidence_set_digest)
        << ",\"replica_visible_state_digest\":"
        << json_quote(replica.visible_state_digest)
        << ",\"replica_cutpoint_digest\":"
        << json_quote(replica.cutpoint_digest)
        << ",\"payload_status_present\":" << json_bool(payload_present)
        << ",\"payload_entries\":" << payload_entries
        << ",\"payload_indexed_bytes\":" << payload_indexed_bytes
        << ",\"payload_transient_entries\":" << payload_transient_entries
        << ",\"payload_transient_bytes\":" << payload_transient_bytes
        << ",\"payload_snapshot_digest\":"
        << json_quote(payload_snapshot_digest)
        << ",\"effect_status_present\":" << json_bool(effect_present)
        << ",\"effect_state_generation\":" << effect_state_generation
        << ",\"effect_total\":" << effect_total
        << ",\"effect_staged\":" << effect_staged
        << ",\"effect_published\":" << effect_published
        << ",\"effect_retained_payload_bytes\":"
        << effect_retained_payload_bytes
        << ",\"effect_cutpoint_digest\":"
        << json_quote(effect_cutpoint_digest)
        << ",\"membership_status_present\":"
        << json_bool(membership_present)
        << ",\"membership_state_generation\":"
        << membership_state_generation
        << ",\"membership_policy_epoch\":" << membership_policy_epoch
        << ",\"membership_entry_count\":" << membership_entry_count
        << ",\"membership_chain_digest\":"
        << json_quote(membership_chain_digest)
        << ",\"membership_anchor_generation\":"
        << membership_anchor_generation
        << ",\"membership_anchor_transition_sequence\":"
        << membership_anchor_transition_sequence
        << ",\"membership_anchor_matches_current\":"
        << json_bool(membership_anchor_matches_current)
        << "}\n";
    return 0;
}

int command_clock_observe(const Options& options) {
    options.require_only({
        "manifest", "operator-clock-authority-id",
        "operator-clock-uncertainty-ns"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "clock-observe");
    const bool operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica clock observation database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica clock observation owner", std::move(clock_source));
    const anonsync::SyncReplicaOutboxClockObservationResult observed =
        owner.observe_outbox_clock_or_throw();

    std::cout << "{\"command\":\"clock-observe\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(operator_trusted_clock))
        << ",\"outcome\":"
        << json_quote(outbox_clock_observation_outcome_name(observed.outcome))
        << ",\"changed\":" << json_bool(observed.changed);
    append_outbox_clock_state_json_fields(std::cout, observed.state);
    std::cout << "}\n";
    return 0;
}

int command_clock_recover(const Options& options) {
    options.require_only({
        "manifest", "expected-observation-generation",
        "operator-clock-authority-id", "operator-clock-uncertainty-ns"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "clock-recover");
    const std::uint64_t expected_generation = parse_uint64(
        options.one("expected-observation-generation"),
        "--expected-observation-generation");
    if (expected_generation == 0U) {
        throw std::invalid_argument(
            "--expected-observation-generation must be nonzero");
    }
    const bool operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica clock recovery database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica clock recovery owner", std::move(clock_source));
    const anonsync::SyncReplicaOutboxClockState recovered =
        owner.recover_outbox_clock_or_throw(expected_generation);

    std::cout << "{\"command\":\"clock-recover\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(operator_trusted_clock))
        << ",\"expected_observation_generation\":"
        << expected_generation;
    append_outbox_clock_state_json_fields(std::cout, recovered);
    std::cout << "}\n";
    return 0;
}

int command_enqueue_file(const Options& options) {
    options.require_only({
        "manifest", "destination-device", "canonical-path", "source-file"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "enqueue-file");
    const fs::path& payload_root =
        require_payload_root(deployment, "enqueue-file");
    const fs::path source_file = require_existing_regular_file(
        options.one("source-file"), "--source-file");
    const auto& destination_values = options.all("destination-device");
    if (destination_values.empty()) {
        throw std::invalid_argument(
            "at least one --destination-device is required");
    }
    std::vector<std::string> destinations = destination_values;
    for (const std::string& destination : destinations) {
        if (!anonsync::sync_id_is_valid(destination)) {
            throw std::invalid_argument(
                "--destination-device contains an invalid sync ID");
        }
    }

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica replica database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica SQLite owner");

    const std::string canonical_path = options.one("canonical-path");
    const anonsync::SyncReplicaSqliteSnapshot observed_snapshot =
        owner.snapshot_or_throw();
    const anonsync::SyncReplicaModel observed_model =
        anonsync::SyncReplicaModel::restore_or_throw(
            observed_snapshot.durable, observed_snapshot.limits.model);
    const auto observed_path = observed_model.visible_path(canonical_path);
    const std::vector<std::string> observed_visible_operation_ids =
        observed_path.has_value()
            ? observed_path->visible_operation_ids
            : std::vector<std::string>{};

    // Prove the exact replica identity before spending payload-directory
    // mutation authority. A mistyped or wrong-role database must not leave an
    // unreferenced content object in an otherwise valid payload store. Capture
    // the exact path heads before reading the caller's bytes as well: a remote
    // admission or competing local publication during payload preparation must
    // make the final transaction reject rather than laundering stale bytes into
    // a causal successor.
    std::string payload =
        anonsync::read_sync_bounded_regular_file_no_symlink_or_throw(
            source_file, deployment.max_payload_bytes,
            "anonsync_replica source payload");
    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, "anonsync_replica enqueue payload identity"),
        payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_store_limits(deployment.max_payload_bytes),
        "anonsync_replica payload store");
    const auto put = payload_store.put_payload_or_throw(std::move(payload));

    const anonsync::SyncReplicaOperation operation =
        owner.create_local_file_from_observed_heads_or_throw(
            canonical_path, observed_visible_operation_ids, put.size_bytes,
            put.content_sha256, destinations);

    std::cout
        << "{\"command\":\"enqueue-file\",\"operation_id\":"
        << json_quote(operation.operation_id)
        << ",\"folder_id\":" << json_quote(operation.folder_id)
        << ",\"canonical_path\":" << json_quote(operation.canonical_path)
        << ",\"content_sha256\":" << json_quote(operation.content_sha256)
        << ",\"size_bytes\":" << operation.size_bytes
        << ",\"destinations\":" << destinations.size();
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"payload_store_disposition\":"
        << json_quote(payload_put_name(put.disposition)) << "}\n";
    return 0;
}

int command_membership_publish(const Options& options) {
    options.require_only({"manifest", "policy-epoch", "peer"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(
            options, "membership-publish");
    require_membership_store(deployment, "membership-publish");
    const std::uint64_t policy_epoch = parse_uint64(
        options.one("policy-epoch"), "--policy-epoch");
    if (policy_epoch == 0U) {
        throw std::invalid_argument("--policy-epoch must be nonzero");
    }
    std::vector<anonsync::SyncReplicaTlsMembershipEntry> entries;
    entries.reserve(options.all("peer").size());
    for (const std::string& peer : options.all("peer")) {
        entries.push_back(parse_peer_entry(peer));
    }

    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            "anonsync_replica membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            "anonsync_replica membership anchor database");
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner,
        "anonsync_replica anchored membership coordinator");
    // Explicit init leaves a durable generation-zero membership/anchor pair
    // without published peer authority. Reconciliation exposes that exact
    // chain cutpoint without manufacturing authorization, so this operational
    // command supports both the first and subsequent CAS publications.
    const auto reconciled = coordinator.reconcile_or_throw();
    const auto published = coordinator.publish_or_throw(
        reconciled.target, policy_epoch, std::move(entries));

    std::cout
        << "{\"command\":\"membership-publish\",\"state_generation\":"
        << published.state_generation()
        << ",\"policy_epoch\":" << published.snapshot().policy_epoch()
        << ",\"entry_count\":" << published.snapshot().entry_count()
        << ",\"snapshot_digest\":"
        << json_quote(published.snapshot().snapshot_digest())
        << ",\"chain_digest\":" << json_quote(published.chain_digest())
        << ",\"durable_anchor_generation\":"
        << published.durable_anchor().state_generation
        << ",\"durable_anchor_chain_digest\":"
        << json_quote(published.durable_anchor().chain_digest);
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout << "}\n";
    return 0;
}

struct SendSessionsExecution final {
    anonsync::SyncReplicaDeploymentManifest deployment;
    anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::SyncReplicaStreamRouteKind::DirectTcp;
    bool operator_trusted_clock = false;
    std::uint64_t maximum_sessions = 0U;
    std::optional<std::uint64_t> maximum_runtime_seconds;
    std::uint64_t session_timeout_seconds = 0U;
    std::uint64_t claim_lease_seconds = 0U;
    std::uint64_t minimum_claim_lease_seconds = 0U;
    std::uint64_t receipts_applied = 0U;
    std::uint64_t deliveries_settled = 0U;
    std::uint64_t deliveries_deferred = 0U;
    anonsync::SyncReplicaSendSupervisorStopReason stop_reason =
        anonsync::SyncReplicaSendSupervisorStopReason::MaximumSessionsReached;
    std::vector<anonsync::SyncReplicaFileTlsClientResult> sessions;
};

[[nodiscard]] SendSessionsExecution execute_send_sessions_or_throw(
    const Options& options,
    std::string_view command_name,
    std::uint64_t maximum_sessions,
    std::optional<std::uint64_t> maximum_runtime_seconds) {
    if (maximum_sessions == 0U ||
        maximum_sessions > kMaximumBatchSessions) {
        throw std::logic_error("invalid internal send-session bound");
    }

    anonsync::SyncReplicaStreamRoute stream_route =
        stream_route_from_options_or_throw(options);
    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(stream_route);
    const std::uint64_t timeout_seconds =
        sender_timeout_from_options(options, route_kind);
    if (route_kind == anonsync::SyncReplicaStreamRouteKind::I2pSam &&
        maximum_runtime_seconds.has_value() &&
        *maximum_runtime_seconds < timeout_seconds) {
        throw std::invalid_argument(
            "--max-runtime-seconds must be at least --timeout-seconds for "
            "--transport i2p");
    }
    const anonsync::SyncReplicaSqliteOwnerLimits sender_owner_limits{};
    const anonsync::SyncReplicaOutboxClockPolicy sender_clock_policy{
        sender_owner_limits.max_outbox_clock_uncertainty_ns,
        sender_owner_limits.max_outbox_clock_forward_step_seconds,
        sender_owner_limits.max_outbox_clock_realtime_lag_seconds,
    };
    const std::uint64_t minimum_lease_seconds = anonsync::
        minimum_sync_replica_session_claim_lease_seconds_or_throw(
            timeout_seconds, sender_clock_policy,
            "anonsync_replica sender claim lease");
    const std::uint64_t lease_seconds = option_uint64_or(
        options, "lease-seconds", minimum_lease_seconds);
    anonsync::validate_sync_replica_session_claim_lease_seconds_or_throw(
        lease_seconds, timeout_seconds, sender_clock_policy,
        "--lease-seconds");
    anonsync::SyncReplicaSessionSupervisor supervisor(
        {maximum_sessions, timeout_seconds, maximum_runtime_seconds},
        std::chrono::steady_clock::now(),
        "anonsync_replica " + std::string(command_name) + " supervisor");

    SendSessionsExecution execution;
    execution.route_kind = route_kind;
    execution.maximum_sessions = maximum_sessions;
    execution.maximum_runtime_seconds = maximum_runtime_seconds;
    execution.session_timeout_seconds = timeout_seconds;
    execution.claim_lease_seconds = lease_seconds;
    execution.minimum_claim_lease_seconds = minimum_lease_seconds;
    execution.sessions.reserve(static_cast<std::size_t>(maximum_sessions));
    execution.deployment =
        load_operational_deployment_manifest_or_throw(options, command_name);
    const fs::path& payload_root =
        require_payload_root(execution.deployment, command_name);
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");
    const anonsync::SyncReplicaTlsPeerPolicy expected_peer =
        expected_peer_from_options_or_throw(options);
    const std::string worker =
        options.one_or("worker", "anonsync-replica-worker");
    execution.operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            execution.deployment, execution.deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica sender database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, execution.deployment.folder_id,
        execution.deployment.local_actor, sender_owner_limits,
        "anonsync_replica sender owner", std::move(clock_source));
    anonsync::SyncReplicaFileDeliveryService service(
        owner, nullptr,
        file_service_limits(execution.deployment.max_payload_bytes),
        "anonsync_replica sender service");
    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            execution.deployment,
            "anonsync_replica sender payload identity"),
        payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_store_limits(execution.deployment.max_payload_bytes),
        "anonsync_replica sender payload store");
    // One immutable payload snapshot is the exact availability cutpoint for
    // the command. Durable outbox state may advance between sessions, but
    // payloads published after this command begins cannot silently enter it.
    auto payload_snapshot = payload_store.snapshot_or_throw();
    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, false,
        "anonsync_replica client TLS context");
    anonsync::SyncReplicaStreamConnector connector(
        std::move(stream_route),
        "anonsync_replica " + std::string(command_name) +
            " outbound route");

    for (;;) {
        // I2P tunnel construction and STREAM CONNECT may each consume roughly
        // a minute. Do not start a later command-bounded attempt when the outer
        // cutpoint cannot grant the route its complete configured first-stage
        // horizon. This avoids creating and immediately abandoning SAM work.
        if (route_kind == anonsync::SyncReplicaStreamRouteKind::I2pSam &&
            supervisor.command_deadline().has_value()) {
            const auto latest_safe_start =
                *supervisor.command_deadline() -
                std::chrono::seconds(timeout_seconds);
            if (std::chrono::steady_clock::now() >= latest_safe_start) {
                execution.stop_reason = anonsync::
                    SyncReplicaSendSupervisorStopReason::CommandDeadlineReached;
                break;
            }
        }
        const anonsync::SyncReplicaSessionAuthorization authorization =
            supervisor.authorize_next_or_throw();
        if (authorization.disposition == anonsync::
                SyncReplicaSessionAuthorizationDisposition::
                    MaximumSessionsReached) {
            execution.stop_reason = anonsync::
                SyncReplicaSendSupervisorStopReason::MaximumSessionsReached;
            break;
        }
        if (authorization.disposition == anonsync::
                SyncReplicaSessionAuthorizationDisposition::
                    CommandDeadlineReached) {
            execution.stop_reason = anonsync::
                SyncReplicaSendSupervisorStopReason::CommandDeadlineReached;
            break;
        }
        if (!authorization.plan.has_value()) {
            throw std::logic_error(
                "authorized send session omitted its deadline plan");
        }
        const anonsync::SyncReplicaSessionDeadlinePlan& plan =
            *authorization.plan;
        auto result =
            anonsync::send_one_sync_replica_file_delivery_tls_session_or_throw(
                service, payload_snapshot,
                anonsync::
                    retain_sync_replica_file_tls_client_context_or_throw(
                        context.get(),
                        "anonsync_replica retained client context"),
                connector, expected_peer, worker, lease_seconds,
                plan.client_deadlines(),
                "anonsync_replica " + std::string(command_name) +
                    " session " + std::to_string(plan.session_index));

        const bool receipt_applied = result.disposition ==
            anonsync::SyncReplicaFileTlsClientDisposition::ReceiptApplied;
        const bool settled =
            anonsync::sync_replica_send_session_effect_is_settled(result);
        const bool deferred =
            anonsync::sync_replica_send_session_receiver_deferred(result);
        std::optional<anonsync::SyncReplicaSendSupervisorStopReason> stop =
            anonsync::sync_replica_send_supervisor_stop_after(result);
        if (stop == anonsync::SyncReplicaSendSupervisorStopReason::SessionFailed &&
            anonsync::
                sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
                    result) &&
            plan.command_limits(anonsync::SyncReplicaSessionStage::Third) &&
            supervisor.command_deadline_reached_at(
                std::chrono::steady_clock::now())) {
            stop = anonsync::
                SyncReplicaSendSupervisorStopReason::CommandDeadlineReached;
        }
        execution.sessions.push_back(std::move(result));

        if (receipt_applied) ++execution.receipts_applied;
        if (settled) ++execution.deliveries_settled;
        if (deferred) ++execution.deliveries_deferred;
        if (!stop.has_value()) continue;

        // An authenticated receiver deferral has already released the exact
        // claim onto the owned retry clock. Stopping is bounded progress; the
        // command does not sleep, immediately retry, or move into causally later
        // work under pressure. Every other terminal decision is likewise typed
        // outside the CLI presentation layer.
        execution.stop_reason = *stop;
        break;
    }
    return execution;
}

int command_send_one(const Options& options) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "address", "port", "certificate", "private-key", "ca-file",
        "worker", "lease-seconds", "timeout-seconds",
        "operator-clock-authority-id", "operator-clock-uncertainty-ns",
        "transport", "tor-socks-address", "tor-socks-port",
        "onion-address", "onion-port", "tor-isolation-token",
        "i2p-sam-address", "i2p-sam-port", "i2p-destination",
        "i2p-session-id", "i2p-private-destination-file",
        "i2p-inbound-quantity", "i2p-outbound-quantity"});
    const SendSessionsExecution execution = execute_send_sessions_or_throw(
        options, "send-one", 1U, std::nullopt);
    const auto& result = execution.sessions.front();

    std::cout << "{\"command\":\"send-one\"";
    append_deployment_authority_json_fields(std::cout, execution.deployment);
    std::cout << ",\"transport\":"
              << json_quote(anonsync::sync_replica_stream_route_kind_name(
                     execution.route_kind))
              << ",\"clock_profile\":"
              << json_quote(clock_profile_name(
                     execution.operator_trusted_clock))
              << ",\"session_timeout_seconds\":"
              << execution.session_timeout_seconds
              << ",\"claim_lease_seconds\":"
              << execution.claim_lease_seconds
              << ",\"minimum_claim_lease_seconds\":"
              << execution.minimum_claim_lease_seconds
              << ",\"stop_reason\":"
              << json_quote(anonsync::
                     sync_replica_send_supervisor_stop_reason_name(
                         execution.stop_reason));
    append_client_session_json_fields(std::cout, result, false);
    std::cout << "}\n";

    return anonsync::sync_replica_send_supervisor_stop_is_success(
               execution.stop_reason)
        ? 0
        : 2;
}

int command_send_batch(const Options& options) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "address", "port", "certificate", "private-key", "ca-file",
        "worker", "lease-seconds", "timeout-seconds", "max-sessions",
        "max-runtime-seconds", "operator-clock-authority-id",
        "operator-clock-uncertainty-ns", "transport",
        "tor-socks-address", "tor-socks-port", "onion-address",
        "onion-port", "tor-isolation-token", "i2p-sam-address",
        "i2p-sam-port", "i2p-destination", "i2p-session-id",
        "i2p-private-destination-file", "i2p-inbound-quantity",
        "i2p-outbound-quantity"});
    const std::uint64_t maximum_sessions = max_sessions_from_options(options);
    const std::uint64_t maximum_runtime_seconds =
        max_runtime_from_options(options);
    const SendSessionsExecution execution = execute_send_sessions_or_throw(
        options, "send-batch", maximum_sessions, maximum_runtime_seconds);

    std::cout << "{\"command\":\"send-batch\"";
    append_deployment_authority_json_fields(std::cout, execution.deployment);
    std::cout
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(
               execution.route_kind))
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(execution.operator_trusted_clock))
        << ",\"max_sessions\":" << execution.maximum_sessions
        << ",\"max_runtime_seconds\":"
        << *execution.maximum_runtime_seconds
        << ",\"session_timeout_seconds\":"
        << execution.session_timeout_seconds
        << ",\"claim_lease_seconds\":"
        << execution.claim_lease_seconds
        << ",\"minimum_claim_lease_seconds\":"
        << execution.minimum_claim_lease_seconds
        << ",\"sessions_attempted\":" << execution.sessions.size()
        << ",\"receipts_applied\":" << execution.receipts_applied
        << ",\"deliveries_settled\":" << execution.deliveries_settled
        << ",\"deliveries_deferred\":" << execution.deliveries_deferred
        << ",\"stop_reason\":"
        << json_quote(anonsync::
               sync_replica_send_supervisor_stop_reason_name(
                   execution.stop_reason))
        << ",\"sessions\":[";
    for (std::size_t index = 0U; index < execution.sessions.size(); ++index) {
        if (index != 0U) std::cout << ',';
        std::cout << "{\"session_index\":" << index + 1U;
        append_client_session_json_fields(std::cout, execution.sessions[index]);
        std::cout << '}';
    }
    std::cout << "]}\n";

    return anonsync::sync_replica_send_supervisor_stop_is_success(
               execution.stop_reason)
        ? 0
        : 2;
}

[[nodiscard]] bool reconciliation_pull_is_bounded_success(
    const anonsync::SyncReplicaReconciliationTlsClientResult& result) noexcept {
    if (result.disposition != anonsync::
            SyncReplicaReconciliationTlsClientDisposition::PullCompleted ||
        !result.pull.has_value()) {
        return false;
    }
    switch (result.pull->disposition) {
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::Complete:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            RoundTripLimitReached:
            return true;
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            SourceChangedLimitReached:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            SourcePayloadUnavailable:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            SourcePayloadPreparing:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            ReceiverCapacityBlocked:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            RequestDeadlineExpired:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::
            ResponseDeadlineExpired:
        case anonsync::SyncReplicaReconciliationTlsPullDisposition::PeerClosed:
            return false;
    }
    return false;
}

int command_reconcile_pull(const Options& options) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "certificate", "private-key", "ca-file", "timeout-seconds",
        "max-round-trips", "max-source-resets", "after-operation-id",
        "source-evidence-set-digest", "payload-operation-id",
        "payload-content-sha256", "payload-total-size",
        "payload-next-offset", "transport", "address", "port",
        "onion-address", "onion-port", "tor-socks-address",
        "tor-socks-port", "tor-isolation-token", "i2p-sam-address",
        "i2p-sam-port", "i2p-destination", "i2p-session-id",
        "i2p-private-destination-file", "i2p-inbound-quantity",
        "i2p-outbound-quantity"});
    require_all_or_none_options(
        options,
        {"payload-operation-id", "payload-content-sha256",
         "payload-total-size", "payload-next-offset"});

    const bool has_page_cursor = options.has("after-operation-id");
    const bool has_source_digest =
        options.has("source-evidence-set-digest");
    const bool has_payload_continuation =
        options.has("payload-operation-id");
    if (has_page_cursor && !has_source_digest) {
        throw std::invalid_argument(
            "--after-operation-id requires --source-evidence-set-digest");
    }
    if (has_payload_continuation && !has_source_digest) {
        throw std::invalid_argument(
            "payload continuation requires --source-evidence-set-digest");
    }
    if (has_source_digest && !has_page_cursor &&
        !has_payload_continuation) {
        throw std::invalid_argument(
            "--source-evidence-set-digest requires a page cursor or payload "
            "continuation");
    }

    anonsync::SyncReplicaStreamRoute stream_route =
        stream_route_from_options_or_throw(options);
    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(stream_route);
    const std::uint64_t timeout_seconds =
        sender_timeout_from_options(options, route_kind);
    const std::uint64_t max_round_trips =
        reconciliation_max_round_trips_from_options(options);
    const std::uint64_t max_source_resets =
        reconciliation_max_source_resets_from_options(options);

    std::optional<std::string> after_operation_id;
    std::optional<std::string> source_evidence_set_digest;
    std::optional<anonsync::SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;
    if (has_page_cursor) {
        after_operation_id = options.one("after-operation-id");
        if (!anonsync::is_lowercase_sha256_hex(*after_operation_id)) {
            throw std::invalid_argument(
                "--after-operation-id must be lowercase SHA-256");
        }
    }
    if (has_source_digest) {
        source_evidence_set_digest =
            options.one("source-evidence-set-digest");
        if (!anonsync::is_lowercase_sha256_hex(
                *source_evidence_set_digest)) {
            throw std::invalid_argument(
                "--source-evidence-set-digest must be lowercase SHA-256");
        }
    }
    if (has_payload_continuation) {
        anonsync::SyncReplicaReconciliationPayloadContinuation continuation;
        continuation.operation_id = options.one("payload-operation-id");
        continuation.content_sha256 =
            options.one("payload-content-sha256");
        continuation.total_size_bytes = parse_uint64(
            options.one("payload-total-size"), "--payload-total-size");
        continuation.next_offset_bytes = parse_uint64(
            options.one("payload-next-offset"), "--payload-next-offset");
        if (!anonsync::is_lowercase_sha256_hex(continuation.operation_id)) {
            throw std::invalid_argument(
                "--payload-operation-id must be lowercase SHA-256");
        }
        if (!anonsync::is_lowercase_sha256_hex(
                continuation.content_sha256)) {
            throw std::invalid_argument(
                "--payload-content-sha256 must be lowercase SHA-256");
        }
        if (continuation.total_size_bytes == 0U) {
            throw std::invalid_argument(
                "--payload-total-size must be greater than zero");
        }
        if (continuation.next_offset_bytes == 0U ||
            continuation.next_offset_bytes >
                continuation.total_size_bytes) {
            throw std::invalid_argument(
                "--payload-next-offset must be in [1, payload-total-size]");
        }
        payload_continuation = std::move(continuation);
    }

    anonsync::SyncReplicaSessionSupervisor supervisor(
        {1U, timeout_seconds, std::nullopt},
        std::chrono::steady_clock::now(),
        "anonsync_replica reconcile-pull supervisor");
    const anonsync::SyncReplicaSessionAuthorization authorization =
        supervisor.authorize_next_or_throw();
    if (authorization.disposition != anonsync::
            SyncReplicaSessionAuthorizationDisposition::Authorized ||
        !authorization.plan.has_value()) {
        throw std::logic_error(
            "reconcile-pull did not receive its one-session deadline plan");
    }
    const anonsync::SyncReplicaFileTlsClientDeadlines staged_deadlines =
        authorization.plan->client_deadlines();
    const anonsync::SyncReplicaReconciliationTlsClientDeadlines deadlines{
        staged_deadlines.connect,
        staged_deadlines.handshake,
        staged_deadlines.receipt,
        staged_deadlines.shutdown,
    };

    anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(
            options, "reconcile-pull");
    if (payload_continuation.has_value() &&
        payload_continuation->total_size_bytes >
            deployment.max_payload_bytes) {
        throw std::invalid_argument(
            "--payload-total-size exceeds the deployment payload ceiling");
    }
    const fs::path& payload_root =
        require_payload_root(deployment, "reconcile-pull");
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");
    const anonsync::SyncReplicaTlsPeerPolicy expected_peer =
        expected_peer_from_options_or_throw(options);

#ifndef __linux__
    (void)deployment;
    (void)payload_root;
    (void)certificate;
    (void)private_key;
    (void)ca_file;
    (void)expected_peer;
    (void)deadlines;
    (void)after_operation_id;
    (void)source_evidence_set_digest;
    (void)payload_continuation;
    throw std::runtime_error("reconcile-pull requires Linux");
#else
    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica reconciliation receiver database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica reconciliation receiver owner");
    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment,
            "anonsync_replica reconciliation receiver payload identity"),
        payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_store_limits(deployment.max_payload_bytes),
        "anonsync_replica reconciliation receiver payload store");
    anonsync::SyncReplicaReconciliationService service(
        owner, payload_store,
        reconciliation_protocol_limits(deployment.max_payload_bytes),
        "anonsync_replica reconciliation receiver service");
    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, false,
        "anonsync_replica reconciliation client TLS context");
    anonsync::SyncReplicaStreamConnector connector(
        std::move(stream_route),
        "anonsync_replica reconcile-pull outbound route");

    anonsync::SyncReplicaReconciliationTlsPullOptions pull_options;
    pull_options.max_round_trips = max_round_trips;
    pull_options.max_source_resets = max_source_resets;
    pull_options.after_operation_id = std::move(after_operation_id);
    pull_options.expected_source_evidence_set_digest =
        std::move(source_evidence_set_digest);
    pull_options.payload_continuation = std::move(payload_continuation);
    const auto result =
        anonsync::pull_sync_replica_reconciliation_tls_session_or_throw(
            service,
            anonsync::retain_sync_replica_file_tls_client_context_or_throw(
                context.get(),
                "anonsync_replica retained reconciliation client context"),
            connector, expected_peer, std::move(pull_options), deadlines,
            "anonsync_replica reconcile-pull session");

    std::cout << "{\"command\":\"reconcile-pull\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"session_timeout_seconds\":" << timeout_seconds
        << ",\"max_round_trips\":" << max_round_trips
        << ",\"max_source_resets\":" << max_source_resets;
    append_reconciliation_client_session_json_fields(std::cout, result);
    std::cout << "}\n";
    return reconciliation_pull_is_bounded_success(result) ? 0 : 2;
#endif
}

struct ServeSessionsExecution final {
    anonsync::SyncReplicaDeploymentManifest deployment;
    ServePublicationKind publication_kind = ServePublicationKind::DirectTcp;
    std::optional<anonsync::SyncReplicaStreamConnectReport>
        i2p_forward_setup;
    bool peer_dispatch_enabled = false;
    std::uint64_t maximum_sessions = 0U;
    std::optional<std::uint64_t> maximum_runtime_seconds;
    std::uint64_t session_timeout_seconds = 0U;
    std::uint64_t reconciliation_max_round_trips = 0U;
    std::uint64_t receipts_sent = 0U;
    std::uint64_t reconciliations_served = 0U;
    anonsync::SyncReplicaServeSupervisorStopReason stop_reason =
        anonsync::SyncReplicaServeSupervisorStopReason::MaximumSessionsReached;
    std::vector<anonsync::SyncReplicaFileTlsServerResult> sessions;
    std::vector<anonsync::SyncReplicaPeerTlsServerResult> peer_sessions;

    [[nodiscard]] std::size_t sessions_attempted() const noexcept {
        return peer_dispatch_enabled ? peer_sessions.size() : sessions.size();
    }
};

[[nodiscard]] ServeSessionsExecution execute_serve_sessions_or_throw(
    const Options& options,
    std::string_view command_name,
    std::uint64_t maximum_sessions,
    std::optional<std::uint64_t> maximum_runtime_seconds) {
    if (maximum_sessions == 0U ||
        maximum_sessions > kMaximumBatchSessions) {
        throw std::logic_error("invalid internal serve-session bound");
    }

    ServeRouteSelection publication =
        serve_route_from_options_or_throw(options);
    const std::uint64_t timeout_seconds = receiver_timeout_from_options(
        options, publication.kind);
    if (publication.kind == ServePublicationKind::I2pSamForward &&
        maximum_runtime_seconds.has_value() &&
        *maximum_runtime_seconds < timeout_seconds) {
        throw std::invalid_argument(
            "--max-runtime-seconds must be at least --timeout-seconds for "
            "--transport i2p");
    }
    anonsync::SyncReplicaSessionSupervisor supervisor(
        {maximum_sessions, timeout_seconds, maximum_runtime_seconds},
        std::chrono::steady_clock::now(),
        "anonsync_replica " + std::string(command_name) + " supervisor");

    ServeSessionsExecution execution;
    execution.publication_kind = publication.kind;
    execution.maximum_sessions = maximum_sessions;
    execution.maximum_runtime_seconds = maximum_runtime_seconds;
    execution.session_timeout_seconds = timeout_seconds;
    execution.reconciliation_max_round_trips =
        reconciliation_max_round_trips_from_options(options);
    execution.deployment =
        load_operational_deployment_manifest_or_throw(options, command_name);
    execution.peer_dispatch_enabled =
        execution.deployment.payload_root.has_value();
    if (execution.peer_dispatch_enabled) {
        execution.peer_sessions.reserve(
            static_cast<std::size_t>(maximum_sessions));
    } else {
        execution.sessions.reserve(static_cast<std::size_t>(maximum_sessions));
    }
    require_effect_store(execution.deployment, command_name);
    require_membership_store(execution.deployment, command_name);
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");

#ifndef __linux__
    (void)certificate;
    (void)private_key;
    (void)ca_file;
    (void)publication;
    (void)supervisor;
    throw std::runtime_error(
        std::string(command_name) + " requires Linux");
#else
    // Prove every prerequisite without bootstrap authority. A bad TLS
    // identity, occupied listener, or any selected-store typo must not leave a
    // new database family or authorize a different receiver/effect pair.
    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, true,
        "anonsync_replica server TLS context");
    anonsync::SyncReplicaNumericListener listener_socket(
        publication.listener_endpoint, "anonsync_replica listener");
    auto& listener = listener_socket.listener_or_throw();
    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            execution.deployment, *execution.deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            "anonsync_replica membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            execution.deployment, *execution.deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            "anonsync_replica membership anchor database");

    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, execution.deployment.folder_id,
        execution.deployment.local_actor,
        "anonsync_replica membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, execution.deployment.folder_id,
        execution.deployment.local_actor,
        "anonsync_replica membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner,
        "anonsync_replica anchored membership coordinator");
    // Resolve and independently anchor the first policy cutpoint before later
    // receiver/effect opens, preserving the one-session command's preflight
    // order. Every subsequent session refreshes this move-only authority so a
    // policy rotation cannot be silently frozen for the whole batch.
    auto membership = coordinator.current_authority_or_throw();

    ProductSqliteDatabaseAuthority replica_database =
        open_bound_operational_database_or_throw(
            execution.deployment, execution.deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica receiver database");
    ProductSqliteDatabaseAuthority effect_database =
        open_bound_operational_database_or_throw(
            execution.deployment, *execution.deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            "anonsync_replica effect database");
    anonsync::SyncReplicaSqliteOwner owner(
        replica_database.db, execution.deployment.folder_id,
        execution.deployment.local_actor, {},
        "anonsync_replica receiver owner");
    anonsync::SyncReplicaFileEffectSqliteOwner effect_owner(
        effect_database.db, execution.deployment.folder_id,
        *execution.deployment.files_root,
        effect_owner_limits(execution.deployment.max_payload_bytes),
        "anonsync_replica receiver effect owner");
    anonsync::SyncReplicaFileDeliveryService service(
        owner, &effect_owner,
        file_service_limits(execution.deployment.max_payload_bytes),
        "anonsync_replica receiver service");

    // A combined deployment exposes one authenticated peer endpoint for both
    // one-shot file delivery and share-global reconciliation. Receiver-only
    // deployments preserve the original file-only grammar and do not gain an
    // implicit payload-store requirement.
    std::unique_ptr<anonsync::SyncReplicaFilePayloadStore>
        reconciliation_payload_store;
    std::unique_ptr<anonsync::SyncReplicaReconciliationService>
        reconciliation_service;
    if (execution.peer_dispatch_enabled) {
        reconciliation_payload_store =
            std::make_unique<anonsync::SyncReplicaFilePayloadStore>(
                anonsync::sync_replica_deployment_identity_or_throw(
                    execution.deployment,
                    "anonsync_replica reconciliation payload identity"),
                *execution.deployment.payload_root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                    ExistingOnly,
                payload_store_limits(execution.deployment.max_payload_bytes),
                "anonsync_replica reconciliation payload store");
        reconciliation_service =
            std::make_unique<anonsync::SyncReplicaReconciliationService>(
                owner, *reconciliation_payload_store,
                reconciliation_protocol_limits(
                    execution.deployment.max_payload_bytes),
                "anonsync_replica reconciliation service");
    }

    std::unique_ptr<anonsync::SyncReplicaI2pSamForwarder> i2p_forwarder;
    if (publication.i2p_forward.has_value()) {
        i2p_forwarder =
            std::make_unique<anonsync::SyncReplicaI2pSamForwarder>(
                std::move(*publication.i2p_forward),
                "anonsync_replica inbound I2P SAM forwarder");
        auto setup_deadline = std::chrono::steady_clock::now() +
            std::chrono::seconds(timeout_seconds);
        if (supervisor.command_deadline().has_value() &&
            *supervisor.command_deadline() < setup_deadline) {
            setup_deadline = *supervisor.command_deadline();
        }
        execution.i2p_forward_setup =
            i2p_forwarder->start_until_or_throw(setup_deadline);
        if (execution.i2p_forward_setup->disposition !=
            anonsync::SyncReplicaStreamConnectDisposition::Connected) {
            throw std::runtime_error(
                "anonsync_replica I2P SAM publication failed at " +
                std::string(anonsync::sync_replica_stream_route_stage_name(
                    execution.i2p_forward_setup->terminal_stage)) +
                " with " +
                std::string(
                    anonsync::sync_replica_stream_connect_disposition_name(
                        execution.i2p_forward_setup->disposition)));
        }
    }

    for (;;) {
        const anonsync::SyncReplicaSessionAuthorization authorization =
            supervisor.authorize_next_or_throw();
        if (authorization.disposition == anonsync::
                SyncReplicaSessionAuthorizationDisposition::
                    MaximumSessionsReached) {
            execution.stop_reason = anonsync::
                SyncReplicaServeSupervisorStopReason::MaximumSessionsReached;
            break;
        }
        if (authorization.disposition == anonsync::
                SyncReplicaSessionAuthorizationDisposition::
                    CommandDeadlineReached) {
            execution.stop_reason = anonsync::
                SyncReplicaServeSupervisorStopReason::CommandDeadlineReached;
            break;
        }
        if (!authorization.plan.has_value()) {
            throw std::logic_error(
                "authorized serve session omitted its deadline plan");
        }
        const anonsync::SyncReplicaSessionDeadlinePlan& plan =
            *authorization.plan;
        if (i2p_forwarder) {
            i2p_forwarder->require_active_or_throw(
                "anonsync_replica retained inbound I2P publication");
        }
        if (plan.session_index != 1U) {
            membership = coordinator.current_authority_or_throw();
        }
        const std::string session_label =
            "anonsync_replica " + std::string(command_name) + " session " +
            std::to_string(plan.session_index);
        bool receipt_sent = false;
        bool reconciliation_served = false;
        std::optional<anonsync::SyncReplicaServeSupervisorStopReason> stop;

        if (execution.peer_dispatch_enabled) {
            if (!reconciliation_service) {
                throw std::logic_error(
                    "combined peer dispatcher omitted reconciliation service");
            }
            auto result =
                anonsync::serve_one_sync_replica_peer_tls_session_or_throw(
                    service, *reconciliation_service, listener,
                    anonsync::
                        retain_sync_replica_file_tls_server_context_or_throw(
                            context.get(),
                            "anonsync_replica retained server context"),
                    std::move(membership), plan.server_deadlines(),
                    execution.reconciliation_max_round_trips, session_label);
            if (result.application.has_value()) {
                receipt_sent = result.application->file_delivery.has_value() &&
                    result.application->file_delivery->disposition ==
                        anonsync::SyncReplicaFileTlsReceiveDisposition::
                            ReceiptSent;
                reconciliation_served =
                    result.application->disposition == anonsync::
                        SyncReplicaPeerTlsServeDisposition::Reconciliation &&
                    result.application->reconciliation.has_value();
            }
            stop = anonsync::sync_replica_serve_supervisor_stop_after(result);
            execution.peer_sessions.push_back(std::move(result));
        } else {
            auto result = anonsync::
                serve_one_sync_replica_file_delivery_tls_session_or_throw(
                    service, listener,
                    anonsync::
                        retain_sync_replica_file_tls_server_context_or_throw(
                            context.get(),
                            "anonsync_replica retained server context"),
                    std::move(membership), plan.server_deadlines(),
                    session_label);
            receipt_sent = result.disposition ==
                anonsync::SyncReplicaFileTlsServerDisposition::ReceiptSent;
            stop = anonsync::sync_replica_serve_supervisor_stop_after(result);
            execution.sessions.push_back(std::move(result));
        }

        if (stop == anonsync::
                SyncReplicaServeSupervisorStopReason::AcceptDeadlineExpired &&
            plan.command_limits(anonsync::SyncReplicaSessionStage::First) &&
            supervisor.command_deadline_reached_at(
                std::chrono::steady_clock::now())) {
            stop = anonsync::
                SyncReplicaServeSupervisorStopReason::CommandDeadlineReached;
        }
        if (receipt_sent) ++execution.receipts_sent;
        if (reconciliation_served) ++execution.reconciliations_served;
        if (!stop.has_value()) continue;
        execution.stop_reason = *stop;
        break;
    }
    return execution;
#endif
}

void append_serve_publication_json_fields(
    std::ostream& output,
    const ServeSessionsExecution& execution) {
    output << ",\"transport\":"
           << json_quote(serve_publication_kind_name(
                  execution.publication_kind));
    if (!execution.i2p_forward_setup.has_value()) return;
    const auto& report = *execution.i2p_forward_setup;
    output
        << ",\"i2p_forward_route_disposition\":"
        << json_quote(anonsync::sync_replica_stream_connect_disposition_name(
               report.disposition))
        << ",\"i2p_forward_route_terminal_stage\":"
        << json_quote(anonsync::sync_replica_stream_route_stage_name(
               report.terminal_stage))
        << ",\"i2p_forward_route_negotiated\":"
        << json_bool(report.route_negotiated)
        << ",\"i2p_forward_control_session_created\":"
        << json_bool(report.control_session_created)
        << ",\"i2p_forward_socket_created\":"
        << json_bool(report.data_socket_created)
        << ",\"i2p_forward_socket_policy_verified\":"
        << json_bool(report.data_socket_policy_verified)
        << ",\"i2p_forward_numeric_connect_attempts\":"
        << report.numeric_connect_attempts
        << ",\"i2p_forward_route_bytes_written\":"
        << report.route_bytes_written
        << ",\"i2p_forward_route_bytes_received\":"
        << report.route_bytes_received;
    if (report.sam_result.has_value()) {
        output << ",\"i2p_forward_sam_result\":"
               << json_quote(anonsync::sync_replica_i2p_sam_result_name(
                      *report.sam_result));
    }
}

int command_serve_one(const Options& options) {
    options.require_only({
        "manifest", "bind-address", "port", "certificate", "private-key",
        "ca-file", "timeout-seconds", "transport", "onion-address",
        "onion-port", "tor-socks-address", "tor-socks-port",
        "tor-isolation-token", "i2p-sam-address", "i2p-sam-port",
        "i2p-destination", "i2p-session-id",
        "i2p-private-destination-file", "i2p-inbound-quantity",
        "i2p-outbound-quantity", "max-round-trips"});
    const ServeSessionsExecution execution = execute_serve_sessions_or_throw(
        options, "serve-one", 1U, std::nullopt);

    std::cout << "{\"command\":\"serve-one\"";
    append_serve_publication_json_fields(std::cout, execution);
    append_deployment_authority_json_fields(std::cout, execution.deployment);
    std::cout << ",\"session_timeout_seconds\":"
              << execution.session_timeout_seconds
              << ",\"peer_dispatch_enabled\":"
              << json_bool(execution.peer_dispatch_enabled);
    if (execution.peer_dispatch_enabled) {
        std::cout << ",\"max_round_trips\":"
                  << execution.reconciliation_max_round_trips;
    }
    std::cout << ",\"stop_reason\":"
              << json_quote(anonsync::
                     sync_replica_serve_supervisor_stop_reason_name(
                         execution.stop_reason));
    if (execution.peer_dispatch_enabled) {
        append_peer_server_session_json_fields(
            std::cout, execution.peer_sessions.front());
    } else {
        append_server_session_json_fields(std::cout, execution.sessions.front());
    }
    std::cout << "}\n";

    return anonsync::sync_replica_serve_supervisor_stop_is_success(
               execution.stop_reason)
        ? 0
        : 2;
}

int command_serve_batch(const Options& options) {
    options.require_only({
        "manifest", "bind-address", "port", "certificate", "private-key",
        "ca-file", "timeout-seconds", "max-sessions",
        "max-runtime-seconds", "transport", "onion-address",
        "onion-port", "tor-socks-address", "tor-socks-port",
        "tor-isolation-token", "i2p-sam-address", "i2p-sam-port",
        "i2p-destination", "i2p-session-id",
        "i2p-private-destination-file", "i2p-inbound-quantity",
        "i2p-outbound-quantity", "max-round-trips"});
    const std::uint64_t maximum_sessions = max_sessions_from_options(options);
    const std::uint64_t maximum_runtime_seconds =
        max_runtime_from_options(options);
    const ServeSessionsExecution execution = execute_serve_sessions_or_throw(
        options, "serve-batch", maximum_sessions, maximum_runtime_seconds);

    std::cout << "{\"command\":\"serve-batch\"";
    append_serve_publication_json_fields(std::cout, execution);
    append_deployment_authority_json_fields(std::cout, execution.deployment);
    std::cout
        << ",\"max_sessions\":" << execution.maximum_sessions
        << ",\"max_runtime_seconds\":"
        << *execution.maximum_runtime_seconds
        << ",\"session_timeout_seconds\":"
        << execution.session_timeout_seconds
        << ",\"peer_dispatch_enabled\":"
        << json_bool(execution.peer_dispatch_enabled)
        << ",\"max_round_trips\":"
        << execution.reconciliation_max_round_trips
        << ",\"sessions_attempted\":" << execution.sessions_attempted()
        << ",\"receipts_sent\":" << execution.receipts_sent
        << ",\"reconciliations_served\":"
        << execution.reconciliations_served
        << ",\"stop_reason\":"
        << json_quote(anonsync::
               sync_replica_serve_supervisor_stop_reason_name(
                   execution.stop_reason))
        << ",\"sessions\":[";
    for (std::size_t index = 0U; index < execution.sessions_attempted(); ++index) {
        if (index != 0U) std::cout << ',';
        std::cout << "{\"session_index\":" << index + 1U;
        if (execution.peer_dispatch_enabled) {
            append_peer_server_session_json_fields(
                std::cout, execution.peer_sessions[index]);
        } else {
            append_server_session_json_fields(
                std::cout, execution.sessions[index]);
        }
        std::cout << '}';
    }
    std::cout << "]}\n";

    return anonsync::sync_replica_serve_supervisor_stop_is_success(
               execution.stop_reason)
        ? 0
        : 2;
}


int command_certificate_spki(const Options& options) {
    options.require_only({"certificate"});
    const fs::path certificate_path = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    ERR_clear_error();
    BioOwner input(
        BIO_new_file(certificate_path.string().c_str(), "rb"), BIO_free);
    if (!input) throw_openssl("could not open certificate");
    CertificateOwner certificate(
        PEM_read_bio_X509(input.get(), nullptr, nullptr, nullptr), X509_free);
    if (!certificate) throw_openssl("could not parse PEM certificate");
    X509_PUBKEY* public_key = X509_get_X509_PUBKEY(certificate.get());
    if (public_key == nullptr) {
        throw std::runtime_error("certificate has no SubjectPublicKeyInfo");
    }
    const int encoded_bytes = i2d_X509_PUBKEY(public_key, nullptr);
    if (encoded_bytes <= 0) {
        throw_openssl("could not size certificate SubjectPublicKeyInfo");
    }
    std::string encoded(static_cast<std::size_t>(encoded_bytes), '\0');
    unsigned char* output =
        reinterpret_cast<unsigned char*>(encoded.data());
    if (i2d_X509_PUBKEY(public_key, &output) != encoded_bytes) {
        throw_openssl("could not encode certificate SubjectPublicKeyInfo");
    }
    std::cout
        << "{\"command\":\"certificate-spki\",\"spki_sha256\":"
        << json_quote(anonsync::sha256_hex(encoded)) << "}\n";
    return 0;
}

void print_usage(std::ostream& output) {
    output <<
        "AnonSync C++ peer-to-peer folder synchronization product spine\n"
        "Goal: replace Resilio Sync, including direct, Tor, and I2P routes.\n\n"
        "Commands:\n"
        "  anonsync_replica init --manifest ABSOLUTE_JSON "
        "--replica-db ABSOLUTE_DB --folder ID --local-device ID "
        "--local-epoch N [--max-payload-bytes N] "
        "[--initial-files empty|adopt-existing] "
        "[--payload-root ABSOLUTE_DIR] "
        "[--effect-db ABSOLUTE_DB --files-root ABSOLUTE_DIR] "
        "[--membership-db ABSOLUTE_DB --anchor-db ABSOLUTE_DB]\n"
        "  anonsync_replica init-resume --manifest ABSOLUTE_JSON "
        "[--initial-files empty|adopt-existing]\n"
        "  anonsync_replica certificate-spki --certificate ABSOLUTE_PEM\n"
        "  anonsync_replica status --manifest ABSOLUTE_JSON\n"
        "  anonsync_replica clock-observe --manifest ABSOLUTE_JSON "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica clock-recover --manifest ABSOLUTE_JSON "
        "--expected-observation-generation N "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica enqueue-file --manifest ABSOLUTE_JSON "
        "--destination-device ID [--destination-device ID...] "
        "--canonical-path PATH --source-file ABSOLUTE_FILE\n"
        "  anonsync_replica membership-publish --manifest ABSOLUTE_JSON "
        "--policy-epoch N [--peer DEVICE:EPOCH:SPKI_SHA256 ...]\n"
        "  anonsync_replica send-one --manifest ABSOLUTE_JSON "
        "--remote-device ID --remote-epoch N --remote-spki SHA256 "
        "--certificate ABSOLUTE_PEM "
        "--private-key ABSOLUTE_PEM --ca-file ABSOLUTE_PEM "
        "[--transport direct --address NUMERIC_IP --port N | "
        "--transport tor --onion-address V3_ONION --onion-port N "
        "[--tor-socks-address NUMERIC_IP] [--tor-socks-port N] "
        "[--tor-isolation-token TOKEN] | "
        "--transport i2p --i2p-destination DESTINATION "
        "[--i2p-sam-address NUMERIC_IP] [--i2p-sam-port N] "
        "[--i2p-session-id ID] "
        "[--i2p-private-destination-file ABSOLUTE_FILE] "
        "[--i2p-inbound-quantity N] [--i2p-outbound-quantity N]] "
        "[--worker ID] [--lease-seconds N] [--timeout-seconds N] "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica send-batch --manifest ABSOLUTE_JSON "
        "--max-sessions N --max-runtime-seconds N "
        "--remote-device ID --remote-epoch N "
        "--remote-spki SHA256 "
        "--certificate ABSOLUTE_PEM --private-key ABSOLUTE_PEM "
        "--ca-file ABSOLUTE_PEM "
        "[--transport direct --address NUMERIC_IP --port N | "
        "--transport tor --onion-address V3_ONION --onion-port N "
        "[--tor-socks-address NUMERIC_IP] [--tor-socks-port N] "
        "[--tor-isolation-token TOKEN] | "
        "--transport i2p --i2p-destination DESTINATION "
        "[--i2p-sam-address NUMERIC_IP] [--i2p-sam-port N] "
        "[--i2p-session-id ID] "
        "[--i2p-private-destination-file ABSOLUTE_FILE] "
        "[--i2p-inbound-quantity N] [--i2p-outbound-quantity N]] "
        "[--worker ID] [--lease-seconds N] "
        "[--timeout-seconds N] [--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica reconcile-pull --manifest ABSOLUTE_JSON "
        "--remote-device ID --remote-epoch N --remote-spki SHA256 "
        "--certificate ABSOLUTE_PEM --private-key ABSOLUTE_PEM "
        "--ca-file ABSOLUTE_PEM "
        "[--transport direct --address NUMERIC_IP --port N | "
        "--transport tor --onion-address V3_ONION --onion-port N "
        "[--tor-socks-address NUMERIC_IP] [--tor-socks-port N] "
        "[--tor-isolation-token TOKEN] | "
        "--transport i2p --i2p-destination DESTINATION "
        "[--i2p-sam-address NUMERIC_IP] [--i2p-sam-port N] "
        "[--i2p-session-id ID] "
        "[--i2p-private-destination-file ABSOLUTE_FILE] "
        "[--i2p-inbound-quantity N] [--i2p-outbound-quantity N]] "
        "[--max-round-trips N] [--max-source-resets N] "
        "[--after-operation-id SHA256] "
        "[--source-evidence-set-digest SHA256 "
        "--payload-operation-id SHA256 "
        "--payload-content-sha256 SHA256 "
        "--payload-total-size N --payload-next-offset N] "
        "[--timeout-seconds N]\n"
        "  anonsync_replica serve-one --manifest ABSOLUTE_JSON "
        "--bind-address NUMERIC_IP --port N "
        "--certificate ABSOLUTE_PEM --private-key ABSOLUTE_PEM "
        "--ca-file ABSOLUTE_PEM "
        "[--transport direct | --transport tor "
        "--onion-address V3_ONION --onion-port N | --transport i2p "
        "--i2p-private-destination-file ABSOLUTE_FILE "
        "[--i2p-sam-address NUMERIC_IP] [--i2p-sam-port N] "
        "[--i2p-session-id ID] [--i2p-inbound-quantity N] "
        "[--i2p-outbound-quantity N]] [--max-round-trips N] "
        "[--timeout-seconds N]\n"
        "  anonsync_replica serve-batch --manifest ABSOLUTE_JSON "
        "--max-sessions N --max-runtime-seconds N "
        "--bind-address NUMERIC_IP --port N "
        "--certificate ABSOLUTE_PEM --private-key ABSOLUTE_PEM "
        "--ca-file ABSOLUTE_PEM "
        "[--transport direct | --transport tor "
        "--onion-address V3_ONION --onion-port N | --transport i2p "
        "--i2p-private-destination-file ABSOLUTE_FILE "
        "[--i2p-sam-address NUMERIC_IP] [--i2p-sam-port N] "
        "[--i2p-session-id ID] [--i2p-inbound-quantity N] "
        "[--i2p-outbound-quantity N]] [--max-round-trips N] "
        "[--timeout-seconds N]\n\n"
        "All paths must be absolute. init is the sole fresh product-spine "
        "bootstrap authority: it proves a clean namespace, durably publishes "
        "an immutable record containing the exact future manifest, initializes "
        "the selected stores, and publishes the manifest last. The default "
        "--initial-files empty keeps fresh bootstrap fail-closed; the explicit "
        "adopt-existing mode permits only ordinary pre-existing files in the "
        "selected folder root, which remain unpublished until the configured "
        "folder owner observes them. init-resume can only resume that exact "
        "recorded deployment after two-phase identity "
        "and role-state attestation; it never adopts path-selected stores. The "
        "selected resources are individually durable but are not one "
        "cross-resource atomic transaction. Absence of the manifest means the "
        "deployment has not reached its committed operational cutpoint. Every "
        "operational "
        "command loads one bounded, no-symlink, canonical, self-digested "
        "manifest before opening a store and derives every store path, local "
        "identity, folder, and payload ceiling from it. Missing, copied, "
        "tampered, noncanonical, or policy-incompatible manifests fail closed. "
        "Operational database and payload opens are existing-only and cannot "
        "mint a database, payload identity marker, or alternate store set. "
        "status emits a bounded attested condition report. clock-observe "
        "samples and publishes clock health without claiming work; "
        "clock-recover requires the exact current quarantine generation. "
        "send-one and serve-one each own exactly one bounded TLS conversation. "
        "A combined payload/effect/membership deployment serves file delivery "
        "and bounded reconciliation on that same authenticated endpoint; "
        "reconcile-pull imports share-global evidence and payload pages over "
        "direct, Tor, or I2P without requiring a second listener or TLS owner. "
        "send-batch and serve-batch require both --max-sessions and "
        "--max-runtime-seconds, retain one manifest/store/context cutpoint, and "
        "mint fresh staged deadlines clamped to one absolute command cutpoint "
        "that begins before deployment/store/TLS preflight. Synchronous local "
        "work is not asynchronously preempted, but its elapsed time is charged "
        "at the next admission or I/O deadline. They stop on transport "
        "ambiguity, peer rejection, local receipt-apply conflict, or "
        "authenticated receiver deferral; receiver deferral is nonfatal bounded "
        "progress rather than permission to amplify causally later work. An "
        "authorized peer close is nonfatal idle only after a completed TLS "
        "handshake with zero application prefix, frame, body, inbound decision, "
        "or receipt write; that classification is not evidence that the peer had "
        "no work. The commands are bounded supervisors, not background daemons: "
        "they do not invent retry, backoff, peer discovery, or scheduling "
        "authority. Outbound direct TCP is the compatibility default. Tor "
        "uses SOCKS5 username/password circuit isolation and sends only a "
        "checksum-valid v3 onion name to the numeric local proxy. I2P uses one "
        "persistent command-local SAM 3.1 STREAM session and fresh data "
        "streams; its stage timeout defaults to and may not be less than 180 "
        "seconds, and a batch does not start a stream without that much command "
        "budget remaining. Every receiver remains one numeric TLS listener. "
        "A Tor receiver profile requires that listener to be loopback and validates "
        "the checksum-bearing v3 onion identity and virtual port, while the Tor "
        "daemon remains the explicit onion-service publication owner. An I2P "
        "receiver natively owns one persistent SAM 3.1 STREAM session plus one "
        "STREAM FORWARD control socket, requires a persistent private destination, "
        "targets only the loopback TLS listener, and forces SILENT=true so SAM "
        "cannot inject an I2P destination line ahead of TLS. SOCKS and SAM bridge "
        "endpoints are loopback-only until authenticated remote-proxy transport "
        "exists. "
        "send-one and send-batch derive the default durable claim lease "
        "from the receipt horizon and exact durable clock policy; an explicit "
        "shorter lease is rejected before manifest, store, payload, TLS, or "
        "socket authority is opened. This is a necessary protocol/clock lower "
        "bound, not a real-time completion guarantee: process descheduling, "
        "SQLite writer waits, local receipt application, and arbitrary system "
        "suspension remain outside the static proof; expiry still fails closed. "
        "Transport deadlines and durable lease observations also use different "
        "Linux clock domains. They default to the fail-closed kernel clock "
        "source; paired "
        "operator-clock options are "
        "an explicit deployment assertion for externally owned synchronization "
        "evidence. JSON is written to stdout and diagnostics to stderr.\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2 || std::string_view(argv[1]) == "--help" ||
            std::string_view(argv[1]) == "help") {
            print_usage(std::cout);
            return argc < 2 ? 2 : 0;
        }
        anonsync::install_sync_replica_sigpipe_ignore_policy_or_throw(
            "anonsync_replica SIGPIPE policy");
        const std::string command = argv[1];
        const Options options(argc, argv, 2);
        if (command == "init") {
            return command_init(options);
        }
        if (command == "init-resume") {
            return command_init_resume(options);
        }
        if (command == "status") {
            return command_status(options);
        }
        if (command == "clock-observe") {
            return command_clock_observe(options);
        }
        if (command == "clock-recover") {
            return command_clock_recover(options);
        }
        if (command == "enqueue-file") {
            return command_enqueue_file(options);
        }
        if (command == "membership-publish") {
            return command_membership_publish(options);
        }
        if (command == "send-one") {
            return command_send_one(options);
        }
        if (command == "send-batch") {
            return command_send_batch(options);
        }
        if (command == "reconcile-pull") {
            return command_reconcile_pull(options);
        }
        if (command == "serve-one") {
            return command_serve_one(options);
        }
        if (command == "serve-batch") {
            return command_serve_batch(options);
        }
        if (command == "certificate-spki") {
            return command_certificate_spki(options);
        }
        throw std::invalid_argument("unknown command: " + command);
    } catch (const std::exception& error) {
        std::cerr << "anonsync_replica: " << error.what() << '\n';
        return 1;
    }
}
