#include "sync_replica_outbox_clock.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kClockStateDomain =
    "anonsync-sync-replica-outbox-clock-state-v2";

[[nodiscard]] bool is_lower_hex(char value) {
    return (value >= '0' && value <= '9') ||
           (value >= 'a' && value <= 'f');
}

[[nodiscard]] bool source_id_is_valid(std::string_view value) {
    if (value.empty() || value.size() > 64U) return false;
    return std::all_of(value.begin(), value.end(), [](char byte) {
        return (byte >= 'a' && byte <= 'z') ||
               (byte >= '0' && byte <= '9') || byte == '-';
    });
}

[[nodiscard]] bool boot_id_is_valid(std::string_view value) {
    if (value.size() != 36U) return false;
    constexpr std::array<std::size_t, 4> kHyphens{{8U, 13U, 18U, 23U}};
    for (std::size_t index = 0; index < value.size(); ++index) {
        if (std::find(kHyphens.begin(), kHyphens.end(), index) !=
            kHyphens.end()) {
            if (value[index] != '-') return false;
        } else if (!is_lower_hex(value[index])) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool sha256_is_valid(std::string_view value) {
    return value.size() == 64U &&
           std::all_of(value.begin(), value.end(), is_lower_hex);
}

[[nodiscard]] std::uint64_t epoch_seconds_or_throw(
    std::uint64_t realtime_ns,
    const std::string& label) {
    const std::uint64_t epoch =
        realtime_ns / kSyncReplicaNanosecondsPerSecond;
    if (epoch == 0U) {
        throw std::invalid_argument(label + " realtime must be after epoch zero");
    }
    return epoch;
}

[[nodiscard]] std::uint64_t increment_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " generation is exhausted");
    }
    return value + 1U;
}

[[nodiscard]] std::uint64_t seconds_to_ns_or_throw(
    std::uint64_t seconds,
    const std::string& label) {
    if (seconds > std::numeric_limits<std::uint64_t>::max() /
                      kSyncReplicaNanosecondsPerSecond) {
        throw std::overflow_error(label + " seconds-to-nanoseconds overflows");
    }
    return seconds * kSyncReplicaNanosecondsPerSecond;
}

// Compare lhs > rhs + a + b + c without adding potentially hostile uint64s.
[[nodiscard]] bool exceeds_with_allowances(
    std::uint64_t lhs,
    std::uint64_t rhs,
    std::uint64_t first,
    std::uint64_t second,
    std::uint64_t third) noexcept {
    if (lhs <= rhs) return false;
    std::uint64_t excess = lhs - rhs;
    for (const std::uint64_t allowance : {first, second, third}) {
        if (excess <= allowance) return false;
        excess -= allowance;
    }
    return true;
}

[[nodiscard]] SyncReplicaOutboxClockState quarantine_state_or_throw(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& rejected,
    SyncReplicaOutboxClockAnomaly anomaly,
    const std::string& label) {
    SyncReplicaOutboxClockState next = current;
    next.health = SyncReplicaOutboxClockHealth::Quarantined;
    next.observation_generation = increment_or_throw(
        current.observation_generation, label + " observation");
    next.anomaly = anomaly;
    next.rejected = rejected;
    validate_sync_replica_outbox_clock_state_or_throw(next, label);
    return next;
}

[[nodiscard]] SyncReplicaOutboxClockAnchor observation_anchor(
    const SyncReplicaOutboxClockObservation& observation) noexcept {
    return {observation.realtime_ns, observation.boottime_ns,
            observation.uncertainty_ns};
}

[[nodiscard]] bool cumulative_forward_step_exceeds_policy(
    const SyncReplicaOutboxClockAnchor& anchor,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label) {
    const std::uint64_t elapsed_boot =
        observation.boottime_ns - anchor.boottime_ns;
    const std::uint64_t elapsed_real =
        observation.realtime_ns - anchor.realtime_ns;
    return exceeds_with_allowances(
        elapsed_real, elapsed_boot, anchor.uncertainty_ns,
        observation.uncertainty_ns,
        seconds_to_ns_or_throw(
            policy.max_forward_step_seconds,
            label + " forward-step policy"));
}

[[nodiscard]] bool cumulative_realtime_lag_exceeds_policy(
    const SyncReplicaOutboxClockAnchor& anchor,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label) {
    const std::uint64_t elapsed_boot =
        observation.boottime_ns - anchor.boottime_ns;
    const std::uint64_t elapsed_real =
        observation.realtime_ns - anchor.realtime_ns;
    return exceeds_with_allowances(
        elapsed_boot, elapsed_real, anchor.uncertainty_ns,
        observation.uncertainty_ns,
        seconds_to_ns_or_throw(
            policy.max_realtime_lag_seconds,
            label + " realtime-lag policy"));
}

void append_u8(std::string& bytes, std::uint8_t value) {
    bytes.push_back(static_cast<char>(value));
}

void append_u64_be(std::string& bytes, std::uint64_t value) {
    for (std::size_t shift = 8U; shift != 0U; --shift) {
        bytes.push_back(static_cast<char>(
            (value >> ((shift - 1U) * 8U)) & 0xffU));
    }
}

void append_observation_or_throw(
    std::string& bytes,
    const SyncReplicaOutboxClockObservation& observation,
    const std::string& label) {
    validate_sync_replica_outbox_clock_observation_or_throw(observation, label);
    append_u8(bytes, static_cast<std::uint8_t>(observation.source_id.size()));
    bytes.append(observation.source_id);
    bytes.append(observation.boot_id);
    bytes.append(observation.time_namespace_id);
    append_u64_be(bytes, observation.realtime_ns);
    append_u64_be(bytes, observation.boottime_ns);
    append_u64_be(bytes, observation.uncertainty_ns);
    append_u8(bytes, static_cast<std::uint8_t>(observation.synchronization));
}

class Reader final {
public:
    Reader(std::string_view bytes, std::string label)
        : bytes_(bytes), label_(std::move(label)) {}

    [[nodiscard]] std::string_view read(std::size_t count,
                                        const std::string& field) {
        if (count > bytes_.size() - cursor_) {
            throw std::runtime_error(
                label_ + " canonical clock state truncates " + field);
        }
        const std::string_view value = bytes_.substr(cursor_, count);
        cursor_ += count;
        return value;
    }
    [[nodiscard]] std::uint8_t u8(const std::string& field) {
        return static_cast<std::uint8_t>(
            static_cast<unsigned char>(read(1U, field)[0]));
    }
    [[nodiscard]] std::uint64_t u64(const std::string& field) {
        std::uint64_t value = 0U;
        for (const unsigned char byte : read(8U, field)) {
            value = (value << 8U) | static_cast<std::uint64_t>(byte);
        }
        return value;
    }
    void done() const {
        if (cursor_ != bytes_.size()) {
            throw std::runtime_error(
                label_ + " canonical clock state has trailing bytes");
        }
    }
private:
    std::string_view bytes_;
    std::string label_;
    std::size_t cursor_ = 0U;
};

[[nodiscard]] SyncReplicaOutboxClockObservation read_observation_or_throw(
    Reader& reader,
    const std::string& label) {
    SyncReplicaOutboxClockObservation observation;
    const std::size_t source_size = reader.u8("source length");
    observation.source_id = std::string(reader.read(source_size, "source id"));
    observation.boot_id = std::string(reader.read(36U, "boot id"));
    observation.time_namespace_id =
        std::string(reader.read(64U, "time namespace id"));
    observation.realtime_ns = reader.u64("realtime");
    observation.boottime_ns = reader.u64("boottime");
    observation.uncertainty_ns = reader.u64("uncertainty");
    observation.synchronization =
        static_cast<SyncReplicaOutboxClockSynchronization>(
            reader.u8("synchronization"));
    validate_sync_replica_outbox_clock_observation_or_throw(observation, label);
    return observation;
}

}  // namespace

void validate_sync_replica_outbox_clock_policy_or_throw(
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label) {
    if (policy.max_uncertainty_ns == 0U ||
        policy.max_uncertainty_ns >
            kSyncReplicaOutboxClockHardMaxUncertaintyNs) {
        throw std::invalid_argument(
            label + " max clock uncertainty must be in 1..60000000000 ns");
    }
    if (policy.max_forward_step_seconds == 0U ||
        policy.max_forward_step_seconds >
            kSyncReplicaOutboxClockHardMaxForwardStepSeconds) {
        throw std::invalid_argument(
            label + " max forward step must be in 1..3600 seconds");
    }
    if (policy.max_realtime_lag_seconds == 0U ||
        policy.max_realtime_lag_seconds >
            kSyncReplicaOutboxClockHardMaxRealtimeLagSeconds) {
        throw std::invalid_argument(
            label + " max realtime lag must be in 1..3600 seconds");
    }
}

void validate_sync_replica_outbox_clock_observation_or_throw(
    const SyncReplicaOutboxClockObservation& observation,
    const std::string& label) {
    if (!source_id_is_valid(observation.source_id)) {
        throw std::invalid_argument(label + " source id is not canonical");
    }
    if (!boot_id_is_valid(observation.boot_id)) {
        throw std::invalid_argument(label + " boot id is not a canonical UUID");
    }
    if (!sha256_is_valid(observation.time_namespace_id)) {
        throw std::invalid_argument(
            label + " time namespace id is not lowercase SHA-256");
    }
    (void)epoch_seconds_or_throw(observation.realtime_ns, label);
    switch (observation.synchronization) {
        case SyncReplicaOutboxClockSynchronization::Unknown:
        case SyncReplicaOutboxClockSynchronization::Synchronized:
        case SyncReplicaOutboxClockSynchronization::Unsynchronized:
            return;
    }
    throw std::invalid_argument(label + " synchronization state is unsupported");
}

void validate_sync_replica_outbox_clock_state_or_throw(
    const SyncReplicaOutboxClockState& state,
    const std::string& label) {
    switch (state.anomaly) {
        case SyncReplicaOutboxClockAnomaly::None:
        case SyncReplicaOutboxClockAnomaly::LegacyUnbound:
        case SyncReplicaOutboxClockAnomaly::Unsynchronized:
        case SyncReplicaOutboxClockAnomaly::ExcessiveUncertainty:
        case SyncReplicaOutboxClockAnomaly::SourceChanged:
        case SyncReplicaOutboxClockAnomaly::BootChanged:
        case SyncReplicaOutboxClockAnomaly::TimeNamespaceChanged:
        case SyncReplicaOutboxClockAnomaly::BoottimeRollback:
        case SyncReplicaOutboxClockAnomaly::RealtimeRollback:
        case SyncReplicaOutboxClockAnomaly::ForwardStep:
        case SyncReplicaOutboxClockAnomaly::RealtimeLag:
        case SyncReplicaOutboxClockAnomaly::SynchronizationUnknown:
            break;
        default:
            throw std::runtime_error(label + " has unsupported clock anomaly");
    }
    if (state.recovery_generation > state.observation_generation) {
        throw std::runtime_error(
            label + " recovery generation exceeds observation generation");
    }
    if (state.anchor) {
        (void)epoch_seconds_or_throw(
            state.anchor->realtime_ns, label + " drift anchor");
        if (state.anchor->uncertainty_ns >
            kSyncReplicaOutboxClockHardMaxUncertaintyNs) {
            throw std::runtime_error(
                label + " drift anchor uncertainty exceeds hard maximum");
        }
    }
    if (state.accepted) {
        validate_sync_replica_outbox_clock_observation_or_throw(
            *state.accepted, label + " accepted observation");
        if (state.high_water_epoch != epoch_seconds_or_throw(
                state.accepted->realtime_ns, label + " accepted observation")) {
            throw std::runtime_error(
                label + " high-water does not equal the accepted observation");
        }
        if (state.accepted->synchronization !=
            SyncReplicaOutboxClockSynchronization::Synchronized) {
            throw std::runtime_error(
                label + " accepted observation is not synchronized");
        }
        if (!state.anchor ||
            state.anchor->realtime_ns > state.accepted->realtime_ns ||
            state.anchor->boottime_ns > state.accepted->boottime_ns) {
            throw std::runtime_error(
                label + " accepted observation has no coherent drift anchor");
        }
    } else if (state.anchor) {
        throw std::runtime_error(
            label + " drift anchor exists without accepted observation");
    }
    if (state.rejected) {
        validate_sync_replica_outbox_clock_observation_or_throw(
            *state.rejected, label + " rejected observation");
    }

    switch (state.health) {
        case SyncReplicaOutboxClockHealth::Uninitialized:
            if (state.high_water_epoch != 0U ||
                state.observation_generation != 0U ||
                state.recovery_generation != 0U || state.anchor || state.accepted ||
                state.rejected ||
                state.anomaly != SyncReplicaOutboxClockAnomaly::None) {
                throw std::runtime_error(
                    label + " has invalid uninitialized clock state");
            }
            return;
        case SyncReplicaOutboxClockHealth::Healthy:
            if (!state.accepted || state.high_water_epoch == 0U ||
                state.observation_generation == 0U || state.rejected ||
                state.anomaly != SyncReplicaOutboxClockAnomaly::None) {
                throw std::runtime_error(label + " has invalid healthy clock state");
            }
            return;
        case SyncReplicaOutboxClockHealth::Quarantined:
            if (state.observation_generation == 0U ||
                state.anomaly == SyncReplicaOutboxClockAnomaly::None) {
                throw std::runtime_error(
                    label + " has incomplete clock quarantine evidence");
            }
            if (state.anomaly == SyncReplicaOutboxClockAnomaly::LegacyUnbound) {
                if (state.high_water_epoch == 0U || state.anchor || state.accepted ||
                    state.rejected) {
                    throw std::runtime_error(
                        label + " has invalid legacy-unbound quarantine");
                }
            } else if (!state.rejected) {
                throw std::runtime_error(
                    label + " quarantine discarded its rejected observation");
            }
            if (!state.accepted &&
                state.anomaly != SyncReplicaOutboxClockAnomaly::LegacyUnbound &&
                state.high_water_epoch != 0U) {
                throw std::runtime_error(
                    label + " has high-water without accepted clock evidence");
            }
            return;
    }
    throw std::runtime_error(label + " has unsupported clock health");
}

void validate_sync_replica_outbox_clock_state_against_policy_or_throw(
    const SyncReplicaOutboxClockState& state,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label) {
    validate_sync_replica_outbox_clock_policy_or_throw(policy, label + " policy");
    validate_sync_replica_outbox_clock_state_or_throw(state, label + " state");
    if (!state.accepted) return;
    if (state.accepted->uncertainty_ns > policy.max_uncertainty_ns ||
        state.anchor->uncertainty_ns > policy.max_uncertainty_ns) {
        throw std::runtime_error(
            label + " accepted clock uncertainty exceeds durable policy");
    }
    if (cumulative_forward_step_exceeds_policy(
            *state.anchor, *state.accepted, policy, label)) {
        throw std::runtime_error(
            label + " accepted clock exceeds cumulative forward-step policy");
    }
    if (cumulative_realtime_lag_exceeds_policy(
            *state.anchor, *state.accepted, policy, label)) {
        throw std::runtime_error(
            label + " accepted clock exceeds cumulative realtime-lag policy");
    }
}

SyncReplicaOutboxClockObservationResult
observe_sync_replica_outbox_clock_or_throw(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    const std::string& label) {
    validate_sync_replica_outbox_clock_policy_or_throw(policy, label + " policy");
    validate_sync_replica_outbox_clock_state_or_throw(current, label + " current");
    validate_sync_replica_outbox_clock_state_against_policy_or_throw(
        current, policy, label + " current");
    validate_sync_replica_outbox_clock_observation_or_throw(
        observation, label + " observation");
    if (current.health == SyncReplicaOutboxClockHealth::Quarantined) {
        return {SyncReplicaOutboxClockObservationOutcome::AlreadyQuarantined,
                current, 0U, false};
    }
    const auto quarantine = [&](SyncReplicaOutboxClockAnomaly anomaly) {
        return SyncReplicaOutboxClockObservationResult{
            SyncReplicaOutboxClockObservationOutcome::Quarantined,
            quarantine_state_or_throw(current, observation, anomaly, label),
            0U, true};
    };
    if (observation.synchronization ==
        SyncReplicaOutboxClockSynchronization::Unknown) {
        return quarantine(
            SyncReplicaOutboxClockAnomaly::SynchronizationUnknown);
    }
    if (observation.synchronization ==
        SyncReplicaOutboxClockSynchronization::Unsynchronized) {
        return quarantine(SyncReplicaOutboxClockAnomaly::Unsynchronized);
    }
    if (observation.uncertainty_ns > policy.max_uncertainty_ns) {
        return quarantine(SyncReplicaOutboxClockAnomaly::ExcessiveUncertainty);
    }
    if (current.health == SyncReplicaOutboxClockHealth::Healthy) {
        const auto& accepted = *current.accepted;
        if (observation.source_id != accepted.source_id)
            return quarantine(SyncReplicaOutboxClockAnomaly::SourceChanged);
        if (observation.boot_id != accepted.boot_id)
            return quarantine(SyncReplicaOutboxClockAnomaly::BootChanged);
        if (observation.time_namespace_id != accepted.time_namespace_id)
            return quarantine(
                SyncReplicaOutboxClockAnomaly::TimeNamespaceChanged);
        if (observation.boottime_ns < accepted.boottime_ns)
            return quarantine(
                SyncReplicaOutboxClockAnomaly::BoottimeRollback);
        if (observation.realtime_ns < accepted.realtime_ns)
            return quarantine(
                SyncReplicaOutboxClockAnomaly::RealtimeRollback);

        if (cumulative_forward_step_exceeds_policy(
                *current.anchor, observation, policy, label)) {
            return quarantine(SyncReplicaOutboxClockAnomaly::ForwardStep);
        }
        if (cumulative_realtime_lag_exceeds_policy(
                *current.anchor, observation, policy, label)) {
            return quarantine(SyncReplicaOutboxClockAnomaly::RealtimeLag);
        }
    }

    const std::uint64_t usable_epoch = epoch_seconds_or_throw(
        observation.realtime_ns, label + " accepted observation");
    if (usable_epoch < current.high_water_epoch) {
        return quarantine(SyncReplicaOutboxClockAnomaly::RealtimeRollback);
    }
    if (current.accepted && *current.accepted == observation) {
        return {SyncReplicaOutboxClockObservationOutcome::Accepted,
                current, usable_epoch, false};
    }
    SyncReplicaOutboxClockState next = current;
    next.health = SyncReplicaOutboxClockHealth::Healthy;
    next.high_water_epoch = usable_epoch;
    next.observation_generation = increment_or_throw(
        current.observation_generation, label + " observation");
    if (!next.anchor) next.anchor = observation_anchor(observation);
    next.accepted = observation;
    next.anomaly = SyncReplicaOutboxClockAnomaly::None;
    next.rejected.reset();
    validate_sync_replica_outbox_clock_state_or_throw(next, label + " accepted");
    return {SyncReplicaOutboxClockObservationOutcome::Accepted,
            std::move(next), usable_epoch, true};
}

SyncReplicaOutboxClockState recover_sync_replica_outbox_clock_or_throw(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& observation,
    const SyncReplicaOutboxClockPolicy& policy,
    std::uint64_t expected_observation_generation,
    const std::string& label) {
    validate_sync_replica_outbox_clock_policy_or_throw(policy, label + " policy");
    validate_sync_replica_outbox_clock_state_or_throw(current, label + " current");
    validate_sync_replica_outbox_clock_state_against_policy_or_throw(
        current, policy, label + " current");
    validate_sync_replica_outbox_clock_observation_or_throw(
        observation, label + " recovery observation");
    if (current.health != SyncReplicaOutboxClockHealth::Quarantined)
        throw std::runtime_error(label + " clock is not quarantined");
    if (expected_observation_generation != current.observation_generation)
        throw std::runtime_error(
            label + " recovery generation does not name current quarantine");
    if (observation.synchronization !=
        SyncReplicaOutboxClockSynchronization::Synchronized)
        throw std::runtime_error(
            label + " recovery observation is unsynchronized");
    if (observation.uncertainty_ns > policy.max_uncertainty_ns)
        throw std::runtime_error(
            label + " recovery observation exceeds uncertainty policy");
    const std::uint64_t usable_epoch = epoch_seconds_or_throw(
        observation.realtime_ns, label + " recovery observation");
    if (usable_epoch < current.high_water_epoch)
        throw std::runtime_error(
            label + " recovery would move below durable high-water");

    SyncReplicaOutboxClockState next;
    next.health = SyncReplicaOutboxClockHealth::Healthy;
    next.high_water_epoch = usable_epoch;
    next.observation_generation = increment_or_throw(
        current.observation_generation, label + " observation");
    next.recovery_generation = increment_or_throw(
        current.recovery_generation, label + " recovery");
    next.anchor = observation_anchor(observation);
    next.accepted = observation;
    validate_sync_replica_outbox_clock_state_or_throw(next, label + " recovered");
    return next;
}

SyncReplicaOutboxClockState
make_legacy_unbound_sync_replica_outbox_clock_state_or_throw(
    std::uint64_t high_water_epoch,
    const std::string& label) {
    if (high_water_epoch == 0U) return {};
    SyncReplicaOutboxClockState state;
    state.health = SyncReplicaOutboxClockHealth::Quarantined;
    state.high_water_epoch = high_water_epoch;
    state.observation_generation = 1U;
    state.anomaly = SyncReplicaOutboxClockAnomaly::LegacyUnbound;
    validate_sync_replica_outbox_clock_state_or_throw(state, label);
    return state;
}

std::string encode_sync_replica_outbox_clock_state_canonical_or_throw(
    const SyncReplicaOutboxClockState& state,
    const std::string& label) {
    validate_sync_replica_outbox_clock_state_or_throw(state, label);
    std::string bytes;
    bytes.reserve(kSyncReplicaOutboxClockStateMaxCanonicalBytes);
    bytes.append(kClockStateDomain);
    append_u8(bytes, static_cast<std::uint8_t>(state.health));
    append_u64_be(bytes, state.high_water_epoch);
    append_u64_be(bytes, state.observation_generation);
    append_u64_be(bytes, state.recovery_generation);
    append_u8(bytes, state.anchor ? 1U : 0U);
    if (state.anchor) {
        append_u64_be(bytes, state.anchor->realtime_ns);
        append_u64_be(bytes, state.anchor->boottime_ns);
        append_u64_be(bytes, state.anchor->uncertainty_ns);
    }
    append_u8(bytes, state.accepted ? 1U : 0U);
    if (state.accepted)
        append_observation_or_throw(
            bytes, *state.accepted, label + " accepted observation");
    append_u8(bytes, static_cast<std::uint8_t>(state.anomaly));
    append_u8(bytes, state.rejected ? 1U : 0U);
    if (state.rejected)
        append_observation_or_throw(
            bytes, *state.rejected, label + " rejected observation");
    if (bytes.size() > kSyncReplicaOutboxClockStateMaxCanonicalBytes)
        throw std::length_error(label + " canonical clock state is oversized");
    return bytes;
}

SyncReplicaOutboxClockState
decode_sync_replica_outbox_clock_state_canonical_or_throw(
    std::string_view bytes,
    const std::string& label) {
    if (bytes.size() > kSyncReplicaOutboxClockStateMaxCanonicalBytes)
        throw std::runtime_error(label + " canonical clock state is oversized");
    Reader reader(bytes, label);
    if (reader.read(kClockStateDomain.size(), "domain") != kClockStateDomain)
        throw std::runtime_error(
            label + " canonical clock state domain mismatch");
    SyncReplicaOutboxClockState state;
    state.health = static_cast<SyncReplicaOutboxClockHealth>(reader.u8("health"));
    state.high_water_epoch = reader.u64("high-water epoch");
    state.observation_generation = reader.u64("observation generation");
    state.recovery_generation = reader.u64("recovery generation");
    const std::uint8_t has_anchor = reader.u8("anchor marker");
    if (has_anchor > 1U)
        throw std::runtime_error(label + " anchor marker is noncanonical");
    if (has_anchor == 1U) {
        state.anchor = SyncReplicaOutboxClockAnchor{
            reader.u64("anchor realtime"),
            reader.u64("anchor boottime"),
            reader.u64("anchor uncertainty")};
    }
    const std::uint8_t has_accepted = reader.u8("accepted marker");
    if (has_accepted > 1U)
        throw std::runtime_error(label + " accepted marker is noncanonical");
    if (has_accepted == 1U)
        state.accepted = read_observation_or_throw(
            reader, label + " accepted observation");
    state.anomaly =
        static_cast<SyncReplicaOutboxClockAnomaly>(reader.u8("anomaly"));
    const std::uint8_t has_rejected = reader.u8("rejected marker");
    if (has_rejected > 1U)
        throw std::runtime_error(label + " rejected marker is noncanonical");
    if (has_rejected == 1U)
        state.rejected = read_observation_or_throw(
            reader, label + " rejected observation");
    reader.done();
    validate_sync_replica_outbox_clock_state_or_throw(state, label);
    if (encode_sync_replica_outbox_clock_state_canonical_or_throw(
            state, label + " re-encode") != bytes)
        throw std::runtime_error(
            label + " canonical clock state is not unique");
    return state;
}

std::string_view sync_replica_outbox_clock_anomaly_name(
    SyncReplicaOutboxClockAnomaly anomaly) noexcept {
    switch (anomaly) {
        case SyncReplicaOutboxClockAnomaly::None: return "none";
        case SyncReplicaOutboxClockAnomaly::LegacyUnbound: return "legacy-unbound";
        case SyncReplicaOutboxClockAnomaly::Unsynchronized: return "unsynchronized";
        case SyncReplicaOutboxClockAnomaly::ExcessiveUncertainty: return "excessive-uncertainty";
        case SyncReplicaOutboxClockAnomaly::SourceChanged: return "source-changed";
        case SyncReplicaOutboxClockAnomaly::BootChanged: return "boot-changed";
        case SyncReplicaOutboxClockAnomaly::TimeNamespaceChanged: return "time-namespace-changed";
        case SyncReplicaOutboxClockAnomaly::BoottimeRollback: return "boottime-rollback";
        case SyncReplicaOutboxClockAnomaly::RealtimeRollback: return "realtime-rollback";
        case SyncReplicaOutboxClockAnomaly::ForwardStep: return "forward-step";
        case SyncReplicaOutboxClockAnomaly::RealtimeLag: return "realtime-lag";
        case SyncReplicaOutboxClockAnomaly::SynchronizationUnknown:
            return "synchronization-unknown";
    }
    return "unsupported";
}

}  // namespace anonsync
