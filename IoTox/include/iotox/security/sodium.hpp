#pragma once

#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::security {

inline constexpr std::size_t kSigningSeedBytes = 32U;
inline constexpr std::size_t kSigningPublicKeyBytes = 32U;
inline constexpr std::size_t kSigningSecretKeyBytes = 64U;
inline constexpr std::size_t kSignatureBytes = 64U;
inline constexpr std::size_t kDigestBytes = 32U;

using SigningSeed = std::array<std::uint8_t, kSigningSeedBytes>;
using SigningPublicKey = std::array<std::uint8_t, kSigningPublicKeyBytes>;
using SigningSecretKey = std::array<std::uint8_t, kSigningSecretKeyBytes>;
using Signature = std::array<std::uint8_t, kSignatureBytes>;
using Digest = std::array<std::uint8_t, kDigestBytes>;

void secure_wipe(std::span<std::uint8_t> bytes) noexcept;
[[nodiscard]] bool constant_time_equal(
    std::span<const std::uint8_t> left,
    std::span<const std::uint8_t> right) noexcept;
[[nodiscard]] std::string hex(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>> decode_hex_exact(
    std::string_view encoded, std::size_t expected_bytes, std::string_view label);

class SigningKeyPair {
  public:
    SigningKeyPair() = default;
    ~SigningKeyPair();

    SigningKeyPair(const SigningKeyPair &) = delete;
    SigningKeyPair &operator=(const SigningKeyPair &) = delete;
    SigningKeyPair(SigningKeyPair &&other) noexcept;
    SigningKeyPair &operator=(SigningKeyPair &&other) noexcept;

    [[nodiscard]] const SigningPublicKey &public_key() const noexcept { return public_key_; }
    [[nodiscard]] std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key() const noexcept {
        return secret_key_;
    }

  private:
    friend class Sodium;
    SigningPublicKey public_key_{};
    SigningSecretKey secret_key_{};
};

class Sodium {
  public:
    Sodium() = default;
    ~Sodium();

    Sodium(const Sodium &) = delete;
    Sodium &operator=(const Sodium &) = delete;
    Sodium(Sodium &&other) noexcept;
    Sodium &operator=(Sodium &&other) noexcept;

    [[nodiscard]] static Result<Sodium> load(
        const std::filesystem::path &explicit_path = {});

    [[nodiscard]] Result<SigningKeyPair> signing_keypair_from_seed(
        std::span<const std::uint8_t, kSigningSeedBytes> seed) const;
    [[nodiscard]] Result<Signature> sign_detached(
        std::span<const std::uint8_t> message,
        std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key) const;
    [[nodiscard]] Status verify_detached(
        std::span<const std::uint8_t, kSignatureBytes> signature,
        std::span<const std::uint8_t> message,
        std::span<const std::uint8_t, kSigningPublicKeyBytes> public_key) const;

    // IoTox's fixed hash contract is BLAKE2b-256 over:
    //   "IOTOXH1" || uint16_be(domain_bytes) || domain || payload
    // Domain strings are part of the protocol and persistence contract.
    [[nodiscard]] Result<Digest> hash(
        std::string_view domain,
        std::span<const std::uint8_t> payload) const;

    // Raw SHA-256 exists only for interoperable release receipts and external
    // tooling checksums. New IoTox protocol/state digests should use hash().
    [[nodiscard]] Result<Digest> sha256(
        std::span<const std::uint8_t> payload) const;

    // IoTox's fixed secret derivation contract is keyed BLAKE2b-256 over:
    //   "IOTOXK1" || uint16_be(domain_bytes) || domain || context
    // with the caller-provided 32-byte root as the BLAKE2b key.
    [[nodiscard]] Result<Digest> derive_key(
        std::string_view domain,
        std::span<const std::uint8_t, kDigestBytes> root,
        std::span<const std::uint8_t> context = {}) const;

    [[nodiscard]] const std::string &loaded_path() const noexcept { return loaded_path_; }
    [[nodiscard]] const std::string &version() const noexcept { return version_; }

  private:
    using InitFn = int (*)();
    using VersionStringFn = const char *(*)();
    using SizeFn = std::size_t (*)();
    using SeedKeypairFn = int (*)(unsigned char *, unsigned char *, const unsigned char *);
    using SignDetachedFn = int (*)(unsigned char *, unsigned long long *, const unsigned char *,
                                   unsigned long long, const unsigned char *);
    using VerifyDetachedFn = int (*)(const unsigned char *, const unsigned char *,
                                     unsigned long long, const unsigned char *);
    using GenericHashFn = int (*)(unsigned char *, std::size_t, const unsigned char *,
                                  unsigned long long, const unsigned char *, std::size_t);
    using Sha256Fn = int (*)(unsigned char *, const unsigned char *,
                             unsigned long long);
    using MemzeroFn = void (*)(void *, std::size_t);

    struct Api {
        InitFn init{nullptr};
        VersionStringFn version_string{nullptr};
        SizeFn seed_bytes{nullptr};
        SizeFn public_key_bytes{nullptr};
        SizeFn secret_key_bytes{nullptr};
        SizeFn signature_bytes{nullptr};
        SeedKeypairFn seed_keypair{nullptr};
        SignDetachedFn sign_detached{nullptr};
        VerifyDetachedFn verify_detached{nullptr};
        GenericHashFn generichash{nullptr};
        SizeFn sha256_bytes{nullptr};
        Sha256Fn sha256{nullptr};
        MemzeroFn memzero{nullptr};
    };

    [[nodiscard]] Result<Digest> generichash(
        std::span<const std::uint8_t> input,
        std::span<const std::uint8_t> key) const;

    void *handle_{nullptr};
    bool owns_handle_{false};
    Api api_{};
    std::string loaded_path_;
    std::string version_;
};

}  // namespace iotox::security
