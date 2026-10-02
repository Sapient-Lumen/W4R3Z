#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/update_bundle.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <utility>

namespace iotox::update {

class LifecycleWitness;

inline constexpr std::size_t kUpdateStateBodyBytes = 512U;
inline constexpr std::size_t kSignedUpdateStateBytes =
    kUpdateStateBodyBytes + security::kSignatureBytes;

using UpdateStateBody = std::array<std::uint8_t, kUpdateStateBodyBytes>;
using SignedUpdateStateBytes =
    std::array<std::uint8_t, kSignedUpdateStateBytes>;
using HealthToken = std::array<std::uint8_t, 32U>;

enum class UpdatePhase : std::uint8_t {
  staged = 1U,
  pending_restart = 2U,
  awaiting_health = 3U,
  confirmed = 4U,
  idle_after_rollback = 5U,
};

struct UpdateRevision {
  PayloadKind payload_kind{PayloadKind::opaque_slot_v1};
  std::uint64_t sequence{0U};
  std::uint64_t payload_bytes{0U};
  sync::Digest payload_digest{};
  sync::Digest manifest_record{};
  std::string version;

  [[nodiscard]] bool operator==(const UpdateRevision &) const = default;
  [[nodiscard]] bool present() const noexcept { return sequence != 0U; }
};

struct UpdateSelectedSlot {
  UpdateRevision revision;
  std::filesystem::path path;
  bool candidate{false};

  [[nodiscard]] bool operator==(const UpdateSelectedSlot &) const = default;
};

struct UpdateState {
  std::string namespace_id;
  std::string target;
  security::SigningPublicKey device{};
  UpdatePhase phase{UpdatePhase::idle_after_rollback};
  std::uint64_t generation{0U};
  std::uint64_t rollback_count{0U};
  std::uint64_t applied_incarnation{0U};
  std::uint64_t health_incarnation{0U};
  std::uint8_t boot_attempts{0U};
  UpdateRevision confirmed;
  UpdateRevision candidate;
  security::Digest health_token_digest{};
  std::uint64_t last_failed_sequence{0U};
  sync::Digest last_failed_digest{};
  security::Signature signature{};

  [[nodiscard]] bool operator==(const UpdateState &) const = default;
};

enum class StartupDisposition : std::uint8_t {
  empty = 1U,
  unchanged = 2U,
  health_window_opened = 3U,
  incomplete_apply_rolled_back = 4U,
  unconfirmed_restart_rolled_back = 5U,
};

struct UpdateStartupResult {
  StartupDisposition disposition{StartupDisposition::empty};
  std::optional<UpdateState> state;
};

struct UpdateStageResult {
  UpdateState state;
  bool duplicate{false};
  std::filesystem::path slot_path;
};

struct UpdateApplyResult {
  UpdateState state;
  HealthToken health_token{};
  std::filesystem::path slot_path;
};

enum class UpdateRetentionMode : std::uint8_t {
  dry_run = 1U,
  quarantine = 2U,
};

struct UpdateRetentionResult {
  std::uint64_t state_generation{0U};
  std::uint64_t eligible_bytes{0U};
  std::uint64_t quarantined_bytes{0U};
  std::size_t active_slots{0U};
  std::size_t protected_slots{0U};
  std::size_t eligible_slots{0U};
  std::size_t quarantined_slots{0U};
  std::size_t prior_quarantine_slots{0U};

  [[nodiscard]] bool operator==(
      const UpdateRetentionResult &) const = default;
};

[[nodiscard]] std::string_view update_phase_name(UpdatePhase phase) noexcept;
[[nodiscard]] std::string_view startup_disposition_name(
    StartupDisposition disposition) noexcept;
[[nodiscard]] Result<UpdateStateBody> encode_update_state_body(
    const UpdateState &state);
[[nodiscard]] Result<SignedUpdateStateBytes> encode_signed_update_state(
    const UpdateState &state);
[[nodiscard]] Result<UpdateState> decode_signed_update_state(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_signed_update_state(
    const UpdatePolicy &policy, const UpdateState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);

class UpdateStore {
public:
  UpdateStore(const UpdateStore &) = delete;
  UpdateStore &operator=(const UpdateStore &) = delete;
  UpdateStore(UpdateStore &&) = delete;
  UpdateStore &operator=(UpdateStore &&) = delete;
  ~UpdateStore() = default;

  [[nodiscard]] static Result<std::unique_ptr<UpdateStore>> open(
      UpdatePolicy policy, const security::DeviceIdentity &identity,
      const security::Sodium &sodium, std::uint64_t process_incarnation,
      std::shared_ptr<LifecycleWitness> witness = nullptr);

  [[nodiscard]] UpdateStartupResult startup_result() const;
  [[nodiscard]] std::optional<UpdateState> snapshot() const;
  // Resolves the exact signed revision named by the recovered current
  // pointer and independently revalidates its immutable slot before return.
  [[nodiscard]] Result<std::optional<UpdateSelectedSlot>>
  selected_slot() const;

  // BUNDLE must already be the immutable artifact named by an exact accepted
  // sync HEAD at the Agent boundary. This layer independently verifies update
  // intent and copies only the payload into an inactive digest-named slot.
  [[nodiscard]] Result<UpdateStageResult> stage(
      const std::filesystem::path &bundle);

  // The caller supplies the exact staged manifest-record token. State is made
  // pending before the derived pointer changes. Confirmation cannot occur
  // until a greater process incarnation opens the health window.
  [[nodiscard]] Result<UpdateApplyResult> apply(
      const sync::Digest &expected_manifest_record,
      std::uint64_t process_incarnation);

  [[nodiscard]] Result<UpdateState> confirm(
      const HealthToken &token, std::uint64_t process_incarnation);

  // Used by the bounded live health timer. Restart recovery invokes the same
  // rollback transition automatically when an unconfirmed second process
  // incarnation is observed.
  [[nodiscard]] Result<UpdateState> expire_health(
      std::uint64_t process_incarnation);

  // Historical slots are never unlinked. Dry-run reports every slot not
  // named by signed current state; quarantine atomically moves exactly that
  // inventory into an owner-private recovery directory. Confirmed and live
  // candidate slots are always protected.
  [[nodiscard]] Result<UpdateRetentionResult> retain_slots(
      UpdateRetentionMode mode);

  [[nodiscard]] const UpdatePolicy &policy() const noexcept { return policy_; }

private:
  UpdateStore(UpdatePolicy policy, const security::DeviceIdentity &identity,
              const security::Sodium &sodium,
              std::shared_ptr<LifecycleWitness> witness)
      : policy_(std::move(policy)), identity_(&identity), sodium_(&sodium),
        witness_(std::move(witness)) {}

  [[nodiscard]] Status initialize(std::uint64_t process_incarnation);
  [[nodiscard]] Result<std::optional<UpdateState>> load_state() const;
  [[nodiscard]] Result<std::optional<SignedUpdateStateBytes>>
  load_state_bytes() const;
  [[nodiscard]] Status install_state_bytes(
      const SignedUpdateStateBytes &bytes) const;
  [[nodiscard]] Status store_state(UpdateState &state) const;
  [[nodiscard]] Status validate_slot(const UpdateRevision &revision) const;
  [[nodiscard]] std::filesystem::path slot_path(
      const UpdateRevision &revision) const;
  [[nodiscard]] Result<UpdateState> rollback_candidate(
      UpdateState state, StartupDisposition disposition);

  UpdatePolicy policy_;
  const security::DeviceIdentity *identity_{nullptr};
  const security::Sodium *sodium_{nullptr};
  std::shared_ptr<LifecycleWitness> witness_;
  mutable std::mutex mutex_;
  std::optional<UpdateState> state_;
  UpdateStartupResult startup_;
};

} // namespace iotox::update
