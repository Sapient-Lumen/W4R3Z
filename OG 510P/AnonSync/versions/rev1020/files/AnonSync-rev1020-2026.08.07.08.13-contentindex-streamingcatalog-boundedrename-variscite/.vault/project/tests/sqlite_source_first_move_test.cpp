#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif
#include "sync_process_incarnation.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <cerrno>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#if !defined(_WIN32)
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

using namespace std::chrono_literals;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_with_output_capture_or_throw;
#endif

std::size_t checks = 0;

[[noreturn]] void fail(std::string_view message) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(1);
}

void require(bool value, std::string_view message) {
    ++checks;
    if (!value) fail(message);
}

anonsync::SyncSqliteDb open_memory_database(std::string_view label) {
    anonsync::SyncSqliteDb out;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    if (sqlite3_open_v2(":memory:", out.db.out(), flags, nullptr) != SQLITE_OK) {
        fail(std::string(label) + " open failed");
    }
    return out;
}

#if !defined(_WIN32)

int marker_fd = -1;

void write_marker() noexcept {
    if (marker_fd < 0) return;
    const char byte = 'X';
    ssize_t rc = -1;
    do {
        rc = ::write(marker_fd, &byte, 1);
    } while (rc < 0 && errno == EINTR);
}

void close_marker_destructor(void*) noexcept { write_marker(); }

void no_op_sql_function(sqlite3_context* context,
                        int,
                        sqlite3_value**) noexcept {
    sqlite3_result_null(context);
}

struct ChildObservation final {
    int exit_code = -1;
    bool marker_observed = false;
};

template <typename Operation>
ChildObservation run_child_with_marker(Operation&& operation) {
    auto child = spawn_inherited_test_process_with_output_capture_or_throw(
        [&](int output_descriptor) {
            marker_fd = output_descriptor;
            std::forward<Operation>(operation)();
            return 12;
        },
        "source-first move inherited-state probe");
    const anonsync::test::InheritedTestProcessOutput output =
        child.wait_for_exit_with_output(
            5s, 1U, "source-first move inherited-state probe");
    require(WIFEXITED(output.wait_status), "child did not exit normally");
    require(output.bytes.empty() || output.bytes == "X",
            "marker pipe returned non-canonical evidence");
    return {
        WEXITSTATUS(output.wait_status),
        output.bytes == "X",
    };
}

void install_close_marker(anonsync::SyncSqliteDb& database) {
    require(sqlite3_create_function_v2(
                database.db.get(), "close_marker", 0, SQLITE_UTF8,
                nullptr, &no_op_sql_function, nullptr, nullptr,
                &close_marker_destructor) == SQLITE_OK,
            "could not install close marker");
}

void inherited_database_source_is_rejected_before_destination_close() {
    anonsync::SyncSqliteDb inherited_source =
        open_memory_database("inherited database source");
    const std::uint64_t generation = inherited_source.db.generation();

    const ChildObservation observation = run_child_with_marker([&] {
        anonsync::SyncSqliteDb destination =
            open_memory_database("child-local database destination");
        install_close_marker(destination);
        destination = std::move(inherited_source);
    });

    require(observation.exit_code ==
                anonsync::kSyncProcessCapabilityViolationExitCode,
            "inherited database source returned wrong fail-stop status");
    require(!observation.marker_observed,
            "invalid database source closed the valid destination first");
    require(inherited_source.db.generation() == generation,
            "child database move disturbed the parent source generation");
    inherited_source.db.reset();
}

void inherited_statement_source_is_rejected_before_destination_finalize() {
    anonsync::SyncSqliteDb source_database =
        open_memory_database("inherited statement database");
    anonsync::SyncSqliteStmt inherited_source =
        anonsync::sqlite_prepare_or_throw(
            source_database.db, "SELECT 1;", "inherited statement source");
    const std::uint64_t generation = inherited_source.owner_generation();

    const ChildObservation observation = run_child_with_marker([&] {
        anonsync::SyncSqliteDb destination_database =
            open_memory_database("child-local statement database");
        anonsync::SyncSqliteStmt destination =
            anonsync::sqlite_prepare_or_throw(
                destination_database.db, "SELECT ?1;",
                "child-local statement destination");
        static char payload[] = "marker";
        if (sqlite3_bind_text(destination.stmt, 1, payload, -1,
                              &close_marker_destructor) != SQLITE_OK) {
            ::_exit(13);
        }
        destination = std::move(inherited_source);
    });

    require(observation.exit_code ==
                anonsync::kSyncProcessCapabilityViolationExitCode,
            "inherited statement source returned wrong fail-stop status");
    require(!observation.marker_observed,
            "invalid statement source finalized the valid destination first");
    require(inherited_source.owner_generation() == generation,
            "child statement move disturbed the parent source generation");
    inherited_source.reset();
    source_database.db.reset();
}

void pending_output_source_is_rejected_before_destination_close() {
    const ChildObservation observation = run_child_with_marker([] {
        anonsync::SyncSqliteDb pending_source;
        auto pending_output = pending_source.db.out();
        (void)pending_output.get();

        anonsync::SyncSqliteDb destination =
            open_memory_database("pending-output destination");
        install_close_marker(destination);
        destination = std::move(pending_source);
    });

    require(observation.exit_code ==
                anonsync::kSyncProcessCapabilityViolationExitCode,
            "pending output source returned wrong fail-stop status");
    require(!observation.marker_observed,
            "pending output source closed the valid destination first");
}

struct DatabaseReentryContext final {
    anonsync::SyncSqliteDb* destination = nullptr;
};

void database_reentry_destructor(void* raw) noexcept {
    write_marker();
    auto* context = static_cast<DatabaseReentryContext*>(raw);
    if (context == nullptr || context->destination == nullptr) ::_exit(14);
    context->destination->db.reset();
    ::_exit(15);
}

void destination_database_reentrancy_is_fail_stopped() {
    const ChildObservation observation = run_child_with_marker([] {
        anonsync::SyncSqliteDb source =
            open_memory_database("database reentry source");
        anonsync::SyncSqliteDb destination =
            open_memory_database("database reentry destination");
        DatabaseReentryContext context{&destination};
        if (sqlite3_create_function_v2(
                destination.db.get(), "reentry_marker", 0, SQLITE_UTF8,
                &context, &no_op_sql_function, nullptr, nullptr,
                &database_reentry_destructor) != SQLITE_OK) {
            ::_exit(13);
        }
        destination = std::move(source);
    });

    require(observation.exit_code ==
                anonsync::kSyncProcessCapabilityViolationExitCode,
            "database close reentry was not fail-stopped");
    require(observation.marker_observed,
            "database close reentry callback was not reached");
}

struct StatementReentryContext final {
    anonsync::SyncSqliteStmt* destination = nullptr;
};

void statement_reentry_destructor(void* raw) noexcept {
    write_marker();
    auto* context = static_cast<StatementReentryContext*>(raw);
    if (context == nullptr || context->destination == nullptr) ::_exit(14);
    context->destination->reset();
    ::_exit(15);
}

void destination_statement_reentrancy_is_fail_stopped() {
    const ChildObservation observation = run_child_with_marker([] {
        anonsync::SyncSqliteDb source_database =
            open_memory_database("statement reentry source database");
        anonsync::SyncSqliteDb destination_database =
            open_memory_database("statement reentry destination database");
        anonsync::SyncSqliteStmt source =
            anonsync::sqlite_prepare_or_throw(
                source_database.db, "SELECT 1;", "statement reentry source");
        anonsync::SyncSqliteStmt destination =
            anonsync::sqlite_prepare_or_throw(
                destination_database.db, "SELECT ?1;",
                "statement reentry destination");
        StatementReentryContext context{&destination};
        if (sqlite3_bind_blob(destination.stmt, 1, &context,
                              static_cast<int>(sizeof(context)),
                              &statement_reentry_destructor) != SQLITE_OK) {
            ::_exit(13);
        }
        destination = std::move(source);
    });

    require(observation.exit_code ==
                anonsync::kSyncProcessCapabilityViolationExitCode,
            "statement finalize reentry was not fail-stopped");
    require(observation.marker_observed,
            "statement finalize reentry callback was not reached");
}

struct DatabaseSourceMutationContext final {
    anonsync::SyncSqliteDb* moved_from_source = nullptr;
    std::size_t callbacks = 0;
};

void mutate_moved_from_database_source(void* raw) noexcept {
    auto* context = static_cast<DatabaseSourceMutationContext*>(raw);
    if (context == nullptr || context->moved_from_source == nullptr) std::abort();
    ++context->callbacks;
    context->moved_from_source->db.reset();
}

void database_source_is_escrowed_before_close_callback() {
    anonsync::SyncSqliteDb source =
        open_memory_database("database escrow source");
    anonsync::SyncSqliteDb destination =
        open_memory_database("database escrow destination");
    const std::uint64_t source_generation = source.db.generation();
    sqlite3* const source_handle = source.db.get();
    DatabaseSourceMutationContext context{&source, 0};
    require(sqlite3_create_function_v2(
                destination.db.get(), "source_mutator", 0, SQLITE_UTF8,
                &context, &no_op_sql_function, nullptr, nullptr,
                &mutate_moved_from_database_source) == SQLITE_OK,
            "could not install database source mutation callback");

    destination = std::move(source);
    require(context.callbacks == 1,
            "database destination close did not invoke source mutation callback");
    require(source.db.empty(),
            "database source retained state after escrowed move");
    require(destination.db.get() == source_handle &&
                destination.db.generation() == source_generation,
            "database close callback destroyed the escrowed source authority");
    destination.db.reset();
}

struct StatementSourceMutationContext final {
    anonsync::SyncSqliteStmt* moved_from_source = nullptr;
    std::size_t callbacks = 0;
};

void mutate_moved_from_statement_source(void* raw) noexcept {
    auto* context = static_cast<StatementSourceMutationContext*>(raw);
    if (context == nullptr || context->moved_from_source == nullptr) std::abort();
    ++context->callbacks;
    context->moved_from_source->reset();
}

void statement_source_is_escrowed_before_finalize_callback() {
    anonsync::SyncSqliteDb source_database =
        open_memory_database("statement escrow source database");
    anonsync::SyncSqliteDb destination_database =
        open_memory_database("statement escrow destination database");
    anonsync::SyncSqliteStmt source =
        anonsync::sqlite_prepare_or_throw(
            source_database.db, "SELECT 1;", "statement escrow source");
    anonsync::SyncSqliteStmt destination =
        anonsync::sqlite_prepare_or_throw(
            destination_database.db, "SELECT ?1;",
            "statement escrow destination");
    const std::uint64_t source_generation = source.owner_generation();
    sqlite3_stmt* const source_handle = source.stmt.get();
    StatementSourceMutationContext context{&source, 0};
    require(sqlite3_bind_blob(destination.stmt, 1, &context,
                              static_cast<int>(sizeof(context)),
                              &mutate_moved_from_statement_source) == SQLITE_OK,
            "could not install statement source mutation callback");

    destination = std::move(source);
    require(context.callbacks == 1,
            "statement destination finalize did not invoke source mutation callback");
    require(source.stmt.get() == nullptr,
            "statement source retained state after escrowed move");
    require(destination.stmt.get() == source_handle &&
                destination.owner_generation() == source_generation,
            "statement finalize callback destroyed the escrowed source authority");
    destination.reset();
    destination_database.db.reset();
    source_database.db.reset();
}

#endif

}  // namespace

int main() {
#if !defined(_WIN32)
    inherited_database_source_is_rejected_before_destination_close();
    inherited_statement_source_is_rejected_before_destination_finalize();
    pending_output_source_is_rejected_before_destination_close();
    destination_database_reentrancy_is_fail_stopped();
    destination_statement_reentrancy_is_fail_stopped();
    database_source_is_escrowed_before_close_callback();
    statement_source_is_escrowed_before_finalize_callback();
#endif
    std::cout << "sqlite source-first move checks passed: " << checks << '\n';
    return 0;
}
