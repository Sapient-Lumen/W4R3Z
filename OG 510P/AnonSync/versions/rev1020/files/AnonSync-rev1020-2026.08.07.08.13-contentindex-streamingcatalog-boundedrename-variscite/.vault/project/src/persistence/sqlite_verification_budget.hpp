#pragma once

#include "sqlite_retained_callback_claim.hpp"
#include "sync_process_incarnation.hpp"
#include "sync_sqlite_handle_slot.hpp"
#include "sync_thread_incarnation.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <stdexcept>
#include <string>
#include <string_view>

struct sqlite3;

namespace anonsync::persistence {

// Reviewed in-process ceilings for interpreting one untrusted SQLite database.
// A caller may tighten any dimension but may never widen one. These bounds are
// defense in depth; a disposable OS-resource-limited worker is still required
// before treating hostile-database interpretation as a complete containment
// boundary.
inline constexpr std::uint64_t kMaximumSqliteVerificationProgressCallbacks =
    1'000'000ULL;
inline constexpr std::uint32_t kMaximumSqliteVerificationProgressOpcodeInterval =
    1'000U;
inline constexpr std::uint64_t kMaximumSqliteVerificationRows = 300'000ULL;
inline constexpr std::uint64_t kMaximumSqliteVerificationDecodedTextBytes =
    256ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kMaximumSqliteVerificationRetainedTextBytes =
    64ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kMaximumSqliteVerificationElapsedMilliseconds =
    60'000ULL;

struct SqliteVerificationBudgetPolicy {
    std::uint64_t maximum_progress_callbacks =
        kMaximumSqliteVerificationProgressCallbacks;
    std::uint32_t progress_opcode_interval =
        kMaximumSqliteVerificationProgressOpcodeInterval;
    std::uint64_t maximum_rows = kMaximumSqliteVerificationRows;
    std::uint64_t maximum_decoded_text_bytes =
        kMaximumSqliteVerificationDecodedTextBytes;
    // Cumulative text copied into verifier-owned sets, maps, and vectors.
    // Allocator metadata, object headers, and SQLite's internal heap are not
    // represented by this counter and must not be claimed as bounded by it.
    std::uint64_t maximum_retained_text_bytes =
        kMaximumSqliteVerificationRetainedTextBytes;
    std::uint64_t maximum_elapsed_milliseconds =
        kMaximumSqliteVerificationElapsedMilliseconds;
};

// Derive a monotone default from geometry already promoted by the exact
// snapshot-geometry owner. Geometry may reduce resource authority but cannot
// enlarge any reviewed ceiling.
[[nodiscard]] SqliteVerificationBudgetPolicy
sqlite_verification_budget_for_snapshot(std::uint64_t exact_file_bytes,
                                        std::uint64_t page_count);

enum class SqliteVerificationBudgetFailure : std::uint8_t {
    none,
    progress_callback_limit,
    elapsed_time_limit,
    row_limit,
    decoded_text_byte_limit,
    retained_text_byte_limit,
};

[[nodiscard]] std::string_view sqlite_verification_budget_failure_name(
    SqliteVerificationBudgetFailure failure) noexcept;

class SqliteVerificationBudgetException final : public std::runtime_error {
public:
    SqliteVerificationBudgetException(
        std::string label,
        SqliteVerificationBudgetFailure failure,
        std::uint64_t observed,
        std::uint64_t limit);

    [[nodiscard]] SqliteVerificationBudgetFailure failure() const noexcept {
        return failure_;
    }
    [[nodiscard]] std::uint64_t observed() const noexcept { return observed_; }
    [[nodiscard]] std::uint64_t limit() const noexcept { return limit_; }

private:
    SqliteVerificationBudgetFailure failure_{};
    std::uint64_t observed_ = 0;
    std::uint64_t limit_ = 0;
};

// Lifetime owner for the sole sqlite3_progress_handler permitted on one
// hostile-verification connection, plus deterministic first-party accounting.
// SQLite retains this object's address as callback context, so it is neither
// copyable nor movable. Construction consumes one exact-generation serialized
// connection borrow and claims one named SQLite client-data slot. The borrow
// prevents typed close/replacement; the claim turns premature connection
// destruction or named-slot replacement into a fail-stop lifetime violation
// before a later detach can dereference stale SQLite storage. A raw
// sqlite3_close_v2() may defer actual destruction behind outstanding SQLite
// dependents; that unmediated call is outside the reviewed ownership protocol,
// and the claim fails stopped when deferred destruction eventually occurs.
// Construction holds the connection's recursive mutex across the complete
// "claim empty slot + install progress callback" transition. Concurrent
// legitimate constructors therefore produce one live owner and one ordinary
// rejection without replacing or destroying either contender's pending claim.
//
// The guarded connection must not execute on any thread except the exact thread
// that attached this owner. FULLMUTEX serialization does not transfer authority
// to this callback context or its ordinary C++ counters. Throwing entry points
// reject a foreign thread before reading diagnostic or mutable owner state;
// callbacks, noexcept accessors, detach, and destruction fail stopped. Process
// authority is checked first so inherited execution cannot be misclassified as
// an ordinary affinity error. The source inventory remains responsible for
// preventing unrelated sqlite3_progress_handler replacement: SQLite exposes no
// progress-handler getter.
class SqliteVerificationBudget final {
public:
    SqliteVerificationBudget(
        SyncSqliteSerializedDbBorrow database_borrow,
        std::string label,
        const SqliteVerificationBudgetPolicy& policy = {});
    ~SqliteVerificationBudget();

    SqliteVerificationBudget(const SqliteVerificationBudget&) = delete;
    SqliteVerificationBudget& operator=(const SqliteVerificationBudget&) = delete;
    SqliteVerificationBudget(SqliteVerificationBudget&&) = delete;
    SqliteVerificationBudget& operator=(SqliteVerificationBudget&&) = delete;

    void consume_row();
    void consume_decoded_text_bytes(std::size_t byte_count);
    void consume_text_row(std::initializer_list<std::string_view> fields);
    void consume_retained_text(std::initializer_list<std::string_view> fields);

    // Check elapsed time at a C++ boundary even when SQLite executed too few
    // opcodes to invoke the progress callback.
    void checkpoint();

    [[nodiscard]] bool exhausted() const noexcept;
    [[nodiscard]] SqliteVerificationBudgetFailure failure() const noexcept;
    [[nodiscard]] std::uint64_t progress_callbacks() const noexcept;
    [[nodiscard]] std::uint64_t rows() const noexcept;
    [[nodiscard]] std::uint64_t decoded_text_bytes() const noexcept;
    [[nodiscard]] std::uint64_t retained_text_bytes() const noexcept;
    [[nodiscard]] std::string safe_summary() const;

    // Turn a sticky callback failure (normally surfaced by SQLite as
    // SQLITE_INTERRUPT) back into the typed, value-free resource reason.
    void throw_if_exhausted() const;

    // Remove this object from SQLite before closing the connection. Manual
    // accounting and sticky-failure inspection remain valid after detach.
    void detach() noexcept;

private:
    static int progress_callback(void* context) noexcept;
    int on_progress() noexcept;
    void check_elapsed_or_throw();
    void consume_or_throw(std::uint64_t amount,
                          std::uint64_t& observed,
                          std::uint64_t limit,
                          SqliteVerificationBudgetFailure failure);
    void mark_failure(SqliteVerificationBudgetFailure failure,
                      std::uint64_t observed,
                      std::uint64_t limit) noexcept;
    void require_current_execution_noexcept() const noexcept;
    void require_current_execution_or_throw() const;

    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
    SyncSqliteSerializedDbBorrow database_borrow_;
    SqliteRetainedCallbackClaim callback_claim_;
    std::string label_;
    SqliteVerificationBudgetPolicy policy_;
    std::chrono::steady_clock::time_point started_;
    std::uint64_t progress_callbacks_ = 0;
    std::uint64_t rows_ = 0;
    std::uint64_t decoded_text_bytes_ = 0;
    std::uint64_t retained_text_bytes_ = 0;
    SqliteVerificationBudgetFailure failure_ =
        SqliteVerificationBudgetFailure::none;
    std::uint64_t failure_observed_ = 0;
    std::uint64_t failure_limit_ = 0;
};

}  // namespace anonsync::persistence
