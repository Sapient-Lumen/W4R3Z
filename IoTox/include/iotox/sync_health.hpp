#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <filesystem>
#include <string_view>

namespace iotox::sync {

enum class NamespaceHealthLevel : std::uint8_t {
    green = 1U,
    yellow = 2U,
    red = 3U,
};

inline constexpr std::uint32_t kHealthPolicyVerified = 1U << 0U;
inline constexpr std::uint32_t kHealthMembershipVerified = 1U << 1U;
inline constexpr std::uint32_t kHealthFrontierVerified = 1U << 2U;
inline constexpr std::uint32_t kHealthMaintenanceVerified = 1U << 3U;
inline constexpr std::uint32_t kHealthWorkspacePresent = 1U << 4U;
inline constexpr std::uint32_t kHealthWorkspaceStable = 1U << 5U;
inline constexpr std::uint32_t kHealthWorkspaceCurrent = 1U << 6U;
inline constexpr std::uint32_t kHealthWorktreeClean = 1U << 7U;
inline constexpr std::uint32_t kHealthSelectedCoverageComplete = 1U << 8U;
inline constexpr std::uint32_t kHealthCustodyComplete = 1U << 9U;
inline constexpr std::uint32_t kHealthAutomationConfigured = 1U << 10U;
inline constexpr std::uint32_t kHealthAutomationStalled = 1U << 11U;
inline constexpr std::uint32_t kHealthStorePressure = 1U << 12U;
inline constexpr std::uint32_t kHealthSourceObserved = 1U << 13U;
inline constexpr std::uint32_t kHealthSourceExhausted = 1U << 14U;
inline constexpr std::uint32_t kKnownNamespaceHealthFlags =
    kHealthPolicyVerified | kHealthMembershipVerified |
    kHealthFrontierVerified | kHealthMaintenanceVerified |
    kHealthWorkspacePresent | kHealthWorkspaceStable |
    kHealthWorkspaceCurrent | kHealthWorktreeClean |
    kHealthSelectedCoverageComplete | kHealthCustodyComplete |
    kHealthAutomationConfigured | kHealthAutomationStalled |
    kHealthStorePressure | kHealthSourceObserved | kHealthSourceExhausted;

// A content-free observation. Digests bind the namespace and complete local
// policy without storing its name, paths, members, or content in this record.
struct NamespaceHealthObservation {
    std::uint64_t observed_unix_ms{0U};
    Engine engine{Engine::tree_v2};
    std::uint32_t flags{0U};
    security::Digest namespace_commitment{};
    security::Digest policy_commitment{};
    std::uint64_t frontier_writers{0U};
    std::uint64_t namespace_writers{0U};
    std::uint64_t subscribers{0U};
    std::uint64_t writer_cutoffs{0U};
    std::uint64_t conflicts{0U};
    std::uint64_t desired_objects{0U};
    std::uint64_t verified_objects{0U};
    std::uint64_t missing_objects{0U};
    std::uint64_t desired_bytes{0U};
    std::uint64_t verified_bytes{0U};
    std::uint64_t store_bytes{0U};
    std::uint64_t store_limit_bytes{0U};
    std::uint64_t source_count{0U};
    std::uint64_t source_absent{0U};
    std::uint64_t source_unavailable{0U};
    std::uint64_t consecutive_automation_failures{0U};

    [[nodiscard]] bool
    operator==(const NamespaceHealthObservation &) const = default;
};

struct NamespaceHealthRecord {
    std::uint64_t sequence{0U};
    NamespaceHealthLevel level{NamespaceHealthLevel::red};
    NamespaceHealthObservation observation;
    security::SigningPublicKey signer{};
    security::Signature signature{};

    [[nodiscard]] bool operator==(const NamespaceHealthRecord &) const =
        default;
};

[[nodiscard]] std::string_view
namespace_health_level_name(NamespaceHealthLevel level) noexcept;
[[nodiscard]] Result<NamespaceHealthLevel>
classify_namespace_health(const NamespaceHealthObservation &observation);
[[nodiscard]] Result<NamespaceHealthObservation>
bind_namespace_health_observation(const NamespacePolicy &policy,
                                  NamespaceHealthObservation observation,
                                  const security::Sodium &sodium);
[[nodiscard]] Result<NamespaceHealthRecord>
load_namespace_health(const NamespacePolicy &policy,
                      const security::SigningPublicKey &expected_device,
                      const security::Sodium &sodium);
// The namespace transaction must serialize commits when multiple callers can
// refresh one namespace concurrently. The Agent holds it around observation
// collection and this commit.
[[nodiscard]] Result<NamespaceHealthRecord>
commit_namespace_health(const NamespacePolicy &policy,
                        NamespaceHealthObservation observation,
                        const security::DeviceIdentity &identity,
                        const security::Sodium &sodium);
[[nodiscard]] bool namespace_health_policy_current(
    const NamespacePolicy &policy, const NamespaceHealthRecord &record,
    const security::Sodium &sodium);
[[nodiscard]] std::filesystem::path
namespace_health_path(const NamespacePolicy &policy);

} // namespace iotox::sync
