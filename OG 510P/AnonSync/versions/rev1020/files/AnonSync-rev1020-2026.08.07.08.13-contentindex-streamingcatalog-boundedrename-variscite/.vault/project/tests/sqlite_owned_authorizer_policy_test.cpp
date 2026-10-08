#include "sync_sqlite_owned_authorizer_policy.hpp"

#if defined(__unix__) || defined(__APPLE__)
#include "inherited_test_process.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

namespace {

using anonsync::SyncSqliteAuthorizerPolicy;
using anonsync::SyncSqliteOwnedAuthorizerPolicy;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::make_sync_sqlite_owned_authorizer_policy;

#if defined(__unix__) || defined(__APPLE__)
using anonsync::test::spawn_inherited_test_process_or_throw;
using namespace std::chrono_literals;
#endif

struct PolicyState final {
    std::uint64_t calls = 0;
    int last_action = 0;
    int decision = 0;

    int member_policy(int,
                      const char*,
                      const char*,
                      const char*,
                      const char*) noexcept {
        return decision;
    }
};

struct WrongPolicyState final {
    int decision = 0;
};

struct ReadOnlyPolicyState final {
    int decision = 0;
};

int counting_policy(PolicyState& state,
                    int action,
                    const char*,
                    const char*,
                    const char*,
                    const char*) noexcept {
    ++state.calls;
    state.last_action = action;
    return state.decision;
}

bool wrong_result_policy(PolicyState&,
                         int,
                         const char*,
                         const char*,
                         const char*,
                         const char*) noexcept {
    return true;
}

int read_only_policy(const ReadOnlyPolicyState& state,
                     int,
                     const char*,
                     const char*,
                     const char*,
                     const char*) noexcept {
    return state.decision;
}

struct StatefulPolicyAdapter final {
    int bias = 0;

    int operator()(PolicyState& state,
                   int action,
                   const char*,
                   const char*,
                   const char*,
                   const char*) const noexcept {
        return state.decision + action + bias;
    }
};

inline constexpr StatefulPolicyAdapter stateful_policy{7};
inline constexpr auto member_policy = &PolicyState::member_policy;
inline constexpr auto lambda_policy = [](PolicyState& state,
                                         int action,
                                         const char*,
                                         const char*,
                                         const char*,
                                         const char*) noexcept -> int {
    ++state.calls;
    state.last_action = action;
    return state.decision;
};

using TypedPolicyFunction = int (*)(PolicyState&,
                                    int,
                                    const char*,
                                    const char*,
                                    const char*,
                                    const char*);
inline constexpr TypedPolicyFunction null_typed_policy = nullptr;

int contextless_policy(void* raw,
                       int action,
                       const char*,
                       const char*,
                       const char*,
                       const char*) noexcept {
    return raw == nullptr ? action + 1 : -1;
}

template <typename Context>
concept CanMakeCountingPolicy = requires(std::shared_ptr<Context> context) {
    {
        make_sync_sqlite_owned_authorizer_policy<counting_policy>(
            std::move(context))
    } -> std::same_as<SyncSqliteOwnedAuthorizerPolicy>;
};

template <auto Policy, typename Context>
concept CanMakePolicy = requires(std::shared_ptr<Context> context) {
    {
        make_sync_sqlite_owned_authorizer_policy<Policy>(std::move(context))
    } -> std::same_as<SyncSqliteOwnedAuthorizerPolicy>;
};

static_assert(CanMakeCountingPolicy<PolicyState>);
static_assert(!CanMakeCountingPolicy<WrongPolicyState>);
static_assert(!CanMakeCountingPolicy<const PolicyState>);
static_assert(!CanMakePolicy<wrong_result_policy, PolicyState>);
static_assert(CanMakePolicy<lambda_policy, PolicyState>);
static_assert(!CanMakePolicy<null_typed_policy, PolicyState>);
static_assert(!CanMakePolicy<member_policy, PolicyState>);
static_assert(!CanMakePolicy<stateful_policy, PolicyState>);
static_assert(CanMakePolicy<read_only_policy, ReadOnlyPolicyState>);
static_assert(CanMakePolicy<read_only_policy, const ReadOnlyPolicyState>);
static_assert(!CanMakeCountingPolicy<volatile PolicyState>);
static_assert(!CanMakeCountingPolicy<PolicyState[2]>);
static_assert(!std::is_constructible_v<SyncSqliteOwnedAuthorizerPolicy,
                                       SyncSqliteAuthorizerPolicy,
                                       std::shared_ptr<void>>);

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void expect(bool condition, std::string_view label, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(std::string(label));
}

template <typename Exception, typename Function>
void expect_exception(Function&& function,
                      std::string_view fragment,
                      std::string_view label,
                      std::uint64_t& checks) {
    ++checks;
    try {
        function();
    } catch (const Exception& error) {
        if (std::string_view(error.what()).find(fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(std::string(label) + ": unexpected error: " + error.what());
    }
    fail(std::string(label) + ": no exception");
}

void test_type_and_empty_contract(std::uint64_t& checks) {
    static_assert(!std::is_copy_constructible_v<
                  SyncSqliteOwnedAuthorizerPolicy>);
    static_assert(!std::is_copy_assignable_v<
                  SyncSqliteOwnedAuthorizerPolicy>);
    static_assert(std::is_nothrow_move_constructible_v<
                  SyncSqliteOwnedAuthorizerPolicy>);
    static_assert(!std::is_move_assignable_v<
                  SyncSqliteOwnedAuthorizerPolicy>);

    SyncSqliteOwnedAuthorizerPolicy empty;
    expect(empty.empty() && !empty.valid() && !empty.owns_context(),
           "default policy owner is exactly empty",
           checks);
    expect_exception<std::logic_error>(
        [&] { (void)empty.invoke(1, nullptr, nullptr, nullptr, nullptr); },
        "owner is empty",
        "empty policy invocation is rejected",
        checks);
    expect_exception<std::invalid_argument>(
        [] {
            SyncSqliteOwnedAuthorizerPolicy invalid(nullptr);
            (void)invalid;
        },
        "policy is null",
        "null context-free callback is rejected",
        checks);
    expect_exception<std::invalid_argument>(
        [] {
            (void)make_sync_sqlite_owned_authorizer_policy<counting_policy>(
                std::shared_ptr<PolicyState>{});
        },
        "non-null shared context",
        "null typed context is rejected before erasure",
        checks);
}

void test_contextless_policy(std::uint64_t& checks) {
    SyncSqliteOwnedAuthorizerPolicy policy(contextless_policy);
    expect(policy.valid() && !policy.empty() && !policy.owns_context(),
           "contextless callback remains a valid policy",
           checks);
    expect(policy.invoke(41, nullptr, nullptr, nullptr, nullptr) == 42,
           "contextless callback receives a null context",
           checks);
}

void test_typed_factory_move_swap_and_release(std::uint64_t& checks) {
    auto external = std::make_shared<PolicyState>();
    external->decision = 73;
    const std::weak_ptr<PolicyState> lifetime = external;

    SyncSqliteOwnedAuthorizerPolicy source =
        make_sync_sqlite_owned_authorizer_policy<counting_policy>(external);
    expect(source.valid() && source.owns_context(),
           "typed factory retains an owned context",
           checks);
    external.reset();
    expect(!lifetime.expired(),
           "external release does not revoke installed policy context",
           checks);

    SyncSqliteOwnedAuthorizerPolicy moved(std::move(source));
    expect(source.empty() && moved.valid() && moved.owns_context(),
           "move transfers callback and typed context as one capsule",
           checks);
    expect(moved.invoke(19, nullptr, nullptr, nullptr, nullptr) == 73,
           "moved typed policy remains callable",
           checks);
    {
        const std::shared_ptr<PolicyState> retained = lifetime.lock();
        expect(retained != nullptr && retained->calls == 1 &&
                   retained->last_action == 19,
               "callback observes the exact retained typed context",
               checks);
    }

    SyncSqliteOwnedAuthorizerPolicy escrow;
    escrow.swap(moved);
    expect(moved.empty() && escrow.valid() && escrow.owns_context(),
           "swap escrows the complete typed policy capsule",
           checks);
    escrow.swap(escrow);
    expect(escrow.valid(), "self-swap preserves policy authority", checks);

    SyncSqliteOwnedAuthorizerPolicy final_owner(std::move(escrow));
    expect(escrow.empty() && final_owner.valid(),
           "a second source-first move remains exact",
           checks);
    final_owner.swap(moved);
    expect(final_owner.empty() && moved.valid(),
           "typed policy can be retired into an ordinary owner",
           checks);

    {
        SyncSqliteOwnedAuthorizerPolicy retiring(std::move(moved));
        expect(!lifetime.expired(),
               "context remains live through the retiring owner",
               checks);
    }
    expect(lifetime.expired(),
           "retiring owner releases the final typed context exactly once",
           checks);
}

void test_const_shared_context(std::uint64_t& checks) {
    auto mutable_context =
        std::make_shared<ReadOnlyPolicyState>(ReadOnlyPolicyState{91});
    std::shared_ptr<const ReadOnlyPolicyState> context = mutable_context;
    const std::weak_ptr<const ReadOnlyPolicyState> lifetime = context;

    {
        auto policy =
            make_sync_sqlite_owned_authorizer_policy<read_only_policy>(context);
        expect(policy.valid() && policy.owns_context(),
               "factory preserves a genuinely const shared context",
               checks);
        mutable_context.reset();
        context.reset();
        expect(!lifetime.expired() &&
                   policy.invoke(0, nullptr, nullptr, nullptr, nullptr) == 91,
               "const policy invokes through its exact retained context",
               checks);
    }
    expect(lifetime.expired(),
           "const context retires with its typed capsule",
           checks);
}

struct AliasingPolicyEnvelope final {
    PolicyState state;
    std::uint64_t guard = 0;
};

void test_aliasing_shared_owner_and_custom_deleter(std::uint64_t& checks) {
    std::uint64_t deletes = 0;
    auto complete = std::shared_ptr<AliasingPolicyEnvelope>(
        new AliasingPolicyEnvelope{{0, 0, 64}, 0xA11A51A5ULL},
        [&deletes](AliasingPolicyEnvelope* value) noexcept {
            ++deletes;
            delete value;
        });
    PolicyState* const exact_alias = &complete->state;
    std::shared_ptr<PolicyState> alias(complete, exact_alias);
    const std::weak_ptr<AliasingPolicyEnvelope> complete_lifetime = complete;
    const std::weak_ptr<PolicyState> alias_lifetime = alias;

    {
        auto policy =
            make_sync_sqlite_owned_authorizer_policy<lambda_policy>(alias);
        complete.reset();
        alias.reset();
        expect(!complete_lifetime.expired() && !alias_lifetime.expired(),
               "typed capsule preserves the aliasing shared control block",
               checks);
        expect(policy.invoke(29, nullptr, nullptr, nullptr, nullptr) == 64,
               "noncapturing lambda invokes through an aliasing context",
               checks);
        const auto retained = alias_lifetime.lock();
        expect(retained != nullptr && retained.get() == exact_alias &&
                   retained->calls == 1 && retained->last_action == 29,
               "capsule preserves the exact alias pointer and state",
               checks);
    }

    expect(complete_lifetime.expired() && alias_lifetime.expired(),
           "aliasing control block retires with the typed capsule",
           checks);
    expect(deletes == 1,
           "custom deleter runs exactly once after capsule retirement",
           checks);
}

#if defined(__unix__) || defined(__APPLE__)

template <typename Function>
void expect_inherited_fail_stop(Function&& function,
                                std::string_view label,
                                std::uint64_t& checks) {
    auto child = spawn_inherited_test_process_or_throw(
        [&function] {
            function();
            return 99;
        },
        label);
    child.wait_for_exact_exit(kSyncProcessCapabilityViolationExitCode,
                              5s,
                              label);
    ++checks;
}

void test_child_local_context_and_owner_work(std::uint64_t& checks) {
    auto child = spawn_inherited_test_process_or_throw(
        [] {
            auto context = std::make_shared<PolicyState>();
            context->decision = 17;
            auto policy =
                make_sync_sqlite_owned_authorizer_policy<counting_policy>(
                    context);
            return policy.invoke(5, nullptr, nullptr, nullptr, nullptr) == 17 &&
                           context->calls == 1 && context->last_action == 5
                       ? 0
                       : 98;
        },
        "child-local typed policy owner");
    child.wait_for_exact_exit(0, 5s, "child-local typed policy owner");
    ++checks;
}

void test_inherited_owner_fails_before_shared_state_access(
    std::uint64_t& checks) {
    auto context = std::make_shared<PolicyState>();
    auto* const policy = new SyncSqliteOwnedAuthorizerPolicy(
        make_sync_sqlite_owned_authorizer_policy<counting_policy>(context));

    expect_inherited_fail_stop(
        [policy] { (void)policy->valid(); },
        "inherited inspection fails stopped",
        checks);
    expect_inherited_fail_stop(
        [policy] {
            SyncSqliteOwnedAuthorizerPolicy moved(std::move(*policy));
            (void)moved;
        },
        "inherited move validates source before capsule transfer",
        checks);
    expect_inherited_fail_stop(
        [policy] { delete policy; },
        "inherited destruction fails before capsule teardown",
        checks);

    delete policy;
    expect(context.use_count() == 1,
           "child fail-stop paths do not alter parent context lifetime",
           checks);
}

#endif

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_type_and_empty_contract(checks);
        test_contextless_policy(checks);
        test_typed_factory_move_swap_and_release(checks);
        test_const_shared_context(checks);
        test_aliasing_shared_owner_and_custom_deleter(checks);
#if defined(__unix__) || defined(__APPLE__)
        test_child_local_context_and_owner_work(checks);
        test_inherited_owner_fails_before_shared_state_access(checks);
#endif
        std::cout << "sqlite owned-authorizer-policy tests passed: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite owned-authorizer-policy tests failed after "
                  << checks << " checks: " << error.what() << "\n";
        return 1;
    }
}
