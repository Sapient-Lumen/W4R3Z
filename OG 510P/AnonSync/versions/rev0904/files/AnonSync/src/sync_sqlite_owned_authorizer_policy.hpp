#pragma once

#include "sync_process_incarnation.hpp"

#include <concepts>
#include <functional>
#include <memory>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace anonsync {

// Context-free compatibility callback invoked by the owned SQLite authorizer
// bridge. SQLite retains only the bridge and its stable connection-state
// context; arbitrary application policy state is retained separately by the
// process-bound owner below.
using SyncSqliteAuthorizerPolicy = int (*)(void*,
                                           int,
                                           const char*,
                                           const char*,
                                           const char*,
                                           const char*);

namespace detail {

template <auto Policy>
inline constexpr bool sync_sqlite_policy_value_is_supported = [] {
    using PolicyType = std::remove_cv_t<decltype(Policy)>;
    if constexpr (std::is_pointer_v<PolicyType>) {
        return std::is_function_v<std::remove_pointer_t<PolicyType>> &&
               Policy != nullptr;
    }
    if constexpr (std::is_class_v<PolicyType>) {
        // Noncapturing lambdas and deliberately stateless structural adapters
        // are empty class types. Reject compile-time state here rather than
        // creating a second, less visible policy-context channel.
        return std::is_empty_v<PolicyType>;
    }
    return false;
}();

// A typed authorizer adapter receives one exact Context reference, the SQLite
// action code, and the four SQLite text arguments. Require an exact int result:
// accidentally returning bool or another merely-convertible type would hide a
// policy ABI mistake behind an implicit conversion. Const context is supported;
// volatile and array context are deliberately rejected because their ownership
// and invocation semantics are not part of this boundary contract.
template <typename Context, auto Policy>
concept SyncSqliteTypedAuthorizerPolicyFor =
    std::is_object_v<Context> && !std::is_array_v<Context> &&
    !std::is_volatile_v<Context> &&
    sync_sqlite_policy_value_is_supported<Policy> &&
    requires(Context& context,
             int action,
             const char* argument1,
             const char* argument2,
             const char* database_name,
             const char* trigger_or_view) {
        {
            std::invoke(Policy,
                        context,
                        action,
                        argument1,
                        argument2,
                        database_name,
                        trigger_or_view)
        } -> std::same_as<int>;
    };

}  // namespace detail

// Move-only process-local ownership for one authorizer policy and its optional
// shared context. Context-bearing policies can be created only through the
// constrained typed factory below: callback/context agreement is established at
// compile time before a single type-erased capsule enters the non-templated
// connection authority. The capsule owns both invocation behavior and the exact
// shared_ptr<T>; there is no public or internal shared_ptr<void>/cast pairing.
//
// A nonempty context is held by shared ownership so a caller can deliberately
// share immutable or synchronized policy state, but the connection authority
// always owns one independent lifetime reference. Const context, aliasing
// shared_ptr values, and custom deleters are supported. The exact stored pointer
// and complete control block stay together inside one typed capsule through
// movement, replacement, retirement, and destruction.
//
// The class is fork-sensitive: invoking, moving, swapping, inspecting, or
// destroying an instance inherited from another process fails stopped before
// its capsule or shared_ptr control block can be touched. This protects the
// parent-side ownership protocol from copied post-fork teardown paths. A new
// owner binds to the process that constructs it; the factory cannot prove that
// an arbitrary supplied shared_ptr control block was itself created in that
// process, so callers must not re-wrap inherited shared ownership after fork.
//
// Custom context deleters are application code. The connection-authority state
// machine therefore swaps retired policies into an ordinary C++ owner and
// releases them only after leaving SQLite's connection mutex and after revoking
// SQLite's retained authorizer callback.
class SyncSqliteOwnedAuthorizerPolicy final {
public:
    SyncSqliteOwnedAuthorizerPolicy() noexcept;

    // Context-free compatibility lane. Non-null application context must use
    // make_sync_sqlite_owned_authorizer_policy<Policy>(shared_ptr<T>).
    explicit SyncSqliteOwnedAuthorizerPolicy(
        SyncSqliteAuthorizerPolicy policy);
    ~SyncSqliteOwnedAuthorizerPolicy();

    SyncSqliteOwnedAuthorizerPolicy(
        const SyncSqliteOwnedAuthorizerPolicy&) = delete;
    SyncSqliteOwnedAuthorizerPolicy& operator=(
        const SyncSqliteOwnedAuthorizerPolicy&) = delete;
    SyncSqliteOwnedAuthorizerPolicy(
        SyncSqliteOwnedAuthorizerPolicy&& other) noexcept;
    SyncSqliteOwnedAuthorizerPolicy& operator=(
        SyncSqliteOwnedAuthorizerPolicy&&) = delete;

    [[nodiscard]] bool valid() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] bool owns_context() const noexcept;

    int invoke(int action,
               const char* argument1,
               const char* argument2,
               const char* database_name,
               const char* trigger_or_view) const;

    // Both participants must belong to the current process. The process proof
    // itself is not swapped: it describes each C++ owner object's provenance,
    // while the callback and context move as one policy capability.
    void swap(SyncSqliteOwnedAuthorizerPolicy& other) noexcept;

    template <auto Policy, typename Context>
        requires detail::SyncSqliteTypedAuthorizerPolicyFor<Context, Policy>
    [[nodiscard]] static SyncSqliteOwnedAuthorizerPolicy from_shared(
        std::shared_ptr<Context> context_owner) {
        if (context_owner == nullptr) {
            throw std::invalid_argument(
                "typed SQLite authorizer policy requires a non-null shared context");
        }
        auto capsule =
            std::make_unique<TypedPolicyCapsuleModel<Context, Policy>>(
                std::move(context_owner));
        return SyncSqliteOwnedAuthorizerPolicy(TypedFactoryTag{},
                                                std::move(capsule));
    }

private:
    class TypedPolicyCapsule {
    public:
        TypedPolicyCapsule() = default;
        virtual ~TypedPolicyCapsule() = default;
        TypedPolicyCapsule(const TypedPolicyCapsule&) = delete;
        TypedPolicyCapsule& operator=(const TypedPolicyCapsule&) = delete;

        virtual int invoke(int action,
                           const char* argument1,
                           const char* argument2,
                           const char* database_name,
                           const char* trigger_or_view) const = 0;
    };

    template <typename Context, auto Policy>
        requires detail::SyncSqliteTypedAuthorizerPolicyFor<Context, Policy>
    class TypedPolicyCapsuleModel final : public TypedPolicyCapsule {
    public:
        explicit TypedPolicyCapsuleModel(
            std::shared_ptr<Context> context_owner) noexcept
            : context_owner_(std::move(context_owner)) {}

        int invoke(int action,
                   const char* argument1,
                   const char* argument2,
                   const char* database_name,
                   const char* trigger_or_view) const override {
            return std::invoke(Policy,
                               *context_owner_,
                               action,
                               argument1,
                               argument2,
                               database_name,
                               trigger_or_view);
        }

    private:
        std::shared_ptr<Context> context_owner_;
    };

    struct TypedFactoryTag final {};

    SyncSqliteOwnedAuthorizerPolicy(
        TypedFactoryTag,
        std::unique_ptr<TypedPolicyCapsule> typed_policy_capsule) noexcept;

    void require_current_process_noexcept() const noexcept;
    void require_shape_noexcept() const noexcept;

    SyncProcessIncarnation process_id_;
    SyncSqliteAuthorizerPolicy context_free_policy_ = nullptr;
    std::unique_ptr<TypedPolicyCapsule> typed_policy_capsule_;
};

// Public context-bearing construction edge. Policy may be a function pointer or
// a C++20 structural noncapturing callable used as a non-type template argument.
// Context is deduced from the shared_ptr, so a mismatched callback/context pair
// is not a viable overload. The factory deliberately accepts shared_ptr<T> by
// value to preserve aliasing pointers and custom control blocks exactly.
template <auto Policy, typename Context>
    requires detail::SyncSqliteTypedAuthorizerPolicyFor<Context, Policy>
[[nodiscard]] SyncSqliteOwnedAuthorizerPolicy
make_sync_sqlite_owned_authorizer_policy(
    std::shared_ptr<Context> context_owner) {
    return SyncSqliteOwnedAuthorizerPolicy::from_shared<Policy>(
        std::move(context_owner));
}

}  // namespace anonsync
