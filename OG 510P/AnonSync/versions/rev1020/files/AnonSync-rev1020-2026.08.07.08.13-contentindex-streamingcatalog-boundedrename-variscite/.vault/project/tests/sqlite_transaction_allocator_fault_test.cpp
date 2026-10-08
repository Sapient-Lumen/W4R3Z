#include "self_exec_test_process.hpp"
#include "sync_sqlite_connection_authority.hpp"
#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace {

using namespace anonsync;
using namespace std::chrono_literals;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

int allow_policy(void*,
                 int,
                 const char*,
                 const char*,
                 const char*,
                 const char*) noexcept {
    return SQLITE_OK;
}

struct FaultAllocatorState final {
    sqlite3_mem_methods base{};
    std::uint64_t attempts = 0;
    std::uint64_t failures = 0;
    std::uint64_t fail_at = 0;
    std::uint64_t live_blocks = 0;
    std::uint64_t live_bytes = 0;
    std::uint64_t peak_live_bytes = 0;
    bool accounting_corrupt = false;
    bool armed = false;
    bool sticky = false;
    bool configured = false;
};

FaultAllocatorState g_allocator;

bool allocation_should_fail(int bytes) noexcept {
    if (!g_allocator.armed || bytes <= 0) return false;
    ++g_allocator.attempts;
    if (g_allocator.fail_at == 0) return false;
    const bool fail_now = g_allocator.sticky
                              ? g_allocator.attempts >= g_allocator.fail_at
                              : g_allocator.attempts == g_allocator.fail_at;
    if (fail_now) ++g_allocator.failures;
    return fail_now;
}

void account_allocation(void* memory) noexcept {
    if (memory == nullptr) return;
    ++g_allocator.live_blocks;
    const int size = g_allocator.base.xSize(memory);
    if (size > 0) {
        g_allocator.live_bytes += static_cast<std::uint64_t>(size);
        g_allocator.peak_live_bytes =
            std::max(g_allocator.peak_live_bytes, g_allocator.live_bytes);
    }
}

void account_free(void* memory) noexcept {
    if (memory == nullptr) return;
    const int size = g_allocator.base.xSize(memory);
    if (g_allocator.live_blocks == 0 ||
        (size > 0 && g_allocator.live_bytes < static_cast<std::uint64_t>(size))) {
        g_allocator.accounting_corrupt = true;
        return;
    }
    --g_allocator.live_blocks;
    if (size > 0) g_allocator.live_bytes -= static_cast<std::uint64_t>(size);
}

void* fault_malloc(int bytes) noexcept {
    if (allocation_should_fail(bytes)) return nullptr;
    void* const memory = g_allocator.base.xMalloc(bytes);
    account_allocation(memory);
    return memory;
}

void fault_free(void* memory) noexcept {
    account_free(memory);
    g_allocator.base.xFree(memory);
}

void* fault_realloc(void* memory, int bytes) noexcept {
    if (allocation_should_fail(bytes)) return nullptr;
    const int old_size = memory != nullptr ? g_allocator.base.xSize(memory) : 0;
    void* const replacement = g_allocator.base.xRealloc(memory, bytes);
    if (replacement == nullptr) return nullptr;
    if (memory == nullptr) {
        account_allocation(replacement);
        return replacement;
    }
    const int new_size = g_allocator.base.xSize(replacement);
    if (old_size > 0 &&
        g_allocator.live_bytes >= static_cast<std::uint64_t>(old_size)) {
        g_allocator.live_bytes -= static_cast<std::uint64_t>(old_size);
    } else if (old_size > 0) {
        g_allocator.accounting_corrupt = true;
    }
    if (new_size > 0) {
        g_allocator.live_bytes += static_cast<std::uint64_t>(new_size);
        g_allocator.peak_live_bytes =
            std::max(g_allocator.peak_live_bytes, g_allocator.live_bytes);
    }
    return replacement;
}

int fault_size(void* memory) noexcept {
    return g_allocator.base.xSize(memory);
}

int fault_roundup(int bytes) noexcept {
    return g_allocator.base.xRoundup(bytes);
}

int fault_init(void*) noexcept {
    return g_allocator.base.xInit != nullptr
               ? g_allocator.base.xInit(g_allocator.base.pAppData)
               : SQLITE_OK;
}

void fault_shutdown(void*) noexcept {
    if (g_allocator.base.xShutdown != nullptr) {
        g_allocator.base.xShutdown(g_allocator.base.pAppData);
    }
}

class FaultAllocatorRuntime final {
public:
    FaultAllocatorRuntime() {
        if (sqlite3_shutdown() != SQLITE_OK) {
            fail("could not place SQLite in pre-initialization state");
        }
        if (sqlite3_config(SQLITE_CONFIG_GETMALLOC, &g_allocator.base) !=
            SQLITE_OK) {
            fail("SQLITE_CONFIG_GETMALLOC was rejected");
        }
        if (g_allocator.base.xMalloc == nullptr ||
            g_allocator.base.xFree == nullptr ||
            g_allocator.base.xRealloc == nullptr ||
            g_allocator.base.xSize == nullptr ||
            g_allocator.base.xRoundup == nullptr) {
            fail("SQLite returned an incomplete base allocator");
        }

        sqlite3_mem_methods overlay = g_allocator.base;
        overlay.xMalloc = fault_malloc;
        overlay.xFree = fault_free;
        overlay.xRealloc = fault_realloc;
        overlay.xSize = fault_size;
        overlay.xRoundup = fault_roundup;
        overlay.xInit = fault_init;
        overlay.xShutdown = fault_shutdown;
        overlay.pAppData = nullptr;
        if (sqlite3_config(SQLITE_CONFIG_MALLOC, &overlay) != SQLITE_OK) {
            fail("SQLITE_CONFIG_MALLOC rejected the fault overlay");
        }
        if (sqlite3_initialize() != SQLITE_OK) {
            fail("SQLite initialization failed with the fault overlay installed");
        }
        g_allocator.configured = true;
    }

    ~FaultAllocatorRuntime() {
        if (!shutdown_) {
            g_allocator.armed = false;
            g_allocator.configured = false;
            (void)sqlite3_shutdown();
        }
    }

    void shutdown_or_throw() {
        if (shutdown_) return;
        g_allocator.armed = false;
        const int rc = sqlite3_shutdown();
        g_allocator.configured = false;
        shutdown_ = true;
        if (rc != SQLITE_OK) fail("SQLite shutdown failed");
        if (g_allocator.accounting_corrupt) {
            fail("SQLite allocator live-block accounting became inconsistent");
        }
        if (g_allocator.live_blocks != 0 || g_allocator.live_bytes != 0) {
            fail("SQLite worker retained overlay allocations after shutdown: blocks=" +
                 std::to_string(g_allocator.live_blocks) + " bytes=" +
                 std::to_string(g_allocator.live_bytes));
        }
    }

    FaultAllocatorRuntime(const FaultAllocatorRuntime&) = delete;
    FaultAllocatorRuntime& operator=(const FaultAllocatorRuntime&) = delete;

private:
    bool shutdown_ = false;
};

struct FaultOutcome final {
    std::uint64_t attempts = 0;
    std::uint64_t failures = 0;
    std::exception_ptr error;
};

template <typename Function>
FaultOutcome run_with_fault(std::uint64_t fail_at,
                            bool sticky,
                            Function&& function) {
    if (!g_allocator.configured || g_allocator.armed) {
        fail("allocator fault boundary was armed in an invalid state");
    }
    g_allocator.attempts = 0;
    g_allocator.failures = 0;
    g_allocator.fail_at = fail_at;
    g_allocator.sticky = sticky;
    g_allocator.armed = true;

    std::exception_ptr error;
    try {
        function();
    } catch (...) {
        error = std::current_exception();
    }

    const FaultOutcome outcome{
        g_allocator.attempts, g_allocator.failures, std::move(error)};
    g_allocator.armed = false;
    g_allocator.fail_at = 0;
    g_allocator.sticky = false;
    return outcome;
}

struct SqliteCloser final {
    void operator()(sqlite3* db) const noexcept {
        if (db == nullptr) return;
        revoke_sync_sqlite_connection_authority_before_close_noexcept(db);
        (void)sqlite3_close_v2(db);
    }
};
using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

SqlitePtr open_memory_database() {
    sqlite3* raw = nullptr;
    const int rc = sqlite3_open_v2(
        ":memory:",
        &raw,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason =
            raw != nullptr ? sqlite3_errmsg(raw) : "unknown SQLite open error";
        if (raw != nullptr) (void)sqlite3_close_v2(raw);
        fail("could not open allocator-fault database: " + reason);
    }
    return SqlitePtr(raw);
}

struct Fixture final {
    SqlitePtr db = open_memory_database();
    SyncSqliteConnectionAuthorityProof authority;

    Fixture() {
        sqlite_exec_or_throw(db.get(),
                             "CREATE TABLE trace_rows(value INTEGER PRIMARY KEY);",
                             "allocator-fault schema");
        authority = install_sync_sqlite_connection_authority_or_throw(
            db.get(), allow_policy, nullptr, "allocator-fault authority");
        if (!authority.valid()) fail("allocator-fault authority is invalid");
    }
};

void insert_row(sqlite3* db, int value) {
    sqlite_exec_or_throw(db,
                         "INSERT INTO trace_rows(value) VALUES(" +
                             std::to_string(value) + ");",
                         "allocator-fault insert");
}

std::vector<int> rows(sqlite3* db) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT value FROM trace_rows ORDER BY value;",
        "allocator-fault row snapshot");
    std::vector<int> result;
    for (;;) {
        const int rc = sqlite3_step(statement.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, "allocator-fault row step");
        }
        result.push_back(sqlite3_column_int(statement.stmt, 0));
    }
    return result;
}

std::string render_rows(const std::vector<int>& values) {
    std::string out = "[";
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) out += ",";
        out += std::to_string(values[index]);
    }
    out += "]";
    return out;
}

void require_rows(sqlite3* db,
                  std::vector<int> expected,
                  const std::string& label,
                  std::uint64_t& checks) {
    const std::vector<int> observed = rows(db);
    require(observed == expected,
            label + " expected " + render_rows(expected) + " but observed " +
                render_rows(observed),
            checks);
}

enum class Scenario {
    TransactionBegin,
    SavepointBegin,
    SavepointRelease,
    SavepointRollback,
    TransactionCommit,
    TransactionRollback
};

constexpr std::array<std::pair<std::string_view, Scenario>, 6> kScenarios{{
    {"transaction-begin", Scenario::TransactionBegin},
    {"savepoint-begin", Scenario::SavepointBegin},
    {"savepoint-release", Scenario::SavepointRelease},
    {"savepoint-rollback", Scenario::SavepointRollback},
    {"transaction-commit", Scenario::TransactionCommit},
    {"transaction-rollback", Scenario::TransactionRollback},
}};

std::optional<Scenario> parse_scenario(std::string_view name) {
    for (const auto& [candidate, scenario] : kScenarios) {
        if (candidate == name) return scenario;
    }
    return std::nullopt;
}

std::string_view scenario_name(Scenario scenario) {
    for (const auto& [name, candidate] : kScenarios) {
        if (candidate == scenario) return name;
    }
    return "unknown";
}

void validate_fault_reached(const FaultOutcome& outcome,
                            std::uint64_t fail_at,
                            std::uint64_t& checks) {
    if (fail_at == 0) return;
    require(outcome.attempts >= fail_at,
            "configured allocation cut was not reached",
            checks);
    require(outcome.failures >= 1,
            "configured allocation cut did not reject an allocation",
            checks);
}

FaultOutcome run_transaction_begin(std::uint64_t fail_at,
                                   bool sticky,
                                   std::uint64_t& checks) {
    Fixture fixture;
    std::unique_ptr<SyncSqliteTransaction> transaction;
    const FaultOutcome outcome = run_with_fault(fail_at, sticky, [&] {
        transaction = std::make_unique<SyncSqliteTransaction>(
            fixture.db.get(), "allocator-fault transaction begin");
    });
    validate_fault_reached(outcome, fail_at, checks);

    if (transaction != nullptr) {
        require(transaction->active(),
                "successful transaction begin did not retain authority",
                checks);
        insert_row(fixture.db.get(), 1);
        transaction->rollback();
    } else {
        require(outcome.error != nullptr,
                "failed transaction construction returned neither guard nor error",
                checks);
        require(sqlite3_get_autocommit(fixture.db.get()) != 0,
                "failed transaction begin orphaned an explicit transaction",
                checks);
        SyncSqliteTransaction retry(
            fixture.db.get(), "allocator-fault transaction begin retry");
        require(retry.active(),
                "transaction begin retry did not recover authority",
                checks);
        insert_row(fixture.db.get(), 2);
        retry.rollback();
    }
    require_rows(fixture.db.get(), {}, "transaction begin recovery", checks);
    return outcome;
}

FaultOutcome run_savepoint_begin(std::uint64_t fail_at,
                                 bool sticky,
                                 std::uint64_t& checks) {
    Fixture fixture;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "allocator-fault savepoint-begin outer");
    insert_row(fixture.db.get(), 1);
    std::unique_ptr<SyncSqliteSavepoint> savepoint;
    const FaultOutcome outcome = run_with_fault(fail_at, sticky, [&] {
        savepoint = std::make_unique<SyncSqliteSavepoint>(
            fixture.db.get(), transaction.authority(),
            "allocator-fault savepoint begin");
    });
    validate_fault_reached(outcome, fail_at, checks);

    if (sqlite3_get_autocommit(fixture.db.get()) != 0) {
        require(savepoint == nullptr && outcome.error != nullptr,
                "savepoint begin auto-rollback returned a live guard",
                checks);
        require(!transaction.active(),
                "savepoint begin auto-rollback retained outer authority",
                checks);
        transaction.rollback();
        require_rows(fixture.db.get(), {},
                     "savepoint begin automatic outer rollback", checks);
        SyncSqliteTransaction next(
            fixture.db.get(), "allocator-fault post-savepoint-begin transaction");
        next.rollback();
        return outcome;
    }

    require(transaction.active(),
            "savepoint begin cut revoked a still-live outer transaction",
            checks);
    if (savepoint != nullptr) {
        require(savepoint->active(),
                "successful savepoint begin did not retain authority",
                checks);
        insert_row(fixture.db.get(), 2);
        savepoint->rollback();
    } else {
        require(outcome.error != nullptr,
                "failed savepoint construction returned neither guard nor error",
                checks);
        SyncSqliteSavepoint retry(
            fixture.db.get(), transaction.authority(),
            "allocator-fault savepoint begin retry");
        insert_row(fixture.db.get(), 3);
        retry.rollback();
    }
    require_rows(fixture.db.get(), {1}, "savepoint begin recovery", checks);
    transaction.rollback();
    require_rows(fixture.db.get(), {}, "savepoint begin outer rollback", checks);
    return outcome;
}

FaultOutcome run_savepoint_release(std::uint64_t fail_at,
                                   bool sticky,
                                   std::uint64_t& checks) {
    Fixture fixture;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "allocator-fault savepoint-release outer");
    insert_row(fixture.db.get(), 1);
    SyncSqliteSavepoint savepoint(
        fixture.db.get(), transaction.authority(),
        "allocator-fault savepoint release");
    insert_row(fixture.db.get(), 2);

    const FaultOutcome outcome =
        run_with_fault(fail_at, sticky, [&] { savepoint.release(); });
    validate_fault_reached(outcome, fail_at, checks);
    if (outcome.error != nullptr &&
        sqlite3_get_autocommit(fixture.db.get()) != 0) {
        require(!savepoint.active(),
                "savepoint release auto-rollback retained mark authority",
                checks);
        require(!transaction.active(),
                "savepoint release auto-rollback retained outer authority",
                checks);
        transaction.rollback();
        require_rows(fixture.db.get(), {},
                     "savepoint release automatic outer rollback", checks);
        SyncSqliteTransaction next(
            fixture.db.get(), "allocator-fault post-savepoint-release transaction");
        next.rollback();
        return outcome;
    }
    if (outcome.error != nullptr) {
        require(savepoint.active(),
                "failed savepoint release permanently revoked a live mark",
                checks);
        savepoint.release();
    }
    require(!savepoint.active(),
            "savepoint release recovery left the mark authoritative",
            checks);
    require(transaction.active(),
            "savepoint release ended or revoked the outer transaction",
            checks);
    transaction.commit();
    require_rows(fixture.db.get(), {1, 2}, "savepoint release commit", checks);
    return outcome;
}

FaultOutcome run_savepoint_rollback(std::uint64_t fail_at,
                                    bool sticky,
                                    std::uint64_t& checks) {
    Fixture fixture;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "allocator-fault savepoint-rollback outer");
    insert_row(fixture.db.get(), 1);
    SyncSqliteSavepoint savepoint(
        fixture.db.get(), transaction.authority(),
        "allocator-fault savepoint rollback");
    insert_row(fixture.db.get(), 2);

    const FaultOutcome outcome =
        run_with_fault(fail_at, sticky, [&] { savepoint.rollback(); });
    validate_fault_reached(outcome, fail_at, checks);
    if (outcome.error != nullptr &&
        sqlite3_get_autocommit(fixture.db.get()) != 0) {
        require(!savepoint.active(),
                "savepoint rollback auto-rollback retained mark authority",
                checks);
        require(!transaction.active(),
                "savepoint rollback auto-rollback retained outer authority",
                checks);
        transaction.rollback();
        require_rows(fixture.db.get(), {},
                     "savepoint rollback automatic outer rollback", checks);
        SyncSqliteTransaction next(
            fixture.db.get(), "allocator-fault post-savepoint-rollback transaction");
        next.rollback();
        return outcome;
    }
    if (outcome.error != nullptr) {
        require(savepoint.active(),
                "failed savepoint rollback permanently revoked a live mark",
                checks);
        // Retry must rewind work added after any successful partial ROLLBACK TO.
        insert_row(fixture.db.get(), 3);
        savepoint.rollback();
    }
    require(!savepoint.active(),
            "savepoint rollback recovery left the mark authoritative",
            checks);
    require_rows(fixture.db.get(), {1}, "savepoint rollback rewind", checks);
    transaction.commit();
    require_rows(fixture.db.get(), {1}, "savepoint rollback commit", checks);
    return outcome;
}

FaultOutcome run_transaction_commit(std::uint64_t fail_at,
                                    bool sticky,
                                    std::uint64_t& checks) {
    Fixture fixture;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "allocator-fault transaction commit");
    insert_row(fixture.db.get(), 1);

    const FaultOutcome outcome =
        run_with_fault(fail_at, sticky, [&] { transaction.commit(); });
    validate_fault_reached(outcome, fail_at, checks);
    if (outcome.error != nullptr && sqlite3_get_autocommit(fixture.db.get()) == 0) {
        require(transaction.active(),
                "failed commit revoked a still-live transaction",
                checks);
        transaction.commit();
    }
    require(sqlite3_get_autocommit(fixture.db.get()) != 0,
            "commit recovery did not restore autocommit",
            checks);
    require(!transaction.active(),
            "commit recovery retained transaction authority",
            checks);
    const std::vector<int> committed = rows(fixture.db.get());
    require(committed.empty() || committed == std::vector<int>{1},
            "failed commit produced an impossible row state " +
                render_rows(committed),
            checks);

    SyncSqliteTransaction next(
        fixture.db.get(), "allocator-fault post-commit transaction");
    insert_row(fixture.db.get(), 2);
    next.rollback();
    require_rows(fixture.db.get(), committed,
                 "post-commit generation isolation", checks);
    return outcome;
}

FaultOutcome run_transaction_rollback(std::uint64_t fail_at,
                                      bool sticky,
                                      std::uint64_t& checks) {
    Fixture fixture;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "allocator-fault transaction rollback");
    insert_row(fixture.db.get(), 1);

    const FaultOutcome outcome =
        run_with_fault(fail_at, sticky, [&] { transaction.rollback(); });
    validate_fault_reached(outcome, fail_at, checks);
    if (outcome.error != nullptr && sqlite3_get_autocommit(fixture.db.get()) == 0) {
        require(transaction.active(),
                "failed rollback revoked a still-live transaction",
                checks);
        transaction.rollback();
    }
    require(sqlite3_get_autocommit(fixture.db.get()) != 0,
            "rollback recovery did not restore autocommit",
            checks);
    require(!transaction.active(),
            "rollback recovery retained transaction authority",
            checks);
    require_rows(fixture.db.get(), {}, "transaction rollback result", checks);

    SyncSqliteTransaction next(
        fixture.db.get(), "allocator-fault post-rollback transaction");
    insert_row(fixture.db.get(), 2);
    next.rollback();
    require_rows(fixture.db.get(), {},
                 "post-rollback generation isolation", checks);
    return outcome;
}

FaultOutcome run_scenario(Scenario scenario,
                          std::uint64_t fail_at,
                          bool sticky,
                          std::uint64_t& checks) {
    switch (scenario) {
        case Scenario::TransactionBegin:
            return run_transaction_begin(fail_at, sticky, checks);
        case Scenario::SavepointBegin:
            return run_savepoint_begin(fail_at, sticky, checks);
        case Scenario::SavepointRelease:
            return run_savepoint_release(fail_at, sticky, checks);
        case Scenario::SavepointRollback:
            return run_savepoint_rollback(fail_at, sticky, checks);
        case Scenario::TransactionCommit:
            return run_transaction_commit(fail_at, sticky, checks);
        case Scenario::TransactionRollback:
            return run_transaction_rollback(fail_at, sticky, checks);
    }
    fail("unknown allocator-fault scenario");
}

std::uint64_t parse_uint64(std::string_view raw, const std::string& label) {
    std::uint64_t value = 0;
    const char* const begin = raw.data();
    const char* const end = raw.data() + raw.size();
    const auto result = std::from_chars(begin, end, value);
    if (result.ec != std::errc{} || result.ptr != end) {
        fail(label + " is not an exact uint64");
    }
    return value;
}

int worker_main(std::string_view scenario_raw,
                std::string_view mode_raw,
                std::string_view fail_at_raw) {
    const std::optional<Scenario> scenario = parse_scenario(scenario_raw);
    if (!scenario.has_value()) fail("unknown worker scenario");
    const bool sticky = mode_raw == "sticky";
    if (!sticky && mode_raw != "oneshot") fail("unknown worker fault mode");
    const std::uint64_t fail_at = parse_uint64(fail_at_raw, "worker fail-at");

    FaultAllocatorRuntime runtime;
    std::uint64_t checks = 0;
    const FaultOutcome outcome =
        run_scenario(*scenario, fail_at, sticky, checks);
    runtime.shutdown_or_throw();
    ++checks;
    std::cout << "scenario=" << scenario_name(*scenario)
              << " mode=" << mode_raw
              << " fail_at=" << fail_at
              << " attempts=" << outcome.attempts
              << " failures=" << outcome.failures
              << " threw=" << (outcome.error != nullptr ? 1 : 0)
              << " checks=" << checks << "\n";
    return 0;
}

#if defined(__linux__)

constexpr std::string_view kWorkerFlag =
    "--anonsync-sqlite-transaction-allocator-fault-worker-v1";
constexpr std::size_t kWorkerCaptureBytesPerStream = 16U * 1024U;
constexpr auto kWorkerTimeout = 5s;

anonsync::test::SelfExecTestProcessOutput run_worker_process(
    const std::filesystem::path& executable,
    std::string_view scenario,
    std::string_view mode,
    std::uint64_t fail_at) {
    auto child =
        anonsync::test::spawn_self_exec_test_process_with_output_capture_or_throw(
            executable,
            {std::string(kWorkerFlag), std::string(scenario), std::string(mode),
             std::to_string(fail_at)});
    const std::string label =
        "allocator worker " + std::string(scenario) + " " +
        std::string(mode) + " cut " + std::to_string(fail_at);
    anonsync::test::SelfExecTestProcessOutput output =
        child.wait_for_exact_exit_with_output(
            0, kWorkerTimeout, kWorkerCaptureBytesPerStream, label);
    if (!output.standard_error.empty()) {
        fail(label + " wrote unexpected stderr: " + output.standard_error);
    }
    return output;
}

std::uint64_t parse_output_field(const std::string& output,
                                 std::string_view field) {
    const std::string needle = std::string(field) + "=";
    const std::size_t start = output.find(needle);
    if (start == std::string::npos) {
        fail("worker output omitted " + std::string(field) + ": " + output);
    }
    const std::size_t value_start = start + needle.size();
    const std::size_t value_end = output.find_first_of(" \r\n", value_start);
    return parse_uint64(
        std::string_view(output).substr(value_start, value_end - value_start),
        "worker output field " + std::string(field));
}

int parent_main() {
    const std::filesystem::path executable =
        anonsync::test::current_self_executable_or_throw();
    std::uint64_t checks = 0;
    std::uint64_t workers = 0;
    std::uint64_t cutpoints = 0;

    for (const auto& [name, scenario] : kScenarios) {
        (void)scenario;
        const anonsync::test::SelfExecTestProcessOutput baseline =
            run_worker_process(executable, name, "oneshot", 0);
        ++workers;
        ++checks;
        const std::uint64_t attempts =
            parse_output_field(baseline.standard_output, "attempts");
        require(attempts > 0,
                "baseline worker reached no SQLite allocation boundary for " +
                    std::string(name),
                checks);
        require(attempts <= 512,
                "allocator cut frontier exceeded the reviewed bound for " +
                    std::string(name),
                checks);

        for (std::uint64_t cut = 1; cut <= attempts; ++cut) {
            for (std::string_view mode : {std::string_view("oneshot"),
                                          std::string_view("sticky")}) {
                const anonsync::test::SelfExecTestProcessOutput result =
                    run_worker_process(executable, name, mode, cut);
                ++workers;
                ++cutpoints;
                ++checks;
                require(
                    parse_output_field(result.standard_output, "failures") >= 1,
                    "allocator worker did not fire configured cut for " +
                        std::string(name) + " " + std::string(mode) +
                        " cut " + std::to_string(cut),
                    checks);
            }
        }
    }

    std::cout << "PASS: SQLite transaction allocator-fault campaign "
              << checks << " checks, " << workers << " isolated workers, "
              << cutpoints << " injected cutpoints\n";
    return 0;
}

#else

int parent_main() {
    std::cout << "SKIP: allocator-fault process campaign requires Linux\n";
    return 0;
}

#endif

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc >= 2 && std::string_view(argv[1]) == kWorkerFlag) {
            anonsync::test::verify_self_exec_child_boundary_or_throw();
            if (argc != 5) fail("invalid allocator-fault worker instruction");
            return worker_main(argv[2], argv[3], argv[4]);
        }
        if (argc != 1) fail("unexpected allocator-fault test arguments");
        return parent_main();
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << "\n";
        return 1;
    } catch (...) {
        std::cerr << "FAIL: non-standard exception\n";
        return 1;
    }
}
