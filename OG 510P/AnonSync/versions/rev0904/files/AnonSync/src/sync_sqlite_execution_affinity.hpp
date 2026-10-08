#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

namespace anonsync {

// Shared fail-stop validation for SQLite owners whose lifetime is bound to the
// process and exact C++ thread that acquired an SQLite-owned resource. Process
// lineage is checked first because a fork descendant must reject copied thread
// storage before interpreting it as a live thread capability.
void require_current_sync_sqlite_execution_noexcept(
    SyncProcessIncarnation process_id,
    SyncThreadIncarnation thread_id) noexcept;

}  // namespace anonsync
