#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>
#include <vector>

#if !defined(_WIN32)
#include "inherited_test_process.hpp"

#include <chrono>
#endif

namespace {

using anonsync::SyncThreadIncarnation;
using anonsync::current_sync_thread_incarnation_noexcept;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::require_sync_thread_incarnation_or_throw;
using anonsync::sync_thread_incarnation_is_current;

static_assert(!std::is_trivially_copyable_v<SyncThreadIncarnation>);
static_assert(!std::is_constructible_v<SyncThreadIncarnation, std::uint64_t>);
static_assert(!std::is_convertible_v<std::uint64_t, SyncThreadIncarnation>);

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }

    template <typename Callable>
    void require_throws(Callable&& callable,
                        const std::string& expected,
                        const std::string& label) {
        try {
            callable();
            require(false, label + " did not throw");
        } catch (const std::exception& error) {
            require(std::string(error.what()).find(expected) !=
                        std::string::npos,
                    label + " reported the expected reason");
        }
    }
};

void test_stable_current_thread_identity(TestState& test) {
    const SyncThreadIncarnation first =
        current_sync_thread_incarnation_noexcept();
    const SyncThreadIncarnation second =
        current_sync_thread_incarnation_noexcept();
    test.require(first.valid(), "current thread incarnation is nonempty");
    test.require(first == second,
                 "current thread incarnation is stable for one lifetime");
    test.require(sync_thread_incarnation_is_current(first),
                 "current thread recognizes its own incarnation");
    require_sync_thread_incarnation_or_throw(first, "current-thread fixture");
    test.require(true, "current thread proof is accepted");
}

void test_empty_and_foreign_proofs_rejected(TestState& test) {
    test.require_throws(
        [] {
            require_sync_thread_incarnation_or_throw(
                SyncThreadIncarnation{}, "empty fixture");
        },
        "thread-affinity proof is empty",
        "empty thread proof");

    const SyncThreadIncarnation owner =
        current_sync_thread_incarnation_noexcept();
    bool foreign_is_current = true;
    std::string reason;
    std::thread worker([&] {
        foreign_is_current = sync_thread_incarnation_is_current(owner);
        try {
            require_sync_thread_incarnation_or_throw(owner,
                                                     "foreign fixture");
        } catch (const std::exception& error) {
            reason = error.what();
        }
    });
    worker.join();
    test.require(!foreign_is_current,
                 "foreign thread does not inherit owner incarnation");
    test.require(reason.find("originating thread") != std::string::npos,
                 "foreign thread proof reports affinity failure");
    test.require(sync_thread_incarnation_is_current(owner),
                 "foreign rejection does not consume owner proof");
}

void test_live_and_recycled_threads_receive_unique_incarnations(
    TestState& test) {
    constexpr std::size_t kConcurrentThreads = 32;
    std::vector<SyncThreadIncarnation> concurrent(kConcurrentThreads);
    std::vector<std::thread> workers;
    workers.reserve(kConcurrentThreads);
    for (std::size_t index = 0; index < kConcurrentThreads; ++index) {
        workers.emplace_back([&, index] {
            concurrent[index] = current_sync_thread_incarnation_noexcept();
        });
    }
    for (std::thread& worker : workers) worker.join();

    const auto all_valid_and_unique = [](const auto& incarnations) {
        for (std::size_t left = 0; left < incarnations.size(); ++left) {
            if (!incarnations[left].valid()) return false;
            for (std::size_t right = left + 1; right < incarnations.size();
                 ++right) {
                if (incarnations[left] == incarnations[right]) return false;
            }
        }
        return true;
    };
    test.require(all_valid_and_unique(concurrent),
                 "live threads receive distinct nonempty incarnations");

    constexpr std::size_t kSequentialThreads = 64;
    std::vector<SyncThreadIncarnation> sequential;
    sequential.reserve(kSequentialThreads);
    for (std::size_t index = 0; index < kSequentialThreads; ++index) {
        SyncThreadIncarnation observed;
        std::thread worker([&] {
            observed = current_sync_thread_incarnation_noexcept();
        });
        worker.join();
        sequential.push_back(observed);
    }
    test.require(all_valid_and_unique(sequential),
                 "joined thread identifiers cannot resurrect an incarnation");
}

#if !defined(_WIN32)

using anonsync::test::spawn_inherited_test_process_or_throw;
using namespace std::chrono_literals;

void test_fork_refreshes_thread_identity(TestState& test) {
    const SyncThreadIncarnation parent =
        current_sync_thread_incarnation_noexcept();
    auto child = spawn_inherited_test_process_or_throw(
        [parent] {
            const SyncThreadIncarnation child_incarnation =
                current_sync_thread_incarnation_noexcept();
            if (!child_incarnation.valid() || child_incarnation == parent ||
                sync_thread_incarnation_is_current(parent) ||
                !sync_thread_incarnation_is_current(child_incarnation)) {
                return 71;
            }
            return 0;
        },
        "fork-refreshed thread incarnation");
    test.require(child.active(),
                 "fork-refreshed thread incarnation child is owned");
    child.wait_for_exact_exit(0, 5s,
                              "fork-refreshed thread incarnation");
    test.require(true,
                 "fork-refreshed thread incarnation returned exactly");
}

void test_noexcept_foreign_thread_violation_fails_stopped(TestState& test) {
    auto child = spawn_inherited_test_process_or_throw(
        [] {
            const SyncThreadIncarnation owner =
                current_sync_thread_incarnation_noexcept();
            int unexpected_status = 73;
            std::thread worker([owner, &unexpected_status] {
                if (sync_thread_incarnation_is_current(owner)) {
                    unexpected_status = 72;
                    return;
                }
                anonsync::
                    fail_stop_on_sync_thread_capability_violation_noexcept();
            });
            worker.join();
            return unexpected_status;
        },
        "foreign-thread noexcept ownership violation");
    test.require(child.active(),
                 "foreign-thread fail-stop child is owned");
    child.wait_for_exact_exit(kSyncProcessCapabilityViolationExitCode, 5s,
                              "foreign-thread noexcept ownership violation");
    test.require(true,
                 "foreign-thread noexcept ownership violation failed stopped");
}

#endif

}  // namespace

int main() {
    TestState test;
    try {
        test_stable_current_thread_identity(test);
        test_empty_and_foreign_proofs_rejected(test);
        test_live_and_recycled_threads_receive_unique_incarnations(test);
#if !defined(_WIN32)
        test_fork_refreshes_thread_identity(test);
        test_noexcept_foreign_thread_violation_fails_stopped(test);
#endif
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "UNEXPECTED: " << error.what() << "\n";
    }

    std::cout << "thread-incarnation checks: " << test.passed
              << " passed, " << test.failed << " failed\n";
    return test.failed == 0 ? 0 : 1;
}
