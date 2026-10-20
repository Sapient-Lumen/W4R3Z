#include "test_harness.hpp"

#include "iotox/diagnostics.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"

#include <array>
#include <filesystem>
#include <limits>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-diagnostics-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data()); created != nullptr) {
            root_ = created;
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

iotox::diagnostics::Observation observation(std::uint64_t value) {
    iotox::diagnostics::Observation result;
    result.event = value % 2U == 0U
        ? iotox::diagnostics::EventClass::transport_state
        : iotox::diagnostics::EventClass::ratox_state;
    result.phase = iotox::diagnostics::AgentPhase::running;
    result.network = iotox::diagnostics::NetworkClass::tox_native;
    result.flags = iotox::diagnostics::kTransportOnline |
        iotox::diagnostics::kAuthorityInitialized;
    result.configuration_commitment.fill(static_cast<std::uint8_t>(value));
    result.peer_count = value;
    result.authorized_peer_count = value / 2U;
    result.pending_command_count = value + 1U;
    result.active_file_transfer_count = value + 2U;
    result.ratox_live_session_count = value + 3U;
    result.ratox_admission_rejections = value + 4U;
    result.transport_dropped_events = value + 5U;
    result.ratox_dropped_events = value + 6U;
    result.sync_work_admitted = value + 7U;
    result.sync_work_rejected = value + 8U;
    return result;
}

}  // namespace

IOTOX_TEST("diagnostic recorder signs and bounds one canonical tail") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory directory;
    const auto identity_path = directory.root() / "device.identity";
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::diagnostics::Recorder::Config config;
    config.path = directory.root() / "diagnostics.store";
    config.maximum_records = 16U;
    auto recorder = iotox::diagnostics::Recorder::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(recorder.ok(), recorder.status().message());
    for (std::uint64_t index = 1U; index <= 20U; ++index) {
        const iotox::Status stored = recorder.value()->record(
            observation(index));
        IOTOX_CHECK_MSG(stored.ok(), stored.message());
    }
    const auto snapshot = recorder.value()->snapshot();
    IOTOX_CHECK(snapshot.high_sequence == 20U);
    IOTOX_CHECK(snapshot.evicted_records == 4U);
    IOTOX_CHECK(snapshot.records.size() == 16U);
    IOTOX_CHECK(snapshot.records.front().sequence == 5U);
    IOTOX_CHECK(snapshot.records.back().observation.peer_count == 20U);
    auto invalid = observation(21U);
    invalid.event = static_cast<iotox::diagnostics::EventClass>(255U);
    IOTOX_CHECK(!recorder.value()->record(invalid).ok());
    invalid = observation(21U);
    invalid.status = static_cast<iotox::ErrorCode>(256);
    IOTOX_CHECK(!recorder.value()->record(invalid).ok());

    auto reopened = iotox::diagnostics::Recorder::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().records == snapshot.records);

    auto bytes = iotox::StateStore::read(config.path);
    IOTOX_CHECK(bytes.ok() && bytes.value().size() > 100U);
    bytes.value()[40U] ^= 0x01U;
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    config.path, bytes.value()).ok());
    IOTOX_CHECK(!iotox::diagnostics::Recorder::open(
                     config, identity.value(), sodium.value()).ok());
}

IOTOX_TEST("diagnostics bundle is content-free canonical and tamper evident") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    iotox::diagnostics::Recorder::Config config;
    config.path = directory.root() / "diagnostics.store";
    config.maximum_records = 16U;
    auto recorder = iotox::diagnostics::Recorder::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(recorder.ok());
    IOTOX_CHECK(recorder.value()->record(observation(7U)).ok());
    auto exported = recorder.value()->redacted_export(observation(8U));
    IOTOX_CHECK_MSG(exported.ok(), exported.status().message());
    const std::array<std::string, 3U> forbidden_values{
        "PRIVATE-COMMAND-CONTENT", "/home/operator/secret",
        identity.value().public_key_hex()};
    for (const std::string &forbidden : forbidden_values) {
        IOTOX_CHECK(exported.value().find(forbidden) == std::string::npos);
    }
    auto bundle = iotox::diagnostics::make_bundle(
        exported.value(), "0.48.0", "rev0048", sodium.value());
    IOTOX_CHECK_MSG(bundle.ok(), bundle.status().message());
    auto inspected = iotox::diagnostics::inspect_bundle(
        bundle.value(), sodium.value());
    IOTOX_CHECK_MSG(inspected.ok(), inspected.status().message());
    IOTOX_CHECK(inspected.value().payload.record_count == 1U);
    IOTOX_CHECK(inspected.value().payload.high_sequence == 1U);
    IOTOX_CHECK(iotox::diagnostics::render_bundle_inspection(
                    inspected.value()).find(
                    "decision=valid-content-free-bundle\n") !=
                std::string::npos);

    // A maximum-size local ring remains exportable even when every decimal
    // counter has its longest representation. The export explicitly reports
    // the oldest locally retained records omitted to honor the fixed control
    // and bundle byte ceilings.
    config.maximum_records = 256U;
    auto wide_recorder = iotox::diagnostics::Recorder::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(wide_recorder.ok());
    auto wide = observation(std::numeric_limits<std::uint64_t>::max());
    wide.peer_count = std::numeric_limits<std::uint64_t>::max();
    wide.authorized_peer_count = std::numeric_limits<std::uint64_t>::max();
    wide.pending_command_count = std::numeric_limits<std::uint64_t>::max();
    wide.active_file_transfer_count = std::numeric_limits<std::uint64_t>::max();
    wide.ratox_live_session_count = std::numeric_limits<std::uint64_t>::max();
    wide.ratox_admission_rejections = std::numeric_limits<std::uint64_t>::max();
    wide.transport_dropped_events = std::numeric_limits<std::uint64_t>::max();
    wide.ratox_dropped_events = std::numeric_limits<std::uint64_t>::max();
    wide.sync_work_admitted = std::numeric_limits<std::uint64_t>::max();
    wide.sync_work_rejected = std::numeric_limits<std::uint64_t>::max();
    for (std::size_t index = 1U; index < 256U; ++index) {
        IOTOX_CHECK(wide_recorder.value()->record(wide).ok());
    }
    auto bounded_export = wide_recorder.value()->redacted_export(wide);
    IOTOX_CHECK(bounded_export.ok());
    IOTOX_CHECK(bounded_export.value().size() <=
                iotox::diagnostics::kMaximumRedactedExportBytes);
    auto bounded_summary = iotox::diagnostics::inspect_redacted_export(
        bounded_export.value());
    IOTOX_CHECK(bounded_summary.ok());
    IOTOX_CHECK(bounded_summary.value().export_omitted_records > 0U);
    IOTOX_CHECK(bounded_summary.value().record_count +
                    bounded_summary.value().export_omitted_records ==
                256U);

    bundle.value()[bundle.value().size() - 20U] ^= 0x01U;
    IOTOX_CHECK(!iotox::diagnostics::inspect_bundle(
                     bundle.value(), sodium.value()).ok());
}

IOTOX_TEST("diagnostics v3 joins normalized health and host capabilities") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    iotox::diagnostics::Recorder::Config config;
    config.path = directory.root() / "diagnostics.store";
    config.maximum_records = 16U;
    auto recorder = iotox::diagnostics::Recorder::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(recorder.ok());

    iotox::diagnostics::NamespaceHealthExport health;
    health.total_namespaces = 3U;
    health.verified_records = 2U;
    health.absent_records = 1U;
    health.green_namespaces = 1U;
    health.red_namespaces = 1U;
    health.stale_policy_namespaces = 1U;
    health.complete_custody_namespaces = 1U;
    health.partial_custody_namespaces = 1U;
    health.conflict_namespaces = 1U;
    health.missing_objects = 2U;
    health.missing_bytes = 9U;
    health.automation_stalled_namespaces = 1U;
    health.source_exhausted_namespaces = 1U;
    health.source_absent_results = 4U;
    health.source_unavailable_results = 5U;
    health.maximum_automation_failure_streak = 6U;
    iotox::diagnostics::HostCapabilitiesExport host;
    host.pidfd = iotox::diagnostics::HostCapabilityGrade::live_proved;
    host.seccomp = iotox::diagnostics::HostCapabilityGrade::available;
    host.mdwe = iotox::diagnostics::HostCapabilityGrade::available;
    host.landlock = iotox::diagnostics::HostCapabilityGrade::available;
    host.landlock_abi = 10U;
    host.privilege_escalation =
        iotox::diagnostics::PrivilegeCapabilityGrade::host_policy_pending;
    host.sudo = iotox::diagnostics::SudoCapabilityGrade::setuid_root;
    host.cgroup_v2 = iotox::diagnostics::CgroupCapabilityGrade::delegated;
    host.cgroup_controller_mask = 0x1fU;
    host.cgroup_interface_available_mask = 0xfffU;
    host.cgroup_interface_readable_mask = 0xfffU;
    host.cgroup_interface_writable_mask = 0x0ffU;
    auto exported = recorder.value()->redacted_export(
        observation(8U), 0U, health, host);
    IOTOX_CHECK_MSG(exported.ok(), exported.status().message());
    IOTOX_CHECK(exported.value().starts_with(
        "iotox-diagnostics-redacted-v3\n"));
    IOTOX_CHECK(exported.value().find("private-namespace-name") ==
                std::string::npos);
    auto inspected = iotox::diagnostics::inspect_redacted_export(
        exported.value());
    IOTOX_CHECK_MSG(inspected.ok(), inspected.status().message());
    IOTOX_CHECK(inspected.value().namespace_health_present);
    IOTOX_CHECK(inspected.value().namespace_health == health);
    IOTOX_CHECK(inspected.value().host_capabilities_present);
    IOTOX_CHECK(inspected.value().host_capabilities == host);

    auto bundle = iotox::diagnostics::make_bundle(
        exported.value(), "0.48.0", "rev0048", sodium.value());
    IOTOX_CHECK(bundle.ok());
    auto bundle_inspection = iotox::diagnostics::inspect_bundle(
        bundle.value(), sodium.value());
    IOTOX_CHECK(bundle_inspection.ok());
    const std::string rendered = iotox::diagnostics::render_bundle_inspection(
        bundle_inspection.value());
    IOTOX_CHECK(rendered.find("namespace-health=aggregated-content-free\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("namespace-health-red=1\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("namespace-health-backup-certified=0\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("host-capabilities=normalized-passive\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("host-capabilities-landlock-abi=10\n") !=
                std::string::npos);

    auto inconsistent = health;
    ++inconsistent.total_namespaces;
    IOTOX_CHECK(!recorder.value()
                     ->redacted_export(observation(8U), 0U, inconsistent,
                                       host)
                     .ok());

    auto inconsistent_host = host;
    inconsistent_host.cgroup_interface_readable_mask = 1U << 15U;
    IOTOX_CHECK(!recorder.value()
                     ->redacted_export(observation(8U), 0U, health,
                                       inconsistent_host)
                     .ok());

    // Standalone inspection remains compatible with v2 health payloads and
    // v1 flight-only payloads emitted before host aggregation existed.
    const std::size_t host_start = exported.value().find(
        "host-capabilities-probe=");
    IOTOX_CHECK(host_start != std::string::npos);
    std::string version_two = exported.value().substr(0U, host_start);
    version_two.replace(
        0U, std::string("iotox-diagnostics-redacted-v3").size(),
        "iotox-diagnostics-redacted-v2");
    auto version_two_inspection =
        iotox::diagnostics::inspect_redacted_export(version_two);
    IOTOX_CHECK_MSG(version_two_inspection.ok(),
                    version_two_inspection.status().message());
    IOTOX_CHECK(version_two_inspection.value().namespace_health_present);
    IOTOX_CHECK(!version_two_inspection.value().host_capabilities_present);
    const std::size_t health_start = exported.value().find(
        "namespace-health-verification=");
    IOTOX_CHECK(health_start != std::string::npos);
    std::string legacy = exported.value().substr(0U, health_start);
    legacy.replace(0U, std::string("iotox-diagnostics-redacted-v3").size(),
                   "iotox-diagnostics-redacted-v1");
    auto legacy_inspection =
        iotox::diagnostics::inspect_redacted_export(legacy);
    IOTOX_CHECK_MSG(legacy_inspection.ok(),
                    legacy_inspection.status().message());
    IOTOX_CHECK(!legacy_inspection.value().namespace_health_present);
}
