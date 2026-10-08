#include "sqlite_live_backup.hpp"

#include "sqlite_exact_value.hpp"
#include "sync_process_incarnation.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <exception>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync::persistence {
namespace {

std::string sqlite_error_text(sqlite3* database) {
    return database != nullptr ? sqlite3_errmsg(database)
                               : "SQLite database handle is null";
}

void sqlite_exec_or_throw(sqlite3* database,
                          const char* sql,
                          const std::string& label) {
    char* error = nullptr;
    const int rc = sqlite3_exec(database, sql, nullptr, nullptr, &error);
    if (rc == SQLITE_OK) return;
    const std::string message =
        error != nullptr ? error : sqlite_error_text(database);
    sqlite3_free(error);
    throw std::runtime_error(label + ": " + message);
}

class ScopedStatement final {
public:
    ScopedStatement(sqlite3* database,
                    const char* sql,
                    const std::string& label)
        : database_(database), label_(label) {
        if (database_ == nullptr ||
            sqlite3_prepare_v2(database_, sql, -1, &statement_, nullptr) !=
                SQLITE_OK) {
            throw std::runtime_error(label_ + ": " + sqlite_error_text(database_));
        }
    }

    ~ScopedStatement() {
        if (statement_ != nullptr) (void)sqlite3_finalize(statement_);
    }

    ScopedStatement(const ScopedStatement&) = delete;
    ScopedStatement& operator=(const ScopedStatement&) = delete;

    sqlite3_stmt* get() const noexcept { return statement_; }

    void finalize_or_throw() {
        if (statement_ == nullptr) return;
        sqlite3_stmt* const owned = std::exchange(statement_, nullptr);
        const int rc = sqlite3_finalize(owned);
        if (rc != SQLITE_OK) {
            throw std::runtime_error(label_ + " finalize failed: " +
                                     sqlite_error_text(database_));
        }
    }

private:
    sqlite3* database_ = nullptr;
    sqlite3_stmt* statement_ = nullptr;
    std::string label_;
};

std::uint64_t sqlite_query_exact_u64_or_throw(sqlite3* database,
                                              const char* sql,
                                              const std::string& label) {
    ScopedStatement statement(database, sql, label + " prepare failed");
    if (sqlite3_step(statement.get()) != SQLITE_ROW) {
        throw std::runtime_error(label + " query failed: " +
                                 sqlite_error_text(database));
    }
    const std::uint64_t value = sqlite_exact_u64_or_throw(
        statement.get(), 0, label + " exact integer projection");
    if (sqlite3_step(statement.get()) != SQLITE_DONE) {
        throw std::runtime_error(label + " returned more than one row");
    }
    statement.finalize_or_throw();
    return value;
}

std::string exception_text(std::exception_ptr failure) {
    if (failure == nullptr) return "unknown failure";
    try {
        std::rethrow_exception(failure);
    } catch (const std::exception& error) {
        return error.what();
    } catch (...) {
        return "non-standard exception";
    }
}

[[noreturn]] void rethrow_with_cleanup_failure(
    const std::string& label,
    std::exception_ptr original,
    const std::string& cleanup_failure) {
    throw std::runtime_error(label + " failed: " + exception_text(original) +
                             "; cleanup failed: " + cleanup_failure);
}

void verify_private_empty_destination_or_throw(sqlite3* destination,
                                               const std::string& label) {
    if (destination == nullptr) {
        throw std::runtime_error(label + " destination database handle is null");
    }
    if (sqlite3_db_mutex(destination) == nullptr) {
        throw std::runtime_error(
            label + " destination database lacks full-mutex protection");
    }
    if (sqlite3_get_autocommit(destination) == 0) {
        throw std::runtime_error(
            label + " destination database has an active transaction");
    }
    if (sqlite3_txn_state(destination, "main") != SQLITE_TXN_NONE) {
        throw std::runtime_error(
            label + " destination database has an active implicit transaction");
    }
    const char* const filename = sqlite3_db_filename(destination, "main");
    if (filename != nullptr && filename[0] != '\0') {
        throw std::runtime_error(
            label + " destination database is not private in-memory state");
    }
    if (sqlite_query_exact_u64_or_throw(
            destination, "PRAGMA main.page_count;",
            label + " destination page-count preflight") != 0U) {
        throw std::runtime_error(
            label + " destination database is not empty");
    }
    if (sqlite3_txn_state(destination, "main") != SQLITE_TXN_NONE) {
        throw std::runtime_error(
            label + " destination preflight retained transaction authority");
    }
}

void verify_pinned_source_or_throw(sqlite3* source,
                                   const std::string& label) {
    if (sqlite3_get_autocommit(source) != 0 ||
        sqlite3_txn_state(source, "main") != SQLITE_TXN_READ) {
        throw std::runtime_error(
            label + " lost its pinned source read transaction");
    }
}

struct CleanupResult {
    int backup_finish_rc = SQLITE_OK;
    int source_rollback_rc = SQLITE_OK;
};

CleanupResult cleanup_after_failure(
    sqlite3_backup*& backup,
    sqlite3* source,
    bool& source_transaction_active) noexcept {
    CleanupResult result;
    if (backup != nullptr) {
        result.backup_finish_rc = sqlite3_backup_finish(backup);
        backup = nullptr;
    }
    if (source_transaction_active) {
        if (source != nullptr && sqlite3_get_autocommit(source) != 0) {
            source_transaction_active = false;
        } else {
            result.source_rollback_rc =
                sqlite3_exec(source, "ROLLBACK;", nullptr, nullptr, nullptr);
            source_transaction_active = false;
        }
    }
    return result;
}

std::string cleanup_failure_text(const CleanupResult& result) {
    std::string failure;
    if (result.backup_finish_rc != SQLITE_OK) {
        failure = "sqlite3_backup_finish returned " +
                  std::to_string(result.backup_finish_rc);
    }
    if (result.source_rollback_rc != SQLITE_OK) {
        if (!failure.empty()) failure += "; ";
        failure += "source rollback returned " +
                   std::to_string(result.source_rollback_rc);
    }
    return failure;
}

}  // namespace

SqliteLiveBackupEvidence copy_sqlite_live_snapshot_bounded_or_throw(
    sqlite3* destination_database,
    sqlite3* source_database,
    const std::string& label,
    const SqliteSnapshotGeometryPolicy& policy,
    SqliteLiveBackupStepObserver observer,
    void* observer_context) {
    if (label.empty()) {
        throw std::runtime_error(
            "SQLite live backup requires a nonempty diagnostic label");
    }
    validate_sqlite_snapshot_geometry_policy_or_throw(policy, label);
    if (source_database == nullptr) {
        throw std::runtime_error(label + " source database handle is null");
    }
    if (source_database == destination_database) {
        throw std::runtime_error(
            label + " source and destination database handles alias");
    }
    if (sqlite3_db_mutex(source_database) == nullptr) {
        throw std::runtime_error(
            label + " source database lacks full-mutex protection");
    }
    if (sqlite3_get_autocommit(source_database) == 0) {
        throw std::runtime_error(
            label + " source database has an active transaction");
    }
    if (sqlite3_txn_state(source_database, "main") != SQLITE_TXN_NONE) {
        throw std::runtime_error(
            label + " source database has an active implicit transaction");
    }
    verify_private_empty_destination_or_throw(destination_database, label);

    const anonsync::SyncProcessIncarnation process_id =
        anonsync::current_sync_process_incarnation_noexcept();
    bool source_transaction_active = false;
    sqlite3_backup* backup = nullptr;
    try {
        sqlite_exec_or_throw(source_database, "BEGIN;",
                             label + " source read transaction begin failed");
        source_transaction_active = true;

        // These reads establish the deferred transaction's exact main-database
        // snapshot before backup_init. External WAL writers may continue, but
        // their later commits cannot enlarge this pinned image.
        const std::uint64_t page_size = sqlite_query_exact_u64_or_throw(
            source_database, "PRAGMA main.page_size;",
            label + " pinned source page-size");
        const std::uint64_t page_count = sqlite_query_exact_u64_or_throw(
            source_database, "PRAGMA main.page_count;",
            label + " pinned source page-count");
        verify_pinned_source_or_throw(source_database, label);

        SqliteLiveBackupEvidence evidence;
        evidence.source_geometry =
            verify_sqlite_snapshot_page_geometry_or_throw(
                page_size, page_count, label + " pinned source geometry", policy);

        backup = sqlite3_backup_init(destination_database, "main",
                                     source_database, "main");
        if (backup == nullptr) {
            throw std::runtime_error(label + " online backup initialization failed: " +
                                     sqlite_error_text(destination_database));
        }

        const std::uint64_t expected_page_count =
            evidence.source_geometry.page_count;
        const std::uint64_t maximum_step_calls =
            (expected_page_count + kSqliteLiveBackupPagesPerStep - 1U) /
                kSqliteLiveBackupPagesPerStep +
            1U;
        std::uint64_t previous_remaining = expected_page_count + 1U;

        for (std::uint64_t step_index = 1U;
             step_index <= maximum_step_calls; ++step_index) {
            anonsync::require_sync_process_incarnation_or_fail_stop(
                process_id, label + " live-backup step");
            verify_pinned_source_or_throw(source_database, label);

            const int step_rc = sqlite3_backup_step(
                backup, static_cast<int>(kSqliteLiveBackupPagesPerStep));
            const int reported_page_count = sqlite3_backup_pagecount(backup);
            const int reported_remaining = sqlite3_backup_remaining(backup);
            if (reported_page_count < 0 || reported_remaining < 0) {
                throw std::runtime_error(
                    label + " online backup reported negative page evidence");
            }

            const std::uint64_t observed_page_count =
                static_cast<std::uint64_t>(reported_page_count);
            const std::uint64_t observed_remaining =
                static_cast<std::uint64_t>(reported_remaining);
            evidence.step_calls = step_index;
            evidence.maximum_reported_page_count =
                std::max(evidence.maximum_reported_page_count,
                         observed_page_count);
            evidence.maximum_reported_remaining_pages =
                std::max(evidence.maximum_reported_remaining_pages,
                         observed_remaining);

            if (observed_page_count != expected_page_count) {
                throw std::runtime_error(
                    label + " online backup source page count changed outside the pinned snapshot");
            }
            if (observed_remaining > observed_page_count) {
                throw std::runtime_error(
                    label + " online backup remaining pages exceed source pages");
            }
            if (observed_remaining >= previous_remaining) {
                throw std::runtime_error(
                    label + " online backup stopped making monotone progress");
            }

            const SqliteLiveBackupStepObservation observation{
                step_index,
                kSqliteLiveBackupPagesPerStep,
                step_rc,
                observed_page_count,
                observed_remaining,
            };
            if (observer != nullptr) observer(observation, observer_context);
            verify_pinned_source_or_throw(source_database, label);

            if (step_rc == SQLITE_DONE) {
                if (observed_remaining != 0U) {
                    throw std::runtime_error(
                        label + " online backup completed with remaining pages");
                }
                const int finish_rc = sqlite3_backup_finish(backup);
                backup = nullptr;
                if (finish_rc != SQLITE_OK) {
                    throw std::runtime_error(
                        label + " online backup finish failed with SQLite result " +
                        std::to_string(finish_rc));
                }
                const SqliteSnapshotGeometry destination_geometry =
                    verify_sqlite_snapshot_page_geometry_or_throw(
                        sqlite_query_exact_u64_or_throw(
                            destination_database, "PRAGMA main.page_size;",
                            label + " completed destination page-size"),
                        sqlite_query_exact_u64_or_throw(
                            destination_database, "PRAGMA main.page_count;",
                            label + " completed destination page-count"),
                        label + " completed destination geometry", policy);
                if (destination_geometry != evidence.source_geometry) {
                    throw std::runtime_error(
                        label + " completed destination geometry differs from the pinned source");
                }
                sqlite_exec_or_throw(
                    source_database, "ROLLBACK;",
                    label + " source read transaction release failed");
                source_transaction_active = false;
                if (sqlite3_get_autocommit(source_database) == 0 ||
                    sqlite3_txn_state(source_database, "main") !=
                        SQLITE_TXN_NONE) {
                    throw std::runtime_error(
                        label + " source read transaction remained active after release");
                }
                return evidence;
            }
            if (step_rc != SQLITE_OK) {
                throw std::runtime_error(
                    label + " online backup step failed with SQLite result " +
                    std::to_string(step_rc) + ": " +
                    sqlite3_errstr(step_rc));
            }
            previous_remaining = observed_remaining;
        }

        throw std::runtime_error(
            label + " online backup exceeded its derived step ceiling");
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        const CleanupResult cleanup_result = cleanup_after_failure(
            backup, source_database, source_transaction_active);
        const std::string cleanup_failure =
            cleanup_failure_text(cleanup_result);
        if (!cleanup_failure.empty()) {
            rethrow_with_cleanup_failure(label, original, cleanup_failure);
        }
        std::rethrow_exception(original);
    }
}

}  // namespace anonsync::persistence
