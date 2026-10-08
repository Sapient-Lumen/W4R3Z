#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_linked_peer_pairing.hpp"
#include "sync_linked_peer_user_layout.hpp"
#include "sync_local_share_setup.hpp"
#include "sync_local_status_socket.hpp"
#include "sync_linux_process_resources.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_database_backup.hpp"
#include "sync_replica_database_replacement.hpp"
#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_folder_scan_owner.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_peer_service.hpp"
#include "sync_replica_peer_service_configuration.hpp"
#include "sync_replica_peer_service_provisioning.hpp"
#include "sync_replica_peer_service_singleton.hpp"
#include "sync_replica_peer_service_status.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_replica_stream_connector.hpp"
#include "sync_replica_sync_once.hpp"
#include "sync_replica_tls_transport.hpp"
#include "sync_systemd_notify.hpp"

#include <algorithm>
#include <charconv>
#include <csignal>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

#include <signal.h>

#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/ssl.h>

#if !defined(_WIN32)

namespace {

namespace fs = std::filesystem;
using SslContextOwner = std::unique_ptr<SSL_CTX, decltype(&SSL_CTX_free)>;

constexpr std::uint64_t kDefaultTimeoutSeconds = 10U;
constexpr std::uint64_t kDefaultI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMinimumI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMaximumTimeoutSeconds = 3600U;
constexpr std::uint64_t kMaximumRuntimeSeconds = 86400U;
constexpr std::uint64_t kMaximumI2pPrivateDestinationBytes = 8192U;
constexpr std::uint64_t kDefaultI2pTunnelQuantity = 2U;
constexpr std::uint64_t kMaximumI2pTunnelQuantity = 16U;

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
            std::string token(argv[index]);
            if (!token.starts_with("--") || token.size() <= 2U) {
                throw std::invalid_argument(
                    "unexpected positional argument: " + token);
            }
            token.erase(0U, 2U);
            std::string key;
            std::string value;
            const std::size_t equals = token.find('=');
            if (equals == std::string::npos) {
                key = std::move(token);
                if (index + 1 >= argc ||
                    std::string_view(argv[index + 1]).starts_with("--")) {
                    throw std::invalid_argument(
                        "missing value for --" + key);
                }
                value = argv[++index];
            } else {
                key = token.substr(0U, equals);
                value = token.substr(equals + 1U);
            }
            if (key.empty()) {
                throw std::invalid_argument("empty option name");
            }
            values_[std::move(key)].push_back(std::move(value));
        }
    }

    void require_only(std::initializer_list<std::string_view> allowed) const {
        const std::set<std::string_view> accepted(
            allowed.begin(), allowed.end());
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

    [[nodiscard]] std::string one(std::string_view key) const {
        const auto found = values_.find(std::string(key));
        if (found == values_.end()) {
            throw std::invalid_argument(
                "required option --" + std::string(key) + " is missing");
        }
        if (found->second.size() != 1U || found->second.front().empty()) {
            throw std::invalid_argument(
                "option --" + std::string(key) +
                " must appear exactly once with a nonempty value");
        }
        return found->second.front();
    }

    [[nodiscard]] std::string one_or(
        std::string_view key,
        std::string fallback) const {
        return has(key) ? one(key) : std::move(fallback);
    }

    [[nodiscard]] std::vector<std::string> many(
        std::string_view key) const {
        const auto found = values_.find(std::string(key));
        if (found == values_.end()) return {};
        for (const std::string& value : found->second) {
            if (value.empty()) {
                throw std::invalid_argument(
                    "option --" + std::string(key) +
                    " must not contain an empty value");
            }
        }
        return found->second;
    }

private:
    std::map<std::string, std::vector<std::string>> values_;
};

[[nodiscard]] std::uint64_t parse_uint64(
    std::string_view text,
    std::string_view label) {
    std::uint64_t value = 0U;
    const char* const begin = text.data();
    const char* const end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end) {
        throw std::invalid_argument(
            std::string(label) + " is not an unsigned decimal integer");
    }
    return value;
}

[[nodiscard]] std::uint64_t option_uint64_or(
    const Options& options,
    std::string_view key,
    std::uint64_t fallback) {
    return options.has(key)
        ? parse_uint64(options.one(key), "--" + std::string(key))
        : fallback;
}

[[nodiscard]] std::optional<std::uint64_t> optional_uint64(
    const Options& options,
    std::string_view key) {
    if (!options.has(key)) return std::nullopt;
    return parse_uint64(options.one(key), "--" + std::string(key));
}

[[nodiscard]] std::uint16_t parse_port(
    std::string_view text,
    std::string_view label) {
    const std::uint64_t value = parse_uint64(text, label);
    if (value == 0U || value > 65535U) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, 65535]");
    }
    return static_cast<std::uint16_t>(value);
}

[[nodiscard]] std::string stable_service_default_token_or_throw(
    std::string_view purpose,
    std::string_view scope,
    std::string_view prefix) {
    if (purpose.empty() || scope.empty()) {
        throw std::invalid_argument(
            "stable service-default purpose and scope must be nonempty");
    }
    std::string material("anonsync.linked-peer-service-default.v1\n");
    material.append(purpose);
    material.push_back('\n');
    material.append(scope);
    const std::string digest = anonsync::sha256_hex(material);
    return std::string(prefix) + digest.substr(0U, 32U);
}

[[nodiscard]] std::string linked_service_default_scope(
    std::string_view instance,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const anonsync::SyncReplicaTlsPeerPolicy& peer) {
    std::string scope(instance);
    scope.push_back('\n');
    scope += deployment.deployment_id;
    scope.push_back('\n');
    scope += deployment.local_actor.device_id;
    scope.push_back('\n');
    scope += std::to_string(deployment.local_actor.epoch);
    scope.push_back('\n');
    scope += peer.actor.device_id;
    scope.push_back('\n');
    scope += std::to_string(peer.actor.epoch);
    scope.push_back('\n');
    scope += peer.spki_sha256;
    return scope;
}

[[nodiscard]] fs::path require_absolute_path(
    std::string value,
    std::string_view label) {
    fs::path path(std::move(value));
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute path");
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

[[nodiscard]] bool regular_file_is_present_or_throw(
    const fs::path& path,
    std::string_view label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error) {
        if (error == std::errc::no_such_file_or_directory) return false;
        throw std::runtime_error(
            std::string(label) + " could not inspect " +
            path.generic_string() + ": " + error.message());
    }
    if (status.type() == fs::file_type::not_found) return false;
    if (fs::is_symlink(status) || !fs::is_regular_file(status)) {
        throw std::runtime_error(
            std::string(label) +
            " must be absent or a non-symlink regular file: " +
            path.generic_string());
    }
    return true;
}

void reject_route_options_or_throw(
    const Options& options,
    std::initializer_list<std::string_view> rejected,
    std::string_view selected_transport) {
    for (const std::string_view key : rejected) {
        if (options.has(key)) {
            throw std::invalid_argument(
                "--" + std::string(key) +
                " is not valid with --transport " +
                std::string(selected_transport));
        }
    }
}

[[nodiscard]] std::string read_i2p_private_destination_file_or_throw(
    const fs::path& path,
    std::string_view label) {
    std::string destination =
        anonsync::read_sync_bounded_private_regular_file_no_symlink_or_throw(
            path, kMaximumI2pPrivateDestinationBytes, std::string(label));
    if (destination.ends_with('\n')) {
        destination.pop_back();
        if (destination.ends_with('\r')) destination.pop_back();
    }
    if (destination.empty()) {
        throw std::invalid_argument(std::string(label) + " is empty");
    }
    return destination;
}

[[nodiscard]] std::string read_i2p_private_destination_or_throw(
    const Options& options) {
    if (!options.has("i2p-private-destination-file")) {
        return "TRANSIENT";
    }
    const fs::path path = require_absolute_path(
        options.one("i2p-private-destination-file"),
        "--i2p-private-destination-file");
    return read_i2p_private_destination_file_or_throw(
        path, "--i2p-private-destination-file");
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
stream_route_from_options_or_throw(
    const Options& options,
    std::optional<std::string_view> stable_default_scope = std::nullopt) {
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
                : stable_default_scope.has_value()
                    ? stable_service_default_token_or_throw(
                          "tor-isolation", *stable_default_scope,
                          "anonsync-")
                    : random_hex_token_or_throw(
                          32U, "anonsync_sync Tor command isolation")};
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
                : stable_default_scope.has_value()
                    ? stable_service_default_token_or_throw(
                          "i2p-outbound-session", *stable_default_scope,
                          "anonsync-")
                    : "anonsync-" + random_hex_token_or_throw(
                          16U, "anonsync_sync I2P SAM session"),
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
        route, "anonsync_sync outbound stream route");
    return route;
}

[[nodiscard]] std::uint64_t timeout_from_options(
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

[[nodiscard]] std::uint64_t maximum_runtime_from_options(
    const Options& options,
    std::uint64_t timeout_seconds) {
    const std::uint64_t fallback = timeout_seconds * 6U;
    const std::uint64_t maximum = option_uint64_or(
        options, "max-runtime-seconds", fallback);
    if (maximum == 0U || maximum > kMaximumRuntimeSeconds) {
        throw std::invalid_argument(
            "--max-runtime-seconds must be in [1, 86400]");
    }
    return maximum;
}

[[nodiscard]] anonsync::SyncReplicaTlsPeerPolicy
expected_peer_from_options_or_throw(const Options& options) {
    anonsync::SyncReplicaActor actor{
        options.one("remote-device"),
        parse_uint64(options.one("remote-epoch"), "--remote-epoch")};
    if (!anonsync::sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument("remote actor identity is invalid");
    }
    const std::string spki = options.one("remote-spki");
    if (!anonsync::is_lowercase_sha256_hex(spki)) {
        throw std::invalid_argument(
            "--remote-spki must be lowercase SHA-256");
    }
    return {std::move(actor), spki};
}

[[nodiscard]] anonsync::SyncReplicaFolderConvergencePassLimits
folder_limits_from_options_or_throw(
    const Options& options,
    const anonsync::SyncReplicaDeploymentManifest& deployment) {
    anonsync::SyncReplicaFolderConvergencePassLimits limits =
        anonsync::sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            deployment.max_payload_bytes,
            "anonsync_sync deployment limits");
    limits.maximum_entries = option_uint64_or(
        options, "maximum-entries", limits.maximum_entries);
    limits.maximum_regular_files = option_uint64_or(
        options, "maximum-regular-files", limits.maximum_regular_files);
    limits.maximum_file_bytes = option_uint64_or(
        options, "maximum-file-bytes", deployment.max_payload_bytes);
    limits.maximum_total_file_bytes = option_uint64_or(
        options, "maximum-total-file-bytes",
        limits.maximum_total_file_bytes);
    limits.maximum_relative_path_bytes = option_uint64_or(
        options, "maximum-relative-path-bytes",
        limits.maximum_relative_path_bytes);
    limits.maximum_directory_depth = option_uint64_or(
        options, "maximum-directory-depth",
        limits.maximum_directory_depth);
    limits.maximum_remote_paths = option_uint64_or(
        options, "maximum-remote-paths", limits.maximum_remote_paths);
    limits.maximum_remote_inspection_paths = option_uint64_or(
        options, "maximum-remote-inspection-paths",
        limits.maximum_remote_inspection_paths);
    if (limits.maximum_file_bytes > deployment.max_payload_bytes) {
        throw std::invalid_argument(
            "--maximum-file-bytes exceeds manifest max_payload_bytes");
    }
    return limits;
}

[[nodiscard]] anonsync::SyncLocalShareFolderLimitOverrides
local_share_folder_limit_overrides_from_options(const Options& options) {
    return {
        .maximum_entries = optional_uint64(options, "maximum-entries"),
        .maximum_regular_files =
            optional_uint64(options, "maximum-regular-files"),
        .maximum_file_bytes = optional_uint64(options, "maximum-file-bytes"),
        .maximum_total_file_bytes =
            optional_uint64(options, "maximum-total-file-bytes"),
        .maximum_relative_path_bytes =
            optional_uint64(options, "maximum-relative-path-bytes"),
        .maximum_directory_depth =
            optional_uint64(options, "maximum-directory-depth"),
        .maximum_remote_paths =
            optional_uint64(options, "maximum-remote-paths"),
        .maximum_remote_inspection_paths =
            optional_uint64(options, "maximum-remote-inspection-paths"),
    };
}

[[nodiscard]] anonsync::SyncReplicaPeerServiceLimits
peer_service_limits_from_options_or_throw(
    const Options& options,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    anonsync::SyncReplicaStreamRouteKind route_kind,
    anonsync::SyncReplicaPeerIngressKind ingress_kind) {
    const std::uint64_t timeout_seconds =
        timeout_from_options(options, route_kind);
    const std::uint64_t cycle_runtime_seconds =
        maximum_runtime_from_options(options, timeout_seconds);
    const std::uint64_t max_round_trips = option_uint64_or(
        options, "max-round-trips",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxRoundTrips);
    const std::uint64_t inbound_timeout_seconds = option_uint64_or(
        options, "inbound-timeout-seconds", timeout_seconds);
    const std::uint64_t inbound_max_round_trips = option_uint64_or(
        options, "inbound-max-round-trips", max_round_trips);
    const std::uint64_t ingress_timeout_fallback =
        ingress_kind == anonsync::SyncReplicaPeerIngressKind::I2pSamAccept
        ? kDefaultI2pTimeoutSeconds
        : timeout_seconds;
    const std::uint64_t ingress_timeout_seconds = option_uint64_or(
        options, "ingress-timeout-seconds", ingress_timeout_fallback);
    if (ingress_timeout_seconds == 0U ||
        ingress_timeout_seconds > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            "--ingress-timeout-seconds must be in [1, 3600]");
    }
    if (ingress_kind ==
            anonsync::SyncReplicaPeerIngressKind::I2pSamAccept &&
        ingress_timeout_seconds < kMinimumI2pTimeoutSeconds) {
        throw std::invalid_argument(
            "--ingress-timeout-seconds must be at least 180 for "
            "--ingress i2p");
    }
    const auto seconds_to_milliseconds = [&](std::string_view key,
                                             std::uint64_t fallback) {
        const std::uint64_t value = option_uint64_or(options, key, fallback);
        if (value == 0U || value > 3600U) {
            throw std::invalid_argument(
                "--" + std::string(key) + " must be in [1, 3600]");
        }
        return value * 1000U;
    };

    anonsync::SyncReplicaPeerServiceLimits limits;
    limits.folder_limits =
        folder_limits_from_options_or_throw(options, deployment);
    limits.max_round_trips = max_round_trips;
    limits.max_source_resets = option_uint64_or(
        options, "max-source-resets",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxSourceResets);
    limits.stage_timeout_seconds = timeout_seconds;
    limits.cycle_runtime_seconds = cycle_runtime_seconds;
    limits.inbound_stage_timeout_seconds = inbound_timeout_seconds;
    limits.inbound_max_round_trips = inbound_max_round_trips;
    limits.accept_window_milliseconds = option_uint64_or(
        options, "accept-poll-milliseconds", 250U);
    limits.repair_interval_milliseconds = seconds_to_milliseconds(
        "scan-interval-seconds", 30U);
    limits.retry_initial_milliseconds = seconds_to_milliseconds(
        "retry-initial-seconds", 1U);
    limits.retry_maximum_milliseconds = seconds_to_milliseconds(
        "retry-maximum-seconds", 60U);
    limits.ingress_setup_timeout_seconds = ingress_timeout_seconds;
    anonsync::validate_sync_replica_peer_service_limits_or_throw(
        limits, "anonsync_sync peer service limits");
    return limits;
}

[[nodiscard]] fs::path required_environment_directory_or_throw(
    const char* variable) {
    const char* const value = std::getenv(variable);
    if (value == nullptr || *value == '\0') {
        throw std::invalid_argument(
            std::string(variable) + " is not set for a linked-peer operation");
    }
    return require_absolute_path(value, variable);
}

struct ProvisioningIngressSelection final {
    anonsync::SyncReplicaPeerIngress ingress;
    anonsync::SyncReplicaNumericStreamEndpoint listen_endpoint;
    std::optional<fs::path> i2p_private_destination_file;
};

void reject_ingress_options_or_throw(
    const Options& options,
    std::initializer_list<std::string_view> rejected,
    std::string_view selected_ingress) {
    for (const std::string_view key : rejected) {
        if (options.has(key)) {
            throw std::invalid_argument(
                "--" + std::string(key) +
                " is not valid with --ingress " +
                std::string(selected_ingress));
        }
    }
}

[[nodiscard]] ProvisioningIngressSelection
provisioning_ingress_from_options_or_throw(
    const Options& options,
    std::optional<std::string_view> stable_default_scope = std::nullopt) {
    const std::string selected = options.one_or("ingress", "direct");
    ProvisioningIngressSelection result;
    if (selected == "direct") {
        reject_ingress_options_or_throw(
            options,
            {"ingress-onion-address", "ingress-onion-port",
             "ingress-i2p-sam-address", "ingress-i2p-sam-port",
             "ingress-i2p-session-id",
             "ingress-i2p-private-destination-file",
             "ingress-i2p-inbound-quantity",
             "ingress-i2p-outbound-quantity"},
            selected);
        result.ingress = anonsync::SyncReplicaDirectTcpIngress{};
        result.listen_endpoint = {
            options.one_or("bind-address", "127.0.0.1"),
            parse_port(options.one("listen-port"), "--listen-port")};
    } else if (selected == "tor") {
        reject_ingress_options_or_throw(
            options,
            {"ingress-i2p-sam-address", "ingress-i2p-sam-port",
             "ingress-i2p-session-id",
             "ingress-i2p-private-destination-file",
             "ingress-i2p-inbound-quantity",
             "ingress-i2p-outbound-quantity"},
            selected);
        result.ingress = anonsync::SyncReplicaTorOnionServiceIngress{
            .onion_service = options.one("ingress-onion-address"),
            .service_port = parse_port(
                options.one("ingress-onion-port"),
                "--ingress-onion-port")};
        result.listen_endpoint = {
            options.one_or("bind-address", "127.0.0.1"),
            parse_port(options.one("listen-port"), "--listen-port")};
    } else if (selected == "i2p") {
        reject_ingress_options_or_throw(
            options,
            {"bind-address", "listen-port", "ingress-onion-address",
             "ingress-onion-port"},
            selected);
        const fs::path destination_path = require_absolute_path(
            options.one("ingress-i2p-private-destination-file"),
            "--ingress-i2p-private-destination-file");
        const std::string destination =
            read_i2p_private_destination_file_or_throw(
                destination_path,
                "--ingress-i2p-private-destination-file");
        result.ingress = anonsync::SyncReplicaI2pSamIngress{
            .bridge = {
                options.one_or("ingress-i2p-sam-address", "127.0.0.1"),
                parse_port(
                    options.one_or("ingress-i2p-sam-port", "7656"),
                    "--ingress-i2p-sam-port")},
            .session_id = options.has("ingress-i2p-session-id")
                ? options.one("ingress-i2p-session-id")
                : stable_default_scope.has_value()
                    ? stable_service_default_token_or_throw(
                          "i2p-inbound-session", *stable_default_scope,
                          "anonsync-ingress-")
                    : "anonsync-ingress-" + random_hex_token_or_throw(
                          16U, "anonsync_sync I2P ingress SAM session"),
            .session_destination = destination,
            .inbound_quantity = i2p_tunnel_quantity_from_options(
                options, "ingress-i2p-inbound-quantity"),
            .outbound_quantity = i2p_tunnel_quantity_from_options(
                options, "ingress-i2p-outbound-quantity")};
        // Schema v2 retains a numeric listen field, but native STREAM ACCEPT
        // never binds or forwards through it. Keep one valid inert value so the
        // compatibility field cannot accidentally expose another ingress path.
        result.listen_endpoint = {"127.0.0.1", 1U};
        result.i2p_private_destination_file = destination_path;
    } else {
        throw std::invalid_argument(
            "--ingress must be one of direct, tor, or i2p");
    }
    anonsync::validate_sync_replica_peer_ingress_or_throw(
        result.ingress, result.listen_endpoint,
        "anonsync_sync provision ingress");
    return result;
}

volatile std::sig_atomic_t g_peer_service_stop_requested = 0;

void peer_service_stop_signal_handler(int) noexcept {
    g_peer_service_stop_requested = 1;
}

class PeerServiceSignalOwner final {
public:
    PeerServiceSignalOwner() {
        struct sigaction action {};
        action.sa_handler = peer_service_stop_signal_handler;
        if (::sigemptyset(&action.sa_mask) != 0) {
            throw std::runtime_error(
                "anonsync_sync could not initialize signal mask");
        }
        action.sa_flags = SA_RESTART;
        if (::sigaction(SIGINT, &action, &old_interrupt_) != 0) {
            throw std::runtime_error(
                "anonsync_sync could not install SIGINT handler");
        }
        interrupt_installed_ = true;
        if (::sigaction(SIGTERM, &action, &old_terminate_) != 0) {
            (void)::sigaction(SIGINT, &old_interrupt_, nullptr);
            interrupt_installed_ = false;
            throw std::runtime_error(
                "anonsync_sync could not install SIGTERM handler");
        }
        terminate_installed_ = true;
    }

    PeerServiceSignalOwner(const PeerServiceSignalOwner&) = delete;
    PeerServiceSignalOwner& operator=(const PeerServiceSignalOwner&) = delete;

    ~PeerServiceSignalOwner() noexcept {
        if (terminate_installed_) {
            (void)::sigaction(SIGTERM, &old_terminate_, nullptr);
        }
        if (interrupt_installed_) {
            (void)::sigaction(SIGINT, &old_interrupt_, nullptr);
        }
    }

private:
    struct sigaction old_interrupt_ {};
    struct sigaction old_terminate_ {};
    bool interrupt_installed_ = false;
    bool terminate_installed_ = false;
};

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

[[nodiscard]] const char* pull_disposition_name(
    anonsync::SyncReplicaReconciliationTlsPullDisposition disposition)
    noexcept {
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

void append_cutpoint_json(
    std::ostream& output,
    std::string_view name,
    const anonsync::SyncReplicaSyncOnceCutpoint& cutpoint) {
    output << ",\"" << name << "\":{"
           << "\"catalog_generation\":" << cutpoint.catalog_generation
           << ",\"catalog_entries\":" << cutpoint.catalog_entries
           << ",\"catalog_digest\":"
           << json_quote(cutpoint.catalog_digest)
           << ",\"local_scan_epoch\":" << cutpoint.local_scan_epoch
           << ",\"local_scan_seen_path_count\":"
           << cutpoint.local_scan_seen_path_count
           << ",\"local_scan_seen_path_bytes\":"
           << cutpoint.local_scan_seen_path_bytes
           << ",\"local_scan_resume_after_path\":"
           << json_quote(cutpoint.local_scan_resume_after_path)
           << ",\"local_scan_seen_chain_digest\":"
           << json_quote(cutpoint.local_scan_seen_chain_digest)
           << ",\"remote_apply_resume_after_path\":"
           << json_quote(cutpoint.remote_apply_resume_after_path)
           << ",\"remote_inspection_sweep_basis_digest\":"
           << json_quote(cutpoint.remote_inspection_sweep_basis_digest)
           << ",\"remote_inspection_sweep_started_after_path\":"
           << json_quote(
                  cutpoint.remote_inspection_sweep_started_after_path)
           << ",\"remote_inspection_sweep_seen_path_count\":"
           << cutpoint.remote_inspection_sweep_seen_path_count
           << ",\"remote_inspection_sweep_had_unresolved_paths\":"
           << json_bool(
                  cutpoint.remote_inspection_sweep_had_unresolved_paths)
           << ",\"replica_generation\":" << cutpoint.replica_generation
           << ",\"replica_cutpoint_digest\":"
           << json_quote(cutpoint.replica_cutpoint_digest)
           << ",\"replica_evidence_set_digest\":"
           << json_quote(cutpoint.replica_evidence_set_digest)
           << ",\"replica_visible_state_digest\":"
           << json_quote(cutpoint.replica_visible_state_digest)
           << '}';
}

void append_pass_json(
    std::ostream& output,
    std::string_view name,
    const std::optional<anonsync::SyncReplicaFolderConvergencePassReport>&
        report) {
    output << ",\"" << name << "\":";
    if (!report.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"visited_entries\":"
        << report->traversal.visited_entry_count
        << ",\"visited_directories\":"
        << report->traversal.visited_directory_count
        << ",\"regular_files\":"
        << report->traversal.regular_file_count
        << ",\"ignored_symbolic_links\":"
        << report->traversal.ignored_symbolic_link_count
        << ",\"ignored_special_files\":"
        << report->traversal.ignored_special_file_count
        << ",\"ignored_internal_artifacts\":"
        << report->traversal.ignored_internal_artifact_count
        << ",\"metadata_only_regular_files\":"
        << report->traversal.metadata_only_regular_file_count
        << ",\"metadata_only_regular_file_logical_bytes\":"
        << report->traversal.metadata_only_regular_file_logical_bytes
        << ",\"metadata_only_pruned_directories\":"
        << report->traversal.metadata_only_pruned_directory_count
        << ",\"classified_regular_file_bytes\":"
        << report->traversal.classified_regular_file_bytes
        << ",\"local_scan_epoch\":" << report->local_scan_epoch
        << ",\"completed_local_scan_epoch\":"
        << json_bool(report->completed_local_scan_epoch)
        << ",\"restarted_local_scan_epoch\":"
        << json_bool(report->restarted_local_scan_epoch)
        << ",\"local_scan_seen_path_count\":"
        << report->local_scan_seen_path_count
        << ",\"local_scan_resume_after_path\":"
        << json_quote(report->local_scan_resume_after_path)
        << ",\"local_scan_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_traversal_stop_reason_name(
                   report->local_scan_stop_reason))
        << ",\"local_directory_enumeration_passes\":"
        << report->local_directory_enumeration_pass_count
        << ",\"local_peak_buffered_directory_component_batch_count\":"
        << report->local_peak_buffered_directory_component_batch_count
        << ",\"local_peak_simultaneously_buffered_directory_component_count\":"
        << report->local_peak_simultaneously_buffered_directory_component_count
        << ",\"used_idle_fast_path\":"
        << (report->used_idle_fast_path ? "true" : "false")
        << ",\"payload_snapshot_handoffs\":"
        << report->payload_snapshot_handoff_count
        << ",\"payload_snapshot_handoff_entries\":"
        << report->payload_snapshot_handoff_entry_count
        << ",\"payload_snapshot_observations\":"
        << report->payload_snapshot_observation_count
        << ",\"payload_snapshot_observed_entries\":"
        << report->payload_snapshot_observed_entry_count
        << ",\"exact_local_file_bytes\":"
        << report->exact_local_file_bytes
        << ",\"exact_remote_file_bytes\":"
        << report->exact_remote_file_bytes
        << ",\"payload_mutation_batches\":"
        << report->payload_mutation_batch_count
        << ",\"payload_mutation_full_scans\":"
        << report->payload_mutation_full_scan_count
        << ",\"payload_mutation_scan_hashed_entries\":"
        << report->payload_mutation_scan_hashed_entry_count
        << ",\"payload_mutation_scan_hashed_bytes\":"
        << report->payload_mutation_scan_hashed_bytes
        << ",\"payload_mutation_scan_reused_entries\":"
        << report->payload_mutation_scan_reused_entry_count
        << ",\"payload_mutation_scan_reused_bytes\":"
        << report->payload_mutation_scan_reused_bytes
        << ",\"payload_mutation_scan_process_reused_entries\":"
        << report->payload_mutation_scan_process_reused_entry_count
        << ",\"payload_mutation_scan_process_reused_bytes\":"
        << report->payload_mutation_scan_process_reused_bytes
        << ",\"payload_mutation_scan_durable_reused_entries\":"
        << report->payload_mutation_scan_durable_reused_entry_count
        << ",\"payload_mutation_scan_durable_reused_bytes\":"
        << report->payload_mutation_scan_durable_reused_bytes
        << ",\"payload_mutation_puts\":"
        << report->payload_mutation_put_count
        << ",\"payload_mutation_source_bytes\":"
        << report->payload_mutation_source_bytes
        << ",\"payload_mutation_work_bytes\":"
        << report->payload_mutation_work_bytes
        << ",\"payload_mutation_peak_batch_puts\":"
        << report->payload_mutation_peak_batch_put_count
        << ",\"payload_mutation_peak_batch_work_bytes\":"
        << report->payload_mutation_peak_batch_work_bytes
        << ",\"payload_mutation_inserted\":"
        << report->payload_mutation_inserted_count
        << ",\"payload_mutation_already_present\":"
        << report->payload_mutation_already_present_count
        << ",\"local_published\":" << report->local_published_count
        << ",\"local_identity_preserving_renames\":"
        << report->local_identity_preserving_rename_count
        << ",\"local_adopted_visible\":"
        << report->local_adopted_visible_count
        << ",\"local_catalog_no_op\":"
        << report->local_catalog_no_op_count
        << ",\"local_catalog_refreshed\":"
        << report->local_catalog_refreshed_count
        << ",\"remote_applied\":" << report->remote_applied_count
        << ",\"remote_adopted_exact\":"
        << report->remote_adopted_exact_count
        << ",\"remote_catalog_no_op\":"
        << report->remote_catalog_no_op_count
        << ",\"remote_apply_operations\":"
        << report->remote_apply_operation_count
        << ",\"remote_metadata_only_files\":"
        << report->remote_metadata_only_file_count
        << ",\"remote_metadata_only_already_absent_files\":"
        << report->remote_metadata_only_already_absent_file_count
        << ",\"remote_targeted_catalog_path_cutpoints\":"
        << report->remote_targeted_catalog_path_cutpoint_count
        << ",\"remote_targeted_replica_path_cutpoints\":"
        << report->remote_targeted_replica_path_cutpoint_count
        << ",\"remote_metadata_only_dematerialization_attempts\":"
        << report->remote_metadata_only_dematerialization_attempt_count
        << ",\"remote_metadata_only_dematerialized_files\":"
        << report->remote_metadata_only_dematerialized_file_count
        << ",\"remote_metadata_only_dematerialized_bytes\":"
        << report->remote_metadata_only_dematerialized_bytes
        << ",\"remote_metadata_only_dematerialization_blocked_files\":"
        << report->remote_metadata_only_dematerialization_blocked_file_count
        << ",\"remote_metadata_only_dematerialization_payload_unavailable\":"
        << report->remote_metadata_only_dematerialization_payload_unavailable_count
        << ",\"local_metadata_only_absence_suppressions\":"
        << report->local_metadata_only_absence_suppressed_count
        << ",\"local_selection_change_absence_suppressions\":"
        << report->local_selection_change_absence_suppressed_count
        << ",\"remote_inspected_paths\":"
        << report->remote_inspected_path_count
        << ",\"remote_acknowledged_paths\":"
        << report->remote_acknowledged_path_count
        << ",\"deferred_remote_inspection_paths\":"
        << report->deferred_remote_inspection_path_count
        << ",\"remote_inspection_sweep_started_after_path\":"
        << json_quote(
               report->remote_inspection_sweep_started_after_path)
        << ",\"remote_inspection_sweep_seen_path_count\":"
        << report->remote_inspection_sweep_seen_path_count
        << ",\"completed_remote_inspection_sweep\":"
        << json_bool(report->completed_remote_inspection_sweep)
        << ",\"remote_inspection_sweep_had_unresolved_paths\":"
        << json_bool(
               report->remote_inspection_sweep_had_unresolved_paths)
        << ",\"remote_inspection_terminal_cutpoint_reproved\":"
        << json_bool(
               report->remote_inspection_terminal_cutpoint_reproved)
        << ",\"remote_inspection_terminal_catalog_digest\":"
        << json_quote(
               report->remote_inspection_terminal_catalog_digest)
        << ",\"remote_inspection_terminal_visible_state_digest\":"
        << json_quote(
               report->remote_inspection_terminal_visible_state_digest)
        << ",\"remote_payload_snapshot_observations\":"
        << report->remote_payload_snapshot_observation_count
        << ",\"remote_payload_snapshot_entries\":"
        << report->remote_payload_snapshot_entry_count
        << ",\"remote_targeted_payload_accesses\":"
        << report->remote_targeted_payload_access_count
        << ",\"remote_targeted_payload_probes\":"
        << report->remote_targeted_payload_probe_count
        << ",\"remote_targeted_payload_selections\":"
        << report->remote_targeted_payload_selection_count
        << ",\"remote_targeted_payload_selected_bytes\":"
        << report->remote_targeted_payload_selected_bytes
        << ",\"deferred_remote_payload_candidates\":"
        << report->deferred_remote_payload_candidate_count
        << ",\"remote_apply_revalidated_catalog_predecessors\":"
        << report
               ->remote_apply_revalidated_catalog_predecessor_count
        << ",\"remote_apply_started_after_path\":"
        << json_quote(report->remote_apply_started_after_path)
        << ",\"remote_apply_resume_after_path\":"
        << json_quote(report->remote_apply_resume_after_path)
        << ",\"remote_apply_wrapped_projection\":"
        << json_bool(report->remote_apply_wrapped_projection)
        << ",\"deferred_remote_apply_candidates\":"
        << report->deferred_remote_apply_candidate_count
        << ",\"remote_apply_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_remote_apply_stop_reason_name(
                   report->remote_apply_stop_reason))
        << ",\"skipped_conflicted_remote_paths\":"
        << report->skipped_conflicted_remote_path_count
        << ",\"skipped_tombstone_remote_paths\":"
        << report->skipped_tombstone_remote_path_count
        << ",\"deferred_unadjudicated_local_absence_remote_files\":"
        << report->deferred_unadjudicated_local_absence_remote_file_count << '}';
}

void append_reconciliation_json(
    std::ostream& output,
    const std::optional<
        anonsync::SyncReplicaReconciliationTlsClientResult>& result) {
    output << ",\"reconciliation\":";
    if (!result.has_value()) {
        output << "null";
        return;
    }
    const auto& route = result->stream_connect;
    output
        << "{\"client_disposition\":"
        << json_quote(
               anonsync::sync_replica_reconciliation_tls_client_disposition_name(
                   result->disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(
               anonsync::sync_replica_file_tls_client_shutdown_disposition_name(
                   result->shutdown_disposition))
        << ",\"connected\":" << json_bool(result->connected)
        << ",\"handshake_complete\":"
        << json_bool(result->handshake_complete)
        << ",\"peer_authenticated\":"
        << json_bool(result->peer_authenticated)
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
        << ",\"route_bytes_written\":" << route.route_bytes_written
        << ",\"route_bytes_received\":" << route.route_bytes_received
        << ",\"connect_attempts\":" << result->connect_attempts
        << ",\"handshake_attempts\":" << result->handshake_attempts;
    if (result->peer_spki_sha256.has_value()) {
        output << ",\"peer_spki_sha256\":"
               << json_quote(*result->peer_spki_sha256);
    }
    if (result->peer_actor.has_value()) {
        output << ",\"peer_device_id\":"
               << json_quote(result->peer_actor->device_id)
               << ",\"peer_epoch\":" << result->peer_actor->epoch;
    }
    if (result->connect_error.has_value()) {
        output << ",\"connect_error\":" << *result->connect_error;
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
    output << ",\"pull\":";
    if (!result->pull.has_value()) {
        output << "null";
    } else {
        const auto& pull = *result->pull;
        output
            << "{\"disposition\":"
            << json_quote(pull_disposition_name(pull.disposition))
            << ",\"round_trips\":" << pull.round_trips
            << ",\"pages_applied\":" << pull.pages_applied
            << ",\"source_resets\":" << pull.source_resets
            << ",\"source_payload_preparing_responses\":"
            << pull.source_payload_preparing_responses
            << ",\"inserted_active\":" << pull.inserted_active
            << ",\"inserted_pending\":" << pull.inserted_pending
            << ",\"inserted_quarantined\":"
            << pull.inserted_quarantined
            << ",\"duplicate_operations\":"
            << pull.duplicate_operations
            << ",\"metadata_only_file_operations\":"
            << pull.metadata_only_file_operations
            << ",\"inserted_payloads\":" << pull.inserted_payloads
            << ",\"existing_payloads\":" << pull.existing_payloads
            << ",\"staged_payload_ranges\":"
            << pull.staged_payload_ranges
            << ",\"staged_payload_bytes\":"
            << pull.staged_payload_bytes
            << ",\"terminal_verification_steps\":"
            << pull.terminal_verification_steps
            << ",\"terminal_verification_local_continuation_steps\":"
            << pull.terminal_verification_local_continuation_steps
            << ",\"terminal_verification_step_budget_exhaustions\":"
            << pull.terminal_verification_step_budget_exhaustions
            << ",\"reused_payload_chunks\":"
            << pull.reused_payload_chunks
            << ",\"reused_payload_ranges\":"
            << pull.reused_payload_ranges
            << ",\"reused_payload_bytes\":"
            << pull.reused_payload_bytes
            << ",\"delta_local_reuse_read_ranges\":"
            << pull.delta_local_reuse_read_ranges
            << ",\"delta_local_reuse_read_bytes\":"
            << pull.delta_local_reuse_read_bytes
            << ",\"delta_local_reuse_maximum_read_range_bytes\":"
            << pull.delta_local_reuse_maximum_read_range_bytes
            << ",\"delta_local_reuse_budget_exhaustions\":"
            << pull.delta_local_reuse_budget_exhaustions
            << ",\"delta_local_reuse_interior_resumptions\":"
            << pull.delta_local_reuse_interior_resumptions
            << ",\"delta_wire_already_durable_ranges\":"
            << pull.delta_wire_already_durable_ranges
            << ",\"delta_wire_already_durable_bytes\":"
            << pull.delta_wire_already_durable_bytes
            << ",\"delta_wire_overlap_trimmed_ranges\":"
            << pull.delta_wire_overlap_trimmed_ranges
            << ",\"delta_predecessor_manifest_scans\":"
            << pull.delta_predecessor_manifest_scans
            << ",\"delta_predecessor_manifest_reuses\":"
            << pull.delta_predecessor_manifest_reuses
            << ",\"delta_predecessor_manifest_hashed_bytes\":"
            << pull.delta_predecessor_manifest_hashed_bytes
            << ",\"target_content_defined_manifest_publications\":"
            << pull.target_content_defined_manifest_publications
            << ",\"target_content_defined_manifest_reuses\":"
            << pull.target_content_defined_manifest_reuses
            << ",\"delta_predecessor_index_builds\":"
            << pull.delta_predecessor_index_builds
            << ",\"delta_predecessor_index_reuses\":"
            << pull.delta_predecessor_index_reuses
            << ",\"delta_cross_file_candidate_pages\":"
            << pull.delta_cross_file_candidate_pages
            << ",\"delta_cross_file_candidate_paths_scanned\":"
            << pull.delta_cross_file_candidate_paths_scanned
            << ",\"delta_cross_file_unavailable_candidates\":"
            << pull.delta_cross_file_unavailable_candidates
            << ",\"delta_cross_file_availability_generation_restarts\":"
            << pull.delta_cross_file_availability_generation_restarts
            << ",\"delta_cross_file_manifest_scan_steps\":"
            << pull.delta_cross_file_manifest_scan_steps
            << ",\"delta_cross_file_manifest_scans\":"
            << pull.delta_cross_file_manifest_scans
            << ",\"delta_cross_file_manifest_reuses\":"
            << pull.delta_cross_file_manifest_reuses
            << ",\"delta_cross_file_manifest_hashed_bytes\":"
            << pull.delta_cross_file_manifest_hashed_bytes
            << ",\"delta_cross_file_candidate_matches\":"
            << pull.delta_cross_file_candidate_matches
            << ",\"delta_cross_file_index_builds\":"
            << pull.delta_cross_file_index_builds
            << ",\"delta_cross_file_index_reuses\":"
            << pull.delta_cross_file_index_reuses
            << ",\"request_frame_bytes_written\":"
            << pull.request_frame_bytes_written
            << ",\"response_frame_bytes_received\":"
            << pull.response_frame_bytes_received
            << ",\"source_state_generation\":"
            << pull.source_state_generation
            << ",\"source_evidence_count\":"
            << pull.source_evidence_count
            << ",\"source_evidence_set_digest\":"
            << json_quote(pull.source_evidence_set_digest)
            << ",\"has_more\":" << json_bool(pull.has_more);
        if (pull.next_after_operation_id.has_value()) {
            output << ",\"next_after_operation_id\":"
                   << json_quote(*pull.next_after_operation_id);
        }
        if (pull.blocked_operation_id.has_value()) {
            output << ",\"blocked_operation_id\":"
                   << json_quote(*pull.blocked_operation_id);
        }
        if (pull.payload_continuation.has_value()) {
            output
                << ",\"payload_operation_id\":"
                << json_quote(pull.payload_continuation->operation_id)
                << ",\"payload_content_sha256\":"
                << json_quote(pull.payload_continuation->content_sha256)
                << ",\"payload_total_size_bytes\":"
                << pull.payload_continuation->total_size_bytes
                << ",\"payload_next_offset_bytes\":"
                << pull.payload_continuation->next_offset_bytes;
        }
        output << '}';
    }
    output << '}';
}

[[nodiscard]] const char* terminal_class(
    anonsync::SyncReplicaSyncOnceDisposition disposition) noexcept {
    if (anonsync::sync_replica_sync_once_is_complete(disposition)) {
        return "completed";
    }
    if (anonsync::sync_replica_sync_once_is_bounded_progress(disposition)) {
        return "partial";
    }
    return "stopped";
}

inline constexpr std::string_view kDatabaseRecoveryExpectationPrefix =
    "v1:";

struct DatabaseRecoveryExpectation final {
    std::string database_incarnation_sha256;
    std::uint64_t database_recovery_epoch = 0U;
    std::string cutpoint_digest;
};

[[nodiscard]] std::string encode_database_recovery_expectation_or_throw(
    std::string_view database_incarnation_sha256,
    std::uint64_t database_recovery_epoch,
    std::string_view cutpoint_digest) {
    if (!anonsync::is_lowercase_sha256_hex(database_incarnation_sha256) ||
        database_recovery_epoch == 0U ||
        !anonsync::is_lowercase_sha256_hex(cutpoint_digest)) {
        throw std::invalid_argument(
            "database recovery expectation fields are invalid");
    }
    std::string encoded(kDatabaseRecoveryExpectationPrefix);
    encoded.reserve(
        kDatabaseRecoveryExpectationPrefix.size() + 64U + 1U + 20U + 1U +
        64U);
    encoded.append(database_incarnation_sha256);
    encoded.push_back(':');
    encoded += std::to_string(database_recovery_epoch);
    encoded.push_back(':');
    encoded.append(cutpoint_digest);
    return encoded;
}

[[nodiscard]] DatabaseRecoveryExpectation
decode_database_recovery_expectation_or_throw(std::string_view encoded) {
    if (!encoded.starts_with(kDatabaseRecoveryExpectationPrefix)) {
        throw std::invalid_argument(
            "--expected must use v1:INCARNATION:EPOCH:CUTPOINT");
    }
    encoded.remove_prefix(kDatabaseRecoveryExpectationPrefix.size());
    const std::size_t first = encoded.find(':');
    if (first == std::string_view::npos) {
        throw std::invalid_argument(
            "--expected must use v1:INCARNATION:EPOCH:CUTPOINT");
    }
    const std::size_t second = encoded.find(':', first + 1U);
    if (second == std::string_view::npos ||
        encoded.find(':', second + 1U) != std::string_view::npos) {
        throw std::invalid_argument(
            "--expected must use v1:INCARNATION:EPOCH:CUTPOINT");
    }

    const std::string_view epoch_text = encoded.substr(
        first + 1U, second - first - 1U);
    DatabaseRecoveryExpectation result{
        std::string(encoded.substr(0U, first)),
        parse_uint64(epoch_text, "--expected recovery epoch"),
        std::string(encoded.substr(second + 1U)),
    };
    if (!anonsync::is_lowercase_sha256_hex(
            result.database_incarnation_sha256) ||
        result.database_recovery_epoch == 0U ||
        std::to_string(result.database_recovery_epoch) != epoch_text ||
        !anonsync::is_lowercase_sha256_hex(result.cutpoint_digest)) {
        throw std::invalid_argument(
            "--expected must use canonical v1:INCARNATION:EPOCH:CUTPOINT");
    }
    return result;
}

// Database recovery is deliberately offline and share-scoped. One ceremony
// owner claims the deployment singleton before any database family is opened.
// Its forensic observation opens only a descriptor-rooted read-only connection
// and cannot initialize or migrate an older image. Advance first performs that
// same side-effect-free observation and rejects a stale token before opening a
// writable connection; the subsequent BEGIN IMMEDIATE transition independently
// re-proves the token so the preflight never becomes mutation authority.
class OfflineReplicaDatabaseRecoveryCeremonyOwner final {
public:
    OfflineReplicaDatabaseRecoveryCeremonyOwner(
        anonsync::SyncReplicaDeploymentManifest deployment,
        std::string label)
        : deployment_(std::move(deployment)),
          singleton_(deployment_, label + " deployment singleton"),
          label_(std::move(label)) {}

    [[nodiscard]] const anonsync::SyncReplicaDeploymentManifest& deployment()
        const noexcept {
        return deployment_;
    }

    [[nodiscard]] anonsync::SyncReplicaSqliteSnapshot snapshot_or_throw() {
        return forensic_snapshot_or_throw("forensic inspection");
    }

    [[nodiscard]] anonsync::SyncReplicaSqliteDatabaseRecoveryEpochResult
    advance_or_throw(const DatabaseRecoveryExpectation& expectation) {
        const anonsync::SyncReplicaSqliteSnapshot observed =
            forensic_snapshot_or_throw("advance preflight");
        if (observed.database_incarnation_sha256 !=
                expectation.database_incarnation_sha256 ||
            observed.database_recovery_epoch !=
                expectation.database_recovery_epoch ||
            observed.cutpoint_digest != expectation.cutpoint_digest) {
            throw std::runtime_error(
                label_ + " database recovery expectation is stale");
        }

        // The read-only handle has closed before writable authority is opened.
        // A low-level process outside the deployment singleton could still race
        // this interval, so the SQLite owner repeats the exact comparison under
        // BEGIN IMMEDIATE before it publishes the epoch transition.
        anonsync::SyncReplicaOperationalDatabase database =
            anonsync::open_attested_sync_replica_primary_database_or_throw(
                deployment_, label_ + " writable primary replica");
        anonsync::SyncReplicaSqliteOwner replica_owner(
            database.handle(), deployment_.folder_id,
            deployment_.local_actor, anonsync::SyncReplicaSqliteOwnerLimits{},
            label_ + " replica owner");
        return replica_owner.advance_database_recovery_epoch_or_throw(
            expectation.database_incarnation_sha256,
            expectation.database_recovery_epoch,
            expectation.cutpoint_digest);
    }

private:
    [[nodiscard]] anonsync::SyncReplicaSqliteSnapshot
    forensic_snapshot_or_throw(std::string_view stage) {
        anonsync::SyncReplicaOperationalDatabase database =
            anonsync::
                open_attested_sync_replica_primary_database_read_only_or_throw(
                    deployment_, label_ + " " + std::string(stage) +
                                     " primary replica");
        return anonsync::
            inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
                database.handle(), deployment_.folder_id,
                deployment_.local_actor,
                label_ + " " + std::string(stage) + " snapshot");
    }

    // Declaration order is authority order: claim the deployment before any
    // selected SQLite family can be opened.
    anonsync::SyncReplicaDeploymentManifest deployment_;
    anonsync::SyncReplicaPeerServiceSingletonOwner singleton_;
    std::string label_;
};

void append_database_recovery_scope_json(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment) {
    output
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"replica_database\":"
        << json_quote(deployment.replica_db.generic_string())
        << ",\"offline_required\":true"
        << ",\"deployment_singleton_acquired\":true"
        << ",\"continuity_scope\":\"in_database_only\""
        << ",\"external_anti_rollback_authority\":false"
        << ",\"payload_store_observed\":false"
        << ",\"folder_catalog_observed\":false"
        << ",\"rooted_files_observed\":false"
        << ",\"network_started\":false";
}

[[nodiscard]] anonsync::SyncReplicaSqliteDeploymentRole
parse_database_backup_role_or_throw(std::string_view role) {
    using Role = anonsync::SyncReplicaSqliteDeploymentRole;
    if (role == "replica") return Role::Replica;
    if (role == "file-effect") return Role::FileEffect;
    if (role == "tls-membership") return Role::TlsMembership;
    if (role == "tls-membership-anchor") {
        return Role::TlsMembershipAnchor;
    }
    if (role == "folder-catalog") return Role::FolderCatalog;
    throw std::invalid_argument(
        "--role must be replica, file-effect, tls-membership, "
        "tls-membership-anchor, or folder-catalog");
}

void append_database_backup_scope_json(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const anonsync::SyncReplicaDatabaseBackupArtifactObservation& artifact) {
    const anonsync::SyncReplicaDatabaseBackupCutpoint& snapshot =
        artifact.source_cutpoint;
    output
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"replica_database\":"
        << json_quote(deployment.replica_db.generic_string())
        << ",\"snapshot_path\":"
        << json_quote(artifact.artifact_path.generic_string())
        << ",\"offline_required\":true"
        << ",\"deployment_singleton_acquired\":true"
        << ",\"continuity_scope\":\"single_replica_database_image\""
        << ",\"external_anti_rollback_authority\":false"
        << ",\"payload_store_observed\":false"
        << ",\"folder_catalog_observed\":false"
        << ",\"rooted_files_observed\":false"
        << ",\"network_started\":false"
        << ",\"payload_bytes_included\":false"
        << ",\"folder_catalog_included\":false"
        << ",\"membership_database_included\":false"
        << ",\"effect_database_included\":false"
        << ",\"anchor_database_included\":false"
        << ",\"snapshot_format\":\"anonsync.replica-database-backup.v1\""
        << ",\"snapshot_sha256\":" << json_quote(artifact.artifact_sha256)
        << ",\"snapshot_byte_count\":" << artifact.artifact_bytes
        << ",\"snapshot_page_size\":" << artifact.sqlite_page_size
        << ",\"snapshot_page_count\":" << artifact.sqlite_page_count
        << ",\"maximum_snapshot_bytes\":"
        << anonsync::kSyncReplicaDatabaseBackupMaximumArtifactBytes
        << ",\"maximum_snapshot_pages\":"
        << anonsync::kSyncReplicaDatabaseBackupMaximumArtifactPages
        << ",\"database_incarnation_sha256\":"
        << json_quote(snapshot.database_incarnation_sha256)
        << ",\"database_recovery_epoch\":"
        << snapshot.database_recovery_epoch
        << ",\"state_generation\":" << snapshot.state_generation
        << ",\"cutpoint_digest\":"
        << json_quote(snapshot.cutpoint_digest)
        << ",\"recovery_expectation\":"
        << json_quote(encode_database_recovery_expectation_or_throw(
               snapshot.database_incarnation_sha256,
               snapshot.database_recovery_epoch,
               snapshot.cutpoint_digest))
        << ",\"canonical_standalone_sqlite\":true"
        << ",\"single_file_sidecar_free\":true"
        << ",\"logical_sqlite_snapshot\":true"
        << ",\"current_schema_required\":true"
        << ",\"deployment_binding_attested\":true"
        << ",\"database_family_replacement_performed\":false"
        << ",\"restore_performed\":false"
        << ",\"recovery_epoch_advanced\":false"
        << ",\"post_replacement_recovery_advance_required\":true"
        << ",\"retention_age_reset_required_after_restore\":true";
}

void append_database_role_backup_scope_json(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const anonsync::SyncReplicaRoleDatabaseBackupArtifactObservation& artifact) {
    using Role = anonsync::SyncReplicaSqliteDeploymentRole;
    const auto& cutpoint = artifact.source_cutpoint;
    const Role role = cutpoint.database_role;
    const bool replica = role == Role::Replica;
    const bool file_effect = role == Role::FileEffect;
    const bool membership = role == Role::TlsMembership;
    const bool anchor = role == Role::TlsMembershipAnchor;
    const bool catalog = role == Role::FolderCatalog;
    output
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"database_role\":"
        << json_quote(
               anonsync::sync_replica_sqlite_deployment_role_name(role))
        << ",\"source_database\":"
        << json_quote(cutpoint.source_database_path.generic_string())
        << ",\"snapshot_path\":"
        << json_quote(artifact.artifact_path.generic_string())
        << ",\"offline_required\":true"
        << ",\"deployment_singleton_acquired\":true"
        << ",\"continuity_scope\":\"single_role_database_image\""
        << ",\"cross_database_atomicity\":false"
        << ",\"complete_share_backup\":false"
        << ",\"external_anti_rollback_authority\":false"
        << ",\"payload_store_observed\":false"
        << ",\"rooted_files_observed\":false"
        << ",\"network_started\":false"
        << ",\"payload_bytes_included\":false"
        << ",\"replica_database_included\":" << json_bool(replica)
        << ",\"effect_database_included\":" << json_bool(file_effect)
        << ",\"membership_database_included\":"
        << json_bool(membership)
        << ",\"anchor_database_included\":" << json_bool(anchor)
        << ",\"folder_catalog_included\":" << json_bool(catalog)
        << ",\"configuration_included\":false"
        << ",\"credentials_included\":false"
        << ",\"snapshot_format\":\"anonsync.role-bound-database-backup.v1\""
        << ",\"snapshot_sha256\":" << json_quote(artifact.artifact_sha256)
        << ",\"snapshot_byte_count\":" << artifact.artifact_bytes
        << ",\"snapshot_page_size\":" << artifact.sqlite_page_size
        << ",\"snapshot_page_count\":" << artifact.sqlite_page_count
        << ",\"maximum_snapshot_bytes\":"
        << anonsync::kSyncReplicaDatabaseBackupMaximumArtifactBytes
        << ",\"maximum_snapshot_pages\":"
        << anonsync::kSyncReplicaDatabaseBackupMaximumArtifactPages
        << ",\"role_state_generation\":" << cutpoint.state_generation
        << ",\"role_logical_record_count\":"
        << cutpoint.logical_record_count
        << ",\"role_state_digest\":"
        << json_quote(cutpoint.state_digest)
        << ",\"role_auxiliary_digest\":"
        << json_quote(cutpoint.auxiliary_digest)
        << ",\"canonical_standalone_sqlite\":true"
        << ",\"single_file_sidecar_free\":true"
        << ",\"logical_sqlite_snapshot\":true"
        << ",\"current_schema_required\":true"
        << ",\"deployment_binding_attested\":true"
        << ",\"restore_supported\":" << json_bool(replica)
        << ",\"inspection_only\":" << json_bool(!replica)
        << ",\"database_family_replacement_performed\":false"
        << ",\"restore_performed\":false"
        << ",\"recovery_epoch_advanced\":false";
    if (replica) {
        if (!cutpoint.replica_cutpoint.has_value()) {
            throw std::logic_error(
                "explicit replica backup observation lacks its replica cutpoint");
        }
        const auto& primary = *cutpoint.replica_cutpoint;
        output
            << ",\"database_incarnation_sha256\":"
            << json_quote(primary.database_incarnation_sha256)
            << ",\"database_recovery_epoch\":"
            << primary.database_recovery_epoch
            << ",\"cutpoint_digest\":"
            << json_quote(primary.cutpoint_digest)
            << ",\"recovery_expectation\":"
            << json_quote(encode_database_recovery_expectation_or_throw(
                   primary.database_incarnation_sha256,
                   primary.database_recovery_epoch,
                   primary.cutpoint_digest))
            << ",\"post_replacement_recovery_advance_required\":true"
            << ",\"retention_age_reset_required_after_restore\":true";
    } else {
        output
            << ",\"database_incarnation_sha256\":null"
            << ",\"database_recovery_epoch\":null"
            << ",\"cutpoint_digest\":null"
            << ",\"recovery_expectation\":null"
            << ",\"post_replacement_recovery_advance_required\":false"
            << ",\"retention_age_reset_required_after_restore\":false";
    }
}

int command_database_backup_create(const Options& options) {
    options.require_only({"manifest", "snapshot", "role"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const fs::path snapshot_path = require_absolute_path(
        options.one("snapshot"), "--snapshot");
    anonsync::SyncReplicaDatabaseBackupOwner owner(
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path,
            "anonsync_sync database-backup-create manifest"),
        "anonsync_sync database-backup-create");

    if (!options.has("role")) {
        const anonsync::SyncReplicaDatabaseBackupArtifactObservation artifact =
            owner.create_artifact_or_throw(snapshot_path);
        std::cout
            << "{\"command\":\"database-backup-create\""
            << ",\"terminal_class\":\"completed\""
            << ",\"response_schema\":"
            << json_quote(
                   "anonsync.local-database-backup-create.response.v1");
        append_database_backup_scope_json(
            std::cout, owner.deployment(), artifact);
        std::cout
            << ",\"active_database_observed\":true"
            << ",\"transactionally_pinned_source\":true"
            << ",\"source_cutpoint_bracketed\":true"
            << ",\"bounded_resident_copy\":true"
            << ",\"immutable_create_new\":true"
            << ",\"postpublication_reverified\":true"
            << ",\"artifact_published\":true"
            << ",\"source_database_mutation_performed\":false"
            << ",\"mutation_performed\":true}\n";
        return 0;
    }

    const anonsync::SyncReplicaSqliteDeploymentRole role =
        parse_database_backup_role_or_throw(options.one("role"));
    const anonsync::SyncReplicaRoleDatabaseBackupArtifactObservation artifact =
        owner.create_role_artifact_or_throw(role, snapshot_path);
    std::cout
        << "{\"command\":\"database-backup-create\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-database-backup-create.response.v2");
    append_database_role_backup_scope_json(
        std::cout, owner.deployment(), artifact);
    std::cout
        << ",\"active_database_observed\":true"
        << ",\"transactionally_pinned_source\":true"
        << ",\"source_cutpoint_bracketed\":true"
        << ",\"bounded_resident_copy\":true"
        << ",\"immutable_create_new\":true"
        << ",\"postpublication_reverified\":true"
        << ",\"artifact_published\":true"
        << ",\"source_database_mutation_performed\":false"
        << ",\"mutation_performed\":true}\n";
    return 0;
}

int command_database_backup_inspect(const Options& options) {
    options.require_only({"manifest", "snapshot", "role"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const fs::path snapshot_path = require_absolute_path(
        options.one("snapshot"), "--snapshot");
    anonsync::SyncReplicaDatabaseBackupOwner owner(
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path,
            "anonsync_sync database-backup-inspect manifest"),
        "anonsync_sync database-backup-inspect");

    if (!options.has("role")) {
        const anonsync::SyncReplicaDatabaseBackupArtifactObservation artifact =
            owner.inspect_artifact_or_throw(snapshot_path);
        std::cout
            << "{\"command\":\"database-backup-inspect\""
            << ",\"terminal_class\":\"completed\""
            << ",\"response_schema\":"
            << json_quote(
                   "anonsync.local-database-backup-inspection.response.v1");
        append_database_backup_scope_json(
            std::cout, owner.deployment(), artifact);
        std::cout
            << ",\"active_database_observed\":false"
            << ",\"transactionally_pinned_source\":false"
            << ",\"source_cutpoint_bracketed\":false"
            << ",\"bounded_resident_copy\":true"
            << ",\"immutable_create_new\":false"
            << ",\"postpublication_reverified\":true"
            << ",\"artifact_published\":false"
            << ",\"source_database_mutation_performed\":false"
            << ",\"mutation_performed\":false}\n";
        return 0;
    }

    const anonsync::SyncReplicaSqliteDeploymentRole role =
        parse_database_backup_role_or_throw(options.one("role"));
    const anonsync::SyncReplicaRoleDatabaseBackupArtifactObservation artifact =
        owner.inspect_role_artifact_or_throw(role, snapshot_path);
    std::cout
        << "{\"command\":\"database-backup-inspect\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-database-backup-inspection.response.v2");
    append_database_role_backup_scope_json(
        std::cout, owner.deployment(), artifact);
    std::cout
        << ",\"active_database_observed\":false"
        << ",\"transactionally_pinned_source\":false"
        << ",\"source_cutpoint_bracketed\":false"
        << ",\"bounded_resident_copy\":true"
        << ",\"immutable_create_new\":false"
        << ",\"postpublication_reverified\":true"
        << ",\"artifact_published\":false"
        << ",\"source_database_mutation_performed\":false"
        << ",\"mutation_performed\":false}\n";
    return 0;
}

int command_database_recovery_replace(const Options& options) {
    options.require_only(
        {"manifest", "snapshot", "rollback", "receipt", "expected-current"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const fs::path snapshot_path = require_absolute_path(
        options.one("snapshot"), "--snapshot");
    const fs::path rollback_path = require_absolute_path(
        options.one("rollback"), "--rollback");
    const fs::path receipt_path = require_absolute_path(
        options.one("receipt"), "--receipt");
    const DatabaseRecoveryExpectation expected =
        decode_database_recovery_expectation_or_throw(
            options.one("expected-current"));
    const std::string expected_encoded =
        encode_database_recovery_expectation_or_throw(
            expected.database_incarnation_sha256,
            expected.database_recovery_epoch,
            expected.cutpoint_digest);

    anonsync::SyncReplicaDatabaseReplacementOwner owner(
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path,
            "anonsync_sync database-recovery-replace manifest"),
        "anonsync_sync database-recovery-replace");
    const anonsync::SyncReplicaDatabaseReplacementResult result =
        owner.replace_or_resume_or_throw(
            snapshot_path, rollback_path, receipt_path,
            {
                expected.database_incarnation_sha256,
                expected.database_recovery_epoch,
                expected.cutpoint_digest,
            });
    const std::string final_expectation =
        encode_database_recovery_expectation_or_throw(
            result.final_cutpoint.database_incarnation_sha256,
            result.final_cutpoint.database_recovery_epoch,
            result.final_cutpoint.cutpoint_digest);
    const bool mutation_performed =
        result.receipt_created_this_invocation ||
        result.rollback_published_this_invocation ||
        result.database_replacement_performed_this_invocation ||
        result.recovery_epoch_advanced_this_invocation;

    std::cout
        << "{\"command\":\"database-recovery-replace\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-database-recovery-replacement.response.v3");
    append_database_recovery_scope_json(std::cout, owner.deployment());
    std::cout
        << ",\"candidate_snapshot_path\":"
        << json_quote(result.candidate_artifact.artifact_path.generic_string())
        << ",\"candidate_snapshot_sha256\":"
        << json_quote(result.candidate_artifact.artifact_sha256)
        << ",\"candidate_snapshot_byte_count\":"
        << result.candidate_artifact.artifact_bytes
        << ",\"candidate_snapshot_page_size\":"
        << result.candidate_artifact.sqlite_page_size
        << ",\"candidate_snapshot_page_count\":"
        << result.candidate_artifact.sqlite_page_count
        << ",\"rollback_snapshot_path\":"
        << json_quote(result.rollback_artifact.artifact_path.generic_string())
        << ",\"rollback_snapshot_sha256\":"
        << json_quote(result.rollback_artifact.artifact_sha256)
        << ",\"rollback_snapshot_byte_count\":"
        << result.rollback_artifact.artifact_bytes
        << ",\"rollback_snapshot_page_size\":"
        << result.rollback_artifact.sqlite_page_size
        << ",\"rollback_snapshot_page_count\":"
        << result.rollback_artifact.sqlite_page_count
        << ",\"replacement_receipt_path\":"
        << json_quote(result.receipt_path.generic_string())
        << ",\"replacement_receipt_action_sha256\":"
        << json_quote(result.receipt_action_sha256)
        << ",\"replacement_receipt_record_sha256\":"
        << json_quote(result.receipt_record_sha256)
        << ",\"replacement_entry_stage\":"
        << json_quote(
               anonsync::sync_replica_database_replacement_entry_stage_name(
                   result.entry_stage))
        << ",\"replacement_receipt_preexisting\":"
        << json_bool(result.receipt_preexisting)
        << ",\"replacement_receipt_created_this_invocation\":"
        << json_bool(result.receipt_created_this_invocation)
        << ",\"rollback_artifact_published_this_invocation\":"
        << json_bool(result.rollback_published_this_invocation)
        << ",\"logical_database_replacement_performed_this_invocation\":"
        << json_bool(result.database_replacement_performed_this_invocation)
        << ",\"recovery_epoch_advanced_this_invocation\":"
        << json_bool(result.recovery_epoch_advanced_this_invocation)
        << ",\"idempotent_reproof_only\":"
        << json_bool(result.idempotent_reproof_only)
        << ",\"expected_current_recovery_expectation\":"
        << json_quote(expected_encoded)
        << ",\"displaced_database_incarnation_sha256\":"
        << json_quote(result.displaced_cutpoint.database_incarnation_sha256)
        << ",\"displaced_database_recovery_epoch\":"
        << result.displaced_cutpoint.database_recovery_epoch
        << ",\"displaced_state_generation\":"
        << result.displaced_cutpoint.state_generation
        << ",\"displaced_cutpoint_digest\":"
        << json_quote(result.displaced_cutpoint.cutpoint_digest)
        << ",\"restored_database_incarnation_sha256\":"
        << json_quote(result.restored_cutpoint.database_incarnation_sha256)
        << ",\"restored_database_recovery_epoch\":"
        << result.restored_cutpoint.database_recovery_epoch
        << ",\"restored_state_generation\":"
        << result.restored_cutpoint.state_generation
        << ",\"restored_cutpoint_digest\":"
        << json_quote(result.restored_cutpoint.cutpoint_digest)
        << ",\"database_incarnation_sha256\":"
        << json_quote(result.final_cutpoint.database_incarnation_sha256)
        << ",\"previous_database_recovery_epoch\":"
        << result.restored_cutpoint.database_recovery_epoch
        << ",\"database_recovery_epoch\":"
        << result.final_cutpoint.database_recovery_epoch
        << ",\"state_generation\":"
        << result.final_cutpoint.state_generation
        << ",\"cutpoint_digest\":"
        << json_quote(result.final_cutpoint.cutpoint_digest)
        << ",\"recovery_expectation\":"
        << json_quote(final_expectation)
        << ",\"backup_step_calls\":" << result.backup_step_calls
        << ",\"maximum_reported_page_count\":"
        << result.maximum_reported_page_count
        << ",\"maximum_reported_remaining_pages\":"
        << result.maximum_reported_remaining_pages
        << ",\"candidate_validated_before_mutation\":true"
        << ",\"candidate_deployment_binding_attested\":true"
        << ",\"replacement_receipt_immutable\":true"
        << ",\"replacement_receipt_effect_authority\":false"
        << ",\"progress_classified_from_active_database\":true"
        << ",\"rollback_artifact_create_new\":true"
        << ",\"rollback_artifact_postpublication_reverified\":true"
        << ",\"rollback_represents_displaced_logical_database\":true"
        << ",\"raw_sqlite_family_byte_identity_preserved\":false"
        << ",\"descriptor_rooted_writable_destination\":true"
        << ",\"sqlite_destination_transaction\":true"
        << ",\"logical_database_replacement_complete\":true"
        << ",\"logical_database_replacement_performed\":"
        << json_bool(result.database_replacement_performed_this_invocation)
        << ",\"restored_cutpoint_reproved_before_advance\":true"
        << ",\"recovery_epoch_advanced\":"
        << json_bool(result.recovery_epoch_advanced_this_invocation)
        << ",\"recovery_epoch_advance_complete\":true"
        << ",\"final_database_reopened_and_reproved\":true"
        << ",\"final_candidate_artifact_path_reproved\":"
        << json_bool(result.final_candidate_path_reproved)
        << ",\"final_rollback_artifact_path_reproved\":"
        << json_bool(result.final_rollback_path_reproved)
        << ",\"final_artifact_reproof_bracketed_by_database_cutpoint\":true"
        << ",\"artifact_pathnames_continuously_reserved\":false"
        << ",\"noncooperating_same_uid_artifact_replacement_excluded\":false"
        << ",\"retention_age_reset_by_exact_source_change\":true"
        << ",\"payload_store_replacement_performed\":false"
        << ",\"other_database_replacement_performed\":false"
        << ",\"mutation_performed\":" << json_bool(mutation_performed)
        << "}\n";
    return 0;
}

int command_database_recovery_inspect(const Options& options) {
    options.require_only({"manifest"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    OfflineReplicaDatabaseRecoveryCeremonyOwner owner(
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path,
            "anonsync_sync database-recovery-inspect manifest"),
        "anonsync_sync database-recovery-inspect");
    const anonsync::SyncReplicaSqliteSnapshot snapshot =
        owner.snapshot_or_throw();
    const std::string expectation =
        encode_database_recovery_expectation_or_throw(
            snapshot.database_incarnation_sha256,
            snapshot.database_recovery_epoch,
            snapshot.cutpoint_digest);

    std::cout
        << "{\"command\":\"database-recovery-inspect\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-database-recovery-inspection.response.v1");
    append_database_recovery_scope_json(std::cout, owner.deployment());
    std::cout
        << ",\"database_incarnation_sha256\":"
        << json_quote(snapshot.database_incarnation_sha256)
        << ",\"database_recovery_epoch\":"
        << snapshot.database_recovery_epoch
        << ",\"state_generation\":" << snapshot.state_generation
        << ",\"cutpoint_digest\":"
        << json_quote(snapshot.cutpoint_digest)
        << ",\"recovery_expectation\":" << json_quote(expectation)
        << ",\"current_schema_required\":true"
        << ",\"operator_assertion_required_before_advance\":true"
        << ",\"mutation_performed\":false}\n";
    return 0;
}

int command_database_recovery_advance(const Options& options) {
    options.require_only({"manifest", "expected"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const DatabaseRecoveryExpectation expectation =
        decode_database_recovery_expectation_or_throw(
            options.one("expected"));
    const std::string previous_expectation =
        encode_database_recovery_expectation_or_throw(
            expectation.database_incarnation_sha256,
            expectation.database_recovery_epoch,
            expectation.cutpoint_digest);

    OfflineReplicaDatabaseRecoveryCeremonyOwner owner(
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path,
            "anonsync_sync database-recovery-advance manifest"),
        "anonsync_sync database-recovery-advance");
    const anonsync::SyncReplicaSqliteDatabaseRecoveryEpochResult result =
        owner.advance_or_throw(expectation);
    const std::string next_expectation =
        encode_database_recovery_expectation_or_throw(
            result.database_incarnation_sha256,
            result.database_recovery_epoch,
            result.cutpoint_digest);

    std::cout
        << "{\"command\":\"database-recovery-advance\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-database-recovery-advance.response.v1");
    append_database_recovery_scope_json(std::cout, owner.deployment());
    std::cout
        << ",\"database_incarnation_sha256\":"
        << json_quote(result.database_incarnation_sha256)
        << ",\"previous_database_recovery_epoch\":"
        << result.previous_database_recovery_epoch
        << ",\"database_recovery_epoch\":"
        << result.database_recovery_epoch
        << ",\"state_generation\":" << result.state_generation
        << ",\"previous_cutpoint_digest\":"
        << json_quote(expectation.cutpoint_digest)
        << ",\"cutpoint_digest\":"
        << json_quote(result.cutpoint_digest)
        << ",\"previous_recovery_expectation\":"
        << json_quote(previous_expectation)
        << ",\"recovery_expectation\":"
        << json_quote(next_expectation)
        << ",\"operator_asserted_database_recovery\":true"
        << ",\"forensic_preflight_before_writable_open\":true"
        << ",\"exact_transaction_reproof\":true"
        << ",\"recovery_epoch_advanced\":true"
        << ",\"whole_image_rollback_reuse_excluded\":false"
        << ",\"retention_age_reset_required_when_continuity_uncertain\":true"
        << ",\"mutation_performed\":true}\n";
    return 0;
}

[[nodiscard]] anonsync::SyncReplicaSelectiveSyncRule
parse_selective_sync_rule_or_throw(std::string_view encoded) {
    const std::size_t separator = encoded.find('=');
    if (separator == std::string_view::npos || separator == 0U ||
        separator + 1U >= encoded.size()) {
        throw std::invalid_argument(
            "--rule must use MODE=CANONICAL_PATH");
    }
    anonsync::SyncReplicaSelectiveSyncRule rule;
    rule.mode =
        anonsync::sync_replica_selective_sync_mode_from_name_or_throw(
            encoded.substr(0U, separator));
    rule.canonical_path = std::string(encoded.substr(separator + 1U));
    return rule;
}

void append_selective_sync_snapshot_json(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& catalog_path,
    const anonsync::SyncReplicaFolderSelectiveSyncSnapshot& snapshot) {
    output
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"folder_catalog\":"
        << json_quote(catalog_path.generic_string())
        << ",\"files_root\":"
        << json_quote(snapshot.absolute_root_path)
        << ",\"catalog_state_generation\":"
        << snapshot.state_generation
        << ",\"catalog_entry_count\":"
        << snapshot.catalog_entry_count
        << ",\"catalog_path_bytes\":"
        << snapshot.catalog_path_bytes
        << ",\"content_catalog_digest\":"
        << json_quote(snapshot.content_catalog_digest)
        << ",\"catalog_digest\":"
        << json_quote(snapshot.catalog_digest)
        << ",\"policy_generation\":"
        << snapshot.policy.generation
        << ",\"policy_default_mode\":"
        << json_quote(
               anonsync::sync_replica_selective_sync_mode_name(
                   snapshot.policy.default_mode))
        << ",\"policy_rule_count\":"
        << snapshot.policy.rules.size()
        << ",\"policy_rule_path_bytes\":"
        << snapshot.policy.rule_path_bytes
        << ",\"policy_digest\":"
        << json_quote(snapshot.policy.policy_digest)
        << ",\"absence_inference_fence_generation\":"
        << snapshot.absence_inference_fence_generation
        << ",\"absence_inference_fence_active\":"
        << json_bool(snapshot.absence_inference_fence_generation != 0U)
        << ",\"policy_maximum_rules\":"
        << anonsync::kSyncReplicaSelectiveSyncMaximumRules
        << ",\"policy_maximum_rule_path_bytes\":"
        << anonsync::kSyncReplicaSelectiveSyncMaximumRulePathBytes
        << ",\"rules\":[";
    for (std::size_t index = 0U;
         index < snapshot.policy.rules.size(); ++index) {
        if (index != 0U) output << ',';
        const auto& rule = snapshot.policy.rules[index];
        output
            << "{\"canonical_path\":"
            << json_quote(rule.canonical_path)
            << ",\"mode\":"
            << json_quote(
                   anonsync::sync_replica_selective_sync_mode_name(
                       rule.mode))
            << '}';
    }
    output
        << ']'
        << ",\"longest_component_prefix_wins\":true"
        << ",\"metadata_only_retains_causal_metadata\":true"
        << ",\"metadata_only_requests_payload_bytes\":false"
        << ",\"metadata_only_publishes_rooted_file\":false"
        << ",\"tombstones_remain_eligible\":true"
        << ",\"payload_store_observed\":false"
        << ",\"rooted_files_observed\":false"
        << ",\"replica_database_observed\":false"
        << ",\"network_started\":false"
        << ",\"deployment_singleton_acquired\":true";
}

[[nodiscard]] anonsync::SyncReplicaFolderSelectiveSyncSnapshot
inspect_selective_sync_policy_for_deployment_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& catalog_path,
    const anonsync::SyncReplicaSqliteDeploymentBinding& catalog_binding,
    const std::string& label) {
    anonsync::SyncReplicaOperationalDatabase database =
        anonsync::SyncReplicaOperationalDatabase::open_or_throw(
            catalog_path,
            anonsync::SyncReplicaOperationalDatabaseOpenDisposition::
                ExistingForensicReadOnly,
            label + " read-only catalog database");
    return anonsync::
        inspect_sync_replica_folder_selective_sync_snapshot_read_only_without_root_access_or_throw(
            database.handle(), catalog_binding, deployment.folder_id,
            *deployment.files_root, label + " policy inspection");
}

int command_selective_sync_status(const Options& options) {
    options.require_only({"manifest"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path, "anonsync_sync selective-sync-status manifest");
    anonsync::SyncReplicaPeerServiceSingletonOwner singleton(
        deployment,
        "anonsync_sync selective-sync-status deployment singleton");
    const fs::path catalog_path =
        anonsync::sync_replica_folder_catalog_path_or_throw(
            deployment, "anonsync_sync selective-sync-status catalog path");
    const anonsync::SyncReplicaSqliteDeploymentBinding catalog_binding =
        anonsync::sync_replica_folder_catalog_binding_or_throw(
            deployment,
            "anonsync_sync selective-sync-status catalog binding");
    const anonsync::SyncReplicaFolderSelectiveSyncSnapshot snapshot =
        inspect_selective_sync_policy_for_deployment_or_throw(
            deployment, catalog_path, catalog_binding,
            "anonsync_sync selective-sync-status");

    std::cout
        << "{\"command\":\"selective-sync-status\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-selective-sync-policy.response.v1");
    append_selective_sync_snapshot_json(
        std::cout, deployment, catalog_path, snapshot);
    std::cout << ",\"mutation_performed\":false}\n";
    return 0;
}

int command_selective_sync_set(const Options& options) {
    options.require_only({"manifest", "default", "rule"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaSelectiveSyncMode default_mode =
        anonsync::sync_replica_selective_sync_mode_from_name_or_throw(
            options.one("default"));
    std::vector<anonsync::SyncReplicaSelectiveSyncRule> rules;
    for (const std::string& encoded : options.many("rule")) {
        rules.push_back(parse_selective_sync_rule_or_throw(encoded));
    }

    const anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path, "anonsync_sync selective-sync-set manifest");
    anonsync::SyncReplicaPeerServiceSingletonOwner singleton(
        deployment,
        "anonsync_sync selective-sync-set deployment singleton");
    const fs::path catalog_path =
        anonsync::sync_replica_folder_catalog_path_or_throw(
            deployment, "anonsync_sync selective-sync-set catalog path");
    const anonsync::SyncReplicaSqliteDeploymentBinding catalog_binding =
        anonsync::sync_replica_folder_catalog_binding_or_throw(
            deployment, "anonsync_sync selective-sync-set catalog binding");

    const anonsync::SyncReplicaFolderSelectiveSyncSnapshot before =
        inspect_selective_sync_policy_for_deployment_or_throw(
            deployment, catalog_path, catalog_binding,
            "anonsync_sync selective-sync-set preflight");
    const anonsync::SyncReplicaSelectiveSyncPolicy requested =
        anonsync::make_sync_replica_selective_sync_policy_or_throw(
            default_mode, rules, before.policy.generation);

    anonsync::SyncReplicaFolderSelectiveSyncSnapshot completed = before;
    if (!anonsync::sync_replica_selective_sync_policy_semantically_equal(
            requested, before.policy)) {
        anonsync::SyncReplicaOperationalDatabase database =
            anonsync::SyncReplicaOperationalDatabase::open_or_throw(
                catalog_path,
                anonsync::SyncReplicaOperationalDatabaseOpenDisposition::
                    ExistingOperational,
                "anonsync_sync selective-sync-set writable catalog database");
        completed = anonsync::
            replace_sync_replica_folder_selective_sync_policy_without_root_access_or_throw(
                database.handle(), catalog_binding, deployment.folder_id,
                *deployment.files_root, default_mode, std::move(rules),
                "anonsync_sync selective-sync-set");
    }
    const bool mutation_performed =
        completed.policy.generation != before.policy.generation;

    std::cout
        << "{\"command\":\"selective-sync-set\""
        << ",\"terminal_class\":\"completed\""
        << ",\"response_schema\":"
        << json_quote(
               "anonsync.local-selective-sync-policy.response.v1");
    append_selective_sync_snapshot_json(
        std::cout, deployment, catalog_path, completed);
    std::cout
        << ",\"previous_policy_generation\":"
        << before.policy.generation
        << ",\"previous_policy_digest\":"
        << json_quote(before.policy.policy_digest)
        << ",\"mutation_performed\":"
        << json_bool(mutation_performed)
        << ",\"scheduling_frontiers_reset\":"
        << json_bool(mutation_performed)
        << ",\"service_must_be_stopped\":true}\n";
    return 0;
}

int command_once(
    const Options& options,
    std::chrono::steady_clock::time_point command_started_at) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "certificate", "private-key", "ca-file", "timeout-seconds",
        "max-runtime-seconds", "max-round-trips", "max-source-resets",
        "transport",
        "address", "port", "onion-address", "onion-port",
        "tor-socks-address", "tor-socks-port", "tor-isolation-token",
        "i2p-sam-address", "i2p-sam-port", "i2p-destination",
        "i2p-session-id", "i2p-private-destination-file",
        "i2p-inbound-quantity", "i2p-outbound-quantity",
        "maximum-entries", "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path, "anonsync_sync once manifest");
    anonsync::SyncReplicaPeerServiceSingletonOwner singleton_owner(
        deployment, "anonsync_sync once deployment singleton");

    anonsync::SyncReplicaStreamRoute route =
        stream_route_from_options_or_throw(options);
    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(route);
    const std::uint64_t timeout_seconds =
        timeout_from_options(options, route_kind);
    const std::uint64_t maximum_runtime_seconds =
        maximum_runtime_from_options(options, timeout_seconds);
    const auto folder_limits =
        folder_limits_from_options_or_throw(options, deployment);
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");
    anonsync::SyncReplicaTlsPeerPolicy expected_peer =
        expected_peer_from_options_or_throw(options);

    anonsync::SyncReplicaSyncOnceOptions sync_options;
    sync_options.folder_limits = folder_limits;
    sync_options.max_round_trips = option_uint64_or(
        options, "max-round-trips",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxRoundTrips);
    sync_options.max_source_resets = option_uint64_or(
        options, "max-source-resets",
        anonsync::kSyncReplicaReconciliationTlsDefaultMaxSourceResets);
    sync_options.stage_timeout_seconds = timeout_seconds;
    sync_options.maximum_runtime_seconds = maximum_runtime_seconds;
    sync_options.command_started_at = command_started_at;
    anonsync::validate_sync_replica_sync_once_options_or_throw(
        sync_options, "anonsync_sync once options");

    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, false,
        "anonsync_sync client TLS context");
    anonsync::SyncReplicaSyncOnceOwner owner(
        std::move(deployment),
        anonsync::retain_sync_replica_file_tls_client_context_or_throw(
            context.get(), "anonsync_sync retained client context"),
        std::move(route), std::move(expected_peer),
        "anonsync_sync once owner");
    const anonsync::SyncReplicaSyncOnceResult result =
        owner.run_once_or_throw(sync_options);

    std::cout
        << "{\"command\":\"once\",\"terminal_class\":"
        << json_quote(terminal_class(result.disposition))
        << ",\"disposition\":"
        << json_quote(anonsync::sync_replica_sync_once_disposition_name(
               result.disposition))
        << ",\"bounded_progress\":"
        << json_bool(anonsync::sync_replica_sync_once_is_bounded_progress(
               result.disposition))
        << ",\"durable_progress\":"
        << json_bool(anonsync::sync_replica_sync_once_made_durable_progress(
               result))
        << ",\"settled\":"
        << json_bool(anonsync::sync_replica_sync_once_is_settled(
               result.disposition))
        << ",\"manifest_path\":"
        << json_quote(owner.deployment().manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(owner.deployment().deployment_id)
        << ",\"folder_id\":" << json_quote(owner.deployment().folder_id)
        << ",\"local_device_id\":"
        << json_quote(owner.deployment().local_actor.device_id)
        << ",\"local_epoch\":" << owner.deployment().local_actor.epoch
        << ",\"remote_device_id\":"
        << json_quote(owner.expected_peer().actor.device_id)
        << ",\"remote_epoch\":" << owner.expected_peer().actor.epoch
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(
               owner.route_kind()))
        << ",\"session_timeout_seconds\":" << timeout_seconds
        << ",\"maximum_runtime_seconds\":"
        << maximum_runtime_seconds
        << ",\"max_round_trips\":" << sync_options.max_round_trips
        << ",\"max_source_resets\":" << sync_options.max_source_resets
        << ",\"pull_attempted\":" << json_bool(result.pull_attempted)
        << ",\"remote_apply_attempted\":"
        << json_bool(result.remote_apply_attempted)
        << ",\"command_deadline_reached_after_completion\":"
        << json_bool(result.command_deadline_reached_after_completion);
    append_cutpoint_json(std::cout, "before", result.before);
    append_cutpoint_json(
        std::cout, "after_local_pass", result.after_local_pass);
    append_cutpoint_json(std::cout, "after_pull", result.after_pull);
    append_cutpoint_json(std::cout, "after", result.after);
    append_pass_json(std::cout, "local_pass", result.local_pass);
    append_reconciliation_json(std::cout, result.reconciliation);
    append_pass_json(
        std::cout, "remote_apply_pass", result.remote_apply_pass);
    std::cout
        << ",\"limits\":{\"maximum_entries\":"
        << folder_limits.maximum_entries
        << ",\"maximum_regular_files\":"
        << folder_limits.maximum_regular_files
        << ",\"maximum_file_bytes\":"
        << folder_limits.maximum_file_bytes
        << ",\"maximum_total_file_bytes\":"
        << folder_limits.maximum_total_file_bytes
        << ",\"maximum_relative_path_bytes\":"
        << folder_limits.maximum_relative_path_bytes
        << ",\"maximum_directory_depth\":"
        << folder_limits.maximum_directory_depth
        << ",\"maximum_remote_paths\":"
        << folder_limits.maximum_remote_paths
        << ",\"maximum_remote_inspection_paths\":"
        << folder_limits.maximum_remote_inspection_paths
        << ",\"maximum_remote_apply_operations\":"
        << folder_limits.maximum_remote_apply_operations << "}}\n";

    return anonsync::sync_replica_sync_once_is_complete(result.disposition)
        ? 0
        : 2;
}

[[nodiscard]] anonsync::SyncReplicaPeerServiceLaunchConfiguration
legacy_peer_service_launch_configuration_from_options_or_throw(
    const Options& options) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "certificate", "private-key", "ca-file", "timeout-seconds",
        "max-runtime-seconds", "max-round-trips", "max-source-resets",
        "transport", "address", "port", "onion-address", "onion-port",
        "tor-socks-address", "tor-socks-port", "tor-isolation-token",
        "i2p-sam-address", "i2p-sam-port", "i2p-destination",
        "i2p-session-id", "i2p-private-destination-file",
        "i2p-inbound-quantity", "i2p-outbound-quantity",
        "maximum-entries", "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths",
        "bind-address", "listen-port", "scan-interval-seconds",
        "retry-initial-seconds", "retry-maximum-seconds",
        "accept-poll-milliseconds", "inbound-timeout-seconds",
        "inbound-max-round-trips", "ingress-timeout-seconds", "max-cycles",
        "max-service-runtime-seconds", "status-socket"});

    anonsync::SyncReplicaStreamRoute route =
        stream_route_from_options_or_throw(options);
    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(route);

    anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            require_absolute_path(options.one("manifest"), "--manifest"),
            "anonsync_sync run manifest");
    anonsync::SyncReplicaPeerServiceLimits limits =
        peer_service_limits_from_options_or_throw(
            options, deployment, route_kind,
            anonsync::SyncReplicaPeerIngressKind::DirectTcp);

    anonsync::SyncReplicaPeerServiceLaunchConfiguration configuration{
        .configuration_schema = std::string(
            anonsync::kSyncReplicaLinkedPeerServiceConfigurationSchema),
        .configuration_path = std::nullopt,
        .deployment = std::move(deployment),
        .expected_peer = expected_peer_from_options_or_throw(options),
        .tls = {
            require_existing_regular_file(
                options.one("certificate"), "--certificate"),
            require_existing_regular_file(
                options.one("private-key"), "--private-key"),
            require_existing_regular_file(
                options.one("ca-file"), "--ca-file")},
        .route = std::move(route),
        .ingress = anonsync::SyncReplicaDirectTcpIngress{},
        .listen_endpoint = {
            options.one_or("bind-address", "127.0.0.1"),
            parse_port(options.one("listen-port"), "--listen-port")},
        .status_socket_path = options.has("status-socket")
            ? std::optional<fs::path>(require_absolute_path(
                  options.one("status-socket"), "--status-socket"))
            : std::nullopt,
        .limits = std::move(limits),
        .maximum_cycles = optional_uint64(options, "max-cycles"),
        .maximum_service_runtime_seconds =
            optional_uint64(options, "max-service-runtime-seconds")};
    anonsync::validate_sync_replica_peer_service_launch_configuration_or_throw(
        configuration, false, "anonsync_sync run launch configuration");
    return configuration;
}

[[nodiscard]] anonsync::SyncReplicaPeerServiceLaunchConfiguration
peer_service_launch_configuration_from_options_or_throw(
    const Options& options) {
    if (!options.has("config")) {
        return legacy_peer_service_launch_configuration_from_options_or_throw(
            options);
    }
    options.require_only({"config"});
    return anonsync::read_sync_replica_linked_peer_service_configuration_or_throw(
        require_absolute_path(options.one("config"), "--config"),
        "anonsync_sync linked-peer service configuration");
}

[[nodiscard]] anonsync::SyncReplicaPeerServiceHistoricalVersionAction
peer_historical_version_action_or_throw(
    anonsync::SyncLocalStatusSocketHistoricalVersionOperation operation) {
    using Local =
        anonsync::SyncLocalStatusSocketHistoricalVersionOperation;
    using Peer = anonsync::SyncReplicaPeerServiceHistoricalVersionAction;
    switch (operation) {
        case Local::Inspect: return Peer::Inspect;
        case Local::Restore: return Peer::Restore;
        case Local::Pin: return Peer::Pin;
        case Local::Unpin: return Peer::Unpin;
        case Local::RetentionPlan: return Peer::RetentionPlan;
    }
    throw std::invalid_argument(
        "anonsync_sync observed an unknown historical-version action");
}

int command_run(const Options& options) {
    anonsync::SyncReplicaPeerServiceLaunchConfiguration launch =
        peer_service_launch_configuration_from_options_or_throw(options);
    const auto configuration_path = launch.configuration_path;
    const auto status_socket_path = launch.status_socket_path;
    const auto maximum_cycles = launch.maximum_cycles;
    const auto maximum_service_runtime_seconds =
        launch.maximum_service_runtime_seconds;
    const auto limits = launch.limits;

    // Install stop handling before any public listener becomes visible. Claim
    // the deployment before TLS setup so a duplicate process fails quickly and
    // cannot hide behind a different listen port, status socket, or config file.
    g_peer_service_stop_requested = 0;
    PeerServiceSignalOwner signal_owner;
    anonsync::SyncSystemdNotifier service_manager =
        anonsync::SyncSystemdNotifier::from_environment_or_throw(
            "anonsync_sync service manager notification");
    service_manager.publish_startup_status_or_throw(
        "Starting: claiming configured deployment");
    anonsync::SyncReplicaPeerServiceSingletonOwner singleton_owner(
        launch.deployment, "anonsync_sync peer service singleton");

    service_manager.publish_startup_status_or_throw(
        "Starting: loading TLS identity");
    SslContextOwner client_context = load_tls_context_or_throw(
        launch.tls.certificate, launch.tls.private_key, launch.tls.ca_file,
        false, "anonsync_sync service client TLS context");
    SslContextOwner server_context = load_tls_context_or_throw(
        launch.tls.certificate, launch.tls.private_key, launch.tls.ca_file,
        true, "anonsync_sync service server TLS context");

    anonsync::SyncReplicaPeerServiceOwner owner(
        std::move(launch.deployment),
        anonsync::retain_sync_replica_file_tls_client_context_or_throw(
            client_context.get(),
            "anonsync_sync service retained client context"),
        anonsync::retain_sync_replica_file_tls_server_context_or_throw(
            server_context.get(),
            "anonsync_sync service retained server context"),
        std::move(launch.route), std::move(launch.ingress),
        std::move(launch.expected_peer), launch.listen_endpoint, limits,
        "anonsync_sync peer service");
    const auto service_started_at = std::chrono::steady_clock::now();
    const std::optional<std::chrono::steady_clock::time_point>
        service_deadline = maximum_service_runtime_seconds.has_value()
        ? std::optional<std::chrono::steady_clock::time_point>(
              service_started_at +
              std::chrono::seconds(*maximum_service_runtime_seconds))
        : std::nullopt;

    anonsync::SyncReplicaPeerServiceLoopSummary summary;
    std::uint64_t status_generation = 0U;
    std::unique_ptr<anonsync::SyncLocalStatusSocketServer> status_server;
    if (status_socket_path.has_value()) {
        status_server = std::make_unique<anonsync::SyncLocalStatusSocketServer>(
            *status_socket_path,
            anonsync::render_sync_replica_peer_service_status_json(
                owner, summary, status_generation, service_started_at,
                "starting", "starting", configuration_path,
                status_socket_path),
            "anonsync_sync local status socket");
    }
    const auto publish_status = [&](std::string_view service_state,
                                    std::string_view activity,
                                    std::optional<std::string_view> reason =
                                        std::nullopt) {
        if (!status_server) return;
        status_server->publish_or_throw(
            anonsync::render_sync_replica_peer_service_status_json(
                owner, summary, status_generation, service_started_at,
                service_state, activity, configuration_path,
                status_socket_path, reason));
        status_server->require_healthy_or_throw();
    };
    const auto current_service_state = [&]() -> std::string_view {
        if (owner.payload_integrity_fault_active()) return "faulted";
        if (!owner.initial_repair_complete()) return "starting";
        return owner.ready() ? "running" : "degraded";
    };
    const auto publish_service_manager_transition = [&]() {
        if (!service_manager.ready_announced()) {
            if (owner.ready()) {
                service_manager.announce_ready_or_throw(
                    "Running: initial repair and required ingress are ready");
            } else if (owner.payload_integrity_fault_active()) {
                service_manager.publish_startup_status_or_throw(
                    "Faulted: payload integrity mismatch; synchronization is "
                    "paused pending current-byte reproof");
            } else if (!owner.initial_repair_complete()) {
                service_manager.publish_startup_status_or_throw(
                    "Starting: repairing configured folder");
            } else {
                service_manager.publish_startup_status_or_throw(
                    "Starting: publishing required peer ingress");
            }
            return;
        }
        if (owner.payload_integrity_fault_active()) {
            service_manager.publish_runtime_status(
                "Faulted: payload integrity mismatch; synchronization is "
                "paused pending current-byte reproof");
        } else if (owner.ready()) {
            service_manager.publish_runtime_status(
                "Running: linked-peer synchronization is operational");
        } else {
            service_manager.publish_runtime_status(
                "Degraded: required readiness evidence is unavailable; local "
                "repair and outbound synchronization continue");
        }
    };
    publish_service_manager_transition();

    std::string_view stop_reason = "stop_requested";
    bool runtime_deadline_reached_after_step = false;
    bool terminal_handoff_drain_attempted = false;
    bool terminal_handoff_drained = false;
    bool terminal_handoff_drain_deadline_reached = false;
    std::optional<std::chrono::steady_clock::time_point>
        terminal_handoff_drain_deadline;
    anonsync::SyncLocalStatusSocketActionSnapshot observed_local_actions;
    const auto observe_local_actions_or_throw = [&]() {
        if (!status_server) {
            observed_local_actions = {};
            return observed_local_actions;
        }
        const auto completed_quarantine = owner.payload_quarantine_status();
        if (completed_quarantine.completed_generation != 0U) {
            status_server->complete_payload_quarantine_request_or_throw(
                completed_quarantine.completed_generation);
        }
        const auto completed_historical_versions =
            owner.historical_version_status();
        if (completed_historical_versions.completed_generation != 0U) {
            status_server->complete_historical_version_request_or_throw(
                completed_historical_versions.completed_generation);
        }
        observed_local_actions = status_server->action_snapshot();
        owner.observe_payload_recheck_request_generation_or_throw(
            observed_local_actions.recheck_request_generation);
        if (observed_local_actions.payload_quarantine_request.has_value()) {
            const auto& request =
                *observed_local_actions.payload_quarantine_request;
            owner.observe_payload_quarantine_request_or_throw(
                request.request_generation,
                request.operation == anonsync::
                        SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
                    ? anonsync::
                          SyncReplicaFilePayloadStoreQuarantineAction::Preserve
                    : anonsync::
                          SyncReplicaFilePayloadStoreQuarantineAction::Release,
                request.expected_content_sha256,
                request.observed_content_sha256);
        }
        if (observed_local_actions.historical_version_request.has_value()) {
            const auto& request =
                *observed_local_actions.historical_version_request;
            owner.observe_historical_version_request_or_throw(
                request.request_generation,
                peer_historical_version_action_or_throw(request.operation),
                request.restore_request, request.query,
                request.retention_plan_query,
                request.retention_operation_id);
        }
        return observed_local_actions;
    };
    for (;;) {
        const auto now = std::chrono::steady_clock::now();
        const auto actions_at_loop_start = observe_local_actions_or_throw();
        if (g_peer_service_stop_requested != 0) {
            stop_reason = "stop_requested";
            break;
        }
        if (actions_at_loop_start.stop_requested) {
            stop_reason = "local_stop_requested";
            break;
        }
        if (service_deadline.has_value() && now >= *service_deadline) {
            stop_reason = "maximum_runtime_reached";
            break;
        }
        if (maximum_cycles.has_value() &&
            owner.counters().outbound_cycles >= *maximum_cycles) {
            if (!terminal_handoff_drain_attempted) {
                const bool successful_final_handoff =
                    summary.last_step.has_value() &&
                    summary.last_step->disposition ==
                        anonsync::SyncReplicaPeerServiceStepDisposition::
                            OutboundCycleCompleted &&
                    summary.last_step->network_turn_handed_off;
                if (!owner.local_is_recovery_initiator() ||
                    !successful_final_handoff) {
                    stop_reason = "maximum_cycles_reached";
                    break;
                }
                terminal_handoff_drain_attempted = true;
                const auto drain_horizon = std::chrono::seconds(
                    static_cast<std::chrono::seconds::rep>(
                        limits.cycle_runtime_seconds));
                if (now > std::chrono::steady_clock::time_point::max() -
                              drain_horizon) {
                    throw std::overflow_error(
                        "anonsync_sync terminal handoff drain deadline "
                        "overflows");
                }
                terminal_handoff_drain_deadline = now + drain_horizon;
            }
            if (terminal_handoff_drained) {
                stop_reason = "maximum_cycles_reached";
                break;
            }
            if (terminal_handoff_drain_deadline.has_value() &&
                now >= *terminal_handoff_drain_deadline) {
                terminal_handoff_drain_deadline_reached = true;
                stop_reason = "maximum_cycles_reached";
                break;
            }
            if (owner.role() !=
                anonsync::SyncReplicaPeerServiceRole::InboundServe) {
                stop_reason = "maximum_cycles_reached";
                break;
            }
        }

        const bool payload_quarantine_pending =
            owner.payload_quarantine_status().pending;
        const bool historical_version_pending =
            owner.historical_version_status().pending;
        const bool payload_recheck_pending =
            owner.payload_recheck_status().pending;
        const auto payload_terminal_verification =
            owner.payload_terminal_verification_status();
        const bool payload_terminal_verification_pending =
            payload_terminal_verification.observation_known &&
            payload_terminal_verification.pending_entry_count != 0U;
        const bool source_manifest_projection_pending =
            owner.source_manifest_projection_status().pending;
        publish_status(
            current_service_state(),
            payload_quarantine_pending
                ? "payload_quarantine"
                : (historical_version_pending
                       ? "historical_version"
                       : (payload_recheck_pending
                              ? "payload_recheck"
                              : (owner.payload_integrity_fault_active()
                       ? "payload_integrity_reproof"
                       : (!owner.initial_repair_complete()
                              ? "initial_repair"
                              : (payload_terminal_verification_pending
                                     ? "payload_terminal_verification"
                                     : (source_manifest_projection_pending
                                            ? "source_manifest_projection"
                                            : (owner.ingress_ready()
                                                   ? "peer_service_step"
                                                   : "ingress_publication"))))))));
        const auto actions_before_step = observe_local_actions_or_throw();
        if (actions_before_step.stop_requested) {
            stop_reason = "local_stop_requested";
            break;
        }
        const auto step = owner.run_next_or_throw();
        anonsync::account_sync_replica_peer_service_step(summary, step);
        ++status_generation;
        publish_service_manager_transition();
        if (terminal_handoff_drain_attempted && step.inbound.has_value() &&
            step.exact_peer_observed && step.network_turn_handed_off) {
            terminal_handoff_drained = true;
        }
        if (service_deadline.has_value() &&
            std::chrono::steady_clock::now() >= *service_deadline) {
            runtime_deadline_reached_after_step = true;
        }
        const auto actions_after_step = observe_local_actions_or_throw();
        const bool local_drain_pending = actions_after_step.stop_requested;
        const bool ingress_backoff_pending =
            step.disposition == anonsync::SyncReplicaPeerServiceStepDisposition::
                IngressPublicationBackoffPending;
        const bool payload_integrity_backoff_pending =
            step.disposition == anonsync::SyncReplicaPeerServiceStepDisposition::
                    PayloadIntegrityFaultObserved ||
            step.disposition == anonsync::SyncReplicaPeerServiceStepDisposition::
                    PayloadIntegrityReproofBackoffPending;
        const bool payload_store_lease_backoff_pending =
            step.disposition == anonsync::SyncReplicaPeerServiceStepDisposition::
                    PayloadStoreLeaseBusyDeferred;
        publish_status(
            current_service_state(),
            local_drain_pending
                ? "drain_requested"
                : (payload_integrity_backoff_pending
                       ? "payload_integrity_retry_wait"
                       : (payload_store_lease_backoff_pending
                              ? "payload_store_lease_retry_wait"
                              : (ingress_backoff_pending
                                     ? "ingress_retry_wait"
                                     : "between_steps"))));
        std::uint64_t bounded_wait = 0U;
        if (payload_integrity_backoff_pending &&
            step.payload_integrity_retry_delay_milliseconds != 0U) {
            bounded_wait = std::min(
                step.payload_integrity_retry_delay_milliseconds,
                anonsync::
                    kSyncReplicaPeerServiceMaximumIntegrityBackoffWaitMilliseconds);
        } else if (payload_store_lease_backoff_pending &&
                   step.payload_store_lease_retry_delay_milliseconds != 0U) {
            bounded_wait = std::min(
                step.payload_store_lease_retry_delay_milliseconds,
                anonsync::
                    kSyncReplicaPeerServiceMaximumPayloadStoreLeaseBackoffWaitMilliseconds);
        } else if (ingress_backoff_pending &&
                   step.ingress_retry_delay_milliseconds != 0U) {
            bounded_wait = std::min(
                step.ingress_retry_delay_milliseconds,
                anonsync::
                    kSyncReplicaPeerServiceMaximumIngressBackoffWaitMilliseconds);
        }
        if (bounded_wait != 0U && !local_drain_pending) {
            if (status_server) {
                (void)status_server->wait_for_action_request_or_timeout(
                    actions_after_step, bounded_wait);
            } else {
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(bounded_wait));
            }
        }
    }
    if (status_server) {
        // Publish any owner-completed quarantine cutpoint before closing action
        // admission. A quarantine or recheck racing any non-local stop reason
        // is then either included in this exact combined action snapshot or
        // rejected after drain; neither can be accepted after the owner's
        // final observation.
        const auto completed_quarantine = owner.payload_quarantine_status();
        if (completed_quarantine.completed_generation != 0U) {
            status_server->complete_payload_quarantine_request_or_throw(
                completed_quarantine.completed_generation);
        }
        const auto completed_historical_versions =
            owner.historical_version_status();
        if (completed_historical_versions.completed_generation != 0U) {
            status_server->complete_historical_version_request_or_throw(
                completed_historical_versions.completed_generation);
        }
        observed_local_actions =
            status_server->seal_actions_for_owner_shutdown();
        owner.observe_payload_recheck_request_generation_or_throw(
            observed_local_actions.recheck_request_generation);
        if (observed_local_actions.payload_quarantine_request.has_value()) {
            const auto& request =
                *observed_local_actions.payload_quarantine_request;
            owner.observe_payload_quarantine_request_or_throw(
                request.request_generation,
                request.operation == anonsync::
                        SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
                    ? anonsync::
                          SyncReplicaFilePayloadStoreQuarantineAction::Preserve
                    : anonsync::
                          SyncReplicaFilePayloadStoreQuarantineAction::Release,
                request.expected_content_sha256,
                request.observed_content_sha256);
        }
        if (observed_local_actions.historical_version_request.has_value()) {
            const auto& request =
                *observed_local_actions.historical_version_request;
            owner.observe_historical_version_request_or_throw(
                request.request_generation,
                peer_historical_version_action_or_throw(request.operation),
                request.restore_request, request.query,
                request.retention_plan_query,
                request.retention_operation_id);
        }
    }
    service_manager.announce_stopping(
        "Stopping: " + std::string(stop_reason));
    publish_status("stopping", "stopped", stop_reason);

    const auto elapsed =
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - service_started_at);
    const auto& counters = owner.counters();
    const auto payload_terminal_verification =
        owner.payload_terminal_verification_status();
    const auto source_manifest_projection =
        owner.source_manifest_projection_status();
    const auto payload_recheck = owner.payload_recheck_status();
    const auto payload_quarantine = owner.payload_quarantine_status();
    const auto historical_versions = owner.historical_version_status();
    const auto service_manager_snapshot = service_manager.snapshot();

    std::cout
        << "{\"command\":\"run\",\"terminal_class\":\"completed\""
        << ",\"stop_reason\":" << json_quote(stop_reason)
        << ",\"service_manager_notify\":{\"configured\":"
        << json_bool(service_manager_snapshot.configured)
        << ",\"ready_announced\":"
        << json_bool(service_manager_snapshot.ready_announced)
        << ",\"stopping_announced\":"
        << json_bool(service_manager_snapshot.stopping_announced)
        << ",\"datagrams_attempted\":"
        << service_manager_snapshot.datagrams_attempted
        << ",\"datagrams_sent\":"
        << service_manager_snapshot.datagrams_sent
        << ",\"datagrams_failed\":"
        << service_manager_snapshot.datagrams_failed
        << ",\"last_status\":";
    if (service_manager_snapshot.last_status.has_value()) {
        std::cout << json_quote(*service_manager_snapshot.last_status);
    } else {
        std::cout << "null";
    }
    std::cout << ",\"last_error\":";
    if (service_manager_snapshot.last_error.has_value()) {
        std::cout << json_quote(*service_manager_snapshot.last_error);
    } else {
        std::cout << "null";
    }
    std::cout << '}'
        << ",\"listener_started\":"
        << json_bool(owner.has_numeric_listener())
        << ",\"configuration_path\":";
    if (configuration_path.has_value()) {
        std::cout << json_quote(configuration_path->generic_string());
    } else {
        std::cout << "null";
    }
    std::cout << ",\"status_socket\":";
    if (status_socket_path.has_value()) {
        std::cout << json_quote(status_socket_path->generic_string());
    } else {
        std::cout << "null";
    }
    std::cout
        << ",\"runtime_deadline_reached_after_step\":"
        << json_bool(runtime_deadline_reached_after_step)
        << ",\"terminal_handoff_drain_attempted\":"
        << json_bool(terminal_handoff_drain_attempted)
        << ",\"terminal_handoff_drained\":"
        << json_bool(terminal_handoff_drained)
        << ",\"terminal_handoff_drain_deadline_reached\":"
        << json_bool(terminal_handoff_drain_deadline_reached)
        << ",\"elapsed_milliseconds\":" << elapsed.count()
        << ",\"manifest_path\":"
        << json_quote(owner.deployment().manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(owner.deployment().deployment_id)
        << ",\"folder_id\":" << json_quote(owner.deployment().folder_id)
        << ",\"local_device_id\":"
        << json_quote(owner.deployment().local_actor.device_id)
        << ",\"local_epoch\":" << owner.deployment().local_actor.epoch
        << ",\"remote_device_id\":"
        << json_quote(owner.expected_peer().actor.device_id)
        << ",\"remote_epoch\":" << owner.expected_peer().actor.epoch
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(
               owner.route_kind()))
        << ",\"ingress_transport\":"
        << json_quote(anonsync::sync_replica_peer_ingress_kind_name(
               owner.ingress_kind()))
        << ",\"ingress_ready\":" << json_bool(owner.ingress_ready())
        << ",\"numeric_listener_active\":"
        << json_bool(owner.has_numeric_listener())
        << ",\"bind_address\":";
    if (owner.has_numeric_listener()) {
        std::cout << json_quote(owner.listen_endpoint().numeric_address);
    } else {
        std::cout << "null";
    }
    std::cout << ",\"listen_port\":";
    if (owner.has_numeric_listener()) {
        std::cout << owner.listen_endpoint().port;
    } else {
        std::cout << "null";
    }
    std::cout
        << ",\"local_recovery_initiator\":"
        << json_bool(owner.local_is_recovery_initiator())
        << ",\"final_role\":"
        << json_quote(anonsync::sync_replica_peer_service_role_name(
               owner.role()))
        << ",\"steps\":" << counters.steps
        << ",\"payload_terminal_verification\":"
        << anonsync::
               render_sync_replica_file_payload_store_terminal_verification_status_json(
                   payload_terminal_verification)
        << ",\"source_manifest_projection\":"
        << anonsync::
               render_sync_replica_source_manifest_projection_status_json(
                   source_manifest_projection)
        << ",\"payload_recheck\":"
        << anonsync::
               render_sync_replica_peer_service_payload_recheck_status_json(
                   payload_recheck)
        << ",\"payload_quarantine\":"
        << anonsync::
               render_sync_replica_peer_service_payload_quarantine_status_json(
                   payload_quarantine)
        << ",\"historical_versions\":"
        << anonsync::
               render_sync_replica_peer_service_historical_version_status_json(
                   historical_versions)
        << ",\"payload_integrity_fault_active\":"
        << json_bool(owner.payload_integrity_fault_active())
        << ",\"payload_integrity_faults_observed\":"
        << counters.payload_integrity_faults_observed
        << ",\"payload_integrity_reproof_attempts\":"
        << counters.payload_integrity_reproof_attempts
        << ",\"payload_integrity_reproof_recoveries\":"
        << counters.payload_integrity_reproof_recoveries
        << ",\"payload_integrity_reproof_snapshot_handoffs\":"
        << counters.payload_integrity_reproof_snapshot_handoffs
        << ",\"payload_integrity_reproof_convergence_snapshot_observations\":"
        << counters
               .payload_integrity_reproof_convergence_snapshot_observations
        << ",\"payload_integrity_reproof_convergence_mutation_full_scans\":"
        << counters
               .payload_integrity_reproof_convergence_mutation_full_scans
        << ",\"payload_integrity_backoff_deferrals\":"
        << counters.payload_integrity_backoff_deferrals
        << ",\"payload_store_lease_busy_deferrals\":"
        << counters.payload_store_lease_busy_deferrals
        << ",\"payload_store_lease_backoff_deferrals\":"
        << counters.payload_store_lease_backoff_deferrals
        << ",\"payload_authority_network_outcome_uncertain_steps\":"
        << counters.payload_authority_network_outcome_uncertain_steps
        << ",\"payload_terminal_verification_scheduler_steps\":"
        << counters.payload_terminal_verification_scheduler_steps
        << ",\"payload_terminal_verification_progress_steps\":"
        << counters.payload_terminal_verification_progress_steps
        << ",\"payload_terminal_verification_completions\":"
        << counters.payload_terminal_verification_completions
        << ",\"payload_terminal_verification_insertions\":"
        << counters.payload_terminal_verification_insertions
        << ",\"payload_terminal_verification_reconciliations\":"
        << counters.payload_terminal_verification_reconciliations
        << ",\"payload_terminal_verification_hashed_bytes\":"
        << counters.payload_terminal_verification_hashed_bytes
        << ",\"payload_terminal_verification_ordinary_turn_yields\":"
        << counters.payload_terminal_verification_ordinary_turn_yields
        << ",\"source_manifest_projection_scheduler_steps\":"
        << counters.source_manifest_projection_scheduler_steps
        << ",\"source_manifest_projection_progress_steps\":"
        << counters.source_manifest_projection_progress_steps
        << ",\"source_manifest_projection_completions\":"
        << counters.source_manifest_projection_completions
        << ",\"source_manifest_projection_payload_unavailable\":"
        << counters.source_manifest_projection_payload_unavailable
        << ",\"source_manifest_projection_restarts\":"
        << counters.source_manifest_projection_restarts
        << ",\"source_manifest_projection_hashed_bytes\":"
        << counters.source_manifest_projection_hashed_bytes
        << ",\"source_manifest_projection_ordinary_turn_yields\":"
        << counters.source_manifest_projection_ordinary_turn_yields
        << ",\"payload_recheck_requests_observed\":"
        << counters.payload_recheck_requests_observed
        << ",\"payload_recheck_requests_coalesced\":"
        << counters.payload_recheck_requests_coalesced
        << ",\"payload_recheck_attempts\":"
        << counters.payload_recheck_attempts
        << ",\"payload_recheck_completions\":"
        << counters.payload_recheck_completions
        << ",\"payload_recheck_integrity_recoveries\":"
        << counters.payload_recheck_integrity_recoveries
        << ",\"payload_recheck_snapshot_handoffs\":"
        << counters.payload_recheck_snapshot_handoffs
        << ",\"payload_recheck_convergence_snapshot_observations\":"
        << counters.payload_recheck_convergence_snapshot_observations
        << ",\"payload_recheck_convergence_mutation_full_scans\":"
        << counters.payload_recheck_convergence_mutation_full_scans
        << ",\"payload_quarantine_requests_observed\":"
        << counters.payload_quarantine_requests_observed
        << ",\"payload_quarantine_requests_coalesced\":"
        << counters.payload_quarantine_requests_coalesced
        << ",\"payload_quarantine_attempts\":"
        << counters.payload_quarantine_attempts
        << ",\"payload_quarantine_completions\":"
        << counters.payload_quarantine_completions
        << ",\"payload_quarantine_images_preserved\":"
        << counters.payload_quarantine_images_preserved
        << ",\"payload_quarantine_images_released\":"
        << counters.payload_quarantine_images_released
        << ",\"payload_quarantine_observed_content_changes\":"
        << counters.payload_quarantine_observed_content_changes
        << ",\"historical_version_requests_observed\":"
        << counters.historical_version_requests_observed
        << ",\"historical_version_requests_coalesced\":"
        << counters.historical_version_requests_coalesced
        << ",\"historical_version_attempts\":"
        << counters.historical_version_attempts
        << ",\"historical_version_completions\":"
        << counters.historical_version_completions
        << ",\"historical_version_inspections\":"
        << counters.historical_version_inspections
        << ",\"historical_version_retention_plans\":"
        << counters.historical_version_retention_plans
        << ",\"historical_version_restores\":"
        << counters.historical_version_restores
        << ",\"historical_version_pins\":"
        << counters.historical_version_pins
        << ",\"historical_version_unpins\":"
        << counters.historical_version_unpins
        << ",\"historical_version_failures\":"
        << counters.historical_version_failures
        << ",\"initial_repairs\":" << counters.initial_repairs
        << ",\"periodic_repairs\":" << counters.periodic_repairs
        << ",\"filesystem_wake_repairs\":"
        << counters.filesystem_wake_repairs
        << ",\"filesystem_wakes_consumed_by_outbound\":"
        << counters.filesystem_wakes_consumed_by_outbound
        << ",\"cycles_attempted\":" << counters.outbound_cycles
        << ",\"cycles_complete\":" << summary.cycles_complete
        << ",\"cycles_settled\":" << summary.cycles_settled
        << ",\"cycles_changed\":" << summary.cycles_changed
        << ",\"cycles_with_unresolved_paths\":"
        << summary.cycles_with_unresolved_paths
        << ",\"cycles_partial_progress\":"
        << summary.cycles_partial_progress
        << ",\"cycles_failed\":" << summary.cycles_failed
        << ",\"cycles_with_durable_progress\":"
        << summary.cycles_with_durable_progress
        << ",\"outbound_handoffs\":" << counters.outbound_handoffs
        << ",\"outbound_failures\":" << counters.outbound_failures
        << ",\"outbound_session_io_failures\":"
        << counters.outbound_session_io_failures
        << ",\"inbound_session_io_failures\":"
        << counters.inbound_session_io_failures
        << ",\"ingress\":{\"setup_attempts\":"
        << counters.ingress_setup_attempts
        << ",\"setup_successes\":" << counters.ingress_setup_successes
        << ",\"setup_failures\":" << counters.ingress_setup_failures
        << ",\"losses\":" << counters.ingress_losses
        << ",\"backoff_deferrals\":"
        << counters.ingress_backoff_deferrals << '}'
        << ",\"inbound\":{\"accept_deadline_expirations\":"
        << counters.inbound_accept_windows_expired
        << ",\"accepted_sessions\":" << summary.accepted_sessions
        << ",\"completed_handshakes\":"
        << summary.completed_handshakes
        << ",\"rejected_handshakes\":"
        << summary.rejected_handshakes
        << ",\"unauthorized_peers\":" << summary.unauthorized_peers
        << ",\"applications_served\":"
        << summary.applications_served
        << ",\"file_delivery_sessions\":"
        << summary.file_delivery_sessions
        << ",\"reconciliation_sessions\":"
        << summary.reconciliation_sessions
        << ",\"unsupported_application_sessions\":"
        << summary.unsupported_application_sessions
        << ",\"peer_closed_sessions\":"
        << summary.peer_closed_sessions
        << ",\"application_deadline_expirations\":"
        << summary.application_deadline_expirations
        << ",\"exact_peer_sessions\":"
        << counters.inbound_exact_peer_sessions
        << ",\"handoffs\":" << counters.inbound_handoffs << '}';

    std::cout << ",\"filesystem_watch\":";
    std::cout << anonsync::render_sync_replica_folder_wake_status_json(
        owner.folder_wake_snapshot());

    std::cout << ",\"last_step\":";
    if (!summary.last_step.has_value()) {
        std::cout << "null";
    } else {
        const auto& step = *summary.last_step;
        std::cout
            << "{\"disposition\":"
            << json_quote(
                   anonsync::sync_replica_peer_service_step_disposition_name(
                       step.disposition))
            << ",\"role_before\":"
            << json_quote(anonsync::sync_replica_peer_service_role_name(
                   step.role_before))
            << ",\"role_after\":"
            << json_quote(anonsync::sync_replica_peer_service_role_name(
                   step.role_after))
            << ",\"exact_peer_observed\":"
            << json_bool(step.exact_peer_observed)
            << ",\"network_turn_handed_off\":"
            << json_bool(step.network_turn_handed_off)
            << ",\"network_outcome_known\":"
            << json_bool(step.network_outcome_known)
            << ",\"payload_store_lease_conflict_observed\":"
            << json_bool(step.payload_store_lease_conflict_observed)
            << ",\"filesystem_wake_observed\":"
            << json_bool(step.filesystem_wake_observed)
            << ",\"filesystem_wake_overflow\":"
            << json_bool(step.filesystem_wake_overflow)
            << ",\"filesystem_watch_rebuilt\":"
            << json_bool(step.filesystem_watch_rebuilt)
            << ",\"filesystem_wake_event_count\":"
            << step.filesystem_wake_event_count
            << ",\"consecutive_outbound_failures\":"
            << step.consecutive_outbound_failures
            << ",\"retry_delay_milliseconds\":"
            << step.retry_delay_milliseconds
            << ",\"ingress_ready\":" << json_bool(step.ingress_ready)
            << ",\"consecutive_ingress_failures\":"
            << step.consecutive_ingress_failures
            << ",\"ingress_retry_delay_milliseconds\":"
            << step.ingress_retry_delay_milliseconds
            << ",\"payload_integrity_retry_delay_milliseconds\":"
            << step.payload_integrity_retry_delay_milliseconds
            << ",\"payload_store_lease_retry_delay_milliseconds\":"
            << step.payload_store_lease_retry_delay_milliseconds
            << ",\"payload_terminal_verification\":";
        if (step.payload_terminal_verification.has_value()) {
            const auto& terminal = *step.payload_terminal_verification;
            std::cout
                << "{\"disposition\":"
                << json_quote(anonsync::
                       sync_replica_file_payload_store_terminal_verification_step_disposition_name(
                           terminal.disposition))
                << ",\"work_before\":";
            if (terminal.work_before.has_value()) {
                const auto& work = *terminal.work_before;
                std::cout
                    << "{\"content_sha256\":"
                    << json_quote(work.content_sha256)
                    << ",\"total_size_bytes\":"
                    << work.total_size_bytes
                    << ",\"verified_offset_bytes\":"
                    << work.verified_offset_bytes << '}';
            } else {
                std::cout << "null";
            }
            std::cout
                << ",\"verified_offset_after_bytes\":"
                << terminal.verified_offset_after_bytes
                << ",\"hashed_bytes\":" << terminal.hashed_bytes
                << ",\"terminal_verification_steps\":"
                << terminal.terminal_verification_steps << '}';
        } else {
            std::cout << "null";
        }
        std::cout
            << ",\"payload_recheck_generation\":"
            << step.payload_recheck_generation
            << ",\"payload_recheck_hashed_entries\":"
            << step.payload_recheck_hashed_entry_count
            << ",\"payload_recheck_hashed_bytes\":"
            << step.payload_recheck_hashed_bytes
            << ",\"payload_recheck_snapshot_handoffs\":"
            << step.payload_recheck_snapshot_handoff_count
            << ",\"payload_recheck_convergence_snapshot_observations\":"
            << step
                   .payload_recheck_convergence_snapshot_observation_count
            << ",\"payload_recheck_convergence_mutation_full_scans\":"
            << step
                   .payload_recheck_convergence_mutation_full_scan_count
            << ",\"payload_recheck_recovered_integrity_fault\":"
            << json_bool(
                   step.payload_recheck_recovered_integrity_fault)
            << ",\"payload_quarantine_generation\":"
            << step.payload_quarantine_generation
            << ",\"payload_quarantine_result\":";
        if (step.payload_quarantine_result.has_value()) {
            std::cout << anonsync::
                render_sync_replica_file_payload_store_quarantine_result_json(
                    *step.payload_quarantine_result);
        } else {
            std::cout << "null";
        }
        std::cout << '}';
    }

    std::cout << ",\"last_cycle\":";
    if (!summary.last_cycle.has_value()) {
        std::cout << "null";
    } else {
        const auto& cycle = *summary.last_cycle;
        std::cout
            << "{\"disposition\":"
            << json_quote(anonsync::sync_replica_sync_once_disposition_name(
                   cycle.disposition))
            << ",\"bounded_progress\":"
            << json_bool(anonsync::sync_replica_sync_once_is_bounded_progress(
                   cycle.disposition))
            << ",\"durable_progress\":"
            << json_bool(anonsync::sync_replica_sync_once_made_durable_progress(
                   cycle))
            << ",\"settled\":"
            << json_bool(anonsync::sync_replica_sync_once_is_settled(
                   cycle.disposition));
        append_cutpoint_json(std::cout, "after", cycle.after);
        append_pass_json(std::cout, "local_pass", cycle.local_pass);
        append_reconciliation_json(std::cout, cycle.reconciliation);
        append_pass_json(
            std::cout, "remote_apply_pass", cycle.remote_apply_pass);
        std::cout << '}';
    }

    std::cout
        << ",\"service_limits\":{\"repair_interval_milliseconds\":"
        << limits.repair_interval_milliseconds
        << ",\"retry_initial_milliseconds\":"
        << limits.retry_initial_milliseconds
        << ",\"retry_maximum_milliseconds\":"
        << limits.retry_maximum_milliseconds
        << ",\"accept_window_milliseconds\":"
        << limits.accept_window_milliseconds
        << ",\"stage_timeout_seconds\":"
        << limits.stage_timeout_seconds
        << ",\"max_round_trips\":" << limits.max_round_trips
        << ",\"inbound_stage_timeout_seconds\":"
        << limits.inbound_stage_timeout_seconds
        << ",\"inbound_max_round_trips\":"
        << limits.inbound_max_round_trips
        << ",\"ingress_setup_timeout_seconds\":"
        << limits.ingress_setup_timeout_seconds
        << ",\"network_step_horizon_seconds\":"
        << anonsync::
               sync_replica_peer_service_network_step_horizon_seconds_or_throw(
                   limits, "anonsync_sync terminal service horizon")
        << ",\"installed_service_maximum_network_step_seconds\":"
        << anonsync::kSyncReplicaInstalledServiceMaximumNetworkStepSeconds
        << ",\"installed_service_stop_timeout_seconds\":"
        << anonsync::kSyncReplicaInstalledServiceStopTimeoutSeconds
        << ",\"maximum_cycles\":";
    if (maximum_cycles.has_value()) {
        std::cout << *maximum_cycles;
    } else {
        std::cout << "null";
    }
    std::cout << ",\"maximum_runtime_seconds\":";
    if (maximum_service_runtime_seconds.has_value()) {
        std::cout << *maximum_service_runtime_seconds;
    } else {
        std::cout << "null";
    }
    std::cout << "}}\n";
    return 0;
}

struct PeerCardSelection final {
    fs::path path;
    anonsync::SyncLinkedPeerCard card;
    std::string sha256;
    std::string verification_code;
    bool sha256_pinned = false;
};

[[nodiscard]] PeerCardSelection peer_card_from_options_or_throw(
    const Options& options,
    bool require_sha256_pin,
    std::string_view label) {
    if (require_sha256_pin && !options.has("peer-card-sha256")) {
        throw std::invalid_argument(
            "--peer-card-sha256 is required for share-join");
    }
    const fs::path path = require_existing_regular_file(
        options.one("peer-card"), "--peer-card");
    anonsync::SyncLinkedPeerCard card =
        anonsync::read_sync_linked_peer_card_file_or_throw(
            path, std::string(label) + " peer card");
    const std::string sha256 =
        anonsync::sync_linked_peer_card_sha256_or_throw(
            card, std::string(label) + " peer pairing-card fingerprint");
    const std::string verification_code =
        anonsync::sync_linked_peer_card_verification_code_or_throw(
            card,
            std::string(label) +
                " peer pairing-card verification code");
    const bool pinned = options.has("peer-card-sha256");
    if (pinned) {
        const std::string expected = options.one("peer-card-sha256");
        if (!anonsync::is_lowercase_sha256_hex(expected)) {
            throw std::invalid_argument(
                "--peer-card-sha256 must be lowercase SHA-256");
        }
        if (expected != sha256) {
            throw std::invalid_argument(
                "--peer-card-sha256 does not match the exact peer card");
        }
    }
    return {
        .path = path,
        .card = std::move(card),
        .sha256 = sha256,
        .verification_code = verification_code,
        .sha256_pinned = pinned,
    };
}

struct LinkedPeerProvisioningSummaryExtensions final {
    const anonsync::SyncLinkedPeerIdentityCreationResult* identity = nullptr;
    const std::string* local_pairing_card_sha256 = nullptr;
    const std::string* local_pairing_verification_code = nullptr;
    const fs::path* peer_card_path = nullptr;
    const std::string* peer_card_sha256 = nullptr;
    const std::string* peer_card_verification_code = nullptr;
    bool peer_card_sha256_pinned = false;
    const anonsync::SyncLinkedPeerAdmissionResult* admission = nullptr;
    const fs::path* state_directory = nullptr;
    const fs::path* files_root = nullptr;
    const fs::path* catalog_path = nullptr;
    const std::string* initial_files_mode = nullptr;
    const std::string* deployment_disposition = nullptr;
    const std::string* catalog_disposition = nullptr;
    const std::uint64_t* initial_local_published_count = nullptr;
    const std::uint64_t* initial_catalog_entry_count = nullptr;
    bool ready_to_start = false;
};

void emit_linked_peer_provisioning_summary(
    std::string_view command,
    const anonsync::SyncLinkedPeerUserLayout& layout,
    const anonsync::SyncReplicaPeerServiceProvisioningResult& provisioned,
    const LinkedPeerProvisioningSummaryExtensions& extensions = {},
    std::string_view terminal_class = "completed") {
    const auto& exact = provisioned.launch;
    const bool numeric_listener_active =
        anonsync::sync_replica_peer_ingress_kind(exact.ingress) !=
        anonsync::SyncReplicaPeerIngressKind::I2pSamAccept;

    const bool configuration_created =
        provisioned.disposition ==
        anonsync::SyncReplicaPeerServiceConfigurationDisposition::Created;
    std::cout
        << "{\"command\":" << json_quote(command)
        << ",\"terminal_class\":" << json_quote(terminal_class)
        << ",\"configuration_created\":"
        << json_bool(configuration_created)
        << ",\"configuration_disposition\":"
        << json_quote(
               anonsync::sync_replica_peer_service_configuration_disposition_name(
                   provisioned.disposition))
        << ",\"instance\":" << json_quote(layout.instance)
        << ",\"configuration_schema\":"
        << json_quote(exact.configuration_schema)
        << ",\"configuration_path\":"
        << json_quote(exact.configuration_path->generic_string())
        << ",\"configuration_bytes\":"
        << provisioned.exact_configuration_bytes.size()
        << ",\"runtime_directory\":"
        << json_quote(layout.runtime_directory.generic_string())
        << ",\"status_socket\":"
        << json_quote(exact.status_socket_path->generic_string())
        << ",\"systemd_unit\":" << json_quote(layout.systemd_unit)
        << ",\"manifest_path\":"
        << json_quote(exact.deployment.manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(exact.deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(exact.deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(exact.deployment.local_actor.device_id)
        << ",\"local_epoch\":" << exact.deployment.local_actor.epoch
        << ",\"remote_device_id\":"
        << json_quote(exact.expected_peer.actor.device_id)
        << ",\"remote_epoch\":" << exact.expected_peer.actor.epoch
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(
               anonsync::sync_replica_stream_route_kind(exact.route)))
        << ",\"ingress_transport\":"
        << json_quote(anonsync::sync_replica_peer_ingress_kind_name(
               anonsync::sync_replica_peer_ingress_kind(exact.ingress)))
        << ",\"numeric_listener_active\":"
        << json_bool(numeric_listener_active)
        << ",\"bind_address\":";
    if (numeric_listener_active) {
        std::cout << json_quote(exact.listen_endpoint.numeric_address);
    } else {
        std::cout << "null";
    }
    std::cout << ",\"listen_port\":";
    if (numeric_listener_active) {
        std::cout << exact.listen_endpoint.port;
    } else {
        std::cout << "null";
    }
    std::cout
        << ",\"network_step_horizon_seconds\":"
        << anonsync::
               sync_replica_peer_service_network_step_horizon_seconds_or_throw(
                   exact.limits,
                   "anonsync_sync linked-peer provisioning service horizon");

    if (extensions.identity != nullptr) {
        const auto& identity = *extensions.identity;
        std::cout
            << ",\"identity_directory\":"
            << json_quote(identity.layout.identity_directory.generic_string())
            << ",\"private_key_path\":"
            << json_quote(identity.layout.private_key_path.generic_string())
            << ",\"certificate_path\":"
            << json_quote(identity.layout.certificate_path.generic_string())
            << ",\"local_pairing_card_path\":"
            << json_quote(identity.layout.pairing_card_path.generic_string())
            << ",\"local_spki_sha256\":"
            << json_quote(identity.card.spki_sha256);
    }
    if (extensions.local_pairing_card_sha256 != nullptr) {
        std::cout
            << ",\"local_pairing_card_sha256\":"
            << json_quote(*extensions.local_pairing_card_sha256);
    }
    if (extensions.local_pairing_verification_code != nullptr) {
        std::cout
            << ",\"local_pairing_verification_code\":"
            << json_quote(*extensions.local_pairing_verification_code);
    }
    if (extensions.peer_card_path != nullptr) {
        std::cout << ",\"peer_card_path\":"
                  << json_quote(extensions.peer_card_path->generic_string());
    }
    if (extensions.peer_card_sha256 != nullptr) {
        std::cout
            << ",\"peer_card_sha256\":"
            << json_quote(*extensions.peer_card_sha256)
            << ",\"peer_card_sha256_pinned\":"
            << json_bool(extensions.peer_card_sha256_pinned);
    }
    if (extensions.peer_card_verification_code != nullptr) {
        std::cout
            << ",\"peer_card_verification_code\":"
            << json_quote(*extensions.peer_card_verification_code);
    }
    if (extensions.admission != nullptr) {
        const auto& admission = *extensions.admission;
        std::cout
            << ",\"peer_trust_created\":"
            << json_bool(admission.peer_trust_created)
            << ",\"membership_changed\":"
            << json_bool(admission.membership_changed)
            << ",\"membership_state_generation\":"
            << admission.membership_state_generation
            << ",\"membership_policy_epoch\":"
            << admission.membership_policy_epoch
            << ",\"membership_entry_count\":"
            << admission.membership_entry_count
            << ",\"membership_chain_digest\":"
            << json_quote(admission.membership_chain_digest);
    }
    if (extensions.state_directory != nullptr) {
        std::cout
            << ",\"state_directory\":"
            << json_quote(extensions.state_directory->generic_string());
    }
    if (extensions.files_root != nullptr) {
        std::cout
            << ",\"files_root\":"
            << json_quote(extensions.files_root->generic_string());
    }
    if (extensions.catalog_path != nullptr) {
        std::cout
            << ",\"catalog_path\":"
            << json_quote(extensions.catalog_path->generic_string());
    }
    if (extensions.initial_files_mode != nullptr) {
        std::cout
            << ",\"initial_files\":"
            << json_quote(*extensions.initial_files_mode);
    }
    if (extensions.deployment_disposition != nullptr) {
        std::cout
            << ",\"deployment_disposition\":"
            << json_quote(*extensions.deployment_disposition);
    }
    if (extensions.catalog_disposition != nullptr) {
        std::cout
            << ",\"catalog_disposition\":"
            << json_quote(*extensions.catalog_disposition);
    }
    if (extensions.initial_local_published_count != nullptr) {
        std::cout
            << ",\"initial_local_published\":"
            << *extensions.initial_local_published_count;
    }
    if (extensions.initial_catalog_entry_count != nullptr) {
        std::cout
            << ",\"initial_catalog_entry_count\":"
            << *extensions.initial_catalog_entry_count;
    }
    if (extensions.ready_to_start) {
        std::cout
            << ",\"ready_to_start\":true"
            << ",\"systemd_start_command\":"
            << json_quote(
                   "systemctl --user enable --now " + layout.systemd_unit);
    }
    std::cout << "}\n";
}

[[nodiscard]] anonsync::SyncLocalShareInitialFilesPolicy
required_local_share_initial_files_policy_or_throw(const Options& options) {
    const std::string selected = options.one("initial-files");
    if (selected == "empty") {
        return anonsync::SyncLocalShareInitialFilesPolicy::RequireEmpty;
    }
    if (selected == "adopt-existing") {
        return anonsync::SyncLocalShareInitialFilesPolicy::AdoptExisting;
    }
    throw std::invalid_argument(
        "--initial-files must be empty or adopt-existing");
}

[[nodiscard]] anonsync::SyncLocalShareSetupRequest
local_share_setup_request_from_options(
    const Options& options,
    std::optional<std::string> folder_id,
    anonsync::SyncLocalShareInitialFilesPolicy initial_files_policy) {
    return {
        .instance = options.one("instance"),
        .state_directory = require_absolute_path(
            options.one("state-directory"), "--state-directory"),
        .files_root = require_absolute_path(
            options.one("files-root"), "--files-root"),
        .home_directory = required_environment_directory_or_throw("HOME"),
        .folder_id = std::move(folder_id),
        .local_device_id = options.has("local-device")
            ? std::optional<std::string>(options.one("local-device"))
            : std::nullopt,
        .local_epoch = optional_uint64(options, "local-epoch"),
        .max_payload_bytes = optional_uint64(options, "max-payload-bytes"),
        .initial_files_policy = initial_files_policy,
        .folder_limit_overrides =
            local_share_folder_limit_overrides_from_options(options),
    };
}

void append_local_share_creation_json(
    std::ostream& output,
    const anonsync::SyncLocalShareSetupResult& created) {
    const auto& prepared = created.layout_preparation;
    const auto& layout = prepared.layout;
    const auto& deployment = created.deployment;
    const auto& pass = created.initial_pass;
    const auto& identity = created.identity;
    output
        << ",\"instance\":" << json_quote(layout.instance)
        << ",\"state_directory\":"
        << json_quote(layout.state_directory.generic_string())
        << ",\"state_directory_disposition\":"
        << json_quote(
               anonsync::sync_local_share_directory_disposition_name(
                   prepared.state_directory_disposition))
        << ",\"payload_root\":"
        << json_quote(layout.payload_root.generic_string())
        << ",\"payload_root_disposition\":"
        << json_quote(
               anonsync::sync_local_share_directory_disposition_name(
                   prepared.payload_root_disposition))
        << ",\"initial_files\":"
        << json_quote(
               anonsync::sync_local_share_initial_files_policy_name(
                   created.initial_files_policy))
        << ",\"deployment_disposition\":"
        << json_quote(
               anonsync::sync_local_share_deployment_disposition_name(
                   created.deployment_disposition))
        << ",\"manifest_path\":"
        << json_quote(layout.manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(deployment.deployment_id)
        << ",\"deployment_manifest_digest\":"
        << json_quote(deployment.manifest_digest)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"max_payload_bytes\":" << deployment.max_payload_bytes
        << ",\"files_root\":"
        << json_quote(layout.files_root.generic_string())
        << ",\"catalog_path\":"
        << json_quote(created.catalog_path.generic_string())
        << ",\"catalog_disposition\":"
        << json_quote(
               anonsync::sync_local_share_catalog_disposition_name(
                   created.catalog_disposition))
        << ",\"catalog_generation_before\":"
        << created.catalog_before.state_generation
        << ",\"catalog_generation_after\":"
        << created.catalog_after.state_generation
        << ",\"catalog_entry_count_before\":"
        << created.catalog_before.entries.size()
        << ",\"catalog_entry_count_after\":"
        << created.catalog_after.entries.size()
        << ",\"replica_generation_before\":"
        << created.replica_before.state_generation
        << ",\"replica_generation_after\":"
        << created.replica_after.state_generation
        << ",\"initial_pass\":{\"visited_entries\":"
        << pass.traversal.visited_entry_count
        << ",\"visited_directories\":"
        << pass.traversal.visited_directory_count
        << ",\"regular_files\":"
        << pass.traversal.regular_file_count
        << ",\"ignored_symbolic_links\":"
        << pass.traversal.ignored_symbolic_link_count
        << ",\"ignored_special_files\":"
        << pass.traversal.ignored_special_file_count
        << ",\"ignored_internal_artifacts\":"
        << pass.traversal.ignored_internal_artifact_count
        << ",\"metadata_only_regular_files\":"
        << pass.traversal.metadata_only_regular_file_count
        << ",\"metadata_only_regular_file_logical_bytes\":"
        << pass.traversal.metadata_only_regular_file_logical_bytes
        << ",\"metadata_only_pruned_directories\":"
        << pass.traversal.metadata_only_pruned_directory_count
        << ",\"classified_regular_file_bytes\":"
        << pass.traversal.classified_regular_file_bytes
        << ",\"local_scan_epoch\":" << pass.local_scan_epoch
        << ",\"completed_local_scan_epoch\":"
        << json_bool(pass.completed_local_scan_epoch)
        << ",\"restarted_local_scan_epoch\":"
        << json_bool(pass.restarted_local_scan_epoch)
        << ",\"local_scan_seen_path_count\":"
        << pass.local_scan_seen_path_count
        << ",\"local_scan_resume_after_path\":"
        << json_quote(pass.local_scan_resume_after_path)
        << ",\"local_scan_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_traversal_stop_reason_name(
                   pass.local_scan_stop_reason))
        << ",\"local_directory_enumeration_passes\":"
        << pass.local_directory_enumeration_pass_count
        << ",\"local_peak_buffered_directory_component_batch_count\":"
        << pass.local_peak_buffered_directory_component_batch_count
        << ",\"local_peak_simultaneously_buffered_directory_component_count\":"
        << pass.local_peak_simultaneously_buffered_directory_component_count
        << ",\"used_idle_fast_path\":"
        << json_bool(pass.used_idle_fast_path)
        << ",\"payload_snapshot_handoffs\":"
        << pass.payload_snapshot_handoff_count
        << ",\"payload_snapshot_handoff_entries\":"
        << pass.payload_snapshot_handoff_entry_count
        << ",\"payload_snapshot_observations\":"
        << pass.payload_snapshot_observation_count
        << ",\"payload_snapshot_observed_entries\":"
        << pass.payload_snapshot_observed_entry_count
        << ",\"exact_local_file_bytes\":"
        << pass.exact_local_file_bytes
        << ",\"payload_mutation_batches\":"
        << pass.payload_mutation_batch_count
        << ",\"payload_mutation_full_scans\":"
        << pass.payload_mutation_full_scan_count
        << ",\"payload_mutation_scan_hashed_entries\":"
        << pass.payload_mutation_scan_hashed_entry_count
        << ",\"payload_mutation_scan_hashed_bytes\":"
        << pass.payload_mutation_scan_hashed_bytes
        << ",\"payload_mutation_scan_reused_entries\":"
        << pass.payload_mutation_scan_reused_entry_count
        << ",\"payload_mutation_scan_reused_bytes\":"
        << pass.payload_mutation_scan_reused_bytes
        << ",\"payload_mutation_scan_process_reused_entries\":"
        << pass.payload_mutation_scan_process_reused_entry_count
        << ",\"payload_mutation_scan_process_reused_bytes\":"
        << pass.payload_mutation_scan_process_reused_bytes
        << ",\"payload_mutation_scan_durable_reused_entries\":"
        << pass.payload_mutation_scan_durable_reused_entry_count
        << ",\"payload_mutation_scan_durable_reused_bytes\":"
        << pass.payload_mutation_scan_durable_reused_bytes
        << ",\"payload_mutation_puts\":"
        << pass.payload_mutation_put_count
        << ",\"payload_mutation_source_bytes\":"
        << pass.payload_mutation_source_bytes
        << ",\"payload_mutation_work_bytes\":"
        << pass.payload_mutation_work_bytes
        << ",\"payload_mutation_peak_batch_puts\":"
        << pass.payload_mutation_peak_batch_put_count
        << ",\"payload_mutation_peak_batch_work_bytes\":"
        << pass.payload_mutation_peak_batch_work_bytes
        << ",\"payload_mutation_inserted\":"
        << pass.payload_mutation_inserted_count
        << ",\"payload_mutation_already_present\":"
        << pass.payload_mutation_already_present_count
        << ",\"local_published\":" << pass.local_published_count
        << ",\"local_identity_preserving_renames\":"
        << pass.local_identity_preserving_rename_count
        << ",\"local_adopted_visible\":"
        << pass.local_adopted_visible_count
        << ",\"local_catalog_no_op\":"
        << pass.local_catalog_no_op_count
        << ",\"local_catalog_refreshed\":"
        << pass.local_catalog_refreshed_count
        << ",\"remote_applied\":" << pass.remote_applied_count
        << ",\"remote_apply_operations\":"
        << pass.remote_apply_operation_count
        << ",\"remote_metadata_only_files\":"
        << pass.remote_metadata_only_file_count
        << ",\"remote_metadata_only_already_absent_files\":"
        << pass.remote_metadata_only_already_absent_file_count
        << ",\"remote_targeted_catalog_path_cutpoints\":"
        << pass.remote_targeted_catalog_path_cutpoint_count
        << ",\"remote_targeted_replica_path_cutpoints\":"
        << pass.remote_targeted_replica_path_cutpoint_count
        << ",\"remote_metadata_only_dematerialization_attempts\":"
        << pass.remote_metadata_only_dematerialization_attempt_count
        << ",\"remote_metadata_only_dematerialized_files\":"
        << pass.remote_metadata_only_dematerialized_file_count
        << ",\"remote_metadata_only_dematerialized_bytes\":"
        << pass.remote_metadata_only_dematerialized_bytes
        << ",\"remote_metadata_only_dematerialization_blocked_files\":"
        << pass.remote_metadata_only_dematerialization_blocked_file_count
        << ",\"remote_metadata_only_dematerialization_payload_unavailable\":"
        << pass.remote_metadata_only_dematerialization_payload_unavailable_count
        << ",\"local_metadata_only_absence_suppressions\":"
        << pass.local_metadata_only_absence_suppressed_count
        << ",\"local_selection_change_absence_suppressions\":"
        << pass.local_selection_change_absence_suppressed_count
        << ",\"remote_inspected_paths\":"
        << pass.remote_inspected_path_count
        << ",\"remote_acknowledged_paths\":"
        << pass.remote_acknowledged_path_count
        << ",\"deferred_remote_inspection_paths\":"
        << pass.deferred_remote_inspection_path_count
        << ",\"remote_inspection_sweep_started_after_path\":"
        << json_quote(pass.remote_inspection_sweep_started_after_path)
        << ",\"remote_inspection_sweep_seen_path_count\":"
        << pass.remote_inspection_sweep_seen_path_count
        << ",\"completed_remote_inspection_sweep\":"
        << json_bool(pass.completed_remote_inspection_sweep)
        << ",\"remote_inspection_sweep_had_unresolved_paths\":"
        << json_bool(pass.remote_inspection_sweep_had_unresolved_paths)
        << ",\"remote_inspection_terminal_cutpoint_reproved\":"
        << json_bool(pass.remote_inspection_terminal_cutpoint_reproved)
        << ",\"remote_inspection_terminal_catalog_digest\":"
        << json_quote(pass.remote_inspection_terminal_catalog_digest)
        << ",\"remote_inspection_terminal_visible_state_digest\":"
        << json_quote(
               pass.remote_inspection_terminal_visible_state_digest)
        << ",\"remote_payload_snapshot_observations\":"
        << pass.remote_payload_snapshot_observation_count
        << ",\"remote_payload_snapshot_entries\":"
        << pass.remote_payload_snapshot_entry_count
        << ",\"remote_targeted_payload_accesses\":"
        << pass.remote_targeted_payload_access_count
        << ",\"remote_targeted_payload_probes\":"
        << pass.remote_targeted_payload_probe_count
        << ",\"remote_targeted_payload_selections\":"
        << pass.remote_targeted_payload_selection_count
        << ",\"remote_targeted_payload_selected_bytes\":"
        << pass.remote_targeted_payload_selected_bytes
        << ",\"deferred_remote_payload_candidates\":"
        << pass.deferred_remote_payload_candidate_count
        << ",\"remote_apply_revalidated_catalog_predecessors\":"
        << pass.remote_apply_revalidated_catalog_predecessor_count
        << ",\"remote_apply_started_after_path\":"
        << json_quote(pass.remote_apply_started_after_path)
        << ",\"remote_apply_resume_after_path\":"
        << json_quote(pass.remote_apply_resume_after_path)
        << ",\"remote_apply_wrapped_projection\":"
        << json_bool(pass.remote_apply_wrapped_projection)
        << ",\"deferred_remote_apply_candidates\":"
        << pass.deferred_remote_apply_candidate_count
        << ",\"remote_apply_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_remote_apply_stop_reason_name(
                   pass.remote_apply_stop_reason))
        << "}"
        << ",\"identity_directory\":"
        << json_quote(identity.layout.identity_directory.generic_string())
        << ",\"private_key_path\":"
        << json_quote(identity.layout.private_key_path.generic_string())
        << ",\"certificate_path\":"
        << json_quote(identity.layout.certificate_path.generic_string())
        << ",\"pairing_card_path\":"
        << json_quote(identity.layout.pairing_card_path.generic_string())
        << ",\"private_key_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   identity.private_key_disposition))
        << ",\"certificate_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   identity.certificate_disposition))
        << ",\"pairing_card_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   identity.pairing_card_disposition))
        << ",\"pairing_card_sha256\":"
        << json_quote(created.pairing_card_sha256)
        << ",\"pairing_verification_code\":"
        << json_quote(created.pairing_verification_code)
        << ",\"limits\":{\"maximum_entries\":"
        << created.folder_limits.maximum_entries
        << ",\"maximum_regular_files\":"
        << created.folder_limits.maximum_regular_files
        << ",\"maximum_file_bytes\":"
        << created.folder_limits.maximum_file_bytes
        << ",\"maximum_total_file_bytes\":"
        << created.folder_limits.maximum_total_file_bytes
        << ",\"maximum_relative_path_bytes\":"
        << created.folder_limits.maximum_relative_path_bytes
        << ",\"maximum_directory_depth\":"
        << created.folder_limits.maximum_directory_depth
        << ",\"maximum_remote_paths\":"
        << created.folder_limits.maximum_remote_paths
        << ",\"maximum_remote_inspection_paths\":"
        << created.folder_limits.maximum_remote_inspection_paths
        << ",\"maximum_remote_apply_operations\":"
        << created.folder_limits.maximum_remote_apply_operations << "}";
}

int command_share_create(const Options& options) {
    options.require_only({
        "instance", "state-directory", "files-root", "folder",
        "local-device", "local-epoch", "max-payload-bytes",
        "maximum-entries", "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths"});

    anonsync::SyncLocalShareSetupRequest request =
        local_share_setup_request_from_options(
            options,
            options.has("folder")
                ? std::optional<std::string>(options.one("folder"))
                : std::nullopt,
            anonsync::SyncLocalShareInitialFilesPolicy::AdoptExisting);
    const anonsync::SyncLocalShareSetupResult created =
        anonsync::create_or_resume_sync_local_share_or_throw(
            std::move(request), "anonsync_sync share-create");
    std::cout
        << "{\"command\":\"share-create\""
        << ",\"terminal_class\":\"ready_to_pair\"";
    append_local_share_creation_json(std::cout, created);
    std::cout << ",\"ready_to_link\":true}\n";
    return 0;
}

int command_identity_create(const Options& options) {
    options.require_only({"instance", "manifest"});
    const std::string instance = options.one("instance");
    const anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            require_absolute_path(options.one("manifest"), "--manifest"),
            "anonsync_sync identity-create manifest");
    const anonsync::SyncLinkedPeerIdentityLayout layout =
        anonsync::prepare_sync_linked_peer_identity_layout_or_throw(
            instance, required_environment_directory_or_throw("HOME"),
            "anonsync_sync identity-create layout");
    const anonsync::SyncLinkedPeerIdentityCreationResult created =
        anonsync::create_or_resume_sync_linked_peer_identity_or_throw(
            layout, deployment, "anonsync_sync linked-peer identity");
    const std::string pairing_card_sha256 =
        anonsync::sync_linked_peer_card_sha256_or_throw(
            created.card, "anonsync_sync local pairing-card fingerprint");
    const std::string pairing_verification_code =
        anonsync::sync_linked_peer_card_verification_code_or_throw(
            created.card,
            "anonsync_sync local pairing-card verification code");

    std::cout
        << "{\"command\":\"identity-create\","
           "\"terminal_class\":\"completed\","
           "\"instance\":"
        << json_quote(created.layout.instance)
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"identity_directory\":"
        << json_quote(created.layout.identity_directory.generic_string())
        << ",\"private_key_path\":"
        << json_quote(created.layout.private_key_path.generic_string())
        << ",\"certificate_path\":"
        << json_quote(created.layout.certificate_path.generic_string())
        << ",\"pairing_card_path\":"
        << json_quote(created.layout.pairing_card_path.generic_string())
        << ",\"peer_trust_path\":"
        << json_quote(created.layout.peer_trust_path.generic_string())
        << ",\"spki_sha256\":" << json_quote(created.card.spki_sha256)
        << ",\"pairing_card_sha256\":"
        << json_quote(pairing_card_sha256)
        << ",\"pairing_verification_code\":"
        << json_quote(pairing_verification_code)
        << ",\"private_key_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   created.private_key_disposition))
        << ",\"certificate_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   created.certificate_disposition))
        << ",\"pairing_card_disposition\":"
        << json_quote(
               anonsync::sync_linked_peer_identity_file_disposition_name(
                   created.pairing_card_disposition))
        << ",\"pairing_card_is_public_only\":true}\n";
    return 0;
}

int command_provision(const Options& options) {
    options.require_only({
        "instance", "manifest", "remote-device", "remote-epoch",
        "remote-spki", "certificate", "private-key", "ca-file",
        "timeout-seconds", "max-runtime-seconds", "max-round-trips",
        "max-source-resets", "transport", "address", "port",
        "onion-address", "onion-port", "tor-socks-address",
        "tor-socks-port", "tor-isolation-token", "i2p-sam-address",
        "i2p-sam-port", "i2p-destination", "i2p-session-id",
        "i2p-private-destination-file", "i2p-inbound-quantity",
        "i2p-outbound-quantity", "ingress", "bind-address",
        "listen-port", "ingress-onion-address", "ingress-onion-port",
        "ingress-i2p-sam-address", "ingress-i2p-sam-port",
        "ingress-i2p-session-id",
        "ingress-i2p-private-destination-file",
        "ingress-i2p-inbound-quantity",
        "ingress-i2p-outbound-quantity", "maximum-entries",
        "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes",
        "maximum-relative-path-bytes", "maximum-directory-depth",
        "maximum-remote-paths", "maximum-remote-inspection-paths",
        "scan-interval-seconds",
        "retry-initial-seconds", "retry-maximum-seconds",
        "accept-poll-milliseconds", "inbound-timeout-seconds",
        "inbound-max-round-trips", "ingress-timeout-seconds",
        "max-cycles", "max-service-runtime-seconds"});

    const std::string instance = options.one("instance");
    anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            require_absolute_path(options.one("manifest"), "--manifest"),
            "anonsync_sync provision manifest");
    anonsync::SyncReplicaTlsPeerPolicy expected_peer =
        expected_peer_from_options_or_throw(options);
    const std::string stable_scope = linked_service_default_scope(
        instance, deployment, expected_peer);
    anonsync::SyncReplicaStreamRoute route =
        stream_route_from_options_or_throw(options, stable_scope);
    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(route);
    ProvisioningIngressSelection ingress =
        provisioning_ingress_from_options_or_throw(options, stable_scope);
    const anonsync::SyncReplicaPeerIngressKind ingress_kind =
        anonsync::sync_replica_peer_ingress_kind(ingress.ingress);
    anonsync::SyncReplicaPeerServiceLimits limits =
        peer_service_limits_from_options_or_throw(
            options, deployment, route_kind, ingress_kind);
    anonsync::SyncReplicaPeerServiceTlsFiles tls{
        require_existing_regular_file(
            options.one("certificate"), "--certificate"),
        require_existing_regular_file(
            options.one("private-key"), "--private-key"),
        require_existing_regular_file(
            options.one("ca-file"), "--ca-file")};
    // This is intentionally before user-layout creation. A deterministic TLS
    // permission failure must not leave an empty runtime/configuration tree,
    // and the provisioning owner repeats the same admission before publish.
    anonsync::validate_sync_replica_peer_service_tls_files_or_throw(
        tls, "anonsync_sync provision TLS files");

    // Provisioning must not publish a launch document whose TLS material only
    // fails after systemd starts it. Exercise both profiles before any durable
    // configuration file is created.
    SslContextOwner client_context = load_tls_context_or_throw(
        tls.certificate, tls.private_key, tls.ca_file, false,
        "anonsync_sync provision client TLS context");
    SslContextOwner server_context = load_tls_context_or_throw(
        tls.certificate, tls.private_key, tls.ca_file, true,
        "anonsync_sync provision server TLS context");
    (void)client_context;
    (void)server_context;

    const anonsync::SyncLinkedPeerUserLayout layout =
        anonsync::prepare_sync_linked_peer_user_layout_or_throw(
            instance,
            required_environment_directory_or_throw("HOME"),
            required_environment_directory_or_throw("XDG_RUNTIME_DIR"),
            "anonsync_sync provision layout");

    anonsync::SyncReplicaPeerServiceLaunchConfiguration launch{
        .configuration_schema = std::string(
            anonsync::kSyncReplicaLinkedPeerServiceConfigurationSchema),
        .configuration_path = layout.configuration_path,
        .deployment = std::move(deployment),
        .expected_peer = std::move(expected_peer),
        .tls = std::move(tls),
        .route = std::move(route),
        .ingress = std::move(ingress.ingress),
        .listen_endpoint = std::move(ingress.listen_endpoint),
        .status_socket_path = layout.status_socket_path,
        .limits = std::move(limits),
        .maximum_cycles = optional_uint64(options, "max-cycles"),
        .maximum_service_runtime_seconds =
            optional_uint64(options, "max-service-runtime-seconds")};

    anonsync::SyncReplicaPeerServiceProvisioningSourceFiles source_files;
    if (options.has("i2p-private-destination-file")) {
        source_files.outbound_i2p_private_destination_file =
            require_absolute_path(
                options.one("i2p-private-destination-file"),
                "--i2p-private-destination-file");
    }
    source_files.inbound_i2p_private_destination_file =
        std::move(ingress.i2p_private_destination_file);

    const anonsync::SyncReplicaPeerServiceProvisioningResult provisioned =
        anonsync::provision_sync_replica_linked_peer_service_configuration_or_throw(
            std::move(launch), std::move(source_files),
            "anonsync_sync linked-peer provisioning");
    emit_linked_peer_provisioning_summary(
        "provision", layout, provisioned);
    return 0;
}


struct LinkedPeerLinkWorkflowResult final {
    anonsync::SyncLinkedPeerIdentityCreationResult identity;
    std::string local_pairing_card_sha256;
    std::string local_pairing_verification_code;
    anonsync::SyncLinkedPeerUserLayout layout;
    anonsync::SyncLinkedPeerAdmissionResult admission;
    anonsync::SyncReplicaPeerServiceProvisioningResult provisioned;
};

[[nodiscard]] LinkedPeerLinkWorkflowResult
link_existing_local_share_to_peer_or_throw(
    const Options& options,
    std::string instance,
    anonsync::SyncReplicaDeploymentManifest deployment,
    const PeerCardSelection& peer,
    anonsync::SyncReplicaStreamRoute route,
    ProvisioningIngressSelection ingress,
    std::string_view command_name,
    bool allow_exact_configuration_resume) {
    const std::string label =
        "anonsync_sync " + std::string(command_name);
    if (peer.card.folder_id != deployment.folder_id) {
        throw std::invalid_argument(
            "linked peer card folder does not match the local deployment");
    }
    if (peer.card.actor.device_id == deployment.local_actor.device_id) {
        throw std::invalid_argument(
            "linked peer card names the local device");
    }

    const anonsync::SyncReplicaStreamRouteKind route_kind =
        anonsync::sync_replica_stream_route_kind(route);
    const anonsync::SyncReplicaPeerIngressKind ingress_kind =
        anonsync::sync_replica_peer_ingress_kind(ingress.ingress);
    anonsync::SyncReplicaPeerServiceLimits limits =
        peer_service_limits_from_options_or_throw(
            options, deployment, route_kind, ingress_kind);

    anonsync::SyncReplicaPeerServiceProvisioningSourceFiles source_files;
    if (options.has("i2p-private-destination-file")) {
        source_files.outbound_i2p_private_destination_file =
            require_absolute_path(
                options.one("i2p-private-destination-file"),
                "--i2p-private-destination-file");
    }
    source_files.inbound_i2p_private_destination_file =
        ingress.i2p_private_destination_file;

    const fs::path home = required_environment_directory_or_throw("HOME");
    const anonsync::SyncLinkedPeerIdentityLayout identity_layout =
        anonsync::prepare_sync_linked_peer_identity_layout_or_throw(
            instance, home, label + " identity layout");
    (void)require_existing_regular_file(
        identity_layout.private_key_path.string(),
        "linked-peer local private key");
    (void)require_existing_regular_file(
        identity_layout.certificate_path.string(),
        "linked-peer local certificate");
    (void)require_existing_regular_file(
        identity_layout.pairing_card_path.string(),
        "linked-peer local pairing card");
    anonsync::SyncLinkedPeerIdentityCreationResult identity =
        anonsync::create_or_resume_sync_linked_peer_identity_or_throw(
            identity_layout, deployment, label + " local identity");
    const std::string local_pairing_card_sha256 =
        anonsync::sync_linked_peer_card_sha256_or_throw(
            identity.card, label + " local pairing-card fingerprint");
    const std::string local_pairing_verification_code =
        anonsync::sync_linked_peer_card_verification_code_or_throw(
            identity.card,
            label + " local pairing-card verification code");

    const anonsync::SyncLinkedPeerUserLayout layout =
        anonsync::prepare_sync_linked_peer_user_layout_or_throw(
            instance, home,
            required_environment_directory_or_throw("XDG_RUNTIME_DIR"),
            label + " service layout");
    // The legacy link command remains create-new. share-join uses exact resume
    // so a lost terminal response after durable configuration publication can
    // be retried without replacing or broadening the installed service.
    if (!allow_exact_configuration_resume) {
        anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
            layout.configuration_path, label + " configuration preflight");
    }

    anonsync::SyncReplicaPeerServiceTlsFiles tls{
        identity.layout.certificate_path,
        identity.layout.private_key_path,
        identity.layout.peer_trust_path};
    anonsync::SyncReplicaPeerServiceLaunchConfiguration launch{
        .configuration_schema = std::string(
            anonsync::kSyncReplicaLinkedPeerServiceConfigurationSchema),
        .configuration_path = layout.configuration_path,
        .deployment = deployment,
        .expected_peer = {
            .actor = peer.card.actor,
            .spki_sha256 = peer.card.spki_sha256,
        },
        .tls = tls,
        .route = std::move(route),
        .ingress = std::move(ingress.ingress),
        .listen_endpoint = std::move(ingress.listen_endpoint),
        .status_socket_path = layout.status_socket_path,
        .limits = std::move(limits),
        .maximum_cycles = optional_uint64(options, "max-cycles"),
        .maximum_service_runtime_seconds =
            optional_uint64(options, "max-service-runtime-seconds")};

    // A present immutable service document is a stronger preflight boundary
    // than peer/folder matching alone. Prove exact route, ingress, credentials,
    // limits, and source-file bindings before membership can change. An absent
    // document is still reserved by the earlier no-replace path check.
    if (allow_exact_configuration_resume &&
        regular_file_is_present_or_throw(
            layout.configuration_path,
            label + " existing service configuration")) {
        const auto inspection =
            anonsync::inspect_sync_replica_linked_peer_service_configuration_or_throw(
                launch, source_files,
                label + " existing service configuration");
        if (inspection !=
            anonsync::SyncReplicaPeerServiceConfigurationInspection::
                ExistingExact) {
            throw std::logic_error(
                label + " existing service configuration was not exact");
        }
    }

    const anonsync::SyncLinkedPeerAdmissionResult admission =
        anonsync::admit_sync_linked_peer_card_or_throw(
            deployment, peer.card, identity.layout.peer_trust_path,
            label + " linked-peer admission");

    anonsync::validate_sync_replica_peer_service_tls_files_or_throw(
        tls, label + " TLS files");
    SslContextOwner client_context = load_tls_context_or_throw(
        tls.certificate, tls.private_key, tls.ca_file, false,
        label + " client TLS context");
    SslContextOwner server_context = load_tls_context_or_throw(
        tls.certificate, tls.private_key, tls.ca_file, true,
        label + " server TLS context");
    (void)client_context;
    (void)server_context;

    anonsync::SyncReplicaPeerServiceProvisioningResult provisioned =
        allow_exact_configuration_resume
            ? anonsync::
                  provision_or_resume_sync_replica_linked_peer_service_configuration_or_throw(
                      std::move(launch), std::move(source_files),
                      label + " provisioning")
            : anonsync::
                  provision_sync_replica_linked_peer_service_configuration_or_throw(
                      std::move(launch), std::move(source_files),
                      label + " provisioning");
    return {
        .identity = std::move(identity),
        .local_pairing_card_sha256 = local_pairing_card_sha256,
        .local_pairing_verification_code =
            local_pairing_verification_code,
        .layout = layout,
        .admission = admission,
        .provisioned = std::move(provisioned),
    };
}


int command_link(const Options& options) {
    options.require_only({
        "instance", "manifest", "peer-card", "peer-card-sha256",
        "timeout-seconds",
        "max-runtime-seconds", "max-round-trips", "max-source-resets",
        "transport", "address", "port", "onion-address", "onion-port",
        "tor-socks-address", "tor-socks-port", "tor-isolation-token",
        "i2p-sam-address", "i2p-sam-port", "i2p-destination",
        "i2p-session-id", "i2p-private-destination-file",
        "i2p-inbound-quantity", "i2p-outbound-quantity", "ingress",
        "bind-address", "listen-port", "ingress-onion-address",
        "ingress-onion-port", "ingress-i2p-sam-address",
        "ingress-i2p-sam-port", "ingress-i2p-session-id",
        "ingress-i2p-private-destination-file",
        "ingress-i2p-inbound-quantity", "ingress-i2p-outbound-quantity",
        "maximum-entries", "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths", "scan-interval-seconds", "retry-initial-seconds",
        "retry-maximum-seconds", "accept-poll-milliseconds",
        "inbound-timeout-seconds", "inbound-max-round-trips",
        "ingress-timeout-seconds", "max-cycles",
        "max-service-runtime-seconds"});

    const std::string instance = options.one("instance");
    const PeerCardSelection peer = peer_card_from_options_or_throw(
        options, false, "anonsync_sync link");
    anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            require_absolute_path(options.one("manifest"), "--manifest"),
            "anonsync_sync link manifest");
    const anonsync::SyncReplicaTlsPeerPolicy peer_policy{
        .actor = peer.card.actor,
        .spki_sha256 = peer.card.spki_sha256,
    };
    const std::string stable_scope = linked_service_default_scope(
        instance, deployment, peer_policy);
    anonsync::SyncReplicaStreamRoute route =
        stream_route_from_options_or_throw(options, stable_scope);
    ProvisioningIngressSelection ingress =
        provisioning_ingress_from_options_or_throw(options, stable_scope);

    const LinkedPeerLinkWorkflowResult linked =
        link_existing_local_share_to_peer_or_throw(
            options, instance, std::move(deployment), peer,
            std::move(route), std::move(ingress), "link", false);
    emit_linked_peer_provisioning_summary(
        "link", linked.layout, linked.provisioned,
        LinkedPeerProvisioningSummaryExtensions{
            .identity = &linked.identity,
            .local_pairing_card_sha256 =
                &linked.local_pairing_card_sha256,
            .local_pairing_verification_code =
                &linked.local_pairing_verification_code,
            .peer_card_path = &peer.path,
            .peer_card_sha256 = &peer.sha256,
            .peer_card_verification_code = &peer.verification_code,
            .peer_card_sha256_pinned = peer.sha256_pinned,
            .admission = &linked.admission,
        });
    return 0;
}


int command_share_join(const Options& options) {
    options.require_only({
        "instance", "state-directory", "files-root", "initial-files",
        "local-device", "local-epoch", "max-payload-bytes",
        "peer-card", "peer-card-sha256", "timeout-seconds",
        "max-runtime-seconds", "max-round-trips", "max-source-resets",
        "transport", "address", "port", "onion-address", "onion-port",
        "tor-socks-address", "tor-socks-port", "tor-isolation-token",
        "i2p-sam-address", "i2p-sam-port", "i2p-destination",
        "i2p-session-id", "i2p-private-destination-file",
        "i2p-inbound-quantity", "i2p-outbound-quantity", "ingress",
        "bind-address", "listen-port", "ingress-onion-address",
        "ingress-onion-port", "ingress-i2p-sam-address",
        "ingress-i2p-sam-port", "ingress-i2p-session-id",
        "ingress-i2p-private-destination-file",
        "ingress-i2p-inbound-quantity", "ingress-i2p-outbound-quantity",
        "maximum-entries", "maximum-regular-files", "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths", "scan-interval-seconds", "retry-initial-seconds",
        "retry-maximum-seconds", "accept-poll-milliseconds",
        "inbound-timeout-seconds", "inbound-max-round-trips",
        "ingress-timeout-seconds", "max-cycles",
        "max-service-runtime-seconds"});

    const std::string instance = options.one("instance");
    const anonsync::SyncLocalShareInitialFilesPolicy initial_files_policy =
        required_local_share_initial_files_policy_or_throw(options);
    const PeerCardSelection peer = peer_card_from_options_or_throw(
        options, true, "anonsync_sync share-join");
    if (options.has("local-device") &&
        options.one("local-device") == peer.card.actor.device_id) {
        throw std::invalid_argument(
            "--local-device must not name the peer card device");
    }

    // Validate every route/ingress field and reserve the create-new service
    // namespace before mutating replica membership or creating local share
    // state. The later link owner repeats the exact no-replace preflight.
    (void)stream_route_from_options_or_throw(
        options, "share-join-option-preflight");
    (void)provisioning_ingress_from_options_or_throw(
        options, "share-join-option-preflight");
    const fs::path home = required_environment_directory_or_throw("HOME");
    const anonsync::SyncLinkedPeerUserLayout preflight_layout =
        anonsync::prepare_sync_linked_peer_user_layout_or_throw(
            instance, home,
            required_environment_directory_or_throw("XDG_RUNTIME_DIR"),
            "anonsync_sync share-join service preflight layout");
    const bool configuration_was_present = regular_file_is_present_or_throw(
        preflight_layout.configuration_path,
        "anonsync_sync share-join configuration preflight");
    if (configuration_was_present) {
        const auto existing =
            anonsync::read_sync_replica_linked_peer_service_configuration_or_throw(
                preflight_layout.configuration_path,
                "anonsync_sync share-join existing configuration preflight");
        if (existing.deployment.folder_id != peer.card.folder_id ||
            existing.expected_peer.actor != peer.card.actor ||
            existing.expected_peer.spki_sha256 != peer.card.spki_sha256) {
            throw std::runtime_error(
                "anonsync_sync share-join existing configuration conflicts "
                "with the pinned peer card");
        }
    } else {
        anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
            preflight_layout.configuration_path,
            "anonsync_sync share-join configuration preflight");
    }

    anonsync::SyncLocalShareSetupRequest local_request =
        local_share_setup_request_from_options(
            options, peer.card.folder_id, initial_files_policy);
    anonsync::SyncLocalShareSetupResult created =
        anonsync::create_or_resume_sync_local_share_or_throw(
            std::move(local_request),
            "anonsync_sync share-join local share");
    const anonsync::SyncReplicaTlsPeerPolicy peer_policy{
        .actor = peer.card.actor,
        .spki_sha256 = peer.card.spki_sha256,
    };
    const std::string stable_scope = linked_service_default_scope(
        instance, created.deployment, peer_policy);
    anonsync::SyncReplicaStreamRoute route =
        stream_route_from_options_or_throw(options, stable_scope);
    ProvisioningIngressSelection ingress =
        provisioning_ingress_from_options_or_throw(options, stable_scope);
    const LinkedPeerLinkWorkflowResult linked =
        link_existing_local_share_to_peer_or_throw(
            options, instance, created.deployment, peer,
            std::move(route), std::move(ingress), "share-join", true);

    const std::string initial_files_name =
        anonsync::sync_local_share_initial_files_policy_name(
            created.initial_files_policy);
    const std::string deployment_disposition =
        anonsync::sync_local_share_deployment_disposition_name(
            created.deployment_disposition);
    const std::string catalog_disposition =
        anonsync::sync_local_share_catalog_disposition_name(
            created.catalog_disposition);
    const std::uint64_t initial_catalog_entry_count =
        static_cast<std::uint64_t>(created.catalog_after.entries.size());
    emit_linked_peer_provisioning_summary(
        "share-join", linked.layout, linked.provisioned,
        LinkedPeerProvisioningSummaryExtensions{
            .identity = &linked.identity,
            .local_pairing_card_sha256 =
                &linked.local_pairing_card_sha256,
            .local_pairing_verification_code =
                &linked.local_pairing_verification_code,
            .peer_card_path = &peer.path,
            .peer_card_sha256 = &peer.sha256,
            .peer_card_verification_code = &peer.verification_code,
            .peer_card_sha256_pinned = peer.sha256_pinned,
            .admission = &linked.admission,
            .state_directory = &created.layout_preparation.layout.state_directory,
            .files_root = &created.layout_preparation.layout.files_root,
            .catalog_path = &created.catalog_path,
            .initial_files_mode = &initial_files_name,
            .deployment_disposition = &deployment_disposition,
            .catalog_disposition = &catalog_disposition,
            .initial_local_published_count =
                &created.initial_pass.local_published_count,
            .initial_catalog_entry_count =
                &initial_catalog_entry_count,
            .ready_to_start = true,
        },
        "ready_to_start");
    return 0;
}

int command_check_config(const Options& options) {
    options.require_only({"config"});
    const auto launch =
        anonsync::read_sync_replica_linked_peer_service_configuration_or_throw(
            require_absolute_path(options.one("config"), "--config"),
            "anonsync_sync linked-peer service configuration check");
    const auto route_kind = anonsync::sync_replica_stream_route_kind(
        launch.route);
    std::cout
        << "{\"command\":\"check-config\","
           "\"terminal_class\":\"completed\","
           "\"configuration_schema\":"
        << json_quote(launch.configuration_schema)
        << ",\"configuration_path\":"
        << json_quote(launch.configuration_path->generic_string())
        << ",\"manifest_path\":"
        << json_quote(launch.deployment.manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(launch.deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(launch.deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(launch.deployment.local_actor.device_id)
        << ",\"local_epoch\":" << launch.deployment.local_actor.epoch
        << ",\"remote_device_id\":"
        << json_quote(launch.expected_peer.actor.device_id)
        << ",\"remote_epoch\":" << launch.expected_peer.actor.epoch
        << ",\"transport\":"
        << json_quote(anonsync::sync_replica_stream_route_kind_name(route_kind))
        << ",\"ingress_transport\":"
        << json_quote(anonsync::sync_replica_peer_ingress_kind_name(
               anonsync::sync_replica_peer_ingress_kind(launch.ingress)));
    const bool numeric_listener_active =
        anonsync::sync_replica_peer_ingress_kind(launch.ingress) !=
        anonsync::SyncReplicaPeerIngressKind::I2pSamAccept;
    std::cout
        << ",\"numeric_listener_active\":"
        << json_bool(numeric_listener_active)
        << ",\"bind_address\":";
    if (numeric_listener_active) {
        std::cout << json_quote(launch.listen_endpoint.numeric_address);
    } else {
        std::cout << "null";
    }
    std::cout << ",\"listen_port\":";
    if (numeric_listener_active) {
        std::cout << launch.listen_endpoint.port;
    } else {
        std::cout << "null";
    }
    std::cout
        << ",\"status_socket\":"
        << json_quote(launch.status_socket_path->generic_string())
        << ",\"maximum_entries\":"
        << launch.limits.folder_limits.maximum_entries
        << ",\"maximum_regular_files\":"
        << launch.limits.folder_limits.maximum_regular_files
        << ",\"maximum_file_bytes\":"
        << launch.limits.folder_limits.maximum_file_bytes
        << ",\"maximum_remote_apply_operations\":"
        << launch.limits.folder_limits.maximum_remote_apply_operations
        << ",\"maximum_remote_inspection_paths\":"
        << launch.limits.folder_limits.maximum_remote_inspection_paths
        << ",\"stage_timeout_seconds\":"
        << launch.limits.stage_timeout_seconds
        << ",\"cycle_runtime_seconds\":"
        << launch.limits.cycle_runtime_seconds
        << ",\"network_step_horizon_seconds\":"
        << anonsync::
               sync_replica_peer_service_network_step_horizon_seconds_or_throw(
                   launch.limits, "anonsync_sync checked service horizon")
        << ",\"installed_service_maximum_network_step_seconds\":"
        << anonsync::kSyncReplicaInstalledServiceMaximumNetworkStepSeconds
        << ",\"installed_service_stop_timeout_seconds\":"
        << anonsync::kSyncReplicaInstalledServiceStopTimeoutSeconds
        << ",\"maximum_cycles\":";
    if (launch.maximum_cycles.has_value()) {
        std::cout << *launch.maximum_cycles;
    } else {
        std::cout << "null";
    }
    std::cout << ",\"maximum_service_runtime_seconds\":";
    if (launch.maximum_service_runtime_seconds.has_value()) {
        std::cout << *launch.maximum_service_runtime_seconds;
    } else {
        std::cout << "null";
    }
    std::cout << "}\n";
    return 0;
}

int command_status(const Options& options) {
    options.require_only({"socket", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout << anonsync::query_sync_local_status_socket_or_throw(
        socket_path, timeout_milliseconds,
        "anonsync_sync status") << '\n';
    return 0;
}

constexpr std::size_t kResourceMaximumProcesses = 256U;
constexpr std::uint64_t kResourceWatchMaximumSamples = 1024U;
constexpr std::uint64_t kResourceWatchMaximumIntervalMilliseconds =
    3'600'000U;
constexpr std::uint64_t kResourceWatchMaximumTimeoutMilliseconds =
    86'400'000U;

using ResourceClock = std::chrono::steady_clock;
using ResourceProcessIdentity =
    std::pair<std::uint64_t, std::uint64_t>;

[[nodiscard]] std::uint64_t checked_resource_add(
    std::uint64_t left,
    std::uint64_t right,
    std::string_view label) {
    if (left > std::numeric_limits<std::uint64_t>::max() - right) {
        throw std::overflow_error(std::string(label) + " overflow");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t checked_resource_delta(
    std::uint64_t first,
    std::uint64_t last,
    std::string_view label) {
    if (last < first) {
        throw std::runtime_error(
            std::string(label) + " decreased within one live process series");
    }
    return last - first;
}

[[nodiscard]] std::chrono::milliseconds resource_milliseconds_or_throw(
    std::uint64_t value,
    std::string_view label) {
    using Rep = std::chrono::milliseconds::rep;
    if (value > static_cast<std::uint64_t>(
                    std::numeric_limits<Rep>::max())) {
        throw std::overflow_error(std::string(label) + " overflows duration");
    }
    return std::chrono::milliseconds(static_cast<Rep>(value));
}

[[nodiscard]] ResourceClock::time_point resource_deadline_or_throw(
    ResourceClock::time_point started_at,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    const auto timeout = resource_milliseconds_or_throw(
        timeout_milliseconds, std::string(label) + " timeout");
    if (started_at > ResourceClock::time_point::max() - timeout) {
        throw std::overflow_error(std::string(label) + " deadline overflows");
    }
    return started_at + timeout;
}

[[nodiscard]] std::uint64_t resource_elapsed_milliseconds_or_throw(
    ResourceClock::time_point started_at,
    ResourceClock::time_point observed_at,
    std::string_view label) {
    if (observed_at < started_at) {
        throw std::runtime_error(
            std::string(label) + " steady clock moved backwards");
    }
    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        observed_at - started_at);
    if (elapsed.count() < 0) {
        throw std::runtime_error(
            std::string(label) + " produced a negative elapsed time");
    }
    return static_cast<std::uint64_t>(elapsed.count());
}

[[nodiscard]] std::vector<fs::path> resource_socket_paths_or_throw(
    const Options& options,
    std::string_view command) {
    const std::vector<std::string> selected = options.many("socket");
    if (selected.empty() || selected.size() > kResourceMaximumProcesses) {
        throw std::invalid_argument(
            std::string(command) +
            " requires between 1 and 256 --socket values");
    }
    std::vector<fs::path> sockets;
    sockets.reserve(selected.size());
    std::set<std::string> distinct_paths;
    for (const std::string& value : selected) {
        fs::path socket = require_absolute_path(value, "--socket");
        const std::string canonical = socket.generic_string();
        if (!distinct_paths.insert(canonical).second) {
            throw std::invalid_argument(
                std::string(command) +
                " received the same --socket path more than once");
        }
        sockets.push_back(std::move(socket));
    }
    return sockets;
}

struct ResourceTotals final {
    std::uint64_t rss_sum_kib = 0U;
    std::uint64_t pss_sum_kib = 0U;
    std::uint64_t pss_anon_sum_kib = 0U;
    std::uint64_t pss_file_sum_kib = 0U;
    std::uint64_t pss_shmem_sum_kib = 0U;
    std::uint64_t private_resident_sum_kib = 0U;
    std::uint64_t swap_pss_sum_kib = 0U;
    std::uint64_t peak_rss_sum_kib = 0U;
    std::uint64_t minor_page_faults_sum = 0U;
    std::uint64_t major_page_faults_sum = 0U;
    std::uint64_t filesystem_input_operations_sum = 0U;
    std::uint64_t filesystem_output_operations_sum = 0U;
    std::uint64_t voluntary_context_switches_sum = 0U;
    std::uint64_t involuntary_context_switches_sum = 0U;
    std::uint64_t open_file_descriptors_sum = 0U;
    std::uint64_t threads_sum = 0U;

    void add(const anonsync::SyncLinuxProcessResourceSnapshot& snapshot) {
        rss_sum_kib = checked_resource_add(
            rss_sum_kib, snapshot.memory.rss_kib, "RSS sum");
        pss_sum_kib = checked_resource_add(
            pss_sum_kib, snapshot.memory.pss_kib, "PSS sum");
        pss_anon_sum_kib = checked_resource_add(
            pss_anon_sum_kib, snapshot.memory.pss_anon_kib,
            "anonymous PSS sum");
        pss_file_sum_kib = checked_resource_add(
            pss_file_sum_kib, snapshot.memory.pss_file_kib,
            "file PSS sum");
        pss_shmem_sum_kib = checked_resource_add(
            pss_shmem_sum_kib, snapshot.memory.pss_shmem_kib,
            "shared-memory PSS sum");
        private_resident_sum_kib = checked_resource_add(
            private_resident_sum_kib,
            snapshot.memory.private_resident_kib(),
            "private resident sum");
        swap_pss_sum_kib = checked_resource_add(
            swap_pss_sum_kib, snapshot.memory.swap_pss_kib,
            "swap PSS sum");
        peak_rss_sum_kib = checked_resource_add(
            peak_rss_sum_kib, snapshot.peak_rss_kib,
            "lifetime peak RSS sum");
        minor_page_faults_sum = checked_resource_add(
            minor_page_faults_sum, snapshot.minor_page_faults,
            "minor page-fault sum");
        major_page_faults_sum = checked_resource_add(
            major_page_faults_sum, snapshot.major_page_faults,
            "major page-fault sum");
        filesystem_input_operations_sum = checked_resource_add(
            filesystem_input_operations_sum,
            snapshot.filesystem_input_operations,
            "filesystem input-operation sum");
        filesystem_output_operations_sum = checked_resource_add(
            filesystem_output_operations_sum,
            snapshot.filesystem_output_operations,
            "filesystem output-operation sum");
        voluntary_context_switches_sum = checked_resource_add(
            voluntary_context_switches_sum,
            snapshot.voluntary_context_switches,
            "voluntary context-switch sum");
        involuntary_context_switches_sum = checked_resource_add(
            involuntary_context_switches_sum,
            snapshot.involuntary_context_switches,
            "involuntary context-switch sum");
        open_file_descriptors_sum = checked_resource_add(
            open_file_descriptors_sum, snapshot.open_file_descriptors,
            "open file-descriptor sum");
        threads_sum = checked_resource_add(
            threads_sum, snapshot.threads, "thread sum");
    }

    void observe_maximum(const ResourceTotals& observed) noexcept {
        rss_sum_kib = std::max(rss_sum_kib, observed.rss_sum_kib);
        pss_sum_kib = std::max(pss_sum_kib, observed.pss_sum_kib);
        pss_anon_sum_kib =
            std::max(pss_anon_sum_kib, observed.pss_anon_sum_kib);
        pss_file_sum_kib =
            std::max(pss_file_sum_kib, observed.pss_file_sum_kib);
        pss_shmem_sum_kib =
            std::max(pss_shmem_sum_kib, observed.pss_shmem_sum_kib);
        private_resident_sum_kib = std::max(
            private_resident_sum_kib, observed.private_resident_sum_kib);
        swap_pss_sum_kib =
            std::max(swap_pss_sum_kib, observed.swap_pss_sum_kib);
        peak_rss_sum_kib =
            std::max(peak_rss_sum_kib, observed.peak_rss_sum_kib);
        minor_page_faults_sum =
            std::max(minor_page_faults_sum, observed.minor_page_faults_sum);
        major_page_faults_sum =
            std::max(major_page_faults_sum, observed.major_page_faults_sum);
        filesystem_input_operations_sum = std::max(
            filesystem_input_operations_sum,
            observed.filesystem_input_operations_sum);
        filesystem_output_operations_sum = std::max(
            filesystem_output_operations_sum,
            observed.filesystem_output_operations_sum);
        voluntary_context_switches_sum = std::max(
            voluntary_context_switches_sum,
            observed.voluntary_context_switches_sum);
        involuntary_context_switches_sum = std::max(
            involuntary_context_switches_sum,
            observed.involuntary_context_switches_sum);
        open_file_descriptors_sum = std::max(
            open_file_descriptors_sum, observed.open_file_descriptors_sum);
        threads_sum = std::max(threads_sum, observed.threads_sum);
    }
};

struct ResourceRoundSample final {
    fs::path socket;
    std::string response_json;
    anonsync::SyncLinuxProcessResourceSnapshot snapshot;
};

struct ResourceRound final {
    std::vector<ResourceRoundSample> samples;
    ResourceTotals totals;
    std::uint64_t sample_span_milliseconds = 0U;
};

[[nodiscard]] ResourceRound sample_resource_round_or_throw(
    const std::vector<fs::path>& sockets,
    ResourceClock::time_point deadline,
    const std::vector<ResourceProcessIdentity>* expected_identities,
    std::string_view label) {
    if (expected_identities != nullptr &&
        expected_identities->size() != sockets.size()) {
        throw std::logic_error(
            std::string(label) + " expected-identity shape mismatch");
    }
    ResourceRound round;
    round.samples.reserve(sockets.size());
    std::set<ResourceProcessIdentity> distinct_processes;
    std::uint64_t earliest_sample_milliseconds =
        std::numeric_limits<std::uint64_t>::max();
    std::uint64_t latest_sample_milliseconds = 0U;
    for (std::size_t index = 0U; index < sockets.size(); ++index) {
        const ResourceClock::time_point now = ResourceClock::now();
        if (now >= deadline) {
            throw std::runtime_error(
                std::string(label) +
                " deadline expired before every socket was sampled");
        }
        const auto remaining =
            std::chrono::duration_cast<std::chrono::milliseconds>(
                deadline - now);
        std::uint64_t remaining_milliseconds =
            remaining.count() <= 0
                ? 1U
                : static_cast<std::uint64_t>(remaining.count());
        remaining_milliseconds = std::min(
            remaining_milliseconds,
            anonsync::kSyncLocalStatusSocketMaximumTimeoutMilliseconds);
        std::string json =
            anonsync::query_sync_local_process_resources_or_throw(
                sockets[index], remaining_milliseconds, label);
        if (ResourceClock::now() > deadline) {
            throw std::runtime_error(
                std::string(label) +
                " deadline expired while sampling a socket");
        }
        anonsync::SyncLinuxProcessResourceSnapshot snapshot =
            anonsync::parse_sync_linux_process_resources_response_json_or_throw(
                json, 0U, std::string(label) + " response");
        if (ResourceClock::now() > deadline) {
            throw std::runtime_error(
                std::string(label) +
                " deadline expired while validating a socket sample");
        }
        const ResourceProcessIdentity identity{
            snapshot.server_pid,
            snapshot.process_start_time_clock_ticks};
        if (!distinct_processes.insert(identity).second) {
            throw std::runtime_error(
                std::string(label) +
                " sockets refer to the same live process; refusing to "
                "double-count its memory");
        }
        if (expected_identities != nullptr &&
            (*expected_identities)[index] != identity) {
            throw std::runtime_error(
                std::string(label) +
                " observed a process restart or socket identity change");
        }
        round.totals.add(snapshot);
        earliest_sample_milliseconds = std::min(
            earliest_sample_milliseconds,
            snapshot.sample_monotonic_milliseconds);
        latest_sample_milliseconds = std::max(
            latest_sample_milliseconds,
            snapshot.sample_monotonic_milliseconds);
        round.samples.push_back(
            {sockets[index], std::move(json), std::move(snapshot)});
    }
    if (latest_sample_milliseconds < earliest_sample_milliseconds) {
        throw std::runtime_error(
            std::string(label) + " sample clock range is invalid");
    }
    round.sample_span_milliseconds =
        latest_sample_milliseconds - earliest_sample_milliseconds;
    return round;
}

void render_resource_totals_json(
    std::ostream& output,
    const ResourceTotals& totals) {
    output
        << "{\"rss_sum_kib\":" << totals.rss_sum_kib
        << ",\"pss_sum_kib\":" << totals.pss_sum_kib
        << ",\"pss_anon_sum_kib\":" << totals.pss_anon_sum_kib
        << ",\"pss_file_sum_kib\":" << totals.pss_file_sum_kib
        << ",\"pss_shmem_sum_kib\":" << totals.pss_shmem_sum_kib
        << ",\"private_resident_sum_kib\":"
        << totals.private_resident_sum_kib
        << ",\"swap_pss_sum_kib\":" << totals.swap_pss_sum_kib
        << ",\"peak_rss_sum_kib\":" << totals.peak_rss_sum_kib
        << ",\"minor_page_faults_sum\":"
        << totals.minor_page_faults_sum
        << ",\"major_page_faults_sum\":"
        << totals.major_page_faults_sum
        << ",\"filesystem_input_operations_sum\":"
        << totals.filesystem_input_operations_sum
        << ",\"filesystem_output_operations_sum\":"
        << totals.filesystem_output_operations_sum
        << ",\"voluntary_context_switches_sum\":"
        << totals.voluntary_context_switches_sum
        << ",\"involuntary_context_switches_sum\":"
        << totals.involuntary_context_switches_sum
        << ",\"open_file_descriptors_sum\":"
        << totals.open_file_descriptors_sum
        << ",\"threads_sum\":" << totals.threads_sum << '}';
}

void render_resource_usage_delta_json(
    std::ostream& output,
    const ResourceTotals& first,
    const ResourceTotals& last) {
    output
        << "{\"peak_rss_sum_kib_increase\":"
        << checked_resource_delta(
               first.peak_rss_sum_kib, last.peak_rss_sum_kib,
               "aggregate lifetime peak RSS")
        << ",\"minor_page_faults\":"
        << checked_resource_delta(
               first.minor_page_faults_sum, last.minor_page_faults_sum,
               "aggregate minor page faults")
        << ",\"major_page_faults\":"
        << checked_resource_delta(
               first.major_page_faults_sum, last.major_page_faults_sum,
               "aggregate major page faults")
        << ",\"filesystem_input_operations\":"
        << checked_resource_delta(
               first.filesystem_input_operations_sum,
               last.filesystem_input_operations_sum,
               "aggregate filesystem input operations")
        << ",\"filesystem_output_operations\":"
        << checked_resource_delta(
               first.filesystem_output_operations_sum,
               last.filesystem_output_operations_sum,
               "aggregate filesystem output operations")
        << ",\"voluntary_context_switches\":"
        << checked_resource_delta(
               first.voluntary_context_switches_sum,
               last.voluntary_context_switches_sum,
               "aggregate voluntary context switches")
        << ",\"involuntary_context_switches\":"
        << checked_resource_delta(
               first.involuntary_context_switches_sum,
               last.involuntary_context_switches_sum,
               "aggregate involuntary context switches")
        << '}';
}

struct ResourceProcessEnvelope final {
    fs::path socket;
    anonsync::SyncLinuxProcessResourceSnapshot first;
    anonsync::SyncLinuxProcessResourceSnapshot last;
    std::uint64_t sample_count = 1U;
    std::uint64_t rss_peak_kib = 0U;
    std::uint64_t pss_peak_kib = 0U;
    std::uint64_t pss_anon_peak_kib = 0U;
    std::uint64_t pss_file_peak_kib = 0U;
    std::uint64_t pss_shmem_peak_kib = 0U;
    std::uint64_t private_resident_peak_kib = 0U;
    std::uint64_t swap_pss_peak_kib = 0U;
    std::uint64_t open_file_descriptors_peak = 0U;
    std::uint64_t threads_peak = 0U;

    ResourceProcessEnvelope(
        fs::path selected_socket,
        const anonsync::SyncLinuxProcessResourceSnapshot& initial)
        : socket(std::move(selected_socket)),
          first(initial),
          last(initial),
          rss_peak_kib(initial.memory.rss_kib),
          pss_peak_kib(initial.memory.pss_kib),
          pss_anon_peak_kib(initial.memory.pss_anon_kib),
          pss_file_peak_kib(initial.memory.pss_file_kib),
          pss_shmem_peak_kib(initial.memory.pss_shmem_kib),
          private_resident_peak_kib(initial.memory.private_resident_kib()),
          swap_pss_peak_kib(initial.memory.swap_pss_kib),
          open_file_descriptors_peak(initial.open_file_descriptors),
          threads_peak(initial.threads) {}

    void observe(const anonsync::SyncLinuxProcessResourceSnapshot& observed) {
        if (observed.server_pid != first.server_pid ||
            observed.process_start_time_clock_ticks !=
                first.process_start_time_clock_ticks) {
            throw std::logic_error(
                "resource process envelope identity changed after round proof");
        }
        (void)checked_resource_delta(
            last.peak_rss_kib, observed.peak_rss_kib,
            "process lifetime peak RSS");
        (void)checked_resource_delta(
            last.minor_page_faults, observed.minor_page_faults,
            "process minor page faults");
        (void)checked_resource_delta(
            last.major_page_faults, observed.major_page_faults,
            "process major page faults");
        (void)checked_resource_delta(
            last.filesystem_input_operations,
            observed.filesystem_input_operations,
            "process filesystem input operations");
        (void)checked_resource_delta(
            last.filesystem_output_operations,
            observed.filesystem_output_operations,
            "process filesystem output operations");
        (void)checked_resource_delta(
            last.voluntary_context_switches,
            observed.voluntary_context_switches,
            "process voluntary context switches");
        (void)checked_resource_delta(
            last.involuntary_context_switches,
            observed.involuntary_context_switches,
            "process involuntary context switches");
        last = observed;
        sample_count = checked_resource_add(
            sample_count, 1U, "process sample count");
        rss_peak_kib = std::max(rss_peak_kib, observed.memory.rss_kib);
        pss_peak_kib = std::max(pss_peak_kib, observed.memory.pss_kib);
        pss_anon_peak_kib = std::max(
            pss_anon_peak_kib, observed.memory.pss_anon_kib);
        pss_file_peak_kib = std::max(
            pss_file_peak_kib, observed.memory.pss_file_kib);
        pss_shmem_peak_kib = std::max(
            pss_shmem_peak_kib, observed.memory.pss_shmem_kib);
        private_resident_peak_kib = std::max(
            private_resident_peak_kib,
            observed.memory.private_resident_kib());
        swap_pss_peak_kib = std::max(
            swap_pss_peak_kib, observed.memory.swap_pss_kib);
        open_file_descriptors_peak = std::max(
            open_file_descriptors_peak, observed.open_file_descriptors);
        threads_peak = std::max(threads_peak, observed.threads);
    }
};

void render_resource_process_envelope_json(
    std::ostream& output,
    const ResourceProcessEnvelope& envelope) {
    output
        << "{\"socket\":" << json_quote(envelope.socket.generic_string())
        << ",\"server_pid\":" << envelope.first.server_pid
        << ",\"process_start_time_clock_ticks\":"
        << envelope.first.process_start_time_clock_ticks
        << ",\"sample_count\":" << envelope.sample_count
        << ",\"observed_peaks\":{\"rss_kib\":"
        << envelope.rss_peak_kib
        << ",\"pss_kib\":" << envelope.pss_peak_kib
        << ",\"pss_anon_kib\":" << envelope.pss_anon_peak_kib
        << ",\"pss_file_kib\":" << envelope.pss_file_peak_kib
        << ",\"pss_shmem_kib\":" << envelope.pss_shmem_peak_kib
        << ",\"private_resident_kib\":"
        << envelope.private_resident_peak_kib
        << ",\"swap_pss_kib\":" << envelope.swap_pss_peak_kib
        << ",\"open_file_descriptors\":"
        << envelope.open_file_descriptors_peak
        << ",\"threads\":" << envelope.threads_peak
        << "},\"usage_delta\":{\"peak_rss_kib_increase\":"
        << checked_resource_delta(
               envelope.first.peak_rss_kib, envelope.last.peak_rss_kib,
               "process lifetime peak RSS")
        << ",\"minor_page_faults\":"
        << checked_resource_delta(
               envelope.first.minor_page_faults,
               envelope.last.minor_page_faults,
               "process minor page faults")
        << ",\"major_page_faults\":"
        << checked_resource_delta(
               envelope.first.major_page_faults,
               envelope.last.major_page_faults,
               "process major page faults")
        << ",\"filesystem_input_operations\":"
        << checked_resource_delta(
               envelope.first.filesystem_input_operations,
               envelope.last.filesystem_input_operations,
               "process filesystem input operations")
        << ",\"filesystem_output_operations\":"
        << checked_resource_delta(
               envelope.first.filesystem_output_operations,
               envelope.last.filesystem_output_operations,
               "process filesystem output operations")
        << ",\"voluntary_context_switches\":"
        << checked_resource_delta(
               envelope.first.voluntary_context_switches,
               envelope.last.voluntary_context_switches,
               "process voluntary context switches")
        << ",\"involuntary_context_switches\":"
        << checked_resource_delta(
               envelope.first.involuntary_context_switches,
               envelope.last.involuntary_context_switches,
               "process involuntary context switches")
        << "},\"first_resources\":"
        << anonsync::render_sync_linux_process_resources_response_json(
               envelope.first)
        << ",\"last_resources\":"
        << anonsync::render_sync_linux_process_resources_response_json(
               envelope.last)
        << '}';
}

struct ResourceSeriesPoint final {
    std::uint64_t index = 0U;
    std::uint64_t scheduled_offset_milliseconds = 0U;
    std::uint64_t started_offset_milliseconds = 0U;
    std::uint64_t completed_offset_milliseconds = 0U;
    std::uint64_t schedule_lag_milliseconds = 0U;
    std::uint64_t sample_span_milliseconds = 0U;
    ResourceTotals totals;
};

int command_resources(const Options& options) {
    options.require_only({"socket", "timeout-milliseconds"});
    const std::vector<fs::path> sockets =
        resource_socket_paths_or_throw(options, "resources");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    if (timeout_milliseconds == 0U ||
        timeout_milliseconds >
            anonsync::kSyncLocalStatusSocketMaximumTimeoutMilliseconds) {
        throw std::invalid_argument(
            "resources aggregate timeout must be in [1, 60000] milliseconds");
    }
    const ResourceClock::time_point started_at = ResourceClock::now();
    const ResourceClock::time_point deadline = resource_deadline_or_throw(
        started_at, timeout_milliseconds, "resources aggregate");
    ResourceRound round = sample_resource_round_or_throw(
        sockets, deadline, nullptr, "anonsync_sync resources");

    std::cout
        << "{\"schema\":"
        << json_quote(anonsync::kSyncLinuxProcessResourcesAggregateSchema)
        << ",\"command\":\"resources\",\"terminal_class\":\"completed\""
           ",\"process_count\":" << round.samples.size()
        << ",\"requested_timeout_milliseconds\":" << timeout_milliseconds
        << ",\"timeout_is_one_aggregate_deadline\":true"
        << ",\"rss_sum_kib\":" << round.totals.rss_sum_kib
        << ",\"pss_sum_kib\":" << round.totals.pss_sum_kib
        << ",\"pss_anon_sum_kib\":" << round.totals.pss_anon_sum_kib
        << ",\"pss_file_sum_kib\":" << round.totals.pss_file_sum_kib
        << ",\"pss_shmem_sum_kib\":" << round.totals.pss_shmem_sum_kib
        << ",\"private_resident_sum_kib\":"
        << round.totals.private_resident_sum_kib
        << ",\"swap_pss_sum_kib\":" << round.totals.swap_pss_sum_kib
        << ",\"peak_rss_sum_kib\":" << round.totals.peak_rss_sum_kib
        << ",\"open_file_descriptors_sum\":"
        << round.totals.open_file_descriptors_sum
        << ",\"threads_sum\":" << round.totals.threads_sum
        << ",\"sample_span_milliseconds\":"
        << round.sample_span_milliseconds
        << ",\"rss_sum_double_counts_shared_pages\":true"
           ",\"pss_values_use_kernel_share_adjustment\":true"
           ",\"samples_are_sequential_not_atomic\":true"
           ",\"measurement_is_diagnostic_only\":true"
           ",\"ordinary_status_remains_procfs_cold\":true"
           ",\"samples\":[";
    for (std::size_t index = 0U; index < round.samples.size(); ++index) {
        if (index != 0U) std::cout << ',';
        std::cout
            << "{\"socket\":"
            << json_quote(round.samples[index].socket.generic_string())
            << ",\"resources\":"
            << round.samples[index].response_json << '}';
    }
    std::cout << "]}\n";
    return 0;
}

int command_resources_watch(const Options& options) {
    options.require_only(
        {"socket", "samples", "interval-milliseconds",
         "timeout-milliseconds"});
    const std::vector<fs::path> sockets =
        resource_socket_paths_or_throw(options, "resources-watch");
    const std::uint64_t sample_count =
        option_uint64_or(options, "samples", 10U);
    const std::uint64_t interval_milliseconds =
        option_uint64_or(options, "interval-milliseconds", 1000U);
    const std::uint64_t timeout_milliseconds =
        option_uint64_or(options, "timeout-milliseconds", 60000U);
    if (sample_count < 2U ||
        sample_count > kResourceWatchMaximumSamples) {
        throw std::invalid_argument(
            "resources-watch samples must be in [2, 1024]");
    }
    if (interval_milliseconds == 0U ||
        interval_milliseconds >
            kResourceWatchMaximumIntervalMilliseconds) {
        throw std::invalid_argument(
            "resources-watch interval must be in [1, 3600000] milliseconds");
    }
    if (timeout_milliseconds == 0U ||
        timeout_milliseconds > kResourceWatchMaximumTimeoutMilliseconds) {
        throw std::invalid_argument(
            "resources-watch timeout must be in [1, 86400000] milliseconds");
    }
    const std::uint64_t interval_count = sample_count - 1U;
    if (interval_count >
        std::numeric_limits<std::uint64_t>::max() /
            interval_milliseconds) {
        throw std::overflow_error(
            "resources-watch schedule overflows uint64");
    }
    const std::uint64_t final_scheduled_offset =
        interval_count * interval_milliseconds;
    if (final_scheduled_offset >= timeout_milliseconds) {
        throw std::invalid_argument(
            "resources-watch final scheduled sample must precede the total deadline");
    }

    const ResourceClock::time_point started_at = ResourceClock::now();
    const ResourceClock::time_point deadline = resource_deadline_or_throw(
        started_at, timeout_milliseconds, "resources-watch");
    std::vector<ResourceSeriesPoint> points;
    points.reserve(static_cast<std::size_t>(sample_count));
    std::vector<ResourceProcessEnvelope> envelopes;
    envelopes.reserve(sockets.size());
    std::vector<ResourceProcessIdentity> expected_identities;
    expected_identities.reserve(sockets.size());
    ResourceTotals first_totals;
    ResourceTotals last_totals;
    ResourceTotals observed_peak_totals;
    std::uint64_t maximum_schedule_lag_milliseconds = 0U;
    std::uint64_t maximum_round_sample_span_milliseconds = 0U;

    for (std::uint64_t index = 0U; index < sample_count; ++index) {
        const std::uint64_t scheduled_offset =
            index * interval_milliseconds;
        const ResourceClock::time_point scheduled_at =
            started_at + resource_milliseconds_or_throw(
                scheduled_offset, "resources-watch scheduled offset");
        while (ResourceClock::now() < scheduled_at) {
            std::this_thread::sleep_until(scheduled_at);
        }
        const ResourceClock::time_point round_started_at =
            ResourceClock::now();
        if (round_started_at >= deadline) {
            throw std::runtime_error(
                "resources-watch deadline expired before a scheduled round");
        }
        const std::uint64_t started_offset =
            resource_elapsed_milliseconds_or_throw(
                started_at, round_started_at,
                "resources-watch round start");
        const std::uint64_t schedule_lag =
            started_offset >= scheduled_offset
                ? started_offset - scheduled_offset
                : 0U;
        ResourceRound round = sample_resource_round_or_throw(
            sockets, deadline,
            expected_identities.empty() ? nullptr : &expected_identities,
            "anonsync_sync resources-watch");
        const std::uint64_t completed_offset =
            resource_elapsed_milliseconds_or_throw(
                started_at, ResourceClock::now(),
                "resources-watch round completion");

        if (index == 0U) {
            first_totals = round.totals;
            observed_peak_totals = round.totals;
            for (const ResourceRoundSample& sample : round.samples) {
                expected_identities.emplace_back(
                    sample.snapshot.server_pid,
                    sample.snapshot.process_start_time_clock_ticks);
                envelopes.emplace_back(sample.socket, sample.snapshot);
            }
        } else {
            for (std::size_t process_index = 0U;
                 process_index < round.samples.size(); ++process_index) {
                envelopes[process_index].observe(
                    round.samples[process_index].snapshot);
            }
            observed_peak_totals.observe_maximum(round.totals);
        }
        last_totals = round.totals;
        maximum_schedule_lag_milliseconds = std::max(
            maximum_schedule_lag_milliseconds, schedule_lag);
        maximum_round_sample_span_milliseconds = std::max(
            maximum_round_sample_span_milliseconds,
            round.sample_span_milliseconds);
        points.push_back(
            {index, scheduled_offset, started_offset, completed_offset,
             schedule_lag, round.sample_span_milliseconds,
             std::move(round.totals)});
    }

    std::cout
        << "{\"schema\":"
        << json_quote(anonsync::kSyncLinuxProcessResourcesSeriesSchema)
        << ",\"command\":\"resources-watch\","
           "\"terminal_class\":\"completed\""
        << ",\"process_count\":" << sockets.size()
        << ",\"sample_count\":" << sample_count
        << ",\"interval_milliseconds\":" << interval_milliseconds
        << ",\"requested_timeout_milliseconds\":"
        << timeout_milliseconds
        << ",\"maximum_processes\":" << kResourceMaximumProcesses
        << ",\"maximum_samples\":" << kResourceWatchMaximumSamples
        << ",\"series_duration_milliseconds\":"
        << points.back().completed_offset_milliseconds
        << ",\"maximum_schedule_lag_milliseconds\":"
        << maximum_schedule_lag_milliseconds
        << ",\"maximum_round_sample_span_milliseconds\":"
        << maximum_round_sample_span_milliseconds
        << ",\"timeout_is_one_series_deadline\":true"
           ",\"schedule_is_anchored_to_command_start\":true"
           ",\"process_identity_must_remain_stable\":true"
           ",\"restarts_fail_closed\":true"
           ",\"retained_shape_is_processes_plus_samples\":true"
           ",\"full_process_by_sample_matrix_is_not_retained\":true"
           ",\"rss_sum_double_counts_shared_pages\":true"
           ",\"pss_values_use_kernel_share_adjustment\":true"
           ",\"rounds_and_processes_are_sampled_sequentially_not_atomically\":true"
           ",\"between_point_peaks_may_be_missed\":true"
           ",\"target_processes_are_not_paused\":true"
           ",\"measurement_is_diagnostic_only\":true"
           ",\"ordinary_status_remains_procfs_cold\":true"
           ",\"cgroup_pressure_is_not_measured\":true"
           ",\"first_totals\":";
    render_resource_totals_json(std::cout, first_totals);
    std::cout << ",\"last_totals\":";
    render_resource_totals_json(std::cout, last_totals);
    std::cout << ",\"observed_peak_sums\":";
    render_resource_totals_json(std::cout, observed_peak_totals);
    std::cout << ",\"aggregate_usage_delta\":";
    render_resource_usage_delta_json(std::cout, first_totals, last_totals);
    std::cout << ",\"points\":[";
    for (std::size_t index = 0U; index < points.size(); ++index) {
        if (index != 0U) std::cout << ',';
        const ResourceSeriesPoint& point = points[index];
        std::cout
            << "{\"index\":" << point.index
            << ",\"scheduled_offset_milliseconds\":"
            << point.scheduled_offset_milliseconds
            << ",\"started_offset_milliseconds\":"
            << point.started_offset_milliseconds
            << ",\"completed_offset_milliseconds\":"
            << point.completed_offset_milliseconds
            << ",\"schedule_lag_milliseconds\":"
            << point.schedule_lag_milliseconds
            << ",\"sample_span_milliseconds\":"
            << point.sample_span_milliseconds
            << ",\"totals\":";
        render_resource_totals_json(std::cout, point.totals);
        std::cout << '}';
    }
    std::cout << "],\"processes\":[";
    for (std::size_t index = 0U; index < envelopes.size(); ++index) {
        if (index != 0U) std::cout << ',';
        render_resource_process_envelope_json(std::cout, envelopes[index]);
    }
    std::cout << "]}\n";
    return 0;
}

int command_stop(const Options& options) {
    options.require_only({"socket", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout << anonsync::request_sync_local_status_stop_or_throw(
        socket_path, timeout_milliseconds,
        "anonsync_sync stop") << '\n';
    return 0;
}

int command_recheck(const Options& options) {
    options.require_only({"socket", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout << anonsync::request_sync_local_status_recheck_or_throw(
        socket_path, timeout_milliseconds,
        "anonsync_sync recheck") << '\n';
    return 0;
}

int command_versions(const Options& options) {
    options.require_only(
        {"socket", "path", "after", "limit", "inspection-mode",
         "source-cutpoint", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    anonsync::SyncReplicaHistoricalVersionQuery query;
    const std::string inspection_mode =
        options.one_or("inspection-mode", "exact");
    if (inspection_mode == "exact") {
        query.inspection_mode = anonsync::
            SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability;
    } else if (inspection_mode == "metadata") {
        query.inspection_mode = anonsync::
            SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly;
    } else {
        throw std::invalid_argument(
            "--inspection-mode must be exact or metadata");
    }
    query.maximum_entries = option_uint64_or(
        options, "limit",
        anonsync::kSyncReplicaHistoricalVersionDefaultMaximumEntries);
    if (options.has("path")) {
        query.canonical_path = options.one("path");
    }
    if (options.has("after")) {
        query.start_after_operation_id = options.one("after");
    }
    if (options.has("source-cutpoint")) {
        query.expected_source_cutpoint = anonsync::
            decode_sync_replica_historical_version_source_cutpoint_or_throw(
                options.one("source-cutpoint"),
                "anonsync_sync versions --source-cutpoint");
    }
    anonsync::validate_sync_replica_historical_version_query_or_throw(
        query, "anonsync_sync versions");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout
        << anonsync::
               request_sync_local_status_historical_versions_query_or_throw(
                   socket_path, std::move(query), timeout_milliseconds,
                   "anonsync_sync versions")
        << '\n';
    return 0;
}

int command_retention_plan(const Options& options) {
    options.require_only(
        {"socket", "after", "limit", "source-cutpoint",
         "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    anonsync::SyncReplicaRetentionPlanQuery query;
    query.maximum_entries = option_uint64_or(
        options, "limit",
        anonsync::kSyncReplicaRetentionPlanDefaultMaximumEntries);
    if (options.has("after")) {
        query.start_after_content_sha256 = options.one("after");
    }
    if (options.has("source-cutpoint")) {
        query.expected_source_cutpoint = anonsync::
            decode_sync_replica_historical_version_source_cutpoint_or_throw(
                options.one("source-cutpoint"),
                "anonsync_sync retention-plan --source-cutpoint");
    }
    anonsync::validate_sync_replica_retention_plan_query_or_throw(
        query, "anonsync_sync retention-plan");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout
        << anonsync::request_sync_local_status_retention_plan_or_throw(
               socket_path, std::move(query), timeout_milliseconds,
               "anonsync_sync retention-plan")
        << '\n';
    return 0;
}

int command_restore(const Options& options) {
    options.require_only(
        {"socket", "operation", "expected-current",
         "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::string operation_id = options.one("operation");
    const std::string expected_current_operation_id =
        options.one("expected-current");
    anonsync::validate_sync_replica_historical_version_restore_request_or_throw(
        anonsync::SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = operation_id,
            .expected_current_operation_id = expected_current_operation_id,
        },
        "anonsync_sync restore");
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout << anonsync::
        request_sync_local_status_historical_version_restore_exact_or_throw(
            socket_path, operation_id, expected_current_operation_id,
            timeout_milliseconds, "anonsync_sync restore")
              << '\n';
    return 0;
}

int command_version_retention_update(
    const Options& options,
    bool pin) {
    options.require_only(
        {"socket", "operation", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::string operation_id = options.one("operation");
    if (!anonsync::is_lowercase_sha256_hex(operation_id)) {
        throw std::invalid_argument(
            "--operation must be one lowercase SHA-256 operation ID");
    }
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout
        << (pin
                ? anonsync::
                      request_sync_local_status_historical_version_pin_or_throw(
                          socket_path, operation_id, timeout_milliseconds,
                          "anonsync_sync version-pin")
                : anonsync::
                      request_sync_local_status_historical_version_unpin_or_throw(
                          socket_path, operation_id, timeout_milliseconds,
                          "anonsync_sync version-unpin"))
        << '\n';
    return 0;
}

int command_quarantine(const Options& options) {
    options.require_only(
        {"socket", "expected", "observed", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::string expected = options.one("expected");
    const std::string observed = options.one("observed");
    if (!anonsync::is_lowercase_sha256_hex(expected) ||
        !anonsync::is_lowercase_sha256_hex(observed) ||
        expected == observed) {
        throw std::invalid_argument(
            "--expected and --observed must be distinct lowercase SHA-256 "
            "digests");
    }
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout
        << anonsync::request_sync_local_status_payload_quarantine_or_throw(
               socket_path, expected, observed, timeout_milliseconds,
               "anonsync_sync quarantine")
        << '\n';
    return 0;
}

int command_quarantine_release(const Options& options) {
    options.require_only(
        {"socket", "expected", "observed", "timeout-milliseconds"});
    const fs::path socket_path = require_absolute_path(
        options.one("socket"), "--socket");
    const std::string expected = options.one("expected");
    const std::string observed = options.one("observed");
    if (!anonsync::is_lowercase_sha256_hex(expected) ||
        !anonsync::is_lowercase_sha256_hex(observed) ||
        expected == observed) {
        throw std::invalid_argument(
            "--expected and --observed must be distinct lowercase SHA-256 "
            "digests");
    }
    const std::uint64_t timeout_milliseconds = option_uint64_or(
        options, "timeout-milliseconds",
        anonsync::kSyncLocalStatusSocketDefaultTimeoutMilliseconds);
    std::cout
        << anonsync::
               request_sync_local_status_payload_quarantine_release_or_throw(
                   socket_path, expected, observed, timeout_milliseconds,
                   "anonsync_sync quarantine-release")
        << '\n';
    return 0;
}

void print_usage(std::ostream& output) {
    output
        << "AnonSync bounded peer synchronization\n\n"
        << "Usage:\n"
        << "  anonsync_sync once --manifest ABSOLUTE_JSON "
           "--remote-device ID --remote-epoch N --remote-spki SHA256 "
           "--certificate PEM --private-key PEM --ca-file PEM "
           "[--transport direct --address NUMERIC --port N] "
           "[--transport tor --onion-address V3_ONION --onion-port N "
           "--tor-socks-address NUMERIC --tor-socks-port N] "
           "[--transport i2p --i2p-destination DESTINATION "
           "--i2p-sam-address NUMERIC --i2p-sam-port N] "
           "[--timeout-seconds N] [--max-runtime-seconds N] "
           "[--max-round-trips N] [--max-source-resets N] "
           "[folder pass bounds]\n"
        << "  anonsync_sync share-create --instance ID "
           "--state-directory ABSOLUTE_DIR --files-root ABSOLUTE_DIR "
           "[--folder ID] [--local-device ID] [--local-epoch N] "
           "[--max-payload-bytes N] [folder pass bounds]\n"
        << "  anonsync_sync share-join --instance ID "
           "--state-directory ABSOLUTE_DIR --files-root ABSOLUTE_DIR "
           "--initial-files empty|adopt-existing "
           "--peer-card ABSOLUTE_JSON "
           "--peer-card-sha256 LOWERCASE_SHA256 "
           "[--local-device ID] [--local-epoch N] "
           "[--max-payload-bytes N] "
           "[outbound direct/Tor/I2P route] "
           "[--ingress direct|tor|i2p and ingress options] "
           "[service and folder bounds]\n"
        << "  anonsync_sync identity-create --instance ID "
           "--manifest ABSOLUTE_JSON\n"
        << "  anonsync_sync link --instance ID --manifest ABSOLUTE_JSON "
           "--peer-card ABSOLUTE_JSON "
           "[--peer-card-sha256 LOWERCASE_SHA256] "
           "[outbound direct/Tor/I2P route] "
           "[--ingress direct|tor|i2p and ingress options] "
           "[service and folder bounds]\n"
        << "  anonsync_sync provision --instance ID --manifest ABSOLUTE_JSON "
           "--remote-device ID --remote-epoch N --remote-spki SHA256 "
           "--certificate PEM --private-key PEM --ca-file PEM "
           "[outbound direct/Tor/I2P route] "
           "[--ingress direct|tor|i2p and ingress options] "
           "[service and folder bounds]\n"
        << "  anonsync_sync check-config --config ABSOLUTE_JSON\n"
        << "  anonsync_sync database-backup-create "
           "--manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE "
           "[--role replica|file-effect|tls-membership|"
           "tls-membership-anchor|folder-catalog]\n"
        << "  anonsync_sync database-backup-inspect "
           "--manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE "
           "[--role replica|file-effect|tls-membership|"
           "tls-membership-anchor|folder-catalog]\n"
        << "  anonsync_sync database-recovery-replace "
           "--manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE "
           "--rollback ABSOLUTE_SQLITE --receipt ABSOLUTE_RECEIPT "
           "--expected-current v1:INCARNATION:EPOCH:CUTPOINT\n"
        << "  anonsync_sync database-recovery-inspect "
           "--manifest ABSOLUTE_JSON\n"
        << "  anonsync_sync database-recovery-advance "
           "--manifest ABSOLUTE_JSON "
           "--expected v1:INCARNATION:EPOCH:CUTPOINT\n"
        << "  anonsync_sync selective-sync-status "
           "--manifest ABSOLUTE_JSON\n"
        << "  anonsync_sync selective-sync-set "
           "--manifest ABSOLUTE_JSON "
           "--default materialize|metadata_only "
           "[--rule MODE=CANONICAL_PATH ...]\n"
        << "  anonsync_sync run --config ABSOLUTE_JSON\n"
        << "  anonsync_sync run [the same peer/TLS/route/folder options] "
           "--listen-port N [--bind-address NUMERIC] "
           "[--status-socket ABSOLUTE_SOCKET] "
           "[--scan-interval-seconds N] [--retry-initial-seconds N] "
           "[--retry-maximum-seconds N] [--max-cycles N] "
           "[--max-service-runtime-seconds N]\n"
        << "  anonsync_sync status --socket ABSOLUTE_SOCKET "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync resources --socket ABSOLUTE_SOCKET "
           "[--socket ABSOLUTE_SOCKET ...] "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync resources-watch --socket ABSOLUTE_SOCKET "
           "[--socket ABSOLUTE_SOCKET ...] [--samples N] "
           "[--interval-milliseconds N] [--timeout-milliseconds N]\n"
        << "  anonsync_sync recheck --socket ABSOLUTE_SOCKET "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync versions --socket ABSOLUTE_SOCKET "
           "[--path CANONICAL_RELATIVE_PATH] "
           "[--after LOWERCASE_SHA256] [--limit 1..1024] "
           "[--inspection-mode exact|metadata] "
           "[--source-cutpoint "
           "v4:exact:OPERATION_SET_SHA256:EVIDENCE_SET_SHA256:PIN_SET_SHA256:PAYLOAD_SHA256|"
           "v4:metadata:OPERATION_SET_SHA256:PIN_SET_SHA256|"
           "v3:exact:OPERATION_SET_SHA256:EVIDENCE_SET_SHA256:PAYLOAD_SHA256|"
           "v1:OPERATION_SET_SHA256:PAYLOAD_SHA256|"
           "v2:metadata:OPERATION_SET_SHA256] "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync retention-plan --socket ABSOLUTE_SOCKET "
           "[--after LOWERCASE_SHA256] [--limit 1..1024] "
           "[--source-cutpoint "
           "v4:exact:OPERATION_SET_SHA256:EVIDENCE_SET_SHA256:PIN_SET_SHA256:PAYLOAD_SHA256] "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync restore --socket ABSOLUTE_SOCKET "
           "--operation LOWERCASE_SHA256 "
           "--expected-current LOWERCASE_SHA256 "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync version-pin --socket ABSOLUTE_SOCKET "
           "--operation LOWERCASE_SHA256 "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync version-unpin --socket ABSOLUTE_SOCKET "
           "--operation LOWERCASE_SHA256 "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync quarantine --socket ABSOLUTE_SOCKET "
           "--expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256 "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync quarantine-release --socket ABSOLUTE_SOCKET "
           "--expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256 "
           "[--timeout-milliseconds N]\n"
        << "  anonsync_sync stop --socket ABSOLUTE_SOCKET "
           "[--timeout-milliseconds N]\n\n"
        << "once performs one local configured-folder pass, at most one "
           "authenticated direct/Tor/I2P reconciliation pull, and one "
           "post-pull apply while the command budget remains. It is the "
           "bounded product operation intended for reuse by the future "
           "long-running service; it is not itself a watcher or retry loop. "
           "run retains one direct/Tor numeric listener or one native I2P "
           "STREAM ACCEPT route worker and repeatedly invokes that exact "
           "operation with bounded retry until SIGINT/SIGTERM, a cycle bound, "
           "or a service-runtime bound. recheck accepts an owner-only, "
           "generation-tracked maintenance obligation that hashes every current "
           "payload byte and moves the exact resulting snapshot into ordinary "
           "convergence; acceptance is not completion, so status reports the "
           "requested and completed generations. database-backup-create, "
           "database-backup-inspect, database-recovery-replace, "
           "database-recovery-inspect, and database-recovery-advance are "
           "offline, share-scoped SQLite "
           "ceremonies that acquire the same deployment singleton as run and "
           "once. Backup creation brackets one transactionally pinned logical "
           "replica-database image, publishes an owner-only sidecar-free file "
           "create-new outside every active database family, payload root, and "
           "synchronized root, then reopens the detached bytes for deployment, "
           "schema, geometry, digest, and cutpoint proof. Backup inspection "
           "performs the detached proof without opening the active database. "
           "The artifact excludes payload bytes, the folder catalog, membership, "
           "effects, and anchors, and neither backup command replaces a database. "
           "Recovery replacement validates one detached artifact before mutation, "
           "publishes one bounded immutable create-new action receipt and the "
           "displaced logical database as a create-new rollback artifact, then "
           "classifies restart progress only from the active database's exact "
           "cutpoint. It admits only the displaced database, the candidate "
           "awaiting epoch advance, or the candidate's exact recovery successor; "
           "unknown continuity fails closed. It replaces the descriptor-rooted "
           "active database through SQLite's bounded destination transaction, "
           "advances the restored recovery epoch when still pending, and reopens "
           "the resulting deployment, rollback artifact, candidate, and receipt "
           "before success. The receipt is immutable evidence, not effect authority. "
           "Recovery inspection emits one canonical incarnation/epoch/cutpoint "
           "expectation from the active database. Recovery advance requires that "
           "exact expectation, advances recovery epoch and state generation "
           "atomically, and rejects stale reuse. None make SQLite lineage an "
           "external anti-rollback anchor. Whole-image rollback can restore an "
           "earlier lineage, so retention age must be reset whenever continuity "
           "is uncertain. Run advance only after any restore or replacement has "
           "completed while the service is stopped. versions "
           "accepts one bounded "
           "inspection page of active causal file predecessors. Exact mode "
           "retains the existing complete payload-namespace observation and "
           "reports immediate restore availability; metadata mode reads no "
           "payload-store state and reports those fields as unknown. An exact "
           "path, page limit, and active superseded operation cursor may select "
           "later pages. Copying the first page's source_cutpoint into "
           "--source-cutpoint makes later pages fail closed if the authority "
           "bound by that inspection mode changes; status reports the exact "
           "query, source cutpoint, and next cursor. "
           "retention-plan observes one exact, digest-ordered page of the "
           "complete physical payload namespace and explains whether each "
           "object is rooted by a current file, active superseded history, "
           "inactive evidence, an explicit local pin, or no retained replica "
           "reference. Its v4 exact source cutpoint binds operations, inactive "
           "evidence, pins, and payload bytes across pages. The result is a "
           "deletion-free diagnostic: it applies no quota, grace period, "
           "in-flight-transfer root, quarantine, or unlink authority. "
           "restore accepts one exact operation ID and the exact current head from "
           "that inventory, rejects stale intent before catalog, rooted-path, or "
           "payload-store work, then re-proves current catalog, replica, rooted-path, "
           "and payload authority, atomically "
           "publishes those bytes, and mints a new causal successor through the "
           "ordinary folder owner. These commands are explicit recovery operations, "
           "not wall-clock chronology, Archive browsing, or garbage collection. "
           "version-pin and version-unpin mutate only the durable local set of "
           "explicit retention roots over immutable File-operation evidence; "
           "they do not copy bytes, restore a path, propagate policy to peers, or "
           "authorize collection. quarantine accepts one exact "
           "active expected/observed corruption pair, preserves that byte image "
           "outside the authoritative payload namespace with a bounded no-replace "
           "rename, and leaves ordinary convergence to re-fetch and re-prove the "
           "expected payload. quarantine-release reclaims one exact retained "
           "diagnostic image only after the active integrity alarm has cleared; "
           "it is explicit evidence release, not restore, versioning, automatic "
           "retention, or garbage collection. share-create is the idempotent first "
           "local-share workflow: it creates or resumes one exact deployment "
           "under an owner-only instance-bound state directory, explicitly "
           "adopts and publishes existing regular files through the ordinary "
           "folder owner, then creates or resumes the signed public pairing "
           "card. It invokes only exact co-installed siblings, never a shell "
           "or PATH search. share-join is the second-peer setup path: it "
           "requires an exact pinned public card and an explicit empty versus "
           "adopt-existing decision, creates or resumes the joining share with "
           "the card's folder ID, publishes its response card, admits the peer, "
           "and provisions the existing retained service without starting it. "
           "identity-create creates or resumes "
           "one share-scoped Ed25519 identity and a signed public-only pairing "
           "card under HOME. link validates an exchanged card, explicitly "
           "admits that peer to durable membership, installs its exact trust "
           "certificate, and provisions the same retained service document. "
           "A card is not itself a share grant. provision creates the exact "
           "owner-only "
           "per-user v2 configuration consumed by the installed systemd unit, "
           "using HOME and XDG_RUNTIME_DIR, and never overwrites an existing "
           "instance. check-config reads and normalizes one "
           "strict owner-only linked-peer document without opening a listener "
           "or deployment owner. --config launches that exact description. "
           "status reads a secret-free immutable snapshot from the optional "
           "owner-only local Unix socket. stop sends that socket's only "
           "mutating request: finish the current bounded owner step and begin "
           "no new one. It is idempotent and is not a generic RPC surface. "
           "Linked-peer v2 "
           "configuration separates outbound routing from inbound publication. "
           "Direct ingress owns the retained listener, Tor onion publication is "
           "externally managed and bound to an exact v3 service identity, and "
           "native I2P ingress owns cancellable SAM SESSION CREATE + STREAM ACCEPT "
           "publication on a route-only worker, with no numeric listener and "
           "bounded reconnect. JSON is written to stdout and "
           "diagnostics to stderr.\n";
}

void emit_error(
    std::string_view command,
    std::string_view error_code,
    std::string_view message) {
    std::cout
        << "{\"command\":" << json_quote(command)
        << ",\"terminal_class\":\"stopped\",\"error_code\":"
        << json_quote(error_code)
        << ",\"message\":" << json_quote(message) << "}\n";
    std::cerr << "anonsync_sync: " << message << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    const auto command_started_at = std::chrono::steady_clock::now();
    std::string command = argc >= 2 ? argv[1] : "";
    try {
        if (argc < 2 || command == "--help" || command == "help") {
            print_usage(std::cout);
            return argc < 2 ? 2 : 0;
        }
        anonsync::install_sync_replica_sigpipe_ignore_policy_or_throw(
            "anonsync_sync SIGPIPE policy");
        const Options options(argc, argv, 2);
        if (command == "once") {
            return command_once(options, command_started_at);
        }
        if (command == "share-create") {
            return command_share_create(options);
        }
        if (command == "share-join") {
            return command_share_join(options);
        }
        if (command == "identity-create") {
            return command_identity_create(options);
        }
        if (command == "link") {
            return command_link(options);
        }
        if (command == "provision") {
            return command_provision(options);
        }
        if (command == "check-config") {
            return command_check_config(options);
        }
        if (command == "database-backup-create") {
            return command_database_backup_create(options);
        }
        if (command == "database-backup-inspect") {
            return command_database_backup_inspect(options);
        }
        if (command == "database-recovery-replace") {
            return command_database_recovery_replace(options);
        }
        if (command == "database-recovery-inspect") {
            return command_database_recovery_inspect(options);
        }
        if (command == "database-recovery-advance") {
            return command_database_recovery_advance(options);
        }
        if (command == "selective-sync-status") {
            return command_selective_sync_status(options);
        }
        if (command == "selective-sync-set") {
            return command_selective_sync_set(options);
        }
        if (command == "run") {
            return command_run(options);
        }
        if (command == "status") {
            return command_status(options);
        }
        if (command == "resources") {
            return command_resources(options);
        }
        if (command == "resources-watch") {
            return command_resources_watch(options);
        }
        if (command == "stop") {
            return command_stop(options);
        }
        if (command == "recheck") {
            return command_recheck(options);
        }
        if (command == "versions") {
            return command_versions(options);
        }
        if (command == "retention-plan") {
            return command_retention_plan(options);
        }
        if (command == "restore") {
            return command_restore(options);
        }
        if (command == "version-pin") {
            return command_version_retention_update(options, true);
        }
        if (command == "version-unpin") {
            return command_version_retention_update(options, false);
        }
        if (command == "quarantine") {
            return command_quarantine(options);
        }
        if (command == "quarantine-release") {
            return command_quarantine_release(options);
        }
        throw std::invalid_argument("unknown command: " + command);
    } catch (const std::invalid_argument& error) {
        emit_error(command, "invalid_arguments", error.what());
        return 2;
    } catch (const std::exception& error) {
        emit_error(command, "operation_failed", error.what());
        return 1;
    }
}

#else

int main() {
    std::cerr << "anonsync_sync requires Linux\n";
    return 2;
}

#endif
