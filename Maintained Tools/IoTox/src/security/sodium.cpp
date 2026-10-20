#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#if defined(IOTOX_LINKED_SODIUM)
extern "C" {
int sodium_init(void);
const char *sodium_version_string(void);
std::size_t crypto_sign_seedbytes(void);
std::size_t crypto_sign_publickeybytes(void);
std::size_t crypto_sign_secretkeybytes(void);
std::size_t crypto_sign_bytes(void);
int crypto_sign_seed_keypair(unsigned char *, unsigned char *, const unsigned char *);
int crypto_sign_detached(unsigned char *, unsigned long long *, const unsigned char *,
                         unsigned long long, const unsigned char *);
int crypto_sign_verify_detached(const unsigned char *, const unsigned char *,
                                unsigned long long, const unsigned char *);
int crypto_generichash(unsigned char *, std::size_t, const unsigned char *,
                       unsigned long long, const unsigned char *, std::size_t);
std::size_t crypto_hash_sha256_bytes(void);
int crypto_hash_sha256(unsigned char *, const unsigned char *, unsigned long long);
void sodium_memzero(void *, std::size_t);
}
#endif

namespace iotox::security {
namespace {

constexpr std::array<std::uint8_t, 7U> kHashPrefix = {'I', 'O', 'T', 'O', 'X', 'H', '1'};
constexpr std::array<std::uint8_t, 7U> kKeyPrefix = {'I', 'O', 'T', 'O', 'X', 'K', '1'};
constexpr std::size_t kMaximumDomainBytes = 255U;
constexpr std::size_t kMaximumHashInputBytes = 64U * 1024U;

void volatile_wipe(void *memory, std::size_t size) noexcept {
    auto *bytes = static_cast<volatile std::uint8_t *>(memory);
    while (size > 0U) {
        *bytes = 0U;
        ++bytes;
        --size;
    }
}

int hex_nibble(char value) noexcept {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    if (value >= 'a' && value <= 'f') {
        return 10 + value - 'a';
    }
    if (value >= 'A' && value <= 'F') {
        return 10 + value - 'A';
    }
    return -1;
}

template <typename FunctionPointer>
Result<FunctionPointer> load_symbol(void *handle, const char *name) {
    ::dlerror();
    void *raw = ::dlsym(handle, name);
    const char *error = ::dlerror();
    if (error != nullptr || raw == nullptr) {
        return Status{ErrorCode::library_error,
                      "libsodium symbol '" + std::string(name) + "' is unavailable: " +
                          (error == nullptr ? std::string("unknown dlsym failure") :
                                              std::string(error))};
    }
    static_assert(sizeof(FunctionPointer) == sizeof(raw));
    FunctionPointer function{};
    std::memcpy(&function, &raw, sizeof(function));
    return function;
}

template <typename FunctionPointer>
Status assign_symbol(void *handle, const char *name, FunctionPointer &destination) {
    auto symbol = load_symbol<FunctionPointer>(handle, name);
    if (!symbol) {
        return symbol.status();
    }
    destination = symbol.value();
    return Status::success();
}

std::vector<std::string> library_candidates(const std::filesystem::path &explicit_path) {
    if (!explicit_path.empty()) {
        return {explicit_path.string()};
    }
    if (const char *environment = std::getenv("IOTOX_SODIUM_LIBRARY");
        environment != nullptr && environment[0] != '\0') {
        return {environment};
    }
    return {"libsodium.so.23", "libsodium.so", "libsodium.dylib"};
}

Status validate_domain(std::string_view domain) {
    if (domain.empty() || domain.size() > kMaximumDomainBytes) {
        return Status{ErrorCode::invalid_argument,
                      "IoTox cryptographic domain must contain 1..255 bytes"};
    }
    for (const char value : domain) {
        const auto byte = static_cast<unsigned char>(value);
        if (byte < 0x21U || byte > 0x7EU) {
            return Status{ErrorCode::invalid_argument,
                          "IoTox cryptographic domain must be printable non-space ASCII"};
        }
    }
    return Status::success();
}

std::vector<std::uint8_t> domain_input(
    std::span<const std::uint8_t, 7U> prefix,
    std::string_view domain,
    std::span<const std::uint8_t> payload) {
    std::vector<std::uint8_t> input;
    input.reserve(prefix.size() + 2U + domain.size() + payload.size());
    input.insert(input.end(), prefix.begin(), prefix.end());
    input.push_back(static_cast<std::uint8_t>((domain.size() >> 8U) & 0xFFU));
    input.push_back(static_cast<std::uint8_t>(domain.size() & 0xFFU));
    input.insert(input.end(), domain.begin(), domain.end());
    input.insert(input.end(), payload.begin(), payload.end());
    return input;
}

}  // namespace

void secure_wipe(std::span<std::uint8_t> bytes) noexcept {
    volatile_wipe(bytes.data(), bytes.size());
}

bool constant_time_equal(
    std::span<const std::uint8_t> left,
    std::span<const std::uint8_t> right) noexcept {
    if (left.size() != right.size()) {
        return false;
    }
    std::uint8_t difference = 0U;
    for (std::size_t index = 0U; index < left.size(); ++index) {
        difference = static_cast<std::uint8_t>(difference | (left[index] ^ right[index]));
    }
    return difference == 0U;
}

std::string hex(std::span<const std::uint8_t> bytes) {
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : bytes) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

Result<std::vector<std::uint8_t>> decode_hex_exact(
    std::string_view encoded, std::size_t expected_bytes, std::string_view label) {
    if (encoded.size() != expected_bytes * 2U) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " must contain exactly " +
                          std::to_string(expected_bytes * 2U) + " hexadecimal characters"};
    }
    std::vector<std::uint8_t> output;
    output.reserve(expected_bytes);
    for (std::size_t index = 0U; index < encoded.size(); index += 2U) {
        const int high = hex_nibble(encoded[index]);
        const int low = hex_nibble(encoded[index + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::invalid_argument,
                          std::string(label) + " contains a non-hexadecimal character"};
        }
        output.push_back(static_cast<std::uint8_t>((high << 4) | low));
    }
    return output;
}

SigningKeyPair::~SigningKeyPair() {
    secure_wipe(secret_key_);
}

SigningKeyPair::SigningKeyPair(SigningKeyPair &&other) noexcept
    : public_key_(other.public_key_), secret_key_(other.secret_key_) {
    secure_wipe(other.secret_key_);
    other.public_key_.fill(0U);
}

SigningKeyPair &SigningKeyPair::operator=(SigningKeyPair &&other) noexcept {
    if (this != &other) {
        secure_wipe(secret_key_);
        public_key_ = other.public_key_;
        secret_key_ = other.secret_key_;
        secure_wipe(other.secret_key_);
        other.public_key_.fill(0U);
    }
    return *this;
}

Sodium::~Sodium() {
    if (owns_handle_ && handle_ != nullptr) {
        ::dlclose(handle_);
    }
}

Sodium::Sodium(Sodium &&other) noexcept
    : handle_(std::exchange(other.handle_, nullptr)),
      owns_handle_(std::exchange(other.owns_handle_, false)),
      api_(other.api_),
      loaded_path_(std::move(other.loaded_path_)),
      version_(std::move(other.version_)) {
    other.api_ = {};
}

Sodium &Sodium::operator=(Sodium &&other) noexcept {
    if (this != &other) {
        if (owns_handle_ && handle_ != nullptr) {
            ::dlclose(handle_);
        }
        handle_ = std::exchange(other.handle_, nullptr);
        owns_handle_ = std::exchange(other.owns_handle_, false);
        api_ = other.api_;
        loaded_path_ = std::move(other.loaded_path_);
        version_ = std::move(other.version_);
        other.api_ = {};
    }
    return *this;
}

Result<Sodium> Sodium::load(const std::filesystem::path &explicit_path) {
    Sodium sodium;

#if defined(IOTOX_LINKED_SODIUM)
    if (explicit_path.empty()) {
        sodium.api_.init = &::sodium_init;
        sodium.api_.version_string = &::sodium_version_string;
        sodium.api_.seed_bytes = &::crypto_sign_seedbytes;
        sodium.api_.public_key_bytes = &::crypto_sign_publickeybytes;
        sodium.api_.secret_key_bytes = &::crypto_sign_secretkeybytes;
        sodium.api_.signature_bytes = &::crypto_sign_bytes;
        sodium.api_.seed_keypair = &::crypto_sign_seed_keypair;
        sodium.api_.sign_detached = &::crypto_sign_detached;
        sodium.api_.verify_detached = &::crypto_sign_verify_detached;
        sodium.api_.generichash = &::crypto_generichash;
        sodium.api_.sha256_bytes = &::crypto_hash_sha256_bytes;
        sodium.api_.sha256 = &::crypto_hash_sha256;
        sodium.api_.memzero = &::sodium_memzero;
        sodium.loaded_path_ = "linked-static-libsodium";
    }
#endif

    if (sodium.api_.init == nullptr) {
        std::string errors;
        for (const std::string &candidate : library_candidates(explicit_path)) {
            void *handle = ::dlopen(candidate.c_str(), RTLD_NOW | RTLD_LOCAL);
            if (handle == nullptr) {
                const char *error = ::dlerror();
                if (!errors.empty()) {
                    errors += "; ";
                }
                errors += candidate + ": " +
                          (error == nullptr ? std::string("unknown dlopen failure") :
                                              std::string(error));
                continue;
            }

            Api api{};
            Status status = assign_symbol(handle, "sodium_init", api.init);
            if (status.ok()) {
                status = assign_symbol(handle, "sodium_version_string", api.version_string);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_seedbytes", api.seed_bytes);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_publickeybytes", api.public_key_bytes);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_secretkeybytes", api.secret_key_bytes);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_bytes", api.signature_bytes);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_seed_keypair", api.seed_keypair);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_detached", api.sign_detached);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_sign_verify_detached", api.verify_detached);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_generichash", api.generichash);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_hash_sha256_bytes", api.sha256_bytes);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "crypto_hash_sha256", api.sha256);
            }
            if (status.ok()) {
                status = assign_symbol(handle, "sodium_memzero", api.memzero);
            }
            if (!status.ok()) {
                ::dlclose(handle);
                return status;
            }

            sodium.handle_ = handle;
            sodium.owns_handle_ = true;
            sodium.api_ = api;
            sodium.loaded_path_ = candidate;
            break;
        }
        if (sodium.api_.init == nullptr) {
            return Status{ErrorCode::library_error,
                          "unable to load libsodium: " + errors};
        }
    }

    if (sodium.api_.init() < 0) {
        return Status{ErrorCode::library_error, "libsodium initialization failed"};
    }
    if (sodium.api_.seed_bytes() != kSigningSeedBytes ||
        sodium.api_.public_key_bytes() != kSigningPublicKeyBytes ||
        sodium.api_.secret_key_bytes() != kSigningSecretKeyBytes ||
        sodium.api_.signature_bytes() != kSignatureBytes ||
        sodium.api_.sha256_bytes() != kDigestBytes) {
        return Status{ErrorCode::library_error,
                      "loaded libsodium does not match IoTox's cryptographic size contract"};
    }
    const char *version = sodium.api_.version_string();
    sodium.version_ = version == nullptr ? "unknown" : std::string(version);
    return sodium;
}

Result<SigningKeyPair> Sodium::signing_keypair_from_seed(
    std::span<const std::uint8_t, kSigningSeedBytes> seed) const {
    if (api_.seed_keypair == nullptr) {
        return Status{ErrorCode::library_error, "libsodium is not initialized"};
    }
    SigningKeyPair keys;
    if (api_.seed_keypair(
            keys.public_key_.data(), keys.secret_key_.data(), seed.data()) != 0) {
        return Status{ErrorCode::library_error,
                      "libsodium failed to derive an Ed25519 keypair from a seed"};
    }
    return keys;
}

Result<Signature> Sodium::sign_detached(
    std::span<const std::uint8_t> message,
    std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key) const {
    if (api_.sign_detached == nullptr) {
        return Status{ErrorCode::library_error, "libsodium is not initialized"};
    }
    if (message.size() > static_cast<std::size_t>(std::numeric_limits<unsigned long long>::max())) {
        return Status{ErrorCode::invalid_argument, "message is too large for Ed25519"};
    }
    Signature signature{};
    unsigned long long signature_bytes = 0U;
    if (api_.sign_detached(
            signature.data(), &signature_bytes, message.data(),
            static_cast<unsigned long long>(message.size()), secret_key.data()) != 0 ||
        signature_bytes != signature.size()) {
        return Status{ErrorCode::library_error,
                      "libsodium failed to create a complete Ed25519 signature"};
    }
    return signature;
}

Status Sodium::verify_detached(
    std::span<const std::uint8_t, kSignatureBytes> signature,
    std::span<const std::uint8_t> message,
    std::span<const std::uint8_t, kSigningPublicKeyBytes> public_key) const {
    if (api_.verify_detached == nullptr) {
        return Status{ErrorCode::library_error, "libsodium is not initialized"};
    }
    if (message.size() > static_cast<std::size_t>(std::numeric_limits<unsigned long long>::max())) {
        return Status{ErrorCode::invalid_argument, "message is too large for Ed25519"};
    }
    if (api_.verify_detached(
            signature.data(), message.data(),
            static_cast<unsigned long long>(message.size()), public_key.data()) != 0) {
        return Status{ErrorCode::protocol_error, "Ed25519 signature verification failed"};
    }
    return Status::success();
}

Result<Digest> Sodium::generichash(
    std::span<const std::uint8_t> input,
    std::span<const std::uint8_t> key) const {
    if (api_.generichash == nullptr) {
        return Status{ErrorCode::library_error, "libsodium is not initialized"};
    }
    if (input.size() > kMaximumHashInputBytes) {
        return Status{ErrorCode::invalid_argument,
                      "IoTox cryptographic input exceeds 65536 bytes"};
    }
    if (input.size() > static_cast<std::size_t>(std::numeric_limits<unsigned long long>::max())) {
        return Status{ErrorCode::invalid_argument, "hash input is too large"};
    }
    Digest digest{};
    const unsigned char *key_data = key.empty() ? nullptr : key.data();
    if (api_.generichash(
            digest.data(), digest.size(), input.data(),
            static_cast<unsigned long long>(input.size()), key_data, key.size()) != 0) {
        return Status{ErrorCode::library_error, "libsodium BLAKE2b operation failed"};
    }
    return digest;
}

Result<Digest> Sodium::hash(
    std::string_view domain,
    std::span<const std::uint8_t> payload) const {
    const Status domain_status = validate_domain(domain);
    if (!domain_status.ok()) {
        return domain_status;
    }
    if (payload.size() > kMaximumHashInputBytes - kHashPrefix.size() - 2U - domain.size()) {
        return Status{ErrorCode::invalid_argument,
                      "IoTox domain-separated hash payload is too large"};
    }
    const std::vector<std::uint8_t> input = domain_input(kHashPrefix, domain, payload);
    return generichash(input, {});
}

Result<Digest> Sodium::sha256(std::span<const std::uint8_t> payload) const {
    if (api_.sha256 == nullptr) {
        return Status{ErrorCode::library_error, "libsodium is not initialized"};
    }
    if (payload.size() >
        static_cast<std::size_t>(std::numeric_limits<unsigned long long>::max())) {
        return Status{ErrorCode::invalid_argument, "SHA-256 input is too large"};
    }
    static constexpr std::array<std::uint8_t, 1U> kEmptyInput{};
    const unsigned char *data =
        payload.empty() ? kEmptyInput.data() : payload.data();
    Digest digest{};
    if (api_.sha256(
            digest.data(), data,
            static_cast<unsigned long long>(payload.size())) != 0) {
        return Status{ErrorCode::library_error, "libsodium SHA-256 operation failed"};
    }
    return digest;
}

Result<Digest> Sodium::derive_key(
    std::string_view domain,
    std::span<const std::uint8_t, kDigestBytes> root,
    std::span<const std::uint8_t> context) const {
    const Status domain_status = validate_domain(domain);
    if (!domain_status.ok()) {
        return domain_status;
    }
    if (context.size() > kMaximumHashInputBytes - kKeyPrefix.size() - 2U - domain.size()) {
        return Status{ErrorCode::invalid_argument,
                      "IoTox domain-separated derivation context is too large"};
    }
    std::vector<std::uint8_t> input = domain_input(kKeyPrefix, domain, context);
    auto derived = generichash(input, root);
    if (api_.memzero != nullptr && !input.empty()) {
        api_.memzero(input.data(), input.size());
    } else {
        secure_wipe(input);
    }
    return derived;
}

}  // namespace iotox::security
