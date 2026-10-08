#pragma once

#include <cstdint>
#include <string>

#include "sync_sqlite_mutex_capability.hpp"
#include "sync_sqlite_owned_authorizer_policy.hpp"

struct sqlite3;
struct sqlite3_mutex;

namespace anonsync {

class SyncSqliteConnectionAuthorityLease;
struct SyncSqliteRetainedMutexCapabilityState;

// Process-local evidence for one logical SQLite connection lifetime and one
// exact authorizer installation. It is intentionally not serializable:
// restart authority must be reconstructed from durable domain evidence.
class SyncSqliteConnectionAuthorityProof final {
public:
    SyncSqliteConnectionAuthorityProof() = default;

    [[nodiscard]] bool valid() const noexcept;
    [[nodiscard]] std::uint64_t authorizer_generation() const noexcept;

private:
    SyncProcessIncarnation process_id_;
    std::uint64_t process_salt_ = 0;
    std::uint64_t connection_incarnation_ = 0;
    std::uint64_t authorizer_generation_ = 0;
    bool valid_ = false;

    SyncSqliteConnectionAuthorityProof(SyncProcessIncarnation process_id,
                                       std::uint64_t process_salt,
                                       std::uint64_t connection_incarnation,
                                       std::uint64_t authorizer_generation) noexcept;

    friend SyncSqliteConnectionAuthorityProof
    install_sync_sqlite_connection_authority_or_throw(
        sqlite3*, SyncSqliteOwnedAuthorizerPolicy, const std::string&);
    friend SyncSqliteConnectionAuthorityProof
    install_sync_sqlite_connection_authority_or_throw(
        sqlite3*, SyncSqliteAuthorizerPolicy, void*, const std::string&);
    friend class SyncSqliteConnectionAuthorityLease;
    friend SyncSqliteConnectionAuthorityLease
    acquire_sync_sqlite_connection_authority_or_throw(
        sqlite3*, const SyncSqliteConnectionAuthorityProof&, const std::string&);
};

// Exclusive use-time lease over a FULLMUTEX SQLite connection. Acquisition
// proves that SQLite still carries the exact client-data incarnation and that
// preparing SQL reaches the exact AnonSync authorizer bridge. Keep this object
// alive through statement preparation, stepping, and transaction completion.
// The retained recursive mutex is bound to the exact acquiring C++ thread
// incarnation. Observing active() elsewhere fails closed; moving or destroying
// a live lease elsewhere fails stopped: use on the wrong thread terminates
// before invoking SQLite undefined behavior by leaving another thread's
// mutex entry.
class SyncSqliteConnectionAuthorityLease final {
public:
    SyncSqliteConnectionAuthorityLease() = default;
    ~SyncSqliteConnectionAuthorityLease();
    SyncSqliteConnectionAuthorityLease(
        const SyncSqliteConnectionAuthorityLease&) = delete;
    SyncSqliteConnectionAuthorityLease& operator=(
        const SyncSqliteConnectionAuthorityLease&) = delete;
    SyncSqliteConnectionAuthorityLease(
        SyncSqliteConnectionAuthorityLease&& other) noexcept;
    SyncSqliteConnectionAuthorityLease& operator=(
        SyncSqliteConnectionAuthorityLease&& other) noexcept;

    [[nodiscard]] bool active() const noexcept;

private:
    sqlite3_mutex* mutex_ = nullptr;
    SyncProcessIncarnation process_id_;
    SyncSqliteThreadIncarnation owner_thread_incarnation_;
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state_ = nullptr;

    SyncSqliteConnectionAuthorityLease(
        sqlite3_mutex* mutex,
        SyncProcessIncarnation process_id,
        SyncSqliteThreadIncarnation owner_thread_incarnation,
        SyncSqliteRetainedMutexCapabilityState* retained_capability_state) noexcept;

    friend SyncSqliteConnectionAuthorityLease
    acquire_sync_sqlite_connection_authority_or_throw(
        sqlite3*, const SyncSqliteConnectionAuthorityProof&, const std::string&);
};

// Installs (or deliberately supersedes) the AnonSync bridge on one serialized
// connection. The first install creates SQLite-owned client data whose
// destructor runs at close; later installs advance the generation without
// replacing the state object, avoiding a dangling callback window.  The
// move-only policy owner retains optional application context through the exact
// installed generation. Replaced or revoked context is released only after the
// callback is detached and SQLite's connection mutex has been left.
[[nodiscard]] SyncSqliteConnectionAuthorityProof
install_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    SyncSqliteOwnedAuthorizerPolicy policy,
    const std::string& label);

// Compatibility lane for context-free policies. A non-null raw context is no
// longer accepted because SQLite could retain it beyond its external owner;
// use the owned-policy overload instead.
[[nodiscard]] SyncSqliteConnectionAuthorityProof
install_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    SyncSqliteAuthorizerPolicy policy,
    void* policy_context,
    const std::string& label);

// Acquires the connection mutex, checks incarnation and generation, and runs
// a prepare-time callback challenge. The returned lease retains the mutex.
[[nodiscard]] SyncSqliteConnectionAuthorityLease
acquire_sync_sqlite_connection_authority_or_throw(
    sqlite3* db,
    const SyncSqliteConnectionAuthorityProof& proof,
    const std::string& label);

}  // namespace anonsync
