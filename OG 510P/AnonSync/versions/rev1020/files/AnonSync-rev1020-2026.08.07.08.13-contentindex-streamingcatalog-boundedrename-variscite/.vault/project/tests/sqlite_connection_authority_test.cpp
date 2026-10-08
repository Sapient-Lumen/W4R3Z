#if defined(__linux__)
#include "self_exec_test_process.hpp"
#endif
#include "sync_sqlite_connection_authority.hpp"
#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_support.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <future>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

#include <sqlite3.h>

namespace {

using namespace anonsync;
using namespace std::chrono_literals;
#if defined(__linux__)
using anonsync::test::current_self_executable_or_throw;
using anonsync::test::spawn_self_exec_test_process_or_throw;
using anonsync::test::verify_self_exec_child_boundary_or_throw;
#endif

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

[[noreturn]] void fail_without_unwinding_live_thread(
    const std::string& message) noexcept {
    // The only callers have proved that a worker may be blocked inside the
    // operation under test. Unwinding a joinable std::thread would terminate,
    // while trying to mutate the shared SQLite owner to unblock it would add a
    // test-only data race. Exit directly so the failure remains deterministic
    // and does not manufacture a second concurrency defect.
    std::cerr << "sqlite connection authority fatal test timeout: " << message
              << "\n";
    std::_Exit(EXIT_FAILURE);
}

template <typename Function>
void require_throws(Function&& function,
                    std::string_view expected_fragment,
                    const std::string& message,
                    std::uint64_t& checks) {
    ++checks;
    try {
        function();
    } catch (const std::exception& error) {
        const std::string reason = error.what();
        if (reason.find(expected_fragment) != std::string::npos) return;
        fail(message + ": unexpected error: " + reason);
    }
    fail(message + ": no exception was thrown");
}

struct SqliteCloser final {
    void operator()(sqlite3* db) const noexcept {
        if (db == nullptr) return;
        revoke_sync_sqlite_connection_authority_before_close_noexcept(db);
        (void)sqlite3_close_v2(db);
    }
};
using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

SqlitePtr open_memory_database(int mutex_flag = SQLITE_OPEN_FULLMUTEX) {
    sqlite3* raw = nullptr;
    const int rc = sqlite3_open_v2(":memory:",
                                   &raw,
                                   SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                                       mutex_flag,
                                   nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason =
            raw != nullptr ? sqlite3_errmsg(raw) : "unknown SQLite open error";
        if (raw != nullptr) (void)sqlite3_close_v2(raw);
        fail("could not open authority test database: " + reason);
    }
    return SqlitePtr(raw);
}

bool schema_mutation_action(int action) noexcept {
    switch (action) {
        case SQLITE_CREATE_INDEX:
        case SQLITE_CREATE_TABLE:
        case SQLITE_CREATE_TEMP_INDEX:
        case SQLITE_CREATE_TEMP_TABLE:
        case SQLITE_CREATE_TEMP_TRIGGER:
        case SQLITE_CREATE_TEMP_VIEW:
        case SQLITE_CREATE_TRIGGER:
        case SQLITE_CREATE_VIEW:
        case SQLITE_DROP_INDEX:
        case SQLITE_DROP_TABLE:
        case SQLITE_DROP_TEMP_INDEX:
        case SQLITE_DROP_TEMP_TABLE:
        case SQLITE_DROP_TEMP_TRIGGER:
        case SQLITE_DROP_TEMP_VIEW:
        case SQLITE_DROP_TRIGGER:
        case SQLITE_DROP_VIEW:
        case SQLITE_ALTER_TABLE:
        case SQLITE_REINDEX:
        case SQLITE_ANALYZE:
        case SQLITE_CREATE_VTABLE:
        case SQLITE_DROP_VTABLE:
        case SQLITE_ATTACH:
        case SQLITE_DETACH:
            return true;
        default:
            return false;
    }
}

int deny_schema_policy(void*,
                       int action,
                       const char*,
                       const char*,
                       const char*,
                       const char*) noexcept {
    return schema_mutation_action(action) ? SQLITE_DENY : SQLITE_OK;
}

int alien_allow_authorizer(void*,
                           int,
                           const char*,
                           const char*,
                           const char*,
                           const char*) noexcept {
    return SQLITE_OK;
}

int raw_context_rejection_policy(void*,
                                 int,
                                 const char*,
                                 const char*,
                                 const char*,
                                 const char*) noexcept {
    return SQLITE_OK;
}

int malformed_policy(void*,
                     int,
                     const char*,
                     const char*,
                     const char*,
                     const char*) noexcept {
    return 777;
}

int throwing_policy(void*,
                    int,
                    const char*,
                    const char*,
                    const char*,
                    const char*) {
    throw std::runtime_error("policy exception must not cross C ABI");
}

int ignore_transaction_policy(void*,
                              int action,
                              const char*,
                              const char*,
                              const char*,
                              const char*) noexcept {
    return action == SQLITE_TRANSACTION ? SQLITE_IGNORE : SQLITE_OK;
}


int ignore_savepoint_policy(void*,
                            int action,
                            const char*,
                            const char*,
                            const char*,
                            const char*) noexcept {
    return action == SQLITE_SAVEPOINT ? SQLITE_IGNORE : SQLITE_OK;
}

struct OwnedPolicyState final {
    std::uint64_t calls = 0;
};

int owned_allow_policy(OwnedPolicyState& state,
                       int,
                       const char*,
                       const char*,
                       const char*,
                       const char*) noexcept {
    ++state.calls;
    return SQLITE_OK;
}

// A context deleter is arbitrary application code. This pre-existing worker
// tests the exact SQLite connection mutex at deletion time without creating a
// thread from inside the deleter. SQLITE_OK proves the retiring function had
// already left the connection mutex; SQLITE_BUSY exposes accidental disposal
// inside the critical section.
class PolicyRetirementMutexProbe final {
public:
    explicit PolicyRetirementMutexProbe(
        sqlite3* db,
        std::uint64_t initial_requests = 0U)
        : db_(db), request_(initial_requests), worker_([this] { run(); }) {}

    ~PolicyRetirementMutexProbe() {
        stop_.store(true, std::memory_order_release);
        request_.fetch_add(1, std::memory_order_acq_rel);
        request_.notify_all();
        worker_.join();
    }

    PolicyRetirementMutexProbe(const PolicyRetirementMutexProbe&) = delete;
    PolicyRetirementMutexProbe& operator=(
        const PolicyRetirementMutexProbe&) = delete;

    void observe_release_noexcept() noexcept {
        const std::uint64_t ticket =
            request_.fetch_add(1, std::memory_order_acq_rel) + 1;
        request_.notify_all();
        for (;;) {
            const std::uint64_t completed =
                completed_.load(std::memory_order_acquire);
            if (completed >= ticket) return;
            completed_.wait(completed, std::memory_order_acquire);
        }
    }

    [[nodiscard]] int result() const noexcept {
        return result_.load(std::memory_order_acquire);
    }

    [[nodiscard]] std::uint64_t releases() const noexcept {
        return releases_.load(std::memory_order_acquire);
    }

    [[nodiscard]] std::uint64_t completed_requests() const noexcept {
        return completed_.load(std::memory_order_acquire);
    }

    void record_release_noexcept() noexcept {
        releases_.fetch_add(1, std::memory_order_release);
    }

private:
    void run() noexcept {
        // Start from the last *completed* ticket, not from the first request
        // value observed by this thread. A request can be published before the
        // worker begins executing; loading that value into the wait predicate
        // would lose the notification and block the context deleter forever.
        std::uint64_t completed = 0U;
        for (;;) {
            const std::uint64_t requested =
                request_.load(std::memory_order_acquire);
            if (stop_.load(std::memory_order_acquire)) return;
            if (requested == completed) {
                request_.wait(requested, std::memory_order_acquire);
                continue;
            }

            sqlite3_mutex* const mutex = sqlite3_db_mutex(db_);
            int result = SQLITE_MISUSE;
            if (mutex != nullptr) {
                result = sqlite3_mutex_try(mutex);
                if (result == SQLITE_OK) sqlite3_mutex_leave(mutex);
            }
            result_.store(result, std::memory_order_release);
            completed_.store(requested, std::memory_order_release);
            completed_.notify_all();
            completed = requested;
        }
    }

    sqlite3* db_ = nullptr;
    std::atomic<std::uint64_t> request_{0};
    std::atomic<std::uint64_t> completed_{0};
    std::atomic<int> result_{SQLITE_MISUSE};
    std::atomic<std::uint64_t> releases_{0};
    std::atomic<bool> stop_{false};
    std::thread worker_;
};

struct OwnedPolicyStateDeleter final {
    PolicyRetirementMutexProbe* probe = nullptr;

    void operator()(OwnedPolicyState* state) const noexcept {
        if (probe == nullptr) std::_Exit(EXIT_FAILURE);
        probe->observe_release_noexcept();
        probe->record_release_noexcept();
        delete state;
    }
};

std::int64_t scalar_i64(sqlite3* db,
                        const std::string& sql,
                        const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(db, sql, label);
    const int row_rc = sqlite3_step(statement.stmt);
    if (row_rc != SQLITE_ROW) {
        throw_sqlite_exception(db, row_rc, label + " row");
    }
    const std::int64_t value = sqlite3_column_int64(statement.stmt, 0);
    const int done_rc = sqlite3_step(statement.stmt);
    if (done_rc != SQLITE_DONE) {
        throw_sqlite_exception(db, done_rc, label + " completion");
    }
    return value;
}

void test_install_probe_and_policy(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "authority baseline");
    require(proof.valid() && proof.authorizer_generation() == 1,
            "first authority install did not produce generation one", checks);

    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "authority baseline acquire");
        require(lease.active(), "authority acquire returned an inactive lease", checks);
        sqlite_exec_or_throw(db.get(), "SELECT 1;", "authorized SELECT");
        require_throws(
            [&] {
                sqlite_exec_or_throw(db.get(),
                                     "CREATE TABLE forbidden(value INTEGER);",
                                     "forbidden DDL");
            },
            "not authorized",
            "owned authorizer did not enforce its schema policy",
            checks);
    }
}

void test_prepared_statement_is_reauthorized(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    const std::string sql = "CREATE TABLE prepared_before_fence(value INTEGER);";
    SyncSqliteStmtHandleSlot statement;
    const int prepare_rc = sqlite3_prepare_v3(db.get(),
                                              sql.data(),
                                              static_cast<int>(sql.size()),
                                              SQLITE_PREPARE_PERSISTENT,
                                              statement.out(),
                                              nullptr);
    if (prepare_rc != SQLITE_OK || statement.empty()) {
        fail("could not prepare pre-fence DDL fixture");
    }

    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "prepared statement fence");
    SyncSqliteConnectionAuthorityLease lease =
        acquire_sync_sqlite_connection_authority_or_throw(
            db.get(), proof, "prepared statement fence acquire");
    const int step_rc = sqlite3_step(statement);
    require(step_rc == SQLITE_AUTH,
            "statement prepared before fence installation was not reauthorized",
            checks);
    require(sqlite3_reset(statement) == SQLITE_AUTH,
            "pre-fence denied statement did not preserve SQLITE_AUTH at reset",
            checks);
}

void test_policy_boundary_fails_closed(std::uint64_t& checks) {
    {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), malformed_policy, nullptr, "malformed policy");
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "malformed policy acquire");
        require_throws(
            [&] { sqlite_exec_or_throw(db.get(), "SELECT 42;", "malformed policy query"); },
            "not authorized",
            "malformed authorizer policy result did not fail closed",
            checks);
    }
    {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), throwing_policy, nullptr, "throwing policy");
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "throwing policy acquire");
        require_throws(
            [&] { sqlite_exec_or_throw(db.get(), "SELECT 43;", "throwing policy query"); },
            "not authorized",
            "throwing authorizer policy crossed the C callback boundary",
            checks);
    }
}

void test_policy_retirement_probe_cannot_lose_prestart_request(
    std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();

    // The ticket exists before std::thread can enter run(). The former worker
    // initialized its wait predicate from request_, so this exact schedule
    // deterministically converted ticket one into an unnotified infinite wait.
    PolicyRetirementMutexProbe probe(db.get(), 1U);
    const auto deadline = std::chrono::steady_clock::now() + 2s;
    while (probe.completed_requests() < 1U &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::yield();
    }
    if (probe.completed_requests() < 1U) {
        fail_without_unwinding_live_thread(
            "policy-retirement probe lost a request published before worker startup");
    }
    require(probe.completed_requests() == 1U,
            "policy-retirement probe completed the wrong startup ticket",
            checks);
    require(probe.result() == SQLITE_OK,
            "policy-retirement startup ticket did not observe an unlocked SQLite mutex",
            checks);
}

void test_owned_policy_context_lifetime_and_retirement(
    std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();

    PolicyRetirementMutexProbe first_retirement(db.get());
    auto first_context = std::shared_ptr<OwnedPolicyState>(
        new OwnedPolicyState(),
        OwnedPolicyStateDeleter{&first_retirement});
    const std::weak_ptr<OwnedPolicyState> first_lifetime = first_context;
    const SyncSqliteConnectionAuthorityProof first =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(),
            make_sync_sqlite_owned_authorizer_policy<owned_allow_policy>(
                first_context),
            "owned policy first generation");
    first_context.reset();
    require(!first_lifetime.expired(),
            "connection authority did not retain its owned policy context",
            checks);
    require(scalar_i64(db.get(), "SELECT 17;", "owned policy first query") == 17,
            "owned policy first query changed its result",
            checks);
    {
        const std::shared_ptr<OwnedPolicyState> retained =
            first_lifetime.lock();
        require(retained != nullptr && retained->calls > 0,
                "owned policy callback did not receive its retained context",
                checks);
    }

    PolicyRetirementMutexProbe second_retirement(db.get());
    auto second_context = std::shared_ptr<OwnedPolicyState>(
        new OwnedPolicyState(),
        OwnedPolicyStateDeleter{&second_retirement});
    const std::weak_ptr<OwnedPolicyState> second_lifetime = second_context;
    const SyncSqliteConnectionAuthorityProof second =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(),
            make_sync_sqlite_owned_authorizer_policy<owned_allow_policy>(
                second_context),
            "owned policy replacement generation");
    require(second.authorizer_generation() ==
                first.authorizer_generation() + 1,
            "owned policy replacement did not advance the generation",
            checks);
    require(first_lifetime.expired() && first_retirement.releases() == 1,
            "replaced policy context was not released exactly once",
            checks);
    require(first_retirement.result() == SQLITE_OK,
            "replaced policy context was released while SQLite mutex remained held",
            checks);

    second_context.reset();
    require(!second_lifetime.expired(),
            "replacement policy context was not retained by the connection",
            checks);

    int raw_context = 0;
    require_throws(
        [&] {
            (void)install_sync_sqlite_connection_authority_or_throw(
                db.get(),
                raw_context_rejection_policy,
                &raw_context,
                "raw policy context rejection");
        },
        "raw authorizer policy context is not owned",
        "raw policy context remained an accepted retained lifetime",
        checks);
    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), second, "raw policy rejection continuity");
        require(lease.active(),
                "raw policy rejection superseded the live owned generation",
                checks);
    }

    revoke_sync_sqlite_connection_authority_before_close_noexcept(db.get());
    require(second_lifetime.expired() && second_retirement.releases() == 1,
            "revoked policy context was not released exactly once",
            checks);
    require(second_retirement.result() == SQLITE_OK,
            "revoked policy context was released while SQLite mutex remained held",
            checks);
    require(!sync_sqlite_connection_authority_state_present_or_throw(
                db.get(), "owned policy post-revoke state"),
            "owned policy revoke left connection authority state behind",
            checks);
}

void test_replacement_disable_and_generation(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    const SyncSqliteConnectionAuthorityProof first =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "replacement baseline");

    require(sqlite3_set_authorizer(db.get(), alien_allow_authorizer, nullptr) ==
                SQLITE_OK,
            "could not replace owned authorizer in adversarial fixture", checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), first, "alien replacement");
        },
        "authorizer ownership probe failed",
        "alien authorizer replacement retained authority",
        checks);

    const SyncSqliteConnectionAuthorityProof second =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "replacement recovery");
    require(second.authorizer_generation() ==
                first.authorizer_generation() + 1,
            "reinstall did not advance the authorizer generation", checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), first, "stale generation");
        },
        "authorizer generation changed",
        "superseded authority proof remained current",
        checks);
    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), second, "replacement recovered authority");
        require(lease.active(), "replacement recovery returned no lease", checks);
    }

    require(sqlite3_set_authorizer(db.get(), nullptr, nullptr) == SQLITE_OK,
            "could not disable authorizer in adversarial fixture", checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), second, "disabled authorizer");
        },
        "authorizer ownership probe failed",
        "disabled authorizer retained authority",
        checks);
}

void test_authorizer_teardown_consumes_retained_context(
    std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    const SyncSqliteConnectionAuthorityProof first =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "teardown baseline");
    require(sqlite3_get_clientdata(
                db.get(), "anonsync.sqlite.connection-authority.v1") != nullptr,
            "connection-authority state was not retained",
            checks);
    require(sqlite3_get_clientdata(
                db.get(), "anonsync.sqlite.authorizer-owner.v1") != nullptr,
            "authorizer lifetime claim was not retained",
            checks);

    revoke_sync_sqlite_connection_authority_before_close_noexcept(db.get());
    require(sqlite3_get_clientdata(
                db.get(), "anonsync.sqlite.connection-authority.v1") == nullptr,
            "teardown left the connection-authority state live",
            checks);
    require(sqlite3_get_clientdata(
                db.get(), "anonsync.sqlite.authorizer-owner.v1") == nullptr,
            "teardown left the authorizer lifetime claim live",
            checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), first, "revoked authority proof");
        },
        "connection incarnation is absent",
        "revoked proof retained a callback context",
        checks);

    // The close hook is intentionally idempotent and the singleton slot can be
    // claimed again only after the old callback context has been consumed.
    revoke_sync_sqlite_connection_authority_before_close_noexcept(db.get());
    const SyncSqliteConnectionAuthorityProof second =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "teardown replacement");
    require(second.authorizer_generation() == 1U,
            "fresh authority state did not restart its local generation",
            checks);
}

void test_cross_connection_and_close_reopen(std::uint64_t& checks) {
    SyncSqliteConnectionAuthorityProof stale;
    {
        SqlitePtr first = open_memory_database();
        stale = install_sync_sqlite_connection_authority_or_throw(
            first.get(), deny_schema_policy, nullptr, "first incarnation");
        SqlitePtr concurrent = open_memory_database();
        require_throws(
            [&] {
                (void)acquire_sync_sqlite_connection_authority_or_throw(
                    concurrent.get(), stale, "cross connection proof");
            },
            "connection incarnation is absent",
            "authority proof crossed a distinct live SQLite connection",
            checks);
    }

    SqlitePtr reopened = open_memory_database();
    // Whether or not malloc reuses the address, a closed incarnation has no
    // client-data authority on the newly opened handle.
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                reopened.get(), stale, "closed incarnation proof");
        },
        "connection incarnation is absent",
        "closed connection proof authorized a reopened connection",
        checks);
}

void test_lease_serializes_replacement(std::uint64_t& checks) {
    using namespace std::chrono_literals;
    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(db.get(),
                         "CREATE TABLE lease_commit_probe(value INTEGER);",
                         "lease commit probe schema");
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "lease serialization baseline");

    std::atomic<bool> replacement_started{false};
    std::atomic<bool> replacement_finished{false};
    std::atomic<int> replacement_rc{SQLITE_ERROR};
    std::jthread replacer;
    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "lease serialization acquire");
        replacer = std::jthread([&] {
            replacement_started.store(true, std::memory_order_release);
            replacement_rc.store(
                sqlite3_set_authorizer(db.get(), alien_allow_authorizer, nullptr),
                std::memory_order_release);
            replacement_finished.store(true, std::memory_order_release);
        });
        const auto start_deadline = std::chrono::steady_clock::now() + 2s;
        while (!replacement_started.load(std::memory_order_acquire) &&
               std::chrono::steady_clock::now() < start_deadline) {
            std::this_thread::yield();
        }
        require(replacement_started.load(std::memory_order_acquire),
                "replacement thread did not start", checks);
        std::this_thread::sleep_for(30ms);
        require(!replacement_finished.load(std::memory_order_acquire),
                "connection authority lease did not block callback replacement",
                checks);
        require_throws(
            [&] {
                sqlite_exec_or_throw(db.get(),
                                     "CREATE TABLE blocked_while_leased(x);",
                                     "lease-protected DDL");
            },
            "not authorized",
            "lease-protected prepare escaped the owned policy",
            checks);
        SyncSqliteTransaction transaction(
            db.get(), "lease commit", SyncSqliteTransactionMode::Immediate);
        sqlite_exec_or_throw(
            db.get(),
            "INSERT INTO lease_commit_probe(value) VALUES(1);",
            "lease commit insert");
        transaction.commit();
        require(!replacement_finished.load(std::memory_order_acquire),
                "callback replacement crossed the transaction commit boundary",
                checks);
    }
    replacer.join();
    require(replacement_finished.load(std::memory_order_acquire) &&
                replacement_rc.load(std::memory_order_acquire) == SQLITE_OK,
            "blocked callback replacement did not complete after lease release",
            checks);
    SyncSqliteStmt committed = sqlite_prepare_or_throw(
        db.get(),
        "SELECT COUNT(*) FROM lease_commit_probe;",
        "lease commit count prepare");
    require(sqlite3_step(committed.stmt) == SQLITE_ROW &&
                sqlite3_column_int64(committed.stmt, 0) == 1,
            "lease-protected transaction was not committed exactly once",
            checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "post-lease replacement");
        },
        "authorizer ownership probe failed",
        "post-lease alien replacement was not detected",
        checks);
}

void test_transaction_retains_same_handle_serialization(
    std::uint64_t& checks) {
    using namespace std::chrono_literals;
    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(db.get(),
                         "CREATE TABLE retained_mutex_probe(value INTEGER);",
                         "retained mutex schema");
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "retained mutex baseline");

    std::atomic<bool> replacement_started{false};
    std::atomic<bool> replacement_finished{false};
    std::atomic<int> replacement_rc{SQLITE_ERROR};
    std::jthread replacer;
    {
        SyncSqliteTransaction transaction(
            db.get(), "retained mutex transaction", SyncSqliteTransactionMode::Immediate);
        replacer = std::jthread([&] {
            replacement_started.store(true, std::memory_order_release);
            replacement_rc.store(
                sqlite3_set_authorizer(db.get(), alien_allow_authorizer, nullptr),
                std::memory_order_release);
            replacement_finished.store(true, std::memory_order_release);
        });
        const auto start_deadline = std::chrono::steady_clock::now() + 2s;
        while (!replacement_started.load(std::memory_order_acquire) &&
               std::chrono::steady_clock::now() < start_deadline) {
            std::this_thread::yield();
        }
        require(replacement_started.load(std::memory_order_acquire),
                "same-handle replacement thread did not start", checks);
        std::this_thread::sleep_for(30ms);
        require(!replacement_finished.load(std::memory_order_acquire),
                "typed transaction released the connection mutex before rollback",
                checks);
        sqlite_exec_or_throw(
            db.get(),
            "INSERT INTO retained_mutex_probe(value) VALUES(1);",
            "retained mutex insert");
        transaction.rollback();
    }
    replacer.join();
    require(replacement_finished.load(std::memory_order_acquire) &&
                replacement_rc.load(std::memory_order_acquire) == SQLITE_OK,
            "same-handle replacement did not resume after typed rollback", checks);
    require_throws(
        [&] {
            (void)acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "retained mutex post-rollback replacement");
        },
        "authorizer ownership probe failed",
        "alien callback replacement was not visible after mutex release", checks);
}

void test_transaction_stack_is_typed_and_generation_bound(
    std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(db.get(),
                         "CREATE TABLE transaction_fence_probe(value INTEGER);",
                         "transaction fence schema");

    const std::string raw_begin_sql = "BEGIN IMMEDIATE;";
    SyncSqliteStmtHandleSlot prepared_begin;
    const int prepare_rc = sqlite3_prepare_v3(
        db.get(),
        raw_begin_sql.data(),
        static_cast<int>(raw_begin_sql.size()),
        SQLITE_PREPARE_PERSISTENT,
        prepared_begin.out(),
        nullptr);
    if (prepare_rc != SQLITE_OK || prepared_begin.empty()) {
        fail("could not prepare pre-fence BEGIN fixture");
    }

    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "transaction stack fence");
    require(proof.valid(), "transaction stack fence did not install", checks);
    require(sqlite3_step(prepared_begin) == SQLITE_AUTH,
            "BEGIN prepared before authority installation bypassed reauthorization",
            checks);
    require(sqlite3_reset(prepared_begin) == SQLITE_AUTH,
            "denied pre-fence BEGIN did not preserve SQLITE_AUTH", checks);
    require(sqlite3_get_autocommit(db.get()) != 0,
            "denied pre-fence BEGIN changed transaction state", checks);

    for (const std::string& sql : {
             std::string("BEGIN;"),
             std::string("BEGIN IMMEDIATE;"),
             std::string("BEGIN EXCLUSIVE;"),
             std::string("SAVEPOINT raw_outer;")}) {
        require_throws(
            [&] { sqlite_exec_or_throw(db.get(), sql, "raw transaction start"); },
            "not authorized",
            "raw transaction-stack start escaped the owned bridge: " + sql,
            checks);
        require(sqlite3_get_autocommit(db.get()) != 0,
                "denied transaction-stack start changed autocommit: " + sql,
                checks);
    }

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed fenced transaction", SyncSqliteTransactionMode::Immediate);
        require(transaction.active() && transaction.authorizes_write(db.get()),
                "typed BEGIN did not acquire exact fenced write authority", checks);

        for (const std::string& sql : {
                 std::string("COMMIT;"),
                 std::string("END;"),
                 std::string("ROLLBACK;"),
                 std::string("SAVEPOINT nested_raw;"),
                 std::string("RELEASE nested_raw;"),
                 std::string("ROLLBACK TO nested_raw;")}) {
            require_throws(
                [&] { sqlite_exec_or_throw(db.get(), sql, "raw transaction end"); },
                "not authorized",
                "raw transaction-stack mutation escaped the typed generation: " +
                    sql,
                checks);
            require(sqlite3_get_autocommit(db.get()) == 0 &&
                        transaction.active(),
                    "denied raw boundary revoked the typed transaction: " + sql,
                    checks);
        }

        sqlite_exec_or_throw(
            db.get(),
            "INSERT INTO transaction_fence_probe(value) VALUES(1);",
            "typed fenced insert");
        transaction.commit();
        require(!transaction.active() && sqlite3_get_autocommit(db.get()) != 0,
                "typed COMMIT did not revoke and close its exact generation", checks);
    }

    SyncSqliteStmt committed = sqlite_prepare_or_throw(
        db.get(),
        "SELECT COUNT(*) FROM transaction_fence_probe;",
        "transaction fence count");
    require(sqlite3_step(committed.stmt) == SQLITE_ROW &&
                sqlite3_column_int64(committed.stmt, 0) == 1,
            "typed fenced COMMIT did not persist exactly one row", checks);
    committed = SyncSqliteStmt();

    {
        SyncSqliteTransaction deferred(
            db.get(), "typed fenced deferred", SyncSqliteTransactionMode::Deferred);
        require(deferred.active() && !deferred.authorizes_snapshot(db.get()),
                "typed deferred boundary was not live before snapshot acquisition",
                checks);
        deferred.rollback();
        require(!deferred.active() && sqlite3_get_autocommit(db.get()) != 0,
                "typed fenced ROLLBACK did not restore autocommit", checks);
    }
}


void test_typed_savepoint_stack_and_atomicity(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(
        db.get(),
        "CREATE TABLE savepoint_probe(value INTEGER PRIMARY KEY);",
        "typed savepoint schema");
    (void)install_sync_sqlite_connection_authority_or_throw(
        db.get(), deny_schema_policy, nullptr, "typed savepoint authority");

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint release parent",
            SyncSqliteTransactionMode::Immediate);
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(1);",
            "typed savepoint outer row");
        SyncSqliteSavepoint savepoint(
            db.get(), transaction.authority(), "typed savepoint release");
        require(savepoint.active(),
                "typed savepoint did not acquire an exact live generation",
                checks);
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(2);",
            "typed savepoint released row");
        savepoint.release();
        require(!savepoint.active() && transaction.active(),
                "savepoint release revoked or committed its parent transaction",
                checks);
        transaction.commit();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe;",
                       "typed savepoint release count") == 2,
            "released savepoint changes were not committed by the parent",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint destructor parent",
            SyncSqliteTransactionMode::Immediate);
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(3);",
            "typed savepoint destructor parent row");
        {
            SyncSqliteSavepoint savepoint(
                db.get(), transaction.authority(), "typed savepoint destructor");
            sqlite_exec_or_throw(
                db.get(), "INSERT INTO savepoint_probe(value) VALUES(4);",
                "typed savepoint destructor discarded row");
        }
        require(transaction.active(),
                "savepoint destructor ended its parent transaction",
                checks);
        transaction.commit();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe WHERE value IN (3,4);",
                       "typed savepoint destructor count") == 1 &&
                scalar_i64(db.get(),
                           "SELECT COUNT(*) FROM savepoint_probe WHERE value=3;",
                           "typed savepoint destructor preserved parent") == 1,
            "savepoint destructor did not discard only its nested mutation",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint explicit rollback parent",
            SyncSqliteTransactionMode::Immediate);
        SyncSqliteSavepoint savepoint(
            db.get(), transaction.authority(), "typed savepoint explicit rollback");
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(5);",
            "typed savepoint explicit rollback row");
        savepoint.rollback();
        require(!savepoint.active() && transaction.active(),
                "explicit savepoint rollback did not preserve the parent",
                checks);
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(6);",
            "typed savepoint post-rollback parent row");
        transaction.commit();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe WHERE value IN (5,6);",
                       "typed savepoint explicit rollback count") == 1 &&
                scalar_i64(db.get(),
                           "SELECT COUNT(*) FROM savepoint_probe WHERE value=6;",
                           "typed savepoint explicit rollback survivor") == 1,
            "explicit savepoint rollback discarded or preserved the wrong rows",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed nested savepoint parent",
            SyncSqliteTransactionMode::Immediate);
        SyncSqliteSavepoint outer(
            db.get(), transaction.authority(), "typed nested savepoint outer");
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(7);",
            "typed nested outer row");
        SyncSqliteSavepoint inner(
            db.get(), transaction.authority(), "typed nested savepoint inner");
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(8);",
            "typed nested inner row");
        require(outer.active() && inner.active(),
                "a non-top typed savepoint lost its exact stack generation",
                checks);
        require_throws(
            [&] { outer.release(); },
            "reverse construction order",
            "an outer savepoint closed across a newer inner frame",
            checks);
        require(outer.active() && inner.active() && transaction.active(),
                "rejected out-of-order release damaged the live stack",
                checks);
        inner.rollback();
        outer.release();
        transaction.commit();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe WHERE value IN (7,8);",
                       "typed nested savepoint count") == 1 &&
                scalar_i64(db.get(),
                           "SELECT COUNT(*) FROM savepoint_probe WHERE value=7;",
                           "typed nested outer survivor") == 1,
            "nested LIFO rollback/release preserved the wrong frame",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint commit fence parent",
            SyncSqliteTransactionMode::Immediate);
        SyncSqliteSavepoint savepoint(
            db.get(), transaction.authority(), "typed savepoint commit fence");
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(9);",
            "typed savepoint commit-fence row");
        require_throws(
            [&] { transaction.commit(); },
            "typed savepoint remains active",
            "outer COMMIT erased a live nested savepoint stack",
            checks);
        require(transaction.active() && savepoint.active(),
                "rejected outer COMMIT revoked a retryable savepoint stack",
                checks);
        savepoint.release();
        transaction.commit();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe WHERE value=9;",
                       "typed savepoint commit-fence count") == 1,
            "savepoint could not be released after a rejected outer COMMIT",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint parent rollback",
            SyncSqliteTransactionMode::Immediate);
        auto savepoint = std::make_unique<SyncSqliteSavepoint>(
            db.get(), transaction.authority(), "typed savepoint parent rollback child");
        sqlite_exec_or_throw(
            db.get(), "INSERT INTO savepoint_probe(value) VALUES(10);",
            "typed savepoint parent rollback row");
        transaction.rollback();
        require(!transaction.active() && !savepoint->active() &&
                    sqlite3_get_autocommit(db.get()) != 0,
                "outer ROLLBACK did not revoke the complete typed stack",
                checks);
        savepoint.reset();
    }
    require(scalar_i64(db.get(),
                       "SELECT COUNT(*) FROM savepoint_probe WHERE value=10;",
                       "typed savepoint parent rollback count") == 0,
            "outer ROLLBACK preserved nested savepoint changes",
            checks);

    {
        SyncSqliteTransaction transaction(
            db.get(), "typed savepoint stale authority parent",
            SyncSqliteTransactionMode::Immediate);
        const SyncSqliteTransactionAuthority stale = transaction.authority();
        transaction.commit();
        require_throws(
            [&] {
                SyncSqliteSavepoint savepoint(
                    db.get(), stale, "typed savepoint stale authority");
            },
            "not live",
            "a stale transaction authority minted a later savepoint",
            checks);
    }

    {
        SqlitePtr denied = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            denied.get(),
            ignore_savepoint_policy,
            nullptr,
            "ignored savepoint policy");
        SyncSqliteTransaction transaction(
            denied.get(), "ignored savepoint policy parent",
            SyncSqliteTransactionMode::Immediate);
        require_throws(
            [&] {
                SyncSqliteSavepoint savepoint(
                    denied.get(), transaction.authority(),
                    "ignored savepoint policy child");
            },
            "not authorized",
            "SQLITE_IGNORE acquired savepoint-boundary authority",
            checks);
        require(transaction.active() && sqlite3_get_autocommit(denied.get()) == 0,
                "denied savepoint begin damaged its parent transaction",
                checks);
        transaction.rollback();
    }

    {
        SyncSqliteTransaction compromised(
            db.get(), "typed savepoint callback replacement parent",
            SyncSqliteTransactionMode::Immediate);
        SyncSqliteSavepoint savepoint(
            db.get(), compromised.authority(),
            "typed savepoint callback replacement child");
        require(sqlite3_set_authorizer(
                    db.get(), alien_allow_authorizer, nullptr) == SQLITE_OK,
                "could not replace authorizer during a typed savepoint",
                checks);
        require_throws(
            [&] { savepoint.release(); },
            "no longer owned",
            "typed savepoint claimed release after callback replacement",
            checks);
        require(!savepoint.active() && sqlite3_get_autocommit(db.get()) == 0,
                "callback replacement silently ended the SQLite transaction",
                checks);
        require_throws(
            [&] { compromised.commit(); },
            "no longer owned",
            "outer transaction claimed COMMIT after callback replacement",
            checks);
        sqlite_exec_or_throw(
            db.get(), "ROLLBACK;", "typed savepoint callback replacement cleanup");
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr,
            "typed savepoint callback replacement recovery");
    }

    {
        SqlitePtr unowned = open_memory_database();
        sqlite_exec_or_throw(
            unowned.get(),
            "CREATE TABLE unowned_savepoint_probe(value INTEGER PRIMARY KEY);",
            "unowned savepoint schema");
        {
            SyncSqliteSavepoint savepoint(
                unowned.get(), "unowned outermost savepoint rollback");
            sqlite_exec_or_throw(
                unowned.get(),
                "INSERT INTO unowned_savepoint_probe(value) VALUES(1);",
                "unowned outermost rolled-back row");
            savepoint.rollback();
        }
        require(sqlite3_get_autocommit(unowned.get()) != 0 &&
                    scalar_i64(unowned.get(),
                               "SELECT COUNT(*) FROM unowned_savepoint_probe;",
                               "unowned outermost rollback count") == 0,
                "unowned outermost savepoint rollback did not restore autocommit",
                checks);
        {
            SyncSqliteSavepoint savepoint(
                unowned.get(), "unowned outermost savepoint release");
            sqlite_exec_or_throw(
                unowned.get(),
                "INSERT INTO unowned_savepoint_probe(value) VALUES(2);",
                "unowned outermost released row");
            savepoint.release();
        }
        require(sqlite3_get_autocommit(unowned.get()) != 0 &&
                    scalar_i64(unowned.get(),
                               "SELECT COUNT(*) FROM unowned_savepoint_probe;",
                               "unowned outermost release count") == 1,
                "unowned outermost savepoint release did not commit its mark",
                checks);
        {
            SyncSqliteTransaction transaction(
                unowned.get(), "unowned typed transaction parent",
                SyncSqliteTransactionMode::Immediate);
            SyncSqliteSavepoint savepoint(
                unowned.get(), "unowned nested compatibility savepoint");
            sqlite_exec_or_throw(
                unowned.get(),
                "INSERT INTO unowned_savepoint_probe(value) VALUES(3);",
                "unowned nested compatibility row");
            savepoint.release();
            transaction.rollback();
        }
        require(sqlite3_get_autocommit(unowned.get()) != 0 &&
                    scalar_i64(unowned.get(),
                               "SELECT COUNT(*) FROM unowned_savepoint_probe WHERE value=3;",
                               "unowned nested compatibility count") == 0,
                "nested compatibility savepoint escaped parent rollback",
                checks);
    }
}

void test_transaction_policy_and_authorizer_replacement_fail_closed(
    std::uint64_t& checks) {
    {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), malformed_policy, nullptr, "malformed transaction policy");
        require_throws(
            [&] {
                SyncSqliteTransaction transaction(
                    db.get(), "malformed policy typed begin");
            },
            "not authorized",
            "malformed policy result authorized a typed transaction", checks);
        require(sqlite3_get_autocommit(db.get()) != 0,
                "malformed transaction policy left a boundary active", checks);
    }
    {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), ignore_transaction_policy, nullptr, "ignored transaction policy");
        require_throws(
            [&] {
                SyncSqliteTransaction transaction(
                    db.get(), "ignored policy typed begin");
            },
            "not authorized",
            "SQLITE_IGNORE acquired transaction-boundary authority", checks);
        require(sqlite3_get_autocommit(db.get()) != 0,
                "ignored transaction policy left a boundary active", checks);
    }

    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(db.get(),
                         "CREATE TABLE replacement_probe(value INTEGER);",
                         "replacement transaction schema");
    const SyncSqliteConnectionAuthorityProof first =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "active generation baseline");
    {
        SyncSqliteTransaction active(db.get(), "active generation replacement");
        require_throws(
            [&] {
                (void)install_sync_sqlite_connection_authority_or_throw(
                    db.get(),
                    deny_schema_policy,
                    nullptr,
                    "active generation reinstall");
            },
            "inside an active transaction",
            "owned authorizer generation was superseded inside a transaction",
            checks);
        active.rollback();
    }

    const SyncSqliteConnectionAuthorityProof second =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "post-rollback generation");
    require(second.authorizer_generation() == first.authorizer_generation() + 1,
            "post-rollback authorizer reinstall did not advance generation", checks);

    {
        SyncSqliteTransaction compromised(
            db.get(), "alien authorizer transaction", SyncSqliteTransactionMode::Immediate);
        require(sqlite3_set_authorizer(
                    db.get(), alien_allow_authorizer, nullptr) == SQLITE_OK,
                "could not replace authorizer during adversarial transaction", checks);
        require_throws(
            [&] { compromised.commit(); },
            "no longer owned",
            "typed COMMIT claimed success after authorizer replacement", checks);
        require(!compromised.active() && sqlite3_get_autocommit(db.get()) == 0,
                "authorizer replacement was not detected without falsely ending SQL state",
                checks);
        sqlite_exec_or_throw(
            db.get(), "ROLLBACK;", "alien transaction cleanup rollback");
    }

    const SyncSqliteConnectionAuthorityProof third =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "alien replacement recovery");
    require(third.authorizer_generation() == second.authorizer_generation() + 1,
            "alien replacement recovery did not advance generation", checks);

    // Destruction after alien replacement must not issue an unproven raw
    // rollback. The alien callback can end generation N and begin N+1 without
    // exposing any SQLite transaction identifier. Rolling back N+1 would be a
    // false ownership claim.
    {
        auto stale = std::make_unique<SyncSqliteTransaction>(
            db.get(), "destructor generation ambiguity");
        require(sqlite3_set_authorizer(
                    db.get(), alien_allow_authorizer, nullptr) == SQLITE_OK,
                "could not install alien authorizer for destructor fixture", checks);
        sqlite_exec_or_throw(
            db.get(), "COMMIT;", "alien commit exact typed generation");
        sqlite_exec_or_throw(
            db.get(), "BEGIN IMMEDIATE;", "alien begin later generation");
        sqlite_exec_or_throw(
            db.get(),
            "INSERT INTO replacement_probe(value) VALUES(9);",
            "alien later-generation insert");
        stale.reset();
        require(sqlite3_get_autocommit(db.get()) == 0,
                "stale typed destructor rolled back a later alien transaction",
                checks);
        SyncSqliteStmt visible = sqlite_prepare_or_throw(
            db.get(),
            "SELECT COUNT(*) FROM replacement_probe;",
            "alien later-generation visibility");
        require(sqlite3_step(visible.stmt) == SQLITE_ROW &&
                    sqlite3_column_int64(visible.stmt, 0) == 1,
                "later alien transaction was not preserved for explicit cleanup",
                checks);
        sqlite_exec_or_throw(
            db.get(), "ROLLBACK;", "alien later-generation cleanup");
    }

    const SyncSqliteConnectionAuthorityProof fourth =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "destructor ambiguity recovery");
    require(fourth.authorizer_generation() == third.authorizer_generation() + 1,
            "stale generation was not safely cleared after explicit rollback", checks);
}


void test_thread_incarnation_affinity(std::uint64_t& checks) {
    using namespace std::chrono_literals;

    SqlitePtr db = open_memory_database();
    sqlite_exec_or_throw(db.get(),
                         "CREATE TABLE thread_affinity_probe(value INTEGER);",
                         "thread affinity schema");
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "thread affinity baseline");

    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "thread affinity lease");
        require(lease.active(), "owner thread did not retain an active lease", checks);

        bool foreign_active = true;
        std::thread observer([&] { foreign_active = lease.active(); });
        observer.join();
        require(!foreign_active,
                "connection authority lease appeared active on a foreign thread",
                checks);
        require(lease.active(),
                "foreign-thread observation revoked the owner-thread lease",
                checks);
    }

    SyncSqliteTransaction transaction(
        db.get(), "thread-affine transaction", SyncSqliteTransactionMode::Immediate);
    const SyncSqliteTransactionAuthority authority = transaction.authority();

    std::promise<std::pair<bool, bool>> authority_promise;
    std::future<std::pair<bool, bool>> authority_result =
        authority_promise.get_future();
    std::thread authority_observer([&] {
        authority_promise.set_value(
            {transaction.active(), authority.authorizes(db.get())});
    });
    const bool authority_ready =
        authority_result.wait_for(2s) == std::future_status::ready;
    if (!authority_ready) {
        fail_without_unwinding_live_thread(
            "foreign-thread transaction authority observation blocked");
    }
    const auto [foreign_transaction_active, foreign_authorized] =
        authority_result.get();
    authority_observer.join();
    require(!foreign_transaction_active,
            "typed transaction appeared active on a foreign thread",
            checks);
    require(!foreign_authorized,
            "transaction authority crossed its originating thread incarnation",
            checks);
    require(transaction.active(),
            "foreign-thread authority observation revoked the owner generation",
            checks);

    std::promise<std::string> commit_promise;
    std::future<std::string> commit_result = commit_promise.get_future();
    std::thread foreign_committer([&] {
        try {
            transaction.commit();
            commit_promise.set_value("unexpected success");
        } catch (const std::exception& error) {
            commit_promise.set_value(error.what());
        }
    });
    const bool commit_ready =
        commit_result.wait_for(2s) == std::future_status::ready;
    if (!commit_ready) {
        fail_without_unwinding_live_thread(
            "foreign-thread typed COMMIT blocked on the owner-held mutex");
    }
    const std::string commit_reason = commit_result.get();
    foreign_committer.join();
    require(commit_reason.find("originating SQLite mutex thread") !=
                std::string::npos,
            "foreign-thread typed COMMIT did not fail at the affinity boundary: " +
                commit_reason,
            checks);
    require(transaction.active(),
            "rejected foreign-thread COMMIT revoked the owner generation",
            checks);

    std::promise<std::string> rollback_promise;
    std::future<std::string> rollback_result = rollback_promise.get_future();
    std::thread foreign_rollback([&] {
        try {
            transaction.rollback();
            rollback_promise.set_value("unexpected success");
        } catch (const std::exception& error) {
            rollback_promise.set_value(error.what());
        }
    });
    const bool rollback_ready =
        rollback_result.wait_for(2s) == std::future_status::ready;
    if (!rollback_ready) {
        fail_without_unwinding_live_thread(
            "foreign-thread typed ROLLBACK blocked on the owner-held mutex");
    }
    const std::string rollback_reason = rollback_result.get();
    foreign_rollback.join();
    require(rollback_reason.find("originating SQLite mutex thread") !=
                std::string::npos,
            "foreign-thread typed ROLLBACK did not fail at the affinity boundary: " +
                rollback_reason,
            checks);
    require(transaction.active(),
            "rejected foreign-thread ROLLBACK revoked the owner generation",
            checks);

    SyncSqliteSavepoint savepoint(
        db.get(), authority, "thread-affine typed savepoint");
    bool foreign_savepoint_active = true;
    std::thread savepoint_observer(
        [&] { foreign_savepoint_active = savepoint.active(); });
    savepoint_observer.join();
    require(!foreign_savepoint_active,
            "typed savepoint appeared active on a foreign thread",
            checks);
    require(savepoint.active(),
            "foreign-thread savepoint observation revoked the owner generation",
            checks);

    std::promise<std::string> savepoint_release_promise;
    std::future<std::string> savepoint_release_result =
        savepoint_release_promise.get_future();
    std::thread foreign_savepoint_releaser([&] {
        try {
            savepoint.release();
            savepoint_release_promise.set_value("unexpected success");
        } catch (const std::exception& error) {
            savepoint_release_promise.set_value(error.what());
        }
    });
    if (savepoint_release_result.wait_for(2s) != std::future_status::ready) {
        fail_without_unwinding_live_thread(
            "foreign-thread typed savepoint RELEASE blocked on the owner-held mutex");
    }
    const std::string savepoint_release_reason = savepoint_release_result.get();
    foreign_savepoint_releaser.join();
    require(savepoint_release_reason.find("originating SQLite mutex thread") !=
                std::string::npos,
            "foreign-thread typed savepoint RELEASE did not fail at the affinity boundary: " +
                savepoint_release_reason,
            checks);
    require(savepoint.active(),
            "rejected foreign-thread savepoint RELEASE revoked the owner generation",
            checks);

    std::promise<std::string> savepoint_rollback_promise;
    std::future<std::string> savepoint_rollback_result =
        savepoint_rollback_promise.get_future();
    std::thread foreign_savepoint_rollback([&] {
        try {
            savepoint.rollback();
            savepoint_rollback_promise.set_value("unexpected success");
        } catch (const std::exception& error) {
            savepoint_rollback_promise.set_value(error.what());
        }
    });
    if (savepoint_rollback_result.wait_for(2s) != std::future_status::ready) {
        fail_without_unwinding_live_thread(
            "foreign-thread typed savepoint ROLLBACK blocked on the owner-held mutex");
    }
    const std::string savepoint_rollback_reason =
        savepoint_rollback_result.get();
    foreign_savepoint_rollback.join();
    require(savepoint_rollback_reason.find("originating SQLite mutex thread") !=
                std::string::npos,
            "foreign-thread typed savepoint ROLLBACK did not fail at the affinity boundary: " +
                savepoint_rollback_reason,
            checks);
    require(savepoint.active(),
            "rejected foreign-thread savepoint ROLLBACK revoked the owner generation",
            checks);

    savepoint.rollback();
    transaction.rollback();
    require(sqlite3_get_autocommit(db.get()) != 0,
            "owner thread could not roll back after rejected foreign finalization",
            checks);
}

void test_owner_thread_lease_moves(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database();
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "owner lease move baseline");

    SyncSqliteConnectionAuthorityLease source =
        acquire_sync_sqlite_connection_authority_or_throw(
            db.get(), proof, "owner lease move source");
    SyncSqliteConnectionAuthorityLease moved(std::move(source));
    require(!source.active() && moved.active(),
            "owner-thread lease move construction did not transfer authority",
            checks);

    SyncSqliteConnectionAuthorityLease* const same_object = &moved;
    moved = std::move(*same_object);
    require(moved.active(),
            "owner-thread lease self-move revoked its retained capability",
            checks);

    SyncSqliteConnectionAuthorityLease replacement =
        acquire_sync_sqlite_connection_authority_or_throw(
            db.get(), proof, "owner lease move replacement");
    moved = std::move(replacement);
    require(moved.active() && !replacement.active(),
            "owner-thread lease move assignment did not transfer one exact entry",
            checks);
}

#if defined(__linux__)
constexpr int kHostileTerminateExit = 87;
constexpr int kAffinityUnexpectedReturnExit = 88;
constexpr int kAffinitySetupFailureExit = 89;

[[noreturn]] void hostile_affinity_terminate_handler() noexcept {
    std::_Exit(kHostileTerminateExit);
}

void child_foreign_lease_destruction() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "foreign lease destructor");
        auto* lease = new SyncSqliteConnectionAuthorityLease(
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "foreign lease destructor acquire"));
        std::set_terminate(hostile_affinity_terminate_handler);
        std::thread destroyer([lease] { delete lease; });
        destroyer.join();
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_foreign_transaction_destruction() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "foreign transaction destructor");
        auto* transaction = new SyncSqliteTransaction(
            db.get(), "foreign transaction destructor");
        std::set_terminate(hostile_affinity_terminate_handler);
        std::thread destroyer([transaction] { delete transaction; });
        destroyer.join();
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_foreign_savepoint_destruction() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        auto* savepoint = new SyncSqliteSavepoint(
            db.get(), "foreign savepoint destructor");
        std::set_terminate(hostile_affinity_terminate_handler);
        std::thread destroyer([savepoint] { delete savepoint; });
        destroyer.join();
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_foreign_lease_move() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "foreign lease move");
        auto* lease = new SyncSqliteConnectionAuthorityLease(
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "foreign lease move acquire"));
        std::set_terminate(hostile_affinity_terminate_handler);
        std::thread mover([lease] {
            SyncSqliteConnectionAuthorityLease moved(std::move(*lease));
            (void)moved;
        });
        mover.join();
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_close_with_live_lease() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "live lease close fence");
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "live lease close fence acquire");
        std::set_terminate(hostile_affinity_terminate_handler);
        (void)sqlite3_close_v2(db.get());
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_close_with_live_unfenced_transaction() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        SyncSqliteTransaction transaction(
            db.get(), "live unfenced transaction close fence");
        std::set_terminate(hostile_affinity_terminate_handler);
        (void)sqlite3_close_v2(db.get());
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_close_with_live_fenced_transaction() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "live fenced transaction close fence");
        SyncSqliteTransaction transaction(
            db.get(), "live fenced transaction close fence");
        std::set_terminate(hostile_affinity_terminate_handler);
        (void)sqlite3_close_v2(db.get());
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_close_with_live_unfenced_savepoint() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        SyncSqliteSavepoint savepoint(
            db.get(), "live unfenced savepoint close fence");
        std::set_terminate(hostile_affinity_terminate_handler);
        (void)sqlite3_close_v2(db.get());
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_close_with_live_authorizer_only() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr,
            "live authorizer-only close fence");
        std::set_terminate(hostile_affinity_terminate_handler);
        (void)sqlite3_close_v2(db.get());
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_replace_live_authority_state() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        (void)install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr,
            "live authority-state replacement fence");
        std::set_terminate(hostile_affinity_terminate_handler);
        // The state pointer is SQLite's retained authorizer context. Replacing
        // its client-data slot must terminate before that address can be freed
        // and later re-entered by sqlite3_prepare().
        (void)sqlite3_set_clientdata(
            db.get(),
            "anonsync.sqlite.connection-authority.v1",
            nullptr,
            nullptr);
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_replace_live_capability_sentinel() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "live sentinel replacement fence");
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "live sentinel replacement fence acquire");
        std::set_terminate(hostile_affinity_terminate_handler);
        // A second registration under the private namespace invokes the old
        // SQLite-owned destructor. It must not invalidate a retained mutex
        // pointer and return to the caller.
        (void)sqlite3_set_clientdata(
            db.get(),
            "anonsync.sqlite.retained-mutex-capabilities.v1",
            nullptr,
            nullptr);
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}

void child_zombie_close_with_live_lease() noexcept {
    try {
        SqlitePtr db = open_memory_database();
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(db.get(), "SELECT 1;", -1, &statement, nullptr) !=
                SQLITE_OK ||
            statement == nullptr) {
            std::_Exit(kAffinitySetupFailureExit);
        }
        const SyncSqliteConnectionAuthorityProof proof =
            install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "zombie close fence");
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "zombie close fence acquire");
        std::set_terminate(hostile_affinity_terminate_handler);
        if (sqlite3_close_v2(db.get()) != SQLITE_OK) {
            std::_Exit(kAffinityUnexpectedReturnExit);
        }
        // sqlite3_close_v2() may defer physical destruction while this
        // statement keeps the connection zombie alive. Whichever operation
        // reaches client-data destruction must detect the retained mutex
        // capability before the mutex becomes dangling.
        (void)sqlite3_finalize(statement);
        std::_Exit(kAffinityUnexpectedReturnExit);
    } catch (...) {
        std::_Exit(kAffinitySetupFailureExit);
    }
}


constexpr std::string_view kAffinityWorkerFlag =
    "--anonsync-sqlite-connection-authority-affinity-worker-v1";

[[noreturn]] void run_affinity_worker_scenario(std::string_view scenario) {
    if (scenario == "foreign-lease-destruction") {
        child_foreign_lease_destruction();
    }
    if (scenario == "foreign-transaction-destruction") {
        child_foreign_transaction_destruction();
    }
    if (scenario == "foreign-savepoint-destruction") {
        child_foreign_savepoint_destruction();
    }
    if (scenario == "foreign-lease-move") {
        child_foreign_lease_move();
    }
    if (scenario == "close-live-lease") {
        child_close_with_live_lease();
    }
    if (scenario == "close-live-unfenced-transaction") {
        child_close_with_live_unfenced_transaction();
    }
    if (scenario == "close-live-fenced-transaction") {
        child_close_with_live_fenced_transaction();
    }
    if (scenario == "close-live-unfenced-savepoint") {
        child_close_with_live_unfenced_savepoint();
    }
    if (scenario == "close-live-authorizer-only") {
        child_close_with_live_authorizer_only();
    }
    if (scenario == "replace-live-authority-state") {
        child_replace_live_authority_state();
    }
    if (scenario == "replace-live-capability-sentinel") {
        child_replace_live_capability_sentinel();
    }
    if (scenario == "zombie-close-live-lease") {
        child_zombie_close_with_live_lease();
    }
    std::_Exit(kAffinitySetupFailureExit);
}

int dispatch_affinity_worker(int argc, char** argv) {
    if (argc < 2 || argv == nullptr || argv[1] == nullptr ||
        std::string_view(argv[1]) != kAffinityWorkerFlag) {
        return -1;
    }
    try {
        verify_self_exec_child_boundary_or_throw();
        if (argc != 3 || argv[2] == nullptr) {
            return kAffinitySetupFailureExit;
        }
        run_affinity_worker_scenario(argv[2]);
    } catch (...) {
        return kAffinitySetupFailureExit;
    }
}

void require_affinity_fail_stop(std::string_view scenario,
                                const std::string& message,
                                std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_or_throw(
        current_self_executable_or_throw(),
        {std::string(kAffinityWorkerFlag), std::string(scenario)});
    const int exit_code = child.wait_for_exit_code(
        5s, "SQLite connection-affinity fresh-image worker");
    require(exit_code == kSyncProcessCapabilityViolationExitCode,
            message + ": child exit=" + std::to_string(exit_code), checks);
}

#endif

void test_mutex_capability_violations_fail_stopped(std::uint64_t& checks) {
#if defined(__linux__)
    require_affinity_fail_stop(
        "foreign-lease-destruction",
        "foreign-thread connection lease destruction did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "foreign-transaction-destruction",
        "foreign-thread transaction destruction did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "foreign-savepoint-destruction",
        "foreign-thread savepoint destruction did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "foreign-lease-move",
        "foreign-thread connection lease move did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "close-live-lease",
        "same-thread close with a live connection lease did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "close-live-unfenced-transaction",
        "same-thread close with a live unfenced transaction did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "close-live-fenced-transaction",
        "same-thread close with a live fenced transaction did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "close-live-unfenced-savepoint",
        "same-thread close with a live unfenced savepoint did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "close-live-authorizer-only",
        "raw close with a live authorizer context did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "replace-live-authority-state",
        "replacement of the live authorizer context state did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "replace-live-capability-sentinel",
        "replacement of the live mutex-capability sentinel did not fail-stop",
        checks);
    require_affinity_fail_stop(
        "zombie-close-live-lease",
        "same-thread zombie close with a live connection lease did not fail-stop",
        checks);
#else
    (void)checks;
#endif
}

void test_close_waits_for_retained_mutex_capability(std::uint64_t& checks) {
    using namespace std::chrono_literals;

    SqlitePtr db = open_memory_database();
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            db.get(), deny_schema_policy, nullptr, "serialized close baseline");
    std::atomic<bool> close_started{false};
    std::atomic<bool> close_finished{false};
    std::atomic<int> close_rc{SQLITE_ERROR};
    std::jthread closer;

    {
        SyncSqliteConnectionAuthorityLease lease =
            acquire_sync_sqlite_connection_authority_or_throw(
                db.get(), proof, "serialized close lease");
        closer = std::jthread([&] {
            close_started.store(true, std::memory_order_release);
            revoke_sync_sqlite_connection_authority_before_close_noexcept(
                db.get());
            close_rc.store(sqlite3_close_v2(db.get()), std::memory_order_release);
            close_finished.store(true, std::memory_order_release);
        });
        const auto deadline = std::chrono::steady_clock::now() + 2s;
        while (!close_started.load(std::memory_order_acquire) &&
               std::chrono::steady_clock::now() < deadline) {
            std::this_thread::yield();
        }
        require(close_started.load(std::memory_order_acquire),
                "foreign close thread did not start", checks);
        std::this_thread::sleep_for(30ms);
        require(!close_finished.load(std::memory_order_acquire),
                "foreign close crossed a retained mutex capability",
                checks);
        require(lease.active(),
                "blocked foreign close revoked the owner lease",
                checks);
    }

    closer.join();
    require(close_finished.load(std::memory_order_acquire) &&
                close_rc.load(std::memory_order_acquire) == SQLITE_OK,
            "foreign close did not complete after capability release",
            checks);
    (void)db.release();

    SqlitePtr transaction_db = open_memory_database();
    {
        SyncSqliteTransaction transaction(
            transaction_db.get(), "normal close after typed rollback");
        transaction.rollback();
    }
    sqlite3* const raw = transaction_db.release();
    require(sqlite3_close_v2(raw) == SQLITE_OK,
            "connection could not close after typed capability revocation",
            checks);

    SqlitePtr savepoint_db = open_memory_database();
    {
        SyncSqliteSavepoint savepoint(
            savepoint_db.get(), "normal close after typed savepoint rollback");
        savepoint.rollback();
    }
    sqlite3* const savepoint_raw = savepoint_db.release();
    require(sqlite3_close_v2(savepoint_raw) == SQLITE_OK,
            "connection could not close after typed savepoint capability revocation",
            checks);
}

void test_fullmutex_is_required(std::uint64_t& checks) {
    SqlitePtr db = open_memory_database(SQLITE_OPEN_NOMUTEX);
    require_throws(
        [&] {
            (void)install_sync_sqlite_connection_authority_or_throw(
                db.get(), deny_schema_policy, nullptr, "nomutex rejection");
        },
        "requires a serialized/FULLMUTEX",
        "authority install accepted a NOMUTEX connection",
        checks);
}

}  // namespace

int main(int argc, char** argv) {
#if defined(__linux__)
    const int worker_result = dispatch_affinity_worker(argc, argv);
    if (worker_result >= 0) return worker_result;
#else
    (void)argc;
    (void)argv;
#endif
    std::uint64_t checks = 0;
    try {
        test_install_probe_and_policy(checks);
        test_policy_retirement_probe_cannot_lose_prestart_request(checks);
        test_owned_policy_context_lifetime_and_retirement(checks);
        test_prepared_statement_is_reauthorized(checks);
        test_policy_boundary_fails_closed(checks);
        test_replacement_disable_and_generation(checks);
        test_authorizer_teardown_consumes_retained_context(checks);
        test_cross_connection_and_close_reopen(checks);
        test_lease_serializes_replacement(checks);
        test_transaction_retains_same_handle_serialization(checks);
        test_transaction_stack_is_typed_and_generation_bound(checks);
        test_typed_savepoint_stack_and_atomicity(checks);
        test_transaction_policy_and_authorizer_replacement_fail_closed(checks);
        test_thread_incarnation_affinity(checks);
        test_owner_thread_lease_moves(checks);
        test_mutex_capability_violations_fail_stopped(checks);
        test_close_waits_for_retained_mutex_capability(checks);
        test_fullmutex_is_required(checks);
        std::cout << "sqlite connection authority checks=" << checks
                  << " failures=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite connection authority checks=" << checks
                  << " failures=1 reason=" << error.what() << "\n";
        return 1;
    }
}
