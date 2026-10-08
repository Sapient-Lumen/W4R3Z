#include "sync_sqlite_connection_authority.hpp"

#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_mutex_capability.hpp"

#include <atomic>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

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

struct ConnectionAuthorityState final {
    std::uint64_t magic = kStateMagic;
    ConnectionAuthorityState* self = this;
    SyncSqliteProcessId process_id = current_sync_sqlite_process_id_noexcept();
    std::uint64_t process_salt = 0;
    std::uint64_t connection_incarnation = 0;
    std::uint64_t authorizer_generation = 0;
    SyncSqliteAuthorizerPolicy policy = nullptr;
    void* policy_context = nullptr;
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
    SyncSqliteProcessId process_id,
    SyncSqliteThreadIncarnation owner_thread_incarnation,
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept {
    if (mutex == nullptr) {
        return process_id == 0 && owner_thread_incarnation == 0 &&
               retained_capability_state == nullptr;
    }
    return process_id != 0 && owner_thread_incarnation != 0 &&
           retained_capability_state != nullptr;
}

void require_retained_mutex_lease_owner_noexcept(
    sqlite3_mutex* mutex,
    SyncSqliteProcessId process_id,
    SyncSqliteThreadIncarnation owner_thread_incarnation,
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept {
    if (!retained_mutex_lease_shape_is_valid(
            mutex, process_id, owner_thread_incarnation,
            retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (mutex == nullptr) return;
    if (!sync_sqlite_process_id_is_current(process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(owner_thread_incarnation) ||
        !sync_sqlite_mutex_capability_is_live_noexcept(
            retained_capability_state)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
}

class DbMutexGuard final {
public:
    DbMutexGuard(sqlite3* db, const std::string& label)
        : process_id_(current_sync_sqlite_process_id_noexcept()),
          owner_thread_incarnation_(
              current_sync_sqlite_thread_incarnation_noexcept()) {
        if (db == nullptr) {
            throw std::invalid_argument(label + " database handle is null");
        }
        mutex_ = sqlite3_db_mutex(db);
        if (mutex_ == nullptr) {
            throw std::runtime_error(
                label + " requires a serialized/FULLMUTEX SQLite connection");
        }
        sqlite3_mutex_enter(mutex_);
    }

    ~DbMutexGuard() {
        if (mutex_ == nullptr) return;
        if (!sync_sqlite_process_id_is_current(process_id_)) {
            fail_stop_on_sync_sqlite_capability_violation_noexcept();
        }
        if (!sync_sqlite_thread_incarnation_is_current(
                owner_thread_incarnation_)) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        sqlite3_mutex_leave(mutex_);
    }

    DbMutexGuard(const DbMutexGuard&) = delete;
    DbMutexGuard& operator=(const DbMutexGuard&) = delete;

    sqlite3_mutex* release() noexcept {
        if (mutex_ != nullptr &&
            !sync_sqlite_process_id_is_current(process_id_)) {
            fail_stop_on_sync_sqlite_capability_violation_noexcept();
        }
        if (mutex_ != nullptr &&
            !sync_sqlite_thread_incarnation_is_current(
                owner_thread_incarnation_)) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        sqlite3_mutex* out = mutex_;
        mutex_ = nullptr;
        return out;
    }

private:
    sqlite3_mutex* mutex_ = nullptr;
    SyncSqliteProcessId process_id_ = 0;
    SyncSqliteThreadIncarnation owner_thread_incarnation_ = 0;
};

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
            state_.transaction_permit != TransactionPermitOperation::None) {
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

void destroy_connection_authority_state(void* raw) noexcept {
    auto* state = static_cast<ConnectionAuthorityState*>(raw);
    if (state == nullptr) return;
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
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
        state->process_id == 0 || state->process_salt == 0 ||
        state->connection_incarnation == 0 ||
        state->authorizer_generation == 0) {
        throw std::runtime_error(
            label + " connection authority client-data slot is corrupt");
    }
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
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

int invoke_policy_or_deny(ConnectionAuthorityState& state,
                          int action,
                          const char* argument1,
                          const char* argument2,
                          const char* database_name,
                          const char* trigger_or_view,
                          bool ignore_is_valid) noexcept {
    if (state.policy == nullptr) return SQLITE_DENY;
    try {
        const int decision = state.policy(state.policy_context,
                                          action,
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
        state->self != state || state->process_id == 0) {
        return SQLITE_DENY;
    }
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
    if (state->probe_active) {
        state->observed_probe_nonce = state->probe_nonce;
        return SQLITE_OK;
    }

    // SAVEPOINT is also transaction-stack control: an outermost SAVEPOINT
    // starts a transaction and RELEASE of the outermost savepoint commits it.
    // Until a typed nested-scope API exists, every SAVEPOINT action is denied.
    if (action == SQLITE_SAVEPOINT) return SQLITE_DENY;

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

void run_authorizer_ownership_probe_or_throw(
    sqlite3* db,
    ConnectionAuthorityState& state,
    const std::string& label) {
    if (state.probe_active) {
        throw std::logic_error(label + " authorizer ownership probe is reentrant");
    }
    if (state.transaction_permit_active) {
        throw std::logic_error(
            label + " authorizer ownership probe crossed an armed transaction permit");
    }
    if (state.probe_nonce == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " exhausted authorizer probe nonces");
    }

    ++state.probe_nonce;
    state.observed_probe_nonce = 0;
    state.probe_active = true;

    sqlite3_stmt* statement = nullptr;
    static constexpr char kProbeSql[] = "SELECT 1;";
    const int prepare_rc = sqlite3_prepare_v3(db,
                                              kProbeSql,
                                              static_cast<int>(sizeof(kProbeSql) - 1),
                                              SQLITE_PREPARE_PERSISTENT,
                                              &statement,
                                              nullptr);
    state.probe_active = false;
    const std::uint64_t observed = state.observed_probe_nonce;
    const int finalize_rc = statement != nullptr ? sqlite3_finalize(statement)
                                                 : SQLITE_OK;

    const bool callback_observed = observed == state.probe_nonce;
    if (prepare_rc != SQLITE_OK) {
        if (!callback_observed && (prepare_rc & 0xff) == SQLITE_AUTH) {
            throw std::runtime_error(
                label +
                " authorizer ownership probe failed: callback was disabled, "
                "replaced, or did not observe the exact generation");
        }
        throw_sqlite_exception(
            db, prepare_rc, label + " prepare authorizer ownership probe");
    }
    if (!callback_observed) {
        throw std::runtime_error(
            label +
            " authorizer ownership probe failed: callback was disabled, replaced, "
            "or did not observe the exact generation");
    }
    if (statement == nullptr) {
        throw std::runtime_error(
            label + " authorizer ownership probe produced no statement");
    }
    if (finalize_rc != SQLITE_OK) {
        throw_sqlite_exception(
            db, finalize_rc, label + " finalize authorizer ownership probe");
    }
}

void execute_permitted_transaction_sql_or_throw(
    sqlite3* db,
    ConnectionAuthorityState& state,
    TransactionPermitOperation operation,
    const std::string& sql,
    const std::string& label) {
    TransactionPermitScope permit(state, operation, label);
    char* raw_error = nullptr;
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &raw_error);
    const bool observed = permit.observed();
    const std::string detail =
        raw_error != nullptr ? std::string(raw_error) : std::string();
    if (raw_error != nullptr) sqlite3_free(raw_error);

    if (rc != SQLITE_OK) {
        throw_sqlite_exception(db, rc, label, detail);
    }
    if (!observed) {
        throw std::runtime_error(
            label +
            " transaction boundary succeeded without consuming the exact "
            "authorizer permit");
    }
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
        proof.process_id == 0 || proof.process_salt == 0 ||
        proof.connection_incarnation == 0 ||
        proof.authorizer_generation == 0 || proof.transaction_generation == 0 ||
        proof.owner_thread_incarnation == 0 ||
        proof.retained_capability_state == nullptr) {
        throw std::logic_error(
            label + " transaction boundary proof is empty or targets another handle");
    }
    // Reject a fork child before touching SQLite-owned state, then reject a
    // foreign thread before inspecting the retained lifetime sentinel.
    require_sync_sqlite_process_id_or_fail_stop(
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
    }
}

}  // namespace

SyncSqliteConnectionAuthorityProof::SyncSqliteConnectionAuthorityProof(
    SyncSqliteProcessId process_id,
    std::uint64_t process_salt,
    std::uint64_t connection_incarnation,
    std::uint64_t authorizer_generation) noexcept
    : process_id_(process_id),
      process_salt_(process_salt),
      connection_incarnation_(connection_incarnation),
      authorizer_generation_(authorizer_generation),
      valid_(process_id != 0 && process_salt != 0 &&
             connection_incarnation != 0 && authorizer_generation != 0) {}

bool SyncSqliteConnectionAuthorityProof::valid() const noexcept {
    return valid_ && sync_sqlite_process_id_is_current(process_id_);
}

std::uint64_t
SyncSqliteConnectionAuthorityProof::authorizer_generation() const noexcept {
    return authorizer_generation_;
}

SyncSqliteConnectionAuthorityLease::SyncSqliteConnectionAuthorityLease(
    sqlite3_mutex* mutex,
    SyncSqliteProcessId process_id,
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
    other.process_id_ = 0;
    other.owner_thread_incarnation_ = 0;
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
    other.process_id_ = 0;
    other.owner_thread_incarnation_ = 0;
    other.retained_capability_state_ = nullptr;
    return *this;
}

bool SyncSqliteConnectionAuthorityLease::active() const noexcept {
    return retained_mutex_lease_shape_is_valid(
               mutex_, process_id_, owner_thread_incarnation_,
               retained_capability_state_) &&
           mutex_ != nullptr &&
           sync_sqlite_process_id_is_current(process_id_) &&
           sync_sqlite_thread_incarnation_is_current(
               owner_thread_incarnation_) &&
           sync_sqlite_mutex_capability_is_live_noexcept(
               retained_capability_state_);
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
    DbMutexGuard guard(db, label + " connection authority install");
    ConnectionAuthorityState* state =
        load_connection_authority_state_or_throw(db, true, label);

    if (state != nullptr) {
        clear_stale_transaction_generation_if_ended(db, *state);
        if (state->transaction_permit_active) {
            throw std::logic_error(
                label + " cannot replace authority while a boundary permit is armed");
        }
        if (state->active_transaction_generation != 0 ||
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
        state->policy = policy;
        state->policy_context = policy_context;

        // With a non-null destructor SQLite assumes ownership even when this
        // call reports SQLITE_NOMEM; do not retain a second C++ owner.
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

        const int authorizer_rc =
            sqlite3_set_authorizer(db, connection_authorizer_bridge, state);
        if (authorizer_rc != SQLITE_OK) {
            // set_authorizer did not accept the new callback. Clearing the
            // client data is safe because no installed callback refers to it.
            (void)sqlite3_set_clientdata(
                db, kConnectionAuthorityClientDataName, nullptr, nullptr);
            throw_sqlite_exception(db,
                                   authorizer_rc,
                                   label + " install owned authorizer bridge");
        }
    } else {
        if (state->authorizer_generation ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(
                label + " exhausted SQLite authorizer generations");
        }
        const int authorizer_rc =
            sqlite3_set_authorizer(db, connection_authorizer_bridge, state);
        if (authorizer_rc != SQLITE_OK) {
            throw_sqlite_exception(db,
                                   authorizer_rc,
                                   label + " supersede SQLite authorizer bridge");
        }
        state->policy = policy;
        state->policy_context = policy_context;
        ++state->authorizer_generation;
    }

    run_authorizer_ownership_probe_or_throw(db, *state, label);
    return SyncSqliteConnectionAuthorityProof(state->process_id,
                                               state->process_salt,
                                               state->connection_incarnation,
                                               state->authorizer_generation);
}

SyncSqliteConnectionAuthorityLease
acquire_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    const SyncSqliteConnectionAuthorityProof& proof,
    const std::string& label) {
    if (!proof.valid_) {
        throw std::invalid_argument(label + " connection authority proof is empty");
    }
    require_sync_sqlite_process_id_or_fail_stop(
        proof.process_id_, label + " connection authority proof");
    DbMutexGuard guard(db, label + " connection authority acquire");
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

bool sync_sqlite_connection_authority_state_present_or_throw(
    sqlite3* db,
    const std::string& label) {
    DbMutexGuard guard(db, label + " connection authority presence");
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
    DbMutexGuard guard(db, label + " typed transaction begin");
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
        proof.process_id = current_sync_sqlite_process_id_noexcept();
        proof.owner_thread_incarnation =
            current_sync_sqlite_thread_incarnation_noexcept();
        proof.retained_connection_mutex = guard.release();
        proof.retained_capability_state = retained_capability.release();
        return proof;
    }

    clear_stale_transaction_generation_if_ended(db, *state);
    if (state->active_transaction_generation != 0) {
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
        }
        throw;
    }
    if (sqlite3_get_autocommit(db) != 0) {
        state->active_transaction_generation = 0;
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

void end_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof,
    SyncSqliteTransactionBoundaryEnd operation,
    const std::string& label) {
    require_sync_sqlite_process_id_or_fail_stop(
        proof.process_id, label + " transaction boundary");
    require_sync_sqlite_thread_incarnation_or_throw(
        proof.owner_thread_incarnation, label + " transaction boundary");
    DbMutexGuard guard(db, label + " typed transaction end");
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
        throw std::logic_error(
            label + " exact typed transaction boundary is no longer active");
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
        }
        throw;
    }

    if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(
            label + " returned success without restoring SQLite autocommit");
    }
    state.active_transaction_generation = 0;
}

void release_sync_sqlite_transaction_mutex_noexcept(
    SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (proof.retained_connection_mutex == nullptr) {
        if (proof.retained_capability_state != nullptr) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        return;
    }
    if (!sync_sqlite_process_id_is_current(proof.process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
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

bool sync_sqlite_transaction_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db ||
        !sync_sqlite_process_id_is_current(proof.process_id) ||
        !sync_sqlite_thread_incarnation_is_current(
            proof.owner_thread_incarnation) ||
        !sync_sqlite_mutex_capability_is_live_noexcept(
            proof.retained_capability_state)) {
        return false;
    }
    if (!proof.fenced) return sqlite3_get_autocommit(db) == 0;

    sqlite3_mutex* mutex = sqlite3_db_mutex(db);
    if (mutex == nullptr) return false;
    sqlite3_mutex_enter(mutex);
    bool current = false;
    try {
        ConnectionAuthorityState& state =
            validate_boundary_proof_or_throw(
                db, proof, "validate typed transaction authority");
        if (sqlite3_get_autocommit(db) == 0) {
            run_authorizer_ownership_probe_or_throw(
                db, state, "validate typed transaction authority");
            current = true;
        } else {
            state.active_transaction_generation = 0;
        }
    } catch (...) {
        current = false;
    }
    sqlite3_mutex_leave(mutex);
    return current;
}

void rollback_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept {
    if (db == nullptr || proof.db != db) return;
    if (!sync_sqlite_process_id_is_current(proof.process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
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
        !sync_sqlite_process_id_is_current(proof.process_id) ||
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
        }
    } catch (...) {
        // noexcept revocation is advisory; never cross a destructor boundary.
    }
    sqlite3_mutex_leave(mutex);
}

}  // namespace anonsync
