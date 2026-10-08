#pragma once

#include <string_view>

namespace anonsync::persistence {

// SQLite retains one callback pointer per connection for each of these API
// families. The client-data names are therefore protocol identifiers, not
// local implementation details: alternate setters and close paths must query
// the same exact spelling before they can safely mutate a retained slot.
inline constexpr char kSqliteBusyHandlerOwnerClientDataName[] =
    "anonsync.sqlite-busy-handler-owner.v1";
inline constexpr char kSqliteVerificationBudgetClientDataName[] =
    "anonsync.sqlite-verification-budget.v1";
inline constexpr char kSqliteAuthorizerOwnerClientDataName[] =
    "anonsync.sqlite.authorizer-owner.v1";

static_assert(
    std::string_view(kSqliteBusyHandlerOwnerClientDataName) !=
        std::string_view(kSqliteVerificationBudgetClientDataName) &&
    std::string_view(kSqliteBusyHandlerOwnerClientDataName) !=
        std::string_view(kSqliteAuthorizerOwnerClientDataName) &&
    std::string_view(kSqliteVerificationBudgetClientDataName) !=
        std::string_view(kSqliteAuthorizerOwnerClientDataName),
    "retained SQLite callback owners require distinct client-data slots");

}  // namespace anonsync::persistence
