#pragma once

#include "iotox/route_inventory.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

struct SyncRangePlan;

// Zero deliberately means an ordinary live process-owned attempt so the
// original ATM1 journal encoding remains canonical and readable. Startup may
// change only a strict positive incomplete canonical partial to
// restart_retained; no dead route or worker is thereby resurrected.
enum class DurableSyncAttemptState : std::uint8_t {
  active = 0U,
  restart_retained = 1U,
};

// Zero preserves the original journal encoding. Range bundles name their
// target object in the scheduler but contain only concatenated missing spans;
// they must never be interpreted as a whole-object prefix after restart.
enum class DurableSyncAttemptMode : std::uint8_t {
  whole_object = 0U,
  range_bundle = 1U,
};

// Zero preserves every historical ATM1 record. Plan-bound range attempts use
// one formerly reserved byte so startup can distinguish the new commitment
// fields from legacy range route/worker fields and fence legacy bytes safely.
enum class DurableSyncAttemptBinding : std::uint8_t {
  route_worker = 0U,
  range_plan_v1 = 1U,
};

struct DurableSyncAttempt {
  std::uint64_t attempt_id{0U};
  SyncObjectRecord object;
  // Whole-object attempts retain their forensic route/worker binding. For a
  // range_bundle these same fixed ATM1 fields instead hold the canonical
  // range-plan commitment and exact bundle byte length. A range prefix is not
  // meaningful without both facts.
  routes::ToxPublicKey route_key{};
  std::uint64_t worker_id{0U};
  DurableSyncAttemptState state{DurableSyncAttemptState::active};
  DurableSyncAttemptMode mode{DurableSyncAttemptMode::whole_object};
  DurableSyncAttemptBinding binding{DurableSyncAttemptBinding::route_worker};

  [[nodiscard]] bool operator==(const DurableSyncAttempt &) const = default;
};

[[nodiscard]] Result<DurableSyncAttempt> make_durable_range_attempt(
    std::uint64_t attempt_id, const SyncRangePlan &plan,
    DurableSyncAttemptState state, const security::Sodium &sodium);

struct SyncAttemptJournal {
  std::string namespace_id;
  std::uint64_t high_attempt_id{0U};
  std::vector<DurableSyncAttempt> active;
  security::SigningPublicKey signer{};
  std::uint64_t mutation{0U};
  Digest previous{};
  security::Signature signature{};

  [[nodiscard]] bool operator==(const SyncAttemptJournal &) const = default;
};

enum class SyncAttemptBegin : std::uint8_t {
  inserted = 1U,
  duplicate = 2U,
};

enum class SyncAttemptRecoveryDisposition : std::uint8_t {
  fenced = 1U,
  committed = 2U,
  retained = 3U,
};

struct RecoveredSyncAttempt {
  DurableSyncAttempt attempt;
  SyncAttemptRecoveryDisposition disposition{
      SyncAttemptRecoveryDisposition::fenced};

  [[nodiscard]] bool operator==(const RecoveredSyncAttempt &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_attempt_journal(const SyncAttemptJournal &journal);
[[nodiscard]] Result<SyncAttemptJournal>
decode_sync_attempt_journal(std::span<const std::uint8_t> bytes,
                            std::size_t maximum_active_attempts);
[[nodiscard]] Status verify_sync_attempt_journal(
    const SyncAttemptJournal &journal,
    const security::SigningPublicKey &expected_device,
    const NamespacePolicy &policy, const security::Sodium &sodium,
    std::size_t maximum_active_attempts);
[[nodiscard]] Result<Digest> sync_attempt_journal_digest(
    const SyncAttemptJournal &journal, const security::Sodium &sodium);

// Stable-device-signed restart truth for live transfer attempts. IDs are
// durably burned before scheduler assignment; only currently live attempts
// are retained. Process-local scheduler tombstones still classify late events.
class SyncAttemptStore {
public:
  struct Config {
    std::size_t maximum_active_attempts{1024U};
  };

  explicit SyncAttemptStore(std::filesystem::path root);
  SyncAttemptStore(std::filesystem::path root, Config config);

  [[nodiscard]] Result<SyncAttemptJournal> load(
      const NamespacePolicy &policy,
      const security::SigningPublicKey &expected_device,
      const security::Sodium &sodium) const;
  [[nodiscard]] Result<std::uint64_t> reserve_attempt_id(
      const NamespacePolicy &policy,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<std::uint64_t> reserve_attempt_id(
      const NamespacePolicy &policy,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<SyncAttemptBegin> begin(
      const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<SyncAttemptBegin> begin(
      const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<bool> finish(
      const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<bool> finish(
      const NamespacePolicy &policy, const DurableSyncAttempt &attempt,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  // Finds only startup-classified restart-retained work for this exact
  // immutable object. The namespace transaction lets a caller inspect,
  // finish, and no-clobber hand the prefix to a fresh attempt without another
  // process observing an intermediate namespace state.
  [[nodiscard]] Result<std::optional<DurableSyncAttempt>> retained_attempt(
      const NamespacePolicy &policy, const SyncObjectRecord &object,
      const security::SigningPublicKey &expected_device,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction) const;
  // Finds only a startup-classified range prefix whose signed ATM1 binding
  // matches the exact freshly derived plan and bundle length.
  [[nodiscard]] Result<std::optional<DurableSyncAttempt>>
  retained_range_attempt(
      const NamespacePolicy &policy, const SyncObjectRecord &target,
      const Digest &plan_commitment, std::uint64_t bundle_bytes,
      const security::SigningPublicKey &expected_device,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction) const;
  // Discards restart-retained range bytes for TARGET unless their exact plan
  // and bundle binding matches. A zero commitment plus zero bytes permits no
  // range prefix. Whole-object retained work is unaffected.
  [[nodiscard]] Result<std::size_t> fence_retained_ranges_except(
      const NamespacePolicy &policy, const SyncObjectRecord &target,
      const Digest &plan_commitment, std::uint64_t bundle_bytes,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  // Discards restart-only prefixes that are not named by the newly verified
  // candidate HEAD. Live process-owned attempts are never selected.
  [[nodiscard]] Result<std::size_t> fence_retained_except(
      const NamespacePolicy &policy,
      std::span<const SyncObjectRecord> allowed_objects,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<std::vector<RecoveredSyncAttempt>> recover(
      const NamespacePolicy &policy,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium, const SyncInstallSeams &seams,
      std::uint64_t copy_chunk_bytes = 64U * 1024U);
  [[nodiscard]] Result<std::vector<RecoveredSyncAttempt>> recover(
      const NamespacePolicy &policy,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium, const SyncInstallSeams &seams,
      const SyncNamespaceTransaction &transaction,
      std::uint64_t copy_chunk_bytes = 64U * 1024U);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  Config config_;
};

} // namespace iotox::sync
