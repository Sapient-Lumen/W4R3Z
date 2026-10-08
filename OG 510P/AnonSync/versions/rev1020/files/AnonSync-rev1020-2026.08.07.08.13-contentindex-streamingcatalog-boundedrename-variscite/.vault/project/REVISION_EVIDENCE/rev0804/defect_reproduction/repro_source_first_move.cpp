#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <cerrno>
#include <cstdlib>
#include <iostream>
#include <utility>

#include <sys/wait.h>
#include <unistd.h>

namespace {
int marker_fd = -1;

void mark_disposal(void*) noexcept {
    if (marker_fd < 0) return;
    const char byte = 'X';
    ssize_t rc = -1;
    do { rc = ::write(marker_fd, &byte, 1); }
    while (rc < 0 && errno == EINTR);
}

void no_op(sqlite3_context* context, int, sqlite3_value**) noexcept {
    sqlite3_result_null(context);
}

anonsync::SyncSqliteDb open_database() {
    anonsync::SyncSqliteDb out;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    if (sqlite3_open_v2(":memory:", out.db.out(), flags, nullptr) != SQLITE_OK) {
        std::abort();
    }
    return out;
}

struct ChildResult final { int exit_code; bool marker; };

template <typename Operation>
ChildResult run_child(Operation&& operation) {
    int fds[2] = {-1, -1};
    if (::pipe(fds) != 0) std::abort();
    const pid_t child = ::fork();
    if (child < 0) std::abort();
    if (child == 0) {
        (void)::close(fds[0]);
        marker_fd = fds[1];
        std::forward<Operation>(operation)();
        ::_exit(12);
    }
    (void)::close(fds[1]);
    int status = 0;
    if (::waitpid(child, &status, 0) != child) std::abort();
    char byte = 0;
    ssize_t count = -1;
    do { count = ::read(fds[0], &byte, 1); }
    while (count < 0 && errno == EINTR);
    (void)::close(fds[0]);
    return {WIFEXITED(status) ? WEXITSTATUS(status) : -1, count == 1};
}
}  // namespace

int main() {
    anonsync::SyncSqliteDb inherited_database = open_database();
    const ChildResult database = run_child([&] {
        anonsync::SyncSqliteDb destination = open_database();
        if (sqlite3_create_function_v2(destination.db.get(), "marker", 0,
                                       SQLITE_UTF8, nullptr, &no_op, nullptr,
                                       nullptr, &mark_disposal) != SQLITE_OK) {
            ::_exit(13);
        }
        destination = std::move(inherited_database);
    });

    anonsync::SyncSqliteDb statement_database = open_database();
    anonsync::SyncSqliteStmt inherited_statement =
        anonsync::sqlite_prepare_or_throw(statement_database.db, "SELECT 1;",
                                          "inherited statement");
    const ChildResult statement = run_child([&] {
        anonsync::SyncSqliteDb local_database = open_database();
        anonsync::SyncSqliteStmt destination =
            anonsync::sqlite_prepare_or_throw(local_database.db, "SELECT ?1;",
                                              "destination statement");
        static char payload[] = "marker";
        if (sqlite3_bind_text(destination.stmt, 1, payload, -1,
                              &mark_disposal) != SQLITE_OK) {
            ::_exit(14);
        }
        destination = std::move(inherited_statement);
    });

    std::cout << "database_move_exit=" << database.exit_code << '\n'
              << "database_destination_disposed_before_rejection="
              << (database.marker ? "true" : "false") << '\n'
              << "statement_move_exit=" << statement.exit_code << '\n'
              << "statement_destination_disposed_before_rejection="
              << (statement.marker ? "true" : "false") << '\n';
    inherited_statement.reset();
    statement_database.db.reset();
    inherited_database.db.reset();
}
