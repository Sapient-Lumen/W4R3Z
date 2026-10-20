#include "iotox/interactive_incarnation.hpp"

#include "iotox/security/random.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <span>
#include <string>
#include <string_view>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

namespace iotox::interactive {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {
    'I', 'O', 'T', 'X', 'R', 'I', 'N', '1'};
constexpr std::uint8_t kFormatVersion = 1U;
constexpr std::uint8_t kAlgorithmEd25519 = 1U;
constexpr std::size_t kPublicKeyOffset = 16U;
constexpr std::size_t kIncarnationOffset = 48U;
constexpr std::size_t kComplementOffset = 56U;
constexpr std::size_t kSignatureOffset = 64U;
constexpr std::size_t kSignedPrefixBytes = kSignatureOffset;
constexpr std::size_t kRecordBytes =
    kSignatureOffset + security::kSignatureBytes;
constexpr std::array<std::uint8_t, 8U> kWitnessIntentMagic = {
    'I', 'O', 'T', 'X', 'I', 'W', 'I', '1'};
constexpr std::size_t kWitnessIntentSignedBytes = 320U;
constexpr std::size_t kWitnessIntentBytes =
    kWitnessIntentSignedBytes + security::kSignatureBytes;
constexpr std::uint64_t kInitialIncarnationMask =
    std::numeric_limits<std::uint64_t>::max() >> 1U;
constexpr std::size_t kTemporaryCreateAttempts = 32U;

static_assert(kRecordBytes == 128U);
static_assert(kWitnessIntentBytes == 384U);

struct IncarnationState {
    bool present{false};
    std::uint64_t incarnation{0U};
    std::array<std::uint8_t, kRecordBytes> bytes{};
    rollback_witness::Head head{};
};

struct IncarnationWitnessIntent {
    rollback_witness::DomainId domain{};
    security::SigningPublicKey device{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Lane lane{
        rollback_witness::Lane::application_incarnation};
    rollback_witness::Head current;
    rollback_witness::Head next;
    rollback_witness::TransactionNonce nonce{};
    std::array<std::uint8_t, kRecordBytes> record{};
};

class ScopedDescriptor {
  public:
    explicit ScopedDescriptor(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~ScopedDescriptor() { reset(); }

    ScopedDescriptor(const ScopedDescriptor &) = delete;
    ScopedDescriptor &operator=(const ScopedDescriptor &) = delete;
    ScopedDescriptor(ScopedDescriptor &&other) noexcept
        : descriptor_(other.release()) {}
    ScopedDescriptor &operator=(ScopedDescriptor &&other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] explicit operator bool() const noexcept {
        return descriptor_ >= 0;
    }
    [[nodiscard]] int release() noexcept {
        const int descriptor = descriptor_;
        descriptor_ = -1;
        return descriptor;
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) {
            // On Linux the descriptor is closed even when close(2) reports
            // EINTR. Retrying could therefore close an unrelated descriptor
            // that another thread has already reused.
            static_cast<void>(::close(descriptor_));
        }
        descriptor_ = descriptor;
    }

  private:
    int descriptor_{-1};
};

Status io_status(
    std::string operation,
    const std::filesystem::path &path,
    int error = errno) {
    return Status{
        ErrorCode::io_error,
        std::move(operation) + " '" + path.string() + "': " +
            std::strerror(error)};
}

Status descriptor_status(
    std::string operation,
    const std::filesystem::path &path,
    int error) {
    return Status{
        error == EWOULDBLOCK || error == EAGAIN
            ? ErrorCode::resource_exhausted
            : ErrorCode::io_error,
        std::move(operation) + " '" + path.string() + "': " +
            std::strerror(error)};
}

Status synchronize_descriptor(
    int descriptor,
    std::string operation,
    const std::filesystem::path &path) {
    int result = -1;
    do {
        result = ::fsync(descriptor);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        return io_status(std::move(operation), path);
    }
    return Status::success();
}

void write_u64(
    std::array<std::uint8_t, kRecordBytes> &bytes,
    std::size_t offset,
    std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        const unsigned int shift =
            static_cast<unsigned int>((7U - index) * 8U);
        bytes[offset + index] =
            static_cast<std::uint8_t>((value >> shift) & 0xffU);
    }
}

std::uint64_t read_u64(
    const std::array<std::uint8_t, kRecordBytes> &bytes,
    std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) |
                static_cast<std::uint64_t>(bytes[offset + index]);
    }
    return value;
}

void put_u64(std::span<std::uint8_t> bytes, std::size_t offset,
             std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        bytes[offset + index] = static_cast<std::uint8_t>(
            value >> ((7U - index) * 8U));
    }
}

std::uint64_t get_u64(std::span<const std::uint8_t> bytes,
                      std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

bool incarnation_lane(rollback_witness::Lane lane) {
    return lane == rollback_witness::Lane::application_incarnation ||
        lane == rollback_witness::Lane::ratox_incarnation;
}

std::string_view incarnation_hash_domain(rollback_witness::Lane lane) {
    return lane == rollback_witness::Lane::application_incarnation
        ? "application-incarnation-witness-v1"
        : "ratox-incarnation-witness-v1";
}

Status validate_private_regular_file(
    const struct stat &metadata,
    const std::filesystem::path &path,
    std::string_view label) {
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1) {
        return Status{
            ErrorCode::io_error,
            std::string(label) +
                " must be a single-link regular file owned by the running user: " +
                path.string()};
    }
    if ((metadata.st_mode & 07777U) != 0600U) {
        return Status{
            ErrorCode::io_error,
            std::string(label) + " must have exact mode 0600: " +
                path.string()};
    }
    return Status::success();
}

Status validate_private_directory(
    int descriptor,
    const std::filesystem::path &path) {
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return io_status("unable to inspect Ratox incarnation directory", path);
    }
    if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{
            ErrorCode::io_error,
            "Ratox incarnation directory must be owned by the running user: " +
                path.string()};
    }
    if ((metadata.st_mode & 07777U) != 0700U) {
        return Status{
            ErrorCode::io_error,
            "Ratox incarnation directory must have exact mode 0700: " +
                path.string()};
    }
    return Status::success();
}

struct ParentHandle {
    ScopedDescriptor descriptor;
    std::filesystem::path path;
    std::string filename;
};

Result<ParentHandle> open_private_parent(
    const std::filesystem::path &state_path) {
    if (state_path.empty() || state_path.filename().empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox incarnation state path must name a file"};
    }
    const std::string filename = state_path.filename().string();
    if (filename == "." || filename == ".." ||
        filename.find('\0') != std::string::npos) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox incarnation state filename is unsafe"};
    }

    std::filesystem::path parent = state_path.parent_path();
    if (parent.empty()) parent = ".";

    ScopedDescriptor current;
    if (parent.is_absolute()) {
        current.reset(::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC));
    } else {
        current.reset(::open(".", O_RDONLY | O_DIRECTORY | O_CLOEXEC));
    }
    if (!current) {
        return io_status(
            "unable to open Ratox incarnation traversal root", parent);
    }

    std::filesystem::path walked = parent.is_absolute()
        ? std::filesystem::path{"/"}
        : std::filesystem::path{"."};
    bool saw_component = false;
    for (const std::filesystem::path &part : parent) {
        const std::string component = part.string();
        if (component.empty() || component == "/" || component == ".") {
            continue;
        }
        if (component == ".." || component.find('\0') != std::string::npos) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox incarnation state path may not contain '..' or NUL components"};
        }
        saw_component = true;
        walked /= part;

        int next = -1;
        do {
            next = ::openat(
                current.get(), component.c_str(),
                O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
        } while (next < 0 && errno == EINTR);
        if (next < 0 && errno == ENOENT) {
            int create_result = -1;
            do {
                create_result =
                    ::mkdirat(current.get(), component.c_str(), 0700);
            } while (create_result != 0 && errno == EINTR);
            const bool created_component = create_result == 0;
            if (create_result != 0 && errno != EEXIST) {
                return io_status(
                    "unable to create Ratox incarnation directory", walked);
            }
            do {
                next = ::openat(
                    current.get(), component.c_str(),
                    O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
            } while (next < 0 && errno == EINTR);
            if (next >= 0 && created_component) {
                ScopedDescriptor created(next);
                if (::fchmod(created.get(), 0700) != 0) {
                    return io_status(
                        "unable to enforce Ratox incarnation directory permissions",
                        walked);
                }
                const Status private_created =
                    validate_private_directory(created.get(), walked);
                if (!private_created.ok()) return private_created;
                const Status directory_synced = synchronize_descriptor(
                    created.get(),
                    "unable to synchronize newly created Ratox incarnation directory",
                    walked);
                if (!directory_synced.ok()) return directory_synced;
                // fsync(new-directory) persists its inode metadata; fsync on
                // the containing directory is separately required to make the
                // new directory name durable before the host depends on it.
                const Status entry_synced = synchronize_descriptor(
                    current.get(),
                    "unable to synchronize containing Ratox incarnation directory",
                    walked.parent_path());
                if (!entry_synced.ok()) return entry_synced;
                next = created.release();
            }
        }
        if (next < 0) {
            return io_status(
                "unable to traverse Ratox incarnation directory", walked);
        }
        current.reset(next);
    }

    // For an explicit "." parent, validate the current directory too. Existing
    // broad ancestors such as /tmp are traversed without following symlinks,
    // but only the final state lane is required to be owner-private.
    static_cast<void>(saw_component);
    const Status private_parent = validate_private_directory(current.get(), parent);
    if (!private_parent.ok()) return private_parent;

    return ParentHandle{std::move(current), parent, filename};
}

Result<int> acquire_lock(
    int parent_descriptor,
    std::string_view state_filename,
    const std::filesystem::path &state_path) {
    const std::string lock_filename = std::string(state_filename) + ".lock";
    const std::filesystem::path lock_path =
        state_path.parent_path() / lock_filename;

    int descriptor = -1;
    bool created = false;
    do {
        descriptor = ::openat(
            parent_descriptor, lock_filename.c_str(),
            O_RDWR | O_CLOEXEC | O_NOFOLLOW | O_CREAT | O_EXCL, 0600);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor >= 0) {
        created = true;
    } else if (errno == EEXIST) {
        do {
            descriptor = ::openat(
                parent_descriptor, lock_filename.c_str(),
                O_RDWR | O_CLOEXEC | O_NOFOLLOW);
        } while (descriptor < 0 && errno == EINTR);
    }
    if (descriptor < 0) {
        return io_status("unable to open Ratox incarnation lock", lock_path);
    }
    ScopedDescriptor lock(descriptor);
    if (created && ::fchmod(lock.get(), 0600) != 0) {
        return io_status(
            "unable to enforce Ratox incarnation lock permissions", lock_path);
    }

    struct stat descriptor_metadata {};
    if (::fstat(lock.get(), &descriptor_metadata) != 0) {
        return io_status("unable to inspect Ratox incarnation lock", lock_path);
    }
    const Status safe_lock = validate_private_regular_file(
        descriptor_metadata, lock_path, "Ratox incarnation lock");
    if (!safe_lock.ok()) return safe_lock;
    if (descriptor_metadata.st_size != 0) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation lock must remain an empty fixed-purpose file: " +
                lock_path.string()};
    }

    struct stat path_metadata {};
    if (::fstatat(
            parent_descriptor, lock_filename.c_str(), &path_metadata,
            AT_SYMLINK_NOFOLLOW) != 0) {
        return io_status(
            "unable to re-inspect Ratox incarnation lock path", lock_path);
    }
    if (path_metadata.st_dev != descriptor_metadata.st_dev ||
        path_metadata.st_ino != descriptor_metadata.st_ino) {
        return Status{
            ErrorCode::io_error,
            "Ratox incarnation lock path changed during acquisition: " +
                lock_path.string()};
    }

    int result = -1;
    do {
        result = ::flock(lock.get(), LOCK_EX | LOCK_NB);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        if (error == EWOULDBLOCK || error == EAGAIN) {
            return Status{
                ErrorCode::resource_exhausted,
                "another IoTox host already owns the Ratox incarnation lane: " +
                    state_path.string()};
        }
        return descriptor_status(
            "unable to lock Ratox incarnation lane", lock_path, error);
    }

    // Revalidate after flock. The pre-lock check prevents following a link,
    // while this second identity check closes a same-owner rename window
    // between inspection and successful lease acquisition.
    struct stat locked_metadata {};
    if (::fstat(lock.get(), &locked_metadata) != 0) {
        return io_status(
            "unable to inspect locked Ratox incarnation lease", lock_path);
    }
    const Status safe_locked = validate_private_regular_file(
        locked_metadata, lock_path, "Ratox incarnation lock");
    if (!safe_locked.ok()) return safe_locked;
    if (locked_metadata.st_size != 0) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation lock changed after lease acquisition: " +
                lock_path.string()};
    }
    struct stat locked_path_metadata {};
    if (::fstatat(
            parent_descriptor, lock_filename.c_str(),
            &locked_path_metadata, AT_SYMLINK_NOFOLLOW) != 0) {
        return io_status(
            "unable to revalidate locked Ratox incarnation path", lock_path);
    }
    if (locked_path_metadata.st_dev != locked_metadata.st_dev ||
        locked_path_metadata.st_ino != locked_metadata.st_ino) {
        return Status{
            ErrorCode::io_error,
            "Ratox incarnation lock path changed after lease acquisition: " +
                lock_path.string()};
    }
    return lock.release();
}

template <std::size_t Bytes>
Result<std::array<std::uint8_t, Bytes>> read_fixed_record(
    int parent_descriptor,
    std::string_view filename,
    const std::filesystem::path &path,
    std::string_view label) {
    int descriptor = -1;
    do {
        descriptor = ::openat(
            parent_descriptor, std::string(filename).c_str(),
            O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (errno == ENOENT) {
            return Status{
                ErrorCode::not_found,
                std::string(label) + " does not exist: " + path.string()};
        }
        return io_status("unable to open " + std::string(label), path);
    }
    ScopedDescriptor state(descriptor);

    struct stat metadata {};
    if (::fstat(state.get(), &metadata) != 0) {
        return io_status("unable to inspect " + std::string(label), path);
    }
    const Status safe_state = validate_private_regular_file(
        metadata, path, label);
    if (!safe_state.ok()) return safe_state;
    if (metadata.st_size != static_cast<off_t>(Bytes)) {
        return Status{
            ErrorCode::protocol_error,
            std::string(label) + " has an unexpected fixed-record size: " +
            path.string()};
    }

    struct stat path_metadata {};
    if (::fstatat(
            parent_descriptor, std::string(filename).c_str(), &path_metadata,
            AT_SYMLINK_NOFOLLOW) != 0) {
        return io_status(
            "unable to re-inspect " + std::string(label) + " path", path);
    }
    if (path_metadata.st_dev != metadata.st_dev ||
        path_metadata.st_ino != metadata.st_ino) {
        return Status{
            ErrorCode::io_error,
            std::string(label) + " path changed while it was opened: " +
            path.string()};
    }

    std::array<std::uint8_t, Bytes> bytes{};
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            state.get(), bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) {
            return io_status("unable to read " + std::string(label), path);
        }
        if (count == 0) {
            return Status{
                ErrorCode::io_error,
                std::string(label) +
                    " ended before its fixed record completed: " +
                path.string()};
        }
        offset += static_cast<std::size_t>(count);
    }
    return bytes;
}

Result<std::array<std::uint8_t, kRecordBytes>> read_record(
    int parent_descriptor,
    std::string_view filename,
    const std::filesystem::path &path) {
    return read_fixed_record<kRecordBytes>(
        parent_descriptor, filename, path, "Ratox incarnation state");
}

Result<std::uint64_t> decode_record(
    const std::array<std::uint8_t, kRecordBytes> &bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[8U] != kFormatVersion ||
        bytes[9U] != kAlgorithmEd25519) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation state magic, format, or algorithm is unsupported"};
    }
    for (std::size_t index = 10U; index < 16U; ++index) {
        if (bytes[index] != 0U) {
            return Status{
                ErrorCode::protocol_error,
                "Ratox incarnation state reserved bytes are non-zero"};
        }
    }

    security::SigningPublicKey stored_public_key{};
    std::copy_n(
        bytes.begin() + static_cast<std::ptrdiff_t>(kPublicKeyOffset),
        stored_public_key.size(), stored_public_key.begin());
    if (!security::constant_time_equal(
            stored_public_key, identity.public_key())) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation state belongs to a different device identity"};
    }

    const std::uint64_t incarnation = read_u64(bytes, kIncarnationOffset);
    const std::uint64_t complement = read_u64(bytes, kComplementOffset);
    if (incarnation == 0U || complement != ~incarnation) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation value or complement is invalid"};
    }

    security::Signature signature{};
    std::copy_n(
        bytes.begin() + static_cast<std::ptrdiff_t>(kSignatureOffset),
        signature.size(), signature.begin());
    const Status verified = sodium.verify_detached(
        signature,
        std::span<const std::uint8_t>(bytes.data(), kSignedPrefixBytes),
        stored_public_key);
    if (!verified.ok()) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation state signature verification failed"};
    }
    return incarnation;
}

Result<std::array<std::uint8_t, kRecordBytes>> encode_record(
    std::uint64_t incarnation,
    const security::DeviceIdentity &identity) {
    if (incarnation == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox incarnation zero is reserved"};
    }
    std::array<std::uint8_t, kRecordBytes> bytes{};
    std::copy(kMagic.begin(), kMagic.end(), bytes.begin());
    bytes[8U] = kFormatVersion;
    bytes[9U] = kAlgorithmEd25519;
    std::copy(
        identity.public_key().begin(), identity.public_key().end(),
        bytes.begin() + static_cast<std::ptrdiff_t>(kPublicKeyOffset));
    write_u64(bytes, kIncarnationOffset, incarnation);
    write_u64(bytes, kComplementOffset, ~incarnation);
    auto signature = identity.sign(
        std::span<const std::uint8_t>(bytes.data(), kSignedPrefixBytes));
    if (!signature) return signature.status();
    std::copy(
        signature.value().begin(), signature.value().end(),
        bytes.begin() + static_cast<std::ptrdiff_t>(kSignatureOffset));
    return bytes;
}

Result<rollback_witness::Head> incarnation_head(
    const std::array<std::uint8_t, kRecordBytes> &bytes,
    std::uint64_t incarnation,
    const security::Sodium &sodium,
    rollback_witness::Lane lane) {
    if (!incarnation_lane(lane) || incarnation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "incarnation witness head has an invalid lane or position"};
    }
    auto digest = sodium.hash(incarnation_hash_domain(lane), bytes);
    if (!digest) return digest.status();
    rollback_witness::Head head;
    head.position = incarnation;
    head.digest = digest.value();
    return head;
}

Result<IncarnationState> load_incarnation_state(
    int parent_descriptor,
    std::string_view filename,
    const std::filesystem::path &path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::Lane lane) {
    auto bytes = read_record(parent_descriptor, filename, path);
    if (!bytes && bytes.status().code() == ErrorCode::not_found) {
        return IncarnationState{};
    }
    if (!bytes) return bytes.status();
    auto incarnation = decode_record(bytes.value(), identity, sodium);
    if (!incarnation) return incarnation.status();
    auto head = incarnation_head(
        bytes.value(), incarnation.value(), sodium, lane);
    if (!head) return head.status();
    IncarnationState state;
    state.present = true;
    state.incarnation = incarnation.value();
    state.bytes = bytes.value();
    state.head = head.value();
    return state;
}

Result<std::array<std::uint8_t, kWitnessIntentBytes>> encode_witness_intent(
    const IncarnationWitnessIntent &intent,
    const security::DeviceIdentity &identity) {
    if (!incarnation_lane(intent.lane) ||
        intent.device != identity.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "incarnation witness intent identity or lane is invalid"};
    }
    rollback_witness::Record committed;
    committed.domain = intent.domain;
    committed.device = intent.device;
    committed.witness_epoch = intent.witness_epoch;
    committed.lane = intent.lane;
    committed.committed = intent.current;
    auto pending = rollback_witness::begin(
        committed, intent.next, intent.nonce);
    if (!pending) return pending.status();

    std::array<std::uint8_t, kWitnessIntentBytes> bytes{};
    std::copy(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
              bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = static_cast<std::uint8_t>(intent.lane);
    std::copy(intent.domain.begin(), intent.domain.end(), bytes.begin() + 16U);
    std::copy(intent.device.begin(), intent.device.end(), bytes.begin() + 32U);
    put_u64(bytes, 64U, intent.witness_epoch);
    put_u64(bytes, 72U, intent.current.position);
    std::copy(intent.current.digest.begin(), intent.current.digest.end(),
              bytes.begin() + 80U);
    put_u64(bytes, 112U, intent.next.position);
    std::copy(intent.next.digest.begin(), intent.next.digest.end(),
              bytes.begin() + 120U);
    std::copy(intent.nonce.begin(), intent.nonce.end(), bytes.begin() + 152U);
    std::copy(intent.record.begin(), intent.record.end(), bytes.begin() + 184U);
    auto signature = identity.sign(
        std::span<const std::uint8_t>{bytes}.first<kWitnessIntentSignedBytes>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + kWitnessIntentSignedBytes);
    return bytes;
}

Result<IncarnationWitnessIntent> decode_witness_intent(
    const std::array<std::uint8_t, kWitnessIntentBytes> &bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (!std::equal(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
                    bytes.begin()) ||
        bytes[8U] != 1U || !all_zero(std::span<const std::uint8_t>{bytes}.subspan(10U, 6U)) ||
        !all_zero(std::span<const std::uint8_t>{bytes}.subspan(312U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent header or reserved bytes are invalid"};
    }
    IncarnationWitnessIntent intent;
    intent.lane = static_cast<rollback_witness::Lane>(bytes[9U]);
    std::copy_n(bytes.begin() + 16U, intent.domain.size(),
                intent.domain.begin());
    std::copy_n(bytes.begin() + 32U, intent.device.size(),
                intent.device.begin());
    intent.witness_epoch = get_u64(bytes, 64U);
    intent.current.position = get_u64(bytes, 72U);
    std::copy_n(bytes.begin() + 80U, intent.current.digest.size(),
                intent.current.digest.begin());
    intent.next.position = get_u64(bytes, 112U);
    std::copy_n(bytes.begin() + 120U, intent.next.digest.size(),
                intent.next.digest.begin());
    std::copy_n(bytes.begin() + 152U, intent.nonce.size(),
                intent.nonce.begin());
    std::copy_n(bytes.begin() + 184U, intent.record.size(),
                intent.record.begin());
    if (!incarnation_lane(intent.lane) ||
        intent.device != identity.public_key()) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent belongs to another identity or lane"};
    }
    rollback_witness::Record committed;
    committed.domain = intent.domain;
    committed.device = intent.device;
    committed.witness_epoch = intent.witness_epoch;
    committed.lane = intent.lane;
    committed.committed = intent.current;
    if (!rollback_witness::begin(committed, intent.next, intent.nonce)) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent does not contain one forward transition"};
    }
    auto decoded = decode_record(intent.record, identity, sodium);
    if (!decoded || decoded.value() != intent.next.position) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent record does not encode its next position"};
    }
    auto head = incarnation_head(
        intent.record, decoded.value(), sodium, intent.lane);
    if (!head || !(head.value() == intent.next)) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent record digest does not match its next head"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + kWitnessIntentSignedBytes,
                signature.size(), signature.begin());
    const Status verified = sodium.verify_detached(
        signature,
        std::span<const std::uint8_t>{bytes}.first<kWitnessIntentSignedBytes>(),
        intent.device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent signature is invalid"};
    }
    return intent;
}

Status write_all(
    int descriptor,
    std::span<const std::uint8_t> bytes,
    const std::filesystem::path &path) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::write(
            descriptor,
            bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) {
            return io_status("unable to write Ratox incarnation state", path);
        }
        if (count == 0) {
            return Status{
                ErrorCode::io_error,
                "Ratox incarnation state write made no progress: " +
                    path.string()};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Status write_record_atomic(
    int parent_descriptor,
    std::string_view filename,
    const std::filesystem::path &path,
    std::span<const std::uint8_t> bytes) {
    std::string temporary_name;
    ScopedDescriptor temporary;
    for (std::size_t attempt = 0U;
         attempt < kTemporaryCreateAttempts; ++attempt) {
        auto random = security::random_u64_nonzero();
        if (!random) return random.status();
        temporary_name = "." + std::string(filename) + ".tmp." +
                         std::to_string(static_cast<unsigned long long>(::getpid())) +
                         "." +
                         std::to_string(
                             static_cast<unsigned long long>(random.value()));
        int descriptor = -1;
        do {
            descriptor = ::openat(
                parent_descriptor, temporary_name.c_str(),
                O_WRONLY | O_CLOEXEC | O_NOFOLLOW | O_CREAT | O_EXCL,
                0600);
        } while (descriptor < 0 && errno == EINTR);
        if (descriptor >= 0) {
            temporary.reset(descriptor);
            break;
        }
        if (errno != EEXIST) {
            return io_status(
                "unable to create temporary Ratox incarnation state", path);
        }
    }
    if (!temporary) {
        return Status{
            ErrorCode::resource_exhausted,
            "unable to allocate a unique temporary Ratox incarnation state"};
    }

    const auto cleanup = [&] {
        if (!temporary_name.empty()) {
            static_cast<void>(::unlinkat(
                parent_descriptor, temporary_name.c_str(), 0));
        }
    };
    if (::fchmod(temporary.get(), 0600) != 0) {
        const Status status = io_status(
            "unable to enforce temporary Ratox incarnation permissions", path);
        cleanup();
        return status;
    }
    const Status written = write_all(temporary.get(), bytes, path);
    if (!written.ok()) {
        cleanup();
        return written;
    }
    const Status temporary_synced = synchronize_descriptor(
        temporary.get(),
        "unable to synchronize temporary Ratox incarnation state", path);
    if (!temporary_synced.ok()) {
        cleanup();
        return temporary_synced;
    }

    struct stat temporary_metadata {};
    if (::fstat(temporary.get(), &temporary_metadata) != 0) {
        const Status status = io_status(
            "unable to inspect temporary Ratox incarnation state", path);
        cleanup();
        return status;
    }
    const Status safe_temporary = validate_private_regular_file(
        temporary_metadata, path, "temporary Ratox incarnation state");
    if (!safe_temporary.ok()) {
        cleanup();
        return safe_temporary;
    }
    if (temporary_metadata.st_size != static_cast<off_t>(bytes.size())) {
        cleanup();
        return Status{
            ErrorCode::io_error,
            "temporary Ratox incarnation state changed before commit: " +
                path.string()};
    }
    struct stat temporary_path_metadata {};
    if (::fstatat(
            parent_descriptor, temporary_name.c_str(),
            &temporary_path_metadata, AT_SYMLINK_NOFOLLOW) != 0) {
        const Status status = io_status(
            "unable to revalidate temporary Ratox incarnation path", path);
        cleanup();
        return status;
    }
    if (temporary_path_metadata.st_dev != temporary_metadata.st_dev ||
        temporary_path_metadata.st_ino != temporary_metadata.st_ino) {
        cleanup();
        return Status{
            ErrorCode::io_error,
            "temporary Ratox incarnation path changed before commit: " +
                path.string()};
    }
    // Keep the temporary descriptor open across rename. Closing it here would
    // leave a same-owner unlink-and-replace window between the last identity
    // check and installation, even though the parent itself remains pinned by
    // descriptor.
    const std::string final_name(filename);
    if (::renameat(
            parent_descriptor, temporary_name.c_str(),
            parent_descriptor, final_name.c_str()) != 0) {
        const Status status = io_status(
            "unable to commit Ratox incarnation state", path);
        cleanup();
        return status;
    }
    temporary_name.clear();

    struct stat committed_path_metadata {};
    if (::fstatat(
            parent_descriptor, final_name.c_str(), &committed_path_metadata,
            AT_SYMLINK_NOFOLLOW) != 0) {
        return io_status(
            "unable to revalidate committed Ratox incarnation path", path);
    }
    if (committed_path_metadata.st_dev != temporary_metadata.st_dev ||
        committed_path_metadata.st_ino != temporary_metadata.st_ino) {
        return Status{
            ErrorCode::io_error,
            "committed Ratox incarnation path changed before directory synchronization: " +
                path.string()};
    }
    return synchronize_descriptor(
        parent_descriptor,
        "unable to synchronize Ratox incarnation directory",
        path.parent_path());
}

std::filesystem::path effective_parent(const std::filesystem::path &path) {
    return path.has_parent_path() ? path.parent_path()
                                  : std::filesystem::path{"."};
}

Status validate_witness_config(
    const IncarnationWitnessConfig &config,
    const std::filesystem::path &state_path) {
    if (!config.backend || !incarnation_lane(config.lane) ||
        all_zero(config.domain) || config.witness_epoch == 0U ||
        config.intent_path.empty() ||
        effective_parent(config.intent_path) != effective_parent(state_path) ||
        config.intent_path.filename().empty() ||
        config.intent_path.filename() == state_path.filename()) {
        return Status{
            ErrorCode::invalid_argument,
            "incarnation witness requires a backend, nonzero domain/epoch, "
            "closed incarnation lane, and distinct same-directory intent"};
    }
    const std::string intent_name = config.intent_path.filename().string();
    if (intent_name == "." || intent_name == ".." ||
        intent_name.find('\0') != std::string::npos) {
        return Status{ErrorCode::invalid_argument,
                      "incarnation witness intent filename is unsafe"};
    }
    if (!config.backend->independently_controlled() &&
        !config.allow_non_independent_for_testing) {
        return Status{
            ErrorCode::invalid_argument,
            "incarnation rollback witness is not independently controlled"};
    }
    return Status::success();
}

Result<std::optional<IncarnationWitnessIntent>> read_witness_intent(
    int parent_descriptor,
    const IncarnationWitnessConfig &config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    const std::string filename = config.intent_path.filename().string();
    auto bytes = read_fixed_record<kWitnessIntentBytes>(
        parent_descriptor, filename, config.intent_path,
        "incarnation witness intent");
    if (!bytes && bytes.status().code() == ErrorCode::not_found) {
        return std::optional<IncarnationWitnessIntent>{};
    }
    if (!bytes) return bytes.status();
    auto decoded = decode_witness_intent(bytes.value(), identity, sodium);
    if (!decoded) return decoded.status();
    return std::optional<IncarnationWitnessIntent>{decoded.value()};
}

Status remove_witness_intent(
    int parent_descriptor,
    const IncarnationWitnessConfig &config) {
    const std::string filename = config.intent_path.filename().string();
    if (::unlinkat(parent_descriptor, filename.c_str(), 0) != 0 &&
        errno != ENOENT) {
        return io_status("unable to remove incarnation witness intent",
                         config.intent_path);
    }
    return synchronize_descriptor(
        parent_descriptor,
        "unable to synchronize removed incarnation witness intent",
        effective_parent(config.intent_path));
}

rollback_witness::Record witness_record(
    const IncarnationWitnessConfig &config,
    const security::DeviceIdentity &identity,
    const rollback_witness::Head &head) {
    rollback_witness::Record record;
    record.domain = config.domain;
    record.device = identity.public_key();
    record.witness_epoch = config.witness_epoch;
    record.lane = config.lane;
    record.committed = head;
    return record;
}

bool same_witness_identity(
    const rollback_witness::Record &record,
    const IncarnationWitnessConfig &config,
    const security::DeviceIdentity &identity) {
    return record.domain == config.domain &&
        record.device == identity.public_key() &&
        record.witness_epoch == config.witness_epoch &&
        record.lane == config.lane;
}

bool same_intent_identity(
    const IncarnationWitnessIntent &intent,
    const IncarnationWitnessConfig &config,
    const security::DeviceIdentity &identity) {
    return intent.domain == config.domain &&
        intent.device == identity.public_key() &&
        intent.witness_epoch == config.witness_epoch &&
        intent.lane == config.lane;
}

Result<IncarnationState> reconcile_witness(
    int parent_descriptor,
    std::string_view state_filename,
    const std::filesystem::path &state_path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const IncarnationWitnessConfig &config,
    IncarnationState local) {
    auto observed = config.backend->query();
    if (!observed) {
        return Status{observed.status().code(),
                      "unable to query incarnation rollback witness: " +
                          observed.status().message()};
    }
    if (!rollback_witness::validate(observed.value()).ok() ||
        !same_witness_identity(observed.value(), config, identity)) {
        return Status{ErrorCode::protocol_error,
                      "incarnation rollback witness returned another or invalid lane"};
    }
    auto loaded_intent = read_witness_intent(
        parent_descriptor, config, identity, sodium);
    if (!loaded_intent) return loaded_intent.status();
    const bool has_intent = loaded_intent.value().has_value();

    if (!observed.value().pending) {
        if (!(observed.value().committed == local.head)) {
            return Status{
                ErrorCode::protocol_error,
                "local incarnation does not match the committed witness head; rollback, deletion, or fork detected"};
        }
        if (!has_intent) return local;
        const IncarnationWitnessIntent &intent = *loaded_intent.value();
        if (!same_intent_identity(intent, config, identity)) {
            return Status{ErrorCode::protocol_error,
                          "incarnation witness intent identity does not match configuration"};
        }
        if (intent.current == local.head) {
            const Status removed = remove_witness_intent(
                parent_descriptor, config);
            if (!removed.ok()) return removed;
            return local;
        }
        if (intent.next == local.head && local.present &&
            intent.record == local.bytes) {
            const Status removed = remove_witness_intent(
                parent_descriptor, config);
            if (!removed.ok()) return removed;
            return local;
        }
        return Status{ErrorCode::protocol_error,
                      "incarnation witness intent does not join committed local and external state"};
    }

    if (!has_intent) {
        return Status{ErrorCode::protocol_error,
                      "incarnation witness is pending without its exact durable intent"};
    }
    const IncarnationWitnessIntent &intent = *loaded_intent.value();
    if (!same_intent_identity(intent, config, identity) ||
        !(intent.current == observed.value().committed) ||
        !(intent.next == *observed.value().pending) ||
        intent.nonce != *observed.value().nonce) {
        return Status{ErrorCode::protocol_error,
                      "pending incarnation witness does not match its exact durable intent"};
    }

    if (local.head == intent.current) {
        const Status written = write_record_atomic(
            parent_descriptor, state_filename, state_path, intent.record);
        if (!written.ok()) return written;
        auto applied = load_incarnation_state(
            parent_descriptor, state_filename, state_path, identity, sodium,
            config.lane);
        if (!applied || !(applied.value().head == intent.next) ||
            applied.value().bytes != intent.record) {
            return Status{ErrorCode::protocol_error,
                          "recovered incarnation record does not match its witnessed next head"};
        }
        local = applied.value();
    } else if (!(local.head == intent.next) || !local.present ||
               local.bytes != intent.record) {
        return Status{ErrorCode::protocol_error,
                      "local incarnation is neither exact side of the pending witness transition"};
    }

    auto committed = rollback_witness::finish(observed.value());
    if (!committed) return committed.status();
    const Status exchanged = config.backend->compare_exchange(
        observed.value(), committed.value());
    if (!exchanged.ok()) {
        auto resolved = config.backend->query();
        if (!resolved || !(resolved.value() == committed.value())) {
            return Status{
                exchanged.code(),
                "unable to commit recovered incarnation witness transition: " +
                    exchanged.message()};
        }
    }
    const Status removed = remove_witness_intent(parent_descriptor, config);
    if (!removed.ok()) return removed;
    return local;
}

Result<IncarnationState> advance_witnessed(
    int parent_descriptor,
    std::string_view state_filename,
    const std::filesystem::path &state_path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const IncarnationWitnessConfig &config,
    IncarnationState current) {
    if (current.present &&
        current.incarnation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "witnessed incarnation namespace is exhausted"};
    }
    const std::uint64_t next_incarnation =
        current.present ? current.incarnation + 1U : 1U;
    auto encoded = encode_record(next_incarnation, identity);
    if (!encoded) return encoded.status();
    auto next_head = incarnation_head(
        encoded.value(), next_incarnation, sodium, config.lane);
    if (!next_head) return next_head.status();

    const rollback_witness::Record expected = witness_record(
        config, identity, current.head);
    auto observed = config.backend->query();
    if (!observed || !(observed.value() == expected)) {
        return Status{
            observed ? ErrorCode::protocol_error : observed.status().code(),
            observed
                ? "incarnation witness changed before the startup advance"
                : "unable to query incarnation witness before startup advance: " +
                      observed.status().message()};
    }
    rollback_witness::TransactionNonce nonce{};
    const Status random = security::fill_random(nonce);
    if (!random.ok()) return random;
    auto pending = rollback_witness::begin(expected, next_head.value(), nonce);
    if (!pending) return pending.status();

    IncarnationWitnessIntent intent;
    intent.domain = config.domain;
    intent.device = identity.public_key();
    intent.witness_epoch = config.witness_epoch;
    intent.lane = config.lane;
    intent.current = current.head;
    intent.next = next_head.value();
    intent.nonce = nonce;
    intent.record = encoded.value();
    auto intent_bytes = encode_witness_intent(intent, identity);
    if (!intent_bytes) return intent_bytes.status();
    const Status intent_written = write_record_atomic(
        parent_descriptor, config.intent_path.filename().string(),
        config.intent_path, intent_bytes.value());
    if (!intent_written.ok()) return intent_written;

    const Status began = config.backend->compare_exchange(
        expected, pending.value());
    if (!began.ok()) {
        auto resolved = config.backend->query();
        if (!resolved || !(resolved.value() == pending.value())) {
            return Status{
                began.code(),
                "unable to begin incarnation witness transition: " +
                    began.message()};
        }
    }
    const Status written = write_record_atomic(
        parent_descriptor, state_filename, state_path, encoded.value());
    if (!written.ok()) return written;
    auto reread = load_incarnation_state(
        parent_descriptor, state_filename, state_path, identity, sodium,
        config.lane);
    if (!reread || !(reread.value().head == next_head.value()) ||
        reread.value().bytes != encoded.value()) {
        return Status{ErrorCode::protocol_error,
                      "witnessed incarnation changed during commit verification"};
    }
    auto committed = rollback_witness::finish(pending.value());
    if (!committed) return committed.status();
    const Status finished = config.backend->compare_exchange(
        pending.value(), committed.value());
    if (!finished.ok()) {
        auto resolved = config.backend->query();
        if (!resolved || !(resolved.value() == committed.value())) {
            return Status{
                finished.code(),
                "local incarnation advanced but witness commit is unresolved: " +
                    finished.message()};
        }
    }
    const Status removed = remove_witness_intent(parent_descriptor, config);
    if (!removed.ok()) return removed;
    return reread.value();
}

Result<std::uint64_t> initial_incarnation() {
    auto random = security::random_u64_nonzero();
    if (!random) return random.status();
    const std::uint64_t value = random.value() & kInitialIncarnationMask;
    return value == 0U ? 1U : value;
}

}  // namespace

RatoxIncarnationLease::~RatoxIncarnationLease() { reset(); }

RatoxIncarnationLease::RatoxIncarnationLease(
    RatoxIncarnationLease &&other) noexcept
    : state_path_(std::move(other.state_path_)),
      incarnation_(other.incarnation_),
      lock_descriptor_(other.lock_descriptor_) {
    other.incarnation_ = 0U;
    other.lock_descriptor_ = -1;
}

RatoxIncarnationLease &RatoxIncarnationLease::operator=(
    RatoxIncarnationLease &&other) noexcept {
    if (this != &other) {
        reset();
        state_path_ = std::move(other.state_path_);
        incarnation_ = other.incarnation_;
        lock_descriptor_ = other.lock_descriptor_;
        other.incarnation_ = 0U;
        other.lock_descriptor_ = -1;
    }
    return *this;
}

void RatoxIncarnationLease::reset() noexcept {
    if (lock_descriptor_ >= 0) {
        static_cast<void>(::flock(lock_descriptor_, LOCK_UN));
        static_cast<void>(::close(lock_descriptor_));
    }
    lock_descriptor_ = -1;
    incarnation_ = 0U;
    state_path_.clear();
}

Result<RatoxIncarnationLease> RatoxIncarnationLease::acquire(
    const std::filesystem::path &state_path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    std::optional<IncarnationWitnessConfig> witness) {
    auto parent = open_private_parent(state_path);
    if (!parent) return parent.status();

    auto lock = acquire_lock(
        parent.value().descriptor.get(), parent.value().filename, state_path);
    if (!lock) return lock.status();
    ScopedDescriptor held_lock(lock.value());

    if (witness) {
        const Status valid_witness = validate_witness_config(
            *witness, state_path);
        if (!valid_witness.ok()) return valid_witness;
        auto local = load_incarnation_state(
            parent.value().descriptor.get(), parent.value().filename,
            state_path, identity, sodium, witness->lane);
        if (!local) return local.status();
        auto reconciled = reconcile_witness(
            parent.value().descriptor.get(), parent.value().filename,
            state_path, identity, sodium, *witness, local.value());
        if (!reconciled) return reconciled.status();
        auto advanced = advance_witnessed(
            parent.value().descriptor.get(), parent.value().filename,
            state_path, identity, sodium, *witness, reconciled.value());
        if (!advanced) return advanced.status();
        return RatoxIncarnationLease(
            state_path, advanced.value().incarnation,
            held_lock.release());
    }

    std::uint64_t next = 0U;
    auto existing = read_record(
        parent.value().descriptor.get(), parent.value().filename, state_path);
    if (!existing) {
        if (existing.status().code() != ErrorCode::not_found) {
            return existing.status();
        }
        auto initial = initial_incarnation();
        if (!initial) return initial.status();
        next = initial.value();
    } else {
        auto decoded = decode_record(existing.value(), identity, sodium);
        security::secure_wipe(existing.value());
        if (!decoded) return decoded.status();
        if (decoded.value() == std::numeric_limits<std::uint64_t>::max()) {
            return Status{
                ErrorCode::resource_exhausted,
                "Ratox incarnation namespace is exhausted"};
        }
        next = decoded.value() + 1U;
    }

    auto encoded = encode_record(next, identity);
    if (!encoded) return encoded.status();
    const Status committed = write_record_atomic(
        parent.value().descriptor.get(), parent.value().filename, state_path,
        encoded.value());
    security::secure_wipe(encoded.value());
    if (!committed.ok()) return committed;

    auto reread = read_record(
        parent.value().descriptor.get(), parent.value().filename, state_path);
    if (!reread) return reread.status();
    auto verified = decode_record(reread.value(), identity, sodium);
    security::secure_wipe(reread.value());
    if (!verified) return verified.status();
    if (verified.value() != next) {
        return Status{
            ErrorCode::protocol_error,
            "Ratox incarnation state changed during its commit verification"};
    }

    return RatoxIncarnationLease(
        state_path, next, held_lock.release());
}

Result<rollback_witness::Record> incarnation_witness_enrollment_record(
    const std::filesystem::path &state_path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::DomainId domain,
    std::uint64_t witness_epoch,
    rollback_witness::Lane lane) {
    if (!incarnation_lane(lane) || all_zero(domain) || witness_epoch == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "incarnation witness enrollment identity is invalid"};
    }
    auto parent = open_private_parent(state_path);
    if (!parent) return parent.status();
    auto lock = acquire_lock(
        parent.value().descriptor.get(), parent.value().filename, state_path);
    if (!lock) return lock.status();
    ScopedDescriptor held_lock(lock.value());
    auto local = load_incarnation_state(
        parent.value().descriptor.get(), parent.value().filename,
        state_path, identity, sodium, lane);
    if (!local) return local.status();
    rollback_witness::Record record;
    record.domain = domain;
    record.device = identity.public_key();
    record.witness_epoch = witness_epoch;
    record.lane = lane;
    record.committed = local.value().head;
    const Status valid = rollback_witness::validate(record);
    if (!valid.ok()) return valid;
    return record;
}

std::filesystem::path default_ratox_incarnation_state_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) return {};
    const std::filesystem::path parent = tox_savedata_path.has_parent_path()
        ? tox_savedata_path.parent_path()
        : std::filesystem::path{"."};
    return parent / "ratox" / "incarnation.state";
}

}  // namespace iotox::interactive
