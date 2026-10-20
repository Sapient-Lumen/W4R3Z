#include "iotox/security/identity.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <linux/fs.h>
#include <string>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::security {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {
    'I', 'O', 'T', 'O', 'X', 'I', 'D', '1'};
constexpr std::uint8_t kFormatVersion = 1U;
constexpr std::uint8_t kAlgorithmEd25519 = 1U;

Status file_status(std::string operation, const std::filesystem::path &path,
                   int error = errno) {
    return Status{ErrorCode::io_error,
                  std::move(operation) + " '" + path.string() + "': " +
                      std::strerror(error)};
}

Result<std::array<std::uint8_t, kDeviceIdentityFileBytes>> read_exact_private_file(
    const std::filesystem::path &path) {
    int descriptor = -1;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          "device identity file does not exist: " + path.string()};
        }
        return file_status("unable to open device identity", path);
    }

    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        const Status status = file_status("unable to inspect device identity", path);
        (void)::close(descriptor);
        return status;
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "device identity must be a regular file owned by the running user: " +
                          path.string()};
    }
    if ((metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "device identity permissions expose secret material; require mode 0600: " +
                          path.string()};
    }
    if (metadata.st_size != static_cast<off_t>(kDeviceIdentityFileBytes)) {
        (void)::close(descriptor);
        return Status{ErrorCode::protocol_error,
                      "device identity has an unexpected size: " + path.string()};
    }

    std::array<std::uint8_t, kDeviceIdentityFileBytes> bytes{};
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor, bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            const Status status = file_status("unable to read device identity", path);
            (void)::close(descriptor);
            secure_wipe(bytes);
            return status;
        }
        if (count == 0) {
            (void)::close(descriptor);
            secure_wipe(bytes);
            return Status{ErrorCode::io_error,
                          "device identity ended before its fixed record was complete: " +
                              path.string()};
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        secure_wipe(bytes);
        return file_status("unable to close device identity", path);
    }
    return bytes;
}

Result<SigningKeyPair> decode_identity(
    std::array<std::uint8_t, kDeviceIdentityFileBytes> bytes,
    SigningIdentityRole expected_role, const Sodium &sodium) {
    const auto wipe = [&bytes] { secure_wipe(bytes); };
    if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[8U] != kFormatVersion || bytes[9U] != kAlgorithmEd25519) {
        wipe();
        return Status{ErrorCode::protocol_error,
                      "device identity magic, format, or algorithm is unsupported"};
    }
    if (bytes[10U] != static_cast<std::uint8_t>(expected_role)) {
        wipe();
        return Status{ErrorCode::protocol_error,
                      "signing identity role does not match its requested use"};
    }
    for (std::size_t index = 11U; index < 16U; ++index) {
        if (bytes[index] != 0U) {
            wipe();
            return Status{ErrorCode::protocol_error,
                          "device identity reserved bytes are non-zero"};
        }
    }

    SigningSeed seed{};
    std::copy_n(bytes.begin() + 16U, seed.size(), seed.begin());
    SigningPublicKey stored_public_key{};
    std::copy_n(bytes.begin() + 48U, stored_public_key.size(), stored_public_key.begin());
    auto keys = sodium.signing_keypair_from_seed(seed);
    secure_wipe(seed);
    wipe();
    if (!keys) {
        return keys.status();
    }
    if (!constant_time_equal(keys.value().public_key(), stored_public_key)) {
        return Status{ErrorCode::protocol_error,
                      "device identity seed does not derive its recorded public key"};
    }
    return std::move(keys).value();
}

Result<DeviceIdentity> create_identity(
    const std::filesystem::path &path, const Sodium &sodium) {
    SigningSeed seed{};
    const Status random = fill_random(seed);
    if (!random.ok()) {
        return random;
    }
    auto keys = sodium.signing_keypair_from_seed(seed);
    if (!keys) {
        secure_wipe(seed);
        return keys.status();
    }

    std::array<std::uint8_t, kDeviceIdentityFileBytes> bytes{};
    std::copy(kMagic.begin(), kMagic.end(), bytes.begin());
    bytes[8U] = kFormatVersion;
    bytes[9U] = kAlgorithmEd25519;
    std::copy(seed.begin(), seed.end(), bytes.begin() + 16U);
    std::copy(
        keys.value().public_key().begin(), keys.value().public_key().end(),
        bytes.begin() + 48U);
    secure_wipe(seed);

    const Status stored = StateStore::write_atomic(path, bytes);
    secure_wipe(bytes);
    if (!stored.ok()) {
        return stored;
    }
    // Re-open through the strict reader so creation and recovery use the same
    // parser and permission contract.
    return DeviceIdentity::load(path, sodium);
}

Result<DeviceIdentity> create_identity_no_replace(
    const std::filesystem::path &path, SigningIdentityRole role,
    const Sodium &sodium) {
    if (path.empty() || path.filename().empty()) {
        return Status{ErrorCode::invalid_argument,
                      "release signer identity path is empty"};
    }
    const std::filesystem::path parent = path.has_parent_path()
        ? path.parent_path()
        : std::filesystem::path{"."};
    struct stat parent_metadata {};
    if (::lstat(parent.c_str(), &parent_metadata) != 0) {
        return file_status("unable to inspect release signer directory", parent);
    }
    if (!S_ISDIR(parent_metadata.st_mode) ||
        parent_metadata.st_uid != ::geteuid() ||
        (parent_metadata.st_mode & 0077U) != 0U ||
        (parent_metadata.st_mode &
         static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "release signer directory must be owner-private: " +
                          parent.string()};
    }

    SigningSeed seed{};
    const Status random = fill_random(seed);
    if (!random.ok()) return random;
    auto keys = sodium.signing_keypair_from_seed(seed);
    if (!keys.ok()) {
        secure_wipe(seed);
        return keys.status();
    }
    std::array<std::uint8_t, kDeviceIdentityFileBytes> bytes{};
    std::copy(kMagic.begin(), kMagic.end(), bytes.begin());
    bytes[8U] = kFormatVersion;
    bytes[9U] = kAlgorithmEd25519;
    bytes[10U] = static_cast<std::uint8_t>(role);
    std::copy(seed.begin(), seed.end(), bytes.begin() + 16U);
    std::copy(keys.value().public_key().begin(),
              keys.value().public_key().end(), bytes.begin() + 48U);
    secure_wipe(seed);

    std::string pattern =
        (parent / (".iotox-" + path.filename().string() +
                   ".new.XXXXXX")).string();
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    const int descriptor = ::mkstemp(mutable_pattern.data());
    if (descriptor < 0) {
        secure_wipe(bytes);
        return file_status("unable to create release signer temporary", parent);
    }
    const std::filesystem::path temporary{mutable_pattern.data()};
    Status stored = Status::success();
    const int flags = ::fcntl(descriptor, F_GETFD);
    if (flags < 0 ||
        ::fcntl(descriptor, F_SETFD, flags | FD_CLOEXEC) != 0) {
        stored = file_status("unable to seal release signer temporary",
                             temporary);
    }
    if (stored.ok() && ::fchmod(descriptor, 0600) != 0) {
        stored = file_status("unable to secure release signer temporary",
                             temporary);
    }
    std::size_t offset = 0U;
    while (stored.ok() && offset < bytes.size()) {
        const ssize_t count = ::write(
            descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            stored = file_status("unable to write release signer temporary",
                                 temporary);
            break;
        }
        offset += static_cast<std::size_t>(count);
    }
    secure_wipe(bytes);
    if (stored.ok() && ::fsync(descriptor) != 0) {
        stored = file_status("unable to sync release signer temporary",
                             temporary);
    }
    if (::close(descriptor) != 0 && stored.ok()) {
        stored = file_status("unable to close release signer temporary",
                             temporary);
    }
    if (!stored.ok()) {
        static_cast<void>(::unlink(temporary.c_str()));
        return stored;
    }
    if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                  path.c_str(), RENAME_NOREPLACE) != 0) {
        const int error = errno;
        static_cast<void>(::unlink(temporary.c_str()));
        return error == EEXIST
            ? Status{ErrorCode::invalid_argument,
                     "release signer identity already exists: " +
                         path.string()}
            : file_status("unable to commit release signer identity", path,
                          error);
    }
    const int directory =
        ::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (directory < 0) {
        return file_status("unable to open release signer directory", parent);
    }
    const int sync_result = ::fsync(directory);
    const int sync_error = errno;
    const int close_result = ::close(directory);
    const int close_error = errno;
    if (sync_result != 0) {
        return file_status("unable to sync release signer directory", parent,
                          sync_error);
    }
    if (close_result != 0) {
        return file_status("unable to close release signer directory", parent,
                          close_error);
    }
    if (role == SigningIdentityRole::release) {
        return DeviceIdentity::load_release(path, sodium);
    }
    if (role == SigningIdentityRole::witness) {
        return DeviceIdentity::load_witness(path, sodium);
    }
    return DeviceIdentity::load(path, sodium);
}

}  // namespace

Result<DeviceIdentity> DeviceIdentity::load(
    const std::filesystem::path &path, const Sodium &sodium) {
    if (path.empty()) {
        return Status{ErrorCode::invalid_argument, "device identity path is empty"};
    }
    auto bytes = read_exact_private_file(path);
    if (!bytes) {
        return bytes.status();
    }
    auto keys = decode_identity(
        std::move(bytes).value(), SigningIdentityRole::device, sodium);
    if (!keys) {
        return keys.status();
    }
    return DeviceIdentity(path, std::move(keys).value(),
                          SigningIdentityRole::device, sodium);
}

Result<DeviceIdentity> DeviceIdentity::load_release(
    const std::filesystem::path &path, const Sodium &sodium) {
    if (path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "release signer identity path is empty"};
    }
    auto bytes = read_exact_private_file(path);
    if (!bytes.ok()) return bytes.status();
    auto keys = decode_identity(
        std::move(bytes).value(), SigningIdentityRole::release, sodium);
    if (!keys.ok()) return keys.status();
    return DeviceIdentity(path, std::move(keys).value(),
                          SigningIdentityRole::release, sodium);
}

Result<DeviceIdentity> DeviceIdentity::load_witness(
    const std::filesystem::path &path, const Sodium &sodium) {
    if (path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "witness service identity path is empty"};
    }
    auto bytes = read_exact_private_file(path);
    if (!bytes.ok()) return bytes.status();
    auto keys = decode_identity(
        std::move(bytes).value(), SigningIdentityRole::witness, sodium);
    if (!keys.ok()) return keys.status();
    return DeviceIdentity(path, std::move(keys).value(),
                          SigningIdentityRole::witness, sodium);
}

Result<DeviceIdentity> DeviceIdentity::load_or_create(
    const std::filesystem::path &path, const Sodium &sodium, bool allow_create) {
    auto loaded = load(path, sodium);
    if (loaded || loaded.status().code() != ErrorCode::not_found) {
        return loaded;
    }
    if (!allow_create) {
        return Status{ErrorCode::not_found,
                      "device identity is missing while durable authority state exists; "
                      "refusing to create an unrelated identity"};
    }
    return create_identity(path, sodium);
}

Result<DeviceIdentity> DeviceIdentity::create_new_release(
    const std::filesystem::path &path, const Sodium &sodium) {
    return create_identity_no_replace(
        path, SigningIdentityRole::release, sodium);
}

Result<DeviceIdentity> DeviceIdentity::create_new_witness(
    const std::filesystem::path &path, const Sodium &sodium) {
    return create_identity_no_replace(
        path, SigningIdentityRole::witness, sodium);
}

Result<Signature> DeviceIdentity::sign(
    std::span<const std::uint8_t> message) const {
    // The stable seed never crosses the process boundary. Authority-session,
    // route-binding, and attestation code pass only domain-separated canonical
    // messages into this narrow signer.
    if (sodium_ == nullptr) {
        return Status{ErrorCode::internal_error, "device identity lost its libsodium provider"};
    }
    return sodium_->sign_detached(message, keys_.secret_key());
}

std::filesystem::path default_device_identity_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) {
        return {};
    }
    const std::filesystem::path parent =
        tox_savedata_path.has_parent_path() ? tox_savedata_path.parent_path() :
                                              std::filesystem::path{"."};
    return parent / "device.identity";
}

}  // namespace iotox::security
