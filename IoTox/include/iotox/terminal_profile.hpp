#pragma once

#include "iotox/interactive.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <shared_mutex>
#include <span>
#include <string>
#include <vector>

namespace iotox::terminal {

inline constexpr std::size_t kMaximumProfiles = 64U;
inline constexpr std::size_t kMaximumBindings = 256U;
inline constexpr std::size_t kMaximumArguments = 32U;
inline constexpr std::size_t kMaximumEnvironmentEntries = 64U;
inline constexpr std::size_t kMaximumProfileFileBytes = 64U * 1024U;
inline constexpr std::size_t kMaximumArgumentBytes = 4096U;
inline constexpr std::size_t kMaximumEnvironmentValueBytes = 4096U;
inline constexpr std::size_t kMaximumResolvedEnvironmentBytes = 32U * 1024U;
inline constexpr std::uint64_t kCgroupMinimumCpuBandwidthMicroseconds = 1000U;
inline constexpr std::uint64_t kCgroupMaximumCpuPeriodMicroseconds = 1000000U;
inline constexpr std::uint64_t kCgroupDefaultCpuPeriodMicroseconds = 100000U;
inline constexpr std::uint16_t kCgroupMaximumPressureBasisPoints = 10000U;
inline constexpr std::uint64_t
    kCgroupPressureTriggerWindowQuantumMicroseconds = 2000000U;
inline constexpr std::uint64_t
    kCgroupMinimumPressureTriggerWindowMicroseconds =
        kCgroupPressureTriggerWindowQuantumMicroseconds;
inline constexpr std::uint64_t
    kCgroupMaximumPressureTriggerWindowMicroseconds = 10000000U;

using PrincipalId = interactive::PrincipalId;
using ExecutableDigest = std::array<std::uint8_t, 32U>;

struct Dimensions {
    std::uint16_t columns{80U};
    std::uint16_t rows{24U};

    [[nodiscard]] bool operator==(const Dimensions &) const = default;
};

struct DimensionPolicy {
    Dimensions minimum{20U, 5U};
    Dimensions initial{80U, 24U};
    Dimensions maximum{512U, 256U};
    bool allow_resize{true};

    [[nodiscard]] bool operator==(const DimensionPolicy &) const = default;
};

enum class IdentityMode : std::uint8_t {
    inherit = 1U,
    exact = 2U,
    // Profile-v6 login identity. Unlike the isolation-oriented `exact` mode,
    // this freezes and restores an account's explicit supplementary groups so
    // an owner shell retains ordinary wheel/device/filesystem membership.
    account = 3U,
};

// Confinement is enforced by the local PTY child immediately before exec.
// `compatibility` omits the syscall filter and exists for decoding canonical
// v1 records. It still receives the common capability/credential/descriptor
// floor. New Profile values default to the reviewed baseline. `strict` is a
// fail-closed Linux contract: unsupported kernel primitives reject the spawn.
enum class ConfinementMode : std::uint8_t {
    compatibility = 1U,
    baseline = 2U,
    strict = 3U,
};

struct IdentityPolicy {
    IdentityMode mode{IdentityMode::inherit};
    std::uint32_t uid{0U};
    std::uint32_t gid{0U};
    bool clear_supplementary_groups{true};
    std::vector<std::uint32_t> supplementary_groups;

    [[nodiscard]] bool operator==(const IdentityPolicy &) const = default;
};

struct ResourceLimits {
    // Zero means the named limit is intentionally not changed by the child.
    // Core dumps are always disabled independently of this structure.
    std::uint64_t cpu_seconds{3600U};
    std::uint64_t address_space_bytes{512U * 1024U * 1024U};
    std::uint64_t file_size_bytes{16U * 1024U * 1024U};
    std::uint64_t open_files{64U};
    std::uint64_t processes{32U};

    [[nodiscard]] bool operator==(const ResourceLimits &) const = default;
};

// Canonical Linux block-device identity used by the cgroup-v2 io controller.
// It is deliberately the numeric identity consumed by io.max, not a path that
// can be rebound through aliases. The tuple is deployment-local and must be
// requalified after block topology or boot-time device numbering changes.
struct CgroupIoDevice {
    std::uint32_t major{0U};
    std::uint32_t minor{0U};

    [[nodiscard]] bool operator==(const CgroupIoDevice &) const = default;
};

// Optional cgroup-v2 resource envelope for one terminal session. The same
// value type represents the administrator-owned host ceiling and local
// profile policy. At admission the two are composed monotonically: the
// stricter value wins for every resource, so a profile can never weaken host
// policy. These values are local and never cross the network.
struct CgroupResourceLimits {
    std::optional<std::uint64_t> maximum_processes;
    // Soft throttle boundary. Crossing memory.high routes allocations through
    // direct reclaim but does not itself invoke the cgroup OOM killer.
    std::optional<std::uint64_t> maximum_memory_high_bytes;
    std::optional<std::uint64_t> maximum_memory_bytes;
    // Zero is a meaningful configured value: disallow swap for the session.
    std::optional<std::uint64_t> maximum_swap_bytes;
    std::optional<std::uint64_t> cpu_quota_microseconds;
    // Absent selects the kernel-standard 100000 microsecond period whenever
    // a quota is configured. A period without a quota is invalid.
    std::optional<std::uint64_t> cpu_period_microseconds;
    // I/O ceilings are one fail-closed policy for one exact block device.
    // Every configured ceiling must be positive. A device without a ceiling,
    // or a ceiling without a device, is invalid. Host/profile composition
    // requires matching device identity and selects the stricter ceiling for
    // each configured dimension.
    std::optional<CgroupIoDevice> io_device;
    std::optional<std::uint64_t> maximum_io_read_bytes_per_second;
    std::optional<std::uint64_t> maximum_io_write_bytes_per_second;
    std::optional<std::uint64_t> maximum_io_read_operations_per_second;
    std::optional<std::uint64_t> maximum_io_write_operations_per_second;

    [[nodiscard]] bool empty() const noexcept {
        return !maximum_processes.has_value() &&
               !maximum_memory_high_bytes.has_value() &&
               !maximum_memory_bytes.has_value() &&
               !maximum_swap_bytes.has_value() &&
               !cpu_quota_microseconds.has_value() &&
               !cpu_period_microseconds.has_value() &&
               !io_device.has_value() &&
               !maximum_io_read_bytes_per_second.has_value() &&
               !maximum_io_write_bytes_per_second.has_value() &&
               !maximum_io_read_operations_per_second.has_value() &&
               !maximum_io_write_operations_per_second.has_value();
    }

    [[nodiscard]] bool operator==(const CgroupResourceLimits &) const = default;
};

// Optional administrator-owned aggregate reservation ceiling across all live
// local Ratox PTY sessions. A configured dimension requires every admitted
// session to carry the corresponding finite CgroupResourceLimits value. The
// exact per-session maxima are reserved before cgroup or process mutation and
// released only after proved complete terminal teardown; uncertain post-spawn
// cleanup retains the charge until restart recovery.
//
// Aggregate CPU bandwidth is one exact rational ceiling. The quota is counted
// at `cpu_period_microseconds`, or at the kernel-standard 100000 microsecond
// period when the period is absent. Every admitted session CPU ratio must be
// exactly representable at that accounting period; ratios requiring rounding
// fail closed rather than consuming an approximate scalar charge.
struct CgroupAggregateLimits {
    std::optional<std::uint64_t> maximum_reserved_processes;
    std::optional<std::uint64_t> maximum_reserved_memory_bytes;
    // Zero is meaningful: every admitted session must explicitly forbid swap.
    std::optional<std::uint64_t> maximum_reserved_swap_bytes;
    std::optional<std::uint64_t> maximum_reserved_cpu_quota_microseconds;
    // Absent selects kCgroupDefaultCpuPeriodMicroseconds whenever an aggregate
    // CPU quota is configured. A period without a quota is invalid.
    std::optional<std::uint64_t> cpu_period_microseconds;

    [[nodiscard]] bool empty() const noexcept {
        return !maximum_reserved_processes.has_value() &&
               !maximum_reserved_memory_bytes.has_value() &&
               !maximum_reserved_swap_bytes.has_value() &&
               !maximum_reserved_cpu_quota_microseconds.has_value() &&
               !cpu_period_microseconds.has_value();
    }

    [[nodiscard]] bool operator==(const CgroupAggregateLimits &) const = default;
};

// Optional host-local admission gate over the delegated cgroup's Pressure
// Stall Information (PSI). Values are exact percentage basis points from the
// kernel's avg10 fields: 1 == 0.01%, 10000 == 100.00%. The gate closes when
// any configured average exceeds its maximum and reopens only after every
// configured average reaches maximum-hysteresis. Optional PSI triggers close
// the same gate asynchronously after the configured cumulative stall time is
// observed inside one common kernel tracking window; reopening is withheld for
// at least that complete window and still requires the avg10 hysteresis test.
// It is host policy only and never crosses the Ratox wire or profile-record
// boundary.
struct CgroupPressureAdmissionLimits {
    std::optional<std::uint16_t> maximum_cpu_some_average_10_basis_points;
    std::optional<std::uint16_t> maximum_memory_full_average_10_basis_points;
    std::optional<std::uint16_t> maximum_io_full_average_10_basis_points;
    std::uint16_t hysteresis_basis_points{0U};
    std::optional<std::uint64_t> trigger_window_microseconds;
    std::optional<std::uint64_t> cpu_some_trigger_stall_microseconds;
    std::optional<std::uint64_t> memory_full_trigger_stall_microseconds;
    std::optional<std::uint64_t> io_full_trigger_stall_microseconds;

    [[nodiscard]] bool triggers_empty() const noexcept {
        return !cpu_some_trigger_stall_microseconds.has_value() &&
               !memory_full_trigger_stall_microseconds.has_value() &&
               !io_full_trigger_stall_microseconds.has_value();
    }

    [[nodiscard]] bool empty() const noexcept {
        return !maximum_cpu_some_average_10_basis_points.has_value() &&
               !maximum_memory_full_average_10_basis_points.has_value() &&
               !maximum_io_full_average_10_basis_points.has_value() &&
               !trigger_window_microseconds.has_value() && triggers_empty();
    }

    [[nodiscard]] bool operator==(
        const CgroupPressureAdmissionLimits &) const = default;
};

// Exact scalar charge derived from one effective per-session envelope beneath
// an aggregate policy. CPU quota units are normalized to the aggregate period.
struct CgroupAggregateCharge {
    std::uint64_t reserved_processes{0U};
    std::uint64_t reserved_memory_bytes{0U};
    std::uint64_t reserved_swap_bytes{0U};
    std::uint64_t reserved_cpu_quota_microseconds{0U};

    [[nodiscard]] bool empty() const noexcept {
        return reserved_processes == 0U && reserved_memory_bytes == 0U &&
               reserved_swap_bytes == 0U &&
               reserved_cpu_quota_microseconds == 0U;
    }

    [[nodiscard]] bool operator==(const CgroupAggregateCharge &) const = default;
};

struct EnvironmentEntry {
    std::string name;
    std::string value;

    [[nodiscard]] bool operator==(const EnvironmentEntry &) const = default;
};

struct Profile {
    std::string id;
    bool enabled{false};
    // argument[0] is an absolute, no-symlink executable path. V1 native
    // spawning accepts regular ELF executables only; no shell text or remote
    // argument is ever appended.
    std::vector<std::string> arguments;
    // Profile-v7 byte identity. When present, the parent hashes the already
    // validated descriptor that is handed to the PTY child and refuses any
    // mismatch before process creation. A rescue profile additionally pins
    // the exact regular `toybox` ELF below IOTOX_RESCUE_TOOLBOX.
    std::optional<ExecutableDigest> executable_sha256;
    std::optional<ExecutableDigest> toolbox_sha256;
    std::string working_directory;
    std::string terminal_type{"xterm-256color"};
    std::vector<std::string> inherited_environment;
    std::vector<EnvironmentEntry> environment;
    IdentityPolicy identity{};
    ConfinementMode confinement{ConfinementMode::baseline};
    // Profile-v6 owner policy. False is the universal historical/default
    // behavior: the child irrevocably denies exec-time privilege gain. True
    // deliberately permits the non-root shell to use host-authorized set-ID
    // or file-capability helpers such as sudo. It is valid only with
    // compatibility confinement and is rechecked against live process state
    // at spawn.
    bool allow_privilege_escalation{false};
    DimensionPolicy dimensions{};
    ResourceLimits limits{};
    // Profile records v3+ may request a profile-specific cgroup budget. An
    // empty value inherits only the host envelope. A nonempty value requires
    // an explicitly delegated cgroup-v2 root at host activation.
    CgroupResourceLimits cgroup_limits{};
    std::chrono::milliseconds hangup_grace{500};
    std::chrono::milliseconds terminate_grace{1500};
    std::chrono::milliseconds kill_reap_grace{1000};

    [[nodiscard]] bool operator==(const Profile &) const = default;
};

struct Binding {
    PrincipalId principal_id{};
    std::string profile_id;
    bool enabled{true};

    [[nodiscard]] bool operator==(const Binding &) const = default;
};

struct ResolvedProfile {
    Profile profile;
    std::vector<EnvironmentEntry> environment;
    Dimensions accepted_dimensions{};
    std::uint64_t policy_generation{0U};
};

struct RegistrySnapshot {
    std::uint64_t generation{0U};
    std::size_t profiles{0U};
    std::size_t enabled_profiles{0U};
    std::size_t bindings{0U};
    std::size_t enabled_bindings{0U};
};

struct ProfileStoreData {
    std::vector<Profile> profiles;
    std::vector<Binding> bindings;
};

// Canonical semantic commitment to the complete validated store. Historical
// profile encodings are normalized through the current public encoder; paths,
// ownership metadata, and directory iteration order do not enter the digest.
[[nodiscard]] Result<security::Digest> profile_store_digest(
    ProfileStoreData data, const security::Sodium &sodium);

[[nodiscard]] Status validate_dimensions(const Dimensions &dimensions);
[[nodiscard]] Status validate_cgroup_resource_limits(
    const CgroupResourceLimits &limits);
[[nodiscard]] Status validate_cgroup_aggregate_limits(
    const CgroupAggregateLimits &limits);
[[nodiscard]] Status validate_cgroup_pressure_admission_limits(
    const CgroupPressureAdmissionLimits &limits);
// Resolve one effective per-session cgroup envelope into its exact aggregate
// scalar charge. Missing dimensions, a single-session reservation larger than
// the host aggregate, and CPU ratios requiring rounding fail activation.
[[nodiscard]] Result<CgroupAggregateCharge> resolve_cgroup_aggregate_charge(
    const CgroupAggregateLimits &aggregate_limits,
    const CgroupResourceLimits &session_limits);
[[nodiscard]] Status validate_cgroup_aggregate_reservation(
    const CgroupAggregateLimits &aggregate_limits,
    const CgroupResourceLimits &session_limits);
// Compose an administrator-owned host envelope with profile-local policy.
// For scalar maxima the smaller value wins. For CPU bandwidth the lower exact
// quota/period ratio wins without floating-point or overflowing products.
[[nodiscard]] Result<CgroupResourceLimits> compose_cgroup_resource_limits(
    const CgroupResourceLimits &host_limits,
    const CgroupResourceLimits &profile_limits);
[[nodiscard]] Status validate_profile(const Profile &profile);
[[nodiscard]] Status validate_binding(const Binding &binding);
[[nodiscard]] Result<Dimensions> accept_dimensions(
    const DimensionPolicy &policy, const Dimensions &requested);
[[nodiscard]] Result<std::vector<EnvironmentEntry>> resolve_environment(
    const Profile &profile, std::span<const EnvironmentEntry> ambient_environment);
[[nodiscard]] Status validate_resolved_profile(
    const ResolvedProfile &profile);

// Canonical, strict, content-addressable local policy records. The encoder
// emits v7; the decoder also accepts canonical v1..v6 records. V1 maps to the
// explicit `compatibility` confinement mode, v1/v2 map to an empty profile
// cgroup budget, v3 maps to a budget without memory.high, v1-v4 map to no I/O
// policy, and v1-v6 map to no executable-byte pins. Decoders require lowercase hexadecimal,
// exact field order, exactly one trailing LF, and no unassigned fields. These
// bytes never cross the network.
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_profile_record(
    const Profile &profile);
[[nodiscard]] Result<Profile> decode_profile_record(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_binding_record(
    const Binding &binding);
[[nodiscard]] Result<Binding> decode_binding_record(
    std::span<const std::uint8_t> bytes);

// Loads one fail-closed local store:
//   ROOT/profiles/<profile-id>.profile
//   ROOT/bindings/<64-lowercase-hex-principal>.binding
// ROOT and both child directories must be owner-only, no-follow directories;
// every record must be a single-link owner-only regular file. Unexpected names
// or entries fail the complete load.
[[nodiscard]] Result<ProfileStoreData> load_profile_store(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid);

// Owner-local mutation primitives use the same no-symlink descriptor walk and
// ownership checks as load_profile_store. A private temporary inode is synced,
// atomically renamed within the pinned child directory, and followed by a
// directory sync. Each mutation locks the root and validates the complete
// prospective store before changing one record; callers can strictly reread
// afterward to surface any external or durability fault at their policy edge.
[[nodiscard]] Status install_profile_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const Profile &profile);
[[nodiscard]] Status remove_profile_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    std::string_view profile_id);
[[nodiscard]] Status install_binding_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const Binding &binding);
[[nodiscard]] Status remove_binding_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const PrincipalId &principal_id);

class ProfileRegistry {
  public:
    // Replacement is atomic: invalid input leaves the prior generation and
    // records authoritative. Generation exhaustion also fails closed.
    [[nodiscard]] Status replace(ProfileStoreData data);
    [[nodiscard]] Result<ResolvedProfile> resolve(
        const PrincipalId &principal_id, const Dimensions &requested,
        std::span<const EnvironmentEntry> ambient_environment) const;
    [[nodiscard]] RegistrySnapshot snapshot() const;

  private:
    mutable std::shared_mutex mutex_;
    std::vector<Profile> profiles_;
    std::vector<Binding> bindings_;
    std::uint64_t generation_{0U};
};

}  // namespace iotox::terminal
