#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/route_inventory.hpp"

#include <filesystem>
#include <memory>
#include <optional>

namespace iotox::routes {

struct StoredRouteSet {
    RouteSet route_set;
    security::Digest artifact_digest{};
    std::uint64_t generation_high_water{0U};
};

struct RouteWitnessConfig {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    std::filesystem::path intent_path;
    bool allow_non_independent_for_testing{false};
};

class RouteSetStore {
  public:
    struct Config {
        std::filesystem::path artifact_path;
        std::filesystem::path generation_state_path;
        std::optional<RouteWitnessConfig> witness;
    };

    // Loads one private signed artifact while holding the generation-state
    // lock. A newer generation is durably checkpointed before it is returned;
    // older or same-generation-different-content artifacts fail closed.
    [[nodiscard]] static Result<StoredRouteSet> open(
        Config config, const security::DeviceIdentity &identity,
        const security::Sodium &sodium);

    // Read-only counterpart for deployment preflight. It verifies the signed
    // artifact and any existing generation high-water record but never opens
    // a lock file, adopts state, or advances the durable high-water mark.
    [[nodiscard]] static Result<StoredRouteSet> inspect(
        Config config, const security::DeviceIdentity &identity,
        const security::Sodium &sodium);

    // Produces the exact committed service record for an explicit quiescent
    // enrollment ceremony. The newest signed artifact is authoritative even
    // when it has not yet been copied into the local generation checkpoint.
    [[nodiscard]] static Result<rollback_witness::Record> witness_enrollment(
        Config config, const security::DeviceIdentity &identity,
        const security::Sodium &sodium,
        rollback_witness::DomainId domain, std::uint64_t witness_epoch);
};

[[nodiscard]] std::filesystem::path default_route_generation_state_path(
    const std::filesystem::path &artifact_path);

}  // namespace iotox::routes
