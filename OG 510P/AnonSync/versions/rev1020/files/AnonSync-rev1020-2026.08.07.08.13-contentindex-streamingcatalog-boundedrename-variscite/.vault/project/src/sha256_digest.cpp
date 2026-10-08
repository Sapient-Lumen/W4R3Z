#include "sha256_digest.hpp"

#include <algorithm>
#include <array>
#include <stdexcept>
#include <utility>

#include <openssl/evp.h>
#include <openssl/sha.h>

namespace anonsync {
namespace {

constexpr char kLowercaseHex[] = "0123456789abcdef";

[[nodiscard]] std::uint8_t lowercase_hex_nibble(char character) noexcept {
    if (character >= '0' && character <= '9') {
        return static_cast<std::uint8_t>(character - '0');
    }
    return static_cast<std::uint8_t>(character - 'a' + 10);
}

[[nodiscard]] std::array<std::uint8_t, kSha256DigestBytes>
decode_lowercase_sha256_or_throw(std::string_view value) {
    if (!is_lowercase_sha256_hex(value)) {
        throw std::invalid_argument(
            "fixed SHA-256 digest is not canonical lowercase hexadecimal");
    }
    std::array<std::uint8_t, kSha256DigestBytes> bytes{};
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        bytes[index] = static_cast<std::uint8_t>(
            (lowercase_hex_nibble(value[index * 2U]) << 4U) |
            lowercase_hex_nibble(value[index * 2U + 1U]));
    }
    return bytes;
}

[[nodiscard]] std::string lowercase_hex(
    const unsigned char* bytes,
    std::size_t byte_count) {
    std::string out(byte_count * 2U, '\0');
    for (std::size_t index = 0; index < byte_count; ++index) {
        const unsigned char byte = bytes[index];
        out[index * 2U] = kLowercaseHex[(byte >> 4U) & 0x0fU];
        out[index * 2U + 1U] = kLowercaseHex[byte & 0x0fU];
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

Sha256DigestValue::Sha256DigestValue(std::string_view lowercase_hex)
    : bytes_(decode_lowercase_sha256_or_throw(lowercase_hex)) {}

Sha256DigestValue& Sha256DigestValue::operator=(
    std::string_view lowercase_hex) {
    const auto decoded = decode_lowercase_sha256_or_throw(lowercase_hex);
    bytes_ = decoded;
    return *this;
}

std::array<char, kSha256HexCharacters>
Sha256DigestValue::lowercase_hex_array() const noexcept {
    std::array<char, kSha256HexCharacters> output{};
    for (std::size_t index = 0U; index < bytes_.size(); ++index) {
        const std::uint8_t byte = bytes_[index];
        output[index * 2U] = kLowercaseHex[(byte >> 4U) & 0x0fU];
        output[index * 2U + 1U] = kLowercaseHex[byte & 0x0fU];
    }
    return output;
}

std::string Sha256DigestValue::lowercase_hex() const {
    const auto text = lowercase_hex_array();
    return std::string(text.data(), text.size());
}

void Sha256DigestValue::append_lowercase_hex_to(
    std::string& destination) const {
    const std::size_t begin = destination.size();
    destination.resize(begin + kSha256HexCharacters);
    const auto text = lowercase_hex_array();
    std::copy(text.begin(), text.end(), destination.begin() +
        static_cast<std::ptrdiff_t>(begin));
}

void Sha256DigestValue::append_binary_to(std::string& destination) const {
    destination.append(
        reinterpret_cast<const char*>(bytes_.data()), bytes_.size());
}

void Sha256DigestValue::update_lowercase_hex(
    Sha256DigestBuilder& destination) const {
    const auto text = lowercase_hex_array();
    destination.update(std::string_view(text.data(), text.size()));
}

bool Sha256DigestValue::equals_lowercase_hex(
    std::string_view value) const noexcept {
    if (value.size() != kSha256HexCharacters) return false;
    for (std::size_t index = 0U; index < bytes_.size(); ++index) {
        const std::uint8_t byte = bytes_[index];
        if (value[index * 2U] !=
                kLowercaseHex[(byte >> 4U) & 0x0fU] ||
            value[index * 2U + 1U] != kLowercaseHex[byte & 0x0fU]) {
            return false;
        }
    }
    return true;
}

int Sha256DigestValue::compare_lowercase_hex(
    std::string_view value) const noexcept {
    const std::size_t common =
        std::min<std::size_t>(kSha256HexCharacters, value.size());
    for (std::size_t index = 0U; index < common; ++index) {
        const std::uint8_t byte = bytes_[index / 2U];
        const char character = (index % 2U == 0U)
            ? kLowercaseHex[(byte >> 4U) & 0x0fU]
            : kLowercaseHex[byte & 0x0fU];
        if (character < value[index]) return -1;
        if (character > value[index]) return 1;
    }
    if (kSha256HexCharacters < value.size()) return -1;
    if (kSha256HexCharacters > value.size()) return 1;
    return 0;
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
