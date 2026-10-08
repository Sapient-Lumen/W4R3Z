#include "sync_replica_deployment_identity.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <array>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <string>

#include <openssl/err.h>
#include <openssl/rand.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::uint64_t kMaximumExactJsonInteger = 9007199254740991ULL;

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

void require_canonical_absolute_path(
    const fs::path& path,
    const std::string& label) {
    if (path.native().find(fs::path::value_type{}) !=
        fs::path::string_type::npos) {
        throw std::invalid_argument(label + " manifest_path contains NUL");
    }
    if (path.empty() || !path.is_absolute()) {
        throw std::invalid_argument(
            label + " manifest_path must be absolute");
    }
    if (path.lexically_normal() != path) {
        throw std::invalid_argument(
            label + " manifest_path must be lexically normalized");
    }
}

}  // namespace

bool sync_replica_deployment_id_is_valid(std::string_view value) noexcept {
    return is_lowercase_sha256_hex(value);
}

std::string generate_sync_replica_deployment_id_or_throw(
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "deployment ID generation label must not be empty");
    }
    std::array<unsigned char, 32U> bytes{};
    ERR_clear_error();
    if (RAND_bytes(bytes.data(), static_cast<int>(bytes.size())) != 1) {
        throw std::runtime_error(
            label + " could not generate a deployment ID: " +
            openssl_errors());
    }
    std::ostringstream encoded;
    encoded << std::hex << std::setfill('0');
    for (const unsigned char byte : bytes) {
        encoded << std::setw(2) << static_cast<unsigned int>(byte);
    }
    const std::string result = encoded.str();
    if (!sync_replica_deployment_id_is_valid(result)) {
        throw std::logic_error(
            label + " generated an invalid deployment ID");
    }
    return result;
}

void validate_sync_replica_deployment_identity_or_throw(
    const SyncReplicaDeploymentIdentity& identity,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "deployment identity validation label must not be empty");
    }
    if (!sync_replica_deployment_id_is_valid(identity.deployment_id)) {
        throw std::invalid_argument(
            label + " deployment_id must be 64 lowercase hexadecimal characters");
    }
    if (!is_lowercase_sha256_hex(identity.manifest_digest)) {
        throw std::invalid_argument(
            label + " manifest_digest must be lowercase SHA-256");
    }
    require_canonical_absolute_path(identity.manifest_path, label);
    if (!sync_id_is_valid(identity.folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync ID");
    }
    if (!sync_id_is_valid(identity.local_actor.device_id) ||
        identity.local_actor.epoch == 0U ||
        identity.local_actor.epoch > kMaximumExactJsonInteger) {
        throw std::invalid_argument(label + " local actor is invalid");
    }
}

}  // namespace anonsync
