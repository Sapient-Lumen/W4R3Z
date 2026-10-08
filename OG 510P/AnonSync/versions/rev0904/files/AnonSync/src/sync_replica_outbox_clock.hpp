#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaNanosecondsPerSecond =
    1000000000ULL;
inline constexpr std::uint64_t kSyncReplicaOutboxDefaultClockMaxUncertaintyNs =
    5ULL * kSyncReplicaNanosecondsPerSecond;
inline constexpr std::uint64_t kSyncReplicaOutboxDefaultClockMaxForwardStepSeconds =
    5ULL * 60ULL;
inline constexpr std::uint64_t kSyncReplicaOutboxDefaultClockMaxRealtimeLagSeconds =
    5ULL * 60ULL;
inline constexpr std::uint64_t kSyncReplicaOutboxClockHardMaxUncertaintyNs =
    60ULL * kSyncReplicaNanosecondsPerSecond;
inline constexpr std::uint64_t kSyncReplicaOutboxClockHardMaxForwardStepSeconds =
    60ULL * 60ULL;
inline constexpr std::uint64_t kSyncReplicaOutboxClockHardMaxRealtimeLagSeconds =
    60ULL * 60ULL;

enum class SyncReplicaOutboxClockSynchronization : std::uint8_t {
    Unknown = 0U,
    Synchronized = 1U,
    Unsynchronized = 2U,
};

enum class SyncReplicaOutboxClockHealth : std::uint8_t {
    Uninitialized = 0U,
    Healthy = 1U,
    Quarantined = 2U,
};

enum class SyncReplicaOutboxClockAnomaly : std::uint8_t {
    None = 0U,
    LegacyUnbound = 1U,
    Unsynchronized = 2U,
    ExcessiveUncertainty = 3U,
    SourceChanged = 4U,
    BootChanged = 5U,
    TimeNamespaceChanged = 6U,
    BoottimeRollback = 7U,
    RealtimeRollback = 8U,
    ForwardStep = 9U,
    RealtimeLag = 10U,
    SynchronizationUnknown = 11U,
};

struct SyncReplicaOutboxClockObservation final {
    std::string source_id;
    std::string boot_id;
    std::string time_namespace_id;
    std::uint64_t realtime_ns = 0;
    std::uint64_t boottime_ns = 0;
    std::uint64_t uncertainty_ns = 0;
    SyncReplicaOutboxClockSynchronization synchronization =
        SyncReplicaOutboxClockSynchronization::Unknown;

    bool operator==(const SyncReplicaOutboxClockObservation&) const = default;
};

struct SyncReplicaOutboxClockPolicy final {
    std::uint64_t max_uncertainty_ns =
        kSyncReplicaOutboxDefaultClockMaxUncertaintyNs;
    std::uint64_t max_forward_step_seconds =
        kSyncReplicaOutboxDefaultClockMaxForwardStepSeconds;
    // A nondecreasing wall clock can still stall while boot-relative time moves.
    // Bound that lag so leases and retries cannot be postponed indefinitely.
    std::uint64_t max_realtime_lag_seconds =
        kSyncReplicaOutboxDefaultClockMaxRealtimeLagSeconds;

    bool operator==(const SyncReplicaOutboxClockPolicy&) const = default;
};

// The first accepted observation after initialization or explicit recovery is
// a cumulative drift anchor.  Keeping this anchor separate from the latest
// accepted observation prevents a sequence of individually-small wall-clock
// steps from laundering an unbounded aggregate jump.
struct SyncReplicaOutboxClockAnchor final {
    std::uint64_t realtime_ns = 0;
    std::uint64_t boottime_ns = 0;
    std::uint64_t uncertainty_ns = 0;

    bool operator==(const SyncReplicaOutboxClockAnchor&) const = default;
};

struct SyncReplicaOutboxClockState final {
    SyncReplicaOutboxClockHealth health =
        SyncReplicaOutboxClockHealth::Uninitialized;
    std::uint64_t high_water_epoch = 0;
    std::uint64_t observation_generation = 0;
    std::uint64_t recovery_generation = 0;
    std::optional<SyncReplicaOutboxClockAnchor> anchor;
    std::optional<SyncReplicaOutboxClockObservation> accepted;
    SyncReplicaOutboxClockAnomaly anomaly =
        SyncReplicaOutboxClockAnomaly::None;
    std::optional<SyncReplicaOutboxClockObservation> rejected;

    bool operator==(const SyncReplicaOutboxClockState&) const = default;
};

enum class SyncReplicaOutboxClockObservationOutcome : std::uint8_t {
    Accepted = 1U,
    Quarantined = 2U,
    AlreadyQuarantined = 3U,
};

struct SyncReplicaOutboxClockObservationResult final {
    SyncReplicaOutboxClockObservationOutcome outcome =
        SyncReplicaOutboxClockObservationOutcome::AlreadyQuarantined;
    SyncReplicaOutboxClockState state;
    std::uint64_t usable_epoch = 0;
    bool changed = false;
};

void validate_sync_replica_outbox_clock_policy_or_throw(
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label);
void validate_sync_replica_outbox_clock_observation_or_throw(
    const SyncReplicaOutboxClockObservation& observation,
    const std::string& label);
void validate_sync_replica_outbox_clock_state_or_throw(
    const SyncReplicaOutboxClockState& state,
    const std::string& label);
void validate_sync_replica_outbox_clock_state_against_policy_or_throw(
    const SyncReplicaOutboxClockState& state,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label);

[[nodiscard]] SyncReplicaOutboxClockObservationResult
observe_sync_replica_outbox_clock_or_throw(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label);

[[nodiscard]] SyncReplicaOutboxClockState
recover_sync_replica_outbox_clock_or_throw(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    std::uint64_t expected_observation_generation,
    const std::string& label);

[[nodiscard]] SyncReplicaOutboxClockState
make_legacy_unbound_sync_replica_outbox_clock_state_or_throw(
    std::uint64_t high_water_epoch,
    const std::string& label);

inline constexpr std::size_t kSyncReplicaOutboxClockStateMaxCanonicalBytes =
    512U;

[[nodiscard]] std::string
encode_sync_replica_outbox_clock_state_canonical_or_throw(
    const SyncReplicaOutboxClockState& state,
    const std::string& label);
[[nodiscard]] SyncReplicaOutboxClockState
decode_sync_replica_outbox_clock_state_canonical_or_throw(
    std::string_view bytes,
    const std::string& label);

[[nodiscard]] std::string_view sync_replica_outbox_clock_anomaly_name(
    SyncReplicaOutboxClockAnomaly anomaly) noexcept;

class SyncReplicaOutboxClockSource {
public:
    virtual ~SyncReplicaOutboxClockSource() = default;
    [[nodiscard]] virtual SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string& label) = 0;
};

[[nodiscard]] std::unique_ptr<SyncReplicaOutboxClockSource>
make_system_sync_replica_outbox_clock_source();

// Explicit deployment trust boundary for sandboxes and containers where the
// kernel clock may be externally disciplined but adjtimex or the calling
// thread's time-namespace identity is intentionally hidden. The authority ID
// and claimed uncertainty are operator assertions, not measurements or
// cryptographic attestations. The resulting source still binds exact boot
// identity, the best available time-namespace observation, bracketed realtime/
// boottime samples, cumulative drift checks, sticky quarantine, and explicit
// recovery. Callers must not select this profile implicitly.
struct SyncReplicaOperatorTrustedClockProfile final {
    std::string authority_id;
    std::uint64_t claimed_uncertainty_ns = 0U;

    bool operator==(
        const SyncReplicaOperatorTrustedClockProfile&) const = default;
};

[[nodiscard]] std::unique_ptr<SyncReplicaOutboxClockSource>
make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
    SyncReplicaOperatorTrustedClockProfile profile);

}  // namespace anonsync
