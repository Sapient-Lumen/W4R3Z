#include "sqlite_live_backup.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::persistence::SqliteLiveBackupEvidence;
using anonsync::persistence::SqliteLiveBackupStepObservation;
using anonsync::persistence::SqliteSnapshotGeometryPolicy;
using anonsync::persistence::copy_sqlite_live_snapshot_bounded_or_throw;
using anonsync::persistence::kSqliteLiveBackupPagesPerStep;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {"", "-wal", "-shm", "-journal"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

class Database final {
public:
    Database(const fs::path& path, int flags) {
        if (sqlite3_open_v2(path.c_str(), &database_, flags, nullptr) != SQLITE_OK) {
            const std::string reason = database_ != nullptr
                                           ? sqlite3_errmsg(database_)
                                           : "SQLite open failed";
            if (database_ != nullptr) (void)sqlite3_close_v2(database_);
            database_ = nullptr;
            throw std::runtime_error(reason);
        }
        if (sqlite3_busy_timeout(database_, 2000) != SQLITE_OK) {
            throw std::runtime_error("could not install SQLite busy timeout");
        }
    }

    ~Database() {
        if (database_ != nullptr) (void)sqlite3_close_v2(database_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    sqlite3* get() const noexcept { return database_; }

    void exec(const std::string& sql) const {
        char* error = nullptr;
        const int rc = sqlite3_exec(database_, sql.c_str(), nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            const std::string reason =
                error != nullptr ? error : sqlite3_errmsg(database_);
            sqlite3_free(error);
            throw std::runtime_error(reason);
        }
    }

    std::uint64_t integer(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int step_rc = sqlite3_step(statement);
        if (step_rc != SQLITE_ROW ||
            sqlite3_column_type(statement, 0) != SQLITE_INTEGER) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned no exact integer row");
        }
        const sqlite3_int64 signed_value = sqlite3_column_int64(statement, 0);
        if (signed_value < 0) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned a negative value");
        }
        const std::uint64_t value = static_cast<std::uint64_t>(signed_value);
        if (sqlite3_step(statement) != SQLITE_DONE) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned multiple rows");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            throw std::runtime_error("integer query finalize failed");
        }
        return value;
    }

private:
    sqlite3* database_ = nullptr;
};

Database open_private_memory_database() {
    return Database(
        ":memory:", SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE |
                        SQLITE_OPEN_MEMORY);
}

void initialize_wal_source(Database& source, std::uint64_t initial_blob_bytes) {
    source.exec("PRAGMA journal_mode=WAL;");
    source.exec("PRAGMA wal_autocheckpoint=0;");
    source.exec("CREATE TABLE evidence(id INTEGER PRIMARY KEY, payload BLOB NOT NULL);");
    source.exec("INSERT INTO evidence(payload) VALUES(zeroblob(" +
                std::to_string(initial_blob_bytes) + "));" );
}

struct ObservationCollector {
    std::vector<SqliteLiveBackupStepObservation> observations;
};

void collect_observation(const SqliteLiveBackupStepObservation& observation,
                         void* context) {
    auto& collector = *static_cast<ObservationCollector*>(context);
    collector.observations.push_back(observation);
}

struct GrowthContext {
    Database* writer = nullptr;
    std::uint64_t growth_bytes = 0;
    bool committed = false;
    std::vector<SqliteLiveBackupStepObservation> observations;
};

void grow_after_first_step(const SqliteLiveBackupStepObservation& observation,
                           void* context) {
    auto& state = *static_cast<GrowthContext*>(context);
    state.observations.push_back(observation);
    if (observation.step_index != 1U || state.committed) return;
    state.writer->exec("BEGIN IMMEDIATE;");
    state.writer->exec("INSERT INTO evidence(payload) VALUES(zeroblob(" +
                       std::to_string(state.growth_bytes) + "));" );
    state.writer->exec("COMMIT;");
    state.committed = true;
}

struct LostPinContext {
    sqlite3* source = nullptr;
    Database* writer = nullptr;
    bool transaction_removed = false;
};

void remove_pin_after_first_step(const SqliteLiveBackupStepObservation& observation,
                                 void* context) {
    auto& state = *static_cast<LostPinContext*>(context);
    if (observation.step_index != 1U || state.transaction_removed) return;
    char* error = nullptr;
    const int rollback_rc =
        sqlite3_exec(state.source, "ROLLBACK;", nullptr, nullptr, &error);
    const std::string reason = error != nullptr ? error : "rollback failed";
    sqlite3_free(error);
    if (rollback_rc != SQLITE_OK) throw std::runtime_error(reason);
    state.writer->exec(
        "INSERT INTO evidence(payload) VALUES(zeroblob(4194304));");
    state.transaction_removed = true;
}

template <typename Callable>
void expect_rejection(Callable&& callable,
                      std::string_view expected_fragment,
                      std::uint64_t& checks) {
    bool rejected = false;
    try {
        callable();
    } catch (const std::exception& error) {
        rejected = std::string(error.what()).find(expected_fragment) !=
                   std::string::npos;
        if (!rejected) {
            throw std::runtime_error(
                "unexpected rejection text: " + std::string(error.what()));
        }
    }
    require(rejected,
            "expected rejection containing: " + std::string(expected_fragment),
            checks);
}

void test_fixed_step_copy(const fs::path& root, std::uint64_t& checks) {
    const fs::path source_path = root / "fixed-step.sqlite";
    cleanup_sqlite_family(source_path);
    Database source(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                         SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE);
    initialize_wal_source(source, 900000U);
    Database destination = open_private_memory_database();
    ObservationCollector collector;

    const SqliteLiveBackupEvidence evidence =
        copy_sqlite_live_snapshot_bounded_or_throw(
            destination.get(), source.get(), "fixed-step live backup",
            {}, &collect_observation, &collector);

    require(evidence.step_calls == collector.observations.size() &&
                evidence.step_calls > 1U,
            "bounded backup did not expose multiple fixed-size steps", checks);
    require(evidence.source_geometry.page_count >
                kSqliteLiveBackupPagesPerStep,
            "fixed-step fixture did not exceed one page batch", checks);
    require(evidence.maximum_reported_page_count ==
                evidence.source_geometry.page_count,
            "bounded backup page-count evidence drifted", checks);
    require(sqlite3_get_autocommit(source.get()) != 0 &&
                sqlite3_txn_state(source.get(), "main") == SQLITE_TXN_NONE,
            "bounded backup retained its source read transaction", checks);
    require(destination.integer("SELECT count(*) FROM evidence;") == 1U,
            "bounded backup did not copy the source row", checks);

    std::uint64_t previous_remaining =
        evidence.source_geometry.page_count + 1U;
    for (const auto& observation : collector.observations) {
        require(observation.requested_pages == kSqliteLiveBackupPagesPerStep,
                "bounded backup changed its per-step page request", checks);
        require(observation.reported_page_count ==
                    evidence.source_geometry.page_count,
                "bounded backup reported a changing source page count", checks);
        require(observation.reported_remaining_pages < previous_remaining,
                "bounded backup observations were not monotone", checks);
        previous_remaining = observation.reported_remaining_pages;
    }
    require(collector.observations.back().sqlite_result == SQLITE_DONE &&
                collector.observations.back().reported_remaining_pages == 0U,
            "bounded backup did not end with exact zero remaining pages", checks);
}

void test_concurrent_growth_is_outside_pinned_snapshot(const fs::path& root,
                                                       std::uint64_t& checks) {
    const fs::path source_path = root / "concurrent-growth.sqlite";
    cleanup_sqlite_family(source_path);
    Database source(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                         SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE);
    initialize_wal_source(source, 900000U);
    Database writer(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                         SQLITE_OPEN_PRIVATECACHE);
    writer.exec("PRAGMA journal_mode=WAL;");
    writer.exec("PRAGMA wal_autocheckpoint=0;");

    const std::uint64_t page_size = source.integer("PRAGMA main.page_size;");
    const std::uint64_t initial_pages = source.integer("PRAGMA main.page_count;");
    require(initial_pages > kSqliteLiveBackupPagesPerStep,
            "concurrent-growth fixture did not require multiple steps", checks);

    SqliteSnapshotGeometryPolicy exact_initial_policy;
    exact_initial_policy.maximum_pages = initial_pages;
    exact_initial_policy.maximum_bytes = page_size * initial_pages;

    Database destination = open_private_memory_database();
    GrowthContext growth{&writer, 8U * 1024U * 1024U, false, {}};
    const SqliteLiveBackupEvidence evidence =
        copy_sqlite_live_snapshot_bounded_or_throw(
            destination.get(), source.get(), "concurrent-growth live backup",
            exact_initial_policy, &grow_after_first_step, &growth);

    require(growth.committed,
            "concurrent writer did not commit at the first exact cutpoint", checks);
    require(writer.integer("PRAGMA main.page_count;") > initial_pages,
            "concurrent writer did not grow the durable source beyond policy", checks);
    require(source.integer("SELECT count(*) FROM evidence;") == 2U,
            "source did not observe the concurrent commit after snapshot release", checks);
    require(destination.integer("SELECT count(*) FROM evidence;") == 1U,
            "resident destination followed a commit outside the pinned snapshot", checks);
    require(evidence.source_geometry.page_count == initial_pages &&
                evidence.maximum_reported_page_count == initial_pages,
            "bounded backup authorized post-pin source growth", checks);
    require(growth.observations.size() == evidence.step_calls &&
                evidence.step_calls > 1U,
            "concurrent-growth oracle did not traverse multiple backup steps", checks);
}

void test_lost_pin_fails_before_next_copy(const fs::path& root,
                                          std::uint64_t& checks) {
    const fs::path source_path = root / "lost-pin.sqlite";
    cleanup_sqlite_family(source_path);
    Database source(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                         SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE);
    initialize_wal_source(source, 900000U);
    Database writer(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                         SQLITE_OPEN_PRIVATECACHE);
    writer.exec("PRAGMA journal_mode=WAL;");
    Database destination = open_private_memory_database();
    LostPinContext context{source.get(), &writer, false};

    expect_rejection(
        [&] {
            (void)copy_sqlite_live_snapshot_bounded_or_throw(
                destination.get(), source.get(), "lost-pin live backup", {},
                &remove_pin_after_first_step, &context);
        },
        "lost its pinned source read transaction", checks);
    require(context.transaction_removed,
            "lost-pin cutpoint did not remove the source transaction", checks);
    require(sqlite3_get_autocommit(source.get()) != 0 &&
                sqlite3_txn_state(source.get(), "main") == SQLITE_TXN_NONE,
            "lost-pin rejection left source transaction authority active", checks);
    require(destination.integer("PRAGMA main.page_count;") == 0U,
            "aborted live backup retained a partial destination image", checks);
}

void test_destination_and_source_preconditions(const fs::path& root,
                                               std::uint64_t& checks) {
    const fs::path source_path = root / "preconditions-source.sqlite";
    const fs::path named_destination_path = root / "named-destination.sqlite";
    cleanup_sqlite_family(source_path);
    cleanup_sqlite_family(named_destination_path);
    Database source(
        source_path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                         SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE);
    initialize_wal_source(source, 65536U);
    Database named_destination(
        named_destination_path,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX |
            SQLITE_OPEN_PRIVATECACHE);
    expect_rejection(
        [&] {
            (void)copy_sqlite_live_snapshot_bounded_or_throw(
                named_destination.get(), source.get(),
                "named-destination live backup");
        },
        "not private in-memory state", checks);

    Database private_destination = open_private_memory_database();
    source.exec("BEGIN;");
    expect_rejection(
        [&] {
            (void)copy_sqlite_live_snapshot_bounded_or_throw(
                private_destination.get(), source.get(),
                "active-source-transaction live backup");
        },
        "source database has an active transaction", checks);
    source.exec("ROLLBACK;");

    sqlite3_stmt* active_read = nullptr;
    if (sqlite3_prepare_v2(source.get(), "SELECT payload FROM evidence;", -1,
                           &active_read, nullptr) != SQLITE_OK ||
        sqlite3_step(active_read) != SQLITE_ROW) {
        if (active_read != nullptr) (void)sqlite3_finalize(active_read);
        throw std::runtime_error(
            "could not establish active implicit source transaction fixture");
    }
    require(sqlite3_get_autocommit(source.get()) != 0 &&
                sqlite3_txn_state(source.get(), "main") == SQLITE_TXN_READ,
            "active statement did not expose an implicit read transaction",
            checks);
    expect_rejection(
        [&] {
            (void)copy_sqlite_live_snapshot_bounded_or_throw(
                private_destination.get(), source.get(),
                "implicit-source-transaction live backup");
        },
        "source database has an active implicit transaction", checks);
    if (sqlite3_finalize(active_read) != SQLITE_OK) {
        throw std::runtime_error(
            "active implicit source transaction finalize failed");
    }
    require(sqlite3_txn_state(source.get(), "main") == SQLITE_TXN_NONE,
            "implicit source transaction remained after statement finalize",
            checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root =
        fs::path("/tmp") /
        ("anonsync_rev0823_sqlite_live_backup_" +
         std::to_string(static_cast<long long>(::getpid())));
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directory(root);
    try {
        test_fixed_step_copy(root, checks);
        test_concurrent_growth_is_outside_pinned_snapshot(root, checks);
        test_lost_pin_fails_before_next_copy(root, checks);
        test_destination_and_source_preconditions(root, checks);
        fs::remove_all(root, ignored);
        std::cout << "anonsync sqlite live backup tests checks=" << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        fs::remove_all(root, ignored);
        std::cerr << "anonsync sqlite live backup test failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}
