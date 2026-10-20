#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>

namespace iotox::interactive {

struct IncarnationWitnessConfig {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Lane lane{
        rollback_witness::Lane::application_incarnation};
    std::filesystem::path intent_path;
    bool allow_non_independent_for_testing{false};
};

// A process-lifetime lease over a durable application or Ratox incarnation
// lane. The historical class name is retained as an internal source API.
//
// The signed record is public metadata, not a secret. Its purpose is to bind a
// monotonically advancing host namespace to the device identity and to prevent
// two legitimate IoTox processes from entering the same namespace at once.
// The advisory lock remains held until this object is destroyed or reset.
class RatoxIncarnationLease {
  public:
    RatoxIncarnationLease() = default;
    ~RatoxIncarnationLease();

    RatoxIncarnationLease(const RatoxIncarnationLease &) = delete;
    RatoxIncarnationLease &operator=(const RatoxIncarnationLease &) = delete;
    RatoxIncarnationLease(RatoxIncarnationLease &&other) noexcept;
    RatoxIncarnationLease &operator=(RatoxIncarnationLease &&other) noexcept;

    [[nodiscard]] static Result<RatoxIncarnationLease> acquire(
        const std::filesystem::path &state_path,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium,
        std::optional<IncarnationWitnessConfig> witness = std::nullopt);

    [[nodiscard]] bool valid() const noexcept { return lock_descriptor_ >= 0; }
    [[nodiscard]] std::uint64_t incarnation() const noexcept {
        return incarnation_;
    }
    [[nodiscard]] const std::filesystem::path &state_path() const noexcept {
        return state_path_;
    }

    void reset() noexcept;

  private:
    RatoxIncarnationLease(
        std::filesystem::path state_path,
        std::uint64_t incarnation,
        int lock_descriptor) noexcept
        : state_path_(std::move(state_path)),
          incarnation_(incarnation),
          lock_descriptor_(lock_descriptor) {}

    std::filesystem::path state_path_;
    std::uint64_t incarnation_{0U};
    int lock_descriptor_{-1};
};

// Read the exact current local head without advancing it. The same lane lock
// used by acquire() is held during inspection, so this is suitable for an
// explicit quiescent enrollment ceremony. An absent state maps to position
// zero and the all-zero digest.
[[nodiscard]] Result<rollback_witness::Record>
incarnation_witness_enrollment_record(
    const std::filesystem::path &state_path,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    rollback_witness::DomainId domain,
    std::uint64_t witness_epoch,
    rollback_witness::Lane lane);

[[nodiscard]] std::filesystem::path default_ratox_incarnation_state_path(
    const std::filesystem::path &tox_savedata_path);

}  // namespace iotox::interactive
