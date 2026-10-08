#include "sync_replica_peer_service_configuration.hpp"

#if !defined(_WIN32)

#include "anonsync_json_parser.hpp"
#include "sha256_digest.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_local_status_socket.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_stream_connector.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <limits>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::uint64_t kDefaultTimeoutSeconds = 10U;
constexpr std::uint64_t kDefaultI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMinimumI2pTimeoutSeconds = 180U;
constexpr std::uint64_t kMaximumTimeoutSeconds = 3600U;
constexpr std::uint64_t kMaximumCycleRuntimeSeconds = 86400U;
constexpr std::uint64_t kMaximumServiceRuntimeSeconds = 86400U;
constexpr std::uint64_t kMaximumCycles = 1000000U;
constexpr std::uint64_t kMaximumI2pPrivateDestinationBytes = 8192U;
constexpr std::uint64_t kDefaultI2pTunnelQuantity = 2U;
constexpr std::uint64_t kMaximumI2pTunnelQuantity = 16U;

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

void require_object_or_throw(const Json& value, std::string_view label) {
    if (!value.is_object()) {
        throw std::invalid_argument(std::string(label) + " must be an object");
    }
}

void require_exact_object_keys_or_throw(
    const Json& value,
    std::initializer_list<std::string_view> required,
    std::initializer_list<std::string_view> optional,
    std::string_view label) {
    require_object_or_throw(value, label);
    const std::set<std::string_view> required_keys(required.begin(), required.end());
    const std::set<std::string_view> optional_keys(optional.begin(), optional.end());
    for (const auto& [key, ignored] : value.o) {
        (void)ignored;
        if (!required_keys.contains(key) && !optional_keys.contains(key)) {
            throw std::invalid_argument(
                std::string(label) + " contains unknown key " + key);
        }
    }
    for (const std::string_view key : required_keys) {
        if (!value.o.contains(std::string(key))) {
            throw std::invalid_argument(
                std::string(label) + " is missing key " + std::string(key));
        }
    }
}

[[nodiscard]] const Json& required_member_or_throw(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    require_object_or_throw(object, label);
    const auto found = object.o.find(std::string(key));
    if (found == object.o.end()) {
        throw std::invalid_argument(
            std::string(label) + " is missing key " + std::string(key));
    }
    return found->second;
}

[[nodiscard]] const Json* optional_member(
    const Json& object,
    std::string_view key) noexcept {
    if (!object.is_object()) return nullptr;
    const auto found = object.o.find(std::string(key));
    return found == object.o.end() ? nullptr : &found->second;
}

[[nodiscard]] std::string required_string_or_throw(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    const Json& value = required_member_or_throw(object, key, label);
    if (!value.is_string() || value.s.empty()) {
        throw std::invalid_argument(
            std::string(label) + " key " + std::string(key) +
            " must be a nonempty string");
    }
    return value.s;
}

[[nodiscard]] std::string optional_string_or(
    const Json& object,
    std::string_view key,
    std::string fallback,
    std::string_view label) {
    const Json* value = optional_member(object, key);
    if (value == nullptr) return fallback;
    if (!value->is_string() || value->s.empty()) {
        throw std::invalid_argument(
            std::string(label) + " key " + std::string(key) +
            " must be a nonempty string");
    }
    return value->s;
}

[[nodiscard]] std::uint64_t json_uint64_or_throw(
    const Json& value,
    std::string_view label) {
    if (!value.is_number()) {
        throw std::invalid_argument(
            std::string(label) + " must be an unsigned integer");
    }
    long long signed_value = 0;
    try {
        signed_value = value.integer();
    } catch (const std::runtime_error& error) {
        throw std::invalid_argument(
            std::string(label) + " must be an exact unsigned integer: " +
            error.what());
    }
    if (signed_value < 0) {
        throw std::invalid_argument(
            std::string(label) + " must be an unsigned integer");
    }
    return static_cast<std::uint64_t>(signed_value);
}

[[nodiscard]] std::uint64_t required_uint64_or_throw(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    return json_uint64_or_throw(
        required_member_or_throw(object, key, label),
        child_label(label, key));
}

[[nodiscard]] std::uint64_t optional_uint64_or(
    const Json& object,
    std::string_view key,
    std::uint64_t fallback,
    std::string_view label) {
    const Json* value = optional_member(object, key);
    return value == nullptr
        ? fallback
        : json_uint64_or_throw(*value, child_label(label, key));
}

[[nodiscard]] std::optional<std::uint64_t> optional_uint64(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    const Json* value = optional_member(object, key);
    if (value == nullptr) return std::nullopt;
    return json_uint64_or_throw(*value, child_label(label, key));
}

[[nodiscard]] std::uint16_t checked_port_or_throw(
    std::uint64_t value,
    std::string_view label) {
    if (value == 0U || value > 65535U) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, 65535]");
    }
    return static_cast<std::uint16_t>(value);
}

[[nodiscard]] std::uint32_t checked_i2p_quantity_or_throw(
    std::uint64_t value,
    std::string_view label) {
    if (value == 0U || value > kMaximumI2pTunnelQuantity) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, 16]");
    }
    return static_cast<std::uint32_t>(value);
}

[[nodiscard]] fs::path absolute_path_or_throw(
    std::string value,
    std::string_view label) {
    fs::path path(std::move(value));
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path || path.filename().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute path");
    }
    return path;
}

void require_existing_regular_file_or_throw(
    const fs::path& path,
    std::string_view label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error || !fs::is_regular_file(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            std::string(label) +
            " must name an existing non-symlink regular file");
    }
}

[[nodiscard]] std::string read_i2p_private_destination_or_throw(
    const Json& route,
    std::string_view label) {
    const Json* path_value = optional_member(route, "private_destination_file");
    if (path_value == nullptr) return "TRANSIENT";
    if (!path_value->is_string() || path_value->s.empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " private_destination_file must be a nonempty string");
    }
    const fs::path path = absolute_path_or_throw(
        path_value->s, child_label(label, "private_destination_file"));
    std::string destination =
        read_sync_bounded_private_regular_file_no_symlink_or_throw(
            path, kMaximumI2pPrivateDestinationBytes,
            child_label(label, "private destination"));
    if (destination.ends_with('\n')) {
        destination.pop_back();
        if (destination.ends_with('\r')) destination.pop_back();
    }
    if (destination.empty()) {
        throw std::invalid_argument(
            std::string(label) + " private destination file is empty");
    }
    return destination;
}

[[nodiscard]] SyncReplicaStreamRoute route_from_json_or_throw(
    const Json& route,
    std::string_view label) {
    require_object_or_throw(route, label);
    const std::string kind = required_string_or_throw(route, "kind", label);
    SyncReplicaStreamRoute result;
    if (kind == "direct") {
        require_exact_object_keys_or_throw(
            route, {"kind", "address", "port"}, {}, label);
        result = SyncReplicaDirectTcpRoute{
            SyncReplicaNumericStreamEndpoint{
                required_string_or_throw(route, "address", label),
                checked_port_or_throw(
                    required_uint64_or_throw(route, "port", label),
                    child_label(label, "port"))}};
    } else if (kind == "tor") {
        require_exact_object_keys_or_throw(
            route,
            {"kind", "onion_address", "onion_port", "isolation_token"},
            {"socks_address", "socks_port"}, label);
        result = SyncReplicaTorSocks5Route{
            .proxy = {
                optional_string_or(
                    route, "socks_address", "127.0.0.1", label),
                checked_port_or_throw(
                    optional_uint64_or(route, "socks_port", 9050U, label),
                    child_label(label, "socks_port"))},
            .onion_service =
                required_string_or_throw(route, "onion_address", label),
            .service_port = checked_port_or_throw(
                required_uint64_or_throw(route, "onion_port", label),
                child_label(label, "onion_port")),
            .isolation_token =
                required_string_or_throw(route, "isolation_token", label)};
    } else if (kind == "i2p") {
        require_exact_object_keys_or_throw(
            route,
            {"kind", "destination", "session_id"},
            {"sam_address", "sam_port", "private_destination_file",
             "inbound_quantity", "outbound_quantity"},
            label);
        result = SyncReplicaI2pSamRoute{
            .bridge = {
                optional_string_or(
                    route, "sam_address", "127.0.0.1", label),
                checked_port_or_throw(
                    optional_uint64_or(route, "sam_port", 7656U, label),
                    child_label(label, "sam_port"))},
            .session_id = required_string_or_throw(route, "session_id", label),
            .peer_destination =
                required_string_or_throw(route, "destination", label),
            .session_destination =
                read_i2p_private_destination_or_throw(route, label),
            .inbound_quantity = checked_i2p_quantity_or_throw(
                optional_uint64_or(
                    route, "inbound_quantity",
                    kDefaultI2pTunnelQuantity, label),
                child_label(label, "inbound_quantity")),
            .outbound_quantity = checked_i2p_quantity_or_throw(
                optional_uint64_or(
                    route, "outbound_quantity",
                    kDefaultI2pTunnelQuantity, label),
                child_label(label, "outbound_quantity"))};
    } else {
        throw std::invalid_argument(
            std::string(label) + " kind must be direct, tor, or i2p");
    }
    validate_sync_replica_stream_route_or_throw(result, label);
    return result;
}

[[nodiscard]] SyncReplicaPeerIngress ingress_from_json_or_throw(
    const Json& ingress,
    std::string_view label) {
    require_object_or_throw(ingress, label);
    const std::string kind = required_string_or_throw(
        ingress, "kind", label);
    SyncReplicaPeerIngress result;
    if (kind == "direct") {
        require_exact_object_keys_or_throw(
            ingress, {"kind"}, {}, label);
        result = SyncReplicaDirectTcpIngress{};
    } else if (kind == "tor") {
        require_exact_object_keys_or_throw(
            ingress, {"kind", "onion_address", "onion_port"}, {}, label);
        result = SyncReplicaTorOnionServiceIngress{
            .onion_service = required_string_or_throw(
                ingress, "onion_address", label),
            .service_port = checked_port_or_throw(
                required_uint64_or_throw(ingress, "onion_port", label),
                child_label(label, "onion_port"))};
    } else if (kind == "i2p") {
        require_exact_object_keys_or_throw(
            ingress,
            {"kind", "session_id", "private_destination_file"},
            {"sam_address", "sam_port", "inbound_quantity",
             "outbound_quantity"},
            label);
        result = SyncReplicaI2pSamIngress{
            .bridge = {
                optional_string_or(
                    ingress, "sam_address", "127.0.0.1", label),
                checked_port_or_throw(
                    optional_uint64_or(ingress, "sam_port", 7656U, label),
                    child_label(label, "sam_port"))},
            .session_id = required_string_or_throw(
                ingress, "session_id", label),
            .session_destination =
                read_i2p_private_destination_or_throw(ingress, label),
            .inbound_quantity = checked_i2p_quantity_or_throw(
                optional_uint64_or(
                    ingress, "inbound_quantity",
                    kDefaultI2pTunnelQuantity, label),
                child_label(label, "inbound_quantity")),
            .outbound_quantity = checked_i2p_quantity_or_throw(
                optional_uint64_or(
                    ingress, "outbound_quantity",
                    kDefaultI2pTunnelQuantity, label),
                child_label(label, "outbound_quantity"))};
    } else {
        throw std::invalid_argument(
            std::string(label) + " kind must be direct, tor, or i2p");
    }
    return result;
}

[[nodiscard]] SyncReplicaTlsPeerPolicy peer_from_json_or_throw(
    const Json& peer,
    std::string_view label) {
    require_exact_object_keys_or_throw(
        peer, {"device_id", "epoch", "spki_sha256"}, {}, label);
    SyncReplicaActor actor{
        required_string_or_throw(peer, "device_id", label),
        required_uint64_or_throw(peer, "epoch", label)};
    if (!sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(std::string(label) + " actor is invalid");
    }
    std::string spki = required_string_or_throw(peer, "spki_sha256", label);
    if (!is_lowercase_sha256_hex(spki)) {
        throw std::invalid_argument(
            std::string(label) + " spki_sha256 must be lowercase SHA-256");
    }
    return {std::move(actor), std::move(spki)};
}

[[nodiscard]] SyncReplicaPeerServiceTlsFiles tls_from_json_or_throw(
    const Json& tls,
    std::string_view label) {
    require_exact_object_keys_or_throw(
        tls, {"certificate", "private_key", "ca_file"}, {}, label);
    SyncReplicaPeerServiceTlsFiles result{
        absolute_path_or_throw(
            required_string_or_throw(tls, "certificate", label),
            child_label(label, "certificate")),
        absolute_path_or_throw(
            required_string_or_throw(tls, "private_key", label),
            child_label(label, "private_key")),
        absolute_path_or_throw(
            required_string_or_throw(tls, "ca_file", label),
            child_label(label, "ca_file"))};
    validate_sync_replica_peer_service_tls_files_or_throw(result, label);
    return result;
}

[[nodiscard]] SyncReplicaNumericStreamEndpoint listen_from_json_or_throw(
    const Json& listen,
    std::string_view label) {
    require_exact_object_keys_or_throw(
        listen, {"address", "port"}, {}, label);
    SyncReplicaNumericStreamEndpoint endpoint{
        required_string_or_throw(listen, "address", label),
        checked_port_or_throw(
            required_uint64_or_throw(listen, "port", label),
            child_label(label, "port"))};
    (void)sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
        endpoint, label);
    return endpoint;
}

[[nodiscard]] SyncReplicaFolderConvergencePassLimits
folder_limits_from_json_or_throw(
    const Json* folder,
    const SyncReplicaDeploymentManifest& deployment,
    std::string_view label) {
    SyncReplicaFolderConvergencePassLimits limits =
        sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            deployment.max_payload_bytes,
            child_label(label, "deployment folder limits"));
    if (folder == nullptr) return limits;
    require_exact_object_keys_or_throw(
        *folder, {},
        {"maximum_entries", "maximum_regular_files", "maximum_file_bytes",
         "maximum_total_file_bytes", "maximum_relative_path_bytes",
         "maximum_directory_depth", "maximum_remote_paths",
         "maximum_remote_inspection_paths"},
        label);
    limits.maximum_entries = optional_uint64_or(
        *folder, "maximum_entries", limits.maximum_entries, label);
    limits.maximum_regular_files = optional_uint64_or(
        *folder, "maximum_regular_files", limits.maximum_regular_files,
        label);
    limits.maximum_file_bytes = optional_uint64_or(
        *folder, "maximum_file_bytes", limits.maximum_file_bytes, label);
    limits.maximum_total_file_bytes = optional_uint64_or(
        *folder, "maximum_total_file_bytes",
        limits.maximum_total_file_bytes, label);
    limits.maximum_relative_path_bytes = optional_uint64_or(
        *folder, "maximum_relative_path_bytes",
        limits.maximum_relative_path_bytes, label);
    limits.maximum_directory_depth = optional_uint64_or(
        *folder, "maximum_directory_depth",
        limits.maximum_directory_depth, label);
    limits.maximum_remote_paths = optional_uint64_or(
        *folder, "maximum_remote_paths",
        limits.maximum_remote_paths, label);
    limits.maximum_remote_inspection_paths = optional_uint64_or(
        *folder, "maximum_remote_inspection_paths",
        limits.maximum_remote_inspection_paths, label);
    if (limits.maximum_file_bytes > deployment.max_payload_bytes) {
        throw std::invalid_argument(
            std::string(label) +
            " maximum_file_bytes exceeds manifest max_payload_bytes");
    }
    return limits;
}

[[nodiscard]] SyncReplicaPeerServiceLimits service_limits_from_json_or_throw(
    const Json* service,
    const SyncReplicaFolderConvergencePassLimits& folder_limits,
    SyncReplicaStreamRouteKind route_kind,
    SyncReplicaPeerIngressKind ingress_kind,
    std::string_view label) {
    SyncReplicaPeerServiceLimits limits;
    limits.folder_limits = folder_limits;
    const std::uint64_t default_timeout =
        route_kind == SyncReplicaStreamRouteKind::I2pSam
        ? kDefaultI2pTimeoutSeconds
        : kDefaultTimeoutSeconds;
    const std::uint64_t default_ingress_timeout =
        ingress_kind == SyncReplicaPeerIngressKind::I2pSamAccept
        ? kDefaultI2pTimeoutSeconds
        : kDefaultTimeoutSeconds;
    if (service == nullptr) {
        limits.stage_timeout_seconds = default_timeout;
        limits.cycle_runtime_seconds = default_timeout * 6U;
        limits.inbound_stage_timeout_seconds = default_timeout;
        limits.ingress_setup_timeout_seconds = default_ingress_timeout;
        limits.repair_interval_milliseconds = 30000U;
        limits.retry_initial_milliseconds = 1000U;
        limits.retry_maximum_milliseconds = 60000U;
        return limits;
    }
    require_exact_object_keys_or_throw(
        *service, {},
        {"timeout_seconds", "cycle_runtime_seconds", "max_round_trips",
         "max_source_resets", "inbound_timeout_seconds",
         "inbound_max_round_trips", "accept_poll_milliseconds",
         "scan_interval_seconds", "retry_initial_seconds",
         "retry_maximum_seconds", "ingress_timeout_seconds",
         "maximum_cycles", "maximum_service_runtime_seconds"},
        label);
    limits.stage_timeout_seconds = optional_uint64_or(
        *service, "timeout_seconds", default_timeout, label);
    if (limits.stage_timeout_seconds == 0U ||
        limits.stage_timeout_seconds > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            std::string(label) + " timeout_seconds must be in [1, 3600]");
    }
    if (route_kind == SyncReplicaStreamRouteKind::I2pSam &&
        limits.stage_timeout_seconds < kMinimumI2pTimeoutSeconds) {
        throw std::invalid_argument(
            std::string(label) +
            " timeout_seconds must be at least 180 for I2P");
    }
    limits.cycle_runtime_seconds = optional_uint64_or(
        *service, "cycle_runtime_seconds",
        limits.stage_timeout_seconds * 6U, label);
    if (limits.cycle_runtime_seconds == 0U ||
        limits.cycle_runtime_seconds > kMaximumCycleRuntimeSeconds) {
        throw std::invalid_argument(
            std::string(label) +
            " cycle_runtime_seconds must be in [1, 86400]");
    }
    limits.max_round_trips = optional_uint64_or(
        *service, "max_round_trips",
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips, label);
    limits.max_source_resets = optional_uint64_or(
        *service, "max_source_resets",
        kSyncReplicaReconciliationTlsDefaultMaxSourceResets, label);
    limits.inbound_stage_timeout_seconds = optional_uint64_or(
        *service, "inbound_timeout_seconds",
        limits.stage_timeout_seconds, label);
    limits.inbound_max_round_trips = optional_uint64_or(
        *service, "inbound_max_round_trips",
        limits.max_round_trips, label);
    limits.ingress_setup_timeout_seconds = optional_uint64_or(
        *service, "ingress_timeout_seconds",
        default_ingress_timeout, label);
    if (limits.ingress_setup_timeout_seconds == 0U ||
        limits.ingress_setup_timeout_seconds > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            std::string(label) +
            " ingress_timeout_seconds must be in [1, 3600]");
    }
    if (ingress_kind == SyncReplicaPeerIngressKind::I2pSamAccept &&
        limits.ingress_setup_timeout_seconds < kMinimumI2pTimeoutSeconds) {
        throw std::invalid_argument(
            std::string(label) +
            " ingress_timeout_seconds must be at least 180 for I2P");
    }
    limits.accept_window_milliseconds = optional_uint64_or(
        *service, "accept_poll_milliseconds", 250U, label);

    const auto seconds_to_milliseconds = [&](std::string_view key,
                                             std::uint64_t fallback) {
        const std::uint64_t seconds = optional_uint64_or(
            *service, key, fallback, label);
        if (seconds == 0U || seconds > 3600U) {
            throw std::invalid_argument(
                child_label(label, key) + " must be in [1, 3600]");
        }
        return seconds * 1000U;
    };
    limits.repair_interval_milliseconds = seconds_to_milliseconds(
        "scan_interval_seconds", 30U);
    limits.retry_initial_milliseconds = seconds_to_milliseconds(
        "retry_initial_seconds", 1U);
    limits.retry_maximum_milliseconds = seconds_to_milliseconds(
        "retry_maximum_seconds", 60U);
    return limits;
}

void validate_optional_stop_limits_or_throw(
    const std::optional<std::uint64_t>& maximum_cycles,
    const std::optional<std::uint64_t>& maximum_runtime_seconds,
    std::string_view label) {
    if (maximum_cycles.has_value() &&
        (*maximum_cycles == 0U || *maximum_cycles > kMaximumCycles)) {
        throw std::invalid_argument(
            std::string(label) + " maximum_cycles must be in [1, 1000000]");
    }
    if (maximum_runtime_seconds.has_value() &&
        (*maximum_runtime_seconds == 0U ||
         *maximum_runtime_seconds > kMaximumServiceRuntimeSeconds)) {
        throw std::invalid_argument(
            std::string(label) +
            " maximum_service_runtime_seconds must be in [1, 86400]");
    }
}

}  // namespace

void validate_sync_replica_peer_service_tls_files_or_throw(
    const SyncReplicaPeerServiceTlsFiles& tls,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer service TLS-file label is empty");
    }
    require_existing_regular_file_or_throw(
        tls.certificate, child_label(label, "certificate"));
    require_existing_regular_file_or_throw(
        tls.private_key, child_label(label, "private_key"));
    require_existing_regular_file_or_throw(
        tls.ca_file, child_label(label, "ca_file"));
    // The key's owner-only mode and bounded identity are part of the durable
    // launch boundary, not merely a late TLS-loader concern. Callers that
    // publish immutable configurations must prove this before publication.
    (void)read_sync_bounded_private_regular_file_no_symlink_or_throw(
        tls.private_key, kSyncReplicaPeerServiceTlsFileMaximumBytes,
        child_label(label, "private_key"));
}

void validate_sync_replica_peer_service_launch_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    bool require_durable_configuration_and_status_socket,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer service configuration label is empty");
    }
    if (configuration.configuration_schema !=
            kSyncReplicaLinkedPeerServiceConfigurationSchema &&
        configuration.configuration_schema !=
            kSyncReplicaLinkedPeerServiceConfigurationLegacySchema) {
        throw std::invalid_argument(
            std::string(label) + " configuration schema is unsupported");
    }
    if (configuration.configuration_schema ==
            kSyncReplicaLinkedPeerServiceConfigurationLegacySchema &&
        sync_replica_peer_ingress_kind(configuration.ingress) !=
            SyncReplicaPeerIngressKind::DirectTcp) {
        throw std::invalid_argument(
            std::string(label) +
            " legacy v1 configuration may only use direct ingress");
    }
    if (require_durable_configuration_and_status_socket &&
        (!configuration.configuration_path.has_value() ||
         !configuration.status_socket_path.has_value())) {
        throw std::invalid_argument(
            std::string(label) +
            " requires a durable configuration path and status socket");
    }
    if (configuration.configuration_path.has_value()) {
        (void)absolute_path_or_throw(
            configuration.configuration_path->generic_string(),
            child_label(label, "configuration_path"));
    }
    validate_sync_replica_deployment_manifest_or_throw(
        configuration.deployment, child_label(label, "deployment"));
    if (!sync_id_is_valid(configuration.expected_peer.actor.device_id) ||
        configuration.expected_peer.actor.epoch == 0U ||
        !is_lowercase_sha256_hex(configuration.expected_peer.spki_sha256)) {
        throw std::invalid_argument(
            std::string(label) + " expected peer identity is invalid");
    }
    validate_sync_replica_peer_service_tls_files_or_throw(
        configuration.tls, child_label(label, "tls"));
    validate_sync_replica_stream_route_or_throw(
        configuration.route, child_label(label, "route"));
    (void)sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
        configuration.listen_endpoint, child_label(label, "listen"));
    validate_sync_replica_peer_ingress_or_throw(
        configuration.ingress, configuration.listen_endpoint,
        child_label(label, "ingress"));
    if (const auto* outbound_i2p =
            std::get_if<SyncReplicaI2pSamRoute>(&configuration.route)) {
        if (const auto* inbound_i2p =
                std::get_if<SyncReplicaI2pSamIngress>(
                    &configuration.ingress)) {
            // session_id is a human-recognizable base, not the bridge-global
            // runtime ID. Each outbound connector and inbound acceptor appends
            // an independently generated bounded suffix when it acquires SAM
            // authority, so one service may safely use the same configured
            // base in both directions. Persistent destinations are different:
            // two sessions still must not claim the same cryptographic I2P
            // identity on one bridge.
            if (outbound_i2p->bridge == inbound_i2p->bridge &&
                outbound_i2p->session_destination != "TRANSIENT" &&
                outbound_i2p->session_destination ==
                    inbound_i2p->session_destination) {
                throw std::invalid_argument(
                    std::string(label) +
                    " outbound and inbound I2P sessions must not claim the "
                    "same persistent destination on one SAM bridge");
            }
        }
    }
    validate_sync_replica_peer_service_limits_or_throw(
        configuration.limits, child_label(label, "limits"));
    if (require_durable_configuration_and_status_socket) {
        const std::uint64_t network_horizon =
            sync_replica_peer_service_network_step_horizon_seconds_or_throw(
                configuration.limits,
                child_label(label, "installed_service"));
        if (network_horizon >
            kSyncReplicaInstalledServiceMaximumNetworkStepSeconds) {
            throw std::invalid_argument(
                std::string(label) +
                " network step horizon exceeds the installed service "
                "graceful-stop policy of " +
                std::to_string(
                    kSyncReplicaInstalledServiceMaximumNetworkStepSeconds) +
                " seconds");
        }
    }
    if (configuration.limits.folder_limits.maximum_file_bytes >
        configuration.deployment.max_payload_bytes) {
        throw std::invalid_argument(
            std::string(label) +
            " maximum file bytes exceeds deployment payload ceiling");
    }
    if (configuration.status_socket_path.has_value()) {
        (void)absolute_path_or_throw(
            configuration.status_socket_path->generic_string(),
            child_label(label, "status_socket"));
        preflight_sync_local_status_socket_or_throw(
            *configuration.status_socket_path,
            child_label(label, "status_socket"));
    }
    validate_optional_stop_limits_or_throw(
        configuration.maximum_cycles,
        configuration.maximum_service_runtime_seconds,
        label);
}

SyncReplicaPeerServiceLaunchConfiguration
read_sync_replica_linked_peer_service_configuration_or_throw(
    const fs::path& absolute_configuration_path,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica linked-peer configuration label is empty");
    }
    const fs::path configuration_path = absolute_path_or_throw(
        absolute_configuration_path.generic_string(),
        child_label(label, "path"));
    const std::string exact =
        read_sync_bounded_private_regular_file_no_symlink_or_throw(
            configuration_path,
            kSyncReplicaLinkedPeerServiceConfigurationMaximumBytes,
            child_label(label, "file"));
    Json root;
    try {
        root = parse_json_text(exact);
    } catch (const std::runtime_error& error) {
        throw std::invalid_argument(
            std::string(label) + " is not valid JSON: " + error.what());
    }
    require_object_or_throw(root, label);
    const std::string schema = required_string_or_throw(root, "schema", label);
    const bool current_schema =
        schema == kSyncReplicaLinkedPeerServiceConfigurationSchema;
    const bool legacy_schema =
        schema == kSyncReplicaLinkedPeerServiceConfigurationLegacySchema;
    if (!current_schema && !legacy_schema) {
        throw std::invalid_argument(
            std::string(label) + " schema is unsupported");
    }
    if (current_schema) {
        require_exact_object_keys_or_throw(
            root,
            {"schema", "manifest", "peer", "tls", "listen", "route",
             "ingress", "status_socket"},
            {"folder_limits", "service"},
            label);
    } else {
        require_exact_object_keys_or_throw(
            root,
            {"schema", "manifest", "peer", "tls", "listen", "route",
             "status_socket"},
            {"folder_limits", "service"},
            label);
    }

    const fs::path manifest_path = absolute_path_or_throw(
        required_string_or_throw(root, "manifest", label),
        child_label(label, "manifest"));
    SyncReplicaDeploymentManifest deployment =
        read_sync_replica_deployment_manifest_or_throw(
            manifest_path, child_label(label, "manifest"));
    SyncReplicaStreamRoute route = route_from_json_or_throw(
        required_member_or_throw(root, "route", label),
        child_label(label, "route"));
    SyncReplicaNumericStreamEndpoint listen_endpoint =
        listen_from_json_or_throw(
            required_member_or_throw(root, "listen", label),
            child_label(label, "listen"));
    SyncReplicaPeerIngress ingress = current_schema
        ? ingress_from_json_or_throw(
              required_member_or_throw(root, "ingress", label),
              child_label(label, "ingress"))
        : SyncReplicaPeerIngress{SyncReplicaDirectTcpIngress{}};
    validate_sync_replica_peer_ingress_or_throw(
        ingress, listen_endpoint, child_label(label, "ingress"));
    const SyncReplicaFolderConvergencePassLimits folder_limits =
        folder_limits_from_json_or_throw(
            optional_member(root, "folder_limits"), deployment,
            child_label(label, "folder_limits"));
    const Json* service = optional_member(root, "service");
    SyncReplicaPeerServiceLimits limits = service_limits_from_json_or_throw(
        service, folder_limits, sync_replica_stream_route_kind(route),
        sync_replica_peer_ingress_kind(ingress),
        child_label(label, "service"));

    SyncReplicaPeerServiceLaunchConfiguration configuration{
        .configuration_schema = schema,
        .configuration_path = configuration_path,
        .deployment = std::move(deployment),
        .expected_peer = peer_from_json_or_throw(
            required_member_or_throw(root, "peer", label),
            child_label(label, "peer")),
        .tls = tls_from_json_or_throw(
            required_member_or_throw(root, "tls", label),
            child_label(label, "tls")),
        .route = std::move(route),
        .ingress = std::move(ingress),
        .listen_endpoint = std::move(listen_endpoint),
        .status_socket_path = absolute_path_or_throw(
            required_string_or_throw(root, "status_socket", label),
            child_label(label, "status_socket")),
        .limits = std::move(limits),
        .maximum_cycles = service == nullptr
            ? std::nullopt
            : optional_uint64(*service, "maximum_cycles",
                              child_label(label, "service")),
        .maximum_service_runtime_seconds = service == nullptr
            ? std::nullopt
            : optional_uint64(
                  *service, "maximum_service_runtime_seconds",
                  child_label(label, "service"))};
    validate_sync_replica_peer_service_launch_configuration_or_throw(
        configuration, true, label);
    return configuration;
}

}  // namespace anonsync

#endif
