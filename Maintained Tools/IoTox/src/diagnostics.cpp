#include "iotox/diagnostics.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::diagnostics {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic{
    'I', 'O', 'T', 'X', 'D', 'G', 'N', '1'};
constexpr std::size_t kHeaderBytes = 36U;
constexpr std::size_t kRecordBytes = 128U;
constexpr std::string_view kStoreDomain = "diagnostics-flight-v1";
constexpr std::string_view kBundleDomain = "diagnostics-bundle-v1";

class FileDescriptor {
  public:
    explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~FileDescriptor() {
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    [[nodiscard]] int get() const noexcept { return descriptor_; }

  private:
    int descriptor_{-1};
};

[[nodiscard]] Status io_status(std::string_view operation,
                               const std::filesystem::path &path,
                               int error_number = errno) {
    return Status{ErrorCode::io_error,
                  std::string(operation) + " '" + path.string() + "': " +
                      std::strerror(error_number)};
}

void append_u16(std::vector<std::uint8_t> &output, std::uint16_t value) {
    output.push_back(static_cast<std::uint8_t>(value >> 8U));
    output.push_back(static_cast<std::uint8_t>(value));
}

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
    for (int shift = 24; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            value >> static_cast<unsigned>(shift)));
    }
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            value >> static_cast<unsigned>(shift)));
    }
}

[[nodiscard]] std::uint16_t read_u16(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        bytes[offset + 1U]);
}

[[nodiscard]] std::uint32_t read_u32(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>(
            (value << 8U) | bytes[offset + index]);
    }
    return value;
}

[[nodiscard]] std::uint64_t read_u64(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

[[nodiscard]] bool valid_event(EventClass value) noexcept {
    switch (value) {
        case EventClass::security_ready:
        case EventClass::agent_running:
        case EventClass::transport_state:
        case EventClass::authority_state:
        case EventClass::sync_state:
        case EventClass::ratox_state:
        case EventClass::resource_pressure:
        case EventClass::projection_failure:
        case EventClass::agent_stopping:
        case EventClass::agent_failed:
        case EventClass::current_snapshot:
            return true;
    }
    return false;
}

[[nodiscard]] bool valid_phase(AgentPhase value) noexcept {
    switch (value) {
        case AgentPhase::starting:
        case AgentPhase::running:
        case AgentPhase::stopping:
        case AgentPhase::stopped:
        case AgentPhase::failed:
            return true;
    }
    return false;
}

[[nodiscard]] bool valid_network(NetworkClass value) noexcept {
    switch (value) {
        case NetworkClass::tox_native:
        case NetworkClass::tox_tor:
        case NetworkClass::tox_i2p:
        case NetworkClass::tox_i2p_construction:
            return true;
    }
    return false;
}

[[nodiscard]] bool valid_error(ErrorCode value) noexcept {
    switch (value) {
        case ErrorCode::ok:
        case ErrorCode::invalid_argument:
        case ErrorCode::not_found:
        case ErrorCode::unsupported:
        case ErrorCode::unavailable:
        case ErrorCode::io_error:
        case ErrorCode::library_error:
        case ErrorCode::protocol_error:
        case ErrorCode::timeout:
        case ErrorCode::internal_error:
        case ErrorCode::resource_exhausted:
            return true;
    }
    return false;
}

[[nodiscard]] Status validate_observation(const Observation &observation) {
    if (!valid_event(observation.event) ||
        !valid_error(observation.status) ||
        !valid_phase(observation.phase) ||
        !valid_network(observation.network) ||
        (observation.flags & ~kKnownObservationFlags) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostic observation contains an unknown closed value"};
    }
    return Status::success();
}

void append_record(std::vector<std::uint8_t> &output, const Record &record) {
    append_u64(output, record.sequence);
    output.push_back(static_cast<std::uint8_t>(record.observation.event));
    output.push_back(static_cast<std::uint8_t>(record.observation.status));
    output.push_back(static_cast<std::uint8_t>(record.observation.phase));
    output.push_back(static_cast<std::uint8_t>(record.observation.network));
    append_u32(output, record.observation.flags);
    output.insert(output.end(),
                  record.observation.configuration_commitment.begin(),
                  record.observation.configuration_commitment.end());
    for (const std::uint64_t value : {
             record.observation.peer_count,
             record.observation.authorized_peer_count,
             record.observation.pending_command_count,
             record.observation.active_file_transfer_count,
             record.observation.ratox_live_session_count,
             record.observation.ratox_admission_rejections,
             record.observation.transport_dropped_events,
             record.observation.ratox_dropped_events,
             record.observation.sync_work_admitted,
             record.observation.sync_work_rejected,
         }) {
        append_u64(output, value);
    }
}

[[nodiscard]] Result<Record> decode_record(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kRecordBytes ||
        !valid_event(static_cast<EventClass>(bytes[8U])) ||
        !valid_error(static_cast<ErrorCode>(bytes[9U])) ||
        !valid_phase(static_cast<AgentPhase>(bytes[10U])) ||
        !valid_network(static_cast<NetworkClass>(bytes[11U]))) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic record has invalid size or closed fields"};
    }
    Record record;
    record.sequence = read_u64(bytes, 0U);
    record.observation.event = static_cast<EventClass>(bytes[8U]);
    record.observation.status = static_cast<ErrorCode>(bytes[9U]);
    record.observation.phase = static_cast<AgentPhase>(bytes[10U]);
    record.observation.network = static_cast<NetworkClass>(bytes[11U]);
    record.observation.flags = read_u32(bytes, 12U);
    if ((record.observation.flags & ~kKnownObservationFlags) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic record contains unknown flags"};
    }
    std::copy_n(bytes.begin() + 16, security::kDigestBytes,
                record.observation.configuration_commitment.begin());
    std::array<std::uint64_t *, 10U> counters{
        &record.observation.peer_count,
        &record.observation.authorized_peer_count,
        &record.observation.pending_command_count,
        &record.observation.active_file_transfer_count,
        &record.observation.ratox_live_session_count,
        &record.observation.ratox_admission_rejections,
        &record.observation.transport_dropped_events,
        &record.observation.ratox_dropped_events,
        &record.observation.sync_work_admitted,
        &record.observation.sync_work_rejected,
    };
    std::size_t offset = 48U;
    for (std::uint64_t *counter : counters) {
        *counter = read_u64(bytes, offset);
        offset += 8U;
    }
    return record;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path) {
    int opened = -1;
    do {
        opened = ::open(path.c_str(),
                        O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    } while (opened < 0 && errno == EINTR);
    if (opened < 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          "diagnostic recorder does not exist"};
        }
        return io_status("unable to open diagnostic recorder", path);
    }
    FileDescriptor descriptor(opened);
    struct stat before {};
    const std::size_t maximum = kHeaderBytes +
        kMaximumMaximumRecords * kRecordBytes + security::kSignatureBytes;
    if (::fstat(descriptor.get(), &before) != 0 ||
        !S_ISREG(before.st_mode) || before.st_nlink != 1 ||
        before.st_uid != ::geteuid() ||
        (before.st_mode & S_IRUSR) == 0U ||
        (before.st_mode & (S_IRWXG | S_IRWXO)) != 0U ||
        before.st_size < 0 ||
        static_cast<std::uint64_t>(before.st_size) > maximum) {
        return Status{ErrorCode::io_error,
                      "diagnostic recorder is not one bounded owner-private regular file"};
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(before.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor.get(), bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            return Status{ErrorCode::io_error,
                          "diagnostic recorder changed or ended during read"};
        }
        offset += static_cast<std::size_t>(count);
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0 ||
        before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
        before.st_mode != after.st_mode || before.st_nlink != after.st_nlink ||
        before.st_uid != after.st_uid || before.st_size != after.st_size ||
        before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
        before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
        before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
        before.st_ctim.tv_nsec != after.st_ctim.tv_nsec) {
        return Status{ErrorCode::io_error,
                      "diagnostic recorder changed while it was read"};
    }
    return bytes;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned(
    const Snapshot &snapshot) {
    if (snapshot.maximum_records < kMinimumMaximumRecords ||
        snapshot.maximum_records > kMaximumMaximumRecords ||
        snapshot.records.size() > snapshot.maximum_records ||
        snapshot.records.size() > std::numeric_limits<std::uint16_t>::max() ||
        snapshot.mutation != snapshot.high_sequence ||
        snapshot.high_sequence < snapshot.records.size() ||
        snapshot.evicted_records !=
            snapshot.high_sequence - snapshot.records.size()) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostic recorder bounds or sequence invariants are invalid"};
    }
    std::vector<std::uint8_t> output;
    output.reserve(kHeaderBytes + snapshot.records.size() * kRecordBytes);
    output.insert(output.end(), kMagic.begin(), kMagic.end());
    append_u16(output, static_cast<std::uint16_t>(snapshot.maximum_records));
    append_u16(output, static_cast<std::uint16_t>(snapshot.records.size()));
    append_u64(output, snapshot.mutation);
    append_u64(output, snapshot.high_sequence);
    append_u64(output, snapshot.evicted_records);
    std::uint64_t expected = snapshot.evicted_records + 1U;
    for (const Record &record : snapshot.records) {
        const Status valid = validate_observation(record.observation);
        if (!valid.ok() || record.sequence != expected++) {
            return Status{ErrorCode::invalid_argument,
                          "diagnostic records are invalid or noncontiguous"};
        }
        append_record(output, record);
    }
    return output;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed(
    const Snapshot &snapshot, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto output = encode_unsigned(snapshot);
    if (!output) return output.status();
    auto digest = sodium.hash(kStoreDomain, output.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    output.value().insert(output.value().end(), signature.value().begin(),
                          signature.value().end());
    return output;
}

[[nodiscard]] Result<Snapshot> decode_signed(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    if (bytes.size() < kHeaderBytes + security::kSignatureBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic recorder header or size is invalid"};
    }
    const std::size_t unsigned_size = bytes.size() - security::kSignatureBytes;
    const auto unsigned_bytes = bytes.first(unsigned_size);
    auto digest = sodium.hash(kStoreDomain, unsigned_bytes);
    if (!digest) return digest.status();
    security::Signature signature{};
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(unsigned_size),
                signature.size(), signature.begin());
    const Status verified = sodium.verify_detached(
        signature, digest.value(), expected_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic recorder signature is invalid"};
    }
    Snapshot snapshot;
    snapshot.maximum_records = read_u16(bytes, 8U);
    const std::size_t count = read_u16(bytes, 10U);
    snapshot.mutation = read_u64(bytes, 12U);
    snapshot.high_sequence = read_u64(bytes, 20U);
    snapshot.evicted_records = read_u64(bytes, 28U);
    if (snapshot.maximum_records < kMinimumMaximumRecords ||
        snapshot.maximum_records > kMaximumMaximumRecords ||
        count > snapshot.maximum_records ||
        unsigned_size != kHeaderBytes + count * kRecordBytes ||
        snapshot.mutation != snapshot.high_sequence ||
        snapshot.high_sequence < count ||
        snapshot.evicted_records != snapshot.high_sequence - count) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic recorder envelope is noncanonical"};
    }
    snapshot.records.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        auto record = decode_record(unsigned_bytes.subspan(
            kHeaderBytes + index * kRecordBytes, kRecordBytes));
        if (!record ||
            record.value().sequence != snapshot.evicted_records + index + 1U) {
            return Status{ErrorCode::protocol_error,
                          "diagnostic recorder sequence is noncanonical"};
        }
        snapshot.records.push_back(std::move(record).value());
    }
    auto canonical = encode_unsigned(snapshot);
    if (!canonical || canonical.value().size() != unsigned_bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    unsigned_bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic recorder bytes are noncanonical"};
    }
    return snapshot;
}

[[nodiscard]] Result<std::uint64_t> parse_decimal(
    std::string_view text, std::string_view label) {
    if (text.empty() || (text.size() > 1U && text.front() == '0')) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical decimal"};
    }
    std::uint64_t value = 0U;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(),
                                        value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical decimal"};
    }
    return value;
}

[[nodiscard]] std::vector<std::string_view> lines(std::string_view text) {
    std::vector<std::string_view> result;
    std::size_t offset = 0U;
    while (offset < text.size()) {
        const std::size_t end = text.find('\n', offset);
        if (end == std::string_view::npos) return {};
        result.push_back(text.substr(offset, end - offset));
        offset = end + 1U;
    }
    return result;
}

[[nodiscard]] Result<std::string_view> field(
    std::string_view line, std::string_view prefix) {
    if (!line.starts_with(prefix)) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics export field order or name is invalid"};
    }
    return line.substr(prefix.size());
}

[[nodiscard]] bool printable_token(std::string_view value,
                                   std::size_t maximum) {
    return !value.empty() && value.size() <= maximum &&
        std::all_of(value.begin(), value.end(), [](unsigned char byte) {
            return byte >= 0x21U && byte <= 0x7eU;
        });
}

template <std::size_t Size>
[[nodiscard]] bool one_of(
    std::string_view value,
    const std::array<std::string_view, Size> &choices) noexcept {
    return std::find(choices.begin(), choices.end(), value) != choices.end();
}

[[nodiscard]] bool event_name(std::string_view value) noexcept {
    static constexpr std::array<std::string_view, 11U> names{
        "security-ready", "agent-running", "transport-state",
        "authority-state", "sync-state", "ratox-state",
        "resource-pressure", "projection-failure", "agent-stopping",
        "agent-failed", "current-snapshot"};
    return one_of(value, names);
}

[[nodiscard]] bool phase_name(std::string_view value) noexcept {
    static constexpr std::array<std::string_view, 5U> names{
        "starting", "running", "stopping", "stopped", "failed"};
    return one_of(value, names);
}

[[nodiscard]] bool network_name(std::string_view value) noexcept {
    static constexpr std::array<std::string_view, 4U> names{
        "tox-native", "tox-tor", "tox-i2p", "tox-i2p-construction"};
    return one_of(value, names);
}

[[nodiscard]] Result<std::vector<std::string_view>> split_exact(
    std::string_view text, char delimiter, std::size_t count) {
    std::vector<std::string_view> result;
    result.reserve(count);
    std::size_t offset = 0U;
    while (result.size() + 1U < count) {
        const std::size_t end = text.find(delimiter, offset);
        if (end == std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "diagnostic record field count is invalid"};
        }
        result.push_back(text.substr(offset, end - offset));
        offset = end + 1U;
    }
    result.push_back(text.substr(offset));
    if (result.size() != count ||
        result.back().find(delimiter) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic record field count is invalid"};
    }
    return result;
}

[[nodiscard]] Result<security::Digest> parse_digest(std::string_view text) {
    auto decoded = security::decode_hex_exact(
        text, security::kDigestBytes, "diagnostic digest");
    if (!decoded) return decoded.status();
    security::Digest digest{};
    std::copy(decoded.value().begin(), decoded.value().end(), digest.begin());
    return digest;
}

[[nodiscard]] Result<std::array<std::uint64_t, 10U>> parse_counters(
    std::string_view text) {
    std::array<std::uint64_t, 10U> result{};
    std::size_t offset = 0U;
    for (std::size_t index = 0U; index < result.size(); ++index) {
        const std::size_t end = index + 1U == result.size()
            ? text.size()
            : text.find(':', offset);
        if (end == std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "diagnostic counter tuple is incomplete"};
        }
        auto parsed = parse_decimal(text.substr(offset, end - offset),
                                    "diagnostic counter");
        if (!parsed) return parsed.status();
        result[index] = parsed.value();
        offset = end + 1U;
    }
    if (offset != text.size() + 1U) {
        return Status{ErrorCode::protocol_error,
                      "diagnostic counter tuple has trailing fields"};
    }
    return result;
}

[[nodiscard]] std::string counters(const Observation &observation) {
    std::ostringstream output;
    output << observation.peer_count << ':'
           << observation.authorized_peer_count << ':'
           << observation.pending_command_count << ':'
           << observation.active_file_transfer_count << ':'
           << observation.ratox_live_session_count << ':'
           << observation.ratox_admission_rejections << ':'
           << observation.transport_dropped_events << ':'
           << observation.ratox_dropped_events << ':'
           << observation.sync_work_admitted << ':'
           << observation.sync_work_rejected;
    return output.str();
}

[[nodiscard]] Status validate_namespace_health_export(
    const NamespaceHealthExport &health) {
    if (health.verified_records > health.total_namespaces ||
        health.absent_records >
            health.total_namespaces - health.verified_records ||
        health.invalid_records != health.total_namespaces -
            health.verified_records - health.absent_records ||
        health.green_namespaces > health.verified_records ||
        health.yellow_namespaces >
            health.verified_records - health.green_namespaces ||
        health.red_namespaces != health.verified_records -
            health.green_namespaces - health.yellow_namespaces ||
        health.complete_custody_namespaces > health.verified_records ||
        health.partial_custody_namespaces != health.verified_records -
            health.complete_custody_namespaces ||
        health.stale_policy_namespaces > health.verified_records ||
        health.conflict_namespaces > health.verified_records ||
        health.automation_stalled_namespaces > health.verified_records ||
        health.store_pressure_namespaces > health.verified_records ||
        health.source_exhausted_namespaces > health.verified_records) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostic namespace-health aggregate is inconsistent"};
    }
    return Status::success();
}

void append_namespace_health(std::ostringstream &output,
                             const NamespaceHealthExport &health) {
    output
        << "namespace-health-verification=stable-device-signature-verified-locally\n"
        << "namespace-health-total=" << health.total_namespaces << '\n'
        << "namespace-health-verified=" << health.verified_records << '\n'
        << "namespace-health-absent=" << health.absent_records << '\n'
        << "namespace-health-invalid=" << health.invalid_records << '\n'
        << "namespace-health-green=" << health.green_namespaces << '\n'
        << "namespace-health-yellow=" << health.yellow_namespaces << '\n'
        << "namespace-health-red=" << health.red_namespaces << '\n'
        << "namespace-health-policy-stale="
        << health.stale_policy_namespaces << '\n'
        << "namespace-health-custody-complete="
        << health.complete_custody_namespaces << '\n'
        << "namespace-health-custody-partial="
        << health.partial_custody_namespaces << '\n'
        << "namespace-health-conflicts=" << health.conflict_namespaces
        << '\n'
        << "namespace-health-missing-objects=" << health.missing_objects
        << '\n'
        << "namespace-health-missing-bytes=" << health.missing_bytes << '\n'
        << "namespace-health-automation-stalled="
        << health.automation_stalled_namespaces << '\n'
        << "namespace-health-store-pressure="
        << health.store_pressure_namespaces << '\n'
        << "namespace-health-source-exhausted="
        << health.source_exhausted_namespaces << '\n'
        << "namespace-health-source-absent-results="
        << health.source_absent_results << '\n'
        << "namespace-health-source-unavailable-results="
        << health.source_unavailable_results << '\n'
        << "namespace-health-maximum-automation-failure-streak="
        << health.maximum_automation_failure_streak << '\n'
        << "namespace-health-rollback-witness=0\n"
        << "namespace-health-backup-certified=0\n";
}

[[nodiscard]] bool valid_host_grade(HostCapabilityGrade value) noexcept {
    return value == HostCapabilityGrade::unavailable ||
        value == HostCapabilityGrade::available ||
        value == HostCapabilityGrade::live_proved ||
        value == HostCapabilityGrade::probe_denied;
}

[[nodiscard]] Status validate_host_capabilities_export(
    const HostCapabilitiesExport &capabilities) {
    constexpr std::uint32_t kKnownControllerMask = (1U << 8U) - 1U;
    constexpr std::uint32_t kKnownInterfaceMask = (1U << 12U) - 1U;
    if (!valid_host_grade(capabilities.pidfd) ||
        !valid_host_grade(capabilities.seccomp) ||
        !valid_host_grade(capabilities.mdwe) ||
        !valid_host_grade(capabilities.landlock) ||
        static_cast<std::uint8_t>(capabilities.privilege_escalation) >
            static_cast<std::uint8_t>(
                PrivilegeCapabilityGrade::probe_denied) ||
        static_cast<std::uint8_t>(capabilities.sudo) >
            static_cast<std::uint8_t>(
                SudoCapabilityGrade::file_capabilities) ||
        static_cast<std::uint8_t>(capabilities.cgroup_v2) >
            static_cast<std::uint8_t>(CgroupCapabilityGrade::delegated) ||
        (capabilities.landlock == HostCapabilityGrade::unavailable &&
         capabilities.landlock_abi != 0U) ||
        (capabilities.cgroup_controller_mask & ~kKnownControllerMask) != 0U ||
        (capabilities.cgroup_interface_available_mask &
         ~kKnownInterfaceMask) != 0U ||
        (capabilities.cgroup_interface_readable_mask &
         ~capabilities.cgroup_interface_available_mask) != 0U ||
        (capabilities.cgroup_interface_writable_mask &
         ~capabilities.cgroup_interface_available_mask) != 0U ||
        (capabilities.cgroup_v2 == CgroupCapabilityGrade::unavailable &&
         (capabilities.cgroup_controller_mask != 0U ||
          capabilities.cgroup_unknown_controllers != 0U ||
          capabilities.cgroup_interface_available_mask != 0U ||
          capabilities.cgroup_interface_readable_mask != 0U ||
          capabilities.cgroup_interface_writable_mask != 0U))) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostic host-capability aggregate is inconsistent"};
    }
    return Status::success();
}

[[nodiscard]] std::string_view host_grade_name(
    HostCapabilityGrade value) noexcept {
    switch (value) {
        case HostCapabilityGrade::unavailable: return "unavailable";
        case HostCapabilityGrade::available: return "available";
        case HostCapabilityGrade::live_proved: return "live-proved";
        case HostCapabilityGrade::probe_denied: return "probe-denied";
    }
    return "unknown";
}

[[nodiscard]] std::string_view privilege_grade_name(
    PrivilegeCapabilityGrade value) noexcept {
    switch (value) {
        case PrivilegeCapabilityGrade::unavailable: return "unavailable";
        case PrivilegeCapabilityGrade::blocked: return "blocked";
        case PrivilegeCapabilityGrade::host_policy_pending:
            return "host-policy-pending";
        case PrivilegeCapabilityGrade::probe_denied: return "probe-denied";
    }
    return "unknown";
}

[[nodiscard]] std::string_view sudo_grade_name(
    SudoCapabilityGrade value) noexcept {
    switch (value) {
        case SudoCapabilityGrade::unavailable: return "unavailable";
        case SudoCapabilityGrade::setuid_root: return "setuid-root";
        case SudoCapabilityGrade::file_capabilities:
            return "file-capabilities";
    }
    return "unknown";
}

[[nodiscard]] std::string_view cgroup_grade_name(
    CgroupCapabilityGrade value) noexcept {
    switch (value) {
        case CgroupCapabilityGrade::unavailable: return "unavailable";
        case CgroupCapabilityGrade::available: return "available";
        case CgroupCapabilityGrade::delegated: return "delegated";
    }
    return "unknown";
}

[[nodiscard]] Result<HostCapabilityGrade> parse_host_grade(
    std::string_view value) {
    if (value == "unavailable") return HostCapabilityGrade::unavailable;
    if (value == "available") return HostCapabilityGrade::available;
    if (value == "live-proved") return HostCapabilityGrade::live_proved;
    if (value == "probe-denied") return HostCapabilityGrade::probe_denied;
    return Status{ErrorCode::protocol_error,
                  "diagnostic host capability grade is invalid"};
}

[[nodiscard]] Result<PrivilegeCapabilityGrade> parse_privilege_grade(
    std::string_view value) {
    if (value == "unavailable")
        return PrivilegeCapabilityGrade::unavailable;
    if (value == "blocked") return PrivilegeCapabilityGrade::blocked;
    if (value == "host-policy-pending")
        return PrivilegeCapabilityGrade::host_policy_pending;
    if (value == "probe-denied")
        return PrivilegeCapabilityGrade::probe_denied;
    return Status{ErrorCode::protocol_error,
                  "diagnostic privilege capability grade is invalid"};
}

[[nodiscard]] Result<SudoCapabilityGrade> parse_sudo_grade(
    std::string_view value) {
    if (value == "unavailable") return SudoCapabilityGrade::unavailable;
    if (value == "setuid-root") return SudoCapabilityGrade::setuid_root;
    if (value == "file-capabilities")
        return SudoCapabilityGrade::file_capabilities;
    return Status{ErrorCode::protocol_error,
                  "diagnostic sudo capability grade is invalid"};
}

[[nodiscard]] Result<CgroupCapabilityGrade> parse_cgroup_grade(
    std::string_view value) {
    if (value == "unavailable") return CgroupCapabilityGrade::unavailable;
    if (value == "available") return CgroupCapabilityGrade::available;
    if (value == "delegated") return CgroupCapabilityGrade::delegated;
    return Status{ErrorCode::protocol_error,
                  "diagnostic cgroup capability grade is invalid"};
}

void append_host_capabilities(std::ostringstream &output,
                              const HostCapabilitiesExport &capabilities) {
    output << "host-capabilities-probe=passive-no-fork\n"
           << "host-capabilities-pidfd="
           << host_grade_name(capabilities.pidfd) << '\n'
           << "host-capabilities-seccomp="
           << host_grade_name(capabilities.seccomp) << '\n'
           << "host-capabilities-mdwe="
           << host_grade_name(capabilities.mdwe) << '\n'
           << "host-capabilities-landlock="
           << host_grade_name(capabilities.landlock) << '\n'
           << "host-capabilities-landlock-abi="
           << capabilities.landlock_abi << '\n'
           << "host-capabilities-privilege-escalation="
           << privilege_grade_name(capabilities.privilege_escalation) << '\n'
           << "host-capabilities-sudo=" << sudo_grade_name(capabilities.sudo)
           << '\n'
           << "host-capabilities-cgroup-v2="
           << cgroup_grade_name(capabilities.cgroup_v2) << '\n'
           << "host-capabilities-cgroup-controller-mask="
           << capabilities.cgroup_controller_mask << '\n'
           << "host-capabilities-cgroup-unknown-controllers="
           << capabilities.cgroup_unknown_controllers << '\n'
           << "host-capabilities-cgroup-interface-available-mask="
           << capabilities.cgroup_interface_available_mask << '\n'
           << "host-capabilities-cgroup-interface-readable-mask="
           << capabilities.cgroup_interface_readable_mask << '\n'
           << "host-capabilities-cgroup-interface-writable-mask="
           << capabilities.cgroup_interface_writable_mask << '\n';
}

}  // namespace

Recorder::Recorder(Config config, const security::DeviceIdentity &identity,
                   const security::Sodium &sodium, Snapshot state)
    : config_(std::move(config)), identity_(&identity), sodium_(&sodium),
      state_(std::move(state)) {}

Result<std::unique_ptr<Recorder>> Recorder::open(
    Config config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (config.path.empty() || !config.path.is_absolute() ||
        config.path == config.path.root_path() ||
        config.path.lexically_normal() != config.path ||
        config.maximum_records < kMinimumMaximumRecords ||
        config.maximum_records > kMaximumMaximumRecords) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostic recorder requires an absolute private path and 16..256 records"};
    }
    Snapshot state;
    state.maximum_records = config.maximum_records;
    auto bytes = read_private_file(config.path);
    if (bytes) {
        auto decoded = decode_signed(
            bytes.value(), identity.public_key(), sodium);
        if (!decoded) return decoded.status();
        state = std::move(decoded).value();
        state.maximum_records = config.maximum_records;
        if (state.records.size() > state.maximum_records) {
            const std::size_t remove =
                state.records.size() - state.maximum_records;
            state.records.erase(
                state.records.begin(),
                state.records.begin() + static_cast<std::ptrdiff_t>(remove));
            state.evicted_records += remove;
        }
    } else if (bytes.status().code() != ErrorCode::not_found) {
        return bytes.status();
    }
    return std::unique_ptr<Recorder>(new Recorder(
        std::move(config), identity, sodium, std::move(state)));
}

Status Recorder::record(const Observation &observation) {
    const Status valid = validate_observation(observation);
    if (!valid.ok()) return valid;
    std::scoped_lock lock(mutex_);
    if (state_.high_sequence == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "diagnostic recorder sequence is exhausted"};
    }
    Snapshot next = state_;
    ++next.high_sequence;
    next.mutation = next.high_sequence;
    next.records.push_back(Record{next.high_sequence, observation});
    if (next.records.size() > next.maximum_records) {
        next.records.erase(next.records.begin());
        ++next.evicted_records;
    }
    auto encoded = encode_signed(next, *identity_, *sodium_);
    if (!encoded) return encoded.status();
    const Status written = StateStore::write_atomic(config_.path, encoded.value());
    if (!written.ok()) return written;
    state_ = std::move(next);
    return Status::success();
}

Snapshot Recorder::snapshot() const {
    std::scoped_lock lock(mutex_);
    return state_;
}

Result<std::string> Recorder::redacted_export(
    const Observation &current,
    std::uint64_t recorder_write_failures,
    const NamespaceHealthExport &namespace_health,
    const HostCapabilitiesExport &host_capabilities) const {
    const Status valid = validate_observation(current);
    if (!valid.ok()) return valid;
    const Status health_valid =
        validate_namespace_health_export(namespace_health);
    if (!health_valid.ok()) return health_valid;
    const Status host_valid =
        validate_host_capabilities_export(host_capabilities);
    if (!host_valid.ok()) return host_valid;
    std::scoped_lock lock(mutex_);
    const auto render = [&](std::size_t omitted) {
        std::ostringstream output;
        output << "iotox-diagnostics-redacted-v3\n"
               << "verification=stable-device-signature-verified-locally\n"
               << "privacy=closed-fields-no-content-identities-paths-or-time\n"
               << "store-mutation=" << state_.mutation << '\n'
               << "high-sequence=" << state_.high_sequence << '\n'
               << "evicted-records=" << state_.evicted_records << '\n'
               << "export-omitted-records=" << omitted << '\n'
               << "record-count=" << state_.records.size() - omitted << '\n'
               << "maximum-records=" << state_.maximum_records << '\n'
               << "recorder-write-failures=" << recorder_write_failures << '\n'
               << "current-config-commitment="
               << security::hex(current.configuration_commitment) << '\n'
               << "current-event=" << to_string(current.event) << '\n'
               << "current-status="
               << static_cast<unsigned>(current.status) << '\n'
               << "current-phase=" << to_string(current.phase) << '\n'
               << "current-network=" << to_string(current.network) << '\n'
               << "current-flags=" << current.flags << '\n'
               << "current-counters=" << counters(current) << '\n';
        append_namespace_health(output, namespace_health);
        append_host_capabilities(output, host_capabilities);
        for (std::size_t index = omitted; index < state_.records.size();
             ++index) {
            const Record &record = state_.records[index];
            const Observation &observed = record.observation;
            output << "record=" << record.sequence << ':'
                   << to_string(observed.event) << ':'
                   << static_cast<unsigned>(observed.status) << ':'
                   << to_string(observed.phase) << ':'
                   << to_string(observed.network) << ':'
                   << observed.flags << ':'
                   << security::hex(observed.configuration_commitment) << ':'
                   << counters(observed) << '\n';
        }
        return output.str();
    };
    std::size_t omitted = 0U;
    std::string rendered = render(omitted);
    while (rendered.size() > kMaximumRedactedExportBytes &&
           omitted < state_.records.size()) {
        ++omitted;
        rendered = render(omitted);
    }
    if (rendered.size() > kMaximumRedactedExportBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "current diagnostic observation exceeds its control-plane bound"};
    }
    return rendered;
}

Result<ExportSummary> inspect_redacted_export(std::string_view text) {
    if (text.empty() || text.size() > kMaximumRedactedExportBytes ||
        text.back() != '\n' ||
        !std::all_of(text.begin(), text.end(), [](unsigned char byte) {
            return byte == '\n' || (byte >= 0x20U && byte <= 0x7eU);
        })) {
        return Status{ErrorCode::protocol_error,
                      "redacted diagnostics bytes are invalid"};
    }
    const auto values = lines(text);
    const bool version_one = !values.empty() &&
        values[0U] == "iotox-diagnostics-redacted-v1";
    const bool version_two = !values.empty() &&
        values[0U] == "iotox-diagnostics-redacted-v2";
    const bool version_three = !values.empty() &&
        values[0U] == "iotox-diagnostics-redacted-v3";
    const std::size_t record_offset = version_three ? 53U
        : version_two                              ? 39U
                                                   : 17U;
    if ((!version_one && !version_two && !version_three) ||
        values.size() < record_offset ||
        values[1U] !=
            "verification=stable-device-signature-verified-locally" ||
        values[2U] !=
            "privacy=closed-fields-no-content-identities-paths-or-time") {
        return Status{ErrorCode::protocol_error,
                      "redacted diagnostics header is invalid"};
    }
    ExportSummary summary;
    auto mutation = field(values[3U], "store-mutation=");
    auto high = field(values[4U], "high-sequence=");
    auto evicted = field(values[5U], "evicted-records=");
    auto omitted = field(values[6U], "export-omitted-records=");
    auto count = field(values[7U], "record-count=");
    auto maximum = field(values[8U], "maximum-records=");
    auto write_failures = field(values[9U], "recorder-write-failures=");
    auto commitment = field(values[10U], "current-config-commitment=");
    if (!mutation || !high || !evicted || !omitted || !count || !maximum ||
        !write_failures || !commitment) {
        return Status{ErrorCode::protocol_error,
                      "redacted diagnostics fields are invalid"};
    }
    auto parsed_mutation = parse_decimal(mutation.value(), "store mutation");
    auto parsed_high = parse_decimal(high.value(), "high sequence");
    auto parsed_evicted = parse_decimal(evicted.value(), "evicted records");
    auto parsed_omitted = parse_decimal(omitted.value(), "export omitted records");
    auto parsed_count = parse_decimal(count.value(), "record count");
    auto parsed_maximum = parse_decimal(maximum.value(), "maximum records");
    auto parsed_write_failures = parse_decimal(
        write_failures.value(), "recorder write failures");
    auto parsed_commitment = parse_digest(commitment.value());
    if (!parsed_mutation || !parsed_high || !parsed_evicted ||
        !parsed_omitted || !parsed_count || !parsed_maximum ||
        !parsed_write_failures || !parsed_commitment ||
        parsed_count.value() > kMaximumMaximumRecords ||
        parsed_omitted.value() > kMaximumMaximumRecords ||
        parsed_maximum.value() < kMinimumMaximumRecords ||
        parsed_maximum.value() > kMaximumMaximumRecords ||
        parsed_omitted.value() > parsed_maximum.value() ||
        parsed_count.value() >
            parsed_maximum.value() - parsed_omitted.value() ||
        parsed_mutation.value() != parsed_high.value() ||
        parsed_high.value() < parsed_count.value() ||
        parsed_high.value() - parsed_count.value() <
            parsed_omitted.value() ||
        parsed_evicted.value() !=
            parsed_high.value() - parsed_count.value() -
                parsed_omitted.value() ||
        values.size() != record_offset + parsed_count.value()) {
        return Status{ErrorCode::protocol_error,
                      "redacted diagnostics envelope is inconsistent"};
    }
    auto event = field(values[11U], "current-event=");
    auto status = field(values[12U], "current-status=");
    auto phase = field(values[13U], "current-phase=");
    auto network = field(values[14U], "current-network=");
    auto flags = field(values[15U], "current-flags=");
    auto current_counters = field(values[16U], "current-counters=");
    auto parsed_status = status
        ? parse_decimal(status.value(), "current status")
        : Result<std::uint64_t>{Status{ErrorCode::protocol_error,
                                      "current status is absent"}};
    auto parsed_flags = flags
        ? parse_decimal(flags.value(), "current flags")
        : Result<std::uint64_t>{Status{ErrorCode::protocol_error,
                                      "current flags are absent"}};
    if (!event || !status || !phase || !network || !flags ||
        !current_counters || !event_name(event.value()) ||
        !phase_name(phase.value()) || !network_name(network.value()) ||
        !parsed_status ||
        parsed_status.value() >
            static_cast<std::uint64_t>(ErrorCode::resource_exhausted) ||
        !parsed_flags || parsed_flags.value() > kKnownObservationFlags ||
        (parsed_flags.value() & ~kKnownObservationFlags) != 0U ||
        !parse_counters(current_counters.value())) {
        return Status{ErrorCode::protocol_error,
                      "redacted diagnostics current observation is invalid"};
    }
    if (version_two || version_three) {
        if (values[17U] !=
                "namespace-health-verification=stable-device-signature-verified-locally" ||
            values[37U] != "namespace-health-rollback-witness=0" ||
            values[38U] != "namespace-health-backup-certified=0") {
            return Status{ErrorCode::protocol_error,
                          "redacted namespace-health qualifiers are invalid"};
        }
        NamespaceHealthExport &health = summary.namespace_health;
        const std::array<std::pair<std::string_view, std::uint64_t *>, 19U>
            fields{{
                {"namespace-health-total=", &health.total_namespaces},
                {"namespace-health-verified=", &health.verified_records},
                {"namespace-health-absent=", &health.absent_records},
                {"namespace-health-invalid=", &health.invalid_records},
                {"namespace-health-green=", &health.green_namespaces},
                {"namespace-health-yellow=", &health.yellow_namespaces},
                {"namespace-health-red=", &health.red_namespaces},
                {"namespace-health-policy-stale=",
                 &health.stale_policy_namespaces},
                {"namespace-health-custody-complete=",
                 &health.complete_custody_namespaces},
                {"namespace-health-custody-partial=",
                 &health.partial_custody_namespaces},
                {"namespace-health-conflicts=", &health.conflict_namespaces},
                {"namespace-health-missing-objects=", &health.missing_objects},
                {"namespace-health-missing-bytes=", &health.missing_bytes},
                {"namespace-health-automation-stalled=",
                 &health.automation_stalled_namespaces},
                {"namespace-health-store-pressure=",
                 &health.store_pressure_namespaces},
                {"namespace-health-source-exhausted=",
                 &health.source_exhausted_namespaces},
                {"namespace-health-source-absent-results=",
                 &health.source_absent_results},
                {"namespace-health-source-unavailable-results=",
                 &health.source_unavailable_results},
                {"namespace-health-maximum-automation-failure-streak=",
                 &health.maximum_automation_failure_streak},
            }};
        for (std::size_t index = 0U; index < fields.size(); ++index) {
            auto value = field(values[18U + index], fields[index].first);
            auto parsed = value
                ? parse_decimal(value.value(), "namespace health aggregate")
                : Result<std::uint64_t>{value.status()};
            if (!parsed) return parsed.status();
            *fields[index].second = parsed.value();
        }
        if (!validate_namespace_health_export(health).ok()) {
            return Status{ErrorCode::protocol_error,
                          "redacted namespace-health aggregate is inconsistent"};
        }
        summary.namespace_health_present = true;
    }
    if (version_three) {
        if (values[39U] != "host-capabilities-probe=passive-no-fork") {
            return Status{ErrorCode::protocol_error,
                          "redacted host-capability probe mode is invalid"};
        }
        HostCapabilitiesExport &host = summary.host_capabilities;
        auto pidfd = field(values[40U], "host-capabilities-pidfd=");
        auto seccomp = field(values[41U], "host-capabilities-seccomp=");
        auto mdwe = field(values[42U], "host-capabilities-mdwe=");
        auto landlock = field(values[43U], "host-capabilities-landlock=");
        auto landlock_abi =
            field(values[44U], "host-capabilities-landlock-abi=");
        auto privilege =
            field(values[45U], "host-capabilities-privilege-escalation=");
        auto sudo = field(values[46U], "host-capabilities-sudo=");
        auto cgroup = field(values[47U], "host-capabilities-cgroup-v2=");
        if (!pidfd || !seccomp || !mdwe || !landlock || !landlock_abi ||
            !privilege || !sudo || !cgroup) {
            return Status{ErrorCode::protocol_error,
                          "redacted host-capability fields are absent"};
        }
        auto parsed_pidfd = parse_host_grade(pidfd.value());
        auto parsed_seccomp = parse_host_grade(seccomp.value());
        auto parsed_mdwe = parse_host_grade(mdwe.value());
        auto parsed_landlock = parse_host_grade(landlock.value());
        auto parsed_landlock_abi =
            parse_decimal(landlock_abi.value(), "landlock ABI");
        auto parsed_privilege = parse_privilege_grade(privilege.value());
        auto parsed_sudo = parse_sudo_grade(sudo.value());
        auto parsed_cgroup = parse_cgroup_grade(cgroup.value());
        if (!parsed_pidfd || !parsed_seccomp || !parsed_mdwe ||
            !parsed_landlock || !parsed_landlock_abi ||
            parsed_landlock_abi.value() >
                std::numeric_limits<std::uint32_t>::max() ||
            !parsed_privilege || !parsed_sudo || !parsed_cgroup) {
            return Status{ErrorCode::protocol_error,
                          "redacted host-capability grade is invalid"};
        }
        host.pidfd = parsed_pidfd.value();
        host.seccomp = parsed_seccomp.value();
        host.mdwe = parsed_mdwe.value();
        host.landlock = parsed_landlock.value();
        host.landlock_abi =
            static_cast<std::uint32_t>(parsed_landlock_abi.value());
        host.privilege_escalation = parsed_privilege.value();
        host.sudo = parsed_sudo.value();
        host.cgroup_v2 = parsed_cgroup.value();
        const std::array<
            std::pair<std::string_view, std::uint32_t *>, 5U> masks{{
            {"host-capabilities-cgroup-controller-mask=",
             &host.cgroup_controller_mask},
            {"host-capabilities-cgroup-unknown-controllers=",
             &host.cgroup_unknown_controllers},
            {"host-capabilities-cgroup-interface-available-mask=",
             &host.cgroup_interface_available_mask},
            {"host-capabilities-cgroup-interface-readable-mask=",
             &host.cgroup_interface_readable_mask},
            {"host-capabilities-cgroup-interface-writable-mask=",
             &host.cgroup_interface_writable_mask},
        }};
        for (std::size_t index = 0U; index < masks.size(); ++index) {
            auto value = field(values[48U + index], masks[index].first);
            auto parsed = value
                ? parse_decimal(value.value(), "host capability mask")
                : Result<std::uint64_t>{value.status()};
            if (!parsed ||
                parsed.value() > std::numeric_limits<std::uint32_t>::max()) {
                return Status{ErrorCode::protocol_error,
                              "redacted host-capability mask is invalid"};
            }
            *masks[index].second = static_cast<std::uint32_t>(parsed.value());
        }
        if (!validate_host_capabilities_export(host).ok()) {
            return Status{ErrorCode::protocol_error,
                          "redacted host-capability aggregate is inconsistent"};
        }
        summary.host_capabilities_present = true;
    }
    for (std::size_t index = 0U; index < parsed_count.value(); ++index) {
        auto record = field(values[record_offset + index], "record=");
        if (!record || record.value().empty()) {
            return Status{ErrorCode::protocol_error,
                          "redacted diagnostic record is malformed"};
        }
        auto fields = split_exact(record.value(), ':', 17U);
        if (!fields) return fields.status();
        auto sequence = parse_decimal(fields.value()[0U], "record sequence");
        auto record_status = parse_decimal(fields.value()[2U], "record status");
        auto record_flags = parse_decimal(fields.value()[5U], "record flags");
        auto record_digest = parse_digest(fields.value()[6U]);
        if (!sequence ||
            sequence.value() != parsed_evicted.value() +
                parsed_omitted.value() + index + 1U ||
            !event_name(fields.value()[1U]) || !record_status ||
            record_status.value() >
                static_cast<std::uint64_t>(ErrorCode::resource_exhausted) ||
            !phase_name(fields.value()[3U]) ||
            !network_name(fields.value()[4U]) || !record_flags ||
            record_flags.value() > kKnownObservationFlags ||
            (record_flags.value() & ~kKnownObservationFlags) != 0U ||
            !record_digest) {
            return Status{ErrorCode::protocol_error,
                          "redacted diagnostic record fields are invalid"};
        }
        for (std::size_t field_index = 7U;
             field_index < fields.value().size(); ++field_index) {
            if (!parse_decimal(fields.value()[field_index],
                               "record counter")) {
                return Status{ErrorCode::protocol_error,
                              "redacted diagnostic record counter is invalid"};
            }
        }
    }
    summary.mutation = parsed_mutation.value();
    summary.high_sequence = parsed_high.value();
    summary.evicted_records = parsed_evicted.value();
    summary.export_omitted_records = parsed_omitted.value();
    summary.record_count = static_cast<std::size_t>(parsed_count.value());
    summary.maximum_records =
        static_cast<std::size_t>(parsed_maximum.value());
    summary.recorder_write_failures = parsed_write_failures.value();
    summary.current_configuration_commitment = parsed_commitment.value();
    return summary;
}

Result<std::vector<std::uint8_t>> make_bundle(
    std::string_view redacted_export, std::string_view product_version,
    std::string_view product_revision, const security::Sodium &sodium) {
    auto inspected = inspect_redacted_export(redacted_export);
    if (!inspected) return inspected.status();
    if (!printable_token(product_version, 32U) ||
        !printable_token(product_revision, 32U)) {
        return Status{ErrorCode::invalid_argument,
                      "diagnostics product identity is not a bounded token"};
    }
    auto digest = sodium.hash(
        kBundleDomain,
        std::span<const std::uint8_t>{
            reinterpret_cast<const std::uint8_t *>(redacted_export.data()),
            redacted_export.size()});
    if (!digest) return digest.status();
    std::ostringstream prefix;
    prefix << "iotox-diagnostics-bundle-v1\n"
           << "product-version=" << product_version << '\n'
           << "product-revision=" << product_revision << '\n'
           << "payload-bytes=" << redacted_export.size() << '\n'
           << "payload-digest=" << security::hex(digest.value()) << '\n'
           << "payload-begin\n";
    const std::string prefix_text = prefix.str();
    constexpr std::string_view suffix = "payload-end\n";
    if (prefix_text.size() + redacted_export.size() + suffix.size() >
        kMaximumBundleBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "diagnostics bundle exceeds its byte bound"};
    }
    std::vector<std::uint8_t> bundle(prefix_text.begin(), prefix_text.end());
    bundle.insert(bundle.end(), redacted_export.begin(), redacted_export.end());
    bundle.insert(bundle.end(), suffix.begin(), suffix.end());
    return bundle;
}

Result<BundleInspection> inspect_bundle(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    if (bytes.empty() || bytes.size() > kMaximumBundleBytes ||
        !std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t byte) {
            return byte == '\n' || (byte >= 0x20U && byte <= 0x7eU);
        })) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle bytes are invalid"};
    }
    const std::string_view text{
        reinterpret_cast<const char *>(bytes.data()), bytes.size()};
    constexpr std::string_view begin = "payload-begin\n";
    constexpr std::string_view end = "payload-end\n";
    const std::size_t marker = text.find(begin);
    if (marker == std::string_view::npos || !text.ends_with(end)) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle framing is invalid"};
    }
    const std::string_view header = text.substr(0U, marker);
    const auto header_lines = lines(header);
    if (header_lines.size() != 5U ||
        header_lines[0U] != "iotox-diagnostics-bundle-v1") {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle header is invalid"};
    }
    auto version = field(header_lines[1U], "product-version=");
    auto revision = field(header_lines[2U], "product-revision=");
    auto length = field(header_lines[3U], "payload-bytes=");
    auto claimed_digest = field(header_lines[4U], "payload-digest=");
    if (!version || !revision || !length || !claimed_digest ||
        !printable_token(version.value(), 32U) ||
        !printable_token(revision.value(), 32U)) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle identity fields are invalid"};
    }
    auto parsed_length = parse_decimal(length.value(), "payload length");
    auto parsed_digest = parse_digest(claimed_digest.value());
    if (!parsed_length || !parsed_digest) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle commitment fields are invalid"};
    }
    const std::size_t payload_offset = marker + begin.size();
    const std::size_t payload_size =
        text.size() - payload_offset - end.size();
    if (parsed_length.value() != payload_size) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle payload length is invalid"};
    }
    const std::string_view payload = text.substr(payload_offset, payload_size);
    auto payload_inspection = inspect_redacted_export(payload);
    if (!payload_inspection) return payload_inspection.status();
    auto actual_digest = sodium.hash(
        kBundleDomain,
        std::span<const std::uint8_t>{
            reinterpret_cast<const std::uint8_t *>(payload.data()),
            payload.size()});
    if (!actual_digest || !security::constant_time_equal(
            actual_digest.value(), parsed_digest.value())) {
        return Status{ErrorCode::protocol_error,
                      "diagnostics bundle payload digest is invalid"};
    }
    BundleInspection inspection;
    inspection.product_version = version.value();
    inspection.product_revision = revision.value();
    inspection.payload_digest = parsed_digest.value();
    inspection.payload = payload_inspection.value();
    return inspection;
}

std::string render_bundle_inspection(const BundleInspection &inspection) {
    std::ostringstream output;
    output << "iotox-diagnostics-inspection-v1\n"
           << "decision=valid-content-free-bundle\n"
           << "product-version=" << inspection.product_version << '\n'
           << "product-revision=" << inspection.product_revision << '\n'
           << "payload-digest=" << security::hex(inspection.payload_digest)
           << '\n'
           << "record-count=" << inspection.payload.record_count << '\n'
           << "evicted-records=" << inspection.payload.evicted_records << '\n'
           << "export-omitted-records="
           << inspection.payload.export_omitted_records << '\n'
           << "high-sequence=" << inspection.payload.high_sequence << '\n'
           << "recorder-write-failures="
           << inspection.payload.recorder_write_failures << '\n';
    if (inspection.payload.namespace_health_present) {
        const NamespaceHealthExport &health =
            inspection.payload.namespace_health;
        output << "namespace-health=aggregated-content-free\n"
               << "namespace-health-total=" << health.total_namespaces
               << '\n'
               << "namespace-health-verified=" << health.verified_records
               << '\n'
               << "namespace-health-green=" << health.green_namespaces
               << '\n'
               << "namespace-health-yellow=" << health.yellow_namespaces
               << '\n'
               << "namespace-health-red=" << health.red_namespaces << '\n'
               << "namespace-health-absent=" << health.absent_records
               << '\n'
               << "namespace-health-invalid=" << health.invalid_records
               << '\n'
               << "namespace-health-rollback-witness=0\n"
               << "namespace-health-backup-certified=0\n";
    } else {
        output << "namespace-health=absent-legacy-bundle\n";
    }
    if (inspection.payload.host_capabilities_present) {
        const HostCapabilitiesExport &host =
            inspection.payload.host_capabilities;
        output << "host-capabilities=normalized-passive\n"
               << "host-capabilities-pidfd=" << host_grade_name(host.pidfd)
               << '\n'
               << "host-capabilities-seccomp="
               << host_grade_name(host.seccomp) << '\n'
               << "host-capabilities-mdwe=" << host_grade_name(host.mdwe)
               << '\n'
               << "host-capabilities-landlock="
               << host_grade_name(host.landlock) << '\n'
               << "host-capabilities-landlock-abi=" << host.landlock_abi
               << '\n'
               << "host-capabilities-privilege-escalation="
               << privilege_grade_name(host.privilege_escalation) << '\n'
               << "host-capabilities-sudo=" << sudo_grade_name(host.sudo)
               << '\n'
               << "host-capabilities-cgroup-v2="
               << cgroup_grade_name(host.cgroup_v2) << '\n';
    } else {
        output << "host-capabilities=absent-legacy-bundle\n";
    }
    output << "share-review=contains-closed-metadata-but-correlates-config-and-activity\n";
    return output.str();
}

std::string_view to_string(EventClass value) noexcept {
    switch (value) {
        case EventClass::security_ready: return "security-ready";
        case EventClass::agent_running: return "agent-running";
        case EventClass::transport_state: return "transport-state";
        case EventClass::authority_state: return "authority-state";
        case EventClass::sync_state: return "sync-state";
        case EventClass::ratox_state: return "ratox-state";
        case EventClass::resource_pressure: return "resource-pressure";
        case EventClass::projection_failure: return "projection-failure";
        case EventClass::agent_stopping: return "agent-stopping";
        case EventClass::agent_failed: return "agent-failed";
        case EventClass::current_snapshot: return "current-snapshot";
    }
    return "unknown";
}

std::string_view to_string(AgentPhase value) noexcept {
    switch (value) {
        case AgentPhase::starting: return "starting";
        case AgentPhase::running: return "running";
        case AgentPhase::stopping: return "stopping";
        case AgentPhase::stopped: return "stopped";
        case AgentPhase::failed: return "failed";
    }
    return "unknown";
}

std::string_view to_string(NetworkClass value) noexcept {
    switch (value) {
        case NetworkClass::tox_native: return "tox-native";
        case NetworkClass::tox_tor: return "tox-tor";
        case NetworkClass::tox_i2p: return "tox-i2p";
        case NetworkClass::tox_i2p_construction:
            return "tox-i2p-construction";
    }
    return "unknown";
}

std::filesystem::path default_recorder_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) return {};
    std::filesystem::path parent = tox_savedata_path.parent_path();
    if (parent.empty()) parent = ".";
    std::filesystem::path name = tox_savedata_path.filename();
    name += ".flight";
    return parent / ".iotox-diagnostics" / name;
}

}  // namespace iotox::diagnostics
