#include "sync_sqlite_execution_affinity.hpp"

namespace anonsync {

void require_current_sync_sqlite_execution_noexcept(
    SyncProcessIncarnation process_id,
    SyncThreadIncarnation thread_id) noexcept {
    if (!process_id.valid() ||
        !sync_process_incarnation_is_current(process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!thread_id.valid() ||
        !sync_thread_incarnation_is_current(thread_id)) {
        fail_stop_on_sync_thread_capability_violation_noexcept();
    }
}

}  // namespace anonsync
