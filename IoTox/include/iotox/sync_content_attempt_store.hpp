#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_content.hpp"
#include "iotox/sync_service.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

struct DurableSyncContentAttempt {
  std::uint64_t attempt_id{0U};
  std::uint64_t request_id{0U};
  std::uint64_t source_id{0U};
  Digest head_record{};
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  std::uint64_t logical_index{0U};
  Digest object{};
  std::uint64_t object_bytes{0U};
  FileId file_id{};
  SyncTransferCarrier carrier;
  PrincipalId source_principal{};

  [[nodiscard]] bool
  operator==(const DurableSyncContentAttempt &) const = default;
};

struct SyncContentAttemptJournal {
  std::string namespace_id;
  std::uint64_t high_attempt_id{0U};
  std::vector<DurableSyncContentAttempt> active;
  security::SigningPublicKey signer{};
  std::uint64_t mutation{0U};
  Digest previous{};
  security::Signature signature{};

  [[nodiscard]] bool
  operator==(const SyncContentAttemptJournal &) const = default;
};

enum class SyncContentAttemptBegin : std::uint8_t {
  inserted = 1U,
  duplicate = 2U,
};

enum class SyncContentAttemptRecoveryDisposition : std::uint8_t {
  committed = 1U,
  fenced = 2U,
};

struct RecoveredSyncContentAttempt {
  DurableSyncContentAttempt attempt;
  SyncContentAttemptRecoveryDisposition disposition{
      SyncContentAttemptRecoveryDisposition::fenced};

  [[nodiscard]] bool
  operator==(const RecoveredSyncContentAttempt &) const = default;
};

[[nodiscard]] std::filesystem::path
sync_content_attempt_staging_path(const NamespacePolicy &policy,
                                  const Digest &object,
                                  std::uint64_t request_id);

[[nodiscard]] Result<std::filesystem::path>
prepare_sync_content_attempt_staging(
    const NamespacePolicy &policy, const Digest &object,
    std::uint64_t request_id, const SyncNamespaceTransaction &transaction);
[[nodiscard]] Status discard_sync_content_attempt_staging(
    const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
    const SyncNamespaceTransaction &transaction);

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_content_attempt_journal(const SyncContentAttemptJournal &journal);
[[nodiscard]] Result<SyncContentAttemptJournal>
decode_sync_content_attempt_journal(std::span<const std::uint8_t> bytes,
                                    std::size_t maximum_active_attempts);
[[nodiscard]] Status verify_sync_content_attempt_journal(
    const SyncContentAttemptJournal &journal,
    const security::SigningPublicKey &expected_device,
    const NamespacePolicy &policy, const security::Sodium &sodium,
    std::size_t maximum_active_attempts);
[[nodiscard]] Result<Digest>
sync_content_attempt_journal_digest(const SyncContentAttemptJournal &journal,
                                    const security::Sodium &sodium);

// Stable-device-signed restart truth for dark content-v2 subscriber work.
// Reservation burns an ID before scheduler assignment; begin persists the
// complete HEAD/object/FileId/carrier binding before any transport effect.
class SyncContentAttemptStore final {
public:
  struct Config {
    std::size_t maximum_active_attempts{1024U};
  };

  explicit SyncContentAttemptStore(std::filesystem::path root);
  SyncContentAttemptStore(std::filesystem::path root, Config config);

  [[nodiscard]] Result<SyncContentAttemptJournal>
  load(const NamespacePolicy &policy,
       const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Result<std::uint64_t>
  reserve_attempt_id(const NamespacePolicy &policy,
                     const security::DeviceIdentity &identity,
                     const security::Sodium &sodium,
                     const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<SyncContentAttemptBegin>
  begin(const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium,
        const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<bool> finish(
      const NamespacePolicy &policy, const DurableSyncContentAttempt &attempt,
      const security::DeviceIdentity &identity, const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);

  // Startup never resurrects a carrier. Complete exact staging may enter CAS;
  // partial/absent work is fenced. Every signed record is then retired.
  [[nodiscard]] Result<std::vector<RecoveredSyncContentAttempt>>
  recover(const NamespacePolicy &policy,
          const security::DeviceIdentity &identity,
          const security::Sodium &sodium,
          const SyncNamespaceTransaction &transaction,
          SyncContentCommitConfig commit_config = {});

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  Config config_;
};

} // namespace iotox::sync
