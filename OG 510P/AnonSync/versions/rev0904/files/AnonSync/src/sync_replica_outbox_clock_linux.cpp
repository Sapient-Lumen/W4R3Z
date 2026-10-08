#include "sync_replica_outbox_clock.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_outbox_clock_linux_internal.hpp"
#include "sync_system_epoch_identity.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#if defined(__linux__)
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/timex.h>
#include <sys/utsname.h>
#include <time.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

#if defined(__linux__)

[[nodiscard]] std::string errno_message(
    const std::string& label,
    int error_number) {
    return label + ": " + std::strerror(error_number);
}

[[nodiscard]] std::string observe_linux_boot_id_or_throw(
    const std::string& label) {
    const SyncSystemBootIdentityObservation observation =
        observe_sync_system_boot_identity_or_throw(label);
    if (observation.kind != SyncSystemBootIdentityKind::LinuxProcBootId) {
        throw std::runtime_error(
            label + " source is unavailable: " +
            sync_system_boot_identity_kind_name(observation.kind));
    }
    return observation.boot_id;
}

struct NamespaceIdentity final {
    std::uint64_t device = 0U;
    std::uint64_t inode = 0U;
    sync_replica_outbox_clock_linux_detail::TimeNamespaceProbeClassification
        classification = sync_replica_outbox_clock_linux_detail::
            TimeNamespaceProbeClassification::FatalError;
    bool operator==(const NamespaceIdentity&) const = default;
};

[[nodiscard]] std::pair<unsigned long, unsigned long>
linux_kernel_major_minor_or_throw(const std::string& label) {
    struct utsname identity {};
    if (::uname(&identity) != 0)
        throw std::runtime_error(errno_message(label + " uname", errno));
    const std::string_view release(identity.release);
    std::size_t cursor = 0U;
    const auto parse = [&](const std::string& component) {
        if (cursor >= release.size() || release[cursor] < '0' ||
            release[cursor] > '9')
            throw std::runtime_error(
                label + " uname release has no " + component);
        unsigned long value = 0UL;
        while (cursor < release.size() && release[cursor] >= '0' &&
               release[cursor] <= '9') {
            const unsigned long digit =
                static_cast<unsigned long>(release[cursor] - '0');
            if (value > (std::numeric_limits<unsigned long>::max() - digit) /
                            10UL)
                throw std::overflow_error(
                    label + " uname release component overflows");
            value = value * 10UL + digit;
            ++cursor;
        }
        return value;
    };
    const unsigned long major = parse("major version");
    if (cursor >= release.size() || release[cursor] != '.')
        throw std::runtime_error(label + " uname release lacks minor version");
    ++cursor;
    return {major, parse("minor version")};
}

[[nodiscard]] NamespaceIdentity read_time_namespace_or_throw(
    const std::string& label) {
    struct stat status {};
    const int stat_result = ::stat("/proc/thread-self/ns/time", &status);
    const int stat_error = stat_result == 0 ? 0 : errno;
    if (stat_result == 0) {
        if (status.st_ino == 0)
            throw std::runtime_error(
                label + " time namespace identity is invalid");
        return {
            static_cast<std::uint64_t>(status.st_dev),
            static_cast<std::uint64_t>(status.st_ino),
            sync_replica_outbox_clock_linux_detail::
                TimeNamespaceProbeClassification::Bound};
    }

    unsigned long kernel_major = 0UL;
    unsigned long kernel_minor = 0UL;
    if (stat_error == ENOENT) {
        const auto version = linux_kernel_major_minor_or_throw(label);
        kernel_major = version.first;
        kernel_minor = version.second;
    }
    const auto classification =
        sync_replica_outbox_clock_linux_detail::classify_time_namespace_probe(
            stat_result, stat_error, kernel_major, kernel_minor);
    switch (classification) {
        case sync_replica_outbox_clock_linux_detail::
            TimeNamespaceProbeClassification::AbsentBeforeMainlineFeature:
        case sync_replica_outbox_clock_linux_detail::
            TimeNamespaceProbeClassification::IdentityUnavailable:
            return {0U, 0U, classification};
        case sync_replica_outbox_clock_linux_detail::
            TimeNamespaceProbeClassification::FatalError:
            throw std::runtime_error(
                errno_message(label + " stat time namespace", stat_error));
        case sync_replica_outbox_clock_linux_detail::
            TimeNamespaceProbeClassification::Bound:
            break;
    }
    throw std::logic_error(label + " time namespace probe was inconsistent");
}

[[nodiscard]] std::uint64_t timespec_to_ns_or_throw(
    const struct timespec& value,
    const std::string& label) {
    if (value.tv_sec < 0 || value.tv_nsec < 0 || value.tv_nsec >= 1000000000L)
        throw std::runtime_error(label + " returned an invalid timespec");
    const std::uint64_t seconds = static_cast<std::uint64_t>(value.tv_sec);
    if (seconds > std::numeric_limits<std::uint64_t>::max() /
                      kSyncReplicaNanosecondsPerSecond)
        throw std::overflow_error(label + " timespec overflows uint64_t");
    const std::uint64_t whole_seconds =
        seconds * kSyncReplicaNanosecondsPerSecond;
    const std::uint64_t nanoseconds =
        static_cast<std::uint64_t>(value.tv_nsec);
    if (nanoseconds >
        std::numeric_limits<std::uint64_t>::max() - whole_seconds)
        throw std::overflow_error(label + " timespec overflows uint64_t");
    return whole_seconds + nanoseconds;
}

[[nodiscard]] std::uint64_t checked_add_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left)
        throw std::overflow_error(label + " overflows uint64_t");
    return left + right;
}

[[nodiscard]] std::uint64_t timex_realtime_ns_or_throw(
    const struct timex& value,
    const std::string& label) {
    if (value.time.tv_sec <= 0 || value.time.tv_usec < 0)
        throw std::runtime_error(label + " adjtimex returned invalid realtime");
    const bool nanoseconds = (value.status & STA_NANO) != 0;
    const long limit = nanoseconds ? 1000000000L : 1000000L;
    if (value.time.tv_usec >= limit)
        throw std::runtime_error(label + " adjtimex returned invalid subsecond");
    const std::uint64_t seconds =
        static_cast<std::uint64_t>(value.time.tv_sec);
    if (seconds > std::numeric_limits<std::uint64_t>::max() /
                      kSyncReplicaNanosecondsPerSecond)
        throw std::overflow_error(label + " realtime overflows uint64_t");
    const std::uint64_t subsecond = nanoseconds
        ? static_cast<std::uint64_t>(value.time.tv_usec)
        : static_cast<std::uint64_t>(value.time.tv_usec) * 1000ULL;
    const std::uint64_t whole_seconds =
        seconds * kSyncReplicaNanosecondsPerSecond;
    if (subsecond >
        std::numeric_limits<std::uint64_t>::max() - whole_seconds)
        throw std::overflow_error(label + " realtime overflows uint64_t");
    return whole_seconds + subsecond;
}

[[nodiscard]] std::uint64_t timex_uncertainty_ns_or_throw(
    const struct timex& value,
    std::uint64_t sample_span_ns,
    const std::string& label) {
    if (value.maxerror < 0 || value.esterror < 0)
        throw std::runtime_error(label + " adjtimex returned negative error");
    const std::uint64_t kernel_error_us = std::max(
        static_cast<std::uint64_t>(value.maxerror),
        static_cast<std::uint64_t>(value.esterror));
    if (kernel_error_us > std::numeric_limits<std::uint64_t>::max() / 1000ULL)
        throw std::overflow_error(label + " adjtimex uncertainty overflows");
    return checked_add_or_throw(
        kernel_error_us * 1000ULL, sample_span_ns,
        label + " total uncertainty");
}

[[nodiscard]] std::string time_namespace_digest(
    const NamespaceIdentity& identity) {
    using Classification = sync_replica_outbox_clock_linux_detail::
        TimeNamespaceProbeClassification;
    switch (identity.classification) {
        case Classification::Bound:
            return sha256_hex(
                "anonsync-linux-time-namespace-v1:" +
                std::to_string(identity.device) + ":" +
                std::to_string(identity.inode));
        case Classification::AbsentBeforeMainlineFeature:
            return sha256_hex(
                "anonsync-linux-time-namespace-v1:"
                "absent-before-mainline-5.6");
        case Classification::IdentityUnavailable:
            return sha256_hex(
                "anonsync-linux-time-namespace-v1:identity-unavailable");
        case Classification::FatalError:
            break;
    }
    throw std::logic_error("time namespace identity classification is fatal");
}

[[nodiscard]] std::string clock_source_id(
    bool has_adjtimex,
    const NamespaceIdentity& identity) {
    using Classification = sync_replica_outbox_clock_linux_detail::
        TimeNamespaceProbeClassification;
    const std::string_view clock = has_adjtimex ? "adjtimex" : "realtime";
    std::string_view namespace_status;
    switch (identity.classification) {
        case Classification::Bound:
            namespace_status = "timens";
            break;
        case Classification::AbsentBeforeMainlineFeature:
            namespace_status = "timens-pre-mainline-unavailable";
            break;
        case Classification::IdentityUnavailable:
            namespace_status = "timens-unavailable";
            break;
        case Classification::FatalError:
            throw std::logic_error(
                "fatal time namespace classification reached source id");
    }
    return "linux-boottime-" + std::string(clock) + "-" +
           std::string(namespace_status) + "-v1";
}

[[nodiscard]] bool operator_clock_authority_id_is_valid(
    std::string_view value) noexcept {
    if (value.empty() || value.size() > 128U) return false;
    const auto lower_alnum = [](char byte) noexcept {
        return (byte >= 'a' && byte <= 'z') ||
               (byte >= '0' && byte <= '9');
    };
    if (!lower_alnum(value.front()) || !lower_alnum(value.back())) {
        return false;
    }
    return std::all_of(value.begin(), value.end(), [&](char byte) {
        return lower_alnum(byte) || byte == '-' || byte == '_' || byte == '.';
    });
}

void validate_operator_clock_profile_or_throw(
    const SyncReplicaOperatorTrustedClockProfile& profile) {
    if (!operator_clock_authority_id_is_valid(profile.authority_id)) {
        throw std::invalid_argument(
            "operator-trusted clock authority ID is not canonical");
    }
    if (profile.claimed_uncertainty_ns == 0U ||
        profile.claimed_uncertainty_ns >
            kSyncReplicaOutboxClockHardMaxUncertaintyNs) {
        throw std::invalid_argument(
            "operator-trusted clock uncertainty must be in 1..60000000000 ns");
    }
}

[[nodiscard]] std::string operator_time_namespace_material_or_throw(
    const std::string& label) {
    struct stat status {};
    if (::stat("/proc/thread-self/ns/time", &status) == 0) {
        if (status.st_ino == 0) {
            throw std::runtime_error(
                label + " time namespace identity is invalid");
        }
        return "bound:" +
               std::to_string(static_cast<std::uint64_t>(status.st_dev)) +
               ":" +
               std::to_string(static_cast<std::uint64_t>(status.st_ino));
    }
    const int error = errno;
    if (error == ENOENT) return "unavailable:missing";
    if (error == EACCES || error == EPERM) {
        return "unavailable:permission-denied";
    }
    throw std::runtime_error(
        errno_message(label + " stat time namespace", error));
}

class OperatorTrustedSyncReplicaOutboxClockSource final
    : public SyncReplicaOutboxClockSource {
public:
    explicit OperatorTrustedSyncReplicaOutboxClockSource(
        SyncReplicaOperatorTrustedClockProfile profile)
        : profile_(std::move(profile)),
          source_id_(
              "operator-trusted-clock-v1-" +
              sha256_hex(profile_.authority_id).substr(0U, 24U)) {
        validate_operator_clock_profile_or_throw(profile_);
    }

    SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string& label) override {
        const std::string boot_before = observe_linux_boot_id_or_throw(
            label + " operator-trusted boot_id before sample");
        const std::string namespace_before =
            operator_time_namespace_material_or_throw(label);

        struct timespec before {};
        struct timespec realtime {};
        struct timespec after {};
        if (::clock_gettime(CLOCK_BOOTTIME, &before) != 0) {
            throw std::runtime_error(errno_message(
                label + " operator-trusted clock_gettime before", errno));
        }
        if (::clock_gettime(CLOCK_REALTIME, &realtime) != 0) {
            throw std::runtime_error(errno_message(
                label + " operator-trusted clock_gettime realtime", errno));
        }
        if (::clock_gettime(CLOCK_BOOTTIME, &after) != 0) {
            throw std::runtime_error(errno_message(
                label + " operator-trusted clock_gettime after", errno));
        }

        const std::string namespace_after =
            operator_time_namespace_material_or_throw(label);
        const std::string boot_after = observe_linux_boot_id_or_throw(
            label + " operator-trusted boot_id after sample");
        if (boot_before != boot_after) {
            throw std::runtime_error(
                label + " operator-trusted boot identity changed during sample");
        }
        if (namespace_before != namespace_after) {
            throw std::runtime_error(
                label + " operator-trusted time namespace changed during sample");
        }

        const std::uint64_t before_ns = timespec_to_ns_or_throw(
            before, label + " operator-trusted boottime before");
        const std::uint64_t after_ns = timespec_to_ns_or_throw(
            after, label + " operator-trusted boottime after");
        if (after_ns < before_ns) {
            throw std::runtime_error(
                label + " operator-trusted boottime moved backward in sample");
        }
        const std::uint64_t span_ns = after_ns - before_ns;
        const std::uint64_t total_uncertainty = checked_add_or_throw(
            profile_.claimed_uncertainty_ns, span_ns,
            label + " operator-trusted total uncertainty");
        if (total_uncertainty >
            kSyncReplicaOutboxClockHardMaxUncertaintyNs) {
            throw std::runtime_error(
                label +
                " operator-trusted sample exceeds hard uncertainty maximum");
        }

        SyncReplicaOutboxClockObservation observation;
        observation.source_id = source_id_;
        observation.boot_id = boot_before;
        observation.time_namespace_id = sha256_hex(
            "anonsync-operator-trusted-time-namespace-v1:" +
            profile_.authority_id + ":" + namespace_before);
        observation.realtime_ns = timespec_to_ns_or_throw(
            realtime, label + " operator-trusted realtime");
        observation.boottime_ns = before_ns + span_ns / 2U;
        observation.uncertainty_ns = total_uncertainty;
        observation.synchronization =
            SyncReplicaOutboxClockSynchronization::Synchronized;
        validate_sync_replica_outbox_clock_observation_or_throw(
            observation, label + " operator-trusted observation");
        return observation;
    }

private:
    SyncReplicaOperatorTrustedClockProfile profile_;
    std::string source_id_;
};

class LinuxSyncReplicaOutboxClockSource final
    : public SyncReplicaOutboxClockSource {
public:
    SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string& label) override {
        const std::string boot_before = observe_linux_boot_id_or_throw(
            label + " boot_id before sample");
        const NamespaceIdentity namespace_before =
            read_time_namespace_or_throw(label);

        struct timespec before {};
        if (::clock_gettime(CLOCK_BOOTTIME, &before) != 0)
            throw std::runtime_error(
                errno_message(label + " clock_gettime before", errno));
        struct timex kernel_time {};
        const int clock_state = ::adjtimex(&kernel_time);
        const int adjtimex_error = clock_state < 0 ? errno : 0;
        const bool has_adjtimex = clock_state >= 0;
        struct timespec fallback_realtime {};
        if (!has_adjtimex) {
            if (adjtimex_error != EPERM && adjtimex_error != EACCES &&
                adjtimex_error != ENOSYS)
                throw std::runtime_error(
                    errno_message(label + " adjtimex", adjtimex_error));
            if (::clock_gettime(CLOCK_REALTIME, &fallback_realtime) != 0)
                throw std::runtime_error(
                    errno_message(label + " clock_gettime realtime", errno));
        }
        struct timespec after {};
        if (::clock_gettime(CLOCK_BOOTTIME, &after) != 0)
            throw std::runtime_error(
                errno_message(label + " clock_gettime after", errno));

        const NamespaceIdentity namespace_after =
            read_time_namespace_or_throw(label);
        const std::string boot_after = observe_linux_boot_id_or_throw(
            label + " boot_id after sample");
        if (boot_before != boot_after)
            throw std::runtime_error(label + " boot identity changed during sample");
        if (namespace_before != namespace_after)
            throw std::runtime_error(
                label + " time namespace changed during sample");

        const std::uint64_t before_ns =
            timespec_to_ns_or_throw(before, label + " boottime before");
        const std::uint64_t after_ns =
            timespec_to_ns_or_throw(after, label + " boottime after");
        if (after_ns < before_ns)
            throw std::runtime_error(label + " boottime moved backward in sample");
        const std::uint64_t span_ns = after_ns - before_ns;

        SyncReplicaOutboxClockObservation observation;
        observation.source_id =
            clock_source_id(has_adjtimex, namespace_before);
        observation.boot_id = boot_before;
        observation.time_namespace_id = time_namespace_digest(namespace_before);
        observation.realtime_ns = has_adjtimex
            ? timex_realtime_ns_or_throw(kernel_time, label)
            : timespec_to_ns_or_throw(
                  fallback_realtime, label + " realtime fallback");
        observation.boottime_ns = before_ns + span_ns / 2U;
        observation.uncertainty_ns = has_adjtimex
            ? timex_uncertainty_ns_or_throw(kernel_time, span_ns, label)
            : span_ns;
        const bool namespace_identity_is_bound =
            namespace_before.classification ==
            sync_replica_outbox_clock_linux_detail::
                TimeNamespaceProbeClassification::Bound;
        observation.synchronization =
            !namespace_identity_is_bound || !has_adjtimex
            ? SyncReplicaOutboxClockSynchronization::Unknown
            : (clock_state == TIME_ERROR ||
                       (kernel_time.status & (STA_UNSYNC | STA_CLOCKERR)) != 0
                   ? SyncReplicaOutboxClockSynchronization::Unsynchronized
                   : SyncReplicaOutboxClockSynchronization::Synchronized);
        validate_sync_replica_outbox_clock_observation_or_throw(
            observation, label + " system observation");
        return observation;
    }
};

#else

class UnsupportedSyncReplicaOutboxClockSource final
    : public SyncReplicaOutboxClockSource {
public:
    SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string& label) override {
        throw std::runtime_error(
            label + " system outbox clock source requires Linux");
    }
};

#endif

}  // namespace

std::unique_ptr<SyncReplicaOutboxClockSource>
make_system_sync_replica_outbox_clock_source() {
#if defined(__linux__)
    return std::make_unique<LinuxSyncReplicaOutboxClockSource>();
#else
    return std::make_unique<UnsupportedSyncReplicaOutboxClockSource>();
#endif
}

std::unique_ptr<SyncReplicaOutboxClockSource>
make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
    SyncReplicaOperatorTrustedClockProfile profile) {
#if defined(__linux__)
    validate_operator_clock_profile_or_throw(profile);
    return std::make_unique<OperatorTrustedSyncReplicaOutboxClockSource>(
        std::move(profile));
#else
    if (profile.authority_id.empty() ||
        profile.claimed_uncertainty_ns == 0U ||
        profile.claimed_uncertainty_ns >
            kSyncReplicaOutboxClockHardMaxUncertaintyNs) {
        throw std::invalid_argument(
            "operator-trusted clock profile is invalid");
    }
    return std::make_unique<UnsupportedSyncReplicaOutboxClockSource>();
#endif
}

}  // namespace anonsync
