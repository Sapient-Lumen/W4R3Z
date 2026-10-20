#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <filesystem>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

inline constexpr std::uint32_t kDefaultSyncAutomationIntervalMs = 30000U;
inline constexpr std::uint32_t kDefaultSyncAutomationRetryInitialMs = 1000U;
inline constexpr std::uint32_t kDefaultSyncAutomationRetryMaximumMs = 300000U;
inline constexpr std::uint32_t kDefaultSyncSourceWatchDebounceMs = 250U;
inline constexpr std::uint32_t
    kDefaultTreeV2SourceWatchBusyRepublishDelayMs = 5000U;
inline constexpr std::size_t kMaximumSyncAutomationPathBytes = 4096U;
// Tree-v2 carries at most sixteen writer branches in one bounded inventory.
// One belongs to this device, leaving fifteen directly scheduled peers.
inline constexpr std::size_t kMaximumSyncAutomationSourcePrincipals = 15U;
inline constexpr std::uint8_t kCurrentSyncAutomationRecordFormat = 2U;

enum class SyncAutomationMode : std::uint8_t {
    disabled = 1U,
    publish = 2U,
    follow = 3U,
    writable = 4U,
    bidirectional = 5U,
};

enum class SyncAutomationActivation : std::uint8_t {
  pull_only = 1U,
  verified = 2U,
};

struct SyncAutomationSpec {
  std::string namespace_id;
  SyncAutomationMode mode{SyncAutomationMode::disabled};
  SyncAutomationActivation activation{SyncAutomationActivation::pull_only};
  std::vector<PrincipalId> source_principals;
  std::string source_path;
  std::uint32_t interval_ms{kDefaultSyncAutomationIntervalMs};
  std::uint32_t retry_initial_ms{kDefaultSyncAutomationRetryInitialMs};
  std::uint32_t retry_maximum_ms{kDefaultSyncAutomationRetryMaximumMs};

  [[nodiscard]] bool operator==(const SyncAutomationSpec &) const = default;
};

struct SyncAutomationPolicy : SyncAutomationSpec {
  std::uint8_t record_format{kCurrentSyncAutomationRecordFormat};
  std::uint64_t generation{0U};
  security::SigningPublicKey signer{};
  security::Signature signature{};

  [[nodiscard]] bool operator==(const SyncAutomationPolicy &) const = default;
};

enum class SyncAutomationStoreDecision : std::uint8_t {
  created = 1U,
  replaced = 2U,
  disabled = 3U,
  duplicate = 4U,
};

struct SyncAutomationStoreResult {
  SyncAutomationStoreDecision decision{SyncAutomationStoreDecision::created};
  SyncAutomationPolicy policy;
};

[[nodiscard]] std::string_view
sync_automation_mode_name(SyncAutomationMode mode) noexcept;
[[nodiscard]] std::string_view
sync_automation_activation_name(SyncAutomationActivation activation) noexcept;
[[nodiscard]] std::string_view sync_automation_store_decision_name(
    SyncAutomationStoreDecision decision) noexcept;
[[nodiscard]] Status validate_sync_automation_spec(
    const SyncAutomationSpec &spec);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_automation_policy(const SyncAutomationPolicy &policy);
[[nodiscard]] Result<SyncAutomationPolicy>
decode_sync_automation_policy(std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_sync_automation_policy(
    const SyncAutomationPolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);

class SyncAutomationStore final {
public:
  explicit SyncAutomationStore(std::filesystem::path policy_root);

  [[nodiscard]] Result<std::vector<SyncAutomationPolicy>>
  load(const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Result<SyncAutomationStoreResult>
  put(const SyncAutomationSpec &spec,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<SyncAutomationStoreResult>
  disable(std::string_view namespace_id,
          const security::DeviceIdentity &identity,
          const security::Sodium &sodium);

  [[nodiscard]] const std::filesystem::path &root() const noexcept {
    return root_;
  }

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
};

enum class SyncAutomationActionKind : std::uint8_t {
  publish = 1U,
  pull = 2U,
  activate = 3U,
};

struct SyncAutomationAction {
  SyncAutomationActionKind kind{SyncAutomationActionKind::publish};
  SyncAutomationPolicy policy;
  PrincipalId source_principal{};

  [[nodiscard]] bool operator==(const SyncAutomationAction &) const = default;
};

struct SyncAutomationRuntimeSnapshot {
  std::string namespace_id;
  SyncAutomationMode mode{SyncAutomationMode::disabled};
  SyncAutomationActivation activation{SyncAutomationActivation::pull_only};
  std::uint64_t policy_generation{0U};
  bool periodic_busy{false};
  bool activation_busy{false};
  bool source_publish_pending{false};
  std::uint64_t next_periodic_ms{0U};
  std::uint64_t next_activation_ms{0U};
  std::uint64_t periodic_attempts{0U};
  std::uint64_t periodic_successes{0U};
  std::uint64_t periodic_failures{0U};
  std::uint64_t activation_attempts{0U};
  std::uint64_t activation_successes{0U};
  std::uint64_t activation_failures{0U};
  std::uint64_t consecutive_periodic_failures{0U};
  std::uint64_t consecutive_activation_failures{0U};
  ErrorCode last_periodic_error{ErrorCode::ok};
  ErrorCode last_activation_error{ErrorCode::ok};
};

class SyncAutomationScheduler final {
public:
  [[nodiscard]] Status replace(
      std::vector<SyncAutomationPolicy> policies, std::uint64_t now_ms);
  [[nodiscard]] std::vector<SyncAutomationAction>
  claim_periodic(std::uint64_t now_ms);
  // Accelerates local-source publication/reconciliation after an observed
  // filesystem change. It never mutates the durable signed automation policy;
  // the normal periodic/retry schedule remains the fallback if events are
  // unavailable or dropped.
  [[nodiscard]] Status trigger_source_change(std::string_view namespace_id,
                                             std::uint64_t now_ms,
                                             std::uint32_t debounce_ms = 0U,
                                             std::uint32_t
                                                 busy_republish_delay_ms = 0U);
  [[nodiscard]] Result<SyncAutomationAction>
  claim_activation(std::string_view namespace_id, std::uint64_t now_ms);
  [[nodiscard]] Status complete(const SyncAutomationAction &action,
                                ErrorCode outcome,
                                std::uint64_t now_ms);
  [[nodiscard]] std::vector<SyncAutomationRuntimeSnapshot> snapshot() const;

private:
  struct PeerRuntime {
    std::uint64_t next_ms{0U};
    std::uint64_t consecutive_failures{0U};
  };

  struct Entry {
    SyncAutomationPolicy policy;
    SyncAutomationRuntimeSnapshot runtime;
    std::size_t next_source_index{0U};
    std::optional<std::uint64_t> next_source_publish_ms;
    std::uint32_t source_republish_delay_ms{0U};
    std::vector<PeerRuntime> peer_runtime;
  };

  mutable std::mutex mutex_;
  std::vector<Entry> entries_;
};

} // namespace iotox::sync
