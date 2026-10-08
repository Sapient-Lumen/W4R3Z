#include "sync_replica_file_effect_identity.hpp"

#include "sha256_digest.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string_view>

namespace anonsync {
namespace {

[[nodiscard]] std::array<char, 8U> big_endian_u64(
    std::uint64_t value) noexcept {
    std::array<char, 8U> bytes{};
    for (std::size_t index = bytes.size(); index != 0U; --index) {
        bytes[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return bytes;
}

void digest_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    const auto bytes = big_endian_u64(value);
    digest.update(std::string_view(bytes.data(), bytes.size()));
}

void digest_field(Sha256DigestBuilder& digest, std::string_view value) {
    digest_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

}  // namespace

std::string make_sync_replica_file_effect_id_or_throw(
    const SyncReplicaOperation& operation) {
    validate_sync_replica_operation_or_throw(operation);
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            "sync replica file-effect identity requires a file operation");
    }
    Sha256DigestBuilder digest;
    digest.update("anonsync-replica-file-effect-id-v1");
    digest_field(digest, operation.folder_id);
    digest_field(digest, operation.operation_id);
    digest_field(digest, operation.canonical_path);
    digest_field(digest, operation.content_sha256);
    digest_u64(digest, operation.size_bytes);
    return digest.finish_hex();
}

}  // namespace anonsync
