#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::diagnostics {

inline constexpr std::size_t kDefaultMaximumRecords = 128U;
inline constexpr std::size_t kMinimumMaximumRecords = 16U;
inline constexpr std::size_t kMaximumMaximumRecords = 256U;
inline constexpr std::size_t kMaximumRedactedExportBytes = 48U * 1024U;
inline constexpr std::size_t kMaximumBundleBytes = 64U * 1024U;

enum class EventClass : std::uint8_t {
    security_ready = 1U,
    agent_running = 2U,
    transport_state = 3U,
    authority_state = 4U,
    sync_state = 5U,
    ratox_state = 6U,
    resource_pressure = 7U,
    projection_failure = 8U,
    agent_stopping = 9U,
    agent_failed = 10U,
    current_snapshot = 11U,
};

enum class AgentPhase : std::uint8_t {
    starting = 1U,
    running = 2U,
    stopping = 3U,
    stopped = 4U,
    failed = 5U,
};

enum class NetworkClass : std::uint8_t {
    tox_native = 1U,
    tox_tor = 2U,
    tox_i2p = 3U,
    tox_i2p_construction = 4U,
};

inline constexpr std::uint32_t kTransportOnline = 1U << 0U;
inline constexpr std::uint32_t kAuthorityInitialized = 1U << 1U;
inline constexpr std::uint32_t kSyncEnabled = 1U << 2U;
inline constexpr std::uint32_t kRatoxEnabled = 1U << 3U;
inline constexpr std::uint32_t kPressureAdmissionClosed = 1U << 4U;
inline constexpr std::uint32_t kCommandClockTrusted = 1U << 5U;
inline constexpr std::uint32_t kRouteWorkersEnabled = 1U << 6U;
inline constexpr std::uint32_t kSignedUpdatesEnabled = 1U << 7U;
inline constexpr std::uint32_t kKnownObservationFlags =
    kTransportOnline | kAuthorityInitialized | kSyncEnabled | kRatoxEnabled |
    kPressureAdmissionClosed | kCommandClockTrusted | kRouteWorkersEnabled |
    kSignedUpdatesEnabled;

struct Observation {
    EventClass event{EventClass::security_ready};
    ErrorCode status{ErrorCode::ok};
    AgentPhase phase{AgentPhase::starting};
    NetworkClass network{NetworkClass::tox_native};
    std::uint32_t flags{0U};
    security::Digest configuration_commitment{};
    std::uint64_t peer_count{0U};
    std::uint64_t authorized_peer_count{0U};
    std::uint64_t pending_command_count{0U};
    std::uint64_t active_file_transfer_count{0U};
    std::uint64_t ratox_live_session_count{0U};
    std::uint64_t ratox_admission_rejections{0U};
    std::uint64_t transport_dropped_events{0U};
    std::uint64_t ratox_dropped_events{0U};
    std::uint64_t sync_work_admitted{0U};
    std::uint64_t sync_work_rejected{0U};

    [[nodiscard]] bool operator==(const Observation &) const = default;
};

struct Record {
    std::uint64_t sequence{0U};
    Observation observation;

    [[nodiscard]] bool operator==(const Record &) const = default;
};

struct Snapshot {
    std::uint64_t mutation{0U};
    std::uint64_t high_sequence{0U};
    std::uint64_t evicted_records{0U};
    std::size_t maximum_records{kDefaultMaximumRecords};
    std::vector<Record> records;
};

// Aggregate only. A shareable diagnostic must not disclose namespace names,
// paths, membership keys, content digests, or stable per-namespace handles.
struct NamespaceHealthExport {
    std::uint64_t total_namespaces{0U};
    std::uint64_t verified_records{0U};
    std::uint64_t absent_records{0U};
    std::uint64_t invalid_records{0U};
    std::uint64_t green_namespaces{0U};
    std::uint64_t yellow_namespaces{0U};
    std::uint64_t red_namespaces{0U};
    std::uint64_t stale_policy_namespaces{0U};
    std::uint64_t complete_custody_namespaces{0U};
    std::uint64_t partial_custody_namespaces{0U};
    std::uint64_t conflict_namespaces{0U};
    std::uint64_t missing_objects{0U};
    std::uint64_t missing_bytes{0U};
    std::uint64_t automation_stalled_namespaces{0U};
    std::uint64_t store_pressure_namespaces{0U};
    std::uint64_t source_exhausted_namespaces{0U};
    std::uint64_t source_absent_results{0U};
    std::uint64_t source_unavailable_results{0U};
    std::uint64_t maximum_automation_failure_streak{0U};

    [[nodiscard]] bool operator==(const NamespaceHealthExport &) const =
        default;
};

enum class HostCapabilityGrade : std::uint8_t {
    unavailable = 0U,
    available = 1U,
    live_proved = 2U,
    probe_denied = 3U,
};

enum class PrivilegeCapabilityGrade : std::uint8_t {
    unavailable = 0U,
    blocked = 1U,
    host_policy_pending = 2U,
    probe_denied = 3U,
};

enum class SudoCapabilityGrade : std::uint8_t {
    unavailable = 0U,
    setuid_root = 1U,
    file_capabilities = 2U,
};

enum class CgroupCapabilityGrade : std::uint8_t {
    unavailable = 0U,
    available = 1U,
    delegated = 2U,
};

struct HostCapabilitiesExport {
    HostCapabilityGrade pidfd{HostCapabilityGrade::unavailable};
    HostCapabilityGrade seccomp{HostCapabilityGrade::unavailable};
    HostCapabilityGrade mdwe{HostCapabilityGrade::unavailable};
    HostCapabilityGrade landlock{HostCapabilityGrade::unavailable};
    std::uint32_t landlock_abi{0U};
    PrivilegeCapabilityGrade privilege_escalation{
        PrivilegeCapabilityGrade::unavailable};
    SudoCapabilityGrade sudo{SudoCapabilityGrade::unavailable};
    CgroupCapabilityGrade cgroup_v2{CgroupCapabilityGrade::unavailable};
    std::uint32_t cgroup_controller_mask{0U};
    std::uint32_t cgroup_unknown_controllers{0U};
    std::uint32_t cgroup_interface_available_mask{0U};
    std::uint32_t cgroup_interface_readable_mask{0U};
    std::uint32_t cgroup_interface_writable_mask{0U};

    [[nodiscard]] bool operator==(const HostCapabilitiesExport &) const =
        default;
};

class Recorder {
  public:
    struct Config {
        std::filesystem::path path;
        std::size_t maximum_records{kDefaultMaximumRecords};
    };

    [[nodiscard]] static Result<std::unique_ptr<Recorder>> open(
        Config config, const security::DeviceIdentity &identity,
        const security::Sodium &sodium);

    [[nodiscard]] Status record(const Observation &observation);
    [[nodiscard]] Snapshot snapshot() const;
    [[nodiscard]] Result<std::string> redacted_export(
        const Observation &current,
        std::uint64_t recorder_write_failures = 0U,
        const NamespaceHealthExport &namespace_health = {},
        const HostCapabilitiesExport &host_capabilities = {}) const;

  private:
    Recorder(Config config, const security::DeviceIdentity &identity,
             const security::Sodium &sodium, Snapshot state);

    Config config_;
    const security::DeviceIdentity *identity_{nullptr};
    const security::Sodium *sodium_{nullptr};
    mutable std::mutex mutex_;
    Snapshot state_;
};

struct ExportSummary {
    std::uint64_t mutation{0U};
    std::uint64_t high_sequence{0U};
    std::uint64_t evicted_records{0U};
    std::uint64_t export_omitted_records{0U};
    std::size_t record_count{0U};
    std::size_t maximum_records{0U};
    std::uint64_t recorder_write_failures{0U};
    security::Digest current_configuration_commitment{};
    bool namespace_health_present{false};
    NamespaceHealthExport namespace_health;
    bool host_capabilities_present{false};
    HostCapabilitiesExport host_capabilities;
};

[[nodiscard]] Result<ExportSummary> inspect_redacted_export(
    std::string_view text);

struct BundleInspection {
    std::string product_version;
    std::string product_revision;
    security::Digest payload_digest{};
    ExportSummary payload;
};

[[nodiscard]] Result<std::vector<std::uint8_t>> make_bundle(
    std::string_view redacted_export, std::string_view product_version,
    std::string_view product_revision, const security::Sodium &sodium);
[[nodiscard]] Result<BundleInspection> inspect_bundle(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] std::string render_bundle_inspection(
    const BundleInspection &inspection);

[[nodiscard]] std::string_view to_string(EventClass value) noexcept;
[[nodiscard]] std::string_view to_string(AgentPhase value) noexcept;
[[nodiscard]] std::string_view to_string(NetworkClass value) noexcept;

[[nodiscard]] std::filesystem::path default_recorder_path(
    const std::filesystem::path &tox_savedata_path);

}  // namespace iotox::diagnostics
