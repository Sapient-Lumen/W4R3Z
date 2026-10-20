#pragma once

#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>

namespace iotox::security {

inline constexpr std::size_t kDeviceIdentityFileBytes = 80U;

enum class SigningIdentityRole : std::uint8_t {
    device = 0U,
    release = 1U,
    witness = 2U,
};

class DeviceIdentity {
  public:
    DeviceIdentity() = default;
    ~DeviceIdentity() = default;

    DeviceIdentity(const DeviceIdentity &) = delete;
    DeviceIdentity &operator=(const DeviceIdentity &) = delete;
    DeviceIdentity(DeviceIdentity &&) noexcept = default;
    DeviceIdentity &operator=(DeviceIdentity &&) noexcept = default;

    [[nodiscard]] static Result<DeviceIdentity> load(
        const std::filesystem::path &path, const Sodium &sodium);
    [[nodiscard]] static Result<DeviceIdentity> load_release(
        const std::filesystem::path &path, const Sodium &sodium);
    [[nodiscard]] static Result<DeviceIdentity> load_witness(
        const std::filesystem::path &path, const Sodium &sodium);
    [[nodiscard]] static Result<DeviceIdentity> load_or_create(
        const std::filesystem::path &path, const Sodium &sodium, bool allow_create);
    // Offline release-key ceremonies need an explicit no-clobber primitive.
    // Unlike load_or_create(), this never adopts an existing identity and
    // atomically refuses a destination that appeared during creation.
    [[nodiscard]] static Result<DeviceIdentity> create_new_release(
        const std::filesystem::path &path, const Sodium &sodium);
    [[nodiscard]] static Result<DeviceIdentity> create_new_witness(
        const std::filesystem::path &path, const Sodium &sodium);

    [[nodiscard]] const SigningPublicKey &public_key() const noexcept {
        return keys_.public_key();
    }
    [[nodiscard]] std::string public_key_hex() const { return hex(public_key()); }
    [[nodiscard]] const std::filesystem::path &path() const noexcept { return path_; }
    [[nodiscard]] SigningIdentityRole role() const noexcept { return role_; }
    [[nodiscard]] Result<Signature> sign(std::span<const std::uint8_t> message) const;

  private:
    DeviceIdentity(
        std::filesystem::path path, SigningKeyPair keys,
        SigningIdentityRole role, const Sodium &sodium)
        : path_(std::move(path)), keys_(std::move(keys)), role_(role),
          sodium_(&sodium) {}

    std::filesystem::path path_;
    SigningKeyPair keys_;
    SigningIdentityRole role_{SigningIdentityRole::device};
    const Sodium *sodium_{nullptr};
};

[[nodiscard]] std::filesystem::path default_device_identity_path(
    const std::filesystem::path &tox_savedata_path);

}  // namespace iotox::security
