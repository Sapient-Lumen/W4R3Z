#include "sync_sqlite_process_incarnation.hpp"

#include <cstdlib>
#include <stdexcept>
#include <string>

#if defined(_WIN32)
#include <process.h>
#else
#include <unistd.h>
#endif

namespace anonsync {

SyncSqliteProcessId current_sync_sqlite_process_id_noexcept() noexcept {
#if defined(_WIN32)
    const int raw = ::_getpid();
#else
    const pid_t raw = ::getpid();
#endif
    if (raw <= 0) fail_stop_on_sync_sqlite_capability_violation_noexcept();
    return static_cast<SyncSqliteProcessId>(raw);
}

bool sync_sqlite_process_id_is_current(SyncSqliteProcessId expected) noexcept {
    return expected != 0 && expected == current_sync_sqlite_process_id_noexcept();
}

void require_sync_sqlite_process_id_or_fail_stop(
    SyncSqliteProcessId expected,
    std::string_view label) {
    if (expected == 0) {
        throw std::logic_error(std::string(label) +
                               " process-incarnation proof is empty");
    }
    if (!sync_sqlite_process_id_is_current(expected)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
}

[[noreturn]] void fail_stop_on_sync_sqlite_capability_violation_noexcept()
    noexcept {
    std::_Exit(kSyncSqliteCapabilityViolationExitCode);
}

}  // namespace anonsync
