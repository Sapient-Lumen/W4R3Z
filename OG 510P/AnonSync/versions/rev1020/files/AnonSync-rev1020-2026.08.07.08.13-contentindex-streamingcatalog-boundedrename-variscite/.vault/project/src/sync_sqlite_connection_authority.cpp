#include "sync_sqlite_connection_authority.hpp"

#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"
#include "persistence/sqlite_authorizer_owner.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_mutex_capability.hpp"

#include <atomic>
#include <cstdint>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {

namespace {

static_assert(SQLITE_VERSION_NUMBER >= 3044000,
              "SQLite connection client data requires SQLite 3.44.0+");

constexpr char kConnectionAuthorityClientDataName[] =
    "anonsync.sqlite.connection-authority.v1";
constexpr std::uint64_t kStateMagic = UINT64_C(0x41534e53434f4e4e);
constexpr std::uint64_t kFallbackProcessSalt =
    UINT64_C(0x416e6f6e53796e63);  // "AnonSync"

enum class TransactionPermitOperation : std::uint8_t {
    None,
    Begin,
    Commit,
    Rollback
};

enum class SavepointPermitOperation : std::uint8_t {
    None,
    Begin,
    Release,
    Rollback
};

struct ActiveSavepointFrame final {
    std::uint64_t generation = 0;
    std::string name;
};

struct ConnectionAuthorityState final {
    std::uint64_t magic = kStateMagic;
    ConnectionAuthorityState* self = this;
    SyncProcessIncarnation process_id = current_sync_process_incarnation_noexcept();
    std::uint64_t process_salt = 0;
    std::uint64_t connection_incarnation = 0;
    std::uint64_t authorizer_generation = 0;
    SyncSqliteOwnedAuthorizerPolicy policy_owner;
    std::uint64_t probe_nonce = 0;
    std::uint64_t observed_probe_nonce = 0;
    bool probe_active = false;

    // The bridge owns the transaction stack once it is installed. A typed
    // guard arms one single-use callback permit for one exact SQL boundary.
    // The generation survives statement objects and binds COMMIT/ROLLBACK to
    // the BEGIN that created the explicit transaction.
    std::uint64_t last_transaction_generation = 0;
    std::uint64_t active_transaction_generation = 0;
    TransactionPermitOperation transaction_permit =
        TransactionPermitOperation::None;
    bool transaction_permit_active = false;
    bool transaction_permit_observed = false;

    // Typed savepoints are a second, independently single-use permit lane.
    // The active vector mirrors only marks created by this bridge and is
    // cleared whenever the owning outer transaction ends. Names are generated
    // internally, so SQL text never contains caller-controlled identifiers.
    std::uint64_t last_savepoint_generation = 0;
    std::vector<ActiveSavepointFrame> active_savepoints;
    SavepointPermitOperation savepoint_permit =
        SavepointPermitOperation::None;
    // A permit is live only for the synchronous sqlite3_exec() call made by
    // the typed boundary owner. Borrow the already-stable generated name
    // instead of copying it. In particular, a rollback close must not perform
    // a C++ allocation after ROLLBACK TO has rewound state but before RELEASE
    // erases the mark.
    std::string_view savepoint_permit_name;
    bool savepoint_permit_active = false;
    bool savepoint_permit_observed = false;

    // The SQLite callback address is an explicit lifetime capability.  The
    // focused owner holds a separate client-data sentinel and must be detached
    // before this state object can be destroyed by explicit connection teardown.
    persistence::SqliteAuthorizerOwner authorizer_owner;
};

class RetainedMutexCapabilityReservation final {
public:
    RetainedMutexCapabilityReservation(sqlite3* db, const std::string& label)
        : state_(retain_sync_sqlite_mutex_capability_or_throw(db, label)) {}

    ~RetainedMutexCapabilityReservation() {
        if (state_ != nullptr) {
            release_sync_sqlite_mutex_capability_noexcept(state_);
        }
    }

    RetainedMutexCapabilityReservation(
        const RetainedMutexCapabilityReservation&) = delete;
    RetainedMutexCapabilityReservation& operator=(
        const RetainedMutexCapabilityReservation&) = delete;

    SyncSqliteRetainedMutexCapabilityState* release() noexcept {
        SyncSqliteRetainedMutexCapabilityState* out = state_;
        state_ = nullptr;
        return out;
    }

private:
    SyncSqliteRetainedMutexCapabilityState* state_ = nullptr;
};

[[nodiscard]] bool retained_mutex_lease_shape_is_valid(
    sqlite3_mutex* mutex,
    SyncProcessIncarnation process_id,
    SyncSqliteThreadIncarnation owner_thread_incarnation,
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept {
    if (mutex == nullptr) {
        return !process_id.valid() && !owner_thread_incarnation.valid() &&
               retained_capability_state == nullptr;
    }
    return process_id.valid() && owner_thread_incarnation.valid() &&
           retained_capability_state != nullptr;
}

void require_retained_mutex_lease_owner_noexcept(
    sqlite3_mutex* mutex,
    SyncProcessIncarnation process_id,
    SyncSqliteThreadIncarnation owner_thread_incarnation,
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept {
    if (!retained_mutex_lease_shape_is_valid(
            mutex, process_id, owner_thread_incarnation,
            retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (mutex == nullptr) return;
    if (!sync_process_incarnation_is_current(process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(owner_thread_incarnation) ||
        !sync_sqlite_mutex_capability_is_live_noexcept(
            retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
}


class TransactionPermitScope final {
public:
    TransactionPermitScope(ConnectionAuthorityState& state,
                           TransactionPermitOperation operation,
                           const std::string& label)
        : state_(state) {
        if (operation == TransactionPermitOperation::None) {
            throw std::invalid_argument(label + " transaction permit is empty");
        }
        if (state_.transaction_permit_active ||
            state_.transaction_permit != TransactionPermitOperation::None ||
            state_.savepoint_permit_active) {
            throw std::logic_error(
                label + " transaction boundary permit is already armed");
        }
        state_.transaction_permit = operation;
        state_.transaction_permit_observed = false;
        state_.transaction_permit_active = true;
    }

    ~TransactionPermitScope() {
        state_.transaction_permit_active = false;
        state_.transaction_permit_observed = false;
        state_.transaction_permit = TransactionPermitOperation::None;
    }

    TransactionPermitScope(const TransactionPermitScope&) = delete;
    TransactionPermitScope& operator=(const TransactionPermitScope&) = delete;

    [[nodiscard]] bool observed() const noexcept {
        return state_.transaction_permit_observed;
    }

private:
    ConnectionAuthorityState& state_;
};

class SavepointPermitScope final {
public:
    SavepointPermitScope(ConnectionAuthorityState& state,
                         SavepointPermitOperation operation,
                         std::string_view name,
                         const std::string& label)
        : state_(state) {
        if (operation == SavepointPermitOperation::None || name.empty()) {
            throw std::invalid_argument(label + " savepoint permit is empty");
        }
        if (state_.savepoint_permit_active ||
            state_.savepoint_permit != SavepointPermitOperation::None ||
            state_.transaction_permit_active) {
            throw std::logic_error(
                label + " transaction-stack permit is already armed");
        }
        state_.savepoint_permit = operation;
        state_.savepoint_permit_name = name;
        state_.savepoint_permit_observed = false;
        state_.savepoint_permit_active = true;
    }

    ~SavepointPermitScope() {
        state_.savepoint_permit_active = false;
        state_.savepoint_permit_observed = false;
        state_.savepoint_permit = SavepointPermitOperation::None;
        state_.savepoint_permit_name = {};
    }

    SavepointPermitScope(const SavepointPermitScope&) = delete;
    SavepointPermitScope& operator=(const SavepointPermitScope&) = delete;

    [[nodiscard]] bool observed() const noexcept {
        return state_.savepoint_permit_observed;
    }

private:
    ConnectionAuthorityState& state_;
};

// Precompute every C++ object needed by a compound ROLLBACK TO + RELEASE
// close before the first SQLite effect. SQLite deliberately keeps the named
// mark live after ROLLBACK TO, so a denied or resource-failed RELEASE remains
// retryable. An unrelated std::bad_alloc between those two effects would be a
// needless split boundary and is therefore excluded by construction.
struct FencedSavepointClosePlan final {
    std::string rollback_sql;
    std::string release_sql;
    std::string rollback_label;
    std::string release_label;
};

FencedSavepointClosePlan make_fenced_savepoint_close_plan_or_throw(
    SyncSqliteSavepointBoundaryEnd operation,
    const std::string& savepoint_name,
    const std::string& label) {
    FencedSavepointClosePlan plan;
    if (operation == SyncSqliteSavepointBoundaryEnd::Rollback) {
        plan.rollback_sql =
            "ROLLBACK TO SAVEPOINT " + savepoint_name + ";";
        plan.rollback_label = label + " rollback to savepoint";
    }
    plan.release_sql = "RELEASE SAVEPOINT " + savepoint_name + ";";
    plan.release_label = label + " release savepoint";
    return plan;
}

std::uint64_t process_salt() noexcept {
    static const std::uint64_t salt = [] {
        std::uint64_t value = 0;
        sqlite3_randomness(static_cast<int>(sizeof(value)), &value);
        return value != 0 ? value : kFallbackProcessSalt;
    }();
    return salt;
}

std::uint64_t allocate_connection_incarnation_or_throw(
    const std::string& label) {
    static std::atomic<std::uint64_t> next{1};
    std::uint64_t current = next.load(std::memory_order_relaxed);
    for (;;) {
        if (current == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label + " exhausted process-local SQLite connection incarnations");
        }
        if (next.compare_exchange_weak(current,
                                       current + 1,
                                       std::memory_order_relaxed,
                                       std::memory_order_relaxed)) {
            return current;
        }
    }
}

std::uint64_t allocate_transaction_generation_or_throw(
    ConnectionAuthorityState& state,
    const std::string& label) {
    if (state.last_transaction_generation ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " exhausted process-local SQLite transaction generations");
    }
    ++state.last_transaction_generation;
    if (state.last_transaction_generation == 0) {
        throw std::overflow_error(
            label + " produced an invalid SQLite transaction generation");
    }
    return state.last_transaction_generation;
}

std::uint64_t allocate_savepoint_generation_or_throw(
    ConnectionAuthorityState& state,
    const std::string& label) {
    if (state.last_savepoint_generation ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " exhausted process-local SQLite savepoint generations");
    }
    ++state.last_savepoint_generation;
    if (state.last_savepoint_generation == 0) {
        throw std::overflow_error(
            label + " produced an invalid SQLite savepoint generation");
    }
    return state.last_savepoint_generation;
}

void destroy_connection_authority_state(void* raw) noexcept {
    auto* state = static_cast<ConnectionAuthorityState*>(raw);
    if (state == nullptr) return;
    if (!sync_process_incarnation_is_current(state->process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    // sqlite3_set_clientdata() uses the same destructor for explicit
    // replacement and connection close.  Either event is unsafe while SQLite
    // still retains state as its authorizer context.  Only the reviewed close
    // path first revokes the callback and its independent lifetime claim.
    if (state->authorizer_owner.attached() || !state->policy_owner.empty()) {
        // A policy context may carry an application-defined shared_ptr deleter.
        // It must be retired by the reviewed teardown path after SQLite has
        // forgotten the callback and after the connection mutex is released.
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    state->magic = 0;
    state->self = nullptr;
    delete state;
}

ConnectionAuthorityState* load_connection_authority_state_or_throw(
    sqlite3* db,
    bool allow_absent,
    const std::string& label) {
    void* raw = sqlite3_get_clientdata(db, kConnectionAuthorityClientDataName);
    if (raw == nullptr) {
        if (allow_absent) return nullptr;
        throw std::runtime_error(
            label + " connection incarnation is absent or was replaced");
    }
    auto* state = static_cast<ConnectionAuthorityState*>(raw);
    if (state->magic != kStateMagic || state->self != state ||
        !state->process_id.valid() || state->process_salt == 0 ||
        state->connection_incarnation == 0 ||
        state->authorizer_generation == 0 || !state->policy_owner.valid()) {
        throw std::runtime_error(
            label + " connection authority client-data slot is corrupt");
    }
    if (!sync_process_incarnation_is_current(state->process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    state->authorizer_owner.require_live(db);
    return state;
}

bool ascii_case_equal(const char* raw, std::string_view expected) noexcept {
    if (raw == nullptr) return false;
    std::size_t index = 0;
    for (; index < expected.size() && raw[index] != '\0'; ++index) {
        unsigned char observed = static_cast<unsigned char>(raw[index]);
        unsigned char wanted = static_cast<unsigned char>(expected[index]);
        if (observed >= 'a' && observed <= 'z') {
            observed = static_cast<unsigned char>(observed - 'a' + 'A');
        }
        if (wanted >= 'a' && wanted <= 'z') {
            wanted = static_cast<unsigned char>(wanted - 'a' + 'A');
        }
        if (observed != wanted) return false;
    }
    return index == expected.size() && raw[index] == '\0';
}

bool transaction_operation_matches(TransactionPermitOperation operation,
                                   const char* argument1) noexcept {
    switch (operation) {
        case TransactionPermitOperation::Begin:
            return ascii_case_equal(argument1, "BEGIN");
        case TransactionPermitOperation::Commit:
            return ascii_case_equal(argument1, "COMMIT");
        case TransactionPermitOperation::Rollback:
            return ascii_case_equal(argument1, "ROLLBACK");
        case TransactionPermitOperation::None:
            return false;
    }
    return false;
}

bool savepoint_operation_matches(SavepointPermitOperation operation,
                                 const char* argument1) noexcept {
    switch (operation) {
        case SavepointPermitOperation::Begin:
            return ascii_case_equal(argument1, "BEGIN");
        case SavepointPermitOperation::Release:
            return ascii_case_equal(argument1, "RELEASE");
        case SavepointPermitOperation::Rollback:
            return ascii_case_equal(argument1, "ROLLBACK");
        case SavepointPermitOperation::None:
            return false;
    }
    return false;
}

int invoke_policy_or_deny(ConnectionAuthorityState& state,
                          int action,
                          const char* argument1,
                          const char* argument2,
                          const char* database_name,
                          const char* trigger_or_view,
                          bool ignore_is_valid) noexcept {
    if (state.policy_owner.empty()) return SQLITE_DENY;
    try {
        const int decision = state.policy_owner.invoke(action,
                                                       argument1,
                                                       argument2,
                                                       database_name,
                                                       trigger_or_view);
        if (decision == SQLITE_OK || decision == SQLITE_DENY ||
            (ignore_is_valid && decision == SQLITE_IGNORE)) {
            return decision;
        }
        // A malformed policy result must never become permissive by relying on
        // SQLite's handling of an undocumented callback value.
        return SQLITE_DENY;
    } catch (...) {
        // Exceptions may not cross SQLite's C callback boundary.
        return SQLITE_DENY;
    }
}

int connection_authorizer_bridge(void* raw,
                                 int action,
                                 const char* argument1,
                                 const char* argument2,
                                 const char* database_name,
                                 const char* trigger_or_view) noexcept {
    auto* state = static_cast<ConnectionAuthorityState*>(raw);
    if (state == nullptr || state->magic != kStateMagic ||
        state->self != state || !state->process_id.valid()) {
        return SQLITE_DENY;
    }
    if (!sync_process_incarnation_is_current(state->process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (state->probe_active) {
        state->observed_probe_nonce = state->probe_nonce;
        return SQLITE_OK;
    }

    // SAVEPOINT is transaction-stack control: an outermost mark starts a
    // transaction and RELEASE of that mark commits it. Only the typed bridge
    // may arm one exact operation/name pair, and SQLITE_IGNORE is never a safe
    // boundary decision.
    if (action == SQLITE_SAVEPOINT) {
        if (!state->savepoint_permit_active ||
            state->savepoint_permit_observed ||
            !savepoint_operation_matches(state->savepoint_permit, argument1) ||
            argument2 == nullptr ||
            state->savepoint_permit_name != argument2) {
            return SQLITE_DENY;
        }
        state->savepoint_permit_observed = true;
        return invoke_policy_or_deny(*state,
                                     action,
                                     argument1,
                                     argument2,
                                     database_name,
                                     trigger_or_view,
                                     false);
    }

    if (action == SQLITE_TRANSACTION) {
        if (!state->transaction_permit_active ||
            state->transaction_permit_observed ||
            !transaction_operation_matches(state->transaction_permit,
                                           argument1)) {
            return SQLITE_DENY;
        }
        // Consume before delegating. A reentrant or repeated callback cannot
        // reuse the same permit even when the policy returns SQLITE_OK.
        state->transaction_permit_observed = true;
        // SQLITE_IGNORE has no safe transaction-boundary meaning. Only an
        // explicit policy OK may pass the bridge's typed permit.
        return invoke_policy_or_deny(*state,
                                     action,
                                     argument1,
                                     argument2,
                                     database_name,
                                     trigger_or_view,
                                     false);
    }

    return invoke_policy_or_deny(*state,
                                 action,
                                 argument1,
                                 argument2,
                                 database_name,
                                 trigger_or_view,
                                 true);
}

struct AuthorizerOwnershipProbeObservation final {
    int prepare_result = SQLITE_MISUSE;
    int finalize_result = SQLITE_OK;
    bool callback_observed = false;
    bool statement_produced = false;
};

AuthorizerOwnershipProbeObservation observe_authorizer_ownership_noexcept(
    sqlite3* db,
    ConnectionAuthorityState& state) noexcept {
    ++state.probe_nonce;
    state.observed_probe_nonce = 0;
    state.probe_active = true;

    sqlite3_stmt* statement = nullptr;
    static constexpr char kProbeSql[] = "SELECT 1;";
    AuthorizerOwnershipProbeObservation observation;
    observation.prepare_result = sqlite3_prepare_v3(
        db,
        kProbeSql,
        static_cast<int>(sizeof(kProbeSql) - 1),
        SQLITE_PREPARE_PERSISTENT,
        &statement,
        nullptr);
    state.probe_active = false;
    observation.callback_observed =
        state.observed_probe_nonce == state.probe_nonce;
    observation.statement_produced = statement != nullptr;
    observation.finalize_result =
        statement != nullptr ? sqlite3_finalize(statement) : SQLITE_OK;
    return observation;
}

SyncSqliteBoundaryAuthorityStatus classify_authorizer_observation_noexcept(
    const AuthorizerOwnershipProbeObservation& observation) noexcept {
    if (observation.callback_observed) {
        // The exact bridge generation ran, but a failed prepare/finalize does
        // not provide a healthy completed probe. Reject this use without
        // revoking identity evidence that was positively observed.
        return observation.prepare_result == SQLITE_OK &&
                       observation.statement_produced &&
                       observation.finalize_result == SQLITE_OK
                   ? SyncSqliteBoundaryAuthorityStatus::Current
                   : SyncSqliteBoundaryAuthorityStatus::Indeterminate;
    }

    const int primary_result = observation.prepare_result & 0xff;
    switch (primary_result) {
        case SQLITE_NOMEM:
        case SQLITE_BUSY:
        case SQLITE_LOCKED:
        case SQLITE_INTERRUPT:
        case SQLITE_IOERR:
        case SQLITE_FULL:
        case SQLITE_CANTOPEN:
        case SQLITE_PROTOCOL:
        case SQLITE_ABORT:
            // SQLite may have failed before it reached the callback. Absence of
            // an observation is therefore not evidence of callback replacement.
            return SyncSqliteBoundaryAuthorityStatus::Indeterminate;
        default:
            // Success without callback, SQLITE_AUTH, malformed-authorizer
            // SQLITE_ERROR, and other deterministic failures invalidate the
            // ownership probe rather than granting a retryable identity claim.
            return SyncSqliteBoundaryAuthorityStatus::Invalid;
    }
}

void run_authorizer_ownership_probe_or_throw(
    sqlite3* db,
    ConnectionAuthorityState& state,
    const std::string& label) {
    if (state.probe_active) {
        throw std::logic_error(label + " authorizer ownership probe is reentrant");
    }
    if (state.transaction_permit_active || state.savepoint_permit_active) {
        throw std::logic_error(
            label + " authorizer ownership probe crossed an armed transaction-stack permit");
    }
    if (state.probe_nonce == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " exhausted authorizer probe nonces");
    }

    const AuthorizerOwnershipProbeObservation observation =
        observe_authorizer_ownership_noexcept(db, state);
    if (observation.prepare_result != SQLITE_OK) {
        if (!observation.callback_observed &&
            (observation.prepare_result & 0xff) == SQLITE_AUTH) {
            throw std::runtime_error(
                label +
                " authorizer ownership probe failed: callback was disabled, "
                "replaced, or did not observe the exact generation");
        }
        throw_sqlite_exception(db,
                               observation.prepare_result,
                               label + " prepare authorizer ownership probe");
    }
    if (!observation.callback_observed) {
        throw std::runtime_error(
            label +
            " authorizer ownership probe failed: callback was disabled, replaced, "
            "or did not observe the exact generation");
    }
    if (!observation.statement_produced) {
        throw std::runtime_error(
            label + " authorizer ownership probe produced no statement");
    }
    if (observation.finalize_result != SQLITE_OK) {
        throw_sqlite_exception(db,
                               observation.finalize_result,
                               label + " finalize authorizer ownership probe");
    }
}

void execute_permitted_transaction_sql_or_throw(
    sqlite3* db,
    ConnectionAuthorityState& state,
    TransactionPermitOperation operation,
    const std::string& sql,
    const std::string& label) {
    TransactionPermitScope permit(state, operation, label);
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    const bool observed = permit.observed();

    if (rc != SQLITE_OK) {
        // Do not ask sqlite3_exec() to allocate a second error string after a
        // transaction-stack effect. sqlite3_errmsg() remains connection-owned,
        // and removing this allocation makes the returned boundary state the
        // only post-effect evidence that must be composed by the caller.
        throw_sqlite_exception(db, rc, label);
    }
    if (!observed) {
        throw std::runtime_error(
            label +
            " transaction boundary succeeded without consuming the exact "
            "authorizer permit");
    }
}

[[nodiscard]] bool execute_permitted_savepoint_sql_or_throw(
    sqlite3* db,
    ConnectionAuthorityState& state,
    SavepointPermitOperation operation,
    const std::string& savepoint_name,
    const std::string& sql,
    const std::string& label) {
    SavepointPermitScope permit(state, operation, savepoint_name, label);
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    const bool observed = permit.observed();

    if (rc != SQLITE_OK) {
        // Do not ask sqlite3_exec() to allocate a second error string after a
        // transaction-stack effect. sqlite3_errmsg() remains connection-owned,
        // and removing this allocation makes the returned boundary state the
        // only post-effect evidence that must be composed by the caller.
        throw_sqlite_exception(db, rc, label);
    }
    // Success without observation means another callback accepted and
    // executed the SQL after our ownership probe. The caller must update its
    // stack model to match SQLite, then fail closed instead of pretending that
    // the AnonSync bridge authorized the operation.
    return observed;
}

std::uint64_t allocate_unfenced_savepoint_generation_or_throw(
    const std::string& label) {
    static std::atomic<std::uint64_t> next{1};
    std::uint64_t current = next.load(std::memory_order_relaxed);
    for (;;) {
        if (current == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label + " exhausted process-local unfenced savepoint generations");
        }
        if (next.compare_exchange_weak(current,
                                       current + 1,
                                       std::memory_order_relaxed,
                                       std::memory_order_relaxed)) {
            return current;
        }
    }
}

std::string fenced_savepoint_name(
    const ConnectionAuthorityState& state,
    std::uint64_t savepoint_generation) {
    return "anonsync_sp_" + std::to_string(state.connection_incarnation) + "_" +
           std::to_string(state.active_transaction_generation) + "_" +
           std::to_string(savepoint_generation);
}

std::string unfenced_savepoint_name(std::uint64_t generation) {
    return "anonsync_unfenced_sp_" + std::to_string(generation);
}

void validate_savepoint_proof_common_or_throw(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof,
    const std::string& label) {
    if (proof.db == nullptr || proof.db != db || !proof.process_id.valid() ||
        proof.savepoint_generation == 0 || !proof.owner_thread_incarnation.valid() ||
        proof.retained_capability_state == nullptr ||
        proof.savepoint_name.empty()) {
        throw std::logic_error(
            label + " savepoint boundary proof is empty or targets another handle");
    }
    require_sync_process_incarnation_or_fail_stop(
        proof.process_id, label + " savepoint boundary");
    require_sync_sqlite_thread_incarnation_or_throw(
        proof.owner_thread_incarnation, label + " savepoint boundary");
    if (!sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        throw std::logic_error(
            label + " retained SQLite savepoint mutex capability is no longer live");
    }
}

std::size_t find_fenced_savepoint_index_or_throw(
    const ConnectionAuthorityState& state,
    const SyncSqliteSavepointBoundaryProof& proof,
    const std::string& label) {
    for (std::size_t index = 0; index < state.active_savepoints.size(); ++index) {
        const ActiveSavepointFrame& frame = state.active_savepoints[index];
        if (frame.generation == proof.savepoint_generation) {
            if (frame.name != proof.savepoint_name) {
                throw std::runtime_error(
                    label + " typed SQLite savepoint name changed");
            }
            return index;
        }
    }
    throw std::runtime_error(
        label + " typed SQLite savepoint generation changed");
}

ConnectionAuthorityState& validate_fenced_savepoint_proof_or_throw(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof,
    const std::string& label,
    bool require_top) {
    validate_savepoint_proof_common_or_throw(db, proof, label);
    if (!proof.fenced || proof.process_salt == 0 ||
        proof.connection_incarnation == 0 || proof.authorizer_generation == 0 ||
        proof.transaction_generation == 0) {
        throw std::logic_error(label + " fenced savepoint proof is incomplete");
    }
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, false, label);
    if (state->process_id != proof.process_id ||
        state->process_salt != proof.process_salt ||
        state->connection_incarnation != proof.connection_incarnation ||
        state->authorizer_generation != proof.authorizer_generation) {
        throw std::runtime_error(
            label + " connection incarnation or authorizer generation changed");
    }
    if (state->active_transaction_generation != proof.transaction_generation ||
        sqlite3_get_autocommit(db) != 0) {
        throw std::runtime_error(
            label + " typed SQLite outer transaction generation changed");
    }
    const std::size_t index =
        find_fenced_savepoint_index_or_throw(*state, proof, label);
    if (require_top && index + 1 != state->active_savepoints.size()) {
        throw std::logic_error(
            label + " savepoint must close in reverse construction order");
    }
    return *state;
}

void rollback_newly_started_transaction_noexcept(
    sqlite3* db,
    ConnectionAuthorityState& state) noexcept {
    if (sqlite3_get_autocommit(db) != 0) return;
    try {
        // The caller still owns the recursive connection mutex and no other
        // operation can have crossed the just-issued BEGIN. A permit handles
        // the normal bridge; the same statement remains a safe exact rollback
        // if the callback was disabled and therefore consumes no permit.
        TransactionPermitScope permit(
            state,
            TransactionPermitOperation::Rollback,
            "failed typed BEGIN cleanup");
        (void)sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
    } catch (...) {
        // The connection remains fail-stopped with its generation recorded.
    }
}

ConnectionAuthorityState& validate_boundary_proof_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof,
    const std::string& label) {
    if (!proof.fenced || proof.db == nullptr || proof.db != db ||
        !proof.process_id.valid() || proof.process_salt == 0 ||
        proof.connection_incarnation == 0 ||
        proof.authorizer_generation == 0 || proof.transaction_generation == 0 ||
        !proof.owner_thread_incarnation.valid() ||
        proof.retained_capability_state == nullptr) {
        throw std::logic_error(
            label + " transaction boundary proof is empty or targets another handle");
    }
    // Reject a fork child before touching SQLite-owned state, then reject a
    // foreign thread before inspecting the retained lifetime sentinel.
    require_sync_process_incarnation_or_fail_stop(
        proof.process_id, label + " transaction boundary");
    require_sync_sqlite_thread_incarnation_or_throw(
        proof.owner_thread_incarnation, label + " transaction boundary");
    if (!sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        throw std::logic_error(
            label + " retained SQLite mutex capability is no longer live");
    }
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, false, label);
    if (state->process_id != proof.process_id ||
        state->process_salt != proof.process_salt ||
        state->connection_incarnation != proof.connection_incarnation ||
        state->authorizer_generation != proof.authorizer_generation) {
        throw std::runtime_error(
            label + " connection incarnation or authorizer generation changed");
    }
    if (state->active_transaction_generation != proof.transaction_generation) {
        throw std::runtime_error(
            label + " typed SQLite transaction generation changed");
    }
    return *state;
}

void clear_stale_transaction_generation_if_ended(
    sqlite3* db,
    ConnectionAuthorityState& state) noexcept {
    if (state.active_transaction_generation != 0 &&
        sqlite3_get_autocommit(db) != 0) {
        state.active_transaction_generation = 0;
        state.active_savepoints.clear();
    }
}

void revoke_connection_authority_state_locked_noexcept(
    sqlite3* db,
    ConnectionAuthorityState* state,
    SyncSqliteOwnedAuthorizerPolicy& retired_policy) noexcept {
    if (db == nullptr || state == nullptr || state->magic != kStateMagic ||
        state->self != state || !state->process_id.valid() ||
        !sync_process_incarnation_is_current(state->process_id) ||
        state->process_salt == 0 || state->connection_incarnation == 0 ||
        state->authorizer_generation == 0 || !retired_policy.empty() ||
        !state->policy_owner.valid()) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (state->probe_active || state->transaction_permit_active ||
        state->transaction_permit != TransactionPermitOperation::None ||
        state->savepoint_permit_active ||
        state->savepoint_permit != SavepointPermitOperation::None ||
        !state->savepoint_permit_name.empty() ||
        sqlite3_get_autocommit(db) == 0) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }

    // An observed out-of-band rollback may leave only stale process-local stack
    // bookkeeping.  Once SQLite proves autocommit, clearing that evidence is
    // safe and prevents close from preserving a phantom generation.
    state->active_transaction_generation = 0;
    state->active_savepoints.clear();

    // Ordered consumption is mandatory: remove SQLite's retained callback,
    // release its independent lifetime claim, escrow the application policy
    // outside the SQLite-owned state, and only then clear that state slot.
    // The caller leaves the connection mutex before retired_policy's destructor
    // can run arbitrary application-defined shared_ptr disposal code.
    state->authorizer_owner.detach(db);
    state->policy_owner.swap(retired_policy);
    if (sqlite3_set_clientdata(
            db, kConnectionAuthorityClientDataName, nullptr, nullptr) !=
        SQLITE_OK) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

}  // namespace

SyncSqliteConnectionAuthorityProof::SyncSqliteConnectionAuthorityProof(
    SyncProcessIncarnation process_id,
    std::uint64_t process_salt,
    std::uint64_t connection_incarnation,
    std::uint64_t authorizer_generation) noexcept
    : process_id_(process_id),
      process_salt_(process_salt),
      connection_incarnation_(connection_incarnation),
      authorizer_generation_(authorizer_generation),
      valid_(process_id.valid() && process_salt != 0 &&
             connection_incarnation != 0 && authorizer_generation != 0) {}

bool SyncSqliteConnectionAuthorityProof::valid() const noexcept {
    return valid_ && sync_process_incarnation_is_current(process_id_);
}

std::uint64_t
SyncSqliteConnectionAuthorityProof::authorizer_generation() const noexcept {
    return authorizer_generation_;
}

SyncSqliteConnectionAuthorityLease::SyncSqliteConnectionAuthorityLease(
    sqlite3_mutex* mutex,
    SyncProcessIncarnation process_id,
    SyncSqliteThreadIncarnation owner_thread_incarnation,
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept
    : mutex_(mutex),
      process_id_(process_id),
      owner_thread_incarnation_(owner_thread_incarnation),
      retained_capability_state_(retained_capability_state) {
    require_retained_mutex_lease_owner_noexcept(
        mutex_, process_id_, owner_thread_incarnation_,
        retained_capability_state_);
}

SyncSqliteConnectionAuthorityLease::~SyncSqliteConnectionAuthorityLease() {
    require_retained_mutex_lease_owner_noexcept(
        mutex_, process_id_, owner_thread_incarnation_,
        retained_capability_state_);
    if (mutex_ == nullptr) return;
    release_sync_sqlite_mutex_capability_noexcept(retained_capability_state_);
    sqlite3_mutex_leave(mutex_);
}

SyncSqliteConnectionAuthorityLease::SyncSqliteConnectionAuthorityLease(
    SyncSqliteConnectionAuthorityLease&& other) noexcept
    : mutex_(other.mutex_),
      process_id_(other.process_id_),
      owner_thread_incarnation_(other.owner_thread_incarnation_),
      retained_capability_state_(other.retained_capability_state_) {
    require_retained_mutex_lease_owner_noexcept(
        mutex_, process_id_, owner_thread_incarnation_,
        retained_capability_state_);
    other.mutex_ = nullptr;
    other.process_id_ = {};
    other.owner_thread_incarnation_ = {};
    other.retained_capability_state_ = nullptr;
}

SyncSqliteConnectionAuthorityLease&
SyncSqliteConnectionAuthorityLease::operator=(
    SyncSqliteConnectionAuthorityLease&& other) noexcept {
    // Validate the destination even for self-move. Otherwise an active lease
    // could be touched from a foreign thread through `x = std::move(x)` and
    // avoid the same fail-stop rule enforced by every other ownership move.
    require_retained_mutex_lease_owner_noexcept(
        mutex_, process_id_, owner_thread_incarnation_,
        retained_capability_state_);
    if (this == &other) return *this;

    require_retained_mutex_lease_owner_noexcept(
        other.mutex_,
        other.process_id_,
        other.owner_thread_incarnation_,
        other.retained_capability_state_);
    if (mutex_ != nullptr) {
        release_sync_sqlite_mutex_capability_noexcept(
            retained_capability_state_);
        sqlite3_mutex_leave(mutex_);
    }
    mutex_ = other.mutex_;
    process_id_ = other.process_id_;
    owner_thread_incarnation_ = other.owner_thread_incarnation_;
    retained_capability_state_ = other.retained_capability_state_;
    other.mutex_ = nullptr;
    other.process_id_ = {};
    other.owner_thread_incarnation_ = {};
    other.retained_capability_state_ = nullptr;
    return *this;
}

bool SyncSqliteConnectionAuthorityLease::active() const noexcept {
    return retained_mutex_lease_shape_is_valid(
               mutex_, process_id_, owner_thread_incarnation_,
               retained_capability_state_) &&
           mutex_ != nullptr &&
           sync_process_incarnation_is_current(process_id_) &&
           sync_sqlite_thread_incarnation_is_current(
               owner_thread_incarnation_) &&
           sync_sqlite_mutex_capability_is_live_noexcept(
               retained_capability_state_);
}

SyncSqliteConnectionAuthorityProof
install_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    SyncSqliteOwnedAuthorizerPolicy policy,
    const std::string& label) {
    if (!policy.valid()) {
        throw std::invalid_argument(label + " authorizer policy is empty");
    }

    // Declare the retirement escrow before the mutex guard. Reverse local
    // destruction order then proves the SQLite mutex is left before an old
    // application context (and its arbitrary custom deleter) is released.
    SyncSqliteOwnedAuthorizerPolicy retired_policy;
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " connection authority install");
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, true, label);

    if (state != nullptr) {
        clear_stale_transaction_generation_if_ended(db, *state);
        if (state->transaction_permit_active ||
            state->savepoint_permit_active) {
            throw std::logic_error(
                label + " cannot replace authority while a boundary permit is armed");
        }
        if (state->active_transaction_generation != 0 ||
            !state->active_savepoints.empty() ||
            sqlite3_get_autocommit(db) == 0) {
            throw std::logic_error(
                label +
                " cannot replace connection authority inside an active transaction");
        }
    } else if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(
            label + " cannot install connection authority inside an active transaction");
    }

    if (state == nullptr) {
        state = new ConnectionAuthorityState();
        state->process_salt = process_salt();
        state->connection_incarnation =
            allocate_connection_incarnation_or_throw(label);
        state->authorizer_generation = 1;

        // Keep the SQLite-owned state policy-empty until every potentially
        // failing publication step has completed. With a non-null destructor
        // SQLite assumes ownership even when set_clientdata reports NOMEM; its
        // synchronous destructor is therefore forbidden from releasing user
        // policy state.
        const int client_data_rc = sqlite3_set_clientdata(
            db,
            kConnectionAuthorityClientDataName,
            state,
            destroy_connection_authority_state);
        if (client_data_rc != SQLITE_OK) {
            throw_sqlite_exception(db,
                                   client_data_rc,
                                   label + " install connection incarnation");
        }

        try {
            state->authorizer_owner.attach(
                db, connection_authorizer_bridge, state,
                label + " install owned authorizer bridge");
        } catch (...) {
            // attach() releases its independent claim before returning an
            // error. The state and policy are still empty, so consuming the
            // client-data slot cannot run application disposal under SQLite.
            if (sqlite3_set_clientdata(
                    db, kConnectionAuthorityClientDataName, nullptr, nullptr) !=
                SQLITE_OK) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            throw;
        }
        state->policy_owner.swap(policy);
    } else {
        if (state->authorizer_generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label + " exhausted SQLite authorizer generations");
        }
        state->authorizer_owner.replace(
            db, connection_authorizer_bridge, state,
            label + " supersede SQLite authorizer bridge");
        state->policy_owner.swap(policy);
        retired_policy.swap(policy);
        ++state->authorizer_generation;
    }

    run_authorizer_ownership_probe_or_throw(db, *state, label);
    return SyncSqliteConnectionAuthorityProof(state->process_id,
                                               state->process_salt,
                                               state->connection_incarnation,
                                               state->authorizer_generation);
}

SyncSqliteConnectionAuthorityProof
install_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    SyncSqliteAuthorizerPolicy policy,
    void* policy_context,
    const std::string& label) {
    if (policy == nullptr) {
        throw std::invalid_argument(label + " authorizer policy is null");
    }
    if (policy_context != nullptr) {
        throw std::invalid_argument(
            label +
            " raw authorizer policy context is not owned; use SyncSqliteOwnedAuthorizerPolicy");
    }
    return install_sync_sqlite_connection_authority_or_throw(
        db, SyncSqliteOwnedAuthorizerPolicy(policy), label);
}

SyncSqliteConnectionAuthorityLease
acquire_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    const SyncSqliteConnectionAuthorityProof& proof,
    const std::string& label) {
    if (!proof.valid_) {
        throw std::invalid_argument(label + " connection authority proof is empty");
    }
    require_sync_process_incarnation_or_fail_stop(
        proof.process_id_, label + " connection authority proof");
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " connection authority acquire");
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, false, label);
    if (proof.process_id_ != state->process_id ||
        proof.process_salt_ != state->process_salt ||
        proof.connection_incarnation_ != state->connection_incarnation ||
        proof.authorizer_generation_ != state->authorizer_generation) {
        throw std::runtime_error(
            label + " connection incarnation or authorizer generation changed");
    }
    RetainedMutexCapabilityReservation retained_capability(
        db, label + " connection authority acquire");
    run_authorizer_ownership_probe_or_throw(db, *state, label);
    const SyncSqliteThreadIncarnation owner_thread =
        current_sync_sqlite_thread_incarnation_noexcept();
    sqlite3_mutex* const retained_mutex = guard.release();
    SyncSqliteRetainedMutexCapabilityState* const capability_state =
        retained_capability.release();
    return SyncSqliteConnectionAuthorityLease(
        retained_mutex, state->process_id, owner_thread, capability_state);
}

void revoke_sync_sqlite_connection_authority_before_close_noexcept(
    sqlite3* db) noexcept {
    if (db == nullptr) return;
    SyncSqliteOwnedAuthorizerPolicy retired_policy;
    void* raw = sqlite3_get_clientdata(db, kConnectionAuthorityClientDataName);
    if (raw == nullptr) return;

    // Authority installation itself requires FULLMUTEX.  An unserialized
    // connection with no authority is a valid owner-close case and must not be
    // rejected merely because this generic disposal hook is present.
    sqlite3_mutex* const mutex = sqlite3_db_mutex(db);
    if (mutex == nullptr) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    sqlite3_mutex_enter(mutex);
    raw = sqlite3_get_clientdata(db, kConnectionAuthorityClientDataName);
    if (raw != nullptr) {
        auto* const state = static_cast<ConnectionAuthorityState*>(raw);
        revoke_connection_authority_state_locked_noexcept(
            db, state, retired_policy);
    }
    sqlite3_mutex_leave(mutex);
}

bool sync_sqlite_connection_authority_state_present_or_throw(
    sqlite3* db,
    const std::string& label) {
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " connection authority presence");
    return load_connection_authority_state_or_throw(db, true, label) != nullptr;
}

SyncSqliteTransactionBoundaryProof
begin_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const std::string& begin_sql,
    const std::string& label) {
    if (begin_sql.empty()) {
        throw std::invalid_argument(label + " begin SQL is empty");
    }
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " typed transaction begin");
    if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(label + " cannot begin inside an active transaction");
    }

    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, true, label);
    if (state == nullptr) {
        RetainedMutexCapabilityReservation retained_capability(
            db, label + " unfenced typed transaction");
        try {
            sqlite_exec_or_throw(db, begin_sql, label);
        } catch (...) {
            if (sqlite3_get_autocommit(db) == 0) {
                (void)sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
            }
            throw;
        }
        if (sqlite3_get_autocommit(db) != 0) {
            throw std::logic_error(
                label + " begin did not establish an explicit transaction");
        }
        SyncSqliteTransactionBoundaryProof proof;
        proof.db = db;
        proof.process_id = current_sync_process_incarnation_noexcept();
        proof.owner_thread_incarnation =
            current_sync_sqlite_thread_incarnation_noexcept();
        proof.retained_connection_mutex = guard.release();
        proof.retained_capability_state = retained_capability.release();
        return proof;
    }

    clear_stale_transaction_generation_if_ended(db, *state);
    if (state->active_transaction_generation != 0 ||
        !state->active_savepoints.empty()) {
        throw std::logic_error(
            label + " another typed transaction generation remains active");
    }
    RetainedMutexCapabilityReservation retained_capability(
        db, label + " fenced typed transaction");
    run_authorizer_ownership_probe_or_throw(db, *state, label);

    const std::uint64_t generation =
        allocate_transaction_generation_or_throw(*state, label);
    state->active_transaction_generation = generation;
    try {
        execute_permitted_transaction_sql_or_throw(
            db,
            *state,
            TransactionPermitOperation::Begin,
            begin_sql,
            label);
    } catch (...) {
        if (sqlite3_get_autocommit(db) == 0) {
            rollback_newly_started_transaction_noexcept(db, *state);
        }
        if (sqlite3_get_autocommit(db) != 0) {
            state->active_transaction_generation = 0;
            state->active_savepoints.clear();
        }
        throw;
    }
    if (sqlite3_get_autocommit(db) != 0) {
        state->active_transaction_generation = 0;
        state->active_savepoints.clear();
        throw std::logic_error(
            label + " begin returned success without retaining a transaction");
    }

    SyncSqliteTransactionBoundaryProof proof;
    proof.db = db;
    proof.process_id = state->process_id;
    proof.process_salt = state->process_salt;
    proof.connection_incarnation = state->connection_incarnation;
    proof.authorizer_generation = state->authorizer_generation;
    proof.transaction_generation = generation;
    proof.owner_thread_incarnation =
        current_sync_sqlite_thread_incarnation_noexcept();
    proof.retained_connection_mutex = guard.release();
    proof.retained_capability_state = retained_capability.release();
    proof.fenced = true;
    return proof;
}

SyncSqliteSavepointBoundaryProof
begin_sync_sqlite_savepoint_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof* outer_transaction_proof,
    const std::string& label) {
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " typed savepoint begin");
    RetainedMutexCapabilityReservation retained_capability(
        db, label + " typed savepoint");
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, true, label);

    if (state == nullptr) {
        if (outer_transaction_proof != nullptr) {
            const SyncSqliteTransactionBoundaryProof& outer =
                *outer_transaction_proof;
            if (outer.fenced || outer.db != db || !outer.process_id.valid() ||
                !outer.owner_thread_incarnation.valid() ||
                outer.retained_capability_state == nullptr) {
                throw std::logic_error(
                    label + " unfenced outer transaction proof is invalid");
            }
            require_sync_process_incarnation_or_fail_stop(
                outer.process_id, label + " unfenced outer transaction");
            require_sync_sqlite_thread_incarnation_or_throw(
                outer.owner_thread_incarnation,
                label + " unfenced outer transaction");
            if (!sync_sqlite_mutex_capability_is_live_noexcept(
                    outer.retained_capability_state)) {
                throw std::logic_error(
                    label + " unfenced outer transaction is no longer live");
            }
            if (sqlite3_get_autocommit(db) != 0) {
                throw std::logic_error(
                    label + " unfenced outer transaction already ended");
            }
        }

        const bool outermost = sqlite3_get_autocommit(db) != 0;
        const std::uint64_t generation =
            allocate_unfenced_savepoint_generation_or_throw(label);
        SyncSqliteSavepointBoundaryProof proof;
        proof.db = db;
        proof.process_id = current_sync_process_incarnation_noexcept();
        proof.savepoint_generation = generation;
        proof.owner_thread_incarnation =
            current_sync_sqlite_thread_incarnation_noexcept();
        proof.savepoint_name = unfenced_savepoint_name(generation);
        proof.outermost_unfenced = outermost;
        const std::string sql = "SAVEPOINT " + proof.savepoint_name + ";";
        try {
            sqlite_exec_or_throw(db, sql, label);
        } catch (...) {
            if (outermost && sqlite3_get_autocommit(db) == 0) {
                (void)sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
            }
            throw;
        }
        if (sqlite3_get_autocommit(db) != 0) {
            throw std::logic_error(
                label + " savepoint did not retain a SQLite transaction");
        }
        proof.retained_connection_mutex = guard.release();
        proof.retained_capability_state = retained_capability.release();
        return proof;
    }

    if (outer_transaction_proof == nullptr) {
        throw std::logic_error(
            label +
            " requires the exact typed outer transaction authority on an "
            "AnonSync-authorized connection");
    }
    ConnectionAuthorityState& validated = validate_boundary_proof_or_throw(
        db, *outer_transaction_proof, label + " outer transaction");
    if (&validated != state || sqlite3_get_autocommit(db) != 0) {
        throw std::logic_error(
            label + " outer typed transaction is no longer active");
    }
    run_authorizer_ownership_probe_or_throw(db, *state, label);

    const std::uint64_t generation =
        allocate_savepoint_generation_or_throw(*state, label);
    SyncSqliteSavepointBoundaryProof proof;
    proof.db = db;
    proof.process_id = state->process_id;
    proof.process_salt = state->process_salt;
    proof.connection_incarnation = state->connection_incarnation;
    proof.authorizer_generation = state->authorizer_generation;
    proof.transaction_generation = state->active_transaction_generation;
    proof.savepoint_generation = generation;
    proof.owner_thread_incarnation =
        current_sync_sqlite_thread_incarnation_noexcept();
    proof.savepoint_name = fenced_savepoint_name(*state, generation);
    proof.fenced = true;

    // Complete every allocation before SQLite accepts the mark. Otherwise a
    // post-SAVEPOINT allocation failure could leave a database mark with no
    // matching C++ generation capable of closing it.
    const std::string sql = "SAVEPOINT " + proof.savepoint_name + ";";
    state->active_savepoints.push_back(
        ActiveSavepointFrame{generation, proof.savepoint_name});
    bool bridge_observed = false;
    try {
        bridge_observed = execute_permitted_savepoint_sql_or_throw(
            db,
            *state,
            SavepointPermitOperation::Begin,
            proof.savepoint_name,
            sql,
            label);
    } catch (...) {
        // A failing SAVEPOINT statement cannot publish the new mark.
        if (!state->active_savepoints.empty() &&
            state->active_savepoints.back().generation == generation) {
            state->active_savepoints.pop_back();
        }
        throw;
    }
    if (!bridge_observed) {
        // Another callback accepted the exact statement after the ownership
        // probe. Try to erase the just-created unique mark while the recursive
        // connection mutex is still held. If the alien callback refuses that
        // cleanup, retain the frame so outer COMMIT remains fail-closed.
        const std::string cleanup_sql =
            "ROLLBACK TO SAVEPOINT " + proof.savepoint_name + ";"
            "RELEASE SAVEPOINT " + proof.savepoint_name + ";";
        if (sqlite3_exec(db, cleanup_sql.c_str(), nullptr, nullptr, nullptr) ==
            SQLITE_OK) {
            state->active_savepoints.pop_back();
        }
        throw std::runtime_error(
            label +
            " savepoint began without consuming the exact AnonSync authorizer permit");
    }
    if (sqlite3_get_autocommit(db) != 0) {
        state->active_transaction_generation = 0;
        state->active_savepoints.clear();
        throw std::logic_error(
            label + " savepoint unexpectedly ended its typed outer transaction");
    }
    proof.retained_connection_mutex = guard.release();
    proof.retained_capability_state = retained_capability.release();
    return proof;
}

void end_sync_sqlite_savepoint_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof,
    SyncSqliteSavepointBoundaryEnd operation,
    const std::string& label) {
    validate_savepoint_proof_common_or_throw(db, proof, label);
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " typed savepoint end");

    if (!proof.fenced) {
        if (load_connection_authority_state_or_throw(db, true, label) != nullptr) {
            throw std::logic_error(
                label + " unfenced savepoint cannot cross authority installation");
        }
        if (sqlite3_get_autocommit(db) != 0) {
            throw std::logic_error(label + " unfenced savepoint is no longer active");
        }
        if (operation == SyncSqliteSavepointBoundaryEnd::Rollback) {
            sqlite_exec_or_throw(
                db,
                "ROLLBACK TO SAVEPOINT " + proof.savepoint_name + ";",
                label + " rollback to savepoint");
        }
        sqlite_exec_or_throw(
            db,
            "RELEASE SAVEPOINT " + proof.savepoint_name + ";",
            label + " release savepoint");
        const bool autocommit = sqlite3_get_autocommit(db) != 0;
        if (autocommit != proof.outermost_unfenced) {
            throw std::logic_error(
                label + " savepoint closure changed the wrong transaction boundary");
        }
        return;
    }

    ConnectionAuthorityState& state =
        validate_fenced_savepoint_proof_or_throw(db, proof, label, true);
    run_authorizer_ownership_probe_or_throw(db, state, label);

    // ROLLBACK TO leaves the mark live. Build both SQL statements, both
    // diagnostic labels, and the borrowed permit-name view before issuing it,
    // so only SQLite boundary outcomes can separate the rewind from RELEASE.
    const FencedSavepointClosePlan close_plan =
        make_fenced_savepoint_close_plan_or_throw(
            operation, proof.savepoint_name, label);

    bool bridge_observed = true;
    if (operation == SyncSqliteSavepointBoundaryEnd::Rollback) {
        bridge_observed = execute_permitted_savepoint_sql_or_throw(
                              db,
                              state,
                              SavepointPermitOperation::Rollback,
                              proof.savepoint_name,
                              close_plan.rollback_sql,
                              close_plan.rollback_label) &&
                          bridge_observed;
    }
    bridge_observed = execute_permitted_savepoint_sql_or_throw(
                          db,
                          state,
                          SavepointPermitOperation::Release,
                          proof.savepoint_name,
                          close_plan.release_sql,
                          close_plan.release_label) &&
                      bridge_observed;

    if (sqlite3_get_autocommit(db) != 0) {
        state.active_transaction_generation = 0;
        state.active_savepoints.clear();
        throw std::logic_error(
            label + " savepoint closure unexpectedly ended the typed transaction");
    }
    state.active_savepoints.pop_back();
    if (!bridge_observed) {
        throw std::runtime_error(
            label +
            " savepoint closed without consuming the exact AnonSync authorizer permit");
    }
}

void end_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof,
    SyncSqliteTransactionBoundaryEnd operation,
    const std::string& label) {
    require_sync_process_incarnation_or_fail_stop(
        proof.process_id, label + " transaction boundary");
    require_sync_sqlite_thread_incarnation_or_throw(
        proof.owner_thread_incarnation, label + " transaction boundary");
    SyncSqliteDatabaseMutexGuard guard(
        db, label + " typed transaction end");
    if (!proof.fenced) {
        if (proof.db != db) {
            throw std::logic_error(
                label + " unfenced transaction proof targets another handle");
        }
        sqlite_exec_or_throw(
            db,
            operation == SyncSqliteTransactionBoundaryEnd::Commit
                ? "COMMIT;"
                : "ROLLBACK;",
            label);
        return;
    }

    ConnectionAuthorityState& state =
        validate_boundary_proof_or_throw(db, proof, label);
    if (sqlite3_get_autocommit(db) != 0) {
        state.active_transaction_generation = 0;
        state.active_savepoints.clear();
        throw std::logic_error(
            label + " exact typed transaction boundary is no longer active");
    }
    if (operation == SyncSqliteTransactionBoundaryEnd::Commit &&
        !state.active_savepoints.empty()) {
        throw std::logic_error(
            label + " cannot commit while a typed savepoint remains active");
    }
    run_authorizer_ownership_probe_or_throw(db, state, label);

    const TransactionPermitOperation permit_operation =
        operation == SyncSqliteTransactionBoundaryEnd::Commit
            ? TransactionPermitOperation::Commit
            : TransactionPermitOperation::Rollback;
    const char* const sql =
        operation == SyncSqliteTransactionBoundaryEnd::Commit
            ? "COMMIT;"
            : "ROLLBACK;";
    try {
        execute_permitted_transaction_sql_or_throw(
            db, state, permit_operation, sql, label);
    } catch (...) {
        // SQLITE_BUSY can leave COMMIT retryable. SQLite may also roll back
        // automatically on selected errors. Retain the generation only while
        // the explicit boundary remains active.
        if (sqlite3_get_autocommit(db) != 0) {
            state.active_transaction_generation = 0;
            state.active_savepoints.clear();
        }
        throw;
    }

    if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(
            label + " returned success without restoring SQLite autocommit");
    }
    state.active_transaction_generation = 0;
    state.active_savepoints.clear();
}

void release_sync_sqlite_savepoint_mutex_noexcept(
    SyncSqliteSavepointBoundaryProof& proof) noexcept {
    if (proof.retained_connection_mutex == nullptr) {
        if (proof.retained_capability_state != nullptr) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        return;
    }
    if (!sync_process_incarnation_is_current(proof.process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (!sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    sqlite3_mutex* mutex = proof.retained_connection_mutex;
    proof.retained_connection_mutex = nullptr;
    release_sync_sqlite_mutex_capability_noexcept(
        proof.retained_capability_state);
    sqlite3_mutex_leave(mutex);
}

void release_sync_sqlite_transaction_mutex_noexcept(
    SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (proof.retained_connection_mutex == nullptr) {
        if (proof.retained_capability_state != nullptr) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        return;
    }
    if (!sync_process_incarnation_is_current(proof.process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (!sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    sqlite3_mutex* mutex = proof.retained_connection_mutex;
    proof.retained_connection_mutex = nullptr;
    release_sync_sqlite_mutex_capability_noexcept(
        proof.retained_capability_state);
    sqlite3_mutex_leave(mutex);
}

SyncSqliteBoundaryAuthorityStatus
sync_sqlite_savepoint_boundary_authority_status_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db ||
        !sync_process_incarnation_is_current(proof.process_id) ||
        !sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation) ||
        !sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        return SyncSqliteBoundaryAuthorityStatus::Invalid;
    }

    sqlite3_mutex* mutex = sqlite3_db_mutex(db);
    if (mutex == nullptr) return SyncSqliteBoundaryAuthorityStatus::Invalid;
    sqlite3_mutex_enter(mutex);
    SyncSqliteBoundaryAuthorityStatus status =
        SyncSqliteBoundaryAuthorityStatus::Invalid;
    try {
        if (!proof.fenced) {
            const bool current =
                load_connection_authority_state_or_throw(
                    db, true, "validate unfenced typed savepoint") == nullptr &&
                sqlite3_get_autocommit(db) == 0;
            status = current ? SyncSqliteBoundaryAuthorityStatus::Current
                             : SyncSqliteBoundaryAuthorityStatus::Invalid;
        } else {
            ConnectionAuthorityState& state =
                validate_fenced_savepoint_proof_or_throw(
                    db, proof, "validate typed savepoint authority", false);
            if (state.probe_active || state.transaction_permit_active ||
                state.savepoint_permit_active ||
                state.probe_nonce == std::numeric_limits<std::uint64_t>::max()) {
                status = SyncSqliteBoundaryAuthorityStatus::Indeterminate;
            } else {
                status = classify_authorizer_observation_noexcept(
                    observe_authorizer_ownership_noexcept(db, state));
            }
        }
    } catch (const std::bad_alloc&) {
        // Diagnostic construction or another host allocation can fail after a
        // SQLite probe error. Preserve the same retryable uncertainty.
        status = SyncSqliteBoundaryAuthorityStatus::Indeterminate;
    } catch (...) {
        status = SyncSqliteBoundaryAuthorityStatus::Invalid;
    }
    sqlite3_mutex_leave(mutex);
    return status;
}

bool sync_sqlite_savepoint_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept {
    return sync_sqlite_savepoint_boundary_authority_status_noexcept(db, proof) ==
           SyncSqliteBoundaryAuthorityStatus::Current;
}

SyncSqliteBoundaryAuthorityStatus
sync_sqlite_transaction_boundary_authority_status_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db ||
        !sync_process_incarnation_is_current(proof.process_id) ||
        !sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation) ||
        !sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        return SyncSqliteBoundaryAuthorityStatus::Invalid;
    }
    if (!proof.fenced) {
        return sqlite3_get_autocommit(db) == 0
                   ? SyncSqliteBoundaryAuthorityStatus::Current
                   : SyncSqliteBoundaryAuthorityStatus::Invalid;
    }

    sqlite3_mutex* mutex = sqlite3_db_mutex(db);
    if (mutex == nullptr) return SyncSqliteBoundaryAuthorityStatus::Invalid;
    sqlite3_mutex_enter(mutex);
    SyncSqliteBoundaryAuthorityStatus status =
        SyncSqliteBoundaryAuthorityStatus::Invalid;
    try {
        ConnectionAuthorityState& state =
            validate_boundary_proof_or_throw(
                db, proof, "validate typed transaction authority");
        if (sqlite3_get_autocommit(db) == 0) {
            if (state.probe_active || state.transaction_permit_active ||
                state.savepoint_permit_active ||
                state.probe_nonce == std::numeric_limits<std::uint64_t>::max()) {
                status = SyncSqliteBoundaryAuthorityStatus::Indeterminate;
            } else {
                status = classify_authorizer_observation_noexcept(
                    observe_authorizer_ownership_noexcept(db, state));
            }
        } else {
            state.active_transaction_generation = 0;
            state.active_savepoints.clear();
        }
    } catch (const std::bad_alloc&) {
        status = SyncSqliteBoundaryAuthorityStatus::Indeterminate;
    } catch (...) {
        status = SyncSqliteBoundaryAuthorityStatus::Invalid;
    }
    sqlite3_mutex_leave(mutex);
    return status;
}

bool sync_sqlite_transaction_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    return sync_sqlite_transaction_boundary_authority_status_noexcept(db, proof) ==
           SyncSqliteBoundaryAuthorityStatus::Current;
}

void rollback_sync_sqlite_savepoint_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db) return;
    if (!sync_process_incarnation_is_current(proof.process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    try {
        end_sync_sqlite_savepoint_boundary_or_throw(
            db,
            proof,
            SyncSqliteSavepointBoundaryEnd::Rollback,
            "typed savepoint destructor rollback");
    } catch (...) {
        // Never issue an unfenced fallback for a fenced mark. An out-of-order
        // destructor or replaced callback leaves the bridge generation live,
        // which blocks outer COMMIT until connection close rather than
        // rewinding across a newer mark or claiming authority over alien work.
    }
}

void rollback_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db) return;
    if (!sync_process_incarnation_is_current(proof.process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (!proof.fenced) {
        if (sqlite3_get_autocommit(db) == 0) {
            (void)sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
        }
        return;
    }

    try {
        end_sync_sqlite_transaction_boundary_or_throw(
            db,
            proof,
            SyncSqliteTransactionBoundaryEnd::Rollback,
            "typed transaction destructor rollback");
    } catch (...) {
        // Do not issue an unfenced fallback after bridge replacement. SQLite
        // exposes no transaction-generation identifier, so an alien callback
        // could already have ended this generation and started another one.
        // Rolling that later transaction back would be a false claim of
        // ownership. Connection close remains SQLite's final rollback fence.
        abandon_sync_sqlite_transaction_boundary_noexcept(db, proof);
    }
}

void abandon_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (db == nullptr || !proof.fenced || proof.db != db ||
        !sync_process_incarnation_is_current(proof.process_id) ||
        !sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation)) {
        return;
    }
    sqlite3_mutex* mutex = sqlite3_db_mutex(db);
    if (mutex == nullptr) return;
    sqlite3_mutex_enter(mutex);
    try {
        ConnectionAuthorityState* state =
            load_connection_authority_state_or_throw(
                db, true, "abandon typed transaction");
        if (state != nullptr &&
            state->process_id == proof.process_id &&
            state->process_salt == proof.process_salt &&
            state->connection_incarnation == proof.connection_incarnation &&
            state->authorizer_generation == proof.authorizer_generation &&
            state->active_transaction_generation == proof.transaction_generation &&
            sqlite3_get_autocommit(db) != 0) {
            state->active_transaction_generation = 0;
            state->active_savepoints.clear();
        }
    } catch (...) {
        // noexcept revocation is advisory; never cross a destructor boundary.
    }
    sqlite3_mutex_leave(mutex);
}

}  // namespace anonsync
