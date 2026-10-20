#include "iotox/policy_witness.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <optional>
#include <span>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace iotox::policy_witness {
namespace {

constexpr std::array<std::uint8_t, 8U> kCheckpointMagic = {
    'I', 'O', 'T', 'X', 'P', 'C', 'P', '1'};
constexpr std::uint8_t kCheckpointVersion = 1U;
constexpr std::size_t kCheckpointSignedBytes = 88U;
constexpr std::size_t kCheckpointBytes =
    kCheckpointSignedBytes + security::kSignatureBytes;
constexpr std::string_view kCheckpointSignatureDomain{
    "iotox-policy-witness-checkpoint-v1"};

constexpr std::array<std::uint8_t, 8U> kIntentMagic = {
    'I', 'O', 'T', 'X', 'P', 'W', 'I', '1'};
constexpr std::uint8_t kIntentVersion = 1U;
constexpr std::size_t kIntentSignedBytes = 184U + kCheckpointBytes;
constexpr std::size_t kIntentBytes =
    kIntentSignedBytes + security::kSignatureBytes;
constexpr std::string_view kIntentSignatureDomain{
    "iotox-policy-witness-intent-v1"};

struct Intent {
    rollback_witness::DomainId domain{};
    security::SigningPublicKey device{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Lane lane{rollback_witness::Lane::terminal_policy};
    rollback_witness::Head current{};
    rollback_witness::Head next{};
    rollback_witness::TransactionNonce nonce{};
    std::array<std::uint8_t, kCheckpointBytes> checkpoint{};
};

struct Reconciled {
    rollback_witness::Record external;
    std::optional<Checkpoint> local;
};

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] Status io_status(std::string operation,
                               const std::filesystem::path &path) {
    return Status{ErrorCode::io_error,
                  std::move(operation) + " '" + path.string() + "': " +
                      std::strerror(errno)};
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        bytes[offset + index] = static_cast<std::uint8_t>(
            value >> ((7U - index) * 8U));
    }
}

[[nodiscard]] std::uint64_t read_u64(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_private_exact(
    const std::filesystem::path &path, std::size_t expected,
    bool absence_allowed, std::string_view label) {
    int descriptor = -1;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (absence_allowed && errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          std::string(label) + " does not exist"};
        }
        return io_status("unable to open " + std::string(label), path);
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        const Status result =
            io_status("unable to inspect " + std::string(label), path);
        static_cast<void>(::close(descriptor));
        return result;
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0777)) != 0600 ||
        metadata.st_size < 0 ||
        static_cast<std::uint64_t>(metadata.st_size) != expected) {
        static_cast<void>(::close(descriptor));
        return Status{
            ErrorCode::io_error,
            std::string(label) +
                " must be one owner-owned mode-0600 regular file of the exact canonical size"};
    }
    std::vector<std::uint8_t> bytes(expected);
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            const Status result = count == 0
                ? Status{ErrorCode::io_error,
                         std::string(label) +
                             " ended before its inspected size"}
                : io_status("unable to read " + std::string(label), path);
            static_cast<void>(::close(descriptor));
            return result;
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        return io_status("unable to close " + std::string(label), path);
    }
    return bytes;
}

[[nodiscard]] Status validate_private_parent(
    const std::filesystem::path &path) {
    const std::filesystem::path parent = path.parent_path();
    if (parent.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "policy witness state requires an absolute parent"};
    }
    int descriptor = -1;
    do {
        descriptor = ::open(
            parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        return io_status("unable to open policy witness parent", parent);
    }
    struct stat metadata {};
    const bool valid = ::fstat(descriptor, &metadata) == 0 &&
        S_ISDIR(metadata.st_mode) && metadata.st_uid == ::geteuid() &&
        (metadata.st_mode & static_cast<mode_t>(0777)) == 0700;
    const int close_result = ::close(descriptor);
    if (!valid) {
        return Status{
            ErrorCode::io_error,
            "policy witness parent must be one owner-owned mode-0700 directory: " +
                parent.string()};
    }
    if (close_result != 0) {
        return io_status("unable to close policy witness parent", parent);
    }
    return Status::success();
}

[[nodiscard]] Result<std::array<std::uint8_t, kCheckpointBytes>>
encode_checkpoint(rollback_witness::Lane lane,
                  const rollback_witness::Head &head,
                  const security::DeviceIdentity &identity,
                  const security::Sodium &sodium) {
    rollback_witness::Record validation;
    validation.domain[0U] = 1U;
    validation.device = identity.public_key();
    validation.witness_epoch = 1U;
    validation.lane = lane;
    validation.committed = head;
    if (!rollback_witness::validate(validation).ok() ||
        head.position == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "policy witness checkpoint head or lane is invalid"};
    }
    std::array<std::uint8_t, kCheckpointBytes> bytes{};
    std::copy(kCheckpointMagic.begin(), kCheckpointMagic.end(), bytes.begin());
    bytes[8U] = kCheckpointVersion;
    bytes[9U] = static_cast<std::uint8_t>(lane);
    write_u64(bytes, 16U, head.position);
    std::copy(head.digest.begin(), head.digest.end(), bytes.begin() + 24U);
    std::copy(identity.public_key().begin(), identity.public_key().end(),
              bytes.begin() + 56U);
    auto digest = sodium.hash(
        kCheckpointSignatureDomain,
        std::span<const std::uint8_t>{bytes}.first<kCheckpointSignedBytes>());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + kCheckpointSignedBytes);
    return bytes;
}

[[nodiscard]] Result<Checkpoint> decode_checkpoint(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &device,
    const security::Sodium &sodium) {
    if (bytes.size() != kCheckpointBytes ||
        !std::equal(kCheckpointMagic.begin(), kCheckpointMagic.end(),
                    bytes.begin()) ||
        bytes[8U] != kCheckpointVersion ||
        !std::all_of(bytes.begin() + 10U, bytes.begin() + 16U,
                     [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::protocol_error,
                      "policy witness checkpoint header is invalid"};
    }
    Checkpoint result;
    result.lane = static_cast<rollback_witness::Lane>(bytes[9U]);
    result.head.position = read_u64(bytes, 16U);
    std::copy_n(bytes.begin() + 24U, result.head.digest.size(),
                result.head.digest.begin());
    security::SigningPublicKey encoded_device{};
    std::copy_n(bytes.begin() + 56U, encoded_device.size(),
                encoded_device.begin());
    rollback_witness::Record validation;
    validation.domain[0U] = 1U;
    validation.device = encoded_device;
    validation.witness_epoch = 1U;
    validation.lane = result.lane;
    validation.committed = result.head;
    if (!security::constant_time_equal(device, encoded_device) ||
        !rollback_witness::validate(validation).ok() ||
        result.head.position == 0U) {
        return Status{ErrorCode::protocol_error,
                      "policy witness checkpoint identity or head is invalid"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + kCheckpointSignedBytes, signature.size(),
                signature.begin());
    auto digest = sodium.hash(
        kCheckpointSignatureDomain,
        bytes.first(kCheckpointSignedBytes));
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        signature, digest.value(), device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "policy witness checkpoint signature is invalid"};
    }
    return result;
}

[[nodiscard]] Result<std::array<std::uint8_t, kIntentBytes>> encode_intent(
    const Intent &intent, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    rollback_witness::Record current;
    current.domain = intent.domain;
    current.device = intent.device;
    current.witness_epoch = intent.witness_epoch;
    current.lane = intent.lane;
    current.committed = intent.current;
    auto pending = rollback_witness::begin(current, intent.next, intent.nonce);
    auto checkpoint = decode_checkpoint(
        intent.checkpoint, identity.public_key(), sodium);
    if (!pending || !checkpoint || checkpoint.value().lane != intent.lane ||
        checkpoint.value().head != intent.next ||
        !security::constant_time_equal(intent.device, identity.public_key())) {
        return Status{ErrorCode::invalid_argument,
                      "policy witness intent identity or transition is invalid"};
    }
    std::array<std::uint8_t, kIntentBytes> bytes{};
    std::copy(kIntentMagic.begin(), kIntentMagic.end(), bytes.begin());
    bytes[8U] = kIntentVersion;
    bytes[9U] = static_cast<std::uint8_t>(intent.lane);
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
    std::copy(intent.checkpoint.begin(), intent.checkpoint.end(),
              bytes.begin() + 184U);
    auto digest = sodium.hash(
        kIntentSignatureDomain,
        std::span<const std::uint8_t>{bytes}.first<kIntentSignedBytes>());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + kIntentSignedBytes);
    return bytes;
}

[[nodiscard]] Result<Intent> decode_intent(
    std::span<const std::uint8_t> bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (bytes.size() != kIntentBytes ||
        !std::equal(kIntentMagic.begin(), kIntentMagic.end(), bytes.begin()) ||
        bytes[8U] != kIntentVersion ||
        !std::all_of(bytes.begin() + 10U, bytes.begin() + 16U,
                     [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::protocol_error,
                      "policy witness intent header is invalid"};
    }
    Intent intent;
    intent.lane = static_cast<rollback_witness::Lane>(bytes[9U]);
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
    std::copy_n(bytes.begin() + 152U, intent.nonce.size(), intent.nonce.begin());
    std::copy_n(bytes.begin() + 184U, intent.checkpoint.size(),
                intent.checkpoint.begin());
    rollback_witness::Record current;
    current.domain = intent.domain;
    current.device = intent.device;
    current.witness_epoch = intent.witness_epoch;
    current.lane = intent.lane;
    current.committed = intent.current;
    auto pending = rollback_witness::begin(current, intent.next, intent.nonce);
    auto checkpoint = decode_checkpoint(
        intent.checkpoint, identity.public_key(), sodium);
    if (!pending || !checkpoint || checkpoint.value().lane != intent.lane ||
        checkpoint.value().head != intent.next ||
        !security::constant_time_equal(intent.device,
                                      identity.public_key())) {
        return Status{ErrorCode::protocol_error,
                      "policy witness intent identity or transition is invalid"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + kIntentSignedBytes, signature.size(),
                signature.begin());
    auto digest = sodium.hash(
        kIntentSignatureDomain, bytes.first(kIntentSignedBytes));
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        signature, digest.value(), identity.public_key());
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "policy witness intent signature is invalid"};
    }
    return intent;
}

[[nodiscard]] Status validate_config(const Config &config) {
    rollback_witness::Record selector;
    selector.domain = config.domain;
    selector.device[0U] = 1U;
    selector.witness_epoch = config.witness_epoch;
    selector.lane = config.lane;
    if (!config.backend || config.checkpoint_path.empty() ||
        config.intent_path.empty() ||
        config.checkpoint_path == config.intent_path ||
        config.checkpoint_path.parent_path() !=
            config.intent_path.parent_path() ||
        !rollback_witness::validate(selector).ok()) {
        return Status{
            ErrorCode::invalid_argument,
            "policy witness requires a valid backend/selector and distinct same-directory checkpoint and intent"};
    }
    if (config.checkpoint_path.filename().empty() ||
        config.intent_path.filename().empty() ||
        config.checkpoint_path.filename() == "." ||
        config.checkpoint_path.filename() == ".." ||
        config.intent_path.filename() == "." ||
        config.intent_path.filename() == "..") {
        return Status{ErrorCode::invalid_argument,
                      "policy witness state filename is unsafe"};
    }
    const Status parent = validate_private_parent(config.checkpoint_path);
    if (!parent.ok()) return parent;
    if (!config.backend->independently_controlled() &&
        !config.allow_non_independent_for_testing) {
        return Status{ErrorCode::unsupported,
                      "policy witness backend shares the local failure domain"};
    }
    return Status::success();
}

[[nodiscard]] bool same_selector(
    const rollback_witness::Record &record, const Config &config,
    const security::DeviceIdentity &identity) {
    return record.domain == config.domain &&
        security::constant_time_equal(record.device, identity.public_key()) &&
        record.witness_epoch == config.witness_epoch &&
        record.lane == config.lane;
}

[[nodiscard]] bool same_selector(
    const Intent &intent, const Config &config,
    const security::DeviceIdentity &identity) {
    return intent.domain == config.domain &&
        security::constant_time_equal(intent.device, identity.public_key()) &&
        intent.witness_epoch == config.witness_epoch &&
        intent.lane == config.lane;
}

[[nodiscard]] Result<std::optional<Checkpoint>> load_checkpoint(
    const Config &config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto bytes = read_private_exact(
        config.checkpoint_path, kCheckpointBytes, true,
        "policy witness checkpoint");
    if (!bytes && bytes.status().code() == ErrorCode::not_found) {
        return std::optional<Checkpoint>{};
    }
    if (!bytes) return bytes.status();
    auto decoded = decode_checkpoint(
        bytes.value(), identity.public_key(), sodium);
    if (!decoded) return decoded.status();
    if (decoded.value().lane != config.lane) {
        return Status{ErrorCode::protocol_error,
                      "policy witness checkpoint belongs to another lane"};
    }
    return std::optional<Checkpoint>{decoded.value()};
}

[[nodiscard]] Result<std::optional<Intent>> load_intent(
    const Config &config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto bytes = read_private_exact(
        config.intent_path, kIntentBytes, true, "policy witness intent");
    if (!bytes && bytes.status().code() == ErrorCode::not_found) {
        return std::optional<Intent>{};
    }
    if (!bytes) return bytes.status();
    auto decoded = decode_intent(bytes.value(), identity, sodium);
    if (!decoded) return decoded.status();
    return std::optional<Intent>{decoded.value()};
}

[[nodiscard]] Status install_checkpoint(
    const Config &config,
    std::span<const std::uint8_t, kCheckpointBytes> bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const rollback_witness::Head &expected) {
    auto decoded = decode_checkpoint(bytes, identity.public_key(), sodium);
    if (!decoded || decoded.value().lane != config.lane ||
        decoded.value().head != expected) {
        return Status{ErrorCode::protocol_error,
                      "policy witness checkpoint does not encode its declared head"};
    }
    const Status written = StateStore::write_atomic(
        config.checkpoint_path, bytes);
    if (!written.ok()) return written;
    auto reread = inspect_checkpoint(
        config.checkpoint_path, identity.public_key(), sodium);
    if (!reread || reread.value().lane != config.lane ||
        reread.value().head != expected) {
        return Status{ErrorCode::io_error,
                      "policy witness checkpoint did not verify after commit"};
    }
    return Status::success();
}

[[nodiscard]] Status remove_intent(const Config &config) {
    if (::unlink(config.intent_path.c_str()) != 0) {
        if (errno == ENOENT) return Status::success();
        return io_status("unable to remove policy witness intent",
                         config.intent_path);
    }
    const std::filesystem::path parent = config.intent_path.parent_path();
    int descriptor = -1;
    do {
        descriptor = ::open(
            parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        return io_status("unable to open policy witness intent parent", parent);
    }
    const int synced = ::fsync(descriptor);
    const int closed = ::close(descriptor);
    if (synced != 0 || closed != 0) {
        return io_status("unable to synchronize policy witness intent parent",
                         parent);
    }
    return Status::success();
}

[[nodiscard]] Status resolve_cas(
    const Config &config, const rollback_witness::Record &expected,
    const rollback_witness::Record &desired, std::string_view label) {
    const Status exchanged = config.backend->compare_exchange(expected, desired);
    if (exchanged.ok()) return exchanged;
    auto observed = config.backend->query();
    if (observed && observed.value() == desired) return Status::success();
    return Status{exchanged.code(), std::string(label) + ": " +
                                         exchanged.message()};
}

[[nodiscard]] Result<Reconciled> reconcile(
    const Config &config, const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    const Status configured = validate_config(config);
    if (!configured.ok()) return configured;
    if (all_zero(policy_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "policy witness cannot bind a zero digest"};
    }
    auto external = config.backend->query();
    if (!external) {
        return Status{external.status().code(),
                      "unable to query policy rollback witness: " +
                          external.status().message()};
    }
    if (!rollback_witness::validate(external.value()).ok() ||
        !same_selector(external.value(), config, identity)) {
        return Status{ErrorCode::protocol_error,
                      "policy rollback witness returned another or invalid lane"};
    }
    auto local = load_checkpoint(config, identity, sodium);
    if (!local) return local.status();
    auto intent = load_intent(config, identity, sodium);
    if (!intent) return intent.status();

    const auto local_head = [&]() -> std::optional<rollback_witness::Head> {
        if (!local.value()) return std::nullopt;
        return local.value()->head;
    };

    if (external.value().pending) {
        if (!intent.value()) {
            return Status{ErrorCode::protocol_error,
                          "policy witness is pending without its exact durable intent"};
        }
        const Intent &transaction = *intent.value();
        if (!same_selector(transaction, config, identity) ||
            transaction.current != external.value().committed ||
            transaction.next != *external.value().pending ||
            transaction.nonce != *external.value().nonce ||
            policy_digest != transaction.next.digest) {
            return Status{ErrorCode::protocol_error,
                          "pending policy witness, intent, and reviewed policy do not join"};
        }
        if (local_head() && *local_head() != transaction.current &&
            *local_head() != transaction.next) {
            return Status{ErrorCode::protocol_error,
                          "local policy checkpoint is neither exact side of the pending transition"};
        }
        const Status installed = install_checkpoint(
            config, transaction.checkpoint, identity, sodium,
            transaction.next);
        if (!installed.ok()) return installed;
        local.value() = Checkpoint{config.lane, transaction.next};
        auto committed = rollback_witness::finish(external.value());
        if (!committed) return committed.status();
        const Status finished = resolve_cas(
            config, external.value(), committed.value(),
            "unable to commit recovered policy witness transition");
        if (!finished.ok()) return finished;
        external = committed.value();
        const Status removed = remove_intent(config);
        if (!removed.ok()) return removed;
        intent.value().reset();
    } else if (intent.value()) {
        const Intent &transaction = *intent.value();
        if (!same_selector(transaction, config, identity)) {
            return Status{ErrorCode::protocol_error,
                          "policy witness intent identity does not match configuration"};
        }
        if (external.value().committed == transaction.next) {
            if (policy_digest != transaction.next.digest ||
                (local_head() && *local_head() != transaction.current &&
                 *local_head() != transaction.next)) {
                return Status{ErrorCode::protocol_error,
                              "committed policy witness does not join its retained intent and reviewed policy"};
            }
            const Status installed = install_checkpoint(
                config, transaction.checkpoint, identity, sodium,
                transaction.next);
            if (!installed.ok()) return installed;
            local.value() = Checkpoint{config.lane, transaction.next};
            const Status removed = remove_intent(config);
            if (!removed.ok()) return removed;
            intent.value().reset();
        } else if (external.value().committed == transaction.current) {
            if (local_head() && *local_head() == transaction.next) {
                return Status{ErrorCode::protocol_error,
                              "local policy checkpoint advanced without its external witness"};
            }
            if (policy_digest == transaction.current.digest) {
                const Status removed = remove_intent(config);
                if (!removed.ok()) return removed;
                intent.value().reset();
            } else if (policy_digest == transaction.next.digest) {
                rollback_witness::Record pending = external.value();
                pending.pending = transaction.next;
                pending.nonce = transaction.nonce;
                const Status began = resolve_cas(
                    config, external.value(), pending,
                    "unable to resume prepared policy witness transition");
                if (!began.ok()) return began;
                const Status installed = install_checkpoint(
                    config, transaction.checkpoint, identity, sodium,
                    transaction.next);
                if (!installed.ok()) return installed;
                local.value() = Checkpoint{config.lane, transaction.next};
                auto committed = rollback_witness::finish(pending);
                if (!committed) return committed.status();
                const Status finished = resolve_cas(
                    config, pending, committed.value(),
                    "unable to commit resumed policy witness transition");
                if (!finished.ok()) return finished;
                external = committed.value();
                const Status removed = remove_intent(config);
                if (!removed.ok()) return removed;
                intent.value().reset();
            } else {
                return Status{ErrorCode::protocol_error,
                              "prepared policy intent does not join current reviewed policy"};
            }
        } else {
            return Status{ErrorCode::protocol_error,
                          "policy witness intent does not join committed external state"};
        }
    }

    const rollback_witness::Head committed = external.value().committed;
    if (local.value()) {
        const rollback_witness::Head head = local.value()->head;
        if (head.position > committed.position ||
            (head.position == committed.position && head != committed)) {
            return Status{ErrorCode::protocol_error,
                          "local policy checkpoint conflicts with the committed witness head"};
        }
    }
    return Reconciled{external.value(), local.value()};
}

[[nodiscard]] Result<std::uint64_t> reconcile_or_commit(
    const Config &config, const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, bool allow_new_transition) {
    auto state = reconcile(config, policy_digest, identity, sodium);
    if (!state) return state.status();
    const rollback_witness::Head current = state.value().external.committed;
    if (policy_digest == current.digest) {
        if (!state.value().local || state.value().local->head != current) {
            auto encoded = encode_checkpoint(
                config.lane, current, identity, sodium);
            if (!encoded) return encoded.status();
            const Status installed = install_checkpoint(
                config, encoded.value(), identity, sodium, current);
            if (!installed.ok()) return installed;
        }
        return current.position;
    }
    if (!allow_new_transition) {
        return Status{ErrorCode::protocol_error,
                      "reviewed policy digest is not the externally committed head"};
    }
    if (current.position == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "policy witness position is exhausted"};
    }
    if (state.value().local &&
        state.value().local->head.position == current.position &&
        state.value().local->head != current) {
        return Status{ErrorCode::protocol_error,
                      "local policy checkpoint forks the committed witness head"};
    }

    const rollback_witness::Head next{current.position + 1U, policy_digest};
    auto checkpoint = encode_checkpoint(config.lane, next, identity, sodium);
    if (!checkpoint) return checkpoint.status();
    rollback_witness::TransactionNonce nonce{};
    const Status random = security::fill_random(nonce);
    if (!random.ok()) return random;
    auto pending = rollback_witness::begin(
        state.value().external, next, nonce);
    if (!pending) return pending.status();
    Intent intent;
    intent.domain = config.domain;
    intent.device = identity.public_key();
    intent.witness_epoch = config.witness_epoch;
    intent.lane = config.lane;
    intent.current = current;
    intent.next = next;
    intent.nonce = nonce;
    intent.checkpoint = checkpoint.value();
    auto encoded_intent = encode_intent(intent, identity, sodium);
    if (!encoded_intent) return encoded_intent.status();
    const Status written = StateStore::write_atomic(
        config.intent_path, encoded_intent.value());
    if (!written.ok()) return written;
    const Status began = resolve_cas(
        config, state.value().external, pending.value(),
        "unable to begin policy witness transition");
    if (!began.ok()) return began;
    const Status installed = install_checkpoint(
        config, checkpoint.value(), identity, sodium, next);
    if (!installed.ok()) return installed;
    auto committed = rollback_witness::finish(pending.value());
    if (!committed) return committed.status();
    const Status finished = resolve_cas(
        config, pending.value(), committed.value(),
        "local policy checkpoint advanced but witness commit is unresolved");
    if (!finished.ok()) return finished;
    const Status removed = remove_intent(config);
    if (!removed.ok()) return removed;
    return next.position;
}

}  // namespace

Result<Checkpoint> inspect_checkpoint(
    const std::filesystem::path &path,
    const security::SigningPublicKey &device,
    const security::Sodium &sodium) {
    auto bytes = read_private_exact(
        path, kCheckpointBytes, true, "policy witness checkpoint");
    if (!bytes) return bytes.status();
    return decode_checkpoint(bytes.value(), device, sodium);
}

Result<rollback_witness::Record> enrollment_record(
    const std::filesystem::path &checkpoint_path,
    const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::DomainId domain,
    std::uint64_t witness_epoch,
    rollback_witness::Lane lane) {
    if (all_zero(policy_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "policy witness enrollment digest is zero"};
    }
    std::uint64_t position = 1U;
    auto existing = inspect_checkpoint(
        checkpoint_path, identity.public_key(), sodium);
    if (existing) {
        if (existing.value().lane != lane ||
            existing.value().head.digest != policy_digest) {
            return Status{ErrorCode::protocol_error,
                          "existing policy checkpoint does not describe the reviewed enrollment policy"};
        }
        position = existing.value().head.position;
    } else if (existing.status().code() != ErrorCode::not_found) {
        return existing.status();
    }
    rollback_witness::Record record;
    record.domain = domain;
    record.device = identity.public_key();
    record.witness_epoch = witness_epoch;
    record.lane = lane;
    record.committed = rollback_witness::Head{position, policy_digest};
    const Status valid = rollback_witness::validate(record);
    if (!valid.ok()) return valid;
    return record;
}

Result<std::uint64_t> verify(
    const Config &config, const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    return reconcile_or_commit(
        config, policy_digest, identity, sodium, false);
}

Result<std::uint64_t> commit(
    const Config &config, const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    return reconcile_or_commit(
        config, policy_digest, identity, sodium, true);
}

}  // namespace iotox::policy_witness
