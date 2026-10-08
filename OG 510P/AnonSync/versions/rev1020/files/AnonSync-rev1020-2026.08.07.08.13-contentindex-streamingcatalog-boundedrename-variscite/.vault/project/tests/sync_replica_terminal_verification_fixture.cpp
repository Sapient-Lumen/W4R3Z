#include "sha256_digest.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_payload_store.hpp"

#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

[[nodiscard]] std::uint64_t parse_uint64_or_throw(
    std::string_view value, std::string_view label) {
    if (value.empty()) {
        throw std::invalid_argument(std::string(label) + " must not be empty");
    }
    std::uint64_t result = 0U;
    for (const unsigned char byte : value) {
        if (byte < '0' || byte > '9') {
            throw std::invalid_argument(
                std::string(label) + " must contain only decimal digits");
        }
        const std::uint64_t digit = static_cast<std::uint64_t>(byte - '0');
        if (result > (std::numeric_limits<std::uint64_t>::max() - digit) / 10U) {
            throw std::out_of_range(std::string(label) + " exceeds uint64");
        }
        result = result * 10U + digit;
    }
    return result;
}

[[nodiscard]] std::string deterministic_payload_or_throw(
    std::uint64_t size_bytes, std::uint64_t salt) {
    if (size_bytes == 0U ||
        size_bytes > static_cast<std::uint64_t>(
                         std::numeric_limits<std::size_t>::max())) {
        throw std::invalid_argument(
            "terminal-verification fixture size is invalid");
    }
    std::string payload(static_cast<std::size_t>(size_bytes), '\0');
    std::uint64_t state = salt ^ 0x9e3779b97f4a7c15ULL;
    for (char& byte : payload) {
        state ^= state >> 12U;
        state ^= state << 25U;
        state ^= state >> 27U;
        byte = static_cast<char>((state * 0x2545f4914f6cdd1dULL) >> 56U);
    }
    return payload;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        std::filesystem::path manifest_path;
        std::uint64_t payload_bytes = 0U;
        std::uint64_t salt = 1U;
        for (int index = 1; index < argc; ++index) {
            const std::string_view argument(argv[index]);
            if (argument == "--manifest" && index + 1 < argc) {
                manifest_path = argv[++index];
            } else if (argument == "--payload-bytes" && index + 1 < argc) {
                payload_bytes = parse_uint64_or_throw(
                    argv[++index], "--payload-bytes");
            } else if (argument == "--salt" && index + 1 < argc) {
                salt = parse_uint64_or_throw(argv[++index], "--salt");
            } else {
                throw std::invalid_argument(
                    "usage: terminal-verification fixture --manifest ABSOLUTE "
                    "--payload-bytes N [--salt N]");
            }
        }
        if (manifest_path.empty() || !manifest_path.is_absolute()) {
            throw std::invalid_argument(
                "terminal-verification fixture requires an absolute manifest");
        }
        const anonsync::SyncReplicaDeploymentManifest manifest =
            anonsync::read_sync_replica_deployment_manifest_or_throw(
                manifest_path,
                "terminal-verification fixture deployment manifest");
        if (!manifest.payload_root.has_value()) {
            throw std::invalid_argument(
                "terminal-verification fixture deployment has no payload root");
        }
        if (payload_bytes == 0U || payload_bytes > manifest.max_payload_bytes) {
            throw std::invalid_argument(
                "terminal-verification fixture payload exceeds deployment ceiling");
        }

        std::string payload =
            deterministic_payload_or_throw(payload_bytes, salt);
        const std::string digest = anonsync::sha256_hex(payload);
        const auto limits =
            anonsync::sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
                manifest.max_payload_bytes,
                "terminal-verification fixture payload-store limits");
        anonsync::SyncReplicaFilePayloadStore store(
            anonsync::sync_replica_deployment_identity_or_throw(
                manifest, "terminal-verification fixture deployment identity"),
            *manifest.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "terminal-verification fixture payload store");
        const auto staged =
            store.stage_payload_prefix_deferring_terminal_verification_or_throw(
                digest, payload_bytes, 0U, digest, payload);
        if (staged.disposition !=
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress ||
            staged.next_offset_bytes != payload_bytes ||
            staged.accepted_range_bytes != payload_bytes ||
            staged.terminal_verification_steps != 0U ||
            staged.terminal_verification_verified_offset_bytes != 0U) {
            throw std::runtime_error(
                "terminal-verification fixture did not leave one deferred complete prefix");
        }
        std::cout
            << "{\"content_sha256\":\"" << digest
            << "\",\"payload_bytes\":" << payload_bytes
            << ",\"terminal_verification_steps\":0}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "terminal-verification fixture failed: "
                  << error.what() << '\n';
        return 1;
    }
}
