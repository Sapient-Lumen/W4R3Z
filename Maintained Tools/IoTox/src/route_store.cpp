#include "iotox/route_store.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::routes {
namespace {

constexpr std::array<std::uint8_t, 8U> kGenerationMagic = {
    'I', 'O', 'T', 'O', 'X', 'R', 'G', '1'};
constexpr std::uint8_t kGenerationVersion = 1U;
constexpr std::size_t kGenerationBodyBytes = 88U;
constexpr std::size_t kGenerationStateBytes =
    kGenerationBodyBytes + security::kSignatureBytes;
constexpr std::size_t kMinimumArtifactBytes = 252U;
constexpr std::size_t kMaximumArtifactBytes = 924U;
constexpr std::string_view kGenerationSignatureDomain{
    "iotox-route-generation-state-v1"};
constexpr std::array<std::uint8_t, 8U> kWitnessIntentMagic = {
    'I', 'O', 'T', 'X', 'R', 'W', 'I', '1'};
constexpr std::size_t kWitnessIntentSignedBytes =
    184U + kGenerationStateBytes;
constexpr std::size_t kWitnessIntentBytes =
    kWitnessIntentSignedBytes + security::kSignatureBytes;

struct RouteWitnessIntent {
    rollback_witness::DomainId domain{};
    security::SigningPublicKey device{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Head current{};
    rollback_witness::Head next{};
    rollback_witness::TransactionNonce nonce{};
    std::array<std::uint8_t, kGenerationStateBytes> generation_state{};
};

Status io_status(std::string operation, const std::filesystem::path &path) {
    return Status{ErrorCode::io_error,
                  std::move(operation) + " '" + path.string() + "': " +
                      std::strerror(errno)};
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            (value >> static_cast<unsigned>(shift)) & 0xffU));
    }
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        bytes[offset + index] = static_cast<std::uint8_t>(
            value >> ((7U - index) * 8U));
    }
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path, std::size_t minimum_bytes,
    std::size_t maximum_bytes, bool absent_allowed) {
    int descriptor = -1;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (errno == ENOENT && absent_allowed) {
            return Status{ErrorCode::not_found,
                          "route state does not exist: " + path.string()};
        }
        return io_status("unable to open route state", path);
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        const Status status = io_status("unable to inspect route state", path);
        (void)::close(descriptor);
        return status;
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & 0777U) != 0600U || metadata.st_size < 0 ||
        static_cast<std::uint64_t>(metadata.st_size) < minimum_bytes ||
        static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "route state must be one owner-owned mode-0600 regular file within its exact size bounds: " +
                          path.string()};
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor, bytes.data() + offset,
                                     bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            const Status status = count == 0
                ? Status{ErrorCode::io_error,
                         "route state ended before its inspected size"}
                : io_status("unable to read route state", path);
            (void)::close(descriptor);
            return status;
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        return io_status("unable to close route state", path);
    }
    return bytes;
}

Status validate_private_parent(const std::filesystem::path &path) {
    const std::filesystem::path parent =
        path.has_parent_path() ? path.parent_path() : std::filesystem::path{"."};
    int descriptor = -1;
    do {
        descriptor = ::open(
            parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        return io_status("unable to open route-state parent directory", parent);
    }
    struct stat metadata {};
    const bool valid = ::fstat(descriptor, &metadata) == 0 &&
        S_ISDIR(metadata.st_mode) && metadata.st_uid == ::geteuid() &&
        (metadata.st_mode & 0777U) == 0700U;
    const int close_result = ::close(descriptor);
    if (!valid) {
        return Status{ErrorCode::io_error,
                      "route-state parent must be one owner-owned mode-0700 directory: " +
                          parent.string()};
    }
    if (close_result != 0) {
        return io_status("unable to close route-state parent directory", parent);
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>> encode_generation_state(
    std::uint64_t generation, const security::Digest &artifact_digest,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
    if (generation == 0U ||
        std::all_of(artifact_digest.begin(), artifact_digest.end(),
                    [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::invalid_argument,
                      "route generation state identity is invalid"};
    }
    std::vector<std::uint8_t> body;
    body.reserve(kGenerationStateBytes);
    body.insert(body.end(), kGenerationMagic.begin(), kGenerationMagic.end());
    body.push_back(kGenerationVersion);
    body.insert(body.end(), 7U, 0U);
    append_u64(body, generation);
    body.insert(body.end(), artifact_digest.begin(), artifact_digest.end());
    body.insert(body.end(), identity.public_key().begin(),
                identity.public_key().end());
    auto digest = sodium.hash(kGenerationSignatureDomain, body);
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    body.insert(body.end(), signature.value().begin(), signature.value().end());
    return body;
}

struct GenerationState {
    std::uint64_t generation{0U};
    security::Digest artifact_digest{};
};

Result<GenerationState> decode_generation_state(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_principal,
    const security::Sodium &sodium) {
    if (bytes.size() != kGenerationStateBytes ||
        !std::equal(kGenerationMagic.begin(), kGenerationMagic.end(),
                    bytes.begin()) || bytes[8U] != kGenerationVersion ||
        !std::all_of(bytes.begin() + 9U, bytes.begin() + 16U,
                     [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::protocol_error,
                      "route generation state header is invalid"};
    }
    GenerationState state;
    state.generation = read_u64(bytes, 16U);
    std::copy_n(bytes.begin() + 24U, state.artifact_digest.size(),
                state.artifact_digest.begin());
    security::SigningPublicKey principal{};
    std::copy_n(bytes.begin() + 56U, principal.size(), principal.begin());
    if (state.generation == 0U ||
        !security::constant_time_equal(principal, expected_principal)) {
        return Status{ErrorCode::protocol_error,
                      "route generation state principal or generation is invalid"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kGenerationBodyBytes),
                signature.size(), signature.begin());
    auto digest = sodium.hash(
        kGenerationSignatureDomain, bytes.first(kGenerationBodyBytes));
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        signature, digest.value(), expected_principal);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "route generation state signature is invalid"};
    }
    return state;
}

rollback_witness::Head route_head(std::uint64_t generation,
                                  const security::Digest &digest) {
    rollback_witness::Head head;
    head.position = generation;
    head.digest = digest;
    return head;
}

Result<std::array<std::uint8_t, kWitnessIntentBytes>> encode_witness_intent(
    const RouteWitnessIntent &intent,
    const security::DeviceIdentity &identity) {
    rollback_witness::Record transition;
    transition.domain = intent.domain;
    transition.device = intent.device;
    transition.witness_epoch = intent.witness_epoch;
    transition.lane = rollback_witness::Lane::route_generation;
    transition.committed = intent.current;
    transition.pending = intent.next;
    transition.nonce = intent.nonce;
    const Status valid = rollback_witness::validate(transition);
    if (!valid.ok() || intent.device != identity.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "route witness intent identity or transition is invalid"};
    }
    std::array<std::uint8_t, kWitnessIntentBytes> bytes{};
    std::copy(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
              bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = static_cast<std::uint8_t>(
        rollback_witness::Lane::route_generation);
    std::copy(intent.domain.begin(), intent.domain.end(), bytes.begin() + 16U);
    std::copy(intent.device.begin(), intent.device.end(), bytes.begin() + 32U);
    write_u64(bytes, 64U, intent.witness_epoch);
    write_u64(bytes, 72U, intent.current.position);
    std::copy(intent.current.digest.begin(), intent.current.digest.end(),
              bytes.begin() + 80U);
    write_u64(bytes, 112U, intent.next.position);
    std::copy(intent.next.digest.begin(), intent.next.digest.end(),
              bytes.begin() + 120U);
    std::copy(intent.nonce.begin(), intent.nonce.end(), bytes.begin() + 152U);
    std::copy(intent.generation_state.begin(), intent.generation_state.end(),
              bytes.begin() + 184U);
    auto signature = identity.sign(
        std::span<const std::uint8_t>{bytes}.first<kWitnessIntentSignedBytes>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + kWitnessIntentSignedBytes);
    return bytes;
}

Result<RouteWitnessIntent> decode_witness_intent(
    std::span<const std::uint8_t> bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (bytes.size() != kWitnessIntentBytes ||
        !std::equal(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
                    bytes.begin()) ||
        bytes[8U] != 1U ||
        bytes[9U] != static_cast<std::uint8_t>(
                         rollback_witness::Lane::route_generation) ||
        !all_zero(bytes.subspan(10U, 6U))) {
        return Status{ErrorCode::protocol_error,
                      "route witness intent header is invalid"};
    }
    RouteWitnessIntent intent;
    std::copy_n(bytes.begin() + 16U, intent.domain.size(),
                intent.domain.begin());
    std::copy_n(bytes.begin() + 32U, intent.device.size(),
                intent.device.begin());
    intent.witness_epoch = read_u64(bytes, 64U);
    intent.current.position = read_u64(bytes, 72U);
    std::copy_n(bytes.begin() + 80U, intent.current.digest.size(),
                intent.current.digest.begin());
    intent.next.position = read_u64(bytes, 112U);
    std::copy_n(bytes.begin() + 120U, intent.next.digest.size(),
                intent.next.digest.begin());
    std::copy_n(bytes.begin() + 152U, intent.nonce.size(),
                intent.nonce.begin());
    std::copy_n(bytes.begin() + 184U, intent.generation_state.size(),
                intent.generation_state.begin());
    rollback_witness::Record transition;
    transition.domain = intent.domain;
    transition.device = intent.device;
    transition.witness_epoch = intent.witness_epoch;
    transition.lane = rollback_witness::Lane::route_generation;
    transition.committed = intent.current;
    transition.pending = intent.next;
    transition.nonce = intent.nonce;
    const Status valid = rollback_witness::validate(transition);
    if (!valid.ok() || intent.device != identity.public_key()) {
        return Status{ErrorCode::protocol_error,
                      "route witness intent identity or transition is invalid"};
    }
    auto state = decode_generation_state(
        intent.generation_state, identity.public_key(), sodium);
    if (!state ||
        route_head(state.value().generation,
                   state.value().artifact_digest) != intent.next) {
        return Status{ErrorCode::protocol_error,
                      "route witness intent state does not match its next head"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + kWitnessIntentSignedBytes, signature.size(),
                signature.begin());
    const Status verified = sodium.verify_detached(
        signature, bytes.first(kWitnessIntentSignedBytes), intent.device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "route witness intent signature is invalid"};
    }
    return intent;
}

std::filesystem::path effective_parent(const std::filesystem::path &path) {
    return path.has_parent_path() ? path.parent_path()
                                  : std::filesystem::path{"."};
}

Status validate_witness_config(const RouteWitnessConfig &config,
                               const std::filesystem::path &state_path) {
    if (!config.backend || all_zero(config.domain) ||
        config.witness_epoch == 0U || config.intent_path.empty() ||
        effective_parent(config.intent_path) != effective_parent(state_path) ||
        config.intent_path.filename().empty() ||
        config.intent_path.filename() == state_path.filename()) {
        return Status{
            ErrorCode::invalid_argument,
            "route witness requires a backend, nonzero domain/epoch, and a distinct same-directory intent"};
    }
    const std::string filename = config.intent_path.filename().string();
    if (filename == "." || filename == ".." ||
        filename.find('\0') != std::string::npos) {
        return Status{ErrorCode::invalid_argument,
                      "route witness intent filename is unsafe"};
    }
    if (!config.backend->independently_controlled() &&
        !config.allow_non_independent_for_testing) {
        return Status{ErrorCode::invalid_argument,
                      "route rollback witness is not independently controlled"};
    }
    return Status::success();
}

bool same_witness_identity(const rollback_witness::Record &record,
                           const RouteWitnessConfig &config,
                           const security::DeviceIdentity &identity) {
    return record.domain == config.domain &&
        record.device == identity.public_key() &&
        record.witness_epoch == config.witness_epoch &&
        record.lane == rollback_witness::Lane::route_generation;
}

bool same_intent_identity(const RouteWitnessIntent &intent,
                          const RouteWitnessConfig &config,
                          const security::DeviceIdentity &identity) {
    return intent.domain == config.domain &&
        intent.device == identity.public_key() &&
        intent.witness_epoch == config.witness_epoch;
}

Result<std::optional<RouteWitnessIntent>> read_witness_intent(
    const RouteWitnessConfig &config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto bytes = read_private_file(config.intent_path, kWitnessIntentBytes,
                                   kWitnessIntentBytes, true);
    if (!bytes && bytes.status().code() == ErrorCode::not_found) {
        return std::optional<RouteWitnessIntent>{};
    }
    if (!bytes) return bytes.status();
    auto decoded = decode_witness_intent(bytes.value(), identity, sodium);
    if (!decoded) return decoded.status();
    return std::optional<RouteWitnessIntent>{decoded.value()};
}

Status remove_witness_intent(const RouteWitnessConfig &config) {
    if (::unlink(config.intent_path.c_str()) != 0 && errno != ENOENT) {
        return io_status("unable to remove route witness intent",
                         config.intent_path);
    }
    const std::filesystem::path parent = effective_parent(config.intent_path);
    const int descriptor = ::open(
        parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return io_status("unable to open route witness intent parent", parent);
    }
    const int sync_result = ::fsync(descriptor);
    const int sync_error = errno;
    const int close_result = ::close(descriptor);
    if (sync_result != 0) {
        errno = sync_error;
        return io_status("unable to synchronize route witness intent parent",
                         parent);
    }
    if (close_result != 0) {
        return io_status("unable to close route witness intent parent", parent);
    }
    return Status::success();
}

Status install_generation_state(
    const std::filesystem::path &path,
    std::span<const std::uint8_t> bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const rollback_witness::Head &expected) {
    if (bytes.size() != kGenerationStateBytes) {
        return Status{ErrorCode::invalid_argument,
                      "route generation checkpoint has the wrong exact size"};
    }
    const Status written = StateStore::write_atomic(path, bytes);
    if (!written.ok()) return written;
    auto reread = read_private_file(path, kGenerationStateBytes,
                                    kGenerationStateBytes, false);
    if (!reread) return reread.status();
    auto decoded = decode_generation_state(
        reread.value(), identity.public_key(), sodium);
    if (!decoded ||
        route_head(decoded.value().generation,
                   decoded.value().artifact_digest) != expected) {
        return Status{ErrorCode::io_error,
                      "route generation checkpoint did not verify after commit"};
    }
    return Status::success();
}

class LockedDescriptor {
  public:
    explicit LockedDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~LockedDescriptor() {
        if (descriptor_ >= 0) {
            (void)::flock(descriptor_, LOCK_UN);
            (void)::close(descriptor_);
        }
    }
    LockedDescriptor(const LockedDescriptor &) = delete;
    LockedDescriptor &operator=(const LockedDescriptor &) = delete;

  private:
    int descriptor_{-1};
};

Result<int> lock_generation_state(const std::filesystem::path &state_path) {
    const std::filesystem::path lock_path = state_path.string() + ".lock";
    int descriptor = -1;
    do {
        descriptor = ::open(lock_path.c_str(),
                            O_RDWR | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        return io_status("unable to open route generation lock", lock_path);
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0 ||
        !S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & 0777U) != 0600U) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "route generation lock is not one private owner-owned regular file"};
    }
    while (::flock(descriptor, LOCK_EX) != 0) {
        if (errno == EINTR) continue;
        const Status status =
            io_status("unable to lock route generation state", lock_path);
        (void)::close(descriptor);
        return status;
    }
    return descriptor;
}

Result<std::uint64_t> open_witnessed(
    const RouteSetStore::Config &config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const rollback_witness::Head &artifact_head,
    std::optional<GenerationState> local_state) {
    const RouteWitnessConfig &witness = *config.witness;
    const Status configured = validate_witness_config(
        witness, config.generation_state_path);
    if (!configured.ok()) return configured;

    auto observed = witness.backend->query();
    if (!observed) {
        return Status{observed.status().code(),
                      "unable to query route rollback witness: " +
                          observed.status().message()};
    }
    if (!rollback_witness::validate(observed.value()).ok() ||
        !same_witness_identity(observed.value(), witness, identity)) {
        return Status{ErrorCode::protocol_error,
                      "route rollback witness returned another or invalid lane"};
    }
    auto loaded_intent = read_witness_intent(witness, identity, sodium);
    if (!loaded_intent) return loaded_intent.status();

    const auto local_head = [&]() -> std::optional<rollback_witness::Head> {
        if (!local_state) return std::nullopt;
        return route_head(local_state->generation,
                          local_state->artifact_digest);
    };

    if (observed.value().pending) {
        if (!loaded_intent.value()) {
            return Status{ErrorCode::protocol_error,
                          "route witness is pending without its exact durable intent"};
        }
        const RouteWitnessIntent &intent = *loaded_intent.value();
        if (!same_intent_identity(intent, witness, identity) ||
            intent.current != observed.value().committed ||
            intent.next != *observed.value().pending ||
            intent.nonce != *observed.value().nonce ||
            artifact_head != intent.next) {
            return Status{ErrorCode::protocol_error,
                          "pending route witness, intent, and signed artifact do not join"};
        }
        if (local_head() && *local_head() != intent.current &&
            *local_head() != intent.next) {
            return Status{ErrorCode::protocol_error,
                          "local route checkpoint is neither exact side of the pending transition"};
        }
        const Status installed = install_generation_state(
            config.generation_state_path, intent.generation_state,
            identity, sodium, intent.next);
        if (!installed.ok()) return installed;
        local_state = decode_generation_state(
            intent.generation_state, identity.public_key(), sodium).value();
        auto committed = rollback_witness::finish(observed.value());
        if (!committed) return committed.status();
        const Status exchanged = witness.backend->compare_exchange(
            observed.value(), committed.value());
        if (!exchanged.ok()) {
            auto resolved = witness.backend->query();
            if (!resolved || !(resolved.value() == committed.value())) {
                return Status{
                    exchanged.code(),
                    "unable to commit recovered route witness transition: " +
                        exchanged.message()};
            }
        }
        observed = committed.value();
        const Status removed = remove_witness_intent(witness);
        if (!removed.ok()) return removed;
        loaded_intent.value().reset();
    } else if (loaded_intent.value()) {
        const RouteWitnessIntent &intent = *loaded_intent.value();
        if (!same_intent_identity(intent, witness, identity)) {
            return Status{ErrorCode::protocol_error,
                          "route witness intent identity does not match configuration"};
        }
        if (observed.value().committed == intent.next) {
            if (artifact_head != intent.next) {
                return Status{ErrorCode::protocol_error,
                              "committed route witness has lost its exact signed artifact"};
            }
            if (local_head() && *local_head() != intent.current &&
                *local_head() != intent.next) {
                return Status{ErrorCode::protocol_error,
                              "route checkpoint does not join the committed intent"};
            }
            const Status installed = install_generation_state(
                config.generation_state_path, intent.generation_state,
                identity, sodium, intent.next);
            if (!installed.ok()) return installed;
            local_state = decode_generation_state(
                intent.generation_state, identity.public_key(), sodium).value();
        } else if (observed.value().committed == intent.current) {
            if (local_head() && *local_head() == intent.next) {
                return Status{ErrorCode::protocol_error,
                              "local route checkpoint advanced without its external witness"};
            }
            if (artifact_head != intent.current && artifact_head != intent.next) {
                return Status{ErrorCode::protocol_error,
                              "unapplied route intent does not join the signed artifact"};
            }
        } else {
            return Status{ErrorCode::protocol_error,
                          "route witness intent does not join committed external state"};
        }
        const Status removed = remove_witness_intent(witness);
        if (!removed.ok()) return removed;
        loaded_intent.value().reset();
    }

    const rollback_witness::Head committed_head = observed.value().committed;
    if (artifact_head == committed_head) {
        // Enrollment may intentionally anchor a reviewed signed artifact that
        // has not yet been adopted into the local high-water file. The
        // independent exact head makes a missing or strictly older local
        // checkpoint repairable; the common loader has already rejected a
        // same-generation fork or any local state newer than this artifact.
        if (!local_head() || *local_head() != committed_head) {
            auto state = encode_generation_state(
                artifact_head.position, artifact_head.digest, identity, sodium);
            if (!state) return state.status();
            const Status installed = install_generation_state(
                config.generation_state_path, state.value(), identity, sodium,
                artifact_head);
            if (!installed.ok()) return installed;
        }
        return artifact_head.position;
    }
    if (committed_head.position == std::numeric_limits<std::uint64_t>::max() ||
        artifact_head.position != committed_head.position + 1U ||
        artifact_head.digest == committed_head.digest) {
        return Status{ErrorCode::protocol_error,
                      "signed route artifact is not the exact next witnessed generation"};
    }
    if (local_head() && *local_head() != committed_head) {
        return Status{ErrorCode::protocol_error,
                      "local route checkpoint is not the committed witness head before adoption"};
    }

    auto generation_state = encode_generation_state(
        artifact_head.position, artifact_head.digest, identity, sodium);
    if (!generation_state) return generation_state.status();
    rollback_witness::TransactionNonce nonce{};
    const Status random = security::fill_random(nonce);
    if (!random.ok()) return random;
    auto pending = rollback_witness::begin(
        observed.value(), artifact_head, nonce);
    if (!pending) return pending.status();
    RouteWitnessIntent intent;
    intent.domain = witness.domain;
    intent.device = identity.public_key();
    intent.witness_epoch = witness.witness_epoch;
    intent.current = committed_head;
    intent.next = artifact_head;
    intent.nonce = nonce;
    std::copy(generation_state.value().begin(), generation_state.value().end(),
              intent.generation_state.begin());
    auto encoded_intent = encode_witness_intent(intent, identity);
    if (!encoded_intent) return encoded_intent.status();
    const Status intent_written = StateStore::write_atomic(
        witness.intent_path, encoded_intent.value());
    if (!intent_written.ok()) return intent_written;

    const Status began = witness.backend->compare_exchange(
        observed.value(), pending.value());
    if (!began.ok()) {
        auto resolved = witness.backend->query();
        if (!resolved || !(resolved.value() == pending.value())) {
            return Status{began.code(),
                          "unable to begin route witness transition: " +
                              began.message()};
        }
    }
    const Status installed = install_generation_state(
        config.generation_state_path, generation_state.value(), identity,
        sodium, artifact_head);
    if (!installed.ok()) return installed;
    auto committed = rollback_witness::finish(pending.value());
    if (!committed) return committed.status();
    const Status finished = witness.backend->compare_exchange(
        pending.value(), committed.value());
    if (!finished.ok()) {
        auto resolved = witness.backend->query();
        if (!resolved || !(resolved.value() == committed.value())) {
            return Status{finished.code(),
                          "local route generation advanced but witness commit is unresolved: " +
                              finished.message()};
        }
    }
    const Status removed = remove_witness_intent(witness);
    if (!removed.ok()) return removed;
    return artifact_head.position;
}

}  // namespace

Result<StoredRouteSet> RouteSetStore::open(
    Config config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (config.artifact_path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "route-set artifact path is empty"};
    }
    if (config.generation_state_path.empty()) {
        config.generation_state_path =
            default_route_generation_state_path(config.artifact_path);
    }
    if (config.artifact_path == config.generation_state_path) {
        return Status{ErrorCode::invalid_argument,
                      "route artifact and generation state paths must differ"};
    }
    const Status artifact_parent =
        validate_private_parent(config.artifact_path);
    if (!artifact_parent.ok()) return artifact_parent;
    const Status generation_parent =
        validate_private_parent(config.generation_state_path);
    if (!generation_parent.ok()) return generation_parent;
    auto locked = lock_generation_state(config.generation_state_path);
    if (!locked) return locked.status();
    LockedDescriptor lock(locked.value());

    auto artifact = read_private_file(config.artifact_path,
                                      kMinimumArtifactBytes,
                                      kMaximumArtifactBytes, false);
    if (!artifact) return artifact.status();
    auto route_set = verify_route_set(
        artifact.value(), identity.public_key(), 1U, sodium);
    if (!route_set) return route_set.status();
    auto artifact_digest = route_set_artifact_digest(
        artifact.value(), sodium);
    if (!artifact_digest) return artifact_digest.status();

    std::uint64_t high_water = 0U;
    std::optional<GenerationState> local_state;
    auto stored_bytes = read_private_file(
        config.generation_state_path, kGenerationStateBytes,
        kGenerationStateBytes, true);
    if (stored_bytes) {
        auto stored = decode_generation_state(
            stored_bytes.value(), identity.public_key(), sodium);
        if (!stored) return stored.status();
        local_state = stored.value();
        high_water = stored.value().generation;
        if (route_set.value().generation < high_water) {
            return Status{ErrorCode::protocol_error,
                          "route-set artifact generation is below its durable high-water mark"};
        }
        if (route_set.value().generation == high_water &&
            !security::constant_time_equal(
                artifact_digest.value(), stored.value().artifact_digest)) {
            return Status{ErrorCode::protocol_error,
                          "route-set artifact forks its durable generation"};
        }
    } else if (stored_bytes.status().code() != ErrorCode::not_found) {
        return stored_bytes.status();
    }

    if (config.witness) {
        auto witnessed = open_witnessed(
            config, identity, sodium,
            route_head(route_set.value().generation, artifact_digest.value()),
            local_state);
        if (!witnessed) return witnessed.status();
        high_water = witnessed.value();
    } else if (route_set.value().generation > high_water) {
        auto state = encode_generation_state(
            route_set.value().generation, artifact_digest.value(), identity,
            sodium);
        if (!state) return state.status();
        const Status written =
            StateStore::write_atomic(config.generation_state_path, state.value());
        if (!written.ok()) return written;
        auto confirmed_bytes = read_private_file(
            config.generation_state_path, kGenerationStateBytes,
            kGenerationStateBytes, false);
        if (!confirmed_bytes) return confirmed_bytes.status();
        auto confirmed = decode_generation_state(
            confirmed_bytes.value(), identity.public_key(), sodium);
        if (!confirmed || confirmed.value().generation !=
                              route_set.value().generation ||
            !security::constant_time_equal(
                confirmed.value().artifact_digest, artifact_digest.value())) {
            return Status{ErrorCode::io_error,
                          "route generation checkpoint did not verify after commit"};
        }
        high_water = route_set.value().generation;
    }

    return StoredRouteSet{
        std::move(route_set).value(), artifact_digest.value(), high_water};
}

Result<StoredRouteSet> RouteSetStore::inspect(
    Config config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (config.artifact_path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "route-set artifact path is empty"};
    }
    if (config.generation_state_path.empty()) {
        config.generation_state_path =
            default_route_generation_state_path(config.artifact_path);
    }
    if (config.artifact_path == config.generation_state_path) {
        return Status{ErrorCode::invalid_argument,
                      "route artifact and generation state paths must differ"};
    }
    const Status artifact_parent =
        validate_private_parent(config.artifact_path);
    if (!artifact_parent.ok()) return artifact_parent;
    const Status generation_parent =
        validate_private_parent(config.generation_state_path);
    if (!generation_parent.ok()) return generation_parent;

    auto artifact = read_private_file(config.artifact_path,
                                      kMinimumArtifactBytes,
                                      kMaximumArtifactBytes, false);
    if (!artifact) return artifact.status();
    auto route_set = verify_route_set(
        artifact.value(), identity.public_key(), 1U, sodium);
    if (!route_set) return route_set.status();
    auto artifact_digest = route_set_artifact_digest(
        artifact.value(), sodium);
    if (!artifact_digest) return artifact_digest.status();

    std::uint64_t high_water = 0U;
    auto generation_bytes = read_private_file(
        config.generation_state_path, kGenerationStateBytes,
        kGenerationStateBytes, true);
    if (generation_bytes) {
        auto generation = decode_generation_state(
            generation_bytes.value(), identity.public_key(), sodium);
        if (!generation) return generation.status();
        high_water = generation.value().generation;
        if (route_set.value().generation < high_water ||
            (route_set.value().generation == high_water &&
             !security::constant_time_equal(
                 generation.value().artifact_digest,
                 artifact_digest.value()))) {
            return Status{ErrorCode::protocol_error,
                          "route artifact is older than or conflicts with its generation high-water state"};
        }
    } else if (generation_bytes.status().code() != ErrorCode::not_found) {
        return generation_bytes.status();
    }

    StoredRouteSet stored;
    stored.route_set = std::move(route_set).value();
    stored.artifact_digest = artifact_digest.value();
    stored.generation_high_water = high_water;
    return stored;
}

Result<rollback_witness::Record> RouteSetStore::witness_enrollment(
    Config config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::DomainId domain, std::uint64_t witness_epoch) {
    config.witness.reset();
    auto inspected = inspect(std::move(config), identity, sodium);
    if (!inspected) return inspected.status();
    rollback_witness::Record record;
    record.domain = domain;
    record.device = identity.public_key();
    record.witness_epoch = witness_epoch;
    record.lane = rollback_witness::Lane::route_generation;
    record.committed = route_head(
        inspected.value().route_set.generation,
        inspected.value().artifact_digest);
    const Status valid = rollback_witness::validate(record);
    if (!valid.ok()) return valid;
    return record;
}

std::filesystem::path default_route_generation_state_path(
    const std::filesystem::path &artifact_path) {
    if (artifact_path.empty()) return {};
    return artifact_path.string() + ".generation";
}

}  // namespace iotox::routes
