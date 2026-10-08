#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_outbox_clock_linux_internal.hpp"

#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using anonsync::SyncReplicaOutboxClockAnomaly;
using anonsync::SyncReplicaOutboxClockHealth;
using anonsync::SyncReplicaOutboxClockObservation;
using anonsync::SyncReplicaOutboxClockObservationOutcome;
using anonsync::SyncReplicaOutboxClockPolicy;
using anonsync::SyncReplicaOutboxClockState;
using anonsync::SyncReplicaOutboxClockSynchronization;

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        function();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

[[nodiscard]] SyncReplicaOutboxClockObservation observation(
    std::uint64_t realtime_seconds,
    std::uint64_t boottime_seconds,
    std::uint64_t uncertainty_ns = 1U) {
    SyncReplicaOutboxClockObservation value;
    value.source_id = "test-boottime-realtime-v1";
    value.boot_id = "01234567-89ab-cdef-0123-456789abcdef";
    value.time_namespace_id = std::string(64U, 'a');
    value.realtime_ns =
        realtime_seconds * anonsync::kSyncReplicaNanosecondsPerSecond;
    value.boottime_ns =
        boottime_seconds * anonsync::kSyncReplicaNanosecondsPerSecond;
    value.uncertainty_ns = uncertainty_ns;
    value.synchronization =
        SyncReplicaOutboxClockSynchronization::Synchronized;
    return value;
}

[[nodiscard]] SyncReplicaOutboxClockState accept(
    const SyncReplicaOutboxClockState& current,
    const SyncReplicaOutboxClockObservation& value,
    const SyncReplicaOutboxClockPolicy& policy = {}) {
    const auto result = anonsync::observe_sync_replica_outbox_clock_or_throw(
        current, value, policy, "clock test accept");
    require(
        result.outcome == SyncReplicaOutboxClockObservationOutcome::Accepted,
        "clock observation should be accepted");
    return result.state;
}

void test_policy_and_observation_validation() {
    anonsync::validate_sync_replica_outbox_clock_policy_or_throw(
        {}, "default policy");
    SyncReplicaOutboxClockPolicy bad{};
    bad.max_uncertainty_ns = 0U;
    require_throws(
        [&] {
            anonsync::validate_sync_replica_outbox_clock_policy_or_throw(
                bad, "zero uncertainty");
        },
        "zero maximum uncertainty must fail");
    bad = {};
    bad.max_forward_step_seconds =
        anonsync::kSyncReplicaOutboxClockHardMaxForwardStepSeconds + 1U;
    require_throws(
        [&] {
            anonsync::validate_sync_replica_outbox_clock_policy_or_throw(
                bad, "oversized forward step");
        },
        "oversized forward-step policy must fail");

    auto value = observation(100U, 10U);
    anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
        value, "valid observation");
    value.boot_id[0] = 'A';
    require_throws(
        [&] {
            anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
                value, "uppercase boot id");
        },
        "noncanonical boot id must fail");
    value = observation(100U, 10U);
    value.synchronization =
        static_cast<SyncReplicaOutboxClockSynchronization>(99U);
    require_throws(
        [&] {
            anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
                value, "unknown synchronization");
        },
        "unknown synchronization state must fail");
}

void test_initial_acceptance_and_canonical_round_trip() {
    const auto first = observation(100U, 10U, 7U);
    const auto result = anonsync::observe_sync_replica_outbox_clock_or_throw(
        {}, first, {}, "initial observation");
    require(
        result.outcome == SyncReplicaOutboxClockObservationOutcome::Accepted &&
            result.changed && result.usable_epoch == 100U,
        "first synchronized observation must initialize the clock");
    require(
        result.state.health == SyncReplicaOutboxClockHealth::Healthy &&
            result.state.high_water_epoch == 100U &&
            result.state.observation_generation == 1U &&
            result.state.recovery_generation == 0U,
        "initialized state must retain exact generations and high-water");
    require(
        result.state.anchor.has_value() &&
            result.state.anchor->realtime_ns == first.realtime_ns &&
            result.state.anchor->boottime_ns == first.boottime_ns &&
            result.state.anchor->uncertainty_ns == first.uncertainty_ns,
        "first accepted observation must become the cumulative anchor");
    require(
        result.state.accepted == first && !result.state.rejected.has_value() &&
            result.state.anomaly == SyncReplicaOutboxClockAnomaly::None,
        "healthy state must retain only accepted evidence");

    const std::string bytes =
        anonsync::encode_sync_replica_outbox_clock_state_canonical_or_throw(
            result.state, "encode");
    require(
        bytes.size() <= anonsync::kSyncReplicaOutboxClockStateMaxCanonicalBytes,
        "canonical state must respect its hard byte ceiling");
    require(
        anonsync::decode_sync_replica_outbox_clock_state_canonical_or_throw(
            bytes, "decode") == result.state,
        "canonical state must round-trip exactly");

    const auto same = anonsync::observe_sync_replica_outbox_clock_or_throw(
        result.state, first, {}, "idempotent observation");
    require(
        same.outcome == SyncReplicaOutboxClockObservationOutcome::Accepted &&
            !same.changed && same.state == result.state,
        "an identical observation must be idempotent");

    require_throws(
        [&] {
            auto truncated = bytes;
            truncated.pop_back();
            (void)anonsync::
                decode_sync_replica_outbox_clock_state_canonical_or_throw(
                    truncated, "truncated state");
        },
        "truncated canonical state must fail closed");
    require_throws(
        [&] {
            auto trailing = bytes;
            trailing.push_back('\0');
            (void)anonsync::
                decode_sync_replica_outbox_clock_state_canonical_or_throw(
                    trailing, "trailing state");
        },
        "canonical state with trailing bytes must fail closed");
}

void test_cumulative_forward_step_tripwire() {
    SyncReplicaOutboxClockPolicy policy{};
    policy.max_forward_step_seconds = 5U;
    policy.max_realtime_lag_seconds = 100U;
    policy.max_uncertainty_ns = 1U;

    const SyncReplicaOutboxClockState start =
        accept({}, observation(100U, 100U), policy);
    const SyncReplicaOutboxClockState first_small_step =
        accept(start, observation(104U, 101U), policy);
    require(
        first_small_step.anchor == start.anchor &&
            first_small_step.accepted == observation(104U, 101U),
        "accepted progress must preserve the original recovery anchor");

    const auto result = anonsync::observe_sync_replica_outbox_clock_or_throw(
        first_small_step, observation(108U, 102U), policy,
        "split forward step");
    require(
        result.outcome == SyncReplicaOutboxClockObservationOutcome::Quarantined &&
            result.state.health == SyncReplicaOutboxClockHealth::Quarantined &&
            result.state.anomaly == SyncReplicaOutboxClockAnomaly::ForwardStep,
        "individually-small steps must not launder excessive cumulative drift");
    require(
        result.state.anchor == start.anchor &&
            result.state.accepted == first_small_step.accepted &&
            result.state.rejected == observation(108U, 102U),
        "forward-step quarantine must preserve anchor, accepted, and rejected evidence");

    const auto again = anonsync::observe_sync_replica_outbox_clock_or_throw(
        result.state, observation(109U, 103U), policy,
        "already quarantined");
    require(
        again.outcome ==
                SyncReplicaOutboxClockObservationOutcome::AlreadyQuarantined &&
            !again.changed && again.state == result.state,
        "ordinary observation must not silently clear quarantine");
}

void test_cumulative_realtime_lag_tripwire() {
    SyncReplicaOutboxClockPolicy policy{};
    policy.max_forward_step_seconds = 100U;
    policy.max_realtime_lag_seconds = 5U;
    policy.max_uncertainty_ns = 1U;

    const SyncReplicaOutboxClockState start =
        accept({}, observation(100U, 100U), policy);
    const SyncReplicaOutboxClockState first_small_lag =
        accept(start, observation(101U, 104U), policy);
    const auto result = anonsync::observe_sync_replica_outbox_clock_or_throw(
        first_small_lag, observation(102U, 108U), policy,
        "split realtime lag");
    require(
        result.outcome == SyncReplicaOutboxClockObservationOutcome::Quarantined &&
            result.state.anomaly == SyncReplicaOutboxClockAnomaly::RealtimeLag,
        "split wall-clock stalls must trip the cumulative lag fence");
}

void test_identity_rollback_and_quality_anomalies() {
    const SyncReplicaOutboxClockState healthy =
        accept({}, observation(100U, 100U));
    const auto expect_anomaly = [&](SyncReplicaOutboxClockObservation value,
                                    SyncReplicaOutboxClockAnomaly anomaly,
                                    std::string_view label) {
        const auto result = anonsync::observe_sync_replica_outbox_clock_or_throw(
            healthy, value, {}, std::string(label));
        require(
            result.outcome ==
                    SyncReplicaOutboxClockObservationOutcome::Quarantined &&
                result.state.anomaly == anomaly,
            label);
    };

    auto value = observation(101U, 101U);
    value.source_id = "other-source-v1";
    expect_anomaly(
        value, SyncReplicaOutboxClockAnomaly::SourceChanged,
        "clock source changes must quarantine");
    value = observation(101U, 101U);
    value.boot_id = "11234567-89ab-cdef-0123-456789abcdef";
    expect_anomaly(
        value, SyncReplicaOutboxClockAnomaly::BootChanged,
        "boot identity changes must quarantine");
    value = observation(101U, 101U);
    value.time_namespace_id = std::string(64U, 'b');
    expect_anomaly(
        value, SyncReplicaOutboxClockAnomaly::TimeNamespaceChanged,
        "time namespace changes must quarantine");
    expect_anomaly(
        observation(101U, 99U),
        SyncReplicaOutboxClockAnomaly::BoottimeRollback,
        "boottime rollback must quarantine");
    expect_anomaly(
        observation(99U, 101U),
        SyncReplicaOutboxClockAnomaly::RealtimeRollback,
        "realtime rollback must quarantine");

    value = observation(101U, 101U);
    value.synchronization =
        SyncReplicaOutboxClockSynchronization::Unknown;
    const auto unknown_result =
        anonsync::observe_sync_replica_outbox_clock_or_throw(
            healthy, value, {}, "unknown clock quality");
    require(
        unknown_result.outcome ==
                SyncReplicaOutboxClockObservationOutcome::Quarantined &&
            unknown_result.state.anomaly ==
                SyncReplicaOutboxClockAnomaly::SynchronizationUnknown &&
            unknown_result.state.rejected == value,
        "unknown clock quality must quarantine without being mislabeled");
    const std::string unknown_bytes =
        anonsync::encode_sync_replica_outbox_clock_state_canonical_or_throw(
            unknown_result.state, "unknown clock encoding");
    require(
        anonsync::decode_sync_replica_outbox_clock_state_canonical_or_throw(
            unknown_bytes, "unknown clock decoding") == unknown_result.state &&
            anonsync::sync_replica_outbox_clock_anomaly_name(
                unknown_result.state.anomaly) == "synchronization-unknown",
        "unknown clock quarantine must survive canonical persistence exactly");
    value = observation(101U, 101U);
    value.synchronization =
        SyncReplicaOutboxClockSynchronization::Unsynchronized;
    expect_anomaly(
        value, SyncReplicaOutboxClockAnomaly::Unsynchronized,
        "unsynchronized time must quarantine");
    value = observation(
        101U, 101U,
        anonsync::kSyncReplicaOutboxDefaultClockMaxUncertaintyNs + 1U);
    expect_anomaly(
        value, SyncReplicaOutboxClockAnomaly::ExcessiveUncertainty,
        "excessive uncertainty must quarantine");
}

void test_recovery_and_generation_fence() {
    auto unsynchronized = observation(100U, 100U);
    unsynchronized.synchronization =
        SyncReplicaOutboxClockSynchronization::Unsynchronized;
    const auto quarantined =
        anonsync::observe_sync_replica_outbox_clock_or_throw(
            {}, unsynchronized, {}, "initial quarantine").state;
    require(
        quarantined.health == SyncReplicaOutboxClockHealth::Quarantined &&
            quarantined.observation_generation == 1U &&
            !quarantined.accepted && !quarantined.anchor,
        "initial quality failure must retain rejected evidence without inventing an anchor");

    require_throws(
        [&] {
            (void)anonsync::recover_sync_replica_outbox_clock_or_throw(
                quarantined, observation(101U, 101U), {}, 0U,
                "stale recovery generation");
        },
        "recovery must name the exact quarantine generation");
    const auto recovered =
        anonsync::recover_sync_replica_outbox_clock_or_throw(
            quarantined, observation(101U, 101U), {}, 1U,
            "valid recovery");
    require(
        recovered.health == SyncReplicaOutboxClockHealth::Healthy &&
            recovered.observation_generation == 2U &&
            recovered.recovery_generation == 1U &&
            recovered.high_water_epoch == 101U,
        "recovery must advance both exact generations and high-water");
    require(
        recovered.anchor.has_value() && recovered.accepted.has_value() &&
            recovered.anchor->realtime_ns == recovered.accepted->realtime_ns &&
            !recovered.rejected &&
            recovered.anomaly == SyncReplicaOutboxClockAnomaly::None,
        "recovery must establish a fresh anchor and clear rejected evidence");

    const auto legacy =
        anonsync::make_legacy_unbound_sync_replica_outbox_clock_state_or_throw(
            500U, "legacy clock");
    require(
        legacy.health == SyncReplicaOutboxClockHealth::Quarantined &&
            legacy.anomaly == SyncReplicaOutboxClockAnomaly::LegacyUnbound &&
            legacy.high_water_epoch == 500U && !legacy.anchor &&
            !legacy.accepted && !legacy.rejected,
        "legacy high-water must migrate as explicit unbound quarantine");
    require_throws(
        [&] {
            (void)anonsync::recover_sync_replica_outbox_clock_or_throw(
                legacy, observation(499U, 499U), {}, 1U,
                "legacy recovery below high-water");
        },
        "legacy recovery must not roll below durable high-water");
    const auto rebound =
        anonsync::recover_sync_replica_outbox_clock_or_throw(
            legacy, observation(500U, 500U), {}, 1U,
            "legacy recovery at high-water");
    require(
        rebound.health == SyncReplicaOutboxClockHealth::Healthy &&
            rebound.high_water_epoch == 500U && rebound.anchor.has_value(),
        "explicit recovery may bind legacy state at its durable high-water");
}

void test_state_policy_cross_attestation() {
    SyncReplicaOutboxClockPolicy permissive{};
    permissive.max_forward_step_seconds = 10U;
    permissive.max_realtime_lag_seconds = 10U;
    permissive.max_uncertainty_ns = 10U;
    auto state = accept({}, observation(100U, 100U, 5U), permissive);
    state = accept(state, observation(108U, 100U, 5U), permissive);
    anonsync::validate_sync_replica_outbox_clock_state_against_policy_or_throw(
        state, permissive, "permissive retained state");

    auto tighter = permissive;
    tighter.max_forward_step_seconds = 5U;
    require_throws(
        [&] {
            anonsync::
                validate_sync_replica_outbox_clock_state_against_policy_or_throw(
                    state, tighter, "tight forward policy");
        },
        "retained cumulative drift must fit a replacement policy");
    tighter = permissive;
    tighter.max_uncertainty_ns = 1U;
    require_throws(
        [&] {
            anonsync::
                validate_sync_replica_outbox_clock_state_against_policy_or_throw(
                    state, tighter, "tight uncertainty policy");
        },
        "retained anchor uncertainty must fit a replacement policy");
}


void test_linux_time_namespace_probe_classification() {
    using anonsync::sync_replica_outbox_clock_linux_detail::
        TimeNamespaceProbeClassification;
    using anonsync::sync_replica_outbox_clock_linux_detail::
        classify_time_namespace_probe;
    using anonsync::sync_replica_outbox_clock_linux_detail::
        mainline_generation_may_expose_time_namespaces;

    require(
        !mainline_generation_may_expose_time_namespaces(5UL, 5UL) &&
            mainline_generation_may_expose_time_namespaces(5UL, 6UL) &&
            mainline_generation_may_expose_time_namespaces(6UL, 12UL),
        "kernel generation is only a mainline feature hint");
    require(
        classify_time_namespace_probe(0, 0, 6UL, 12UL) ==
            TimeNamespaceProbeClassification::Bound,
        "successful stat must be the only bound-identity proof");
    require(
        classify_time_namespace_probe(-1, ENOENT, 5UL, 5UL) ==
            TimeNamespaceProbeClassification::AbsentBeforeMainlineFeature,
        "missing identity before Linux 5.6 is diagnostically distinct but unbound");
    require(
        classify_time_namespace_probe(-1, ENOENT, 5UL, 6UL) ==
                TimeNamespaceProbeClassification::IdentityUnavailable &&
            classify_time_namespace_probe(-1, ENOENT, 6UL, 12UL) ==
                TimeNamespaceProbeClassification::IdentityUnavailable,
        "missing identity on a feature-generation kernel is not capability proof");
    require(
        classify_time_namespace_probe(-1, EACCES, 6UL, 12UL) ==
                TimeNamespaceProbeClassification::IdentityUnavailable &&
            classify_time_namespace_probe(-1, EPERM, 6UL, 12UL) ==
                TimeNamespaceProbeClassification::IdentityUnavailable,
        "permission-hidden namespace identity must remain unavailable");
    require(
        classify_time_namespace_probe(-1, EIO, 6UL, 12UL) ==
            TimeNamespaceProbeClassification::FatalError,
        "transient or corrupt procfs failures must not be normalized");
}

void test_operator_trusted_source_shape() {
    require_throws(
        [] {
            (void)anonsync::
                make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
                    {"", 1U});
        },
        "operator-trusted source must reject an empty authority ID");
    require_throws(
        [] {
            (void)anonsync::
                make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
                    {"clock-owner", 0U});
        },
        "operator-trusted source must reject zero uncertainty");
    require_throws(
        [] {
            (void)anonsync::
                make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
                    {"clock-owner",
                     anonsync::kSyncReplicaOutboxClockHardMaxUncertaintyNs +
                         1U});
        },
        "operator-trusted source must reject uncertainty above the hard cap");

#if defined(__linux__)
    constexpr std::uint64_t kClaimedUncertainty = 1000000U;
    auto source = anonsync::
        make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
            {"clock-owner", kClaimedUncertainty});
    require(source != nullptr,
            "operator-trusted Linux clock source must be constructible");
    const auto first = source->observe_or_throw(
        "operator-trusted clock first sample");
    const auto second = source->observe_or_throw(
        "operator-trusted clock second sample");
    anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
        first, "operator-trusted first observation");
    anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
        second, "operator-trusted second observation");
    require(
        first.source_id.starts_with("operator-trusted-clock-v1-") &&
            first.source_id == second.source_id &&
            first.boot_id == second.boot_id &&
            first.time_namespace_id == second.time_namespace_id,
        "operator-trusted samples must retain exact deployment identity");
    require(
        first.synchronization ==
                SyncReplicaOutboxClockSynchronization::Synchronized &&
            second.synchronization ==
                SyncReplicaOutboxClockSynchronization::Synchronized &&
            first.uncertainty_ns >= kClaimedUncertainty &&
            second.uncertainty_ns >= kClaimedUncertainty,
        "operator-trusted samples must expose the explicit trust and claimed uncertainty");
    require(
        second.realtime_ns >= first.realtime_ns &&
            second.boottime_ns >= first.boottime_ns,
        "operator-trusted samples must remain nondecreasing inside one boot");
    const auto accepted = anonsync::observe_sync_replica_outbox_clock_or_throw(
        {}, first, {}, "operator-trusted initial acceptance");
    require(
        accepted.outcome ==
                SyncReplicaOutboxClockObservationOutcome::Accepted &&
            accepted.state.health == SyncReplicaOutboxClockHealth::Healthy,
        "operator-trusted source must mint liveness only through the normal clock state machine");
#endif
}

void test_system_source_shape() {
#if defined(__linux__)
    auto source = anonsync::make_system_sync_replica_outbox_clock_source();
    require(source != nullptr, "Linux system clock source must be constructible");
    const auto value = source->observe_or_throw("system clock smoke test");
    anonsync::validate_sync_replica_outbox_clock_observation_or_throw(
        value, "system clock smoke observation");
    require(
        value.realtime_ns > 0U && !value.source_id.empty() &&
            value.boottime_ns > 0U,
        "Linux system source must return bounded identity and clock material");
    if (value.source_id.find("unavailable") != std::string::npos) {
        require(
            value.synchronization ==
                SyncReplicaOutboxClockSynchronization::Unknown,
            "unobservable time namespace identity must force unknown quality");
        const auto result =
            anonsync::observe_sync_replica_outbox_clock_or_throw(
                {}, value, {}, "system clock unavailable capability");
        require(
            result.outcome ==
                    SyncReplicaOutboxClockObservationOutcome::Quarantined &&
                result.state.anomaly ==
                    SyncReplicaOutboxClockAnomaly::SynchronizationUnknown &&
                result.state.rejected == value,
            "unavailable capability must become durable quarantine evidence");
    }
#endif
}

}  // namespace

int main() {
    try {
        test_policy_and_observation_validation();
        test_initial_acceptance_and_canonical_round_trip();
        test_cumulative_forward_step_tripwire();
        test_cumulative_realtime_lag_tripwire();
        test_identity_rollback_and_quality_anomalies();
        test_recovery_and_generation_fence();
        test_state_policy_cross_attestation();
        test_linux_time_namespace_probe_classification();
        test_operator_trusted_source_shape();
        test_system_source_shape();
        std::cout << "sync replica outbox clock tests passed: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica outbox clock tests failed after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}
