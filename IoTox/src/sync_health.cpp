#include "iotox/sync_health.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <span>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic{
    'I', 'O', 'T', 'X', 'H', 'L', 'T', '1'};
constexpr std::size_t kBodyBytes = 256U;
constexpr std::size_t kRecordBytes = kBodyBytes + security::kSignatureBytes;
constexpr std::size_t kCounterOffset = 128U;
constexpr std::size_t kCounterCount = 16U;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-namespace-health-signature-v1";
constexpr std::string_view kNamespaceDomain =
    "iotox-sync-namespace-health-namespace-v1";
constexpr std::string_view kPolicyDomain =
    "iotox-sync-namespace-health-policy-v1";

class FileDescriptor {
  public:
    explicit FileDescriptor(int value) noexcept : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    [[nodiscard]] int get() const noexcept { return value_; }

  private:
    int value_{-1};
};

[[nodiscard]] Status io_status(std::string_view operation,
                               const std::filesystem::path &path,
                               int error_number = errno) {
    return Status{ErrorCode::io_error,
                  std::string(operation) + " '" + path.string() + "': " +
                      std::strerror(error_number)};
}

[[nodiscard]] Result<std::array<std::uint8_t, kRecordBytes>>
read_record(const std::filesystem::path &path) {
    int opened = -1;
    do {
        opened = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW |
                                          O_NONBLOCK);
    } while (opened < 0 && errno == EINTR);
    if (opened < 0) {
        if (errno == ENOENT)
            return Status{ErrorCode::not_found,
                          "sync health record does not exist"};
        return io_status("unable to open sync health record", path);
    }
    FileDescriptor descriptor(opened);
    struct stat before {};
    if (::fstat(descriptor.get(), &before) != 0)
        return io_status("unable to inspect sync health record", path);
    if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
        before.st_uid != ::geteuid() ||
        (before.st_mode & S_IRUSR) == 0U ||
        (before.st_mode & (S_IRWXG | S_IRWXO)) != 0U ||
        before.st_size != static_cast<off_t>(kRecordBytes)) {
        return Status{ErrorCode::protocol_error,
                      "sync health record is not one exact owner-private file"};
    }
    std::array<std::uint8_t, kRecordBytes> bytes{};
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor.get(), bytes.data() + offset,
                                     bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0)
            return io_status("unable to read sync health record", path,
                             count == 0 ? EIO : errno);
        offset += static_cast<std::size_t>(count);
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0 ||
        before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
        before.st_mode != after.st_mode ||
        before.st_nlink != after.st_nlink || before.st_uid != after.st_uid ||
        before.st_size != after.st_size ||
        before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
        before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
        before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
        before.st_ctim.tv_nsec != after.st_ctim.tv_nsec) {
        return Status{ErrorCode::io_error,
                      "sync health record changed while it was read"};
    }
    return bytes;
}

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> value) noexcept {
    return std::all_of(value.begin(), value.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

void write_u32(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint32_t value) {
    for (std::size_t index = 0U; index < 4U; ++index)
        bytes[offset + index] = static_cast<std::uint8_t>(
            value >> (24U - static_cast<unsigned>(index) * 8U));
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index)
        bytes[offset + index] = static_cast<std::uint8_t>(
            value >> (56U - static_cast<unsigned>(index) * 8U));
}

[[nodiscard]] std::uint32_t read_u32(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index)
        value = static_cast<std::uint32_t>((value << 8U) |
                                           bytes[offset + index]);
    return value;
}

[[nodiscard]] std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index)
        value = (value << 8U) | bytes[offset + index];
    return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
    std::copy(value.begin(), value.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), Size,
                value.begin());
}

[[nodiscard]] bool valid_engine(Engine engine) noexcept {
    return engine == Engine::range_v1 || engine == Engine::content_v2 ||
           engine == Engine::treepack_v1 || engine == Engine::tree_v2;
}

[[nodiscard]] Status validate_observation(
    const NamespaceHealthObservation &observation) {
    if (observation.observed_unix_ms == 0U ||
        !valid_engine(observation.engine) ||
        (observation.flags & ~kKnownNamespaceHealthFlags) != 0U ||
        all_zero(observation.namespace_commitment) ||
        all_zero(observation.policy_commitment) ||
        observation.verified_objects > observation.desired_objects ||
        observation.missing_objects !=
            observation.desired_objects - observation.verified_objects ||
        observation.verified_bytes > observation.desired_bytes ||
        observation.store_limit_bytes == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "sync health observation invariants are invalid"};
    }
    const bool coverage =
        (observation.flags & kHealthSelectedCoverageComplete) != 0U;
    if (coverage != (observation.missing_objects == 0U)) {
        return Status{ErrorCode::invalid_argument,
                      "sync health coverage flag disagrees with counters"};
    }
    if ((observation.flags & kHealthWorkspaceCurrent) != 0U &&
        (observation.flags & (kHealthWorkspacePresent |
                              kHealthWorkspaceStable)) !=
            (kHealthWorkspacePresent | kHealthWorkspaceStable)) {
        return Status{ErrorCode::invalid_argument,
                      "sync health current workspace is not stable and present"};
    }
    if ((observation.flags & kHealthWorktreeClean) != 0U &&
        (observation.flags & kHealthWorkspaceCurrent) == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "sync health clean worktree is not current"};
    }
    if ((observation.flags & kHealthAutomationStalled) != 0U &&
        (observation.flags & kHealthAutomationConfigured) == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "sync health stalled automation is not configured"};
    }
    return Status::success();
}

[[nodiscard]] Result<std::array<std::uint8_t, kBodyBytes>> encode_body(
    const NamespaceHealthRecord &record) {
    const Status valid = validate_observation(record.observation);
    if (!valid.ok() || record.sequence == 0U || all_zero(record.signer))
        return valid.ok()
            ? Status{ErrorCode::invalid_argument,
                     "sync health sequence or signer is invalid"}
            : valid;
    auto classified = classify_namespace_health(record.observation);
    if (!classified || classified.value() != record.level)
        return Status{ErrorCode::invalid_argument,
                      "sync health level is not derived canonically"};
    std::array<std::uint8_t, kBodyBytes> output{};
    std::copy(kMagic.begin(), kMagic.end(), output.begin());
    output[8U] = static_cast<std::uint8_t>(record.level);
    output[9U] = static_cast<std::uint8_t>(record.observation.engine);
    write_u32(output, 12U, record.observation.flags);
    write_u64(output, 16U, record.sequence);
    write_u64(output, 24U, record.observation.observed_unix_ms);
    write_array(output, 32U, record.observation.namespace_commitment);
    write_array(output, 64U, record.observation.policy_commitment);
    write_array(output, 96U, record.signer);
    const std::array<std::uint64_t, kCounterCount> counters{
        record.observation.frontier_writers,
        record.observation.namespace_writers,
        record.observation.subscribers,
        record.observation.writer_cutoffs,
        record.observation.conflicts,
        record.observation.desired_objects,
        record.observation.verified_objects,
        record.observation.missing_objects,
        record.observation.desired_bytes,
        record.observation.verified_bytes,
        record.observation.store_bytes,
        record.observation.store_limit_bytes,
        record.observation.source_count,
        record.observation.source_absent,
        record.observation.source_unavailable,
        record.observation.consecutive_automation_failures};
    for (std::size_t index = 0U; index < counters.size(); ++index)
        write_u64(output, kCounterOffset + index * 8U, counters[index]);
    return output;
}

[[nodiscard]] Result<NamespaceHealthRecord> decode_record(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    if (bytes.size() != kRecordBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "sync health record header or size is invalid"};
    }
    NamespaceHealthRecord record;
    record.level = static_cast<NamespaceHealthLevel>(bytes[8U]);
    record.observation.engine = static_cast<Engine>(bytes[9U]);
    if (bytes[10U] != 0U || bytes[11U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "sync health reserved bytes are not zero"};
    }
    record.observation.flags = read_u32(bytes, 12U);
    record.sequence = read_u64(bytes, 16U);
    record.observation.observed_unix_ms = read_u64(bytes, 24U);
    read_array(bytes, 32U, record.observation.namespace_commitment);
    read_array(bytes, 64U, record.observation.policy_commitment);
    read_array(bytes, 96U, record.signer);
    std::array<std::uint64_t *, kCounterCount> counters{
        &record.observation.frontier_writers,
        &record.observation.namespace_writers,
        &record.observation.subscribers,
        &record.observation.writer_cutoffs,
        &record.observation.conflicts,
        &record.observation.desired_objects,
        &record.observation.verified_objects,
        &record.observation.missing_objects,
        &record.observation.desired_bytes,
        &record.observation.verified_bytes,
        &record.observation.store_bytes,
        &record.observation.store_limit_bytes,
        &record.observation.source_count,
        &record.observation.source_absent,
        &record.observation.source_unavailable,
        &record.observation.consecutive_automation_failures};
    for (std::size_t index = 0U; index < counters.size(); ++index)
        *counters[index] = read_u64(bytes, kCounterOffset + index * 8U);
    read_array(bytes, kBodyBytes, record.signature);
    if (record.signer != expected_device || all_zero(expected_device)) {
        return Status{ErrorCode::protocol_error,
                      "sync health signer is not this device"};
    }
    auto canonical = encode_body(record);
    if (!canonical ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "sync health record is not canonical"};
    }
    auto digest = sodium.hash(kSignatureDomain, canonical.value());
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        record.signature, digest.value(), expected_device);
    return verified.ok()
        ? Result<NamespaceHealthRecord>{record}
        : Result<NamespaceHealthRecord>{Status{
              ErrorCode::protocol_error,
              "sync health record signature is invalid"}};
}

[[nodiscard]] Result<security::Digest> namespace_commitment(
    const NamespacePolicy &policy, const security::Sodium &sodium) {
    return sodium.hash(
        kNamespaceDomain,
        std::span<const std::uint8_t>{
            reinterpret_cast<const std::uint8_t *>(policy.id.data()),
            policy.id.size()});
}

[[nodiscard]] Result<security::Digest> policy_commitment(
    const NamespacePolicy &policy, const security::Sodium &sodium) {
    auto encoded = encode_namespace_policy(policy);
    return encoded ? sodium.hash(kPolicyDomain, encoded.value())
                   : Result<security::Digest>{encoded.status()};
}

} // namespace

std::string_view
namespace_health_level_name(NamespaceHealthLevel level) noexcept {
    switch (level) {
        case NamespaceHealthLevel::green:
            return "green";
        case NamespaceHealthLevel::yellow:
            return "yellow";
        case NamespaceHealthLevel::red:
            return "red";
    }
    return "unknown";
}

Result<NamespaceHealthLevel>
classify_namespace_health(const NamespaceHealthObservation &observation) {
    const Status valid = validate_observation(observation);
    if (!valid.ok()) return valid;
    constexpr std::uint32_t required =
        kHealthPolicyVerified | kHealthMembershipVerified |
        kHealthFrontierVerified | kHealthMaintenanceVerified |
        kHealthSelectedCoverageComplete;
    if ((observation.flags & required) != required ||
        observation.missing_objects != 0U ||
        ((observation.flags & kHealthWorkspacePresent) != 0U &&
         (observation.flags & kHealthWorkspaceStable) == 0U) ||
        (observation.flags & kHealthSourceExhausted) != 0U) {
        return NamespaceHealthLevel::red;
    }
    if (observation.conflicts != 0U ||
        (observation.flags & kHealthWorkspacePresent) == 0U ||
        (observation.flags & kHealthWorkspaceCurrent) == 0U ||
        (observation.flags & kHealthWorktreeClean) == 0U ||
        (observation.flags & (kHealthAutomationStalled |
                              kHealthStorePressure)) != 0U) {
        return NamespaceHealthLevel::yellow;
    }
    return NamespaceHealthLevel::green;
}

Result<NamespaceHealthObservation> bind_namespace_health_observation(
    const NamespacePolicy &policy, NamespaceHealthObservation observation,
    const security::Sodium &sodium) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    auto namespace_digest = namespace_commitment(policy, sodium);
    auto policy_digest = policy_commitment(policy, sodium);
    if (!namespace_digest || !policy_digest)
        return namespace_digest ? policy_digest.status()
                                : namespace_digest.status();
    observation.engine = policy.engine;
    observation.namespace_commitment = namespace_digest.value();
    observation.policy_commitment = policy_digest.value();
    return observation;
}

std::filesystem::path namespace_health_path(const NamespacePolicy &policy) {
    return std::filesystem::path(policy.root) / "health.state";
}

Result<NamespaceHealthRecord> load_namespace_health(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    auto bytes = read_record(namespace_health_path(policy));
    if (!bytes) return bytes.status();
    auto decoded = decode_record(bytes.value(), expected_device, sodium);
    if (!decoded) return decoded.status();
    auto expected_namespace = namespace_commitment(policy, sodium);
    if (!expected_namespace) return expected_namespace.status();
    if (decoded.value().observation.namespace_commitment !=
        expected_namespace.value()) {
        return Status{ErrorCode::protocol_error,
                      "sync health namespace commitment changed"};
    }
    return decoded;
}

Result<NamespaceHealthRecord> commit_namespace_health(
    const NamespacePolicy &policy, NamespaceHealthObservation observation,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto bound = bind_namespace_health_observation(
        policy, std::move(observation), sodium);
    if (!bound) return bound.status();
    auto level = classify_namespace_health(bound.value());
    if (!level) return level.status();
    std::uint64_t sequence = 1U;
    auto prior = load_namespace_health(policy, identity.public_key(), sodium);
    if (prior) {
        if (prior.value().sequence == std::numeric_limits<std::uint64_t>::max())
            return Status{ErrorCode::resource_exhausted,
                          "sync health sequence is exhausted"};
        sequence = prior.value().sequence + 1U;
    } else if (prior.status().code() != ErrorCode::not_found) {
        return prior.status();
    }
    NamespaceHealthRecord record;
    record.sequence = sequence;
    record.level = level.value();
    record.observation = std::move(bound).value();
    record.signer = identity.public_key();
    auto body = encode_body(record);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    record.signature = signature.value();
    std::array<std::uint8_t, kRecordBytes> encoded{};
    std::copy(body.value().begin(), body.value().end(), encoded.begin());
    std::copy(record.signature.begin(), record.signature.end(),
              encoded.begin() + static_cast<std::ptrdiff_t>(kBodyBytes));
    const Status stored =
        StateStore::write_atomic(namespace_health_path(policy), encoded);
    if (!stored.ok()) return stored;
    return record;
}

bool namespace_health_policy_current(const NamespacePolicy &policy,
                                     const NamespaceHealthRecord &record,
                                     const security::Sodium &sodium) {
    auto current = policy_commitment(policy, sodium);
    return current &&
           current.value() == record.observation.policy_commitment;
}

} // namespace iotox::sync
