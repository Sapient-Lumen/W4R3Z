#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/update_state.hpp"

#include <filesystem>
#include <functional>
#include <memory>
#include <optional>

namespace iotox::update {

// Exact-state coordinator for the update policy and signed lifecycle state.
// The selected-slot symlink is deliberately excluded: it is a derived effect
// repaired from the externally committed signed state after reconciliation.
class LifecycleWitness {
public:
  struct Config {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    std::filesystem::path intent_path;
    bool allow_non_independent_for_testing{false};
  };

  using LoadState = std::function<
      Result<std::optional<SignedUpdateStateBytes>>() >;
  using InstallState =
      std::function<Status(const SignedUpdateStateBytes &)>;

  LifecycleWitness(Config config, UpdatePolicy policy,
                   const security::DeviceIdentity &identity,
                   const security::Sodium &sodium);

  [[nodiscard]] Result<rollback_witness::Record> enrollment_record(
      const std::optional<SignedUpdateStateBytes> &state) const;
  [[nodiscard]] Result<rollback_witness::Head> verify_and_recover(
      const LoadState &load, const InstallState &install) const;
  [[nodiscard]] Result<rollback_witness::Head> transition(
      const SignedUpdateStateBytes &next, const LoadState &load,
      const InstallState &install) const;

private:
  Config config_;
  UpdatePolicy policy_;
  const security::DeviceIdentity *identity_{nullptr};
  const security::Sodium *sodium_{nullptr};
};

[[nodiscard]] Result<security::Digest> update_lifecycle_digest(
    const UpdatePolicy &policy,
    const std::optional<SignedUpdateStateBytes> &state,
    const security::Sodium &sodium);

} // namespace iotox::update
