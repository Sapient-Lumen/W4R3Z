#include "sync_replica_peer_service_provisioning.hpp"

#if !defined(_WIN32)

#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_replica_stream_connector.hpp"

#include <cstdint>
#include <exception>
#include <filesystem>
#include <iomanip>
#include <optional>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <variant>

namespace anonsync {
namespace {

namespace fs = std::filesystem;
constexpr std::uint64_t kMaximumI2pPrivateDestinationBytes = 8192U;

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    std::string_view value) noexcept {
    return {
        reinterpret_cast<const unsigned char*>(value.data()), value.size()};
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

[[nodiscard]] fs::path normalized_absolute_file_or_throw(
    const fs::path& path,
    std::string_view label) {
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path || path.filename().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute file path");
    }
    return path;
}

[[nodiscard]] std::string read_private_destination_or_throw(
    const fs::path& selected,
    std::string_view label) {
    const fs::path path = normalized_absolute_file_or_throw(selected, label);
    std::string exact =
        read_sync_bounded_private_regular_file_no_symlink_or_throw(
            path, kMaximumI2pPrivateDestinationBytes, std::string(label));
    if (exact.ends_with('\n')) {
        exact.pop_back();
        if (exact.ends_with('\r')) exact.pop_back();
    }
    if (exact.empty()) {
        throw std::invalid_argument(
            std::string(label) + " is empty");
    }
    return exact;
}

void validate_i2p_source_files_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files,
    std::string_view label) {
    if (const auto* route =
            std::get_if<SyncReplicaI2pSamRoute>(&configuration.route)) {
        if (source_files.outbound_i2p_private_destination_file.has_value()) {
            const std::string exact = read_private_destination_or_throw(
                *source_files.outbound_i2p_private_destination_file,
                child_label(label, "outbound I2P private destination"));
            if (exact != route->session_destination) {
                throw std::invalid_argument(
                    std::string(label) +
                    " outbound I2P private destination bytes changed");
            }
        } else if (route->session_destination != "TRANSIENT") {
            throw std::invalid_argument(
                std::string(label) +
                " persistent outbound I2P destination requires its source file");
        }
    } else if (
        source_files.outbound_i2p_private_destination_file.has_value()) {
        throw std::invalid_argument(
            std::string(label) +
            " outbound I2P private destination file is set for a non-I2P route");
    }

    if (const auto* ingress =
            std::get_if<SyncReplicaI2pSamIngress>(&configuration.ingress)) {
        if (!source_files.inbound_i2p_private_destination_file.has_value()) {
            throw std::invalid_argument(
                std::string(label) +
                " native I2P ingress requires its persistent destination file");
        }
        const std::string exact = read_private_destination_or_throw(
            *source_files.inbound_i2p_private_destination_file,
            child_label(label, "inbound I2P private destination"));
        if (exact != ingress->session_destination) {
            throw std::invalid_argument(
                std::string(label) +
                " inbound I2P private destination bytes changed");
        }
    } else if (source_files.inbound_i2p_private_destination_file.has_value()) {
        throw std::invalid_argument(
            std::string(label) +
            " inbound I2P private destination file is set for non-I2P ingress");
    }
}

void append_route_json(
    std::ostringstream& output,
    const SyncReplicaStreamRoute& route,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files) {
    std::visit(
        [&](const auto& selected) {
            using Route = std::decay_t<decltype(selected)>;
            if constexpr (std::is_same_v<Route, SyncReplicaDirectTcpRoute>) {
                output << "{\"kind\":\"direct\",\"address\":"
                       << json_quote(selected.endpoint.numeric_address)
                       << ",\"port\":" << selected.endpoint.port << '}';
            } else if constexpr (
                std::is_same_v<Route, SyncReplicaTorSocks5Route>) {
                output << "{\"kind\":\"tor\",\"onion_address\":"
                       << json_quote(selected.onion_service)
                       << ",\"onion_port\":" << selected.service_port
                       << ",\"isolation_token\":"
                       << json_quote(selected.isolation_token)
                       << ",\"socks_address\":"
                       << json_quote(selected.proxy.numeric_address)
                       << ",\"socks_port\":" << selected.proxy.port << '}';
            } else {
                output << "{\"kind\":\"i2p\",\"destination\":"
                       << json_quote(selected.peer_destination)
                       << ",\"session_id\":"
                       << json_quote(selected.session_id)
                       << ",\"sam_address\":"
                       << json_quote(selected.bridge.numeric_address)
                       << ",\"sam_port\":" << selected.bridge.port;
                if (source_files.outbound_i2p_private_destination_file
                        .has_value()) {
                    output << ",\"private_destination_file\":"
                           << json_quote(
                                  source_files
                                      .outbound_i2p_private_destination_file
                                      ->generic_string());
                }
                output << ",\"inbound_quantity\":"
                       << selected.inbound_quantity
                       << ",\"outbound_quantity\":"
                       << selected.outbound_quantity << '}';
            }
        },
        route);
}

void append_ingress_json(
    std::ostringstream& output,
    const SyncReplicaPeerIngress& ingress,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files) {
    std::visit(
        [&](const auto& selected) {
            using Ingress = std::decay_t<decltype(selected)>;
            if constexpr (
                std::is_same_v<Ingress, SyncReplicaDirectTcpIngress>) {
                output << "{\"kind\":\"direct\"}";
            } else if constexpr (
                std::is_same_v<Ingress, SyncReplicaTorOnionServiceIngress>) {
                output << "{\"kind\":\"tor\",\"onion_address\":"
                       << json_quote(selected.onion_service)
                       << ",\"onion_port\":" << selected.service_port << '}';
            } else {
                output << "{\"kind\":\"i2p\",\"session_id\":"
                       << json_quote(selected.session_id)
                       << ",\"private_destination_file\":"
                       << json_quote(
                              source_files
                                  .inbound_i2p_private_destination_file
                                  ->generic_string())
                       << ",\"sam_address\":"
                       << json_quote(selected.bridge.numeric_address)
                       << ",\"sam_port\":" << selected.bridge.port
                       << ",\"inbound_quantity\":"
                       << selected.inbound_quantity
                       << ",\"outbound_quantity\":"
                       << selected.outbound_quantity << '}';
            }
        },
        ingress);
}

[[nodiscard]] std::uint64_t exact_seconds_or_throw(
    std::uint64_t milliseconds,
    std::string_view label) {
    if (milliseconds == 0U || milliseconds % 1000U != 0U) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a positive whole number of seconds");
    }
    return milliseconds / 1000U;
}

void require_same_launch_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& expected,
    const SyncReplicaPeerServiceLaunchConfiguration& observed,
    std::string_view label) {
    if (observed.configuration_schema != expected.configuration_schema ||
        observed.configuration_path != expected.configuration_path ||
        observed.deployment != expected.deployment ||
        observed.expected_peer != expected.expected_peer ||
        observed.tls != expected.tls || observed.route != expected.route ||
        observed.ingress != expected.ingress ||
        observed.listen_endpoint != expected.listen_endpoint ||
        observed.status_socket_path != expected.status_socket_path ||
        observed.limits != expected.limits ||
        observed.maximum_cycles != expected.maximum_cycles ||
        observed.maximum_service_runtime_seconds !=
            expected.maximum_service_runtime_seconds) {
        throw std::runtime_error(
            std::string(label) +
            " readback does not describe the requested service launch");
    }
}

[[nodiscard]] SyncReplicaPeerServiceProvisioningResult
readback_provisioning_result_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& expected,
    std::string exact,
    SyncReplicaPeerServiceConfigurationDisposition disposition,
    std::string_view label) {
    SyncReplicaPeerServiceLaunchConfiguration readback =
        read_sync_replica_linked_peer_service_configuration_or_throw(
            *expected.configuration_path, child_label(label, "readback"));
    require_same_launch_or_throw(
        expected, readback, child_label(label, "readback"));
    return {
        .launch = std::move(readback),
        .exact_configuration_bytes = std::move(exact),
        .disposition = disposition,
    };
}

}  // namespace

const char* sync_replica_peer_service_configuration_disposition_name(
    SyncReplicaPeerServiceConfigurationDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaPeerServiceConfigurationDisposition::Created:
            return "created";
        case SyncReplicaPeerServiceConfigurationDisposition::ResumedExact:
            return "resumed_exact";
    }
    return "invalid";
}

std::string encode_sync_replica_linked_peer_service_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica linked-peer configuration encoding label is empty");
    }
    if (configuration.configuration_schema !=
        kSyncReplicaLinkedPeerServiceConfigurationSchema) {
        throw std::invalid_argument(
            label + " can encode only the current v2 schema");
    }
    if (!configuration.configuration_path.has_value() ||
        !configuration.status_socket_path.has_value()) {
        throw std::invalid_argument(
            label +
            " requires exact durable configuration and status-socket paths");
    }
    validate_i2p_source_files_or_throw(
        configuration, source_files, label);
    validate_sync_replica_peer_service_launch_configuration_or_throw(
        configuration, true, label);

    const auto& limits = configuration.limits;
    std::ostringstream output;
    output
        << "{\"schema\":"
        << json_quote(configuration.configuration_schema)
        << ",\"manifest\":"
        << json_quote(configuration.deployment.manifest_path.generic_string())
        << ",\"peer\":{\"device_id\":"
        << json_quote(configuration.expected_peer.actor.device_id)
        << ",\"epoch\":" << configuration.expected_peer.actor.epoch
        << ",\"spki_sha256\":"
        << json_quote(configuration.expected_peer.spki_sha256)
        << "},\"tls\":{\"certificate\":"
        << json_quote(configuration.tls.certificate.generic_string())
        << ",\"private_key\":"
        << json_quote(configuration.tls.private_key.generic_string())
        << ",\"ca_file\":"
        << json_quote(configuration.tls.ca_file.generic_string())
        << "},\"listen\":{\"address\":"
        << json_quote(configuration.listen_endpoint.numeric_address)
        << ",\"port\":" << configuration.listen_endpoint.port
        << "},\"route\":";
    append_route_json(output, configuration.route, source_files);
    output << ",\"ingress\":";
    append_ingress_json(output, configuration.ingress, source_files);
    output
        << ",\"status_socket\":"
        << json_quote(configuration.status_socket_path->generic_string())
        << ",\"folder_limits\":{\"maximum_entries\":"
        << limits.folder_limits.maximum_entries
        << ",\"maximum_regular_files\":"
        << limits.folder_limits.maximum_regular_files
        << ",\"maximum_file_bytes\":"
        << limits.folder_limits.maximum_file_bytes
        << ",\"maximum_total_file_bytes\":"
        << limits.folder_limits.maximum_total_file_bytes
        << ",\"maximum_relative_path_bytes\":"
        << limits.folder_limits.maximum_relative_path_bytes
        << ",\"maximum_directory_depth\":"
        << limits.folder_limits.maximum_directory_depth
        << ",\"maximum_remote_paths\":"
        << limits.folder_limits.maximum_remote_paths
        << ",\"maximum_remote_inspection_paths\":"
        << limits.folder_limits.maximum_remote_inspection_paths
        << "},\"service\":{\"timeout_seconds\":"
        << limits.stage_timeout_seconds
        << ",\"cycle_runtime_seconds\":"
        << limits.cycle_runtime_seconds
        << ",\"max_round_trips\":" << limits.max_round_trips
        << ",\"max_source_resets\":" << limits.max_source_resets
        << ",\"inbound_timeout_seconds\":"
        << limits.inbound_stage_timeout_seconds
        << ",\"inbound_max_round_trips\":"
        << limits.inbound_max_round_trips
        << ",\"accept_poll_milliseconds\":"
        << limits.accept_window_milliseconds
        << ",\"scan_interval_seconds\":"
        << exact_seconds_or_throw(
               limits.repair_interval_milliseconds,
               child_label(label, "scan interval"))
        << ",\"retry_initial_seconds\":"
        << exact_seconds_or_throw(
               limits.retry_initial_milliseconds,
               child_label(label, "initial retry"))
        << ",\"retry_maximum_seconds\":"
        << exact_seconds_or_throw(
               limits.retry_maximum_milliseconds,
               child_label(label, "maximum retry"))
        << ",\"ingress_timeout_seconds\":"
        << limits.ingress_setup_timeout_seconds;
    if (configuration.maximum_cycles.has_value()) {
        output << ",\"maximum_cycles\":"
               << *configuration.maximum_cycles;
    }
    if (configuration.maximum_service_runtime_seconds.has_value()) {
        output << ",\"maximum_service_runtime_seconds\":"
               << *configuration.maximum_service_runtime_seconds;
    }
    output << "}}\n";

    const std::string exact = output.str();
    if (exact.size() >
        kSyncReplicaLinkedPeerServiceConfigurationMaximumBytes) {
        throw std::length_error(
            label + " exceeds the linked-peer configuration byte limit");
    }
    return exact;
}

SyncReplicaPeerServiceConfigurationInspection
inspect_sync_replica_linked_peer_service_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica linked-peer configuration inspection label is empty");
    }
    const std::string exact =
        encode_sync_replica_linked_peer_service_configuration_or_throw(
            configuration, source_files, child_label(label, "encoding"));
    const auto observed =
        reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            *configuration.configuration_path, byte_span(exact),
            child_label(label, "immutable reconciliation"));
    if (observed == SyncImmutableFileReconciliationOutcome::Absent) {
        return SyncReplicaPeerServiceConfigurationInspection::Absent;
    }
    if (observed ==
        SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        throw std::runtime_error(
            label + " existing configuration conflicts with the requested "
                    "linked-peer service");
    }
    (void)readback_provisioning_result_or_throw(
        configuration, exact,
        SyncReplicaPeerServiceConfigurationDisposition::ResumedExact,
        label);
    return SyncReplicaPeerServiceConfigurationInspection::ExistingExact;
}

SyncReplicaPeerServiceProvisioningResult
provision_sync_replica_linked_peer_service_configuration_or_throw(
    SyncReplicaPeerServiceLaunchConfiguration configuration,
    SyncReplicaPeerServiceProvisioningSourceFiles source_files,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica linked-peer configuration provisioning label is empty");
    }
    const std::string exact =
        encode_sync_replica_linked_peer_service_configuration_or_throw(
            configuration, source_files, child_label(label, "encoding"));
    const fs::path destination = *configuration.configuration_path;

    write_sync_json_file_atomically_create_new_no_symlink_or_throw(
        destination, exact, child_label(label, "publication"));
    return readback_provisioning_result_or_throw(
        configuration, exact,
        SyncReplicaPeerServiceConfigurationDisposition::Created, label);
}

SyncReplicaPeerServiceProvisioningResult
provision_or_resume_sync_replica_linked_peer_service_configuration_or_throw(
    SyncReplicaPeerServiceLaunchConfiguration configuration,
    SyncReplicaPeerServiceProvisioningSourceFiles source_files,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica linked-peer configuration create-or-resume label is empty");
    }
    const std::string exact =
        encode_sync_replica_linked_peer_service_configuration_or_throw(
            configuration, source_files, child_label(label, "encoding"));
    const fs::path destination = *configuration.configuration_path;

    const auto reconcile_exact = [&]() {
        return reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, byte_span(exact),
            child_label(label, "restart reconciliation"));
    };
    const auto initial = reconcile_exact();
    if (initial ==
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        return readback_provisioning_result_or_throw(
            configuration, exact,
            SyncReplicaPeerServiceConfigurationDisposition::ResumedExact,
            label);
    }
    if (initial == SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        throw std::runtime_error(
            label + " existing configuration conflicts with the requested "
                    "linked-peer service");
    }

    try {
        write_sync_json_file_atomically_create_new_no_symlink_or_throw(
            destination, exact, child_label(label, "publication"));
    } catch (...) {
        const std::exception_ptr publication_error = std::current_exception();
        const auto recovered = reconcile_exact();
        if (recovered ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            return readback_provisioning_result_or_throw(
                configuration, exact,
                SyncReplicaPeerServiceConfigurationDisposition::ResumedExact,
                label);
        }
        if (recovered ==
            SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
            throw std::runtime_error(
                label + " publication raced a conflicting linked-peer "
                        "configuration");
        }
        std::rethrow_exception(publication_error);
    }

    return readback_provisioning_result_or_throw(
        configuration, exact,
        SyncReplicaPeerServiceConfigurationDisposition::Created, label);
}

}  // namespace anonsync

#endif
