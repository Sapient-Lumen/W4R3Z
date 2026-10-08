#include "sha256_digest.hpp"

#include <array>
#include <stdexcept>
#include <utility>

#include <openssl/evp.h>
#include <openssl/sha.h>

namespace anonsync {
namespace {

[[nodiscard]] std::string lowercase_hex(
    const unsigned char* bytes,
    std::size_t byte_count) {
    static constexpr char kHex[] = "0123456789abcdef";
    std::string out(byte_count * 2U, '\0');
    for (std::size_t index = 0; index < byte_count; ++index) {
        const unsigned char byte = bytes[index];
        out[index * 2U] = kHex[(byte >> 4U) & 0x0fU];
        out[index * 2U + 1U] = kHex[byte & 0x0fU];
    }
    return out;
}

}  // namespace

struct Sha256DigestBuilder::State final {
    State() {
        context = EVP_MD_CTX_new();
        if (context == nullptr) {
            throw std::runtime_error("SHA-256 digest context allocation failed");
        }
        if (EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
            EVP_MD_CTX_free(context);
            context = nullptr;
            throw std::runtime_error("SHA-256 digest initialization failed");
        }
    }

    ~State() { EVP_MD_CTX_free(context); }

    EVP_MD_CTX* context = nullptr;
    bool finished = false;
};

Sha256DigestBuilder::Sha256DigestBuilder() : state_(std::make_unique<State>()) {}

Sha256DigestBuilder::~Sha256DigestBuilder() = default;

Sha256DigestBuilder::Sha256DigestBuilder(Sha256DigestBuilder&& other) noexcept =
    default;

Sha256DigestBuilder& Sha256DigestBuilder::operator=(
    Sha256DigestBuilder&& other) noexcept = default;

void Sha256DigestBuilder::update(std::string_view bytes) {
    if (!state_ || state_->finished || state_->context == nullptr) {
        throw std::logic_error("SHA-256 digest builder is not updateable");
    }
    if (bytes.empty()) return;
    if (EVP_DigestUpdate(state_->context, bytes.data(), bytes.size()) != 1) {
        throw std::runtime_error("SHA-256 digest update failed");
    }
}

std::string Sha256DigestBuilder::finish_hex() {
    if (!state_ || state_->finished || state_->context == nullptr) {
        throw std::logic_error("SHA-256 digest builder is not finishable");
    }
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int digest_size = 0;
    // Finalization consumes the cryptographic state even when the provider
    // reports an error. Poison the builder before crossing that boundary so a
    // caller can never retry against an indeterminate EVP context.
    state_->finished = true;
    if (EVP_DigestFinal_ex(state_->context, digest.data(), &digest_size) != 1 ||
        digest_size != SHA256_DIGEST_LENGTH) {
        throw std::runtime_error("SHA-256 digest finalization failed");
    }
    return lowercase_hex(digest.data(), digest_size);
}

std::string sha256_hex(const std::string& data) {
    Sha256DigestBuilder builder;
    builder.update(data);
    return builder.finish_hex();
}

bool is_lowercase_sha256_hex(std::string_view value) noexcept {
    if (value.size() != SHA256_DIGEST_LENGTH * 2U) return false;
    for (const char c : value) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
            return false;
        }
    }
    return true;
}

}  // namespace anonsync
