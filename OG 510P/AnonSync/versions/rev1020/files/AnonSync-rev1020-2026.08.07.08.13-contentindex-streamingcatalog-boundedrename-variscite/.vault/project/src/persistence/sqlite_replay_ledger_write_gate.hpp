#pragma once

#include <cstdint>
#include <filesystem>
#include <memory>

namespace anonsync::persistence {

enum class SqliteReplayLedgerWriteGateNesting : std::uint8_t {
    AllowSameThread,
    RejectSameThread,
};

enum class SqliteReplayLedgerWriteGateParentPolicy : std::uint8_t {
    CreatePrivateParents,
    RequireExistingParent,
};

// Process-, thread-incarnation-, and scope-bound exclusive writer capability
// for one SQLite replay-ledger namespace. The adjacent lock file is opened
// through the hardened path guard and locked non-blockingly. A fork child may
// neither reuse nor destroy an inherited capability. Reviewed same-thread
// nesting is strict LIFO: lifetime inversion fails stopped before the outer
// kernel lock can be released.
class SqliteReplayLedgerWriteGate final {
public:
    explicit SqliteReplayLedgerWriteGate(
        const std::filesystem::path& ledger_path,
        SqliteReplayLedgerWriteGateNesting nesting =
            SqliteReplayLedgerWriteGateNesting::AllowSameThread,
        SqliteReplayLedgerWriteGateParentPolicy parent_policy =
            SqliteReplayLedgerWriteGateParentPolicy::CreatePrivateParents);
    ~SqliteReplayLedgerWriteGate();

    SqliteReplayLedgerWriteGate(const SqliteReplayLedgerWriteGate&) = delete;
    SqliteReplayLedgerWriteGate& operator=(
        const SqliteReplayLedgerWriteGate&) = delete;
    SqliteReplayLedgerWriteGate(SqliteReplayLedgerWriteGate&&) = delete;
    SqliteReplayLedgerWriteGate& operator=(
        SqliteReplayLedgerWriteGate&&) = delete;

    [[nodiscard]] bool owns_exclusive_gate() const noexcept;

private:
    struct State;
    std::unique_ptr<State> state_;
};

[[nodiscard]] std::filesystem::path sqlite_replay_ledger_write_gate_path(
    const std::filesystem::path& ledger_path);

}  // namespace anonsync::persistence
