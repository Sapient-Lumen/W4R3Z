#pragma once

#include "sync_process_incarnation.hpp"

#include <memory>
#include <string>

namespace anonsync::persistence {

// One process-incarnation-bound owner for the adjacent restore serialization
// lock. The implementation retains the path-family capability and locked file
// descriptor for the full lifetime. A fork child may neither destroy nor reuse
// inherited authority: destruction outside the minting process fails closed.
class SqliteReplayLedgerRestoreLock final {
public:
    explicit SqliteReplayLedgerRestoreLock(const std::string& ledger_path);
    ~SqliteReplayLedgerRestoreLock();

    SqliteReplayLedgerRestoreLock(const SqliteReplayLedgerRestoreLock&) = delete;
    SqliteReplayLedgerRestoreLock& operator=(
        const SqliteReplayLedgerRestoreLock&) = delete;
    SqliteReplayLedgerRestoreLock(SqliteReplayLedgerRestoreLock&&) = delete;
    SqliteReplayLedgerRestoreLock& operator=(
        SqliteReplayLedgerRestoreLock&&) = delete;

private:
    struct State;

    SyncProcessIncarnation process_id_;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync::persistence
