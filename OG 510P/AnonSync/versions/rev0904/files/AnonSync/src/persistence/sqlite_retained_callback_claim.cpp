#include "sqlite_retained_callback_claim.hpp"

#include <sqlite3.h>

#include <atomic>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync::persistence {
namespace {

static_assert(SQLITE_VERSION_NUMBER >= 3044000,
              "SQLite connection client data requires SQLite 3.44.0+");

[[noreturn]] void fail_stop_on_retained_callback_lifetime_violation_noexcept()
    noexcept {
    fail_stop_on_sync_process_capability_violation_noexcept();
}

std::runtime_error client_data_error(sqlite3* database,
                                     int result_code,
                                     const std::string& label,
                                     std::string_view owner_kind) {
    const char* detail = database == nullptr ? nullptr : sqlite3_errmsg(database);
    if (detail == nullptr || *detail == '\0') detail = sqlite3_errstr(result_code);
    return std::runtime_error(
        label + " could not claim SQLite " + std::string(owner_kind) +
        " callback lifetime: " +
        (detail == nullptr ? "SQLite error" : detail));
}

}  // namespace

struct SqliteRetainedCallbackClaim::ClaimState final {
    enum class State : std::uint8_t {
        registration_pending = 0,
        live = 1,
        detaching = 2,
    };

    static constexpr std::uint64_t kMagic = UINT64_C(0x41534E535243434C);

    explicit ClaimState(SyncProcessIncarnation process_id_value) noexcept
        : process_id(process_id_value) {}

    const std::uint64_t magic = kMagic;
    ClaimState* const self = this;
    const SyncProcessIncarnation process_id;
    static_assert(std::atomic<State>::is_always_lock_free,
                  "retained callback claim state must remain lock-free after fork");
    std::atomic<State> state{State::registration_pending};
};

namespace {

// sqlite3_set_clientdata() may invoke the destructor synchronously on
// allocation failure, replacement, or explicit clearing.  A transient state
// bit alone is not authority for a racing close/replacement on another thread.
// Only the exact thread executing the reviewed set_clientdata call may destroy
// this exact claim in registration_pending or detaching state.
thread_local void* g_authorized_retained_claim_destruction = nullptr;

class ScopedAuthorizedRetainedClaimDestruction final {
public:
    explicit ScopedAuthorizedRetainedClaimDestruction(
        void* claim) noexcept
        : claim_(claim) {
        if (claim_ == nullptr ||
            g_authorized_retained_claim_destruction != nullptr) {
            fail_stop_on_retained_callback_lifetime_violation_noexcept();
        }
        g_authorized_retained_claim_destruction = claim_;
    }

    ~ScopedAuthorizedRetainedClaimDestruction() {
        if (g_authorized_retained_claim_destruction != claim_) {
            fail_stop_on_retained_callback_lifetime_violation_noexcept();
        }
        g_authorized_retained_claim_destruction = nullptr;
    }

    ScopedAuthorizedRetainedClaimDestruction(
        const ScopedAuthorizedRetainedClaimDestruction&) = delete;
    ScopedAuthorizedRetainedClaimDestruction& operator=(
        const ScopedAuthorizedRetainedClaimDestruction&) = delete;

private:
    void* claim_ = nullptr;
};

}  // namespace

SqliteRetainedCallbackClaim::SqliteRetainedCallbackClaim() noexcept
    : process_id_(current_sync_process_incarnation_noexcept()) {}

SqliteRetainedCallbackClaim::~SqliteRetainedCallbackClaim() {
    require_current_process_noexcept();
    if (claim_state_ != nullptr || !client_data_name_.empty()) {
        // Auto-detach would touch an address that may already have been closed.
        // The enclosing callback owner must run its ordered detach protocol.
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
}

void SqliteRetainedCallbackClaim::attach(
    sqlite3* database,
    const SyncSqliteDatabaseMutexGuard& mutex_guard,
    std::string_view client_data_name,
    const std::string& label,
    std::string_view owner_kind) {
    require_current_process_noexcept();
    if (claim_state_ != nullptr || !client_data_name_.empty()) {
        throw std::logic_error(
            "SQLite retained callback claim is already attached");
    }
    if (database == nullptr) {
        throw std::invalid_argument(
            "SQLite retained callback claim requires an open database handle");
    }
    if (!mutex_guard.authorizes(database)) {
        throw std::logic_error(
            label +
            " requires the exact serialized database-mutex guard before claiming a retained callback slot");
    }
    if (client_data_name.empty() ||
        client_data_name.find('\0') != std::string_view::npos ||
        owner_kind.empty()) {
        throw std::invalid_argument(
            "SQLite retained callback claim requires a nonempty NUL-free name and owner identity");
    }

    // Freeze every allocating C++ value before publishing any member state.
    // In particular, a ClaimState allocation failure must leave this object
    // ordinarily destructible rather than looking like a half-attached owner.
    std::string frozen_client_data_name(client_data_name);
    if (sqlite3_get_clientdata(
            database, frozen_client_data_name.c_str()) != nullptr) {
        throw std::logic_error(
            label + " already has an AnonSync SQLite " +
            std::string(owner_kind));
    }

    auto pending = std::make_unique<ClaimState>(process_id_);
    client_data_name_.swap(frozen_client_data_name);
    ClaimState* const claim = pending.release();
    int result = SQLITE_ERROR;
    {
        ScopedAuthorizedRetainedClaimDestruction authorized(claim);
        result = sqlite3_set_clientdata(
            database,
            client_data_name_.c_str(),
            claim,
            &SqliteRetainedCallbackClaim::destroy_claim_state);
    }
    if (result != SQLITE_OK) {
        // SQLite destroys claim on registration allocation failure.
        client_data_name_.clear();
        throw client_data_error(database, result, label, owner_kind);
    }

    claim->state.store(ClaimState::State::live, std::memory_order_release);
    claim_state_ = claim;
}

void SqliteRetainedCallbackClaim::require_live(
    sqlite3* database,
    const SyncSqliteDatabaseMutexGuard& mutex_guard) const noexcept {
    require_current_process_noexcept();
    if (!mutex_guard.authorizes(database)) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
    ClaimState* const claim = claim_state_;
    if (database == nullptr || claim == nullptr || client_data_name_.empty() ||
        claim->magic != ClaimState::kMagic || claim->self != claim ||
        claim->process_id != process_id_ ||
        claim->state.load(std::memory_order_acquire) !=
            ClaimState::State::live ||
        sqlite3_get_clientdata(database, client_data_name_.c_str()) != claim) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
}

void SqliteRetainedCallbackClaim::detach(
    sqlite3* database,
    const SyncSqliteDatabaseMutexGuard& mutex_guard) noexcept {
    require_current_process_noexcept();
    if (claim_state_ == nullptr) {
        if (!client_data_name_.empty()) {
            fail_stop_on_retained_callback_lifetime_violation_noexcept();
        }
        return;
    }

    require_live(database, mutex_guard);
    ClaimState* const claim = claim_state_;
    claim->state.store(ClaimState::State::detaching,
                       std::memory_order_release);
    int result = SQLITE_ERROR;
    {
        ScopedAuthorizedRetainedClaimDestruction authorized(claim);
        result = sqlite3_set_clientdata(
            database, client_data_name_.c_str(), nullptr, nullptr);
    }
    if (result != SQLITE_OK) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }

    // The synchronous client-data destructor deleted claim.
    claim_state_ = nullptr;
    client_data_name_.clear();
}

bool SqliteRetainedCallbackClaim::attached() const noexcept {
    require_current_process_noexcept();
    const bool has_state = claim_state_ != nullptr;
    if (has_state != !client_data_name_.empty()) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
    return has_state;
}

void SqliteRetainedCallbackClaim::destroy_claim_state(void* context) noexcept {
    auto* const claim = static_cast<ClaimState*>(context);
    if (claim == nullptr || claim->magic != ClaimState::kMagic ||
        claim->self != claim || !claim->process_id.valid() ||
        !sync_process_incarnation_is_current(claim->process_id)) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }

    const ClaimState::State state =
        claim->state.load(std::memory_order_acquire);
    if (state == ClaimState::State::live) {
        // SQLite is actually destroying the handle or replacing this named
        // slot before the enclosing C++ owner revoked the retained callback
        // address. A close_v2 zombie does not reach this destructor until its
        // final dependent SQLite object is released.
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
    if ((state != ClaimState::State::registration_pending &&
         state != ClaimState::State::detaching) ||
        g_authorized_retained_claim_destruction != claim) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }

    delete claim;
}

void SqliteRetainedCallbackClaim::require_current_process_noexcept() const
    noexcept {
    if (!process_id_.valid() ||
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_retained_callback_lifetime_violation_noexcept();
    }
}

}  // namespace anonsync::persistence
