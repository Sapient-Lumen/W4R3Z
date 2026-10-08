#pragma once

#include "sqlite_path_security.hpp"

#include <cstdint>
#include <exception>
#include <filesystem>
#include <stdexcept>
#include <string>

namespace anonsync::persistence {

inline constexpr const char* kSqliteReplayLedgerResetRequestFormat =
    "anonsync-sqlite-replay-ledger-reset-request-v3";
inline constexpr const char* kSqliteReplayLedgerResetStateFormat =
    "anonsync-sqlite-replay-ledger-reset-state-v2";
inline constexpr const char* kSqliteReplayLedgerResetReceiptFormat =
    "anonsync-sqlite-replay-ledger-reset-receipt-v4";

enum class SqliteReplayLedgerResetOutcome : std::uint8_t {
    Committed,
    AlreadyCommitted,
};

enum class SqliteReplayLedgerResetCutpoint : std::uint8_t {
    DurableOutcomeObservedBeforePostcommitVerification,
};

using SqliteReplayLedgerResetObserver = void (*)(
    SqliteReplayLedgerResetCutpoint cutpoint,
    void* context);

// A reset transaction may be durably committed even when a later namespace,
// integrity, or receipt-postcondition check cannot complete. This typed error
// prevents callers from reporting a false pre-commit failure. Its receipt digest
// names the reset candidate established at the transaction boundary; callers
// must independently reopen and bind the current durable identity before this
// becomes replay authority.
class SqliteReplayLedgerResetDurableOutcomeError final
    : public std::runtime_error, public std::nested_exception {
public:
    SqliteReplayLedgerResetDurableOutcomeError(
        SqliteReplayLedgerResetOutcome outcome,
        std::string reset_receipt_sha256);

    [[nodiscard]] SqliteReplayLedgerResetOutcome outcome() const noexcept;
    [[nodiscard]] const std::string& reset_receipt_sha256() const noexcept;

private:
    SqliteReplayLedgerResetOutcome outcome_;
    std::string reset_receipt_sha256_;
};

// Exact logical-state evidence produced under one pinned SQLite transaction.
// The digest covers every value in every durable table in a canonical order,
// while the summary fields make an operator request and receipt inspectable.
struct SqliteReplayLedgerResetState final {
    std::string normalized_ledger_path;
    SqlitePathIdentity namespace_identity;
    std::string ledger_instance_id;
    std::string state_sha256;
    std::int64_t durable_line_count = 0;
    std::string durable_head_hash{"GENESIS"};
    std::int64_t effect_transition_line_count = 0;
    std::string effect_transition_head_hash{"GENESIS"};
    std::int64_t ledger_entry_rows = 0;
    std::int64_t effect_transition_rows = 0;
    std::int64_t effect_outbox_rows = 0;
    std::int64_t ingress_sender_replay_rows = 0;
    std::uint64_t connection_owner_generation = 0;
};

// A destructive reset is authorized only for this exact prior logical state.
// Summary fields are redundant with state_sha256 by design: they produce a
// human-reviewable request and are independently compared before mutation.
struct SqliteReplayLedgerResetExpectation final {
    SqlitePathIdentity namespace_identity;
    std::string ledger_instance_id;
    std::string state_sha256;
    std::int64_t durable_line_count = 0;
    std::string durable_head_hash{"GENESIS"};
    std::int64_t effect_transition_line_count = 0;
    std::string effect_transition_head_hash{"GENESIS"};
    std::int64_t ledger_entry_rows = 0;
    std::int64_t effect_transition_rows = 0;
    std::int64_t effect_outbox_rows = 0;
    std::int64_t ingress_sender_replay_rows = 0;
};

struct SqliteReplayLedgerResetRequest final {
    std::filesystem::path ledger_path;
    std::string reset_intent_id;
    std::string operator_id;
    std::string reason;
    SqliteReplayLedgerResetExpectation expected;
};

struct SqliteReplayLedgerResetResult final {
    SqliteReplayLedgerResetOutcome outcome{
        SqliteReplayLedgerResetOutcome::Committed};
    SqliteReplayLedgerResetExpectation prior;
    std::string normalized_ledger_path;
    std::string new_ledger_instance_id;
    // The post-reset ledger identity is the durable receipt digest. It is
    // changed in the same SQLite transaction that clears operational rows.
    std::string reset_receipt_sha256;
    std::string reason_sha256;
    std::uint64_t connection_owner_generation = 0;
    // A retry may observe legitimate rows written after the reset committed.
    // Receipt identity proves the earlier atomic reset; the retry never clears
    // the newer state.
    bool state_advanced_after_commit = false;
};

// Observe and canonically digest one exact ledger image under a pinned read
// transaction and the same exclusive write gate used by reset. This is the
// source of the state precondition embedded in an administrative request.
[[nodiscard]] SqliteReplayLedgerResetState
inspect_sqlite_replay_ledger_reset_state(
    const std::filesystem::path& ledger_path);

// Pure deterministic receipt derivation. The request path must already be
// absolute and lexically normalized, and every expected field is validated
// before any digest is minted.
[[nodiscard]] std::string sqlite_replay_ledger_reset_receipt_sha256(
    const SqliteReplayLedgerResetRequest& request);

// Destructive administration without namespace deletion. The exact schema,
// durable identity, canonical logical-state digest, human-readable summaries,
// parent namespace, open database object, process incarnation,
// connection-owner generation, and exclusive write gate are revalidated. All
// operational rows are cleared and the ledger identity is rotated to the
// deterministic receipt in one typed SQLite transaction. Repeating the same
// exact request returns AlreadyCommitted when the durable identity already
// equals its deterministic receipt. Later rows are reported as advanced state
// and are never cleared by the retry. The optional test observer runs only
// after the transaction boundary has produced a durable outcome and before
// post-commit verification; any observer or verification failure is rethrown as
// SqliteReplayLedgerResetDurableOutcomeError so callers cannot report a false
// pre-commit denial.
[[nodiscard]] SqliteReplayLedgerResetResult reset_sqlite_replay_ledger(
    const SqliteReplayLedgerResetRequest& request,
    SqliteReplayLedgerResetObserver observer = nullptr,
    void* observer_context = nullptr);

}  // namespace anonsync::persistence
