#pragma once

#include "iotox/protocol/command.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace iotox {

// Durable command identity is independent of toxcore's process-local friend
// number and of one online connection epoch. The sender chooses one persistent
// non-zero epoch and a message id; the receiver keys deduplication by the
// sender's Tox public key plus that pair.
inline constexpr std::size_t kCommandPeerKeyBytes = 32U;
inline constexpr std::size_t kDefaultMaximumCommandRecords = 1024U;
inline constexpr std::size_t kDefaultMaximumCommandStoreBytes = 8U * 1024U * 1024U;
inline constexpr std::size_t kDefaultMaximumPendingCommandRecords = 256U;
inline constexpr std::size_t kDefaultMaximumPendingCommandsPerPeer = 32U;
inline constexpr std::size_t kDefaultMaximumCommandBytesPerPeer = 256U * 1024U;
inline constexpr std::uint64_t kDefaultCommandAdmissionDelayMs = 1000U;
inline constexpr std::uint64_t kDefaultCommandRetryBaseMs = 1000U;
inline constexpr std::uint64_t kDefaultCommandRetryMaximumMs = 5U * 60U * 1000U;
using CommandPeerKey = std::array<std::uint8_t, kCommandPeerKeyBytes>;

enum class CommandDirection : std::uint8_t {
    incoming = 1U,
    outgoing = 2U,
};

enum class CommandLifecycle : std::uint8_t {
    reserved = 1U,
    locally_queued = 2U,
    received = 3U,
    admitted = 4U,
    started = 5U,
    succeeded = 6U,
    failed = 7U,
    expired = 8U,
    cancelled = 9U,
    timed_out_unconfirmed = 10U,
};

enum class CommandDeliveryState : std::uint8_t {
    none = 0U,
    pending = 1U,
    send_failed = 2U,
    queued = 3U,
    terminal_failure = 4U,
    observed = 5U,
};

enum class CommandPriority : std::uint8_t {
    low = 1U,
    normal = 2U,
    high = 3U,
};

enum class CommandClockRequirement : std::uint8_t {
    none = 0U,
    trusted_wall = 1U,
};

enum class CommandArtifact : std::uint8_t {
    request = 1U,
    receipt = 2U,
    result = 3U,
};

struct CommandDeliverySchedule {
    std::uint32_t attempts{0U};
    ErrorCode last_error_code{ErrorCode::ok};
    std::uint64_t last_attempt_unix_ms{0U};
    std::uint64_t next_attempt_unix_ms{0U};

    [[nodiscard]] bool operator==(const CommandDeliverySchedule &) const = default;
};

struct CommandRetryPolicy {
    std::uint64_t base_delay_ms{kDefaultCommandRetryBaseMs};
    std::uint64_t maximum_delay_ms{kDefaultCommandRetryMaximumMs};
};

struct DurableCommandKey {
    // The same remote peer can legitimately originate a command whose wire
    // epoch/message pair matches one of our outgoing commands. Direction is
    // therefore part of the local journal locator even though it is not part
    // of the sender-defined wire identity.
    CommandDirection direction{CommandDirection::incoming};
    CommandPeerKey peer_public_key{};
    std::uint64_t sender_epoch{0U};
    std::uint64_t message_id{0U};

    [[nodiscard]] auto operator<=>(const DurableCommandKey &) const = default;
};

struct DurableCommandRecord {
    DurableCommandKey key;
    CommandDirection direction{CommandDirection::incoming};
    CommandLifecycle lifecycle{CommandLifecycle::received};
    protocol::CommandOperation operation{protocol::CommandOperation::unknown};
    protocol::CommandOutcome outcome{protocol::CommandOutcome::internal_error};
    CommandDeliveryState receipt_delivery{CommandDeliveryState::none};
    CommandDeliveryState result_delivery{CommandDeliveryState::none};
    CommandPriority priority{CommandPriority::normal};
    CommandClockRequirement clock_requirement{CommandClockRequirement::none};
    security::SigningPublicKey peer_principal{};
    std::uint64_t correlation_id{0U};
    std::uint64_t result_message_id{0U};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t authority_sequence{0U};
    std::uint64_t created_unix_ms{0U};
    std::uint64_t updated_unix_ms{0U};
    std::uint64_t expiry_unix_ms{0U};
    CommandDeliverySchedule request_schedule;
    CommandDeliverySchedule receipt_schedule;
    CommandDeliverySchedule result_schedule;
    std::vector<std::uint8_t> canonical_request;
    std::vector<std::uint8_t> canonical_receipt;
    std::vector<std::uint8_t> canonical_result;

    [[nodiscard]] bool operator==(const DurableCommandRecord &) const = default;
};

struct DurableCommandSnapshot {
    std::uint64_t generation{0U};
    std::uint64_t local_sender_epoch{0U};
    std::uint64_t clock_high_water_unix_ms{0U};
    std::vector<DurableCommandRecord> records;
};

enum class CommandInsertDisposition : std::uint8_t {
    inserted = 1U,
    exact_duplicate = 2U,
    conflicting_reuse = 3U,
};

class DurableCommandStore {
  public:
    struct Config {
        std::filesystem::path path;
        std::size_t maximum_records{kDefaultMaximumCommandRecords};
        std::size_t maximum_file_bytes{kDefaultMaximumCommandStoreBytes};
        std::size_t maximum_pending_records{kDefaultMaximumPendingCommandRecords};
        std::size_t maximum_pending_per_peer{
            kDefaultMaximumPendingCommandsPerPeer};
        std::size_t maximum_bytes_per_peer{kDefaultMaximumCommandBytesPerPeer};
        // A witnessed effect frontier cannot permit its supporting records to
        // disappear through ordinary terminal-history pruning.
        bool retain_mutating_effect_history{false};
    };

    DurableCommandStore(const DurableCommandStore &) = delete;
    DurableCommandStore &operator=(const DurableCommandStore &) = delete;
    DurableCommandStore(DurableCommandStore &&) = delete;
    DurableCommandStore &operator=(DurableCommandStore &&) = delete;
    ~DurableCommandStore() = default;

    [[nodiscard]] static Result<std::unique_ptr<DurableCommandStore>> open(
        Config config,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium);

    [[nodiscard]] DurableCommandSnapshot snapshot() const;
    [[nodiscard]] std::uint64_t local_sender_epoch() const;
    [[nodiscard]] std::uint64_t clock_high_water_unix_ms() const;
    [[nodiscard]] Result<std::optional<DurableCommandRecord>> find(
        const DurableCommandKey &key) const;
    [[nodiscard]] std::vector<DurableCommandRecord> records_for_peer(
        const CommandPeerKey &peer_public_key,
        CommandDirection direction) const;

    [[nodiscard]] Result<CommandInsertDisposition> insert(
        const DurableCommandRecord &record);
    [[nodiscard]] Status update(const DurableCommandRecord &record);
    [[nodiscard]] Status checkpoint_clock_high_water(
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<DurableCommandRecord> cancel_before_start(
        const DurableCommandKey &key, std::uint64_t now_unix_ms);

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return config_.path;
    }

  private:
    DurableCommandStore(
        Config config,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium)
        : config_(std::move(config)), identity_(&identity), sodium_(&sodium) {}

    [[nodiscard]] Status load_or_create();
    [[nodiscard]] Status persist(const DurableCommandSnapshot &candidate) const;

    Config config_;
    const security::DeviceIdentity *identity_{nullptr};
    const security::Sodium *sodium_{nullptr};
    mutable std::mutex mutex_;
    DurableCommandSnapshot snapshot_;
};

[[nodiscard]] std::filesystem::path default_command_store_path(
    const std::filesystem::path &tox_savedata_path);
[[nodiscard]] bool command_lifecycle_terminal(CommandLifecycle lifecycle) noexcept;
[[nodiscard]] bool command_lifecycle_locally_terminal(
    CommandLifecycle lifecycle) noexcept;
[[nodiscard]] bool command_record_unfinished(
    const DurableCommandRecord &record) noexcept;
// True only after an incoming mutating command has durably crossed STARTED and
// therefore participates in the independently witnessed effect frontier.
[[nodiscard]] bool command_record_has_effect_identity(
    const DurableCommandRecord &record) noexcept;
// Path-free semantic commitment over every retained local effect identity.
// Delivery/result churn and read-only commands deliberately do not enter it.
[[nodiscard]] Result<security::Digest> command_effect_frontier_digest(
    const DurableCommandSnapshot &snapshot,
    const security::Sodium &sodium);
[[nodiscard]] bool command_clock_within_rollback_tolerance(
    std::uint64_t high_water_unix_ms,
    std::uint64_t now_unix_ms,
    std::uint64_t tolerance_ms) noexcept;
[[nodiscard]] CommandDeliverySchedule &command_delivery_schedule(
    DurableCommandRecord &record, CommandArtifact artifact);
[[nodiscard]] const CommandDeliverySchedule &command_delivery_schedule(
    const DurableCommandRecord &record, CommandArtifact artifact);
[[nodiscard]] std::size_t command_record_canonical_bytes(
    const DurableCommandRecord &record) noexcept;
[[nodiscard]] bool command_artifact_due(
    const DurableCommandRecord &record, CommandArtifact artifact,
    std::uint64_t now_unix_ms) noexcept;
[[nodiscard]] Status begin_command_delivery_attempt(
    DurableCommandRecord &record, CommandArtifact artifact,
    std::uint64_t now_unix_ms, const CommandRetryPolicy &policy = {},
    bool force_replay = false);
[[nodiscard]] std::vector<DurableCommandRecord> order_command_outbox(
    std::vector<DurableCommandRecord> records);
[[nodiscard]] std::string to_string(CommandDirection direction);
[[nodiscard]] std::string to_string(CommandLifecycle lifecycle);
[[nodiscard]] std::string to_string(CommandDeliveryState state);
[[nodiscard]] std::string to_string(CommandPriority priority);
[[nodiscard]] std::string to_string(CommandClockRequirement requirement);
[[nodiscard]] std::string to_string(CommandArtifact artifact);
[[nodiscard]] std::string render_command_record(const DurableCommandRecord &record);
[[nodiscard]] std::string render_command_snapshot(const DurableCommandSnapshot &snapshot);

}  // namespace iotox
