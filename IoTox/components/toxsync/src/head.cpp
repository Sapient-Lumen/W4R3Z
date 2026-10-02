#include "toxsync/head.hpp"

#include "native_file.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <system_error>

#if defined(TOXSYNC_HAVE_OPENSSL)
#include <openssl/evp.h>
#endif

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {
namespace {

constexpr std::array<std::byte, 8> kStateMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'H'}, std::byte{'S'},
    std::byte{'T'}, std::byte{'A'}, std::byte{'T'}, std::byte{'E'},
};
constexpr std::uint16_t kStateVersion = 1U;
constexpr std::size_t kStateHeaderBytes = 12U;
constexpr std::size_t kStateBytes =
    kStateHeaderBytes + kMutableHeadBytes + 32U + 32U;

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

void write_u16_le(std::span<std::byte> output,
                  std::size_t offset,
                  std::uint16_t value) noexcept {
    output[offset] = static_cast<std::byte>(value & 0xffU);
    output[offset + 1U] = static_cast<std::byte>(value >> 8U);
}

[[nodiscard]] std::uint16_t read_u16_le(std::span<const std::byte> input,
                                        std::size_t offset) noexcept {
    return static_cast<std::uint16_t>(
        std::to_integer<unsigned char>(input[offset]) |
        (static_cast<std::uint16_t>(
             std::to_integer<unsigned char>(input[offset + 1U]))
         << 8U));
}

void ensure_parent(const std::filesystem::path& path) {
    const auto parent = path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
}

void sync_parent(const std::filesystem::path& path) {
#if defined(__unix__) || defined(__APPLE__)
    auto parent = path.parent_path();
    if (parent.empty()) parent = ".";
    const int descriptor = ::open(parent.c_str(), O_RDONLY | O_CLOEXEC);
    if (descriptor < 0) {
        throw std::runtime_error("cannot open mutable-head parent directory: " +
                                 parent.string() + ": " + std::strerror(errno));
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    (void)::close(descriptor);
    if (result != 0) {
        throw std::runtime_error("cannot fsync mutable-head parent directory: " +
                                 parent.string() + ": " + std::strerror(saved));
    }
#else
    (void)path;
#endif
}

[[nodiscard]] std::filesystem::path temporary_path_for(
    const std::filesystem::path& destination) {
#if defined(__unix__) || defined(__APPLE__)
    const auto process = static_cast<unsigned long long>(::getpid());
#else
    const auto process = 0ULL;
#endif
    auto result = destination;
    result += ".toxsync.tmp." + std::to_string(process);
    return result;
}

void atomic_replace(const std::filesystem::path& source,
                    const std::filesystem::path& destination) {
#if defined(__unix__) || defined(__APPLE__)
    if (::rename(source.c_str(), destination.c_str()) != 0) {
        throw std::runtime_error("cannot atomically publish mutable-head state: " +
                                 std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) {
        throw std::runtime_error("cannot publish mutable-head state: " + error.message());
    }
#endif
}

[[nodiscard]] bool default_verifier(void* context,
                                    const MutableHead&,
                                    std::span<const std::byte, kMutableHeadSigningBytes> body,
                                    std::span<const std::byte, 64> signature) {
    if (context == nullptr) return false;
    const auto* key = static_cast<const Ed25519PublicKey*>(context);
    return ed25519_verify(body, *key, signature);
}

} // namespace

bool ed25519_backend_available() noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    return true;
#else
    return false;
#endif
}

bool ed25519_generate_key(Ed25519PrivateKey& private_key,
                          Ed25519PublicKey& public_key) noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_PKEY_CTX* context = EVP_PKEY_CTX_new_id(EVP_PKEY_ED25519, nullptr);
    if (context == nullptr) return false;
    EVP_PKEY* key = nullptr;
    bool ok = EVP_PKEY_keygen_init(context) == 1 &&
              EVP_PKEY_keygen(context, &key) == 1 && key != nullptr;
    if (ok) {
        std::size_t private_size = private_key.bytes.size();
        std::size_t public_size = public_key.bytes.size();
        ok = EVP_PKEY_get_raw_private_key(
                 key,
                 reinterpret_cast<unsigned char*>(private_key.bytes.data()),
                 &private_size) == 1 &&
             private_size == private_key.bytes.size() &&
             EVP_PKEY_get_raw_public_key(
                 key,
                 reinterpret_cast<unsigned char*>(public_key.bytes.data()),
                 &public_size) == 1 &&
             public_size == public_key.bytes.size();
    }
    EVP_PKEY_free(key);
    EVP_PKEY_CTX_free(context);
    if (!ok) {
        private_key.bytes.fill(std::byte{0});
        public_key.bytes.fill(std::byte{0});
    }
    return ok;
#else
    (void)private_key;
    (void)public_key;
    return false;
#endif
}

bool ed25519_sign(std::span<const std::byte> message,
                  const Ed25519PrivateKey& private_key,
                  std::span<std::byte, 64> signature) noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_PKEY* key = EVP_PKEY_new_raw_private_key(
        EVP_PKEY_ED25519, nullptr,
        reinterpret_cast<const unsigned char*>(private_key.bytes.data()),
        private_key.bytes.size());
    if (key == nullptr) return false;
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr) {
        EVP_PKEY_free(key);
        return false;
    }
    bool ok = EVP_DigestSignInit(context, nullptr, nullptr, nullptr, key) == 1;
    std::size_t signature_size = signature.size();
    if (ok) {
        ok = EVP_DigestSign(
                 context,
                 reinterpret_cast<unsigned char*>(signature.data()),
                 &signature_size,
                 reinterpret_cast<const unsigned char*>(message.data()),
                 message.size()) == 1 &&
             signature_size == signature.size();
    }
    EVP_MD_CTX_free(context);
    EVP_PKEY_free(key);
    return ok;
#else
    (void)message;
    (void)private_key;
    (void)signature;
    return false;
#endif
}

bool ed25519_verify(std::span<const std::byte> message,
                    const Ed25519PublicKey& public_key,
                    std::span<const std::byte, 64> signature) noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_PKEY* key = EVP_PKEY_new_raw_public_key(
        EVP_PKEY_ED25519, nullptr,
        reinterpret_cast<const unsigned char*>(public_key.bytes.data()),
        public_key.bytes.size());
    if (key == nullptr) return false;
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr) {
        EVP_PKEY_free(key);
        return false;
    }
    bool ok = EVP_DigestVerifyInit(context, nullptr, nullptr, nullptr, key) == 1;
    if (ok) {
        ok = EVP_DigestVerify(
                 context,
                 reinterpret_cast<const unsigned char*>(signature.data()),
                 signature.size(),
                 reinterpret_cast<const unsigned char*>(message.data()),
                 message.size()) == 1;
    }
    EVP_MD_CTX_free(context);
    EVP_PKEY_free(key);
    return ok;
#else
    (void)message;
    (void)public_key;
    (void)signature;
    return false;
#endif
}

bool ed25519_public_key(const Ed25519PrivateKey& private_key,
                        Ed25519PublicKey& public_key) noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_PKEY* key = EVP_PKEY_new_raw_private_key(
        EVP_PKEY_ED25519, nullptr,
        reinterpret_cast<const unsigned char*>(private_key.bytes.data()),
        private_key.bytes.size());
    if (key == nullptr) return false;
    std::size_t size = public_key.bytes.size();
    const bool ok = EVP_PKEY_get_raw_public_key(
                        key,
                        reinterpret_cast<unsigned char*>(public_key.bytes.data()),
                        &size) == 1 &&
                    size == public_key.bytes.size();
    EVP_PKEY_free(key);
    return ok;
#else
    (void)private_key;
    (void)public_key;
    return false;
#endif
}

Digest256 mutable_head_record_digest(const MutableHead& head) {
    const auto encoded = encode_mutable_head(head);
    return sha256(encoded);
}

bool sign_mutable_head(MutableHead& head,
                       const Ed25519PrivateKey& private_key) noexcept {
    try {
        const auto body = encode_mutable_head_signing(head);
        return ed25519_sign(body, private_key, head.signature);
    } catch (...) {
        return false;
    }
}

bool verify_mutable_head(const MutableHead& head,
                         const Ed25519PublicKey& public_key) noexcept {
    try {
        const auto body = encode_mutable_head_signing(head);
        return ed25519_verify(body, public_key, head.signature);
    } catch (...) {
        return false;
    }
}

MutableHeadEvaluation evaluate_mutable_head(
    const MutableHead& candidate,
    const std::optional<MutableHead>& current,
    MutableHeadSignatureVerifier verifier,
    void* verifier_context,
    const MutableHeadPolicy& policy) {
    MutableHeadEvaluation result;
    result.candidate_record = mutable_head_record_digest(candidate);

    if (candidate.generation < policy.minimum_generation ||
        candidate.artifact_size > policy.maximum_artifact_size ||
        candidate.index_size > policy.maximum_index_size) {
        result.decision = HeadDecision::resource_limit;
        return result;
    }

    if (current.has_value()) {
        result.current_record = mutable_head_record_digest(*current);
        if (candidate.namespace_id != current->namespace_id) {
            result.decision = HeadDecision::wrong_namespace;
            return result;
        }
    }

    if (policy.require_signature) {
        if (verifier == nullptr) verifier = &default_verifier;
        const auto body = encode_mutable_head_signing(candidate);
        if (!verifier(verifier_context, candidate, body, candidate.signature)) {
            result.decision = HeadDecision::invalid_signature;
            return result;
        }
    }

    if (!current.has_value()) {
        if (policy.require_parent_link && !all_zero(candidate.parent.bytes) &&
            (candidate.flags & kHeadFlagSnapshot) == 0U) {
            result.decision = HeadDecision::parent_mismatch;
            return result;
        }
        result.decision = HeadDecision::accept_genesis;
        return result;
    }

    if (candidate == *current || result.candidate_record == result.current_record) {
        result.decision = HeadDecision::duplicate;
        return result;
    }
    if (candidate.generation < current->generation) {
        result.decision = HeadDecision::stale;
        return result;
    }
    if (candidate.generation == current->generation) {
        result.decision = HeadDecision::fork;
        return result;
    }

    result.generation_delta = candidate.generation - current->generation;
    if (result.generation_delta > policy.maximum_generation_jump) {
        result.decision = HeadDecision::generation_gap;
        return result;
    }
    if (policy.forbid_engine_downgrade &&
        static_cast<std::uint16_t>(candidate.engine) <
            static_cast<std::uint16_t>(current->engine)) {
        result.decision = HeadDecision::engine_downgrade;
        return result;
    }

    const bool linked = candidate.parent == result.current_record;
    if (linked || !policy.require_parent_link) {
        result.decision = HeadDecision::accept_advance;
        return result;
    }

    const bool snapshot = (candidate.flags & kHeadFlagSnapshot) != 0U;
    if (snapshot && policy.allow_snapshot_rebase) {
        result.decision = HeadDecision::accept_snapshot;
        return result;
    }

    result.decision = HeadDecision::parent_mismatch;
    return result;
}

const char* head_decision_name(HeadDecision decision) noexcept {
    switch (decision) {
        case HeadDecision::accept_genesis: return "accept-genesis";
        case HeadDecision::accept_advance: return "accept-advance";
        case HeadDecision::accept_snapshot: return "accept-snapshot";
        case HeadDecision::duplicate: return "duplicate";
        case HeadDecision::stale: return "stale";
        case HeadDecision::fork: return "fork";
        case HeadDecision::wrong_namespace: return "wrong-namespace";
        case HeadDecision::invalid_signature: return "invalid-signature";
        case HeadDecision::generation_gap: return "generation-gap";
        case HeadDecision::parent_mismatch: return "parent-mismatch";
        case HeadDecision::engine_downgrade: return "engine-downgrade";
        case HeadDecision::resource_limit: return "resource-limit";
    }
    return "unknown";
}

void store_mutable_head_state(const std::filesystem::path& path,
                              const MutableHead& head,
                              const MutableHeadStateOptions& options) {
    if (options.create_parent_directories) ensure_parent(path);
    const auto encoded_head = encode_mutable_head(head);
    const auto record_digest = sha256(encoded_head);

    std::array<std::byte, kStateBytes> bytes{};
    std::copy(kStateMagic.begin(), kStateMagic.end(), bytes.begin());
    write_u16_le(bytes, 8U, kStateVersion);
    write_u16_le(bytes, 10U, static_cast<std::uint16_t>(kStateHeaderBytes));
    std::size_t offset = kStateHeaderBytes;
    std::copy(encoded_head.begin(), encoded_head.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += encoded_head.size();
    std::copy(record_digest.bytes.begin(), record_digest.bytes.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += record_digest.bytes.size();
    const auto checksum = sha256(std::span<const std::byte>(bytes.data(), offset));
    std::copy(checksum.bytes.begin(), checksum.bytes.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));

    const auto temporary = temporary_path_for(path);
    std::error_code ignored;
    std::filesystem::remove(temporary, ignored);
    try {
        detail::NativeFile output(
            temporary, detail::NativeOpenMode::read_write_create_exclusive, 0600U);
        output.write_exact_at(0U, bytes);
        if (options.fsync_on_commit) output.sync();
        output.close();
        atomic_replace(temporary, path);
        if (options.fsync_on_commit) sync_parent(path);
    } catch (...) {
        std::filesystem::remove(temporary, ignored);
        throw;
    }
}

std::optional<MutableHead> load_mutable_head_state(
    const std::filesystem::path& path) {
    std::error_code error;
    if (!std::filesystem::exists(path, error)) return std::nullopt;
    if (error) {
        throw std::runtime_error("cannot inspect mutable-head state: " + error.message());
    }
    detail::NativeFile input(path, detail::NativeOpenMode::read_only);
    if (input.size() != kStateBytes) {
        throw std::runtime_error("mutable-head state has an invalid length");
    }
    std::array<std::byte, kStateBytes> bytes{};
    input.read_exact_at(0U, bytes);
    if (!std::equal(kStateMagic.begin(), kStateMagic.end(), bytes.begin()) ||
        read_u16_le(bytes, 8U) != kStateVersion ||
        read_u16_le(bytes, 10U) != kStateHeaderBytes) {
        throw std::runtime_error("mutable-head state has an unsupported header");
    }
    constexpr std::size_t head_offset = kStateHeaderBytes;
    constexpr std::size_t digest_offset = head_offset + kMutableHeadBytes;
    constexpr std::size_t checksum_offset = digest_offset + 32U;
    const auto expected_checksum = sha256(
        std::span<const std::byte>(bytes.data(), checksum_offset));
    if (!std::equal(expected_checksum.bytes.begin(), expected_checksum.bytes.end(),
                    bytes.begin() + static_cast<std::ptrdiff_t>(checksum_offset))) {
        throw std::runtime_error("mutable-head state checksum mismatch");
    }
    const auto head = decode_mutable_head(
        std::span<const std::byte>(bytes.data() + head_offset, kMutableHeadBytes));
    const auto record_digest = mutable_head_record_digest(head);
    if (!std::equal(record_digest.bytes.begin(), record_digest.bytes.end(),
                    bytes.begin() + static_cast<std::ptrdiff_t>(digest_offset))) {
        throw std::runtime_error("mutable-head state record digest mismatch");
    }
    return head;
}

} // namespace toxsync
