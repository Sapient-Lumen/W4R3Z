#pragma once

#include "sqlite_replay_ledger_reset.hpp"

#include <string>
#include <string_view>

namespace anonsync::persistence {

// Lossless projection from the pinned inspection result to the exact
// destructive precondition carried by an operator request. Observation-only
// connection metadata is deliberately excluded.
[[nodiscard]] SqliteReplayLedgerResetExpectation
sqlite_replay_ledger_reset_expectation_from_state(
    const SqliteReplayLedgerResetState& state);

// Canonical operator-facing inspection document. This report may contain
// observation metadata and is therefore not a durable reset receipt.
[[nodiscard]] std::string sqlite_replay_ledger_reset_state_report_json(
    const SqliteReplayLedgerResetState& state);

// Canonical durable-event document. Its bytes are a pure function of the exact
// validated request semantics and the SHA-256 of the exact request file bytes.
// It deliberately excludes attempt-local outcome, connection generation, and
// later-state observations so first execution and exact recovery emit the same
// bytes to distinct immutable destinations.
[[nodiscard]] std::string sqlite_replay_ledger_reset_receipt_json(
    const SqliteReplayLedgerResetRequest& request,
    std::string_view request_sha256);

}  // namespace anonsync::persistence
