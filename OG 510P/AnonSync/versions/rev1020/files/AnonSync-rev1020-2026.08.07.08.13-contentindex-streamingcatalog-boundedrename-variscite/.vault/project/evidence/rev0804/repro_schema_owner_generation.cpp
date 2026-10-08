#include "sync_peer_ingress_schema.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <cerrno>
#include <cstdlib>
#include <iostream>

#include <sys/wait.h>
#include <unistd.h>

namespace {
anonsync::SyncSqliteDb open_database() {
    anonsync::SyncSqliteDb out;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    if (sqlite3_open_v2(":memory:", out.db.out(), flags, nullptr) != SQLITE_OK) {
        std::abort();
    }
    return out;
}
}

int main() {
    int fds[2] = {-1, -1};
    if (::pipe(fds) != 0) std::abort();
    const pid_t child = ::fork();
    if (child < 0) std::abort();
    if (child == 0) {
        (void)::close(fds[0]);
        anonsync::SyncSqliteDb database = open_database();
#if defined(ANONSYNC_TYPED_SCHEMA_OWNER)
        auto attestation =
            anonsync::initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                database.db, true, false, "schema owner-generation reproducer");
#else
        auto attestation =
            anonsync::initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                database.db.get(), true, false, "schema owner-generation reproducer");
#endif
        (void)attestation;
        const std::size_t borrows = database.db.active_borrows();
        const char byte = borrows < 10 ? static_cast<char>('0' + borrows) : 'X';
        ssize_t rc = -1;
        do { rc = ::write(fds[1], &byte, 1); }
        while (rc < 0 && errno == EINTR);
        if (rc != 1) ::_exit(12);
        database.db.reset();
        ::_exit(0);
    }

    (void)::close(fds[1]);
    char byte = '?';
    ssize_t count = -1;
    do { count = ::read(fds[0], &byte, 1); }
    while (count < 0 && errno == EINTR);
    (void)::close(fds[0]);
    int status = 0;
    if (::waitpid(child, &status, 0) != child) std::abort();
    std::cout << "attestation_owner_borrows="
              << (count == 1 ? byte : '?') << '\n'
              << "owner_close_exit="
              << (WIFEXITED(status) ? WEXITSTATUS(status) : -1) << '\n';
}
