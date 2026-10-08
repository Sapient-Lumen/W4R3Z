#pragma once

#include <cstdint>
#include <string_view>

namespace anonsync {

// One live operating-system process identity. This value is intentionally
// process-local and non-serializable. It rejects SQLite capabilities inherited
// across fork() before any SQLite routine or cleanup handler can touch them.
using SyncSqliteProcessId = std::uint64_t;

inline constexpr int kSyncSqliteCapabilityViolationExitCode = 86;

[[nodiscard]] SyncSqliteProcessId
current_sync_sqlite_process_id_noexcept() noexcept;

[[nodiscard]] bool sync_sqlite_process_id_is_current(
    SyncSqliteProcessId expected) noexcept;

// Empty proof is a programming error and throws. A nonempty proof from another
// process is an inherited-capability violation and exits immediately without
// C++ unwinding or atexit processing.
void require_sync_sqlite_process_id_or_fail_stop(
    SyncSqliteProcessId expected,
    std::string_view label);

[[noreturn]] void fail_stop_on_sync_sqlite_capability_violation_noexcept()
    noexcept;

}  // namespace anonsync
