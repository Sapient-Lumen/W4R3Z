#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

#include <string_view>

struct sqlite3;
struct sqlite3_mutex;

namespace anonsync {

// Narrow process- and exact-thread-bound fence for the raw
// sqlite3_busy_timeout() compatibility gateway. A FULLMUTEX connection is
// serialized through its recursive database mutex. A NOMUTEX connection owns
// no SQLite mutex and is admitted only under SQLite's external single-user
// contract, but the guard's C++ lifetime remains process/thread affine.
//
// This type intentionally exposes no authorizes(), mutex identity, or transfer
// operation. It cannot satisfy the retained-callback claim interface and must
// not be confused with SyncSqliteDatabaseMutexGuard authority.
class SyncSqliteBusyTimeoutMutationGuard final {
public:
    SyncSqliteBusyTimeoutMutationGuard(sqlite3* database,
                                       std::string_view label);
    ~SyncSqliteBusyTimeoutMutationGuard() noexcept;

    SyncSqliteBusyTimeoutMutationGuard(
        const SyncSqliteBusyTimeoutMutationGuard&) = delete;
    SyncSqliteBusyTimeoutMutationGuard& operator=(
        const SyncSqliteBusyTimeoutMutationGuard&) = delete;
    SyncSqliteBusyTimeoutMutationGuard(
        SyncSqliteBusyTimeoutMutationGuard&&) = delete;
    SyncSqliteBusyTimeoutMutationGuard& operator=(
        SyncSqliteBusyTimeoutMutationGuard&&) = delete;

private:
    sqlite3_mutex* mutex_ = nullptr;
    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
};

}  // namespace anonsync
