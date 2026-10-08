#pragma once

#include "sqlite_retained_callback_claim.hpp"

#include <string>

struct sqlite3;

namespace anonsync::persistence {

using SqliteAuthorizerCallback = int (*)(void*,
                                         int,
                                         const char*,
                                         const char*,
                                         const char*,
                                         const char*);

// Stable process-bound owner for SQLite's singleton authorizer callback slot.
//
// sqlite3_set_authorizer() retains both the callback and its context but offers
// neither a destructor nor a getter.  This owner therefore composes the shared
// connection client-data claim, makes replacement an explicit transition, and
// requires ordered callback revocation before the context address may die.
//
// Attach, replace, and detach internally hold the exact serialized connection
// mutex across each complete claim-and-setter transition. Thus simultaneous
// legitimate attach attempts resolve as one live owner and one ordinary
// rejection instead of replacing a pending claim. A broader enclosing
// connection authority may already hold the same recursive mutex; the guards
// compose without changing ownership. The enclosing authority must still keep
// the callback context alive for the complete attached lifetime and quiesce
// connection use before teardown.
class SqliteAuthorizerOwner final {
public:
    SqliteAuthorizerOwner() noexcept;
    ~SqliteAuthorizerOwner();

    SqliteAuthorizerOwner(const SqliteAuthorizerOwner&) = delete;
    SqliteAuthorizerOwner& operator=(const SqliteAuthorizerOwner&) = delete;
    SqliteAuthorizerOwner(SqliteAuthorizerOwner&&) = delete;
    SqliteAuthorizerOwner& operator=(SqliteAuthorizerOwner&&) = delete;

    void attach(sqlite3* database,
                SqliteAuthorizerCallback callback,
                void* callback_context,
                const std::string& label);

    // Deliberately supersede the singleton slot while retaining the same
    // connection-lifetime claim.  This also recovers from an alien raw setter
    // call without allowing the callback context to become unowned.
    void replace(sqlite3* database,
                 SqliteAuthorizerCallback callback,
                 void* callback_context,
                 const std::string& label);

    // Prove the connection-lifetime claim and the owner's frozen local shape.
    // SQLite exposes no authorizer getter, so exact callback identity remains a
    // use-time probe obligation of the enclosing authority protocol.
    void require_live(sqlite3* database) const noexcept;

    // Idempotent after successful detach.  The caller must have quiesced use of
    // the serialized connection.  The callback is disabled before the named
    // lifetime claim is released.
    void detach(sqlite3* database) noexcept;

    [[nodiscard]] bool attached() const noexcept;

private:
    void require_current_process_noexcept() const noexcept;
    void require_shape_noexcept() const noexcept;

    SyncProcessIncarnation process_id_;
    sqlite3* database_ = nullptr;
    SqliteAuthorizerCallback callback_ = nullptr;
    void* callback_context_ = nullptr;
    SqliteRetainedCallbackClaim callback_claim_;
};

}  // namespace anonsync::persistence
