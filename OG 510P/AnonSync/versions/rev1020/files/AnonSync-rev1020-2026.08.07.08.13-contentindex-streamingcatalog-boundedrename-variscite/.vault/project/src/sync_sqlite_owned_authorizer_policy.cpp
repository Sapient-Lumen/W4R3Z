#include "sync_sqlite_owned_authorizer_policy.hpp"

#include <stdexcept>
#include <utility>

namespace anonsync {
namespace {

[[noreturn]] void fail_stop_on_authorizer_policy_lifetime_violation_noexcept()
    noexcept {
    fail_stop_on_sync_process_capability_violation_noexcept();
}

}  // namespace

SyncSqliteOwnedAuthorizerPolicy::SyncSqliteOwnedAuthorizerPolicy() noexcept
    : process_id_(current_sync_process_incarnation_noexcept()) {}

SyncSqliteOwnedAuthorizerPolicy::SyncSqliteOwnedAuthorizerPolicy(
    SyncSqliteAuthorizerPolicy policy)
    : process_id_(current_sync_process_incarnation_noexcept()),
      context_free_policy_(policy) {
    if (context_free_policy_ == nullptr) {
        throw std::invalid_argument("SQLite authorizer policy is null");
    }
    require_shape_noexcept();
}

SyncSqliteOwnedAuthorizerPolicy::SyncSqliteOwnedAuthorizerPolicy(
    TypedFactoryTag,
    std::unique_ptr<TypedPolicyCapsule> typed_policy_capsule) noexcept
    : process_id_(current_sync_process_incarnation_noexcept()),
      typed_policy_capsule_(std::move(typed_policy_capsule)) {
    require_shape_noexcept();
}

SyncSqliteOwnedAuthorizerPolicy::~SyncSqliteOwnedAuthorizerPolicy() {
    // Validate before typed_policy_capsule_ reaches its implicit destructor. A
    // foreign-process owner exits here, so no inherited unique_ptr, virtual
    // destructor, shared_ptr reference count, or custom deleter is touched.
    require_current_process_noexcept();
    require_shape_noexcept();
}

SyncSqliteOwnedAuthorizerPolicy::SyncSqliteOwnedAuthorizerPolicy(
    SyncSqliteOwnedAuthorizerPolicy&& other) noexcept
    : process_id_(current_sync_process_incarnation_noexcept()) {
    // Source-first validation is essential: do not even move the capsule out of
    // an inherited owner before rejecting the capability.
    other.require_current_process_noexcept();
    other.require_shape_noexcept();
    context_free_policy_ = other.context_free_policy_;
    typed_policy_capsule_ = std::move(other.typed_policy_capsule_);
    other.context_free_policy_ = nullptr;
    require_shape_noexcept();
    other.require_shape_noexcept();
}

bool SyncSqliteOwnedAuthorizerPolicy::valid() const noexcept {
    require_current_process_noexcept();
    require_shape_noexcept();
    return context_free_policy_ != nullptr || typed_policy_capsule_ != nullptr;
}

bool SyncSqliteOwnedAuthorizerPolicy::empty() const noexcept {
    return !valid();
}

bool SyncSqliteOwnedAuthorizerPolicy::owns_context() const noexcept {
    require_current_process_noexcept();
    require_shape_noexcept();
    return typed_policy_capsule_ != nullptr;
}

int SyncSqliteOwnedAuthorizerPolicy::invoke(
    int action,
    const char* argument1,
    const char* argument2,
    const char* database_name,
    const char* trigger_or_view) const {
    require_current_process_noexcept();
    require_shape_noexcept();
    if (typed_policy_capsule_ != nullptr) {
        return typed_policy_capsule_->invoke(action,
                                             argument1,
                                             argument2,
                                             database_name,
                                             trigger_or_view);
    }
    if (context_free_policy_ == nullptr) {
        throw std::logic_error("SQLite authorizer policy owner is empty");
    }
    return context_free_policy_(nullptr,
                                action,
                                argument1,
                                argument2,
                                database_name,
                                trigger_or_view);
}

void SyncSqliteOwnedAuthorizerPolicy::swap(
    SyncSqliteOwnedAuthorizerPolicy& other) noexcept {
    require_current_process_noexcept();
    other.require_current_process_noexcept();
    require_shape_noexcept();
    other.require_shape_noexcept();
    if (this == &other) return;

    using std::swap;
    swap(context_free_policy_, other.context_free_policy_);
    typed_policy_capsule_.swap(other.typed_policy_capsule_);
    require_shape_noexcept();
    other.require_shape_noexcept();
}

void SyncSqliteOwnedAuthorizerPolicy::require_current_process_noexcept() const
    noexcept {
    if (!process_id_.valid() ||
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_authorizer_policy_lifetime_violation_noexcept();
    }
}

void SyncSqliteOwnedAuthorizerPolicy::require_shape_noexcept() const noexcept {
    const bool empty = context_free_policy_ == nullptr &&
                       typed_policy_capsule_ == nullptr;
    const bool context_free = context_free_policy_ != nullptr &&
                              typed_policy_capsule_ == nullptr;
    const bool typed = context_free_policy_ == nullptr &&
                       typed_policy_capsule_ != nullptr;
    if (!empty && !context_free && !typed) {
        fail_stop_on_authorizer_policy_lifetime_violation_noexcept();
    }
}

}  // namespace anonsync
