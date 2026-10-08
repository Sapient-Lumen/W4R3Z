#include "sqlite_verification_budget.hpp"

#include "sqlite_retained_callback_slots.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <limits>
#include <utility>

namespace anonsync::persistence {
namespace {

std::uint64_t saturating_multiply(std::uint64_t left,
                                  std::uint64_t right) noexcept {
    if (left == 0U || right == 0U) return 0U;
    if (left > std::numeric_limits<std::uint64_t>::max() / right) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return left * right;
}

std::uint64_t clamp_budget(std::uint64_t value,
                           std::uint64_t minimum,
                           std::uint64_t maximum) noexcept {
    return std::min(std::max(value, minimum), maximum);
}

void validate_policy_or_throw(const SqliteVerificationBudgetPolicy& policy) {
    if (policy.maximum_progress_callbacks == 0U ||
        policy.progress_opcode_interval == 0U ||
        policy.maximum_rows == 0U ||
        policy.maximum_decoded_text_bytes == 0U ||
        policy.maximum_retained_text_bytes == 0U ||
        policy.maximum_elapsed_milliseconds == 0U) {
        throw std::runtime_error(
            "SQLite verification budget policy has a zero ceiling");
    }
    if (policy.maximum_progress_callbacks >
            kMaximumSqliteVerificationProgressCallbacks ||
        policy.progress_opcode_interval >
            kMaximumSqliteVerificationProgressOpcodeInterval ||
        policy.maximum_rows > kMaximumSqliteVerificationRows ||
        policy.maximum_decoded_text_bytes >
            kMaximumSqliteVerificationDecodedTextBytes ||
        policy.maximum_retained_text_bytes >
            kMaximumSqliteVerificationRetainedTextBytes ||
        policy.maximum_elapsed_milliseconds >
            kMaximumSqliteVerificationElapsedMilliseconds) {
        throw std::runtime_error(
            "SQLite verification budget policy may tighten but not widen reviewed ceilings");
    }
    if (policy.progress_opcode_interval >
        static_cast<std::uint32_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error(
            "SQLite verification progress interval exceeds SQLite integer range");
    }
}

std::string exception_message(std::string label,
                              SqliteVerificationBudgetFailure failure,
                              std::uint64_t observed,
                              std::uint64_t limit) {
    if (label.empty()) label = "SQLite verification";
    return std::move(label) + ": sqlite_verification_budget[" +
           std::string(sqlite_verification_budget_failure_name(failure)) +
           "]:observed=" + std::to_string(observed) +
           ":limit=" + std::to_string(limit);
}

}  // namespace

SqliteVerificationBudgetPolicy sqlite_verification_budget_for_snapshot(
    std::uint64_t exact_file_bytes,
    std::uint64_t page_count) {
    if (exact_file_bytes == 0U || page_count == 0U) {
        throw std::runtime_error(
            "SQLite verification budget derivation requires nonzero verified geometry");
    }

    SqliteVerificationBudgetPolicy policy;
    policy.maximum_progress_callbacks = clamp_budget(
        saturating_multiply(page_count, 64U), 10'000U,
        kMaximumSqliteVerificationProgressCallbacks);
    policy.maximum_rows = clamp_budget(
        saturating_multiply(page_count, 32U), 1'024U,
        kMaximumSqliteVerificationRows);
    policy.maximum_decoded_text_bytes = clamp_budget(
        saturating_multiply(exact_file_bytes, 4U), 4ULL * 1024ULL * 1024ULL,
        kMaximumSqliteVerificationDecodedTextBytes);
    policy.maximum_retained_text_bytes = clamp_budget(
        exact_file_bytes, 1ULL * 1024ULL * 1024ULL,
        kMaximumSqliteVerificationRetainedTextBytes);
    return policy;
}

std::string_view sqlite_verification_budget_failure_name(
    SqliteVerificationBudgetFailure failure) noexcept {
    switch (failure) {
        case SqliteVerificationBudgetFailure::none:
            return "none";
        case SqliteVerificationBudgetFailure::progress_callback_limit:
            return "progress_callback_limit";
        case SqliteVerificationBudgetFailure::elapsed_time_limit:
            return "elapsed_time_limit";
        case SqliteVerificationBudgetFailure::row_limit:
            return "row_limit";
        case SqliteVerificationBudgetFailure::decoded_text_byte_limit:
            return "decoded_text_byte_limit";
        case SqliteVerificationBudgetFailure::retained_text_byte_limit:
            return "retained_text_byte_limit";
    }
    return "unknown_failure";
}

SqliteVerificationBudgetException::SqliteVerificationBudgetException(
    std::string label,
    SqliteVerificationBudgetFailure failure,
    std::uint64_t observed,
    std::uint64_t limit)
    : std::runtime_error(
          exception_message(std::move(label), failure, observed, limit)),
      failure_(failure),
      observed_(observed),
      limit_(limit) {}

SqliteVerificationBudget::SqliteVerificationBudget(
    SyncSqliteSerializedDbBorrow database_borrow,
    std::string label,
    const SqliteVerificationBudgetPolicy& policy)
    : process_id_(current_sync_process_incarnation_noexcept()),
      thread_id_(current_sync_thread_incarnation_noexcept()),
      database_borrow_(std::move(database_borrow)),
      label_(std::move(label)),
      policy_(policy),
      started_(std::chrono::steady_clock::now()) {
    sqlite3* const database = database_borrow_.get();
    if (database == nullptr) {
        throw std::runtime_error(
            "SQLite verification budget requires an exact serialized database-generation borrow");
    }
    if (label_.empty()) {
        throw std::runtime_error(
            "SQLite verification budget requires a nonempty diagnostic label");
    }
    validate_policy_or_throw(policy_);

    // Claim publication and progress-handler installation are one serialized
    // slot transition. This converts concurrent duplicate attachment into one
    // winner and one ordinary claim rejection instead of allowing a later
    // set_clientdata() call to destroy another constructor's live sentinel.
    SyncSqliteDatabaseMutexGuard mutation_guard(
        database, label_ + " verification-progress slot attachment");
    callback_claim_.attach(database,
                           mutation_guard,
                           kSqliteVerificationBudgetClientDataName,
                           label_,
                           "verification-budget owner");
    sqlite3_progress_handler(
        database, static_cast<int>(policy_.progress_opcode_interval),
        &SqliteVerificationBudget::progress_callback, this);
}

SqliteVerificationBudget::~SqliteVerificationBudget() { detach(); }

void SqliteVerificationBudget::consume_row() {
    require_current_execution_or_throw();
    check_elapsed_or_throw();
    consume_or_throw(1U, rows_, policy_.maximum_rows,
                     SqliteVerificationBudgetFailure::row_limit);
}

void SqliteVerificationBudget::consume_decoded_text_bytes(
    std::size_t byte_count) {
    require_current_execution_or_throw();
    check_elapsed_or_throw();
    consume_or_throw(static_cast<std::uint64_t>(byte_count),
                     decoded_text_bytes_, policy_.maximum_decoded_text_bytes,
                     SqliteVerificationBudgetFailure::decoded_text_byte_limit);
}

void SqliteVerificationBudget::consume_text_row(
    std::initializer_list<std::string_view> fields) {
    require_current_execution_or_throw();
    check_elapsed_or_throw();
    consume_or_throw(1U, rows_, policy_.maximum_rows,
                     SqliteVerificationBudgetFailure::row_limit);
    for (const std::string_view field : fields) {
        consume_or_throw(static_cast<std::uint64_t>(field.size()),
                         decoded_text_bytes_,
                         policy_.maximum_decoded_text_bytes,
                         SqliteVerificationBudgetFailure::decoded_text_byte_limit);
    }
}

void SqliteVerificationBudget::consume_retained_text(
    std::initializer_list<std::string_view> fields) {
    require_current_execution_or_throw();
    check_elapsed_or_throw();
    for (const std::string_view field : fields) {
        consume_or_throw(static_cast<std::uint64_t>(field.size()),
                         retained_text_bytes_,
                         policy_.maximum_retained_text_bytes,
                         SqliteVerificationBudgetFailure::retained_text_byte_limit);
    }
}

void SqliteVerificationBudget::checkpoint() {
    require_current_execution_or_throw();
    check_elapsed_or_throw();
}

bool SqliteVerificationBudget::exhausted() const noexcept {
    require_current_execution_noexcept();
    return failure_ != SqliteVerificationBudgetFailure::none;
}

SqliteVerificationBudgetFailure SqliteVerificationBudget::failure() const noexcept {
    require_current_execution_noexcept();
    return failure_;
}

std::uint64_t SqliteVerificationBudget::progress_callbacks() const noexcept {
    require_current_execution_noexcept();
    return progress_callbacks_;
}

std::uint64_t SqliteVerificationBudget::rows() const noexcept {
    require_current_execution_noexcept();
    return rows_;
}

std::uint64_t SqliteVerificationBudget::decoded_text_bytes() const noexcept {
    require_current_execution_noexcept();
    return decoded_text_bytes_;
}

std::uint64_t SqliteVerificationBudget::retained_text_bytes() const noexcept {
    require_current_execution_noexcept();
    return retained_text_bytes_;
}

std::string SqliteVerificationBudget::safe_summary() const {
    require_current_execution_or_throw();
    if (!exhausted()) return "sqlite_verification_budget[none]";
    return "sqlite_verification_budget[" +
           std::string(sqlite_verification_budget_failure_name(failure_)) +
           "]:observed=" + std::to_string(failure_observed_) +
           ":limit=" + std::to_string(failure_limit_);
}

void SqliteVerificationBudget::throw_if_exhausted() const {
    require_current_execution_or_throw();
    if (!exhausted()) return;
    throw SqliteVerificationBudgetException(
        label_, failure_, failure_observed_, failure_limit_);
}

void SqliteVerificationBudget::detach() noexcept {
    require_current_execution_noexcept();
    sqlite3* const database = database_borrow_.get();
    if (database == nullptr) {
        if (callback_claim_.attached()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return;
    }

    {
        SyncSqliteDatabaseMutexGuard mutation_guard(
            database, kSyncSqliteDatabaseMutexFailStop);
        callback_claim_.require_live(database, mutation_guard);
        sqlite3_progress_handler(database, 0, nullptr, nullptr);
        callback_claim_.detach(database, mutation_guard);
    }
    // The generation pin outlives the exact recursive mutex entry.
    database_borrow_.reset();
}

int SqliteVerificationBudget::progress_callback(void* context) noexcept {
    if (context == nullptr) return 1;
    return static_cast<SqliteVerificationBudget*>(context)->on_progress();
}

int SqliteVerificationBudget::on_progress() noexcept {
    require_current_execution_noexcept();
    // The callback already established process and exact-thread authority.
    // Read the sticky field directly instead of repeating the same fail-stop
    // checks through the public diagnostic accessor on every SQLite callback.
    if (failure_ != SqliteVerificationBudgetFailure::none) return 1;
    if (progress_callbacks_ == std::numeric_limits<std::uint64_t>::max()) {
        mark_failure(SqliteVerificationBudgetFailure::progress_callback_limit,
                     progress_callbacks_,
                     policy_.maximum_progress_callbacks);
        return 1;
    }
    ++progress_callbacks_;
    if (progress_callbacks_ > policy_.maximum_progress_callbacks) {
        mark_failure(SqliteVerificationBudgetFailure::progress_callback_limit,
                     progress_callbacks_,
                     policy_.maximum_progress_callbacks);
        return 1;
    }

    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - started_);
    const auto observed = elapsed.count() < 0
                              ? 0U
                              : static_cast<std::uint64_t>(elapsed.count());
    if (observed > policy_.maximum_elapsed_milliseconds) {
        mark_failure(SqliteVerificationBudgetFailure::elapsed_time_limit,
                     observed, policy_.maximum_elapsed_milliseconds);
        return 1;
    }
    return 0;
}

void SqliteVerificationBudget::check_elapsed_or_throw() {
    if (exhausted()) throw_if_exhausted();
    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - started_);
    const auto observed = elapsed.count() < 0
                              ? 0U
                              : static_cast<std::uint64_t>(elapsed.count());
    if (observed > policy_.maximum_elapsed_milliseconds) {
        mark_failure(SqliteVerificationBudgetFailure::elapsed_time_limit,
                     observed, policy_.maximum_elapsed_milliseconds);
        throw_if_exhausted();
    }
}

void SqliteVerificationBudget::consume_or_throw(
    std::uint64_t amount,
    std::uint64_t& observed,
    std::uint64_t limit,
    SqliteVerificationBudgetFailure failure) {
    if (exhausted()) throw_if_exhausted();
    if (observed > limit || amount > limit - observed) {
        const std::uint64_t attempted =
            amount > std::numeric_limits<std::uint64_t>::max() - observed
                ? std::numeric_limits<std::uint64_t>::max()
                : observed + amount;
        mark_failure(failure, attempted, limit);
        throw_if_exhausted();
    }
    observed += amount;
}

void SqliteVerificationBudget::mark_failure(
    SqliteVerificationBudgetFailure failure,
    std::uint64_t observed,
    std::uint64_t limit) noexcept {
    if (failure_ != SqliteVerificationBudgetFailure::none) return;
    failure_ = failure;
    failure_observed_ = observed;
    failure_limit_ = limit;
}

void SqliteVerificationBudget::require_current_execution_noexcept() const noexcept {
    if (!sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_thread_incarnation_is_current(thread_id_)) {
        fail_stop_on_sync_thread_capability_violation_noexcept();
    }
}

void SqliteVerificationBudget::require_current_execution_or_throw() const {
    // Do not inspect diagnostics or any other owner state until both execution
    // capabilities are established. A foreign thread receives a stable,
    // value-free programming-error message rather than caller diagnostics.
    require_sync_process_incarnation_or_fail_stop(
        process_id_, "SQLite verification budget");
    require_sync_thread_incarnation_or_throw(
        thread_id_, "SQLite verification budget");
}

}  // namespace anonsync::persistence
