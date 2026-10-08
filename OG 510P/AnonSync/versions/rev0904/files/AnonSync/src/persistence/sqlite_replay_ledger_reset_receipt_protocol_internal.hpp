#pragma once

#include "sqlite_replay_ledger_reset_receipt_protocol.hpp"
#include "sync_atomic_file_publication_internal.hpp"

namespace anonsync::persistence::detail {

// The public error is intentionally not constructible by callers. This access
// point is private to the protocol translation unit and preserves the
// relationship between phase, durable evidence, and recovery authority.
class SqliteReplayLedgerResetReceiptProtocolErrorAccess final {
public:
    [[nodiscard]] static SqliteReplayLedgerResetReceiptProtocolError make(
        SqliteReplayLedgerResetReceiptProtocolFailure failure,
        SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
        SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
        std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
        std::string expected_reset_receipt_sha256,
        std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
            publication_effect,
        std::string message);
};

// Test-only mutation seam after the reset owner returns and before the protocol
// binds the result to its original request. It is internal so production callers
// cannot manufacture or alter durable evidence.
using SqliteReplayLedgerResetResultBindingObserver = void (*)(
    SqliteReplayLedgerResetResult& result,
    void* context);

// Deterministic simulation access to the exact production protocol owner. The
// public entry point delegates here with null observers; tests therefore cannot
// accidentally validate parallel reset/publication choreography.
class SqliteReplayLedgerResetReceiptProtocolObserverAccess final {
public:
    [[nodiscard]] static SqliteReplayLedgerResetReceiptProtocolResult
    execute_or_throw(
        const SqliteReplayLedgerResetRequest& request,
        const std::string& request_sha256,
        const std::filesystem::path& receipt_path,
        SqliteReplayLedgerResetObserver reset_observer,
        void* reset_observer_context,
        SqliteReplayLedgerResetResultBindingObserver result_binding_observer,
        void* result_binding_observer_context,
        atomic_file_publication_detail::AtomicFilePublicationObserver
            publication_observer,
        void* publication_observer_context);
};

}  // namespace anonsync::persistence::detail
