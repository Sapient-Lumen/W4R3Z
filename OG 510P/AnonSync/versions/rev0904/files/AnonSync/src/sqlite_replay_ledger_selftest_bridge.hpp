#pragma once

#include "anonsync_core_internal.hpp"

#include <cstddef>
#include <functional>
#include <string>

namespace anonsync {

// Narrow bridge from the extracted diagnostic corpus into the replay-ledger
// verifier. Runtime consumers do not include this header, and the bridge owns
// no fixture generation or subprocess behavior.
ReplayLedgerStats verify_sqlite_ledger_snapshot_readonly_for_selftest(
    const std::string& snapshot_path,
    const std::string& label);

ReplayLedgerStats
verify_sqlite_ledger_snapshot_readonly_with_row_limit_for_selftest(
    const std::string& snapshot_path,
    const std::string& label,
    std::size_t maximum_rows);

std::string sqlite_effect_pending_report_json_for_selftest(
    const std::string& ledger_path,
    const std::function<void()>& after_verification);

}  // namespace anonsync
