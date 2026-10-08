#pragma once

#include <cerrno>
#include <cstdint>

namespace anonsync::sync_replica_outbox_clock_linux_detail {

// A kernel release at or after Linux 5.6 is only a feature-generation hint.
// CONFIG_TIME_NS is optional and procfs may intentionally hide namespace
// handles, so this predicate must never be interpreted as a capability proof.
[[nodiscard]] constexpr bool
mainline_generation_may_expose_time_namespaces(
    unsigned long major,
    unsigned long minor) noexcept {
    return major > 5UL || (major == 5UL && minor >= 6UL);
}

enum class TimeNamespaceProbeClassification : std::uint8_t {
    Bound = 0U,
    AbsentBeforeMainlineFeature = 1U,
    IdentityUnavailable = 2U,
    FatalError = 3U,
};

// Classify the observable result without converting a kernel-version hint into
// a capability claim.  Only a successful stat proves that the calling thread's
// time namespace identity is bound.  Missing or permission-hidden identity on
// a feature-generation kernel is evidence of unavailable identity, not proof
// that time namespaces are supported or unsupported by that running kernel.
[[nodiscard]] constexpr TimeNamespaceProbeClassification
classify_time_namespace_probe(
    int stat_result,
    int stat_error,
    unsigned long kernel_major,
    unsigned long kernel_minor) noexcept {
    if (stat_result == 0)
        return TimeNamespaceProbeClassification::Bound;
    if (stat_error == ENOENT) {
        return mainline_generation_may_expose_time_namespaces(
                   kernel_major, kernel_minor)
            ? TimeNamespaceProbeClassification::IdentityUnavailable
            : TimeNamespaceProbeClassification::AbsentBeforeMainlineFeature;
    }
    if (stat_error == EACCES || stat_error == EPERM)
        return TimeNamespaceProbeClassification::IdentityUnavailable;
    return TimeNamespaceProbeClassification::FatalError;
}

}  // namespace anonsync::sync_replica_outbox_clock_linux_detail
