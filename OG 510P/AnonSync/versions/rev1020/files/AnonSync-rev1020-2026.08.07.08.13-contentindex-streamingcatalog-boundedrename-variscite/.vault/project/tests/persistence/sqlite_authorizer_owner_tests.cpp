#include "sqlite_authorizer_owner.hpp"

#include <sqlite3.h>

#include <array>
#include <atomic>
#include <cstdint>
#include <exception>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>

namespace {

using anonsync::persistence::SqliteAuthorizerOwner;

struct SqliteCloser final {
    void operator()(sqlite3* database) const noexcept {
        if (database != nullptr) (void)sqlite3_close(database);
    }
};
using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

struct CallbackState final {
    std::uint64_t calls = 0;
    int decision = SQLITE_OK;
};

int counting_authorizer(void* raw,
                         int,
                         const char*,
                         const char*,
                         const char*,
                         const char*) noexcept {
    auto* const state = static_cast<CallbackState*>(raw);
    if (state == nullptr) return SQLITE_DENY;
    ++state->calls;
    return state->decision;
}

int alien_authorizer(void*,
                     int,
                     const char*,
                     const char*,
                     const char*,
                     const char*) noexcept {
    return SQLITE_OK;
}

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

SqlitePtr open_database() {
    sqlite3* raw = nullptr;
    const int result = sqlite3_open_v2(
        ":memory:",
        &raw,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (result != SQLITE_OK || raw == nullptr) {
        const std::string detail =
            raw == nullptr ? sqlite3_errstr(result) : sqlite3_errmsg(raw);
        if (raw != nullptr) (void)sqlite3_close_v2(raw);
        fail("could not open authorizer-owner fixture: " + detail);
    }
    return SqlitePtr(raw);
}

void prepare_select_or_throw(sqlite3* database) {
    sqlite3_stmt* statement = nullptr;
    const int prepare_result =
        sqlite3_prepare_v2(database, "SELECT 1;", -1, &statement, nullptr);
    if (prepare_result != SQLITE_OK || statement == nullptr) {
        if (statement != nullptr) (void)sqlite3_finalize(statement);
        fail("authorizer-owner SELECT prepare failed");
    }
    if (sqlite3_finalize(statement) != SQLITE_OK) {
        fail("authorizer-owner SELECT finalize failed");
    }
}

void test_type_and_input_contract(std::uint64_t& checks) {
    static_assert(!std::is_copy_constructible_v<SqliteAuthorizerOwner>);
    static_assert(!std::is_copy_assignable_v<SqliteAuthorizerOwner>);
    static_assert(!std::is_move_constructible_v<SqliteAuthorizerOwner>);
    static_assert(!std::is_move_assignable_v<SqliteAuthorizerOwner>);
    expect(true, "authorizer owner address remains stable", checks);

    SqlitePtr database = open_database();
    CallbackState state;
    SqliteAuthorizerOwner owner;
    expect_exception<std::invalid_argument>(
        [&] { owner.attach(nullptr, counting_authorizer, &state, "null db"); },
        "requires a database",
        "null database rejected",
        checks);
    expect_exception<std::invalid_argument>(
        [&] { owner.attach(database.get(), nullptr, &state, "null callback"); },
        "requires a database",
        "null callback rejected",
        checks);
    expect_exception<std::invalid_argument>(
        [&] {
            owner.attach(database.get(), counting_authorizer, nullptr,
                         "null context");
        },
        "retained context",
        "null retained context rejected",
        checks);
    expect_exception<std::invalid_argument>(
        [&] { owner.attach(database.get(), counting_authorizer, &state, ""); },
        "nonempty diagnostic label",
        "empty label rejected",
        checks);
    expect(!owner.attached(), "input failures leave the owner empty", checks);
}

void test_attach_replace_detach_and_reuse(std::uint64_t& checks) {
    SqlitePtr database = open_database();
    SqlitePtr other_database = open_database();
    CallbackState first;
    CallbackState second;
    SqliteAuthorizerOwner owner;

    owner.attach(database.get(), counting_authorizer, &first, "first owner");
    expect(owner.attached(), "owner reports attached state", checks);
    expect(sqlite3_get_clientdata(
               database.get(), "anonsync.sqlite.authorizer-owner.v1") != nullptr,
           "owner publishes its lifetime claim",
           checks);
    prepare_select_or_throw(database.get());
    expect(first.calls > 0, "attached callback receives prepare events", checks);

    SqliteAuthorizerOwner duplicate;
    expect_exception<std::logic_error>(
        [&] {
            duplicate.attach(database.get(), counting_authorizer, &second,
                             "duplicate owner");
        },
        "already has an AnonSync SQLite authorizer owner",
        "duplicate owner cannot replace the singleton claim",
        checks);
    expect(!duplicate.attached(), "duplicate rejection leaves owner empty", checks);

    expect_exception<std::logic_error>(
        [&] {
            owner.replace(other_database.get(), counting_authorizer, &second,
                          "wrong connection");
        },
        "exact attached connection",
        "replacement cannot cross connections",
        checks);

    expect(sqlite3_set_authorizer(
               database.get(), alien_authorizer, nullptr) == SQLITE_OK,
           "adversarial raw replacement fixture installed",
           checks);
    const std::uint64_t first_calls = first.calls;
    prepare_select_or_throw(database.get());
    expect(first.calls == first_calls,
           "alien replacement bypasses the old callback before recovery",
           checks);

    owner.replace(database.get(), counting_authorizer, &second,
                  "recover exact owner");
    prepare_select_or_throw(database.get());
    expect(second.calls > 0,
           "explicit owner replacement recovers the singleton callback",
           checks);

    owner.detach(database.get());
    expect(!owner.attached(), "detach empties owner state", checks);
    expect(sqlite3_get_clientdata(
               database.get(), "anonsync.sqlite.authorizer-owner.v1") == nullptr,
           "detach consumes the lifetime claim",
           checks);
    const std::uint64_t second_calls = second.calls;
    prepare_select_or_throw(database.get());
    expect(second.calls == second_calls,
           "detach disables the retained callback before context release",
           checks);
    owner.detach(database.get());
    expect(!owner.attached(), "detach is idempotent", checks);

    CallbackState reused;
    SqliteAuthorizerOwner replacement;
    replacement.attach(database.get(), counting_authorizer, &reused,
                       "reused owner");
    prepare_select_or_throw(database.get());
    expect(reused.calls > 0, "consumed singleton claim can be reused", checks);
    replacement.detach(database.get());
}

void test_concurrent_duplicate_owners_reject_without_fail_stop(
    std::uint64_t& checks) {
    static constexpr const char* kClaimName =
        "anonsync.sqlite.authorizer-owner.v1";
    SqlitePtr database = open_database();

    constexpr int kIterations = 64;
    int successful_attachments = 0;
    int duplicate_rejections = 0;
    for (int iteration = 0; iteration < kIterations; ++iteration) {
        std::array<CallbackState, 2> states;
        std::array<std::exception_ptr, 2> errors;
        std::array<std::atomic<int>, 2> outcomes;
        for (auto& outcome : outcomes) {
            outcome.store(0, std::memory_order_relaxed);
        }
        std::atomic<int> ready{0};
        std::atomic<int> finished{0};
        std::atomic<bool> start{false};
        std::atomic<bool> release{false};
        std::array<std::thread, 2> threads;

        for (std::size_t index = 0; index < threads.size(); ++index) {
            threads[index] = std::thread([&, index] {
                ready.fetch_add(1, std::memory_order_release);
                while (!start.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }

                auto owner = std::make_unique<SqliteAuthorizerOwner>();
                try {
                    owner->attach(database.get(),
                                  counting_authorizer,
                                  &states[index],
                                  "concurrent duplicate authorizer owner");
                    outcomes[index].store(1, std::memory_order_release);
                } catch (const std::logic_error& error) {
                    if (std::string(error.what()).find(
                            "already has an AnonSync SQLite authorizer owner") !=
                        std::string::npos) {
                        owner.reset();
                        outcomes[index].store(2, std::memory_order_release);
                    } else {
                        errors[index] = std::current_exception();
                        owner.reset();
                        outcomes[index].store(3, std::memory_order_release);
                    }
                } catch (...) {
                    errors[index] = std::current_exception();
                    owner.reset();
                    outcomes[index].store(3, std::memory_order_release);
                }

                finished.fetch_add(1, std::memory_order_release);
                while (!release.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }
                if (owner) owner->detach(database.get());
            });
        }

        while (ready.load(std::memory_order_acquire) != 2) {
            std::this_thread::yield();
        }
        start.store(true, std::memory_order_release);
        while (finished.load(std::memory_order_acquire) != 2) {
            std::this_thread::yield();
        }

        int iteration_successes = 0;
        int iteration_rejections = 0;
        for (const auto& outcome : outcomes) {
            const int value = outcome.load(std::memory_order_acquire);
            iteration_successes += value == 1 ? 1 : 0;
            iteration_rejections += value == 2 ? 1 : 0;
        }
        successful_attachments += iteration_successes;
        duplicate_rejections += iteration_rejections;
        const bool claim_is_live =
            sqlite3_get_clientdata(database.get(), kClaimName) != nullptr;
        prepare_select_or_throw(database.get());
        const std::uint64_t callback_calls = states[0].calls + states[1].calls;

        release.store(true, std::memory_order_release);
        for (auto& thread : threads) thread.join();
        for (const auto& error : errors) {
            if (error) std::rethrow_exception(error);
        }
        if (iteration_successes != 1 || iteration_rejections != 1 ||
            !claim_is_live || callback_calls == 0U) {
            throw std::runtime_error(
                "concurrent duplicate authorizer outcome mismatch at iteration " +
                std::to_string(iteration));
        }
        if (sqlite3_get_clientdata(database.get(), kClaimName) != nullptr) {
            throw std::runtime_error(
                "concurrent duplicate authorizer claim leaked at iteration " +
                std::to_string(iteration));
        }
    }

    expect(successful_attachments == kIterations &&
               duplicate_rejections == kIterations,
           "every concurrent authorizer race has one live owner and one recoverable rejection",
           checks);
    expect(sqlite3_get_clientdata(database.get(), kClaimName) == nullptr,
           "concurrent authorizer corpus consumes every lifetime claim",
           checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_type_and_input_contract(checks);
        test_attach_replace_detach_and_reuse(checks);
        test_concurrent_duplicate_owners_reject_without_fail_stop(checks);
        std::cout << "sqlite authorizer-owner tests passed: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite authorizer-owner tests failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}
