#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>

namespace iotox::policy_witness {

// A reusable exact-head freshness transaction for low-churn, owner-reviewed
// policy trees. The policy bytes remain owned by their subsystem; this layer
// signs only a monotonic position and the subsystem's canonical digest.
struct Config {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Lane lane{rollback_witness::Lane::terminal_policy};
    std::filesystem::path checkpoint_path;
    std::filesystem::path intent_path;
    bool allow_non_independent_for_testing{false};
};

struct Checkpoint {
    rollback_witness::Lane lane{rollback_witness::Lane::terminal_policy};
    rollback_witness::Head head{};
};

// Read-only local inspection. Absence is reported as ErrorCode::not_found.
[[nodiscard]] Result<Checkpoint> inspect_checkpoint(
    const std::filesystem::path &path,
    const security::SigningPublicKey &device,
    const security::Sodium &sodium);

// Produces an explicit service enrollment record without changing local or
// remote state. An absent checkpoint starts at position one; an existing
// checkpoint must already describe the exact reviewed policy digest.
[[nodiscard]] Result<rollback_witness::Record> enrollment_record(
    const std::filesystem::path &checkpoint_path,
    const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::DomainId domain,
    std::uint64_t witness_epoch,
    rollback_witness::Lane lane);

// Startup boundary. It may complete a transition that already has the exact
// durable signed intent, but it never blesses a newly observed policy digest.
// The returned value is the externally committed policy position.
[[nodiscard]] Result<std::uint64_t> verify(
    const Config &config,
    const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium);

// Explicit quiescent review boundary. A changed policy digest advances by
// exactly one durable pending/committed transaction; an unchanged digest is
// only reconciled and verified.
[[nodiscard]] Result<std::uint64_t> commit(
    const Config &config,
    const security::Digest &policy_digest,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium);

}  // namespace iotox::policy_witness
