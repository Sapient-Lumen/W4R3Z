#pragma once

#include "sqlite_replay_ledger_reset.hpp"
#include "sync_atomic_file_publication.hpp"

#include <cstdint>
#include <exception>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <string>

namespace anonsync::persistence {

namespace detail {
class SqliteReplayLedgerResetReceiptProtocolErrorAccess;
}

// One typed owner joins the durable SQLite reset and immutable receipt
// publication without pretending that the two resources are one transaction.
// A failure carries tri-state durable evidence: no durable reset was observed,
// the exact request-derived identity was verified by the reset owner or by an
// independent reopen, or a durable frontier was crossed but the identity is
// indeterminate.
enum class SqliteReplayLedgerResetReceiptDurableEvidence : std::uint8_t {
    NotDurable,
    ExactRequestDurable,
    DurableIdentityIndeterminate,
};

[[nodiscard]] const char*
sqlite_replay_ledger_reset_receipt_durable_evidence_name(
    SqliteReplayLedgerResetReceiptDurableEvidence evidence) noexcept;

enum class SqliteReplayLedgerResetReceiptProtocolFailure : std::uint8_t {
    Preparation,
    ResetBeforeDurableOutcome,
    ResetAfterExactDurableOutcome,
    ResetDurableIdentityIndeterminate,
    ReceiptPublicationAfterExactDurableOutcome,
};

[[nodiscard]] const char*
sqlite_replay_ledger_reset_receipt_protocol_failure_name(
    SqliteReplayLedgerResetReceiptProtocolFailure failure) noexcept;

enum class SqliteReplayLedgerResetReceiptRecoveryAction : std::uint8_t {
    None,
    ResolveDurableIdentityBeforeRecovery,
    ReplayExactRequestToFreshReceiptPath,
};

[[nodiscard]] const char*
sqlite_replay_ledger_reset_receipt_recovery_action_name(
    SqliteReplayLedgerResetReceiptRecoveryAction action) noexcept;

struct SqliteReplayLedgerResetReceiptPublicationEffect final {
    SyncAtomicFilePublicationOutcome outcome{
        SyncAtomicFilePublicationOutcome::NotPublished};
    SyncAtomicFilePublicationResidue residue{
        SyncAtomicFilePublicationResidue::None};
};

struct SqliteReplayLedgerResetReceiptProtocolResult final {
    SqliteReplayLedgerResetResult reset;
    SqliteReplayLedgerResetReceiptPublicationEffect publication{
        SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced,
        SyncAtomicFilePublicationResidue::None};
};

class SqliteReplayLedgerResetReceiptProtocolError final
    : public std::runtime_error, public std::nested_exception {
public:
    [[nodiscard]] SqliteReplayLedgerResetReceiptProtocolFailure failure()
        const noexcept;
    [[nodiscard]] SqliteReplayLedgerResetReceiptDurableEvidence
    durable_evidence() const noexcept;
    [[nodiscard]] SqliteReplayLedgerResetReceiptRecoveryAction recovery_action()
        const noexcept;
    // This is the reset implementation's reported transaction outcome. It is
    // authoritative recovery evidence only when durable_evidence() is
    // ExactRequestDurable.
    [[nodiscard]] const std::optional<SqliteReplayLedgerResetOutcome>&
    reported_reset_outcome() const noexcept;
    [[nodiscard]] const std::string& expected_reset_receipt_sha256()
        const noexcept;
    [[nodiscard]] const std::optional<
        SqliteReplayLedgerResetReceiptPublicationEffect>&
    publication_effect() const noexcept;

private:
    friend class detail::
        SqliteReplayLedgerResetReceiptProtocolErrorAccess;

    SqliteReplayLedgerResetReceiptProtocolError(
        SqliteReplayLedgerResetReceiptProtocolFailure failure,
        SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
        SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
        std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
        std::string expected_reset_receipt_sha256,
        std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
            publication_effect,
        std::string message);

    SqliteReplayLedgerResetReceiptProtocolFailure failure_;
    SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence_;
    SqliteReplayLedgerResetReceiptRecoveryAction recovery_action_;
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome_;
    std::string expected_reset_receipt_sha256_;
    std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
        publication_effect_;
};

// Render and bind the exact immutable receipt before the destructive reset,
// execute the reset, verify that its returned evidence is bound to the same
// request-derived digest, and consume the prepared publication capability.
// Success means both the SQLite outcome and a directory-synced receipt are
// established. A typed failure is the complete retry/recovery authority.
[[nodiscard]] SqliteReplayLedgerResetReceiptProtocolResult
execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(
    const SqliteReplayLedgerResetRequest& request,
    const std::string& request_sha256,
    const std::filesystem::path& receipt_path);

}  // namespace anonsync::persistence
